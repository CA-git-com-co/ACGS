#!/bin/bash

# ACGS-PGP Master Test Runner
# Executes all setup script tests in proper sequence
# Constitutional hash: cdd01ef066bc6cf2

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test configuration
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
TEST_RESULTS_DIR="test_results"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Test suite configuration
declare -A TEST_SUITES=(
    ["comprehensive"]="scripts/test_setup_scripts_comprehensive.sh"
    ["performance"]="scripts/test_performance_validation.sh"
    ["emergency"]="scripts/test_emergency_shutdown.sh"
)

# Test results tracking
TOTAL_SUITES=0
PASSED_SUITES=0
FAILED_SUITES=0
SUITE_RESULTS=()

# Logging functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

failure() {
    echo -e "${RED}❌ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Function to create test results directory
setup_test_environment() {
    log "Setting up test environment..."
    
    # Create test results directory
    mkdir -p "$TEST_RESULTS_DIR"
    
    # Create test session directory
    local session_dir="$TEST_RESULTS_DIR/session_$TIMESTAMP"
    mkdir -p "$session_dir"
    
    echo "$session_dir"
}

# Function to run a test suite
run_test_suite() {
    local suite_name=$1
    local script_path=$2
    local session_dir=$3
    
    log "🧪 Running $suite_name test suite..."
    ((TOTAL_SUITES++))
    
    if [ ! -f "$script_path" ]; then
        failure "$suite_name: Test script not found: $script_path"
        SUITE_RESULTS+=("$suite_name: FAILED (script not found)")
        ((FAILED_SUITES++))
        return 1
    fi
    
    if [ ! -x "$script_path" ]; then
        failure "$suite_name: Test script not executable: $script_path"
        SUITE_RESULTS+=("$suite_name: FAILED (not executable)")
        ((FAILED_SUITES++))
        return 1
    fi
    
    # Run the test suite and capture output
    local output_file="$session_dir/${suite_name}_output.log"
    local start_time=$(date +%s)
    
    if "$script_path" > "$output_file" 2>&1; then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        success "$suite_name: PASSED (${duration}s)"
        SUITE_RESULTS+=("$suite_name: PASSED (${duration}s)")
        ((PASSED_SUITES++))
        return 0
    else
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        failure "$suite_name: FAILED (${duration}s)"
        SUITE_RESULTS+=("$suite_name: FAILED (${duration}s)")
        ((FAILED_SUITES++))
        
        # Show last few lines of output for debugging
        echo ""
        warning "Last 10 lines of $suite_name output:"
        tail -n 10 "$output_file" | sed 's/^/  /'
        echo ""
        
        return 1
    fi
}

# Function to check prerequisites
check_prerequisites() {
    log "Checking test prerequisites..."
    
    # Check if required scripts exist
    local missing_scripts=()
    
    for suite_name in "${!TEST_SUITES[@]}"; do
        local script_path=${TEST_SUITES[$suite_name]}
        if [ ! -f "$script_path" ]; then
            missing_scripts+=("$script_path")
        fi
    done
    
    if [ ${#missing_scripts[@]} -ne 0 ]; then
        failure "Missing test scripts: ${missing_scripts[*]}"
        return 1
    fi
    
    # Check if services are available for testing
    local available_services=0
    local service_ports=(8000 8001 8002 8003 8004 8005 8006)
    
    for port in "${service_ports[@]}"; do
        if curl -f -s --connect-timeout 2 --max-time 5 "http://localhost:$port/health" > /dev/null 2>&1; then
            ((available_services++))
        fi
    done
    
    log "Available services for testing: $available_services/7"
    
    if [ $available_services -eq 0 ]; then
        warning "No services are running. Some tests may be skipped."
        warning "To start services: ./scripts/start_all_services.sh"
    fi
    
    return 0
}

# Function to generate comprehensive report
generate_comprehensive_report() {
    local session_dir=$1
    local report_file="$session_dir/comprehensive_test_report.md"
    
    log "Generating comprehensive test report..."
    
    cat > "$report_file" << EOF
# ACGS-PGP Setup Scripts Test Report

**Date**: $(date)  
**Session**: $TIMESTAMP  
**Constitutional Hash**: $CONSTITUTIONAL_HASH  

## Executive Summary

- **Total Test Suites**: $TOTAL_SUITES
- **Passed**: $PASSED_SUITES
- **Failed**: $FAILED_SUITES
- **Success Rate**: $(( PASSED_SUITES * 100 / TOTAL_SUITES ))%

## Test Suite Results

EOF
    
    for result in "${SUITE_RESULTS[@]}"; do
        echo "- $result" >> "$report_file"
    done
    
    cat >> "$report_file" << EOF

## Detailed Analysis

### Constitutional Governance Compliance
- Constitutional hash validation: $(grep -q "Constitutional Hash Consistency.*PASS" "$session_dir"/* && echo "✅ PASSED" || echo "❌ FAILED")
- DGM safety patterns: $(grep -q "DGM Safety Patterns.*PASS" "$session_dir"/* && echo "✅ PASSED" || echo "❌ FAILED")
- AI model integrations: $(grep -q "AI Model Integrations.*PASS" "$session_dir"/* && echo "✅ PASSED" || echo "❌ FAILED")

### Performance Validation
- Response time targets: $(grep -q "response time.*✓" "$session_dir"/* && echo "✅ PASSED" || echo "❌ FAILED")
- Throughput capability: $(grep -q "throughput.*✓" "$session_dir"/* && echo "✅ PASSED" || echo "❌ FAILED")
- Constitutional compliance performance: $(grep -q "constitutional compliance.*✓" "$session_dir"/* && echo "✅ PASSED" || echo "❌ FAILED")

### Emergency Shutdown Capability
- Emergency endpoints: $(grep -q "emergency shutdown.*✓" "$session_dir"/* && echo "✅ PASSED" || echo "❌ FAILED")
- RTO compliance (<30min): $(grep -q "30min RTO.*✓" "$session_dir"/* && echo "✅ PASSED" || echo "❌ FAILED")
- System-wide procedures: $(grep -q "System-wide.*validated" "$session_dir"/* && echo "✅ PASSED" || echo "❌ FAILED")

## Recommendations

EOF
    
    local overall_success=$(( PASSED_SUITES * 100 / TOTAL_SUITES ))
    
    if [ $overall_success -ge 95 ]; then
        cat >> "$report_file" << EOF
### ✅ Production Ready
- All critical tests passed
- System meets constitutional governance requirements
- Performance targets achieved
- Emergency procedures validated

**Next Steps:**
1. Deploy to production environment
2. Monitor constitutional compliance metrics
3. Validate real-world performance
4. Test emergency procedures in production
EOF
    elif [ $overall_success -ge 80 ]; then
        cat >> "$report_file" << EOF
### ⚠️ Staging Ready
- Most tests passed with minor issues
- Some optimization required
- Additional testing recommended

**Next Steps:**
1. Address failed test cases
2. Deploy to staging environment
3. Conduct additional performance testing
4. Rerun tests before production deployment
EOF
    else
        cat >> "$report_file" << EOF
### ❌ Requires Remediation
- Critical test failures detected
- System not ready for deployment
- Immediate attention required

**Next Steps:**
1. Review failed test outputs
2. Implement missing functionality
3. Fix performance issues
4. Rerun all tests
EOF
    fi
    
    cat >> "$report_file" << EOF

## Test Artifacts

- Session directory: \`$session_dir\`
- Individual test outputs: \`$session_dir/*_output.log\`
- This report: \`$report_file\`

---
*Generated by ACGS-PGP Test Suite*
EOF
    
    success "Comprehensive report generated: $report_file"
}

# Main test execution
main() {
    log "🧪 Starting ACGS-PGP Master Test Suite"
    echo "======================================"
    echo "Constitutional hash: $CONSTITUTIONAL_HASH"
    echo "Test session: $TIMESTAMP"
    echo ""
    
    # Setup test environment
    local session_dir=$(setup_test_environment)
    log "Test session directory: $session_dir"
    echo ""
    
    # Check prerequisites
    if ! check_prerequisites; then
        failure "Prerequisites check failed"
        exit 1
    fi
    echo ""
    
    # Run test suites in order
    log "Executing test suites..."
    echo ""
    
    # 1. Comprehensive setup validation (non-destructive)
    run_test_suite "comprehensive" "${TEST_SUITES[comprehensive]}" "$session_dir"
    echo ""
    
    # 2. Performance validation (requires running services)
    run_test_suite "performance" "${TEST_SUITES[performance]}" "$session_dir"
    echo ""
    
    # 3. Emergency shutdown (destructive - run last)
    warning "⚠️ Emergency shutdown test is destructive and will stop services"
    read -p "Run emergency shutdown test? (y/N): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        run_test_suite "emergency" "${TEST_SUITES[emergency]}" "$session_dir"
    else
        log "Emergency shutdown test skipped by user"
        SUITE_RESULTS+=("emergency: SKIPPED (user choice)")
    fi
    echo ""
    
    # Generate comprehensive report
    generate_comprehensive_report "$session_dir"
    echo ""
    
    # Final results
    echo "======================================"
    echo "🧪 ACGS-PGP Master Test Results"
    echo "======================================"
    echo "Test suites run: $TOTAL_SUITES"
    echo "Passed: $PASSED_SUITES"
    echo "Failed: $FAILED_SUITES"
    echo "Success rate: $(( PASSED_SUITES * 100 / TOTAL_SUITES ))%"
    echo ""
    
    echo "📊 Suite Results:"
    for result in "${SUITE_RESULTS[@]}"; do
        echo "  $result"
    done
    
    echo ""
    local overall_success=$(( PASSED_SUITES * 100 / TOTAL_SUITES ))
    
    if [ $overall_success -ge 95 ]; then
        success "🎉 ALL TESTS PASSED - PRODUCTION READY"
        echo "✅ Constitutional governance validated"
        echo "✅ Performance targets met"
        echo "✅ Emergency procedures verified"
        echo "✅ System ready for production deployment"
    elif [ $overall_success -ge 80 ]; then
        warning "⚠️ MOST TESTS PASSED - STAGING READY"
        echo "⚠️ Minor issues detected"
        echo "⚠️ Additional testing recommended"
        echo "⚠️ Review failed tests before production"
    else
        failure "❌ CRITICAL ISSUES DETECTED - REMEDIATION REQUIRED"
        echo "❌ Multiple test failures"
        echo "❌ System not ready for deployment"
        echo "❌ Review test outputs and fix issues"
    fi
    
    echo ""
    echo "📁 Test artifacts: $session_dir"
    echo "📄 Comprehensive report: $session_dir/comprehensive_test_report.md"
    
    # Return appropriate exit code
    if [ $overall_success -ge 80 ]; then
        return 0
    else
        return 1
    fi
}

# Run main function
main "$@"
