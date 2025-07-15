#!/bin/bash

# ACGE Phase 2 Governance Synthesis Service Migration Script
# Migrate governance synthesis service with ACGE integration and constitutional principles

set -euo pipefail

# Configuration
SERVICE_NAME="gs"
SERVICE_PORT="8004"
NAMESPACE_BLUE="acgs-blue"
NAMESPACE_GREEN="acgs-green"
NAMESPACE_SHARED="acgs-shared"
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
MIGRATION_DURATION="4h"

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
    "validate_governance_prerequisites"
    "deploy_acge_gs_service"
    "validate_governance_synthesis"
    "test_constitutional_governance"
    "start_gs_traffic_migration"
    "monitor_governance_performance"
    "complete_gs_migration"
)

# Validate governance prerequisites
validate_governance_prerequisites() {
    log "🏛️ Validating governance synthesis prerequisites..."
    
    # Check dependent services
    local dependent_services=("acgs-auth-service-green:8000" "acgs-ac-service-green:8001" "acgs-integrity-service-green:8002" "acgs-fv-service-green:8003")
    for service_endpoint in "${dependent_services[@]}"; do
        local service_name=$(echo "$service_endpoint" | cut -d: -f1)
        local service_port=$(echo "$service_endpoint" | cut -d: -f2)
        
        if ! kubectl run dep-gs-test --image=curlimages/curl --rm -i --restart=Never -- \
            curl -f -s "http://$service_name.$NAMESPACE_GREEN.svc.cluster.local:$service_port/health" >/dev/null 2>&1; then
            error "Dependent service $service_name not operational"
        fi
    done
    
    success "Governance synthesis prerequisites validated"
}

# Deploy ACGE governance synthesis service
deploy_acge_gs_service() {
    log "🚀 Deploying ACGE-enhanced governance synthesis service..."
    
    cat > /tmp/gs-green-deployment.yaml << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: acgs-gs-service-green
  namespace: $NAMESPACE_GREEN
  labels:
    app: acgs-gs-service
    environment: green
    service: governance-synthesis
    phase: phase-2
    acge-enabled: "true"
spec:
  replicas: 2
  selector:
    matchLabels:
      app: acgs-gs-service
      environment: green
  template:
    metadata:
      labels:
        app: acgs-gs-service
        environment: green
        service: governance-synthesis
        acge-enabled: "true"
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8004"
        prometheus.io/path: "/metrics"
        constitutional.ai/enabled: "true"
        constitutional.ai/hash: "$CONSTITUTIONAL_HASH"
    spec:
      containers:
        - name: gs-service
          image: acgs/gs-service:acge-v2
          ports:
            - containerPort: 8004
              name: http
          env:
            - name: SERVICE_NAME
              value: "acgs-gs-service-acge"
            - name: SERVICE_PORT
              value: "8004"
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
            - name: AUTH_SERVICE_URL
              value: "http://acgs-auth-service-green.$NAMESPACE_GREEN.svc.cluster.local:8000"
            - name: AC_SERVICE_URL
              value: "http://acgs-ac-service-green.$NAMESPACE_GREEN.svc.cluster.local:8001"
            - name: INTEGRITY_SERVICE_URL
              value: "http://acgs-integrity-service-green.$NAMESPACE_GREEN.svc.cluster.local:8002"
            - name: FV_SERVICE_URL
              value: "http://acgs-fv-service-green.$NAMESPACE_GREEN.svc.cluster.local:8003"
          livenessProbe:
            httpGet:
              path: /health
              port: 8004
            initialDelaySeconds: 30
            periodSeconds: 15
          readinessProbe:
            httpGet:
              path: /health/constitutional
              port: 8004
            initialDelaySeconds: 15
            periodSeconds: 10
          resources:
            requests:
              memory: "1Gi"
              cpu: "300m"
            limits:
              memory: "2Gi"
              cpu: "800m"

---
apiVersion: v1
kind: Service
metadata:
  name: acgs-gs-service-green
  namespace: $NAMESPACE_GREEN
  labels:
    app: acgs-gs-service
    environment: green
    service: governance-synthesis
spec:
  selector:
    app: acgs-gs-service
    environment: green
  ports:
    - port: 8004
      targetPort: 8004
      name: http
  type: ClusterIP
EOF
    
    kubectl apply -f /tmp/gs-green-deployment.yaml
    kubectl wait --for=condition=available deployment/acgs-gs-service-green -n "$NAMESPACE_GREEN" --timeout=300s
    rm -f /tmp/gs-green-deployment.yaml
    
    success "ACGE governance synthesis service deployed"
}

# Validate governance synthesis
validate_governance_synthesis() {
    log "🔍 Validating governance synthesis capabilities..."
    
    # Check pod readiness
    local ready_pods
    ready_pods=$(kubectl get pods -n "$NAMESPACE_GREEN" -l app=acgs-gs-service,environment=green --no-headers | grep " Running " | wc -l)
    if [[ $ready_pods -lt 2 ]]; then
        error "Insufficient ready pods: $ready_pods (expected 2)"
    fi
    
    # Test health endpoints
    if ! kubectl run gs-health-test --image=curlimages/curl --rm -i --restart=Never -- \
        curl -f -s "http://acgs-gs-service-green.$NAMESPACE_GREEN.svc.cluster.local:8004/health" >/dev/null 2>&1; then
        error "Health endpoint not accessible"
    fi
    
    if ! kubectl run gs-constitutional-test --image=curlimages/curl --rm -i --restart=Never -- \
        curl -f -s "http://acgs-gs-service-green.$NAMESPACE_GREEN.svc.cluster.local:8004/health/constitutional" >/dev/null 2>&1; then
        error "Constitutional health endpoint not accessible"
    fi
    
    success "Governance synthesis validation completed"
}

