# Constitutional Hash: cdd01ef066bc6cf2
# ACGS-2 Constitutional Compliance Validation
#!/bin/bash
# Constitutional Trainer Load Testing Orchestration Script
#
# This script orchestrates comprehensive load testing of the Constitutional Trainer Service
# including HPA validation, performance monitoring, and automated reporting.
#
# Usage:
#   ./run-constitutional-trainer-load-tests.sh [OPTIONS]

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
NAMESPACE="${NAMESPACE:-acgs-load-test}"
CONSTITUTIONAL_TRAINER_URL="${CONSTITUTIONAL_TRAINER_URL:-http://constitutional-trainer:8000}"
POLICY_ENGINE_URL="${POLICY_ENGINE_URL:-http://policy-engine:8001}"
LOAD_TEST_TOOL="${LOAD_TEST_TOOL:-k6}"  # k6 or locust
RESULTS_DIR="${RESULTS_DIR:-./load-test-results}"
GRAFANA_URL="${GRAFANA_URL:-http://grafana:3000}"

# Test configuration
BASELINE_USERS=10
PEAK_USERS=100
SPIKE_USERS=200
TEST_DURATION="10m"
RAMP_DURATION="5m"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Help function
show_help() {
    cat << EOF
Constitutional Trainer Load Testing Orchestration

This script runs comprehensive load tests against the Constitutional Trainer Service
with HPA validation and performance monitoring.

Usage:
    $0 [OPTIONS]

Options:
    --tool TOOL             Load testing tool: k6 or locust (default: k6)
    --namespace NAME        Kubernetes namespace (default: acgs-load-test)
    --baseline-users N      Baseline concurrent users (default: 10)
    --peak-users N          Peak concurrent users (default: 100)
    --spike-users N         Spike test users (default: 200)
    --duration TIME         Test duration (default: 10m)
    --results-dir DIR       Results output directory (default: ./load-test-results)
    --skip-setup           Skip environment setup
    --skip-monitoring      Skip monitoring setup
    --skip-cleanup         Skip cleanup after tests
    --help                 Show this help message

Examples:
    # Run with default settings
    $0

    # Run with custom configuration
    $0 --tool locust --peak-users 200 --duration 15m

    # Run against existing environment
    $0 --skip-setup --namespace production

Environment Variables:
    CONSTITUTIONAL_TRAINER_URL  Target service URL
    POLICY_ENGINE_URL          Policy engine URL
    GRAFANA_URL               Grafana dashboard URL
    KUBECONFIG                Kubernetes configuration

EOF
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --tool)
                LOAD_TEST_TOOL="$2"
                shift 2
                ;;
            --namespace)
                NAMESPACE="$2"
                shift 2
                ;;
            --baseline-users)
                BASELINE_USERS="$2"
                shift 2
                ;;
            --peak-users)
                PEAK_USERS="$2"
                shift 2
                ;;
            --spike-users)
                SPIKE_USERS="$2"
                shift 2
                ;;
            --duration)
                TEST_DURATION="$2"
                shift 2
                ;;
            --results-dir)
                RESULTS_DIR="$2"
                shift 2
                ;;
            --skip-setup)
                SKIP_SETUP=true
                shift
                ;;
            --skip-monitoring)
                SKIP_MONITORING=true
                shift
                ;;
            --skip-cleanup)
                SKIP_CLEANUP=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed"
        exit 1
    fi
    
    # Check load testing tool
    if [[ "$LOAD_TEST_TOOL" == "k6" ]]; then
        if ! command -v k6 &> /dev/null; then
            log_error "k6 is not installed. Install from: https://k6.io/docs/getting-started/installation/"
            exit 1
        fi
    elif [[ "$LOAD_TEST_TOOL" == "locust" ]]; then
        if ! command -v locust &> /dev/null; then
            log_error "locust is not installed. Install with: pip install locust"
            exit 1
        fi
    else
        log_error "Unsupported load testing tool: $LOAD_TEST_TOOL"
        exit 1
    fi
    
    # Check Kubernetes connectivity
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Setup test environment
setup_environment() {
    if [[ "${SKIP_SETUP:-false}" == "true" ]]; then
        log_info "Skipping environment setup"
        return
    fi
    
    log_info "Setting up load test environment..."
    
    # Create results directory
    mkdir -p "$RESULTS_DIR"
    
    # Deploy or verify services
    if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
        log_info "Deploying test environment..."
        "$PROJECT_ROOT/scripts/testing/deploy-constitutional-trainer-test-env.sh" \
            --namespace "$NAMESPACE"
    else
        log_info "Using existing namespace: $NAMESPACE"
    fi
    
    # Wait for services to be ready
    log_info "Waiting for services to be ready..."
    kubectl wait --for=condition=Ready pods --all -n "$NAMESPACE" --timeout=300s
    
    log_success "Environment setup completed"
}

