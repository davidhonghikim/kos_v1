---
title: "Agent-to-Agent Protocol"
description: "Universal communication protocol for inter-agent interactions"
type: "protocol"
status: "future"
priority: "high"
last_updated: "2025-01-27"
related_docs: ["agent-communication-protocols-core.md", "agent-swarm-coordination.md"]
implementation_status: "planned"
---

# Agent-to-Agent Protocol (kAIP)

## Agent Context
Universal communication and behavioral protocol enabling standardized inter-agent messaging, intent propagation, context sharing, and secure collaboration across the kAI ecosystem with trust management and audit trails.

## Protocol Architecture

```typescript
interface AgentMessage {
  type: MessageType;
  from: AgentURI;
  to: AgentURI;
  timestamp: number;
  intent: string;
  data: MessageData;
  signature: string;
  trustToken?: string;
  conversationId?: string;
  replyTo?: string;
}

interface MessageData {
  payload: any;
  context?: ContextData;
  metadata?: MessageMetadata;
  attachments?: Attachment[];
}

type MessageType = 
  | 'intent_request'
  | 'status_report'
  | 'context_broadcast'
  | 'handoff_notice'
  | 'failure_signal'
  | 'validation_request'
  | 'consensus_vote'
  | 'capability_query'
  | 'resource_request';

type AgentURI = string; // Format: kAI://agent.category.name
```

## Protocol Stack Implementation

```typescript
class AgentInteractionProtocol {
  private transport: TransportLayer;
  private messageEncoder: MessageEncoder;
  private trustManager: TrustManager;
  private auditLogger: AuditLogger;
  private agentRegistry: AgentRegistry;

  constructor(config: ProtocolConfig) {
    this.transport = this.initializeTransport(config.transport);
    this.messageEncoder = new MessageEncoder(config.encoding);
    this.trustManager = new TrustManager(config.trust);
    this.auditLogger = new AuditLogger(config.audit);
    this.agentRegistry = new AgentRegistry(config.registry);
  }

  async sendMessage(message: AgentMessage): Promise<MessageResult> {
    // Validate message structure
    const validation = await this.validateMessage(message);
    if (!validation.valid) {
      throw new Error(`Invalid message: ${validation.errors.join(', ')}`);
    }

    // Sign message
    const signedMessage = await this.signMessage(message);
    
    // Encode message
    const encodedMessage = await this.messageEncoder.encode(signedMessage);
    
    // Send via transport
    const result = await this.transport.send(message.to, encodedMessage);
    
    // Log to audit trail
    await this.auditLogger.logMessage(signedMessage, result);
    
    return result;
  }

  async receiveMessage(encodedMessage: EncodedMessage): Promise<void> {
    try {
      // Decode message
      const message = await this.messageEncoder.decode(encodedMessage);
      
      // Verify signature
      const signatureValid = await this.verifySignature(message);
      if (!signatureValid) {
        await this.handleInvalidSignature(message);
        return;
      }

      // Check trust level
      const trustCheck = await this.trustManager.verifyTrust(message.from, message.intent);
      if (!trustCheck.authorized) {
        await this.handleUnauthorizedMessage(message, trustCheck.reason);
        return;
      }

      // Process message based on type
      await this.processMessage(message);
      
      // Log successful processing
      await this.auditLogger.logProcessedMessage(message);

    } catch (error) {
      await this.handleMessageError(encodedMessage, error);
    }
  }

  private async processMessage(message: AgentMessage): Promise<void> {
    switch (message.type) {
      case 'intent_request':
        await this.handleIntentRequest(message);
        break;
      
      case 'status_report':
        await this.handleStatusReport(message);
        break;
      
      case 'context_broadcast':
        await this.handleContextBroadcast(message);
        break;
      
      case 'handoff_notice':
        await this.handleHandoffNotice(message);
        break;
      
      case 'failure_signal':
        await this.handleFailureSignal(message);
        break;
      
      case 'validation_request':
        await this.handleValidationRequest(message);
        break;
      
      case 'consensus_vote':
        await this.handleConsensusVote(message);
        break;
      
      default:
        console.warn(`Unknown message type: ${message.type}`);
    }
  }

  private async handleIntentRequest(message: AgentMessage): Promise<void> {
    const intentHandler = await this.getIntentHandler(message.intent);
    
    if (!intentHandler) {
      await this.sendResponse(message, {
        success: false,
        error: `Unknown intent: ${message.intent}`,
        supportedIntents: await this.getSupportedIntents()
      });
      return;
    }

    try {
      const result = await intentHandler.execute(message.data, message.from);
      
      await this.sendResponse(message, {
        success: true,
        result,
        executedBy: this.getLocalAgentURI(),
        executedAt: new Date().toISOString()
      });
    } catch (error) {
      await this.sendResponse(message, {
        success: false,
        error: error.message,
        executedBy: this.getLocalAgentURI(),
        executedAt: new Date().toISOString()
      });
    }
  }

  private async handleHandoffNotice(message: AgentMessage): Promise<void> {
    const handoffData = message.data.payload as HandoffData;
    
    // Check if we can accept the handoff
    const canAccept = await this.canAcceptHandoff(handoffData);
    
    if (canAccept.acceptable) {
      // Request context if needed
      if (!handoffData.context || handoffData.context.incomplete) {
        await this.requestContext(message.from, handoffData.taskId);
      }
      
      // Accept handoff
      await this.acceptHandoff(handoffData);
      
      // Confirm acceptance
      await this.sendResponse(message, {
        success: true,
        accepted: true,
        estimatedCompletion: canAccept.estimatedCompletion
      });
    } else {
      await this.sendResponse(message, {
        success: false,
        accepted: false,
        reason: canAccept.reason,
        alternativeSuggestions: canAccept.alternatives
      });
    }
  }

  private async signMessage(message: AgentMessage): Promise<AgentMessage> {
    const messageHash = await this.calculateMessageHash(message);
    const signature = await this.trustManager.signHash(messageHash);
    
    return {
      ...message,
      signature
    };
  }

  private async verifySignature(message: AgentMessage): Promise<boolean> {
    const senderPublicKey = await this.agentRegistry.getPublicKey(message.from);
    if (!senderPublicKey) {
      console.warn(`No public key found for agent: ${message.from}`);
      return false;
    }

    const messageHash = await this.calculateMessageHash({
      ...message,
      signature: undefined // Exclude signature from hash calculation
    });

    return await this.trustManager.verifySignature(
      messageHash,
      message.signature,
      senderPublicKey
    );
  }
}
```

