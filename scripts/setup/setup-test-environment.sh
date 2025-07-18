# Constitutional Hash: cdd01ef066bc6cf2
#!/bin/bash

# ACGS GitOps Test Environment Setup
# Install necessary tools and create a local Kubernetes cluster for testing

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

# Install kubectl
install_kubectl() {
    log_info "Installing kubectl..."
    
    if command -v kubectl &> /dev/null; then
        log_success "kubectl already installed"
        return 0
    fi
    
    # Download kubectl
    curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
    
    # Install kubectl
    sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
    rm kubectl
    
    # Verify installation
    if kubectl version --client &> /dev/null; then
        log_success "kubectl installed successfully"
    else
        log_error "kubectl installation failed"
        return 1
    fi
}

# Install kind
install_kind() {
    log_info "Installing kind..."
    
    if command -v kind &> /dev/null; then
        log_success "kind already installed"
        return 0
    fi
    
    # Download and install kind
    curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
    chmod +x ./kind
    sudo mv ./kind /usr/local/bin/kind
    
    # Verify installation
    if kind version &> /dev/null; then
        log_success "kind installed successfully"
    else
        log_error "kind installation failed"
        return 1
    fi
}

# Install helm
install_helm() {
    log_info "Installing helm..."
    
    if command -v helm &> /dev/null; then
        log_success "helm already installed"
        return 0
    fi
    
    # Install helm
    curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
    
    # Verify installation
    if helm version &> /dev/null; then
        log_success "helm installed successfully"
    else
        log_error "helm installation failed"
        return 1
    fi
}

# Create kind cluster
create_cluster() {
    log_info "Creating kind cluster..."
    
    # Check if cluster already exists
    if kind get clusters | grep -q "acgs-test"; then
        log_warning "Cluster 'acgs-test' already exists"
        return 0
    fi
    
    # Create cluster configuration
    cat <<EOF > kind-config.yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: acgs-test
nodes:
- role: control-plane
  kubeadmConfigPatches:
  - |
    kind: InitConfiguration
    nodeRegistration:
      kubeletExtraArgs:
        node-labels: "ingress-ready=true"
  extraPortMappings:
  - containerPort: 80
    hostPort: 80
    protocol: TCP
  - containerPort: 443
    hostPort: 443
    protocol: TCP
- role: worker
- role: worker
EOF
    
    # Create cluster
    kind create cluster --config kind-config.yaml --wait 300s
    
    # Verify cluster
    if kubectl cluster-info &> /dev/null; then
        log_success "Kind cluster created successfully"
        kubectl get nodes
    else
        log_error "Failed to create kind cluster"
        return 1
    fi
    
    # Clean up config file
    rm kind-config.yaml
}

# Verify environment
verify_environment() {
    log_info "Verifying test environment..."
    
    # Check tools
    local tools=("kubectl" "kind" "helm" "docker")
    for tool in "${tools[@]}"; do
        if command -v $tool &> /dev/null; then
            log_success "$tool is available"
        else
            log_error "$tool is not available"
            return 1
        fi
    done
    
    # Check cluster
    if kubectl cluster-info &> /dev/null; then
        log_success "Kubernetes cluster is accessible"
        kubectl get nodes -o wide
    else
        log_error "Cannot access Kubernetes cluster"
        return 1
    fi
    
    # Check Docker
    if docker ps &> /dev/null; then
        log_success "Docker is running"
    else
        log_error "Docker is not running"
        return 1
    fi
}

# Main setup function
main() {
    log_info "Setting up ACGS GitOps test environment..."
    
    install_kubectl
    install_kind
    install_helm
    create_cluster
    verify_environment
    
    log_success "Test environment setup completed!"
    log_info "You can now run the GitOps validation tests"
}

# Cleanup function
cleanup() {
    log_warning "Cleaning up test environment..."
    
    # Delete kind cluster
    if kind get clusters | grep -q "acgs-test"; then
        kind delete cluster --name acgs-test
        log_success "Kind cluster deleted"
    fi
}

# Handle script arguments
case "${1:-setup}" in
    setup)
        main
        ;;
    cleanup)
        cleanup
        ;;
    verify)
        verify_environment
        ;;
    *)
        echo "Usage: $0 {setup|cleanup|verify}"
        echo "  setup   - Set up test environment"
        echo "  cleanup - Clean up test environment"
        echo "  verify  - Verify environment is ready"
        exit 1
        ;;
esac
