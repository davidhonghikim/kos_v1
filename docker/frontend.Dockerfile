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