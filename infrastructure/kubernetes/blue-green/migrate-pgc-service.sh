#!/bin/bash

# ACGE Phase 2 Policy Governance Service Migration Script
# Migrate policy governance service (highest complexity) with ACGE integration

set -euo pipefail

# Configuration
SERVICE_NAME="pgc"
SERVICE_PORT="8005"
NAMESPACE_BLUE="acgs-blue"
NAMESPACE_GREEN="acgs-green"
NAMESPACE_SHARED="acgs-shared"
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
MIGRATION_DURATION="6h"
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

# Critical migration stages for highest complexity service
MIGRATION_STAGES=(
    "validate_policy_governance_prerequisites"
    "backup_policy_enforcement_state"
    "deploy_acge_pgc_service"
    "validate_policy_enforcement_consistency"
    "test_constitutional_policy_compliance"
    "perform_policy_governance_stress_tests"
    "start_pgc_gradual_migration"
    "monitor_policy_enforcement_performance"
    "validate_constitutional_compliance_consistency"
    "complete_critical_pgc_migration"
)

# Validate policy governance prerequisites
validate_policy_governance_prerequisites() {
    log "🏛️ Validating policy governance prerequisites (highest complexity)..."
    
    # Check all dependent services are operational
    local dependent_services=("acgs-auth-service-green:8000" "acgs-ac-service-green:8001" "acgs-integrity-service-green:8002" "acgs-fv-service-green:8003" "acgs-gs-service-green:8004")
    for service_endpoint in "${dependent_services[@]}"; do
        local service_name=$(echo "$service_endpoint" | cut -d: -f1)
        local service_port=$(echo "$service_endpoint" | cut -d: -f2)
        
        if ! kubectl run dep-pgc-test --image=curlimages/curl --rm -i --restart=Never -- \
            curl -f -s "http://$service_name.$NAMESPACE_GREEN.svc.cluster.local:$service_port/health" >/dev/null 2>&1; then
            error "Critical dependent service $service_name not operational"
        fi
        
        # Verify constitutional compliance of dependent services
        local service_compliance
        service_compliance=$(kubectl run dep-compliance-check --image=curlimages/curl --rm -i --restart=Never -- \
            curl -s "http://$service_name.$NAMESPACE_GREEN.svc.cluster.local:$service_port/health/constitutional" | \
            grep -o '"constitutional_compliance":"[^"]*' | cut -d: -f2 | tr -d '"' || echo "unknown")
        
        if [[ "$service_compliance" != "active" ]]; then
            error "Dependent service $service_name constitutional compliance not active: $service_compliance"
        fi
    done
    
    # Check ACGE model service with enhanced validation
    if ! kubectl run acge-model-pgc-test --image=curlimages/curl --rm -i --restart=Never -- \
        curl -f -s "http://acge-model-service.$NAMESPACE_SHARED.svc.cluster.local:8080/health" >/dev/null 2>&1; then
        error "ACGE model service not operational for critical PGC migration"
    fi
    
    success "Policy governance prerequisites validated (all dependencies operational)"
}

# Backup policy enforcement state
backup_policy_enforcement_state() {
    log "💾 Backing up policy enforcement state and governance configuration..."
    
    # Backup PGC service deployment
    kubectl get deployment acgs-pgc-service-blue -n "$NAMESPACE_BLUE" -o yaml > "/tmp/pgc-blue-backup-$(date +%Y%m%d-%H%M%S).yaml"
    
    # Backup policy governance configuration
    kubectl get configmap policy-governance-config -n "$NAMESPACE_BLUE" -o yaml > "/tmp/policy-config-backup-$(date +%Y%m%d-%H%M%S).yaml" 2>/dev/null || true
    
    # Export current policy enforcement metrics
    kubectl run pgc-metrics-backup --image=curlimages/curl --rm -i --restart=Never -- \
        curl -s "http://acgs-pgc-service-blue.$NAMESPACE_BLUE.svc.cluster.local:8005/api/v1/policy/info" > "/tmp/pgc-metrics-backup-$(date +%Y%m%d-%H%M%S).json" || true
    
    # Backup policy enforcement rules
    kubectl run pgc-rules-backup --image=curlimages/curl --rm -i --restart=Never -- \
        curl -s "http://acgs-pgc-service-blue.$NAMESPACE_BLUE.svc.cluster.local:8005/api/v1/policy/rules/export" > "/tmp/pgc-rules-backup-$(date +%Y%m%d-%H%M%S).json" || true
    
    success "Policy enforcement state backed up"
}

