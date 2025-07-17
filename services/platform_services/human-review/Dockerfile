# Human Review Interface Service Dockerfile
# Constitutional Hash: cdd01ef066bc6cf2

FROM node:18-alpine AS frontend-builder

# Build frontend
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# Python backend
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV CONSTITUTIONAL_HASH=cdd01ef066bc6cf2

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Copy built frontend
COPY --from=frontend-builder /app/frontend/build ./frontend/build

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app_user && \
    chown -R app_user:app_user /app
USER app_user

# Expose service port
EXPOSE 8023

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8023/health || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8023"]