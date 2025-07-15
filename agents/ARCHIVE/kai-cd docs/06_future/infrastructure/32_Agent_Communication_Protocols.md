---
title: "Agent Communication Protocols (kLink/KLP)"
version: "1.0.0"
last_updated: "2024-12-19"
status: "Specification"
type: "Communication Protocol"
tags: ["communication", "agents", "protocols", "trust", "federation"]
related_files: 
  - "28_agent-message-bus-event-pipeline.md"
  - "29_kind-link-protocol-specification.md"
  - "30_device-agent-bootstrap-protocol.md"
  - "31_kai-api-socket-services.md"
---

# Agent Communication Protocols (kLink/KLP)

## Agent Context

**Primary Function**: Unified communication layer providing peer-to-peer messaging, real-time federation relays, permissioned syncing, and blockchain-aware message trails across agents in the Kind ecosystem.

**Integration Points**: 
- Direct agent-to-agent communication
- Cross-host federation and relay systems
- Trust graph management and reputation scoring
- Message validation and governance enforcement
- Integration with kAI, kOS, and kHub systems

**Dependencies**: Ed25519 cryptography, KLP protocol stack, transport adapters, trust management, message validation

## Overview

The `kLink` Protocol, also known as **KLP (Kind Link Protocol)**, provides a unified communication layer across agents in the Kind ecosystem. It supports peer-to-peer messaging, real-time federation relays, permissioned syncing, and blockchain-aware message trails.

This protocol defines kLink roles, message formats, transport mechanisms, trust validation strategies, decentralized agent synchronization, and comprehensive integration with kAI, kOS, and kHub systems.

## Protocol Identity & Transport

### Agent Identity System

```typescript
class AgentIdentity {
  private keyPair: Ed25519KeyPair;
  private uuid: string;
  private did?: string;

  constructor(keyPair?: Ed25519KeyPair) {
    this.keyPair = keyPair || this.generateKeyPair();
    this.uuid = this.generateUUIDv7();
  }

  getIdentifier(): string {
    return `agent:${this.uuid}`;
  }

  getFullIdentifier(): string {
    const publicKeyHash = this.hashPublicKey();
    return `agent:kai-${publicKeyHash}`;
  }

  async signMessage(message: string): Promise<string> {
    return this.keyPair.sign(message);
  }

  async verifySignature(message: string, signature: string, publicKey: string): Promise<boolean> {
    return Ed25519.verify(message, signature, publicKey);
  }

  getPublicKey(): string {
    return this.keyPair.publicKey;
  }

  private generateUUIDv7(): string {
    // UUID v7 implementation with timestamp
    const timestamp = Date.now();
    return `${timestamp.toString(16)}-${crypto.randomUUID().slice(9)}`;
  }

  private hashPublicKey(): string {
    return crypto.createHash('sha256')
      .update(this.keyPair.publicKey)
      .digest('hex')
      .substring(0, 8);
  }
}
```

### Transport Layer Implementation

