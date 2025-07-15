---
title: "Agent Communication Bus"
description: "Comprehensive local, networked, and mesh messaging architecture for agent-to-agent communication"
type: "architecture"
status: "future"
priority: "high"
last_updated: "2025-01-27"
related_docs:
  - "future/protocols/kind-link-protocol-core.md"
  - "future/agents/agent-scheduling-system.md"
  - "future/security/agent-trust-protocols.md"
implementation_status: "planned"
---

# Agent Communication Bus

## Agent Context
This document defines the complete Agent Communication Bus (ACB) architecture enabling secure, efficient communication between agents across local systems, networks, and mesh topologies. Essential for agents implementing inter-agent messaging, event coordination, and distributed system communication.

## Communication Bus Overview

The Agent Communication Bus provides a unified messaging layer supporting agent communication across multiple transport mechanisms including local in-memory, networked connections, mesh topologies, and internet protocols. All communication is secured through the KindLink Protocol with comprehensive event routing and subscription management.

## Core Architecture Components

### ACB Core Dispatcher

```typescript
interface CommunicationBus {
  dispatcher: MessageDispatcher;
  event_bus: LocalEventBus;
  network_relay: NetworkedMessageRelay;
  mesh_layer: MeshLayerModule;
  bridge_adapters: BridgeAdapter[];
  security_manager: CommunicationSecurityManager;
}

interface MessageDispatcher {
  routeMessage(message: ACBMessage): Promise<RoutingDecision>;
  registerAgent(agentId: string, capabilities: AgentCapabilities): Promise<void>;
  unregisterAgent(agentId: string): Promise<void>;
  getRoutingTable(): Promise<RoutingTable>;
  updateRoute(route: RouteUpdate): Promise<void>;
}

interface ACBMessage {
  id: string;
  sender: string;
  recipient: string | string[];
  message_type: MessageType;
  payload: any;
  timestamp: Date;
  ttl: number;
  priority: MessagePriority;
  routing_hints?: RoutingHint[];
  security_context?: SecurityContext;
}

type MessageType = 
  | 'event.emit'
  | 'event.subscribe'
  | 'query.request'
  | 'query.response'
  | 'command.execute'
  | 'state.sync'
  | 'heartbeat'
  | 'announcement'
  | 'broadcast';

class ACBCoreDispatcher implements MessageDispatcher {
  private agents = new Map<string, AgentRegistration>();
  private routingTable: RoutingTable;
  private transports = new Map<string, Transport>();
  
  async routeMessage(message: ACBMessage): Promise<RoutingDecision> {
    // Determine optimal transport
    const transport = await this.selectTransport(message);
    
    // Check recipient availability
    const recipientStatus = await this.checkRecipientStatus(message.recipient);
    
    if (!recipientStatus.available) {
      return {
        action: 'queue',
        reason: 'Recipient unavailable',
        retry_after: recipientStatus.retry_after
      };
    }
    
    // Apply security policies
    const securityCheck = await this.validateMessageSecurity(message);
    if (!securityCheck.allowed) {
      return {
        action: 'block',
        reason: securityCheck.reason
      };
    }
    
    // Route the message
    try {
      await transport.sendMessage(message);
      return {
        action: 'delivered',
        transport_used: transport.name,
        delivery_time: Date.now()
      };
    } catch (error) {
      return {
        action: 'failed',
        reason: error.message,
        retry_possible: this.isRetryableError(error)
      };
    }
  }
  
  async registerAgent(agentId: string, capabilities: AgentCapabilities): Promise<void> {
    const registration: AgentRegistration = {
      agent_id: agentId,
      capabilities,
      registered_at: new Date(),
      last_heartbeat: new Date(),
      status: 'active',
      transport_preferences: capabilities.transport_preferences || [],
      subscriptions: new Set()
    };
    
    this.agents.set(agentId, registration);
    
    // Update routing table
    await this.updateRoutingTable(agentId, registration);
    
    // Announce agent registration
    await this.announceAgentRegistration(registration);
  }
}
```

### Local Event Bus

