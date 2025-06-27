# ACGS-1 Policy Governance Compiler Service

**Status**: 🧪 **Prototype**  
**Last Updated**: 2025-06-27

## Overview

The Policy Governance Compiler (PGC) Service is an enterprise-grade policy enforcement engine that provides real-time governance policy enforcement, workflow orchestration, and constitutional compliance validation using Open Policy Agent (OPA) integration and advanced optimization algorithms.

**Service Port**: 8005
**Service Version**: 3.0.0 (Phase 3 Production)
**Constitutional Hash**: `cdd01ef066bc6cf2`
**Health Check**: http://localhost:8005/health

## Core Features

### Real-Time Policy Enforcement

- **Open Policy Agent Integration**: Advanced OPA integration for policy evaluation
- **Ultra-Low Latency**: <25ms P95 latency for 95% of enforcement requests
- **Real-Time Compliance**: Sub-200ms constitutional compliance validation
- **Action Interception**: Real-time interception and validation of governance actions
- **Policy Evaluation**: Comprehensive policy query evaluation against active policies

### Policy Lifecycle Management

- **Comprehensive Lifecycle**: Complete policy creation, review, approval, and activation workflow
- **Multi-Stakeholder Processes**: Coordinated governance processes across stakeholders
- **Workflow Orchestration**: Automated governance workflow management
- **Version Control**: Policy versioning with rollback capabilities
- **Incremental Compilation**: Zero-downtime policy updates with hot-swapping

### Advanced Enforcement Capabilities

- **Constitutional Compliance**: Continuous validation against constitutional hash
- **AlphaEvolve Integration**: Advanced enforcement optimization algorithms
- **WINA Optimization**: Weighted Intelligence Network Architecture for enforcement
- **Circuit Breaker Patterns**: Fault tolerance and cascade failure prevention
- **Audit Trail**: Comprehensive audit logging for all enforcement actions

### Enterprise Features

- **Performance Optimization**: P99 latency <500ms, P95 latency <25ms targets
- **High Availability**: >99.5% availability with automatic failover
- **Scalability**: Horizontal scaling with load balancing
- **Security**: mTLS, RBAC, and comprehensive security controls
- **Monitoring**: Real-time performance and compliance monitoring

## API Endpoints

### Policy Enforcement

- `POST /api/v1/enforcement/evaluate` - Evaluate policy queries against active policies
- `POST /api/v1/enforcement/realtime-compliance` - Real-time compliance checking (<200ms)
- `POST /api/v1/enforcement/intercept-action` - Intercept and validate governance actions
- `GET /api/v1/enforcement/compliance-metrics` - Compliance performance metrics
- `POST /api/v1/enforcement/batch-evaluate` - Batch policy evaluation

### Policy Lifecycle Management

- `POST /api/v1/lifecycle/create` - Create new policy in lifecycle
- `POST /api/v1/lifecycle/review` - Submit policy for review
- `POST /api/v1/lifecycle/approve` - Approve policy for activation
- `POST /api/v1/lifecycle/activate` - Activate approved policy
- `GET /api/v1/lifecycle/status/{policy_id}` - Get policy lifecycle status

### Governance Workflows

- `POST /api/v1/governance-workflows/initiate` - Initiate governance workflow
- `GET /api/v1/governance-workflows/status/{workflow_id}` - Get workflow status
- `POST /api/v1/governance-workflows/advance` - Advance workflow to next stage
- `GET /api/v1/governance-workflows/active` - List active workflows

### Incremental Compilation

- `POST /api/v1/incremental/deploy` - Deploy policy update with zero-downtime
- `POST /api/v1/incremental/rollback` - Rollback to previous policy version
- `GET /api/v1/incremental/status` - Get compilation and deployment status
- `GET /api/v1/incremental/metrics` - Compilation performance metrics

### Ultra-Low Latency Optimization

- `POST /api/v1/ultra-low-latency/evaluate` - Optimized policy evaluation (<25ms)
- `GET /api/v1/ultra-low-latency/metrics` - Ultra-low latency performance metrics
- `POST /api/v1/ultra-low-latency/optimize` - Optimize enforcement paths
- `GET /api/v1/ultra-low-latency/cache-stats` - Cache performance statistics

