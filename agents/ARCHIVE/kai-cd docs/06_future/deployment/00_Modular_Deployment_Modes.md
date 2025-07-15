---
version: "1.0.0"
last_updated: "2025-01-27"
status: "draft" 
type: "specification"
category: "deployment"
tags: ["deployment", "architecture", "scalability", "orchestration", "multi-platform"]
related_docs:
  - "current/deployment/01_deployment-architecture.md"
  - "future/architecture/02_kos-system-blueprint.md"
  - "future/services/04_system-services-stack.md"
complexity: "high"
implementation_status: "planned"
code_references:
  - "src/config/"
  - "public/manifest.json"
  - "vite.config.ts"
decision_scope: "system-wide"
external_references:
  - "https://kubernetes.io/docs/concepts/"
  - "https://docs.docker.com/compose/"
  - "https://developer.chrome.com/docs/extensions/"
changelog:
  - "2025-01-27: Initial migration from brainstorm file 170"
---

# Modular Deployment Modes for kAI/kOS

**Agent Context**: This document defines all supported deployment environments for the kAI (Kind AI) and kOS (Kind Operating System) ecosystem. Agents should understand this as the comprehensive deployment strategy that enables seamless scaling from personal devices to enterprise clusters, with optimized configurations for performance, security, and device constraints across all platforms.

## Deployment Architecture Overview

The kAI/kOS system supports five primary deployment modes, each optimized for specific use cases and infrastructure requirements:

```typescript
interface DeploymentMode {
  name: string;
  description: string;
  targetEnvironment: string;
  scalabilityLevel: 'single' | 'local' | 'distributed' | 'cloud';
  securityModel: 'local' | 'federated' | 'enterprise';
  resourceRequirements: ResourceRequirements;
  supportedFeatures: string[];
  migrationPaths: string[];
}

interface ResourceRequirements {
  minCPU: string;
  minRAM: string;
  minStorage: string;
  networkBandwidth: string;
  gpuRequired: boolean;
}

const deploymentModes: DeploymentMode[] = [
  {
    name: 'standalone',
    description: 'Full system on one local device',
    targetEnvironment: 'Personal usage, developer workstation',
    scalabilityLevel: 'single',
    securityModel: 'local',
    resourceRequirements: {
      minCPU: '4 cores',
      minRAM: '8GB',
      minStorage: '50GB',
      networkBandwidth: '10Mbps',
      gpuRequired: false
    },
    supportedFeatures: ['ollama', 'comfyui', 'chroma', 'local_vault'],
    migrationPaths: ['server', 'browser']
  },
  {
    name: 'browser',
    description: 'Browser extension + IndexedDB backend',
    targetEnvironment: 'End-user assistant, PWA mode',
    scalabilityLevel: 'single',
    securityModel: 'local',
    resourceRequirements: {
      minCPU: '2 cores',
      minRAM: '4GB',
      minStorage: '2GB',
      networkBandwidth: '5Mbps',
      gpuRequired: false
    },
    supportedFeatures: ['indexeddb', 'chrome_storage', 'webrtc'],
    migrationPaths: ['standalone']
  },
  {
    name: 'embedded',
    description: 'On-device (IoT, wearable, robot)',
    targetEnvironment: 'kOS runtime on custom hardware',
    scalabilityLevel: 'single',
    securityModel: 'local',
    resourceRequirements: {
      minCPU: '1 core ARM',
      minRAM: '1GB',
      minStorage: '8GB',
      networkBandwidth: '1Mbps',
      gpuRequired: false
    },
    supportedFeatures: ['mqtt', 'klp', 'voice_ui', 'hardware_keys'],
    migrationPaths: ['server']
  },
  {
    name: 'server',
    description: 'Backend server + remote clients',
    targetEnvironment: 'Team or home network environments',
    scalabilityLevel: 'local',
    securityModel: 'federated',
    resourceRequirements: {
      minCPU: '8 cores',
      minRAM: '32GB',
      minStorage: '500GB',
      networkBandwidth: '100Mbps',
      gpuRequired: true
    },
    supportedFeatures: ['postgresql', 'redis', 'oauth2', 'gpu_acceleration'],
    migrationPaths: ['cluster', 'standalone']
  },
  {
    name: 'cluster',
    description: 'Distributed multi-agent with autoscaling',
    targetEnvironment: 'Org-wide deployments, research labs',
    scalabilityLevel: 'distributed',
    securityModel: 'enterprise',
    resourceRequirements: {
      minCPU: '32 cores distributed',
      minRAM: '128GB distributed',
      minStorage: '2TB distributed',
      networkBandwidth: '1Gbps',
      gpuRequired: true
    },
    supportedFeatures: ['kubernetes', 'nats', 'envoy', 'vault_provider'],
    migrationPaths: ['server']
  }
];
```

