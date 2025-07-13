"""
High-Performance Connection Pool Manager for ACGS Services
Constitutional Hash: cdd01ef066bc6cf2

Advanced connection pool management with performance tracking, monitoring,
and optimization for PostgreSQL and Redis connections.
"""

import asyncio
import logging
import threading
import time
from collections import deque
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any

# Constitutional compliance hash
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


@dataclass
class ConnectionMetrics:
    """Connection performance metrics."""

    total_connections: int = 0
    active_connections: int = 0
    peak_connections: int = 0
    connection_times: deque = field(default_factory=lambda: deque(maxlen=1000))
    query_times: deque = field(default_factory=lambda: deque(maxlen=1000))
    error_count: int = 0
    timeout_count: int = 0

    def add_connection_time(self, time_ms: float):
        """Add connection time measurement."""
        self.connection_times.append(time_ms)

    def add_query_time(self, time_ms: float):
        """Add query time measurement."""
        self.query_times.append(time_ms)

    def get_avg_connection_time(self) -> float:
        """Get average connection time."""
        if not self.connection_times:
            return 0.0
        return sum(self.connection_times) / len(self.connection_times)

    def get_avg_query_time(self) -> float:
        """Get average query time."""
        if not self.query_times:
            return 0.0
        return sum(self.query_times) / len(self.query_times)

    def get_p95_connection_time(self) -> float:
        """Get P95 connection time."""
        if not self.connection_times:
            return 0.0
        sorted_times = sorted(self.connection_times)
        index = int(len(sorted_times) * 0.95)
        return sorted_times[min(index, len(sorted_times) - 1)]


