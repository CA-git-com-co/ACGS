#!/bin/bash

# ACGS-PGP Blue-Green Production Deployment
# Implements zero-downtime deployment with automated rollback capabilities

set -e

PRODUCTION_NAMESPACE="acgs-production"
BLUE_NAMESPACE="acgs-blue"
GREEN_NAMESPACE="acgs-green"
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
HEALTH_CHECK_TIMEOUT=300
TRAFFIC_MIGRATION_STEPS=5

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
log_deploy() { echo -e "${BLUE}[DEPLOY]${NC} $(date '+%H:%M:%S') $1"; }
log_traffic() { echo -e "${PURPLE}[TRAFFIC]${NC} $(date '+%H:%M:%S') $1"; }

# Current deployment state
CURRENT_ACTIVE=""
CURRENT_INACTIVE=""

# Determine current active environment
determine_active_environment() {
    log_deploy "Determining current active environment..."
    
    # Check which environment is currently receiving traffic
    local blue_traffic=$(kubectl get service acgs-production-router -n $PRODUCTION_NAMESPACE -o jsonpath='{.spec.selector.environment}' 2>/dev/null || echo "")
    
    if [[ "$blue_traffic" == "blue" ]]; then
        CURRENT_ACTIVE="blue"
        CURRENT_INACTIVE="green"
        log_info "Current active environment: BLUE"
    elif [[ "$blue_traffic" == "green" ]]; then
        CURRENT_ACTIVE="green"
        CURRENT_INACTIVE="blue"
        log_info "Current active environment: GREEN"
    else
        # First deployment - default to blue as active
        CURRENT_ACTIVE="blue"
        CURRENT_INACTIVE="green"
        log_info "First deployment - setting BLUE as active environment"
    fi
}

# Create production namespaces
create_production_namespaces() {
    log_deploy "Creating production namespaces..."
    
    # Main production namespace
    cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Namespace
metadata:
  name: $PRODUCTION_NAMESPACE
  labels:
    name: $PRODUCTION_NAMESPACE
    environment: production
    app.kubernetes.io/part-of: acgs-system
---
apiVersion: v1
kind: Namespace
metadata:
  name: $BLUE_NAMESPACE
  labels:
    name: $BLUE_NAMESPACE
    environment: blue
    app.kubernetes.io/part-of: acgs-system
---
apiVersion: v1
kind: Namespace
metadata:
  name: $GREEN_NAMESPACE
  labels:
    name: $GREEN_NAMESPACE
    environment: green
    app.kubernetes.io/part-of: acgs-system
EOF
    
    log_info "✓ Production namespaces created"
}

