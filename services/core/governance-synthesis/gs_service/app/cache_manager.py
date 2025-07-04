"""
Enhanced Cache Manager for gs_service - ACGS Performance Optimization
Integrates intelligent caching with optimization engine
"""

import os
from typing import Any, Optional

import structlog

from services.shared.redis_client import ACGSRedisClient, get_redis_client
from services.shared.cache.enhanced_cache_optimizer import EnhancedCacheOptimizer, CacheDataType
from services.core.governance-synthesis.gs_service.app.services.advanced_cache import MultiTierCache, LRUCache, RedisCache

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = structlog.get_logger(__name__)


class EnhancedGsCacheManager:
    """Enhanced cache manager with intelligent optimization."""
    
    def __init__(self):
        self.service_name = "gs_service"
        self.redis_client: Optional[ACGSRedisClient] = None
        self.cache_optimizer: Optional[EnhancedCacheOptimizer] = None
        self.multi_tier_cache: Optional[MultiTierCache] = None
        self._initialized = False

    async def initialize(self):
        """Initialize enhanced cache manager with optimization."""
        if self._initialized:
            return

        try:
            # Initialize Redis client
            self.redis_client = await get_redis_client(self.service_name)
            
            # Initialize cache optimizer
            self.cache_optimizer = EnhancedCacheOptimizer(
                redis_client=self.redis_client,
                service_name=self.service_name
            )
            
            # Initialize multi-tier cache
            await self._initialize_multi_tier_cache()
            
            # Start optimization engine
            await self.cache_optimizer.start_optimization_engine()
            
            self._initialized = True
            logger.info(
                "Enhanced cache manager initialized",
                service=self.service_name,
                constitutional_hash=CONSTITUTIONAL_HASH
            )

        except Exception as e:
            logger.error("Failed to initialize enhanced cache manager", error=str(e))
            raise

    async def _initialize_multi_tier_cache(self):
        """Initialize multi-tier cache system."""
        # L1 Cache: In-memory LRU cache
        l1_cache = LRUCache(max_size=1000, default_ttl=300)
        
        # L2 Cache: Redis distributed cache
        async with self.redis_client.get_client() as redis_conn:
            l2_cache = RedisCache(
                redis_client=redis_conn,
                key_prefix=f"acgs:{self.service_name}:",
                enable_pubsub=True
            )
        
        # Multi-tier cache
        self.multi_tier_cache = MultiTierCache(
            l1_cache=l1_cache,
            l2_cache=l2_cache,
            enable_warming=True
        )

    async def get(self, key: str, data_type: Optional[CacheDataType] = None) -> Any:
        """Get value from cache with optimization tracking."""
        if not self._initialized:
            await self.initialize()
        
        # Try multi-tier cache first
        value = await self.multi_tier_cache.get(key)
        hit = value is not None
        
        # Record access for optimization
        await self.cache_optimizer.record_cache_access(key, hit, "get")
        
        return value

    async def put(
        self,
        key: str,
        value: Any,
        data_type: Optional[CacheDataType] = None,
        tags: Optional[list[str]] = None
    ) -> bool:
        """Put value in cache with intelligent TTL."""
        if not self._initialized:
            await self.initialize()
        
        # Calculate intelligent TTL
        ttl = self.cache_optimizer.calculate_intelligent_ttl(key, data_type)
        
        # Store in multi-tier cache
        success = await self.multi_tier_cache.put(key, value, ttl, tags)
        
        if success:
            # Record successful cache operation
            await self.cache_optimizer.record_cache_access(key, True, "put")
        
        return success

    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if not self._initialized:
            await self.initialize()
        
        return await self.multi_tier_cache.delete(key)

    async def invalidate_by_tags(self, tags: list[str]):
        """Invalidate cache entries by tags."""
        if not self._initialized:
            await self.initialize()
        
        self.multi_tier_cache.invalidate_by_tags(tags)

    async def warm_cache_with_governance_data(self, governance_data: list[dict[str, Any]]):
        """Warm cache with governance-specific data."""
        if not self._initialized:
            await self.initialize()
        
        # Convert governance data to warming format
        warming_data = []
        for item in governance_data:
            warming_data.append({
                "key": f"governance:{item.get('id', 'unknown')}",
                "value": item,
                "ttl": self.cache_optimizer.calculate_intelligent_ttl(
                    f"governance:{item.get('id')}", 
                    CacheDataType.GOVERNANCE_RULES
                ),
                "tags": ["governance", item.get("category", "general")]
            })
        
        # Force warming
        await self.cache_optimizer.force_cache_warming(warming_data)
        
        logger.info(
            "Cache warmed with governance data",
            items_count=len(warming_data),
            service=self.service_name
        )

    async def warm_cache_with_constitutional_data(self, constitutional_data: list[dict[str, Any]]):
        """Warm cache with constitutional validation data."""
        if not self._initialized:
            await self.initialize()
        
        warming_data = []
        for item in constitutional_data:
            key = f"constitutional:{CONSTITUTIONAL_HASH}:{item.get('id', 'validation')}"
            warming_data.append({
                "key": key,
                "value": item,
                "ttl": self.cache_optimizer.calculate_intelligent_ttl(
                    key, 
                    CacheDataType.CONSTITUTIONAL_VALIDATIONS
                ),
                "tags": ["constitutional", "validation", CONSTITUTIONAL_HASH]
            })
        
        await self.cache_optimizer.force_cache_warming(warming_data)
        
        logger.info(
            "Cache warmed with constitutional data",
            items_count=len(warming_data),
            constitutional_hash=CONSTITUTIONAL_HASH
        )

    async def get_enhanced_cache_metrics(self) -> dict[str, Any]:
        """Get comprehensive cache metrics including optimization data."""
        if not self._initialized:
            await self.initialize()

        # Get base cache stats
        cache_stats = self.multi_tier_cache.get_stats()
        
        # Get optimization metrics
        optimization_metrics = self.cache_optimizer.get_optimization_metrics()
        
        return {
            "service": self.service_name,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "cache_stats": {
                "multi_tier": {
                    "total_requests": cache_stats["multi_tier"].total_requests,
                    "cache_hits": cache_stats["multi_tier"].cache_hits,
                    "cache_misses": cache_stats["multi_tier"].cache_misses,
                    "hit_rate": cache_stats["multi_tier"].hit_rate,
                },
                "l1_cache": {
                    "entry_count": cache_stats["l1_cache"].entry_count,
                    "memory_usage_bytes": cache_stats["l1_cache"].memory_usage_bytes,
                    "evictions": cache_stats["l1_cache"].evictions,
                    "hit_rate": cache_stats["l1_cache"].hit_rate,
                },
                "l2_cache": {
                    "total_requests": cache_stats["l2_cache"].total_requests,
                    "cache_hits": cache_stats["l2_cache"].cache_hits,
                    "cache_misses": cache_stats["l2_cache"].cache_misses,
                    "hit_rate": cache_stats["l2_cache"].hit_rate,
                    "errors": cache_stats["l2_cache"].errors,
                }
            },
            "optimization": optimization_metrics,
            "performance_targets": {
                "hit_rate_target": 0.85,  # 85% cache hit rate target
                "response_time_target": 5,  # 5ms response time target
                "warming_efficiency": optimization_metrics["warming_strategy"]["enabled"]
            }
        }

    async def optimize_cache_performance(self):
        """Manually trigger cache performance optimization."""
        if not self._initialized:
            await self.initialize()
        
        # Force TTL optimization
        await self.cache_optimizer.optimize_existing_cache_ttls()
        
        # Force predictive warming
        await self.cache_optimizer.predictive_cache_warming()
        
        logger.info(
            "Manual cache optimization completed",
            service=self.service_name
        )

    async def shutdown(self):
        """Gracefully shutdown cache manager."""
        if self.cache_optimizer:
            await self.cache_optimizer.stop_optimization_engine()
        
        if self.redis_client:
            await self.redis_client.close()
        
        self._initialized = False
        
        logger.info(
            "Enhanced cache manager shutdown completed",
            service=self.service_name
        )


