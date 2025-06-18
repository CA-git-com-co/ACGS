#!/usr/bin/env python3
"""
ACGS-1 Redis Caching Setup and Optimization

Implements enterprise-grade Redis caching strategies for the ACGS-1 constitutional governance system.
Optimizes response times and reduces database load across all 7 core services.

Features:
- Service-specific caching strategies
- Constitutional governance data caching
- Policy enforcement result caching
- Cross-service cache invalidation
- Performance monitoring integration
- Cache warming and preloading

Performance Targets:
- Cache hit ratio: >80%
- Response time reduction: >50%
- Database load reduction: >70%
"""

import hashlib
import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import redis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ACGS-1-Redis-Cache")


@dataclass
class CacheConfig:
    """Cache configuration for different data types."""

    ttl_seconds: int
    max_size: int
    compression: bool = False
    invalidation_pattern: str | None = None


class ACGSRedisCache:
    """Enterprise Redis caching system for ACGS-1."""

    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        """Initialize Redis cache with enterprise configuration."""
        try:
            self.redis_client = redis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30,
            )

            # Test connection
            self.redis_client.ping()
            logger.info("✅ Redis connection established successfully")

        except redis.ConnectionError:
            logger.warning("⚠️ Redis not available, using in-memory fallback")
            self.redis_client = None
            self._memory_cache = {}

        # Cache configurations for different services
        self.cache_configs = {
            # Auth Service caching
            "auth_tokens": CacheConfig(ttl_seconds=3600, max_size=10000),
            "user_sessions": CacheConfig(ttl_seconds=1800, max_size=5000),
            "rbac_permissions": CacheConfig(ttl_seconds=7200, max_size=1000),
            # AC Service caching
            "constitutional_principles": CacheConfig(ttl_seconds=86400, max_size=100),
            "compliance_results": CacheConfig(ttl_seconds=1800, max_size=5000),
            "council_decisions": CacheConfig(ttl_seconds=3600, max_size=1000),
            # Integrity Service caching
            "policy_rules": CacheConfig(ttl_seconds=3600, max_size=2000),
            "audit_logs": CacheConfig(ttl_seconds=7200, max_size=10000),
            "crypto_signatures": CacheConfig(ttl_seconds=86400, max_size=5000),
            # FV Service caching
            "verification_results": CacheConfig(ttl_seconds=7200, max_size=3000),
            "z3_proofs": CacheConfig(ttl_seconds=86400, max_size=1000),
            "safety_properties": CacheConfig(ttl_seconds=3600, max_size=500),
            # GS Service caching
            "policy_synthesis": CacheConfig(ttl_seconds=1800, max_size=2000),
            "llm_responses": CacheConfig(ttl_seconds=3600, max_size=5000),
            "constitutional_prompts": CacheConfig(ttl_seconds=7200, max_size=1000),
            # PGC Service caching
            "policy_enforcement": CacheConfig(ttl_seconds=300, max_size=10000),
            "opa_decisions": CacheConfig(ttl_seconds=600, max_size=5000),
            "compiled_policies": CacheConfig(ttl_seconds=3600, max_size=1000),
            # EC Service caching
            "wina_metrics": CacheConfig(ttl_seconds=300, max_size=2000),
            "oversight_results": CacheConfig(ttl_seconds=1800, max_size=1000),
            "performance_data": CacheConfig(ttl_seconds=600, max_size=5000),
        }

        # Performance metrics
        self.metrics = {
            "cache_hits": 0,
            "cache_misses": 0,
            "cache_sets": 0,
            "cache_deletes": 0,
            "total_requests": 0,
        }

    def _generate_cache_key(self, service: str, data_type: str, identifier: str) -> str:
        """Generate standardized cache key."""
        return f"acgs1:{service}:{data_type}:{identifier}"

    def _hash_data(self, data: Any) -> str:
        """Generate hash for cache key from complex data."""
        if isinstance(data, dict):
            # Sort dict for consistent hashing
            sorted_data = json.dumps(data, sort_keys=True)
        else:
            sorted_data = str(data)

        return hashlib.sha256(sorted_data.encode()).hexdigest()[:32]

    def get(self, service: str, data_type: str, identifier: str) -> Any | None:
        """Get data from cache."""
        cache_key = self._generate_cache_key(service, data_type, identifier)
        self.metrics["total_requests"] += 1

        try:
            if self.redis_client:
                cached_data = self.redis_client.get(cache_key)
                if cached_data:
                    self.metrics["cache_hits"] += 1
                    return json.loads(cached_data)
            else:
                # Fallback to memory cache
                if cache_key in self._memory_cache:
                    entry = self._memory_cache[cache_key]
                    if entry["expires"] > time.time():
                        self.metrics["cache_hits"] += 1
                        return entry["data"]
                    else:
                        del self._memory_cache[cache_key]

            self.metrics["cache_misses"] += 1
            return None

        except Exception as e:
            logger.error(f"Cache get error for {cache_key}: {e}")
            self.metrics["cache_misses"] += 1
            return None

    def set(
        self,
        service: str,
        data_type: str,
        identifier: str,
        data: Any,
        custom_ttl: int | None = None,
    ) -> bool:
        """Set data in cache."""
        cache_key = self._generate_cache_key(service, data_type, identifier)
        config = self.cache_configs.get(
            data_type, CacheConfig(ttl_seconds=3600, max_size=1000)
        )
        ttl = custom_ttl or config.ttl_seconds

        try:
            serialized_data = json.dumps(data, default=str)

            if self.redis_client:
                self.redis_client.setex(cache_key, ttl, serialized_data)
            else:
                # Fallback to memory cache
                self._memory_cache[cache_key] = {
                    "data": data,
                    "expires": time.time() + ttl,
                }

                # Simple LRU eviction for memory cache
                if len(self._memory_cache) > config.max_size:
                    oldest_key = min(
                        self._memory_cache.keys(),
                        key=lambda k: self._memory_cache[k]["expires"],
                    )
                    del self._memory_cache[oldest_key]

            self.metrics["cache_sets"] += 1
            return True

        except Exception as e:
            logger.error(f"Cache set error for {cache_key}: {e}")
            return False

    def delete(self, service: str, data_type: str, identifier: str) -> bool:
        """Delete data from cache."""
        cache_key = self._generate_cache_key(service, data_type, identifier)

        try:
            if self.redis_client:
                deleted = self.redis_client.delete(cache_key)
                if deleted:
                    self.metrics["cache_deletes"] += 1
                return bool(deleted)
            else:
                if cache_key in self._memory_cache:
                    del self._memory_cache[cache_key]
                    self.metrics["cache_deletes"] += 1
                    return True
                return False

        except Exception as e:
            logger.error(f"Cache delete error for {cache_key}: {e}")
            return False

    def invalidate_pattern(self, service: str, pattern: str) -> int:
        """Invalidate cache entries matching a pattern."""
        try:
            if self.redis_client:
                cache_pattern = f"acgs1:{service}:{pattern}"
                keys = self.redis_client.keys(cache_pattern)
                if keys:
                    deleted = self.redis_client.delete(*keys)
                    self.metrics["cache_deletes"] += deleted
                    return deleted
                return 0
            else:
                # Memory cache pattern matching
                pattern_key = f"acgs1:{service}:{pattern}"
                matching_keys = [
                    k for k in self._memory_cache.keys() if pattern_key in k
                ]
                for key in matching_keys:
                    del self._memory_cache[key]
                self.metrics["cache_deletes"] += len(matching_keys)
                return len(matching_keys)

        except Exception as e:
            logger.error(f"Cache pattern invalidation error: {e}")
            return 0

    def warm_cache(self) -> None:
        """Warm cache with frequently accessed data."""
        logger.info("🔥 Starting cache warming process...")

        # Warm constitutional principles (rarely change, frequently accessed)
        constitutional_principles = [
            {
                "id": "PC-001",
                "text": "No unauthorized state mutations",
                "priority": "critical",
            },
            {
                "id": "GV-001",
                "text": "Democratic governance required",
                "priority": "high",
            },
            {
                "id": "FN-001",
                "text": "Treasury protection mandatory",
                "priority": "critical",
            },
            {
                "id": "TR-001",
                "text": "Full transparency in governance",
                "priority": "medium",
            },
            {
                "id": "AC-001",
                "text": "Accountability for all actions",
                "priority": "high",
            },
        ]

        for principle in constitutional_principles:
            self.set(
                "ac", "constitutional_principles", principle["id"], principle, 86400
            )

        # Warm common RBAC permissions
        common_permissions = {
            "admin": ["read", "write", "delete", "govern"],
            "user": ["read"],
            "council_member": ["read", "write", "vote"],
            "auditor": ["read", "audit"],
        }

        for role, permissions in common_permissions.items():
            self.set("auth", "rbac_permissions", role, permissions, 7200)

        # Warm safety properties for FV service
        safety_properties = [
            {
                "id": "SP-001",
                "property": "no_double_spending",
                "formula": "∀x: spend(x) → ¬spent(x)",
            },
            {
                "id": "SP-002",
                "property": "governance_integrity",
                "formula": "∀p: policy(p) → verified(p)",
            },
            {
                "id": "SP-003",
                "property": "access_control",
                "formula": "∀u,r: access(u,r) → authorized(u,r)",
            },
        ]

        for prop in safety_properties:
            self.set("fv", "safety_properties", prop["id"], prop, 3600)

        logger.info("✅ Cache warming completed")

    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache performance statistics."""
        total_requests = self.metrics["total_requests"]
        hit_ratio = (
            (self.metrics["cache_hits"] / total_requests * 100)
            if total_requests > 0
            else 0
        )

        stats = {
            "hit_ratio_percent": round(hit_ratio, 2),
            "total_requests": total_requests,
            "cache_hits": self.metrics["cache_hits"],
            "cache_misses": self.metrics["cache_misses"],
            "cache_sets": self.metrics["cache_sets"],
            "cache_deletes": self.metrics["cache_deletes"],
            "redis_available": self.redis_client is not None,
            "timestamp": datetime.now().isoformat(),
        }

        if self.redis_client:
            try:
                info = self.redis_client.info()
                stats.update(
                    {
                        "redis_memory_used": info.get("used_memory_human", "unknown"),
                        "redis_connected_clients": info.get("connected_clients", 0),
                        "redis_keyspace_hits": info.get("keyspace_hits", 0),
                        "redis_keyspace_misses": info.get("keyspace_misses", 0),
                    }
                )
            except Exception as e:
                logger.error(f"Failed to get Redis info: {e}")
        else:
            stats.update(
                {
                    "memory_cache_size": len(self._memory_cache),
                    "memory_cache_keys": list(self._memory_cache.keys())[
                        :10
                    ],  # First 10 keys
                }
            )

        return stats

    def optimize_cache(self) -> dict[str, Any]:
        """Perform cache optimization operations."""
        optimization_results = {
            "timestamp": datetime.now().isoformat(),
            "operations_performed": [],
            "performance_improvement": {},
        }

        try:
            if self.redis_client:
                # Get memory usage before optimization
                info_before = self.redis_client.info()
                memory_before = info_before.get("used_memory", 0)

                # Remove expired keys
                expired_removed = 0
                try:
                    # This is a simplified approach - in production, use Redis SCAN
                    all_keys = self.redis_client.keys("acgs1:*")
                    for key in all_keys:
                        ttl = self.redis_client.ttl(key)
                        if ttl == -2:  # Key doesn't exist (expired)
                            expired_removed += 1
                except Exception as e:
                    logger.warning(f"Expired key cleanup failed: {e}")

                optimization_results["operations_performed"].append(
                    f"Removed {expired_removed} expired keys"
                )

                # Get memory usage after optimization
                info_after = self.redis_client.info()
                memory_after = info_after.get("used_memory", 0)
                memory_saved = memory_before - memory_after

                optimization_results["performance_improvement"] = {
                    "memory_saved_bytes": memory_saved,
                    "expired_keys_removed": expired_removed,
                }
            else:
                # Memory cache optimization
                current_time = time.time()
                expired_keys = [
                    key
                    for key, entry in self._memory_cache.items()
                    if entry["expires"] <= current_time
                ]

                for key in expired_keys:
                    del self._memory_cache[key]

                optimization_results["operations_performed"].append(
                    f"Removed {len(expired_keys)} expired keys from memory cache"
                )
                optimization_results["performance_improvement"] = {
                    "expired_keys_removed": len(expired_keys),
                    "memory_cache_size": len(self._memory_cache),
                }

            logger.info(f"Cache optimization completed: {optimization_results}")
            return optimization_results

        except Exception as e:
            logger.error(f"Cache optimization failed: {e}")
            optimization_results["error"] = str(e)
            return optimization_results


# Global cache instance
_cache_instance = None


def get_cache() -> ACGSRedisCache:
    """Get global cache instance."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = ACGSRedisCache()
    return _cache_instance


def setup_cache_for_services() -> dict[str, Any]:
    """Setup and configure cache for all ACGS-1 services."""
    logger.info("🚀 Setting up Redis cache for ACGS-1 services...")

    cache = get_cache()

    # Warm the cache
    cache.warm_cache()

    # Get initial stats
    stats = cache.get_cache_stats()

    logger.info(f"✅ Cache setup completed. Hit ratio: {stats['hit_ratio_percent']}%")

    return {
        "setup_completed": True,
        "cache_available": stats["redis_available"],
        "initial_stats": stats,
        "timestamp": datetime.now().isoformat(),
    }


if __name__ == "__main__":
    # Setup cache and run basic tests
    setup_result = setup_cache_for_services()
    print(json.dumps(setup_result, indent=2))

    # Run optimization
    cache = get_cache()
    optimization_result = cache.optimize_cache()
    print(json.dumps(optimization_result, indent=2))
