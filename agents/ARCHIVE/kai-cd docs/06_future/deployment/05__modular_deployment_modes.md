---
title: "Modular Deployment Modes"
description: "Comprehensive deployment modes for kAI/kOS ecosystem with detailed configuration schemas, runtime topologies, and platform-specific considerations"
type: "deployment"
status: "future"
priority: "high"
last_updated: "2024-01-20"
related_docs: ["deployment-profiles-and-strategies.md", "installer-and-initialization.md"]
implementation_status: "planned"
---

# Modular Deployment Modes for kAI/kOS

## Agent Context
Complete specification for all supported deployment modes in kAI (Kind AI) and kOS (Kind Operating System) ecosystem. Agents implementing deployment orchestration, configuration management, or platform integration must reference this for comprehensive deployment mode compliance.

## Overview

Defines standardized deployment environments optimized for scalability, performance, and device constraints. Enables seamless migration between modes (local to server to cluster) while ensuring security and performance isolation across services. Supports embedded edge devices, browsers, desktop, server, and cloud clusters.

## Deployment Modes Overview

| Mode         | Description                                         | Primary Use Case                      | Complexity |
| ------------ | --------------------------------------------------- | ------------------------------------- | ---------- |
| `standalone` | Full system on one local device                     | Personal usage, developer workstation | Low        |
| `browser`    | Browser extension + IndexedDB backend               | End-user assistant, PWA mode          | Low        |
| `embedded`   | On-device (e.g., wearable, IoT, robot)              | kOS runtime on custom hardware        | Medium     |
| `server`     | Backend server + remote clients                     | Team or home network environments     | Medium     |
| `cluster`    | Distributed multi-agent with autoscaling + API mesh | Org-wide deployments, research labs   | High       |

## Mode Specifications

### Standalone Mode (Desktop/Local)

```typescript
interface StandaloneConfig {
  storage: {
    db: 'sqlite' | 'duckdb';
    files: string;
    cache: 'memory' | 'redis';
  };
  auth: {
    mode: 'none' | 'local_vault';
    vaultPath?: string;
  };
  services: {
    ollama: boolean;
    comfyui: boolean;
    chroma: boolean;
    a1111?: boolean;
  };
  features: {
    auto_update: boolean;
    telemetry: boolean;
    federation: boolean;
  };
  networking: {
    port: number;
    bindAddress: string;
    cors: CorsConfig;
  };
}

class StandaloneDeployment {
  private config: StandaloneConfig;
  private services = new Map<string, ServiceInstance>();
  
  async initialize(config: StandaloneConfig): Promise<void> {
    this.config = config;
    
    // Initialize storage
    await this.initializeStorage();
    
    // Start core services
    await this.startCoreServices();
    
    // Initialize AI services
    await this.initializeAIServices();
    
    // Setup UI
    await this.initializeUI();
  }
  
  private async initializeStorage(): Promise<void> {
    if (this.config.storage.db === 'sqlite') {
      const db = new SQLiteDatabase(path.join(this.config.storage.files, 'kai.db'));
      await db.initialize();
      this.services.set('database', db);
    }
    
    if (this.config.storage.cache === 'redis') {
      const redis = new RedisCache({ host: 'localhost', port: 6379 });
      await redis.connect();
      this.services.set('cache', redis);
    }
  }
  
  private async startCoreServices(): Promise<void> {
    // Start API server
    const apiServer = new FastAPIServer({
      port: this.config.networking.port,
      cors: this.config.networking.cors
    });
    await apiServer.start();
    this.services.set('api', apiServer);
    
    // Start background task queue
    const taskQueue = new LocalTaskQueue();
    await taskQueue.start();
    this.services.set('tasks', taskQueue);
  }
  
  private async initializeAIServices(): Promise<void> {
    if (this.config.services.ollama) {
      const ollama = new OllamaService({ url: 'http://localhost:11434' });
      await ollama.healthCheck();
      this.services.set('ollama', ollama);
    }
    
    if (this.config.services.comfyui) {
      const comfyui = new ComfyUIService({ url: 'http://localhost:8188' });
      await comfyui.healthCheck();
      this.services.set('comfyui', comfyui);
    }
  }
}
```

### Browser Mode (Extension)

