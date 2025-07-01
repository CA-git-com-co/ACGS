#!/usr/bin/env python3
"""
Redis Cache Optimization for ACGS-2
Implements high-performance caching with >85% hit rate target
"""

import json
import time
import hashlib
import logging
from typing import Any, Dict, Optional, Union
from datetime import datetime, timedelta
import redis
import asyncio
from functools import wraps

logger = logging.getLogger(__name__)

class ACGSCacheManager:
    """High-performance cache manager for ACGS services."""
    
    def __init__(self, redis_host: str = "localhost", redis_port: int = 6379, redis_db: int = 0):
        """Initialize cache manager with Redis connection."""
        self.redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30
        )
        
        # Cache configuration for different data types
        self.cache_config = {
            "constitutional_compliance": {
                "ttl": 3600,  # 1 hour
                "prefix": "cc:",
                "max_size": 10000
            },
            "policy_validation": {
                "ttl": 1800,  # 30 minutes
                "prefix": "pv:",
                "max_size": 5000
            },
            "formal_verification": {
                "ttl": 7200,  # 2 hours
                "prefix": "fv:",
                "max_size": 3000
            },
            "governance_decisions": {
                "ttl": 900,   # 15 minutes
                "prefix": "gd:",
                "max_size": 2000
            },
            "user_sessions": {
                "ttl": 86400, # 24 hours
                "prefix": "us:",
                "max_size": 1000
            }
        }
        
        # Performance metrics
        self.metrics = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "errors": 0
        }
        
        # Initialize Redis optimizations
        self._optimize_redis_config()
    
    def _optimize_redis_config(self):
        """Apply Redis optimizations for high performance."""
        try:
            # Set memory policy for cache eviction
            self.redis_client.config_set("maxmemory-policy", "allkeys-lru")
            
            # Optimize for performance
            self.redis_client.config_set("tcp-keepalive", "60")
            self.redis_client.config_set("timeout", "0")
            
            # Enable keyspace notifications for cache monitoring
            self.redis_client.config_set("notify-keyspace-events", "Ex")
            
            logger.info("Redis cache optimizations applied successfully")
        except Exception as e:
            logger.error(f"Failed to apply Redis optimizations: {e}")
    
    def _generate_cache_key(self, cache_type: str, identifier: str) -> str:
        """Generate optimized cache key."""
        prefix = self.cache_config[cache_type]["prefix"]
        # Use SHA256 hash for consistent key length and avoid key collisions
        key_hash = hashlib.sha256(identifier.encode()).hexdigest()[:16]
        return f"{prefix}{key_hash}"
    
    def get(self, cache_type: str, identifier: str) -> Optional[Dict[str, Any]]:
        """Get item from cache with performance tracking."""
        try:
            cache_key = self._generate_cache_key(cache_type, identifier)
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                self.metrics["hits"] += 1
                data = json.loads(cached_data)
                
                # Check if data is still valid (additional TTL check)
                if "cached_at" in data:
                    cached_time = datetime.fromisoformat(data["cached_at"])
                    ttl = self.cache_config[cache_type]["ttl"]
                    if datetime.now() - cached_time > timedelta(seconds=ttl):
                        self.delete(cache_type, identifier)
                        self.metrics["misses"] += 1
                        return None
                
                return data
            else:
                self.metrics["misses"] += 1
                return None
                
        except Exception as e:
            self.metrics["errors"] += 1
            logger.error(f"Cache get error for {cache_type}:{identifier}: {e}")
            return None
    
    def set(self, cache_type: str, identifier: str, data: Dict[str, Any], 
            custom_ttl: Optional[int] = None) -> bool:
        """Set item in cache with optimization."""
        try:
            cache_key = self._generate_cache_key(cache_type, identifier)
            ttl = custom_ttl or self.cache_config[cache_type]["ttl"]
            
            # Add metadata
            cache_data = {
                **data,
                "cached_at": datetime.now().isoformat(),
                "cache_type": cache_type,
                "ttl": ttl
            }
            
            # Set with expiration
            success = self.redis_client.setex(
                cache_key, 
                ttl, 
                json.dumps(cache_data, default=str)
            )
            
            if success:
                self.metrics["sets"] += 1
                
                # Implement cache size management
                self._manage_cache_size(cache_type)
                
            return success
            
        except Exception as e:
            self.metrics["errors"] += 1
            logger.error(f"Cache set error for {cache_type}:{identifier}: {e}")
            return False
    
    def delete(self, cache_type: str, identifier: str) -> bool:
        """Delete item from cache."""
        try:
            cache_key = self._generate_cache_key(cache_type, identifier)
            result = self.redis_client.delete(cache_key)
            
            if result:
                self.metrics["deletes"] += 1
            
            return bool(result)
            
        except Exception as e:
            self.metrics["errors"] += 1
            logger.error(f"Cache delete error for {cache_type}:{identifier}: {e}")
            return False
    
    def _manage_cache_size(self, cache_type: str):
        """Manage cache size to prevent memory overflow."""
        try:
            prefix = self.cache_config[cache_type]["prefix"]
            max_size = self.cache_config[cache_type]["max_size"]
            
            # Get all keys for this cache type
            pattern = f"{prefix}*"
            keys = self.redis_client.keys(pattern)
            
            if len(keys) > max_size:
                # Remove oldest entries (LRU simulation)
                excess_count = len(keys) - max_size
                keys_to_remove = keys[:excess_count]
                
                if keys_to_remove:
                    self.redis_client.delete(*keys_to_remove)
                    logger.info(f"Removed {len(keys_to_remove)} excess cache entries for {cache_type}")
                    
        except Exception as e:
            logger.error(f"Cache size management error for {cache_type}: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        try:
            redis_info = self.redis_client.info()
            
            # Calculate hit rate
            total_requests = self.metrics["hits"] + self.metrics["misses"]
            hit_rate = (self.metrics["hits"] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                "performance_metrics": {
                    "hit_rate_percentage": round(hit_rate, 2),
                    "total_hits": self.metrics["hits"],
                    "total_misses": self.metrics["misses"],
                    "total_sets": self.metrics["sets"],
                    "total_deletes": self.metrics["deletes"],
                    "total_errors": self.metrics["errors"],
                    "total_requests": total_requests
                },
                "redis_metrics": {
                    "used_memory": redis_info.get("used_memory_human", "N/A"),
                    "connected_clients": redis_info.get("connected_clients", 0),
                    "total_commands_processed": redis_info.get("total_commands_processed", 0),
                    "keyspace_hits": redis_info.get("keyspace_hits", 0),
                    "keyspace_misses": redis_info.get("keyspace_misses", 0)
                },
                "cache_health": {
                    "status": "healthy" if self.metrics["errors"] < 10 else "degraded",
                    "target_hit_rate": 85.0,
                    "hit_rate_status": "excellent" if hit_rate >= 85 else "needs_improvement"
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"error": str(e)}
    
    def warm_cache(self, cache_type: str, data_loader_func, identifiers: list):
        """Warm cache with frequently accessed data."""
        try:
            warmed_count = 0
            for identifier in identifiers:
                if not self.get(cache_type, identifier):
                    data = data_loader_func(identifier)
                    if data and self.set(cache_type, identifier, data):
                        warmed_count += 1
            
            logger.info(f"Cache warming completed: {warmed_count} items loaded for {cache_type}")
            return warmed_count
            
        except Exception as e:
            logger.error(f"Cache warming error for {cache_type}: {e}")
            return 0
    
    def flush_cache_type(self, cache_type: str) -> int:
        """Flush all entries for a specific cache type."""
        try:
            prefix = self.cache_config[cache_type]["prefix"]
            pattern = f"{prefix}*"
            keys = self.redis_client.keys(pattern)
            
            if keys:
                deleted_count = self.redis_client.delete(*keys)
                logger.info(f"Flushed {deleted_count} entries for cache type: {cache_type}")
                return deleted_count
            
            return 0
            
        except Exception as e:
            logger.error(f"Error flushing cache type {cache_type}: {e}")
            return 0

# Global cache manager instance
cache_manager = ACGSCacheManager()

def cache_result(cache_type: str, ttl: Optional[int] = None, key_func: Optional[callable] = None):
    """Decorator for caching function results."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_type, cache_key)
            if cached_result and "result" in cached_result:
                return cached_result["result"]
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache_manager.set(cache_type, cache_key, {"result": result}, ttl)
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_type, cache_key)
            if cached_result and "result" in cached_result:
                return cached_result["result"]
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_type, cache_key, {"result": result}, ttl)
            
            return result
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
