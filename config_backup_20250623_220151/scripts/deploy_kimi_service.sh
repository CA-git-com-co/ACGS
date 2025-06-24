#!/bin/bash

# ACGS Kimi-Dev-72B Deployment Script
# Enterprise-grade deployment with comprehensive validation and monitoring

set -euo pipefail

# =============================================================================
# Configuration
# =============================================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
COMPOSE_FILE="$PROJECT_ROOT/infrastructure/docker/docker-compose.kimi.yml"
SWE_COMPOSE_FILE="$PROJECT_ROOT/infrastructure/docker/docker-compose.kimi-swe.yml"
ENV_FILE="$PROJECT_ROOT/.env"
LOG_FILE="$PROJECT_ROOT/logs/kimi-deployment-$(date +%Y%m%d-%H%M%S).log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# =============================================================================
# Logging Functions
# =============================================================================
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

# =============================================================================
# Validation Functions
# =============================================================================
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check NVIDIA Docker runtime
    if ! docker info | grep -q nvidia; then
        log_warning "NVIDIA Docker runtime not detected. GPU acceleration may not work."
    fi
    
    # Check GPU availability
    if command -v nvidia-smi &> /dev/null; then
        GPU_COUNT=$(nvidia-smi --list-gpus | wc -l)
        log_info "Found $GPU_COUNT GPU(s)"
        nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv,noheader,nounits | tee -a "$LOG_FILE"
    else
        log_warning "nvidia-smi not found. Cannot verify GPU availability."
    fi
    
    # Check disk space for model cache
    CACHE_DIR="${HOME}/.cache/huggingface"
    if [[ -d "$CACHE_DIR" ]]; then
        AVAILABLE_SPACE=$(df -BG "$CACHE_DIR" | awk 'NR==2 {print $4}' | sed 's/G//')
        if [[ $AVAILABLE_SPACE -lt 200 ]]; then
            log_warning "Low disk space in cache directory: ${AVAILABLE_SPACE}GB available. Kimi-Dev-72B requires ~150GB."
        fi
    fi
    
    log_success "Prerequisites check completed"
}

check_environment() {
    log_info "Checking environment configuration..."
    
    if [[ ! -f "$ENV_FILE" ]]; then
        log_error "Environment file not found: $ENV_FILE"
        exit 1
    fi
    
    # Check required environment variables
    source "$ENV_FILE"
    
    if [[ -z "${HUGGINGFACE_API_KEY:-}" ]]; then
        log_error "HUGGINGFACE_API_KEY not set in environment"
        exit 1
    fi
    
    if [[ -z "${KIMI_SERVICE_URL:-}" ]]; then
        log_error "KIMI_SERVICE_URL not set in environment"
        exit 1
    fi
    
    log_success "Environment configuration validated"
}

create_directories() {
    log_info "Creating required directories..."
    
    mkdir -p "$PROJECT_ROOT/logs"
    mkdir -p "$PROJECT_ROOT/config/kimi"
    mkdir -p "${HOME}/.cache/huggingface"
    mkdir -p "/tmp/prometheus_multiproc_dir"
    
    log_success "Directories created"
}

# =============================================================================
# Network Management
# =============================================================================
setup_network() {
    log_info "Setting up Docker network..."
    
    if ! docker network ls | grep -q acgs_network; then
        docker network create acgs_network
        log_success "Created acgs_network"
    else
        log_info "acgs_network already exists"
    fi
}

# =============================================================================
# Service Management
# =============================================================================
pull_images() {
    log_info "Pulling Docker images..."
    
    docker pull vllm/vllm-openai:latest
    docker pull prom/node-exporter:latest
    
    log_success "Images pulled successfully"
}

deploy_service() {
    log_info "Deploying Kimi service..."

    cd "$PROJECT_ROOT"

    # Check if SWE-bench mode is enabled
    if [[ "${ENABLE_SWE_BENCH:-false}" == "true" ]]; then
        log_info "Deploying in SWE-bench mode..."
        docker-compose -f "$SWE_COMPOSE_FILE" --env-file "$ENV_FILE" up -d
    else
        log_info "Deploying in standard mode..."
        docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d
    fi

    log_success "Kimi service deployed"
}

wait_for_service() {
    log_info "Waiting for Kimi service to be ready..."
    
    local max_attempts=60  # 10 minutes with 10-second intervals
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -sf http://localhost:8007/health > /dev/null 2>&1; then
            log_success "Kimi service is ready!"
            return 0
        fi
        
        log_info "Attempt $attempt/$max_attempts: Service not ready yet, waiting..."
        sleep 10
        ((attempt++))
    done
    
    log_error "Service failed to become ready within timeout"
    return 1
}

# =============================================================================
# Validation Functions
# =============================================================================
validate_deployment() {
    log_info "Validating deployment..."
    
    # Check container status
    if ! docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
        log_error "Containers are not running properly"
        return 1
    fi
    
    # Test API endpoint
    if ! curl -sf http://localhost:8007/v1/models > /dev/null; then
        log_error "API endpoint not responding"
        return 1
    fi
    
    # Test chat completion
    local test_response
    test_response=$(curl -s -X POST "http://localhost:8007/v1/chat/completions" \
        -H "Content-Type: application/json" \
        --data '{
            "model": "kimi-dev-72b",
            "messages": [{"role": "user", "content": "Hello, test message"}],
            "max_tokens": 10
        }')
    
    if [[ -z "$test_response" ]] || ! echo "$test_response" | jq -e '.choices[0].message.content' > /dev/null 2>&1; then
        log_error "Chat completion test failed"
        return 1
    fi
    
    log_success "Deployment validation completed successfully"
}

# =============================================================================
# Main Execution
# =============================================================================
main() {
    log_info "Starting Kimi-Dev-72B deployment..."
    log_info "Log file: $LOG_FILE"
    
    check_prerequisites
    check_environment
    create_directories
    setup_network
    pull_images
    deploy_service
    
    if wait_for_service; then
        validate_deployment
        log_success "Kimi-Dev-72B deployment completed successfully!"
        log_info "Service available at: http://localhost:8007"
        log_info "API documentation: http://localhost:8007/docs"
        log_info "Health check: http://localhost:8007/health"
    else
        log_error "Deployment failed"
        exit 1
    fi
}

# =============================================================================
# Script Execution
# =============================================================================
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
