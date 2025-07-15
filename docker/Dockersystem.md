##supervisor

[supervisord]
nodaemon=true
user=root
logfile=/app/logs/supervisord.log
pidfile=/app/supervisord.pid

[program:kos-backend]
command=uvicorn backend.main:app --host 0.0.0.0 --port %(API_INTERNAL_PORT)s
directory=/app
user=root
autostart=true
autorestart=true
stderr_logfile=/app/logs/backend.err.log
stdout_logfile=/app/logs/backend.out.log
environment=PYTHONPATH="/app",PYTHONUNBUFFERED="1"

[program:kos-frontend]
command=serve -s frontend/dist -l %(FRONTEND_INTERNAL_PORT)s
directory=/app
user=root
autostart=true
autorestart=true
stderr_logfile=/app/logs/frontend.err.log
stdout_logfile=/app/logs/frontend.out.log

[program:kos-cadvisor]
command=/usr/local/bin/cadvisor -port %(CADVISOR_INTERNAL_PORT)s
directory=/app
user=root
autostart=true
autorestart=true
stderr_logfile=/app/logs/cadvisor.err.log
stdout_logfile=/app/logs/cadvisor.out.log

[program:kos-wait-services]
command=/app/scripts/wait-for-services.sh
directory=/app
user=root
autostart=true
autorestart=false
stderr_logfile=/app/logs/wait-services.err.log
stdout_logfile=/app/logs/wait-services.out.log 




##frontend
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Install curl for health checks
RUN apk add --no-cache curl

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY frontend/ ./

# Build the application
RUN npm run build

# Install serve to run the built app
RUN npm install -g serve

# Set environment variables
ENV KOS_APP_NAME="KOS v1 Knowledge Library Framework"
ENV KOS_VERSION="1.0.0"

# Expose port
EXPOSE ${KOS_FRONTEND_INTERNAL_PORT:-3000}

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${KOS_FRONTEND_INTERNAL_PORT:-3000} || exit 1

# Serve the built application
CMD ["serve", "-s", "dist", "-l", "${KOS_FRONTEND_INTERNAL_PORT:-3000}"] 



##backend

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    wget \
    git \
    supervisor \
    postgresql-client \
    redis-tools \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements/docker.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY config/ ./config/
COPY scripts/ ./scripts/

# Create necessary directories with proper permissions
RUN mkdir -p vault dicom models plugins logs data tmp && \
    chmod 755 vault dicom models plugins logs data tmp

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV KOS_APP_NAME="KOS v1 Knowledge Library Framework"
ENV KOS_VERSION="1.0.0"

# Expose port
EXPOSE ${KOS_API_INTERNAL_PORT:-8000}

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${KOS_API_INTERNAL_PORT:-8000}/health || exit 1

# Run the application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "${KOS_API_INTERNAL_PORT:-8000}"] 


##context7

# Context7 MCP Server Dockerfile
# Based on official Context7 GitHub repository: https://github.com/upstash/context7

FROM node:18-alpine

# Set working directory
WORKDIR /app

# Install git for cloning the repository
RUN apk add --no-cache git

# Clone the Context7 repository
RUN git clone https://github.com/upstash/context7.git .

# Install dependencies
RUN npm ci --only=production

# Build the application
RUN npm run build

# Expose port (if needed for web interface)
EXPOSE 3000

# Set environment variables
ENV NODE_ENV=production

# Run the MCP server
CMD ["node", "dist/index.js"] 



## unified

# KOS v1 Unified Application Container
FROM node:20-slim AS frontend-builder

WORKDIR /app

# Copy frontend package files and install dependencies
COPY frontend/package*.json ./
RUN npm install

# Copy frontend source code
COPY frontend/ ./
# Ensure public directory exists for static assets
RUN mkdir -p public
RUN npm run build

# --- Backend Stage ---
FROM python:3.11-slim AS backend

ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    nodejs \
    npm \
    supervisor \
    postgresql-client \
    redis-tools \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Python requirements and install dependencies
COPY requirements/docker.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/
COPY config/ ./config/
COPY scripts/ ./scripts/

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/dist/ ./frontend/dist/
COPY --from=frontend-builder /app/package.json ./frontend/package.json

# Install serve for frontend
RUN npm install -g serve

# Create supervisor configuration
RUN mkdir -p /etc/supervisor/conf.d
COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/tmp /app/vault /app/dicom /app/models /app/plugins

# Set permissions
RUN chmod +x scripts/*.sh

# Install Cadvisor for container monitoring
RUN wget -O /usr/local/bin/cadvisor https://github.com/google/cadvisor/releases/download/v0.47.2/cadvisor-v0.47.2-linux-amd64 \
    && chmod +x /usr/local/bin/cadvisor

# Create wait-for-services script with environment variables
RUN echo '#!/bin/bash\necho "KOS v1: Waiting for services to be ready..."\n\n# Wait for PostgreSQL\nuntil pg_isready -h ${KOS_POSTGRES_HOST:-postgres} -p ${KOS_POSTGRES_INTERNAL_PORT:-5432} -U ${KOS_POSTGRES_USER:-kos-admin}; do\n  echo "Waiting for PostgreSQL..."\n  sleep 2\ndone\n\n# Wait for Redis\nuntil redis-cli -h ${KOS_REDIS_HOST:-redis} -p ${KOS_REDIS_INTERNAL_PORT:-6379} ping; do\n  echo "Waiting for Redis..."\n  sleep 2\ndone\n\n# Wait for Weaviate\nuntil curl -f http://${KOS_WEAVIATE_HOST:-weaviate}:${KOS_WEAVIATE_INTERNAL_PORT:-8080}/v1/.well-known/ready; do\n  echo "Waiting for Weaviate..."\n  sleep 2\ndone\n\n# Wait for MinIO\nuntil curl -f http://${KOS_MINIO_HOST:-minio}:${KOS_MINIO_INTERNAL_PORT:-9000}/minio/health/live; do\n  echo "Waiting for MinIO..."\n  sleep 2\ndone\n\necho "KOS v1: All services are ready!"\n' > /app/scripts/wait-for-services.sh && chmod +x /app/scripts/wait-for-services.sh

# Set environment variables (will be overridden by docker-compose)
ENV KOS_APP_NAME="KOS v1 Knowledge Library Framework"
ENV KOS_VERSION="1.0.0"
ENV PYTHONPATH=/app

# Expose ports (will be overridden by environment variables)
EXPOSE ${KOS_API_INTERNAL_PORT:-8000} ${KOS_FRONTEND_INTERNAL_PORT:-3000} ${KOS_CADVISOR_INTERNAL_PORT:-8081}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${KOS_API_INTERNAL_PORT:-8000}/health || exit 1

# Start supervisor
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"] 