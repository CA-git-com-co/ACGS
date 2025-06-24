#!/bin/bash
# Constitutional Trainer Staging Smoke Tests
#
# Comprehensive smoke tests for validating the Constitutional Trainer Service
# deployment in the staging environment.
#
# Usage:
#   ./staging-smoke-tests.sh [OPTIONS]

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
STAGING_NAMESPACE="${STAGING_NAMESPACE:-acgs-staging}"
TIMEOUT="${TIMEOUT:-300}"
RESULTS_DIR="${RESULTS_DIR:-./smoke-test-results}"

# Service endpoints
CONSTITUTIONAL_TRAINER_URL="http://localhost:8000"
POLICY_ENGINE_URL="http://localhost:8001"
AUDIT_ENGINE_URL="http://localhost:8003"
REDIS_URL="redis://localhost:6379"

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

# Test results tracking
TESTS_TOTAL=0
TESTS_PASSED=0
TESTS_FAILED=0
FAILED_TESTS=()

# Help function
show_help() {
    cat << EOF
Constitutional Trainer Staging Smoke Tests

This script runs comprehensive smoke tests to validate the Constitutional Trainer Service
deployment in the staging environment.

Usage:
    $0 [OPTIONS]

Options:
    --namespace NAME        Staging namespace (default: acgs-staging)
    --timeout SECONDS       Test timeout (default: 300)
    --results-dir DIR       Results output directory (default: ./smoke-test-results)
    --skip-port-forward    Skip automatic port forwarding setup
    --verbose              Enable verbose output
    --help                 Show this help message

Examples:
    # Run all smoke tests
    $0

    # Run with custom namespace
    $0 --namespace acgs-staging-v2

    # Run with verbose output
    $0 --verbose

Environment Variables:
    STAGING_NAMESPACE      Staging namespace override
    KUBECONFIG            Kubernetes configuration file

EOF
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --namespace)
                STAGING_NAMESPACE="$2"
                shift 2
                ;;
            --timeout)
                TIMEOUT="$2"
                shift 2
                ;;
            --results-dir)
                RESULTS_DIR="$2"
                shift 2
                ;;
            --skip-port-forward)
                SKIP_PORT_FORWARD=true
                shift
                ;;
            --verbose)
                VERBOSE=true
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

# Setup test environment
setup_test_environment() {
    log_info "Setting up smoke test environment..."
    
    # Create results directory
    mkdir -p "$RESULTS_DIR"
    
    # Check kubectl connectivity
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi
    
    # Check if namespace exists
    if ! kubectl get namespace "$STAGING_NAMESPACE" &> /dev/null; then
        log_error "Staging namespace not found: $STAGING_NAMESPACE"
        exit 1
    fi
    
    # Setup port forwarding if not skipped
    if [[ "${SKIP_PORT_FORWARD:-false}" != "true" ]]; then
        setup_port_forwarding
    fi
    
    log_success "Test environment setup completed"
}

# Setup port forwarding
setup_port_forwarding() {
    log_info "Setting up port forwarding..."
    
    # Kill any existing port forwards
    pkill -f "kubectl port-forward" || true
    sleep 2
    
    # Start port forwards
    kubectl port-forward -n "$STAGING_NAMESPACE" svc/constitutional-trainer 8000:8000 &
    CT_PF_PID=$!
    
    kubectl port-forward -n "$STAGING_NAMESPACE" svc/policy-engine 8001:8001 &
    PE_PF_PID=$!
    
    kubectl port-forward -n "$STAGING_NAMESPACE" svc/audit-engine 8003:8003 &
    AE_PF_PID=$!
    
    kubectl port-forward -n "$STAGING_NAMESPACE" svc/redis 6379:6379 &
    REDIS_PF_PID=$!
    
    # Wait for port forwards to be established
    sleep 10
    
    log_success "Port forwarding established"
}

