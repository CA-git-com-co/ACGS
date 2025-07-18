<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

# High Response Time Runbook - ACGS-1 Constitutional Governance System

## Alert: HighResponseTime / ACGSHighResponseTime

**Severity:** Warning/High  
**Component:** Performance  
**SLA Impact:** Medium - User experience degraded

## Overview

This runbook addresses high response time alerts in the ACGS-1 Constitutional Governance System. Response times exceeding 500ms (warning) or 2s (critical) can impact user experience and constitutional governance operations.

## Target Performance Metrics

- **Target Response Time:** <500ms for 95% of requests
- **Critical Threshold:** >2s response time
- **SLA Requirement:** <500ms for constitutional compliance operations

## Immediate Response (0-5 minutes)

### 1. Alert Acknowledgment

```bash
# Acknowledge the alert
curl -X POST http://localhost:8080/alerts/{alert_id}/acknowledge \
  -H "Authorization: Bearer acgs-webhook-secret-2024"
```

### 2. Quick Performance Check

```bash
# Check current response times for all services
for port in {8000..8006}; do
  echo -n "Port $port: "
  time curl -s http://localhost:$port/health >/dev/null
done

# Check system load
uptime
top -bn1 | head -20
```

### 3. Identify Affected Service

```bash
# Check which service is experiencing high response times
curl -s http://localhost:9090/api/v1/query?query='http_request_duration_seconds{quantile="0.95"}' | jq .
```

## Investigation (5-15 minutes)

### 4. System Resource Analysis

```bash
# CPU usage
top -bn1 | grep "Cpu(s)"
ps aux --sort=-%cpu | head -10

# Memory usage
free -h
ps aux --sort=-%mem | head -10

# Disk I/O
iostat -x 1 5
df -h

# Network
netstat -i
ss -tuln | grep :80
```

### 5. Database Performance Check

```bash
# Check PostgreSQL performance
sudo -u postgres psql -c "
SELECT query, calls, total_time, mean_time, rows
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;"

# Check active connections
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"

# Check for long-running queries
sudo -u postgres psql -c "
SELECT pid, now() - pg_stat_activity.query_start AS duration, query
FROM pg_stat_activity
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';"
```

### 6. Application-Level Analysis

```bash
# Check service logs for errors
for service in auth ac integrity fv gs pgc ec; do
  echo "=== $service service ==="
  tail -n 50 /home/dislove/ACGS-1/logs/${service}_service.log | grep -i "error\|slow\|timeout"
done

# Check for memory leaks
ps aux | grep uvicorn | awk '{print $2, $4, $6}' # PID, %MEM, VSZ
```

### 7. Cache Performance

```bash
# Check Redis performance
redis-cli info stats | grep -E "keyspace_hits|keyspace_misses|used_memory"
redis-cli info replication
redis-cli slowlog get 10
```

## Automated Remediation

### 8. Intelligent Alerting Response

The system will automatically attempt:

1. **Health Check Validation**
2. **Cache Clearing** (if memory pressure detected)
3. **Service Scaling** (if load is high)
4. **Database Connection Pool Reset**

## Manual Performance Optimization

### 9. Immediate Performance Fixes

#### Clear Application Caches

```bash
# Clear Redis cache
redis-cli FLUSHALL

# Restart services to clear memory leaks
python3 /home/dislove/ACGS-1/scripts/emergency_rollback_procedures.py restart
```

#### Database Optimization

```bash
# Analyze and vacuum database
sudo -u postgres psql acgs_db -c "ANALYZE;"
sudo -u postgres psql acgs_db -c "VACUUM ANALYZE;"

# Check for missing indexes
sudo -u postgres psql acgs_db -c "
SELECT schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats
WHERE schemaname = 'public'
ORDER BY n_distinct DESC;"
```

#### Service-Specific Optimizations

**Auth Service (Port 8000)**

```bash
# Check JWT token cache
curl http://localhost:8000/metrics | grep jwt_cache

# Restart if memory leak suspected
pkill -f "auth_service"
cd /home/dislove/ACGS-1/services/core/auth_service
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 &
```

**GS Service (Port 8004) - LLM Performance**

```bash
# Check LLM response times
curl http://localhost:8004/metrics | grep llm_response_time

# Check model loading status
curl http://localhost:8004/api/v1/models/status
```

**PGC Service (Port 8005) - Blockchain Performance**

```bash
# Check Solana RPC response times
curl http://localhost:8006/metrics | grep solana_rpc_time

# Verify blockchain connectivity
curl http://localhost:8006/api/v1/blockchain/health
```

### 10. Load Balancing and Scaling

#### Horizontal Scaling

```bash
# Scale critical services
docker-compose up --scale gs_service=2 --scale pgc_service=2

# Check load distribution
curl http://localhost:9090/api/v1/query?query='rate(http_requests_total[5m])'
```

#### Connection Pool Tuning

```bash
# Increase database connection pool
# Edit service configurations to increase max_connections
sed -i 's/max_connections=10/max_connections=20/g' /home/dislove/ACGS-1/config/*_config.json
```

## Performance Monitoring

### 11. Real-Time Monitoring

