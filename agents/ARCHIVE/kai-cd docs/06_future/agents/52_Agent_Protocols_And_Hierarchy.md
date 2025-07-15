---
title: "Agent Protocols and Role Hierarchy"
description: "Hierarchical structure, communication standards, coordination logic, configuration protocols, and execution framework for all AI agents in kAI and kOS ecosystem"
category: "agents"
subcategory: "protocols"
context: "future/kos-vision"
implementation_status: "planned"
decision_scope: "agent-system-wide"
complexity: "high"
last_updated: "2024-01-20"
code_references: [
  "agents/kCore/",
  "agents/kPlanner/",
  "comms/klp/",
  "config/agents/"
]
related_documents: [
  "future/agents/01_agent-hierarchy.md",
  "future/protocols/01_klp-specification.md",
  "future/architecture/04_kos-core-architecture.md"
]
dependencies: [
  "KLP Protocol",
  "Agent Execution Engine",
  "Security Framework",
  "Message Bus System"
]
breaking_changes: [
  "New agent hierarchy system",
  "Enhanced communication protocols",
  "Redesigned security model"
]
agent_notes: [
  "Defines complete agent role hierarchy and protocols",
  "Contains KLP message specifications and transport protocols",
  "Critical reference for agent coordination implementation",
  "Includes execution lifecycle and failure handling"
]
---

# Agent Protocols and Role Hierarchy

> **Agent Context**: This document defines the hierarchical structure, communication standards, and execution framework for all AI agents in the kAI and kOS ecosystem. Use this when implementing agent coordination, designing communication protocols, or understanding agent lifecycle management. All specifications support modular, extensible, and secure coordination across distributed environments.

## Quick Summary
Comprehensive agent system design defining role hierarchy, KLP communication protocol, execution lifecycle, configuration management, and observability framework for distributed AI agent coordination in kAI and kOS platforms.

## Agent Role Hierarchy

### Agent Classes by Responsibility Scope

| Class          | Role               | Description                                                                                         | Scope |
| -------------- | ------------------ | --------------------------------------------------------------------------------------------------- | ----- |
| `kCore`        | Primary Controller | Global coordinator agent. Oversees all agent lifecycles, routing, and system configuration.         | System-wide |
| `kCoordinator` | Domain Coordinator | Manages a sub-domain (e.g., Health, Scheduling, Research). Assigns work to planners and evaluators. | Domain-specific |
| `kPlanner`     | Planner Agent      | Converts user goals into tasks. Queries knowledge base, generates task graphs.                      | Task planning |
| `kExecutor`    | Worker Agent       | Executes a single task (code run, API call, data retrieval). Pure execution, no reasoning.          | Task execution |
| `kReviewer`    | Evaluator Agent    | Performs QA, test coverage, output verification, formatting, consistency checking.                  | Quality assurance |
| `kSentinel`    | Security Agent     | Monitors for anomalies, performs boundary enforcement, access control, usage audits.                | Security monitoring |
| `kMemory`      | Memory Agent       | Handles memory retrieval, summarization, embedding, and memory map updates.                         | Memory management |
| `kPersona`     | Persona Host       | Maintains persona constraints, tone, context, user alignment.                                       | Personality management |
| `kBridge`      | Service Proxy      | Acts as a connector between external APIs and internal service mesh.                                | External integration |

### Agent Types by Interaction Mode

```typescript
type AgentInteractionMode = 
  | 'Active'    // Initiates tasks autonomously or by schedule
  | 'Reactive'  // Waits for user or agent requests
  | 'Hybrid';   // Periodically monitors context + responds to triggers

interface AgentConfiguration {
  id: string;
  class: AgentClass;
  mode: AgentInteractionMode;
  autonomyLevel: 'low' | 'medium' | 'high';
  maxConcurrentTasks: number;
  allowedDomains: string[];
}
```

## Inter-Agent Communication (KLP - Kind Link Protocol)

### Message Types Specification
```typescript
type KLPMessageType = 
  | 'TASK_REQUEST'
  | 'TASK_RESULT'
  | 'TASK_ERROR'
  | 'STATUS_UPDATE'
  | 'INTENTION_DECLARATION'
  | 'MEMORY_READ'
  | 'MEMORY_WRITE'
  | 'PLAN_GRAPH'
  | 'SECURITY_ALERT'
  | 'CONFIG_UPDATE';
```