### AlphaEvolve Enhancement

- `POST /api/v1/alphaevolve/optimize-enforcement` - AlphaEvolve enforcement optimization
- `GET /api/v1/alphaevolve/strategies` - Available optimization strategies
- `POST /api/v1/alphaevolve/evaluate` - AlphaEvolve-optimized policy evaluation
- `GET /api/v1/alphaevolve/performance` - AlphaEvolve performance metrics

### Constitutional Compliance

- `POST /api/v1/constitutional/validate` - Constitutional compliance validation
- `GET /api/v1/constitutional/status` - Constitutional compliance status
- `POST /api/v1/constitutional/workflow` - Constitutional compliance workflow
- `GET /api/v1/constitutional/metrics` - Constitutional compliance metrics

### System Management

- `GET /health` - Service health with component status
- `GET /api/v1/status` - Detailed API status and capabilities
- `GET /metrics` - Prometheus metrics for monitoring
- `GET /` - Service information and governance capabilities

## Configuration

### Environment Variables

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/acgs_policy_governance
REDIS_URL=redis://localhost:6379/5

# Service Configuration
SERVICE_NAME=pgc-service
SERVICE_VERSION=3.0.0
SERVICE_PORT=8005
APP_ENV=production
LOG_LEVEL=INFO

# OPA Configuration
OPA_SERVER_URL=http://localhost:8181
OPA_BUNDLE_NAME=authz
OPA_TIMEOUT_MS=5000
ENABLE_OPA_FALLBACK=true

# Constitutional Governance
CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
CONSTITUTIONAL_COMPLIANCE_THRESHOLD=0.8
ENABLE_CONSTITUTIONAL_VALIDATION=true
STRICT_CONSTITUTIONAL_MODE=true

# Performance Configuration
P99_LATENCY_TARGET_MS=500
P95_LATENCY_TARGET_MS=25
ULTRA_LOW_LATENCY_TARGET_MS=25
RESPONSE_TIME_TARGET_MS=200
AVAILABILITY_TARGET=0.995

# Enforcement Configuration
ENABLE_REAL_TIME_ENFORCEMENT=true
ENABLE_ACTION_INTERCEPTION=true
ENABLE_BATCH_EVALUATION=true
MAX_CONCURRENT_EVALUATIONS=100
ENFORCEMENT_TIMEOUT_MS=200

# Service Integration
AC_SERVICE_URL=http://localhost:8001
FV_SERVICE_URL=http://localhost:8003
INTEGRITY_SERVICE_URL=http://localhost:8002
AUTH_SERVICE_URL=http://localhost:8000

# Advanced Features
ENABLE_ALPHAEVOLVE_OPTIMIZATION=true
ENABLE_WINA_ENFORCEMENT=true
ENABLE_INCREMENTAL_COMPILATION=true
ENABLE_CIRCUIT_BREAKER=true
CIRCUIT_BREAKER_THRESHOLD=5

# Security Configuration
ENABLE_MTLS=true
ENABLE_RBAC=true
ENABLE_AUDIT_LOGGING=true
ENABLE_RATE_LIMITING=true
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
- Open Policy Agent (OPA) 0.58+
- Docker & Docker Compose (for containerized deployment)

### Local Development

```bash
# 1. Install dependencies
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
uv sync

# Alternative: Traditional pip
pip install -r requirements.txt

# 2. Install and start OPA
# Download OPA
curl -L -o opa https://openpolicyagent.org/downloads/v0.58.0/opa_linux_amd64_static
chmod +x opa
sudo mv opa /usr/local/bin/

# Start OPA server
opa run --server --addr localhost:8181 &

# 3. Setup database
createdb acgs_policy_governance
alembic upgrade head

# 4. Configure environment
cp .env.example .env
# Edit .env with your configuration

# 5. Start service
uv run uvicorn app.main:app --reload --port 8005
```

### Production Deployment

