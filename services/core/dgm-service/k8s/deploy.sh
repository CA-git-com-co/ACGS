#!/bin/bash

# DGM Service Kubernetes Deployment Script
# This script deploys the Darwin Gödel Machine Service to Kubernetes

set -euo pipefail

# Configuration
NAMESPACE="acgs-dgm"
SERVICE_NAME="dgm-service"
IMAGE_TAG="${IMAGE_TAG:-1.0.0}"
KUBECTL_TIMEOUT="${KUBECTL_TIMEOUT:-300s}"

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

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if kubectl is installed
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed or not in PATH"
        exit 1
    fi
    
    # Check if kubectl can connect to cluster
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi
    
    # Check if Docker image exists (if building locally)
    if [[ "${BUILD_IMAGE:-false}" == "true" ]]; then
        if ! command -v docker &> /dev/null; then
            log_error "Docker is not installed or not in PATH"
            exit 1
        fi
    fi
    
    log_success "Prerequisites check passed"
}

# Build Docker image if requested
build_image() {
    if [[ "${BUILD_IMAGE:-false}" == "true" ]]; then
        log_info "Building Docker image..."
        cd "$(dirname "$0")/.."
        docker build -t "acgs/${SERVICE_NAME}:${IMAGE_TAG}" .
        log_success "Docker image built successfully"
    fi
}

# Create namespace if it doesn't exist
create_namespace() {
    log_info "Creating namespace ${NAMESPACE}..."
    kubectl apply -f namespace.yaml
    log_success "Namespace ${NAMESPACE} created/updated"
}

# Deploy configuration
deploy_config() {
    log_info "Deploying configuration..."
    kubectl apply -f configmap.yaml
    kubectl apply -f secret.yaml
    log_success "Configuration deployed"
}

# Deploy RBAC
deploy_rbac() {
    log_info "Deploying RBAC..."
    kubectl apply -f serviceaccount.yaml
    log_success "RBAC deployed"
}

# Deploy storage
deploy_storage() {
    log_info "Deploying storage..."
    kubectl apply -f pvc.yaml
    
    # Wait for PVCs to be bound
    log_info "Waiting for PVCs to be bound..."
    kubectl wait --for=condition=Bound pvc/dgm-data-pvc -n ${NAMESPACE} --timeout=${KUBECTL_TIMEOUT}
    kubectl wait --for=condition=Bound pvc/dgm-archive-pvc -n ${NAMESPACE} --timeout=${KUBECTL_TIMEOUT}
    log_success "Storage deployed and bound"
}

# Deploy application
deploy_app() {
    log_info "Deploying application..."
    
    # Update image tag in deployment
    sed -i.bak "s|image: acgs/dgm-service:.*|image: acgs/dgm-service:${IMAGE_TAG}|" deployment.yaml
    
    kubectl apply -f deployment.yaml
    kubectl apply -f service.yaml
    
    # Wait for deployment to be ready
    log_info "Waiting for deployment to be ready..."
    kubectl wait --for=condition=Available deployment/${SERVICE_NAME} -n ${NAMESPACE} --timeout=${KUBECTL_TIMEOUT}
    
    # Restore original deployment file
    mv deployment.yaml.bak deployment.yaml
    
    log_success "Application deployed"
}

# Deploy autoscaling
deploy_autoscaling() {
    log_info "Deploying autoscaling..."
    kubectl apply -f hpa.yaml
    log_success "Autoscaling deployed"
}

# Verify deployment
verify_deployment() {
    log_info "Verifying deployment..."
    
    # Check pod status
    kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/name=${SERVICE_NAME}
    
    # Check service endpoints
    kubectl get endpoints -n ${NAMESPACE} ${SERVICE_NAME}
    
    # Test health endpoint
    log_info "Testing health endpoint..."
    kubectl port-forward -n ${NAMESPACE} service/${SERVICE_NAME} 8007:8007 &
    PORT_FORWARD_PID=$!
    
    sleep 5
    
    if curl -f http://localhost:8007/health &> /dev/null; then
        log_success "Health check passed"
    else
        log_warning "Health check failed - service may still be starting"
    fi
    
    kill $PORT_FORWARD_PID 2>/dev/null || true
    
    log_success "Deployment verification completed"
}

# Show deployment status
show_status() {
    log_info "Deployment Status:"
    echo
    kubectl get all -n ${NAMESPACE} -l app.kubernetes.io/name=${SERVICE_NAME}
    echo
    log_info "To access the service:"
    echo "kubectl port-forward -n ${NAMESPACE} service/${SERVICE_NAME} 8007:8007"
    echo "Then visit: http://localhost:8007"
}

# Cleanup function
cleanup() {
    if [[ "${1:-}" == "all" ]]; then
        log_warning "Removing all DGM service resources..."
        kubectl delete namespace ${NAMESPACE} --ignore-not-found=true
        log_success "All resources removed"
    else
        log_warning "Removing DGM service deployment..."
        kubectl delete -f deployment.yaml --ignore-not-found=true
        kubectl delete -f service.yaml --ignore-not-found=true
        kubectl delete -f hpa.yaml --ignore-not-found=true
        log_success "Deployment removed"
    fi
}

# Main deployment function
main() {
    local action="${1:-deploy}"
    
    case $action in
        "deploy")
            log_info "Starting DGM Service deployment..."
            check_prerequisites
            build_image
            create_namespace
            deploy_config
            deploy_rbac
            deploy_storage
            deploy_app
            deploy_autoscaling
            verify_deployment
            show_status
            log_success "DGM Service deployment completed successfully!"
            ;;
        "cleanup")
            cleanup "${2:-}"
            ;;
        "status")
            show_status
            ;;
        *)
            echo "Usage: $0 {deploy|cleanup [all]|status}"
            echo "  deploy  - Deploy the DGM service"
            echo "  cleanup - Remove deployment (add 'all' to remove everything)"
            echo "  status  - Show deployment status"
            exit 1
            ;;
    esac
}

# Change to script directory
cd "$(dirname "$0")"

# Run main function with all arguments
main "$@"
