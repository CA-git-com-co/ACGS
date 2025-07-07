# Unified Governance Engine Service Dockerfile
# Constitutional Hash: cdd01ef066bc6cf2

FROM python:3.11-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY pyproject.toml ./
COPY services/shared ./services/shared

# Install Python dependencies
RUN pip install --no-cache-dir -e ".[ai,dev]"

# Copy service code
COPY services/core/governance-engine ./services/core/governance-engine

# Set environment variables
ENV PYTHONPATH=/app
ENV SERVICE_NAME=governance-engine
ENV SERVICE_PORT=8004
ENV CONSTITUTIONAL_HASH=cdd01ef066bc6cf2

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8004/health || exit 1

# Expose port
EXPOSE 8004

# Run the service
CMD ["uvicorn", "services.core.governance-engine.app.main:app", "--host", "0.0.0.0", "--port", "8004"]