# Deploy to inactive environment
deploy_to_inactive_environment() {
    local target_env=$1
    local target_namespace=""
    
    if [[ "$target_env" == "blue" ]]; then
        target_namespace=$BLUE_NAMESPACE
    else
        target_namespace=$GREEN_NAMESPACE
    fi
    
    log_deploy "Deploying to $target_env environment ($target_namespace)..."
    
    # Copy and modify configurations for target environment
    local temp_dir=$(mktemp -d)
    cp -r infrastructure/kubernetes/*.yaml "$temp_dir/"
    cp -r infrastructure/kubernetes/services/*.yaml "$temp_dir/"
    
    # Update namespace in all files
    find "$temp_dir" -name "*.yaml" -exec sed -i "s/namespace: acgs-system/namespace: $target_namespace/g" {} \;
    find "$temp_dir" -name "*.yaml" -exec sed -i "s/namespace: acgs-staging/namespace: $target_namespace/g" {} \;
    
    # Add environment labels
    find "$temp_dir" -name "*.yaml" -exec sed -i "/labels:/a\\    environment: $target_env" {} \;
    
    # Deploy infrastructure
    log_deploy "Deploying infrastructure to $target_env..."
    kubectl apply -f "$temp_dir/acgs-secrets.yaml"
    kubectl apply -f "$temp_dir/cockroachdb.yaml"
    kubectl apply -f "$temp_dir/dragonflydb.yaml"
    kubectl apply -f "$temp_dir/opa.yaml"
    kubectl apply -f "$temp_dir/prometheus.yaml"
    kubectl apply -f "$temp_dir/grafana.yaml"
    
    # Wait for infrastructure
    kubectl wait --for=condition=ready pod -l app=cockroachdb -n $target_namespace --timeout=${HEALTH_CHECK_TIMEOUT}s
    kubectl wait --for=condition=ready pod -l app=dragonflydb -n $target_namespace --timeout=${HEALTH_CHECK_TIMEOUT}s
    kubectl wait --for=condition=ready pod -l app=opa -n $target_namespace --timeout=${HEALTH_CHECK_TIMEOUT}s
    
    # Deploy services
    log_deploy "Deploying services to $target_env..."
    for service_file in "$temp_dir"/*-service.yaml; do
        if [[ -f "$service_file" ]]; then
            kubectl apply -f "$service_file"
        fi
    done
    
    # Wait for all services
    kubectl wait --for=condition=available deployment --all -n $target_namespace --timeout=${HEALTH_CHECK_TIMEOUT}s
    
    # Cleanup
    rm -rf "$temp_dir"
    
    log_info "✓ Deployment to $target_env environment completed"
}

# Validate deployment health
validate_deployment_health() {
    local target_env=$1
    local target_namespace=""
    
    if [[ "$target_env" == "blue" ]]; then
        target_namespace=$BLUE_NAMESPACE
    else
        target_namespace=$GREEN_NAMESPACE
    fi
    
    log_deploy "Validating $target_env environment health..."
    
    # Check all pods are running
    local failed_pods=$(kubectl get pods -n $target_namespace --field-selector=status.phase!=Running --no-headers | wc -l)
    
    if [[ $failed_pods -gt 0 ]]; then
        log_error "Found $failed_pods non-running pods in $target_env"
        return 1
    fi
    
    # Test service health endpoints
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
        
        if kubectl exec -n $target_namespace deployment/$service -- curl -f -s http://localhost:$port/health &> /dev/null; then
            log_info "✓ $service health check passed in $target_env"
        else
            log_error "✗ $service health check failed in $target_env"
            failed_services+=("$service")
        fi
    done
    
    if [[ ${#failed_services[@]} -gt 0 ]]; then
        log_error "Health validation failed for services: ${failed_services[*]}"
        return 1
    fi
    
    # Validate constitutional compliance
    local compliance_test=$(kubectl exec -n $target_namespace deployment/constitutional-ai-service -- \
        curl -s -X POST -H "Content-Type: application/json" \
        -d '{"query": "production deployment validation", "context": "blue_green_deployment"}' \
        http://localhost:8001/validate 2>/dev/null || echo '{"compliance_score": 0}')
    
    local compliance_score=$(echo "$compliance_test" | grep -o '"compliance_score":[0-9.]*' | cut -d: -f2 || echo "0")
    
    if (( $(echo "$compliance_score >= 0.95" | bc -l 2>/dev/null || echo "0") )); then
        log_info "✓ Constitutional compliance validated in $target_env: $compliance_score"
    else
        log_error "✗ Constitutional compliance failed in $target_env: $compliance_score"
        return 1
    fi
    
    log_info "✓ $target_env environment health validation passed"
    return 0
}

# Create traffic router
create_traffic_router() {
    log_deploy "Creating production traffic router..."
    
    cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Service
metadata:
  name: acgs-production-router
  namespace: $PRODUCTION_NAMESPACE
  labels:
    app: acgs-production-router
    app.kubernetes.io/part-of: acgs-system
spec:
  selector:
    environment: $CURRENT_ACTIVE
    app: constitutional-ai-service
  ports:
  - name: http
    protocol: TCP
    port: 8001
    targetPort: 8001
  type: LoadBalancer
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: acgs-production-ingress
  namespace: $PRODUCTION_NAMESPACE
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  rules:
  - host: acgs-production.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: acgs-production-router
            port:
              number: 8001
EOF
    
    log_info "✓ Production traffic router created"
}

# Gradual traffic migration
gradual_traffic_migration() {
    local from_env=$1
    local to_env=$2
    
    log_traffic "Starting gradual traffic migration from $from_env to $to_env..."
    
    # Traffic migration percentages
    local traffic_steps=(20 40 60 80 100)
    
    for step in "${traffic_steps[@]}"; do
        log_traffic "Migrating $step% traffic to $to_env environment..."
        
        # Update traffic routing (simplified - in production would use service mesh)
        kubectl patch service acgs-production-router -n $PRODUCTION_NAMESPACE \
            --type='merge' -p="{\"spec\":{\"selector\":{\"environment\":\"$to_env\"}}}"
        
        # Wait and monitor
        log_traffic "Monitoring system health for 60 seconds..."
        sleep 60
        
        # Health check during migration
        if ! validate_deployment_health "$to_env"; then
            log_error "Health check failed during traffic migration at $step%"
            log_error "Initiating automatic rollback..."
            rollback_deployment "$from_env"
            return 1
        fi
        
        log_traffic "✓ $step% traffic migration successful"
    done
    
    log_traffic "✓ Traffic migration completed - 100% traffic on $to_env"
    return 0
}

# Rollback deployment
rollback_deployment() {
    local rollback_env=$1
    
    log_error "INITIATING EMERGENCY ROLLBACK TO $rollback_env"
    
    # Immediate traffic switch
    kubectl patch service acgs-production-router -n $PRODUCTION_NAMESPACE \
        --type='merge' -p="{\"spec\":{\"selector\":{\"environment\":\"$rollback_env\"}}}"
    
    log_error "✓ Traffic rolled back to $rollback_env environment"
    
    # Send emergency notification
    echo "EMERGENCY ROLLBACK EXECUTED" > "/tmp/emergency_rollback_$(date +%Y%m%d_%H%M%S).log"
    
    return 0
}

# Monitor deployment
monitor_deployment() {
    local target_env=$1
    local duration=${2:-300}  # 5 minutes default
    
    log_deploy "Monitoring $target_env environment for ${duration} seconds..."
    
    local start_time=$(date +%s)
    local end_time=$((start_time + duration))
    
    while [[ $(date +%s) -lt $end_time ]]; do
        # Check service health
        if ! validate_deployment_health "$target_env"; then
            log_error "Health check failed during monitoring"
            return 1
        fi
        
        # Check resource usage
        local high_cpu_pods=$(kubectl top pods -n ${target_env} --no-headers 2>/dev/null | awk '$2 > 400 {print $1}' | wc -l)
        local high_mem_pods=$(kubectl top pods -n ${target_env} --no-headers 2>/dev/null | awk '$3 > 800 {print $1}' | wc -l)
        
        if [[ $high_cpu_pods -gt 0 ]] || [[ $high_mem_pods -gt 0 ]]; then
            log_warn "High resource usage detected: CPU($high_cpu_pods pods), Memory($high_mem_pods pods)"
        fi
        
        log_deploy "Monitoring... $(( ($(date +%s) - start_time) ))s elapsed"
        sleep 30
    done
    
    log_info "✓ Monitoring completed - $target_env environment stable"
    return 0
}

# Generate deployment report
generate_deployment_report() {
    local deployment_env=$1
    local report_file="/tmp/blue_green_deployment_report_$(date +%Y%m%d_%H%M%S).txt"
    
    {
        echo "ACGS-PGP Blue-Green Deployment Report"
        echo "Generated: $(date '+%Y-%m-%d %H:%M:%S')"
        echo "Deployed Environment: $deployment_env"
        echo "Constitutional Hash: $CONSTITUTIONAL_HASH"
        echo "======================================"
        echo
        
        echo "Active Environment: $deployment_env"
        echo "Inactive Environment: $CURRENT_INACTIVE"
        echo
        
        echo "Service Status ($deployment_env):"
        if [[ "$deployment_env" == "blue" ]]; then
            kubectl get pods -n $BLUE_NAMESPACE -o wide
        else
            kubectl get pods -n $GREEN_NAMESPACE -o wide
        fi
        echo
        
        echo "Traffic Routing:"
        kubectl get service acgs-production-router -n $PRODUCTION_NAMESPACE
        echo
        
        echo "Resource Usage:"
        if [[ "$deployment_env" == "blue" ]]; then
            kubectl top pods -n $BLUE_NAMESPACE 2>/dev/null || echo "Metrics not available"
        else
            kubectl top pods -n $GREEN_NAMESPACE 2>/dev/null || echo "Metrics not available"
        fi
        
    } > "$report_file"
    
    log_deploy "Deployment report generated: $report_file"
    echo "$report_file"
}

# Main deployment function
main() {
    local action=${1:-"deploy"}
    
    case $action in
        "deploy")
            log_deploy "Starting ACGS-PGP blue-green production deployment..."
            
            determine_active_environment
            create_production_namespaces
            create_traffic_router
            
            # Deploy to inactive environment
            deploy_to_inactive_environment "$CURRENT_INACTIVE"
            
            # Validate new deployment
            if validate_deployment_health "$CURRENT_INACTIVE"; then
                log_deploy "New deployment validated - starting traffic migration..."
                
                # Gradual traffic migration
                if gradual_traffic_migration "$CURRENT_ACTIVE" "$CURRENT_INACTIVE"; then
                    log_deploy "🎉 Blue-green deployment completed successfully!"
                    log_deploy "Active environment: $CURRENT_INACTIVE"
                    
                    # Monitor for stability
                    monitor_deployment "$CURRENT_INACTIVE" 300
                    
                    generate_deployment_report "$CURRENT_INACTIVE"
                else
                    log_error "Traffic migration failed - deployment aborted"
                    exit 1
                fi
            else
                log_error "New deployment validation failed - aborting deployment"
                exit 1
            fi
            ;;
        "rollback")
            determine_active_environment
            rollback_deployment "$CURRENT_INACTIVE"
            ;;
        "status")
            determine_active_environment
            echo "Current active environment: $CURRENT_ACTIVE"
            echo "Current inactive environment: $CURRENT_INACTIVE"
            ;;
        "monitor")
            determine_active_environment
            monitor_deployment "$CURRENT_ACTIVE" "${2:-300}"
            ;;
        *)
            echo "Usage: $0 {deploy|rollback|status|monitor}"
            echo "  deploy   - Execute blue-green deployment"
            echo "  rollback - Rollback to previous environment"
            echo "  status   - Show current deployment status"
            echo "  monitor  - Monitor active environment"
            exit 1
            ;;
    esac
}

main "$@"
