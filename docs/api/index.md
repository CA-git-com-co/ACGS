# ACGS API Documentation Index

<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

## 1. Overview

This document serves as the central index for all API documentation within the Autonomous Coding Governance System (ACGS). It provides quick navigation to individual service APIs, outlines the common API architecture, and details authentication flows and performance specifications.

- **Last Updated**: 2025-07-07
- **API Version**: v1
- **Constitutional Hash**: `cdd01ef066bc6cf2`

## 2. Quick Navigation

### 2.1. Core Service APIs

| Service | Port | Documentation | Status |
|---------|------|---------------|--------|
| **Authentication** | 8016 | [Authentication API](authentication.md) | ✅ Available |
| **Constitutional AI** | 8001 | [Constitutional AI API](constitutional-ai.md) | ✅ Available |
| **Integrity Service** | 8002 | [Integrity API](integrity.md) | ✅ Available |
| **Formal Verification** | 8003 | [Formal Verification API](formal-verification.md) | ✅ Available |
| **Governance Synthesis** | 8004 | [Governance Synthesis API](governance_synthesis.md) | ✅ Available |
| **Policy Governance** | 8005 | [Policy Governance API](policy-governance.md) | ✅ Available |
| **Evolutionary Computation** | 8006 | [Evolutionary Computation API](evolutionary-computation.md) | ✅ Available |

### 2.2. Integration APIs

| API | Documentation | Purpose |
|-----|---------------|---------|
| **Cross-Service Integration** | [Integration Guide](../integration/ACGS_SERVICE_INTEGRATION_GUIDE.md) | Service-to-service communication |
| **JWT Token Management** | [JWT Reference](jwt.md) | Token handling and validation |
| **Role-Based Access Control** | [RBAC Design](rbac.md) | Permission and role management |

## 3. API Architecture

### 3.1. Base URLs

- **Production**: `https://acgs.example.com:<port>/api/v1`
- **Development**: `http://localhost:<port>/api/v1`

### 3.2. Common Headers

All API requests should include the following headers:

```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
X-Constitutional-Hash: cdd01ef066bc6cf2
X-Request-ID: <unique_request_id>
```

### 3.3. Standard Response Format

All successful API responses adhere to the following format:

```json
{
  "success": true,
  "data": {},
  "constitutional_hash": "cdd01ef066bc6cf2",
  "timestamp": "2025-07-07T12:00:00Z",
  "request_id": "req_123456789"
}
```

## 4. Authentication Flow

1. **Login**: Authenticate via `POST /auth/login` to obtain a JWT token.
2. **Token Validation**: Include the JWT token in the `Authorization` header for all subsequent requests.
3. **Constitutional Compliance**: The `X-Constitutional-Hash` header must be present and valid in all requests and responses.
4. **Token Refresh**: Use `POST /auth/refresh` to obtain a new JWT token when the current one expires.

## 5. Performance Specifications

| Metric | Target | Monitoring |
|--------|--------|------------|
| **Response Time** | P99 ≤5ms | `/metrics` endpoint |
| **Throughput** | ≥100 RPS | Load balancer metrics |

## 6. Development Resources

### 6.1. OpenAPI Specifications

- [ACGS Code Analysis Engine API](../architecture/ACGS_CODE_ANALYSIS_ENGINE_ARCHITECTURE.md)
- Additional OpenAPI specs are available per service.

### 6.2. Testing

To perform health checks on all services:

```bash
curl http://localhost:8016/health  # Auth
curl http://localhost:8001/health  # Constitutional AI
curl http://localhost:8002/health  # Integrity
curl http://localhost:8003/health  # Formal Verification
curl http://localhost:8004/health  # Governance Synthesis
curl http://localhost:8005/health  # Policy Governance
curl http://localhost:8006/health  # Evolutionary Computation
```

### 6.3. Error Handling

All APIs follow standard HTTP status codes:

| Status | Meaning | Response |
|--------|---------|-------

## Implementation Status

- ✅ **Constitutional Hash Validation**: Active enforcement of `cdd01ef066bc6cf2`
- 🔄 **Performance Monitoring**: Continuous validation of targets
- ✅ **Documentation Standards**: Compliant with ACGS-2 requirements
- 🔄 **Cross-Reference Validation**: Ongoing link integrity maintenance

**Overall Status**: 🔄 IN PROGRESS - Systematic enhancement implementation

## Performance Targets

This component maintains the following performance requirements:

- **P99 Latency**: <5ms (constitutional requirement)
- **Throughput**: >100 RPS (minimum operational standard)
- **Cache Hit Rate**: >85% (efficiency requirement)
- **Constitutional Compliance**: 100% (hash: cdd01ef066bc6cf2)

These targets are validated continuously and must be maintained across all operations.

---|
| 200 | Success | Standard response format |
| 400 | Bad Request | Validation errors |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 500 | Internal Error | Server error |

## 7. Additional Resources

- [Configuration Guide](../configuration/README.md)
- [Deployment Guide](../deployment/ACGS_PGP_SETUP_GUIDE.md)
- [Service Status](../operations/SERVICE_STATUS.md)
- [Architecture Documentation](../architecture/README.md)

## 8. Related Information

For a broader understanding of the ACGS platform and its components, refer to:

- [ACGS Service Architecture Overview](../ACGS_SERVICE_OVERVIEW.md)
- [ACGS System Overview](../../SYSTEM_OVERVIEW.md)
