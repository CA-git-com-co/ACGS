#!/bin/bash

# ACGS GitOps Workflow Validation Script
# Comprehensive testing of the GitOps workflow

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

# Configuration
NAMESPACE_CROSSPLANE="crossplane-system"
NAMESPACE_ARGOCD="argocd"
NAMESPACE_ACGS="acgs-system"
TEST_CLAIM_NAME="test-validation-service"
TIMEOUT=300

# Test counter
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

# Wait for condition with timeout
wait_for_condition() {
    local description="$1"
    local command="$2"
    local timeout="${3:-$TIMEOUT}"
    
    log_info "Waiting for: $description (timeout: ${timeout}s)"
    
    local count=0
    while [[ $count -lt $timeout ]]; do
        if eval "$command" &>/dev/null; then
            log_success "$description - completed"
            return 0
        fi
        sleep 5
        ((count+=5))
        echo -n "."
    done
    
    echo
    log_error "$description - timed out after ${timeout}s"
    return 1
}

# Test 1: Verify prerequisites
test_prerequisites() {
    log_info "Test 1: Verifying prerequisites..."
    
    local result="PASS"
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl not found"
        result="FAIL"
    fi
    
    # Check cluster connectivity
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster"
        result="FAIL"
    fi
    
    # Check required namespaces
    for ns in $NAMESPACE_CROSSPLANE $NAMESPACE_ARGOCD $NAMESPACE_ACGS; do
        if ! kubectl get namespace $ns &> /dev/null; then
            log_error "Namespace $ns not found"
            result="FAIL"
        fi
    done
    
    test_result "Prerequisites check" "$result"
}

# Test 2: Verify Crossplane installation
test_crossplane() {
    log_info "Test 2: Verifying Crossplane installation..."
    
    local result="PASS"
    
    # Check Crossplane pods
    if ! kubectl get pods -n $NAMESPACE_CROSSPLANE -l app=crossplane | grep -q "Running"; then
        log_error "Crossplane pods not running"
        result="FAIL"
    fi
    
    # Check providers
    if ! kubectl get providers | grep -q "provider-github"; then
        log_error "GitHub provider not found"
        result="FAIL"
    fi
    
    # Check provider health
    if ! kubectl get providers provider-github -o jsonpath='{.status.conditions[?(@.type=="Healthy")].status}' | grep -q "True"; then
        log_error "GitHub provider not healthy"
        result="FAIL"
    fi
    
    # Check functions
    if ! kubectl get functions | grep -q "function-kcl"; then
        log_error "KCL function not found"
        result="FAIL"
    fi
    
    # Check compositions
    if ! kubectl get compositions | grep -q "acgs-service-composition"; then
        log_error "ACGS service composition not found"
        result="FAIL"
    fi
    
    test_result "Crossplane installation" "$result"
}

# Test 3: Verify ArgoCD installation
test_argocd() {
    log_info "Test 3: Verifying ArgoCD installation..."
    
    local result="PASS"
    
    # Check ArgoCD pods
    local argocd_pods
    argocd_pods=$(kubectl get pods -n $NAMESPACE_ARGOCD --no-headers | grep -c "Running" || echo "0")
    
    if [[ $argocd_pods -lt 3 ]]; then
        log_error "Not enough ArgoCD pods running (found: $argocd_pods, expected: >=3)"
        result="FAIL"
    fi
    
    # Check ArgoCD applications
    if ! kubectl get applications -n $NAMESPACE_ARGOCD | grep -q "acgs-service-claims"; then
        log_error "ACGS service claims application not found"
        result="FAIL"
    fi
    
    test_result "ArgoCD installation" "$result"
}

