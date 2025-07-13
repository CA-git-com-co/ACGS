"""
Advanced Connection Pool Management for ACGS
Constitutional Hash: cdd01ef066bc6cf2

Optimized connection pooling for PostgreSQL, Redis, and other services.
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, AsyncContextManager

import aioredis
import asyncpg
from shared.resilience.circuit_breaker import CircuitBreakerConfig, get_circuit_breaker
from shared.resilience.retry import retry_with_exponential_backoff

logger = logging.getLogger(__name__)


@dataclass
class PoolConfig:
    """Configuration for connection pools."""

    min_size: int = 5  # Minimum connections
    max_size: int = 20  # Maximum connections
    max_queries: int = 50000  # Max queries per connection
    max_inactive_time: int = 300  # Max idle time (seconds)
    retry_attempts: int = 3  # Connection retry attempts
    command_timeout: float = 60.0  # Command timeout
    server_settings: dict[str, str] = None

    def __post_init__(self):
        if self.server_settings is None:
            self.server_settings = {}


@dataclass
class PoolMetrics:
    """Metrics for connection pool monitoring."""

    pool_name: str
    current_size: int = 0
    min_size: int = 0
    max_size: int = 0
    free_connections: int = 0
    used_connections: int = 0
    total_acquisitions: int = 0
    total_releases: int = 0
    failed_acquisitions: int = 0
    average_acquisition_time: float = 0.0
    queries_executed: int = 0
    connections_created: int = 0
    connections_closed: int = 0

    @property
    def utilization_rate(self) -> float:
        """Calculate pool utilization rate."""
        if self.current_size == 0:
            return 0.0
        return self.used_connections / self.current_size

    @property
    def success_rate(self) -> float:
        """Calculate acquisition success rate."""
        total_attempts = self.total_acquisitions + self.failed_acquisitions
        if total_attempts == 0:
            return 1.0
        return self.total_acquisitions / total_attempts

    def to_dict(self) -> dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "pool_name": self.pool_name,
            "current_size": self.current_size,
            "min_size": self.min_size,
            "max_size": self.max_size,
            "free_connections": self.free_connections,
            "used_connections": self.used_connections,
            "utilization_rate": self.utilization_rate,
            "total_acquisitions": self.total_acquisitions,
            "total_releases": self.total_releases,
            "failed_acquisitions": self.failed_acquisitions,
            "success_rate": self.success_rate,
            "average_acquisition_time": self.average_acquisition_time,
            "queries_executed": self.queries_executed,
            "connections_created": self.connections_created,
            "connections_closed": self.connections_closed,
            "constitutional_hash": "cdd01ef066bc6cf2",
        }


class ConnectionPool(ABC):
    """Abstract base class for connection pools."""

    def __init__(self, name: str, config: PoolConfig):
        self.name = name
        self.config = config
        self._metrics = PoolMetrics(
            pool_name=name, min_size=config.min_size, max_size=config.max_size
        )
        self._acquisition_times: list[float] = []
        self._lock = asyncio.Lock()

    @abstractmethod
    async def acquire(self) -> Any:
        """Acquire a connection from the pool."""

    @abstractmethod
    async def release(self, connection: Any) -> None:
        """Release a connection back to the pool."""

    @abstractmethod
    async def close(self) -> None:
        """Close the connection pool."""

    @abstractmethod
    async def get_pool_status(self) -> dict[str, Any]:
        """Get detailed pool status."""

    def get_metrics(self) -> PoolMetrics:
        """Get current pool metrics."""
        return self._metrics

    def _record_acquisition(self, duration: float, success: bool) -> None:
        """Record connection acquisition metrics."""
        if success:
            self._metrics.total_acquisitions += 1
            self._acquisition_times.append(duration)

            # Keep only last 100 acquisition times for average
            if len(self._acquisition_times) > 100:
                self._acquisition_times = self._acquisition_times[-100:]

            self._metrics.average_acquisition_time = sum(self._acquisition_times) / len(
                self._acquisition_times
            )
        else:
            self._metrics.failed_acquisitions += 1

    def _record_release(self) -> None:
        """Record connection release metrics."""
        self._metrics.total_releases += 1

    def _record_query(self) -> None:
        """Record query execution metrics."""
        self._metrics.queries_executed += 1


class PostgreSQLPoolManager(ConnectionPool):
    """Advanced PostgreSQL connection pool with circuit breaker protection."""

    def __init__(self, name: str, dsn: str, config: PoolConfig = None):
        super().__init__(name, config or PoolConfig())
        self.dsn = dsn
        self._pool: asyncpg.Pool | None = None
        self._circuit_breaker = get_circuit_breaker(
            f"postgresql_pool_{name}",
            CircuitBreakerConfig(
                failure_threshold=5, recovery_timeout=60.0, timeout=30.0
            ),
        )
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the PostgreSQL connection pool."""
        if self._initialized:
            return

        try:
            logger.info(f"Initializing PostgreSQL pool '{self.name}'")

            async def setup_connection(conn):
                """Setup function for new connections."""
                # Set application name for monitoring
                await conn.execute(f"SET application_name = 'acgs_{self.name}'")

                # Set timezone
                await conn.execute("SET timezone = 'UTC'")

                # Apply server settings
                for setting, value in self.config.server_settings.items():
                    await conn.execute(f"SET {setting} = $1", value)

            self._pool = await asyncpg.create_pool(
                dsn=self.dsn,
                min_size=self.config.min_size,
                max_size=self.config.max_size,
                max_queries=self.config.max_queries,
                max_inactive_connection_lifetime=self.config.max_inactive_time,
                command_timeout=self.config.command_timeout,
                setup=setup_connection,
            )

            self._metrics.connections_created = self.config.min_size
            self._metrics.current_size = self._pool.get_size()
            self._metrics.free_connections = self._pool.get_idle_size()

            self._initialized = True
            logger.info(f"PostgreSQL pool '{self.name}' initialized successfully")

        except Exception as e:
            logger.exception(f"Failed to initialize PostgreSQL pool '{self.name}': {e}")
            raise

    async def acquire(self) -> asyncpg.Connection:
        """Acquire a PostgreSQL connection with circuit breaker protection."""
        await self.initialize()

        start_time = time.time()

        try:
            connection = await self._circuit_breaker.call(
                self._acquire_internal, fallback=self._acquire_fallback
            )

            duration = time.time() - start_time
            self._record_acquisition(duration, True)

            return connection

        except Exception as e:
            duration = time.time() - start_time
            self._record_acquisition(duration, False)
            logger.exception(
                f"Failed to acquire connection from pool '{self.name}': {e}"
            )
            raise

    async def _acquire_internal(self) -> asyncpg.Connection:
        """Internal connection acquisition."""
        connection = await self._pool.acquire()

        # Update metrics
        self._metrics.current_size = self._pool.get_size()
        self._metrics.free_connections = self._pool.get_idle_size()
        self._metrics.used_connections = (
            self._metrics.current_size - self._metrics.free_connections
        )

        return connection

    async def _acquire_fallback(self) -> asyncpg.Connection:
        """Fallback when circuit breaker is open."""
        logger.warning(
            f"Circuit breaker open for pool '{self.name}', creating direct connection"
        )

        # Create a direct connection as fallback
        return await retry_with_exponential_backoff(
            asyncpg.connect,
            dsn=self.dsn,
            max_attempts=3,
            operation_name="postgresql_direct_connect",
        )

    async def release(self, connection: asyncpg.Connection) -> None:
        """Release a PostgreSQL connection back to the pool."""
        try:
            if hasattr(connection, "_pool") and connection._pool == self._pool:
                # Connection belongs to our pool
                await self._pool.release(connection)
            else:
                # Direct connection, close it
                await connection.close()

            self._record_release()

            # Update metrics
            if self._pool:
                self._metrics.current_size = self._pool.get_size()
                self._metrics.free_connections = self._pool.get_idle_size()
                self._metrics.used_connections = (
                    self._metrics.current_size - self._metrics.free_connections
                )

        except Exception as e:
            logger.exception(f"Error releasing connection to pool '{self.name}': {e}")

    async def execute_query(self, query: str, *args) -> Any:
        """Execute a query with automatic connection management."""
        async with self.acquire() as connection:
            self._record_query()
            return await connection.fetch(query, *args)

    async def execute_transaction(self, queries: list[tuple]) -> list[Any]:
        """Execute multiple queries in a transaction."""
        async with self.acquire() as connection, connection.transaction():
            results = []
            for query, args in queries:
                result = await connection.fetch(query, *args)
                results.append(result)
                self._record_query()
            return results

    async def close(self) -> None:
        """Close the PostgreSQL connection pool."""
        if self._pool:
            logger.info(f"Closing PostgreSQL pool '{self.name}'")
            await self._pool.close()
            self._pool = None
            self._initialized = False

    async def get_pool_status(self) -> dict[str, Any]:
        """Get detailed PostgreSQL pool status."""
        if not self._pool:
            return {"status": "not_initialized"}

        return {
            "status": "active",
            "size": self._pool.get_size(),
            "idle_size": self._pool.get_idle_size(),
            "used_size": self._pool.get_size() - self._pool.get_idle_size(),
            "min_size": self.config.min_size,
            "max_size": self.config.max_size,
            "circuit_breaker": self._circuit_breaker.get_status(),
            "metrics": self._metrics.to_dict(),
        }


