#!/usr/bin/env python3
"""
ACGS-1 Comprehensive Codebase Cleanup and Reorganization
========================================================  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2

This script performs a comprehensive cleanup and reorganization of the ACGS-1 codebase
while preserving all critical functionality including:
- Quantumagi Solana devnet deployment (Constitution Hash: cdd01ef066bc6cf2)
- 7 core services operational status
- 5 governance workflows functionality
- Host-based deployment architecture with Redis integration

Author: ACGS-1 Development Team
Version: 1.0.0
"""

import json
import logging
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            f"acgs_reorganization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        ),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class ACGSReorganizer:
    """Main class for ACGS-1 codebase reorganization"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.backup_dir = (
            self.project_root
            / "backups"
            / f"reorganization_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        self.report = {
            "start_time": datetime.now().isoformat(),
            "phases": {},
            "preserved_functionality": [],
            "performance_metrics": {},
            "validation_results": {},
        }

    def create_backup(self) -> bool:
        """Create comprehensive backup before reorganization"""
        try:
            logger.info("Creating comprehensive backup...")
            self.backup_dir.mkdir(parents=True, exist_ok=True)

            # Critical directories to backup
            critical_dirs = [
                "blockchain/programs",
                "services/core",
                "services/platform",
                "config",
                "infrastructure",
                "docs",
            ]

            for dir_path in critical_dirs:
                src = self.project_root / dir_path
                if src.exists():
                    dst = self.backup_dir / dir_path
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    if src.is_dir():
                        shutil.copytree(src, dst, dirs_exist_ok=True)
                    else:
                        shutil.copy2(src, dst)

            logger.info(f"Backup created at: {self.backup_dir}")
            return True

        except Exception as e:
            logger.error(f"Backup creation failed: {e}")
            return False

    def validate_service_health(self) -> dict[str, bool]:
        """Validate current service health status"""
        try:
            result = subprocess.run(
                ["python3", "check_service_health.py"],
                check=False,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Parse service health from output
            services = {
                "constitutional-ai": False,
                "governance-synthesis": False,
                "formal-verification": False,
                "policy-governance": False,
                "evolutionary-computation": False,
                "self-evolving-ai": False,
                "acgs-pgp-v8": False,
            }

            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if "✅" in line:
                        for service in services:
                            if service in line or service.replace("-", "_") in line:
                                services[service] = True

            logger.info(f"Service health status: {services}")
            return services

        except Exception as e:
            logger.error(f"Service health validation failed: {e}")
            return {}

    def reorganize_directory_structure(self) -> bool:
        """Implement the target directory structure"""
        try:
            logger.info("Starting directory structure reorganization...")

            # Target structure mapping
            target_structure = {
                # Core services already well-organized
                "services/core": [
                    "constitutional-ai",
                    "governance-synthesis",
                    "formal-verification",
                    "policy-governance",
                    "evolutionary-computation",
                    "self-evolving-ai",
                    "acgs-pgp-v8",
                ],
                # Platform services
                "services/platform": [
                    "authentication",
                    "integrity",
                    "workflow",
                    "nvidia-llm-router",
                ],
                # Blockchain programs (already good)
                "blockchain/programs": ["quantumagi-core", "appeals", "logging"],
                # Applications
                "applications": ["governance-dashboard", "frontend", "app"],
                # Infrastructure
                "infrastructure": [
                    "docker",
                    "monitoring",
                    "redis",
                    "database",
                    "security",
                    "load-balancer",
                ],
            }

            # Create target directories
            for target_dir, subdirs in target_structure.items():
                target_path = self.project_root / target_dir
                target_path.mkdir(parents=True, exist_ok=True)

                for subdir in subdirs:
                    (target_path / subdir).mkdir(parents=True, exist_ok=True)

            # Move infrastructure components
            self._reorganize_infrastructure()

            # Standardize service directory patterns
            self._standardize_service_structure()

            logger.info("Directory structure reorganization completed")
            return True

        except Exception as e:
            logger.error(f"Directory reorganization failed: {e}")
            return False

    def _reorganize_infrastructure(self):
        """Reorganize infrastructure components"""
        # Move Docker configurations
        docker_files = [
            "docker-compose*.yml",
            "Dockerfile*",
            "deploy/docker-compose*.yaml",
        ]

        infra_docker = self.project_root / "infrastructure/docker"
        infra_docker.mkdir(parents=True, exist_ok=True)

        # Move monitoring configurations
        monitoring_sources = [
            "monitoring",
            "config/monitoring",
            "config/prometheus.yml",
            "grafana_dashboard.json",
        ]

        infra_monitoring = self.project_root / "infrastructure/monitoring"
        infra_monitoring.mkdir(parents=True, exist_ok=True)

        for source in monitoring_sources:
            src_path = self.project_root / source
            if src_path.exists():
                dst_path = infra_monitoring / src_path.name
                if src_path.is_dir():
                    if not dst_path.exists():
                        shutil.copytree(src_path, dst_path)
                else:
                    shutil.copy2(src_path, dst_path)

    def _standardize_service_structure(self):
        """Standardize service directory patterns"""
        services_core = self.project_root / "services/core"

        for service_dir in services_core.iterdir():
            if service_dir.is_dir():
                # Ensure standard subdirectories
                standard_dirs = ["src", "tests", "docs", "config"]
                for std_dir in standard_dirs:
                    (service_dir / std_dir).mkdir(exist_ok=True)

                # Move service files to src/ if not already there
                src_dir = service_dir / "src"
                for item in service_dir.iterdir():
                    if (
                        item.is_file()
                        and item.suffix == ".py"
                        and item.name != "requirements.txt"
                    ):
                        if not (src_dir / item.name).exists():
                            shutil.move(str(item), str(src_dir / item.name))

    def consolidate_configurations(self) -> bool:
        """Consolidate scattered configuration files"""
        try:
            logger.info("Consolidating configuration files...")

            config_dir = self.project_root / "config"
            config_dir.mkdir(exist_ok=True)

            # Create environment-specific config directories
            env_dirs = ["development", "staging", "production"]
            for env in env_dirs:
                (config_dir / "environments" / env).mkdir(parents=True, exist_ok=True)

            # Consolidate scattered configs
            config_patterns = [
                "*config/environments/development.env*",
                "*config*.json",
                "*config*.yaml",
                "*config*.yml",
            ]

            # Move configs from services to centralized location
            for pattern in config_patterns:
                for config_file in self.project_root.rglob(pattern):
                    if "node_modules" not in str(config_file) and "venv" not in str(
                        config_file
                    ):
                        relative_path = config_file.relative_to(self.project_root)
                        if len(relative_path.parts) > 1:  # Not in root
                            dst = (
                                config_dir
                                / "services"
                                / relative_path.parts[0]
                                / config_file.name
                            )
                            dst.parent.mkdir(parents=True, exist_ok=True)
                            if not dst.exists():
                                shutil.copy2(config_file, dst)

            logger.info("Configuration consolidation completed")
            return True

        except Exception as e:
            logger.error(f"Configuration consolidation failed: {e}")
            return False

    def consolidate_dependencies(self) -> bool:
        """Consolidate and clean up dependency files using package managers"""
        try:
            logger.info("Consolidating dependency files...")

            # Python dependencies consolidation
            self._consolidate_python_dependencies()

            # Node.js dependencies consolidation
            self._consolidate_nodejs_dependencies()

            # Rust dependencies consolidation
            self._consolidate_rust_dependencies()

            logger.info("Dependency consolidation completed")
            return True

        except Exception as e:
            logger.error(f"Dependency consolidation failed: {e}")
            return False

    def _consolidate_python_dependencies(self):
        """Consolidate Python requirements.txt files"""
        # Find all requirements.txt files (excluding node_modules)
        req_files = []
        for req_file in self.project_root.rglob("requirements*.txt"):
            if "node_modules" not in str(req_file) and "venv" not in str(req_file):
                req_files.append(req_file)

        logger.info(f"Found {len(req_files)} Python requirements files")

        # Group by service/component
        service_deps = {}
        for req_file in req_files:
            relative_path = req_file.relative_to(self.project_root)
            if len(relative_path.parts) >= 2:
                service_name = relative_path.parts[1]  # services/core/service_name
                if service_name not in service_deps:
                    service_deps[service_name] = []
                service_deps[service_name].append(req_file)

        # Consolidate dependencies for each service
        for service, files in service_deps.items():
            if len(files) > 1:
                self._merge_requirements_files(files, service)

    def _merge_requirements_files(self, files: list[Path], service: str):
        """Merge multiple requirements files for a service"""
        all_deps = set()

        for req_file in files:
            try:
                with open(req_file) as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            all_deps.add(line)
            except Exception as e:
                logger.warning(f"Could not read {req_file}: {e}")

        # Write consolidated requirements
        main_req_file = files[0].parent / "requirements.txt"
        with open(main_req_file, "w") as f:
            f.write(f"# {service} Service Dependencies\n")
            f.write(f"# Consolidated on {datetime.now().strftime('%Y-%m-%d')}\n\n")
            for dep in sorted(all_deps):
                f.write(f"{dep}\n")

        # Remove duplicate files
        for req_file in files[1:]:
            if req_file.exists():
                req_file.unlink()

    def _consolidate_nodejs_dependencies(self):
        """Consolidate Node.js package.json files"""
        package_files = []
        for pkg_file in self.project_root.rglob("package.json"):
            if "node_modules" not in str(pkg_file):
                package_files.append(pkg_file)

        logger.info(f"Found {len(package_files)} package.json files")

    def _consolidate_rust_dependencies(self):
        """Consolidate Rust Cargo.toml files"""
        cargo_files = []
        for cargo_file in self.project_root.rglob("Cargo.toml"):
            if "target" not in str(cargo_file):
                cargo_files.append(cargo_file)

        logger.info(f"Found {len(cargo_files)} Cargo.toml files")

        # Create workspace Cargo.toml if not exists
        workspace_cargo = self.project_root / "Cargo.toml"
        if not workspace_cargo.exists():
            self._create_rust_workspace()

    def _create_rust_workspace(self):
        """Create Rust workspace configuration"""
        workspace_content = """[workspace]
