# CLAUDE.md - ACGS Context Engineering Framework

This file provides comprehensive guidance to Claude Code when working with the ACGS (Autonomous Constitutional Governance System) repository, integrating Context Engineering principles with constitutional compliance requirements.

**Constitutional Hash:** `cdd01ef066bc6cf2` - Must be validated in ALL operations.

## Context Engineering Principles for ACGS

### Core Philosophy: "Context is King"
- **Traditional Prompt Engineering**: Optimize individual requests
- **ACGS Context Engineering**: Provide comprehensive context for systematic implementation
- **Constitutional Compliance**: All context must validate constitutional governance

### ACGS Context Engineering Rules

#### 1. Constitutional Compliance (MANDATORY)
```python
# ALL code must include constitutional validation
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

def validate_constitutional_compliance(operation_data: dict) -> bool:
    """Validate all operations against constitutional framework."""
    return operation_data.get("constitutional_hash") == CONSTITUTIONAL_HASH
```

#### 2. Performance Targets (ENFORCED)
- **P99 Latency**: < 5ms for all coordination operations
- **Throughput**: > 100 RPS for multi-agent handoffs
- **Cache Hit Rate**: > 85% for constitutional validation
- **Availability**: 99.99% for core services

#### 3. Multi-Agent Coordination Context
- **Always reference** existing agent patterns in `services/core/multi_agent_coordinator/`
- **Validate** against blackboard service integration at port 8010
- **Ensure** constitutional compliance in all agent communications
- **Test** consensus engine integration with multiple algorithms

## Development Environment Setup

```bash
# Initial setup with Context Engineering validation
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Start infrastructure with constitutional compliance validation
docker compose -f infrastructure/docker/docker-compose.acgs.yml up -d

# Validate constitutional compliance across all services
python tools/validation/constitutional_compliance_validator.py

# Run Context Engineering validation framework
python tools/context_engineering/validate_acgs_context.py
```

## ACGS Service Architecture Context

### Production Services with Context Engineering Integration

**Core Constitutional Services:**
- **Constitutional AI Service** (8001): Core compliance with hash validation
- **Integrity Service** (8002): Cryptographic audit trail with hash chaining
- **Multi-Agent Coordinator** (8008): Agent orchestration with constitutional safety
- **Worker Agents** (8009): Specialized governance agents (Ethics, Legal, Operational)
- **Blackboard Service** (8010): Redis-based shared knowledge with constitutional validation

**Infrastructure Services:**
- **API Gateway** (8010): Production routing with constitutional middleware
- **Authentication** (8016): JWT multi-tenant auth with constitutional claims
- **Audit Aggregator** (8015): Centralized logging with 45+ event types

**Performance Monitoring:**
- **PostgreSQL** (5439): Row-Level Security with constitutional compliance
- **Redis** (6389): Constitutional caching with tenant isolation
- **Prometheus**: Constitutional compliance metrics
- **Grafana**: Real-time constitutional governance dashboards

## Context Engineering Workflow for ACGS

### 1. Project Context Awareness

**ALWAYS READ FIRST:**
- `CLAUDE_CONTEXT_ENGINEERING.md` (this file)
- Current constitutional compliance status via `/health` endpoints
- Performance metrics via Prometheus at http://localhost:9090
- Multi-agent coordination status via blackboard service

**NEVER ASSUME:**
- Existing service configurations without validation
- Constitutional compliance without hash verification
- Multi-agent state without blackboard consultation
- Performance characteristics without metrics validation

### 2. ACGS Code Quality Standards

**File Structure Limits:**
- Maximum 500 lines per file (enforced via ruff)
- Modular constitutional compliance validation
- Async/await patterns throughout for sub-5ms performance

**Import Patterns (MANDATORY):**
```python
# Constitutional compliance imports
try:
    from services.shared.constitutional.safety_framework import (
        ConstitutionalSafetyValidator,
        validate_constitutional_hash,
    )
    CONSTITUTIONAL_VALIDATION_AVAILABLE = True
except ImportError:
    CONSTITUTIONAL_VALIDATION_AVAILABLE = False
    # NEVER proceed without constitutional validation in production

# Multi-tenant isolation imports
try:
    from services.shared.middleware.tenant_middleware import (
        TenantContextMiddleware,
        get_tenant_context,
    )
    MULTI_TENANT_AVAILABLE = True
except ImportError:
    MULTI_TENANT_AVAILABLE = False

# Performance monitoring imports
from services.shared.performance.metrics import (
    track_latency,
    track_constitutional_compliance,
)
```