## Transport Layer Abstraction

```typescript
abstract class TransportLayer {
  abstract async send(destination: AgentURI, message: EncodedMessage): Promise<MessageResult>;
  abstract async listen(callback: MessageCallback): Promise<void>;
  abstract async close(): Promise<void>;
}

class LocalTransport extends TransportLayer {
  private messageQueue: Map<AgentURI, EncodedMessage[]>;
  private callbacks: Map<AgentURI, MessageCallback>;

  async send(destination: AgentURI, message: EncodedMessage): Promise<MessageResult> {
    const queue = this.messageQueue.get(destination) || [];
    queue.push(message);
    this.messageQueue.set(destination, queue);
    
    // Immediately deliver to callback if available
    const callback = this.callbacks.get(destination);
    if (callback) {
      try {
        await callback(message);
        return { success: true, delivered: true };
      } catch (error) {
        return { success: false, error: error.message };
      }
    }
    
    return { success: true, queued: true };
  }

  async listen(callback: MessageCallback): Promise<void> {
    const agentURI = this.getLocalAgentURI();
    this.callbacks.set(agentURI, callback);
    
    // Process any queued messages
    const queue = this.messageQueue.get(agentURI) || [];
    for (const message of queue) {
      try {
        await callback(message);
      } catch (error) {
        console.error('Error processing queued message:', error);
      }
    }
    
    // Clear queue
    this.messageQueue.delete(agentURI);
  }
}

class NetworkTransport extends TransportLayer {
  private webSocket: WebSocket;
  private grpcClient: GRPCClient;
  private mqttClient: MQTTClient;

  async send(destination: AgentURI, message: EncodedMessage): Promise<MessageResult> {
    const protocol = this.getProtocolForDestination(destination);
    
    switch (protocol) {
      case 'websocket':
        return await this.sendViaWebSocket(destination, message);
      
      case 'grpc':
        return await this.sendViaGRPC(destination, message);
      
      case 'mqtt':
        return await this.sendViaMQTT(destination, message);
      
      default:
        throw new Error(`Unsupported protocol for destination: ${destination}`);
    }
  }

  private async sendViaWebSocket(
    destination: AgentURI,
    message: EncodedMessage
  ): Promise<MessageResult> {
    if (!this.webSocket || this.webSocket.readyState !== WebSocket.OPEN) {
      await this.establishWebSocketConnection(destination);
    }

    return new Promise((resolve) => {
      const messageId = crypto.randomUUID();
      const envelope = {
        id: messageId,
        destination,
        message,
        timestamp: Date.now()
      };

      const timeout = setTimeout(() => {
        resolve({ success: false, error: 'Message timeout' });
      }, 30000);

      this.webSocket.send(JSON.stringify(envelope));
      
      // Wait for acknowledgment
      const ackHandler = (event: MessageEvent) => {
        const ack = JSON.parse(event.data);
        if (ack.type === 'ack' && ack.messageId === messageId) {
          clearTimeout(timeout);
          this.webSocket.removeEventListener('message', ackHandler);
          resolve({ success: true, delivered: true });
        }
      };

      this.webSocket.addEventListener('message', ackHandler);
    });
  }
}
```

