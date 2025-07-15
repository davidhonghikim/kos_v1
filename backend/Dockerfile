# Multi-stage build for KOS v1 Backend
# Stage 1: Base Python image
FROM python:3.11-slim AS base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Stage 2: Dependencies installation
FROM base AS deps

# Copy requirements files
COPY requirements/*.txt ./

# Set pip configuration
RUN pip config set global.index-url https://pypi.org/simple/ && \
    pip config set global.trusted-host pypi.org pypi.python.org files.pythonhosted.org

# Install Python dependencies
RUN echo "Installing Python dependencies..." && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r core.txt && \
    pip install --no-cache-dir -r database.txt && \
    pip install --no-cache-dir -r ai-ml.txt && \
    echo "Python dependencies installed successfully"

# Stage 3: Development runtime
FROM base AS dev

# Copy dependencies from deps stage
COPY --from=deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy source code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV ENVIRONMENT=development
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start development server
CMD ["python", "main.py"]

# Stage 4: Production runtime
FROM base AS production

# Copy dependencies from deps stage
COPY --from=deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy source code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV ENVIRONMENT=production
ENV PYTHONUNBUFFERED=1

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Change ownership of the app directory
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start production server
CMD ["python", "main.py"] 