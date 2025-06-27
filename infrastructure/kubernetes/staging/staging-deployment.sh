#!/bin/bash

# ACGS-PGP Staging Deployment Script
# Deploys the complete ACGS-PGP system to staging environment with validation

set -e

NAMESPACE="acgs-staging"
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
DEPLOYMENT_TIMEOUT=600

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $(date '+%H:%M:%S') $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $(date '+%H:%M:%S') $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $(date '+%H:%M:%S') $1"; }
log_deploy() { echo -e "${BLUE}[DEPLOY]${NC} $(date '+%H:%M:%S') $1"; }

# Pre-deployment validation
pre_deployment_validation() {
    log_deploy "Running pre-deployment validation..."
    
    # Check kubectl connectivity
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster"
        return 1
    fi
    
    # Validate configurations
    log_deploy "Validating Kubernetes configurations..."
    if ! ./infrastructure/kubernetes/quick-validate.sh; then
        log_error "Configuration validation failed"
        return 1
    fi
    
    log_info "✓ Pre-deployment validation passed"
    return 0
}

# Create staging namespace
create_staging_namespace() {
    log_deploy "Creating staging namespace..."
    
    cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Namespace
metadata:
  name: $NAMESPACE
  labels:
    name: $NAMESPACE
    environment: staging
    app.kubernetes.io/part-of: acgs-system
---
apiVersion: v1
kind: ResourceQuota
metadata:
  name: acgs-staging-quota
  namespace: $NAMESPACE
spec:
  hard:
    requests.cpu: "2"
    requests.memory: 4Gi
    limits.cpu: "4"
    limits.memory: 8Gi
    pods: "50"
    persistentvolumeclaims: "10"
EOF
    
    log_info "✓ Staging namespace created with resource quotas"
}

