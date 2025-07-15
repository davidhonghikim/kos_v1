---
title: "System Configuration Architecture"
description: "Three-tier configuration system with user, agent, and infrastructure layers"
type: "architecture"
category: "implementation"
subcategory: "system-configuration"
context: "kAI/kOS system configuration management with multi-tier overrides"
implementation_status: "future"
decision_scope: "system-wide"
complexity: "high"
last_updated: "2025-01-20"
code_references: ["config/", "src/core/config/", "src/core/security/"]
related_documents: ["07_configuration-layers-and-control.md", "06_installer-and-initialization.md"]
dependencies: ["JSON5/TOML/YAML parsers", "Zod validation", "AES encryption", "Ed25519 signing"]
breaking_changes: "None - new configuration architecture"
agent_notes: "Complete configuration architecture with three-tier overrides, hot-reloading, security, and centralized management"
---

# System Configuration Architecture

## Agent Context

This document defines the full configuration architecture for kAI and kOS, covering user-level preferences, agent-specific runtime settings, and infrastructure deployment parameters. The system supports centralized management with modular override options at each level.

**Implementation Guidance**: Use this architecture for implementing comprehensive configuration management with secure signing, hot-reloading, and multi-environment support. All configuration access should be validated and audited.

## Quick Summary

Three-tier configuration system with global defaults, system profiles, and user overrides supporting hot-reloading, cryptographic signing, centralized management, and environment-specific deployments.

## I. Configuration Philosophy

### Three-Tier Override Model

1. **Global Defaults** (checked into source)
2. **System Profiles** (environment-specific: dev/staging/prod)
3. **User Overrides** (per-device, per-profile, per-session)

### Core Principles

- **Hot-Reloadable**: All configs support live updates via file watchers or API reload hooks
- **Secure & Declarative**: All config files are JSON5 / TOML / YAML with strong schema validation via Zod
- **Cryptographic Signing (Optional)**: Trusted config bundles (e.g., from enterprise admins) can be signed and verified

## II. Directory Layout (Config Files)

```typescript
config/
├── global/
│   ├── defaults.yaml              # Core system-wide settings
│   ├── prompts.yaml               # Shared system prompt templates
│   ├── ai-profiles.yaml           # Default AI personality configs
│   └── services.yaml              # Built-in and external service mappings
├── environments/
│   ├── dev.yaml                   # Dev overrides
│   ├── prod.yaml                  # Production secure settings
│   └── test.yaml                  # For automated test environments
├── user/
│   ├── prefs.json5                # Per-user preferences (theme, hotkeys)
│   ├── vault.json                 # Encrypted credentials
│   ├── keybindings.json           # Custom key mappings
│   └── session.json               # Temporary session variables
├── secrets/
│   ├── jwt-secret.key             # Signing key for access tokens
│   ├── api-keys.env               # Dotenv-compatible secrets
│   └── encryption-passphrase.txt  # Master vault passphrase (optional)
└── agents/
    ├── scheduler.yaml             # Agent-specific runtime behaviors
    ├── orchestrator.yaml          # Priority rules and delegation logic
    └── watchdog.yaml              # Crash recovery and error hooks
```

## III. Configuration Schemas (Examples)

### A. User Preferences (`prefs.json5`)

```typescript
interface UserPreferences {
  theme: "dark" | "light" | "auto";
  fontSize: number;
  language: string;
  notifications: NotificationSettings;
  privacy: PrivacySettings;
  accessibility: AccessibilitySettings;
  keybindings: Record<string, string>;
}

interface NotificationSettings {
  enabled: boolean;
  sound: boolean;
  vibration: boolean;
  desktop: boolean;
  types: {
    agent_completion: boolean;
    service_errors: boolean;
    security_alerts: boolean;
    system_updates: boolean;
  };
}

interface PrivacySettings {
  telemetry: boolean;
  localLogging: boolean;
  shareUsageData: boolean;
  allowRemoteSync: boolean;
  encryptLocalStorage: boolean;
}

interface AccessibilitySettings {
  highContrast: boolean;
  largeText: boolean;
  screenReader: boolean;
  keyboardNavigation: boolean;
  reducedMotion: boolean;
}

// Example JSON5 configuration
const examplePrefs = {
  theme: "dark",
  fontSize: 14,
  language: "en-US",
  notifications: {
    enabled: true,
    sound: false,
    vibration: true,
    desktop: true,
    types: {
      agent_completion: true,
      service_errors: true,
      security_alerts: true,
      system_updates: false
    }
  },
  privacy: {
    telemetry: false,
    localLogging: true,
    shareUsageData: false,
    allowRemoteSync: true,
    encryptLocalStorage: true
  },
  accessibility: {
    highContrast: false,
    largeText: false,
    screenReader: false,
    keyboardNavigation: true,
    reducedMotion: false
  },
  keybindings: {
    "toggle_sidebar": "Ctrl+B",
    "new_chat": "Ctrl+N",
    "search": "Ctrl+K",
    "settings": "Ctrl+,"
  }
};
```

