#!/bin/bash

# ACGE Phase 2 Infrastructure Readiness Validation
# Comprehensive validation of blue-green infrastructure, monitoring, and rollback systems

set -euo pipefail

# Configuration
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
NAMESPACE_SHARED="acgs-shared"
NAMESPACE_BLUE="acgs-blue"
NAMESPACE_GREEN="acgs-green"

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

# Validation results tracking
VALIDATION_RESULTS=()
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
WARNING_CHECKS=0

# Add validation result
add_result() {
    local status=$1
    local message=$2
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    case "$status" in
        "PASS")
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
            success "$message"
            ;;
        "WARN")
            WARNING_CHECKS=$((WARNING_CHECKS + 1))
            warning "$message"
            ;;
        "FAIL")
            FAILED_CHECKS=$((FAILED_CHECKS + 1))
            error "$message"
            ;;
    esac
    
    VALIDATION_RESULTS+=("$status: $message")
}

# Validate Kubernetes cluster
validate_cluster() {
    log "Validating Kubernetes cluster..."
    
    # Check cluster connectivity
    if kubectl cluster-info >/dev/null 2>&1; then
        add_result "PASS" "Cluster connectivity established"
    else
        add_result "FAIL" "Cannot connect to Kubernetes cluster"
        return 1
    fi
    
    # Check node count and status
    local node_count
    node_count=$(kubectl get nodes --no-headers | wc -l)
    if [[ $node_count -ge 9 ]]; then
        add_result "PASS" "Node count: $node_count (minimum 9 required)"
    else
        add_result "FAIL" "Insufficient nodes: $node_count (minimum 9 required)"
    fi
    
    # Check node readiness
    local not_ready_nodes
    not_ready_nodes=$(kubectl get nodes --no-headers | grep -v " Ready " | wc -l)
    if [[ $not_ready_nodes -eq 0 ]]; then
        add_result "PASS" "All nodes are ready"
    else
        add_result "FAIL" "$not_ready_nodes nodes are not ready"
    fi
    
    # Check system pods
    local not_running_pods
    not_running_pods=$(kubectl get pods -n kube-system --no-headers | grep -v " Running " | grep -v " Completed " | wc -l)
    if [[ $not_running_pods -eq 0 ]]; then
        add_result "PASS" "All system pods are running"
    else
        add_result "FAIL" "$not_running_pods system pods are not running"
    fi
}

# Validate namespaces
validate_namespaces() {
    log "Validating namespaces..."
    
    local namespaces=("$NAMESPACE_SHARED" "$NAMESPACE_BLUE" "$NAMESPACE_GREEN" "istio-system")
    
    for ns in "${namespaces[@]}"; do
        if kubectl get namespace "$ns" >/dev/null 2>&1; then
            add_result "PASS" "Namespace $ns exists"
        else
            add_result "FAIL" "Namespace $ns not found"
        fi
    done
    
    # Check constitutional hash in shared namespace
    if kubectl get configmap acge-constitutional-config -n "$NAMESPACE_SHARED" >/dev/null 2>&1; then
        local stored_hash
        stored_hash=$(kubectl get configmap acge-constitutional-config -n "$NAMESPACE_SHARED" -o jsonpath='{.data.constitutional-hash}')
        if [[ "$stored_hash" == "$CONSTITUTIONAL_HASH" ]]; then
            add_result "PASS" "Constitutional hash validated: $CONSTITUTIONAL_HASH"
        else
            add_result "FAIL" "Constitutional hash mismatch. Expected: $CONSTITUTIONAL_HASH, Got: $stored_hash"
        fi
    else
        add_result "FAIL" "Constitutional configuration not found"
    fi
}

# Validate blue-green environments
validate_blue_green_environments() {
    log "Validating blue-green environments..."
    
    # Check blue environment services
    local blue_services=("acgs-auth-service-blue" "acgs-ac-service-blue" "acgs-pgc-service-blue")
    for service in "${blue_services[@]}"; do
        if kubectl get service "$service" -n "$NAMESPACE_BLUE" >/dev/null 2>&1; then
            add_result "PASS" "Blue service $service exists"
        else
            add_result "WARN" "Blue service $service not found"
        fi
    done
    
    # Check green environment services
    local green_services=("acgs-auth-service-green" "acgs-ac-service-green" "acgs-integrity-service-green")
    for service in "${green_services[@]}"; do
        if kubectl get service "$service" -n "$NAMESPACE_GREEN" >/dev/null 2>&1; then
            add_result "PASS" "Green service $service exists"
        else
            add_result "WARN" "Green service $service not found"
        fi
    done
    
    # Check ACGE model service
    if kubectl get service acge-model-service -n "$NAMESPACE_SHARED" >/dev/null 2>&1; then
        add_result "PASS" "ACGE model service exists"
    else
        add_result "FAIL" "ACGE model service not found"
    fi
}

