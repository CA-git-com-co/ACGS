# ACGS Developer Onboarding Guide
<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

**Version**: 2.0  
**Last Updated**: January 7, 2025  
**Based on**: FastAPI Service Template (API Standardization Complete)

## 🎯 Welcome to ACGS Development

This comprehensive guide will get you up and running with ACGS development using our standardized FastAPI service template. By following this guide, you'll be able to create production-ready ACGS services with constitutional compliance, multi-tenant support, and enterprise-grade patterns.

## 📋 Prerequisites

### Required Knowledge
- **Python 3.11+** with async/await patterns
- **FastAPI** framework fundamentals
- **PostgreSQL** and SQLAlchemy async
- **Redis** for caching and sessions
- **Docker** and containerization
- **Git** version control

### Development Environment
- **Operating System**: Linux/macOS (Windows with WSL2)
- **Python**: 3.11 or higher
- **Docker**: Latest stable version
- **IDE**: VS Code with Python extension (recommended)

## 🚀 Quick Start (5 Minutes)

### 1. Clone and Setup

```bash
# Clone the ACGS repository
git clone https://github.com/CA-git-com-co/ACGS.git
cd ACGS-2

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev,test]"
```

### 2. Start Infrastructure

```bash
# Start PostgreSQL and Redis
docker-compose -f docker-compose.postgresql.yml up -d
docker-compose -f docker-compose.redis.yml up -d

# Run database migrations
cd services/shared
alembic upgrade head
```

### 3. Create Your First Service

```bash
# Copy the FastAPI template
cp -r services/shared/templates/fastapi_service_template services/core/my-service

# Navigate to your service
cd services/core/my-service

# Customize the service
# Edit main.py to update SERVICE_NAME, SERVICE_VERSION, SERVICE_DESCRIPTION
```

### 4. Test Your Service

```bash
# Start your service
python main.py

# Test the health endpoint
curl http://localhost:8001/health

# Expected response:
{
  "status": "healthy",
  "service": "my-service",
  "constitutional_hash": "cdd01ef066bc6cf2",
  "constitutional_compliance": "verified"
}
```

## 🏗️ Creating a New ACGS Service

### Step 1: Service Planning

**Before coding, define:**
- **Service Purpose**: What problem does this service solve?
- **Port Assignment**: Choose an available port (8001-8020 range)
- **Constitutional Requirements**: What compliance validations are needed?
- **Multi-Tenant Needs**: How will tenant isolation work?
- **Integration Points**: Which other ACGS services will you integrate with?

### Step 2: Copy and Customize Template

```bash
# Copy the template to your service location
cp -r services/shared/templates/fastapi_service_template services/core/your-service-name

# Navigate to your new service
cd services/core/your-service-name
```

**Customize `main.py`:**
```python
# Update these values for your service
SERVICE_NAME = os.getenv("SERVICE_NAME", "your-service-name")
SERVICE_VERSION = os.getenv("SERVICE_VERSION", "1.0.0")
SERVICE_DESCRIPTION = os.getenv("SERVICE_DESCRIPTION", "Your service description")
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8001"))  # Choose your port
```

### Step 3: Define Your Data Models

**Edit `models.py`:**
```python
from services.shared.templates.fastapi_service_template.models import BaseACGSModel
from sqlalchemy import Column, String, Integer, DateTime

class YourModel(BaseACGSModel):
    __tablename__ = "your_table"
    
    # Your specific fields
    name = Column(String(255), nullable=False)
    description = Column(String(1000))
    priority = Column(Integer, default=1)
    
    # BaseACGSModel automatically includes:
    # - id (UUID primary key)
    # - tenant_id (for multi-tenant isolation)
    # - constitutional_hash (for compliance)
    # - created_at, updated_at (for audit trails)
    # - status, is_active (for status tracking)
```

### Step 4: Create API Schemas

**Edit `schemas.py`:**
```python
from services.shared.templates.fastapi_service_template.schemas import ConstitutionalBaseModel

class YourModelCreate(ConstitutionalBaseModel):
    name: str
    description: str | None = None
    priority: int = 1

class YourModelResponse(ConstitutionalBaseModel):
    id: str
    name: str
    description: str | None
    priority: int
    tenant_id: str
    created_at: datetime
    updated_at: datetime
```

