# KOS v1 Services Reference Guide

## Overview

This document provides comprehensive reference information for all services in the KOS v1 stack, including official Docker images, web links, documentation, endpoints, API references, and user guides. All information is sourced from official documentation and repositories.

## Core Infrastructure Services

### PostgreSQL Database
- **Official Image**: `postgres:15-alpine`
- **Default Port**: 5432
- **Default Credentials**: 
  - Username: `postgres`
  - Password: `postgres`
- **Documentation**: 
  - [PostgreSQL Official Docs](https://www.postgresql.org/docs/)
  - [PostgreSQL Docker Hub](https://hub.docker.com/_/postgres)
- **Connection String**: `postgresql://postgres:postgres@localhost:5432/postgres`
- **Health Check**: `pg_isready -h localhost -p 5432`

### Redis Cache
- **Official Image**: `redis:7.2-alpine`
- **Default Port**: 6379
- **Default Password**: None (unprotected by default)
- **Documentation**:
  - [Redis Official Docs](https://redis.io/documentation)
  - [Redis Docker Hub](https://hub.docker.com/_/redis)
- **Connection**: `redis://localhost:6379`
- **Health Check**: `redis-cli ping`

### MongoDB Database
- **Official Image**: `mongo:7.0`
- **Default Port**: 27017
- **Default Credentials**: None (unprotected by default)
- **Documentation**:
  - [MongoDB Official Docs](https://docs.mongodb.com/)
  - [MongoDB Docker Hub](https://hub.docker.com/_/mongo)
- **Connection**: `mongodb://localhost:27017`
- **Health Check**: `mongosh --eval "db.adminCommand('ping')"`

### Neo4j Graph Database
- **Official Image**: `neo4j:5.15`
- **Default Ports**: 
  - Bolt: 7687
  - HTTP: 7474
  - HTTPS: 7473
- **Default Credentials**:
  - Username: `neo4j`
  - Password: `password` (must be changed on first login)
- **Documentation**:
  - [Neo4j Official Docs](https://neo4j.com/docs/)
  - [Neo4j Docker Hub](https://hub.docker.com/_/neo4j)
- **Web Interface**: http://localhost:7474
- **Health Check**: `curl http://localhost:7474/browser/`

### MinIO Object Storage
- **Official Image**: `minio/minio:RELEASE.2024-01-16T16-07-38Z`
- **Default Ports**:
  - API: 9000
  - Console: 9001
- **Default Credentials**:
  - Username: `minioadmin`
  - Password: `minioadmin`
- **Documentation**:
  - [MinIO Official Docs](https://min.io/docs/)
  - [MinIO Docker Hub](https://hub.docker.com/r/minio/minio)
- **Web Interface**: http://localhost:9001
- **Health Check**: `curl http://localhost:9000/minio/health/live`

### Elasticsearch Search Engine
- **Official Image**: `docker.elastic.co/elasticsearch/elasticsearch:8.11.0`
- **Default Port**: 9200
- **Default Credentials**:
  - Username: `elastic`
  - Password: `changeme`
- **Documentation**:
  - [Elasticsearch Official Docs](https://www.elastic.co/guide/index.html)
  - [Elasticsearch Docker](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html)
- **API Endpoint**: http://localhost:9200
- **Health Check**: `curl http://localhost:9200/_cluster/health`

### Weaviate Vector Database
- **Official Image**: `semitechnologies/weaviate:1.22.4`
- **Default Port**: 8080
- **Default Credentials**: None (anonymous access enabled by default)
- **Documentation**:
  - [Weaviate Official Docs](https://weaviate.io/developers/weaviate)
  - [Weaviate Docker Hub](https://hub.docker.com/r/semitechnologies/weaviate)
- **Web Interface**: http://localhost:8080
- **API Reference**: http://localhost:8080/v1/meta
- **GraphQL Playground**: http://localhost:8080/v1/graphql
- **Health Check**: `curl http://localhost:8080/v1/.well-known/ready`

### HashiCorp Vault
- **Official Image**: `hashicorp/vault:1.15.0`
- **Default Port**: 8200
- **Default Credentials**: None (dev mode)
- **Documentation**:
  - [Vault Official Docs](https://developer.hashicorp.com/vault/docs)
  - [Vault Docker Hub](https://hub.docker.com/r/hashicorp/vault)
- **Web Interface**: http://localhost:8200
- **Health Check**: `curl http://localhost:8200/v1/sys/health`

## AI/ML Services

### Ollama (Local LLMs)
- **Official Image**: `ollama/ollama:latest`
- **Default Port**: 11434
- **Default Credentials**: None
- **Documentation**:
  - [Ollama Official Docs](https://ollama.ai/docs)
  - [Ollama GitHub](https://github.com/ollama/ollama)
  - [Ollama Docker Hub](https://hub.docker.com/r/ollama/ollama)
- **API Endpoint**: http://localhost:11434/api
- **Health Check**: `curl http://localhost:11434/api/tags`
- **Special Notes**: 
  - Requires GPU support for optimal performance
  - Models are downloaded on first use
  - Supports multiple model formats (GGUF, etc.)

### OpenWebUI
- **Official Image**: `ghcr.io/open-webui/open-webui:main`
- **Default Port**: 8080
- **Default Credentials**:
  - Username: `admin`
  - Password: `admin`
- **Documentation**:
  - [OpenWebUI GitHub](https://github.com/open-webui/open-webui)
  - [OpenWebUI Docs](https://docs.openwebui.com/)
- **Web Interface**: http://localhost:8080
- **Health Check**: `curl http://localhost:8080`
- **Special Notes**: 
  - Requires Ollama backend
  - Supports multiple LLM providers
  - Has built-in user management

### Hugging Face Transformers
- **Official Image**: `huggingface/transformers-pytorch-gpu:latest`
- **Default Port**: 8080
- **Default Credentials**: None
- **Documentation**:
  - [Hugging Face Docs](https://huggingface.co/docs)
  - [Transformers Library](https://huggingface.co/docs/transformers)
  - [Hugging Face Docker Hub](https://hub.docker.com/r/huggingface/transformers-pytorch-gpu)
- **API Endpoint**: http://localhost:8080
- **Special Notes**: 
  - GPU-optimized image
  - Large image size (~10GB)
  - Supports all Hugging Face models

### Automatic1111 (Stable Diffusion)
- **Community Image**: `ashleykza/stable-diffusion-webui:latest`
- **Default Port**: 7860
- **Default Credentials**: None
- **Documentation**:
  - [Automatic1111 GitHub](https://github.com/AUTOMATIC1111/stable-diffusion-webui)
  - [Stable Diffusion Guide](https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki)
- **Web Interface**: http://localhost:7860
- **Health Check**: `curl http://localhost:7860`
- **Special Notes**: 
  - Requires GPU for optimal performance
  - Large image size (~15GB)
  - Supports extensive model ecosystem

### ComfyUI
- **Community Image**: `zhangp365/comfyui:latest`
- **Default Port**: 8188
- **Default Credentials**: None
- **Documentation**:
  - [ComfyUI GitHub](https://github.com/comfyanonymous/ComfyUI)
  - [ComfyUI Examples](https://github.com/comfyanonymous/ComfyUI_examples)
- **Web Interface**: http://localhost:8188
- **Health Check**: `curl http://localhost:8188`
- **Special Notes**: 
  - Node-based workflow interface
  - Requires GPU for optimal performance
  - Supports custom nodes and workflows

### InvokeAI
- **Official Image**: `invokeai/invokeai:3.6.0`
- **Default Port**: 9090
- **Default Credentials**: None
- **Documentation**:
  - [InvokeAI GitHub](https://github.com/invoke-ai/InvokeAI)
  - [InvokeAI Docs](https://invoke-ai.github.io/InvokeAI/)
- **Web Interface**: http://localhost:9090
- **Health Check**: `curl http://localhost:9090`
- **Special Notes**: 
  - Professional-grade image generation
  - Supports multiple model formats
  - Built-in model management

## Workflow & Automation Services

### n8n (Workflow Automation)
- **Official Image**: `n8nio/n8n:latest`
- **Default Port**: 5678
- **Default Credentials**: None (first user becomes admin)
- **Documentation**:
  - [n8n Official Docs](https://docs.n8n.io/)
  - [n8n GitHub](https://github.com/n8n-io/n8n)
  - [n8n Docker Hub](https://hub.docker.com/r/n8nio/n8n)
- **Web Interface**: http://localhost:5678
- **Health Check**: `curl http://localhost:5678`
- **Special Notes**: 
  - Requires database (PostgreSQL recommended)
  - Supports 200+ integrations
  - Has built-in webhook support

### Penpot (Design Tool)
- **Official Images**:
  - Frontend: `penpotapp/frontend:latest`
  - Backend: `penpotapp/backend:latest`
  - Exporter: `penpotapp/exporter:latest`
- **Default Ports**:
  - Frontend: 9000
  - Backend: 6060
  - Exporter: 6061
- **Default Credentials**:
  - Username: `admin`
  - Password: `admin`
- **Documentation**:
  - [Penpot Official Docs](https://help.penpot.app/)
  - [Penpot GitHub](https://github.com/penpot/penpot)
- **Web Interface**: http://localhost:9000
- **Health Check**: `curl http://localhost:9000`
- **Special Notes**: 
  - Multi-container setup required
  - Requires PostgreSQL and Redis
  - Open-source Figma alternative

### NextCloud (File Storage)
- **Official Image**: `nextcloud:25.0.0`
- **Default Port**: 80
- **Default Credentials**: None (set during first setup)
- **Documentation**:
  - [NextCloud Official Docs](https://docs.nextcloud.com/)
  - [NextCloud Docker Hub](https://hub.docker.com/_/nextcloud)
- **Web Interface**: http://localhost
- **Health Check**: `curl http://localhost/status.php`
- **Special Notes**: 
  - Requires database (PostgreSQL/MySQL)
  - Supports extensive app ecosystem
  - Self-hosted Dropbox alternative

## Development Services

### Code Server (VS Code in Browser)
- **Official Image**: `codercom/code-server:latest`
- **Default Port**: 8080
- **Default Credentials**: None (set via environment variable)
- **Documentation**:
  - [Code Server Official Docs](https://coder.com/docs/code-server/latest)
  - [Code Server GitHub](https://github.com/coder/code-server)
- **Web Interface**: http://localhost:8080
- **Health Check**: `curl http://localhost:8080`
- **Special Notes**: 
  - Full VS Code experience in browser
  - Supports extensions and themes
  - Can be password protected

### BrowserUse (Browser Automation)
- **Community Image**: `browseruse/browseruse:latest`
- **Default Port**: 3000
- **Default Credentials**: None
- **Documentation**:
  - [BrowserUse GitHub](https://github.com/browseruse/browseruse)
- **Web Interface**: http://localhost:3000
- **API Documentation**: http://localhost:3000/docs
- **Special Notes**: 
  - Browser automation tool
  - Supports multiple browser engines
  - API-first design

### Context7 (MCP Server)
- **Image**: `context7-mcp:latest` (custom build from official repo)
- **Default Port**: 3017 (assigned in ports.env, referenced everywhere else)
- **Default Credentials**: None
- **Documentation**:
  - [Context7 GitHub](https://github.com/upstash/context7)
  - [Context7 Docker Setup](https://github.com/upstash/context7#using-docker)
- **Web Interface**: http://localhost:3017 (KOS port mapping)
- **MCP Configuration**: Requires MCP client configuration
- **Special Notes**: 
  - Model Context Protocol (MCP) server
  - Custom Docker build from official repository
  - Integrates with MCP clients (Cursor, VS Code, etc.)
  - Context management for AI applications
  - Uses stdio transport by default
  - Requires PostgreSQL database connection
  - **Ports and all config values are assigned in ports.env and referenced everywhere else. Never hardcode or duplicate values.**

## Database Management Services

### pgAdmin (PostgreSQL Admin)
- **Official Image**: `dpage/pgadmin4:latest`
- **Default Port**: 80
- **Default Credentials**:
  - Email: `admin@admin.com`
  - Password: `root`
- **Documentation**:
  - [pgAdmin Official Docs](https://www.pgadmin.org/docs/)
  - [pgAdmin Docker Hub](https://hub.docker.com/r/dpage/pgadmin4)
- **Web Interface**: http://localhost
- **Health Check**: `curl http://localhost/misc/ping`
- **Special Notes**: 
  - Web-based PostgreSQL administration
  - Supports multiple server connections
  - Built-in query tool

### Mongo Express (MongoDB Admin)
- **Official Image**: `mongo-express:1.0.0`
- **Default Port**: 8081
- **Default Credentials**: None
- **Documentation**:
  - [Mongo Express GitHub](https://github.com/mongo-express/mongo-express)
  - [Mongo Express Docker Hub](https://hub.docker.com/_/mongo-express)
- **Web Interface**: http://localhost:8081
- **Health Check**: `curl http://localhost:8081`
- **Special Notes**: 
  - Web-based MongoDB administration
  - Requires MongoDB connection
  - Supports CRUD operations

### Redis Commander
- **Official Image**: `rediscommander/redis-commander:latest`
- **Default Port**: 8081
- **Default Credentials**: None
- **Documentation**:
  - [Redis Commander GitHub](https://github.com/joeferner/redis-commander)
  - [Redis Commander Docker Hub](https://hub.docker.com/r/rediscommander/redis-commander)
- **Web Interface**: http://localhost:8081
- **Health Check**: `curl http://localhost:8081`
- **Special Notes**: 
  - Web-based Redis administration
  - Supports multiple Redis instances
  - Real-time monitoring

## Monitoring Services

### Prometheus
- **Official Image**: `prom/prometheus:v2.48.0`
- **Default Port**: 9090
- **Default Credentials**: None
- **Documentation**:
  - [Prometheus Official Docs](https://prometheus.io/docs/)
  - [Prometheus Docker Hub](https://hub.docker.com/r/prom/prometheus)
- **Web Interface**: http://localhost:9090
- **Health Check**: `curl http://localhost:9090/-/healthy`
- **Special Notes**: 
  - Time-series database
  - Pull-based monitoring
  - Powerful query language (PromQL)

### Grafana
- **Official Image**: `grafana/grafana:10.2.0`
- **Default Port**: 3000
- **Default Credentials**:
  - Username: `admin`
  - Password: `admin`
- **Documentation**:
  - [Grafana Official Docs](https://grafana.com/docs/)
  - [Grafana Docker Hub](https://hub.docker.com/r/grafana/grafana)
- **Web Interface**: http://localhost:3000
- **Health Check**: `curl http://localhost:3000/api/health`
- **Special Notes**: 
  - Visualization and analytics platform
  - Supports 100+ data sources
  - Extensive dashboard ecosystem

### cAdvisor (Container Monitoring)
- **Official Image**: `gcr.io/cadvisor/cadvisor:v0.47.2`
- **Default Port**: 8080
- **Default Credentials**: None
- **Documentation**:
  - [cAdvisor GitHub](https://github.com/google/cadvisor)
  - [cAdvisor Docker Hub](https://hub.docker.com/r/gcr.io/cadvisor/cadvisor)
- **Web Interface**: http://localhost:8080
- **Health Check**: `curl http://localhost:8080/healthz`
- **Special Notes**: 
  - Container resource monitoring
  - Exports metrics to Prometheus
  - Real-time container stats

## Admin Services

### Portainer (Container Management)
- **Official Image**: `portainer/portainer-ce:latest`
- **Default Port**: 9000
- **Default Credentials**: None (set during first setup)
- **Documentation**:
  - [Portainer Official Docs](https://docs.portainer.io/)
  - [Portainer Docker Hub](https://hub.docker.com/r/portainer/portainer-ce)
- **Web Interface**: http://localhost:9000
- **Health Check**: `curl http://localhost:9000/api/status`
- **Special Notes**: 
  - Web-based Docker management
  - Supports Docker Swarm
  - User management and access control

### Docker Registry
- **Official Image**: `registry:2`
- **Default Port**: 5000
- **Default Credentials**: None (unprotected by default)
- **Documentation**:
  - [Docker Registry Docs](https://docs.docker.com/registry/)
  - [Registry Docker Hub](https://hub.docker.com/_/registry)
- **API Endpoint**: http://localhost:5000/v2/
- **Health Check**: `curl http://localhost:5000/v2/`
- **Special Notes**: 
  - Private Docker image registry
  - Supports authentication
  - Can be used with Docker Compose

## Service Dependencies

### Core Dependencies
- **PostgreSQL** → Required by: API, n8n, NextCloud, Penpot
- **Redis** → Required by: API, OpenWebUI, Penpot
- **Weaviate** → Required by: API (vector search)
- **MinIO** → Required by: API (file storage)

### Optional Dependencies
- **Elasticsearch** → Used by: API (search functionality)
- **Neo4j** → Used by: API (graph database)
- **MongoDB** → Used by: API (document storage)

## Health Check Endpoints

| Service | Health Check URL | Method |
|---------|------------------|--------|
| PostgreSQL | `pg_isready -h localhost -p 5432` | CLI |
| Redis | `redis-cli ping` | CLI |
| MongoDB | `mongosh --eval "db.adminCommand('ping')"` | CLI |
| Neo4j | `curl http://localhost:7474/browser/` | HTTP |
| MinIO | `curl http://localhost:9000/minio/health/live` | HTTP |
| Elasticsearch | `curl http://localhost:9200/_cluster/health` | HTTP |
| Weaviate | `curl http://localhost:8080/v1/.well-known/ready` | HTTP |
| Vault | `curl http://localhost:8200/v1/sys/health` | HTTP |
| Ollama | `curl http://localhost:11434/api/tags` | HTTP |
| OpenWebUI | `curl http://localhost:8080` | HTTP |
| Automatic1111 | `curl http://localhost:7860` | HTTP |
| ComfyUI | `curl http://localhost:8188` | HTTP |
| InvokeAI | `curl http://localhost:9090` | HTTP |
| n8n | `curl http://localhost:5678` | HTTP |
| Penpot | `curl http://localhost:9000` | HTTP |
| NextCloud | `curl http://localhost/status.php` | HTTP |
| Code Server | `curl http://localhost:8080` | HTTP |
| BrowserUse | `curl http://localhost:3000` | HTTP |
| Context7 | `curl http://localhost:3017` | HTTP |
| pgAdmin | `curl http://localhost/misc/ping` | HTTP |
| Mongo Express | `curl http://localhost:8081` | HTTP |
| Redis Commander | `curl http://localhost:8081` | HTTP |
| Prometheus | `curl http://localhost:9090/-/healthy` | HTTP |
| Grafana | `curl http://localhost:3000/api/health` | HTTP |
| cAdvisor | `curl http://localhost:8080/healthz` | HTTP |
| Portainer | `curl http://localhost:9000/api/status` | HTTP |
| Registry | `curl http://localhost:5000/v2/` | HTTP |

## Troubleshooting

### Common Issues

1. **Service Not Starting**
   - Check logs: `docker-compose logs [service-name]`
   - Verify ports are not in use: `netstat -an | findstr :[port]`
   - Check resource requirements (especially for AI services)

2. **Database Connection Issues**
   - Verify database is running: `docker-compose ps [database-service]`
   - Check connection string format
   - Verify credentials match defaults

3. **GPU Services Not Working**
   - Verify NVIDIA Docker support: `docker run --gpus all nvidia/cuda:11.0-base nvidia-smi`
   - Check GPU availability: `nvidia-smi`
   - Ensure proper Docker runtime configuration

4. **Memory Issues**
   - Monitor memory usage: `docker stats`
   - Increase Docker memory limits
   - Consider running heavy services separately

### Useful Commands

```bash
# View all service logs
docker-compose logs -f

# Restart specific service
docker-compose restart [service-name]

# Check service status
docker-compose ps

# Access service shell
docker-compose exec [service-name] bash

# View service resources
docker stats

# Check service health
curl [health-check-url]

# Pull latest images
docker-compose pull

# Rebuild services
docker-compose build --no-cache
```

## Service Configuration

### Environment Variables
All service configurations are managed through environment variables in the `env/` directory:
- `env/local.env` - Local service configurations
- `env/ports.env` - Port assignments
- `env/api-keys.env` - API keys and secrets
- `env/cloud.env` - Cloud deployment settings

### Customization
To customize service configurations:
1. Edit the appropriate file in `env/`
2. Run `python scripts/env_loader.py` to regenerate `.env`
3. Run `python scripts/generate_docker_compose.py` to update compose files
4. Restart services: `docker-compose restart`

### Security Considerations
- Change default passwords for all services
- Enable authentication where available
- Use secrets management (Vault) for sensitive data
- Configure proper network isolation
- Regular security updates

## Support and Resources

- **KOS v1 Documentation**: [DEPLOYMENT.md](./DEPLOYMENT.md)
- **GitHub Repository**: [KOS v1 Project](https://github.com/your-org/kos-v1)
- **Issues and Support**: [GitHub Issues](https://github.com/your-org/kos-v1/issues)

---

*Last updated: July 14, 2025*
*KOS v1 Version: 1.0.0* 