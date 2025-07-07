#!/usr/bin/env python3
"""
ACGS Production Environment Cleanup Script
Constitutional Hash: cdd01ef066bc6cf2

This script prepares the ACGS codebase for production deployment by:
1. Removing development artifacts and temporary files
2. Cleaning up test-only configurations and debug code
3. Ensuring constitutional compliance across all files
4. Creating production-specific environment configurations
5. Validating production readiness

Performance Targets: P99 <5ms, >100 RPS, >85% cache hit rate
"""

import glob
import json
import logging
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Set

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Constitutional compliance hash
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class ProductionCleanup:
    """Production environment cleanup orchestrator."""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.cleanup_report = {
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "timestamp": None,
            "files_removed": [],
            "directories_removed": [],
            "configurations_updated": [],
            "total_size_freed": 0,
            "production_ready": False,
        }

        # Development artifacts to remove
        self.dev_artifacts = {
            # Python artifacts
            "__pycache__",
            ".pytest_cache",
            ".mypy_cache",
            ".ruff_cache",
            ".coverage",
            "htmlcov",
            ".tox",
            ".nox",
            # Node.js artifacts
            "node_modules",
            ".next",
            ".nuxt",
            ".parcel-cache",
            # Build artifacts
            "build",
            "dist",
            "target/debug",
            "target/release",
            # IDE artifacts
            ".vscode",
            ".idea",
            "*.code-workspace",
            # Temporary files
            "temp",
            "tmp",
            ".tmp",
            # Log files (development)
            "*.log",
            "logs/*.log",
            # Backup files
            "backup_*",
            "*.backup",
            "*.bak",
            # Test databases
            "*.db",
            "*.sqlite3",
            "test_*.db",
            # Process ID files
            "pids",
            "*.pid",
            # Cache directories
            ".cache",
            "cache",
            # Report files (development)
            "*_report_*.json",
            "*_results_*.json",
            "test_reports",
            "validation_reports",
            "audit_reports",
        }

        # Files with development-specific configurations
        self.dev_config_patterns = [
            "development_password",
            "debug=True",
            "DEBUG=true",
            "localhost:8000",
            "127.0.0.1",
            "test_database",
            "dev_mode",
            "DEVELOPMENT",
        ]

        # Production configuration templates
        self.production_configs = {
            "database": {
                "host": "${POSTGRESQL_HOST}",
                "port": 5439,
                "database": "${POSTGRESQL_DATABASE}",
                "user": "${POSTGRESQL_USER}",
                "password": "${POSTGRESQL_PASSWORD}",
                "pool_size": 20,
                "max_overflow": 10,
            },
            "redis": {
                "host": "${REDIS_HOST}",
                "port": 6389,
                "password": "${REDIS_PASSWORD}",
                "db": 0,
            },
            "services": {
                "auth_service": {"port": 8016},
                "constitutional_ai": {"port": 8001},
                "coordinator": {"port": 8008},
                "blackboard": {"port": 8010},
            },
        }

    def remove_development_artifacts(self) -> None:
        """Remove development artifacts and temporary files."""
        logger.info("Removing development artifacts...")

        removed_count = 0
        size_freed = 0

        for artifact_pattern in self.dev_artifacts:
            # Handle glob patterns
            if "*" in artifact_pattern:
                matches = list(self.project_root.glob(f"**/{artifact_pattern}"))
                for match in matches:
                    if match.exists():
                        size_freed += self._get_size(match)
                        if match.is_dir():
                            shutil.rmtree(match)
                            self.cleanup_report["directories_removed"].append(
                                str(match)
                            )
                        else:
                            match.unlink()
                            self.cleanup_report["files_removed"].append(str(match))
                        removed_count += 1
            else:
                # Handle directory patterns
                matches = list(self.project_root.glob(f"**/{artifact_pattern}"))
                for match in matches:
                    if match.exists() and match.is_dir():
                        size_freed += self._get_size(match)
                        shutil.rmtree(match)
                        self.cleanup_report["directories_removed"].append(str(match))
                        removed_count += 1

        self.cleanup_report["total_size_freed"] += size_freed
        logger.info(
            f"Removed {removed_count} development artifacts, freed {size_freed / 1024 / 1024:.2f} MB"
        )

    def update_production_configurations(self) -> None:
        """Update configuration files for production environment."""
        logger.info("Updating production configurations...")

        config_files = [
            "config/environments/production.yaml",
            "config/environments/production.json",
            "docker-compose.production.yml",
            ".env.production",
        ]

        for config_file in config_files:
            config_path = self.project_root / config_file
            if config_path.exists():
                self._update_config_file(config_path)
                self.cleanup_report["configurations_updated"].append(str(config_path))

    def _update_config_file(self, config_path: Path) -> None:
        """Update a specific configuration file for production."""
        try:
            content = config_path.read_text()

            # Replace development-specific values
            for dev_pattern in self.dev_config_patterns:
                if dev_pattern in content:
                    if "password" in dev_pattern.lower():
                        content = content.replace(dev_pattern, "${PRODUCTION_PASSWORD}")
                    elif "debug" in dev_pattern.lower():
                        content = content.replace(dev_pattern, "false")
                    elif "localhost" in dev_pattern or "127.0.0.1" in dev_pattern:
                        content = content.replace(dev_pattern, "${PRODUCTION_HOST}")
                    elif "test_" in dev_pattern:
                        content = content.replace(dev_pattern, "production_")

            # Ensure constitutional hash is present
            if CONSTITUTIONAL_HASH not in content:
                if config_path.suffix in [".yaml", ".yml"]:
                    content = f"# Constitutional Hash: {CONSTITUTIONAL_HASH}\n{content}"
                elif config_path.suffix == ".json":
                    # Add to JSON structure
                    try:
                        data = json.loads(content)
                        data["constitutional_hash"] = CONSTITUTIONAL_HASH
                        content = json.dumps(data, indent=2)
                    except json.JSONDecodeError:
                        pass

            config_path.write_text(content)
            logger.info(f"Updated production configuration: {config_path}")

        except Exception as e:
            logger.error(f"Failed to update config file {config_path}: {e}")

    def create_production_environment_files(self) -> None:
        """Create production-specific environment configuration files."""
        logger.info("Creating production environment files...")

        # Create production environment file
        env_production = self.project_root / ".env.production"
        env_content = f"""# ACGS Production Environment Configuration
# Constitutional Hash: {CONSTITUTIONAL_HASH}

# Performance Targets
ACGS_PERFORMANCE_P99_TARGET=5
ACGS_PERFORMANCE_RPS_TARGET=100
ACGS_CACHE_HIT_RATE_TARGET=85

# Database Configuration (PostgreSQL - Port 5439)
POSTGRESQL_HOST=${{POSTGRESQL_HOST:-localhost}}
POSTGRESQL_PORT=5439
POSTGRESQL_DATABASE=${{POSTGRESQL_DATABASE:-acgs}}
POSTGRESQL_USER=${{POSTGRESQL_USER:-acgs_user}}
POSTGRESQL_PASSWORD=${{POSTGRESQL_PASSWORD}}
POSTGRESQL_POOL_SIZE=20
POSTGRESQL_MAX_OVERFLOW=10

# Redis Configuration (Port 6389)
REDIS_HOST=${{REDIS_HOST:-localhost}}
REDIS_PORT=6389
REDIS_PASSWORD=${{REDIS_PASSWORD}}
REDIS_DB=0

# Service Ports
AUTH_SERVICE_PORT=8016
CONSTITUTIONAL_AI_PORT=8001
COORDINATOR_PORT=8008
BLACKBOARD_PORT=8010

# Production Settings
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
ENABLE_METRICS=true
ENABLE_TRACING=true

# Constitutional Compliance
CONSTITUTIONAL_HASH={CONSTITUTIONAL_HASH}
CONSTITUTIONAL_VALIDATION_ENABLED=true
"""

        env_production.write_text(env_content)
        self.cleanup_report["configurations_updated"].append(str(env_production))

        # Create production Docker Compose override
        docker_compose_prod = self.project_root / "docker-compose.production.yml"
        compose_content = f"""# ACGS Production Docker Compose Configuration
# Constitutional Hash: {CONSTITUTIONAL_HASH}

version: '3.8'

services:
  postgres:
    ports:
      - "5439:5432"
    environment:
      POSTGRES_USER: ${{POSTGRESQL_USER}}
      POSTGRES_PASSWORD: ${{POSTGRESQL_PASSWORD}}
      POSTGRES_DB: ${{POSTGRESQL_DATABASE}}
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'

  redis:
    ports:
      - "6389:6379"
    environment:
      REDIS_PASSWORD: ${{REDIS_PASSWORD}}
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'

  auth-service:
    ports:
      - "8016:8016"
    environment:
      CONSTITUTIONAL_HASH: {CONSTITUTIONAL_HASH}
      ENVIRONMENT: production
      DEBUG: false

  constitutional-ai-service:
    ports:
      - "8001:8001"
    environment:
      CONSTITUTIONAL_HASH: {CONSTITUTIONAL_HASH}
      ENVIRONMENT: production
      DEBUG: false

networks:
  default:
    name: acgs_production_network
"""

        docker_compose_prod.write_text(compose_content)
        self.cleanup_report["configurations_updated"].append(str(docker_compose_prod))

    def validate_constitutional_compliance(self) -> bool:
        """Validate constitutional compliance across all production files."""
        logger.info("Validating constitutional compliance...")

        non_compliant_files = []

        # Check Python files
        python_files = list(self.project_root.glob("**/*.py"))
        for py_file in python_files:
            if "test" in str(py_file) or "__pycache__" in str(py_file):
                continue

            try:
                content = py_file.read_text()
                if CONSTITUTIONAL_HASH not in content:
                    non_compliant_files.append(str(py_file))
            except Exception:
                continue

        # Check configuration files
        config_files = (
            list(self.project_root.glob("**/*.yaml"))
            + list(self.project_root.glob("**/*.yml"))
            + list(self.project_root.glob("**/*.json"))
        )

        for config_file in config_files:
            if "test" in str(config_file) or "node_modules" in str(config_file):
                continue

            try:
                content = config_file.read_text()
                if CONSTITUTIONAL_HASH not in content:
                    non_compliant_files.append(str(config_file))
            except Exception:
                continue

        if non_compliant_files:
            logger.warning(f"Found {len(non_compliant_files)} non-compliant files")
            return False

        logger.info("Constitutional compliance validation passed")
        return True

    def _get_size(self, path: Path) -> int:
        """Get size of file or directory in bytes."""
        if path.is_file():
            return path.stat().st_size
        elif path.is_dir():
            total = 0
            try:
                for item in path.rglob("*"):
                    if item.is_file():
                        total += item.stat().st_size
            except (PermissionError, OSError):
                pass
            return total
        return 0

    def generate_cleanup_report(self) -> None:
        """Generate comprehensive cleanup report."""
        import datetime

        self.cleanup_report["timestamp"] = datetime.datetime.now().isoformat()
        self.cleanup_report["production_ready"] = (
            self.validate_constitutional_compliance()
        )

        report_path = self.project_root / "production_cleanup_report.json"
        with open(report_path, "w") as f:
            json.dump(self.cleanup_report, f, indent=2)

        logger.info(f"Cleanup report generated: {report_path}")

    def run_production_cleanup(self) -> bool:
        """Execute complete production cleanup process."""
        logger.info(
            f"Starting ACGS production cleanup (Constitutional Hash: {CONSTITUTIONAL_HASH})"
        )

        try:
            # Step 1: Remove development artifacts
            self.remove_development_artifacts()

            # Step 2: Update production configurations
            self.update_production_configurations()

            # Step 3: Create production environment files
            self.create_production_environment_files()

            # Step 4: Validate constitutional compliance
            compliance_valid = self.validate_constitutional_compliance()

            # Step 5: Generate cleanup report
            self.generate_cleanup_report()

            if compliance_valid:
                logger.info("✅ Production cleanup completed successfully!")
                logger.info("🎯 ACGS is ready for production deployment!")
                return True
            else:
                logger.warning("⚠️ Production cleanup completed with compliance issues")
                return False

        except Exception as e:
            logger.error(f"Production cleanup failed: {e}")
            return False


def main():
    """Main entry point."""
    cleanup = ProductionCleanup()
    success = cleanup.run_production_cleanup()
    exit(0 if success else 1)


if __name__ == "__main__":
    main()
