---
title: "Configuration Management Architecture"
description: "Complete configuration system from current hierarchical setup to future kOS distributed configuration"
category: "current"
subcategory: "implementation"
context: "implementation_ready"
implementation_status: "active_implementation"
decision_scope: "major"
complexity: "high"
last_updated: "2025-01-20"
code_references:
  - "src/config/"
  - "src/core/config/"
  - "src/store/chromeStorage.ts"
  - "src/utils/configManager.ts"
related_documents:
  - "../architecture/01_system-architecture.md"
  - "../architecture/03_core-system-design.md"
  - "../deployment/01_deployment-architecture.md"
  - "../../future/architecture/"
---

# Configuration Management Architecture

## Agent Context
**For AI Agents**: Complete configuration management system with hierarchical configuration merging, type-safe access patterns, and hot-reloading capabilities. Use this when managing application configuration, implementing settings systems, understanding configuration patterns, or planning distributed configuration management. Critical foundation for all configuration work.

**Implementation Notes**: Contains three-tier override system (system/user/runtime), type-safe configuration API, hot-reloading capabilities, and Chrome storage integration. Includes working TypeScript interfaces and configuration management patterns.
**Quality Requirements**: Keep configuration patterns and access methods synchronized with actual implementation. Maintain accuracy of hierarchical merging and validation systems.
**Integration Points**: Foundation for all configuration management, links to deployment architecture, storage systems, and future distributed configuration for comprehensive settings management.

---

## Quick Summary
Complete configuration management system with hierarchical configuration merging, type-safe access patterns, hot-reloading capabilities, and evolution path to future kOS distributed configuration management.

## Current Implementation Status
- ✅ **Hierarchical Configuration**: Three-tier override system working
- ✅ **Type-Safe Access**: Centralized configuration API with TypeScript
- ✅ **Hot Reloading**: Live configuration updates supported
- ✅ **Chrome Storage Integration**: Persistent configuration storage
- 🔄 **Validation System**: Schema validation and error handling

---

## I. Configuration Philosophy & Architecture

### A. Core Principles

**Three-Tier Override Model**
1. **System Configuration** (`system.env.ts`) - Immutable application defaults
2. **User Configuration** (`user.env.ts`) - Personal overrides and customizations
3. **Runtime Configuration** - Temporary session-specific overrides

**Design Philosophy**
- **Declarative Configuration**: YAML/JSON/TypeScript configuration files
- **Type Safety**: Full TypeScript interface definitions
- **Hot Reloadable**: Live updates without application restart
- **Secure by Default**: Sensitive data encrypted and isolated
- **Validation First**: Schema validation for all configuration changes

### B. Configuration Hierarchy

```text
Configuration Precedence (highest to lowest):
┌─────────────────────────────────────┐
│  Runtime/Session Overrides         │ ← Temporary, in-memory
├─────────────────────────────────────┤
│  User Configuration                 │ ← Personal settings, gitignored
├─────────────────────────────────────┤
│  System Configuration               │ ← Application defaults
└─────────────────────────────────────┘
```

---

## II. Configuration Structure & Schema

### A. Master Configuration Interface

```typescript
export interface KaiConfiguration {
  // Network configuration
  networking: {
    defaultTimeoutMs: number;
    retryAttempts: number;
    localIPs: string[];
    remoteIPs: string[];
    enableMeshDiscovery: boolean;
  };
  
  // Service configuration
  services: {
    defaultModels: Record<string, string>;
    enabledCapabilities: string[];
    healthCheckInterval: number;
    maxConcurrentRequests: number;
  };
  
  // UI configuration
  ui: {
    theme: string;
    language: string;
    logLevel: 'debug' | 'info' | 'warn' | 'error';
    animationsEnabled: boolean;
    autoSave: boolean;
  };
  
  // Security configuration
  security: {
    vaultTimeout: number;
    autoLock: boolean;
    requireBiometric: boolean;
    encryptionAlgorithm: string;
  };
  
  // Agent configuration (future)
  agents?: {
    maxConcurrentAgents: number;
    defaultPersona: string;
    memoryRetention: 'session' | 'persistent';
    autonomyLevel: 'low' | 'medium' | 'high';
  };
  
  // Federation configuration (future)
  federation?: {
    enabled: boolean;
    discoveryProtocol: string;
    trustLevel: 'strict' | 'moderate' | 'permissive';
    peerTimeout: number;
  };
}
```

