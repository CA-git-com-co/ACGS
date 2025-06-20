"""
Simplified test configuration for DGM Service.

Basic test fixtures that don't require external dependencies.
"""

import asyncio
import os
import pytest
import tempfile
from datetime import datetime, timedelta
from typing import Dict, Any
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_workspace():
    """Create temporary workspace for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        workspace_path = os.path.join(temp_dir, "test_workspace")
        os.makedirs(workspace_path, exist_ok=True)
        yield workspace_path


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
            "completed_at": datetime.utcnow() + timedelta(minutes=5)
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
            "constitutional_hash": "cdd01ef066bc6cf2"
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
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as an end-to-end test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
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
