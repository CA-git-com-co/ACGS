"""
Unified Governance Engine Configuration
Constitutional Hash: cdd01ef066bc6cf2
"""

import os

from pydantic import BaseModel, Field


class DatabaseConfig(BaseModel):
    """Database configuration."""

    url: str = Field(
        default_factory=lambda: os.getenv(
            "DATABASE_URL",
            "postgresql+asyncpg://acgs_user:acgs_password@localhost:5439/acgs_db",
        )
    )
    pool_size: int = Field(default=10)
    max_overflow: int = Field(default=20)
    pool_timeout: int = Field(default=30)
    pool_recycle: int = Field(default=3600)


class RedisConfig(BaseModel):
    """Redis configuration."""

    url: str = Field(
        default_factory=lambda: os.getenv("REDIS_URL", "redis://localhost:6389/0")
    )
    max_connections: int = Field(default=100)
    retry_on_timeout: bool = Field(default=True)
    decode_responses: bool = Field(default=True)


class SecurityConfig(BaseModel):
    """Security configuration."""

    constitutional_hash: str = Field(default="cdd01ef066bc6cf2")
    jwt_secret_key: str = Field(
        default_factory=lambda: os.getenv("JWT_SECRET_KEY", "dev-secret-key")
    )
    jwt_algorithm: str = Field(default="HS256")
    jwt_expire_minutes: int = Field(default=60)
    cors_origins: list[str] = Field(default=["*"])
    trusted_hosts: list[str] = Field(default=["*"])


class ServiceConfig(BaseModel):
    """Service configuration."""

    name: str = Field(default="governance-engine")
    port: int = Field(default_factory=lambda: int(os.getenv("SERVICE_PORT", "8004")))
    host: str = Field(default="0.0.0.0")
    log_level: str = Field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    debug: bool = Field(
        default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true"
    )
    environment: str = Field(
        default_factory=lambda: os.getenv("ENVIRONMENT", "development")
    )


class ExternalServiceConfig(BaseModel):
    """External service configuration."""

    constitutional_ai_url: str = Field(
        default_factory=lambda: os.getenv(
            "CONSTITUTIONAL_AI_URL", "http://localhost:8001"
        )
    )
    formal_verification_url: str = Field(
        default_factory=lambda: os.getenv(
            "FORMAL_VERIFICATION_URL", "http://localhost:8003"
        )
    )
    integrity_service_url: str = Field(
        default_factory=lambda: os.getenv(
            "INTEGRITY_SERVICE_URL", "http://localhost:8002"
        )
    )
    auth_service_url: str = Field(
        default_factory=lambda: os.getenv("AUTH_SERVICE_URL", "http://localhost:8016")
    )
    opa_server_url: str = Field(
        default_factory=lambda: os.getenv("OPA_SERVER_URL", "http://localhost:8181")
    )


class PerformanceConfig(BaseModel):
    """Performance configuration."""

    synthesis_timeout_seconds: int = Field(default=30)
    enforcement_timeout_seconds: int = Field(default=5)
    compliance_timeout_seconds: int = Field(default=10)
    cache_ttl_seconds: int = Field(default=300)
    max_concurrent_requests: int = Field(default=100)

    # Performance targets
    synthesis_p99_target_ms: int = Field(default=5000)
    enforcement_p99_target_ms: int = Field(default=5)
    compliance_p99_target_ms: int = Field(default=100)


class GovernanceEngineConfig(BaseModel):
    """Complete governance engine configuration."""

    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    service: ServiceConfig = Field(default_factory=ServiceConfig)
    external_services: ExternalServiceConfig = Field(
        default_factory=ExternalServiceConfig
    )
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)

    class Config:
        env_file = "config/environments/development.env"
        env_nested_delimiter = "__"


# Global configuration instance
config = GovernanceEngineConfig()


def get_config() -> GovernanceEngineConfig:
    """Get the application configuration."""
    return config
