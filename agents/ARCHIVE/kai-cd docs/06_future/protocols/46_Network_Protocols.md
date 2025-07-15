---
title: "Network Protocols and Distributed Systems"
type: "protocol_specification"
status: "future_vision"
priority: "critical"
last_updated: "2024-01-20"
relates_to: ["02_agent-communication-protocols.md", "01_klp-specification.md"]
version: "1.0.0"
---

# Network Protocols and Distributed Systems

> **Agent Context**: This document provides the complete technical specification for network protocols, distributed system architecture, and mesh networking capabilities in the kOS ecosystem. It defines the transport layers, routing algorithms, peer discovery mechanisms, and resilience patterns that enable reliable communication across heterogeneous network environments. Implementation teams must follow these specifications exactly to ensure network interoperability and performance.

## Overview

The Network Protocols define the foundational networking layer for the kOS distributed system. This includes mesh networking protocols, peer discovery mechanisms, routing algorithms, and transport abstractions that enable agents to communicate reliably across diverse network topologies including local networks, mesh networks, and internet-based connections.

**Implementation Status**: Future vision for kOS distributed networking
**Current Foundation**: HTTP-based service calls in Kai-CD
**Evolution Path**: HTTP services → WebSocket connections → Mesh networking → Distributed protocols

## Network Architecture Overview

### Network Stack

```typescript
// Future: src/kos/network/NetworkStack.ts
export interface NetworkStack {
  application: ApplicationProtocol;
  session: SessionProtocol;
  transport: TransportProtocol;
  network: NetworkProtocol;
  dataLink: DataLinkProtocol;
  physical: PhysicalProtocol;
}

export class KindNetworkStack implements NetworkStack {
  private protocols: Map<string, Protocol> = new Map();
  private routingEngine: RoutingEngine;
  private peerManager: PeerManager;
  private meshManager: MeshManager;
  private connectionPool: ConnectionPool;

  constructor(config: NetworkConfig) {
    this.initializeProtocols(config);
    this.setupRouting(config.routing);
    this.setupPeerManagement(config.peers);
    this.setupMeshNetworking(config.mesh);
  }

  async initializeProtocols(config: NetworkConfig): Promise<void> {
    // Initialize protocol layers
    this.protocols.set('physical', new PhysicalProtocol(config.physical));
    this.protocols.set('dataLink', new DataLinkProtocol(config.dataLink));
    this.protocols.set('network', new NetworkProtocol(config.network));
    this.protocols.set('transport', new TransportProtocol(config.transport));
    this.protocols.set('session', new SessionProtocol(config.session));
    this.protocols.set('application', new ApplicationProtocol(config.application));

    // Initialize supporting services
    this.routingEngine = new RoutingEngine(config.routing);
    this.peerManager = new PeerManager(config.peers);
    this.meshManager = new MeshManager(config.mesh);
    this.connectionPool = new ConnectionPool(config.connections);

    // Start protocol services
    await this.startProtocolServices();
  }

  async sendPacket(
    destination: NetworkAddress,
    payload: NetworkPayload,
    options: SendOptions = {}
  ): Promise<SendResult> {
    try {
      // Create network packet
      const packet: NetworkPacket = {
        id: crypto.randomUUID(),
        version: NETWORK_VERSION,
        timestamp: Date.now(),
        source: this.getLocalAddress(),
        destination,
        payload,
        options,
        route: [],
        metadata: {
          hops: 0,
          ttl: options.ttl || DEFAULT_TTL,
          priority: options.priority || PacketPriority.NORMAL
        }
      };

      // Find route to destination
      const route = await this.routingEngine.findRoute(destination, options);
      if (!route) {
        throw new NetworkError(`No route to ${destination.toString()}`);
      }

      // Send packet through network stack
      return await this.transmitPacket(packet, route);

    } catch (error) {
      return {
        success: false,
        error: error.message,
        timestamp: Date.now()
      };
    }
  }

  async receivePacket(packet: NetworkPacket): Promise<void> {
    try {
      // Validate packet structure
      await this.validatePacket(packet);

      // Check if packet is for us
      if (this.isLocalDestination(packet.destination)) {
        await this.processLocalPacket(packet);
      } else {
        // Forward packet
        await this.forwardPacket(packet);
      }

    } catch (error) {
      await this.handlePacketError(packet, error);
    }
  }

  private async transmitPacket(
    packet: NetworkPacket,
    route: NetworkRoute
  ): Promise<SendResult> {
    // Add route information
    packet.route = route.hops;

    // Pass through protocol stack
    let processedPacket = packet;
    
    for (const [layerName, protocol] of this.protocols) {
      processedPacket = await protocol.processOutbound(processedPacket);
    }

    // Send via appropriate transport
    const transport = this.getTransport(route.transport);
    const result = await transport.send(processedPacket);

    return {
      success: true,
      packetId: packet.id,
      route: route.id,
      timestamp: Date.now(),
      result
    };
  }
}
```

