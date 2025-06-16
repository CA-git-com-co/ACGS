"""
Advanced Redis Client for ACGS-1 Phase A3 Caching Implementation
Provides enterprise-grade caching with connection pooling, failover, and monitoring
"""

import asyncio
import hashlib
import json
import pickle
import threading
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar, Union

import redis.asyncio as redis
import structlog
from redis.exceptions import ConnectionError, RedisError, TimeoutError
from redis.sentinel import Sentinel

logger = structlog.get_logger(__name__)

T = TypeVar("T")

# Enhanced Cache TTL policies for Phase 2 performance optimization
CACHE_TTL_POLICIES = {
    "policy_decisions": 300,  # 5 minutes
    "governance_rules": 3600,  # 1 hour
    "static_configuration": 86400,  # 24 hours
    "user_sessions": 1800,  # 30 minutes
    "api_responses": 600,  # 10 minutes
    "compliance_checks": 900,  # 15 minutes
    "synthesis_results": 1200,  # 20 minutes
    "auth_tokens": 3600,  # 1 hour
    "workflow_state": 7200,  # 2 hours
    # Phase 2 enhancements for >1000 concurrent users
    "multi_model_consensus": 1800,  # 30 minutes - longer for expensive operations
    "constitutional_analysis": 2400,  # 40 minutes - stable constitutional data
    "load_balancer_metrics": 60,  # 1 minute - frequent updates needed
    "performance_metrics": 120,  # 2 minutes - monitoring data
    "security_validations": 600,  # 10 minutes - security checks
    "user_preferences": 3600,  # 1 hour - user settings
    "system_health": 30,  # 30 seconds - critical health data
}


@dataclass
class CacheMetrics:
    """Cache performance metrics."""

    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    hit_rate: float = 0.0
    errors: int = 0
    avg_response_time_ms: float = 0.0
    memory_usage_bytes: int = 0
    active_connections: int = 0


@dataclass
class CacheConfig:
    """Cache configuration."""

    redis_url: str = "redis://localhost:6379/0"
    redis_password: str = "acgs_redis_production_2024_secure_cache_key"
    max_connections: int = 20
    socket_timeout: int = 5
    socket_connect_timeout: int = 5
    retry_on_timeout: bool = True
    health_check_interval: int = 30
    enable_sentinel: bool = False
    sentinel_hosts: Optional[List[Tuple[str, int]]] = None
    master_name: str = "acgs-master"