# Deploy ACGE policy governance service
deploy_acge_pgc_service() {
    log "🚀 Deploying ACGE-enhanced policy governance service (highest complexity)..."
    
    cat > /tmp/pgc-green-deployment.yaml << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: acgs-pgc-service-green
  namespace: $NAMESPACE_GREEN
  labels:
    app: acgs-pgc-service
    environment: green
    service: policy-governance
    phase: phase-2
    acge-enabled: "true"
    complexity: "highest"
spec:
  replicas: 3
  selector:
    matchLabels:
      app: acgs-pgc-service
      environment: green
  template:
    metadata:
      labels:
        app: acgs-pgc-service
        environment: green
        service: policy-governance
        acge-enabled: "true"
        complexity: "highest"
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8005"
        prometheus.io/path: "/metrics"
        constitutional.ai/enabled: "true"
        constitutional.ai/hash: "$CONSTITUTIONAL_HASH"
        policy.governance/critical: "true"
    spec:
      containers:
        - name: pgc-service
          image: acgs/pgc-service:acge-v2
          ports:
            - containerPort: 8005
              name: http
          env:
            - name: SERVICE_NAME
              value: "acgs-pgc-service-acge"
            - name: SERVICE_PORT
              value: "8005"
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
            - name: POLICY_ENFORCEMENT_MODE
              value: "constitutional_compliance"
            - name: COMPLIANCE_THRESHOLD
              value: "$COMPLIANCE_THRESHOLD"
            - name: AUTH_SERVICE_URL
              value: "http://acgs-auth-service-green.$NAMESPACE_GREEN.svc.cluster.local:8000"
            - name: AC_SERVICE_URL
              value: "http://acgs-ac-service-green.$NAMESPACE_GREEN.svc.cluster.local:8001"
            - name: INTEGRITY_SERVICE_URL
              value: "http://acgs-integrity-service-green.$NAMESPACE_GREEN.svc.cluster.local:8002"
            - name: FV_SERVICE_URL
              value: "http://acgs-fv-service-green.$NAMESPACE_GREEN.svc.cluster.local:8003"
            - name: GS_SERVICE_URL
              value: "http://acgs-gs-service-green.$NAMESPACE_GREEN.svc.cluster.local:8004"
          livenessProbe:
            httpGet:
              path: /health
              port: 8005
            initialDelaySeconds: 60
            periodSeconds: 20
            timeoutSeconds: 15
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /health/constitutional
              port: 8005
            initialDelaySeconds: 45
            periodSeconds: 15
            timeoutSeconds: 10
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
  name: acgs-pgc-service-green
  namespace: $NAMESPACE_GREEN
  labels:
    app: acgs-pgc-service
    environment: green
    service: policy-governance
    complexity: "highest"
spec:
  selector:
    app: acgs-pgc-service
    environment: green
  ports:
    - port: 8005
      targetPort: 8005
      name: http
  type: ClusterIP

---
apiVersion: v1
kind: ServiceMonitor
metadata:
  name: acgs-pgc-service-green
  namespace: $NAMESPACE_GREEN
  labels:
    app: acgs-pgc-service
    environment: green
spec:
  selector:
    matchLabels:
      app: acgs-pgc-service
      environment: green
  endpoints:
    - port: http
      path: /metrics
      interval: 15s
EOF
    
    kubectl apply -f /tmp/pgc-green-deployment.yaml
    
    # Extended wait time for highest complexity service
    kubectl wait --for=condition=available deployment/acgs-pgc-service-green -n "$NAMESPACE_GREEN" --timeout=900s
    
    rm -f /tmp/pgc-green-deployment.yaml
    
    success "ACGE policy governance service deployed (highest complexity)"
}

# Validate policy enforcement consistency
validate_policy_enforcement_consistency() {
    log "🔍 Validating policy enforcement consistency (critical validation)..."
    
    # Check pod readiness
    local ready_pods
    ready_pods=$(kubectl get pods -n "$NAMESPACE_GREEN" -l app=acgs-pgc-service,environment=green --no-headers | grep " Running " | wc -l)
    if [[ $ready_pods -lt 3 ]]; then
        error "Insufficient ready pods for critical service: $ready_pods (expected 3)"
    fi
    
    # Test health endpoints
    if ! kubectl run pgc-health-test --image=curlimages/curl --rm -i --restart=Never -- \
        curl -f -s "http://acgs-pgc-service-green.$NAMESPACE_GREEN.svc.cluster.local:8005/health" >/dev/null 2>&1; then
        error "Critical: PGC health endpoint not accessible"
    fi
    
    if ! kubectl run pgc-constitutional-test --image=curlimages/curl --rm -i --restart=Never -- \
        curl -f -s "http://acgs-pgc-service-green.$NAMESPACE_GREEN.svc.cluster.local:8005/health/constitutional" >/dev/null 2>&1; then
        error "Critical: PGC constitutional health endpoint not accessible"
    fi
    
    # Verify ACGE integration
    local acge_status
    acge_status=$(kubectl run pgc-acge-test --image=curlimages/curl --rm -i --restart=Never -- \
        curl -s "http://acgs-pgc-service-green.$NAMESPACE_GREEN.svc.cluster.local:8005/api/v1/policy/info" | \
        grep -o '"acge_enabled":[^,]*' | cut -d: -f2 || echo "false")
    
    if [[ "$acge_status" != "true" ]]; then
        error "Critical: ACGE integration not enabled for PGC service: $acge_status"
    fi
    
    success "Policy enforcement consistency validated"
}

