---
title: "Agent Message Bus and Event Pipeline (KMB)"
description: "Comprehensive decentralized messaging system for event communication, state propagation, and task dispatch across agents and system modules"
version: "2.1.0"
last_updated: "2024-12-28"
category: "Communication"
tags: ["message-bus", "events", "communication", "distributed", "real-time"]
author: "kAI Development Team"
status: "active"
---

# Agent Message Bus and Event Pipeline (KMB)

## Agent Context
The Kind Message Bus (KMB) serves as the core architectural component providing a decentralized, modular, and extensible system for event communication, state propagation, service messaging, and task dispatch across all agents and system modules. This real-time nervous system of kAI supports plug-and-play message handlers, durable and ephemeral messages, topic subscriptions, routing layers, and both local and distributed deployment configurations with comprehensive security, traceability, and performance optimization.

## Overview

The Kind Message Bus (KMB) provides the foundational communication infrastructure that enables seamless interaction between agents, services, and users through a secure, traceable, low-latency messaging layer with modular architecture supporting both centralized and federated deployments.

## 🎯 Objectives and Architecture

```typescript
interface MessageBusObjectives {
  eventPublishing: PublishSubscribeSystem;
  secureTraceability: SecurityTraceabilityLayer;
  modularExtensibility: PluginSystem;
  deploymentFlexibility: DeploymentModes;
}

class KindMessageBus {
  private readonly broker: KMBBroker;
  private readonly topicRegistry: TopicRegistry;
  private readonly securityLayer: SecurityLayer;
  private readonly devTools: DevToolsDashboard;
  private readonly clientManager: ClientManager;

  constructor(config: KMBConfig) {
    this.broker = new KMBBroker(config.broker);
    this.topicRegistry = new TopicRegistry(config.topics);
    this.securityLayer = new SecurityLayer(config.security);
    this.devTools = new DevToolsDashboard(config.devtools);
    this.clientManager = new ClientManager(config.clients);
  }

  async initialize(): Promise<InitializationResult> {
    // Initialize core components
    await this.broker.initialize();
    await this.topicRegistry.loadTopics();
    await this.securityLayer.setupAuthentication();
    
    // Start monitoring and health checks
    await this.startHealthMonitoring();
    
    // Register built-in message handlers
    await this.registerCoreHandlers();

    return {
      status: 'initialized',
      brokerStatus: await this.broker.getStatus(),
      registeredTopics: await this.topicRegistry.getTopicCount(),
      activeClients: this.clientManager.getActiveClientCount(),
      timestamp: new Date().toISOString()
    };
  }

  async publish(message: KMBMessage): Promise<PublishResult> {
    // Validate message format
    const validation = await this.validateMessage(message);
    if (!validation.valid) {
      return {
        success: false,
        reason: 'Message validation failed',
        errors: validation.errors
      };
    }

    // Apply security and signing
    const securedMessage = await this.securityLayer.secureMessage(message);
    
    // Route through broker
    const routingResult = await this.broker.routeMessage(securedMessage);
    
    // Log for traceability
    await this.logMessageEvent('publish', securedMessage, routingResult);

    return {
      success: routingResult.success,
      messageId: securedMessage.id,
      deliveredTo: routingResult.deliveredTo,
      timestamp: securedMessage.timestamp
    };
  }

  async subscribe(
    topic: string, 
    handler: MessageHandler, 
    options: SubscriptionOptions = {}
  ): Promise<Subscription> {
    // Validate topic access
    const accessValidation = await this.securityLayer.validateTopicAccess(
      topic, 
      options.clientId
    );
    
    if (!accessValidation.allowed) {
      throw new Error(`Access denied to topic: ${topic}`);
    }

    // Create subscription
    const subscription: Subscription = {
      id: crypto.randomUUID(),
      topic,
      handler,
      options,
      createdAt: new Date().toISOString(),
      active: true
    };

    // Register with broker
    await this.broker.addSubscription(subscription);
    
    // Track for management
    this.clientManager.trackSubscription(subscription);

    return subscription;
  }
}
```

## 🔌 Core Components Implementation

### 1. KMB Broker

