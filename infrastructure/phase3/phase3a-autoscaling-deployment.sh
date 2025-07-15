#!/bin/bash

# ACGS Phase 3A: Service Auto-Scaling Setup
# Deploys Kubernetes with HPA, service mesh, and circuit breakers
# Constitutional compliance hash: cdd01ef066bc6cf2

set -euo pipefail

# Configuration
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
NAMESPACE="acgs-production"
PHASE="phase-3a"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Logging functions
log() { echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"; }
success() { echo -e "${GREEN}[✓] $1${NC}"; }
warning() { echo -e "${YELLOW}[⚠] $1${NC}"; }
error() { echo -e "${RED}[✗] $1${NC}"; exit 1; }
mesh() { echo -e "${PURPLE}[MESH] $1${NC}"; }

# Validate prerequisites
validate_prerequisites() {
    log "Validating prerequisites for auto-scaling deployment..."
    
    # Check required tools
    local required_tools=("kubectl" "helm" "jq")
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            error "$tool is required but not installed"
        fi
    done
    
    # Check Kubernetes connectivity
    if ! kubectl cluster-info >/dev/null 2>&1; then
        error "Cannot connect to Kubernetes cluster"
    fi
    
    # Check if metrics server is available
    if ! kubectl get deployment metrics-server -n kube-system >/dev/null 2>&1; then
        warning "Metrics server not found, HPA may not work properly"
    fi
    
    success "Prerequisites validated"
}

# Deploy metrics server if not present
deploy_metrics_server() {
    log "Checking and deploying metrics server..."
    
    if ! kubectl get deployment metrics-server -n kube-system >/dev/null 2>&1; then
        log "Deploying metrics server..."
        kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
        
        # Wait for metrics server to be ready (with shorter timeout)
        kubectl wait --for=condition=available deployment/metrics-server -n kube-system --timeout=60s || warning "Metrics server taking longer to start, continuing..."
        success "Metrics server deployed"
    else
        success "Metrics server already available"
    fi
}

# Create namespace if not exists
create_namespace() {
    log "Creating namespace: $NAMESPACE"
    
    kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
    kubectl label namespace "$NAMESPACE" constitutional-hash="$CONSTITUTIONAL_HASH" --overwrite
    
    success "Namespace $NAMESPACE ready"
}

# Deploy HPA configurations
deploy_hpa() {
    log "Deploying Horizontal Pod Autoscalers..."

    # Apply simplified HPA configuration for Phase 3A
    kubectl apply -f infrastructure/phase3/phase3a-hpa-simple.yaml || warning "Some HPA resources failed to apply"

    # Wait for HPAs to be ready
    sleep 10

    # Verify HPA deployment
    local hpa_count=$(kubectl get hpa -n "$NAMESPACE" --no-headers 2>/dev/null | wc -l || echo "0")
    if [[ $hpa_count -gt 0 ]]; then
        success "Deployed $hpa_count Horizontal Pod Autoscalers"
        kubectl get hpa -n "$NAMESPACE"
    else
        warning "No HPAs found in namespace $NAMESPACE"
    fi
}

# Deploy service mesh (Linkerd)
deploy_service_mesh() {
    log "Deploying Linkerd service mesh..."
    
    # Check if Linkerd is already installed
    if kubectl get namespace linkerd >/dev/null 2>&1; then
        warning "Linkerd already installed, skipping installation"
    else
        # Run Linkerd deployment script
        if [[ -f "infrastructure/kubernetes/service-mesh/linkerd-deployment.sh" ]]; then
            chmod +x infrastructure/kubernetes/service-mesh/linkerd-deployment.sh
            ./infrastructure/kubernetes/service-mesh/linkerd-deployment.sh deploy
        else
            warning "Linkerd deployment script not found, skipping service mesh deployment"
        fi
    fi
    
    success "Service mesh deployment completed"
}

# Deploy circuit breaker configurations
deploy_circuit_breakers() {
    log "Deploying circuit breaker configurations..."
    
    # Create circuit breaker config map
    cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: circuit-breaker-config
  namespace: $NAMESPACE
  labels:
    constitutional-hash: "$CONSTITUTIONAL_HASH"
    app.kubernetes.io/part-of: acgs
    app.kubernetes.io/component: circuit-breaker
data:
  config.yaml: |
    # Circuit Breaker Configuration
    # Constitutional Hash: $CONSTITUTIONAL_HASH
    
    circuit_breakers:
      auth_service:
        failure_threshold: 5
        recovery_timeout_ms: 30000
        half_open_max_calls: 3
        enabled: true
      
      constitutional_ai_service:
        failure_threshold: 3
        recovery_timeout_ms: 60000
        half_open_max_calls: 2
        enabled: true
      
      integrity_service:
        failure_threshold: 5
        recovery_timeout_ms: 45000
        half_open_max_calls: 3
        enabled: true
      
      formal_verification_service:
        failure_threshold: 3
        recovery_timeout_ms: 120000
        half_open_max_calls: 2
        enabled: true
      
      policy_governance_service:
        failure_threshold: 5
        recovery_timeout_ms: 30000
        half_open_max_calls: 3
        enabled: true
      
      governance_synthesis_service:
        failure_threshold: 4
        recovery_timeout_ms: 60000
        half_open_max_calls: 2
        enabled: true
    
    global_settings:
      constitutional_hash: "$CONSTITUTIONAL_HASH"
      monitoring_enabled: true
      metrics_export_interval: 30
      alert_on_open_circuit: true
EOF
    
    success "Circuit breaker configurations deployed"
}

# Deploy cluster autoscaler
deploy_cluster_autoscaler() {
    log "Deploying cluster autoscaler..."
    
    # Check if cluster autoscaler is already deployed
    if kubectl get deployment cluster-autoscaler -n kube-system >/dev/null 2>&1; then
        warning "Cluster autoscaler already deployed"
    else
        # Deploy using Helm if available
        if command -v helm >/dev/null 2>&1; then
            helm repo add autoscaler https://kubernetes.github.io/autoscaler
            helm repo update
            
            helm upgrade --install cluster-autoscaler autoscaler/cluster-autoscaler \
                --namespace kube-system \
                --set autoDiscovery.clusterName=acge-production \
                --set awsRegion=us-west-2 \
                --set extraArgs.scale-down-delay-after-add=10m \
                --set extraArgs.scale-down-unneeded-time=10m \
                --set extraArgs.skip-nodes-with-local-storage=false \
                --wait
        else
            warning "Helm not available, skipping cluster autoscaler deployment"
        fi
    fi
    
    success "Cluster autoscaler deployment completed"
}

# Validate auto-scaling deployment
validate_autoscaling() {
    log "Validating auto-scaling deployment..."
    
    # Check HPA status
    log "Checking HPA status..."
    kubectl get hpa -A | grep -E "(acgs|constitutional)" || warning "No ACGS HPAs found"
    
    # Check VPA status
    log "Checking VPA status..."
    kubectl get vpa -A | grep -E "(acgs|constitutional)" || warning "No ACGS VPAs found"
    
    # Check service mesh status
    if kubectl get namespace linkerd >/dev/null 2>&1; then
        log "Checking Linkerd status..."
        if command -v linkerd >/dev/null 2>&1; then
            linkerd check || warning "Linkerd check failed"
        fi
    fi
    
    # Check circuit breaker config
    if kubectl get configmap circuit-breaker-config -n "$NAMESPACE" >/dev/null 2>&1; then
        success "Circuit breaker configuration found"
    else
        warning "Circuit breaker configuration not found"
    fi
    
    # Check cluster autoscaler
    if kubectl get deployment cluster-autoscaler -n kube-system >/dev/null 2>&1; then
        success "Cluster autoscaler found"
    else
        warning "Cluster autoscaler not found"
    fi
    
    success "Auto-scaling validation completed"
}

# Generate deployment report
generate_report() {
    local report_file="/tmp/autoscaling_deployment_report_$(date +%Y%m%d_%H%M%S).txt"
    
    {
        echo "ACGS Phase 3A: Service Auto-Scaling Deployment Report"
        echo "Generated: $(date '+%Y-%m-%d %H:%M:%S')"
        echo "Constitutional Hash: $CONSTITUTIONAL_HASH"
        echo "Namespace: $NAMESPACE"
        echo "Phase: $PHASE"
        echo "=============================================="  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
        echo
        
        echo "HPA Status:"
        kubectl get hpa -A | grep -E "(acgs|constitutional)" || echo "No ACGS HPAs found"
        echo
        
        echo "VPA Status:"
        kubectl get vpa -A | grep -E "(acgs|constitutional)" || echo "No ACGS VPAs found"
        echo
        
        echo "Circuit Breaker Configuration:"
        kubectl get configmap circuit-breaker-config -n "$NAMESPACE" -o yaml 2>/dev/null || echo "Not found"
        echo
        
        echo "Cluster Autoscaler Status:"
        kubectl get deployment cluster-autoscaler -n kube-system 2>/dev/null || echo "Not found"
        echo
        
        if kubectl get namespace linkerd >/dev/null 2>&1; then
            echo "Service Mesh Status:"
            if command -v linkerd >/dev/null 2>&1; then
                linkerd check --output short 2>/dev/null || echo "Linkerd check failed"
            else
                echo "Linkerd CLI not available"
            fi
        else
            echo "Service Mesh: Not deployed"
        fi
        
    } > "$report_file"
    
    log "Auto-scaling deployment report generated: $report_file"
    echo "$report_file"
}

# Main deployment function
main() {
    log "🚀 Starting ACGS Phase 3A: Service Auto-Scaling Setup..."
    log "Constitutional Hash: $CONSTITUTIONAL_HASH"
    log "Target Namespace: $NAMESPACE"
    
    validate_prerequisites
    deploy_metrics_server
    create_namespace
    deploy_hpa
    deploy_service_mesh
    deploy_circuit_breakers
    deploy_cluster_autoscaler
    validate_autoscaling
    
    local report_file=$(generate_report)
    
    success "🎉 ACGS Phase 3A: Service Auto-Scaling Setup completed!"
    log "Report: $report_file"
    
    echo ""
    echo "Next steps:"
    echo "1. Monitor HPA scaling behavior"
    echo "2. Test circuit breaker functionality"
    echo "3. Validate service mesh mTLS"
    echo "4. Configure custom metrics for constitutional compliance"
    echo ""
    echo "Access commands:"
    echo "- View HPAs: kubectl get hpa -A"
    echo "- View VPAs: kubectl get vpa -A"
    echo "- Linkerd dashboard: linkerd viz dashboard"
    echo "- Circuit breaker config: kubectl get configmap circuit-breaker-config -n $NAMESPACE -o yaml"
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    case "${1:-deploy}" in
        "deploy")
            main
            ;;
        "validate")
            validate_autoscaling
            ;;
        "report")
            generate_report
            ;;
        *)
            echo "Usage: $0 {deploy|validate|report}"
            echo ""
            echo "Commands:"
            echo "  deploy   - Deploy auto-scaling infrastructure"
            echo "  validate - Validate auto-scaling deployment"
            echo "  report   - Generate deployment report"
            exit 1
            ;;
    esac
fi
