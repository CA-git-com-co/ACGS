"""
ACGS FastAPI Service Configuration Template
Constitutional Hash: cdd01ef066bc6cf2

This module provides standardized configuration management for ACGS services including:
- Environment-based configuration
- Constitutional compliance settings
- Multi-tenant configuration
- Database and Redis configuration
- Security and authentication settings
- Monitoring and observability configuration
"""

import os
from functools import lru_cache
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseSettings, validator, Field

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class DatabaseConfig(BaseSettings):
    """Database configuration settings."""
    
    # Connection settings
    url: str = Field(
        default="postgresql+asyncpg://acgs_user:acgs_password@localhost:5432/acgs_db",
        env="DATABASE_URL",
        description="Database connection URL"
    )
    
    # Connection pool settings
    pool_size: int = Field(
        default=10,
        env="DATABASE_POOL_SIZE",
        description="Database connection pool size"
    )
    
    max_overflow: int = Field(
        default=20,
        env="DATABASE_MAX_OVERFLOW",
        description="Maximum connection pool overflow"
    )
    
    pool_timeout: int = Field(
        default=30,
        env="DATABASE_POOL_TIMEOUT",
        description="Connection pool timeout in seconds"
    )
    
    pool_recycle: int = Field(
        default=1800,
        env="DATABASE_POOL_RECYCLE",
        description="Connection recycle time in seconds"
    )
    
    # Query settings
    echo: bool = Field(
        default=False,
        env="DATABASE_ECHO",
        description="Enable SQL query logging"
    )
    
    # Multi-tenant settings
    enable_rls: bool = Field(
        default=True,
        env="DATABASE_ENABLE_RLS",
        description="Enable Row-Level Security for multi-tenancy"
    )


class RedisConfig(BaseSettings):
    """Redis configuration settings."""
    
    # Connection settings
    url: str = Field(
        default="redis://localhost:6379/0",
        env="REDIS_URL",
        description="Redis connection URL"
    )
    
    # Connection pool settings
    max_connections: int = Field(
        default=20,
        env="REDIS_MAX_CONNECTIONS",
        description="Maximum Redis connections"
    )
    
    # Caching settings
    default_ttl: int = Field(
        default=3600,
        env="REDIS_DEFAULT_TTL",
        description="Default cache TTL in seconds"
    )
    
    key_prefix: str = Field(
        default="acgs",
        env="REDIS_KEY_PREFIX",
        description="Prefix for Redis keys"
    )


