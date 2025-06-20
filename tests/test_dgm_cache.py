"""
Test suite for DGM cache implementation.
"""

import asyncio
import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from services.core.dgm_service.dgm_service.cache import (
    DGMCacheManager,
    CacheStrategy,
    CacheTier,
    initialize_cache_manager,
    close_cache_manager
)
from services.core.dgm_service.dgm_service.cache.performance_cache import (
    PerformanceMetricsCache,
    initialize_performance_cache
)
from services.core.dgm_service.dgm_service.cache.bandit_cache import (
    BanditStateCache,
    initialize_bandit_cache
)


class TestDGMCacheManager:
    """Test suite for DGM cache manager."""
    
    @pytest.fixture
    def cache_manager(self):
        """Create cache manager instance for testing."""
        return DGMCacheManager(
            redis_url="redis://localhost:6379/15",  # Test database
            max_memory_cache_size=100,
            default_ttl=300,
            constitutional_hash="cdd01ef066bc6cf2"
        )
    
    @pytest.fixture
    async def initialized_cache_manager(self, cache_manager):
        """Create and initialize cache manager."""
        # Mock Redis for testing
        with patch('redis.asyncio.from_url') as mock_redis:
            mock_client = AsyncMock()
            mock_client.ping.return_value = True
            mock_client.get.return_value = None
            mock_client.set.return_value = True
            mock_client.setex.return_value = True
            mock_client.delete.return_value = 1
            mock_client.exists.return_value = 0
            mock_redis.return_value = mock_client
            
            await cache_manager.initialize()
            yield cache_manager
            await cache_manager.close()
    
    def test_cache_manager_initialization(self, cache_manager):
        """Test cache manager initialization."""
        assert cache_manager.redis_url == "redis://localhost:6379/15"
        assert cache_manager.max_memory_cache_size == 100
        assert cache_manager.default_ttl == 300
        assert cache_manager.constitutional_hash == "cdd01ef066bc6cf2"
        assert cache_manager.cache_strategy == CacheStrategy.ADAPTIVE
    
    def test_cache_config_setup(self, cache_manager):
        """Test cache configuration setup."""
        config = cache_manager._get_cache_config("performance_metrics")
        assert config["ttl"] == 3600
        assert config["strategy"] == CacheStrategy.WRITE_THROUGH
        assert config["compression"] is True
        assert config["tier"] == CacheTier.L2_REDIS
        
        config = cache_manager._get_cache_config("bandit_states")
        assert config["ttl"] == 1800
        assert config["tier"] == CacheTier.L1_MEMORY
    
    def test_integrity_hash_generation(self, cache_manager):
        """Test integrity hash generation and verification."""
        test_value = {"test": "data", "number": 42}
        
        hash1 = cache_manager._generate_integrity_hash(test_value)
        hash2 = cache_manager._generate_integrity_hash(test_value)
        
        # Same data should produce same hash
        assert hash1 == hash2
        
        # Verification should work
        assert cache_manager._verify_integrity_hash(test_value, hash1)
        
        # Different data should produce different hash
        different_value = {"test": "different", "number": 42}
        hash3 = cache_manager._generate_integrity_hash(different_value)
        assert hash1 != hash3
        
        # Verification should fail for wrong hash
        assert not cache_manager._verify_integrity_hash(different_value, hash1)
    
    @pytest.mark.asyncio
    async def test_memory_cache_operations(self, initialized_cache_manager):
        """Test memory cache operations."""
        cache = initialized_cache_manager
        
        # Test set and get
        test_key = "test:memory:key"
        test_value = {"data": "test", "timestamp": time.time()}
        
        success = await cache.set(test_key, test_value, cache_type="bandit_states")
        assert success is True
        
        retrieved_value = await cache.get(test_key, cache_type="bandit_states")
        assert retrieved_value == test_value
        
        # Test exists
        exists = await cache.exists(test_key)
        assert exists is True
        
        # Test delete
        deleted = await cache.delete(test_key, cache_type="bandit_states")
        assert deleted is True
        
        # Verify deletion
        retrieved_value = await cache.get(test_key, cache_type="bandit_states")
        assert retrieved_value is None
    
    @pytest.mark.asyncio
    async def test_cache_expiration(self, initialized_cache_manager):
        """Test cache entry expiration."""
        cache = initialized_cache_manager
        
        test_key = "test:expiration:key"
        test_value = {"data": "expires"}
        
        # Set with short TTL
        await cache.set(test_key, test_value, ttl=1, cache_type="bandit_states")
        
        # Should be available immediately
        retrieved = await cache.get(test_key, cache_type="bandit_states")
        assert retrieved == test_value
        
        # Wait for expiration
        await asyncio.sleep(1.1)
        
        # Should be expired
        retrieved = await cache.get(test_key, cache_type="bandit_states")
        assert retrieved is None
    
    @pytest.mark.asyncio
    async def test_lru_eviction(self, cache_manager):
        """Test LRU eviction in memory cache."""
        # Set small cache size for testing
        cache_manager.max_memory_cache_size = 3
        
        with patch('redis.asyncio.from_url') as mock_redis:
            mock_client = AsyncMock()
            mock_client.ping.return_value = True
            mock_redis.return_value = mock_client
            
            await cache_manager.initialize()
            
            # Fill cache beyond capacity
            for i in range(5):
                await cache_manager.set(f"key_{i}", f"value_{i}", cache_type="bandit_states")
            
            # Check that only the last 3 entries remain
            assert len(cache_manager.memory_cache) <= 3
            
            # The earliest entries should be evicted
            assert await cache_manager.get("key_0", cache_type="bandit_states") is None
            assert await cache_manager.get("key_1", cache_type="bandit_states") is None
            
            # The latest entries should remain
            assert await cache_manager.get("key_4", cache_type="bandit_states") == "value_4"
            
            await cache_manager.close()
    
    @pytest.mark.asyncio
    async def test_cache_stats(self, initialized_cache_manager):
        """Test cache statistics."""
        cache = initialized_cache_manager
        
        # Perform some operations
        await cache.set("test_key_1", "value_1", cache_type="bandit_states")
        await cache.set("test_key_2", "value_2", cache_type="bandit_states")
        await cache.get("test_key_1", cache_type="bandit_states")
        await cache.get("nonexistent_key", cache_type="bandit_states")
        
        stats = await cache.get_stats()
        
        assert "memory_cache" in stats
        assert "redis_cache" in stats
        assert "metrics" in stats
        assert "constitutional_compliance" in stats
        
        assert stats["metrics"]["sets"] >= 2
        assert stats["metrics"]["hits"] >= 1
        assert stats["metrics"]["misses"] >= 1
        assert stats["constitutional_compliance"]["hash"] == "cdd01ef066bc6cf2"
    
    @pytest.mark.asyncio
    async def test_health_check(self, initialized_cache_manager):
        """Test cache health check."""
        cache = initialized_cache_manager
        
        health = await cache.health_check()
        
        assert "status" in health
        assert "memory_cache" in health
        assert "redis_cache" in health
        assert "constitutional_compliance" in health
        assert "errors" in health
        
        assert health["memory_cache"] is True
        assert health["constitutional_compliance"] is True


