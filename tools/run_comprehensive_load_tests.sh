#!/bin/bash
# ACGS-PGP Comprehensive Load Testing Suite Runner
# Production-Ready Performance Validation

set -e

PROJECT_ROOT="/home/ubuntu/ACGS"
RESULTS_DIR="$PROJECT_ROOT/tests/performance/results"
LOG_DIR="$PROJECT_ROOT/logs/load_testing"

# Create necessary directories
mkdir -p "$RESULTS_DIR" "$LOG_DIR"

echo "🚀 ACGS-PGP Comprehensive Load Testing Suite"
echo "============================================"

# Check if services are running
check_services() {
    echo "🔍 Checking service availability..."
    
    services=(
        "localhost:8003"  # Policy Governance Controller
        "localhost:8000"  # Constitutional Trainer
        "localhost:8005"  # Quantum Error Correction
        "localhost:8007"  # Democratic Governance Module
        "localhost:8006"  # Appeals Logging Service
    )
    
    for service in "${services[@]}"; do
        if curl -s --connect-timeout 5 "http://$service/health" > /dev/null 2>&1; then
            echo "  ✅ $service is available"
        else
            echo "  ❌ $service is not available"
            echo "  Please start the ACGS-PGP services before running load tests"
            exit 1
        fi
    done
}

# Install dependencies
install_dependencies() {
    echo "📦 Installing load testing dependencies..."
    
    cd "$PROJECT_ROOT"
    
    # Install Python dependencies
    pip install -q aiohttp locust pytest-asyncio
    
    echo "  ✅ Dependencies installed"
}

# Run baseline performance tests
run_baseline_tests() {
    echo "📊 Running baseline performance tests..."
    
    cd "$PROJECT_ROOT"
    
    # Run individual service tests
    python -m pytest tests/performance/test_performance.py -v \
        --tb=short \
        --log-file="$LOG_DIR/baseline_tests.log" \
        > "$RESULTS_DIR/baseline_test_output.txt" 2>&1
    
    echo "  ✅ Baseline tests completed"
}

# Run comprehensive load testing suite
run_comprehensive_tests() {
    echo "🔥 Running comprehensive load testing suite..."
    
    local users=${1:-1000}
    local duration=${2:-300}
    local chaos_enabled=${3:-true}
    
    cd "$PROJECT_ROOT"
    
    # Set environment variables
    export ACGS_BASE_URL="http://localhost"
    export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"
    
    # Run comprehensive load tests
    if [ "$chaos_enabled" = "true" ]; then
        python tests/performance/comprehensive_load_testing_suite.py \
            --users "$users" \
            --duration "$duration" \
            > "$LOG_DIR/comprehensive_load_test.log" 2>&1
    else
        python tests/performance/comprehensive_load_testing_suite.py \
            --users "$users" \
            --duration "$duration" \
            --no-chaos \
            > "$LOG_DIR/comprehensive_load_test.log" 2>&1
    fi
    
    echo "  ✅ Comprehensive load tests completed"
}

# Run Locust-based load tests
run_locust_tests() {
    echo "🦗 Running Locust-based load tests..."
    
    cd "$PROJECT_ROOT"
    
    # Run PGC load test
    if [ -f "tests/performance/test_pgc_load.py" ]; then
        locust -f tests/performance/test_pgc_load.py \
            --host=http://localhost:8003 \
            --users=100 \
            --spawn-rate=10 \
            --run-time=120s \
            --headless \
            --html="$RESULTS_DIR/pgc_load_test_report.html" \
            --csv="$RESULTS_DIR/pgc_load_test" \
            > "$LOG_DIR/locust_pgc_test.log" 2>&1
        
        echo "  ✅ PGC Locust test completed"
    fi
    
    # Run DGM load test
    if [ -f "services/core/dgm-service/tests/performance/locustfile.py" ]; then
        locust -f services/core/dgm-service/tests/performance/locustfile.py \
            --host=http://localhost:8007 \
            --users=50 \
            --spawn-rate=5 \
            --run-time=120s \
            --headless \
            --html="$RESULTS_DIR/dgm_load_test_report.html" \
            --csv="$RESULTS_DIR/dgm_load_test" \
            > "$LOG_DIR/locust_dgm_test.log" 2>&1
        
        echo "  ✅ DGM Locust test completed"
    fi
}

