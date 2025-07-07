#!/usr/bin/env python3
"""
Unit tests for create_missing_dirs.py

Tests the functionality of creating missing host directories based on catalogue data.
Constitutional hash: cdd01ef066bc6cf2
"""

import os
import shutil
import sys
import tempfile
from pathlib import Path

import pytest
import yaml

# Import the module directly
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
script_path = os.path.join(project_root, "scripts", "create_missing_dirs.py")

# Import module from file
import importlib.util

spec = importlib.util.spec_from_file_location("create_missing_dirs", script_path)
create_missing_dirs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(create_missing_dirs)

# Import functions and constants
create_missing_directories = create_missing_dirs.create_missing_directories
read_yaml_catalogue = create_missing_dirs.read_yaml_catalogue
CONSTITUTIONAL_HASH = create_missing_dirs.CONSTITUTIONAL_HASH


class TestCreateMissingDirs:
    """Test suite for create_missing_dirs.py"""

    @pytest.fixture
    def sample_catalogue_data(self):
        """Sample catalogue data for testing"""
        return {
            "broken_volume_mounts_by_compose_file": {
                "infrastructure/docker/docker-compose.acgs.yml": {
                    "missing_host_directory": [
                        {
                            "container_path": "/app/config",
                            "full_mount": "config:/app/config:ro",
                            "host_path": "config",
                            "mount_options": "ro",
                            "recommended_action": "Create directory: config",
                        },
                        {
                            "container_path": "/app/reports",
                            "full_mount": "reports:/app/reports",
                            "host_path": "reports",
                            "mount_options": "",
                            "recommended_action": "Create directory: reports",
                        },
                        {
                            "container_path": "/app/logs",
                            "full_mount": "infrastructure/docker/logs/agent-hitl:/app/logs",
                            "host_path": "infrastructure/docker/logs/agent-hitl",
                            "mount_options": "",
                            "recommended_action": "Create directory: infrastructure/docker/logs/agent-hitl",
                        },
                    ]
                },
                "infrastructure/docker/docker-compose-test.yml": {
                    "missing_host_directory": [
                        {
                            "container_path": "/app/shared",
                            "full_mount": "infrastructure/docker/services/shared:/app/shared",
                            "host_path": "infrastructure/docker/services/shared",
                            "mount_options": "",
                            "recommended_action": "Create directory: infrastructure/docker/services/shared",
                        }
                    ]
                },
            }
        }

    @pytest.fixture
    def catalogue_file(self, tmp_path, sample_catalogue_data):
        """Create a temporary catalogue file for testing"""
        catalogue_file = tmp_path / "volume_mount_triage.yaml"
        with open(catalogue_file, "w", encoding="utf-8") as f:
            yaml.dump(sample_catalogue_data, f)
        return catalogue_file

    @pytest.fixture
    def test_base_dir(self, tmp_path):
        """Create a temporary base directory for testing"""
        return tmp_path

    def test_read_yaml_catalogue_success(self, catalogue_file, sample_catalogue_data):
        """Test successful reading of catalogue file"""
        result = read_yaml_catalogue(str(catalogue_file))
        assert result == sample_catalogue_data

    def test_read_yaml_catalogue_file_not_found(self):
        """Test handling of non-existent catalogue file"""
        with pytest.raises(FileNotFoundError):
            read_yaml_catalogue("non_existent_file.yaml")

    def test_read_yaml_catalogue_invalid_yaml(self, tmp_path):
        """Test handling of invalid YAML file"""
        invalid_yaml_file = tmp_path / "invalid.yaml"
        with open(invalid_yaml_file, "w") as f:
            f.write("invalid: yaml: content: [unclosed")

        with pytest.raises(yaml.YAMLError):
            read_yaml_catalogue(str(invalid_yaml_file))

    def test_create_missing_directories_success(
        self, sample_catalogue_data, test_base_dir
    ):
        """Test successful creation of missing directories"""
        created_dirs = create_missing_directories(
            sample_catalogue_data, base_path=str(test_base_dir), dry_run=False
        )

        expected_paths = [
            "config",
            "reports",
            "infrastructure/docker/logs/agent-hitl",
            "infrastructure/docker/services/shared",
        ]

        # Check that all expected directories were created
        for expected_path in expected_paths:
            full_path = os.path.join(str(test_base_dir), expected_path)
            assert full_path in created_dirs
            assert os.path.exists(full_path)
            assert os.path.isdir(full_path)

            # Check that .keep file exists and contains constitutional hash
            keep_file_path = os.path.join(full_path, ".keep")
            assert os.path.exists(keep_file_path)
            assert os.path.isfile(keep_file_path)

            with open(keep_file_path, "r") as f:
                assert f.read() == CONSTITUTIONAL_HASH

        assert len(created_dirs) == 4

    def test_create_missing_directories_dry_run(
        self, sample_catalogue_data, test_base_dir, capsys
    ):
        """Test dry run mode doesn't create directories"""
        created_dirs = create_missing_directories(
            sample_catalogue_data, base_path=str(test_base_dir), dry_run=True
        )

        # Check that directories are listed but not actually created
        expected_paths = [
            "config",
            "reports",
            "infrastructure/docker/logs/agent-hitl",
            "infrastructure/docker/services/shared",
        ]

        for expected_path in expected_paths:
            full_path = os.path.join(str(test_base_dir), expected_path)
            assert full_path in created_dirs
            # Directory should NOT exist in dry run mode
            assert not os.path.exists(full_path)

        # Check console output
        captured = capsys.readouterr()
        assert "[DRY RUN] Would create directory:" in captured.out
        assert "[DRY RUN] Would create .keep file:" in captured.out

    def test_create_missing_directories_empty_catalogue(self, test_base_dir):
        """Test handling of empty catalogue"""
        empty_catalogue = {"broken_volume_mounts_by_compose_file": {}}

        created_dirs = create_missing_directories(
            empty_catalogue, base_path=str(test_base_dir), dry_run=False
        )

        assert created_dirs == []

    def test_create_missing_directories_missing_host_path(self, test_base_dir):
        """Test handling of missing host_path in catalogue entries"""
        catalogue_with_missing_path = {
            "broken_volume_mounts_by_compose_file": {
                "test.yml": {
                    "missing_host_directory": [
                        {
                            "container_path": "/app/test",
                            "full_mount": "test:/app/test",
                            # Missing 'host_path' key
                            "mount_options": "",
                            "recommended_action": "Create directory: test",
                        },
                        {
                            "container_path": "/app/valid",
                            "full_mount": "valid:/app/valid",
                            "host_path": "valid",  # This one has host_path
                            "mount_options": "",
                            "recommended_action": "Create directory: valid",
                        },
                    ]
                }
            }
        }

        created_dirs = create_missing_directories(
            catalogue_with_missing_path, base_path=str(test_base_dir), dry_run=False
        )

        # Only the entry with valid host_path should be created
        assert len(created_dirs) == 1
        valid_path = os.path.join(str(test_base_dir), "valid")
        assert valid_path in created_dirs
        assert os.path.exists(valid_path)

    def test_create_missing_directories_already_exists(
        self, sample_catalogue_data, test_base_dir
    ):
        """Test handling of directories that already exist"""
        # Pre-create one of the directories
        existing_dir = os.path.join(str(test_base_dir), "config")
        os.makedirs(existing_dir, exist_ok=True)

        created_dirs = create_missing_directories(
            sample_catalogue_data, base_path=str(test_base_dir), dry_run=False
        )

        # Should still include the pre-existing directory in the list
        assert existing_dir in created_dirs
        assert os.path.exists(existing_dir)

        # .keep file should still be created
        keep_file_path = os.path.join(existing_dir, ".keep")
        assert os.path.exists(keep_file_path)

        with open(keep_file_path, "r") as f:
            assert f.read() == CONSTITUTIONAL_HASH

    def test_constitutional_hash_constant(self):
        """Test that the constitutional hash constant is correct"""
        assert CONSTITUTIONAL_HASH == "cdd01ef066bc6cf2"
        assert len(CONSTITUTIONAL_HASH) == 16  # Verify length
        assert CONSTITUTIONAL_HASH.isalnum()  # Verify alphanumeric


if __name__ == "__main__":
    pytest.main([__file__])
