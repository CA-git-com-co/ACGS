# ACGS API Documentation Index

<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

**Generated**: 2025-07-05 19:55:49  
**Constitutional Hash**: `cdd01ef066bc6cf2`  
**Total APIs**: 10

## Quick Navigation

### Core Services
- [Authentication API](authentication.md) - Core authentication functionality
- [Constitutional Ai API](constitutional-ai.md) - Core constitutional ai functionality
- [Integrity API](integrity.md) - Core integrity functionality
- [Formal Verification API](formal-verification.md) - Core formal verification functionality

### Governance Services
- [Governance Synthesis API](governance_synthesis.md) - governance synthesis capabilities
- [Policy Governance API](policy-governance.md) - policy governance capabilities
- [Evolutionary Computation API](evolutionary-computation.md) - evolutionary computation capabilities


## API Standards

All ACGS APIs follow these standards:

### Authentication
- **Method**: JWT Bearer tokens
- **Endpoint**: `/auth/login` for token acquisition
- **Headers**: `Authorization: Bearer <token>`

### Response Format
All API responses include:
```json
{
  "data": "response content",
  "constitutional_hash": "cdd01ef066bc6cf2",
  "timestamp": "ISO 8601 timestamp"
}
```

### Error Handling
Standardized error responses:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": {}
  },
  "constitutional_hash": "cdd01ef066bc6cf2",
  "timestamp": "ISO 8601 timestamp"
}
```

### Performance Targets
- **Latency**: P99 ≤ 5ms for cached queries
- **Throughput**: ≥ 100 RPS sustained
- **Cache Hit Rate**: ≥ 85%
- **Availability**: 99.9% uptime

### Rate Limiting
- **Standard endpoints**: 1000 requests/hour per API key
- **Heavy operations**: 100 requests/hour per API key
- **Authentication**: 50 requests/hour per IP

## Service Ports

| Service | Port | Base URL |
|---------|------|----------|
| Authentication | 8016 | `http://localhost:8016/api/v1` |
| Constitutional AI | 8001 | `http://localhost:8001/api/v1` |
| Integrity | 8002 | `http://localhost:8002/api/v1` |
| Formal Verification | 8003 | `http://localhost:8003/api/v1` |
| Governance Synthesis | 8004 | `http://localhost:8004/api/v1` |
| Policy Governance | 8005 | `http://localhost:8005/api/v1` |
| Evolutionary Computation | 8006 | `http://localhost:8006/api/v1` |

## Constitutional Compliance

All APIs implement constitutional compliance:
- ✅ Constitutional hash in all responses
- ✅ Compliance validation in all operations
- ✅ Audit logging with constitutional tracking
- ✅ Security controls with constitutional verification

---

**Auto-Generated**: This index is automatically updated during deployment  
**Constitutional Hash**: `cdd01ef066bc6cf2` ✅
