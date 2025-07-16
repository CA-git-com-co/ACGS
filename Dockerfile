# ACGS-2 Multi-Service Container
# Constitutional Hash: cdd01ef066bc6cf2
# 
# This Dockerfile provides a unified container for ACGS-2 services
# Optimized for security scanning and production deployment

FROM python:3.11-slim as base

# Constitutional compliance metadata
LABEL constitutional.hash="cdd01ef066bc6cf2"
LABEL version="2.0.0"
LABEL description="ACGS-2 Constitutional Governance System"

# Security hardening
RUN groupadd -r acgs && useradd -r -g acgs acgs

# System dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements*.txt ./
COPY services/*/requirements*.txt ./services/

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/config && \
    chown -R acgs:acgs /app

# Security: Remove unnecessary packages and files
RUN apt-get remove -y build-essential && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Switch to non-root user
USER acgs

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8010/health || exit 1

# Default service ports
EXPOSE 8001 8002 8003 8004 8005 8006 8007 8010 8016

# Environment variables
ENV PYTHONPATH=/app
ENV CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
ENV ENVIRONMENT=production

# Default command (can be overridden)
CMD ["python", "-m", "uvicorn", "services.api_gateway.main:app", "--host", "0.0.0.0", "--port", "8010"]
