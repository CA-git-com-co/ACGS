"""
Cache Manager for ACGS-PGP v8

Redis-based caching infrastructure with performance monitoring and cache invalidation.
"""

import hashlib
import json
import logging
import time
from datetime import datetime
from typing import Any

import redis.asyncio as redis

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Redis-based cache manager with performance monitoring and constitutional compliance.

    Provides high-performance caching for ACGS-PGP v8 components with proper
    cache invalidation, TTL management, and performance metrics.
    """

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379/0",
        max_connections: int = 100,
        default_ttl: int = 3600,
        constitutional_hash: str = "cdd01ef066bc6cf2",
    ):
        """Initialize cache manager with Redis connection."""
        self.redis_url = redis_url
        self.max_connections = max_connections
        self.default_ttl = default_ttl
        self.constitutional_hash = constitutional_hash

        # Redis connection pool
        self.redis_client: redis.Redis | None = None

        # Performance metrics
        self._cache_hits = 0
        self._cache_misses = 0
        self._cache_sets = 0
        self._cache_deletes = 0
        self._total_operations = 0

        # Cache key prefixes for organization
        self.key_prefixes = {
            "policy": "acgs:pgp:policy:",
            "execution": "acgs:pgp:execution:",
            "diagnostic": "acgs:pgp:diagnostic:",
            "lsu": "acgs:pgp:lsu:",
            "config": "acgs:pgp:config:",
            "metrics": "acgs:pgp:metrics:",
        }

        logger.info("Cache manager initialized")

    async def initialize(self) -> None:
        """Initialize Redis connection and verify connectivity."""
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=self.max_connections,
                retry_on_timeout=True,
                socket_timeout=5,
                socket_connect_timeout=5,
            )

            # Test connection
            await self.redis_client.ping()
            logger.info("✅ Redis cache connection established")

            # Set constitutional hash in cache for validation
            await self.set(
                "config:constitutional_hash",
                self.constitutional_hash,
                ttl=86400,  # 24 hours
            )

        except Exception as e:
            logger.error(f"❌ Failed to initialize Redis cache: {e}")
            raise

    def _generate_cache_key(self, prefix: str, key: str) -> str:
        """Generate standardized cache key with prefix."""
        if prefix in self.key_prefixes:
            return f"{self.key_prefixes[prefix]}{key}"
        return f"acgs:pgp:{prefix}:{key}"

    def _hash_key(self, data: str | dict[str, Any]) -> str:
        """Generate hash for complex cache keys."""
        if isinstance(data, dict):
            # Sort dict for consistent hashing
            sorted_data = json.dumps(data, sort_keys=True)
            return hashlib.sha256(sorted_data.encode()).hexdigest()[:16]
        return hashlib.sha256(str(data).encode()).hexdigest()[:16]

    async def get(self, key: str, prefix: str = "general") -> Any | None:
        """
        Get value from cache with performance tracking.

        Args:
            key: Cache key
            prefix: Key prefix for organization

        Returns:
            Cached value or None if not found
        """
        if not self.redis_client:
            return None

        cache_key = self._generate_cache_key(prefix, key)

        try:
            time.time()
            value = await self.redis_client.get(cache_key)

            self._total_operations += 1

            if value is not None:
                self._cache_hits += 1
                # Try to deserialize JSON
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    return value
            else:
                self._cache_misses += 1
                return None

        except Exception as e:
            logger.warning(f"Cache get failed for key {cache_key}: {e}")
            self._cache_misses += 1
            return None

    async def set(
        self, key: str, value: Any, ttl: int | None = None, prefix: str = "general"
    ) -> bool:
        """
        Set value in cache with TTL and performance tracking.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (optional)
            prefix: Key prefix for organization

        Returns:
            True if successful, False otherwise
        """
        if not self.redis_client:
            return False

        cache_key = self._generate_cache_key(prefix, key)
        ttl = ttl or self.default_ttl

        try:
            # Serialize value if needed
            if isinstance(value, dict | list):
                serialized_value = json.dumps(value)
            else:
                serialized_value = str(value)

            await self.redis_client.setex(cache_key, ttl, serialized_value)
            self._cache_sets += 1
            self._total_operations += 1

            return True

        except Exception as e:
            logger.warning(f"Cache set failed for key {cache_key}: {e}")
            return False

    async def delete(self, key: str, prefix: str = "general") -> bool:
        """
        Delete value from cache.

        Args:
            key: Cache key
            prefix: Key prefix for organization

        Returns:
            True if successful, False otherwise
        """
        if not self.redis_client:
            return False

        cache_key = self._generate_cache_key(prefix, key)

        try:
            result = await self.redis_client.delete(cache_key)
            self._cache_deletes += 1
            self._total_operations += 1

            return result > 0

        except Exception as e:
            logger.warning(f"Cache delete failed for key {cache_key}: {e}")
            return False

    async def exists(self, key: str, prefix: str = "general") -> bool:
        """Check if key exists in cache."""
        if not self.redis_client:
            return False

        cache_key = self._generate_cache_key(prefix, key)

        try:
            result = await self.redis_client.exists(cache_key)
            return result > 0
        except Exception as e:
            logger.warning(f"Cache exists check failed for key {cache_key}: {e}")
            return False

    async def invalidate_pattern(self, pattern: str, prefix: str = "general") -> int:
        """
        Invalidate cache keys matching a pattern.

        Args:
            pattern: Pattern to match (supports wildcards)
            prefix: Key prefix for organization

        Returns:
            Number of keys deleted
        """
        if not self.redis_client:
            return 0

        cache_pattern = self._generate_cache_key(prefix, pattern)

        try:
            keys = await self.redis_client.keys(cache_pattern)
            if keys:
                deleted = await self.redis_client.delete(*keys)
                self._cache_deletes += deleted
                self._total_operations += deleted
                return deleted
            return 0

        except Exception as e:
            logger.warning(f"Cache pattern invalidation failed for pattern {cache_pattern}: {e}")
            return 0

    async def get_ttl(self, key: str, prefix: str = "general") -> int:
        """Get remaining TTL for a cache key."""
        if not self.redis_client:
            return -1

        cache_key = self._generate_cache_key(prefix, key)

        try:
            return await self.redis_client.ttl(cache_key)
        except Exception as e:
            logger.warning(f"Cache TTL check failed for key {cache_key}: {e}")
            return -1

    async def extend_ttl(self, key: str, ttl: int, prefix: str = "general") -> bool:
        """Extend TTL for an existing cache key."""
        if not self.redis_client:
            return False

        cache_key = self._generate_cache_key(prefix, key)

        try:
            result = await self.redis_client.expire(cache_key, ttl)
            return result
        except Exception as e:
            logger.warning(f"Cache TTL extension failed for key {cache_key}: {e}")
            return False

    def get_cache_hit_rate(self) -> float:
        """Calculate cache hit rate percentage."""
        total_reads = self._cache_hits + self._cache_misses
        if total_reads == 0:
            return 0.0
        return (self._cache_hits / total_reads) * 100.0

    async def get_metrics(self) -> dict[str, Any]:
        """Get comprehensive cache performance metrics."""
        hit_rate = self.get_cache_hit_rate()

        # Get Redis info
        redis_info = {}
        if self.redis_client:
            try:
                info = await self.redis_client.info()
                redis_info = {
                    "used_memory": info.get("used_memory", 0),
                    "used_memory_human": info.get("used_memory_human", "0B"),
                    "connected_clients": info.get("connected_clients", 0),
                    "total_commands_processed": info.get("total_commands_processed", 0),
                    "keyspace_hits": info.get("keyspace_hits", 0),
                    "keyspace_misses": info.get("keyspace_misses", 0),
                }
            except Exception as e:
                logger.warning(f"Failed to get Redis info: {e}")

        return {
            "cache_performance": {
                "hit_rate_percent": hit_rate,
                "cache_hits": self._cache_hits,
                "cache_misses": self._cache_misses,
                "cache_sets": self._cache_sets,
                "cache_deletes": self._cache_deletes,
                "total_operations": self._total_operations,
            },
            "redis_info": redis_info,
            "constitutional_hash": self.constitutional_hash,
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def health_check(self) -> dict[str, Any]:
        """Perform cache health check."""
        health_status = {
            "status": "healthy",
            "constitutional_hash": self.constitutional_hash,
            "timestamp": datetime.utcnow().isoformat(),
        }

        try:
            if self.redis_client:
                # Test basic operations
                test_key = "health_check_test"
                test_value = "test_value"

                await self.set(test_key, test_value, ttl=60)
                retrieved_value = await self.get(test_key)
                await self.delete(test_key)

                if retrieved_value == test_value:
                    health_status["cache_operations"] = "healthy"
                    health_status["hit_rate_percent"] = self.get_cache_hit_rate()
                else:
                    health_status["status"] = "unhealthy"
                    health_status["cache_operations"] = "failed"
            else:
                health_status["status"] = "unhealthy"
                health_status["error"] = "Redis client not initialized"

        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)
            logger.error(f"Cache health check failed: {e}")

        return health_status

    async def close(self) -> None:
        """Close Redis connection and clean up resources."""
        try:
            if self.redis_client:
                await self.redis_client.close()
                logger.info("Redis cache connection closed")
        except Exception as e:
            logger.warning(f"Error closing Redis connection: {e}")


# Global cache manager instance
_cache_manager: CacheManager | None = None


def initialize_cache_manager(
    redis_url: str | None = None,
    max_connections: int = 100,
    default_ttl: int = 3600,
    constitutional_hash: str = "cdd01ef066bc6cf2",
) -> CacheManager:
    """Initialize global cache manager."""
    global _cache_manager

    if redis_url is None:
        import os

        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    _cache_manager = CacheManager(
        redis_url=redis_url,
        max_connections=max_connections,
        default_ttl=default_ttl,
        constitutional_hash=constitutional_hash,
    )

    return _cache_manager


def get_cache_manager() -> CacheManager:
    """Get global cache manager instance."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = initialize_cache_manager()
    return _cache_manager
