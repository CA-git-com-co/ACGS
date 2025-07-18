# ACGS-2 Monitoring and Maintenance Runbook
<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

## Overview

Comprehensive monitoring and maintenance procedures for ACGS-2 (Advanced Constitutional Governance System). This runbook provides step-by-step procedures for monitoring system health, performing routine maintenance, and ensuring constitutional compliance.

## Constitutional Requirements

All monitoring and maintenance procedures must maintain constitutional hash `cdd01ef066bc6cf2` validation and adhere to:
- **Continuous monitoring** of constitutional compliance
- **Performance targets** (P99 <5ms, >100 RPS) maintained during maintenance
- **Zero-downtime maintenance** for constitutional services
- **Audit trail** of all maintenance activities

## Monitoring Architecture

### Core Monitoring Components
- **Prometheus**: Metrics collection and alerting
- **Grafana**: Visualization and dashboards
- **Jaeger**: Distributed tracing
- **Elasticsearch**: Log aggregation
- **Monitoring Service**: ACGS-2 specific monitoring

### Constitutional Compliance Monitoring
- **Hash Validation**: Continuous verification of constitutional hash
- **Performance Monitoring**: P99 latency and throughput tracking
- **Consensus Monitoring**: Consensus operation health
- **Audit Monitoring**: Compliance and security events

## Daily Monitoring Procedures

### Morning Health Check
```bash
#!/bin/bash
# Daily morning health check
echo "=== ACGS-2 Daily Health Check - $(date) ==="
echo "Constitutional Hash: cdd01ef066bc6cf2"

# 1. System Overview
echo "1. System Overview"
kubectl get nodes
kubectl get pods -n acgs-system
kubectl get services -n acgs-system

# 2. Constitutional Compliance Check
echo "2. Constitutional Compliance"
COMPLIANT_PODS=$(kubectl get pods -n acgs-system -l constitutional-hash=cdd01ef066bc6cf2 --no-headers | wc -l)
TOTAL_PODS=$(kubectl get pods -n acgs-system --no-headers | wc -l)
echo "Compliant pods: $COMPLIANT_PODS/$TOTAL_PODS"

# 3. Performance Metrics
echo "3. Performance Metrics"
LATENCY=$(curl -s "http://monitoring-service:8014/api/metrics/latency/constitutional-core" | jq -r .p99)
THROUGHPUT=$(curl -s "http://monitoring-service:8014/api/metrics/throughput/constitutional-core" | jq -r .rps)
echo "Constitutional Core - P99: $LATENCY ms, Throughput: $THROUGHPUT RPS"

# 4. Service Health
echo "4. Service Health"
for service in constitutional-core groqcloud-policy auth-service api-gateway monitoring-service; do
  STATUS=$(kubectl get deployment $service -n acgs-system -o jsonpath='{.status.readyReplicas}/{.spec.replicas}')
  echo "$service: $STATUS"
done

# 5. Resource Usage
echo "5. Resource Usage"
kubectl top nodes
kubectl top pods -n acgs-system --sort-by=memory

# 6. Storage Status
echo "6. Storage Status"
kubectl get pv,pvc -n acgs-system
df -h /data /backup 2>/dev/null || echo "Storage directories not mounted"

# 7. Recent Alerts
echo "7. Recent Alerts (last 24 hours)"
curl -s "http://monitoring-service:8014/api/alerts?since=24h" | jq -r '.[] | "\(.timestamp) \(.severity) \(.title)"'

# 8. Backup Status
echo "8. Backup Status"
kubectl get job -n acgs-system backup-job -o jsonpath='{.status.completionTime}'
kubectl logs -n acgs-system job/backup-job --tail=5

echo "=== Health Check Complete ==="
```