```typescript
interface LocalEventBus {
  publish(event: LocalEvent): Promise<void>;
  subscribe(pattern: string, handler: EventHandler): Promise<SubscriptionId>;
  unsubscribe(subscriptionId: SubscriptionId): Promise<void>;
  getSubscriptions(agentId: string): Promise<Subscription[]>;
}

interface LocalEvent {
  event_id: string;
  event_type: string;
  source_agent: string;
  data: any;
  timestamp: Date;
  tags: string[];
  correlation_id?: string;
}

class FastLocalEventBus implements LocalEventBus {
  private subscriptions = new Map<string, Subscription[]>();
  private eventHistory: LocalEvent[] = [];
  private maxHistorySize = 1000;
  
  async publish(event: LocalEvent): Promise<void> {
    // Add to history
    this.eventHistory.push(event);
    if (this.eventHistory.length > this.maxHistorySize) {
      this.eventHistory.shift();
    }
    
    // Find matching subscriptions
    const matchingSubscriptions = this.findMatchingSubscriptions(event.event_type);
    
    // Deliver to subscribers
    const deliveryPromises = matchingSubscriptions.map(async (subscription) => {
      try {
        await subscription.handler(event);
        subscription.delivery_count++;
        subscription.last_delivery = new Date();
      } catch (error) {
        subscription.error_count++;
        console.error(`Event delivery failed for subscription ${subscription.id}:`, error);
      }
    });
    
    await Promise.allSettled(deliveryPromises);
  }
  
  async subscribe(pattern: string, handler: EventHandler): Promise<SubscriptionId> {
    const subscription: Subscription = {
      id: this.generateSubscriptionId(),
      pattern,
      handler,
      created_at: new Date(),
      delivery_count: 0,
      error_count: 0,
      active: true
    };
    
    const patternSubscriptions = this.subscriptions.get(pattern) || [];
    patternSubscriptions.push(subscription);
    this.subscriptions.set(pattern, patternSubscriptions);
    
    return subscription.id;
  }
  
  private findMatchingSubscriptions(eventType: string): Subscription[] {
    const matching: Subscription[] = [];
    
    for (const [pattern, subscriptions] of this.subscriptions) {
      if (this.matchesPattern(eventType, pattern)) {
        matching.push(...subscriptions.filter(s => s.active));
      }
    }
    
    return matching;
  }
  
  private matchesPattern(eventType: string, pattern: string): boolean {
    // Support wildcard patterns
    if (pattern === '*') return true;
    if (pattern.endsWith('*')) {
      return eventType.startsWith(pattern.slice(0, -1));
    }
    return eventType === pattern;
  }
}
```

### Networked Message Relay

