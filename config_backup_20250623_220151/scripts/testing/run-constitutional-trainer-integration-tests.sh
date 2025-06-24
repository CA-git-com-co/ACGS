#!/bin/bash
# Constitutional Trainer Integration Test Runner
#
# Quick execution script for running Constitutional Trainer integration tests
# with proper environment setup and reporting.
#
# Usage:
#   ./run-constitutional-trainer-integration-tests.sh [OPTIONS]

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
TEST_NAMESPACE="acgs-integration-test"
DEPLOY_SERVICES=true
CLEANUP_AFTER=true
GENERATE_REPORT=true

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --no-deploy)
            DEPLOY_SERVICES=false
            shift
            ;;
        --no-cleanup)
            CLEANUP_AFTER=false
            shift
            ;;
        --no-report)
            GENERATE_REPORT=false
            shift
            ;;
        --namespace)
            TEST_NAMESPACE="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [--no-deploy] [--no-cleanup] [--no-report] [--namespace NAME]"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

main() {
    log_info "🚀 Starting Constitutional Trainer Integration Tests"
    echo "============================================================"
    
    # Step 1: Deploy test environment (if requested)
    if [[ "$DEPLOY_SERVICES" == "true" ]]; then
        log_info "📦 Deploying test environment..."
        if ! "$SCRIPT_DIR/deploy-constitutional-trainer-test-env.sh" --namespace "$TEST_NAMESPACE" --mock-services; then
            log_error "Failed to deploy test environment"
            exit 1
        fi
        
        # Wait a bit for services to stabilize
        log_info "⏳ Waiting for services to stabilize..."
        sleep 30
    fi
    
    # Step 2: Set up port forwarding for local testing
    log_info "🔗 Setting up port forwarding..."
    setup_port_forwarding
    
    # Step 3: Run integration tests
    log_info "🧪 Running integration tests..."
    run_tests
    
    # Step 4: Generate test report (if requested)
    if [[ "$GENERATE_REPORT" == "true" ]]; then
        log_info "📊 Generating test report..."
        generate_report
    fi
    
    # Step 5: Cleanup (if requested)
    if [[ "$CLEANUP_AFTER" == "true" ]]; then
        log_info "🧹 Cleaning up test environment..."
        cleanup_environment
    fi
    
    log_info "✅ Integration test execution completed"
}

setup_port_forwarding() {
    # Kill any existing port forwards
    pkill -f "kubectl port-forward" || true
    sleep 2
    
    # Set up new port forwards
    kubectl port-forward -n "$TEST_NAMESPACE" svc/constitutional-trainer 8000:8000 &
    kubectl port-forward -n "$TEST_NAMESPACE" svc/policy-engine 8001:8001 &
    kubectl port-forward -n "$TEST_NAMESPACE" svc/audit-engine 8003:8003 &
    kubectl port-forward -n "$TEST_NAMESPACE" svc/redis 6379:6379 &
    
    # Wait for port forwards to be established
    sleep 10
    
    # Verify connectivity
    for port in 8000 8001 8003 6379; do
        if ! nc -z localhost "$port" 2>/dev/null; then
            log_warning "Port $port not accessible, continuing anyway..."
        fi
    done
}

run_tests() {
    cd "$PROJECT_ROOT"
    
    # Set environment variables for tests
    export CONSTITUTIONAL_TRAINER_URL="http://localhost:8000"
    export POLICY_ENGINE_URL="http://localhost:8001"
    export AUDIT_ENGINE_URL="http://localhost:8003"
    export REDIS_URL="redis://localhost:6379/0"
    
    # Run pytest with comprehensive options
    if pytest tests/integration/test_constitutional_trainer_integration.py \
        -v \
        --tb=short \
        --capture=no \
        --junit-xml=constitutional_trainer_test_results.xml; then
        log_info "✅ Integration tests PASSED"
        return 0
    else
        log_error "❌ Integration tests FAILED"
        return 1
    fi
}

generate_report() {
    cd "$PROJECT_ROOT"
    
    # Find the latest test results file
    LATEST_REPORT=$(find . -name "constitutional_trainer_integration_report_*.json" -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)
    
    if [[ -n "$LATEST_REPORT" && -f "$LATEST_REPORT" ]]; then
        log_info "📄 Generating reports from: $LATEST_REPORT"
        
        # Create reports directory
        mkdir -p reports
        
        # Generate reports in all formats
        python scripts/testing/generate-integration-test-report.py \
            --input-file "$LATEST_REPORT" \
            --output-dir reports \
            --format all \
            --include-metrics \
            --include-charts
            
        log_info "📊 Reports generated in: reports/"
        ls -la reports/
    else
        log_warning "No test results file found for report generation"
    fi
}

cleanup_environment() {
    # Kill port forwards
    pkill -f "kubectl port-forward" || true
    
    # Delete test namespace if we deployed it
    if [[ "$DEPLOY_SERVICES" == "true" ]]; then
        kubectl delete namespace "$TEST_NAMESPACE" --ignore-not-found=true
        log_info "🗑️ Test namespace deleted: $TEST_NAMESPACE"
    fi
}

# Trap to ensure cleanup on exit
trap cleanup_environment EXIT

# Execute main function
main "$@"
