---
title: "Agent System Protocols and Directory Architecture"
description: "Complete breakdown of system architecture, directory structure, and configuration protocols for all agent modules in kAI and kOS ecosystems"
category: "protocols"
subcategory: "agent-systems"
context: "future_vision"
implementation_status: "planned"
decision_scope: "critical"
complexity: "very_high"
last_updated: "2025-01-27"
code_references:
  - "src/features/ai-services/"
  - "src/core/"
  - "src/store/"
related_documents:
  - "../agents/38_agent-protocols-hierarchy-complete.md"
  - "./01_kind-link-protocol-core.md"
  - "../architecture/10_kos-core-architecture-internal.md"
dependencies: ["KLP Protocol", "Agent Hierarchy", "File System Architecture", "Configuration Management"]
breaking_changes: false
agent_notes: "Complete agent system protocol specification including directory structure, configuration conventions, and file organization patterns. Use this for understanding system layout, implementing file organization, and managing agent configurations. Critical for system development and deployment."
---

# Agent System Protocols and Directory Architecture

> **Agent Context**: Comprehensive specification for agent system architecture, directory structure, and configuration protocols. Use this document for understanding system file organization, implementing agent configurations, and managing the complete kOS file system layout. Essential for system development and deployment.

## Quick Summary
Complete breakdown of system architecture, directory structure, and configuration protocols for all agent modules under the kAI (Kind AI) and kOS ecosystems, providing the foundation for agent coordination, configuration management, and system organization.

## Implementation Status
- 🔬 **Research**: Complete directory architecture design
- 📋 **Planned**: Full system file organization implementation
- 🔄 **In Progress**: Core agent configuration systems
- ⚠️ **Dependencies**: Requires KLP protocol and agent hierarchy

## Master Directory Layout Architecture

### **Complete System Structure**
```typescript
interface KAIDirectoryStructure {
  root: 'kai/';
  agents: {
    kCore: {
      controller: 'controller.py';
      config: {
        system: 'system.json';
        defaults: 'defaults.yml';
      };
      tasks: ['startup.py'];
      logs: ['controller.log'];
    };
    kPlanner: {
      planner: 'planner.py';
      prompts: 'template_directory';
      config: 'planner.json';
    };
    kExecutor: {
      executor: 'executor.py';
      plugins: 'plugin_directory';
      config: 'executor.json';
    };
    // ... all other agent types
  };
  communications: {
    klp: {
      schema: 'schema.json';
      transports: ['transport_grpc.py', 'transport_ws.py'];
      auth: ['signer.py', 'verifier.py'];
      handler: 'protocol_handler.py';
    };
    mesh: {
      local: 'local_mesh.py';
      remote: 'remote_mesh.py';
    };
  };
  configuration: {
    agents: {
      manifest: 'manifest.json';
      configurations: 'per_agent_configs';
    };
    services: 'services.yml';
    global: 'global_settings.json';
  };
}

class DirectoryManager {
  private baseDir: string;
  private structure: DirectoryStructure;
  
  constructor(basePath: string) {
    this.baseDir = basePath;
    this.structure = this.loadStructureDefinition();
  }
  
  async initializeDirectoryStructure(): Promise<void> {
    // Create base directory structure
    await this.createDirectories();
    
    // Initialize agent directories
    await this.initializeAgentDirectories();
    
    // Setup configuration directories
    await this.initializeConfigurationDirectories();
    
    // Create logging directories
    await this.initializeLoggingDirectories();
    
    // Setup security directories
    await this.initializeSecurityDirectories();
  }
  
  private async createDirectories(): Promise<void> {
    const directories = [
      'agents',
      'comms/klp',
      'comms/mesh',
      'config/agents',
      'core',
      'data/embeddings',
      'data/memory',
      'data/vault',
      'logs',
      'plugins',
      'security/keys',
      'security/audit',
      'security/policies',
      'tests/unit',
      'tests/integration',
      'tests/simulation',
      'ui/webapp/components',
      'ui/webapp/store',
      'ui/webapp/pages',
      'ui/themes'
    ];
    
    for (const dir of directories) {
      await this.ensureDirectory(path.join(this.baseDir, dir));
    }
  }
}
```