```typescript
interface NetworkedMessageRelay {
  sendMessage(message: ACBMessage, destination: NetworkDestination): Promise<void>;
  receiveMessage(message: ACBMessage): Promise<void>;
  establishConnection(endpoint: NetworkEndpoint): Promise<Connection>;
  discoverPeers(): Promise<PeerInfo[]>;
}

interface NetworkDestination {
  type: 'direct' | 'broadcast' | 'multicast';
  addresses: string[];
  transport: 'websocket' | 'http' | 'tcp' | 'udp';
  security_requirements: SecurityRequirements;
}

interface Connection {
  id: string;
  endpoint: NetworkEndpoint;
  status: ConnectionStatus;
  created_at: Date;
  last_activity: Date;
  message_count: number;
  error_count: number;
}

class NetworkMessageRelay implements NetworkedMessageRelay {
  private connections = new Map<string, Connection>();
  private discoveryService: PeerDiscoveryService;
  private securityManager: NetworkSecurityManager;
  
  async sendMessage(message: ACBMessage, destination: NetworkDestination): Promise<void> {
    // Select best connection for destination
    const connection = await this.selectConnection(destination);
    
    // Encrypt message if required
    const secureMessage = await this.securityManager.encryptMessage(
      message,
      destination.security_requirements
    );
    
    // Send via transport
    switch (destination.transport) {
      case 'websocket':
        await this.sendViaWebSocket(secureMessage, connection);
        break;
      case 'http':
        await this.sendViaHTTP(secureMessage, connection);
        break;
      case 'tcp':
        await this.sendViaTCP(secureMessage, connection);
        break;
      case 'udp':
        await this.sendViaUDP(secureMessage, connection);
        break;
      default:
        throw new Error(`Unsupported transport: ${destination.transport}`);
    }
    
    // Update connection statistics
    connection.message_count++;
    connection.last_activity = new Date();
  }
  
  async establishConnection(endpoint: NetworkEndpoint): Promise<Connection> {
    // Check if connection already exists
    const existingConnection = this.connections.get(endpoint.address);
    if (existingConnection && existingConnection.status === 'connected') {
      return existingConnection;
    }
    
    // Create new connection
    const connection: Connection = {
      id: this.generateConnectionId(),
      endpoint,
      status: 'connecting',
      created_at: new Date(),
      last_activity: new Date(),
      message_count: 0,
      error_count: 0
    };
    
    try {
      // Perform handshake
      await this.performHandshake(connection);
      
      // Establish secure channel
      await this.securityManager.establishSecureChannel(connection);
      
      connection.status = 'connected';
      this.connections.set(endpoint.address, connection);
      
      return connection;
    } catch (error) {
      connection.status = 'failed';
      connection.error_count++;
      throw error;
    }
  }
  
  async discoverPeers(): Promise<PeerInfo[]> {
    const discoveryMethods = [
      this.discoverViaMDNS(),
      this.discoverViaRegistry(),
      this.discoverViaBroadcast()
    ];
    
    const results = await Promise.allSettled(discoveryMethods);
    const peers: PeerInfo[] = [];
    
    for (const result of results) {
      if (result.status === 'fulfilled') {
        peers.push(...result.value);
      }
    }
    
    // Deduplicate and validate peers
    return this.deduplicatePeers(peers);
  }
}
```

### Mesh Layer Module

```typescript
interface MeshLayerModule {
  initialize(config: MeshConfig): Promise<void>;
  sendMeshMessage(message: ACBMessage, destination: MeshDestination): Promise<void>;
  receiveMeshMessage(message: ACBMessage): Promise<void>;
  getMeshTopology(): Promise<MeshTopology>;
  announcePresence(): Promise<void>;
}

interface MeshConfig {
  transport: 'reticulum' | 'lora' | 'bluetooth' | 'wifi_direct';
  interface: string;
  encryption_enabled: boolean;
  mesh_id: string;
  routing_algorithm: 'flooding' | 'dsdv' | 'aodv' | 'olsr';
}

interface MeshDestination {
  node_id: string;
  hop_limit: number;
  reliability_required: boolean;
}

class ReticulumMeshLayer implements MeshLayerModule {
  private reticulumInterface: ReticulumInterface;
  private meshNodes = new Map<string, MeshNode>();
  private routingTable: MeshRoutingTable;
  
  async initialize(config: MeshConfig): Promise<void> {
    // Initialize Reticulum interface
    this.reticulumInterface = new ReticulumInterface(config.interface);
    await this.reticulumInterface.initialize();
    
    // Set up mesh routing
    this.routingTable = new MeshRoutingTable(config.routing_algorithm);
    
    // Start mesh discovery
    await this.startMeshDiscovery();
    
    // Announce our presence
    await this.announcePresence();
  }
  
  async sendMeshMessage(message: ACBMessage, destination: MeshDestination): Promise<void> {
    // Find route to destination
    const route = await this.routingTable.findRoute(destination.node_id);
    
    if (!route) {
      // Initiate route discovery
      await this.initiateRouteDiscovery(destination.node_id);
      throw new Error(`No route to destination: ${destination.node_id}`);
    }
    
    // Prepare mesh packet
    const meshPacket: MeshPacket = {
      source: this.getNodeId(),
      destination: destination.node_id,
      next_hop: route.next_hop,
      hop_count: 0,
      max_hops: destination.hop_limit,
      payload: message,
      timestamp: Date.now(),
      sequence_number: this.getNextSequenceNumber()
    };
    
    // Send via Reticulum
    await this.reticulumInterface.sendPacket(meshPacket);
  }
  
  async getMeshTopology(): Promise<MeshTopology> {
    const nodes = Array.from(this.meshNodes.values());
    const links = await this.routingTable.getAllLinks();
    
    return {
      nodes,
      links,
      total_nodes: nodes.length,
      connected_nodes: nodes.filter(n => n.status === 'connected').length,
      mesh_diameter: this.calculateMeshDiameter(nodes, links),
      last_updated: new Date()
    };
  }
  
  private async startMeshDiscovery(): Promise<void> {
    // Set up periodic announcements
    setInterval(async () => {
      await this.announcePresence();
    }, 30000); // Every 30 seconds
    
    // Listen for announcements from other nodes
    this.reticulumInterface.onAnnouncement((announcement) => {
      this.handleNodeAnnouncement(announcement);
    });
  }
}
```

