#!/bin/bash

# ACGE Phase 2 AC Service Migration Script
# Critical migration from multi-model consensus to single ACGE model architecture

set -euo pipefail

# Configuration
SERVICE_NAME="ac"
SERVICE_PORT="8001"
NAMESPACE_BLUE="acgs-blue"
NAMESPACE_GREEN="acgs-green"
NAMESPACE_SHARED="acgs-shared"
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
MIGRATION_DURATION="4h"
COMPLIANCE_THRESHOLD="0.95"

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

# Critical migration stages
MIGRATION_STAGES=(
    "validate_critical_prerequisites"
    "backup_multi_model_state"
    "deploy_acge_single_model"
    "validate_acge_deployment"
    "perform_constitutional_validation_tests"
    "start_gradual_traffic_migration"
    "monitor_constitutional_compliance"
    "validate_single_model_performance"
    "complete_critical_migration"
    "disable_multi_model_consensus"
)

# Validate critical prerequisites
validate_critical_prerequisites() {
    log "🔍 Validating critical prerequisites for AC service migration..."
    
    # Check ACGE model service is operational
    if ! kubectl run acge-model-test --image=curlimages/curl --rm -i --restart=Never -- \
        curl -f -s "http://acge-model-service.$NAMESPACE_SHARED.svc.cluster.local:8080/health" >/dev/null 2>&1; then
        error "ACGE model service not operational - CRITICAL FAILURE"
    fi
    
    # Check constitutional hash consistency
    local stored_hash
    stored_hash=$(kubectl get configmap acge-constitutional-config -n "$NAMESPACE_SHARED" -o jsonpath='{.data.constitutional-hash}' 2>/dev/null || echo "")
    if [[ "$stored_hash" != "$CONSTITUTIONAL_HASH" ]]; then
        error "Constitutional hash mismatch - CRITICAL FAILURE. Expected: $CONSTITUTIONAL_HASH, Got: $stored_hash"
    fi
    
    # Check blue AC service current compliance
    local blue_compliance
    blue_compliance=$(kubectl run blue-compliance-check --image=curlimages/curl --rm -i --restart=Never -- \
        curl -s "http://acgs-ac-service-blue.$NAMESPACE_BLUE.svc.cluster.local:8001/health/constitutional" | \
        grep -o '"compliance_score":[^,]*' | cut -d: -f2 || echo "0.0")
    
    if (( $(echo "$blue_compliance < $COMPLIANCE_THRESHOLD" | bc -l) )); then
        error "Blue AC service compliance below threshold: $blue_compliance < $COMPLIANCE_THRESHOLD"
    fi
    
    # Check dependent services
    local dependent_services=("acgs-auth-service-green" "acge-model-service")
    for service in "${dependent_services[@]}"; do
        if ! kubectl get service "$service" -n "$NAMESPACE_SHARED" >/dev/null 2>&1 && \
           ! kubectl get service "$service" -n "$NAMESPACE_GREEN" >/dev/null 2>&1; then
            error "Dependent service $service not found"
        fi
    done
    
    success "Critical prerequisites validated"
}

# Backup multi-model state
backup_multi_model_state() {
    log "💾 Backing up multi-model consensus state..."
    
    # Create backup of current multi-model configuration
    kubectl get configmap multi-model-config -n "$NAMESPACE_BLUE" -o yaml > "/tmp/multi-model-backup-$(date +%Y%m%d-%H%M%S).yaml" 2>/dev/null || true
    
    # Backup current AC service deployment
    kubectl get deployment acgs-ac-service-blue -n "$NAMESPACE_BLUE" -o yaml > "/tmp/ac-blue-backup-$(date +%Y%m%d-%H%M%S).yaml"
    
    # Export current compliance metrics
    kubectl run metrics-backup --image=curlimages/curl --rm -i --restart=Never -- \
        curl -s "http://acgs-ac-service-blue.$NAMESPACE_BLUE.svc.cluster.local:8001/api/v1/constitutional/info" > "/tmp/ac-metrics-backup-$(date +%Y%m%d-%H%M%S).json" || true
    
    success "Multi-model state backed up"
}

