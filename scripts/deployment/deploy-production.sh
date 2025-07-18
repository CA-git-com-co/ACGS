# Constitutional Hash: cdd01ef066bc6cf2
# ACGS-2 Constitutional Compliance Validation
#!/bin/bash
set -euo pipefail

# ACGS-1 Lite Production Deployment Script
# This script automates the deployment of ACGS-1 Lite to production

# Configuration
ENVIRONMENT="production"
AWS_REGION="us-east-1"
CLUSTER_NAME="acgs-lite-production"
NAMESPACE_GOVERNANCE="governance"
NAMESPACE_WORKLOAD="workload"
NAMESPACE_MONITORING="monitoring"
NAMESPACE_SHARED="shared"

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

# Error handling
error_exit() {
    log_error "$1"
    exit 1
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check required tools
    command -v aws >/dev/null 2>&1 || error_exit "AWS CLI is required but not installed"
    command -v kubectl >/dev/null 2>&1 || error_exit "kubectl is required but not installed"
    command -v terraform >/dev/null 2>&1 || error_exit "Terraform is required but not installed"
    command -v helm >/dev/null 2>&1 || error_exit "Helm is required but not installed"
    
    # Check AWS credentials
    aws sts get-caller-identity >/dev/null 2>&1 || error_exit "AWS credentials not configured"
    
    # Check Terraform version
    terraform_version=$(terraform version -json | jq -r '.terraform_version')
    log_info "Terraform version: $terraform_version"
    
    log_success "Prerequisites check passed"
}

# Deploy infrastructure
deploy_infrastructure() {
    log_info "Deploying infrastructure with Terraform..."
    
    cd infrastructure/terraform
    
    # Initialize Terraform
    terraform init || error_exit "Terraform init failed"
    
    # Validate configuration
    terraform validate || error_exit "Terraform validation failed"
    
    # Plan deployment
    log_info "Creating Terraform plan..."
    terraform plan -var-file=environments/${ENVIRONMENT}.tfvars -out=tfplan || error_exit "Terraform plan failed"
    
    # Apply infrastructure
    log_info "Applying Terraform configuration..."
    terraform apply tfplan || error_exit "Terraform apply failed"
    
    # Update kubeconfig
    log_info "Updating kubeconfig for EKS cluster..."
    aws eks update-kubeconfig --region $AWS_REGION --name $CLUSTER_NAME || error_exit "Failed to update kubeconfig"
    
    cd ../..
    log_success "Infrastructure deployment completed"
}

# Install operators
install_operators() {
    log_info "Installing required operators..."
    
    # Install CloudNativePG operator
    log_info "Installing CloudNativePG operator..."
    kubectl apply -f https://raw.githubusercontent.com/cloudnative-pg/cloudnative-pg/release-1.20/releases/cnpg-1.20.0.yaml || error_exit "Failed to install CloudNativePG operator"
    
    # Install RedPanda operator
    log_info "Installing RedPanda operator..."
    kubectl apply -f https://github.com/redpanda-data/redpanda/releases/latest/download/redpanda-operator-crd.yaml || error_exit "Failed to install RedPanda CRDs"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    kubectl apply -f https://github.com/redpanda-data/redpanda/releases/latest/download/redpanda-operator.yaml || error_exit "Failed to install RedPanda operator"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    
    # Install Prometheus operator
    log_info "Installing Prometheus operator..."
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts || error_exit "Failed to add Prometheus helm repo"
    helm repo update || error_exit "Failed to update helm repos"
    helm install prometheus-operator prometheus-community/kube-prometheus-stack -n monitoring --create-namespace || log_warning "Prometheus operator may already be installed"
    
    log_success "Operators installation completed"
}

