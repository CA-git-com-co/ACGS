# ACGS-2 API Comprehensive Guide

**Constitutional Hash**: `cdd01ef066bc6cf2`

## Overview

The ACGS-2 (Advanced Constitutional Governance System) provides a comprehensive REST API for constitutional AI governance operations. This guide provides practical examples and integration patterns for developers.

## Core Services API Reference

### 1. Constitutional Core Service (Port 8001)

The primary service for constitutional AI reasoning and formal verification.

**Base URL**: `http://localhost:8001`

#### Health Check
```bash
GET /health
```

**Response**:
```json
{
  "status": "healthy",
  "constitutional_hash": "cdd01ef066bc6cf2",
  "timestamp": "2025-01-08T10:30:00Z",
  "service": "constitutional-core",
  "version": "2.0.0"
}
```

#### Constitutional Validation
```bash
POST /api/v1/constitutional/validate
Content-Type: application/json
```

**Request**:
```json
{
  "decision": {
    "description": "AI model deployment for healthcare recommendations",
    "context": {
      "domain": "healthcare",
      "impact_level": "high",
      "affected_populations": ["patients", "healthcare_providers"]
    }
  },
  "tenant_id": "healthcare-org-001"
}
```

**Response**:
```json
{
  "constitutional_hash": "cdd01ef066bc6cf2",
  "validation_result": {
    "compliant": true,
    "compliance_score": 0.94,
    "violations": [],
    "recommendations": [
      "Implement bias monitoring for patient demographics",
      "Ensure explainability for clinical recommendations"
    ]
  },
  "audit_id": "audit_789xyz",
  "timestamp": "2025-01-08T10:30:00Z"
}
```

#### Formal Verification
```bash
POST /api/v1/formal/verify
```

**Request**:
```json
{
  "axioms": [
    "fairness(decision) => no_bias(decision)",
    "transparency(system) => explainable(decision)"
  ],
  "constraints": [
    "accuracy >= 0.85",
    "false_positive_rate <= 0.05"
  ],
  "tenant_id": "research-lab-002"
}
```

**Response**:
```json
{
  "constitutional_hash": "cdd01ef066bc6cf2",
  "verification_result": {
    "satisfiable": true,
    "model": {
      "accuracy": 0.92,
      "false_positive_rate": 0.03,
      "bias_score": 0.02
    },
    "proof_trace": "z3_proof_12345"
  }
}
```

### 2. Integrity Service (Port 8002)

Cryptographic audit trail and compliance logging service.

**Base URL**: `http://localhost:8002`

#### Create Audit Entry
```bash
POST /api/v1/audit/create
```

**Request**:
```json
{
  "event_type": "constitutional_validation",
  "event_data": {
    "service": "constitutional-core",
    "decision_id": "decision_123",
    "compliance_score": 0.94,
    "violations": []
  },
  "tenant_id": "healthcare-org-001",
  "user_id": "user_456"
}
```

**Response**:
```json
{
  "constitutional_hash": "cdd01ef066bc6cf2",
  "audit_id": "audit_789xyz",
  "hash_chain": "sha256:abc123...",
  "timestamp": "2025-01-08T10:30:00Z",
  "status": "recorded"
}
```

#### Query Audit Trail
```bash
GET /api/v1/audit/query?tenant_id=healthcare-org-001&start_date=2025-01-01&event_type=constitutional_validation
```

**Response**:
```json
{
  "constitutional_hash": "cdd01ef066bc6cf2",
  "audit_entries": [
    {
      "audit_id": "audit_789xyz",
      "event_type": "constitutional_validation",
      "timestamp": "2025-01-08T10:30:00Z",
      "event_data": {
        "compliance_score": 0.94,
        "violations": []
      },
      "hash_chain": "sha256:abc123..."
    }
  ],
  "total_count": 1,
  "query_metadata": {
    "execution_time_ms": 15,
    "cache_hit": true
  }
}
```

### 3. Governance Engine (Port 8004)

Policy synthesis and enforcement service with OPA integration.

**Base URL**: `http://localhost:8004`

#### Policy Evaluation
```bash
POST /api/v1/policy/evaluate
```

