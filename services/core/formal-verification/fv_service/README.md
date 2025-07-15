# ACGS-1 Formal Verification Service

**Status**: 🧪 **Prototype**  
**Last Updated**: 2025-06-27

## Overview

The Formal Verification (FV) Service is a critical component of the ACGS-1 system, providing enterprise-grade formal verification capabilities with mathematical proof generation. It integrates with the Z3 SMT solver to mathematically prove the correctness of policies and system behaviors, ensuring constitutional compliance through formal methods.

**Service Port**: 8003
**Service Version**: 3.0.0
**Constitutional Hash**: `cdd01ef066bc6cf2`
**Health Check**: http://localhost:8003/health

## Core Features

### Mathematical Verification

- **Z3 SMT Solver Integration**: Advanced mathematical proof capabilities for complex logical constraints
- **Formal Proof Generation**: Mathematical proofs for policy correctness and system behavior
- **Property Verification**: Safety, liveness, and constitutional compliance property checking
- **Constraint Solving**: Complex logical constraint resolution and validation
- **Theorem Proving**: Automated theorem proving for governance policies

### Cryptographic Validation

- **Digital Signature Validation**: RSA and ECDSA signature verification
- **Hash Verification**: SHA-256, SHA-512 integrity checking
- **Merkle Proof Validation**: Blockchain-style proof verification
- **Certificate Validation**: X.509 certificate chain validation
- **Cryptographic Audit Trail**: Immutable verification activity logging

### Constitutional Compliance

- **AC Service Integration**: Real-time validation against constitutional principles
- **Constitutional Hash Validation**: Verification of constitutional hash `cdd01ef066bc6cf2`
- **Compliance Scoring**: Quantitative constitutional compliance assessment
- **Violation Detection**: Real-time constitutional violation identification
- **DGM Safety Patterns**: Sandbox execution with human review and rollback capabilities

## API Endpoints

### Core Verification

- `POST /api/v1/verify/formal` - Perform formal verification with Z3 solver
- `POST /api/v1/verify/constitutional` - Constitutional compliance verification
- `POST /api/v1/verify/policy` - Policy correctness verification
- `GET /api/v1/verify/status` - Verification service status

### Proof Generation

- `POST /api/v1/verify/generate-proof` - Generate formal mathematical proof
- `POST /api/v1/verify/validate-proof` - Validate existing proof
- `GET /api/v1/verify/proof/{proof_id}` - Retrieve proof by ID
- `DELETE /api/v1/verify/proof/{proof_id}` - Delete proof

### Cryptographic Operations

- `POST /api/v1/crypto/verify-signature` - Verify digital signature
- `POST /api/v1/crypto/verify-hash` - Verify hash integrity
- `POST /api/v1/crypto/verify-merkle` - Verify Merkle proof
- `GET /api/v1/crypto/certificates` - List certificates

### Constitutional Validation

- `POST /api/v1/constitutional/validate` - Validate constitutional compliance
- `GET /api/v1/constitutional/violations` - List constitutional violations
- `GET /api/v1/constitutional/audit-log` - Constitutional audit trail
- `POST /api/v1/constitutional/emergency-shutdown` - Emergency shutdown procedure

### Health & Monitoring

- `GET /health` - Service health check
- `GET /metrics` - Prometheus metrics
- `GET /api/v1/status` - Detailed service status
- `GET /api/v1/performance` - Performance metrics

## Configuration

### Environment Variables

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/acgs_fv
REDIS_URL=redis://localhost:6379/3

# Service Configuration
SERVICE_NAME=formal-verification-service
SERVICE_VERSION=3.0.0
SERVICE_PORT=8003
APP_ENV=production
LOG_LEVEL=INFO

# Z3 Solver Configuration
Z3_TIMEOUT_MS=30000
Z3_MAX_MEMORY_MB=2048
Z3_PARALLEL_THREADS=4
Z3_PROOF_GENERATION=true

# Constitutional Governance
CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
AC_SERVICE_URL=http://localhost:8001
INTEGRITY_SERVICE_URL=http://localhost:8002

