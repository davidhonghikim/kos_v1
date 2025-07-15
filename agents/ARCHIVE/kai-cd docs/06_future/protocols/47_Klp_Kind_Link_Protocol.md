---
title: "KLP Specification – Kind Link Protocol"
description: "Foundational interoperability standard for agent communication, permission negotiation, and decentralized coordination across the kAI/kOS ecosystem"
type: "protocol"
status: "future"
priority: "critical"
last_updated: "2024-12-21"
related_docs: ["agent-delegation-rules.md", "agent-trust-protocols.md"]
implementation_status: "planned"
---

# KLP Specification – Kind Link Protocol (Agent & Entity Interoperability)

## Agent Context
**For AI Agents**: This document defines the foundational communication protocol that ALL agents must implement for interoperability. KLP is the backbone of agent-to-agent communication, identity verification, and capability negotiation. Every agent must support KLPHandshake, KLPEnvelope, and capability negotiation.

**Implementation Priority**: Critical infrastructure - implement KLPIdentity and KLPHandshake first, then KLPEnvelope, then capability negotiation and state sync.

## Purpose

KLP enables autonomous agents, user applications, and external entities to:

- Discover each other through decentralized mechanisms
- Authenticate identities using cryptographic verification
- Negotiate capabilities and access permissions
- Exchange structured, signed messages securely
- Link into shared multi-agent workflows
- Participate in distributed governance and state synchronization
- Maintain trust relationships across federated networks

## Architecture

### Directory Structure

```typescript
src/
└── protocols/
    ├── klp/
    │   ├── KLPHandshake.ts               // Secure initial link negotiation
    │   ├── KLPIdentity.ts                // DID and keypair identity handling
    │   ├── KLPEnvelope.ts               // Signed message transport
    │   ├── KLPCapabilityRequest.ts      // Capability negotiation layer
    │   ├── KLPStateSync.ts              // State update sync layer
    │   ├── KLPDiscovery.ts              // Peer discovery and service location
    │   └── registry/
    │       ├── EntityRegistry.ts        // Known agents and services
    │       ├── TrustLinkGraph.ts        // Trust-weighted graph of relationships
    │       └── ServiceDirectory.ts      // Service discovery and registration
```

## Identity Layer

### DID and Cryptographic Keys

Every entity (agent, service, user) has a **Decentralized Identifier (DID)** backed by cryptographic keys:

```typescript
interface KLPIdentity {
  did: string;                          // Format: "did:kind:agent123"
  publicKey: string;                    // Ed25519 public key
  exchangeKey: string;                  // X25519 key exchange key
  type: 'agent' | 'service' | 'user';
  capabilities: string[];               // Advertised capabilities
  metadata: IdentityMetadata;
  signature: string;                    // Self-signed identity proof
}

interface IdentityMetadata {
  name: string;
  description?: string;
  version: string;
  created: string;
  lastUpdated: string;
  endpoints: ServiceEndpoint[];
  trustAnchors: string[];               // DIDs of trust anchors
}

interface ServiceEndpoint {
  type: 'KLPService' | 'WebSocket' | 'HTTP';
  endpoint: string;                     // e.g., "wss://agent.example.com/klp"
  priority: number;                     // Connection priority
}
```

### Identity Document Structure

```json
{
  "id": "did:kind:agent123",
  "publicKey": "edpk_5a7b9c2d1e3f4g5h6i7j8k9l0m1n2o3p4q5r6s7t8u9v0w1x2y3z",
  "exchangeKey": "x25519_1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z",
  "type": "agent",
  "capabilities": ["llm:completion", "vector:search", "file:read"],
  "metadata": {
    "name": "Research Assistant",
    "version": "1.2.0",
    "created": "2024-01-01T00:00:00Z",
    "endpoints": [
      {
        "type": "KLPService",
        "endpoint": "wss://localhost:8080/klp",
        "priority": 1
      }
    ]
  },
  "signature": "ed25519_signature_of_identity_document"
}
```

## Handshake Protocol

### Four-Phase Handshake