## Standalone Mode Implementation

```typescript
interface StandaloneConfig {
  storage: {
    db: 'sqlite' | 'leveldb';
    files: string;
    maxSize: number;
  };
  auth: {
    mode: 'none' | 'local';
    sessionTimeout: number;
  };
  services: {
    [serviceName: string]: boolean | ServiceConfig;
  };
  features: {
    auto_update: boolean;
    telemetry: boolean;
    backup: boolean;
  };
}

class StandaloneDeployment {
  private config: StandaloneConfig;
  private services: Map<string, any> = new Map();

  constructor(config: StandaloneConfig) {
    this.config = config;
  }

  async initialize(): Promise<void> {
    // Initialize local database
    await this.initializeDatabase();
    
    // Setup local services
    await this.setupServices();
    
    // Configure security
    await this.setupLocalSecurity();
    
    // Start monitoring
    this.startHealthMonitoring();
  }

  private async initializeDatabase(): Promise<void> {
    if (this.config.storage.db === 'sqlite') {
      // Initialize SQLite database
      const dbPath = `${this.config.storage.files}/kai.db`;
      // Implementation would use better-sqlite3 or similar
      console.log(`Initializing SQLite database at ${dbPath}`);
    }
  }

  private async setupServices(): Promise<void> {
    for (const [serviceName, serviceConfig] of Object.entries(this.config.services)) {
      if (serviceConfig === true || (typeof serviceConfig === 'object' && serviceConfig.enabled)) {
        await this.startService(serviceName, serviceConfig);
      }
    }
  }

  private async startService(name: string, config: any): Promise<void> {
    switch (name) {
      case 'ollama':
        await this.startOllamaService(config);
        break;
      case 'comfyui':
        await this.startComfyUIService(config);
        break;
      case 'chroma':
        await this.startChromaService(config);
        break;
      default:
        console.warn(`Unknown service: ${name}`);
    }
  }

  private async startOllamaService(config: any): Promise<void> {
    const ollamaConfig = {
      host: '127.0.0.1',
      port: 11434,
      models: config.models || ['llama2'],
      gpu: config.gpu || false
    };
    
    // Implementation would start Ollama process
    this.services.set('ollama', ollamaConfig);
    console.log('Started Ollama service');
  }

  private async startComfyUIService(config: any): Promise<void> {
    const comfyConfig = {
      host: '127.0.0.1',
      port: 8188,
      models_path: `${this.config.storage.files}/comfyui/models`,
      output_path: `${this.config.storage.files}/comfyui/output`
    };
    
    this.services.set('comfyui', comfyConfig);
    console.log('Started ComfyUI service');
  }

  private async startChromaService(config: any): Promise<void> {
    const chromaConfig = {
      host: '127.0.0.1',
      port: 8000,
      persist_directory: `${this.config.storage.files}/chroma`
    };
    
    this.services.set('chroma', chromaConfig);
    console.log('Started Chroma service');
  }

  private async setupLocalSecurity(): Promise<void> {
    // Setup local vault for credentials
    const vaultPath = `${this.config.storage.files}/vault`;
    // Implementation would initialize secure storage
    console.log(`Initialized local vault at ${vaultPath}`);
  }

  private startHealthMonitoring(): void {
    setInterval(async () => {
      for (const [serviceName, serviceConfig] of this.services.entries()) {
        const isHealthy = await this.checkServiceHealth(serviceName, serviceConfig);
        if (!isHealthy) {
          console.warn(`Service ${serviceName} is unhealthy`);
          await this.restartService(serviceName);
        }
      }
    }, 30000); // Check every 30 seconds
  }

  private async checkServiceHealth(name: string, config: any): Promise<boolean> {
    try {
      const response = await fetch(`http://${config.host}:${config.port}/health`);
      return response.ok;
    } catch {
      return false;
    }
  }

  private async restartService(name: string): Promise<void> {
    console.log(`Restarting service: ${name}`);
    // Implementation would restart the service
  }
}
```

## Browser Mode Implementation

```typescript
interface BrowserConfig {
  mode: 'browser';
  data_store: 'indexeddb' | 'chrome_storage';
  sync_with_kOS: boolean;
  local_services: string[];
  telemetry: boolean;
  max_storage: number;
}