```typescript
class KMBBroker {
  private readonly backend: MessageBackend;
  private readonly routingEngine: RoutingEngine;
  private readonly durabilityManager: DurabilityManager;
  private readonly transformPipeline: TransformPipeline;

  constructor(config: BrokerConfig) {
    this.backend = this.createBackend(config.backend);
    this.routingEngine = new RoutingEngine(config.routing);
    this.durabilityManager = new DurabilityManager(config.durability);
    this.transformPipeline = new TransformPipeline(config.transforms);
  }

  private createBackend(config: BackendConfig): MessageBackend {
    switch (config.type) {
      case 'redis':
        return new RedisBackend(config.redis);
      case 'postgres':
        return new PostgresBackend(config.postgres);
      case 'nats':
        return new NATSBackend(config.nats);
      case 'kafka':
        return new KafkaBackend(config.kafka);
      default:
        throw new Error(`Unsupported backend type: ${config.type}`);
    }
  }

  async routeMessage(message: SecuredKMBMessage): Promise<RoutingResult> {
    // Apply message transforms
    const transformedMessage = await this.transformPipeline.process(message);
    
    // Determine routing targets
    const targets = await this.routingEngine.findTargets(transformedMessage.topic);
    
    // Handle durability if required
    if (transformedMessage.metadata.durable) {
      await this.durabilityManager.persistMessage(transformedMessage);
    }

    // Deliver to targets
    const deliveryResults = await Promise.allSettled(
      targets.map(target => this.deliverToTarget(transformedMessage, target))
    );

    const successful = deliveryResults.filter(r => r.status === 'fulfilled');
    const failed = deliveryResults.filter(r => r.status === 'rejected');

    return {
      success: successful.length > 0,
      totalTargets: targets.length,
      successfulDeliveries: successful.length,
      failedDeliveries: failed.length,
      deliveredTo: successful.map((r, i) => targets[i].id),
      errors: failed.map(r => (r as PromiseRejectedResult).reason)
    };
  }

  private async deliverToTarget(
    message: SecuredKMBMessage, 
    target: RoutingTarget
  ): Promise<DeliveryResult> {
    try {
      // Apply target-specific transforms
      const targetMessage = await this.applyTargetTransforms(message, target);
      
      // Deliver via appropriate transport
      const delivery = await this.backend.deliver(targetMessage, target);
      
      // Handle acknowledgment if required
      if (target.requiresAck) {
        await this.waitForAcknowledgment(message.id, target, 30000); // 30s timeout
      }

      return {
        success: true,
        targetId: target.id,
        deliveredAt: new Date().toISOString(),
        acknowledged: target.requiresAck
      };
    } catch (error) {
      // Handle delivery failure
      await this.handleDeliveryFailure(message, target, error);
      throw error;
    }
  }

  async handleDeliveryFailure(
    message: SecuredKMBMessage,
    target: RoutingTarget,
    error: Error
  ): Promise<void> {
    // Add to dead letter queue if configured
    if (target.deadLetterQueue) {
      await this.addToDeadLetterQueue(message, target, error);
    }

    // Retry logic
    if (target.retryPolicy && target.retryCount < target.retryPolicy.maxRetries) {
      const delay = this.calculateRetryDelay(target.retryCount, target.retryPolicy);
      setTimeout(() => {
        this.deliverToTarget(message, { ...target, retryCount: target.retryCount + 1 });
      }, delay);
    }

    // Log failure
    await this.logDeliveryFailure(message, target, error);
  }
}
```

### 2. Topic Registry System

