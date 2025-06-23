# Constitutional Trainer Service Dockerfile
# Multi-stage build for production-ready container with security hardening
# ACGS-1 Lite Constitutional AI Training Service

# Build stage
FROM python:3.11-slim as builder

# Set build arguments
ARG CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
ARG BUILD_DATE
ARG VERSION=1.0.0

# Set environment variables for build
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for building
RUN groupadd -r constitutional && useradd -r -g constitutional constitutional

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim as production

# Set build arguments
ARG CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
ARG BUILD_DATE
ARG VERSION=1.0.0

# Add labels for container metadata
LABEL maintainer="ACGS-1 Development Team" \
      version="${VERSION}" \
      description="Constitutional Trainer Service for ACGS-1 Lite" \
      constitutional.hash="${CONSTITUTIONAL_HASH}" \
      build.date="${BUILD_DATE}" \
      org.opencontainers.image.title="Constitutional Trainer" \
      org.opencontainers.image.description="ACGS-1 Lite Constitutional AI Training Service" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.source="https://github.com/CA-git-com-co/ACGS" \
      org.opencontainers.image.licenses="MIT"

# Set production environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PATH="/app/.local/bin:$PATH" \
    CONSTITUTIONAL_HASH=${CONSTITUTIONAL_HASH} \
    SERVICE_VERSION=${VERSION} \
    ENVIRONMENT=production

# Install runtime system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Security updates
    ca-certificates \
    # Runtime dependencies
    curl \
    # GPU support (if available)
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user with specific UID/GID for security
RUN groupadd -r -g 1000 constitutional && \
    useradd -r -u 1000 -g constitutional -d /app -s /bin/bash constitutional

# Create necessary directories with proper permissions
RUN mkdir -p /app/logs /app/models /app/data /app/tmp && \
    chown -R constitutional:constitutional /app

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=constitutional:constitutional . .

# Create __init__.py files for proper Python module structure
RUN touch __init__.py && \
    chmod 644 __init__.py

# Set proper permissions for application files
RUN chmod -R 755 /app && \
    chmod -R 644 /app/*.py && \
    chmod +x /app/main.py

# Create health check script
RUN echo '#!/bin/bash\ncurl -f http://localhost:8010/health || exit 1' > /app/healthcheck.sh && \
    chmod +x /app/healthcheck.sh

# Security hardening
RUN chmod 1777 /tmp && \
    # Remove unnecessary packages
    apt-get autoremove -y && \
    # Clear package cache
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Switch to non-root user
USER constitutional

# Expose port
EXPOSE 8010

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD /app/healthcheck.sh

# Volume mounts for persistent data
VOLUME ["/app/models", "/app/data", "/app/logs"]

# Default command
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8010", "--workers", "1"]

# Alternative commands for different deployment scenarios
# Development: CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8010", "--reload"]
# Production with Gunicorn: CMD ["gunicorn", "main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8010"]

# Security scan metadata
LABEL security.scan.enabled="true" \
      security.scan.vendor="trivy" \
      security.compliance.constitutional="true"

# Build information
LABEL build.constitutional_hash="${CONSTITUTIONAL_HASH}" \
      build.version="${VERSION}" \
      build.date="${BUILD_DATE}"