```typescript
interface TransportLayer {
  name: string;
  priority: number;
  reliability: 'high' | 'medium' | 'low';
  latency: 'low' | 'medium' | 'high';
  bandwidth: 'high' | 'medium' | 'low';
}

class TransportManager {
  private transports: Map<string, TransportAdapter>;
  private activeConnections: Map<string, Connection>;

  constructor() {
    this.transports = new Map();
    this.activeConnections = new Map();
    this.initializeTransports();
  }

  private initializeTransports(): void {
    // Core mesh transports
    this.registerTransport(new ReticuumTransport());
    this.registerTransport(new LoRaTransport());
    this.registerTransport(new TCPTransport());
    
    // Federation transports
    this.registerTransport(new GRPCOverQUICTransport());
    this.registerTransport(new WebSocketTransport());
    
    // Edge RPC transports
    this.registerTransport(new HTTPSTransport());
    this.registerTransport(new BluetoothLETransport());
    this.registerTransport(new WebRTCTransport());
  }

  async selectOptimalTransport(destination: string, requirements: TransportRequirements): Promise<TransportAdapter> {
    const availableTransports = Array.from(this.transports.values())
      .filter(transport => this.meetsRequirements(transport, requirements))
      .sort((a, b) => this.calculateScore(b, requirements) - this.calculateScore(a, requirements));

    if (availableTransports.length === 0) {
      throw new Error('No suitable transport available');
    }

    return availableTransports[0];
  }

  private meetsRequirements(transport: TransportAdapter, requirements: TransportRequirements): boolean {
    return transport.capabilities.includes(requirements.reliability) &&
           transport.maxLatency <= requirements.maxLatency &&
           transport.minBandwidth >= requirements.minBandwidth;
  }

  private calculateScore(transport: TransportAdapter, requirements: TransportRequirements): number {
    let score = 0;
    
    // Reliability scoring
    if (transport.reliability === requirements.reliability) score += 40;
    else if (transport.reliability === 'high') score += 30;
    
    // Latency scoring
    if (transport.latency === 'low') score += 30;
    else if (transport.latency === 'medium') score += 20;
    
    // Bandwidth scoring
    if (transport.bandwidth === 'high') score += 20;
    else if (transport.bandwidth === 'medium') score += 10;
    
    // Priority bonus
    score += transport.priority;
    
    return score;
  }
}

interface TransportRequirements {
  reliability: 'high' | 'medium' | 'low';
  maxLatency: number; // milliseconds
  minBandwidth: number; // kbps
  encrypted: boolean;
  authenticated: boolean;
}

const TRANSPORT_LAYERS: Record<string, TransportLayer> = {
  CORE_MESH: {
    name: 'Core Mesh',
    priority: 90,
    reliability: 'high',
    latency: 'low',
    bandwidth: 'medium'
  },
  FEDERATION: {
    name: 'Federation',
    priority: 80,
    reliability: 'high',
    latency: 'medium',
    bandwidth: 'high'
  },
  EDGE_RPC: {
    name: 'Edge RPC',
    priority: 70,
    reliability: 'medium',
    latency: 'low',
    bandwidth: 'low'
  }
};
```

## Message Format & Types

```typescript
interface KLinkMessage {
  id: string;                    // Message identifier
  from: string;                  // Source agent identifier
  to: string;                    // Destination agent identifier
  timestamp: number;             // Unix timestamp
  type: MessageType;             // Message type
  payload: MessagePayload;       // Message content
  signature: string;             // Ed25519 signature
  nonce: string;                 // Random nonce for replay protection
  hash: string;                  // SHA3-512 message hash
  reply_to?: string;             // Optional reply-to message ID
}

enum MessageType {
  AGENT_PING = 'agent.ping',
  AGENT_PONG = 'agent.pong',
  TASK_CREATE = 'task.create',
  TASK_UPDATE = 'task.update',
  TASK_CANCEL = 'task.cancel',
  STATUS_QUERY = 'status.query',
  STATUS_REPLY = 'status.reply',
  FILE_OFFER = 'file.offer',
  FILE_ACCEPT = 'file.accept',
  FILE_REJECT = 'file.reject',
  CAPABILITY_ADVERTISE = 'capability.advertise',
  CAPABILITY_REQUEST = 'capability.request',
  TRUST_REQUEST = 'trust.request',
  TRUST_GRANT = 'trust.grant',
  TRUST_REVOKE = 'trust.revoke'
}

interface MessagePayload {
  data: unknown;
  metadata?: PayloadMetadata;
}

interface PayloadMetadata {
  priority?: 'low' | 'normal' | 'high' | 'critical';
  ttl?: number;
  encryption?: EncryptionInfo;
  compression?: CompressionInfo;
}

class MessageFactory {
  private identity: AgentIdentity;

  constructor(identity: AgentIdentity) {
    this.identity = identity;
  }

  async createMessage(
    to: string,
    type: MessageType,
    payload: unknown,
    options?: MessageOptions
  ): Promise<KLinkMessage> {
    const message: KLinkMessage = {
      id: `msg-${crypto.randomUUID()}`,
      from: this.identity.getFullIdentifier(),
      to,
      timestamp: Date.now(),
      type,
      payload: { data: payload, metadata: options?.metadata },
      signature: '',
      nonce: crypto.randomBytes(16).toString('base64'),
      hash: '',
      reply_to: options?.replyTo
    };

    // Calculate hash
    message.hash = await this.calculateMessageHash(message);
    
    // Sign message
    message.signature = await this.identity.signMessage(message.hash);

    return message;
  }

  async verifyMessage(message: KLinkMessage, senderPublicKey: string): Promise<boolean> {
    // Verify hash
    const calculatedHash = await this.calculateMessageHash({
      ...message,
      signature: '',
      hash: ''
    });

    if (calculatedHash !== message.hash) {
      return false;
    }

    // Verify signature
    return this.identity.verifySignature(message.hash, message.signature, senderPublicKey);
  }

  private async calculateMessageHash(message: Partial<KLinkMessage>): Promise<string> {
    const hashContent = {
      id: message.id,
      from: message.from,
      to: message.to,
      timestamp: message.timestamp,
      type: message.type,
      payload: message.payload,
      nonce: message.nonce
    };

    const canonical = JSON.stringify(hashContent, Object.keys(hashContent).sort());
    return crypto.createHash('sha3-512').update(canonical).digest('hex');
  }
}

interface MessageOptions {
  replyTo?: string;
  metadata?: PayloadMetadata;
}
```

