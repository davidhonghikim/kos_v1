---
title: "System Services Stack and Architecture"
description: "Complete system architecture, software stack, service directories, protocols, configuration layouts, and inter-service relationships for kOS and kAI ecosystem"
category: "services"
subcategory: "system-architecture"
context: "future/kos-vision"
implementation_status: "planned"
decision_scope: "system-wide"
complexity: "high"
last_updated: "2024-01-20"
code_references: [
  "services/",
  "frontend/",
  "backend/",
  "config/",
  "agents/"
]
related_documents: [
  "future/architecture/03_kos-technology-stack.md",
  "future/architecture/04_kos-core-architecture.md",
  "future/services/01_service-architecture.md"
]
dependencies: [
  "FastAPI",
  "React",
  "PostgreSQL",
  "Redis",
  "Vector Database",
  "Nginx/Caddy"
]
breaking_changes: [
  "Complete service architecture redesign",
  "New directory structure standards",
  "Enhanced security protocols"
]
agent_notes: [
  "Defines complete system services architecture",
  "Contains detailed directory structures and protocols",
  "Critical reference for fullstack implementation",
  "Includes security, logging, and telemetry systems"
]
---

# System Services Stack and Architecture

> **Agent Context**: This document outlines the complete system architecture, software stack, service directories, protocols, and configuration layouts for the kOS and kAI ecosystem. Use this when implementing system services, understanding inter-service relationships, or designing fullstack components. All specifications support agent coordination, security, and modularity.

## Quick Summary
Comprehensive system architecture defining fullstack services, directory structures, protocols, configuration layouts, and security architecture for the complete kOS and kAI ecosystem with detailed implementation specifications.

## Top-Level Directory Structure

```text
/kindos-root
├── README.md
├── docker-compose.yml
├── .env
├── .gitignore
├── logs/
├── config/
├── services/
├── agents/
├── frontend/
├── backend/
├── data/
├── scripts/
├── tests/
└── documentation/
```

## Fullstack Services Directory

### Complete Services Architecture
```text
/services
├── gateway/                  # Nginx or Caddy config + TLS certs
├── api/                      # FastAPI core services
│   ├── auth/                 # JWT, OAuth2, token validation
│   ├── user/                 # Profiles, configs, permissions
│   ├── agent-orchestrator/  # Agent execution, logging, planning
│   ├── memory/               # Vector DB, embeddings, recall engine
│   ├── artifact/             # Files, images, notes
│   ├── prompt/               # Prompt templates, prompt history
│   ├── security/             # Intrusion detection, vault interfaces
│   └── telemetry/            # Event logs, usage metrics
├── vector-db/               # Qdrant, Chroma, or Weaviate
├── postgres/                # PostgreSQL DB service
├── redis/                   # In-memory cache, Celery broker
├── rabbitmq/                # Optional queue broker
└── vault/                   # Secrets management, Hashicorp Vault
```

### Service Implementation Details

#### Gateway Service
```typescript
interface GatewayConfig {
  proxy: {
    api: 'http://backend:8000';
    frontend: 'http://frontend:3000';
    vectordb: 'http://vector-db:6333';
  };
  tls: {
    certPath: '/etc/ssl/certs/kindos.crt';
    keyPath: '/etc/ssl/private/kindos.key';
    autoRenew: boolean;
  };
  rateLimit: {
    global: '1000/hour';
    api: '100/minute';
    auth: '10/minute';
  };
}
```

#### API Services Architecture
```typescript
interface APIServices {
  auth: {
    endpoints: ['/login', '/logout', '/refresh', '/validate'];
    methods: ['JWT', 'OAuth2', 'Ed25519'];
    storage: 'Redis sessions + PostgreSQL users';
  };
  user: {
    endpoints: ['/profile', '/preferences', '/permissions'];
    features: ['RBAC', 'user configs', 'agent permissions'];
  };
  agentOrchestrator: {
    endpoints: ['/agents', '/tasks', '/logs', '/planning'];
    features: ['execution', 'logging', 'planning', 'monitoring'];
  };
  memory: {
    endpoints: ['/embeddings', '/search', '/recall'];
    backends: ['vector DB', 'graph DB', 'cache layer'];
  };
}
```

## Frontend Directory Structure

### Complete Frontend Architecture
```text
/frontend
├── public/
├── src/
│   ├── components/
│   │   ├── common/
│   │   ├── services/
│   │   ├── prompts/
│   │   ├── dashboard/
│   │   ├── artifacts/
│   │   └── memory/
│   ├── pages/
│   │   ├── index.tsx
│   │   ├── settings.tsx
│   │   └── agent-center.tsx
│   ├── contexts/
│   ├── state/
│   ├── styles/
│   ├── utils/
│   ├── assets/
│   └── App.tsx
├── tailwind.config.js
├── tsconfig.json
└── vite.config.ts
```

