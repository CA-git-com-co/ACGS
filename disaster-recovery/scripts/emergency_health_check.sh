#!/bin/bash
# ACGS-2 Emergency Health Check
# Constitutional Hash: cdd01ef066bc6cf2

set -euo pipefail

CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M:%S UTC")

echo "🚨 ACGS-2 Emergency Health Check"
echo "Constitutional Hash: $CONSTITUTIONAL_HASH"
echo "Timestamp: $TIMESTAMP"
echo "================================="

# Check Kubernetes cluster health
echo "📋 Checking Kubernetes cluster health..."
if kubectl cluster-info &>/dev/null; then
    echo "✅ Kubernetes cluster is accessible"
    kubectl get nodes --no-headers | while read line; do
        node_name=$(echo $line | awk '{print $1}')
        node_status=$(echo $line | awk '{print $2}')
        echo "  Node $node_name: $node_status"
    done
else
    echo "❌ Kubernetes cluster is not accessible"
    exit 1
fi

# Check namespace
echo "📋 Checking ACGS-2 namespace..."
if kubectl get namespace acgs-system &>/dev/null; then
    echo "✅ acgs-system namespace exists"
else
    echo "❌ acgs-system namespace not found"
    exit 1
fi

# Check critical services
echo "📋 Checking critical services..."
SERVICES=("constitutional-core" "auth-service" "monitoring-service" "audit-service" "api-gateway")

for service in "${SERVICES[@]}"; do
    echo "Checking $service..."
    
    # Check if deployment exists
    if kubectl get deployment $service -n acgs-system &>/dev/null; then
        # Check if pods are running
        RUNNING_PODS=$(kubectl get pods -l app=$service -n acgs-system --field-selector=status.phase=Running --no-headers | wc -l)
        TOTAL_PODS=$(kubectl get pods -l app=$service -n acgs-system --no-headers | wc -l)
        
        if [[ $RUNNING_PODS -gt 0 ]]; then
            echo "✅ $service is running ($RUNNING_PODS/$TOTAL_PODS pods)"
        else
            echo "❌ $service is not running (0/$TOTAL_PODS pods)"
            kubectl describe pods -l app=$service -n acgs-system | grep -E "Events:|Warning|Error" | tail -5
        fi
    else
        echo "❌ $service deployment not found"
    fi
done

# Check database connectivity
echo "📋 Checking database connectivity..."
if kubectl get deployment postgres -n acgs-system &>/dev/null; then
    if kubectl exec deployment/postgres -n acgs-system -- pg_isready -h localhost -p 5432 -U acgs_user &>/dev/null; then
        echo "✅ PostgreSQL database is accessible"
    else
        echo "❌ PostgreSQL database is not accessible"
    fi
else
    echo "❌ PostgreSQL deployment not found"
fi

# Check Redis connectivity
echo "📋 Checking Redis connectivity..."
if kubectl get deployment redis -n acgs-system &>/dev/null; then
    if kubectl exec deployment/redis -n acgs-system -- redis-cli ping &>/dev/null; then
        echo "✅ Redis is accessible"
    else
        echo "❌ Redis is not accessible"
    fi
else
    echo "❌ Redis deployment not found"
fi

# Check constitutional compliance
echo "📋 Checking constitutional compliance..."
COMPLIANCE_FAILURES=0

for service in "${SERVICES[@]}"; do
    # Get service port
    case $service in
        "constitutional-core") PORT=8001 ;;
        "auth-service") PORT=8013 ;;
        "monitoring-service") PORT=8014 ;;
        "audit-service") PORT=8015 ;;
        "api-gateway") PORT=8080 ;;
        *) PORT=8080 ;;
    esac
    
    # Check if service is accessible
    if kubectl get service $service -n acgs-system &>/dev/null; then
        # Port forward and check health
        kubectl port-forward service/$service $PORT:$PORT -n acgs-system &>/dev/null &
        PID=$!
        sleep 5
        
        RESPONSE=$(curl -s http://localhost:$PORT/health 2>/dev/null || echo "{}")
        HASH=$(echo "$RESPONSE" | jq -r '.constitutional_hash // empty' 2>/dev/null || echo "")
        
        if [[ "$HASH" == "$CONSTITUTIONAL_HASH" ]]; then
            echo "✅ $service constitutional compliance verified"
        else
            echo "❌ $service constitutional compliance failed (expected: $CONSTITUTIONAL_HASH, got: $HASH)"
            ((COMPLIANCE_FAILURES++))
        fi
        
        kill $PID 2>/dev/null || true
        sleep 1
    else
        echo "❌ $service service not found"
        ((COMPLIANCE_FAILURES++))
    fi
done

# Check storage volumes
echo "📋 Checking persistent volumes..."
PV_STATUS=$(kubectl get pv --no-headers 2>/dev/null | wc -l)
PVC_STATUS=$(kubectl get pvc -n acgs-system --no-headers 2>/dev/null | wc -l)
echo "  Persistent Volumes: $PV_STATUS"
echo "  Persistent Volume Claims: $PVC_STATUS"

# Check secrets
echo "📋 Checking secrets..."
if kubectl get secret acgs-secrets -n acgs-system &>/dev/null; then
    echo "✅ ACGS secrets are present"
else
    echo "❌ ACGS secrets not found"
fi

# Generate summary
echo ""
echo "📊 EMERGENCY HEALTH CHECK SUMMARY"
echo "================================="
echo "Timestamp: $TIMESTAMP"
echo "Constitutional Hash: $CONSTITUTIONAL_HASH"
echo "Constitutional Compliance Failures: $COMPLIANCE_FAILURES"

if [[ $COMPLIANCE_FAILURES -eq 0 ]]; then
    echo "✅ OVERALL STATUS: HEALTHY"
    echo "🏛️ Constitutional compliance maintained"
    exit 0
else
    echo "❌ OVERALL STATUS: CRITICAL"
    echo "🚨 Constitutional compliance compromised"
    echo "🛠️ Immediate intervention required"
    exit 1
fi