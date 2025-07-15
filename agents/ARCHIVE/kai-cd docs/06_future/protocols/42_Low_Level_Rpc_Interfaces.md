---
title: "Low-Level RPC Interfaces"
description: "Comprehensive specification for inter-agent communication protocols, RPC interfaces, and transport mechanisms"
type: "protocol"
status: "future"
priority: "high"
last_updated: "2025-01-27"
related_docs: ["agent-communication-protocols-core.md", "kind-link-protocol-core.md"]
implementation_status: "planned"
---

# Low-Level RPC Interfaces & Inter-Agent Communication

## Agent Context
This document specifies the complete low-level communication protocols between services, agents, and system modules within the kOS/kAI ecosystem. Essential for agents implementing distributed communication, service discovery, and inter-process coordination. Provides the foundation for scalable, reliable, and secure agent-to-agent communication.

## Protocol Overview

The kOS ecosystem employs a hybrid communication architecture combining REST, WebSocket, and internal RPC mechanisms optimized for different latency, persistence, and real-time requirements. The core **Agent-Module RPC Interface (AMRI)** protocol serves as the foundation for all service-to-service communication within the distributed system.

### Communication Architecture
```typescript
interface CommunicationArchitecture {
  transportLayers: {
    rest: {
      description: "External-facing HTTP/REST API for web clients";
      technology: "FastAPI with automatic OpenAPI documentation";
      useCases: ["Web UI communication", "External integrations", "Public APIs"];
      features: ["Request/response", "Stateless", "Cacheable", "HTTP semantics"];
    };
    
    websocket: {
      description: "Persistent bi-directional communication";
      technology: "WebSocket with JSON-RPC over persistent connections";
      useCases: ["Real-time updates", "Streaming responses", "Interactive sessions"];
      features: ["Full-duplex", "Low latency", "Event-driven", "Session state"];
    };
    
    grpc: {
      description: "High-performance binary RPC for internal services";
      technology: "gRPC with Protocol Buffers";
      useCases: ["Internal service communication", "High-throughput operations"];
      features: ["Binary protocol", "Streaming", "Type safety", "Performance"];
      status: "Planned implementation";
    };
    
    jsonRpc: {
      description: "Lightweight RPC for single-node operations";
      technology: "JSON-RPC 2.0 over various transports";
      useCases: ["Local agent communication", "Development", "Testing"];
      features: ["Simple protocol", "Language agnostic", "Easy debugging"];
    };
  };
  
  layerResponsibilities: {
    transportAgnostic: "Unified API contract enforcement across all transport types";
    reliability: "Timeout management, retry logic, and failure handling";
    observability: "Comprehensive logging, metrics, and distributed tracing";
    versioning: "Schema versioning and backward compatibility";
    serialization: "Efficient JSON serialization with validation";
    contextPropagation: "Request context and trace propagation";
  };
}
```

## Message Protocol Specifications

### Request Envelope Schema
```typescript
interface RequestEnvelope {
  // Core identification
  id: string; // UUID v4 for request correlation
  origin: string; // Source agent/module identifier (e.g., "kAI.module.scheduler")
  destination: string; // Target agent/module identifier (e.g., "kAI.agent.calendar")
  timestamp: number; // Unix timestamp in milliseconds
  
  // RPC specification
  method: string; // Dot-notation RPC method (e.g., "agent.register", "memory.query")
  params: Record<string, any>; // Method parameters as key-value pairs
  
  // Request metadata
  headers: {
    traceId: string; // Distributed tracing identifier
    authToken?: string; // Optional JWT or API token
    userId?: string; // User context identifier
    ttl: number; // Time-to-live in milliseconds
    priority?: "low" | "normal" | "high" | "critical";
    retryCount?: number; // Current retry attempt number
    correlationId?: string; // Workflow correlation identifier
  };
  
  // Protocol version and capabilities
  version: string; // Protocol version (e.g., "1.0")
  capabilities?: string[]; // Optional capability requirements
}

// Example request envelope
const exampleRequest: RequestEnvelope = {
  id: "550e8400-e29b-41d4-a716-446655440000",
  origin: "kAI.module.scheduler",
  destination: "kAI.agent.calendar",
  timestamp: 1718963981000,
  method: "calendar.createEvent",
  params: {
    title: "Team Meeting",
    startTime: "2025-01-27T10:00:00Z",
    duration: 3600,
    attendees: ["user1@example.com", "user2@example.com"]
  },
  headers: {
    traceId: "trace-123e4567-e89b-12d3-a456-426614174000",
    authToken: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    userId: "user-789",
    ttl: 30000,
    priority: "normal"
  },
  version: "1.0"
};
```

