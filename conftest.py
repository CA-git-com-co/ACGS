"""
Pytest configuration for ACGS-1 test suite.
Sets up Python path and imports for services with hyphened directory names.
"""

import os
import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv

# Load test environment variables
test_env_path = Path(__file__).parent / "config" / "test.env"
if test_env_path.exists():
    load_dotenv(test_env_path)

# Set testing environment variables
os.environ["ENVIRONMENT"] = "testing"
os.environ["PYTEST_CURRENT_TEST"] = "true"

# Add project root and service directories to Python path
project_root = Path(__file__).parent
paths_to_add = [
    project_root,
    project_root / "services",
    project_root / "services/shared",
    project_root / "services/core",
    project_root / "services/platform",
    project_root / "integrations",
    project_root / "scripts",
    project_root / "tools",
]

for path in paths_to_add:
    if path.exists():
        path_str = str(path.absolute())
        if path_str not in sys.path:
            sys.path.insert(0, path_str)
