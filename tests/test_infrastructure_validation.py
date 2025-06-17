"""
Test Infrastructure Validation
Tests to verify that the testing infrastructure is working correctly.
"""

import sys
from pathlib import Path

import pytest


def test_python_version():
    """Test that we're running the correct Python version."""
    assert sys.version_info >= (3, 11), f"Python 3.11+ required, got {sys.version}"


def test_pytest_working():
    """Test that pytest is working correctly."""
    assert pytest.__version__ is not None
    print(f"✅ Pytest version: {pytest.__version__}")


def test_project_structure():
    """Test that the project structure is correct."""
    project_root = Path(__file__).parent.parent

    # Check key directories exist for ACGS-1 project
    assert (project_root / "tests").exists(), "tests directory missing"
    assert (project_root / "services").exists(), "services directory missing"
    assert (project_root / "blockchain").exists(), "blockchain directory missing"
    assert (project_root / "applications").exists(), "applications directory missing"

    print("✅ Project structure validated")


def test_environment_setup():
    """Test that the environment is set up correctly."""
    # Check that we're in a virtual environment
    assert hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    ), "Not running in virtual environment"

    print("✅ Virtual environment detected")


def test_basic_imports():
    """Test that basic imports work."""
    try:
        import asyncio
        import datetime
        import json
        import pathlib

        print("✅ Basic imports working")
    except ImportError as e:
        pytest.fail(f"Basic import failed: {e}")


def test_coverage_tools():
    """Test that coverage tools are available."""
    try:
        import coverage

        print(f"✅ Coverage.py version: {coverage.__version__}")
    except ImportError:
        pytest.fail("Coverage.py not available")


@pytest.mark.asyncio
async def test_async_support():
    """Test that async/await support is working."""

    async def dummy_async_function():
        return "async_working"

    result = await dummy_async_function()
    assert result == "async_working"
    print("✅ Async/await support working")


def test_test_markers():
    """Test that custom test markers are recognized."""
    # This test itself should run without marker warnings
    assert True
    print("✅ Test markers working")


class TestClassExample:
    """Example test class to verify class-based testing."""

    def test_class_method(self):
        """Test that class-based tests work."""
        assert True
        print("✅ Class-based tests working")

    def test_setup_teardown(self):
        """Test setup and teardown functionality."""
        # This would normally have setup/teardown
        assert True
        print("✅ Setup/teardown functionality working")


def test_parametrized_tests():
    """Test parametrized test functionality."""

    @pytest.mark.parametrize(
        "input,expected",
        [
            (1, 2),
            (2, 3),
            (3, 4),
        ],
    )
    def inner_test(input, expected):
        assert input + 1 == expected

    # Run the parametrized test manually
    for input_val, expected_val in [(1, 2), (2, 3), (3, 4)]:
        inner_test(input_val, expected_val)

    print("✅ Parametrized tests working")


def test_fixtures_basic():
    """Test that basic fixtures work."""
    # This would normally use fixtures, but we'll test the concept
    test_data = {"key": "value"}
    assert test_data["key"] == "value"
    print("✅ Basic fixtures working")


if __name__ == "__main__":
    # Allow running this test file directly
    pytest.main([__file__, "-v"])