```typescript
interface KLPHandshakeFlow {
  phase1: HelloMessage;
  phase2: ChallengeMessage;
  phase3: VerifyMessage;
  phase4: AcceptMessage;
}

interface HelloMessage {
  type: 'klp:hello';
  from: string;                         // Initiator DID
  to?: string;                          // Target DID (optional for discovery)
  capabilities: string[];               // Requested capabilities
  protocols: string[];                  // Supported protocol versions
  nonce: string;                        // Random nonce
  timestamp: string;
  signature: string;
}

interface ChallengeMessage {
  type: 'klp:challenge';
  from: string;                         // Responder DID
  to: string;                           // Initiator DID
  challenge: string;                    // Encrypted challenge using initiator's exchange key
  supportedCapabilities: string[];      // Capabilities responder can provide
  sessionKey: string;                   // Ephemeral session key (encrypted)
  timestamp: string;
  signature: string;
}

interface VerifyMessage {
  type: 'klp:verify';
  from: string;                         // Initiator DID
  to: string;                           // Responder DID
  challengeResponse: string;            // Decrypted and signed challenge
  requestedCapabilities: string[];      // Final capability request
  sessionConfirm: string;               // Session key confirmation
  timestamp: string;
  signature: string;
}

interface AcceptMessage {
  type: 'klp:accept';
  from: string;                         // Responder DID
  to: string;                           // Initiator DID
  grantedCapabilities: string[];        // Approved capabilities
  sessionId: string;                    // Established session identifier
  expiresAt: string;                    // Session expiration
  constraints?: CapabilityConstraints;  // Usage constraints
  timestamp: string;
  signature: string;
}
```

### Handshake Implementation

```typescript
class KLPHandshake {
  private identity: KLPIdentity;
  private cryptoProvider: CryptoProvider;
  private sessionManager: SessionManager;

  async initiateHandshake(targetDID: string, requestedCapabilities: string[]): Promise<KLPSession> {
    // Phase 1: Send Hello
    const hello: HelloMessage = {
      type: 'klp:hello',
      from: this.identity.did,
      to: targetDID,
      capabilities: requestedCapabilities,
      protocols: ['klp/1.0'],
      nonce: generateNonce(),
      timestamp: new Date().toISOString(),
      signature: ''
    };
    hello.signature = await this.signMessage(hello);

    const challenge = await this.sendMessage(hello);

    // Phase 2: Process Challenge
    const decryptedChallenge = await this.cryptoProvider.decrypt(
      challenge.challenge,
      this.identity.exchangeKey
    );

    // Phase 3: Send Verify
    const verify: VerifyMessage = {
      type: 'klp:verify',
      from: this.identity.did,
      to: targetDID,
      challengeResponse: await this.signChallenge(decryptedChallenge),
      requestedCapabilities,
      sessionConfirm: await this.confirmSessionKey(challenge.sessionKey),
      timestamp: new Date().toISOString(),
      signature: ''
    };
    verify.signature = await this.signMessage(verify);

    const accept = await this.sendMessage(verify);

    // Phase 4: Establish Session
    return this.sessionManager.createSession({
      sessionId: accept.sessionId,
      peerDID: targetDID,
      grantedCapabilities: accept.grantedCapabilities,
      expiresAt: accept.expiresAt,
      constraints: accept.constraints
    });
  }
}
```

## Message Transport Layer

### KLP Envelope Structure

```typescript
interface KLPEnvelope {
  id: string;                           // Unique message ID
  from: string;                         // Sender DID
  to: string;                           // Recipient DID
  type: KLPMessageType;
  sessionId?: string;                   // Session context
  timestamp: string;                    // ISO8601 timestamp
  expiresAt?: string;                   // Message expiration
  body: KLPMessageBody;
  metadata: EnvelopeMetadata;
  signature: string;                    // Ed25519 signature
}

type KLPMessageType = 
  | 'capability_request'
  | 'capability_response'
  | 'link_request'
  | 'link_response'
  | 'state_update'
  | 'state_query'
  | 'ping'
  | 'pong'
  | 'error'
  | 'revocation';

interface EnvelopeMetadata {
  priority: 'low' | 'normal' | 'high' | 'urgent';
  retryable: boolean;
  encrypted: boolean;
  compression?: 'gzip' | 'brotli';
  route?: string[];                     // Routing path for federated messages
}
```

### Message Processing

```typescript
class KLPMessageProcessor {
  private handlers: Map<KLPMessageType, MessageHandler> = new Map();
  private validator: MessageValidator;
  private encryptionProvider: EncryptionProvider;

  async processMessage(envelope: KLPEnvelope): Promise<KLPEnvelope | null> {
    // 1. Validate message structure
    const validation = await this.validator.validate(envelope);
    if (!validation.valid) {
      return this.createErrorResponse(envelope, validation.errors);
    }

    // 2. Verify signature
    const signatureValid = await this.verifySignature(envelope);
    if (!signatureValid) {
      return this.createErrorResponse(envelope, ['Invalid signature']);
    }

    // 3. Check expiration
    if (envelope.expiresAt && new Date(envelope.expiresAt) < new Date()) {
      return this.createErrorResponse(envelope, ['Message expired']);
    }

    // 4. Decrypt if necessary
    if (envelope.metadata.encrypted) {
      envelope.body = await this.encryptionProvider.decrypt(envelope.body, envelope.from);
    }

    // 5. Route to appropriate handler
    const handler = this.handlers.get(envelope.type);
    if (!handler) {
      return this.createErrorResponse(envelope, [`No handler for message type: ${envelope.type}`]);
    }

    return await handler.handle(envelope);
  }
}
```

