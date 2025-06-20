#!/bin/bash
# ACGS Production Deployment Script with UV
# Updated for UV-based dependency management

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] SUCCESS: $1${NC}"
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENVIRONMENT="${ENVIRONMENT:-production}"
DEPLOY_TYPE="${DEPLOY_TYPE:-docker}"

# UV-based deployment functions
setup_uv_environment() {
    log "Setting up UV-based Python environment..."
    
    cd "$PROJECT_ROOT"
    
    # Check if UV is installed
    if ! command -v uv &> /dev/null; then
        log "Installing UV..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        source ~/.cargo/env
    fi
    
    # Verify UV installation
    uv --version
    success "UV is available"
    
    # Sync dependencies using UV
    log "Syncing Python dependencies with UV..."
    if uv sync --frozen; then
        success "Dependencies synced successfully with UV"
    else
        error "Failed to sync dependencies with UV"
        exit 1
    fi
    
    # Activate virtual environment
    source .venv/bin/activate
    success "UV virtual environment activated"
}

# Verify service functionality with UV
verify_service_with_uv() {
    local service_name=$1
    local service_port=$2
    
    log "Verifying $service_name with UV environment..."
    
    cd "$PROJECT_ROOT"
    source .venv/bin/activate
    
    # Start service in background for testing
    case $service_name in
        "constitutional-ai")
            cd services/core/constitutional-ai
            timeout 5 python simple_ac_main.py &
            local service_pid=$!
            ;;
        "governance-synthesis")
            cd services/core/governance-synthesis
            timeout 5 python gs_service_main.py &
            local service_pid=$!
            ;;
        *)
            warning "Unknown service: $service_name"
            return 1
            ;;
    esac
    
    # Wait for service to start
    sleep 3
    
    # Test health endpoint
    if curl -f "http://localhost:$service_port/health" > /dev/null 2>&1; then
        success "$service_name health check passed"
        kill $service_pid 2>/dev/null || true
        return 0
    else
        error "$service_name health check failed"
        kill $service_pid 2>/dev/null || true
        return 1
    fi
}

# Deploy with Docker using UV
deploy_docker_with_uv() {
    log "Deploying with Docker using UV-based images..."
    
    # Create UV-based Dockerfile
    create_uv_dockerfile
    
    # Build images
    log "Building Docker images with UV..."
    docker-compose -f docker-compose.uv.yml build --no-cache
    
    # Deploy services
    log "Starting services with UV-based containers..."
    docker-compose -f docker-compose.uv.yml up -d
    
    success "Docker deployment with UV completed"
}

# Create UV-based Dockerfile
create_uv_dockerfile() {
    log "Creating UV-based Dockerfile..."
    
    cat > "$PROJECT_ROOT/Dockerfile.uv" << 'EOF'
FROM python:3.13-slim

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies with UV
RUN uv sync --frozen --no-cache

# Copy application code
COPY . .

# Set Python path
ENV PYTHONPATH="/app:$PYTHONPATH"

# Activate virtual environment
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Create non-root user
RUN useradd --create-home --shell /bin/bash acgs
RUN chown -R acgs:acgs /app
USER acgs

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Default command
CMD ["python", "-m", "uvicorn", "services.core.constitutional_ai.simple_ac_main:app", "--host", "0.0.0.0", "--port", "8001"]
EOF

    success "UV-based Dockerfile created"
}

# Create UV-based docker-compose
create_uv_docker_compose() {
    log "Creating UV-based docker-compose.yml..."
    
    cat > "$PROJECT_ROOT/docker-compose.uv.yml" << 'EOF'
version: '3.8'

services:
  constitutional-ai:
    build:
      context: .
      dockerfile: Dockerfile.uv
    ports:
      - "8001:8001"
    environment:
      - PYTHONPATH=/app
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    restart: unless-stopped

  governance-synthesis:
    build:
      context: .
      dockerfile: Dockerfile.uv
    ports:
      - "8002:8002"
    environment:
      - PYTHONPATH=/app
    command: ["python", "-m", "uvicorn", "services.core.governance_synthesis.gs_service_main:app", "--host", "0.0.0.0", "--port", "8002"]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8002/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    restart: unless-stopped

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: acgs_production
      POSTGRES_USER: acgs_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
EOF

    success "UV-based docker-compose.yml created"
}

