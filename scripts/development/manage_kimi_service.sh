# Constitutional Hash: cdd01ef066bc6cf2
# ACGS-2 Constitutional Compliance Validation
#!/bin/bash

# ACGS Kimi-Dev-72B Service Management Script
# Comprehensive service lifecycle management with monitoring and troubleshooting

set -euo pipefail

# =============================================================================  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
# Configuration
# =============================================================================  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
COMPOSE_FILE="$PROJECT_ROOT/infrastructure/docker/docker-compose.kimi.yml"
ENV_FILE="$PROJECT_ROOT/config/environments/development.env"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# =============================================================================  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
# Utility Functions
# =============================================================================  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

show_usage() {
    cat << EOF
ACGS Kimi-Dev-72B Service Management

Usage: $0 <command> [options]

Commands:
    start           Start the Kimi service
    stop            Stop the Kimi service
    restart         Restart the Kimi service
    status          Show service status
    logs            Show service logs
    health          Check service health
    test            Run API tests
    monitor         Show real-time monitoring
    cleanup         Clean up resources
    backup          Backup model cache
    restore         Restore model cache

Options:
    -f, --follow    Follow logs (for logs command)
    -t, --tail N    Show last N lines of logs
    -h, --help      Show this help message

Examples:
    $0 start
    $0 logs --follow
    $0 test
    $0 monitor
EOF
}

# =============================================================================  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
# Service Management Functions
# =============================================================================  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
start_service() {
    log_info "Starting Kimi service..."
    
    cd "$PROJECT_ROOT"
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d
    
    log_success "Kimi service started"
    
    # Wait for service to be ready
    log_info "Waiting for service to be ready..."
    local attempts=0
    local max_attempts=30
    
    while [[ $attempts -lt $max_attempts ]]; do
        if curl -sf http://localhost:8007/health > /dev/null 2>&1; then
            log_success "Service is ready!"
            return 0
        fi
        sleep 10
        ((attempts++))
        log_info "Waiting... ($attempts/$max_attempts)"
    done
    
    log_warning "Service may not be fully ready yet. Check logs for details."
}

stop_service() {
    log_info "Stopping Kimi service..."
    
    cd "$PROJECT_ROOT"
    docker-compose -f "$COMPOSE_FILE" down
    
    log_success "Kimi service stopped"
}

restart_service() {
    log_info "Restarting Kimi service..."
    stop_service
    sleep 5
    start_service
}

show_status() {
    log_info "Kimi service status:"
    
    cd "$PROJECT_ROOT"
    docker-compose -f "$COMPOSE_FILE" ps
    
    echo
    log_info "Container resource usage:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" \
        acgs_kimi_service acgs_kimi_monitor 2>/dev/null || log_warning "Containers not running"
    
    echo
    log_info "GPU usage:"
    if command -v nvidia-smi &> /dev/null; then
        nvidia-smi --query-gpu=index,name,utilization.gpu,memory.used,memory.total --format=csv,noheader
    else
        log_warning "nvidia-smi not available"
    fi
}

show_logs() {
    local follow_flag=""
    local tail_lines=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -f|--follow)
                follow_flag="--follow"
                shift
                ;;
            -t|--tail)
                tail_lines="--tail $2"
                shift 2
                ;;
            *)
                shift
                ;;
        esac
    done
    
    cd "$PROJECT_ROOT"
    docker-compose -f "$COMPOSE_FILE" logs $follow_flag $tail_lines kimi_service
}

check_health() {
    log_info "Checking Kimi service health..."
    
    # Basic connectivity
    if curl -sf http://localhost:8007/health > /dev/null; then
        log_success "✓ Health endpoint responding"
    else
        log_error "✗ Health endpoint not responding"
        return 1
    fi
    
    # API availability
    if curl -sf http://localhost:8007/v1/models > /dev/null; then
        log_success "✓ API endpoint responding"
    else
        log_error "✗ API endpoint not responding"
        return 1
    fi
    
    # Model availability
    local models_response
    models_response=$(curl -s http://localhost:8007/v1/models)
    if echo "$models_response" | jq -e '.data[] | select(.id == "kimi-dev-72b")' > /dev/null 2>&1; then
        log_success "✓ Kimi-Dev-72B model available"
    else
        log_error "✗ Kimi-Dev-72B model not available"
        return 1
    fi
    
    # Container health
    local container_health
    container_health=$(docker inspect acgs_kimi_service --format='{{.State.Health.Status}}' 2>/dev/null || echo "unknown")
    case "$container_health" in
        "healthy")
            log_success "✓ Container health: healthy"
            ;;
        "unhealthy")
            log_error "✗ Container health: unhealthy"
            return 1
            ;;
        "starting")
            log_warning "⚠ Container health: starting"
            ;;
        *)
            log_warning "⚠ Container health: $container_health"
            ;;
    esac
    
    log_success "All health checks passed!"
}

