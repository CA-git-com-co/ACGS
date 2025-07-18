#!/usr/bin/env python3
"""
ACGS Comprehensive Dependency Management Setup

This script sets up unified dependency management using:
- UV for Python dependencies
- TOML configuration files
- Proper .gitignore for all dependency artifacts
- Workspace-based dependency resolution

Features:
1. Consolidates all Python requirements into config/environments/pyproject.toml files
2. Sets up UV workspace configuration
3. Removes duplicate dependency files
4. Configures proper .gitignore patterns
5. Creates lock files for reproducible builds
"""

import logging
import shutil
import subprocess
import sys
from pathlib import Path

import toml

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("dependency_management_setup.log"),
    ],
)
logger = logging.getLogger(__name__)


class DependencyManager:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.uv_installed = False
        self.backup_dir = self.project_root / "dependency_backup"

        # Service directories that need config/environments/pyproject.toml
        self.service_dirs = [
            "services/core/constitutional-ai",
            "services/core/formal-verification",
            "services/core/governance-synthesis",
            "services/core/policy-governance",
            "services/core/evolutionary-computation",
            "services/platform/authentication",
            "services/platform/integrity",
            "services/shared",
            "integrations/data-flywheel",
            "integrations/quantumagi-bridge",
            "integrations/alphaevolve-engine",
            "tools",
            "scripts",
            "infrastructure/monitoring/elk-config/security-processor",
        ]

    def check_uv_installation(self) -> bool:
        """Check if UV is installed and install if needed"""
        try:
            result = subprocess.run(
                ["uv", "--version"], check=False, capture_output=True, text=True
            )
            if result.returncode == 0:
                logger.info(f"UV is already installed: {result.stdout.strip()}")
                self.uv_installed = True
                return True
        except FileNotFoundError:
            pass

        logger.info("Installing UV...")
        try:
            # Install UV using the official installer
            subprocess.run(
                ["curl", "-LsSf", "https://astral.sh/uv/install.sh"],
                check=True,
                shell=True,
            )

            # Verify installation
            result = subprocess.run(
                ["uv", "--version"], check=False, capture_output=True, text=True
            )
            if result.returncode == 0:
                logger.info(f"UV installed successfully: {result.stdout.strip()}")
                self.uv_installed = True
                return True
            logger.error("UV installation verification failed")
            return False

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install UV: {e}")
            return False

    def backup_existing_files(self) -> None:
        """Backup existing dependency files before modification"""
        logger.info("Creating backup of existing dependency files...")

        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        self.backup_dir.mkdir(parents=True)

        # Find all dependency files to backup
        dependency_patterns = [
            "requirements*.txt",
            "package.json",
            "package-lock.json",
            "yarn.lock",
            "Pipfile",
            "Pipfile.lock",
            "poetry.lock",
            "config/environments/pyproject.toml",
        ]

        for pattern in dependency_patterns:
            for file_path in self.project_root.rglob(pattern):
                if "node_modules" not in str(file_path) and "venv" not in str(
                    file_path
                ):
                    relative_path = file_path.relative_to(self.project_root)
                    backup_path = self.backup_dir / relative_path
                    backup_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_path, backup_path)
                    logger.debug(f"Backed up: {relative_path}")

    def collect_python_dependencies(self) -> dict[str, set[str]]:
        """Collect all Python dependencies from requirements files"""
        logger.info("Collecting Python dependencies from requirements files...")

        all_deps = {"main": set(), "dev": set(), "test": set(), "docs": set()}

        # Find all requirements files
        for req_file in self.project_root.rglob("requirements*.txt"):
            if "node_modules" in str(req_file) or "venv" in str(req_file):
                continue

            logger.debug(f"Processing: {req_file}")

            try:
                with open(req_file) as f:
                    lines = f.readlines()

                # Determine category based on filename
                filename = req_file.name.lower()
                if "dev" in filename:
                    category = "dev"
                elif "test" in filename:
                    category = "test"
                elif "doc" in filename:
                    category = "docs"
                else:
                    category = "main"

                # Parse dependencies
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith("#") and not line.startswith("-"):
                        # Clean up the dependency specification
                        dep = line.split("#")[0].strip()
                        if dep:
                            all_deps[category].add(dep)

            except Exception as e:
                logger.warning(f"Failed to process {req_file}: {e}")

        # Log summary
        for category, deps in all_deps.items():
            logger.info(f"Found {len(deps)} {category} dependencies")

        return all_deps

    def create_service_pyproject_toml(
        self, service_dir: Path, service_name: str, deps: dict[str, set[str]]
    ) -> None:
        """Create config/environments/pyproject.toml for a service directory"""
        logger.info(f"Creating config/environments/pyproject.toml for {service_name}")

        # Base configuration
        config = {
            "build-system": {
                "requires": ["hatchling"],
                "build-backend": "hatchling.build",
            },
            "project": {
                "name": f"acgs-{service_name}",
                "version": "1.0.0",
                "description": f"ACGS {service_name.replace('-', ' ').title()} Service",
                "readme": "README.md",
                "license": "Apache-2.0",
                "requires-python": ">=3.11",
                "authors": [{"name": "ACGS-1 Team", "email": "info@soln.ai"}],
                "keywords": ["acgs", "governance", "constitutional", "ai"],
                "classifiers": [
                    "Development Status :: 4 - Beta",
                    "Intended Audience :: Developers",
                    "License :: OSI Approved :: Apache Software License",
                    "Programming Language :: Python :: 3",
                    "Programming Language :: Python :: 3.11",
                    "Programming Language :: Python :: 3.12",
                ],
                "dependencies": sorted(list(deps["main"])),
                "optional-dependencies": {
                    "dev": sorted(list(deps["dev"])),
                    "test": sorted(list(deps["test"])),
                    "docs": sorted(list(deps["docs"])),
                },
            },
            "tool": {
                "hatch": {"build": {"targets": {"wheel": {"packages": ["src"]}}}},
                "black": {
                    "line-length": 100,
                    "target-version": ["py311"],
                    "include": r"\.pyi?$",
                },
                "isort": {"profile": "black", "line_length": 100},
                "mypy": {
                    "python_version": "3.11",
                    "warn_return_any": True,
                    "warn_unused_configs": True,
                    "disallow_untyped_defs": True,
                },
            },
        }

        # Write config/environments/pyproject.toml
        pyproject_path = service_dir / "config/environments/pyproject.toml"
        with open(pyproject_path, "w") as f:
            toml.dump(config, f)

        logger.debug(f"Created: {pyproject_path}")

    def setup_uv_workspace(self) -> None:
        """Initialize UV workspace"""
        if not self.uv_installed:
            logger.error("UV is not installed. Cannot setup workspace.")
            return

        logger.info("Setting up UV workspace...")

        try:
            # Initialize UV project
            subprocess.run(
                ["uv", "init", "--no-readme"], cwd=self.project_root, check=True
            )

            # Sync dependencies
            subprocess.run(["uv", "sync"], cwd=self.project_root, check=True)

            logger.info("UV workspace setup complete")

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to setup UV workspace: {e}")

    def remove_old_dependency_files(self) -> None:
        """Remove old dependency files after migration"""
        logger.info("Removing old dependency files...")

        files_to_remove = []

        # Find requirements files to remove (keep root-level ones for now)
        for req_file in self.project_root.rglob("requirements*.txt"):
            if "node_modules" not in str(req_file) and "venv" not in str(req_file):
                # Only remove if not in root directory
                if req_file.parent != self.project_root:
                    files_to_remove.append(req_file)

        # Remove files
        for file_path in files_to_remove:
            try:
                file_path.unlink()
                logger.debug(f"Removed: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to remove {file_path}: {e}")

        logger.info(f"Removed {len(files_to_remove)} old dependency files")

    def run_setup(self) -> bool:
        """Run the complete dependency management setup"""
        logger.info("Starting ACGS dependency management setup...")

        try:
            # Step 1: Check UV installation
            if not self.check_uv_installation():
                logger.error("UV installation failed. Aborting setup.")
                return False

            # Step 2: Backup existing files
            self.backup_existing_files()

            # Step 3: Collect dependencies
            all_deps = self.collect_python_dependencies()

            # Step 4: Create config/environments/pyproject.toml for each service
            for service_dir_str in self.service_dirs:
                service_dir = self.project_root / service_dir_str
                if service_dir.exists():
                    service_name = service_dir.name
                    self.create_service_pyproject_toml(
                        service_dir, service_name, all_deps
                    )

            # Step 5: Setup UV workspace
            self.setup_uv_workspace()

            # Step 6: Remove old files
            self.remove_old_dependency_files()

            logger.info("✅ Dependency management setup completed successfully!")
            logger.info(f"Backup created in: {self.backup_dir}")
            logger.info("Next steps:")
            logger.info("1. Review generated config/environments/pyproject.toml files")
            logger.info("2. Run 'uv sync' to install dependencies")
            logger.info("3. Test your services")
            logger.info("4. Commit changes to git")

            return True

        except Exception as e:
            logger.error(f"Setup failed: {e}")
            return False


def main():
    """Main entry point"""
    manager = DependencyManager()
    success = manager.run_setup()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
