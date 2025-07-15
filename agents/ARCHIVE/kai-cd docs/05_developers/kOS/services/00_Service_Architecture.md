---
title: "Service Architecture"
description: "Technical specification for service architecture"
type: "service"
status: "current"
priority: "medium"
last_updated: "2025-06-22"
agent_notes: "AI agent guidance for implementing service architecture"
---

# 01: kOS Service Architecture

> **Source**: `documentation/brainstorm/kOS/09_service_architecture.md`  
> **Migrated**: 2025-01-20  
> **Status**: Foundation Document

## Overview

This document details the complete modular service architecture of the kOS and kAI platform, including system components, communication protocols, software modules, and deployment models. It serves as the core blueprint for infrastructure and runtime integration.

## Architectural Layers

### User Layer (Client Interfaces)

#### kAI Web Application (kai-cd)
- **Framework**: React + Tailwind CSS
- **Features**: Built-in theme engine and accessibility layer
- **Deployment**: Chrome extension (tab/popup/sidepanel)
- **Communication**: WebSocket API + REST API client
- **Capabilities**: Plugin UIs, iframe sandboxed services, real-time interaction

#### kAI Terminal Interface (CLI)
- **Runtime**: Node.js REPL + Python fallback
- **Purpose**: Local agent control and diagnostic tools
- **Security**: Encrypted local config and vault integration

#### Mobile Client (Planned)
- **Framework**: React Native app wrapper for core kAI modules
- **Features**: Push notifications, camera/mic sensor integration

### Control Layer

#### Agent Mesh Runtime
- **Orchestrator**: kCore manages all agents
- **Registry**: All agents registered with `manifest.json`
- **Authentication**: Mutual auth via Ed25519 identity keys
- **Deployment Options**:
  - localhost (default)
  - LAN via mDNS
  - Cloud RPC (gRPC/WebSocket)

#### Central Orchestration Bus
- **Message Broker**: Redis pub/sub or NATS for lightweight broadcasting
- **WebSocket Relay**: Server for browser ↔ backend messaging
- **API Gateway**: FastAPI / Envoy / Nginx

### Infrastructure Layer

#### Backend Services
- **Core API**: FastAPI service
- **Orchestration**: LangChain for chaining operations
- **Task Queue**: Celery for async task processing
- **Vector Storage**: Chroma, Qdrant, Weaviate managers
- **Security**: Secure Vault API (AES-256 local or remote KMS)

#### Data Stores
- **Primary Database**: PostgreSQL for structured data
- **Cache**: Redis for short-term memory and sessions
- **File Storage**: S3/GCS for artifacts and documents

#### LLM Provider Interfaces
- **Local Models**: Ollama, llama.cpp, vLLM
- **Remote APIs**: OpenAI, Claude, Gemini, HuggingFace

## Component Architecture

### Prompt Management System
```
components/prompt_manager/
├── PromptStore.ts         # IndexedDB local prompt history
├── PromptProfile.ts       # Named context templates
├── PromptEditor.tsx       # WYSIWYG + markdown hybrid
├── PromptRenderer.ts      # Inject runtime variables
├── PromptVaultAdapter.ts  # Connect to secure vault
```

### Agent Mesh Components
```
services/agents/
├── kCore/                 # Orchestrator runtime
├── kPlanner/              # Goal decomposition
├── kExecutor/             # Task runners
├── kReviewer/             # QA and test evaluation
├── kSentinel/             # Monitoring and intrusion detection
├── kMemory/               # Memory graph and embedding
├── kPersona/              # Persona config and modulation
├── kBridge/               # API proxies and adapters
```

### Artifact Management
```
services/artifact_manager/
├── ArtifactIndex.ts       # Metadata and hash database
├── UploadHandler.ts       # File and blob intake
├── PreviewRenderer.tsx    # Markdown, image, PDF rendering
├── ShareLink.ts           # Temporary signed URLs
├── SignatureVerifier.ts   # Blockchain-backed checksum (planned)
```

