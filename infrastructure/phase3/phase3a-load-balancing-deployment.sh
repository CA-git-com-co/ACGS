#!/bin/bash

# ACGS Phase 3A: Load Balancing & Traffic Management
# Configure HAProxy/Nginx with SSL termination, health checks, traffic splitting for canary deployments
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
traffic() { echo -e "${PURPLE}[TRAFFIC] $1${NC}"; }

# Validate prerequisites
validate_prerequisites() {
    log "Validating prerequisites for load balancing deployment..."
    
    # Check required tools
    local required_tools=("kubectl" "helm" "openssl")
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            error "$tool is required but not installed"
        fi
    done
    
    # Check Kubernetes connectivity
    if ! kubectl cluster-info >/dev/null 2>&1; then
        error "Cannot connect to Kubernetes cluster"
    fi
    
    # Check if cert-manager is available
    if ! kubectl get crd certificates.cert-manager.io >/dev/null 2>&1; then
        warning "cert-manager CRDs not found, SSL certificates may not work"
    fi
    
    success "Prerequisites validated"
}

# Install cert-manager if not present
install_cert_manager() {
    log "Checking and installing cert-manager..."
    
    if ! kubectl get namespace cert-manager >/dev/null 2>&1; then
        log "Installing cert-manager..."
        
        # Install cert-manager using Helm
        if command -v helm >/dev/null 2>&1; then
            helm repo add jetstack https://charts.jetstack.io
            helm repo update
            
            helm upgrade --install cert-manager jetstack/cert-manager \
                --namespace cert-manager \
                --create-namespace \
                --version v1.13.0 \
                --set installCRDs=true \
                --wait
        else
            # Install using kubectl
            kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
        fi
        
        # Wait for cert-manager to be ready
        kubectl wait --for=condition=available deployment/cert-manager -n cert-manager --timeout=300s
        success "cert-manager installed"
    else
        success "cert-manager already available"
    fi
}

# Create SSL certificates
create_ssl_certificates() {
    log "Creating SSL certificates..."
    
    # Apply cert-manager cluster issuers
    kubectl apply -f infrastructure/kubernetes/production/ingress/cert-manager.yaml
    
    # Create self-signed certificate for development
    cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: acgs-production-tls
  namespace: $NAMESPACE
  labels:
    constitutional-hash: "$CONSTITUTIONAL_HASH"
spec:
  secretName: acgs-production-tls
  issuerRef:
    name: letsencrypt-staging
    kind: ClusterIssuer
  dnsNames:
  - acgs-production.local
  - api.acgs-production.local
  - auth.acgs-production.local
  - constitutional.acgs-production.local
EOF
    
    success "SSL certificates configured"
}

# Deploy Nginx ingress controller
deploy_nginx_ingress() {
    log "Checking Nginx ingress controller..."

    # Check if nginx-ingress is already installed
    if kubectl get deployment ingress-nginx-controller -n ingress-nginx >/dev/null 2>&1; then
        success "Nginx ingress controller already available"
    else
        warning "Nginx ingress controller not found, skipping installation"
    fi
}

# Deploy custom Nginx gateway
deploy_nginx_gateway() {
    log "Deploying custom Nginx gateway..."
    
    # Update namespace in nginx deployment
    sed "s/namespace: acgs-pgp/namespace: $NAMESPACE/g" \
        infrastructure/kubernetes/production/ingress/nginx-deployment.yaml | \
        kubectl apply -f -
    
    # Apply nginx ingress configuration
    sed "s/namespace: acgs-pgp/namespace: $NAMESPACE/g" \
        infrastructure/kubernetes/production/ingress/nginx-ingress.yaml | \
        kubectl apply -f -
    
    success "Custom Nginx gateway deployed"
}