# Deploy ACGS-1 Lite services
deploy_services() {
    log_info "Deploying ACGS-1 Lite services..."
    
    # Create namespaces and RBAC
    log_info "Creating namespaces and RBAC..."
    kubectl apply -f infrastructure/kubernetes/acgs-lite/namespaces.yaml || error_exit "Failed to create namespaces"
    kubectl apply -f infrastructure/kubernetes/acgs-lite/rbac.yaml || error_exit "Failed to create RBAC"
    kubectl apply -f infrastructure/kubernetes/acgs-lite/security-policies.yaml || error_exit "Failed to apply security policies"
    kubectl apply -f infrastructure/kubernetes/acgs-lite/network-policies.yaml || error_exit "Failed to apply network policies"
    
    # Deploy database infrastructure
    log_info "Deploying PostgreSQL HA cluster..."
    kubectl apply -f infrastructure/kubernetes/acgs-lite/postgresql-ha.yaml || error_exit "Failed to deploy PostgreSQL"
    
    log_info "Waiting for PostgreSQL cluster to be ready..."
    kubectl wait --for=condition=Ready cluster/constitutional-postgres -n $NAMESPACE_SHARED --timeout=600s || error_exit "PostgreSQL cluster failed to become ready"
    
    # Initialize database
    log_info "Initializing database schema..."
    kubectl apply -f infrastructure/kubernetes/acgs-lite/database-init.yaml || error_exit "Failed to initialize database"
    kubectl wait --for=condition=Complete job/acgs-lite-db-init -n $NAMESPACE_SHARED --timeout=300s || error_exit "Database initialization failed"
    
    # Deploy event streaming
    log_info "Deploying RedPanda cluster..."
    kubectl apply -f infrastructure/kubernetes/acgs-lite/redpanda-cluster.yaml || error_exit "Failed to deploy RedPanda"
    
    log_info "Waiting for RedPanda cluster to be ready..."
    kubectl wait --for=condition=Ready redpanda/constitutional-events -n $NAMESPACE_SHARED --timeout=600s || error_exit "RedPanda cluster failed to become ready"
    
    # Apply event streaming configuration
    kubectl apply -f infrastructure/kubernetes/acgs-lite/event-streaming-config.yaml || error_exit "Failed to apply event streaming config"
    
    # Deploy core services
    log_info "Deploying Policy Engine..."
    kubectl apply -f infrastructure/kubernetes/acgs-lite/policy-engine.yaml || error_exit "Failed to deploy Policy Engine"
    
    log_info "Waiting for Policy Engine to be ready..."
    kubectl wait --for=condition=Available deployment/policy-engine -n $NAMESPACE_GOVERNANCE --timeout=300s || error_exit "Policy Engine failed to become ready"
    kubectl wait --for=condition=Available deployment/opa -n $NAMESPACE_GOVERNANCE --timeout=300s || error_exit "OPA failed to become ready"
    
    log_info "Deploying Sandbox Controller..."
    kubectl apply -f infrastructure/kubernetes/acgs-lite/sandbox-controller.yaml || error_exit "Failed to deploy Sandbox Controller"
    
    log_info "Waiting for Sandbox Controller to be ready..."
    kubectl wait --for=condition=Available deployment/sandbox-controller -n $NAMESPACE_WORKLOAD --timeout=300s || error_exit "Sandbox Controller failed to become ready"
    
    log_success "Services deployment completed"
}

# Deploy monitoring stack
deploy_monitoring() {
    log_info "Deploying monitoring stack..."
    
    # Deploy Prometheus
    log_info "Deploying Prometheus..."
    kubectl apply -f infrastructure/kubernetes/acgs-lite/monitoring.yaml || error_exit "Failed to deploy Prometheus"
    
    # Deploy Grafana
    log_info "Deploying Grafana..."
    kubectl apply -f infrastructure/kubernetes/acgs-lite/grafana.yaml || error_exit "Failed to deploy Grafana"
    
    # Deploy AlertManager
    log_info "Deploying AlertManager..."
    kubectl apply -f infrastructure/kubernetes/acgs-lite/alertmanager.yaml || error_exit "Failed to deploy AlertManager"
    
    log_info "Waiting for monitoring stack to be ready..."
    kubectl wait --for=condition=Available deployment/prometheus -n $NAMESPACE_MONITORING --timeout=300s || error_exit "Prometheus failed to become ready"
    kubectl wait --for=condition=Available deployment/grafana -n $NAMESPACE_MONITORING --timeout=300s || error_exit "Grafana failed to become ready"
    kubectl wait --for=condition=Available deployment/alertmanager -n $NAMESPACE_MONITORING --timeout=300s || error_exit "AlertManager failed to become ready"
    
    log_success "Monitoring stack deployment completed"
}

