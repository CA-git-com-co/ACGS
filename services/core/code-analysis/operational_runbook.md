# ACGS Code Analysis Engine - Operational Runbook

## Service Information
- **Service Name**: ACGS Code Analysis Engine
- **Constitutional Hash**: cdd01ef066bc6cf2
- **Service URL**: http://localhost:8107
- **Prometheus**: http://localhost:9190
- **Grafana**: http://localhost:3100

## Health Check Procedures

### 1. Basic Health Check
```bash
curl http://localhost:8107/health
```
Expected response: HTTP 200 with constitutional_hash: cdd01ef066bc6cf2

### 2. Metrics Check
```bash
curl http://localhost:8107/metrics
```
Expected: Prometheus metrics format

### 3. Performance Check
```bash
# Check P99 latency (should be <10ms)
curl -w "@curl-format.txt" http://localhost:8107/health
```

## Troubleshooting Guide

### High Latency (P99 > 10ms)
1. Check system resources: `docker stats acgs-code-analysis-engine`
2. Review recent logs: `docker logs --tail 100 acgs-code-analysis-engine`
3. Check database connections
4. Verify cache performance

### Constitutional Compliance Violations
1. **CRITICAL**: Immediate investigation required
2. Check service logs for compliance errors
3. Verify constitutional hash in all responses
4. Escalate to security team if needed

### Service Down
1. Check container status: `docker ps | grep acgs-code-analysis-engine`
2. Restart if needed: `docker restart acgs-code-analysis-engine`
3. Check logs: `docker logs acgs-code-analysis-engine`
4. Verify dependencies (PostgreSQL, Redis, Auth Service)

### Low Throughput (<100 RPS)
1. Check resource utilization
2. Review connection pool settings
3. Analyze slow queries
4. Consider horizontal scaling

## Monitoring Checklist

### Daily Checks
- [ ] Service health status
- [ ] P99 latency < 10ms
- [ ] Constitutional compliance rate 100%
- [ ] Error rate < 1%
- [ ] Memory usage < 2GB

### Weekly Reviews
- [ ] Performance trend analysis
- [ ] Capacity planning review
- [ ] Security compliance audit
- [ ] Dependency updates check

## Emergency Contacts
- **On-call Engineer**: [Contact Information]
- **Security Team**: [Contact Information]
- **Infrastructure Team**: [Contact Information]

## Escalation Procedures
1. **Level 1**: Service degradation (>5ms P99 latency)
2. **Level 2**: Service outage or constitutional violations
3. **Level 3**: Security incidents or data breaches

Generated: 2025-07-05T09:08:38.169182