class RedisPoolManager(ConnectionPool):
    """Redis connection pool manager with cluster support."""

    def __init__(self, name: str, redis_url: str, config: PoolConfig = None):
        super().__init__(name, config or PoolConfig())
        self.redis_url = redis_url
        self._pool: aioredis.ConnectionPool | None = None
        self._redis: aioredis.Redis | None = None
        self._circuit_breaker = get_circuit_breaker(
            f"redis_pool_{name}",
            CircuitBreakerConfig(
                failure_threshold=3, recovery_timeout=30.0, timeout=10.0
            ),
        )
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the Redis connection pool."""
        if self._initialized:
            return

        try:
            logger.info(f"Initializing Redis pool '{self.name}'")

            self._pool = aioredis.ConnectionPool.from_url(
                self.redis_url,
                max_connections=self.config.max_size,
                encoding="utf-8",
                decode_responses=False,
            )

            self._redis = aioredis.Redis(connection_pool=self._pool)

            # Test connection
            await self._redis.ping()

            self._metrics.current_size = self.config.max_size
            self._metrics.free_connections = self.config.max_size

            self._initialized = True
            logger.info(f"Redis pool '{self.name}' initialized successfully")

        except Exception as e:
            logger.exception(f"Failed to initialize Redis pool '{self.name}': {e}")
            raise

    async def acquire(self) -> aioredis.Redis:
        """Acquire a Redis connection."""
        await self.initialize()

        start_time = time.time()

        try:
            # Redis connection pool handles this internally
            connection = await self._circuit_breaker.call(
                lambda: self._redis, fallback=self._acquire_fallback
            )

            duration = time.time() - start_time
            self._record_acquisition(duration, True)

            return connection

        except Exception as e:
            duration = time.time() - start_time
            self._record_acquisition(duration, False)
            logger.exception(
                f"Failed to acquire Redis connection from pool '{self.name}': {e}"
            )
            raise

    async def _acquire_fallback(self) -> aioredis.Redis:
        """Fallback Redis connection."""
        logger.warning(
            f"Circuit breaker open for Redis pool '{self.name}', creating direct connection"
        )

        return await retry_with_exponential_backoff(
            aioredis.from_url,
            self.redis_url,
            max_attempts=3,
            operation_name="redis_direct_connect",
        )

    async def release(self, connection: aioredis.Redis) -> None:
        """Release a Redis connection (no-op for aioredis)."""
        # aioredis handles connection lifecycle internally
        self._record_release()

    async def execute_command(self, command: str, *args) -> Any:
        """Execute a Redis command."""
        async with self.acquire() as redis:
            self._record_query()
            return await redis.execute_command(command, *args)

    async def close(self) -> None:
        """Close the Redis connection pool."""
        if self._redis:
            logger.info(f"Closing Redis pool '{self.name}'")
            await self._redis.close()
            self._redis = None
            self._pool = None
            self._initialized = False

    async def get_pool_status(self) -> dict[str, Any]:
        """Get detailed Redis pool status."""
        if not self._redis:
            return {"status": "not_initialized"}

        try:
            info = await self._redis.info()
            return {
                "status": "active",
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "circuit_breaker": self._circuit_breaker.get_status(),
                "metrics": self._metrics.to_dict(),
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "metrics": self._metrics.to_dict(),
            }


class ConnectionPoolRegistry:
    """Registry for managing multiple connection pools."""

    def __init__(self):
        self._pools: dict[str, ConnectionPool] = {}

    def register_pool(self, pool: ConnectionPool) -> None:
        """Register a connection pool."""
        self._pools[pool.name] = pool
        logger.info(f"Registered connection pool: {pool.name}")

    def get_pool(self, name: str) -> ConnectionPool | None:
        """Get connection pool by name."""
        return self._pools.get(name)

    async def close_all(self) -> None:
        """Close all registered connection pools."""
        logger.info("Closing all connection pools")
        for pool in self._pools.values():
            try:
                await pool.close()
            except Exception as e:
                logger.exception(f"Error closing pool {pool.name}: {e}")

    async def get_global_status(self) -> dict[str, Any]:
        """Get status of all connection pools."""
        status = {}
        for name, pool in self._pools.items():
            try:
                status[name] = await pool.get_pool_status()
            except Exception as e:
                status[name] = {"error": str(e)}

        return {
            "total_pools": len(self._pools),
            "pools": status,
            "constitutional_hash": "cdd01ef066bc6cf2",
        }


# Global registry
_pool_registry = ConnectionPoolRegistry()


def get_connection_pool_registry() -> ConnectionPoolRegistry:
    """Get the global connection pool registry."""
    return _pool_registry


def get_connection_pool(name: str) -> ConnectionPool | None:
    """Get connection pool by name."""
    return _pool_registry.get_pool(name)


# Convenience context managers
@asyncio.contextmanager
async def get_postgres_connection(
    pool_name: str,
) -> AsyncContextManager[asyncpg.Connection]:
    """Context manager for PostgreSQL connections."""
    pool = get_connection_pool(pool_name)
    if not isinstance(pool, PostgreSQLPoolManager):
        raise ValueError(f"Pool {pool_name} is not a PostgreSQL pool")

    connection = await pool.acquire()
    try:
        yield connection
    finally:
        await pool.release(connection)


@asyncio.contextmanager
async def get_redis_connection(pool_name: str) -> AsyncContextManager[aioredis.Redis]:
    """Context manager for Redis connections."""
    pool = get_connection_pool(pool_name)
    if not isinstance(pool, RedisPoolManager):
        raise ValueError(f"Pool {pool_name} is not a Redis pool")

    connection = await pool.acquire()
    try:
        yield connection
    finally:
        await pool.release(connection)