```typescript
interface BrowserConfig {
  mode: 'browser';
  data_store: 'indexeddb' | 'chrome_storage';
  sync_with_kOS: boolean;
  local_services: string[];
  telemetry: boolean;
  ui_mode: 'popup' | 'sidepanel' | 'tab' | 'all';
  permissions: BrowserPermission[];
}

interface BrowserPermission {
  permission: string;
  required: boolean;
  reason: string;
}

class BrowserDeployment {
  private config: BrowserConfig;
  private storage: BrowserStorage;
  private serviceConnector: ServiceConnector;
  
  async initialize(config: BrowserConfig): Promise<void> {
    this.config = config;
    
    // Initialize storage
    this.storage = config.data_store === 'indexeddb' 
      ? new IndexedDBStorage() 
      : new ChromeStorageAdapter();
    await this.storage.initialize();
    
    // Setup service connections
    this.serviceConnector = new ServiceConnector();
    await this.connectToLocalServices();
    
    // Initialize UI contexts
    await this.initializeUIContexts();
  }
  
  private async connectToLocalServices(): Promise<void> {
    for (const serviceName of this.config.local_services) {
      try {
        const service = await this.serviceConnector.connect(serviceName);
        await service.healthCheck();
        console.log(`Connected to ${serviceName}`);
      } catch (error) {
        console.warn(`Failed to connect to ${serviceName}:`, error);
      }
    }
  }
  
  private async initializeUIContexts(): Promise<void> {
    const contexts = this.config.ui_mode === 'all' 
      ? ['popup', 'sidepanel', 'tab'] 
      : [this.config.ui_mode];
    
    for (const context of contexts) {
      await this.initializeContext(context);
    }
  }
  
  async handleCrossContextSync(event: SyncEvent): Promise<void> {
    // Sync state across popup, sidepanel, and tab
    const broadcastChannel = new BroadcastChannel('kai-sync');
    broadcastChannel.postMessage({
      type: 'state_update',
      context: event.sourceContext,
      data: event.data,
      timestamp: Date.now()
    });
  }
}
```

### Embedded Mode (IoT/Mobile/Wearable)

```typescript
interface EmbeddedConfig {
  klp_enabled: boolean;
  mqtt_host: string;
  device_id: string;
  heartbeat_interval: number; // seconds
  voice_ui: boolean;
  display_type: 'none' | 'led' | 'oled' | 'eink';
  sensors: SensorConfig[];
  actuators: ActuatorConfig[];
  power_management: PowerConfig;
}

interface SensorConfig {
  type: 'temperature' | 'humidity' | 'motion' | 'camera' | 'microphone';
  pin?: number;
  i2c_address?: number;
  sampling_rate: number;
  enabled: boolean;
}

class EmbeddedDeployment {
  private config: EmbeddedConfig;
  private mqttClient: MQTTClient;
  private sensorManager: SensorManager;
  private klpNode: KLPNode;
  
  async initialize(config: EmbeddedConfig): Promise<void> {
    this.config = config;
    
    // Initialize hardware interfaces
    await this.initializeHardware();
    
    // Connect to MQTT broker
    await this.connectMQTT();
    
    // Initialize KLP if enabled
    if (config.klp_enabled) {
      await this.initializeKLP();
    }
    
    // Start sensor monitoring
    await this.startSensorMonitoring();
    
    // Initialize power management
    await this.initializePowerManagement();
  }
  
  private async initializeHardware(): Promise<void> {
    this.sensorManager = new SensorManager();
    
    for (const sensorConfig of this.config.sensors) {
      const sensor = await this.sensorManager.initializeSensor(sensorConfig);
      if (sensor) {
        console.log(`Initialized ${sensorConfig.type} sensor`);
      }
    }
  }
  
  private async connectMQTT(): Promise<void> {
    this.mqttClient = new MQTTClient({
      host: this.config.mqtt_host,
      clientId: this.config.device_id,
      keepalive: this.config.heartbeat_interval
    });
    
    await this.mqttClient.connect();
    
    // Subscribe to device-specific topics
    await this.mqttClient.subscribe(`kai/${this.config.device_id}/commands`);
    await this.mqttClient.subscribe(`kai/${this.config.device_id}/config`);
  }
  
  private async initializeKLP(): Promise<void> {
    this.klpNode = new KLPNode({
      nodeId: this.config.device_id,
      nodeType: 'embedded',
      capabilities: await this.detectCapabilities()
    });
    
    await this.klpNode.join();
  }
}
```

### Server Mode

