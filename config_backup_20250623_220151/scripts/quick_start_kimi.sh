#!/bin/bash

# ACGS Kimi-Dev-72B Quick Start Script
# One-command deployment for immediate testing

set -euo pipefail

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}"
cat << "EOF"
    ___   _____ _____ _____   _  _____ __  __ _____ 
   / _ \ / ____/ ____|  __ \ | |/ /_ _|  \/  |_ _|
  / /_\ | |   | |  __| |__) || ' / | || |\/| || | 
 /  _  | |   | | |_ |  _  / |  <  | || |  | || | 
/_/ \_|_|    \____|_| \_\ |_|\_\|___|_|  |_|___|
                                                
Kimi-Dev-72B Quick Start Deployment
EOF
echo -e "${NC}"

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check if running with sudo (not recommended)
if [[ $EUID -eq 0 ]]; then
    log_warning "Running as root is not recommended. Consider running as a regular user."
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Quick prerequisites check
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        echo "Install with: curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed."
        exit 1
    fi
    
    # Check if user is in docker group
    if ! groups | grep -q docker; then
        log_warning "User is not in docker group. You may need to use sudo."
    fi
    
    # Check NVIDIA runtime
    if ! docker info 2>/dev/null | grep -q nvidia; then
        log_warning "NVIDIA Docker runtime not detected. GPU acceleration may not work."
        log_info "Install with: sudo apt-get install -y nvidia-container-toolkit"
    fi
    
    log_success "Prerequisites check completed"
}

# Quick environment setup
setup_environment() {
    log_info "Setting up environment..."
    
    cd "$PROJECT_ROOT"
    
    # Check if .env exists
    if [[ ! -f .env ]]; then
        log_error ".env file not found. Please ensure you're in the ACGS project directory."
        exit 1
    fi
    
    # Check HuggingFace token
    if ! grep -q "HUGGINGFACE_API_KEY=" .env || grep -q "HUGGINGFACE_API_KEY=$" .env; then
        log_warning "HuggingFace API key not set in .env file"
        read -p "Enter your HuggingFace API token: " -r HF_TOKEN
        if [[ -n "$HF_TOKEN" ]]; then
            sed -i "s/HUGGINGFACE_API_KEY=.*/HUGGINGFACE_API_KEY=$HF_TOKEN/" .env
            log_success "HuggingFace token updated"
        else
            log_error "HuggingFace token is required"
            exit 1
        fi
    fi
    
    # Create required directories
    mkdir -p logs config/kimi
    mkdir -p "${HOME}/.cache/huggingface"
    
    log_success "Environment setup completed"
}

# Quick deployment
deploy_service() {
    log_info "Deploying Kimi-Dev-72B service..."
    
    cd "$PROJECT_ROOT"
    
    # Create network if it doesn't exist
    if ! docker network ls | grep -q acgs_network; then
        docker network create acgs_network
        log_info "Created acgs_network"
    fi
    
    # Pull images
    log_info "Pulling Docker images (this may take a while)..."
    docker pull vllm/vllm-openai:latest
    docker pull prom/node-exporter:latest
    
    # Deploy service
    log_info "Starting Kimi service..."
    docker-compose -f infrastructure/docker/docker-compose.kimi.yml --env-file .env up -d
    
    log_success "Service deployment initiated"
}

# Wait for service to be ready
wait_for_service() {
    log_info "Waiting for Kimi service to be ready (this may take 5-10 minutes for first startup)..."
    
    local max_attempts=60  # 10 minutes
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -sf http://localhost:8007/health > /dev/null 2>&1; then
            log_success "Kimi service is ready!"
            return 0
        fi
        
        # Show progress
        local dots=$(printf "%*s" $((attempt % 4)) "" | tr ' ' '.')
        printf "\r${BLUE}[INFO]${NC} Waiting for service$dots (attempt $attempt/$max_attempts)"
        
        sleep 10
        ((attempt++))
    done
    
    echo  # New line after progress indicator
    log_error "Service failed to become ready within timeout"
    log_info "Check logs with: docker logs acgs_kimi_service"
    return 1
}

# Quick test
test_service() {
    log_info "Testing service..."
    
    # Test health endpoint
    if curl -sf http://localhost:8007/health > /dev/null; then
        log_success "✓ Health check passed"
    else
        log_error "✗ Health check failed"
        return 1
    fi
    
    # Test API endpoint
    if curl -sf http://localhost:8007/v1/models > /dev/null; then
        log_success "✓ API endpoint responding"
    else
        log_error "✗ API endpoint not responding"
        return 1
    fi
    
    # Test simple completion
    log_info "Testing chat completion..."
    local response
    response=$(curl -s -X POST "http://localhost:8007/v1/chat/completions" \
        -H "Content-Type: application/json" \
        --data '{
            "model": "kimi-dev-72b",
            "messages": [{"role": "user", "content": "Say hello"}],
            "max_tokens": 10
        }' 2>/dev/null)
    
    if echo "$response" | jq -e '.choices[0].message.content' > /dev/null 2>&1; then
        local content=$(echo "$response" | jq -r '.choices[0].message.content')
        log_success "✓ Chat completion test passed"
        log_info "Response: $content"
    else
        log_warning "⚠ Chat completion test failed, but service is running"
        log_info "You may need to wait longer for the model to fully load"
    fi
}

# Show usage information
show_usage_info() {
    log_success "Kimi-Dev-72B deployment completed!"
    echo
    echo -e "${GREEN}Service Information:${NC}"
    echo "  • Service URL: http://localhost:8007"
    echo "  • API Documentation: http://localhost:8007/docs"
    echo "  • Health Check: http://localhost:8007/health"
    echo "  • Metrics: http://localhost:9007/metrics"
    echo
    echo -e "${GREEN}Management Commands:${NC}"
    echo "  • Check status: ./scripts/manage_kimi_service.sh status"
    echo "  • View logs: ./scripts/manage_kimi_service.sh logs"
    echo "  • Run tests: ./scripts/manage_kimi_service.sh test"
    echo "  • Stop service: ./scripts/manage_kimi_service.sh stop"
    echo
    echo -e "${GREEN}Example API Call:${NC}"
    cat << 'EOF'
curl -X POST "http://localhost:8007/v1/chat/completions" \
  -H "Content-Type: application/json" \
  --data '{
    "model": "kimi-dev-72b",
    "messages": [{"role": "user", "content": "Hello, how are you?"}],
    "max_tokens": 50
  }'
EOF
    echo
    echo -e "${BLUE}For detailed documentation, see: docs/KIMI_DEPLOYMENT_GUIDE.md${NC}"
}

# Main execution
main() {
    log_info "Starting Kimi-Dev-72B quick deployment..."
    
    check_prerequisites
    setup_environment
    deploy_service
    
    if wait_for_service; then
        test_service
        show_usage_info
    else
        log_error "Deployment failed. Check logs for details:"
        echo "  docker logs acgs_kimi_service"
        echo "  docker logs acgs_kimi_monitor"
        exit 1
    fi
}

# Handle interruption
trap 'echo -e "\n${YELLOW}Deployment interrupted${NC}"; exit 1' INT TERM

# Run main function
main "$@"