# Setup monitoring
setup_monitoring() {
    if [[ "${SKIP_MONITORING:-false}" == "true" ]]; then
        log_info "Skipping monitoring setup"
        return
    fi
    
    log_info "Setting up performance monitoring..."
    
    # Start port forwarding for monitoring
    kubectl port-forward -n "$NAMESPACE" svc/grafana 3000:3000 &
    GRAFANA_PID=$!
    
    kubectl port-forward -n "$NAMESPACE" svc/prometheus 9090:9090 &
    PROMETHEUS_PID=$!
    
    # Wait for port forwards
    sleep 10
    
    log_success "Monitoring setup completed"
}

# Run baseline load test
run_baseline_test() {
    log_info "🧪 Running baseline load test ($BASELINE_USERS users)..."
    
    local test_name="baseline-$(date +%Y%m%d-%H%M%S)"
    local results_file="$RESULTS_DIR/${test_name}-results"
    
    if [[ "$LOAD_TEST_TOOL" == "k6" ]]; then
        run_k6_test "baseline" "$BASELINE_USERS" "$results_file"
    else
        run_locust_test "baseline" "$BASELINE_USERS" "$results_file"
    fi
    
    # Capture HPA metrics
    capture_hpa_metrics "$test_name"
    
    log_success "Baseline test completed"
}

# Run peak load test
run_peak_test() {
    log_info "🚀 Running peak load test ($PEAK_USERS users)..."
    
    local test_name="peak-$(date +%Y%m%d-%H%M%S)"
    local results_file="$RESULTS_DIR/${test_name}-results"
    
    if [[ "$LOAD_TEST_TOOL" == "k6" ]]; then
        run_k6_test "peak" "$PEAK_USERS" "$results_file"
    else
        run_locust_test "peak" "$PEAK_USERS" "$results_file"
    fi
    
    # Capture HPA metrics
    capture_hpa_metrics "$test_name"
    
    log_success "Peak test completed"
}

# Run spike test
run_spike_test() {
    log_info "⚡ Running spike load test ($SPIKE_USERS users)..."
    
    local test_name="spike-$(date +%Y%m%d-%H%M%S)"
    local results_file="$RESULTS_DIR/${test_name}-results"
    
    if [[ "$LOAD_TEST_TOOL" == "k6" ]]; then
        run_k6_test "spike" "$SPIKE_USERS" "$results_file"
    else
        run_locust_test "spike" "$SPIKE_USERS" "$results_file"
    fi
    
    # Capture HPA metrics
    capture_hpa_metrics "$test_name"
    
    log_success "Spike test completed"
}

# Run k6 test
run_k6_test() {
    local test_type="$1"
    local users="$2"
    local results_file="$3"
    
    export CONSTITUTIONAL_TRAINER_URL
    export POLICY_ENGINE_URL
    export TEST_DURATION
    
    k6 run \
        --vus "$users" \
        --duration "$TEST_DURATION" \
        --out json="${results_file}.json" \
        --summary-export="${results_file}-summary.json" \
        "$PROJECT_ROOT/tests/load/constitutional-trainer-load-test.js" \
        > "${results_file}.log" 2>&1
}

# Run locust test
run_locust_test() {
    local test_type="$1"
    local users="$2"
    local results_file="$3"
    
    export POLICY_ENGINE_URL
    
    locust \
        -f "$PROJECT_ROOT/tests/load/constitutional_trainer_locust.py" \
        --host "$CONSTITUTIONAL_TRAINER_URL" \
        --users "$users" \
        --spawn-rate 10 \
        --run-time "$TEST_DURATION" \
        --headless \
        --html "${results_file}.html" \
        --csv "${results_file}" \
        > "${results_file}.log" 2>&1
}

