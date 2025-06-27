#!/bin/bash

# ACGE Phase 2 Complete Infrastructure Deployment
# Orchestrates deployment of all infrastructure components

set -euo pipefail

# Configuration
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
PHASE="phase-2"

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
    exit 1
}

# Deployment steps
DEPLOYMENT_STEPS=(
    "deploy_cluster"
    "deploy_namespaces"
    "deploy_storage"
    "deploy_istio"
    "deploy_blue_green_environments"
    "deploy_monitoring_stack"
    "deploy_elk_stack"
    "deploy_jaeger"
    "deploy_rollback_system"
    "validate_infrastructure"
)

# Deploy Kubernetes cluster
deploy_cluster() {
    log "Step 1: Deploying Kubernetes cluster..."
    
    if ./infrastructure/kubernetes/production/deploy-cluster.sh; then
        success "Kubernetes cluster deployment completed"
    else
        error "Kubernetes cluster deployment failed"
    fi
}

# Deploy namespaces
deploy_namespaces() {
    log "Step 2: Deploying namespaces..."
    
    # Apply namespace configurations
    kubectl apply -f infrastructure/kubernetes/blue-green/namespace.yaml
    kubectl apply -f infrastructure/kubernetes/production/namespace.yaml
    
    # Create Istio namespace
    kubectl create namespace istio-system --dry-run=client -o yaml | kubectl apply -f -
    
    success "Namespaces deployed"
}

# Deploy storage
deploy_storage() {
    log "Step 3: Deploying storage configuration..."
    
    # Apply cluster configuration (includes storage classes)
    kubectl apply -f infrastructure/kubernetes/production/cluster-config.yaml
    
    success "Storage configuration deployed"
}

# Deploy Istio service mesh
deploy_istio() {
    log "Step 4: Deploying Istio service mesh..."
    
    # Install Istio
    if command -v istioctl >/dev/null 2>&1; then
        istioctl install --set values.defaultRevision=default -y
        
        # Apply Istio configurations
        kubectl apply -f infrastructure/kubernetes/blue-green/istio-service-mesh.yaml
        
        success "Istio service mesh deployed"
    else
        warning "Istioctl not found, skipping Istio installation"
    fi
}

# Deploy blue-green environments
deploy_blue_green_environments() {
    log "Step 5: Deploying blue-green environments..."
    
    # Apply blue environment
    kubectl apply -f infrastructure/kubernetes/blue-green/blue-environment.yaml
    
    # Apply enhanced green environment with ACGE
    kubectl apply -f infrastructure/kubernetes/blue-green/acge-green-environment.yaml
    
    # Apply shared resources
    kubectl apply -f infrastructure/kubernetes/blue-green/shared-resources.yaml
    
    success "Blue-green environments deployed"
}

# Deploy monitoring stack
deploy_monitoring_stack() {
    log "Step 6: Deploying monitoring stack..."
    
    # Deploy Prometheus
    kubectl apply -f infrastructure/kubernetes/production/monitoring/acge-prometheus-config.yaml
    
    # Deploy alert rules
    kubectl apply -f infrastructure/kubernetes/production/monitoring/acge-alert-rules.yaml
    
    # Deploy Grafana dashboards
    kubectl apply -f infrastructure/kubernetes/production/monitoring/acge-grafana-dashboards.yaml
    
    # Install Prometheus using Helm if available
    if command -v helm >/dev/null 2>&1; then
        helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
        helm repo update
        
        helm upgrade --install prometheus prometheus-community/kube-prometheus-stack \
            --namespace acgs-shared \
            --create-namespace \
            --values infrastructure/kubernetes/production/monitoring/prometheus-values.yaml \
            --wait
    fi
    
    success "Monitoring stack deployed"
}

# Deploy ELK stack
deploy_elk_stack() {
    log "Step 7: Deploying ELK stack..."
    
    kubectl apply -f infrastructure/kubernetes/production/monitoring/elk-stack.yaml
    
    # Wait for Elasticsearch to be ready
    kubectl wait --for=condition=ready pod -l app=elasticsearch -n acgs-shared --timeout=300s
    
    success "ELK stack deployed"
}

# Deploy Jaeger tracing
deploy_jaeger() {
    log "Step 8: Deploying Jaeger tracing..."
    
    kubectl apply -f infrastructure/kubernetes/production/monitoring/jaeger-tracing.yaml
    
    # Wait for Jaeger to be ready
    kubectl wait --for=condition=ready pod -l app=jaeger -n acgs-shared --timeout=300s
    
    success "Jaeger tracing deployed"
}

# Deploy rollback system
deploy_rollback_system() {
    log "Step 9: Deploying automated rollback system..."
    
    kubectl apply -f infrastructure/kubernetes/blue-green/automated-rollback-system.yaml
    
    # Wait for rollback controller to be ready
    kubectl wait --for=condition=available deployment/rollback-controller -n acgs-shared --timeout=300s
    
    success "Automated rollback system deployed"
}

