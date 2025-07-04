"""
Enterprise Redis Cluster for ACGS-1 Distributed Caching

Provides high-performance distributed caching with:
- Redis cluster support
- Automatic failover
- Consistent hashing
- Cache invalidation patterns
- Performance monitoring
- Circuit breaker protection
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import redis.asyncio as redis
from redis.asyncio.cluster import RedisCluster

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


logger = logging.getLogger(__name__)


class CacheStrategy(Enum):
    """Cache strategies."""

    WRITE_THROUGH = "write_through"
    WRITE_BEHIND = "write_behind"
    WRITE_AROUND = "write_around"
    READ_THROUGH = "read_through"


@dataclass
class RedisClusterConfig:
    """Redis cluster configuration."""

    # Cluster nodes
    nodes: List[Dict[str, Union[str, int]]] = None

    # Connection settings
    password: Optional[str] = None
    username: Optional[str] = None
    ssl: bool = False
    ssl_cert_reqs: str = "required"

    # Pool settings
    max_connections: int = 100
    max_connections_per_node: int = 50
    retry_on_timeout: bool = True
    retry_on_cluster_down: bool = True

    # Performance settings
    socket_timeout: float = 5.0
    socket_connect_timeout: float = 5.0
    socket_keepalive: bool = True
    socket_keepalive_options: Dict[str, int] = None

    # Cache settings
    default_ttl: int = 3600  # 1 hour
    key_prefix: str = "acgs:"
    serialization_format: str = "json"  # json, pickle, msgpack

    # Circuit breaker settings
    failure_threshold: int = 5
    recovery_timeout: int = 60

    def __post_init__(self):
        if self.nodes is None:
            self.nodes = [
                {"host": "localhost", "port": 7000},
                {"host": "localhost", "port": 7001},
                {"host": "localhost", "port": 7002},
            ]

        if self.socket_keepalive_options is None:
            self.socket_keepalive_options = {
                "TCP_KEEPIDLE": 1,
                "TCP_KEEPINTVL": 3,
                "TCP_KEEPCNT": 5,
            }


class CacheCircuitBreaker:
    """Circuit breaker for cache operations."""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.is_open = False

    def record_success(self):
        """Record successful operation."""
        self.failure_count = 0
        self.is_open = False

    def record_failure(self):
        """Record failed operation."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.is_open = True
            logger.warning(
                f"Cache circuit breaker opened after {self.failure_count} failures"
            )

    def can_execute(self) -> bool:
        """Check if operations can be executed."""
        if not self.is_open:
            return True

        if time.time() - self.last_failure_time > self.recovery_timeout:
            self.is_open = False
            self.failure_count = 0
            logger.info("Cache circuit breaker closed - entering recovery")
            return True

        return False


