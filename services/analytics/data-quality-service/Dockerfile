# ACGS Data Quality Microservice
# Constitutional Hash: cdd01ef066bc6cf2

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY ../../core/acgs-pgp-v8/ ./core/acgs-pgp-v8/

# Create non-root user for security
RUN useradd -m -u 1000 acgs && chown -R acgs:acgs /app
USER acgs

# Expose service port
EXPOSE 8010

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8010/health || exit 1

# Set environment variables
ENV PYTHONPATH=/app/core
ENV CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
ENV SERVICE_PORT=8010

# Run the service
CMD ["python", "app.py"]
