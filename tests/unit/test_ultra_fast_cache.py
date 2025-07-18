"""
Unit Tests for Ultra-Fast Multi-Tier Cache
Constitutional Hash: cdd01ef066bc6cf2

Comprehensive test suite for the UltraFastMultiTierCache
covering all caching functionality and performance optimizations.

Test Coverage:
- L1 (memory) cache operations
- L2 (Redis) cache operations  
- Cache promotion and demotion
- Performance metrics and optimization
- TTL and expiration handling
- Concurrent access and thread safety
"""

import asyncio
import pytest
import time
from unittest.mock import AsyncMock, Mock, patch
from typing import Dict, Any

from services.shared.performance.ultra_fast_cache import (
    UltraFastMultiTierCache,
    CacheEntry,
    CacheMetrics,
    CACHE_PERFORMANCE_TARGETS,
    CONSTITUTIONAL_HASH
)
from services.shared.constitutional.validation import UltraFastConstitutionalValidator


class TestCacheEntry:
    """Test suite for CacheEntry."""

    def test_initialization(self):
        """Test cache entry initialization."""
        entry = CacheEntry(
            value="test_value",
            created_at=time.time(),
            last_accessed=time.time()
        )
        
        assert entry.value == "test_value"
        assert entry.access_count == 0
        assert entry.constitutional_hash == CONSTITUTIONAL_HASH

    def test_expiration_check(self):
        """Test cache entry expiration."""
        current_time = time.time()
        
        # Non-expiring entry
        entry = CacheEntry(
            value="test",
            created_at=current_time,
            last_accessed=current_time,
            ttl=None
        )
        assert entry.is_expired() is False
        
        # Expired entry
        entry = CacheEntry(
            value="test",
            created_at=current_time - 100,
            last_accessed=current_time - 100,
            ttl=50  # Expired 50 seconds ago
        )
        assert entry.is_expired() is True
        
        # Non-expired entry
        entry = CacheEntry(
            value="test",
            created_at=current_time,
            last_accessed=current_time,
            ttl=3600  # Expires in 1 hour
        )
        assert entry.is_expired() is False

    def test_touch_functionality(self):
        """Test cache entry touch functionality."""
        entry = CacheEntry(
            value="test",
            created_at=time.time(),
            last_accessed=time.time()
        )
        
        initial_access_count = entry.access_count
        initial_last_accessed = entry.last_accessed
        
        time.sleep(0.001)  # Small delay
        entry.touch()
        
        assert entry.access_count == initial_access_count + 1
        assert entry.last_accessed > initial_last_accessed


class TestCacheMetrics:
    """Test suite for CacheMetrics."""

    def test_initialization(self):
        """Test metrics initialization."""
        metrics = CacheMetrics()
        
        assert metrics.l1_hits == 0
        assert metrics.l1_misses == 0
        assert metrics.l2_hits == 0
        assert metrics.l2_misses == 0
        assert metrics.l3_hits == 0
        assert metrics.l3_misses == 0

    def test_hit_rate_calculation(self):
        """Test overall hit rate calculation."""
        metrics = CacheMetrics()
        
        # No requests
        assert metrics.get_overall_hit_rate() == 0.0
        
        # Add some hits and misses
        metrics.l1_hits = 50
        metrics.l2_hits = 30
        metrics.l3_hits = 10
        metrics.l3_misses = 10
        
        # Total hits: 90, Total requests: 100, Hit rate: 90%
        assert metrics.get_overall_hit_rate() == 0.9

    def test_avg_access_time(self):
        """Test average access time calculation."""
        metrics = CacheMetrics()
        
        # No accesses
        assert metrics.get_avg_access_time_ms() == 0.0
        
        # Add some access times
        metrics.total_accesses = 5
        metrics.total_access_time = 0.005  # 5ms total
        
        assert metrics.get_avg_access_time_ms() == 1.0  # 1ms average


