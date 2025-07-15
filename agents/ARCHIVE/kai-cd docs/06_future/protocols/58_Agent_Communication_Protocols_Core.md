---
title: "Agent Communication Protocols - Core"
description: "Core communication protocols for agent-to-agent interactions"
type: "protocol"
status: "future"
priority: "high"
last_updated: "2025-01-27"
related_docs: ["agent-communication-protocols-security.md", "federated-mesh-protocols.md"]
implementation_status: "planned"
---

# Agent Communication Protocols - Core

## Agent Context
Core communication protocols enabling structured agent-to-agent interactions with message routing, protocol negotiation, and capability discovery.

## Protocol Architecture

```typescript
interface CommunicationProtocol {
  name: string;
  version: string;
  transport: TransportLayer;
  encoding: EncodingType;
  security: SecurityLayer;
  features: ProtocolFeature[];
}

interface AgentMessage {
  id: string;
  protocol: string;
  version: string;
  source: string; // Source agent kID
  destination: string; // Destination agent kID
  type: MessageType;
  payload: any;
  metadata: MessageMetadata;
  timestamp: string;
  signature?: string;
}

interface MessageMetadata {
  correlationId?: string;
  replyTo?: string;
  priority: 'low' | 'normal' | 'high' | 'urgent';
  ttl?: number; // Time to live in seconds
  encoding: 'json' | 'msgpack' | 'protobuf';
  compression?: 'gzip' | 'brotli';
}

type MessageType = 
  | 'request'
  | 'response'
  | 'notification'
  | 'heartbeat'
  | 'capability_query'
  | 'capability_response'
  | 'delegation'
  | 'error';
```

## Message Router

```typescript
class AgentMessageRouter {
  private routes: Map<string, RouteHandler>;
  private protocols: Map<string, CommunicationProtocol>;
  private connections: Map<string, Connection>;

  async sendMessage(message: AgentMessage): Promise<MessageResult> {
    try {
      // 1. Validate message
      const validation = await this.validateMessage(message);
      if (!validation.valid) {
        return { success: false, error: validation.error };
      }

      // 2. Find route to destination
      const route = await this.findRoute(message.destination);
      if (!route) {
        return { success: false, error: 'No route to destination' };
      }

      // 3. Select appropriate protocol
      const protocol = await this.negotiateProtocol(message.destination);
      
      // 4. Encode and send
      const encodedMessage = await this.encodeMessage(message, protocol);
      await route.send(encodedMessage);

      return { success: true, messageId: message.id };

    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  async receiveMessage(rawMessage: Buffer, connection: Connection): Promise<void> {
    try {
      // 1. Decode message
      const message = await this.decodeMessage(rawMessage, connection.protocol);
      
      // 2. Verify signature if present
      if (message.signature) {
        const signatureValid = await this.verifySignature(message);
        if (!signatureValid) {
          console.warn('Received message with invalid signature');
          return;
        }
      }

      // 3. Route to appropriate handler
      const handler = this.routes.get(message.type);
      if (handler) {
        await handler.handle(message, connection);
      } else {
        console.warn(`No handler for message type: ${message.type}`);
      }

    } catch (error) {
      console.error('Message processing failed:', error);
    }
  }

  private async negotiateProtocol(destinationId: string): Promise<CommunicationProtocol> {
    // Query destination capabilities
    const capabilityQuery: AgentMessage = {
      id: crypto.randomUUID(),
      protocol: 'core',
      version: '1.0',
      source: this.agentId,
      destination: destinationId,
      type: 'capability_query',
      payload: { protocols: Array.from(this.protocols.keys()) },
      metadata: { priority: 'normal', encoding: 'json' },
      timestamp: new Date().toISOString()
    };

    const response = await this.sendAndWaitForResponse(capabilityQuery, 5000);
    
    if (response && response.type === 'capability_response') {
      const supportedProtocols = response.payload.protocols;
      
      // Find best matching protocol
      for (const protocolName of this.getPreferredProtocols()) {
        if (supportedProtocols.includes(protocolName)) {
          return this.protocols.get(protocolName)!;
        }
      }
    }

    // Fallback to basic protocol
    return this.protocols.get('basic')!;
  }
}
```

## Protocol Handlers

