"""
ACGS Code Analysis Engine - Test Configuration
Pytest configuration and fixtures for comprehensive testing.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import os
import tempfile
import shutil
from typing import AsyncGenerator, Dict, Any, List
from pathlib import Path

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import redis.asyncio as redis
from httpx import AsyncClient

# Add the service directory to Python path
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from config.settings import Settings, get_settings
from config.database import DatabaseManager
from app.services.cache_service import CacheService
from app.models.database import Base
from app.utils.constitutional import CONSTITUTIONAL_HASH


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as a performance test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "constitutional: mark test as constitutional compliance test"
    )


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# SETTINGS AND CONFIGURATION FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """Test settings with overrides for testing environment"""
    
    # Create temporary directory for test database
    test_db_dir = tempfile.mkdtemp(prefix="acgs_test_db_")
    test_db_path = os.path.join(test_db_dir, "test.db")
    
    # Override settings for testing
    test_env = {
        "ENVIRONMENT": "testing",
        "POSTGRESQL_HOST": "localhost",
        "POSTGRESQL_PORT": "5439",
        "POSTGRESQL_DATABASE": "acgs_test",
        "POSTGRESQL_USER": "acgs_test_user",
        "POSTGRESQL_PASSWORD": "test_password",
        "REDIS_HOST": "localhost",
        "REDIS_PORT": "6389",
        "REDIS_DB": "15",  # Use separate Redis DB for testing
        "LOG_LEVEL": "DEBUG",
        "PROMETHEUS_ENABLED": "false",
        "WATCH_PATHS": test_db_dir,
        "CONSTITUTIONAL_HASH": "cdd01ef066bc6cf2"
    }
    
    # Set environment variables
    for key, value in test_env.items():
        os.environ[key] = value
    
    # Clear settings cache and create new instance
    get_settings.cache_clear()
    settings = get_settings()
    
    yield settings
    
    # Cleanup
    if os.path.exists(test_db_dir):
        shutil.rmtree(test_db_dir)


# ============================================================================
# DATABASE FIXTURES
# ============================================================================

@pytest_asyncio.fixture(scope="session")
async def test_db_engine(test_settings):
    """Create test database engine"""
    # Use in-memory SQLite for fast testing
    database_url = "sqlite+aiosqlite:///:memory:"
    
    engine = create_async_engine(
        database_url,
        echo=False,
        pool_pre_ping=True
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()


@pytest_asyncio.fixture
async def test_db_session(test_db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session with transaction rollback"""
    AsyncSessionLocal = sessionmaker(
        test_db_engine, 
        class_=AsyncSession, 
        expire_on_commit=False
    )
    
    async with AsyncSessionLocal() as session:
        # Start a transaction
        transaction = await session.begin()
        
        try:
            yield session
        finally:
            # Rollback transaction to ensure test isolation
            await transaction.rollback()


@pytest_asyncio.fixture
async def test_db_manager(test_db_engine, test_settings) -> DatabaseManager:
    """Create test database manager"""
    db_manager = DatabaseManager("sqlite+aiosqlite:///:memory:")
    db_manager.engine = test_db_engine
    await db_manager.initialize()
    
    yield db_manager
    
    await db_manager.close()


# ============================================================================
# CACHE FIXTURES
# ============================================================================

@pytest_asyncio.fixture
async def test_cache_service(test_settings) -> CacheService:
    """Create test cache service with fakeredis"""
    try:
        # Try to use real Redis for integration tests
        cache_service = CacheService(
            redis_url=test_settings.redis_url,
            redis_db=15  # Use separate DB for testing
        )
        await cache_service.initialize()
        
        # Clear test database
        await cache_service.redis_client.flushdb()
        
        yield cache_service
        
        # Cleanup
        await cache_service.redis_client.flushdb()
        await cache_service.close()
        
    except Exception:
        # Fallback to fake Redis for unit tests
        import fakeredis.aioredis
        
        fake_redis = fakeredis.aioredis.FakeRedis()
        cache_service = CacheService("redis://localhost:6379/15", redis_db=15)
        cache_service.redis_client = fake_redis
        
        yield cache_service


