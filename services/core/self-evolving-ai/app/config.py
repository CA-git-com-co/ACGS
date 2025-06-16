"""
Configuration management for ACGS-1 Self-Evolving AI Architecture Foundation Service.

This module provides comprehensive configuration management with environment-based
settings, security configurations, and integration parameters for all ACGS-1 services.
"""

import os
from functools import lru_cache
from typing import List, Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with comprehensive configuration management."""
    
    # Service Configuration
    SERVICE_NAME: str = "acgs-self-evolving-ai"
    VERSION: str = "1.0.0"
    HOST: str = "0.0.0.0"
    PORT: int = 8007
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Security Configuration
    SECRET_KEY: str = "acgs-self-evolving-ai-secret-key-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS Configuration
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001,http://localhost:8000,http://localhost:8001,http://localhost:8002,http://localhost:8003,http://localhost:8004,http://localhost:8005,http://localhost:8006"

    # Trusted hosts
    ALLOWED_HOSTS: str = "*"
    
    # Database Configuration
    DATABASE_URL: str = "postgresql://acgs_user:acgs_password@localhost:5432/acgs_self_evolving_ai"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # Redis Configuration (for caching and background processing)
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    
    # Celery Configuration (background processing)
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_RESULT_SERIALIZER: str = "json"
    CELERY_ACCEPT_CONTENT: str = "json"
    CELERY_TIMEZONE: str = "UTC"
    CELERY_ENABLE_UTC: bool = True
    
    # OPA (Open Policy Agent) Configuration
    OPA_SERVER_URL: str = "http://localhost:8181"
    OPA_BUNDLE_NAME: str = "self_evolving_ai"
    OPA_TIMEOUT: int = 30
    OPA_RETRY_ATTEMPTS: int = 3
    
    # Sandboxing Configuration
    SANDBOX_ENABLED: bool = True
    SANDBOX_TYPE: str = "gvisor"  # or "firecracker"
    RESOURCE_LIMITS_ENABLED: bool = True
    MAX_CPU_CORES: int = 2
    MAX_MEMORY_MB: int = 1024
    MAX_DISK_MB: int = 2048
    EXECUTION_TIMEOUT_SECONDS: int = 300
    
    # OpenTelemetry Configuration
    OPENTELEMETRY_ENABLED: bool = True
    OTLP_ENDPOINT: str = "http://localhost:4317"
    OTLP_VERSION: str = "v1.37.0"
    TRACING_ENABLED: bool = True
    METRICS_ENABLED: bool = True
    
    # Secrets Management (Vault)
    VAULT_URL: str = "http://localhost:8200"
    VAULT_TOKEN: Optional[str] = None
    VAULT_MOUNT_POINT: str = "secret"
    VAULT_ENABLED: bool = False
    
    # ACGS-1 Core Services Integration
    AUTH_SERVICE_URL: str = "http://localhost:8000"
    AC_SERVICE_URL: str = "http://localhost:8001"
    INTEGRITY_SERVICE_URL: str = "http://localhost:8002"
    FV_SERVICE_URL: str = "http://localhost:8003"
    GS_SERVICE_URL: str = "http://localhost:8004"
    PGC_SERVICE_URL: str = "http://localhost:8005"
    EC_SERVICE_URL: str = "http://localhost:8006"
    
    # Service timeouts and retries
    SERVICE_TIMEOUT: int = 30
    SERVICE_RETRY_ATTEMPTS: int = 3
    SERVICE_RETRY_DELAY: float = 1.0
    
    # Quantumagi Solana Integration
    QUANTUMAGI_ENABLED: bool = True
    SOLANA_CLUSTER: str = "devnet"
    SOLANA_RPC_URL: str = "https://api.devnet.solana.com"
    CONSTITUTION_HASH: str = "cdd01ef066bc6cf2"
    GOVERNANCE_PROGRAM_ID: Optional[str] = None
    
    # Evolution Engine Configuration
    EVOLUTION_ENABLED: bool = True
    MANUAL_APPROVAL_REQUIRED: bool = True
    MAX_CONCURRENT_EVOLUTIONS: int = 5
    EVOLUTION_TIMEOUT_MINUTES: int = 10
    ROLLBACK_ENABLED: bool = True
    
    # Security Framework Configuration
    THREAT_DETECTION_ENABLED: bool = True
    AUDIT_LOGGING_ENABLED: bool = True
    RATE_LIMITING_ENABLED: bool = True
    IP_WHITELISTING_ENABLED: bool = False
    ALLOWED_IPS: str = ""
    
    # Performance Configuration
    MAX_CONCURRENT_REQUESTS: int = 1000
    REQUEST_TIMEOUT_SECONDS: int = 30
    RESPONSE_TIME_TARGET_MS: int = 500
    AVAILABILITY_TARGET_PERCENT: float = 99.9
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: str = "logs/self_evolving_ai.log"
    LOG_ROTATION_SIZE: str = "10MB"
    LOG_RETENTION_DAYS: int = 30
    
    def get_cors_origins_list(self) -> list[str]:
        """Get CORS origins as a list."""
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",") if origin.strip()]

    def get_allowed_hosts_list(self) -> list[str]:
        """Get allowed hosts as a list."""
        return [host.strip() for host in self.ALLOWED_HOSTS.split(",") if host.strip()]

    def get_allowed_ips_list(self) -> list[str]:
        """Get allowed IPs as a list."""
        if not self.ALLOWED_IPS:
            return []
        return [ip.strip() for ip in self.ALLOWED_IPS.split(",") if ip.strip()]

    def get_celery_accept_content_list(self) -> list[str]:
        """Get Celery accept content as a list."""
        return [content.strip() for content in self.CELERY_ACCEPT_CONTENT.split(",") if content.strip()]
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True
    }


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


# Configuration validation
def validate_configuration(settings: Settings) -> bool:
    """Validate configuration settings for production readiness."""
    validation_errors = []
    
    # Security validations
    if settings.ENVIRONMENT == "production":
        if settings.SECRET_KEY == "acgs-self-evolving-ai-secret-key-2024":
            validation_errors.append("Production environment requires custom SECRET_KEY")
        
        if settings.DEBUG:
            validation_errors.append("DEBUG should be False in production")
        
        if not settings.VAULT_ENABLED:
            validation_errors.append("Vault should be enabled in production")
        
        if not settings.OPENTELEMETRY_ENABLED:
            validation_errors.append("OpenTelemetry should be enabled in production")
    
    # Service integration validations
    required_services = [
        "AUTH_SERVICE_URL",
        "AC_SERVICE_URL", 
        "INTEGRITY_SERVICE_URL",
        "FV_SERVICE_URL",
        "GS_SERVICE_URL",
        "PGC_SERVICE_URL",
        "EC_SERVICE_URL",
    ]
    
    for service in required_services:
        url = getattr(settings, service)
        if not url or url == f"http://localhost:800{required_services.index(service)}":
            if settings.ENVIRONMENT == "production":
                validation_errors.append(f"{service} requires production URL")
    
    # Performance validations
    if settings.MAX_CONCURRENT_REQUESTS < 1000:
        validation_errors.append("MAX_CONCURRENT_REQUESTS should be >= 1000 for performance targets")
    
    if settings.RESPONSE_TIME_TARGET_MS > 500:
        validation_errors.append("RESPONSE_TIME_TARGET_MS should be <= 500ms for performance targets")
    
    if settings.AVAILABILITY_TARGET_PERCENT < 99.9:
        validation_errors.append("AVAILABILITY_TARGET_PERCENT should be >= 99.9% for performance targets")
    
    # Quantumagi validations
    if settings.QUANTUMAGI_ENABLED:
        if settings.CONSTITUTION_HASH != "cdd01ef066bc6cf2":
            validation_errors.append("CONSTITUTION_HASH must match Quantumagi deployment")
        
        if settings.SOLANA_CLUSTER not in ["devnet", "testnet", "mainnet-beta"]:
            validation_errors.append("Invalid SOLANA_CLUSTER specified")
    
    if validation_errors:
        print("❌ Configuration validation errors:")
        for error in validation_errors:
            print(f"  - {error}")
        return False
    
    print("✅ Configuration validation passed")
    return True


# Export settings instance for convenience
settings = get_settings()