```typescript
class TopicRegistry {
  private readonly schemaValidator: SchemaValidator;
  private readonly versionManager: TopicVersionManager;
  private readonly accessController: TopicAccessController;
  private readonly topics = new Map<string, TopicDefinition>();

  constructor(config: TopicRegistryConfig) {
    this.schemaValidator = new SchemaValidator(config.validation);
    this.versionManager = new TopicVersionManager(config.versioning);
    this.accessController = new TopicAccessController(config.access);
  }

  async registerTopic(definition: TopicDefinition): Promise<TopicRegistration> {
    // Validate topic definition
    const validation = await this.validateTopicDefinition(definition);
    if (!validation.valid) {
      throw new Error(`Topic validation failed: ${validation.errors.join(', ')}`);
    }

    // Check for conflicts
    const existingTopic = this.topics.get(definition.name);
    if (existingTopic) {
      return await this.handleTopicConflict(definition, existingTopic);
    }

    // Register topic
    const registration: TopicRegistration = {
      id: crypto.randomUUID(),
      topic: definition,
      registeredAt: new Date().toISOString(),
      version: '1.0.0',
      status: 'active'
    };

    this.topics.set(definition.name, definition);
    await this.persistTopicRegistration(registration);

    return registration;
  }

  async validateMessage(topic: string, message: any): Promise<MessageValidation> {
    const topicDef = this.topics.get(topic);
    if (!topicDef) {
      return {
        valid: false,
        errors: [`Unknown topic: ${topic}`]
      };
    }

    // Validate against schema
    const schemaValidation = await this.schemaValidator.validate(
      message,
      topicDef.schema
    );

    if (!schemaValidation.valid) {
      return {
        valid: false,
        errors: schemaValidation.errors,
        topic
      };
    }

    // Validate message format requirements
    const formatValidation = this.validateMessageFormat(message, topicDef);
    
    return {
      valid: formatValidation.valid,
      errors: formatValidation.errors,
      topic,
      schema: topicDef.schema.version
    };
  }

  private async handleTopicConflict(
    newDefinition: TopicDefinition,
    existingDefinition: TopicDefinition
  ): Promise<TopicRegistration> {
    // Check if it's a version update
    if (this.isVersionUpdate(newDefinition, existingDefinition)) {
      return await this.versionManager.createNewVersion(newDefinition, existingDefinition);
    }

    // Check if schemas are compatible
    const compatibility = await this.schemaValidator.checkCompatibility(
      newDefinition.schema,
      existingDefinition.schema
    );

    if (compatibility.compatible) {
      // Update existing topic
      return await this.updateExistingTopic(newDefinition, existingDefinition);
    } else {
      throw new Error(
        `Topic conflict: ${newDefinition.name} - Incompatible schema changes detected`
      );
    }
  }
}
```

### 3. Security Layer Implementation

```typescript
class SecurityLayer {
  private readonly authProvider: AuthenticationProvider;
  private readonly encryptionService: EncryptionService;
  private readonly signingService: SigningService;
  private readonly accessControl: AccessControlManager;

  constructor(config: SecurityConfig) {
    this.authProvider = new AuthenticationProvider(config.auth);
    this.encryptionService = new EncryptionService(config.encryption);
    this.signingService = new SigningService(config.signing);
    this.accessControl = new AccessControlManager(config.access);
  }

  async secureMessage(message: KMBMessage): Promise<SecuredKMBMessage> {
    // Add timestamp and nonce for replay protection
    const securityMetadata: SecurityMetadata = {
      timestamp: new Date().toISOString(),
      nonce: crypto.randomUUID(),
      version: '1.0.0'
    };

    // Sign message
    const signature = await this.signingService.signMessage(message, securityMetadata);

    // Encrypt if required
    let encryptedPayload = message.payload;
    if (message.metadata?.encrypted) {
      encryptedPayload = await this.encryptionService.encrypt(
        JSON.stringify(message.payload),
        message.metadata.encryptionKey
      );
    }

    const securedMessage: SecuredKMBMessage = {
      ...message,
      payload: encryptedPayload,
      security: securityMetadata,
      signature,
      proofs: await this.generateProofs(message)
    };

    return securedMessage;
  }

  async validateTopicAccess(
    topic: string,
    clientId: string
  ): Promise<AccessValidation> {
    // Get client permissions
    const clientPermissions = await this.accessControl.getClientPermissions(clientId);
    
    // Check topic-specific permissions
    const topicPermissions = await this.accessControl.getTopicPermissions(topic);
    
    // Evaluate access
    const hasAccess = this.evaluateAccess(clientPermissions, topicPermissions, 'subscribe');
    
    return {
      allowed: hasAccess,
      clientId,
      topic,
      permissions: hasAccess ? clientPermissions : [],
      reason: hasAccess ? undefined : 'Insufficient permissions'
    };
  }

  private async generateProofs(message: KMBMessage): Promise<string[]> {
    const proofs: string[] = [];

    // Add identity proof
    if (message.metadata?.requiresIdentityProof) {
      const identityProof = await this.generateIdentityProof(message.source);
      proofs.push(`identity:${identityProof}`);
    }

    // Add capability proof
    if (message.metadata?.requiresCapabilityProof) {
      const capabilityProof = await this.generateCapabilityProof(
        message.source,
        message.topic
      );
      proofs.push(`capability:${capabilityProof}`);
    }

    return proofs;
  }
}
```

## 📦 Message Format and Types

### Message Structure

