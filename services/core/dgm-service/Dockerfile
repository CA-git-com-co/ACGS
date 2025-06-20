# Darwin Gödel Machine Service Dockerfile
# Multi-stage build for production optimization

# Build stage
FROM python:3.11-slim as builder

# Set build arguments
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION=1.0.0

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim as production

# Set build arguments for labels
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION=1.0.0

# Add labels for metadata
LABEL maintainer="ACGS Development Team" \
      org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.name="dgm-service" \
      org.label-schema.description="Darwin Gödel Machine Service for ACGS Platform" \
      org.label-schema.url="https://github.com/CA-git-com-co/ACGS" \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.vcs-url="https://github.com/CA-git-com-co/ACGS" \
      org.label-schema.vendor="ACGS" \
      org.label-schema.version=$VERSION \
      org.label-schema.schema-version="1.0"

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r dgm && useradd -r -g dgm dgm

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=dgm:dgm . .

# Create necessary directories with proper permissions
RUN mkdir -p /app/logs /app/data /app/cache /app/archive && \
    chown -R dgm:dgm /app

# Switch to non-root user
USER dgm

# Expose port
EXPOSE 8007

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8007/health || exit 1

# Set environment variables
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DGM_PORT=8007 \
    DGM_HOST=0.0.0.0

# Default command
CMD ["python", "-m", "dgm_service.main"]

# Development stage
FROM production as development

# Switch back to root for development tools
USER root

# Install development dependencies
RUN apt-get update && apt-get install -y \
    vim \
    htop \
    strace \
    && rm -rf /var/lib/apt/lists/*

# Install development Python packages
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

# Switch back to dgm user
USER dgm

# Override command for development
CMD ["python", "-m", "dgm_service.main", "--reload"]

# Enterprise deployment annotations
LABEL org.acgs.service.type="core" \
      org.acgs.service.tier="production" \
      org.acgs.service.scaling="horizontal" \
      org.acgs.service.dependencies="auth,ac,integrity,fv,gs,pgc,ec,postgres,redis" \
      org.acgs.service.monitoring="prometheus,grafana" \
      org.acgs.service.logging="structured,centralized" \
      org.acgs.service.security="rbac,audit,encryption" \
      org.acgs.service.compliance="constitutional,enterprise" \
      org.acgs.service.dgm="self-improving,evolutionary"