### Step 5: Implement API Routes

**Edit `api/v1/routes.py`:**
```python
from fastapi import APIRouter, Depends, HTTPException
from services.shared.templates.fastapi_service_template.schemas import SuccessResponse
from services.shared.multi_tenant.context import get_tenant_context, SimpleTenantContext
from services.shared.database.connection import get_tenant_db

router = APIRouter()

@router.post("/your-resources", response_model=SuccessResponse[YourModelResponse])
async def create_resource(
    request: YourModelCreate,
    tenant_context: SimpleTenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_tenant_db)
):
    # Constitutional compliance validation
    if len(request.name) < 3:
        raise HTTPException(
            status_code=400,
            detail="Resource name must meet constitutional requirements (min 3 characters)"
        )
    
    # Create resource with tenant isolation
    resource = YourModel(
        name=request.name,
        description=request.description,
        priority=request.priority,
        tenant_id=tenant_context.tenant_id
    )
    
    db.add(resource)
    await db.commit()
    await db.refresh(resource)
    
    return SuccessResponse(
        data=YourModelResponse.from_orm(resource),
        message="Resource created successfully",
        constitutional_hash="cdd01ef066bc6cf2"
    )
```

### Step 6: Configure Environment

**Create `.env` file:**
```bash
# Service identification
SERVICE_NAME=your-service-name
SERVICE_VERSION=1.0.0
SERVICE_DESCRIPTION=Your service description
SERVICE_PORT=8001

# Database configuration
DATABASE_URL=postgresql+asyncpg://acgs:acgs@localhost:5439/acgs
REDIS_URL=redis://localhost:6389

# Constitutional compliance
CONSTITUTIONAL_HASH=cdd01ef066bc6cf2

# Multi-tenant configuration
ENABLE_MULTI_TENANT=true
TENANT_HEADER=X-Tenant-ID

# Security configuration
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
```

## 🔒 Constitutional Compliance Implementation

### Automatic Compliance Features

The FastAPI template includes built-in constitutional compliance:

**1. Response Headers:**
```python
# Automatically added to all responses
X-Constitutional-Hash: cdd01ef066bc6cf2
X-Service-Name: your-service-name
X-Request-ID: unique-request-id
```

**2. Constitutional Validation Endpoint:**
```python
@router.post("/constitutional/validate")
async def validate_constitutional_compliance(request: ValidationRequest):
    # Built-in constitutional validation logic
    return {
        "valid": True,
        "constitutional_hash": "cdd01ef066bc6cf2",
        "validation_details": {...}
    }
```

**3. Audit Logging:**
```python
# Automatic audit logging for all operations
await audit_logger.log_operation(
    operation="resource_create",
    resource_id=resource.id,
    tenant_id=tenant_context.tenant_id,
    constitutional_hash="cdd01ef066bc6cf2",
    success=True
)
```

### Custom Compliance Validation

**Add custom validation logic:**
```python
def validate_custom_constitutional_requirements(data: dict) -> bool:
    """Custom constitutional compliance validation."""
    
    # Example: Ensure data meets transparency requirements
    if not data.get("description"):
        return False
    
    # Example: Validate fairness requirements
    if data.get("priority", 0) < 1:
        return False
    
    # Example: Check accountability requirements
    if not data.get("created_by"):
        return False
    
    return True
```

## 🏢 Multi-Tenant Implementation

### Automatic Tenant Isolation

The template provides automatic tenant isolation:

**1. Tenant Context Injection:**
```python
@router.get("/resources")
async def get_resources(
    tenant_context: SimpleTenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_tenant_db)
):
    # tenant_context.tenant_id is automatically available
    # Database queries are automatically filtered by tenant
    resources = await db.execute(
        select(YourModel).where(YourModel.tenant_id == tenant_context.tenant_id)
    )
    return resources.scalars().all()
```

**2. Database Row-Level Security:**
```sql
-- Automatically applied RLS policies
CREATE POLICY tenant_isolation ON your_table
    FOR ALL TO authenticated_user
    USING (tenant_id = current_setting('app.current_tenant_id'));
```