### B. Configuration Files

**System Configuration** (`src/config/system.env.ts`)
```typescript
export const systemConfig: KaiConfiguration = {
  networking: {
    defaultTimeoutMs: 30000,
    retryAttempts: 3,
    localIPs: ['127.0.0.1', '192.168.1.159'],
    remoteIPs: ['192.168.1.180'],
    enableMeshDiscovery: false
  },
  services: {
    defaultModels: {
      'ollama': 'llama3.2:latest',
      'openai': 'gpt-4',
      'anthropic': 'claude-3-sonnet'
    },
    enabledCapabilities: ['llm_chat', 'image_generation', 'embeddings'],
    healthCheckInterval: 30000,
    maxConcurrentRequests: 5
  },
  ui: {
    theme: 'dark-mode-professional',
    language: 'en',
    logLevel: 'info',
    animationsEnabled: true,
    autoSave: true
  },
  security: {
    vaultTimeout: 300000, // 5 minutes
    autoLock: true,
    requireBiometric: false,
    encryptionAlgorithm: 'AES-256-GCM'
  }
};
```

**User Configuration** (`src/config/user.env.ts` - Optional, gitignored)
```typescript
export const userConfig: Partial<KaiConfiguration> = {
  networking: {
    localIPs: ['127.0.0.1', '10.0.0.100'], // Override local IPs
    remoteIPs: ['192.168.1.200']           // Override remote IPs
  },
  ui: {
    theme: 'dark-mode-elite',              // Personal theme preference
    logLevel: 'debug'                      // Debug logging enabled
  },
  security: {
    vaultTimeout: 600000,                  // 10 minutes
    requireBiometric: true                 // Enable biometric unlock
  }
};
```

---

## III. Configuration Access & Management

### A. Centralized Configuration Manager

**Configuration Loader** (`src/core/config/index.ts`)
```typescript
import { systemConfig } from './system';
import { userConfig } from './user';
import { deepMerge } from '../utils/deepMerge';

class ConfigManager {
  private config: KaiConfiguration;
  private listeners: Set<(config: KaiConfiguration) => void> = new Set();
  
  constructor() {
    this.config = this.loadConfiguration();
  }
  
  private loadConfiguration(): KaiConfiguration {
    // Deep merge configuration layers
    const mergedConfig = deepMerge(
      systemConfig,
      userConfig || {},
      this.getRuntimeOverrides()
    );
    
    // Validate configuration
    return this.validateConfiguration(mergedConfig);
  }
  
  public get<T>(path: string): T {
    return this.getNestedValue(this.config, path);
  }
  
  public set<T>(path: string, value: T): Promise<void> {
    return this.setNestedValue(path, value);
  }
  
  public watch(callback: (config: KaiConfiguration) => void): () => void {
    this.listeners.add(callback);
    return () => this.listeners.delete(callback);
  }
  
  public reload(): void {
    const newConfig = this.loadConfiguration();
    this.config = newConfig;
    this.notifyListeners();
  }
  
  private notifyListeners(): void {
    this.listeners.forEach(listener => listener(this.config));
  }
  
  private validateConfiguration(config: any): KaiConfiguration {
    // Schema validation using Zod or similar
    return configSchema.parse(config);
  }
}

export const configManager = new ConfigManager();
```

**Type-Safe Configuration Access**
```typescript
// Utility functions for type-safe access
export function getConfigValue<T>(path: string): T {
  return configManager.get<T>(path);
}

export function setConfigValue<T>(path: string, value: T): Promise<void> {
  return configManager.set(path, value);
}

export function watchConfig(callback: (config: KaiConfiguration) => void): () => void {
  return configManager.watch(callback);
}

// Usage examples
const timeout = getConfigValue<number>('networking.defaultTimeoutMs');
const theme = getConfigValue<string>('ui.theme');
const localIPs = getConfigValue<string[]>('networking.localIPs');

await setConfigValue('ui.theme', 'dark-mode-elite');
await setConfigValue('security.vaultTimeout', 600000);
```

### B. Configuration Validation