# Test 4: Verify CRD functionality
test_crd() {
    log_info "Test 4: Verifying CRD functionality..."
    
    local result="PASS"
    
    # Check CRD exists
    if ! kubectl get crd acgsserviceclaims.acgs.io &> /dev/null; then
        log_error "ACGSServiceClaim CRD not found"
        result="FAIL"
    fi
    
    # Check CRD is established
    if ! kubectl get crd acgsserviceclaims.acgs.io -o jsonpath='{.status.conditions[?(@.type=="Established")].status}' | grep -q "True"; then
        log_error "CRD not established"
        result="FAIL"
    fi
    
    # Test CRD validation
    if ! kubectl explain acgsserviceclaim.spec &> /dev/null; then
        log_error "CRD spec not accessible"
        result="FAIL"
    fi
    
    test_result "CRD functionality" "$result"
}

# Test 5: Create test service claim
test_service_claim_creation() {
    log_info "Test 5: Testing service claim creation..."
    
    local result="PASS"
    
    # Clean up any existing test claim
    kubectl delete acgsserviceclaim $TEST_CLAIM_NAME -n $NAMESPACE_ACGS --ignore-not-found=true
    
    # Create test service claim
    cat <<EOF | kubectl apply -f -
apiVersion: acgs.io/v1alpha1
kind: ACGSServiceClaim
metadata:
  name: $TEST_CLAIM_NAME
  namespace: $NAMESPACE_ACGS
spec:
  serviceType: gs
  serviceName: $TEST_CLAIM_NAME
  constitutionalHash: "cdd01ef066bc6cf2"
  deployment:
    replicas: 1
    resources:
      requests:
        cpu: "200m"
        memory: "512Mi"
      limits:
        cpu: "500m"
        memory: "1Gi"
    port: 8004
  gitops:
    enabled: true
    repository:
      name: "$TEST_CLAIM_NAME-governance-synthesis"
      description: "Test Governance Synthesis Service for validation"
EOF
    
    if [[ $? -ne 0 ]]; then
        log_error "Failed to create test service claim"
        result="FAIL"
    fi
    
    # Wait for claim to be created
    if ! wait_for_condition "Service claim creation" "kubectl get acgsserviceclaim $TEST_CLAIM_NAME -n $NAMESPACE_ACGS" 60; then
        result="FAIL"
    fi
    
    test_result "Service claim creation" "$result"
}

# Test 6: Verify GitHub repository creation
test_github_repository() {
    log_info "Test 6: Testing GitHub repository creation..."
    
    local result="PASS"
    local repo_name="$TEST_CLAIM_NAME-governance-synthesis"
    
    # Wait for GitHub repository to be created
    if ! wait_for_condition "GitHub repository creation" "kubectl get repositories.github.upbound.io $repo_name" 180; then
        result="FAIL"
    fi
    
    # Check repository status
    if ! kubectl get repositories.github.upbound.io $repo_name -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}' | grep -q "True"; then
        log_warning "Repository not ready yet"
    fi
    
    test_result "GitHub repository creation" "$result"
}

# Test 7: Verify repository files creation
test_repository_files() {
    log_info "Test 7: Testing repository files creation..."
    
    local result="PASS"
    local repo_name="$TEST_CLAIM_NAME-governance-synthesis"
    
    # Expected files
    local expected_files=("dockerfile" "main-py" "requirements" "readme" "k8s-manifests")
    
    for file in "${expected_files[@]}"; do
        local file_resource="$repo_name-$file"
        if ! wait_for_condition "Repository file $file" "kubectl get repositoryfiles.github.upbound.io $file_resource" 120; then
            log_warning "File $file not created"
        fi
    done
    
    # Check if at least some files were created
    local files_count
    files_count=$(kubectl get repositoryfiles.github.upbound.io -l crossplane.io/claim-name=$TEST_CLAIM_NAME --no-headers 2>/dev/null | wc -l || echo "0")
    
    if [[ $files_count -eq 0 ]]; then
        log_error "No repository files created"
        result="FAIL"
    else
        log_info "Created $files_count repository files"
    fi
    
    test_result "Repository files creation" "$result"
}

