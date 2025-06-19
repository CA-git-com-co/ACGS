"""
Service Configuration for PGC Service.

This configuration file defines the service settings for the
Policy Governance Compiler (PGC) service including networking,
integration points, and performance parameters.
"""

import os
from typing import Any

import yaml


class ServiceConfig:
    """Service configuration for PGC Service with ACGS-1 enhancements."""

    # Default configuration values
    DEFAULT_CONFIG = {
        "service": {
            "name": "pgc_service",
            "host": "0.0.0.0",
            "port": 8005,  # Updated port per ACGS-1 requirements
            "workers": 4,
            "log_level": "INFO",
            "enable_docs": True,
            "cors_origins": ["*"],
            "timeout_seconds": 30,
        },
        "integrations": {
            "fv_service": {
                "url": "http://localhost:8003",  # FV service on correct port for host deployment
                "timeout_ms": 5000,
                "circuit_breaker_enabled": True,
                "retry_attempts": 3,
                "retry_delay_ms": 500,
            },
            "integrity_service": {
                "url": "http://localhost:8002",
                "timeout_ms": 5000,
                "circuit_breaker_enabled": True,
                "retry_attempts": 3,
                "retry_delay_ms": 500,
            },
            "ac_service": {
                "url": "http://localhost:8001",
                "timeout_ms": 5000,
                "circuit_breaker_enabled": True,
                "retry_attempts": 3,
                "retry_delay_ms": 500,
            },
        },
        "telemetry": {
            "enabled": True,
            "otlp_endpoint": "http://localhost:4317",
            "otlp_version": "v1.37.0",  # Specified OpenTelemetry version
            "service_name": "pgc_service",
            "environment": "production",
            "traces_sample_rate": 0.1,
        },
        "performance": {
            "p99_latency_target_ms": 500,  # p99 latency below 500ms
            "p95_latency_target_ms": 25,  # p95 latency below 25ms
            "enable_optimizations": True,
            "cache_enabled": True,
            "max_concurrent_requests": 200,
        },
        "security": {
            "enable_mtls": True,
            "require_auth": True,
            "token_expiry_seconds": 3600,
            "enable_rate_limiting": True,
            "rate_limit_requests": 100,
            "rate_limit_window_seconds": 60,
        },
    }

    def __init__(self, config_path: str | None = None):
        """Initialize service configuration.

        Args:
            config_path: Path to YAML configuration file (optional)
        """
        self.config = self.DEFAULT_CONFIG.copy()

        # Load from environment variable if specified
        env_config_path = os.environ.get("PGC_CONFIG_PATH")
        if env_config_path:
            config_path = env_config_path

        # Load from YAML file if provided
        if config_path and os.path.exists(config_path):
            self._load_from_yaml(config_path)

        # Override with environment variables
        self._load_from_env()

    def _load_from_yaml(self, config_path: str) -> None:
        """Load configuration from YAML file.

        Args:
            config_path: Path to YAML configuration file
        """
        try:
            with open(config_path) as f:
                yaml_config = yaml.safe_load(f)
                if yaml_config:
                    # Deep merge configuration
                    self._deep_merge(self.config, yaml_config)
        except Exception as e:
            print(f"Error loading configuration from {config_path}: {e}")

    def _load_from_env(self) -> None:
        """Load configuration from environment variables.

        Environment variables override file-based configuration.
        Format: PGC_{SECTION}_{KEY}=value
        Example: PGC_SERVICE_PORT=8005
        """
        for env_name, env_value in os.environ.items():
            if env_name.startswith("PGC_"):
                parts = env_name[4:].lower().split("_", 1)
                if len(parts) == 2:
                    section, key = parts
                    if section in self.config and key in self.config[section]:
                        # Convert value to the appropriate type
                        current_value = self.config[section][key]
                        if isinstance(current_value, bool):
                            self.config[section][key] = env_value.lower() in [
                                "true",
                                "1",
                                "yes",
                            ]
                        elif isinstance(current_value, int):
                            self.config[section][key] = int(env_value)
                        elif isinstance(current_value, float):
                            self.config[section][key] = float(env_value)
                        else:
                            self.config[section][key] = env_value

    def _deep_merge(self, target: dict[str, Any], source: dict[str, Any]) -> None:
        """Deep merge source dictionary into target dictionary.

        Args:
            target: Target dictionary to merge into
            source: Source dictionary to merge from
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_merge(target[key], value)
            else:
                target[key] = value

    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Get configuration value.

        Args:
            section: Configuration section
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        if section in self.config and key in self.config[section]:
            return self.config[section][key]
        return default

    def get_section(self, section: str) -> dict[str, Any]:
        """Get configuration section.

        Args:
            section: Configuration section

        Returns:
            Section dictionary or empty dict if not found
        """
        return self.config.get(section, {})


# Singleton instance
_service_config = None


def get_service_config() -> ServiceConfig:
    """Get singleton service configuration instance.

    Returns:
        ServiceConfig instance
    """
    global _service_config
    if _service_config is None:
        config_path = os.environ.get("PGC_CONFIG_PATH", "/app/config/service_config.yaml")
        _service_config = ServiceConfig(config_path)
    return _service_config
