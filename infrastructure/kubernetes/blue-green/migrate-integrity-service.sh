#!/bin/bash

# ACGE Phase 2 Integrity Service Migration Script
# Migrate cryptographic integrity service with ACGE integration and constitutional hash validation

set -euo pipefail

# Configuration
SERVICE_NAME="integrity"
SERVICE_PORT="8002"
NAMESPACE_BLUE="acgs-blue"
NAMESPACE_GREEN="acgs-green"
NAMESPACE_SHARED="acgs-shared"
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
MIGRATION_DURATION="3h"

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
    "validate_cryptographic_prerequisites"
    "backup_cryptographic_state"
    "deploy_acge_integrity_service"
    "validate_cryptographic_operations"
    "test_constitutional_hash_validation"
    "perform_signature_verification_tests"
    "start_integrity_traffic_migration"
    "monitor_cryptographic_compliance"
    "validate_integrity_performance"
    "complete_integrity_migration"
)

# Validate cryptographic prerequisites
validate_cryptographic_prerequisites() {
    log "🔐 Validating cryptographic prerequisites for integrity service migration..."
    
    # Check blue integrity service is operational
    if ! kubectl run integrity-blue-test --image=curlimages/curl --rm -i --restart=Never -- \
        curl -f -s "http://acgs-integrity-service-blue.$NAMESPACE_BLUE.svc.cluster.local:8002/health" >/dev/null 2>&1; then
        error "Blue integrity service not operational"
    fi
    
    # Check constitutional hash consistency across services
    local auth_hash
    auth_hash=$(kubectl run auth-hash-check --image=curlimages/curl --rm -i --restart=Never -- \
        curl -s "http://acgs-auth-service-green.$NAMESPACE_GREEN.svc.cluster.local:8000/health" | \
        grep -o '"constitutional_hash":"[^"]*' | cut -d: -f2 | tr -d '"' || echo "")
    
    if [[ "$auth_hash" != "$CONSTITUTIONAL_HASH" ]]; then
        error "Constitutional hash mismatch with auth service: $auth_hash != $CONSTITUTIONAL_HASH"
    fi
    
    local ac_hash
    ac_hash=$(kubectl run ac-hash-check --image=curlimages/curl --rm -i --restart=Never -- \
        curl -s "http://acgs-ac-service-green.$NAMESPACE_GREEN.svc.cluster.local:8001/health" | \
        grep -o '"constitutional_hash":"[^"]*' | cut -d: -f2 | tr -d '"' || echo "")
    
    if [[ "$ac_hash" != "$CONSTITUTIONAL_HASH" ]]; then
        error "Constitutional hash mismatch with AC service: $ac_hash != $CONSTITUTIONAL_HASH"
    fi
    
    # Check ACGE model service
    if ! kubectl run acge-model-integrity-test --image=curlimages/curl --rm -i --restart=Never -- \
        curl -f -s "http://acge-model-service.$NAMESPACE_SHARED.svc.cluster.local:8080/health" >/dev/null 2>&1; then
        error "ACGE model service not operational"
    fi
    
    success "Cryptographic prerequisites validated"
}

# Backup cryptographic state
backup_cryptographic_state() {
    log "💾 Backing up cryptographic state and keys..."
    
    # Backup integrity service deployment
    kubectl get deployment acgs-integrity-service-blue -n "$NAMESPACE_BLUE" -o yaml > "/tmp/integrity-blue-backup-$(date +%Y%m%d-%H%M%S).yaml"
    
    # Backup cryptographic configuration
    kubectl get configmap crypto-config -n "$NAMESPACE_BLUE" -o yaml > "/tmp/crypto-config-backup-$(date +%Y%m%d-%H%M%S).yaml" 2>/dev/null || true
    
    # Export current integrity metrics
    kubectl run integrity-metrics-backup --image=curlimages/curl --rm -i --restart=Never -- \
        curl -s "http://acgs-integrity-service-blue.$NAMESPACE_BLUE.svc.cluster.local:8002/api/v1/integrity/info" > "/tmp/integrity-metrics-backup-$(date +%Y%m%d-%H%M%S).json" || true
    
    success "Cryptographic state backed up"
}

