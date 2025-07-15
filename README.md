# KOS v1 - Knowledge Operating System

A comprehensive, self-hosted knowledge management and AI platform with automated deployment and validation.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.8+
- Git

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd kos_v1

# Run the automated installer
./kos-install.sh
```

The installer will:
1. Detect your system capabilities
2. Install dependencies
3. Generate environment configuration
4. Start all services with health checks
5. Display access information

## 📋 Service Validation

The system now includes comprehensive validation to ensure all services start correctly:

### Environment Validation
- **Service Configuration**: Validates that all enabled services have required variables (ports, images, credentials)
- **API Keys**: Checks for required API keys and secrets for enabled cloud services
- **Security Keys**: Validates JWT secrets, encryption keys, and other security requirements

### Health Checks
- **Dynamic Health Monitoring**: Automatically checks health for all enabled services
- **Endpoint Validation**: Verifies UI, health endpoints, and addon exposure
- **Container Status**: Monitors container status for headless services

### Service Exposure
- **UI Endpoints**: Web interfaces for user interaction
- **Health Endpoints**: Service health monitoring endpoints
- **Addon Endpoints**: Additional service interfaces

## 🔧 Configuration

### Environment Files
The system uses modular environment configuration:

- `env/ports.env` - Port assignments and container names
- `env/local.env` - Service enablement and local configuration
- `env/settings.env` - System settings and feature flags
- `env/api-keys.env` - External API keys and authentication
- `env/cloud.env` - Cloud service configuration

### Adding New Services
To add a new service:

1. **Add Service Configuration** in `env/local.env`:
```bash
KOS_NEW_SERVICE_ENABLE=true
KOS_NEW_SERVICE_IMAGE=service:latest
KOS_NEW_SERVICE_INTERNAL_PORT=8080
KOS_NEW_SERVICE_EXTERNAL_PORT=8080
KOS_NEW_SERVICE_HOST=${KOS_DEFAULT_HOST}
```

2. **Add Port Configuration** in `env/ports.env`:
```bash
KOS_NEW_SERVICE_CONTAINER_NAME=kos-new-service
KOS_NEW_SERVICE_EXTERNAL_PORT=8080
KOS_NEW_SERVICE_INTERNAL_PORT=8080
```

3. **Update Validation** in `scripts/env_loader.py`:
```python
'NEW_SERVICE': ['_ENABLE', '_IMAGE', '_INTERNAL_PORT', '_EXTERNAL_PORT', '_HOST'],
```

4. **Add Health Check** in `scripts/generate_docker_compose.py`:
```python
elif service_name == 'new_service':
    return {
        'test': ['CMD-SHELL', 'curl -f http://localhost:8080/health || exit 1'],
        'interval': '30s',
        'timeout': '10s',
        'retries': 3
    }
```

## 🔑 API Keys and Secrets

### Required API Keys
For production use, ensure these API keys are configured:

- **OpenAI**: `OPENAI_API_KEY`, `OPENAI_ORGANIZATION`
- **Anthropic**: `ANTHROPIC_API_KEY`
- **Google AI**: `GOOGLE_AI_API_KEY`
- **Azure OpenAI**: `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`
- **HuggingFace**: `HUGGINGFACE_API_TOKEN`
- **AWS**: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
- **Pinecone**: `PINECONE_API_KEY`, `PINECONE_ENVIRONMENT`

### Security Keys
Generate these security keys for production:

```bash
# JWT Secret
openssl rand -base64 32

# OpenWebUI Secret
openssl rand -base64 32

# N8N Encryption Key
openssl rand -base64 32

# Penpot Secret Key
openssl rand -base64 32
```

## 🐛 Troubleshooting

### Service Startup Issues

#### 1. Missing Environment Variables
**Error**: `Service X is enabled but missing required variables`
**Solution**: Check the service configuration in `env/local.env` and `env/ports.env`

#### 2. Service Health Check Failures
**Error**: `Service X health check failed`
**Solution**: 
- Check service logs: `docker-compose logs -f <service-name>`
- Verify port availability: `netstat -tulpn | grep <port>`
- Check service dependencies are healthy

#### 3. Nextcloud/Postgres Connection Issues
**Error**: Nextcloud fails to start or loops
**Solution**:
- Ensure Postgres is healthy: `docker-compose ps postgres`
- Check database credentials in `env/local.env`
- Verify Nextcloud DB configuration

#### 4. API Key Errors
**Error**: `Missing API key/secret for service`
**Solution**: Add required API keys to `env/api-keys.env` or `env/cloud.env`

### Common Commands

```bash
# View all service logs
docker-compose logs -f

# Check service status
docker-compose ps

# Restart specific service
docker-compose restart <service-name>

# Rebuild and restart
docker-compose down
docker-compose up -d --build

# Check service health
curl http://localhost:<port>/health

# Access service logs
docker-compose logs -f <service-name>
```

### Service Dependencies
The system uses health checks and dependencies to ensure proper startup order:

1. **Infrastructure**: PostgreSQL, Redis, MinIO, Elasticsearch, Weaviate
2. **Core Services**: API, Frontend, Nginx
3. **AI Services**: Ollama, OpenWebUI, Image Generation
4. **Workflow**: n8n, Penpot, Nextcloud
5. **Admin Tools**: Database management UIs
6. **Monitoring**: Prometheus, Grafana, cAdvisor

## 🌐 Service Access

### Core Services
- **Web Dashboard**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **API Health**: http://localhost:8000/health

### Database Access
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **Weaviate**: http://localhost:8082
- **MinIO Console**: http://localhost:9001

### Admin Tools
- **pgAdmin**: http://localhost:8086
- **Mongo Express**: http://localhost:8087
- **Redis Commander**: http://localhost:8085

### AI Services
- **OpenWebUI**: http://localhost:3001
- **Automatic1111**: http://localhost:7860
- **ComfyUI**: http://localhost:8188
- **InvokeAI**: http://localhost:9091

### Workflow Tools
- **Nextcloud**: http://localhost:8083
- **n8n**: http://localhost:5678
- **Penpot**: http://localhost:9002

### Monitoring
- **Grafana**: http://localhost:3007
- **Prometheus**: http://localhost:9090
- **cAdvisor**: http://localhost:8088

## 🔒 Security

### Default Credentials
- **Admin User**: kos-admin
- **Admin Password**: kos-30437

**⚠️ Change these credentials in production!**

### SSL/TLS
For production deployment:
1. Add SSL certificates to `env/api-keys.env`
2. Enable HTTPS in `env/settings.env`
3. Configure nginx SSL settings

## 📊 Monitoring

### Health Monitoring
- All services include health checks
- Automatic restart on failure
- Health status reporting in installer

### Logging
- Centralized logging in `./logs/`
- Service-specific log files
- Docker Compose log aggregation

### Metrics
- Prometheus metrics collection
- Grafana dashboards
- cAdvisor container monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

[Add your license information here]

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review service logs
3. Verify environment configuration
4. Create an issue with detailed information 