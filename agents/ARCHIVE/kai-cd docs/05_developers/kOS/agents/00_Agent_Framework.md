---
title: "Agent Framework"
description: "Technical specification for agent framework"
type: "agent"
status: "current"
priority: "medium"
last_updated: "2025-06-22"
agent_notes: "AI agent guidance for implementing agent framework"
---

# 01: kOS Agent Framework

> **Source**: `documentation/brainstorm/kOS/04_agent_protocols_and_hierarchy.md`  
> **Migrated**: 2025-01-20  
> **Status**: Foundation Document

## Overview

This document defines the hierarchical structure, communication standards, coordination logic, configuration protocols, and execution framework for all AI agents operating within the kAI and kOS ecosystem. The framework supports modular, extensible, and secure coordination between agents across distributed environments.

## Agent Role Hierarchy

### Agent Classes (by Responsibility Scope)

| Class | Role | Description |
|-------|------|-------------|
| **kCore** | Primary Controller | Global coordinator agent. Oversees all agent lifecycles, routing, and system configuration |
| **kCoordinator** | Domain Coordinator | Manages a sub-domain (e.g., Health, Scheduling, Research). Assigns work to planners and evaluators |
| **kPlanner** | Planner Agent | Converts user goals into tasks. Queries knowledge base, generates task graphs |
| **kExecutor** | Worker Agent | Executes a single task (code run, API call, data retrieval). Pure execution, no reasoning |
| **kReviewer** | Evaluator Agent | Performs QA, test coverage, output verification, formatting, consistency checking |
| **kSentinel** | Security Agent | Monitors for anomalies, performs boundary enforcement, access control, usage audits |
| **kMemory** | Memory Agent | Handles memory retrieval, summarization, embedding, and memory map updates |
| **kPersona** | Persona Host | Maintains persona constraints, tone, context, user alignment |
| **kBridge** | Service Proxy | Acts as a connector between external APIs and internal service mesh |

### Agent Types (by Interaction Mode)

- **Active**: Initiates tasks autonomously or by schedule
- **Reactive**: Waits for user or agent requests
- **Hybrid**: Periodically monitors context + responds to triggers

## Inter-Agent Communication (KLP)

### Message Types

The Kind Link Protocol (KLP) defines the following message types:

- `TASK_REQUEST` - Request for task execution
- `TASK_RESULT` - Task completion result
- `TASK_ERROR` - Task execution error
- `STATUS_UPDATE` - Agent status information
- `INTENTION_DECLARATION` - Agent intention announcement
- `MEMORY_READ/WRITE` - Memory operations
- `PLAN_GRAPH` - Task planning information
- `SECURITY_ALERT` - Security-related notifications
- `CONFIG_UPDATE` - Configuration changes

### Message Structure

```json
{
  "type": "TASK_REQUEST",
  "from": "kPlanner:research",
  "to": "kExecutor:webscraper",
  "task_id": "abc123",
  "payload": {
    "action": "scrape",
    "target": "https://example.com",
    "params": {}
  },
  "timestamp": "2025-06-20T22:04:00Z",
  "auth": {
    "signature": "ed25519:...",
    "token": "..."
  }
}
```

### Transport Protocols

| Protocol | Use Case |
|----------|----------|
| **WebSocket** | Local real-time mesh communication |
| **gRPC** | High-performance backend microservices |
| **MQTT/NATS** | Lightweight mesh broadcasting |
| **REST** | HTTP-based integration fallback |

### Authentication & Authorization

- **Mutual Identity**: Agent identity via Ed25519/RSA keys
- **Access Control**: Role-based ACLs enforced via kSentinel
- **Token Authentication**: API-level auth via OAuth2/JWT

## Execution Protocol

### Task Lifecycle

1. **Goal Created** → by user or kCore
2. **Plan Generated** → by kPlanner
3. **Subtasks Spawned** → sent to kExecutor
4. **Execution + Logging** → results reported back
5. **Review** → kReviewer checks integrity, correctness
6. **Memory Update** → kMemory embeds or indexes output

### Task Traceability

Each task is tagged with:
- `task_id` - Unique task identifier
- `parent_id` - Parent task reference
- `plan_id` - Associated plan identifier
- `agent_id` - Executing agent identifier
- `timestamp` - Execution timestamp
- `resource_footprint` - Resource usage metrics

### Failure Handling

- **Automatic Retry**: Via kCoordinator with exponential backoff
- **Escalation**: To user or fallback plan execution
- **Loop Detection**: Retry throttling and infinite loop prevention

## Configuration Management

### Global Agent Manifest

Stored at `config/agents/manifest.json`:

```json
{
  "agents": [
    {
      "id": "kPlanner:research",
      "type": "planner",
      "class": "kPlanner",
      "active": true
    },
    {
      "id": "kExecutor:webscraper",
      "type": "executor",
      "class": "kExecutor",
      "active": true
    }
  ]
}
```

### Agent Configuration Files

Stored in `config/agents/<agent_id>.json`:

```json
{
  "name": "Research Planner",
  "allowed_domains": ["knowledge", "science"],
  "max_tasks": 5,
  "persona": "Analytical, Efficient",
  "autonomy_level": "high",
  "enabled": true
}
```

### Central Control Dashboard

Planned features:
- Global state visualization
- Agent restart, suspend, reconfigure controls
- Performance monitoring and charts
- Message log inspection interface
- Dynamic role reassignment

## Observability & Logging

### Event Log Types

- Agent startup/shutdown events
- Message sent/received logs
- Execution begin/end timestamps
- Errors and exception details
- Security violation alerts
- Memory read/write operations

### Storage Targets

- **Local Logs**: `logs/agents/agent_id/date.log`
- **Cloud Logs**: Optional Grafana Loki, S3 backup
- **Database**: `sqlite://logs.db` for indexing and queries

### Analysis Tools

- Log parser and visualizer UI (kAI plugin)
- Time series performance viewer
- JSON query console (jq equivalent)
- Real-time monitoring dashboard

## Development Roadmap

| Feature | Description | Target Version |
|---------|-------------|----------------|
| **Agent Containerization** | Isolated runtime with audit hooks | v1.1 |
| **Persona Overlay System** | Real-time personality modulation | v1.2 |
| **Distributed Mesh Routing** | Agent swarm routing (local + global) | v2.0 |
| **ZK Agent Voting** | Zero Knowledge-based decisions | v2.1 |
| **Hardware Bridge Layer** | Raspberry Pi, ESP32, robot control | v2.2 |

## Implementation Considerations

### Security Framework
- Agent identity verification and trust chains
- Sandboxed execution environments
- Resource usage monitoring and limits
- Audit trail maintenance

### Performance Optimization
- Message routing efficiency
- Task scheduling optimization
- Memory usage management
- Network communication overhead

### Scalability Design
- Horizontal agent scaling
- Load balancing strategies
- Fault tolerance mechanisms
- Dynamic resource allocation

---

### Related Documents
- [System Overview](../architecture/01_System_Overview.md) - High-level system architecture
- [KLP Core Protocol](../protocols/01_KLP_Core_Protocol.md) - Communication protocol details
- [Security Architecture](../security/01_Security_Architecture.md) - Security framework

### External References
- [Agent Framework Design Patterns](https://example.com/agent-patterns)
- [Distributed Systems Best Practices](https://example.com/distributed-systems)