class BrowserDeployment {
  private config: BrowserConfig;
  private db: IDBDatabase | null = null;
  private storageQuota: number = 0;

  constructor(config: BrowserConfig) {
    this.config = config;
  }

  async initialize(): Promise<void> {
    // Request storage quota
    await this.requestStorageQuota();
    
    // Initialize IndexedDB
    await this.initializeIndexedDB();
    
    // Setup message passing
    this.setupMessagePassing();
    
    // Initialize local services
    await this.initializeLocalServices();
  }

  private async requestStorageQuota(): Promise<void> {
    if ('storage' in navigator && 'estimate' in navigator.storage) {
      const estimate = await navigator.storage.estimate();
      this.storageQuota = estimate.quota || 0;
      console.log(`Storage quota: ${this.storageQuota / 1024 / 1024}MB`);
    }
  }

  private async initializeIndexedDB(): Promise<void> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open('KaiDB', 1);
      
      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        resolve();
      };
      
      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;
        
        // Create object stores
        if (!db.objectStoreNames.contains('agents')) {
          const agentStore = db.createObjectStore('agents', { keyPath: 'id' });
          agentStore.createIndex('type', 'type', { unique: false });
        }
        
        if (!db.objectStoreNames.contains('sessions')) {
          const sessionStore = db.createObjectStore('sessions', { keyPath: 'sessionId' });
          sessionStore.createIndex('agentId', 'agentId', { unique: false });
        }
        
        if (!db.objectStoreNames.contains('messages')) {
          const messageStore = db.createObjectStore('messages', { keyPath: 'id' });
          messageStore.createIndex('sessionId', 'sessionId', { unique: false });
        }
      };
    });
  }

  private setupMessagePassing(): void {
    // Setup communication between popup, content script, and background
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
      this.handleMessage(message, sender).then(sendResponse);
      return true; // Async response
    });
  }

  private async handleMessage(message: any, sender: chrome.runtime.MessageSender): Promise<any> {
    switch (message.type) {
      case 'GET_AGENTS':
        return await this.getAgents();
      case 'CREATE_SESSION':
        return await this.createSession(message.agentId);
      case 'SEND_MESSAGE':
        return await this.sendMessage(message.sessionId, message.content);
      default:
        throw new Error(`Unknown message type: ${message.type}`);
    }
  }

  private async getAgents(): Promise<any[]> {
    if (!this.db) throw new Error('Database not initialized');
    
    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['agents'], 'readonly');
      const store = transaction.objectStore('agents');
      const request = store.getAll();
      
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  private async createSession(agentId: string): Promise<string> {
    const sessionId = crypto.randomUUID();
    const session = {
      sessionId,
      agentId,
      createdAt: new Date().toISOString(),
      lastUpdated: new Date().toISOString(),
      messages: []
    };

    if (!this.db) throw new Error('Database not initialized');
    
    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['sessions'], 'readwrite');
      const store = transaction.objectStore('sessions');
      const request = store.add(session);
      
      request.onsuccess = () => resolve(sessionId);
      request.onerror = () => reject(request.error);
    });
  }

  private async sendMessage(sessionId: string, content: string): Promise<void> {
    const message = {
      id: crypto.randomUUID(),
      sessionId,
      content,
      timestamp: new Date().toISOString(),
      role: 'user'
    };

    if (!this.db) throw new Error('Database not initialized');
    
    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['messages'], 'readwrite');
      const store = transaction.objectStore('messages');
      const request = store.add(message);
      
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  private async initializeLocalServices(): Promise<void> {
    for (const service of this.config.local_services) {
      switch (service) {
        case 'open-webui':
          await this.connectToOpenWebUI();
          break;
        case 'ollama':
          await this.connectToOllama();
          break;
      }
    }
  }

  private async connectToOpenWebUI(): Promise<void> {
    // Connect to local Open WebUI instance
    const endpoint = 'http://localhost:3000';
    try {
      const response = await fetch(`${endpoint}/api/health`);
      if (response.ok) {
        console.log('Connected to Open WebUI');
      }
    } catch (error) {
      console.warn('Failed to connect to Open WebUI:', error);
    }
  }

  private async connectToOllama(): Promise<void> {
    // Connect to local Ollama instance
    const endpoint = 'http://localhost:11434';
    try {
      const response = await fetch(`${endpoint}/api/tags`);
      if (response.ok) {
        console.log('Connected to Ollama');
      }
    } catch (error) {
      console.warn('Failed to connect to Ollama:', error);
    }
  }
}
```

## Server Mode Implementation

```typescript
interface ServerConfig {
  db_url: string;
  celery_broker: string;
  log_retention_days: number;
  auth_provider: 'oidc' | 'oauth2' | 'local';
  vector_store: 'qdrant' | 'chroma' | 'pinecone';
  gpu_nodes: string[];
  backup_schedule: string;
}

