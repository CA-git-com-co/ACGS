# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Environment Setup

```bash
# Initial setup
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Start infrastructure dependencies
docker-compose -f docker-compose.postgresql.yml up -d  # PostgreSQL on port 5439
docker-compose -f docker-compose.redis.yml up -d       # Redis on port 6389

# Run database migrations
cd services/shared
alembic upgrade head

# Start all services
docker-compose -f infrastructure/docker/docker-compose.yml up -d
```

## Testing Commands

```bash
# Run all tests
make test

# Specific test types
make test-unit                    # Unit tests only
make test-integration            # Integration tests only
make test-performance            # Performance tests
make test-security               # Security tests
make test-coverage               # Generate coverage report

# Multi-agent coordination tests
python tests/multi_agent_test_runner.py --test-types unit integration
pytest tests/unit/multi_agent_coordination/ -v
pytest tests/integration/multi_agent_coordination/ -v

# Load testing
cd tests/load_testing
python run_load_test.py

# Security testing
cd tests/security
python run_security_tests.py

# Documentation validation (comprehensive)
python3 tools/validation/unified_documentation_validation_framework.py
```

## Service Architecture

This is a research prototype implementing constitutional AI governance through an 8-service microservices architecture:

### Production-Grade Services (3)
- **Constitutional AI Service** (port 8001): Core constitutional compliance with hash validation (`cdd01ef066bc6cf2`)
- **Integrity Service** (port 8002): Database audit trail with cryptographic hash chaining
- **API Gateway Service**: Production routing, rate limiting, and security middleware

### Prototype Services (5) 
- **Formal Verification Service** (port 8003): Z3 SMT solver integration (basic implementation)
- **Governance Synthesis Service** (port 8004): OPA policy synthesis (contains mock implementations)
- **Policy Governance Service** (port 8005): Multi-framework compliance (placeholder functions)
- **Evolutionary Computation Service** (port 8006): Constitutional evolution tracking (TODO items)
- **Authentication Service** (port 8016): JWT multi-tenant auth (test mocks, not production-ready)

### Infrastructure Components
- **PostgreSQL**: Port 5439 with Row-Level Security for multi-tenant isolation
- **Redis**: Port 6389 for caching and session management
- **Constitutional Hash**: `cdd01ef066bc6cf2` - enforced across all components for compliance validation

## Constitutional Compliance System

The entire system operates under constitutional compliance with hash `cdd01ef066bc6cf2`:

- All services must include this hash in responses and documentation
- Constitutional validation is performed on all operations
- Audit logging tracks constitutional compliance
- 100% compliance rate is maintained across documentation and code

## Key Development Patterns

### Service Structure
Each service follows this pattern:
```
services/{core|platform_services}/service_name/
├── app/
│   ├── main.py           # FastAPI application
│   ├── schemas.py        # Pydantic models
│   ├── models.py         # Database models
│   └── api/              # API endpoints
├── config/
├── tests/
└── requirements.txt
```

### Multi-Tenant Architecture
- All services support multi-tenancy via `services/shared/middleware/tenant_middleware.py`
- Database isolation using PostgreSQL Row-Level Security
- JWT-based authentication with tenant context
- Shared utilities in `services/shared/`

### Import Patterns for Services
Services use conditional imports for shared components:
```python
try:
    from services.shared.middleware.tenant_middleware import (
        TenantContextMiddleware,
        get_tenant_context,
    )
    MULTI_TENANT_AVAILABLE = True
except ImportError:
    MULTI_TENANT_AVAILABLE = False
```

### Error Handling
Use standardized error handling from `services/shared/middleware/error_handling.py`:
- `ConstitutionalComplianceError`
- `SecurityValidationError`
- `setup_error_handlers(app)`

## Performance Targets

The system maintains these performance standards:
- **Throughput**: ≥100 RPS (Current: 306.9 RPS)
- **Latency**: P99 ≤5ms for cached queries (Current: 0.97ms)
- **Cache Hit Rate**: ≥85% (Current: 25% - optimization in progress)
- **Constitutional Compliance**: ≥95% accuracy (Current: 98.0%)
- **Availability**: 99.9% uptime

## Documentation and Validation Tools

The repository includes sophisticated documentation validation tools:

```bash
# Enhanced validation framework (consolidates all validators)
python3 tools/validation/unified_documentation_validation_framework.py

# Individual validators
python3 tools/validation/enhanced_validation.py
python3 tools/validation/advanced_cross_reference_analyzer.py
python3 tools/validation/api_code_sync_validator.py

# Auto-generate missing documentation
python3 tools/automation/enhanced_auto_doc_generator.py
```

## Database Migrations

Database operations use Alembic with multi-tenant support:
```bash
cd services/shared
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## Service Health Checks

All services provide standardized endpoints:
- `/health` - Service health status
- `/metrics` - Prometheus metrics
- `/api/v1/` - API endpoints

```bash
# Check service health
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
```

## Kubernetes Deployment

Production deployment uses Kubernetes manifests in `infrastructure/kubernetes/`:
- Complete auto-scaling configuration
- Multi-tenant security policies  
- Monitoring and alerting setup
- Constitutional compliance validation

## Research Context

This is a research prototype demonstrating constitutional AI governance concepts. Some services contain mock implementations, placeholder functions, or TODO items as they represent theoretical frameworks being validated through practical implementation.