---
title: "Service Registry System - Dynamic Agent & Service Registration"
last_updated: "2025-01-27"
version: "1.0"
status: "future"
complexity: "high"
decision_scope: "system-wide"
implementation_status: "specification"
code_references:
  - "service-registry.ts"
  - "service-discovery.ts"
  - "registry-sync.ts"
related_documents:
  - "documentation/current/services/04_service-registry.md"
  - "documentation/future/protocols/07_federated-mesh-protocols.md"
  - "documentation/future/security/17_agent-trust-reputation-system.md"
external_references:
  - "https://fastapi.tiangolo.com/"
  - "https://redis.io/"
  - "https://neo4j.com/"
---

# Service Registry System - Dynamic Agent & Service Registration

## Agent Context

This document specifies the comprehensive Service Registry System for AI agents operating within the kAI/kOS ecosystem. Agents should understand that this system enables dynamic discovery, secure registration, and metadata synchronization of all services, agents, APIs, and tools across the distributed ecosystem. The registry provides centralized and federated service discovery with cryptographic integrity and real-time status monitoring.

## I. System Overview

The Service Registry System ensures dynamic discovery, secure registration, and metadata synchronization of all components across the distributed kAI/kOS ecosystem, enabling intelligent service routing and orchestration.

### Core Objectives
- **Dynamic Discovery**: Enable all system components to register and discover services dynamically
- **Secure Registration**: Cryptographically verified service registration with access control
- **Metadata Synchronization**: Real-time service metadata and status synchronization
- **Federated Architecture**: Support both centralized and federated registry deployments

## II. Service Registry Architecture

### A. Service Metadata Schema

```typescript
interface ServiceRegistration {
  id: string; // UUID or unique hash
  name: string; // Human-readable name
  type: ServiceType;
  tags: string[];
  url: string;
  protocol: ServiceProtocol;
  auth: AuthenticationConfig;
  endpoints: ServiceEndpoint[];
  heartbeat: Date;
  status: ServiceStatus;
  owner: string; // agent_id or user_id
  visibility: VisibilityLevel;
  capabilities: ServiceCapability[];
  metadata: ServiceMetadata;
  registration_signature: string;
}

enum ServiceType {
  AGENT = "agent",
  TOOL = "tool",
  SERVICE = "service",
  API = "api",
  DEVICE = "device",
  NODE = "node",
  GATEWAY = "gateway",
  VALIDATOR = "validator"
}

enum ServiceProtocol {
  HTTP = "http",
  HTTPS = "https",
  WEBSOCKET = "ws",
  KLP = "klp", // Kind Link Protocol
  GRPC = "grpc",
  MQTT = "mqtt"
}

interface AuthenticationConfig {
  type: AuthType;
  token?: string;
  certificate?: string;
  public_key?: string;
  auth_endpoint?: string;
}

enum AuthType {
  NONE = "none",
  API_KEY = "api_key",
  JWT = "jwt",
  OAUTH = "oauth",
  CERTIFICATE = "certificate",
  SIGNATURE = "signature"
}

interface ServiceEndpoint {
  path: string;
  method: HTTPMethod;
  description: string;
  input_schema?: JSONSchema;
  output_schema?: JSONSchema;
  rate_limit?: RateLimit;
  auth_required: boolean;
}

enum HTTPMethod {
  GET = "GET",
  POST = "POST",
  PUT = "PUT",
  DELETE = "DELETE",
  PATCH = "PATCH",
  OPTIONS = "OPTIONS"
}

interface ServiceCapability {
  capability_name: string;
  capability_type: CapabilityType;
  input_types: string[];
  output_types: string[];
  complexity_level: ComplexityLevel;
  performance_metrics: PerformanceMetrics;
}

enum CapabilityType {
  PROCESSING = "processing",
  STORAGE = "storage",
  COMMUNICATION = "communication",
  ANALYSIS = "analysis",
  GENERATION = "generation",
  VALIDATION = "validation"
}

enum ServiceStatus {
  ACTIVE = "active",
  OFFLINE = "offline",
  DEGRADED = "degraded",
  MAINTENANCE = "maintenance",
  ERROR = "error"
}

enum VisibilityLevel {
  PUBLIC = "public",
  PRIVATE = "private",
  INTERNAL = "internal",
  RESTRICTED = "restricted"
}

interface ServiceMetadata {
  version: string;
  description: string;
  documentation_url?: string;
  health_check_endpoint?: string;
  metrics_endpoint?: string;
  logs_endpoint?: string;
  deployment_info: DeploymentInfo;
  performance_profile: PerformanceProfile;
}

interface DeploymentInfo {
  environment: string;
  region: string;
  availability_zone?: string;
  container_id?: string;
  process_id?: string;
  startup_time: Date;
}
```

