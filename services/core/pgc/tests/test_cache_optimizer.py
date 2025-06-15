"""
Comprehensive unit tests for PGC Cache Optimizer
Target: >90% test coverage with performance validation

Tests cover:
- Cache hit/miss scenarios
- Adaptive TTL calculation
- Redis integration
- Performance metrics
- Eviction policies
- Error handling
"""

import asyncio
import os

# Import the module under test
import sys
import time
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from cache_optimizer import (
    CacheEntry,
    CacheStats,
    PolicyCacheOptimizer,
    get_cache_optimizer,
)


class TestCacheEntry:
    """Test CacheEntry functionality."""

    def test_cache_entry_creation(self):
    // requires: Valid input parameters
    // ensures: Correct function execution
    // sha256: func_hash
        """Test cache entry creation and properties."""
        entry = CacheEntry(
            value={"result": "allow"},
            created_at=time.time(),
            last_accessed=time.time(),
            access_count=1,
            ttl=300,
            policy_volatility=0.2,
        )

        assert entry.value == {"result": "allow"}
        assert entry.access_count == 1
        assert entry.ttl == 300
        assert entry.policy_volatility == 0.2
        assert entry.age >= 0
        assert not entry.is_expired

    def test_cache_entry_expiration(self):
    // requires: Valid input parameters
    // ensures: Correct function execution
    // sha256: func_hash
        """Test cache entry expiration logic."""
        # Create entry that's already expired
        past_time = time.time() - 400  # 400 seconds ago
        entry = CacheEntry(
            value={"result": "deny"},
            created_at=past_time,
            last_accessed=past_time,
            access_count=1,
            ttl=300,  # 5 minutes TTL
        )

        assert entry.age > 300
        assert entry.is_expired

    def test_cache_entry_update_access(self):
    // requires: Valid input parameters
    // ensures: Correct function execution
    // sha256: func_hash
        """Test access tracking updates."""
        entry = CacheEntry(
            value={"result": "allow"},
            created_at=time.time(),
            last_accessed=time.time() - 10,
            access_count=1,
            ttl=300,
        )

        original_access_time = entry.last_accessed
        original_count = entry.access_count

        entry.update_access()

        assert entry.last_accessed > original_access_time
        assert entry.access_count == original_count + 1


class TestCacheStats:
    """Test CacheStats functionality."""

    def test_cache_stats_hit_rate_calculation(self):
    // requires: Valid input parameters
    // ensures: Correct function execution
    // sha256: func_hash
        """Test hit rate calculation."""
        stats = CacheStats(total_requests=100, cache_hits=80, cache_misses=20)

        assert stats.hit_rate == 80.0

    def test_cache_stats_zero_requests(self):
    // requires: Valid input parameters
    // ensures: Correct function execution
    // sha256: func_hash
        """Test hit rate with zero requests."""
        stats = CacheStats()
        assert stats.hit_rate == 0.0