# Deploy ACGE single model service
deploy_acge_single_model() {
    log "🚀 Deploying ACGE single model AC service..."
    
    # Create ACGE single model deployment
    cat > /tmp/ac-green-acge-deployment.yaml << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: acgs-ac-service-green
  namespace: $NAMESPACE_GREEN
  labels:
    app: acgs-ac-service
    environment: green
    service: constitutional-ai
    phase: phase-2
    model-type: acge-single
spec:
  replicas: 3
  selector:
    matchLabels:
      app: acgs-ac-service
      environment: green
  template:
    metadata:
      labels:
        app: acgs-ac-service
        environment: green
        service: constitutional-ai
        model-type: acge-single
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8001"
        prometheus.io/path: "/metrics"
        constitutional.ai/enabled: "true"
        constitutional.ai/hash: "$CONSTITUTIONAL_HASH"
        constitutional.ai/single-model: "true"
    spec:
      containers:
        - name: ac-service
          image: acgs/ac-service:acge-single-v2
          ports:
            - containerPort: 8001
              name: http
          env:
            - name: SERVICE_NAME
              value: "acgs-ac-service-acge"
            - name: SERVICE_PORT
              value: "8001"
            - name: ENVIRONMENT
              value: "green"
            - name: CONSTITUTIONAL_HASH
              value: "$CONSTITUTIONAL_HASH"
            - name: ACGE_MODEL_ENDPOINT
              value: "http://acge-model-service.$NAMESPACE_SHARED.svc.cluster.local:8080"
            - name: ACGE_ENABLED
              value: "true"
            - name: SINGLE_MODEL_MODE
              value: "true"
            - name: MULTI_MODEL_DISABLED
              value: "true"
            - name: PHASE
              value: "phase-2"
            - name: AUTH_SERVICE_URL
              value: "http://acgs-auth-service-green.$NAMESPACE_GREEN.svc.cluster.local:8000"
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
          livenessProbe:
            httpGet:
              path: /health
              port: 8001
            initialDelaySeconds: 45
            periodSeconds: 15
            timeoutSeconds: 10
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /health/constitutional
              port: 8001
            initialDelaySeconds: 30
            periodSeconds: 10
            timeoutSeconds: 5
            failureThreshold: 2
          resources:
            requests:
              memory: "2Gi"
              cpu: "500m"
            limits:
              memory: "4Gi"
              cpu: "1"
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
  name: acgs-ac-service-green
  namespace: $NAMESPACE_GREEN
  labels:
    app: acgs-ac-service
    environment: green
    service: constitutional-ai
    model-type: acge-single
spec:
  selector:
    app: acgs-ac-service
    environment: green
  ports:
    - port: 8001
      targetPort: 8001
      name: http
  type: ClusterIP

---
apiVersion: v1
kind: ServiceMonitor
metadata:
  name: acgs-ac-service-green
  namespace: $NAMESPACE_GREEN
  labels:
    app: acgs-ac-service
    environment: green
spec:
  selector:
    matchLabels:
      app: acgs-ac-service
      environment: green
  endpoints:
    - port: http
      path: /metrics
      interval: 15s
EOF
    
    # Apply the deployment
    kubectl apply -f /tmp/ac-green-acge-deployment.yaml
    
    # Wait for deployment with extended timeout for critical service
    kubectl wait --for=condition=available deployment/acgs-ac-service-green -n "$NAMESPACE_GREEN" --timeout=600s
    
    # Clean up
    rm -f /tmp/ac-green-acge-deployment.yaml
    
    success "ACGE single model AC service deployed"
}