### **Agent Directory Implementation**
```typescript
interface AgentDirectoryStructure {
  [agentType: string]: {
    mainFile: string;
    configFiles: string[];
    dataDirectories: string[];
    logFiles: string[];
    dependencies: string[];
  };
}

class AgentDirectoryManager {
  private agentTypes: Map<string, AgentDirectoryDefinition>;
  
  async createAgentDirectory(agentType: string, agentId: string): Promise<string> {
    const definition = this.agentTypes.get(agentType);
    if (!definition) {
      throw new Error(`Unknown agent type: ${agentType}`);
    }
    
    const agentDir = path.join('agents', agentType, agentId);
    
    // Create agent-specific directory
    await this.ensureDirectory(agentDir);
    
    // Create subdirectories
    for (const subDir of definition.dataDirectories) {
      await this.ensureDirectory(path.join(agentDir, subDir));
    }
    
    // Initialize configuration files
    await this.initializeAgentConfig(agentDir, definition);
    
    // Setup logging
    await this.initializeAgentLogging(agentDir, agentId);
    
    return agentDir;
  }
  
  private async initializeAgentConfig(
    agentDir: string,
    definition: AgentDirectoryDefinition
  ): Promise<void> {
    for (const configFile of definition.configFiles) {
      const configPath = path.join(agentDir, 'config', configFile);
      const defaultConfig = await this.generateDefaultConfig(definition.type);
      
      await this.writeJsonFile(configPath, defaultConfig);
    }
  }
}
```

## Configuration Conventions and Standards

### **Configuration File Hierarchy**
```typescript
interface ConfigurationStandards {
  jsonFiles: {
    purpose: 'Runtime settings, identities, manifests';
    examples: ['manifest.json', 'global_settings.json', 'agent_configs.json'];
    features: ['real_time_updates', 'strict_validation', 'hot_reloading'];
  };
  yamlFiles: {
    purpose: 'User-editable service descriptions';
    examples: ['services.yml', 'defaults.yml', 'policies.yml'];
    features: ['human_readable', 'comments_supported', 'hierarchical'];
  };
  environmentFiles: {
    purpose: 'Environment-specific settings';
    examples: ['.env', '.env.production', '.env.development'];
    features: ['secret_management', 'environment_isolation'];
  };
}

interface GlobalSettings {
  debugMode: boolean;
  defaultLanguage: string;
  maxParallelTasks: number;
  enableMesh: boolean;
  logLevel: 'debug' | 'info' | 'warn' | 'error';
  securityLevel: 'low' | 'medium' | 'high' | 'strict';
  agentDefaults: {
    timeout: number;
    retries: number;
    memoryLimit: string;
  };
}

class ConfigurationManager {
  private configs: Map<string, ConfigurationFile>;
  private watchers: Map<string, ConfigWatcher>;
  private validator: ConfigValidator;
  
  async loadGlobalSettings(): Promise<GlobalSettings> {
    const configPath = 'config/global_settings.json';
    const rawConfig = await this.loadJsonFile(configPath);
    
    // Validate configuration
    const validatedConfig = await this.validator.validateGlobalSettings(rawConfig);
    
    return validatedConfig as GlobalSettings;
  }
  
  async updateGlobalSetting<K extends keyof GlobalSettings>(
    key: K,
    value: GlobalSettings[K]
  ): Promise<void> {
    const currentConfig = await this.loadGlobalSettings();
    currentConfig[key] = value;
    
    // Validate updated configuration
    await this.validator.validateGlobalSettings(currentConfig);
    
    // Save configuration
    await this.saveJsonFile('config/global_settings.json', currentConfig);
    
    // Notify configuration change
    await this.notifyConfigurationChange('global_settings', key, value);
  }
  
  async watchConfiguration(
    configPath: string,
    callback: (config: any) => void
  ): Promise<void> {
    const watcher = new ConfigWatcher(configPath, {
      onChange: async (newConfig) => {
        // Validate new configuration
        await this.validator.validate(configPath, newConfig);
        
        // Update cache
        this.configs.set(configPath, newConfig);
        
        // Notify callback
        callback(newConfig);
      }
    });
    
    await watcher.start();
    this.watchers.set(configPath, watcher);
  }
}
```

## KLP Message Contract Specification

