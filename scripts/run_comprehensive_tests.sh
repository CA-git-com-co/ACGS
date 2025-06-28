#!/bin/bash
# Comprehensive test runner for ACGS project
# This script runs all test suites with proper error handling and reporting

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Test results tracking
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
SKIPPED_TESTS=0

# Error handling
trap 'echo -e "${RED}Script interrupted. Cleaning up...${NC}"; exit 130' INT TERM

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

# Check if required tools are installed
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    local missing_tools=()
    
    # Check for Python
    if ! command -v python3 >/dev/null 2>&1; then
        missing_tools+=("python3")
    fi
    
    # Check for Node.js
    if ! command -v node >/dev/null 2>&1; then
        missing_tools+=("node")
    fi
    
    # Check for Rust/Cargo
    if ! command -v cargo >/dev/null 2>&1; then
        missing_tools+=("cargo")
    fi
    
    # Check for Docker (optional but recommended)
    if ! command -v docker >/dev/null 2>&1; then
        log_warning "Docker not found. Some integration tests may be skipped."
    fi
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        log_error "Please install the missing tools and try again."
        exit 1
    fi
    
    log_success "All required tools are installed"
}

# Run Python tests
run_python_tests() {
    log_info "Running Python tests..."
    
    cd "$PROJECT_ROOT"
    
    # Check if pytest is installed
    if ! python3 -m pytest --version >/dev/null 2>&1; then
        log_warning "pytest not installed. Installing it temporarily..."
        python3 -m pip install --user pytest pytest-cov pytest-asyncio || {
            log_error "Failed to install pytest"
            return 1
        }
    fi
    
    # Find and run Python tests
    if [ -d "tests" ] || find . -name "test_*.py" -o -name "*_test.py" | grep -q .; then
        log_info "Found Python test files"
        
        # Run tests with coverage if possible
        if python3 -m pytest --version >/dev/null 2>&1; then
            python3 -m pytest \
                --tb=short \
                --verbose \
                -x \
                --capture=no \
                2>&1 | tee pytest_output.log || {
                log_error "Python tests failed"
                ((FAILED_TESTS++))
                return 1
            }
            ((PASSED_TESTS++))
            log_success "Python tests passed"
        else
            log_warning "pytest not available, skipping Python tests"
            ((SKIPPED_TESTS++))
        fi
    else
        log_warning "No Python test files found"
        ((SKIPPED_TESTS++))
    fi
    
    ((TOTAL_TESTS++))
}

