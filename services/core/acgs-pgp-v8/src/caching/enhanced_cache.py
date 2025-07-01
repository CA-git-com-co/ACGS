"""
Enhanced Caching System for ACGS-PGP v8

Implements intelligent caching with TTL optimization, cache warming strategies,
predictive caching, and comprehensive performance monitoring.
"""

import asyncio
import json
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

import numpy as np
import redis.asyncio as redis

logger = logging.getLogger(__name__)


class CacheStrategy(Enum):
    """Cache strategy types for different data patterns."""

    WRITE_THROUGH = "write_through"  # Write to cache and database simultaneously
    WRITE_BEHIND = "write_behind"  # Write to cache first, database later
    READ_THROUGH = "read_through"  # Read from cache, fallback to database
    CACHE_ASIDE = "cache_aside"  # Manual cache management
    REFRESH_AHEAD = "refresh_ahead"  # Proactive cache refresh before expiry


@dataclass
class CacheMetrics:
    """Comprehensive cache performance metrics."""

    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    evictions: int = 0
    total_operations: int = 0

    # Performance metrics
    avg_get_time: float = 0.0
    avg_set_time: float = 0.0
    max_get_time: float = 0.0
    max_set_time: float = 0.0

    # Memory metrics
    memory_usage_bytes: int = 0
    key_count: int = 0
    expired_keys: int = 0

    # TTL optimization metrics
    ttl_hits: int = 0
    ttl_misses: int = 0
    avg_ttl_accuracy: float = 0.0

    # Warming metrics
    warming_operations: int = 0
    successful_warmings: int = 0
    warming_time: float = 0.0

    timestamp: datetime = field(default_factory=datetime.utcnow)

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.hits + self.misses
        return (self.hits / total) if total > 0 else 0.0

    @property
    def miss_rate(self) -> float:
        """Calculate cache miss rate."""
        return 1.0 - self.hit_rate


@dataclass
class CacheItem:
    """Cache item with metadata for intelligent management."""

    key: str
    value: Any
    ttl: int
    strategy: CacheStrategy
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.utcnow)
    created_at: datetime = field(default_factory=datetime.utcnow)
    size_bytes: int = 0
    priority: int = 1  # 1=low, 5=high
    tags: list[str] = field(default_factory=list)


class IntelligentTTLOptimizer:
    """Intelligent TTL optimization based on access patterns."""

    def __init__(self, learning_rate: float = 0.1):
        """Initialize TTL optimizer."""
        self.learning_rate = learning_rate
        self.access_patterns: dict[str, list[datetime]] = {}
        self.ttl_predictions: dict[str, int] = {}
        self.accuracy_scores: dict[str, float] = {}

    def record_access(self, key: str, access_time: datetime = None):
        """Record cache access for pattern learning."""
        access_time = access_time or datetime.utcnow()

        if key not in self.access_patterns:
            self.access_patterns[key] = []

        self.access_patterns[key].append(access_time)

        # Keep only recent accesses (last 100)
        if len(self.access_patterns[key]) > 100:
            self.access_patterns[key] = self.access_patterns[key][-100:]

    def predict_optimal_ttl(self, key: str, default_ttl: int = 3600) -> int:
        """Predict optimal TTL based on access patterns."""
        if key not in self.access_patterns or len(self.access_patterns[key]) < 2:
            return default_ttl

        accesses = self.access_patterns[key]

        # Calculate access intervals
        intervals = []
        for i in range(1, len(accesses)):
            interval = (accesses[i] - accesses[i - 1]).total_seconds()
            intervals.append(interval)

        if not intervals:
            return default_ttl

        # Use statistical analysis for TTL prediction
        avg_interval = np.mean(intervals)
        std_interval = np.std(intervals)

        # Predict TTL as 2x average interval + 1 standard deviation
        predicted_ttl = int(avg_interval * 2 + std_interval)

        # Apply bounds
        min_ttl = 60  # 1 minute minimum
        max_ttl = 86400  # 24 hours maximum

        predicted_ttl = max(min_ttl, min(max_ttl, predicted_ttl))

        # Store prediction for accuracy tracking
        self.ttl_predictions[key] = predicted_ttl

        return predicted_ttl

    def update_accuracy(self, key: str, actual_hit: bool):
        """Update TTL prediction accuracy."""
        if key in self.ttl_predictions:
            current_accuracy = self.accuracy_scores.get(key, 0.5)

            # Update accuracy using exponential moving average
            new_accuracy = current_accuracy * (1 - self.learning_rate)
            if actual_hit:
                new_accuracy += self.learning_rate

            self.accuracy_scores[key] = new_accuracy


