"""
Configuration for HITL Safety Architecture
"""

import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings

class HITLSafetyConfig(BaseSettings):
    """Configuration for HITL Safety service"""
    
    # Service configuration
    service_name: str = Field(default="hitl_safety_architecture", env="SERVICE_NAME")
    service_version: str = Field(default="1.0.0", env="SERVICE_VERSION")
    service_port: int = Field(default=8007, env="SERVICE_PORT")
    
    # Performance targets
    emergency_response_target_ms: int = Field(default=2000, env="EMERGENCY_RESPONSE_TARGET_MS")
    approval_interface_target_ms: int = Field(default=500, env="APPROVAL_INTERFACE_TARGET_MS")
    availability_target_percent: float = Field(default=99.9, env="AVAILABILITY_TARGET_PERCENT")
    
    # ACGS-1 service URLs
    auth_service_url: str = Field(default="http://localhost:8000", env="AUTH_SERVICE_URL")
    ac_service_url: str = Field(default="http://localhost:8001", env="AC_SERVICE_URL")
    integrity_service_url: str = Field(default="http://localhost:8002", env="INTEGRITY_SERVICE_URL")
    fv_service_url: str = Field(default="http://localhost:8003", env="FV_SERVICE_URL")
    gs_service_url: str = Field(default="http://localhost:8004", env="GS_SERVICE_URL")
    pgc_service_url: str = Field(default="http://localhost:8005", env="PGC_SERVICE_URL")
    ec_service_url: str = Field(default="http://localhost:8006", env="EC_SERVICE_URL")
    
    # Quantumagi compatibility
    constitution_hash: str = Field(default="cdd01ef066bc6cf2", env="CONSTITUTION_HASH")
    solana_devnet_endpoint: str = Field(default="https://api.devnet.solana.com", env="SOLANA_DEVNET_ENDPOINT")
    
    # Security configuration
    jwt_secret_key: str = Field(default="your-secret-key", env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expiration_hours: int = Field(default=24, env="JWT_EXPIRATION_HOURS")
    
    # Notification configuration
    notification_channels: List[str] = Field(default=["dashboard", "webhook", "audit_log"], env="NOTIFICATION_CHANNELS")
    webhook_url: Optional[str] = Field(default=None, env="WEBHOOK_URL")
    
    # Redis configuration for state management
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    redis_key_prefix: str = Field(default="hitl_safety", env="REDIS_KEY_PREFIX")
    redis_ttl_seconds: int = Field(default=86400, env="REDIS_TTL_SECONDS")
    
    # Database configuration
    database_url: Optional[str] = Field(default=None, env="DATABASE_URL")
    
    # Monitoring configuration
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    
    # Circuit breaker configuration
    circuit_breaker_failure_threshold: int = Field(default=5, env="CIRCUIT_BREAKER_FAILURE_THRESHOLD")
    circuit_breaker_recovery_timeout: int = Field(default=60, env="CIRCUIT_BREAKER_RECOVERY_TIMEOUT")
    
    # Workflow configuration
    max_pending_proposals: int = Field(default=100, env="MAX_PENDING_PROPOSALS")
    proposal_timeout_hours: int = Field(default=24, env="PROPOSAL_TIMEOUT_HOURS")
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False
    }

# Global configuration instance
config = HITLSafetyConfig()