## Trust Management System

```typescript
class TrustManager {
  private trustGraph: TrustGraph;
  private reputationLedger: ReputationLedger;
  private blockchainInterface?: BlockchainInterface;

  constructor(options: TrustManagerOptions) {
    this.trustGraph = new TrustGraph();
    this.reputationLedger = new ReputationLedger();
    this.blockchainInterface = options.blockchainEnabled ? new BlockchainInterface() : undefined;
  }

  async establishTrust(
    trustor: string,
    trustee: string,
    trustLevel: number,
    evidence?: TrustEvidence[]
  ): Promise<TrustRelationship> {
    const relationship: TrustRelationship = {
      id: crypto.randomUUID(),
      trustor,
      trustee,
      trustLevel,
      evidence: evidence || [],
      establishedAt: Date.now(),
      expiresAt: Date.now() + (30 * 24 * 60 * 60 * 1000), // 30 days
      status: 'active'
    };

    // Add to trust graph
    await this.trustGraph.addRelationship(relationship);

    // Update reputation
    await this.reputationLedger.updateReputation(trustee, trustLevel, trustor);

    // Optional blockchain recording
    if (this.blockchainInterface) {
      await this.blockchainInterface.recordTrustTransaction(relationship);
    }

    return relationship;
  }

  async calculateTrustScore(agentId: string): Promise<TrustScore> {
    const relationships = await this.trustGraph.getIncomingTrust(agentId);
    const reputation = await this.reputationLedger.getReputation(agentId);

    let totalScore = 0;
    let weightSum = 0;

    for (const rel of relationships) {
      if (rel.expiresAt > Date.now() && rel.status === 'active') {
        const trustorScore = await this.getTrustorReliability(rel.trustor);
        const evidenceWeight = this.calculateEvidenceWeight(rel.evidence);
        const weight = trustorScore * evidenceWeight;

        totalScore += rel.trustLevel * weight;
        weightSum += weight;
      }
    }

    const directTrust = weightSum > 0 ? totalScore / weightSum : 0;
    const reputationScore = reputation.score;
    
    // Combine direct trust and reputation
    const finalScore = (directTrust * 0.7) + (reputationScore * 0.3);

    return {
      agentId,
      overallScore: Math.min(100, Math.max(0, finalScore)),
      directTrust,
      reputationScore,
      relationshipCount: relationships.length,
      lastUpdated: Date.now()
    };
  }

  async revokeTrust(trustor: string, trustee: string, reason: string): Promise<void> {
    const relationship = await this.trustGraph.getRelationship(trustor, trustee);
    
    if (relationship) {
      relationship.status = 'revoked';
      relationship.revocationReason = reason;
      relationship.revokedAt = Date.now();

      await this.trustGraph.updateRelationship(relationship);
      await this.reputationLedger.adjustReputation(trustee, -relationship.trustLevel, trustor);

      if (this.blockchainInterface) {
        await this.blockchainInterface.recordTrustRevocation(relationship);
      }
    }
  }

  private async getTrustorReliability(trustorId: string): Promise<number> {
    const trustorScore = await this.calculateTrustScore(trustorId);
    return Math.min(1.0, trustorScore.overallScore / 100);
  }

  private calculateEvidenceWeight(evidence: TrustEvidence[]): number {
    let weight = 0.1; // Base weight

    for (const item of evidence) {
      switch (item.type) {
        case 'social_proof':
          weight += 0.2;
          break;
        case 'behavior_history':
          weight += 0.3;
          break;
        case 'hardware_attestation':
          weight += 0.4;
          break;
        case 'cryptographic_proof':
          weight += 0.5;
          break;
      }
    }

    return Math.min(1.0, weight);
  }
}

interface TrustRelationship {
  id: string;
  trustor: string;
  trustee: string;
  trustLevel: number;
  evidence: TrustEvidence[];
  establishedAt: number;
  expiresAt: number;
  status: 'active' | 'expired' | 'revoked';
  revocationReason?: string;
  revokedAt?: number;
}

interface TrustEvidence {
  type: 'social_proof' | 'behavior_history' | 'hardware_attestation' | 'cryptographic_proof';
  data: unknown;
  verifier: string;
  timestamp: number;
  weight: number;
}

interface TrustScore {
  agentId: string;
  overallScore: number;
  directTrust: number;
  reputationScore: number;
  relationshipCount: number;
  lastUpdated: number;
}
```

