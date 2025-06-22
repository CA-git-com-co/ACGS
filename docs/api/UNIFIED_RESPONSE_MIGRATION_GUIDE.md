# ACGS-1 Unified Response Format Migration Guide

**Version:** 1.0  
**Date:** 2025-06-22  
**Status:** Implementation Guide  

## Overview

This guide provides step-by-step instructions for migrating all ACGS-1 microservices to use the new unified response format. The migration ensures consistent API responses across all 8 services while maintaining backward compatibility.

## 🎯 Unified Response Format

### New Standard Format

```json
{
  "success": boolean,
  "data": any,
  "message": string,
  "metadata": {
    "timestamp": "ISO8601",
    "requestId": "UUID",
    "version": "string",
    "service": "string",
    "executionTimeMs": number
  },
  "pagination": {  // Optional for paginated responses
    "page": number,
    "limit": number,
    "total": number,
    "hasNext": boolean,
    "hasPrevious": boolean
  }
}
```

### Benefits

- ✅ **Consistent API responses** across all services
- ✅ **Enhanced debugging** with request tracking
- ✅ **Better monitoring** with execution time metrics
- ✅ **Improved pagination** with standardized metadata
- ✅ **Backward compatibility** support during transition

## 📋 Migration Steps by Service

### 1. Authentication Service (Port 8000)

**Current Format:**
```json
{
  "access_token": "jwt_token",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**New Format:**
```json
{
  "success": true,
  "data": {
    "access_token": "jwt_token",
    "token_type": "bearer",
    "expires_in": 3600
  },
  "message": "Authentication successful",
  "metadata": {
    "timestamp": "2025-06-22T10:30:00Z",
    "requestId": "uuid-here",
    "version": "2.1.0",
    "service": "authentication-service"
  }
}
```

**Migration Code:**
```python
# Before
from fastapi import APIRouter
from fastapi.responses import JSONResponse

@router.post("/login")
async def login(credentials: LoginRequest):
    token = await authenticate_user(credentials)
    return JSONResponse({
        "access_token": token,
        "token_type": "bearer",
        "expires_in": 3600
    })

# After
from fastapi import APIRouter, Depends
from services.shared.response.unified_response import (
    ResponseBuilder, 
    get_response_builder,
    UnifiedJSONResponse
)

@router.post("/login")
async def login(
    credentials: LoginRequest,
    response_builder: ResponseBuilder = Depends(get_response_builder)
):
    token = await authenticate_user(credentials)
    
    response = response_builder.success(
        data={
            "access_token": token,
            "token_type": "bearer",
            "expires_in": 3600
        },
        message="Authentication successful"
    )
    
    return UnifiedJSONResponse(content=response)
```

### 2. Constitutional AI Service (Port 8001)

**Migration Example:**
```python
# Before
@router.get("/principles")
async def get_principles():
    principles = await get_constitutional_principles()
    return {"principles": principles, "count": len(principles)}

# After
@router.get("/principles")
async def get_principles(
    response_builder: ResponseBuilder = Depends(get_response_builder)
):
    principles = await get_constitutional_principles()
    
    response = response_builder.success(
        data={
            "principles": principles,
            "count": len(principles)
        },
        message="Constitutional principles retrieved successfully"
    )
    
    return UnifiedJSONResponse(content=response)
```

### 3. Governance Synthesis Service (Port 8004) - Paginated Response

**Migration Example:**
```python
# Before
@router.get("/policies")
async def get_policies(page: int = 1, limit: int = 10):
    policies, total = await get_policies_paginated(page, limit)
    return {
        "policies": policies,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total
        }
    }

# After
@router.get("/policies")
async def get_policies(
    page: int = 1,
    limit: int = 10,
    response_builder: ResponseBuilder = Depends(get_response_builder)
):
    policies, total = await get_policies_paginated(page, limit)
    
    response = response_builder.paginated_success(
        data=policies,
        page=page,
        limit=limit,
        total=total,
        message="Policies retrieved successfully"
    )
    
    return UnifiedJSONResponse(content=response)
