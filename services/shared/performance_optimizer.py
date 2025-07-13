"""
Enhanced Performance Optimizer for ACGS Services

Provides comprehensive performance optimization including O(1) lookups,
advanced caching strategies, connection pooling, and real-time monitoring.
"""

import asyncio
import hashlib
import json
import logging
import time
from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass, field
from functools import wraps
from typing import Any

import asyncpg
import redis.asyncio as redis
from prometheus_client import Counter, Gauge, Histogram

logger = logging.getLogger(__name__)

# Prometheus metrics
CACHE_HITS = Counter(
    "acgs_cache_hits_total", "Total cache hits", ["service", "cache_type"]
)
CACHE_MISSES = Counter(
    "acgs_cache_misses_total", "Total cache misses", ["service", "cache_type"]
)
CACHE_LATENCY = Histogram(
    "acgs_cache_latency_seconds", "Cache operation latency", ["service", "operation"]
)
DB_CONNECTIONS = Gauge(
    "acgs_db_connections_active", "Active database connections", ["service"]
)
QUERY_LATENCY = Histogram(
    "acgs_query_latency_seconds", "Database query latency", ["service", "query_type"]
)


@dataclass
class CacheEntry:
    """Enhanced cache entry with metadata."""

    value: Any
    timestamp: float
    ttl: int
    access_count: int = 0
    last_access: float = field(default_factory=time.time)
    size_bytes: int = 0
    constitutional_hash: str = "cdd01ef066bc6cf2"


@dataclass
class PerformanceMetrics:
    """Performance metrics tracking."""

    cache_hit_rate: float = 0.0
    avg_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    throughput_rps: float = 0.0
    active_connections: int = 0
    memory_usage_mb: float = 0.0