# Cleanup port forwarding
cleanup_port_forwarding() {
    log_info "Cleaning up port forwarding..."
    
    for pid in "${CT_PF_PID:-}" "${PE_PF_PID:-}" "${AE_PF_PID:-}" "${REDIS_PF_PID:-}"; do
        if [[ -n "$pid" ]]; then
            kill "$pid" 2>/dev/null || true
        fi
    done
    
    # Additional cleanup
    pkill -f "kubectl port-forward" || true
}

# Test helper functions
run_test() {
    local test_name="$1"
    local test_function="$2"
    
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    
    log_info "Running test: $test_name"
    
    if [[ "${VERBOSE:-false}" == "true" ]]; then
        if $test_function; then
            TESTS_PASSED=$((TESTS_PASSED + 1))
            log_success "✅ $test_name PASSED"
        else
            TESTS_FAILED=$((TESTS_FAILED + 1))
            FAILED_TESTS+=("$test_name")
            log_error "❌ $test_name FAILED"
        fi
    else
        if $test_function &> /dev/null; then
            TESTS_PASSED=$((TESTS_PASSED + 1))
            log_success "✅ $test_name PASSED"
        else
            TESTS_FAILED=$((TESTS_FAILED + 1))
            FAILED_TESTS+=("$test_name")
            log_error "❌ $test_name FAILED"
        fi
    fi
}

# Test 1: Service startup health checks
test_service_health_checks() {
    local services=("constitutional-trainer:8000" "policy-engine:8001" "audit-engine:8003")
    
    for service_port in "${services[@]}"; do
        local service_name="${service_port%:*}"
        local port="${service_port#*:}"
        
        if ! curl -f -s "http://localhost:$port/health" --max-time 10; then
            log_error "$service_name health check failed"
            return 1
        fi
    done
    
    return 0
}

# Test 2: Redis connectivity
test_redis_connectivity() {
    if command -v redis-cli &> /dev/null; then
        if ! redis-cli -h localhost -p 6379 ping | grep -q PONG; then
            return 1
        fi
    else
        # Test with netcat if redis-cli not available
        if ! nc -z localhost 6379; then
            return 1
        fi
    fi
    
    return 0
}

# Test 3: Constitutional Trainer API
test_constitutional_trainer_api() {
    local test_request='{
        "model_name": "smoke-test-model",
        "model_id": "smoke-test-001",
        "training_data": [
            {
                "prompt": "What is constitutional AI?",
                "response": "Constitutional AI is an approach to training AI systems to be helpful, harmless, and honest while respecting human values and constitutional principles."
            }
        ],
        "lora_config": {
            "r": 16,
            "lora_alpha": 32,
            "target_modules": ["q_proj", "v_proj"],
            "lora_dropout": 0.1
        },
        "privacy_config": {
            "enable_differential_privacy": true,
            "epsilon": 8.0,
            "delta": 1e-5
        }
    }'
    
    local response=$(curl -f -s -X POST \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer smoke-test-token" \
        -d "$test_request" \
        "$CONSTITUTIONAL_TRAINER_URL/api/v1/train" \
        --max-time 30)
    
    # Check if response contains training_id
    if ! echo "$response" | grep -q "training_id"; then
        return 1
    fi
    
    return 0
}

# Test 4: Policy Engine evaluation
test_policy_engine_evaluation() {
    local policy_request='{
        "action": "constitutional_training",
        "agent_id": "smoke-test-agent",
        "resource": {
            "type": "training_session",
            "constitutional_hash": "cdd01ef066bc6cf2"
        },
        "context": {
            "user_permissions": ["model_training"],
            "compliance_threshold": 0.95
        }
    }'
    
    local response=$(curl -f -s -X POST \
        -H "Content-Type: application/json" \
        -d "$policy_request" \
        "$POLICY_ENGINE_URL/v1/evaluate" \
        --max-time 10)
    
    # Check if response contains allow field
    if ! echo "$response" | grep -q "allow"; then
        return 1
    fi
    
    return 0
}