**Schema Definition** (`src/core/config/schema.ts`)
```typescript
import { z } from 'zod';

const networkingSchema = z.object({
  defaultTimeoutMs: z.number().min(1000).max(300000),
  retryAttempts: z.number().min(1).max(10),
  localIPs: z.array(z.string().ip()),
  remoteIPs: z.array(z.string().ip()),
  enableMeshDiscovery: z.boolean()
});

const servicesSchema = z.object({
  defaultModels: z.record(z.string()),
  enabledCapabilities: z.array(z.string()),
  healthCheckInterval: z.number().min(5000),
  maxConcurrentRequests: z.number().min(1).max(20)
});

const uiSchema = z.object({
  theme: z.string(),
  language: z.string().length(2),
  logLevel: z.enum(['debug', 'info', 'warn', 'error']),
  animationsEnabled: z.boolean(),
  autoSave: z.boolean()
});

const securitySchema = z.object({
  vaultTimeout: z.number().min(60000), // Minimum 1 minute
  autoLock: z.boolean(),
  requireBiometric: z.boolean(),
  encryptionAlgorithm: z.string()
});

export const configSchema = z.object({
  networking: networkingSchema,
  services: servicesSchema,
  ui: uiSchema,
  security: securitySchema,
  agents: z.optional(z.object({})), // Future schema
  federation: z.optional(z.object({})) // Future schema
});
```

---

## IV. Storage & Persistence

### A. Chrome Storage Integration

**Storage Adapter** (`src/store/chromeStorage.ts`)
```typescript
export interface StorageAdapter {
  getItem(key: string): Promise<string | null>;
  setItem(key: string, value: string): Promise<void>;
  removeItem(key: string): Promise<void>;
}

export const chromeStorage: StorageAdapter = {
  async getItem(key: string): Promise<string | null> {
    const result = await chrome.storage.local.get([key]);
    return result[key] || null;
  },
  
  async setItem(key: string, value: string): Promise<void> {
    await chrome.storage.local.set({ [key]: value });
  },
  
  async removeItem(key: string): Promise<void> {
    await chrome.storage.local.remove([key]);
  }
};
```

**Configuration Persistence**
```typescript
class PersistentConfigManager extends ConfigManager {
  private readonly STORAGE_KEY = 'kai-config-overrides';
  
  async saveUserOverrides(overrides: Partial<KaiConfiguration>): Promise<void> {
    const serialized = JSON.stringify(overrides);
    await chromeStorage.setItem(this.STORAGE_KEY, serialized);
    this.reload(); // Reload with new overrides
  }
  
  async loadUserOverrides(): Promise<Partial<KaiConfiguration>> {
    const serialized = await chromeStorage.getItem(this.STORAGE_KEY);
    if (!serialized) return {};
    
    try {
      return JSON.parse(serialized);
    } catch (error) {
      console.warn('Failed to parse stored configuration:', error);
      return {};
    }
  }
  
  private getRuntimeOverrides(): Partial<KaiConfiguration> {
    // Load from Chrome storage
    return this.cachedUserOverrides || {};
  }
}
```

### B. Configuration Migration

**Migration System**
```typescript
interface ConfigMigration {
  version: string;
  migrate: (config: any) => any;
}

const migrations: ConfigMigration[] = [
  {
    version: '1.0.0',
    migrate: (config) => {
      // Migration from version 0.x to 1.0.0
      if (config.networking?.timeout) {
        config.networking.defaultTimeoutMs = config.networking.timeout;
        delete config.networking.timeout;
      }
      return config;
    }
  },
  {
    version: '1.1.0',
    migrate: (config) => {
      // Add new security defaults
      if (!config.security) {
        config.security = {
          vaultTimeout: 300000,
          autoLock: true,
          requireBiometric: false,
          encryptionAlgorithm: 'AES-256-GCM'
        };
      }
      return config;
    }
  }
];

export function migrateConfiguration(config: any, fromVersion: string): any {
  let migratedConfig = { ...config };
  
  for (const migration of migrations) {
    if (semver.gt(migration.version, fromVersion)) {
      migratedConfig = migration.migrate(migratedConfig);
    }
  }
  
  return migratedConfig;
}
```

---

## V. Hot Reloading & Live Updates

### A. Configuration Watching

**File System Watcher** (Development)
```typescript
class DevConfigWatcher {
  private watchers: Map<string, FSWatcher> = new Map();
  
  startWatching(): void {
    const configFiles = [
      'src/config/system.env.ts',
      'src/config/user.env.ts'
    ];
    
    configFiles.forEach(file => {
      const watcher = fs.watch(file, (eventType) => {
        if (eventType === 'change') {
          this.handleConfigChange(file);
        }
      });
      
      this.watchers.set(file, watcher);
    });
  }
  
  private async handleConfigChange(file: string): Promise<void> {
    try {
      // Clear module cache
      delete require.cache[require.resolve(file)];
      
      // Reload configuration
      configManager.reload();
      
      console.log(`Configuration reloaded from ${file}`);
    } catch (error) {
      console.error(`Failed to reload configuration from ${file}:`, error);
    }
  }
  
  stop(): void {
    this.watchers.forEach(watcher => watcher.close());
    this.watchers.clear();
  }
}
```

