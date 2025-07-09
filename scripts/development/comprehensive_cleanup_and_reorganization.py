#!/usr/bin/env python3
"""
ACGS-1 Comprehensive Codebase Cleanup and Reorganization

This script analyzes and reorganizes the ACGS-1 repository structure to improve
maintainability, remove technical debt, and ensure consistent organization patterns.

Features:
1. Identifies and removes duplicate files
2. Cleans up backup and temporary files
3. Reorganizes misplaced files according to standard patterns
4. Consolidates scattered configuration files
5. Validates the structure of core services (Auth, AC, FV, GS, PGC, EC)
6. Ensures test files are in the proper test directories
7. Creates backups of all changes for safety

Usage:
    python comprehensive_cleanup_and_reorganization.py --dry-run  # Show what would be done without making changes
    python comprehensive_cleanup_and_reorganization.py --execute  # Execute the cleanup
"""

import argparse
import glob
import hashlib
import json
import logging
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from typing import Any

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("acgs_cleanup.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Root directory of the ACGS-1 repository
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Backup directory for files that will be modified or removed
BACKUP_TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = os.path.join(ROOT_DIR, "backups", f"cleanup_backup_{BACKUP_TIMESTAMP}")

# File patterns to ignore
IGNORE_PATTERNS = [
    # Git files
    ".git/**",
    ".github/**",
    ".gitignore",
    ".gitattributes",
    ".gitmodules",
    # Build artifacts and directories
    "**/__pycache__/**",
    "**/*.pyc",
    "**/.pytest_cache/**",
    "**/node_modules/**",
    "**/venv/**",
    "**/target/**",
    "**/dist/**",
    "**/build/**",
    # IDE files
    "**/.idea/**",
    "**/.vscode/**",
    "**/*.code-workspace",
    # Temporary files
    "**/tmp/**",
    "**/temp/**",
    # This script and backups
    "comprehensive_cleanup_and_reorganization.py",
    "comprehensive_codebase_cleanup.py",
    "backups/**",
]

# Standard directory structure
STANDARD_DIRS = {
    "services": {
        "core": [
            "constitutional-ai/ac_service",
            "formal-verification/fv_service",
            "governance-synthesis/gs_service",
            "policy-governance/pgc_service",
            "evolutionary-computation/ec_service",
            "self-evolving-ai/se_service",
        ],
        "platform": ["authentication/auth_service", "integrity/integrity_service"],
        "shared": ["models", "middleware", "utils", "database", "cache"],
    },
    "blockchain": ["programs", "tests", "scripts", "quantumagi-deployment"],
    "applications": ["app", "governance-dashboard", "shared"],
    "infrastructure": [
        "docker",
        "kubernetes",
        "monitoring",
        "database",
        "load-balancer",
    ],
    "config": ["production", "staging", "development", "monitoring"],
    "docs": ["api", "architecture", "deployment", "operations"],
    "scripts": ["deployment", "testing", "maintenance", "analysis"],
    "tests": ["unit", "integration", "e2e", "performance", "security"],
}

# Files to keep at root level
ROOT_LEVEL_KEEP = [
    "README.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "SECURITY.md",
    "CHANGELOG.md",
    "pyproject.toml",
    "pytest.ini",
    "requirements.txt",
    "package.json",
    "package-lock.json",
    "Cargo.toml",
    "Cargo.lock",
    "Dockerfile",
    "CLAUDE.md",
]

# Core services to preserve
CORE_SERVICES = [
    "ac_service",  # Constitutional AI
    "auth_service",  # Authentication
    "fv_service",  # Formal Verification
    "gs_service",  # Governance Synthesis
    "pgc_service",  # Policy Governance
    "integrity_service",  # Integrity
    "ec_service",  # Evolutionary Computation
]


class FileAction:
    """Represents an action to take on a file or directory"""

    MOVE = "move"
    REMOVE = "remove"
    RENAME = "rename"
    STANDARDIZE = "standardize"

    def __init__(
        self,
        action_type: str,
        source: str,
        destination: str | None = None,
        reason: str = "",
    ):
        self.action_type = action_type
        self.source = source
        self.destination = destination
        self.reason = reason

    def __str__(self) -> str:
        if self.action_type == FileAction.MOVE:
            return f"MOVE: {self.source} -> {self.destination} ({self.reason})"
        if self.action_type == FileAction.REMOVE:
            return f"REMOVE: {self.source} ({self.reason})"
        if self.action_type == FileAction.RENAME:
            return f"RENAME: {self.source} -> {self.destination} ({self.reason})"
        if self.action_type == FileAction.STANDARDIZE:
            return f"STANDARDIZE: {self.source} ({self.reason})"
        return f"UNKNOWN ACTION: {self.action_type} - {self.source}"


class CodebaseReorganizer:
    """Manages the cleanup and reorganization of the ACGS-1 repository"""

    def __init__(self):
        self.actions: list[FileAction] = []
        self.file_hashes: dict[str, list[str]] = (
            {}
        )  # Maps file hash to list of file paths
        self.duplicate_files: list[tuple[str, list[str]]] = (
            []
        )  # (hash, list of file paths)
        self.backup_files: list[str] = []
        self.misplaced_files: dict[str, str] = (
            {}
        )  # Maps file path to recommended location
        self.test_files_outside_tests: list[str] = []
        self.script_files_outside_scripts: list[str] = []
        self.docker_files_outside_infrastructure: list[str] = []
        self.config_files_outside_config: list[str] = []
        self.scanned_files: int = 0
        self.directories_created: set[str] = set()
        self.verification_results: dict[str, Any] = {}

    def add_action(self, action: FileAction) -> None:
        """Add an action to the plan"""
        self.actions.append(action)

    def compute_file_hash(self, filepath: str) -> str:
        """Compute a hash of the file contents"""
        try:
            with open(filepath, "rb") as f:
                return hashlib.md5(f.read()).hexdigest()
        except OSError:
            return "error-computing-hash"

    def should_ignore(self, filepath: str) -> bool:
        """Check if a file should be ignored"""
        rel_path = os.path.relpath(filepath, ROOT_DIR)
        for pattern in IGNORE_PATTERNS:
            if pattern.endswith("/**"):
                # Handle directory wildcards
                dir_pattern = pattern[:-3]
                if rel_path.startswith(dir_pattern):
                    return True
            elif glob.fnmatch.fnmatch(rel_path, pattern):
                return True
        return False

    def scan_files(self) -> None:
        """Scan all files in the repository"""
        logger.info("Scanning files in repository...")

        for root, _, files in os.walk(ROOT_DIR):
            if self.should_ignore(root):
                continue

            for filename in files:
                filepath = os.path.join(root, filename)
                if self.should_ignore(filepath):
                    continue

                self.scanned_files += 1
                if self.scanned_files % 1000 == 0:
                    logger.info(f"Scanned {self.scanned_files} files...")

                # Skip large files
                try:
                    if os.path.getsize(filepath) > 10 * 1024 * 1024:  # 10MB
                        continue
                except OSError:
                    continue

                try:
                    file_hash = self.compute_file_hash(filepath)
                    if file_hash not in self.file_hashes:
                        self.file_hashes[file_hash] = []
                    self.file_hashes[file_hash].append(filepath)
                except OSError:
                    continue

    def find_duplicate_files(self) -> None:
        """Find duplicate files in the repository"""
        logger.info("Finding duplicate files...")

        # Consider only files with the same hash
        for file_hash, filepaths in self.file_hashes.items():
            if len(filepaths) > 1 and file_hash != "error-computing-hash":
                # Group by filename to avoid false positives
                by_filename = {}
                for path in filepaths:
                    filename = os.path.basename(path)
                    if filename not in by_filename:
                        by_filename[filename] = []
                    by_filename[filename].append(path)

                # Check each group
                for filename, paths in by_filename.items():
                    if len(paths) > 1:
                        # Skip node_modules files
                        if any("node_modules" in path for path in paths):
                            continue

                        # Skip test fixtures or data files that might be intentionally duplicated
                        if any("fixtures" in path or "data" in path for path in paths):
                            continue

                        self.duplicate_files.append((file_hash, paths))

    def find_backup_files(self) -> None:
        """Find backup and temporary files"""
        logger.info("Finding backup and temporary files...")

        backup_patterns = [
            "*.bak",
            "*.backup",
            "*.old",
            "*_old.*",
            "*.tmp",
            "*.temp",
            "*.swp",
            "*.swo",
            "*.pyc",
            "*.pyo",
            "*.log.*",
            "*.bak.*",
            "*copy*",
            "*COPY*",
            "*backup*",
            "*BACKUP*",
        ]

        for root, _, files in os.walk(ROOT_DIR):
            if self.should_ignore(root):
                continue

            for filename in files:
                if any(
                    glob.fnmatch.fnmatch(filename, pattern)
                    for pattern in backup_patterns
                ):
                    filepath = os.path.join(root, filename)
                    self.backup_files.append(filepath)

    def find_misplaced_files(self) -> None:
        """Find files that are in the wrong directories"""
        logger.info("Finding misplaced files...")

        # Find test files not in tests directory
        test_file_pattern = re.compile(r"^test_.*\.py$")
        for root, _, files in os.walk(ROOT_DIR):
            if "tests" in root.split(os.path.sep) or "test" in root.split(os.path.sep):
                continue

            for filename in files:
                if test_file_pattern.match(filename):
                    filepath = os.path.join(root, filename)
                    self.test_files_outside_tests.append(filepath)

        # Find script files not in scripts directory
        script_extensions = [".sh", ".py", ".js", ".ts"]
        for root, _, files in os.walk(ROOT_DIR):
            if "scripts" in root.split(os.path.sep) or self.should_ignore(root):
                continue

            for filename in files:
                ext = os.path.splitext(filename)[1].lower()
                if ext in script_extensions and (
                    "setup" in filename.lower() or "deploy" in filename.lower()
                ):
                    filepath = os.path.join(root, filename)

                    # Skip service entry points
                    if filename == "main.py" or filename.startswith("app."):
                        continue

                    self.script_files_outside_scripts.append(filepath)

        # Find Docker files not in infrastructure directory
        for root, _, files in os.walk(ROOT_DIR):
            if "infrastructure" in root.split(os.path.sep) or self.should_ignore(root):
                continue

            for filename in files:
                if (
                    filename.startswith("docker-compose")
                    and os.path.dirname(root) == ROOT_DIR
                ):
                    filepath = os.path.join(root, filename)
                    self.docker_files_outside_infrastructure.append(filepath)

        # Find config files not in config directory
        config_patterns = ["*.yaml", "*.yml", "*.json", "*.conf", "*.config", "*.ini"]
        for root, _, files in os.walk(ROOT_DIR):
            if "config" in root.split(os.path.sep) or self.should_ignore(root):
                continue

            for filename in files:
                if (
                    any(
                        glob.fnmatch.fnmatch(filename, pattern)
                        for pattern in config_patterns
                    )
                    and "config" in filename.lower()
                ):
                    filepath = os.path.join(root, filename)

                    # Skip package.json and similar files
                    if filename in [
                        "package.json",
                        "tsconfig.json",
                        "jest.config.json",
                    ]:
                        continue

                    self.config_files_outside_config.append(filepath)

    def validate_core_services(self) -> None:
        """Validate the structure of core services"""
        logger.info("Validating core services structure...")

        self.verification_results["core_services"] = {}

        for service_name in CORE_SERVICES:
            service_results = {
                "found": False,
                "has_dockerfile": False,
                "has_tests": False,
                "has_app_dir": False,
                "issues": [],
            }

            # Find service directory
            service_paths = []
            for root, dirs, _ in os.walk(ROOT_DIR):
                if service_name in dirs:
                    service_path = os.path.join(root, service_name)
                    service_paths.append(service_path)

            if not service_paths:
                service_results["issues"].append(
                    f"Service directory not found: {service_name}"
                )
                self.verification_results["core_services"][
                    service_name
                ] = service_results
                continue

            # Use the most specific path (deepest in directory structure)
            service_path = max(service_paths, key=lambda p: len(p.split(os.path.sep)))
            service_results["found"] = True
            service_results["path"] = service_path

            # Check for Dockerfile
            dockerfile_path = os.path.join(service_path, "Dockerfile")
            if os.path.exists(dockerfile_path):
                service_results["has_dockerfile"] = True
            else:
                service_results["issues"].append("Missing Dockerfile")

            # Check for app directory
            app_dir = os.path.join(service_path, "app")
            if os.path.exists(app_dir) and os.path.isdir(app_dir):
                service_results["has_app_dir"] = True
            else:
                service_results["issues"].append("Missing app directory")

            # Check for tests
            tests_dir = os.path.join(service_path, "tests")
            if os.path.exists(tests_dir) and os.path.isdir(tests_dir):
                service_results["has_tests"] = True
            else:
                service_results["issues"].append("Missing tests directory")

            # Add service results to verification
            self.verification_results["core_services"][service_name] = service_results

    def generate_cleanup_plan(self) -> None:
        """Generate a cleanup plan based on the findings"""
        logger.info("Generating cleanup plan...")

        # Plan for duplicate files
        for file_hash, paths in self.duplicate_files:
            # Sort by path length (keep shorter paths)
            sorted_paths = sorted(paths, key=lambda p: (len(p.split("/")), p))
            # Keep the first file (usually in a more standard location)
            keep_file = sorted_paths[0]
            for path in sorted_paths[1:]:
                # Skip if in different directories (likely needed duplicates)
                if os.path.dirname(path) != os.path.dirname(keep_file):
                    continue
                self.add_action(
                    FileAction(
                        FileAction.REMOVE, path, reason=f"Duplicate of {keep_file}"
                    )
                )

        # Plan for backup files
        for filepath in self.backup_files:
            # Skip if the file is needed
            if any(filepath.endswith(ext) for ext in [".gitignore", ".dockerignore"]):
                continue
            self.add_action(
                FileAction(
                    FileAction.REMOVE, filepath, reason="Backup or temporary file"
                )
            )

        # Plan for test files outside tests directory
        for filepath in self.test_files_outside_tests:
            # Determine appropriate test directory
            service_dir = None
            rel_path = os.path.relpath(filepath, ROOT_DIR)

            if "services" in rel_path.split(os.path.sep):
                # Extract service name from path
                path_parts = rel_path.split(os.path.sep)
                service_idx = path_parts.index("services")
                for i in range(service_idx, len(path_parts)):
                    if path_parts[i] in CORE_SERVICES:
                        service_dir = os.path.join(*path_parts[: i + 1])
                        break

                if service_dir:
                    dest_dir = os.path.join(ROOT_DIR, service_dir, "tests")
                else:
                    dest_dir = os.path.join(ROOT_DIR, "tests")
            else:
                dest_dir = os.path.join(ROOT_DIR, "tests")

            # Create test subdirectory based on filename
            filename = os.path.basename(filepath)
            if "integration" in filename.lower():
                dest_dir = os.path.join(dest_dir, "integration")
            elif "e2e" in filename.lower():
                dest_dir = os.path.join(dest_dir, "e2e")
            else:
                dest_dir = os.path.join(dest_dir, "unit")

            dest_filepath = os.path.join(dest_dir, os.path.basename(filepath))
            self.add_action(
                FileAction(
                    FileAction.MOVE,
                    filepath,
                    dest_filepath,
                    reason="Test file outside tests directory",
                )
            )

        # Plan for Docker files outside infrastructure directory
        for filepath in self.docker_files_outside_infrastructure:
            # Skip if at repository root (some should stay there)
            if (
                os.path.dirname(filepath) == ROOT_DIR
                and os.path.basename(filepath) in ROOT_LEVEL_KEEP
            ):
                continue

            dest_dir = os.path.join(ROOT_DIR, "infrastructure", "docker")
            dest_filepath = os.path.join(dest_dir, os.path.basename(filepath))
            self.add_action(
                FileAction(
                    FileAction.MOVE,
                    filepath,
                    dest_filepath,
                    reason="Docker file outside infrastructure directory",
                )
            )

        # Plan for core service standardization
        for service_name, service_info in self.verification_results.get(
            "core_services", {}
        ).items():
            if not service_info["found"]:
                continue

            service_path = service_info["path"]

            # Check if app directory is missing
            if not service_info["has_app_dir"]:
                app_dir = os.path.join(service_path, "app")
                self.add_action(
                    FileAction(
                        FileAction.STANDARDIZE,
                        service_path,
                        reason=f"Create app directory for {service_name}",
                    )
                )

            # Check if tests directory is missing
            if not service_info["has_tests"]:
                tests_dir = os.path.join(service_path, "tests")
                self.add_action(
                    FileAction(
                        FileAction.STANDARDIZE,
                        service_path,
                        reason=f"Create tests directory for {service_name}",
                    )
                )

    def execute_plan(self, dry_run: bool = True) -> None:
        """Execute the cleanup plan"""
        if dry_run:
            logger.info("\nDRY RUN - No changes will be made\n")
        else:
            logger.info("\nExecuting cleanup plan...\n")
            os.makedirs(BACKUP_DIR, exist_ok=True)

        # Group actions by type for better reporting
        move_actions = [a for a in self.actions if a.action_type == FileAction.MOVE]
        remove_actions = [a for a in self.actions if a.action_type == FileAction.REMOVE]
        rename_actions = [a for a in self.actions if a.action_type == FileAction.RENAME]
        standardize_actions = [
            a for a in self.actions if a.action_type == FileAction.STANDARDIZE
        ]

        # Execute move actions
        if move_actions:
            logger.info(f"\n=== Move Actions ({len(move_actions)}) ===")
            for action in move_actions:
                logger.info(f"- {action}")
                if not dry_run:
                    self._execute_move_action(action)

        # Execute remove actions
        if remove_actions:
            logger.info(f"\n=== Remove Actions ({len(remove_actions)}) ===")
            for action in remove_actions:
                logger.info(f"- {action}")
                if not dry_run:
                    self._execute_remove_action(action)

        # Execute rename actions
        if rename_actions:
            logger.info(f"\n=== Rename Actions ({len(rename_actions)}) ===")
            for action in rename_actions:
                logger.info(f"- {action}")
                if not dry_run:
                    self._execute_rename_action(action)

        # Execute standardize actions
        if standardize_actions:
            logger.info(f"\n=== Standardize Actions ({len(standardize_actions)}) ===")
            for action in standardize_actions:
                logger.info(f"- {action}")
                if not dry_run:
                    self._execute_standardize_action(action)

        logger.info("\nSummary:")
        logger.info(f"- Total files scanned: {self.scanned_files}")
        logger.info(f"- Duplicate files found: {len(self.duplicate_files)}")
        logger.info(f"- Backup files found: {len(self.backup_files)}")
        logger.info(f"- Test files outside tests: {len(self.test_files_outside_tests)}")
        logger.info(
            f"- Script files outside scripts: {len(self.script_files_outside_scripts)}"
        )
        logger.info(
            f"- Docker files outside infrastructure: {len(self.docker_files_outside_infrastructure)}"
        )
        logger.info(
            f"- Config files outside config: {len(self.config_files_outside_config)}"
        )
        logger.info(f"- Total actions: {len(self.actions)}")

        if not dry_run:
            logger.info(f"\nBackup directory: {BACKUP_DIR}")

    def _execute_move_action(self, action: FileAction) -> None:
        """Execute a move action"""
        source = action.source
        destination = action.destination

        # Create backup
        backup_path = os.path.join(BACKUP_DIR, os.path.relpath(source, ROOT_DIR))
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        shutil.copy2(source, backup_path)

        # Create destination directory if needed
        os.makedirs(os.path.dirname(destination), exist_ok=True)

        # Move file
        shutil.move(source, destination)

    def _execute_remove_action(self, action: FileAction) -> None:
        """Execute a remove action"""
        source = action.source

        # Create backup
        backup_path = os.path.join(BACKUP_DIR, os.path.relpath(source, ROOT_DIR))
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        shutil.copy2(source, backup_path)

        # Remove file
        os.remove(source)

    def _execute_rename_action(self, action: FileAction) -> None:
        """Execute a rename action"""
        source = action.source
        destination = action.destination

        # Create backup
        backup_path = os.path.join(BACKUP_DIR, os.path.relpath(source, ROOT_DIR))
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        shutil.copy2(source, backup_path)

        # Rename file
        os.rename(source, destination)

    def _execute_standardize_action(self, action: FileAction) -> None:
        """Execute a standardize action"""
        source = action.source

        if "Create app directory" in action.reason:
            service_path = source
            app_dir = os.path.join(service_path, "app")
            os.makedirs(app_dir, exist_ok=True)

            # Find all Python files at root and move them to app directory
            for file in os.listdir(service_path):
                if file.endswith(".py") and not file.startswith("test_"):
                    file_path = os.path.join(service_path, file)
                    if os.path.isfile(file_path):
                        # Create backup
                        backup_path = os.path.join(
                            BACKUP_DIR, os.path.relpath(file_path, ROOT_DIR)
                        )
                        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
                        shutil.copy2(file_path, backup_path)

                        # Move to app directory
                        shutil.move(file_path, os.path.join(app_dir, file))

        elif "Create tests directory" in action.reason:
            service_path = source
            tests_dir = os.path.join(service_path, "tests")
            os.makedirs(tests_dir, exist_ok=True)

            # Find all test files at root and move them to tests directory
            for file in os.listdir(service_path):
                if file.startswith("test_") and file.endswith(".py"):
                    file_path = os.path.join(service_path, file)
                    if os.path.isfile(file_path):
                        # Create backup
                        backup_path = os.path.join(
                            BACKUP_DIR, os.path.relpath(file_path, ROOT_DIR)
                        )
                        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
                        shutil.copy2(file_path, backup_path)

                        # Move to tests directory
                        shutil.move(file_path, os.path.join(tests_dir, file))

    def save_plan(self, output_file: str) -> None:
        """Save the cleanup plan to a file"""
        plan_data = {
            "actions": [
                {
                    "action_type": action.action_type,
                    "source": action.source,
                    "destination": action.destination,
                    "reason": action.reason,
                }
                for action in self.actions
            ],
            "summary": {
                "total_files_scanned": self.scanned_files,
                "duplicate_files": len(self.duplicate_files),
                "backup_files": len(self.backup_files),
                "test_files_outside_tests": len(self.test_files_outside_tests),
                "script_files_outside_scripts": len(self.script_files_outside_scripts),
                "docker_files_outside_infrastructure": len(
                    self.docker_files_outside_infrastructure
                ),
                "config_files_outside_config": len(self.config_files_outside_config),
                "total_actions": len(self.actions),
            },
            "verification_results": self.verification_results,
        }

        with open(output_file, "w") as f:
            json.dump(plan_data, f, indent=2)

    def verify_system_functionality(self) -> dict[str, Any]:
        """Verify that the system still functions after cleanup"""
        logger.info("Verifying system functionality...")

        verification_results = {
            "tests_passed": False,
            "services_started": False,
            "blockchain_intact": False,
            "errors": [],
        }

        # Run tests
        try:
            logger.info("Running tests...")
            result = subprocess.run(
                ["pytest", "-xvs", "tests/"],
                check=False,
                cwd=ROOT_DIR,
                capture_output=True,
                text=True,
            )
            verification_results["tests_passed"] = result.returncode == 0
            if result.returncode != 0:
                verification_results["errors"].append("Tests failed")
                verification_results["test_output"] = result.stdout + result.stderr
        except Exception as e:
            verification_results["errors"].append(f"Error running tests: {e}")

        # Check if services can start
        try:
            logger.info("Checking if services can start...")
            services_ok = True
            for service_name in CORE_SERVICES:
                # Just check if the service directory exists and has a main.py or app.py
                service_found = False
                for root, dirs, files in os.walk(ROOT_DIR):
                    if service_name in dirs:
                        service_dir = os.path.join(root, service_name)
                        if (
                            os.path.exists(os.path.join(service_dir, "main.py"))
                            or os.path.exists(os.path.join(service_dir, "app.py"))
                            or os.path.exists(
                                os.path.join(service_dir, "app", "main.py")
                            )
                        ):
                            service_found = True
                            break

                if not service_found:
                    services_ok = False
                    verification_results["errors"].append(
                        f"Service {service_name} missing entry point"
                    )

            verification_results["services_started"] = services_ok
        except Exception as e:
            verification_results["errors"].append(f"Error checking services: {e}")

        # Check blockchain integrity
        try:
            logger.info("Checking blockchain integrity...")
            blockchain_dir = os.path.join(ROOT_DIR, "blockchain")
            if os.path.exists(blockchain_dir) and os.path.isdir(blockchain_dir):
                verification_results["blockchain_intact"] = True
            else:
                verification_results["errors"].append("Blockchain directory missing")
        except Exception as e:
            verification_results["errors"].append(f"Error checking blockchain: {e}")

        return verification_results

    def apply_code_formatting(self) -> None:
        """Apply code formatting and style standards"""
        logger.info("Applying code formatting and style standards...")

        # Format Python files with Black
        try:
            result = subprocess.run(
                [
                    "black",
                    "--line-length",
                    "88",
                    "services/",
                    "scripts/",
                    "tests/",
                    "--exclude",
                    "venv|__pycache__|.git",
                ],
                check=False,
                cwd=ROOT_DIR,
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                logger.info("Successfully formatted Python files with Black")
            else:
                logger.warning(f"Error formatting Python files: {result.stderr}")
        except Exception as e:
            logger.warning(f"Error running Black: {e}")

        # Format JavaScript/TypeScript files with Prettier
        try:
            result = subprocess.run(
                [
                    "npx",
                    "prettier",
                    "--write",
                    "**/*.{js,ts,jsx,tsx,json}",
                    "--ignore-path",
                    ".gitignore",
                ],
                check=False,
                cwd=ROOT_DIR,
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                logger.info("Successfully formatted JS/TS files with Prettier")
            else:
                logger.warning(f"Error formatting JS/TS files: {result.stderr}")
        except Exception as e:
            logger.warning(f"Error running Prettier: {e}")

        # Format Rust files with rustfmt
        try:
            result = subprocess.run(
                ["find", ".", "-name", "*.rs", "-exec", "rustfmt", "{}", ";"],
                check=False,
                cwd=ROOT_DIR,
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                logger.info("Successfully formatted Rust files with rustfmt")
            else:
                logger.warning(f"Error formatting Rust files: {result.stderr}")
        except Exception as e:
            logger.warning(f"Error running rustfmt: {e}")


def main() -> None:
    """Main function"""
    parser = argparse.ArgumentParser(
        description="ACGS-1 Codebase Cleanup and Reorganization"
    )
    parser.add_argument(
        "--execute", action="store_true", help="Execute the cleanup plan"
    )
    parser.add_argument(
        "--output", default="cleanup_plan.json", help="Output file for the cleanup plan"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify system functionality after cleanup",
    )
    parser.add_argument(
        "--skip-scan",
        action="store_true",
        help="Skip scanning files (use existing plan)",
    )
    parser.add_argument("--format", action="store_true", help="Apply code formatting")
    args = parser.parse_args()

    reorganizer = CodebaseReorganizer()

    try:
        if not args.skip_scan:
            reorganizer.scan_files()
            reorganizer.find_duplicate_files()
            reorganizer.find_backup_files()
            reorganizer.find_misplaced_files()
            reorganizer.validate_core_services()
            reorganizer.generate_cleanup_plan()

            # Save the plan to a file
            reorganizer.save_plan(args.output)
            logger.info(f"Cleanup plan saved to {args.output}")
        else:
            # Load plan from file
            with open(args.output) as f:
                plan_data = json.load(f)
                for action_data in plan_data.get("actions", []):
                    reorganizer.add_action(
                        FileAction(
                            action_data["action_type"],
                            action_data["source"],
                            action_data.get("destination"),
                            action_data["reason"],
                        )
                    )

        # Execute the plan if requested
        reorganizer.execute_plan(dry_run=not args.execute)

        # Apply code formatting if requested
        if args.format:
            reorganizer.apply_code_formatting()

        # Verify system functionality if requested and changes were made
        if args.verify and args.execute:
            verification_results = reorganizer.verify_system_functionality()

            # Save verification results
            verification_file = f"verification_results_{BACKUP_TIMESTAMP}.json"
            with open(verification_file, "w") as f:
                json.dump(verification_results, f, indent=2)

            logger.info(f"Verification results saved to {verification_file}")

            # Check if verification passed
            if verification_results.get("errors"):
                logger.error("Verification failed with errors:")
                for error in verification_results["errors"]:
                    logger.error(f"- {error}")
            else:
                logger.info("Verification passed!")

        if not args.execute:
            logger.info("\nTo execute the cleanup plan, run:")
            logger.info(f"python {__file__} --execute")

    except KeyboardInterrupt:
        logger.error("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback

        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