## Mesh Networking Implementation

### Mesh Manager

```typescript
// Future: src/kos/network/mesh/MeshManager.ts
export class MeshManager {
  private meshTopology: MeshTopology;
  private nodeRegistry: NodeRegistry;
  private gossipProtocol: GossipProtocol;
  private routingProtocol: MeshRoutingProtocol;
  private discoveryProtocol: PeerDiscoveryProtocol;

  constructor(config: MeshConfig) {
    this.meshTopology = new MeshTopology(config.topology);
    this.nodeRegistry = new NodeRegistry(config.registry);
    this.gossipProtocol = new GossipProtocol(config.gossip);
    this.routingProtocol = new MeshRoutingProtocol(config.routing);
    this.discoveryProtocol = new PeerDiscoveryProtocol(config.discovery);
  }

  async initializeMesh(): Promise<void> {
    // Initialize local node
    await this.initializeLocalNode();

    // Start discovery
    await this.discoveryProtocol.startDiscovery();

    // Start gossip protocol
    await this.gossipProtocol.start();

    // Initialize routing
    await this.routingProtocol.initialize();

    // Start mesh maintenance
    await this.startMeshMaintenance();
  }

  async joinMesh(bootstrapNodes: NodeAddress[]): Promise<JoinResult> {
    try {
      // Attempt to connect to bootstrap nodes
      const connections: MeshConnection[] = [];
      
      for (const nodeAddress of bootstrapNodes) {
        try {
          const connection = await this.connectToNode(nodeAddress);
          connections.push(connection);
          
          // Exchange node information
          await this.exchangeNodeInfo(connection);
          
          // Request mesh topology
          const topology = await this.requestTopology(connection);
          await this.meshTopology.merge(topology);
          
        } catch (error) {
          console.warn(`Failed to connect to bootstrap node ${nodeAddress}:`, error);
        }
      }

      if (connections.length === 0) {
        throw new Error('Failed to connect to any bootstrap nodes');
      }

      // Announce presence to mesh
      await this.announceMeshJoin();

      // Start participating in mesh protocols
      await this.startMeshParticipation();

      return {
        success: true,
        connectedNodes: connections.length,
        meshSize: this.meshTopology.getNodeCount(),
        timestamp: Date.now()
      };

    } catch (error) {
      return {
        success: false,
        error: error.message,
        timestamp: Date.now()
      };
    }
  }

  async leaveMesh(): Promise<void> {
    // Announce departure
    await this.announceMeshLeave();

    // Stop mesh protocols
    await this.stopMeshParticipation();

    // Close connections
    await this.closeAllConnections();

    // Clear topology
    this.meshTopology.clear();
  }

  async routePacket(
    packet: MeshPacket,
    destination: NodeAddress
  ): Promise<RoutingResult> {
    // Check if destination is directly connected
    const directConnection = this.getDirectConnection(destination);
    if (directConnection) {
      return await this.sendDirect(packet, directConnection);
    }

    // Find route through mesh
    const route = await this.routingProtocol.findRoute(destination);
    if (!route) {
      throw new RoutingError(`No route to ${destination.toString()}`);
    }

    // Send via route
    return await this.sendViaRoute(packet, route);
  }

  private async sendViaRoute(
    packet: MeshPacket,
    route: MeshRoute
  ): Promise<RoutingResult> {
    const nextHop = route.hops[0];
    const connection = this.getDirectConnection(nextHop.address);
    
    if (!connection) {
      throw new RoutingError(`No connection to next hop ${nextHop.address}`);
    }

    // Update packet routing information
    packet.route = route.hops;
    packet.metadata.hops += 1;
    packet.metadata.ttl -= 1;

    // Check TTL
    if (packet.metadata.ttl <= 0) {
      throw new RoutingError('Packet TTL exceeded');
    }

    // Forward packet
    return await connection.send(packet);
  }

  async handleMeshPacket(packet: MeshPacket): Promise<void> {
    // Check if packet is for local node
    if (this.isLocalDestination(packet.destination)) {
      await this.processLocalMeshPacket(packet);
      return;
    }

    // Forward packet if TTL allows
    if (packet.metadata.ttl > 0) {
      await this.forwardMeshPacket(packet);
    } else {
      // Drop packet and notify sender if possible
      await this.sendTTLExceeded(packet);
    }
  }

  private async forwardMeshPacket(packet: MeshPacket): Promise<void> {
    try {
      // Update routing information
      packet.metadata.hops += 1;
      packet.metadata.ttl -= 1;

      // Find next hop
      const route = await this.routingProtocol.findRoute(packet.destination);
      if (!route) {
        await this.sendDestinationUnreachable(packet);
        return;
      }

      // Forward to next hop
      await this.sendViaRoute(packet, route);

    } catch (error) {
      await this.sendRoutingError(packet, error);
    }
  }
}

export interface MeshPacket {
  id: string;
  version: string;
  timestamp: number;
  source: NodeAddress;
  destination: NodeAddress;
  payload: MeshPayload;
  route: RouteHop[];
  metadata: MeshMetadata;
  signature?: string;
}

export interface MeshMetadata {
  hops: number;
  ttl: number;
  priority: PacketPriority;
  type: MeshPacketType;
  flags: MeshPacketFlags;
}

export enum MeshPacketType {
  DATA = 'data',
  CONTROL = 'control',
  ROUTING = 'routing',
  DISCOVERY = 'discovery',
  HEARTBEAT = 'heartbeat'
}

export interface RouteHop {
  address: NodeAddress;
  transport: TransportType;
  latency?: number;
  reliability?: number;
}
```