### B. Service Definitions (`services.yaml`)

```typescript
interface ServiceConfiguration {
  [serviceId: string]: ServiceConfig;
}

interface ServiceConfig {
  type: "local" | "cloud";
  baseUrl: string;
  capabilities: string[];
  auth?: AuthConfig;
  timeout?: number;
  retries?: number;
  rateLimit?: RateLimitConfig;
  healthCheck?: HealthCheckConfig;
  metadata?: Record<string, any>;
}

interface AuthConfig {
  type: "bearer_token" | "api_key" | "oauth" | "none";
  tokenEnv?: string;
  endpoint?: string;
  scope?: string[];
}

interface RateLimitConfig {
  requests: number;
  window: number; // seconds
  burst?: number;
}

interface HealthCheckConfig {
  endpoint: string;
  interval: number;
  timeout: number;
  retries: number;
}

// YAML Example
const servicesYaml = `
ollama:
  type: local
  baseUrl: "http://localhost:11434"
  capabilities: [llm_chat, embeddings]
  timeout: 30000
  healthCheck:
    endpoint: "/api/tags"
    interval: 60000
    timeout: 5000
    retries: 3
  
openai:
  type: cloud
  baseUrl: "https://api.openai.com/v1"
  capabilities: [llm_chat, embeddings, image_generation]
  auth:
    type: bearer_token
    tokenEnv: OPENAI_API_KEY
  timeout: 60000
  retries: 3
  rateLimit:
    requests: 60
    window: 60
    burst: 10
  healthCheck:
    endpoint: "/models"
    interval: 300000
    timeout: 10000
    retries: 2

chroma:
  type: local
  baseUrl: "http://localhost:8000"
  capabilities: [vector_storage, similarity_search]
  timeout: 15000
  healthCheck:
    endpoint: "/api/v1/heartbeat"
    interval: 30000
    timeout: 3000
    retries: 2
`;
```

### C. Agent Runtime (`scheduler.yaml`)

```typescript
interface AgentRuntimeConfig {
  scheduler: SchedulerConfig;
  orchestrator: OrchestratorConfig;
  watchdog: WatchdogConfig;
}

interface SchedulerConfig {
  maxConcurrentTasks: number;
  retryPolicy: RetryPolicy;
  allowedHours: TimeWindow;
  resources: ResourceLimits;
  priorities: PriorityConfig;
}

interface RetryPolicy {
  retries: number;
  backoff: number;
  backoffMultiplier: number;
  maxBackoff: number;
  retryableErrors: string[];
}

interface TimeWindow {
  start: string;
  end: string;
  timezone?: string;
}

interface ResourceLimits {
  maxMemoryMB: number;
  maxCpuPercent: number;
  maxDiskMB: number;
  maxNetworkMbps: number;
}

interface PriorityConfig {
  default: number;
  user_initiated: number;
  system_maintenance: number;
  emergency: number;
}

interface OrchestratorConfig {
  delegationRules: DelegationRule[];
  loadBalancing: LoadBalancingConfig;
  failover: FailoverConfig;
}

interface DelegationRule {
  capability: string;
  conditions: Record<string, any>;
  target: string;
  priority: number;
}

interface LoadBalancingConfig {
  strategy: "round_robin" | "least_connections" | "weighted" | "random";
  weights?: Record<string, number>;
  healthCheck: boolean;
}

interface FailoverConfig {
  enabled: boolean;
  maxFailures: number;
  cooldownSeconds: number;
  fallbackAgents: string[];
}

interface WatchdogConfig {
  enabled: boolean;
  checkInterval: number;
  restartThreshold: number;
  crashRecovery: CrashRecoveryConfig;
  alerts: AlertConfig[];
}

interface CrashRecoveryConfig {
  autoRestart: boolean;
  maxRestarts: number;
  restartDelay: number;
  preserveState: boolean;
  backupFrequency: number;
}

interface AlertConfig {
  type: "email" | "webhook" | "log" | "desktop";
  threshold: string;
  config: Record<string, any>;
}

// YAML Example
const agentRuntimeYaml = `
scheduler:
  maxConcurrentTasks: 5
  retryPolicy:
    retries: 3
    backoff: 2000
    backoffMultiplier: 2
    maxBackoff: 30000
    retryableErrors: ["timeout", "connection", "rate_limit"]
  allowedHours:
    start: "07:00"
    end: "23:00"
    timezone: "UTC"
  resources:
    maxMemoryMB: 512
    maxCpuPercent: 50
    maxDiskMB: 1024
    maxNetworkMbps: 10
  priorities:
    default: 5
    user_initiated: 8
    system_maintenance: 3
    emergency: 10