# ============================================================================
# APPLICATION FIXTURES
# ============================================================================

@pytest.fixture
def test_client(test_settings) -> TestClient:
    """Create test client for synchronous testing"""
    # Override app dependencies for testing
    app.dependency_overrides[get_settings] = lambda: test_settings
    
    with TestClient(app) as client:
        yield client
    
    # Clear overrides
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_async_client(test_settings) -> AsyncGenerator[AsyncClient, None]:
    """Create async test client for asynchronous testing"""
    # Override app dependencies for testing
    app.dependency_overrides[get_settings] = lambda: test_settings
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    # Clear overrides
    app.dependency_overrides.clear()


# ============================================================================
# AUTHENTICATION FIXTURES
# ============================================================================

@pytest.fixture
def mock_auth_token() -> str:
    """Mock JWT token for testing"""
    return "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoidGVzdF91c2VyIiwidXNlcm5hbWUiOiJ0ZXN0X3VzZXIiLCJyb2xlcyI6WyJhZG1pbiJdLCJleHAiOjk5OTk5OTk5OTl9.test_signature"


@pytest.fixture
def auth_headers(mock_auth_token) -> Dict[str, str]:
    """Authentication headers for testing"""
    return {"Authorization": f"Bearer {mock_auth_token}"}


@pytest.fixture
def mock_user_info() -> Dict[str, Any]:
    """Mock user information for testing"""
    return {
        "user_id": "test_user",
        "username": "test_user",
        "email": "test@acgs.ai",
        "roles": ["admin"],
        "permissions": ["code_analysis:read", "code_analysis:write"],
        "constitutional_hash": CONSTITUTIONAL_HASH
    }


# ============================================================================
# TEST DATA FIXTURES
# ============================================================================

@pytest.fixture
def sample_python_code() -> str:
    """Sample Python code for testing"""
    return '''
def validate_user_permissions(user_id: str, required_permissions: List[str]) -> bool:
    """
    Validate that a user has the required permissions.
    
    Args:
        user_id: The user identifier
        required_permissions: List of required permission strings
        
    Returns:
        True if user has all required permissions, False otherwise
    """
    user = get_user_by_id(user_id)
    if not user:
        return False
    
    user_permissions = set(user.permissions)
    required_permissions_set = set(required_permissions)
    
    return required_permissions_set.issubset(user_permissions)


class UserPermissionValidator:
    """Validates user permissions against policies."""
    
    def __init__(self, policy_engine):
        self.policy_engine = policy_engine
    
    def validate(self, user_id: str, action: str) -> bool:
        """Validate user action against policies."""
        return self.policy_engine.evaluate(user_id, action)
'''


@pytest.fixture
def sample_javascript_code() -> str:
    """Sample JavaScript code for testing"""
    return '''
/**
 * Validates user authentication token
 * @param {string} token - JWT token to validate
 * @returns {Promise<boolean>} True if token is valid
 */
async function validateAuthToken(token) {
    try {
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        const user = await User.findById(decoded.userId);
        return user && user.isActive;
    } catch (error) {
        console.error('Token validation failed:', error);
        return false;
    }
}

class AuthenticationService {
    constructor(config) {
        this.config = config;
        this.tokenCache = new Map();
    }
    
    async authenticate(credentials) {
        // Authentication logic here
        return this.generateToken(credentials.userId);
    }
}
'''


@pytest.fixture
def sample_code_symbols() -> List[Dict[str, Any]]:
    """Sample code symbols for testing"""
    return [
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "file_path": "/test/auth.py",
            "symbol_name": "validate_user_permissions",
            "symbol_type": "function",
            "language": "python",
            "start_line": 1,
            "end_line": 15,
            "signature": "validate_user_permissions(user_id: str, required_permissions: List[str]) -> bool",
            "docstring": "Validate that a user has the required permissions.",
            "is_public": True,
            "constitutional_hash": CONSTITUTIONAL_HASH
        },
        {
            "id": "123e4567-e89b-12d3-a456-426614174001",
            "file_path": "/test/auth.py",
            "symbol_name": "UserPermissionValidator",
            "symbol_type": "class",
            "language": "python",
            "start_line": 18,
            "end_line": 25,
            "signature": "class UserPermissionValidator",
            "docstring": "Validates user permissions against policies.",
            "is_public": True,
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
    ]