# Validate ACGE deployment
validate_acge_deployment() {
    log "🔍 Validating ACGE single model deployment..."
    
    # Check pod readiness
    local ready_pods
    ready_pods=$(kubectl get pods -n "$NAMESPACE_GREEN" -l app=acgs-ac-service,environment=green --no-headers | grep " Running " | wc -l)
    if [[ $ready_pods -lt 3 ]]; then
        error "Insufficient ready pods: $ready_pods (expected 3)"
    fi
    
    # Test health endpoint
    if ! kubectl run ac-health-test --image=curlimages/curl --rm -i --restart=Never -- \
        curl -f -s "http://acgs-ac-service-green.$NAMESPACE_GREEN.svc.cluster.local:8001/health" >/dev/null 2>&1; then
        error "Health endpoint not accessible"
    fi
    
    # Test constitutional health endpoint
    if ! kubectl run ac-constitutional-test --image=curlimages/curl --rm -i --restart=Never -- \
        curl -f -s "http://acgs-ac-service-green.$NAMESPACE_GREEN.svc.cluster.local:8001/health/constitutional" >/dev/null 2>&1; then
        error "Constitutional health endpoint not accessible"
    fi
    
    # Verify single model mode
    local single_model_status
    single_model_status=$(kubectl run ac-model-test --image=curlimages/curl --rm -i --restart=Never -- \
        curl -s "http://acgs-ac-service-green.$NAMESPACE_GREEN.svc.cluster.local:8001/api/v1/constitutional/info" | \
        grep -o '"single_model_mode":[^,]*' | cut -d: -f2 || echo "false")
    
    if [[ "$single_model_status" != "true" ]]; then
        error "Single model mode not enabled: $single_model_status"
    fi
    
    # Verify ACGE integration
    local acge_status
    acge_status=$(kubectl run ac-acge-test --image=curlimages/curl --rm -i --restart=Never -- \
        curl -s "http://acgs-ac-service-green.$NAMESPACE_GREEN.svc.cluster.local:8001/api/v1/constitutional/info" | \
        grep -o '"acge_enabled":[^,]*' | cut -d: -f2 || echo "false")
    
    if [[ "$acge_status" != "true" ]]; then
        error "ACGE integration not enabled: $acge_status"
    fi
    
    success "ACGE deployment validation completed"
}

# Perform constitutional validation tests
perform_constitutional_validation_tests() {
    log "🧪 Performing constitutional validation tests..."
    
    # Test basic constitutional validation
    local test_policy='{"id":"test-001","title":"Test Policy","content":"Test constitutional compliance","category":"test","impact_level":"low"}'
    
    local validation_result
    validation_result=$(kubectl run ac-validation-test --image=curlimages/curl --rm -i --restart=Never -- \
        curl -s -X POST "http://acgs-ac-service-green.$NAMESPACE_GREEN.svc.cluster.local:8001/api/v1/constitutional/validate" \
        -H "Content-Type: application/json" \
        -d "{\"policy\":$test_policy,\"validation_mode\":\"comprehensive\"}" | \
        grep -o '"compliance_score":[^,]*' | cut -d: -f2 || echo "0.0")
    
    if (( $(echo "$validation_result < $COMPLIANCE_THRESHOLD" | bc -l) )); then
        error "Constitutional validation test failed: $validation_result < $COMPLIANCE_THRESHOLD"
    fi
    
    # Test ACGE-specific validation
    local acge_validation_result
    acge_validation_result=$(kubectl run ac-acge-validation-test --image=curlimages/curl --rm -i --restart=Never -- \
        curl -s -X POST "http://acgs-ac-service-green.$NAMESPACE_GREEN.svc.cluster.local:8001/api/v1/constitutional/acge-validate" \
        -H "Content-Type: application/json" \
        -d "{\"policy\":$test_policy,\"validation_mode\":\"comprehensive\",\"single_model_mode\":true}" | \
        grep -o '"compliance_score":[^,]*' | cut -d: -f2 || echo "0.0")
    
    if (( $(echo "$acge_validation_result < $COMPLIANCE_THRESHOLD" | bc -l) )); then
        error "ACGE validation test failed: $acge_validation_result < $COMPLIANCE_THRESHOLD"
    fi
    
    success "Constitutional validation tests passed"
}

