# ACGS-2 API Documentation
<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

## Overview

Comprehensive API documentation for ACGS-2 (Advanced Constitutional Governance System). This documentation provides detailed information about all APIs, endpoints, authentication, and constitutional compliance requirements.

## Constitutional Requirements

All ACGS-2 APIs must maintain constitutional hash `cdd01ef066bc6cf2` validation and adhere to:
- **Constitutional Header**: `constitutional-hash: cdd01ef066bc6cf2` required in all requests
- **Performance Targets**: P99 <5ms response time, >100 RPS throughput
- **Authentication**: JWT-based authentication with constitutional validation
- **Audit Logging**: All API interactions logged with constitutional compliance tracking

## API Architecture

### Service-Oriented Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway (Port 8080)                 │
├─────────────────────────────────────────────────────────────┤
│  ✓ Authentication & Authorization                           │
│  ✓ Rate Limiting & Throttling                              │
│  ✓ Request/Response Validation                             │
│  ✓ Constitutional Compliance Checking                       │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                     Core Services                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │Constitutional│  │ GroqCloud   │  │    Auth     │        │
│  │Core (8001)  │  │Policy(8023) │  │Service(8013)│        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Infrastructure                           │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Monitoring  │  │    Audit    │  │    GDPR     │        │
│  │Service(8014)│  │Service(8015)│  │Service(8016)│        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## API Services

### Core Services

#### 1. [Constitutional Core API](./constitutional-core.md)
**Port**: 8001  
**Base URL**: `http://constitutional-core:8001`

Primary API for constitutional governance operations including validation, consensus, and compliance management.

**Key Endpoints**:
- `POST /api/constitutional/validate` - Validate constitutional compliance
- `POST /api/consensus/propose` - Submit consensus proposals
- `GET /api/constitutional/status` - Get constitutional system status
- `POST /api/constitutional/audit` - Perform constitutional audits

#### 2. [GroqCloud Policy API](./groqcloud-policy.md)
**Port**: 8023  
**Base URL**: `http://groqcloud-policy:8023`

API for AI policy evaluation and decision-making using GroqCloud and OpenAI integration.

**Key Endpoints**:
- `POST /api/policy/evaluate` - Evaluate policy proposals
- `POST /api/policy/generate` - Generate policy recommendations
- `GET /api/policy/models` - Get available AI models
- `POST /api/policy/chat` - Interactive policy consultation

#### 3. [Authentication Service API](./auth-service.md)
**Port**: 8013  
**Base URL**: `http://auth-service:8013`

Comprehensive authentication and authorization API with JWT tokens and RBAC.

**Key Endpoints**:
- `POST /api/auth/login` - User authentication
- `POST /api/auth/refresh` - Token refresh
- `GET /api/auth/profile` - Get user profile
- `POST /api/auth/logout` - User logout

### Infrastructure Services

#### 4. [Monitoring Service API](./monitoring-service.md)
**Port**: 8014  
**Base URL**: `http://monitoring-service:8014`

System monitoring, metrics collection, and alerting API.

**Key Endpoints**:
- `GET /api/metrics/system` - System performance metrics
- `GET /api/metrics/constitutional` - Constitutional compliance metrics
- `POST /api/alerts` - Create system alerts
- `GET /api/health/services` - Service health status

#### 5. [Audit Service API](./audit-service.md)
**Port**: 8015  
**Base URL**: `http://audit-service:8015`

Comprehensive audit logging and compliance reporting API.

**Key Endpoints**:
- `POST /api/audit/log` - Log audit events
- `GET /api/audit/reports` - Generate audit reports
- `GET /api/audit/compliance` - Compliance status
- `POST /api/audit/search` - Search audit logs

#### 6. [GDPR Compliance API](./gdpr-compliance.md)
**Port**: 8016  
**Base URL**: `http://gdpr-compliance:8016`

GDPR compliance management and data subject rights API.

**Key Endpoints**:
- `POST /api/gdpr/request` - Data subject requests
- `GET /api/gdpr/status` - Compliance status
- `POST /api/gdpr/export` - Data export requests
- `POST /api/gdpr/delete` - Data deletion requests

### Management Services

#### 7. [API Gateway](./api-gateway.md)
**Port**: 8080  
**Base URL**: `http://api-gateway:8080`

Central API gateway for routing, authentication, and request management.

**Key Endpoints**:
- `GET /api/gateway/health` - Gateway health status
- `GET /api/gateway/routes` - Available routes
- `POST /api/gateway/configure` - Configure gateway settings
- `GET /api/gateway/metrics` - Gateway performance metrics

## Authentication and Authorization

### JWT Authentication
All API requests (except health checks) require JWT authentication with constitutional validation.