### B. Runtime Configuration Updates

**Live Configuration API**
```typescript
export class LiveConfigManager {
  async updateConfiguration(
    path: string,
    value: any,
    persist: boolean = true
  ): Promise<void> {
    // Validate the update
    const validation = this.validateConfigUpdate(path, value);
    if (!validation.valid) {
      throw new Error(`Invalid configuration update: ${validation.error}`);
    }
    
    // Apply the update
    await configManager.set(path, value);
    
    // Persist if requested
    if (persist) {
      await this.persistConfigUpdate(path, value);
    }
    
    // Notify components
    this.notifyConfigUpdate(path, value);
  }
  
  private async persistConfigUpdate(path: string, value: any): Promise<void> {
    const currentOverrides = await this.loadUserOverrides();
    const updatedOverrides = this.setNestedValue(currentOverrides, path, value);
    await this.saveUserOverrides(updatedOverrides);
  }
  
  private notifyConfigUpdate(path: string, value: any): void {
    // Emit configuration change event
    window.dispatchEvent(new CustomEvent('config-change', {
      detail: { path, value }
    }));
  }
}
```

---

## VI. Security & Validation

### A. Configuration Security

**Sensitive Data Handling**
```typescript
interface SecureConfigValue {
  encrypted: boolean;
  value: string;
  algorithm?: string;
}

class SecureConfigManager {
  private encryptionKey: CryptoKey | null = null;
  
  async setSecureValue(path: string, value: string): Promise<void> {
    if (!this.encryptionKey) {
      this.encryptionKey = await this.generateEncryptionKey();
    }
    
    const encrypted = await this.encrypt(value);
    const secureValue: SecureConfigValue = {
      encrypted: true,
      value: encrypted,
      algorithm: 'AES-256-GCM'
    };
    
    await configManager.set(path, secureValue);
  }
  
  async getSecureValue(path: string): Promise<string> {
    const secureValue = configManager.get<SecureConfigValue>(path);
    
    if (!secureValue.encrypted) {
      return secureValue.value;
    }
    
    return await this.decrypt(secureValue.value);
  }
  
  private async encrypt(plaintext: string): Promise<string> {
    // Implementation using Web Crypto API
    const encoder = new TextEncoder();
    const data = encoder.encode(plaintext);
    
    const iv = crypto.getRandomValues(new Uint8Array(12));
    const encrypted = await crypto.subtle.encrypt(
      { name: 'AES-GCM', iv },
      this.encryptionKey!,
      data
    );
    
    return btoa(JSON.stringify({
      iv: Array.from(iv),
      data: Array.from(new Uint8Array(encrypted))
    }));
  }
}
```

### B. Configuration Validation

**Real-time Validation**
```typescript
export class ConfigValidator {
  validateUpdate(path: string, value: any): ValidationResult {
    const pathParts = path.split('.');
    const schema = this.getSchemaForPath(pathParts);
    
    try {
      schema.parse(value);
      return { valid: true };
    } catch (error) {
      return {
        valid: false,
        error: error.message,
        path
      };
    }
  }
  
  validateFullConfig(config: any): ValidationResult {
    try {
      configSchema.parse(config);
      return { valid: true };
    } catch (error) {
      return {
        valid: false,
        error: error.message,
        details: error.errors
      };
    }
  }
  
  private getSchemaForPath(pathParts: string[]): z.ZodSchema {
    // Navigate schema based on path
    let currentSchema = configSchema;
    
    for (const part of pathParts) {
      if (currentSchema instanceof z.ZodObject) {
        currentSchema = currentSchema.shape[part];
      }
    }
    
    return currentSchema;
  }
}
```

---

## VII. Future Evolution: kOS Configuration

### A. Distributed Configuration Architecture