class CacheWarmingEngine:
    """Advanced cache warming with predictive capabilities."""

    def __init__(self, cache_client: redis.Redis):
        """Initialize cache warming engine."""
        self.cache_client = cache_client
        self.warming_sources: dict[str, Callable] = {}
        self.warming_schedule: dict[str, datetime] = {}
        self.warming_priorities: dict[str, int] = {}

    def register_warming_source(
        self, name: str, source_func: Callable, priority: int = 1
    ):
        """Register a data source for cache warming."""
        self.warming_sources[name] = source_func
        self.warming_priorities[name] = priority

    async def warm_cache_proactive(self, keys: list[str]) -> int:
        """Proactively warm cache for specified keys."""
        successful_warmings = 0

        for key in keys:
            try:
                # Check if key needs warming
                ttl = await self.cache_client.ttl(key)

                # Warm if key doesn't exist or expires soon (< 10% of original TTL)
                if ttl <= 0 or ttl < 360:  # Less than 6 minutes
                    await self._warm_single_key(key)
                    successful_warmings += 1

            except Exception as e:
                logger.warning(f"Failed to warm cache key {key}: {e}")

        return successful_warmings

    async def warm_cache_predictive(self, prediction_window: int = 3600) -> int:
        """Predictively warm cache based on usage patterns."""
        # Get keys that are likely to be accessed soon
        predicted_keys = await self._predict_future_accesses(prediction_window)

        return await self.warm_cache_proactive(predicted_keys)

    async def _warm_single_key(self, key: str):
        """Warm a single cache key."""
        # Try each warming source in priority order
        sources = sorted(
            self.warming_sources.items(),
            key=lambda x: self.warming_priorities.get(x[0], 1),
            reverse=True,
        )

        for source_name, source_func in sources:
            try:
                data = await source_func(key)
                if data is not None:
                    # Determine appropriate TTL and strategy
                    ttl = self._calculate_warming_ttl(key)
                    await self.cache_client.setex(key, ttl, json.dumps(data))
                    logger.debug(f"Warmed cache key {key} from source {source_name}")
                    return
            except Exception as e:
                logger.warning(
                    f"Warming source {source_name} failed for key {key}: {e}"
                )

    async def _predict_future_accesses(self, window_seconds: int) -> list[str]:
        """Predict keys likely to be accessed in the future."""
        # This is a simplified prediction - in production, you'd use ML models
        # For now, return keys that were accessed recently

        try:
            # Get all keys with pattern matching
            all_keys = await self.cache_client.keys("*")

            # Filter keys that might be accessed soon based on patterns
            predicted_keys = []
            current_time = datetime.utcnow()

            for key in all_keys:
                # Simple heuristic: keys accessed in the last hour are likely to be accessed again
                try:
                    last_access_str = await self.cache_client.hget(
                        f"meta:{key}", "last_access"
                    )
                    if last_access_str:
                        last_access = datetime.fromisoformat(last_access_str)
                        if (current_time - last_access).total_seconds() < 3600:
                            predicted_keys.append(key)
                except Exception:
                    continue

            return predicted_keys[:50]  # Limit to top 50 predictions

        except Exception as e:
            logger.error(f"Failed to predict future accesses: {e}")
            return []

    def _calculate_warming_ttl(self, key: str) -> int:
        """Calculate appropriate TTL for warmed cache items."""
        # Default warming TTL based on key patterns
        if "policy:" in key:
            return 3600  # 1 hour for policies
        if "constitutional:" in key:
            return 1800  # 30 minutes for constitutional data
        if "diagnostic:" in key:
            return 900  # 15 minutes for diagnostics
        return 1800  # 30 minutes default


