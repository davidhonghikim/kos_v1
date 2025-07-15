---
title: "Service Architecture and System Topology"
description: "Complete modular service architecture of kOS and kAI platform including low-level component breakdowns, communication protocols, software modules, and deployment models"
category: "services"
subcategory: "architecture"
context: "future/kos-vision"
implementation_status: "planned"
decision_scope: "system-wide"
complexity: "high"
last_updated: "2024-01-20"
code_references: [
  "services/agents/",
  "components/prompt_manager/",
  "services/artifact_manager/",
  "config/"
]
related_documents: [
  "future/services/04_system-services-stack.md",
  "future/architecture/04_kos-core-architecture.md",
  "future/agents/03_agent-protocols-and-hierarchy.md"
]
dependencies: [
  "Agent Mesh Runtime",
  "Central Orchestration Bus",
  "Backend Services",
  "Data Stores"
]
breaking_changes: [
  "Complete service architecture redesign",
  "New communication protocols",
  "Enhanced security components"
]
agent_notes: [
  "Defines complete modular service architecture",
  "Contains detailed component breakdowns and protocols",
  "Critical reference for infrastructure implementation",
  "Includes deployment models and security specifications"
]
---

# Service Architecture and System Topology

> **Agent Context**: This document details the complete modular service architecture of the kOS and kAI platform. Use this when implementing infrastructure components, understanding system topology, or designing service communication protocols. All specifications include low-level breakdowns for runtime integration and deployment.

## Quick Summary
Comprehensive service architecture defining architectural layers, component breakdowns, communication protocols, deployment models, and security components for the complete kOS and kAI platform with detailed infrastructure specifications.

## Architectural Layers

### User Layer (Client Interfaces)

#### kAI Web Application (kai-cd)
```typescript
interface KAIWebApp {
  technology: {
    frontend: 'React + Tailwind CSS';
    features: ['theme engine', 'accessibility layer'];
    deployment: ['Chrome extension', 'tab', 'popup', 'sidepanel'];
  };
  communication: {
    realtime: 'WebSocket API';
    rest: 'REST API client';
    features: ['plugin UIs', 'iframe sandboxed services'];
  };
  capabilities: 'real-time interaction with agent mesh';
}
```

#### kAI Terminal Interface (CLI)
```typescript
interface KAITerminal {
  runtime: 'Node.js REPL + Python fallback';
  features: [
    'local agent control',
    'diagnostic tools',
    'encrypted local config',
    'vault integration'
  ];
  usage: 'development and administrative tasks';
}
```

#### Mobile Client (Planned)
```typescript
interface MobileClient {
  technology: 'React Native app wrapper';
  features: [
    'push notifications',
    'camera/mic sensors',
    'core kAI modules'
  ];
  deployment: 'iOS and Android platforms';
}
```

### Control Layer

#### Agent Mesh Runtime
```typescript
interface AgentMeshRuntime {
  orchestrator: {
    component: 'kCore';
    responsibility: 'orchestrates all agents';
  };
  registration: {
    manifest: 'manifest.json';
    authentication: 'Ed25519 identity keys';
  };
  deployment: {
    localhost: 'default deployment';
    lan: 'mDNS discovery';
    cloud: 'gRPC/WebSocket RPC';
  };
}
```

#### Central Orchestration Bus
```typescript
interface OrchestrationBus {
  messaging: {
    lightweight: 'Redis pub/sub or NATS';
    relay: 'WebSocket server for browser ↔ backend';
  };
  gateway: {
    options: ['FastAPI', 'Envoy', 'Nginx'];
    purpose: 'API request routing and load balancing';
  };
}
```

### Infrastructure Layer

#### Backend Services
```typescript
interface BackendServices {
  core: {
    api: 'FastAPI (core API service)';
    orchestration: 'LangChain for chaining';
    async: 'Celery for async tasks';
  };
  storage: {
    vector: 'Chroma, Qdrant, Weaviate';
    vault: 'AES-256 local or remote KMS';
  };
}
```

#### Data Stores
```typescript
interface DataStores {
  structured: {
    primary: 'PostgreSQL';
    features: ['ACID compliance', 'JSON support'];
  };
  cache: {
    service: 'Redis';
    usage: ['cache', 'short-term memory'];
  };
  artifacts: {
    storage: 'S3/GCS';
    purpose: 'file and artifact storage';
  };
}
```

#### LLM Provider Interfaces
```typescript
interface LLMProviders {
  local: {
    services: ['Ollama', 'llama.cpp', 'vLLM'];
    deployment: 'self-hosted inference';
  };
  remote: {
    apis: ['OpenAI', 'Claude', 'Gemini', 'HuggingFace'];
    integration: 'HTTP client with rate limiting';
  };
}
```

