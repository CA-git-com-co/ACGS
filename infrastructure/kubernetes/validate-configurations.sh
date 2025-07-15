#!/bin/bash

# ACGS-PGP Kubernetes Configuration Validation Script
# Validates all Kubernetes configurations against ACGS-PGP requirements

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration constants
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
EXPECTED_CPU_REQUEST="200m"
EXPECTED_CPU_LIMIT="500m"
EXPECTED_MEMORY_REQUEST="512Mi"
EXPECTED_MEMORY_LIMIT="1Gi"

# Expected service ports
declare -A EXPECTED_PORTS=(
    ["auth-service"]="8000"
    ["constitutional-ai-service"]="8001"
    ["integrity-service"]="8002"
    ["formal-verification-service"]="8003"
    ["governance-synthesis-service"]="8004"
    ["policy-governance-service"]="8005"
    ["evolutionary-computation-service"]="8006"
    ["model-orchestrator-service"]="8007"
)

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_test() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

# Check if required tools are available
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    local missing_tools=()
    
    if ! command -v kubectl &> /dev/null; then
        missing_tools+=("kubectl")
    fi
    
    if ! command -v yq &> /dev/null; then
        log_warn "yq not found - using grep/awk for YAML parsing (less reliable)"
    fi
    
    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        return 1
    fi
    
    log_info "Prerequisites check passed"
    return 0
}

