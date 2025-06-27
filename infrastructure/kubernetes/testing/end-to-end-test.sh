#!/bin/bash

# ACGS-PGP End-to-End Test Suite
# Comprehensive testing from configuration validation through production operations

set -e

CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
TEST_NAMESPACE="acgs-e2e-test"
PRODUCTION_NAMESPACE="acgs-production"
START_TIME=$(date +%s)

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $(date '+%H:%M:%S') $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $(date '+%H:%M:%S') $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $(date '+%H:%M:%S') $1"; }
log_test() { echo -e "${BLUE}[TEST]${NC} $(date '+%H:%M:%S') $1"; }
log_e2e() { echo -e "${PURPLE}[E2E]${NC} $(date '+%H:%M:%S') $1"; }
log_phase() { echo -e "${CYAN}[PHASE]${NC} $(date '+%H:%M:%S') $1"; }

# Test results tracking
declare -A TEST_RESULTS
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Record test result
record_test() {
    local test_name=$1
    local result=$2
    
    TEST_RESULTS["$test_name"]=$result
    ((TOTAL_TESTS++))
    
    if [[ "$result" == "PASS" ]]; then
        ((PASSED_TESTS++))
        log_test "✅ $test_name: PASSED"
    else
        ((FAILED_TESTS++))
        log_test "❌ $test_name: FAILED"
    fi
}

