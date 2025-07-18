# Constitutional Hash: cdd01ef066bc6cf2
#!/bin/bash

# Hunyuan-A13B Management Script for ACGS
# Provides easy management of the Hunyuan model deployment

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DOCKER_COMPOSE_FILE="$PROJECT_ROOT/docker-compose.hunyuan.yml"
CONFIG_FILE="$PROJECT_ROOT/config/models/hunyuan-a13b.yaml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
}

# Check GPU availability
check_gpu() {
    print_status "Checking GPU availability..."
    if ! command -v nvidia-smi &> /dev/null; then
        print_error "nvidia-smi not found. NVIDIA GPU drivers required."
        exit 1
    fi
    
    GPU_COUNT=$(nvidia-smi --query-gpu=count --format=csv,noheader,nounits | head -1)
    GPU_MEMORY=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1)
    
    print_success "Found GPU: ${GPU_COUNT} device(s) with ${GPU_MEMORY}MB memory"
    
    if [ "$GPU_MEMORY" -lt 24000 ]; then
        print_warning "GPU memory is less than 24GB. Performance may be limited."
    fi
}

# Pull Docker images
pull_images() {
    print_status "Pulling Hunyuan Docker images..."
    
    # Try primary image first
    if docker pull hunyuaninfer/hunyuan-a13b:hunyuan-moe-A13B-vllm; then
        print_success "Primary image pulled successfully"
    else
        print_warning "Primary image failed, trying alternative..."
        if docker pull docker.cnb.cool/tencent/hunyuan/hunyuan-a13b:hunyuan-moe-A13B-vllm; then
            print_success "Alternative image pulled successfully"
        else
            print_error "Failed to pull any Hunyuan images"
            exit 1
        fi
    fi
}

# Start services
start_services() {
    local download_source=${1:-"huggingface"}
    
    print_status "Starting Hunyuan services with $download_source source..."
    
    cd "$PROJECT_ROOT"
    
    if [ "$download_source" = "modelscope" ]; then
        docker compose -f "$DOCKER_COMPOSE_FILE" --profile modelscope up -d hunyuan-a13b-modelscope
    else
        docker compose -f "$DOCKER_COMPOSE_FILE" up -d hunyuan-a13b
    fi
    
    print_success "Services started"
}

# Stop services
stop_services() {
    print_status "Stopping Hunyuan services..."
    
    cd "$PROJECT_ROOT"
    docker compose -f "$DOCKER_COMPOSE_FILE" down
    
    print_success "Services stopped"
}

# Check service status
check_status() {
    print_status "Checking service status..."
    
    cd "$PROJECT_ROOT"
    docker compose -f "$DOCKER_COMPOSE_FILE" ps
    
    # Check if API is responding
    echo ""
    print_status "Checking API health..."
    
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        print_success "API is healthy and responding"
    else
        print_warning "API is not responding on port 8000"
    fi
}

# Show logs
show_logs() {
    local lines=${1:-50}
    
    print_status "Showing last $lines lines of logs..."
    
    cd "$PROJECT_ROOT"
    docker compose -f "$DOCKER_COMPOSE_FILE" logs --tail="$lines" hunyuan-a13b
}

# Test model inference
test_inference() {
    print_status "Testing model inference..."
    
    local test_response=$(curl -s -X POST http://localhost:8000/v1/chat/completions \
        -H "Content-Type: application/json" \
        -d '{
            "model": "tencent/Hunyuan-A13B-Instruct",
            "messages": [{"role": "user", "content": "Hello! Can you respond in both English and Chinese?"}],
            "max_tokens": 100,
            "temperature": 0.7
        }' | jq -r '.choices[0].message.content' 2>/dev/null)
    
    if [ $? -eq 0 ] && [ -n "$test_response" ]; then
        print_success "Model inference test passed"
        echo "Response: $test_response"
    else
        print_error "Model inference test failed"
        exit 1
    fi
}

# Monitor system resources
monitor_resources() {
    print_status "Monitoring system resources..."
    
    echo "=== GPU Usage ==="
    nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu --format=csv,noheader,nounits
    
    echo ""
    echo "=== Container Resources ==="
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" | grep hunyuan || echo "No Hunyuan containers running"
    
    echo ""
    echo "=== API Metrics ==="
    curl -s http://localhost:8000/metrics 2>/dev/null | head -20 || echo "Metrics not available"
}

# Clean up resources
cleanup() {
    print_status "Cleaning up Hunyuan resources..."
    
    cd "$PROJECT_ROOT"
    
    # Stop containers
    docker compose -f "$DOCKER_COMPOSE_FILE" down -v
    
    # Remove unused images (optional)
    read -p "Remove unused Docker images? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker image prune -f
        print_success "Unused images removed"
    fi
    
    print_success "Cleanup completed"
}

# Show usage
show_usage() {
    echo "Hunyuan-A13B Management Script for ACGS"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  start [source]     Start Hunyuan services (source: huggingface|modelscope)"
    echo "  stop               Stop all Hunyuan services"
    echo "  restart [source]   Restart services"
    echo "  status             Show service status"
    echo "  logs [lines]       Show service logs (default: 50 lines)"
    echo "  test               Test model inference"
    echo "  monitor            Monitor system resources"
    echo "  pull               Pull Docker images"
    echo "  cleanup            Clean up resources"
    echo "  health             Quick health check"
    echo "  help               Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start                    # Start with HuggingFace download"
    echo "  $0 start modelscope         # Start with ModelScope download"
    echo "  $0 logs 100                 # Show last 100 log lines"
    echo "  $0 test                     # Test model inference"
}

# Quick health check
health_check() {
    print_status "Running quick health check..."
    
    # Check Docker
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running"
        return 1
    fi
    
    # Check GPU
    if ! nvidia-smi >/dev/null 2>&1; then
        print_error "GPU not available"
        return 1
    fi
    
    # Check API
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        print_success "All systems healthy"
    else
        print_warning "API not responding"
        return 1
    fi
}

# Main execution
main() {
    case "${1:-help}" in
        "start")
            check_docker
            check_gpu
            start_services "${2:-huggingface}"
            ;;
        "stop")
            check_docker
            stop_services
            ;;
        "restart")
            check_docker
            stop_services
            sleep 2
            start_services "${2:-huggingface}"
            ;;
        "status")
            check_docker
            check_status
            ;;
        "logs")
            check_docker
            show_logs "${2:-50}"
            ;;
        "test")
            test_inference
            ;;
        "monitor")
            monitor_resources
            ;;
        "pull")
            check_docker
            pull_images
            ;;
        "cleanup")
            check_docker
            cleanup
            ;;
        "health")
            health_check
            ;;
        "help"|"--help"|"-h"|"")
            show_usage
            ;;
        *)
            print_error "Unknown command: $1"
            echo ""
            show_usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"