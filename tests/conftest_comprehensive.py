"""
Comprehensive Test Configuration for ACGS-1 Services

This module provides centralized test configuration, fixtures, and utilities
for comprehensive testing across all 8 ACGS services with >80% coverage target.

Key Features:
- Service-specific test fixtures
- Mock implementations for external dependencies
- Database test setup and teardown
- Authentication test utilities
- Performance testing helpers
- Integration test support
"""

import asyncio
import os
import sys
from collections.abc import AsyncGenerator
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Add project root to Python path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "services" / "shared"))

# Test database configuration
TEST_DB_URL = "sqlite+aiosqlite:///./test_acgs.db"

# Service port mappings
SERVICE_PORTS = {
    "auth": 8000,
    "ac": 8001,
    "integrity": 8002,
    "fv": 8003,
    "gs": 8004,
    "pgc": 8005,
    "ec": 8006,
    "research": 8007,
}

# Service base URLs for testing
SERVICE_URLS = {
    name: f"http://localhost:{port}" for name, port in SERVICE_PORTS.items()
}


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_db_engine():
    """Create test database engine."""
    engine = create_async_engine(TEST_DB_URL, echo=False)
    yield engine
    await engine.dispose()


@pytest.fixture
async def test_db_session(test_db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session = sessionmaker(
        test_db_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


@pytest.fixture
def mock_redis():
    """Mock Redis client for testing."""
    mock_redis = MagicMock()
    mock_redis.get = AsyncMock(return_value=None)
    mock_redis.set = AsyncMock(return_value=True)
    mock_redis.setex = AsyncMock(return_value=True)
    mock_redis.delete = AsyncMock(return_value=True)
    mock_redis.exists = AsyncMock(return_value=False)
    return mock_redis


@pytest.fixture
def mock_service_client():
    """Mock service client for inter-service communication."""
    mock_client = MagicMock()
    mock_client.get = AsyncMock()
    mock_client.post = AsyncMock()
    mock_client.put = AsyncMock()
    mock_client.delete = AsyncMock()
    return mock_client


@pytest.fixture
def test_user_data():
    """Test user data for authentication tests."""
    return {
        "email": "test@acgs.gov",
        "password": "SecureTestPassword123!",
        "full_name": "Test User",
        "roles": ["user"],
        "is_active": True,
    }


@pytest.fixture
def test_principle_data():
    """Test constitutional principle data."""
    return {
        "title": "Test Constitutional Principle",
        "content": "This is a test constitutional principle for validation.",
        "category": "democratic_process",
        "priority": 5,
        "constitutional_hash": "cdd01ef066bc6cf2",
        "is_active": True,
    }


@pytest.fixture
def test_policy_data():
    """Test policy data for governance tests."""
    return {
        "title": "Test Policy",
        "description": "Test policy for governance validation",
        "content": "This is test policy content for validation.",
        "category": "governance",
        "status": "draft",
        "constitutional_compliance": True,
    }


@pytest.fixture
def mock_llm_client():
    """Mock LLM client for testing AI operations."""
    mock_client = MagicMock()
    mock_client.generate_response = AsyncMock(
        return_value={
            "response": "Test LLM response",
            "confidence": 0.95,
            "model": "test-model",
            "tokens_used": 100,
        }
    )
    mock_client.validate_content = AsyncMock(
        return_value={
            "is_valid": True,
            "confidence": 0.98,
            "violations": [],
        }
    )
    return mock_client


@pytest.fixture
def mock_constitutional_validator():
    """Mock constitutional validator for testing compliance."""
    mock_validator = MagicMock()
    mock_validator.validate_hash = AsyncMock(
        return_value={
            "hash_valid": True,
            "constitutional_hash": "cdd01ef066bc6cf2",
            "compliance_score": 0.95,
        }
    )
    mock_validator.validate_policy = AsyncMock(
        return_value={
            "compliant": True,
            "score": 0.92,
            "violations": [],
        }
    )
    return mock_validator


@pytest.fixture
def performance_metrics():
    """Performance metrics tracking for tests."""
    return {
        "response_times": [],
        "memory_usage": [],
        "cpu_usage": [],
        "error_count": 0,
        "success_count": 0,
    }


class MockServiceRegistry:
    """Mock service registry for testing service discovery."""

    def __init__(self):
        self.services = {
            name: {"url": url, "status": "healthy", "version": "3.0.0"}
            for name, url in SERVICE_URLS.items()
        }

    async def get_service_url(self, service_name: str) -> str:
        return self.services.get(service_name, {}).get("url", "")

    async def register_service(self, name: str, url: str) -> bool:
        self.services[name] = {"url": url, "status": "healthy"}
        return True

    async def health_check(self, service_name: str) -> bool:
        return service_name in self.services


@pytest.fixture
def mock_service_registry():
    """Mock service registry fixture."""
    return MockServiceRegistry()


@pytest.fixture
def test_constitutional_hash():
    """Standard constitutional hash for testing."""
    return "cdd01ef066bc6cf2"


@pytest.fixture
def mock_prometheus_metrics():
    """Mock Prometheus metrics for testing."""
    mock_metrics = MagicMock()
    mock_metrics.inc = MagicMock()
    mock_metrics.observe = MagicMock()
    mock_metrics.set = MagicMock()
    return mock_metrics


# Test markers for categorizing tests
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.performance = pytest.mark.performance
pytest.mark.security = pytest.mark.security
pytest.mark.e2e = pytest.mark.e2e


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "performance: Performance tests")
    config.addinivalue_line("markers", "security: Security tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add default markers."""
    for item in items:
        # Add unit marker to tests without specific markers
        if not any(
            mark.name in ["integration", "performance", "security", "e2e"]
            for mark in item.iter_markers()
        ):
            item.add_marker(pytest.mark.unit)


# Environment setup for testing
os.environ.setdefault("TESTING", "true")
os.environ.setdefault("DATABASE_URL", TEST_DB_URL)
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/1")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only")
os.environ.setdefault("CONSTITUTIONAL_HASH", "cdd01ef066bc6cf2")