# Test 5: Audit Engine logging
test_audit_engine_logging() {
    local audit_request='{
        "service_name": "constitutional-trainer",
        "user_id": "smoke-test-user",
        "action": "training_started",
        "resource_id": "smoke-test-training-001",
        "details": {
            "model_name": "smoke-test-model",
            "constitutional_hash": "cdd01ef066bc6cf2",
            "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
        }
    }'
    
    local response=$(curl -f -s -X POST \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer internal-service-token" \
        -d "$audit_request" \
        "$AUDIT_ENGINE_URL/api/v1/audit" \
        --max-time 10)
    
    # Check if response contains audit ID
    if ! echo "$response" | grep -q "id"; then
        return 1
    fi
    
    return 0
}

# Test 6: Metrics endpoints
test_metrics_endpoints() {
    local services=("constitutional-trainer:8000" "policy-engine:8001")
    
    for service_port in "${services[@]}"; do
        local service_name="${service_port%:*}"
        local port="${service_port#*:}"
        
        local metrics=$(curl -f -s "http://localhost:$port/metrics" --max-time 10)
        
        # Check for basic Prometheus metrics
        if ! echo "$metrics" | grep -q "# HELP"; then
            log_error "$service_name metrics endpoint failed"
            return 1
        fi
    done
    
    return 0
}

# Test 7: Pod readiness and liveness
test_pod_readiness() {
    local deployments=("constitutional-trainer" "policy-engine" "audit-engine" "redis")
    
    for deployment in "${deployments[@]}"; do
        # Check if deployment is available
        local available=$(kubectl get deployment "$deployment" -n "$STAGING_NAMESPACE" \
            -o jsonpath='{.status.conditions[?(@.type=="Available")].status}' 2>/dev/null || echo "False")
        
        if [[ "$available" != "True" ]]; then
            log_error "$deployment deployment not available"
            return 1
        fi
        
        # Check if all replicas are ready
        local ready_replicas=$(kubectl get deployment "$deployment" -n "$STAGING_NAMESPACE" \
            -o jsonpath='{.status.readyReplicas}' 2>/dev/null || echo "0")
        local desired_replicas=$(kubectl get deployment "$deployment" -n "$STAGING_NAMESPACE" \
            -o jsonpath='{.spec.replicas}' 2>/dev/null || echo "1")
        
        if [[ "$ready_replicas" != "$desired_replicas" ]]; then
            log_error "$deployment: $ready_replicas/$desired_replicas replicas ready"
            return 1
        fi
    done
    
    return 0
}

# Test 8: Service discovery
test_service_discovery() {
    local services=("constitutional-trainer" "policy-engine" "audit-engine" "redis")
    
    for service in "${services[@]}"; do
        if ! kubectl get service "$service" -n "$STAGING_NAMESPACE" &> /dev/null; then
            log_error "Service $service not found"
            return 1
        fi
        
        # Check if service has endpoints
        local endpoints=$(kubectl get endpoints "$service" -n "$STAGING_NAMESPACE" \
            -o jsonpath='{.subsets[*].addresses[*].ip}' 2>/dev/null || echo "")
        
        if [[ -z "$endpoints" ]]; then
            log_error "Service $service has no endpoints"
            return 1
        fi
    done
    
    return 0
}

# Test 9: Configuration validation
test_configuration_validation() {
    # Check if ConfigMaps exist
    local configmaps=("constitutional-trainer-config")
    
    for cm in "${configmaps[@]}"; do
        if kubectl get configmap "$cm" -n "$STAGING_NAMESPACE" &> /dev/null; then
            # ConfigMap exists, validate content
            local config=$(kubectl get configmap "$cm" -n "$STAGING_NAMESPACE" -o yaml)
            
            # Check for required configuration keys
            if ! echo "$config" | grep -q "constitutional_hash"; then
                log_error "ConfigMap $cm missing constitutional_hash"
                return 1
            fi
        fi
    done
    
    return 0
}

