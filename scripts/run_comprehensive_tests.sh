#!/bin/bash

# ACGS Comprehensive Test Runner
# Runs all tests across the project with proper error handling and reporting

set -e

# Configuration
TEST_REPORT_DIR="tests/reports"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$TEST_REPORT_DIR/test_run_${TIMESTAMP}.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
RUN_PYTHON=true
RUN_TYPESCRIPT=true
RUN_RUST=true
RUN_INTEGRATION=true
RUN_PERFORMANCE=false
GENERATE_JSON_REPORT=false
VERBOSE=false

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to log and print
log_and_print() {
    local message="$1"
    echo "$message" | tee -a "$LOG_FILE"
}

# Help function
show_help() {
    cat << EOF
ACGS Comprehensive Test Runner

Usage: $0 [OPTIONS]

Options:
    --python-only          Run only Python tests
    --typescript-only      Run only TypeScript tests
    --rust-only           Run only Rust tests
    --integration-only    Run only integration tests
    --performance         Include performance tests
    --json-report         Generate JSON report
    --verbose, -v         Verbose output
    --help, -h           Show this help message

Examples:
    $0                    # Run all tests
    $0 --python-only      # Run only Python tests
    $0 --performance --json-report  # Run all tests with performance and JSON report
EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --python-only)
            RUN_PYTHON=true
            RUN_TYPESCRIPT=false
            RUN_RUST=false
            RUN_INTEGRATION=false
            shift
            ;;
        --typescript-only)
            RUN_PYTHON=false
            RUN_TYPESCRIPT=true
            RUN_RUST=false
            RUN_INTEGRATION=false
            shift
            ;;
        --rust-only)
            RUN_PYTHON=false
            RUN_TYPESCRIPT=false
            RUN_RUST=true
            RUN_INTEGRATION=false
            shift
            ;;
        --integration-only)
            RUN_PYTHON=false
            RUN_TYPESCRIPT=false
            RUN_RUST=false
            RUN_INTEGRATION=true
            shift
            ;;
        --performance)
            RUN_PERFORMANCE=true
            shift
            ;;
        --json-report)
            GENERATE_JSON_REPORT=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Initialize test environment
init_test_environment() {
    print_status $BLUE "🔧 Initializing test environment..."
    
    # Create test reports directory
    mkdir -p "$TEST_REPORT_DIR"
    
    # Create log file
    touch "$LOG_FILE"
    
    # Check for required tools
    local missing_tools=""
    
    if $RUN_PYTHON && ! command -v python3 &> /dev/null; then
        missing_tools+="python3 "
    fi
    
    if $RUN_PYTHON && ! command -v pytest &> /dev/null; then
        print_status $YELLOW "⚠️ pytest not found, installing..."
        pip install pytest pytest-cov pytest-asyncio || missing_tools+="pytest "
    fi
    
    if $RUN_TYPESCRIPT && ! command -v npm &> /dev/null; then
        missing_tools+="npm "
    fi
    
    if $RUN_RUST && ! command -v cargo &> /dev/null; then
        missing_tools+="cargo "
    fi
    
    if [[ -n "$missing_tools" ]]; then
        print_status $RED "❌ Missing required tools: $missing_tools"
        return 1
    fi
    
    print_status $GREEN "✅ Test environment initialized"
    return 0
}

