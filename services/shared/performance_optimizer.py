"""
ACGS-1 Performance Optimizer

Comprehensive performance optimization service for all 7 core services.
Implements caching, connection pooling, async optimization, and monitoring
to achieve <50ms response times and 99.5% uptime requirements.

Key Features:
- Intelligent caching with Redis
- Database connection optimization
- Async operation batching
- Memory usage optimization
- Response time monitoring
- Circuit breaker integration
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Callable, Union
import hashlib
import json

from .redis_cache import RedisCache
from .database.pool_manager import get_pool_manager
from .service_mesh.circuit_breaker import get_circuit_breaker_manager

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics tracking."""
    
    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    avg_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0
    error_rate: float = 0.0
    memory_usage_mb: float = 0.0
    
    @property
    def cache_hit_rate(self) -> float:
        """Calculate cache hit rate percentage."""
        total_cache_requests = self.cache_hits + self.cache_misses
        return (self.cache_hits / max(total_cache_requests, 1)) * 100


class AsyncBatchProcessor:
    """Batch processor for async operations to improve throughput."""
    
    def __init__(self, batch_size: int = 10, max_wait_time: float = 0.1):
        self.batch_size = batch_size
        self.max_wait_time = max_wait_time
        self.pending_operations: List[Dict[str, Any]] = []
        self.batch_lock = asyncio.Lock()
        
    async def add_operation(self, operation: Callable, *args, **kwargs) -> Any:
        """Add operation to batch queue."""
        future = asyncio.Future()
        
        async with self.batch_lock:
            self.pending_operations.append({
                'operation': operation,
                'args': args,
                'kwargs': kwargs,
                'future': future,
                'timestamp': time.time()
            })
            
            # Process batch if size threshold reached or timeout exceeded
            if (len(self.pending_operations) >= self.batch_size or 
                (self.pending_operations and 
                 time.time() - self.pending_operations[0]['timestamp'] > self.max_wait_time)):
                await self._process_batch()
        
        return await future
    
    async def _process_batch(self):
        """Process pending operations in batch."""
        if not self.pending_operations:
            return
            
        batch = self.pending_operations.copy()
        self.pending_operations.clear()
        
        # Execute operations concurrently
        tasks = []
        for item in batch:
            task = asyncio.create_task(
                self._execute_operation(item['operation'], item['args'], item['kwargs'])
            )
            tasks.append((task, item['future']))
        
        # Wait for all operations to complete
        for task, future in tasks:
            try:
                result = await task
                future.set_result(result)
            except Exception as e:
                future.set_exception(e)
    
    async def _execute_operation(self, operation: Callable, args: tuple, kwargs: dict) -> Any:
        """Execute individual operation."""
        if asyncio.iscoroutinefunction(operation):
            return await operation(*args, **kwargs)
        else:
            return operation(*args, **kwargs)


class IntelligentCache:
    """Intelligent caching system with TTL and invalidation strategies."""
    
    def __init__(self, redis_cache: RedisCache):
        self.redis_cache = redis_cache
        self.local_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_stats = {"hits": 0, "misses": 0, "invalidations": 0}
        
    def _generate_cache_key(self, service: str, operation: str, params: Dict[str, Any]) -> str:
        """Generate consistent cache key."""
        key_data = f"{service}:{operation}:{json.dumps(params, sort_keys=True)}"
        return hashlib.sha256(key_data.encode()).hexdigest()[:16]
    
    async def get(self, service: str, operation: str, params: Dict[str, Any]) -> Optional[Any]:
        """Get cached result."""
        cache_key = self._generate_cache_key(service, operation, params)
        
        # Try local cache first (fastest)
        if cache_key in self.local_cache:
            cache_entry = self.local_cache[cache_key]
            if time.time() < cache_entry['expires_at']:
                self.cache_stats["hits"] += 1
                return cache_entry['data']
            else:
                del self.local_cache[cache_key]
        
        # Try Redis cache
        try:
            cached_data = await self.redis_cache.get(cache_key)
            if cached_data:
                self.cache_stats["hits"] += 1
                # Store in local cache for faster access
                self.local_cache[cache_key] = {
                    'data': cached_data,
                    'expires_at': time.time() + 60  # 1 minute local cache
                }
                return cached_data
        except Exception as e:
            logger.warning(f"Redis cache error: {e}")
        
        self.cache_stats["misses"] += 1
        return None
    
    async def set(self, service: str, operation: str, params: Dict[str, Any], 
                  data: Any, ttl: int = 300) -> None:
        """Set cached result."""
        cache_key = self._generate_cache_key(service, operation, params)
        
        # Store in Redis
        try:
            await self.redis_cache.set(cache_key, data, ttl)
        except Exception as e:
            logger.warning(f"Redis cache set error: {e}")
        
        # Store in local cache
        self.local_cache[cache_key] = {
            'data': data,
            'expires_at': time.time() + min(ttl, 300)  # Max 5 minutes local cache
        }
    
    async def invalidate_pattern(self, pattern: str) -> None:
        """Invalidate cache entries matching pattern."""
        try:
            await self.redis_cache.delete_pattern(pattern)
            # Clear local cache entries matching pattern
            keys_to_remove = [k for k in self.local_cache.keys() if pattern in k]
            for key in keys_to_remove:
                del self.local_cache[key]
            self.cache_stats["invalidations"] += len(keys_to_remove)
        except Exception as e:
            logger.warning(f"Cache invalidation error: {e}")