# Validate infrastructure
validate_infrastructure() {
    log "Step 10: Validating infrastructure..."
    
    if ./infrastructure/kubernetes/production/infrastructure-validation.sh; then
        success "Infrastructure validation passed"
    else
        error "Infrastructure validation failed"
    fi
}

# Wait for components to be ready
wait_for_readiness() {
    log "Waiting for all components to be ready..."
    
    # Wait for system pods
    kubectl wait --for=condition=ready pod --all -n kube-system --timeout=600s
    
    # Wait for shared namespace pods
    kubectl wait --for=condition=ready pod --all -n acgs-shared --timeout=600s
    
    # Wait for blue environment pods
    kubectl wait --for=condition=ready pod --all -n acgs-blue --timeout=300s || warning "Some blue environment pods not ready"
    
    # Wait for green environment pods
    kubectl wait --for=condition=ready pod --all -n acgs-green --timeout=300s || warning "Some green environment pods not ready"
    
    success "Components readiness check completed"
}

# Display deployment summary
display_summary() {
    log "Deployment summary:"
    
    echo ""
    echo "=========================================="
    echo "ACGE Phase 2 Infrastructure Deployment Summary"
    echo "=========================================="
    echo "Constitutional Hash: $CONSTITUTIONAL_HASH"
    echo "Phase: $PHASE"
    echo "Deployment Time: $(date)"
    echo ""
    
    # Check cluster status
    echo "Cluster Status:"
    kubectl get nodes -o wide
    echo ""
    
    # Check namespace status
    echo "Namespace Status:"
    kubectl get namespaces
    echo ""
    
    # Check service status
    echo "Service Status:"
    kubectl get services --all-namespaces | grep -E "(acgs-|prometheus|grafana|elasticsearch|jaeger)"
    echo ""
    
    # Check deployment status
    echo "Deployment Status:"
    kubectl get deployments --all-namespaces | grep -E "(acgs-|prometheus|grafana|elasticsearch|jaeger|rollback)"
    echo ""
    
    success "🎉 ACGE Phase 2 infrastructure deployment completed!"
    echo ""
    echo "Next steps:"
    echo "1. Verify all services are healthy"
    echo "2. Configure monitoring dashboards"
    echo "3. Test rollback procedures"
    echo "4. Begin service-by-service migration"
    echo ""
    echo "Access URLs (port-forward required):"
    echo "- Grafana: kubectl port-forward svc/grafana 3000:3000 -n acgs-shared"
    echo "- Prometheus: kubectl port-forward svc/prometheus 9090:9090 -n acgs-shared"
    echo "- Kibana: kubectl port-forward svc/kibana 5601:5601 -n acgs-shared"
    echo "- Jaeger: kubectl port-forward svc/jaeger 16686:16686 -n acgs-shared"
}

# Cleanup on failure
cleanup_on_failure() {
    error "Deployment failed. Cleaning up..."
    
    # Add cleanup logic here if needed
    warning "Manual cleanup may be required"
}

# Main execution
main() {
    log "🚀 Starting ACGE Phase 2 infrastructure deployment..."
    log "Constitutional Hash: $CONSTITUTIONAL_HASH"
    log "Phase: $PHASE"
    
    # Set trap for cleanup on failure
    trap cleanup_on_failure ERR
    
    # Execute deployment steps
    for step in "${DEPLOYMENT_STEPS[@]}"; do
        log "Executing: $step"
        $step
        sleep 5  # Brief pause between steps
    done
    
    # Wait for readiness
    wait_for_readiness
    
    # Display summary
    display_summary
    
    success "✅ ACGE Phase 2 infrastructure deployment completed successfully!"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check required tools
    local required_tools=("kubectl" "jq" "curl")
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            error "$tool is required but not installed"
        fi
    done
    
    # Check optional tools
    local optional_tools=("helm" "istioctl")
    for tool in "${optional_tools[@]}"; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            warning "$tool not found (optional)"
        fi
    done
    
    # Check Kubernetes connectivity
    if ! kubectl cluster-info >/dev/null 2>&1; then
        error "Cannot connect to Kubernetes cluster"
    fi
    
    success "Prerequisites check passed"
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    case "${1:-deploy}" in
        "deploy")
            check_prerequisites
            main
            ;;
        "validate")
            validate_infrastructure
            ;;
        "cleanup")
            warning "Cleanup functionality not implemented"
            ;;
        *)
            echo "Usage: $0 {deploy|validate|cleanup}"
            echo ""
            echo "Commands:"
            echo "  deploy   - Deploy complete ACGE Phase 2 infrastructure"
            echo "  validate - Validate infrastructure readiness"
            echo "  cleanup  - Clean up deployed resources"
            exit 1
            ;;
    esac
fi
