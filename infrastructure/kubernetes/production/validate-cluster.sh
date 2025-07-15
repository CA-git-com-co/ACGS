#!/bin/bash

# ACGE Phase 2 Kubernetes Cluster Validation Script
# Comprehensive validation of production cluster readiness

set -euo pipefail

# Configuration
CLUSTER_NAME="acge-production"
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
NAMESPACE="acgs-pgp"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

success() {
    echo -e "${GREEN}[✓] $1${NC}"
}

warning() {
    echo -e "${YELLOW}[⚠] $1${NC}"
}

error() {
    echo -e "${RED}[✗] $1${NC}"
}

# Validation results
VALIDATION_RESULTS=()
TOTAL_CHECKS=0
PASSED_CHECKS=0

# Add validation result
add_result() {
    local status=$1
    local message=$2
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    if [[ "$status" == "PASS" ]]; then
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
        success "$message"
    elif [[ "$status" == "WARN" ]]; then
        warning "$message"
    else
        error "$message"
    fi
    
    VALIDATION_RESULTS+=("$status: $message")
}

# Check cluster connectivity
check_cluster_connectivity() {
    log "Checking cluster connectivity..."
    
    if kubectl cluster-info >/dev/null 2>&1; then
        add_result "PASS" "Cluster connectivity established"
    else
        add_result "FAIL" "Cannot connect to cluster"
        return 1
    fi
}

# Check node status and specifications
check_nodes() {
    log "Checking node status and specifications..."
    
    # Check total node count
    NODE_COUNT=$(kubectl get nodes --no-headers | wc -l)
    if [[ $NODE_COUNT -ge 9 ]]; then
        add_result "PASS" "Node count: $NODE_COUNT (minimum 9 required)"
    else
        add_result "FAIL" "Insufficient nodes: $NODE_COUNT (minimum 9 required)"
    fi
    
    # Check node readiness
    NOT_READY_NODES=$(kubectl get nodes --no-headers | grep -v " Ready " | wc -l)
    if [[ $NOT_READY_NODES -eq 0 ]]; then
        add_result "PASS" "All nodes are ready"
    else
        add_result "FAIL" "$NOT_READY_NODES nodes are not ready"
    fi
    
    # Check node specifications
    log "Validating node specifications..."
    kubectl get nodes -o custom-columns="NAME:.metadata.name,CPU:.status.capacity.cpu,MEMORY:.status.capacity.memory,STORAGE:.status.capacity.ephemeral-storage" --no-headers | while read -r line; do
        NODE_NAME=$(echo "$line" | awk '{print $1}')
        CPU_CORES=$(echo "$line" | awk '{print $2}' | sed 's/m$//' | awk '{print int($1/1000)}')
        MEMORY_GB=$(echo "$line" | awk '{print $3}' | sed 's/Ki$//' | awk '{print int($1/1024/1024)}')
        
        if [[ $CPU_CORES -ge 15 ]] && [[ $MEMORY_GB -ge 60 ]]; then
            add_result "PASS" "Node $NODE_NAME meets specifications (${CPU_CORES} cores, ${MEMORY_GB}GB)"
        else
            add_result "WARN" "Node $NODE_NAME below specifications (${CPU_CORES} cores, ${MEMORY_GB}GB)"
        fi
    done
}

# Check system pods
check_system_pods() {
    log "Checking system pods..."
    
    # Check kube-system namespace
    NOT_RUNNING_PODS=$(kubectl get pods -n kube-system --no-headers | grep -v " Running " | grep -v " Completed " | wc -l)
    if [[ $NOT_RUNNING_PODS -eq 0 ]]; then
        add_result "PASS" "All system pods are running"
    else
        add_result "FAIL" "$NOT_RUNNING_PODS system pods are not running"
    fi
    
    # Check essential add-ons
    ESSENTIAL_ADDONS=("aws-load-balancer-controller" "cluster-autoscaler" "coredns" "kube-proxy")
    for addon in "${ESSENTIAL_ADDONS[@]}"; do
        if kubectl get pods -n kube-system | grep -q "$addon"; then
            ADDON_STATUS=$(kubectl get pods -n kube-system | grep "$addon" | awk '{print $3}' | head -1)
            if [[ "$ADDON_STATUS" == "Running" ]]; then
                add_result "PASS" "Add-on $addon is running"
            else
                add_result "FAIL" "Add-on $addon status: $ADDON_STATUS"
            fi
        else
            add_result "FAIL" "Add-on $addon not found"
        fi
    done
}

