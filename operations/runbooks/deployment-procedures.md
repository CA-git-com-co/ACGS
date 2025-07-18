# ACGS-2 Deployment Procedures Runbook
<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

## Overview

Comprehensive deployment procedures for ACGS-2 (Advanced Constitutional Governance System). This runbook provides step-by-step procedures for deploying, updating, and rolling back ACGS-2 services while maintaining constitutional compliance and operational continuity.

## Constitutional Requirements

All deployment procedures must maintain constitutional hash `cdd01ef066bc6cf2` validation and adhere to:
- **Zero-downtime deployments** for constitutional services
- **Rollback capability** within 5 minutes
- **Performance validation** (P99 <5ms, >100 RPS) post-deployment
- **Constitutional compliance** verification at each stage

## Deployment Types

### 1. New Service Deployment
### 2. Service Updates and Patches
### 3. Infrastructure Updates
### 4. Emergency Hotfixes
### 5. Rollback Procedures

## Pre-Deployment Checklist

### Environment Validation
```bash
# Verify cluster health
kubectl cluster-info
kubectl get nodes
kubectl get pods -n acgs-system

# Check constitutional compliance
kubectl get pods -n acgs-system -l constitutional-hash=cdd01ef066bc6cf2

# Verify resource availability
kubectl describe nodes | grep -A 5 "Allocated resources"

# Check storage availability
kubectl get pv,pvc -n acgs-system
```

### Backup Verification
```bash
# Verify recent backup
kubectl get job -n acgs-system backup-job
kubectl logs -n acgs-system job/backup-job

# Test backup restore capability
kubectl apply -f /deployment/testing/backup-restore-test.yaml
kubectl wait --for=condition=complete job/backup-restore-test -n acgs-system --timeout=300s
```

### Performance Baseline
```bash
# Capture current performance metrics
BASELINE_TIMESTAMP=$(date --iso-8601)
curl -s "http://monitoring-service:8014/api/metrics/performance" > /tmp/baseline-$BASELINE_TIMESTAMP.json

# Record current constitutional operations
curl -s "http://constitutional-core:8001/api/health" > /tmp/constitutional-baseline-$BASELINE_TIMESTAMP.json
```

## New Service Deployment

### Step 1: Prepare Deployment Manifests
```bash
# Create service directory
SERVICE_NAME="new-service"
mkdir -p /deployment/services/$SERVICE_NAME

# Generate deployment manifest
cat > /deployment/services/$SERVICE_NAME/deployment.yaml << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: $SERVICE_NAME
  namespace: acgs-system
  labels:
    app: $SERVICE_NAME
    constitutional-hash: cdd01ef066bc6cf2
    version: v1.0.0
spec:
  replicas: 3
  selector:
    matchLabels:
      app: $SERVICE_NAME
  template:
    metadata:
      labels:
        app: $SERVICE_NAME
        constitutional-hash: cdd01ef066bc6cf2
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8080"
        prometheus.io/path: "/metrics"
    spec:
      serviceAccountName: acgs-system-sa
      containers:
      - name: $SERVICE_NAME
        image: acgs/$SERVICE_NAME:v1.0.0
        ports:
        - containerPort: 8080
          name: http
        env:
        - name: CONSTITUTIONAL_HASH
          value: "cdd01ef066bc6cf2"
        - name: SERVICE_NAME
          value: "$SERVICE_NAME"
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
        volumeMounts:
        - name: config
          mountPath: /etc/config
      volumes:
      - name: config
        configMap:
          name: $SERVICE_NAME-config
EOF
```

### Step 2: Create Service and Configuration
```bash
# Create service manifest
cat > /deployment/services/$SERVICE_NAME/service.yaml << EOF
apiVersion: v1
kind: Service
metadata:
  name: $SERVICE_NAME
  namespace: acgs-system
  labels:
    app: $SERVICE_NAME
    constitutional-hash: cdd01ef066bc6cf2
spec:
  type: ClusterIP
  ports:
  - port: 8080
    targetPort: 8080
    name: http
  selector:
    app: $SERVICE_NAME
EOF

# Create configuration
cat > /deployment/services/$SERVICE_NAME/configmap.yaml << EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: $SERVICE_NAME-config
  namespace: acgs-system
  labels:
    constitutional-hash: cdd01ef066bc6cf2
data:
  config.yaml: |
    constitutional_hash: "cdd01ef066bc6cf2"
    service_name: "$SERVICE_NAME"
    logging_level: "INFO"
    metrics_enabled: true
    tracing_enabled: true
EOF
```