```bash
# Using Docker
docker build -t acgs-pgc-service .
docker run -p 8005:8005 --env-file .env acgs-pgc-service

# Using systemd
sudo cp pgc-service.service /etc/systemd/system/
sudo systemctl enable pgc-service
sudo systemctl start pgc-service

# Using Docker Compose with OPA
docker-compose up -d
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
# Test OPA integration
uv run pytest tests/test_opa_integration.py -v

# Test policy enforcement
uv run pytest tests/test_enforcement.py -v

# Test constitutional compliance
uv run pytest tests/test_constitutional_compliance.py -v
```

### Performance Tests

```bash
# Test enforcement latency
python scripts/test_enforcement_latency.py

# Test ultra-low latency performance
python scripts/test_ultra_low_latency.py

# Load testing
python scripts/test_enforcement_load.py --concurrent 50
```

## Usage Examples

### Basic Policy Enforcement

```python
import httpx

async def evaluate_policy():
    async with httpx.AsyncClient() as client:
        # Evaluate policy query against active policies
        response = await client.post(
            "http://localhost:8005/api/v1/enforcement/evaluate",
            json={
                "query": "data.acgs.authz.allow",
                "input_data": {
                    "user": {"id": "user123", "role": "citizen"},
                    "action": {"type": "data_access", "resource": "personal_data"},
                    "resource": {"id": "resource456", "type": "sensitive_data"},
                    "environment": {"time": "2025-06-24T10:00:00Z"}
                },
                "explain": "full",
                "metrics": True
            },
            headers={"Authorization": f"Bearer {access_token}"}
        )

        result = response.json()
        return {
            "allowed": result["result"]["allow"],
            "explanation": result["explanation"],
            "decision_time_ms": result["metrics"]["decision_time_ms"]
        }
```

### Real-Time Compliance Checking

```python
async def realtime_compliance_check():
    async with httpx.AsyncClient() as client:
        # Ultra-fast compliance validation (<200ms)
        response = await client.post(
            "http://localhost:8005/api/v1/enforcement/realtime-compliance",
            json={
                "action_type": "policy_creation",
                "user_id": "user123",
                "resource_id": "policy456",
                "action_data": {
                    "policy_content": "Citizens have right to privacy",
                    "policy_category": "privacy_rights"
                },
                "constitutional_principles": [
                    "privacy_rights",
                    "constitutional_supremacy"
                ],
                "validation_level": "comprehensive"
            },
            headers={"Authorization": f"Bearer {access_token}"}
        )

        result = response.json()
        return {
            "compliant": result["compliance_result"]["compliant"],
            "confidence": result["compliance_result"]["confidence"],
            "validation_time_ms": result["performance_metrics"]["validation_time_ms"],
            "constitutional_hash": result["constitutional_hash"]
        }
```

### Action Interception and Validation

```python
async def intercept_governance_action():
    async with httpx.AsyncClient() as client:
        # Intercept and validate governance action
        response = await client.post(
            "http://localhost:8005/api/v1/enforcement/intercept-action",
            json={
                "action_type": "constitutional_amendment",
                "user_id": "council_member_123",
                "action_data": {
                    "amendment_text": "Add new privacy protection clause",
                    "affected_sections": ["privacy_rights", "data_protection"],
                    "justification": "Enhanced citizen privacy protection"
                },
                "stakeholders": ["constitutional_council", "privacy_advocates"],
                "urgency_level": "high"
            },
            headers={"Authorization": f"Bearer {access_token}"}
        )

        result = response.json()
        return {
            "action_allowed": result["enforcement_decision"]["allow"],
            "required_approvals": result["enforcement_decision"]["required_approvals"],
            "workflow_initiated": result["workflow_status"]["initiated"],
            "estimated_completion": result["workflow_status"]["estimated_completion"]
        }
```

### Policy Lifecycle Management

```python
async def manage_policy_lifecycle():
    async with httpx.AsyncClient() as client:
        # Create new policy in lifecycle
        create_response = await client.post(
            "http://localhost:8005/api/v1/lifecycle/create",
            json={
                "policy_content": "New environmental protection policy",
                "policy_type": "environmental",
                "author_id": "policy_author_123",
                "stakeholders": ["environmental_committee", "legal_team"],
                "priority": "high"
            },
            headers={"Authorization": f"Bearer {access_token}"}
        )

        policy_id = create_response.json()["policy_id"]

        # Submit for review
        review_response = await client.post(
            "http://localhost:8005/api/v1/lifecycle/review",
            json={
                "policy_id": policy_id,
                "reviewers": ["legal_team", "environmental_experts"],
                "review_deadline": "2025-07-01T00:00:00Z"
            },
            headers={"Authorization": f"Bearer {access_token}"}
        )

        return {
            "policy_id": policy_id,
            "lifecycle_stage": "under_review",
            "review_id": review_response.json()["review_id"]
        }
```