### Peer Discovery Protocol

```typescript
// Future: src/kos/network/discovery/PeerDiscoveryProtocol.ts
export class PeerDiscoveryProtocol {
  private discoveryMethods: DiscoveryMethod[];
  private peerCache: PeerCache;
  private announcementManager: AnnouncementManager;
  private discoveryScheduler: DiscoveryScheduler;

  constructor(config: DiscoveryConfig) {
    this.discoveryMethods = this.initializeDiscoveryMethods(config);
    this.peerCache = new PeerCache(config.cache);
    this.announcementManager = new AnnouncementManager(config.announcements);
    this.discoveryScheduler = new DiscoveryScheduler(config.scheduling);
  }

  async startDiscovery(): Promise<void> {
    // Start all discovery methods
    for (const method of this.discoveryMethods) {
      await method.start();
    }

    // Start periodic announcements
    await this.announcementManager.start();

    // Start discovery scheduling
    await this.discoveryScheduler.start();
  }

  async discoverPeers(criteria: DiscoveryCriteria): Promise<PeerInfo[]> {
    const discoveredPeers: PeerInfo[] = [];

    // Try each discovery method
    for (const method of this.discoveryMethods) {
      if (method.supports(criteria)) {
        try {
          const peers = await method.discover(criteria);
          discoveredPeers.push(...peers);
        } catch (error) {
          console.warn(`Discovery method ${method.name} failed:`, error);
        }
      }
    }

    // Deduplicate and validate peers
    const uniquePeers = this.deduplicatePeers(discoveredPeers);
    const validatedPeers = await this.validatePeers(uniquePeers);

    // Cache discovered peers
    await this.peerCache.store(validatedPeers);

    return validatedPeers;
  }

  async announceSelf(): Promise<void> {
    const announcement: PeerAnnouncement = {
      nodeId: this.getNodeId(),
      nodeInfo: await this.getNodeInfo(),
      capabilities: await this.getCapabilities(),
      endpoints: await this.getEndpoints(),
      timestamp: Date.now(),
      signature: await this.signAnnouncement()
    };

    // Broadcast announcement via all methods
    for (const method of this.discoveryMethods) {
      if (method.supportsAnnouncements()) {
        try {
          await method.announce(announcement);
        } catch (error) {
          console.warn(`Announcement via ${method.name} failed:`, error);
        }
      }
    }
  }

  private initializeDiscoveryMethods(config: DiscoveryConfig): DiscoveryMethod[] {
    const methods: DiscoveryMethod[] = [];

    // mDNS Discovery
    if (config.mdns?.enabled) {
      methods.push(new MDNSDiscovery(config.mdns));
    }

    // DHT Discovery
    if (config.dht?.enabled) {
      methods.push(new DHTDiscovery(config.dht));
    }

    // Bluetooth Discovery
    if (config.bluetooth?.enabled) {
      methods.push(new BluetoothDiscovery(config.bluetooth));
    }

    // LoRa Discovery
    if (config.lora?.enabled) {
      methods.push(new LoRaDiscovery(config.lora));
    }

    // Bootstrap Discovery
    if (config.bootstrap?.enabled) {
      methods.push(new BootstrapDiscovery(config.bootstrap));
    }

    // Gossip Discovery
    if (config.gossip?.enabled) {
      methods.push(new GossipDiscovery(config.gossip));
    }

    return methods;
  }
}

// mDNS Discovery Implementation
export class MDNSDiscovery implements DiscoveryMethod {
  private mdns: MDNSService;
  private serviceType: string;
  private domain: string;

  constructor(config: MDNSConfig) {
    this.mdns = new MDNSService(config);
    this.serviceType = config.serviceType || '_kos._tcp';
    this.domain = config.domain || 'local';
  }

  async start(): Promise<void> {
    await this.mdns.start();
    
    // Register our service
    await this.mdns.register({
      name: this.getServiceName(),
      type: this.serviceType,
      domain: this.domain,
      port: this.getPort(),
      txt: this.getTxtRecord()
    });

    // Start browsing for peers
    await this.mdns.browse(this.serviceType, this.domain);
  }

  async discover(criteria: DiscoveryCriteria): Promise<PeerInfo[]> {
    const services = await this.mdns.query(this.serviceType, this.domain);
    const peers: PeerInfo[] = [];

    for (const service of services) {
      try {
        const peerInfo = await this.parseMDNSService(service);
        if (this.matchesCriteria(peerInfo, criteria)) {
          peers.push(peerInfo);
        }
      } catch (error) {
        console.warn(`Failed to parse mDNS service:`, error);
      }
    }

    return peers;
  }

  async announce(announcement: PeerAnnouncement): Promise<void> {
    // Update TXT record with announcement data
    const txtRecord = this.createTxtRecord(announcement);
    
    await this.mdns.updateService({
      name: this.getServiceName(),
      type: this.serviceType,
      domain: this.domain,
      txt: txtRecord
    });
  }

  supports(criteria: DiscoveryCriteria): boolean {
    // mDNS supports local network discovery
    return criteria.scope === DiscoveryScope.LOCAL || 
           criteria.scope === DiscoveryScope.LAN;
  }

  supportsAnnouncements(): boolean {
    return true;
  }

  get name(): string {
    return 'mDNS';
  }

  private async parseMDNSService(service: MDNSServiceInfo): Promise<PeerInfo> {
    const txtData = this.parseTxtRecord(service.txt);
    
    return {
      nodeId: txtData.nodeId,
      addresses: [
        {
          type: AddressType.IPV4,
          address: service.address,
          port: service.port
        }
      ],
      capabilities: txtData.capabilities?.split(',') || [],
      metadata: {
        discoveryMethod: 'mDNS',
        lastSeen: Date.now(),
        ...txtData
      }
    };
  }
}
```

