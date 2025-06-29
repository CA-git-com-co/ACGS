# ACGS-1 Lite Policy Engine Optimization Service
# Constitutional Hash: cdd01ef066bc6cf2

FROM python:3.11-slim

LABEL maintainer="ACGS-1 Lite Team"
LABEL constitutional_hash="cdd01ef066bc6cf2"
LABEL service="policy-engine-optimization"
LABEL version="1.0.0"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install OPA binary for policy compilation
RUN curl -L -o /usr/local/bin/opa https://openpolicyagent.org/downloads/v0.58.0/opa_linux_amd64_static \
    && chmod +x /usr/local/bin/opa

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy policy files
COPY *.rego ./
COPY constitutional/ constitutional/
COPY evolution/ evolution/
COPY data/ data/
COPY tests/ tests/
COPY .manifest .

# Copy application code
COPY main.py .
COPY build.sh .
COPY test.sh .

# Build optimized policy bundle
RUN chmod +x build.sh test.sh && \
    ./build.sh && \
    mkdir -p /app/policies && \
    cp build/*.tar.gz /app/policies/ || echo "Bundle build failed, will use fallback"

# Create directories
RUN mkdir -p /app/logs /app/cache

# Set environment variables
ENV PYTHONPATH=/app
ENV POLICY_BUNDLE_PATH=/app/policies/acgs-constitutional-policies-1.0.0.tar.gz
ENV REDIS_URL=redis://redis:6379
ENV PORT=8004
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8004/v1/data/acgs/main/health || exit 1

# Security settings
RUN groupadd -r acgs && useradd -r -g acgs acgs
RUN chown -R acgs:acgs /app
USER acgs

# Expose port
EXPOSE 8004

# Start command
CMD ["python", "main.py"]