class TestPerformanceMetricsCache:
    """Test suite for performance metrics cache."""
    
    @pytest.fixture
    def performance_cache(self):
        """Create performance cache instance."""
        mock_cache_manager = MagicMock()
        mock_cache_manager.set = AsyncMock(return_value=True)
        mock_cache_manager.get = AsyncMock(return_value=None)
        
        return PerformanceMetricsCache(mock_cache_manager)
    
    @pytest.mark.asyncio
    async def test_store_metric(self, performance_cache):
        """Test storing performance metrics."""
        success = await performance_cache.store_metric(
            metric_name="response_time",
            value=150.5,
            tags={"service": "dgm", "endpoint": "/health"},
            service_name="dgm-service"
        )
        
        assert success is True
        
        # Verify cache manager was called
        performance_cache.cache_manager.set.assert_called()
        call_args = performance_cache.cache_manager.set.call_args
        
        assert "response_time" in call_args[0][0]  # Cache key contains metric name
        assert call_args[0][1]["value"] == 150.5  # Metric value
        assert call_args[0][1]["service_name"] == "dgm-service"
    
    @pytest.mark.asyncio
    async def test_get_metric_summary(self, performance_cache):
        """Test getting metric summary."""
        # Mock aggregated data
        mock_metrics = [
            {"avg": 100.0, "count": 10},
            {"avg": 120.0, "count": 15},
            {"avg": 110.0, "count": 12}
        ]
        
        performance_cache.get_metric = AsyncMock(return_value=mock_metrics)
        
        summary = await performance_cache.get_metric_summary("response_time", "1h")
        
        assert summary["metric_name"] == "response_time"
        assert summary["time_range"] == "1h"
        assert summary["count"] == 3
        assert summary["avg"] == 110.0  # Average of averages
        assert summary["min"] == 100.0
        assert summary["max"] == 120.0
        assert summary["constitutional_compliance"] is True
    
    def test_trend_calculation(self, performance_cache):
        """Test trend calculation."""
        # Increasing trend
        increasing_values = [100, 105, 110, 115, 120, 125]
        trend = performance_cache._calculate_trend(increasing_values)
        assert trend == "increasing"
        
        # Decreasing trend
        decreasing_values = [125, 120, 115, 110, 105, 100]
        trend = performance_cache._calculate_trend(decreasing_values)
        assert trend == "decreasing"
        
        # Stable trend
        stable_values = [100, 102, 98, 101, 99, 103]
        trend = performance_cache._calculate_trend(stable_values)
        assert trend == "stable"


