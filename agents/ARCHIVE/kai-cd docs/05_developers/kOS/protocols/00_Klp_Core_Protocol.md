---
title: "KLP Core Protocol"
description: "Technical specification for klp core protocol"
type: "protocol"
status: "current"
priority: "medium"
last_updated: "2025-06-22"
agent_notes: "AI agent guidance for implementing klp core protocol"
---

# 01: Kind Link Protocol (KLP) Core Specification

> **Source**: `documentation/brainstorm/kOS/30_klp_protocol_spec.md`  
> **Migrated**: 2025-01-20  
> **Status**: Foundation Protocol

## Protocol Overview

The Kind Link Protocol (KLP) is a decentralized, identity-centric communication protocol that enables secure interaction between agents, services, nodes, and users across the kOS ecosystem. It provides the foundation for trust, authentication, and message routing in distributed multi-agent networks.

## Core Objectives

### Universal Interoperability
- Enable secure agent communication across any node or device
- Support verifiable identity and cryptographically signed messages
- Facilitate decentralized ownership with user-defined governance
- Operate across P2P, cloud, mesh, and hybrid network topologies

### Programmable Service Composition
- Enable dynamic service discovery and capability negotiation
- Support composable service chaining and workflow orchestration
- Provide standardized interfaces for cross-platform integration
- Facilitate automated agent collaboration and task delegation

## Architecture Components

### Core Directory Structure
```typescript
src/klp/
├── registry/
│   ├── NodeDirectory.ts           # Node discovery and trust management
│   └── CapabilityIndex.ts         # Service-to-peer capability mapping
├── identity/
│   ├── IdentityManager.ts         # DID generation and validation
│   ├── DID.ts                     # Decentralized identifier schema
│   └── ProofOfOrigin.ts           # Message attestation and timestamps
├── messaging/
│   ├── KLPEnvelope.ts             # Standard message format
│   ├── KLPRouter.ts               # Multi-hop route resolution
│   └── KLPTransport.ts            # Transport layer abstraction
├── contracts/
│   ├── FederatedAction.ts         # Distributed task contracts
│   └── ContractValidator.ts       # Intent validation logic
└── auth/
    ├── TokenGrant.ts              # Scoped access tokens
    └── ScopeDefinition.ts         # Capability-based permissions
```

## Identity Framework

### Decentralized Identity (DID)
Every entity in the kOS ecosystem has a cryptographically verifiable identifier:

```
Format: kind:did:base64_pubkey#ed25519
```

**Properties:**
- **Cryptographic Generation**: Based on Ed25519 public keys
- **Self-Sovereign**: No central authority required
- **Verifiable**: Public key embedded for signature verification
- **Extensible**: Optional service endpoints for enhanced functionality

### Trust and Verification
- **Signature Requirement**: All messages signed with Ed25519 or secp256k1
- **Trust Networks**: Local registries with web-of-trust support
- **Verification Chain**: Cryptographic proof of message origin
- **Revocation Support**: Identity and capability revocation mechanisms

## Message Protocol

### KLP Envelope Format
```typescript
interface KLPMessage {
  id: string;                        // Unique message identifier (UUID)
  from: DID;                         // Sender's decentralized identifier
  to: DID | Topic;                   // Recipient or topic destination
  type: 'event' | 'task' | 'contract'; // Message classification
  protocol: 'klp/1.0';              // Protocol version
  timestamp: string;                 // ISO 8601 timestamp
  payload: any;                      // Message content
  signature: string;                 // Cryptographic signature
  route?: RouteHint[];               // Optional routing information
  auth?: TokenGrant;                 // Optional authorization token
}
```

### Message Types
- **Event**: Asynchronous notifications and state updates
- **Task**: Synchronous requests requiring responses
- **Contract**: Formal agreements with multiple participants

## Transport Layer

### Supported Transports
KLP implements a multi-transport architecture supporting:

| Transport | Use Case | Status |
|-----------|----------|---------|
| **WebSocket** | Real-time web communication | Production |
| **HTTP3** | High-performance web requests | Production |
| **MQTT** | IoT and lightweight messaging | Production |
| **Reticulum** | Mesh networking and offline-first | Beta |
| **Bluetooth** | Local device communication | Planned |
| **Nostr** | Decentralized social protocols | Planned |