**Testing Requirements (COMPREHENSIVE):**
```python
# MANDATORY test patterns for all ACGS features
import pytest
from services.shared.testing.constitutional_test_framework import (
    ConstitutionalTestCase,
    validate_performance_targets,
)

class TestACGSFeature(ConstitutionalTestCase):
    """All ACGS tests must inherit from ConstitutionalTestCase."""
    
    @pytest.mark.constitutional
    def test_constitutional_compliance(self):
        """Validate constitutional hash in all operations."""
        assert self.validate_constitutional_hash()
    
    @pytest.mark.performance
    def test_performance_targets(self):
        """Validate sub-5ms P99 latency."""
        assert self.validate_latency_target(max_p99_ms=5.0)
    
    @pytest.mark.integration
    def test_multi_agent_coordination(self):
        """Validate multi-agent coordination patterns."""
        assert self.validate_blackboard_integration()
```

### 3. ACGS-Specific Error Handling

**Constitutional Compliance Errors:**
```python
from services.shared.middleware.error_handling import (
    ConstitutionalComplianceError,
    SecurityValidationError,
    PerformanceTargetExceededError,
)

# Handle constitutional violations
if not validate_constitutional_hash(operation_data):
    raise ConstitutionalComplianceError(
        f"Operation violates constitutional framework: {CONSTITUTIONAL_HASH}"
    )

# Handle performance violations
if latency_p99 > 5.0:
    raise PerformanceTargetExceededError(
        f"P99 latency {latency_p99}ms exceeds 5ms target"
    )
```

## Context Engineering Documentation Standards

### 1. Feature Documentation Structure

**For every ACGS feature, provide:**
```markdown
# Feature: [Name]

## Constitutional Compliance
- Hash: cdd01ef066bc6cf2
- Validation: [Description of compliance validation]
- Audit Events: [List of generated audit events]

## Performance Impact
- P99 Latency: [Expected impact in ms]
- Throughput: [Expected RPS impact]
- Cache Dependencies: [Constitutional cache requirements]

## Multi-Agent Integration
- Coordinator Integration: [How feature integrates with coordinator]
- Blackboard Operations: [Required blackboard interactions]
- Worker Agent Dependencies: [Which agents are involved]

## Examples
- Code Pattern: [Link to example in services/examples/]
- Test Pattern: [Link to test example]
- Integration Pattern: [Link to integration example]

## Validation Commands
```bash
# Syntax validation
ruff check services/[service_name]/
mypy services/[service_name]/

# Constitutional compliance validation
python tools/validation/constitutional_compliance_validator.py --service [service_name]

# Performance validation
python tests/performance/test_[feature]_performance.py

# Integration validation
pytest tests/integration/test_[feature]_integration.py -v
```

## Gotchas and Anti-Patterns
- [Specific issues to avoid]
- [Common constitutional compliance mistakes]
- [Performance pitfalls]
```

### 2. Code Examples and Patterns

**ALWAYS include working examples in `services/examples/context_engineering/`:**
- Constitutional compliance patterns
- Multi-agent coordination examples
- Performance optimization patterns
- Error handling examples
- Testing framework usage

## ACGS Context Engineering Commands

### Constitutional Validation Loop
```bash
# Level 1: Syntax and constitutional compliance
ruff check --fix services/
mypy services/
python tools/validation/constitutional_compliance_validator.py

# Level 2: Unit tests with constitutional validation
pytest tests/unit/ -v --constitutional-compliance

# Level 3: Integration tests with multi-agent coordination
pytest tests/integration/ -v --multi-agent-coordination

# Level 4: Performance validation
python tests/performance/test_performance_regression.py
```

### Multi-Agent Coordination Validation
```bash
# Validate blackboard service integration
curl http://localhost:8010/health
python tools/multi_agent/validate_blackboard_integration.py

# Validate consensus engine coordination
python tools/multi_agent/test_consensus_algorithms.py

# Validate worker agent coordination
python tools/multi_agent/test_worker_agent_coordination.py
```

## Performance Monitoring and Validation

