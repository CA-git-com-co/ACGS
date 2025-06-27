#!/bin/bash

# ACGE Phase 2 Production Kubernetes Cluster Deployment Script
# Deploys production-grade 12-node cluster with enhanced specifications

set -euo pipefail

# Configuration
CLUSTER_NAME="acge-production"
CLUSTER_VERSION="1.28.0"
REGION="us-west-2"
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
PHASE="phase-2"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}"
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

# Validate prerequisites
validate_prerequisites() {
    log "Validating prerequisites..."
    
    # Check required tools
    command -v kubectl >/dev/null 2>&1 || error "kubectl is required but not installed"
    command -v helm >/dev/null 2>&1 || error "helm is required but not installed"
    command -v aws >/dev/null 2>&1 || error "AWS CLI is required but not installed"
    
    # Check AWS credentials
    aws sts get-caller-identity >/dev/null 2>&1 || error "AWS credentials not configured"
    
    # Check cluster doesn't already exist
    if aws eks describe-cluster --name "$CLUSTER_NAME" --region "$REGION" >/dev/null 2>&1; then
        warning "Cluster $CLUSTER_NAME already exists. Continuing with configuration..."
    fi
    
    success "Prerequisites validated"
}

# Create EKS cluster
create_eks_cluster() {
    log "Creating EKS cluster: $CLUSTER_NAME"
    
    # Create cluster configuration
    cat > cluster-config.yaml << EOF
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig

metadata:
  name: $CLUSTER_NAME
  region: $REGION
  version: "$CLUSTER_VERSION"
  tags:
    Environment: production
    Phase: $PHASE
    ConstitutionalHash: $CONSTITUTIONAL_HASH
    Project: ACGE

# VPC Configuration
vpc:
  enableDnsHostnames: true
  enableDnsSupport: true
  cidr: "10.0.0.0/16"

# IAM Configuration
iam:
  withOIDC: true
  serviceAccounts:
    - metadata:
        name: acge-service-account
        namespace: acgs-pgp
      wellKnownPolicies:
        autoScaler: true
        awsLoadBalancerController: true
        ebs: true
        efs: true
        cloudWatch: true

# Node Groups
nodeGroups:
  # Control plane nodes (managed by EKS)
  
  # Worker nodes for general workloads
  - name: acge-worker-nodes
    instanceType: m5.4xlarge
    minSize: 6
    maxSize: 12
    desiredCapacity: 9
    volumeSize: 1000
    volumeType: gp3
    ssh:
      allow: false
    iam:
      withAddonPolicies:
        autoScaler: true
        cloudWatch: true
        ebs: true
    labels:
      role: worker
      constitutional-compliance: required
    tags:
      k8s.io/cluster-autoscaler/enabled: "true"
      k8s.io/cluster-autoscaler/$CLUSTER_NAME: "owned"
    
  # GPU nodes for ACGE model inference
  - name: acge-gpu-nodes
    instanceType: p3.2xlarge
    minSize: 1
    maxSize: 4
    desiredCapacity: 2
    volumeSize: 1000
    volumeType: gp3
    ssh:
      allow: false
    iam:
      withAddonPolicies:
        autoScaler: true
        cloudWatch: true
        ebs: true
    labels:
      role: gpu-worker
      constitutional-compliance: required
      nvidia.com/gpu: "true"
    taints:
      - key: nvidia.com/gpu
        value: "true"
        effect: NoSchedule
    tags:
      k8s.io/cluster-autoscaler/enabled: "true"
      k8s.io/cluster-autoscaler/$CLUSTER_NAME: "owned"

# Add-ons
addons:
  - name: vpc-cni
    version: latest
  - name: coredns
    version: latest
  - name: kube-proxy
    version: latest
  - name: aws-ebs-csi-driver
    version: latest
    wellKnownPolicies:
      ebsCSIController: true

# CloudWatch logging
cloudWatch:
  clusterLogging:
    enableTypes: ["*"]
    logRetentionInDays: 30
EOF

    # Create the cluster
    if ! aws eks describe-cluster --name "$CLUSTER_NAME" --region "$REGION" >/dev/null 2>&1; then
        log "Creating new EKS cluster..."
        eksctl create cluster -f cluster-config.yaml
    else
        log "Updating existing EKS cluster..."
        eksctl upgrade cluster -f cluster-config.yaml
    fi
    
    # Update kubeconfig
    aws eks update-kubeconfig --region "$REGION" --name "$CLUSTER_NAME"
    
    success "EKS cluster created/updated successfully"
}