# Post-deployment verification
verify_deployment() {
    log_info "Running post-deployment verification..."
    
    # Check all deployments
    log_info "Checking deployment status..."
    kubectl get deployments --all-namespaces || error_exit "Failed to get deployments"
    
    # Check services
    log_info "Checking service endpoints..."
    kubectl get services --all-namespaces || error_exit "Failed to get services"
    
    # Test Policy Engine health
    log_info "Testing Policy Engine health..."
    kubectl port-forward svc/policy-engine 8001:8001 -n $NAMESPACE_GOVERNANCE &
    PORT_FORWARD_PID=$!
    sleep 5
    
    if curl -f http://localhost:8001/health >/dev/null 2>&1; then
        log_success "Policy Engine health check passed"
    else
        log_error "Policy Engine health check failed"
    fi
    
    kill $PORT_FORWARD_PID 2>/dev/null || true
    
    # Test database connectivity
    log_info "Testing database connectivity..."
    kubectl exec -it constitutional-postgres-1 -n $NAMESPACE_SHARED -- psql -U postgres -d acgs_lite -c "SELECT COUNT(*) FROM constitutional_policies;" || log_warning "Database connectivity test failed"
    
    # Check RedPanda topics
    log_info "Checking RedPanda topics..."
    kubectl exec -it constitutional-events-0 -n $NAMESPACE_SHARED -- rpk topic list || log_warning "RedPanda topic check failed"
    
    log_success "Post-deployment verification completed"
}

# Generate deployment report
generate_report() {
    log_info "Generating deployment report..."
    
    REPORT_FILE="deployment-report-$(date +%Y%m%d-%H%M%S).txt"
    
    {
        echo "ACGS-1 Lite Production Deployment Report"
        echo "========================================"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
        echo "Deployment Date: $(date)"
        echo "Environment: $ENVIRONMENT"
        echo "AWS Region: $AWS_REGION"
        echo "Cluster Name: $CLUSTER_NAME"
        echo ""
        echo "Deployment Status:"
        kubectl get deployments --all-namespaces
        echo ""
        echo "Service Endpoints:"
        kubectl get services --all-namespaces
        echo ""
        echo "Pod Status:"
        kubectl get pods --all-namespaces
        echo ""
        echo "Persistent Volumes:"
        kubectl get pv,pvc --all-namespaces
    } > $REPORT_FILE
    
    log_success "Deployment report generated: $REPORT_FILE"
}

# Main deployment function
main() {
    log_info "Starting ACGS-1 Lite production deployment..."
    log_info "Environment: $ENVIRONMENT"
    log_info "AWS Region: $AWS_REGION"
    log_info "Cluster Name: $CLUSTER_NAME"
    
    # Run deployment steps
    check_prerequisites
    deploy_infrastructure
    install_operators
    deploy_services
    deploy_monitoring
    verify_deployment
    generate_report
    
    log_success "ACGS-1 Lite production deployment completed successfully!"
    log_info "Next steps:"
    log_info "1. Configure monitoring dashboards in Grafana"
    log_info "2. Set up alerting notification channels"
    log_info "3. Run integration tests"
    log_info "4. Update DNS records for external access"
    log_info "5. Schedule regular backup verification"
}

# Script execution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
