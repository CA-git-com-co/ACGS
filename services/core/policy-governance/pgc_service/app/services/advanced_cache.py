"""
Advanced caching implementation for PGC Service

Provides multi-tier caching with Redis backend and in-memory fallback.
"""

import json
import logging
import time
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Cache entry with metadata."""

    value: Any
    timestamp: float
    ttl: float | None = None
    access_count: int = 0

    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        if self.ttl is None:
            return False
        return time.time() - self.timestamp > self.ttl


class MultiTierCache:
    """Multi-tier cache with Redis and in-memory layers."""

    def __init__(self, redis_client=None, default_ttl: int = 300):
        self.redis_client = redis_client
        self.default_ttl = default_ttl
        self.memory_cache: dict[str, CacheEntry] = {}
        self.max_memory_entries = 1000

    async def get(self, key: str) -> Any | None:
        """Get value from cache (memory first, then Redis)."""
        try:
            # Check memory cache first
            if key in self.memory_cache:
                entry = self.memory_cache[key]
                if not entry.is_expired():
                    entry.access_count += 1
                    return entry.value
                else:
                    del self.memory_cache[key]

            # Check Redis cache
            if self.redis_client:
                try:
                    value = await self.redis_client.get(key)
                    if value:
                        decoded_value = json.loads(value)
                        # Store in memory cache for faster access
                        self.memory_cache[key] = CacheEntry(
                            value=decoded_value,
                            timestamp=time.time(),
                            ttl=self.default_ttl,
                        )
                        return decoded_value
                except Exception as e:
                    logger.warning(f"Redis cache get error: {e}")

            return None

        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """Set value in cache (both memory and Redis)."""
        try:
            cache_ttl = ttl or self.default_ttl

            # Store in memory cache
            self.memory_cache[key] = CacheEntry(
                value=value, timestamp=time.time(), ttl=cache_ttl
            )

            # Evict old entries if memory cache is full
            if len(self.memory_cache) > self.max_memory_entries:
                self._evict_memory_cache()

            # Store in Redis cache
            if self.redis_client:
                try:
                    serialized_value = json.dumps(value)
                    await self.redis_client.setex(key, cache_ttl, serialized_value)
                except Exception as e:
                    logger.warning(f"Redis cache set error: {e}")

            return True

        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        try:
            # Remove from memory cache
            if key in self.memory_cache:
                del self.memory_cache[key]

            # Remove from Redis cache
            if self.redis_client:
                try:
                    await self.redis_client.delete(key)
                except Exception as e:
                    logger.warning(f"Redis cache delete error: {e}")

            return True

        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False

    async def clear(self) -> bool:
        """Clear all cache entries."""
        try:
            # Clear memory cache
            self.memory_cache.clear()

            # Clear Redis cache (if available)
            if self.redis_client:
                try:
                    await self.redis_client.flushdb()
                except Exception as e:
                    logger.warning(f"Redis cache clear error: {e}")

            return True

        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return False

    def _evict_memory_cache(self):
        """Evict least recently used entries from memory cache."""
        if len(self.memory_cache) <= self.max_memory_entries:
            return

        # Sort by access count and timestamp
        sorted_entries = sorted(
            self.memory_cache.items(), key=lambda x: (x[1].access_count, x[1].timestamp)
        )

        # Remove oldest 20% of entries
        entries_to_remove = len(sorted_entries) // 5
        for key, _ in sorted_entries[:entries_to_remove]:
            del self.memory_cache[key]

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        memory_entries = len(self.memory_cache)
        expired_entries = sum(
            1 for entry in self.memory_cache.values() if entry.is_expired()
        )

        return {
            "memory_entries": memory_entries,
            "expired_entries": expired_entries,
            "max_memory_entries": self.max_memory_entries,
            "redis_available": self.redis_client is not None,
        }


# Global cache instance
_cache_instance: MultiTierCache | None = None


def get_cache() -> MultiTierCache:
    """Get global cache instance."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = MultiTierCache()
    return _cache_instance


def initialize_cache(redis_client=None, default_ttl: int = 300) -> MultiTierCache:
    """Initialize global cache instance."""
    global _cache_instance
    _cache_instance = MultiTierCache(redis_client=redis_client, default_ttl=default_ttl)
    return _cache_instance