## Synchronization Models

```typescript
class SynchronizationManager {
  private liveStreamSync: LiveStreamSync;
  private pushPullGossip: PushPullGossip;
  private conflictResolver: ConflictResolver;

  constructor() {
    this.liveStreamSync = new LiveStreamSync();
    this.pushPullGossip = new PushPullGossip();
    this.conflictResolver = new ConflictResolver();
  }

  async initializeLiveStreamSync(peerId: string): Promise<StreamSession> {
    const session = await this.liveStreamSync.createSession(peerId);
    
    // Set up bidirectional stream
    await session.establishConnection();
    
    // Configure sync parameters
    session.configure({
      batchSize: 100,
      syncInterval: 1000, // 1 second
      retryPolicy: {
        maxAttempts: 3,
        backoffStrategy: 'exponential',
        baseDelay: 1000
      }
    });

    return session;
  }

  async performGossipSync(peers: string[]): Promise<GossipSyncResult> {
    const syncResults: PeerSyncResult[] = [];

    for (const peerId of peers) {
      try {
        const peerResult = await this.syncWithPeer(peerId);
        syncResults.push(peerResult);
      } catch (error) {
        syncResults.push({
          peerId,
          success: false,
          error: (error as Error).message,
          timestamp: Date.now()
        });
      }
    }

    return {
      totalPeers: peers.length,
      successfulSyncs: syncResults.filter(r => r.success).length,
      results: syncResults,
      timestamp: Date.now()
    };
  }

  private async syncWithPeer(peerId: string): Promise<PeerSyncResult> {
    // Get local state hash
    const localHash = await this.getLocalStateHash();
    
    // Request peer state hash
    const peerHash = await this.pushPullGossip.requestStateHash(peerId);
    
    if (localHash === peerHash) {
      return {
        peerId,
        success: true,
        action: 'no_sync_needed',
        timestamp: Date.now()
      };
    }

    // Determine sync direction
    const syncPlan = await this.createSyncPlan(peerId, localHash, peerHash);
    
    // Execute sync
    const syncResult = await this.executeSyncPlan(syncPlan);
    
    return {
      peerId,
      success: true,
      action: syncResult.action,
      messagesReceived: syncResult.messagesReceived,
      messagesSent: syncResult.messagesSent,
      timestamp: Date.now()
    };
  }

  private async createSyncPlan(peerId: string, localHash: string, peerHash: string): Promise<SyncPlan> {
    const localMessages = await this.getRecentMessages();
    const peerMessages = await this.pushPullGossip.requestRecentMessages(peerId);
    
    const toReceive = peerMessages.filter(msg => !this.hasMessage(msg.id));
    const toSend = localMessages.filter(msg => !this.peerHasMessage(peerId, msg.id));
    
    return {
      peerId,
      toReceive,
      toSend,
      conflicts: this.detectConflicts(localMessages, peerMessages)
    };
  }

  private async executeSyncPlan(plan: SyncPlan): Promise<SyncExecutionResult> {
    let messagesReceived = 0;
    let messagesSent = 0;

    // Send messages to peer
    if (plan.toSend.length > 0) {
      await this.pushPullGossip.sendMessages(plan.peerId, plan.toSend);
      messagesSent = plan.toSend.length;
    }

    // Receive messages from peer
    if (plan.toReceive.length > 0) {
      await this.processReceivedMessages(plan.toReceive);
      messagesReceived = plan.toReceive.length;
    }

    // Resolve conflicts
    if (plan.conflicts.length > 0) {
      await this.conflictResolver.resolveConflicts(plan.conflicts);
    }

    return {
      action: 'sync_completed',
      messagesReceived,
      messagesSent,
      conflictsResolved: plan.conflicts.length
    };
  }
}

interface StreamSession {
  peerId: string;
  establishConnection(): Promise<void>;
  configure(options: StreamOptions): void;
  send(messages: KLinkMessage[]): Promise<void>;
  receive(handler: (messages: KLinkMessage[]) => Promise<void>): void;
  close(): Promise<void>;
}

interface StreamOptions {
  batchSize: number;
  syncInterval: number;
  retryPolicy: RetryPolicy;
}

interface GossipSyncResult {
  totalPeers: number;
  successfulSyncs: number;
  results: PeerSyncResult[];
  timestamp: number;
}

interface PeerSyncResult {
  peerId: string;
  success: boolean;
  action?: string;
  messagesReceived?: number;
  messagesSent?: number;
  error?: string;
  timestamp: number;
}
```

