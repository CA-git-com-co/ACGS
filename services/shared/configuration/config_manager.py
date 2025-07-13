"""
Configuration Management System for ACGS
Constitutional Hash: cdd01ef066bc6cf2

Centralized configuration with validation, environment support, and hot reloading.
"""

import asyncio
import json
import logging
import os
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

import yaml
from shared.resilience.exceptions import ConfigurationError
from shared.validation.validators import SchemaValidator, ValidationResult
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

logger = logging.getLogger(__name__)


class ConfigFormat(str, Enum):
    """Configuration file formats."""

    JSON = "json"
    YAML = "yaml"
    TOML = "toml"
    ENV = "env"


class ConfigSource(str, Enum):
    """Configuration sources."""

    FILE = "file"
    ENVIRONMENT = "environment"
    REMOTE = "remote"
    DATABASE = "database"


@dataclass
class ConfigSchema:
    """Schema definition for configuration validation."""

    name: str
    schema: dict[str, Any]
    required_fields: list[str] = field(default_factory=list)
    default_values: dict[str, Any] = field(default_factory=dict)
    validators: list[Callable[[dict[str, Any]], bool]] = field(default_factory=list)

    def validate(self, config: dict[str, Any]) -> ValidationResult:
        """Validate configuration against schema."""
        validator = SchemaValidator(self.schema, f"config_schema_{self.name}")
        return asyncio.run(validator.validate(config))


@dataclass
class ConfigValidator:
    """Configuration validator with business rules."""

    name: str
    validation_func: Callable[[dict[str, Any]], ValidationResult]
    description: str = ""

    def validate(self, config: dict[str, Any]) -> ValidationResult:
        """Validate configuration."""
        try:
            return self.validation_func(config)
        except Exception as e:
            from shared.validation.validators import (
                ValidationResult,
                ValidationSeverity,
            )

            result = ValidationResult(is_valid=False)
            result.add_issue(
                field="validator",
                message=f"Validation error in {self.name}: {e}",
                severity=ValidationSeverity.ERROR,
                error_code="VALIDATOR_ERROR",
            )
            return result


class ConfigChangeHandler:
    """Handler for configuration changes."""

    def __init__(self, callback: Callable[[str, dict[str, Any]], None]):
        self.callback = callback

    def on_change(self, config_name: str, new_config: dict[str, Any]) -> None:
        """Handle configuration change."""
        try:
            self.callback(config_name, new_config)
        except Exception as e:
            logger.exception(f"Error in config change handler: {e}")


class FileWatcher(FileSystemEventHandler):
    """File system watcher for configuration files."""

    def __init__(self, config_manager: "ConfigManager"):
        self.config_manager = config_manager

    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory:
            return

        file_path = Path(event.src_path)
        if file_path.suffix in {".json", ".yaml", ".yml", ".toml"}:
            logger.info(f"Configuration file changed: {file_path}")
            asyncio.create_task(self.config_manager.reload_config_file(str(file_path)))


class EnvironmentConfig:
    """Environment-specific configuration manager."""

    def __init__(self, environment: str | None = None):
        self.environment = environment or os.getenv("ENVIRONMENT", "development")
        self.prefix = f"ACGS_{self.environment.upper()}_"

    def get_env_vars(self) -> dict[str, str]:
        """Get environment variables for this environment."""
        env_vars = {}
        for key, value in os.environ.items():
            if key.startswith(self.prefix):
                config_key = key[len(self.prefix) :].lower()
                env_vars[config_key] = value
        return env_vars

    def get_config_files(self) -> list[str]:
        """Get configuration files for this environment."""
        config_dir = Path("config")
        files = []

        # Base configuration
        for ext in ["json", "yaml", "yml"]:
            base_file = config_dir / f"config.{ext}"
            if base_file.exists():
                files.append(str(base_file))

        # Environment-specific configuration
        for ext in ["json", "yaml", "yml"]:
            env_file = config_dir / f"config.{self.environment}.{ext}"
            if env_file.exists():
                files.append(str(env_file))

        return files