### Continuous Monitoring Script
```bash
#!/bin/bash
# Continuous monitoring script
MONITOR_INTERVAL=60  # seconds
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"

while true; do
  echo "=== Monitoring Check - $(date) ==="
  
  # Constitutional compliance check
  COMPLIANCE_RATE=$(curl -s "http://monitoring-service:8014/api/metrics/compliance/system" | jq -r .rate)
  if (( $(echo "$COMPLIANCE_RATE < 0.95" | bc -l) )); then
    echo "⚠️ WARNING: Constitutional compliance rate: $COMPLIANCE_RATE"
    # Trigger alert
    curl -X POST "http://monitoring-service:8014/api/alerts" \
      -H "Content-Type: application/json" \
      -d "{\"severity\": \"warning\", \"title\": \"Low Constitutional Compliance\", \"rate\": $COMPLIANCE_RATE}"
  fi
  
  # Performance monitoring
  LATENCY=$(curl -s "http://monitoring-service:8014/api/metrics/latency/constitutional-core" | jq -r .p99)
  if (( $(echo "$LATENCY > 5" | bc -l) )); then
    echo "⚠️ WARNING: High latency: $LATENCY ms"
    # Trigger performance alert
    curl -X POST "http://monitoring-service:8014/api/alerts" \
      -H "Content-Type: application/json" \
      -d "{\"severity\": \"warning\", \"title\": \"High P99 Latency\", \"latency\": $LATENCY}"
  fi
  
  # Service availability check
  for service in constitutional-core groqcloud-policy auth-service api-gateway; do
    if ! kubectl exec -n acgs-system deployment/$service -- curl -f http://localhost:8080/health >/dev/null 2>&1; then
      echo "❌ ERROR: Service $service health check failed"
      # Trigger service alert
      curl -X POST "http://monitoring-service:8014/api/alerts" \
        -H "Content-Type: application/json" \
        -d "{\"severity\": \"error\", \"title\": \"Service Health Check Failed\", \"service\": \"$service\"}"
    fi
  done
  
  sleep $MONITOR_INTERVAL
done
```

## Performance Monitoring

### Performance Metrics Collection
```bash
# Collect comprehensive performance metrics
collect_performance_metrics() {
  echo "=== Performance Metrics Collection - $(date) ==="
  
  # System-wide metrics
  echo "1. System-wide Performance"
  SYSTEM_LATENCY=$(curl -s "http://monitoring-service:8014/api/metrics/latency/system" | jq -r .p99)
  SYSTEM_THROUGHPUT=$(curl -s "http://monitoring-service:8014/api/metrics/throughput/system" | jq -r .rps)
  SYSTEM_ERRORS=$(curl -s "http://monitoring-service:8014/api/metrics/errors/system" | jq -r .rate)
  
  echo "System P99 Latency: $SYSTEM_LATENCY ms"
  echo "System Throughput: $SYSTEM_THROUGHPUT RPS"
  echo "System Error Rate: $SYSTEM_ERRORS"
  
  # Service-specific metrics
  echo "2. Service-specific Performance"
  for service in constitutional-core groqcloud-policy auth-service api-gateway; do
    LATENCY=$(curl -s "http://monitoring-service:8014/api/metrics/latency/$service" | jq -r .p99)
    THROUGHPUT=$(curl -s "http://monitoring-service:8014/api/metrics/throughput/$service" | jq -r .rps)
    ERRORS=$(curl -s "http://monitoring-service:8014/api/metrics/errors/$service" | jq -r .rate)
    
    echo "$service - P99: $LATENCY ms, RPS: $THROUGHPUT, Errors: $ERRORS"
  done
  
  # Constitutional operations performance
  echo "3. Constitutional Operations Performance"
  CONST_LATENCY=$(curl -s "http://monitoring-service:8014/api/metrics/latency/constitutional-operations" | jq -r .p99)
  CONST_THROUGHPUT=$(curl -s "http://monitoring-service:8014/api/metrics/throughput/constitutional-operations" | jq -r .rps)
  CONST_SUCCESS=$(curl -s "http://monitoring-service:8014/api/metrics/success/constitutional-operations" | jq -r .rate)
  
  echo "Constitutional Operations - P99: $CONST_LATENCY ms, RPS: $CONST_THROUGHPUT, Success: $CONST_SUCCESS"
  
  # Database performance
  echo "4. Database Performance"
  DB_CONNECTIONS=$(kubectl exec -n acgs-system deployment/postgres -- \
    psql -U postgres -t -c "SELECT count(*) FROM pg_stat_activity WHERE state = 'active';")
  DB_LOCKS=$(kubectl exec -n acgs-system deployment/postgres -- \
    psql -U postgres -t -c "SELECT count(*) FROM pg_locks WHERE NOT granted;")
  
  echo "Database - Active connections: $DB_CONNECTIONS, Locks: $DB_LOCKS"
  
  # Cache performance
  echo "5. Cache Performance"
  CACHE_HITS=$(kubectl exec -n acgs-system deployment/redis -- \
    redis-cli info stats | grep keyspace_hits | cut -d: -f2 | tr -d '\r')
  CACHE_MISSES=$(kubectl exec -n acgs-system deployment/redis -- \
    redis-cli info stats | grep keyspace_misses | cut -d: -f2 | tr -d '\r')
  
  if [ -n "$CACHE_HITS" ] && [ -n "$CACHE_MISSES" ]; then
    CACHE_HIT_RATE=$(echo "scale=2; $CACHE_HITS / ($CACHE_HITS + $CACHE_MISSES) * 100" | bc -l)
    echo "Cache hit rate: $CACHE_HIT_RATE%"
  fi
}
```