# Check storage configuration
check_storage() {
    log "Checking storage configuration..."
    
    # Check storage classes
    STORAGE_CLASSES=("acge-fast-ssd" "acge-constitutional-data")
    for sc in "${STORAGE_CLASSES[@]}"; do
        if kubectl get storageclass "$sc" >/dev/null 2>&1; then
            add_result "PASS" "Storage class $sc exists"
        else
            add_result "FAIL" "Storage class $sc not found"
        fi
    done
    
    # Check default storage class
    if kubectl get storageclass | grep -q "(default)"; then
        DEFAULT_SC=$(kubectl get storageclass | grep "(default)" | awk '{print $1}')
        add_result "PASS" "Default storage class: $DEFAULT_SC"
    else
        add_result "FAIL" "No default storage class configured"
    fi
}

# Check networking
check_networking() {
    log "Checking networking configuration..."
    
    # Check service mesh (if installed)
    if kubectl get namespace istio-system >/dev/null 2>&1; then
        ISTIO_PODS=$(kubectl get pods -n istio-system --no-headers | grep -c " Running ")
        if [[ $ISTIO_PODS -gt 0 ]]; then
            add_result "PASS" "Istio service mesh is running ($ISTIO_PODS pods)"
        else
            add_result "FAIL" "Istio service mesh pods not running"
        fi
    else
        add_result "WARN" "Istio service mesh not installed (will be configured later)"
    fi
    
    # Check DNS resolution
    if kubectl run test-dns --image=busybox --rm -it --restart=Never -- nslookup kubernetes.default >/dev/null 2>&1; then
        add_result "PASS" "DNS resolution working"
    else
        add_result "FAIL" "DNS resolution not working"
    fi
}

# Check namespace and configuration
check_namespace_config() {
    log "Checking namespace and configuration..."
    
    # Check namespace exists
    if kubectl get namespace "$NAMESPACE" >/dev/null 2>&1; then
        add_result "PASS" "Namespace $NAMESPACE exists"
    else
        add_result "FAIL" "Namespace $NAMESPACE not found"
        return 1
    fi
    
    # Check constitutional hash configuration
    if kubectl get configmap acge-constitutional-config -n "$NAMESPACE" >/dev/null 2>&1; then
        STORED_HASH=$(kubectl get configmap acge-constitutional-config -n "$NAMESPACE" -o jsonpath='{.data.constitutional-hash}')
        if [[ "$STORED_HASH" == "$CONSTITUTIONAL_HASH" ]]; then
            add_result "PASS" "Constitutional hash validated: $CONSTITUTIONAL_HASH"
        else
            add_result "FAIL" "Constitutional hash mismatch. Expected: $CONSTITUTIONAL_HASH, Got: $STORED_HASH"
        fi
    else
        add_result "FAIL" "Constitutional configuration not found"
    fi
    
    # Check resource quotas
    if kubectl get resourcequota -n "$NAMESPACE" >/dev/null 2>&1; then
        add_result "PASS" "Resource quotas configured"
    else
        add_result "WARN" "Resource quotas not configured"
    fi
}

# Check security configuration
check_security() {
    log "Checking security configuration..."
    
    # Check RBAC
    if kubectl auth can-i get pods --as=system:serviceaccount:default:default >/dev/null 2>&1; then
        add_result "WARN" "Default service account has pod access (review RBAC)"
    else
        add_result "PASS" "RBAC properly configured"
    fi
    
    # Check pod security policies/standards
    if kubectl get podsecuritypolicy >/dev/null 2>&1; then
        PSP_COUNT=$(kubectl get podsecuritypolicy --no-headers | wc -l)
        add_result "PASS" "Pod security policies configured ($PSP_COUNT policies)"
    else
        add_result "WARN" "Pod security policies not configured"
    fi
}

