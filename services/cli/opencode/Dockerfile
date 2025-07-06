# OpenCode CLI with ACGS Integration Dockerfile
# Multi-stage build for production-ready container
# Constitutional Hash: cdd01ef066bc6cf2

# Stage 1: Build stage
FROM oven/bun:1.2.8-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files first for better layer caching
COPY package.json bun.lockb ./

# Install dependencies
RUN bun install --frozen-lockfile

# Copy source code and configuration
COPY src/ ./src/
COPY tsconfig.json ./
COPY acgs-config.json ./

# Type check and prepare for production
RUN bun run typecheck

# Stage 2: Production runtime
FROM oven/bun:1.2.8-alpine AS production

# Create non-root user for security
RUN addgroup -g 1001 -S acgs && \
    adduser -S acgs -u 1001

# Set working directory
WORKDIR /app

# Install curl for health checks
RUN apk add --no-cache curl

# Copy built application from builder stage
COPY --from=builder --chown=acgs:acgs /app .

# Create directories for logs and data
RUN mkdir -p logs data && \
    chown -R acgs:acgs logs data

# Set environment variables
ENV NODE_ENV=production \
    ACGS_CONFIG_PATH=/app/acgs-config.json \
    CONSTITUTIONAL_HASH=cdd01ef066bc6cf2

# Expose port (though CLI typically doesn't serve HTTP)
EXPOSE 8020

# Health check script
RUN echo '#!/bin/sh\nbun run acgs-health > /dev/null 2>&1 || exit 1' > /health-check.sh && \
    chmod +x /health-check.sh && \
    chown acgs:acgs /health-check.sh

# Switch to non-root user
USER acgs

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD /health-check.sh

# Default command - keep container running for CLI access
CMD ["bun", "run", "start"]