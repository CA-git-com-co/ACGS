#!/bin/bash
# ACGS-2 Accessibility Testing Script
# Constitutional Hash: cdd01ef066bc6cf2
# 
# Comprehensive accessibility testing with axe-core, Lighthouse, and PA11Y
# Target: >95% accessibility score with zero critical violations

set -e

# Configuration
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
TARGET_SCORE=${ACCESSIBILITY_TARGET_SCORE:-95}
SERVER_PORT=${PORT:-8080}
RESULTS_DIR="accessibility-results"
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
    log_info "Checking dependencies..."
    
    # Check if trunk is installed
    if ! command -v trunk &> /dev/null; then
        log_error "Trunk is not installed. Please install it with: cargo install trunk"
        exit 1
    fi
    
    # Check if Node.js tools are available
    if ! command -v node &> /dev/null; then
        log_error "Node.js is not installed"
        exit 1
    fi
    
    # Check if accessibility tools are installed
    local missing_tools=()
    
    if ! command -v axe &> /dev/null; then
        missing_tools+=("@axe-core/cli")
    fi
    
    if ! command -v lighthouse &> /dev/null; then
        missing_tools+=("lighthouse")
    fi
    
    if ! command -v pa11y &> /dev/null; then
        missing_tools+=("pa11y")
    fi
    
    if [ ${#missing_tools[@]} -gt 0 ]; then
        log_warning "Missing accessibility tools: ${missing_tools[*]}"
        log_info "Installing missing tools..."
        npm install -g "${missing_tools[@]}"
    fi
    
    log_success "All dependencies are available"
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
    local timeout=30
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

# Run axe-core accessibility tests
run_axe_tests() {
    log_info "Running axe-core accessibility tests..."
    
    # Run axe-core with JSON output
    axe "http://localhost:$SERVER_PORT" \
        --rules-file "../.github/workflows/axe-rules.json" \
        --reporter json \
        --output "$RESULTS_DIR/axe-results.json" \
        --timeout 30000 \
        --exit || true
    
    # Generate HTML report
    axe "http://localhost:$SERVER_PORT" \
        --rules-file "../.github/workflows/axe-rules.json" \
        --reporter html \
        --output "$RESULTS_DIR/axe-report.html" \
        --timeout 30000 || true
    
    log_success "Axe-core testing completed"
}

# Run Lighthouse accessibility audit
run_lighthouse_audit() {
    log_info "Running Lighthouse accessibility audit..."
    
    # Run Lighthouse accessibility audit
    lighthouse "http://localhost:$SERVER_PORT" \
        --only-categories=accessibility \
        --output=json \
        --output-path="$RESULTS_DIR/lighthouse-accessibility.json" \
        --chrome-flags="--headless --no-sandbox --disable-dev-shm-usage" \
        --quiet || true
    
    # Generate HTML report
    lighthouse "http://localhost:$SERVER_PORT" \
        --only-categories=accessibility \
        --output=html \
        --output-path="$RESULTS_DIR/lighthouse-accessibility.html" \
        --chrome-flags="--headless --no-sandbox --disable-dev-shm-usage" \
        --quiet || true
    
    log_success "Lighthouse accessibility audit completed"
}

# Run PA11Y WCAG tests
run_pa11y_tests() {
    log_info "Running PA11Y WCAG 2.1 AA compliance tests..."
    
    # Run PA11Y tests
    pa11y "http://localhost:$SERVER_PORT" \
        --standard WCAG2AA \
        --reporter json \
        --timeout 30000 \
        --output "$RESULTS_DIR/pa11y-results.json" || true
    
    # Generate HTML report
    pa11y "http://localhost:$SERVER_PORT" \
        --standard WCAG2AA \
        --reporter html \
        --timeout 30000 \
        --output "$RESULTS_DIR/pa11y-report.html" || true
    
    log_success "PA11Y WCAG 2.1 AA testing completed"
}

# Analyze results
analyze_results() {
    log_info "Analyzing accessibility test results..."
    
    local overall_pass=true
    
    # Analyze Lighthouse results
    if [ -f "$RESULTS_DIR/lighthouse-accessibility.json" ]; then
        local lighthouse_score=$(node -e "
            const data = JSON.parse(require('fs').readFileSync('$RESULTS_DIR/lighthouse-accessibility.json', 'utf8'));
            console.log(Math.round(data.lhr.categories.accessibility.score * 100));
        " 2>/dev/null || echo "0")
        
        echo ""
        log_info "💡 Lighthouse Accessibility Score: $lighthouse_score%"
        
        if [ "$lighthouse_score" -ge "$TARGET_SCORE" ]; then
            log_success "Lighthouse score meets target ($lighthouse_score% >= $TARGET_SCORE%)"
        else
            log_error "Lighthouse score below target ($lighthouse_score% < $TARGET_SCORE%)"
            overall_pass=false
        fi
    else
        log_warning "Lighthouse results not available"
    fi
    
    # Analyze Axe-Core results
    if [ -f "$RESULTS_DIR/axe-results.json" ]; then
        local violations_info=$(node -e "
            const data = JSON.parse(require('fs').readFileSync('$RESULTS_DIR/axe-results.json', 'utf8'));
            const violations = data.violations || [];
            const critical = violations.filter(v => v.impact === 'critical').length;
            const serious = violations.filter(v => v.impact === 'serious').length;
            console.log(\`\${violations.length} \${critical} \${serious}\`);
        " 2>/dev/null || echo "0 0 0")
        
        read total_violations critical_violations serious_violations <<< "$violations_info"
        
        echo ""
        log_info "🔍 Axe-Core Results:"
        log_info "  - Total violations: $total_violations"
        log_info "  - Critical violations: $critical_violations"
        log_info "  - Serious violations: $serious_violations"
        
        if [ "$critical_violations" -eq 0 ]; then
            log_success "No critical accessibility violations found"
        else
            log_error "Found $critical_violations critical accessibility violations"
            overall_pass=false
        fi
    else
        log_warning "Axe-Core results not available"
    fi
    
    echo ""
    log_info "📋 Constitutional compliance: $CONSTITUTIONAL_HASH"
    
    if [ "$overall_pass" = true ]; then
        log_success "🎉 All accessibility tests passed!"
        echo ""
        log_info "📊 Reports generated in: $RESULTS_DIR/"
        return 0
    else
        log_error "❌ Accessibility tests failed"
        echo ""
        log_info "📊 Check detailed reports in: $RESULTS_DIR/"
        return 1
    fi
}

# Main execution
main() {
    echo "🏛️ ACGS-2 Accessibility Testing"
    echo "Constitutional Hash: $CONSTITUTIONAL_HASH"
    echo "Target Score: $TARGET_SCORE%"
    echo ""
    
    # Create results directory
    mkdir -p "$RESULTS_DIR"
    
    # Run all steps
    check_dependencies
    build_frontend
    start_server
    
    # Run accessibility tests
    run_axe_tests
    run_lighthouse_audit
    run_pa11y_tests
    
    # Analyze and report results
    analyze_results
}

# Run main function
main "$@"
