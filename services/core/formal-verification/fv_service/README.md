# ACGS-1 Formal Verification Service

## Overview

The Formal Verification (FV) Service is a **prototype implementation** of a formal verification system for policies and constitutional compliance validation. This service provides basic verification capabilities with plans for advanced SMT solver integration.

**Implementation Status**: 🧪 **Prototype**
**Service Port**: 8003
**Service Version**: 2.0.0
**Constitutional Hash**: `cdd01ef066bc6cf2`
**Health Check**: http://localhost:8003/health

## ⚠️ Prototype Limitations

**Current Implementation Status**:
- ✅ Basic formal verification endpoints implemented
- ✅ Content validation and threat detection functional
- ✅ Constitutional compliance checking operational
- ⚠️ **Z3 SMT solver integration incomplete** (mock implementation)
- ⚠️ **Mathematical proof generation uses simulated data**
- ⚠️ **Advanced verification algorithms not fully implemented**
- ⚠️ **Some endpoints return mock/demonstration data**

**Production Readiness**: This service requires completion of Z3 integration and advanced algorithm implementation before production deployment.

## Implemented Features

### ✅ Functional Capabilities
- **Basic Content Validation**: Threat detection and security pattern analysis
- **Constitutional Compliance Checking**: Basic compliance validation against principles
- **Cryptographic Validation**: Mock digital signature verification
- **Audit Trail**: Simulated blockchain-style audit logging
- **Health Monitoring**: Service health and status endpoints
- **Performance Metrics**: Basic performance monitoring

### 🧪 Prototype Features (Limited Implementation)
- **Z3 SMT Solver Integration**: ⚠️ Mock implementation, not fully functional
- **Mathematical Proof Generation**: ⚠️ Simulated proofs, not real theorem proving
- **Advanced Verification**: ⚠️ Basic algorithms, advanced features incomplete
- **Parallel Processing**: ⚠️ Framework exists but not optimized
- **Blockchain Audit**: ⚠️ In-memory simulation, not persistent

### 📋 Planned Features (Not Yet Implemented)
- **Production Z3 Integration**: Real SMT solver integration
- **Advanced Theorem Proving**: Complete mathematical proof generation
- **Temporal Logic Verification**: Time-based property verification
- **Datalog Reasoning**: Logic programming for policy analysis
- **Enterprise Performance**: Sub-500ms response times with real optimization

## API Endpoints

### Core Verification
- `POST /api/v1/verify` - Submit policies for formal verification
- `POST /api/v1/verify/parallel` - Parallel policy verification (100+ concurrent)
- `POST /api/v1/verify/constitutional-compliance` - Constitutional compliance verification
- `POST /api/v1/verify/generate-formal-proof` - Generate mathematical proofs
- `GET /api/v1/verify/verification-metrics` - Performance and success metrics

### Constitutional Verification
- `POST /api/v1/constitutional-compliance` - Z3-based constitutional verification
- `POST /api/v1/generate-formal-proof` - Formal proof generation with Z3
- `GET /api/v1/constitutional/properties` - Available constitutional properties
- `POST /api/v1/constitutional/validate` - Validate against constitutional principles

### Bias and Fairness Analysis
- `POST /api/v1/verify/bias-detection` - Detect bias in policies
- `GET /api/v1/bias-metrics` - Available bias detection metrics
- `GET /api/v1/fairness-properties` - Available fairness properties
- `POST /api/v1/fairness/analyze` - Comprehensive fairness analysis

### Cross-Domain Testing
- `POST /api/v1/cross-domain-testing` - Multi-domain policy testing
- `GET /api/v1/cross-domain/domains` - Available testing domains
- `POST /api/v1/cross-domain/validate` - Cross-domain validation

### Performance and Monitoring
- `GET /api/v1/enterprise/status` - Enterprise verification capabilities
- `GET /api/v1/performance/metrics` - Performance optimization metrics
- `GET /api/v1/verification/status/{task_id}` - Verification task status
- `GET /api/v1/cache/stats` - Verification cache statistics

### System Management
- `GET /health` - Service health with component status
- `GET /metrics` - Prometheus metrics for monitoring
- `GET /` - Service information and capabilities