## Transport Protocols

### Transport Manager

```typescript
// Future: src/kos/network/transport/TransportManager.ts
export class TransportManager {
  private transports: Map<TransportType, Transport> = new Map();
  private connectionManager: ConnectionManager;
  private loadBalancer: TransportLoadBalancer;
  private failoverManager: TransportFailoverManager;

  constructor(config: TransportConfig) {
    this.initializeTransports(config);
    this.connectionManager = new ConnectionManager(config.connections);
    this.loadBalancer = new TransportLoadBalancer(config.loadBalancing);
    this.failoverManager = new TransportFailoverManager(config.failover);
  }

  private initializeTransports(config: TransportConfig): void {
    // WebSocket Transport
    if (config.websocket?.enabled) {
      this.transports.set(
        TransportType.WEBSOCKET,
        new WebSocketTransport(config.websocket)
      );
    }

    // WebRTC Transport
    if (config.webrtc?.enabled) {
      this.transports.set(
        TransportType.WEBRTC,
        new WebRTCTransport(config.webrtc)
      );
    }

    // HTTP Transport
    if (config.http?.enabled) {
      this.transports.set(
        TransportType.HTTP,
        new HTTPTransport(config.http)
      );
    }

    // TCP Transport
    if (config.tcp?.enabled) {
      this.transports.set(
        TransportType.TCP,
        new TCPTransport(config.tcp)
      );
    }

    // UDP Transport
    if (config.udp?.enabled) {
      this.transports.set(
        TransportType.UDP,
        new UDPTransport(config.udp)
      );
    }

    // LoRa Transport
    if (config.lora?.enabled) {
      this.transports.set(
        TransportType.LORA,
        new LoRaTransport(config.lora)
      );
    }

    // Bluetooth Transport
    if (config.bluetooth?.enabled) {
      this.transports.set(
        TransportType.BLUETOOTH,
        new BluetoothTransport(config.bluetooth)
      );
    }
  }

  async sendPacket(
    packet: NetworkPacket,
    transportType: TransportType,
    endpoint: TransportEndpoint
  ): Promise<TransportResult> {
    const transport = this.transports.get(transportType);
    if (!transport) {
      throw new Error(`Transport ${transportType} not available`);
    }

    try {
      // Get or create connection
      const connection = await this.connectionManager.getConnection(
        transportType,
        endpoint
      );

      // Send packet
      const result = await transport.send(packet, connection);

      // Update connection metrics
      await this.connectionManager.updateMetrics(connection.id, result);

      return result;

    } catch (error) {
      // Handle transport failure
      await this.failoverManager.handleTransportFailure(
        transportType,
        endpoint,
        error
      );
      
      throw error;
    }
  }

  async createConnection(
    transportType: TransportType,
    endpoint: TransportEndpoint,
    options: ConnectionOptions = {}
  ): Promise<TransportConnection> {
    const transport = this.transports.get(transportType);
    if (!transport) {
      throw new Error(`Transport ${transportType} not available`);
    }

    const connection = await transport.connect(endpoint, options);
    
    // Register connection
    await this.connectionManager.registerConnection(connection);

    // Setup connection monitoring
    this.setupConnectionMonitoring(connection);

    return connection;
  }

  private setupConnectionMonitoring(connection: TransportConnection): void {
    // Monitor connection health
    connection.on('error', async (error) => {
      await this.handleConnectionError(connection, error);
    });

    connection.on('close', async () => {
      await this.handleConnectionClose(connection);
    });

    connection.on('data', async (data) => {
      await this.handleConnectionData(connection, data);
    });

    // Start heartbeat if supported
    if (connection.supportsHeartbeat()) {
      this.startHeartbeat(connection);
    }
  }
}

// WebSocket Transport Implementation
export class WebSocketTransport implements Transport {
  private config: WebSocketConfig;
  private connections: Map<string, WebSocketConnection> = new Map();

  constructor(config: WebSocketConfig) {
    this.config = config;
  }

  async connect(
    endpoint: TransportEndpoint,
    options: ConnectionOptions = {}
  ): Promise<WebSocketConnection> {
    const url = this.buildWebSocketURL(endpoint);
    const ws = new WebSocket(url, options.protocols);

    return new Promise((resolve, reject) => {
      const connection = new WebSocketConnection(ws, endpoint);

      ws.onopen = () => {
        this.connections.set(connection.id, connection);
        resolve(connection);
      };

      ws.onerror = (error) => {
        reject(new TransportError(`WebSocket connection failed: ${error}`));
      };

      ws.onclose = () => {
        this.connections.delete(connection.id);
      };

      ws.onmessage = (event) => {
        connection.handleMessage(event.data);
      };
    });
  }

  async send(
    packet: NetworkPacket,
    connection: TransportConnection
  ): Promise<TransportResult> {
    if (!(connection instanceof WebSocketConnection)) {
      throw new Error('Invalid connection type for WebSocket transport');
    }

    try {
      const serializedPacket = this.serializePacket(packet);
      connection.send(serializedPacket);

      return {
        success: true,
        packetId: packet.id,
        timestamp: Date.now(),
        bytesSent: serializedPacket.length
      };

    } catch (error) {
      return {
        success: false,
        packetId: packet.id,
        error: error.message,
        timestamp: Date.now()
      };
    }
  }

  private buildWebSocketURL(endpoint: TransportEndpoint): string {
    const protocol = endpoint.secure ? 'wss' : 'ws';
    return `${protocol}://${endpoint.host}:${endpoint.port}${endpoint.path || '/'}`;
  }

  private serializePacket(packet: NetworkPacket): string {
    return JSON.stringify(packet);
  }
}

