# ACGS Testing Strategy Foundation
<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

**Version**: 2.0  
**Last Updated**: January 7, 2025  
**Based on**: FastAPI Template Testing Patterns (API Standardization Complete)

## 🎯 Overview

This document establishes the testing strategy foundation for ACGS services, leveraging the standardized testing patterns from the completed FastAPI service template. This foundation prepares for the final **Testing Strategy Implementation** task (Task 10/10) and ensures all ACGS services maintain constitutional compliance, performance targets, and production readiness.

## 🧪 Testing Framework Architecture

### Core Testing Principles

1. **Constitutional Compliance Testing**: Every test validates constitutional hash `cdd01ef066bc6cf2`
2. **Multi-Tenant Testing**: All tests include tenant isolation validation
3. **Performance Testing**: Automated validation of P99 <5ms, >100 RPS, >85% cache hit rate
4. **Template-Based Consistency**: All services use standardized testing patterns

### Testing Pyramid Structure

```
                    ┌─────────────────────┐
                    │   E2E Tests (5%)    │
                    │ Full system testing │
                    └─────────────────────┘
                ┌─────────────────────────────┐
                │   Integration Tests (15%)   │
                │ Service-to-service testing  │
                └─────────────────────────────┘
            ┌─────────────────────────────────────┐
            │        Unit Tests (80%)             │
            │ Individual component testing        │
            └─────────────────────────────────────┘
```

## 🔧 FastAPI Template Testing Patterns

### 1. Unit Testing Framework

**Base Test Class (from FastAPI template):**
```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from services.shared.templates.fastapi_service_template.main import app
from services.shared.testing.constitutional_test_case import ConstitutionalTestCase

class TestServiceBase(ConstitutionalTestCase):
    """Base test class with constitutional compliance validation."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    async def db_session(self):
        # Async database session for testing
        async with get_test_db_session() as session:
            yield session
    
    @pytest.fixture
    def tenant_context(self):
        return SimpleTenantContext(
            tenant_id="test-tenant-id",
            user_id="test-user-id",
            is_admin=False
        )
    
    def assert_constitutional_compliance(self, response):
        """Validate constitutional compliance in response."""
        assert response.headers.get("X-Constitutional-Hash") == "cdd01ef066bc6cf2"
        if response.status_code == 200:
            data = response.json()
            assert data.get("constitutional_hash") == "cdd01ef066bc6cf2"
```

### 2. API Testing Patterns

**Health Check Testing:**
```python
def test_health_check(self, client):
    """Test service health endpoint with constitutional compliance."""
    response = client.get("/health")
    
    assert response.status_code == 200
    self.assert_constitutional_compliance(response)
    
    data = response.json()
    assert data["status"] == "healthy"
    assert data["constitutional_compliance"] == "verified"
    assert "uptime_seconds" in data
    assert "components" in data
```

**CRUD Operations Testing:**
```python
def test_create_resource(self, client, tenant_context):
    """Test resource creation with constitutional compliance."""
    resource_data = {
        "name": "Test Resource",
        "description": "Test Description",
        "priority": 1
    }
    
    response = client.post(
        "/api/v1/resources",
        json=resource_data,
        headers={"X-Tenant-ID": tenant_context.tenant_id}
    )
    
    assert response.status_code == 200
    self.assert_constitutional_compliance(response)
    
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["name"] == resource_data["name"]
    assert data["data"]["tenant_id"] == tenant_context.tenant_id
```

### 3. Multi-Tenant Testing

**Tenant Isolation Testing:**
```python
async def test_tenant_isolation(self, client, db_session):
    """Test that tenant isolation is properly enforced."""
    tenant1_id = "tenant-1"
    tenant2_id = "tenant-2"
    
    # Create resource for tenant 1
    resource1 = await create_test_resource(db_session, tenant1_id, "Resource 1")
    
    # Create resource for tenant 2
    resource2 = await create_test_resource(db_session, tenant2_id, "Resource 2")
    
    # Tenant 1 should only see their resource
    response = client.get(
        "/api/v1/resources",
        headers={"X-Tenant-ID": tenant1_id}
    )
    
    assert response.status_code == 200
    self.assert_constitutional_compliance(response)
    
    data = response.json()
    resources = data["data"]
    assert len(resources) == 1
    assert resources[0]["id"] == str(resource1.id)
    assert all(r["tenant_id"] == tenant1_id for r in resources)
```

