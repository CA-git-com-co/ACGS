<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

# Service Down Runbook - ACGS-1 Constitutional Governance System

## Alert: ACGSServiceDown

**Severity:** Critical  
**Component:** Service Health  
**SLA Impact:** High - Constitutional governance operations affected

## Overview

This runbook provides step-by-step procedures for responding to service down alerts in the ACGS-1 Constitutional Governance System. When a core service becomes unavailable, it can impact constitutional compliance validation, governance workflows, and system integrity.

## Immediate Response (0-5 minutes)

### 1. Alert Acknowledgment

```bash
# Acknowledge the alert to prevent escalation
curl -X POST http://localhost:8080/alerts/{alert_id}/acknowledge \
  -H "Authorization: Bearer acgs-webhook-secret-2024" \
  -d '{"acknowledged_by": "ops_team"}'
```

### 2. Quick Health Assessment

```bash
# Run comprehensive health check
cd /home/dislove/ACGS-1
python3 scripts/emergency_rollback_procedures.py health

# Check specific service status
curl -f http://localhost:800{X}/health || echo "Service on port 800{X} is down"
```

### 3. Identify Affected Service

```bash
# Check which services are down
for port in {8000..8006}; do
  echo -n "Port $port: "
  curl -s -f http://localhost:$port/health >/dev/null && echo "UP" || echo "DOWN"
done
```

## Investigation (5-15 minutes)

### 4. Check Service Logs

```bash
# Check recent logs for the affected service
tail -n 100 /home/dislove/ACGS-1/logs/{service_name}.log

# Look for error patterns
grep -i "error\|exception\|failed" /home/dislove/ACGS-1/logs/{service_name}.log | tail -20
```

### 5. Check System Resources

```bash
# Check system resources
htop
df -h
free -h
netstat -tulpn | grep :{port}
```

### 6. Check Process Status

```bash
# Check if process is running
ps aux | grep {service_name}

# Check PID files
ls -la /home/dislove/ACGS-1/pids/
```

## Automated Remediation (Parallel to Investigation)

### 7. Trigger Automated Recovery

The intelligent alerting system will automatically attempt:

1. **Health Check Validation**

   ```bash
   python3 scripts/emergency_rollback_procedures.py health
   ```

2. **Service Restart**

   ```bash
   python3 scripts/emergency_rollback_procedures.py restart
   ```

3. **Service Isolation** (if restart fails)
   ```bash
   python3 scripts/emergency_rollback_procedures.py isolate --service {service_name}
   ```

## Manual Recovery Procedures

### 8. Manual Service Restart

If automated remediation fails:

```bash
# Stop the service
pkill -f "{service_name}"

# Wait for graceful shutdown
sleep 5

# Start the service
cd /home/dislove/ACGS-1/services/core/{service_name}
nohup uvicorn app.main:app --host 0.0.0.0 --port 800{X} > /home/dislove/ACGS-1/logs/{service_name}.log 2>&1 &

# Record PID
echo $! > /home/dislove/ACGS-1/pids/{service_name}.pid
```

### 9. Database Connection Issues

If the issue is database-related:

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Restart PostgreSQL if needed (requires approval)
sudo systemctl restart postgresql

# Verify database connectivity
psql -h localhost -U acgs_user -d acgs_db -c "SELECT 1;"
```

### 10. Configuration Issues

```bash
# Validate configuration files
python3 -c "import json; json.load(open('config/{service_name}_config.json'))"

# Check environment variables
env | grep ACGS_

# Verify file permissions
ls -la /home/dislove/ACGS-1/services/core/{service_name}/
```

## Verification (15-20 minutes)

### 11. Service Health Verification

```bash
# Verify service is responding
curl -f http://localhost:800{X}/health

# Check service metrics
curl http://localhost:800{X}/metrics

# Verify constitutional compliance (for governance services)
curl http://localhost:8005/api/v1/governance/health
```

### 12. End-to-End Testing

```bash
# Run basic functionality tests
python3 scripts/comprehensive_health_check.py

# Test governance workflows (if applicable)
python3 scripts/test_governance_workflows.py
```

### 13. Performance Validation

```bash
# Check response times
time curl http://localhost:800{X}/health

# Monitor for 5 minutes
watch -n 30 'curl -s http://localhost:800{X}/health | jq .status'
```

## Escalation Procedures

### Level 1 Escalation (20 minutes)

If service cannot be restored:

- Contact: ACGS Operations Team
- Slack: #acgs-critical-alerts
- Phone: On-call rotation

### Level 2 Escalation (45 minutes)

If system-wide impact:

- Contact: Infrastructure Team Lead
- Escalate to: System Architecture Team
- Consider: Emergency maintenance window

### Level 3 Escalation (60 minutes)

If constitutional governance affected:

- Contact: Constitutional Governance Team
- Notify: Stakeholders via governance channels
- Activate: Disaster recovery procedures

## Post-Incident Actions

### 14. Incident Documentation

```bash
# Create incident report
python3 scripts/emergency_rollback_procedures.py incident \
  --type "service_failure" \
  --description "Service {service_name} was down for {duration}" \
  --severity "critical" \
  --resolution "Service restarted successfully"
```

### 15. Root Cause Analysis

- Review logs for failure patterns
- Check for resource constraints
- Analyze configuration changes
- Review deployment history

### 16. Preventive Measures

- Update monitoring thresholds
- Improve health checks
- Enhance automated recovery
- Update documentation

## Service-Specific Procedures

### Auth Service (Port 8000)

- **Impact:** User authentication disabled
- **Dependencies:** PostgreSQL, Redis
- **Special Considerations:** JWT token validation

### AC Service (Port 8001)

- **Impact:** Constitutional amendments affected
- **Dependencies:** Auth Service, PostgreSQL
- **Special Considerations:** Stakeholder notifications

### Integrity Service (Port 8002)

- **Impact:** Data integrity validation disabled
- **Dependencies:** PostgreSQL
- **Special Considerations:** Blockchain synchronization

### FV Service (Port 8003)

- **Impact:** Formal verification disabled
- **Dependencies:** Z3 solver, PostgreSQL
- **Special Considerations:** Mathematical proof validation

### GS Service (Port 8004)

- **Impact:** Governance synthesis disabled
- **Dependencies:** LLM services, PostgreSQL
- **Special Considerations:** Policy generation affected

### PGC Service (Port 8005)

- **Impact:** Constitutional compliance validation disabled
- **Dependencies:** Solana blockchain, all other services
- **Special Considerations:** Critical for governance operations

### EC Service (Port 8006)

- **Impact:** External communications disabled
- **Dependencies:** Auth Service, PostgreSQL
- **Special Considerations:** Stakeholder notifications

## Emergency Contacts

- **Primary On-Call:** ACGS Operations Team
- **Secondary:** Infrastructure Team
- **Escalation:** System Architecture Team
- **Constitutional Issues:** Governance Team

## Related Runbooks

- [High Response Time Runbook](high_response_time_runbook.md)
- [Database Issues Runbook](database_issues_runbook.md)
- [Constitutional Compliance Failure Runbook](constitutional_compliance_runbook.md)
- [Emergency Rollback Procedures](emergency_rollback_runbook.md)



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
**Owner:** ACGS Operations Team
