# ACGS-2 Incident Response Runbook
<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

## Overview

Comprehensive incident response procedures for ACGS-2 (Advanced Constitutional Governance System). This runbook provides step-by-step procedures for handling system incidents while maintaining constitutional compliance and operational continuity.

## Constitutional Requirements

All incident response procedures must maintain constitutional hash `cdd01ef066bc6cf2` validation and adhere to:
- **Recovery Time Objective (RTO)**: <15 minutes for constitutional services
- **Recovery Point Objective (RPO)**: <5 minutes data loss tolerance
- **Performance Targets**: P99 <5ms, >100 RPS during and after recovery
- **Compliance Maintenance**: Constitutional hash validation throughout incident response

## Incident Classification

### Severity Levels

#### SEV-1 (Critical)
- **Constitutional core service unavailable**
- **Complete system outage**
- **Security breach or constitutional violation**
- **Data corruption or loss**
- **Performance degradation >50% from baseline**

#### SEV-2 (High)
- **Single service unavailable**
- **Partial functionality impacted**
- **Authentication/authorization issues**
- **External API integration failures**
- **Database connection issues**

#### SEV-3 (Medium)
- **Non-critical service degradation**
- **Monitoring/logging issues**
- **Performance issues <25% degradation**
- **Configuration drift**
- **Capacity planning concerns**

#### SEV-4 (Low)
- **Documentation issues**
- **Non-urgent security patches**
- **Cosmetic issues**
- **Feature requests**

## Incident Response Process

### Phase 1: Detection & Assessment (0-5 minutes)

#### 1.1 Incident Detection
```bash
# Check system health dashboard
kubectl get pods -n acgs-system
kubectl get services -n acgs-system
kubectl get ingress -n acgs-system

# Check constitutional compliance
kubectl get pods -n acgs-system -l constitutional-hash=cdd01ef066bc6cf2

# Check monitoring alerts
curl -s "http://monitoring-service:8014/api/alerts/active" | jq .
```

#### 1.2 Initial Assessment
```bash
# Check service availability
for service in constitutional-core groqcloud-policy auth-service api-gateway; do
  echo "=== $service ==="
  kubectl get pods -n acgs-system -l app=$service
  kubectl logs -n acgs-system -l app=$service --tail=50
done

# Check database connectivity
kubectl exec -n acgs-system deployment/constitutional-core -- \
  pg_isready -h postgres -p 5432

# Check cache connectivity
kubectl exec -n acgs-system deployment/constitutional-core -- \
  redis-cli -h redis ping
```

#### 1.3 Severity Classification
```bash
# Constitutional service check
CONSTITUTIONAL_STATUS=$(kubectl get pods -n acgs-system -l app=constitutional-core -o jsonpath='{.items[0].status.phase}')

if [ "$CONSTITUTIONAL_STATUS" != "Running" ]; then
  echo "SEV-1: Constitutional core service down"
  SEVERITY="SEV-1"
elif [ "$(kubectl get pods -n acgs-system --field-selector=status.phase!=Running | wc -l)" -gt 3 ]; then
  echo "SEV-2: Multiple services impacted"
  SEVERITY="SEV-2"
else
  echo "SEV-3: Limited impact"
  SEVERITY="SEV-3"
fi
```

### Phase 2: Containment & Mitigation (5-15 minutes)

#### 2.1 Immediate Containment
```bash
# For SEV-1 incidents - Emergency procedures
if [ "$SEVERITY" = "SEV-1" ]; then
  echo "=== EXECUTING SEV-1 EMERGENCY PROCEDURES ==="
  
  # Enable emergency maintenance mode
  kubectl patch configmap emergency-config -n acgs-system --patch '{"data":{"maintenance_mode":"true"}}'
  
  # Scale up healthy services
  kubectl scale deployment constitutional-core -n acgs-system --replicas=5
  kubectl scale deployment groqcloud-policy -n acgs-system --replicas=3
  
  # Redirect traffic to healthy nodes
  kubectl patch service constitutional-core -n acgs-system --patch '{"spec":{"selector":{"health":"healthy"}}}'
fi
```

#### 2.2 Service Recovery
```bash
# Restart failed pods
kubectl delete pods -n acgs-system --field-selector=status.phase=Failed

# Check for stuck pods
kubectl get pods -n acgs-system --field-selector=status.phase=Pending
kubectl describe pods -n acgs-system --field-selector=status.phase=Pending

# Force restart if needed
kubectl rollout restart deployment/constitutional-core -n acgs-system
kubectl rollout status deployment/constitutional-core -n acgs-system
```