**Request**:
```json
{
  "policy_type": "constitutional",
  "input": {
    "decision": {
      "type": "ai_model_deployment",
      "domain": "finance",
      "risk_level": "medium"
    },
    "context": {
      "regulatory_framework": "GDPR",
      "jurisdiction": "EU"
    }
  },
  "tenant_id": "fintech-corp-003"
}
```

**Response**:
```json
{
  "constitutional_hash": "cdd01ef066bc6cf2",
  "policy_result": {
    "decision": "allow",
    "score": 0.87,
    "applied_policies": [
      "constitutional_base",
      "gdpr_compliance",
      "financial_regulation"
    ],
    "requirements": [
      "Data minimization required",
      "Consent mechanism needed",
      "Regular bias auditing mandatory"
    ]
  },
  "evaluation_time_ms": 12
}
```

#### Policy Synthesis
```bash
POST /api/v1/policy/synthesize
```

**Request**:
```json
{
  "context": {
    "domain": "healthcare",
    "regulations": ["HIPAA", "FDA"],
    "use_case": "diagnostic_ai"
  },
  "requirements": [
    "patient_privacy",
    "clinical_accuracy",
    "regulatory_compliance"
  ],
  "tenant_id": "healthcare-org-001"
}
```

**Response**:
```json
{
  "constitutional_hash": "cdd01ef066bc6cf2",
  "synthesized_policy": {
    "policy_id": "healthcare_diagnostic_ai_001",
    "rules": [
      {
        "condition": "patient_data_access",
        "action": "require_consent_and_audit"
      },
      {
        "condition": "model_prediction",
        "action": "require_explainability"
      }
    ],
    "compliance_checks": [
      "hipaa_privacy_rule",
      "fda_medical_device_rule"
    ]
  }
}
```

### 4. Authentication Service (Port 8016)

Multi-tenant JWT authentication with constitutional context.

**Base URL**: `http://localhost:8016`

#### Authenticate
```bash
POST /api/v1/auth/login
```

**Request**:
```json
{
  "username": "developer@healthcare-org.com",
  "password": "secure_password",
  "tenant_id": "healthcare-org-001"
}
```

**Response**:
```json
{
  "constitutional_hash": "cdd01ef066bc6cf2",
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "tenant_context": {
    "tenant_id": "healthcare-org-001",
    "constitutional_compliance_level": "high",
    "permissions": ["constitutional.validate", "audit.read"]
  }
}
```

#### Token Validation
```bash
GET /api/v1/auth/validate
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response**:
```json
{
  "constitutional_hash": "cdd01ef066bc6cf2",
  "valid": true,
  "user_context": {
    "user_id": "user_456",
    "tenant_id": "healthcare-org-001",
    "permissions": ["constitutional.validate", "audit.read"],
    "constitutional_compliance_verified": true
  },
  "expires_at": "2025-01-08T11:30:00Z"
}
```

## Integration Patterns

### 1. Complete Constitutional Workflow

```python
import httpx
import asyncio

class ACGSClient:
    def __init__(self, base_url="http://localhost", token=None):
        self.base_url = base_url
        self.token = token
        self.headers = {"Authorization": f"Bearer {token}"} if token else {}

    async def constitutional_validation_workflow(self, decision, tenant_id):
        """Complete workflow: authenticate, validate, audit"""

        # Step 1: Constitutional validation
        async with httpx.AsyncClient() as client:
            validation_response = await client.post(
                f"{self.base_url}:8001/api/v1/constitutional/validate",
                json={"decision": decision, "tenant_id": tenant_id},
                headers=self.headers
            )
            validation_result = validation_response.json()

            # Step 2: Create audit entry
            audit_response = await client.post(
                f"{self.base_url}:8002/api/v1/audit/create",
                json={
                    "event_type": "constitutional_validation",
                    "event_data": validation_result,
                    "tenant_id": tenant_id
                },
                headers=self.headers
            )
            audit_result = audit_response.json()

            return {
                "validation": validation_result,
                "audit": audit_result
            }

