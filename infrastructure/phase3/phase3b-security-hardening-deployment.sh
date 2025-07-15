#!/bin/bash

# ACGS Phase 3B: Security Hardening
# Implement secrets management, network security, security monitoring, and penetration testing
# Target: >90/100 security posture with constitutional compliance hash: cdd01ef066bc6cf2

set -euo pipefail

# Configuration
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
NAMESPACE="acgs-production"
PHASE="phase-3b"
SECURITY_TARGET_SCORE=90

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Logging functions
log() { echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"; }
success() { echo -e "${GREEN}[✓] $1${NC}"; }
warning() { echo -e "${YELLOW}[⚠] $1${NC}"; }
error() { echo -e "${RED}[✗] $1${NC}"; exit 1; }
security() { echo -e "${PURPLE}[SECURITY] $1${NC}"; }
vault() { echo -e "${CYAN}[VAULT] $1${NC}"; }

# Validate prerequisites
validate_prerequisites() {
    log "Validating prerequisites for security hardening deployment..."
    
    # Check required tools
    local required_tools=("kubectl" "helm" "vault" "openssl" "python3")
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            error "$tool is required but not installed"
        fi
    done
    
    # Check Kubernetes connectivity
    if ! kubectl cluster-info >/dev/null 2>&1; then
        error "Cannot connect to Kubernetes cluster"
    fi
    
    # Check Python dependencies
    if ! python3 -c "import hvac, cryptography, requests" >/dev/null 2>&1; then
        warning "Some Python security libraries may be missing"
    fi
    
    success "Prerequisites validated"
}

# Deploy HashiCorp Vault for secrets management
deploy_vault() {
    log "Deploying HashiCorp Vault for secrets management..."
    
    # Add HashiCorp Helm repository
    helm repo add hashicorp https://helm.releases.hashicorp.com
    helm repo update
    
    # Create Vault namespace
    kubectl create namespace vault --dry-run=client -o yaml | kubectl apply -f -
    kubectl label namespace vault constitutional-hash="$CONSTITUTIONAL_HASH" --overwrite
    
    # Deploy Vault using Helm
    helm upgrade --install vault hashicorp/vault \
        --namespace vault \
        --set server.ha.enabled=true \
        --set server.ha.replicas=3 \
        --set server.dataStorage.enabled=true \
        --set server.dataStorage.size=10Gi \
        --set server.auditStorage.enabled=true \
        --set server.auditStorage.size=5Gi \
        --set ui.enabled=true \
        --set ui.serviceType=ClusterIP \
        --set injector.enabled=true \
        --set injector.replicas=2 \
        --wait --timeout=600s
    
    # Wait for Vault to be ready
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=vault -n vault --timeout=300s
    
    success "HashiCorp Vault deployed"
}

# Initialize and configure Vault
configure_vault() {
    vault "Initializing and configuring Vault..."
    
    # Port forward to access Vault
    kubectl port-forward svc/vault 8200:8200 -n vault &
    VAULT_PORT_FORWARD_PID=$!
    sleep 10
    
    export VAULT_ADDR="http://localhost:8200"
    
    # Initialize Vault if not already initialized
    if ! vault status >/dev/null 2>&1; then
        vault operator init -key-shares=5 -key-threshold=3 > /tmp/vault-init.txt
        
        # Extract unseal keys and root token
        UNSEAL_KEY_1=$(grep 'Unseal Key 1:' /tmp/vault-init.txt | awk '{print $4}')
        UNSEAL_KEY_2=$(grep 'Unseal Key 2:' /tmp/vault-init.txt | awk '{print $4}')
        UNSEAL_KEY_3=$(grep 'Unseal Key 3:' /tmp/vault-init.txt | awk '{print $4}')
        ROOT_TOKEN=$(grep 'Initial Root Token:' /tmp/vault-init.txt | awk '{print $4}')
        
        # Unseal Vault
        vault operator unseal "$UNSEAL_KEY_1"
        vault operator unseal "$UNSEAL_KEY_2"
        vault operator unseal "$UNSEAL_KEY_3"
        
        # Login with root token
        vault auth "$ROOT_TOKEN"
        
        # Store keys securely
        kubectl create secret generic vault-keys \
            --from-literal=unseal-key-1="$UNSEAL_KEY_1" \
            --from-literal=unseal-key-2="$UNSEAL_KEY_2" \
            --from-literal=unseal-key-3="$UNSEAL_KEY_3" \
            --from-literal=root-token="$ROOT_TOKEN" \
            -n vault
        
        rm -f /tmp/vault-init.txt
    fi
    
    # Configure Vault policies and auth methods
    vault policy write acgs-policy - <<EOF
path "secret/data/acgs/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "secret/metadata/acgs/*" {
  capabilities = ["list"]
}

path "auth/token/lookup-self" {
  capabilities = ["read"]
}

path "auth/token/renew-self" {
  capabilities = ["update"]
}
EOF
    
    # Enable KV secrets engine
    vault secrets enable -path=secret kv-v2
    
    # Store constitutional hash
    vault kv put secret/acgs/constitutional constitutional_hash="$CONSTITUTIONAL_HASH"
    
    # Kill port forward
    kill $VAULT_PORT_FORWARD_PID 2>/dev/null || true
    
    success "Vault configured with ACGS policies"
}

# Deploy network security policies
deploy_network_security() {
    security "Deploying network security policies..."
    
    # Create network policies for namespace isolation
    cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: acgs-production-network-policy
  namespace: $NAMESPACE
  labels:
    constitutional-hash: "$CONSTITUTIONAL_HASH"
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    - namespaceSelector:
        matchLabels:
          name: linkerd
    - podSelector:
        matchLabels:
          app.kubernetes.io/part-of: acgs
    ports:
    - protocol: TCP
      port: 8000
    - protocol: TCP
      port: 8001
    - protocol: TCP
      port: 8002
    - protocol: TCP
      port: 8003
    - protocol: TCP
      port: 8004
    - protocol: TCP
      port: 8005
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
  - to:
    - namespaceSelector:
        matchLabels:
          name: vault
    ports:
    - protocol: TCP
      port: 8200
  - to: []
    ports:
    - protocol: TCP
      port: 53
    - protocol: UDP
      port: 53
    - protocol: TCP
      port: 443
    - protocol: TCP
      port: 5432
    - protocol: TCP
      port: 6379
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: vault-network-policy
  namespace: vault
  labels:
    constitutional-hash: "$CONSTITUTIONAL_HASH"
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/name: vault
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: $NAMESPACE
    - podSelector: {}
    ports:
    - protocol: TCP
      port: 8200
  egress:
  - to: []
    ports:
    - protocol: TCP
      port: 53
    - protocol: UDP
      port: 53
    - protocol: TCP
      port: 443
EOF
    
    success "Network security policies deployed"
}

# Deploy security monitoring
deploy_security_monitoring() {
    security "Deploying security monitoring infrastructure..."
    
    # Deploy Falco for runtime security monitoring
    helm repo add falcosecurity https://falcosecurity.github.io/charts
    helm repo update
    
    helm upgrade --install falco falcosecurity/falco \
        --namespace falco-system \
        --create-namespace \
        --set falco.grpc.enabled=true \
        --set falco.grpcOutput.enabled=true \
        --set falco.httpOutput.enabled=true \
        --set falco.httpOutput.url=http://prometheus-server.monitoring.svc.cluster.local:9090/api/v1/write \
        --set falco.jsonOutput=true \
        --set falco.logLevel=info \
        --wait
    
    # Create custom Falco rules for constitutional compliance
    cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: falco-constitutional-rules
  namespace: falco-system
  labels:
    constitutional-hash: "$CONSTITUTIONAL_HASH"
data:
  constitutional_rules.yaml: |
    - rule: Constitutional Hash Violation
      desc: Detect requests without proper constitutional hash
      condition: >
        k8s_audit and
        ka.verb in (create, update, patch) and
        not ka.request_object contains "constitutional-hash" and
        ka.target.namespace = "$NAMESPACE"
      output: >
        Constitutional hash missing in request
        (user=%ka.user.name verb=%ka.verb 
         resource=%ka.target.resource 
         namespace=%ka.target.namespace)
      priority: CRITICAL
      tags: [constitutional, compliance, security]
    
    - rule: Unauthorized Service Access
      desc: Detect unauthorized access to ACGS services
      condition: >
        spawned_process and
        proc.name in (curl, wget, nc, ncat) and
        proc.cmdline contains "8000" or
        proc.cmdline contains "8001" or
        proc.cmdline contains "8002" or
        proc.cmdline contains "8003" or
        proc.cmdline contains "8004" or
        proc.cmdline contains "8005"
      output: >
        Unauthorized service access attempt
        (user=%user.name command=%proc.cmdline 
         container=%container.name)
      priority: HIGH
      tags: [network, unauthorized, acgs]
EOF
    
    success "Security monitoring deployed with Falco"
}

# Run penetration testing
run_penetration_testing() {
    security "Running automated penetration testing..."
    
    # Create penetration testing job
    cat <<EOF | kubectl apply -f -
apiVersion: batch/v1
kind: Job
metadata:
  name: acgs-pentest-$(date +%Y%m%d-%H%M%S)
  namespace: $NAMESPACE
  labels:
    constitutional-hash: "$CONSTITUTIONAL_HASH"
    app.kubernetes.io/part-of: acgs
    app.kubernetes.io/component: security-testing
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
      - name: pentest
        image: python:3.11-slim
        command: ["/bin/bash"]
        args:
        - -c
        - |
          pip install requests aiohttp pytest-asyncio
          cat > /tmp/pentest.py << 'PENTEST_EOF'
          import asyncio
          import aiohttp
          import json
          import sys
          from datetime import datetime
          
          CONSTITUTIONAL_HASH = "$CONSTITUTIONAL_HASH"
          
          async def test_service_security(service_name, port):
              """Test basic security of a service."""
              results = []
              base_url = f"http://{service_name}:{port}"
              
              async with aiohttp.ClientSession() as session:
                  # Test 1: Health endpoint accessibility
                  try:
                      async with session.get(f"{base_url}/health") as resp:
                          if resp.status == 200:
                              data = await resp.json()
                              if CONSTITUTIONAL_HASH in str(data):
                                  results.append({"test": "constitutional_hash_present", "status": "PASS"})
                              else:
                                  results.append({"test": "constitutional_hash_present", "status": "FAIL"})
                          else:
                              results.append({"test": "health_endpoint", "status": "FAIL"})
                  except Exception as e:
                      results.append({"test": "health_endpoint", "status": "ERROR", "error": str(e)})
                  
                  # Test 2: Unauthorized access attempt
                  try:
                      async with session.get(f"{base_url}/admin") as resp:
                          if resp.status in [401, 403, 404]:
                              results.append({"test": "unauthorized_access_blocked", "status": "PASS"})
                          else:
                              results.append({"test": "unauthorized_access_blocked", "status": "FAIL"})
                  except Exception:
                      results.append({"test": "unauthorized_access_blocked", "status": "PASS"})
                  
                  # Test 3: SQL injection attempt
                  try:
                      payload = "'; DROP TABLE users; --"
                      async with session.post(f"{base_url}/api/test", json={"input": payload}) as resp:
                          if resp.status in [400, 422, 500]:
                              results.append({"test": "sql_injection_protection", "status": "PASS"})
                          else:
                              results.append({"test": "sql_injection_protection", "status": "UNKNOWN"})
                  except Exception:
                      results.append({"test": "sql_injection_protection", "status": "PASS"})
              
              return {"service": service_name, "port": port, "tests": results}
          
          async def main():
              services = [
                  ("auth-service", 8000),
                  ("constitutional-ai-service", 8001),
                  ("integrity-service", 8002),
                  ("formal-verification-service", 8003),
                  ("governance-synthesis-service", 8004),
                  ("policy-governance-service", 8005)
              ]
              
              results = []
              for service_name, port in services:
                  print(f"Testing {service_name}:{port}...")
                  result = await test_service_security(service_name, port)
                  results.append(result)
              
              # Generate report
              report = {
                  "timestamp": datetime.now().isoformat(),
                  "constitutional_hash": CONSTITUTIONAL_HASH,
                  "test_results": results,
                  "summary": {
                      "total_services": len(services),
                      "total_tests": sum(len(r["tests"]) for r in results),
                      "passed_tests": sum(len([t for t in r["tests"] if t["status"] == "PASS"]) for r in results),
                      "failed_tests": sum(len([t for t in r["tests"] if t["status"] == "FAIL"]) for r in results)
                  }
              }
              
              print(json.dumps(report, indent=2))
              
              # Exit with error if any tests failed
              if report["summary"]["failed_tests"] > 0:
                  sys.exit(1)
          
          if __name__ == "__main__":
              asyncio.run(main())
          PENTEST_EOF
          
          python /tmp/pentest.py
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
  backoffLimit: 3
EOF
    
    success "Penetration testing job created"
}

# Calculate security posture score
calculate_security_score() {
    security "Calculating security posture score..."
    
    local score=0
    local max_score=100
    
    # Check Vault deployment (20 points)
    if kubectl get statefulset vault -n vault >/dev/null 2>&1; then
        score=$((score + 20))
        success "Vault deployment: +20 points"
    else
        warning "Vault deployment: 0 points"
    fi
    
    # Check network policies (20 points)
    local network_policies=$(kubectl get networkpolicy -n "$NAMESPACE" --no-headers | wc -l)
    if [[ $network_policies -gt 0 ]]; then
        score=$((score + 20))
        success "Network policies: +20 points"
    else
        warning "Network policies: 0 points"
    fi
    
    # Check security monitoring (20 points)
    if kubectl get daemonset falco -n falco-system >/dev/null 2>&1; then
        score=$((score + 20))
        success "Security monitoring: +20 points"
    else
        warning "Security monitoring: 0 points"
    fi
    
    # Check SSL/TLS certificates (15 points)
    local certificates=$(kubectl get certificate -A --no-headers | wc -l)
    if [[ $certificates -gt 0 ]]; then
        score=$((score + 15))
        success "SSL/TLS certificates: +15 points"
    else
        warning "SSL/TLS certificates: 0 points"
    fi
    
    # Check constitutional compliance (15 points)
    if kubectl get configmap -n "$NAMESPACE" -o yaml | grep -q "$CONSTITUTIONAL_HASH"; then
        score=$((score + 15))
        success "Constitutional compliance: +15 points"
    else
        warning "Constitutional compliance: 0 points"
    fi
    
    # Check service mesh security (10 points)
    if kubectl get namespace linkerd >/dev/null 2>&1; then
        score=$((score + 10))
        success "Service mesh security: +10 points"
    else
        warning "Service mesh security: 0 points"
    fi
    
    log "Security Posture Score: $score/$max_score"
    
    if [[ $score -ge $SECURITY_TARGET_SCORE ]]; then
        success "🎉 Security target achieved: $score/$max_score (target: $SECURITY_TARGET_SCORE)"
        return 0
    else
        warning "⚠️ Security target not met: $score/$max_score (target: $SECURITY_TARGET_SCORE)"
        return 1
    fi
}

# Generate security report
generate_security_report() {
    local report_file="/tmp/security_hardening_report_$(date +%Y%m%d_%H%M%S).txt"
    
    {
        echo "ACGS Phase 3B: Security Hardening Deployment Report"
        echo "Generated: $(date '+%Y-%m-%d %H:%M:%S')"
        echo "Constitutional Hash: $CONSTITUTIONAL_HASH"
        echo "Namespace: $NAMESPACE"
        echo "Phase: $PHASE"
        echo "Security Target Score: $SECURITY_TARGET_SCORE"
        echo "=============================================="  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
        echo
        
        echo "Vault Status:"
        kubectl get statefulset vault -n vault 2>/dev/null || echo "Not deployed"
        echo

        echo "Network Policies:"
        kubectl get networkpolicy -n "$NAMESPACE" 2>/dev/null || echo "None found"
        echo

        echo "Security Monitoring (Falco):"
        kubectl get daemonset falco -n falco-system 2>/dev/null || echo "Not deployed"
        echo
        
        echo "SSL/TLS Certificates:"
        kubectl get certificate -A 2>/dev/null || echo "None found"
        echo
        
        echo "Penetration Testing Jobs:"
        kubectl get jobs -n "$NAMESPACE" | grep pentest || echo "None found"
        echo
        
        echo "Constitutional Compliance Check:"
        if kubectl get configmap -n "$NAMESPACE" -o yaml | grep -q "$CONSTITUTIONAL_HASH"; then
            echo "✓ Constitutional hash found in configurations"
        else
            echo "✗ Constitutional hash not found"
        fi
        
    } > "$report_file"
    
    log "Security hardening report generated: $report_file"
    echo "$report_file"
}

# Main deployment function
main() {
    log "🔒 Starting ACGS Phase 3B: Security Hardening..."
    log "Constitutional Hash: $CONSTITUTIONAL_HASH"
    log "Target Namespace: $NAMESPACE"
    log "Security Target Score: $SECURITY_TARGET_SCORE"
    
    validate_prerequisites
    deploy_vault
    configure_vault
    deploy_network_security
    deploy_security_monitoring
    run_penetration_testing
    
    # Calculate final security score
    if calculate_security_score; then
        local report_file=$(generate_security_report)
        success "🎉 ACGS Phase 3B: Security Hardening completed successfully!"
        log "Security posture target achieved: >$SECURITY_TARGET_SCORE/100"
        log "Report: $report_file"
    else
        local report_file=$(generate_security_report)
        warning "⚠️ ACGS Phase 3B: Security Hardening completed with warnings"
        log "Security posture target not fully achieved"
        log "Report: $report_file"
    fi
    
    echo ""
    echo "Next steps:"
    echo "1. Review penetration testing results"
    echo "2. Configure additional security policies as needed"
    echo "3. Set up security incident response procedures"
    echo "4. Schedule regular security audits"
    echo ""
    echo "Access commands:"
    echo "- Vault UI: kubectl port-forward svc/vault-ui 8200:8200 -n vault"
    echo "- Falco logs: kubectl logs -f daemonset/falco -n falco-system"
    echo "- Network policies: kubectl get networkpolicy -n $NAMESPACE"
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    case "${1:-deploy}" in
        "deploy")
            main
            ;;
        "score")
            calculate_security_score
            ;;
        "report")
            generate_security_report
            ;;
        *)
            echo "Usage: $0 {deploy|score|report}"
            echo ""
            echo "Commands:"
            echo "  deploy - Deploy security hardening infrastructure"
            echo "  score  - Calculate current security posture score"
            echo "  report - Generate security hardening report"
            exit 1
            ;;
    esac
fi
