# KOS v1 - System Architecture

**last_updated: 2025-07-12**

## Overview

KOS v1 (Knowledge Operating System) is a modular, environment-driven AI platform designed for a wide range of deployments—including wearable, server, cloud, and edge environments. The architecture supports multi-agent systems, plugin extensibility, and robust security, forming the foundation for all KOS v1 applications. This document reflects the unified architecture and principles described in the KOS v1 PRD manual.

## Development Status

**Current Phase**: Active Development  
**AI Assistant**: Various AI models providing development support  
**KOS Agent Status**: Not yet implemented - This project is building the foundation for future KOS agent development

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Amauta Wearable AI Node                  │
├─────────────────────────────────────────────────────────────┤
│  Frontend (React + TypeScript)                              │
│  ├── Plugin Shell                                           │
│  ├── Health Dashboard                                       │
│  ├── DICOM Viewer                                           │
│  ├── Media Player                                           │
│  ├── IDE                                                    │
│  └── Vault Manager                                          │
├─────────────────────────────────────────────────────────────┤
│  Backend (FastAPI + Python)                                 │
│  ├── Authentication (OAuth2 + WebAuthN)                     │
│  ├── Agent System                                           │
│  ├── Plugin Registry                                        │
│  ├── Vault (Encrypted Storage)                              │
│  ├── RAG Engine                                             │
│  └── Medical Integration                                    │
├─────────────────────────────────────────────────────────────┤
│  Infrastructure                                             │
│  ├── PostgreSQL (Database)                                  │
│  ├── Redis (Cache)                                          │
│  ├── Weaviate (Vector Store)                                │
│  ├── Nginx (Reverse Proxy)                                  │
│  └── Monitoring (Prometheus + Grafana)                      │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Agent System

The agent system consists of five specialized AI agents:

- **Gallery**: Media management and image processing
- **Hakim**: Medical AI and health monitoring
- **Musa**: Audio processing and music generation
- **Ronin**: RAG (Retrieval-Augmented Generation) specialist
- **Skald**: Multilingual assistant and translator

### 2. Plugin Architecture

The plugin system allows dynamic loading of functionality:

- **Dynamic Loading**: Runtime plugin loading based on KLF manifests
- **Permission System**: Role-based plugin access
- **Plugin Registry**: Centralized plugin management
- **Plugin Store**: Repository for community plugins

### 3. Security System

Multi-layered security implementation:

- **OAuth2**: Standard authentication
- **Plugin Guard**: Secure plugin execution
- **RBAC**: Role-based access control
- **Vault**: Encrypted storage with AES256 + Argon2
- **WebAuthN**: Biometric authentication

### 4. Medical Integration

Medical-grade features for healthcare applications:

- **DICOM Support**: Medical image processing
- **Health Monitoring**: Real-time vitals tracking
- **HIPAA Compliance**: Privacy and security standards
- **PACS Integration**: Picture Archiving and Communication System

## Data Flow

### 1. User Authentication
```
User → OAuth2/WebAuthN → JWT Token → RBAC Check → Access Granted
```

### 2. Agent Request Processing
```
Frontend → API Gateway → Agent Router → Specific Agent → LLM Engine → Response
```

### 3. Plugin Loading
```
Plugin Request → Registry Check → Permission Validation → Dynamic Load → Execution
```

### 4. Medical Data Processing
```
DICOM File → Validation → Processing → Storage → Analysis → Results
```

## Technology Stack

### Frontend
- **React 18**: UI framework
- **Socket.io**: Real-time communication
- **Tailwind CSS**: Styling
- **TypeScript**: Type safety
- **Vite**: Build tool

### Backend
- **FastAPI**: API framework
- **Pydantic**: Data validation
- **Python 3.8+**: Runtime
- **SQLAlchemy**: ORM
- **Uvicorn**: ASGI server

### Database & Storage
- **PostgreSQL**: Primary database
- **Redis**: Caching and sessions
- **SQLite**: Local development
- **Weaviate**: Vector database

### Infrastructure
- **Docker**: Containerization
- **Docker Compose**: Orchestration
- **Grafana**: Monitoring
- **Nginx**: Reverse proxy
- **Prometheus**: Metrics

## Security Architecture

### Authentication Layers
1. **OAuth2**: Standard web authentication
2. **WebAuthN**: Biometric authentication
3. **JWT Tokens**: Session management
4. **Refresh Tokens**: Secure token renewal