# Usage example
async def main():
    client = ACGSClient(token="your_jwt_token")

    decision = {
        "description": "Deploy sentiment analysis model",
        "context": {
            "domain": "social_media",
            "impact_level": "medium"
        }
    }

    result = await client.constitutional_validation_workflow(
        decision,
        "social-platform-004"
    )

    print(f"Constitutional compliance: {result['validation']['validation_result']['compliant']}")
    print(f"Audit ID: {result['audit']['audit_id']}")

# Run the example
asyncio.run(main())
```

### 2. Policy-Driven Decision Making

```javascript
// Node.js/TypeScript example
import axios from 'axios';

class PolicyDrivenDecisionMaker {
    constructor(baseUrl = 'http://localhost', authToken) {
        this.baseUrl = baseUrl;
        this.authHeaders = authToken ? { Authorization: `Bearer ${authToken}` } : {};
    }

    async makePolicyDrivenDecision(context, tenantId) {
        try {
            // Step 1: Get policy evaluation
            const policyResponse = await axios.post(
                `${this.baseUrl}:8004/api/v1/policy/evaluate`,
                {
                    policy_type: 'constitutional',
                    input: context,
                    tenant_id: tenantId
                },
                { headers: this.authHeaders }
            );

            const policyResult = policyResponse.data;

            // Step 2: If approved, proceed with constitutional validation
            if (policyResult.policy_result.decision === 'allow') {
                const constitutionalResponse = await axios.post(
                    `${this.baseUrl}:8001/api/v1/constitutional/validate`,
                    {
                        decision: context.decision,
                        tenant_id: tenantId
                    },
                    { headers: this.authHeaders }
                );

                return {
                    policy_approved: true,
                    constitutional_compliant: constitutionalResponse.data.validation_result.compliant,
                    recommendations: [
                        ...policyResult.policy_result.requirements,
                        ...constitutionalResponse.data.validation_result.recommendations
                    ]
                };
            }

            return {
                policy_approved: false,
                reason: policyResult.policy_result.reason || 'Policy evaluation failed'
            };

        } catch (error) {
            throw new Error(`Policy decision failed: ${error.message}`);
        }
    }
}

// Usage example
const decisionMaker = new PolicyDrivenDecisionMaker('http://localhost', 'your_jwt_token');

const context = {
    decision: {
        type: 'ai_model_deployment',
        domain: 'healthcare',
        risk_level: 'high'
    },
    context: {
        regulatory_framework: 'HIPAA',
        jurisdiction: 'US'
    }
};

decisionMaker.makePolicyDrivenDecision(context, 'healthcare-org-001')
    .then(result => {
        console.log('Decision result:', result);
    })
    .catch(error => {
        console.error('Decision failed:', error);
    });
