#!/bin/bash

# ACGS E2E Test Runner Script
# Provides convenient commands for running different test scenarios

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
E2E_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(dirname "$(dirname "$E2E_DIR")")"

# Default values
TEST_MODE="${E2E_TEST_MODE:-offline}"
CONSTITUTIONAL_HASH="${CONSTITUTIONAL_HASH:-cdd01ef066bc6cf2}"
PARALLEL_WORKERS="${E2E_PARALLEL_WORKERS:-4}"
TIMEOUT="${E2E_TEST_TIMEOUT:-1800}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
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

# Help function
show_help() {
    cat << EOF
ACGS E2E Test Runner

Usage: $0 [COMMAND] [OPTIONS]

Commands:
    smoke           Run smoke tests (quick validation)
    constitutional  Run constitutional compliance tests
    hitl           Run HITL decision processing tests
    performance    Run performance and load tests
    security       Run security and compliance tests
    integration    Run service integration tests
    governance     Run multi-agent governance tests
    infrastructure Run infrastructure component tests
    all            Run complete test suite
    docker         Run tests in Docker environment
    clean          Clean test artifacts and reports

Options:
    --mode MODE         Test mode: offline|online|hybrid (default: $TEST_MODE)
    --workers N         Number of parallel workers (default: $PARALLEL_WORKERS)
    --timeout N         Test timeout in seconds (default: $TIMEOUT)
    --coverage          Generate coverage report
    --benchmark         Generate performance benchmarks
    --html              Generate HTML report
    --junit             Generate JUnit XML report
    --verbose           Verbose output
    --debug             Debug mode
    --help              Show this help

Environment Variables:
    E2E_TEST_MODE           Test execution mode
    CONSTITUTIONAL_HASH     Constitutional hash for validation
    E2E_PARALLEL_WORKERS    Number of parallel workers
    E2E_TEST_TIMEOUT        Test timeout in seconds

Examples:
    $0 smoke                    # Quick smoke tests
    $0 all --coverage          # Full suite with coverage
    $0 performance --benchmark # Performance tests with benchmarks
    $0 docker                  # Run in Docker environment
    $0 constitutional --mode online --verbose
EOF
}

# Setup environment
setup_environment() {
    log_info "Setting up test environment..."
    
    # Create reports directory
    mkdir -p "$E2E_DIR/reports"
    
    # Set environment variables
    export E2E_TEST_MODE="$TEST_MODE"
    export CONSTITUTIONAL_HASH="$CONSTITUTIONAL_HASH"
    export E2E_PARALLEL_WORKERS="$PARALLEL_WORKERS"
    export E2E_TEST_TIMEOUT="$TIMEOUT"
    export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"
    
    log_info "Test Mode: $TEST_MODE"
    log_info "Constitutional Hash: $CONSTITUTIONAL_HASH"
    log_info "Parallel Workers: $PARALLEL_WORKERS"
    log_info "Timeout: ${TIMEOUT}s"
}

# Check dependencies
check_dependencies() {
    log_info "Checking dependencies..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed"
        exit 1
    fi
    
    # Check pytest
    if ! python3 -c "import pytest" &> /dev/null; then
        log_error "pytest is required but not installed"
        log_info "Install with: pip install pytest pytest-asyncio pytest-cov"
        exit 1
    fi
    
    # Check Docker (for docker command)
    if [[ "$1" == "docker" ]] && ! command -v docker &> /dev/null; then
        log_error "Docker is required for docker command"
        exit 1
    fi
    
    log_success "Dependencies check passed"
}

# Build pytest command
build_pytest_command() {
    local test_path="$1"
    local markers="$2"
    local extra_args="$3"
    
    local cmd="python3 -m pytest"
    
    # Add test path
    if [[ -n "$test_path" ]]; then
        cmd="$cmd $test_path"
    else
        cmd="$cmd $E2E_DIR/tests/"
    fi
    
    # Add markers
    if [[ -n "$markers" ]]; then
        cmd="$cmd -m \"$markers\""
    fi
    
    # Add timeout
    cmd="$cmd --timeout=$TIMEOUT"
    
    # Add extra arguments
    if [[ -n "$extra_args" ]]; then
        cmd="$cmd $extra_args"
    fi
    
    echo "$cmd"
}

# Run smoke tests
run_smoke_tests() {
    log_info "Running smoke tests..."
    
    local cmd=$(build_pytest_command \
        "$E2E_DIR/tests/health.py" \
        "smoke" \
        "--maxfail=5 $PYTEST_ARGS")
    
    eval "$cmd"
}

# Run constitutional tests
run_constitutional_tests() {
    log_info "Running constitutional compliance tests..."
    
    local cmd=$(build_pytest_command \
        "$E2E_DIR/tests/constitutional.py $E2E_DIR/tests/hitl.py" \
        "constitutional" \
        "$PYTEST_ARGS")
    
    eval "$cmd"
}

# Run HITL tests
run_hitl_tests() {
    log_info "Running HITL decision processing tests..."
    
    local cmd=$(build_pytest_command \
        "$E2E_DIR/tests/hitl.py" \
        "hitl" \
        "$PYTEST_ARGS")
    
    eval "$cmd"
}