class ConfigManager:
    """Centralized configuration management system."""

    def __init__(self, environment: str | None = None):
        self.environment = environment or os.getenv("ENVIRONMENT", "development")
        self._configs: dict[str, dict[str, Any]] = {}
        self._schemas: dict[str, ConfigSchema] = {}
        self._validators: list[ConfigValidator] = []
        self._change_handlers: list[ConfigChangeHandler] = []
        self._file_watcher: Observer | None = None
        self._watched_files: set = set()
        self._lock = threading.RLock()

        # Environment config
        self._env_config = EnvironmentConfig(environment)

        # Load environment variables
        self._load_environment_config()

        # Constitutional compliance
        self._constitutional_hash = "cdd01ef066bc6cf2"

    def add_schema(self, schema: ConfigSchema) -> None:
        """Add configuration schema."""
        with self._lock:
            self._schemas[schema.name] = schema
            logger.info(f"Added configuration schema: {schema.name}")

    def add_validator(self, validator: ConfigValidator) -> None:
        """Add configuration validator."""
        with self._lock:
            self._validators.append(validator)
            logger.info(f"Added configuration validator: {validator.name}")

    def add_change_handler(self, handler: ConfigChangeHandler) -> None:
        """Add configuration change handler."""
        with self._lock:
            self._change_handlers.append(handler)
            logger.info("Added configuration change handler")

    def _load_environment_config(self) -> None:
        """Load configuration from environment variables."""
        env_vars = self._env_config.get_env_vars()
        if env_vars:
            self._configs["environment"] = env_vars
            logger.info(f"Loaded {len(env_vars)} environment variables")

    async def load_config_file(
        self,
        file_path: str,
        config_name: str | None = None,
        format: ConfigFormat = None,
        watch: bool = True,
    ) -> None:
        """Load configuration from file."""
        file_path = Path(file_path)
        config_name = config_name or file_path.stem

        if not file_path.exists():
            raise ConfigurationError(f"Configuration file not found: {file_path}")

        # Auto-detect format
        if format is None:
            extension = file_path.suffix.lower()
            format_map = {
                ".json": ConfigFormat.JSON,
                ".yaml": ConfigFormat.YAML,
                ".yml": ConfigFormat.YAML,
                ".toml": ConfigFormat.TOML,
            }
            format = format_map.get(extension, ConfigFormat.JSON)

        try:
            # Load file content
            content = file_path.read_text()

            # Parse based on format
            if format == ConfigFormat.JSON:
                config_data = json.loads(content)
            elif format == ConfigFormat.YAML:
                config_data = yaml.safe_load(content)
            elif format == ConfigFormat.TOML:
                import tomli

                config_data = tomli.loads(content)
            else:
                raise ConfigurationError(f"Unsupported config format: {format}")

            # Validate configuration
            await self._validate_config(config_name, config_data)

            # Store configuration
            with self._lock:
                old_config = self._configs.get(config_name)
                self._configs[config_name] = config_data

                # Add constitutional compliance
                config_data["constitutional_hash"] = self._constitutional_hash
                config_data["loaded_at"] = datetime.utcnow().isoformat()
                config_data["source"] = str(file_path)

            # Watch file for changes
            if watch and str(file_path) not in self._watched_files:
                self._watch_file(str(file_path))

            # Notify change handlers
            if old_config != config_data:
                await self._notify_change_handlers(config_name, config_data)

            logger.info(f"Loaded configuration '{config_name}' from {file_path}")

        except Exception as e:
            raise ConfigurationError(f"Failed to load config file {file_path}: {e}")

    async def reload_config_file(self, file_path: str) -> None:
        """Reload configuration file."""
        # Find config name by file path
        config_name = None
        with self._lock:
            for name, config in self._configs.items():
                if config.get("source") == file_path:
                    config_name = name
                    break

        if config_name:
            await self.load_config_file(file_path, config_name, watch=False)
        else:
            logger.warning(f"No configuration found for file: {file_path}")

    def _watch_file(self, file_path: str) -> None:
        """Start watching configuration file for changes."""
        if self._file_watcher is None:
            self._file_watcher = Observer()
            self._file_watcher.start()

        file_path = Path(file_path)
        event_handler = FileWatcher(self)

        self._file_watcher.schedule(
            event_handler, path=str(file_path.parent), recursive=False
        )

        self._watched_files.add(str(file_path))
        logger.info(f"Watching configuration file: {file_path}")

    async def _validate_config(
        self, config_name: str, config_data: dict[str, Any]
    ) -> None:
        """Validate configuration data."""
        # Schema validation
        if config_name in self._schemas:
            schema = self._schemas[config_name]
            result = schema.validate(config_data)
            if not result.is_valid:
                raise ConfigurationError(
                    f"Schema validation failed for {config_name}: {result.issues}"
                )

        # Custom validators
        for validator in self._validators:
            try:
                result = validator.validate(config_data)
                if not result.is_valid:
                    raise ConfigurationError(
                        f"Validation failed ({validator.name}): {result.issues}"
                    )
            except Exception as e:
                raise ConfigurationError(f"Validator error ({validator.name}): {e}")

    async def _notify_change_handlers(
        self, config_name: str, new_config: dict[str, Any]
    ) -> None:
        """Notify configuration change handlers."""
        for handler in self._change_handlers:
            try:
                handler.on_change(config_name, new_config)
            except Exception as e:
                logger.exception(f"Error in configuration change handler: {e}")

    def get_config(self, config_name: str, default: Any = None) -> dict[str, Any]:
        """Get configuration by name."""
        with self._lock:
            return self._configs.get(config_name, default)

    def get_value(self, config_name: str, key: str, default: Any = None) -> Any:
        """Get specific configuration value."""
        config = self.get_config(config_name, {})
        return config.get(key, default)

    def get_nested_value(
        self, config_name: str, key_path: str, default: Any = None
    ) -> Any:
        """Get nested configuration value using dot notation."""
        config = self.get_config(config_name, {})

        keys = key_path.split(".")
        value = config

        try:
            for key in keys:
                if isinstance(value, dict):
                    value = value[key]
                else:
                    return default
            return value
        except KeyError:
            return default

    def set_value(self, config_name: str, key: str, value: Any) -> None:
        """Set configuration value."""
        with self._lock:
            if config_name not in self._configs:
                self._configs[config_name] = {}
            self._configs[config_name][key] = value

    def merge_config(self, config_name: str, new_config: dict[str, Any]) -> None:
        """Merge new configuration with existing."""
        with self._lock:
            if config_name not in self._configs:
                self._configs[config_name] = {}

            def deep_merge(base_dict: dict, update_dict: dict) -> dict:
                """Deep merge two dictionaries."""
                result = base_dict.copy()
                for key, value in update_dict.items():
                    if (
                        key in result
                        and isinstance(result[key], dict)
                        and isinstance(value, dict)
                    ):
                        result[key] = deep_merge(result[key], value)
                    else:
                        result[key] = value
                return result

            self._configs[config_name] = deep_merge(
                self._configs[config_name], new_config
            )

    def list_configs(self) -> list[str]:
        """List all configuration names."""
        with self._lock:
            return list(self._configs.keys())

    def get_all_configs(self) -> dict[str, dict[str, Any]]:
        """Get all configurations."""
        with self._lock:
            return self._configs.copy()

    async def load_environment_configs(self) -> None:
        """Load all configuration files for current environment."""
        config_files = self._env_config.get_config_files()

        for file_path in config_files:
            try:
                await self.load_config_file(file_path)
            except Exception as e:
                logger.exception(f"Failed to load config file {file_path}: {e}")

    def export_config(
        self, config_name: str, format: ConfigFormat = ConfigFormat.JSON
    ) -> str:
        """Export configuration to string."""
        config = self.get_config(config_name)
        if config is None:
            raise ConfigurationError(f"Configuration '{config_name}' not found")

        if format == ConfigFormat.JSON:
            return json.dumps(config, indent=2)
        if format == ConfigFormat.YAML:
            return yaml.dump(config, default_flow_style=False)
        if format == ConfigFormat.TOML:
            import tomli_w

            return tomli_w.dumps(config)
        raise ConfigurationError(f"Unsupported export format: {format}")

    def get_config_stats(self) -> dict[str, Any]:
        """Get configuration statistics."""
        with self._lock:
            return {
                "environment": self.environment,
                "total_configs": len(self._configs),
                "schemas_count": len(self._schemas),
                "validators_count": len(self._validators),
                "change_handlers_count": len(self._change_handlers),
                "watched_files_count": len(self._watched_files),
                "configs": list(self._configs.keys()),
                "constitutional_hash": self._constitutional_hash,
            }

    def stop_file_watching(self) -> None:
        """Stop file watching."""
        if self._file_watcher:
            self._file_watcher.stop()
            self._file_watcher.join()
            self._file_watcher = None
            self._watched_files.clear()
            logger.info("Stopped configuration file watching")


