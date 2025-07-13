"""
Service Configuration for XAI Integration Service.

This configuration file defines the service settings for the
X.AI Integration service including networking, integration points,
and performance parameters.

Constitutional Hash: cdd01ef066bc6cf2
"""

import os
import pathlib
from typing import Any

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class ServiceConfig:
    """Service configuration for XAI Integration Service with ACGS-2 enhancements."""

    # Default configuration values
    DEFAULT_CONFIG = {
        "service": {
            "name": "xai_integration_service",
            "host": "0.0.0.0",
            "port": 8014,  # New port for XAI integration
            "workers": 2,  # Conservative for LLM operations
            "log_level": "INFO",
            "enable_docs": True,
            "cors_origins": ["*"],
            "timeout_seconds": 30,
            "constitutional_hash": CONSTITUTIONAL_HASH,
        },
        "xai": {
            "api_host": "api.x.ai",
            "default_model": "grok-4-0709",
            "max_tokens": 4000,
            "temperature": 0.7,
            "timeout_seconds": 25,
            "retry_attempts": 3,
            "retry_delay_seconds": 1,
        },
        "performance": {
            "target_p99_latency_ms": 5000,  # 5 seconds for LLM operations
            "target_cache_hit_rate": 0.85,
            "target_throughput_rps": 50,
            "max_cache_size": 1000,
            "cache_ttl_seconds": 3600,
        },
        "constitutional": {
            "validation_enabled": True,
            "hash_validation": True,
            "compliance_threshold": 0.95,
            "audit_logging": True,
        },
        "integration": {
            "auth_service_url": "http://auth_service:8016",
            "constitutional_ai_url": "http://constitutional_core:8001",
            "integrity_service_url": "http://integrity_service:8002",
            "governance_engine_url": "http://governance_engine:8004",
        },
        "monitoring": {
            "metrics_enabled": True,
            "health_check_interval": 30,
            "performance_logging": True,
            "prometheus_port": 9014,
        },
        "security": {
            "api_key_required": True,
            "rate_limiting": True,
            "max_requests_per_minute": 100,
            "content_filtering": True,
        },
    }

    def __init__(self, config_path: str | None = None):
        """Initialize service configuration.

        Args:
            config_path: Optional path to configuration file
        """
        self.config = self.DEFAULT_CONFIG.copy()

        # Override with environment variables
        self._load_from_environment()

        # Load from file if provided
        if config_path and pathlib.Path(config_path).exists():
            self._load_from_file(config_path)

    def _load_from_environment(self):
        """Load configuration from environment variables."""
        # Service configuration
        if os.getenv("XAI_SERVICE_PORT"):
            self.config["service"]["port"] = int(os.getenv("XAI_SERVICE_PORT"))

        if os.getenv("XAI_SERVICE_HOST"):
            self.config["service"]["host"] = os.getenv("XAI_SERVICE_HOST")

        if os.getenv("LOG_LEVEL"):
            self.config["service"]["log_level"] = os.getenv("LOG_LEVEL")

        # X.AI configuration
        if os.getenv("XAI_API_HOST"):
            self.config["xai"]["api_host"] = os.getenv("XAI_API_HOST")

        if os.getenv("XAI_DEFAULT_MODEL"):
            self.config["xai"]["default_model"] = os.getenv("XAI_DEFAULT_MODEL")

        if os.getenv("XAI_MAX_TOKENS"):
            self.config["xai"]["max_tokens"] = int(os.getenv("XAI_MAX_TOKENS"))

        if os.getenv("XAI_TEMPERATURE"):
            self.config["xai"]["temperature"] = float(os.getenv("XAI_TEMPERATURE"))

        # Performance configuration
        if os.getenv("XAI_TARGET_LATENCY_MS"):
            self.config["performance"]["target_p99_latency_ms"] = int(
                os.getenv("XAI_TARGET_LATENCY_MS")
            )

        if os.getenv("XAI_CACHE_SIZE"):
            self.config["performance"]["max_cache_size"] = int(
                os.getenv("XAI_CACHE_SIZE")
            )

        # Integration URLs
        if os.getenv("AUTH_SERVICE_URL"):
            self.config["integration"]["auth_service_url"] = os.getenv(
                "AUTH_SERVICE_URL"
            )

        if os.getenv("CONSTITUTIONAL_AI_URL"):
            self.config["integration"]["constitutional_ai_url"] = os.getenv(
                "CONSTITUTIONAL_AI_URL"
            )

        if os.getenv("INTEGRITY_SERVICE_URL"):
            self.config["integration"]["integrity_service_url"] = os.getenv(
                "INTEGRITY_SERVICE_URL"
            )

        if os.getenv("GOVERNANCE_ENGINE_URL"):
            self.config["integration"]["governance_engine_url"] = os.getenv(
                "GOVERNANCE_ENGINE_URL"
            )

    def _load_from_file(self, config_path: str):
        """Load configuration from YAML file.

        Args:
            config_path: Path to configuration file
        """
        try:
            import yaml

            with open(config_path, encoding="utf-8") as f:
                file_config = yaml.safe_load(f)
                self._merge_config(self.config, file_config)
        except Exception:
            pass

    def _merge_config(self, base: dict[str, Any], override: dict[str, Any]):
        """Recursively merge configuration dictionaries.

        Args:
            base: Base configuration dictionary
            override: Override configuration dictionary
        """
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value

    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value by dot-separated key path.

        Args:
            key_path: Dot-separated key path (e.g., 'service.port')
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key_path.split(".")
        value = self.config

        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

    def get_service_config(self) -> dict[str, Any]:
        """Get service-specific configuration."""
        return self.config["service"]

    def get_xai_config(self) -> dict[str, Any]:
        """Get X.AI-specific configuration."""
        return self.config["xai"]

    def get_performance_config(self) -> dict[str, Any]:
        """Get performance-specific configuration."""
        return self.config["performance"]

    def get_constitutional_config(self) -> dict[str, Any]:
        """Get constitutional governance configuration."""
        return self.config["constitutional"]

    def get_integration_config(self) -> dict[str, Any]:
        """Get service integration configuration."""
        return self.config["integration"]

    def get_monitoring_config(self) -> dict[str, Any]:
        """Get monitoring configuration."""
        return self.config["monitoring"]

    def get_security_config(self) -> dict[str, Any]:
        """Get security configuration."""
        return self.config["security"]

    def validate_config(self) -> list[str]:
        """Validate configuration and return list of issues.

        Returns:
            List of configuration validation issues
        """
        issues = []

        # Validate required environment variables
        if not os.getenv("XAI_API_KEY"):
            issues.append("XAI_API_KEY environment variable is required")

        # Validate port ranges
        port = self.get("service.port")
        if not (1024 <= port <= 65535):
            issues.append(f"Service port {port} is not in valid range (1024-65535)")

        # Validate performance targets
        latency = self.get("performance.target_p99_latency_ms")
        if latency <= 0:
            issues.append("Target P99 latency must be positive")

        cache_hit_rate = self.get("performance.target_cache_hit_rate")
        if not (0.0 <= cache_hit_rate <= 1.0):
            issues.append("Target cache hit rate must be between 0.0 and 1.0")

        # Validate constitutional hash
        if self.get("service.constitutional_hash") != CONSTITUTIONAL_HASH:
            issues.append(
                f"Constitutional hash mismatch: expected {CONSTITUTIONAL_HASH}"
            )

        return issues

    def __str__(self) -> str:
        """String representation of configuration."""
        return f"XAIServiceConfig(port={self.get('service.port')}, hash={CONSTITUTIONAL_HASH})"


# Global configuration instance
config = ServiceConfig()