### Step 3: Deploy Service
```bash
# Apply configurations
kubectl apply -f /deployment/services/$SERVICE_NAME/configmap.yaml
kubectl apply -f /deployment/services/$SERVICE_NAME/service.yaml
kubectl apply -f /deployment/services/$SERVICE_NAME/deployment.yaml

# Monitor deployment
kubectl rollout status deployment/$SERVICE_NAME -n acgs-system --timeout=300s

# Verify deployment
kubectl get pods -n acgs-system -l app=$SERVICE_NAME
kubectl get service -n acgs-system $SERVICE_NAME
```

### Step 4: Post-Deployment Validation
```bash
# Health check
kubectl exec -n acgs-system deployment/$SERVICE_NAME -- curl -f http://localhost:8080/health

# Constitutional compliance check
kubectl exec -n acgs-system deployment/$SERVICE_NAME -- \
  curl -H "constitutional-hash: cdd01ef066bc6cf2" http://localhost:8080/health

# Performance validation
kubectl exec -n acgs-system deployment/$SERVICE_NAME -- \
  curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8080/health
```

## Service Updates and Patches

### Step 1: Pre-Update Preparation
```bash
SERVICE_NAME="constitutional-core"
NEW_VERSION="v1.0.1"
CURRENT_VERSION=$(kubectl get deployment $SERVICE_NAME -n acgs-system -o jsonpath='{.spec.template.spec.containers[0].image}' | cut -d: -f2)

echo "Updating $SERVICE_NAME from $CURRENT_VERSION to $NEW_VERSION"

# Create backup of current configuration
kubectl get deployment $SERVICE_NAME -n acgs-system -o yaml > /tmp/$SERVICE_NAME-backup-$(date +%Y%m%d%H%M%S).yaml
```

### Step 2: Rolling Update Strategy
```bash
# Configure rolling update strategy
kubectl patch deployment $SERVICE_NAME -n acgs-system --patch '
{
  "spec": {
    "strategy": {
      "type": "RollingUpdate",
      "rollingUpdate": {
        "maxSurge": 1,
        "maxUnavailable": 0
      }
    }
  }
}'

# Update image
kubectl set image deployment/$SERVICE_NAME -n acgs-system $SERVICE_NAME=acgs/$SERVICE_NAME:$NEW_VERSION

# Monitor rolling update
kubectl rollout status deployment/$SERVICE_NAME -n acgs-system --timeout=600s
```

### Step 3: Deployment Validation
```bash
# Verify new pods are running
kubectl get pods -n acgs-system -l app=$SERVICE_NAME

# Check constitutional compliance
kubectl get pods -n acgs-system -l app=$SERVICE_NAME -o jsonpath='{.items[*].metadata.labels.constitutional-hash}'

# Test service functionality
kubectl exec -n acgs-system deployment/$SERVICE_NAME -- curl -f http://localhost:8080/health

# Validate constitutional operations
curl -X POST "http://$SERVICE_NAME:8080/api/constitutional/validate" \
  -H "constitutional-hash: cdd01ef066bc6cf2" \
  -d '{"test": "post_deployment"}'
```

### Step 4: Performance Validation
```bash
# Run performance test
kubectl apply -f /deployment/testing/performance/service-performance-test.yaml
kubectl wait --for=condition=complete job/service-performance-test -n acgs-system --timeout=300s

# Check performance metrics
LATENCY=$(curl -s "http://monitoring-service:8014/api/metrics/latency/$SERVICE_NAME" | jq -r .p99)
THROUGHPUT=$(curl -s "http://monitoring-service:8014/api/metrics/throughput/$SERVICE_NAME" | jq -r .rps)

echo "Post-deployment performance: P99=$LATENCY ms, Throughput=$THROUGHPUT RPS"

# Validate constitutional requirements
if (( $(echo "$LATENCY > 5" | bc -l) )); then
  echo "❌ PERFORMANCE VIOLATION: P99 latency ($LATENCY ms) exceeds 5ms"
  exit 1
fi

if (( $(echo "$THROUGHPUT < 100" | bc -l) )); then
  echo "❌ PERFORMANCE VIOLATION: Throughput ($THROUGHPUT RPS) below 100 RPS"
  exit 1
fi

echo "✅ Performance validation passed"
```