**3. Cross-Tenant Administration:**
```python
@router.get("/admin/all-resources")
async def get_all_resources(
    tenant_context: SimpleTenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_tenant_db)
):
    # Admin users can access cross-tenant data
    if not tenant_context.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Query without tenant filtering for admin users
    resources = await db.execute(select(YourModel))
    return resources.scalars().all()
```

## 🧪 Testing Your Service

### Unit Testing

**Create `test_your_service.py`:**
```python
import pytest
from fastapi.testclient import TestClient
from services.shared.templates.fastapi_service_template.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["constitutional_hash"] == "cdd01ef066bc6cf2"

def test_create_resource():
    response = client.post(
        "/api/v1/your-resources",
        json={"name": "Test Resource", "description": "Test Description"},
        headers={"X-Tenant-ID": "test-tenant"}
    )
    assert response.status_code == 200
    assert response.json()["constitutional_hash"] == "cdd01ef066bc6cf2"
```

### Integration Testing

**Test with other ACGS services:**
```python
async def test_service_integration():
    # Test integration with Auth Service
    auth_response = await auth_client.validate_token(test_token)
    assert auth_response.status_code == 200
    
    # Test integration with your service
    service_response = await your_service_client.create_resource(
        data=test_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert service_response.status_code == 200
```

## 🚀 Deployment and Operations

### Local Development Deployment

```bash
# Start your service locally
python main.py

# Service will be available at:
# http://localhost:8001 (or your configured port)

# Health check
curl http://localhost:8001/health

# API documentation
open http://localhost:8001/docs
```

### Docker Deployment

```bash
# Build Docker image
docker build -t acgs/your-service-name .

# Run with Docker Compose
docker-compose up -d your-service-name
```

### Production Deployment

```bash
# Deploy to Kubernetes
kubectl apply -f k8s/your-service-deployment.yaml

# Monitor deployment
kubectl get pods -l app=your-service-name
```

## 📊 Performance Targets

Your service must meet these ACGS performance requirements:

- **P99 Latency**: <5ms
- **Throughput**: >100 RPS
- **Cache Hit Rate**: >85%
- **Availability**: 99.99%
- **Constitutional Compliance**: 100%
- **Memory Usage**: <1GB per instance
- **CPU Usage**: <50% average load

## 📚 Next Steps

### Key Architectural Concepts

Before diving deep into service development, it's important to understand the core architectural principles that govern the ACGS ecosystem. These concepts are crucial for building compliant, secure, and performant services.

- **Constitutional Compliance**: The entire system operates under a set of constitutional principles, enforced by the constitutional hash (`cdd01ef066bc6cf2`). All services must adhere to these principles. For more details, see the [ACGS Unified Architecture Guide](../architecture/ACGS_UNIFIED_ARCHITECTURE_GUIDE.md#constitutional-compliance-first).
- **Multi-Tenancy**: The system is designed to support multiple tenants, with strict data isolation enforced at the database and application levels. For more information on how multi-tenancy is implemented, see the [ACGS Unified Architecture Guide](../architecture/ACGS_UNIFIED_ARCHITECTURE_GUIDE.md#multi-tenant-architecture).
- **API Standardization**: All services follow a standardized API design, based on the FastAPI service template. This ensures consistency and predictability across the entire ecosystem. For more details, see the [ACGS Unified Architecture Guide](../architecture/ACGS_UNIFIED_ARCHITECTURE_GUIDE.md#api-standardization).



### Advanced Topics
- **Performance Optimization**: Caching strategies and database optimization
- **Security Hardening**: Advanced security patterns and vulnerability testing
- **Monitoring Integration**: Custom metrics and alerting
- **Deployment Automation**: CI/CD pipelines and infrastructure as code

### Resources
- **API Documentation**: [`docs/api/`](../api/)
- **Architecture Guides**: [`docs/architecture/`](../architecture/)
- **Deployment Guides**: [`docs/deployment/`](../deployment/)
- **Testing Strategies**: [`docs/testing/`](../testing/)
- **FastAPI Template**: [`services/shared/templates/fastapi_service_template/`](../../services/shared/templates/fastapi_service_template/)

---

**Constitutional Hash**: `cdd01ef066bc6cf2`
**Support**: ACGS Development Team
**Documentation**: [ACGS Documentation Standards](../standards/ACGS_DOCUMENTATION_STANDARDS.md)