orchestrator:
  delegationRules:
    - capability: "llm_chat"
      conditions: { "model_size": "large" }
      target: "gpu_agent"
      priority: 8
    - capability: "vector_search"
      conditions: { "dataset_size": ">1M" }
      target: "vector_agent"
      priority: 7
  loadBalancing:
    strategy: "least_connections"
    healthCheck: true
  failover:
    enabled: true
    maxFailures: 3
    cooldownSeconds: 300
    fallbackAgents: ["backup_agent", "emergency_agent"]

watchdog:
  enabled: true
  checkInterval: 30000
  restartThreshold: 3
  crashRecovery:
    autoRestart: true
    maxRestarts: 5
    restartDelay: 5000
    preserveState: true
    backupFrequency: 300000
  alerts:
    - type: "log"
      threshold: "error"
      config: { level: "error", file: "watchdog.log" }
    - type: "webhook"
      threshold: "critical"
      config: { url: "https://alerts.example.com/webhook" }
`;
```

### D. Infrastructure Environment (`prod.yaml`)

```typescript
interface InfrastructureConfig {
  environment: string;
  telemetry: TelemetryConfig;
  secureMode: boolean;
  auth: AuthenticationConfig;
  database: DatabaseConfig;
  vectorDb: VectorDbConfig;
  cache: CacheConfig;
  networking: NetworkingConfig;
  monitoring: MonitoringConfig;
  backup: BackupConfig;
}

interface TelemetryConfig {
  enabled: boolean;
  endpoint?: string;
  sampleRate: number;
  includePersonalData: boolean;
  retention: number;
}

interface AuthenticationConfig {
  require2FA: boolean;
  allowFallback: boolean;
  sessionTimeout: number;
  maxFailedAttempts: number;
  lockoutDuration: number;
  passwordPolicy: PasswordPolicy;
}

interface PasswordPolicy {
  minLength: number;
  requireUppercase: boolean;
  requireLowercase: boolean;
  requireNumbers: boolean;
  requireSymbols: boolean;
  maxAge: number;
  historyCount: number;
}

interface DatabaseConfig {
  postgres?: PostgresConfig;
  redis?: RedisConfig;
  sqlite?: SqliteConfig;
}

interface PostgresConfig {
  uri: string;
  poolSize: number;
  timeout: number;
  ssl: boolean;
  migrations: boolean;
}

interface RedisConfig {
  uri: string;
  ttl: number;
  maxMemory: string;
  evictionPolicy: string;
}

interface SqliteConfig {
  path: string;
  wal: boolean;
  backup: boolean;
}

interface VectorDbConfig {
  provider: "qdrant" | "chroma" | "weaviate" | "pinecone";
  host: string;
  port: number;
  apiKey?: string;
  collection: string;
  dimensions: number;
  distance: "cosine" | "euclidean" | "dot";
}

interface CacheConfig {
  provider: "redis" | "memory" | "disk";
  ttl: number;
  maxSize: string;
  compression: boolean;
}

interface NetworkingConfig {
  cors: CorsConfig;
  rateLimit: GlobalRateLimitConfig;
  proxy: ProxyConfig;
  ssl: SslConfig;
}

interface CorsConfig {
  enabled: boolean;
  origins: string[];
  methods: string[];
  headers: string[];
  credentials: boolean;
}

interface GlobalRateLimitConfig {
  enabled: boolean;
  requests: number;
  window: number;
  skipSuccessful: boolean;
}

interface ProxyConfig {
  enabled: boolean;
  upstream: string;
  timeout: number;
  retries: number;
}

interface SslConfig {
  enabled: boolean;
  cert: string;
  key: string;
  ca?: string;
}

interface MonitoringConfig {
  metrics: MetricsConfig;
  logging: LoggingConfig;
  alerts: AlertingConfig;
}

interface MetricsConfig {
  enabled: boolean;
  endpoint: string;
  interval: number;
  retention: number;
}

interface LoggingConfig {
  level: "debug" | "info" | "warn" | "error";
  format: "json" | "text";
  output: "console" | "file" | "both";
  rotation: LogRotationConfig;
}

interface LogRotationConfig {
  maxSize: string;
  maxFiles: number;
  compress: boolean;
}

interface AlertingConfig {
  enabled: boolean;
  channels: AlertChannel[];
  rules: AlertRule[];
}

interface AlertChannel {
  type: "email" | "slack" | "webhook" | "pagerduty";
  config: Record<string, any>;
}

interface AlertRule {
  name: string;
  condition: string;
  severity: "low" | "medium" | "high" | "critical";
  channels: string[];
}

interface BackupConfig {
  enabled: boolean;
  schedule: string;
  retention: number;
  encryption: boolean;
  destinations: BackupDestination[];
}

interface BackupDestination {
  type: "local" | "s3" | "gcs" | "azure";
  config: Record<string, any>;
}

// YAML Example
const prodYaml = `
environment: "production"
telemetry:
  enabled: true
  endpoint: "https://telemetry.example.com"
  sampleRate: 0.1
  includePersonalData: false
  retention: 2592000  # 30 days