## Protocol Flow Examples

### Agent Introduction Flow

```typescript
class AgentIntroductionProtocol {
  private identity: AgentIdentity;
  private capabilityManager: CapabilityManager;
  private messageFactory: MessageFactory;

  async introduceToAgent(targetAgent: string): Promise<IntroductionResult> {
    // Step 1: Send ping
    const pingMessage = await this.messageFactory.createMessage(
      targetAgent,
      MessageType.AGENT_PING,
      {
        version: '1.0.0',
        capabilities: await this.capabilityManager.getCapabilities(),
        publicKey: this.identity.getPublicKey()
      }
    );

    const pongResponse = await this.sendAndWaitForResponse(pingMessage, MessageType.AGENT_PONG, 5000);
    
    if (!pongResponse) {
      throw new Error('No response to ping');
    }

    // Step 2: Receive capability advertisement
    const capabilityMessage = await this.waitForMessage(MessageType.CAPABILITY_ADVERTISE, 10000);
    
    if (capabilityMessage) {
      await this.capabilityManager.processCapabilityAdvertisement(capabilityMessage);
    }

    // Step 3: Send our capabilities
    const ourCapabilities = await this.messageFactory.createMessage(
      targetAgent,
      MessageType.CAPABILITY_ADVERTISE,
      await this.capabilityManager.getDetailedCapabilities()
    );

    await this.sendMessage(ourCapabilities);

    return {
      success: true,
      agentId: targetAgent,
      capabilities: capabilityMessage?.payload.data,
      establishedAt: Date.now()
    };
  }

  private async sendAndWaitForResponse(
    message: KLinkMessage,
    expectedResponseType: MessageType,
    timeout: number
  ): Promise<KLinkMessage | null> {
    await this.sendMessage(message);
    
    return new Promise((resolve) => {
      const timer = setTimeout(() => resolve(null), timeout);
      
      this.onMessage(expectedResponseType, (response) => {
        if (response.reply_to === message.id) {
          clearTimeout(timer);
          resolve(response);
        }
      });
    });
  }
}

interface IntroductionResult {
  success: boolean;
  agentId: string;
  capabilities?: unknown;
  establishedAt: number;
}
```