class O1LookupCache:
    """O(1) lookup cache with LRU eviction and performance tracking."""

    def __init__(self, max_size: int = 10000, default_ttl: int = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.index: dict[str, str] = {}  # Fast lookup index
        self.metrics = PerformanceMetrics()
        self.hit_count = 0
        self.miss_count = 0

    def _generate_key(self, key: str | dict[str, Any]) -> str:
        """Generate O(1) lookup key."""
        if isinstance(key, str):
            return key

        # Create deterministic hash for complex keys
        key_str = json.dumps(key, sort_keys=True)
        return hashlib.sha256(key_str.encode()).hexdigest()[:16]

    def get(self, key: str | dict[str, Any]) -> Any | None:
        """O(1) cache get operation."""
        start_time = time.time()
        cache_key = self._generate_key(key)

        try:
            if cache_key in self.cache:
                entry = self.cache[cache_key]

                # Check TTL
                if time.time() - entry.timestamp > entry.ttl:
                    del self.cache[cache_key]
                    if cache_key in self.index:
                        del self.index[cache_key]
                    self.miss_count += 1
                    return None

                # Move to end (LRU)
                self.cache.move_to_end(cache_key)
                entry.access_count += 1
                entry.last_access = time.time()

                self.hit_count += 1
                self._update_hit_rate()

                return entry.value

            self.miss_count += 1
            self._update_hit_rate()
            return None

        finally:
            latency = (time.time() - start_time) * 1000
            CACHE_LATENCY.labels(service="shared", operation="get").observe(
                latency / 1000
            )

    def set(
        self, key: str | dict[str, Any], value: Any, ttl: int | None = None
    ) -> bool:
        """O(1) cache set operation."""
        start_time = time.time()
        cache_key = self._generate_key(key)
        cache_ttl = ttl or self.default_ttl

        try:
            # Calculate value size
            try:
                size_bytes = len(json.dumps(value).encode())
            except:
                size_bytes = 1024  # Default estimate

            entry = CacheEntry(
                value=value, timestamp=time.time(), ttl=cache_ttl, size_bytes=size_bytes
            )

            # Add to cache
            self.cache[cache_key] = entry
            self.index[cache_key] = cache_key

            # Move to end
            self.cache.move_to_end(cache_key)

            # Evict if necessary
            while len(self.cache) > self.max_size:
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
                if oldest_key in self.index:
                    del self.index[oldest_key]

            return True

        except Exception as e:
            logger.exception(f"Cache set error: {e}")
            return False
        finally:
            latency = (time.time() - start_time) * 1000
            CACHE_LATENCY.labels(service="shared", operation="set").observe(
                latency / 1000
            )

    def _update_hit_rate(self):
        """Update cache hit rate metrics."""
        total = self.hit_count + self.miss_count
        if total > 0:
            self.metrics.cache_hit_rate = (self.hit_count / total) * 100


class EnhancedRedisCache:
    """Enhanced Redis cache with connection pooling and monitoring."""

    def __init__(self, redis_url: str, service_name: str, max_connections: int = 20):
        self.redis_url = redis_url
        self.service_name = service_name
        self.max_connections = max_connections
        self.redis_client: redis.Redis | None = None
        self.connection_pool: redis.ConnectionPool | None = None
        self.circuit_breaker_failures = 0
        self.circuit_breaker_threshold = 5
        self.circuit_breaker_timeout = 60
        self.circuit_breaker_last_failure = 0

    async def initialize(self):
        """Initialize Redis connection pool."""
        try:
            self.connection_pool = redis.ConnectionPool.from_url(
                self.redis_url,
                max_connections=self.max_connections,
                retry_on_timeout=True,
                socket_keepalive=True,
                socket_connect_timeout=5,
                socket_timeout=2,
                health_check_interval=30,
            )

            self.redis_client = redis.Redis(
                connection_pool=self.connection_pool, decode_responses=True
            )

            # Test connection
            await self.redis_client.ping()
            logger.info(f"Redis cache initialized for {self.service_name}")

        except Exception as e:
            logger.exception(f"Failed to initialize Redis cache: {e}")
            raise

    def _is_circuit_breaker_open(self) -> bool:
        """Check if circuit breaker is open."""
        if self.circuit_breaker_failures >= self.circuit_breaker_threshold:
            if (
                time.time() - self.circuit_breaker_last_failure
                < self.circuit_breaker_timeout
            ):
                return True
            # Reset circuit breaker
            self.circuit_breaker_failures = 0
        return False

    async def get(self, key: str) -> Any | None:
        """Get value from Redis with circuit breaker."""
        if self._is_circuit_breaker_open():
            return None

        start_time = time.time()

        try:
            value = await self.redis_client.get(key)
            if value:
                CACHE_HITS.labels(service=self.service_name, cache_type="redis").inc()
                try:
                    return json.loads(value)
                except:
                    return value
            else:
                CACHE_MISSES.labels(service=self.service_name, cache_type="redis").inc()
                return None

        except Exception as e:
            logger.exception(f"Redis get error: {e}")
            self.circuit_breaker_failures += 1
            self.circuit_breaker_last_failure = time.time()
            CACHE_MISSES.labels(service=self.service_name, cache_type="redis").inc()
            return None
        finally:
            latency = time.time() - start_time
            CACHE_LATENCY.labels(service=self.service_name, operation="get").observe(
                latency
            )

    async def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set value in Redis with circuit breaker."""
        if self._is_circuit_breaker_open():
            return False

        start_time = time.time()

        try:
            serialized_value = (
                json.dumps(value) if not isinstance(value, str) else value
            )
            await self.redis_client.setex(key, ttl, serialized_value)
            return True

        except Exception as e:
            logger.exception(f"Redis set error: {e}")
            self.circuit_breaker_failures += 1
            self.circuit_breaker_last_failure = time.time()
            return False
        finally:
            latency = time.time() - start_time
            CACHE_LATENCY.labels(service=self.service_name, operation="set").observe(
                latency
            )


class DatabaseConnectionPool:
    """Enhanced database connection pool with monitoring."""

    def __init__(
        self,
        database_url: str,
        service_name: str,
        min_connections: int = 5,
        max_connections: int = 20,
    ):
        self.database_url = database_url
        self.service_name = service_name
        self.min_connections = min_connections
        self.max_connections = max_connections
        self.pool: asyncpg.Pool | None = None

    async def initialize(self):
        """Initialize connection pool."""
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=self.min_connections,
                max_size=self.max_connections,
                command_timeout=30,
                server_settings={
                    "application_name": f"acgs_{self.service_name}",
                    "tcp_keepalives_idle": "600",
                    "tcp_keepalives_interval": "30",
                    "tcp_keepalives_count": "3",
                },
            )

            # Update metrics
            DB_CONNECTIONS.labels(service=self.service_name).set(self.min_connections)
            logger.info(f"Database pool initialized for {self.service_name}")

        except Exception as e:
            logger.exception(f"Failed to initialize database pool: {e}")
            raise

    async def execute_query(self, query: str, *args, query_type: str = "select") -> Any:
        """Execute query with performance monitoring."""
        start_time = time.time()

        try:
            async with self.pool.acquire() as connection:
                if query_type.lower() == "select":
                    result = await connection.fetch(query, *args)
                else:
                    result = await connection.execute(query, *args)

                return result

        except Exception as e:
            logger.exception(f"Database query error: {e}")
            raise
        finally:
            latency = time.time() - start_time
            QUERY_LATENCY.labels(
                service=self.service_name, query_type=query_type
            ).observe(latency)


def performance_cache(ttl: int = 300, cache_type: str = "memory"):
    """Performance caching decorator with O(1) lookups."""

    def decorator(func: Callable) -> Callable:
        cache = O1LookupCache(default_ttl=ttl)

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = (
                f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            )

            # Try cache first
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Execute function
            start_time = time.time()
            result = await func(*args, **kwargs)
            execution_time = (time.time() - start_time) * 1000

            # Cache result
            cache.set(cache_key, result, ttl)

            # Log slow operations
            if execution_time > 100:  # > 100ms
                logger.warning(
                    f"Slow operation {func.__name__}: {execution_time:.2f}ms"
                )

            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = (
                f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            )

            # Try cache first
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Execute function
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = (time.time() - start_time) * 1000

            # Cache result
            cache.set(cache_key, result, ttl)

            # Log slow operations
            if execution_time > 100:  # > 100ms
                logger.warning(
                    f"Slow operation {func.__name__}: {execution_time:.2f}ms"
                )

            return result

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator


class PerformanceMonitor:
    """Real-time performance monitoring."""

    def __init__(self, service_name: str):
        self.service_name = service_name
        self.metrics = PerformanceMetrics()
        self.latency_samples: list[float] = []
        self.max_samples = 1000

    def record_latency(self, latency_ms: float):
        """Record latency sample."""
        self.latency_samples.append(latency_ms)

        # Keep only recent samples
        if len(self.latency_samples) > self.max_samples:
            self.latency_samples = self.latency_samples[-self.max_samples :]

        # Update metrics
        if self.latency_samples:
            self.metrics.avg_latency_ms = sum(self.latency_samples) / len(
                self.latency_samples
            )
            self.metrics.p99_latency_ms = sorted(self.latency_samples)[
                int(0.99 * len(self.latency_samples))
            ]

    def get_performance_report(self) -> dict[str, Any]:
        """Get comprehensive performance report."""
        return {
            "service": self.service_name,
            "cache_hit_rate": self.metrics.cache_hit_rate,
            "avg_latency_ms": self.metrics.avg_latency_ms,
            "p99_latency_ms": self.metrics.p99_latency_ms,
            "throughput_rps": self.metrics.throughput_rps,
            "active_connections": self.metrics.active_connections,
            "memory_usage_mb": self.metrics.memory_usage_mb,
            "constitutional_compliance": "cdd01ef066bc6cf2",
            "timestamp": time.time(),
        }
