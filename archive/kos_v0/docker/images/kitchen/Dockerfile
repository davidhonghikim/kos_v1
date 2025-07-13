# Kitchen Service Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV KOS_ENV=development

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/core/kitchen/ ./src/core/kitchen/
COPY src/shared/ ./src/shared/
COPY config/ ./config/
COPY data/ ./data/

# Create non-root user
RUN useradd --create-home --shell /bin/bash kos && \
    chown -R kos:kos /app
USER kos

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/kitchen/health')" || exit 1

# Run Kitchen engine
CMD ["python", "-m", "src.core.kitchen.engine"] 