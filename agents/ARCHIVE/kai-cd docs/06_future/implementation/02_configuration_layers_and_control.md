---
title: "Configuration Layers and Control Planes"
description: "Comprehensive configuration architecture for kAI/kOS with multi-tier override model, secure vault integration, and governance controls"
type: "implementation"
status: "future"
priority: "high"
last_updated: "2025-01-20"
related_docs: ["system-configuration-architecture.md", "security-architecture-and-trust.md"]
implementation_status: "planned"
complexity: "high"
decision_scope: "system-wide"
code_references: ["src/core/config/ConfigLoader.ts", "src/core/security/VaultService.ts"]
---

# Configuration Layers and Control Planes

## Agent Context
This document defines the complete configuration architecture for kAI/kOS systems. Agents should understand this as the foundational layer for all system behavior, user preferences, and security policies. The multi-tier configuration model enables flexible deployment scenarios from single-user installations to enterprise-managed environments.

## Overview of Configuration Scope

The kAI/kOS configuration system implements a four-tier hierarchical model with clear precedence rules and secure override capabilities:

```text
┌────────────────────────────┐
|        System-Wide         | <-- Immutable defaults, org policies, OS-level settings
├────────────────────────────┤
|      User Configuration     | <-- Preferences, integrations, credentials, UI settings
├────────────────────────────┤
|   Session / Runtime Cache   | <-- Temporary overrides, dynamic agent state
├────────────────────────────┤
|       Agent-Specific        | <-- Local per-agent config, personas, role behaviors
└────────────────────────────┘
```

## Directory Structure

```text
configs/
├── system/
│   ├── defaults.json          # Immutable or locked defaults
│   ├── org_policy.json        # Global rules for managed deployments
│   ├── klp_policy.toml        # Federation participation rules
├── user/
│   ├── preferences.json       # UI themes, sound, accessibility
│   ├── integrations.json      # Service keys, sync preferences
│   ├── vault.enc              # Encrypted user secrets (AES-256)
├── agents/
│   ├── agent-[ID]/
│   │   ├── persona.json       # Prompt, style, capabilities
│   │   └── overrides.json     # Per-agent config changes
├── runtime/
│   ├── cache.json             # In-memory session state
│   └── auth-tokens/           # Short-lived service tokens
└── templates/
    ├── default-theme.json     # Default light/dark themes
    └── default-persona.json   # Baseline persona settings
```

## Configuration Precedence and Merging

```text
Precedence (highest to lowest):
 1. Runtime/session (`runtime/`)
 2. Agent-specific (`agents/[ID]/`)
 3. User preferences (`user/`)
 4. System policies (`system/`)
```

**Merging Rules:**
- Deep-merge applied to all JSON objects
- `@locked` annotations in system config prevent override
- `@env` annotations allow referencing environment variables
- Array values are replaced, not merged (explicit override behavior)

## Configuration Loader Implementation

```typescript
// src/core/config/ConfigLoader.ts
interface Config {
  system: SystemConfig;
  user: UserConfig;
  agent: AgentConfig;
  runtime: RuntimeConfig;
}

interface ConfigMergeOptions {
  respectLocks: boolean;
  allowEnvOverrides: boolean;
  validateSchema: boolean;
}

class ConfigLoader {
  private static cache: Map<string, Config> = new Map();
  private static watchers: Map<string, FileWatcher> = new Map();

  static async loadEffectiveConfig(
    agentId?: string, 
    options: ConfigMergeOptions = { respectLocks: true, allowEnvOverrides: true, validateSchema: true }
  ): Promise<Config> {
    const cacheKey = `${agentId || 'global'}-${JSON.stringify(options)}`;
    
    if (this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey)!;
    }

    const systemDefaults = await this.loadJson('configs/system/defaults.json');
    const orgPolicy = await this.loadJson('configs/system/org_policy.json');
    const userPrefs = await this.loadJson('configs/user/preferences.json');
    const agentOverrides = agentId ? 
      await this.loadJson(`configs/agents/${agentId}/overrides.json`) : {};
    const sessionState = await this.loadJson('configs/runtime/cache.json');

    const merged = this.deepMergeConfigs([
      systemDefaults,
      orgPolicy,
      userPrefs,
      agentOverrides,
      sessionState
    ], options);

    if (options.validateSchema) {
      await this.validateConfig(merged);
    }

    this.cache.set(cacheKey, merged);
    this.setupWatcher(cacheKey, merged);
    
    return merged;
  }

  private static deepMergeConfigs(configs: any[], options: ConfigMergeOptions): Config {
    return configs.reduce((acc, config) => {
      return this.mergeWithRules(acc, config, options);
    }, {});
  }

  private static mergeWithRules(target: any, source: any, options: ConfigMergeOptions): any {
    for (const key in source) {
      if (target[key]?.['@locked'] && options.respectLocks) {
        continue; // Skip locked properties
      }

      if (typeof source[key] === 'string' && source[key].startsWith('@env:') && options.allowEnvOverrides) {
        const envVar = source[key].substring(5);
        target[key] = process.env[envVar] || target[key];
      } else if (typeof source[key] === 'object' && !Array.isArray(source[key])) {
        target[key] = this.mergeWithRules(target[key] || {}, source[key], options);
      } else {
        target[key] = source[key];
      }
    }
    return target;
  }

  static async reloadConfig(agentId?: string): Promise<void> {
    const cacheKey = `${agentId || 'global'}`;
    this.cache.delete(cacheKey);
    await this.loadEffectiveConfig(agentId);
    this.notifyConfigChange(cacheKey);
  }

  private static setupWatcher(cacheKey: string, config: Config): void {
    // Implementation for file system watchers
    const watcher = new FileWatcher([
      'configs/system/',
      'configs/user/',
      'configs/agents/',
      'configs/runtime/'
    ]);
    
    watcher.on('change', () => this.reloadConfig());
    this.watchers.set(cacheKey, watcher);
  }
}
```