### Complete Message Structure
```typescript
interface KLPMessage {
  type: KLPMessageType;
  from: string;  // Agent identifier (e.g., "kPlanner:research")
  to: string;    // Target agent identifier
  task_id: string;
  payload: {
    action?: string;
    target?: string;
    params?: Record<string, any>;
    data?: any;
  };
  timestamp: string; // ISO 8601 format
  auth: {
    signature: string; // ed25519 signature
    token?: string;    // Optional JWT token
  };
  metadata?: {
    priority?: 'low' | 'medium' | 'high' | 'critical';
    ttl?: number;      // Time to live in seconds
    retryCount?: number;
  };
}
```

### Example Message Implementation
```json
{
  "type": "TASK_REQUEST",
  "from": "kPlanner:research",
  "to": "kExecutor:webscraper",
  "task_id": "abc123",
  "payload": {
    "action": "scrape",
    "target": "https://example.com",
    "params": {
      "depth": 2,
      "format": "markdown"
    }
  },
  "timestamp": "2025-06-20T22:04:00Z",
  "auth": {
    "signature": "ed25519:a1b2c3d4...",
    "token": "eyJhbGciOiJIUzI1NiIs..."
  },
  "metadata": {
    "priority": "medium",
    "ttl": 300
  }
}
```

### Transport Protocols

| Protocol   | Use Case                              | Implementation |
|------------|---------------------------------------|----------------|
| `WebSocket` | Local real-time mesh communication   | socket.io, native WebSocket |
| `gRPC`     | High-performance backend microservices | Protocol Buffers |
| `MQTT`     | Lightweight mesh broadcasting         | MQTT broker |
| `NATS`     | High-performance messaging           | NATS server |
| `REST`     | HTTP-based integration fallback      | FastAPI, Express |

### Authentication and Authorization

#### Mutual Agent Identity
```typescript
interface AgentIdentity {
  publicKey: string;    // Ed25519 or RSA public key
  agentId: string;      // Unique agent identifier
  capabilities: string[]; // List of allowed operations
  trustLevel: number;   // 0-100 trust score
}
```

#### Role-Based Access Control
- **ACL Enforcement**: Via `kSentinel` security agent
- **Token Management**: OAuth2/JWT for API-level authentication
- **Permission Matrix**: Fine-grained operation permissions

## Execution Protocol

### Task Lifecycle Management
```typescript
interface TaskLifecycle {
  phases: [
    'Goal Created',      // by user or kCore
    'Plan Generated',    // by kPlanner
    'Subtasks Spawned',  // sent to kExecutor
    'Execution + Logging', // results reported back
    'Review',           // kReviewer checks integrity
    'Memory Update'     // kMemory embeds/indexes output
  ];
}
```

### Task Traceability Schema
```typescript
interface TaskTrace {
  task_id: string;
  parent_id?: string;
  plan_id: string;
  agent_id: string;
  timestamp: string;
  resource_footprint: {
    cpu_time: number;
    memory_used: number;
    network_bytes: number;
  };
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
}
```

### Failure Handling Protocol
```typescript
interface FailureHandling {
  automaticRetry: {
    maxAttempts: number;
    backoffStrategy: 'exponential' | 'linear' | 'fixed';
    coordinator: 'kCoordinator';
  };
  escalation: {
    toUser: boolean;
    fallbackPlan: boolean;
    alertThreshold: number;
  };
  protection: {
    retryThrottling: boolean;
    loopDetection: boolean;
    circuitBreaker: boolean;
  };
}
```

## Configuration and Synchronization

### Global Agent Manifest
```typescript
// Stored at config/agents/manifest.json
interface AgentManifest {
  agents: Array<{
    id: string;
    type: string;
    class: AgentClass;
    active: boolean;
    version: string;
    lastUpdate: string;
  }>;
  version: string;
  lastModified: string;
}
```

### Individual Agent Configuration
```typescript
// Stored in config/agents/<agent_id>.json
interface IndividualAgentConfig {
  name: string;
  allowed_domains: string[];
  max_tasks: number;
  persona: string;
  autonomy_level: 'low' | 'medium' | 'high';
  enabled: boolean;
  resources: {
    max_memory: string;
    max_cpu_percent: number;
    timeout_seconds: number;
  };
  security: {
    sandbox_mode: boolean;
    allowed_operations: string[];
    restricted_domains: string[];
  };
}
```

