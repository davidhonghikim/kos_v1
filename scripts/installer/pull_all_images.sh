#!/bin/bash
# KOS v1 - Pre-pull all required Docker images (Linux/macOS/WSL)
# Feature flags: set to "on" or "off"
CORE_ADMIN=on
AI_ML=on
WORKFLOW=on
DB_STORAGE=on
MONITORING=on

# Priority 1: Core DBs
  docker pull postgres:15-alpine
  docker pull redis:7.2-alpine
  docker pull minio/minio:RELEASE.2024-01-16T16-07-38Z
  docker pull neo4j:5.15
  docker pull docker.elastic.co/elasticsearch/elasticsearch:8.11.0
  docker pull semitechnologies/weaviate:1.22.4
  docker pull mongo:7.0

# Priority 2: Core AI/LLM
  docker pull ollama/ollama:latest
  docker pull ghcr.io/open-webui/open-webui:main
  docker pull nvidia/cuda:12.2.0-base
  # docker pull rocm/rocm-terminal:latest

# Priority 3: Workflow/Monitoring
  docker pull n8nio/n8n:latest
  docker pull penpotapp/frontend:latest
  docker pull nextcloud:latest
  docker pull browserless/chrome:latest
  docker pull gitea/gitea:1.21.7
  docker pull grafana/grafana:latest
  docker pull prom/prometheus:latest
  docker pull gcr.io/cadvisor/cadvisor:latest

# Priority 4: Admin/Dev/Other
  docker pull portainer/portainer-ce:latest
  docker pull mongo-express:1.0.0-alpha.4
  docker pull dpage/pgadmin4:8.6
  docker pull rediscommander/redis-commander:latest
  docker pull codercom/code-server:latest

# Priority 5: Big AI Images
  docker pull ashleykza/stable-diffusion-webui:latest
  docker pull zhangp365/comfyui:latest
  docker pull ghcr.io/invoke-ai/invokeai:latest

# Priority 6: Rest (add any additional images here) 