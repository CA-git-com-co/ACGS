<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

# CLAUDE.md - Policy Governance Service

## Directory Overview

The Policy Governance service provides comprehensive policy evaluation, compliance checking, and governance decision-making within the ACGS-2 constitutional AI governance framework. It integrates with Open Policy Agent (OPA) for robust policy enforcement.

## File Inventory

- **CLAUDE.md**: This documentation file
- **app/**: FastAPI application and API endpoints
- **governance_decision_engine.py**: Core policy evaluation engine
- **pgc_service/**: Policy Governance Compiler service components
- **qpe_service/**: Quantum Policy Engine service components
- **simple_pgc_main.py**: Simplified policy governance main application
- **src/**: Source code and core logic
- **monitoring/**: Monitoring and observability configuration
- **k8s/**: Kubernetes deployment manifests
- **chaos-testing/**: Chaos engineering test scenarios

## Dependencies & Interactions

- **Open Policy Agent (OPA)**: Policy evaluation and enforcement engine
- **Constitutional AI Service**: Constitutional compliance validation
- **Governance Synthesis Service**: Policy synthesis and orchestration
- **Integrity Service**: Audit trail for policy decisions
- **Constitutional Framework**: Compliance with hash `cdd01ef066bc6cf2`

## Key Components

### Policy Evaluation Engine
- **OPA Integration**: Advanced Open Policy Agent integration for policy evaluation
- **Multi-Policy Orchestration**: Evaluation across constitutional, regulatory, and procedural policies
- **Conflict Resolution**: Detection and resolution of policy conflicts
- **Decision Synthesis**: Combining multiple policy evaluations into coherent decisions
- **Constitutional Enforcement**: Ensuring all policies align with constitutional principles

### Policy Types Supported
- **Constitutional Policies**: Core constitutional compliance rules
- **Regulatory Policies**: Legal and regulatory compliance requirements
- **Procedural Policies**: Operational and workflow policies
- **Security Policies**: Security and access control policies
- **Data Governance Policies**: Data handling and privacy policies
- **Multi-Tenant Policies**: Tenant-specific policy isolation
- **Agent Lifecycle Policies**: AI agent governance and lifecycle management

### Governance Decision Framework
- **Policy Compilation**: Converting high-level policies into executable rules
- **Decision Trees**: Hierarchical policy evaluation structures
- **Audit Trails**: Complete logging of all policy decisions
- **Performance Optimization**: Caching and optimization for policy evaluation
- **Real-time Evaluation**: Sub-millisecond policy decision capabilities

## Constitutional Compliance Status

✅ **IMPLEMENTED**: Constitutional hash validation (`cdd01ef066bc6cf2`)
✅ **IMPLEMENTED**: OPA integration and policy evaluation
✅ **IMPLEMENTED**: Multi-policy orchestration
✅ **IMPLEMENTED**: Basic conflict resolution
🔄 **IN PROGRESS**: Advanced policy synthesis
🔄 **IN PROGRESS**: Quantum policy engine integration
❌ **PLANNED**: AI-driven policy optimization
❌ **PLANNED**: Predictive policy analysis

## Performance Considerations

- **Policy Evaluation Latency**: <2ms for standard policy checks
- **Constitutional Validation**: <1ms additional overhead
- **Throughput**: >1000 policy evaluations per second
- **Memory Usage**: Efficient policy caching and compilation
- **Scalability**: Horizontal scaling with policy distribution

## Implementation Status

### ✅ IMPLEMENTED
- Core policy evaluation engine with OPA integration
- Multi-policy orchestration and conflict resolution
- Constitutional compliance validation
- Basic monitoring and audit trails
- Kubernetes deployment configuration

### 🔄 IN PROGRESS
- Advanced policy synthesis and optimization
- Quantum policy engine integration
- Enhanced conflict resolution algorithms
- Real-time policy analytics
- Chaos engineering test suite

### ❌ PLANNED
- AI-driven policy optimization and learning
- Predictive policy analysis and recommendations
- Advanced policy versioning and rollback
- Multi-region policy distribution
- Policy performance machine learning

## API Endpoints

### Policy Evaluation
- **POST /evaluate**: Evaluate request against configured policies
- **POST /evaluate/batch**: Batch policy evaluation for multiple requests
- **GET /policies**: List available policies and their status
- **POST /policies/compile**: Compile high-level policies into executable rules
- **GET /policies/{id}/conflicts**: Check for policy conflicts

### Policy Management
- **POST /policies**: Create new policy
- **PUT /policies/{id}**: Update existing policy
- **DELETE /policies/{id}**: Remove policy
- **GET /policies/{id}/audit**: Get policy decision audit trail

### Monitoring and Health
- **GET /health**: Service health check
- **GET /metrics**: Prometheus metrics endpoint
- **GET /policies/stats**: Policy evaluation performance statistics

## Configuration

```yaml
# Policy Governance Configuration
policy_governance:
  opa_server_url: http://localhost:8181
  constitutional_hash: cdd01ef066bc6cf2
  evaluation_timeout: 5s
  max_concurrent_evaluations: 1000

policy_types:
  constitutional:
    priority: 1
    cache_ttl: 3600s
  regulatory:
    priority: 2
    cache_ttl: 1800s
  procedural:
    priority: 3
    cache_ttl: 900s

performance:
  evaluation_latency_target: 2ms
  throughput_target: 1000rps
  cache_hit_ratio_target: 90%

monitoring:
  enable_audit_trail: true
  log_level: INFO
  metrics_interval: 30s
```

## Usage Examples

```python
# Evaluate governance request against policies
policy_request = {
    "request_id": "pol-eval-456",
    "context": {
        "actor": "researcher",
        "resource": "patient_data",
        "action": "read",
        "environment": "research_environment"
    },
    "constitutional_hash": "cdd01ef066bc6cf2"
}

evaluation_result = await policy_service.evaluate(policy_request)

# Result includes decision, confidence, and audit trail
{
    "decision": "allow",
    "confidence": 0.95,
    "policies_evaluated": ["constitutional", "regulatory", "data_governance"],
    "conflicts_detected": [],
    "audit_trail_id": "audit-789"
}
```

## Cross-References & Navigation

**Navigation**:
- [Core Services](../CLAUDE.md)
- [Governance Synthesis](../governance-synthesis/CLAUDE.md)
- [Constitutional AI](../constitutional-ai/CLAUDE.md)
- [Formal Verification](../formal-verification/CLAUDE.md)

**Related Components**:
- [Integrity Service](../../platform_services/integrity/CLAUDE.md)
- [Multi-Agent Coordinator](../multi_agent_coordinator/CLAUDE.md)
- [API Gateway](../../platform_services/api_gateway/CLAUDE.md)

**External References**:
- [Open Policy Agent Documentation](https://www.openpolicyagent.org/docs/)
- [Policy as Code Best Practices](https://www.openpolicyagent.org/docs/latest/policy-language/)

---

**Constitutional Compliance**: All policy evaluations maintain constitutional hash `cdd01ef066bc6cf2` validation