# Test 10: Resource limits validation
test_resource_limits() {
    local deployments=("constitutional-trainer" "policy-engine" "audit-engine")
    
    for deployment in "${deployments[@]}"; do
        local limits=$(kubectl get deployment "$deployment" -n "$STAGING_NAMESPACE" \
            -o jsonpath='{.spec.template.spec.containers[0].resources.limits}' 2>/dev/null || echo "{}")
        
        if [[ "$limits" == "{}" ]]; then
            log_warning "$deployment has no resource limits defined"
        fi
    done
    
    return 0
}

# Generate test report
generate_test_report() {
    log_info "Generating smoke test report..."
    
    local report_file="$RESULTS_DIR/staging-smoke-test-report-$(date +%Y%m%d-%H%M%S).md"
    
    cat > "$report_file" << EOF
# Constitutional Trainer Staging Smoke Test Report

**Test Date:** $(date)  
**Namespace:** $STAGING_NAMESPACE  
**Total Tests:** $TESTS_TOTAL  
**Passed:** $TESTS_PASSED  
**Failed:** $TESTS_FAILED  
**Success Rate:** $(( TESTS_PASSED * 100 / TESTS_TOTAL ))%  

## Test Results Summary

| Test | Status |
|------|--------|
| Service Health Checks | $(if [[ " ${FAILED_TESTS[*]} " =~ " Service Health Checks " ]]; then echo "❌ FAILED"; else echo "✅ PASSED"; fi) |
| Redis Connectivity | $(if [[ " ${FAILED_TESTS[*]} " =~ " Redis Connectivity " ]]; then echo "❌ FAILED"; else echo "✅ PASSED"; fi) |
| Constitutional Trainer API | $(if [[ " ${FAILED_TESTS[*]} " =~ " Constitutional Trainer API " ]]; then echo "❌ FAILED"; else echo "✅ PASSED"; fi) |
| Policy Engine Evaluation | $(if [[ " ${FAILED_TESTS[*]} " =~ " Policy Engine Evaluation " ]]; then echo "❌ FAILED"; else echo "✅ PASSED"; fi) |
| Audit Engine Logging | $(if [[ " ${FAILED_TESTS[*]} " =~ " Audit Engine Logging " ]]; then echo "❌ FAILED"; else echo "✅ PASSED"; fi) |
| Metrics Endpoints | $(if [[ " ${FAILED_TESTS[*]} " =~ " Metrics Endpoints " ]]; then echo "❌ FAILED"; else echo "✅ PASSED"; fi) |
| Pod Readiness | $(if [[ " ${FAILED_TESTS[*]} " =~ " Pod Readiness " ]]; then echo "❌ FAILED"; else echo "✅ PASSED"; fi) |
| Service Discovery | $(if [[ " ${FAILED_TESTS[*]} " =~ " Service Discovery " ]]; then echo "❌ FAILED"; else echo "✅ PASSED"; fi) |
| Configuration Validation | $(if [[ " ${FAILED_TESTS[*]} " =~ " Configuration Validation " ]]; then echo "❌ FAILED"; else echo "✅ PASSED"; fi) |
| Resource Limits | $(if [[ " ${FAILED_TESTS[*]} " =~ " Resource Limits " ]]; then echo "❌ FAILED"; else echo "✅ PASSED"; fi) |

## Environment Status

### Deployments
\`\`\`
$(kubectl get deployments -n "$STAGING_NAMESPACE" 2>/dev/null || echo "No deployments found")
\`\`\`

### Services
\`\`\`
$(kubectl get services -n "$STAGING_NAMESPACE" 2>/dev/null || echo "No services found")
\`\`\`

### Pods
\`\`\`
$(kubectl get pods -n "$STAGING_NAMESPACE" 2>/dev/null || echo "No pods found")
\`\`\`

## Failed Tests

EOF

    if [[ ${#FAILED_TESTS[@]} -gt 0 ]]; then
        for test in "${FAILED_TESTS[@]}"; do
            echo "- $test" >> "$report_file"
        done
    else
        echo "No failed tests! 🎉" >> "$report_file"
    fi
    
    cat >> "$report_file" << EOF

## Recommendations

EOF

    if [[ $TESTS_FAILED -gt 0 ]]; then
        cat >> "$report_file" << EOF
1. **Address Failed Tests**: Investigate and resolve the failed test cases listed above
2. **Review Logs**: Check pod logs for any error messages or warnings
3. **Validate Configuration**: Ensure all configuration values are correct for staging
4. **Resource Monitoring**: Monitor resource usage and adjust limits if needed
5. **Re-run Tests**: Execute smoke tests again after fixes are applied

## Next Steps

1. Fix identified issues
2. Re-run smoke tests to validate fixes
3. Proceed with integration testing
4. Schedule load testing
5. Prepare for stakeholder sign-off

EOF
    else
        cat >> "$report_file" << EOF
1. **Proceed with Integration Testing**: All smoke tests passed, ready for comprehensive testing
2. **Schedule Load Testing**: Plan and execute performance testing
3. **Security Validation**: Run security scans and audits
4. **Stakeholder Sign-off**: Present results to stakeholders for approval
5. **Production Readiness**: Prepare for production deployment

## Staging Environment Ready! 🚀

All smoke tests have passed successfully. The staging environment is ready for:
- Integration testing
- Load testing
- Security validation
- Stakeholder review
- Production deployment preparation

EOF
    fi
    
    log_success "Smoke test report generated: $report_file"
}

# Main execution
main() {
    log_info "🧪 Constitutional Trainer Staging Smoke Tests"
    echo "============================================================"
    
    parse_args "$@"
    setup_test_environment
    
    # Run all smoke tests
    run_test "Service Health Checks" test_service_health_checks
    run_test "Redis Connectivity" test_redis_connectivity
    run_test "Constitutional Trainer API" test_constitutional_trainer_api
    run_test "Policy Engine Evaluation" test_policy_engine_evaluation
    run_test "Audit Engine Logging" test_audit_engine_logging
    run_test "Metrics Endpoints" test_metrics_endpoints
    run_test "Pod Readiness" test_pod_readiness
    run_test "Service Discovery" test_service_discovery
    run_test "Configuration Validation" test_configuration_validation
    run_test "Resource Limits" test_resource_limits
    
    # Generate report
    generate_test_report
    
    # Print summary
    echo ""
    echo "============================================================"
    log_info "📊 SMOKE TEST SUMMARY"
    echo "============================================================"
    echo "Total Tests: $TESTS_TOTAL"
    echo "Passed: $TESTS_PASSED"
    echo "Failed: $TESTS_FAILED"
    echo "Success Rate: $(( TESTS_PASSED * 100 / TESTS_TOTAL ))%"
    
    if [[ $TESTS_FAILED -eq 0 ]]; then
        log_success "✅ All smoke tests PASSED! Staging environment is ready."
        echo ""
        echo "🎯 Ready for stakeholder sign-off!"
    else
        log_error "❌ $TESTS_FAILED smoke tests FAILED. Please review and fix issues."
        echo ""
        echo "Failed tests:"
        for test in "${FAILED_TESTS[@]}"; do
            echo "  - $test"
        done
    fi
    
    echo ""
    echo "📄 Detailed report: $RESULTS_DIR/staging-smoke-test-report-*.md"
    
    # Exit with appropriate code
    if [[ $TESTS_FAILED -gt 0 ]]; then
        exit 1
    fi
}

# Trap for cleanup
trap cleanup_port_forwarding EXIT

# Execute main function
main "$@"