# Check GPU nodes (if applicable)
check_gpu_nodes() {
    log "Checking GPU nodes..."
    
    GPU_NODES=$(kubectl get nodes -l nvidia.com/gpu=true --no-headers 2>/dev/null | wc -l)
    if [[ $GPU_NODES -gt 0 ]]; then
        add_result "PASS" "GPU nodes available: $GPU_NODES"
        
        # Check NVIDIA device plugin
        if kubectl get pods -n kube-system | grep -q nvidia-device-plugin; then
            add_result "PASS" "NVIDIA device plugin running"
        else
            add_result "FAIL" "NVIDIA device plugin not running"
        fi
    else
        add_result "WARN" "No GPU nodes found (will be configured if needed)"
    fi
}

# Performance validation
check_performance() {
    log "Checking performance characteristics..."
    
    # Check cluster autoscaler
    if kubectl get deployment cluster-autoscaler -n kube-system >/dev/null 2>&1; then
        CA_STATUS=$(kubectl get deployment cluster-autoscaler -n kube-system -o jsonpath='{.status.readyReplicas}')
        if [[ "$CA_STATUS" == "1" ]]; then
            add_result "PASS" "Cluster autoscaler is ready"
        else
            add_result "FAIL" "Cluster autoscaler not ready"
        fi
    else
        add_result "FAIL" "Cluster autoscaler not found"
    fi
    
    # Check load balancer controller
    if kubectl get deployment aws-load-balancer-controller -n kube-system >/dev/null 2>&1; then
        LB_STATUS=$(kubectl get deployment aws-load-balancer-controller -n kube-system -o jsonpath='{.status.readyReplicas}')
        if [[ "$LB_STATUS" -ge "1" ]]; then
            add_result "PASS" "AWS Load Balancer Controller is ready"
        else
            add_result "FAIL" "AWS Load Balancer Controller not ready"
        fi
    else
        add_result "FAIL" "AWS Load Balancer Controller not found"
    fi
}

# Generate validation report
generate_report() {
    log "Generating validation report..."
    
    echo ""
    echo "=========================================="  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    echo "ACGE Phase 2 Cluster Validation Report"
    echo "=========================================="  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    echo "Cluster: $CLUSTER_NAME"
    echo "Namespace: $NAMESPACE"
    echo "Constitutional Hash: $CONSTITUTIONAL_HASH"
    echo "Validation Time: $(date)"
    echo ""
    echo "Results: $PASSED_CHECKS/$TOTAL_CHECKS checks passed"
    echo ""
    
    # Calculate success percentage
    SUCCESS_PERCENTAGE=$((PASSED_CHECKS * 100 / TOTAL_CHECKS))
    
    if [[ $SUCCESS_PERCENTAGE -ge 90 ]]; then
        success "Cluster validation: $SUCCESS_PERCENTAGE% - READY FOR PHASE 2"
    elif [[ $SUCCESS_PERCENTAGE -ge 75 ]]; then
        warning "Cluster validation: $SUCCESS_PERCENTAGE% - NEEDS ATTENTION"
    else
        error "Cluster validation: $SUCCESS_PERCENTAGE% - NOT READY"
    fi
    
    echo ""
    echo "Detailed Results:"
    echo "=================="
    for result in "${VALIDATION_RESULTS[@]}"; do
        echo "$result"
    done
    
    echo ""
    if [[ $SUCCESS_PERCENTAGE -ge 90 ]]; then
        success "Cluster is ready for Phase 2 blue-green deployment!"
        echo "Next steps:"
        echo "1. Configure blue-green environments"
        echo "2. Deploy monitoring stack"
        echo "3. Implement automated rollback system"
    else
        error "Cluster requires fixes before proceeding with Phase 2"
        echo "Please address the failed checks and re-run validation"
    fi
}

# Main execution
main() {
    log "Starting ACGE Phase 2 cluster validation..."
    
    check_cluster_connectivity
    check_nodes
    check_system_pods
    check_storage
    check_networking
    check_namespace_config
    check_security
    check_gpu_nodes
    check_performance
    
    generate_report
}

# Execute main function
main "$@"
