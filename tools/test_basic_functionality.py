#!/usr/bin/env python3
"""
Basic functionality test to verify test infrastructure is working.
"""

import sys
from pathlib import Path

import pytest


def test_python_environment():
    """Test that Python environment is working correctly."""
    assert sys.version_info >= (3, 8), "Python 3.8+ required"
    assert pytest is not None, "Pytest should be available"


def test_project_structure():
    """Test that basic project structure exists."""
    project_root = Path()

    # Check for key directories
    assert (project_root / "tests").exists(), "Tests directory should exist"
    assert (project_root / "services").exists(), "Services directory should exist"
    assert (project_root / "blockchain").exists(), "Blockchain directory should exist"

    # Check for key files
    assert (project_root / "pytest.ini").exists(), "pytest.ini should exist"
    assert (
        project_root / "requirements-test.txt"
    ).exists(), "requirements-test.txt should exist"


def test_imports():
    """Test that basic imports work."""
    # Test standard library imports
    import asyncio
    import datetime
    import json

    import httpx
    import pydantic

    # Test installed packages
    import pytest

    assert json is not None
    assert asyncio is not None
    assert datetime is not None
    assert pytest is not None
    assert httpx is not None
    assert pydantic is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