### Configuration & Vault System
```
config/
├── system_config.json     # Global toggles, logging, themes
├── user_config.json       # Local overrides, profile info
├── vault/
│   ├── secrets.db         # AES-encrypted SQLite store
│   └── policy.json        # Access rules and TTL config
```

## Core Protocols & Service APIs

### WebSocket Message Structure
```json
{
  "type": "AGENT_RESULT",
  "agent": "kExecutor:webscraper",
  "task_id": "xyz123",
  "payload": {
    "status": "success",
    "data": { ... }
  },
  "timestamp": "2025-06-20T23:05:00Z"
}
```

### Internal Service APIs
- `POST /agent/task` → Submit new goal or subtask
- `GET /agent/status` → List agent health and state
- `POST /vault/encrypt` / `POST /vault/decrypt` → Vault operations
- `POST /artifact/upload` / `GET /artifact/:id` → Artifact management
- `GET /memory/search?q=...` → Memory retrieval
- `POST /planner/plan` → Task planning

## Deployment Models

### Localhost (Developer Mode)
- **Scope**: All services and agents on single machine
- **Stack**: Local SQLite + Ollama + FastAPI
- **Interface**: CLI + Web UI on `http://localhost:3000`

### Home Server (Self-Hosted Node)
- **Containerization**: Docker Compose with shared volumes
- **Isolation**: Agents in separate containers
- **Access**: Optional public tunnel (ngrok, tailscale)

### Multi-Tenant Cloud
- **Orchestration**: Kubernetes or Nomad
- **High Availability**: S3, Postgres, Redis in HA mode
- **Management**: Central admin UI for tenant control

### Federated Mesh (Planned)
- **Architecture**: Peered mesh of kCore nodes
- **Consensus**: Each node signs and publishes to shared ledger
- **Sync**: IPFS or RAG-2 knowledge synchronization

## Security Framework

### Core Security Components
- **Vault**: AES-256 + PBKDF2 local, or KMS cloud mode
- **Authentication**: JWT / OAuth2 for user and agent tokens
- **Agent Communication**: Ed25519 signatures for all KLP messages
- **Plugin Security**: WebWorker or nsjail-based sandboxing

### kSentinel Security Monitoring
- **Rate Limiting**: Request throttling and anomaly detection
- **Audit Trail**: Execution trace logging
- **Resource Monitoring**: CPU, memory, network usage tracking
- **Intrusion Detection**: Behavioral analysis and alerting

## System Observability

### Monitoring Stack
- **Logging**: Grafana + Loki for log aggregation and dashboard
- **Metrics**: Prometheus for agent performance monitoring
- **Tracing**: Jaeger for task trace and profiling
- **Lightweight Debug**: SQLite log adapter for development

### Observability Features
- Real-time agent performance metrics
- Task execution tracing and profiling
- System resource utilization monitoring
- Error tracking and alerting

## Naming Conventions & Standards

### Service Conventions
- **Service Routes**: Follow `/service_name/function` pattern
- **Agent IDs**: Follow `kClass:name` format
- **Log Tagging**: All internal logs tagged with task ID and plan ID
- **Configuration**: Deep merge resolution for config file overrides

### Code Organization
- Modular service architecture
- Clear separation of concerns
- Standardized API interfaces
- Consistent error handling patterns

## Development Roadmap

### Phase 1: Core Services
- Basic agent mesh implementation
- Core API and WebSocket communication
- Local storage and configuration management

### Phase 2: Advanced Features
- Vector storage integration
- Advanced security features
- Multi-deployment support

### Phase 3: Federation
- Federated mesh networking
- Advanced consensus mechanisms
- Cross-node knowledge synchronization

---

### Related Documents
- [System Overview](../architecture/01_System_Overview.md) - High-level system architecture
- [Agent Framework](../agents/01_Agent_Framework.md) - Agent system details
- [Security Architecture](../security/01_Security_Architecture.md) - Security framework

### External References
- [FastAPI Documentation](https://fastapi.tiangolo.com/) - API framework
- [Docker Compose](https://docs.docker.com/compose/) - Container orchestration
- [Kubernetes](https://kubernetes.io/) - Container orchestration platform

