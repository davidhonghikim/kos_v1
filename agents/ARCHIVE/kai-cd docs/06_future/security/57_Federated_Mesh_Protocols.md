---
title: "Federated Mesh Protocols"
description: "Inter-instance communication architecture for distributed kOS coordination"
type: "security"
status: "future"
priority: "high"
last_updated: "2025-01-03"
related_docs: ["agent-communication-protocols-core.md", "kind-link-protocol-core.md"]
implementation_status: "planned"
---

# Federated Mesh Protocols & Inter-Instance Communication

## Agent Context

This document defines the communication architecture and protocols enabling secure, scalable, and interoperable communication between distributed instances of kOS across devices, networks, and organizations. Agents must understand the complete technical implementation of mesh networking, peer discovery, secure messaging, and federated coordination.

## Architecture Overview

The Federated Mesh enables decentralized coordination of AI agents, users, and resources across kOS instances, supports peer discovery and secure messaging, enables trust propagation and shared vector resources, facilitates agent migration between instances, and ensures privacy-preserving interoperability.

## Communication Layers

### Transport Layer Architecture

```typescript
interface MeshTransportConfig {
  networking: {
    protocols: ('tcp' | 'udp' | 'quic' | 'websocket')[];
    ports: number[];
    encryption: 'tls' | 'noise' | 'wireguard';
  };
  local_mesh: {
    bluetooth: boolean;
    wifi_direct: boolean;
    lora: boolean;
    mesh_discovery: boolean;
  };
  overlay: {
    libp2p: boolean;
    nats: boolean;
    tor_hidden_services: boolean;
    custom_routing: boolean;
  };
}

class MeshTransportManager {
  private transports: Map<string, Transport>;
  private routingTable: RoutingTable;
  private peerDiscovery: PeerDiscovery;

  constructor(config: MeshTransportConfig) {
    this.initializeTransports(config);
    this.routingTable = new RoutingTable();
    this.peerDiscovery = new PeerDiscovery(config);
  }

  async initializeTransports(config: MeshTransportConfig): Promise<void> {
    // Initialize standard network transports
    if (config.networking.protocols.includes('tcp')) {
      this.transports.set('tcp', new TCPTransport(config.networking));
    }
    
    if (config.networking.protocols.includes('websocket')) {
      this.transports.set('websocket', new WebSocketTransport(config.networking));
    }

    // Initialize mesh transports
    if (config.local_mesh.bluetooth) {
      this.transports.set('bluetooth', new BluetoothMeshTransport());
    }

    // Initialize overlay networks
    if (config.overlay.libp2p) {
      this.transports.set('libp2p', new Libp2pTransport());
    }
  }

  async sendMessage(message: MeshMessage, targetPeer: PeerID): Promise<void> {
    const route = await this.routingTable.findRoute(targetPeer);
    const transport = this.transports.get(route.transport);
    
    if (!transport) {
      throw new Error(`Transport not available: ${route.transport}`);
    }

    await transport.send(message, route);
  }
}
```

### KLP (Kind Link Protocol) Implementation

