# Constitutional Hash: cdd01ef066bc6cf2
# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install any needed packages specified in requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app

# Set Python path to include shared module
ENV PYTHONPATH="/app:$PYTHONPATH"

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash acgs
RUN chown -R acgs:acgs /app
USER acgs

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8003/health || exit 1

# Make port 8003 available to the world outside this container
EXPOSE 8003

# Run main.py when the container launches
# The command should point to main:app since main.py is in the root directory
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003", "--workers", "2"]