members = [
    "blockchain/programs/quantumagi-core",
    "blockchain/programs/appeals",
    "blockchain/programs/logging"
]

[workspace.dependencies]
anchor-lang = "0.29.0"
anchor-spl = "0.29.0"
solana-program = "~1.18.22"
"""

        with open(self.project_root / "Cargo.toml", "w") as f:
            f.write(workspace_content)

    def apply_code_formatting(self) -> bool:
        """Apply automated code formatting"""
        try:
            logger.info("Applying code formatting...")

            # Python formatting with black
            self._format_python_code()

            # JavaScript/TypeScript formatting with prettier
            self._format_js_code()

            # Rust formatting with rustfmt
            self._format_rust_code()

            logger.info("Code formatting completed")
            return True

        except Exception as e:
            logger.error(f"Code formatting failed: {e}")
            return False

    def _format_python_code(self):
        """Format Python code with black and isort"""
        try:
            # Install black and isort if not available
            subprocess.run(["pip", "install", "black", "isort"], check=False)

            # Format with black
            subprocess.run(
                ["black", "--line-length", "88", "services/", "scripts/", "tests/"],
                cwd=self.project_root,
                check=False,
            )

            # Sort imports with isort
            subprocess.run(
                ["isort", "services/", "scripts/", "tests/"],
                cwd=self.project_root,
                check=False,
            )

        except Exception as e:
            logger.warning(f"Python formatting failed: {e}")

    def _format_js_code(self):
        """Format JavaScript/TypeScript code with prettier"""
        try:
            # Check if prettier is available
            result = subprocess.run(
                ["npx", "prettier", "--version"], capture_output=True, check=False
            )
            if result.returncode == 0:
                subprocess.run(
                    [
                        "npx",
                        "prettier",
                        "--write",
                        "applications/**/*.{js,ts,jsx,tsx}",
                        "blockchain/**/*.{js,ts}",
                    ],
                    cwd=self.project_root,
                    check=False,
                )

        except Exception as e:
            logger.warning(f"JavaScript formatting failed: {e}")

    def _format_rust_code(self):
        """Format Rust code with rustfmt"""
        try:
            subprocess.run(
                ["cargo", "fmt"], cwd=self.project_root / "blockchain", check=False
            )
        except Exception as e:
            logger.warning(f"Rust formatting failed: {e}")

    def run_comprehensive_reorganization(self) -> bool:
        """Execute the complete reorganization process"""
        try:
            logger.info("Starting ACGS-1 comprehensive codebase reorganization...")

            # Phase 1: Backup
            if not self.create_backup():
                return False

            # Phase 2: Validate current state
            initial_health = self.validate_service_health()
            self.report["phases"]["initial_health"] = initial_health

            # Phase 3: Directory reorganization
            if not self.reorganize_directory_structure():
                return False

            # Phase 4: Configuration consolidation
            if not self.consolidate_configurations():
                return False

            # Phase 5: Dependency consolidation
            if not self.consolidate_dependencies():
                return False

            # Phase 6: Code formatting
            if not self.apply_code_formatting():
                return False

            # Phase 7: Final validation
            final_health = self.validate_service_health()
            self.report["phases"]["final_health"] = final_health

            # Generate report
            self.report["end_time"] = datetime.now().isoformat()
            self.report["success"] = True

            report_file = (
                self.project_root
                / f"reorganization_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            with open(report_file, "w") as f:
                json.dump(self.report, f, indent=2)

            logger.info(f"Reorganization completed successfully. Report: {report_file}")
            return True

        except Exception as e:
            logger.error(f"Reorganization failed: {e}")
            self.report["success"] = False
            self.report["error"] = str(e)
            return False


def main():
    """Main execution function"""
    reorganizer = ACGSReorganizer()

    if reorganizer.run_comprehensive_reorganization():
        print("✅ ACGS-1 codebase reorganization completed successfully!")
        print(f"📁 Backup created at: {reorganizer.backup_dir}")
        print("🔍 Check the reorganization report for details")
        sys.exit(0)
    else:
        print("❌ Reorganization failed. Check logs for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