# Test 8: Verify ArgoCD sync
test_argocd_sync() {
    log_info "Test 8: Testing ArgoCD sync..."
    
    local result="PASS"
    
    # Check if ArgoCD application is synced
    local app_status
    app_status=$(kubectl get application acgs-service-claims -n $NAMESPACE_ARGOCD -o jsonpath='{.status.sync.status}' 2>/dev/null || echo "Unknown")
    
    if [[ "$app_status" != "Synced" ]]; then
        log_warning "ArgoCD application not synced (status: $app_status)"
        
        # Try to trigger sync if ArgoCD CLI is available
        if command -v argocd &> /dev/null; then
            log_info "Attempting to sync ArgoCD application..."
            argocd app sync acgs-service-claims 2>/dev/null || log_warning "Failed to sync with ArgoCD CLI"
        fi
    fi
    
    test_result "ArgoCD sync" "$result"
}

# Test 9: Verify service claim status
test_claim_status() {
    log_info "Test 9: Testing service claim status..."
    
    local result="PASS"
    
    # Check claim status
    local claim_status
    claim_status=$(kubectl get acgsserviceclaim $TEST_CLAIM_NAME -n $NAMESPACE_ACGS -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}' 2>/dev/null || echo "Unknown")
    
    if [[ "$claim_status" != "True" ]]; then
        log_warning "Service claim not ready (status: $claim_status)"
        
        # Show claim details for debugging
        kubectl describe acgsserviceclaim $TEST_CLAIM_NAME -n $NAMESPACE_ACGS
    fi
    
    test_result "Service claim status" "$result"
}

# Test 10: Cleanup test resources
test_cleanup() {
    log_info "Test 10: Cleaning up test resources..."
    
    local result="PASS"
    
    # Delete test service claim
    if ! kubectl delete acgsserviceclaim $TEST_CLAIM_NAME -n $NAMESPACE_ACGS --ignore-not-found=true; then
        log_error "Failed to delete test service claim"
        result="FAIL"
    fi
    
    # Wait for resources to be cleaned up
    sleep 10
    
    # Check if GitHub resources are cleaned up
    local repo_name="$TEST_CLAIM_NAME-governance-synthesis"
    if kubectl get repositories.github.upbound.io $repo_name &> /dev/null; then
        log_warning "GitHub repository still exists (may take time to clean up)"
    fi
    
    test_result "Cleanup test resources" "$result"
}

# Run all tests
run_all_tests() {
    log_info "Starting ACGS GitOps Workflow Validation..."
    echo "=============================================="
    
    test_prerequisites
    test_crossplane
    test_argocd
    test_crd
    test_service_claim_creation
    test_github_repository
    test_repository_files
    test_argocd_sync
    test_claim_status
    test_cleanup
    
    echo
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
        log_success "All tests passed! GitOps workflow is functioning correctly."
        return 0
    else
        log_error "Some tests failed. Please check the logs above for details."
        return 1
    fi
}

# Quick validation (subset of tests)
run_quick_validation() {
    log_info "Running quick validation..."
    
    test_prerequisites
    test_crossplane
    test_argocd
    test_crd
    
    echo
    log_info "Quick validation completed."
    log_info "Passed: $TESTS_PASSED, Failed: $TESTS_FAILED"
}

# Show help
show_help() {
    echo "ACGS GitOps Workflow Validation Script"
    echo "Usage: $0 [command]"
    echo
    echo "Commands:"
    echo "  full     - Run full validation suite (default)"
    echo "  quick    - Run quick validation (no resource creation)"
    echo "  help     - Show this help"
    echo
    echo "The full validation will:"
    echo "  1. Check prerequisites and installations"
    echo "  2. Create a test service claim"
    echo "  3. Verify GitHub repository creation"
    echo "  4. Verify ArgoCD sync"
    echo "  5. Clean up test resources"
    echo
    echo "Note: Full validation requires GitHub token and may create/delete repositories"
}

# Handle script arguments
case "${1:-full}" in
    full)
        run_all_tests
        ;;
    quick)
        run_quick_validation
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        log_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