## Configuration

### Environment Variables

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/acgs_formal_verification
REDIS_URL=redis://localhost:6379/3

# Service Configuration
SERVICE_NAME=fv-service
SERVICE_VERSION=2.0.0
SERVICE_PORT=8003
APP_ENV=production
LOG_LEVEL=INFO

# Z3 SMT Solver Configuration
Z3_TIMEOUT_MS=30000
MAX_PROOF_STEPS=1000
ENABLE_PARALLEL_VERIFICATION=true
MAX_CONCURRENT_VERIFICATIONS=100

# Constitutional Governance
CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
CONSTITUTIONAL_COMPLIANCE_THRESHOLD=0.8
ENABLE_CONSTITUTIONAL_VERIFICATION=true

# Service Integration
AC_SERVICE_URL=http://localhost:8001
INTEGRITY_SERVICE_URL=http://localhost:8002
AUTH_SERVICE_URL=http://localhost:8000

# Performance Configuration
ENABLE_VERIFICATION_CACHE=true
CACHE_SIZE_MB=1024
ENABLE_PERFORMANCE_OPTIMIZATION=true
TARGET_RESPONSE_TIME_MS=500

# Security Configuration
ENABLE_CRYPTOGRAPHIC_VALIDATION=true
ENABLE_BLOCKCHAIN_AUDIT=true
ENABLE_BIAS_DETECTION=true
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
- Z3 SMT Solver 4.8+
- Mathematical libraries (NumPy, SciPy)

### Local Development

```bash
# 1. Install dependencies
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
uv sync

# Alternative: Traditional pip
pip install -r requirements.txt

# 2. Install Z3 SMT Solver
# Ubuntu/Debian
sudo apt-get install z3

# macOS
brew install z3

# Python Z3 bindings
pip install z3-solver

# 3. Setup database
createdb acgs_formal_verification
alembic upgrade head

# 4. Configure environment
cp .env.example .env
# Edit .env with your configuration

# 5. Start service
uv run uvicorn main:app --reload --port 8003
```

### Production Deployment

```bash
# Using Docker
docker build -t acgs-fv-service .
docker run -p 8003:8003 --env-file .env acgs-fv-service

# Using systemd
sudo cp fv-service.service /etc/systemd/system/
sudo systemctl enable fv-service
sudo systemctl start fv-service
```

## Testing

### Unit Tests
```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=app --cov-report=html
```

### Integration Tests
```bash
# Test Z3 integration
uv run pytest tests/test_z3_integration.py -v

# Test constitutional verification
uv run pytest tests/test_constitutional_verification.py -v

# Test parallel verification
uv run pytest tests/test_parallel_verification.py -v
```

### Verification Tests
```bash
# Test formal proof generation
python scripts/test_formal_proofs.py

# Test bias detection
python scripts/test_bias_detection.py

# Performance testing
python scripts/test_verification_performance.py --concurrent 50
```

## Usage Examples

### Basic Policy Verification

```python
import httpx

async def verify_policy():
    async with httpx.AsyncClient() as client:
        # Submit policy for formal verification
        response = await client.post(
            "http://localhost:8003/api/v1/verify",
            json={
                "policy_rule_refs": ["policy_123"],
                "verification_level": "comprehensive",
                "constitutional_principles": [
                    "democratic_process",
                    "transparency",
                    "accountability"
                ],
                "safety_properties": [
                    "no_unauthorized_access",
                    "data_integrity_maintained"
                ]
            },
            headers={"Authorization": f"Bearer {access_token}"}
        )

        result = response.json()
        return {
            "verification_status": result["verification_status"],
            "mathematical_proof": result["mathematical_proof"],
            "constitutional_compliance": result["constitutional_compliance"]
        }
```

### Constitutional Compliance Verification