export class WebSocketConnection extends EventEmitter implements TransportConnection {
  public readonly id: string;
  public readonly type = TransportType.WEBSOCKET;
  public readonly endpoint: TransportEndpoint;
  private ws: WebSocket;
  private metrics: ConnectionMetrics;

  constructor(ws: WebSocket, endpoint: TransportEndpoint) {
    super();
    this.id = crypto.randomUUID();
    this.ws = ws;
    this.endpoint = endpoint;
    this.metrics = {
      bytesReceived: 0,
      bytesSent: 0,
      packetsReceived: 0,
      packetsSent: 0,
      errors: 0,
      lastActivity: Date.now()
    };
  }

  send(data: string | Buffer): void {
    this.ws.send(data);
    this.metrics.packetsSent++;
    this.metrics.bytesSent += data.length;
    this.metrics.lastActivity = Date.now();
  }

  close(): void {
    this.ws.close();
  }

  isConnected(): boolean {
    return this.ws.readyState === WebSocket.OPEN;
  }

  supportsHeartbeat(): boolean {
    return true;
  }

  getMetrics(): ConnectionMetrics {
    return { ...this.metrics };
  }

  handleMessage(data: string | Buffer): void {
    try {
      const packet = JSON.parse(data.toString());
      this.metrics.packetsReceived++;
      this.metrics.bytesReceived += data.length;
      this.metrics.lastActivity = Date.now();
      
      this.emit('packet', packet);
    } catch (error) {
      this.metrics.errors++;
      this.emit('error', error);
    }
  }
}
```

## Routing Algorithms

### Advanced Routing Engine

```typescript
// Future: src/kos/network/routing/AdvancedRoutingEngine.ts
export class AdvancedRoutingEngine {
  private routingTable: RoutingTable;
  private topologyManager: TopologyManager;
  private routingAlgorithms: Map<RoutingAlgorithm, RoutingImplementation>;
  private qosManager: QoSManager;
  private trafficAnalyzer: TrafficAnalyzer;

