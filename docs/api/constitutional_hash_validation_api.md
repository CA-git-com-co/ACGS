# ACGS-1 Constitutional Hash Validation API Documentation

**Version**: v3.0.0  
**Last Updated**: 2025-06-15  
**Service**: PGC Service (Policy Governance Control)  
**Base URL**: `http://localhost:8005`  

## Overview

The Constitutional Hash Validation API provides enterprise-grade constitutional compliance validation for the ACGS-1 Constitutional Governance System. All endpoints validate against the constitutional reference hash `cdd01ef066bc6cf2` with ultra-low latency performance targets.

## Authentication

All endpoints require valid JWT authentication:
```bash
Authorization: Bearer <jwt_token>
```

## Performance Targets

- **Validation Latency**: ≤5ms for 95% of operations
- **Middleware Latency**: ≤2ms for 95% of requests  
- **Compliance Accuracy**: ≥95%
- **Availability**: >99.5%
- **Cache Hit Rate**: >80%

## Constitutional Hash Validation Endpoints

### GET /api/v1/constitutional/validate

Validate constitutional hash with comprehensive compliance checking.

**Request Parameters:**
```json
{
  "hash": "string (optional)",
  "validation_level": "basic|standard|comprehensive|critical",
  "operation_type": "string",
  "context": {
    "user_id": "string",
    "session_id": "string",
    "request_id": "string"
  }
}
```

**Response:**
```json
{
  "status": "valid|invalid|error",
  "hash_valid": true,
  "compliance_score": 0.98,
  "validation_timestamp": 1734567890.123,
  "validation_level": "comprehensive",
  "constitutional_hash": "cdd01ef066bc6cf2",
  "integrity_signature": "hmac_sha256_signature",
  "violations": [],
  "recommendations": [],
  "performance_metrics": {
    "validation_latency_ms": 3.2,
    "cache_hit": true,
    "circuit_breaker_status": "closed"
  }
}
```

**Example Request:**
```bash
curl -X GET "http://localhost:8005/api/v1/constitutional/validate" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "validation_level": "comprehensive",
    "operation_type": "policy_validation",
    "context": {
      "user_id": "user123",
      "session_id": "session456"
    }
  }'
```

### GET /api/v1/constitutional/state

Get current constitutional state and system metrics.

**Response:**
```json
{
  "constitutional_hash": "cdd01ef066bc6cf2",
  "framework_version": "v2.0.0",
  "governance_protocol": "ACGS-1 Enterprise Standards",
  "system_status": "operational",
  "validation_statistics": {
    "total_validations": 15420,
    "successful_validations": 15398,
    "failed_validations": 22,
    "average_latency_ms": 2.8,
    "cache_hit_rate": 0.847
  },
  "circuit_breaker_status": {
    "status": "closed",
    "failure_count": 0,
    "last_failure": null
  },
  "performance_metrics": {
    "p50_latency_ms": 2.1,
    "p95_latency_ms": 4.3,
    "p99_latency_ms": 7.8,
    "availability_percentage": 99.97
  }
}
```

### POST /api/v1/constitutional/validate-policy

Validate policy compliance against constitutional framework.

**Request Body:**
```json
{
  "policy_data": {
    "policy_id": "POL-001",
    "title": "Data Privacy Policy",
    "content": "Policy content...",
    "constitutional_hash": "cdd01ef066bc6cf2",
    "metadata": {
      "version": "1.0",
      "author": "policy_author",
      "created_at": "2025-06-15T10:00:00Z"
    }
  },
  "validation_level": "comprehensive",
  "context": {
    "operation_type": "policy_creation",
    "user_id": "user123",
    "session_id": "session456"
  }
}
```

**Response:**
```json
{
  "policy_compliance": {
    "status": "compliant",
    "compliance_score": 0.96,
    "constitutional_alignment": true,
    "policy_id": "POL-001"
  },
  "constitutional_validation": {
    "hash_valid": true,
    "constitutional_hash": "cdd01ef066bc6cf2",
    "integrity_verified": true
  },
  "validation_details": {
    "violations": [],
    "recommendations": [
      "Consider adding explicit data retention clauses",
      "Enhance user consent mechanisms"
    ],
    "compliance_checks": [
      {
        "check_type": "constitutional_alignment",
        "status": "passed",
        "score": 0.98
      },
      {
        "check_type": "policy_structure",
        "status": "passed", 
        "score": 0.94
      }
    ]
  },
  "performance_metrics": {
    "validation_latency_ms": 4.7,
    "total_checks": 12,
    "cache_utilization": true
  }
}
```

## Validation Levels

### Basic Validation
- **Latency Target**: <2ms
- **Checks**: Constitutional hash verification only
- **Use Case**: High-frequency operations, real-time validation