class TestBanditStateCache:
    """Test suite for bandit state cache."""
    
    @pytest.fixture
    def bandit_cache(self):
        """Create bandit cache instance."""
        mock_cache_manager = MagicMock()
        mock_cache_manager.set = AsyncMock(return_value=True)
        mock_cache_manager.get = AsyncMock(return_value=None)
        
        return BanditStateCache(mock_cache_manager)
    
    @pytest.mark.asyncio
    async def test_store_bandit_state(self, bandit_cache):
        """Test storing bandit state."""
        state_data = {
            "total_pulls": 10,
            "total_reward": 8.5,
            "average_reward": 0.85,
            "safety_threshold": 0.8
        }
        
        success = await bandit_cache.store_bandit_state(
            context_key="test_context",
            arm_id="arm_1",
            algorithm_type="conservative_bandit",
            state_data=state_data
        )
        
        assert success is True
        
        # Verify cache manager was called
        bandit_cache.cache_manager.set.assert_called()
        call_args = bandit_cache.cache_manager.set.call_args
        
        stored_data = call_args[0][1]
        assert stored_data["context_key"] == "test_context"
        assert stored_data["arm_id"] == "arm_1"
        assert stored_data["algorithm_type"] == "conservative_bandit"
        assert stored_data["total_pulls"] == 10
        assert stored_data["constitutional_hash"] == "cdd01ef066bc6cf2"
    
    def test_validate_state_data(self, bandit_cache):
        """Test state data validation."""
        # Valid state data
        valid_state = {
            "total_pulls": 10,
            "total_reward": 8.5,
            "average_reward": 0.85,
            "safety_threshold": 0.8
        }
        assert bandit_cache._validate_state_data(valid_state) is True
        
        # Missing required field
        invalid_state = {
            "total_pulls": 10,
            "total_reward": 8.5
            # Missing average_reward
        }
        assert bandit_cache._validate_state_data(invalid_state) is False
        
        # Invalid safety threshold
        invalid_threshold = {
            "total_pulls": 10,
            "total_reward": 8.5,
            "average_reward": 0.85,
            "safety_threshold": 1.5  # > 1.0
        }
        assert bandit_cache._validate_state_data(invalid_threshold) is False
    
    @pytest.mark.asyncio
    async def test_update_bandit_reward(self, bandit_cache):
        """Test updating bandit reward."""
        # Mock existing state
        existing_state = {
            "total_pulls": 10,
            "total_reward": 8.5,
            "average_reward": 0.85,
            "safety_threshold": 0.8,
            "constitutional_hash": "cdd01ef066bc6cf2"
        }
        
        bandit_cache.get_bandit_state = AsyncMock(return_value=existing_state)
        bandit_cache.store_bandit_state = AsyncMock(return_value=True)
        
        success = await bandit_cache.update_bandit_reward(
            context_key="test_context",
            arm_id="arm_1",
            algorithm_type="conservative_bandit",
            reward=0.9
        )
        
        assert success is True
        
        # Verify updated state was stored
        bandit_cache.store_bandit_state.assert_called()
        call_args = bandit_cache.store_bandit_state.call_args
        updated_state = call_args[0][3]  # state_data argument
        
        assert updated_state["total_pulls"] == 11
        assert updated_state["total_reward"] == 9.4
        assert abs(updated_state["average_reward"] - 0.8545) < 0.001
        assert updated_state["last_reward"] == 0.9


@pytest.mark.integration
class TestCacheIntegration:
    """Integration tests for cache system."""
    
    @pytest.mark.asyncio
    async def test_cache_manager_integration(self):
        """Test cache manager integration."""
        # This test would require a real Redis instance
        # For now, we'll test the initialization flow
        
        with patch('redis.asyncio.from_url') as mock_redis:
            mock_client = AsyncMock()
            mock_client.ping.return_value = True
            mock_client.get.return_value = None
            mock_client.set.return_value = True
            mock_redis.return_value = mock_client
            
            cache_manager = await initialize_cache_manager(
                redis_url="redis://localhost:6379/15"
            )
            
            assert cache_manager is not None
            assert cache_manager.redis_available is True
            
            # Test specialized caches
            perf_cache = initialize_performance_cache(cache_manager)
            bandit_cache = initialize_bandit_cache(cache_manager)
            
            assert perf_cache is not None
            assert bandit_cache is not None
            
            await close_cache_manager()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
