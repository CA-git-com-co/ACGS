# ACGS Comprehensive API Documentation

**Version:** 3.0.0  
**Date:** July 1, 2025  
**Constitutional Hash:** cdd01ef066bc6cf2  

## Overview

The Autonomous Coding Governance System (ACGS) provides a comprehensive REST API for enterprise integration. This documentation covers all available endpoints, authentication methods, and integration patterns.

## Base URLs

- **Production:** `https://api.acgs.enterprise.com/v3`
- **Staging:** `https://staging-api.acgs.enterprise.com/v3`
- **Development:** `http://localhost:8000/v3`

## Authentication

### API Key Authentication

```http
Authorization: Bearer YOUR_API_KEY
X-Constitutional-Hash: cdd01ef066bc6cf2
```

### JWT Token Authentication

```http
Authorization: Bearer YOUR_JWT_TOKEN
X-Constitutional-Hash: cdd01ef066bc6cf2
```

### OAuth 2.0 (Enterprise)

```http
Authorization: Bearer YOUR_OAUTH_TOKEN
X-Constitutional-Hash: cdd01ef066bc6cf2
```

## Core API Endpoints

### Authentication Service (Port 8016)

#### POST /auth/login
Authenticate user and obtain access token.

**Request:**
```json
{
  "username": "user@company.com",
  "password": "secure_password",
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "constitutional_compliance": true,
  "user_id": "user_123"
}
```

#### POST /auth/refresh
Refresh access token.