## Component Breakdown by Subsystem

### Prompt Management System
```text
components/prompt_manager/
├── PromptStore.ts         # IndexedDB local prompt history
├── PromptProfile.ts       # Named context templates
├── PromptEditor.tsx       # WYSIWYG + markdown hybrid
├── PromptRenderer.ts      # Inject runtime variables
├── PromptVaultAdapter.ts  # Connect to secure vault
```

#### Implementation Specifications
```typescript
interface PromptManagementSystem {
  storage: {
    local: 'IndexedDB for browser persistence';
    backend: 'PostgreSQL for server storage';
  };
  features: {
    versioning: 'full prompt version history';
    templates: 'reusable prompt templates';
    variables: 'dynamic variable injection';
    security: 'vault integration for sensitive prompts';
  };
}
```

### Agent Mesh Architecture
```text
services/agents/
├── kCore/                  # Orchestrator runtime
├── kPlanner/               # Goal decomposition
├── kExecutor/              # Task runners
├── kReviewer/              # QA and test evaluation
├── kSentinel/              # Monitoring and intrusion detection
├── kMemory/                # Memory graph and embedding
├── kPersona/               # Persona config and modulation
├── kBridge/                # API proxies and adapters
```

#### Agent Service Specifications
```typescript
interface AgentServices {
  kCore: {
    role: 'Global orchestrator and coordinator';
    responsibilities: ['agent lifecycle', 'task routing', 'system health'];
  };
  kPlanner: {
    role: 'Goal decomposition and task planning';
    capabilities: ['task graphs', 'dependency resolution', 'optimization'];
  };
  kExecutor: {
    role: 'Task execution and action performance';
    features: ['parallel execution', 'resource management', 'error handling'];
  };
  kReviewer: {
    role: 'Quality assurance and validation';
    functions: ['output verification', 'test coverage', 'compliance checks'];
  };
}
```

### Artifact Manager
```text
services/artifact_manager/
├── ArtifactIndex.ts        # Metadata and hash DB
├── UploadHandler.ts        # File and blob intake
├── PreviewRenderer.tsx     # Markdown, image, and PDF rendering
├── ShareLink.ts            # Temporary signed URLs
├── SignatureVerifier.ts    # Blockchain-backed checksum (planned)
```

#### Artifact Management Implementation
```typescript
interface ArtifactManager {
  indexing: {
    metadata: 'comprehensive file metadata storage';
    hashing: 'content-based deduplication';
    search: 'full-text and semantic search';
  };
  processing: {
    upload: 'multi-format file intake';
    preview: 'real-time preview generation';
    sharing: 'secure temporary access links';
  };
  security: {
    verification: 'cryptographic integrity checks';
    access: 'role-based permission system';
  };
}
```

### Configuration and Vault System
```text
config/
├── system_config.json      # Global toggles, logging, themes
├── user_config.json        # Local overrides, profile info
├── vault/
│   ├── secrets.db          # AES-encrypted SQLite store
│   └── policy.json         # Access rules and TTL config
```

#### Configuration Architecture
```typescript
interface ConfigurationSystem {
  hierarchy: {
    system: 'global system configuration';
    user: 'user-specific overrides';
    vault: 'encrypted sensitive data';
  };
  features: {
    hotReload: 'runtime configuration updates';
    validation: 'schema-based configuration validation';
    backup: 'automatic configuration backup';
  };
}
```

## Core Protocols and Service APIs

### WebSocket Message Structure
```typescript
interface WebSocketMessage {
  type: 'AGENT_RESULT' | 'TASK_REQUEST' | 'STATUS_UPDATE' | 'ERROR';
  agent: string;           // e.g., "kExecutor:webscraper"
  task_id: string;
  payload: {
    status: 'success' | 'error' | 'pending';
    data: any;
  };
  timestamp: string;       // ISO 8601 format
}

// Example message
const exampleMessage: WebSocketMessage = {
  type: "AGENT_RESULT",
  agent: "kExecutor:webscraper",
  task_id: "xyz123",
  payload: {
    status: "success",
    data: { url: "https://example.com", content: "..." }
  },
  timestamp: "2025-06-20T23:05:00Z"
};
```

### Internal Service APIs
```typescript
interface ServiceAPIs {
  agent: {
    endpoints: {
      submitTask: 'POST /agent/task';
      getStatus: 'GET /agent/status';
      listAgents: 'GET /agent/list';
    };
  };
  vault: {
    endpoints: {
      encrypt: 'POST /vault/encrypt';
      decrypt: 'POST /vault/decrypt';
      store: 'POST /vault/store';
    };
  };
  artifact: {
    endpoints: {
      upload: 'POST /artifact/upload';
      get: 'GET /artifact/:id';
      search: 'GET /artifact/search';
    };
  };
  memory: {
    endpoints: {
      search: 'GET /memory/search?q=...';
      store: 'POST /memory/store';
      recall: 'GET /memory/recall/:id';
    };
  };
  planner: {
    endpoints: {
      plan: 'POST /planner/plan';
      status: 'GET /planner/status/:id';
    };
  };
}
```