class TestUltraFastMultiTierCache:
    """Test suite for UltraFastMultiTierCache."""

    @pytest.fixture
    def mock_validator(self):
        """Create a mock constitutional validator."""
        validator = Mock(spec=UltraFastConstitutionalValidator)
        validator.validate_hash.return_value = True
        return validator

    @pytest.fixture
    def cache(self, mock_validator):
        """Create a cache instance for testing."""
        return UltraFastMultiTierCache(
            redis_url="redis://localhost:6389/0",
            l1_max_size=1000,
            constitutional_validator=mock_validator
        )

    def test_initialization(self, cache):
        """Test cache initialization."""
        assert cache.constitutional_hash == CONSTITUTIONAL_HASH
        assert cache.l1_max_size == 1000
        assert len(cache.l1_cache) == 0
        assert cache.redis_client is None
        assert cache.prediction_enabled is True

    @pytest.mark.asyncio
    async def test_initialization_with_redis(self, mock_validator):
        """Test cache initialization with Redis."""
        with patch('services.shared.performance.ultra_fast_cache.redis') as mock_redis:
            mock_redis_client = AsyncMock()
            mock_redis_client.ping.return_value = True
            mock_redis.from_url.return_value = mock_redis_client
            
            cache = UltraFastMultiTierCache(
                constitutional_validator=mock_validator
            )
            await cache.initialize()
            
            assert cache.redis_client is not None
            mock_redis_client.ping.assert_called_once()

    @pytest.mark.asyncio
    async def test_initialization_redis_failure(self, mock_validator):
        """Test cache initialization with Redis failure."""
        with patch('services.shared.performance.ultra_fast_cache.redis') as mock_redis:
            mock_redis.from_url.side_effect = Exception("Redis connection failed")
            
            cache = UltraFastMultiTierCache(
                constitutional_validator=mock_validator
            )
            await cache.initialize()
            
            # Should handle Redis failure gracefully
            assert cache.redis_client is None

    def test_l1_cache_set_and_get(self, cache):
        """Test L1 cache set and get operations."""
        # Set value in L1
        cache._set_in_l1("test_key", "test_value", 3600)
        
        # Get value from L1
        result = cache._get_from_l1("test_key")
        
        assert result == "test_value"
        assert "test_key" in cache.l1_cache

    def test_l1_cache_expiration(self, cache):
        """Test L1 cache expiration."""
        # Set value with short TTL
        cache._set_in_l1("test_key", "test_value", 0.001)  # 1ms TTL
        
        # Wait for expiration
        time.sleep(0.002)
        
        # Should return None for expired entry
        result = cache._get_from_l1("test_key")
        assert result is None
        assert "test_key" not in cache.l1_cache

    def test_l1_cache_lru_eviction(self, cache):
        """Test L1 cache LRU eviction."""
        # Fill cache beyond limit
        cache.l1_max_size = 3
        
        for i in range(5):
            cache._set_in_l1(f"key_{i}", f"value_{i}", 3600)
        
        # Should only have 3 entries (max size)
        assert len(cache.l1_cache) == 3
        
        # Should have evicted the oldest entries
        assert "key_0" not in cache.l1_cache
        assert "key_1" not in cache.l1_cache
        assert "key_2" in cache.l1_cache
        assert "key_3" in cache.l1_cache
        assert "key_4" in cache.l1_cache

    @pytest.mark.asyncio
    async def test_l2_cache_operations(self, cache):
        """Test L2 (Redis) cache operations."""
        with patch('services.shared.performance.ultra_fast_cache.redis') as mock_redis:
            mock_redis_client = AsyncMock()
            mock_redis_client.get.return_value = '{"test": "value"}'
            mock_redis_client.setex.return_value = True
            cache.redis_client = mock_redis_client
            
            # Test set
            await cache._set_in_l2("test_key", {"test": "value"}, 3600)
            mock_redis_client.setex.assert_called_once()
            
            # Test get
            result = await cache._get_from_l2("test_key")
            assert result == {"test": "value"}
            mock_redis_client.get.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_cache_get_l1_hit(self, cache):
        """Test cache get with L1 hit."""
        # Pre-populate L1 cache
        cache._set_in_l1("test_key", "test_value", 3600)
        
        result = await cache.get("test_key")
        
        assert result == "test_value"
        assert cache.metrics.l1_hits == 1
        assert cache.metrics.l1_misses == 0

    @pytest.mark.asyncio
    async def test_cache_get_l2_hit(self, cache):
        """Test cache get with L2 hit."""
        with patch('services.shared.performance.ultra_fast_cache.redis') as mock_redis:
            mock_redis_client = AsyncMock()
            mock_redis_client.get.return_value = '"test_value"'
            cache.redis_client = mock_redis_client
            
            result = await cache.get("test_key")
            
            assert result == "test_value"
            assert cache.metrics.l1_misses == 1
            assert cache.metrics.l2_hits == 1

    @pytest.mark.asyncio
    async def test_cache_get_miss(self, cache):
        """Test cache get with complete miss."""
        result = await cache.get("nonexistent_key")
        
        assert result is None
        assert cache.metrics.l1_misses == 1
        assert cache.metrics.l3_misses == 1

    @pytest.mark.asyncio
    async def test_cache_set(self, cache):
        """Test cache set operation."""
        with patch('services.shared.performance.ultra_fast_cache.redis') as mock_redis:
            mock_redis_client = AsyncMock()
            cache.redis_client = mock_redis_client
            
            success = await cache.set("test_key", "test_value", ttl=3600)
            
            assert success is True
            
            # Should be in L1 cache
            l1_result = cache._get_from_l1("test_key")
            assert l1_result == "test_value"
            
            # Should have called Redis set
            mock_redis_client.setex.assert_called_once()

    def test_optimal_ttl_selection(self, cache):
        """Test optimal TTL selection based on data type."""
        # Test different data types
        constitutional_ttl = cache._get_optimal_ttl("constitutional")
        policy_ttl = cache._get_optimal_ttl("policy")
        metrics_ttl = cache._get_optimal_ttl("metrics")
        default_ttl = cache._get_optimal_ttl("unknown_type")
        
        assert constitutional_ttl == 86400  # 24 hours
        assert policy_ttl == 3600          # 1 hour
        assert metrics_ttl == 300          # 5 minutes
        assert default_ttl == CACHE_PERFORMANCE_TARGETS["l2_ttl_default"]

    @pytest.mark.asyncio
    async def test_cache_promotion(self, cache):
        """Test cache promotion from L2 to L1."""
        # Simulate L2 hit that should trigger promotion
        test_key = "promotion_test"
        test_value = "test_value"
        
        # Add to access patterns to trigger promotion
        current_time = time.time()
        cache.access_patterns[test_key] = [
            current_time - 10,
            current_time - 5,
            current_time
        ]  # 3 accesses (meets promotion threshold)
        
        await cache._consider_promotion(test_key, test_value, "default")
        
        # Should be promoted to L1
        l1_result = cache._get_from_l1(test_key)
        assert l1_result == test_value
        assert cache.metrics.promotions == 1

    @pytest.mark.asyncio
    async def test_cache_delete(self, cache):
        """Test cache deletion."""
        with patch('services.shared.performance.ultra_fast_cache.redis') as mock_redis:
            mock_redis_client = AsyncMock()
            cache.redis_client = mock_redis_client
            
            # Set value in L1
            cache._set_in_l1("test_key", "test_value", 3600)
            
            # Delete
            success = await cache.delete("test_key")
            
            assert success is True
            assert cache._get_from_l1("test_key") is None
            mock_redis_client.delete.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_cache_clear_all(self, cache):
        """Test clearing all cache tiers."""
        with patch('services.shared.performance.ultra_fast_cache.redis') as mock_redis:
            mock_redis_client = AsyncMock()
            cache.redis_client = mock_redis_client
            
            # Add some data
            cache._set_in_l1("test_key", "test_value", 3600)
            cache.access_patterns["test_key"] = [time.time()]
            
            await cache.clear_all()
            
            assert len(cache.l1_cache) == 0
            assert len(cache.access_patterns) == 0
            mock_redis_client.flushdb.assert_called_once()

    def test_performance_metrics(self, cache):
        """Test performance metrics collection."""
        # Simulate some cache activity
        cache.metrics.l1_hits = 80
        cache.metrics.l1_misses = 10
        cache.metrics.l2_hits = 5
        cache.metrics.l2_misses = 3
        cache.metrics.l3_misses = 2
        cache.metrics.total_accesses = 100
        cache.metrics.total_access_time = 0.1  # 100ms total
        
        metrics = cache.get_performance_metrics()
        
        assert "performance_summary" in metrics
        assert "tier_performance" in metrics
        assert "cache_statistics" in metrics
        
        perf_summary = metrics["performance_summary"]
        assert perf_summary["overall_hit_rate"] == 0.98  # 98% hit rate
        assert perf_summary["avg_access_time_ms"] == 1.0  # 1ms average

    @pytest.mark.asyncio
    async def test_performance_optimization(self, cache):
        """Test performance optimization."""
        # Simulate poor performance
        cache.metrics.l1_hits = 50
        cache.metrics.l1_misses = 50
        cache.metrics.l2_hits = 30
        cache.metrics.l2_misses = 20
        cache.metrics.l3_misses = 20
        
        # Add some expired entries to L1
        cache._set_in_l1("expired_key", "value", 0.001)
        time.sleep(0.002)
        
        optimization = await cache.optimize_performance()
        
        assert "optimizations_applied" in optimization
        assert "recommendations" in optimization
        assert "current_metrics" in optimization

    @pytest.mark.asyncio
    async def test_health_check_success(self, cache):
        """Test successful health check."""
        with patch('services.shared.performance.ultra_fast_cache.redis') as mock_redis:
            mock_redis_client = AsyncMock()
            mock_redis_client.ping.return_value = True
            cache.redis_client = mock_redis_client
            
            health = await cache.health_check()
            
            assert health["healthy"] is True
            assert health["l1_healthy"] is True
            assert health["l2_healthy"] is True
            assert health["redis_connected"] is True

    @pytest.mark.asyncio
    async def test_health_check_redis_failure(self, cache):
        """Test health check with Redis failure."""
        with patch('services.shared.performance.ultra_fast_cache.redis') as mock_redis:
            mock_redis_client = AsyncMock()
            mock_redis_client.ping.side_effect = Exception("Redis failed")
            cache.redis_client = mock_redis_client
            
            health = await cache.health_check()
            
            assert health["healthy"] is True  # L1 still works
            assert health["l1_healthy"] is True
            assert health["l2_healthy"] is False

    @pytest.mark.asyncio
    async def test_concurrent_access(self, cache):
        """Test concurrent cache access."""
        async def cache_worker(worker_id: int):
            results = []
            for i in range(100):
                key = f"worker_{worker_id}_key_{i}"
                value = f"worker_{worker_id}_value_{i}"
                
                # Set and get
                await cache.set(key, value)
                result = await cache.get(key)
                results.append(result == value)
            
            return results
        
        # Run multiple workers concurrently
        tasks = [cache_worker(i) for i in range(5)]
        all_results = await asyncio.gather(*tasks)
        
        # Verify all operations succeeded
        for worker_results in all_results:
            assert all(worker_results)

    def test_access_pattern_tracking(self, cache):
        """Test access pattern tracking for predictive caching."""
        test_key = "pattern_test"
        current_time = time.time()
        
        # Simulate access pattern
        cache._update_access_patterns(test_key)
        
        # Access patterns should be tracked
        assert test_key in cache.access_patterns or not cache.prediction_enabled

    @pytest.mark.asyncio
    async def test_cache_promotion_threshold(self, cache):
        """Test cache promotion threshold logic."""
        test_key = "threshold_test"
        test_value = "test_value"
        
        # Access less than threshold
        current_time = time.time()
        cache.access_patterns[test_key] = [current_time]
        
        await cache._consider_promotion(test_key, test_value, "default")
        
        # Should not be promoted
        assert cache._get_from_l1(test_key) is None
        
        # Access at threshold
        cache.access_patterns[test_key] = [
            current_time - 10,
            current_time - 5,
            current_time
        ]
        
        await cache._consider_promotion(test_key, test_value, "default")
        
        # Should be promoted
        assert cache._get_from_l1(test_key) == test_value

    @pytest.mark.asyncio
    async def test_cache_close(self, cache):
        """Test cache closure."""
        with patch('services.shared.performance.ultra_fast_cache.redis') as mock_redis:
            mock_redis_client = AsyncMock()
            cache.redis_client = mock_redis_client
            
            # Add some data
            cache._set_in_l1("test_key", "test_value", 3600)
            
            await cache.close()
            
            mock_redis_client.close.assert_called_once()
            assert cache.redis_client is None
            assert len(cache.l1_cache) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