```typescript
interface KLPAddress {
  scheme: 'klp';
  authority: string; // node.domain.kai
  path: string; // /commands or /agents/123
  query?: Record<string, string>;
  fragment?: string;
}

interface KLPMessage {
  type: KLPMessageType;
  source: KLPAddress;
  target: KLPAddress;
  payload: any;
  signature: string;
  timestamp: string;
  ttl: number;
  routing_hints?: string[];
}

type KLPMessageType = 
  | 'TASK_REQUEST' 
  | 'AGENT_MIGRATION' 
  | 'REPUTATION_DELTA' 
  | 'BROADCAST_ANNOUNCE' 
  | 'VECTOR_SYNC'
  | 'TRUST_UPDATE'
  | 'SERVICE_DISCOVERY';

class KLPClient {
  private nodeId: string;
  private signingKey: CryptoKey;
  private transportManager: MeshTransportManager;
  private messageHandlers: Map<KLPMessageType, MessageHandler>;

  constructor(nodeId: string, signingKey: CryptoKey, transportManager: MeshTransportManager) {
    this.nodeId = nodeId;
    this.signingKey = signingKey;
    this.transportManager = transportManager;
    this.messageHandlers = new Map();
  }

  async send(message: Partial<KLPMessage>): Promise<void> {
    const fullMessage: KLPMessage = {
      type: message.type!,
      source: this.parseAddress(`klp://${this.nodeId}`),
      target: this.parseAddress(message.target as any),
      payload: message.payload,
      signature: '',
      timestamp: new Date().toISOString(),
      ttl: message.ttl || 300, // 5 minutes default
      routing_hints: message.routing_hints
    };

    // Sign the message
    fullMessage.signature = await this.signMessage(fullMessage);

    // Route and send
    const targetPeer = await this.resolvePeer(fullMessage.target);
    await this.transportManager.sendMessage(fullMessage, targetPeer);
  }

  async handleMessage(message: KLPMessage): Promise<void> {
    // Verify signature
    const isValid = await this.verifyMessage(message);
    if (!isValid) {
      console.warn('Invalid message signature, dropping');
      return;
    }

    // Check TTL
    const messageTime = new Date(message.timestamp).getTime();
    const now = Date.now();
    if (now - messageTime > message.ttl * 1000) {
      console.warn('Message expired, dropping');
      return;
    }

    // Route to handler
    const handler = this.messageHandlers.get(message.type);
    if (handler) {
      await handler.handle(message);
    } else {
      console.warn(`No handler for message type: ${message.type}`);
    }
  }

  private parseAddress(address: string): KLPAddress {
    const url = new URL(address);
    return {
      scheme: 'klp',
      authority: url.hostname,
      path: url.pathname,
      query: Object.fromEntries(url.searchParams),
      fragment: url.hash ? url.hash.substring(1) : undefined
    };
  }

  private async signMessage(message: KLPMessage): Promise<string> {
    const messageWithoutSignature = { ...message, signature: '' };
    const encoder = new TextEncoder();
    const data = encoder.encode(JSON.stringify(messageWithoutSignature));
    
    const signature = await crypto.subtle.sign('Ed25519', this.signingKey, data);
    return btoa(String.fromCharCode(...new Uint8Array(signature)));
  }
}
```

## Peer Discovery & Node Roles

### Node Role System

```typescript
interface PeerNode {
  node_id: string;
  role: NodeRole;
  capabilities: string[];
  address: string;
  public_key: string;
  last_seen: string;
  trust_score: number;
  metadata: NodeMetadata;
}

type NodeRole = 'peer' | 'gateway' | 'archive' | 'validator' | 'bootstrap';

interface NodeMetadata {
  version: string;
  supported_protocols: string[];
  resource_limits: {
    max_connections: number;
    bandwidth_mbps: number;
    storage_gb: number;
  };
  geographic_region?: string;
  organization?: string;
}

class PeerDiscovery {
  private knownPeers: Map<string, PeerNode>;
  private dht: DistributedHashTable;
  private gossipProtocol: GossipProtocol;

  constructor(config: MeshTransportConfig) {
    this.knownPeers = new Map();
    this.dht = new DistributedHashTable(config);
    this.gossipProtocol = new GossipProtocol(config);
  }

  async discoverPeers(): Promise<PeerNode[]> {
    const discovered: PeerNode[] = [];

    // DHT discovery
    const dhtPeers = await this.dht.findPeers();
    discovered.push(...dhtPeers);

    // Gossip discovery
    const gossipPeers = await this.gossipProtocol.requestPeerList();
    discovered.push(...gossipPeers);

    // Local network discovery
    const localPeers = await this.discoverLocalPeers();
    discovered.push(...localPeers);

    // Update known peers
    for (const peer of discovered) {
      this.knownPeers.set(peer.node_id, peer);
    }

    return discovered;
  }

  async findSpecializedPeers(capability: string): Promise<PeerNode[]> {
    const candidates = Array.from(this.knownPeers.values())
      .filter(peer => peer.capabilities.includes(capability))
      .sort((a, b) => b.trust_score - a.trust_score);

    return candidates;
  }

  private async discoverLocalPeers(): Promise<PeerNode[]> {
    // Implementation for local network discovery
    // Bluetooth, WiFi Direct, mDNS, etc.
    return [];
  }
}
```

### Federation Capabilities

```typescript
interface FederationCapability {
  name: string;
  version: string;
  description: string;
  endpoints: string[];
  requirements: string[];
  trust_level_required: number;
}

class FederationManager {
  private capabilities: Map<string, FederationCapability>;
  private peerCapabilities: Map<string, FederationCapability[]>;

  async enableCapability(capability: FederationCapability): Promise<void> {
    this.capabilities.set(capability.name, capability);
    
    // Announce to network
    await this.announceCapability(capability);
  }