## Deployment Models

### Localhost (Developer Mode)
```typescript
interface LocalhostDeployment {
  architecture: 'single machine deployment';
  services: [
    'local SQLite database',
    'Ollama for local LLM inference',
    'FastAPI backend service'
  ];
  access: 'http://localhost:3000 for web UI';
  features: ['rapid development', 'offline capability', 'full feature set'];
}
```

### Home Server (Self-Hosted Node)
```typescript
interface HomeServerDeployment {
  orchestration: 'Docker Compose with shared volumes';
  isolation: 'agents in separate containers';
  networking: 'optional public tunnel (ngrok, tailscale)';
  features: ['multi-user support', 'persistent storage', 'remote access'];
}
```

### Multi-Tenant Cloud
```typescript
interface CloudDeployment {
  orchestration: 'Kubernetes or Nomad';
  infrastructure: 'S3, Postgres, Redis in HA mode';
  management: 'central admin UI for tenant control';
  features: ['horizontal scaling', 'high availability', 'enterprise features'];
}
```

### Federated Mesh (Planned)
```typescript
interface FederatedMesh {
  topology: 'peered mesh of kCore nodes';
  consensus: 'each node signs and publishes blocks to shared ledger';
  synchronization: 'IPFS or RAG-2 knowledge sync';
  features: ['decentralized operation', 'cross-node collaboration'];
}
```

## Security Components

### Comprehensive Security Architecture
```typescript
interface SecurityComponents {
  vault: {
    local: 'AES-256 + PBKDF2';
    cloud: 'KMS integration';
    features: ['key rotation', 'audit logging'];
  };
  authentication: {
    user: 'JWT / OAuth2 tokens';
    agent: 'Ed25519 signatures via KLP';
  };
  isolation: {
    plugins: 'WebWorker or nsjail-based sandboxing';
    processes: 'container isolation';
  };
  monitoring: {
    sentinel: 'kSentinel agent hooks';
    features: [
      'rate limiting',
      'anomaly detection',
      'execution trace logging',
      'resource monitoring (CPU, memory, network)'
    ];
  };
}
```

### Security Implementation Details
```typescript
interface SecurityImplementation {
  encryption: {
    atRest: 'AES-256-GCM for stored data';
    inTransit: 'TLS 1.3 for all communications';
    keys: 'Ed25519 for agent identity';
  };
  access: {
    rbac: 'role-based access control';
    permissions: 'fine-grained resource permissions';
    audit: 'comprehensive audit trail';
  };
  validation: {
    input: 'all inputs validated and sanitized';
    output: 'output verification and filtering';
    integrity: 'cryptographic integrity checks';
  };
}
```

## System Observability

### Monitoring Stack
```typescript
interface MonitoringStack {
  logging: {
    collection: 'Grafana + Loki for log aggregation';
    format: 'structured JSON logging';
    retention: 'configurable retention policies';
  };
  metrics: {
    collection: 'Prometheus for metrics';
    visualization: 'Grafana dashboards';
    alerting: 'threshold-based alerts';
  };
  tracing: {
    distributed: 'Jaeger for task tracing';
    profiling: 'performance profiling';
  };
  debugging: {
    local: 'SQLite log adapter for lightweight debugging';
    tools: 'integrated debugging tools';
  };
}
```

### Observability Implementation
```typescript
interface ObservabilityFeatures {
  realtime: {
    dashboard: 'real-time system health dashboard';
    alerts: 'immediate notification of issues';
  };
  historical: {
    trends: 'long-term performance trends';
    analysis: 'historical data analysis';
  };
  debugging: {
    tracing: 'end-to-end request tracing';
    logs: 'centralized log search and analysis';
  };
}
```

## Naming Conventions & Standards

### Service Conventions
```typescript
interface NamingConventions {
  routes: {
    format: '/service_name/function';
    example: '/agent/execute, /vault/decrypt';
  };
  agents: {
    format: 'kClass:name';
    examples: ['kCore:main', 'kExecutor:webscraper'];
  };
  logging: {
    tags: 'all logs tagged with task_id and plan_id';
    format: 'structured JSON with consistent fields';
  };
  configuration: {
    resolution: 'deep merge for config file overrides';
    hierarchy: 'system < user < environment';
  };
}
```

---

