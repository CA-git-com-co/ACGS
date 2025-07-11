# ACGS FastAPI Service Template

**Constitutional Hash**: `cdd01ef066bc6cf2`

## Overview

This template provides a standardized foundation for creating FastAPI services within the ACGS (Autonomous Constitutional Governance System) ecosystem. It includes all the essential patterns, configurations, and integrations needed for production-ready ACGS services.

## Features

- ✅ **Constitutional Compliance**: Built-in constitutional hash validation and compliance tracking
- ✅ **Multi-Tenant Support**: Row-Level Security (RLS) and tenant isolation
- ✅ **Standardized API Patterns**: RESTful endpoints with consistent response formats
- ✅ **Comprehensive Error Handling**: Structured error responses with constitutional compliance
- ✅ **Authentication & Authorization**: JWT-based auth with tenant context
- ✅ **Database Integration**: SQLAlchemy async models with constitutional compliance
- ✅ **Health Checks**: Comprehensive health monitoring with component status
- ✅ **Configuration Management**: Environment-based configuration with validation
- ✅ **Audit Logging**: Built-in audit trails for all operations
- ✅ **Performance Optimized**: Async operations and database connection pooling

## Quick Start

### 1. Copy the Template

```bash
# Copy the template to your new service location
cp -r services/shared/templates/fastapi_service_template services/core/your-service-name

# Navigate to your new service
cd services/core/your-service-name
```

### 2. Customize Service Configuration

Edit the service identification in `main.py`:

```python
# Update these values for your service
SERVICE_NAME = os.getenv("SERVICE_NAME", "your-service-name")
SERVICE_VERSION = os.getenv("SERVICE_VERSION", "1.0.0")
SERVICE_DESCRIPTION = os.getenv("SERVICE_DESCRIPTION", "Your service description")
```

### 3. Configure Environment Variables

Create a `.env` file:

```bash
# Service identification
SERVICE_NAME=your-service-name
SERVICE_VERSION=1.0.0
SERVICE_DESCRIPTION=Your ACGS service description
SERVICE_PORT=8005

# Environment
ENVIRONMENT=development
DEBUG=true

# Database (using ACGS shared database)
DATABASE_URL=postgresql+asyncpg://acgs_user:acgs_password@localhost:5439/acgs_db

# Redis (using ACGS shared Redis)
REDIS_URL=redis://localhost:6389/0

# Security
JWT_SECRET_KEY=your-jwt-secret-key-here

# Multi-tenant
MULTI_TENANT_ENABLED=true
MULTI_TENANT_REQUIRED=true

# Constitutional compliance
CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
CONSTITUTIONAL_COMPLIANCE_REQUIRED=true
```

### 4. Install Dependencies

Add to your service's `requirements.txt`:

```txt
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.5.0
sqlalchemy>=2.0.0
asyncpg>=0.29.0
redis>=5.0.0
python-jose[cryptography]>=3.3.0
python-multipart>=0.0.6
```

Or if using the consolidated `pyproject.toml`:

```bash
pip install -e .[api,database,cache,auth]
```

### 5. Run the Service

```bash
# Development mode with auto-reload
uvicorn main:app --host 0.0.0.0 --port 8005 --reload

# Or using the built-in server
python main.py
```

## File Structure

```
your-service-name/
├── main.py                 # FastAPI application entry point
├── config.py              # Configuration management
├── schemas.py             # Pydantic request/response models
├── models.py              # SQLAlchemy database models
├── api/
│   └── v1/
│       └── routes.py      # API route definitions
├── tests/                 # Service tests
├── requirements.txt       # Python dependencies
├── .env                   # Environment configuration
└── README.md             # Service-specific documentation
```

## Core Components

### 1. Main Application (`main.py`)

The main application file provides:

- **Standardized FastAPI app creation** with constitutional compliance
- **Comprehensive middleware stack** including tenant isolation
- **Health check endpoints** with component monitoring
- **Error handling** with structured responses
- **Constitutional compliance validation** throughout the request lifecycle