```http
Authorization: Bearer <jwt-token>
constitutional-hash: cdd01ef066bc6cf2
```

### Authentication Flow
```javascript
// 1. Login to get JWT token
const loginResponse = await fetch('/api/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'constitutional-hash': 'cdd01ef066bc6cf2'
  },
  body: JSON.stringify({
    username: 'your-username',
    password: 'your-password'
  })
});

const { token } = await loginResponse.json();

// 2. Use token for authenticated requests
const apiResponse = await fetch('/api/constitutional/validate', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'constitutional-hash': 'cdd01ef066bc6cf2',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    data: 'your-data'
  })
});
```

### Role-Based Access Control (RBAC)
- **Constitutional Admin**: Full system access
- **Constitutional Auditor**: Read-only constitutional data
- **Policy Maker**: Policy creation and modification
- **System Admin**: Infrastructure management
- **Compliance Officer**: Audit and compliance operations
- **API User**: Basic API access
- **Guest**: Limited read access

## Common Request/Response Patterns

### Standard Request Headers
```http
Content-Type: application/json
Authorization: Bearer <jwt-token>
constitutional-hash: cdd01ef066bc6cf2
X-Request-ID: <unique-request-id>
```

### Standard Response Format
```json
{
  "success": true,
  "data": {
    // Response data
  },
  "metadata": {
    "timestamp": "2025-07-18T10:30:00Z",
    "request_id": "req-123456",
    "constitutional_hash": "cdd01ef066bc6cf2",
    "performance": {
      "response_time_ms": 2.5,
      "constitutional_compliance": true
    }
  }
}
```

### Error Response Format
```json
{
  "success": false,
  "error": {
    "code": "CONSTITUTIONAL_VIOLATION",
    "message": "Constitutional hash validation failed",
    "details": {
      "expected_hash": "cdd01ef066bc6cf2",
      "received_hash": "invalid-hash"
    }
  },
  "metadata": {
    "timestamp": "2025-07-18T10:30:00Z",
    "request_id": "req-123456",
    "constitutional_hash": "cdd01ef066bc6cf2"
  }
}
```

## Rate Limiting and Throttling

### Rate Limits by Service
- **Constitutional Core**: 1000 requests/minute per user
- **GroqCloud Policy**: 100 requests/minute per user (AI model limits)
- **Authentication**: 60 requests/minute per IP (login attempts)
- **Monitoring**: 500 requests/minute per user
- **Audit**: 200 requests/minute per user

### Rate Limit Headers
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642694400
X-RateLimit-Policy: constitutional-core
```

## Performance Requirements

### Response Time Targets
- **Constitutional Operations**: P99 <5ms
- **Policy Evaluation**: P99 <500ms (due to AI processing)
- **Authentication**: P99 <10ms
- **Monitoring**: P99 <50ms
- **Audit**: P99 <100ms

### Throughput Targets
- **System-wide**: >100 RPS minimum
- **Constitutional Core**: >1000 RPS
- **Authentication**: >500 RPS
- **Monitoring**: >200 RPS

## API Testing and Validation

### Health Check Endpoints
All services provide health check endpoints for monitoring and validation.

```bash
# System health check
curl -H "constitutional-hash: cdd01ef066bc6cf2" \
  http://api-gateway:8080/api/health

# Service-specific health checks
curl -H "constitutional-hash: cdd01ef066bc6cf2" \
  http://constitutional-core:8001/health
```

### Constitutional Compliance Testing
```bash
# Test constitutional compliance
curl -X POST \
  -H "Content-Type: application/json" \
  -H "constitutional-hash: cdd01ef066bc6cf2" \
  -d '{"test": "constitutional-compliance"}' \
  http://constitutional-core:8001/api/constitutional/validate
```

### Performance Testing
```bash
# Load testing with constitutional compliance
ab -n 1000 -c 10 \
  -H "constitutional-hash: cdd01ef066bc6cf2" \
  http://constitutional-core:8001/api/constitutional/validate
