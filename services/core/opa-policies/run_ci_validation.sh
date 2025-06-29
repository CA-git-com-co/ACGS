#!/bin/bash
# ACGS-1 Lite CI/CD Performance Validation Runner
# Constitutional Hash: cdd01ef066bc6cf2

set -e

echo "🚀 ACGS-1 Lite CI/CD Performance Validation Suite"
echo "Constitutional Hash: cdd01ef066bc6cf2"
echo "================================================="

# Configuration
POLICY_ENGINE_URL="${POLICY_ENGINE_URL:-http://localhost:8004}"
PROMETHEUS_URL="${PROMETHEUS_URL:-http://localhost:9090}"
PERFORMANCE_TARGET_P99_MS="${PERFORMANCE_TARGET_P99_MS:-5.0}"
RESULTS_DIR="ci-validation-results"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create results directory
mkdir -p "$RESULTS_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Test results tracking
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

run_test() {
    local test_name="$1"
    local test_command="$2"
    local test_description="$3"
    
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    
    log_info "Running: $test_description"
    echo "Command: $test_command"
    echo ""
    
    if eval "$test_command"; then
        log_success "$test_name PASSED"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        log_error "$test_name FAILED"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# Pre-flight checks
echo ""
log_info "Pre-flight checks..."

# Check if policy engine is running
if curl -s -f "$POLICY_ENGINE_URL/v1/data/acgs/main/health" > /dev/null; then
    log_success "Policy engine is accessible at $POLICY_ENGINE_URL"
else
    log_error "Policy engine is not accessible at $POLICY_ENGINE_URL"
    echo "Please ensure the policy engine service is running:"
    echo "  cd /home/ubuntu/ACGS/services/core/opa-policies"
    echo "  ./deploy.sh"
    exit 1
fi

# Check dependencies
log_info "Checking dependencies..."

missing_deps=()

if ! command -v python3 &> /dev/null; then
    missing_deps+=("python3")
fi

if ! python3 -c "import pytest" &> /dev/null; then
    missing_deps+=("pytest")
fi

if ! python3 -c "import locust" &> /dev/null; then
    missing_deps+=("locust")
fi

if ! python3 -c "import httpx" &> /dev/null; then
    missing_deps+=("httpx")
fi

if [ ${#missing_deps[@]} -ne 0 ]; then
    log_error "Missing dependencies: ${missing_deps[*]}"
    log_info "Installing missing dependencies..."
    pip install -r requirements.txt
fi

log_success "All dependencies are available"

# Start validation tests
echo ""
echo "🧪 Starting CI/CD Performance Validation Tests"
echo "=============================================="

# Test 1: Pytest Benchmark Tests
echo ""
log_info "Test 1: Pytest Benchmark Validation"
run_test "pytest_benchmark" \
    "python3 -m pytest test_ci_performance.py::test_single_request_latency_slo -v --tb=short" \
    "Single request latency SLO validation"

# Test 2: Concurrent Performance Test
echo ""
log_info "Test 2: Concurrent Performance Validation"
run_test "concurrent_performance" \
    "python3 -m pytest test_ci_performance.py::test_concurrent_performance_scaling -v --tb=short" \
    "Concurrent performance scaling validation"

# Test 3: Mixed Workload Test
echo ""
log_info "Test 3: Mixed Workload Performance"
run_test "mixed_workload" \
    "python3 -m pytest test_ci_performance.py::test_mixed_workload_performance -v --tb=short" \
    "Mixed workload performance validation"

# Test 4: Cache Effectiveness
echo ""
log_info "Test 4: Cache Effectiveness Validation"
run_test "cache_effectiveness" \
    "python3 -m pytest test_ci_performance.py::test_cache_effectiveness -v --tb=short" \
    "Cache effectiveness validation"

# Test 5: Service Metrics Validation
echo ""
log_info "Test 5: Service Metrics Validation"
run_test "service_metrics" \
    "python3 -m pytest test_ci_performance.py::test_service_metrics_validation -v --tb=short" \
    "Service metrics validation"

# Test 6: Locust Load Test
echo ""
log_info "Test 6: Locust Load Testing"
LOCUST_RESULTS_FILE="$RESULTS_DIR/locust_results_${TIMESTAMP}.json"

run_test "locust_load_test" \
    "timeout 120 locust -f locust_ci.py --headless --users 25 --spawn-rate 5 --run-time 60s --host $POLICY_ENGINE_URL --logfile $RESULTS_DIR/locust_${TIMESTAMP}.log" \
    "Realistic load testing with Locust"

# Copy Locust results if they exist
if [ -f "locust_results.json" ]; then
    cp "locust_results.json" "$LOCUST_RESULTS_FILE"
    log_success "Locust results saved to $LOCUST_RESULTS_FILE"
fi

# Test 7: Prometheus Metrics Validation
echo ""
log_info "Test 7: Prometheus Metrics Validation"
run_test "prometheus_metrics" \
    "python3 prometheus_metrics.py --mode validate --policy-url $POLICY_ENGINE_URL --prometheus-url $PROMETHEUS_URL" \
    "Prometheus metrics availability validation"

# Test 8: Performance Regression Test
echo ""
log_info "Test 8: Performance Regression Test"
run_test "performance_regression" \
    "python3 prometheus_metrics.py --mode test --policy-url $POLICY_ENGINE_URL --duration 30" \
    "Performance regression detection"

# Test 9: Comprehensive Benchmark
echo ""
log_info "Test 9: Comprehensive Performance Benchmark"
BENCHMARK_RESULTS_FILE="$RESULTS_DIR/benchmark_results_${TIMESTAMP}.json"

run_test "comprehensive_benchmark" \
    "timeout 300 python3 benchmark.py --url $POLICY_ENGINE_URL --requests 1000 --concurrent-users 25 --requests-per-user 40 > $RESULTS_DIR/benchmark_${TIMESTAMP}.log 2>&1" \
    "Comprehensive performance benchmark"

# Generate test report
echo ""
echo "📊 Generating Test Report"
echo "========================"

REPORT_FILE="$RESULTS_DIR/ci_validation_report_${TIMESTAMP}.md"

cat > "$REPORT_FILE" << EOF
# ACGS-1 Lite CI/CD Performance Validation Report

**Generated:** $(date)  
**Constitutional Hash:** cdd01ef066bc6cf2  
**Policy Engine URL:** $POLICY_ENGINE_URL  
**Performance Target:** P99 < ${PERFORMANCE_TARGET_P99_MS}ms

## Test Results Summary

| Test | Status | Description |
|------|--------|-------------|
| Pytest Benchmark | $([ $TESTS_PASSED -gt 0 ] && echo "✅ PASSED" || echo "❌ FAILED") | Single request latency SLO validation |
| Concurrent Performance | $([ $TESTS_PASSED -gt 1 ] && echo "✅ PASSED" || echo "❌ FAILED") | Concurrent performance scaling |
| Mixed Workload | $([ $TESTS_PASSED -gt 2 ] && echo "✅ PASSED" || echo "❌ FAILED") | Mixed workload performance |
| Cache Effectiveness | $([ $TESTS_PASSED -gt 3 ] && echo "✅ PASSED" || echo "❌ FAILED") | Cache performance validation |
| Service Metrics | $([ $TESTS_PASSED -gt 4 ] && echo "✅ PASSED" || echo "❌ FAILED") | Service metrics validation |
| Locust Load Test | $([ $TESTS_PASSED -gt 5 ] && echo "✅ PASSED" || echo "❌ FAILED") | Realistic load testing |
| Prometheus Metrics | $([ $TESTS_PASSED -gt 6 ] && echo "✅ PASSED" || echo "❌ FAILED") | Metrics collection validation |
| Performance Regression | $([ $TESTS_PASSED -gt 7 ] && echo "✅ PASSED" || echo "❌ FAILED") | Regression detection |
| Comprehensive Benchmark | $([ $TESTS_PASSED -gt 8 ] && echo "✅ PASSED" || echo "❌ FAILED") | Full performance benchmark |

## Overall Results

- **Total Tests:** $TESTS_TOTAL
- **Passed:** $TESTS_PASSED
- **Failed:** $TESTS_FAILED
- **Success Rate:** $(( TESTS_PASSED * 100 / TESTS_TOTAL ))%

## Performance Targets

- **P99 Latency:** < ${PERFORMANCE_TARGET_P99_MS}ms
- **Average Latency:** < 2ms
- **Cache Hit Rate:** > 90%
- **Success Rate:** > 99%
- **Constitutional Compliance:** > 95%

## Files Generated

- Test logs: \`$RESULTS_DIR/\`
- Locust results: \`$LOCUST_RESULTS_FILE\`
- Benchmark results: \`$BENCHMARK_RESULTS_FILE\`

## Recommendations

$(if [ $TESTS_FAILED -eq 0 ]; then
    echo "✅ **All tests passed!** The policy engine is performing within SLO targets and is ready for production deployment."
else
    echo "❌ **Some tests failed.** Review the failed tests and address performance issues before deployment:"
    echo ""
    echo "1. Check service logs for errors"
    echo "2. Verify resource allocation (CPU, memory)"
    echo "3. Review cache configuration"
    echo "4. Analyze request patterns and optimize accordingly"
fi)

---
*Generated by ACGS-1 Lite CI/CD Performance Validation Suite*
EOF

log_success "Test report generated: $REPORT_FILE"

# Final summary
echo ""
echo "🏁 CI/CD Performance Validation Complete"
echo "========================================"
echo ""
echo "Results Summary:"
echo "  Total Tests: $TESTS_TOTAL"
echo "  Passed: $TESTS_PASSED"
echo "  Failed: $TESTS_FAILED"
echo "  Success Rate: $(( TESTS_PASSED * 100 / TESTS_TOTAL ))%"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    log_success "All performance validation tests PASSED!"
    echo ""
    echo "🎉 The ACGS-1 Lite Policy Engine is performing within SLO targets."
    echo "✅ Ready for production deployment."
    echo ""
    echo "Key Results:"
    if [ -f "$LOCUST_RESULTS_FILE" ]; then
        echo "  - Locust Results: $LOCUST_RESULTS_FILE"
    fi
    echo "  - Full Report: $REPORT_FILE"
    echo "  - All Logs: $RESULTS_DIR/"
    
    exit 0
else
    log_error "Performance validation FAILED!"
    echo ""
    echo "❌ $TESTS_FAILED out of $TESTS_TOTAL tests failed."
    echo "🔧 Please address the performance issues before proceeding."
    echo ""
    echo "Next Steps:"
    echo "  1. Review failed test logs in $RESULTS_DIR/"
    echo "  2. Check service resource utilization"
    echo "  3. Optimize configuration as needed"
    echo "  4. Re-run validation: ./run_ci_validation.sh"
    
    exit 1
fi