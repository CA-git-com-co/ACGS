#!/bin/bash

# ACGS-PGP Linkerd Service Mesh Deployment
# Implements mTLS, traffic policies, and advanced observability

set -e

PRODUCTION_NAMESPACE="acgs-production"
LINKERD_NAMESPACE="linkerd"
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $(date '+%H:%M:%S') $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $(date '+%H:%M:%S') $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $(date '+%H:%M:%S') $1"; }
log_mesh() { echo -e "${BLUE}[MESH]${NC} $(date '+%H:%M:%S') $1"; }
log_security() { echo -e "${PURPLE}[SECURITY]${NC} $(date '+%H:%M:%S') $1"; }

# Check Linkerd CLI availability
check_linkerd_cli() {
    log_mesh "Checking Linkerd CLI availability..."
    
    if ! command -v linkerd &> /dev/null; then
        log_warn "Linkerd CLI not found. Installing..."
        
        # Download and install Linkerd CLI
        curl -sL https://run.linkerd.io/install | sh
        export PATH=$PATH:$HOME/.linkerd2/bin
        
        if command -v linkerd &> /dev/null; then
            log_info "✓ Linkerd CLI installed successfully"
        else
            log_error "Failed to install Linkerd CLI"
            return 1
        fi
    else
        log_info "✓ Linkerd CLI is available"
    fi
    
    # Verify CLI version
    local linkerd_version=$(linkerd version --client --short)
    log_info "Linkerd CLI version: $linkerd_version"
    
    return 0
}

# Pre-installation checks
pre_installation_checks() {
    log_mesh "Running Linkerd pre-installation checks..."
    
    # Check cluster connectivity
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster"
        return 1
    fi
    
    # Run Linkerd pre-check
    if linkerd check --pre; then
        log_info "✓ Linkerd pre-installation checks passed"
    else
        log_error "Linkerd pre-installation checks failed"
        return 1
    fi
    
    return 0
}

# Install Linkerd control plane
install_linkerd_control_plane() {
    log_mesh "Installing Linkerd control plane..."
    
    # Generate and apply CRDs
    log_mesh "Applying Linkerd CRDs..."
    linkerd install --crds | kubectl apply -f -
    
    # Install control plane
    log_mesh "Installing Linkerd control plane..."
    linkerd install | kubectl apply -f -
    
    # Wait for control plane to be ready
    log_mesh "Waiting for Linkerd control plane to be ready..."
    linkerd check --wait
    
    log_info "✓ Linkerd control plane installed successfully"
}

# Install Linkerd Viz extension
install_linkerd_viz() {
    log_mesh "Installing Linkerd Viz extension..."
    
    # Install Viz extension
    linkerd viz install | kubectl apply -f -
    
    # Wait for Viz to be ready
    log_mesh "Waiting for Linkerd Viz to be ready..."
    linkerd viz check --wait
    
    log_info "✓ Linkerd Viz extension installed successfully"
}

