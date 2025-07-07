# Constitutional Hash: cdd01ef066bc6cf2
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Create gemini CLI user
RUN useradd -m -s /bin/bash gemini && \
    mkdir -p /home/gemini/.gemini_cli && \
    chown -R gemini:gemini /home/gemini

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Gemini CLI source
COPY . /app/gemini_cli/
RUN pip install -e /app/gemini_cli/

# Copy ACGS integration files
COPY ../../shared/ /app/shared/
COPY ../../../scripts/ /app/scripts/

# Set up configuration
RUN mkdir -p /home/gemini/.gemini_cli/logs && \
    mkdir -p /home/gemini/.gemini_cli/mcp_servers && \
    chown -R gemini:gemini /home/gemini/.gemini_cli

# Create startup script
RUN cat > /app/start-gemini-cli.sh << 'EOF'
#!/bin/bash
set -e

echo "Starting Gemini CLI with MCP servers..."

# Wait for ACGS services to be ready
echo "Waiting for ACGS services..."
until curl -s http://acgs-coordinator:8000/health > /dev/null 2>&1; do
    echo "Waiting for ACGS Coordinator..."
    sleep 5
done

# Initialize configuration if needed
if [ ! -f "/home/gemini/.gemini_cli/config.json" ]; then
    echo "Initializing Gemini CLI configuration..."
    gemini-cli config init
fi

# Set ACGS service URLs for containerized deployment
gemini-cli config set acgs_coordinator_url "http://acgs-coordinator:8000"
gemini-cli config set auth_service_url "http://auth-service:8006"
gemini-cli config set sandbox_service_url "http://sandbox-service:8009"
gemini-cli config set formal_verification_url "http://formal-verification:8010"
gemini-cli config set audit_service_url "http://audit-service:8011"
gemini-cli config set hitl_service_url "http://hitl-service:8008"

# Start MCP servers in background
echo "Starting MCP servers..."
nohup python -m gemini_cli.mcp_servers.acgs_constitutional > /home/gemini/.gemini_cli/logs/mcp-constitutional.log 2>&1 &
nohup python -m gemini_cli.mcp_servers.filesystem --root /app > /home/gemini/.gemini_cli/logs/mcp-filesystem.log 2>&1 &

# Start the CLI in interactive mode or run command
if [ $# -eq 0 ]; then
    echo "Gemini CLI ready! Use 'docker exec -it <container> gemini-cli <command>'"
    echo "Or start an interactive session with 'docker exec -it <container> bash'"
    tail -f /dev/null
else
    exec gemini-cli "$@"
fi
EOF

RUN chmod +x /app/start-gemini-cli.sh && \
    chown gemini:gemini /app/start-gemini-cli.sh

# Switch to gemini user
USER gemini

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD gemini-cli monitor health || exit 1

# Expose port for MCP servers
EXPOSE 8080

# Default command
CMD ["/app/start-gemini-cli.sh"]