## Vault Access and Encryption

All sensitive configuration data is protected through the integrated vault system:

```typescript
// src/core/security/VaultService.ts
interface VaultEntry {
  id: string;
  type: 'api_key' | 'password' | 'certificate' | 'token';
  value: string; // Encrypted
  metadata: {
    created: string;
    lastAccessed: string;
    expiresAt?: string;
  };
}

interface VaultSchema {
  version: number;
  encryption: {
    algorithm: 'AES-256-GCM';
    iterations: number;
    saltRotation: string;
  };
  entries: VaultEntry[];
}

class VaultService {
  private static readonly ENCRYPTION_ALGORITHM = 'AES-256-GCM';
  private static readonly PBKDF2_ITERATIONS = 150000;

  static async encryptVault(data: VaultSchema, password: string): Promise<Buffer> {
    const salt = crypto.randomBytes(32);
    const key = await this.deriveKey(password, salt);
    const iv = crypto.randomBytes(16);
    
    const cipher = crypto.createCipher(this.ENCRYPTION_ALGORITHM, key);
    cipher.setAAD(salt);
    
    const encrypted = Buffer.concat([
      cipher.update(JSON.stringify(data), 'utf8'),
      cipher.final()
    ]);
    
    const authTag = cipher.getAuthTag();
    
    return Buffer.concat([salt, iv, authTag, encrypted]);
  }

  static async decryptVault(encryptedData: Buffer, password: string): Promise<VaultSchema> {
    const salt = encryptedData.subarray(0, 32);
    const iv = encryptedData.subarray(32, 48);
    const authTag = encryptedData.subarray(48, 64);
    const encrypted = encryptedData.subarray(64);
    
    const key = await this.deriveKey(password, salt);
    
    const decipher = crypto.createDecipher(this.ENCRYPTION_ALGORITHM, key);
    decipher.setAAD(salt);
    decipher.setAuthTag(authTag);
    
    const decrypted = Buffer.concat([
      decipher.update(encrypted),
      decipher.final()
    ]);
    
    return JSON.parse(decrypted.toString('utf8'));
  }

  private static async deriveKey(password: string, salt: Buffer): Promise<Buffer> {
    return new Promise((resolve, reject) => {
      crypto.pbkdf2(password, salt, this.PBKDF2_ITERATIONS, 32, 'sha256', (err, key) => {
        if (err) reject(err);
        else resolve(key);
      });
    });
  }
}
```

## Persona and Agent Behavior Configuration

Each agent maintains an isolated configuration profile for behavioral customization:

```typescript
interface PersonaConfig {
  id: string;
  name: string;
  description: string;
  tone: string;
  capabilities: string[];
  constraints: string[];
  defaultPrompt: string;
  contextWindow: number;
  temperature: number;
  maxTokens: number;
  stopSequences: string[];
  customInstructions?: string;
}

// Example persona configuration
const helperAgentPersona: PersonaConfig = {
  id: "helper-agent",
  name: "Kind Assistant",
  description: "A helpful, empathetic assistant focused on user support",
  tone: "kind, empathetic, warm, encouraging",
  capabilities: ["summarize", "answer_questions", "provide_guidance", "emotional_support"],
  constraints: ["no_harmful_content", "respect_privacy", "factual_accuracy"],
  defaultPrompt: "You are a helpful assistant who never gives up on a user. You provide thoughtful, accurate responses while maintaining a warm and encouraging tone.",
  contextWindow: 4096,
  temperature: 0.7,
  maxTokens: 1000,
  stopSequences: ["Human:", "Assistant:"],
  customInstructions: "Always acknowledge user emotions and provide supportive responses."
};
```

## Governance and Central Control

For enterprise deployments and multi-device synchronization, the kControlPlane provides centralized management:

```text
kControlPlane/
├── endpoints/
│   ├── sync/                    # Configuration synchronization
│   ├── audit/                   # Change auditing and compliance
│   ├── revoke/                  # Emergency credential revocation
│   └── federation/              # Cross-system coordination
├── agents/
│   ├── active_list.json         # Currently deployed agents
│   ├── trust_scores.json        # Agent reputation metrics
│   └── deployment_policies.json # Rollout and update rules
├── policies/
│   ├── klp_access_policies.json # KindLink Protocol access rules
│   ├── data_retention.json      # Data lifecycle policies
│   └── security_policies.json   # Security compliance rules
└── monitoring/
    ├── config_drift.json        # Configuration drift detection
    └── compliance_status.json   # Policy compliance monitoring
```