class EnhancedCacheManager:
    """Enhanced cache manager with intelligent features."""

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379/0",
        max_connections: int = 100,
        enable_ttl_optimization: bool = True,
        enable_cache_warming: bool = True,
    ):
        """Initialize enhanced cache manager."""
        self.redis_url = redis_url
        self.max_connections = max_connections
        self.enable_ttl_optimization = enable_ttl_optimization
        self.enable_cache_warming = enable_cache_warming

        # Core components
        self.redis_client: redis.Redis | None = None
        self.metrics = CacheMetrics()

        # Enhanced features
        self.ttl_optimizer = (
            IntelligentTTLOptimizer() if enable_ttl_optimization else None
        )
        self.warming_engine: CacheWarmingEngine | None = None

        # Cache item tracking
        self.cache_items: dict[str, CacheItem] = {}

        # Performance tracking
        self.operation_times: list[float] = []

        logger.info("Enhanced cache manager initialized")

    async def initialize(self):
        """Initialize Redis connection and enhanced features."""
        try:
            # Create Redis connection pool
            self.redis_client = redis.from_url(
                self.redis_url,
                max_connections=self.max_connections,
                retry_on_timeout=True,
                socket_timeout=5.0,
                socket_connect_timeout=5.0,
                decode_responses=True,
            )

            # Test connection
            await self.redis_client.ping()
            logger.info("✅ Enhanced Redis cache connection established")

            # Initialize warming engine
            if self.enable_cache_warming:
                self.warming_engine = CacheWarmingEngine(self.redis_client)
                logger.info("✅ Cache warming engine initialized")

            # Start background tasks
            asyncio.create_task(self._background_maintenance())

        except Exception as e:
            logger.error(f"❌ Failed to initialize enhanced cache: {e}")
            raise

    async def get(
        self, key: str, strategy: CacheStrategy = CacheStrategy.READ_THROUGH
    ) -> Any | None:
        """Get value from cache with intelligent features."""
        start_time = time.time()

        try:
            # Record access for TTL optimization
            if self.ttl_optimizer:
                self.ttl_optimizer.record_access(key)

            # Get from Redis
            value = await self.redis_client.get(key)

            # Update metrics
            operation_time = time.time() - start_time
            self.operation_times.append(operation_time)

            if value is not None:
                self.metrics.hits += 1

                # Update cache item metadata
                if key in self.cache_items:
                    self.cache_items[key].access_count += 1
                    self.cache_items[key].last_accessed = datetime.utcnow()

                # Update TTL accuracy
                if self.ttl_optimizer:
                    self.ttl_optimizer.update_accuracy(key, True)

                # Deserialize value
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            else:
                self.metrics.misses += 1

                # Update TTL accuracy
                if self.ttl_optimizer:
                    self.ttl_optimizer.update_accuracy(key, False)

                return None

        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            self.metrics.misses += 1
            return None
        finally:
            self.metrics.total_operations += 1

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
        strategy: CacheStrategy = CacheStrategy.WRITE_THROUGH,
        priority: int = 1,
        tags: list[str] | None = None,
    ) -> bool:
        """Set value in cache with intelligent TTL and metadata."""
        start_time = time.time()

        try:
            # Optimize TTL if enabled
            if self.ttl_optimizer and ttl is None:
                ttl = self.ttl_optimizer.predict_optimal_ttl(key)
            elif ttl is None:
                ttl = 3600  # Default 1 hour

            # Serialize value
            if isinstance(value, (dict, list)):
                serialized_value = json.dumps(value)
            else:
                serialized_value = str(value)

            # Set in Redis
            result = await self.redis_client.setex(key, ttl, serialized_value)

            # Track cache item
            self.cache_items[key] = CacheItem(
                key=key,
                value=value,
                ttl=ttl,
                strategy=strategy,
                size_bytes=len(serialized_value.encode("utf-8")),
                priority=priority,
                tags=tags or [],
            )

            # Update metrics
            self.metrics.sets += 1
            self.metrics.total_operations += 1

            operation_time = time.time() - start_time

            return bool(result)

        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False

    async def warm_cache(self, keys: list[str] | None = None) -> int:
        """Warm cache proactively or predictively."""
        if not self.warming_engine:
            return 0

        start_time = time.time()

        try:
            if keys:
                # Proactive warming for specific keys
                successful = await self.warming_engine.warm_cache_proactive(keys)
            else:
                # Predictive warming
                successful = await self.warming_engine.warm_cache_predictive()

            # Update metrics
            warming_time = time.time() - start_time
            self.metrics.warming_operations += 1
            self.metrics.successful_warmings += successful
            self.metrics.warming_time += warming_time

            logger.info(
                f"Cache warming completed: {successful} keys warmed in {warming_time:.3f}s"
            )
            return successful

        except Exception as e:
            logger.error(f"Cache warming failed: {e}")
            return 0

    def _update_performance_metrics(self, operation_time: float, operation_type: str):
        """Update performance metrics."""
        if operation_type == "get":
            if self.metrics.avg_get_time == 0:
                self.metrics.avg_get_time = operation_time
            else:
                self.metrics.avg_get_time = (
                    self.metrics.avg_get_time + operation_time
                ) / 2
            self.metrics.max_get_time = max(self.metrics.max_get_time, operation_time)
        elif operation_type == "set":
            if self.metrics.avg_set_time == 0:
                self.metrics.avg_set_time = operation_time
            else:
                self.metrics.avg_set_time = (
                    self.metrics.avg_set_time + operation_time
                ) / 2
            self.metrics.max_set_time = max(self.metrics.max_set_time, operation_time)

    async def _background_maintenance(self):
        """Enhanced background maintenance tasks with comprehensive monitoring."""
        maintenance_interval = 300  # 5 minutes
        error_backoff = 60  # 1 minute on error

        while True:
            try:
                start_time = time.time()

                # TTL optimization with performance tracking
                if self.ttl_optimizer:
                    ttl_start = time.time()
                    await self._optimize_ttls()
                    ttl_duration = time.time() - ttl_start
                    logger.debug(f"TTL optimization completed in {ttl_duration:.2f}s")

                # Enhanced memory metrics collection
                info = await self.redis_client.info("memory")
                self.metrics.memory_usage_bytes = info.get("used_memory", 0)
                memory_mb = self.metrics.memory_usage_bytes / (1024 * 1024)

                # Key count and fragmentation metrics
                self.metrics.key_count = await self.redis_client.dbsize()
                fragmentation_ratio = info.get("mem_fragmentation_ratio", 1.0)

                # Predictive cache warming with metrics
                if self.warming_engine:
                    warming_start = time.time()
                    warming_metrics = await self.warm_cache()
                    warming_duration = time.time() - warming_start
                    if warming_metrics:
                        logger.info(
                            f"Cache warming: {warming_metrics.successful_warmings}/{warming_metrics.total_items_warmed} items in {warming_duration:.2f}s"
                        )

                # Memory usage monitoring and alerts
                await self._monitor_memory_usage(memory_mb, fragmentation_ratio)

                # Cleanup expired items
                cleaned_items = await self._cleanup_expired_items()

                # Performance metrics update
                await self._update_performance_metrics()

                total_duration = time.time() - start_time
                logger.debug(
                    f"Background maintenance cycle completed in {total_duration:.2f}s - Memory: {memory_mb:.1f}MB, Keys: {self.metrics.key_count}, Cleaned: {cleaned_items}"
                )

                await asyncio.sleep(maintenance_interval)

            except Exception as e:
                logger.error(f"Background maintenance error: {e}")
                await asyncio.sleep(error_backoff)

    def get_metrics(self) -> CacheMetrics:
        """Get current cache metrics."""
        self.metrics.timestamp = datetime.utcnow()
        return self.metrics

    def get_performance_summary(self) -> dict[str, Any]:
        """Get comprehensive performance summary."""
        return {
            "hit_rate": self.metrics.hit_rate,
            "miss_rate": self.metrics.miss_rate,
            "total_operations": self.metrics.total_operations,
            "avg_get_time_ms": self.metrics.avg_get_time * 1000,
            "avg_set_time_ms": self.metrics.avg_set_time * 1000,
            "memory_usage_mb": self.metrics.memory_usage_bytes / (1024 * 1024),
            "key_count": self.metrics.key_count,
            "warming_success_rate": (
                self.metrics.successful_warmings
                / max(1, self.metrics.warming_operations)
            ),
            "ttl_optimization_enabled": self.ttl_optimizer is not None,
            "cache_warming_enabled": self.warming_engine is not None,
            "timestamp": datetime.utcnow(),
        }

    async def _optimize_ttls(self):
        """Optimize TTL values based on access patterns."""
        if not self.ttl_optimizer:
            return

        try:
            # Get keys that need TTL optimization
            keys_to_optimize = await self._get_keys_for_ttl_optimization()

            for key in keys_to_optimize:
                optimal_ttl = self.ttl_optimizer.predict_optimal_ttl(key)
                current_ttl = await self.redis_client.ttl(key)

                # Only update if significantly different
                if abs(optimal_ttl - current_ttl) > 300:  # 5 minute threshold
                    await self.redis_client.expire(key, optimal_ttl)
                    logger.debug(
                        f"Updated TTL for {key}: {current_ttl}s -> {optimal_ttl}s"
                    )

        except Exception as e:
            logger.error(f"TTL optimization error: {e}")

    async def _get_keys_for_ttl_optimization(self) -> list[str]:
        """Get keys that should be considered for TTL optimization."""
        try:
            # Get a sample of keys for optimization
            keys = []
            cursor = 0
            while len(keys) < 100:  # Limit to 100 keys per cycle
                cursor, batch = await self.redis_client.scan(cursor, count=50)
                keys.extend(batch)
                if cursor == 0:
                    break
            return keys[:100]
        except Exception as e:
            logger.error(f"Error getting keys for TTL optimization: {e}")
            return []

    async def _monitor_memory_usage(self, memory_mb: float, fragmentation_ratio: float):
        """Monitor memory usage and trigger alerts if needed."""
        try:
            # Memory usage alerts
            if memory_mb > 3000:  # 3GB threshold
                logger.warning(f"High memory usage: {memory_mb:.1f}MB")

            # Fragmentation alerts
            if fragmentation_ratio > 1.5:
                logger.warning(f"High memory fragmentation: {fragmentation_ratio:.2f}")

            # Update metrics
            self.metrics.memory_usage_bytes = int(memory_mb * 1024 * 1024)

        except Exception as e:
            logger.error(f"Memory monitoring error: {e}")

    async def _cleanup_expired_items(self) -> int:
        """Clean up expired cache items and return count."""
        try:
            cleaned_count = 0
            current_time = datetime.utcnow()

            # Clean up local cache item tracking
            expired_keys = []
            for key, item in self.cache_items.items():
                if item.expires_at and current_time > item.expires_at:
                    expired_keys.append(key)

            for key in expired_keys:
                del self.cache_items[key]
                cleaned_count += 1

            self.metrics.expired_keys += cleaned_count
            return cleaned_count

        except Exception as e:
            logger.error(f"Cleanup error: {e}")
            return 0

    async def _update_performance_metrics(self):
        """Update comprehensive performance metrics."""
        try:
            # Calculate hit rate
            total_ops = self.metrics.hits + self.metrics.misses
            if total_ops > 0:
                self.metrics.hit_rate = self.metrics.hits / total_ops
                self.metrics.miss_rate = self.metrics.misses / total_ops

            # Update timestamp
            self.metrics.timestamp = datetime.utcnow()

            # Log performance summary periodically
            if total_ops % 1000 == 0 and total_ops > 0:
                logger.info(
                    f"Cache performance: {self.metrics.hit_rate:.2%} hit rate, {len(self.operation_times)} operations"
                )

        except Exception as e:
            logger.error(f"Performance metrics update error: {e}")

    async def cleanup(self):
        """Cleanup cache resources."""
        if self.redis_client:
            await self.redis_client.close()
        logger.info("Enhanced cache manager cleanup completed")