secureMode: true

auth:
  require2FA: true
  allowFallback: false
  sessionTimeout: 3600
  maxFailedAttempts: 5
  lockoutDuration: 1800
  passwordPolicy:
    minLength: 12
    requireUppercase: true
    requireLowercase: true
    requireNumbers: true
    requireSymbols: true
    maxAge: 7776000  # 90 days
    historyCount: 12

database:
  postgres:
    uri: "postgresql://kuser:pass@db.internal:5432/kind"
    poolSize: 20
    timeout: 30000
    ssl: true
    migrations: true
  redis:
    uri: "redis://redis.internal:6379"
    ttl: 86400
    maxMemory: "256mb"
    evictionPolicy: "allkeys-lru"

vectorDb:
  provider: qdrant
  host: "qdrant.internal"
  port: 6333
  apiKey: "\${QDRANT_API_KEY}"
  collection: "embeddings"
  dimensions: 1536
  distance: "cosine"

cache:
  provider: "redis"
  ttl: 3600
  maxSize: "128mb"
  compression: true

networking:
  cors:
    enabled: true
    origins: ["https://app.example.com"]
    methods: ["GET", "POST", "PUT", "DELETE"]
    headers: ["Authorization", "Content-Type"]
    credentials: true
  rateLimit:
    enabled: true
    requests: 1000
    window: 3600
    skipSuccessful: false
  ssl:
    enabled: true
    cert: "/etc/ssl/certs/app.crt"
    key: "/etc/ssl/private/app.key"

monitoring:
  metrics:
    enabled: true
    endpoint: "http://prometheus:9090"
    interval: 15000
    retention: 2592000
  logging:
    level: "info"
    format: "json"
    output: "both"
    rotation:
      maxSize: "100mb"
      maxFiles: 10
      compress: true
  alerts:
    enabled: true
    channels:
      - type: "slack"
        config: { webhook: "\${SLACK_WEBHOOK}" }
      - type: "email"
        config: { smtp: "smtp.example.com", from: "alerts@example.com" }
    rules:
      - name: "High CPU Usage"
        condition: "cpu_usage > 80"
        severity: "high"
        channels: ["slack", "email"]
      - name: "Database Connection Failed"
        condition: "db_connection_failed"
        severity: "critical"
        channels: ["slack", "email"]

