# Constitutional Hash: cdd01ef066bc6cf2
# ACGS-2 Constitutional Compliance Validation
#!/bin/bash

# ACGS GitOps Deployment Script
# Automated deployment of Crossplane and ArgoCD for ACGS services

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
GITHUB_TOKEN="${GITHUB_TOKEN:-}"
NAMESPACE_CROSSPLANE="crossplane-system"
NAMESPACE_ARGOCD="argocd"
NAMESPACE_ACGS="acgs-system"

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed"
        exit 1
    fi
    
    # Check helm
    if ! command -v helm &> /dev/null; then
        log_error "helm is not installed"
        exit 1
    fi
    
    # Check cluster connectivity
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi
    
    # Check GitHub token
    if [[ -z "$GITHUB_TOKEN" ]]; then
        log_error "GITHUB_TOKEN environment variable is not set"
        log_info "Please set your GitHub token: export GITHUB_TOKEN=your_token"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Install Crossplane
install_crossplane() {
    log_info "Installing Crossplane..."
    
    # Add Helm repository
    helm repo add crossplane-stable https://charts.crossplane.io/stable
    helm repo update
    
    # Create namespace
    kubectl create namespace $NAMESPACE_CROSSPLANE --dry-run=client -o yaml | kubectl apply -f -
    
    # Install Crossplane
    helm upgrade --install crossplane crossplane-stable/crossplane \
        --namespace $NAMESPACE_CROSSPLANE \
        --set args='{--debug}' \
        --wait \
        --timeout=10m
    
    # Wait for Crossplane to be ready
    kubectl wait --for=condition=ready pod -l app=crossplane -n $NAMESPACE_CROSSPLANE --timeout=300s
    
    log_success "Crossplane installed successfully"
}

# Install ArgoCD
install_argocd() {
    log_info "Installing ArgoCD..."
    
    # Create namespace
    kubectl create namespace $NAMESPACE_ARGOCD --dry-run=client -o yaml | kubectl apply -f -
    
    # Install ArgoCD
    kubectl apply -n $NAMESPACE_ARGOCD -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
    
    # Wait for ArgoCD to be ready
    kubectl wait --for=condition=available --timeout=600s deployment/argocd-server -n $NAMESPACE_ARGOCD
    kubectl wait --for=condition=available --timeout=600s deployment/argocd-application-controller -n $NAMESPACE_ARGOCD
    
    log_success "ArgoCD installed successfully"
    
    # Get admin password
    local admin_password
    admin_password=os.environ.get("PASSWORD"){.data.password}" | base64 -d)
    log_info "ArgoCD admin password: os.environ.get("PASSWORD")
}

# Configure GitHub credentials
configure_github() {
    log_info "Configuring GitHub credentials..."
    
    # Create GitHub credentials secret
    kubectl create secret generic github-credentials \
        --from-literal=token=$GITHUB_TOKEN \
        --namespace $NAMESPACE_CROSSPLANE \
        --dry-run=client -o yaml | kubectl apply -f -
    
    log_success "GitHub credentials configured"
}

# Deploy Crossplane providers
deploy_providers() {
    log_info "Deploying Crossplane providers..."
    
    # Apply GitHub provider
    kubectl apply -f crossplane/providers/github-provider.yaml
    
    # Wait for providers to be ready
    log_info "Waiting for GitHub provider to be ready..."
    kubectl wait --for=condition=installed provider/provider-github --timeout=300s
    kubectl wait --for=condition=healthy provider/provider-github --timeout=300s
    
    log_info "Waiting for KCL function to be ready..."
    kubectl wait --for=condition=installed function/function-kcl --timeout=300s
    kubectl wait --for=condition=healthy function/function-kcl --timeout=300s
    
    log_success "Providers deployed successfully"
}

# Deploy CRD and compositions
deploy_compositions() {
    log_info "Deploying CRD and compositions..."
    
    # Apply CRD
    kubectl apply -f crossplane/definitions/githubclaim.yaml
    kubectl wait --for condition=established crd/acgsserviceclaims.acgs.io --timeout=60s
    
    # Apply composition
    kubectl apply -f crossplane/compositions/acgs-service.yaml
    
    log_success "CRD and compositions deployed successfully"
}

