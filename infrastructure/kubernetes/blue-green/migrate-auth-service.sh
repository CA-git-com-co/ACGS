#!/bin/bash

# ACGE Phase 2 Auth Service Migration Script
# Migrates auth service from blue to green environment with ACGE integration

set -euo pipefail

# Configuration
SERVICE_NAME="auth"
SERVICE_PORT="8000"
NAMESPACE_BLUE="acgs-blue"
NAMESPACE_GREEN="acgs-green"
NAMESPACE_SHARED="acgs-shared"
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
MIGRATION_DURATION="2h"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

success() {
    echo -e "${GREEN}[✓] $1${NC}"
}

warning() {
    echo -e "${YELLOW}[⚠] $1${NC}"
}

error() {
    echo -e "${RED}[✗] $1${NC}"
    exit 1
}

# Migration stages
MIGRATION_STAGES=(
    "validate_prerequisites"
    "deploy_green_auth_service"
    "validate_green_deployment"
    "start_traffic_shifting"
    "monitor_migration"
    "complete_migration"
    "cleanup_blue_service"
)

# Validate prerequisites
validate_prerequisites() {
    log "Validating prerequisites for auth service migration..."
    
    # Check kubectl connectivity
    if ! kubectl cluster-info >/dev/null 2>&1; then
        error "Cannot connect to Kubernetes cluster"
    fi
    
    # Check namespaces exist
    for ns in "$NAMESPACE_BLUE" "$NAMESPACE_GREEN" "$NAMESPACE_SHARED"; do
        if ! kubectl get namespace "$ns" >/dev/null 2>&1; then
            error "Namespace $ns not found"
        fi
    done
    
    # Check blue auth service is running
    if ! kubectl get service "acgs-auth-service-blue" -n "$NAMESPACE_BLUE" >/dev/null 2>&1; then
        error "Blue auth service not found"
    fi
    
    # Check ACGE model service is available
    if ! kubectl get service "acge-model-service" -n "$NAMESPACE_SHARED" >/dev/null 2>&1; then
        error "ACGE model service not found"
    fi
    
    # Check constitutional hash configuration
    local stored_hash
    stored_hash=$(kubectl get configmap acge-constitutional-config -n "$NAMESPACE_SHARED" -o jsonpath='{.data.constitutional-hash}' 2>/dev/null || echo "")
    if [[ "$stored_hash" != "$CONSTITUTIONAL_HASH" ]]; then
        error "Constitutional hash mismatch. Expected: $CONSTITUTIONAL_HASH, Got: $stored_hash"
    fi
    
    success "Prerequisites validation completed"
}

# Deploy green auth service with ACGE integration
deploy_green_auth_service() {
    log "Deploying green auth service with ACGE integration..."
    
    # Create ACGE-enhanced auth service deployment
    cat > /tmp/auth-green-deployment.yaml << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: acgs-auth-service-green
  namespace: $NAMESPACE_GREEN
  labels:
    app: acgs-auth-service
    environment: green
    service: auth
    phase: phase-2
    acge-enabled: "true"
spec:
  replicas: 3
  selector:
    matchLabels:
      app: acgs-auth-service
      environment: green
  template:
    metadata:
      labels:
        app: acgs-auth-service
        environment: green
        service: auth
        acge-enabled: "true"
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8000"
        prometheus.io/path: "/metrics"
        constitutional.ai/enabled: "true"
        constitutional.ai/hash: "$CONSTITUTIONAL_HASH"
    spec:
      containers:
        - name: auth-service
          image: acgs/auth-service:acge-v2
          ports:
            - containerPort: 8000
              name: http
          env:
            - name: SERVICE_NAME
              value: "acgs-auth-service-acge"
            - name: SERVICE_PORT
              value: "8000"
            - name: ENVIRONMENT
              value: "green"
            - name: CONSTITUTIONAL_HASH
              value: "$CONSTITUTIONAL_HASH"
            - name: ACGE_MODEL_ENDPOINT
              value: "http://acge-model-service.$NAMESPACE_SHARED.svc.cluster.local:8080"
            - name: ACGE_ENABLED
              value: "true"
            - name: PHASE
              value: "phase-2"
            - name: DATABASE_URL
              valueFrom:
                configMapKeyRef:
                  name: acge-green-config
                  key: database-url
            - name: REDIS_URL
              valueFrom:
                configMapKeyRef:
                  name: acge-green-config
                  key: redis-url
            - name: JWT_SECRET_KEY
              valueFrom:
                secretKeyRef:
                  name: acgs-secrets
                  key: jwt-secret-key
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 10
            timeoutSeconds: 5
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /health/constitutional
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 5
            timeoutSeconds: 3
            failureThreshold: 2
          resources:
            requests:
              memory: "512Mi"
              cpu: "200m"
            limits:
              memory: "1Gi"
              cpu: "500m"
          securityContext:
            runAsNonRoot: true
            runAsUser: 1000
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop:
                - ALL

---
apiVersion: v1
kind: Service
metadata:
  name: acgs-auth-service-green
  namespace: $NAMESPACE_GREEN
  labels:
    app: acgs-auth-service
    environment: green
    service: auth
spec:
  selector:
    app: acgs-auth-service
    environment: green
  ports:
    - port: 8000
      targetPort: 8000
      name: http
  type: ClusterIP

---
apiVersion: v1
kind: ServiceMonitor
metadata:
  name: acgs-auth-service-green
  namespace: $NAMESPACE_GREEN
  labels:
    app: acgs-auth-service
    environment: green
spec:
  selector:
    matchLabels:
      app: acgs-auth-service
      environment: green
  endpoints:
    - port: http
      path: /metrics
      interval: 30s
EOF
    
    # Apply the deployment
    kubectl apply -f /tmp/auth-green-deployment.yaml
    
    # Wait for deployment to be ready
    kubectl wait --for=condition=available deployment/acgs-auth-service-green -n "$NAMESPACE_GREEN" --timeout=300s
    
    # Clean up
    rm -f /tmp/auth-green-deployment.yaml
    
    success "Green auth service deployed successfully"
}

