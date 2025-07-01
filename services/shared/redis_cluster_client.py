"""
ACGS-1 Redis Cluster Client
Phase 2 - Enterprise Scalability & Performance

High-performance Redis cluster client with connection pooling,
failover support, and caching patterns for >1000 concurrent users.
"""

import asyncio
import json
import logging
import pickle
from dataclasses import dataclass
from typing import Any

from redis.asyncio.cluster import RedisCluster
from redis.exceptions import (
    ClusterDownError,
    ConnectionError,
    TimeoutError,
)

logger = logging.getLogger(__name__)


@dataclass
class CacheConfig:
    """Configuration for Redis caching behavior."""

    # Default TTL settings (in seconds)
    default_ttl: int = 3600  # 1 hour
    short_ttl: int = 300  # 5 minutes
    long_ttl: int = 86400  # 24 hours

    # Key prefixes for different data types
    session_prefix: str = "acgs:session"
    policy_prefix: str = "acgs:policy"
    user_prefix: str = "acgs:user"
    temp_prefix: str = "acgs:temp"

    # Serialization settings
    use_compression: bool = True
    compression_threshold: int = 1024  # Compress data larger than 1KB

    # Performance settings
    max_connections: int = 100
    connection_timeout: float = 5.0
    socket_timeout: float = 5.0
    retry_attempts: int = 3
    retry_delay: float = 0.1


