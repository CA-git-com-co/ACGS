"""
Centralized Configuration using Pydantic Settings
Constitutional Hash: cdd01ef066bc6cf2

This module provides centralized configuration management using pydantic-settings
with support for environment variables and .env.acgs file.
"""

import logging

from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""

    model_config = SettingsConfigDict(
        env_prefix="POSTGRES_",
        case_sensitive=False,
    )

    user: str = Field(default="acgs_user", description="Database user")
    password: str = Field(default="", description="Database password")
    host: str = Field(default="localhost", description="Database host")
    port: int = Field(default=5440, description="Database port")
    db: str = Field(default="acgs_db", description="Database name")
    pool_size: int = Field(default=10, description="Connection pool size")
    max_overflow: int = Field(default=5, description="Max overflow connections")

    @property
    def url(self) -> str:
        """Get database URL."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"

    @property
    def async_url(self) -> str:
        """Get async database URL."""
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"


class RedisSettings(BaseSettings):
    """Redis configuration settings."""

    model_config = SettingsConfigDict(
        env_prefix="REDIS_",
        case_sensitive=False,
    )

    host: str = Field(default="localhost", description="Redis host")
    port: int = Field(default=6390, description="Redis port")
    password: str | None = Field(default=None, description="Redis password")
    db: int = Field(default=0, description="Redis database number")
    connection_pool_size: int = Field(default=10, description="Connection pool size")

    @property
    def url(self) -> str:
        """Get Redis URL."""
        auth_part = f":{self.password}@" if self.password else ""
        return f"redis://{auth_part}{self.host}:{self.port}/{self.db}"


class SecuritySettings(BaseSettings):
    """Security configuration settings."""

    model_config = SettingsConfigDict(
        env_prefix="",
        case_sensitive=False,
    )

    auth_secret_key: str = Field(..., description="Authentication secret key")
    jwt_secret_key: str = Field(..., description="JWT secret key")
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_access_token_expire_minutes: int = Field(default=30, description="JWT expiration minutes")

    # CORS settings
    backend_cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="CORS origins"
    )
    allowed_hosts: list[str] = Field(
        default=["localhost", "127.0.0.1"],
        description="Allowed hosts"
    )

    @validator("backend_cors_origins", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @validator("allowed_hosts", pre=True)
    def assemble_allowed_hosts(cls, v):
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v


class ServicePortSettings(BaseSettings):
    """Service port configuration."""

    model_config = SettingsConfigDict(
        env_prefix="",
        case_sensitive=False,
    )

    api_gateway_port: int = Field(default=8080, description="API Gateway port")
    constitutional_ai_port: int = Field(default=8001, description="Constitutional AI service port")
    integrity_service_port: int = Field(default=8002, description="Integrity service port")
    governance_engine_port: int = Field(default=8004, description="Governance engine port")
    ec_service_port: int = Field(default=8006, description="Evolutionary computation port")
    auth_service_port: int = Field(default=8016, description="Authentication service port")
    rules_engine_port: int = Field(default=8020, description="Rules engine port")
    coordinator_port: int = Field(default=8008, description="Multi-agent coordinator port")
    blackboard_port: int = Field(default=8010, description="Blackboard service port")
    prometheus_port: int = Field(default=9090, description="Prometheus port")
    grafana_port: int = Field(default=3001, description="Grafana port")


class PerformanceSettings(BaseSettings):
    """Performance configuration settings."""

    model_config = SettingsConfigDict(
        env_prefix="ACGS_PERFORMANCE_",
        case_sensitive=False,
    )

    p99_target: int = Field(default=5, description="P99 latency target (ms)")
    rps_target: int = Field(default=100, description="RPS target")
    cache_hit_rate_target: int = Field(default=85, description="Cache hit rate target (%)")
    constitutional_fidelity_threshold: float = Field(default=0.85, description="Constitutional fidelity threshold")
    policy_quality_threshold: float = Field(default=0.80, description="Policy quality threshold")
    max_synthesis_loops: int = Field(default=3, description="Max synthesis loops")
    pgc_latency_target: int = Field(default=25, description="PGC latency target (ms)")


class MonitoringSettings(BaseSettings):
    """Monitoring and observability settings."""

    model_config = SettingsConfigDict(
        env_prefix="",
        case_sensitive=False,
    )

    enable_metrics: bool = Field(default=True, description="Enable metrics collection")
    enable_tracing: bool = Field(default=True, description="Enable distributed tracing")
    prometheus_retention: str = Field(default="200h", description="Prometheus retention period")
    grafana_admin_user: str = Field(default="admin", description="Grafana admin user")
    grafana_admin_password: str = Field(default="", description="Grafana admin password")


class ConstitutionalSettings(BaseSettings):
    """Constitutional governance settings."""

    model_config = SettingsConfigDict(
        env_prefix="CONSTITUTIONAL_",
        case_sensitive=False,
    )

    hash: str = Field(default=CONSTITUTIONAL_HASH, description="Constitutional hash")
    validation_enabled: bool = Field(default=True, description="Enable constitutional validation")
    audit_enabled: bool = Field(default=True, description="Enable constitutional audit")


class ACGSSettings(BaseSettings):
    """
    Main ACGS configuration settings.
    
    This class combines all configuration subsections and provides
    a central configuration object for the entire system.
    """

    model_config = SettingsConfigDict(
        env_file=".env.acgs",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Core settings
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH, description="Constitutional hash")
    environment: str = Field(default="development", description="Environment")
    log_level: str = Field(default="INFO", description="Log level")

    # Subsection settings
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    ports: ServicePortSettings = Field(default_factory=ServicePortSettings)
    performance: PerformanceSettings = Field(default_factory=PerformanceSettings)
    monitoring: MonitoringSettings = Field(default_factory=MonitoringSettings)
    constitutional: ConstitutionalSettings = Field(default_factory=ConstitutionalSettings)

    # Service discovery
    enable_service_discovery: bool = Field(default=True, description="Enable service discovery")
    service_discovery_registry: str = Field(default="redis", description="Service discovery registry")

    # Rate limiting
    rate_limit_requests_per_minute: int = Field(default=1000, description="Rate limit requests per minute")
    rate_limit_burst: int = Field(default=100, description="Rate limit burst")

    # Gateway settings
    gateway_enable_docs: bool = Field(default=True, description="Enable gateway documentation")

    # AI models
    google_gemini_enabled: bool = Field(default=True, description="Enable Google Gemini")
    deepseek_r1_enabled: bool = Field(default=True, description="Enable DeepSeek R1")
    nvidia_qwen_enabled: bool = Field(default=True, description="Enable NVIDIA Qwen")
    nano_vllm_enabled: bool = Field(default=True, description="Enable Nano vLLM")

    # Evolutionary computation
    wina_enabled: bool = Field(default=True, description="Enable WINA")
    evolutionary_computation_enabled: bool = Field(default=True, description="Enable evolutionary computation")

    # Health checks
    health_check_interval: str = Field(default="30s", description="Health check interval")
    health_check_timeout: str = Field(default="10s", description="Health check timeout")
    health_check_retries: int = Field(default=3, description="Health check retries")
    health_check_start_period: str = Field(default="60s", description="Health check start period")

    # OPA configuration
    opa_server_url: str = Field(default="http://opa:8181", description="OPA server URL")

    # Blockchain settings (optional)
    solana_network: str = Field(default="devnet", description="Solana network")
    anchor_provider_url: str = Field(default="https://api.devnet.solana.com", description="Anchor provider URL")

    def __init__(self, **kwargs):
        """Initialize settings with constitutional validation."""
        super().__init__(**kwargs)
        self._validate_constitutional_integrity()

        # Load subsection settings with environment variables
        self.database = DatabaseSettings()
        self.redis = RedisSettings()
        self.security = SecuritySettings()
        self.ports = ServicePortSettings()
        self.performance = PerformanceSettings()
        self.monitoring = MonitoringSettings()
        self.constitutional = ConstitutionalSettings()

        logger.info(f"✅ ACGS configuration loaded with constitutional hash: {self.constitutional_hash}")

    def _validate_constitutional_integrity(self):
        """Validate constitutional integrity."""
        if self.constitutional_hash != CONSTITUTIONAL_HASH:
            raise ValueError(f"Constitutional hash mismatch: expected {CONSTITUTIONAL_HASH}, got {self.constitutional_hash}")

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"

    @property
    def database_url(self) -> str:
        """Get database URL."""
        return self.database.url

    @property
    def async_database_url(self) -> str:
        """Get async database URL."""
        return self.database.async_url

    @property
    def redis_url(self) -> str:
        """Get Redis URL."""
        return self.redis.url

    def get_service_url(self, service_name: str) -> str:
        """Get service URL by name."""
        port_mapping = {
            "api_gateway": self.ports.api_gateway_port,
            "constitutional_ai": self.ports.constitutional_ai_port,
            "integrity": self.ports.integrity_service_port,
            "governance_engine": self.ports.governance_engine_port,
            "evolutionary_computation": self.ports.ec_service_port,
            "auth": self.ports.auth_service_port,
            "rules_engine": self.ports.rules_engine_port,
            "coordinator": self.ports.coordinator_port,
            "blackboard": self.ports.blackboard_port,
        }

        port = port_mapping.get(service_name)
        if port is None:
            raise ValueError(f"Unknown service: {service_name}")

        return f"http://localhost:{port}"


# Global settings instance
_settings: ACGSSettings | None = None


def get_settings() -> ACGSSettings:
    """Get the global settings instance."""
    global _settings
    if _settings is None:
        _settings = ACGSSettings()
    return _settings


def reload_settings() -> ACGSSettings:
    """Reload settings from environment."""
    global _settings
    _settings = ACGSSettings()
    logger.info("🔄 Settings reloaded")
    return _settings
