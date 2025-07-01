"""
Enterprise PostgreSQL Connection Pooling for ACGS-1

Provides high-performance connection pooling with:
- Async connection management
- Circuit breaker pattern
- Health monitoring
- Read/write splitting
- Connection retry mechanisms
- Performance metrics
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass
from enum import Enum
from typing import Any

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.pool import QueuePool

logger = logging.getLogger(__name__)


class ConnectionState(Enum):
    """Connection pool states."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    RECOVERING = "recovering"


@dataclass
class PoolConfig:
    """Connection pool configuration."""

    # Primary database
    primary_host: str = "localhost"
    primary_port: int = 5432
    primary_database: str = "acgs_db"
    primary_user: str = "acgs_user"
    primary_password: str = "acgs_password"

    # Read replica (optional)
    replica_host: str | None = None
    replica_port: int = 5432
    replica_database: str | None = None
    replica_user: str | None = None
    replica_password: str | None = None

    # Pool settings
    min_connections: int = 5
    max_connections: int = 20
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600
    pool_pre_ping: bool = True

    # Circuit breaker settings
    failure_threshold: int = 5
    recovery_timeout: int = 60
    health_check_interval: int = 30

    # Performance settings
    command_timeout: int = 60
    server_settings: dict[str, str] = None

    def __post_init__(self):
        if self.server_settings is None:
            self.server_settings = {
                "application_name": "acgs-1",
                "tcp_keepalives_idle": "600",
                "tcp_keepalives_interval": "30",
                "tcp_keepalives_count": "3",
            }


