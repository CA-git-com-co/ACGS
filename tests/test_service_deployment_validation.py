# Constitutional Hash: cdd01ef066bc6cf2

import asyncio
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add the root directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Mock the docker module
sys.modules["docker"] = Mock()
sys.modules["aiohttp"] = Mock()

from scripts.service_deployment_validation import DEFAULT_EXCLUDE, ACGSServiceValidator


@pytest.fixture
def setup_fake_venv(tmp_path) -> Path:
    """Creates a fake .venv structure with a file to test exclusion."""
    venv_path = tmp_path / ".venv" / "lib"
    venv_path.mkdir(parents=True, exist_ok=True)
    fake_file = venv_path / "foo.py"
    fake_file.write_text("print('This should be excluded')")
    return tmp_path


@pytest.mark.asyncio
@patch("scripts.service_deployment_validation.docker")
async def test_venv_exclusion(mock_docker, setup_fake_venv):
    """Test that .venv files are excluded from compliance scanning."""
    mock_docker.from_env.return_value = Mock()
    validator = ACGSServiceValidator()
    # Perform repo scan
    scan_results = validator.scan_repo_for_compliance(setup_fake_venv)

    # Verify that the .venv file was excluded
    assert scan_results["excluded_files"] == 1
    assert any(".venv" in path for path in scan_results["excluded_paths"])

    # Verify that the .venv file is not in the non-compliant list
    # (since it was excluded, it shouldn't be checked for compliance)
    venv_files_in_non_compliant = [
        path for path in scan_results["non_compliant_files"] if ".venv" in path
    ]
    assert (
        len(venv_files_in_non_compliant) == 0
    ), "Files in .venv should be excluded, not marked as non-compliant"


@patch("scripts.service_deployment_validation.docker")
def test_extra_exclude_functionality(mock_docker, tmp_path):
    """Test that extra exclude patterns work correctly."""
    mock_docker.from_env.return_value = Mock()

    # Create a custom directory to exclude
    custom_dir = tmp_path / "custom_exclude"
    custom_dir.mkdir()
    custom_file = custom_dir / "test.py"
    custom_file.write_text("print('This should also be excluded')")

    # Create validator with extra exclude pattern
    extra_exclude = {"custom_exclude"}
    validator = ACGSServiceValidator(extra_exclude=extra_exclude)

    # Perform repo scan
    scan_results = validator.scan_repo_for_compliance(tmp_path)

    # Verify the custom pattern is in exclude patterns
    assert "custom_exclude" in validator.exclude_patterns

    # Verify that the custom file was excluded
    assert scan_results["excluded_files"] == 1
    assert any("custom_exclude" in path for path in scan_results["excluded_paths"])

    # Verify that the custom file is not in the non-compliant list
    custom_files_in_non_compliant = [
        path for path in scan_results["non_compliant_files"] if "custom_exclude" in path
    ]
    assert (
        len(custom_files_in_non_compliant) == 0
    ), "Files in custom_exclude should be excluded"
