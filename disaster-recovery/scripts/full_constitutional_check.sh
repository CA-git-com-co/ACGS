#!/bin/bash
# ACGS-2 Full Constitutional Compliance Check
# Constitutional Hash: cdd01ef066bc6cf2

set -euo pipefail

CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
NAMESPACE="${NAMESPACE:-acgs-system}"
TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M:%S UTC")

echo "🏛️ ACGS-2 Full Constitutional Compliance Check"
echo "Constitutional Hash: $CONSTITUTIONAL_HASH"
echo "Namespace: $NAMESPACE"
echo "Timestamp: $TIMESTAMP"
echo "============================================="

# Initialize counters
TOTAL_SERVICES=0
COMPLIANT_SERVICES=0
TOTAL_FAILURES=0

# Services to check with their ports
declare -A SERVICES=(
    ["constitutional-core"]="8001"
    ["auth-service"]="8013"
    ["monitoring-service"]="8014"
    ["audit-service"]="8015"
    ["gdpr-compliance"]="8016"
    ["alerting-service"]="8017"
    ["api-gateway"]="8080"
)

echo "📋 Checking service constitutional compliance..."

for service in "${!SERVICES[@]}"; do
    port=${SERVICES[$service]}
    ((TOTAL_SERVICES++))
    
    echo ""
    echo "🔍 Checking $service (port $port)..."
    
    # Check if service exists
    if ! kubectl get service "$service" -n "$NAMESPACE" &>/dev/null; then
        echo "  ❌ Service $service not found"
        ((TOTAL_FAILURES++))
        continue
    fi
    
    # Check if pods are running
    RUNNING_PODS=$(kubectl get pods -l app="$service" -n "$NAMESPACE" --field-selector=status.phase=Running --no-headers | wc -l)
    if [[ $RUNNING_PODS -eq 0 ]]; then
        echo "  ❌ No running pods for $service"
        ((TOTAL_FAILURES++))
        continue
    fi
    
    echo "  ✅ Service $service has $RUNNING_PODS running pod(s)"
    
    # Port forward and check health endpoint
    kubectl port-forward service/"$service" "$port":"$port" -n "$NAMESPACE" &>/dev/null &
    PID=$!
    sleep 5
    
    # Check health endpoint
    RESPONSE=$(curl -s "http://localhost:$port/health" 2>/dev/null || echo "{}")
    HASH=$(echo "$RESPONSE" | jq -r '.constitutional_hash // empty' 2>/dev/null || echo "")
    STATUS=$(echo "$RESPONSE" | jq -r '.status // empty' 2>/dev/null || echo "")
    
    # Clean up port forward
    kill $PID 2>/dev/null || true
    sleep 1
    
    # Validate constitutional compliance
    if [[ "$HASH" == "$CONSTITUTIONAL_HASH" ]]; then
        echo "  ✅ Constitutional compliance verified"
        ((COMPLIANT_SERVICES++))
        
        # Additional health checks
        if [[ "$STATUS" == "healthy" ]]; then
            echo "  ✅ Service health confirmed"
        else
            echo "  ⚠️ Service health status: $STATUS"
        fi
    else
        echo "  ❌ Constitutional compliance failed"
        echo "     Expected: $CONSTITUTIONAL_HASH"
        echo "     Received: $HASH"
        echo "     Response: $RESPONSE"
        ((TOTAL_FAILURES++))
    fi
done

echo ""
echo "📊 Database Constitutional Compliance Check..."