### B. Service Registry Engine

```typescript
class ServiceRegistryEngine {
  private storage: RegistryStorage;
  private discoveryEngine: DiscoveryEngine;
  private heartbeatManager: HeartbeatManager;
  private federationSync: FederationSync;
  private cryptoService: CryptographicService;

  constructor(config: RegistryConfig) {
    this.storage = new RegistryStorage(config.storage);
    this.discoveryEngine = new DiscoveryEngine();
    this.heartbeatManager = new HeartbeatManager(config.heartbeat);
    this.federationSync = new FederationSync(config.federation);
    this.cryptoService = new CryptographicService();
  }

  async registerService(registration: ServiceRegistrationRequest): Promise<ServiceRegistration> {
    // 1. Validate registration data
    const validation_result = await this.validateRegistration(registration);
    if (!validation_result.valid) {
      throw new Error(`Registration validation failed: ${validation_result.errors.join(', ')}`);
    }

    // 2. Verify service signature
    const signature_valid = await this.cryptoService.verifySignature(
      registration.signature,
      registration.public_key,
      this.serializeRegistrationData(registration)
    );

    if (!signature_valid) {
      throw new Error("Invalid service registration signature");
    }

    // 3. Check for existing registration
    const existing_service = await this.storage.findServiceById(registration.id);
    if (existing_service) {
      return await this.updateServiceRegistration(registration);
    }

    // 4. Create service registration
    const service_registration: ServiceRegistration = {
      id: registration.id,
      name: registration.name,
      type: registration.type,
      tags: registration.tags,
      url: registration.url,
      protocol: registration.protocol,
      auth: registration.auth,
      endpoints: registration.endpoints,
      heartbeat: new Date(),
      status: ServiceStatus.ACTIVE,
      owner: registration.owner,
      visibility: registration.visibility,
      capabilities: registration.capabilities,
      metadata: registration.metadata,
      registration_signature: registration.signature
    };

    // 5. Store registration
    await this.storage.saveService(service_registration);

    // 6. Start heartbeat monitoring
    await this.heartbeatManager.startMonitoring(service_registration.id);

    // 7. Sync with federated registries
    await this.federationSync.propagateRegistration(service_registration);

    // 8. Index for discovery
    await this.discoveryEngine.indexService(service_registration);

    return service_registration;
  }

  async discoverServices(query: ServiceDiscoveryQuery): Promise<ServiceDiscoveryResults> {
    // 1. Parse discovery query
    const search_criteria = this.parseDiscoveryQuery(query);

    // 2. Apply access control filters
    const filtered_criteria = await this.applyAccessFilters(search_criteria, query.requester_id);

    // 3. Search local registry
    const local_results = await this.discoveryEngine.search(filtered_criteria);

    // 4. Query federated registries if needed
    let federated_results: ServiceRegistration[] = [];
    if (query.include_federated) {
      federated_results = await this.federationSync.queryFederatedServices(filtered_criteria);
    }

    // 5. Merge and rank results
    const all_services = [...local_results, ...federated_results];
    const ranked_services = await this.rankServices(all_services, query);

    return {
      query,
      services: ranked_services,
      total_count: ranked_services.length,
      local_count: local_results.length,
      federated_count: federated_results.length,
      search_time_ms: Date.now() - query.start_time.getTime()
    };
  }

  async updateServiceStatus(service_id: string, status: ServiceStatus, metadata?: any): Promise<void> {
    const service = await this.storage.findServiceById(service_id);
    if (!service) {
      throw new Error(`Service not found: ${service_id}`);
    }

    service.status = status;
    service.heartbeat = new Date();
    
    if (metadata) {
      service.metadata = { ...service.metadata, ...metadata };
    }

    await this.storage.updateService(service);
    await this.federationSync.propagateStatusUpdate(service);
  }

  async deregisterService(service_id: string, deregistration_signature: string): Promise<void> {
    const service = await this.storage.findServiceById(service_id);
    if (!service) {
      throw new Error(`Service not found: ${service_id}`);
    }

    // Verify deregistration signature
    const signature_valid = await this.cryptoService.verifyDeregistrationSignature(
      deregistration_signature,
      service.owner,
      service_id
    );

    if (!signature_valid) {
      throw new Error("Invalid deregistration signature");
    }

    // Stop heartbeat monitoring
    await this.heartbeatManager.stopMonitoring(service_id);

    // Remove from storage
    await this.storage.deleteService(service_id);

    // Propagate deregistration
    await this.federationSync.propagateDeregistration(service_id);

    // Remove from discovery index
    await this.discoveryEngine.removeService(service_id);
  }

  private async rankServices(services: ServiceRegistration[], query: ServiceDiscoveryQuery): Promise<ServiceRegistration[]> {
    const scoring_weights = {
      capability_match: 0.4,
      status_health: 0.3,
      proximity: 0.2,
      trust_score: 0.1
    };

    const scored_services = await Promise.all(
      services.map(async (service) => {
        const capability_score = this.calculateCapabilityMatch(service.capabilities, query.required_capabilities);
        const health_score = this.calculateHealthScore(service.status, service.heartbeat);
        const proximity_score = await this.calculateProximityScore(service, query.requester_location);
        const trust_score = await this.getTrustScore(service.id);

        const composite_score = (
          capability_score * scoring_weights.capability_match +
          health_score * scoring_weights.status_health +
          proximity_score * scoring_weights.proximity +
          trust_score * scoring_weights.trust_score
        );

        return { service, score: composite_score };
      })
    );

    return scored_services
      .sort((a, b) => b.score - a.score)
      .map(item => item.service);
  }
}

interface ServiceRegistrationRequest {
  id: string;
  name: string;
  type: ServiceType;
  tags: string[];
  url: string;
  protocol: ServiceProtocol;
  auth: AuthenticationConfig;
  endpoints: ServiceEndpoint[];
  owner: string;
  visibility: VisibilityLevel;
  capabilities: ServiceCapability[];
  metadata: ServiceMetadata;
  signature: string;
  public_key: string;
}

interface ServiceDiscoveryQuery {
  service_types?: ServiceType[];
  tags?: string[];
  capabilities?: string[];
  required_capabilities?: ServiceCapability[];
  status_filter?: ServiceStatus[];
  visibility_filter?: VisibilityLevel[];
  owner_filter?: string;
  protocol_filter?: ServiceProtocol[];
  include_federated: boolean;
  requester_id: string;
  requester_location?: GeographicLocation;
  max_results: number;
  start_time: Date;
}

interface ServiceDiscoveryResults {
  query: ServiceDiscoveryQuery;
  services: ServiceRegistration[];
  total_count: number;
  local_count: number;
  federated_count: number;
  search_time_ms: number;
}
```

