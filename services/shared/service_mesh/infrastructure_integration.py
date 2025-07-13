"""
Infrastructure Integration for ACGS-1 Load Balancing
Integrates load balancing with Redis caching and PostgreSQL optimization
"""

import json
import logging
import time
from dataclasses import asdict, dataclass
from typing import Any

import asyncpg

from services.shared.advanced_redis_client import AdvancedRedisClient

from .common_types import ServiceInstance, ServiceType

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


logger = logging.getLogger(__name__)


@dataclass
class ConnectionPoolConfig:
    """Configuration for database connection pooling."""

    min_connections: int = 5
    max_connections: int = 20
    max_inactive_connection_lifetime: float = 300.0
    max_queries: int = 50000
    max_cached_statement_lifetime: int = 300
    command_timeout: float = 60.0


@dataclass
class LoadBalancingMetrics:
    """Load balancing metrics for persistence."""

    service_type: str
    instance_id: str
    timestamp: float
    response_time: float
    success_count: int
    failure_count: int
    current_connections: int
    total_requests: int
    cpu_usage: float | None = None
    memory_usage: float | None = None


class DatabaseConnectionManager:
    """
    Manages PostgreSQL connections with load balancing optimization.

    Provides connection pooling, load distribution, and performance monitoring
    for database operations across multiple service instances.
    """

    def __init__(self, config: ConnectionPoolConfig):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """
        Initialize database connection manager.

        Args:
            config: Connection pool configuration
        """
        self.config = config
        self.pools: dict[str, asyncpg.Pool] = {}
        self.pool_metrics: dict[str, dict[str, Any]] = {}

    async def create_pool(self, pool_name: str, database_url: str) -> asyncpg.Pool:
        """
        Create a connection pool for a database.

        Args:
            pool_name: Name for the connection pool
            database_url: Database connection URL

        Returns:
            Connection pool
        """
        if pool_name in self.pools:
            return self.pools[pool_name]

        pool = await asyncpg.create_pool(
            database_url,
            min_size=self.config.min_connections,
            max_size=self.config.max_connections,
            max_inactive_connection_lifetime=self.config.max_inactive_connection_lifetime,
            max_queries=self.config.max_queries,
            max_cached_statement_lifetime=self.config.max_cached_statement_lifetime,
            command_timeout=self.config.command_timeout,
        )

        self.pools[pool_name] = pool
        self.pool_metrics[pool_name] = {
            "created_at": time.time(),
            "total_queries": 0,
            "failed_queries": 0,
            "avg_query_time": 0.0,
        }

        logger.info(
            f"Created database pool '{pool_name}' with {self.config.max_connections} max connections"
        )
        return pool

    async def get_pool(self, pool_name: str) -> asyncpg.Pool | None:
        """Get connection pool by name."""
        return self.pools.get(pool_name)

    async def execute_query(
        self, pool_name: str, query: str, *args, timeout: float | None = None
    ) -> Any:
        """
        Execute query with performance tracking.

        Args:
            pool_name: Name of the connection pool
            query: SQL query to execute
            *args: Query parameters
            timeout: Query timeout

        Returns:
            Query result
        """
        pool = self.pools.get(pool_name)
        if not pool:
            raise ValueError(f"Pool '{pool_name}' not found")

        start_time = time.time()

        try:
            async with pool.acquire() as connection:
                result = await connection.fetch(query, *args, timeout=timeout)

                # Update metrics
                query_time = time.time() - start_time
                self._update_pool_metrics(pool_name, query_time, success=True)

                return result

        except Exception as e:
            query_time = time.time() - start_time
            self._update_pool_metrics(pool_name, query_time, success=False)
            logger.exception(f"Query failed in pool '{pool_name}': {e}")
            raise

    def _update_pool_metrics(self, pool_name: str, query_time: float, success: bool):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Update pool performance metrics."""
        metrics = self.pool_metrics.get(pool_name, {})

        metrics["total_queries"] = metrics.get("total_queries", 0) + 1
        if not success:
            metrics["failed_queries"] = metrics.get("failed_queries", 0) + 1

        # Update average query time
        total_queries = metrics["total_queries"]
        current_avg = metrics.get("avg_query_time", 0.0)
        metrics["avg_query_time"] = (
            (current_avg * (total_queries - 1)) + query_time
        ) / total_queries

        self.pool_metrics[pool_name] = metrics

    async def get_pool_stats(self, pool_name: str) -> dict[str, Any]:
        """Get connection pool statistics."""
        pool = self.pools.get(pool_name)
        metrics = self.pool_metrics.get(pool_name, {})

        if not pool:
            return {"error": f"Pool '{pool_name}' not found"}

        return {
            "pool_name": pool_name,
            "size": pool.get_size(),
            "max_size": pool.get_max_size(),
            "min_size": pool.get_min_size(),
            "idle_size": pool.get_idle_size(),
            "metrics": metrics,
        }

    async def close_all_pools(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Close all connection pools."""
        for pool_name, pool in self.pools.items():
            await pool.close()
            logger.info(f"Closed database pool '{pool_name}'")

        self.pools.clear()
        self.pool_metrics.clear()


