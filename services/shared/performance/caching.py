"""
Advanced Caching System for ACGS
Constitutional Hash: cdd01ef066bc6cf2

Multi-level caching with Redis, memory, and intelligent invalidation strategies.
"""

import asyncio
import hashlib
import json
import logging
import pickle
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union

import aioredis

from ..resilience.circuit_breaker import CircuitBreakerConfig, get_circuit_breaker

logger = logging.getLogger(__name__)
T = TypeVar("T")


class CacheStrategy(str, Enum):
    """Cache strategies for different use cases."""

    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"  # Time To Live
    WRITE_THROUGH = "write_through"  # Write to cache and storage
    WRITE_BACK = "write_back"  # Write to cache, async to storage
    WRITE_AROUND = "write_around"  # Write to storage, invalidate cache


@dataclass
class CacheConfig:
    """Configuration for cache behavior."""

    default_ttl: int = 300  # 5 minutes default TTL
    max_size: int = 10000  # Maximum cache entries
    strategy: CacheStrategy = CacheStrategy.LRU
    enable_compression: bool = False
    enable_encryption: bool = False
    batch_size: int = 100  # For batch operations
    circuit_breaker_enabled: bool = True


class CacheKey:
    """Utility for generating consistent cache keys."""

    @staticmethod
    def generate(prefix: str, *args, tenant_id: str = None, **kwargs) -> str:
        """Generate a consistent cache key."""
        key_parts = [prefix]

        if tenant_id:
            key_parts.append(f"tenant:{tenant_id}")

        # Add positional arguments
        for arg in args:
            if isinstance(arg, (str, int, float)):
                key_parts.append(str(arg))
            else:
                # Hash complex objects
                key_parts.append(CacheKey._hash_object(arg))

        # Add keyword arguments (sorted for consistency)
        for k, v in sorted(kwargs.items()):
            if isinstance(v, (str, int, float)):
                key_parts.append(f"{k}:{v}")
            else:
                key_parts.append(f"{k}:{CacheKey._hash_object(v)}")

        return ":".join(key_parts)

    @staticmethod
    def _hash_object(obj: Any) -> str:
        """Generate hash for complex objects."""
        try:
            if hasattr(obj, "to_dict"):
                obj_str = json.dumps(obj.to_dict(), sort_keys=True)
            elif hasattr(obj, "__dict__"):
                obj_str = json.dumps(obj.__dict__, sort_keys=True, default=str)
            else:
                obj_str = str(obj)

            return hashlib.md5(obj_str.encode()).hexdigest()[:8]
        except Exception:
            return hashlib.md5(str(obj).encode()).hexdigest()[:8]


class Cache(ABC):
    """Abstract base class for cache implementations."""

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        pass

    @abstractmethod
    async def clear(self) -> bool:
        """Clear all cache entries."""
        pass

    @abstractmethod
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        pass