```bash
# Monitor response times in real-time
watch -n 5 'curl -s http://localhost:9090/api/v1/query?query="http_request_duration_seconds{quantile=\"0.95\"}" | jq ".data.result[].value[1]"'

# Monitor system resources
watch -n 2 'echo "=== CPU ===" && top -bn1 | head -5 && echo "=== Memory ===" && free -h && echo "=== Load ===" && uptime'
```

### 12. Performance Baseline Establishment

```bash
# Run performance test
python3 /home/dislove/ACGS-1/scripts/performance_test.py --duration 300 --concurrent 10

# Generate performance report
python3 /home/dislove/ACGS-1/scripts/performance_optimization.py --report
```

## Service-Specific Performance Tuning

### Auth Service Performance

- **Common Issues:** JWT validation overhead, database connection pool exhaustion
- **Solutions:** Increase connection pool, implement JWT caching
- **Monitoring:** `auth_jwt_validation_time`, `auth_db_connection_pool_usage`

### AC Service Performance

- **Common Issues:** Large amendment document processing, stakeholder notification delays
- **Solutions:** Implement document chunking, async notifications
- **Monitoring:** `ac_document_processing_time`, `ac_notification_queue_size`

### Integrity Service Performance

- **Common Issues:** Hash computation overhead, large data validation
- **Solutions:** Parallel hash computation, data streaming
- **Monitoring:** `integrity_hash_computation_time`, `integrity_validation_queue`

### FV Service Performance

- **Common Issues:** Z3 solver timeout, complex proof generation
- **Solutions:** Proof caching, solver timeout tuning
- **Monitoring:** `fv_proof_generation_time`, `fv_solver_timeout_rate`

### GS Service Performance

- **Common Issues:** LLM response delays, policy synthesis complexity
- **Solutions:** Model caching, request batching
- **Monitoring:** `gs_llm_response_time`, `gs_policy_synthesis_duration`

### PGC Service Performance

- **Common Issues:** Blockchain RPC delays, compliance validation overhead
- **Solutions:** RPC connection pooling, validation caching
- **Monitoring:** `pgc_blockchain_rpc_time`, `pgc_compliance_validation_time`

### EC Service Performance

- **Common Issues:** External API timeouts, notification delivery delays
- **Solutions:** Async processing, retry mechanisms
- **Monitoring:** `ec_external_api_time`, `ec_notification_delivery_time`

## Escalation Procedures

### Level 1 Escalation (15 minutes)

- **Trigger:** Response times >2s for >15 minutes
- **Action:** Contact Performance Engineering Team
- **Channels:** #acgs-performance-alerts

### Level 2 Escalation (30 minutes)

- **Trigger:** System-wide performance degradation
- **Action:** Engage Infrastructure Team
- **Channels:** #acgs-critical-alerts, On-call rotation

### Level 3 Escalation (45 minutes)

- **Trigger:** Constitutional governance operations affected
- **Action:** Emergency performance optimization
- **Channels:** Emergency response team, Stakeholder notifications

## Post-Incident Actions

### 13. Performance Analysis

```bash
# Generate detailed performance report
python3 /home/dislove/ACGS-1/scripts/performance_analysis.py \
  --start-time "2024-01-01T10:00:00" \
  --end-time "2024-01-01T11:00:00" \
  --output performance_incident_report.json
```

### 14. Capacity Planning

- Review resource utilization trends
- Update performance baselines
- Plan infrastructure scaling
- Update monitoring thresholds

### 15. Preventive Measures

- Implement performance regression testing
- Enhance monitoring coverage
- Update performance SLAs
- Schedule regular performance reviews

## Performance Optimization Checklist

- [ ] System resources within normal ranges
- [ ] Database queries optimized
- [ ] Cache hit rates >90%
- [ ] No memory leaks detected
- [ ] Connection pools properly sized
- [ ] Load balancing configured
- [ ] Monitoring thresholds updated
- [ ] Performance baselines established

## Related Runbooks

- [Service Down Runbook](service_down_runbook.md)
- [Database Issues Runbook](database_issues_runbook.md)
- [Memory Issues Runbook](database_issues_runbook.md)
- [Load Balancing Runbook](../grafana/dashboards/infrastructure/load-balancing-dashboard.json)



## Implementation Status

- ✅ **Constitutional Hash Validation**: Active enforcement of `cdd01ef066bc6cf2`
- 🔄 **Performance Monitoring**: Continuous validation of targets
- ✅ **Documentation Standards**: Compliant with ACGS-2 requirements
- 🔄 **Cross-Reference Validation**: Ongoing link integrity maintenance

**Overall Status**: 🔄 IN PROGRESS - Systematic enhancement implementation

## Performance Targets

This component maintains the following performance requirements:

- **P99 Latency**: <5ms (constitutional requirement)
- **Throughput**: >100 RPS (minimum operational standard)
- **Cache Hit Rate**: >85% (efficiency requirement)
- **Constitutional Compliance**: 100% (hash: cdd01ef066bc6cf2)

These targets are validated continuously and must be maintained across all operations.

---

**Last Updated:** 2024-01-01  
**Version:** 1.0  
**Owner:** ACGS Performance Engineering Team