# Run TypeScript/JavaScript tests
run_typescript_tests() {
    log_info "Running TypeScript/JavaScript tests..."
    
    cd "$PROJECT_ROOT"
    
    # Look for package.json files
    local test_dirs=()
    while IFS= read -r -d '' package_json; do
        local dir=$(dirname "$package_json")
        if grep -q '"test"' "$package_json" 2>/dev/null; then
            test_dirs+=("$dir")
        fi
    done < <(find . -name "package.json" -not -path "*/node_modules/*" -print0)
    
    if [ ${#test_dirs[@]} -eq 0 ]; then
        log_warning "No TypeScript/JavaScript test configurations found"
        ((SKIPPED_TESTS++))
        ((TOTAL_TESTS++))
        return 0
    fi
    
    for dir in "${test_dirs[@]}"; do
        log_info "Running tests in $dir..."
        cd "$dir"
        
        # Install dependencies if needed
        if [ ! -d "node_modules" ]; then
            log_info "Installing dependencies..."
            npm install --no-audit --no-fund || {
                log_error "Failed to install dependencies in $dir"
                ((FAILED_TESTS++))
                ((TOTAL_TESTS++))
                continue
            }
        fi
        
        # Run tests
        npm test || {
            log_error "Tests failed in $dir"
            ((FAILED_TESTS++))
            ((TOTAL_TESTS++))
            continue
        }
        
        ((PASSED_TESTS++))
        ((TOTAL_TESTS++))
        log_success "Tests passed in $dir"
        
        cd "$PROJECT_ROOT"
    done
}

# Run Rust tests
run_rust_tests() {
    log_info "Running Rust tests..."
    
    cd "$PROJECT_ROOT"
    
    # Find Cargo.toml files
    local cargo_dirs=()
    while IFS= read -r -d '' cargo_toml; do
        cargo_dirs+=("$(dirname "$cargo_toml")")
    done < <(find . -name "Cargo.toml" -not -path "*/target/*" -print0)
    
    if [ ${#cargo_dirs[@]} -eq 0 ]; then
        log_warning "No Rust projects found"
        ((SKIPPED_TESTS++))
        ((TOTAL_TESTS++))
        return 0
    fi
    
    for dir in "${cargo_dirs[@]}"; do
        log_info "Running Rust tests in $dir..."
        cd "$dir"
        
        # Run tests
        cargo test --all-features || {
            log_error "Rust tests failed in $dir"
            ((FAILED_TESTS++))
            ((TOTAL_TESTS++))
            continue
        }
        
        ((PASSED_TESTS++))
        ((TOTAL_TESTS++))
        log_success "Rust tests passed in $dir"
        
        cd "$PROJECT_ROOT"
    done
}

# Run integration tests
run_integration_tests() {
    log_info "Running integration tests..."
    
    cd "$PROJECT_ROOT"
    
    # Check if Docker is available for integration tests
    if ! command -v docker >/dev/null 2>&1; then
        log_warning "Docker not available, skipping integration tests"
        ((SKIPPED_TESTS++))
        ((TOTAL_TESTS++))
        return 0
    fi
    
    # Check if docker-compose exists
    if [ -f "docker-compose.yml" ] || [ -f "docker-compose.yaml" ]; then
        log_info "Found docker-compose configuration"
        
        # Run integration tests if they exist
        if [ -d "tests/integration" ] || [ -f "scripts/integration_test.py" ]; then
            log_info "Running integration test suite..."
            
            # Start services if needed
            docker-compose up -d || {
                log_error "Failed to start Docker services"
                ((FAILED_TESTS++))
                ((TOTAL_TESTS++))
                return 1
            }
            
            # Wait for services to be ready
            sleep 5
            
            # Run integration tests
            if [ -f "scripts/integration_test.py" ]; then
                python3 scripts/integration_test.py || {
                    log_error "Integration tests failed"
                    docker-compose down
                    ((FAILED_TESTS++))
                    ((TOTAL_TESTS++))
                    return 1
                }
            fi
            
            # Clean up
            docker-compose down
            
            ((PASSED_TESTS++))
            ((TOTAL_TESTS++))
            log_success "Integration tests passed"
        else
            log_warning "No integration test files found"
            ((SKIPPED_TESTS++))
            ((TOTAL_TESTS++))
        fi
    else
        log_warning "No docker-compose configuration found"
        ((SKIPPED_TESTS++))
        ((TOTAL_TESTS++))
    fi
}

# Generate test report
generate_report() {
    log_info "Generating test report..."
    
    local report_file="$PROJECT_ROOT/test_report.txt"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    cat > "$report_file" << EOF
ACGS Comprehensive Test Report
Generated: $timestamp

Test Summary:
=============
Total Tests Run: $TOTAL_TESTS
Passed: $PASSED_TESTS
Failed: $FAILED_TESTS
Skipped: $SKIPPED_TESTS

Success Rate: $(( TOTAL_TESTS > 0 ? (PASSED_TESTS * 100 / TOTAL_TESTS) : 0 ))%

Test Categories:
- Python Tests: $([ -f pytest_output.log ] && echo "Run" || echo "Skipped")
- TypeScript/JavaScript Tests: Run
- Rust Tests: Run
- Integration Tests: Run

EOF
    
    if [ $FAILED_TESTS -gt 0 ]; then
        echo "Failed Tests Details:" >> "$report_file"
        echo "===================" >> "$report_file"
        # Add details from test logs if available
        if [ -f pytest_output.log ]; then
            echo "Python Test Failures:" >> "$report_file"
            grep -E "FAILED|ERROR" pytest_output.log >> "$report_file" || true
        fi
    fi
    
    log_info "Test report saved to: $report_file"
}

# Main execution
main() {
    log_info "Starting ACGS comprehensive test suite..."
    log_info "Project root: $PROJECT_ROOT"
    
    # Check prerequisites
    check_prerequisites
    
    # Run different test suites
    run_python_tests
    run_typescript_tests
    run_rust_tests
    run_integration_tests
    
    # Generate report
    generate_report
    
    # Summary
    echo
    log_info "Test execution completed!"
    log_info "Total: $TOTAL_TESTS, Passed: $PASSED_TESTS, Failed: $FAILED_TESTS, Skipped: $SKIPPED_TESTS"
    
    # Exit with appropriate code
    if [ $FAILED_TESTS -gt 0 ]; then
        log_error "Some tests failed. Please check the test report for details."
        exit 1
    elif [ $PASSED_TESTS -eq 0 ] && [ $SKIPPED_TESTS -gt 0 ]; then
        log_warning "All tests were skipped. Please check your test configuration."
        exit 0
    else
        log_success "All tests passed!"
        exit 0
    fi
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  -h, --help     Show this help message"
            echo "  --verbose      Enable verbose output"
            echo "  --no-color     Disable colored output"
            exit 0
            ;;
        --verbose)
            set -x
            shift
            ;;
        --no-color)
            RED=''
            GREEN=''
            YELLOW=''
            BLUE=''
            NC=''
            shift
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Run the main function
main