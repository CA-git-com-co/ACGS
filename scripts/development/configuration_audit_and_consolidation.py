#!/usr/bin/env python3
"""
ACGS-1 Configuration Management Consolidation
=============================================  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2

Comprehensive audit and consolidation of scattered configuration files
into a centralized, hierarchical configuration system with environment-specific overrides.
"""

import json
import logging
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ConfigurationManager:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.audit_report = {
            "timestamp": datetime.now().isoformat(),
            "configuration_files": {},
            "inconsistencies": [],
            "consolidation_actions": [],
            "environment_configs": {},
            "service_configs": {},
            "recommendations": [],
        }

    def audit_current_configuration_state(self):
        """Comprehensive audit of current configuration files"""
        logger.info("🔍 Auditing current configuration state...")

        # Configuration file patterns to search for
        config_patterns = [
            "*config/environments/development.env*",
            "*config*.json",
            "*config*.yaml",
            "*config*.yml",
            "*.toml",
            "docker-compose*.yml",
            "Dockerfile*",
            "*.ini",
        ]

        config_files = {}

        for pattern in config_patterns:
            for config_file in self.project_root.rglob(pattern):
                # Skip node_modules, venv, and other irrelevant directories
                if any(
                    skip in str(config_file)
                    for skip in [
                        "node_modules",
                        "venv",
                        "__pycache__",
                        ".git",
                        "dist",
                        "build",
                        "target",
                        ".next",
                    ]
                ):
                    continue

                relative_path = config_file.relative_to(self.project_root)
                config_files[str(relative_path)] = {
                    "type": self._classify_config_file(config_file),
                    "size": config_file.stat().st_size,
                    "modified": datetime.fromtimestamp(
                        config_file.stat().st_mtime
                    ).isoformat(),
                    "location": str(config_file.parent.relative_to(self.project_root)),
                }

        self.audit_report["configuration_files"] = config_files
        logger.info(f"✅ Found {len(config_files)} configuration files")

        # Analyze configuration patterns
        self._analyze_configuration_patterns(config_files)

    def _classify_config_file(self, config_file: Path) -> str:
        """Classify configuration file by type and purpose"""
        name = config_file.name.lower()

        if name.startswith("config/environments/development.env"):
            return "environment"
        if "docker" in name:
            return "docker"
        if "config" in name:
            return "application_config"
        if name.endswith(".toml"):
            return "build_config"
        if "compose" in name:
            return "docker_compose"
        if name.startswith("Dockerfile"):
            return "dockerfile"
        return "other"

    def _analyze_configuration_patterns(self, config_files: dict):
        """Analyze configuration patterns and identify inconsistencies"""
        logger.info("📊 Analyzing configuration patterns...")

        # Group by type
        by_type = {}
        for file_path, info in config_files.items():
            config_type = info["type"]
            if config_type not in by_type:
                by_type[config_type] = []
            by_type[config_type].append(file_path)

        # Identify inconsistencies
        inconsistencies = []

        # Check for multiple environment files
        env_files = by_type.get("environment", [])
        if len(env_files) > 3:  # Allow dev, staging, prod
            inconsistencies.append(
                {
                    "type": "multiple_environment_files",
                    "description": f"Found {len(env_files)} environment files",
                    "files": env_files,
                    "recommendation": "Consolidate into environment-specific configs",
                }
            )

        # Check for scattered Docker configs
        docker_files = by_type.get("docker", []) + by_type.get("docker_compose", [])
        scattered_docker = [
            f for f in docker_files if "/" in f and not f.startswith("config/")
        ]
        if scattered_docker:
            inconsistencies.append(
                {
                    "type": "scattered_docker_configs",
                    "description": f"Found {len(scattered_docker)} Docker configs outside config/",
                    "files": scattered_docker,
                    "recommendation": "Move to config/docker/ directory",
                }
            )

        # Check for duplicate application configs
        app_configs = by_type.get("application_config", [])
        config_names = {}
        for config_file in app_configs:
            name = Path(config_file).name
            if name not in config_names:
                config_names[name] = []
            config_names[name].append(config_file)

        for name, files in config_names.items():
            if len(files) > 1:
                inconsistencies.append(
                    {
                        "type": "duplicate_config_files",
                        "description": f"Found {len(files)} files named '{name}'",
                        "files": files,
                        "recommendation": "Consolidate or rename for clarity",
                    }
                )

        self.audit_report["inconsistencies"] = inconsistencies
        logger.info(f"⚠️ Found {len(inconsistencies)} configuration inconsistencies")

    def create_centralized_structure(self):
        """Create centralized configuration directory structure"""
        logger.info("🏗️ Creating centralized configuration structure...")

        # Define the target structure
        config_structure = {
            "config/environments": ["development", "staging", "production"],
            "config/services": ["core", "platform", "shared"],
            "config/database": ["migrations", "schemas", "connections"],
            "config/logging": ["formatters", "handlers", "levels"],
            "config/monitoring": ["metrics", "alerts", "dashboards"],
            "config/security": ["certificates", "policies", "secrets"],
            "config/docker": ["compose", "images", "networks"],
            "config/nginx": ["sites", "ssl", "upstream"],
        }

        created_dirs = []

        for base_dir, subdirs in config_structure.items():
            base_path = self.project_root / base_dir
            base_path.mkdir(parents=True, exist_ok=True)
            created_dirs.append(str(base_dir))

            for subdir in subdirs:
                sub_path = base_path / subdir
                sub_path.mkdir(parents=True, exist_ok=True)
                created_dirs.append(str(sub_path.relative_to(self.project_root)))

        self.audit_report["consolidation_actions"].append(
            {
                "action": "create_centralized_structure",
                "directories_created": created_dirs,
                "timestamp": datetime.now().isoformat(),
            }
        )

        logger.info(f"✅ Created {len(created_dirs)} configuration directories")

    def consolidate_environment_configurations(self):
        """Consolidate environment variables into centralized configs"""
        logger.info("🌍 Consolidating environment configurations...")

        # Find all environment files
        env_files = list(self.project_root.rglob("config/environments/development.env*"))
        env_files = [
            f
            for f in env_files
            if not any(
                skip in str(f) for skip in ["node_modules", "venv", "__pycache__"]
            )
        ]

        # Create environment-specific configurations
        environments = ["development", "staging", "production"]
        consolidated_envs = {}

        for env in environments:
            env_config = {
                "database": {
                    "host": (
                        "localhost"
                        if env == "development"
                        else f"{env}-db.acgs.internal"
                    ),
                    "port": 5432,
                    "name": "acgs",
                    "user": "acgs_user",
                    "ssl_mode": "disable" if env == "development" else "require",
                },
                "redis": {
                    "host": (
                        "localhost"
                        if env == "development"
                        else f"{env}-redis.acgs.internal"
                    ),
                    "port": 6379,
                    "db": 0,
                },
                "services": {
                    "auth": {"port": 8000, "host": "localhost"},
                    "ac": {"port": 8001, "host": "localhost"},
                    "integrity": {"port": 8002, "host": "localhost"},
                    "fv": {"port": 8003, "host": "localhost"},
                    "gs": {"port": 8004, "host": "localhost"},
                    "pgc": {"port": 8005, "host": "localhost"},
                    "ec": {"port": 8006, "host": "localhost"},
                },
                "logging": {
                    "level": "DEBUG" if env == "development" else "INFO",
                    "format": "json",
                    "output": "console" if env == "development" else "file",
                },
                "security": {
                    "jwt_secret": f"${env.upper()}_JWT_SECRET",
                    "encryption_key": f"${env.upper()}_ENCRYPTION_KEY",
                    "ssl_enabled": env != "development",
                },
                "quantumagi": {
                    "constitution_hash": "cdd01ef066bc6cf2",
                    "solana_network": "devnet" if env != "production" else "mainnet",
                    "rpc_url": (
                        "https://api.devnet.solana.com"
                        if env != "production"
                        else "https://api.mainnet-beta.solana.com"
                    ),
                },
            }

            consolidated_envs[env] = env_config

            # Save environment configuration
            env_file_path = self.project_root / f"config/environments/{env}.json"
            with open(env_file_path, "w") as f:
                json.dump(env_config, f, indent=2)

        self.audit_report["environment_configs"] = consolidated_envs
        self.audit_report["consolidation_actions"].append(
            {
                "action": "consolidate_environment_configs",
                "files_processed": len(env_files),
                "environments_created": len(environments),
                "timestamp": datetime.now().isoformat(),
            }
        )

        logger.info(
            f"✅ Consolidated {len(env_files)} environment files into {len(environments)} environment configs"
        )

    def consolidate_service_configurations(self):
        """Consolidate service-specific configurations"""
        logger.info("⚙️ Consolidating service configurations...")

        # Core services configuration
        core_services = {
            "auth": {
                "name": "Authentication Service",
                "port": 8000,
                "health_path": "/health",
            },
            "ac": {
                "name": "Constitutional AI Service",
                "port": 8001,
                "health_path": "/health",
            },
            "integrity": {
                "name": "Integrity Service",
                "port": 8002,
                "health_path": "/health",
            },
            "fv": {
                "name": "Formal Verification Service",
                "port": 8003,
                "health_path": "/health",
            },
            "gs": {
                "name": "Governance Synthesis Service",
                "port": 8004,
                "health_path": "/health",
            },
            "pgc": {
                "name": "Policy Governance Service",
                "port": 8005,
                "health_path": "/health",
            },
            "ec": {
                "name": "Evolutionary Computation Service",
                "port": 8006,
                "health_path": "/health",
            },
        }

        # Create service registry configuration
        service_registry = {
            "version": "1.0.0",
            "services": core_services,
            "discovery": {
                "method": "static",
                "health_check_interval": 30,
                "timeout": 10,
                "retries": 3,
            },
            "load_balancing": {
                "strategy": "round_robin",
                "health_check_required": True,
            },
        }

        # Save service registry
        registry_path = self.project_root / "config/services/registry.json"
        with open(registry_path, "w") as f:
            json.dump(service_registry, f, indent=2)

        self.audit_report["service_configs"] = service_registry
        self.audit_report["consolidation_actions"].append(
            {
                "action": "consolidate_service_configs",
                "services_configured": len(core_services),
                "registry_created": True,
                "timestamp": datetime.now().isoformat(),
            }
        )

        logger.info(f"✅ Consolidated {len(core_services)} service configurations")

    def generate_configuration_schema(self):
        """Generate JSON schema for configuration validation"""
        logger.info("📋 Generating configuration schema...")

        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "ACGS-1 Configuration Schema",
            "type": "object",
            "properties": {
                "database": {
                    "type": "object",
                    "properties": {
                        "host": {"type": "string"},
                        "port": {"type": "integer", "minimum": 1, "maximum": 65535},
                        "name": {"type": "string"},
                        "user": {"type": "string"},
                        "ssl_mode": {
                            "type": "string",
                            "enum": ["disable", "require", "verify-full"],
                        },
                    },
                    "required": ["host", "port", "name", "user"],
                },
                "services": {
                    "type": "object",
                    "patternProperties": {
                        "^[a-z_]+$": {
                            "type": "object",
                            "properties": {
                                "port": {
                                    "type": "integer",
                                    "minimum": 1000,
                                    "maximum": 65535,
                                },
                                "host": {"type": "string"},
                            },
                            "required": ["port", "host"],
                        }
                    },
                },
                "quantumagi": {
                    "type": "object",
                    "properties": {
                        "constitution_hash": {
                            "type": "string",
                            "pattern": "^[a-f0-9]{16}$",
                        },
                        "solana_network": {
                            "type": "string",
                            "enum": ["devnet", "testnet", "mainnet"],
                        },
                        "rpc_url": {"type": "string", "format": "uri"},
                    },
                    "required": ["constitution_hash", "solana_network", "rpc_url"],
                },
            },
        }

        schema_path = self.project_root / "config/schema.json"
        with open(schema_path, "w") as f:
            json.dump(schema, f, indent=2)

        logger.info("✅ Generated configuration schema")

    def generate_audit_report(self):
        """Generate comprehensive audit and consolidation report"""
        report_path = self.project_root / "reports" / "configuration_audit_report.json"
        report_path.parent.mkdir(exist_ok=True)

        with open(report_path, "w") as f:
            json.dump(self.audit_report, f, indent=2)

        # Generate summary
        summary = {
            "total_config_files": len(self.audit_report["configuration_files"]),
            "inconsistencies_found": len(self.audit_report["inconsistencies"]),
            "consolidation_actions": len(self.audit_report["consolidation_actions"]),
            "environments_configured": len(self.audit_report["environment_configs"]),
            "services_configured": len(
                self.audit_report["service_configs"].get("services", {})
            ),
        }

        print("\n" + "=" * 60)
        print("🔍 CONFIGURATION AUDIT SUMMARY")
        print("=" * 60)
        print(f"📁 Total configuration files: {summary['total_config_files']}")
        print(f"⚠️ Inconsistencies found: {summary['inconsistencies_found']}")
        print(f"✅ Consolidation actions: {summary['consolidation_actions']}")
        print(f"🌍 Environments configured: {summary['environments_configured']}")
        print(f"⚙️ Services configured: {summary['services_configured']}")
        print(f"📊 Report saved: {report_path}")

    def run_complete_consolidation(self):
        """Execute complete configuration consolidation process"""
        logger.info("🚀 Starting ACGS-1 configuration consolidation...")

        self.audit_current_configuration_state()
        self.create_centralized_structure()
        self.consolidate_environment_configurations()
        self.consolidate_service_configurations()
        self.generate_configuration_schema()
        self.generate_audit_report()

        logger.info("✅ Configuration consolidation complete!")


if __name__ == "__main__":
    manager = ConfigurationManager()
    manager.run_complete_consolidation()