@pytest.fixture
def sample_dependencies() -> List[Dict[str, Any]]:
    """Sample dependencies for testing"""
    return [
        {
            "id": "dep-123e4567-e89b-12d3-a456-426614174000",
            "source_symbol_id": "123e4567-e89b-12d3-a456-426614174000",
            "target_symbol_id": "123e4567-e89b-12d3-a456-426614174001",
            "dependency_type": "call",
            "is_external": False,
            "confidence_score": 0.95,
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
    ]


# ============================================================================
# PERFORMANCE TESTING FIXTURES
# ============================================================================

@pytest.fixture
def performance_test_data() -> Dict[str, Any]:
    """Performance test data and thresholds"""
    return {
        "target_p99_latency_ms": 10.0,
        "target_cache_hit_rate": 0.85,
        "target_throughput_rps": 100.0,
        "max_memory_usage_mb": 512,
        "test_duration_seconds": 60,
        "concurrent_users": 10
    }


@pytest.fixture
def load_test_queries() -> List[str]:
    """Sample queries for load testing"""
    return [
        "authentication function",
        "user validation",
        "permission check",
        "token verification",
        "security validation",
        "access control",
        "authorization logic",
        "user management",
        "session handling",
        "credential validation"
    ]


# ============================================================================
# MOCK SERVICE FIXTURES
# ============================================================================

@pytest_asyncio.fixture
async def mock_auth_service(httpx_mock):
    """Mock Auth Service responses"""
    httpx_mock.add_response(
        method="POST",
        url="http://localhost:8016/api/v1/auth/validate",
        json={
            "valid": True,
            "user_id": "test_user",
            "username": "test_user",
            "roles": ["admin"],
            "permissions": ["code_analysis:read", "code_analysis:write"],
            "constitutional_hash": CONSTITUTIONAL_HASH
        },
        status_code=200
    )


@pytest_asyncio.fixture
async def mock_context_service(httpx_mock):
    """Mock Context Service responses"""
    httpx_mock.add_response(
        method="GET",
        url="http://localhost:8012/api/v1/context/retrieve",
        json={
            "results": [
                {
                    "context_id": "ctx-123",
                    "context_type": "DomainContext",
                    "relevance_score": 0.9,
                    "content": "Authentication and authorization domain context"
                }
            ],
            "total_results": 1,
            "constitutional_compliance": {"hash": CONSTITUTIONAL_HASH}
        },
        status_code=200
    )


# ============================================================================
# CLEANUP FIXTURES
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup_environment():
    """Cleanup environment after each test"""
    yield
    
    # Clear any test environment variables
    test_env_vars = [
        "ENVIRONMENT", "POSTGRESQL_DATABASE", "REDIS_DB",
        "LOG_LEVEL", "PROMETHEUS_ENABLED"
    ]
    
    for var in test_env_vars:
        if var in os.environ:
            del os.environ[var]
    
    # Clear settings cache
    get_settings.cache_clear()


# ============================================================================
# CONSTITUTIONAL COMPLIANCE FIXTURES
# ============================================================================

@pytest.fixture
def constitutional_validator():
    """Constitutional compliance validator for testing"""
    from app.utils.constitutional import ConstitutionalValidator
    return ConstitutionalValidator(CONSTITUTIONAL_HASH)


@pytest.fixture
def constitutional_test_data() -> Dict[str, Any]:
    """Test data with constitutional compliance"""
    return {
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "test_data": {
            "symbol_id": "test-symbol-123",
            "analysis_result": {"type": "function", "complexity": 5}
        },
        "expected_signature": "expected_constitutional_signature_here"
    }