# Cryptographic Configuration
SIGNATURE_ALGORITHMS=RSA,ECDSA
HASH_ALGORITHMS=SHA256,SHA512
CERTIFICATE_VALIDATION=true
MERKLE_PROOF_VALIDATION=true

# Performance Configuration
MAX_CONCURRENT_VERIFICATIONS=10
VERIFICATION_TIMEOUT_SECONDS=300
CACHE_TTL_SECONDS=3600
ENABLE_PARALLEL_PROCESSING=true

# DGM Safety Configuration
SANDBOX_ENABLED=true
HUMAN_REVIEW_REQUIRED=true
EMERGENCY_SHUTDOWN_ENABLED=true
RTO_TARGET_MINUTES=30
```

### Resource Limits

```yaml
resources:
  requests:
    cpu: 200m
    memory: 512Mi
  limits:
    cpu: 500m
    memory: 1Gi
```

## Installation & Deployment

### Prerequisites

- Python 3.11+
- PostgreSQL 12+
- Redis 6+
- Z3 Theorem Prover 4.8+
- OpenSSL 1.1.1+

### Local Development

```bash
# 1. Install dependencies
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
uv sync

# 2. Install Z3 solver
# Ubuntu/Debian
sudo apt-get install z3

# macOS
brew install z3

# 3. Setup database
createdb acgs_fv
alembic upgrade head

# 4. Configure environment
cp config/environments/developmentconfig/environments/example.env config/environments/development.env
# Edit config/environments/development.env with your configuration

# 5. Start service
uv run uvicorn main:app --reload --port 8003
```

### Production Deployment

```bash
# Using Docker
docker build -t acgs-fv-service .
docker run -p 8003:8003 --env-file config/environments/development.env acgs-fv-service

# Using Docker Compose
docker-compose up -d fv-service

# Health check
curl http://localhost:8003/health
```

### Kubernetes Deployment

````yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fv-service
spec:
  replicas: 2
  selector:
    matchLabels:
      app: fv-service
  template:
    metadata:
      labels:
        app: fv-service
    spec:
      containers:
      - name: fv-service
        image: acgs-fv-service:latest
        ports:
        - containerPort: 8003
        resources:
          requests:
            cpu: 200m
            memory: 512Mi
          limits:
            cpu: 500m
            memory: 1Gi
        env:
        - name: CONSTITUTIONAL_HASH
          value: "cdd01ef066bc6cf2"

## Usage Examples

### Basic Formal Verification

```python
import httpx

# Verify policy compliance
async def verify_policy():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8003/api/v1/verify/formal",
            json={
                "policy_content": "All governance decisions must be constitutional",
                "constitutional_properties": [
                    "transparency",
                    "accountability",
                    "democratic_legitimacy"
                ],
                "proof_type": "constitutional_compliance"
            }
        )
        return response.json()
````

### Constitutional Compliance Check

```bash
# Check constitutional compliance
curl -X POST http://localhost:8003/api/v1/constitutional/validate \
  -H "Content-Type: application/json" \
  -d '{
    "policy_text": "New governance policy",
    "constitutional_hash": "cdd01ef066bc6cf2",
    "compliance_threshold": 0.95
  }'
```

### Generate Formal Proof

```python
# Generate mathematical proof
proof_request = {
    "property_specification": "policy_correctness(P) -> constitutional_compliance(P)",
    "policy_constraints": ["transparency", "accountability"],
    "proof_type": "safety"
}

response = await client.post(
    "http://localhost:8003/api/v1/verify/generate-proof",
    json=proof_request
)
```

## Monitoring

### Health Checks

```bash
# Basic health check
curl http://localhost:8003/health

# Detailed status
curl http://localhost:8003/api/v1/status

# Performance metrics
curl http://localhost:8003/api/v1/performance
```

### Prometheus Metrics

Key metrics exposed:

