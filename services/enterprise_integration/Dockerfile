# ACGS Enterprise Integration Hub Dockerfile

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libldap2-dev \
    libsasl2-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY integration_hub.py .

# Create non-root user
RUN useradd -m -u 1000 acgs && chown -R acgs:acgs /app
USER acgs

# Expose port
EXPOSE 8020

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8020/api/v1/health || exit 1

# Run the application
CMD ["python", "integration_hub.py"]
