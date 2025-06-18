"""
Constitutional Cache for ACGS-1 Performance Optimization

Implements Redis-based caching for constitutional validation results to improve
performance across all services with <500ms response times.
"""

import hashlib
import json
import logging
import time
from typing import Any

import redis.asyncio as redis

logger = logging.getLogger(__name__)


class ConstitutionalCache:
    """
    Redis-based caching for constitutional validation results.

    Provides high-performance caching with automatic TTL management
    and cache invalidation for constitutional governance operations.
    """

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        """
        Initialize constitutional cache with Redis connection.

        Args:
            redis_url: Redis connection URL
        """
        self.redis_url = redis_url
        self.redis_client = None
        self.cache_ttl = 300  # 5 minutes default TTL
        self.cache_prefix = "acgs:constitutional"

    async def initialize(self):
        """Initialize Redis connection."""
        try:
            self.redis_client = redis.from_url(self.redis_url)
            # Test connection
            await self.redis_client.ping()
            logger.info("Constitutional cache initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize constitutional cache: {e}")
            self.redis_client = None

    async def get_validation_result(self, cache_key: str) -> dict[str, Any] | None:
        """
        Get cached constitutional validation result.

        Args:
            cache_key: Unique cache key for the validation

        Returns:
            Cached validation result or None if not found
        """
        if not self.redis_client:
            return None

        try:
            full_key = f"{self.cache_prefix}:validation:{cache_key}"
            cached_data = await self.redis_client.get(full_key)

            if cached_data:
                result = json.loads(cached_data)
                logger.debug(f"Cache hit for key: {cache_key}")
                return result

            logger.debug(f"Cache miss for key: {cache_key}")
            return None

        except Exception as e:
            logger.warning(f"Cache get failed for key {cache_key}: {e}")
            return None

    async def set_validation_result(
        self, cache_key: str, result: dict[str, Any], ttl: int | None = None
    ):
        """
        Cache constitutional validation result.

        Args:
            cache_key: Unique cache key for the validation
            result: Validation result to cache
            ttl: Time to live in seconds (uses default if None)
        """
        if not self.redis_client:
            return

        try:
            full_key = f"{self.cache_prefix}:validation:{cache_key}"
            cache_ttl = ttl or self.cache_ttl

            # Add cache metadata
            cached_result = {**result, "cached_at": time.time(), "cache_ttl": cache_ttl}

            await self.redis_client.setex(
                full_key, cache_ttl, json.dumps(cached_result, default=str)
            )

            logger.debug(f"Cached validation result for key: {cache_key}")

        except Exception as e:
            logger.warning(f"Cache set failed for key {cache_key}: {e}")

    def generate_cache_key(self, operation_type: str, data: dict[str, Any]) -> str:
        """
        Generate cache key for constitutional validation.

        Args:
            operation_type: Type of constitutional operation
            data: Data to include in cache key generation

        Returns:
            Unique cache key
        """
        # Create deterministic key from operation and data
        key_data = {
            "operation_type": operation_type,
            "constitutional_hash": data.get("constitutional_hash"),
            "validation_level": data.get("validation_level", "standard"),
            "policy_id": data.get("policy_id"),
            "content_hash": self._hash_content(data),
        }

        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_string.encode()).hexdigest()[:32]

    def _hash_content(self, data: dict[str, Any]) -> str:
        """Generate hash of content for cache key."""
        # Extract relevant content for hashing
        content_items = []

        for key in ["title", "description", "content", "constitutional_principles"]:
            if key in data:
                content_items.append(f"{key}:{data[key]}")

        content_string = "|".join(content_items)
        return hashlib.sha256(content_string.encode()).hexdigest()[:32]

    async def invalidate_cache(self, pattern: str = None):
        """
        Invalidate cached validation results.

        Args:
            pattern: Pattern to match keys for invalidation (None = all)
        """
        if not self.redis_client:
            return

        try:
            if pattern:
                full_pattern = f"{self.cache_prefix}:validation:{pattern}"
            else:
                full_pattern = f"{self.cache_prefix}:validation:*"

            keys = await self.redis_client.keys(full_pattern)

            if keys:
                await self.redis_client.delete(*keys)
                logger.info(
                    f"Invalidated {len(keys)} cache entries matching pattern: {pattern or 'all'}"
                )

        except Exception as e:
            logger.error(f"Cache invalidation failed: {e}")

    async def get_cache_stats(self) -> dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Cache statistics including hit rate and size
        """
        if not self.redis_client:
            return {"status": "unavailable"}

        try:
            # Get all validation cache keys
            keys = await self.redis_client.keys(f"{self.cache_prefix}:validation:*")

            # Get Redis info
            info = await self.redis_client.info()

            stats = {
                "status": "active",
                "total_keys": len(keys),
                "redis_memory_used": info.get("used_memory_human", "unknown"),
                "redis_connected_clients": info.get("connected_clients", 0),
                "cache_prefix": self.cache_prefix,
                "default_ttl": self.cache_ttl,
            }

            return stats

        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {"status": "error", "error": str(e)}

    async def close(self):
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Constitutional cache connection closed")


# Global cache instance
_constitutional_cache = None


async def get_constitutional_cache() -> ConstitutionalCache:
    """Get global constitutional cache instance."""
    global _constitutional_cache

    if _constitutional_cache is None:
        _constitutional_cache = ConstitutionalCache()
        await _constitutional_cache.initialize()

    return _constitutional_cache


async def cache_constitutional_validation(
    operation_type: str,
    data: dict[str, Any],
    result: dict[str, Any],
    ttl: int | None = None,
) -> str:
    """
    Cache constitutional validation result.

    Args:
        operation_type: Type of constitutional operation
        data: Input data for validation
        result: Validation result to cache
        ttl: Cache TTL in seconds

    Returns:
        Cache key used for storage
    """
    cache = await get_constitutional_cache()
    cache_key = cache.generate_cache_key(operation_type, data)
    await cache.set_validation_result(cache_key, result, ttl)
    return cache_key


async def get_cached_constitutional_validation(
    operation_type: str, data: dict[str, Any]
) -> dict[str, Any] | None:
    """
    Get cached constitutional validation result.

    Args:
        operation_type: Type of constitutional operation
        data: Input data for validation

    Returns:
        Cached validation result or None
    """
    cache = await get_constitutional_cache()
    cache_key = cache.generate_cache_key(operation_type, data)
    return await cache.get_validation_result(cache_key)
