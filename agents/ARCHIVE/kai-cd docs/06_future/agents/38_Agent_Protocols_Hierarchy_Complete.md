---
title: "Agent Protocols and Role Hierarchy System"
description: "Hierarchical structure, communication standards, coordination logic, and execution framework for all AI agents in the kAI and kOS ecosystem"
category: "agents"
subcategory: "protocols-hierarchy"
context: "future_vision"
implementation_status: "planned"
decision_scope: "critical"
complexity: "very_high"
last_updated: "2025-01-27"
code_references:
  - "src/features/ai-services/"
  - "src/store/"
  - "src/core/"
related_documents:
  - "./01_agent-hierarchy.md"
  - "../protocols/01_kind-link-protocol-core.md"
  - "../architecture/10_kos-core-architecture-internal.md"
dependencies: ["KLP Protocol", "Identity System", "Agent Engine", "Communication Infrastructure"]
breaking_changes: false
agent_notes: "Complete agent hierarchy and protocol specification defining roles, communication standards, and coordination patterns for the entire kOS ecosystem. Use this for understanding agent relationships, implementing communication protocols, and designing agent coordination systems."
---

# Agent Protocols and Role Hierarchy System

> **Agent Context**: Definitive specification for agent hierarchy, communication protocols, and coordination patterns in the kOS ecosystem. Use this document for implementing agent systems, designing communication protocols, and understanding agent role relationships. Critical for any agent-related development work.

## Quick Summary
Comprehensive hierarchical structure, communication standards, coordination logic, configuration protocols, and execution framework supporting modular, extensible, and secure coordination between agents across distributed environments.

## Implementation Status
- 🔬 **Research**: Complete agent hierarchy and protocol design
- 📋 **Planned**: Full agent coordination system implementation
- 🔄 **In Progress**: Core agent types and communication protocols
- ⚠️ **Dependencies**: Requires KLP protocol and identity system

## Agent Role Hierarchy

