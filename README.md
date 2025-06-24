# ACGS-PGP System Documentation

## System Overview

The ACGS-PGP (Autonomous Constitutional Governance System - Policy Generation Platform) is a 7-service microservices architecture implementing constitutional AI governance with quantum-inspired semantic fault tolerance and DGM (Darwin Gödel Machine) safety patterns.

**Constitutional Hash**: `cdd01ef066bc6cf2`
**System Version**: 3.0.0
**Last Updated**: 2025-06-24
**Architecture**: ACGS-1 Lite with Constitutional AI Constraints

## Core Service Architecture

| Service | Port | Purpose | Status | Health Check |
|---------|------|---------|--------|--------------|
| **auth-service** | 8000 | Authentication & Authorization with MFA | ✅ Operational | http://localhost:8000/health |
| **ac-service** | 8001 | Constitutional AI Management & Compliance | ✅ Operational | http://localhost:8001/health |
| **integrity-service** | 8002 | Cryptographic Integrity & PGP Assurance | ✅ Operational | http://localhost:8002/health |
| **fv-service** | 8003 | Formal Verification & Policy Validation | ✅ Operational | http://localhost:8003/health |
| **gs-service** | 8004 | Governance Synthesis & Policy Generation | ✅ Operational | http://localhost:8004/health |
| **pgc-service** | 8005 | Policy Governance Compiler & Enforcement | ⚠️ Degraded | http://localhost:8005/health |
| **ec-service** | 8006 | Evolutionary Computation & WINA Oversight | ✅ Operational | http://localhost:8006/health |

## AI Model Integrations

### Production AI Models
- **Google Gemini** (2.0 Flash, 2.5 Pro) - Constitutional analysis and policy synthesis
- **DeepSeek-R1** - Advanced reasoning and formal verification support
- **NVIDIA Qwen** - Multi-model consensus and governance workflows
- **Nano-vLLM** - Lightweight inference with GPU/CPU fallback

### Performance Metrics

- **Response Time Target**: ≤2s P99 (Current: 1.1s P99)
- **Constitutional Compliance**: >95% (Current: >95%)
- **System Throughput**: 61 requests/second
- **Overall Success Rate**: 83.3%
- **Emergency Shutdown**: <30min RTO capability

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 12+
- Redis 6+
- Docker & Docker Compose
- OPA (Open Policy Agent) for PGC service

### Deployment

```bash
# 1. Start all services
./scripts/start_all_services.sh

# 2. Verify service health
for port in 8000 8001 8002 8003 8004 8005 8006; do
  echo "Port $port: $(curl -s http://localhost:$port/health | jq -r '.status // .service // "UNKNOWN"')"
done

# 3. Run system validation
python scripts/comprehensive_system_validation.py

# 4. Load testing (optional)
cd scripts && python load_test_acgs_pgp.py --concurrent 15
```

### Individual Service Management

```bash
# Start specific service
./scripts/manage_<service>_service.sh start

# Check service logs
tail -f logs/<service>_service.log

# Restart service
./scripts/manage_<service>_service.sh restart
```

## Security & Compliance

### Security Hardening ✅
- **Shell Injection Protection**: Subprocess vulnerabilities patched
- **Cryptographic Upgrade**: MD5 → SHA-256 migration complete
- **Security Headers**: CORS, CSP, and security middleware applied
- **Rate Limiting**: Per-endpoint and global rate limits
- **Input Validation**: Comprehensive validation middleware
- **Authentication**: JWT with MFA support

### Constitutional Compliance
- **DGM Safety Patterns**: Sandbox + human review + rollback
- **Constitutional Hash Validation**: `cdd01ef066bc6cf2`
- **Compliance Monitoring**: Real-time constitutional violation detection
- **Emergency Procedures**: <30min RTO with automated rollback

## Resource Configuration

### Standard Resource Limits
All services use consistent resource allocation:
- **CPU Request**: 200m
- **CPU Limit**: 500m
- **Memory Request**: 512Mi
- **Memory Limit**: 1Gi

### Configuration Management
- **Shared Config**: `/config/shared/` - Common service configurations
- **Environment Config**: `/config/environments/` - Environment-specific settings
- **Service Config**: `/config/services/` - Individual service configurations
- **Security Config**: `/config/security/` - Security policies and settings

## Troubleshooting

### Common Issues

#### PGC Service Degraded ⚠️
**Issue**: PGC service requires OPA (Open Policy Agent) on port 8181

**Resolution**:
```bash
# Install OPA
curl -L -o opa https://openpolicyagent.org/downloads/v0.58.0/opa_linux_amd64_static
chmod +x opa
sudo mv opa /usr/local/bin/

# Start OPA server
opa run --server --addr localhost:8181 &

# Verify OPA is running
curl http://localhost:8181/health
```

#### Service Startup Issues
**Issue**: Services fail to start due to dependency issues

**Resolution**:
```bash
# Check database connectivity
pg_isready -h localhost -p 5432

# Check Redis connectivity
redis-cli ping

# Restart services in dependency order
./scripts/restart_services_with_pgbouncer.sh
```

#### Constitutional Compliance Failures
**Issue**: Constitutional hash validation failures

**Resolution**:
```bash
# Verify constitutional hash
echo "Expected: cdd01ef066bc6cf2"
curl -s http://localhost:8001/api/v1/constitutional/validate | jq -r '.constitutional_hash'

# Reset constitutional state if needed
python scripts/fix_constitutional_compliance_auth.py
```

## Monitoring & Observability

### Monitoring Stack
- **Prometheus**: http://localhost:9090 - Metrics collection
- **Grafana**: http://localhost:3000 - Dashboards and visualization
- **Health Endpoints**: All services expose `/health` and `/metrics`
- **Log Aggregation**: Centralized logging in `/logs/` directory

### Key Metrics
- **Constitutional Compliance Score**: Target >0.8
- **Response Time P99**: Target <2s
- **Service Availability**: Target >99.9%
- **Error Rate**: Target <1%

### Alerting
- **Critical Alerts**: Constitutional violations, service failures
- **Warning Alerts**: Performance degradation, resource limits
- **Info Alerts**: Deployment events, configuration changes

## Emergency Procedures

### Emergency Shutdown
```bash
# Immediate shutdown (< 30min RTO)
./scripts/emergency_rollback.py --immediate

# Graceful shutdown
./scripts/emergency_rollback.py --graceful
```

### Disaster Recovery
```bash
# Backup current state
./scripts/backup_system.py --full

# Restore from backup
./scripts/restore_database.sh <backup_timestamp>
```

## Documentation & Support

### Documentation Structure
- **[API Documentation](docs/API_SPECIFICATIONS.md)** - Complete API reference
- **[Architecture Guide](docs/architecture/system_architecture.md)** - System design
- **[Deployment Guide](docs/deployment/DEPLOYMENT_QUICK_START_GUIDE.md)** - Step-by-step deployment
- **[Operational Runbook](docs/OPERATIONAL_RUNBOOK.md)** - Production operations
- **[Security Guide](docs/security/SECURITY_POSTURE_ASSESSMENT.md)** - Security procedures

### Getting Help
1. **Service Logs**: Check `/logs/<service>_service.log`
2. **Health Checks**: Verify all service `/health` endpoints
3. **Configuration**: Review `/config/shared/` and service-specific configs
4. **Monitoring**: Check Grafana dashboards for system metrics
5. **Emergency**: Follow emergency procedures above

### Development Resources
- **Service READMEs**: Individual service documentation in `services/*/README.md`
- **API Testing**: Interactive docs at `http://localhost:<port>/docs`
- **Code Examples**: See `docs/tutorials/` for usage examples