```python
async def verify_constitutional_compliance():
    async with httpx.AsyncClient() as client:
        # Verify constitutional compliance with Z3 proofs
        response = await client.post(
            "http://localhost:8003/api/v1/verify/constitutional-compliance",
            json={
                "policy_content": "Citizens have the right to privacy",
                "constitutional_principles": [
                    "privacy_rights",
                    "individual_liberty",
                    "constitutional_supremacy"
                ],
                "verification_level": "formal_proof",
                "generate_proof": True
            },
            headers={"Authorization": f"Bearer {access_token}"}
        )

        result = response.json()
        return {
            "compliant": result["verification_result"]["compliant"],
            "confidence_score": result["verification_result"]["confidence"],
            "formal_proof": result["formal_proof"],
            "constitutional_hash": result["constitutional_hash"]
        }
```

### Parallel Verification

```python
async def parallel_policy_verification():
    async with httpx.AsyncClient() as client:
        # Submit multiple policies for parallel verification
        response = await client.post(
            "http://localhost:8003/api/v1/verify/parallel",
            json={
                "policy_rule_refs": [
                    "policy_001", "policy_002", "policy_003",
                    "policy_004", "policy_005"
                ],
                "enable_parallel": True,
                "max_concurrent": 10,
                "verification_level": "comprehensive",
                "constitutional_principles": ["fairness", "transparency"]
            },
            headers={"Authorization": f"Bearer {access_token}"}
        )

        result = response.json()
        return {
            "batch_verification_id": result["verification_id"],
            "parallel_results": result["parallel_results"],
            "overall_compliance": result["overall_compliance"]
        }
```

### Bias Detection Analysis

```python
async def detect_policy_bias():
    async with httpx.AsyncClient() as client:
        # Analyze policy for bias and fairness issues
        response = await client.post(
            "http://localhost:8003/api/v1/verify/bias-detection",
            json={
                "policy_content": "Hiring policy for technical positions",
                "protected_attributes": ["gender", "race", "age"],
                "bias_metrics": [
                    "demographic_parity",
                    "equalized_odds",
                    "individual_fairness"
                ],
                "fairness_threshold": 0.1
            },
            headers={"Authorization": f"Bearer {access_token}"}
        )

        result = response.json()
        return {
            "bias_detected": result["bias_analysis"]["bias_detected"],
            "fairness_score": result["bias_analysis"]["fairness_score"],
            "bias_metrics": result["bias_analysis"]["detailed_metrics"],
            "recommendations": result["bias_analysis"]["recommendations"]
        }
```

## Z3 SMT Solver Integration

### Formal Proof Generation
The service uses Z3 SMT solver for mathematical proof generation:

```python
# Example Z3 integration for constitutional verification
import z3

def generate_constitutional_proof(policy_constraints, constitutional_properties):
    solver = z3.Solver()
    solver.set("timeout", 30000)  # 30 second timeout

    # Convert policy constraints to Z3 formulas
    for constraint in policy_constraints:
        formula = convert_to_z3_formula(constraint)
        solver.add(formula)

    # Verify constitutional properties
    for prop in constitutional_properties:
        property_formula = convert_to_z3_formula(prop)
        solver.push()
        solver.add(z3.Not(property_formula))

        if solver.check() == z3.unsat:
            # Property is provable
            proof_steps = generate_proof_steps(solver.proof())
            return {"status": "proven", "proof": proof_steps}
        else:
            return {"status": "unprovable", "counterexample": solver.model()}
```

### Constitutional Hash Validation
```python
# Constitutional hash validation in formal verification
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

def validate_constitutional_integrity(verification_result):
    computed_hash = hashlib.sha256(
        f"{verification_result['policy_content']}"
        f"{verification_result['constitutional_principles']}"
        f"{verification_result['verification_timestamp']}"
    ).hexdigest()[:16]

    return computed_hash == CONSTITUTIONAL_HASH
```

## Monitoring & Observability

### Health Checks
```bash
# Service health with component status
curl http://localhost:8003/health

# Expected response includes Z3 solver status
{
  "status": "healthy",
  "service": "enhanced_fv_service",
  "version": "2.0.0",
  "components": {
    "z3_smt_solver": "operational",
    "tiered_validation": "operational",
    "parallel_pipeline": "operational",
    "cryptographic_validation": "operational"
  }
}
```

### Performance Metrics
```bash
# Get performance metrics
curl http://localhost:8003/api/v1/performance/metrics

# Verification metrics
curl http://localhost:8003/api/v1/verification-metrics
```