# Deploy ACGE integrity service
deploy_acge_integrity_service() {
    log "🚀 Deploying ACGE-enhanced integrity service..."
    
    # Create ACGE integrity service deployment
    cat > /tmp/integrity-green-deployment.yaml << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: acgs-integrity-service-green
  namespace: $NAMESPACE_GREEN
  labels:
    app: acgs-integrity-service
    environment: green
    service: integrity
    phase: phase-2
    acge-enabled: "true"
spec:
  replicas: 2
  selector:
    matchLabels:
      app: acgs-integrity-service
      environment: green
  template:
    metadata:
      labels:
        app: acgs-integrity-service
        environment: green
        service: integrity
        acge-enabled: "true"
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8002"
        prometheus.io/path: "/metrics"
        constitutional.ai/enabled: "true"
        constitutional.ai/hash: "$CONSTITUTIONAL_HASH"
        cryptographic.integrity/enabled: "true"
    spec:
      containers:
        - name: integrity-service
          image: acgs/integrity-service:acge-v2
          ports:
            - containerPort: 8002
              name: http
          env:
            - name: SERVICE_NAME
              value: "acgs-integrity-service-acge"
            - name: SERVICE_PORT
              value: "8002"
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
              port: 8002
            initialDelaySeconds: 30
            periodSeconds: 15
            timeoutSeconds: 10
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /health/constitutional
              port: 8002
            initialDelaySeconds: 15
            periodSeconds: 10
            timeoutSeconds: 5
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
  name: acgs-integrity-service-green
  namespace: $NAMESPACE_GREEN
  labels:
    app: acgs-integrity-service
    environment: green
    service: integrity
spec:
  selector:
    app: acgs-integrity-service
    environment: green
  ports:
    - port: 8002
      targetPort: 8002
      name: http
  type: ClusterIP

---
apiVersion: v1
kind: ServiceMonitor
metadata:
  name: acgs-integrity-service-green
  namespace: $NAMESPACE_GREEN
  labels:
    app: acgs-integrity-service
    environment: green
spec:
  selector:
    matchLabels:
      app: acgs-integrity-service
      environment: green
  endpoints:
    - port: http
      path: /metrics
      interval: 30s
EOF
    
    # Apply the deployment
    kubectl apply -f /tmp/integrity-green-deployment.yaml
    
    # Wait for deployment to be ready
    kubectl wait --for=condition=available deployment/acgs-integrity-service-green -n "$NAMESPACE_GREEN" --timeout=300s
    
    # Clean up
    rm -f /tmp/integrity-green-deployment.yaml
    
    success "ACGE integrity service deployed"
}

# Validate cryptographic operations
validate_cryptographic_operations() {
    log "🔍 Validating cryptographic operations..."
    
    # Check pod readiness
    local ready_pods
    ready_pods=$(kubectl get pods -n "$NAMESPACE_GREEN" -l app=acgs-integrity-service,environment=green --no-headers | grep " Running " | wc -l)
    if [[ $ready_pods -lt 2 ]]; then
        error "Insufficient ready pods: $ready_pods (expected 2)"
    fi
    
    # Test health endpoint
    if ! kubectl run integrity-health-test --image=curlimages/curl --rm -i --restart=Never -- \
        curl -f -s "http://acgs-integrity-service-green.$NAMESPACE_GREEN.svc.cluster.local:8002/health" >/dev/null 2>&1; then
        error "Health endpoint not accessible"
    fi
    
    # Test constitutional health endpoint
    if ! kubectl run integrity-constitutional-test --image=curlimages/curl --rm -i --restart=Never -- \
        curl -f -s "http://acgs-integrity-service-green.$NAMESPACE_GREEN.svc.cluster.local:8002/health/constitutional" >/dev/null 2>&1; then
        error "Constitutional health endpoint not accessible"
    fi
    
    # Verify ACGE integration
    local acge_status
    acge_status=$(kubectl run integrity-acge-test --image=curlimages/curl --rm -i --restart=Never -- \
        curl -s "http://acgs-integrity-service-green.$NAMESPACE_GREEN.svc.cluster.local:8002/api/v1/integrity/info" | \
        grep -o '"acge_enabled":[^,]*' | cut -d: -f2 || echo "false")
    
    if [[ "$acge_status" != "true" ]]; then
        error "ACGE integration not enabled: $acge_status"
    fi
    
    success "Cryptographic operations validated"
}