class HighPerformanceConnectionPool:
    """High-performance connection pool with monitoring and optimization."""

    def __init__(
        self,
        pool_name: str,
        min_size: int = 20,
        max_size: int = 50,
        timeout: float = 10.0,
        constitutional_hash: str = CONSTITUTIONAL_HASH,
    ):
        self.pool_name = pool_name
        self.min_size = min_size
        self.max_size = max_size
        self.timeout = timeout
        self.constitutional_hash = constitutional_hash

        # Connection pool
        self.pool = None
        self.is_initialized = False

        # Performance metrics
        self.metrics = ConnectionMetrics()
        self.metrics_lock = threading.Lock()

        # Health monitoring
        self.last_health_check = 0
        self.health_check_interval = 30  # 30 seconds
        self.is_healthy = True

        logger.info(
            f"Initialized {pool_name} connection pool: {min_size}-{max_size} connections"
        )

    async def initialize_postgresql_pool(self, dsn: str):
        """Initialize PostgreSQL connection pool with optimizations."""
        try:
            import asyncpg

            start_time = time.perf_counter()

            # Create optimized connection pool
            self.pool = await asyncpg.create_pool(
                dsn=dsn,
                min_size=self.min_size,
                max_size=self.max_size,
                command_timeout=self.timeout,
                # Performance optimizations
                server_settings={
                    "application_name": f"acgs_{self.pool_name}",
                    "search_path": "public",
                    "statement_timeout": f"{int(self.timeout * 1000)}ms",
                    "idle_in_transaction_session_timeout": "300s",
                    "tcp_keepalives_idle": "600",
                    "tcp_keepalives_interval": "30",
                    "tcp_keepalives_count": "3",
                },
                # Connection initialization
                init=self._init_postgresql_connection,
                # Connection setup
                setup=self._setup_postgresql_connection,
            )

            connection_time = (time.perf_counter() - start_time) * 1000
            self.metrics.add_connection_time(connection_time)

            self.is_initialized = True

            logger.info(
                f"✅ PostgreSQL pool '{self.pool_name}' initialized in {connection_time:.2f}ms "
                f"[hash: {CONSTITUTIONAL_HASH}]"
            )

            return self.pool

        except Exception as e:
            logger.exception(
                f"❌ Failed to initialize PostgreSQL pool '{self.pool_name}': {e}"
            )
            self.metrics.error_count += 1
            raise

    async def initialize_redis_pool(self, redis_url: str, max_connections: int = 50):
        """Initialize Redis connection pool with optimizations."""
        try:
            import aioredis

            start_time = time.perf_counter()

            # Create optimized Redis pool
            self.pool = aioredis.ConnectionPool.from_url(
                redis_url,
                max_connections=max_connections,
                retry_on_timeout=True,
                socket_timeout=5.0,
                socket_connect_timeout=5.0,
                socket_keepalive=True,
                socket_keepalive_options={
                    1: 1,  # TCP_KEEPIDLE
                    2: 3,  # TCP_KEEPINTVL
                    3: 5,  # TCP_KEEPCNT
                },
                decode_responses=True,
                encoding="utf-8",
            )

            # Test connection
            redis = aioredis.Redis(connection_pool=self.pool)
            await redis.ping()

            # Set constitutional hash
            await redis.set(f"acgs:pool:{self.pool_name}:hash", CONSTITUTIONAL_HASH)

            connection_time = (time.perf_counter() - start_time) * 1000
            self.metrics.add_connection_time(connection_time)

            self.is_initialized = True

            logger.info(
                f"✅ Redis pool '{self.pool_name}' initialized in {connection_time:.2f}ms "
                f"[hash: {CONSTITUTIONAL_HASH}]"
            )

            return self.pool

        except Exception as e:
            logger.exception(
                f"❌ Failed to initialize Redis pool '{self.pool_name}': {e}"
            )
            self.metrics.error_count += 1
            raise

    async def _init_postgresql_connection(self, connection):
        """Initialize PostgreSQL connection with optimizations."""
        # Set connection-level optimizations
        await connection.execute("SET synchronous_commit = off")
        await connection.execute("SET wal_writer_delay = '10ms'")
        await connection.execute("SET checkpoint_completion_target = 0.9")
        await connection.execute("SET effective_cache_size = '1GB'")
        await connection.execute("SET shared_buffers = '256MB'")

        # Set constitutional hash
        await connection.execute(
            "SELECT set_config('acgs.constitutional_hash', $1, false)",
            CONSTITUTIONAL_HASH,
        )

        with self.metrics_lock:
            self.metrics.total_connections += 1

    async def _setup_postgresql_connection(self, connection):
        """Setup PostgreSQL connection for performance."""
        # Prepare common statements
        await connection.execute("PREPARE acgs_health_check AS SELECT 1")
        await connection.execute(
            "PREPARE acgs_hash_check AS SELECT current_setting('acgs.constitutional_hash')"
        )

    @asynccontextmanager
    async def get_connection(self):
        """Get connection with performance monitoring."""
        if not self.is_initialized or not self.pool:
            raise RuntimeError(f"Connection pool '{self.pool_name}' not initialized")

        start_time = time.perf_counter()
        connection = None

        try:
            # Acquire connection with timeout
            connection = await asyncio.wait_for(
                self.pool.acquire(), timeout=self.timeout
            )

            connection_time = (time.perf_counter() - start_time) * 1000

            with self.metrics_lock:
                self.metrics.active_connections += 1
                self.metrics.peak_connections = max(
                    self.metrics.peak_connections, self.metrics.active_connections
                )
                self.metrics.add_connection_time(connection_time)

            # Log slow connections
            if connection_time > 2.0:  # >2ms is slow
                logger.warning(
                    f"Slow connection acquisition for '{self.pool_name}': {connection_time:.2f}ms"
                )

            yield connection

        except asyncio.TimeoutError:
            with self.metrics_lock:
                self.metrics.timeout_count += 1
            logger.exception(
                f"Connection timeout for pool '{self.pool_name}' after {self.timeout}s"
            )
            raise
        except Exception as e:
            with self.metrics_lock:
                self.metrics.error_count += 1
            logger.exception(f"Connection error for pool '{self.pool_name}': {e}")
            raise
        finally:
            if connection:
                try:
                    await self.pool.release(connection)
                    with self.metrics_lock:
                        self.metrics.active_connections -= 1
                except Exception as e:
                    logger.exception(f"Error releasing connection: {e}")

    async def execute_query(self, query: str, *args, **kwargs):
        """Execute query with performance monitoring."""
        start_time = time.perf_counter()

        async with self.get_connection() as conn:
            try:
                if hasattr(conn, "fetch"):  # PostgreSQL
                    result = await conn.fetch(query, *args, **kwargs)
                else:  # Redis
                    result = await conn.execute(query, *args, **kwargs)

                query_time = (time.perf_counter() - start_time) * 1000

                with self.metrics_lock:
                    self.metrics.add_query_time(query_time)

                # Log slow queries
                if query_time > 5.0:  # >5ms is slow
                    logger.warning(
                        f"Slow query for '{self.pool_name}' ({query_time:.2f}ms): {query[:100]}..."
                    )

                return result

            except Exception as e:
                with self.metrics_lock:
                    self.metrics.error_count += 1
                logger.exception(f"Query failed for pool '{self.pool_name}': {e}")
                raise

    async def health_check(self) -> bool:
        """Perform health check on connection pool."""
        current_time = time.time()

        # Skip if recently checked
        if current_time - self.last_health_check < self.health_check_interval:
            return self.is_healthy

        try:
            async with self.get_connection() as conn:
                if hasattr(conn, "fetchval"):  # PostgreSQL
                    result = await conn.fetchval("EXECUTE acgs_hash_check")
                    health_ok = result == CONSTITUTIONAL_HASH
                else:  # Redis
                    result = await conn.get(f"acgs:pool:{self.pool_name}:hash")
                    health_ok = result == CONSTITUTIONAL_HASH

                self.is_healthy = health_ok
                self.last_health_check = current_time

                if not health_ok:
                    logger.error(
                        f"Health check failed for pool '{self.pool_name}': hash mismatch"
                    )

                return health_ok

        except Exception as e:
            logger.exception(f"Health check error for pool '{self.pool_name}': {e}")
            self.is_healthy = False
            self.last_health_check = current_time
            return False

    def get_performance_stats(self) -> dict[str, Any]:
        """Get comprehensive performance statistics."""
        with self.metrics_lock:
            pool_size = (
                self.pool.get_size()
                if self.pool and hasattr(self.pool, "get_size")
                else 0
            )

            return {
                "pool_name": self.pool_name,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "pool_config": {
                    "min_size": self.min_size,
                    "max_size": self.max_size,
                    "timeout": self.timeout,
                    "current_size": pool_size,
                },
                "connection_metrics": {
                    "total_connections": self.metrics.total_connections,
                    "active_connections": self.metrics.active_connections,
                    "peak_connections": self.metrics.peak_connections,
                    "avg_connection_time_ms": self.metrics.get_avg_connection_time(),
                    "p95_connection_time_ms": self.metrics.get_p95_connection_time(),
                },
                "query_metrics": {
                    "avg_query_time_ms": self.metrics.get_avg_query_time(),
                    "total_queries": len(self.metrics.query_times),
                },
                "error_metrics": {
                    "error_count": self.metrics.error_count,
                    "timeout_count": self.metrics.timeout_count,
                    "error_rate": (
                        self.metrics.error_count
                        / max(self.metrics.total_connections, 1)
                        * 100
                    ),
                },
                "health": {
                    "is_healthy": self.is_healthy,
                    "last_health_check": self.last_health_check,
                },
                "performance_targets": {
                    "connection_time_target_ms": 2.0,
                    "query_time_target_ms": 5.0,
                    "connection_time_met": self.metrics.get_avg_connection_time()
                    <= 2.0,
                    "query_time_met": self.metrics.get_avg_query_time() <= 5.0,
                },
            }

    async def close(self):
        """Close the connection pool."""
        if self.pool:
            if hasattr(self.pool, "close"):  # PostgreSQL
                await self.pool.close()
            else:  # Redis
                await self.pool.disconnect()

            logger.info(f"Connection pool '{self.pool_name}' closed")


