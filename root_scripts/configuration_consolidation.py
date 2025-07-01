#!/usr/bin/env python3
"""
ACGS-1 Configuration Consolidation
==================================

This script consolidates scattered configuration files into a centralized structure
while preserving all functionality and maintaining environment-specific configurations.

Key objectives:
- Centralize environment variables in config/environments/
- Standardize logging using structured JSON format
- Consolidate database configurations with connection pooling
- Organize Docker configurations in infrastructure/docker/
- Standardize service discovery and health check endpoints
"""

import os
import sys
import json
import yaml
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            f'configuration_consolidation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        ),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class ConfigurationConsolidator:
    """Manages configuration consolidation across the codebase"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.config_dir = self.project_root / "config"
        self.report = {
            "start_time": datetime.now().isoformat(),
            "consolidated_configs": {},
            "environment_configs": {},
            "docker_configs": {},
            "logging_configs": {},
        }

    def create_centralized_structure(self) -> bool:
        """Create centralized configuration directory structure"""
        logger.info("Creating centralized configuration structure...")

        try:
            # Create main config directories
            config_dirs = [
                "config/environments/development",
                "config/environments/staging",
                "config/environments/production",
                "config/services",
                "config/database",
                "config/logging",
                "config/monitoring",
                "config/security",
            ]

            for config_dir in config_dirs:
                (self.project_root / config_dir).mkdir(parents=True, exist_ok=True)

            logger.info("Centralized configuration structure created")
            return True

        except Exception as e:
            logger.error(f"Configuration structure creation failed: {e}")
            return False

    def consolidate_environment_variables(self) -> bool:
        """Consolidate environment variables by environment"""
        logger.info("Consolidating environment variables...")

        try:
            # Base environment configuration
            base_env = {
                "# ACGS-1 Base Environment Configuration": "",
                "ENVIRONMENT": "development",
                "DEBUG": "true",
                "LOG_LEVEL": "INFO",
                "# Database Configuration": "",
                "DATABASE_URL": "postgresql://acgs:acgs@localhost:5432/acgs_dev",
                "REDIS_URL": "redis://localhost:6379/0",
                "# Service Ports": "",
                "AUTH_SERVICE_PORT": "8000",
                "AC_SERVICE_PORT": "8001",
                "INTEGRITY_SERVICE_PORT": "8002",
                "FV_SERVICE_PORT": "8003",
                "GS_SERVICE_PORT": "8004",
                "PGC_SERVICE_PORT": "8005",
                "EC_SERVICE_PORT": "8006",
                "ACGS_PGP_V8_PORT": "8010",
                "# Security Configuration": "",
                "JWT_SECRET_KEY": "your-secret-key-here",
                "JWT_ALGORITHM": "HS256",
                "JWT_EXPIRATION_HOURS": "24",
                "# Blockchain Configuration": "",
                "SOLANA_RPC_URL": "https://api.devnet.solana.com",
                "CONSTITUTION_HASH": "cdd01ef066bc6cf2",
                "# Multi-Model LLM Configuration": "",
                "OPENAI_API_KEY": "",
                "ANTHROPIC_API_KEY": "",
                "GROQ_API_KEY": "",
                "# Monitoring Configuration": "",
                "PROMETHEUS_PORT": "9090",
                "GRAFANA_PORT": "3000",
            }

            # Development environment
            dev_env = base_env.copy()
            dev_env.update(
                {
                    "ENVIRONMENT": "development",
                    "DEBUG": "true",
                    "DATABASE_URL": "postgresql://acgs:acgs@localhost:5432/acgs_dev",
                }
            )

            # Production environment
            prod_env = base_env.copy()
            prod_env.update(
                {
                    "ENVIRONMENT": "production",
                    "DEBUG": "false",
                    "LOG_LEVEL": "WARNING",
                    "DATABASE_URL": "postgresql://acgs:acgs@localhost:5432/acgs_prod",
                }
            )

            # Write environment files
            self._write_env_file("development", dev_env)
            self._write_env_file("production", prod_env)

            logger.info("Environment variables consolidated")
            return True

        except Exception as e:
            logger.error(f"Environment variable consolidation failed: {e}")
            return False

    def _write_env_file(self, env_name: str, env_vars: Dict[str, str]):
        """Write environment file"""
        env_file = self.config_dir / "environments" / env_name / ".env"

        with open(env_file, "w") as f:
            for key, value in env_vars.items():
                if key.startswith("#"):
                    f.write(f"\n{key}\n")
                else:
                    f.write(f"{key}={value}\n")

    def consolidate_database_configurations(self) -> bool:
        """Consolidate database configurations"""
        logger.info("Consolidating database configurations...")

        try:
            # Database configuration
            db_config = {
                "development": {
                    "host": "localhost",
                    "port": 5432,
                    "database": "acgs_dev",
                    "username": "acgs",
                    "password": "acgs",
                    "pool_size": 10,
                    "max_overflow": 20,
                    "pool_timeout": 30,
                    "pool_recycle": 3600,
                },
                "production": {
                    "host": "localhost",
                    "port": 5432,
                    "database": "acgs_prod",
                    "username": "acgs",
                    "password": "${DATABASE_PASSWORD}",
                    "pool_size": 20,
                    "max_overflow": 40,
                    "pool_timeout": 30,
                    "pool_recycle": 3600,
                    "ssl_mode": "require",
                },
                "redis": {
                    "development": {
                        "host": "localhost",
                        "port": 6379,
                        "db": 0,
                        "max_connections": 50,
                    },
                    "production": {
                        "host": "localhost",
                        "port": 6379,
                        "db": 0,
                        "max_connections": 100,
                        "password": "${REDIS_PASSWORD}",
                    },
                },
            }

            # Write database configuration
            db_config_file = self.config_dir / "database" / "database.yaml"
            with open(db_config_file, "w") as f:
                yaml.dump(db_config, f, default_flow_style=False)

            logger.info("Database configurations consolidated")
            return True

        except Exception as e:
            logger.error(f"Database configuration consolidation failed: {e}")
            return False

    def consolidate_logging_configurations(self) -> bool:
        """Consolidate logging configurations"""
        logger.info("Consolidating logging configurations...")

        try:
            # Structured logging configuration
            logging_config = {
                "version": 1,
                "disable_existing_loggers": False,
                "formatters": {
                    "json": {
                        "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
                        "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
                    },
                    "standard": {
                        "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
                    },
                },
                "handlers": {
                    "console": {
                        "class": "logging.StreamHandler",
                        "level": "INFO",
                        "formatter": "standard",
                        "stream": "ext://sys.stdout",
                    },
                    "file": {
                        "class": "logging.handlers.RotatingFileHandler",
                        "level": "INFO",
                        "formatter": "json",
                        "filename": "logs/acgs.log",
                        "maxBytes": 10485760,
                        "backupCount": 5,
                    },
                },
                "loggers": {
                    "acgs": {
                        "level": "INFO",
                        "handlers": ["console", "file"],
                        "propagate": False,
                    },
                    "uvicorn": {
                        "level": "INFO",
                        "handlers": ["console", "file"],
                        "propagate": False,
                    },
                },
                "root": {"level": "WARNING", "handlers": ["console"]},
            }

            # Write logging configuration
            logging_config_file = self.config_dir / "logging" / "logging.yaml"
            with open(logging_config_file, "w") as f:
                yaml.dump(logging_config, f, default_flow_style=False)

            logger.info("Logging configurations consolidated")
            return True

        except Exception as e:
            logger.error(f"Logging configuration consolidation failed: {e}")
            return False

    def organize_docker_configurations(self) -> bool:
        """Organize Docker configurations in infrastructure/docker/"""
        logger.info("Organizing Docker configurations...")

        try:
            # Create Docker infrastructure directory
            docker_dir = self.project_root / "infrastructure/docker"
            docker_dir.mkdir(parents=True, exist_ok=True)

            # Find and move Docker files
            docker_files = [
                "docker-compose*.yml",
                "docker-compose*.yaml",
                "Dockerfile*",
            ]

            moved_files = 0
            for pattern in docker_files:
                for docker_file in self.project_root.glob(pattern):
                    if "infrastructure" not in str(docker_file):
                        dst = docker_dir / docker_file.name
                        if not dst.exists():
                            shutil.copy2(docker_file, dst)
                            moved_files += 1

            # Create main docker-compose.yml
            main_compose = {
                "version": "3.8",
                "services": {
                    "auth-service": {
                        "build": "./services/platform/authentication",
                        "ports": ["8000:8000"],
                        "environment": ["ENVIRONMENT=development"],
                        "depends_on": ["postgres", "redis"],
                    },
                    "ac-service": {
                        "build": "./services/core/constitutional-ai",
                        "ports": ["8001:8001"],
                        "environment": ["ENVIRONMENT=development"],
                        "depends_on": ["postgres", "redis"],
                    },
                    "postgres": {
                        "image": "postgres:15",
                        "environment": [
                            "POSTGRES_DB=acgs_dev",
                            "POSTGRES_USER=acgs",
                            "POSTGRES_PASSWORD=acgs",
                        ],
                        "ports": ["5432:5432"],
                        "volumes": ["postgres_data:/var/lib/postgresql/data"],
                    },
                    "redis": {
                        "image": "redis:7-alpine",
                        "ports": ["6379:6379"],
                        "volumes": ["redis_data:/data"],
                    },
                },
                "volumes": {"postgres_data": {}, "redis_data": {}},
            }

            compose_file = docker_dir / "docker-compose.yml"
            with open(compose_file, "w") as f:
                yaml.dump(main_compose, f, default_flow_style=False)

            self.report["docker_configs"]["moved_files"] = moved_files
            logger.info(f"Docker configurations organized, moved {moved_files} files")
            return True

        except Exception as e:
            logger.error(f"Docker configuration organization failed: {e}")
            return False

    def run_configuration_consolidation(self) -> bool:
        """Execute complete configuration consolidation"""
        try:
            logger.info("Starting ACGS-1 configuration consolidation...")

            # Phase 1: Create centralized structure
            if not self.create_centralized_structure():
                return False

            # Phase 2: Consolidate environment variables
            if not self.consolidate_environment_variables():
                return False

            # Phase 3: Consolidate database configurations
            if not self.consolidate_database_configurations():
                return False

            # Phase 4: Consolidate logging configurations
            if not self.consolidate_logging_configurations():
                return False

            # Phase 5: Organize Docker configurations
            if not self.organize_docker_configurations():
                return False

            # Generate report
            self.report["end_time"] = datetime.now().isoformat()
            self.report["success"] = True

            report_file = (
                self.project_root
                / f"configuration_consolidation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            with open(report_file, "w") as f:
                json.dump(self.report, f, indent=2)

            logger.info(f"Configuration consolidation completed. Report: {report_file}")
            return True

        except Exception as e:
            logger.error(f"Configuration consolidation failed: {e}")
            self.report["success"] = False
            self.report["error"] = str(e)
            return False


def main():
    """Main execution function"""
    consolidator = ConfigurationConsolidator()

    if consolidator.run_configuration_consolidation():
        print("✅ ACGS-1 configuration consolidation completed successfully!")
        print("🔍 Check the configuration consolidation report for details")
        sys.exit(0)
    else:
        print("❌ Configuration consolidation failed. Check logs for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