```typescript
interface KMBMessage {
  id: string;
  timestamp: string;
  topic: string;
  type: MessageType;
  source: string;
  destination?: string;
  payload: MessagePayload;
  metadata: MessageMetadata;
  traceId?: string;
}

interface MessageMetadata {
  priority: 'low' | 'medium' | 'high' | 'critical';
  durable: boolean;
  encrypted: boolean;
  encryptionKey?: string;
  ttl?: number;
  requiresAck: boolean;
  requiresIdentityProof?: boolean;
  requiresCapabilityProof?: boolean;
  compression?: 'gzip' | 'brotli' | 'none';
  encoding?: 'json' | 'cbor' | 'msgpack';
}

enum MessageType {
  EVENT = 'event',
  COMMAND = 'command',
  QUERY = 'query',
  TRANSACTIONAL = 'transactional'
}

class MessageFactory {
  static createEvent(
    topic: string,
    payload: any,
    source: string,
    options: Partial<MessageMetadata> = {}
  ): KMBMessage {
    return {
      id: crypto.randomUUID(),
      timestamp: new Date().toISOString(),
      topic,
      type: MessageType.EVENT,
      source,
      payload,
      metadata: {
        priority: 'medium',
        durable: false,
        encrypted: false,
        requiresAck: false,
        compression: 'none',
        encoding: 'json',
        ...options
      }
    };
  }

  static createCommand(
    topic: string,
    command: string,
    parameters: any,
    source: string,
    destination: string,
    options: Partial<MessageMetadata> = {}
  ): KMBMessage {
    return {
      id: crypto.randomUUID(),
      timestamp: new Date().toISOString(),
      topic,
      type: MessageType.COMMAND,
      source,
      destination,
      payload: {
        command,
        parameters,
        expectsResponse: true
      },
      metadata: {
        priority: 'high',
        durable: true,
        encrypted: false,
        requiresAck: true,
        compression: 'gzip',
        encoding: 'json',
        ...options
      }
    };
  }

  static createQuery(
    topic: string,
    query: string,
    parameters: any,
    source: string,
    destination: string
  ): KMBMessage {
    return {
      id: crypto.randomUUID(),
      timestamp: new Date().toISOString(),
      topic,
      type: MessageType.QUERY,
      source,
      destination,
      payload: {
        query,
        parameters,
        expectsResponse: true,
        timeout: 30000 // 30 seconds
      },
      metadata: {
        priority: 'medium',
        durable: false,
        encrypted: false,
        requiresAck: true,
        compression: 'none',
        encoding: 'json'
      }
    };
  }
}
```

## 🌐 Topic Hierarchies and Management

```typescript
class TopicHierarchyManager {
  private readonly hierarchyTree: TopicTree;
  private readonly wildcardMatcher: WildcardMatcher;
  private readonly subscriptionManager: SubscriptionManager;

  constructor(config: TopicHierarchyConfig) {
    this.hierarchyTree = new TopicTree();
    this.wildcardMatcher = new WildcardMatcher();
    this.subscriptionManager = new SubscriptionManager(config.subscriptions);
  }

  registerTopicHierarchy(hierarchy: TopicHierarchy): void {
    // Build topic tree
    this.hierarchyTree.addHierarchy(hierarchy);
    
    // Register wildcard patterns
    this.wildcardMatcher.addPatterns(hierarchy.wildcardPatterns);
  }

  findMatchingSubscriptions(topic: string): Subscription[] {
    const exactMatches = this.subscriptionManager.getExactMatches(topic);
    const wildcardMatches = this.wildcardMatcher.findMatches(topic);
    
    return [...exactMatches, ...wildcardMatches];
  }

  validateTopicName(topic: string): TopicValidation {
    const segments = topic.split('.');
    
    // Validate segment count
    if (segments.length > 10) {
      return {
        valid: false,
        errors: ['Topic hierarchy too deep (max 10 levels)']
      };
    }

    // Validate segment format
    const invalidSegments = segments.filter(segment => 
      !/^[a-z][a-z0-9_]*$/.test(segment)
    );

    if (invalidSegments.length > 0) {
      return {
        valid: false,
        errors: [`Invalid segment format: ${invalidSegments.join(', ')}`]
      };
    }

    // Check against reserved patterns
    if (this.isReservedTopic(topic)) {
      return {
        valid: false,
        errors: ['Topic name conflicts with reserved pattern']
      };
    }

    return { valid: true };
  }

  private isReservedTopic(topic: string): boolean {
    const reservedPatterns = [
      /^kmb\.system\./,
      /^kmb\.internal\./,
      /^kmb\.debug\./
    ];

    return reservedPatterns.some(pattern => pattern.test(topic));
  }
}

// Example topic hierarchies
const standardTopics = {
  agent: {
    lifecycle: [
      'kmb.agent.lifecycle.start',
      'kmb.agent.lifecycle.stop',
      'kmb.agent.lifecycle.restart',
      'kmb.agent.lifecycle.error'
    ],
    health: [
      'kmb.agent.health.heartbeat',
      'kmb.agent.health.status',
      'kmb.agent.health.metrics'
    ],
    intent: [
      'kmb.agent.intent.create',
      'kmb.agent.intent.update',
      'kmb.agent.intent.complete',
      'kmb.agent.intent.cancel'
    ]
  },
  service: [
    'kmb.service.status',
    'kmb.service.discovery',
    'kmb.service.registration'
  ],
  ui: [
    'kmb.ui.command.button.click',
    'kmb.ui.command.input.change',
    'kmb.ui.notification.show'
  ]
};
```