**Request:**
```json
{
  "refresh_token": "refresh_token_here",
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

#### GET /auth/validate
Validate current token.

**Response:**
```json
{
  "valid": true,
  "user_id": "user_123",
  "expires_at": "2025-07-01T12:00:00Z",
  "constitutional_compliance": true
}
```

### Constitutional AI Service (Port 8002)

#### POST /constitutional/validate
Validate content against constitutional policies.

**Request:**
```json
{
  "content": "Code or policy content to validate",
  "policy_set": "enterprise_policies_v3",
  "validation_level": "strict",
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Response:**
```json
{
  "validation_id": "val_123456",
  "compliant": true,
  "compliance_score": 0.987,
  "violations": [],
  "recommendations": [
    "Consider adding error handling for edge cases"
  ],
  "constitutional_hash": "cdd01ef066bc6cf2",
  "processing_time_ms": 2.3
}
```

#### GET /constitutional/policies
List available constitutional policies.

**Response:**
```json
{
  "policies": [
    {
      "id": "safety_v3",
      "name": "Safety Policies",
      "version": "3.0.0",
      "description": "Core safety requirements",
      "rules_count": 47
    },
    {
      "id": "fairness_v3",
      "name": "Fairness Policies",
      "version": "3.0.0",
      "description": "Fairness and bias prevention",
      "rules_count": 23
    }
  ],
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

#### POST /constitutional/policies
Create new constitutional policy.

**Request:**
```json
{
  "name": "Custom Enterprise Policy",
  "description": "Company-specific governance rules",
  "rules": [
    {
      "id": "rule_001",
      "condition": "code.contains('sensitive_data')",
      "action": "require_encryption",
      "severity": "high"
    }
  ],
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

### Policy Governance Service (Port 8003)

#### GET /governance/status
Get governance system status.

**Response:**
```json
{
  "status": "operational",
  "active_policies": 24,
  "compliance_rate": 99.2,
  "last_update": "2025-07-01T10:30:00Z",
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

#### POST /governance/evaluate
Evaluate governance decision.

**Request:**
```json
{
  "context": {
    "user_id": "user_123",
    "action": "deploy_code",
    "resource": "production_environment"
  },
  "policies": ["safety_v3", "security_v3"],
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Response:**
```json
{
  "decision": "approved",
  "confidence": 0.95,
  "applied_policies": ["safety_v3", "security_v3"],
  "conditions": [
    "Requires security review within 24 hours"
  ],
  "constitutional_compliance": true
}
```

### Formal Verification Service (Port 8005)

#### POST /verification/verify
Perform formal verification of code or policies.

**Request:**
```json
{
  "content": "function_to_verify()",
  "verification_type": "safety_properties",
  "properties": [
    "no_null_pointer_dereference",
    "memory_safety",
    "constitutional_compliance"
  ],
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Response:**
```json
{
  "verification_id": "ver_789012",
  "status": "verified",
  "properties_verified": [
    {
      "property": "no_null_pointer_dereference",
      "verified": true,
      "confidence": 0.99
    },
    {
      "property": "memory_safety",
      "verified": true,
      "confidence": 0.97
    }
  ],
  "constitutional_compliance": true,
  "verification_time_ms": 45.2
}
```

## Error Handling

### Standard Error Response

```json
{
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "Constitutional validation failed",
    "details": {
      "violations": ["Policy rule safety_001 violated"],
      "constitutional_hash_mismatch": false
    },
    "request_id": "req_123456",
    "timestamp": "2025-07-01T10:30:00Z"
  }
}
```

### HTTP Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request parameters
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Constitutional validation failed
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - Service temporarily unavailable

## Rate Limiting

- **Standard Tier:** 1,000 requests/hour
- **Professional Tier:** 10,000 requests/hour
- **Enterprise Tier:** 100,000 requests/hour

Rate limit headers:
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1625097600
```

## Webhooks

### Constitutional Compliance Events

```json
{
  "event": "constitutional.compliance.violation",
  "data": {
    "violation_id": "viol_123456",
    "policy_id": "safety_v3",
    "severity": "high",
    "user_id": "user_123",
    "timestamp": "2025-07-01T10:30:00Z",
    "constitutional_hash": "cdd01ef066bc6cf2"
  }
}
```

### Policy Update Events

```json
{
  "event": "policy.updated",
  "data": {
    "policy_id": "fairness_v3",
    "version": "3.1.0",
    "changes": ["Added new bias detection rule"],
    "effective_date": "2025-07-01T12:00:00Z",
    "constitutional_hash": "cdd01ef066bc6cf2"
  }
}
```

## SDK Examples

### Python SDK

```python
from acgs_sdk import ACGSClient

# Initialize client
client = ACGSClient(
    api_key="your_api_key",
    base_url="https://api.acgs.enterprise.com/v3",
    constitutional_hash="cdd01ef066bc6cf2"
)

# Validate content
result = client.constitutional.validate(
    content="def secure_function(): pass",
    policy_set="enterprise_policies_v3"
)

print(f"Compliant: {result.compliant}")
print(f"Score: {result.compliance_score}")
```

### JavaScript SDK

```javascript
import { ACGSClient } from '@acgs/sdk';

// Initialize client
const client = new ACGSClient({
  apiKey: 'your_api_key',
  baseURL: 'https://api.acgs.enterprise.com/v3',
  constitutionalHash: 'cdd01ef066bc6cf2'
});

// Validate content
const result = await client.constitutional.validate({
  content: 'function secureFunction() {}',
  policySet: 'enterprise_policies_v3'
});

console.log(`Compliant: ${result.compliant}`);
console.log(`Score: ${result.complianceScore}`);
```

### Java SDK

```java
import com.acgs.sdk.ACGSClient;
import com.acgs.sdk.models.ValidationRequest;

// Initialize client
ACGSClient client = new ACGSClient.Builder()
    .apiKey("your_api_key")
    .baseUrl("https://api.acgs.enterprise.com/v3")
    .constitutionalHash("cdd01ef066bc6cf2")
    .build();

// Validate content
ValidationRequest request = new ValidationRequest()
    .content("public void secureMethod() {}")
    .policySet("enterprise_policies_v3");

ValidationResult result = client.constitutional().validate(request);
System.out.println("Compliant: " + result.isCompliant());
```

## Integration Patterns

### Synchronous Validation

```python
# Real-time validation during development
def validate_code_change(code):
    result = client.constitutional.validate(
        content=code,
        validation_level="strict"
    )
    
    if not result.compliant:
        raise ValidationError(result.violations)
    
    return result
```

### Asynchronous Processing

```python
# Batch processing for large codebases
async def validate_codebase(files):
    tasks = []
    for file in files:
        task = client.constitutional.validate_async(
            content=file.content,
            policy_set="enterprise_policies_v3"
        )
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return results
```

### CI/CD Integration

```yaml
# GitHub Actions example
- name: ACGS Constitutional Validation
  uses: acgs/github-action@v3
  with:
    api-key: ${{ secrets.ACGS_API_KEY }}
    policy-set: enterprise_policies_v3
    constitutional-hash: cdd01ef066bc6cf2
    fail-on-violation: true
```

## Performance Considerations

### Caching

- Validation results cached for 1 hour by default
- Cache key includes content hash and policy version
- Cache hit rate: >95% in typical enterprise environments

### Latency Optimization

- P99 latency: <5ms for cached results
- P99 latency: <50ms for new validations
- Batch validation available for multiple items

### Scaling

- Auto-scaling based on request volume
- Multi-region deployment available
- CDN integration for global performance

## Security

### Data Protection

- All data encrypted in transit (TLS 1.3)
- Sensitive data encrypted at rest (AES-256)
- No customer code stored permanently

### Access Control

- Role-based access control (RBAC)
- API key scoping and rotation
- Audit logging for all operations

### Constitutional Compliance

- All operations validated against constitutional hash
- Compliance violations logged and reported
- Automatic policy enforcement

## Support and Resources

### Documentation

- **API Reference:** https://docs.acgs.ai/api/v3
- **SDK Documentation:** https://docs.acgs.ai/sdks
- **Integration Guides:** https://docs.acgs.ai/integrations

### Support Channels

- **Enterprise Support:** api-support@acgs.ai
- **Community Forum:** https://community.acgs.ai/api
- **GitHub Issues:** https://github.com/acgs/api-issues

### Status and Monitoring

- **Status Page:** https://status.acgs.ai
- **API Metrics:** https://metrics.acgs.ai
- **Incident Reports:** https://incidents.acgs.ai

---

**Document Version:** 3.0.0  
**Last Updated:** July 1, 2025  
**Constitutional Hash:** cdd01ef066bc6cf2  
**API Version:** v3.0.0