# Configure ACGS-PGP specific policies
configure_acgs_policies() {
    log_mesh "Configuring ACGS-PGP specific service mesh policies..."
    
    # Create constitutional AI traffic policy
    cat <<EOF | kubectl apply -f -
apiVersion: policy.linkerd.io/v1beta1
kind: Server
metadata:
  name: constitutional-ai-server
  namespace: $PRODUCTION_NAMESPACE
spec:
  podSelector:
    matchLabels:
      app: constitutional-ai-service
  port: 8001
  proxyProtocol: "HTTP/2"
---
apiVersion: policy.linkerd.io/v1beta1
kind: ServerAuthorization
metadata:
  name: constitutional-ai-authz
  namespace: $PRODUCTION_NAMESPACE
spec:
  server:
    name: constitutional-ai-server
  requiredRoutes:
  - pathRegex: "/validate"
    methods: ["POST"]
  - pathRegex: "/health"
    methods: ["GET"]
  client:
    meshTLS:
      identities:
      - "auth-service.$PRODUCTION_NAMESPACE.serviceaccount.identity.linkerd.cluster.local"
      - "integrity-service.$PRODUCTION_NAMESPACE.serviceaccount.identity.linkerd.cluster.local"
      - "formal-verification-service.$PRODUCTION_NAMESPACE.serviceaccount.identity.linkerd.cluster.local"
      - "governance-synthesis-service.$PRODUCTION_NAMESPACE.serviceaccount.identity.linkerd.cluster.local"
      - "policy-governance-service.$PRODUCTION_NAMESPACE.serviceaccount.identity.linkerd.cluster.local"
      - "evolutionary-computation-service.$PRODUCTION_NAMESPACE.serviceaccount.identity.linkerd.cluster.local"
      - "model-orchestrator-service.$PRODUCTION_NAMESPACE.serviceaccount.identity.linkerd.cluster.local"
EOF
    
    # Create traffic split for constitutional compliance monitoring
    cat <<EOF | kubectl apply -f -
apiVersion: split.smi-spec.io/v1alpha1
kind: TrafficSplit
metadata:
  name: constitutional-ai-split
  namespace: $PRODUCTION_NAMESPACE
spec:
  service: constitutional-ai-service
  backends:
  - service: constitutional-ai-service
    weight: 100
---
apiVersion: policy.linkerd.io/v1beta1
kind: HTTPRoute
metadata:
  name: constitutional-compliance-route
  namespace: $PRODUCTION_NAMESPACE
spec:
  parentRefs:
  - name: constitutional-ai-service
    kind: Service
  rules:
  - matches:
    - path:
        type: PathPrefix
        value: "/validate"
    filters:
    - type: RequestHeaderModifier
      requestHeaderModifier:
        add:
        - name: "X-Constitutional-Hash"
          value: "$CONSTITUTIONAL_HASH"
        - name: "X-Compliance-Required"
          value: "true"
EOF
    
    log_info "✓ ACGS-PGP service mesh policies configured"
}

# Inject Linkerd proxy into ACGS services
inject_linkerd_proxy() {
    log_mesh "Injecting Linkerd proxy into ACGS-PGP services..."
    
    # Annotate namespace for automatic injection
    kubectl annotate namespace $PRODUCTION_NAMESPACE linkerd.io/inject=enabled --overwrite
    
    # Get all deployments in production namespace
    local deployments=$(kubectl get deployments -n $PRODUCTION_NAMESPACE -o name)
    
    for deployment in $deployments; do
        local deployment_name=$(echo $deployment | cut -d/ -f2)
        
        log_mesh "Injecting Linkerd proxy into $deployment_name..."
        
        # Get current deployment and inject Linkerd
        kubectl get $deployment -n $PRODUCTION_NAMESPACE -o yaml | \
            linkerd inject - | \
            kubectl apply -f -
        
        # Wait for rollout to complete
        kubectl rollout status $deployment -n $PRODUCTION_NAMESPACE --timeout=300s
        
        log_info "✓ Linkerd proxy injected into $deployment_name"
    done
    
    log_info "✓ All ACGS-PGP services have Linkerd proxy injected"
}

# Configure mTLS policies
configure_mtls() {
    log_security "Configuring mTLS policies for ACGS-PGP services..."
    
    # Create network policy for constitutional AI service
    cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: constitutional-ai-network-policy
  namespace: $PRODUCTION_NAMESPACE
spec:
  podSelector:
    matchLabels:
      app: constitutional-ai-service
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: $PRODUCTION_NAMESPACE
    - namespaceSelector:
        matchLabels:
          name: linkerd
    ports:
    - protocol: TCP
      port: 8001
    - protocol: TCP
      port: 4143  # Linkerd proxy port
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: $PRODUCTION_NAMESPACE
    - namespaceSelector:
        matchLabels:
          name: linkerd
    - namespaceSelector:
        matchLabels:
          name: kube-system
  - to: []
    ports:
    - protocol: TCP
      port: 53  # DNS
    - protocol: UDP
      port: 53  # DNS
---
apiVersion: policy.linkerd.io/v1alpha1
kind: MeshTLSAuthentication
metadata:
  name: constitutional-ai-mtls
  namespace: $PRODUCTION_NAMESPACE
spec:
  targetRef:
    group: ""
    kind: Service
    name: constitutional-ai-service
  identities:
  - "auth-service.$PRODUCTION_NAMESPACE.serviceaccount.identity.linkerd.cluster.local"
  - "integrity-service.$PRODUCTION_NAMESPACE.serviceaccount.identity.linkerd.cluster.local"
  - "formal-verification-service.$PRODUCTION_NAMESPACE.serviceaccount.identity.linkerd.cluster.local"
  - "governance-synthesis-service.$PRODUCTION_NAMESPACE.serviceaccount.identity.linkerd.cluster.local"
  - "policy-governance-service.$PRODUCTION_NAMESPACE.serviceaccount.identity.linkerd.cluster.local"
  - "evolutionary-computation-service.$PRODUCTION_NAMESPACE.serviceaccount.identity.linkerd.cluster.local"
  - "model-orchestrator-service.$PRODUCTION_NAMESPACE.serviceaccount.identity.linkerd.cluster.local"
EOF
    
    log_security "✓ mTLS policies configured for constitutional AI service"
}

