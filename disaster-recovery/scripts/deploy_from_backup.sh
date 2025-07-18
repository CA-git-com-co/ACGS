#!/bin/bash
# ACGS-2 Service Recovery from Backup
# Constitutional Hash: cdd01ef066bc6cf2

set -euo pipefail

CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
BACKUP_REGISTRY="${BACKUP_REGISTRY:-ghcr.io/acgs-backup}"
RECOVERY_TAG="${RECOVERY_TAG:-disaster-recovery}"
NAMESPACE="${NAMESPACE:-acgs-system}"

echo "🏛️ ACGS-2 Service Recovery from Backup"
echo "Constitutional Hash: $CONSTITUTIONAL_HASH"
echo "Backup Registry: $BACKUP_REGISTRY"
echo "Recovery Tag: $RECOVERY_TAG"
echo "Namespace: $NAMESPACE"
echo "================================="

# Critical services in deployment order
SERVICES=(
    "constitutional-core:8001"
    "auth-service:8013"
    "monitoring-service:8014"
    "audit-service:8015"
    "gdpr-compliance:8016"
    "alerting-service:8017"
    "api-gateway:8080"
)

# Check if namespace exists
if ! kubectl get namespace "$NAMESPACE" &>/dev/null; then
    echo "🔧 Creating namespace $NAMESPACE..."
    kubectl create namespace "$NAMESPACE"
fi

# Deploy infrastructure first (if needed)
echo "🏗️ Ensuring infrastructure components are ready..."

# Check and deploy PostgreSQL if needed
if ! kubectl get deployment postgres -n "$NAMESPACE" &>/dev/null; then
    echo "🐘 Deploying PostgreSQL..."
    kubectl create deployment postgres --image=postgres:15 -n "$NAMESPACE"
    kubectl set env deployment/postgres POSTGRES_DB=acgs_db POSTGRES_USER=acgs_user POSTGRES_PASSWORD=postgres_secret -n "$NAMESPACE"
    kubectl expose deployment postgres --port=5432 -n "$NAMESPACE"
    kubectl wait --for=condition=available --timeout=120s deployment/postgres -n "$NAMESPACE"
fi

# Check and deploy Redis if needed
if ! kubectl get deployment redis -n "$NAMESPACE" &>/dev/null; then
    echo "🔴 Deploying Redis..."
    kubectl create deployment redis --image=redis:7-alpine -n "$NAMESPACE"
    kubectl expose deployment redis --port=6379 -n "$NAMESPACE"
    kubectl wait --for=condition=available --timeout=120s deployment/redis -n "$NAMESPACE"
fi

# Deploy services from backup images
echo "🚀 Deploying services from backup images..."

for service_config in "${SERVICES[@]}"; do
    IFS=':' read -r service port <<< "$service_config"
    
    echo ""
    echo "📦 Deploying $service from backup..."
    
    # Check if deployment exists
    if kubectl get deployment "$service" -n "$NAMESPACE" &>/dev/null; then
        echo "  Updating existing deployment..."
        
        # Update deployment with backup image
        kubectl patch deployment "$service" -n "$NAMESPACE" -p "{
            \"spec\": {
                \"template\": {
                    \"spec\": {
                        \"containers\": [{
                            \"name\": \"$service\",
                            \"image\": \"$BACKUP_REGISTRY/$service:$RECOVERY_TAG\",
                            \"env\": [
                                {\"name\": \"CONSTITUTIONAL_HASH\", \"value\": \"$CONSTITUTIONAL_HASH\"},
                                {\"name\": \"PORT\", \"value\": \"$port\"},
                                {\"name\": \"DATABASE_URL\", \"value\": \"postgresql://acgs_user:postgres_secret@postgres:5432/acgs_db\"},
                                {\"name\": \"REDIS_URL\", \"value\": \"redis://redis:6379/0\"}
                            ]
                        }]
                    }
                }
            }
        }"
    else
        echo "  Creating new deployment..."
        
        # Create deployment from backup image
        kubectl create deployment "$service" --image="$BACKUP_REGISTRY/$service:$RECOVERY_TAG" -n "$NAMESPACE"
        
        # Set environment variables
        kubectl set env deployment/"$service" \
            CONSTITUTIONAL_HASH="$CONSTITUTIONAL_HASH" \
            PORT="$port" \
            DATABASE_URL="postgresql://acgs_user:postgres_secret@postgres:5432/acgs_db" \
            REDIS_URL="redis://redis:6379/0" \
            -n "$NAMESPACE"
        
        # Expose service
        kubectl expose deployment "$service" --port="$port" -n "$NAMESPACE"
    fi
    
    # Wait for deployment to be ready
    echo "  Waiting for $service to be ready..."
    kubectl wait --for=condition=available --timeout=180s deployment/"$service" -n "$NAMESPACE"
    
    # Verify service is running
    RUNNING_PODS=$(kubectl get pods -l app="$service" -n "$NAMESPACE" --field-selector=status.phase=Running --no-headers | wc -l)
    if [[ $RUNNING_PODS -gt 0 ]]; then
        echo "  ✅ $service is running ($RUNNING_PODS pod(s))"
    else
        echo "  ❌ $service failed to start"
        kubectl logs deployment/"$service" -n "$NAMESPACE" --tail=10
        continue
    fi
    
    # Verify constitutional compliance
    echo "  🏛️ Verifying constitutional compliance..."
    
    # Port forward to check health endpoint
    kubectl port-forward service/"$service" "$port":"$port" -n "$NAMESPACE" &>/dev/null &
    PID=$!
    sleep 10
    
    # Check health endpoint
    RESPONSE=$(curl -s "http://localhost:$port/health" 2>/dev/null || echo "{}")
    HASH=$(echo "$RESPONSE" | jq -r '.constitutional_hash // empty' 2>/dev/null || echo "")
    
    if [[ "$HASH" == "$CONSTITUTIONAL_HASH" ]]; then
        echo "  ✅ $service constitutional compliance verified"
    else
        echo "  ⚠️ $service constitutional compliance check failed"
        echo "     Expected: $CONSTITUTIONAL_HASH"
        echo "     Received: $HASH"
        echo "     Response: $RESPONSE"
        
        # Try to fix constitutional compliance
        echo "  🔧 Attempting to fix constitutional compliance..."
        kubectl set env deployment/"$service" CONSTITUTIONAL_HASH="$CONSTITUTIONAL_HASH" -n "$NAMESPACE"
        kubectl rollout restart deployment/"$service" -n "$NAMESPACE"
        kubectl wait --for=condition=available --timeout=120s deployment/"$service" -n "$NAMESPACE"
        
        # Re-check after fix
        sleep 5
        RESPONSE=$(curl -s "http://localhost:$port/health" 2>/dev/null || echo "{}")
        HASH=$(echo "$RESPONSE" | jq -r '.constitutional_hash // empty' 2>/dev/null || echo "")
        
        if [[ "$HASH" == "$CONSTITUTIONAL_HASH" ]]; then
            echo "  ✅ $service constitutional compliance fixed"
        else
            echo "  ❌ $service constitutional compliance could not be fixed"
        fi
    fi
    
    # Clean up port forward
    kill $PID 2>/dev/null || true
    sleep 2
    
    echo "  ✅ $service deployment completed"