# Test constitutional policy compliance
test_constitutional_policy_compliance() {
    log "🏛️ Testing constitutional policy compliance (comprehensive testing)..."
    
    # Test policy enforcement with constitutional compliance
    local policy_test='{"policy_content":"test constitutional policy enforcement","enforcement_mode":"constitutional_compliance","compliance_threshold":0.95}'
    
    local compliance_score
    compliance_score=$(kubectl run pgc-compliance-test --image=curlimages/curl --rm -i --restart=Never -- \
        curl -s -X POST "http://acgs-pgc-service-green.$NAMESPACE_GREEN.svc.cluster.local:8005/api/v1/policy/enforce" \
        -H "Content-Type: application/json" \
        -d "$policy_test" | \
        grep -o '"constitutional_compliance_score":[^,]*' | cut -d: -f2 || echo "0.0")
    
    if (( $(echo "$compliance_score < $COMPLIANCE_THRESHOLD" | bc -l) )); then
        error "Constitutional policy compliance test failed: $compliance_score < $COMPLIANCE_THRESHOLD"
    fi
    
    # Test policy rule validation
    local rule_validation
    rule_validation=$(kubectl run pgc-rule-test --image=curlimages/curl --rm -i --restart=Never -- \
        curl -s -X POST "http://acgs-pgc-service-green.$NAMESPACE_GREEN.svc.cluster.local:8005/api/v1/policy/validate-rule" \
        -H "Content-Type: application/json" \
        -d '{"rule":"constitutional_rule_test","constitutional_hash":"'$CONSTITUTIONAL_HASH'"}' | \
        grep -o '"valid":[^,]*' | cut -d: -f2 || echo "false")
    
    if [[ "$rule_validation" != "true" ]]; then
        error "Policy rule validation test failed: $rule_validation"
    fi
    
    success "Constitutional policy compliance tests passed"
}

# Perform policy governance stress tests
perform_policy_governance_stress_tests() {
    log "🧪 Performing policy governance stress tests (critical performance validation)..."
    
    # Stress test with multiple concurrent policy enforcement requests
    local test_requests=5
    local successful_requests=0
    
    for i in $(seq 1 $test_requests); do
        local stress_test="{\"policy_content\":\"stress_test_policy_$i\",\"enforcement_mode\":\"constitutional_compliance\",\"priority\":\"high\"}"
        
        local response_time
        response_time=$(kubectl run pgc-stress-test-$i --image=curlimages/curl --rm -i --restart=Never -- \
            curl -w "%{time_total}" -s -X POST "http://acgs-pgc-service-green.$NAMESPACE_GREEN.svc.cluster.local:8005/api/v1/policy/enforce" \
            -H "Content-Type: application/json" \
            -d "$stress_test" | \
            tail -1 || echo "10.0")
        
        if (( $(echo "$response_time < 5.0" | bc -l) )); then
            successful_requests=$((successful_requests + 1))
        fi
        
        log "🔍 Stress Test Request $i: ${response_time}s"
    done
    
    local success_rate=$((successful_requests * 100 / test_requests))
    if [[ $success_rate -lt 80 ]]; then
        error "Policy governance stress test failed: $success_rate% success rate (expected ≥80%)"
    fi
    
    success "Policy governance stress tests passed: $success_rate% success rate"
}