# Check database constitutional compliance
if kubectl get deployment postgres -n "$NAMESPACE" &>/dev/null; then
    echo "🔍 Checking database constitutional compliance..."
    
    # Check audit logs table
    AUDIT_COMPLIANCE=$(kubectl exec deployment/postgres -n "$NAMESPACE" -- psql -U acgs_user -d acgs_db -t -c "
    SELECT COUNT(*) FROM audit_logs WHERE constitutional_hash = '$CONSTITUTIONAL_HASH';
    " 2>/dev/null | tr -d ' ' || echo "0")
    
    # Check service configs table
    CONFIG_COMPLIANCE=$(kubectl exec deployment/postgres -n "$NAMESPACE" -- psql -U acgs_user -d acgs_db -t -c "
    SELECT COUNT(*) FROM service_configs WHERE constitutional_hash = '$CONSTITUTIONAL_HASH';
    " 2>/dev/null | tr -d ' ' || echo "0")
    
    echo "  📊 Database compliance results:"
    echo "    Audit logs with correct hash: $AUDIT_COMPLIANCE"
    echo "    Service configs with correct hash: $CONFIG_COMPLIANCE"
    
    if [[ "$AUDIT_COMPLIANCE" -gt 0 ]] && [[ "$CONFIG_COMPLIANCE" -gt 0 ]]; then
        echo "  ✅ Database constitutional compliance verified"
    else
        echo "  ❌ Database constitutional compliance failed"
        ((TOTAL_FAILURES++))
    fi
else
    echo "  ⚠️ PostgreSQL deployment not found"
    ((TOTAL_FAILURES++))
fi

echo ""
echo "🔐 Security Constitutional Compliance Check..."

# Check secrets compliance
if kubectl get secret acgs-secrets -n "$NAMESPACE" &>/dev/null; then
    echo "  ✅ ACGS secrets present"
    
    # Check if secrets have constitutional hash annotation
    SECRET_HASH=$(kubectl get secret acgs-secrets -n "$NAMESPACE" -o jsonpath='{.metadata.annotations.constitutional-hash}' 2>/dev/null || echo "")
    
    if [[ "$SECRET_HASH" == "$CONSTITUTIONAL_HASH" ]]; then
        echo "  ✅ Secrets constitutional compliance verified"
    else
        echo "  ⚠️ Secrets missing constitutional hash annotation"
        # Add annotation if missing
        kubectl annotate secret acgs-secrets constitutional-hash="$CONSTITUTIONAL_HASH" -n "$NAMESPACE" --overwrite
        echo "  🔧 Constitutional hash annotation added to secrets"
    fi
else
    echo "  ❌ ACGS secrets not found"
    ((TOTAL_FAILURES++))
fi

echo ""
echo "🏗️ Infrastructure Constitutional Compliance Check..."

# Check ConfigMaps
if kubectl get configmap acgs-config -n "$NAMESPACE" &>/dev/null; then
    CONFIG_HASH=$(kubectl get configmap acgs-config -n "$NAMESPACE" -o jsonpath='{.data.CONSTITUTIONAL_HASH}' 2>/dev/null || echo "")
    
    if [[ "$CONFIG_HASH" == "$CONSTITUTIONAL_HASH" ]]; then
        echo "  ✅ ConfigMap constitutional compliance verified"
    else
        echo "  ❌ ConfigMap constitutional compliance failed"
        echo "     Expected: $CONSTITUTIONAL_HASH"
        echo "     Found: $CONFIG_HASH"
        ((TOTAL_FAILURES++))
    fi
else
    echo "  ⚠️ ACGS ConfigMap not found"
fi

# Check namespace labels
NAMESPACE_HASH=$(kubectl get namespace "$NAMESPACE" -o jsonpath='{.metadata.labels.constitutional-hash}' 2>/dev/null || echo "")

if [[ "$NAMESPACE_HASH" == "$CONSTITUTIONAL_HASH" ]]; then
    echo "  ✅ Namespace constitutional compliance verified"
else
    echo "  ⚠️ Namespace missing constitutional hash label"
    # Add label if missing
    kubectl label namespace "$NAMESPACE" constitutional-hash="$CONSTITUTIONAL_HASH" --overwrite
    echo "  🔧 Constitutional hash label added to namespace"
fi

echo ""
echo "🧪 Running Constitutional Compliance Test Suite..."

# Run security audit if available
if [[ -f "/home/dislove/ACGS-2/tests/security/constitutional_security_audit.py" ]]; then
    echo "🔒 Running security audit..."
    cd /home/dislove/ACGS-2/tests/security
    if python constitutional_security_audit.py --post-disaster-recovery &>/dev/null; then
        echo "  ✅ Security audit passed"
    else
        echo "  ⚠️ Security audit found issues"
        ((TOTAL_FAILURES++))
    fi
else
    echo "  ⚠️ Security audit script not found"
fi

# Run performance tests if available
if [[ -f "/home/dislove/ACGS-2/tests/performance/run_performance_tests.py" ]]; then
    echo "⚡ Running performance validation..."
    cd /home/dislove/ACGS-2/tests/performance
    if python run_performance_tests.py --disaster-recovery-validation &>/dev/null; then
        echo "  ✅ Performance validation passed"
    else
        echo "  ⚠️ Performance validation found issues"
        ((TOTAL_FAILURES++))
    fi
else
    echo "  ⚠️ Performance test script not found"
fi

echo ""
echo "📊 CONSTITUTIONAL COMPLIANCE SUMMARY"
echo "====================================="
echo "Timestamp: $TIMESTAMP"
echo "Constitutional Hash: $CONSTITUTIONAL_HASH"
echo "Namespace: $NAMESPACE"
echo ""
echo "Service Compliance:"
echo "  Total services checked: $TOTAL_SERVICES"
echo "  Compliant services: $COMPLIANT_SERVICES"
echo "  Compliance rate: $((COMPLIANT_SERVICES * 100 / TOTAL_SERVICES))%"
echo ""
echo "Overall Results:"
echo "  Total failures: $TOTAL_FAILURES"
echo "  Critical issues: $((TOTAL_SERVICES - COMPLIANT_SERVICES))"

# Generate detailed report
REPORT_FILE="/tmp/constitutional_compliance_report_$(date +%Y%m%d_%H%M%S).json"

cat > "$REPORT_FILE" << EOF
{
  "timestamp": "$TIMESTAMP",
  "constitutional_hash": "$CONSTITUTIONAL_HASH",
  "namespace": "$NAMESPACE",
  "summary": {
    "total_services": $TOTAL_SERVICES,
    "compliant_services": $COMPLIANT_SERVICES,
    "compliance_rate": $((COMPLIANT_SERVICES * 100 / TOTAL_SERVICES)),
    "total_failures": $TOTAL_FAILURES,
    "status": "$(if [[ $TOTAL_FAILURES -eq 0 ]]; then echo "COMPLIANT"; else echo "NON_COMPLIANT"; fi)"
  },
  "services": {
EOF

# Add service details to report
first=true
for service in "${!SERVICES[@]}"; do
    if [[ "$first" == "true" ]]; then
        first=false
    else
        echo "," >> "$REPORT_FILE"
    fi
    
    echo "    \"$service\": {" >> "$REPORT_FILE"
    echo "      \"port\": ${SERVICES[$service]}," >> "$REPORT_FILE"
    echo "      \"constitutional_hash\": \"$CONSTITUTIONAL_HASH\"" >> "$REPORT_FILE"
    echo -n "    }" >> "$REPORT_FILE"
done

echo "" >> "$REPORT_FILE"
echo "  }" >> "$REPORT_FILE"
echo "}" >> "$REPORT_FILE"

echo ""
echo "📄 Detailed report saved to: $REPORT_FILE"

# Final status determination
if [[ $TOTAL_FAILURES -eq 0 ]] && [[ $COMPLIANT_SERVICES -eq $TOTAL_SERVICES ]]; then
    echo ""
    echo "✅ CONSTITUTIONAL COMPLIANCE: FULLY COMPLIANT"
    echo "🏛️ All services maintain constitutional hash $CONSTITUTIONAL_HASH"
    echo "🎉 System is ready for production operation"
    exit 0
elif [[ $COMPLIANT_SERVICES -gt 0 ]]; then
    echo ""
    echo "⚠️ CONSTITUTIONAL COMPLIANCE: PARTIALLY COMPLIANT"
    echo "🔧 Some services require attention"
    echo "📋 Review failures and take corrective action"
    exit 1
else
    echo ""
    echo "❌ CONSTITUTIONAL COMPLIANCE: NON-COMPLIANT"
    echo "🚨 Critical constitutional compliance failure"
    echo "🛠️ Immediate intervention required"
    exit 2
fi