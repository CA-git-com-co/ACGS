#!/usr/bin/env python3
"""
ACGS Volume Mount Directory Creator

Reads the catalogue from step 1 (volume_mount_triage.yaml) and creates missing host directories.
For each "missing host directory" path, creates it (with mkdir -p) and drops a .keep file
containing constitutional hash cdd01ef066bc6cf2.

Constitutional hash: cdd01ef066bc6cf2
"""

import argparse
import os
import sys
from pathlib import Path

import yaml

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


def read_yaml_catalogue(file_path):
    """
    Read the YAML catalogue file from step 1.

    Args:
        file_path (str): Path to the volume_mount_triage.yaml file

    Returns:
        dict: Parsed YAML content

    Raises:
        FileNotFoundError: If catalogue file doesn't exist
        yaml.YAMLError: If file is not valid YAML
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Catalogue file not found: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            catalogue = yaml.safe_load(file)
        return catalogue
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Error parsing YAML file: {e}")


def create_missing_directories(catalogue, base_path=".", dry_run=False):
    """
    Create missing host directories from the catalogue.

    Args:
        catalogue (dict): Parsed catalogue data
        base_path (str): Base directory path (default: current directory)
        dry_run (bool): If True, only print what would be created

    Returns:
        list: List of directories that were (or would be) created
    """
    created_dirs = []
    missing_dirs = catalogue.get("broken_volume_mounts_by_compose_file", {})

    for compose_file, details in missing_dirs.items():
        host_dirs = details.get("missing_host_directory", [])

        for entry in host_dirs:
            host_path = entry.get("host_path", "")
            if not host_path:
                continue

            full_path = os.path.join(base_path, host_path)
            keep_file_path = os.path.join(full_path, ".keep")

            if dry_run:
                print(f"[DRY RUN] Would create directory: {full_path}")
                print(f"[DRY RUN] Would create .keep file: {keep_file_path}")
            else:
                # Create directory with mkdir -p equivalent
                os.makedirs(full_path, exist_ok=True)

                # Create .keep file with constitutional hash
                with open(keep_file_path, "w", encoding="utf-8") as keep_file:
                    keep_file.write(CONSTITUTIONAL_HASH)

                print(f"Created directory: {full_path}")
                print(f"Created .keep file: {keep_file_path}")

            created_dirs.append(full_path)

    return created_dirs


def main():
    """
    Main function to handle command line arguments and execute the script.
    """
    parser = argparse.ArgumentParser(
        description="Create missing host directories from ACGS volume mount catalogue"
    )

    parser.add_argument(
        "--catalogue",
        "-c",
        default="volume_mount_triage.yaml",
        help="Path to the volume mount catalogue file (default: volume_mount_triage.yaml)",
    )

    parser.add_argument(
        "--base-path",
        "-b",
        default=".",
        help="Base directory path (default: current directory)",
    )

    parser.add_argument(
        "--dry-run",
        "-d",
        action="store_true",
        help="Dry run mode - only show what would be created",
    )

    args = parser.parse_args()

    try:
        # Read the catalogue
        catalogue_data = read_yaml_catalogue(args.catalogue)

        # Create missing directories
        created_dirs = create_missing_directories(
            catalogue_data, args.base_path, args.dry_run
        )

        if args.dry_run:
            print(f"\n[DRY RUN] Would create {len(created_dirs)} directories")
        else:
            print(f"\nSuccessfully created {len(created_dirs)} directories")
            print(f"Constitutional hash used: {CONSTITUTIONAL_HASH}")

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