# Test constitutional governance
test_constitutional_governance() {
    log "🏛️ Testing constitutional governance capabilities..."
    
    # Test governance synthesis with constitutional principles
    local governance_test='{"governance_request":"test constitutional governance","principles":["constitutional_principle_1"],"synthesis_mode":"constitutional"}'
    
    local synthesis_result
    synthesis_result=$(kubectl run gs-synthesis-test --image=curlimages/curl --rm -i --restart=Never -- \
        curl -s -X POST "http://acgs-gs-service-green.$NAMESPACE_GREEN.svc.cluster.local:8004/api/v1/governance/synthesize" \
        -H "Content-Type: application/json" \
        -d "$governance_test" | \
        grep -o '"constitutional_compliance":[^,]*' | cut -d: -f2 || echo "0.0")
    
    if (( $(echo "$synthesis_result < 0.5" | bc -l) )); then
        error "Constitutional governance test failed: $synthesis_result"
    fi
    
    success "Constitutional governance tests passed"
}

# Start GS traffic migration
start_gs_traffic_migration() {
    log "🔄 Starting governance synthesis service traffic migration..."
    
    local stages=("90 10" "70 30" "50 50" "30 70" "10 90" "0 100")
    
    for stage in "${stages[@]}"; do
        local blue_weight=$(echo "$stage" | awk '{print $1}')
        local green_weight=$(echo "$stage" | awk '{print $2}')
        
        log "🔄 GS Traffic: Blue=$blue_weight%, Green=$green_weight%"
        
        if [[ -f "infrastructure/kubernetes/blue-green/traffic-routing-controller.sh" ]]; then
            ./infrastructure/kubernetes/blue-green/traffic-routing-controller.sh shift gs 8004 "$blue_weight" "$green_weight"
        fi
        
        sleep 120
        
        # Check governance synthesis performance
        local governance_health
        governance_health=$(kubectl run migration-gs-check --image=curlimages/curl --rm -i --restart=Never -- \
            curl -s "http://acgs-gs-service-green.$NAMESPACE_GREEN.svc.cluster.local:8004/health/constitutional" | \
            grep -o '"constitutional_compliance":"[^"]*' | cut -d: -f2 | tr -d '"' || echo "unknown")
        
        if [[ "$governance_health" != "active" ]]; then
            error "Governance synthesis health degraded during migration: $governance_health"
        fi
        
        log "✅ Stage completed: Governance synthesis operational"
    done
    
    success "GS traffic migration completed"
}

# Monitor governance performance
monitor_governance_performance() {
    log "📊 Monitoring governance synthesis performance..."
    
    # Monitor for 15 minutes
    local monitor_duration=900
    local start_time=$(date +%s)
    local end_time=$((start_time + monitor_duration))
    
    while [[ $(date +%s) -lt $end_time ]]; do
        # Check service health
        local service_health
        service_health=$(kubectl run gs-health-monitor --image=curlimages/curl --rm -i --restart=Never -- \
            curl -s "http://acgs-gs-service-green.$NAMESPACE_GREEN.svc.cluster.local:8004/health" | \
            grep -o '"acge_enabled":[^,]*' | cut -d: -f2 || echo "false")
        
        if [[ "$service_health" != "true" ]]; then
            error "GS service health degraded: $service_health"
        fi
        
        log "📊 Monitoring: GS Health=operational"
        sleep 60
    done
    
    success "Governance synthesis performance monitoring completed"
}

# Complete GS migration
complete_gs_migration() {
    log "✅ Completing governance synthesis service migration..."
    
    # Final validation
    validate_governance_synthesis
    test_constitutional_governance
    
    # Update service labels
    kubectl label service acgs-gs-service-green -n "$NAMESPACE_GREEN" migration-status=completed
    kubectl annotate service acgs-gs-service-green -n "$NAMESPACE_GREEN" migration-completed-at="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    
    # Record migration event
    kubectl create event gs-migration-completed \
        --namespace="$NAMESPACE_SHARED" \
        --reason="GovernanceSynthesisMigrationCompleted" \
        --message="Governance synthesis service migration with ACGE integration completed successfully" \
        --type="Normal" || true
    
    success "Governance synthesis service migration completed successfully"
}

# Main migration execution
main() {
    log "🚀 Starting ACGE Phase 2 Governance Synthesis Service Migration"
    log "Service: $SERVICE_NAME"
    log "Port: $SERVICE_PORT"
    log "Constitutional Hash: $CONSTITUTIONAL_HASH"
    log "Duration: $MIGRATION_DURATION"
    
    # Execute migration stages
    for stage in "${MIGRATION_STAGES[@]}"; do
        log "🔄 Executing stage: $stage"
        $stage
        sleep 15
    done
    
    success "✅ Governance synthesis service migration completed successfully!"
    
    echo ""
    echo "=========================================="  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    echo "Governance Synthesis Service Migration Summary"
    echo "=========================================="  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    echo "Service: $SERVICE_NAME"
    echo "Migration completed at: $(date)"
    echo "Constitutional Hash: $CONSTITUTIONAL_HASH"
    echo "ACGE Integration: Enabled"
    echo "Environment: Green"
    echo ""
    echo "Next steps:"
    echo "1. Monitor governance synthesis performance"
    echo "2. Proceed with policy governance service migration"
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    case "${1:-migrate}" in
        "migrate")
            main
            ;;
        "validate")
            validate_governance_synthesis
            test_constitutional_governance
            ;;
        *)
            echo "Usage: $0 {migrate|validate}"
            exit 1
            ;;
    esac
fi
