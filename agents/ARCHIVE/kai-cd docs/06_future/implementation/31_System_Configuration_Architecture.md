---
title: "System Configuration Architecture - Multi-Tier Override Model"
description: "Hierarchical configuration management with global defaults, environment profiles, user overrides, and cryptographic signing support"
type: "implementation"
status: "future"
priority: "high"
last_updated: "2025-01-27"
complexity: "medium"
decision_scope: "medium"
implementation_status: "planned"
agent_notes: "Comprehensive configuration system with three-tier override model, hot-reloading, and secure cryptographic validation"
related_documents:
  - "./29_configuration-layers-and-control.md"
  - "../security/05_comprehensive-security-architecture.md"
  - "../../current/implementation/configuration-management.md"
code_references:
  - "src/config/env.ts"
  - "src/config/system.env.ts"
  - "src/config/user.env.ts"
dependencies: ["Zod", "JSON5", "TOML", "YAML", "Ed25519", "AES-GCM"]
breaking_changes: false
---

# System Configuration Architecture - Multi-Tier Override Model

> **Agent Context**: Hierarchical configuration system supporting hot-reloading, secure validation, and multi-environment deployment scenarios  
> **Implementation**: 🔬 Planned - Advanced configuration management requiring schema validation and cryptographic security  
> **Use When**: Implementing multi-environment deployments, user preferences, or secure configuration distribution

## Quick Summary
Comprehensive configuration architecture supporting three-tier override model (global defaults, system profiles, user overrides) with hot-reloadable updates, strong schema validation, and cryptographic signing for trusted configuration bundles.

## Configuration Philosophy

### **Three-Tier Override Model**
1. **Global Defaults** - Source-controlled baseline settings for all environments
2. **System Profiles** - Environment-specific overrides (dev/staging/prod)  
3. **User Overrides** - Per-device, per-profile, and per-session customizations

### **Core Principles**
- **Hot-Reloadable**: All configurations support live updates via file watchers or API reload hooks
- **Secure & Declarative**: JSON5/TOML/YAML files with strong Zod schema validation
- **Cryptographically Signed**: Trusted config bundles can be signed and verified with Ed25519
- **Environment Aware**: Automatic profile selection based on deployment context

## Core Implementation

### **Configuration Management System**