- `fv_verifications_total` - Total verification requests
- `fv_verification_duration_seconds` - Verification processing time
- `fv_constitutional_compliance_score` - Constitutional compliance scores
- `fv_z3_solver_timeouts_total` - Z3 solver timeout count
- `fv_active_verifications` - Currently active verifications

### Grafana Dashboard

Import the FV Service dashboard:

```bash
# Dashboard location
infrastructure/monitoring/grafana/dashboards/services/fv-service-dashboard.json
```

### Alerting Rules

```yaml
# Critical alerts
- alert: FVServiceDown
  expr: up{job="fv-service"} == 0
  for: 1m

- alert: HighVerificationLatency
  expr: fv_verification_duration_seconds > 30
  for: 5m

- alert: ConstitutionalComplianceBelow95
  expr: fv_constitutional_compliance_score < 0.95
  for: 2m
```

## Troubleshooting

### Common Issues

#### Z3 Solver Timeout

```bash
# Check Z3 configuration
curl http://localhost:8003/api/v1/status | jq '.z3_config'

# Increase timeout
export Z3_TIMEOUT_MS=60000

# Restart service
sudo systemctl restart fv-service
```

#### High Memory Usage

```bash
# Check memory usage
curl http://localhost:8003/metrics | grep memory

# Reduce Z3 memory limit
export Z3_MAX_MEMORY_MB=1024

# Enable garbage collection
export PYTHON_GC_ENABLED=true
```

#### Constitutional Hash Mismatch

```bash
# Verify constitutional hash
curl http://localhost:8003/api/v1/constitutional/validate | jq '.constitutional_hash'

# Expected: "cdd01ef066bc6cf2"
# Reset if corrupted
python scripts/reset_constitutional_state.py --service fv
```

#### Database Connection Issues

```bash
# Test database connectivity
python -c "import asyncpg; print('DB OK')"

# Check connection pool
curl http://localhost:8003/api/v1/status | jq '.database'

# Restart with fresh connections
sudo systemctl restart fv-service
```

### Emergency Procedures

#### Emergency Shutdown

```bash
# Immediate shutdown (< 30min RTO)
curl -X POST http://localhost:8003/api/v1/constitutional/emergency-shutdown \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Verify shutdown
curl http://localhost:8003/health
```

#### Rollback Procedure

```bash
# Rollback to previous version
kubectl rollout undo deployment/fv-service

# Verify rollback
kubectl get pods -l app=fv-service
```

## Testing

### Unit Tests

```bash
# Run unit tests
pytest tests/unit/ -v --cov=app

# Test Z3 integration
pytest tests/unit/test_z3_integration.py -v
```

### Integration Tests

```bash
# Run integration tests
pytest tests/integration/ -v

# Test AC service integration
pytest tests/integration/test_ac_integration.py -v
```

### Performance Tests

```bash
# Load testing
pytest tests/performance/test_verification_load.py -v

# Stress testing
python tests/performance/stress_test.py --concurrent=50
```

## Security

### Authentication

- **JWT Integration**: Seamless integration with ACGS-1 auth service
- **Service-to-Service**: Mutual TLS authentication
- **API Key Support**: Alternative authentication method

### Data Protection

- **Encryption at Rest**: AES-256 encryption for stored proofs
- **Encryption in Transit**: TLS 1.3 for all communications
- **Key Management**: Secure key rotation and storage

### Audit Logging

- **Comprehensive Logging**: All verification activities logged
- **Immutable Audit Trail**: Blockchain-style verification logs
- **Compliance Reporting**: Automated compliance reports

## Contributing

1. Follow ACGS-1 coding standards
2. Ensure >90% test coverage for new features
3. Update API documentation for endpoint changes
4. Test Z3 integration thoroughly
5. Validate constitutional compliance integration

## Support

- **Documentation**: [FV Service API](../../../docs/api/formal_verification_service_api.md)
- **Health Check**: http://localhost:8003/health
- **Interactive API Docs**: http://localhost:8003/docs
- **Logs**: `/logs/fv_service.log`
- **Configuration**: `services/core/formal-verification/fv_service/config/environments/development.env`

```

```