### **Agent Classes by Responsibility Scope**
```typescript
interface AgentHierarchy {
  kCore: {
    role: 'Primary Controller';
    description: 'Global coordinator agent overseeing all agent lifecycles, routing, and system configuration';
    scope: 'system_wide';
    capabilities: ['lifecycle_management', 'routing_control', 'system_configuration'];
  };
  kCoordinator: {
    role: 'Domain Coordinator';
    description: 'Manages sub-domains (Health, Scheduling, Research), assigns work to planners and evaluators';
    scope: 'domain_specific';
    capabilities: ['domain_management', 'task_assignment', 'resource_allocation'];
  };
  kPlanner: {
    role: 'Planner Agent';
    description: 'Converts user goals into tasks, queries knowledge base, generates task graphs';
    scope: 'task_planning';
    capabilities: ['goal_decomposition', 'knowledge_querying', 'task_graph_generation'];
  };
  kExecutor: {
    role: 'Worker Agent';
    description: 'Executes single tasks (code run, API call, data retrieval) - pure execution, no reasoning';
    scope: 'task_execution';
    capabilities: ['code_execution', 'api_calls', 'data_retrieval'];
  };
  kReviewer: {
    role: 'Evaluator Agent';
    description: 'Performs QA, test coverage, output verification, formatting, consistency checking';
    scope: 'quality_assurance';
    capabilities: ['quality_analysis', 'test_coverage', 'output_verification'];
  };
  kSentinel: {
    role: 'Security Agent';
    description: 'Monitors anomalies, enforces boundaries, access control, usage audits';
    scope: 'security_monitoring';
    capabilities: ['anomaly_detection', 'boundary_enforcement', 'access_control'];
  };
  kMemory: {
    role: 'Memory Agent';
    description: 'Handles memory retrieval, summarization, embedding, and memory map updates';
    scope: 'memory_management';
    capabilities: ['memory_retrieval', 'summarization', 'embedding', 'indexing'];
  };
  kPersona: {
    role: 'Persona Host';
    description: 'Maintains persona constraints, tone, context, user alignment';
    scope: 'personality_management';
    capabilities: ['persona_constraints', 'tone_management', 'context_awareness'];
  };
  kBridge: {
    role: 'Service Proxy';
    description: 'Acts as connector between external APIs and internal service mesh';
    scope: 'service_integration';
    capabilities: ['protocol_translation', 'api_bridging', 'service_mesh_integration'];
  };
}

abstract class Agent {
  protected id: string;
  protected type: AgentType;
  protected capabilities: AgentCapability[];
  protected state: AgentState;
  protected config: AgentConfig;
  
  constructor(config: AgentConfig) {
    this.id = config.id;
    this.type = config.type;
    this.capabilities = config.capabilities;
    this.state = AgentState.INITIALIZING;
    this.config = config;
  }
  
  abstract async initialize(): Promise<void>;
  abstract async processMessage(message: AgentMessage): Promise<AgentResponse>;
  abstract async shutdown(): Promise<void>;
  
  async updateState(newState: AgentState): Promise<void> {
    const previousState = this.state;
    this.state = newState;
    
    await this.notifyStateChange(previousState, newState);
  }
  
  protected async notifyStateChange(
    from: AgentState, 
    to: AgentState
  ): Promise<void> {
    const event = {
      agentId: this.id,
      type: 'state_change',
      from,
      to,
      timestamp: new Date()
    };
    
    await this.emitEvent('agent.state.changed', event);
  }
}

class CoreAgent extends Agent {
  private agentRegistry: AgentRegistry;
  private systemRouter: SystemRouter;
  private configurationManager: ConfigurationManager;
  
  async initialize(): Promise<void> {
    await this.agentRegistry.initialize();
    await this.systemRouter.initialize();
    await this.configurationManager.initialize();
    
    this.state = AgentState.ACTIVE;
  }
  
  async processMessage(message: AgentMessage): Promise<AgentResponse> {
    switch (message.type) {
      case 'AGENT_REGISTRATION':
        return await this.handleAgentRegistration(message);
      case 'ROUTE_REQUEST':
        return await this.handleRouteRequest(message);
      case 'CONFIG_UPDATE':
        return await this.handleConfigUpdate(message);
      default:
        throw new Error(`Unknown message type: ${message.type}`);
    }
  }
  
  private async handleAgentRegistration(
    message: AgentMessage
  ): Promise<AgentResponse> {
    const agentInfo = message.payload as AgentRegistrationInfo;
    
    // Validate agent configuration
    await this.validateAgentConfig(agentInfo.config);
    
    // Register in system
    const registrationId = await this.agentRegistry.register(agentInfo);
    
    // Setup routing
    await this.systemRouter.addAgent(agentInfo.id, agentInfo.capabilities);
    
    return {
      type: 'REGISTRATION_SUCCESS',
      payload: { registrationId },
      timestamp: new Date()
    };
  }
}
```

### **Agent Types by Interaction Mode**
```typescript
interface AgentInteractionModes {
  active: {
    description: 'Initiates tasks autonomously or by schedule';
    triggers: ['autonomous_decisions', 'scheduled_tasks', 'event_driven'];
    examples: ['monitoring_agents', 'maintenance_agents', 'proactive_assistants'];
  };
  reactive: {
    description: 'Waits for user or agent requests';
    triggers: ['user_requests', 'agent_messages', 'external_events'];
    examples: ['service_agents', 'query_processors', 'tool_executors'];
  };
  hybrid: {
    description: 'Periodically monitors context + responds to triggers';
    triggers: ['periodic_monitoring', 'context_changes', 'threshold_events'];
    examples: ['adaptive_agents', 'learning_agents', 'optimization_agents'];
  };
}

class AgentModeManager {
  private activeAgents: Set<string>;
  private reactiveAgents: Set<string>;
  private hybridAgents: Set<string>;
  private scheduler: TaskScheduler;
  
  async configureAgentMode(agentId: string, mode: AgentMode): Promise<void> {
    // Remove from previous mode
    await this.removeFromAllModes(agentId);
    
    // Add to new mode
    switch (mode) {
      case 'active':
        this.activeAgents.add(agentId);
        await this.scheduler.scheduleActiveAgent(agentId);
        break;
      case 'reactive':
        this.reactiveAgents.add(agentId);
        await this.setupReactiveListeners(agentId);
        break;
      case 'hybrid':
        this.hybridAgents.add(agentId);
        await this.setupHybridMode(agentId);
        break;
    }
  }
  
  private async setupHybridMode(agentId: string): Promise<void> {
    // Schedule periodic monitoring
    await this.scheduler.schedulePeriodicTask(agentId, {
      interval: '5m',
      task: 'context_monitoring'
    });
    
    // Setup reactive listeners
    await this.setupReactiveListeners(agentId);
  }
}
```

