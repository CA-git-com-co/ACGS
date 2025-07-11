# Constitutional Middleware Rollback Plan
**Constitutional Hash: cdd01ef066bc6cf2**

## Overview
This document provides a comprehensive rollback procedure for the FastConstitutionalValidator middleware integration in case of validation failures, performance degradation, or constitutional compliance violations.

## Pre-Rollback Assessment

### 1. Identify the Issue
Before initiating rollback, determine the specific issue:

```bash
# Check service health
curl -f http://localhost:8001/health
curl -f http://localhost:8002/health
curl -f http://localhost:8005/health

# Check constitutional compliance metrics
curl http://localhost:9090/api/v1/query?query=acgs_constitutional_compliance_failures_total

# Check performance metrics
curl http://localhost:9090/api/v1/query?query=acgs_fast_constitutional_validation_seconds
```

### 2. Validate Current State
```bash
# Check current middleware version
grep -r "FastConstitutionalValidator" services/shared/middleware/
git log --oneline -10 services/shared/middleware/constitutional_validation.py

# Verify constitutional hash consistency
grep -r "cdd01ef066bc6cf2" services/shared/middleware/
```

## Rollback Procedures

### Option 1: Git Revert (Recommended)

#### Step 1: Identify Commit Hash
```bash
# Find the middleware integration commit
git log --oneline services/shared/middleware/constitutional_validation.py | head -5

# Example output:
# abc1234 Integrate FastConstitutionalValidator with constitutional middleware
# def5678 Previous working version
```

#### Step 2: Create Rollback Branch
```bash
# Create rollback branch
git checkout -b rollback-constitutional-middleware-$(date +%Y%m%d)

# Revert the integration commit
git revert <commit-hash>  # Replace with actual commit hash

# Example:
# git revert abc1234
```

#### Step 3: Validate Rollback
```bash
# Check that old middleware is restored
grep -A 10 "_validate_request_headers" services/shared/middleware/constitutional_validation.py

# Ensure constitutional hash is still present
grep "cdd01ef066bc6cf2" services/shared/middleware/constitutional_validation.py
```

### Option 2: File-Level Rollback

#### Step 1: Backup Current State
```bash
# Backup current middleware
cp services/shared/middleware/constitutional_validation.py \
   services/shared/middleware/constitutional_validation.py.rollback.$(date +%Y%m%d_%H%M%S)

# Backup fast validator
cp services/shared/middleware/fast_constitutional_validator.py \
   services/shared/middleware/fast_constitutional_validator.py.rollback.$(date +%Y%m%d_%H%M%S)
```

#### Step 2: Restore Previous Version
```bash
# Restore from git history
git checkout HEAD~1 -- services/shared/middleware/constitutional_validation.py

# Or restore from backup if available
# cp services/shared/middleware/constitutional_validation.py.backup \
#    services/shared/middleware/constitutional_validation.py
```

### Option 3: Emergency Bypass

#### Step 1: Disable Strict Validation
```bash
# Edit middleware to disable strict validation temporarily
sed -i 's/enable_strict_validation=True/enable_strict_validation=False/g' \
    services/shared/middleware/constitutional_validation.py
```

#### Step 2: Restart Services
```bash
# Restart all ACGS services
docker-compose restart auth-service
docker-compose restart ai-service  
docker-compose restart coordination-service
docker-compose restart integrity-service
docker-compose restart rules-engine
```

## Service Restart Procedures

### 1. Graceful Restart (Recommended)
```bash
# Stop services gracefully
docker-compose stop auth-service ai-service coordination-service integrity-service rules-engine

# Wait for connections to drain (30 seconds)
sleep 30

# Start services
docker-compose start auth-service ai-service coordination-service integrity-service rules-engine

# Verify startup
docker-compose ps
```

### 2. Rolling Restart
```bash
# Restart one service at a time
for service in auth-service ai-service coordination-service integrity-service rules-engine; do
    echo "Restarting $service..."
    docker-compose restart $service
    sleep 10
    
    # Verify service health
    docker-compose exec $service curl -f http://localhost:8000/health || echo "Health check failed for $service"
done
```

### 3. Emergency Restart
```bash
# Force restart all services
docker-compose down
docker-compose up -d

# Check logs for errors
docker-compose logs --tail=50 auth-service
docker-compose logs --tail=50 ai-service
docker-compose logs --tail=50 coordination-service
```

## Constitutional Compliance Validation

### 1. Immediate Validation
```bash
# Test constitutional hash validation
curl -X POST http://localhost:8001/test \
  -H "Content-Type: application/json" \
  -H "X-Constitutional-Hash: cdd01ef066bc6cf2" \
  -d '{"constitutional_hash": "cdd01ef066bc6cf2", "test": "data"}'

# Expected: 200 OK with constitutional headers
```