class RedisClusterClient:
    """High-performance Redis cluster client for ACGS services."""

    def __init__(
        self,
        service_name: str,
        cluster_nodes: list[dict[str, str | int]] = None,
        config: CacheConfig = None,
    ):
        self.service_name = service_name
        self.config = config or CacheConfig()

        # Default cluster nodes
        self.cluster_nodes = cluster_nodes or [
            {"host": "localhost", "port": 7001},
            {"host": "localhost", "port": 7002},
            {"host": "localhost", "port": 7003},
        ]

        self._cluster = None
        self._connection_pool = None
        self._is_connected = False

        # Performance metrics
        self.metrics = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "errors": 0,
            "total_operations": 0,
        }

        logger.info(f"Redis cluster client initialized for {service_name}")

    async def connect(self):
        """Establish connection to Redis cluster."""
        if self._is_connected:
            return

        try:
            # Create Redis cluster connection
            self._cluster = RedisCluster(
                startup_nodes=self.cluster_nodes,
                decode_responses=False,  # We handle encoding/decoding manually
                skip_full_coverage_check=True,
                max_connections=self.config.max_connections,
                socket_timeout=self.config.socket_timeout,
                socket_connect_timeout=self.config.connection_timeout,
                retry_on_timeout=True,
                retry_on_error=[ConnectionError, TimeoutError],
                health_check_interval=30,
            )

            # Test connection
            await self._cluster.ping()
            self._is_connected = True

            logger.info(f"Connected to Redis cluster for {self.service_name}")

        except Exception as e:
            logger.error(f"Failed to connect to Redis cluster: {e}")
            raise

    async def disconnect(self):
        """Close Redis cluster connection."""
        if self._cluster:
            await self._cluster.close()
            self._is_connected = False
            logger.info(f"Disconnected from Redis cluster for {self.service_name}")

    def _generate_key(self, key: str, prefix: str = None) -> str:
        """Generate a properly prefixed cache key."""
        if prefix:
            return f"{prefix}:{self.service_name}:{key}"
        return f"{self.service_name}:{key}"

    def _serialize_value(self, value: Any) -> bytes:
        """Serialize value for storage in Redis."""
        try:
            # Use pickle for Python objects, JSON for simple types
            if isinstance(value, (str, int, float, bool, type(None))):
                serialized = json.dumps(value).encode("utf-8")
            else:
                serialized = pickle.dumps(value)

            # Compress if enabled and data is large enough
            if (
                self.config.use_compression
                and len(serialized) > self.config.compression_threshold
            ):
                import gzip

                serialized = gzip.compress(serialized)
                # Add compression marker
                serialized = b"GZIP:" + serialized

            return serialized

        except Exception as e:
            logger.error(f"Failed to serialize value: {e}")
            raise

    def _deserialize_value(self, data: bytes) -> Any:
        """Deserialize value from Redis storage."""
        try:
            # Check for compression marker
            if data.startswith(b"GZIP:"):
                import gzip

                data = gzip.decompress(data[5:])  # Remove 'GZIP:' prefix

            # Try JSON first (faster for simple types)
            try:
                return json.loads(data.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                # Fall back to pickle
                return pickle.loads(data)

        except Exception as e:
            logger.error(f"Failed to deserialize value: {e}")
            raise

    async def _execute_with_retry(self, operation, *args, **kwargs):
        """Execute Redis operation with retry logic."""
        last_exception = None

        for attempt in range(self.config.retry_attempts):
            try:
                if not self._is_connected:
                    await self.connect()

                result = await operation(*args, **kwargs)
                self.metrics["total_operations"] += 1
                return result

            except (ConnectionError, TimeoutError, ClusterDownError) as e:
                last_exception = e
                self.metrics["errors"] += 1

                if attempt < self.config.retry_attempts - 1:
                    await asyncio.sleep(self.config.retry_delay * (2**attempt))
                    # Try to reconnect
                    try:
                        await self.disconnect()
                        await self.connect()
                    except:
                        pass
                else:
                    logger.error(
                        f"Redis operation failed after {self.config.retry_attempts} attempts: {e}"
                    )
                    raise e

            except Exception as e:
                self.metrics["errors"] += 1
                logger.error(f"Unexpected Redis error: {e}")
                raise e

        if last_exception:
            raise last_exception

    async def get(self, key: str, prefix: str = None) -> Any | None:
        """Get value from cache."""
        cache_key = self._generate_key(key, prefix)

        try:
            data = await self._execute_with_retry(self._cluster.get, cache_key)

            if data is None:
                self.metrics["misses"] += 1
                return None

            self.metrics["hits"] += 1
            return self._deserialize_value(data)

        except Exception as e:
            logger.error(f"Failed to get key {cache_key}: {e}")
            self.metrics["misses"] += 1
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int = None,
        prefix: str = None,
        nx: bool = False,
        xx: bool = False,
    ) -> bool:
        """Set value in cache."""
        cache_key = self._generate_key(key, prefix)
        ttl = ttl or self.config.default_ttl

        try:
            serialized_value = self._serialize_value(value)

            # Build Redis SET command arguments
            kwargs = {"ex": ttl}  # Set expiration time
            if nx:
                kwargs["nx"] = True  # Only set if key doesn't exist
            if xx:
                kwargs["xx"] = True  # Only set if key exists

            result = await self._execute_with_retry(
                self._cluster.set, cache_key, serialized_value, **kwargs
            )

            if result:
                self.metrics["sets"] += 1
                return True
            return False

        except Exception as e:
            logger.error(f"Failed to set key {cache_key}: {e}")
            return False

    async def delete(self, key: str, prefix: str = None) -> bool:
        """Delete key from cache."""
        cache_key = self._generate_key(key, prefix)

        try:
            result = await self._execute_with_retry(self._cluster.delete, cache_key)

            if result > 0:
                self.metrics["deletes"] += 1
                return True
            return False

        except Exception as e:
            logger.error(f"Failed to delete key {cache_key}: {e}")
            return False

    async def exists(self, key: str, prefix: str = None) -> bool:
        """Check if key exists in cache."""
        cache_key = self._generate_key(key, prefix)

        try:
            result = await self._execute_with_retry(self._cluster.exists, cache_key)
            return result > 0

        except Exception as e:
            logger.error(f"Failed to check existence of key {cache_key}: {e}")
            return False

    async def expire(self, key: str, ttl: int, prefix: str = None) -> bool:
        """Set expiration time for key."""
        cache_key = self._generate_key(key, prefix)

        try:
            result = await self._execute_with_retry(
                self._cluster.expire, cache_key, ttl
            )
            return result

        except Exception as e:
            logger.error(f"Failed to set expiration for key {cache_key}: {e}")
            return False

    async def increment(
        self, key: str, amount: int = 1, prefix: str = None
    ) -> int | None:
        """Increment numeric value."""
        cache_key = self._generate_key(key, prefix)

        try:
            result = await self._execute_with_retry(
                self._cluster.incrby, cache_key, amount
            )
            return result

        except Exception as e:
            logger.error(f"Failed to increment key {cache_key}: {e}")
            return None

    async def hash_set(
        self, key: str, field: str, value: Any, prefix: str = None
    ) -> bool:
        """Set field in hash."""
        cache_key = self._generate_key(key, prefix)

        try:
            serialized_value = self._serialize_value(value)
            result = await self._execute_with_retry(
                self._cluster.hset, cache_key, field, serialized_value
            )
            return result

        except Exception as e:
            logger.error(f"Failed to set hash field {cache_key}:{field}: {e}")
            return False

    async def hash_get(self, key: str, field: str, prefix: str = None) -> Any | None:
        """Get field from hash."""
        cache_key = self._generate_key(key, prefix)

        try:
            data = await self._execute_with_retry(self._cluster.hget, cache_key, field)

            if data is None:
                return None

            return self._deserialize_value(data)

        except Exception as e:
            logger.error(f"Failed to get hash field {cache_key}:{field}: {e}")
            return None

    async def hash_delete(self, key: str, field: str, prefix: str = None) -> bool:
        """Delete field from hash."""
        cache_key = self._generate_key(key, prefix)

        try:
            result = await self._execute_with_retry(
                self._cluster.hdel, cache_key, field
            )
            return result > 0

        except Exception as e:
            logger.error(f"Failed to delete hash field {cache_key}:{field}: {e}")
            return False

    async def list_push(
        self, key: str, value: Any, prefix: str = None, left: bool = True
    ) -> int:
        """Push value to list."""
        cache_key = self._generate_key(key, prefix)

        try:
            serialized_value = self._serialize_value(value)

            if left:
                result = await self._execute_with_retry(
                    self._cluster.lpush, cache_key, serialized_value
                )
            else:
                result = await self._execute_with_retry(
                    self._cluster.rpush, cache_key, serialized_value
                )

            return result

        except Exception as e:
            logger.error(f"Failed to push to list {cache_key}: {e}")
            return 0

    async def list_pop(
        self, key: str, prefix: str = None, left: bool = True
    ) -> Any | None:
        """Pop value from list."""
        cache_key = self._generate_key(key, prefix)

        try:
            if left:
                data = await self._execute_with_retry(self._cluster.lpop, cache_key)
            else:
                data = await self._execute_with_retry(self._cluster.rpop, cache_key)

            if data is None:
                return None

            return self._deserialize_value(data)

        except Exception as e:
            logger.error(f"Failed to pop from list {cache_key}: {e}")
            return None

    async def get_cluster_info(self) -> dict[str, Any]:
        """Get cluster information and health status."""
        try:
            if not self._is_connected:
                await self.connect()

            # Get cluster info
            cluster_info = await self._cluster.cluster_info()
            cluster_nodes = await self._cluster.cluster_nodes()

            # Calculate hit rate
            total_cache_ops = self.metrics["hits"] + self.metrics["misses"]
            hit_rate = (
                (self.metrics["hits"] / total_cache_ops * 100)
                if total_cache_ops > 0
                else 0
            )

            return {
                "service": self.service_name,
                "cluster_state": cluster_info.get("cluster_state", "unknown"),
                "cluster_slots_assigned": cluster_info.get("cluster_slots_assigned", 0),
                "cluster_known_nodes": cluster_info.get("cluster_known_nodes", 0),
                "cluster_size": cluster_info.get("cluster_size", 0),
                "nodes": len(cluster_nodes),
                "metrics": self.metrics,
                "hit_rate": f"{hit_rate:.2f}%",
                "is_connected": self._is_connected,
            }

        except Exception as e:
            logger.error(f"Failed to get cluster info: {e}")
            return {
                "service": self.service_name,
                "error": str(e),
                "is_connected": self._is_connected,
                "metrics": self.metrics,
            }


# Global Redis clients for each service
_redis_clients: dict[str, RedisClusterClient] = {}


async def get_redis_client(service_name: str) -> RedisClusterClient:
    """Get or create Redis cluster client for a service."""
    if service_name not in _redis_clients:
        client = RedisClusterClient(service_name)
        await client.connect()
        _redis_clients[service_name] = client

    return _redis_clients[service_name]


async def close_all_redis_clients():
    """Close all Redis clients."""
    for client in _redis_clients.values():
        await client.disconnect()

    _redis_clients.clear()
    logger.info("All Redis clients closed")
