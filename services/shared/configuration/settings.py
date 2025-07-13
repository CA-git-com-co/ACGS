"""
Application Settings Management for ACGS
Constitutional Hash: cdd01ef066bc6cf2

Centralized settings with environment-specific configurations and validation.
"""

import logging
import os
from dataclasses import dataclass, field
from typing import Any

from .config_manager import get_config_manager

logger = logging.getLogger(__name__)


@dataclass
class DatabaseSettings:
    """Database configuration settings."""

    host: str = "localhost"
    port: int = 5432
    database: str = "acgs"
    username: str = "acgs_user"
    password: str = ""
    pool_size: int = 20
    max_overflow: int = 10
    pool_timeout: float = 30.0
    pool_recycle: int = 3600
    ssl_mode: str = "prefer"
    echo: bool = False

    @property
    def dsn(self) -> str:
        """Get database connection string."""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "host": self.host,
            "port": self.port,
            "database": self.database,
            "username": self.username,
            "password": "***" if self.password else "",
            "pool_size": self.pool_size,
            "max_overflow": self.max_overflow,
            "pool_timeout": self.pool_timeout,
            "pool_recycle": self.pool_recycle,
            "ssl_mode": self.ssl_mode,
            "echo": self.echo,
            "dsn": f"postgresql://{self.username}:***@{self.host}:{self.port}/{self.database}",
        }


@dataclass
class CacheSettings:
    """Cache configuration settings."""

    redis_url: str = "redis://localhost:6379/0"
    default_ttl: int = 3600
    max_connections: int = 50
    key_prefix: str = "acgs:"
    compression: bool = False
    serializer: str = "json"  # json, pickle, msgpack
    cluster_mode: bool = False
    sentinel_hosts: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "redis_url": self.redis_url,
            "default_ttl": self.default_ttl,
            "max_connections": self.max_connections,
            "key_prefix": self.key_prefix,
            "compression": self.compression,
            "serializer": self.serializer,
            "cluster_mode": self.cluster_mode,
            "sentinel_hosts": self.sentinel_hosts,
        }


@dataclass
class LoggingSettings:
    """Logging configuration settings."""

    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: str | None = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    enable_console: bool = True
    enable_structured: bool = False
    structured_format: str = "json"  # json, ecs

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "level": self.level,
            "format": self.format,
            "file_path": self.file_path,
            "max_file_size": self.max_file_size,
            "backup_count": self.backup_count,
            "enable_console": self.enable_console,
            "enable_structured": self.enable_structured,
            "structured_format": self.structured_format,
        }


@dataclass
class SecuritySettings:
    """Security configuration settings."""

    secret_key: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    password_min_length: int = 8
    password_require_special: bool = True
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 30
    enable_2fa: bool = False
    allowed_origins: list[str] = field(default_factory=lambda: ["*"])
    rate_limit_per_minute: int = 100
    enable_csrf_protection: bool = True
    session_timeout_minutes: int = 60

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "secret_key": "***" if self.secret_key else "",
            "jwt_algorithm": self.jwt_algorithm,
            "jwt_expiration_hours": self.jwt_expiration_hours,
            "password_min_length": self.password_min_length,
            "password_require_special": self.password_require_special,
            "max_login_attempts": self.max_login_attempts,
            "lockout_duration_minutes": self.lockout_duration_minutes,
            "enable_2fa": self.enable_2fa,
            "allowed_origins": self.allowed_origins,
            "rate_limit_per_minute": self.rate_limit_per_minute,
            "enable_csrf_protection": self.enable_csrf_protection,
            "session_timeout_minutes": self.session_timeout_minutes,
        }


@dataclass
class MonitoringSettings:
    """Monitoring configuration settings."""

    enable_metrics: bool = True
    metrics_port: int = 9090
    enable_tracing: bool = True
    jaeger_endpoint: str = "http://localhost:14268/api/traces"
    enable_health_checks: bool = True
    health_check_interval: int = 30
    enable_alerts: bool = True
    alert_webhook_url: str = ""
    prometheus_pushgateway: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "enable_metrics": self.enable_metrics,
            "metrics_port": self.metrics_port,
            "enable_tracing": self.enable_tracing,
            "jaeger_endpoint": self.jaeger_endpoint,
            "enable_health_checks": self.enable_health_checks,
            "health_check_interval": self.health_check_interval,
            "enable_alerts": self.enable_alerts,
            "alert_webhook_url": self.alert_webhook_url,
            "prometheus_pushgateway": self.prometheus_pushgateway,
        }