## Inter-Agent Communication (KLP Protocol)

### **Message Types and Structure**
```typescript
interface KLPMessageTypes {
  TASK_REQUEST: {
    purpose: 'Request task execution from another agent';
    fields: ['task_definition', 'parameters', 'priority', 'deadline'];
  };
  TASK_RESULT: {
    purpose: 'Return task execution results';
    fields: ['task_id', 'result_data', 'status', 'metadata'];
  };
  TASK_ERROR: {
    purpose: 'Report task execution failure';
    fields: ['task_id', 'error_code', 'error_message', 'retry_info'];
  };
  STATUS_UPDATE: {
    purpose: 'Share agent status information';
    fields: ['agent_status', 'capabilities', 'load_metrics', 'availability'];
  };
  INTENTION_DECLARATION: {
    purpose: 'Declare intended actions for coordination';
    fields: ['intended_actions', 'resource_requirements', 'timeline'];
  };
  MEMORY_READ: {
    purpose: 'Request memory access';
    fields: ['memory_path', 'access_type', 'permissions'];
  };
  MEMORY_WRITE: {
    purpose: 'Request memory update';
    fields: ['memory_path', 'data', 'metadata', 'permissions'];
  };
  PLAN_GRAPH: {
    purpose: 'Share task planning graphs';
    fields: ['plan_id', 'task_graph', 'dependencies', 'timeline'];
  };
  SECURITY_ALERT: {
    purpose: 'Report security issues or violations';
    fields: ['alert_level', 'description', 'affected_resources', 'recommendations'];
  };
  CONFIG_UPDATE: {
    purpose: 'Update agent configuration';
    fields: ['config_section', 'new_values', 'validation_info'];
  };
}

interface KLPMessage {
  header: {
    type: keyof KLPMessageTypes;
    from: string;
    to: string;
    taskId?: string;
    timestamp: string;
    version: '1.0.0';
  };
  payload: {
    action?: string;
    target?: string;
    params?: Record<string, any>;
    data?: any;
  };
  auth: {
    signature: string;
    token?: string;
    permissions?: string[];
  };
  metadata: {
    priority: 'low' | 'normal' | 'high' | 'urgent';
    ttl?: number;
    retryPolicy?: RetryPolicy;
  };
}

class KLPMessageHandler {
  private messageHandlers: Map<string, MessageHandler>;
  private cryptoService: CryptographicService;
  private routingService: RoutingService;
  
  async processMessage(message: KLPMessage): Promise<KLPResponse> {
    // Validate message structure
    await this.validateMessage(message);
    
    // Verify authentication
    const authResult = await this.cryptoService.verifySignature(
      message.auth.signature,
      message,
      message.header.from
    );
    
    if (!authResult.valid) {
      throw new Error('Message authentication failed');
    }
    
    // Route to appropriate handler
    const handler = this.messageHandlers.get(message.header.type);
    if (!handler) {
      throw new Error(`No handler for message type: ${message.header.type}`);
    }
    
    // Process message
    const response = await handler.process(message);
    
    // Sign response
    const signedResponse = await this.cryptoService.signMessage(response);
    
    return signedResponse;
  }
  
  async sendMessage(to: string, message: Partial<KLPMessage>): Promise<void> {
    const fullMessage: KLPMessage = {
      header: {
        type: message.header?.type || 'STATUS_UPDATE',
        from: this.agentId,
        to,
        timestamp: new Date().toISOString(),
        version: '1.0.0',
        ...message.header
      },
      payload: message.payload || {},
      auth: {
        signature: '',
        ...message.auth
      },
      metadata: {
        priority: 'normal',
        ...message.metadata
      }
    };
    
    // Sign message
    fullMessage.auth.signature = await this.cryptoService.signMessage(fullMessage);
    
    // Send via routing service
    await this.routingService.route(fullMessage);
  }
}
```