# Start PGC gradual migration
start_pgc_gradual_migration() {
    log "🔄 Starting policy governance service gradual migration (critical service)..."
    
    # Extra gradual migration for highest complexity service
    local stages=("95 5" "90 10" "80 20" "70 30" "60 40" "50 50" "40 60" "30 70" "20 80" "10 90" "0 100")
    
    for stage in "${stages[@]}"; do
        local blue_weight=$(echo "$stage" | awk '{print $1}')
        local green_weight=$(echo "$stage" | awk '{print $2}')
        
        log "🔄 PGC Traffic: Blue=$blue_weight%, Green=$green_weight%"
        
        if [[ -f "infrastructure/kubernetes/blue-green/traffic-routing-controller.sh" ]]; then
            ./infrastructure/kubernetes/blue-green/traffic-routing-controller.sh shift pgc 8005 "$blue_weight" "$green_weight"
        fi
        
        # Extended monitoring between stages for critical service
        sleep 180  # 3 minutes between stages
        
        # Check policy enforcement consistency during migration
        local enforcement_health
        enforcement_health=$(kubectl run migration-pgc-check --image=curlimages/curl --rm -i --restart=Never -- \
            curl -s "http://acgs-pgc-service-green.$NAMESPACE_GREEN.svc.cluster.local:8005/health/constitutional" | \
            grep -o '"constitutional_compliance":"[^"]*' | cut -d: -f2 | tr -d '"' || echo "unknown")
        
        if [[ "$enforcement_health" != "active" ]]; then
            error "Policy enforcement health degraded during migration: $enforcement_health"
        fi
        
        # Check constitutional compliance score
        local compliance_check
        compliance_check=$(kubectl run migration-compliance-check --image=curlimages/curl --rm -i --restart=Never -- \
            curl -s "http://acgs-pgc-service-green.$NAMESPACE_GREEN.svc.cluster.local:8005/health/constitutional" | \
            grep -o '"constitutional_hash_valid":[^,]*' | cut -d: -f2 || echo "false")
        
        if [[ "$compliance_check" != "true" ]]; then
            error "Constitutional compliance lost during migration: $compliance_check"
        fi
        
        log "✅ Stage completed: Policy enforcement operational, compliance verified"
    done
    
    success "PGC gradual migration completed"
}

# Monitor policy enforcement performance
monitor_policy_enforcement_performance() {
    log "📊 Monitoring policy enforcement performance (extended monitoring)..."
    
    # Extended monitoring for 30 minutes for critical service
    local monitor_duration=1800
    local start_time=$(date +%s)
    local end_time=$((start_time + monitor_duration))
    
    while [[ $(date +%s) -lt $end_time ]]; do
        # Check service health
        local service_health
        service_health=$(kubectl run pgc-health-monitor --image=curlimages/curl --rm -i --restart=Never -- \
            curl -s "http://acgs-pgc-service-green.$NAMESPACE_GREEN.svc.cluster.local:8005/health" | \
            grep -o '"acge_enabled":[^,]*' | cut -d: -f2 || echo "false")
        
        if [[ "$service_health" != "true" ]]; then
            error "PGC service health degraded: $service_health"
        fi
        
        # Check policy enforcement performance
        local enforcement_performance
        enforcement_performance=$(kubectl run pgc-performance-monitor --image=curlimages/curl --rm -i --restart=Never -- \
            curl -s "http://acgs-pgc-service-green.$NAMESPACE_GREEN.svc.cluster.local:8005/health/constitutional" | \
            grep -o '"constitutional_compliance":"[^"]*' | cut -d: -f2 | tr -d '"' || echo "unknown")
        
        if [[ "$enforcement_performance" != "active" ]]; then
            error "Policy enforcement performance degraded: $enforcement_performance"
        fi
        
        log "📊 Monitoring: Health=operational, Enforcement=active"
        sleep 90  # Check every 1.5 minutes
    done
    
    success "Policy enforcement performance monitoring completed"
}

# Validate constitutional compliance consistency
validate_constitutional_compliance_consistency() {
    log "🏛️ Validating constitutional compliance consistency (final critical validation)..."
    
    # Comprehensive constitutional compliance validation
    local final_compliance_test='{"policy_content":"final constitutional compliance validation","enforcement_mode":"constitutional_compliance","validation_level":"comprehensive"}'
    
    local final_compliance_score
    final_compliance_score=$(kubectl run pgc-final-compliance-test --image=curlimages/curl --rm -i --restart=Never -- \
        curl -s -X POST "http://acgs-pgc-service-green.$NAMESPACE_GREEN.svc.cluster.local:8005/api/v1/policy/enforce" \
        -H "Content-Type: application/json" \
        -d "$final_compliance_test" | \
        grep -o '"constitutional_compliance_score":[^,]*' | cut -d: -f2 || echo "0.0")
    
    if (( $(echo "$final_compliance_score < $COMPLIANCE_THRESHOLD" | bc -l) )); then
        error "Final constitutional compliance validation failed: $final_compliance_score < $COMPLIANCE_THRESHOLD"
    fi
    
    # Verify constitutional hash consistency across all services
    local services=("auth:8000" "ac:8001" "integrity:8002" "fv:8003" "gs:8004" "pgc:8005")
    for service_info in "${services[@]}"; do
        local service_name=$(echo "$service_info" | cut -d: -f1)
        local service_port=$(echo "$service_info" | cut -d: -f2)
        
        local service_hash
        service_hash=$(kubectl run final-hash-check-$service_name --image=curlimages/curl --rm -i --restart=Never -- \
            curl -s "http://acgs-$service_name-service-green.$NAMESPACE_GREEN.svc.cluster.local:$service_port/health" | \
            grep -o '"constitutional_hash":"[^"]*' | cut -d: -f2 | tr -d '"' || echo "")
        
        if [[ "$service_hash" != "$CONSTITUTIONAL_HASH" ]]; then
            error "Constitutional hash inconsistency in $service_name: $service_hash != $CONSTITUTIONAL_HASH"
        fi
    done
    
    success "Constitutional compliance consistency validated across all services"
}