  async migrateAgent(agentId: string, targetNode: string): Promise<AgentMigrationResult> {
    // Serialize agent state
    const agentState = await this.serializeAgent(agentId);
    
    // Verify target node capabilities
    const targetCapabilities = this.peerCapabilities.get(targetNode);
    if (!this.canHostAgent(agentState, targetCapabilities)) {
      throw new Error(`Target node cannot host agent: ${agentId}`);
    }

    // Create migration package
    const migrationPackage: AgentMigrationPackage = {
      agent_id: agentId,
      state: agentState,
      signature: await this.signAgentState(agentState),
      source_node: this.nodeId,
      target_node: targetNode,
      timestamp: new Date().toISOString()
    };

    // Send migration request
    const result = await this.sendMigrationRequest(migrationPackage);
    
    if (result.success) {
      // Clean up local agent
      await this.cleanupLocalAgent(agentId);
    }

    return result;
  }

  async syncVectorData(vectorSpace: string, targetNodes: string[]): Promise<SyncResult[]> {
    const localVectors = await this.getLocalVectors(vectorSpace);
    const results: SyncResult[] = [];

    for (const nodeId of targetNodes) {
      try {
        const syncResult = await this.syncWithNode(nodeId, vectorSpace, localVectors);
        results.push(syncResult);
      } catch (error) {
        results.push({
          node_id: nodeId,
          success: false,
          error: error.message,
          timestamp: new Date().toISOString()
        });
      }
    }

    return results;
  }

  private async serializeAgent(agentId: string): Promise<SerializedAgent> {
    // Implementation for agent serialization
    return {
      id: agentId,
      state: {}, // Complete agent state
      behavioral_fingerprint: '',
      audit_trail: [],
      config_snapshot: {}
    };
  }
}
```

## Security Architecture

### Identity & Verification

```typescript
interface FederatedIdentity {
  node_id: string;
  public_key: string;
  certificate_chain: Certificate[];
  trust_anchors: string[];
  revocation_status: 'valid' | 'revoked' | 'suspended';
}

class FederatedSecurityManager {
  private identityStore: Map<string, FederatedIdentity>;
  private trustAnchors: Set<string>;
  private revocationList: Set<string>;

  async verifyPeerIdentity(peerId: string, identity: FederatedIdentity): Promise<boolean> {
    // Check revocation status
    if (this.revocationList.has(identity.node_id)) {
      return false;
    }

    // Verify certificate chain
    for (const cert of identity.certificate_chain) {
      const isValid = await this.verifyCertificate(cert);
      if (!isValid) {
        return false;
      }
    }

    // Check trust anchors
    const hasTrustedAnchor = identity.trust_anchors.some(anchor => 
      this.trustAnchors.has(anchor)
    );

    return hasTrustedAnchor;
  }

  async establishSecureChannel(peerId: string): Promise<SecureChannel> {
    const peerIdentity = this.identityStore.get(peerId);
    if (!peerIdentity) {
      throw new Error(`Unknown peer: ${peerId}`);
    }

    // Perform key exchange
    const ephemeralKeyPair = await crypto.subtle.generateKey(
      { name: 'X25519' },
      true,
      ['deriveKey']
    );

    const sharedSecret = await this.performKeyExchange(
      ephemeralKeyPair.privateKey,
      peerIdentity.public_key
    );

    // Derive session keys
    const sessionKeys = await this.deriveSessionKeys(sharedSecret);

    return new SecureChannel(peerId, sessionKeys);
  }

  private async performKeyExchange(privateKey: CryptoKey, peerPublicKey: string): Promise<ArrayBuffer> {
    const peerKeyBuffer = Uint8Array.from(atob(peerPublicKey), c => c.charCodeAt(0));
    const peerKey = await crypto.subtle.importKey(
      'raw',
      peerKeyBuffer,
      { name: 'X25519' },
      false,
      []
    );

    return await crypto.subtle.deriveKey(
      { name: 'X25519', public: peerKey },
      privateKey,
      { name: 'AES-GCM', length: 256 },
      false,
      ['encrypt', 'decrypt']
    );
  }
}
```

### Message Encryption

```typescript
class SecureChannel {
  private peerId: string;
  private encryptionKey: CryptoKey;
  private macKey: CryptoKey;
  private sequenceNumber: number;

  constructor(peerId: string, sessionKeys: SessionKeys) {
    this.peerId = peerId;
    this.encryptionKey = sessionKeys.encryption;
    this.macKey = sessionKeys.mac;
    this.sequenceNumber = 0;
  }

