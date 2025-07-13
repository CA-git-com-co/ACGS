"""
ACGS Infrastructure Configuration
Constitutional Hash: cdd01ef066bc6cf2

This module provides standardized infrastructure configuration for ACGS services including:
- Service port standardization with validation
- Database connection pool configuration (asyncpg)
- Redis connection configuration (aioredis)
- Prometheus metrics integration
"""

import logging
import os
from urllib.parse import urlparse

# Optional imports for runtime dependencies
try:
    import asyncpg
except ImportError:
    asyncpg = None

try:
    import aioredis
except ImportError:
    aioredis = None

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


class ACGSConfig:
    """
    ACGS Infrastructure Configuration with validated ports and connection settings.

    This configuration standardizes ports and connection management across all ACGS services.
    """

    def __init__(self):
        # Standardized ACGS Service Ports
        self.AUTH_PORT = int(os.getenv("ACGS_AUTH_PORT", "8016"))
        self.POSTGRES_PORT = int(os.getenv("ACGS_POSTGRES_PORT", "5439"))
        self.REDIS_PORT = int(os.getenv("ACGS_REDIS_PORT", "6389"))

        # Additional standardized service ports
        self.CONSTITUTIONAL_AI_PORT = int(
            os.getenv("ACGS_CONSTITUTIONAL_AI_PORT", "8001")
        )
        self.INTEGRITY_SERVICE_PORT = int(
            os.getenv("ACGS_INTEGRITY_SERVICE_PORT", "8002")
        )
        self.GOVERNANCE_SYNTHESIS_PORT = int(
            os.getenv("ACGS_GOVERNANCE_SYNTHESIS_PORT", "8003")
        )
        self.POLICY_GOVERNANCE_PORT = int(
            os.getenv("ACGS_POLICY_GOVERNANCE_PORT", "8004")
        )
        self.FORMAL_VERIFICATION_PORT = int(
            os.getenv("ACGS_FORMAL_VERIFICATION_PORT", "8005")
        )
        self.EVOLUTIONARY_COMPUTATION_PORT = int(
            os.getenv("ACGS_EVOLUTIONARY_COMPUTATION_PORT", "8006")
        )
        self.CODE_ANALYSIS_PORT = int(os.getenv("ACGS_CODE_ANALYSIS_PORT", "8007"))
        self.MULTI_AGENT_COORDINATOR_PORT = int(
            os.getenv("ACGS_MULTI_AGENT_COORDINATOR_PORT", "8008")
        )
        self.WORKER_AGENTS_PORT = int(os.getenv("ACGS_WORKER_AGENTS_PORT", "8009"))
        self.BLACKBOARD_SERVICE_PORT = int(
            os.getenv("ACGS_BLACKBOARD_SERVICE_PORT", "8010")
        )

        # Database Configuration
        self.POSTGRES_HOST = os.getenv("ACGS_POSTGRES_HOST", "localhost")
        self.POSTGRES_USER = os.getenv("ACGS_POSTGRES_USER", "acgs_user")
        self.POSTGRES_PASSWORD = os.getenv(
            "ACGS_POSTGRES_PASSWORD", "acgs_secure_password"
        )
        self.POSTGRES_DB = os.getenv("ACGS_POSTGRES_DB", "acgs_db")

        # Enhanced Connection Pool Settings (asyncpg) - Optimized for >200 connections
        self.POSTGRES_POOL_MIN_SIZE = int(
            os.getenv("ACGS_POSTGRES_POOL_MIN_SIZE", "20")
        )  # Increased from 5
        self.POSTGRES_POOL_MAX_SIZE = int(
            os.getenv("ACGS_POSTGRES_POOL_MAX_SIZE", "50")  # Increased from 20
        )
        self.POSTGRES_POOL_TIMEOUT = int(os.getenv("ACGS_POSTGRES_POOL_TIMEOUT", "30"))

        # Redis Configuration
        self.REDIS_HOST = os.getenv("ACGS_REDIS_HOST", "localhost")
        self.REDIS_PASSWORD = os.getenv("ACGS_REDIS_PASSWORD", None)
        self.REDIS_DB = int(os.getenv("ACGS_REDIS_DB", "0"))
        self.REDIS_MAX_CONNECTIONS = int(os.getenv("ACGS_REDIS_MAX_CONNECTIONS", "50"))
        self.REDIS_TIMEOUT = int(os.getenv("ACGS_REDIS_TIMEOUT", "5"))

        # Prometheus Metrics Configuration
        self.PROMETHEUS_METRICS_ENABLED = (
            os.getenv("ACGS_PROMETHEUS_METRICS_ENABLED", "true").lower() == "true"
        )
        self.PROMETHEUS_METRICS_PORT = int(
            os.getenv("ACGS_PROMETHEUS_METRICS_PORT", "9090")
        )
        self.PROMETHEUS_METRICS_PATH = os.getenv(
            "ACGS_PROMETHEUS_METRICS_PATH", "/metrics"
        )

        # Constitutional compliance
        self.CONSTITUTIONAL_HASH = os.getenv(
            "ACGS_CONSTITUTIONAL_HASH", CONSTITUTIONAL_HASH
        )

        # Validate configuration
        self._validate_config()

    def _validate_config(self):
        """Validate configuration values."""
        # Validate port ranges
        for port_name, port_value in [
            ("AUTH_PORT", self.AUTH_PORT),
            ("POSTGRES_PORT", self.POSTGRES_PORT),
            ("REDIS_PORT", self.REDIS_PORT),
        ]:
            if not (1024 <= port_value <= 65535):
                raise ValueError(
                    f"{port_name} {port_value} must be between 1024 and 65535"
                )

        # Validate constitutional hash
        if len(self.CONSTITUTIONAL_HASH) != 16:
            raise ValueError(
                f"Constitutional hash must be 16 characters, got {len(self.CONSTITUTIONAL_HASH)}"
            )

    def get_postgres_url(self) -> str:
        """Get PostgreSQL connection URL for asyncpg"""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    def get_redis_url(self) -> str:
        """Get Redis connection URL for aioredis"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


class DatabaseManager:
    """
    Standardized database connection manager using asyncpg connection pools.
    """

    def __init__(self, config: ACGSConfig):
        self.config = config
        self.pool = None

    async def create_pool(self):
        """Create asyncpg connection pool with standardized configuration"""
        if asyncpg is None:
            raise ImportError("asyncpg is required for database operations")

        if self.pool is not None:
            logger.warning("Database pool already exists")
            return self.pool

        try:
            self.pool = await asyncpg.create_pool(
                dsn=self.config.get_postgres_url(),
                min_size=self.config.POSTGRES_POOL_MIN_SIZE,
                max_size=self.config.POSTGRES_POOL_MAX_SIZE,
                command_timeout=self.config.POSTGRES_POOL_TIMEOUT,
                # Connection validation
                connection_class=asyncpg.Connection,
                # Health check configuration
                server_settings={
                    "application_name": f"acgs_service_{os.getpid()}",
                    "search_path": "public",
                },
            )

            logger.info(
                f"Created asyncpg pool: min_size={self.config.POSTGRES_POOL_MIN_SIZE}, "
                f"max_size={self.config.POSTGRES_POOL_MAX_SIZE}, "
                f"timeout={self.config.POSTGRES_POOL_TIMEOUT}s"
            )

            return self.pool

        except Exception as e:
            logger.exception(f"Failed to create database pool: {e}")
            raise

    async def close_pool(self):
        """Close the database connection pool"""
        if self.pool:
            await self.pool.close()
            self.pool = None
            logger.info("Database pool closed")

    async def get_connection(self):
        """Get a connection from the pool"""
        if not self.pool:
            await self.create_pool()
        return self.pool.acquire()

    async def health_check(self) -> bool:
        """Perform database health check"""
        try:
            if not self.pool:
                return False

            async with self.pool.acquire() as conn:
                result = await conn.fetchval("SELECT 1")
                return result == 1

        except Exception as e:
            logger.exception(f"Database health check failed: {e}")
            return False


class RedisManager:
    """
    Standardized Redis connection manager using aioredis with validated configuration.
    """

    def __init__(self, config: ACGSConfig):
        self.config = config
        self.redis = None

    async def create_connection(self):
        """Create Redis connection with standardized configuration"""
        if aioredis is None:
            raise ImportError("aioredis is required for Redis operations")

        if self.redis is not None:
            logger.warning("Redis connection already exists")
            return self.redis

        try:
            # Validate port before connection
            parsed_url = urlparse(self.config.get_redis_url())
            if parsed_url.port != self.config.REDIS_PORT:
                raise ValueError(
                    f"Redis URL port mismatch: expected {self.config.REDIS_PORT}, got {parsed_url.port}"
                )

            self.redis = await aioredis.from_url(
                self.config.get_redis_url(),
                max_connections=self.config.REDIS_MAX_CONNECTIONS,
                socket_timeout=self.config.REDIS_TIMEOUT,
                socket_connect_timeout=self.config.REDIS_TIMEOUT,
                health_check_interval=30,
                retry_on_timeout=True,
                decode_responses=True,
            )

            logger.info(
                f"Created Redis connection: host={self.config.REDIS_HOST}, "
                f"port={self.config.REDIS_PORT}, "
                f"db={self.config.REDIS_DB}, "
                f"max_connections={self.config.REDIS_MAX_CONNECTIONS}"
            )

            return self.redis

        except Exception as e:
            logger.exception(f"Failed to create Redis connection: {e}")
            raise

    async def close_connection(self):
        """Close the Redis connection"""
        if self.redis:
            await self.redis.close()
            self.redis = None
            logger.info("Redis connection closed")

    async def health_check(self) -> bool:
        """Perform Redis health check"""
        try:
            if not self.redis:
                return False

            await self.redis.ping()
            return True

        except Exception as e:
            logger.exception(f"Redis health check failed: {e}")
            return False


# Global configuration instance
acgs_config = ACGSConfig()

# Global manager instances
database_manager = DatabaseManager(acgs_config)
redis_manager = RedisManager(acgs_config)


def get_acgs_config() -> ACGSConfig:
    """Get the global ACGS configuration instance"""
    return acgs_config


def get_database_manager() -> DatabaseManager:
    """Get the global database manager instance"""
    return database_manager


def get_redis_manager() -> RedisManager:
    """Get the global Redis manager instance"""
    return redis_manager


async def initialize_infrastructure():
    """Initialize all infrastructure components"""
    logger.info(
        f"Initializing ACGS infrastructure with constitutional hash: {CONSTITUTIONAL_HASH}"
    )

    # Initialize database pool
    await database_manager.create_pool()

    # Initialize Redis connection
    await redis_manager.create_connection()

    logger.info("ACGS infrastructure initialization complete")


async def cleanup_infrastructure():
    """Cleanup all infrastructure components"""
    logger.info("Cleaning up ACGS infrastructure")

    # Cleanup database pool
    await database_manager.close_pool()

    # Cleanup Redis connection
    await redis_manager.close_connection()

    logger.info("ACGS infrastructure cleanup complete")


# Export key components
__all__ = [
    "CONSTITUTIONAL_HASH",
    "ACGSConfig",
    "DatabaseManager",
    "RedisManager",
    "acgs_config",
    "cleanup_infrastructure",
    "database_manager",
    "get_acgs_config",
    "get_database_manager",
    "get_redis_manager",
    "initialize_infrastructure",
    "redis_manager",
]