```typescript
// Comprehensive configuration manager with hierarchical merging and validation
interface ConfigurationSchema {
  global: GlobalConfiguration;
  environments: Record<string, EnvironmentConfiguration>;
  user: UserConfiguration;
  agents: AgentConfiguration;
  secrets: SecretConfiguration;
}

interface GlobalConfiguration {
  system: SystemDefaults;
  prompts: PromptTemplates;
  aiProfiles: AIPersonalityConfigs;
  services: ServiceMappings;
}

interface EnvironmentConfiguration {
  name: string;
  telemetry: boolean;
  secureMode: boolean;
  auth: AuthenticationConfig;
  database: DatabaseConfig;
  vectorDb: VectorDbConfig;
  logging: LoggingConfig;
}

interface UserConfiguration {
  theme: string;
  fontSize: number;
  language: string;
  notifications: NotificationSettings;
  privacy: PrivacySettings;
  keybindings: KeyBindingConfig;
  session: SessionVariables;
}

// Comprehensive configuration manager with validation and hot-reloading
class SystemConfigurationManager {
  private configSchema: ZodSchema<ConfigurationSchema>;
  private currentConfig: ConfigurationSchema;
  private fileWatchers: Map<string, FileWatcher> = new Map();
  private changeListeners: Set<ConfigChangeListener> = new Set();
  private cryptoValidator: ConfigCryptoValidator;
  
  constructor(cryptoValidator: ConfigCryptoValidator) {
    this.cryptoValidator = cryptoValidator;
    this.configSchema = this.createConfigurationSchema();
  }
  
  async loadConfiguration(environment?: string): Promise<ConfigurationSchema> {
    // Load global defaults
    const globalConfig = await this.loadGlobalConfiguration();
    
    // Load environment-specific overrides
    const envConfig = environment 
      ? await this.loadEnvironmentConfiguration(environment)
      : {};
    
    // Load user-specific overrides
    const userConfig = await this.loadUserConfiguration();
    
    // Load agent-specific configurations
    const agentConfig = await this.loadAgentConfiguration();
    
    // Load secrets (encrypted)
    const secretConfig = await this.loadSecretConfiguration();
    
    // Merge configurations with proper precedence
    const mergedConfig = this.mergeConfigurations([
      globalConfig,
      envConfig,
      userConfig,
      agentConfig,
      { secrets: secretConfig }
    ]);
    
    // Validate merged configuration
    const validatedConfig = await this.validateConfiguration(mergedConfig);
    
    // Set up file watchers for hot-reloading
    await this.setupFileWatchers();
    
    this.currentConfig = validatedConfig;
    return validatedConfig;
  }
  
  async getConfig<T = any>(path: string): Promise<T> {
    return this.getNestedValue(this.currentConfig, path);
  }
  
  async setConfig(path: string, value: any): Promise<void> {
    // Validate the new value
    await this.validateConfigValue(path, value);
    
    // Update configuration
    this.setNestedValue(this.currentConfig, path, value);
    
    // Persist to appropriate file
    await this.persistConfigChange(path, value);
    
    // Notify listeners
    await this.notifyConfigChange(path, value);
  }
  
  async reloadConfiguration(): Promise<void> {
    const environment = process.env.NODE_ENV || 'development';
    this.currentConfig = await this.loadConfiguration(environment);
    
    // Notify all listeners of full reload
    await this.notifyConfigReload();
  }
  
  watchConfig(callback: ConfigChangeListener): () => void {
    this.changeListeners.add(callback);
    
    return () => {
      this.changeListeners.delete(callback);
    };
  }
  
  private async loadGlobalConfiguration(): Promise<Partial<ConfigurationSchema>> {
    const configFiles = [
      'config/global/defaults.yaml',
      'config/global/prompts.yaml',
      'config/global/ai-profiles.yaml',
      'config/global/services.yaml'
    ];
    
    const configs = await Promise.all(
      configFiles.map(file => this.loadConfigFile(file))
    );
    
    return {
      global: {
        system: configs[0],
        prompts: configs[1],
        aiProfiles: configs[2],
        services: configs[3]
      }
    };
  }
  
  private async loadEnvironmentConfiguration(
    environment: string
  ): Promise<Partial<ConfigurationSchema>> {
    try {
      const envConfig = await this.loadConfigFile(
        `config/environments/${environment}.yaml`
      );
      
      return { environments: { [environment]: envConfig } };
    } catch (error) {
      console.warn(`Environment config not found: ${environment}`);
      return {};
    }
  }
  
  private async loadUserConfiguration(): Promise<Partial<ConfigurationSchema>> {
    try {
      const userFiles = [
        'config/user/prefs.json5',
        'config/user/keybindings.json',
        'config/user/session.json'
      ];
      
      const configs = await Promise.all(
        userFiles.map(file => this.loadConfigFile(file))
      );
      
      return {
        user: {
          ...configs[0],
          keybindings: configs[1],
          session: configs[2]
        }
      };
    } catch (error) {
      console.warn('User configuration not found, using defaults');
      return { user: this.getDefaultUserConfig() };
    }
  }
  
  private async loadSecretConfiguration(): Promise<SecretConfiguration> {
    try {
      const encryptedSecrets = await this.loadConfigFile('config/secrets/vault.json');
      return await this.cryptoValidator.decryptSecrets(encryptedSecrets);
    } catch (error) {
      console.warn('Secret configuration not found or decryption failed');
      return {};
    }
  }
  
  private async validateConfiguration(
    config: Partial<ConfigurationSchema>
  ): Promise<ConfigurationSchema> {
    try {
      return this.configSchema.parse(config);
    } catch (error) {
      throw new Error(`Configuration validation failed: ${error.message}`);
    }
  }
  
  private mergeConfigurations(
    configs: Partial<ConfigurationSchema>[]
  ): Partial<ConfigurationSchema> {
    return configs.reduce((merged, config) => {
      return this.deepMerge(merged, config);
    }, {});
  }
  
  private async setupFileWatchers(): Promise<void> {
    const watchPaths = [
      'config/global/',
      'config/environments/',
      'config/user/',
      'config/agents/'
    ];
    
    for (const path of watchPaths) {
      const watcher = this.createFileWatcher(path, async (changedFile) => {
        console.log(`Configuration file changed: ${changedFile}`);
        await this.reloadConfiguration();
      });
      
      this.fileWatchers.set(path, watcher);
    }
  }
  
  private async persistConfigChange(path: string, value: any): Promise<void> {
    // Determine which file should store this configuration
    const targetFile = this.getTargetFileForPath(path);
    
    // Load current file content
    const currentContent = await this.loadConfigFile(targetFile);
    
    // Update the specific path
    this.setNestedValue(currentContent, this.getRelativePath(path), value);
    
    // Save back to file
    await this.saveConfigFile(targetFile, currentContent);
  }
  
  private async notifyConfigChange(path: string, value: any): Promise<void> {
    const changeEvent: ConfigChangeEvent = {
      path,
      value,
      previousValue: this.getNestedValue(this.currentConfig, path),
      timestamp: new Date(),
      source: 'user_update'
    };
    
    const notifications = Array.from(this.changeListeners).map(listener =>
      listener(changeEvent)
    );
    
    await Promise.allSettled(notifications);
  }
}

// Cryptographic configuration validation and signing
class ConfigCryptoValidator {
  private signingKey: CryptoKey;
  private verificationKeys: Map<string, CryptoKey> = new Map();
  
  async validateSignedConfig(
    configData: any,
    signature: string,
    signerId?: string
  ): Promise<boolean> {
    const verificationKey = signerId 
      ? this.verificationKeys.get(signerId)
      : this.signingKey;
    
    if (!verificationKey) {
      throw new Error(`Verification key not found for signer: ${signerId}`);
    }
    
    const canonicalConfig = JSON.stringify(configData, Object.keys(configData).sort());
    const messageBuffer = new TextEncoder().encode(canonicalConfig);
    const signatureBuffer = new Uint8Array(
      atob(signature).split('').map(c => c.charCodeAt(0))
    );
    
    return await crypto.subtle.verify(
      'Ed25519',
      verificationKey,
      signatureBuffer,
      messageBuffer
    );
  }
  
  async signConfig(configData: any): Promise<string> {
    const canonicalConfig = JSON.stringify(configData, Object.keys(configData).sort());
    const messageBuffer = new TextEncoder().encode(canonicalConfig);
    
    const signature = await crypto.subtle.sign(
      'Ed25519',
      this.signingKey,
      messageBuffer
    );
    
    return btoa(String.fromCharCode(...new Uint8Array(signature)));
  }
  
  async decryptSecrets(encryptedSecrets: EncryptedSecretsContainer): Promise<SecretConfiguration> {
    const secrets: SecretConfiguration = {};
    
    for (const [key, encryptedValue] of Object.entries(encryptedSecrets)) {
      try {
        secrets[key] = await this.decryptSecret(encryptedValue);
      } catch (error) {
        console.warn(`Failed to decrypt secret: ${key}`);
      }
    }
    
    return secrets;
  }
}

type ConfigChangeListener = (event: ConfigChangeEvent) => void | Promise<void>;

interface ConfigChangeEvent {
  path: string;
  value: any;
  previousValue: any;
  timestamp: Date;
  source: 'user_update' | 'file_change' | 'api_update' | 'environment_change';
}

interface SecretConfiguration {
  jwtSecret?: string;
  encryptionPassphrase?: string;
  apiKeys?: Record<string, string>;
  databaseCredentials?: DatabaseCredentials;
}
```