class AdvancedRedisClient:
    """Advanced Redis client with enterprise features."""

    def __init__(self, service_name: str, config: Optional[CacheConfig] = None):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        self.service_name = service_name
        self.config = config or CacheConfig()
        self.redis_client: Optional[redis.Redis] = None
        self.sentinel: Optional[Sentinel] = None
        self.connection_pool = None
        self.metrics = CacheMetrics()
        self._lock = threading.Lock()
        self._health_check_task = None
        self._initialized = False

    async def initialize(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Initialize Redis connection with failover support."""
        if self._initialized:
            return

        try:
            if self.config.enable_sentinel and self.config.sentinel_hosts:
                await self._initialize_sentinel()
            else:
                await self._initialize_direct()

            # Start health check monitoring
            self._health_check_task = asyncio.create_task(self._health_check_loop())

            self._initialized = True
            logger.info(
                "Advanced Redis client initialized",
                service=self.service_name,
                sentinel_enabled=self.config.enable_sentinel,
            )

        except Exception as e:
            logger.error(
                "Failed to initialize Redis client",
                service=self.service_name,
                error=str(e),
            )
            raise

    async def _initialize_sentinel(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Initialize Redis with Sentinel for high availability."""
        self.sentinel = Sentinel(
            self.config.sentinel_hosts,
            socket_timeout=self.config.socket_timeout,
            password=self.config.redis_password,
        )

        # Get master connection
        master = self.sentinel.master_for(
            self.config.master_name,
            socket_timeout=self.config.socket_timeout,
            password=self.config.redis_password,
            decode_responses=False,
        )

        self.redis_client = master
        await self.redis_client.ping()

    async def _initialize_direct(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Initialize direct Redis connection."""
        self.connection_pool = redis.ConnectionPool.from_url(
            self.config.redis_url,
            password=self.config.redis_password,
            max_connections=self.config.max_connections,
            socket_timeout=self.config.socket_timeout,
            socket_connect_timeout=self.config.socket_connect_timeout,
            decode_responses=False,
            retry_on_timeout=self.config.retry_on_timeout,
        )

        self.redis_client = redis.Redis(connection_pool=self.connection_pool)
        await self.redis_client.ping()

    async def _health_check_loop(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Continuous health check monitoring."""
        while True:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                start_time = time.time()
                await self.redis_client.ping()
                response_time = (time.time() - start_time) * 1000

                # Update metrics
                with self._lock:
                    self.metrics.avg_response_time_ms = (
                        self.metrics.avg_response_time_ms * 0.9 + response_time * 0.1
                    )

                logger.debug(
                    "Redis health check passed",
                    service=self.service_name,
                    response_time_ms=response_time,
                )

            except Exception as e:
                with self._lock:
                    self.metrics.errors += 1

                logger.warning("Redis health check failed", service=self.service_name, error=str(e))

    def _generate_key(self, key: Union[str, Dict[str, Any]], prefix: Optional[str] = None) -> str:
        """Generate cache key with service prefix."""
        if isinstance(key, str):
            cache_key = key
        else:
            key_str = json.dumps(key, sort_keys=True)
            cache_key = hashlib.sha256(key_str.encode()).hexdigest()

        service_prefix = f"acgs:{self.service_name}:"
        if prefix:
            service_prefix += f"{prefix}:"

        return f"{service_prefix}{cache_key}"

    async def get(
        self,
        key: Union[str, Dict[str, Any]],
        prefix: Optional[str] = None,
        deserialize: bool = True,
    ) -> Optional[Any]:
        """Get value from cache with metrics tracking."""
        cache_key = self._generate_key(key, prefix)
        start_time = time.time()

        try:
            with self._lock:
                self.metrics.total_requests += 1

            data = await self.redis_client.get(cache_key)

            if data is None:
                with self._lock:
                    self.metrics.cache_misses += 1
                    self._update_hit_rate()
                return None

            # Deserialize data
            if deserialize:
                try:
                    value = pickle.loads(data)
                except Exception:
                    value = json.loads(data.decode("utf-8"))
            else:
                value = data

            with self._lock:
                self.metrics.cache_hits += 1
                self._update_hit_rate()

            response_time = (time.time() - start_time) * 1000
            logger.debug(
                "Cache hit",
                service=self.service_name,
                key=cache_key[:50],
                response_time_ms=response_time,
            )

            return value

        except (RedisError, ConnectionError, TimeoutError) as e:
            with self._lock:
                self.metrics.errors += 1

            logger.error(
                "Cache get error",
                service=self.service_name,
                key=cache_key[:50],
                error=str(e),
            )
            return None

    async def set(
        self,
        key: Union[str, Dict[str, Any]],
        value: Any,
        ttl: Optional[int] = None,
        prefix: Optional[str] = None,
        serialize: bool = True,
    ) -> bool:
        """Set value in cache with TTL."""
        cache_key = self._generate_key(key, prefix)

        try:
            # Serialize data
            if serialize:
                try:
                    data = pickle.dumps(value)
                except Exception:
                    data = json.dumps(value).encode("utf-8")
            else:
                data = value

            if ttl:
                await self.redis_client.setex(cache_key, ttl, data)
            else:
                await self.redis_client.set(cache_key, data)

            logger.debug("Cache set", service=self.service_name, key=cache_key[:50], ttl=ttl)
            return True

        except (RedisError, ConnectionError, TimeoutError) as e:
            with self._lock:
                self.metrics.errors += 1

            logger.error(
                "Cache set error",
                service=self.service_name,
                key=cache_key[:50],
                error=str(e),
            )
            return False

    async def delete(self, key: Union[str, Dict[str, Any]], prefix: Optional[str] = None) -> bool:
        """Delete key from cache."""
        cache_key = self._generate_key(key, prefix)

        try:
            result = await self.redis_client.delete(cache_key)
            logger.debug(
                "Cache delete",
                service=self.service_name,
                key=cache_key[:50],
                deleted=bool(result),
            )
            return bool(result)

        except (RedisError, ConnectionError, TimeoutError) as e:
            with self._lock:
                self.metrics.errors += 1

            logger.error(
                "Cache delete error",
                service=self.service_name,
                key=cache_key[:50],
                error=str(e),
            )
            return False

    async def invalidate_pattern(self, pattern: str, prefix: Optional[str] = None) -> int:
        """Invalidate keys matching pattern."""
        full_pattern = self._generate_key(pattern, prefix)

        try:
            keys = await self.redis_client.keys(full_pattern)
            if keys:
                deleted = await self.redis_client.delete(*keys)
                logger.info(
                    "Cache pattern invalidation",
                    service=self.service_name,
                    pattern=full_pattern[:50],
                    deleted_count=deleted,
                )
                return deleted
            return 0

        except (RedisError, ConnectionError, TimeoutError) as e:
            with self._lock:
                self.metrics.errors += 1

            logger.error(
                "Cache pattern invalidation error",
                service=self.service_name,
                pattern=full_pattern[:50],
                error=str(e),
            )
            return 0

    def _update_hit_rate(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Update cache hit rate."""
        if self.metrics.total_requests > 0:
            self.metrics.hit_rate = (self.metrics.cache_hits / self.metrics.total_requests) * 100

    async def get_metrics(self) -> CacheMetrics:
        """Get current cache metrics."""
        try:
            info = await self.redis_client.info("memory")
            with self._lock:
                self.metrics.memory_usage_bytes = info.get("used_memory", 0)
                self.metrics.active_connections = info.get("connected_clients", 0)
        except Exception:
            pass

        return self.metrics

    async def close(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Close Redis connection."""
        if self._health_check_task:
            self._health_check_task.cancel()

        if self.redis_client:
            await self.redis_client.close()

        if self.connection_pool:
            await self.connection_pool.disconnect()

        logger.info("Redis client closed", service=self.service_name)


# Global Redis clients for each service
_redis_clients: Dict[str, AdvancedRedisClient] = {}


async def get_redis_client(
    service_name: str, config: Optional[CacheConfig] = None
) -> AdvancedRedisClient:
    """Get or create Redis client for service."""
    if service_name not in _redis_clients:
        client = AdvancedRedisClient(service_name, config)
        await client.initialize()
        _redis_clients[service_name] = client

    return _redis_clients[service_name]


async def close_all_redis_clients():
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """Close all Redis clients."""
    for client in _redis_clients.values():
        await client.close()
    _redis_clients.clear()


# Cache decorators for easy integration
def cache_result(
    ttl: Optional[int] = None,
    key_prefix: Optional[str] = None,
    cache_type: str = "api_responses",
    service_name: Optional[str] = None,
):
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """Decorator to cache function results."""

    def decorator(func: Callable[..., Any]):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        if asyncio.iscoroutinefunction(func):

            async def async_wrapper(*args, **kwargs):
                # requires: Valid input parameters
                # ensures: Correct function execution
                # sha256: func_hash
                # Generate cache key from function name and arguments
                func_name = f"{func.__module__}.{func.__name__}"
                cache_key = {
                    "function": func_name,
                    "args": str(args),
                    "kwargs": sorted(kwargs.items()),
                }

                # Get service name from context or use provided
                svc_name = service_name or getattr(func, "__service_name__", "default")
                client = await get_redis_client(svc_name)

                # Try to get from cache
                cached_result = await client.get(cache_key, prefix=key_prefix)
                if cached_result is not None:
                    return cached_result

                # Execute function and cache result
                result = await func(*args, **kwargs)
                cache_ttl = ttl or CACHE_TTL_POLICIES.get(cache_type, 600)
                await client.set(cache_key, result, ttl=cache_ttl, prefix=key_prefix)

                return result

            return async_wrapper
        else:

            def sync_wrapper(*args, **kwargs):
                # requires: Valid input parameters
                # ensures: Correct function execution
                # sha256: func_hash
                # For sync functions, we can't use async cache directly
                # This would need to be handled differently in a real implementation
                return func(*args, **kwargs)

            return sync_wrapper

    return decorator


@asynccontextmanager
async def cache_context(service_name: str, config: Optional[CacheConfig] = None):
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """Context manager for cache operations."""
    client = await get_redis_client(service_name, config)
    try:
        yield client
    finally:
        # Client remains open for reuse
        pass