### Bridge Adapters

```typescript
interface BridgeAdapter {
  name: string;
  protocol: string;
  connect(): Promise<void>;
  disconnect(): Promise<void>;
  sendMessage(message: ACBMessage): Promise<void>;
  onMessage(handler: MessageHandler): void;
  getStatus(): AdapterStatus;
}

interface AdapterStatus {
  connected: boolean;
  last_activity: Date;
  message_count: number;
  error_count: number;
  latency: number;
}

class MQTTBridgeAdapter implements BridgeAdapter {
  name = 'mqtt_bridge';
  protocol = 'mqtt';
  
  private client: MQTTClient;
  private messageHandlers: MessageHandler[] = [];
  private status: AdapterStatus;
  
  async connect(): Promise<void> {
    this.client = new MQTTClient(this.config);
    
    await this.client.connect();
    
    // Subscribe to agent topics
    await this.client.subscribe('agents/+/messages');
    await this.client.subscribe('agents/broadcast');
    
    // Set up message handling
    this.client.onMessage((topic, payload) => {
      this.handleMQTTMessage(topic, payload);
    });
    
    this.status = {
      connected: true,
      last_activity: new Date(),
      message_count: 0,
      error_count: 0,
      latency: 0
    };
  }
  
  async sendMessage(message: ACBMessage): Promise<void> {
    const topic = this.buildMQTTTopic(message);
    const payload = JSON.stringify(message);
    
    const startTime = Date.now();
    await this.client.publish(topic, payload);
    
    this.status.message_count++;
    this.status.last_activity = new Date();
    this.status.latency = Date.now() - startTime;
  }
  
  private handleMQTTMessage(topic: string, payload: Buffer): void {
    try {
      const message: ACBMessage = JSON.parse(payload.toString());
      
      // Validate message format
      if (this.validateMessage(message)) {
        // Notify handlers
        this.messageHandlers.forEach(handler => {
          handler(message);
        });
      }
    } catch (error) {
      this.status.error_count++;
      console.error('Failed to handle MQTT message:', error);
    }
  }
}
```

### Security Framework