run_tests() {
    log_info "Running API tests..."
    
    # Test 1: Simple completion
    log_info "Test 1: Simple completion"
    local response1
    response1=$(curl -s -X POST "http://localhost:8007/v1/chat/completions" \
        -H "Content-Type: application/json" \
        --data '{
            "model": "kimi-dev-72b",
            "messages": [{"role": "user", "content": "What is 2+2?"}],
            "max_tokens": 50
        }')
    
    if echo "$response1" | jq -e '.choices[0].message.content' > /dev/null 2>&1; then
        log_success "✓ Simple completion test passed"
        echo "Response: $(echo "$response1" | jq -r '.choices[0].message.content')"
    else
        log_error "✗ Simple completion test failed"
        echo "Response: $response1"
    fi
    
    # Test 2: Streaming completion
    log_info "Test 2: Streaming completion"
    local stream_test
    stream_test=$(curl -s -X POST "http://localhost:8007/v1/chat/completions" \
        -H "Content-Type: application/json" \
        --data '{
            "model": "kimi-dev-72b",
            "messages": [{"role": "user", "content": "Count from 1 to 5"}],
            "max_tokens": 30,
            "stream": true
        }' | head -n 5)
    
    if [[ -n "$stream_test" ]]; then
        log_success "✓ Streaming completion test passed"
    else
        log_error "✗ Streaming completion test failed"
    fi
    
    # Test 3: Performance test
    log_info "Test 3: Performance test (5 concurrent requests)"
    local start_time=$(date +%s)
    
    for i in {1..5}; do
        curl -s -X POST "http://localhost:8007/v1/chat/completions" \
            -H "Content-Type: application/json" \
            --data "{
                \"model\": \"kimi-dev-72b\",
                \"messages\": [{\"role\": \"user\", \"content\": \"Test request $i\"}],
                \"max_tokens\": 10
            }" > /dev/null &
    done
    
    wait
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    log_success "✓ Performance test completed in ${duration}s"
}

monitor_service() {
    log_info "Starting real-time monitoring (Press Ctrl+C to exit)..."
    
    while true; do
        clear
        echo "=== ACGS Kimi Service Monitor ==="
        echo "Timestamp: $(date)"
        echo
        
        # Container status
        echo "Container Status:"
        docker-compose -f "$COMPOSE_FILE" ps 2>/dev/null || echo "Service not running"
        echo
        
        # Resource usage
        echo "Resource Usage:"
        docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" \
            acgs_kimi_service 2>/dev/null || echo "Container not running"
        echo
        
        # GPU usage
        echo "GPU Usage:"
        if command -v nvidia-smi &> /dev/null; then
            nvidia-smi --query-gpu=index,name,utilization.gpu,memory.used,memory.total --format=csv,noheader
        else
            echo "nvidia-smi not available"
        fi
        echo
        
        # API health
        echo "API Health:"
        if curl -sf http://localhost:8007/health > /dev/null 2>&1; then
            echo "✓ Service responding"
        else
            echo "✗ Service not responding"
        fi
        
        sleep 5
    done
}

cleanup_resources() {
    log_info "Cleaning up Kimi service resources..."
    
    # Stop services
    cd "$PROJECT_ROOT"
    docker-compose -f "$COMPOSE_FILE" down -v
    
    # Remove unused images
    docker image prune -f
    
    # Clean up logs
    find "$PROJECT_ROOT/logs" -name "kimi-*.log" -mtime +7 -delete 2>/dev/null || true
    
    # Clean up prometheus metrics
    rm -rf /tmp/prometheus_multiproc_dir/*
    
    log_success "Cleanup completed"
}

# =============================================================================  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
# Main Function
# =============================================================================  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
main() {
    if [[ $# -eq 0 ]]; then
        show_usage
        exit 1
    fi
    
    local command="$1"
    shift
    
    case "$command" in
        start)
            start_service
            ;;
        stop)
            stop_service
            ;;
        restart)
            restart_service
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs "$@"
            ;;
        health)
            check_health
            ;;
        test)
            run_tests
            ;;
        monitor)
            monitor_service
            ;;
        cleanup)
            cleanup_resources
            ;;
        -h|--help)
            show_usage
            ;;
        *)
            log_error "Unknown command: $command"
            show_usage
            exit 1
            ;;
    esac
}

# =============================================================================  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
# Script Execution
# =============================================================================  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
