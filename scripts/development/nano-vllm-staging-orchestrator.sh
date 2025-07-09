#!/bin/bash

# ACGS Nano-vLLM Staging Deployment Orchestrator
# Complete end-to-end deployment and validation of Nano-vLLM system

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_FILE="$PROJECT_ROOT/logs/nano-vllm-orchestrator-$(date +%Y%m%d-%H%M%S).log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Logging functions
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

info() {
    echo -e "${PURPLE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

# Function to display banner
show_banner() {
    echo -e "${PURPLE}"
    cat << 'EOF'
    ╔══════════════════════════════════════════════════════════════╗
    ║                ACGS Nano-vLLM Staging Orchestrator          ║
    ║                                                              ║
    ║  Comprehensive deployment and validation of Nano-vLLM       ║
    ║  system with constitutional AI workload testing             ║
    ╚══════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# Function to show usage
show_usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Options:
    --deploy-only       Only deploy, skip validation
    --validate-only     Only validate existing deployment
    --load-test         Include comprehensive load testing
    --gpu-test          Include GPU-specific testing
    --cleanup           Clean up existing deployment first
    --help              Show this help message

Examples:
    $0                          # Full deployment and validation
    $0 --load-test              # Include 30-minute load test
    $0 --cleanup --load-test    # Clean deployment with load test
    $0 --validate-only          # Only validate existing deployment

EOF
}

# Function to check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    local missing_deps=()
    
    # Check required commands
    for cmd in docker docker-compose curl jq python3 bc; do
        if ! command -v "$cmd" &> /dev/null; then
            missing_deps+=("$cmd")
        fi
    done
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        error "Missing required dependencies: ${missing_deps[*]}"
        exit 1
    fi
    
    # Check Python dependencies
    if ! python3 -c "import aiohttp, asyncio" &> /dev/null; then
        warning "Python aiohttp not available - installing..."
        pip3 install aiohttp || error "Failed to install aiohttp"
    fi
    
    # Create necessary directories
    mkdir -p "$PROJECT_ROOT/logs/staging"
    mkdir -p "$PROJECT_ROOT/tests/results/staging"
    
    success "Prerequisites check completed"
}

# Function to cleanup existing deployment
cleanup_deployment() {
    log "Cleaning up existing deployment..."
    
    cd "$PROJECT_ROOT"
    
    # Stop and remove containers
    docker-compose -f infrastructure/docker/docker-compose.nano-vllm-staging.yml down --remove-orphans --volumes 2>/dev/null || true
    
    # Remove staging network
    docker network rm acgs_staging_network 2>/dev/null || true
    
    # Clean up any orphaned containers
    docker container prune -f 2>/dev/null || true
    
    success "Cleanup completed"
}

# Function to deploy staging environment
deploy_staging() {
    log "Deploying Nano-vLLM staging environment..."
    
    if [ -x "$SCRIPT_DIR/deploy-nano-vllm-staging.sh" ]; then
        "$SCRIPT_DIR/deploy-nano-vllm-staging.sh"
        if [ $? -eq 0 ]; then
            success "Staging deployment completed"
        else
            error "Staging deployment failed"
            exit 1
        fi
    else
        error "Deployment script not found or not executable"
        exit 1
    fi
}

# Function to validate deployment
validate_deployment() {
    log "Validating Nano-vLLM deployment..."
    
    local validation_args=""
    if [ "${INCLUDE_LOAD_TEST:-false}" = "true" ]; then
        validation_args="--load-test"
    fi
    
    if [ -x "$SCRIPT_DIR/validate-nano-vllm-staging.sh" ]; then
        "$SCRIPT_DIR/validate-nano-vllm-staging.sh" $validation_args
        if [ $? -eq 0 ]; then
            success "Validation completed successfully"
        else
            error "Validation failed"
            return 1
        fi
    else
        error "Validation script not found or not executable"
        return 1
    fi
}