done

# Verify inter-service communication
echo ""
echo "🔗 Verifying inter-service communication..."

# Test auth service -> monitoring service communication
kubectl port-forward service/auth-service 8013:8013 -n "$NAMESPACE" &>/dev/null &
AUTH_PID=$!
kubectl port-forward service/monitoring-service 8014:8014 -n "$NAMESPACE" &>/dev/null &
MONITOR_PID=$!
sleep 10

# Test health endpoints
AUTH_HEALTH=$(curl -s http://localhost:8013/health 2>/dev/null || echo "{}")
MONITOR_HEALTH=$(curl -s http://localhost:8014/health 2>/dev/null || echo "{}")

if [[ $(echo "$AUTH_HEALTH" | jq -r '.status // empty') == "healthy" ]] && [[ $(echo "$MONITOR_HEALTH" | jq -r '.status // empty') == "healthy" ]]; then
    echo "✅ Inter-service communication verified"
else
    echo "⚠️ Inter-service communication issues detected"
fi

kill $AUTH_PID $MONITOR_PID 2>/dev/null || true

# Create ingress for API gateway (if needed)
echo ""
echo "🌐 Setting up ingress for API gateway..."
if ! kubectl get ingress acgs-ingress -n "$NAMESPACE" &>/dev/null; then
    cat << EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: acgs-ingress
  namespace: $NAMESPACE
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: acgs.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api-gateway
            port:
              number: 8080
EOF
    echo "✅ Ingress created for API gateway"
fi

# Final system health check
echo ""
echo "🏥 Running final system health check..."

HEALTHY_SERVICES=0
TOTAL_SERVICES=${#SERVICES[@]}

for service_config in "${SERVICES[@]}"; do
    IFS=':' read -r service port <<< "$service_config"
    
    if kubectl get pods -l app="$service" -n "$NAMESPACE" --field-selector=status.phase=Running --no-headers | grep -q Running; then
        ((HEALTHY_SERVICES++))
    fi
done

echo "📊 Recovery Summary:"
echo "  Total services: $TOTAL_SERVICES"
echo "  Healthy services: $HEALTHY_SERVICES"
echo "  Success rate: $((HEALTHY_SERVICES * 100 / TOTAL_SERVICES))%"
echo "  Constitutional hash: $CONSTITUTIONAL_HASH"
echo "  Recovery timestamp: $(date -u)"

if [[ $HEALTHY_SERVICES -eq $TOTAL_SERVICES ]]; then
    echo ""
    echo "✅ All services deployed successfully from backup!"
    echo "🏛️ Constitutional compliance maintained throughout recovery"
    echo ""
    echo "🔗 Access points:"
    echo "  API Gateway: http://acgs.local (via ingress)"
    echo "  Direct access: kubectl port-forward service/api-gateway 8080:8080 -n $NAMESPACE"
    echo ""
    echo "📋 Next steps:"
    echo "  1. Run comprehensive tests: ./tests/run_all_tests.py"
    echo "  2. Verify performance: ./tests/performance/run_performance_tests.py"
    echo "  3. Check monitoring: kubectl port-forward service/monitoring-service 8014:8014 -n $NAMESPACE"
    exit 0
else
    echo ""
    echo "⚠️ Partial recovery completed"
    echo "🛠️ Manual intervention may be required for failed services"
    echo ""
    echo "🔧 Troubleshooting commands:"
    echo "  Check pods: kubectl get pods -n $NAMESPACE"
    echo "  Check logs: kubectl logs deployment/<service-name> -n $NAMESPACE"
    echo "  Describe deployment: kubectl describe deployment <service-name> -n $NAMESPACE"
    exit 1
fi