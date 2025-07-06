# Integrity Service API

## Service Overview

This service provides core functionality for the ACGS platform with constitutional compliance validation.

**Service**: Integrity
**Port**: 8XXX
**Constitutional Hash**: `cdd01ef066bc6cf2`


**Service**: Integrity Service
**Port**: 8002
**Base URL**: `http://localhost:8002/api/v1`
<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

## Overview

The Integrity Service provides cryptographic verification, data integrity validation, and secure hash operations for the ACGS system. It ensures all data and operations maintain cryptographic integrity and constitutional compliance.

## Authentication

All endpoints require JWT authentication:

```http
Authorization: Bearer <jwt_token>
X-Constitutional-Hash: cdd01ef066bc6cf2
```

## Performance Targets

- **Latency**: P99 ≤ 5ms for cached queries
- **Throughput**: ≥ 100 RPS sustained
- **Cache Hit Rate**: ≥ 85%
- **Test Coverage**: ≥ 80%
- **Availability**: 99.9% uptime
- **Constitutional Compliance**: 100% validation

## Endpoints

### Health Check

```http
GET /health
```

**Response**:
```json
{
  "status": "healthy",
  "service": "integrity_service",
  "constitutional_hash": "cdd01ef066bc6cf2",
  "timestamp": "2025-07-05T12:00:00Z"
}
```

### Data Integrity Validation

```http
POST /integrity/validate
```

**Request**:
```json
{
  "data": "base64_encoded_data",
  "hash": "sha256_hash",
  "signature": "digital_signature"
,
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Response**:
```json
{
  "success": true,
  "valid": true,
  "integrity_score": 1.0,
  "constitutional_hash": "cdd01ef066bc6cf2",
  "validation_details": {
    "hash_match": true,
    "signature_valid": true,
    "timestamp_valid": true
  }
}
```

### Cryptographic Hash Generation

```http
POST /integrity/hash
```

**Request**:
```json
{
  "data": "data_to_hash",
  "algorithm": "sha256",
  "include_constitutional": true
,
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Response**:
```json
{
  "success": true,
  "hash": "generated_hash",
  "algorithm": "sha256",
  "constitutional_hash": "cdd01ef066bc6cf2",
  "timestamp": "2025-07-05T12:00:00Z"
}
```

### Digital Signature Operations

```http
POST /integrity/sign
```

**Request**:
```json
{
  "data": "data_to_sign",
  "key_id": "signing_key_identifier"
,
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Response**:
```json
{
  "success": true,
  "signature": "digital_signature",
  "key_id": "signing_key_identifier",
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

### Signature Verification

```http
POST /integrity/verify
```

**Request**:
```json
{
  "data": "original_data",
  "signature": "digital_signature",
  "public_key": "verification_key"
,
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Response**:
```json
{
  "success": true,
  "valid": true,
  "verification_details": {
    "signature_valid": true,
    "key_trusted": true,
    "timestamp_valid": true
  ,
  "constitutional_hash": "cdd01ef066bc6cf2"
},
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

### Constitutional Compliance Check

```http
POST /integrity/constitutional
```

**Request**:
```json
{
  "operation": "policy_validation",
  "data": "operation_data",
  "context": "governance_context"
,
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Response**:
```json
{
  "success": true,
  "compliant": true,
  "compliance_score": 0.98,
  "constitutional_hash": "cdd01ef066bc6cf2",
  "validation_details": {
    "hash_verified": true,
    "policy_compliant": true,
    "context_valid": true
  }
}
```

## Error Responses

### 400 Bad Request
```json
{
  "success": false,
  "error": "Invalid data format",
  "code": "INVALID_DATA",
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

### 401 Unauthorized
```json
{
  "success": false,
  "error": "Authentication required",
  "code": "AUTH_REQUIRED",
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

### 500 Internal Server Error
```json
{
  "success": false,
  "error": "Cryptographic operation failed",
  "code": "CRYPTO_ERROR",
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

## Performance Specifications

| Metric | Target | Current |
|--------|--------|---------|
| **Response Time** | P99 ≤5ms | 0.007s |
| **Throughput** | ≥100 RPS | High |
| **Availability** | ≥99.9% | ⚠️ HTTP 500 errors |
| **Cryptographic Operations** | ≤10ms | Optimized |

## Security Features

- **End-to-End Encryption**: All data encrypted in transit
- **Digital Signatures**: RSA/ECDSA signature support
- **Hash Algorithms**: SHA-256, SHA-512, Blake2b
- **Key Management**: Secure key storage and rotation
- **Constitutional Validation**: All operations validate constitutional hash

## Integration Examples

### Python Client

```python
import requests

# Validate data integrity
response = requests.post(
    "http://localhost:8002/api/v1/integrity/validate",
    headers={
        "Authorization": f"Bearer {jwt_token}",
        "X-Constitutional-Hash": "cdd01ef066bc6cf2"
    },
    json={
        "data": "base64_data",
        "hash": "sha256_hash",
        "signature": "digital_signature"
    }
)

result = response.json()
if result["success"] and result["valid"]:
    print("Data integrity validated")
```

### JavaScript Client

```javascript
const response = await fetch('http://localhost:8002/api/v1/integrity/hash', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${jwtToken}`,
    'X-Constitutional-Hash': 'cdd01ef066bc6cf2',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    data: 'data_to_hash',
    algorithm: 'sha256',
    include_constitutional: true
  })
});

const result = await response.json();
console.log('Generated hash:', result.hash);
```

## Troubleshooting

### Common Issues

1. **HTTP 500 Errors**: Service currently experiencing internal errors
   - Check service logs: `docker logs acgs_integrity_service`
   - Restart service: `docker restart acgs_integrity_service`

2. **Slow Response Times**: Cryptographic operations taking too long
   - Check system resources
   - Verify key storage accessibility

3. **Authentication Failures**: JWT token issues
   - Verify token validity
   - Check constitutional hash in headers

## Related Documentation

- [API Documentation Index](index.md)
- [Authentication API](authentication.md)
- [Constitutional AI API](constitutional-ai.md)
- [Service Status](../operations/SERVICE_STATUS.md)

---

**Status**: ⚠️ Service experiencing HTTP 500 errors - troubleshooting in progress
<!-- Constitutional Hash: cdd01ef066bc6cf2 --> ✅

## Error Handling

Standard HTTP status codes are used with detailed error messages:

- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

All errors include constitutional compliance validation status.


## Monitoring

Service health and performance metrics:

- Health check endpoint: `/health`
- Metrics endpoint: `/metrics`
- Constitutional compliance status: `/compliance`
- Performance dashboard integration available
