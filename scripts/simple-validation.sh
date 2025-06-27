#!/bin/bash

# Simple ACGS GitOps Validation Script
# Quick validation of core components

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0

# Test result tracking
test_result() {
    local test_name="$1"
    local result="$2"
    
    if [[ "$result" == "PASS" ]]; then
        log_success "✓ $test_name"
        ((TESTS_PASSED++))
    else
        log_error "✗ $test_name"
        ((TESTS_FAILED++))
    fi
}

# Check if file exists
check_file() {
    local file="$1"
    local name="$2"
    
    if [[ -f "$file" && -r "$file" ]]; then
        test_result "$name" "PASS"
        return 0
    else
        test_result "$name" "FAIL"
        return 1
    fi
}

# Validate YAML syntax
validate_yaml() {
    local file="$1"
    local name="$2"
    
    if python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null; then
        test_result "$name YAML syntax" "PASS"
        return 0
    else
        test_result "$name YAML syntax" "FAIL"
        return 1
    fi
}

# Main validation
main() {
    log_info "ACGS GitOps Simple Validation"
    echo "================================"
    
    # Test 1: File existence
    log_info "Test 1: File Structure"
    check_file "crossplane/definitions/githubclaim.yaml" "CRD Definition"
    check_file "crossplane/compositions/acgs-service.yaml" "Crossplane Composition"
    check_file "crossplane/providers/github-provider.yaml" "GitHub Provider"
    check_file "argocd/applications/acgs-claims.yaml" "ArgoCD Applications"
    check_file "examples/gs-service-claim.yaml" "Service Claim Examples"
    
    echo
    
    # Test 2: YAML syntax
    log_info "Test 2: YAML Syntax"
    if [[ -f "crossplane/definitions/githubclaim.yaml" ]]; then
        validate_yaml "crossplane/definitions/githubclaim.yaml" "CRD"
    fi
    
    if [[ -f "crossplane/compositions/acgs-service.yaml" ]]; then
        validate_yaml "crossplane/compositions/acgs-service.yaml" "Composition"
    fi
    
    if [[ -f "argocd/applications/acgs-claims.yaml" ]]; then
        validate_yaml "argocd/applications/acgs-claims.yaml" "ArgoCD"
    fi
    
    if [[ -f "examples/gs-service-claim.yaml" ]]; then
        validate_yaml "examples/gs-service-claim.yaml" "Examples"
    fi
    
    echo
    
    # Test 3: Constitutional hash check
    log_info "Test 3: Constitutional Hash"
    local expected_hash="cdd01ef066bc6cf2"
    
    if grep -q "$expected_hash" crossplane/definitions/githubclaim.yaml 2>/dev/null; then
        test_result "CRD constitutional hash" "PASS"
    else
        test_result "CRD constitutional hash" "FAIL"
    fi
    
    if grep -q "$expected_hash" examples/gs-service-claim.yaml 2>/dev/null; then
        test_result "Example constitutional hash" "PASS"
    else
        test_result "Example constitutional hash" "FAIL"
    fi
    
    echo
    
    # Test 4: Service types check
    log_info "Test 4: Service Types"
    local service_types=("auth" "ac" "integrity" "fv" "gs" "pgc" "ec" "dgm")
    local found_types=0
    
    for service in "${service_types[@]}"; do
        if grep -q "- $service" crossplane/definitions/githubclaim.yaml 2>/dev/null; then
            ((found_types++))
        fi
    done
    
    if [[ $found_types -eq 8 ]]; then
        test_result "All 8 service types" "PASS"
    else
        test_result "All 8 service types (found: $found_types)" "FAIL"
    fi
    
    echo
    
    # Test 5: Scripts check
    log_info "Test 5: Scripts"
    local scripts=(
        "scripts/deploy-gitops.sh"
        "scripts/monitor-gitops.sh"
        "scripts/validate-gitops-workflow.sh"
    )
    
    for script in "${scripts[@]}"; do
        if [[ -f "$script" && -x "$script" ]]; then
            test_result "$(basename $script)" "PASS"
        else
            test_result "$(basename $script)" "FAIL"
        fi
    done
    
    echo
    
    # Summary
    log_info "Validation Summary:"
    log_success "Tests passed: $TESTS_PASSED"
    if [[ $TESTS_FAILED -gt 0 ]]; then
        log_error "Tests failed: $TESTS_FAILED"
    else
        log_success "Tests failed: $TESTS_FAILED"
    fi
    
    local total_tests=$((TESTS_PASSED + TESTS_FAILED))
    local success_rate=$((TESTS_PASSED * 100 / total_tests))
    log_info "Success rate: $success_rate%"
    
    if [[ $TESTS_FAILED -eq 0 ]]; then
        log_success "All tests passed! GitOps workflow structure is valid."
        return 0
    else
        log_error "Some tests failed. Please review the issues above."
        return 1
    fi
}

main "$@"