class MemoryCache(Cache):
    """High-performance in-memory cache with LRU eviction."""

    def __init__(self, config: CacheConfig = None):
        self.config = config or CacheConfig()
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._access_times: Dict[str, float] = {}
        self._access_counts: Dict[str, int] = {}
        self._lock = asyncio.Lock()

        # Statistics
        self._hits = 0
        self._misses = 0
        self._sets = 0
        self._evictions = 0

    async def get(self, key: str) -> Optional[Any]:
        """Get value from memory cache."""
        async with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None

            entry = self._cache[key]

            # Check TTL
            if entry.get("expires_at") and time.time() > entry["expires_at"]:
                await self._remove_key(key)
                self._misses += 1
                return None

            # Update access tracking
            self._access_times[key] = time.time()
            self._access_counts[key] = self._access_counts.get(key, 0) + 1

            self._hits += 1
            return entry["value"]

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in memory cache."""
        async with self._lock:
            # Check if we need to evict
            if len(self._cache) >= self.config.max_size and key not in self._cache:
                await self._evict_one()

            expires_at = None
            if ttl or self.config.default_ttl:
                expires_at = time.time() + (ttl or self.config.default_ttl)

            self._cache[key] = {
                "value": value,
                "expires_at": expires_at,
                "created_at": time.time(),
            }

            self._access_times[key] = time.time()
            self._access_counts[key] = 1
            self._sets += 1

            return True

    async def delete(self, key: str) -> bool:
        """Delete value from memory cache."""
        async with self._lock:
            if key in self._cache:
                await self._remove_key(key)
                return True
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in memory cache."""
        return key in self._cache

    async def clear(self) -> bool:
        """Clear all cache entries."""
        async with self._lock:
            self._cache.clear()
            self._access_times.clear()
            self._access_counts.clear()
            return True

    async def _remove_key(self, key: str) -> None:
        """Remove key and its tracking data."""
        self._cache.pop(key, None)
        self._access_times.pop(key, None)
        self._access_counts.pop(key, None)

    async def _evict_one(self) -> None:
        """Evict one entry based on strategy."""
        if not self._cache:
            return

        if self.config.strategy == CacheStrategy.LRU:
            # Evict least recently used
            lru_key = min(
                self._access_times.keys(), key=lambda k: self._access_times[k]
            )
            await self._remove_key(lru_key)
        elif self.config.strategy == CacheStrategy.LFU:
            # Evict least frequently used
            lfu_key = min(
                self._access_counts.keys(), key=lambda k: self._access_counts[k]
            )
            await self._remove_key(lfu_key)
        else:
            # Default: remove oldest entry
            oldest_key = min(
                self._cache.keys(), key=lambda k: self._cache[k]["created_at"]
            )
            await self._remove_key(oldest_key)

        self._evictions += 1

    async def get_stats(self) -> Dict[str, Any]:
        """Get memory cache statistics."""
        total_requests = self._hits + self._misses
        hit_rate = self._hits / max(total_requests, 1)

        return {
            "type": "memory",
            "size": len(self._cache),
            "max_size": self.config.max_size,
            "hits": self._hits,
            "misses": self._misses,
            "sets": self._sets,
            "evictions": self._evictions,
            "hit_rate": hit_rate,
            "strategy": self.config.strategy.value,
            "constitutional_hash": "cdd01ef066bc6cf2",
        }


