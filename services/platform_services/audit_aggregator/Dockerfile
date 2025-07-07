# ACGS Audit Aggregation Service Dockerfile
# Constitutional Hash: cdd01ef066bc6cf2

FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create audit storage directories
RUN mkdir -p /app/logs/audit && \
    mkdir -p /app/audit_keys && \
    chmod 755 /app/logs/audit && \
    chmod 700 /app/audit_keys

# Expose port
EXPOSE 8015

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8015/health || exit 1

# Add constitutional hash as environment variable
ENV CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
ENV SERVICE_NAME=audit-aggregator

# Run the application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8015"]