### Control Plane API

```typescript
interface ControlPlaneAPI {
  // Configuration Management
  syncConfig(nodeId: string, config: Partial<Config>): Promise<void>;
  auditConfigChanges(timeRange: TimeRange): Promise<ConfigAudit[]>;
  enforcePolicy(policyId: string, nodes: string[]): Promise<EnforcementResult>;
  
  // Agent Management
  deployAgent(agentSpec: AgentDeploymentSpec): Promise<DeploymentResult>;
  updateAgentTrustScore(agentId: string, score: number): Promise<void>;
  revokeAgentAccess(agentId: string, reason: string): Promise<void>;
  
  // Monitoring and Compliance
  detectConfigDrift(): Promise<DriftReport[]>;
  generateComplianceReport(): Promise<ComplianceReport>;
  alertOnPolicyViolation(violation: PolicyViolation): Promise<void>;
}
```

## Theme and Accessibility Configuration

```typescript
interface ThemeConfig {
  id: string;
  name: string;
  colors: {
    primary: string;
    secondary: string;
    background: string;
    surface: string;
    text: string;
    accent: string;
  };
  typography: {
    fontFamily: string;
    fontSize: number;
    lineHeight: number;
    fontWeight: number;
  };
  accessibility: {
    contrastMode: 'normal' | 'high' | 'maximum';
    animations: boolean;
    reducedMotion: boolean;
    screenReader: boolean;
    keyboard: boolean;
  };
  customProperties: Record<string, string>;
}

// Example theme configuration
const solarizedDarkTheme: ThemeConfig = {
  id: "solarized-dark",
  name: "Solarized Dark",
  colors: {
    primary: "#268bd2",
    secondary: "#2aa198",
    background: "#002b36",
    surface: "#073642",
    text: "#839496",
    accent: "#b58900"
  },
  typography: {
    fontFamily: "Inter, system-ui, sans-serif",
    fontSize: 16,
    lineHeight: 1.6,
    fontWeight: 400
  },
  accessibility: {
    contrastMode: "high",
    animations: false,
    reducedMotion: true,
    screenReader: true,
    keyboard: true
  },
  customProperties: {
    "--border-radius": "8px",
    "--shadow-elevation": "2px 4px 8px rgba(0,0,0,0.1)"
  }
};
```

## Change Auditing and Logging

Every configuration change triggers comprehensive auditing:

```typescript
// src/core/logging/ConfigAuditLogger.ts
interface ConfigChangeEvent {
  timestamp: string;
  userId?: string;
  agentId?: string;
  changeType: 'create' | 'update' | 'delete' | 'merge';
  configPath: string;
  oldValue: any;
  newValue: any;
  source: 'user' | 'system' | 'agent' | 'api' | 'sync';
  metadata: {
    sessionId: string;
    ipAddress?: string;
    userAgent?: string;
    reason?: string;
  };
}

class ConfigAuditLogger {
  static async logConfigChange(event: ConfigChangeEvent): Promise<void> {
    // Store in append-only audit log
    await this.appendToAuditLog(event);
    
    // Generate diff for complex changes
    if (event.changeType === 'update') {
      event.diff = this.generateDiff(event.oldValue, event.newValue);
    }
    
    // Trigger real-time notifications
    await this.notifyConfigWatchers(event);
    
    // Check for policy violations
    await this.checkPolicyCompliance(event);
  }

  private static generateDiff(oldValue: any, newValue: any): ConfigDiff {
    return {
      added: this.getAddedKeys(oldValue, newValue),
      removed: this.getRemovedKeys(oldValue, newValue),
      modified: this.getModifiedKeys(oldValue, newValue)
    };
  }
}
```

## CLI Configuration Management

```bash
# Configuration management commands
kctl config set theme solarized-light
kctl config get vault-status
kctl config list --scope=user
kctl config validate --all
kctl config backup --output=config-backup.json
kctl config restore --input=config-backup.json

# Agent-specific configuration
kctl agent reload persona --agent=calendarAgent
kctl agent config set --agent=helperAgent tone="professional"
kctl agent config export --agent=all --output=agent-configs/

# System administration
kctl config sync --from=control-plane
kctl config audit --since=24h
kctl config enforce-policy --policy=security-baseline
```

## Integration Points

This configuration system integrates with:

- **Service Manager**: Service-specific authentication and routing rules
- **Agent Framework**: Persona loading and behavioral configuration  
- **Security System**: Vault access and encryption key management
- **UI System**: Theme application and accessibility settings
- **Monitoring System**: Configuration drift detection and compliance
- **Deployment System**: Environment-specific configuration profiles

## Implementation Status

- **Current**: Basic configuration loading and merging
- **Planned**: Full vault integration, control plane API, audit logging
- **Future**: Advanced policy enforcement, federated configuration sync

This configuration architecture provides the stability and flexibility needed for the Kind AI ecosystem to scale from individual users to enterprise deployments while maintaining security and usability.
