"""
Pytest configuration for ACGS test suite.
Sets up Python path, imports, and mocks for comprehensive testing.
"""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock

# Add project root and service directories to Python path
project_root = Path(__file__).parent.parent
paths_to_add = [
    project_root,
    project_root / "services",
    project_root / "services/shared",
    project_root / "services/core",
    project_root / "services/platform",
    project_root / "integrations",
]

for path in paths_to_add:
    if path.exists():
        path_str = str(path.absolute())
        if path_str not in sys.path:
            sys.path.insert(0, path_str)

# Mock PyTorch to avoid CUDA library issues
try:
    import torch
except ImportError:
    # Create a comprehensive mock for torch
    torch = MagicMock()
    torch.tensor = MagicMock()
    torch.svd = MagicMock()
    torch.zeros = MagicMock()
    torch.ones = MagicMock()
    torch.randn = MagicMock()
    torch.float32 = 'float32'
    torch.device = MagicMock()
    torch.nn = MagicMock()
    torch.nn.Module = MagicMock
    torch.optim = MagicMock()
    sys.modules['torch'] = torch

# Set environment variables for testing
os.environ.setdefault('ENVIRONMENT', 'testing')
os.environ.setdefault('CONSTITUTIONAL_HASH', 'cdd01ef066bc6cf2')
os.environ.setdefault('DATABASE_URL', 'sqlite:///:memory:')
os.environ.setdefault('REDIS_URL', 'redis://localhost:6379/0')

# Import pytest fixtures and configuration
import pytest

# Configure pytest markers
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.performance = pytest.mark.performance
pytest.mark.security = pytest.mark.security
pytest.mark.e2e = pytest.mark.e2e

def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance test"
    )
    config.addinivalue_line(
        "markers", "security: mark test as security test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )

def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers and skip conditions."""
    for item in items:
        # Skip integration tests if services are not running
        if "integration" in item.keywords:
            if not _services_running():
                item.add_marker(
                    pytest.mark.skip(reason="integration test requires running services")
                )

def _services_running():
    """Check if required services are running for integration tests."""
    return os.environ.get('SERVICES_RUNNING', 'false').lower() == 'true'

@pytest.fixture(scope="session")
def constitutional_hash():
    """Provide the constitutional hash for tests."""
    return "cdd01ef066bc6cf2"

@pytest.fixture
def mock_wina_config():
    """Provide a mock WINA configuration for testing."""
    return MagicMock()
