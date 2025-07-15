# KOS v1 Automated Deployment System

## Overview

KOS v1 (Knowledge Operating System) features a **zero-interaction automated deployment system** that detects your system capabilities and configures all services automatically. The system uses a **dynamic environment loader** that reads modular `.env` files and generates unified configurations.

## 🚀 One-Button Install & Deploy (Recommended)

- ✅ **Zero User Interaction** - Fully automated installation
- ✅ **System Auto-Detection** - OS, GPU, memory, storage detection
- ✅ **Smart Feature Flags** - Auto-disable features based on capabilities
- ✅ **Unified Container** - All services in one container with supervisor
- ✅ **Persistent Storage** - Docker volumes for all data
- ✅ **Dynamic Configuration** - Environment variables from modular files

## Quick Start

### 1. Automated Deployment (Recommended)

```bash
# Run the automated deployment script
./scripts/kos-auto-deploy.sh
```

### For Windows (No Bash):
- Use [WSL](https://docs.microsoft.com/en-us/windows/wsl/) or [Git Bash](https://gitforwindows.org/) to run the script above.
- Or, run the manual steps below in your terminal.

This script will:
- Detect your OS and system capabilities
- Install Docker if needed
- Generate environment configuration
- Start all KOS v1 services
- Display access information

## Manual Deployment (Advanced)

```bash
# Generate environment configuration
python3 scripts/env_loader.py

# Generate docker-compose config (if needed)
python3 scripts/generate_docker_compose.py

# Start services
docker-compose up -d
```

## Environment System

### Modular Configuration Files

All directory trees in this documentation are always sorted alphabetically.

The system uses modular `.env` files in the `env/` directory:

```
env/
├── api-keys.env           # API keys and secrets
├── cloud.env              # Cloud deployment settings
├── local.env              # Local service configurations
├── ports.env              # Port assignments and container names
└── settings/              # Service-specific settings
    ├── api.settings.env
    ├── ollama.settings.env
    └── openwebui.settings.env
```

### Dynamic Environment Loader

The `scripts/env_loader.py` script:

1. **Loads** all modular `.env` files
2. **Resolves** variable references (e.g., `${KOS_API_PORT}`)
3. **Detects** system capabilities (OS, GPU, memory, storage)
4. **Adjusts** feature flags based on capabilities
5. **Generates** unified `.env` and `.env.docker` files

### System Capability Detection

The system automatically detects:

- **Docker**: Docker and Docker Compose availability
- **GPU Availability**: NVIDIA, AMD, Intel GPUs
- **Memory**: Total and available RAM
- **Operating System**: Linux, macOS, Windows, WSL
- **Storage**: Available disk space

### Smart Feature Flag Management

Features are automatically enabled/disabled based on capabilities:

- **Low Memory (<8GB)**: Disables Elasticsearch, Neo4j
- **Low Storage (<20GB)**: Disables NextCloud
- **No GPU**: Disables Automatic1111, ComfyUI

## Services

### Core Services (Always Enabled)
- **API Server**: FastAPI backend on port 8000
- **Frontend**: React dashboard on port 3000
- **MinIO**: Object storage on port 9000/9001
- **PostgreSQL**: Primary database on port 5432
- **Redis**: Cache and session storage on port 6379
- **Weaviate**: Vector database on port 8082

### Optional Services (Auto-Configured)
- **AI Image Generation**: Automatic1111/ComfyUI (GPU required)
- **Gitea**: Git hosting on port 3002
- **Monitoring**: Prometheus/Grafana on ports 9090/3007
- **Ollama**: Local LLMs on port 11434
- **OpenWebUI**: LLM interface on port 3001

## Access Information

After deployment, access services at:

- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/health
- **Container Monitoring**: http://localhost:8081
- **MinIO Console**: http://localhost:9001
- **Weaviate**: http://localhost:8082
- **Web Dashboard**: http://localhost:3000

### Default Credentials
- **Admin User**: `kos-admin`
- **Admin Password**: `kos-30437`

## Configuration

### Customizing Environment

1. **Edit modular files** in `env/` directory
2. **Regenerate configuration**:
   ```bash
   python3 scripts/env_loader.py
   ```
3. **Regenerate docker-compose config** (if needed):
   ```bash
   python3 scripts/generate_docker_compose.py
   ```
4. **Restart services**:
   ```bash
   docker-compose restart
   ```

### Adding New Services

1. **Add service configuration** to `env/local.env`
2. **Add port mapping** to `env/ports.env`
3. **Add service** to `docker-compose.yml` (or use the generator script)
4. **Regenerate environment** and restart

### Production Deployment

1. **Set environment** to production in `env/cloud.env`
2. **Configure SSL certificates**
3. **Set secure passwords** in `env/api-keys.env`
4. **Deploy with**:
   ```bash
   KOS_ENVIRONMENT=production ./scripts/kos-auto-deploy.sh
   ```

## Troubleshooting

### Common Issues

1. **GPU Services Not Available**
   - Check GPU detection: `nvidia-smi`
   - Verify Docker GPU support: `docker run --gpus all nvidia/cuda:11.0-base nvidia-smi`

2. **Low Memory/Storage**
   - Disable heavy services in `env/local.env`
   - Regenerate environment and restart

3. **Port Conflicts**
   - Edit `env/ports.env` to change external ports
   - Regenerate environment: `python3 scripts/env_loader.py`

4. **Service Not Starting**
   - Check logs: `docker-compose logs [service-name]`
   - Verify environment variables: `docker-compose config`

### Useful Commands

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f kos-app

# Check service status
docker-compose ps

# Restart services
docker-compose restart

# Update services
docker-compose pull && docker-compose up -d

# Stop all services
docker-compose down

# Remove all data (WARNING: Destructive)
docker-compose down -v
```

## Architecture

### Unified Container Design

```
┌─────────────────────────────────────┐
│           KOS v1 Container          │
├─────────────────────────────────────┤
│  ┌─────────┐ ┌─────────┐ ┌─────────┐│
│  │ Backend │ │Frontend │ │Cadvisor ││
│  │ (8000)  │ │ (3000)  │ │ (8081)  ││
│  └─────────┘ └─────────┘ └─────────┘│
│           Supervisor                │
└─────────────────────────────────────┘
```

### Service Dependencies

```
KOS App Container
├── MinIO (Object Storage)
├── PostgreSQL (Database)
├── Redis (Cache)
└── Weaviate (Vector DB)
```

## Development

### Local Development

```bash
# Start only infrastructure
docker-compose up postgres redis weaviate minio

# Run backend locally
python -m uvicorn backend.main:app --reload

# Run frontend locally
cd frontend && npm run dev
```

### Adding New Environment Variables

1. **Add to appropriate** `.env` file in `env/`
2. **Reference in** `docker-compose.yml` if needed
3. **Regenerate** environment configuration
4. **Restart** services

## Security

### Default Security

- **Container isolation** via Docker networks
- **JWT Authentication** for API access
- **MinIO** access control
- **PostgreSQL** authentication
- **Redis Password** protection

### Production Security

- **Change default passwords** in `env/api-keys.env`
- **Configure firewall** rules
- **Enable SSL/TLS** certificates
- **Regular security updates**
- **Use secrets management** for sensitive data

## Support

For issues and questions:

1. **Check logs**: `docker-compose logs`
2. **Check system capabilities**: `python3 scripts/env_loader.py`
3. **Review documentation**: This file and inline comments
4. **Verify configuration**: `docker-compose config`

---

**KOS v1** - Knowledge Operating System v1.0.0
*Universal knowledge management and agent orchestration ecosystem* 