---
title: "Service Registry API"
description: "REST API and client SDKs for service registry operations"
type: "service"
status: "future"
priority: "medium"
last_updated: "2025-01-27"
related_docs: ["service-registry-core.md", "federated-mesh-protocols.md"]
implementation_status: "planned"
---

# Service Registry API

## Agent Context
Comprehensive API specification for service registry operations including REST endpoints, client SDKs, and real-time subscription capabilities.

## REST API Specification

```typescript
interface ServiceRegistryAPI {
  // Service registration
  'POST /services': (registration: ServiceRegistration) => Promise<ServiceRegistration>;
  'PUT /services/:id': (id: string, updates: ServiceUpdate) => Promise<ServiceRegistration>;
  'DELETE /services/:id': (id: string) => Promise<void>;
  
  // Service discovery
  'GET /services': (query: ServiceQuery) => Promise<ServiceRegistration[]>;
  'GET /services/:id': (id: string) => Promise<ServiceRegistration>;
  'POST /services/discover': (query: ComplexServiceQuery) => Promise<DiscoveryResult>;
  
  // Health monitoring
  'GET /services/:id/health': (id: string) => Promise<HealthStatus>;
  'POST /services/:id/health': (id: string, status: HealthUpdate) => Promise<void>;
  
  // Capabilities
  'GET /services/:id/capabilities': (id: string) => Promise<ServiceCapability[]>;
  'POST /services/:id/capabilities': (id: string, capability: ServiceCapability) => Promise<void>;
}
```

## Client SDK

```typescript
class ServiceRegistryClient {
  private baseUrl: string;
  private apiKey: string;
  private httpClient: HttpClient;

  constructor(config: RegistryClientConfig) {
    this.baseUrl = config.baseUrl;
    this.apiKey = config.apiKey;
    this.httpClient = new HttpClient(config);
  }

  async registerService(registration: ServiceRegistration): Promise<ServiceRegistration> {
    const response = await this.httpClient.post('/services', registration, {
      headers: { 'Authorization': `Bearer ${this.apiKey}` }
    });
    
    return response.data;
  }

  async discoverServices(query: ServiceQuery): Promise<ServiceRegistration[]> {
    const params = new URLSearchParams();
    
    if (query.type) params.append('type', query.type);
    if (query.capabilities) {
      query.capabilities.forEach(cap => params.append('capability', cap));
    }
    if (query.tags) {
      query.tags.forEach(tag => params.append('tag', tag));
    }

    const response = await this.httpClient.get(`/services?${params.toString()}`);
    return response.data;
  }

  async updateServiceHealth(serviceId: string, health: HealthUpdate): Promise<void> {
    await this.httpClient.post(`/services/${serviceId}/health`, health, {
      headers: { 'Authorization': `Bearer ${this.apiKey}` }
    });
  }

  async subscribeToServiceUpdates(
    callback: (event: ServiceEvent) => void
  ): Promise<ServiceSubscription> {
    const ws = new WebSocket(`${this.baseUrl.replace('http', 'ws')}/ws`);
    
    ws.onmessage = (event) => {
      const serviceEvent = JSON.parse(event.data) as ServiceEvent;
      callback(serviceEvent);
    };

    return new ServiceSubscription(ws);
  }
}
```