## Blue-Green Deployment

### Step 1: Prepare Green Environment
```bash
SERVICE_NAME="constitutional-core"
BLUE_VERSION="v1.0.0"
GREEN_VERSION="v1.0.1"

# Create green deployment
kubectl apply -f - << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: $SERVICE_NAME-green
  namespace: acgs-system
  labels:
    app: $SERVICE_NAME
    version: green
    constitutional-hash: cdd01ef066bc6cf2
spec:
  replicas: 3
  selector:
    matchLabels:
      app: $SERVICE_NAME
      version: green
  template:
    metadata:
      labels:
        app: $SERVICE_NAME
        version: green
        constitutional-hash: cdd01ef066bc6cf2
    spec:
      serviceAccountName: acgs-system-sa
      containers:
      - name: $SERVICE_NAME
        image: acgs/$SERVICE_NAME:$GREEN_VERSION
        ports:
        - containerPort: 8080
        env:
        - name: CONSTITUTIONAL_HASH
          value: "cdd01ef066bc6cf2"
        - name: VERSION
          value: "green"
        resources:
          requests:
            memory: "512Mi"
            cpu: "200m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
EOF
```

### Step 2: Validate Green Environment
```bash
# Wait for green deployment
kubectl rollout status deployment/$SERVICE_NAME-green -n acgs-system --timeout=300s

# Test green environment
kubectl exec -n acgs-system deployment/$SERVICE_NAME-green -- curl -f http://localhost:8080/health

# Run comprehensive tests on green
kubectl apply -f /deployment/testing/integration/green-environment-test.yaml
kubectl wait --for=condition=complete job/green-environment-test -n acgs-system --timeout=600s
```

### Step 3: Traffic Switch
```bash
# Switch service to green
kubectl patch service $SERVICE_NAME -n acgs-system --patch '
{
  "spec": {
    "selector": {
      "app": "'$SERVICE_NAME'",
      "version": "green"
    }
  }
}'

# Verify traffic switch
kubectl get service $SERVICE_NAME -n acgs-system -o yaml | grep -A 5 selector
```

### Step 4: Cleanup Blue Environment
```bash
# Monitor green environment for 10 minutes
for i in {1..10}; do
  echo "=== Monitoring Green Environment - Minute $i/10 ==="
  kubectl get pods -n acgs-system -l app=$SERVICE_NAME,version=green
  kubectl exec -n acgs-system deployment/$SERVICE_NAME-green -- curl -f http://localhost:8080/health
  sleep 60
done

# If stable, remove blue environment
kubectl delete deployment $SERVICE_NAME-blue -n acgs-system
echo "✅ Blue-green deployment completed successfully"
```

## Canary Deployment

### Step 1: Deploy Canary Version
```bash
SERVICE_NAME="groqcloud-policy"
CANARY_VERSION="v1.0.2"
CANARY_PERCENTAGE=10

# Create canary deployment
kubectl apply -f - << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: $SERVICE_NAME-canary
  namespace: acgs-system
  labels:
    app: $SERVICE_NAME
    version: canary
    constitutional-hash: cdd01ef066bc6cf2
spec:
  replicas: 1
  selector:
    matchLabels:
      app: $SERVICE_NAME
      version: canary
  template:
    metadata:
      labels:
        app: $SERVICE_NAME
        version: canary
        constitutional-hash: cdd01ef066bc6cf2
    spec:
      serviceAccountName: acgs-system-sa
      containers:
      - name: $SERVICE_NAME
        image: acgs/$SERVICE_NAME:$CANARY_VERSION
        ports:
        - containerPort: 8080
        env:
        - name: CONSTITUTIONAL_HASH
          value: "cdd01ef066bc6cf2"
        - name: VERSION
          value: "canary"
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
EOF
```