class ServerDeployment {
  private config: ServerConfig;
  private services: Map<string, any> = new Map();

  constructor(config: ServerConfig) {
    this.config = config;
  }

  async initialize(): Promise<void> {
    // Initialize database connections
    await this.initializeDatabase();
    
    // Setup authentication
    await this.setupAuthentication();
    
    // Initialize services
    await this.initializeServices();
    
    // Setup monitoring
    await this.setupMonitoring();
    
    // Configure load balancing
    await this.setupLoadBalancing();
  }

  private async initializeDatabase(): Promise<void> {
    // Initialize PostgreSQL connection
    const dbConfig = {
      connectionString: this.config.db_url,
      max: 20,
      idleTimeoutMillis: 30000,
      connectionTimeoutMillis: 2000,
    };
    
    // Implementation would use pg or similar
    console.log('Initialized PostgreSQL connection');
  }

  private async setupAuthentication(): Promise<void> {
    switch (this.config.auth_provider) {
      case 'oidc':
        await this.setupOIDC();
        break;
      case 'oauth2':
        await this.setupOAuth2();
        break;
      case 'local':
        await this.setupLocalAuth();
        break;
    }
  }

  private async setupOIDC(): Promise<void> {
    const oidcConfig = {
      issuer: process.env.OIDC_ISSUER,
      clientId: process.env.OIDC_CLIENT_ID,
      clientSecret: process.env.OIDC_CLIENT_SECRET,
      redirectUri: process.env.OIDC_REDIRECT_URI
    };
    
    // Implementation would configure OIDC provider
    console.log('Configured OIDC authentication');
  }