### **Transport Protocol Implementation**
```typescript
interface TransportProtocols {
  webSocket: {
    purpose: 'Local real-time mesh communication';
    features: ['low_latency', 'bidirectional', 'connection_pooling'];
    implementation: 'socket.io' | 'native_websocket';
  };
  grpc: {
    purpose: 'High-performance backend microservices';
    features: ['streaming', 'type_safety', 'load_balancing'];
    implementation: '@grpc/grpc-js';
  };
  mqtt: {
    purpose: 'Lightweight mesh broadcasting';
    features: ['publish_subscribe', 'qos_levels', 'retained_messages'];
    implementation: 'mqtt.js';
  };
  nats: {
    purpose: 'High-performance message streaming';
    features: ['clustering', 'jetstream', 'key_value_store'];
    implementation: 'nats.js';
  };
  rest: {
    purpose: 'HTTP-based integrations fallback';
    features: ['request_response', 'caching', 'rate_limiting'];
    implementation: 'fastify' | 'express';
  };
}

class TransportManager {
  private transports: Map<string, Transport>;
  private routingTable: RoutingTable;
  private loadBalancer: LoadBalancer;
  
  async initializeTransports(): Promise<void> {
    // Initialize WebSocket transport
    const websocket = new WebSocketTransport({
      port: this.config.websocket.port,
      path: '/ws',
      cors: this.config.websocket.cors
    });
    
    await websocket.initialize();
    this.transports.set('websocket', websocket);
    
    // Initialize gRPC transport
    const grpc = new GRPCTransport({
      port: this.config.grpc.port,
      services: this.config.grpc.services
    });
    
    await grpc.initialize();
    this.transports.set('grpc', grpc);
    
    // Initialize MQTT transport
    const mqtt = new MQTTTransport({
      broker: this.config.mqtt.broker,
      topics: this.config.mqtt.topics
    });
    
    await mqtt.initialize();
    this.transports.set('mqtt', mqtt);
  }
  
  async routeMessage(message: KLPMessage): Promise<void> {
    // Determine optimal transport
    const transport = await this.selectTransport(message);
    
    // Route message
    await transport.send(message);
    
    // Update routing metrics
    await this.updateRoutingMetrics(transport.name, message);
  }
  
  private async selectTransport(message: KLPMessage): Promise<Transport> {
    const destination = message.header.to;
    const routeInfo = await this.routingTable.getRoute(destination);
    
    if (routeInfo.isLocal) {
      return this.transports.get('websocket')!;
    } else if (routeInfo.requiresReliability) {
      return this.transports.get('grpc')!;
    } else {
      return this.transports.get('mqtt')!;
    }
  }
}
```

## Task Execution Protocol

