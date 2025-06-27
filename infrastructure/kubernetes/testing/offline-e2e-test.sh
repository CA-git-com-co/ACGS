#!/bin/bash

# ACGS-PGP Offline End-to-End Test Suite
# Comprehensive testing without requiring live Kubernetes cluster

set -e

CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
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

# Phase 1: File Structure and Configuration Tests
test_file_structure() {
    log_phase "Phase 1: File Structure and Configuration Tests"
    
    # Test 1: Core Service Files Exist
    log_test "Testing core service files existence..."
    local services=("auth-service" "constitutional-ai-service" "integrity-service" 
                   "formal-verification-service" "governance-synthesis-service" 
                   "policy-governance-service" "evolutionary-computation-service" 
                   "model-orchestrator-service")
    local missing_services=0
    
    for service in "${services[@]}"; do
        if [[ ! -f "infrastructure/kubernetes/services/$service.yaml" ]]; then
            ((missing_services++))
        fi
    done
    
    if [[ $missing_services -eq 0 ]]; then
        record_test "core_service_files_exist" "PASS"
    else
        record_test "core_service_files_exist" "FAIL"
    fi
    
    # Test 2: Infrastructure Files Exist
    log_test "Testing infrastructure files existence..."
    local infra_files=("cockroachdb.yaml" "dragonflydb.yaml" "opa.yaml" "prometheus.yaml" "grafana.yaml")
    local missing_infra=0
    
    for file in "${infra_files[@]}"; do
        if [[ ! -f "infrastructure/kubernetes/$file" ]]; then
            ((missing_infra++))
        fi
    done
    
    if [[ $missing_infra -eq 0 ]]; then
        record_test "infrastructure_files_exist" "PASS"
    else
        record_test "infrastructure_files_exist" "FAIL"
    fi
    
    # Test 3: Operational Tools Exist
    log_test "Testing operational tools existence..."
    local tools=("validate-deployment.sh" "load-test.sh" "quick-validate.sh")
    local missing_tools=0
    
    for tool in "${tools[@]}"; do
        if [[ ! -f "infrastructure/kubernetes/$tool" ]]; then
            ((missing_tools++))
        fi
    done
    
    if [[ $missing_tools -eq 0 ]]; then
        record_test "operational_tools_exist" "PASS"
    else
        record_test "operational_tools_exist" "FAIL"
    fi
}