# Run chaos engineering tests
run_chaos_tests() {
    echo "🔥 Running chaos engineering tests..."
    
    cd "$PROJECT_ROOT"
    
    # Run enhanced integration tests with chaos
    python -m pytest tests/enhanced_integration_tests.py::test_full_chaos_engineering_suite \
        -v --tb=short \
        --log-file="$LOG_DIR/chaos_tests.log" \
        > "$RESULTS_DIR/chaos_test_output.txt" 2>&1
    
    echo "  ✅ Chaos engineering tests completed"
}

# Generate performance report
generate_report() {
    echo "📋 Generating performance report..."
    
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local report_file="$RESULTS_DIR/load_testing_summary_$timestamp.md"
    
    cat > "$report_file" << EOF
# ACGS-PGP Load Testing Summary Report

**Generated:** $(date)
**Test Suite:** Comprehensive Load Testing Suite

## Test Configuration
- Maximum Concurrent Users: ${1:-1000}
- Test Duration: ${2:-300} seconds
- Chaos Engineering: ${3:-enabled}

## Test Results

### Baseline Performance Tests
$(if [ -f "$RESULTS_DIR/baseline_test_output.txt" ]; then
    echo "✅ Completed - See baseline_test_output.txt for details"
else
    echo "❌ Not completed"
fi)

### Comprehensive Load Tests
$(if [ -f "$LOG_DIR/comprehensive_load_test.log" ]; then
    echo "✅ Completed - See comprehensive_load_test.log for details"
    if [ -f "$RESULTS_DIR/comprehensive_load_test_report_"*.json ]; then
        echo "📊 Detailed report: $(ls -t $RESULTS_DIR/comprehensive_load_test_report_*.json | head -1)"
    fi
else
    echo "❌ Not completed"
fi)

### Locust Load Tests
$(if [ -f "$RESULTS_DIR/pgc_load_test_report.html" ]; then
    echo "✅ PGC Load Test - See pgc_load_test_report.html"
else
    echo "❌ PGC Load Test not completed"
fi)

$(if [ -f "$RESULTS_DIR/dgm_load_test_report.html" ]; then
    echo "✅ DGM Load Test - See dgm_load_test_report.html"
else
    echo "❌ DGM Load Test not completed"
fi)

### Chaos Engineering Tests
$(if [ -f "$RESULTS_DIR/chaos_test_output.txt" ]; then
    echo "✅ Completed - See chaos_test_output.txt for details"
else
    echo "❌ Not completed"
fi)

## Performance Targets
- Policy Generation Latency: ≤100ms (95th percentile)
- Sustained Throughput: ≥10,000 TPS
- System Uptime: ≥99.9%
- False Positive Reduction: ≥40%
- Detection Accuracy: ≥95%

## Files Generated
- Logs: $LOG_DIR/
- Results: $RESULTS_DIR/
- Reports: $RESULTS_DIR/*_report.html

## Next Steps
1. Review detailed test results in the generated files
2. Analyze performance bottlenecks
3. Implement recommended optimizations
4. Re-run tests to validate improvements
EOF

    echo "  ✅ Report generated: $report_file"
}

# Main execution
main() {
    local users=${1:-1000}
    local duration=${2:-300}
    local chaos_enabled=${3:-true}
    local skip_services_check=${4:-false}
    
    echo "Starting load testing with $users users for ${duration}s (chaos: $chaos_enabled)"
    
    # Check services unless skipped
    if [ "$skip_services_check" != "true" ]; then
        check_services
    fi
    
    # Install dependencies
    install_dependencies
    
    # Run test phases
    run_baseline_tests
    run_comprehensive_tests "$users" "$duration" "$chaos_enabled"
    run_locust_tests
    
    if [ "$chaos_enabled" = "true" ]; then
        run_chaos_tests
    fi
    
    # Generate final report
    generate_report "$users" "$duration" "$chaos_enabled"
    
    echo ""
    echo "🎉 Load testing suite completed successfully!"
    echo "📊 Results available in: $RESULTS_DIR"
    echo "📋 Logs available in: $LOG_DIR"
}

# Parse command line arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [users] [duration] [chaos_enabled] [skip_services_check]"
        echo "  users: Maximum concurrent users (default: 1000)"
        echo "  duration: Test duration in seconds (default: 300)"
        echo "  chaos_enabled: Enable chaos engineering (default: true)"
        echo "  skip_services_check: Skip service availability check (default: false)"
        echo ""
        echo "Examples:"
        echo "  $0                    # Run with defaults"
        echo "  $0 500 180 true       # 500 users, 180s, with chaos"
        echo "  $0 1000 300 false     # 1000 users, 300s, no chaos"
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac
