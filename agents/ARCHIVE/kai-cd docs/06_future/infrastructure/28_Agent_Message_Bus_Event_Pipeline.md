---
title: "Agent Message Bus & Event Pipeline (KMB)"
version: "1.0.0"
last_updated: "2024-12-19"
status: "Specification"
type: "Infrastructure Protocol"
tags: ["messaging", "event-driven", "distributed-systems", "real-time"]
related_files: 
  - "29_kind-link-protocol-specification.md"
  - "30_device-agent-bootstrap-protocol.md"
  - "31_kai-api-socket-services.md"
  - "32_agent-communication-protocols.md"
---

# Agent Message Bus & Event Pipeline (KMB)

## Agent Context

**Primary Function**: Decentralized, modular, and extensible system for event communication, state propagation, service messaging, and task dispatch across all agents and system modules.

**Integration Points**: 
- Core communication backbone for all kAI agents
- Real-time event processing for kOS system UI
- Message routing for distributed agent coordination
- Event sourcing for audit and replay capabilities

**Dependencies**: Redis Streams, PostgreSQL, FastAPI, WebSocket infrastructure, cryptographic signing services

## Overview

The **Kind Message Bus (KMB)** serves as the core architectural component of the kAI/kOS ecosystem, providing a decentralized, modular, and extensible system for event communication, state propagation, service messaging, and task dispatch across all agents and system modules.

KMB supports plug-and-play message handlers, durable and ephemeral messages, topic subscriptions, routing layers, and local or distributed deployment. It serves as the real-time nervous system of kAI, enabling seamless communication between agents, services, and user interfaces.

## Core Objectives

- **Decentralized Communication**: Enable agents, services, and users to publish/subscribe to structured events
- **Security & Traceability**: Provide a secure, traceable, low-latency communication layer
- **Extensibility**: Allow for modular interceptors, plugins, and custom protocol handlers
- **Scalability**: Support both centralized (single-node) and federated multi-node deployment

## Architecture Components

### 1. KMB Broker

The central message routing engine that handles message delivery, durability, and topic management.

```typescript
interface KMBBroker {
  // Core routing functionality
  routeMessage(message: KMBMessage): Promise<RoutingResult>;
  
  // Topic management
  createTopic(topic: TopicConfig): Promise<void>;
  deleteTopic(topicName: string): Promise<void>;
  
  // Subscription management
  subscribe(subscription: SubscriptionConfig): Promise<string>;
  unsubscribe(subscriptionId: string): Promise<void>;
  
  // Durability controls
  enableDurability(topicName: string): Promise<void>;
  configureDurability(config: DurabilityConfig): Promise<void>;
}

interface TopicConfig {
  name: string;
  schema: JSONSchema;
  durability: 'ephemeral' | 'durable' | 'persistent';
  retention: {
    maxAge: number; // seconds
    maxMessages: number;
  };
  accessControl: {
    publishers: string[];
    subscribers: string[];
  };
}

interface DurabilityConfig {
  backend: 'redis' | 'postgresql' | 'kafka' | 'nats';
  replication: {
    enabled: boolean;
    factor: number;
  };
  compression: 'none' | 'gzip' | 'brotli';
}
```

### 2. KMB Client SDKs

Lightweight libraries for agents, applications, and services to connect to the message bus.

```typescript
class KMBClient {
  private connection: WebSocket | HTTPConnection;
  private subscriptions: Map<string, MessageHandler>;
  private middleware: MiddlewareChain;

  constructor(config: KMBClientConfig) {
    this.connection = this.createConnection(config);
    this.subscriptions = new Map();
    this.middleware = new MiddlewareChain();
  }

  // Publishing interface
  async publish(topic: string, message: unknown, metadata?: MessageMetadata): Promise<string> {
    const kmbMessage: KMBMessage = {
      id: generateUUID(),
      timestamp: new Date().toISOString(),
      topic,
      payload: message,
      metadata: {
        ...metadata,
        auth: await this.getAuthContext(),
        trace_id: metadata?.trace_id || generateTraceId()
      }
    };

    // Apply middleware transformations
    const processedMessage = await this.middleware.process(kmbMessage);
    
    return this.connection.send(processedMessage);
  }

  // Subscription interface
  async subscribe(topic: string, handler: MessageHandler): Promise<string> {
    const subscriptionId = generateUUID();
    this.subscriptions.set(subscriptionId, handler);
    
    await this.connection.subscribe(topic, subscriptionId);
    return subscriptionId;
  }

  // Acknowledgment interface
  async ack(messageId: string): Promise<void> {
    await this.connection.ack(messageId);
  }

  // Middleware support
  use(middleware: Middleware): void {
    this.middleware.add(middleware);
  }
}

interface KMBClientConfig {
  brokerUrl: string;
  authentication: {
    type: 'jwt' | 'apikey' | 'certificate';
    credentials: Record<string, string>;
  };
  transport: {
    type: 'websocket' | 'http' | 'grpc';
    options: Record<string, unknown>;
  };
  retry: {
    maxAttempts: number;
    backoffStrategy: 'linear' | 'exponential';
  };
}

type MessageHandler = (message: KMBMessage) => Promise<void>;

interface Middleware {
  process(message: KMBMessage): Promise<KMBMessage>;
}
```

### 3. Topic Registry

Centralized registry for topic schemas, versioning, and validation contracts.

```typescript
class TopicRegistry {
  private schemas: Map<string, TopicSchema>;
  private versions: Map<string, string[]>;

  async registerTopic(topic: string, schema: TopicSchema): Promise<void> {
    // Validate schema compatibility
    await this.validateSchemaCompatibility(topic, schema);
    
    this.schemas.set(topic, schema);
    this.updateVersionHistory(topic, schema.version);
  }

  async validateMessage(topic: string, message: unknown): Promise<ValidationResult> {
    const schema = this.schemas.get(topic);
    if (!schema) {
      throw new Error(`Topic ${topic} not registered`);
    }

    return this.validateAgainstSchema(message, schema);
  }

  async getTopicSchema(topic: string, version?: string): Promise<TopicSchema> {
    const schema = this.schemas.get(topic);
    if (!schema) {
      throw new Error(`Topic ${topic} not found`);
    }

    if (version && schema.version !== version) {
      return this.getHistoricalSchema(topic, version);
    }

    return schema;
  }
}

interface TopicSchema {
  name: string;
  version: string;
  description: string;
  schema: JSONSchema;
  compatibility: 'backward' | 'forward' | 'full' | 'none';
  examples: unknown[];
}
```

### 4. Security Layer

Comprehensive security implementation with authentication, authorization, and encryption.

```typescript
class KMBSecurityLayer {
  private jwtValidator: JWTValidator;
  private accessControl: AccessControlEngine;
  private encryptionService: EncryptionService;

  async authenticateClient(token: string): Promise<AuthContext> {
    const payload = await this.jwtValidator.validate(token);
    return {
      clientId: payload.sub,
      permissions: payload.permissions,
      expiresAt: new Date(payload.exp * 1000)
    };
  }

  async authorizeTopicAccess(
    context: AuthContext, 
    topic: string, 
    operation: 'publish' | 'subscribe'
  ): Promise<boolean> {
    return this.accessControl.checkPermission(context, topic, operation);
  }

  async signMessage(message: KMBMessage, privateKey: string): Promise<string> {
    const messageHash = await this.hashMessage(message);
    return this.encryptionService.sign(messageHash, privateKey);
  }

  async verifySignature(message: KMBMessage, signature: string, publicKey: string): Promise<boolean> {
    const messageHash = await this.hashMessage(message);
    return this.encryptionService.verify(messageHash, signature, publicKey);
  }

  private async hashMessage(message: KMBMessage): Promise<string> {
    const canonical = JSON.stringify(message, Object.keys(message).sort());
    return this.encryptionService.hash(canonical, 'sha256');
  }
}

interface AuthContext {
  clientId: string;
  permissions: string[];
  expiresAt: Date;
}
```

## Message Format Specification

### Core Message Structure

```typescript
interface KMBMessage {
  id: string; // UUID v4
  timestamp: string; // ISO 8601
  topic: string; // Hierarchical topic name
  payload: unknown; // Message content
  metadata: MessageMetadata;
}

interface MessageMetadata {
  trace_id?: string;
  correlation_id?: string;
  reply_to?: string;
  auth: AuthMetadata;
  headers?: Record<string, string>;
  priority?: 'low' | 'normal' | 'high' | 'critical';
  ttl?: number; // Time to live in seconds
}

interface AuthMetadata {
  issuer: string;
  client_id: string;
  signature?: string;
  timestamp: string;
}
```

### Message Types

