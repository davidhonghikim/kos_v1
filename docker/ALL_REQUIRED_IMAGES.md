# KOS v1 – All Required Docker Images for Full Deployment

This document lists every image used in `docker-compose.full.yml` and provides ready-to-use scripts to pre-pull images by group. Use the feature flags to enable/disable each group as needed.

---

## How to Use

1. **Set the feature flags** at the top of the script to `on` or `off` for each group.
2. **Run the script** to pull only the images you want.
3. After pulling, run your deployment as usual:
   ```sh
   docker compose -f docker/docker-compose.full.yml build
   docker compose -f docker/docker-compose.full.yml up -d
   ```

---

## Bash Script (Linux/macOS/WLS)

```bash
#!/bin/bash
# Feature flags: set to "on" or "off"
CORE_ADMIN=on
AI_ML=on
WORKFLOW=on
DB_STORAGE=on
MONITORING=on

if [ "$CORE_ADMIN" = "on" ]; then
  docker pull nginx:alpine
  docker pull portainer/portainer-ce:latest
  docker pull mongo-express:1.0.0
  docker pull dpage/pgadmin4:latest
  docker pull rediscommander/redis-commander:latest
  docker pull codercom/code-server:latest
fi

if [ "$AI_ML" = "on" ]; then
  docker pull ollama/ollama:latest
  docker pull ghcr.io/open-webui/open-webui:main
  docker pull ashleykza/stable-diffusion-webui:latest
  docker pull zhangp365/comfyui:latest
  docker pull ghcr.io/invoke-ai/invokeai:latest
  docker pull huggingface/transformers-pytorch-gpu:latest
fi

if [ "$WORKFLOW" = "on" ]; then
  docker pull n8nio/n8n:latest
  docker pull penpotapp/frontend:latest
  docker pull nextcloud:25.0.0
  docker pull browseruse/browseruse:latest
  docker pull gitea/gitea:latest
fi

if [ "$DB_STORAGE" = "on" ]; then
  docker pull supabase/postgres:15.1.0.117
  docker pull minio/minio:RELEASE.2024-01-16T16-07-38Z
  docker pull mongo:7.0
  docker pull neo4j:5.15
  docker pull docker.elastic.co/elasticsearch/elasticsearch:8.11.0
  docker pull semitechnologies/weaviate:1.22.4
  docker pull postgres:15-alpine
  docker pull redis:7.2-alpine
  docker pull hashicorp/vault:1.15.0
fi

if [ "$MONITORING" = "on" ]; then
  docker pull gcr.io/cadvisor/cadvisor:v0.47.2
  docker pull grafana/grafana:10.2.0
  docker pull prom/prometheus:v2.48.0
fi

# Context7 is built locally from docker/context7.Dockerfile
```

---

## Windows Batch Script

```bat
@echo off
REM Feature flags: set to on or off
set CORE_ADMIN=on
set AI_ML=on
set WORKFLOW=on
set DB_STORAGE=on
set MONITORING=on

if "%CORE_ADMIN%" == "on" (
  docker pull nginx:alpine
  docker pull portainer/portainer-ce:latest
  docker pull mongo-express:1.0.0
  docker pull dpage/pgadmin4:latest
  docker pull rediscommander/redis-commander:latest
  docker pull codercom/code-server:latest
)

if "%AI_ML%" == "on" (
  docker pull ashleykza/stable-diffusion-webui:latest
  docker pull zhangp365/comfyui:latest
  docker pull ghcr.io/invoke-ai/invokeai:latest
  docker pull ollama/ollama:latest
  docker pull ghcr.io/open-webui/open-webui:main
  docker pull huggingface/transformers-pytorch-gpu:latest
)

if "%WORKFLOW%" == "on" (
  docker pull n8nio/n8n:latest
  docker pull penpotapp/frontend:latest
  docker pull nextcloud:25.0.0
  docker pull browseruse/browseruse:latest
  docker pull gitea/gitea:latest
)

if "%DB_STORAGE%" == "on" (
  docker pull supabase/postgres:15.1.0.117
  docker pull minio/minio:RELEASE.2024-01-16T16-07-38Z
  docker pull mongo:7.0
  docker pull neo4j:5.15
  docker pull docker.elastic.co/elasticsearch/elasticsearch:8.11.0
  docker pull semitechnologies/weaviate:1.22.4
  docker pull postgres:15-alpine
  docker pull redis:7.2-alpine
  docker pull hashicorp/vault:1.15.0
)

if "%MONITORING%" == "on" (
  docker pull gcr.io/cadvisor/cadvisor:v0.47.2
  docker pull grafana/grafana:10.2.0
  docker pull prom/prometheus:v2.48.0
)

REM Context7 is built locally from docker/context7.Dockerfile
```

---

## Notes
- **Context7** is built locally from `docker/context7.Dockerfile` and does not have a remote image to pull.
- You can copy and run the script for your OS, or run individual pull commands as needed.
- For a full distro install, set all flags to `on` (default). 