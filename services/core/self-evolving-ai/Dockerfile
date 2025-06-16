# ACGS-1 Self-Evolving AI Architecture Foundation Service
# Multi-stage Docker build for production deployment

# Build stage
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
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
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Production stage
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH="/app"

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r acgs && useradd -r -g acgs acgs

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Create application directory
WORKDIR /app

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/config && \
    chown -R acgs:acgs /app

# Copy application code
COPY --chown=acgs:acgs app/ /app/app/
COPY --chown=acgs:acgs *.py /app/
COPY --chown=acgs:acgs *.md /app/

# Create configuration file
RUN echo "# ACGS-1 Self-Evolving AI Configuration" > /app/.env && \
    echo "ENVIRONMENT=production" >> /app/.env && \
    echo "DEBUG=false" >> /app/.env && \
    echo "HOST=0.0.0.0" >> /app/.env && \
    echo "PORT=8007" >> /app/.env && \
    chown acgs:acgs /app/.env

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8007/health || exit 1

# Switch to non-root user
USER acgs

# Expose port
EXPOSE 8007

# Default command
CMD ["python", "-m", "app.main"]

# Labels for metadata
LABEL maintainer="ACGS Development Team" \
      version="1.0.0" \
      description="ACGS-1 Self-Evolving AI Architecture Foundation Service" \
      service="self-evolving-ai" \
      component="core" \
      architecture="multi-layer-security" \
      features="manual-evolution,human-oversight,opa-integration,observability" \
      performance.targets="1000-concurrent,99.9-availability,500ms-response" \
      quantumagi.compatible="true" \
      constitution.hash="cdd01ef066bc6cf2"