### 4. Constitutional Compliance Testing

**Constitutional Validation Testing:**
```python
def test_constitutional_validation_endpoint(self, client):
    """Test constitutional compliance validation endpoint."""
    validation_request = {
        "content": "Test content for validation",
        "context": {"operation": "create_resource"},
        "validation_level": "standard"
    }
    
    response = client.post(
        "/api/v1/constitutional/validate",
        json=validation_request
    )
    
    assert response.status_code == 200
    self.assert_constitutional_compliance(response)
    
    data = response.json()
    assert data["valid"] is True
    assert data["constitutional_hash"] == "cdd01ef066bc6cf2"
    assert "validation_details" in data
```

**Constitutional Compliance Violation Testing:**
```python
def test_constitutional_compliance_violation(self, client):
    """Test handling of constitutional compliance violations."""
    invalid_request = {
        "name": "X",  # Too short, violates constitutional requirements
        "description": ""
    }
    
    response = client.post(
        "/api/v1/resources",
        json=invalid_request,
        headers={"X-Tenant-ID": "test-tenant"}
    )
    
    assert response.status_code == 400
    self.assert_constitutional_compliance(response)
    
    data = response.json()
    assert "constitutional" in data["error"].lower()
```

## 🚀 Performance Testing Framework

### 1. Latency Testing

**P99 Latency Validation:**
```python
import time
import statistics

async def test_p99_latency_target(self, client):
    """Test that P99 latency meets <5ms target."""
    latencies = []
    
    # Perform 100 requests to get statistical significance
    for _ in range(100):
        start_time = time.perf_counter()
        
        response = client.get("/health")
        
        end_time = time.perf_counter()
        latency_ms = (end_time - start_time) * 1000
        latencies.append(latency_ms)
        
        assert response.status_code == 200
        self.assert_constitutional_compliance(response)
    
    # Calculate P99 latency
    p99_latency = statistics.quantiles(latencies, n=100)[98]  # 99th percentile
    
    assert p99_latency < 5.0, f"P99 latency {p99_latency:.2f}ms exceeds 5ms target"
```

### 2. Throughput Testing

**RPS Target Validation:**
```python
import asyncio
import aiohttp

async def test_throughput_target(self):
    """Test that service can handle >100 RPS."""
    target_rps = 100
    test_duration = 10  # seconds
    total_requests = target_rps * test_duration
    
    async def make_request(session):
        async with session.get("http://localhost:8001/health") as response:
            assert response.status == 200
            data = await response.json()
            assert data.get("constitutional_hash") == "cdd01ef066bc6cf2"
            return response.status
    
    start_time = time.time()
    
    async with aiohttp.ClientSession() as session:
        tasks = [make_request(session) for _ in range(total_requests)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
    
    end_time = time.time()
    actual_duration = end_time - start_time
    successful_requests = sum(1 for r in results if r == 200)
    actual_rps = successful_requests / actual_duration
    
    assert actual_rps >= target_rps, f"Actual RPS {actual_rps:.1f} below target {target_rps}"
```

### 3. Cache Performance Testing

**Cache Hit Rate Validation:**
```python
async def test_cache_hit_rate_target(self, client, redis_client):
    """Test that cache hit rate meets >85% target."""
    cache_key = "test:cache:performance"
    
    # Prime the cache
    await redis_client.set(cache_key, json.dumps({
        "data": "test_data",
        "constitutional_hash": "cdd01ef066bc6cf2"
    }), ex=300)
    
    hits = 0
    total_requests = 100
    
    for i in range(total_requests):
        # Make requests that should hit cache
        response = client.get(f"/api/v1/cached-data/{i % 10}")  # Repeat keys for cache hits
        
        assert response.status_code == 200
        self.assert_constitutional_compliance(response)
        
        # Check if response came from cache
        if response.headers.get("X-Cache-Status") == "HIT":
            hits += 1
    
    hit_rate = hits / total_requests
    assert hit_rate >= 0.85, f"Cache hit rate {hit_rate:.2%} below 85% target"
```

## 🔄 Integration Testing Framework

### 1. Service-to-Service Testing