### Routing Mechanisms

#### Route Hints
```typescript
interface RouteHint {
  relay: DID;                        // Relay node identifier
  via: string;                       // Transport protocol
  latency?: number;                  // Optional performance metric
}
```

#### Routing Modes
- **Direct**: Point-to-point communication
- **Mesh**: Multi-hop routing through peer networks
- **Overlay**: Privacy-preserving routing (Tor, I2P, VPN)
- **Federated**: Inter-cluster communication

## Service Discovery

### Capability Manifests
Services advertise their capabilities through standardized manifests:

```typescript
interface ServiceManifest {
  serviceId: string;                 // Unique service identifier
  version: string;                   // Semantic version
  capabilities: string[];            // Supported capabilities
  roles: string[];                   // Service roles in network
  ttl: number;                       // Time-to-live for manifest
  endpoint: string;                  // Service endpoint URL
  signatures: string[];              // Cryptographic attestations
}
```

### Discovery Mechanisms
- **Gossip Protocol**: Peer-to-peer manifest distribution
- **Registry Services**: Centralized capability directories
- **DHT Storage**: Distributed hash table for scalable lookup
- **Handshake Verification**: Real-time capability validation

## Federated Contracts

### Contract Structure
Distributed actions are formalized as immutable contracts:

```typescript
interface FederatedAction {
  actionId: string;                  // Unique action identifier
  from: DID;                         // Contract initiator
  participants: DID[];               // Required participants
  intent: string;                    // Human-readable intent
  scope: ScopeDefinition;            // Permission boundaries
  expiry: number;                    // Contract expiration
  signatures: string[];              // Multi-party signatures
}
```

### Contract Lifecycle
1. **Proposal**: Initial contract creation and distribution
2. **Negotiation**: Participant review and modification
3. **Execution**: Atomic contract fulfillment
4. **Audit**: Immutable logging for accountability

## Authorization Framework

### Token Grants
Temporary access delegation through scoped tokens:

```typescript
interface TokenGrant {
  issuedBy: DID;                     // Token issuer
  for: DID;                          // Token recipient
  capabilities: string[];            // Granted permissions
  ttl: number;                       // Token lifetime
  token: string;                     // Signed JWT/JWS token
}
```

### Permission Scoping
- **Capability-Based**: Fine-grained permission sets
- **Time-Limited**: Automatic token expiration
- **Revocable**: Real-time permission withdrawal
- **Auditable**: Complete access logging

## Security Specifications

### Cryptographic Standards
| Component | Specification |
|-----------|---------------|
| **Encryption** | AES-256-GCM, ChaCha20-Poly1305 |
| **Signatures** | Ed25519, secp256k1 |
| **Key Exchange** | X25519, ECDH |
| **Hashing** | SHA-256, BLAKE3 |

### Security Measures
- **Identity Verification**: DID + signature chain validation
- **Message Integrity**: Cryptographic signatures on all messages
- **Audit Logging**: Append-only logs with Merkle tree proofs
- **Network Segmentation**: Role-based endpoint access control
- **Key Rotation**: Automatic key lifecycle management
- **Abuse Prevention**: Optional proof-of-work throttling

## Synchronization Patterns

### Sync Operations
- `sync:capabilities` - Service capability updates
- `sync:memory` - Agent memory synchronization
- `sync:config` - Configuration state updates
- `sync:status` - Health and status information

### Storage Backends
- **IndexedDB**: Browser-based storage
- **SQLite**: Embedded database storage
- **Redis**: In-memory caching and pub/sub
- **CRDTs**: Conflict-free replicated data types
- **Merkle DAG**: Content-addressed storage

---

### Related Documents
- [KLP Specification](02_klp_specification.md) - Extended protocol details
- [Kind Link Protocol](03_kind_link_protocol.md) - Implementation guide
- [Protocol Overview](05_protocols_overview.md) - Multi-protocol architecture

### Implementation References
- [Current Reticulum Connector](../../../src/connectors/definitions/reticulum.ts)
- [Message Bus Architecture](../services/03_orchestration_hub.md)
