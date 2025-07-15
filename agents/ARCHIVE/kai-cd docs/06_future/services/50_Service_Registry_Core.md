---
title: "Service Registry Core"
description: "Distributed service discovery and registration system"
type: "service"
status: "future"
priority: "high"
last_updated: "2025-01-27"
related_docs: ["service-registry-api.md", "federated-mesh-protocols.md"]
implementation_status: "planned"
---

# Service Registry Core

## Agent Context
Distributed service registry enabling automatic service discovery, health monitoring, and load balancing across federated agent clusters.

## Registry Architecture

```typescript
interface ServiceRegistration {
  id: string;
  name: string;
  type: ServiceType;
  version: string;
  address: ServiceAddress;
  capabilities: ServiceCapability[];
  metadata: ServiceMetadata;
  health: HealthStatus;
  registered: string;
  lastSeen: string;
}

interface ServiceAddress {
  protocol: 'http' | 'https' | 'websocket' | 'klp';
  host: string;
  port: number;
  path?: string;
  endpoints: ServiceEndpoint[];
}

interface ServiceCapability {
  name: string;
  version: string;
  interface: string; // API specification
  requirements: string[];
  optional: boolean;
}

type ServiceType = 
  | 'llm_service'
  | 'vector_database'
  | 'artifact_server'
  | 'memory_service'
  | 'auth_service'
  | 'orchestrator'
  | 'bridge_service';
```

## Registry Manager

```typescript
class ServiceRegistryManager {
  private services: Map<string, ServiceRegistration>;
  private healthMonitor: HealthMonitor;
  private discoveryEngine: ServiceDiscoveryEngine;

  async registerService(registration: ServiceRegistration): Promise<void> {
    // Validate registration
    const validation = await this.validateRegistration(registration);
    if (!validation.valid) {
      throw new Error(`Invalid registration: ${validation.error}`);
    }

    // Store registration
    this.services.set(registration.id, registration);
    
    // Start health monitoring
    await this.healthMonitor.startMonitoring(registration);
    
    // Notify discovery engine
    await this.discoveryEngine.serviceRegistered(registration);
    
    console.log(`Service registered: ${registration.name} (${registration.id})`);
  }

  async discoverServices(query: ServiceQuery): Promise<ServiceRegistration[]> {
    const results: ServiceRegistration[] = [];
    
    for (const [id, service] of this.services) {
      if (this.matchesQuery(service, query)) {
        // Check if service is healthy
        if (service.health.status === 'healthy') {
          results.push(service);
        }
      }
    }

    // Sort by relevance and health score
    return results.sort((a, b) => {
      const scoreA = this.calculateRelevanceScore(a, query);
      const scoreB = this.calculateRelevanceScore(b, query);
      return scoreB - scoreA;
    });
  }

  async getServiceHealth(serviceId: string): Promise<HealthStatus | null> {
    const service = this.services.get(serviceId);
    return service ? service.health : null;
  }

  private matchesQuery(service: ServiceRegistration, query: ServiceQuery): boolean {
    // Type filter
    if (query.type && service.type !== query.type) {
      return false;
    }

    // Capability filter
    if (query.capabilities) {
      const hasAllCapabilities = query.capabilities.every(reqCap =>
        service.capabilities.some(cap => cap.name === reqCap)
      );
      if (!hasAllCapabilities) {
        return false;
      }
    }

    // Tag filter
    if (query.tags) {
      const hasTags = query.tags.every(tag =>
        service.metadata.tags?.includes(tag)
      );
      if (!hasTags) {
        return false;
      }
    }

    return true;
  }
}
```

## Health Monitoring

```typescript
class HealthMonitor {
  private monitors: Map<string, ServiceMonitor>;
  private checkInterval: number = 30000; // 30 seconds

  async startMonitoring(service: ServiceRegistration): Promise<void> {
    const monitor = new ServiceMonitor(service);
    this.monitors.set(service.id, monitor);
    
    // Start periodic health checks
    const intervalId = setInterval(async () => {
      await this.performHealthCheck(service.id);
    }, this.checkInterval);

    monitor.intervalId = intervalId;
  }

  async performHealthCheck(serviceId: string): Promise<HealthCheckResult> {
    const service = this.registry.services.get(serviceId);
    if (!service) {
      return { healthy: false, error: 'Service not found' };
    }

    try {
      const healthEndpoint = service.address.endpoints.find(
        ep => ep.path === '/health'
      );

      if (!healthEndpoint) {
        // No health endpoint, assume healthy if reachable
        const reachable = await this.checkReachability(service.address);
        return { healthy: reachable, lastCheck: new Date().toISOString() };
      }

      const response = await this.callHealthEndpoint(service.address, healthEndpoint);
      
      const result: HealthCheckResult = {
        healthy: response.status === 'healthy',
        lastCheck: new Date().toISOString(),
        details: response.details,
        metrics: response.metrics
      };

      // Update service health status
      service.health = {
        status: result.healthy ? 'healthy' : 'unhealthy',
        lastCheck: result.lastCheck,
        details: result.details,
        consecutiveFailures: result.healthy ? 0 : (service.health.consecutiveFailures || 0) + 1
      };

      return result;

    } catch (error) {
      service.health = {
        status: 'unhealthy',
        lastCheck: new Date().toISOString(),
        error: error.message,
        consecutiveFailures: (service.health.consecutiveFailures || 0) + 1
      };

      return { healthy: false, error: error.message };
    }
  }

  private async callHealthEndpoint(
    address: ServiceAddress,
    endpoint: ServiceEndpoint
  ): Promise<HealthResponse> {
    const url = `${address.protocol}://${address.host}:${address.port}${endpoint.path}`;
    
    const response = await fetch(url, {
      method: 'GET',
      timeout: 5000,
      headers: {
        'Accept': 'application/json'
      }
    });

    if (!response.ok) {
      throw new Error(`Health check failed: ${response.status}`);
    }

    return await response.json();
  }
}
```
