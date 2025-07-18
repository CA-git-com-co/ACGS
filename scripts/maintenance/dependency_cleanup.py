#!/usr/bin/env python3
"""
ACGS-1 Dependency Management and Cleanup

This script consolidates and cleans up dependency files across the ACGS-1
constitutional governance system, removing duplicates and resolving conflicts.

Features:
- Consolidate config/environments/requirements.txt files
- Remove unused dependencies
- Resolve version conflicts
- Clean up package.json files
- Update Cargo.toml files
"""

import json
import logging
from collections import defaultdict
from pathlib import Path

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DependencyCleanup:
    """Handles dependency management and cleanup."""

    def __init__(self, project_root: str = "/home/dislove/ACGS-1"):
        self.project_root = Path(project_root)
        self.dependency_report = {
            "requirements_files_processed": [],
            "package_json_files_processed": [],
            "cargo_toml_files_processed": [],
            "duplicates_removed": [],
            "conflicts_resolved": [],
            "errors": [],
        }

    def consolidate_requirements_files(self):
        """Consolidate and clean config/environments/requirements.txt files."""
        logger.info("🔧 Consolidating config/environments/requirements.txt files...")

        # Find all requirements files
        requirements_files = list(self.project_root.glob("**/requirements*.txt"))

        # Group by service/directory
        service_requirements = defaultdict(list)

        for req_file in requirements_files:
            if self._should_process_file(req_file):
                # Determine service name from path
                service_name = self._get_service_name(req_file)
                service_requirements[service_name].append(req_file)

        # Process each service's requirements
        for service_name, req_files in service_requirements.items():
            if len(req_files) > 1:
                self._merge_requirements_files(service_name, req_files)
            else:
                self._clean_single_requirements_file(req_files[0])

    def clean_package_json_files(self):
        """Clean and optimize package.json files."""
        logger.info("📦 Cleaning package.json files...")

        package_files = list(self.project_root.glob("**/package.json"))

        for package_file in package_files:
            if self._should_process_file(package_file):
                try:
                    with open(package_file) as f:
                        package_data = json.load(f)

                    # Remove common unused dependencies
                    self._remove_unused_npm_dependencies(package_data)

                    # Sort dependencies
                    if "dependencies" in package_data:
                        package_data["dependencies"] = dict(
                            sorted(package_data["dependencies"].items())
                        )
                    if "devDependencies" in package_data:
                        package_data["devDependencies"] = dict(
                            sorted(package_data["devDependencies"].items())
                        )

                    # Write back cleaned package.json
                    with open(package_file, "w") as f:
                        json.dump(package_data, f, indent=2)

                    self.dependency_report["package_json_files_processed"].append(
                        str(package_file)
                    )
                    logger.info(f"Cleaned package.json: {package_file}")

                except Exception as e:
                    logger.error(f"Error cleaning package.json {package_file}: {e}")
                    self.dependency_report["errors"].append(
                        f"Package.json error: {package_file}"
                    )

    def clean_cargo_toml_files(self):
        """Clean and optimize Cargo.toml files."""
        logger.info("🦀 Cleaning Cargo.toml files...")

        cargo_files = list(self.project_root.glob("**/Cargo.toml"))

        for cargo_file in cargo_files:
            if self._should_process_file(cargo_file):
                try:
                    with open(cargo_file) as f:
                        content = f.read()

                    # Basic cleanup - remove empty lines and normalize formatting
                    lines = content.split("\n")
                    cleaned_lines = []

                    for line in lines:
                        stripped = line.strip()
                        if stripped or (cleaned_lines and cleaned_lines[-1].strip()):
                            cleaned_lines.append(line)

                    # Write back cleaned content
                    with open(cargo_file, "w") as f:
                        f.write("\n".join(cleaned_lines))

                    self.dependency_report["cargo_toml_files_processed"].append(
                        str(cargo_file)
                    )
                    logger.info(f"Cleaned Cargo.toml: {cargo_file}")

                except Exception as e:
                    logger.error(f"Error cleaning Cargo.toml {cargo_file}: {e}")
                    self.dependency_report["errors"].append(
                        f"Cargo.toml error: {cargo_file}"
                    )

    def _merge_requirements_files(self, service_name: str, req_files: list[Path]):
        """Merge multiple requirements files for a service."""
        logger.info(f"Merging {len(req_files)} requirements files for {service_name}")

        all_dependencies = {}
        comments = []

        # Read all requirements files
        for req_file in req_files:
            try:
                with open(req_file) as f:
                    lines = f.readlines()

                for line in lines:
                    line = line.strip()
                    if line.startswith("#"):
                        if line not in comments:
                            comments.append(line)
                    elif line and "==" in line:
                        package_name = line.split("==")[0].strip()
                        all_dependencies[package_name] = line
                    elif line and ">=" in line:
                        package_name = line.split(">=")[0].strip()
                        if package_name not in all_dependencies:
                            all_dependencies[package_name] = line

            except Exception as e:
                logger.error(f"Error reading {req_file}: {e}")

        # Write merged requirements to main file
        main_req_file = req_files[0]  # Use first file as main
        try:
            with open(main_req_file, "w") as f:
                # Write comments first
                for comment in comments:
                    f.write(comment + "\n")

                if comments:
                    f.write("\n")

                # Write sorted dependencies
                for package_name in sorted(all_dependencies.keys()):
                    f.write(all_dependencies[package_name] + "\n")

            # Remove other requirements files
            for req_file in req_files[1:]:
                req_file.unlink()
                self.dependency_report["duplicates_removed"].append(str(req_file))

            self.dependency_report["requirements_files_processed"].append(
                str(main_req_file)
            )
            logger.info(f"Merged requirements for {service_name} into {main_req_file}")

        except Exception as e:
            logger.error(f"Error merging requirements for {service_name}: {e}")

    def _clean_single_requirements_file(self, req_file: Path):
        """Clean a single requirements file."""
        try:
            with open(req_file) as f:
                lines = f.readlines()

            cleaned_lines = []
            seen_packages = set()

            for line in lines:
                line = line.strip()
                if line.startswith("#") or not line:
                    cleaned_lines.append(line)
                elif "==" in line or ">=" in line:
                    package_name = line.split("==")[0].split(">=")[0].strip()
                    if package_name not in seen_packages:
                        seen_packages.add(package_name)
                        cleaned_lines.append(line)
                    else:
                        self.dependency_report["duplicates_removed"].append(
                            f"{package_name} in {req_file}"
                        )

            # Write back cleaned requirements
            with open(req_file, "w") as f:
                f.write("\n".join(cleaned_lines) + "\n")

            self.dependency_report["requirements_files_processed"].append(str(req_file))
            logger.info(f"Cleaned requirements file: {req_file}")

        except Exception as e:
            logger.error(f"Error cleaning requirements file {req_file}: {e}")

    def _remove_unused_npm_dependencies(self, package_data: dict):
        """Remove commonly unused npm dependencies."""

        dependencies = package_data.get("dependencies", {})
        package_data.get("devDependencies", {})

        # Move typescript to devDependencies if in dependencies
        if "typescript" in dependencies:
            if "devDependencies" not in package_data:
                package_data["devDependencies"] = {}
            package_data["devDependencies"]["typescript"] = dependencies.pop(
                "typescript"
            )
            self.dependency_report["conflicts_resolved"].append(
                "Moved typescript to devDependencies"
            )

        # Remove truly unused dependencies (this would need more sophisticated analysis)
        # For now, just clean up obvious issues

    def _get_service_name(self, file_path: Path) -> str:
        """Extract service name from file path."""
        parts = file_path.parts

        # Look for service indicators
        for i, part in enumerate(parts):
            if part in ["services", "backend", "src"]:
                if i + 1 < len(parts):
                    return parts[i + 1]

        # Fallback to parent directory name
        return file_path.parent.name

    def _should_process_file(self, file_path: Path) -> bool:
        """Determine if file should be processed."""
        exclude_patterns = [
            "venv",
            ".venv",
            "__pycache__",
            ".git",
            "node_modules",
            "target",
            "backup_",
            "archive",
            ".pytest_cache",
            "build",
            "dist",
        ]
        return not any(pattern in str(file_path) for pattern in exclude_patterns)

    def generate_dependency_summary(self):
        """Generate a summary of all dependencies across the project."""
        logger.info("📊 Generating dependency summary...")

        summary = {
            "python_dependencies": {},
            "npm_dependencies": {},
            "rust_dependencies": {},
        }

        # Collect Python dependencies
        for req_file in self.project_root.glob("**/requirements*.txt"):
            if self._should_process_file(req_file):
                try:
                    with open(req_file) as f:
                        for line in f:
                            line = line.strip()
                            if (
                                line
                                and not line.startswith("#")
                                and ("==" in line or ">=" in line)
                            ):
                                package_name = (
                                    line.split("==")[0].split(">=")[0].strip()
                                )
                                summary["python_dependencies"][package_name] = line
                except Exception:
                    pass

        # Collect NPM dependencies
        for package_file in self.project_root.glob("**/package.json"):
            if self._should_process_file(package_file):
                try:
                    with open(package_file) as f:
                        package_data = json.load(f)

                    for dep_type in ["dependencies", "devDependencies"]:
                        if dep_type in package_data:
                            for name, version in package_data[dep_type].items():
                                summary["npm_dependencies"][name] = version
                except Exception:
                    pass

        # Save summary
        summary_file = self.project_root / "dependency_summary.json"
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)

        logger.info(f"Dependency summary saved to: {summary_file}")
        return summary

    def run_dependency_cleanup(self):
        """Run complete dependency cleanup process."""
        logger.info("🚀 Starting ACGS-1 Dependency Cleanup...")

        # 1. Consolidate requirements files
        self.consolidate_requirements_files()

        # 2. Clean package.json files
        self.clean_package_json_files()

        # 3. Clean Cargo.toml files
        self.clean_cargo_toml_files()

        # 4. Generate dependency summary
        self.generate_dependency_summary()

        # 5. Save cleanup report
        report_path = self.project_root / "dependency_cleanup_report.json"
        with open(report_path, "w") as f:
            json.dump(self.dependency_report, f, indent=2)

        logger.info(f"✅ Dependency cleanup completed. Report: {report_path}")

        # Summary
        logger.info("📊 Summary:")
        logger.info(
            f"  - {len(self.dependency_report['requirements_files_processed'])} requirements files processed"
        )
        logger.info(
            f"  - {len(self.dependency_report['package_json_files_processed'])} package.json files processed"
        )
        logger.info(
            f"  - {len(self.dependency_report['cargo_toml_files_processed'])} Cargo.toml files processed"
        )
        logger.info(
            f"  - {len(self.dependency_report['duplicates_removed'])} duplicates removed"
        )
        logger.info(
            f"  - {len(self.dependency_report['conflicts_resolved'])} conflicts resolved"
        )
        logger.info(f"  - {len(self.dependency_report['errors'])} errors encountered")

        return self.dependency_report


def main():
    """Main execution function."""
    cleanup = DependencyCleanup()
    cleanup.run_dependency_cleanup()


if __name__ == "__main__":
    main()