### Step 2: Configure Traffic Splitting
```bash
# Create Istio traffic split
kubectl apply -f - << EOF
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: $SERVICE_NAME-canary
  namespace: acgs-system
  labels:
    constitutional-hash: cdd01ef066bc6cf2
spec:
  hosts:
  - $SERVICE_NAME
  http:
  - match:
    - headers:
        canary:
          exact: "true"
    route:
    - destination:
        host: $SERVICE_NAME
        subset: canary
  - route:
    - destination:
        host: $SERVICE_NAME
        subset: stable
      weight: 90
    - destination:
        host: $SERVICE_NAME
        subset: canary
      weight: 10
---
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: $SERVICE_NAME-canary
  namespace: acgs-system
  labels:
    constitutional-hash: cdd01ef066bc6cf2
spec:
  host: $SERVICE_NAME
  subsets:
  - name: stable
    labels:
      version: stable
  - name: canary
    labels:
      version: canary
EOF
```

### Step 3: Monitor Canary Performance
```bash
# Monitor canary metrics
for i in {1..30}; do
  echo "=== Canary Monitoring - Minute $i/30 ==="
  
  # Check error rates
  STABLE_ERRORS=$(curl -s "http://monitoring-service:8014/api/metrics/errors/$SERVICE_NAME?version=stable" | jq -r .rate)
  CANARY_ERRORS=$(curl -s "http://monitoring-service:8014/api/metrics/errors/$SERVICE_NAME?version=canary" | jq -r .rate)
  
  echo "Stable error rate: $STABLE_ERRORS"
  echo "Canary error rate: $CANARY_ERRORS"
  
  # Check latency
  STABLE_LATENCY=$(curl -s "http://monitoring-service:8014/api/metrics/latency/$SERVICE_NAME?version=stable" | jq -r .p99)
  CANARY_LATENCY=$(curl -s "http://monitoring-service:8014/api/metrics/latency/$SERVICE_NAME?version=canary" | jq -r .p99)
  
  echo "Stable P99 latency: $STABLE_LATENCY ms"
  echo "Canary P99 latency: $CANARY_LATENCY ms"
  
  # Check constitutional compliance
  CANARY_COMPLIANCE=$(curl -s "http://monitoring-service:8014/api/metrics/compliance/$SERVICE_NAME?version=canary" | jq -r .rate)
  echo "Canary compliance rate: $CANARY_COMPLIANCE"
  
  sleep 60
done
```

### Step 4: Promote or Rollback Canary
```bash
# Decision logic
if (( $(echo "$CANARY_ERRORS < 0.01" | bc -l) )) && (( $(echo "$CANARY_LATENCY < 5" | bc -l) )) && (( $(echo "$CANARY_COMPLIANCE > 0.99" | bc -l) )); then
  echo "✅ Canary validation passed - Promoting to production"
  
  # Promote canary
  kubectl patch service $SERVICE_NAME -n acgs-system --patch '
  {
    "spec": {
      "selector": {
        "app": "'$SERVICE_NAME'",
        "version": "canary"
      }
    }
  }'
  
  # Update stable deployment
  kubectl set image deployment/$SERVICE_NAME -n acgs-system $SERVICE_NAME=acgs/$SERVICE_NAME:$CANARY_VERSION
  
  # Cleanup canary
  kubectl delete deployment $SERVICE_NAME-canary -n acgs-system
  kubectl delete virtualservice $SERVICE_NAME-canary -n acgs-system
  kubectl delete destinationrule $SERVICE_NAME-canary -n acgs-system
  
else
  echo "❌ Canary validation failed - Rolling back"
  
  # Rollback canary
  kubectl delete deployment $SERVICE_NAME-canary -n acgs-system
  kubectl delete virtualservice $SERVICE_NAME-canary -n acgs-system
  kubectl delete destinationrule $SERVICE_NAME-canary -n acgs-system
fi
```

## Emergency Hotfix Deployment

### Step 1: Emergency Assessment
```bash
HOTFIX_VERSION="v1.0.1-hotfix.1"
SERVICE_NAME="constitutional-core"
INCIDENT_ID="ACGS-$(date +%Y%m%d%H%M%S)"

echo "=== EMERGENCY HOTFIX DEPLOYMENT ==="
echo "Incident ID: $INCIDENT_ID"
echo "Service: $SERVICE_NAME"
echo "Hotfix Version: $HOTFIX_VERSION"
echo "Constitutional Hash: cdd01ef066bc6cf2"
```

