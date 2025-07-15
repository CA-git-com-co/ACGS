# Constitutional Hash: cdd01ef066bc6cf2
# ACGS-2 Constitutional Compliance Validation
#!/bin/bash

# ACGS Nano-vLLM Staging Deployment Script
# Deploy and validate Nano-vLLM system in staging environment

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
STAGING_COMPOSE_FILE="$PROJECT_ROOT/infrastructure/docker/docker-compose.nano-vllm-staging.yml"
LOG_FILE="$PROJECT_ROOT/logs/nano-vllm-staging-deployment.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

# Function to check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
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
    
    # Check for NVIDIA Docker runtime (optional)
    if docker info 2>/dev/null | grep -q nvidia; then
        success "NVIDIA Docker runtime detected"
    else
        warning "NVIDIA Docker runtime not detected - GPU support will be limited"
    fi
    
    # Create necessary directories
    mkdir -p "$PROJECT_ROOT/logs/staging"
    mkdir -p "$PROJECT_ROOT/tests/results/staging"
    
    success "Prerequisites check completed"
}

# Function to build Docker images
build_images() {
    log "Building Nano-vLLM Docker images..."
    
    cd "$PROJECT_ROOT"
    
    # Build the Nano-vLLM image
    docker-compose -f "$STAGING_COMPOSE_FILE" build nano-vllm-reasoning-staging
    
    if [ $? -eq 0 ]; then
        success "Docker images built successfully"
    else
        error "Failed to build Docker images"
        exit 1
    fi
}

# Function to deploy staging environment
deploy_staging() {
    log "Deploying Nano-vLLM staging environment..."
    
    cd "$PROJECT_ROOT"
    
    # Stop any existing staging services
    docker-compose -f "$STAGING_COMPOSE_FILE" down --remove-orphans || true
    
    # Create network if it doesn't exist
    docker network create acgs_staging_network 2>/dev/null || true
    
    # Start core services
    log "Starting Nano-vLLM reasoning service..."
    docker-compose -f "$STAGING_COMPOSE_FILE" up -d nano-vllm-reasoning-staging
    
    # Wait for service to be ready
    log "Waiting for Nano-vLLM service to be ready..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:8100/health > /dev/null 2>&1; then
            success "Nano-vLLM service is ready"
            break
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            error "Nano-vLLM service failed to start within timeout"
            docker-compose -f "$STAGING_COMPOSE_FILE" logs nano-vllm-reasoning-staging
            exit 1
        fi
        
        log "Waiting for service... (attempt $attempt/$max_attempts)"
        sleep 10
        ((attempt++))
    done
    
    # Start monitoring services
    log "Starting monitoring services..."
    docker-compose -f "$STAGING_COMPOSE_FILE" up -d prometheus-staging grafana-staging
    
    # Wait for monitoring to be ready
    sleep 30
    
    success "Staging environment deployed successfully"
}

# Function to validate constitutional reasoning endpoints
validate_endpoints() {
    log "Validating constitutional reasoning endpoints..."
    
    local base_url="http://localhost:8100"
    
    # Test health endpoint
    log "Testing health endpoint..."
    if curl -f "$base_url/health" > /dev/null 2>&1; then
        success "Health endpoint is responding"
    else
        error "Health endpoint is not responding"
        return 1
    fi
    
    # Test chat completions endpoint
    log "Testing chat completions endpoint..."
    local chat_response=$(curl -s -X POST "$base_url/v1/chat/completions" \
        -H "Content-Type: application/json" \
        -d '{
            "model": "nvidia/Llama-3.1-Nemotron-70B-Instruct-HF",
            "messages": [{"role": "user", "content": "Hello, test message"}],
            "max_tokens": 50
        }')
    
    if echo "$chat_response" | jq -e '.choices[0].message.content' > /dev/null 2>&1; then
        success "Chat completions endpoint is working"
    else
        error "Chat completions endpoint failed"
        echo "Response: $chat_response"
        return 1
    fi
    
    # Test constitutional reasoning endpoint
    log "Testing constitutional reasoning endpoint..."
    local constitutional_response=$(curl -s -X POST "$base_url/v1/constitutional-reasoning" \
        -H "Content-Type: application/json" \
        -d '{
            "content": "Should we implement a policy that restricts user access?",
            "domain": "governance",
            "reasoning_depth": "standard"
        }')
    
    if echo "$constitutional_response" | jq -e '.constitutional_compliance' > /dev/null 2>&1; then
        success "Constitutional reasoning endpoint is working"
        local compliance_score=$(echo "$constitutional_response" | jq -r '.constitutional_compliance')
        log "Constitutional compliance score: $compliance_score"
    else
        error "Constitutional reasoning endpoint failed"
        echo "Response: $constitutional_response"
        return 1
    fi
    
    success "All endpoints validated successfully"
}

