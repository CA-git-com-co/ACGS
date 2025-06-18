"""
Cache Enhancer for ACGS-1 Services

Provides Redis caching integration with constitutional compliance validation.
Optimizes performance through intelligent caching strategies.
"""

import json
import logging
import time
from typing import Any, Dict, Optional

# Try to import Redis
try:
    import redis.asyncio as redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)


class CacheEnhancer:
    """
    Lightweight Redis caching integration for ACGS-1 services.

    Features:
    - Redis connection pooling
    - Constitutional compliance caching
    - Performance optimization
    - Fallback to in-memory caching
    - Cache invalidation strategies
    """

    def __init__(
        self,
        service_name: str,
        redis_url: str = "redis://localhost:6379/0",
        default_ttl: int = 300,  # 5 minutes
    ):
        self.service_name = service_name
        self.redis_url = redis_url
        self.default_ttl = default_ttl
        self.redis_client: Optional[redis.Redis] = None
        self.redis_available = REDIS_AVAILABLE

        # Fallback in-memory cache
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "errors": 0,
        }

        logger.info(f"Cache enhancer initialized for {service_name}")

    async def initialize(self):
        """Initialize Redis connection."""
        if not self.redis_available:
            logger.warning("Redis not available - using in-memory cache fallback")
            return

        try:
            self.redis_client = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=20,
                socket_timeout=5,
                socket_connect_timeout=5,
            )

            # Test connection
            await self.redis_client.ping()
            logger.info(f"Redis cache initialized for {self.service_name}")

        except Exception as e:
            logger.error(f"Failed to initialize Redis cache: {e}")
            self.redis_client = None

    async def close(self):
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()
            logger.info(f"Redis cache closed for {self.service_name}")

    def _generate_cache_key(self, key: str, namespace: Optional[str] = None) -> str:
        """Generate cache key with service namespace."""
        if namespace:
            return f"{self.service_name}:{namespace}:{key}"
        return f"{self.service_name}:{key}"

    async def get(self, key: str, namespace: Optional[str] = None) -> Optional[Any]:
        """Get value from cache."""
        cache_key = self._generate_cache_key(key, namespace)

        try:
            # Try Redis first
            if self.redis_client:
                value = await self.redis_client.get(cache_key)
                if value is not None:
                    self.cache_stats["hits"] += 1
                    return json.loads(value)

            # Fallback to memory cache
            if cache_key in self.memory_cache:
                cache_entry = self.memory_cache[cache_key]

                # Check expiration
                if cache_entry["expires_at"] > time.time():
                    self.cache_stats["hits"] += 1
                    return cache_entry["value"]
                else:
                    # Remove expired entry
                    del self.memory_cache[cache_key]

            self.cache_stats["misses"] += 1
            return None

        except Exception as e:
            logger.error(f"Cache get error for key {cache_key}: {e}")
            self.cache_stats["errors"] += 1
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        namespace: Optional[str] = None,
    ) -> bool:
        """Set value in cache."""
        cache_key = self._generate_cache_key(key, namespace)
        ttl = ttl or self.default_ttl

        try:
            # Try Redis first
            if self.redis_client:
                json_value = json.dumps(value)
                await self.redis_client.setex(cache_key, ttl, json_value)
                self.cache_stats["sets"] += 1
                return True

            # Fallback to memory cache
            self.memory_cache[cache_key] = {
                "value": value,
                "expires_at": time.time() + ttl,
            }
            self.cache_stats["sets"] += 1
            return True

        except Exception as e:
            logger.error(f"Cache set error for key {cache_key}: {e}")
            self.cache_stats["errors"] += 1
            return False

    async def delete(self, key: str, namespace: Optional[str] = None) -> bool:
        """Delete value from cache."""
        cache_key = self._generate_cache_key(key, namespace)

        try:
            # Try Redis first
            if self.redis_client:
                await self.redis_client.delete(cache_key)

            # Remove from memory cache
            if cache_key in self.memory_cache:
                del self.memory_cache[cache_key]

            self.cache_stats["deletes"] += 1
            return True

        except Exception as e:
            logger.error(f"Cache delete error for key {cache_key}: {e}")
            self.cache_stats["errors"] += 1
            return False

    async def cache_constitutional_validation(
        self, request_hash: str, validation_result: Dict[str, Any], ttl: int = 300
    ) -> str:
        """Cache constitutional validation result."""
        cache_key = f"constitutional_validation:{request_hash}"
        await self.set(cache_key, validation_result, ttl, "constitutional")
        return cache_key

    async def get_cached_constitutional_validation(
        self, request_hash: str
    ) -> Optional[Dict[str, Any]]:
        """Get cached constitutional validation result."""
        cache_key = f"constitutional_validation:{request_hash}"
        return await self.get(cache_key, "constitutional")

    async def cache_policy_decision(
        self,
        policy_content: str,
        input_data: Dict[str, Any],
        result: Any,
        ttl: int = 300,
    ) -> str:
        """Cache policy decision result."""
        # Create cache key from policy content and input data
        cache_data = {
            "policy_content": policy_content,
            "input_data": input_data,
        }
        cache_key = f"policy_decision:{hash(json.dumps(cache_data, sort_keys=True))}"
        await self.set(cache_key, result, ttl, "policy")
        return cache_key

    async def get_cached_policy_decision(
        self, policy_content: str, input_data: Dict[str, Any]
    ) -> Optional[Any]:
        """Get cached policy decision result."""
        cache_data = {
            "policy_content": policy_content,
            "input_data": input_data,
        }
        cache_key = f"policy_decision:{hash(json.dumps(cache_data, sort_keys=True))}"
        return await self.get(cache_key, "policy")

    async def invalidate_namespace(self, namespace: str) -> int:
        """Invalidate all cache entries in a namespace."""
        pattern = f"{self.service_name}:{namespace}:*"
        deleted_count = 0

        try:
            if self.redis_client:
                # Get all keys matching pattern
                keys = await self.redis_client.keys(pattern)
                if keys:
                    deleted_count = await self.redis_client.delete(*keys)

            # Clear from memory cache
            keys_to_delete = [
                key
                for key in self.memory_cache.keys()
                if key.startswith(f"{self.service_name}:{namespace}:")
            ]
            for key in keys_to_delete:
                del self.memory_cache[key]
                deleted_count += 1

            logger.info(
                f"Invalidated {deleted_count} cache entries in namespace {namespace}"
            )
            return deleted_count

        except Exception as e:
            logger.error(f"Cache invalidation error for namespace {namespace}: {e}")
            return 0

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = (
            self.cache_stats["hits"] / total_requests if total_requests > 0 else 0.0
        )

        return {
            "service": self.service_name,
            "redis_available": self.redis_client is not None,
            "cache_stats": self.cache_stats.copy(),
            "hit_rate": hit_rate,
            "memory_cache_size": len(self.memory_cache),
        }
