"""
Audit Integrity Service Configuration

Manages configuration for audit logging integrity and blockchain anchoring.
"""

import os
from typing import List, Dict, Optional
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Audit integrity service configuration settings."""
    
    # Service identification
    SERVICE_NAME: str = "audit-integrity-service"
    SERVICE_VERSION: str = "1.0.0"
    
    # Server configuration
    HOST: str = Field(default="0.0.0.0", env="AUDIT_INTEGRITY_HOST")
    PORT: int = Field(default=8011, env="AUDIT_INTEGRITY_PORT")
    DEBUG: bool = Field(default=False, env="AUDIT_INTEGRITY_DEBUG")
    
    # Constitutional configuration
    CONSTITUTIONAL_HASH: str = Field(
        default="cdd01ef066bc6cf2",
        env="CONSTITUTIONAL_HASH"
    )
    
    # Cryptographic configuration
    PRIVATE_KEY_PATH: str = Field(
        default="/app/keys/audit_private_key.pem",
        env="PRIVATE_KEY_PATH"
    )
    PUBLIC_KEY_PATH: str = Field(
        default="/app/keys/audit_public_key.pem",
        env="PUBLIC_KEY_PATH"
    )
    KEY_SIZE: int = Field(default=2048, env="KEY_SIZE")
    
    # Batch processing configuration
    BATCH_SIZE: int = Field(default=100, env="BATCH_SIZE")
    BATCH_TIMEOUT_MINUTES: int = Field(default=15, env="BATCH_TIMEOUT_MINUTES")
    MAX_BATCH_AGE_HOURS: int = Field(default=24, env="MAX_BATCH_AGE_HOURS")
    
    # Blockchain anchoring configuration
    ENABLE_BLOCKCHAIN_ANCHORING: bool = Field(default=True, env="ENABLE_BLOCKCHAIN_ANCHORING")
    BLOCKCHAIN_TYPE: str = Field(default="mock", env="BLOCKCHAIN_TYPE")  # mock, solana, ethereum
    BLOCKCHAIN_NETWORK: str = Field(default="testnet", env="BLOCKCHAIN_NETWORK")
    
    # Solana configuration
    SOLANA_RPC_URL: str = Field(
        default="https://api.testnet.solana.com",
        env="SOLANA_RPC_URL"
    )
    SOLANA_PRIVATE_KEY: str = Field(default="", env="SOLANA_PRIVATE_KEY")
    SOLANA_PROGRAM_ID: str = Field(default="", env="SOLANA_PROGRAM_ID")
    
    # Ethereum configuration
    ETHEREUM_RPC_URL: str = Field(
        default="https://goerli.infura.io/v3/YOUR_PROJECT_ID",
        env="ETHEREUM_RPC_URL"
    )
    ETHEREUM_PRIVATE_KEY: str = Field(default="", env="ETHEREUM_PRIVATE_KEY")
    ETHEREUM_CONTRACT_ADDRESS: str = Field(default="", env="ETHEREUM_CONTRACT_ADDRESS")
    ETHEREUM_GAS_LIMIT: int = Field(default=100000, env="ETHEREUM_GAS_LIMIT")
    
    # Database configuration
    DATABASE_URL: str = Field(
        default="postgresql://user:pass@localhost/audit_integrity_db",
        env="DATABASE_URL"
    )
    
    # Redis configuration for caching
    REDIS_URL: str = Field(
        default="redis://localhost:6379/3",
        env="REDIS_URL"
    )
    CACHE_TTL: int = Field(default=3600, env="CACHE_TTL")  # 1 hour
    
    # Service dependencies
    AUTH_SERVICE_URL: str = Field(
        default="http://localhost:8006",
        env="AUTH_SERVICE_URL"
    )
    AGENT_HITL_URL: str = Field(
        default="http://localhost:8008",
        env="AGENT_HITL_URL"
    )
    SANDBOX_EXECUTION_URL: str = Field(
        default="http://localhost:8009",
        env="SANDBOX_EXECUTION_URL"
    )
    FORMAL_VERIFICATION_URL: str = Field(
        default="http://localhost:8010",
        env="FORMAL_VERIFICATION_URL"
    )
    
    # Storage configuration
    AUDIT_STORAGE_PATH: str = Field(
        default="/app/data/audit_logs",
        env="AUDIT_STORAGE_PATH"
    )
    PROOF_STORAGE_PATH: str = Field(
        default="/app/data/integrity_proofs",
        env="PROOF_STORAGE_PATH"
    )
    BACKUP_STORAGE_PATH: str = Field(
        default="/app/data/backups",
        env="BACKUP_STORAGE_PATH"
    )
    
    # Retention policies
    AUDIT_LOG_RETENTION_DAYS: int = Field(default=2555, env="AUDIT_LOG_RETENTION_DAYS")  # 7 years
    PROOF_RETENTION_DAYS: int = Field(default=3650, env="PROOF_RETENTION_DAYS")  # 10 years
    BACKUP_RETENTION_DAYS: int = Field(default=1095, env="BACKUP_RETENTION_DAYS")  # 3 years
    
    # Integrity verification settings
    ENABLE_CONTINUOUS_VERIFICATION: bool = Field(default=True, env="ENABLE_CONTINUOUS_VERIFICATION")
    VERIFICATION_INTERVAL_HOURS: int = Field(default=24, env="VERIFICATION_INTERVAL_HOURS")
    ENABLE_MERKLE_PROOFS: bool = Field(default=True, env="ENABLE_MERKLE_PROOFS")
    
    # Alerting configuration
    ENABLE_INTEGRITY_ALERTS: bool = Field(default=True, env="ENABLE_INTEGRITY_ALERTS")
    ALERT_WEBHOOK_URL: str = Field(default="", env="ALERT_WEBHOOK_URL")
    ALERT_EMAIL_RECIPIENTS: List[str] = Field(default=[], env="ALERT_EMAIL_RECIPIENTS")
    
    # Performance configuration
    MAX_CONCURRENT_OPERATIONS: int = Field(default=10, env="MAX_CONCURRENT_OPERATIONS")
    HASH_ALGORITHM: str = Field(default="sha256", env="HASH_ALGORITHM")
    SIGNATURE_ALGORITHM: str = Field(default="RSA-PSS", env="SIGNATURE_ALGORITHM")
    
    # Audit event types
    CRITICAL_EVENT_TYPES: List[str] = Field(
        default=[
            "authentication_failure",
            "authorization_failure",
            "policy_violation",
            "security_breach",
            "data_access_unauthorized",
            "system_compromise",
            "constitutional_violation",
        ],
        env="CRITICAL_EVENT_TYPES"
    )
    
    # Compliance settings
    COMPLIANCE_STANDARDS: List[str] = Field(
        default=["SOC2", "ISO27001", "GDPR", "CONSTITUTIONAL_AI"],
        env="COMPLIANCE_STANDARDS"
    )
    ENABLE_COMPLIANCE_REPORTING: bool = Field(default=True, env="ENABLE_COMPLIANCE_REPORTING")
    COMPLIANCE_REPORT_FREQUENCY: str = Field(default="daily", env="COMPLIANCE_REPORT_FREQUENCY")
    
    # Monitoring and metrics
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    ENABLE_METRICS: bool = Field(default=True, env="ENABLE_METRICS")
    METRICS_PORT: int = Field(default=9093, env="METRICS_PORT")
    
    # Development and testing
    ENABLE_TESTING_MODE: bool = Field(default=False, env="ENABLE_TESTING_MODE")
    MOCK_BLOCKCHAIN_DELAY_MS: int = Field(default=100, env="MOCK_BLOCKCHAIN_DELAY_MS")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()