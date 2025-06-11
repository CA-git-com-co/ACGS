# ACGS-1 FV and GS Service Restoration Commands

## 1. Make Scripts Executable
```bash
chmod +x scripts/start_missing_services.sh
chmod +x scripts/validate_fv_gs_restoration.sh
```

## 2. Execute Enhanced Service Restoration Script
```bash
./scripts/start_missing_services.sh
```

## 3. Verify Service Restoration Using Health Checks
```bash
# Quick health check for both services
curl -s http://localhost:8003/health | jq .
curl -s http://localhost:8004/health | jq .

# Alternative without jq
curl -s http://localhost:8003/health
curl -s http://localhost:8004/health
```

## 4. Run Comprehensive Validation Script
```bash
./scripts/validate_fv_gs_restoration.sh
```

## 5. Check Service Logs for Startup Errors/Warnings
```bash
# Check FV service logs
tail -f logs/fv_service.log

# Check GS service logs  
tail -f logs/gs_service.log

# Check for recent errors in both logs
grep -i "error\|exception\|failed" logs/fv_service.log | tail -10
grep -i "error\|exception\|failed" logs/gs_service.log | tail -10
```

## 6. Confirm Constitutional Compliance Validation Workflows
```bash
# Test FV enterprise verification capabilities
curl -s http://localhost:8003/api/v1/enterprise/status | jq .

# Test GS synthesis capabilities
curl -s http://localhost:8004/api/v1/status | jq .

# Test FV performance metrics
curl -s http://localhost:8003/api/v1/performance/metrics | jq .

# Test GS performance metrics
curl -s http://localhost:8004/api/v1/performance | jq .
```

## 7. Verify PID Management
```bash
# Check if PID files exist and processes are running
ls -la pids/fv_service.pid pids/gs_service.pid

# Verify processes are actually running
ps aux | grep -E "(fv_service|gs_service)" | grep -v grep
```

## 8. Test Constitutional Governance Workflows
```bash
# Test FV cryptographic validation endpoint
curl -X POST http://localhost:8003/api/v1/crypto/validate-signature \
  -H "Content-Type: application/json" \
  -d '{"data":"test_policy","signature":"test_sig_123","public_key":"test_key_456"}'

# Test GS root endpoint for governance capabilities
curl -s http://localhost:8004/ | jq .governance_workflows
```

## Success Criteria Validation

### ✅ Services Respond to HTTP Health Checks
- FV Service (port 8003): `curl -f http://localhost:8003/health`
- GS Service (port 8004): `curl -f http://localhost:8004/health`

### ✅ Services are Properly Logged and PID-Tracked
- Log files: `logs/fv_service.log`, `logs/gs_service.log`
- PID files: `pids/fv_service.pid`, `pids/gs_service.pid`

### ✅ Constitutional Governance Workflows Operational
- FV enterprise endpoints accessible
- GS synthesis endpoints accessible
- Performance metrics available

### ✅ Integration with ACGS-1 Service Management
- Host-based deployment architecture maintained
- Compatible with existing service management patterns
- Enhanced error handling and status reporting

## Troubleshooting Commands

### If Services Fail to Start:
```bash
# Check system dependencies
pg_isready -h localhost -p 5432
redis-cli ping

# Check virtual environment
source venv/bin/activate
python --version

# Manual service restart
cd services/core/formal-verification/fv_service
source /home/dislove/ACGS-1/venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8003

cd /home/dislove/ACGS-1/services/core/governance-synthesis/gs_service
source /home/dislove/ACGS-1/venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8004
```

### If Health Checks Fail:
```bash
# Check if ports are in use
netstat -tlnp | grep -E ":800[34]"

# Check for conflicting processes
ps aux | grep uvicorn | grep -E "800[34]"

# Kill conflicting processes
pkill -f "uvicorn.*:8003"
pkill -f "uvicorn.*:8004"
```

## Expected Output Indicators

### Successful Restoration:
- ✅ "MISSION ACCOMPLISHED: Both FV and GS services are operational!"
- ✅ "Constitutional governance workflows are now available for validation"
- ✅ HTTP 200 responses from health endpoints
- ✅ Valid JSON responses from status endpoints

### Partial Success:
- ⚠️ "PARTIAL SUCCESS: Some critical services are operational, others need attention"
- ⚠️ One service responding, one service failing

### Failure Indicators:
- ❌ "MISSION FAILED: Critical services could not be restored"
- ❌ Connection refused errors from curl commands
- ❌ Missing or invalid PID files
- ❌ Error messages in service logs
