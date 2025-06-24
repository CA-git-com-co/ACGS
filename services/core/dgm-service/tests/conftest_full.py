"""
Test configuration and fixtures for DGM Service.

This module provides shared fixtures, test configuration, and utilities
for comprehensive testing of the Darwin Gödel Machine Service.
"""

import asyncio
import os
import tempfile
from datetime import datetime, timedelta
from typing import Any, AsyncGenerator, Dict, Optional
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import httpx
import pytest
from dgm_service.auth.auth_client import AuthClient
from dgm_service.config import settings
from dgm_service.core.archive_manager import ArchiveManager
from dgm_service.core.constitutional_validator import ConstitutionalValidator
from dgm_service.core.dgm_engine import DGMEngine
from dgm_service.core.performance_monitor import PerformanceMonitor
from dgm_service.database import Base, get_db

# Import DGM service components
from dgm_service.main import app
from dgm_service.models import (
    BanditState,
    ConstitutionalComplianceLog,
    DGMArchive,
    ImprovementWorkspace,
    PerformanceMetric,
    SystemConfiguration,
)
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Test database configuration
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_db_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def test_db_session(test_db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session = sessionmaker(test_db_engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session


@pytest.fixture
def override_get_db(test_db_session):
    """Override database dependency for testing."""

    async def _override_get_db():
        yield test_db_session

    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def test_client(override_get_db):
    """Create test client with database override."""
    with TestClient(app) as client:
        yield client


@pytest.fixture
async def async_test_client(override_get_db):
    """Create async test client."""
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_auth_client():
    """Mock authentication client."""
    mock_client = AsyncMock(spec=AuthClient)
    mock_client.validate_token.return_value = {
        "user_id": str(uuid4()),
        "username": "test_user",
        "roles": ["dgm_user"],
        "permissions": ["dgm:read", "dgm:write", "dgm:execute"],
    }
    mock_client.check_permission.return_value = True
    return mock_client


@pytest.fixture
def mock_dgm_engine():
    """Mock DGM engine for testing."""
    mock_engine = AsyncMock(spec=DGMEngine)
    mock_engine.generate_improvement_proposal.return_value = {
        "strategy": "performance_optimization",
        "target_services": ["gs-service"],
        "priority": "medium",
        "expected_improvement": 0.15,
        "risk_assessment": {"risk_level": "low", "confidence": 0.85},
    }
    mock_engine.execute_improvement.return_value = {
        "success": True,
        "improvement_metrics": {"performance_gain": 0.12},
        "execution_time": 45.2,
    }
    return mock_engine


@pytest.fixture
def mock_constitutional_validator():
    """Mock constitutional validator."""
    mock_validator = AsyncMock(spec=ConstitutionalValidator)
    mock_validator.validate_proposal.return_value = {
        "is_compliant": True,
        "compliance_score": 0.95,
        "violations": [],
        "recommendations": [],
    }
    mock_validator.validate_execution.return_value = {
        "is_compliant": True,
        "compliance_score": 0.92,
        "constitutional_hash": "cdd01ef066bc6cf2",
    }
    return mock_validator


@pytest.fixture
def mock_performance_monitor():
    """Mock performance monitor."""
    mock_monitor = AsyncMock(spec=PerformanceMonitor)
    mock_monitor.get_current_metrics.return_value = {
        "response_time": 125.5,
        "throughput": 850.2,
        "error_rate": 0.002,
        "cpu_usage": 0.45,
        "memory_usage": 0.62,
    }
    mock_monitor.record_metric.return_value = True
    return mock_monitor


@pytest.fixture
def mock_archive_manager():
    """Mock archive manager."""
    mock_manager = AsyncMock(spec=ArchiveManager)
    mock_manager.store_improvement.return_value = str(uuid4())
    mock_manager.get_improvement.return_value = {
        "id": str(uuid4()),
        "strategy": "test_strategy",
        "status": "completed",
        "created_at": datetime.utcnow(),
    }
    return mock_manager


@pytest.fixture
def sample_improvement_request():
    """Sample improvement request for testing."""
    return {
        "target_services": ["gs-service"],
        "priority": "medium",
        "strategy_hint": "performance_optimization",
        "constraints": {
            "max_risk_level": "medium",
            "max_execution_time": 300,
            "rollback_threshold": -0.05,
        },
        "metadata": {"requester": "test_user", "reason": "performance_testing"},
    }


@pytest.fixture
def sample_performance_metrics():
    """Sample performance metrics for testing."""
    return [
        {
            "metric_name": "response_time",
            "value": 125.5,
            "timestamp": datetime.utcnow(),
            "service_name": "dgm-service",
            "tags": {"endpoint": "/api/v1/dgm/improve"},
        },
        {
            "metric_name": "throughput",
            "value": 850.2,
            "timestamp": datetime.utcnow(),
            "service_name": "dgm-service",
            "tags": {"endpoint": "/api/v1/dgm/improve"},
        },
    ]


@pytest.fixture
def sample_constitutional_log():
    """Sample constitutional compliance log."""
    return {
        "improvement_id": str(uuid4()),
        "compliance_level": "HIGH",
        "compliance_score": 0.95,
        "constitutional_hash": "cdd01ef066bc6cf2",
        "validation_details": {"checks_passed": 15, "checks_failed": 0, "warnings": 1},
        "validator_version": "1.0.0",
    }


@pytest.fixture
def sample_bandit_state():
    """Sample bandit algorithm state."""
    return {
        "algorithm_type": "UCB1",
        "arms": {
            "performance_optimization": {"pulls": 25, "rewards": 18.5},
            "code_refactoring": {"pulls": 15, "rewards": 12.2},
            "architecture_improvement": {"pulls": 10, "rewards": 7.8},
        },
        "exploration_parameter": 1.414,
        "total_pulls": 50,
        "average_reward": 0.772,
    }


@pytest.fixture
def temp_workspace():
    """Create temporary workspace for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        workspace_path = os.path.join(temp_dir, "test_workspace")
        os.makedirs(workspace_path, exist_ok=True)
        yield workspace_path


@pytest.fixture
def mock_redis():
    """Mock Redis client for testing."""
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True
    mock_redis.delete.return_value = 1
    mock_redis.exists.return_value = False
    mock_redis.expire.return_value = True
    return mock_redis


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    mock_client = AsyncMock()
    mock_client.chat.completions.create.return_value = MagicMock(
        choices=[
            MagicMock(
                message=MagicMock(content='{"improvement_type": "performance", "confidence": 0.85}')
            )
        ]
    )
    return mock_client


@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic client for testing."""
    mock_client = AsyncMock()
    mock_client.messages.create.return_value = MagicMock(
        content=[MagicMock(text='{"analysis": "code_optimization", "risk_level": "low"}')]
    )
    return mock_client


# Test data factories
class TestDataFactory:
    """Factory for creating test data objects."""

    @staticmethod
    def create_dgm_archive(**kwargs) -> Dict[str, Any]:
        """Create DGM archive test data."""
        defaults = {
            "id": str(uuid4()),
            "improvement_type": "performance_optimization",
            "status": "completed",
            "strategy_used": "gradient_descent",
            "target_services": ["gs-service"],
            "performance_before": {"response_time": 150.0},
            "performance_after": {"response_time": 125.0},
            "constitutional_compliance_score": 0.95,
            "created_at": datetime.utcnow(),
            "completed_at": datetime.utcnow() + timedelta(minutes=5),
        }
        defaults.update(kwargs)
        return defaults

    @staticmethod
    def create_performance_metric(**kwargs) -> Dict[str, Any]:
        """Create performance metric test data."""
        defaults = {
            "id": str(uuid4()),
            "metric_name": "response_time",
            "value": 125.5,
            "timestamp": datetime.utcnow(),
            "service_name": "dgm-service",
            "constitutional_hash": "cdd01ef066bc6cf2",
        }
        defaults.update(kwargs)
        return defaults


@pytest.fixture
def test_data_factory():
    """Provide test data factory."""
    return TestDataFactory


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "e2e: mark test as an end-to-end test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line(
        "markers", "constitutional: mark test as constitutional compliance test"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test location."""
    for item in items:
        # Add markers based on test file location
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)

        # Add slow marker for tests that might be slow
        if any(keyword in item.name.lower() for keyword in ["performance", "load", "stress"]):
            item.add_marker(pytest.mark.slow)