### Response Envelope Schema
```typescript
interface ResponseEnvelope {
  // Core identification (mirrors request)
  id: string; // Same UUID as request for correlation
  origin: string; // Responding agent/module identifier
  destination: string; // Original requester identifier
  timestamp: number; // Response timestamp
  
  // Response data
  result?: any; // Successful response data
  error?: RpcError; // Error information if request failed
  
  // Performance and debugging metrics
  metrics: {
    latencyMs: number; // Total processing time
    retries: number; // Number of retry attempts
    backend: string; // Transport backend used
    queueTime?: number; // Time spent in queue
    processingTime?: number; // Actual processing time
  };
  
  // Response metadata
  headers: {
    traceId: string; // Same trace ID as request
    correlationId?: string; // Workflow correlation
    cacheHit?: boolean; // Whether response was cached
    version: string; // Response protocol version
  };
}

interface RpcError {
  code: number; // HTTP-style error code
  message: string; // Human-readable error message
  details?: Record<string, any>; // Additional error context
  stack?: string; // Stack trace for debugging
  retryable: boolean; // Whether the error is retryable
}

// Example successful response
const successResponse: ResponseEnvelope = {
  id: "550e8400-e29b-41d4-a716-446655440000",
  origin: "kAI.agent.calendar",
  destination: "kAI.module.scheduler",
  timestamp: 1718963983000,
  result: {
    eventId: "cal-event-456",
    status: "created",
    url: "https://calendar.example.com/event/456"
  },
  metrics: {
    latencyMs: 125,
    retries: 0,
    backend: "WebSocket",
    processingTime: 95
  },
  headers: {
    traceId: "trace-123e4567-e89b-12d3-a456-426614174000",
    version: "1.0"
  }
};

// Example error response
const errorResponse: ResponseEnvelope = {
  id: "550e8400-e29b-41d4-a716-446655440000",
  origin: "kAI.agent.calendar",
  destination: "kAI.module.scheduler",
  timestamp: 1718963983000,
  error: {
    code: 403,
    message: "Insufficient permissions to create calendar event",
    details: {
      requiredPermission: "calendar.write",
      userPermissions: ["calendar.read"]
    },
    retryable: false
  },
  metrics: {
    latencyMs: 50,
    retries: 0,
    backend: "WebSocket"
  },
  headers: {
    traceId: "trace-123e4567-e89b-12d3-a456-426614174000",
    version: "1.0"
  }
};
```

## Agent Registration and Discovery

### Agent Handshake Protocol
```typescript
interface AgentHandshakeProtocol {
  registration: {
    method: "agent.register";
    params: {
      capabilities: string[]; // Supported capabilities
      intents: AgentIntent[]; // Agent intentions
      metadata: AgentMetadata; // Agent metadata
      contractHash?: string; // Optional trust contract hash
    };
    response: {
      agentId: string; // Assigned agent identifier
      accepted: boolean; // Registration acceptance status
      heartbeatInterval: number; // Required heartbeat interval in seconds
      assignedCapabilities: string[]; // Actually granted capabilities
      restrictions?: string[]; // Any imposed restrictions
    };
  };
  
  heartbeat: {
    method: "agent.heartbeat";
    params: {
      agentId: string;
      status: AgentStatus;
      metrics: PerformanceMetrics;
    };
    response: {
      acknowledged: boolean;
      newInstructions?: string[];
    };
  };
  
  deregistration: {
    method: "agent.deregister";
    params: {
      agentId: string;
      reason: string;
    };
    response: {
      acknowledged: boolean;
      gracePeriod?: number; // Seconds before forced termination
    };
  };
}

type AgentIntent = "serve" | "consume" | "coordinate" | "monitor" | "backup";

interface AgentMetadata {
  hostname: string;
  version: string;
  load: number; // 0.0 to 1.0
  memory: {
    total: number;
    available: number;
    used: number;
  };
  capabilities: {
    [capability: string]: {
      version: string;
      performance: PerformanceMetrics;
    };
  };
}

interface AgentStatus {
  state: "initializing" | "ready" | "busy" | "overloaded" | "error" | "shutting_down";
  activeConnections: number;
  queuedRequests: number;
  lastActivity: number; // Unix timestamp
}

interface PerformanceMetrics {
  requestsPerSecond: number;
  averageLatency: number;
  errorRate: number;
  cpuUsage: number;
  memoryUsage: number;
}
```