### C. Heartbeat and Health Monitoring

```typescript
class HeartbeatManager {
  private heartbeatIntervals: Map<string, NodeJS.Timeout>;
  private healthChecker: HealthChecker;
  private alertManager: AlertManager;

  constructor(config: HeartbeatConfig) {
    this.heartbeatIntervals = new Map();
    this.healthChecker = new HealthChecker(config.health_check);
    this.alertManager = new AlertManager(config.alerts);
  }

  async startMonitoring(service_id: string): Promise<void> {
    const service = await this.registryEngine.getService(service_id);
    
    const interval = setInterval(async () => {
      await this.performHealthCheck(service);
    }, this.config.heartbeat_interval_ms);

    this.heartbeatIntervals.set(service_id, interval);
  }

  async stopMonitoring(service_id: string): Promise<void> {
    const interval = this.heartbeatIntervals.get(service_id);
    if (interval) {
      clearInterval(interval);
      this.heartbeatIntervals.delete(service_id);
    }
  }

  private async performHealthCheck(service: ServiceRegistration): Promise<void> {
    try {
      const health_result = await this.healthChecker.checkHealth(service);
      
      if (health_result.healthy) {
        await this.registryEngine.updateServiceStatus(service.id, ServiceStatus.ACTIVE, {
          last_health_check: new Date(),
          health_score: health_result.score
        });
      } else {
        await this.registryEngine.updateServiceStatus(service.id, ServiceStatus.DEGRADED, {
          last_health_check: new Date(),
          health_issues: health_result.issues
        });
        
        await this.alertManager.sendHealthAlert(service, health_result);
      }
    } catch (error) {
      await this.registryEngine.updateServiceStatus(service.id, ServiceStatus.ERROR, {
        last_health_check: new Date(),
        error_message: error.message
      });
      
      await this.alertManager.sendErrorAlert(service, error);
    }
  }
}

class HealthChecker {
  async checkHealth(service: ServiceRegistration): Promise<HealthCheckResult> {
    const health_checks: HealthCheck[] = [];

    // 1. Basic connectivity check
    const connectivity_check = await this.checkConnectivity(service.url);
    health_checks.push(connectivity_check);

    // 2. Health endpoint check (if available)
    if (service.metadata.health_check_endpoint) {
      const endpoint_check = await this.checkHealthEndpoint(
        service.url + service.metadata.health_check_endpoint
      );
      health_checks.push(endpoint_check);
    }

    // 3. Response time check
    const response_time_check = await this.checkResponseTime(service);
    health_checks.push(response_time_check);

    // 4. Calculate overall health score
    const health_score = this.calculateHealthScore(health_checks);
    const healthy = health_score > 0.7; // 70% threshold

    return {
      healthy,
      score: health_score,
      checks: health_checks,
      issues: health_checks.filter(check => !check.passed).map(check => check.issue),
      checked_at: new Date()
    };
  }

  private async checkConnectivity(url: string): Promise<HealthCheck> {
    try {
      const response = await fetch(url, { 
        method: 'HEAD', 
        timeout: 5000 
      });
      
      return {
        check_type: 'connectivity',
        passed: response.ok,
        score: response.ok ? 1.0 : 0.0,
        issue: response.ok ? null : `HTTP ${response.status}: ${response.statusText}`
      };
    } catch (error) {
      return {
        check_type: 'connectivity',
        passed: false,
        score: 0.0,
        issue: `Connection failed: ${error.message}`
      };
    }
  }
}

interface HealthCheckResult {
  healthy: boolean;
  score: number;
  checks: HealthCheck[];
  issues: string[];
  checked_at: Date;
}

interface HealthCheck {
  check_type: string;
  passed: boolean;
  score: number;
  issue: string | null;
}
```