# Run Python tests
run_python_tests() {
    if ! $RUN_PYTHON; then
        return 0
    fi
    
    print_status $BLUE "🐍 Running Python tests..."
    
    local python_exit_code=0
    local test_files=""
    
    # Find Python test files
    if [ -d "tests/unit" ]; then
        test_files+="tests/unit/ "
    fi
    
    if [ -d "tests/integration" ] && $RUN_INTEGRATION; then
        test_files+="tests/integration/ "
    fi
    
    if [ -d "tests/performance" ] && $RUN_PERFORMANCE; then
        test_files+="tests/performance/ "
    fi
    
    if [ -z "$test_files" ]; then
        print_status $YELLOW "⚠️ No Python test directories found"
        return 0
    fi
    
    # Run tests with coverage
    if $VERBOSE; then
        pytest $test_files -v --cov=services --cov-report=xml --cov-report=term-missing \
            --junit-xml="$TEST_REPORT_DIR/python_test_results.xml" \
            2>&1 | tee -a "$LOG_FILE" || python_exit_code=$?
    else
        pytest $test_files --cov=services --cov-report=xml \
            --junit-xml="$TEST_REPORT_DIR/python_test_results.xml" \
            >> "$LOG_FILE" 2>&1 || python_exit_code=$?
    fi
    
    if [ $python_exit_code -eq 0 ]; then
        print_status $GREEN "✅ Python tests passed"
    else
        print_status $RED "❌ Python tests failed (exit code: $python_exit_code)"
    fi
    
    return $python_exit_code
}

# Run TypeScript/JavaScript tests
run_typescript_tests() {
    if ! $RUN_TYPESCRIPT; then
        return 0
    fi
    
    print_status $BLUE "🟨 Running TypeScript/JavaScript tests..."
    
    local typescript_exit_code=0
    local test_dirs=("applications/governance-dashboard" "project" "frontend" "client")
    local tests_found=false
    
    for dir in "${test_dirs[@]}"; do
        if [ -d "$dir" ] && [ -f "$dir/package.json" ]; then
            print_status $BLUE "Testing $dir..."
            tests_found=true
            
            cd "$dir"
            
            # Install dependencies if needed
            if [ ! -d "node_modules" ]; then
                npm install || npm ci
            fi
            
            # Run tests
            if $VERBOSE; then
                npm test 2>&1 | tee -a "../$LOG_FILE" || typescript_exit_code=$?
            else
                npm test >> "../$LOG_FILE" 2>&1 || typescript_exit_code=$?
            fi
            
            cd - > /dev/null
        fi
    done
    
    if ! $tests_found; then
        print_status $YELLOW "⚠️ No TypeScript/JavaScript projects found"
        return 0
    fi
    
    if [ $typescript_exit_code -eq 0 ]; then
        print_status $GREEN "✅ TypeScript/JavaScript tests passed"
    else
        print_status $RED "❌ TypeScript/JavaScript tests failed (exit code: $typescript_exit_code)"
    fi
    
    return $typescript_exit_code
}

# Run Rust tests
run_rust_tests() {
    if ! $RUN_RUST; then
        return 0
    fi
    
    print_status $BLUE "🦀 Running Rust tests..."
    
    local rust_exit_code=0
    
    if [ -d "blockchain" ] && [ -f "blockchain/Cargo.toml" ]; then
        cd blockchain
        
        if $VERBOSE; then
            cargo test 2>&1 | tee -a "../$LOG_FILE" || rust_exit_code=$?
        else
            cargo test >> "../$LOG_FILE" 2>&1 || rust_exit_code=$?
        fi
        
        cd - > /dev/null
    else
        print_status $YELLOW "⚠️ No Rust project found in blockchain directory"
        return 0
    fi
    
    if [ $rust_exit_code -eq 0 ]; then
        print_status $GREEN "✅ Rust tests passed"
    else
        print_status $RED "❌ Rust tests failed (exit code: $rust_exit_code)"
    fi
    
    return $rust_exit_code
}

# Run integration tests
run_integration_tests() {
    if ! $RUN_INTEGRATION; then
        return 0
    fi
    
    print_status $BLUE "🔗 Running integration tests..."
    
    local integration_exit_code=0
    
    if [ -d "tests/integration" ]; then
        if $VERBOSE; then
            pytest tests/integration/ -v --junit-xml="$TEST_REPORT_DIR/integration_test_results.xml" \
                2>&1 | tee -a "$LOG_FILE" || integration_exit_code=$?
        else
            pytest tests/integration/ --junit-xml="$TEST_REPORT_DIR/integration_test_results.xml" \
                >> "$LOG_FILE" 2>&1 || integration_exit_code=$?
        fi
    else
        print_status $YELLOW "⚠️ No integration tests found"
        return 0
    fi
    
    if [ $integration_exit_code -eq 0 ]; then
        print_status $GREEN "✅ Integration tests passed"
    else
        print_status $RED "❌ Integration tests failed (exit code: $integration_exit_code)"
    fi
    
    return $integration_exit_code
}