### Service Discovery Implementation
```typescript
class ServiceDiscovery {
  private registry: Map<string, ServiceRegistration>;
  private routingTable: Map<string, string>;
  
  constructor() {
    this.registry = new Map();
    this.routingTable = new Map();
  }
  
  async registerService(registration: ServiceRegistration): Promise<void> {
    // Validate service registration
    await this.validateRegistration(registration);
    
    // Store in registry
    this.registry.set(registration.serviceId, registration);
    
    // Update routing table
    this.updateRoutingTable(registration);
    
    // Broadcast registration event
    await this.broadcastRegistration(registration);
  }
  
  async discoverService(capability: string): Promise<ServiceRegistration[]> {
    const services = Array.from(this.registry.values())
      .filter(service => service.capabilities.includes(capability))
      .filter(service => service.status === 'ready')
      .sort((a, b) => a.load - b.load); // Sort by load
    
    return services;
  }
  
  async routeRequest(method: string): Promise<string> {
    const serviceId = this.routingTable.get(method);
    if (!serviceId) {
      throw new Error(`No service registered for method: ${method}`);
    }
    
    const service = this.registry.get(serviceId);
    if (!service || service.status !== 'ready') {
      throw new Error(`Service unavailable: ${serviceId}`);
    }
    
    return serviceId;
  }
  
  private updateRoutingTable(registration: ServiceRegistration): void {
    // Update routing table based on service capabilities
    for (const capability of registration.capabilities) {
      this.routingTable.set(capability, registration.serviceId);
    }
  }
}

interface ServiceRegistration {
  serviceId: string;
  capabilities: string[];
  endpoint: string;
  status: AgentStatus;
  load: number;
  metadata: AgentMetadata;
  registeredAt: number;
  lastHeartbeat: number;
}
```

## Reliability and Error Handling

### Retry and Timeout Configuration
```typescript
interface ReliabilityConfiguration {
  timeoutPolicies: {
    [methodPattern: string]: {
      timeoutMs: number;
      retries: number;
      backoffStrategy: "linear" | "exponential" | "fixed";
      backoffParams: {
        initialDelay: number;
        maxDelay: number;
        multiplier?: number; // For exponential backoff
        jitter?: boolean; // Add randomization
      };
    };
  };
  
  circuitBreaker: {
    failureThreshold: number; // Failures before opening circuit
    recoveryTimeout: number; // Time before attempting recovery
    successThreshold: number; // Successes needed to close circuit
  };
  
  bulkhead: {
    maxConcurrentRequests: number;
    queueSize: number;
    timeoutMs: number;
  };
}

const defaultReliabilityConfig: ReliabilityConfiguration = {
  timeoutPolicies: {
    "agent.*": {
      timeoutMs: 5000,
      retries: 3,
      backoffStrategy: "linear",
      backoffParams: {
        initialDelay: 1000,
        maxDelay: 5000,
        jitter: true
      }
    },
    "memory.*": {
      timeoutMs: 2500,
      retries: 2,
      backoffStrategy: "exponential",
      backoffParams: {
        initialDelay: 500,
        maxDelay: 2000,
        multiplier: 2,
        jitter: true
      }
    },
    "llm_chat.*": {
      timeoutMs: 30000, // LLM calls can be slow
      retries: 1,
      backoffStrategy: "fixed",
      backoffParams: {
        initialDelay: 5000,
        maxDelay: 5000
      }
    },
    "media_gen.*": {
      timeoutMs: 60000, // Media generation is slow
      retries: 0,
      backoffStrategy: "fixed",
      backoffParams: {
        initialDelay: 0,
        maxDelay: 0
      }
    }
  },
  circuitBreaker: {
    failureThreshold: 5,
    recoveryTimeout: 30000,
    successThreshold: 3
  },
  bulkhead: {
    maxConcurrentRequests: 100,
    queueSize: 1000,
    timeoutMs: 30000
  }
};
```