### **Configuration Schema Definitions**

```typescript
// Comprehensive Zod schemas for configuration validation
import { z } from 'zod';

const NotificationSettingsSchema = z.object({
  enabled: z.boolean().default(true),
  sound: z.boolean().default(false),
  vibration: z.boolean().default(true),
  types: z.array(z.string()).default(['system', 'agent', 'error'])
});

const PrivacySettingsSchema = z.object({
  telemetry: z.boolean().default(false),
  localLogging: z.boolean().default(true),
  shareUsageData: z.boolean().default(false),
  anonymizeData: z.boolean().default(true)
});

const UserConfigurationSchema = z.object({
  theme: z.string().default('dark'),
  fontSize: z.number().min(8).max(32).default(14),
  language: z.string().default('en-US'),
  notifications: NotificationSettingsSchema,
  privacy: PrivacySettingsSchema,
  keybindings: z.record(z.string()).default({}),
  session: z.record(z.any()).default({})
});

const DatabaseConfigSchema = z.object({
  uri: z.string(),
  pool: z.object({
    min: z.number().default(2),
    max: z.number().default(10)
  }).optional(),
  ssl: z.boolean().default(true),
  timeout: z.number().default(30000)
});

const ServiceConfigSchema = z.object({
  type: z.enum(['local', 'cloud']),
  baseUrl: z.string().url(),
  capabilities: z.array(z.string()),
  auth: z.object({
    type: z.enum(['none', 'bearer_token', 'api_key', 'oauth2']),
    tokenEnv: z.string().optional()
  }).optional()
});

const EnvironmentConfigurationSchema = z.object({
  name: z.string(),
  telemetry: z.boolean().default(false),
  secureMode: z.boolean().default(true),
  auth: z.object({
    require2FA: z.boolean().default(false),
    allowFallback: z.boolean().default(true),
    sessionTimeout: z.number().default(3600)
  }),
  database: DatabaseConfigSchema.optional(),
  vectorDb: z.object({
    provider: z.enum(['qdrant', 'chroma', 'pinecone']),
    host: z.string(),
    port: z.number(),
    credentials: z.record(z.string()).optional()
  }).optional(),
  logging: z.object({
    level: z.enum(['debug', 'info', 'warn', 'error']).default('info'),
    output: z.enum(['console', 'file', 'both']).default('console'),
    retention: z.number().default(30)
  })
});

const ConfigurationSchema = z.object({
  global: z.object({
    system: z.record(z.any()),
    prompts: z.record(z.string()),
    aiProfiles: z.record(z.any()),
    services: z.record(ServiceConfigSchema)
  }),
  environments: z.record(EnvironmentConfigurationSchema),
  user: UserConfigurationSchema,
  agents: z.record(z.any()).default({}),
  secrets: z.record(z.string()).default({})
});
```