# Validate Istio service mesh
validate_istio() {
    log "Validating Istio service mesh..."
    
    # Check Istio installation
    if kubectl get namespace istio-system >/dev/null 2>&1; then
        add_result "PASS" "Istio namespace exists"
        
        # Check Istio pods
        local istio_pods_running
        istio_pods_running=$(kubectl get pods -n istio-system --no-headers | grep " Running " | wc -l)
        if [[ $istio_pods_running -gt 0 ]]; then
            add_result "PASS" "Istio pods running: $istio_pods_running"
        else
            add_result "FAIL" "No Istio pods running"
        fi
        
        # Check VirtualService
        if kubectl get virtualservice acgs-blue-green-routing -n "$NAMESPACE_SHARED" >/dev/null 2>&1; then
            add_result "PASS" "Blue-green VirtualService exists"
        else
            add_result "FAIL" "Blue-green VirtualService not found"
        fi
        
        # Check Gateway
        if kubectl get gateway acgs-gateway -n "$NAMESPACE_SHARED" >/dev/null 2>&1; then
            add_result "PASS" "ACGS Gateway exists"
        else
            add_result "FAIL" "ACGS Gateway not found"
        fi
    else
        add_result "FAIL" "Istio not installed"
    fi
}

# Validate monitoring stack
validate_monitoring() {
    log "Validating monitoring stack..."
    
    # Check Prometheus
    if kubectl get service prometheus -n "$NAMESPACE_SHARED" >/dev/null 2>&1; then
        add_result "PASS" "Prometheus service exists"
        
        # Test Prometheus connectivity
        if kubectl run prometheus-test --image=curlimages/curl --rm -i --restart=Never -- \
            curl -f -s "http://prometheus.$NAMESPACE_SHARED.svc.cluster.local:9090/api/v1/status/config" >/dev/null 2>&1; then
            add_result "PASS" "Prometheus is accessible"
        else
            add_result "FAIL" "Prometheus is not accessible"
        fi
    else
        add_result "FAIL" "Prometheus service not found"
    fi
    
    # Check Grafana
    if kubectl get service grafana -n "$NAMESPACE_SHARED" >/dev/null 2>&1; then
        add_result "PASS" "Grafana service exists"
    else
        add_result "WARN" "Grafana service not found"
    fi
    
    # Check AlertManager
    if kubectl get service alertmanager -n "$NAMESPACE_SHARED" >/dev/null 2>&1; then
        add_result "PASS" "AlertManager service exists"
    else
        add_result "WARN" "AlertManager service not found"
    fi
}

# Validate ELK stack
validate_elk_stack() {
    log "Validating ELK stack..."
    
    # Check Elasticsearch
    if kubectl get service elasticsearch -n "$NAMESPACE_SHARED" >/dev/null 2>&1; then
        add_result "PASS" "Elasticsearch service exists"
        
        # Test Elasticsearch connectivity
        if kubectl run elasticsearch-test --image=curlimages/curl --rm -i --restart=Never -- \
            curl -f -s "http://elasticsearch.$NAMESPACE_SHARED.svc.cluster.local:9200/_cluster/health" >/dev/null 2>&1; then
            add_result "PASS" "Elasticsearch is accessible"
        else
            add_result "FAIL" "Elasticsearch is not accessible"
        fi
    else
        add_result "FAIL" "Elasticsearch service not found"
    fi
    
    # Check Logstash
    if kubectl get service logstash -n "$NAMESPACE_SHARED" >/dev/null 2>&1; then
        add_result "PASS" "Logstash service exists"
    else
        add_result "WARN" "Logstash service not found"
    fi
    
    # Check Kibana
    if kubectl get service kibana -n "$NAMESPACE_SHARED" >/dev/null 2>&1; then
        add_result "PASS" "Kibana service exists"
    else
        add_result "WARN" "Kibana service not found"
    fi
}

# Validate Jaeger tracing
validate_jaeger() {
    log "Validating Jaeger tracing..."
    
    # Check Jaeger service
    if kubectl get service jaeger -n "$NAMESPACE_SHARED" >/dev/null 2>&1; then
        add_result "PASS" "Jaeger service exists"
        
        # Test Jaeger connectivity
        if kubectl run jaeger-test --image=curlimages/curl --rm -i --restart=Never -- \
            curl -f -s "http://jaeger.$NAMESPACE_SHARED.svc.cluster.local:16686/api/services" >/dev/null 2>&1; then
            add_result "PASS" "Jaeger is accessible"
        else
            add_result "FAIL" "Jaeger is not accessible"
        fi
    else
        add_result "FAIL" "Jaeger service not found"
    fi
    
    # Check OpenTelemetry Collector
    if kubectl get service otel-collector -n "$NAMESPACE_SHARED" >/dev/null 2>&1; then
        add_result "PASS" "OpenTelemetry Collector service exists"
    else
        add_result "WARN" "OpenTelemetry Collector service not found"
    fi
}