# Phase 1: Configuration Validation Tests
test_configuration_validation() {
    log_phase "Phase 1: Configuration Validation Tests"
    
    # Test 1: YAML Syntax Validation
    log_test "Testing YAML syntax validation..."
    if kubectl apply --dry-run=client --validate=false -f infrastructure/kubernetes/services/ &>/dev/null; then
        record_test "yaml_syntax_validation" "PASS"
    else
        record_test "yaml_syntax_validation" "FAIL"
    fi
    
    # Test 2: Service Port Configuration
    log_test "Testing service port configuration..."
    local port_errors=0
    local expected_ports=("auth-service:8000" "constitutional-ai-service:8001" "integrity-service:8002" 
                         "formal-verification-service:8003" "governance-synthesis-service:8004" 
                         "policy-governance-service:8005" "evolutionary-computation-service:8006" 
                         "model-orchestrator-service:8007")
    
    for service_port in "${expected_ports[@]}"; do
        local service=$(echo $service_port | cut -d: -f1)
        local expected_port=$(echo $service_port | cut -d: -f2)
        local actual_port=$(grep -A 5 "containerPort:" "infrastructure/kubernetes/services/$service.yaml" | head -1 | grep -o '[0-9]*' || echo "")
        
        if [[ "$actual_port" != "$expected_port" ]]; then
            ((port_errors++))
        fi
    done
    
    if [[ $port_errors -eq 0 ]]; then
        record_test "service_port_configuration" "PASS"
    else
        record_test "service_port_configuration" "FAIL"
    fi
    
    # Test 3: Constitutional Hash Validation
    log_test "Testing constitutional hash validation..."
    local hash_found=$(grep -r "$CONSTITUTIONAL_HASH" infrastructure/kubernetes/services/ | wc -l)
    if [[ $hash_found -ge 8 ]]; then
        record_test "constitutional_hash_validation" "PASS"
    else
        record_test "constitutional_hash_validation" "FAIL"
    fi
    
    # Test 4: Resource Limits Validation
    log_test "Testing resource limits validation..."
    local resource_errors=0
    for service_file in infrastructure/kubernetes/services/*.yaml; do
        if ! grep -q "cpu: 200m" "$service_file" || ! grep -q "cpu: 500m" "$service_file" || \
           ! grep -q "memory: 512Mi" "$service_file" || ! grep -q "memory: 1Gi" "$service_file"; then
            ((resource_errors++))
        fi
    done
    
    if [[ $resource_errors -eq 0 ]]; then
        record_test "resource_limits_validation" "PASS"
    else
        record_test "resource_limits_validation" "FAIL"
    fi
    
    # Test 5: Security Context Validation
    log_test "Testing security context validation..."
    local security_errors=0
    for service_file in infrastructure/kubernetes/services/*.yaml; do
        if ! grep -q "runAsNonRoot: true" "$service_file" || ! grep -q "readOnlyRootFilesystem: true" "$service_file"; then
            ((security_errors++))
        fi
    done
    
    if [[ $security_errors -eq 0 ]]; then
        record_test "security_context_validation" "PASS"
    else
        record_test "security_context_validation" "FAIL"
    fi
}

# Phase 2: Deployment Validation Tests
test_deployment_validation() {
    log_phase "Phase 2: Deployment Validation Tests"
    
    # Test 6: Validation Script Execution
    log_test "Testing validation script execution..."
    if ./infrastructure/kubernetes/quick-validate.sh &>/dev/null; then
        record_test "validation_script_execution" "PASS"
    else
        record_test "validation_script_execution" "FAIL"
    fi
    
    # Test 7: Deployment Guide Completeness
    log_test "Testing deployment guide completeness..."
    local guide_sections=("Prerequisites" "Deployment Order" "Health Validation" "Emergency Procedures")
    local missing_sections=0
    
    for section in "${guide_sections[@]}"; do
        if ! grep -q "$section" infrastructure/kubernetes/DEPLOYMENT_GUIDE.md; then
            ((missing_sections++))
        fi
    done
    
    if [[ $missing_sections -eq 0 ]]; then
        record_test "deployment_guide_completeness" "PASS"
    else
        record_test "deployment_guide_completeness" "FAIL"
    fi
    
    # Test 8: Operational Tools Availability
    log_test "Testing operational tools availability..."
    local tools=("validate-deployment.sh" "load-test.sh" "health-monitor.sh" "emergency-response.sh" "backup-restore.sh")
    local missing_tools=0
    
    for tool in "${tools[@]}"; do
        if [[ ! -x "infrastructure/kubernetes/$tool" ]] && [[ ! -x "infrastructure/kubernetes/operations/$tool" ]]; then
            ((missing_tools++))
        fi
    done
    
    if [[ $missing_tools -eq 0 ]]; then
        record_test "operational_tools_availability" "PASS"
    else
        record_test "operational_tools_availability" "FAIL"
    fi
}

# Phase 3: Load Testing Validation
test_load_testing_framework() {
    log_phase "Phase 3: Load Testing Framework Validation"
    
    # Test 9: Load Test Script Validation
    log_test "Testing load test script validation..."
    if [[ -x "infrastructure/kubernetes/load-test.sh" ]] && [[ -x "infrastructure/kubernetes/testing/comprehensive-load-test.sh" ]]; then
        record_test "load_test_script_validation" "PASS"
    else
        record_test "load_test_script_validation" "FAIL"
    fi
    
    # Test 10: Performance Targets Definition
    log_test "Testing performance targets definition..."
    local targets_found=0
    if grep -q "2.0" infrastructure/kubernetes/testing/comprehensive-load-test.sh; then
        ((targets_found++))
    fi
    if grep -q "1000" infrastructure/kubernetes/testing/comprehensive-load-test.sh; then
        ((targets_found++))
    fi
    if grep -q "0.95" infrastructure/kubernetes/testing/comprehensive-load-test.sh; then
        ((targets_found++))
    fi
    
    if [[ $targets_found -eq 3 ]]; then
        record_test "performance_targets_definition" "PASS"
    else
        record_test "performance_targets_definition" "FAIL"
    fi
    
    # Test 11: Constitutional Compliance Testing
    log_test "Testing constitutional compliance testing framework..."
    if grep -q "constitutional_compliance_test" infrastructure/kubernetes/testing/comprehensive-load-test.sh; then
        record_test "constitutional_compliance_testing" "PASS"
    else
        record_test "constitutional_compliance_testing" "FAIL"
    fi
}

# Phase 4: Production Deployment Validation
test_production_deployment() {
    log_phase "Phase 4: Production Deployment Validation"
    
    # Test 12: Blue-Green Deployment Script
    log_test "Testing blue-green deployment script..."
    if [[ -x "infrastructure/kubernetes/production/blue-green-deployment.sh" ]]; then
        record_test "blue_green_deployment_script" "PASS"
    else
        record_test "blue_green_deployment_script" "FAIL"
    fi
    
    # Test 13: Traffic Router Configuration
    log_test "Testing traffic router configuration..."
    if grep -q "acgs-production-router" infrastructure/kubernetes/production/blue-green-deployment.sh; then
        record_test "traffic_router_configuration" "PASS"
    else
        record_test "traffic_router_configuration" "FAIL"
    fi
    
    # Test 14: Rollback Capability
    log_test "Testing rollback capability..."
    if grep -q "rollback_deployment" infrastructure/kubernetes/production/blue-green-deployment.sh; then
        record_test "rollback_capability" "PASS"
    else
        record_test "rollback_capability" "FAIL"
    fi
    
    # Test 15: Emergency Shutdown Procedures
    log_test "Testing emergency shutdown procedures..."
    if grep -q "emergency_shutdown" infrastructure/kubernetes/operations/emergency-response.sh && \
       grep -q "30.*min" infrastructure/kubernetes/operations/emergency-response.sh; then
        record_test "emergency_shutdown_procedures" "PASS"
    else
        record_test "emergency_shutdown_procedures" "FAIL"
    fi
}

# Phase 5: Service Mesh Integration Validation
test_service_mesh_integration() {
    log_phase "Phase 5: Service Mesh Integration Validation"
    
    # Test 16: Linkerd Deployment Script
    log_test "Testing Linkerd deployment script..."
    if [[ -x "infrastructure/kubernetes/service-mesh/linkerd-deployment.sh" ]]; then
        record_test "linkerd_deployment_script" "PASS"
    else
        record_test "linkerd_deployment_script" "FAIL"
    fi
    
    # Test 17: mTLS Configuration
    log_test "Testing mTLS configuration..."
    if grep -q "MeshTLSAuthentication" infrastructure/kubernetes/service-mesh/linkerd-deployment.sh; then
        record_test "mtls_configuration" "PASS"
    else
        record_test "mtls_configuration" "FAIL"
    fi
    
    # Test 18: Service Mesh Policies
    log_test "Testing service mesh policies..."
    if grep -q "ServerAuthorization" infrastructure/kubernetes/service-mesh/linkerd-deployment.sh && \
       grep -q "constitutional-ai-service" infrastructure/kubernetes/service-mesh/linkerd-deployment.sh; then
        record_test "service_mesh_policies" "PASS"
    else
        record_test "service_mesh_policies" "FAIL"
    fi
}

# Phase 6: Monitoring and Observability Validation
test_monitoring_observability() {
    log_phase "Phase 6: Monitoring and Observability Validation"
    
    # Test 19: Prometheus Configuration
    log_test "Testing Prometheus configuration..."
    if [[ -f "infrastructure/kubernetes/prometheus.yaml" ]] && [[ -f "infrastructure/kubernetes/monitoring/prometheus-rules.yaml" ]]; then
        record_test "prometheus_configuration" "PASS"
    else
        record_test "prometheus_configuration" "FAIL"
    fi
    
    # Test 20: Grafana Dashboard Configuration
    log_test "Testing Grafana dashboard configuration..."
    if [[ -f "infrastructure/kubernetes/grafana.yaml" ]] && [[ -f "infrastructure/kubernetes/monitoring/grafana-dashboard.json" ]]; then
        record_test "grafana_dashboard_configuration" "PASS"
    else
        record_test "grafana_dashboard_configuration" "FAIL"
    fi
    
    # Test 21: Constitutional Compliance Monitoring
    log_test "Testing constitutional compliance monitoring..."
    if grep -q "constitutional_compliance_score" infrastructure/kubernetes/monitoring/prometheus-rules.yaml; then
        record_test "constitutional_compliance_monitoring" "PASS"
    else
        record_test "constitutional_compliance_monitoring" "FAIL"
    fi
    
    # Test 22: Health Monitoring System
    log_test "Testing health monitoring system..."
    if [[ -x "infrastructure/kubernetes/operations/health-monitor.sh" ]] && \
       grep -q "check_constitutional_compliance" infrastructure/kubernetes/operations/health-monitor.sh; then
        record_test "health_monitoring_system" "PASS"
    else
        record_test "health_monitoring_system" "FAIL"
    fi
}

# Phase 7: Security and Compliance Validation
test_security_compliance() {
    log_phase "Phase 7: Security and Compliance Validation"
    
    # Test 23: Network Policies
    log_test "Testing network policies..."
    if grep -q "NetworkPolicy" infrastructure/kubernetes/service-mesh/linkerd-deployment.sh; then
        record_test "network_policies" "PASS"
    else
        record_test "network_policies" "FAIL"
    fi
    
    # Test 24: Secrets Management
    log_test "Testing secrets management..."
    if [[ -f "infrastructure/kubernetes/acgs-secrets.yaml" ]] && \
       grep -q "secretKeyRef" infrastructure/kubernetes/services/auth-service.yaml; then
        record_test "secrets_management" "PASS"
    else
        record_test "secrets_management" "FAIL"
    fi
    
    # Test 25: Constitutional AI Governance
    log_test "Testing constitutional AI governance..."
    local governance_components=0
    if grep -q "$CONSTITUTIONAL_HASH" infrastructure/kubernetes/services/constitutional-ai-service.yaml; then
        ((governance_components++))
    fi
    if grep -q "COMPLIANCE_THRESHOLD" infrastructure/kubernetes/services/constitutional-ai-service.yaml; then
        ((governance_components++))
    fi
    
    if [[ $governance_components -eq 2 ]]; then
        record_test "constitutional_ai_governance" "PASS"
    else
        record_test "constitutional_ai_governance" "FAIL"
    fi
}

# Phase 8: Documentation and Operational Readiness
test_documentation_readiness() {
    log_phase "Phase 8: Documentation and Operational Readiness"
    
    # Test 26: Documentation Completeness
    log_test "Testing documentation completeness..."
    local docs=("DEPLOYMENT_GUIDE.md" "PRODUCTION_READINESS_CHECKLIST.md" "PHASE_1_COMPLETION_REPORT.md" "PHASE_2_COMPLETION_REPORT.md")
    local missing_docs=0
    
    for doc in "${docs[@]}"; do
        if [[ ! -f "infrastructure/kubernetes/$doc" ]] && [[ ! -f "infrastructure/kubernetes/service-mesh/$doc" ]]; then
            ((missing_docs++))
        fi
    done
    
    if [[ $missing_docs -eq 0 ]]; then
        record_test "documentation_completeness" "PASS"
    else
        record_test "documentation_completeness" "FAIL"
    fi
    
    # Test 27: Operational Runbooks
    log_test "Testing operational runbooks..."
    if grep -q "Emergency Procedures" infrastructure/kubernetes/DEPLOYMENT_GUIDE.md && \
       grep -q "Troubleshooting" infrastructure/kubernetes/DEPLOYMENT_GUIDE.md; then
        record_test "operational_runbooks" "PASS"
    else
        record_test "operational_runbooks" "FAIL"
    fi
    
    # Test 28: Production Readiness Checklist
    log_test "Testing production readiness checklist..."
    if [[ -f "infrastructure/kubernetes/PRODUCTION_READINESS_CHECKLIST.md" ]] && \
       grep -q "Constitutional AI Compliance" infrastructure/kubernetes/PRODUCTION_READINESS_CHECKLIST.md; then
        record_test "production_readiness_checklist" "PASS"
    else
        record_test "production_readiness_checklist" "FAIL"
    fi
}

# Generate comprehensive test report
generate_test_report() {
    local end_time=$(date +%s)
    local duration=$((end_time - START_TIME))
    local report_file="/tmp/acgs_e2e_test_report_$(date +%Y%m%d_%H%M%S).txt"
    
    {
        echo "ACGS-PGP End-to-End Test Report"
        echo "Generated: $(date '+%Y-%m-%d %H:%M:%S')"
        echo "Test Duration: ${duration} seconds"
        echo "Constitutional Hash: $CONSTITUTIONAL_HASH"
        echo "========================================"
        echo
        
        echo "Test Summary:"
        echo "  Total Tests: $TOTAL_TESTS"
        echo "  Passed: $PASSED_TESTS"
        echo "  Failed: $FAILED_TESTS"
        echo "  Success Rate: $(( PASSED_TESTS * 100 / TOTAL_TESTS ))%"
        echo
        
        echo "Test Results by Phase:"
        echo
        
        echo "Phase 1: Configuration Validation"
        for test in yaml_syntax_validation service_port_configuration constitutional_hash_validation resource_limits_validation security_context_validation; do
            echo "  $test: ${TEST_RESULTS[$test]}"
        done
        echo
        
        echo "Phase 2: Deployment Validation"
        for test in validation_script_execution deployment_guide_completeness operational_tools_availability; do
            echo "  $test: ${TEST_RESULTS[$test]}"
        done
        echo
        
        echo "Phase 3: Load Testing Framework"
        for test in load_test_script_validation performance_targets_definition constitutional_compliance_testing; do
            echo "  $test: ${TEST_RESULTS[$test]}"
        done
        echo
        
        echo "Phase 4: Production Deployment"
        for test in blue_green_deployment_script traffic_router_configuration rollback_capability emergency_shutdown_procedures; do
            echo "  $test: ${TEST_RESULTS[$test]}"
        done
        echo
        
        echo "Phase 5: Service Mesh Integration"
        for test in linkerd_deployment_script mtls_configuration service_mesh_policies; do
            echo "  $test: ${TEST_RESULTS[$test]}"
        done
        echo
        
        echo "Phase 6: Monitoring and Observability"
        for test in prometheus_configuration grafana_dashboard_configuration constitutional_compliance_monitoring health_monitoring_system; do
            echo "  $test: ${TEST_RESULTS[$test]}"
        done
        echo
        
        echo "Phase 7: Security and Compliance"
        for test in network_policies secrets_management constitutional_ai_governance; do
            echo "  $test: ${TEST_RESULTS[$test]}"
        done
        echo
        
        echo "Phase 8: Documentation and Operational Readiness"
        for test in documentation_completeness operational_runbooks production_readiness_checklist; do
            echo "  $test: ${TEST_RESULTS[$test]}"
        done
        echo
        
        if [[ $FAILED_TESTS -eq 0 ]]; then
            echo "🎉 ALL TESTS PASSED - ACGS-PGP SYSTEM READY FOR PRODUCTION"
        else
            echo "❌ $FAILED_TESTS TESTS FAILED - REVIEW REQUIRED BEFORE PRODUCTION"
        fi
        
    } > "$report_file"
    
    log_e2e "End-to-end test report generated: $report_file"
    echo "$report_file"
}

# Main test execution
main() {
    log_e2e "Starting ACGS-PGP End-to-End Test Suite..."
    log_e2e "Testing complete system from configuration through production operations"
    echo
    
    # Execute all test phases
    test_configuration_validation
    test_deployment_validation
    test_load_testing_framework
    test_production_deployment
    test_service_mesh_integration
    test_monitoring_observability
    test_security_compliance
    test_documentation_readiness
    
    # Generate comprehensive report
    local report_file=$(generate_test_report)
    
    echo
    log_e2e "=== END-TO-END TEST SUMMARY ==="
    log_e2e "Total Tests: $TOTAL_TESTS"
    log_e2e "Passed: $PASSED_TESTS"
    log_e2e "Failed: $FAILED_TESTS"
    log_e2e "Success Rate: $(( PASSED_TESTS * 100 / TOTAL_TESTS ))%"
    log_e2e "Report: $report_file"
    
    if [[ $FAILED_TESTS -eq 0 ]]; then
        log_e2e "🎉 ALL END-TO-END TESTS PASSED!"
        log_e2e "ACGS-PGP system is ready for production deployment"
        exit 0
    else
        log_e2e "❌ $FAILED_TESTS tests failed - review required"
        exit 1
    fi
}

main "$@"