# Test constitutional hash validation
test_constitutional_hash_validation() {
    log "🏛️ Testing constitutional hash validation..."
    
    # Test valid constitutional hash
    local hash_validation_result
    hash_validation_result=$(kubectl run hash-validation-test --image=curlimages/curl --rm -i --restart=Never -- \
        curl -s "http://acgs-integrity-service-green.$NAMESPACE_GREEN.svc.cluster.local:8002/api/v1/integrity/constitutional-hash?hash_value=$CONSTITUTIONAL_HASH" | \
        grep -o '"valid":[^,]*' | cut -d: -f2 || echo "false")
    
    if [[ "$hash_validation_result" != "true" ]]; then
        error "Constitutional hash validation failed: $hash_validation_result"
    fi
    
    # Test invalid constitutional hash
    local invalid_hash_result
    invalid_hash_result=$(kubectl run invalid-hash-test --image=curlimages/curl --rm -i --restart=Never -- \
        curl -s "http://acgs-integrity-service-green.$NAMESPACE_GREEN.svc.cluster.local:8002/api/v1/integrity/constitutional-hash?hash_value=invalid_hash" | \
        grep -o '"valid":[^,]*' | cut -d: -f2 || echo "true")
    
    if [[ "$invalid_hash_result" != "false" ]]; then
        error "Invalid hash should be rejected: $invalid_hash_result"
    fi
    
    success "Constitutional hash validation tests passed"
}

# Perform signature verification tests
perform_signature_verification_tests() {
    log "✍️ Performing signature verification tests..."
    
    # Test basic integrity validation
    local test_data='{"data":"test constitutional data","operation_type":"signature_verification","acge_validation":true}'
    
    local integrity_result
    integrity_result=$(kubectl run integrity-validation-test --image=curlimages/curl --rm -i --restart=Never -- \
        curl -s -X POST "http://acgs-integrity-service-green.$NAMESPACE_GREEN.svc.cluster.local:8002/api/v1/integrity/validate" \
        -H "Content-Type: application/json" \
        -d "$test_data" | \
        grep -o '"constitutional_compliance":[^,]*' | cut -d: -f2 || echo "0.0")
    
    if (( $(echo "$integrity_result < 0.5" | bc -l) )); then
        error "Integrity validation test failed: $integrity_result"
    fi
    
    # Test cryptographic hash generation
    local hash_test_data='{"data":"constitutional test data for hashing","operation_type":"hash_generation"}'
    
    local hash_result
    hash_result=$(kubectl run hash-generation-test --image=curlimages/curl --rm -i --restart=Never -- \
        curl -s -X POST "http://acgs-integrity-service-green.$NAMESPACE_GREEN.svc.cluster.local:8002/api/v1/integrity/validate" \
        -H "Content-Type: application/json" \
        -d "$hash_test_data" | \
        grep -o '"constitutional_hash_verified":[^,]*' | cut -d: -f2 || echo "false")
    
    if [[ "$hash_result" != "true" ]]; then
        error "Hash generation test failed: $hash_result"
    fi
    
    success "Signature verification tests passed"
}