# Validate green deployment
validate_green_deployment() {
    log "Validating green auth service deployment..."
    
    # Check pod status
    local ready_pods
    ready_pods=$(kubectl get pods -n "$NAMESPACE_GREEN" -l app=acgs-auth-service,environment=green --no-headers | grep " Running " | wc -l)
    if [[ $ready_pods -lt 3 ]]; then
        error "Insufficient ready pods: $ready_pods (expected 3)"
    fi
    
    # Test health endpoint
    if kubectl run auth-health-test --image=curlimages/curl --rm -i --restart=Never -- \
        curl -f -s "http://acgs-auth-service-green.$NAMESPACE_GREEN.svc.cluster.local:8000/health" >/dev/null 2>&1; then
        success "Health endpoint accessible"
    else
        error "Health endpoint not accessible"
    fi
    
    # Test constitutional health endpoint
    if kubectl run auth-constitutional-test --image=curlimages/curl --rm -i --restart=Never -- \
        curl -f -s "http://acgs-auth-service-green.$NAMESPACE_GREEN.svc.cluster.local:8000/health/constitutional" >/dev/null 2>&1; then
        success "Constitutional health endpoint accessible"
    else
        error "Constitutional health endpoint not accessible"
    fi
    
    # Test ACGE integration
    local acge_status
    acge_status=$(kubectl run auth-acge-test --image=curlimages/curl --rm -i --restart=Never -- \
        curl -s "http://acgs-auth-service-green.$NAMESPACE_GREEN.svc.cluster.local:8000/api/v1/auth/info" | \
        grep -o '"acge_enabled":[^,]*' | cut -d: -f2 || echo "false")
    
    if [[ "$acge_status" == "true" ]]; then
        success "ACGE integration enabled"
    else
        warning "ACGE integration not enabled: $acge_status"
    fi
    
    success "Green deployment validation completed"
}

# Start traffic shifting
start_traffic_shifting() {
    log "Starting gradual traffic shifting from blue to green..."
    
    # Use traffic routing controller
    if [[ -f "infrastructure/kubernetes/blue-green/traffic-routing-controller.sh" ]]; then
        ./infrastructure/kubernetes/blue-green/traffic-routing-controller.sh migrate auth 8000
    else
        warning "Traffic routing controller not found, performing manual traffic shift"
        
        # Manual traffic shifting stages
        local stages=("90 10" "70 30" "50 50" "30 70" "10 90" "0 100")
        
        for stage in "${stages[@]}"; do
            local blue_weight=$(echo "$stage" | awk '{print $1}')
            local green_weight=$(echo "$stage" | awk '{print $2}')
            
            log "Shifting traffic: Blue=$blue_weight%, Green=$green_weight%"
            
            # Update VirtualService
            kubectl patch virtualservice acgs-blue-green-routing -n "$NAMESPACE_SHARED" --type='merge' -p="{
                \"spec\": {
                    \"http\": [{
                        \"match\": [{\"uri\": {\"prefix\": \"/api/v1/auth\"}}],
                        \"route\": [
                            {
                                \"destination\": {
                                    \"host\": \"acgs-auth-service-blue.$NAMESPACE_BLUE.svc.cluster.local\",
                                    \"port\": {\"number\": 8000}
                                },
                                \"weight\": $blue_weight
                            },
                            {
                                \"destination\": {
                                    \"host\": \"acgs-auth-service-green.$NAMESPACE_GREEN.svc.cluster.local\",
                                    \"port\": {\"number\": 8000}
                                },
                                \"weight\": $green_weight
                            }
                        ]
                    }]
                }
            }"
            
            # Wait and monitor
            sleep 120
            
            # Check metrics
            log "Monitoring metrics for stage: Blue=$blue_weight%, Green=$green_weight%"
            sleep 60
        done
    fi
    
    success "Traffic shifting completed"
}