# Global connection pool manager
class ConnectionPoolManager:
    """Global connection pool manager for ACGS services."""

    def __init__(self):
        self.pools: dict[str, HighPerformanceConnectionPool] = {}
        self.constitutional_hash = CONSTITUTIONAL_HASH

    async def create_postgresql_pool(
        self,
        name: str,
        dsn: str,
        min_size: int = 20,
        max_size: int = 50,
        timeout: float = 10.0,
    ) -> HighPerformanceConnectionPool:
        """Create and register PostgreSQL connection pool."""
        pool = HighPerformanceConnectionPool(name, min_size, max_size, timeout)
        await pool.initialize_postgresql_pool(dsn)
        self.pools[name] = pool
        return pool

    async def create_redis_pool(
        self,
        name: str,
        redis_url: str,
        max_connections: int = 50,
        timeout: float = 5.0,
    ) -> HighPerformanceConnectionPool:
        """Create and register Redis connection pool."""
        pool = HighPerformanceConnectionPool(name, 0, max_connections, timeout)
        await pool.initialize_redis_pool(redis_url, max_connections)
        self.pools[name] = pool
        return pool

    def get_pool(self, name: str) -> HighPerformanceConnectionPool | None:
        """Get connection pool by name."""
        return self.pools.get(name)

    async def health_check_all(self) -> dict[str, bool]:
        """Perform health check on all pools."""
        results = {}
        for name, pool in self.pools.items():
            results[name] = await pool.health_check()
        return results

    def get_all_stats(self) -> dict[str, dict[str, Any]]:
        """Get performance statistics for all pools."""
        return {name: pool.get_performance_stats() for name, pool in self.pools.items()}

    async def close_all(self):
        """Close all connection pools."""
        for pool in self.pools.values():
            await pool.close()
        self.pools.clear()


# Global instance
connection_pool_manager = ConnectionPoolManager()