## Capability Negotiation

### Capability Request System

```typescript
interface KLPCapabilityRequest {
  requester: string;                    // Requester DID
  requested: string;                    // Target DID
  capabilities: CapabilitySpec[];       // Requested capabilities
  context: RequestContext;
  constraints: RequestConstraints;
  reason: string;                       // Human-readable justification
  expiry?: string;                      // Request expiration
  signature: string;
}

interface CapabilitySpec {
  name: string;                         // e.g., 'read:memory', 'query:vector'
  parameters?: Record<string, any>;     // Capability-specific parameters
  scope?: string[];                     // Resource scope limitations
  priority: 'required' | 'preferred' | 'optional';
}

interface RequestContext {
  purpose: string;                      // Why this capability is needed
  duration: number;                     // Expected usage duration (seconds)
  frequency: number;                    // Expected usage frequency
  dataTypes: string[];                  // Types of data that will be processed
}

interface RequestConstraints {
  maxDuration?: number;                 // Maximum allowed duration
  maxFrequency?: number;                // Maximum usage frequency
  allowedHours?: string[];              // Time-based restrictions
  auditLevel: 'none' | 'basic' | 'full'; // Required audit level
}
```

### Capability Response

```typescript
interface KLPCapabilityResponse {
  requestId: string;                    // Original request ID
  responder: string;                    // Responder DID
  status: 'granted' | 'partial' | 'denied';
  grantedCapabilities: GrantedCapability[];
  deniedCapabilities: DeniedCapability[];
  conditions: GrantConditions;
  expiresAt: string;                    // Grant expiration
  signature: string;
}

interface GrantedCapability {
  name: string;
  parameters: Record<string, any>;
  constraints: CapabilityConstraints;
  auditRequired: boolean;
}

interface DeniedCapability {
  name: string;
  reason: string;
  alternative?: string;                 // Suggested alternative
}

interface GrantConditions {
  requiresApproval: boolean;
  approvalTimeout?: number;
  maxConcurrentUse?: number;
  rateLimits?: RateLimit[];
  auditingEnabled: boolean;
}
```

## Trust Link Graph

### Trust Relationship Management

```typescript
interface TrustLink {
  from: string;                         // Trustor DID
  to: string;                           // Trustee DID
  weight: number;                       // Trust weight (0.0 - 1.0)
  type: 'direct' | 'delegated' | 'inferred';
  capabilities: string[];               // Trusted capabilities
  constraints: TrustConstraints;
  issuedAt: string;
  expiresAt?: string;
  signature: string;
}

interface TrustConstraints {
  maxDelegationDepth: number;
  allowedResources: string[];
  deniedResources: string[];
  timeRestrictions: TimeRestriction[];
}

class TrustLinkGraph {
  private links: Map<string, TrustLink[]> = new Map();
  private trustCalculator: TrustCalculator;

  async calculateTrustPath(from: string, to: string): Promise<TrustPath | null> {
    const path = await this.findShortestTrustPath(from, to);
    if (!path) return null;

    const trustScore = this.trustCalculator.calculatePathTrust(path);
    const capabilities = this.derivePathCapabilities(path);

    return {
      path: path.map(link => link.to),
      trustScore,
      capabilities,
      constraints: this.mergePathConstraints(path)
    };
  }

  async addTrustLink(link: TrustLink): Promise<void> {
    // Validate trust link
    await this.validateTrustLink(link);

    // Store link
    const fromLinks = this.links.get(link.from) || [];
    fromLinks.push(link);
    this.links.set(link.from, fromLinks);

    // Update trust graph
    await this.updateTrustGraph(link);
  }
}
```

## State Synchronization

### State Update Protocol

```typescript
interface KLPStateUpdate {
  source: string;                       // Source DID
  target?: string;                      // Target DID (optional for broadcast)
  namespace: string;                    // State namespace
  operation: 'set' | 'delete' | 'merge' | 'increment';
  key: string;
  value?: any;
  version: number;                      // Vector clock or version number
  timestamp: string;
  signature: string;
}

interface KLPStateQuery {
  requester: string;
  target: string;
  namespace: string;
  keys?: string[];                      // Specific keys (optional)
  filter?: StateFilter;                 // Query filter
  includeHistory?: boolean;
  signature: string;
}

class KLPStateSync {
  private stateStore: StateStore;
  private vectorClock: VectorClock;
  private conflictResolver: ConflictResolver;

  async handleStateUpdate(update: KLPStateUpdate): Promise<void> {
    // Validate update
    const isValid = await this.validateStateUpdate(update);
    if (!isValid) {
      throw new Error('Invalid state update');
    }

    // Check for conflicts
    const currentState = await this.stateStore.get(update.namespace, update.key);
    if (currentState && this.hasConflict(currentState, update)) {
      const resolved = await this.conflictResolver.resolve(currentState, update);
      await this.stateStore.set(update.namespace, update.key, resolved);
    } else {
      await this.applyStateUpdate(update);
    }

    // Update vector clock
    this.vectorClock.update(update.source, update.version);

    // Propagate to subscribers
    await this.propagateStateUpdate(update);
  }
}
```

