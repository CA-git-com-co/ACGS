#!/bin/bash
# 5-Tier Hybrid Inference Router Deployment and Testing Script
# Constitutional Hash: cdd01ef066bc6cf2

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"

# Logging function
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "🔍 Checking prerequisites..."
    
    # Check required tools
    local required_tools=("docker" "docker-compose" "python3" "pip")
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            log_error "Required tool not found: $tool"
            exit 1
        fi
    done
    
    # Check Python packages
    if ! python3 -c "import locust, aiohttp, redis" &> /dev/null; then
        log_warning "Installing required Python packages..."
        pip install locust aiohttp redis pyyaml
    fi
    
    # Check environment variables
    local required_env_vars=("OPENROUTER_API_KEY" "GROQ_API_KEY" "POSTGRES_PASSWORD")
    for var in "${required_env_vars[@]}"; do
        if [[ -z "${!var}" ]]; then
            log_error "Required environment variable not set: $var"
            echo "Please set the following environment variables:"
            echo "export OPENROUTER_API_KEY='your_openrouter_api_key'"
            echo "export GROQ_API_KEY='your_groq_api_key'"
            echo "export POSTGRES_PASSWORD='your_postgres_password'"
            exit 1
        fi
    done
    
    log_success "Prerequisites check completed"
}

# Setup environment
setup_environment() {
    log_info "🏗️ Setting up environment..."
    
    # Create necessary directories
    mkdir -p logs reports results
    
    # Set up Python path
    export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"
    
    # Create Docker network if it doesn't exist
    if ! docker network ls | grep -q "acgs-staging"; then
        docker network create acgs-staging
        log_info "Created Docker network: acgs-staging"
    fi
    
    log_success "Environment setup completed"
}

# Run deployment and testing
run_deployment_and_testing() {
    log_info "🚀 Starting 5-Tier Router Deployment and Testing..."
    log_info "🔒 Constitutional Hash: $CONSTITUTIONAL_HASH"
    
    # Change to project root
    cd "$PROJECT_ROOT"
    
    # Run the deployment and testing orchestrator
    python3 scripts/deployment/deploy_and_scripts/testing/test_5_tier_router.py 2>&1 | tee logs/deployment_test_$(date +%Y%m%d_%H%M%S).log
    
    local exit_code=${PIPESTATUS[0]}
    
    if [[ $exit_code -eq 0 ]]; then
        log_success "Deployment and testing completed successfully!"
        
        # Display results summary
        echo ""
        echo "📊 DEPLOYMENT AND TESTING SUMMARY"
        echo "=================================="
        echo "🔒 Constitutional Hash: $CONSTITUTIONAL_HASH"
        echo "📅 Completed: $(date)"
        echo ""
        
        # Check for generated reports
        if [[ -f "load_test_report.html" ]]; then
            echo "📈 Load Test Report: load_test_report.html"
        fi
        
        if [[ -f "reports/stress_test_report.html" ]]; then
            echo "💪 Stress Test Report: reports/stress_test_report.html"
        fi
        
        # Find the latest deployment report
        local latest_report=$(ls -t deployment_test_report_*.json 2>/dev/null | head -1)
        if [[ -n "$latest_report" ]]; then
            echo "📄 Deployment Report: $latest_report"
            
            # Extract key metrics from report
            if command -v jq &> /dev/null; then
                echo ""
                echo "🎯 KEY METRICS:"
                echo "Status: $(jq -r '.deployment_summary.status' "$latest_report")"
                echo "Duration: $(jq -r '.deployment_summary.duration_seconds' "$latest_report")s"
                echo "Constitutional Hash: $(jq -r '.deployment_summary.constitutional_hash' "$latest_report")"
            fi
        fi
        
        echo ""
        echo "🔗 ENDPOINTS:"
        echo "Hybrid Router: http://localhost:8020"
        echo "Health Check: http://localhost:8020/health"
        echo "Models List: http://localhost:8020/models"
        echo ""
        
    else
        log_error "Deployment and testing failed with exit code: $exit_code"
        echo ""
        echo "🔍 TROUBLESHOOTING:"
        echo "1. Check the log file in logs/ directory"
        echo "2. Verify all environment variables are set"
        echo "3. Ensure Docker is running and accessible"
        echo "4. Check network connectivity for API endpoints"
        echo ""
        exit $exit_code
    fi
}

# Cleanup function
cleanup() {
    log_info "🧹 Cleaning up resources..."
    
    # Stop any running containers
    docker-compose -f docker-compose.router.staging.yml down 2>/dev/null || true
    docker-compose -f infrastructure/docker/docker-compose.staging.yml down 2>/dev/null || true
    
    # Remove temporary files
    rm -f config/environments/development.env.staging docker-compose.router.staging.yml
    
    log_success "Cleanup completed"
}

# Trap for cleanup on exit
trap cleanup EXIT

# Main execution
main() {
    echo "🚀 5-Tier Hybrid Inference Router Deployment and Testing"
    echo "========================================================"
    echo "🔒 Constitutional Hash: $CONSTITUTIONAL_HASH"
    echo ""
    
    check_prerequisites
    setup_environment
    run_deployment_and_testing
    
    log_success "🎉 All operations completed successfully!"
}

# Help function
show_help() {
    echo "5-Tier Hybrid Inference Router Deployment and Testing"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -c, --cleanup  Cleanup resources and exit"
    echo ""
    echo "Environment Variables Required:"
    echo "  OPENROUTER_API_KEY  - OpenRouter API key"
    echo "  GROQ_API_KEY        - Groq API key"
    echo "  POSTGRES_PASSWORD   - PostgreSQL password"
    echo ""
    echo "Constitutional Hash: $CONSTITUTIONAL_HASH"
}

# Parse command line arguments
case "${1:-}" in
    -h|--help)
        show_help
        exit 0
        ;;
    -c|--cleanup)
        cleanup
        exit 0
        ;;
    "")
        main
        ;;
    *)
        log_error "Unknown option: $1"
        show_help
        exit 1
        ;;
esac
