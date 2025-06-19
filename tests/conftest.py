"""
Pytest configuration for ACGS-1 test suite.
Sets up Python path and imports for services with hyphened directory names.
"""

import sys
from pathlib import Path

# Add project root and service directories to Python path
project_root = Path(__file__).parent
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

# Import pytest fixtures and configuration
import pytest

# Configure pytest markers
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration  
pytest.mark.performance = pytest.mark.performance
pytest.mark.security = pytest.mark.security
pytest.mark.e2e = pytest.mark.e2e
