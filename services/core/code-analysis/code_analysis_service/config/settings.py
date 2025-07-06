"""
ACGS Code Analysis Engine - Configuration Settings
Pydantic-based configuration management with environment variable support.

Constitutional Hash: cdd01ef066bc6cf2
"""

import os
from typing import List, Optional, Dict, Any
from functools import lru_cache

from pydantic import Field, field_validator, AnyHttpUrl, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # ============================================================================
    # SERVICE CONFIGURATION
    # ============================================================================
    
    # Service identity
    service_name: str = Field(
        default="acgs-code-analysis-engine",
        description="Service name for registration and logging"
    )
    
    service_version: str = Field(
        default="1.0.0",
        description="Service version"
    )
    
    # Server configuration
    host: str = Field(
        default="0.0.0.0",
        env="ACGS_CODE_ANALYSIS_HOST",
        description="Host to bind the service to"
    )
    
    port: int = Field(
        default=8007,
        env="ACGS_CODE_ANALYSIS_PORT",
        description="Port to bind the service to"
    )
    
    workers: int = Field(
        default=4,
        env="ACGS_CODE_ANALYSIS_WORKERS",
        description="Number of worker processes for production"
    )
    
    # Environment configuration
    environment: str = Field(
        default="development",
        env="ENVIRONMENT",
        description="Application environment (development, staging, production)"
    )
    
    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v):
        allowed = ["development", "staging", "production", "testing"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of: {allowed}")
        return v
    
    # ============================================================================
    # DATABASE CONFIGURATION (ACGS PostgreSQL - Port 5439)
    # ============================================================================
    
    # PostgreSQL connection
    postgresql_host: str = Field(
        default="localhost",
        env="POSTGRESQL_HOST",
        description="PostgreSQL host"
    )
    
    postgresql_port: int = Field(
        default=5439,
        env="POSTGRESQL_PORT",
        description="PostgreSQL port (ACGS standard)"
    )
    
    postgresql_database: str = Field(
        default="acgs",
        env="POSTGRESQL_DATABASE",
        description="PostgreSQL database name"
    )
    
    postgresql_user: str = Field(
        default="acgs_user",
        env="POSTGRESQL_USER",
        description="PostgreSQL username"
    )
    
    postgresql_password: str = Field(
        default="development_password",
        env="POSTGRESQL_PASSWORD",
        description="PostgreSQL password"
    )
    
    postgresql_pool_size: int = Field(
        default=20,
        env="POSTGRESQL_POOL_SIZE",
        description="PostgreSQL connection pool size"
    )
    
    postgresql_max_overflow: int = Field(
        default=10,
        env="POSTGRESQL_MAX_OVERFLOW",
        description="PostgreSQL connection pool max overflow"
    )
    
    @property
    def database_url(self) -> str:
        """Construct PostgreSQL database URL"""
        return (
            f"postgresql+asyncpg://"
            f"{self.postgresql_user}:{self.postgresql_password}@"
            f"{self.postgresql_host}:{self.postgresql_port}/"
            f"{self.postgresql_database}"
        )
    
    # ============================================================================
    # REDIS CONFIGURATION (ACGS Redis - Port 6389)
    # ============================================================================
    
    # Redis connection
    redis_host: str = Field(
        default="localhost",
        env="REDIS_HOST",
        description="Redis host"
    )
    
    redis_port: int = Field(
        default=6389,
        env="REDIS_PORT",
        description="Redis port (ACGS standard)"
    )
    
    redis_db: int = Field(
        default=3,
        env="REDIS_DB",
        description="Redis database number for code analysis"
    )
    
    redis_password: Optional[str] = Field(
        default=None,
        env="REDIS_PASSWORD",
        description="Redis password"
    )
    
    redis_pool_size: int = Field(
        default=20,
        env="REDIS_POOL_SIZE",
        description="Redis connection pool size"
    )
    
    @property
    def redis_url(self) -> str:
        """Construct Redis URL"""
        auth_part = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{auth_part}{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    # ============================================================================
    # SERVICE INTEGRATION CONFIGURATION
    # ============================================================================
    
    # Auth Service (Port 8016)
    auth_service_url: AnyHttpUrl = Field(
        default="http://localhost:8016",
        env="AUTH_SERVICE_URL",
        description="ACGS Auth Service URL"
    )
    
    # Context Service (Port 8012)
    context_service_url: AnyHttpUrl = Field(
        default="http://localhost:8012",
        env="CONTEXT_SERVICE_URL",
        description="ACGS Context Service URL"
    )
    
    # Service Registry
    service_registry_url: AnyHttpUrl = Field(
        default="http://localhost:8001/registry",
        env="SERVICE_REGISTRY_URL",
        description="ACGS Service Registry URL"
    )
    
    # ============================================================================
    # CONSTITUTIONAL COMPLIANCE CONFIGURATION
    # ============================================================================
    
    # Constitutional compliance
    constitutional_hash: str = Field(
        default="cdd01ef066bc6cf2",
        env="CONSTITUTIONAL_HASH",
        description="ACGS constitutional compliance hash"
    )
    
    audit_enabled: bool = Field(
        default=True,
        env="AUDIT_ENABLED",
        description="Enable audit logging"
    )
    
    compliance_strict_mode: bool = Field(
        default=True,
        env="COMPLIANCE_STRICT_MODE",
        description="Enable strict constitutional compliance mode"
    )
    
    @field_validator("constitutional_hash")
    @classmethod
    def validate_constitutional_hash(cls, v):
        if v != "cdd01ef066bc6cf2":
            raise ValueError("Invalid constitutional hash")
        return v
    
    # ============================================================================
    # CODE ANALYSIS CONFIGURATION
    # ============================================================================
    
    # File watching
    watch_paths: List[str] = Field(
        default=["/home/dislove/ACGS-2"],
        env="WATCH_PATHS",
        description="Paths to watch for code changes"
    )
    
    @field_validator("watch_paths", mode="before")
    @classmethod
    def parse_watch_paths(cls, v):
        if isinstance(v, str):
            return [path.strip() for path in v.split(",") if path.strip()]
        return v
    
    # Supported file extensions
    supported_extensions: List[str] = Field(
        default=[".py", ".js", ".ts", ".yml", ".yaml", ".json", ".sql", ".md"],
        description="File extensions to analyze"
    )
    
    # Ignore patterns
    ignore_patterns: List[str] = Field(
        default=["__pycache__", ".git", "node_modules", ".pytest_cache", ".venv", "venv"],
        description="Directory patterns to ignore during analysis"
    )
    
    # Embedding configuration
    embedding_model: str = Field(
        default="microsoft/codebert-base",
        env="EMBEDDING_MODEL",
        description="Model for code embeddings"
    )
    
    embedding_batch_size: int = Field(
        default=32,
        env="EMBEDDING_BATCH_SIZE",
        description="Batch size for embedding generation"
    )
    
    # ============================================================================
    # PERFORMANCE CONFIGURATION
    # ============================================================================
    
    # Cache configuration
    cache_ttl_default: int = Field(
        default=1800,
        env="CACHE_TTL_DEFAULT",
        description="Default cache TTL in seconds"
    )
    
    cache_ttl_search: int = Field(
        default=300,
        env="CACHE_TTL_SEARCH",
        description="Search results cache TTL in seconds"
    )
    
    cache_ttl_symbols: int = Field(
        default=3600,
        env="CACHE_TTL_SYMBOLS",
        description="Symbol data cache TTL in seconds"
    )
    
    # Request limits
    max_concurrent_requests: int = Field(
        default=100,
        env="MAX_CONCURRENT_REQUESTS",
        description="Maximum concurrent requests"
    )
    
    request_timeout_seconds: int = Field(
        default=30,
        env="REQUEST_TIMEOUT_SECONDS",
        description="Request timeout in seconds"
    )
    
    # Performance targets
    target_p99_latency_ms: float = Field(
        default=10.0,
        env="TARGET_P99_LATENCY_MS",
        description="Target P99 latency in milliseconds"
    )
    
    target_cache_hit_rate: float = Field(
        default=0.85,
        env="TARGET_CACHE_HIT_RATE",
        description="Target cache hit rate (0.0 to 1.0)"
    )
    
    target_throughput_rps: float = Field(
        default=100.0,
        env="TARGET_THROUGHPUT_RPS",
        description="Target throughput in requests per second"
    )
    
    # ============================================================================
    # MONITORING AND LOGGING CONFIGURATION
    # ============================================================================
    
    # Logging
    log_level: str = Field(
        default="INFO",
        env="LOG_LEVEL",
        description="Logging level"
    )
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v):
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed:
            raise ValueError(f"Log level must be one of: {allowed}")
        return v.upper()
    
    structured_logging: bool = Field(
        default=True,
        env="STRUCTURED_LOGGING",
        description="Enable structured JSON logging"
    )
    
    access_log: bool = Field(
        default=True,
        env="ACCESS_LOG",
        description="Enable access logging"
    )
    
    # Prometheus monitoring
    prometheus_enabled: bool = Field(
        default=True,
        env="PROMETHEUS_ENABLED",
        description="Enable Prometheus metrics"
    )
    
    prometheus_port: int = Field(
        default=9091,
        env="PROMETHEUS_PORT",
        description="Prometheus metrics port"
    )
    
    # ============================================================================
    # SECURITY CONFIGURATION
    # ============================================================================
    
    # CORS
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        env="ALLOWED_ORIGINS",
        description="Allowed CORS origins"
    )
    
    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v
    
    # SSL configuration
    ssl_cert_file: Optional[str] = Field(
        default=None,
        env="SSL_CERT_FILE",
        description="SSL certificate file path"
    )
    
    ssl_key_file: Optional[str] = Field(
        default=None,
        env="SSL_KEY_FILE",
        description="SSL private key file path"
    )
    
    # Rate limiting
    rate_limit_enabled: bool = Field(
        default=True,
        env="RATE_LIMIT_ENABLED",
        description="Enable rate limiting"
    )
    
    rate_limit_requests_per_minute: int = Field(
        default=1000,
        env="RATE_LIMIT_REQUESTS_PER_MINUTE",
        description="Rate limit: requests per minute per IP"
    )
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        validate_assignment=True,
        extra="forbid"
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Export settings function for easy import
# Note: Don't instantiate settings at import time to avoid validation errors