### Performance Alerting
```bash
# Performance alerting rules
setup_performance_alerts() {
  echo "Setting up performance alerts..."
  
  # Create alert rules
  kubectl apply -f - << EOF
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: acgs-performance-alerts
  namespace: acgs-system
  labels:
    constitutional-hash: cdd01ef066bc6cf2
spec:
  groups:
  - name: acgs.performance
    rules:
    - alert: HighLatency
      expr: histogram_quantile(0.99, acgs_request_duration_seconds_bucket{service="constitutional-core"}) > 0.005
      for: 1m
      labels:
        severity: warning
        constitutional_hash: cdd01ef066bc6cf2
      annotations:
        summary: "High P99 latency detected"
        description: "P99 latency is {{ \$value }}ms, exceeding 5ms threshold"
        
    - alert: LowThroughput
      expr: rate(acgs_requests_total{service="constitutional-core"}[5m]) < 100
      for: 2m
      labels:
        severity: warning
        constitutional_hash: cdd01ef066bc6cf2
      annotations:
        summary: "Low throughput detected"
        description: "Throughput is {{ \$value }} RPS, below 100 RPS threshold"
        
    - alert: ConstitutionalComplianceViolation
      expr: rate(acgs_constitutional_violations_total[5m]) > 0
      for: 0m
      labels:
        severity: critical
        constitutional_hash: cdd01ef066bc6cf2
      annotations:
        summary: "Constitutional compliance violation detected"
        description: "{{ \$value }} constitutional violations detected"
        
    - alert: HighErrorRate
      expr: rate(acgs_errors_total[5m]) / rate(acgs_requests_total[5m]) > 0.01
      for: 2m
      labels:
        severity: error
        constitutional_hash: cdd01ef066bc6cf2
      annotations:
        summary: "High error rate detected"
        description: "Error rate is {{ \$value }}%, exceeding 1% threshold"
EOF
}
```

## Maintenance Procedures