### Error Handling Implementation
```typescript
class RpcErrorHandler {
  private circuitBreakers: Map<string, CircuitBreaker>;
  private metrics: MetricsCollector;
  
  constructor(metrics: MetricsCollector) {
    this.circuitBreakers = new Map();
    this.metrics = metrics;
  }
  
  async handleRequest<T>(
    request: RequestEnvelope,
    handler: () => Promise<T>
  ): Promise<ResponseEnvelope> {
    const startTime = Date.now();
    const circuitBreaker = this.getCircuitBreaker(request.method);
    
    try {
      // Check circuit breaker
      if (circuitBreaker.isOpen()) {
        throw new RpcError(503, "Service temporarily unavailable", {}, false);
      }
      
      // Execute with timeout
      const result = await this.executeWithTimeout(handler, request);
      
      // Record success
      circuitBreaker.recordSuccess();
      this.metrics.recordSuccess(request.method, Date.now() - startTime);
      
      return {
        id: request.id,
        origin: request.destination,
        destination: request.origin,
        timestamp: Date.now(),
        result,
        metrics: {
          latencyMs: Date.now() - startTime,
          retries: 0,
          backend: "internal"
        },
        headers: {
          traceId: request.headers.traceId,
          version: "1.0"
        }
      };
      
    } catch (error) {
      // Record failure
      circuitBreaker.recordFailure();
      this.metrics.recordError(request.method, error);
      
      const rpcError = error instanceof RpcError ? error : new RpcError(
        500,
        error.message || "Internal server error",
        { originalError: error.toString() },
        true
      );
      
      return {
        id: request.id,
        origin: request.destination,
        destination: request.origin,
        timestamp: Date.now(),
        error: rpcError,
        metrics: {
          latencyMs: Date.now() - startTime,
          retries: 0,
          backend: "internal"
        },
        headers: {
          traceId: request.headers.traceId,
          version: "1.0"
        }
      };
    }
  }
  
  private async executeWithTimeout<T>(
    handler: () => Promise<T>,
    request: RequestEnvelope
  ): Promise<T> {
    const timeoutMs = this.getTimeoutForMethod(request.method);
    
    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        reject(new RpcError(408, "Request timeout", { timeoutMs }, true));
      }, timeoutMs);
      
      handler()
        .then(result => {
          clearTimeout(timeout);
          resolve(result);
        })
        .catch(error => {
          clearTimeout(timeout);
          reject(error);
        });
    });
  }
  
  private getCircuitBreaker(method: string): CircuitBreaker {
    if (!this.circuitBreakers.has(method)) {
      this.circuitBreakers.set(method, new CircuitBreaker({
        failureThreshold: 5,
        recoveryTimeout: 30000,
        successThreshold: 3
      }));
    }
    return this.circuitBreakers.get(method)!;
  }
  
  private getTimeoutForMethod(method: string): number {
    // Implementation to get timeout based on method pattern
    return 5000; // Default timeout
  }
}
```

## Observability and Monitoring