### **Complete Message Schema**
```typescript
interface KLPMessageSchema {
  $schema: 'https://json-schema.org/draft/2020-12/schema';
  title: 'KLPMessage';
  type: 'object';
  required: ['type', 'from', 'to', 'task_id', 'payload'];
  properties: {
    type: {
      type: 'string';
      enum: [
        'TASK_REQUEST',
        'TASK_RESULT',
        'TASK_ERROR',
        'STATUS_UPDATE',
        'INTENTION_DECLARATION',
        'MEMORY_READ',
        'MEMORY_WRITE',
        'PLAN_GRAPH',
        'SECURITY_ALERT',
        'CONFIG_UPDATE'
      ];
    };
    from: { type: 'string'; format: 'agent_id' };
    to: { type: 'string'; format: 'agent_id' };
    task_id: { type: 'string'; format: 'uuid' };
    timestamp: { type: 'string'; format: 'date-time' };
    payload: { type: 'object' };
    auth: {
      type: 'object';
      properties: {
        signature: { type: 'string'; format: 'ed25519_signature' };
        token: { type: 'string'; format: 'jwt' };
        permissions: { type: 'array'; items: { type: 'string' } };
      };
      required: ['signature'];
    };
    metadata: {
      type: 'object';
      properties: {
        priority: {
          type: 'string';
          enum: ['low', 'normal', 'high', 'urgent'];
        };
        ttl: { type: 'number'; minimum: 0 };
        retryPolicy: { $ref: '#/definitions/RetryPolicy' };
      };
    };
  };
}

class KLPMessageValidator {
  private schema: JSONSchema;
  private ajv: AjvInstance;
  
  constructor() {
    this.schema = this.loadKLPSchema();
    this.ajv = new Ajv({ allErrors: true });
    this.ajv.addSchema(this.schema, 'klp-message');
  }
  
  async validateMessage(message: any): Promise<KLPMessage> {
    const isValid = this.ajv.validate('klp-message', message);
    
    if (!isValid) {
      const errors = this.ajv.errors || [];
      throw new KLPValidationError(
        'Invalid KLP message format',
        errors
      );
    }
    
    // Additional semantic validation
    await this.validateSemantics(message as KLPMessage);
    
    return message as KLPMessage;
  }
  
  private async validateSemantics(message: KLPMessage): Promise<void> {
    // Validate agent IDs exist
    await this.validateAgentExists(message.from);
    await this.validateAgentExists(message.to);
    
    // Validate timestamp is recent
    const messageTime = new Date(message.timestamp);
    const now = new Date();
    const maxAge = 5 * 60 * 1000; // 5 minutes
    
    if (now.getTime() - messageTime.getTime() > maxAge) {
      throw new KLPValidationError('Message timestamp too old');
    }
    
    // Validate payload structure based on message type
    await this.validatePayloadStructure(message.type, message.payload);
  }
}
```

## Role-to-File Mapping System