# Validate rollback system
validate_rollback_system() {
    log "Validating automated rollback system..."
    
    # Check rollback controller
    if kubectl get deployment rollback-controller -n "$NAMESPACE_SHARED" >/dev/null 2>&1; then
        add_result "PASS" "Rollback controller deployment exists"
        
        local ready_replicas
        ready_replicas=$(kubectl get deployment rollback-controller -n "$NAMESPACE_SHARED" -o jsonpath='{.status.readyReplicas}')
        if [[ "$ready_replicas" -ge "1" ]]; then
            add_result "PASS" "Rollback controller is ready"
        else
            add_result "FAIL" "Rollback controller not ready"
        fi
    else
        add_result "FAIL" "Rollback controller deployment not found"
    fi
    
    # Check rollback monitor CronJob
    if kubectl get cronjob rollback-monitor -n "$NAMESPACE_SHARED" >/dev/null 2>&1; then
        add_result "PASS" "Rollback monitor CronJob exists"
    else
        add_result "FAIL" "Rollback monitor CronJob not found"
    fi
    
    # Check rollback notifier
    if kubectl get deployment rollback-notifier -n "$NAMESPACE_SHARED" >/dev/null 2>&1; then
        add_result "PASS" "Rollback notifier deployment exists"
    else
        add_result "WARN" "Rollback notifier deployment not found"
    fi
}

# Validate storage
validate_storage() {
    log "Validating storage configuration..."
    
    # Check storage classes
    local storage_classes=("acge-fast-ssd" "acge-constitutional-data")
    for sc in "${storage_classes[@]}"; do
        if kubectl get storageclass "$sc" >/dev/null 2>&1; then
            add_result "PASS" "Storage class $sc exists"
        else
            add_result "FAIL" "Storage class $sc not found"
        fi
    done
    
    # Check persistent volumes
    local pv_count
    pv_count=$(kubectl get pv --no-headers | wc -l)
    if [[ $pv_count -gt 0 ]]; then
        add_result "PASS" "Persistent volumes available: $pv_count"
    else
        add_result "WARN" "No persistent volumes found"
    fi
}

# Performance validation
validate_performance() {
    log "Validating performance requirements..."
    
    # Check resource quotas
    if kubectl get resourcequota -n "$NAMESPACE_SHARED" >/dev/null 2>&1; then
        add_result "PASS" "Resource quotas configured"
    else
        add_result "WARN" "Resource quotas not configured"
    fi
    
    # Check HPA
    local hpa_count
    hpa_count=$(kubectl get hpa --all-namespaces --no-headers | wc -l)
    if [[ $hpa_count -gt 0 ]]; then
        add_result "PASS" "Horizontal Pod Autoscalers configured: $hpa_count"
    else
        add_result "WARN" "No Horizontal Pod Autoscalers found"
    fi
    
    # Check cluster autoscaler
    if kubectl get deployment cluster-autoscaler -n kube-system >/dev/null 2>&1; then
        add_result "PASS" "Cluster autoscaler deployed"
    else
        add_result "WARN" "Cluster autoscaler not found"
    fi
}

# Generate validation report
generate_report() {
    log "Generating infrastructure validation report..."
    
    echo ""
    echo "=========================================="  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    echo "ACGE Phase 2 Infrastructure Validation Report"
    echo "=========================================="  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    echo "Constitutional Hash: $CONSTITUTIONAL_HASH"
    echo "Validation Time: $(date)"
    echo ""
    echo "Results Summary:"
    echo "  Total Checks: $TOTAL_CHECKS"
    echo "  Passed: $PASSED_CHECKS"
    echo "  Warnings: $WARNING_CHECKS"
    echo "  Failed: $FAILED_CHECKS"
    echo ""
    
    # Calculate success percentage
    local success_percentage=$((PASSED_CHECKS * 100 / TOTAL_CHECKS))
    
    if [[ $success_percentage -ge 95 ]]; then
        success "Infrastructure validation: $success_percentage% - READY FOR PHASE 2"
        echo "🟢 Infrastructure is ready for service migration!"
    elif [[ $success_percentage -ge 85 ]]; then
        warning "Infrastructure validation: $success_percentage% - NEEDS ATTENTION"
        echo "🟡 Infrastructure needs some fixes before migration"
    else
        error "Infrastructure validation: $success_percentage% - NOT READY"
        echo "🔴 Infrastructure requires significant fixes"
    fi
    
    echo ""
    echo "Detailed Results:"
    echo "=================="
    for result in "${VALIDATION_RESULTS[@]}"; do
        echo "$result"
    done
    
    echo ""
    if [[ $success_percentage -ge 95 ]]; then
        success "✅ Infrastructure validation completed successfully!"
        echo "Next steps:"
        echo "1. Begin service-by-service migration"
        echo "2. Monitor constitutional compliance during migration"
        echo "3. Validate performance targets"
    else
        error "❌ Infrastructure validation failed"
        echo "Please address the failed checks and re-run validation"
    fi
    
    return $((FAILED_CHECKS > 0 ? 1 : 0))
}

# Main execution
main() {
    log "Starting ACGE Phase 2 infrastructure validation..."
    
    validate_cluster
    validate_namespaces
    validate_blue_green_environments
    validate_istio
    validate_monitoring
    validate_elk_stack
    validate_jaeger
    validate_rollback_system
    validate_storage
    validate_performance
    
    generate_report
}

# Execute main function
main "$@"