### Step 2: Expedited Deployment
```bash
# Skip normal validation for emergency
kubectl set image deployment/$SERVICE_NAME -n acgs-system $SERVICE_NAME=acgs/$SERVICE_NAME:$HOTFIX_VERSION

# Force immediate rollout
kubectl rollout restart deployment/$SERVICE_NAME -n acgs-system
kubectl rollout status deployment/$SERVICE_NAME -n acgs-system --timeout=180s

# Immediate health check
kubectl exec -n acgs-system deployment/$SERVICE_NAME -- curl -f http://localhost:8080/health
```

### Step 3: Critical Validation
```bash
# Validate constitutional compliance
kubectl exec -n acgs-system deployment/$SERVICE_NAME -- \
  curl -H "constitutional-hash: cdd01ef066bc6cf2" http://localhost:8080/health

# Test critical functionality
curl -X POST "http://$SERVICE_NAME:8080/api/constitutional/validate" \
  -H "constitutional-hash: cdd01ef066bc6cf2" \
  -d '{"emergency_test": true}'

# Quick performance check
curl -w "@curl-format.txt" -o /dev/null -s "http://$SERVICE_NAME:8080/health"
```

## Rollback Procedures

### Automatic Rollback Triggers
```bash
# Create rollback trigger script
cat > /scripts/rollback-trigger.sh << 'EOF'
#!/bin/bash
SERVICE_NAME=$1
ROLLBACK_THRESHOLD_ERRORS=0.05
ROLLBACK_THRESHOLD_LATENCY=10
ROLLBACK_THRESHOLD_COMPLIANCE=0.95

# Get current metrics
ERROR_RATE=$(curl -s "http://monitoring-service:8014/api/metrics/errors/$SERVICE_NAME" | jq -r .rate)
LATENCY=$(curl -s "http://monitoring-service:8014/api/metrics/latency/$SERVICE_NAME" | jq -r .p99)
COMPLIANCE=$(curl -s "http://monitoring-service:8014/api/metrics/compliance/$SERVICE_NAME" | jq -r .rate)

# Check rollback conditions
if (( $(echo "$ERROR_RATE > $ROLLBACK_THRESHOLD_ERRORS" | bc -l) )) || \
   (( $(echo "$LATENCY > $ROLLBACK_THRESHOLD_LATENCY" | bc -l) )) || \
   (( $(echo "$COMPLIANCE < $ROLLBACK_THRESHOLD_COMPLIANCE" | bc -l) )); then
  
  echo "❌ ROLLBACK TRIGGERED for $SERVICE_NAME"
  echo "Error rate: $ERROR_RATE (threshold: $ROLLBACK_THRESHOLD_ERRORS)"
  echo "Latency: $LATENCY ms (threshold: $ROLLBACK_THRESHOLD_LATENCY ms)"
  echo "Compliance: $COMPLIANCE (threshold: $ROLLBACK_THRESHOLD_COMPLIANCE)"
  
  # Execute rollback
  kubectl rollout undo deployment/$SERVICE_NAME -n acgs-system
  kubectl rollout status deployment/$SERVICE_NAME -n acgs-system --timeout=300s
  
  echo "✅ Rollback completed for $SERVICE_NAME"
else
  echo "✅ All metrics within acceptable range for $SERVICE_NAME"
fi
EOF

chmod +x /scripts/rollback-trigger.sh
```

### Manual Rollback
```bash
SERVICE_NAME="constitutional-core"

# Check rollout history
kubectl rollout history deployment/$SERVICE_NAME -n acgs-system

# Rollback to previous version
kubectl rollout undo deployment/$SERVICE_NAME -n acgs-system

# Rollback to specific revision
kubectl rollout undo deployment/$SERVICE_NAME -n acgs-system --to-revision=2

# Monitor rollback
kubectl rollout status deployment/$SERVICE_NAME -n acgs-system --timeout=300s
```