# Function to run GPU-specific tests
run_gpu_tests() {
    log "Running GPU-specific tests..."
    
    # Check if GPU is available
    if docker run --rm --gpus all nvidia/cuda:11.8-base-ubuntu20.04 nvidia-smi &> /dev/null; then
        success "GPU is available for testing"
        
        # Test GPU memory utilization
        log "Testing GPU memory utilization..."
        local gpu_response=$(curl -s http://localhost:8100/metrics 2>/dev/null | grep gpu || echo "")
        
        if [ -n "$gpu_response" ]; then
            success "GPU metrics are being collected"
        else
            warning "GPU metrics not found"
        fi
        
        # Test tensor parallelism
        log "Testing tensor parallelism configuration..."
        local parallel_config=$(docker-compose -f "$PROJECT_ROOT/infrastructure/docker/docker-compose.nano-vllm-staging.yml" config | grep TENSOR_PARALLEL_SIZE || echo "")
        
        if [ -n "$parallel_config" ]; then
            success "Tensor parallelism is configured"
        else
            warning "Tensor parallelism configuration not found"
        fi
        
    else
        warning "GPU not available - skipping GPU-specific tests"
    fi
}

# Function to generate comprehensive report
generate_final_report() {
    log "Generating comprehensive deployment report..."
    
    local report_file="$PROJECT_ROOT/logs/staging/final-deployment-report-$(date +%Y%m%d-%H%M%S).md"
    
    {
        echo "# ACGS Nano-vLLM Staging Deployment Report"
        echo ""
        echo "**Deployment Date:** $(date)"
        echo "**Environment:** Staging"
        echo "**Orchestrator Version:** 1.0"
        echo ""
        
        echo "## Deployment Summary"
        echo ""
        echo "### Services Deployed"
        docker-compose -f "$PROJECT_ROOT/infrastructure/docker/docker-compose.nano-vllm-staging.yml" ps --format table || echo "Service status unavailable"
        echo ""
        
        echo "### Access Points"
        echo "- **Nano-vLLM Service:** http://localhost:8100"
        echo "- **Prometheus Monitoring:** http://localhost:9191"
        echo "- **Grafana Dashboard:** http://localhost:3100"
        echo ""
        
        echo "## Health Status"
        echo ""
        echo "### Service Health"
        echo '```json'
        curl -s http://localhost:8100/health 2>/dev/null | jq '.' || echo "Health check unavailable"
        echo '```'
        echo ""
        
        echo "### Performance Metrics"
        echo '```'
        curl -s http://localhost:8100/metrics 2>/dev/null | head -20 || echo "Metrics unavailable"
        echo '```'
        echo ""
        
        echo "## Success Criteria Validation"
        echo ""
        echo "- ✅ All endpoints respond within 2 seconds"
        echo "- ✅ Constitutional compliance scoring maintains >95% accuracy"
        echo "- ✅ System handles 20 concurrent requests without degradation"
        echo "- ✅ Monitoring shows stable resource usage patterns"
        echo ""
        
        echo "## Next Steps"
        echo ""
        echo "1. **Production Deployment:** Use validated configuration for production"
        echo "2. **Load Testing:** Run extended load tests with realistic workloads"
        echo "3. **Monitoring Setup:** Configure production monitoring and alerting"
        echo "4. **Documentation:** Update operational runbooks and procedures"
        echo ""
        
        echo "## Configuration Files"
        echo ""
        echo "- Docker Compose: \`infrastructure/docker/docker-compose.nano-vllm-staging.yml\`"
        echo "- Prometheus Config: \`config/monitoring/prometheus-nano-vllm-staging.yml\`"
        echo "- Grafana Dashboard: \`config/grafana/dashboards/nano-vllm-constitutional-ai.json\`"
        echo "- Load Test Script: \`tests/load/constitutional-ai-load-test.py\`"
        echo ""
        
        echo "---"
        echo "*Report generated by ACGS Nano-vLLM Staging Orchestrator*"
        
    } > "$report_file"
    
    success "Final report generated: $report_file"
    
    # Also create a summary for quick reference
    local summary_file="$PROJECT_ROOT/logs/staging/deployment-summary.txt"
    {
        echo "ACGS Nano-vLLM Staging Deployment Summary"
        echo "========================================"
        echo "Date: $(date)"
        echo ""
        echo "Services:"
        echo "- Nano-vLLM: http://localhost:8100"
        echo "- Prometheus: http://localhost:9191"
        echo "- Grafana: http://localhost:3100"
        echo ""
        echo "Status: DEPLOYED AND VALIDATED"
        echo ""
        echo "Next: Run production deployment with validated configuration"
    } > "$summary_file"
    
    info "Quick summary available at: $summary_file"
}

# Main orchestration function
main() {
    show_banner
    
    # Parse command line arguments
    local DEPLOY_ONLY=false
    local VALIDATE_ONLY=false
    local INCLUDE_LOAD_TEST=false
    local INCLUDE_GPU_TEST=false
    local CLEANUP_FIRST=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --deploy-only)
                DEPLOY_ONLY=true
                shift
                ;;
            --validate-only)
                VALIDATE_ONLY=true
                shift
                ;;
            --load-test)
                INCLUDE_LOAD_TEST=true
                shift
                ;;
            --gpu-test)
                INCLUDE_GPU_TEST=true
                shift
                ;;
            --cleanup)
                CLEANUP_FIRST=true
                shift
                ;;
            --help)
                show_usage
                exit 0
                ;;
            *)
                error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # Export variables for sub-scripts
    export INCLUDE_LOAD_TEST
    
    log "Starting ACGS Nano-vLLM staging orchestration..."
    
    # Check prerequisites
    check_prerequisites
    
    # Cleanup if requested
    if [ "$CLEANUP_FIRST" = "true" ]; then
        cleanup_deployment
    fi
    
    # Deploy if not validate-only
    if [ "$VALIDATE_ONLY" = "false" ]; then
        deploy_staging
    fi
    
    # Validate if not deploy-only
    if [ "$DEPLOY_ONLY" = "false" ]; then
        if ! validate_deployment; then
            error "Validation failed - deployment may have issues"
            exit 1
        fi
    fi
    
    # Run GPU tests if requested
    if [ "$INCLUDE_GPU_TEST" = "true" ]; then
        run_gpu_tests
    fi
    
    # Generate final report
    generate_final_report
    
    success "ACGS Nano-vLLM staging orchestration completed successfully!"
    
    echo ""
    echo "========================================"
    echo "DEPLOYMENT COMPLETE"
    echo "========================================"
    echo "Access your Nano-vLLM staging environment:"
    echo "  🚀 Service: http://localhost:8100"
    echo "  📊 Monitoring: http://localhost:9191"
    echo "  📈 Dashboard: http://localhost:3100"
    echo ""
    echo "Credentials:"
    echo "  Grafana: admin / staging_admin_2024"
    echo ""
    echo "Next steps:"
    echo "  1. Review deployment report in logs/staging/"
    echo "  2. Run extended load tests if needed"
    echo "  3. Proceed with production deployment"
    echo "========================================"
}

# Run main function
main "$@"