```

## 🔧 Implementation Steps

### Step 1: Install Shared Response Module

```bash
# Add to requirements.txt
orjson>=3.9.0
pydantic>=2.0.0

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Update Service Main Application

```python
# services/[service]/app/main.py
from fastapi import FastAPI
from services.shared.response.unified_response import UnifiedResponseMiddleware

app = FastAPI(title="Service Name")

# Add unified response middleware
app.add_middleware(UnifiedResponseMiddleware, service_name="service-name")

# Import routers
from .api.v1 import router as api_router
app.include_router(api_router, prefix="/api/v1")
```

### Step 3: Update Router Endpoints

```python
# services/[service]/app/api/v1/endpoints.py
from fastapi import APIRouter, Depends, HTTPException
from services.shared.response.unified_response import (
    ResponseBuilder,
    get_response_builder,
    UnifiedJSONResponse
)

router = APIRouter()

@router.get("/example")
async def example_endpoint(
    response_builder: ResponseBuilder = Depends(get_response_builder)
):
    try:
        # Your business logic here
        data = await get_example_data()
        
        response = response_builder.success(
            data=data,
            message="Data retrieved successfully"
        )
        
        return UnifiedJSONResponse(content=response)
        
    except ValueError as e:
        response = response_builder.error(
            message="Invalid input provided",
            data={"validation_errors": str(e)},
            error_code="VALIDATION_ERROR"
        )
        
        return UnifiedJSONResponse(content=response, status_code=400)
        
    except Exception as e:
        response = response_builder.error(
            message="Internal server error",
            error_code="INTERNAL_ERROR"
        )
        
        return UnifiedJSONResponse(content=response, status_code=500)
```

### Step 4: Update Error Handling

```python
# services/[service]/app/core/exceptions.py
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from services.shared.response.unified_response import ResponseBuilder

async def unified_exception_handler(request: Request, exc: HTTPException):
    """Global exception handler using unified response format."""
    
    # Extract service name from request
    service_name = request.headers.get("X-Service-Name", "unknown-service")
    builder = ResponseBuilder(service_name)
    builder.set_request_context(request)
    
    response = builder.error(
        message=exc.detail,
        error_code=f"HTTP_{exc.status_code}"
    )
    
    return JSONResponse(
        content=response.dict(),
        status_code=exc.status_code
    )

# Register in main.py
from fastapi.exceptions import HTTPException
app.add_exception_handler(HTTPException, unified_exception_handler)
```

## 🧪 Testing Migration

### Unit Tests

```python
# tests/unit/api/test_unified_responses.py
import pytest
from fastapi.testclient import TestClient
from services.shared.response.unified_response import validate_response_format

def test_endpoint_unified_response_format(client: TestClient):
    """Test that endpoint returns unified response format."""
    response = client.get("/api/v1/example")
    
    assert response.status_code == 200
    
    response_data = response.json()
    
    # Validate unified format
    assert validate_response_format(response_data) is True
    
    # Check required fields
    assert "success" in response_data
    assert "data" in response_data
    assert "message" in response_data
    assert "metadata" in response_data
    
    # Check metadata structure
    metadata = response_data["metadata"]
    assert "timestamp" in metadata
    assert "requestId" in metadata
    assert "version" in metadata
    assert "service" in metadata
```

### Integration Tests

```python
# tests/integration/test_service_responses.py
import pytest
import httpx

@pytest.mark.asyncio
async def test_all_endpoints_unified_format():
    """Test that all service endpoints return unified format."""
    
    endpoints = [
        "http://localhost:8000/health",  # Auth Service
        "http://localhost:8001/health",  # AC Service
        "http://localhost:8002/health",  # Integrity Service
        # ... add all service endpoints
    ]
    
    async with httpx.AsyncClient() as client:
        for endpoint in endpoints:
            response = await client.get(endpoint)
            
            if response.status_code == 200:
                response_data = response.json()
                assert validate_response_format(response_data) is True
```

## 🔄 Backward Compatibility

### Legacy Response Support