## III. Federation and Synchronization

### A. Federated Registry Sync

```typescript
class FederationSync {
  private klpProtocol: KLPProtocol;
  private peerRegistry: PeerRegistry;
  private syncManager: SyncManager;

  async propagateRegistration(service: ServiceRegistration): Promise<PropagationResult> {
    const federated_peers = await this.peerRegistry.getActivePeers();
    const propagation_results: PeerPropagationResult[] = [];

    for (const peer of federated_peers) {
      try {
        const sync_message = this.createRegistrationSyncMessage(service);
        const result = await this.klpProtocol.sendMessage(peer, sync_message);
        
        propagation_results.push({
          peer_id: peer.id,
          success: true,
          response_time_ms: result.response_time_ms
        });
      } catch (error) {
        propagation_results.push({
          peer_id: peer.id,
          success: false,
          error: error.message
        });
      }
    }

    return {
      service_id: service.id,
      peers_contacted: federated_peers.length,
      successful_propagations: propagation_results.filter(r => r.success).length,
      failed_propagations: propagation_results.filter(r => !r.success).length,
      propagation_results
    };
  }

  async queryFederatedServices(criteria: SearchCriteria): Promise<ServiceRegistration[]> {
    const federated_peers = await this.peerRegistry.getActivePeers();
    const federated_services: ServiceRegistration[] = [];

    const query_promises = federated_peers.map(async (peer) => {
      try {
        const query_message = this.createServiceQueryMessage(criteria);
        const response = await this.klpProtocol.sendMessage(peer, query_message);
        return response.payload.services as ServiceRegistration[];
      } catch (error) {
        console.warn(`Failed to query peer ${peer.id}: ${error.message}`);
        return [];
      }
    });

    const peer_results = await Promise.all(query_promises);
    
    // Merge and deduplicate results
    for (const services of peer_results) {
      for (const service of services) {
        if (!federated_services.find(s => s.id === service.id)) {
          federated_services.push(service);
        }
      }
    }

    return federated_services;
  }

  private createRegistrationSyncMessage(service: ServiceRegistration): KLPMessage {
    return {
      type: KLPMessageType.SERVICE_REGISTRATION,
      source: this.getLocalNodeAddress(),
      target: "broadcast",
      payload: {
        action: "register",
        service,
        timestamp: new Date(),
        signature: this.signRegistration(service)
      },
      metadata: {
        priority: MessagePriority.NORMAL,
        ttl: 3600,
        trust_requirements: {
          minimum_trust_score: 6.0,
          verification_level: VerificationLevel.BASIC
        }
      }
    };
  }
}

interface PropagationResult {
  service_id: string;
  peers_contacted: number;
  successful_propagations: number;
  failed_propagations: number;
  propagation_results: PeerPropagationResult[];
}

interface PeerPropagationResult {
  peer_id: string;
  success: boolean;
  response_time_ms?: number;
  error?: string;
}
```

