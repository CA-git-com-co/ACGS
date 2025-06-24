#!/bin/bash

# ACGS-1 Nano-vLLM Service Deployment Script
# Simplified deployment replacing complex vLLM infrastructure

set -euo pipefail

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DEPLOYMENT_LOG="$PROJECT_ROOT/logs/nano-vllm-deployment.log"
CONFIG_DIR="$PROJECT_ROOT/config/nano-vllm"
DOCKER_COMPOSE_FILE="$PROJECT_ROOT/infrastructure/docker/docker-compose.nano-vllm.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}" | tee -a "$DEPLOYMENT_LOG"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARN: $1${NC}" | tee -a "$DEPLOYMENT_LOG"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" | tee -a "$DEPLOYMENT_LOG"
}

success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] SUCCESS: $1${NC}" | tee -a "$DEPLOYMENT_LOG"
}

# Create necessary directories
mkdir -p "$(dirname "$DEPLOYMENT_LOG")"
mkdir -p "$CONFIG_DIR"
mkdir -p "$PROJECT_ROOT/logs"

# Check prerequisites
check_prerequisites() {
    log "Checking deployment prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        error "Docker daemon is not running"
        exit 1
    fi
    
    # Check if ACGS network exists
    if ! docker network ls | grep -q acgs_network; then
        log "Creating ACGS network..."
        docker network create acgs_network
    fi
    
    success "Prerequisites check completed"
}

# Create configuration files
create_configuration() {
    log "Creating Nano-vLLM configuration..."
    
    # Create main configuration
    cat > "$CONFIG_DIR/service-config.yaml" << 'EOF'
# Nano-vLLM Service Configuration
service:
  name: "nano-vllm-reasoning"
  version: "1.0.0"
  environment: "${ENVIRONMENT:-development}"

models:
  nvidia_acerreason:
    model_path: "nvidia/Llama-3.1-Nemotron-70B-Instruct-HF"
    tensor_parallel_size: 1
    gpu_memory_utilization: 0.9
    max_model_len: 32768
    port: 8000
    specialties: ["governance", "accountability"]
    
  microsoft_phi4:
    model_path: "microsoft/Phi-4"
    tensor_parallel_size: 1
    gpu_memory_utilization: 0.6
    max_model_len: 16384
    port: 8001
    specialties: ["ethics", "fairness"]

constitutional:
  principles_file: "/app/constitutional/principles.yaml"
  compliance_threshold: 0.75
  reasoning_depth: "standard"
  require_citations: true

performance:
  max_concurrent_requests: 10
  request_timeout: 60
  health_check_interval: 30
  
logging:
  level: "INFO"
  format: "structured"
  file: "/app/logs/nano-vllm.log"

monitoring:
  metrics_enabled: true
  prometheus_port: 9090
  health_endpoint: "/health"
EOF

    # Create constitutional principles
    mkdir -p "$PROJECT_ROOT/config/constitutional"
    cat > "$PROJECT_ROOT/config/constitutional/principles.yaml" << 'EOF'
# Constitutional Principles for AI Governance
version: "2.0"
principles:
  transparency:
    name: "Transparency"
    description: "All governance decisions must be transparent and auditable"
    weight: 0.25
    keywords: ["transparent", "open", "auditable", "visible", "clear"]
    
  fairness:
    name: "Fairness" 
    description: "Policies must treat all stakeholders fairly and equitably"
    weight: 0.25
    keywords: ["fair", "equitable", "just", "equal", "unbiased"]
    
  privacy:
    name: "Privacy"
    description: "User privacy and data rights must be protected"
    weight: 0.25
    keywords: ["privacy", "protect", "consent", "rights", "confidential"]
    
  accountability:
    name: "Accountability"
    description: "Decision makers must be accountable for their actions"
    weight: 0.25
    keywords: ["accountable", "responsible", "oversight", "liable"]
EOF

    success "Configuration files created"
}

# Build Docker images
build_images() {
    log "Building Nano-vLLM Docker images..."
    
    cd "$PROJECT_ROOT"
    
    # Build the main service image
    docker-compose -f "$DOCKER_COMPOSE_FILE" build nano-vllm-reasoning
    
    success "Docker images built successfully"
}

# Deploy services
deploy_services() {
    log "Deploying Nano-vLLM services..."
    
    cd "$PROJECT_ROOT"
    
    # Stop any existing services
    docker-compose -f "$DOCKER_COMPOSE_FILE" down 2>/dev/null || true
    
    # Start services
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
    
    success "Services deployed successfully"
}

# Health check
health_check() {
    log "Performing health checks..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        log "Health check attempt $attempt/$max_attempts"
        
        # Check main service
        if curl -f http://localhost:8000/health &>/dev/null; then
            success "Nano-vLLM service is healthy"
            return 0
        fi
        
        sleep 10
        ((attempt++))
    done
    
    error "Health check failed after $max_attempts attempts"
    return 1
}

# Show service status
show_status() {
    log "Service Status:"
    docker-compose -f "$DOCKER_COMPOSE_FILE" ps
    
    log "Service Logs (last 20 lines):"
    docker-compose -f "$DOCKER_COMPOSE_FILE" logs --tail=20 nano-vllm-reasoning
}

# Stop services
stop_services() {
    log "Stopping Nano-vLLM services..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" down
    success "Services stopped"
}

# Clean up (remove containers and volumes)
cleanup() {
    log "Cleaning up Nano-vLLM deployment..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" down -v --remove-orphans
    docker system prune -f
    success "Cleanup completed"
}

# Main deployment function
deploy() {
    log "Starting Nano-vLLM service deployment"
    log "Project root: $PROJECT_ROOT"
    log "Deployment log: $DEPLOYMENT_LOG"
    
    check_prerequisites
    create_configuration
    build_images
    deploy_services
    
    if health_check; then
        success "Deployment completed successfully"
        show_status
        
        log "Service endpoints:"
        log "  - Main service: http://localhost:8000"
        log "  - Health check: http://localhost:8000/health"
        log "  - Metrics: http://localhost:9100/metrics"
        
    else
        error "Deployment failed health checks"
        show_status
        exit 1
    fi
}

# Main function
main() {
    case "${1:-deploy}" in
        "deploy")
            deploy
            ;;
        "stop")
            stop_services
            ;;
        "status")
            show_status
            ;;
        "health")
            health_check
            ;;
        "cleanup")
            cleanup
            ;;
        "logs")
            docker-compose -f "$DOCKER_COMPOSE_FILE" logs -f nano-vllm-reasoning
            ;;
        *)
            echo "Usage: $0 {deploy|stop|status|health|cleanup|logs}"
            echo "  deploy:  Deploy Nano-vLLM services"
            echo "  stop:    Stop all services"
            echo "  status:  Show service status"
            echo "  health:  Check service health"
            echo "  cleanup: Remove all containers and volumes"
            echo "  logs:    Follow service logs"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