#### 2.3 Database Recovery
```bash
# Check database health
kubectl exec -n acgs-system deployment/postgres -- \
  psql -U postgres -c "SELECT version();"

# Check for locks
kubectl exec -n acgs-system deployment/postgres -- \
  psql -U postgres -c "SELECT * FROM pg_locks WHERE NOT granted;"

# Check replication status
kubectl exec -n acgs-system deployment/postgres -- \
  psql -U postgres -c "SELECT * FROM pg_stat_replication;"

# Recovery from backup if needed
if [ "$DATABASE_CORRUPTED" = "true" ]; then
  echo "=== INITIATING DATABASE RECOVERY ==="
  kubectl exec -n acgs-system deployment/postgres -- \
    /scripts/restore_from_backup.sh --latest --validate-constitutional-hash
fi
```

### Phase 3: Communication & Escalation (Ongoing)

#### 3.1 Incident Communication
```bash
# Create incident record
INCIDENT_ID="ACGS-$(date +%Y%m%d%H%M%S)"
echo "Incident ID: $INCIDENT_ID"

# Notify stakeholders
curl -X POST "http://monitoring-service:8014/api/incidents" \
  -H "Content-Type: application/json" \
  -H "constitutional-hash: cdd01ef066bc6cf2" \
  -d "{
    \"incident_id\": \"$INCIDENT_ID\",
    \"severity\": \"$SEVERITY\",
    \"title\": \"System Incident\",
    \"description\": \"Incident details\",
    \"status\": \"investigating\"
  }"
```

#### 3.2 Escalation Matrix
```bash
# SEV-1 Escalation
if [ "$SEVERITY" = "SEV-1" ]; then
  # Immediate escalation to on-call engineer
  curl -X POST "https://api.pagerduty.com/incidents" \
    -H "Authorization: Token $PAGERDUTY_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
      \"incident\": {
        \"type\": \"incident\",
        \"title\": \"ACGS-2 SEV-1 Incident: $INCIDENT_ID\",
        \"service\": {\"id\": \"$ACGS_SERVICE_ID\", \"type\": \"service_reference\"},
        \"urgency\": \"high\"
      }
    }"
fi
```

### Phase 4: Investigation & Root Cause Analysis (15-60 minutes)

#### 4.1 Log Analysis
```bash
# Collect system logs
mkdir -p /tmp/incident-logs/$INCIDENT_ID
kubectl logs -n acgs-system -l app=constitutional-core --previous > /tmp/incident-logs/$INCIDENT_ID/constitutional-core.log
kubectl logs -n acgs-system -l app=groqcloud-policy --previous > /tmp/incident-logs/$INCIDENT_ID/groqcloud-policy.log
kubectl logs -n acgs-system -l app=auth-service --previous > /tmp/incident-logs/$INCIDENT_ID/auth-service.log

# Analyze error patterns
grep -i "error\|exception\|panic\|fatal" /tmp/incident-logs/$INCIDENT_ID/*.log

# Check constitutional compliance violations
grep -i "constitutional.*violation\|hash.*mismatch" /tmp/incident-logs/$INCIDENT_ID/*.log
```

#### 4.2 Performance Analysis
```bash
# Check resource utilization
kubectl top nodes
kubectl top pods -n acgs-system

# Check metrics
curl -s "http://monitoring-service:8014/api/metrics/system" | jq .
curl -s "http://monitoring-service:8014/api/metrics/performance" | jq .

# Check distributed tracing
curl -s "http://jaeger-query.jaeger-system:16686/api/traces?service=constitutional-core&limit=10" | jq .
```

#### 4.3 External Dependencies
```bash
# Check external API connectivity
kubectl exec -n acgs-system deployment/groqcloud-policy -- \
  curl -s -o /dev/null -w "%{http_code}" "https://api.groq.com/health"

kubectl exec -n acgs-system deployment/groqcloud-policy -- \
  curl -s -o /dev/null -w "%{http_code}" "https://api.openai.com/v1/models"

# Check network connectivity
kubectl exec -n acgs-system deployment/constitutional-core -- \
  nslookup postgres

kubectl exec -n acgs-system deployment/constitutional-core -- \
  nslookup redis
```

### Phase 5: Recovery & Validation (30-120 minutes)

#### 5.1 Service Recovery
```bash
# Systematic service restart
services=("postgres" "redis" "constitutional-core" "groqcloud-policy" "auth-service" "api-gateway")

for service in "${services[@]}"; do
  echo "=== Recovering $service ==="
  kubectl rollout restart deployment/$service -n acgs-system
  kubectl rollout status deployment/$service -n acgs-system --timeout=300s
  
  # Validate service health
  kubectl exec -n acgs-system deployment/$service -- curl -f http://localhost:8080/health || echo "Warning: $service health check failed"
done
```

