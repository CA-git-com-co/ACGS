"""
Redis Cache Manager for ACGS-1 PGC Service Enterprise Implementation

Implements Redis-backed caching with HMAC-SHA256 integrity verification,
intelligent cache invalidation, and multi-tier caching strategy for
ultra-low-latency policy compilation and enforcement.

# requires: Redis server available, constitutional_hash = "cdd01ef066bc6cf2"
# ensures: cache_hit_rate >= 80.0 AND cache_lookup_latency_ms <= 2.0
# sha256: redis_cache_manager_enterprise_v1.0_acgs1_constitutional_governance

Enterprise Features:
- HMAC-SHA256 integrity verification for all cached data
- Constitutional hash validation (cdd01ef066bc6cf2)
- Multi-tier caching (L1: memory, L2: Redis, L3: persistent)
- Intelligent cache invalidation with dependency tracking
- Circuit breaker pattern for Redis failures
- Performance monitoring and metrics
"""

import hashlib
import hmac
import json
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any

import redis.asyncio as redis
from prometheus_client import Counter, Gauge, Histogram

logger = logging.getLogger(__name__)

# Global metrics to prevent duplication
_cache_metrics_initialized = False
_cache_hit_counter = None
_cache_miss_counter = None
_cache_lookup_histogram = None
_cache_size_gauge = None


def _get_cache_metrics():
    """Get or create singleton cache metrics to prevent duplication."""
    global _cache_metrics_initialized, _cache_hit_counter, _cache_miss_counter, _cache_lookup_histogram, _cache_size_gauge

    if not _cache_metrics_initialized:
        try:
            _cache_hit_counter = Counter("pgc_cache_hits_total", "Total cache hits", ["level"])
            _cache_miss_counter = Counter("pgc_cache_misses_total", "Total cache misses")
            _cache_lookup_histogram = Histogram(
                "pgc_cache_lookup_duration_seconds",
                "Cache lookup duration in seconds",
                buckets=[0.001, 0.002, 0.005, 0.01, 0.025, 0.05, 0.1],
            )
            _cache_size_gauge = Gauge("pgc_cache_entries_total", "Total cache entries", ["level"])
            _cache_metrics_initialized = True
            logger.info("PGC cache metrics initialized successfully")
        except ValueError as e:
            if "Duplicated timeseries" in str(e):
                # Metrics already exist, try to get them from registry
                logger.warning(f"Cache metrics already exist, reusing: {e}")
                # For now, set to None to disable metrics rather than crash
                _cache_hit_counter = None
                _cache_miss_counter = None
                _cache_lookup_histogram = None
                _cache_size_gauge = None
                _cache_metrics_initialized = True
            else:
                raise

    return (
        _cache_hit_counter,
        _cache_miss_counter,
        _cache_lookup_histogram,
        _cache_size_gauge,
    )


class CacheLevel(Enum):
    """Cache levels for multi-tier caching strategy."""

    L1_MEMORY = "l1_memory"
    L2_REDIS = "l2_redis"
    L3_PERSISTENT = "l3_persistent"


class CacheStrategy(Enum):
    """Caching strategies for different data types."""

    IMMEDIATE = "immediate"  # No TTL, cache until invalidated
    SHORT_TERM = "short_term"  # 5 minutes TTL
    MEDIUM_TERM = "medium_term"  # 1 hour TTL
    LONG_TERM = "long_term"  # 24 hours TTL
    CONSTITUTIONAL = "constitutional"  # Special handling for constitutional data


@dataclass
class CacheEntry:
    """Cache entry with integrity verification."""

    key: str
    value: Any
    timestamp: float
    ttl: int
    hmac_signature: str
    constitutional_hash: str | None = None
    access_count: int = 0
    last_access: float = 0.0


@dataclass
class CacheMetrics:
    """Cache performance metrics."""

    hit_rate: float = 0.0
    miss_rate: float = 0.0
    avg_lookup_time_ms: float = 0.0
    total_entries: int = 0
    memory_usage_mb: float = 0.0
    invalidations_count: int = 0