  constructor(config: RoutingConfig) {
    this.routingTable = new RoutingTable(config.table);
    this.topologyManager = new TopologyManager(config.topology);
    this.qosManager = new QoSManager(config.qos);
    this.trafficAnalyzer = new TrafficAnalyzer(config.traffic);
    this.initializeRoutingAlgorithms(config.algorithms);
  }

  private initializeRoutingAlgorithms(config: RoutingAlgorithmConfig): void {
    this.routingAlgorithms = new Map([
      [RoutingAlgorithm.DIJKSTRA, new DijkstraRouting(config.dijkstra)],
      [RoutingAlgorithm.ASTAR, new AStarRouting(config.astar)],
      [RoutingAlgorithm.FLOODING, new FloodingRouting(config.flooding)],
      [RoutingAlgorithm.DSR, new DSRRouting(config.dsr)],
      [RoutingAlgorithm.AODV, new AODVRouting(config.aodv)],
      [RoutingAlgorithm.OLSR, new OLSRRouting(config.olsr)]
    ]);
  }

  async findOptimalRoute(
    source: NodeAddress,
    destination: NodeAddress,
    requirements: RouteRequirements
  ): Promise<OptimalRoute | null> {
    // Analyze traffic patterns
    const trafficPattern = await this.trafficAnalyzer.analyzePattern(
      source,
      destination
    );

    // Select best routing algorithm based on requirements
    const algorithm = this.selectRoutingAlgorithm(requirements, trafficPattern);
    const implementation = this.routingAlgorithms.get(algorithm);

    if (!implementation) {
      throw new Error(`Routing algorithm ${algorithm} not available`);
    }

    // Find routes using selected algorithm
    const routes = await implementation.findRoutes(
      source,
      destination,
      requirements
    );

    if (routes.length === 0) {
      return null;
    }

    // Apply QoS constraints
    const qosFilteredRoutes = await this.qosManager.filterRoutes(
      routes,
      requirements.qos
    );

    // Select best route
    const optimalRoute = this.selectBestRoute(qosFilteredRoutes, requirements);

    return optimalRoute;
  }