**Inter-Service Communication:**
```python
async def test_service_integration(self):
    """Test integration between ACGS services."""
    # Test Constitutional AI service integration
    constitutional_response = await call_constitutional_ai_service({
        "content": "Test content",
        "validation_type": "standard"
    }, tenant_id="test-tenant")
    
    assert constitutional_response["valid"] is True
    assert constitutional_response["constitutional_hash"] == "cdd01ef066bc6cf2"
    
    # Test Auth service integration
    auth_response = await call_auth_service({
        "token": "test-jwt-token"
    })
    
    assert auth_response["valid"] is True
    assert auth_response["tenant_id"] == "test-tenant"
```

### 2. Database Integration Testing

**Multi-Tenant Database Testing:**
```python
async def test_database_rls_integration(self, db_session):
    """Test Row-Level Security integration."""
    # Set tenant context
    await db_session.execute(
        text("SELECT set_config('app.current_tenant_id', :tenant_id, true)"),
        {"tenant_id": "test-tenant"}
    )
    
    # Create test data
    resource = YourModel(
        name="Test Resource",
        tenant_id="test-tenant",
        constitutional_hash="cdd01ef066bc6cf2"
    )
    db_session.add(resource)
    await db_session.commit()
    
    # Query should only return tenant's data
    result = await db_session.execute(select(YourModel))
    resources = result.scalars().all()
    
    assert len(resources) == 1
    assert resources[0].tenant_id == "test-tenant"
    assert resources[0].constitutional_hash == "cdd01ef066bc6cf2"
```

## 📊 Test Coverage and Quality Metrics

### Coverage Targets

- **Unit Test Coverage**: >80% (Target for Task 10/10)
- **Integration Test Coverage**: >70%
- **API Endpoint Coverage**: 100%
- **Constitutional Compliance Coverage**: 100%

### Quality Metrics

```python
# Example coverage validation
def test_coverage_targets():
    """Validate that test coverage meets targets."""
    coverage_report = get_coverage_report()
    
    assert coverage_report.unit_coverage >= 0.80
    assert coverage_report.integration_coverage >= 0.70
    assert coverage_report.api_coverage == 1.0
    assert coverage_report.constitutional_coverage == 1.0
```

## 🚀 Preparation for Testing Strategy Implementation

### Ready-to-Implement Components

1. **Test Framework**: Base classes and utilities ready
2. **Constitutional Testing**: Compliance validation patterns established
3. **Performance Testing**: Latency, throughput, and cache testing ready
4. **Multi-Tenant Testing**: Isolation and context testing patterns ready
5. **Integration Testing**: Service-to-service communication patterns ready

### Implementation Roadmap for Task 10/10

1. **Week 1**: Implement unified test runner and CI/CD integration
2. **Week 2**: Deploy comprehensive test suite across all services
3. **Week 3**: Performance test automation and monitoring integration
4. **Week 4**: Final validation and production readiness certification

### Success Criteria for Task 10/10

- [ ] All services achieve >80% test coverage
- [ ] Constitutional compliance testing at 100%
- [ ] Performance targets validated automatically
- [ ] Multi-tenant isolation verified
- [ ] CI/CD pipeline with automated testing
- [ ] Production readiness certification complete



## Implementation Status

- ✅ **Constitutional Hash Validation**: Active enforcement of `cdd01ef066bc6cf2`
- 🔄 **Performance Monitoring**: Continuous validation of targets
- ✅ **Documentation Standards**: Compliant with ACGS-2 requirements
- 🔄 **Cross-Reference Validation**: Ongoing link integrity maintenance

**Overall Status**: 🔄 IN PROGRESS - Systematic enhancement implementation

## Performance Targets

This component maintains the following performance requirements:

- **P99 Latency**: <5ms (constitutional requirement)
- **Throughput**: >100 RPS (minimum operational standard)
- **Cache Hit Rate**: >85% (efficiency requirement)
- **Constitutional Compliance**: 100% (hash: cdd01ef066bc6cf2)

These targets are validated continuously and must be maintained across all operations.

---

**Constitutional Hash**: `cdd01ef066bc6cf2`  
**Testing Foundation**: Complete and ready for implementation  
**Next Phase**: Testing Strategy Implementation (Task 10/10)

## Related Information

For a broader understanding of the ACGS platform and its components, refer to:

- **Unified Architecture Guide**: For a comprehensive overview of the ACGS architecture, see the [ACGS Unified Architecture Guide](../architecture/ACGS_UNIFIED_ARCHITECTURE_GUIDE.md).
- **GEMINI.md**: For a comprehensive overview of the entire ACGS project, including development environment setup, testing commands, and service architecture, see the [GEMINI.md](../../GEMINI.md) file.
