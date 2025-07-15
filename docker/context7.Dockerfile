# Context7 MCP Server Dockerfile
# Based on official Context7 GitHub repository: https://github.com/upstash/context7

FROM node:18-alpine

# Set working directory
WORKDIR /app

# Install git for cloning the repository
RUN apk add --no-cache git

# Clone the Context7 repository
RUN git clone https://github.com/upstash/context7.git .

# Install dependencies (including dev)
RUN npm install

# Build the application
RUN npm run build

# Prune devDependencies for production
RUN npm prune --production

# Expose port (if needed for web interface)
EXPOSE 3000

# Set environment variables
ENV NODE_ENV=production

# Run the MCP server
CMD ["node", "dist/index.js"] 