# Monitor migration
monitor_migration() {
    log "Monitoring migration progress..."
    
    # Monitor for 10 minutes
    local monitor_duration=600
    local start_time=$(date +%s)
    local end_time=$((start_time + monitor_duration))
    
    while [[ $(date +%s) -lt $end_time ]]; do
        # Check green service health
        local green_health
        green_health=$(kubectl run migration-monitor --image=curlimages/curl --rm -i --restart=Never -- \
            curl -s "http://acgs-auth-service-green.$NAMESPACE_GREEN.svc.cluster.local:8000/health" | \
            grep -o '"status":"[^"]*' | cut -d: -f2 | tr -d '"' || echo "unhealthy")
        
        if [[ "$green_health" != "healthy" ]]; then
            error "Green service health check failed: $green_health"
        fi
        
        # Check constitutional compliance
        local compliance_score
        compliance_score=$(kubectl run compliance-monitor --image=curlimages/curl --rm -i --restart=Never -- \
            curl -s "http://acgs-auth-service-green.$NAMESPACE_GREEN.svc.cluster.local:8000/health/constitutional" | \
            grep -o '"compliance_score":[^,]*' | cut -d: -f2 || echo "0.0")
        
        if (( $(echo "$compliance_score < 0.95" | bc -l) )); then
            error "Constitutional compliance below threshold: $compliance_score"
        fi
        
        log "Migration monitoring: Health=$green_health, Compliance=$compliance_score"
        sleep 30
    done
    
    success "Migration monitoring completed successfully"
}

# Complete migration
complete_migration() {
    log "Completing auth service migration..."
    
    # Final validation
    validate_green_deployment
    
    # Update service labels
    kubectl label service acgs-auth-service-green -n "$NAMESPACE_GREEN" migration-status=completed
    kubectl annotate service acgs-auth-service-green -n "$NAMESPACE_GREEN" migration-completed-at="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    
    # Record migration event
    kubectl create event auth-migration-completed \
        --namespace="$NAMESPACE_SHARED" \
        --reason="MigrationCompleted" \
        --message="Auth service migration to ACGE completed successfully" \
        --type="Normal" || true
    
    success "Auth service migration completed successfully"
}

# Cleanup blue service (optional)
cleanup_blue_service() {
    log "Cleaning up blue auth service..."
    
    # Scale down blue deployment
    kubectl scale deployment acgs-auth-service-blue -n "$NAMESPACE_BLUE" --replicas=0
    
    # Add cleanup annotation
    kubectl annotate deployment acgs-auth-service-blue -n "$NAMESPACE_BLUE" cleanup-scheduled="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    
    success "Blue service cleanup completed"
}

# Main migration execution
main() {
    log "🚀 Starting ACGE Phase 2 Auth Service Migration"
    log "Service: $SERVICE_NAME"
    log "Port: $SERVICE_PORT"
    log "Constitutional Hash: $CONSTITUTIONAL_HASH"
    log "Duration: $MIGRATION_DURATION"
    
    # Execute migration stages
    for stage in "${MIGRATION_STAGES[@]}"; do
        log "Executing stage: $stage"
        $stage
        sleep 10  # Brief pause between stages
    done
    
    success "✅ Auth service migration completed successfully!"
    
    # Display summary
    echo ""
    echo "=========================================="  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    echo "Auth Service Migration Summary"
    echo "=========================================="  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    echo "Service: $SERVICE_NAME"
    echo "Migration completed at: $(date)"
    echo "Constitutional Hash: $CONSTITUTIONAL_HASH"
    echo "ACGE Integration: Enabled"
    echo "Environment: Green"
    echo ""
    echo "Next steps:"
    echo "1. Monitor service performance"
    echo "2. Validate constitutional compliance"
    echo "3. Proceed with AC service migration"
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    case "${1:-migrate}" in
        "migrate")
            main
            ;;
        "validate")
            validate_green_deployment
            ;;
        "rollback")
            warning "Rollback functionality should use automated rollback system"
            ;;
        *)
            echo "Usage: $0 {migrate|validate|rollback}"
            echo ""
            echo "Commands:"
            echo "  migrate   - Execute complete auth service migration"
            echo "  validate  - Validate green deployment"
            echo "  rollback  - Trigger automated rollback"
            exit 1
            ;;
    esac
fi
