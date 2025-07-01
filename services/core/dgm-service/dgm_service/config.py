"""
Configuration settings for the Darwin Gödel Machine Service.
"""

from pydantic import BaseSettings, Field, validator


class Settings(BaseSettings):
    """Application settings."""

    # Service Configuration
    SERVICE_NAME: str = "dgm-service"
    HOST: str = Field(default="0.0.0.0", env="DGM_HOST")
    PORT: int = Field(default=8007, env="DGM_PORT")
    WORKERS: int = Field(default=4, env="DGM_WORKERS")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=False, env="DEBUG")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")

    # Security Configuration
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALLOWED_ORIGINS: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        env="ALLOWED_ORIGINS",
    )
    ALLOWED_HOSTS: list[str] = Field(
        default=["localhost", "127.0.0.1", "0.0.0.0"], env="ALLOWED_HOSTS"
    )

    # Database Configuration
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    DATABASE_POOL_SIZE: int = Field(default=20, env="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=30, env="DATABASE_MAX_OVERFLOW")
    DATABASE_POOL_TIMEOUT: int = Field(default=30, env="DATABASE_POOL_TIMEOUT")
    DATABASE_POOL_RECYCLE: int = Field(default=3600, env="DATABASE_POOL_RECYCLE")

    # Redis Configuration
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    REDIS_MAX_CONNECTIONS: int = Field(default=100, env="REDIS_MAX_CONNECTIONS")
    REDIS_RETRY_ON_TIMEOUT: bool = Field(default=True, env="REDIS_RETRY_ON_TIMEOUT")
    REDIS_SOCKET_TIMEOUT: int = Field(default=5, env="REDIS_SOCKET_TIMEOUT")
    REDIS_SOCKET_CONNECT_TIMEOUT: int = Field(
        default=5, env="REDIS_SOCKET_CONNECT_TIMEOUT"
    )
    REDIS_HEALTH_CHECK_INTERVAL: int = Field(
        default=30, env="REDIS_HEALTH_CHECK_INTERVAL"
    )

    # ACGS Service URLs
    AUTH_SERVICE_URL: str = Field(
        default="http://localhost:8000", env="AUTH_SERVICE_URL"
    )
    AC_SERVICE_URL: str = Field(default="http://localhost:8001", env="AC_SERVICE_URL")
    INTEGRITY_SERVICE_URL: str = Field(
        default="http://localhost:8002", env="INTEGRITY_SERVICE_URL"
    )
    FV_SERVICE_URL: str = Field(default="http://localhost:8003", env="FV_SERVICE_URL")
    GS_SERVICE_URL: str = Field(default="http://localhost:8004", env="GS_SERVICE_URL")
    PGC_SERVICE_URL: str = Field(default="http://localhost:8005", env="PGC_SERVICE_URL")
    EC_SERVICE_URL: str = Field(default="http://localhost:8006", env="EC_SERVICE_URL")

    # DGM Configuration
    CONSTITUTIONAL_COMPLIANCE_THRESHOLD: float = Field(
        default=0.8, env="CONSTITUTIONAL_COMPLIANCE_THRESHOLD"
    )
    IMPROVEMENT_CYCLE_INTERVAL: int = Field(
        default=3600, env="IMPROVEMENT_CYCLE_INTERVAL"
    )  # seconds
    MAX_IMPROVEMENT_ATTEMPTS: int = Field(default=5, env="MAX_IMPROVEMENT_ATTEMPTS")
    SAFETY_EXPLORATION_RATE: float = Field(default=0.1, env="SAFETY_EXPLORATION_RATE")
    ARCHIVE_RETENTION_DAYS: int = Field(default=365, env="ARCHIVE_RETENTION_DAYS")

    # Performance Monitoring
    PERFORMANCE_MONITORING_ENABLED: bool = Field(
        default=True, env="PERFORMANCE_MONITORING_ENABLED"
    )
    PERFORMANCE_METRICS_INTERVAL: int = Field(
        default=60, env="PERFORMANCE_METRICS_INTERVAL"
    )  # seconds
    PERFORMANCE_ALERT_THRESHOLD: float = Field(
        default=0.95, env="PERFORMANCE_ALERT_THRESHOLD"
    )

    # Foundation Model Configuration
    OPENAI_API_KEY: str | None = Field(default=None, env="OPENAI_API_KEY")
    ANTHROPIC_API_KEY: str | None = Field(default=None, env="ANTHROPIC_API_KEY")
    MODEL_TIMEOUT: int = Field(default=30, env="MODEL_TIMEOUT")
    MODEL_MAX_RETRIES: int = Field(default=3, env="MODEL_MAX_RETRIES")

    # Bandit Algorithm Configuration
    BANDIT_ALGORITHM: str = Field(
        default="ucb", env="BANDIT_ALGORITHM"
    )  # ucb, epsilon_greedy, thompson
    BANDIT_EXPLORATION_PARAMETER: float = Field(
        default=2.0, env="BANDIT_EXPLORATION_PARAMETER"
    )
    BANDIT_DECAY_RATE: float = Field(default=0.99, env="BANDIT_DECAY_RATE")

    # Monitoring and Observability
    PROMETHEUS_ENABLED: bool = Field(default=True, env="PROMETHEUS_ENABLED")
    JAEGER_ENABLED: bool = Field(default=False, env="JAEGER_ENABLED")
    JAEGER_ENDPOINT: str | None = Field(default=None, env="JAEGER_ENDPOINT")

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    RATE_LIMIT_REQUESTS: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_WINDOW: int = Field(default=60, env="RATE_LIMIT_WINDOW")  # seconds

    @validator("ALLOWED_ORIGINS", pre=True)
    def parse_allowed_origins(cls, v):
        """Parse allowed origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @validator("ALLOWED_HOSTS", pre=True)
    def parse_allowed_hosts(cls, v):
        """Parse allowed hosts from string or list."""
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v

    @validator("CONSTITUTIONAL_COMPLIANCE_THRESHOLD")
    def validate_compliance_threshold(cls, v):
        """Validate compliance threshold is between 0 and 1."""
        if not 0 <= v <= 1:
            raise ValueError(
                "Constitutional compliance threshold must be between 0 and 1"
            )
        return v

    @validator("SAFETY_EXPLORATION_RATE")
    def validate_exploration_rate(cls, v):
        """Validate exploration rate is between 0 and 1."""
        if not 0 <= v <= 1:
            raise ValueError("Safety exploration rate must be between 0 and 1")
        return v

    @validator("PERFORMANCE_ALERT_THRESHOLD")
    def validate_alert_threshold(cls, v):
        """Validate alert threshold is between 0 and 1."""
        if not 0 <= v <= 1:
            raise ValueError("Performance alert threshold must be between 0 and 1")
        return v

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()
