# ACGS-1 Comprehensive API Reference

This document provides a complete API reference for all services in the ACGS-1 Constitutional Governance System.

## 🏛️ Service Overview

The ACGS-1 system consists of multiple microservices, each providing specific functionality for constitutional governance. All services follow RESTful API principles and provide OpenAPI/Swagger documentation at `/docs`.

### Service Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ACGS-1 API Gateway                      │
├─────────────────────────────────────────────────────────────┤
│  Authentication Service (8000)  │  Integrity Service (8002) │
├─────────────────────────────────────────────────────────────┤
│  Constitutional AI (8001)       │  Formal Verification (8003)│
├─────────────────────────────────────────────────────────────┤
│  Governance Synthesis (8004)    │  Policy Governance (8005)  │
├─────────────────────────────────────────────────────────────┤
│  Evolutionary Computation (8006)│  Darwin Gödel Machine (8007)│
├─────────────────────────────────────────────────────────────┤
│  ACGS-PGP v8 (8010)            │  OCR Service (8020)        │
└─────────────────────────────────────────────────────────────┘
```

## 🔐 Authentication

All API endpoints (except health checks) require JWT authentication:

```http
Authorization: Bearer <jwt_token>
```

Obtain tokens from the Authentication Service:

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

## 📋 Service Endpoints

### 1. Authentication Service (Port 8000)

**Base URL**: `http://localhost:8000`
**Interactive Docs**: `http://localhost:8000/docs`

#### Core Endpoints

- `POST /auth/login` - User authentication
- `POST /auth/refresh` - Token refresh
- `POST /auth/logout` - User logout
- `GET /auth/profile` - User profile
- `GET /health` - Service health check

#### Example Usage

```bash
# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "secure_password"}'

# Health check
curl http://localhost:8000/health
```

### 2. Constitutional AI Service (Port 8001)

**Base URL**: `http://localhost:8001`
**Interactive Docs**: `http://localhost:8001/docs`

#### Core Endpoints

- `POST /api/v1/analyze` - Constitutional analysis
- `POST /api/v1/validate` - Policy validation
- `GET /api/v1/principles` - Constitutional principles
- `POST /api/v1/compliance-check` - Compliance verification
- `GET /health` - Service health check

#### Example Usage

```bash
# Analyze constitutional compliance
curl -X POST http://localhost:8001/api/v1/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Policy proposal text",
    "principles": ["transparency", "fairness", "accountability"]
  }'
```

### 3. Integrity Service (Port 8002)

**Base URL**: `http://localhost:8002`
**Interactive Docs**: `http://localhost:8002/docs`

#### Core Endpoints

- `POST /api/v1/sign` - Digital signature creation
- `POST /api/v1/verify` - Signature verification
- `GET /api/v1/audit-log` - Audit trail retrieval
- `POST /api/v1/hash` - Document hashing
- `GET /health` - Service health check

#### Example Usage

```bash
# Sign a document
curl -X POST http://localhost:8002/api/v1/sign \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "document": "Policy document content",
    "signer_id": "user123"
  }'
```

### 4. Formal Verification Service (Port 8003)

**Base URL**: `http://localhost:8003`
**Interactive Docs**: `http://localhost:8003/docs`

#### Core Endpoints

- `POST /api/v1/verify-policy` - Policy formal verification
- `POST /api/v1/check-consistency` - Consistency checking
- `GET /api/v1/verification-rules` - Available verification rules
- `POST /api/v1/custom-verification` - Custom verification logic
- `GET /health` - Service health check

#### Example Usage

```bash
# Verify policy consistency
curl -X POST http://localhost:8003/api/v1/verify-policy \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "policy": "Policy text",
    "rules": ["consistency", "completeness", "non-contradiction"]
  }'
```

### 5. Governance Synthesis Service (Port 8004)

**Base URL**: `http://localhost:8004`
**Interactive Docs**: `http://localhost:8004/docs`

#### Core Endpoints

- `POST /api/v1/synthesize` - Policy synthesis
- `POST /api/v1/generate-alternatives` - Alternative generation
- `GET /api/v1/synthesis-templates` - Available templates
- `POST /api/v1/stakeholder-analysis` - Stakeholder impact analysis
- `GET /health` - Service health check

#### Example Usage

```bash
# Synthesize policy from inputs
curl -X POST http://localhost:8004/api/v1/synthesize \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": ["requirement1", "requirement2"],
    "stakeholders": ["citizens", "government"],
    "principles": ["transparency", "fairness"]
  }'
```

### 6. Policy Governance Service (Port 8005)

**Base URL**: `http://localhost:8005`
**Interactive Docs**: `http://localhost:8005/docs`

