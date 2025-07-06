# Multi-stage Dockerfile for ACGS Code Analysis Engine
# Constitutional Hash: cdd01ef066bc6cf2

# =============================================================================
# Stage 1: Base Dependencies
# =============================================================================
FROM python:3.12-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create application directory
WORKDIR /app

# =============================================================================
# Stage 2: Development Dependencies
# =============================================================================
FROM base as development

# Install build dependencies first
RUN pip install --no-cache-dir setuptools wheel

# Copy requirements first for better caching
COPY code_analysis_service/requirements_minimal.txt ./requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install development dependencies
RUN pip install --no-cache-dir \
    pytest \
    pytest-cov \
    pytest-asyncio \
    black \
    ruff \
    mypy

# Copy source code
COPY code_analysis_service/ ./

# Create non-root user for development
RUN groupadd -r acgs && useradd -r -g acgs -d /app -s /bin/bash acgs \
    && chown -R acgs:acgs /app

USER acgs

# Expose ports
EXPOSE 8007 9091

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8007/health || exit 1

# Default command for development
CMD ["python", "main_simple.py"]

# =============================================================================
# Stage 3: Production Dependencies
# =============================================================================
FROM base as production-deps

# Install build dependencies first
RUN pip install --no-cache-dir setuptools wheel

# Copy requirements and install only production dependencies
COPY code_analysis_service/requirements_minimal.txt ./requirements.txt

# Install production Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# =============================================================================
# Stage 4: Production Runtime
# =============================================================================
FROM production-deps as production

# Copy application code
COPY code_analysis_service/ ./

# Create logs and data directories
RUN mkdir -p /app/logs /app/data

# Create non-root user for security
RUN groupadd -r acgs && useradd -r -g acgs -d /app -s /bin/bash acgs \
    && chown -R acgs:acgs /app

# Create health check script
RUN echo '#!/bin/bash\ncurl -f http://localhost:8007/health || exit 1' > /app/health_check.sh \
    && chmod +x /app/health_check.sh \
    && chown acgs:acgs /app/health_check.sh

USER acgs

# Set Python path
ENV PYTHONPATH="/app:$PYTHONPATH"

# Expose ports
EXPOSE 8007 9091

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD /app/health_check.sh

# Production command
CMD ["uvicorn", "main_simple:app", "--host", "0.0.0.0", "--port", "8007", "--workers", "4"]

# =============================================================================
# Stage 5: Testing
# =============================================================================
FROM development as testing

# Install additional testing dependencies
RUN pip install --no-cache-dir \
    requests \
    matplotlib \
    numpy \
    asyncpg \
    redis

# Copy test files
COPY code_analysis_service/test_*.py ./
COPY code_analysis_service/run_priority3_validation.py ./
COPY code_analysis_service/validate_test_suite.py ./
COPY code_analysis_service/deployment_readiness_validation.py ./

# Set environment for testing
ENV ENVIRONMENT=testing \
    LOG_LEVEL=INFO \
    POSTGRESQL_PASSWORD=test_password \
    JWT_SECRET_KEY=test_jwt_secret_key_for_development_only \
    REDIS_PASSWORD=""

# Default command for testing
CMD ["python", "run_priority3_validation.py"]

# =============================================================================
# Build Arguments and Labels
# =============================================================================
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION=1.0.0

LABEL maintainer="ACGS Team <team@acgs.ai>" \
      org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.name="ACGS Code Analysis Engine" \
      org.label-schema.description="Intelligent code analysis, semantic search, and dependency mapping service for ACGS" \
      org.label-schema.url="https://acgs.ai" \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.vcs-url="https://github.com/CA-git-com-co/ACGS.git" \
      org.label-schema.vendor="ACGS" \
      org.label-schema.version=$VERSION \
      org.label-schema.schema-version="1.0" \
      constitutional.hash="cdd01ef066bc6cf2" \
      service.name="acgs-code-analysis-engine" \
      service.port="8007" \
      service.version="1.0.0"