class SecurityConfig(BaseSettings):
    """Security and authentication configuration."""
    
    # JWT settings
    jwt_secret_key: str = Field(
        default="your-secret-key-change-in-production",
        env="JWT_SECRET_KEY",
        description="JWT signing secret key"
    )
    
    jwt_algorithm: str = Field(
        default="HS256",
        env="JWT_ALGORITHM",
        description="JWT signing algorithm"
    )
    
    jwt_access_token_expire_minutes: int = Field(
        default=30,
        env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
        description="JWT access token expiration in minutes"
    )
    
    # CORS settings
    cors_origins: List[str] = Field(
        default=["*"],
        env="CORS_ORIGINS",
        description="Allowed CORS origins"
    )
    
    cors_allow_credentials: bool = Field(
        default=True,
        env="CORS_ALLOW_CREDENTIALS",
        description="Allow credentials in CORS requests"
    )
    
    # Host validation
    allowed_hosts: List[str] = Field(
        default=["*"],
        env="ALLOWED_HOSTS",
        description="Allowed host names"
    )
    
    # Rate limiting
    rate_limit_requests_per_minute: int = Field(
        default=60,
        env="RATE_LIMIT_REQUESTS_PER_MINUTE",
        description="Rate limit: requests per minute"
    )
    
    rate_limit_burst: int = Field(
        default=10,
        env="RATE_LIMIT_BURST",
        description="Rate limit: burst capacity"
    )
    
    @validator('cors_origins', pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from environment variable."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator('allowed_hosts', pre=True)
    def parse_allowed_hosts(cls, v):
        """Parse allowed hosts from environment variable."""
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v


class ConstitutionalConfig(BaseSettings):
    """Constitutional compliance configuration."""
    
    # Core constitutional settings
    hash: str = Field(
        default=CONSTITUTIONAL_HASH,
        env="CONSTITUTIONAL_HASH",
        description="Constitutional compliance hash"
    )
    
    compliance_required: bool = Field(
        default=True,
        env="CONSTITUTIONAL_COMPLIANCE_REQUIRED",
        description="Whether constitutional compliance is required"
    )
    
    compliance_threshold: float = Field(
        default=0.8,
        env="CONSTITUTIONAL_COMPLIANCE_THRESHOLD",
        ge=0.0,
        le=1.0,
        description="Minimum constitutional compliance score"
    )
    
    # Validation settings
    validate_on_startup: bool = Field(
        default=True,
        env="CONSTITUTIONAL_VALIDATE_ON_STARTUP",
        description="Validate constitutional compliance on service startup"
    )
    
    validate_on_request: bool = Field(
        default=True,
        env="CONSTITUTIONAL_VALIDATE_ON_REQUEST",
        description="Validate constitutional compliance on each request"
    )
    
    # Audit settings
    audit_constitutional_violations: bool = Field(
        default=True,
        env="CONSTITUTIONAL_AUDIT_VIOLATIONS",
        description="Audit constitutional compliance violations"
    )
    
    @validator('hash')
    def validate_constitutional_hash(cls, v):
        """Validate constitutional hash format."""
        if len(v) != 16:  # Expected length for hash
            raise ValueError(f"Invalid constitutional hash format: {v}")
        return v


class MultiTenantConfig(BaseSettings):
    """Multi-tenant configuration settings."""
    
    # Core multi-tenant settings
    enabled: bool = Field(
        default=True,
        env="MULTI_TENANT_ENABLED",
        description="Enable multi-tenant functionality"
    )
    
    tenant_required: bool = Field(
        default=True,
        env="MULTI_TENANT_REQUIRED",
        description="Require tenant context for all requests"
    )
    
    # Tenant isolation settings
    enforce_rls: bool = Field(
        default=True,
        env="MULTI_TENANT_ENFORCE_RLS",
        description="Enforce row-level security for tenant isolation"
    )
    
    tenant_header_name: str = Field(
        default="X-Tenant-ID",
        env="MULTI_TENANT_HEADER_NAME",
        description="Header name for tenant identification"
    )
    
    # Cross-tenant settings
    allow_cross_tenant_access: bool = Field(
        default=False,
        env="MULTI_TENANT_ALLOW_CROSS_TENANT",
        description="Allow cross-tenant access for admin users"
    )
    
    admin_bypass_tenant_isolation: bool = Field(
        default=True,
        env="MULTI_TENANT_ADMIN_BYPASS",
        description="Allow admin users to bypass tenant isolation"
    )


class MonitoringConfig(BaseSettings):
    """Monitoring and observability configuration."""
    
    # Logging settings
    log_level: str = Field(
        default="INFO",
        env="LOG_LEVEL",
        description="Logging level"
    )
    
    log_format: str = Field(
        default="json",
        env="LOG_FORMAT",
        description="Log format (json or text)"
    )
    
    log_requests: bool = Field(
        default=True,
        env="LOG_REQUESTS",
        description="Log HTTP requests"
    )
    
    # Metrics settings
    enable_metrics: bool = Field(
        default=True,
        env="ENABLE_METRICS",
        description="Enable metrics collection"
    )
    
    metrics_port: int = Field(
        default=9090,
        env="METRICS_PORT",
        description="Port for metrics endpoint"
    )
    
    # Health check settings
    health_check_interval: int = Field(
        default=30,
        env="HEALTH_CHECK_INTERVAL",
        description="Health check interval in seconds"
    )
    
    # Tracing settings
    enable_tracing: bool = Field(
        default=False,
        env="ENABLE_TRACING",
        description="Enable distributed tracing"
    )
    
    jaeger_endpoint: Optional[str] = Field(
        default=None,
        env="JAEGER_ENDPOINT",
        description="Jaeger tracing endpoint"
    )
    
    @validator('log_level')
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level: {v}. Must be one of {valid_levels}")
        return v.upper()


class APIConfig(BaseSettings):
    """API configuration settings."""
    
    # Basic API settings
    title: str = Field(
        default="ACGS Service",
        env="API_TITLE",
        description="API title for documentation"
    )
    
    description: str = Field(
        default="ACGS service with constitutional compliance",
        env="API_DESCRIPTION",
        description="API description for documentation"
    )
    
    version: str = Field(
        default="1.0.0",
        env="API_VERSION",
        description="API version"
    )
    
    prefix: str = Field(
        default="/api/v1",
        env="API_PREFIX",
        description="API URL prefix"
    )
    
    # Documentation settings
    enable_docs: bool = Field(
        default=True,
        env="API_ENABLE_DOCS",
        description="Enable API documentation"
    )
    
    enable_redoc: bool = Field(
        default=True,
        env="API_ENABLE_REDOC",
        description="Enable ReDoc documentation"
    )
    
    docs_url: Optional[str] = Field(
        default="/docs",
        env="API_DOCS_URL",
        description="URL for Swagger UI documentation"
    )
    
    redoc_url: Optional[str] = Field(
        default="/redoc",
        env="API_REDOC_URL",
        description="URL for ReDoc documentation"
    )
    
    # Request/Response settings
    max_request_size: int = Field(
        default=10 * 1024 * 1024,  # 10MB
        env="API_MAX_REQUEST_SIZE",
        description="Maximum request size in bytes"
    )
    
    request_timeout: int = Field(
        default=30,
        env="API_REQUEST_TIMEOUT",
        description="Request timeout in seconds"
    )


class ServiceConfig(BaseSettings):
    """Main service configuration combining all config sections."""
    
    # Service identification
    name: str = Field(
        default="acgs-service",
        env="SERVICE_NAME",
        description="Service name"
    )
    
    version: str = Field(
        default="1.0.0",
        env="SERVICE_VERSION",
        description="Service version"
    )
    
    description: str = Field(
        default="ACGS service with constitutional compliance",
        env="SERVICE_DESCRIPTION",
        description="Service description"
    )
    
    # Environment settings
    environment: str = Field(
        default="development",
        env="ENVIRONMENT",
        description="Deployment environment"
    )
    
    debug: bool = Field(
        default=False,
        env="DEBUG",
        description="Enable debug mode"
    )
    
    # Server settings
    host: str = Field(
        default="0.0.0.0",
        env="SERVICE_HOST",
        description="Service host"
    )
    
    port: int = Field(
        default=8000,
        env="SERVICE_PORT",
        description="Service port"
    )
    
    # Component configurations
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    constitutional: ConstitutionalConfig = Field(default_factory=ConstitutionalConfig)
    multi_tenant: MultiTenantConfig = Field(default_factory=MultiTenantConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        # Allow reading from multiple .env files
        env_nested_delimiter = "__"
    
    @validator('environment')
    def validate_environment(cls, v):
        """Validate environment setting."""
        valid_environments = ["development", "staging", "production", "test"]
        if v.lower() not in valid_environments:
            raise ValueError(f"Invalid environment: {v}. Must be one of {valid_environments}")
        return v.lower()
    
    def get_database_url(self) -> str:
        """Get the complete database URL."""
        return self.database.url
    
    def get_redis_url(self) -> str:
        """Get the complete Redis URL."""
        return self.redis.url
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"
    
    def get_cors_settings(self) -> Dict[str, Any]:
        """Get CORS settings for FastAPI."""
        return {
            "allow_origins": self.security.cors_origins,
            "allow_credentials": self.security.cors_allow_credentials,
            "allow_methods": ["*"],
            "allow_headers": ["*"],
        }
    
    def get_api_metadata(self) -> Dict[str, Any]:
        """Get API metadata for FastAPI app creation."""
        return {
            "title": self.api.title,
            "description": self.api.description,
            "version": self.api.version,
            "docs_url": self.api.docs_url if self.api.enable_docs else None,
            "redoc_url": self.api.redoc_url if self.api.enable_redoc else None,
            "openapi_url": f"{self.api.prefix}/openapi.json",
        }


@lru_cache()
def get_settings() -> ServiceConfig:
    """
    Get cached service settings.
    
    This function provides a cached instance of the service configuration
    that can be used throughout the application.
    """
    return ServiceConfig()


# Environment-specific configuration factories
def get_development_config() -> ServiceConfig:
    """Get configuration for development environment."""
    config = ServiceConfig()
    config.environment = "development"
    config.debug = True
    config.api.enable_docs = True
    config.api.enable_redoc = True
    config.monitoring.log_level = "DEBUG"
    config.database.echo = True
    return config


def get_production_config() -> ServiceConfig:
    """Get configuration for production environment."""
    config = ServiceConfig()
    config.environment = "production"
    config.debug = False
    config.api.enable_docs = False
    config.api.enable_redoc = False
    config.monitoring.log_level = "WARNING"
    config.database.echo = False
    config.security.cors_origins = []  # Must be explicitly set in production
    return config


def get_test_config() -> ServiceConfig:
    """Get configuration for testing environment."""
    config = ServiceConfig()
    config.environment = "test"
    config.debug = True
    config.database.url = "sqlite+aiosqlite:///./test.db"
    config.redis.url = "redis://localhost:6379/15"  # Use separate Redis DB for tests
    config.monitoring.log_level = "ERROR"  # Reduce log noise in tests
    return config


# Configuration validation utilities
def validate_production_config(config: ServiceConfig) -> List[str]:
    """
    Validate configuration for production deployment.
    
    Returns a list of configuration issues that should be addressed
    before deploying to production.
    """
    issues = []
    
    # Security checks
    if config.security.jwt_secret_key == "your-secret-key-change-in-production":
        issues.append("JWT secret key must be changed for production")
    
    if "*" in config.security.cors_origins:
        issues.append("CORS origins should be explicitly set for production")
    
    if "*" in config.security.allowed_hosts:
        issues.append("Allowed hosts should be explicitly set for production")
    
    # Database checks
    if "localhost" in config.database.url:
        issues.append("Database URL should not use localhost in production")
    
    # Constitutional compliance checks
    if not config.constitutional.compliance_required:
        issues.append("Constitutional compliance should be required in production")
    
    if config.constitutional.hash != CONSTITUTIONAL_HASH:
        issues.append(f"Constitutional hash mismatch: expected {CONSTITUTIONAL_HASH}")
    
    return issues


# Export main configuration
__all__ = [
    "ServiceConfig",
    "get_settings",
    "get_development_config",
    "get_production_config", 
    "get_test_config",
    "validate_production_config",
    "CONSTITUTIONAL_HASH"
]