backup:
  enabled: true
  schedule: "0 2 * * *"  # Daily at 2 AM
  retention: 30
  encryption: true
  destinations:
    - type: "s3"
      config: 
        bucket: "backups-example"
        region: "us-west-2"
        accessKey: "\${AWS_ACCESS_KEY}"
        secretKey: "\${AWS_SECRET_KEY}"
    - type: "local"
      config:
        path: "/var/backups/kai"
`;
```

## IV. Configuration Access API

```typescript
interface ConfigurationManager {
  load(): Promise<void>;
  reload(): Promise<void>;
  get<T>(path: string): T | undefined;
  set<T>(path: string, value: T): Promise<void>;
  watch(path: string, callback: (value: any) => void): () => void;
  validate(): ValidationResult;
  export(format: 'yaml' | 'json'): string;
  import(data: string, format: 'yaml' | 'json'): Promise<void>;
}

class ConfigManager implements ConfigurationManager {
  private config: any = {};
  private watchers: Map<string, ((value: any) => void)[]> = new Map();
  private validators: Map<string, z.ZodSchema> = new Map();
  
  async load(): Promise<void> {
    // Load configuration from all sources in order
    const globalDefaults = await this.loadYaml('config/global/defaults.yaml');
    const envConfig = await this.loadYaml(`config/environments/${process.env.NODE_ENV || 'dev'}.yaml`);
    const userPrefs = await this.loadJson5('config/user/prefs.json5');
    const agentConfigs = await this.loadAgentConfigs();
    const sessionConfig = await this.loadJson('config/user/session.json');
    
    // Merge configurations with proper precedence
    this.config = this.deepMerge(
      globalDefaults,
      envConfig,
      userPrefs,
      agentConfigs,
      sessionConfig
    );
    
    // Validate merged configuration
    const validation = this.validate();
    if (!validation.valid) {
      throw new Error(`Configuration validation failed: ${validation.errors.join(', ')}`);
    }
    
    // Start file watchers
    this.startFileWatchers();
  }
  
  async reload(): Promise<void> {
    this.stopFileWatchers();
    await this.load();
    this.notifyAllWatchers();
  }
  
  get<T>(path: string): T | undefined {
    return this.getNestedValue(this.config, path);
  }
  
  async set<T>(path: string, value: T): Promise<void> {
    // Determine which config file to update based on path
    const configFile = this.determineConfigFile(path);
    
    // Update the specific config file
    await this.updateConfigFile(configFile, path, value);
    
    // Update in-memory config
    this.setNestedValue(this.config, path, value);
    
    // Notify watchers
    this.notifyWatchers(path, value);
  }
  
  watch(path: string, callback: (value: any) => void): () => void {
    if (!this.watchers.has(path)) {
      this.watchers.set(path, []);
    }
    
    this.watchers.get(path)!.push(callback);
    
    // Return unwatch function
    return () => {
      const callbacks = this.watchers.get(path);
      if (callbacks) {
        const index = callbacks.indexOf(callback);
        if (index > -1) {
          callbacks.splice(index, 1);
        }
      }
    };
  }
  
  validate(): ValidationResult {
    const errors: string[] = [];
    
    // Validate against registered schemas
    for (const [path, schema] of this.validators.entries()) {
      const value = this.get(path);
      const result = schema.safeParse(value);
      
      if (!result.success) {
        errors.push(`${path}: ${result.error.message}`);
      }
    }
    
    // Additional custom validations
    errors.push(...this.customValidations());
    
    return {
      valid: errors.length === 0,
      errors
    };
  }
  
  export(format: 'yaml' | 'json'): string {
    if (format === 'yaml') {
      return yaml.dump(this.config);
    } else {
      return JSON.stringify(this.config, null, 2);
    }
  }
  
  async import(data: string, format: 'yaml' | 'json'): Promise<void> {
    let importedConfig: any;
    
    if (format === 'yaml') {
      importedConfig = yaml.load(data);
    } else {
      importedConfig = JSON.parse(data);
    }
    
    // Validate imported config
    const tempConfig = this.deepMerge(this.config, importedConfig);
    const validation = this.validateConfig(tempConfig);
    
    if (!validation.valid) {
      throw new Error(`Invalid configuration: ${validation.errors.join(', ')}`);
    }
    
    // Apply imported config
    this.config = tempConfig;
    
    // Save to appropriate files
    await this.saveImportedConfig(importedConfig);
    
    // Notify watchers
    this.notifyAllWatchers();
  }
  
  // Schema registration for validation
  registerSchema(path: string, schema: z.ZodSchema): void {
    this.validators.set(path, schema);
  }
  
  private deepMerge(...objects: any[]): any {
    return objects.reduce((acc, obj) => {
      for (const key in obj) {
        if (obj[key] && typeof obj[key] === 'object' && !Array.isArray(obj[key])) {
          acc[key] = this.deepMerge(acc[key] || {}, obj[key]);
        } else {
          // Check for @locked annotation
          if (!acc[key] || !obj[key]?.['@locked']) {
            acc[key] = obj[key];
          }
        }
      }
      return acc;
    }, {});
  }
  
  private getNestedValue(obj: any, path: string): any {
    return path.split('.').reduce((current, key) => current?.[key], obj);
  }
  
  private setNestedValue(obj: any, path: string, value: any): void {
    const keys = path.split('.');
    const lastKey = keys.pop()!;
    const target = keys.reduce((current, key) => {
      if (!current[key]) current[key] = {};
      return current[key];
    }, obj);
    
    target[lastKey] = value;
  }
  
  private notifyWatchers(path: string, value: any): void {
    const callbacks = this.watchers.get(path);
    if (callbacks) {
      callbacks.forEach(callback => callback(value));
    }
  }
  
  private notifyAllWatchers(): void {
    for (const [path, callbacks] of this.watchers.entries()) {
      const value = this.get(path);
      callbacks.forEach(callback => callback(value));
    }
  }
  
  private customValidations(): string[] {
    const errors: string[] = [];
    
    // Example custom validations
    const dbConfig = this.get('database');
    if (dbConfig && !dbConfig.postgres && !dbConfig.sqlite) {
      errors.push('At least one database configuration is required');
    }
    
    const authConfig = this.get('auth');
    if (authConfig?.require2FA && !authConfig.passwordPolicy) {
      errors.push('Password policy required when 2FA is enabled');
    }
    
    return errors;
  }
}

// Usage Examples
const configManager = new ConfigManager();

// Register validation schemas
configManager.registerSchema('user.preferences', UserPreferencesSchema);
configManager.registerSchema('database', DatabaseConfigSchema);
configManager.registerSchema('auth', AuthenticationConfigSchema);

// Load configuration
await configManager.load();

// Get configuration values
const theme = configManager.get<string>('user.preferences.theme');
const dbUri = configManager.get<string>('database.postgres.uri');
const require2FA = configManager.get<boolean>('auth.require2FA');

// Set configuration values
await configManager.set('user.preferences.theme', 'dark');
await configManager.set('scheduler.maxConcurrentTasks', 10);

// Watch for changes
const unwatchTheme = configManager.watch('user.preferences.theme', (newTheme) => {
  console.log(`Theme changed to: ${newTheme}`);
});

// Validate configuration
const validation = configManager.validate();
if (!validation.valid) {
  console.error('Configuration errors:', validation.errors);
}

// Export/Import
const yamlConfig = configManager.export('yaml');
await configManager.import(yamlConfig, 'yaml');
```