  private async setupOAuth2(): Promise<void> {
    // Configure OAuth2 provider
    console.log('Configured OAuth2 authentication');
  }

  private async setupLocalAuth(): Promise<void> {
    // Configure local authentication with JWT
    console.log('Configured local authentication');
  }

  private async initializeServices(): Promise<void> {
    // Initialize Celery for task queue
    await this.initializeCelery();
    
    // Initialize vector store
    await this.initializeVectorStore();
    
    // Initialize GPU nodes
    await this.initializeGPUNodes();
  }

  private async initializeCelery(): Promise<void> {
    const celeryConfig = {
      broker: this.config.celery_broker,
      backend: this.config.celery_broker,
      include: ['tasks.agent_tasks', 'tasks.ml_tasks']
    };
    
    // Implementation would configure Celery
    console.log('Initialized Celery task queue');
  }

  private async initializeVectorStore(): Promise<void> {
    switch (this.config.vector_store) {
      case 'qdrant':
        await this.initializeQdrant();
        break;
      case 'chroma':
        await this.initializeChroma();
        break;
      case 'pinecone':
        await this.initializePinecone();
        break;
    }
  }

  private async initializeQdrant(): Promise<void> {
    const qdrantConfig = {
      host: process.env.QDRANT_HOST || 'localhost',
      port: parseInt(process.env.QDRANT_PORT || '6333'),
      apiKey: process.env.QDRANT_API_KEY,
      https: process.env.QDRANT_HTTPS === 'true'
    };
    
    // Implementation would initialize Qdrant client
    console.log('Initialized Qdrant vector store');
  }

  private async initializeChroma(): Promise<void> {
    // Initialize Chroma vector store
    console.log('Initialized Chroma vector store');
  }

  private async initializePinecone(): Promise<void> {
    // Initialize Pinecone vector store
    console.log('Initialized Pinecone vector store');
  }

  private async initializeGPUNodes(): Promise<void> {
    for (const nodeUrl of this.config.gpu_nodes) {
      try {
        const response = await fetch(`${nodeUrl}/health`);
        if (response.ok) {
          console.log(`GPU node ${nodeUrl} is healthy`);
        }
      } catch (error) {
        console.warn(`GPU node ${nodeUrl} is unreachable:`, error);
      }
    }
  }

  private async setupMonitoring(): Promise<void> {
    // Setup Prometheus metrics
    // Setup Grafana dashboards  
    // Configure alerting
    console.log('Configured monitoring and alerting');
  }

  private async setupLoadBalancing(): Promise<void> {
    // Configure load balancer for multiple instances
    console.log('Configured load balancing');
  }
}
```

## Migration System

```typescript
interface MigrationConfig {
  fromMode: string;
  toMode: string;
  dataPath: string;
  preserveData: boolean;
  migrationSteps: MigrationStep[];
}

interface MigrationStep {
  step: string;
  description: string;
  required: boolean;
  estimatedTime: number;
  dependencies: string[];
}

class DeploymentMigrationManager {
  private migrations: Map<string, MigrationConfig> = new Map();

  constructor() {
    this.initializeMigrations();
  }