```typescript
interface ServerConfig {
  db_url: string;
  celery_broker: string;
  log_retention_days: number;
  auth_provider: 'oidc' | 'oauth2' | 'local';
  vector_store: 'qdrant' | 'chroma' | 'pinecone';
  scaling: ScalingConfig;
  monitoring: MonitoringConfig;
}

interface ScalingConfig {
  min_workers: number;
  max_workers: number;
  target_cpu_utilization: number;
  target_memory_utilization: number;
  scale_up_threshold: number;
  scale_down_threshold: number;
}

class ServerDeployment {
  private config: ServerConfig;
  private database: Database;
  private taskQueue: CeleryQueue;
  private apiServer: FastAPIServer;
  private workerManager: WorkerManager;
  
  async initialize(config: ServerConfig): Promise<void> {
    this.config = config;
    
    // Initialize database
    await this.initializeDatabase();
    
    // Setup task queue
    await this.initializeTaskQueue();
    
    // Start API server
    await this.startAPIServer();
    
    // Initialize worker management
    await this.initializeWorkerManagement();
    
    // Setup monitoring
    await this.initializeMonitoring();
  }
  
  private async initializeDatabase(): Promise<void> {
    this.database = new PostgreSQLDatabase(this.config.db_url);
    await this.database.connect();
    await this.database.runMigrations();
  }
  
  private async initializeTaskQueue(): Promise<void> {
    this.taskQueue = new CeleryQueue({
      broker: this.config.celery_broker,
      backend: this.config.db_url
    });
    await this.taskQueue.initialize();
  }
  
  private async initializeWorkerManagement(): Promise<void> {
    this.workerManager = new WorkerManager({
      minWorkers: this.config.scaling.min_workers,
      maxWorkers: this.config.scaling.max_workers,
      scalingMetrics: {
        cpuThreshold: this.config.scaling.target_cpu_utilization,
        memoryThreshold: this.config.scaling.target_memory_utilization
      }
    });
    
    await this.workerManager.start();
  }
  
  async handleScalingEvent(metrics: SystemMetrics): Promise<void> {
    const decision = await this.workerManager.evaluateScaling(metrics);
    
    if (decision.action === 'scale_up') {
      await this.workerManager.scaleUp(decision.targetWorkers);
    } else if (decision.action === 'scale_down') {
      await this.workerManager.scaleDown(decision.targetWorkers);
    }
  }
}
```

### Cluster Mode (Distributed Multi-Agent)

```typescript
interface ClusterConfig {
  orchestrator: 'kubernetes' | 'docker_swarm' | 'nomad';
  control_plane: {
    agents: number;
    trust_zones: string[];
    high_availability: boolean;
  };
  services: {
    nats: boolean;
    envoy: boolean;
    vector_db: string;
    monitoring_stack: string[];
  };
  secrets: {
    vault_provider: 'aws_kms' | 'hashicorp_vault' | 'kubernetes_secrets';
    rotate_interval: string;
  };
  networking: {
    service_mesh: boolean;
    ingress_controller: string;
    load_balancer: string;
  };
}

class ClusterDeployment {
  private config: ClusterConfig;
  private orchestrator: Orchestrator;
  private serviceMesh: ServiceMesh;
  private secretsManager: SecretsManager;
  
  async initialize(config: ClusterConfig): Promise<void> {
    this.config = config;
    
    // Initialize orchestrator
    await this.initializeOrchestrator();
    
    // Setup service mesh
    if (config.networking.service_mesh) {
      await this.initializeServiceMesh();
    }
    
    // Initialize secrets management
    await this.initializeSecretsManagement();
    
    // Deploy core services
    await this.deployCoreServices();
    
    // Setup monitoring and observability
    await this.initializeObservability();
  }
  
  private async initializeOrchestrator(): Promise<void> {
    switch (this.config.orchestrator) {
      case 'kubernetes':
        this.orchestrator = new KubernetesOrchestrator();
        break;
      case 'docker_swarm':
        this.orchestrator = new DockerSwarmOrchestrator();
        break;
      case 'nomad':
        this.orchestrator = new NomadOrchestrator();
        break;
    }
    
    await this.orchestrator.initialize();
  }
  
  private async deployCoreServices(): Promise<void> {
    const deployments = [
      this.deployNATS(),
      this.deployEnvoy(),
      this.deployVectorDB(),
      this.deployAgentControllers()
    ];
    
    await Promise.all(deployments);
  }
  
  private async deployAgentControllers(): Promise<void> {
    for (const trustZone of this.config.control_plane.trust_zones) {
      const controller = new AgentController({
        trustZone,
        replicas: this.config.control_plane.agents,
        highAvailability: this.config.control_plane.high_availability
      });
      
      await this.orchestrator.deploy(controller);
    }
  }
  
  async handleNodeFailure(failedNode: string): Promise<void> {
    // Implement node failure recovery
    const affectedServices = await this.orchestrator.getServicesOnNode(failedNode);
    
    for (const service of affectedServices) {
      await this.orchestrator.reschedule(service);
    }
    
    // Update service mesh configuration
    if (this.serviceMesh) {
      await this.serviceMesh.removeNode(failedNode);
    }
  }
}
```

