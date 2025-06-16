# ACGS-1 Evolutionary Computation Service Dockerfile
# Enterprise-grade containerization following ACGS-1 standards

FROM python:3.11-slim-bullseye

# Metadata
LABEL maintainer="ACGS-1 Development Team"
LABEL version="1.0.0"
LABEL description="Evolutionary Computation Service for ACGS-1 Constitutional Governance"
LABEL service="ec"
LABEL port="8006"

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app
ENV SERVICE_NAME=ec_service
ENV SERVICE_PORT=8006
ENV LOG_LEVEL=INFO
ENV WORKERS=4

# Security: Create non-root user
RUN groupadd -r acgs && useradd -r -g acgs -d /app -s /bin/bash acgs

# System dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    curl \
    git \
    libpq-dev \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt requirements-test.txt ./
COPY services/core/ec/requirements.txt ./ec-requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r ec-requirements.txt

# Copy application code
COPY services/core/ec/ ./services/core/ec/
COPY services/shared/ ./services/shared/
COPY config/ ./config/

# Copy startup scripts
COPY scripts/start_services_simple.sh ./scripts/
COPY scripts/health_check.sh ./scripts/

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/tmp && \
    chown -R acgs:acgs /app

# Security: Switch to non-root user
USER acgs

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${SERVICE_PORT}/health || exit 1

# Expose service port
EXPOSE ${SERVICE_PORT}

# Enterprise configuration
ENV ENTERPRISE_MODE=true
ENV CONSTITUTIONAL_COMPLIANCE=enabled
ENV PERFORMANCE_MONITORING=enabled
ENV SECURITY_HARDENING=enabled

# Evolutionary Computation specific configuration
ENV EC_ALGORITHM_TYPE=constitutional_evolution
ENV EC_POPULATION_SIZE=100
ENV EC_MUTATION_RATE=0.01
ENV EC_CROSSOVER_RATE=0.8
ENV EC_SELECTION_METHOD=tournament
ENV EC_FITNESS_FUNCTION=constitutional_compliance
ENV EC_MAX_GENERATIONS=1000
ENV EC_CONVERGENCE_THRESHOLD=0.001

# Performance tuning
ENV EC_PARALLEL_PROCESSING=true
ENV EC_THREAD_POOL_SIZE=8
ENV EC_MEMORY_LIMIT=2GB
ENV EC_CACHE_SIZE=1000

# Integration settings
ENV QUANTUMAGI_INTEGRATION=enabled
ENV CONSTITUTION_HASH=cdd01ef066bc6cf2
ENV BLOCKCHAIN_SYNC=enabled
ENV PGC_INTEGRATION=enabled

# Monitoring and observability
ENV PROMETHEUS_METRICS=enabled
ENV STRUCTURED_LOGGING=enabled
ENV TRACE_SAMPLING_RATE=0.1

# Security settings
ENV SECURITY_HEADERS=enabled
ENV RATE_LIMITING=enabled
ENV INPUT_VALIDATION=strict
ENV AUDIT_LOGGING=enabled

# Database configuration
ENV DATABASE_POOL_SIZE=20
ENV DATABASE_MAX_OVERFLOW=30
ENV DATABASE_POOL_TIMEOUT=30
ENV DATABASE_POOL_RECYCLE=3600

# Redis configuration for caching
ENV REDIS_ENABLED=true
ENV REDIS_CACHE_TTL=3600
ENV REDIS_MAX_CONNECTIONS=100

# Startup command
CMD ["python", "-m", "services.core.ec.main"]

# Alternative startup options for different environments
# Development: CMD ["python", "-m", "services.core.ec.main", "--debug"]
# Production: CMD ["gunicorn", "--bind", "0.0.0.0:8006", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "services.core.ec.main:app"]

# Enterprise deployment annotations
LABEL org.acgs.service.type="core"
LABEL org.acgs.service.tier="production"
LABEL org.acgs.service.scaling="horizontal"
LABEL org.acgs.service.dependencies="auth,pgc,gs"
LABEL org.acgs.service.monitoring="prometheus,grafana"
LABEL org.acgs.service.logging="structured,centralized"
LABEL org.acgs.service.security="rbac,audit,encryption"
LABEL org.acgs.service.compliance="constitutional,enterprise"

# Performance targets
LABEL org.acgs.performance.response_time="<500ms"
LABEL org.acgs.performance.availability=">99.5%"
LABEL org.acgs.performance.throughput=">1000_concurrent"
LABEL org.acgs.performance.memory="<2GB"
LABEL org.acgs.performance.cpu="<80%"

# Integration metadata
LABEL org.acgs.integration.quantumagi="enabled"
LABEL org.acgs.integration.solana="devnet"
LABEL org.acgs.integration.constitution_hash="cdd01ef066bc6cf2"
LABEL org.acgs.integration.pgc="real_time"
LABEL org.acgs.integration.wina="enabled"

# Governance metadata
LABEL org.acgs.governance.constitutional_compliance="enforced"
LABEL org.acgs.governance.policy_synthesis="enabled"
LABEL org.acgs.governance.democratic_participation="supported"
LABEL org.acgs.governance.audit_trail="comprehensive"
LABEL org.acgs.governance.transparency="full"

# Development and debugging support
# Uncomment for development builds
# ENV FLASK_ENV=development
# ENV DEBUG=true
# COPY --chown=acgs:acgs scripts/debug/ ./scripts/debug/

# Production optimizations
# Multi-stage build for smaller production images
# FROM python:3.11-slim-bullseye as production
# COPY --from=builder /app /app
# USER acgs
# CMD ["gunicorn", "--bind", "0.0.0.0:8006", "--workers", "4", "services.core.ec.main:app"]