#### 5.2 Constitutional Compliance Validation
```bash
# Validate constitutional hash
kubectl get pods -n acgs-system -o jsonpath='{.items[*].metadata.labels.constitutional-hash}' | grep -c "cdd01ef066bc6cf2"

# Test constitutional operations
curl -X POST "http://constitutional-core:8001/api/constitutional/validate" \
  -H "Content-Type: application/json" \
  -H "constitutional-hash: cdd01ef066bc6cf2" \
  -d '{"operation": "test_recovery"}'

# Validate consensus functionality
curl -X POST "http://constitutional-core:8001/api/consensus/test" \
  -H "constitutional-hash: cdd01ef066bc6cf2"
```

#### 5.3 Performance Validation
```bash
# Run performance tests
kubectl apply -f /deployment/testing/performance/constitutional_performance_suite.yaml
kubectl wait --for=condition=complete job/performance-test -n acgs-system --timeout=300s

# Check P99 latency
LATENCY=$(curl -s "http://monitoring-service:8014/api/metrics/latency/p99" | jq -r .value)
if (( $(echo "$LATENCY > 5" | bc -l) )); then
  echo "WARNING: P99 latency ($LATENCY ms) exceeds constitutional requirement (5ms)"
fi

# Check throughput
THROUGHPUT=$(curl -s "http://monitoring-service:8014/api/metrics/throughput" | jq -r .value)
if (( $(echo "$THROUGHPUT < 100" | bc -l) )); then
  echo "WARNING: Throughput ($THROUGHPUT RPS) below constitutional requirement (100 RPS)"
fi
```

### Phase 6: Post-Incident Activities (1-24 hours)

#### 6.1 System Stabilization
```bash
# Monitor system stability
for i in {1..30}; do
  echo "=== Stability Check $i/30 ==="
  kubectl get pods -n acgs-system --field-selector=status.phase!=Running
  if [ $? -eq 0 ]; then
    echo "System stable at $(date)"
  else
    echo "System unstable at $(date)"
  fi
  sleep 60
done
```

#### 6.2 Incident Documentation
```bash
# Generate incident report
cat > /tmp/incident-report-$INCIDENT_ID.md << EOF
# ACGS-2 Incident Report
**Incident ID**: $INCIDENT_ID
**Severity**: $SEVERITY
**Date**: $(date)
**Duration**: $INCIDENT_DURATION
**Constitutional Hash**: cdd01ef066bc6cf2

## Summary
Brief description of the incident.

## Timeline
- Detection: $(date)
- Mitigation: $(date)
- Resolution: $(date)

## Root Cause
Detailed analysis of the root cause.

## Impact
- Services affected: 
- Constitutional compliance: Maintained/Violated
- Performance impact: 
- User impact: 

## Resolution
Steps taken to resolve the incident.

## Lessons Learned
- What went well:
- What could be improved:
- Action items:

## Constitutional Compliance
- Hash validation: ✅/❌
- Performance targets: ✅/❌
- Recovery objectives: ✅/❌
EOF
```

#### 6.3 Post-Incident Review
```bash
# Schedule post-incident review
curl -X POST "http://monitoring-service:8014/api/incidents/$INCIDENT_ID/review" \
  -H "Content-Type: application/json" \
  -H "constitutional-hash: cdd01ef066bc6cf2" \
  -d "{
    \"review_date\": \"$(date -d '+1 day' --iso-8601)\",
    \"attendees\": [\"ops-team\", \"dev-team\", \"security-team\"],
    \"agenda\": [\"timeline-review\", \"root-cause-analysis\", \"action-items\"]
  }"
```

## Common Incident Scenarios

### Constitutional Core Service Failure

#### Symptoms
- Constitutional validation API returning 500 errors
- Constitutional hash validation failures
- Consensus operations failing

#### Diagnosis
```bash
# Check constitutional core logs
kubectl logs -n acgs-system -l app=constitutional-core --tail=100

# Check database connectivity
kubectl exec -n acgs-system deployment/constitutional-core -- \
  psql -h postgres -U postgres -c "SELECT 1"

# Check constitutional data integrity
kubectl exec -n acgs-system deployment/constitutional-core -- \
  python3 -c "
import hashlib
# Verify constitutional hash
expected_hash = 'cdd01ef066bc6cf2'
print(f'Expected hash: {expected_hash}')
"
```

#### Recovery
```bash
# Restart constitutional core service
kubectl rollout restart deployment/constitutional-core -n acgs-system

# Validate constitutional hash after restart
kubectl exec -n acgs-system deployment/constitutional-core -- \
  curl -f http://localhost:8001/health

# Test constitutional operations
curl -X POST "http://constitutional-core:8001/api/constitutional/validate" \
  -H "constitutional-hash: cdd01ef066bc6cf2" \
  -d '{"test": "recovery"}'
```

