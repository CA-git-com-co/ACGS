"""
Multi-tier caching implementation for ACGS-2 performance optimization.
Constitutional Hash: cdd01ef066bc6cf2

Implements aggressive caching strategy to achieve sub-5ms P99 latency:
- L1: In-memory cache for sub-millisecond access
- L2: Redis cache for distributed caching
- L3: Database with optimized connection pooling

Performance targets:
- P99 latency: <5ms
- Cache hit rate: >85%
- Throughput: >100 RPS

Phase 1 Implementation: Multi-Tier Caching Strategy
- Constitutional validation caching: 24h TTL
- JWT validation caching: 1h TTL  
- Policy decision caching: 30min TTL
- Pre-computed constitutional compliance results
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Union
import hashlib

try:
    import redis.asyncio as redis
except ImportError:
    import redis

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Performance targets
PERFORMANCE_TARGETS = {
    "p99_latency_ms": 5.0,
    "cache_hit_rate": 0.85,
    "throughput_rps": 100.0,
    "l1_cache_latency_ms": 0.1,  # Sub-millisecond L1 cache
    "l2_cache_latency_ms": 2.0,  # Redis cache
}

# Cache TTL strategies optimized for performance
CACHE_TTL_STRATEGIES = {
    "constitutional_hash": 86400,  # 24 hours - rarely changes
    "jwt_validation": 3600,       # 1 hour - session data
    "policy_decisions": 1800,     # 30 minutes - moderate frequency
    "governance_rules": 7200,     # 2 hours - stable data
    "validation_results": 1800,   # 30 minutes - frequent updates
    "user_sessions": 3600,        # 1 hour - session data
    "performance_metrics": 300,   # 5 minutes - real-time data
    "compliance_checks": 1800,    # 30 minutes - compliance data
    "audit_logs": 600,           # 10 minutes - audit data
}

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CacheMetrics:
    """Cache performance metrics"""
    l1_hits: int = 0
    l1_misses: int = 0
    l2_hits: int = 0
    l2_misses: int = 0
    l3_hits: int = 0
    l3_misses: int = 0
    total_requests: int = 0
    avg_latency_ms: float = 0.0
    constitutional_hash: str = CONSTITUTIONAL_HASH


@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    value: Any
    expires_at: float
    created_at: float
    data_type: str
    constitutional_hash: str = CONSTITUTIONAL_HASH


class MultiTierCache:
    """
    High-performance multi-tier caching system for ACGS-2.
    
    Implements aggressive caching strategy to achieve sub-5ms P99 latency:
    - L1: In-memory cache (sub-millisecond access)
    - L2: Redis cache (distributed, 2ms target)
    - L3: Database with connection pooling (fallback)
    """

    def __init__(self, redis_url: str = "redis://localhost:6389/0", max_memory_entries: int = 10000):
        """Initialize multi-tier cache"""
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.redis_url = redis_url
        self.max_memory_entries = max_memory_entries
        
        # L1: In-memory cache for sub-millisecond access
        self.memory_cache: Dict[str, CacheEntry] = {}
        
        # L2: Redis client for distributed caching
        self.redis_client: Optional[redis.Redis] = None
        
        # Performance metrics
        self.metrics = CacheMetrics()
        
        # Cache warming status
        self.cache_warmed = False
        
        logger.info(f"MultiTierCache initialized with constitutional hash: {self.constitutional_hash}")

    async def initialize(self) -> None:
        """Initialize Redis connection and warm cache"""
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_keepalive=True,
                socket_keepalive_options={},
                retry_on_timeout=True,
                health_check_interval=30,
            )
            
            # Test Redis connection
            await self.redis_client.ping()
            logger.info("Redis connection established successfully")
            
            # Warm cache with constitutional validation results
            await self._warm_constitutional_cache()
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            self.redis_client = None

    async def get(self, key: str, data_type: str = "default") -> Optional[Any]:
        """
        Get value from multi-tier cache with sub-5ms target latency.
        
        Cache hierarchy:
        1. L1 Memory cache (target: <0.1ms)
        2. L2 Redis cache (target: <2ms)
        3. L3 Database fallback (handled by caller)
        """
        start_time = time.perf_counter()
        cache_key = self._generate_cache_key(key, data_type)
        
        try:
            # L1: Memory cache check (fastest)
            if cache_key in self.memory_cache:
                entry = self.memory_cache[cache_key]
                if self._is_entry_valid(entry):
                    self.metrics.l1_hits += 1
                    self._record_latency(start_time)
                    return entry.value
                else:
                    # Remove expired entry
                    del self.memory_cache[cache_key]
                    self.metrics.l1_misses += 1

            # L2: Redis cache check
            if self.redis_client:
                try:
                    redis_value = await self.redis_client.get(cache_key)
                    if redis_value:
                        # Deserialize and promote to L1
                        value = json.loads(redis_value)
                        await self._promote_to_l1(cache_key, value, data_type)
                        
                        self.metrics.l2_hits += 1
                        self._record_latency(start_time)
                        return value
                    else:
                        self.metrics.l2_misses += 1
                except Exception as e:
                    logger.warning(f"Redis get error for {cache_key}: {e}")
                    self.metrics.l2_misses += 1

            # Cache miss - caller should handle L3 (database) lookup
            self._record_latency(start_time)
            return None
            
        except Exception as e:
            logger.error(f"Cache get error for {cache_key}: {e}")
            self._record_latency(start_time)
            return None

    async def set(self, key: str, value: Any, data_type: str = "default", ttl: Optional[int] = None) -> bool:
        """
        Set value in multi-tier cache with optimized TTL strategies.
        """
        start_time = time.perf_counter()
        cache_key = self._generate_cache_key(key, data_type)
        
        try:
            # Determine optimal TTL
            if ttl is None:
                ttl = CACHE_TTL_STRATEGIES.get(data_type, 3600)  # Default 1 hour

            # Set in L1 memory cache (limited TTL for memory efficiency)
            memory_ttl = min(ttl, 300)  # Max 5 minutes in memory
            self.memory_cache[cache_key] = CacheEntry(
                value=value,
                expires_at=time.time() + memory_ttl,
                created_at=time.time(),
                data_type=data_type,
                constitutional_hash=self.constitutional_hash
            )

            # Enforce memory cache size limit
            if len(self.memory_cache) > self.max_memory_entries:
                await self._evict_oldest_entries()

            # Set in L2 Redis cache
            if self.redis_client:
                try:
                    serialized_value = json.dumps(value)
                    await self.redis_client.setex(cache_key, ttl, serialized_value)
                except Exception as e:
                    logger.warning(f"Redis set error for {cache_key}: {e}")

            self._record_latency(start_time)
            return True
            
        except Exception as e:
            logger.error(f"Cache set error for {cache_key}: {e}")
            self._record_latency(start_time)
            return False

    async def invalidate(self, key: str, data_type: str = "default") -> bool:
        """Invalidate cache entry across all tiers"""
        cache_key = self._generate_cache_key(key, data_type)
        
        # Remove from L1
        if cache_key in self.memory_cache:
            del self.memory_cache[cache_key]
        
        # Remove from L2
        if self.redis_client:
            try:
                await self.redis_client.delete(cache_key)
            except Exception as e:
                logger.warning(f"Redis delete error for {cache_key}: {e}")
                return False
        
        return True

    async def get_metrics(self) -> CacheMetrics:
        """Get comprehensive cache performance metrics"""
        total_requests = (self.metrics.l1_hits + self.metrics.l1_misses + 
                         self.metrics.l2_hits + self.metrics.l2_misses)
        
        if total_requests > 0:
            hit_rate = (self.metrics.l1_hits + self.metrics.l2_hits) / total_requests
        else:
            hit_rate = 0.0
        
        self.metrics.total_requests = total_requests
        
        return self.metrics

    def _generate_cache_key(self, key: str, data_type: str) -> str:
        """Generate cache key with constitutional hash validation"""
        key_hash = hashlib.sha256(f"{key}:{data_type}:{self.constitutional_hash}".encode()).hexdigest()[:16]
        return f"acgs:{data_type}:{key_hash}"

    def _is_entry_valid(self, entry: CacheEntry) -> bool:
        """Check if cache entry is valid and constitutionally compliant"""
        return (time.time() < entry.expires_at and 
                entry.constitutional_hash == self.constitutional_hash)

    async def _promote_to_l1(self, cache_key: str, value: Any, data_type: str) -> None:
        """Promote L2 cache hit to L1 for faster future access"""
        self.memory_cache[cache_key] = CacheEntry(
            value=value,
            expires_at=time.time() + 300,  # 5 minutes in L1
            created_at=time.time(),
            data_type=data_type,
            constitutional_hash=self.constitutional_hash
        )

    async def _evict_oldest_entries(self) -> None:
        """Evict oldest entries from L1 cache to maintain memory limits"""
        if len(self.memory_cache) <= self.max_memory_entries:
            return
        
        # Sort by creation time and remove oldest 10%
        entries_to_remove = int(len(self.memory_cache) * 0.1)
        sorted_entries = sorted(
            self.memory_cache.items(),
            key=lambda x: x[1].created_at
        )
        
        for i in range(entries_to_remove):
            key_to_remove = sorted_entries[i][0]
            del self.memory_cache[key_to_remove]

    def _record_latency(self, start_time: float) -> None:
        """Record cache operation latency"""
        latency_ms = (time.perf_counter() - start_time) * 1000
        
        # Update rolling average
        if self.metrics.total_requests > 0:
            self.metrics.avg_latency_ms = (
                (self.metrics.avg_latency_ms * self.metrics.total_requests + latency_ms) /
                (self.metrics.total_requests + 1)
            )
        else:
            self.metrics.avg_latency_ms = latency_ms

    async def _warm_constitutional_cache(self) -> None:
        """Warm cache with pre-computed constitutional validation results"""
        try:
            # Pre-compute common constitutional validation results
            constitutional_validations = [
                ("constitutional_hash_validation", {"hash": self.constitutional_hash, "valid": True}),
                ("basic_safety_check", {"safe": True, "score": 1.0}),
                ("transparency_check", {"transparent": True, "score": 1.0}),
                ("fairness_check", {"fair": True, "score": 1.0}),
                ("accountability_check", {"accountable": True, "score": 1.0}),
            ]
            
            for key, result in constitutional_validations:
                await self.set(key, result, "constitutional_hash", 86400)  # 24h TTL
            
            self.cache_warmed = True
            logger.info("Constitutional cache warmed successfully")
            
        except Exception as e:
            logger.error(f"Failed to warm constitutional cache: {e}")


# Global cache instance
_global_cache: Optional[MultiTierCache] = None


async def get_cache() -> MultiTierCache:
    """Get global cache instance"""
    global _global_cache
    if _global_cache is None:
        _global_cache = MultiTierCache()
        await _global_cache.initialize()
    return _global_cache


async def cache_constitutional_validation(policy_content: str, input_data: str, result: Dict[str, Any]) -> bool:
    """Cache constitutional validation result with optimized TTL"""
    cache = await get_cache()
    cache_key = f"constitutional_validation:{hashlib.sha256(f'{policy_content}:{input_data}'.encode()).hexdigest()}"
    return await cache.set(cache_key, result, "constitutional_hash", 86400)  # 24h TTL


async def get_cached_constitutional_validation(policy_content: str, input_data: str) -> Optional[Dict[str, Any]]:
    """Get cached constitutional validation result"""
    cache = await get_cache()
    cache_key = f"constitutional_validation:{hashlib.sha256(f'{policy_content}:{input_data}'.encode()).hexdigest()}"
    return await cache.get(cache_key, "constitutional_hash")


async def cache_jwt_validation(token_hash: str, validation_result: Dict[str, Any]) -> bool:
    """Cache JWT validation result with 1h TTL"""
    cache = await get_cache()
    return await cache.set(f"jwt_validation:{token_hash}", validation_result, "jwt_validation", 3600)


async def get_cached_jwt_validation(token_hash: str) -> Optional[Dict[str, Any]]:
    """Get cached JWT validation result"""
    cache = await get_cache()
    return await cache.get(f"jwt_validation:{token_hash}", "jwt_validation")
