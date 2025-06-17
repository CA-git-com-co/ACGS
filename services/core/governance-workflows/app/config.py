"""
Configuration management for ACGS-1 Advanced Governance Workflows Service.

This module provides comprehensive configuration management with environment-based
settings, performance configurations, and integration parameters for all ACGS-1 services.
"""

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with comprehensive configuration management."""

    # Service Configuration
    SERVICE_NAME: str = "acgs-governance-workflows"
    VERSION: str = "1.0.0"
    HOST: str = "0.0.0.0"
    PORT: int = 8008
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # Security Configuration
    SECRET_KEY: str = "acgs-governance-workflows-secret-key-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS Configuration
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8000",
        "http://localhost:8001",
        "http://localhost:8002",
        "http://localhost:8003",
        "http://localhost:8004",
        "http://localhost:8005",
        "http://localhost:8006",
        "http://localhost:8007",
    ]

    # Trusted hosts
    ALLOWED_HOSTS: list[str] = ["*"]

    # Database Configuration
    DATABASE_URL: str = (
        "postgresql://acgs_user:acgs_password@localhost:5432/acgs_governance_workflows"
    )
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 40

    # Redis Configuration (for caching and performance)
    REDIS_URL: str = "redis://localhost:6379/1"
    REDIS_PASSWORD: str | None = None
    REDIS_DB: int = 1

    # ACGS-1 Core Services Integration
    AUTH_SERVICE_URL: str = "http://localhost:8000"
    AC_SERVICE_URL: str = "http://localhost:8001"
    INTEGRITY_SERVICE_URL: str = "http://localhost:8002"
    FV_SERVICE_URL: str = "http://localhost:8003"
    GS_SERVICE_URL: str = "http://localhost:8004"
    PGC_SERVICE_URL: str = "http://localhost:8005"
    EC_SERVICE_URL: str = "http://localhost:8006"
    SELF_EVOLVING_AI_SERVICE_URL: str = "http://localhost:8007"

    # Service timeouts and retries
    SERVICE_TIMEOUT: int = 30
    SERVICE_RETRY_ATTEMPTS: int = 3
    SERVICE_RETRY_DELAY: float = 1.0

    # Quantumagi Solana Integration
    QUANTUMAGI_ENABLED: bool = True
    SOLANA_CLUSTER: str = "devnet"
    SOLANA_RPC_URL: str = "https://api.devnet.solana.com"
    CONSTITUTION_HASH: str = "cdd01ef066bc6cf2"
    GOVERNANCE_PROGRAM_ID: str | None = None

    # Workflow Configuration
    MAX_CONCURRENT_WORKFLOWS: int = 1000
    WORKFLOW_TIMEOUT_MINUTES: int = 30
    WORKFLOW_RETRY_ATTEMPTS: int = 3
    WORKFLOW_BATCH_SIZE: int = 100

    # Performance Configuration
    RESPONSE_TIME_TARGET_MS: int = 500
    AVAILABILITY_TARGET_PERCENT: float = 99.9
    COMPLIANCE_ACCURACY_TARGET_PERCENT: float = 95.0
    WINA_OPTIMIZATION_TARGET_PERCENT: float = 90.0

    # Policy Creation Workflow Configuration
    POLICY_CREATION_ENABLED: bool = True
    POLICY_CREATION_TIMEOUT_MINUTES: int = 15
    POLICY_CREATION_APPROVAL_REQUIRED: bool = True
    POLICY_CREATION_STAKEHOLDER_THRESHOLD: int = 3

    # Constitutional Compliance Configuration
    CONSTITUTIONAL_COMPLIANCE_ENABLED: bool = True
    CONSTITUTIONAL_COMPLIANCE_TIMEOUT_SECONDS: int = 2
    CONSTITUTIONAL_COMPLIANCE_ACCURACY_TARGET: float = 95.0
    CONSTITUTIONAL_COMPLIANCE_BATCH_SIZE: int = 50

    # Policy Enforcement Configuration
    POLICY_ENFORCEMENT_ENABLED: bool = True
    POLICY_ENFORCEMENT_TIMEOUT_MS: int = 50
    POLICY_ENFORCEMENT_REAL_TIME: bool = True
    POLICY_ENFORCEMENT_VIOLATION_THRESHOLD: float = 0.1

    # WINA Oversight Configuration
    WINA_OVERSIGHT_ENABLED: bool = True
    WINA_OVERSIGHT_MONITORING_INTERVAL_SECONDS: int = 30
    WINA_OVERSIGHT_OPTIMIZATION_THRESHOLD: float = 0.8
    WINA_OVERSIGHT_REPORTING_INTERVAL_MINUTES: int = 60

    # Audit/Transparency Configuration
    AUDIT_TRANSPARENCY_ENABLED: bool = True
    AUDIT_TRANSPARENCY_REPORT_GENERATION_TIMEOUT_SECONDS: int = 30
    AUDIT_TRANSPARENCY_PUBLIC_REPORTING: bool = True
    AUDIT_TRANSPARENCY_IMMUTABLE_STORAGE: bool = True

    # Monitoring Configuration
    PROMETHEUS_ENABLED: bool = True
    PROMETHEUS_PORT: int = 9090
    OPENTELEMETRY_ENABLED: bool = True
    OTLP_ENDPOINT: str = "http://localhost:4317"
    METRICS_EXPORT_INTERVAL_SECONDS: int = 30

    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: str = "logs/governance_workflows.log"
    LOG_ROTATION_SIZE: str = "10MB"
    LOG_RETENTION_DAYS: int = 30

    # Caching Configuration
    CACHE_ENABLED: bool = True
    CACHE_TTL_SECONDS: int = 300
    CACHE_MAX_SIZE: int = 10000
    CACHE_POLICY_RESULTS: bool = True
    CACHE_COMPLIANCE_RESULTS: bool = True

    # Security Configuration
    RATE_LIMITING_ENABLED: bool = True
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 1000
    RATE_LIMIT_BURST_SIZE: int = 100
    IP_WHITELISTING_ENABLED: bool = False
    ALLOWED_IPS: list[str] = []

    # Multi-Model Configuration
    MULTI_MODEL_ENABLED: bool = True
    MULTI_MODEL_CONSENSUS_THRESHOLD: float = 0.8
    MULTI_MODEL_TIMEOUT_SECONDS: int = 10
    MULTI_MODEL_FALLBACK_ENABLED: bool = True

    # Enhanced Constitutional Analyzer Configuration
    ENHANCED_ANALYZER_ENABLED: bool = True
    QWEN3_EMBEDDINGS_ENABLED: bool = True
    SEMANTIC_SIMILARITY_THRESHOLD: float = 0.85
    CONSTITUTIONAL_ANALYSIS_TIMEOUT_SECONDS: int = 5

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        """Assemble CORS origins from environment variable or list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list | str):
            return v
        raise ValueError(v)

    @field_validator("ALLOWED_HOSTS", mode="before")
    @classmethod
    def assemble_allowed_hosts(cls, v):
        """Assemble allowed hosts from environment variable or list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list | str):
            return v
        raise ValueError(v)

    @field_validator("ALLOWED_IPS", mode="before")
    @classmethod
    def assemble_allowed_ips(cls, v):
        """Assemble allowed IPs from environment variable or list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list | str):
            return v
        raise ValueError(v)

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