## Migration Paths

### Migration Manager

```typescript
interface MigrationPath {
  from: DeploymentMode;
  to: DeploymentMode;
  supported: boolean;
  method: MigrationMethod;
  estimatedTime: string;
  prerequisites: string[];
  risks: string[];
}

class DeploymentMigrationManager {
  private migrationPaths: Map<string, MigrationPath> = new Map();
  
  constructor() {
    this.initializeMigrationPaths();
  }
  
  private initializeMigrationPaths(): void {
    // Standalone to Server
    this.migrationPaths.set('standalone->server', {
      from: 'standalone',
      to: 'server',
      supported: true,
      method: 'export_import_with_reattach',
      estimatedTime: '30-60 minutes',
      prerequisites: ['server_infrastructure', 'network_connectivity'],
      risks: ['data_loss', 'service_interruption']
    });
    
    // Browser to Standalone
    this.migrationPaths.set('browser->standalone', {
      from: 'browser',
      to: 'standalone',
      supported: true,
      method: 'export_import_ui',
      estimatedTime: '10-15 minutes',
      prerequisites: ['desktop_application'],
      risks: ['local_service_configuration']
    });
    
    // Server to Cluster
    this.migrationPaths.set('server->cluster', {
      from: 'server',
      to: 'cluster',
      supported: true,
      method: 'helm_charts_replica_configs',
      estimatedTime: '2-4 hours',
      prerequisites: ['kubernetes_cluster', 'helm', 'persistent_storage'],
      risks: ['complex_networking', 'distributed_state']
    });
  }
  
  async planMigration(
    from: DeploymentMode,
    to: DeploymentMode,
    currentConfig: any
  ): Promise<MigrationPlan> {
    const pathKey = `${from}->${to}`;
    const migrationPath = this.migrationPaths.get(pathKey);
    
    if (!migrationPath || !migrationPath.supported) {
      throw new Error(`Migration from ${from} to ${to} is not supported`);
    }
    
    const plan: MigrationPlan = {
      path: migrationPath,
      steps: await this.generateMigrationSteps(migrationPath, currentConfig),
      rollbackPlan: await this.generateRollbackPlan(migrationPath),
      validationChecks: this.getValidationChecks(migrationPath)
    };
    
    return plan;
  }
  
  async executeMigration(plan: MigrationPlan): Promise<MigrationResult> {
    const result: MigrationResult = {
      success: false,
      completedSteps: [],
      errors: [],
      rollbackRequired: false
    };
    
    try {
      for (const step of plan.steps) {
        await this.executeStep(step);
        result.completedSteps.push(step.name);
        
        // Validate step completion
        const validation = await this.validateStep(step);
        if (!validation.success) {
          throw new Error(`Step validation failed: ${validation.error}`);
        }
      }
      
      result.success = true;
    } catch (error) {
      result.errors.push(error.message);
      result.rollbackRequired = true;
      
      // Execute rollback
      await this.executeRollback(plan.rollbackPlan, result.completedSteps);
    }
    
    return result;
  }
}
```

## Mode-Specific Debug Tools

```typescript
interface DebugTool {
  name: string;
  mode: DeploymentMode;
  type: 'profiler' | 'logger' | 'monitor' | 'inspector';
  endpoint?: string;
  configuration: any;
}

class DebugToolManager {
  private tools = new Map<DeploymentMode, DebugTool[]>();
  
  constructor() {
    this.initializeDebugTools();
  }
  
  private initializeDebugTools(): void {
    // Standalone tools
    this.tools.set('standalone', [
      {
        name: 'devtools-agent',
        mode: 'standalone',
        type: 'inspector',
        endpoint: 'http://localhost:8080/debug',
        configuration: { realtime: true }
      },
      {
        name: 'tail-log',
        mode: 'standalone',
        type: 'logger',
        configuration: { logLevel: 'debug', follow: true }
      }
    ]);
    
    // Browser tools
    this.tools.set('browser', [
      {
        name: 'indexeddb-inspector',
        mode: 'browser',
        type: 'inspector',
        configuration: { database: 'kai-cd' }
      },
      {
        name: 'extension-console',
        mode: 'browser',
        type: 'logger',
        configuration: { context: 'all' }
      }
    ]);
    
    // Cluster tools
    this.tools.set('cluster', [
      {
        name: 'kiali',
        mode: 'cluster',
        type: 'monitor',
        endpoint: 'http://kiali.istio-system:20001',
        configuration: { namespace: 'kai-system' }
      },
      {
        name: 'jaeger',
        mode: 'cluster',
        type: 'profiler',
        endpoint: 'http://jaeger.observability:16686',
        configuration: { service: 'kai-agents' }
      }
    ]);
  }
  
  async enableDebugMode(mode: DeploymentMode): Promise<DebugSession> {
    const tools = this.tools.get(mode) || [];
    const session: DebugSession = {
      sessionId: crypto.randomUUID(),
      mode,
      enabledTools: [],
      startTime: new Date().toISOString()
    };
    
    for (const tool of tools) {
      try {
        await this.activateTool(tool);
        session.enabledTools.push(tool.name);
      } catch (error) {
        console.warn(`Failed to activate ${tool.name}:`, error);
      }
    }
    
    return session;
  }
}
```