# Run performance tests
run_performance_tests() {
    log_info "Running performance and load tests..."
    
    local cmd=$(build_pytest_command \
        "$E2E_DIR/tests/performance.py" \
        "performance" \
        "$PYTEST_ARGS")
    
    eval "$cmd"
}

# Run security tests
run_security_tests() {
    log_info "Running security and compliance tests..."
    
    local cmd=$(build_pytest_command \
        "$E2E_DIR/tests/security.py" \
        "security" \
        "$PYTEST_ARGS")
    
    eval "$cmd"
}

# Run integration tests
run_integration_tests() {
    log_info "Running service integration tests..."
    
    local cmd=$(build_pytest_command \
        "$E2E_DIR/tests/infrastructure.py $E2E_DIR/tests/governance.py" \
        "integration" \
        "$PYTEST_ARGS")
    
    eval "$cmd"
}

# Run governance tests
run_governance_tests() {
    log_info "Running multi-agent governance tests..."
    
    local cmd=$(build_pytest_command \
        "$E2E_DIR/tests/governance.py" \
        "governance" \
        "$PYTEST_ARGS")
    
    eval "$cmd"
}

# Run infrastructure tests
run_infrastructure_tests() {
    log_info "Running infrastructure component tests..."
    
    local cmd=$(build_pytest_command \
        "$E2E_DIR/tests/infrastructure.py" \
        "infrastructure" \
        "$PYTEST_ARGS")
    
    eval "$cmd"
}

# Run all tests
run_all_tests() {
    log_info "Running complete E2E test suite..."
    
    local cmd=$(build_pytest_command \
        "" \
        "" \
        "$PYTEST_ARGS")
    
    eval "$cmd"
}

# Run tests in Docker
run_docker_tests() {
    log_info "Running tests in Docker environment..."
    
    cd "$E2E_DIR/docker"
    
    # Build and run
    docker-compose -f docker-compose.e2e.yml up --build --abort-on-container-exit
    
    # Copy reports
    docker cp acgs_e2e_test_runner:/app/reports "$E2E_DIR/" || true
    
    # Cleanup
    docker-compose -f docker-compose.e2e.yml down
    
    cd - > /dev/null
}

# Clean artifacts
clean_artifacts() {
    log_info "Cleaning test artifacts and reports..."
    
    rm -rf "$E2E_DIR/reports"
    rm -rf "$E2E_DIR/.pytest_cache"
    rm -rf "$E2E_DIR/__pycache__"
    find "$E2E_DIR" -name "*.pyc" -delete
    find "$E2E_DIR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    
    log_success "Cleanup completed"
}

# Parse arguments
COMMAND=""
PYTEST_ARGS=""

while [[ $# -gt 0 ]]; do
    case $1 in
        smoke|constitutional|hitl|performance|security|integration|governance|infrastructure|all|docker|clean)
            COMMAND="$1"
            shift
            ;;
        --mode)
            TEST_MODE="$2"
            shift 2
            ;;
        --workers)
            PARALLEL_WORKERS="$2"
            shift 2
            ;;
        --timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        --coverage)
            PYTEST_ARGS="$PYTEST_ARGS --cov=tests/e2e --cov-report=html --cov-report=xml"
            shift
            ;;
        --benchmark)
            PYTEST_ARGS="$PYTEST_ARGS --benchmark-json=reports/benchmark.json"
            shift
            ;;
        --html)
            PYTEST_ARGS="$PYTEST_ARGS --html=reports/report.html --self-contained-html"
            shift
            ;;
        --junit)
            PYTEST_ARGS="$PYTEST_ARGS --junitxml=reports/junit.xml"
            shift
            ;;
        --verbose)
            PYTEST_ARGS="$PYTEST_ARGS -v"
            shift
            ;;
        --debug)
            PYTEST_ARGS="$PYTEST_ARGS -s --log-cli-level=DEBUG"
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

# Main execution
main() {
    if [[ -z "$COMMAND" ]]; then
        log_error "No command specified"
        show_help
        exit 1
    fi
    
    check_dependencies "$COMMAND"
    setup_environment
    
    case "$COMMAND" in
        smoke)
            run_smoke_tests
            ;;
        constitutional)
            run_constitutional_tests
            ;;
        hitl)
            run_hitl_tests
            ;;
        performance)
            run_performance_tests
            ;;
        security)
            run_security_tests
            ;;
        integration)
            run_integration_tests
            ;;
        governance)
            run_governance_tests
            ;;
        infrastructure)
            run_infrastructure_tests
            ;;
        all)
            run_all_tests
            ;;
        docker)
            run_docker_tests
            ;;
        clean)
            clean_artifacts
            ;;
    esac
    
    local exit_code=$?
    
    if [[ $exit_code -eq 0 ]]; then
        log_success "Test execution completed successfully"
    else
        log_error "Test execution failed with exit code $exit_code"
    fi
    
    exit $exit_code
}

# Run main function
main "$@"