# Capture HPA metrics
capture_hpa_metrics() {
    local test_name="$1"
    local hpa_file="$RESULTS_DIR/${test_name}-hpa-metrics.json"
    
    log_info "Capturing HPA metrics for $test_name..."
    
    # Get HPA status
    kubectl get hpa -n "$NAMESPACE" -o json > "$hpa_file" 2>/dev/null || true
    
    # Get pod metrics
    kubectl top pods -n "$NAMESPACE" --no-headers > "$RESULTS_DIR/${test_name}-pod-metrics.txt" 2>/dev/null || true
    
    # Get deployment replica counts
    kubectl get deployments -n "$NAMESPACE" -o json > "$RESULTS_DIR/${test_name}-deployments.json" 2>/dev/null || true
}

# Generate comprehensive report
generate_report() {
    log_info "📊 Generating comprehensive load test report..."
    
    local report_file="$RESULTS_DIR/load-test-report-$(date +%Y%m%d-%H%M%S).md"
    
    cat > "$report_file" << EOF
# Constitutional Trainer Load Test Report

**Generated:** $(date)  
**Namespace:** $NAMESPACE  
**Load Testing Tool:** $LOAD_TEST_TOOL  
**Test Duration:** $TEST_DURATION  

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Baseline Users | $BASELINE_USERS |
| Peak Users | $PEAK_USERS |
| Spike Users | $SPIKE_USERS |
| Constitutional Trainer URL | $CONSTITUTIONAL_TRAINER_URL |
| Policy Engine URL | $POLICY_ENGINE_URL |

## Test Results Summary

### Performance Targets

| Metric | Target | Baseline Result | Peak Result | Status |
|--------|--------|----------------|-------------|--------|
| P99 Latency (Baseline) | ≤ 5ms | TBD | N/A | TBD |
| P99 Latency (Peak) | ≤ 10ms | N/A | TBD | TBD |
| Error Rate | < 1% | TBD | TBD | TBD |
| HPA Scaling | Responsive | TBD | TBD | TBD |

### Detailed Results

EOF

    # Add detailed results from each test
    for result_file in "$RESULTS_DIR"/*-summary.json; do
        if [[ -f "$result_file" ]]; then
            echo "#### $(basename "$result_file" -summary.json)" >> "$report_file"
            echo '```json' >> "$report_file"
            cat "$result_file" >> "$report_file"
            echo '```' >> "$report_file"
            echo "" >> "$report_file"
        fi
    done
    
    log_success "Report generated: $report_file"
}

# Cleanup
cleanup() {
    if [[ "${SKIP_CLEANUP:-false}" == "true" ]]; then
        log_info "Skipping cleanup"
        return
    fi
    
    log_info "🧹 Cleaning up load test environment..."
    
    # Kill port forwards
    if [[ -n "${GRAFANA_PID:-}" ]]; then
        kill "$GRAFANA_PID" 2>/dev/null || true
    fi
    if [[ -n "${PROMETHEUS_PID:-}" ]]; then
        kill "$PROMETHEUS_PID" 2>/dev/null || true
    fi
    
    # Optionally delete test namespace
    read -p "Delete test namespace '$NAMESPACE'? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kubectl delete namespace "$NAMESPACE" --ignore-not-found=true
        log_success "Test namespace deleted"
    fi
}

# Main execution
main() {
    log_info "🚀 Constitutional Trainer Load Testing Orchestration"
    echo "============================================================"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    
    parse_args "$@"
    check_prerequisites
    setup_environment
    setup_monitoring
    
    # Run test suite
    run_baseline_test
    sleep 60  # Cool down between tests
    
    run_peak_test
    sleep 60  # Cool down between tests
    
    run_spike_test
    
    # Generate final report
    generate_report
    
    log_success "✅ Load testing completed successfully!"
    echo ""
    echo "📊 Results available in: $RESULTS_DIR"
    echo "📈 Grafana dashboard: $GRAFANA_URL"
    echo ""
}

# Trap for cleanup
trap cleanup EXIT

# Execute main function
main "$@"