## IV. API and WebSocket Interface

### A. REST API Endpoints

```typescript
class ServiceRegistryAPI {
  // POST /api/services/register
  async registerService(request: RegisterServiceRequest): Promise<RegistrationResponse> {
    const registration_request: ServiceRegistrationRequest = {
      id: request.id || this.generateServiceId(),
      name: request.name,
      type: request.type,
      tags: request.tags || [],
      url: request.url,
      protocol: request.protocol,
      auth: request.auth,
      endpoints: request.endpoints,
      owner: request.owner,
      visibility: request.visibility || VisibilityLevel.PRIVATE,
      capabilities: request.capabilities || [],
      metadata: request.metadata,
      signature: request.signature,
      public_key: request.public_key
    };

    const service = await this.registryEngine.registerService(registration_request);
    
    return {
      service,
      success: true,
      registration_id: service.id
    };
  }

  // GET /api/services
  async discoverServices(request: DiscoveryRequest): Promise<DiscoveryResponse> {
    const query: ServiceDiscoveryQuery = {
      service_types: request.types,
      tags: request.tags,
      capabilities: request.capabilities,
      status_filter: request.status_filter,
      visibility_filter: request.visibility_filter,
      include_federated: request.include_federated || false,
      requester_id: request.requester_id,
      max_results: request.limit || 50,
      start_time: new Date()
    };

    const results = await this.registryEngine.discoverServices(query);
    
    return {
      services: results.services,
      total_count: results.total_count,
      search_time_ms: results.search_time_ms,
      federated_results: results.federated_count > 0
    };
  }

  // POST /api/services/{id}/heartbeat
  async updateHeartbeat(service_id: string, request: HeartbeatRequest): Promise<HeartbeatResponse> {
    await this.registryEngine.updateServiceStatus(
      service_id,
      request.status || ServiceStatus.ACTIVE,
      request.metadata
    );

    return {
      service_id,
      heartbeat_updated: true,
      next_heartbeat_due: new Date(Date.now() + this.config.heartbeat_interval_ms)
    };
  }
}

// WebSocket interface for real-time updates
class ServiceRegistryWebSocket {
  private connections: Map<string, WebSocket>;
  private subscriptions: Map<string, SubscriptionFilter[]>;

  async handleConnection(ws: WebSocket, user_id: string): Promise<void> {
    this.connections.set(user_id, ws);
    
    ws.on('message', async (message) => {
      const data = JSON.parse(message.toString());
      await this.handleMessage(user_id, data);
    });

    ws.on('close', () => {
      this.connections.delete(user_id);
      this.subscriptions.delete(user_id);
    });
  }

  async broadcastServiceUpdate(service: ServiceRegistration, update_type: UpdateType): Promise<void> {
    const notification = {
      type: 'service_update',
      update_type,
      service,
      timestamp: new Date()
    };

    for (const [user_id, filters] of this.subscriptions) {
      if (this.matchesSubscriptionFilters(service, filters)) {
        const ws = this.connections.get(user_id);
        if (ws && ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify(notification));
        }
      }
    }
  }
}
```

## V. Implementation Status

- **Core Registry Engine**: Architecture complete, federation sync implementation required
- **Discovery System**: Service discovery framework specified, ranking algorithm optimization needed
- **Heartbeat Management**: Health monitoring system designed, alert integration required
- **Federation Sync**: KLP integration framework defined, peer management implementation needed
- **API Layer**: REST and WebSocket interfaces complete, authentication integration required

This service registry system provides comprehensive service discovery, registration, and monitoring capabilities essential for dynamic service orchestration across the kAI/kOS ecosystem. 