## 🧠 Advanced Features Implementation

### Message Transform Pipelines

```typescript
class TransformPipeline {
  private readonly transforms: MessageTransform[];
  private readonly logger: TransformLogger;

  constructor(config: TransformConfig) {
    this.transforms = this.loadTransforms(config.transforms);
    this.logger = new TransformLogger(config.logging);
  }

  async process(message: SecuredKMBMessage): Promise<SecuredKMBMessage> {
    let processedMessage = { ...message };

    for (const transform of this.transforms) {
      try {
        if (await transform.shouldApply(processedMessage)) {
          const startTime = Date.now();
          processedMessage = await transform.apply(processedMessage);
          const duration = Date.now() - startTime;

          await this.logger.logTransform({
            transformId: transform.id,
            messageId: message.id,
            duration,
            success: true
          });
        }
      } catch (error) {
        await this.logger.logTransform({
          transformId: transform.id,
          messageId: message.id,
          success: false,
          error: error.message
        });

        // Decide whether to continue or fail
        if (transform.critical) {
          throw new Error(`Critical transform failed: ${transform.id}`);
        }
      }
    }

    return processedMessage;
  }

  private loadTransforms(transformConfigs: TransformConfig[]): MessageTransform[] {
    return transformConfigs.map(config => {
      switch (config.type) {
        case 'logging':
          return new LoggingTransform(config);
        case 'replication':
          return new ReplicationTransform(config);
        case 'mutation':
          return new MutationTransform(config);
        case 'encryption':
          return new EncryptionTransform(config);
        default:
          throw new Error(`Unknown transform type: ${config.type}`);
      }
    });
  }
}

class LoggingTransform implements MessageTransform {
  readonly id = 'logging-transform';
  readonly critical = false;

  constructor(private config: LoggingTransformConfig) {}

  async shouldApply(message: SecuredKMBMessage): Promise<boolean> {
    return this.config.logAllMessages || 
           this.config.logTopics.includes(message.topic) ||
           message.metadata.priority === 'critical';
  }

  async apply(message: SecuredKMBMessage): Promise<SecuredKMBMessage> {
    await this.logMessage(message);
    return message; // Logging doesn't modify the message
  }

  private async logMessage(message: SecuredKMBMessage): Promise<void> {
    const logEntry = {
      messageId: message.id,
      topic: message.topic,
      source: message.source,
      destination: message.destination,
      timestamp: message.timestamp,
      type: message.type,
      priority: message.metadata.priority,
      payloadSize: JSON.stringify(message.payload).length
    };

    await this.config.logger.log(logEntry);
  }
}
```

## Cross-References

- **Related Systems**: [KLP Protocol](./34_klp-kind-link-protocol.md), [API Services](./36_kai-api-socket-services.md)
- **Implementation Guides**: [Device Bootstrap](./35_device-agent-bootstrap.md), [Communication Protocols](./37_agent-communication-protocols.md)
- **Configuration**: [Message Configuration](../current/message-configuration.md), [Communication Settings](../current/communication-settings.md)

## Changelog

- **v2.1.0** (2024-12-28): Complete TypeScript implementation with advanced features and security
- **v2.0.0** (2024-12-27): Enhanced with transform pipelines and topic hierarchy management
- **v1.0.0** (2024-06-20): Initial message bus architecture definition

---

*This document is part of the Kind AI Documentation System - enabling seamless, secure communication across the entire agent ecosystem.* 