  private selectRoutingAlgorithm(
    requirements: RouteRequirements,
    trafficPattern: TrafficPattern
  ): RoutingAlgorithm {
    // High reliability requirements
    if (requirements.reliability > 0.99) {
      return RoutingAlgorithm.DIJKSTRA;
    }

    // Low latency requirements
    if (requirements.maxLatency < 100) {
      return RoutingAlgorithm.ASTAR;
    }

    // Mobile/dynamic topology
    if (trafficPattern.mobility > 0.7) {
      return RoutingAlgorithm.AODV;
    }

    // Dense network
    if (trafficPattern.density > 0.8) {
      return RoutingAlgorithm.OLSR;
    }

    // Broadcast/multicast
    if (requirements.multicast) {
      return RoutingAlgorithm.FLOODING;
    }

    // Default to Dijkstra
    return RoutingAlgorithm.DIJKSTRA;
  }

  private selectBestRoute(
    routes: NetworkRoute[],
    requirements: RouteRequirements
  ): OptimalRoute {
    // Score routes based on requirements
    const scoredRoutes = routes.map(route => ({
      route,
      score: this.scoreRoute(route, requirements)
    }));

    // Sort by score (higher is better)
    scoredRoutes.sort((a, b) => b.score - a.score);

    const bestRoute = scoredRoutes[0].route;

    return {
      ...bestRoute,
      score: scoredRoutes[0].score,
      algorithm: this.getRouteAlgorithm(bestRoute),
      confidence: this.calculateConfidence(bestRoute, requirements)
    };
  }

  private scoreRoute(
    route: NetworkRoute,
    requirements: RouteRequirements
  ): number {
    let score = 0;

    // Latency score (lower is better)
    const latencyScore = Math.max(0, 100 - (route.latency / requirements.maxLatency) * 100);
    score += latencyScore * (requirements.weights?.latency || 0.3);

    // Reliability score (higher is better)
    const reliabilityScore = route.reliability * 100;
    score += reliabilityScore * (requirements.weights?.reliability || 0.3);

    // Bandwidth score (higher is better)
    const bandwidthScore = Math.min(100, (route.bandwidth / requirements.minBandwidth) * 100);
    score += bandwidthScore * (requirements.weights?.bandwidth || 0.2);

    // Hop count score (lower is better)
    const hopScore = Math.max(0, 100 - route.hops.length * 10);
    score += hopScore * (requirements.weights?.hops || 0.1);

    // Cost score (lower is better)
    const costScore = Math.max(0, 100 - route.cost);
    score += costScore * (requirements.weights?.cost || 0.1);

    return score;
  }
}

// Dijkstra Routing Implementation
export class DijkstraRouting implements RoutingImplementation {
  private config: DijkstraConfig;

  constructor(config: DijkstraConfig) {
    this.config = config;
  }