## Configuration Management

```typescript
class ConfigurationManager {
  private configs = new Map<DeploymentMode, any>();
  private validator = new ConfigValidator();
  
  async loadConfiguration(mode: DeploymentMode, configPath?: string): Promise<any> {
    const defaultConfig = this.getDefaultConfiguration(mode);
    
    if (configPath) {
      const userConfig = await this.loadUserConfiguration(configPath);
      const mergedConfig = this.mergeConfigurations(defaultConfig, userConfig);
      
      // Validate merged configuration
      const validation = await this.validator.validate(mode, mergedConfig);
      if (!validation.valid) {
        throw new Error(`Invalid configuration: ${validation.errors.join(', ')}`);
      }
      
      return mergedConfig;
    }
    
    return defaultConfig;
  }
  
  private getDefaultConfiguration(mode: DeploymentMode): any {
    const defaults = {
      standalone: {
        storage: { db: 'sqlite', files: './data/', cache: 'memory' },
        auth: { mode: 'none' },
        services: { ollama: true, comfyui: false, chroma: true },
        features: { auto_update: false, telemetry: false },
        networking: { port: 8080, bindAddress: '127.0.0.1' }
      },
      browser: {
        mode: 'browser',
        data_store: 'indexeddb',
        sync_with_kOS: false,
        local_services: ['ollama'],
        telemetry: false,
        ui_mode: 'all'
      },
      embedded: {
        klp_enabled: true,
        mqtt_host: '10.0.0.1',
        device_id: 'kai_device_001',
        heartbeat_interval: 60,
        voice_ui: false,
        display_type: 'none'
      },
      server: {
        db_url: 'postgresql://kai:kai@localhost/kos',
        celery_broker: 'redis://localhost:6379/0',
        log_retention_days: 30,
        auth_provider: 'local',
        vector_store: 'qdrant'
      },
      cluster: {
        orchestrator: 'kubernetes',
        control_plane: { agents: 3, trust_zones: ['public', 'internal'] },
        services: { nats: true, envoy: true, vector_db: 'qdrant-cloud' },
        secrets: { vault_provider: 'kubernetes_secrets', rotate_interval: '7d' }
      }
    };
    
    return defaults[mode];
  }
}
```

## Implementation Examples

### Standalone Deployment

```typescript
// Initialize standalone deployment
const config: StandaloneConfig = {
  storage: { db: 'sqlite', files: './kai-data/', cache: 'redis' },
  auth: { mode: 'local_vault', vaultPath: './vault.db' },
  services: { ollama: true, comfyui: true, chroma: true },
  features: { auto_update: true, telemetry: false, federation: false },
  networking: { port: 8080, bindAddress: '0.0.0.0', cors: { origins: ['*'] } }
};

const deployment = new StandaloneDeployment();
await deployment.initialize(config);

console.log('Standalone deployment ready on http://localhost:8080');
```

### Migration Example

```typescript
// Migrate from standalone to server
const migrationManager = new DeploymentMigrationManager();
const plan = await migrationManager.planMigration('standalone', 'server', currentConfig);

console.log(`Migration will take approximately ${plan.path.estimatedTime}`);
console.log(`Prerequisites: ${plan.path.prerequisites.join(', ')}`);

const result = await migrationManager.executeMigration(plan);
if (result.success) {
  console.log('Migration completed successfully');
} else {
  console.error('Migration failed:', result.errors);
}
```

## Conclusion

Modular Deployment Modes provide comprehensive, flexible deployment strategies for kAI/kOS ecosystem across all target platforms and use cases. The system supports seamless transitions between deployment modes while maintaining data integrity, service continuity, and optimal performance characteristics for each environment.

The architecture enables organizations to start simple with browser or standalone deployments and scale to full cluster deployments as needs grow, with well-defined migration paths and comprehensive tooling support.

---

*This document defines complete deployment mode specifications for kOS ecosystem. All agents implementing deployment orchestration must comply with these specifications for ecosystem interoperability.*