### Task Delegation Flow

```typescript
class TaskDelegationProtocol {
  private messageFactory: MessageFactory;
  private taskManager: TaskManager;

  async delegateTask(targetAgent: string, task: TaskDefinition): Promise<TaskDelegationResult> {
    // Create task
    const taskId = crypto.randomUUID();
    const taskMessage = await this.messageFactory.createMessage(
      targetAgent,
      MessageType.TASK_CREATE,
      {
        taskId,
        type: task.type,
        parameters: task.parameters,
        priority: task.priority,
        deadline: task.deadline
      }
    );

    await this.sendMessage(taskMessage);

    // Wait for task acceptance/rejection
    const response = await this.waitForTaskResponse(taskId, 30000);
    
    if (!response || response.payload.data.status === 'rejected') {
      return {
        success: false,
        taskId,
        reason: response?.payload.data.reason || 'No response'
      };
    }

    // Monitor task progress
    const progressMonitor = this.startProgressMonitoring(taskId, targetAgent);
    
    return {
      success: true,
      taskId,
      estimatedCompletion: response.payload.data.estimatedCompletion,
      progressMonitor
    };
  }

  private startProgressMonitoring(taskId: string, agentId: string): TaskProgressMonitor {
    return new TaskProgressMonitor(taskId, agentId, {
      onProgress: (progress) => this.handleTaskProgress(taskId, progress),
      onComplete: (result) => this.handleTaskComplete(taskId, result),
      onError: (error) => this.handleTaskError(taskId, error)
    });
  }

  private async handleTaskProgress(taskId: string, progress: TaskProgress): Promise<void> {
    await this.taskManager.updateTaskProgress(taskId, progress);
  }

  private async handleTaskComplete(taskId: string, result: TaskResult): Promise<void> {
    await this.taskManager.completeTask(taskId, result);
  }

  private async handleTaskError(taskId: string, error: TaskError): Promise<void> {
    await this.taskManager.failTask(taskId, error);
  }
}

interface TaskDefinition {
  type: string;
  parameters: Record<string, unknown>;
  priority: 'low' | 'normal' | 'high' | 'critical';
  deadline?: number;
}

interface TaskDelegationResult {
  success: boolean;
  taskId: string;
  estimatedCompletion?: number;
  progressMonitor?: TaskProgressMonitor;
  reason?: string;
}
```

## Security Implementation