## Configuration File Structure

### **Directory Layout**
```text
config/
├── global/
│   ├── defaults.yaml              # Core system-wide settings
│   ├── prompts.yaml               # Shared system prompt templates
│   ├── ai-profiles.yaml           # Default AI personality configs
│   └── services.yaml              # Built-in and external service mappings
├── environments/
│   ├── dev.yaml                   # Development overrides
│   ├── staging.yaml               # Staging environment settings
│   ├── prod.yaml                  # Production secure settings
│   └── test.yaml                  # Automated test environment
├── user/
│   ├── prefs.json5                # Per-user preferences
│   ├── vault.json                 # Encrypted credentials
│   ├── keybindings.json           # Custom key mappings
│   └── session.json               # Temporary session variables
├── secrets/
│   ├── jwt-secret.key             # Signing key for access tokens
│   ├── api-keys.env               # Environment variables for secrets
│   └── encryption-passphrase.txt  # Master vault passphrase
└── agents/
    ├── scheduler.yaml             # Agent-specific runtime behaviors
    ├── orchestrator.yaml          # Priority rules and delegation logic
    └── watchdog.yaml              # Crash recovery and error hooks
```

## For AI Agents

### When to Use System Configuration Architecture
- ✅ **Multi-environment deployments** requiring different settings per environment
- ✅ **User customization** supporting themes, preferences, and personalization
- ✅ **Secure configuration distribution** requiring cryptographic validation
- ✅ **Hot-reloadable systems** needing configuration updates without restart
- ❌ Don't use for simple static configurations that never change

### Key Implementation Points
- **Three-tier override hierarchy** ensures proper configuration precedence
- **Strong schema validation** prevents configuration errors at runtime
- **Cryptographic signing** ensures trusted configuration distribution
- **Hot-reloading capability** enables configuration updates without system restart
- **Secure secret management** with encrypted credential storage

### Integration with Current System
```typescript
// Integration with existing Kai-CD configuration system
interface KaiCDConfigIntegration {
  currentConfigManager: typeof configManager;
  
  async migrateToSystemConfiguration(): Promise<void> {
    // Migrate existing config structure to new three-tier model
    const currentConfig = await this.currentConfigManager.getAllConfig();
    
    // Split into appropriate tiers
    const globalConfig = this.extractGlobalDefaults(currentConfig);
    const userConfig = this.extractUserOverrides(currentConfig);
    
    // Create new configuration files
    await this.createConfigurationFiles(globalConfig, userConfig);
    
    // Initialize new configuration manager
    const newConfigManager = new SystemConfigurationManager(cryptoValidator);
    await newConfigManager.loadConfiguration();
  }
}
```

## Related Documentation
- **Implementation**: `./29_configuration-layers-and-control.md` - Configuration layer architecture
- **Security**: `../security/05_comprehensive-security-architecture.md` - Security framework
- **Current**: `../../current/implementation/configuration-management.md` - Current config system

## External References
- **Zod**: Runtime type validation library
- **JSON5**: Extended JSON format with comments
- **TOML**: Configuration file format
- **YAML**: Human-readable data serialization
</rewritten_file> 