### Post-Rollback Validation
```bash
# Validate rollback
kubectl get deployment $SERVICE_NAME -n acgs-system -o jsonpath='{.spec.template.spec.containers[0].image}'

# Test service functionality
kubectl exec -n acgs-system deployment/$SERVICE_NAME -- curl -f http://localhost:8080/health

# Validate constitutional compliance
curl -X POST "http://$SERVICE_NAME:8080/api/constitutional/validate" \
  -H "constitutional-hash: cdd01ef066bc6cf2" \
  -d '{"rollback_test": true}'
```

## Infrastructure Updates

### Kubernetes Cluster Updates
```bash
# Pre-update backup
kubectl get all -n acgs-system -o yaml > /backup/acgs-system-backup-$(date +%Y%m%d%H%M%S).yaml

# Drain nodes one by one
for node in $(kubectl get nodes -o jsonpath='{.items[*].metadata.name}'); do
  echo "Draining node: $node"
  kubectl drain $node --ignore-daemonsets --delete-emptydir-data
  
  # Wait for node update (manual step)
  echo "Update node $node and press Enter when ready"
  read
  
  # Uncordon node
  kubectl uncordon $node
  
  # Verify node health
  kubectl get nodes $node
done
```

### Database Updates
```bash
# Create database backup
kubectl exec -n acgs-system deployment/postgres -- \
  pg_dump -U postgres -d acgs > /backup/acgs-db-backup-$(date +%Y%m%d%H%M%S).sql

# Update database schema
kubectl exec -n acgs-system deployment/postgres -- \
  psql -U postgres -d acgs -f /migrations/schema-update.sql

# Verify database integrity
kubectl exec -n acgs-system deployment/postgres -- \
  psql -U postgres -d acgs -c "SELECT COUNT(*) FROM constitutional_data;"
```

## Deployment Monitoring

### Real-time Monitoring
```bash
# Monitor deployment progress
watch -n 5 'kubectl get pods -n acgs-system -o wide'

# Monitor service health
watch -n 10 'kubectl get endpoints -n acgs-system'

# Monitor performance metrics
watch -n 30 'curl -s "http://monitoring-service:8014/api/metrics/performance" | jq .'
```

### Post-Deployment Monitoring
```bash
# 24-hour monitoring script
cat > /scripts/post-deployment-monitor.sh << 'EOF'
#!/bin/bash
SERVICE_NAME=$1
DURATION_HOURS=24
CHECK_INTERVAL=300  # 5 minutes

echo "Starting $DURATION_HOURS hour monitoring for $SERVICE_NAME"

for i in $(seq 1 $((DURATION_HOURS * 12))); do
  echo "=== Check $i/$((DURATION_HOURS * 12)) ==="
  
  # Health check
  kubectl exec -n acgs-system deployment/$SERVICE_NAME -- curl -f http://localhost:8080/health
  
  # Performance check
  LATENCY=$(curl -s "http://monitoring-service:8014/api/metrics/latency/$SERVICE_NAME" | jq -r .p99)
  THROUGHPUT=$(curl -s "http://monitoring-service:8014/api/metrics/throughput/$SERVICE_NAME" | jq -r .rps)
  
  echo "P99 Latency: $LATENCY ms"
  echo "Throughput: $THROUGHPUT RPS"
  
  # Constitutional compliance check
  COMPLIANCE=$(curl -s "http://monitoring-service:8014/api/metrics/compliance/$SERVICE_NAME" | jq -r .rate)
  echo "Constitutional compliance: $COMPLIANCE"
  
  sleep $CHECK_INTERVAL
done

echo "✅ $DURATION_HOURS hour monitoring completed for $SERVICE_NAME"
EOF

chmod +x /scripts/post-deployment-monitor.sh
```

## Troubleshooting Deployments

### Common Issues and Solutions

#### Pod Stuck in Pending State
```bash
# Check resource constraints
kubectl describe pod -n acgs-system <pod-name>

# Check node resources
kubectl top nodes

# Check storage
kubectl get pv,pvc -n acgs-system
```

#### ImagePullBackOff
```bash
# Check image availability
kubectl describe pod -n acgs-system <pod-name>

# Verify image registry access
kubectl exec -n acgs-system deployment/constitutional-core -- \
  docker pull acgs/constitutional-core:v1.0.0
```