## V. Security Considerations

```typescript
interface ConfigSecurity {
  signing: SigningConfig;
  encryption: EncryptionConfig;
  access: AccessConfig;
  audit: AuditConfig;
}

interface SigningConfig {
  enabled: boolean;
  algorithm: "Ed25519" | "ECDSA";
  publicKey: string;
  privateKey?: string;
  trustedKeys: string[];
}

interface EncryptionConfig {
  enabled: boolean;
  algorithm: "AES-256-GCM" | "ChaCha20-Poly1305";
  keyDerivation: "PBKDF2" | "Argon2id";
  iterations: number;
}

interface AccessConfig {
  requireAuth: boolean;
  adminOnly: string[];
  readOnly: string[];
  allowedUsers: string[];
}

interface AuditConfig {
  enabled: boolean;
  logChanges: boolean;
  logAccess: boolean;
  retention: number;
}

class ConfigSecurity {
  async signConfig(config: any, privateKey: string): Promise<SignedConfig> {
    const payload = JSON.stringify(config);
    const signature = await this.sign(payload, privateKey);
    
    return {
      config,
      signature,
      timestamp: Date.now(),
      version: "1.0"
    };
  }
  
  async verifyConfig(signedConfig: SignedConfig, publicKey: string): Promise<boolean> {
    const payload = JSON.stringify(signedConfig.config);
    return await this.verify(payload, signedConfig.signature, publicKey);
  }
  
  async encryptSensitiveValues(config: any, key: string): Promise<any> {
    const sensitiveKeys = ['password', 'apiKey', 'secret', 'token'];
    
    return this.traverseAndEncrypt(config, (key, value) => {
      if (typeof value === 'string' && sensitiveKeys.some(sk => key.toLowerCase().includes(sk))) {
        return this.encrypt(value, key);
      }
      return value;
    });
  }
  
  async decryptSensitiveValues(config: any, key: string): Promise<any> {
    return this.traverseAndDecrypt(config, (key, value) => {
      if (typeof value === 'string' && value.startsWith('encrypted:')) {
        return this.decrypt(value.substring(10), key);
      }
      return value;
    });
  }
  
  detectTamper(configPath: string): Promise<TamperResult> {
    // Implementation for tamper detection
    return this.checkFileIntegrity(configPath);
  }
  
  auditConfigChange(change: ConfigChange): void {
    const auditEntry = {
      timestamp: new Date().toISOString(),
      user: change.user,
      path: change.path,
      oldValue: this.sanitizeForAudit(change.oldValue),
      newValue: this.sanitizeForAudit(change.newValue),
      source: change.source
    };
    
    this.writeAuditLog(auditEntry);
  }
}
```