### **Task Lifecycle Management**
```typescript
interface TaskLifecycle {
  states: {
    CREATED: 'Goal created by user or kCore';
    PLANNED: 'Plan generated by kPlanner';
    SPAWNED: 'Subtasks spawned and sent to kExecutor';
    EXECUTING: 'Execution in progress with logging';
    REVIEWING: 'kReviewer checks integrity and correctness';
    COMPLETED: 'kMemory embeds or indexes output';
    FAILED: 'Error occurred, retry or escalation needed';
  };
  transitions: {
    valid: [
      ['CREATED', 'PLANNED'],
      ['PLANNED', 'SPAWNED'],
      ['SPAWNED', 'EXECUTING'],
      ['EXECUTING', 'REVIEWING'],
      ['REVIEWING', 'COMPLETED'],
      ['EXECUTING', 'FAILED'],
      ['FAILED', 'SPAWNED'] // Retry
    ];
  };
}

class TaskLifecycleManager {
  private tasks: Map<string, Task>;
  private stateHandlers: Map<TaskState, StateHandler>;
  private eventBus: EventBus;
  
  async createTask(goal: Goal): Promise<string> {
    const taskId = this.generateTaskId();
    const task = new Task({
      id: taskId,
      goal,
      state: TaskState.CREATED,
      created: new Date(),
      metadata: {
        priority: goal.priority || 'normal',
        deadline: goal.deadline,
        requiredCapabilities: []
      }
    });
    
    this.tasks.set(taskId, task);
    
    // Emit creation event
    await this.eventBus.emit('task.created', {
      taskId,
      goal,
      timestamp: new Date()
    });
    
    // Trigger planning
    await this.transitionState(taskId, TaskState.PLANNED);
    
    return taskId;
  }
  
  async transitionState(taskId: string, newState: TaskState): Promise<void> {
    const task = this.tasks.get(taskId);
    if (!task) {
      throw new Error(`Task not found: ${taskId}`);
    }
    
    // Validate transition
    const isValidTransition = this.validateTransition(task.state, newState);
    if (!isValidTransition) {
      throw new Error(`Invalid transition: ${task.state} -> ${newState}`);
    }
    
    // Execute state transition
    const handler = this.stateHandlers.get(newState);
    if (handler) {
      await handler.enter(task);
    }
    
    // Update task state
    const previousState = task.state;
    task.state = newState;
    task.lastUpdated = new Date();
    
    // Emit state change event
    await this.eventBus.emit('task.state.changed', {
      taskId,
      from: previousState,
      to: newState,
      timestamp: new Date()
    });
  }
}
```

### **Traceability and Audit System**
```typescript
interface TaskTraceability {
  taskTags: {
    taskId: string;
    parentId?: string;
    planId: string;
    agentId: string;
    timestamp: string;
    resourceFootprint: ResourceFootprint;
  };
  auditTrail: {
    events: TaskEvent[];
    signatures: CryptographicSignature[];
    immutableLog: boolean;
  };
}

interface ResourceFootprint {
  cpu: {
    cores: number;
    utilization: number;
    duration: number;
  };
  memory: {
    allocated: number;
    peak: number;
    duration: number;
  };
  network: {
    bytesIn: number;
    bytesOut: number;
    connections: number;
  };
  storage: {
    bytesRead: number;
    bytesWritten: number;
    filesAccessed: string[];
  };
}

class TaskTraceabilityManager {
  private auditLog: AuditLog;
  private resourceMonitor: ResourceMonitor;
  private cryptoService: CryptographicService;
  
  async recordTaskExecution(
    task: Task,
    execution: TaskExecution
  ): Promise<void> {
    // Gather resource footprint
    const footprint = await this.resourceMonitor.getFootprint(execution);
    
    // Create audit entry
    const auditEntry = {
      taskId: task.id,
      parentId: task.parentId,
      planId: task.planId,
      agentId: execution.agentId,
      timestamp: new Date().toISOString(),
      resourceFootprint: footprint,
      execution: {
        startTime: execution.startTime,
        endTime: execution.endTime,
        success: execution.success,
        result: execution.result,
        error: execution.error
      }
    };
    
    // Sign audit entry
    const signature = await this.cryptoService.signData(auditEntry);
    
    // Store in immutable log
    await this.auditLog.append({
      ...auditEntry,
      signature
    });
  }
  
  async getTaskTrace(taskId: string): Promise<TaskTrace> {
    const entries = await this.auditLog.getEntriesForTask(taskId);
    
    // Verify signatures
    for (const entry of entries) {
      const isValid = await this.cryptoService.verifySignature(
        entry.signature,
        entry,
        entry.agentId
      );
      
      if (!isValid) {
        throw new Error(`Invalid signature in audit trail for task: ${taskId}`);
      }
    }
    
    return new TaskTrace(entries);
  }
}
```