## Trust and Security Framework

```typescript
class TrustManager {
  private keyPairs: Map<AgentURI, CryptoKeyPair>;
  private trustLevels: Map<AgentURI, TrustLevel>;
  private trustTokens: Map<string, TrustToken>;

  async verifyTrust(
    senderURI: AgentURI,
    intent: string
  ): Promise<TrustVerificationResult> {
    const trustLevel = this.trustLevels.get(senderURI);
    if (!trustLevel) {
      return {
        authorized: false,
        reason: 'Unknown agent - no trust level assigned'
      };
    }

    const requiredLevel = await this.getRequiredTrustLevel(intent);
    
    if (trustLevel.level < requiredLevel) {
      return {
        authorized: false,
        reason: `Insufficient trust level: ${trustLevel.level} < ${requiredLevel}`
      };
    }

    // Check for specific intent permissions
    const intentPermissions = await this.getIntentPermissions(senderURI, intent);
    if (!intentPermissions.allowed) {
      return {
        authorized: false,
        reason: `Intent not permitted: ${intent}`
      };
    }

    return {
      authorized: true,
      trustLevel: trustLevel.level,
      permissions: intentPermissions.permissions
    };
  }

  async generateTrustToken(
    agentURI: AgentURI,
    permissions: string[],
    duration: number = 3600000 // 1 hour default
  ): Promise<TrustToken> {
    const token: TrustToken = {
      id: crypto.randomUUID(),
      agentURI,
      permissions,
      issued: Date.now(),
      expires: Date.now() + duration,
      signature: ''
    };

    // Sign token
    const tokenHash = await this.calculateTokenHash(token);
    token.signature = await this.signHash(tokenHash);
    
    this.trustTokens.set(token.id, token);
    return token;
  }

  async validateTrustToken(tokenId: string): Promise<TokenValidationResult> {
    const token = this.trustTokens.get(tokenId);
    if (!token) {
      return { valid: false, reason: 'Token not found' };
    }

    if (Date.now() > token.expires) {
      return { valid: false, reason: 'Token expired' };
    }

    // Verify signature
    const tokenHash = await this.calculateTokenHash({
      ...token,
      signature: ''
    });
    
    const signatureValid = await this.verifyTokenSignature(
      tokenHash,
      token.signature,
      token.agentURI
    );

    if (!signatureValid) {
      return { valid: false, reason: 'Invalid token signature' };
    }

    return {
      valid: true,
      token,
      remainingTime: token.expires - Date.now()
    };
  }
}
```

## Agent Registry and Discovery

```typescript
class AgentRegistry {
  private agents: Map<AgentURI, AgentRegistration>;
  private capabilities: Map<string, AgentURI[]>;
  private publicKeys: Map<AgentURI, CryptoKey>;

  async registerAgent(registration: AgentRegistration): Promise<void> {
    const agentURI = registration.uri;
    
    // Validate registration
    const validation = await this.validateRegistration(registration);
    if (!validation.valid) {
      throw new Error(`Invalid registration: ${validation.errors.join(', ')}`);
    }

    // Store registration
    this.agents.set(agentURI, registration);
    
    // Index capabilities
    for (const capability of registration.capabilities) {
      const capabilityAgents = this.capabilities.get(capability) || [];
      capabilityAgents.push(agentURI);
      this.capabilities.set(capability, capabilityAgents);
    }

    // Store public key
    this.publicKeys.set(agentURI, registration.publicKey);
    
    console.log(`Agent registered: ${agentURI}`);
  }

  async findAgentsByCapability(capability: string): Promise<AgentRegistration[]> {
    const agentURIs = this.capabilities.get(capability) || [];
    const agents: AgentRegistration[] = [];
    
    for (const uri of agentURIs) {
      const agent = this.agents.get(uri);
      if (agent && agent.status === 'active') {
        agents.push(agent);
      }
    }

    return agents.sort((a, b) => b.reputation - a.reputation);
  }

  async getAgentManifest(agentURI: AgentURI): Promise<AgentManifest | null> {
    const registration = this.agents.get(agentURI);
    return registration ? registration.manifest : null;
  }

  async updateAgentStatus(
    agentURI: AgentURI,
    status: AgentStatus,
    metadata?: any
  ): Promise<void> {
    const registration = this.agents.get(agentURI);
    if (registration) {
      registration.status = status;
      registration.lastSeen = new Date().toISOString();
      if (metadata) {
        registration.metadata = { ...registration.metadata, ...metadata };
      }
    }
  }
}
```