## VI. Centralized Config Management (Enterprise / Multi-Node)

```typescript
interface CentralizedConfigManager {
  syncFromRemote(): Promise<ConfigDiff[]>;
  pushToRemote(changes: ConfigChange[]): Promise<void>;
  subscribeToUpdates(callback: (updates: ConfigUpdate[]) => void): () => void;
  enforcePolicy(policy: ConfigPolicy): Promise<void>;
}

class EnterpriseConfigManager implements CentralizedConfigManager {
  private controlPlaneClient: ControlPlaneClient;
  
  constructor(controlPlaneUrl: string, credentials: any) {
    this.controlPlaneClient = new ControlPlaneClient(controlPlaneUrl, credentials);
  }
  
  async syncFromRemote(): Promise<ConfigDiff[]> {
    const remoteConfig = await this.controlPlaneClient.getConfig();
    const localConfig = await this.localConfigManager.export('json');
    
    return this.calculateDiff(JSON.parse(localConfig), remoteConfig);
  }
  
  async pushToRemote(changes: ConfigChange[]): Promise<void> {
    const signedChanges = await Promise.all(
      changes.map(change => this.signChange(change))
    );
    
    await this.controlPlaneClient.updateConfig(signedChanges);
  }
  
  subscribeToUpdates(callback: (updates: ConfigUpdate[]) => void): () => void {
    return this.controlPlaneClient.subscribe('config:updates', callback);
  }
  
  async enforcePolicy(policy: ConfigPolicy): Promise<void> {
    const violations = await this.checkPolicyViolations(policy);
    
    if (violations.length > 0) {
      await this.applyPolicyCorrections(violations);
    }
  }
  
  private async checkPolicyViolations(policy: ConfigPolicy): Promise<PolicyViolation[]> {
    const violations: PolicyViolation[] = [];
    const currentConfig = this.localConfigManager.config;
    
    for (const rule of policy.rules) {
      const value = this.getNestedValue(currentConfig, rule.path);
      
      if (!this.evaluateRule(rule, value)) {
        violations.push({
          rule,
          currentValue: value,
          expectedValue: rule.expectedValue,
          severity: rule.severity
        });
      }
    }
    
    return violations;
  }
}
```

## VII. Related Documentation

- **Configuration Layers**: See `07_configuration-layers-and-control.md`
- **Installer System**: See `06_installer-and-initialization.md`
- **Security Framework**: See `03_security-architecture-and-trust.md`
- **Service Management**: See `15_service-manager-stack.md`