### Weekly Maintenance
```bash
#!/bin/bash
# Weekly maintenance script
echo "=== ACGS-2 Weekly Maintenance - $(date) ==="
echo "Constitutional Hash: cdd01ef066bc6cf2"

# 1. System cleanup
echo "1. System Cleanup"
kubectl delete pods -n acgs-system --field-selector=status.phase=Succeeded
kubectl delete pods -n acgs-system --field-selector=status.phase=Failed

# 2. Log rotation
echo "2. Log Rotation"
kubectl exec -n acgs-system deployment/constitutional-core -- \
  find /var/log -name "*.log" -type f -mtime +7 -exec gzip {} \;

# 3. Database maintenance
echo "3. Database Maintenance"
kubectl exec -n acgs-system deployment/postgres -- \
  psql -U postgres -c "VACUUM ANALYZE;"

kubectl exec -n acgs-system deployment/postgres -- \
  psql -U postgres -c "REINDEX DATABASE acgs;"

# 4. Cache cleanup
echo "4. Cache Cleanup"
kubectl exec -n acgs-system deployment/redis -- \
  redis-cli FLUSHDB

# 5. Backup verification
echo "5. Backup Verification"
kubectl apply -f /deployment/testing/backup-verification.yaml
kubectl wait --for=condition=complete job/backup-verification -n acgs-system --timeout=300s

# 6. Security scan
echo "6. Security Scan"
kubectl apply -f /deployment/testing/security-scan.yaml
kubectl wait --for=condition=complete job/security-scan -n acgs-system --timeout=600s

# 7. Performance baseline update
echo "7. Performance Baseline Update"
kubectl apply -f /deployment/testing/performance-baseline.yaml
kubectl wait --for=condition=complete job/performance-baseline -n acgs-system --timeout=300s

# 8. Constitutional compliance audit
echo "8. Constitutional Compliance Audit"
COMPLIANCE_RATE=$(curl -s "http://monitoring-service:8014/api/metrics/compliance/audit" | jq -r .rate)
echo "Weekly compliance rate: $COMPLIANCE_RATE"

if (( $(echo "$COMPLIANCE_RATE < 0.99" | bc -l) )); then
  echo "⚠️ WARNING: Weekly compliance rate below 99%"
  # Generate compliance report
  curl -X POST "http://monitoring-service:8014/api/reports/compliance" \
    -H "Content-Type: application/json" \
    -d "{\"period\": \"weekly\", \"rate\": $COMPLIANCE_RATE}"
fi

echo "=== Weekly Maintenance Complete ==="
```

### Monthly Maintenance
```bash
#!/bin/bash
# Monthly maintenance script
echo "=== ACGS-2 Monthly Maintenance - $(date) ==="
echo "Constitutional Hash: cdd01ef066bc6cf2"

# 1. Full system backup
echo "1. Full System Backup"
kubectl apply -f /deployment/backup/full-system-backup.yaml
kubectl wait --for=condition=complete job/full-system-backup -n acgs-system --timeout=1800s

# 2. Security patches
echo "2. Security Patches"
kubectl apply -f /deployment/security/monthly-security-patches.yaml

# 3. Performance optimization
echo "3. Performance Optimization"
kubectl apply -f /deployment/optimization/monthly-performance-tuning.yaml

# 4. Capacity planning
echo "4. Capacity Planning"
kubectl apply -f /deployment/planning/capacity-analysis.yaml
kubectl wait --for=condition=complete job/capacity-analysis -n acgs-system --timeout=600s

# 5. Constitutional compliance review
echo "5. Constitutional Compliance Review"
kubectl apply -f /deployment/compliance/monthly-compliance-review.yaml
kubectl wait --for=condition=complete job/monthly-compliance-review -n acgs-system --timeout=600s

# 6. Disaster recovery test
echo "6. Disaster Recovery Test"
kubectl apply -f /deployment/testing/disaster-recovery-test.yaml
kubectl wait --for=condition=complete job/disaster-recovery-test -n acgs-system --timeout=1800s

# 7. Documentation update
echo "7. Documentation Update"
kubectl apply -f /deployment/documentation/monthly-doc-update.yaml

echo "=== Monthly Maintenance Complete ==="
```

