#!/usr/bin/env python3
"""
ACGS-1 Configuration Loader
===========================

Centralized configuration loading with environment-specific overrides,
validation, and secure secrets management.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import jsonschema
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ConfigurationError(Exception):
    """Configuration loading or validation error"""

    message: str
    config_file: Optional[str] = None
    validation_errors: Optional[list] = None


class ConfigurationLoader:
    """Centralized configuration loader for ACGS-1"""

    def __init__(self, config_dir: str = None):
        self.config_dir = Path(config_dir or os.path.join(os.path.dirname(__file__)))
        self.schema_path = self.config_dir / "schema.json"
        self.environments_dir = self.config_dir / "environments"
        self.services_dir = self.config_dir / "services"

        # Load schema for validation
        self.schema = self._load_schema()

    def _load_schema(self) -> Dict[str, Any]:
        """Load configuration schema for validation"""
        try:
            with open(self.schema_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Schema file not found: {self.schema_path}")
            return {}
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid schema JSON: {e}", str(self.schema_path))

    def load_environment_config(self, environment: str = None) -> Dict[str, Any]:
        """Load environment-specific configuration"""
        if not environment:
            environment = os.getenv("ACGS_ENVIRONMENT", "development")

        config_file = self.environments_dir / f"{environment}.json"

        if not config_file.exists():
            raise ConfigurationError(
                f"Environment configuration not found: {environment}", str(config_file)
            )

        try:
            with open(config_file, "r") as f:
                config = json.load(f)

            # Validate configuration
            if self.schema:
                self._validate_config(config, str(config_file))

            # Apply environment variable substitutions
            config = self._apply_env_substitutions(config)

            logger.info(f"Loaded configuration for environment: {environment}")
            return config

        except json.JSONDecodeError as e:
            raise ConfigurationError(
                f"Invalid JSON in config file: {e}", str(config_file)
            )

    def load_service_registry(self) -> Dict[str, Any]:
        """Load service registry configuration"""
        registry_file = self.services_dir / "registry.json"

        if not registry_file.exists():
            raise ConfigurationError("Service registry not found", str(registry_file))

        try:
            with open(registry_file, "r") as f:
                registry = json.load(f)

            logger.info("Loaded service registry configuration")
            return registry

        except json.JSONDecodeError as e:
            raise ConfigurationError(
                f"Invalid JSON in registry file: {e}", str(registry_file)
            )

    def _validate_config(self, config: Dict[str, Any], config_file: str):
        """Validate configuration against schema"""
        try:
            jsonschema.validate(config, self.schema)
        except jsonschema.ValidationError as e:
            raise ConfigurationError(
                f"Configuration validation failed: {e.message}",
                config_file,
                [e.message],
            )
        except jsonschema.SchemaError as e:
            raise ConfigurationError(f"Invalid schema: {e.message}")

    def _apply_env_substitutions(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment variable substitutions"""

        def substitute_value(value):
            if (
                isinstance(value, str)
                and value.startswith("${")
                and value.endswith("}")
            ):
                env_var = value[2:-1]  # Remove ${ and }
                env_value = os.getenv(env_var)
                if env_value is None:
                    logger.warning(f"Environment variable not found: {env_var}")
                    return value  # Return original if not found
                return env_value
            elif isinstance(value, dict):
                return {k: substitute_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [substitute_value(item) for item in value]
            else:
                return value

        return substitute_value(config)

    def get_service_config(
        self, service_name: str, environment: str = None
    ) -> Dict[str, Any]:
        """Get configuration for a specific service"""
        env_config = self.load_environment_config(environment)
        service_registry = self.load_service_registry()

        # Get service-specific configuration
        service_config = env_config.get("services", {}).get(service_name, {})
        registry_config = service_registry.get("services", {}).get(service_name, {})

        # Merge configurations (environment overrides registry)
        merged_config = {
            **registry_config,
            **service_config,
            "database": env_config.get("database", {}),
            "redis": env_config.get("redis", {}),
            "logging": env_config.get("logging", {}),
            "security": env_config.get("security", {}),
            "quantumagi": env_config.get("quantumagi", {}),
            "monitoring": env_config.get("monitoring", {}),
            "environment": env_config.get("environment", "development"),
        }

        return merged_config

    def get_database_config(self, environment: str = None) -> Dict[str, Any]:
        """Get database configuration"""
        env_config = self.load_environment_config(environment)
        return env_config.get("database", {})

    def get_redis_config(self, environment: str = None) -> Dict[str, Any]:
        """Get Redis configuration"""
        env_config = self.load_environment_config(environment)
        return env_config.get("redis", {})

    def get_quantumagi_config(self, environment: str = None) -> Dict[str, Any]:
        """Get Quantumagi blockchain configuration"""
        env_config = self.load_environment_config(environment)
        return env_config.get("quantumagi", {})

    def validate_all_environments(self) -> Dict[str, Any]:
        """Validate all environment configurations"""
        results = {}

        for env_file in self.environments_dir.glob("*.json"):
            environment = env_file.stem
            try:
                config = self.load_environment_config(environment)
                results[environment] = {"valid": True, "config": config}
            except ConfigurationError as e:
                results[environment] = {
                    "valid": False,
                    "error": e.message,
                    "validation_errors": e.validation_errors,
                }

        return results


# Global configuration loader instance
config_loader = ConfigurationLoader()


def get_config(service_name: str = None, environment: str = None) -> Dict[str, Any]:
    """Convenience function to get configuration"""
    if service_name:
        return config_loader.get_service_config(service_name, environment)
    else:
        return config_loader.load_environment_config(environment)


def get_database_url(environment: str = None) -> str:
    """Get database connection URL"""
    db_config = config_loader.get_database_config(environment)

    # Construct database URL
    user = db_config.get("user", "")
    password = (
        os.getenv(f"{environment.upper()}_DB_PASSWORD", "") if environment else ""
    )
    host = db_config.get("host", "localhost")
    port = db_config.get("port", 5432)
    name = db_config.get("name", "acgs")

    if password:
        return f"postgresql://{user}:{password}@{host}:{port}/{name}"
    else:
        return f"postgresql://{user}@{host}:{port}/{name}"


def get_redis_url(environment: str = None) -> str:
    """Get Redis connection URL"""
    redis_config = config_loader.get_redis_config(environment)

    host = redis_config.get("host", "localhost")
    port = redis_config.get("port", 6379)
    db = redis_config.get("db", 0)
    password = redis_config.get("password")
    ssl = redis_config.get("ssl", False)

    scheme = "rediss" if ssl else "redis"

    if password and not password.startswith("${"):
        return f"{scheme}://:{password}@{host}:{port}/{db}"
    else:
        return f"{scheme}://{host}:{port}/{db}"


if __name__ == "__main__":
    # Validate all configurations
    loader = ConfigurationLoader()
    results = loader.validate_all_environments()

    print("Configuration Validation Results:")
    print("=" * 40)

    for env, result in results.items():
        status = "✅ VALID" if result["valid"] else "❌ INVALID"
        print(f"{env}: {status}")

        if not result["valid"]:
            print(f"  Error: {result['error']}")
            if result.get("validation_errors"):
                for error in result["validation_errors"]:
                    print(f"    - {error}")

    print("\nConfiguration loading test complete!")