Key features:
- Automatic constitutional hash validation
- Multi-tenant middleware integration
- Request logging and monitoring
- Component health checking framework

### 2. Configuration Management (`config.py`)

The configuration system provides:

- **Environment-based configuration** using Pydantic BaseSettings
- **Structured configuration** organized by component (database, security, etc.)
- **Configuration validation** with custom validators
- **Environment-specific configurations** (development, production, test)
- **Production readiness checks** to validate deployment configurations

Example usage:
```python
from config import get_settings

settings = get_settings()
database_url = settings.get_database_url()
```

### 3. API Schemas (`schemas.py`)

Standardized Pydantic models including:

- **Constitutional compliance base models** with automatic hash validation
- **Generic response wrappers** for consistent API responses
- **Pagination and filtering models** for list endpoints
- **Error response models** with detailed error information
- **Multi-tenant aware models** with tenant context

Example:
```python
from schemas import SuccessResponse, ExampleCreateRequest

@router.post("/items", response_model=SuccessResponse[ExampleResponse])
async def create_item(request: ExampleCreateRequest):
    # Implementation
    pass
```

### 4. Database Models (`models.py`)

SQLAlchemy models with:

- **Constitutional compliance integration** with automatic hash validation
- **Multi-tenant support** with tenant isolation
- **Audit trail functionality** with creation/update tracking
- **Standardized mixins** for common functionality
- **Database event listeners** for constitutional compliance

Example:
```python
from models import BaseACGSModel

class YourModel(BaseACGSModel):
    __tablename__ = "your_table"
    
    name = Column(String(255), nullable=False)
    # Tenant isolation, constitutional compliance, and audit trails are automatic
```

### 5. API Routes (`api/v1/routes.py`)

Standardized route patterns including:

- **RESTful CRUD operations** with proper error handling
- **Multi-tenant aware endpoints** with automatic tenant filtering
- **Constitutional compliance validation** for all operations
- **Pagination and filtering** for list endpoints
- **Admin-only routes** with proper authorization

## Constitutional Compliance Integration

Every component of the template includes constitutional compliance:

### Automatic Hash Validation
```python
# All responses include constitutional hash
{
    "status": "success",
    "data": {...},
    "constitutional_hash": "cdd01ef066bc6cf2"
}
```

### Database Models
```python
class YourModel(BaseACGSModel):
    # Automatically includes constitutional_hash field
    # Validated on insert/update operations
    pass
```

### Request Middleware
```python
# All responses include constitutional compliance headers
response.headers["X-Constitutional-Hash"] = CONSTITUTIONAL_HASH
```

## Multi-Tenant Integration

The template provides seamless multi-tenant support:

### Automatic Tenant Context
```python
@router.get("/items")
async def get_items(
    tenant_context: SimpleTenantContext = Depends(get_tenant_context)
):
    # tenant_context.tenant_id is automatically available
    # Database queries are automatically filtered by tenant
    pass
```

### Tenant-Aware Database Models
```python
class YourModel(BaseACGSModel):
    # Automatically includes tenant_id field
    # RLS policies ensure tenant isolation
    pass
```

### Tenant Administration
```python
@router.get("/admin/stats")
async def admin_stats(
    admin_context: SimpleTenantContext = Depends(get_admin_context)
):
    # Only admin users can access this endpoint
    pass
```

## Health Checks and Monitoring

### Component Health Registration
```python
# Register component health checks
health_checker.register_component("database", check_database_health)
health_checker.register_component("redis", check_redis_health)
health_checker.register_component("external_api", check_external_api_health)
```

### Health Check Response
```json
{
    "status": "healthy",
    "service": "your-service-name",
    "version": "1.0.0",
    "constitutional_hash": "cdd01ef066bc6cf2",
    "constitutional_compliance": "verified",
    "uptime_seconds": 3600.0,
    "components": {
        "database": "healthy",
        "redis": "healthy",
        "external_api": "healthy"
    }
}
```