# Configuration validation
def validate_configuration(settings: Settings) -> bool:
    """Validate configuration settings for production readiness."""
    validation_errors = []

    # Security validations
    if settings.ENVIRONMENT == "production":
        if settings.SECRET_KEY == "acgs-governance-workflows-secret-key-2024":
            validation_errors.append(
                "Production environment requires custom SECRET_KEY"
            )

        if settings.DEBUG:
            validation_errors.append("DEBUG should be False in production")

        if not settings.PROMETHEUS_ENABLED:
            validation_errors.append("Prometheus should be enabled in production")

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
    if settings.MAX_CONCURRENT_WORKFLOWS < 1000:
        validation_errors.append(
            "MAX_CONCURRENT_WORKFLOWS should be >= 1000 for performance targets"
        )

    if settings.RESPONSE_TIME_TARGET_MS > 500:
        validation_errors.append(
            "RESPONSE_TIME_TARGET_MS should be <= 500ms for performance targets"
        )

    if settings.AVAILABILITY_TARGET_PERCENT < 99.9:
        validation_errors.append(
            "AVAILABILITY_TARGET_PERCENT should be >= 99.9% for performance targets"
        )

    if settings.COMPLIANCE_ACCURACY_TARGET_PERCENT < 95.0:
        validation_errors.append(
            "COMPLIANCE_ACCURACY_TARGET_PERCENT should be >= 95% for accuracy targets"
        )

    # Workflow validations
    if settings.POLICY_ENFORCEMENT_TIMEOUT_MS > 50:
        validation_errors.append(
            "POLICY_ENFORCEMENT_TIMEOUT_MS should be <= 50ms for real-time enforcement"
        )

    if settings.CONSTITUTIONAL_COMPLIANCE_TIMEOUT_SECONDS > 2:
        validation_errors.append(
            "CONSTITUTIONAL_COMPLIANCE_TIMEOUT_SECONDS should be <= 2s for performance targets"
        )

    if settings.AUDIT_TRANSPARENCY_REPORT_GENERATION_TIMEOUT_SECONDS > 30:
        validation_errors.append(
            "AUDIT_TRANSPARENCY_REPORT_GENERATION_TIMEOUT_SECONDS should be <= 30s"
        )

    # Quantumagi validations
    if settings.QUANTUMAGI_ENABLED:
        if settings.CONSTITUTION_HASH != "cdd01ef066bc6cf2":
            validation_errors.append(
                "CONSTITUTION_HASH must match Quantumagi deployment"
            )

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
