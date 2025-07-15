# 5-Tier Router Metrics Exporter Dockerfile
# Constitutional Hash: cdd01ef066bc6cf2

FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN groupadd -r metrics && useradd -r -g metrics metrics
RUN chown -R metrics:metrics /app
USER metrics

# Expose metrics port
EXPOSE 9200

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:9200/metrics || exit 1

# Start exporter
CMD ["python", "router_metrics_exporter.py"]
