@echo off
REM KOS v1 - Pre-pull all required Docker images (Windows)
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
  docker pull nvidia/cuda:12.2.0-base
  docker pull rocm/rocm-terminal:latest
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