### 2. Comprehensive Validation
```bash
# Run constitutional compliance test suite
python tests/constitutional/test_compliance_validation.py

# Run performance validation
python tests/performance/constitutional_validation_test.py --target-time 5.0

# Check metrics
curl http://localhost:9090/api/v1/query?query=acgs_constitutional_compliance_failures_total
```

### 3. Load Testing Validation
```bash
# Run load test to ensure system stability
python tests/performance/load_test.py --duration 60 --rps 50

# Monitor for constitutional violations
watch -n 1 'curl -s http://localhost:9090/api/v1/query?query=acgs_constitutional_hash_violations_total'
```

## Monitoring and Alerting

### 1. Set Up Rollback Monitoring
```bash
# Create temporary alert rules for rollback monitoring
cat > /tmp/rollback_alerts.yml << 'EOF'
groups:
- name: constitutional_rollback
  rules:
  - alert: ConstitutionalComplianceFailure
    expr: increase(acgs_constitutional_compliance_failures_total[5m]) > 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Constitutional compliance failure detected during rollback"
      
  - alert: MiddlewarePerformanceDegradation
    expr: histogram_quantile(0.99, acgs_constitutional_validation_seconds) > 0.005
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "Middleware performance degraded after rollback"
EOF

# Load alert rules
curl -X POST http://localhost:9090/api/v1/admin/tsdb/delete_series?match[]=acgs_constitutional_compliance_failures_total
```

### 2. Dashboard Monitoring
```bash
# Key metrics to monitor during rollback:
# - Constitutional compliance rate (should be 100%)
# - Middleware response time (should be <5ms)
# - Service availability (should be >99%)
# - Error rates (should be <1%)

# Access Grafana dashboard
echo "Monitor rollback at: http://localhost:3000/d/constitutional-middleware"
```

## Validation Checklist

### Pre-Rollback
- [ ] Issue clearly identified and documented
- [ ] Rollback branch created
- [ ] Current state backed up
- [ ] Stakeholders notified

### During Rollback
- [ ] Rollback method selected and executed
- [ ] Services restarted successfully
- [ ] Constitutional hash validation working
- [ ] No constitutional compliance violations
- [ ] Performance within acceptable limits

### Post-Rollback
- [ ] All services healthy and responding
- [ ] Constitutional compliance at 100%
- [ ] Performance metrics stable
- [ ] Load testing passed
- [ ] Monitoring alerts configured
- [ ] Incident documented
- [ ] Root cause analysis initiated

## Emergency Contacts

### Technical Escalation
- **Primary**: ACGS System Administrator
- **Secondary**: Constitutional Compliance Officer
- **Emergency**: Infrastructure Team Lead

### Communication
- **Slack**: #acgs-incidents
- **Email**: acgs-alerts@organization.com
- **Phone**: Emergency hotline (if configured)

## Recovery Validation

### 1. Functional Testing
```bash
# Test all critical endpoints
curl -f http://localhost:8001/health
curl -f http://localhost:8002/health
curl -f http://localhost:8005/health
curl -f http://localhost:8008/health
curl -f http://localhost:8016/health

# Test constitutional validation
python tests/constitutional/test_full_compliance.py
```

### 2. Performance Testing
```bash
# Validate performance is acceptable
python tests/performance/constitutional_validation_test.py --target-time 5.0

# Run sustained load test
python tests/performance/load_test.py --duration 300 --rps 100
```

### 3. Constitutional Compliance Audit
```bash
# Full compliance audit
python scripts/constitutional_audit.py --hash cdd01ef066bc6cf2

# Generate compliance report
python scripts/generate_compliance_report.py --output rollback_compliance_$(date +%Y%m%d).json
```

## Documentation Updates

After successful rollback:

1. **Update incident log** with rollback details
2. **Document lessons learned** for future improvements
3. **Update rollback procedures** based on experience
4. **Schedule post-incident review** within 48 hours
5. **Update monitoring** to prevent similar issues

## Success Criteria

Rollback is considered successful when:

- ✅ All services are healthy and responding
- ✅ Constitutional compliance rate is 100%
- ✅ Performance is within acceptable limits (<5ms P99)
- ✅ No constitutional hash violations detected
- ✅ Load testing passes without errors
- ✅ Monitoring shows stable metrics for 30+ minutes

**HASH-OK:cdd01ef066bc6cf2**

---

*This rollback plan ensures constitutional compliance is maintained throughout the rollback process while minimizing service disruption.*