class TestPolicyCacheOptimizer:
    """Test PolicyCacheOptimizer functionality."""

    @pytest.fixture
    def cache_optimizer(self):
    // requires: Valid input parameters
    // ensures: Correct function execution
    // sha256: func_hash
        """Create cache optimizer for testing."""
        return PolicyCacheOptimizer(
            max_size=100, default_ttl=300, enable_adaptive_ttl=True
        )

    @pytest.fixture
    def sample_policy_context(self):
    // requires: Valid input parameters
    // ensures: Correct function execution
    // sha256: func_hash
        """Sample policy evaluation context."""
        return {
            "user_id": "user123",
            "action": "read",
            "resource": "document456",
            "timestamp": time.time(),
        }

    def test_cache_key_generation(self, cache_optimizer, sample_policy_context):
    // requires: Valid input parameters
    // ensures: Correct function execution
    // sha256: func_hash
        """Test deterministic cache key generation."""
        policy_id = "POL-001"

        key1 = cache_optimizer._generate_cache_key(policy_id, sample_policy_context)
        key2 = cache_optimizer._generate_cache_key(policy_id, sample_policy_context)

        assert key1 == key2
        assert len(key1) == 16  # SHA256 truncated to 16 chars
        assert isinstance(key1, str)

    def test_adaptive_ttl_calculation(self, cache_optimizer):
    // requires: Valid input parameters
    // ensures: Correct function execution
    // sha256: func_hash
        """Test adaptive TTL based on policy volatility."""
        policy_id = "POL-001"
        base_ttl = 300

        # Test with low volatility (stable policy)
        cache_optimizer._policy_volatility[policy_id] = 0.1
        ttl_low = cache_optimizer._calculate_adaptive_ttl(policy_id, base_ttl)

        # Test with high volatility (unstable policy)
        cache_optimizer._policy_volatility[policy_id] = 0.9
        ttl_high = cache_optimizer._calculate_adaptive_ttl(policy_id, base_ttl)

        # High volatility should result in shorter TTL
        assert ttl_high < ttl_low
        assert ttl_high >= 60  # Minimum TTL
        assert ttl_low <= 3600  # Maximum TTL

    def test_policy_volatility_updates(self, cache_optimizer):
    // requires: Valid input parameters
    // ensures: Correct function execution
    // sha256: func_hash
        """Test policy volatility tracking."""
        policy_id = "POL-001"

        # Initial volatility should be 0.0
        assert cache_optimizer._policy_volatility.get(policy_id, 0.0) == 0.0

        # Cache miss should increase volatility
        cache_optimizer._update_policy_volatility(policy_id, cache_miss=True)
        volatility_after_miss = cache_optimizer._policy_volatility[policy_id]
        assert volatility_after_miss > 0.0

        # Cache hit should decrease volatility
        cache_optimizer._update_policy_volatility(policy_id, cache_miss=False)
        volatility_after_hit = cache_optimizer._policy_volatility[policy_id]
        assert volatility_after_hit < volatility_after_miss

    @pytest.mark.asyncio
    async def test_cache_miss_scenario(self, cache_optimizer, sample_policy_context):
    // requires: Valid input parameters
    // ensures: Correct function execution
    // sha256: func_hash
        """Test cache miss scenario."""
        policy_id = "POL-001"

        # First access should be a cache miss
        result = await cache_optimizer.get(policy_id, sample_policy_context)
        assert result is None

        # Verify stats
        assert cache_optimizer.stats.total_requests == 1
        assert cache_optimizer.stats.cache_misses == 1
        assert cache_optimizer.stats.cache_hits == 0
        assert cache_optimizer.stats.hit_rate == 0.0

    @pytest.mark.asyncio
    async def test_cache_hit_scenario(self, cache_optimizer, sample_policy_context):
    // requires: Valid input parameters
    // ensures: Correct function execution
    // sha256: func_hash
        """Test cache hit scenario."""
        policy_id = "POL-001"
        policy_decision = {"result": "allow", "confidence": 0.95}

        # Store value in cache
        success = await cache_optimizer.set(
            policy_id, sample_policy_context, policy_decision
        )
        assert success

        # Retrieve value from cache (should be a hit)
        result = await cache_optimizer.get(policy_id, sample_policy_context)
        assert result == policy_decision

        # Verify stats
        assert cache_optimizer.stats.cache_hits >= 1
        assert cache_optimizer.stats.hit_rate > 0.0

    @pytest.mark.asyncio
    async def test_cache_eviction(self, cache_optimizer, sample_policy_context):
    // requires: Valid input parameters
    // ensures: Correct function execution
    // sha256: func_hash
        """Test LRU cache eviction."""
        # Fill cache to capacity
        for i in range(cache_optimizer.max_size + 10):
            policy_id = f"POL-{i:03d}"
            context = {**sample_policy_context, "iteration": i}
            decision = {"result": "allow", "policy_id": policy_id}

            await cache_optimizer.set(policy_id, context, decision)

        # Verify cache size doesn't exceed maximum
        assert len(cache_optimizer._cache) <= cache_optimizer.max_size

        # Verify evictions occurred
        assert cache_optimizer.stats.evictions > 0

    @pytest.mark.asyncio
    async def test_cache_invalidation_specific(
        self, cache_optimizer, sample_policy_context
    ):
    // requires: Valid input parameters
    // ensures: Correct function execution
    // sha256: func_hash
        """Test specific cache entry invalidation."""
        policy_id = "POL-001"
        policy_decision = {"result": "allow"}

        # Store and verify
        await cache_optimizer.set(policy_id, sample_policy_context, policy_decision)
        result = await cache_optimizer.get(policy_id, sample_policy_context)
        assert result == policy_decision

        # Invalidate specific entry
        await cache_optimizer.invalidate(policy_id, sample_policy_context)

        # Verify invalidation
        result = await cache_optimizer.get(policy_id, sample_policy_context)
        assert result is None

    @pytest.mark.asyncio
    async def test_cache_invalidation_all_policy(self, cache_optimizer):
    // requires: Valid input parameters
    // ensures: Correct function execution
    // sha256: func_hash
        """Test invalidation of all entries for a policy."""
        policy_id = "POL-001"

        # Store multiple contexts for same policy
        contexts = [
            {"user": "user1", "action": "read"},
            {"user": "user2", "action": "write"},
            {"user": "user3", "action": "delete"},
        ]

        for context in contexts:
            await cache_optimizer.set(policy_id, context, {"result": "allow"})

        # Verify entries exist
        for context in contexts:
            result = await cache_optimizer.get(policy_id, context)
            assert result is not None

        # Invalidate all entries for policy
        await cache_optimizer.invalidate(policy_id)

        # Verify all entries are invalidated
        for context in contexts:
            result = await cache_optimizer.get(policy_id, context)
            assert result is None

    @pytest.mark.asyncio
    async def test_expired_entry_cleanup(self, cache_optimizer, sample_policy_context):
    // requires: Valid input parameters
    // ensures: Correct function execution
    // sha256: func_hash
        """Test cleanup of expired cache entries."""
        policy_id = "POL-001"

        # Store entry with very short TTL
        await cache_optimizer.set(
            policy_id, sample_policy_context, {"result": "allow"}, ttl=1
        )

        # Wait for expiration
        await asyncio.sleep(1.1)

        # Cleanup expired entries
        await cache_optimizer.cleanup_expired_entries()

        # Verify entry was removed
        result = await cache_optimizer.get(policy_id, sample_policy_context)
        assert result is None

    def test_performance_stats(self, cache_optimizer):
    // requires: Valid input parameters
    // ensures: Correct function execution
    // sha256: func_hash
        """Test performance statistics collection."""
        stats = cache_optimizer.get_performance_stats()

        # Verify required fields
        required_fields = [
            "cache_size",
            "max_size",
            "hit_rate_percent",
            "total_requests",
            "cache_hits",
            "cache_misses",
            "evictions",
            "memory_usage_bytes",
            "avg_latency_ms",
            "latency_p50_ms",
            "latency_p95_ms",
            "latency_p99_ms",
            "policy_volatility_count",
            "redis_enabled",
            "adaptive_ttl_enabled",
            "target_hit_rate_percent",
            "target_latency_ms",
            "performance_status",
        ]

        for field in required_fields:
            assert field in stats

        # Verify target values
        assert stats["target_hit_rate_percent"] == 80.0
        assert stats["target_latency_ms"] == 25.0
        assert stats["performance_status"] in ["optimal", "needs_optimization"]