### **Agent Role Configuration**
```typescript
interface AgentRoleMapping {
  [roleName: string]: {
    mainFile: string;
    configPath: string;
    capabilities: string[];
    dependencies: string[];
    resources: ResourceRequirements;
    notes: string;
  };
}

const AGENT_ROLE_MAPPINGS: AgentRoleMapping = {
  kCore: {
    mainFile: 'agents/kCore/controller.py',
    configPath: 'config/global_settings.json',
    capabilities: ['orchestration', 'lifecycle_management', 'system_control'],
    dependencies: ['all_other_agents'],
    resources: {
      memory: '512MB',
      cpu: '0.5',
      storage: '1GB'
    },
    notes: 'Primary runtime orchestrator'
  },
  kPlanner: {
    mainFile: 'agents/kPlanner/planner.py',
    configPath: 'config/agents/kPlanner:*.json',
    capabilities: ['task_planning', 'goal_decomposition', 'knowledge_querying'],
    dependencies: ['kMemory', 'kCore'],
    resources: {
      memory: '1GB',
      cpu: '1.0',
      storage: '2GB'
    },
    notes: 'Supports dynamic subroles'
  },
  kExecutor: {
    mainFile: 'agents/kExecutor/executor.py',
    configPath: 'config/agents/kExecutor:*.json',
    capabilities: ['task_execution', 'plugin_management', 'tool_invocation'],
    dependencies: ['kCore', 'kSentinel'],
    resources: {
      memory: '2GB',
      cpu: '2.0',
      storage: '5GB'
    },
    notes: 'Pluggable execution handlers'
  },
  kBridge: {
    mainFile: 'agents/kBridge/bridge.py',
    configPath: 'config/services.yml',
    capabilities: ['api_integration', 'protocol_translation', 'service_proxy'],
    dependencies: ['kCore', 'kSentinel'],
    resources: {
      memory: '512MB',
      cpu: '0.5',
      storage: '1GB'
    },
    notes: 'Handles external API bindings'
  },
  kSentinel: {
    mainFile: 'agents/kSentinel/security.py',
    configPath: 'security/policies/*.yml',
    capabilities: ['security_monitoring', 'access_control', 'anomaly_detection'],
    dependencies: ['kCore'],
    resources: {
      memory: '1GB',
      cpu: '1.0',
      storage: '2GB'
    },
    notes: 'RBAC + anomaly detection'
  }
};

class AgentRoleManager {
  private roleMappings: Map<string, AgentRoleDefinition>;
  private activeAgents: Map<string, AgentInstance>;
  
  async initializeAgentRole(
    roleName: string,
    instanceId: string
  ): Promise<AgentInstance> {
    const roleDefinition = this.roleMappings.get(roleName);
    if (!roleDefinition) {
      throw new Error(`Unknown agent role: ${roleName}`);
    }
    
    // Create agent instance directory
    const instanceDir = await this.createAgentInstance(roleName, instanceId);
    
    // Load configuration
    const config = await this.loadAgentConfig(roleDefinition.configPath, instanceId);
    
    // Initialize agent runtime
    const agent = new AgentInstance({
      id: instanceId,
      role: roleName,
      definition: roleDefinition,
      config,
      directory: instanceDir
    });
    
    // Register dependencies
    await this.registerDependencies(agent, roleDefinition.dependencies);
    
    // Start agent
    await agent.initialize();
    
    this.activeAgents.set(instanceId, agent);
    return agent;
  }
  
  async getAgentsByRole(roleName: string): Promise<AgentInstance[]> {
    return Array.from(this.activeAgents.values())
      .filter(agent => agent.role === roleName);
  }
  
  async updateAgentConfig(
    instanceId: string,
    configUpdates: Partial<AgentConfiguration>
  ): Promise<void> {
    const agent = this.activeAgents.get(instanceId);
    if (!agent) {
      throw new Error(`Agent instance not found: ${instanceId}`);
    }
    
    // Validate configuration updates
    await this.validateConfigUpdates(agent.role, configUpdates);
    
    // Apply configuration updates
    await agent.updateConfiguration(configUpdates);
    
    // Persist configuration
    await this.persistAgentConfig(instanceId, agent.config);
  }
}
```

## Environment and Runtime Configuration

### **Environment Configuration System**
```typescript
interface EnvironmentConfiguration {
  database: {
    postgresUrl: string;
    redisUrl: string;
    vectorDb: 'qdrant' | 'chroma' | 'weaviate';
  };
  runtime: {
    debug: boolean;
    enableKlp: boolean;
    agentKeyDir: string;
    maxConcurrentTasks: number;
  };
  security: {
    vaultEnabled: boolean;
    encryptionLevel: 'basic' | 'enhanced' | 'paranoid';
    auditLevel: 'minimal' | 'standard' | 'comprehensive';
  };
  networking: {
    meshEnabled: boolean;
    p2pPort: number;
    apiPort: number;
    websocketPort: number;
  };
}

class EnvironmentManager {
  private config: EnvironmentConfiguration;
  private configPath: string;
  
  async loadEnvironmentConfig(): Promise<EnvironmentConfiguration> {
    // Load from .env file
    const envConfig = await this.loadDotEnv();
    
    // Load from environment variables
    const processEnv = this.loadProcessEnvironment();
    
    // Merge configurations (process env takes precedence)
    const mergedConfig = { ...envConfig, ...processEnv };
    
    // Validate configuration
    await this.validateEnvironmentConfig(mergedConfig);
    
    this.config = mergedConfig;
    return this.config;
  }
  
  private loadProcessEnvironment(): Partial<EnvironmentConfiguration> {
    return {
      database: {
        postgresUrl: process.env.POSTGRES_URL || '',
        redisUrl: process.env.REDIS_URL || '',
        vectorDb: (process.env.VECTORDB as any) || 'qdrant'
      },
      runtime: {
        debug: process.env.DEBUG === 'true',
        enableKlp: process.env.ENABLE_KLP !== 'false',
        agentKeyDir: process.env.AGENT_KEY_DIR || './security/keys',
        maxConcurrentTasks: parseInt(process.env.MAX_CONCURRENT_TASKS || '10')
      },
      security: {
        vaultEnabled: process.env.VAULT_ENABLED === 'true',
        encryptionLevel: (process.env.ENCRYPTION_LEVEL as any) || 'enhanced',
        auditLevel: (process.env.AUDIT_LEVEL as any) || 'standard'
      },
      networking: {
        meshEnabled: process.env.MESH_ENABLED !== 'false',
        p2pPort: parseInt(process.env.P2P_PORT || '4000'),
        apiPort: parseInt(process.env.API_PORT || '3000'),
        websocketPort: parseInt(process.env.WS_PORT || '3001')
      }
    };
  }
}
```