# Global configuration manager
_global_config_manager = ConfigManager()


def get_config_manager() -> ConfigManager:
    """Get the global configuration manager."""
    return _global_config_manager


# Common configuration schemas
def create_database_schema() -> ConfigSchema:
    """Create database configuration schema."""
    schema = {
        "type": "object",
        "properties": {
            "host": {"type": "string"},
            "port": {"type": "integer", "minimum": 1, "maximum": 65535},
            "database": {"type": "string"},
            "username": {"type": "string"},
            "password": {"type": "string"},
            "pool_size": {"type": "integer", "minimum": 1, "maximum": 100},
            "max_overflow": {"type": "integer", "minimum": 0},
            "pool_timeout": {"type": "number", "minimum": 0},
            "pool_recycle": {"type": "integer", "minimum": -1},
            "ssl_mode": {
                "type": "string",
                "enum": ["disable", "allow", "prefer", "require"],
            },
        },
        "required": ["host", "database", "username"],
    }

    return ConfigSchema(
        name="database",
        schema=schema,
        required_fields=["host", "database", "username"],
        default_values={
            "port": 5432,
            "pool_size": 20,
            "max_overflow": 10,
            "pool_timeout": 30,
            "pool_recycle": 3600,
            "ssl_mode": "prefer",
        },
    )


