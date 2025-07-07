# Constitutional Hash: cdd01ef066bc6cf2
# ACGS-1 Security Event Processor
# Real-time security event analysis and automated response

FROM python:3.11-slim

LABEL maintainer="ACGS-1 Security Team"
LABEL description="ACGS-1 Security Event Processor for real-time threat detection"
LABEL version="1.0.0"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    jq \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN groupadd -r acgs && useradd -r -g acgs acgs
RUN chown -R acgs:acgs /app
USER acgs

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose port
EXPOSE 8080

# Run the application
CMD ["python", "security_processor.py"]
