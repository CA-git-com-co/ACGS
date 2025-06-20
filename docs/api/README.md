# ACGS-1 API Documentation

This directory contains comprehensive API documentation for all ACGS-1 services across the blockchain-integrated governance system.

## Core Service APIs

### Constitutional AI Service (`constitutional-ai`)
- **Base URL:** `http://localhost:8001/api/constitutional-ai/`
- **Documentation:** [ac_service_api.md](ac_service_api.md)
- **Interactive Docs:** `http://localhost:8001/docs`
- **Features:** Constitutional principles, meta-rules, Constitutional Council, conflict resolution

### Governance Synthesis Service (`governance-synthesis`)
- **Base URL:** `http://localhost:8004/api/governance-synthesis/`
- **Documentation:** [gs_service_api.md](gs_service_api.md)
- **Interactive Docs:** `http://localhost:8004/docs`
- **Features:** LLM-powered policy synthesis, multi-model validation, QEC error correction

### Policy Governance Service (`policy-governance`)
- **Base URL:** `http://localhost:8005/api/policy-governance/`
- **Interactive Docs:** `http://localhost:8005/docs`
- **Features:** Real-time policy enforcement, OPA integration, constitutional amendment integration

### Formal Verification Service (`formal-verification`)
- **Base URL:** `http://localhost:8003/api/formal-verification/`
- **Interactive Docs:** `http://localhost:8003/docs`
- **Features:** Z3 SMT solver integration, safety property checking, formal policy validation

## Platform Service APIs

### Authentication Service (`authentication`)
- **Base URL:** `http://localhost:8000/api/authentication/`
- **Interactive Docs:** `http://localhost:8000/docs`
- **Features:** User authentication, RBAC, JWT token management

### Integrity Service (`integrity`)
- **Base URL:** `http://localhost:8002/api/integrity/`
- **Interactive Docs:** `http://localhost:8002/docs`
- **Features:** Cryptographic integrity, policy storage, versioning, audit logs, PGP assurance

### Evolutionary Computation Service (`evolutionary-computation`)
- **Base URL:** `http://localhost:8006/api/evolutionary-computation/`
- **Interactive Docs:** `http://localhost:8006/docs`
- **Features:** WINA optimization, evolutionary governance strategies, performance monitoring

## Research Service APIs

### Federated Evaluation Service (`federated-evaluation`)
- **Base URL:** `http://localhost:8008/api/federated-evaluation/`
- **Interactive Docs:** `http://localhost:8008/docs`
- **Features:** Distributed evaluation, federated learning, cross-domain testing

### Research Platform Service (`research-platform`)
- **Base URL:** `http://localhost:8009/api/research-platform/`
- **Interactive Docs:** `http://localhost:8009/docs`
- **Features:** Research infrastructure, experiment tracking, data collection

## Blockchain Integration APIs

### Quantumagi Bridge (`quantumagi-bridge`)
- **Base URL:** `http://localhost:8010/api/quantumagi-bridge/`
- **Interactive Docs:** `http://localhost:8010/docs`
- **Features:** Blockchain-backend integration, event monitoring, cross-chain coordination

### AlphaEvolve Engine (`alphaevolve-engine`)
- **Base URL:** `http://localhost:8011/api/alphaevolve-engine/`
- **Interactive Docs:** `http://localhost:8011/docs`
- **Features:** AlphaEvolve integration, constitutional AI framework

### Data Flywheel Integration (`data-flywheel`)
- **Base URL:** `http://localhost:8010/api/data-flywheel/`
- **Interactive Docs:** `http://localhost:8010/docs`
- **Features:** NVIDIA AI Blueprints Data Flywheel, autonomous model optimization, constitutional compliance validation

## Common API Patterns

### Authentication
All API endpoints (except public health checks) require authentication via JWT tokens:

```bash
curl -H "Authorization: Bearer <your_jwt_token>" \
     http://localhost:8000/api/ac/principles
```

### Response Format
All APIs follow a consistent response format:

```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Error Handling
Error responses include detailed information:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid principle data",
    "details": { ... }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Pagination
List endpoints support pagination:

```bash
GET /api/ac/principles?page=1&limit=20&sort=created_at&order=desc
```

## Service Integration Patterns

### Cross-Service Communication
Services communicate using internal service tokens and standardized schemas:

1. **Constitutional AI → Governance Synthesis:** Principle retrieval for constitutional prompting
2. **Governance Synthesis → Formal Verification:** Policy verification requests
3. **Formal Verification → Integrity:** Verification result storage
4. **Policy Governance → All Services:** Runtime governance enforcement
5. **Quantumagi Bridge → Blockchain:** On-chain governance coordination

### Constitutional Workflow
The complete constitutional governance workflow:

1. **Principle Management** (Constitutional AI): Define constitutional principles
2. **Constitutional Prompting** (Governance Synthesis): Generate policies with constitutional guidance
3. **Formal Verification** (Formal Verification): Verify policies against principles
4. **Integrity Assurance** (Integrity): Store with cryptographic signatures
5. **Runtime Enforcement** (Policy Governance): Enforce policies in real-time
6. **Blockchain Integration** (Quantumagi Bridge): Sync with on-chain governance

## Development and Testing

### Local Development
Start all services with Docker Compose:

```bash
docker-compose -f infrastructure/docker/infrastructure/docker/docker-compose.yml up --build -d
```

### API Testing
Use the provided test scripts:

```bash
# Load test data
python scripts/load_test_data.py

# Run API tests
python -m pytest tests/integration/test_api_endpoints.py
```

### Interactive Documentation
Each service provides Swagger UI documentation at `/docs` endpoint:

**Core Services:**
- Constitutional AI: http://localhost:8001/docs
- Governance Synthesis: http://localhost:8004/docs
- Policy Governance: http://localhost:8005/docs
- Formal Verification: http://localhost:8003/docs
- Darwin Gödel Machine: http://localhost:8007/docs

**Platform Services:**
- Authentication: http://localhost:8000/docs
- Integrity: http://localhost:8002/docs
- Evolutionary Computation: http://localhost:8006/docs

**Research Services:**
- Federated Evaluation: http://localhost:8008/docs
- Research Platform: http://localhost:8009/docs

**Integration Services:**
- Data Flywheel: http://localhost:8010/docs
- Quantumagi Bridge: http://localhost:8011/docs
- AlphaEvolve Engine: http://localhost:8012/docs

## Security Considerations

### Authentication & Authorization
- JWT tokens with configurable expiration
- Role-based access control (Admin, Policy Manager, Auditor)
- Service-to-service authentication with internal tokens

### Data Protection
- HTTPS enforcement in production
- Input validation and sanitization
- Rate limiting and request throttling
- Audit logging for all operations

### Constitutional Compliance
- All operations logged for constitutional audit
- Principle-based access control
- Cryptographic integrity verification
- Democratic governance through Constitutional Council

For detailed endpoint documentation, refer to the individual service API documentation files.