### **Runtime System Initialization**
```typescript
interface SystemRuntimeConfiguration {
  orchestrator: {
    enabled: boolean;
    startupScript: string;
    healthCheckInterval: number;
  };
  agents: {
    autoStart: string[];
    startupOrder: string[];
    dependencies: Record<string, string[]>;
  };
  monitoring: {
    enabled: boolean;
    metricsPort: number;
    logLevel: string;
  };
}

class SystemRuntime {
  private config: SystemRuntimeConfiguration;
  private orchestrator: SystemOrchestrator;
  private agentManager: AgentManager;
  private monitoringService: MonitoringService;
  
  async startSystem(): Promise<void> {
    try {
      // Initialize core services
      await this.initializeCoreServices();
      
      // Start orchestrator
      await this.orchestrator.start();
      
      // Initialize agents in dependency order
      await this.initializeAgents();
      
      // Start monitoring
      if (this.config.monitoring.enabled) {
        await this.monitoringService.start();
      }
      
      // Setup graceful shutdown
      this.setupGracefulShutdown();
      
      console.log('System started successfully');
      
    } catch (error) {
      console.error('Failed to start system:', error);
      await this.gracefulShutdown();
      throw error;
    }
  }
  
  private async initializeAgents(): Promise<void> {
    const startupOrder = this.config.agents.startupOrder;
    
    for (const agentType of startupOrder) {
      try {
        await this.agentManager.startAgent(agentType);
        console.log(`Started agent: ${agentType}`);
      } catch (error) {
        console.error(`Failed to start agent ${agentType}:`, error);
        throw error;
      }
    }
  }
  
  private setupGracefulShutdown(): void {
    const shutdown = async (signal: string) => {
      console.log(`Received ${signal}, starting graceful shutdown...`);
      await this.gracefulShutdown();
      process.exit(0);
    };
    
    process.on('SIGINT', () => shutdown('SIGINT'));
    process.on('SIGTERM', () => shutdown('SIGTERM'));
  }
  
  private async gracefulShutdown(): Promise<void> {
    // Stop monitoring
    await this.monitoringService?.stop();
    
    // Stop agents in reverse order
    await this.agentManager.stopAllAgents();
    
    // Stop orchestrator
    await this.orchestrator?.stop();
  }
}
```

## For AI Agents

### **When to Use This Document**
- ✅ Setting up system directory structure and file organization
- ✅ Implementing agent configuration management systems
- ✅ Understanding KLP message schemas and validation
- ✅ Configuring agent role mappings and dependencies
- ✅ Setting up environment and runtime configuration

### **Key Implementation Points**
- **Directory Structure**: Follow exact directory layout for consistency and interoperability
- **Configuration Standards**: Use JSON for runtime settings, YAML for user-editable configs
- **KLP Protocol**: All inter-agent messages must conform to KLP schema
- **Role-Based Organization**: Each agent type has specific file and configuration patterns
- **Environment Management**: Support multiple configuration sources with proper precedence

### **Critical Design Patterns**
- **Hierarchical Configuration**: Global → Role → Instance configuration inheritance
- **Schema Validation**: All configurations and messages validated against schemas
- **Directory Conventions**: Consistent file organization across all agent types
- **Runtime Initialization**: Dependency-aware startup sequence with health checks
- **Graceful Lifecycle**: Proper initialization and shutdown procedures

## Related Documentation
- **Agent Hierarchy**: `../agents/38_agent-protocols-hierarchy-complete.md`
- **KLP Protocol**: `./01_kind-link-protocol-core.md`
- **Core Architecture**: `../architecture/10_kos-core-architecture-internal.md`
- **Service Architecture**: `../services/01_service-architecture.md`

## External References
- [JSON Schema Specification](https://json-schema.org/) - Configuration validation
- [YAML Specification](https://yaml.org/) - Human-readable configuration format
- [FastAPI Documentation](https://fastapi.tiangolo.com/) - Python web framework
- [Python Type Hints](https://docs.python.org/3/library/typing.html) - Type system for Python 