### Telemetry and Tracing
```typescript
interface TelemetrySystem {
  tracing: {
    implementation: "OpenTelemetry compatible distributed tracing";
    propagation: "W3C Trace Context propagation headers";
    sampling: "Configurable sampling rates per service";
    export: "Jaeger, Zipkin, or custom trace exporters";
  };
  
  metrics: {
    types: ["Counter", "Histogram", "Gauge", "Summary"];
    labels: ["method", "status", "service", "version"];
    collection: "Prometheus-compatible metrics collection";
    alerting: "Configurable alerting rules";
  };
  
  logging: {
    format: "Structured JSON logging";
    levels: ["DEBUG", "INFO", "WARN", "ERROR", "FATAL"];
    correlation: "Trace and correlation ID injection";
    aggregation: "Centralized log aggregation";
  };
}

class TelemetryCollector {
  private tracer: Tracer;
  private metrics: MetricsRegistry;
  private logger: Logger;
  
  constructor() {
    this.tracer = trace.getTracer('rpc-system');
    this.metrics = new MetricsRegistry();
    this.logger = new Logger('rpc-system');
  }
  
  async instrumentRequest<T>(
    request: RequestEnvelope,
    handler: () => Promise<T>
  ): Promise<T> {
    const span = this.tracer.startSpan(`rpc.${request.method}`, {
      attributes: {
        'rpc.method': request.method,
        'rpc.service': request.destination,
        'rpc.client': request.origin,
        'rpc.request_id': request.id
      }
    });
    
    const startTime = Date.now();
    
    try {
      const result = await handler();
      
      // Record success metrics
      this.metrics.counter('rpc_requests_total', {
        method: request.method,
        status: 'success'
      }).inc();
      
      this.metrics.histogram('rpc_request_duration_ms', {
        method: request.method
      }).observe(Date.now() - startTime);
      
      span.setStatus({ code: SpanStatusCode.OK });
      
      return result;
      
    } catch (error) {
      // Record error metrics
      this.metrics.counter('rpc_requests_total', {
        method: request.method,
        status: 'error'
      }).inc();
      
      span.setStatus({
        code: SpanStatusCode.ERROR,
        message: error.message
      });
      
      span.recordException(error);
      
      throw error;
      
    } finally {
      span.end();
      
      // Log request completion
      this.logger.info('RPC request completed', {
        method: request.method,
        duration: Date.now() - startTime,
        traceId: request.headers.traceId,
        requestId: request.id
      });
    }
  }
}
```

## Transport Implementation

### Unified RPC Client
```typescript
class UnifiedRpcClient {
  private transports: Map<string, Transport>;
  private loadBalancer: LoadBalancer;
  private errorHandler: RpcErrorHandler;
  private telemetry: TelemetryCollector;
  
  constructor(config: RpcClientConfig) {
    this.transports = new Map();
    this.loadBalancer = new LoadBalancer(config.loadBalancing);
    this.errorHandler = new RpcErrorHandler(config.reliability);
    this.telemetry = new TelemetryCollector();
    
    // Initialize transports
    this.initializeTransports(config);
  }
  
  async call<T>(
    method: string,
    params: any,
    options?: CallOptions
  ): Promise<T> {
    const request: RequestEnvelope = {
      id: generateUUID(),
      origin: this.getClientId(),
      destination: await this.resolveDestination(method),
      timestamp: Date.now(),
      method,
      params,
      headers: {
        traceId: options?.traceId || generateTraceId(),
        ttl: options?.timeout || 30000,
        priority: options?.priority || "normal"
      },
      version: "1.0"
    };
    
    return this.telemetry.instrumentRequest(request, async () => {
      const transport = await this.selectTransport(method, options);
      const response = await this.errorHandler.handleRequest(request, () =>
        transport.send(request)
      );
      
      if (response.error) {
        throw new RpcError(
          response.error.code,
          response.error.message,
          response.error.details,
          response.error.retryable
        );
      }
      
      return response.result;
    });
  }
  
  async stream<T>(
    method: string,
    params: any,
    options?: StreamOptions
  ): AsyncIterable<T> {
    const transport = await this.selectTransport(method, options);
    
    if (!transport.supportsStreaming()) {
      throw new Error(`Transport does not support streaming: ${transport.name}`);
    }
    
    const request: RequestEnvelope = {
      id: generateUUID(),
      origin: this.getClientId(),
      destination: await this.resolveDestination(method),
      timestamp: Date.now(),
      method,
      params,
      headers: {
        traceId: options?.traceId || generateTraceId(),
        ttl: options?.timeout || 300000, // Longer timeout for streams
        priority: options?.priority || "normal"
      },
      version: "1.0"
    };
    
    yield* transport.stream(request);
  }
  
  private async selectTransport(
    method: string,
    options?: CallOptions
  ): Promise<Transport> {
    const transportName = this.getPreferredTransport(method, options);
    const transport = this.transports.get(transportName);
    
    if (!transport) {
      throw new Error(`Transport not available: ${transportName}`);
    }
    
    return transport;
  }
  
  private getPreferredTransport(method: string, options?: CallOptions): string {
    // Determine best transport based on method and options
    if (options?.streaming) return "websocket";
    if (method.startsWith("internal.")) return "jsonrpc";
    if (options?.performance === "high") return "grpc";
    return "rest";
  }
}

interface CallOptions {
  timeout?: number;
  priority?: "low" | "normal" | "high" | "critical";
  traceId?: string;
  streaming?: boolean;
  performance?: "standard" | "high";
}

interface StreamOptions extends CallOptions {
  bufferSize?: number;
  backpressure?: boolean;
}
```