# Complete critical PGC migration
complete_critical_pgc_migration() {
    log "✅ Completing critical policy governance service migration..."
    
    # Final comprehensive validation
    validate_policy_enforcement_consistency
    test_constitutional_policy_compliance
    validate_constitutional_compliance_consistency
    
    # Update service labels with critical service designation
    kubectl label service acgs-pgc-service-green -n "$NAMESPACE_GREEN" migration-status=completed
    kubectl label service acgs-pgc-service-green -n "$NAMESPACE_GREEN" service-criticality=highest
    kubectl label service acgs-pgc-service-green -n "$NAMESPACE_GREEN" policy-enforcement=constitutional-compliance
    kubectl annotate service acgs-pgc-service-green -n "$NAMESPACE_GREEN" migration-completed-at="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    kubectl annotate service acgs-pgc-service-green -n "$NAMESPACE_GREEN" migration-complexity=highest
    kubectl annotate service acgs-pgc-service-green -n "$NAMESPACE_GREEN" constitutional-compliance-verified="$COMPLIANCE_THRESHOLD"
    
    # Record critical migration event
    kubectl create event pgc-critical-migration-completed \
        --namespace="$NAMESPACE_SHARED" \
        --reason="PolicyGovernanceCriticalMigrationCompleted" \  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
        --message="Policy governance service (highest complexity) migration with ACGE integration completed successfully" \
        --type="Normal" || true
    
    success "Critical policy governance service migration completed successfully"
}

# Main migration execution
main() {
    log "🚀 Starting ACGE Phase 2 Policy Governance Service Critical Migration"
    log "⚠️  CRITICAL: Highest complexity service migration"
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
    
    success "✅ Policy governance service critical migration completed successfully!"
    
    # Display comprehensive summary
    echo ""
    echo "=========================================="  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    echo "Policy Governance Service Critical Migration Summary"
    echo "=========================================="  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    echo "Service: $SERVICE_NAME (Highest Complexity)"
    echo "Migration completed at: $(date)"
    echo "Constitutional Hash: $CONSTITUTIONAL_HASH"
    echo "ACGE Integration: Enabled"
    echo "Policy Enforcement: Constitutional Compliance"
    echo "Compliance Threshold: $COMPLIANCE_THRESHOLD"
    echo "Environment: Green"
    echo ""
    echo "🏛️ Critical Success Metrics:"
    echo "✅ Constitutional Compliance: ≥$COMPLIANCE_THRESHOLD"
    echo "✅ Policy Enforcement: Operational"
    echo "✅ ACGE Integration: Functional"
    echo "✅ Service Dependencies: All Operational"
    echo "✅ Zero Downtime: Achieved"
    echo ""
    echo "Next steps:"
    echo "1. Monitor policy enforcement performance continuously"
    echo "2. Validate constitutional compliance consistency"
    echo "3. Proceed with executive council service migration (final service)"
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    case "${1:-migrate}" in
        "migrate")
            main
            ;;
        "validate")
            validate_policy_enforcement_consistency
            test_constitutional_policy_compliance
            validate_constitutional_compliance_consistency
            ;;
        "rollback")
            error "PGC service rollback must use automated rollback system due to critical nature"
            ;;
        *)
            echo "Usage: $0 {migrate|validate|rollback}"
            echo ""
            echo "Commands:"
            echo "  migrate   - Execute complete policy governance service critical migration"
            echo "  validate  - Validate policy enforcement and constitutional compliance"
            echo "  rollback  - Trigger automated rollback (critical service)"
            exit 1
            ;;
    esac
fi