@dataclass
class ConstitutionalSettings:
    """Constitutional compliance settings."""

    hash_value: str = "cdd01ef066bc6cf2"
    validation_enabled: bool = True
    strict_mode: bool = True
    audit_all_operations: bool = True
    require_hash_in_responses: bool = True
    compliance_check_interval: int = 60
    violation_alert_threshold: int = 1

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "hash_value": self.hash_value,
            "validation_enabled": self.validation_enabled,
            "strict_mode": self.strict_mode,
            "audit_all_operations": self.audit_all_operations,
            "require_hash_in_responses": self.require_hash_in_responses,
            "compliance_check_interval": self.compliance_check_interval,
            "violation_alert_threshold": self.violation_alert_threshold,
        }


@dataclass
class PerformanceSettings:
    """Performance optimization settings."""

    enable_caching: bool = True
    cache_strategy: str = "multi_level"  # memory, redis, multi_level
    connection_pool_size: int = 20
    max_workers: int = 4
    request_timeout: float = 30.0
    max_request_size: int = 10 * 1024 * 1024  # 10MB
    enable_compression: bool = True
    enable_circuit_breaker: bool = True
    circuit_breaker_threshold: int = 5

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "enable_caching": self.enable_caching,
            "cache_strategy": self.cache_strategy,
            "connection_pool_size": self.connection_pool_size,
            "max_workers": self.max_workers,
            "request_timeout": self.request_timeout,
            "max_request_size": self.max_request_size,
            "enable_compression": self.enable_compression,
            "enable_circuit_breaker": self.enable_circuit_breaker,
            "circuit_breaker_threshold": self.circuit_breaker_threshold,
        }