```typescript
abstract class ProtocolHandler {
  abstract handle(message: AgentMessage, connection: Connection): Promise<void>;
  
  protected async sendResponse(
    originalMessage: AgentMessage,
    response: any,
    connection: Connection
  ): Promise<void> {
    const responseMessage: AgentMessage = {
      id: crypto.randomUUID(),
      protocol: originalMessage.protocol,
      version: originalMessage.version,
      source: this.agentId,
      destination: originalMessage.source,
      type: 'response',
      payload: response,
      metadata: {
        correlationId: originalMessage.id,
        priority: originalMessage.metadata.priority,
        encoding: originalMessage.metadata.encoding
      },
      timestamp: new Date().toISOString()
    };

    await connection.send(responseMessage);
  }
}

class RequestHandler extends ProtocolHandler {
  async handle(message: AgentMessage, connection: Connection): Promise<void> {
    try {
      const result = await this.processRequest(message.payload);
      await this.sendResponse(message, { success: true, data: result }, connection);
    } catch (error) {
      await this.sendResponse(message, { 
        success: false, 
        error: error.message 
      }, connection);
    }
  }

  private async processRequest(payload: any): Promise<any> {
    // Process the request based on payload type
    switch (payload.action) {
      case 'execute_task':
        return await this.executeTask(payload.task);
      
      case 'query_data':
        return await this.queryData(payload.query);
      
      case 'update_state':
        return await this.updateState(payload.state);
      
      default:
        throw new Error(`Unknown action: ${payload.action}`);
    }
  }
}

class DelegationHandler extends ProtocolHandler {
  async handle(message: AgentMessage, connection: Connection): Promise<void> {
    const delegation = message.payload as DelegationRequest;
    
    // Verify delegation authority
    const authorized = await this.verifyDelegationAuthority(
      message.source,
      delegation
    );

    if (!authorized) {
      await this.sendResponse(message, {
        success: false,
        error: 'Insufficient authority for delegation'
      }, connection);
      return;
    }

    // Accept delegation
    const result = await this.acceptDelegation(delegation);
    await this.sendResponse(message, result, connection);
  }

  private async acceptDelegation(delegation: DelegationRequest): Promise<any> {
    // Create delegation context
    const context = await this.createDelegationContext(delegation);
    
    // Execute delegated task
    const result = await this.executeDelegatedTask(delegation.task, context);
    
    // Record delegation completion
    await this.recordDelegationCompletion(delegation.id, result);
    
    return {
      success: true,
      delegationId: delegation.id,
      result
    };
  }
}
```

## Connection Management

```typescript
class ConnectionManager {
  private connections: Map<string, Connection>;
  private connectionPool: ConnectionPool;

  async establishConnection(
    targetId: string,
    options: ConnectionOptions = {}
  ): Promise<Connection> {
    // Check if connection already exists
    const existing = this.connections.get(targetId);
    if (existing && existing.isActive()) {
      return existing;
    }

    // Create new connection
    const connection = await this.createConnection(targetId, options);
    
    // Perform handshake
    await this.performHandshake(connection);
    
    // Store connection
    this.connections.set(targetId, connection);
    
    return connection;
  }

  private async createConnection(
    targetId: string,
    options: ConnectionOptions
  ): Promise<Connection> {
    // Resolve target address
    const address = await this.resolveAddress(targetId);
    
    // Select transport
    const transport = options.transport || this.selectBestTransport(address);
    
    // Create connection based on transport
    switch (transport) {
      case 'websocket':
        return new WebSocketConnection(address, options);
      
      case 'webrtc':
        return new WebRTCConnection(address, options);
      
      case 'tcp':
        return new TCPConnection(address, options);
      
      default:
        throw new Error(`Unsupported transport: ${transport}`);
    }
  }

  private async performHandshake(connection: Connection): Promise<void> {
    const handshake = {
      agentId: this.agentId,
      protocols: Array.from(this.supportedProtocols.keys()),
      capabilities: this.getCapabilities(),
      timestamp: new Date().toISOString()
    };

    await connection.send(handshake);
    
    const response = await connection.waitForMessage(5000);
    if (!response || !this.validateHandshakeResponse(response)) {
      throw new Error('Handshake failed');
    }

    connection.setRemoteInfo(response);
  }
}
```