### Frontend Technology Stack
```typescript
interface FrontendStack {
  framework: 'React 18+ with TypeScript';
  styling: 'Tailwind CSS + ShadCN/UI';
  stateManagement: 'Zustand + React Query';
  routing: 'React Router v6';
  build: 'Vite with ESM';
  testing: 'Vitest + React Testing Library';
}
```

## Backend Directory Layout

### FastAPI Backend Structure
```text
/backend
├── main.py
├── app/
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── logging.py
│   ├── models/
│   ├── schemas/
│   ├── routers/
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── prompts.py
│   │   ├── memory.py
│   │   ├── agents.py
│   │   ├── files.py
│   │   ├── system.py
│   │   └── telemetry.py
│   ├── services/
│   │   ├── vector_store.py
│   │   ├── prompt_engine.py
│   │   ├── memory.py
│   │   └── orchestrator.py
│   └── utils/
├── celery_worker.py
└── requirements.txt
```

### Backend Implementation Standards
```python
# Example service implementation
from fastapi import FastAPI, Depends
from app.core.security import get_current_user
from app.services.orchestrator import AgentOrchestrator

app = FastAPI(title="kOS API", version="1.0.0")

@app.post("/agents/execute")
async def execute_agent_task(
    task: TaskRequest,
    user: User = Depends(get_current_user),
    orchestrator: AgentOrchestrator = Depends()
):
    """Execute agent task with full traceability"""
    result = await orchestrator.execute_task(
        task=task,
        user_id=user.id,
        trace_enabled=True
    )
    return result
```

## Configuration Directory Structure

### Modular Configuration System
```text
/config
├── agents/
│   ├── manifest.json
│   ├── kPlanner:dev.json
│   ├── kExecutor:web.json
│   └── ...
├── services/
│   ├── vector-db.json
│   ├── memory.json
│   ├── gateway.json
│   └── auth.json
├── ui/
│   ├── themes.json
│   ├── components.json
│   └── layout.json
├── security/
│   ├── vault.json
│   ├── keys/
│   └── auth-policies.json
└── system.json
```

### Configuration Schema Examples
```typescript
// config/system.json
interface SystemConfig {
  environment: 'development' | 'staging' | 'production';
  debug: boolean;
  logging: {
    level: 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR';
    format: 'json' | 'text';
    rotation: 'daily' | 'weekly';
  };
  security: {
    requireAuth: boolean;
    encryptionKey: string;
    sessionTimeout: number;
  };
  agents: {
    maxConcurrent: number;
    defaultTimeout: number;
    memoryLimit: string;
  };
}
```

## System-Level Protocols & APIs

### Protocol Specifications
```typescript
interface SystemProtocols {
  internal: {
    api: 'REST + gRPC';
    realtime: 'FastAPI WebSocket / socket.io';
    agentComm: 'KLP (Kind Link Protocol)';
  };
  security: {
    auth: 'OAuth2 + JWT';
    signing: 'Ed25519';
    encryption: 'AES-256-GCM';
  };
  database: {
    postgres: 'TCP with connection pooling';
    redis: 'PubSub + caching';
    vectorDB: 'HTTP + gRPC';
  };
  fileTransfer: {
    method: 'Signed URLs';
    storage: 'S3-compatible interface';
    encryption: 'at-rest + in-transit';
  };
}
```

### API Endpoint Standards
```python
# Example API router implementation
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.agent import AgentResponse, TaskRequest
from app.services.agent_service import AgentService

router = APIRouter(prefix="/api/v1/agents", tags=["agents"])

@router.get("/", response_model=List[AgentResponse])
async def list_agents(
    service: AgentService = Depends(),
    user: User = Depends(get_current_user)
):
    """List all available agents for user"""
    return await service.list_agents(user.id)

@router.post("/{agent_id}/execute", response_model=TaskResponse)
async def execute_task(
    agent_id: str,
    task: TaskRequest,
    service: AgentService = Depends(),
    user: User = Depends(get_current_user)
):
    """Execute task on specific agent"""
    return await service.execute_task(agent_id, task, user.id)
```

## Security & Privacy Architecture

### Comprehensive Security Stack
```typescript
interface SecurityArchitecture {
  vault: {
    implementation: 'HashiCorp Vault | custom AES-GCM';
    features: ['key rotation', 'secret versioning', 'audit logs'];
  };
  rbac: {
    enforcement: 'API layer + agent layer';
    granularity: 'resource-level permissions';
  };
  signedTasks: {
    algorithm: 'Ed25519';
    scope: 'all agent instructions';
  };
  memoryIsolation: {
    method: 'namespaces + TTL limits';
    scope: 'per session';
  };
  auditTrails: {
    logger: 'kSentinel agent';
    storage: 'encrypted logs + UI access';
  };
}
```