### **Failure Handling and Recovery**
```typescript
interface FailureHandling {
  retryStrategies: {
    automatic: 'Automatic retry via kCoordinator';
    escalation: 'Escalation to user or fallback plan';
    throttling: 'Retry throttling and loop detection';
  };
  recoveryMechanisms: {
    checkpoint: 'Restore from previous checkpoint';
    rollback: 'Rollback to known good state';
    alternative: 'Switch to alternative execution path';
  };
}

class FailureRecoveryManager {
  private retryPolicies: Map<string, RetryPolicy>;
  private checkpointManager: CheckpointManager;
  private escalationManager: EscalationManager;
  
  async handleTaskFailure(
    taskId: string,
    error: TaskError
  ): Promise<RecoveryAction> {
    const task = await this.getTask(taskId);
    const retryPolicy = this.retryPolicies.get(task.type) || this.defaultRetryPolicy;
    
    // Check if retry is allowed
    if (task.retryCount < retryPolicy.maxRetries) {
      // Determine retry delay
      const delay = this.calculateRetryDelay(task.retryCount, retryPolicy);
      
      // Schedule retry
      return new RecoveryAction({
        type: 'retry',
        delay,
        modifications: await this.suggestRetryModifications(error)
      });
    }
    
    // Check for alternative execution paths
    const alternatives = await this.findAlternativePaths(task);
    if (alternatives.length > 0) {
      return new RecoveryAction({
        type: 'alternative',
        path: alternatives[0]
      });
    }
    
    // Escalate to human oversight
    return new RecoveryAction({
      type: 'escalation',
      escalationLevel: this.determineEscalationLevel(error),
      context: await this.buildEscalationContext(task, error)
    });
  }
  
  private calculateRetryDelay(
    retryCount: number,
    policy: RetryPolicy
  ): number {
    switch (policy.strategy) {
      case 'exponential':
        return Math.min(
          policy.baseDelay * Math.pow(2, retryCount),
          policy.maxDelay
        );
      case 'linear':
        return Math.min(
          policy.baseDelay * (retryCount + 1),
          policy.maxDelay
        );
      case 'fixed':
        return policy.baseDelay;
      default:
        return policy.baseDelay;
    }
  }
}
```

## Configuration and Synchronization

### **Agent Manifest System**
```typescript
interface AgentManifest {
  version: string;
  agents: AgentDefinition[];
  relationships: AgentRelationship[];
  policies: GlobalPolicy[];
}

interface AgentDefinition {
  id: string;
  name: string;
  type: AgentType;
  class: AgentClass;
  active: boolean;
  config: AgentConfiguration;
  capabilities: AgentCapability[];
  dependencies: string[];
}

class AgentManifestManager {
  private manifest: AgentManifest;
  private configStore: ConfigurationStore;
  private validator: ManifestValidator;
  
  async loadManifest(): Promise<void> {
    const manifestData = await this.configStore.load('agents/manifest.json');
    
    // Validate manifest structure
    await this.validator.validate(manifestData);
    
    this.manifest = manifestData as AgentManifest;
    
    // Initialize agents from manifest
    await this.initializeAgentsFromManifest();
  }
  
  async updateAgentConfig(
    agentId: string,
    config: Partial<AgentConfiguration>
  ): Promise<void> {
    // Find agent in manifest
    const agent = this.manifest.agents.find(a => a.id === agentId);
    if (!agent) {
      throw new Error(`Agent not found in manifest: ${agentId}`);
    }
    
    // Validate configuration
    await this.validator.validateAgentConfig(config);
    
    // Update configuration
    agent.config = { ...agent.config, ...config };
    
    // Persist manifest
    await this.configStore.save('agents/manifest.json', this.manifest);
    
    // Notify agent of configuration change
    await this.notifyAgentConfigChange(agentId, config);
  }
  
  private async initializeAgentsFromManifest(): Promise<void> {
    // Sort agents by dependencies
    const sortedAgents = await this.topologicalSort(this.manifest.agents);
    
    // Initialize agents in dependency order
    for (const agentDef of sortedAgents) {
      if (agentDef.active) {
        await this.initializeAgent(agentDef);
      }
    }
  }
}
```