class Settings:
    """Main application settings."""

    def __init__(self, environment: str | None = None):
        self.environment = environment or os.getenv("ENVIRONMENT", "development")
        self._config_manager = get_config_manager()

        # Initialize settings from configuration
        self._load_settings()

    def _load_settings(self) -> None:
        """Load settings from configuration manager."""
        # Database settings
        db_config = self._config_manager.get_config("database", {})
        self.database = DatabaseSettings(
            host=db_config.get("host", "localhost"),
            port=db_config.get("port", 5432),
            database=db_config.get("database", "acgs"),
            username=db_config.get("username", "acgs_user"),
            password=db_config.get("password", ""),
            pool_size=db_config.get("pool_size", 20),
            max_overflow=db_config.get("max_overflow", 10),
            pool_timeout=db_config.get("pool_timeout", 30.0),
            pool_recycle=db_config.get("pool_recycle", 3600),
            ssl_mode=db_config.get("ssl_mode", "prefer"),
            echo=db_config.get("echo", False),
        )

        # Cache settings
        cache_config = self._config_manager.get_config("cache", {})
        self.cache = CacheSettings(
            redis_url=cache_config.get("redis_url", "redis://localhost:6379/0"),
            default_ttl=cache_config.get("default_ttl", 3600),
            max_connections=cache_config.get("max_connections", 50),
            key_prefix=cache_config.get("key_prefix", "acgs:"),
            compression=cache_config.get("compression", False),
            serializer=cache_config.get("serializer", "json"),
            cluster_mode=cache_config.get("cluster_mode", False),
            sentinel_hosts=cache_config.get("sentinel_hosts", []),
        )

        # Logging settings
        logging_config = self._config_manager.get_config("logging", {})
        self.logging = LoggingSettings(
            level=logging_config.get("level", "INFO"),
            format=logging_config.get(
                "format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            ),
            file_path=logging_config.get("file_path"),
            max_file_size=logging_config.get("max_file_size", 10 * 1024 * 1024),
            backup_count=logging_config.get("backup_count", 5),
            enable_console=logging_config.get("enable_console", True),
            enable_structured=logging_config.get("enable_structured", False),
            structured_format=logging_config.get("structured_format", "json"),
        )

        # Security settings
        security_config = self._config_manager.get_config("security", {})
        self.security = SecuritySettings(
            secret_key=security_config.get("secret_key", ""),
            jwt_algorithm=security_config.get("jwt_algorithm", "HS256"),
            jwt_expiration_hours=security_config.get("jwt_expiration_hours", 24),
            password_min_length=security_config.get("password_min_length", 8),
            password_require_special=security_config.get(
                "password_require_special", True
            ),
            max_login_attempts=security_config.get("max_login_attempts", 5),
            lockout_duration_minutes=security_config.get(
                "lockout_duration_minutes", 30
            ),
            enable_2fa=security_config.get("enable_2fa", False),
            allowed_origins=security_config.get("allowed_origins", ["*"]),
            rate_limit_per_minute=security_config.get("rate_limit_per_minute", 100),
            enable_csrf_protection=security_config.get("enable_csrf_protection", True),
            session_timeout_minutes=security_config.get("session_timeout_minutes", 60),
        )

        # Monitoring settings
        monitoring_config = self._config_manager.get_config("monitoring", {})
        self.monitoring = MonitoringSettings(
            enable_metrics=monitoring_config.get("enable_metrics", True),
            metrics_port=monitoring_config.get("metrics_port", 9090),
            enable_tracing=monitoring_config.get("enable_tracing", True),
            jaeger_endpoint=monitoring_config.get(
                "jaeger_endpoint", "http://localhost:14268/api/traces"
            ),
            enable_health_checks=monitoring_config.get("enable_health_checks", True),
            health_check_interval=monitoring_config.get("health_check_interval", 30),
            enable_alerts=monitoring_config.get("enable_alerts", True),
            alert_webhook_url=monitoring_config.get("alert_webhook_url", ""),
            prometheus_pushgateway=monitoring_config.get("prometheus_pushgateway", ""),
        )

        # Constitutional settings
        constitutional_config = self._config_manager.get_config("constitutional", {})
        self.constitutional = ConstitutionalSettings(
            hash_value=constitutional_config.get("hash_value", "cdd01ef066bc6cf2"),
            validation_enabled=constitutional_config.get("validation_enabled", True),
            strict_mode=constitutional_config.get("strict_mode", True),
            audit_all_operations=constitutional_config.get(
                "audit_all_operations", True
            ),
            require_hash_in_responses=constitutional_config.get(
                "require_hash_in_responses", True
            ),
            compliance_check_interval=constitutional_config.get(
                "compliance_check_interval", 60
            ),
            violation_alert_threshold=constitutional_config.get(
                "violation_alert_threshold", 1
            ),
        )

        # Performance settings
        performance_config = self._config_manager.get_config("performance", {})
        self.performance = PerformanceSettings(
            enable_caching=performance_config.get("enable_caching", True),
            cache_strategy=performance_config.get("cache_strategy", "multi_level"),
            connection_pool_size=performance_config.get("connection_pool_size", 20),
            max_workers=performance_config.get("max_workers", 4),
            request_timeout=performance_config.get("request_timeout", 30.0),
            max_request_size=performance_config.get(
                "max_request_size", 10 * 1024 * 1024
            ),
            enable_compression=performance_config.get("enable_compression", True),
            enable_circuit_breaker=performance_config.get(
                "enable_circuit_breaker", True
            ),
            circuit_breaker_threshold=performance_config.get(
                "circuit_breaker_threshold", 5
            ),
        )

        # Environment-specific overrides
        self._apply_environment_overrides()

    def _apply_environment_overrides(self) -> None:
        """Apply environment-specific setting overrides."""
        if self.environment == "development":
            self.database.echo = True
            self.logging.level = "DEBUG"
            self.security.enable_csrf_protection = False
            self.constitutional.strict_mode = False
        elif self.environment == "testing":
            self.database.database = "acgs_test"
            self.cache.redis_url = "redis://localhost:6379/1"
            self.logging.level = "WARNING"
            self.monitoring.enable_alerts = False
        elif self.environment == "production":
            self.logging.level = "INFO"
            self.security.enable_2fa = True
            self.constitutional.strict_mode = True
            self.performance.enable_circuit_breaker = True

    def reload(self) -> None:
        """Reload settings from configuration."""
        self._load_settings()
        logger.info(f"Settings reloaded for environment: {self.environment}")

    def get_database_url(self) -> str:
        """Get database connection URL."""
        return self.database.dsn

    def get_cache_url(self) -> str:
        """Get cache connection URL."""
        return self.cache.redis_url

    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"

    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"

    def is_testing(self) -> bool:
        """Check if running in testing mode."""
        return self.environment == "testing"

    def to_dict(self) -> dict[str, Any]:
        """Convert all settings to dictionary."""
        return {
            "environment": self.environment,
            "database": self.database.to_dict(),
            "cache": self.cache.to_dict(),
            "logging": self.logging.to_dict(),
            "security": self.security.to_dict(),
            "monitoring": self.monitoring.to_dict(),
            "constitutional": self.constitutional.to_dict(),
            "performance": self.performance.to_dict(),
            "constitutional_hash": "cdd01ef066bc6cf2",
        }

    def validate(self) -> list[str]:
        """Validate settings and return list of issues."""
        issues = []

        # Database validation
        if not self.database.password and self.is_production():
            issues.append("Database password is required in production")

        if self.database.pool_size < 1:
            issues.append("Database pool size must be at least 1")

        # Security validation
        if not self.security.secret_key:
            issues.append("Secret key is required")

        if len(self.security.secret_key) < 32:
            issues.append("Secret key should be at least 32 characters")

        # Constitutional validation
        if self.constitutional.hash_value != "cdd01ef066bc6cf2":
            issues.append("Invalid constitutional hash value")

        # Cache validation
        if not self.cache.redis_url:
            issues.append("Redis URL is required")

        return issues


# Global settings instance
_global_settings: Settings | None = None


def get_settings() -> Settings:
    """Get global settings instance."""
    global _global_settings
    if _global_settings is None:
        _global_settings = Settings()
    return _global_settings


def reload_settings() -> Settings:
    """Reload global settings."""
    global _global_settings
    _global_settings = Settings()
    return _global_settings


# Environment-specific setting loaders
def load_development_settings() -> Settings:
    """Load development environment settings."""
    return Settings("development")


def load_production_settings() -> Settings:
    """Load production environment settings."""
    return Settings("production")


def load_testing_settings() -> Settings:
    """Load testing environment settings."""
    return Settings("testing")


# Validation helpers
def validate_settings(settings: Settings = None) -> bool:
    """Validate settings and log issues."""
    if settings is None:
        settings = get_settings()

    issues = settings.validate()

    if issues:
        logger.error("Settings validation failed:")
        for issue in issues:
            logger.error(f"  - {issue}")
        return False
    logger.info("Settings validation passed")
    return True


# Configuration file helpers
def create_sample_config_files() -> None:
    """Create sample configuration files for each environment."""
    import json
    from pathlib import Path

    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)

    # Base configuration
    base_config = {
        "constitutional_hash": "cdd01ef066bc6cf2",
        "database": {
            "host": "localhost",
            "port": 5432,
            "database": "acgs",
            "username": "acgs_user",
            "password": "",
            "pool_size": 20,
            "max_overflow": 10,
            "ssl_mode": "prefer",
        },
        "cache": {
            "redis_url": "redis://localhost:6379/0",
            "default_ttl": 3600,
            "max_connections": 50,
            "key_prefix": "acgs:",
        },
        "security": {
            "secret_key": "your-secret-key-here-change-in-production",
            "jwt_algorithm": "HS256",
            "jwt_expiration_hours": 24,
            "max_login_attempts": 5,
        },
        "monitoring": {
            "enable_metrics": True,
            "enable_tracing": True,
            "enable_health_checks": True,
        },
        "constitutional": {
            "hash_value": "cdd01ef066bc6cf2",
            "validation_enabled": True,
            "strict_mode": True,
        },
    }

    # Write base config
    with open(config_dir / "config.json", "w", encoding="utf-8") as f:
        json.dump(base_config, f, indent=2)

    # Development config
    dev_config = base_config.copy()
    dev_config["database"]["echo"] = True
    dev_config["logging"] = {"level": "DEBUG"}
    dev_config["constitutional"]["strict_mode"] = False

    with open(config_dir / "config.development.json", "w", encoding="utf-8") as f:
        json.dump(dev_config, f, indent=2)

    # Production config
    prod_config = base_config.copy()
    prod_config["database"]["ssl_mode"] = "require"
    prod_config["security"]["enable_2fa"] = True
    prod_config["logging"] = {"level": "INFO", "file_path": "/var/log/acgs/app.log"}

    with open(config_dir / "config.production.json", "w", encoding="utf-8") as f:
        json.dump(prod_config, f, indent=2)

    logger.info(f"Sample configuration files created in {config_dir}")


if __name__ == "__main__":
    # Create sample config files if run directly
    create_sample_config_files()