class PerformanceOptimizer:
    """Main performance optimization service."""
    
    def __init__(self):
        self.redis_cache = RedisCache()
        self.intelligent_cache = IntelligentCache(self.redis_cache)
        self.batch_processor = AsyncBatchProcessor()
        self.pool_manager = get_pool_manager()
        self.circuit_breaker_manager = get_circuit_breaker_manager()
        self.metrics = PerformanceMetrics()
        self.response_times: List[float] = []
        
    async def initialize(self):
        """Initialize performance optimizer."""
        try:
            await self.redis_cache.initialize()
            logger.info("✅ Performance Optimizer initialized successfully")
        except Exception as e:
            logger.error(f"❌ Performance Optimizer initialization failed: {e}")
            raise
    
    @asynccontextmanager
    async def optimized_operation(self, service_name: str, operation_name: str):
        """Context manager for optimized operations with monitoring."""
        start_time = time.time()
        circuit_breaker = self.circuit_breaker_manager.get_circuit_breaker(
            f"{service_name}_{operation_name}"
        )
        
        if not circuit_breaker.can_execute():
            raise Exception(f"Circuit breaker open for {service_name}_{operation_name}")
        
        try:
            yield
            # Record success
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            self._record_success(response_time)
            circuit_breaker.record_success()
            
        except Exception as e:
            # Record failure
            response_time = (time.time() - start_time) * 1000
            self._record_failure(response_time)
            circuit_breaker.record_failure()
            raise
    
    async def cached_operation(self, service: str, operation: str, params: Dict[str, Any],
                             operation_func: Callable, ttl: int = 300) -> Any:
        """Execute operation with intelligent caching."""
        # Try cache first
        cached_result = await self.intelligent_cache.get(service, operation, params)
        if cached_result is not None:
            return cached_result
        
        # Execute operation
        async with self.optimized_operation(service, operation):
            result = await operation_func()
            
            # Cache result
            await self.intelligent_cache.set(service, operation, params, result, ttl)
            return result
    
    async def batch_database_operations(self, operations: List[Callable]) -> List[Any]:
        """Execute database operations in optimized batches."""
        results = []
        for operation in operations:
            result = await self.batch_processor.add_operation(operation)
            results.append(result)
        return results
    
    def _record_success(self, response_time: float):
        """Record successful operation metrics."""
        self.metrics.total_requests += 1
        self.response_times.append(response_time)
        
        # Keep only last 1000 response times for percentile calculation
        if len(self.response_times) > 1000:
            self.response_times = self.response_times[-1000:]
        
        # Update metrics
        self.metrics.avg_response_time = sum(self.response_times) / len(self.response_times)
        if len(self.response_times) >= 20:  # Need sufficient data for percentiles
            sorted_times = sorted(self.response_times)
            self.metrics.p95_response_time = sorted_times[int(len(sorted_times) * 0.95)]
            self.metrics.p99_response_time = sorted_times[int(len(sorted_times) * 0.99)]
    
    def _record_failure(self, response_time: float):
        """Record failed operation metrics."""
        self.metrics.total_requests += 1
        # Don't include failed operations in response time averages
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report."""
        cache_stats = self.intelligent_cache.cache_stats
        
        return {
            "performance_metrics": {
                "total_requests": self.metrics.total_requests,
                "avg_response_time_ms": round(self.metrics.avg_response_time, 2),
                "p95_response_time_ms": round(self.metrics.p95_response_time, 2),
                "p99_response_time_ms": round(self.metrics.p99_response_time, 2),
                "meets_50ms_target": self.metrics.p95_response_time < 50.0,
            },
            "cache_performance": {
                "hit_rate_percent": round(
                    (cache_stats["hits"] / max(cache_stats["hits"] + cache_stats["misses"], 1)) * 100, 2
                ),
                "total_hits": cache_stats["hits"],
                "total_misses": cache_stats["misses"],
                "invalidations": cache_stats["invalidations"],
            },
            "circuit_breaker_status": self.circuit_breaker_manager.get_all_status(),
            "database_pool_metrics": self.pool_manager.get_all_metrics(),
            "recommendations": self._generate_recommendations(),
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate performance optimization recommendations."""
        recommendations = []
        
        if self.metrics.p95_response_time > 50.0:
            recommendations.append("Response times exceed 50ms target - consider caching optimization")
        
        cache_hit_rate = self.intelligent_cache.cache_stats["hits"] / max(
            self.intelligent_cache.cache_stats["hits"] + self.intelligent_cache.cache_stats["misses"], 1
        ) * 100
        
        if cache_hit_rate < 80.0:
            recommendations.append("Cache hit rate below 80% - review caching strategy")
        
        unhealthy_services = self.circuit_breaker_manager.get_unhealthy_services()
        if unhealthy_services:
            recommendations.append(f"Circuit breakers open for: {', '.join(unhealthy_services)}")
        
        return recommendations


# Global performance optimizer instance
_performance_optimizer: Optional[PerformanceOptimizer] = None


def get_performance_optimizer() -> PerformanceOptimizer:
    """Get global performance optimizer instance."""
    global _performance_optimizer
    
    if _performance_optimizer is None:
        _performance_optimizer = PerformanceOptimizer()
    
    return _performance_optimizer