### Ultra-Low Latency Enforcement

```python
async def ultra_low_latency_evaluation():
    async with httpx.AsyncClient() as client:
        # Optimized policy evaluation targeting <25ms
        response = await client.post(
            "http://localhost:8005/api/v1/ultra-low-latency/evaluate",
            json={
                "query": "data.acgs.authz.allow",
                "input_data": {
                    "user": {"id": "user123"},
                    "action": {"type": "read"},
                    "resource": {"id": "resource456"}
                },
                "optimization_level": "maximum",
                "cache_enabled": True
            },
            headers={"Authorization": f"Bearer {access_token}"}
        )

        result = response.json()
        return {
            "allowed": result["result"]["allow"],
            "latency_ms": result["performance"]["latency_ms"],
            "cache_hit": result["performance"]["cache_hit"],
            "optimization_applied": result["performance"]["optimization_applied"]
        }
```

## Open Policy Agent Integration

### OPA Configuration

The service integrates with OPA for policy evaluation:

```rego
# Example OPA policy for ACGS governance
package acgs.authz

import rego.v1

# Default deny
default allow := false

# Allow if user has required permissions
allow if {
    input.user.role in ["admin", "policy_creator"]
    input.action.type in ["create_policy", "modify_policy"]
    constitutional_compliance
}

# Constitutional compliance check
constitutional_compliance if {
    input.constitutional_hash == "cdd01ef066bc6cf2"
    input.constitutional_principles
    count(input.constitutional_principles) > 0
}

# Privacy protection enforcement
allow if {
    input.action.type == "data_access"
    input.resource.type == "personal_data"
    privacy_consent_valid
}

privacy_consent_valid if {
    input.user.consent_status == "granted"
    input.user.consent_expiry > time.now_ns()
}
```

### OPA Health Check

```python
# OPA connectivity verification
async def check_opa_health():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://localhost:8181/health")
            return response.status_code == 200
        except Exception:
            return False
```

### Constitutional Hash Validation

```python
# Constitutional hash validation in policy enforcement
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

def validate_constitutional_enforcement(enforcement_result):
    return (
        enforcement_result.get("constitutional_hash") == CONSTITUTIONAL_HASH and
        enforcement_result.get("constitutional_compliance", {}).get("compliant", False)
    )
```

## Monitoring & Observability

### Health Checks

```bash
# Service health with component status
curl http://localhost:8005/health

# Expected response includes OPA status
{
  "status": "healthy",
  "service": "pgc_service_production",
  "version": "3.0.0",
  "components": {
    "opa_server": "operational",
    "policy_engine": "operational",
    "enforcement_engine": "operational"
  },
  "performance_targets": {
    "p99_latency_ms": 500,
    "p95_latency_ms": 25
  }
}
```

### Performance Metrics

```bash
# Get enforcement performance metrics
curl http://localhost:8005/api/v1/enforcement/compliance-metrics

# Ultra-low latency metrics
curl http://localhost:8005/api/v1/ultra-low-latency/metrics

# Incremental compilation metrics
curl http://localhost:8005/api/v1/incremental/metrics
```

### Real-time Monitoring

```bash
# Monitor enforcement operations
curl http://localhost:8005/api/v1/monitoring/enforcement

# OPA server status
curl http://localhost:8181/health

# Constitutional compliance status
curl http://localhost:8005/api/v1/constitutional/status
```

## Troubleshooting

### Common Issues

#### OPA Server Not Available

```bash
# Check OPA server status
curl http://localhost:8181/health

# Start OPA if not running
opa run --server --addr localhost:8181 &

# Verify OPA connectivity from PGC service
curl http://localhost:8005/health | jq '.components.opa_server'
```

#### High Enforcement Latency