class RedisClusterManager:
    """Enterprise Redis cluster manager."""

    def __init__(self, config: RedisClusterConfig):
        self.config = config
        self.cluster: Optional[RedisCluster] = None
        self.circuit_breaker = CacheCircuitBreaker(
            config.failure_threshold, config.recovery_timeout
        )
        self.metrics = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "errors": 0,
            "avg_response_time": 0.0,
            "total_operations": 0,
        }
        self.health_check_task: Optional[asyncio.Task] = None

    async def initialize(self):
        """Initialize Redis cluster connection."""
        try:
            startup_nodes = [
                redis.ConnectionPool.from_url(f"redis://{node['host']}:{node['port']}")
                for node in self.config.nodes
            ]

            self.cluster = RedisCluster(
                startup_nodes=self.config.nodes,
                password=self.config.password,
                username=self.config.username,
                ssl=self.config.ssl,
                ssl_cert_reqs=self.config.ssl_cert_reqs,
                max_connections=self.config.max_connections,
                max_connections_per_node=self.config.max_connections_per_node,
                retry_on_timeout=self.config.retry_on_timeout,
                retry_on_cluster_down=self.config.retry_on_cluster_down,
                socket_timeout=self.config.socket_timeout,
                socket_connect_timeout=self.config.socket_connect_timeout,
                socket_keepalive=self.config.socket_keepalive,
                socket_keepalive_options=self.config.socket_keepalive_options,
                decode_responses=True,
            )

            # Test connection
            await self.cluster.ping()

            # Start health check task
            self.health_check_task = asyncio.create_task(self._health_check_loop())

            logger.info("Redis cluster initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Redis cluster: {e}")
            raise

    def _build_key(self, key: str) -> str:
        """Build cache key with prefix."""
        return f"{self.config.key_prefix}{key}"

    def _serialize_value(self, value: Any) -> str:
        """Serialize value for storage."""
        if self.config.serialization_format == "json":
            return json.dumps(value, default=str)
        else:
            # For now, default to JSON
            return json.dumps(value, default=str)

    def _deserialize_value(self, value: str) -> Any:
        """Deserialize value from storage."""
        if self.config.serialization_format == "json":
            return json.loads(value)
        else:
            # For now, default to JSON
            return json.loads(value)

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.circuit_breaker.can_execute():
            logger.warning("Cache circuit breaker is open, skipping get operation")
            return None

        start_time = time.time()

        try:
            cache_key = self._build_key(key)
            value = await self.cluster.get(cache_key)

            if value is not None:
                self.metrics["hits"] += 1
                result = self._deserialize_value(value)
            else:
                self.metrics["misses"] += 1
                result = None

            self.circuit_breaker.record_success()
            self._update_metrics(time.time() - start_time)

            return result

        except Exception as e:
            self.circuit_breaker.record_failure()
            self.metrics["errors"] += 1
            logger.error(f"Cache get error for key {key}: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        if not self.circuit_breaker.can_execute():
            logger.warning("Cache circuit breaker is open, skipping set operation")
            return False

        start_time = time.time()

        try:
            cache_key = self._build_key(key)
            serialized_value = self._serialize_value(value)
            ttl = ttl or self.config.default_ttl

            await self.cluster.setex(cache_key, ttl, serialized_value)

            self.metrics["sets"] += 1
            self.circuit_breaker.record_success()
            self._update_metrics(time.time() - start_time)

            return True

        except Exception as e:
            self.circuit_breaker.record_failure()
            self.metrics["errors"] += 1
            logger.error(f"Cache set error for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if not self.circuit_breaker.can_execute():
            logger.warning("Cache circuit breaker is open, skipping delete operation")
            return False

        start_time = time.time()

        try:
            cache_key = self._build_key(key)
            result = await self.cluster.delete(cache_key)

            self.metrics["deletes"] += 1
            self.circuit_breaker.record_success()
            self._update_metrics(time.time() - start_time)

            return result > 0

        except Exception as e:
            self.circuit_breaker.record_failure()
            self.metrics["errors"] += 1
            logger.error(f"Cache delete error for key {key}: {e}")
            return False

    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate cache keys matching pattern."""
        if not self.circuit_breaker.can_execute():
            logger.warning(
                "Cache circuit breaker is open, skipping invalidate operation"
            )
            return 0

        try:
            cache_pattern = self._build_key(pattern)
            keys = []

            # Get all keys matching pattern from all nodes
            for node in self.cluster.get_nodes():
                node_keys = await node.redis_connection.keys(cache_pattern)
                keys.extend(node_keys)

            if keys:
                deleted = await self.cluster.delete(*keys)
                logger.info(
                    f"Invalidated {deleted} cache keys matching pattern: {pattern}"
                )
                return deleted

            return 0

        except Exception as e:
            self.circuit_breaker.record_failure()
            self.metrics["errors"] += 1
            logger.error(f"Cache invalidate pattern error for {pattern}: {e}")
            return 0

    async def get_cluster_info(self) -> Dict[str, Any]:
        """Get Redis cluster information."""
        try:
            cluster_info = await self.cluster.cluster_info()
            cluster_nodes = await self.cluster.cluster_nodes()

            return {
                "cluster_info": cluster_info,
                "cluster_nodes": cluster_nodes,
                "metrics": self.metrics.copy(),
                "circuit_breaker_open": self.circuit_breaker.is_open,
                "hit_rate": (
                    self.metrics["hits"]
                    / (self.metrics["hits"] + self.metrics["misses"])
                    if (self.metrics["hits"] + self.metrics["misses"]) > 0
                    else 0
                ),
            }

        except Exception as e:
            logger.error(f"Error getting cluster info: {e}")
            return {"error": str(e)}

    def _update_metrics(self, response_time: float):
        """Update performance metrics."""
        self.metrics["total_operations"] += 1
        self.metrics["avg_response_time"] = (
            self.metrics["avg_response_time"] * (self.metrics["total_operations"] - 1)
            + response_time
        ) / self.metrics["total_operations"]

    async def _health_check_loop(self):
        """Periodic health check for cluster."""
        while True:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                await self.cluster.ping()
                self.circuit_breaker.record_success()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.circuit_breaker.record_failure()
                logger.warning(f"Redis cluster health check failed: {e}")

    async def close(self):
        """Close cluster connections."""
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass

        if self.cluster:
            await self.cluster.close()

        logger.info("Redis cluster connections closed")


# Global cache manager instance
_cache_manager: Optional[RedisClusterManager] = None


async def initialize_cache_manager(config: RedisClusterConfig) -> RedisClusterManager:
    """Initialize global cache manager."""
    global _cache_manager
    _cache_manager = RedisClusterManager(config)
    await _cache_manager.initialize()
    return _cache_manager


def get_cache_manager() -> RedisClusterManager:
    """Get global cache manager instance."""
    if _cache_manager is None:
        raise RuntimeError(
            "Cache manager not initialized. Call initialize_cache_manager() first."
        )
    return _cache_manager


async def close_cache_manager():
    """Close global cache manager."""
    global _cache_manager
    if _cache_manager:
        await _cache_manager.close()
        _cache_manager = None