  private initializeMigrations(): void {
    // Standalone to Server migration
    this.migrations.set('standalone->server', {
      fromMode: 'standalone',
      toMode: 'server',
      dataPath: '',
      preserveData: true,
      migrationSteps: [
        {
          step: 'export_data',
          description: 'Export SQLite data to PostgreSQL format',
          required: true,
          estimatedTime: 600, // 10 minutes
          dependencies: []
        },
        {
          step: 'setup_server',
          description: 'Initialize server infrastructure',
          required: true,
          estimatedTime: 1800, // 30 minutes
          dependencies: ['export_data']
        },
        {
          step: 'migrate_services',
          description: 'Migrate local services to server',
          required: true,
          estimatedTime: 900, // 15 minutes
          dependencies: ['setup_server']
        },
        {
          step: 'test_connectivity',
          description: 'Test client-server connectivity',
          required: true,
          estimatedTime: 300, // 5 minutes
          dependencies: ['migrate_services']
        }
      ]
    });

    // Browser to Standalone migration
    this.migrations.set('browser->standalone', {
      fromMode: 'browser',
      toMode: 'standalone',
      dataPath: '',
      preserveData: true,
      migrationSteps: [
        {
          step: 'export_browser_data',
          description: 'Export IndexedDB data',
          required: true,
          estimatedTime: 300,
          dependencies: []
        },
        {
          step: 'install_standalone',
          description: 'Install standalone application',
          required: true,
          estimatedTime: 600,
          dependencies: []
        },
        {
          step: 'import_data',
          description: 'Import browser data to standalone',
          required: true,
          estimatedTime: 300,
          dependencies: ['export_browser_data', 'install_standalone']
        }
      ]
    });
  }

  async performMigration(
    fromMode: string,
    toMode: string,
    dataPath: string,
    progressCallback?: (step: string, progress: number) => void
  ): Promise<void> {
    const migrationKey = `${fromMode}->${toMode}`;
    const migration = this.migrations.get(migrationKey);
    
    if (!migration) {
      throw new Error(`Migration from ${fromMode} to ${toMode} not supported`);
    }

    migration.dataPath = dataPath;
    
    for (let i = 0; i < migration.migrationSteps.length; i++) {
      const step = migration.migrationSteps[i];
      
      if (progressCallback) {
        progressCallback(step.step, (i / migration.migrationSteps.length) * 100);
      }
      
      await this.executeStep(step, migration);
    }
    
    if (progressCallback) {
      progressCallback('complete', 100);
    }
  }

  private async executeStep(step: MigrationStep, migration: MigrationConfig): Promise<void> {
    console.log(`Executing migration step: ${step.step}`);
    
    switch (step.step) {
      case 'export_data':
        await this.exportData(migration);
        break;
      case 'setup_server':
        await this.setupServer(migration);
        break;
      case 'migrate_services':
        await this.migrateServices(migration);
        break;
      case 'test_connectivity':
        await this.testConnectivity(migration);
        break;
      case 'export_browser_data':
        await this.exportBrowserData(migration);
        break;
      case 'install_standalone':
        await this.installStandalone(migration);
        break;
      case 'import_data':
        await this.importData(migration);
        break;
      default:
        throw new Error(`Unknown migration step: ${step.step}`);
    }
    
    // Simulate step execution time
    await new Promise(resolve => setTimeout(resolve, step.estimatedTime));
  }

  private async exportData(migration: MigrationConfig): Promise<void> {
    // Implementation would export data from source format
    console.log(`Exporting data from ${migration.fromMode}`);
  }

  private async setupServer(migration: MigrationConfig): Promise<void> {
    // Implementation would setup server infrastructure
    console.log('Setting up server infrastructure');
  }

  private async migrateServices(migration: MigrationConfig): Promise<void> {
    // Implementation would migrate services
    console.log('Migrating services');
  }

  private async testConnectivity(migration: MigrationConfig): Promise<void> {
    // Implementation would test connectivity
    console.log('Testing connectivity');
  }

  private async exportBrowserData(migration: MigrationConfig): Promise<void> {
    // Implementation would export browser data
    console.log('Exporting browser data');
  }

  private async installStandalone(migration: MigrationConfig): Promise<void> {
    // Implementation would install standalone app
    console.log('Installing standalone application');
  }

  private async importData(migration: MigrationConfig): Promise<void> {
    // Implementation would import data
    console.log('Importing data');
  }
}
```

This comprehensive deployment system provides flexible, scalable deployment options that can adapt to different use cases and infrastructure requirements while maintaining consistent functionality and migration capabilities across all modes. 