# Validate service port configuration
validate_service_ports() {
    log_test "Validating service port configurations..."
    
    local failed_services=()
    local services_dir="infrastructure/kubernetes/services"
    
    for service_name in "${!EXPECTED_PORTS[@]}"; do
        local expected_port="${EXPECTED_PORTS[$service_name]}"
        local service_file="$services_dir/$service_name.yaml"
        
        if [[ ! -f "$service_file" ]]; then
            log_error "✗ Service file not found: $service_file"
            failed_services+=("$service_name")
            continue
        fi
        
        # Check container port
        local container_port=$(grep -A 10 "containers:" "$service_file" | grep "containerPort:" | head -1 | awk '{print $2}')
        
        # Check service port
        local service_port=$(grep -A 20 "kind: Service" "$service_file" | grep "port:" | head -1 | awk '{print $2}')
        
        if [[ "$container_port" == "$expected_port" ]] && [[ "$service_port" == "$expected_port" ]]; then
            log_info "✓ $service_name port configuration correct ($expected_port)"
        else
            log_error "✗ $service_name port mismatch - Expected: $expected_port, Container: $container_port, Service: $service_port"
            failed_services+=("$service_name")
        fi
    done
    
    if [[ ${#failed_services[@]} -gt 0 ]]; then
        log_error "Failed port validation for services: ${failed_services[*]}"
        return 1
    fi
    
    log_info "All service ports validated successfully"
    return 0
}

# Validate resource limits
validate_resource_limits() {
    log_test "Validating resource limits..."
    
    local failed_services=()
    local services_dir="infrastructure/kubernetes/services"
    
    for service_name in "${!EXPECTED_PORTS[@]}"; do
        local service_file="$services_dir/$service_name.yaml"
        
        if [[ ! -f "$service_file" ]]; then
            continue
        fi
        
        # Check if resources section exists
        if ! grep -q "resources:" "$service_file"; then
            log_error "✗ $service_name missing resource limits"
            failed_services+=("$service_name")
            continue
        fi
        
        # Extract resource values (simplified parsing)
        local cpu_request=$(grep -A 10 "requests:" "$service_file" | grep "cpu:" | awk '{print $2}' | tr -d '"')
        local cpu_limit=$(grep -A 10 "limits:" "$service_file" | grep "cpu:" | awk '{print $2}' | tr -d '"')
        local memory_request=$(grep -A 10 "requests:" "$service_file" | grep "memory:" | awk '{print $2}' | tr -d '"')
        local memory_limit=$(grep -A 10 "limits:" "$service_file" | grep "memory:" | awk '{print $2}' | tr -d '"')
        
        # Validate resource values
        local resource_valid=true
        
        if [[ "$cpu_request" != "$EXPECTED_CPU_REQUEST" ]]; then
            log_error "✗ $service_name CPU request mismatch - Expected: $EXPECTED_CPU_REQUEST, Found: $cpu_request"
            resource_valid=false
        fi
        
        if [[ "$cpu_limit" != "$EXPECTED_CPU_LIMIT" ]]; then
            log_error "✗ $service_name CPU limit mismatch - Expected: $EXPECTED_CPU_LIMIT, Found: $cpu_limit"
            resource_valid=false
        fi
        
        if [[ "$memory_request" != "$EXPECTED_MEMORY_REQUEST" ]]; then
            log_error "✗ $service_name Memory request mismatch - Expected: $EXPECTED_MEMORY_REQUEST, Found: $memory_request"
            resource_valid=false
        fi
        
        if [[ "$memory_limit" != "$EXPECTED_MEMORY_LIMIT" ]]; then
            log_error "✗ $service_name Memory limit mismatch - Expected: $EXPECTED_MEMORY_LIMIT, Found: $memory_limit"
            resource_valid=false
        fi
        
        if [[ "$resource_valid" == "true" ]]; then
            log_info "✓ $service_name resource limits correct"
        else
            failed_services+=("$service_name")
        fi
    done
    
    if [[ ${#failed_services[@]} -gt 0 ]]; then
        log_error "Failed resource validation for services: ${failed_services[*]}"
        return 1
    fi
    
    log_info "All resource limits validated successfully"
    return 0
}

# Validate constitutional hash
validate_constitutional_hash() {
    log_test "Validating constitutional hash configuration..."
    
    local constitutional_service="infrastructure/kubernetes/services/constitutional-ai-service.yaml"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    
    if [[ ! -f "$constitutional_service" ]]; then
        log_error "✗ Constitutional AI service file not found"
        return 1
    fi
    
    # Check if constitutional hash is present
    local hash_line=$(grep "CONSTITUTIONAL_HASH" "$constitutional_service" || echo "")
    
    if [[ -z "$hash_line" ]]; then
        log_error "✗ CONSTITUTIONAL_HASH environment variable not found"
        return 1
    fi
    
    # Extract hash value
    local hash_value=$(echo "$hash_line" | grep -o '"[^"]*"' | tr -d '"')
    
    if [[ "$hash_value" == "$CONSTITUTIONAL_HASH" ]]; then
        log_info "✓ Constitutional hash validated: $CONSTITUTIONAL_HASH"
        return 0
    else
        log_error "✗ Constitutional hash mismatch - Expected: $CONSTITUTIONAL_HASH, Found: $hash_value"
        return 1
    fi
}

# Validate security configurations
validate_security_config() {
    log_test "Validating security configurations..."
    
    local failed_checks=()
    local services_dir="infrastructure/kubernetes/services"
    
    for service_name in "${!EXPECTED_PORTS[@]}"; do
        local service_file="$services_dir/$service_name.yaml"
        
        if [[ ! -f "$service_file" ]]; then
            continue
        fi
        
        # Check for security context
        if ! grep -q "securityContext:" "$service_file"; then
            log_warn "⚠ $service_name missing security context"
            failed_checks+=("$service_name-security-context")
        fi
        
        # Check for non-root user
        if ! grep -q "runAsNonRoot:" "$service_file"; then
            log_warn "⚠ $service_name missing runAsNonRoot setting"
            failed_checks+=("$service_name-non-root")
        fi
        
        # Check for readiness/liveness probes
        if ! grep -q "readinessProbe:" "$service_file"; then
            log_warn "⚠ $service_name missing readiness probe"
            failed_checks+=("$service_name-readiness")
        fi
        
        if ! grep -q "livenessProbe:" "$service_file"; then
            log_warn "⚠ $service_name missing liveness probe"
            failed_checks+=("$service_name-liveness")
        fi
    done
    
    if [[ ${#failed_checks[@]} -gt 0 ]]; then
        log_warn "Security configuration warnings: ${failed_checks[*]}"
        return 1
    fi
    
    log_info "Security configurations validated"
    return 0
}

# Validate YAML syntax
validate_yaml_syntax() {
    log_test "Validating YAML syntax..."
    
    local failed_files=()
    local yaml_files=$(find infrastructure/kubernetes -name "*.yaml" -type f)
    
    for yaml_file in $yaml_files; do
        if kubectl apply --dry-run=client -f "$yaml_file" &> /dev/null; then
            log_info "✓ $yaml_file syntax valid"
        else
            log_error "✗ $yaml_file syntax invalid"
            failed_files+=("$yaml_file")
        fi
    done
    
    if [[ ${#failed_files[@]} -gt 0 ]]; then
        log_error "YAML syntax validation failed for: ${failed_files[*]}"
        return 1
    fi
    
    log_info "All YAML files have valid syntax"
    return 0
}

# Generate validation report
generate_report() {
    local validation_results=("$@")
    
    log_info "=== VALIDATION REPORT ==="
    echo
    
    local passed_tests=0
    local total_tests=${#validation_results[@]}
    
    for result in "${validation_results[@]}"; do
        if [[ "$result" == "PASS" ]]; then
            ((passed_tests++))
        fi
    done
    
    log_info "Tests Passed: $passed_tests/$total_tests"
    
    if [[ $passed_tests -eq $total_tests ]]; then
        log_info "🎉 All validation tests passed! Configurations are ready for deployment."
        return 0
    else
        log_error "❌ Validation failed. Please fix the issues above before deployment."
        return 1
    fi
}

# Main validation function
main() {
    log_info "Starting ACGS-PGP Kubernetes configuration validation..."
    log_info "Constitutional Hash: $CONSTITUTIONAL_HASH"
    log_info "Expected Resource Limits: CPU($EXPECTED_CPU_REQUEST/$EXPECTED_CPU_LIMIT), Memory($EXPECTED_MEMORY_REQUEST/$EXPECTED_MEMORY_LIMIT)"
    echo
    
    local validation_tests=(
        "check_prerequisites"
        "validate_service_ports"
        "validate_resource_limits"
        "validate_constitutional_hash"
        "validate_security_config"
        "validate_yaml_syntax"
    )
    
    local results=()
    
    for test in "${validation_tests[@]}"; do
        echo
        if $test; then
            log_info "✓ $test PASSED"
            results+=("PASS")
        else
            log_error "✗ $test FAILED"
            results+=("FAIL")
        fi
    done
    
    echo
    generate_report "${results[@]}"
}

# Run main function
main "$@"