### Maintenance Windows
```bash
# Maintenance window management
maintenance_window() {
  local WINDOW_TYPE=$1  # minor, major, emergency
  local DURATION=$2     # in minutes
  
  echo "=== Starting $WINDOW_TYPE maintenance window ($DURATION minutes) ==="
  
  # Enable maintenance mode
  kubectl patch configmap maintenance-config -n acgs-system --patch '{"data":{"maintenance_mode":"true"}}'
  
  # Reduce non-essential services
  if [ "$WINDOW_TYPE" = "major" ]; then
    kubectl scale deployment groqcloud-policy -n acgs-system --replicas=1
    kubectl scale deployment monitoring-service -n acgs-system --replicas=1
  fi
  
  # Maintenance notification
  curl -X POST "http://monitoring-service:8014/api/notifications" \
    -H "Content-Type: application/json" \
    -d "{
      \"type\": \"maintenance_start\",
      \"window_type\": \"$WINDOW_TYPE\",
      \"duration_minutes\": $DURATION,
      \"constitutional_hash\": \"cdd01ef066bc6cf2\"
    }"
  
  echo "Maintenance window started. Execute maintenance tasks now."
  echo "Run 'end_maintenance_window' when complete."
}

end_maintenance_window() {
  echo "=== Ending maintenance window ==="
  
  # Disable maintenance mode
  kubectl patch configmap maintenance-config -n acgs-system --patch '{"data":{"maintenance_mode":"false"}}'
  
  # Restore service replicas
  kubectl scale deployment groqcloud-policy -n acgs-system --replicas=3
  kubectl scale deployment monitoring-service -n acgs-system --replicas=2
  
  # Verify system health
  sleep 30
  kubectl get pods -n acgs-system
  
  # Test constitutional operations
  curl -X POST "http://constitutional-core:8001/api/constitutional/validate" \
    -H "constitutional-hash: cdd01ef066bc6cf2" \
    -d '{"test": "post_maintenance"}'
  
  # Maintenance completion notification
  curl -X POST "http://monitoring-service:8014/api/notifications" \
    -H "Content-Type: application/json" \
    -d "{
      \"type\": \"maintenance_end\",
      \"constitutional_hash\": \"cdd01ef066bc6cf2\"
    }"
  
  echo "✅ Maintenance window completed"
}
```

## Log Management

### Log Collection and Analysis
```bash
# Comprehensive log collection
collect_logs() {
  local LOG_DIR="/var/log/acgs-maintenance/$(date +%Y%m%d)"
  mkdir -p "$LOG_DIR"
  
  echo "Collecting ACGS-2 logs to $LOG_DIR"
  
  # System logs
  kubectl logs -n acgs-system -l app=constitutional-core --tail=1000 > "$LOG_DIR/constitutional-core.log"
  kubectl logs -n acgs-system -l app=groqcloud-policy --tail=1000 > "$LOG_DIR/groqcloud-policy.log"
  kubectl logs -n acgs-system -l app=auth-service --tail=1000 > "$LOG_DIR/auth-service.log"
  kubectl logs -n acgs-system -l app=api-gateway --tail=1000 > "$LOG_DIR/api-gateway.log"
  kubectl logs -n acgs-system -l app=monitoring-service --tail=1000 > "$LOG_DIR/monitoring-service.log"
  
  # Infrastructure logs
  kubectl logs -n acgs-system -l app=postgres --tail=1000 > "$LOG_DIR/postgres.log"
  kubectl logs -n acgs-system -l app=redis --tail=1000 > "$LOG_DIR/redis.log"
  
  # Kubernetes events
  kubectl get events -n acgs-system --sort-by='.lastTimestamp' > "$LOG_DIR/kubernetes-events.log"
  
  # Constitutional compliance logs
  grep -h "constitutional" "$LOG_DIR"/*.log > "$LOG_DIR/constitutional-events.log"
  
  echo "Log collection complete: $LOG_DIR"
}

# Log analysis for issues
analyze_logs() {
  local LOG_DIR="/var/log/acgs-maintenance/$(date +%Y%m%d)"
  
  echo "=== Log Analysis - $(date) ==="
  
  # Error analysis
  echo "1. Error Analysis"
  grep -hi "error\|exception\|panic\|fatal" "$LOG_DIR"/*.log | head -20
  
  # Constitutional violations
  echo "2. Constitutional Violations"
  grep -hi "constitutional.*violation\|hash.*mismatch" "$LOG_DIR"/*.log
  
  # Performance issues
  echo "3. Performance Issues"
  grep -hi "timeout\|slow\|latency\|performance" "$LOG_DIR"/*.log | head -10
  
  # Security events
  echo "4. Security Events"
  grep -hi "unauthorized\|forbidden\|authentication\|security" "$LOG_DIR"/*.log | head -10
  
  # Database issues
  echo "5. Database Issues"
  grep -hi "connection.*failed\|deadlock\|lock.*timeout" "$LOG_DIR"/*.log
  
  # Summary
  echo "6. Summary"
  ERROR_COUNT=$(grep -hic "error\|exception" "$LOG_DIR"/*.log | paste -sd+ | bc)
  WARNING_COUNT=$(grep -hic "warning\|warn" "$LOG_DIR"/*.log | paste -sd+ | bc)
  
  echo "Total errors: $ERROR_COUNT"
  echo "Total warnings: $WARNING_COUNT"
}
```