### Standard Validation  
- **Latency Target**: <5ms
- **Checks**: Hash verification + basic compliance checks
- **Use Case**: Regular policy operations, standard workflows

### Comprehensive Validation
- **Latency Target**: <10ms
- **Checks**: Full constitutional compliance analysis
- **Use Case**: Policy creation, constitutional amendments

### Critical Validation
- **Latency Target**: <15ms
- **Checks**: Maximum security validation with formal verification
- **Use Case**: Constitutional changes, emergency procedures

## Error Handling

### Error Response Format
```json
{
  "error": {
    "code": "CONSTITUTIONAL_VALIDATION_ERROR",
    "message": "Constitutional hash validation failed",
    "details": {
      "provided_hash": "invalid_hash",
      "expected_hash": "cdd01ef066bc6cf2",
      "validation_level": "comprehensive"
    },
    "timestamp": 1734567890.123,
    "request_id": "req_123456"
  }
}
```

### Common Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `INVALID_CONSTITUTIONAL_HASH` | Provided hash doesn't match reference | 400 |
| `VALIDATION_TIMEOUT` | Validation exceeded time limit | 408 |
| `CIRCUIT_BREAKER_OPEN` | Service temporarily unavailable | 503 |
| `INSUFFICIENT_PERMISSIONS` | User lacks validation permissions | 403 |
| `INVALID_VALIDATION_LEVEL` | Unsupported validation level | 400 |
| `POLICY_COMPLIANCE_FAILURE` | Policy violates constitutional principles | 422 |

## Security Features

### HMAC-SHA256 Integrity Verification
All constitutional operations include HMAC-SHA256 signatures for integrity verification:
```json
{
  "integrity_signature": "hmac_sha256_signature",
  "signature_algorithm": "HMAC-SHA256",
  "signature_timestamp": 1734567890.123
}
```

### Circuit Breaker Protection
Automatic circuit breaker protection prevents cascade failures:
- **Failure Threshold**: 5 consecutive failures
- **Timeout**: 30 seconds
- **Half-Open State**: Gradual recovery testing

### Audit Logging
All constitutional validation operations are logged:
```json
{
  "audit_log": {
    "operation_id": "op_123456",
    "user_id": "user123",
    "operation_type": "constitutional_validation",
    "timestamp": 1734567890.123,
    "result": "success",
    "latency_ms": 3.2
  }
}
```

## Rate Limiting

- **Standard Users**: 1000 requests/minute
- **Premium Users**: 5000 requests/minute  
- **System Services**: 10000 requests/minute
- **Emergency Operations**: Unlimited

## Monitoring Headers

All responses include monitoring headers:
```
X-Constitutional-Hash: cdd01ef066bc6cf2
X-Constitutional-Validation: passed
X-Validation-Latency-Ms: 3.2
X-Cache-Status: hit
X-Circuit-Breaker-Status: closed
```

## SDK Examples

### Python SDK
```python
from acgs_client import ACGSClient

client = ACGSClient(base_url="http://localhost:8005", token="jwt_token")

# Validate constitutional hash
result = await client.constitutional.validate(
    validation_level="comprehensive",
    operation_type="policy_validation"
)

# Validate policy compliance
policy_result = await client.constitutional.validate_policy(
    policy_data={
        "policy_id": "POL-001",
        "content": "Policy content...",
        "constitutional_hash": "cdd01ef066bc6cf2"
    }
)
```

### JavaScript SDK
```javascript
import { ACGSClient } from '@acgs/client';

const client = new ACGSClient({
  baseURL: 'http://localhost:8005',
  token: 'jwt_token'
});

// Validate constitutional hash
const result = await client.constitutional.validate({
  validationLevel: 'comprehensive',
  operationType: 'policy_validation'
});

// Get constitutional state
const state = await client.constitutional.getState();
```

## Integration Examples

### Middleware Integration
```python
from fastapi import FastAPI, Request
from acgs_middleware import ConstitutionalValidationMiddleware

app = FastAPI()

# Add constitutional validation middleware
app.add_middleware(
    ConstitutionalValidationMiddleware,
    constitutional_hash="cdd01ef066bc6cf2",
    performance_target_ms=2.0,
    bypass_paths=["/health", "/metrics"]
)
```

### Service-to-Service Integration
```python
import httpx

async def validate_constitutional_compliance(policy_data: dict) -> bool:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8005/api/v1/constitutional/validate-policy",
            json={
                "policy_data": policy_data,
                "validation_level": "comprehensive"
            },
            headers={"Authorization": f"Bearer {jwt_token}"}
        )
        
        result = response.json()
        return result["policy_compliance"]["status"] == "compliant"
```

---

**API Status**: ✅ **PRODUCTION READY**  
**Documentation Version**: v3.0.0  
**Last Validated**: 2025-06-15 22:45:00 UTC