```

## API Versioning

### Version Strategy
- **Current Version**: v1.0.0
- **Versioning Scheme**: Semantic versioning (MAJOR.MINOR.PATCH)
- **Backward Compatibility**: Maintained for one major version
- **Version Header**: `API-Version: v1.0.0`

### Version Deprecation Policy
- **Advance Notice**: 6 months before deprecation
- **Migration Period**: 6 months overlap between versions
- **Support Period**: 12 months total for each version

## Error Handling

### Standard Error Codes
- **400**: Bad Request - Invalid input or missing constitutional hash
- **401**: Unauthorized - Invalid or missing authentication
- **403**: Forbidden - Insufficient permissions
- **404**: Not Found - Resource not found
- **409**: Conflict - Constitutional compliance violation
- **422**: Unprocessable Entity - Validation failed
- **429**: Too Many Requests - Rate limit exceeded
- **500**: Internal Server Error - System error
- **503**: Service Unavailable - Service temporarily unavailable

### Constitutional Error Codes
- **CONSTITUTIONAL_VIOLATION**: Constitutional hash validation failed
- **COMPLIANCE_CHECK_FAILED**: Compliance requirements not met
- **CONSENSUS_REQUIRED**: Consensus required for operation
- **AUDIT_REQUIRED**: Audit logging required
- **PERFORMANCE_VIOLATION**: Performance requirements not met

## SDK and Client Libraries

### Official SDKs
- **Python SDK**: `acgs-python-sdk`
- **JavaScript SDK**: `acgs-js-sdk`
- **Go SDK**: `acgs-go-sdk`
- **Java SDK**: `acgs-java-sdk`

### SDK Installation
```bash
# Python
pip install acgs-python-sdk

# JavaScript
npm install acgs-js-sdk

# Go
go get github.com/acgs/acgs-go-sdk

# Java
mvn install acgs-java-sdk
```

### SDK Usage Example (Python)
```python
from acgs_sdk import ACGSClient

# Initialize client
client = ACGSClient(
    base_url="http://api-gateway:8080",
    constitutional_hash="cdd01ef066bc6cf2"
)

# Authenticate
client.authenticate(username="user", password="pass")

# Make constitutional API call
result = client.constitutional.validate({
    "data": "constitutional-data"
})

print(f"Validation result: {result}")
```

## Monitoring and Observability

### API Metrics
- **Request Count**: Total API requests
- **Response Time**: P50, P95, P99 latencies
- **Error Rate**: Percentage of failed requests
- **Throughput**: Requests per second
- **Constitutional Compliance**: Compliance rate

### Distributed Tracing
All API calls are traced using OpenTelemetry with constitutional compliance tags.

### Logging Standards
```json
{
  "timestamp": "2025-07-18T10:30:00Z",
  "service": "constitutional-core",
  "level": "INFO",
  "message": "API request processed",
  "request_id": "req-123456",
  "constitutional_hash": "cdd01ef066bc6cf2",
  "user_id": "user123",
  "endpoint": "/api/constitutional/validate",
  "response_time_ms": 2.5,
  "constitutional_compliance": true
}
```

## Security Considerations

### API Security
- **HTTPS Only**: All API communications encrypted
- **JWT Tokens**: Secure token-based authentication
- **Rate Limiting**: Protection against abuse
- **Input Validation**: Comprehensive input sanitization
- **CORS**: Proper cross-origin resource sharing

### Constitutional Security
- **Hash Validation**: Every request validated
- **Compliance Checking**: Constitutional requirements enforced
- **Audit Logging**: All interactions logged
- **Performance Monitoring**: Real-time performance tracking

## Getting Started

### Quick Start Guide
1. **Setup Authentication**: Get JWT token from auth service
2. **Include Constitutional Hash**: Add required header to all requests
3. **Make API Calls**: Use documented endpoints
4. **Monitor Performance**: Check response times and compliance
5. **Handle Errors**: Implement proper error handling

### Development Environment
```bash
# Clone repository
git clone https://github.com/acgs/acgs-2.git

# Setup development environment
cd acgs-2
docker-compose up -d

# Test API connectivity
curl -H "constitutional-hash: cdd01ef066bc6cf2" \
  http://localhost:8080/api/health
```

### Production Environment
```bash
# Deploy to Kubernetes
kubectl apply -f deployment/kubernetes/

# Verify deployment
kubectl get pods -n acgs-system

# Test production API
curl -H "constitutional-hash: cdd01ef066bc6cf2" \
  https://api.acgs.local/api/health
```

## Support and Resources

### Documentation
- **API Reference**: Detailed endpoint documentation
- **SDK Documentation**: Client library guides
- **Examples**: Code samples and tutorials
- **Best Practices**: Development guidelines

### Community
- **GitHub**: https://github.com/acgs/acgs-2
- **Discord**: https://discord.gg/acgs
- **Forum**: https://forum.acgs.local
- **Stack Overflow**: Tag `acgs-2`

### Support
- **Technical Support**: support@acgs.local
- **Bug Reports**: https://github.com/acgs/acgs-2/issues
- **Feature Requests**: https://github.com/acgs/acgs-2/discussions
- **Security Issues**: security@acgs.local

---

**Navigation**: [Root](../../CLAUDE.md) | [Documentation](../CLAUDE.md) | [Services](../../services/README.md)

**Constitutional Compliance**: All APIs maintain constitutional hash `cdd01ef066bc6cf2` validation and performance targets (P99 <5ms, >100 RPS).

**Last Updated**: 2025-07-18 - API documentation framework established