# Legacy cache manager for backward compatibility
class Gs_serviceCacheManager:
    """Legacy cache manager - deprecated, use EnhancedGsCacheManager instead."""
    
    def __init__(self):
        self.service_name = "gs_service"
        self.enhanced_manager: Optional[EnhancedGsCacheManager] = None
        self._initialized = False

    async def initialize(self):
        if self._initialized:
            return
        
        self.enhanced_manager = EnhancedGsCacheManager()
        await self.enhanced_manager.initialize()
        self._initialized = True

    async def get_cache_metrics(self) -> dict[str, Any]:
        """Get cache metrics - delegates to enhanced manager."""
        if not self._initialized:
            await self.initialize()
        
        enhanced_metrics = await self.enhanced_manager.get_enhanced_cache_metrics()
        
        # Return simplified metrics for backward compatibility
        return {
            "service": self.service_name,
            "total_requests": enhanced_metrics["cache_stats"]["multi_tier"]["total_requests"],
            "cache_hits": enhanced_metrics["cache_stats"]["multi_tier"]["cache_hits"],
            "cache_misses": enhanced_metrics["cache_stats"]["multi_tier"]["cache_misses"],
            "hit_rate": enhanced_metrics["cache_stats"]["multi_tier"]["hit_rate"],
            "errors": enhanced_metrics["cache_stats"]["l2_cache"]["errors"],
        }


# Global cache manager instances
_cache_manager: Optional[Gs_serviceCacheManager] = None
_enhanced_cache_manager: Optional[EnhancedGsCacheManager] = None


async def get_cache_manager() -> Gs_serviceCacheManager:
    """Get legacy cache manager for backward compatibility."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = Gs_serviceCacheManager()
        await _cache_manager.initialize()
    return _cache_manager


async def get_enhanced_cache_manager() -> EnhancedGsCacheManager:
    """Get enhanced cache manager with optimization features."""
    global _enhanced_cache_manager
    if _enhanced_cache_manager is None:
        _enhanced_cache_manager = EnhancedGsCacheManager()
        await _enhanced_cache_manager.initialize()
    return _enhanced_cache_manager


async def shutdown_cache_managers():
    """Shutdown all cache managers gracefully."""
    global _cache_manager, _enhanced_cache_manager
    
    if _enhanced_cache_manager:
        await _enhanced_cache_manager.shutdown()
        _enhanced_cache_manager = None
    
    if _cache_manager and _cache_manager.enhanced_manager:
        await _cache_manager.enhanced_manager.shutdown()
    
    _cache_manager = None
    
    logger.info("All cache managers shutdown completed")