### Security Implementation
```python
# Example security service
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ed25519

class SecurityService:
    def __init__(self, private_key_path: str):
        self.private_key = self._load_private_key(private_key_path)
    
    def sign_task(self, task_data: dict) -> str:
        """Sign agent task with Ed25519"""
        message = json.dumps(task_data, sort_keys=True).encode()
        signature = self.private_key.sign(message)
        return base64.b64encode(signature).decode()
    
    def verify_signature(self, message: bytes, signature: str, public_key: str) -> bool:
        """Verify Ed25519 signature"""
        try:
            pub_key = ed25519.Ed25519PublicKey.from_public_bytes(
                base64.b64decode(public_key)
            )
            pub_key.verify(base64.b64decode(signature), message)
            return True
        except Exception:
            return False
```

## Telemetry & Logging System

### Logging Architecture
```typescript
interface LoggingSystem {
  storage: {
    local: 'logs/agents/, logs/system/, logs/security/';
    format: 'JSON lines (.jsonl) + rotating files';
    retention: '30 days local, 1 year archived';
  };
  visualization: {
    tools: ['Grafana Loki', 'SQLite Viewer UI'];
    realtime: 'WebSocket streaming';
  };
  metrics: {
    collection: 'Prometheus + custom metrics';
    alerting: 'threshold-based notifications';
  };
}
```

### Telemetry Implementation
```python
# Example telemetry service
import structlog
from prometheus_client import Counter, Histogram, Gauge

logger = structlog.get_logger(__name__)

# Metrics
task_counter = Counter('agent_tasks_total', 'Total agent tasks', ['agent_type', 'status'])
task_duration = Histogram('agent_task_duration_seconds', 'Task execution time')
active_agents = Gauge('active_agents', 'Number of active agents')

class TelemetryService:
    def log_task_start(self, task_id: str, agent_id: str, user_id: str):
        logger.info("task.started", 
                   task_id=task_id, 
                   agent_id=agent_id, 
                   user_id=user_id)
        task_counter.labels(agent_type=agent_id.split(':')[0], status='started').inc()
    
    def log_task_complete(self, task_id: str, duration: float, result: dict):
        logger.info("task.completed", 
                   task_id=task_id, 
                   duration=duration, 
                   result=result)
        task_duration.observe(duration)
        task_counter.labels(agent_type='all', status='completed').inc()
```

## Data Directory Structure

### Data Management Architecture
```text
/data
├── db_backups/
│   ├── postgres/
│   └── vector_store/
├── uploads/
│   ├── user_files/
│   └── agent_artifacts/
├── encrypted/
│   ├── vault_data/
│   └── secure_memory/
├── vector_store/
│   ├── embeddings/
│   └── indices/
└── telemetry/
    ├── logs/
    └── metrics/
```

## Agent-Oriented Service Mesh

### Agent Service Architecture
```text
/kindos-root/agents
├── kCore/            # Global controller
├── kPlanner/         # Goal breakdown and reasoning
├── kExecutor/        # Subtask execution agents
├── kReviewer/        # Verification agents
├── kSentinel/        # Security enforcement
├── kMemory/          # Embedding + recall
├── kPersona/         # Persona config
├── kBridge/          # External API linkers
└── shared/
    ├── protocols/
    └── taskgraph/
```

### Service Mesh Implementation
```typescript
interface ServiceMesh {
  discovery: {
    method: 'DNS + service registry';
    healthChecks: 'HTTP endpoints + heartbeat';
  };
  loadBalancing: {
    algorithm: 'round-robin + least-connections';
    failover: 'automatic with circuit breaker';
  };
  communication: {
    internal: 'gRPC with TLS';
    external: 'REST API with rate limiting';
  };
  monitoring: {
    tracing: 'distributed tracing with spans';
    metrics: 'per-service resource utilization';
  };
}
```

## Deployment Architecture

### Container Orchestration
```yaml
# docker-compose.yml example
version: '3.8'
services:
  gateway:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./services/gateway/nginx.conf:/etc/nginx/nginx.conf
  
  api:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/kindos
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
  
  frontend:
    build: ./frontend
    environment:
      - VITE_API_URL=http://api:8000
  
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: kindos
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
  
  vector-db:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - vector_data:/qdrant/storage

volumes:
  postgres_data:
  redis_data:
  vector_data:
```

---