```typescript
enum MessageType {
  EVENT = 'event',         // One-way broadcast (fire-and-forget)
  COMMAND = 'command',     // Request for execution with ACK/ERROR/DONE
  QUERY = 'query',         // Request for data with response
  TRANSACTIONAL = 'transactional' // Multi-phase with rollback support
}

interface CommandMessage extends KMBMessage {
  type: MessageType.COMMAND;
  payload: {
    command: string;
    parameters: Record<string, unknown>;
    timeout?: number;
    retries?: number;
  };
}

interface QueryMessage extends KMBMessage {
  type: MessageType.QUERY;
  payload: {
    query: string;
    parameters: Record<string, unknown>;
    responseFormat?: 'json' | 'binary' | 'stream';
  };
}

interface TransactionalMessage extends KMBMessage {
  type: MessageType.TRANSACTIONAL;
  payload: {
    transactionId: string;
    phase: 'prepare' | 'commit' | 'rollback';
    operations: TransactionOperation[];
  };
}

interface TransactionOperation {
  type: string;
  target: string;
  parameters: Record<string, unknown>;
}
```

## Topic Hierarchy & Routing

### Hierarchical Naming Convention

Topics follow hierarchical namespacing conventions:

```
kmb.agent.lifecycle
kmb.agent.error
kmb.agent.intent.create
kmb.agent.intent.complete
kmb.service.status
kmb.ui.command.button.click
```

Supports:
- `*` for single segment wildcard
- `#` for recursive wildcard

```typescript
class TopicRouter {
  private subscriptions: Map<string, Set<string>>;
  private wildcardSubscriptions: Map<string, Set<string>>;

  // Route message to appropriate subscribers
  async routeMessage(message: KMBMessage): Promise<string[]> {
    const topic = message.topic;
    const subscribers = new Set<string>();

    // Direct topic matches
    const directSubs = this.subscriptions.get(topic);
    if (directSubs) {
      directSubs.forEach(sub => subscribers.add(sub));
    }

    // Wildcard matches
    const wildcardMatches = this.findWildcardMatches(topic);
    wildcardMatches.forEach(sub => subscribers.add(sub));

    return Array.from(subscribers);
  }

  private findWildcardMatches(topic: string): string[] {
    const parts = topic.split('.');
    const matches: string[] = [];

    // Single segment wildcard (*)
    for (let i = 0; i < parts.length; i++) {
      const pattern = [...parts];
      pattern[i] = '*';
      const wildcardTopic = pattern.join('.');
      
      const subs = this.wildcardSubscriptions.get(wildcardTopic);
      if (subs) {
        matches.push(...subs);
      }
    }

    return matches;
  }
}
```

## Advanced Features

### 1. Message Transform Pipelines

```typescript
class MessageTransformPipeline {
  private transforms: Transform[];

  constructor() {
    this.transforms = [];
  }

  addTransform(transform: Transform): void {
    this.transforms.push(transform);
  }

  async process(message: KMBMessage): Promise<KMBMessage> {
    let result = message;
    
    for (const transform of this.transforms) {
      result = await transform.apply(result);
    }
    
    return result;
  }
}

interface Transform {
  name: string;
  apply(message: KMBMessage): Promise<KMBMessage>;
}

class LoggingTransform implements Transform {
  name = 'logging';
  
  async apply(message: KMBMessage): Promise<KMBMessage> {
    console.log(`[KMB] Processing message ${message.id} on topic ${message.topic}`);
    return message;
  }
}

class EncryptionTransform implements Transform {
  name = 'encryption';
  
  constructor(private encryptionKey: string) {}
  
  async apply(message: KMBMessage): Promise<KMBMessage> {
    const encrypted = await this.encrypt(JSON.stringify(message.payload));
    return {
      ...message,
      payload: { encrypted: true, data: encrypted }
    };
  }
  
  private async encrypt(data: string): Promise<string> {
    // Implement encryption logic
    return Buffer.from(data).toString('base64');
  }
}
```

### 2. Dead Letter Queue & Retry Logic