# Deploy HAProxy load balancer
deploy_haproxy() {
    log "Deploying HAProxy load balancer..."
    
    # Create HAProxy configuration
    cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: haproxy-config
  namespace: $NAMESPACE
  labels:
    constitutional-hash: "$CONSTITUTIONAL_HASH"
    app.kubernetes.io/part-of: acgs
    app.kubernetes.io/component: load-balancer
data:
  haproxy.cfg: |
    global
        daemon
        maxconn 4096
        log stdout local0
        
    defaults
        mode http
        timeout connect 5000ms
        timeout client 50000ms
        timeout server 50000ms
        option httplog
        option dontlognull
        option redispatch
        retries 3
        
    # Constitutional compliance headers
    http-response set-header X-Constitutional-Hash "$CONSTITUTIONAL_HASH"
    http-response set-header X-ACGS-Security "enabled"
    
    # Frontend
    frontend acgs_frontend
        bind *:80
        bind *:443 ssl crt /etc/ssl/certs/acgs.pem
        redirect scheme https if !{ ssl_fc }
        
        # Rate limiting
        stick-table type ip size 100k expire 30s store http_req_rate(10s)
        http-request track-sc0 src
        http-request reject if { sc_http_req_rate(0) gt 20 }
        
        # Routing rules
        acl is_auth path_beg /api/v1/auth
        acl is_constitutional path_beg /api/v1/constitutional
        acl is_integrity path_beg /api/v1/integrity
        acl is_verification path_beg /api/v1/verification
        acl is_policy path_beg /api/v1/policy
        acl is_governance path_beg /api/v1/governance
        
        use_backend auth_backend if is_auth
        use_backend constitutional_backend if is_constitutional
        use_backend integrity_backend if is_integrity
        use_backend verification_backend if is_verification
        use_backend policy_backend if is_policy
        use_backend governance_backend if is_governance
        
        default_backend health_backend
    
    # Backend configurations
    backend auth_backend
        balance roundrobin
        option httpchk GET /health
        server auth1 auth-service:8000 check inter 10s fall 3 rise 2
        
    backend constitutional_backend
        balance roundrobin
        option httpchk GET /health
        server constitutional1 constitutional-ai-service:8001 check inter 10s fall 3 rise 2
        
    backend integrity_backend
        balance roundrobin
        option httpchk GET /health
        server integrity1 integrity-service:8002 check inter 10s fall 3 rise 2
        
    backend verification_backend
        balance roundrobin
        option httpchk GET /health
        server verification1 formal-verification-service:8003 check inter 10s fall 3 rise 2
        
    backend policy_backend
        balance roundrobin
        option httpchk GET /health
        server policy1 policy-governance-service:8005 check inter 10s fall 3 rise 2
        
    backend governance_backend
        balance roundrobin
        option httpchk GET /health
        server governance1 governance-synthesis-service:8004 check inter 10s fall 3 rise 2
        
    backend health_backend
        mode http
        http-request return status 200 content-type text/plain string "OK"
        
    # Stats interface
    listen stats
        bind *:8080
        stats enable
        stats uri /stats
        stats refresh 30s
        stats admin if TRUE
EOF
    
    # Deploy HAProxy
    cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: haproxy-lb
  namespace: $NAMESPACE
  labels:
    app: haproxy-lb
    constitutional-hash: "$CONSTITUTIONAL_HASH"
spec:
  replicas: 2
  selector:
    matchLabels:
      app: haproxy-lb
  template:
    metadata:
      labels:
        app: haproxy-lb
    spec:
      containers:
      - name: haproxy
        image: haproxy:2.8-alpine
        ports:
        - containerPort: 80
        - containerPort: 443
        - containerPort: 8080
        volumeMounts:
        - name: haproxy-config
          mountPath: /usr/local/etc/haproxy/haproxy.cfg
          subPath: haproxy.cfg
        - name: ssl-certs
          mountPath: /etc/ssl/certs
          readOnly: true
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /stats
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /stats
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: haproxy-config
        configMap:
          name: haproxy-config
      - name: ssl-certs
        secret:
          secretName: acgs-production-tls
---
apiVersion: v1
kind: Service
metadata:
  name: haproxy-lb
  namespace: $NAMESPACE
  labels:
    app: haproxy-lb
spec:
  type: LoadBalancer
  ports:
  - name: http
    port: 80
    targetPort: 80
  - name: https
    port: 443
    targetPort: 443
  - name: stats
    port: 8080
    targetPort: 8080
  selector:
    app: haproxy-lb
EOF
    
    success "HAProxy load balancer deployed"
}

# Configure traffic splitting for canary deployments
configure_traffic_splitting() {
    log "Configuring traffic splitting for canary deployments..."

    # Check if TrafficSplit CRD is available
    if kubectl get crd trafficsplits.split.smi-spec.io >/dev/null 2>&1; then
        # Create traffic split configuration using SMI
        cat <<EOF | kubectl apply -f -
apiVersion: split.smi-spec.io/v1alpha1
kind: TrafficSplit
metadata:
  name: constitutional-ai-canary
  namespace: $NAMESPACE
  labels:
    constitutional-hash: "$CONSTITUTIONAL_HASH"
spec:
  service: constitutional-ai-service
  backends:
  - service: constitutional-ai-service-stable
    weight: 90
  - service: constitutional-ai-service-canary
    weight: 10
---
apiVersion: split.smi-spec.io/v1alpha1
kind: TrafficSplit
metadata:
  name: auth-service-canary
  namespace: $NAMESPACE
  labels:
    constitutional-hash: "$CONSTITUTIONAL_HASH"
spec:
  service: auth-service
  backends:
  - service: auth-service-stable
    weight: 95
  - service: auth-service-canary
    weight: 5
EOF
        success "Traffic splitting configured with SMI"
    else
        # Create basic canary configuration using Kubernetes native resources
        log "SMI not available, creating basic canary configuration..."

        cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: canary-config
  namespace: $NAMESPACE
  labels:
    constitutional-hash: "$CONSTITUTIONAL_HASH"
    app.kubernetes.io/part-of: acgs
    app.kubernetes.io/component: canary
data:
  canary.yaml: |
    # Canary Deployment Configuration
    # Constitutional Hash: $CONSTITUTIONAL_HASH

    canary_deployments:
      constitutional_ai_service:
        stable_weight: 90
        canary_weight: 10
        success_rate_threshold: 99.5
        latency_threshold_ms: 100

      auth_service:
        stable_weight: 95
        canary_weight: 5
        success_rate_threshold: 99.9
        latency_threshold_ms: 50

      integrity_service:
        stable_weight: 90
        canary_weight: 10
        success_rate_threshold: 99.5
        latency_threshold_ms: 75

    global_settings:
      constitutional_hash: "$CONSTITUTIONAL_HASH"
      monitoring_enabled: true
      rollback_on_failure: true
      canary_duration_minutes: 30
EOF
        success "Basic canary configuration created"
    fi
}