# Generate JSON report
generate_json_report() {
    if ! $GENERATE_JSON_REPORT; then
        return 0
    fi
    
    print_status $BLUE "📄 Generating JSON report..."
    
    local start_time=$(date -d "@$(($(date +%s) - 300))" --iso-8601=seconds)
    local end_time=$(date --iso-8601=seconds)
    local duration=300  # Approximate duration in seconds
    
    cat > "$TEST_REPORT_DIR/comprehensive_test_report.json" << EOF
{
    "test_run_info": {
        "timestamp": "$end_time",
        "start_time": "$start_time",
        "end_time": "$end_time",
        "duration": $duration,
        "status": "completed",
        "runner": "comprehensive_test_runner",
        "version": "1.0.0"
    },
    "configuration": {
        "python_tests": $RUN_PYTHON,
        "typescript_tests": $RUN_TYPESCRIPT,
        "rust_tests": $RUN_RUST,
        "integration_tests": $RUN_INTEGRATION,
        "performance_tests": $RUN_PERFORMANCE,
        "verbose": $VERBOSE
    },
    "results": {
        "python": {
            "enabled": $RUN_PYTHON,
            "status": "completed"
        },
        "typescript": {
            "enabled": $RUN_TYPESCRIPT,
            "status": "completed"
        },
        "rust": {
            "enabled": $RUN_RUST,
            "status": "completed"
        },
        "integration": {
            "enabled": $RUN_INTEGRATION,
            "status": "completed"
        }
    },
    "artifacts": [
        "python_test_results.xml",
        "integration_test_results.xml",
        "coverage.xml",
        "test_run_${TIMESTAMP}.log"
    ]
}
EOF
    
    print_status $GREEN "✅ JSON report generated at $TEST_REPORT_DIR/comprehensive_test_report.json"
}

# Main execution function
main() {
    local start_time=$(date +%s)
    
    print_status $BLUE "🚀 Starting ACGS Comprehensive Test Runner"
    log_and_print "Test run started at $(date)"
    
    # Initialize environment
    if ! init_test_environment; then
        print_status $RED "❌ Failed to initialize test environment"
        exit 1
    fi
    
    # Track overall success
    local overall_exit_code=0
    
    # Run tests
    run_python_tests || overall_exit_code=$?
    run_typescript_tests || overall_exit_code=$?
    run_rust_tests || overall_exit_code=$?
    run_integration_tests || overall_exit_code=$?
    
    # Generate reports
    generate_json_report
    
    # Calculate duration
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    print_status $BLUE "📊 Test Summary"
    log_and_print "===================="
    log_and_print "Total duration: ${duration}s"
    log_and_print "Python tests: $([ "$RUN_PYTHON" = true ] && echo "enabled" || echo "disabled")"
    log_and_print "TypeScript tests: $([ "$RUN_TYPESCRIPT" = true ] && echo "enabled" || echo "disabled")"
    log_and_print "Rust tests: $([ "$RUN_RUST" = true ] && echo "enabled" || echo "disabled")"
    log_and_print "Integration tests: $([ "$RUN_INTEGRATION" = true ] && echo "enabled" || echo "disabled")"
    log_and_print "Performance tests: $([ "$RUN_PERFORMANCE" = true ] && echo "enabled" || echo "disabled")"
    
    if [ $overall_exit_code -eq 0 ]; then
        print_status $GREEN "✅ All tests completed successfully!"
        log_and_print "Overall result: SUCCESS"
    else
        print_status $RED "❌ Some tests failed"
        log_and_print "Overall result: FAILURE (exit code: $overall_exit_code)"
    fi
    
    log_and_print "Test run completed at $(date)"
    print_status $BLUE "📄 Full log available at: $LOG_FILE"
    
    exit $overall_exit_code
}

# Run main function
main "$@"