# Deploy ArgoCD applications
deploy_argocd_apps() {
    log_info "Deploying ArgoCD applications..."
    
    # Create ACGS namespace
    kubectl create namespace $NAMESPACE_ACGS --dry-run=client -o yaml | kubectl apply -f -
    
    # Apply ArgoCD applications
    kubectl apply -f argocd/applications/acgs-claims.yaml
    
    log_success "ArgoCD applications deployed successfully"
}

# Verify deployment
verify_deployment() {
    log_info "Verifying deployment..."
    
    # Check Crossplane
    log_info "Checking Crossplane components..."
    kubectl get providers
    kubectl get functions
    kubectl get compositions
    
    # Check ArgoCD
    log_info "Checking ArgoCD applications..."
    kubectl get applications -n $NAMESPACE_ARGOCD
    
    # Check CRD
    log_info "Checking ACGS CRD..."
    kubectl get crds | grep acgs
    
    log_success "Deployment verification completed"
}

# Deploy example service
deploy_example() {
    log_info "Deploying example service claim..."
    
    # Copy example to claims directory
    cp examples/gs-service-claim.yaml claims/
    
    # Apply example
    kubectl apply -f examples/gs-service-claim.yaml
    
    log_info "Example service claim deployed. Monitor with:"
    log_info "kubectl get acgsserviceclaims -n $NAMESPACE_ACGS -w"
}

# Main deployment function
main() {
    log_info "Starting ACGS GitOps deployment..."
    
    check_prerequisites
    install_crossplane
    install_argocd
    configure_github
    deploy_providers
    deploy_compositions
    deploy_argocd_apps
    verify_deployment
    
    log_success "ACGS GitOps deployment completed successfully!"
    
    # Optional: deploy example
    read -p "Deploy example service claim? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        deploy_example
    fi
    
    log_info "Deployment summary:"
    log_info "- Crossplane: $NAMESPACE_CROSSPLANE namespace"
    log_info "- ArgoCD: $NAMESPACE_ARGOCD namespace"
    log_info "- ACGS Services: $NAMESPACE_ACGS namespace"
    log_info ""
    log_info "Next steps:"
    log_info "1. Access ArgoCD UI: kubectl port-forward svc/argocd-server -n $NAMESPACE_ARGOCD 8080:443"
    log_info "2. Create service claims: kubectl apply -f examples/gs-service-claim.yaml"
    log_info "3. Monitor claims: kubectl get acgsserviceclaims -n $NAMESPACE_ACGS -w"
}

# Cleanup function
cleanup() {
    log_warning "Cleaning up ACGS GitOps deployment..."
    
    # Remove service claims
    kubectl delete acgsserviceclaims --all -n $NAMESPACE_ACGS --ignore-not-found=true
    
    # Remove ArgoCD applications
    kubectl delete -f argocd/applications/acgs-claims.yaml --ignore-not-found=true
    
    # Remove Crossplane resources
    kubectl delete -f crossplane/compositions/acgs-service.yaml --ignore-not-found=true
    kubectl delete -f crossplane/definitions/githubclaim.yaml --ignore-not-found=true
    kubectl delete -f crossplane/providers/github-provider.yaml --ignore-not-found=true
    
    # Uninstall ArgoCD
    kubectl delete -n $NAMESPACE_ARGOCD -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml --ignore-not-found=true
    kubectl delete namespace $NAMESPACE_ARGOCD --ignore-not-found=true
    
    # Uninstall Crossplane
    helm uninstall crossplane -n $NAMESPACE_CROSSPLANE --ignore-not-found=true
    kubectl delete namespace $NAMESPACE_CROSSPLANE --ignore-not-found=true
    
    # Remove ACGS namespace
    kubectl delete namespace $NAMESPACE_ACGS --ignore-not-found=true
    
    log_success "Cleanup completed"
}

# Handle script arguments
case "${1:-deploy}" in
    deploy)
        main
        ;;
    cleanup)
        cleanup
        ;;
    verify)
        verify_deployment
        ;;
    *)
        echo "Usage: $0 {deploy|cleanup|verify}"
        echo "  deploy  - Deploy ACGS GitOps workflow"
        echo "  cleanup - Remove all components"
        echo "  verify  - Verify deployment status"
        exit 1
        ;;
esac