# Configure advanced observability
configure_observability() {
    log_mesh "Configuring advanced observability..."
    
    # Create ServiceProfile for constitutional AI service
    cat <<EOF | kubectl apply -f -
apiVersion: linkerd.io/v1alpha2
kind: ServiceProfile
metadata:
  name: constitutional-ai-service
  namespace: $PRODUCTION_NAMESPACE
spec:
  routes:
  - name: validate
    condition:
      method: POST
      pathRegex: "/validate"
    responseClasses:
    - condition:
        status:
          min: 200
          max: 299
      isFailure: false
    - condition:
        status:
          min: 500
          max: 599
      isFailure: true
    timeout: "2s"
  - name: health
    condition:
      method: GET
      pathRegex: "/health"
    responseClasses:
    - condition:
        status:
          min: 200
          max: 299
      isFailure: false
    timeout: "1s"
  retryBudget:
    retryRatio: 0.2
    minRetriesPerSecond: 10
    ttl: "10s"
---
apiVersion: linkerd.io/v1alpha2
kind: TrafficSplit
metadata:
  name: constitutional-ai-canary
  namespace: $PRODUCTION_NAMESPACE
spec:
  service: constitutional-ai-service
  backends:
  - service: constitutional-ai-service
    weight: 100
EOF
    
    # Create custom metrics for constitutional compliance
    cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: linkerd-prometheus-config
  namespace: linkerd-viz
data:
  prometheus.yml: |
    global:
      scrape_interval: 10s
      evaluation_interval: 10s
    rule_files:
    - "/etc/prometheus/rules/*.yml"
    scrape_configs:
    - job_name: 'linkerd-controller'
      kubernetes_sd_configs:
      - role: pod
        namespaces:
          names: ['linkerd']
      relabel_configs:
      - source_labels: [__meta_kubernetes_pod_container_name]
        action: keep
        regex: ^(destination|identity|proxy-injector)$
    - job_name: 'linkerd-proxy'
      kubernetes_sd_configs:
      - role: pod
      relabel_configs:
      - source_labels: [__meta_kubernetes_pod_container_name]
        action: keep
        regex: ^linkerd-proxy$
      - source_labels: [__meta_kubernetes_namespace]
        action: keep
        regex: ^$PRODUCTION_NAMESPACE$
    - job_name: 'constitutional-compliance'
      kubernetes_sd_configs:
      - role: pod
        namespaces:
          names: ['$PRODUCTION_NAMESPACE']
      relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        action: keep
        regex: constitutional-ai-service
      metrics_path: /metrics
      scrape_interval: 5s
EOF
    
    log_info "✓ Advanced observability configured"
}