```

## Error Handling

### Standard Error Format

All ACGS services return errors in a consistent format:

```json
{
  "constitutional_hash": "cdd01ef066bc6cf2",
  "error": {
    "code": "CONSTITUTIONAL_VIOLATION",
    "message": "Decision violates constitutional principles",
    "details": {
      "violations": [
        {
          "principle": "fairness",
          "severity": "high",
          "description": "Detected demographic bias in decision criteria"
        }
      ]
    },
    "timestamp": "2025-01-08T10:30:00Z",
    "request_id": "req_123abc"
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `CONSTITUTIONAL_VIOLATION` | 400 | Decision violates constitutional principles |
| `INVALID_TENANT` | 401 | Invalid or missing tenant context |
| `UNAUTHORIZED` | 401 | Authentication required or invalid |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `VALIDATION_FAILED` | 422 | Request validation failed |
| `FORMAL_VERIFICATION_FAILED` | 422 | Formal verification constraints not satisfied |
| `POLICY_EVALUATION_ERROR` | 500 | Policy evaluation service error |
| `AUDIT_LOGGING_FAILED` | 500 | Failed to create audit entry |

## Rate Limiting

All services implement rate limiting with constitutional compliance tracking:

### Rate Limit Headers

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1641638400
X-Constitutional-Hash: cdd01ef066bc6cf2
X-Constitutional-Compliance-Rate: 0.97
```

### Rate Limit Exceeded Response

```json
{
  "constitutional_hash": "cdd01ef066bc6cf2",
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded",
    "details": {
      "limit": 100,
      "window_seconds": 3600,
      "retry_after": 1800
    }
  }
}
```

## Performance Targets

All APIs are designed to meet these performance standards:

- **P99 Latency**: <5ms for core operations
- **Throughput**: >100 RPS sustained
- **Constitutional Compliance Rate**: >95%
- **Cache Hit Rate**: >85%
- **Availability**: 99.99%

## Authentication

### JWT Token Structure

ACGS JWT tokens include constitutional context:

```json
{
  "sub": "user_456",
  "tenant_id": "healthcare-org-001",
  "constitutional_hash": "cdd01ef066bc6cf2",
  "constitutional_compliance_verified": true,
  "permissions": [
    "constitutional.validate",
    "audit.read",
    "policy.evaluate"
  ],
  "iat": 1641634800,
  "exp": 1641638400
}
```

### Service-to-Service Authentication

For service-to-service communication, use service tokens:

```bash
POST /api/v1/auth/service-token
```

**Request**:
```json
{
  "service_id": "external-ai-service",
  "tenant_id": "healthcare-org-001",
  "requested_scopes": ["constitutional.validate"]
}
```

## SDK Examples

### Python SDK Usage

```python
from acgs_sdk import ACGSClient

# Initialize client
client = ACGSClient(
    base_url="http://localhost",
    tenant_id="healthcare-org-001",
    api_key="your_api_key"
)

# Constitutional validation
result = await client.constitutional.validate({
    "description": "AI diagnostic tool deployment",
    "context": {"domain": "healthcare", "risk_level": "high"}
})

# Check compliance
if result.compliant:
    print(f"Compliant with score: {result.compliance_score}")
else:
    print(f"Violations: {result.violations}")
```

### TypeScript SDK Usage

```typescript
import { ACGSClient } from '@acgs/sdk';

const client = new ACGSClient({
    baseUrl: 'http://localhost',
    tenantId: 'healthcare-org-001',
    apiKey: 'your_api_key'
});

// Policy evaluation with constitutional validation
const decision = await client.governance.evaluateWithConstitutional({
    policyType: 'constitutional',
    input: {
        decision: {
            type: 'ai_model_deployment',
            domain: 'healthcare'
        }
    }
});

console.log(`Decision: ${decision.approved ? 'Approved' : 'Rejected'}`);
```

## Testing Your Integration

### Health Check All Services

```bash
#!/bin/bash
# health-check.sh

services=(
    "8001:Constitutional Core"
    "8002:Integrity Service"
    "8004:Governance Engine"
    "8006:Evolutionary Computation"
    "8016:Authentication"
)

for service in "${services[@]}"; do
    port="${service%%:*}"
    name="${service##*:}"

    if curl -f "http://localhost:${port}/health" > /dev/null 2>&1; then
        echo "✓ ${name} (${port}): Healthy"
    else
        echo "✗ ${name} (${port}): Unhealthy"
    fi
done
```

### Integration Test Example

```python
import pytest
import httpx

@pytest.mark.asyncio
async def test_constitutional_workflow():
    """Test complete constitutional validation workflow"""

    # Authenticate
    auth_response = await httpx.AsyncClient().post(
        "http://localhost:8016/api/v1/auth/login",
        json={
            "username": "test@example.com",
            "password": "test_password",
            "tenant_id": "test-tenant"
        }
    )
    assert auth_response.status_code == 200
    token = auth_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    # Constitutional validation
    validation_response = await httpx.AsyncClient().post(
        "http://localhost:8001/api/v1/constitutional/validate",
        json={
            "decision": {
                "description": "Test AI deployment",
                "context": {"domain": "test", "impact_level": "low"}
            },
            "tenant_id": "test-tenant"
        },
        headers=headers
    )

    assert validation_response.status_code == 200
    result = validation_response.json()
    assert "constitutional_hash" in result
    assert result["constitutional_hash"] == "cdd01ef066bc6cf2"
    assert "validation_result" in result
```

---

**Constitutional Hash**: `cdd01ef066bc6cf2`
**Last Updated**: 2025-01-08
**API Version**: 2.0.0