## Development and Testing Tools

### RPC Testing Framework
```typescript
class RpcTestClient {
  private client: UnifiedRpcClient;
  private mockTransport: MockTransport;
  
  constructor() {
    this.mockTransport = new MockTransport();
    this.client = new UnifiedRpcClient({
      transports: { mock: this.mockTransport },
      defaultTransport: "mock"
    });
  }
  
  // Mock response for testing
  mockResponse(method: string, response: any): void {
    this.mockTransport.addMockResponse(method, response);
  }
  
  // Mock error for testing
  mockError(method: string, error: RpcError): void {
    this.mockTransport.addMockError(method, error);
  }
  
  // Test method call
  async testCall(method: string, params: any): Promise<any> {
    return this.client.call(method, params);
  }
  
  // Test timeout behavior
  async testTimeout(method: string, params: any, timeoutMs: number): Promise<void> {
    this.mockTransport.addDelay(method, timeoutMs + 1000);
    
    try {
      await this.client.call(method, params, { timeout: timeoutMs });
      throw new Error("Expected timeout error");
    } catch (error) {
      if (error.code !== 408) {
        throw error;
      }
    }
  }
  
  // Test retry behavior
  async testRetry(method: string, params: any, failureCount: number): Promise<any> {
    this.mockTransport.addFailures(method, failureCount);
    return this.client.call(method, params);
  }
}

// CLI testing tool
class RpcCliTester {
  private client: UnifiedRpcClient;
  
  constructor(config: RpcClientConfig) {
    this.client = new UnifiedRpcClient(config);
  }
  
  async runTest(args: string[]): Promise<void> {
    const [method, paramsJson] = args;
    const params = JSON.parse(paramsJson || '{}');
    
    console.log(`Testing RPC call: ${method}`);
    console.log(`Parameters: ${JSON.stringify(params, null, 2)}`);
    
    try {
      const startTime = Date.now();
      const result = await this.client.call(method, params);
      const duration = Date.now() - startTime;
      
      console.log(`✅ Success (${duration}ms)`);
      console.log(`Result: ${JSON.stringify(result, null, 2)}`);
      
    } catch (error) {
      console.log(`❌ Error: ${error.message}`);
      console.log(`Code: ${error.code}`);
      console.log(`Retryable: ${error.retryable}`);
    }
  }
}

// Usage: node rpc_test_client.js memory.query '{"q": "cat"}'
```

## Future Enhancements

### Advanced Features
```typescript
interface FutureEnhancements {
  protocolUpgrades: {
    http3: "HTTP/3 with QUIC for improved performance";
    grpcWeb: "gRPC-Web for browser compatibility";
    webrtc: "WebRTC for peer-to-peer communication";
    messageQueues: "Integration with message queue systems";
  };
  
  securityEnhancements: {
    mutualTls: "Mutual TLS authentication for all connections";
    tokenRotation: "Automatic token rotation and refresh";
    rateLimiting: "Advanced rate limiting with quotas";
    encryption: "End-to-end encryption for sensitive data";
  };
  
  performanceOptimizations: {
    connectionPooling: "Intelligent connection pooling";
    requestBatching: "Automatic request batching";
    compressionOptimization: "Adaptive compression algorithms";
    cachingLayer: "Intelligent response caching";
  };
  
  observabilityEnhancements: {
    distributedTracing: "Enhanced distributed tracing";
    realTimeMetrics: "Real-time performance metrics";
    anomalyDetection: "AI-powered anomaly detection";
    predictiveAnalytics: "Predictive performance analytics";
  };
}
```

---

**Implementation Status**: Core protocol specification complete, reference implementation in development
**Dependencies**: Service Discovery, Security Framework, Monitoring Infrastructure
**Performance Target**: Sub-10ms local latency, 99.9% reliability, linear scalability 