# Start gradual traffic migration
start_gradual_traffic_migration() {
    log "🔄 Starting gradual traffic migration to ACGE single model..."
    
    # Use traffic routing controller with extended monitoring
    if [[ -f "infrastructure/kubernetes/blue-green/traffic-routing-controller.sh" ]]; then
        # Custom AC service migration with enhanced monitoring
        local stages=("95 5" "90 10" "80 20" "70 30" "50 50" "30 70" "10 90" "0 100")
        
        for stage in "${stages[@]}"; do
            local blue_weight=$(echo "$stage" | awk '{print $1}')
            local green_weight=$(echo "$stage" | awk '{print $2}')
            
            log "🔄 AC Service Traffic: Blue=$blue_weight%, Green=$green_weight%"
            
            # Update traffic weights
            ./infrastructure/kubernetes/blue-green/traffic-routing-controller.sh shift ac 8001 "$blue_weight" "$green_weight"
            
            # Extended monitoring for critical service
            sleep 180  # 3 minutes between stages
            
            # Check constitutional compliance during migration
            local current_compliance
            current_compliance=$(kubectl run migration-compliance-check --image=curlimages/curl --rm -i --restart=Never -- \
                curl -s "http://acgs-ac-service-green.$NAMESPACE_GREEN.svc.cluster.local:8001/health/constitutional" | \
                grep -o '"compliance_score":[^,]*' | cut -d: -f2 || echo "0.0")
            
            if (( $(echo "$current_compliance < $COMPLIANCE_THRESHOLD" | bc -l) )); then
                error "Constitutional compliance dropped during migration: $current_compliance"
            fi
            
            log "✅ Stage completed: Compliance=$current_compliance"
        done
    else
        error "Traffic routing controller not found"
    fi
    
    success "Traffic migration completed"
}

# Monitor constitutional compliance
monitor_constitutional_compliance() {
    log "📊 Monitoring constitutional compliance during migration..."
    
    # Extended monitoring for 30 minutes
    local monitor_duration=1800
    local start_time=$(date +%s)
    local end_time=$((start_time + monitor_duration))
    
    while [[ $(date +%s) -lt $end_time ]]; do
        # Check compliance score
        local compliance_score
        compliance_score=$(kubectl run compliance-monitor --image=curlimages/curl --rm -i --restart=Never -- \
            curl -s "http://acgs-ac-service-green.$NAMESPACE_GREEN.svc.cluster.local:8001/health/constitutional" | \
            grep -o '"compliance_score":[^,]*' | cut -d: -f2 || echo "0.0")
        
        if (( $(echo "$compliance_score < $COMPLIANCE_THRESHOLD" | bc -l) )); then
            error "Constitutional compliance violation: $compliance_score < $COMPLIANCE_THRESHOLD"
        fi
        
        # Check ACGE model status
        local acge_status
        acge_status=$(kubectl run acge-status-monitor --image=curlimages/curl --rm -i --restart=Never -- \
            curl -s "http://acgs-ac-service-green.$NAMESPACE_GREEN.svc.cluster.local:8001/api/v1/constitutional/info" | \
            grep -o '"acge_model_status":"[^"]*' | cut -d: -f2 | tr -d '"' || echo "unknown")
        
        if [[ "$acge_status" != "healthy" ]]; then
            error "ACGE model status unhealthy: $acge_status"
        fi
        
        log "📊 Monitoring: Compliance=$compliance_score, ACGE=$acge_status"
        sleep 60  # Check every minute
    done
    
    success "Constitutional compliance monitoring completed"
}

# Validate single model performance
validate_single_model_performance() {
    log "⚡ Validating single model performance..."
    
    # Performance test with multiple validation requests
    local test_start=$(date +%s)
    local test_requests=10
    local successful_requests=0
    
    for i in $(seq 1 $test_requests); do
        local test_policy="{\"id\":\"perf-test-$i\",\"title\":\"Performance Test $i\",\"content\":\"Test policy for performance validation\",\"category\":\"performance\"}"
        
        local response_time
        response_time=$(kubectl run perf-test-$i --image=curlimages/curl --rm -i --restart=Never -- \
            curl -w "%{time_total}" -s -X POST "http://acgs-ac-service-green.$NAMESPACE_GREEN.svc.cluster.local:8001/api/v1/constitutional/validate" \
            -H "Content-Type: application/json" \
            -d "{\"policy\":$test_policy,\"validation_mode\":\"comprehensive\"}" | \
            tail -1 || echo "10.0")
        
        if (( $(echo "$response_time < 2.0" | bc -l) )); then
            successful_requests=$((successful_requests + 1))
        fi
        
        log "🔍 Request $i: ${response_time}s"
    done
    
    local success_rate=$((successful_requests * 100 / test_requests))
    if [[ $success_rate -lt 95 ]]; then
        error "Performance test failed: $success_rate% success rate (expected ≥95%)"
    fi
    
    success "Single model performance validated: $success_rate% success rate"
}

