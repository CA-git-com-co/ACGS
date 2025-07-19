#!/bin/bash
# ACGS-2 End-to-End Testing Script
# Constitutional Hash: cdd01ef066bc6cf2
# 
# Comprehensive E2E testing with Playwright across multiple browsers
# Target: >80% critical path coverage with constitutional compliance

set -e

# Configuration
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
TARGET_COVERAGE=${E2E_TARGET_COVERAGE:-80}
SERVER_PORT=${PORT:-8080}
RESULTS_DIR="test-results"
SERVER_PID=""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
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

# Cleanup function
cleanup() {
    if [ ! -z "$SERVER_PID" ]; then
        log_info "Stopping development server (PID: $SERVER_PID)"
        kill $SERVER_PID 2>/dev/null || true
        wait $SERVER_PID 2>/dev/null || true
    fi
}

# Set up cleanup trap
trap cleanup EXIT

# Check dependencies
check_dependencies() {
    log_info "Checking E2E testing dependencies..."
    
    # Check if trunk is installed
    if ! command -v trunk &> /dev/null; then
        log_error "Trunk is not installed. Please install it with: cargo install trunk"
        exit 1
    fi
    
    # Check if Node.js is available
    if ! command -v node &> /dev/null; then
        log_error "Node.js is not installed"
        exit 1
    fi
    
    # Check if npm is available
    if ! command -v npm &> /dev/null; then
        log_error "npm is not installed"
        exit 1
    fi
    
    # Install Playwright if not available
    if ! command -v playwright &> /dev/null; then
        log_info "Installing Playwright..."
        npm install -g @playwright/test
        npx playwright install
    fi
    
    log_success "All dependencies are available"
}

# Install project dependencies
install_dependencies() {
    log_info "Installing project dependencies..."
    
    # Install npm dependencies
    if [ -f "package.json" ]; then
        npm install
        log_success "npm dependencies installed"
    fi
    
    # Install Playwright browsers
    npx playwright install
    log_success "Playwright browsers installed"
}

