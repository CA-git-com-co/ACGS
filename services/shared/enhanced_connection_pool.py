"""
Enhanced Database Connection Pooling
====================================

Optimized connection pooling for ACGS services to improve throughput and scalability.
Addresses the AC service throughput issue (643 RPS vs 1000 RPS target).
"""

import logging
import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import QueuePool

logger = logging.getLogger(__name__)


class EnhancedConnectionPool:
    """
    Enhanced database connection pool with optimized settings for high throughput.
    """

    def __init__(
        self,
        database_url: str,
        min_connections: int = 10,
        max_connections: int = 50,
        max_overflow: int = 20,
        pool_timeout: int = 30,
        pool_recycle: int = 3600,
        pool_pre_ping: bool = True,
    ):
        self.database_url = database_url
        self.min_connections = min_connections
        self.max_connections = max_connections
        self.max_overflow = max_overflow
        self.pool_timeout = pool_timeout
        self.pool_recycle = pool_recycle
        self.pool_pre_ping = pool_pre_ping

        self.engine = None
        self.session_factory = None
        self._connection_stats = {
            "total_connections": 0,
            "active_connections": 0,
            "pool_hits": 0,
            "pool_misses": 0,
            "connection_errors": 0,
        }

    async def initialize(self):
        """Initialize the connection pool with optimized settings."""
        try:
            # Create engine with optimized pool settings
            self.engine = create_async_engine(
                self.database_url,
                poolclass=QueuePool,
                pool_size=self.min_connections,
                max_overflow=self.max_overflow,
                pool_timeout=self.pool_timeout,
                pool_recycle=self.pool_recycle,
                pool_pre_ping=self.pool_pre_ping,
                # Optimization settings
                echo=False,  # Disable SQL logging for performance
                future=True,
                connect_args={
                    "server_settings": {
                        "application_name": "acgs_optimized_pool",
                        "jit": "off",  # Disable JIT for faster connection
                    }
                },
            )

            # Create session factory
            self.session_factory = async_sessionmaker(
                bind=self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=False,  # Manual flush for better control
                autocommit=False,
            )

            logger.info(
                f"Enhanced connection pool initialized: {self.min_connections}-{self.max_connections} connections"
            )

        except Exception as e:
            logger.error(f"Failed to initialize connection pool: {e}")
            raise

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get a database session from the pool."""
        session = None
        start_time = time.time()

        try:
            session = self.session_factory()
            self._connection_stats["pool_hits"] += 1
            self._connection_stats["active_connections"] += 1

            yield session

            # Commit if no exception occurred
            await session.commit()

        except Exception as e:
            self._connection_stats["connection_errors"] += 1
            if session:
                await session.rollback()
            logger.error(f"Database session error: {e}")
            raise

        finally:
            if session:
                await session.close()
                self._connection_stats["active_connections"] -= 1

            # Track performance metrics
            duration = time.time() - start_time
            if duration > 1.0:  # Log slow queries
                logger.warning(f"Slow database operation: {duration:.2f}s")

    async def get_connection_stats(self) -> dict[str, Any]:
        """Get connection pool statistics."""
        pool_stats = {}

        if self.engine and self.engine.pool:
            pool = self.engine.pool
            pool_stats = {
                "pool_size": pool.size(),
                "checked_in": pool.checkedin(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
                "invalid": pool.invalid(),
            }

        return {
            **self._connection_stats,
            **pool_stats,
            "pool_efficiency": (
                self._connection_stats["pool_hits"]
                / max(
                    1,
                    self._connection_stats["pool_hits"]
                    + self._connection_stats["pool_misses"],
                )
            ),
        }

    async def health_check(self) -> dict[str, Any]:
        """Perform health check on the connection pool."""
        try:
            async with self.get_session() as session:
                result = await session.execute("SELECT 1")
                await result.fetchone()

            stats = await self.get_connection_stats()

            return {
                "status": "healthy",
                "pool_stats": stats,
                "response_time_ms": time.time() * 1000,
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "pool_stats": await self.get_connection_stats(),
            }

    async def close(self):
        """Close the connection pool."""
        if self.engine:
            await self.engine.dispose()
            logger.info("Connection pool closed")


class ConnectionPoolManager:
    """
    Global connection pool manager for ACGS services.
    """

    _pools: dict[str, EnhancedConnectionPool] = {}

    @classmethod
    async def get_pool(
        cls, service_name: str, database_url: str, **pool_kwargs
    ) -> EnhancedConnectionPool:
        """Get or create a connection pool for a service."""
        if service_name not in cls._pools:
            pool = EnhancedConnectionPool(database_url, **pool_kwargs)
            await pool.initialize()
            cls._pools[service_name] = pool
            logger.info(f"Created connection pool for {service_name}")

        return cls._pools[service_name]

    @classmethod
    async def close_all_pools(cls):
        """Close all connection pools."""
        for service_name, pool in cls._pools.items():
            await pool.close()
            logger.info(f"Closed connection pool for {service_name}")

        cls._pools.clear()

    @classmethod
    async def get_all_stats(cls) -> dict[str, Any]:
        """Get statistics for all connection pools."""
        stats = {}

        for service_name, pool in cls._pools.items():
            stats[service_name] = await pool.get_connection_stats()

        return stats


# Optimized connection settings for different service types
SERVICE_POOL_CONFIGS = {
    "ac": {  # AC service needs higher throughput
        "min_connections": 15,
        "max_connections": 60,
        "max_overflow": 30,
        "pool_timeout": 10,
    },
    "auth": {
        "min_connections": 10,
        "max_connections": 40,
        "max_overflow": 20,
        "pool_timeout": 15,
    },
    "integrity": {
        "min_connections": 8,
        "max_connections": 30,
        "max_overflow": 15,
        "pool_timeout": 20,
    },
    "fv": {
        "min_connections": 5,
        "max_connections": 25,
        "max_overflow": 10,
        "pool_timeout": 25,
    },
    "gs": {
        "min_connections": 12,
        "max_connections": 50,
        "max_overflow": 25,
        "pool_timeout": 15,
    },
    "pgc": {
        "min_connections": 10,
        "max_connections": 40,
        "max_overflow": 20,
        "pool_timeout": 15,
    },
    "ec": {
        "min_connections": 6,
        "max_connections": 25,
        "max_overflow": 12,
        "pool_timeout": 20,
    },
}


async def setup_optimized_pool(
    service_name: str, database_url: str
) -> EnhancedConnectionPool:
    """
    Setup an optimized connection pool for a specific service.

    Args:
        service_name: Name of the service
        database_url: Database connection URL

    Returns:
        Configured connection pool
    """
    config = SERVICE_POOL_CONFIGS.get(service_name, {})

    pool = await ConnectionPoolManager.get_pool(
        service_name=service_name, database_url=database_url, **config
    )

    logger.info(f"Optimized connection pool setup for {service_name}")
    return pool


# Export key components
__all__ = [
    "SERVICE_POOL_CONFIGS",
    "ConnectionPoolManager",
    "EnhancedConnectionPool",
    "setup_optimized_pool",
]
