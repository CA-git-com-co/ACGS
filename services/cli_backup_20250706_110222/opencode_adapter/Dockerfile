FROM node:20-alpine AS builder

# Install build dependencies
RUN apk add --no-cache python3 make g++

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY tsconfig.json ./

# Install dependencies
RUN npm ci --legacy-peer-deps

# Copy source code
COPY src ./src

# Build the application
RUN npm run build

# Production stage
FROM node:20-alpine

# Create non-root user
RUN addgroup -g 1000 opencode && \
    adduser -u 1000 -G opencode -s /bin/sh -D opencode

WORKDIR /app

# Copy package files and install production dependencies
COPY package*.json ./
RUN npm ci --only=production --legacy-peer-deps && \
    npm cache clean --force

# Copy built application from builder
COPY --from=builder /app/dist ./dist

# Copy configuration files
COPY .env.example .env.example

# Set ownership
RUN chown -R opencode:opencode /app

# Switch to non-root user
USER opencode

# Expose service port
EXPOSE 8020

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD node -e "require('http').get('http://localhost:8020/health', (res) => { process.exit(res.statusCode === 200 ? 0 : 1); })"

# Start the service
CMD ["node", "dist/index.js"]