```python
# services/shared/response/legacy_support.py
from typing import Dict, Any
from fastapi import Request
from services.shared.response.unified_response import migrate_legacy_response

async def legacy_response_middleware(request: Request, call_next):
    """Middleware to support legacy response format during transition."""
    
    # Check if client requests legacy format
    accept_legacy = request.headers.get("X-Accept-Legacy-Format", "false").lower() == "true"
    
    response = await call_next(request)
    
    if accept_legacy and hasattr(response, 'body'):
        # Convert unified response back to legacy format if requested
        # Implementation depends on specific legacy format requirements
        pass
    
    return response
```

### Gradual Migration Strategy

1. **Phase 1 (Week 1):** Implement unified response in new endpoints
2. **Phase 2 (Week 2):** Migrate existing endpoints with backward compatibility
3. **Phase 3 (Week 3):** Update client applications to use new format
4. **Phase 4 (Week 4):** Remove legacy format support

## 📊 Validation and Monitoring

### Response Format Validation

```python
# scripts/validate_response_formats.py
import asyncio
import httpx
from services.shared.response.unified_response import validate_response_format

async def validate_all_service_responses():
    """Validate that all services return unified response format."""
    
    services = [
        {"name": "auth", "url": "http://localhost:8000"},
        {"name": "ac", "url": "http://localhost:8001"},
        {"name": "integrity", "url": "http://localhost:8002"},
        {"name": "fv", "url": "http://localhost:8003"},
        {"name": "gs", "url": "http://localhost:8004"},
        {"name": "pgc", "url": "http://localhost:8005"},
        {"name": "ec", "url": "http://localhost:8006"},
        {"name": "dgm", "url": "http://localhost:8007"},
    ]
    
    results = {}
    
    async with httpx.AsyncClient() as client:
        for service in services:
            try:
                response = await client.get(f"{service['url']}/health")
                
                if response.status_code == 200:
                    is_valid = validate_response_format(response.json())
                    results[service['name']] = {
                        "status": "success",
                        "unified_format": is_valid
                    }
                else:
                    results[service['name']] = {
                        "status": "error",
                        "error": f"HTTP {response.status_code}"
                    }
                    
            except Exception as e:
                results[service['name']] = {
                    "status": "error",
                    "error": str(e)
                }
    
    return results

if __name__ == "__main__":
    results = asyncio.run(validate_all_service_responses())
    
    print("🔍 Response Format Validation Results:")
    for service, result in results.items():
        status = "✅" if result.get("unified_format") else "❌"
        print(f"{status} {service}: {result}")
```

### Monitoring Metrics

```python
# Add to Prometheus metrics
from prometheus_client import Counter, Histogram

# Response format metrics
response_format_counter = Counter(
    'acgs_response_format_total',
    'Total responses by format type',
    ['service', 'format_type']
)

response_time_histogram = Histogram(
    'acgs_response_time_seconds',
    'Response time by service',
    ['service', 'endpoint']
)
```

## 🚀 Rollout Plan

### Week 1: Foundation
- ✅ Implement shared response utilities
- ✅ Create comprehensive unit tests
- ✅ Update 2 services (Auth + AC) as proof of concept

### Week 2: Core Services
- 🔄 Migrate Integrity, FV, and GS services
- 🔄 Implement backward compatibility middleware
- 🔄 Update integration tests

### Week 3: Remaining Services
- 🔄 Migrate PGC, EC, and DGM services
- 🔄 Update all 86 identified endpoints
- 🔄 Comprehensive validation testing

### Week 4: Validation & Documentation
- 🔄 Complete end-to-end testing
- 🔄 Update API documentation
- 🔄 Performance validation
- 🔄 Remove legacy format support

## 📈 Success Metrics

- **API Consistency Score:** Target >95% (from current 76%)
- **Response Format Compliance:** 100% across all 86 endpoints
- **Test Coverage:** >90% for response formatting code
- **Performance Impact:** <5ms additional response time
- **Backward Compatibility:** Zero breaking changes during migration

---

**Next Steps:**
1. ✅ Unified Response Format Implementation: **IN_PROGRESS**
2. Error Handling Standardization
3. OpenAPI Documentation Generation
4. API Versioning Strategy Implementation