  async findRoutes(
    source: NodeAddress,
    destination: NodeAddress,
    requirements: RouteRequirements
  ): Promise<NetworkRoute[]> {
    const graph = await this.buildGraph();
    const distances = new Map<string, number>();
    const previous = new Map<string, NodeAddress | null>();
    const unvisited = new Set<string>();

    // Initialize distances
    for (const node of graph.nodes) {
      const nodeId = node.address.toString();
      distances.set(nodeId, nodeId === source.toString() ? 0 : Infinity);
      previous.set(nodeId, null);
      unvisited.add(nodeId);
    }

    while (unvisited.size > 0) {
      // Find unvisited node with minimum distance
      let currentNode: string | null = null;
      let minDistance = Infinity;

      for (const nodeId of unvisited) {
        const distance = distances.get(nodeId) || Infinity;
        if (distance < minDistance) {
          minDistance = distance;
          currentNode = nodeId;
        }
      }

      if (currentNode === null || minDistance === Infinity) {
        break; // No more reachable nodes
      }

      unvisited.delete(currentNode);

      // If we reached the destination, we can stop
      if (currentNode === destination.toString()) {
        break;
      }

      // Update distances to neighbors
      const neighbors = graph.getNeighbors(NodeAddress.fromString(currentNode));
      for (const neighbor of neighbors) {
        const neighborId = neighbor.address.toString();
        if (unvisited.has(neighborId)) {
          const edgeWeight = this.calculateEdgeWeight(
            NodeAddress.fromString(currentNode),
            neighbor.address,
            requirements
          );
          const altDistance = minDistance + edgeWeight;
          
          if (altDistance < (distances.get(neighborId) || Infinity)) {
            distances.set(neighborId, altDistance);
            previous.set(neighborId, NodeAddress.fromString(currentNode));
          }
        }
      }
    }

    // Reconstruct path
    const path = this.reconstructPath(previous, source, destination);
    if (path.length === 0) {
      return [];
    }

    // Convert path to route
    const route = await this.pathToRoute(path, requirements);
    return [route];
  }

  private calculateEdgeWeight(
    from: NodeAddress,
    to: NodeAddress,
    requirements: RouteRequirements
  ): number {
    // Get edge information from topology
    const edge = this.getEdge(from, to);
    if (!edge) {
      return Infinity;
    }

    let weight = 0;

    // Latency component
    weight += edge.latency * (requirements.weights?.latency || 0.3);

    // Reliability component (inverted - lower reliability = higher weight)
    weight += (1 - edge.reliability) * 100 * (requirements.weights?.reliability || 0.3);

    // Bandwidth component (inverted - lower bandwidth = higher weight)
    const bandwidthRatio = requirements.minBandwidth / edge.bandwidth;
    weight += Math.max(0, bandwidthRatio - 1) * 100 * (requirements.weights?.bandwidth || 0.2);

    // Cost component
    weight += edge.cost * (requirements.weights?.cost || 0.1);

    return weight;
  }

  private reconstructPath(
    previous: Map<string, NodeAddress | null>,
    source: NodeAddress,
    destination: NodeAddress
  ): NodeAddress[] {
    const path: NodeAddress[] = [];
    let current: NodeAddress | null = destination;

    while (current !== null) {
      path.unshift(current);
      current = previous.get(current.toString()) || null;
    }

    // Check if path is valid (starts with source)
    if (path.length === 0 || !path[0].equals(source)) {
      return [];
    }

    return path;
  }
}
```

## Implementation Roadmap

### Phase 1: Basic Networking (Months 1-3)
- HTTP and WebSocket transport implementations
- Basic peer discovery via mDNS
- Simple routing table management
- Connection pooling and management

### Phase 2: Mesh Networking (Months 4-6)
- Mesh topology management
- Gossip protocol implementation
- Multi-hop routing algorithms
- Peer-to-peer connections

### Phase 3: Advanced Protocols (Months 7-9)
- LoRa and Bluetooth transport layers
- Advanced routing algorithms (AODV, OLSR)
- QoS management and traffic shaping
- Network security and encryption

### Phase 4: Optimization (Months 10-12)
- Performance monitoring and analytics
- Adaptive routing and load balancing
- Network resilience and fault tolerance
- Cross-platform compatibility

## Code References

- Current HTTP client: `src/utils/apiClient.ts`
- Service configuration: `src/config/`
- Connection management: `src/store/serviceStore.ts`
- UI communication: `src/components/CapabilityUI.tsx`

## Metrics and KPIs

- **Network Latency**: Average round-trip time for packets
- **Packet Loss Rate**: Percentage of packets lost in transmission
- **Throughput**: Data transfer rate across network connections
- **Route Discovery Time**: Time to find optimal routes
- **Network Availability**: Percentage of time network is operational
- **Mesh Connectivity**: Percentage of nodes reachable in mesh network

---

