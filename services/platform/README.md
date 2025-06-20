# ACGS-1 Platform Services

This directory contains the platform services that provide foundational capabilities for the ACGS-1 governance system.

## Service Overview

### Authentication Service (`authentication/`)
**Purpose**: User authentication, authorization, and access control
- User registration, login, and session management
- JWT token issuance and validation
- Role-Based Access Control (RBAC) implementation
- Multi-factor authentication support

**Key Features**:
- OAuth2/OpenID Connect integration
- Session management
- Permission-based access control
- Security audit logging

**Port**: 8000
**API Base**: `/api/authentication/`

### Integrity Service (`integrity/`)
**Purpose**: Cryptographic integrity and data assurance
- Policy storage and versioning
- Audit log management
- Cryptographic integrity (PGP Assurance)
- Data validation and verification

**Key Features**:
- PGP signature verification
- Audit trail management
- Data integrity checking
- Version control for policies

**Port**: 8002
**API Base**: `/api/integrity/`

### Workflow Service (`workflow/`)
**Purpose**: Workflow orchestration and process automation
- Business process management
- Task scheduling and execution
- Workflow state management
- Process monitoring and analytics

**Key Features**:
- Workflow definition and execution
- Task queue management
- Process automation
- Integration with core services

**Port**: 8007
**API Base**: `/api/workflow/`

## Service Architecture

### Communication Patterns
```
Authentication ──→ All Services (Auth validation)
       │
       ▼
   Integrity ──→ Core Services (Data validation)
       │
       ▼
   Workflow ──→ Process Orchestration
```

### Data Flow
1. **Authentication** validates all incoming requests
2. **Integrity** ensures data consistency and audit trails
3. **Workflow** orchestrates complex governance processes

### Integration Points
- **Core Services**: Provides authentication and data integrity
- **Blockchain Integration**: Ensures integrity of on-chain operations
- **Applications**: Provides user authentication and workflow management
- **External APIs**: Secure integration with external services

## Development

### Running All Platform Services
```bash
# Start all platform services
docker-compose -f infrastructure/docker/docker-compose.platform.yml up -d

# Or start individually with UV (recommended)
cd services/platform/authentication && uv sync && uv run uvicorn app.main:app --reload --port 8000
cd services/platform/integrity && uv sync && uv run uvicorn app.main:app --reload --port 8002
cd services/platform/workflow && uv sync && uv run uvicorn app.main:app --reload --port 9007

# Alternative: Traditional Python
cd services/platform/authentication && python -m uvicorn app.main:app --reload --port 8000
cd services/platform/integrity && python -m uvicorn app.main:app --reload --port 8002
cd services/platform/workflow && python -m uvicorn app.main:app --reload --port 9007
```

### Testing Platform Services
```bash
# Run platform service tests
python -m pytest tests/unit/platform/
python -m pytest tests/integration/platform/

# Test authentication flow
python scripts/validation/test_authentication_workflow.py

# Test integrity verification
python scripts/validation/test_integrity_verification.py
```

### Service Dependencies
- **Database**: PostgreSQL for user data and audit logs
- **Cache**: Redis for session storage and caching
- **Message Queue**: NATS for workflow coordination
- **External Services**: OAuth providers, HSM for key management

## Configuration

### Environment Variables
Platform services use these environment variables:

**Authentication Service**:
- `JWT_SECRET_KEY`: Secret key for JWT token signing
- `JWT_EXPIRATION_HOURS`: Token expiration time
- `OAUTH_CLIENT_ID`: OAuth client identifier
- `OAUTH_CLIENT_SECRET`: OAuth client secret

**Integrity Service**:
- `PGP_KEY_PATH`: Path to PGP private key
- `AUDIT_LOG_RETENTION_DAYS`: Audit log retention period
- `INTEGRITY_CHECK_INTERVAL`: Data integrity check frequency

**Workflow Service**:
- `WORKFLOW_ENGINE`: Workflow engine type (celery, temporal)
- `TASK_QUEUE_URL`: Task queue connection string
- `WORKFLOW_TIMEOUT`: Default workflow timeout

### Service Registry
Platform services register with the shared service registry:
```python
# services/shared/config/service_registry.py
PLATFORM_SERVICES = {
    "authentication": "http://localhost:8005",
    "integrity": "http://localhost:8006",
    "workflow": "http://localhost:8007"
}
```

## Security Features

### Authentication Security
- **Multi-factor Authentication**: TOTP, SMS, email verification
- **Password Policies**: Complexity requirements, rotation policies
- **Session Security**: Secure session management, automatic timeout
- **Audit Logging**: Complete authentication audit trail

### Integrity Security
- **Cryptographic Signatures**: PGP/GPG signature verification
- **Hash Verification**: SHA-256 integrity checking
- **Tamper Detection**: Automatic detection of data modifications
- **Secure Storage**: Encrypted storage of sensitive data

### Workflow Security
- **Process Isolation**: Secure execution environments
- **Access Control**: Role-based workflow permissions
- **Audit Trail**: Complete workflow execution logging
- **Secure Communication**: Encrypted inter-service communication

## Monitoring & Health Checks

### Health Endpoints
Each platform service provides:
- `GET /health` - Basic health check
- `GET /health/detailed` - Detailed health information
- `GET /metrics` - Prometheus metrics
- `GET /status` - Service status and dependencies

### Service Monitoring
- **Authentication Metrics**: Login success/failure rates, token usage
- **Integrity Metrics**: Verification success rates, audit log volume
- **Workflow Metrics**: Process execution times, success rates
- **Performance Metrics**: Response times, throughput, error rates

## API Examples

### Authentication Service
```bash
# User login
curl -X POST http://localhost:8005/api/authentication/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user@example.com", "password": "password"}'

# Token validation
curl -X GET http://localhost:8005/api/authentication/validate \
  -H "Authorization: Bearer <jwt_token>"
```

### Integrity Service
```bash
# Verify data integrity
curl -X POST http://localhost:8006/api/integrity/verify \
  -H "Content-Type: application/json" \
  -d '{"data": "policy_content", "signature": "pgp_signature"}'

# Get audit log
curl -X GET http://localhost:8006/api/integrity/audit-log?entity_id=123
```

### Workflow Service
```bash
# Start workflow
curl -X POST http://localhost:8007/api/workflow/start \
  -H "Content-Type: application/json" \
  -d '{"workflow_type": "policy_approval", "data": {...}}'

# Get workflow status
curl -X GET http://localhost:8007/api/workflow/status/workflow_id
```

## Documentation

- **[API Documentation](../../docs/api/README.md)**: Complete API reference
- **[Security Guide](../../docs/security/README.md)**: Security implementation details
- **[Development Guide](../../docs/development/developer_guide.md)**: Development workflows
- **[Deployment Guide](../../docs/deployment/deployment.md)**: Deployment instructions

---

**Platform Services**: Foundational capabilities for secure governance 🔐
