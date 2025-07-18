"""
Shared Database Configuration for ACGS Services
Constitutional Hash: cdd01ef066bc6cf2
"""

from pydantic import BaseSettings, Field


class SharedDatabaseConfig(BaseSettings):
    """Shared database configuration for all ACGS services."""
    
    constitutional_hash: str = "cdd01ef066bc6cf2"
    
    # Connection settings
    url: str = Field(
        default="postgresql+asyncpg://acgs_user:acgs_password@localhost:5432/acgs_db",
        env="DATABASE_URL",
        description="Database connection URL",
    )
    
    # Enhanced connection pool settings (optimized for >200 concurrent connections)
    pool_size: int = Field(
        default=50,
        env="DATABASE_POOL_SIZE", 
        description="Database connection pool size",
    )
    
    max_overflow: int = Field(
        default=50,
        env="DATABASE_MAX_OVERFLOW",
        description="Maximum connection pool overflow",
    )
    
    pool_timeout: int = Field(
        default=30,
        env="DATABASE_POOL_TIMEOUT",
        description="Connection pool timeout in seconds",
    )
    
    pool_recycle: int = Field(
        default=3600,
        env="DATABASE_POOL_RECYCLE",
        description="Connection pool recycle time in seconds",
    )
    
    # Performance settings
    echo: bool = Field(
        default=False,
        env="DATABASE_ECHO",
        description="Enable SQL query logging",
    )
    
    class Config:
        env_prefix = "ACGS_DB_"
        case_sensitive = False