## Registry and Discovery

### Entity Registry

```typescript
interface EntityRegistration {
  did: string;
  identity: KLPIdentity;
  capabilities: string[];
  endpoints: ServiceEndpoint[];
  trustScore: number;
  lastSeen: string;
  metadata: RegistrationMetadata;
}

interface RegistrationMetadata {
  tags: string[];
  category: string;
  reputation: number;
  uptime: number;
  responseTime: number;
}

class EntityRegistry {
  private entities: Map<string, EntityRegistration> = new Map();
  private discoveryService: DiscoveryService;

  async registerEntity(registration: EntityRegistration): Promise<void> {
    // Validate registration
    await this.validateRegistration(registration);

    // Store registration
    this.entities.set(registration.did, registration);

    // Announce to network
    await this.announceRegistration(registration);
  }

  async discoverEntities(query: DiscoveryQuery): Promise<EntityRegistration[]> {
    // Local search first
    const localResults = this.searchLocal(query);

    // Federated search if needed
    if (localResults.length < query.maxResults && query.includeFederated) {
      const federatedResults = await this.discoveryService.searchFederated(query);
      return [...localResults, ...federatedResults].slice(0, query.maxResults);
    }

    return localResults;
  }
}
```

## Security and Governance

### Security Considerations

```typescript
interface KLPSecurityPolicy {
  requireSignatures: boolean;
  requireEncryption: boolean;
  maxMessageSize: number;
  maxSessionDuration: number;
  allowedCipherSuites: string[];
  trustedRoots: string[];               // Trusted root DIDs
  revocationCheckRequired: boolean;
}

class KLPSecurityManager {
  private policy: KLPSecurityPolicy;
  private revocationList: Set<string> = new Set();

  async validateSecurity(envelope: KLPEnvelope): Promise<SecurityValidationResult> {
    const results: SecurityCheck[] = [];

    // Check signature requirement
    if (this.policy.requireSignatures && !envelope.signature) {
      results.push({ check: 'signature', passed: false, reason: 'Signature required' });
    }

    // Check encryption requirement
    if (this.policy.requireEncryption && !envelope.metadata.encrypted) {
      results.push({ check: 'encryption', passed: false, reason: 'Encryption required' });
    }

    // Check message size
    if (JSON.stringify(envelope).length > this.policy.maxMessageSize) {
      results.push({ check: 'size', passed: false, reason: 'Message too large' });
    }

    // Check revocation status
    if (this.policy.revocationCheckRequired && this.revocationList.has(envelope.from)) {
      results.push({ check: 'revocation', passed: false, reason: 'Sender revoked' });
    }

    return {
      valid: results.every(r => r.passed),
      checks: results
    };
  }
}
```

## Future Enhancements

| Feature | Target Version | Description |
|---------|----------------|-------------|
| Multi-agent broadcast routing | v1.1 | Efficient message routing for group communications |
| zkDelegationProof + CRDT support | v1.3 | Zero-knowledge proofs and conflict-free data types |
| On-chain DID anchoring + revocation | v1.5 | Blockchain-based identity anchoring and revocation |
| Federated discovery with trust stitching | v1.7 | Cross-domain discovery with trust propagation |
| Formal specification RFC | v2.0 | Complete formal specification document |
| Quantum-resistant cryptography | v2.2 | Post-quantum cryptographic algorithms |

## Implementation Guidelines

### Development Phases

1. **Phase 1**: Core identity and handshake protocol
2. **Phase 2**: Message transport and basic capabilities
3. **Phase 3**: Trust relationships and state synchronization
4. **Phase 4**: Advanced discovery and federation
5. **Phase 5**: Security hardening and governance features

### Protocol Compliance

All KLP implementations must:
- Support the four-phase handshake protocol
- Implement message signing and verification
- Respect capability constraints and limitations
- Maintain audit logs of all interactions
- Support graceful degradation for unsupported features

This protocol specification forms the foundation of secure, interoperable communication across the entire kAI/kOS ecosystem, enabling autonomous agents to collaborate while maintaining security and trust. 