### Central Control Dashboard Architecture
```typescript
interface ControlDashboard {
  features: {
    globalStateView: 'real-time agent status monitoring';
    agentControl: 'restart, suspend, reconfigure operations';
    performanceCharts: 'resource utilization graphs';
    messageLogInspection: 'KLP message history and analysis';
    roleReassignment: 'dynamic agent role management';
  };
  implementation: 'React dashboard with WebSocket updates';
}
```

## Observability and Logging

### Event Log Types
```typescript
type LogEventType = 
  | 'agent_startup'
  | 'agent_shutdown'
  | 'message_sent'
  | 'message_received'
  | 'execution_begin'
  | 'execution_end'
  | 'error_occurred'
  | 'security_violation'
  | 'memory_read'
  | 'memory_write'
  | 'config_change';
```

### Storage Architecture
```typescript
interface LogStorage {
  local: {
    path: 'logs/agents/{agent_id}/{date}.log';
    format: 'structured JSON';
    rotation: 'daily';
  };
  cloud: {
    targets: ['Grafana Loki', 'S3 backup'];
    optional: true;
  };
  database: {
    engine: 'sqlite://logs.db';
    purpose: 'indexing and query';
  };
}
```

### Analysis Tools Implementation
```typescript
interface AnalysisTools {
  logParser: {
    component: 'kAI plugin';
    features: ['visualizer UI', 'time series viewer'];
  };
  queryConsole: {
    engine: 'jq equivalent';
    format: 'JSON query interface';
  };
  monitoring: {
    realTime: 'WebSocket-based updates';
    alerts: 'threshold-based notifications';
  };
}
```

## Agent System Directory Structure

```text
kai/
├── agents/
│   ├── kCore/
│   │   ├── controller.py
│   │   ├── config/
│   │   │   ├── system.json
│   │   │   └── defaults.yml
│   │   ├── tasks/
│   │   │   └── startup.py
│   │   └── logs/
│   │       └── controller.log
│   ├── kPlanner/
│   │   ├── planner.py
│   │   ├── prompts/
│   │   └── config/planner.json
│   ├── kExecutor/
│   │   ├── executor.py
│   │   ├── plugins/
│   │   └── config/executor.json
│   ├── kReviewer/
│   ├── kMemory/
│   ├── kPersona/
│   ├── kBridge/
│   └── kSentinel/
├── comms/
│   ├── klp/
│   │   ├── schema.json
│   │   ├── transport_grpc.py
│   │   ├── transport_ws.py
│   │   ├── auth/
│   │   │   ├── signer.py
│   │   │   └── verifier.py
│   │   └── protocol_handler.py
│   └── mesh/
│       ├── local_mesh.py
│       └── remote_mesh.py
├── config/
│   ├── agents/
│   │   ├── manifest.json
│   │   ├── kExecutor:webscraper.json
│   │   └── kPlanner:research.json
│   ├── services.yml
│   └── global_settings.json
├── core/
│   ├── orchestrator.py
│   ├── scheduler.py
│   ├── dispatcher.py
│   └── logger.py
├── data/
│   ├── embeddings/
│   ├── memory/
│   └── vault/
├── logs/
│   ├── kCore/
│   ├── kPlanner/
│   └── global.log
├── plugins/
│   ├── generator_tools/
│   ├── validators/
│   └── external_apis/
├── security/
│   ├── keys/
│   ├── audit/
│   └── policies/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── simulation/
└── ui/
    ├── webapp/
    │   ├── components/
    │   ├── store/
    │   ├── pages/
    │   └── index.tsx
    └── themes/
        └── default.css
```

## Development Roadmap

### Feature Implementation Timeline
| Feature                     | Description                            | Target Version | Priority |
| --------------------------- | -------------------------------------- | -------------- | -------- |
| 🔲 Agent Containerization   | Isolated runtime with audit hooks      | v1.1           | High     |
| 🔲 Persona Overlay System   | Real-time personality modulation       | v1.2           | Medium   |
| 🔲 Distributed Mesh Routing | Agent swarm routing (local + global)   | v2.0           | High     |
| 🔲 ZK Agent Voting          | Zero Knowledge-based decisions         | v2.1           | Medium   |
| 🔲 Hardware Bridge Layer    | Raspberry Pi, ESP32, and robot control | v2.2           | Low      |

### Configuration Standards
```typescript
// Global settings configuration
interface GlobalSettings {
  debug_mode: boolean;
  default_language: string;
  max_parallel_tasks: number;
  enable_mesh: boolean;
  security: {
    require_signatures: boolean;
    audit_all_operations: boolean;
    max_trust_level: number;
  };
}
```

---