```typescript
class DeadLetterQueue {
  private dlqTopic = 'kmb.system.dlq';
  private maxRetries = 3;
  private retryDelays = [1000, 5000, 15000]; // milliseconds

  async handleFailedMessage(
    message: KMBMessage, 
    error: Error, 
    attempt: number
  ): Promise<void> {
    if (attempt < this.maxRetries) {
      // Schedule retry
      await this.scheduleRetry(message, attempt);
    } else {
      // Send to dead letter queue
      await this.sendToDLQ(message, error);
    }
  }

  private async scheduleRetry(message: KMBMessage, attempt: number): Promise<void> {
    const delay = this.retryDelays[attempt - 1] || 30000;
    
    setTimeout(async () => {
      try {
        await this.reprocessMessage(message);
      } catch (error) {
        await this.handleFailedMessage(message, error as Error, attempt + 1);
      }
    }, delay);
  }

  private async sendToDLQ(message: KMBMessage, error: Error): Promise<void> {
    const dlqMessage: KMBMessage = {
      id: generateUUID(),
      timestamp: new Date().toISOString(),
      topic: this.dlqTopic,
      payload: {
        originalMessage: message,
        error: {
          message: error.message,
          stack: error.stack,
          timestamp: new Date().toISOString()
        }
      },
      metadata: {
        auth: message.metadata.auth,
        trace_id: message.metadata.trace_id
      }
    };

    // Send to DLQ topic for manual inspection
    await this.publishToDLQ(dlqMessage);
  }
}
```

### 3. Message Replay & Audit

```typescript
class MessageReplayService {
  private eventStore: EventStore;

  constructor(eventStore: EventStore) {
    this.eventStore = eventStore;
  }

  async replayMessages(
    topic: string, 
    fromTimestamp: Date, 
    toTimestamp: Date
  ): Promise<KMBMessage[]> {
    const messages = await this.eventStore.getMessages({
      topic,
      fromTimestamp,
      toTimestamp
    });

    return messages.map(msg => this.deserializeMessage(msg));
  }

  async createSnapshot(topic: string): Promise<string> {
    const messages = await this.eventStore.getAllMessages(topic);
    const snapshot = {
      topic,
      timestamp: new Date().toISOString(),
      messageCount: messages.length,
      messages
    };

    const snapshotId = generateUUID();
    await this.eventStore.saveSnapshot(snapshotId, snapshot);
    
    return snapshotId;
  }

  async restoreFromSnapshot(snapshotId: string): Promise<void> {
    const snapshot = await this.eventStore.getSnapshot(snapshotId);
    
    for (const message of snapshot.messages) {
      await this.replayMessage(message);
    }
  }
}
```

## Configuration & Deployment

### FastAPI + Redis Configuration

```yaml
kmb:
  broker:
    backend: redis
    redis_url: redis://localhost:6379/0
    connection_pool:
      max_connections: 100
      retry_on_timeout: true
  
  durability:
    enabled: true
    backend: postgresql
    database_url: postgresql://user:pass@localhost/kmb
    retention_policy:
      default_ttl: 86400  # 24 hours
      max_message_size: 1048576  # 1MB
  
  security:
    tls:
      enabled: true
      cert_file: /etc/kmb/tls.crt
      key_file: /etc/kmb/tls.key
    
    authentication:
      jwt:
        secret_key: ${KMB_JWT_SECRET}
        algorithm: HS256
        token_ttl: 3600
      
      topic_acl:
        enabled: true
        default_policy: deny
        rules_file: /etc/kmb/acl.yaml
  
  monitoring:
    metrics:
      enabled: true
      prometheus_port: 9090
    
    logging:
      level: info
      format: json
      output: /var/log/kmb/kmb.log
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
COPY config/ ./config/

EXPOSE 8080 9090

CMD ["python", "-m", "src.kmb.server", "--config", "config/kmb.yaml"]
```

## Integration Points

- kAI Agents use KMB to send/receive all messages
- kOS System UI reacts to KMB events
- Vector stores listen for `vector.upsert`
- kVault publishes `vault.secret.accessed`
- Prompts and workflows emitted via `prompt.issued`, `workflow.started`

## Future Extensions

- Federation across multiple kOS devices or agents
- WebRTC or Reticulum-compatible transports
- CRDT-based sync messages for offline collaboration
- Integration with KindLink Protocol (KLP)

## Related Documentation

- **[Kind Link Protocol Specification](29_kind-link-protocol-specification.md)** - Core communication protocol
- **[Device Agent Bootstrap Protocol](30_device-agent-bootstrap-protocol.md)** - Agent initialization procedures
- **[kAI API & Socket Services](31_kai-api-socket-services.md)** - REST and WebSocket APIs
- **[Agent Communication Protocols](32_agent-communication-protocols.md)** - Inter-agent messaging standards

## Implementation Status

- ✅ Core message format specification
- ✅ TypeScript client SDK interfaces
- ✅ Security layer design
- ✅ Topic registry architecture
- 🔄 FastAPI broker implementation
- 🔄 Redis/PostgreSQL backend integration
- ⏳ Federation protocol implementation
- ⏳ CRDT synchronization features 