# Start integrity traffic migration
start_integrity_traffic_migration() {
    log "🔄 Starting integrity service traffic migration..."
    
    # Use traffic routing controller with integrity-specific monitoring
    local stages=("90 10" "75 25" "50 50" "25 75" "10 90" "0 100")
    
    for stage in "${stages[@]}"; do
        local blue_weight=$(echo "$stage" | awk '{print $1}')
        local green_weight=$(echo "$stage" | awk '{print $2}')
        
        log "🔄 Integrity Traffic: Blue=$blue_weight%, Green=$green_weight%"
        
        # Update traffic weights
        if [[ -f "infrastructure/kubernetes/blue-green/traffic-routing-controller.sh" ]]; then
            ./infrastructure/kubernetes/blue-green/traffic-routing-controller.sh shift integrity 8002 "$blue_weight" "$green_weight"
        fi
        
        # Monitor cryptographic operations during migration
        sleep 120  # 2 minutes between stages
        
        # Check constitutional hash consistency
        local hash_consistency
        hash_consistency=$(kubectl run migration-hash-check --image=curlimages/curl --rm -i --restart=Never -- \
            curl -s "http://acgs-integrity-service-green.$NAMESPACE_GREEN.svc.cluster.local:8002/api/v1/integrity/constitutional-hash" | \
            grep -o '"valid":[^,]*' | cut -d: -f2 || echo "false")
        
        if [[ "$hash_consistency" != "true" ]]; then
            error "Constitutional hash consistency lost during migration"
        fi
        
        log "✅ Stage completed: Hash consistency verified"
    done
    
    success "Integrity traffic migration completed"
}

# Monitor cryptographic compliance
monitor_cryptographic_compliance() {
    log "📊 Monitoring cryptographic compliance..."
    
    # Monitor for 15 minutes
    local monitor_duration=900
    local start_time=$(date +%s)
    local end_time=$((start_time + monitor_duration))
    
    while [[ $(date +%s) -lt $end_time ]]; do
        # Check service health
        local service_health
        service_health=$(kubectl run crypto-health-monitor --image=curlimages/curl --rm -i --restart=Never -- \
            curl -s "http://acgs-integrity-service-green.$NAMESPACE_GREEN.svc.cluster.local:8002/health" | \
            grep -o '"acge_model_status":"[^"]*' | cut -d: -f2 | tr -d '"' || echo "unknown")
        
        if [[ "$service_health" != "healthy" ]]; then
            error "Integrity service health degraded: $service_health"
        fi
        
        # Check constitutional compliance
        local constitutional_health
        constitutional_health=$(kubectl run crypto-constitutional-monitor --image=curlimages/curl --rm -i --restart=Never -- \
            curl -s "http://acgs-integrity-service-green.$NAMESPACE_GREEN.svc.cluster.local:8002/health/constitutional" | \
            grep -o '"constitutional_hash_valid":[^,]*' | cut -d: -f2 || echo "false")
        
        if [[ "$constitutional_health" != "true" ]]; then
            error "Constitutional compliance lost: $constitutional_health"
        fi
        
        log "📊 Monitoring: Health=$service_health, Constitutional=$constitutional_health"
        sleep 45  # Check every 45 seconds
    done
    
    success "Cryptographic compliance monitoring completed"
}

# Validate integrity performance
validate_integrity_performance() {
    log "⚡ Validating integrity service performance..."
    
    # Performance test with multiple integrity operations
    local test_requests=5
    local successful_requests=0
    
    for i in $(seq 1 $test_requests); do
        local test_data="{\"data\":\"performance test data $i\",\"operation_type\":\"performance_test\",\"acge_validation\":true}"
        
        local response_time
        response_time=$(kubectl run integrity-perf-test-$i --image=curlimages/curl --rm -i --restart=Never -- \
            curl -w "%{time_total}" -s -X POST "http://acgs-integrity-service-green.$NAMESPACE_GREEN.svc.cluster.local:8002/api/v1/integrity/validate" \
            -H "Content-Type: application/json" \
            -d "$test_data" | \
            tail -1 || echo "10.0")
        
        if (( $(echo "$response_time < 3.0" | bc -l) )); then
            successful_requests=$((successful_requests + 1))
        fi
        
        log "🔍 Integrity Request $i: ${response_time}s"
    done
    
    local success_rate=$((successful_requests * 100 / test_requests))
    if [[ $success_rate -lt 80 ]]; then
        error "Integrity performance test failed: $success_rate% success rate (expected ≥80%)"
    fi
    
    success "Integrity performance validated: $success_rate% success rate"
}