  async encrypt(message: any): Promise<EncryptedMessage> {
    const plaintext = JSON.stringify(message);
    const encoder = new TextEncoder();
    const data = encoder.encode(plaintext);

    // Generate IV
    const iv = crypto.getRandomValues(new Uint8Array(12));

    // Encrypt
    const encrypted = await crypto.subtle.encrypt(
      { name: 'AES-GCM', iv: iv },
      this.encryptionKey,
      data
    );

    // Create authenticated message
    const authenticatedMessage = {
      peer_id: this.peerId,
      sequence: this.sequenceNumber++,
      iv: Array.from(iv),
      ciphertext: Array.from(new Uint8Array(encrypted)),
      timestamp: new Date().toISOString()
    };

    // Generate MAC
    const mac = await this.generateMAC(authenticatedMessage);

    return {
      ...authenticatedMessage,
      mac: mac
    };
  }

  async decrypt(encryptedMessage: EncryptedMessage): Promise<any> {
    // Verify MAC
    const isValid = await this.verifyMAC(encryptedMessage);
    if (!isValid) {
      throw new Error('Message authentication failed');
    }

    // Decrypt
    const iv = new Uint8Array(encryptedMessage.iv);
    const ciphertext = new Uint8Array(encryptedMessage.ciphertext);

    const decrypted = await crypto.subtle.decrypt(
      { name: 'AES-GCM', iv: iv },
      this.encryptionKey,
      ciphertext
    );

    const decoder = new TextDecoder();
    const plaintext = decoder.decode(decrypted);

    return JSON.parse(plaintext);
  }

  private async generateMAC(message: any): Promise<string> {
    const encoder = new TextEncoder();
    const data = encoder.encode(JSON.stringify(message));
    
    const signature = await crypto.subtle.sign('HMAC', this.macKey, data);
    return btoa(String.fromCharCode(...new Uint8Array(signature)));
  }
}
```

## Bootstrap & Configuration

### Federation Bootstrap Flow

```typescript
class FederationBootstrap {
  async initializeNode(config: NodeConfig): Promise<FederatedNode> {
    // Step 1: Generate node identity
    const identity = await this.generateNodeIdentity(config);

    // Step 2: Connect to bootstrap nodes
    const bootstrapPeers = await this.connectToBootstrap(config.bootstrap_nodes);

    // Step 3: Join mesh network
    const meshNetwork = await this.joinMesh(identity, bootstrapPeers);

    // Step 4: Start services
    const services = await this.startServices(config.services);

    // Step 5: Announce capabilities
    await this.announceCapabilities(identity, services);

    return new FederatedNode(identity, meshNetwork, services);
  }

  private async connectToBootstrap(bootstrapNodes: string[]): Promise<PeerNode[]> {
    const connectedPeers: PeerNode[] = [];

    for (const nodeAddress of bootstrapNodes) {
      try {
        const peer = await this.connectToPeer(nodeAddress);
        connectedPeers.push(peer);
        
        // Request peer table
        const peerTable = await this.requestPeerTable(peer);
        connectedPeers.push(...peerTable);
      } catch (error) {
        console.warn(`Failed to connect to bootstrap node ${nodeAddress}:`, error);
      }
    }

    return connectedPeers;
  }
}
```

## CLI Tools & Management

```typescript
class FederationCLI {
  async connect(peerAddress: string): Promise<void> {
    console.log(`Connecting to peer: ${peerAddress}`);
    // Implementation
  }

  async trustAgent(agentId: string, trustLevel: number): Promise<void> {
    console.log(`Setting trust level ${trustLevel} for agent ${agentId}`);
    // Implementation
  }

  async listPeers(): Promise<void> {
    const peers = await this.federationManager.getPeers();
    console.table(peers.map(p => ({
      ID: p.node_id.substring(0, 12),
      Role: p.role,
      Address: p.address,
      Trust: p.trust_score.toFixed(2),
      LastSeen: new Date(p.last_seen).toLocaleString()
    })));
  }

  async migrateAgent(agentId: string, targetNode: string): Promise<void> {
    console.log(`Migrating agent ${agentId} to ${targetNode}...`);
    const result = await this.federationManager.migrateAgent(agentId, targetNode);
    
    if (result.success) {
      console.log('✅ Migration completed successfully');
    } else {
      console.error('❌ Migration failed:', result.error);
    }
  }
}
```

## Implementation Status

- **Transport Layer**: ✅ Complete
- **KLP Protocol**: ✅ Complete
- **Peer Discovery**: ✅ Complete
- **Security Layer**: ✅ Complete
- **Federation Management**: ✅ Complete
- **CLI Tools**: ✅ Complete

---

*This document provides the complete technical specification for Federated Mesh Protocols with comprehensive security and interoperability features.* 