### Database Connection Issues

#### Symptoms
- Database connection timeouts
- Service pods in CrashLoopBackOff
- Data inconsistency errors

#### Diagnosis
```bash
# Check database pods
kubectl get pods -n acgs-system -l app=postgres

# Check database logs
kubectl logs -n acgs-system -l app=postgres --tail=50

# Check connection pool
kubectl exec -n acgs-system deployment/postgres -- \
  psql -U postgres -c "SELECT * FROM pg_stat_activity;"
```

#### Recovery
```bash
# Restart database service
kubectl rollout restart deployment/postgres -n acgs-system

# Check database recovery
kubectl exec -n acgs-system deployment/postgres -- \
  psql -U postgres -c "SELECT version();"

# Restart dependent services
for service in constitutional-core groqcloud-policy auth-service; do
  kubectl rollout restart deployment/$service -n acgs-system
done
```

### External API Failures

#### Symptoms
- GroqCloud or OpenAI API timeouts
- HTTP 429 (rate limit) errors
- Authentication failures

#### Diagnosis
```bash
# Check external API connectivity
kubectl exec -n acgs-system deployment/groqcloud-policy -- \
  curl -v "https://api.groq.com/health"

# Check API rate limits
kubectl logs -n acgs-system -l app=groqcloud-policy | grep -i "rate\|limit\|429"

# Check authentication
kubectl exec -n acgs-system deployment/groqcloud-policy -- \
  env | grep -i "API_KEY\|TOKEN"
```

#### Recovery
```bash
# Implement circuit breaker
kubectl patch deployment groqcloud-policy -n acgs-system --patch '
{
  "spec": {
    "template": {
      "spec": {
        "containers": [{
          "name": "groqcloud-policy",
          "env": [{
            "name": "CIRCUIT_BREAKER_ENABLED",
            "value": "true"
          }]
        }]
      }
    }
  }
}'

# Scale down to reduce API load
kubectl scale deployment groqcloud-policy -n acgs-system --replicas=1
```

### Performance Degradation

#### Symptoms
- P99 latency >5ms
- Throughput <100 RPS
- High CPU/memory usage

#### Diagnosis
```bash
# Check resource usage
kubectl top pods -n acgs-system
kubectl top nodes

# Check performance metrics
curl -s "http://monitoring-service:8014/api/metrics/performance" | jq .

# Check distributed tracing
curl -s "http://jaeger-query.jaeger-system:16686/api/traces?service=constitutional-core&limit=10" | jq .
```

#### Recovery
```bash
# Scale up services
kubectl scale deployment constitutional-core -n acgs-system --replicas=5
kubectl scale deployment groqcloud-policy -n acgs-system --replicas=3

# Optimize resource limits
kubectl patch deployment constitutional-core -n acgs-system --patch '
{
  "spec": {
    "template": {
      "spec": {
        "containers": [{
          "name": "constitutional-core",
          "resources": {
            "limits": {"cpu": "2000m", "memory": "4Gi"},
            "requests": {"cpu": "1000m", "memory": "2Gi"}
          }
        }]
      }
    }
  }
}'
```

## Emergency Contacts

### Escalation Path
1. **Level 1**: On-call Engineer
2. **Level 2**: Senior SRE
3. **Level 3**: Engineering Manager
4. **Level 4**: CTO

### Contact Information
- **Emergency Hotline**: +1-555-ACGS-911
- **Slack Channel**: #acgs-incidents
- **Email**: incidents@acgs.local
- **PagerDuty**: https://acgs.pagerduty.com

## Tools and Resources

### Monitoring URLs
- **System Dashboard**: http://monitoring-service:8014/dashboard
- **Jaeger Tracing**: http://jaeger-query.jaeger-system:16686
- **Grafana**: http://grafana:3000/dashboards/acgs
- **Prometheus**: http://prometheus:9090

### Common Commands
```bash
# Quick system health check
kubectl get pods -n acgs-system -o wide

# View all logs
kubectl logs -n acgs-system --all-containers=true -f

# Emergency shutdown
kubectl scale deployment --all -n acgs-system --replicas=0

# Emergency startup
kubectl scale deployment --all -n acgs-system --replicas=1
```

### Constitutional Compliance Checklist
- [ ] Constitutional hash validation active
- [ ] Performance targets met (P99 <5ms, >100 RPS)
- [ ] All services reporting healthy
- [ ] Consensus operations functional
- [ ] Audit logs capturing all actions
- [ ] Security policies enforced
- [ ] Backup systems operational

---

**Constitutional Compliance**: All incident response procedures maintain constitutional hash `cdd01ef066bc6cf2` validation and performance targets throughout recovery operations.

**Last Updated**: 2025-07-18 - Incident response procedures established