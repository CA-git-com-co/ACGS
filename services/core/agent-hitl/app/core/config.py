"""
Agent HITL Service Configuration

Manages configuration for the Agent Human-in-the-Loop service.
"""

import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Agent HITL service configuration settings."""
    
    # Service identification
    SERVICE_NAME: str = "agent-hitl-service"
    SERVICE_VERSION: str = "1.0.0"
    
    # Server configuration
    HOST: str = Field(default="0.0.0.0", env="AGENT_HITL_HOST")
    PORT: int = Field(default=8008, env="AGENT_HITL_PORT")
    DEBUG: bool = Field(default=False, env="AGENT_HITL_DEBUG")
    
    # Database configuration
    DATABASE_URL: str = Field(
        default="postgresql://user:pass@localhost/agent_hitl_db",
        env="DATABASE_URL"
    )
    
    # Redis configuration for caching
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        env="REDIS_URL"
    )
    CACHE_TTL: int = Field(default=300, env="CACHE_TTL")  # 5 minutes
    
    # Constitutional configuration
    CONSTITUTIONAL_HASH: str = Field(
        default="cdd01ef066bc6cf2",
        env="CONSTITUTIONAL_HASH"
    )
    
    # Service dependencies
    CONSTITUTIONAL_AI_URL: str = Field(
        default="http://localhost:8002",
        env="CONSTITUTIONAL_AI_URL"
    )
    POLICY_GOVERNANCE_URL: str = Field(
        default="http://localhost:8003",
        env="POLICY_GOVERNANCE_URL"
    )
    AUTH_SERVICE_URL: str = Field(
        default="http://localhost:8006",
        env="AUTH_SERVICE_URL"
    )
    
    # HITL configuration
    DEFAULT_CONFIDENCE_THRESHOLD: float = Field(
        default=0.9,
        env="DEFAULT_CONFIDENCE_THRESHOLD"
    )
    
    # Escalation levels configuration
    ESCALATION_LEVEL_1_THRESHOLD: float = Field(default=0.9)  # Auto-approve
    ESCALATION_LEVEL_2_THRESHOLD: float = Field(default=0.7)  # Team lead review
    ESCALATION_LEVEL_3_THRESHOLD: float = Field(default=0.5)  # Domain expert review
    ESCALATION_LEVEL_4_THRESHOLD: float = Field(default=0.0)  # Constitutional Council
    
    # Performance targets
    AUTO_DECISION_TIMEOUT_MS: int = Field(default=5, env="AUTO_DECISION_TIMEOUT_MS")
    HUMAN_REVIEW_TIMEOUT_MINUTES: int = Field(default=30, env="HUMAN_REVIEW_TIMEOUT_MINUTES")
    
    # Queue configuration
    REVIEW_QUEUE_MAX_SIZE: int = Field(default=1000, env="REVIEW_QUEUE_MAX_SIZE")
    REVIEW_QUEUE_PRIORITY_LEVELS: int = Field(default=4, env="REVIEW_QUEUE_PRIORITY_LEVELS")
    
    # Monitoring and metrics
    ENABLE_METRICS: bool = Field(default=True, env="ENABLE_METRICS")
    METRICS_PORT: int = Field(default=9090, env="METRICS_PORT")
    
    # Security
    API_KEY_HEADER: str = Field(default="X-API-Key", env="API_KEY_HEADER")
    REQUIRE_HTTPS: bool = Field(default=True, env="REQUIRE_HTTPS")
    
    # Agent-specific configuration
    AGENT_CONFIDENCE_LEARNING_RATE: float = Field(default=0.1, env="AGENT_CONFIDENCE_LEARNING_RATE")
    MIN_AGENT_OPERATIONS_FOR_ADAPTATION: int = Field(default=100)
    
    # Risk assessment weights
    OPERATION_RISK_WEIGHTS: dict = Field(
        default={
            "code_execution": 0.9,
            "code_modification": 0.8,
            "policy_update": 0.95,
            "data_access": 0.7,
            "external_api_call": 0.6,
            "system_command": 0.85,
            "file_operation": 0.5,
            "network_operation": 0.7,
        }
    )
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings