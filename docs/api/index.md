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
| **Governance Synthesis** | 8004 | [Governance Synthesis API](governance_synthesis.md) | ✅ Available |
| **Policy Governance** | 8005 | [Policy Governance API](policy-governance.md) | ✅ Available |
| **Evolutionary Computation** | 8006 | [Evolutionary Computation API](evolutionary-computation.md) | ✅ Available |

### Integration APIs

| API | Documentation | Purpose |
|-----|---------------|---------|
| **Cross-Service Integration** | [Integration Guide](../integration/ACGS_SERVICE_INTEGRATION_GUIDE.md) | Service-to-service communication |
| **Audit Logging** | [Audit Logging API](#) | Compliance and audit trails (Documentation pending) |
| **JWT Token Management** | [JWT Reference](jwt.md) | Token handling and validation |
| **Role-Based Access Control** | [RBAC Design](rbac.md) | Permission and role management |

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
  "data": {},
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

## 📚 Additional Resources

- [Configuration Guide](../configuration/README.md)
- [Deployment Guide](../deployment/ACGS_PGP_SETUP_GUIDE.md)
- [Service Status](../operations/SERVICE_STATUS.md)
- [Architecture Documentation](../architecture/)

## Related Information

For a broader understanding of the ACGS platform and its components, refer to:

- [ACGS Service Architecture Overview](../../docs/ACGS_SERVICE_OVERVIEW.md)
- [ACGS Documentation Implementation and Maintenance Plan - Completion Report](../../docs/ACGS_DOCUMENTATION_IMPLEMENTATION_COMPLETION_REPORT.md)
- [ACGE Strategic Implementation Plan - 24 Month Roadmap](../../docs/ACGE_STRATEGIC_IMPLEMENTATION_PLAN_24_MONTH.md)
- [ACGE Testing and Validation Framework](../../docs/ACGE_TESTING_VALIDATION_FRAMEWORK.md)
- [ACGE Cost Analysis and ROI Projections](../../docs/ACGE_COST_ANALYSIS_ROI_PROJECTIONS.md)
- [ACGS Comprehensive Task Completion - Final Report](../architecture/ACGS_COMPREHENSIVE_TASK_COMPLETION_FINAL_REPORT.md)
- [ACGS-Claudia Integration Architecture Plan](../architecture/ACGS_CLAUDIA_INTEGRATION_ARCHITECTURE.md)
- [ACGS Implementation Guide](../deployment/ACGS_IMPLEMENTATION_GUIDE.md)
- [ACGS-PGP Operational Deployment Guide](../deployment/ACGS_PGP_OPERATIONAL_DEPLOYMENT_GUIDE.md)
- [ACGS-PGP Troubleshooting Guide](../deployment/ACGS_PGP_TROUBLESHOOTING_GUIDE.md)
- [ACGS-PGP Setup Guide](../deployment/ACGS_PGP_SETUP_GUIDE.md)
- [ACGS-2 Technical Specifications - 2025 Edition](../TECHNICAL_SPECIFICATIONS_2025.md)

---

**Constitutional Compliance**: All APIs validate hash `cdd01ef066bc6cf2`
**Support**: Check service logs and health endpoints for troubleshooting