```typescript
interface CommunicationSecurityManager {
  validateMessage(message: ACBMessage): Promise<SecurityValidationResult>;
  encryptMessage(message: ACBMessage, requirements: SecurityRequirements): Promise<EncryptedMessage>;
  decryptMessage(encrypted: EncryptedMessage): Promise<ACBMessage>;
  establishSecureChannel(connection: Connection): Promise<SecureChannel>;
  verifyAgentIdentity(agentId: string): Promise<IdentityVerificationResult>;
}

interface SecurityValidationResult {
  valid: boolean;
  trust_level: TrustLevel;
  violations: SecurityViolation[];
  recommendations: string[];
}

interface SecurityRequirements {
  encryption_required: boolean;
  signature_required: boolean;
  minimum_trust_level: TrustLevel;
  allowed_transports: string[];
}

class ACBSecurityManager implements CommunicationSecurityManager {
  private trustManager: TrustManager;
  private cryptoProvider: CryptographicProvider;
  
  async validateMessage(message: ACBMessage): Promise<SecurityValidationResult> {
    const violations: SecurityViolation[] = [];
    
    // Verify sender identity
    const senderIdentity = await this.verifyAgentIdentity(message.sender);
    if (!senderIdentity.valid) {
      violations.push({
        type: 'invalid_sender',
        severity: 'high',
        description: 'Sender identity could not be verified'
      });
    }
    
    // Check trust level
    const trustLevel = await this.trustManager.getTrustLevel(message.sender);
    
    // Validate message signature if present
    if (message.security_context?.signature) {
      const signatureValid = await this.cryptoProvider.verifySignature(
        message,
        message.security_context.signature,
        senderIdentity.public_key
      );
      
      if (!signatureValid) {
        violations.push({
          type: 'invalid_signature',
          severity: 'critical',
          description: 'Message signature verification failed'
        });
      }
    }
    
    // Check for suspicious content
    const contentAnalysis = await this.analyzeMessageContent(message);
    if (contentAnalysis.suspicious) {
      violations.push({
        type: 'suspicious_content',
        severity: 'medium',
        description: contentAnalysis.reason
      });
    }
    
    return {
      valid: violations.length === 0,
      trust_level: trustLevel,
      violations,
      recommendations: this.generateSecurityRecommendations(violations)
    };
  }
  
  async encryptMessage(
    message: ACBMessage,
    requirements: SecurityRequirements
  ): Promise<EncryptedMessage> {
    if (!requirements.encryption_required) {
      return { encrypted: false, message };
    }
    
    // Get recipient public key
    const recipientKey = await this.getRecipientPublicKey(message.recipient);
    
    // Encrypt payload
    const encryptedPayload = await this.cryptoProvider.encrypt(
      JSON.stringify(message.payload),
      recipientKey
    );
    
    // Create encrypted message
    const encryptedMessage: EncryptedMessage = {
      encrypted: true,
      message: {
        ...message,
        payload: null // Remove original payload
      },
      encrypted_payload: encryptedPayload,
      encryption_algorithm: this.cryptoProvider.getAlgorithm(),
      recipient_key_fingerprint: this.cryptoProvider.getKeyFingerprint(recipientKey)
    };
    
    // Sign if required
    if (requirements.signature_required) {
      const signature = await this.cryptoProvider.sign(encryptedMessage, message.sender);
      encryptedMessage.signature = signature;
    }
    
    return encryptedMessage;
  }
}
```

## Configuration and Deployment

### Communication Bus Configuration

```typescript
interface ACBConfig {
  enabled: boolean;
  transports: TransportConfig[];
  security: SecurityConfig;
  performance: PerformanceConfig;
  discovery: DiscoveryConfig;
}

interface TransportConfig {
  name: string;
  type: 'local' | 'websocket' | 'tcp' | 'udp' | 'mesh' | 'bridge';
  enabled: boolean;
  priority: number;
  config: any;
}

const defaultACBConfig: ACBConfig = {
  enabled: true,
  transports: [
    {
      name: 'local',
      type: 'local',
      enabled: true,
      priority: 1,
      config: {
        max_history: 1000,
        cleanup_interval: 60000
      }
    },
    {
      name: 'websocket',
      type: 'websocket',
      enabled: true,
      priority: 2,
      config: {
        host: '0.0.0.0',
        port: 8593,
        tls: true,
        max_connections: 100
      }
    },
    {
      name: 'mesh_reticulum',
      type: 'mesh',
      enabled: false,
      priority: 3,
      config: {
        interface: 'ttyUSB0',
        mesh_id: 'kai_mesh',
        routing_algorithm: 'aodv'
      }
    }
  ],
  security: {
    encryption_enabled: true,
    signature_required: true,
    trust_verification: true,
    replay_protection: true
  },
  performance: {
    message_batching: true,
    compression_enabled: true,
    max_message_size: 1048576, // 1MB
    connection_pooling: true
  },
  discovery: {
    mdns_enabled: true,
    registry_enabled: true,
    broadcast_enabled: false,
    discovery_interval: 30000
  }
};
```

## Related Documentation

- [Kind Link Protocol Core](../protocols/kind-link-protocol-core.md)
- [Agent Scheduling System](../agents/agent-scheduling-system.md)
- [Agent Trust Protocols](../security/agent-trust-protocols.md)
- [Agent Security Framework](../security/agent-security-framework.md)

---

*This communication bus provides the foundation for seamless agent interaction across diverse network topologies, enabling distributed intelligence while maintaining security and performance standards.* 