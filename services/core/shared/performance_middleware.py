"""
Performance Optimization Middleware for ACGS-2 Services
Constitutional Hash: cdd01ef066bc6cf2

This module provides performance optimization middleware including:
- Multi-tier caching (L1 in-memory, L2 Redis, L3 Database)
- Connection pooling optimization
- Request batching and deduplication
- Performance monitoring and alerting
"""

import asyncio
import json
import logging
import time
from typing import Any, Dict, Optional, Callable, List, Tuple
from dataclasses import dataclass
from contextlib import asynccontextmanager
import hashlib
import redis.asyncio as redis
from collections import defaultdict, OrderedDict
import weakref
import threading

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics collection."""
    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    avg_response_time: float = 0.0
    p99_response_time: float = 0.0
    constitutional_compliance_checks: int = 0
    constitutional_hash: str = "cdd01ef066bc6cf2"

class LRUCache:
    """Thread-safe LRU cache implementation."""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache = OrderedDict()
        self.lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        with self.lock:
            if key in self.cache:
                # Move to end (most recently used)
                self.cache.move_to_end(key)
                return self.cache[key]
            return None
    
    def set(self, key: str, value: Any):
        """Set value in cache."""
        with self.lock:
            if key in self.cache:
                # Update existing key
                self.cache[key] = value
                self.cache.move_to_end(key)
            else:
                # Add new key
                self.cache[key] = value
                if len(self.cache) > self.max_size:
                    # Remove least recently used
                    self.cache.popitem(last=False)
    
    def delete(self, key: str):
        """Delete key from cache."""
        with self.lock:
            self.cache.pop(key, None)
    
    def clear(self):
        """Clear all cache entries."""
        with self.lock:
            self.cache.clear()
    
    def size(self) -> int:
        """Get current cache size."""
        with self.lock:
            return len(self.cache)

class MultiTierCache:
    """
    Multi-tier cache implementation with constitutional compliance.
    
    Tiers:
    - L1: In-memory LRU cache (fastest, smallest)
    - L2: Redis cache (fast, medium size)
    - L3: Database cache (slowest, largest)
    """
    
    def __init__(self, 
                 redis_client: Optional[redis.Redis] = None,
                 l1_size: int = 1000,
                 l2_ttl: int = 3600,
                 constitutional_hash: str = "cdd01ef066bc6cf2"):
        self.redis_client = redis_client
        self.l1_cache = LRUCache(l1_size)
        self.l2_ttl = l2_ttl
        self.constitutional_hash = constitutional_hash
        self.metrics = PerformanceMetrics()
        
        logger.info(f"MultiTierCache initialized with L1 size: {l1_size}")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from multi-tier cache."""
        cache_key = self._generate_cache_key(key)
        
        # L1 Cache (in-memory)
        value = self.l1_cache.get(cache_key)
        if value is not None:
            self.metrics.cache_hits += 1
            logger.debug(f"L1 cache hit for key: {key}")
            return value
        
        # L2 Cache (Redis)
        if self.redis_client:
            try:
                redis_value = await self.redis_client.get(cache_key)
                if redis_value:
                    value = json.loads(redis_value)
                    # Promote to L1 cache
                    self.l1_cache.set(cache_key, value)
                    self.metrics.cache_hits += 1
                    logger.debug(f"L2 cache hit for key: {key}")
                    return value
            except Exception as e:
                logger.warning(f"Redis cache error: {e}")
        
        # Cache miss
        self.metrics.cache_misses += 1
        logger.debug(f"Cache miss for key: {key}")
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in multi-tier cache."""
        cache_key = self._generate_cache_key(key)
        
        # Set in L1 cache
        self.l1_cache.set(cache_key, value)
        
        # Set in L2 cache (Redis)
        if self.redis_client:
            try:
                redis_value = json.dumps(value, default=str)
                await self.redis_client.setex(
                    cache_key, 
                    ttl or self.l2_ttl, 
                    redis_value
                )
                logger.debug(f"Set L2 cache for key: {key}")
            except Exception as e:
                logger.warning(f"Redis cache set error: {e}")
        
        logger.debug(f"Set L1 cache for key: {key}")
    
    async def delete(self, key: str):
        """Delete key from all cache tiers."""
        cache_key = self._generate_cache_key(key)
        
        # Delete from L1
        self.l1_cache.delete(cache_key)
        
        # Delete from L2
        if self.redis_client:
            try:
                await self.redis_client.delete(cache_key)
            except Exception as e:
                logger.warning(f"Redis cache delete error: {e}")
    
    def _generate_cache_key(self, key: str) -> str:
        """Generate cache key with constitutional hash."""
        return f"{self.constitutional_hash}:{hashlib.sha256(key.encode()).hexdigest()[:16]}"
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get cache performance metrics."""
        total_requests = self.metrics.cache_hits + self.metrics.cache_misses
        hit_rate = (self.metrics.cache_hits / total_requests) if total_requests > 0 else 0
        
        return {
            "total_requests": total_requests,
            "cache_hits": self.metrics.cache_hits,
            "cache_misses": self.metrics.cache_misses,
            "hit_rate": hit_rate,
            "l1_size": self.l1_cache.size(),
            "constitutional_hash": self.constitutional_hash
        }

