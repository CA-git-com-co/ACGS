"""
Sandbox Execution Service Configuration

Manages configuration for secure code execution environment.
"""

import os
from typing import List, Dict, Optional
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Sandbox execution service configuration settings."""
    
    # Service identification
    SERVICE_NAME: str = "sandbox-execution-service"
    SERVICE_VERSION: str = "1.0.0"
    
    # Server configuration
    HOST: str = Field(default="0.0.0.0", env="SANDBOX_HOST")
    PORT: int = Field(default=8009, env="SANDBOX_PORT")
    DEBUG: bool = Field(default=False, env="SANDBOX_DEBUG")
    
    # Constitutional configuration
    CONSTITUTIONAL_HASH: str = Field(
        default="cdd01ef066bc6cf2",
        env="CONSTITUTIONAL_HASH"
    )
    
    # Docker configuration
    DOCKER_SOCKET: str = Field(default="unix:///var/run/docker.sock", env="DOCKER_SOCKET")
    DOCKER_REGISTRY: str = Field(default="", env="DOCKER_REGISTRY")
    
    # Sandbox configuration
    SANDBOX_BASE_IMAGE: str = Field(default="ubuntu:22.04", env="SANDBOX_BASE_IMAGE")
    SANDBOX_NETWORK_MODE: str = Field(default="none", env="SANDBOX_NETWORK_MODE")
    SANDBOX_MEMORY_LIMIT: str = Field(default="512m", env="SANDBOX_MEMORY_LIMIT")
    SANDBOX_CPU_LIMIT: str = Field(default="0.5", env="SANDBOX_CPU_LIMIT")
    SANDBOX_TIMEOUT_SECONDS: int = Field(default=300, env="SANDBOX_TIMEOUT_SECONDS")
    SANDBOX_DISK_LIMIT: str = Field(default="1g", env="SANDBOX_DISK_LIMIT")
    
    # Security settings
    ENABLE_NETWORK_ACCESS: bool = Field(default=False, env="ENABLE_NETWORK_ACCESS")
    ALLOWED_NETWORK_HOSTS: List[str] = Field(default=[], env="ALLOWED_NETWORK_HOSTS")
    MAX_CONCURRENT_SANDBOXES: int = Field(default=10, env="MAX_CONCURRENT_SANDBOXES")
    SANDBOX_USER_ID: int = Field(default=1000, env="SANDBOX_USER_ID")
    
    # File system restrictions
    SANDBOX_WORK_DIR: str = Field(default="/tmp/sandbox", env="SANDBOX_WORK_DIR")
    READONLY_PATHS: List[str] = Field(
        default=["/bin", "/usr", "/lib", "/lib64", "/etc"],
        env="READONLY_PATHS"
    )
    WRITABLE_PATHS: List[str] = Field(
        default=["/tmp", "/var/tmp"],
        env="WRITABLE_PATHS"
    )
    
    # Language-specific configurations
    PYTHON_BASE_IMAGE: str = Field(default="python:3.11-slim", env="PYTHON_BASE_IMAGE")
    NODE_BASE_IMAGE: str = Field(default="node:18-alpine", env="NODE_BASE_IMAGE")
    BASH_BASE_IMAGE: str = Field(default="ubuntu:22.04", env="BASH_BASE_IMAGE")
    
    # Service dependencies
    AUTH_SERVICE_URL: str = Field(
        default="http://localhost:8006",
        env="AUTH_SERVICE_URL"
    )
    AGENT_HITL_URL: str = Field(
        default="http://localhost:8008",
        env="AGENT_HITL_URL"
    )
    POLICY_GOVERNANCE_URL: str = Field(
        default="http://localhost:8003",
        env="POLICY_GOVERNANCE_URL"
    )
    
    # Monitoring and logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    ENABLE_METRICS: bool = Field(default=True, env="ENABLE_METRICS")
    METRICS_PORT: int = Field(default=9091, env="METRICS_PORT")
    
    # Database for execution logs
    DATABASE_URL: str = Field(
        default="postgresql://user:pass@localhost/sandbox_db",
        env="DATABASE_URL"
    )
    
    # Redis for session management
    REDIS_URL: str = Field(
        default="redis://localhost:6379/1",
        env="REDIS_URL"
    )
    
    # Resource cleanup
    CLEANUP_INTERVAL_MINUTES: int = Field(default=15, env="CLEANUP_INTERVAL_MINUTES")
    MAX_EXECUTION_LOG_AGE_DAYS: int = Field(default=30, env="MAX_EXECUTION_LOG_AGE_DAYS")
    
    # Execution policies
    EXECUTION_POLICIES: Dict[str, Dict] = Field(
        default={
            "python": {
                "allowed_imports": [
                    "os", "sys", "json", "datetime", "math", "re", "urllib",
                    "requests", "numpy", "pandas", "matplotlib"
                ],
                "blocked_imports": ["subprocess", "multiprocessing", "socket"],
                "max_execution_time": 120,
                "max_memory_mb": 256,
            },
            "bash": {
                "allowed_commands": ["ls", "cat", "grep", "awk", "sed", "sort", "head", "tail"],
                "blocked_commands": ["rm", "curl", "wget", "ssh", "nc", "netcat"],
                "max_execution_time": 60,
                "max_memory_mb": 128,
            },
            "node": {
                "allowed_modules": ["fs", "path", "crypto", "util"],
                "blocked_modules": ["child_process", "cluster", "net", "http"],
                "max_execution_time": 90,
                "max_memory_mb": 256,
            }
        }
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()