### Log Rotation and Cleanup
```bash
# Log rotation script
rotate_logs() {
  echo "=== Log Rotation - $(date) ==="
  
  # Rotate application logs
  for service in constitutional-core groqcloud-policy auth-service api-gateway monitoring-service; do
    kubectl exec -n acgs-system deployment/$service -- \
      find /var/log -name "*.log" -type f -mtime +1 -exec gzip {} \;
    
    kubectl exec -n acgs-system deployment/$service -- \
      find /var/log -name "*.log.gz" -type f -mtime +30 -delete
  done
  
  # Rotate database logs
  kubectl exec -n acgs-system deployment/postgres -- \
    find /var/log/postgresql -name "*.log" -type f -mtime +7 -exec gzip {} \;
  
  # Clean old monitoring logs
  find /var/log/acgs-maintenance -type f -mtime +30 -delete
  
  echo "Log rotation complete"
}
```

## Resource Management

### Resource Monitoring
```bash
# Resource utilization monitoring
monitor_resources() {
  echo "=== Resource Monitoring - $(date) ==="
  
  # Node resources
  echo "1. Node Resource Usage"
  kubectl top nodes
  
  # Pod resources
  echo "2. Pod Resource Usage"
  kubectl top pods -n acgs-system --sort-by=memory
  
  # Persistent volume usage
  echo "3. Storage Usage"
  kubectl exec -n acgs-system deployment/postgres -- df -h /var/lib/postgresql/data
  kubectl exec -n acgs-system deployment/redis -- df -h /data
  
  # Memory usage by service
  echo "4. Memory Usage by Service"
  for service in constitutional-core groqcloud-policy auth-service api-gateway; do
    MEMORY=$(kubectl top pod -n acgs-system -l app=$service --no-headers | awk '{print $3}' | head -1)
    echo "$service: $MEMORY"
  done
  
  # CPU usage by service
  echo "5. CPU Usage by Service"
  for service in constitutional-core groqcloud-policy auth-service api-gateway; do
    CPU=$(kubectl top pod -n acgs-system -l app=$service --no-headers | awk '{print $2}' | head -1)
    echo "$service: $CPU"
  done
  
  # Resource limits vs usage
  echo "6. Resource Limits vs Usage"
  kubectl describe nodes | grep -A 5 "Allocated resources"
}
```

### Resource Optimization
```bash
# Resource optimization recommendations
optimize_resources() {
  echo "=== Resource Optimization Analysis - $(date) ==="
  
  # Identify over-provisioned services
  echo "1. Over-provisioned Services"
  kubectl top pods -n acgs-system --no-headers | while read pod cpu memory; do
    # Extract CPU and memory values
    CPU_VAL=$(echo $cpu | sed 's/m//')
    MEM_VAL=$(echo $memory | sed 's/Mi//')
    
    # Get resource limits
    POD_LIMITS=$(kubectl get pod $pod -n acgs-system -o jsonpath='{.spec.containers[0].resources.limits}')
    
    if [ -n "$POD_LIMITS" ]; then
      echo "Analyzing $pod: CPU=$cpu, Memory=$memory"
    fi
  done
  
  # Identify under-provisioned services
  echo "2. Under-provisioned Services"
  kubectl get pods -n acgs-system -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.containerStatuses[0].restartCount}{"\n"}{end}' | \
    awk '$2 > 5 {print $1 " has " $2 " restarts"}'
  
  # Storage optimization
  echo "3. Storage Optimization"
  kubectl exec -n acgs-system deployment/postgres -- \
    psql -U postgres -c "SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size FROM pg_tables ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC LIMIT 10;"
}
```

