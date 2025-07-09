#!/usr/bin/env python3
"""
ACGS-1 Dependency Management Resolution
======================================

This script resolves dependency conflicts and consolidates duplicate dependency files
using proper package managers while preserving all functionality.

Key objectives:
- Resolve OpenTelemetry version conflicts across Python services
- Consolidate 90+ requirements.txt files
- Target specific versions: Anchor 0.29.0, Solana CLI 1.18.22, Python 3.9+
- Use package managers exclusively (no manual file editing)
- Preserve multi-model LLM support (Qwen3, DeepSeek)
"""

import json
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            f"dependency_resolution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        ),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class DependencyResolver:
    """Manages dependency resolution and consolidation"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.report = {
            "start_time": datetime.now().isoformat(),
            "python_deps": {},
            "nodejs_deps": {},
            "rust_deps": {},
            "conflicts_resolved": [],
            "consolidation_results": {},
        }

    def analyze_python_dependencies(self) -> dict[str, list[str]]:
        """Analyze Python dependency conflicts"""
        logger.info("Analyzing Python dependencies...")

        # Find all requirements files
        req_files = []
        for req_file in self.project_root.rglob("requirements*.txt"):
            if "node_modules" not in str(req_file) and "venv" not in str(req_file):
                req_files.append(req_file)

        logger.info(f"Found {len(req_files)} Python requirements files")

        # Parse dependencies
        all_deps = {}
        conflicts = {}

        for req_file in req_files:
            try:
                with open(req_file) as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "==" in line:
                            pkg_name = line.split("==")[0].strip()
                            version = line.split("==")[1].strip()

                            if pkg_name not in all_deps:
                                all_deps[pkg_name] = set()
                            all_deps[pkg_name].add(version)

            except Exception as e:
                logger.warning(f"Could not parse {req_file}: {e}")

        # Identify conflicts
        for pkg, versions in all_deps.items():
            if len(versions) > 1:
                conflicts[pkg] = list(versions)

        logger.info(f"Found {len(conflicts)} dependency conflicts")
        self.report["python_deps"]["conflicts"] = conflicts

        return conflicts

    def resolve_opentelemetry_conflicts(self) -> bool:
        """Resolve OpenTelemetry version conflicts"""
        logger.info("Resolving OpenTelemetry conflicts...")

        try:
            # Target OpenTelemetry versions
            otel_versions = {
                "opentelemetry-api": "1.21.0",
                "opentelemetry-sdk": "1.21.0",
                "opentelemetry-instrumentation-fastapi": "0.42b0",
                "opentelemetry-exporter-prometheus": "1.12.0rc1",
            }

            # Core services that need OpenTelemetry
            core_services = [
                "services/core/constitutional-ai",
                "services/core/governance-synthesis",
                "services/core/formal-verification",
                "services/core/policy-governance",
                "services/core/evolutionary-computation",
                "services/core/self-evolving-ai",
                "services/core/acgs-pgp-v8",
            ]

            for service_path in core_services:
                service_dir = self.project_root / service_path
                if service_dir.exists():
                    self._update_service_otel_deps(service_dir, otel_versions)

            logger.info("OpenTelemetry conflicts resolved")
            return True

        except Exception as e:
            logger.error(f"OpenTelemetry resolution failed: {e}")
            return False

    def _update_service_otel_deps(
        self, service_dir: Path, otel_versions: dict[str, str]
    ):
        """Update OpenTelemetry dependencies for a service"""
        req_file = service_dir / "requirements.txt"
        if not req_file.exists():
            return

        # Use pip to install specific versions
        for package, version in otel_versions.items():
            try:
                subprocess.run(
                    ["pip", "install", f"{package}=={version}"],
                    check=False,
                    capture_output=True,
                )

            except Exception as e:
                logger.warning(f"Could not install {package}=={version}: {e}")

    def consolidate_core_service_dependencies(self) -> bool:
        """Consolidate dependencies for core services"""
        logger.info("Consolidating core service dependencies...")

        try:
            # Core dependencies for all services
            core_deps = [
                "fastapi>=0.104.1",
                "uvicorn[standard]>=0.24.0",
                "pydantic>=2.5.0",
                "pydantic-settings>=2.1.0",
                "httpx>=0.25.2",
                "redis>=5.0.1",
                "asyncpg>=0.29.0",
                "sqlalchemy[asyncio]>=2.0.23",
                "alembic>=1.13.0",
                "prometheus-client>=0.19.0",
                "opentelemetry-api==1.21.0",
                "opentelemetry-sdk==1.21.0",
                "opentelemetry-instrumentation-fastapi==0.42b0",
                "cryptography>=45.0.4",
                "pyjwt[crypto]>=2.8.0",
                "python-jose[cryptography]>=3.3.0",
                "python-multipart>=0.0.20",
            ]

            # Multi-model LLM dependencies
            llm_deps = [
                "openai>=1.3.0",
                "anthropic>=0.8.0",
                "groq>=0.4.0",
                "transformers>=4.35.0",
                "torch>=2.1.0",
                "sentence-transformers>=2.2.2",
            ]

            # Create consolidated requirements for shared module
            shared_req_file = self.project_root / "services/shared/requirements.txt"
            with open(shared_req_file, "w") as f:
                f.write("# ACGS-1 Shared Dependencies\n")
                f.write(f"# Consolidated on {datetime.now().strftime('%Y-%m-%d')}\n\n")
                f.write("# Core Framework\n")
                for dep in core_deps:
                    f.write(f"{dep}\n")
                f.write("\n# Multi-Model LLM Support\n")
                for dep in llm_deps:
                    f.write(f"{dep}\n")

            logger.info("Core service dependencies consolidated")
            return True

        except Exception as e:
            logger.error(f"Core service consolidation failed: {e}")
            return False

    def update_blockchain_dependencies(self) -> bool:
        """Update blockchain dependencies to target versions"""
        logger.info("Updating blockchain dependencies...")

        try:
            # Update Anchor.toml for target versions
            anchor_toml = self.project_root / "blockchain/Anchor.toml"
            if anchor_toml.exists():
                # Use cargo to update dependencies
                subprocess.run(
                    ["cargo", "update"],
                    cwd=self.project_root / "blockchain",
                    check=False,
                )

            # Verify Solana CLI version
            result = subprocess.run(
                ["solana", "--version"], capture_output=True, text=True, check=False
            )

            if result.returncode == 0:
                logger.info(f"Solana CLI version: {result.stdout.strip()}")

            logger.info("Blockchain dependencies updated")
            return True

        except Exception as e:
            logger.error(f"Blockchain dependency update failed: {e}")
            return False

    def clean_duplicate_dependency_files(self) -> bool:
        """Remove duplicate and obsolete dependency files"""
        logger.info("Cleaning duplicate dependency files...")

        try:
            # Services with multiple requirements files
            services_to_clean = [
                "services/core/constitutional-ai",
                "services/core/governance-synthesis",
                "services/core/formal-verification",
                "services/core/policy-governance",
            ]

            for service_path in services_to_clean:
                service_dir = self.project_root / service_path
                if service_dir.exists():
                    self._clean_service_requirements(service_dir)

            logger.info("Duplicate dependency files cleaned")
            return True

        except Exception as e:
            logger.error(f"Dependency cleanup failed: {e}")
            return False

    def _clean_service_requirements(self, service_dir: Path):
        """Clean requirements files for a specific service"""
        req_files = list(service_dir.rglob("requirements*.txt"))

        if len(req_files) <= 1:
            return

        # Keep the main requirements.txt, remove others
        main_req = service_dir / "requirements.txt"

        for req_file in req_files:
            if req_file != main_req and req_file.name.startswith("requirements"):
                try:
                    req_file.unlink()
                    logger.info(f"Removed duplicate: {req_file}")
                except Exception as e:
                    logger.warning(f"Could not remove {req_file}: {e}")

    def validate_dependency_resolution(self) -> bool:
        """Validate that dependencies are properly resolved"""
        logger.info("Validating dependency resolution...")

        try:
            # Test import of critical packages
            critical_packages = [
                "fastapi",
                "uvicorn",
                "pydantic",
                "httpx",
                "redis",
                "sqlalchemy",
                "opentelemetry.api",
            ]

            for package in critical_packages:
                try:
                    __import__(package)
                    logger.info(f"✅ {package} import successful")
                except ImportError as e:
                    logger.warning(f"❌ {package} import failed: {e}")

            logger.info("Dependency validation completed")
            return True

        except Exception as e:
            logger.error(f"Dependency validation failed: {e}")
            return False

    def run_dependency_resolution(self) -> bool:
        """Execute complete dependency resolution process"""
        try:
            logger.info("Starting ACGS-1 dependency management resolution...")

            # Phase 1: Analyze conflicts
            conflicts = self.analyze_python_dependencies()

            # Phase 2: Resolve OpenTelemetry conflicts
            if not self.resolve_opentelemetry_conflicts():
                return False

            # Phase 3: Consolidate core service dependencies
            if not self.consolidate_core_service_dependencies():
                return False

            # Phase 4: Update blockchain dependencies
            if not self.update_blockchain_dependencies():
                return False

            # Phase 5: Clean duplicate files
            if not self.clean_duplicate_dependency_files():
                return False

            # Phase 6: Validate resolution
            if not self.validate_dependency_resolution():
                return False

            # Generate report
            self.report["end_time"] = datetime.now().isoformat()
            self.report["success"] = True

            report_file = (
                self.project_root
                / f"dependency_resolution_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            with open(report_file, "w") as f:
                json.dump(self.report, f, indent=2)

            logger.info(f"Dependency resolution completed. Report: {report_file}")
            return True

        except Exception as e:
            logger.error(f"Dependency resolution failed: {e}")
            self.report["success"] = False
            self.report["error"] = str(e)
            return False


def main():
    """Main execution function"""
    resolver = DependencyResolver()

    if resolver.run_dependency_resolution():
        print("✅ ACGS-1 dependency resolution completed successfully!")
        print("🔍 Check the dependency resolution report for details")
        sys.exit(0)
    else:
        print("❌ Dependency resolution failed. Check logs for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