class RedisLoadBalancingCache:
    """
    Redis-based caching for load balancing data.

    Provides high-performance caching for service discovery,
    session affinity, and load balancing metrics.
    """

    def __init__(self, redis_client: AdvancedRedisClient):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """
        Initialize Redis load balancing cache.

        Args:
            redis_client: Advanced Redis client
        """
        self.redis_client = redis_client

        # Cache key prefixes
        self.SERVICE_INSTANCES_PREFIX = "lb:instances"
        self.SESSION_AFFINITY_PREFIX = "lb:session"
        self.METRICS_PREFIX = "lb:metrics"
        self.HEALTH_PREFIX = "lb:health"

        # Cache TTLs
        self.INSTANCE_TTL = 300  # 5 minutes
        self.SESSION_TTL = 3600  # 1 hour
        self.METRICS_TTL = 600  # 10 minutes
        self.HEALTH_TTL = 60  # 1 minute

    async def cache_service_instances(
        self, service_type: ServiceType, instances: list[ServiceInstance]
    ):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Cache service instances for a service type."""
        key = f"{self.SERVICE_INSTANCES_PREFIX}:{service_type.value}"

        # Convert instances to serializable format
        instances_data = [
            {
                "instance_id": inst.instance_id,
                "base_url": inst.base_url,
                "port": inst.port,
                "status": inst.status,
                "response_time": inst.response_time,
                "weight": inst.weight,
                "current_connections": inst.current_connections,
                "total_requests": inst.total_requests,
                "failed_requests": inst.failed_requests,
                "last_check": inst.last_check,
            }
            for inst in instances
        ]

        await self.redis_client.setex(
            key, self.INSTANCE_TTL, json.dumps(instances_data)
        )

    async def get_cached_service_instances(
        self, service_type: ServiceType
    ) -> list[dict[str, Any]] | None:
        """Get cached service instances."""
        key = f"{self.SERVICE_INSTANCES_PREFIX}:{service_type.value}"

        data = await self.redis_client.get(key)
        if data:
            return json.loads(data)
        return None

    async def cache_session_affinity(
        self, session_id: str, service_type: ServiceType, instance_id: str
    ):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Cache session affinity mapping."""
        key = f"{self.SESSION_AFFINITY_PREFIX}:{session_id}:{service_type.value}"

        await self.redis_client.setex(key, self.SESSION_TTL, instance_id)

    async def get_session_affinity(
        self, session_id: str, service_type: ServiceType
    ) -> str | None:
        """Get cached session affinity."""
        key = f"{self.SESSION_AFFINITY_PREFIX}:{session_id}:{service_type.value}"

        return await self.redis_client.get(key)

    async def cache_load_balancing_metrics(self, metrics: LoadBalancingMetrics):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Cache load balancing metrics."""
        key = f"{self.METRICS_PREFIX}:{metrics.service_type}:{metrics.instance_id}"

        await self.redis_client.setex(
            key, self.METRICS_TTL, json.dumps(asdict(metrics))
        )

    async def get_cached_metrics(
        self, service_type: str, instance_id: str
    ) -> LoadBalancingMetrics | None:
        """Get cached load balancing metrics."""
        key = f"{self.METRICS_PREFIX}:{service_type}:{instance_id}"

        data = await self.redis_client.get(key)
        if data:
            metrics_data = json.loads(data)
            return LoadBalancingMetrics(**metrics_data)
        return None

    async def cache_health_status(
        self,
        service_type: ServiceType,
        instance_id: str,
        is_healthy: bool,
        response_time: float | None = None,
    ):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Cache instance health status."""
        key = f"{self.HEALTH_PREFIX}:{service_type.value}:{instance_id}"

        health_data = {
            "is_healthy": is_healthy,
            "response_time": response_time,
            "timestamp": time.time(),
        }

        await self.redis_client.setex(key, self.HEALTH_TTL, json.dumps(health_data))

    async def get_cached_health_status(
        self, service_type: ServiceType, instance_id: str
    ) -> dict[str, Any] | None:
        """Get cached health status."""
        key = f"{self.HEALTH_PREFIX}:{service_type.value}:{instance_id}"

        data = await self.redis_client.get(key)
        if data:
            return json.loads(data)
        return None

    async def invalidate_service_cache(self, service_type: ServiceType):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Invalidate all cache entries for a service type."""
        patterns = [
            f"{self.SERVICE_INSTANCES_PREFIX}:{service_type.value}",
            f"{self.METRICS_PREFIX}:{service_type.value}:*",
            f"{self.HEALTH_PREFIX}:{service_type.value}:*",
        ]

        for pattern in patterns:
            keys = await self.redis_client.keys(pattern)
            if keys:
                await self.redis_client.delete(*keys)

    async def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        stats = {}

        for prefix in [
            self.SERVICE_INSTANCES_PREFIX,
            self.SESSION_AFFINITY_PREFIX,
            self.METRICS_PREFIX,
            self.HEALTH_PREFIX,
        ]:
            keys = await self.redis_client.keys(f"{prefix}:*")
            stats[prefix] = len(keys)

        return {"cache_key_counts": stats, "redis_info": await self.redis_client.info()}


class InfrastructureIntegrationManager:
    """
    Manages integration between load balancing and infrastructure components.

    Coordinates Redis caching, PostgreSQL connection pooling, and
    performance monitoring for optimal load balancing performance.
    """

    def __init__(
        self, redis_client: AdvancedRedisClient, db_config: ConnectionPoolConfig
    ):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """
        Initialize infrastructure integration manager.

        Args:
            redis_client: Redis client for caching
            db_config: Database connection configuration
        """
        self.redis_cache = RedisLoadBalancingCache(redis_client)
        self.db_manager = DatabaseConnectionManager(db_config)

        # Performance tracking
        self.performance_metrics: dict[str, Any] = {}
        self.last_metrics_update = time.time()

    async def initialize_database_pools(self, database_configs: dict[str, str]):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """
        Initialize database connection pools.

        Args:
            database_configs: Mapping of pool names to database URLs
        """
        for pool_name, database_url in database_configs.items():
            await self.db_manager.create_pool(pool_name, database_url)

    async def cache_service_discovery_data(
        self, service_type: ServiceType, instances: list[ServiceInstance]
    ):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Cache service discovery data for performance."""
        await self.redis_cache.cache_service_instances(service_type, instances)

        # Cache individual health statuses
        for instance in instances:
            await self.redis_cache.cache_health_status(
                service_type,
                instance.instance_id,
                instance.is_healthy,
                instance.response_time,
            )

    async def get_cached_service_data(
        self, service_type: ServiceType
    ) -> list[dict[str, Any]] | None:
        """Get cached service discovery data."""
        return await self.redis_cache.get_cached_service_instances(service_type)

    async def record_load_balancing_metrics(
        self, service_type: ServiceType, instance: ServiceInstance
    ):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record load balancing metrics to cache and database."""
        metrics = LoadBalancingMetrics(
            service_type=service_type.value,
            instance_id=instance.instance_id,
            timestamp=time.time(),
            response_time=instance.response_time or 0.0,
            success_count=instance.total_requests - instance.failed_requests,
            failure_count=instance.failed_requests,
            current_connections=instance.current_connections,
            total_requests=instance.total_requests,
        )

        # Cache metrics
        await self.redis_cache.cache_load_balancing_metrics(metrics)

        # Store in database for long-term analysis
        await self._store_metrics_in_database(metrics)

    async def _store_metrics_in_database(self, metrics: LoadBalancingMetrics):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Store metrics in PostgreSQL for analysis."""
        query = """
        INSERT INTO load_balancing_metrics
        (service_type, instance_id, timestamp, response_time, success_count,
         failure_count, current_connections, total_requests)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        """

        try:
            await self.db_manager.execute_query(
                "metrics",
                query,
                metrics.service_type,
                metrics.instance_id,
                metrics.timestamp,
                metrics.response_time,
                metrics.success_count,
                metrics.failure_count,
                metrics.current_connections,
                metrics.total_requests,
            )
        except Exception as e:
            logger.exception(f"Failed to store metrics in database: {e}")

    async def get_performance_analytics(
        self, service_type: ServiceType, time_range_hours: int = 24
    ) -> dict[str, Any]:
        """Get performance analytics from database."""
        query = """
        SELECT
            instance_id,
            AVG(response_time) as avg_response_time,
            SUM(success_count) as total_success,
            SUM(failure_count) as total_failures,
            AVG(current_connections) as avg_connections
        FROM load_balancing_metrics
        WHERE service_type = $1
        AND timestamp > $2
        GROUP BY instance_id
        """

        cutoff_time = time.time() - (time_range_hours * 3600)

        try:
            results = await self.db_manager.execute_query(
                "metrics", query, service_type.value, cutoff_time
            )

            return {
                "service_type": service_type.value,
                "time_range_hours": time_range_hours,
                "instance_analytics": [dict(row) for row in results],
            }
        except Exception as e:
            logger.exception(f"Failed to get performance analytics: {e}")
            return {}

    async def get_system_health_summary(self) -> dict[str, Any]:
        """Get overall system health summary."""
        cache_stats = await self.redis_cache.get_cache_stats()

        db_stats = {}
        for pool_name in self.db_manager.pools:
            db_stats[pool_name] = await self.db_manager.get_pool_stats(pool_name)

        return {
            "cache_statistics": cache_stats,
            "database_pools": db_stats,
            "last_update": time.time(),
        }

    async def cleanup(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Cleanup resources."""
        await self.db_manager.close_all_pools()
        logger.info("Infrastructure integration manager cleaned up")


# Global infrastructure integration manager
_infrastructure_manager: InfrastructureIntegrationManager | None = None


async def initialize_load_balancing_schema(db_manager: DatabaseConnectionManager):
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """Initialize database schema for load balancing metrics."""
    schema_queries = [
        """
        CREATE TABLE IF NOT EXISTS load_balancing_metrics (
            id SERIAL PRIMARY KEY,
            service_type VARCHAR(50) NOT NULL,
            instance_id VARCHAR(100) NOT NULL,
            timestamp DOUBLE PRECISION NOT NULL,
            response_time DOUBLE PRECISION NOT NULL,
            success_count INTEGER NOT NULL DEFAULT 0,
            failure_count INTEGER NOT NULL DEFAULT 0,
            current_connections INTEGER NOT NULL DEFAULT 0,
            total_requests INTEGER NOT NULL DEFAULT 0,
            cpu_usage DOUBLE PRECISION,
            memory_usage DOUBLE PRECISION,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_lb_metrics_service_timestamp
        ON load_balancing_metrics(service_type, timestamp);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_lb_metrics_instance_timestamp
        ON load_balancing_metrics(instance_id, timestamp);
        """,
        """
        CREATE TABLE IF NOT EXISTS service_health_history (
            id SERIAL PRIMARY KEY,
            service_type VARCHAR(50) NOT NULL,
            instance_id VARCHAR(100) NOT NULL,
            is_healthy BOOLEAN NOT NULL,
            response_time DOUBLE PRECISION,
            error_message TEXT,
            timestamp DOUBLE PRECISION NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_health_history_service_timestamp
        ON service_health_history(service_type, timestamp);
        """,
    ]

    for query in schema_queries:
        try:
            await db_manager.execute_query("metrics", query)
            logger.info("Load balancing schema initialized successfully")
        except Exception as e:
            logger.exception(f"Failed to initialize schema: {e}")


async def get_infrastructure_manager() -> InfrastructureIntegrationManager:
    """Get the global infrastructure integration manager."""
    global _infrastructure_manager

    if _infrastructure_manager is None:
        # Initialize with default configuration
        redis_client = AdvancedRedisClient("load_balancing")
        db_config = ConnectionPoolConfig()
        _infrastructure_manager = InfrastructureIntegrationManager(
            redis_client, db_config
        )

    return _infrastructure_manager