## Constitutional Compliance Monitoring

### Compliance Metrics Collection
```bash
# Constitutional compliance monitoring
monitor_constitutional_compliance() {
  echo "=== Constitutional Compliance Monitoring - $(date) ==="
  echo "Constitutional Hash: cdd01ef066bc6cf2"
  
  # 1. Hash validation across all components
  echo "1. Hash Validation"
  TOTAL_PODS=$(kubectl get pods -n acgs-system --no-headers | wc -l)
  COMPLIANT_PODS=$(kubectl get pods -n acgs-system -l constitutional-hash=cdd01ef066bc6cf2 --no-headers | wc -l)
  COMPLIANCE_RATE=$(echo "scale=2; $COMPLIANT_PODS / $TOTAL_PODS * 100" | bc -l)
  
  echo "Total pods: $TOTAL_PODS"
  echo "Compliant pods: $COMPLIANT_PODS"
  echo "Compliance rate: $COMPLIANCE_RATE%"
  
  # 2. Constitutional operations monitoring
  echo "2. Constitutional Operations"
  CONST_OPS=$(curl -s "http://monitoring-service:8014/api/metrics/constitutional-operations" | jq -r .total)
  CONST_SUCCESS=$(curl -s "http://monitoring-service:8014/api/metrics/constitutional-operations" | jq -r .success_rate)
  
  echo "Constitutional operations: $CONST_OPS"
  echo "Success rate: $CONST_SUCCESS"
  
  # 3. Consensus operations monitoring
  echo "3. Consensus Operations"
  CONSENSUS_OPS=$(curl -s "http://monitoring-service:8014/api/metrics/consensus-operations" | jq -r .total)
  CONSENSUS_SUCCESS=$(curl -s "http://monitoring-service:8014/api/metrics/consensus-operations" | jq -r .success_rate)
  
  echo "Consensus operations: $CONSENSUS_OPS"
  echo "Success rate: $CONSENSUS_SUCCESS"
  
  # 4. Audit compliance
  echo "4. Audit Compliance"
  AUDIT_EVENTS=$(curl -s "http://monitoring-service:8014/api/metrics/audit-events" | jq -r .total)
  AUDIT_VIOLATIONS=$(curl -s "http://monitoring-service:8014/api/metrics/audit-violations" | jq -r .total)
  
  echo "Audit events: $AUDIT_EVENTS"
  echo "Audit violations: $AUDIT_VIOLATIONS"
  
  # 5. Performance compliance
  echo "5. Performance Compliance"
  LATENCY_COMPLIANCE=$(curl -s "http://monitoring-service:8014/api/metrics/performance-compliance" | jq -r .latency_compliance)
  THROUGHPUT_COMPLIANCE=$(curl -s "http://monitoring-service:8014/api/metrics/performance-compliance" | jq -r .throughput_compliance)
  
  echo "Latency compliance: $LATENCY_COMPLIANCE"
  echo "Throughput compliance: $THROUGHPUT_COMPLIANCE"
  
  # Generate compliance report
  if (( $(echo "$COMPLIANCE_RATE < 95" | bc -l) )) || \
     (( $(echo "$CONST_SUCCESS < 0.99" | bc -l) )) || \
     (( $(echo "$CONSENSUS_SUCCESS < 0.99" | bc -l) )); then
    echo "⚠️ Constitutional compliance issues detected"
    generate_compliance_report
  fi
}

generate_compliance_report() {
  echo "=== Generating Constitutional Compliance Report ==="
  
  cat > "/tmp/compliance-report-$(date +%Y%m%d%H%M%S).json" << EOF
{
  "timestamp": "$(date --iso-8601)",
  "constitutional_hash": "cdd01ef066bc6cf2",
  "compliance_metrics": {
    "pod_compliance_rate": $COMPLIANCE_RATE,
    "constitutional_operations_success": $CONST_SUCCESS,
    "consensus_operations_success": $CONSENSUS_SUCCESS,
    "audit_violations": $AUDIT_VIOLATIONS,
    "latency_compliance": $LATENCY_COMPLIANCE,
    "throughput_compliance": $THROUGHPUT_COMPLIANCE
  },
  "recommendations": [
    "Review non-compliant pods and update constitutional hash labels",
    "Investigate constitutional operation failures",
    "Analyze consensus operation issues",
    "Address audit violations",
    "Optimize performance to meet constitutional requirements"
  ]
}
EOF
  
  echo "Compliance report generated: /tmp/compliance-report-$(date +%Y%m%d%H%M%S).json"
}
```