# Install essential add-ons
install_addons() {
    log "Installing essential add-ons..."
    
    # Install AWS Load Balancer Controller
    log "Installing AWS Load Balancer Controller..."
    helm repo add eks https://aws.github.io/eks-charts
    helm repo update
    
    helm upgrade --install aws-load-balancer-controller eks/aws-load-balancer-controller \
        -n kube-system \
        --set clusterName="$CLUSTER_NAME" \
        --set serviceAccount.create=false \
        --set serviceAccount.name=aws-load-balancer-controller
    
    # Install Cluster Autoscaler
    log "Installing Cluster Autoscaler..."
    helm repo add autoscaler https://kubernetes.github.io/autoscaler
    helm upgrade --install cluster-autoscaler autoscaler/cluster-autoscaler \
        -n kube-system \
        --set autoDiscovery.clusterName="$CLUSTER_NAME" \
        --set awsRegion="$REGION"
    
    # Install NVIDIA Device Plugin (for GPU nodes)
    log "Installing NVIDIA Device Plugin..."
    kubectl apply -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.14.0/nvidia-device-plugin.yml
    
    success "Essential add-ons installed"
}

# Configure storage classes
configure_storage() {
    log "Configuring storage classes..."
    
    # Apply storage configuration
    kubectl apply -f - << EOF
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: acge-fast-ssd
  annotations:
    storageclass.kubernetes.io/is-default-class: "true"
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
  iops: "3000"
  throughput: "125"
  encrypted: "true"
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer
---
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: acge-constitutional-data
provisioner: ebs.csi.aws.com
parameters:
  type: io2
  iops: "10000"
  encrypted: "true"
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer
EOF
    
    success "Storage classes configured"
}

# Apply cluster configuration
apply_cluster_config() {
    log "Applying cluster configuration..."
    
    # Apply all configuration files
    kubectl apply -f cluster-config.yaml
    
    # Wait for all pods to be ready
    kubectl wait --for=condition=ready pod --all -n kube-system --timeout=300s
    
    success "Cluster configuration applied"
}

# Validate cluster health
validate_cluster() {
    log "Validating cluster health..."
    
    # Check node status
    log "Checking node status..."
    kubectl get nodes -o wide
    
    # Check system pods
    log "Checking system pods..."
    kubectl get pods -n kube-system
    
    # Check storage classes
    log "Checking storage classes..."
    kubectl get storageclass
    
    # Validate constitutional hash
    STORED_HASH=$(kubectl get configmap acge-constitutional-config -n acgs-pgp -o jsonpath='{.data.constitutional-hash}' 2>/dev/null || echo "")
    if [[ "$STORED_HASH" == "$CONSTITUTIONAL_HASH" ]]; then
        success "Constitutional hash validated: $CONSTITUTIONAL_HASH"
    else
        error "Constitutional hash mismatch. Expected: $CONSTITUTIONAL_HASH, Got: $STORED_HASH"
    fi
    
    success "Cluster validation completed"
}

# Main execution
main() {
    log "Starting ACGE Phase 2 Kubernetes cluster deployment..."
    log "Cluster: $CLUSTER_NAME"
    log "Version: $CLUSTER_VERSION"
    log "Region: $REGION"
    log "Constitutional Hash: $CONSTITUTIONAL_HASH"
    
    validate_prerequisites
    create_eks_cluster
    install_addons
    configure_storage
    apply_cluster_config
    validate_cluster
    
    success "ACGE Phase 2 Kubernetes cluster deployment completed successfully!"
    log "Next steps:"
    log "1. Configure blue-green environments"
    log "2. Deploy monitoring stack"
    log "3. Implement automated rollback system"
}

# Execute main function
main "$@"