# Phase 2: Service Configuration Validation
test_service_configuration() {
    log_phase "Phase 2: Service Configuration Validation"
    
    # Test 4: Service Port Configuration
    log_test "Testing service port configuration..."
    local port_errors=0
    local expected_ports=("auth-service:8000" "constitutional-ai-service:8001" "integrity-service:8002" 
                         "formal-verification-service:8003" "governance-synthesis-service:8004" 
                         "policy-governance-service:8005" "evolutionary-computation-service:8006" 
                         "model-orchestrator-service:8007")
    
    for service_port in "${expected_ports[@]}"; do
        local service=$(echo $service_port | cut -d: -f1)
        local expected_port=$(echo $service_port | cut -d: -f2)
        
        if [[ -f "infrastructure/kubernetes/services/$service.yaml" ]]; then
            local actual_port=$(grep -A 5 "containerPort:" "infrastructure/kubernetes/services/$service.yaml" | head -1 | grep -o '[0-9]*' || echo "")
            if [[ "$actual_port" != "$expected_port" ]]; then
                ((port_errors++))
            fi
        else
            ((port_errors++))
        fi
    done
    
    if [[ $port_errors -eq 0 ]]; then
        record_test "service_port_configuration" "PASS"
    else
        record_test "service_port_configuration" "FAIL"
    fi
    
    # Test 5: Constitutional Hash Validation
    log_test "Testing constitutional hash validation..."
    local hash_count=$(grep -r "$CONSTITUTIONAL_HASH" infrastructure/kubernetes/services/ 2>/dev/null | wc -l)
    if [[ $hash_count -ge 8 ]]; then
        record_test "constitutional_hash_validation" "PASS"
    else
        record_test "constitutional_hash_validation" "FAIL"
    fi
    
    # Test 6: Resource Limits Configuration
    log_test "Testing resource limits configuration..."
    local resource_errors=0
    for service_file in infrastructure/kubernetes/services/*.yaml; do
        if [[ -f "$service_file" ]]; then
            if ! grep -q "cpu: 200m" "$service_file" || ! grep -q "cpu: 500m" "$service_file" || \
               ! grep -q "memory: 512Mi" "$service_file" || ! grep -q "memory: 1Gi" "$service_file"; then
                ((resource_errors++))
            fi
        fi
    done
    
    if [[ $resource_errors -eq 0 ]]; then
        record_test "resource_limits_configuration" "PASS"
    else
        record_test "resource_limits_configuration" "FAIL"
    fi
    
    # Test 7: Security Context Configuration
    log_test "Testing security context configuration..."
    local security_errors=0
    for service_file in infrastructure/kubernetes/services/*.yaml; do
        if [[ -f "$service_file" ]]; then
            if ! grep -q "runAsNonRoot: true" "$service_file" || ! grep -q "readOnlyRootFilesystem: true" "$service_file"; then
                ((security_errors++))
            fi
        fi
    done
    
    if [[ $security_errors -eq 0 ]]; then
        record_test "security_context_configuration" "PASS"
    else
        record_test "security_context_configuration" "FAIL"
    fi
}

# Phase 3: Deployment and Operations Validation
test_deployment_operations() {
    log_phase "Phase 3: Deployment and Operations Validation"
    
    # Test 8: Deployment Scripts Executable
    log_test "Testing deployment scripts are executable..."
    local scripts=("validate-deployment.sh" "load-test.sh" "quick-validate.sh")
    local non_executable=0
    
    for script in "${scripts[@]}"; do
        if [[ -f "infrastructure/kubernetes/$script" ]] && [[ ! -x "infrastructure/kubernetes/$script" ]]; then
            ((non_executable++))
        fi
    done
    
    if [[ $non_executable -eq 0 ]]; then
        record_test "deployment_scripts_executable" "PASS"
    else
        record_test "deployment_scripts_executable" "FAIL"
    fi
    
    # Test 9: Blue-Green Deployment Configuration
    log_test "Testing blue-green deployment configuration..."
    if [[ -f "infrastructure/kubernetes/production/blue-green-deployment.sh" ]] && \
       grep -q "acgs-production" "infrastructure/kubernetes/production/blue-green-deployment.sh" && \
       grep -q "acgs-blue" "infrastructure/kubernetes/production/blue-green-deployment.sh" && \
       grep -q "acgs-green" "infrastructure/kubernetes/production/blue-green-deployment.sh"; then
        record_test "blue_green_deployment_configuration" "PASS"
    else
        record_test "blue_green_deployment_configuration" "FAIL"
    fi
    
    # Test 10: Emergency Response Procedures
    log_test "Testing emergency response procedures..."
    if [[ -f "infrastructure/kubernetes/operations/emergency-response.sh" ]] && \
       grep -q "emergency_shutdown" "infrastructure/kubernetes/operations/emergency-response.sh" && \
       grep -q "constitutional_violation_response" "infrastructure/kubernetes/operations/emergency-response.sh"; then
        record_test "emergency_response_procedures" "PASS"
    else
        record_test "emergency_response_procedures" "FAIL"
    fi
}

# Phase 4: Service Mesh and Advanced Features
test_service_mesh_features() {
    log_phase "Phase 4: Service Mesh and Advanced Features"
    
    # Test 11: Linkerd Service Mesh Configuration
    log_test "Testing Linkerd service mesh configuration..."
    if [[ -f "infrastructure/kubernetes/service-mesh/linkerd-deployment.sh" ]] && \
       grep -q "linkerd" "infrastructure/kubernetes/service-mesh/linkerd-deployment.sh" && \
       grep -q "mTLS" "infrastructure/kubernetes/service-mesh/linkerd-deployment.sh"; then
        record_test "linkerd_service_mesh_configuration" "PASS"
    else
        record_test "linkerd_service_mesh_configuration" "FAIL"
    fi
    
    # Test 12: Traffic Policies Configuration
    log_test "Testing traffic policies configuration..."
    if [[ -f "infrastructure/kubernetes/service-mesh/linkerd-deployment.sh" ]] && \
       grep -q "ServerAuthorization" "infrastructure/kubernetes/service-mesh/linkerd-deployment.sh" && \
       grep -q "constitutional-ai-service" "infrastructure/kubernetes/service-mesh/linkerd-deployment.sh"; then
        record_test "traffic_policies_configuration" "PASS"
    else
        record_test "traffic_policies_configuration" "FAIL"
    fi
    
    # Test 13: Network Policies
    log_test "Testing network policies..."
    if [[ -f "infrastructure/kubernetes/service-mesh/linkerd-deployment.sh" ]] && \
       grep -q "NetworkPolicy" "infrastructure/kubernetes/service-mesh/linkerd-deployment.sh"; then
        record_test "network_policies" "PASS"
    else
        record_test "network_policies" "FAIL"
    fi
}

# Phase 5: Monitoring and Observability
test_monitoring_observability() {
    log_phase "Phase 5: Monitoring and Observability"
    
    # Test 14: Prometheus Configuration
    log_test "Testing Prometheus configuration..."
    if [[ -f "infrastructure/kubernetes/prometheus.yaml" ]] && \
       [[ -f "infrastructure/kubernetes/monitoring/prometheus-rules.yaml" ]] && \
       grep -q "constitutional_compliance_score" "infrastructure/kubernetes/monitoring/prometheus-rules.yaml"; then
        record_test "prometheus_configuration" "PASS"
    else
        record_test "prometheus_configuration" "FAIL"
    fi
    
    # Test 15: Grafana Dashboard Configuration
    log_test "Testing Grafana dashboard configuration..."
    if [[ -f "infrastructure/kubernetes/grafana.yaml" ]] && \
       [[ -f "infrastructure/kubernetes/monitoring/grafana-dashboard.json" ]] && \
       grep -q "Constitutional Compliance Score" "infrastructure/kubernetes/monitoring/grafana-dashboard.json"; then
        record_test "grafana_dashboard_configuration" "PASS"
    else
        record_test "grafana_dashboard_configuration" "FAIL"
    fi
    
    # Test 16: Health Monitoring System
    log_test "Testing health monitoring system..."
    if [[ -f "infrastructure/kubernetes/operations/health-monitor.sh" ]] && \
       grep -q "check_constitutional_compliance" "infrastructure/kubernetes/operations/health-monitor.sh" && \
       grep -q "$CONSTITUTIONAL_HASH" "infrastructure/kubernetes/operations/health-monitor.sh"; then
        record_test "health_monitoring_system" "PASS"
    else
        record_test "health_monitoring_system" "FAIL"
    fi
}

# Phase 6: Documentation and Compliance
test_documentation_compliance() {
    log_phase "Phase 6: Documentation and Compliance"
    
    # Test 17: Documentation Completeness
    log_test "Testing documentation completeness..."
    local docs=("DEPLOYMENT_GUIDE.md" "PRODUCTION_READINESS_CHECKLIST.md")
    local missing_docs=0
    
    for doc in "${docs[@]}"; do
        if [[ ! -f "infrastructure/kubernetes/$doc" ]]; then
            ((missing_docs++))
        fi
    done
    
    if [[ $missing_docs -eq 0 ]]; then
        record_test "documentation_completeness" "PASS"
    else
        record_test "documentation_completeness" "FAIL"
    fi
    
    # Test 18: Production Readiness Checklist
    log_test "Testing production readiness checklist..."
    if [[ -f "infrastructure/kubernetes/PRODUCTION_READINESS_CHECKLIST.md" ]] && \
       grep -q "Constitutional AI Compliance" "infrastructure/kubernetes/PRODUCTION_READINESS_CHECKLIST.md" && \
       grep -q "$CONSTITUTIONAL_HASH" "infrastructure/kubernetes/PRODUCTION_READINESS_CHECKLIST.md"; then
        record_test "production_readiness_checklist" "PASS"
    else
        record_test "production_readiness_checklist" "FAIL"
    fi
    
    # Test 19: Phase Completion Reports
    log_test "Testing phase completion reports..."
    local reports=("PHASE_1_COMPLETION_REPORT.md" "PHASE_2_COMPLETION_REPORT.md")
    local missing_reports=0
    
    for report in "${reports[@]}"; do
        if [[ ! -f "infrastructure/kubernetes/$report" ]] && [[ ! -f "infrastructure/kubernetes/service-mesh/$report" ]]; then
            ((missing_reports++))
        fi
    done
    
    if [[ $missing_reports -eq 0 ]]; then
        record_test "phase_completion_reports" "PASS"
    else
        record_test "phase_completion_reports" "FAIL"
    fi
}

# Phase 7: Load Testing and Performance
test_load_testing_performance() {
    log_phase "Phase 7: Load Testing and Performance"
    
    # Test 20: Load Testing Framework
    log_test "Testing load testing framework..."
    if [[ -f "infrastructure/kubernetes/testing/comprehensive-load-test.sh" ]] && \
       grep -q "constitutional_compliance_test" "infrastructure/kubernetes/testing/comprehensive-load-test.sh" && \
       grep -q "TARGET_RPS" "infrastructure/kubernetes/testing/comprehensive-load-test.sh"; then
        record_test "load_testing_framework" "PASS"
    else
        record_test "load_testing_framework" "FAIL"
    fi
    
    # Test 21: Performance Targets Definition
    log_test "Testing performance targets definition..."
    local targets_found=0
    if grep -q "2.0" "infrastructure/kubernetes/testing/comprehensive-load-test.sh" 2>/dev/null; then
        ((targets_found++))
    fi
    if grep -q "1000" "infrastructure/kubernetes/testing/comprehensive-load-test.sh" 2>/dev/null; then
        ((targets_found++))
    fi
    if grep -q "0.95" "infrastructure/kubernetes/testing/comprehensive-load-test.sh" 2>/dev/null; then
        ((targets_found++))
    fi
    
    if [[ $targets_found -eq 3 ]]; then
        record_test "performance_targets_definition" "PASS"
    else
        record_test "performance_targets_definition" "FAIL"
    fi
}

# Generate comprehensive test report
generate_test_report() {
    local end_time=$(date +%s)
    local duration=$((end_time - START_TIME))
    local report_file="/tmp/acgs_offline_e2e_test_report_$(date +%Y%m%d_%H%M%S).txt"
    
    {
        echo "ACGS-PGP Offline End-to-End Test Report"
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
        
        echo "Detailed Test Results:"
        for test_name in "${!TEST_RESULTS[@]}"; do
            echo "  $test_name: ${TEST_RESULTS[$test_name]}"
        done
        echo
        
        if [[ $FAILED_TESTS -eq 0 ]]; then
            echo "🎉 ALL TESTS PASSED - ACGS-PGP SYSTEM CONFIGURATION VALIDATED"
            echo "System is ready for Kubernetes deployment and production operations"
        else
            echo "❌ $FAILED_TESTS TESTS FAILED - CONFIGURATION ISSUES DETECTED"
            echo "Review failed tests and fix issues before deployment"
        fi
        
    } > "$report_file"
    
    log_e2e "Offline end-to-end test report generated: $report_file"
    echo "$report_file"
}

# Main test execution
main() {
    log_e2e "Starting ACGS-PGP Offline End-to-End Test Suite..."
    log_e2e "Testing system configuration without requiring live Kubernetes cluster"
    echo
    
    # Execute all test phases
    test_file_structure
    test_service_configuration
    test_deployment_operations
    test_service_mesh_features
    test_monitoring_observability
    test_documentation_compliance
    test_load_testing_performance
    
    # Generate comprehensive report
    local report_file=$(generate_test_report)
    
    echo
    log_e2e "=== OFFLINE END-TO-END TEST SUMMARY ==="
    log_e2e "Total Tests: $TOTAL_TESTS"
    log_e2e "Passed: $PASSED_TESTS"
    log_e2e "Failed: $FAILED_TESTS"
    log_e2e "Success Rate: $(( PASSED_TESTS * 100 / TOTAL_TESTS ))%"
    log_e2e "Report: $report_file"
    
    if [[ $FAILED_TESTS -eq 0 ]]; then
        log_e2e "🎉 ALL OFFLINE TESTS PASSED!"
        log_e2e "ACGS-PGP system configuration is validated and ready for deployment"
        exit 0
    else
        log_e2e "❌ $FAILED_TESTS tests failed - configuration review required"
        exit 1
    fi
}

main "$@"