def create_cache_schema() -> ConfigSchema:
    """Create cache configuration schema."""
    schema = {
        "type": "object",
        "properties": {
            "redis_url": {"type": "string"},
            "default_ttl": {"type": "integer", "minimum": 0},
            "max_connections": {"type": "integer", "minimum": 1},
            "key_prefix": {"type": "string"},
            "compression": {"type": "boolean"},
            "serializer": {"type": "string", "enum": ["json", "pickle", "msgpack"]},
        },
        "required": ["redis_url"],
    }

    return ConfigSchema(
        name="cache",
        schema=schema,
        required_fields=["redis_url"],
        default_values={
            "default_ttl": 3600,
            "max_connections": 50,
            "key_prefix": "acgs:",
            "compression": False,
            "serializer": "json",
        },
    )


# Setup default configuration
def setup_default_config() -> None:
    """Set up default configuration schemas and validators."""
    config_manager = get_config_manager()

    # Add schemas
    config_manager.add_schema(create_database_schema())
    config_manager.add_schema(create_cache_schema())

    # Add constitutional compliance validator
    def constitutional_validator(config: dict[str, Any]) -> "ValidationResult":
        from shared.validation.validators import ValidationResult, ValidationSeverity

        result = ValidationResult(is_valid=True)

        if "constitutional_hash" not in config:
            result.add_issue(
                field="constitutional_hash",
                message="Constitutional hash is required in configuration",
                severity=ValidationSeverity.ERROR,
                error_code="MISSING_CONSTITUTIONAL_HASH",
            )
        elif config["constitutional_hash"] != "cdd01ef066bc6cf2":
            result.add_issue(
                field="constitutional_hash",
                message="Invalid constitutional hash in configuration",
                severity=ValidationSeverity.CRITICAL,
                error_code="INVALID_CONSTITUTIONAL_HASH",
            )

        return result

    validator = ConfigValidator(
        name="constitutional_compliance",
        validation_func=constitutional_validator,
        description="Ensures constitutional compliance in configuration",
    )
    config_manager.add_validator(validator)

    logger.info("Default configuration management setup complete")
