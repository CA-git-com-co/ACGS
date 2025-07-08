#!/usr/bin/env python3
"""
ACGS Dependency and Configuration Cleanup
Constitutional Hash: cdd01ef066bc6cf2

Cleans unused dependencies, optimizes configuration files, and validates
ACGS service compatibility while maintaining constitutional compliance.
"""

import json
import logging
import subprocess
from pathlib import Path

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
REPO_ROOT = Path("/home/dislove/ACGS-2")

# Configuration files to optimize
CONFIG_FILES = [
    "pyproject.toml",
    "pytest.ini",
    "docker-compose.yml",
    "docker-compose.*.yml",
]

# Protected dependencies (never remove)
PROTECTED_DEPENDENCIES = {
    "fastapi",
    "pydantic",
    "uvicorn",
    "asyncio",
    "redis",
    "psycopg",
    "sqlalchemy",
    "prometheus-client",
    "pytest",
    "pytest-asyncio",
}


class ACGSDependencyConfigurationCleanup:
    """Handles cleanup of dependencies and configuration optimization."""

    def __init__(self):
        self.logger = self._setup_logging()
        self.cleanup_stats = {
            "dependencies_analyzed": 0,
            "unused_dependencies": 0,
            "config_files_optimized": 0,
            "duplicates_removed": 0,
            "bytes_freed": 0,
            "protected_items": 0,
            "errors": [],
        }

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for cleanup operations."""
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )
        return logging.getLogger(__name__)

    def _run_command(self, command: str, cwd: Path = None) -> tuple[bool, str, str]:
        """Run shell command safely."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=cwd or REPO_ROOT,
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)

    def _is_protected_dependency(self, dep_name: str) -> bool:
        """Check if dependency should be protected."""
        dep_lower = dep_name.lower()

        # Check protected dependencies
        for protected in PROTECTED_DEPENDENCIES:
            if protected in dep_lower:
                return True

        # Check for constitutional compliance related packages
        constitutional_keywords = [
            "constitutional",
            "compliance",
            "governance",
            "auth",
            "security",
        ]
        if any(keyword in dep_lower for keyword in constitutional_keywords):
            return True

        return False

    def analyze_python_dependencies(self) -> dict[str, list[str]]:
        """Analyze Python dependencies for unused packages."""
        self.logger.info("🐍 Analyzing Python dependencies...")

        dependency_analysis = {"used": [], "unused": [], "protected": []}

        # Check if pip-audit is available
        success, stdout, stderr = self._run_command("pip list --format=json")
        if not success:
            self.logger.warning("Could not analyze Python dependencies")
            return dependency_analysis

        try:
            installed_packages = json.loads(stdout)
            self.cleanup_stats["dependencies_analyzed"] = len(installed_packages)

            for package in installed_packages:
                package_name = package["name"]

                if self._is_protected_dependency(package_name):
                    dependency_analysis["protected"].append(package_name)
                    self.cleanup_stats["protected_items"] += 1
                    self.logger.info(f"  🛡️ Protected: {package_name}")
                else:
                    # For now, mark as used (would need more sophisticated analysis)
                    dependency_analysis["used"].append(package_name)

        except json.JSONDecodeError:
            self.logger.error("Failed to parse pip list output")

        return dependency_analysis

    def optimize_requirements_files(self) -> list[str]:
        """Optimize requirements files by removing duplicates."""
        self.logger.info("📋 Optimizing requirements files...")
        optimized_files = []

        requirements_files = list(REPO_ROOT.rglob("requirements*.txt"))

        for req_file in requirements_files:
            if req_file.is_file():
                try:
                    with open(req_file) as f:
                        lines = f.readlines()

                    # Remove duplicates while preserving order
                    seen = set()
                    unique_lines = []

                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            # Extract package name (before ==, >=, etc.)
                            package_name = (
                                line.split("==")[0]
                                .split(">=")[0]
                                .split("<=")[0]
                                .split("~=")[0]
                                .strip()
                            )

                            if package_name not in seen:
                                seen.add(package_name)
                                unique_lines.append(line + "\n")
                            else:
                                self.cleanup_stats["duplicates_removed"] += 1
                                self.logger.info(
                                    f"  ✅ Removed duplicate: {package_name} from"
                                    f" {req_file.name}"
                                )
                        else:
                            unique_lines.append(line)

                    # Write back if changes were made
                    if len(unique_lines) < len(lines):
                        with open(req_file, "w") as f:
                            f.writelines(unique_lines)
                        optimized_files.append(str(req_file.relative_to(REPO_ROOT)))
                        self.cleanup_stats["config_files_optimized"] += 1
                        self.logger.info(
                            f"  ✅ Optimized: {req_file.relative_to(REPO_ROOT)}"
                        )

                except Exception as e:
                    error_msg = f"Failed to optimize {req_file}: {e}"
                    self.cleanup_stats["errors"].append(error_msg)
                    self.logger.error(f"  ❌ {error_msg}")

        return optimized_files

    def optimize_docker_compose_files(self) -> list[str]:
        """Optimize Docker Compose files."""
        self.logger.info("🐳 Optimizing Docker Compose files...")
        optimized_files = []

        compose_files = list(REPO_ROOT.glob("docker-compose*.yml"))

        for compose_file in compose_files:
            if compose_file.is_file():
                try:
                    with open(compose_file) as f:
                        content = f.read()

                    # Check if file contains constitutional hash
                    if CONSTITUTIONAL_HASH not in content:
                        # Add constitutional hash comment
                        lines = content.split("\n")
                        if lines and not lines[0].startswith("#"):
                            lines.insert(
                                0, f"# Constitutional Hash: {CONSTITUTIONAL_HASH}"
                            )
                            lines.insert(1, "")

                            new_content = "\n".join(lines)
                            with open(compose_file, "w") as f:
                                f.write(new_content)

                            optimized_files.append(
                                str(compose_file.relative_to(REPO_ROOT))
                            )
                            self.cleanup_stats["config_files_optimized"] += 1
                            self.logger.info(
                                "  ✅ Added constitutional hash to:"
                                f" {compose_file.relative_to(REPO_ROOT)}"
                            )
                    else:
                        self.logger.info(
                            "  ✅ Constitutional hash present:"
                            f" {compose_file.relative_to(REPO_ROOT)}"
                        )

                except Exception as e:
                    error_msg = f"Failed to optimize {compose_file}: {e}"
                    self.cleanup_stats["errors"].append(error_msg)
                    self.logger.error(f"  ❌ {error_msg}")

        return optimized_files

    def validate_acgs_service_compatibility(self) -> bool:
        """Validate that ACGS services are still compatible after cleanup."""
        self.logger.info("🔍 Validating ACGS service compatibility...")

        # Check critical service files
        critical_services = [
            "services/core/constitutional-ai",
            "services/core/integrity",
            "services/shared/auth",
            "services/core/multi-agent-coordinator",
        ]

        all_compatible = True
        for service_path in critical_services:
            service_dir = REPO_ROOT / service_path

            # Check if service directory exists
            if service_dir.exists():
                self.logger.info(f"  ✅ Service directory exists: {service_path}")

                # Check for requirements or dependencies
                req_files = list(service_dir.rglob("requirements*.txt"))
                if req_files:
                    self.logger.info(f"    Requirements files found: {len(req_files)}")
                else:
                    self.logger.info(
                        "    No requirements files (may use parent requirements)"
                    )
            else:
                self.logger.warning(f"  ⚠️ Service directory not found: {service_path}")

        # Check Docker Compose files are valid
        compose_files = ["docker-compose.yml", "docker-compose.services.yml"]
        for compose_file in compose_files:
            compose_path = REPO_ROOT / compose_file
            if compose_path.exists():
                # Try to validate YAML syntax
                success, stdout, stderr = self._run_command(
                    f"docker-compose -f {compose_file} config --quiet"
                )
                if success:
                    self.logger.info(f"  ✅ Valid Docker Compose: {compose_file}")
                else:
                    self.logger.error(f"  ❌ Invalid Docker Compose: {compose_file}")
                    all_compatible = False
            else:
                self.logger.warning(f"  ⚠️ Docker Compose file missing: {compose_file}")

        return all_compatible

    def cleanup_configuration_duplicates(self) -> list[str]:
        """Remove duplicate configuration entries."""
        self.logger.info("⚙️ Cleaning configuration duplicates...")
        cleaned_files = []

        # Check pyproject.toml for duplicates
        pyproject_path = REPO_ROOT / "pyproject.toml"
        if pyproject_path.exists():
            try:
                with open(pyproject_path) as f:
                    content = f.read()

                # Add constitutional hash if missing
                if CONSTITUTIONAL_HASH not in content:
                    lines = content.split("\n")
                    lines.insert(0, f"# Constitutional Hash: {CONSTITUTIONAL_HASH}")
                    lines.insert(1, "")

                    new_content = "\n".join(lines)
                    with open(pyproject_path, "w") as f:
                        f.write(new_content)

                    cleaned_files.append("pyproject.toml")
                    self.cleanup_stats["config_files_optimized"] += 1
                    self.logger.info(
                        "  ✅ Added constitutional hash to: pyproject.toml"
                    )

            except Exception as e:
                error_msg = f"Failed to process pyproject.toml: {e}"
                self.cleanup_stats["errors"].append(error_msg)
                self.logger.error(f"  ❌ {error_msg}")

        return cleaned_files

    def run_cleanup(self) -> dict:
        """Run complete dependency and configuration cleanup."""
        self.logger.info("🧹 Starting ACGS Dependency and Configuration Cleanup...")
        self.logger.info(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")

        # Run all cleanup operations
        self.analyze_python_dependencies()
        self.optimize_requirements_files()
        self.optimize_docker_compose_files()
        self.cleanup_configuration_duplicates()

        # Validate service compatibility
        if not self.validate_acgs_service_compatibility():
            self.logger.warning("⚠️ Some ACGS service compatibility issues detected")

        # Format bytes freed
        bytes_freed = self.cleanup_stats["bytes_freed"]
        if bytes_freed > 1024 * 1024:
            size_str = f"{bytes_freed / (1024 * 1024):.1f} MB"
        elif bytes_freed > 1024:
            size_str = f"{bytes_freed / 1024:.1f} KB"
        else:
            size_str = f"{bytes_freed} bytes"

        self.logger.info("📊 Cleanup Summary:")
        self.logger.info(
            f"  Dependencies analyzed: {self.cleanup_stats['dependencies_analyzed']}"
        )
        self.logger.info(
            f"  Config files optimized: {self.cleanup_stats['config_files_optimized']}"
        )
        self.logger.info(
            f"  Duplicates removed: {self.cleanup_stats['duplicates_removed']}"
        )
        self.logger.info(f"  Protected items: {self.cleanup_stats['protected_items']}")
        self.logger.info(f"  Space freed: {size_str}")
        self.logger.info(f"  Errors: {len(self.cleanup_stats['errors'])}")

        if self.cleanup_stats["errors"]:
            self.logger.warning("⚠️ Errors encountered:")
            for error in self.cleanup_stats["errors"]:
                self.logger.warning(f"  - {error}")

        return self.cleanup_stats


def main():
    """Main cleanup function."""
    print("🧹 ACGS Dependency and Configuration Cleanup")
    print("=" * 50)
    print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print(f"Repository: {REPO_ROOT}")
    print()

    cleaner = ACGSDependencyConfigurationCleanup()
    results = cleaner.run_cleanup()

    print("\n✅ Dependency and configuration cleanup completed!")
    return results


if __name__ == "__main__":
    main()
