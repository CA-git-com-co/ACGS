# ACGS-PGP v8 Dockerfile
# Quantum-Inspired Semantic Fault Tolerance System
# Enterprise-grade containerization following ACGS-1 standards

FROM python:3.11-slim-bullseye

# Metadata
LABEL maintainer="ACGS-1 Development Team"
LABEL version="8.0.0"
LABEL description="ACGS-PGP v8: Quantum-Inspired Semantic Fault Tolerance System"
LABEL service="acgs-pgp-v8"
LABEL port="8010"

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app
ENV SERVICE_NAME=acgs-pgp-v8
ENV SERVICE_PORT=8010
ENV LOG_LEVEL=INFO
ENV WORKERS=4

# Security: Create non-root user
RUN groupadd -r acgs && useradd -r -g acgs -d /app -s /bin/bash acgs

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=acgs:acgs . .

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/cache && \
    chown -R acgs:acgs /app

# Switch to non-root user
USER acgs

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8010/health || exit 1

# Performance settings
ENV UVICORN_WORKERS=4
ENV UVICORN_WORKER_CLASS=uvicorn.workers.UvicornWorker
ENV UVICORN_MAX_REQUESTS=1000
ENV UVICORN_MAX_REQUESTS_JITTER=100

# Constitutional governance settings
ENV CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
ENV CONSTITUTIONAL_COMPLIANCE_THRESHOLD=0.8
ENV GOVERNANCE_VALIDATION_ENABLED=true

# Database configuration
ENV DATABASE_URL=postgresql://acgs_user:acgs_password@postgres:5432/acgs_db
ENV DATABASE_POOL_SIZE=20
ENV DATABASE_MAX_OVERFLOW=30
ENV DATABASE_POOL_TIMEOUT=30
ENV DATABASE_POOL_RECYCLE=3600

# Redis configuration
ENV REDIS_URL=redis://redis:6379/0
ENV REDIS_MAX_CONNECTIONS=100
ENV REDIS_CACHE_TTL=3600

# Service integration URLs
ENV AUTH_SERVICE_URL=http://auth_service:8000
ENV AC_SERVICE_URL=http://ac_service:8001
ENV INTEGRITY_SERVICE_URL=http://integrity_service:8002
ENV FV_SERVICE_URL=http://fv_service:8003
ENV GS_SERVICE_URL=http://gs_service:8004
ENV PGC_SERVICE_URL=http://pgc_service:8005
ENV EC_SERVICE_URL=http://ec_service:8006

# Quantum-inspired configuration
ENV QUANTUM_ERROR_CORRECTION=true
ENV SEMANTIC_ENTANGLEMENT_STRENGTH=0.5
ENV DECOHERENCE_THRESHOLD=0.1
ENV FAULT_TOLERANCE_LEVEL=2

# Generation engine configuration
ENV MAX_POLICY_LENGTH=5000
ENV MIN_CONSTITUTIONAL_COMPLIANCE=0.8
ENV CONSENSUS_THRESHOLD=0.7
ENV MAX_CONCURRENT_GENERATIONS=10
ENV GENERATION_TIMEOUT_SECONDS=300
ENV RESPONSE_TIME_TARGET_MS=500

# Multi-model LLM configuration
ENV PRIMARY_MODEL=qwen3-32b
ENV FALLBACK_MODELS=deepseek-chat,qwen3-235b,deepseek-r1
ENV CONSENSUS_STRATEGY=weighted_average
ENV MODEL_TIMEOUT_SECONDS=30

# Monitoring and observability
ENV PROMETHEUS_METRICS=enabled
ENV STRUCTURED_LOGGING=enabled
ENV TRACE_SAMPLING_RATE=0.1
ENV AUDIT_TRAIL_ENABLED=true

# Security settings
ENV SECURITY_HEADERS=enabled
ENV RATE_LIMITING=enabled
ENV INPUT_VALIDATION=strict
ENV JWT_SECRET_KEY=acgs-pgp-v8-secret-key-2024
ENV JWT_ALGORITHM=HS256
ENV JWT_EXPIRATION_MINUTES=30

# Performance optimization
ENV ASYNC_WORKERS=4
ENV CONNECTION_POOL_SIZE=100
ENV REQUEST_TIMEOUT=30
ENV KEEP_ALIVE_TIMEOUT=5
ENV MAX_REQUEST_SIZE=10485760
ENV GZIP_COMPRESSION=true

# Caching configuration
ENV POLICY_GENERATION_CACHE_TTL=3600
ENV CONSTITUTIONAL_VALIDATION_CACHE_TTL=1800
ENV DIAGNOSTIC_RESULTS_CACHE_TTL=900
ENV REPRESENTATION_CACHE_TTL=7200

# Error handling
ENV MAX_RETRIES=3
ENV RETRY_DELAY_SECONDS=1
ENV EXPONENTIAL_BACKOFF=true
ENV CIRCUIT_BREAKER_ENABLED=true
ENV FALLBACK_RESPONSES_ENABLED=true

# Quantumagi integration
ENV QUANTUMAGI_INTEGRATION=enabled
ENV QUANTUMAGI_DEVNET_ENDPOINT=https://api.devnet.solana.com
ENV BLOCKCHAIN_SYNC=enabled
ENV PGC_INTEGRATION=enabled

# Expose port
EXPOSE 8010

# Startup command
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8010", "--workers", "4"]

# Alternative startup options for different environments
# Development: CMD ["python", "main.py"]
# Production with Gunicorn: CMD ["gunicorn", "--bind", "0.0.0.0:8010", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "main:app"]

# Enterprise deployment annotations
LABEL org.acgs.service.type="core"
LABEL org.acgs.service.tier="production"
LABEL org.acgs.service.scaling="horizontal"
LABEL org.acgs.service.dependencies="auth,ac,integrity,fv,gs,pgc,ec,postgres,redis"
LABEL org.acgs.service.monitoring="prometheus,grafana"
LABEL org.acgs.service.logging="structured,centralized"
LABEL org.acgs.service.security="rbac,audit,encryption"
LABEL org.acgs.service.compliance="constitutional,enterprise"
LABEL org.acgs.service.quantum="semantic-fault-tolerance,error-correction"
