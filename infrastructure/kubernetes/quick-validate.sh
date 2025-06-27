#!/bin/bash

# Quick ACGS-PGP Configuration Validation
# Performs essential validation checks without external dependencies

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Constants
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
SERVICES_DIR="infrastructure/kubernetes/services"

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Expected service configurations
declare -A EXPECTED_SERVICES=(
    ["auth-service"]="8000"
    ["constitutional-ai-service"]="8001"
    ["integrity-service"]="8002"
    ["formal-verification-service"]="8003"
    ["governance-synthesis-service"]="8004"
    ["policy-governance-service"]="8005"
    ["evolutionary-computation-service"]="8006"
    ["model-orchestrator-service"]="8007"
)

validate_service_ports() {
    log_info "Validating service port configurations..."
    local errors=0
    
    for service in "${!EXPECTED_SERVICES[@]}"; do
        local expected_port="${EXPECTED_SERVICES[$service]}"
        local service_file="$SERVICES_DIR/$service.yaml"
        
        if [[ ! -f "$service_file" ]]; then
            log_error "✗ Missing service file: $service_file"
            ((errors++))
            continue
        fi
        
        # Check container port
        local container_port=$(grep -A 5 "containerPort:" "$service_file" | head -1 | grep -o '[0-9]*' || echo "")
        
        if [[ "$container_port" == "$expected_port" ]]; then
            log_info "✓ $service port correct ($expected_port)"
        else
            log_error "✗ $service port incorrect - Expected: $expected_port, Found: $container_port"
            ((errors++))
        fi
    done
    
    return $errors
}

validate_resource_limits() {
    log_info "Validating resource limits..."
    local errors=0
    
    for service in "${!EXPECTED_SERVICES[@]}"; do
        local service_file="$SERVICES_DIR/$service.yaml"
        
        if [[ ! -f "$service_file" ]]; then
            continue
        fi
        
        if grep -q "resources:" "$service_file"; then
            if grep -q "cpu: 200m" "$service_file" && grep -q "cpu: 500m" "$service_file" && \
               grep -q "memory: 512Mi" "$service_file" && grep -q "memory: 1Gi" "$service_file"; then
                log_info "✓ $service resource limits correct"
            else
                log_error "✗ $service resource limits incorrect"
                ((errors++))
            fi
        else
            log_error "✗ $service missing resource limits"
            ((errors++))
        fi
    done
    
    return $errors
}

validate_constitutional_hash() {
    log_info "Validating constitutional hash..."
    local service_file="$SERVICES_DIR/constitutional-ai-service.yaml"
    
    if [[ ! -f "$service_file" ]]; then
        log_error "✗ Constitutional AI service file not found"
        return 1
    fi
    
    if grep -q "CONSTITUTIONAL_HASH" "$service_file" && grep -q "$CONSTITUTIONAL_HASH" "$service_file"; then
        log_info "✓ Constitutional hash validated: $CONSTITUTIONAL_HASH"
        return 0
    else
        log_error "✗ Constitutional hash missing or incorrect"
        return 1
    fi
}

validate_security_contexts() {
    log_info "Validating security contexts..."
    local errors=0
    
    for service in "${!EXPECTED_SERVICES[@]}"; do
        local service_file="$SERVICES_DIR/$service.yaml"
        
        if [[ ! -f "$service_file" ]]; then
            continue
        fi
        
        if grep -q "runAsNonRoot: true" "$service_file"; then
            log_info "✓ $service has security context"
        else
            log_warn "⚠ $service missing security context"
            ((errors++))
        fi
    done
    
    return $errors
}

validate_namespaces() {
    log_info "Validating namespace configurations..."
    local errors=0
    
    for service in "${!EXPECTED_SERVICES[@]}"; do
        local service_file="$SERVICES_DIR/$service.yaml"
        
        if [[ ! -f "$service_file" ]]; then
            continue
        fi
        
        if grep -q "namespace: acgs-system" "$service_file"; then
            log_info "✓ $service has correct namespace"
        else
            log_warn "⚠ $service missing namespace specification"
            ((errors++))
        fi
    done
    
    return $errors
}

main() {
    log_info "Starting ACGS-PGP Quick Validation..."
    echo
    
    local total_errors=0
    
    # Run validation tests
    validate_service_ports || total_errors=$((total_errors + $?))
    echo
    
    validate_resource_limits || total_errors=$((total_errors + $?))
    echo
    
    validate_constitutional_hash || total_errors=$((total_errors + $?))
    echo
    
    validate_security_contexts || total_errors=$((total_errors + $?))
    echo
    
    validate_namespaces || total_errors=$((total_errors + $?))
    echo
    
    # Summary
    log_info "=== VALIDATION SUMMARY ==="
    if [[ $total_errors -eq 0 ]]; then
        log_info "🎉 All critical validations passed!"
        log_info "Configurations are ready for deployment."
        exit 0
    else
        log_error "❌ Found $total_errors validation issues."
        log_error "Please fix issues before deployment."
        exit 1
    fi
}

main "$@"