### **Dynamic Configuration Management**
```typescript
interface DynamicConfiguration {
  hotReload: boolean;
  validationEnabled: boolean;
  backupOnChange: boolean;
  auditChanges: boolean;
}

class DynamicConfigManager {
  private configs: Map<string, AgentConfiguration>;
  private watchers: Map<string, ConfigWatcher>;
  private validator: ConfigValidator;
  
  async watchConfiguration(
    agentId: string,
    callback: (config: AgentConfiguration) => void
  ): Promise<void> {
    const watcher = new ConfigWatcher({
      path: `config/agents/${agentId}.json`,
      onChange: async (newConfig) => {
        // Validate configuration
        await this.validator.validate(newConfig);
        
        // Update cached config
        this.configs.set(agentId, newConfig);
        
        // Notify callback
        callback(newConfig);
      }
    });
    
    await watcher.start();
    this.watchers.set(agentId, watcher);
  }
  
  async updateConfig(
    agentId: string,
    updates: Partial<AgentConfiguration>
  ): Promise<void> {
    const currentConfig = this.configs.get(agentId);
    if (!currentConfig) {
      throw new Error(`Configuration not found for agent: ${agentId}`);
    }
    
    // Merge configurations
    const newConfig = { ...currentConfig, ...updates };
    
    // Validate merged configuration
    await this.validator.validate(newConfig);
    
    // Backup current configuration
    await this.backupConfiguration(agentId, currentConfig);
    
    // Save new configuration
    await this.saveConfiguration(agentId, newConfig);
    
    // Update cache
    this.configs.set(agentId, newConfig);
  }
}
```

## For AI Agents

### **When to Use This Document**
- ✅ Implementing agent communication protocols
- ✅ Understanding agent role hierarchies and responsibilities
- ✅ Designing task execution and lifecycle management
- ✅ Implementing failure handling and recovery systems
- ✅ Configuring agent coordination and synchronization

### **Key Implementation Points**
- **Role-Based Design**: Each agent class has specific responsibilities and capabilities
- **Protocol Compliance**: All communication must use KLP message formats
- **State Management**: Task lifecycle states must be properly managed and auditable
- **Security Integration**: All operations must be authenticated and authorized
- **Configuration Flexibility**: Support dynamic configuration updates with validation

### **Critical Design Patterns**
- **Hierarchical Coordination**: Higher-level agents coordinate lower-level agents
- **Message-Driven Architecture**: All inter-agent communication via structured messages
- **State Machine Pattern**: Task execution follows defined state transitions
- **Retry and Recovery**: Automatic failure handling with escalation paths
- **Audit Trail**: All operations must be traceable and verifiable

## Related Documentation
- **Agent Hierarchy**: `./01_agent-hierarchy.md`
- **KLP Protocol**: `../protocols/01_kind-link-protocol-core.md`
- **Core Architecture**: `../architecture/10_kos-core-architecture-internal.md`
- **Service Architecture**: `../services/01_service-architecture.md`

## External References
- [gRPC Documentation](https://grpc.io/docs/) - High-performance RPC framework
- [MQTT Protocol](https://mqtt.org/) - Lightweight messaging protocol
- [NATS Messaging](https://nats.io/) - Cloud native messaging system
- [WebSocket Standards](https://websockets.spec.whatwg.org/) - Real-time communication protocol 