#### Service Unavailable
```bash
# Check service endpoints
kubectl get endpoints -n acgs-system

# Check service selector
kubectl get service -n acgs-system -o yaml | grep -A 5 selector

# Check pod labels
kubectl get pods -n acgs-system --show-labels
```

### Deployment Validation Script
```bash
cat > /scripts/validate-deployment.sh << 'EOF'
#!/bin/bash
SERVICE_NAME=$1
EXPECTED_REPLICAS=$2

echo "Validating deployment for $SERVICE_NAME"

# Check deployment status
ACTUAL_REPLICAS=$(kubectl get deployment $SERVICE_NAME -n acgs-system -o jsonpath='{.status.readyReplicas}')
if [ "$ACTUAL_REPLICAS" -eq "$EXPECTED_REPLICAS" ]; then
  echo "✅ Replica count: $ACTUAL_REPLICAS/$EXPECTED_REPLICAS"
else
  echo "❌ Replica count: $ACTUAL_REPLICAS/$EXPECTED_REPLICAS"
  exit 1
fi

# Check pod health
kubectl get pods -n acgs-system -l app=$SERVICE_NAME

# Check service endpoints
kubectl get endpoints -n acgs-system $SERVICE_NAME

# Health check
kubectl exec -n acgs-system deployment/$SERVICE_NAME -- curl -f http://localhost:8080/health

# Constitutional compliance check
kubectl exec -n acgs-system deployment/$SERVICE_NAME -- \
  curl -H "constitutional-hash: cdd01ef066bc6cf2" http://localhost:8080/health

echo "✅ Deployment validation completed for $SERVICE_NAME"
EOF

chmod +x /scripts/validate-deployment.sh
```

## Constitutional Compliance Validation

### Deployment Compliance Checklist
```bash
# Constitutional compliance validation
cat > /scripts/constitutional-compliance-check.sh << 'EOF'
#!/bin/bash
SERVICE_NAME=$1

echo "=== Constitutional Compliance Validation ==="
echo "Service: $SERVICE_NAME"
echo "Expected Hash: cdd01ef066bc6cf2"

# Check pod labels
HASH_LABEL=$(kubectl get pods -n acgs-system -l app=$SERVICE_NAME -o jsonpath='{.items[0].metadata.labels.constitutional-hash}')
if [ "$HASH_LABEL" = "cdd01ef066bc6cf2" ]; then
  echo "✅ Pod constitutional hash label: $HASH_LABEL"
else
  echo "❌ Pod constitutional hash label: $HASH_LABEL"
  exit 1
fi

# Check service functionality
HEALTH_RESPONSE=$(kubectl exec -n acgs-system deployment/$SERVICE_NAME -- \
  curl -s -H "constitutional-hash: cdd01ef066bc6cf2" http://localhost:8080/health)

if echo "$HEALTH_RESPONSE" | grep -q "constitutional-hash.*cdd01ef066bc6cf2"; then
  echo "✅ Service constitutional compliance: Validated"
else
  echo "❌ Service constitutional compliance: Failed"
  exit 1
fi

# Check performance targets
LATENCY=$(curl -s "http://monitoring-service:8014/api/metrics/latency/$SERVICE_NAME" | jq -r .p99)
THROUGHPUT=$(curl -s "http://monitoring-service:8014/api/metrics/throughput/$SERVICE_NAME" | jq -r .rps)

if (( $(echo "$LATENCY < 5" | bc -l) )); then
  echo "✅ P99 Latency: $LATENCY ms (< 5ms)"
else
  echo "❌ P99 Latency: $LATENCY ms (>= 5ms)"
  exit 1
fi

if (( $(echo "$THROUGHPUT > 100" | bc -l) )); then
  echo "✅ Throughput: $THROUGHPUT RPS (> 100 RPS)"
else
  echo "❌ Throughput: $THROUGHPUT RPS (<= 100 RPS)"
  exit 1
fi

echo "✅ Constitutional compliance validation passed"
EOF

chmod +x /scripts/constitutional-compliance-check.sh
```

---

**Constitutional Compliance**: All deployment procedures maintain constitutional hash `cdd01ef066bc6cf2` validation and performance targets throughout the deployment lifecycle.

**Last Updated**: 2025-07-18 - Deployment procedures established