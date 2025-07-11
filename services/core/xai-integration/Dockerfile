# ACGS-2 XAI Integration Service Dockerfile
# Constitutional Hash: cdd01ef066bc6cf2

FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV CONSTITUTIONAL_HASH=cdd01ef066bc6cf2

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY xai_service/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY xai_service/ .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash acgs && \
    chown -R acgs:acgs /app
USER acgs

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8014/health || exit 1

# Expose port
EXPOSE 8014

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8014"]