# Validate load balancing deployment
validate_load_balancing() {
    log "Validating load balancing deployment..."
    
    # Check nginx ingress controller
    if kubectl get deployment ingress-nginx-controller -n ingress-nginx >/dev/null 2>&1; then
        success "Nginx ingress controller found"
    else
        warning "Nginx ingress controller not found"
    fi
    
    # Check custom nginx gateway
    if kubectl get deployment nginx-gateway -n "$NAMESPACE" >/dev/null 2>&1; then
        success "Custom Nginx gateway found"
    else
        warning "Custom Nginx gateway not found"
    fi
    
    # Check HAProxy
    if kubectl get deployment haproxy-lb -n "$NAMESPACE" >/dev/null 2>&1; then
        success "HAProxy load balancer found"
    else
        warning "HAProxy load balancer not found"
    fi
    
    # Check SSL certificates
    if kubectl get certificate acgs-production-tls -n "$NAMESPACE" >/dev/null 2>&1; then
        success "SSL certificates found"
    else
        warning "SSL certificates not found"
    fi
    
    # Check traffic splits
    if kubectl get trafficsplit -n "$NAMESPACE" >/dev/null 2>&1; then
        success "Traffic splitting configured"
    else
        warning "Traffic splitting not configured"
    fi
    
    success "Load balancing validation completed"
}

# Generate deployment report
generate_report() {
    local report_file="/tmp/load_balancing_deployment_report_$(date +%Y%m%d_%H%M%S).txt"
    
    {
        echo "ACGS Phase 3A: Load Balancing & Traffic Management Deployment Report"
        echo "Generated: $(date '+%Y-%m-%d %H:%M:%S')"
        echo "Constitutional Hash: $CONSTITUTIONAL_HASH"
        echo "Namespace: $NAMESPACE"
        echo "Phase: $PHASE"
        echo "=============================================="
        echo
        
        echo "Nginx Ingress Controller Status:"
        kubectl get deployment ingress-nginx-controller -n ingress-nginx 2>/dev/null || echo "Not found"
        echo
        
        echo "Custom Nginx Gateway Status:"
        kubectl get deployment nginx-gateway -n "$NAMESPACE" 2>/dev/null || echo "Not found"
        echo
        
        echo "HAProxy Load Balancer Status:"
        kubectl get deployment haproxy-lb -n "$NAMESPACE" 2>/dev/null || echo "Not found"
        echo
        
        echo "SSL Certificates Status:"
        kubectl get certificate -n "$NAMESPACE" 2>/dev/null || echo "Not found"
        echo
        
        echo "Traffic Splits Status:"
        kubectl get trafficsplit -n "$NAMESPACE" 2>/dev/null || echo "Not found"
        echo
        
        echo "Load Balancer Services:"
        kubectl get services -n "$NAMESPACE" | grep -E "(nginx|haproxy|lb)" || echo "Not found"
        
    } > "$report_file"
    
    log "Load balancing deployment report generated: $report_file"
    echo "$report_file"
}

# Main deployment function
main() {
    log "🚀 Starting ACGS Phase 3A: Load Balancing & Traffic Management..."
    log "Constitutional Hash: $CONSTITUTIONAL_HASH"
    log "Target Namespace: $NAMESPACE"
    
    validate_prerequisites
    install_cert_manager
    create_ssl_certificates
    deploy_nginx_ingress
    deploy_nginx_gateway
    deploy_haproxy
    configure_traffic_splitting
    validate_load_balancing
    
    local report_file=$(generate_report)
    
    success "🎉 ACGS Phase 3A: Load Balancing & Traffic Management completed!"
    log "Report: $report_file"
    
    echo ""
    echo "Next steps:"
    echo "1. Configure DNS records for load balancers"
    echo "2. Test SSL certificate validation"
    echo "3. Validate traffic splitting behavior"
    echo "4. Monitor load balancer performance"
    echo ""
    echo "Access commands:"
    echo "- HAProxy stats: kubectl port-forward svc/haproxy-lb 8080:8080 -n $NAMESPACE"
    echo "- Nginx status: kubectl get ingress -n $NAMESPACE"
    echo "- SSL certificates: kubectl get certificate -n $NAMESPACE"
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    case "${1:-deploy}" in
        "deploy")
            main
            ;;
        "validate")
            validate_load_balancing
            ;;
        "report")
            generate_report
            ;;
        *)
            echo "Usage: $0 {deploy|validate|report}"
            echo ""
            echo "Commands:"
            echo "  deploy   - Deploy load balancing infrastructure"
            echo "  validate - Validate load balancing deployment"
            echo "  report   - Generate deployment report"
            exit 1
            ;;
    esac
fi
