"""
ACGS-1 Database Connection Pool Configuration
Phase 2 - Enterprise Scalability & Performance

Centralized configuration for database connection pooling across all services.
Optimized for >1000 concurrent users, >99.9% availability, <500ms response.
"""

import logging
import os
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ConnectionPoolConfig:
    """Enhanced connection pool configuration for enterprise scalability."""

    # PgBouncer connection settings
    host: str = "localhost"
    port: int = 6432  # PgBouncer port
    database: str = "acgs_db"
    username: str = "acgs_user"
    password: str = "acgs_password"

    # Pool size configuration for >1000 concurrent users
    min_connections: int = 10
    max_connections: int = 50  # Increased for high concurrency
    max_overflow: int = 20
    pool_timeout: float = 20.0  # Reduced for faster failover
    pool_recycle: int = 1800  # 30 minutes
    pool_pre_ping: bool = True

    # Connection retry settings
    retry_attempts: int = 3
    retry_delay: float = 1.0
    retry_backoff: float = 2.0

    # Performance settings
    echo: bool = False
    echo_pool: bool = False

    # Health check settings
    health_check_interval: int = 30
    connection_timeout: float = 10.0

    def get_connection_url(self) -> str:
        """Get the database connection URL for PgBouncer."""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

    def get_async_connection_url(self) -> str:
        """Get the async database connection URL for PgBouncer."""
        return f"postgresql+asyncpg://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"


class ServiceConnectionPools:
    """Manages connection pool configurations for all ACGS core services."""

    # Service-specific pool configurations optimized for workload patterns
    SERVICE_CONFIGS = {
        "auth_service": ConnectionPoolConfig(
            database="auth_db",  # Dedicated database
            min_connections=20,  # High auth traffic
            max_connections=80,
            max_overflow=30,
            pool_timeout=15.0,  # Faster timeout for auth
            pool_recycle=1200,  # 20 minutes for high turnover
        ),
        "ac_service": ConnectionPoolConfig(
            database="constitutional_db",
            min_connections=15,  # Constitutional AI operations
            max_connections=60,
            max_overflow=25,
            pool_timeout=20.0,
            pool_recycle=1800,
        ),
        "integrity_service": ConnectionPoolConfig(
            database="integrity_db",
            min_connections=12,  # Cryptographic operations
            max_connections=50,
            max_overflow=20,
            pool_timeout=25.0,  # Longer for crypto ops
            pool_recycle=2400,  # 40 minutes
        ),
        "fv_service": ConnectionPoolConfig(
            database="verification_db",
            min_connections=10,  # Formal verification
            max_connections=40,
            max_overflow=15,
            pool_timeout=30.0,  # Longer for complex verification
            pool_recycle=3600,  # 1 hour
        ),
        "gs_service": ConnectionPoolConfig(
            database="acgs_db",
            min_connections=20,  # High LLM workload
            max_connections=80,  # Highest pool for policy generation
            max_overflow=30,
        ),
        "pgc_service": ConnectionPoolConfig(
            database="acgs_db",
            min_connections=15,  # Policy governance
            max_connections=60,
            max_overflow=25,
        ),
        "ec_service": ConnectionPoolConfig(
            database="acgs_db",
            min_connections=8,  # Evaluation and compliance
            max_connections=35,
            max_overflow=15,
        ),
        "acgs_pgp_v8": ConnectionPoolConfig(
            database="acgs_pgp_db",  # Separate database
            min_connections=12,
            max_connections=50,
            max_overflow=20,
        ),
    }

    @classmethod
    def get_config(cls, service_name: str) -> ConnectionPoolConfig:
        """Get connection pool configuration for a specific service."""
        config = cls.SERVICE_CONFIGS.get(service_name)
        if not config:
            logger.warning(f"No specific config for {service_name}, using default")
            return ConnectionPoolConfig()

        # Override with environment variables if present
        cls._apply_env_overrides(config, service_name)
        return config

    @classmethod
    def _apply_env_overrides(
        cls, config: ConnectionPoolConfig, service_name: str
    ) -> None:
        """Apply environment variable overrides to configuration."""
        prefix = f"{service_name.upper()}_DB_"

        # Database connection overrides
        config.host = os.getenv(f"{prefix}HOST", config.host)
        config.port = int(os.getenv(f"{prefix}PORT", str(config.port)))
        config.database = os.getenv(f"{prefix}NAME", config.database)
        config.username = os.getenv(f"{prefix}USER", config.username)
        config.password = os.getenv(f"{prefix}PASSWORD", config.password)

        # Pool size overrides
        config.min_connections = int(
            os.getenv(f"{prefix}MIN_CONNECTIONS", str(config.min_connections))
        )
        config.max_connections = int(
            os.getenv(f"{prefix}MAX_CONNECTIONS", str(config.max_connections))
        )
        config.max_overflow = int(
            os.getenv(f"{prefix}MAX_OVERFLOW", str(config.max_overflow))
        )
        config.pool_timeout = float(
            os.getenv(f"{prefix}POOL_TIMEOUT", str(config.pool_timeout))
        )
        config.pool_recycle = int(
            os.getenv(f"{prefix}POOL_RECYCLE", str(config.pool_recycle))
        )

        # Global overrides
        if os.getenv("PGBOUNCER_HOST"):
            config.host = os.getenv("PGBOUNCER_HOST")
        if os.getenv("PGBOUNCER_PORT"):
            config.port = int(os.getenv("PGBOUNCER_PORT"))

    @classmethod
    def get_all_configs(cls) -> dict[str, ConnectionPoolConfig]:
        """Get all service connection pool configurations."""
        return {
            service: cls.get_config(service) for service in cls.SERVICE_CONFIGS.keys()
        }

    @classmethod
    def validate_configurations(cls) -> bool:
        """Validate all connection pool configurations."""
        total_max_connections = 0

        for service_name, config in cls.get_all_configs().items():
            total_max_connections += config.max_connections + config.max_overflow

            # Validate individual service configuration
            if config.min_connections > config.max_connections:
                logger.error(f"{service_name}: min_connections > max_connections")
                return False

            if config.max_connections <= 0:
                logger.error(f"{service_name}: max_connections must be > 0")
                return False

        # Check total connections don't exceed PgBouncer limits
        pgbouncer_max = int(os.getenv("PGBOUNCER_MAX_CLIENT_CONN", "1000"))
        if total_max_connections > pgbouncer_max:
            logger.warning(
                f"Total max connections ({total_max_connections}) exceeds "
                f"PgBouncer limit ({pgbouncer_max})"
            )

        logger.info(
            f"Connection pool validation passed. Total max connections: {total_max_connections}"
        )
        return True


# Environment-based configuration
def get_database_url(service_name: str) -> str:
    """Get database URL for a specific service."""
    config = ServiceConnectionPools.get_config(service_name)
    return config.get_connection_url()


def get_async_database_url(service_name: str) -> str:
    """Get async database URL for a specific service."""
    config = ServiceConnectionPools.get_config(service_name)
    return config.get_async_connection_url()


# Export commonly used configurations
DEFAULT_CONFIG = ConnectionPoolConfig()
AUTH_CONFIG = ServiceConnectionPools.get_config("auth_service")
GS_CONFIG = ServiceConnectionPools.get_config("gs_service")
PGC_CONFIG = ServiceConnectionPools.get_config("pgc_service")

# Validate configurations on import
if not ServiceConnectionPools.validate_configurations():
    logger.error("Connection pool configuration validation failed!")