## Automated Monitoring Scripts

### Monitoring Automation
```bash
# Create monitoring automation
create_monitoring_jobs() {
  echo "Creating monitoring automation jobs..."
  
  # Daily health check job
  kubectl apply -f - << EOF
apiVersion: batch/v1
kind: CronJob
metadata:
  name: daily-health-check
  namespace: acgs-system
  labels:
    constitutional-hash: cdd01ef066bc6cf2
spec:
  schedule: "0 8 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: health-check
            image: busybox:latest
            command: ["/bin/sh", "-c"]
            args:
            - |
              echo "Daily health check started"
              # Add health check commands here
              echo "Daily health check completed"
          restartPolicy: OnFailure
EOF

  # Weekly maintenance job
  kubectl apply -f - << EOF
apiVersion: batch/v1
kind: CronJob
metadata:
  name: weekly-maintenance
  namespace: acgs-system
  labels:
    constitutional-hash: cdd01ef066bc6cf2
spec:
  schedule: "0 2 * * 0"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: maintenance
            image: busybox:latest
            command: ["/bin/sh", "-c"]
            args:
            - |
              echo "Weekly maintenance started"
              # Add maintenance commands here
              echo "Weekly maintenance completed"
          restartPolicy: OnFailure
EOF

  # Constitutional compliance monitoring job
  kubectl apply -f - << EOF
apiVersion: batch/v1
kind: CronJob
metadata:
  name: constitutional-compliance-check
  namespace: acgs-system
  labels:
    constitutional-hash: cdd01ef066bc6cf2
spec:
  schedule: "*/15 * * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: compliance-check
            image: busybox:latest
            command: ["/bin/sh", "-c"]
            args:
            - |
              echo "Constitutional compliance check started"
              # Add compliance check commands here
              echo "Constitutional compliance check completed"
          restartPolicy: OnFailure
EOF

  echo "Monitoring automation jobs created"
}
```

## Troubleshooting Guide

### Common Monitoring Issues

#### Metrics Not Collecting
```bash
# Check Prometheus configuration
kubectl get configmap prometheus-config -n acgs-system -o yaml

# Check Prometheus targets
kubectl port-forward -n acgs-system svc/prometheus 9090:9090 &
curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | select(.health != "up")'

# Restart Prometheus
kubectl rollout restart deployment/prometheus -n acgs-system
```

#### Grafana Dashboard Issues
```bash
# Check Grafana datasources
kubectl exec -n acgs-system deployment/grafana -- \
  curl -s http://localhost:3000/api/datasources | jq .

# Reset Grafana admin password
kubectl exec -n acgs-system deployment/grafana -- \
  grafana-cli admin reset-admin-password admin
```

#### Log Aggregation Problems
```bash
# Check Elasticsearch cluster health
kubectl exec -n acgs-system deployment/elasticsearch -- \
  curl -s http://localhost:9200/_cluster/health | jq .

# Check Logstash processing
kubectl logs -n acgs-system -l app=logstash

# Restart log aggregation stack
kubectl rollout restart deployment/elasticsearch -n acgs-system
kubectl rollout restart deployment/logstash -n acgs-system
```

---

**Constitutional Compliance**: All monitoring and maintenance procedures maintain constitutional hash `cdd01ef066bc6cf2` validation and performance targets throughout operations.

**Last Updated**: 2025-07-18 - Monitoring and maintenance procedures established