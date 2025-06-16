"""
Redis Performance Optimizer for ACGS-1

Implements advanced Redis caching strategies, connection pooling,
and performance optimizations to support >1000 concurrent governance actions
with <500ms response times.
"""

import asyncio
import redis.asyncio as redis
import time
import json
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
import hashlib
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


@dataclass
class CacheConfig:
    """Redis cache configuration."""
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    max_connections: int = 50
    retry_on_timeout: bool = True
    socket_timeout: float = 5.0
    socket_connect_timeout: float = 5.0
    health_check_interval: int = 30


@dataclass
class CacheMetrics:
    """Cache performance metrics."""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    errors: int = 0
    total_operations: int = 0
    avg_response_time: float = 0.0
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total_gets = self.hits + self.misses
        return self.hits / total_gets if total_gets > 0 else 0.0


class RedisPerformanceOptimizer:
    """
    Advanced Redis performance optimizer for ACGS-1.
    
    Provides high-performance caching with connection pooling,
    intelligent cache strategies, and comprehensive monitoring.
    """
    
    def __init__(self, config: CacheConfig = None):
        """
        Initialize Redis performance optimizer.
        
        Args:
            config: Redis configuration
        """
        self.config = config or CacheConfig()
        self.pool = None
        self.metrics = CacheMetrics()
        self.cache_strategies = {}
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize Redis connection pool."""
        try:
            self.pool = redis.ConnectionPool(
                host=self.config.host,
                port=self.config.port,
                db=self.config.db,
                password=self.config.password,
                max_connections=self.config.max_connections,
                retry_on_timeout=self.config.retry_on_timeout,
                socket_timeout=self.config.socket_timeout,
                socket_connect_timeout=self.config.socket_connect_timeout,
                decode_responses=True
            )
            
            # Test connection
            async with redis.Redis(connection_pool=self.pool) as client:
                await client.ping()
            
            self.is_initialized = True
            logger.info("Redis performance optimizer initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis optimizer: {e}")
            raise
    
    @asynccontextmanager
    async def get_client(self):
        """Get Redis client from pool."""
        if not self.is_initialized:
            await self.initialize()
        
        client = redis.Redis(connection_pool=self.pool)
        try:
            yield client
        finally:
            await client.close()
    
    async def set_with_strategy(
        self, 
        key: str, 
        value: Any, 
        strategy: str = "default",
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set cache value with specific strategy.
        
        Args:
            key: Cache key
            value: Value to cache
            strategy: Caching strategy (default, constitutional, policy, etc.)
            ttl: Time to live in seconds
            
        Returns:
            Success status
        """
        start_time = time.time()
        
        try:
            async with self.get_client() as client:
                # Apply strategy-specific processing
                processed_value = await self._apply_cache_strategy(value, strategy)
                serialized_value = json.dumps(processed_value, default=str)
                
                # Set with appropriate TTL
                strategy_ttl = ttl or self._get_strategy_ttl(strategy)
                
                if strategy_ttl:
                    result = await client.setex(key, strategy_ttl, serialized_value)
                else:
                    result = await client.set(key, serialized_value)
                
                self.metrics.sets += 1
                self.metrics.total_operations += 1
                
                logger.debug(f"Cache set: {key} (strategy: {strategy}, ttl: {strategy_ttl})")
                return bool(result)
                
        except Exception as e:
            self.metrics.errors += 1
            logger.error(f"Cache set failed for key {key}: {e}")
            return False
        finally:
            self._update_response_time(start_time)
    
    async def get_with_fallback(
        self, 
        key: str, 
        fallback_func: Optional[callable] = None,
        strategy: str = "default"
    ) -> Optional[Any]:
        """
        Get cache value with fallback function.
        
        Args:
            key: Cache key
            fallback_func: Function to call if cache miss
            strategy: Caching strategy
            
        Returns:
            Cached or computed value
        """
        start_time = time.time()
        
        try:
            async with self.get_client() as client:
                cached_value = await client.get(key)
                
                if cached_value is not None:
                    self.metrics.hits += 1
                    self.metrics.total_operations += 1
                    
                    try:
                        return json.loads(cached_value)
                    except json.JSONDecodeError:
                        return cached_value
                
                # Cache miss - use fallback if provided
                self.metrics.misses += 1
                self.metrics.total_operations += 1
                
                if fallback_func:
                    value = await fallback_func() if asyncio.iscoroutinefunction(fallback_func) else fallback_func()
                    
                    # Cache the computed value
                    await self.set_with_strategy(key, value, strategy)
                    return value
                
                return None
                
        except Exception as e:
            self.metrics.errors += 1
            logger.error(f"Cache get failed for key {key}: {e}")
            return None
        finally:
            self._update_response_time(start_time)
    
    async def batch_get(self, keys: List[str]) -> Dict[str, Any]:
        """
        Get multiple cache values in batch.
        
        Args:
            keys: List of cache keys
            
        Returns:
            Dictionary of key-value pairs
        """
        start_time = time.time()
        results = {}
        
        try:
            async with self.get_client() as client:
                values = await client.mget(keys)
                
                for key, value in zip(keys, values):
                    if value is not None:
                        try:
                            results[key] = json.loads(value)
                            self.metrics.hits += 1
                        except json.JSONDecodeError:
                            results[key] = value
                            self.metrics.hits += 1
                    else:
                        self.metrics.misses += 1
                
                self.metrics.total_operations += len(keys)
                
        except Exception as e:
            self.metrics.errors += 1
            logger.error(f"Batch get failed: {e}")
        finally:
            self._update_response_time(start_time)
        
        return results
    
    async def batch_set(self, data: Dict[str, Any], strategy: str = "default", ttl: Optional[int] = None) -> int:
        """
        Set multiple cache values in batch.
        
        Args:
            data: Dictionary of key-value pairs
            strategy: Caching strategy
            ttl: Time to live in seconds
            
        Returns:
            Number of successful sets
        """
        start_time = time.time()
        success_count = 0
        
        try:
            async with self.get_client() as client:
                pipe = client.pipeline()
                
                for key, value in data.items():
                    processed_value = await self._apply_cache_strategy(value, strategy)
                    serialized_value = json.dumps(processed_value, default=str)
                    
                    strategy_ttl = ttl or self._get_strategy_ttl(strategy)
                    
                    if strategy_ttl:
                        pipe.setex(key, strategy_ttl, serialized_value)
                    else:
                        pipe.set(key, serialized_value)
                
                results = await pipe.execute()
                success_count = sum(1 for result in results if result)
                
                self.metrics.sets += success_count
                self.metrics.total_operations += len(data)
                
        except Exception as e:
            self.metrics.errors += 1
            logger.error(f"Batch set failed: {e}")
        finally:
            self._update_response_time(start_time)
        
        return success_count
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate cache keys matching pattern.
        
        Args:
            pattern: Key pattern (supports wildcards)
            
        Returns:
            Number of keys deleted
        """
        start_time = time.time()
        deleted_count = 0
        
        try:
            async with self.get_client() as client:
                keys = await client.keys(pattern)
                
                if keys:
                    deleted_count = await client.delete(*keys)
                    self.metrics.deletes += deleted_count
                    self.metrics.total_operations += 1
                    
                    logger.info(f"Invalidated {deleted_count} keys matching pattern: {pattern}")
                
        except Exception as e:
            self.metrics.errors += 1
            logger.error(f"Pattern invalidation failed for {pattern}: {e}")
        finally:
            self._update_response_time(start_time)
        
        return deleted_count
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive cache statistics.
        
        Returns:
            Cache statistics and performance metrics
        """
        try:
            async with self.get_client() as client:
                info = await client.info()
                
                return {
                    "performance_metrics": asdict(self.metrics),
                    "redis_info": {
                        "connected_clients": info.get("connected_clients", 0),
                        "used_memory": info.get("used_memory_human", "unknown"),
                        "used_memory_peak": info.get("used_memory_peak_human", "unknown"),
                        "keyspace_hits": info.get("keyspace_hits", 0),
                        "keyspace_misses": info.get("keyspace_misses", 0),
                        "total_commands_processed": info.get("total_commands_processed", 0),
                        "instantaneous_ops_per_sec": info.get("instantaneous_ops_per_sec", 0)
                    },
                    "connection_pool": {
                        "max_connections": self.config.max_connections,
                        "created_connections": getattr(self.pool, "created_connections", 0),
                        "available_connections": getattr(self.pool, "available_connections", 0),
                        "in_use_connections": getattr(self.pool, "in_use_connections", 0)
                    }
                }
                
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {"error": str(e)}
    
    async def _apply_cache_strategy(self, value: Any, strategy: str) -> Any:
        """Apply strategy-specific processing to cache value."""
        if strategy == "constitutional":
            # Add constitutional metadata
            if isinstance(value, dict):
                value["cache_strategy"] = "constitutional"
                value["constitutional_hash"] = "cdd01ef066bc6cf2"
        elif strategy == "policy":
            # Add policy metadata
            if isinstance(value, dict):
                value["cache_strategy"] = "policy"
                value["policy_version"] = "v1.0"
        
        # Add common cache metadata
        if isinstance(value, dict):
            value["cached_at"] = time.time()
            value["cache_version"] = "1.0"
        
        return value
    
    def _get_strategy_ttl(self, strategy: str) -> int:
        """Get TTL for specific caching strategy."""
        strategy_ttls = {
            "constitutional": 3600,  # 1 hour for constitutional data
            "policy": 1800,          # 30 minutes for policy data
            "governance": 900,       # 15 minutes for governance actions
            "user": 600,             # 10 minutes for user data
            "default": 300           # 5 minutes default
        }
        return strategy_ttls.get(strategy, strategy_ttls["default"])
    
    def _update_response_time(self, start_time: float):
        """Update average response time metric."""
        response_time = time.time() - start_time
        
        # Calculate rolling average
        total_ops = self.metrics.total_operations
        if total_ops > 0:
            self.metrics.avg_response_time = (
                (self.metrics.avg_response_time * (total_ops - 1) + response_time) / total_ops
            )
        else:
            self.metrics.avg_response_time = response_time
    
    async def close(self):
        """Close Redis connection pool."""
        if self.pool:
            await self.pool.disconnect()
            logger.info("Redis connection pool closed")