# Deploy infrastructure components
deploy_infrastructure() {
    log_deploy "Deploying infrastructure components..."
    
    # Update namespace in configuration files for staging
    local temp_dir=$(mktemp -d)
    
    # Copy and modify configurations for staging
    cp -r infrastructure/kubernetes/*.yaml "$temp_dir/"
    
    # Update namespace in all files
    find "$temp_dir" -name "*.yaml" -exec sed -i "s/namespace: acgs-system/namespace: $NAMESPACE/g" {} \;
    
    # Deploy secrets
    log_deploy "Deploying secrets..."
    kubectl apply -f "$temp_dir/acgs-secrets.yaml"
    
    # Deploy databases
    log_deploy "Deploying CockroachDB..."
    kubectl apply -f "$temp_dir/cockroachdb.yaml"
    
    log_deploy "Deploying DragonflyDB..."
    kubectl apply -f "$temp_dir/dragonflydb.yaml"
    
    # Wait for databases
    log_deploy "Waiting for databases to be ready..."
    kubectl wait --for=condition=ready pod -l app=cockroachdb -n $NAMESPACE --timeout=${DEPLOYMENT_TIMEOUT}s
    kubectl wait --for=condition=ready pod -l app=dragonflydb -n $NAMESPACE --timeout=${DEPLOYMENT_TIMEOUT}s
    
    # Deploy policy engine
    log_deploy "Deploying OPA..."
    kubectl apply -f "$temp_dir/opa.yaml"
    
    # Deploy monitoring
    log_deploy "Deploying Prometheus..."
    kubectl apply -f "$temp_dir/prometheus.yaml"
    
    log_deploy "Deploying Grafana..."
    kubectl apply -f "$temp_dir/grafana.yaml"
    
    # Wait for infrastructure
    kubectl wait --for=condition=ready pod -l app=opa -n $NAMESPACE --timeout=180s
    kubectl wait --for=condition=ready pod -l app=prometheus -n $NAMESPACE --timeout=180s
    
    # Cleanup
    rm -rf "$temp_dir"
    
    log_info "✓ Infrastructure deployment completed"
}

# Deploy ACGS-PGP services
deploy_services() {
    log_deploy "Deploying ACGS-PGP services..."
    
    local temp_dir=$(mktemp -d)
    
    # Copy and modify service configurations for staging
    cp -r infrastructure/kubernetes/services/*.yaml "$temp_dir/"
    
    # Update namespace in all service files
    find "$temp_dir" -name "*.yaml" -exec sed -i "s/namespace: acgs-system/namespace: $NAMESPACE/g" {} \;
    
    # Deploy services in dependency order
    local services=(
        "auth-service"
        "integrity-service"
        "constitutional-ai-service"
        "formal-verification-service"
        "governance-synthesis-service"
        "policy-governance-service"
        "evolutionary-computation-service"
        "model-orchestrator-service"
    )
    
    for service in "${services[@]}"; do
        log_deploy "Deploying $service..."
        kubectl apply -f "$temp_dir/$service.yaml"
        
        # Wait for deployment to be ready
        kubectl wait --for=condition=available deployment/$service -n $NAMESPACE --timeout=300s
    done
    
    # Wait for all services to be ready
    log_deploy "Waiting for all services to be ready..."
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/part-of=acgs-system -n $NAMESPACE --timeout=${DEPLOYMENT_TIMEOUT}s
    
    # Cleanup
    rm -rf "$temp_dir"
    
    log_info "✓ Services deployment completed"
}

# Validate staging deployment
validate_staging_deployment() {
    log_deploy "Validating staging deployment..."
    
    # Check all pods are running
    local failed_pods=$(kubectl get pods -n $NAMESPACE --field-selector=status.phase!=Running --no-headers | wc -l)
    
    if [[ $failed_pods -gt 0 ]]; then
        log_error "Found $failed_pods non-running pods"
        kubectl get pods -n $NAMESPACE
        return 1
    fi
    
    # Check service endpoints
    log_deploy "Validating service endpoints..."
    local services=(
        "auth-service:8000"
        "constitutional-ai-service:8001"
        "integrity-service:8002"
        "formal-verification-service:8003"
        "governance-synthesis-service:8004"
        "policy-governance-service:8005"
        "evolutionary-computation-service:8006"
        "model-orchestrator-service:8007"
    )
    
    local failed_services=()
    
    for service_port in "${services[@]}"; do
        local service=$(echo $service_port | cut -d: -f1)
        local port=$(echo $service_port | cut -d: -f2)
        
        # Test health endpoint
        if kubectl exec -n $NAMESPACE deployment/$service -- curl -f -s http://localhost:$port/health &> /dev/null; then
            log_info "✓ $service health check passed"
        else
            log_error "✗ $service health check failed"
            failed_services+=("$service")
        fi
    done
    
    if [[ ${#failed_services[@]} -gt 0 ]]; then
        log_error "Service validation failed: ${failed_services[*]}"
        return 1
    fi
    
    # Validate constitutional compliance
    log_deploy "Validating constitutional compliance..."
    local compliance_test=$(kubectl exec -n $NAMESPACE deployment/constitutional-ai-service -- \
        curl -s -X POST -H "Content-Type: application/json" \
        -d '{"query": "staging validation test", "context": "deployment_validation"}' \
        http://localhost:8001/validate 2>/dev/null || echo '{"compliance_score": 0}')
    
    # Extract compliance score (simplified)
    local compliance_score=$(echo "$compliance_test" | grep -o '"compliance_score":[0-9.]*' | cut -d: -f2 || echo "0")
    
    if (( $(echo "$compliance_score >= 0.95" | bc -l 2>/dev/null || echo "0") )); then
        log_info "✓ Constitutional compliance validated: $compliance_score"
    else
        log_error "✗ Constitutional compliance failed: $compliance_score"
        return 1
    fi
    
    log_info "✓ Staging deployment validation completed successfully"
    return 0
}

# Generate staging deployment report
generate_staging_report() {
    local report_file="/tmp/staging_deployment_report_$(date +%Y%m%d_%H%M%S).txt"
    
    {
        echo "ACGS-PGP Staging Deployment Report"
        echo "Generated: $(date '+%Y-%m-%d %H:%M:%S')"
        echo "Namespace: $NAMESPACE"
        echo "Constitutional Hash: $CONSTITUTIONAL_HASH"
        echo "=================================="
        echo
        
        echo "Pod Status:"
        kubectl get pods -n $NAMESPACE -o wide
        echo
        
        echo "Service Status:"
        kubectl get svc -n $NAMESPACE
        echo
        
        echo "Deployment Status:"
        kubectl get deployments -n $NAMESPACE
        echo
        
        echo "Resource Usage:"
        kubectl top pods -n $NAMESPACE 2>/dev/null || echo "Metrics not available"
        echo
        
        echo "Recent Events:"
        kubectl get events -n $NAMESPACE --sort-by='.lastTimestamp' | tail -10
        
    } > "$report_file"
    
    log_deploy "Staging deployment report generated: $report_file"
    echo "$report_file"
}

# Cleanup staging environment
cleanup_staging() {
    log_deploy "Cleaning up staging environment..."
    
    # Delete all resources in staging namespace
    kubectl delete namespace $NAMESPACE --ignore-not-found=true
    
    log_info "✓ Staging environment cleaned up"
}

# Main deployment function
main() {
    local action=${1:-"deploy"}
    
    case $action in
        "deploy")
            log_deploy "Starting ACGS-PGP staging deployment..."
            
            pre_deployment_validation
            create_staging_namespace
            deploy_infrastructure
            deploy_services
            validate_staging_deployment
            
            local report_file=$(generate_staging_report)
            
            log_deploy "🎉 Staging deployment completed successfully!"
            log_deploy "Report: $report_file"
            log_deploy "Access services via port-forwarding:"
            log_deploy "  kubectl port-forward svc/grafana 3000:3000 -n $NAMESPACE"
            log_deploy "  kubectl port-forward svc/constitutional-ai-service 8001:8001 -n $NAMESPACE"
            ;;
        "validate")
            validate_staging_deployment
            ;;
        "cleanup")
            cleanup_staging
            ;;
        "report")
            generate_staging_report
            ;;
        *)
            echo "Usage: $0 {deploy|validate|cleanup|report}"
            echo "  deploy   - Full staging deployment"
            echo "  validate - Validate existing staging deployment"
            echo "  cleanup  - Clean up staging environment"
            echo "  report   - Generate staging deployment report"
            exit 1
            ;;
    esac
}

main "$@"
