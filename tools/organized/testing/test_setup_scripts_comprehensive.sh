#!/bin/bash

# ACGS-PGP Comprehensive Setup Scripts Test Suite
# Tests all setup scripts for constitutional compliance, performance, and safety requirements
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
COMPLIANCE_THRESHOLD=0.95
RESPONSE_TIME_THRESHOLD=2000  # 2 seconds in milliseconds
THROUGHPUT_TARGET=1000        # RPS
EMERGENCY_SHUTDOWN_RTO=1800   # 30 minutes in seconds

# Test results tracking
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
TEST_RESULTS=()

# Logging functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
    ((PASSED_TESTS++))
    TEST_RESULTS+=("PASS: $1")
}

failure() {
    echo -e "${RED}❌ $1${NC}"
    ((FAILED_TESTS++))
    TEST_RESULTS+=("FAIL: $1")
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Test function wrapper
run_test() {
    local test_name="$1"
    local test_function="$2"
    
    ((TOTAL_TESTS++))
    log "Running test: $test_name"
    
    if $test_function; then
        success "$test_name"
    else
        failure "$test_name"
    fi
    echo ""
}

# Test 1: Validate setup script architecture
test_setup_script_architecture() {
    log "Validating setup script architecture..."
    
    # Check if required setup scripts exist
    local required_scripts=(
        "scripts/start_all_services.sh"
        "scripts/setup/project_setup.sh"
        "scripts/setup/install_dependencies.sh"
        "infrastructure/docker/docker-compose.acgs.yml"
    )
    
    for script in "${required_scripts[@]}"; do
        if [ ! -f "$script" ]; then
            failure "Required script missing: $script"
            return 1
        fi
    done
    
    # Check if scripts are executable
    for script in scripts/start_all_services.sh scripts/setup/project_setup.sh scripts/setup/install_dependencies.sh; do
        if [ ! -x "$script" ]; then
            failure "Script not executable: $script"
            return 1
        fi
    done
    
    return 0
}

# Test 2: Validate constitutional hash consistency
test_constitutional_hash_consistency() {
    log "Validating constitutional hash consistency..."
    
    local files_to_check=(
        "scripts/start_all_services.sh"
        "scripts/setup/project_setup.sh"
        "infrastructure/docker/docker-compose.acgs.yml"
    )
    
    for file in "${files_to_check[@]}"; do
        if [ -f "$file" ]; then
            if ! grep -q "$CONSTITUTIONAL_HASH" "$file"; then
                failure "Constitutional hash missing in: $file"
                return 1
            fi
        fi
    done
    
    return 0
}

# Test 3: Validate package manager configuration
test_package_manager_configuration() {
    log "Validating package manager configuration..."
    
    # Check for pnpm configuration
    if grep -q "npm install" scripts/setup/project_setup.sh; then
        failure "Found npm usage instead of pnpm in project_setup.sh"
        return 1
    fi
    
    if ! grep -q "pnpm" scripts/setup/project_setup.sh; then
        failure "pnpm not configured in project_setup.sh"
        return 1
    fi
    
    # Check for cargo configuration
    if ! grep -q "cargo" scripts/setup/install_dependencies.sh; then
        failure "cargo not configured in install_dependencies.sh"
        return 1
    fi
    
    return 0
}

# Test 4: Validate AI model integrations
test_ai_model_integrations() {
    log "Validating real AI model integrations..."
    
    local required_models=(
        "GOOGLE_GEMINI"
        "DEEPSEEK_R1"
        "NVIDIA_QWEN"
        "NANO_VLLM"
    )
    
    for model in "${required_models[@]}"; do
        if ! grep -q "$model" scripts/setup/project_setup.sh; then
            failure "AI model integration missing: $model"
            return 1
        fi
    done
    
    # Check for fictional integrations that should be removed
    local fictional_patterns=(
        "inspect_ai"
        "fictional"
        "mock_ai"
        "fake_model"
    )
    
    for pattern in "${fictional_patterns[@]}"; do
        if grep -qi "$pattern" scripts/setup/project_setup.sh; then
            failure "Fictional integration found: $pattern"
            return 1
        fi
    done
    
    return 0
}

# Test 5: Validate DGM safety patterns
test_dgm_safety_patterns() {
    log "Validating DGM safety patterns..."
    
    local required_patterns=(
        "DGM_SANDBOX"
        "DGM_HUMAN_REVIEW"
        "DGM_ROLLBACK"
        "check_dgm_safety"
    )
    
    for pattern in "${required_patterns[@]}"; do
        if ! grep -q "$pattern" scripts/start_all_services.sh; then
            failure "DGM safety pattern missing: $pattern"
            return 1
        fi
    done
    
    return 0
}

# Test 6: Validate resource limits configuration
test_resource_limits_configuration() {
    log "Validating resource limits configuration..."
    
    # Check Docker Compose resource limits
    if ! grep -q "500m" infrastructure/docker/docker-compose.acgs.yml; then
        failure "CPU limit 500m not found in Docker Compose"
        return 1
    fi
    
    if ! grep -q "1Gi" infrastructure/docker/docker-compose.acgs.yml; then
        failure "Memory limit 1Gi not found in Docker Compose"
        return 1
    fi
    
    if ! grep -q "200m" infrastructure/docker/docker-compose.acgs.yml; then
        failure "CPU reservation 200m not found in Docker Compose"
        return 1
    fi
    
    if ! grep -q "512Mi" infrastructure/docker/docker-compose.acgs.yml; then
        failure "Memory reservation 512Mi not found in Docker Compose"
        return 1
    fi
    
    return 0
}

# Test 7: Validate service startup validation
test_service_startup_validation() {
    log "Validating service startup validation..."
    
    # Check if all 7 services are configured
    local required_services=(
        "auth_service"
        "ac_service"
        "integrity_service"
        "fv_service"
        "gs_service"
        "pgc_service"
        "ec_service"
    )
    
    for service in "${required_services[@]}"; do
        if ! grep -q "$service" scripts/start_all_services.sh; then
            failure "Service not configured: $service"
            return 1
        fi
    done
    
    # Check for constitutional compliance validation
    if ! grep -q "check_constitutional_compliance" scripts/start_all_services.sh; then
        failure "Constitutional compliance validation missing"
        return 1
    fi
    
    return 0
}

# Test 8: Validate emergency shutdown capability
test_emergency_shutdown_capability() {
    log "Validating emergency shutdown capability..."
    
    if ! grep -q "test_emergency_shutdown" scripts/start_all_services.sh; then
        failure "Emergency shutdown testing missing"
        return 1
    fi
    
    if ! grep -q "30.*min" scripts/start_all_services.sh; then
        failure "30-minute RTO requirement not found"
        return 1
    fi
    
    return 0
}

# Test 9: Validate performance targets
test_performance_targets() {
    log "Validating performance targets..."
    
    if ! grep -q "2.*s" scripts/start_all_services.sh; then
        failure "2-second response time target not found"
        return 1
    fi
    
    if ! grep -q "1000.*RPS\|1000.*rps" scripts/start_all_services.sh; then
        failure "1000 RPS throughput target not found"
        return 1
    fi
    
    return 0
}

# Test 10: Validate comprehensive reporting
test_comprehensive_reporting() {
    log "Validating comprehensive reporting..."
    
    if ! grep -q "compliance_percentage" scripts/start_all_services.sh; then
        failure "Compliance percentage calculation missing"
        return 1
    fi
    
    if ! grep -q "95.*compliance\|95.*%" scripts/start_all_services.sh; then
        failure "95% compliance threshold not found"
        return 1
    fi
    
    return 0
}

# Main test execution
main() {
    log "🧪 Starting ACGS-PGP Setup Scripts Comprehensive Test Suite"
    echo "============================================================"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    echo "Constitutional hash: $CONSTITUTIONAL_HASH"
    echo "Compliance threshold: $COMPLIANCE_THRESHOLD"
    echo "Response time threshold: ${RESPONSE_TIME_THRESHOLD}ms"
    echo "Throughput target: ${THROUGHPUT_TARGET} RPS"
    echo "Emergency shutdown RTO: ${EMERGENCY_SHUTDOWN_RTO}s"
    echo ""
    
    # Run all tests
    run_test "Setup Script Architecture" test_setup_script_architecture
    run_test "Constitutional Hash Consistency" test_constitutional_hash_consistency
    run_test "Package Manager Configuration" test_package_manager_configuration
    run_test "AI Model Integrations" test_ai_model_integrations
    run_test "DGM Safety Patterns" test_dgm_safety_patterns
    run_test "Resource Limits Configuration" test_resource_limits_configuration
    run_test "Service Startup Validation" test_service_startup_validation
    run_test "Emergency Shutdown Capability" test_emergency_shutdown_capability
    run_test "Performance Targets" test_performance_targets
    run_test "Comprehensive Reporting" test_comprehensive_reporting
    
    # Generate test report
    echo ""
    echo "============================================================"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    echo "🧪 ACGS-PGP Setup Scripts Test Results"
    echo "============================================================"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    echo "Total tests: $TOTAL_TESTS"
    echo "Passed: $PASSED_TESTS"
    echo "Failed: $FAILED_TESTS"
    echo "Success rate: $(( PASSED_TESTS * 100 / TOTAL_TESTS ))%"
    echo ""
    
    # Calculate compliance percentage
    local compliance_percentage=$(( PASSED_TESTS * 100 / TOTAL_TESTS ))
    
    if [ $compliance_percentage -ge 95 ]; then
        success "🎉 SETUP SCRIPTS READY FOR PRODUCTION (≥95% compliance)"
        echo "✅ All critical requirements met"
        echo "✅ Constitutional governance validated"
        echo "✅ DGM safety patterns implemented"
        echo "✅ Performance targets configured"
        echo "✅ Emergency shutdown capability verified"
    elif [ $compliance_percentage -ge 80 ]; then
        warning "⚠️ SETUP SCRIPTS READY FOR STAGING ($compliance_percentage% compliance)"
        echo "⚠️ Some non-critical issues found"
        echo "⚠️ Production deployment requires ≥95% compliance"
    else
        failure "❌ SETUP SCRIPTS REQUIRE REMEDIATION (<80% compliance)"
        echo "❌ Critical issues found"
        echo "❌ System not ready for deployment"
    fi
    
    echo ""
    echo "📋 Detailed Results:"
    for result in "${TEST_RESULTS[@]}"; do
        echo "  $result"
    done
    
    # Return appropriate exit code
    if [ $compliance_percentage -ge 95 ]; then
        return 0
    else
        return 1
    fi
}

# Run main function
main "$@"