# Global Redis optimizer instance
_redis_optimizer = None


async def get_redis_optimizer() -> RedisPerformanceOptimizer:
    """Get global Redis optimizer instance."""
    global _redis_optimizer
    
    if _redis_optimizer is None:
        _redis_optimizer = RedisPerformanceOptimizer()
        await _redis_optimizer.initialize()
    
    return _redis_optimizer


# Convenience functions for common operations
async def cache_constitutional_data(key: str, data: Any, ttl: Optional[int] = None) -> bool:
    """Cache constitutional governance data."""
    optimizer = await get_redis_optimizer()
    return await optimizer.set_with_strategy(key, data, "constitutional", ttl)


async def get_constitutional_data(key: str, fallback_func: Optional[callable] = None) -> Optional[Any]:
    """Get constitutional governance data from cache."""
    optimizer = await get_redis_optimizer()
    return await optimizer.get_with_fallback(key, fallback_func, "constitutional")


async def cache_policy_data(key: str, data: Any, ttl: Optional[int] = None) -> bool:
    """Cache policy data."""
    optimizer = await get_redis_optimizer()
    return await optimizer.set_with_strategy(key, data, "policy", ttl)


async def get_policy_data(key: str, fallback_func: Optional[callable] = None) -> Optional[Any]:
    """Get policy data from cache."""
    optimizer = await get_redis_optimizer()
    return await optimizer.get_with_fallback(key, fallback_func, "policy")