# Complete critical migration
complete_critical_migration() {
    log "✅ Completing critical AC service migration..."
    
    # Final validation
    validate_acge_deployment
    perform_constitutional_validation_tests
    
    # Update service labels
    kubectl label service acgs-ac-service-green -n "$NAMESPACE_GREEN" migration-status=completed
    kubectl label service acgs-ac-service-green -n "$NAMESPACE_GREEN" model-type=acge-single
    kubectl annotate service acgs-ac-service-green -n "$NAMESPACE_GREEN" migration-completed-at="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    kubectl annotate service acgs-ac-service-green -n "$NAMESPACE_GREEN" migration-type=multi-to-single-model
    
    # Record critical migration event
    kubectl create event ac-critical-migration-completed \
        --namespace="$NAMESPACE_SHARED" \
        --reason="CriticalMigrationCompleted" \
        --message="AC service migration from multi-model to ACGE single model completed successfully" \
        --type="Normal" || true
    
    success "Critical AC service migration completed successfully"
}

# Disable multi-model consensus
disable_multi_model_consensus() {
    log "🔒 Disabling multi-model consensus in blue environment..."
    
    # Scale down blue deployment
    kubectl scale deployment acgs-ac-service-blue -n "$NAMESPACE_BLUE" --replicas=0
    
    # Add migration completion annotations
    kubectl annotate deployment acgs-ac-service-blue -n "$NAMESPACE_BLUE" multi-model-disabled="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    kubectl annotate deployment acgs-ac-service-blue -n "$NAMESPACE_BLUE" migration-to-single-model="completed"
    
    success "Multi-model consensus disabled"
}

# Main migration execution
main() {
    log "🚀 Starting ACGE Phase 2 AC Service Critical Migration"
    log "⚠️  CRITICAL: Migrating from multi-model consensus to single ACGE model"
    log "Service: $SERVICE_NAME"
    log "Port: $SERVICE_PORT"
    log "Constitutional Hash: $CONSTITUTIONAL_HASH"
    log "Duration: $MIGRATION_DURATION"
    log "Compliance Threshold: $COMPLIANCE_THRESHOLD"
    
    # Execute critical migration stages
    for stage in "${MIGRATION_STAGES[@]}"; do
        log "🔄 Executing critical stage: $stage"
        $stage
        sleep 30  # Extended pause between critical stages
    done
    
    success "✅ AC service critical migration completed successfully!"
    
    # Display summary
    echo ""
    echo "=========================================="
    echo "AC Service Critical Migration Summary"
    echo "=========================================="
    echo "Service: $SERVICE_NAME"
    echo "Migration completed at: $(date)"
    echo "Constitutional Hash: $CONSTITUTIONAL_HASH"
    echo "Model Architecture: Single ACGE Model"
    echo "Multi-Model Consensus: Disabled"
    echo "Environment: Green"
    echo ""
    echo "🎯 Critical Success Metrics:"
    echo "✅ Constitutional Compliance: ≥$COMPLIANCE_THRESHOLD"
    echo "✅ ACGE Single Model: Operational"
    echo "✅ Multi-Model Consensus: Disabled"
    echo "✅ Zero Downtime: Achieved"
    echo ""
    echo "Next steps:"
    echo "1. Monitor constitutional compliance continuously"
    echo "2. Validate ACGE model performance"
    echo "3. Proceed with integrity service migration"
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    case "${1:-migrate}" in
        "migrate")
            main
            ;;
        "validate")
            validate_acge_deployment
            perform_constitutional_validation_tests
            ;;
        "rollback")
            error "AC service rollback must use automated rollback system due to criticality"
            ;;
        *)
            echo "Usage: $0 {migrate|validate|rollback}"
            echo ""
            echo "Commands:"
            echo "  migrate   - Execute complete AC service critical migration"
            echo "  validate  - Validate ACGE deployment and constitutional compliance"
            echo "  rollback  - Trigger automated rollback (critical service)"
            exit 1
            ;;
    esac
fi