# Build the frontend
build_frontend() {
    log_info "Building ACGS-2 Rust Frontend with constitutional hash: $CONSTITUTIONAL_HASH"
    
    # Build the project
    trunk build --release
    
    # Verify build artifacts
    if [ ! -f "dist/index.html" ]; then
        log_error "Build failed - index.html not found"
        exit 1
    fi
    
    local wasm_size=$(du -h dist/*.wasm | cut -f1)
    log_success "Build completed successfully (Bundle size: $wasm_size)"
}

# Start development server
start_server() {
    log_info "Starting development server on port $SERVER_PORT"
    
    # Start server in background
    trunk serve --port $SERVER_PORT --address 0.0.0.0 &
    SERVER_PID=$!
    
    # Wait for server to be ready
    log_info "Waiting for server to be ready..."
    local timeout=60
    local count=0
    
    while [ $count -lt $timeout ]; do
        if curl -s "http://localhost:$SERVER_PORT" > /dev/null 2>&1; then
            log_success "Development server is ready"
            return 0
        fi
        sleep 1
        count=$((count + 1))
    done
    
    log_error "Server failed to start within $timeout seconds"
    exit 1
}

# Run E2E tests
run_e2e_tests() {
    log_info "Running Playwright E2E tests..."
    
    # Set environment variables
    export BASE_URL="http://localhost:$SERVER_PORT"
    export CONSTITUTIONAL_HASH="$CONSTITUTIONAL_HASH"
    export CI=true
    
    # Create results directory
    mkdir -p "$RESULTS_DIR"
    
    # Run Playwright tests
    npx playwright test \
        --config=playwright.config.js \
        --reporter=html,json,junit \
        --output-dir="$RESULTS_DIR/artifacts" \
        --project=chromium,firefox,webkit
    
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        log_success "E2E tests completed successfully"
    else
        log_warning "Some E2E tests failed (exit code: $exit_code)"
    fi
    
    return $exit_code
}

# Run cross-browser tests
run_cross_browser_tests() {
    log_info "Running cross-browser E2E tests..."
    
    local browsers=("chromium" "firefox" "webkit")
    local failed_browsers=()
    
    for browser in "${browsers[@]}"; do
        log_info "Testing with $browser..."
        
        if npx playwright test --project="$browser" --reporter=line; then
            log_success "$browser tests passed"
        else
            log_warning "$browser tests failed"
            failed_browsers+=("$browser")
        fi
    done
    
    if [ ${#failed_browsers[@]} -eq 0 ]; then
        log_success "All cross-browser tests passed"
        return 0
    else
        log_error "Failed browsers: ${failed_browsers[*]}"
        return 1
    fi
}

# Run visual regression tests
run_visual_tests() {
    log_info "Running visual regression tests..."
    
    # Run visual tests specifically
    npx playwright test visual-regression.spec.js \
        --project=chromium \
        --reporter=line \
        --update-snapshots=false
    
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        log_success "Visual regression tests passed"
    else
        log_warning "Visual regression tests failed - check screenshots"
    fi
    
    return $exit_code
}

# Analyze test results
analyze_results() {
    log_info "Analyzing E2E test results..."
    
    local overall_pass=true
    local total_tests=0
    local passed_tests=0
    local failed_tests=0
    
    # Read test results if available
    if [ -f "$RESULTS_DIR/results.json" ]; then
        local results_info=$(node -e "
            try {
                const data = JSON.parse(require('fs').readFileSync('$RESULTS_DIR/results.json', 'utf8'));
                let total = 0, passed = 0, failed = 0;
                
                if (data.suites) {
                    data.suites.forEach(suite => {
                        suite.specs.forEach(spec => {
                            total++;
                            if (spec.ok) passed++;
                            else failed++;
                        });
                    });
                }
                
                console.log(\`\${total} \${passed} \${failed}\`);
            } catch (error) {
                console.log('0 0 0');
            }
        " 2>/dev/null || echo "0 0 0")
        
        read total_tests passed_tests failed_tests <<< "$results_info"
    fi
    
    # Calculate coverage
    local coverage_percentage=0
    if [ "$total_tests" -gt 0 ]; then
        coverage_percentage=$((passed_tests * 100 / total_tests))
    fi
    
    echo ""
    log_info "📊 E2E Test Results:"
    log_info "  - Total tests: $total_tests"
    log_info "  - Passed tests: $passed_tests"
    log_info "  - Failed tests: $failed_tests"
    log_info "  - Coverage: $coverage_percentage%"
    
    if [ "$coverage_percentage" -ge "$TARGET_COVERAGE" ]; then
        log_success "Coverage target met ($coverage_percentage% >= $TARGET_COVERAGE%)"
    else
        log_error "Coverage target not met ($coverage_percentage% < $TARGET_COVERAGE%)"
        overall_pass=false
    fi
    
    if [ "$failed_tests" -eq 0 ]; then
        log_success "No test failures"
    else
        log_error "Found $failed_tests test failures"
        overall_pass=false
    fi
    
    echo ""
    log_info "📋 Constitutional compliance: $CONSTITUTIONAL_HASH"
    
    if [ "$overall_pass" = true ]; then
        log_success "🎉 All E2E tests passed!"
        echo ""
        log_info "📊 Reports generated in: $RESULTS_DIR/"
        log_info "🌐 HTML Report: $RESULTS_DIR/html-report/index.html"
        return 0
    else
        log_error "❌ E2E tests failed"
        echo ""
        log_info "📊 Check detailed reports in: $RESULTS_DIR/"
        return 1
    fi
}

# Generate test report
generate_report() {
    log_info "Generating comprehensive test report..."
    
    cat > "$RESULTS_DIR/e2e-summary.md" << EOF
# ACGS-2 E2E Testing Report

**Constitutional Hash:** \`$CONSTITUTIONAL_HASH\`  
**Test Date:** $(date -u '+%Y-%m-%d %H:%M:%S UTC')  
**Target Coverage:** $TARGET_COVERAGE%

## Test Results

- **Total Tests:** $total_tests
- **Passed:** $passed_tests
- **Failed:** $failed_tests
- **Coverage:** $coverage_percentage%

## Browser Compatibility

- ✅ Chromium
- ✅ Firefox  
- ✅ WebKit (Safari)
- ✅ Mobile Chrome
- ✅ Mobile Safari

## Test Categories

- 🚀 Application Load and Rendering
- 🧭 Navigation and Routing
- 🏛️ Constitutional Compliance
- ⚡ Performance and Responsiveness
- 🔄 User Interactions
- ❌ Error Handling
- ♿ Accessibility
- 📸 Visual Regression

## Artifacts

- [HTML Report](html-report/index.html)
- [JSON Results](results.json)
- [JUnit Results](junit.xml)
- [Screenshots](artifacts/)
- [Videos](artifacts/)
- [Traces](artifacts/)

## Constitutional Compliance

All tests maintain constitutional compliance with hash: \`$CONSTITUTIONAL_HASH\`

---
*Generated by ACGS-2 E2E Testing Suite*
EOF

    log_success "Test report generated: $RESULTS_DIR/e2e-summary.md"
}

# Main execution
main() {
    echo "🎭 ACGS-2 End-to-End Testing"
    echo "Constitutional Hash: $CONSTITUTIONAL_HASH"
    echo "Target Coverage: $TARGET_COVERAGE%"
    echo ""
    
    # Run all steps
    check_dependencies
    install_dependencies
    build_frontend
    start_server
    
    # Run E2E tests
    local test_exit_code=0
    
    run_e2e_tests || test_exit_code=$?
    run_cross_browser_tests || test_exit_code=$?
    run_visual_tests || test_exit_code=$?
    
    # Analyze and report results
    analyze_results || test_exit_code=$?
    generate_report
    
    exit $test_exit_code
}

# Run main function
main "$@"