# Host-based deployment with UV
deploy_host_with_uv() {
    log "Deploying on host using UV..."
    
    setup_uv_environment
    
    # Verify core services
    log "Verifying core services with UV..."
    verify_service_with_uv "constitutional-ai" 8001
    
    # Start services with systemd (if available)
    if command -v systemctl &> /dev/null; then
        create_systemd_services_uv
        start_systemd_services
    else
        warning "systemctl not available, starting services manually"
        start_services_manually
    fi
    
    success "Host-based deployment with UV completed"
}

# Create systemd services for UV
create_systemd_services_uv() {
    log "Creating systemd services for UV-based deployment..."
    
    # Constitutional AI service
    sudo tee /etc/systemd/system/acgs-constitutional-ai.service > /dev/null << EOF
[Unit]
Description=ACGS Constitutional AI Service
After=network.target

[Service]
Type=simple
User=acgs
WorkingDirectory=$PROJECT_ROOT
Environment=PYTHONPATH=$PROJECT_ROOT
ExecStart=$PROJECT_ROOT/.venv/bin/python -m uvicorn services.core.constitutional_ai.simple_ac_main:app --host 0.0.0.0 --port 8001
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd
    sudo systemctl daemon-reload
    sudo systemctl enable acgs-constitutional-ai
    
    success "Systemd services created for UV deployment"
}

# Start systemd services
start_systemd_services() {
    log "Starting ACGS services with systemd..."
    
    sudo systemctl start acgs-constitutional-ai
    
    # Wait for services to start
    sleep 5
    
    # Check service status
    if systemctl is-active --quiet acgs-constitutional-ai; then
        success "Constitutional AI service is running"
    else
        error "Constitutional AI service failed to start"
        sudo systemctl status acgs-constitutional-ai
        exit 1
    fi
}

# Validate deployment
validate_deployment() {
    log "Validating UV-based deployment..."
    
    local services=("constitutional-ai:8001")
    
    for service_info in "${services[@]}"; do
        IFS=':' read -r service_name port <<< "$service_info"
        
        log "Testing $service_name on port $port..."
        
        # Test health endpoint
        if curl -f "http://localhost:$port/health" > /dev/null 2>&1; then
            success "$service_name is healthy"
        else
            error "$service_name health check failed"
            return 1
        fi
        
        # Test root endpoint
        if curl -f "http://localhost:$port/" > /dev/null 2>&1; then
            success "$service_name root endpoint is accessible"
        else
            warning "$service_name root endpoint test failed"
        fi
    done
    
    success "All services validated successfully"
}

# Main deployment function
main() {
    log "Starting ACGS Production Deployment with UV"
    echo "=============================================="
    echo "Environment: $ENVIRONMENT"
    echo "Deploy Type: $DEPLOY_TYPE"
    echo "Project Root: $PROJECT_ROOT"
    echo "=============================================="
    
    case $DEPLOY_TYPE in
        "docker")
            create_uv_docker_compose
            deploy_docker_with_uv
            ;;
        "host")
            deploy_host_with_uv
            ;;
        *)
            error "Unknown deployment type: $DEPLOY_TYPE"
            exit 1
            ;;
    esac
    
    # Validate deployment
    sleep 10
    validate_deployment
    
    success "🎉 ACGS Production Deployment with UV Complete!"
    echo "=============================================="
    echo "Constitutional AI Service: http://localhost:8001"
    echo "Health Check: http://localhost:8001/health"
    echo "API Documentation: http://localhost:8001/docs"
    echo "=============================================="
}

# Run main function
main "$@"