```typescript
class SecurityLayer {
  private encryptionService: EncryptionService;
  private rateLimiter: RateLimiter;
  private proofOfWorkValidator: ProofOfWorkValidator;

  async validateMessage(message: KLinkMessage, senderPublicKey: string): Promise<ValidationResult> {
    const validations = await Promise.all([
      this.validateSignature(message, senderPublicKey),
      this.validateTimestamp(message),
      this.validateNonce(message),
      this.checkRateLimit(message.from),
      this.validateProofOfWork(message)
    ]);

    const isValid = validations.every(v => v.valid);
    const errors = validations.filter(v => !v.valid).map(v => v.error);

    return {
      valid: isValid,
      errors,
      validations
    };
  }

  async encryptMessage(message: KLinkMessage, recipientPublicKey: string): Promise<KLinkMessage> {
    const encryptedPayload = await this.encryptionService.encrypt(
      JSON.stringify(message.payload),
      recipientPublicKey
    );

    return {
      ...message,
      payload: {
        data: { encrypted: true, content: encryptedPayload },
        metadata: {
          ...message.payload.metadata,
          encryption: {
            algorithm: 'x25519-chacha20-poly1305',
            recipientPublicKey
          }
        }
      }
    };
  }

  async decryptMessage(message: KLinkMessage, privateKey: string): Promise<KLinkMessage> {
    if (!this.isEncrypted(message)) {
      return message;
    }

    const encryptedContent = message.payload.data.content;
    const decryptedContent = await this.encryptionService.decrypt(encryptedContent, privateKey);
    const originalPayload = JSON.parse(decryptedContent);

    return {
      ...message,
      payload: originalPayload
    };
  }

  private async validateSignature(message: KLinkMessage, publicKey: string): Promise<ValidationStep> {
    const messageFactory = new MessageFactory(new AgentIdentity());
    const isValid = await messageFactory.verifyMessage(message, publicKey);
    
    return {
      step: 'signature',
      valid: isValid,
      error: isValid ? undefined : 'Invalid signature'
    };
  }

  private async validateTimestamp(message: KLinkMessage): Promise<ValidationStep> {
    const now = Date.now();
    const messageAge = now - message.timestamp;
    const maxAge = 5 * 60 * 1000; // 5 minutes

    const isValid = messageAge >= 0 && messageAge <= maxAge;
    
    return {
      step: 'timestamp',
      valid: isValid,
      error: isValid ? undefined : 'Message timestamp out of acceptable range'
    };
  }

  private async validateNonce(message: KLinkMessage): Promise<ValidationStep> {
    const isUsed = await this.hasNonceBeenUsed(message.nonce);
    
    if (!isUsed) {
      await this.recordNonce(message.nonce, message.timestamp);
    }
    
    return {
      step: 'nonce',
      valid: !isUsed,
      error: isUsed ? 'Nonce has been used before (replay attack)' : undefined
    };
  }

  private async checkRateLimit(agentId: string): Promise<ValidationStep> {
    const isAllowed = await this.rateLimiter.checkLimit(agentId, 'message');
    
    return {
      step: 'rate_limit',
      valid: isAllowed,
      error: isAllowed ? undefined : 'Rate limit exceeded'
    };
  }

  private async validateProofOfWork(message: KLinkMessage): Promise<ValidationStep> {
    // Optional proof-of-work validation for high-volume senders
    const requiresPoW = await this.requiresProofOfWork(message.from);
    
    if (!requiresPoW) {
      return { step: 'proof_of_work', valid: true };
    }

    const isValid = await this.proofOfWorkValidator.validate(message);
    
    return {
      step: 'proof_of_work',
      valid: isValid,
      error: isValid ? undefined : 'Invalid proof of work'
    };
  }
}

interface ValidationResult {
  valid: boolean;
  errors: string[];
  validations: ValidationStep[];
}

interface ValidationStep {
  step: string;
  valid: boolean;
  error?: string;
}
```

## Related Documentation

- **[Agent Message Bus & Event Pipeline](28_agent-message-bus-event-pipeline.md)** - Message bus infrastructure
- **[Kind Link Protocol Specification](29_kind-link-protocol-specification.md)** - Core protocol specification
- **[Device Agent Bootstrap Protocol](30_device-agent-bootstrap-protocol.md)** - Agent initialization
- **[kAI API & Socket Services](31_kai-api-socket-services.md)** - API layer integration

## Implementation Status

- ✅ Agent identity and transport layer
- ✅ Message format and validation
- ✅ Trust management system
- ✅ Synchronization protocols
- ✅ Security and encryption layer
- 🔄 Protocol flow implementations
- 🔄 Rate limiting and abuse prevention
- ⏳ Blockchain integration
- ⏳ Advanced cryptographic features 