### Real-time Constitutional Compliance Monitoring
```bash
# Check constitutional compliance metrics
curl http://localhost:9090/api/v1/query?query=constitutional_compliance_score

# Validate performance targets
curl http://localhost:9090/api/v1/query?query=http_request_duration_seconds

# Check multi-agent coordination health
curl http://localhost:8008/api/v1/coordination/health
```

### Grafana Dashboards
- **Constitutional Compliance Dashboard**: http://localhost:3000/d/constitutional-compliance
- **Multi-Agent Coordination Dashboard**: http://localhost:3000/d/multi-agent-coordination
- **Performance Monitoring Dashboard**: http://localhost:3000/d/acgs-performance

## Advanced ACGS Context Engineering Patterns

### 1. Multi-Agent PRP Patterns
```python
# Example multi-agent coordination context
MULTI_AGENT_CONTEXT = {
    "constitutional_hash": "cdd01ef066bc6cf2",
    "coordinator_endpoint": "http://localhost:8008",
    "blackboard_endpoint": "http://localhost:8010", 
    "required_agents": ["ethics", "legal", "operational"],
    "consensus_algorithms": [
        "MajorityVoteConsensus",
        "ConstitutionalPriorityConsensus"
    ],
    "performance_targets": {
        "coordination_latency_ms": 5.0,
        "consensus_timeout_ms": 1000.0
    }
}
```

### 2. Constitutional Compliance Context
```python
# Example constitutional validation context
CONSTITUTIONAL_CONTEXT = {
    "hash": "cdd01ef066bc6cf2",
    "validation_service": "http://localhost:8001",
    "audit_service": "http://localhost:8002",
    "compliance_threshold": 0.95,
    "required_validations": [
        "hash_integrity",
        "policy_compliance", 
        "audit_trail_integrity"
    ]
}
```

### 3. Performance Optimization Context
```python
# Example performance context
PERFORMANCE_CONTEXT = {
    "latency_targets": {
        "p99_ms": 5.0,
        "p95_ms": 3.0,
        "p50_ms": 1.0
    },
    "throughput_targets": {
        "rps": 100,
        "concurrent_agents": 50
    },
    "caching_strategy": {
        "constitutional_cache_ttl": 300,
        "redis_endpoint": "redis://localhost:6389"
    }
}
```

## Context Engineering Quality Gates

### Pre-Implementation Checklist
- [ ] Constitutional compliance context gathered
- [ ] Performance targets defined and validated
- [ ] Multi-agent coordination patterns identified
- [ ] Existing ACGS patterns reviewed
- [ ] Test validation commands prepared
- [ ] Documentation structure planned

### Post-Implementation Validation
- [ ] Constitutional hash validation passes
- [ ] Performance targets met (P99 < 5ms)
- [ ] Multi-agent coordination functional
- [ ] All tests pass with constitutional compliance
- [ ] Documentation updated with examples
- [ ] Integration with existing ACGS services verified

## ACGS-Specific Gotchas and Common Issues

### Constitutional Compliance
- **Never** hardcode constitutional hash without validation
- **Always** validate hash in async operations
- **Remember** to include hash in all audit events

### Multi-Agent Coordination
- **Check** blackboard service availability before agent operations
- **Validate** consensus algorithm compatibility
- **Ensure** proper agent lifecycle management

### Performance Optimization
- **Profile** constitutional validation overhead
- **Cache** frequently accessed constitutional data
- **Monitor** multi-agent coordination latency

### Testing and Validation
- **Use** ConstitutionalTestCase for all ACGS tests
- **Include** performance regression tests
- **Validate** multi-tenant isolation in tests

## Integration with Existing ACGS Infrastructure

### Service Integration Patterns
- **FastAPI** with Pydantic v2 for all new services
- **Async/await** throughout for performance
- **Constitutional middleware** on all endpoints
- **Multi-tenant** context in all operations

### Database Integration
- **PostgreSQL** with Row-Level Security for constitutional compliance
- **Alembic** migrations with constitutional validation
- **Audit tables** for all constitutional events

### Monitoring Integration
- **Prometheus** metrics for constitutional compliance
- **Grafana** dashboards for real-time monitoring
- **Alert rules** for constitutional violations

---

**Remember**: In ACGS Context Engineering, constitutional compliance is not optional - it's the foundation of every operation. Always validate the constitutional hash `cdd01ef066bc6cf2` and maintain sub-5ms P99 latency targets while ensuring robust multi-agent coordination.