## Error Handling

Standardized error responses with constitutional compliance:

```json
{
    "error": "Validation failed",
    "type": "validation_error",
    "constitutional_hash": "cdd01ef066bc6cf2",
    "timestamp": "2024-01-01T12:00:00Z",
    "service": "your-service-name",
    "details": {...}
}
```

## Testing

### Unit Tests
```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["constitutional_hash"] == "cdd01ef066bc6cf2"
```

### Integration Tests
```python
@pytest.mark.asyncio
async def test_create_resource():
    # Test with tenant context
    response = await client.post(
        "/api/v1/resources",
        json={"name": "Test Resource"},
        headers={"Authorization": "Bearer valid-jwt-token"}
    )
    assert response.status_code == 201
```

## Deployment

### Docker Integration

The template works seamlessly with the consolidated Docker Compose configurations:

```yaml
# Add to docker-compose.dev.yml
your_service:
  build:
    context: ../..
    dockerfile: infrastructure/docker/Dockerfile.acgs
    target: development
  container_name: acgs_your_service_dev
  environment:
    - SERVICE_NAME=your-service-name
    - SERVICE_PORT=8005
    - CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
  working_dir: /app/services/core/your-service-name
  command: ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8005", "--reload"]
  ports:
    - "8005:8005"
```

### Production Configuration

```python
from config import validate_production_config, get_production_config

config = get_production_config()
issues = validate_production_config(config)

if issues:
    for issue in issues:
        print(f"⚠️ Production issue: {issue}")
    exit(1)
```

## Best Practices

### 1. Service Naming
- Use kebab-case for service names: `user-management`, `content-analysis`
- Include service type in name when appropriate: `auth-service`, `ml-inference`

### 2. API Design
- Follow RESTful conventions
- Use proper HTTP status codes
- Include constitutional compliance in all responses
- Implement proper pagination for list endpoints

### 3. Error Handling
- Use structured error responses
- Include meaningful error messages
- Log errors with proper context
- Maintain constitutional compliance in error responses

### 4. Security
- Always validate JWT tokens
- Implement proper tenant isolation
- Use environment variables for secrets
- Validate all input data

### 5. Database
- Use the shared RLS implementation for tenant isolation
- Include audit trails for important operations
- Validate constitutional compliance at the database level
- Use proper indexes for performance

## Migration from Existing Services

### 1. Gradual Migration Strategy
1. **Copy existing routes** to the new template structure
2. **Update imports** to use standardized components
3. **Add constitutional compliance** to existing models
4. **Implement multi-tenant support** using provided mixins
5. **Update error handling** to use standardized responses

### 2. Database Migration
```python
# Add constitutional compliance to existing models
class ExistingModel(BaseACGSModel):
    __tablename__ = "existing_table"
    
    # Your existing fields
    name = Column(String(255), nullable=False)
    
    # Constitutional compliance and tenant isolation are automatically added
```

### 3. API Migration
```python
# Convert existing endpoints to use standardized patterns
@router.get("/items", response_model=SuccessResponse[List[ItemResponse]])
async def get_items(
    pagination: PaginationParams = Depends(),
    tenant_context: SimpleTenantContext = Depends(get_tenant_context)
):
    # Implementation with automatic tenant filtering
    pass
```

## Contributing

When extending the template:

1. **Maintain constitutional compliance** in all components
2. **Follow established patterns** for consistency
3. **Update documentation** for new features
4. **Include comprehensive tests** for new functionality
5. **Validate production readiness** for configuration changes

## Support

For questions about the template:

1. **Review this documentation** and the inline code comments
2. **Check existing ACGS services** for implementation examples
3. **Consult the ACGS architectural documentation** for design patterns
4. **Submit issues** for template improvements or bug reports

---

This template provides a solid foundation for building production-ready ACGS services with constitutional compliance, multi-tenant support, and standardized patterns. Follow the established conventions to ensure consistency across the ACGS ecosystem.