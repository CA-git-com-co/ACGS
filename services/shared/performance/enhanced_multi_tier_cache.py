"""
Enhanced Multi-Tier Caching Implementation for ACGS-2
HASH-OK:cdd01ef066bc6cf2

Implements optimized multi-tier caching strategy to achieve P99 latency <5ms:
- L1: In-memory cache with LRU eviction
- L2: Redis request-level caching
- L3: JWT and constitutional validation caching
- Performance monitoring and metrics collection
- Constitutional compliance validation throughout
"""

import asyncio
import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Union
from datetime import datetime, timedelta
import weakref

import aioredis
from aioredis import Redis

# Constitutional Hash: cdd01ef066bc6cf2
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)

@dataclass
class CacheMetrics:
    """Cache performance metrics for monitoring."""
    l1_hits: int = 0
    l1_misses: int = 0
    l2_hits: int = 0
    l2_misses: int = 0
    total_requests: int = 0
    avg_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    constitutional_validations: int = 0
    cache_errors: int = 0
    last_reset: datetime = field(default_factory=datetime.now)

@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    value: Any
    timestamp: float
    ttl: int
    access_count: int = 0
    constitutional_hash: str = CONSTITUTIONAL_HASH
    size_bytes: int = 0

class EnhancedMultiTierCache:
    """
    Enhanced multi-tier caching system optimized for ACGS-2 performance targets.
    
    Performance Targets:
    - P99 latency <5ms
    - Cache hit rate >85%
    - Constitutional compliance 100%
    """
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6389/0",
        l1_max_size: int = 10000,
        l2_default_ttl: int = 3600,
        enable_metrics: bool = True
    ):
        self.redis_url = redis_url
        self.l1_max_size = l1_max_size
        self.l2_default_ttl = l2_default_ttl
        self.enable_metrics = enable_metrics
        
        # L1 Cache (In-Memory)
        self.l1_cache: Dict[str, CacheEntry] = {}
        self.l1_access_order: List[str] = []
        self.l1_lock = asyncio.Lock()
        
        # L2 Cache (Redis)
        self.redis_client: Optional[Redis] = None
        self.redis_pool = None
        
        # Performance metrics
        self.metrics = CacheMetrics()
        self.latency_samples: List[float] = []
        
        # Constitutional compliance tracking
        self.constitutional_validations: Set[str] = set()
        
        # Cache configuration
        self.cache_prefixes = {
            "constitutional": "acgs:const:",
            "jwt": "acgs:jwt:",
            "validation": "acgs:val:",
            "policy": "acgs:policy:",
            "request": "acgs:req:",
            "session": "acgs:session:"
        }
        
        # TTL configuration by cache type
        self.ttl_config = {
            "constitutional": 7200,  # 2 hours - stable data
            "jwt": 3600,            # 1 hour - security sensitive
            "validation": 1800,     # 30 minutes - validation results
            "policy": 3600,         # 1 hour - policy data
            "request": 300,         # 5 minutes - request responses
            "session": 1800         # 30 minutes - session data
        }

    async def initialize(self) -> bool:
        """Initialize Redis connection and validate configuration."""
        try:
            # Create Redis connection pool
            self.redis_client = aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=20,
                retry_on_timeout=True,
                socket_keepalive=True
            )
            
            # Test Redis connection
            await self.redis_client.ping()
            
            # Validate constitutional hash
            await self._validate_constitutional_compliance()
            
            logger.info(f"Enhanced multi-tier cache initialized - Hash: {CONSTITUTIONAL_HASH}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize cache: {e}")
            return False

    async def get(
        self, 
        key: str, 
        cache_type: str = "request",
        validate_constitutional: bool = True
    ) -> Optional[Any]:
        """
        Get value from multi-tier cache with performance monitoring.
        
        Args:
            key: Cache key
            cache_type: Type of cache (constitutional, jwt, validation, etc.)
            validate_constitutional: Whether to validate constitutional compliance
            
        Returns:
            Cached value or None if not found
        """
        start_time = time.time()
        
        try:
            self.metrics.total_requests += 1
            cache_key = f"{self.cache_prefixes[cache_type]}{key}"
            
            # L1 Cache lookup (in-memory)
            async with self.l1_lock:
                if cache_key in self.l1_cache:
                    entry = self.l1_cache[cache_key]
                    
                    # Check TTL
                    if time.time() - entry.timestamp < entry.ttl:
                        # Update access order for LRU
                        if cache_key in self.l1_access_order:
                            self.l1_access_order.remove(cache_key)
                        self.l1_access_order.append(cache_key)
                        entry.access_count += 1
                        
                        # Validate constitutional compliance if required
                        if validate_constitutional and entry.constitutional_hash != CONSTITUTIONAL_HASH:
                            await self._invalidate_l1_entry(cache_key)
                            self.metrics.l1_misses += 1
                        else:
                            self.metrics.l1_hits += 1
                            self._record_latency(start_time)
                            return entry.value
                    else:
                        # Expired entry
                        await self._invalidate_l1_entry(cache_key)
                        self.metrics.l1_misses += 1
                else:
                    self.metrics.l1_misses += 1
            
            # L2 Cache lookup (Redis)
            if self.redis_client:
                try:
                    cached_data = await self.redis_client.get(cache_key)
                    if cached_data:
                        try:
                            entry_data = json.loads(cached_data)
                            
                            # Validate constitutional compliance
                            if validate_constitutional and entry_data.get("constitutional_hash") != CONSTITUTIONAL_HASH:
                                await self.redis_client.delete(cache_key)
                                self.metrics.l2_misses += 1
                            else:
                                # Store in L1 cache for faster future access
                                await self._store_l1_cache(cache_key, entry_data["value"], self.ttl_config[cache_type])
                                
                                self.metrics.l2_hits += 1
                                self._record_latency(start_time)
                                return entry_data["value"]
                                
                        except (json.JSONDecodeError, KeyError) as e:
                            logger.warning(f"Invalid cache data for key {cache_key}: {e}")
                            await self.redis_client.delete(cache_key)
                            self.metrics.cache_errors += 1
                    else:
                        self.metrics.l2_misses += 1
                        
                except Exception as e:
                    logger.warning(f"Redis cache lookup error: {e}")
                    self.metrics.cache_errors += 1
            
            self._record_latency(start_time)
            return None
            
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            self.metrics.cache_errors += 1
            self._record_latency(start_time)
            return None

    async def set(
        self, 
        key: str, 
        value: Any, 
        cache_type: str = "request",
        ttl: Optional[int] = None,
        validate_constitutional: bool = True
    ) -> bool:
        """
        Set value in multi-tier cache with constitutional validation.
        
        Args:
            key: Cache key
            value: Value to cache
            cache_type: Type of cache
            ttl: Time to live in seconds
            validate_constitutional: Whether to validate constitutional compliance
            
        Returns:
            True if successfully cached, False otherwise
        """
        start_time = time.time()
        
        try:
            cache_key = f"{self.cache_prefixes[cache_type]}{key}"
            cache_ttl = ttl or self.ttl_config[cache_type]
            
            # Prepare cache entry data
            entry_data = {
                "value": value,
                "timestamp": time.time(),
                "ttl": cache_ttl,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "cache_type": cache_type
            }
            
            # Constitutional compliance validation
            if validate_constitutional:
                await self._validate_cache_entry(entry_data)
                self.metrics.constitutional_validations += 1
            
            # Store in L1 cache
            await self._store_l1_cache(cache_key, value, cache_ttl)
            
            # Store in L2 cache (Redis)
            if self.redis_client:
                try:
                    serialized_data = json.dumps(entry_data)
                    await self.redis_client.setex(cache_key, cache_ttl, serialized_data)
                except Exception as e:
                    logger.warning(f"Redis cache set error: {e}")
                    self.metrics.cache_errors += 1
            
            self._record_latency(start_time)
            return True
            
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            self.metrics.cache_errors += 1
            self._record_latency(start_time)
            return False

    async def invalidate(self, key: str, cache_type: str = "request") -> bool:
        """Invalidate cache entry across all tiers."""
        try:
            cache_key = f"{self.cache_prefixes[cache_type]}{key}"
            
            # Invalidate L1 cache
            await self._invalidate_l1_entry(cache_key)
            
            # Invalidate L2 cache
            if self.redis_client:
                await self.redis_client.delete(cache_key)
            
            return True
            
        except Exception as e:
            logger.error(f"Cache invalidation error for key {key}: {e}")
            return False

    async def invalidate_pattern(self, pattern: str, cache_type: str = "request") -> int:
        """Invalidate multiple cache entries by pattern."""
        try:
            cache_pattern = f"{self.cache_prefixes[cache_type]}{pattern}"
            invalidated_count = 0
            
            # Invalidate L1 cache entries matching pattern
            async with self.l1_lock:
                keys_to_remove = [k for k in self.l1_cache.keys() if pattern in k]
                for key in keys_to_remove:
                    await self._invalidate_l1_entry(key)
                    invalidated_count += 1
            
            # Invalidate L2 cache entries matching pattern
            if self.redis_client:
                try:
                    keys = await self.redis_client.keys(cache_pattern)
                    if keys:
                        await self.redis_client.delete(*keys)
                        invalidated_count += len(keys)
                except Exception as e:
                    logger.warning(f"Redis pattern invalidation error: {e}")
            
            return invalidated_count
            
        except Exception as e:
            logger.error(f"Pattern invalidation error for pattern {pattern}: {e}")
            return 0

    async def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive cache performance metrics."""
        total_hits = self.metrics.l1_hits + self.metrics.l2_hits
        total_requests = self.metrics.total_requests
        
        hit_rate = total_hits / total_requests if total_requests > 0 else 0
        l1_hit_rate = self.metrics.l1_hits / total_requests if total_requests > 0 else 0
        l2_hit_rate = self.metrics.l2_hits / total_requests if total_requests > 0 else 0
        
        # Calculate P99 latency
        if self.latency_samples:
            sorted_latencies = sorted(self.latency_samples)
            p99_index = int(0.99 * len(sorted_latencies))
            p99_latency = sorted_latencies[p99_index] if p99_index < len(sorted_latencies) else 0
        else:
            p99_latency = 0
        
        return {
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "total_requests": total_requests,
            "cache_hit_rate": hit_rate,
            "l1_hit_rate": l1_hit_rate,
            "l2_hit_rate": l2_hit_rate,
            "avg_latency_ms": self.metrics.avg_latency_ms,
            "p99_latency_ms": p99_latency,
            "constitutional_validations": self.metrics.constitutional_validations,
            "cache_errors": self.metrics.cache_errors,
            "l1_cache_size": len(self.l1_cache),
            "performance_targets": {
                "hit_rate_target": 0.85,
                "p99_latency_target_ms": 5.0,
                "hit_rate_met": hit_rate >= 0.85,
                "latency_target_met": p99_latency <= 5.0
            }
        }

    async def _store_l1_cache(self, key: str, value: Any, ttl: int):
        """Store entry in L1 cache with LRU eviction."""
        async with self.l1_lock:
            # Create cache entry
            entry = CacheEntry(
                value=value,
                timestamp=time.time(),
                ttl=ttl,
                constitutional_hash=CONSTITUTIONAL_HASH,
                size_bytes=len(str(value))
            )
            
            # Store entry
            self.l1_cache[key] = entry
            
            # Update access order
            if key in self.l1_access_order:
                self.l1_access_order.remove(key)
            self.l1_access_order.append(key)
            
            # Evict if cache is full
            while len(self.l1_cache) > self.l1_max_size:
                oldest_key = self.l1_access_order.pop(0)
                if oldest_key in self.l1_cache:
                    del self.l1_cache[oldest_key]

    async def _invalidate_l1_entry(self, key: str):
        """Remove entry from L1 cache."""
        if key in self.l1_cache:
            del self.l1_cache[key]
        if key in self.l1_access_order:
            self.l1_access_order.remove(key)

    async def _validate_constitutional_compliance(self):
        """Validate constitutional compliance of cache system."""
        validation_key = f"constitutional_validation_{int(time.time())}"
        self.constitutional_validations.add(validation_key)
        
        # Verify constitutional hash
        if CONSTITUTIONAL_HASH != "cdd01ef066bc6cf2":
            raise ValueError(f"Invalid constitutional hash: {CONSTITUTIONAL_HASH}")

    async def _validate_cache_entry(self, entry_data: Dict[str, Any]):
        """Validate constitutional compliance of cache entry."""
        if entry_data.get("constitutional_hash") != CONSTITUTIONAL_HASH:
            raise ValueError("Cache entry constitutional hash mismatch")

    def _record_latency(self, start_time: float):
        """Record latency measurement for performance monitoring."""
        latency_ms = (time.time() - start_time) * 1000
        
        # Update metrics
        self.latency_samples.append(latency_ms)
        
        # Keep only recent samples for P99 calculation
        if len(self.latency_samples) > 10000:
            self.latency_samples = self.latency_samples[-5000:]
        
        # Update average latency
        if self.metrics.total_requests > 0:
            self.metrics.avg_latency_ms = (
                (self.metrics.avg_latency_ms * (self.metrics.total_requests - 1) + latency_ms) 
                / self.metrics.total_requests
            )

    async def close(self):
        """Close cache connections and cleanup resources."""
        if self.redis_client:
            await self.redis_client.close()
        
        # Clear L1 cache
        async with self.l1_lock:
            self.l1_cache.clear()
            self.l1_access_order.clear()

# Global cache instance
_cache_instance: Optional[EnhancedMultiTierCache] = None

async def get_enhanced_cache() -> EnhancedMultiTierCache:
    """Get global enhanced cache instance."""
    global _cache_instance
    
    if _cache_instance is None:
        _cache_instance = EnhancedMultiTierCache()
        await _cache_instance.initialize()
    
    return _cache_instance

# Specialized caching functions for common use cases

async def cache_constitutional_validation(
    policy_content: str, 
    validation_result: Dict[str, Any]
) -> bool:
    """Cache constitutional validation result."""
    cache = await get_enhanced_cache()
    key = hashlib.sha256(policy_content.encode()).hexdigest()
    return await cache.set(key, validation_result, "constitutional", ttl=7200)

async def get_cached_constitutional_validation(policy_content: str) -> Optional[Dict[str, Any]]:
    """Get cached constitutional validation result."""
    cache = await get_enhanced_cache()
    key = hashlib.sha256(policy_content.encode()).hexdigest()
    return await cache.get(key, "constitutional")

async def cache_jwt_validation(token_hash: str, validation_result: Dict[str, Any]) -> bool:
    """Cache JWT validation result."""
    cache = await get_enhanced_cache()
    return await cache.set(token_hash, validation_result, "jwt", ttl=3600)

async def get_cached_jwt_validation(token_hash: str) -> Optional[Dict[str, Any]]:
    """Get cached JWT validation result."""
    cache = await get_enhanced_cache()
    return await cache.get(token_hash, "jwt")

async def cache_request_response(
    request_hash: str, 
    response_data: Dict[str, Any]
) -> bool:
    """Cache request response data."""
    cache = await get_enhanced_cache()
    return await cache.set(request_hash, response_data, "request", ttl=300)

async def get_cached_request_response(request_hash: str) -> Optional[Dict[str, Any]]:
    """Get cached request response data."""
    cache = await get_enhanced_cache()
    return await cache.get(request_hash, "request")
