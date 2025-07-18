#!/usr/bin/env python3
"""
Constitutional Hash Addition Script
Adds constitutional hash to all configuration files missing it
Constitutional Hash: cdd01ef066bc6cf2
"""

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Set

import yaml


def add_hash_to_yaml_file(file_path: str) -> bool:
    """Add constitutional hash to YAML file"""
    try:
        with open(file_path, "r") as f:
            content = f.read()

        # Check if hash already exists
        if "cdd01ef066bc6cf2" in content:
            return False

        # Add hash comment at the top
        lines = content.split("\n")

        # Find first non-comment, non-empty line
        insert_index = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                insert_index = i
                break

        # Insert constitutional hash comment
        hash_comment = "# Constitutional Hash: cdd01ef066bc6cf2"
        lines.insert(insert_index, hash_comment)

        new_content = "\n".join(lines)

        with open(file_path, "w") as f:
            f.write(new_content)

        return True

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def add_hash_to_json_file(file_path: str) -> bool:
    """Add constitutional hash to JSON file"""
    try:
        with open(file_path, "r") as f:
            content = f.read()

        # Check if hash already exists
        if "cdd01ef066bc6cf2" in content:
            return False

        try:
            data = json.loads(content)

            # Add constitutional hash to metadata
            if isinstance(data, dict):
                data["_constitutional_hash"] = "cdd01ef066bc6cf2"

                # Write back with proper formatting
                with open(file_path, "w") as f:
                    json.dump(data, f, indent=2)
                return True

        except json.JSONDecodeError:
            # If JSON is invalid, add as comment at top
            lines = content.split("\n")
            hash_comment = "// Constitutional Hash: cdd01ef066bc6cf2"
            lines.insert(0, hash_comment)

            with open(file_path, "w") as f:
                f.write("\n".join(lines))
            return True

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def add_hash_to_config_file(file_path: str) -> bool:
    """Add constitutional hash to configuration file"""
    try:
        with open(file_path, "r") as f:
            content = f.read()

        # Check if hash already exists
        if "cdd01ef066bc6cf2" in content:
            return False

        # Add hash comment at the top
        lines = content.split("\n")
        hash_comment = "# Constitutional Hash: cdd01ef066bc6cf2"
        lines.insert(0, hash_comment)

        new_content = "\n".join(lines)

        with open(file_path, "w") as f:
            f.write(new_content)

        return True

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def find_config_files(repo_root: Path) -> List[Path]:
    """Find all configuration files that might need constitutional hash"""
    config_extensions = {
        ".yml",
        ".yaml",  # YAML files
        ".json",  # JSON files
        ".toml",  # TOML files
        ".ini",  # INI files
        ".conf",  # Config files
        ".cfg",  # Config files
        ".config",  # Config files
        ".properties",  # Properties files
        "config/environments/development.env",  # Environment files
        ".dockerignore",  # Docker files
        "Dockerfile",  # Docker files
        "docker-compose.yml",  # Docker compose
        "docker-compose.yaml",  # Docker compose
    }

    config_files = []

    # Search for configuration files
    for root, dirs, files in os.walk(repo_root):
        # Skip certain directories
        skip_dirs = {
            ".git",
            "__pycache__",
            ".pytest_cache",
            "node_modules",
            ".venv",
            "venv",
        }
        dirs[:] = [d for d in dirs if d not in skip_dirs]

        for file in files:
            file_path = Path(root) / file

            # Check by extension
            if file_path.suffix.lower() in config_extensions:
                config_files.append(file_path)
            # Check by filename
            elif file in [
                "Dockerfile",
                ".dockerignore",
                "docker-compose.yml",
                "docker-compose.yaml",
            ]:
                config_files.append(file_path)
            # Check for compose files
            elif "docker-compose" in file and (
                file.endswith(".yml") or file.endswith(".yaml")
            ):
                config_files.append(file_path)
            # Check for config in name
            elif "config" in file.lower() and not file.endswith(".py"):
                config_files.append(file_path)

    return sorted(config_files)


def main():
    """Main function to add constitutional hash to configuration files"""
    repo_root = Path("/home/dislove/ACGS-2")

    print("🔧 Constitutional Hash Addition for Configuration Files")
    print("📋 Constitutional Hash: cdd01ef066bc6cf2")
    print()

    # Find all configuration files
    config_files = find_config_files(repo_root)
    print(f"Found {len(config_files)} configuration files")

    updated_count = 0
    skipped_count = 0
    error_count = 0

    for file_path in config_files:
        try:
            relative_path = file_path.relative_to(repo_root)
            print(f"Processing: {relative_path}")

            updated = False

            if file_path.suffix.lower() in [".yml", ".yaml"]:
                updated = add_hash_to_yaml_file(str(file_path))
            elif file_path.suffix.lower() == ".json":
                updated = add_hash_to_json_file(str(file_path))
            else:
                updated = add_hash_to_config_file(str(file_path))

            if updated:
                updated_count += 1
                print(f"  ✅ Added constitutional hash")
            else:
                skipped_count += 1
                print(f"  ⏭️  Skipped (hash already present)")

        except Exception as e:
            error_count += 1
            print(f"  ❌ Error: {e}")

    print(f"\n🎯 Constitutional Hash Addition Summary:")
    print("=" * 50)
    print(f"Total files processed: {len(config_files)}")
    print(f"Files updated: {updated_count}")
    print(f"Files skipped: {skipped_count}")
    print(f"Files with errors: {error_count}")
    print(f"\n✅ Constitutional hash addition completed!")
    print(f"📋 Constitutional Hash: cdd01ef066bc6cf2")


if __name__ == "__main__":
    main()
