# Formal Verification Service API

## Service Overview

This service provides core functionality for the ACGS platform with constitutional compliance validation.

**Service**: Formal Verification
**Port**: 8XXX
**Constitutional Hash**: `cdd01ef066bc6cf2`


**Service**: Formal Verification Service
**Port**: 8003
**Base URL**: `http://localhost:8003/api/v1`
<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

## Overview

The Formal Verification Service provides mathematical proof validation, logical consistency checking, and formal verification of policies and governance decisions within the ACGS system.

## Authentication

All endpoints require JWT authentication:

```http
Authorization: Bearer <jwt_token>
X-Constitutional-Hash: cdd01ef066bc6cf2
```

## Endpoints

### Health Check

```http
GET /health
```

**Response**:
```json
{
  "status": "healthy",
  "service": "fv_service",
  "constitutional_hash": "cdd01ef066bc6cf2",
  "verification_engine": "active",
  "timestamp": "2025-07-05T12:00:00Z"
}
```

### Policy Verification

```http
POST /verification/policy
```

**Request**:
```json
{
  "policy": {
    "id": "policy_123",
    "rules": ["rule1", "rule2"],
    "constraints": ["constraint1"],
    "context": "governance"
  ,
  "constitutional_hash": "cdd01ef066bc6cf2"
},
  "verification_type": "consistency_check"
}
```

**Response**:
```json
{
  "success": true,
  "verified": true,
  "verification_score": 0.95,
  "constitutional_hash": "cdd01ef066bc6cf2",
  "proof_details": {
    "consistency": true,
    "completeness": true,
    "soundness": true,
    "logical_errors": []
  }
}
```

### Logical Consistency Check

```http
POST /verification/consistency
```

**Request**:
```json
{
  "statements": [
    "statement1",
    "statement2",
    "statement3"
  ],
  "logical_framework": "propositional"
,
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Response**:
```json
{
  "success": true,
  "consistent": true,
  "consistency_score": 1.0,
  "constitutional_hash": "cdd01ef066bc6cf2",
  "analysis": {
    "contradictions": [],
    "tautologies": [],
    "satisfiable": true
  }
}
```

### Proof Generation

```http
POST /verification/proof
```

**Request**:
```json
{
  "theorem": "governance_theorem",
  "premises": ["premise1", "premise2"],
  "proof_method": "natural_deduction"
,
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Response**:
```json
{
  "success": true,
  "proof_valid": true,
  "constitutional_hash": "cdd01ef066bc6cf2",
  "proof": {
    "steps": [
      {"step": 1, "rule": "modus_ponens", "conclusion": "conclusion1"},
      {"step": 2, "rule": "universal_instantiation", "conclusion": "conclusion2"}
    ],
    "conclusion": "final_conclusion",
    "confidence": 0.98
  }
}
```

### Constitutional Compliance Verification

```http
POST /verification/constitutional
```

**Request**:
```json
{
  "governance_decision": {
    "type": "policy_approval",
    "content": "decision_content",
    "context": "constitutional_framework"
  ,
  "constitutional_hash": "cdd01ef066bc6cf2"
},
  "constitutional_principles": ["principle1", "principle2"]
}
```

**Response**:
```json
{
  "success": true,
  "constitutionally_valid": true,
  "compliance_score": 0.97,
  "constitutional_hash": "cdd01ef066bc6cf2",
  "verification_details": {
    "principle_violations": [],
    "consistency_with_framework": true,
    "precedent_alignment": true
  }
}
```

### Model Checking

```http
POST /verification/model-check
```

**Request**:
```json
{
  "model": "governance_model",
  "properties": ["safety", "liveness"],
  "specification": "temporal_logic_spec"
,
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Response**:
```json
{
  "success": true,
  "properties_satisfied": true,
  "constitutional_hash": "cdd01ef066bc6cf2",
  "model_check_results": {
    "safety": {"satisfied": true, "counterexample": null},
    "liveness": {"satisfied": true, "counterexample": null},
    "verification_time": "0.005s"
  }
}
```

## Performance Specifications

| Metric | Target | Current |
|--------|--------|---------|
| **Response Time** | P99 ≤5ms | 0.007s ✅ |
| **Throughput** | ≥50 RPS | Medium |
| **Availability** | ≥99.9% | ✅ Healthy |
| **Proof Generation** | ≤100ms | Optimized |
| **Model Checking** | ≤1s | Fast |

## Verification Algorithms

### Supported Proof Methods

- **Natural Deduction**: Classical logical proofs
- **Resolution**: Automated theorem proving
- **Tableau Method**: Satisfiability checking
- **Model Checking**: Temporal logic verification
- **SMT Solving**: Satisfiability modulo theories

### Logical Frameworks

- **Propositional Logic**: Boolean satisfiability
- **First-Order Logic**: Predicate logic reasoning
- **Temporal Logic**: Time-based properties
- **Modal Logic**: Necessity and possibility
- **Constitutional Logic**: ACGS-specific framework

## Integration Examples

### Python Client

```python
import requests

# Verify policy consistency
response = requests.post(
    "http://localhost:8003/api/v1/verification/policy",
    headers={
        "Authorization": f"Bearer {jwt_token}",
        "X-Constitutional-Hash": "cdd01ef066bc6cf2"
    },
    json={
        "policy": {
            "id": "policy_123",
            "rules": ["rule1", "rule2"],
            "constraints": ["constraint1"],
            "context": "governance"
        },
        "verification_type": "consistency_check"
    }
)

result = response.json()
if result["success"] and result["verified"]:
    print(f"Policy verified with score: {result['verification_score']}")
```

### JavaScript Client

```javascript
const response = await fetch('http://localhost:8003/api/v1/verification/consistency', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${jwtToken}`,
    'X-Constitutional-Hash': 'cdd01ef066bc6cf2',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    statements: ['statement1', 'statement2', 'statement3'],
    logical_framework: 'propositional'
  })
});

const result = await response.json();
console.log('Consistency check:', result.consistent);
```

## Error Handling

### Common Error Codes

| Code | Description | Resolution |
|------|-------------|------------|
| `INVALID_LOGIC` | Malformed logical statement | Check statement syntax |
| `PROOF_FAILED` | Cannot generate proof | Verify premises and theorem |
| `TIMEOUT` | Verification timeout | Simplify problem or increase timeout |
| `UNSUPPORTED_METHOD` | Unknown proof method | Use supported verification method |

## Performance Targets

- **Latency**: P99 ≤ 5ms for cached queries
- **Throughput**: ≥ 100 RPS sustained
- **Cache Hit Rate**: ≥ 85%
- **Test Coverage**: ≥ 80%
- **Availability**: 99.9% uptime
- **Constitutional Compliance**: 100% validation

## Security Features

- **Formal Proof Validation**: Mathematical certainty
- **Constitutional Compliance**: All proofs validate constitutional hash
- **Audit Trail**: Complete verification history
- **Secure Computation**: Isolated verification environment

## Related Documentation

- [API Documentation Index](index.md)
- [Constitutional AI API](constitutional-ai.md)
- [Policy Governance API](policy-governance.md)
- [Constitutional Compliance Framework](../constitutional_compliance_validation_framework.md)

---

**Status**: ✅ Healthy and operational
<!-- Constitutional Hash: cdd01ef066bc6cf2 --> ✅

## Monitoring

Service health and performance metrics:

- Health check endpoint: `/health`
- Metrics endpoint: `/metrics`
- Constitutional compliance status: `/compliance`
- Performance dashboard integration available
