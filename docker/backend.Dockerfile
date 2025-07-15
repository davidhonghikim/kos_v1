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