# Validate service mesh deployment
validate_service_mesh() {
    log_mesh "Validating service mesh deployment..."
    
    # Run Linkerd check
    if linkerd check; then
        log_info "✓ Linkerd control plane validation passed"
    else
        log_error "Linkerd control plane validation failed"
        return 1
    fi
    
    # Check proxy injection
    local injected_pods=$(kubectl get pods -n $PRODUCTION_NAMESPACE -o jsonpath='{.items[*].spec.containers[*].name}' | grep -c linkerd-proxy || echo "0")
    local total_pods=$(kubectl get pods -n $PRODUCTION_NAMESPACE --no-headers | wc -l)
    
    if [[ $injected_pods -eq $total_pods ]]; then
        log_info "✓ All pods have Linkerd proxy injected ($injected_pods/$total_pods)"
    else
        log_warn "⚠ Not all pods have Linkerd proxy injected ($injected_pods/$total_pods)"
    fi
    
    # Test mTLS connectivity
    log_mesh "Testing mTLS connectivity..."
    local mtls_test=$(kubectl exec -n $PRODUCTION_NAMESPACE deployment/auth-service -c linkerd-proxy -- \
        curl -s http://constitutional-ai-service:8001/health 2>/dev/null || echo "FAIL")
    
    if [[ "$mtls_test" != "FAIL" ]]; then
        log_security "✓ mTLS connectivity test passed"
    else
        log_warn "⚠ mTLS connectivity test failed"
    fi
    
    # Check traffic metrics
    log_mesh "Checking traffic metrics..."
    local metrics_available=$(linkerd viz stat deployment -n $PRODUCTION_NAMESPACE | grep -c "constitutional-ai-service" || echo "0")
    
    if [[ $metrics_available -gt 0 ]]; then
        log_info "✓ Traffic metrics are available"
    else
        log_warn "⚠ Traffic metrics not yet available"
    fi
    
    log_info "✓ Service mesh validation completed"
}

# Generate service mesh report
generate_mesh_report() {
    local report_file="/tmp/linkerd_deployment_report_$(date +%Y%m%d_%H%M%S).txt"
    
    {
        echo "ACGS-PGP Linkerd Service Mesh Deployment Report"
        echo "Generated: $(date '+%Y-%m-%d %H:%M:%S')"
        echo "Production Namespace: $PRODUCTION_NAMESPACE"
        echo "Constitutional Hash: $CONSTITUTIONAL_HASH"
        echo "=============================================="  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
        echo
        
        echo "Linkerd Control Plane Status:"
        linkerd check --output short
        echo
        
        echo "Service Mesh Statistics:"
        linkerd viz stat deployment -n $PRODUCTION_NAMESPACE
        echo
        
        echo "mTLS Status:"
        linkerd viz edges -n $PRODUCTION_NAMESPACE
        echo
        
        echo "Traffic Policies:"
        kubectl get servers,serverauthorizations,httproutes -n $PRODUCTION_NAMESPACE
        echo
        
        echo "Network Policies:"
        kubectl get networkpolicies -n $PRODUCTION_NAMESPACE
        
    } > "$report_file"
    
    log_mesh "Service mesh deployment report generated: $report_file"
    echo "$report_file"
}

# Main deployment function
main() {
    local action=${1:-"deploy"}
    
    case $action in
        "deploy")
            log_mesh "Starting Linkerd service mesh deployment for ACGS-PGP..."
            
            check_linkerd_cli
            pre_installation_checks
            install_linkerd_control_plane
            install_linkerd_viz
            configure_acgs_policies
            inject_linkerd_proxy
            configure_mtls
            configure_observability
            validate_service_mesh
            
            local report_file=$(generate_mesh_report)
            
            log_mesh "🎉 Linkerd service mesh deployment completed!"
            log_mesh "Report: $report_file"
            log_mesh "Access Linkerd dashboard: linkerd viz dashboard"
            ;;
        "validate")
            validate_service_mesh
            ;;
        "dashboard")
            log_mesh "Opening Linkerd dashboard..."
            linkerd viz dashboard
            ;;
        "stats")
            linkerd viz stat deployment -n $PRODUCTION_NAMESPACE
            ;;
        "edges")
            linkerd viz edges -n $PRODUCTION_NAMESPACE
            ;;
        *)
            echo "Usage: $0 {deploy|validate|dashboard|stats|edges}"
            echo "  deploy    - Deploy Linkerd service mesh"
            echo "  validate  - Validate service mesh deployment"
            echo "  dashboard - Open Linkerd dashboard"
            echo "  stats     - Show traffic statistics"
            echo "  edges     - Show mTLS edges"
            exit 1
            ;;
    esac
}

main "$@"