class CircuitBreaker:
    """Circuit breaker for database connections."""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = ConnectionState.HEALTHY

    def record_success(self):
        """Record successful operation."""
        self.failure_count = 0
        self.state = ConnectionState.HEALTHY

    def record_failure(self):
        """Record failed operation."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = ConnectionState.FAILED
            logger.warning(
                f"Circuit breaker opened after {self.failure_count} failures"
            )

    def can_execute(self) -> bool:
        """Check if operations can be executed."""
        if self.state == ConnectionState.HEALTHY:
            return True

        if self.state == ConnectionState.FAILED:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = ConnectionState.RECOVERING
                logger.info("Circuit breaker entering recovery state")
                return True
            return False

        # RECOVERING state - allow limited operations
        return True

    def is_healthy(self) -> bool:
        """Check if circuit breaker is in healthy state."""
        return self.state == ConnectionState.HEALTHY


class ConnectionPool:
    """Enterprise PostgreSQL connection pool."""

    def __init__(self, config: PoolConfig):
        self.config = config
        self.primary_engine: AsyncEngine | None = None
        self.replica_engine: AsyncEngine | None = None
        self.primary_circuit_breaker = CircuitBreaker(
            config.failure_threshold, config.recovery_timeout
        )
        self.replica_circuit_breaker = CircuitBreaker(
            config.failure_threshold, config.recovery_timeout
        )
        self.health_check_task: asyncio.Task | None = None
        self.metrics = {
            "total_connections": 0,
            "active_connections": 0,
            "failed_connections": 0,
            "query_count": 0,
            "avg_query_time": 0.0,
            "last_health_check": 0,
        }

    async def initialize(self):
        """Initialize connection pools."""
        try:
            # Create primary engine
            primary_url = self._build_connection_url(
                self.config.primary_host,
                self.config.primary_port,
                self.config.primary_database,
                self.config.primary_user,
                self.config.primary_password,
            )

            self.primary_engine = create_async_engine(
                primary_url,
                poolclass=QueuePool,
                pool_size=self.config.min_connections,
                max_overflow=self.config.max_overflow,
                pool_timeout=self.config.pool_timeout,
                pool_recycle=self.config.pool_recycle,
                pool_pre_ping=self.config.pool_pre_ping,
                echo=False,  # Set to True for SQL debugging
            )

            # Create replica engine if configured
            if self.config.replica_host:
                replica_url = self._build_connection_url(
                    self.config.replica_host,
                    self.config.replica_port,
                    self.config.replica_database or self.config.primary_database,
                    self.config.replica_user or self.config.primary_user,
                    self.config.replica_password or self.config.primary_password,
                )

                self.replica_engine = create_async_engine(
                    replica_url,
                    poolclass=QueuePool,
                    pool_size=self.config.min_connections,
                    max_overflow=self.config.max_overflow,
                    pool_timeout=self.config.pool_timeout,
                    pool_recycle=self.config.pool_recycle,
                    pool_pre_ping=self.config.pool_pre_ping,
                    echo=False,
                )

            # Start health check task
            self.health_check_task = asyncio.create_task(self._health_check_loop())

            logger.info("Database connection pool initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize connection pool: {e}")
            raise

    def _build_connection_url(
        self, host: str, port: int, database: str, user: str, password: str
    ) -> str:
        """Build PostgreSQL connection URL."""
        return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}"

    @asynccontextmanager
    async def get_connection(self, read_only: bool = False):
        """Get database connection with circuit breaker protection."""
        engine = self._select_engine(read_only)
        circuit_breaker = self._select_circuit_breaker(read_only)

        if not circuit_breaker.can_execute():
            raise Exception(
                f"Circuit breaker is open for {'replica' if read_only else 'primary'} database"
            )

        start_time = time.time()
        connection = None

        try:
            async with engine.begin() as connection:
                self.metrics["active_connections"] += 1
                yield connection

                # Record success
                circuit_breaker.record_success()

                # Update metrics
                query_time = time.time() - start_time
                self.metrics["query_count"] += 1
                self.metrics["avg_query_time"] = (
                    self.metrics["avg_query_time"] * (self.metrics["query_count"] - 1)
                    + query_time
                ) / self.metrics["query_count"]

        except Exception as e:
            # Record failure
            circuit_breaker.record_failure()
            self.metrics["failed_connections"] += 1
            logger.error(f"Database connection error: {e}")
            raise

        finally:
            if connection:
                self.metrics["active_connections"] -= 1

    def _select_engine(self, read_only: bool) -> AsyncEngine:
        """Select appropriate engine based on operation type."""
        if (
            read_only
            and self.replica_engine
            and self.replica_circuit_breaker.is_healthy()
        ):
            return self.replica_engine
        return self.primary_engine

    def _select_circuit_breaker(self, read_only: bool) -> CircuitBreaker:
        """Select appropriate circuit breaker."""
        if read_only and self.replica_engine:
            return self.replica_circuit_breaker
        return self.primary_circuit_breaker

    async def _health_check_loop(self):
        """Periodic health check for connections."""
        while True:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                await self._perform_health_check()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check error: {e}")

    async def _perform_health_check(self):
        """Perform health check on all engines."""
        self.metrics["last_health_check"] = time.time()

        # Check primary engine
        try:
            async with self.primary_engine.begin() as conn:
                await conn.execute("SELECT 1")
            self.primary_circuit_breaker.record_success()
        except Exception as e:
            self.primary_circuit_breaker.record_failure()
            logger.warning(f"Primary database health check failed: {e}")

        # Check replica engine if available
        if self.replica_engine:
            try:
                async with self.replica_engine.begin() as conn:
                    await conn.execute("SELECT 1")
                self.replica_circuit_breaker.record_success()
            except Exception as e:
                self.replica_circuit_breaker.record_failure()
                logger.warning(f"Replica database health check failed: {e}")

    async def get_pool_status(self) -> dict[str, Any]:
        """Get connection pool status and metrics."""
        primary_pool = self.primary_engine.pool if self.primary_engine else None
        replica_pool = self.replica_engine.pool if self.replica_engine else None

        return {
            "primary": {
                "state": self.primary_circuit_breaker.state.value,
                "failure_count": self.primary_circuit_breaker.failure_count,
                "pool_size": primary_pool.size() if primary_pool else 0,
                "checked_in": primary_pool.checkedin() if primary_pool else 0,
                "checked_out": primary_pool.checkedout() if primary_pool else 0,
                "overflow": primary_pool.overflow() if primary_pool else 0,
            },
            "replica": {
                "state": (
                    self.replica_circuit_breaker.state.value
                    if self.replica_engine
                    else "disabled"
                ),
                "failure_count": (
                    self.replica_circuit_breaker.failure_count
                    if self.replica_engine
                    else 0
                ),
                "pool_size": replica_pool.size() if replica_pool else 0,
                "checked_in": replica_pool.checkedin() if replica_pool else 0,
                "checked_out": replica_pool.checkedout() if replica_pool else 0,
                "overflow": replica_pool.overflow() if replica_pool else 0,
            },
            "metrics": self.metrics.copy(),
        }

    async def close(self):
        """Close all connections and cleanup."""
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass

        if self.primary_engine:
            await self.primary_engine.dispose()

        if self.replica_engine:
            await self.replica_engine.dispose()

        logger.info("Database connection pool closed")


# Global connection pool instance
_connection_pool: ConnectionPool | None = None


async def initialize_connection_pool(config: PoolConfig) -> ConnectionPool:
    """Initialize global connection pool."""
    global _connection_pool
    _connection_pool = ConnectionPool(config)
    await _connection_pool.initialize()
    return _connection_pool


def get_connection_pool() -> ConnectionPool:
    """Get global connection pool instance."""
    if _connection_pool is None:
        raise RuntimeError(
            "Connection pool not initialized. Call initialize_connection_pool() first."
        )
    return _connection_pool


async def close_connection_pool():
    """Close global connection pool."""
    global _connection_pool
    if _connection_pool:
        await _connection_pool.close()
        _connection_pool = None