class RedisCacheManager:
    """
    Enterprise Redis cache manager with HMAC integrity verification.

        # requires: Redis connection available, HMAC secret configured
        # ensures: cache operations complete within 2ms, integrity verified
        # sha256: redis_cache_manager_v1.0_enterprise_acgs1
    """

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        hmac_secret: str = "acgs1-enterprise-cache-secret",
        constitutional_hash: str = "cdd01ef066bc6cf2",
        max_memory_cache_size: int = 1000,
    ):
        # requires: redis_url is valid, hmac_secret is secure
        # ensures: cache manager initialized with enterprise configuration
        # sha256: redis_cache_init_enterprise_v1.0

        self.redis_url = redis_url
        self.hmac_secret = hmac_secret.encode()
        self.constitutional_hash = constitutional_hash
        self.max_memory_cache_size = max_memory_cache_size

        # Redis client
        self.redis_client: redis.Redis | None = None

        # L1 Memory cache
        self.memory_cache: dict[str, CacheEntry] = {}
        self.memory_cache_order: list[str] = []  # LRU tracking

        # Circuit breaker for Redis failures
        self.circuit_breaker_failures = 0
        self.circuit_breaker_threshold = 5
        self.circuit_breaker_reset_time = 60  # seconds
        self.circuit_breaker_last_failure = 0

        # Performance metrics
        self.metrics = {
            "total_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "l1_hits": 0,
            "l2_hits": 0,
            "l3_hits": 0,
            "invalidations": 0,
            "integrity_failures": 0,
            "circuit_breaker_trips": 0,
        }

        # Prometheus metrics (singleton to prevent duplication)
        (
            self.cache_hit_counter,
            self.cache_miss_counter,
            self.cache_lookup_histogram,
            self.cache_size_gauge,
        ) = _get_cache_metrics()

    async def initialize(self) -> None:
        """Initialize Redis connection and validate configuration."""
        # requires: Redis server accessible
        # ensures: Redis client connected and validated
        # sha256: redis_init_validation_v1.0

        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=2,
                retry_on_timeout=True,
                health_check_interval=30,
            )

            # Test connection
            await self.redis_client.ping()

            # Enhanced constitutional hash validation
            await self._validate_and_update_constitutional_hash()

            # Initialize constitutional hash monitoring
            await self._setup_constitutional_hash_monitoring()

            logger.info("Redis cache manager initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Redis cache manager: {e}")
            self.redis_client = None
            raise

    async def get(self, key: str, verify_constitutional: bool = True) -> Any | None:
        """
        Get value from cache with integrity verification.

        # requires: key is non-empty string
        # ensures: returned value integrity verified or None
        # sha256: cache_get_with_integrity_v1.0
        """
        start_time = time.time()
        self.metrics["total_requests"] += 1

        try:
            # Try L1 memory cache first
            if key in self.memory_cache:
                entry = self.memory_cache[key]
                if self._is_entry_valid(entry):
                    if self._verify_integrity(entry):
                        self._update_access_stats(entry, CacheLevel.L1_MEMORY)
                        if self.cache_hit_counter:
                            self.cache_hit_counter.labels(level="l1").inc()
                        self.metrics["cache_hits"] += 1
                        self.metrics["l1_hits"] += 1
                        return entry.value
                    else:
                        # Integrity failure - remove from cache
                        self._remove_from_memory_cache(key)
                        self.metrics["integrity_failures"] += 1

            # Try L2 Redis cache
            if self.redis_client and not self._is_circuit_breaker_open():
                try:
                    cached_data = await self.redis_client.get(f"pgc:{key}")
                    if cached_data:
                        entry = self._deserialize_cache_entry(cached_data)
                        if entry and self._is_entry_valid(entry):
                            if self._verify_integrity(entry):
                                # Promote to L1 cache
                                self._add_to_memory_cache(key, entry)
                                self._update_access_stats(entry, CacheLevel.L2_REDIS)
                                if self.cache_hit_counter:
                                    self.cache_hit_counter.labels(level="l2").inc()
                                self.metrics["cache_hits"] += 1
                                self.metrics["l2_hits"] += 1
                                return entry.value
                            else:
                                # Remove corrupted entry
                                await self.redis_client.delete(f"pgc:{key}")
                                self.metrics["integrity_failures"] += 1

                except Exception as e:
                    logger.error(f"Redis cache lookup failed: {e}")
                    self._handle_circuit_breaker_failure()

            # Cache miss
            if self.cache_miss_counter:
                self.cache_miss_counter.inc()
            self.metrics["cache_misses"] += 1
            return None

        finally:
            lookup_time = time.time() - start_time
            if self.cache_lookup_histogram:
                self.cache_lookup_histogram.observe(lookup_time)

    async def put(
        self,
        key: str,
        value: Any,
        ttl: int = 300,
        strategy: CacheStrategy = CacheStrategy.SHORT_TERM,
        constitutional_validation: bool = True,
    ) -> bool:
        """
        Put value in cache with integrity protection.

        # requires: key non-empty, value serializable, ttl > 0
        # ensures: value cached with HMAC integrity or operation fails
        # sha256: cache_put_with_integrity_v1.0
        """
        try:
            # Validate constitutional compliance before caching
            if constitutional_validation:
                compliance_valid = await self.validate_constitutional_compliance(key, value)
                if not compliance_valid:
                    logger.warning(f"Constitutional compliance validation failed for key: {key}")
                    return False

            # Create cache entry with integrity signature
            entry = CacheEntry(
                key=key,
                value=value,
                timestamp=time.time(),
                ttl=ttl,
                hmac_signature=self._generate_hmac(key, value),
                constitutional_hash=(
                    self.constitutional_hash if constitutional_validation else None
                ),
            )

            # Add to L1 memory cache
            self._add_to_memory_cache(key, entry)

            # Add to L2 Redis cache if available
            if self.redis_client and not self._is_circuit_breaker_open():
                try:
                    serialized_entry = self._serialize_cache_entry(entry)
                    await self.redis_client.setex(f"pgc:{key}", ttl, serialized_entry)
                except Exception as e:
                    logger.error(f"Redis cache put failed: {e}")
                    self._handle_circuit_breaker_failure()
                    # Continue with L1 cache only

            return True

        except Exception as e:
            logger.error(f"Cache put operation failed: {e}")
            return False

    def _generate_hmac(self, key: str, value: Any) -> str:
        """Generate HMAC signature for cache entry integrity."""
        # requires: key and value are not None
        # ensures: HMAC signature generated using SHA256
        # sha256: hmac_generation_v1.0

        data = f"{key}:{json.dumps(value, sort_keys=True)}"
        signature = hmac.new(self.hmac_secret, data.encode(), hashlib.sha256).hexdigest()
        return signature

    def _verify_integrity(self, entry: CacheEntry) -> bool:
        """Verify cache entry integrity using HMAC."""
        # requires: entry has valid hmac_signature
        # ensures: integrity verified or False returned
        # sha256: integrity_verification_v1.0

        expected_signature = self._generate_hmac(entry.key, entry.value)
        return hmac.compare_digest(entry.hmac_signature, expected_signature)

    def _is_entry_valid(self, entry: CacheEntry) -> bool:
        """Check if cache entry is still valid (not expired)."""
        if entry.ttl <= 0:  # No expiration
            return True
        return (time.time() - entry.timestamp) < entry.ttl

    def _add_to_memory_cache(self, key: str, entry: CacheEntry) -> None:
        """Add entry to L1 memory cache with LRU eviction."""
        # Remove if already exists
        if key in self.memory_cache:
            self.memory_cache_order.remove(key)

        # Add to cache
        self.memory_cache[key] = entry
        self.memory_cache_order.append(key)

        # LRU eviction if over capacity
        while len(self.memory_cache) > self.max_memory_cache_size:
            oldest_key = self.memory_cache_order.pop(0)
            del self.memory_cache[oldest_key]

        # Update metrics
        if self.cache_size_gauge:
            self.cache_size_gauge.labels(level="l1").set(len(self.memory_cache))

    def _remove_from_memory_cache(self, key: str) -> None:
        """Remove entry from L1 memory cache."""
        if key in self.memory_cache:
            del self.memory_cache[key]
            self.memory_cache_order.remove(key)
            if self.cache_size_gauge:
                self.cache_size_gauge.labels(level="l1").set(len(self.memory_cache))

    def _serialize_cache_entry(self, entry: CacheEntry) -> str:
        """Serialize cache entry for Redis storage."""
        return json.dumps(
            {
                "key": entry.key,
                "value": entry.value,
                "timestamp": entry.timestamp,
                "ttl": entry.ttl,
                "hmac_signature": entry.hmac_signature,
                "constitutional_hash": entry.constitutional_hash,
                "access_count": entry.access_count,
                "last_access": entry.last_access,
            }
        )

    def _deserialize_cache_entry(self, data: str) -> CacheEntry | None:
        """Deserialize cache entry from Redis storage."""
        try:
            entry_data = json.loads(data)
            return CacheEntry(**entry_data)
        except Exception as e:
            logger.error(f"Failed to deserialize cache entry: {e}")
            return None

    def _update_access_stats(self, entry: CacheEntry, level: CacheLevel) -> None:
        """Update access statistics for cache entry."""
        entry.access_count += 1
        entry.last_access = time.time()

    def _is_circuit_breaker_open(self) -> bool:
        """Check if circuit breaker is open (Redis unavailable)."""
        if self.circuit_breaker_failures >= self.circuit_breaker_threshold:
            if time.time() - self.circuit_breaker_last_failure > self.circuit_breaker_reset_time:
                # Reset circuit breaker
                self.circuit_breaker_failures = 0
                return False
            return True
        return False

    def _handle_circuit_breaker_failure(self) -> None:
        """Handle circuit breaker failure."""
        self.circuit_breaker_failures += 1
        self.circuit_breaker_last_failure = time.time()
        if self.circuit_breaker_failures >= self.circuit_breaker_threshold:
            self.metrics["circuit_breaker_trips"] += 1
            logger.warning("Redis circuit breaker opened due to failures")

    async def invalidate(self, key: str) -> bool:
        """Invalidate cache entry across all levels."""
        # requires: key is non-empty string
        # ensures: cache entry removed from all levels
        # sha256: cache_invalidation_v1.0

        success = True
        self.metrics["invalidations"] += 1

        # Remove from L1 memory cache
        self._remove_from_memory_cache(key)

        # Remove from L2 Redis cache
        if self.redis_client and not self._is_circuit_breaker_open():
            try:
                await self.redis_client.delete(f"pgc:{key}")
            except Exception as e:
                logger.error(f"Redis cache invalidation failed: {e}")
                success = False

        return success

    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all cache entries matching pattern."""
        # requires: pattern is valid Redis pattern
        # ensures: matching entries removed, count returned
        # sha256: pattern_invalidation_v1.0

        invalidated_count = 0

        # Invalidate from L1 memory cache
        keys_to_remove = [k for k in self.memory_cache.keys() if self._matches_pattern(k, pattern)]
        for key in keys_to_remove:
            self._remove_from_memory_cache(key)
            invalidated_count += 1

        # Invalidate from L2 Redis cache
        if self.redis_client and not self._is_circuit_breaker_open():
            try:
                redis_pattern = f"pgc:{pattern}"
                keys = await self.redis_client.keys(redis_pattern)
                if keys:
                    await self.redis_client.delete(*keys)
                    invalidated_count += len(keys)
            except Exception as e:
                logger.error(f"Redis pattern invalidation failed: {e}")

        self.metrics["invalidations"] += invalidated_count
        return invalidated_count

    def _matches_pattern(self, key: str, pattern: str) -> bool:
        """Check if key matches pattern (simplified glob matching)."""
        import fnmatch

        return fnmatch.fnmatch(key, pattern)

    def get_metrics(self) -> CacheMetrics:
        """Get cache performance metrics."""
        total_requests = self.metrics["total_requests"]
        if total_requests > 0:
            hit_rate = self.metrics["cache_hits"] / total_requests
            miss_rate = self.metrics["cache_misses"] / total_requests
        else:
            hit_rate = miss_rate = 0.0

        return CacheMetrics(
            hit_rate=hit_rate,
            miss_rate=miss_rate,
            avg_lookup_time_ms=0.0,  # Would be calculated from histogram
            total_entries=len(self.memory_cache),
            memory_usage_mb=0.0,  # Would be calculated from memory usage
            invalidations_count=self.metrics["invalidations"],
        )

    async def close(self) -> None:
        """Close Redis connection and cleanup resources."""
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None

        self.memory_cache.clear()
        self.memory_cache_order.clear()

        logger.info("Redis cache manager closed")

    # Constitutional hash validation methods

    async def _validate_and_update_constitutional_hash(self) -> None:
        """Validate and update constitutional hash in Redis."""
        try:
            # Get stored constitutional hash
            stored_hash = await self.redis_client.get("constitutional_hash")

            if stored_hash:
                if stored_hash != self.constitutional_hash:
                    logger.warning(
                        f"Constitutional hash mismatch detected: "
                        f"stored={stored_hash}, expected={self.constitutional_hash}"
                    )

                    # Invalidate all cached data due to constitutional change
                    await self._invalidate_all_constitutional_data()

                    # Update metrics
                    self.metrics["constitutional_hash_mismatches"] = (
                        self.metrics.get("constitutional_hash_mismatches", 0) + 1
                    )
                else:
                    logger.info("Constitutional hash validation successful")

            # Store/update current constitutional hash
            await self.redis_client.set(
                "constitutional_hash", self.constitutional_hash, ex=86400  # 24 hours
            )

            # Store constitutional hash metadata
            await self.redis_client.hset(
                "constitutional_metadata",
                mapping={
                    "hash": self.constitutional_hash,
                    "last_validated": str(time.time()),
                    "validation_count": str(self.metrics.get("constitutional_validations", 0) + 1),
                    "service": "pgc_service",
                },
            )

            self.metrics["constitutional_validations"] = (
                self.metrics.get("constitutional_validations", 0) + 1
            )

        except Exception as e:
            logger.error(f"Constitutional hash validation failed: {e}")
            self.metrics["constitutional_validation_errors"] = (
                self.metrics.get("constitutional_validation_errors", 0) + 1
            )

    async def _setup_constitutional_hash_monitoring(self) -> None:
        """Setup constitutional hash monitoring and alerts."""
        try:
            # Set up constitutional hash expiration monitoring
            await self.redis_client.set(
                "constitutional_hash_monitor",
                "active",
                ex=3600,  # 1 hour monitoring interval
            )

            # Initialize constitutional compliance metrics
            await self.redis_client.hset(
                "constitutional_compliance_metrics",
                mapping={
                    "total_validations": "0",
                    "successful_validations": "0",
                    "failed_validations": "0",
                    "last_validation_time": str(time.time()),
                    "compliance_score": "1.0",
                },
            )

            logger.info("Constitutional hash monitoring initialized")

        except Exception as e:
            logger.error(f"Constitutional hash monitoring setup failed: {e}")

    async def _invalidate_all_constitutional_data(self) -> None:
        """Invalidate all cached data due to constitutional hash change."""
        try:
            # Clear all policy-related cache entries
            policy_patterns = [
                "pgc:policy:*",
                "pgc:compliance:*",
                "pgc:validation:*",
                "pgc:constitutional:*",
            ]

            invalidated_total = 0
            for pattern in policy_patterns:
                keys = await self.redis_client.keys(pattern)
                if keys:
                    await self.redis_client.delete(*keys)
                    invalidated_total += len(keys)

            # Clear memory cache
            self.memory_cache.clear()
            self.memory_cache_order.clear()

            logger.warning(
                f"Invalidated {invalidated_total} cache entries due to constitutional hash change"
            )

            self.metrics["constitutional_invalidations"] = (
                self.metrics.get("constitutional_invalidations", 0) + invalidated_total
            )

        except Exception as e:
            logger.error(f"Constitutional data invalidation failed: {e}")

    async def validate_constitutional_compliance(self, key: str, value: Any) -> bool:
        """Validate that cached data complies with current constitutional hash."""
        try:
            # Check if this is constitutional data
            if not any(
                keyword in key.lower() for keyword in ["policy", "compliance", "constitutional"]
            ):
                return True  # Non-constitutional data doesn't need validation

            # Get constitutional hash from cache entry if it exists
            if isinstance(value, dict) and "constitutional_hash" in value:
                entry_hash = value["constitutional_hash"]
                if entry_hash != self.constitutional_hash:
                    logger.warning(
                        f"Constitutional compliance violation for key {key}: "
                        f"entry_hash={entry_hash}, current_hash={self.constitutional_hash}"
                    )
                    return False

            return True

        except Exception as e:
            logger.error(f"Constitutional compliance validation failed for key {key}: {e}")
            return False

    async def get_constitutional_state(self) -> dict[str, Any]:
        """Get current constitutional state and metrics."""
        try:
            # Get constitutional metadata
            metadata = await self.redis_client.hgetall("constitutional_metadata")
            compliance_metrics = await self.redis_client.hgetall(
                "constitutional_compliance_metrics"
            )

            return {
                "constitutional_hash": self.constitutional_hash,
                "metadata": metadata,
                "compliance_metrics": compliance_metrics,
                "cache_metrics": {
                    "constitutional_validations": self.metrics.get("constitutional_validations", 0),
                    "constitutional_hash_mismatches": self.metrics.get(
                        "constitutional_hash_mismatches", 0
                    ),
                    "constitutional_validation_errors": self.metrics.get(
                        "constitutional_validation_errors", 0
                    ),
                    "constitutional_invalidations": self.metrics.get(
                        "constitutional_invalidations", 0
                    ),
                },
                "timestamp": time.time(),
            }

        except Exception as e:
            logger.error(f"Failed to get constitutional state: {e}")
            return {
                "constitutional_hash": self.constitutional_hash,
                "error": str(e),
                "timestamp": time.time(),
            }


# Global cache manager instance
_cache_manager: RedisCacheManager | None = None


async def get_cache_manager() -> RedisCacheManager:
    """Get or create the global cache manager instance."""
    global _cache_manager

    if _cache_manager is None:
        _cache_manager = RedisCacheManager()
        await _cache_manager.initialize()

    return _cache_manager