### Real-time Monitoring
```bash
# Monitor verification tasks
curl http://localhost:8003/api/v1/verification/status/{task_id}

# Cache performance
curl http://localhost:8003/api/v1/cache/stats
```

## Troubleshooting

### Common Issues

#### Z3 SMT Solver Not Available
```bash
# Check Z3 installation
python -c "import z3; print('Z3 version:', z3.get_version_string())"

# Install Z3 if missing
pip install z3-solver

# Ubuntu/Debian system installation
sudo apt-get install z3

# Verify Z3 service integration
curl http://localhost:8003/health | jq '.components.z3_smt_solver'
```

#### Verification Timeout Issues
```bash
# Check Z3 timeout configuration
grep "Z3_TIMEOUT_MS" .env

# Increase timeout for complex proofs
export Z3_TIMEOUT_MS=60000  # 60 seconds

# Monitor verification performance
curl http://localhost:8003/api/v1/performance/metrics | jq '.current_metrics.average_response_time_ms'
```

#### Constitutional Hash Mismatch
```bash
# Verify constitutional hash
curl http://localhost:8003/api/v1/verify/constitutional-compliance \
  -H "Content-Type: application/json" \
  -d '{"policy_content": "test"}' | jq '.constitutional_hash'

# Expected: "cdd01ef066bc6cf2"
# Reset if corrupted
python scripts/reset_constitutional_state.py --service fv
```

#### Parallel Verification Failures
```bash
# Check concurrent verification limits
curl http://localhost:8003/api/v1/performance/metrics | jq '.optimization_features.parallel_processing'

# Reduce concurrent load if needed
export MAX_CONCURRENT_VERIFICATIONS=50

# Monitor verification queue
curl http://localhost:8003/api/v1/verification/queue-status
```

#### Memory Issues with Large Proofs
```bash
# Monitor memory usage
free -h
docker stats acgs-fv-service

# Increase memory limits if needed
# In docker-compose.yml or Kubernetes deployment
memory: 2Gi

# Enable proof caching
export ENABLE_VERIFICATION_CACHE=true
export CACHE_SIZE_MB=2048
```

### Performance Optimization

#### Database Optimization
```sql
-- Optimize verification queries
CREATE INDEX idx_verification_policy_id ON verifications(policy_id);
CREATE INDEX idx_verification_timestamp ON verifications(created_at);
CREATE INDEX idx_verification_status ON verifications(verification_status);
```

#### Cache Optimization
```bash
# Monitor cache hit rates
redis-cli info stats | grep hit_rate

# Optimize cache configuration
redis-cli config set maxmemory 2gb
redis-cli config set maxmemory-policy allkeys-lru
```

#### Z3 Solver Optimization
```python
# Optimize Z3 solver configuration
solver.set("timeout", 30000)
solver.set("memory_max_size", 1024)  # 1GB memory limit
solver.set("threads", 4)  # Use multiple threads
```

## Security Considerations

### Formal Verification Security
- **Proof Integrity**: All proofs are cryptographically signed
- **Constitutional Validation**: Continuous constitutional hash verification
- **Access Control**: Role-based access for verification operations
- **Audit Trail**: Complete audit trail for all verification activities

### Z3 Solver Security
- **Timeout Protection**: Prevents infinite loops and DoS attacks
- **Memory Limits**: Prevents memory exhaustion attacks
- **Input Validation**: Comprehensive validation of verification requests
- **Sandboxing**: Z3 operations run in controlled environments

## Contributing

1. Follow ACGS-1 coding standards with formal verification best practices
2. Ensure >90% test coverage for verification algorithms
3. Update API documentation for new verification endpoints
4. Test Z3 integration thoroughly with edge cases
5. Validate constitutional compliance for all changes

## Support

- **Documentation**: [Formal Verification API](../../../docs/api/formal_verification_service_api.md)
- **Health Check**: http://localhost:8003/health
- **Interactive API Docs**: http://localhost:8003/docs
- **Logs**: `/logs/fv_service.log`
- **Configuration**: `services/core/formal-verification/fv_service/.env`
- **Z3 Documentation**: [Z3 Theorem Prover Guide](https://z3prover.github.io/api/html/index.html)