#### Core Endpoints

- `POST /api/v1/policies` - Create policy
- `GET /api/v1/policies` - List policies
- `GET /api/v1/policies/{id}` - Get specific policy
- `PUT /api/v1/policies/{id}` - Update policy
- `DELETE /api/v1/policies/{id}` - Delete policy
- `POST /api/v1/policies/{id}/vote` - Vote on policy
- `GET /health` - Service health check

#### Example Usage

```bash
# Create new policy
curl -X POST http://localhost:8005/api/v1/policies \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New Policy",
    "description": "Policy description",
    "category": "governance",
    "priority": "high"
  }'
```

### 7. Evolutionary Computation Service (Port 8006)

**Base URL**: `http://localhost:8006`
**Interactive Docs**: `http://localhost:8006/docs`

#### Core Endpoints

- `POST /api/v1/evolve` - Start evolution process
- `GET /api/v1/evolution/{id}` - Get evolution status
- `POST /api/v1/fitness-evaluation` - Evaluate fitness
- `GET /api/v1/population` - Get current population
- `GET /health` - Service health check

#### Example Usage

```bash
# Start policy evolution
curl -X POST http://localhost:8006/api/v1/evolve \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "initial_policies": ["policy1", "policy2"],
    "fitness_criteria": ["effectiveness", "fairness"],
    "generations": 10
  }'
```

### 8. Darwin Gödel Machine Service (Port 8007)

**Base URL**: `http://localhost:8007`
**Interactive Docs**: `http://localhost:8007/docs`

#### Core Endpoints

- `POST /api/v1/improve` - Trigger self-improvement
- `GET /api/v1/improvements` - List improvements
- `GET /api/v1/performance` - Performance metrics
- `POST /api/v1/validate-improvement` - Validate improvement
- `GET /health` - Service health check

### 9. ACGS-PGP v8 Service (Port 8010)

**Base URL**: `http://localhost:8010`
**Interactive Docs**: `http://localhost:8010/docs`

Comprehensive documentation available at: [ACGS-PGP v8 API Documentation](../services/core/acgs-pgp-v8/docs/API_DOCUMENTATION.md)

### 10. OCR Service (Port 8020)

**Base URL**: `http://localhost:8020`
**Interactive Docs**: `http://localhost:8020/docs`

#### Core Endpoints

- `POST /api/v1/ocr/extract` - Extract text from images
- `POST /api/v1/ocr/analyze` - Analyze document structure
- `GET /api/v1/ocr/formats` - Supported formats
- `GET /health` - Service health check

## 🔄 Common Response Formats

### Success Response

```json
{
  "status": "success",
  "data": { ... },
  "timestamp": "2024-06-20T10:30:00Z",
  "request_id": "req_123456"
}
```

### Error Response

```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input parameters",
    "details": { ... }
  },
  "timestamp": "2024-06-20T10:30:00Z",
  "request_id": "req_123456"
}
```

### Health Check Response

```json
{
  "status": "healthy",
  "service": "service_name",
  "version": "1.0.0",
  "uptime": 3600,
  "dependencies": {
    "database": "connected",
    "redis": "connected"
  }
}
```

## 📊 Monitoring & Metrics

All services expose Prometheus metrics at `/metrics`:

```bash
curl http://localhost:8001/metrics
```

Key metrics include:

- Request count and duration
- Error rates
- Service health status
- Resource utilization

## 🚀 Getting Started

1. **Start Services**:

   ```bash
   ./scripts/setup/start_development.sh
   ```

2. **Get Authentication Token**:

   ```bash
   TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username":"admin","password":"password"}' | \
     jq -r '.access_token')
   ```

3. **Test API Endpoints**:
   ```bash
   curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8001/api/v1/principles
   ```

## 📚 Additional Resources

- [Authentication Service API](./authentication_service_api.md)
- [Constitutional AI Service API](./constitutional_ai_service_api.md)
- [Integrity Service API](./integrity_service_api.md)
- [Formal Verification Service API](./formal_verification_service_api.md)
- [Governance Synthesis Service API](./governance_synthesis_service_api.md)
- [Policy Governance Service API](./policy_governance_service_api.md)
- [Evolutionary Computation Service API](./evolutionary_computation_service_api.md)
- [Darwin Gödel Machine Service API](./darwin_godel_machine_service_api.md)
- [OCR Service API](./ocr_service_api.md)
- [Integration Examples](../examples/)
- [Troubleshooting Guide](../troubleshooting.md)
- [Development Guide](../development/REORGANIZED_DEVELOPER_GUIDE.md)

---

**Last Updated**: 2024-06-20
**API Version**: 2.1
**Documentation Status**: ✅ Current