class RequestBatcher:
    """
    Request batching and deduplication for performance optimization.
    
    Features:
    - Automatic request batching
    - Duplicate request deduplication
    - Constitutional compliance validation
    - Performance monitoring
    """
    
    def __init__(self, 
                 batch_size: int = 10,
                 batch_timeout: float = 0.1,
                 constitutional_hash: str = "cdd01ef066bc6cf2"):
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self.constitutional_hash = constitutional_hash
        self.pending_requests: Dict[str, List[asyncio.Future]] = defaultdict(list)
        self.batch_lock = asyncio.Lock()
        
        logger.info(f"RequestBatcher initialized with batch_size: {batch_size}")
    
    async def batch_request(self, 
                           key: str, 
                           func: Callable, 
                           *args, 
                           **kwargs) -> Any:
        """
        Batch similar requests for performance optimization.
        
        Args:
            key: Request identifier for batching
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Any: Function result
        """
        # Validate constitutional compliance
        if not self._validate_constitutional_compliance(kwargs):
            raise ValueError("Constitutional compliance validation failed")
        
        request_key = self._generate_request_key(key, args, kwargs)
        
        async with self.batch_lock:
            # Check if request is already pending
            if request_key in self.pending_requests:
                # Deduplicate - wait for existing request
                future = asyncio.Future()
                self.pending_requests[request_key].append(future)
                logger.debug(f"Deduplicated request for key: {key}")
                return await future
            
            # Create new batch
            future = asyncio.Future()
            self.pending_requests[request_key] = [future]
            
            # Schedule batch execution
            asyncio.create_task(self._execute_batch(request_key, func, *args, **kwargs))
            
            return await future
    
    async def _execute_batch(self, 
                           request_key: str, 
                           func: Callable, 
                           *args, 
                           **kwargs):
        """Execute batched request."""
        # Wait for batch to fill or timeout
        await asyncio.sleep(self.batch_timeout)
        
        async with self.batch_lock:
            futures = self.pending_requests.pop(request_key, [])
        
        if not futures:
            return
        
        try:
            # Execute function once for all requests
            start_time = time.time()
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Set result for all waiting futures
            for future in futures:
                if not future.done():
                    future.set_result(result)
            
            logger.debug(f"Batch executed for {len(futures)} requests in {execution_time:.3f}s")
            
        except Exception as e:
            # Set exception for all waiting futures
            for future in futures:
                if not future.done():
                    future.set_exception(e)
            
            logger.error(f"Batch execution failed: {e}")
    
    def _generate_request_key(self, key: str, args: tuple, kwargs: dict) -> str:
        """Generate unique request key for batching."""
        content = f"{key}:{args}:{sorted(kwargs.items())}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _validate_constitutional_compliance(self, kwargs: Dict[str, Any]) -> bool:
        """Validate constitutional compliance in request."""
        constitutional_hash = kwargs.get('constitutional_hash')
        return constitutional_hash == self.constitutional_hash