# Function to test fallback mechanisms
test_fallback() {
    log "Testing fallback mechanisms..."
    
    # This would involve stopping the primary service and ensuring fallback works
    # For now, we'll just verify the configuration
    
    local config_check=$(docker-compose -f "$STAGING_COMPOSE_FILE" config | grep -c "FALLBACK_TO_VLLM=true")
    if [ "$config_check" -gt 0 ]; then
        success "Fallback configuration is enabled"
    else
        warning "Fallback configuration not found"
    fi
}

# Function to check monitoring
check_monitoring() {
    log "Checking monitoring infrastructure..."
    
    # Check Prometheus
    if curl -f http://localhost:9191/api/v1/status/config > /dev/null 2>&1; then
        success "Prometheus is accessible"
    else
        error "Prometheus is not accessible"
        return 1
    fi
    
    # Check Grafana
    if curl -f http://localhost:3100/api/health > /dev/null 2>&1; then
        success "Grafana is accessible"
    else
        error "Grafana is not accessible"
        return 1
    fi
    
    # Check if metrics are being collected
    local metrics_check=$(curl -s http://localhost:9191/api/v1/query?query=up | jq -r '.data.result | length')
    if [ "$metrics_check" -gt 0 ]; then
        success "Metrics are being collected"
    else
        warning "No metrics found"
    fi
}

# Function to run basic load test
run_basic_load_test() {
    log "Running basic load test..."
    
    # Simple concurrent request test
    local concurrent_requests=5
    local test_duration=60  # seconds
    
    log "Starting $concurrent_requests concurrent requests for $test_duration seconds..."
    
    for i in $(seq 1 $concurrent_requests); do
        (
            local end_time=$(($(date +%s) + test_duration))
            local request_count=0
            
            while [ $(date +%s) -lt $end_time ]; do
                curl -s -X POST http://localhost:8100/v1/chat/completions \
                    -H "Content-Type: application/json" \
                    -d '{
                        "model": "nvidia/Llama-3.1-Nemotron-70B-Instruct-HF",
                        "messages": [{"role": "user", "content": "Test message '$i'-'$request_count'"}],
                        "max_tokens": 20
                    }' > /dev/null
                ((request_count++))
                sleep 1
            done
            
            log "Worker $i completed $request_count requests"
        ) &
    done
    
    wait
    success "Basic load test completed"
}

# Function to generate deployment report
generate_report() {
    log "Generating deployment report..."
    
    local report_file="$PROJECT_ROOT/logs/staging/deployment-report-$(date +%Y%m%d-%H%M%S).txt"
    
    {
        echo "ACGS Nano-vLLM Staging Deployment Report"
        echo "========================================"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
        echo "Deployment Date: $(date)"
        echo "Environment: Staging"
        echo ""
        
        echo "Service Status:"
        docker-compose -f "$STAGING_COMPOSE_FILE" ps
        echo ""
        
        echo "Health Check Results:"
        curl -s http://localhost:8100/health | jq '.' || echo "Health check failed"
        echo ""
        
        echo "Metrics Summary:"
        curl -s http://localhost:8100/metrics 2>/dev/null | head -20 || echo "Metrics not available"
        echo ""
        
        echo "Resource Usage:"
        docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" || echo "Stats not available"
        
    } > "$report_file"
    
    success "Deployment report generated: $report_file"
}

# Main deployment function
main() {
    log "Starting ACGS Nano-vLLM staging deployment..."
    
    check_prerequisites
    build_images
    deploy_staging
    validate_endpoints
    test_fallback
    check_monitoring
    run_basic_load_test
    generate_report
    
    success "Staging deployment completed successfully!"
    log "Access points:"
    log "  - Nano-vLLM Service: http://localhost:8100"
    log "  - Prometheus: http://localhost:9191"
    log "  - Grafana: http://localhost:3100 (admin/staging_admin_2024)"
    log ""
    log "Next steps:"
    log "  1. Run comprehensive load tests"
    log "  2. Validate constitutional compliance scoring"
    log "  3. Monitor performance metrics"
    log "  4. Test GPU acceleration (if available)"
}

# Run main function
main "$@"