class TestCacheOptimizerIntegration:
    """Integration tests for cache optimizer."""

    @pytest.mark.asyncio
    async def test_global_cache_optimizer_singleton(self):
    // requires: Valid input parameters
    // ensures: Correct function execution
    // sha256: func_hash
        """Test global cache optimizer singleton pattern."""
        optimizer1 = await get_cache_optimizer()
        optimizer2 = await get_cache_optimizer()

        # Should return same instance
        assert optimizer1 is optimizer2

    @pytest.mark.asyncio
    @patch("cache_optimizer.get_redis_client")
    async def test_redis_integration_mock(self, mock_redis_client):
    // requires: Valid input parameters
    // ensures: Correct function execution
    // sha256: func_hash
        """Test Redis integration with mocked client."""
        # Setup mock Redis client
        mock_client = AsyncMock()
        mock_client.get.return_value = {"result": "cached_value"}
        mock_client.set.return_value = True
        mock_redis_client.return_value = mock_client

        # Create cache optimizer with Redis config
        from services.shared.advanced_redis_client import CacheConfig

        redis_config = CacheConfig(redis_url="redis://localhost:6379/2")

        optimizer = PolicyCacheOptimizer(redis_config=redis_config)
        await optimizer.initialize_redis()

        # Test Redis integration
        policy_id = "POL-001"
        context = {"user": "test"}

        # Should call Redis on cache miss
        result = await optimizer.get(policy_id, context)
        mock_client.get.assert_called_once()

        # Should call Redis on cache set
        await optimizer.set(policy_id, context, {"result": "allow"})
        mock_client.set.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=cache_optimizer", "--cov-report=term-missing"])
