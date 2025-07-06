# ACGS API Documentation Index

<!-- Constitutional Hash: cdd01ef066bc6cf2 -->  
**Last Updated**: 2025-07-05  
**API Version**: v1

## 🎯 Quick Navigation

### Core Service APIs

| Service | Port | Documentation | Status |
|---------|------|---------------|--------|
| **Authentication** | 8016 | [Authentication API](authentication.md) | ✅ Available |
| **Constitutional AI** | 8001 | [Constitutional AI API](constitutional-ai.md) | ✅ Available |
| **Integrity Service** | 8002 | [Integrity API](integrity.md) | ✅ Available |
| **Formal Verification** | 8003 | [Formal Verification API](formal-verification.md) | ✅ Available |
| **Governance Synthesis** | 8004 | [Governance Synthesis API](governance_synthesis.md) | 📝 Planned |
| **Policy Governance** | 8005 | [Policy Governance API](policy-governance.md) | ✅ Available |
| **Evolutionary Computation** | 8006 | [Evolutionary Computation API](evolutionary-computation.md) | ✅ Available |

### Integration APIs

| API | Documentation | Purpose |
|-----|---------------|---------|
| **Cross-Service Integration** | [Integration API](api/index.md) | Service-to-service communication |
| **Audit Logging** | [Audit Logging API](api/index.md) | Compliance and audit trails |
| **JWT Token Management** | [JWT Reference](api/authentication.md) | Token handling and validation |
| **Role-Based Access Control** | [RBAC Design](api/authentication.md) | Permission and role management |

## 🏗️ API Architecture

### Base URLs

```
Production:
- Authentication: https://acgs.example.com:8016/api/v1
- Constitutional AI: https://acgs.example.com:8001/api/v1
- Other Services: https://acgs.example.com:<port>/api/v1

Development:
- Authentication: http://localhost:8016/api/v1
- Constitutional AI: http://localhost:8001/api/v1
- Other Services: http://localhost:<port>/api/v1
```

### Common Headers

```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
X-Constitutional-Hash: cdd01ef066bc6cf2
X-Request-ID: <unique_request_id>
```

### Standard Response Format

```json
{
  "success": true,
  "data": {,
  "constitutional_hash": "cdd01ef066bc6cf2"
},
  "constitutional_hash": "cdd01ef066bc6cf2",
  "timestamp": "2025-07-05T12:00:00Z",
  "request_id": "req_123456789"
}
```

## 🔐 Authentication Flow

1. **Login**: POST `/auth/login` → JWT token
2. **Token Validation**: Include in `Authorization` header
3. **Constitutional Compliance**: Validate hash in all responses
4. **Refresh**: POST `/auth/refresh` → New JWT token

## 📊 Performance Specifications

| Metric | Target | Monitoring |
|--------|--------|------------|
| **Response Time** | P99 ≤5ms | `/metrics` endpoint |
| **Throughput** | ≥100 RPS | Load balancer metrics |
| **Availability** | ≥99.9% | Health check endpoints |
| **Constitutional Compliance** | 100% | Hash validation |

## 🛠️ Development Resources

### OpenAPI Specifications

- [ACGS Code Analysis Engine API](ACGS_CODE_ANALYSIS_ENGINE_API_SPECIFICATION.yaml)
- Additional OpenAPI specs available per service

### Testing

```bash
# Health check all services
curl http://localhost:8016/health  # Auth
curl http://localhost:8001/health  # Constitutional AI
curl http://localhost:8002/health  # Integrity
curl http://localhost:8003/health  # Formal Verification
curl http://localhost:8004/health  # Governance Synthesis
curl http://localhost:8005/health  # Policy Governance
curl http://localhost:8006/health  # Evolutionary Computation
```

### Error Handling

All APIs follow standard HTTP status codes:

| Status | Meaning | Response |
|--------|---------|----------|
| 200 | Success | Standard response format |
| 400 | Bad Request | Validation errors |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 500 | Internal Error | Server error |

## Performance Targets

- **Latency**: P99 ≤ 5ms for cached queries
- **Throughput**: ≥ 100 RPS sustained
- **Cache Hit Rate**: ≥ 85%
- **Test Coverage**: ≥ 80%
- **Availability**: 99.9% uptime
- **Constitutional Compliance**: 100% validation

## 🔄 Workflow Documentation

### Policy Governance Workflows

- [Governance Workflow Design](api/policy-governance.md)
- [Council Review Process](api/policy-governance.md)

### Constitutional Compliance

- [Constitutional Compliance Checks RFC](api/constitutional-ai.md)
- [Compliance Validation Framework](../constitutional_compliance_validation_framework.md)

## 📚 Additional Resources

- [Configuration Guide](../configuration/README.md)
- [Deployment Guide](../deployment/ACGS_PGP_SETUP_GUIDE.md)
- [Service Status](../operations/SERVICE_STATUS.md)
- [Architecture Documentation](../architecture/)

---

**Constitutional Compliance**: All APIs validate hash `cdd01ef066bc6cf2`  
**Support**: Check service logs and health endpoints for troubleshooting