class RedisCache(Cache):
    """Redis-based distributed cache with circuit breaker protection."""

    def __init__(
        self, redis_url: str = "redis://localhost:6379", config: CacheConfig = None
    ):
        self.redis_url = redis_url
        self.config = config or CacheConfig()
        self._redis: Optional[aioredis.Redis] = None
        self._circuit_breaker = None

        if self.config.circuit_breaker_enabled:
            cb_config = CircuitBreakerConfig(
                failure_threshold=3, recovery_timeout=30.0, timeout=5.0
            )
            self._circuit_breaker = get_circuit_breaker("redis_cache", cb_config)

        # Statistics
        self._hits = 0
        self._misses = 0
        self._sets = 0
        self._errors = 0

    async def _get_redis(self) -> aioredis.Redis:
        """Get Redis connection with lazy initialization."""
        if self._redis is None:
            try:
                self._redis = await aioredis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=False,  # We handle serialization
                )
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                self._errors += 1
                raise

        return self._redis

    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache."""
        try:
            if self._circuit_breaker:
                return await self._circuit_breaker.call(self._get_internal, key)
            else:
                return await self._get_internal(key)
        except Exception as e:
            logger.error(f"Redis cache get error: {e}")
            self._errors += 1
            self._misses += 1
            return None

    async def _get_internal(self, key: str) -> Optional[Any]:
        """Internal get method."""
        redis = await self._get_redis()

        data = await redis.get(key)
        if data is None:
            self._misses += 1
            return None

        try:
            value = pickle.loads(data)
            self._hits += 1
            return value
        except Exception as e:
            logger.error(f"Failed to deserialize cached value: {e}")
            self._errors += 1
            self._misses += 1
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in Redis cache."""
        try:
            if self._circuit_breaker:
                return await self._circuit_breaker.call(
                    self._set_internal, key, value, ttl
                )
            else:
                return await self._set_internal(key, value, ttl)
        except Exception as e:
            logger.error(f"Redis cache set error: {e}")
            self._errors += 1
            return False

    async def _set_internal(
        self, key: str, value: Any, ttl: Optional[int] = None
    ) -> bool:
        """Internal set method."""
        redis = await self._get_redis()

        try:
            data = pickle.dumps(value)
            expire_time = ttl or self.config.default_ttl

            await redis.setex(key, expire_time, data)
            self._sets += 1
            return True
        except Exception as e:
            logger.error(f"Failed to serialize value for cache: {e}")
            self._errors += 1
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from Redis cache."""
        try:
            redis = await self._get_redis()
            result = await redis.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Redis cache delete error: {e}")
            self._errors += 1
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis cache."""
        try:
            redis = await self._get_redis()
            return await redis.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis cache exists error: {e}")
            self._errors += 1
            return False

    async def clear(self) -> bool:
        """Clear all cache entries (use with caution)."""
        try:
            redis = await self._get_redis()
            await redis.flushdb()
            return True
        except Exception as e:
            logger.error(f"Redis cache clear error: {e}")
            self._errors += 1
            return False

    async def get_stats(self) -> Dict[str, Any]:
        """Get Redis cache statistics."""
        total_requests = self._hits + self._misses
        hit_rate = self._hits / max(total_requests, 1)

        redis_info = {}
        try:
            redis = await self._get_redis()
            info = await redis.info()
            redis_info = {
                "used_memory": info.get("used_memory", 0),
                "connected_clients": info.get("connected_clients", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
            }
        except Exception as e:
            logger.error(f"Failed to get Redis info: {e}")

        return {
            "type": "redis",
            "hits": self._hits,
            "misses": self._misses,
            "sets": self._sets,
            "errors": self._errors,
            "hit_rate": hit_rate,
            "redis_info": redis_info,
            "circuit_breaker": (
                self._circuit_breaker.get_status() if self._circuit_breaker else None
            ),
            "constitutional_hash": "cdd01ef066bc6cf2",
        }

    async def close(self) -> None:
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
            self._redis = None


class MultiLevelCache(Cache):
    """Multi-level cache combining memory and Redis for optimal performance."""

    def __init__(
        self,
        memory_cache: MemoryCache = None,
        redis_cache: RedisCache = None,
        config: CacheConfig = None,
    ):
        self.config = config or CacheConfig()
        self.l1_cache = memory_cache or MemoryCache(config)
        self.l2_cache = redis_cache

        # Statistics
        self._l1_hits = 0
        self._l2_hits = 0
        self._misses = 0

    async def get(self, key: str) -> Optional[Any]:
        """Get value from multi-level cache (L1 -> L2)."""
        # Try L1 cache first (memory)
        value = await self.l1_cache.get(key)
        if value is not None:
            self._l1_hits += 1
            return value

        # Try L2 cache (Redis) if available
        if self.l2_cache:
            value = await self.l2_cache.get(key)
            if value is not None:
                # Promote to L1 cache
                await self.l1_cache.set(key, value)
                self._l2_hits += 1
                return value

        self._misses += 1
        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in both cache levels."""
        l1_success = await self.l1_cache.set(key, value, ttl)

        l2_success = True
        if self.l2_cache:
            l2_success = await self.l2_cache.set(key, value, ttl)

        return l1_success and l2_success

    async def delete(self, key: str) -> bool:
        """Delete value from both cache levels."""
        l1_success = await self.l1_cache.delete(key)

        l2_success = True
        if self.l2_cache:
            l2_success = await self.l2_cache.delete(key)

        return l1_success or l2_success

    async def exists(self, key: str) -> bool:
        """Check if key exists in any cache level."""
        if await self.l1_cache.exists(key):
            return True

        if self.l2_cache:
            return await self.l2_cache.exists(key)

        return False

    async def clear(self) -> bool:
        """Clear all cache levels."""
        l1_success = await self.l1_cache.clear()

        l2_success = True
        if self.l2_cache:
            l2_success = await self.l2_cache.clear()

        return l1_success and l2_success

    async def get_stats(self) -> Dict[str, Any]:
        """Get multi-level cache statistics."""
        total_requests = self._l1_hits + self._l2_hits + self._misses
        l1_hit_rate = self._l1_hits / max(total_requests, 1)
        l2_hit_rate = self._l2_hits / max(total_requests, 1)
        overall_hit_rate = (self._l1_hits + self._l2_hits) / max(total_requests, 1)

        l1_stats = await self.l1_cache.get_stats()
        l2_stats = None
        if self.l2_cache:
            l2_stats = await self.l2_cache.get_stats()

        return {
            "type": "multi_level",
            "l1_hits": self._l1_hits,
            "l2_hits": self._l2_hits,
            "misses": self._misses,
            "l1_hit_rate": l1_hit_rate,
            "l2_hit_rate": l2_hit_rate,
            "overall_hit_rate": overall_hit_rate,
            "l1_stats": l1_stats,
            "l2_stats": l2_stats,
            "constitutional_hash": "cdd01ef066bc6cf2",
        }


class CacheManager:
    """Central cache manager for coordinating multiple cache instances."""

    def __init__(self):
        self._caches: Dict[str, Cache] = {}
        self._default_cache: Optional[Cache] = None

    def register_cache(self, name: str, cache: Cache, is_default: bool = False) -> None:
        """Register a cache instance."""
        self._caches[name] = cache
        if is_default or self._default_cache is None:
            self._default_cache = cache

        logger.info(f"Registered cache: {name}")

    def get_cache(self, name: str = None) -> Optional[Cache]:
        """Get cache by name or default."""
        if name:
            return self._caches.get(name)
        return self._default_cache

    async def get_global_stats(self) -> Dict[str, Any]:
        """Get statistics for all registered caches."""
        stats = {}
        for name, cache in self._caches.items():
            try:
                stats[name] = await cache.get_stats()
            except Exception as e:
                logger.error(f"Failed to get stats for cache {name}: {e}")
                stats[name] = {"error": str(e)}

        return {
            "cache_count": len(self._caches),
            "caches": stats,
            "constitutional_hash": "cdd01ef066bc6cf2",
        }


# Global cache manager
_cache_manager = CacheManager()


def get_cache_manager() -> CacheManager:
    """Get the global cache manager."""
    return _cache_manager


def cache_result(
    cache_name: str = None,
    key_prefix: str = None,
    ttl: int = None,
    tenant_aware: bool = True,
):
    """Decorator for caching function results."""

    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            cache = _cache_manager.get_cache(cache_name)
            if not cache:
                # No cache available, execute function directly
                return await func(*args, **kwargs)

            # Generate cache key
            prefix = key_prefix or func.__name__
            tenant_id = kwargs.get("tenant_id") if tenant_aware else None
            cache_key = CacheKey.generate(prefix, *args, tenant_id=tenant_id, **kwargs)

            # Try to get from cache
            result = await cache.get(cache_key)
            if result is not None:
                return result

            # Execute function and cache result
            result = await func(*args, **kwargs)
            if result is not None:
                await cache.set(cache_key, result, ttl)

            return result

        return wrapper

    return decorator


async def invalidate_cache(
    pattern: str, cache_name: str = None, tenant_id: str = None
) -> int:
    """Invalidate cache entries matching pattern."""
    cache = _cache_manager.get_cache(cache_name)
    if not cache:
        return 0

    # For now, this is a simplified implementation
    # In production, you'd want pattern matching for Redis
    logger.warning(f"Cache invalidation requested for pattern: {pattern}")
    return 0