```bash
# Check current latency metrics
curl http://localhost:8005/api/v1/enforcement/compliance-metrics | jq '.performance_metrics'

# Enable ultra-low latency mode
export ULTRA_LOW_LATENCY_TARGET_MS=15

# Optimize OPA policies
opa fmt --diff policies/
```

#### Constitutional Hash Mismatch

```bash
# Verify constitutional hash
curl http://localhost:8005/api/v1/constitutional/status | jq '.constitutional_hash'

# Expected: "cdd01ef066bc6cf2"
# Reset if corrupted
python scripts/reset_constitutional_state.py --service pgc
```

#### Policy Compilation Failures

```bash
# Check compilation status
curl http://localhost:8005/api/v1/incremental/status

# View compilation logs
tail -f /logs/pgc_service.log | grep "compilation"

# Rollback to previous version if needed
curl -X POST http://localhost:8005/api/v1/incremental/rollback \
  -H "Content-Type: application/json" \
  -d '{"version": "previous"}'
```

#### Circuit Breaker Activation

```bash
# Check circuit breaker status
curl http://localhost:8005/api/v1/monitoring/circuit-breaker

# Reset circuit breaker if needed
curl -X POST http://localhost:8005/api/v1/monitoring/circuit-breaker/reset

# Adjust circuit breaker threshold
export CIRCUIT_BREAKER_THRESHOLD=10
```

### Performance Optimization

#### OPA Policy Optimization

```rego
# Optimize OPA policies for performance
package acgs.authz.optimized

import rego.v1

# Use indexed lookups
user_permissions := data.users[input.user.id].permissions

# Cache frequently accessed data
cached_policies := data.policies

# Minimize rule complexity
allow if {
    required_permission in user_permissions
    policy_allows_action
}
```

#### Database Optimization

```sql
-- Optimize enforcement queries
CREATE INDEX idx_enforcement_timestamp ON enforcement_logs(timestamp);
CREATE INDEX idx_enforcement_user ON enforcement_logs(user_id);
CREATE INDEX idx_enforcement_action ON enforcement_logs(action_type);
```

#### Cache Optimization

```bash
# Monitor cache performance
redis-cli info stats | grep hit_rate

# Optimize enforcement caching
redis-cli config set maxmemory 2gb
redis-cli config set maxmemory-policy allkeys-lru
```

## Security Considerations

### Policy Enforcement Security

- **OPA Security**: Secure OPA server configuration with authentication
- **Constitutional Validation**: Continuous constitutional hash verification
- **Access Control**: Role-based access for policy enforcement operations
- **Audit Trail**: Comprehensive logging of all enforcement decisions

### Real-Time Enforcement Security

- **Input Validation**: Comprehensive validation of enforcement requests
- **Rate Limiting**: Protection against enforcement abuse
- **Circuit Breakers**: Protection against cascade failures
- **Secure Communication**: mTLS for service-to-service communication

## Contributing

1. Follow ACGS-1 coding standards with policy enforcement best practices
2. Ensure >90% test coverage for enforcement algorithms
3. Update API documentation for new enforcement endpoints
4. Test OPA integration thoroughly with edge cases
5. Validate constitutional compliance for all changes

## Support

- **Documentation**: [Policy Governance API](../../../docs/api/policy_governance_service_api.md)
- **Health Check**: http://localhost:8005/health
- **Interactive API Docs**: http://localhost:8005/docs
- **Logs**: `/logs/pgc_service.log`
- **Configuration**: `services/core/policy-governance/pgc_service/.env`
- **OPA Documentation**: [Open Policy Agent](https://www.openpolicyagent.org/docs/latest/)

2. Copy `.env.example` to `.env` and set:
   - `INTEGRITY_SERVICE_URL` - URL of the Integrity service
   - `POLICY_REFRESH_INTERVAL_SECONDS` - policy reload interval

### Running Service

```bash
# Using UV (recommended)
uv run uvicorn main:app --reload --port 8005

# Alternative: Traditional
uvicorn main:app --reload --port 8005
```

### Running Tests

```bash
# Using UV
uv run pytest tests/

# Alternative: Traditional
pytest tests/
```

### Running Service

```bash
uvicorn main:app --reload
```

### Running Tests

```bash
pytest tests
```