**kOS Configuration Vision**
```typescript
interface KOSConfiguration extends KaiConfiguration {
  // Distributed system configuration
  cluster: {
    nodeId: string;
    discoveryService: string;
    heartbeatInterval: number;
    electionTimeout: number;
  };
  
  // Agent mesh configuration
  agents: {
    maxConcurrentAgents: number;
    defaultPersona: string;
    memoryRetention: 'session' | 'persistent' | 'distributed';
    autonomyLevel: 'low' | 'medium' | 'high';
    communicationProtocol: 'klp' | 'http' | 'websocket';
  };
  
  // Federation configuration
  federation: {
    enabled: boolean;
    discoveryProtocol: 'dns-sd' | 'mdns' | 'manual';
    trustLevel: 'strict' | 'moderate' | 'permissive';
    peerTimeout: number;
    maxPeers: number;
  };
  
  // Service mesh configuration
  mesh: {
    enabled: boolean;
    loadBalancing: 'round-robin' | 'least-connections' | 'random';
    circuitBreaker: boolean;
    retryPolicy: 'exponential' | 'linear' | 'none';
  };
}
```

### B. Configuration Synchronization

**Multi-Node Configuration Sync**
```typescript
class DistributedConfigManager extends ConfigManager {
  private peers: Set<string> = new Set();
  private syncInterval: number = 30000; // 30 seconds
  
  async syncConfiguration(): Promise<void> {
    const localConfig = this.getConfiguration();
    const configHash = await this.calculateConfigHash(localConfig);
    
    for (const peer of this.peers) {
      try {
        const peerHash = await this.getPeerConfigHash(peer);
        
        if (configHash !== peerHash) {
          await this.synchronizeWithPeer(peer, localConfig);
        }
      } catch (error) {
        console.warn(`Failed to sync with peer ${peer}:`, error);
      }
    }
  }
  
  private async synchronizeWithPeer(
    peer: string,
    localConfig: KOSConfiguration
  ): Promise<void> {
    const peerConfig = await this.getPeerConfiguration(peer);
    const mergedConfig = this.mergeConfigurations(localConfig, peerConfig);
    
    // Apply conflict resolution
    const resolvedConfig = this.resolveConfigConflicts(mergedConfig);
    
    // Update local configuration
    await this.updateConfiguration(resolvedConfig);
    
    // Notify peer of changes
    await this.notifyPeerOfChanges(peer, resolvedConfig);
  }
}
```

---

## VIII. Development & Testing

### A. Configuration Testing

**Unit Tests**
```typescript
describe('ConfigManager', () => {
  let configManager: ConfigManager;
  
  beforeEach(() => {
    configManager = new ConfigManager();
  });
  
  it('should merge configurations correctly', () => {
    const result = configManager.get<number>('networking.defaultTimeoutMs');
    expect(result).toBe(30000);
  });
  
  it('should handle user overrides', async () => {
    await configManager.set('ui.theme', 'custom-theme');
    const theme = configManager.get<string>('ui.theme');
    expect(theme).toBe('custom-theme');
  });
  
  it('should validate configuration updates', async () => {
    await expect(
      configManager.set('networking.defaultTimeoutMs', -1)
    ).rejects.toThrow('Invalid configuration');
  });
});
```

### B. Configuration Debugging

**Debug Tools**
```typescript
export class ConfigDebugger {
  static dumpConfiguration(): void {
    const config = configManager.getConfiguration();
    console.table(this.flattenConfig(config));
  }
  
  static validateConfiguration(): ValidationResult {
    const config = configManager.getConfiguration();
    return new ConfigValidator().validateFullConfig(config);
  }
  
  static traceConfigValue(path: string): ConfigTrace {
    return {
      path,
      value: configManager.get(path),
      source: this.getValueSource(path),
      schema: this.getSchemaForPath(path)
    };
  }
  
  private static flattenConfig(
    obj: any,
    prefix: string = ''
  ): Record<string, any> {
    const flattened: Record<string, any> = {};
    
    for (const [key, value] of Object.entries(obj)) {
      const fullKey = prefix ? `${prefix}.${key}` : key;
      
      if (typeof value === 'object' && value !== null) {
        Object.assign(flattened, this.flattenConfig(value, fullKey));
      } else {
        flattened[fullKey] = value;
      }
    }
    
    return flattened;
  }
}
```

---

## IX. Agent Implementation Notes

- Configuration system provides foundation for distributed kOS architecture
- Type-safe access patterns ensure reliable configuration management
- Hot reloading supports rapid development and testing
- Security model protects sensitive configuration data
- Migration system enables smooth version upgrades
- Validation ensures configuration integrity across all layers