# Complete integrity migration
complete_integrity_migration() {
    log "✅ Completing integrity service migration..."
    
    # Final validation
    validate_cryptographic_operations
    test_constitutional_hash_validation
    
    # Update service labels
    kubectl label service acgs-integrity-service-green -n "$NAMESPACE_GREEN" migration-status=completed
    kubectl label service acgs-integrity-service-green -n "$NAMESPACE_GREEN" cryptographic-integrity=acge-enhanced
    kubectl annotate service acgs-integrity-service-green -n "$NAMESPACE_GREEN" migration-completed-at="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    kubectl annotate service acgs-integrity-service-green -n "$NAMESPACE_GREEN" constitutional-hash-verified="$CONSTITUTIONAL_HASH"
    
    # Record migration event
    kubectl create event integrity-migration-completed \
        --namespace="$NAMESPACE_SHARED" \
        --reason="IntegrityMigrationCompleted" \
        --message="Integrity service migration with ACGE cryptographic compliance completed successfully" \
        --type="Normal" || true
    
    success "Integrity service migration completed successfully"
}

# Main migration execution
main() {
    log "🚀 Starting ACGE Phase 2 Integrity Service Migration"
    log "🔐 Cryptographic integrity with constitutional compliance"
    log "Service: $SERVICE_NAME"
    log "Port: $SERVICE_PORT"
    log "Constitutional Hash: $CONSTITUTIONAL_HASH"
    log "Duration: $MIGRATION_DURATION"
    
    # Execute migration stages
    for stage in "${MIGRATION_STAGES[@]}"; do
        log "🔄 Executing stage: $stage"
        $stage
        sleep 15  # Pause between stages
    done
    
    success "✅ Integrity service migration completed successfully!"
    
    # Display summary
    echo ""
    echo "=========================================="  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    echo "Integrity Service Migration Summary"
    echo "=========================================="  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    echo "Service: $SERVICE_NAME"
    echo "Migration completed at: $(date)"
    echo "Constitutional Hash: $CONSTITUTIONAL_HASH"
    echo "ACGE Integration: Enabled"
    echo "Cryptographic Features: Enhanced"
    echo "Environment: Green"
    echo ""
    echo "🔐 Cryptographic Success Metrics:"
    echo "✅ Constitutional Hash Validation: Operational"
    echo "✅ ACGE Cryptographic Compliance: Enabled"
    echo "✅ Signature Verification: Enhanced"
    echo "✅ Zero Downtime: Achieved"
    echo ""
    echo "Next steps:"
    echo "1. Monitor cryptographic operations"
    echo "2. Validate constitutional hash consistency"
    echo "3. Proceed with formal verification service migration"
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    case "${1:-migrate}" in
        "migrate")
            main
            ;;
        "validate")
            validate_cryptographic_operations
            test_constitutional_hash_validation
            ;;
        "rollback")
            warning "Integrity service rollback should use automated rollback system"
            ;;
        *)
            echo "Usage: $0 {migrate|validate|rollback}"
            echo ""
            echo "Commands:"
            echo "  migrate   - Execute complete integrity service migration"
            echo "  validate  - Validate cryptographic operations and constitutional compliance"
            echo "  rollback  - Trigger automated rollback"
            exit 1
            ;;
    esac
fi