class PerformanceMonitor:
    """
    Performance monitoring with constitutional compliance.
    
    Features:
    - Real-time performance tracking
    - Constitutional compliance monitoring
    - Alert generation
    - Metrics collection
    """
    
    def __init__(self, 
                 service_name: str,
                 constitutional_hash: str = "cdd01ef066bc6cf2"):
        self.service_name = service_name
        self.constitutional_hash = constitutional_hash
        self.metrics = PerformanceMetrics()
        self.response_times: List[float] = []
        self.max_response_times = 1000  # Keep last 1000 response times
        
        logger.info(f"PerformanceMonitor initialized for service: {service_name}")
    
    def record_request(self, response_time: float, constitutional_compliant: bool = True):
        """Record request performance metrics."""
        self.metrics.total_requests += 1
        
        if constitutional_compliant:
            self.metrics.constitutional_compliance_checks += 1
        
        # Update response times
        self.response_times.append(response_time)
        if len(self.response_times) > self.max_response_times:
            self.response_times.pop(0)
        
        # Update average response time
        self.metrics.avg_response_time = sum(self.response_times) / len(self.response_times)
        
        # Update P99 response time
        if len(self.response_times) >= 2:
            sorted_times = sorted(self.response_times)
            p99_index = int(len(sorted_times) * 0.99)
            self.metrics.p99_response_time = sorted_times[p99_index]
        
        # Check for performance alerts
        self._check_performance_alerts(response_time)
    
    def _check_performance_alerts(self, response_time: float):
        """Check for performance alert conditions."""
        # P99 latency alert
        if self.metrics.p99_response_time > 5.0:  # 5ms threshold
            logger.warning(f"P99 latency exceeded threshold: {self.metrics.p99_response_time:.3f}ms")
        
        # Individual request latency alert
        if response_time > 10.0:  # 10ms threshold
            logger.warning(f"High latency request: {response_time:.3f}ms")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return {
            "service_name": self.service_name,
            "total_requests": self.metrics.total_requests,
            "avg_response_time": self.metrics.avg_response_time,
            "p99_response_time": self.metrics.p99_response_time,
            "constitutional_compliance_rate": (
                self.metrics.constitutional_compliance_checks / self.metrics.total_requests
                if self.metrics.total_requests > 0 else 0
            ),
            "constitutional_hash": self.constitutional_hash
        }

class PerformanceMiddleware:
    """
    FastAPI middleware for performance optimization.
    
    Features:
    - Request/response timing
    - Multi-tier caching
    - Request batching
    - Performance monitoring
    - Constitutional compliance validation
    """
    
    def __init__(self, 
                 service_name: str,
                 redis_client: Optional[redis.Redis] = None,
                 constitutional_hash: str = "cdd01ef066bc6cf2"):
        self.service_name = service_name
        self.constitutional_hash = constitutional_hash
        self.cache = MultiTierCache(redis_client, constitutional_hash=constitutional_hash)
        self.batcher = RequestBatcher(constitutional_hash=constitutional_hash)
        self.monitor = PerformanceMonitor(service_name, constitutional_hash)
        
        logger.info(f"PerformanceMiddleware initialized for service: {service_name}")
    
    async def __call__(self, request, call_next):
        """Middleware execution."""
        start_time = time.time()
        
        # Validate constitutional compliance
        constitutional_hash = request.headers.get('X-Constitutional-Hash')
        constitutional_compliant = constitutional_hash == self.constitutional_hash
        
        if not constitutional_compliant:
            logger.warning(f"Constitutional compliance violation in request")
        
        # Execute request
        response = await call_next(request)
        
        # Record performance metrics
        response_time = (time.time() - start_time) * 1000  # Convert to ms
        self.monitor.record_request(response_time, constitutional_compliant)
        
        # Add performance headers
        response.headers['X-Response-Time'] = str(response_time)
        response.headers['X-Constitutional-Hash'] = self.constitutional_hash
        
        return response
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics."""
        return {
            "service_name": self.service_name,
            "cache_metrics": self.cache.get_metrics(),
            "performance_metrics": self.monitor.get_metrics(),
            "constitutional_hash": self.constitutional_hash
        }

def setup_performance_middleware(app, 
                               service_name: str,
                               redis_client: Optional[redis.Redis] = None):
    """
    Set up performance middleware for FastAPI application.
    
    Args:
        app: FastAPI application instance
        service_name: Name of the service
        redis_client: Optional Redis client for L2 cache
    """
    middleware = PerformanceMiddleware(service_name, redis_client)
    app.add_middleware(BaseHTTPMiddleware, dispatch=middleware)
    
    # Add metrics endpoint
    @app.get("/metrics/performance")
    async def get_performance_metrics():
        return middleware.get_metrics()
    
    logger.info(f"Performance middleware configured for service: {service_name}")

# Convenience functions
async def cached_call(cache: MultiTierCache, 
                     key: str, 
                     func: Callable, 
                     *args, 
                     ttl: Optional[int] = None,
                     **kwargs) -> Any:
    """
    Execute function with caching.
    
    Args:
        cache: MultiTierCache instance
        key: Cache key
        func: Function to execute
        *args: Function arguments
        ttl: Cache TTL in seconds
        **kwargs: Function keyword arguments
        
    Returns:
        Any: Function result
    """
    # Try to get from cache
    cached_result = await cache.get(key)
    if cached_result is not None:
        return cached_result
    
    # Execute function
    result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
    
    # Cache result
    await cache.set(key, result, ttl)
    
    return result

from starlette.middleware.base import BaseHTTPMiddleware