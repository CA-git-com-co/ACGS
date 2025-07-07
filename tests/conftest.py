"""
ACGS Test Configuration and Fixtures
Constitutional Hash: cdd01ef066bc6cf2

Global test configuration for ACGS test suite including:
- Database and Redis mocking
- Service endpoint configuration
- Authentication fixtures
- Performance testing utilities
- Constitutional compliance validation
"""

import asyncio
import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest
import pytest_asyncio

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Service endpoints configuration
SERVICE_ENDPOINTS = {
    "auth_service": "http://localhost:8016",
    "constitutional_ai": "http://localhost:8001",
    "integrity_service": "http://localhost:8002",
    "formal_verification": "http://localhost:8003",
    "governance_synthesis": "http://localhost:8004",
    "policy_governance": "http://localhost:8005",
    "evolutionary_computation": "http://localhost:8006",
    "acgs_pgp": "http://localhost:8010",
}

# Test database configuration
TEST_DATABASE_URL = (
    "postgresql+asyncpg://test_user:test_pass@localhost:5439/test_acgs_db"
)
TEST_REDIS_URL = "redis://localhost:6389/0"

# JWT configuration for testing
TEST_JWT_SECRET = os.getenv("SECRET_KEY", "test_jwt_secret_for_acgs_testing")
TEST_JWT_ALGORITHM = "HS256"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def mock_redis():
    """Mock Redis client for testing."""
    redis_mock = AsyncMock()

    # Configure async methods properly
    redis_mock.get = AsyncMock(return_value=None)
    redis_mock.set = AsyncMock(return_value=True)
    redis_mock.exists = AsyncMock(return_value=False)
    redis_mock.hget = AsyncMock(return_value=None)
    redis_mock.hset = AsyncMock(return_value=True)
    redis_mock.delete = AsyncMock(return_value=True)
    redis_mock.flushdb = AsyncMock(return_value=True)
    redis_mock.ping = AsyncMock(return_value=True)

    return redis_mock


@pytest.fixture
async def mock_database():
    """Mock database connection for testing."""
    db_mock = AsyncMock()

    # Configure database methods
    db_mock.execute = AsyncMock(return_value=Mock())
    db_mock.fetch = AsyncMock(return_value=[])
    db_mock.fetchrow = AsyncMock(return_value=None)
    db_mock.fetchval = AsyncMock(return_value=None)

    return db_mock


@pytest.fixture
async def mock_http_client():
    """Mock HTTP client for service communication."""
    client = AsyncMock()

    # Configure async methods properly
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json = Mock(
        return_value={"status": "healthy", "constitutional_hash": CONSTITUTIONAL_HASH}
    )
    mock_response.text = "OK"

    client.get = AsyncMock(return_value=mock_response)
    client.post = AsyncMock(return_value=mock_response)
    client.put = AsyncMock(return_value=mock_response)
    client.delete = AsyncMock(return_value=mock_response)

    return client


@pytest.fixture
def sample_auth_token():
    """Sample authentication token for testing."""
    return {
        "token": "mock_jwt_token_123",
        "user_id": "test_user",
        "permissions": ["read", "write", "admin"],
        "expires_at": "2025-07-07T12:00:00Z",
        "constitutional_hash": CONSTITUTIONAL_HASH,
    }


@pytest.fixture
def sample_policy():
    """Sample policy for testing constitutional validation."""
    return {
        "id": "test_policy_001",
        "name": "Democratic Governance Policy",
        "content": (
            "All citizens shall have equal rights to participate in governance "
            "decisions through transparent democratic processes."
        ),
        "metadata": {
            "category": "governance",
            "priority": "high",
            "constitutional_hash": CONSTITUTIONAL_HASH,
        },
    }


@pytest.fixture
def performance_targets():
    """Performance targets for ACGS services."""
    return {
        "p99_latency_ms": 5.0,
        "throughput_rps": 100,
        "cache_hit_rate": 0.85,
        "constitutional_compliance": True,
        "memory_usage_mb": 512,
        "cpu_usage_percent": 80,
    }


@pytest.fixture
async def mock_constitutional_service():
    """Mock Constitutional AI Service for testing."""
    service = AsyncMock()

    service.validate_policy = AsyncMock(
        return_value={
            "compliant": True,
            "confidence_score": 0.85,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "validation_details": {
                "principles_checked": ["democratic_participation", "transparency"],
                "scores": {"democratic_participation": 0.9, "transparency": 0.8},
            },
        }
    )

    return service


@pytest.fixture
async def mock_evolutionary_service():
    """Mock Evolutionary Computation Service for testing."""
    service = AsyncMock()

    service.evaluate_fitness = AsyncMock(
        return_value={
            "fitness_score": 0.85,
            "generation": 1,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "metrics": {"performance": 0.9, "compliance": 0.8, "efficiency": 0.85},
        }
    )

    return service


@pytest.fixture
async def mock_auth_service():
    """Mock Authentication Service for testing."""
    service = AsyncMock()

    service.validate_token = AsyncMock(
        return_value={
            "valid": True,
            "user_id": "test_user",
            "permissions": ["read", "write"],
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }
    )

    service.generate_token = AsyncMock(
        return_value={
            "token": "mock_jwt_token",
            "expires_at": "2025-07-07T12:00:00Z",
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }
    )

    return service


# Test environment setup
def pytest_configure(config):
    """Configure pytest with ACGS-specific settings."""
    # Set environment variables for testing
    os.environ["ACGS_ENVIRONMENT"] = "test"
    os.environ["ACGS_DATABASE_URL"] = TEST_DATABASE_URL
    os.environ["ACGS_REDIS_URL"] = TEST_REDIS_URL
    os.environ["ACGS_JWT_SECRET"] = TEST_JWT_SECRET
    os.environ["ACGS_JWT_ALGORITHM"] = TEST_JWT_ALGORITHM
    os.environ["ACGS_CONSTITUTIONAL_HASH"] = CONSTITUTIONAL_HASH


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers."""
    for item in items:
        # Add asyncio marker to all async tests
        if asyncio.iscoroutinefunction(item.function):
            item.add_marker(pytest.mark.asyncio)

        # Add performance marker to performance tests
        if "performance" in item.nodeid:
            item.add_marker(pytest.mark.performance)

        # Add integration marker to integration tests
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)


# Pytest markers
pytest_plugins = ["pytest_asyncio"]

# Configure asyncio for testing
asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