### Data Protection
1. **AES256 Encryption**: Vault storage
2. **Argon2 Hashing**: Password security
3. **TLS/SSL**: Transport security
4. **RBAC**: Access control

### Plugin Security
1. **Sandboxing**: Isolated execution
2. **Permission Validation**: Resource access control
3. **Code Signing**: Plugin integrity
4. **Audit Logging**: Security monitoring

## Deployment Architecture

### Development
```
Local Machine
├── Frontend (localhost:3000)
├── Backend (localhost:8000)
├── Database (SQLite)
└── Vector Store (Local Weaviate)
```

### Production
```
Docker Containers
├── Frontend Container
├── Backend Container
├── PostgreSQL Container
├── Redis Container
├── Weaviate Container
├── Nginx Container
└── Monitoring Containers
```

### Cloud Deployment
```
Load Balancer
├── Frontend Instances
├── Backend Instances
├── Database Cluster
├── Cache Cluster
└── Monitoring Stack
```

## Performance Considerations

### Scalability
- **Horizontal Scaling**: Multiple backend instances
- **Load Balancing**: Nginx reverse proxy
- **Caching**: Redis for session and data caching
- **Database Optimization**: Connection pooling and indexing

### Monitoring
- **Metrics Collection**: Prometheus
- **Visualization**: Grafana dashboards
- **Logging**: Structured logging with correlation IDs
- **Health Checks**: Endpoint monitoring

### Optimization
- **Lazy Loading**: Plugin system
- **Connection Pooling**: Database connections
- **Compression**: API responses
- **CDN**: Static asset delivery

## Development Workflow

### Local Development
1. **Setup**: Run `./scripts/setup.sh`
2. **Frontend**: `npm run dev`
3. **Backend**: `python -m uvicorn backend.main:app --reload`
4. **Testing**: `npm test` and `pytest`

### CI/CD Pipeline
1. **Code Push**: GitHub repository
2. **Automated Testing**: Unit and integration tests
3. **Security Scan**: Vulnerability assessment
4. **Build**: Docker image creation
5. **Deploy**: Production deployment

## Future Enhancements

### Planned Features
- **Edge Computing**: Local AI processing
- **Federated Learning**: Distributed model training
- **Blockchain Integration**: Decentralized identity
- **AR/VR Support**: Immersive interfaces
- **IoT Integration**: Sensor data processing

### Scalability Improvements
- **Microservices**: Service decomposition
- **Event Sourcing**: Event-driven architecture
- **CQRS**: Command Query Responsibility Segregation
- **Kubernetes**: Container orchestration 

## Service Port Mapping (Sequential, Unique)

All *_EXTERNAL_PORT values are unique and sequential except for standard ports (80, 443, 5432, etc.).

| Service            | External Port |
|--------------------|--------------|
| Frontend           | 3000         |
| OpenWebUI          | 3001         |
| Gitea              | 3002         |
| Supabase Studio    | 3003         |
| Browseruse         | 3004         |
| Context7           | 3005         |
| Codium             | 3006         |
| Grafana            | 3007         |
| Prompt Manager     | 3008         |
| Artifact Manager   | 3009         |
| Redis Commander    | 3010         |
| PgAdmin            | 3011         |
| Mongo Express      | 3012         |
| Weaviate           | 3013         |
| Nextcloud          | 3014         |
| Huggingface        | 3015         |
| Automatic1111      | 3016         |
| ComfyUI            | 3017         |
| InvokeAI           | 3018         |
| N8N                | 3019         |
| Penpot             | 3020         |
| Admin Panel        | 3021         |
| Ollama             | 3022         |
| CAdvisor           | 3023         |
| API                | 8000         |
| Registry           | 5000         |
| Elasticsearch      | 9200         |
| MinIO              | 9000         |
| MinIO Console      | 9001         |
| Prometheus         | 9090         |
| Vault              | 8200         |
| Supabase           | 54321        |
| Postgres           | 5432         |
| Redis              | 6379         |
| MongoDB            | 27017        |
| Neo4j (Bolt)       | 7687         |
| Neo4j (Browser)    | 7474         |
| Gitea SSH          | 2222         |
| NGINX (HTTP)       | 80           |
| NGINX (HTTPS)      | 443          |

**Rationale:**
- Sequential port assignment eliminates conflicts and makes the system predictable and easy to maintain.
- Standard ports are preserved for compatibility. 