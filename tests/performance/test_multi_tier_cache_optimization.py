"""
Multi-Tier Cache Performance Optimization Tests
Constitutional Hash: cdd01ef066bc6cf2

Tests for Priority 3: Performance Issues - Phase 1: Multi-Tier Caching Implementation

Validates:
- Sub-5ms P99 latency targets
- >85% cache hit rate achievement
- Constitutional validation caching performance
- JWT validation caching performance
- Memory cache vs Redis cache performance
- Cache warming effectiveness
"""

import asyncio
import json
import pytest
import time
import statistics
from typing import Dict, List, Any
from unittest.mock import AsyncMock, patch

# Import the multi-tier cache implementation
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from services.shared.performance.multi_tier_cache import (
    MultiTierCache,
    get_cache,
    cache_constitutional_validation,
    get_cached_constitutional_validation,
    cache_jwt_validation,
    get_cached_jwt_validation,
    CONSTITUTIONAL_HASH,
    PERFORMANCE_TARGETS
)

# Test configuration
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
TEST_ITERATIONS = 1000
CONCURRENT_USERS = 50
LATENCY_TARGET_MS = 5.0
CACHE_HIT_RATE_TARGET = 0.85


class TestMultiTierCachePerformance:
    """Test suite for multi-tier cache performance optimization"""

    @pytest.fixture
    async def cache_instance(self):
        """Create a test cache instance"""
        cache = MultiTierCache(redis_url="redis://localhost:6389/0")
        await cache.initialize()
        yield cache
        # Cleanup
        if cache.redis_client:
            await cache.redis_client.flushdb()
            await cache.redis_client.close()

    @pytest.mark.asyncio
    async def test_l1_memory_cache_latency(self, cache_instance):
        """Test L1 memory cache achieves sub-millisecond latency"""
        cache = cache_instance
        
        # Warm the cache
        test_key = "test_l1_performance"
        test_value = {"constitutional_hash": CONSTITUTIONAL_HASH, "result": "valid"}
        await cache.set(test_key, test_value, "constitutional_hash")
        
        # Measure L1 cache latency
        latencies = []
        for i in range(100):
            start_time = time.perf_counter()
            result = await cache.get(test_key, "constitutional_hash")
            end_time = time.perf_counter()
            
            latency_ms = (end_time - start_time) * 1000
            latencies.append(latency_ms)
            
            assert result is not None
            assert result["constitutional_hash"] == CONSTITUTIONAL_HASH

        # Validate L1 cache performance
        avg_latency = statistics.mean(latencies)
        p99_latency = statistics.quantiles(latencies, n=100)[98]  # 99th percentile
        
        print(f"L1 Cache Performance:")
        print(f"  Average latency: {avg_latency:.3f}ms")
        print(f"  P99 latency: {p99_latency:.3f}ms")
        print(f"  Target: <{PERFORMANCE_TARGETS['l1_cache_latency_ms']}ms")
        
        # Assert performance targets
        assert avg_latency < PERFORMANCE_TARGETS['l1_cache_latency_ms'], f"L1 cache average latency {avg_latency:.3f}ms exceeds target {PERFORMANCE_TARGETS['l1_cache_latency_ms']}ms"
        assert p99_latency < 1.0, f"L1 cache P99 latency {p99_latency:.3f}ms should be sub-millisecond"

    @pytest.mark.asyncio
    async def test_l2_redis_cache_latency(self, cache_instance):
        """Test L2 Redis cache achieves <2ms latency"""
        cache = cache_instance
        
        # Clear L1 cache to force L2 access
        cache.memory_cache.clear()
        
        # Set value in Redis only
        test_key = "test_l2_performance"
        test_value = {"constitutional_hash": CONSTITUTIONAL_HASH, "result": "valid"}
        
        if cache.redis_client:
            await cache.redis_client.set(
                cache._generate_cache_key(test_key, "constitutional_hash"),
                json.dumps(test_value),
                ex=3600
            )
        
        # Measure L2 cache latency
        latencies = []
        for i in range(100):
            # Clear L1 to force L2 access
            cache_key = cache._generate_cache_key(test_key, "constitutional_hash")
            if cache_key in cache.memory_cache:
                del cache.memory_cache[cache_key]
            
            start_time = time.perf_counter()
            result = await cache.get(test_key, "constitutional_hash")
            end_time = time.perf_counter()
            
            latency_ms = (end_time - start_time) * 1000
            latencies.append(latency_ms)
            
            assert result is not None
            assert result["constitutional_hash"] == CONSTITUTIONAL_HASH

        # Validate L2 cache performance
        avg_latency = statistics.mean(latencies)
        p99_latency = statistics.quantiles(latencies, n=100)[98]
        
        print(f"L2 Cache Performance:")
        print(f"  Average latency: {avg_latency:.3f}ms")
        print(f"  P99 latency: {p99_latency:.3f}ms")
        print(f"  Target: <{PERFORMANCE_TARGETS['l2_cache_latency_ms']}ms")
        
        # Assert performance targets
        assert avg_latency < PERFORMANCE_TARGETS['l2_cache_latency_ms'], f"L2 cache average latency {avg_latency:.3f}ms exceeds target {PERFORMANCE_TARGETS['l2_cache_latency_ms']}ms"
        assert p99_latency < PERFORMANCE_TARGETS['l2_cache_latency_ms'], f"L2 cache P99 latency {p99_latency:.3f}ms exceeds target {PERFORMANCE_TARGETS['l2_cache_latency_ms']}ms"

    @pytest.mark.asyncio
    async def test_constitutional_validation_caching_performance(self, cache_instance):
        """Test constitutional validation caching achieves performance targets"""
        
        # Test data
        policy_content = "constitutional_policy_test"
        input_data = "test_input_data"
        validation_result = {
            "valid": True,
            "score": 1.0,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "timestamp": time.time()
        }
        
        # Cache the validation result
        cache_success = await cache_constitutional_validation(policy_content, input_data, validation_result)
        assert cache_success, "Failed to cache constitutional validation result"
        
        # Measure retrieval performance
        latencies = []
        cache_hits = 0
        
        for i in range(TEST_ITERATIONS):
            start_time = time.perf_counter()
            cached_result = await get_cached_constitutional_validation(policy_content, input_data)
            end_time = time.perf_counter()
            
            latency_ms = (end_time - start_time) * 1000
            latencies.append(latency_ms)
            
            if cached_result is not None:
                cache_hits += 1
                assert cached_result["constitutional_hash"] == CONSTITUTIONAL_HASH
                assert cached_result["valid"] == True

        # Calculate performance metrics
        cache_hit_rate = cache_hits / TEST_ITERATIONS
        avg_latency = statistics.mean(latencies)
        p99_latency = statistics.quantiles(latencies, n=100)[98]
        
        print(f"Constitutional Validation Caching Performance:")
        print(f"  Cache hit rate: {cache_hit_rate:.1%}")
        print(f"  Average latency: {avg_latency:.3f}ms")
        print(f"  P99 latency: {p99_latency:.3f}ms")
        print(f"  Targets: >{CACHE_HIT_RATE_TARGET:.0%} hit rate, <{LATENCY_TARGET_MS}ms P99")
        
        # Assert performance targets
        assert cache_hit_rate >= CACHE_HIT_RATE_TARGET, f"Cache hit rate {cache_hit_rate:.1%} below target {CACHE_HIT_RATE_TARGET:.0%}"
        assert p99_latency < LATENCY_TARGET_MS, f"P99 latency {p99_latency:.3f}ms exceeds target {LATENCY_TARGET_MS}ms"

    @pytest.mark.asyncio
    async def test_jwt_validation_caching_performance(self, cache_instance):
        """Test JWT validation caching achieves performance targets"""
        
        # Test data
        token_hash = "test_jwt_token_hash_12345"
        validation_result = {
            "valid": True,
            "user_id": "test_user",
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "expires_at": time.time() + 3600
        }
        
        # Cache the JWT validation result
        cache_success = await cache_jwt_validation(token_hash, validation_result)
        assert cache_success, "Failed to cache JWT validation result"
        
        # Measure retrieval performance
        latencies = []
        cache_hits = 0
        
        for i in range(TEST_ITERATIONS):
            start_time = time.perf_counter()
            cached_result = await get_cached_jwt_validation(token_hash)
            end_time = time.perf_counter()
            
            latency_ms = (end_time - start_time) * 1000
            latencies.append(latency_ms)
            
            if cached_result is not None:
                cache_hits += 1
                assert cached_result["constitutional_hash"] == CONSTITUTIONAL_HASH
                assert cached_result["valid"] == True

        # Calculate performance metrics
        cache_hit_rate = cache_hits / TEST_ITERATIONS
        avg_latency = statistics.mean(latencies)
        p99_latency = statistics.quantiles(latencies, n=100)[98]
        
        print(f"JWT Validation Caching Performance:")
        print(f"  Cache hit rate: {cache_hit_rate:.1%}")
        print(f"  Average latency: {avg_latency:.3f}ms")
        print(f"  P99 latency: {p99_latency:.3f}ms")
        print(f"  Targets: >{CACHE_HIT_RATE_TARGET:.0%} hit rate, <{LATENCY_TARGET_MS}ms P99")
        
        # Assert performance targets
        assert cache_hit_rate >= CACHE_HIT_RATE_TARGET, f"Cache hit rate {cache_hit_rate:.1%} below target {CACHE_HIT_RATE_TARGET:.0%}"
        assert p99_latency < LATENCY_TARGET_MS, f"P99 latency {p99_latency:.3f}ms exceeds target {LATENCY_TARGET_MS}ms"

    @pytest.mark.asyncio
    async def test_concurrent_cache_performance(self, cache_instance):
        """Test cache performance under concurrent load"""
        cache = cache_instance
        
        # Pre-populate cache with test data
        test_data = {}
        for i in range(100):
            key = f"concurrent_test_{i}"
            value = {"id": i, "constitutional_hash": CONSTITUTIONAL_HASH}
            await cache.set(key, value, "performance_test")
            test_data[key] = value

        async def concurrent_cache_operations():
            """Perform concurrent cache operations"""
            latencies = []
            cache_hits = 0
            
            for i in range(20):  # 20 operations per concurrent user
                key = f"concurrent_test_{i % 100}"
                
                start_time = time.perf_counter()
                result = await cache.get(key, "performance_test")
                end_time = time.perf_counter()
                
                latency_ms = (end_time - start_time) * 1000
                latencies.append(latency_ms)
                
                if result is not None:
                    cache_hits += 1
            
            return latencies, cache_hits

        # Run concurrent operations
        tasks = [concurrent_cache_operations() for _ in range(CONCURRENT_USERS)]
        results = await asyncio.gather(*tasks)
        
        # Aggregate results
        all_latencies = []
        total_cache_hits = 0
        total_operations = 0
        
        for latencies, cache_hits in results:
            all_latencies.extend(latencies)
            total_cache_hits += cache_hits
            total_operations += len(latencies)
        
        # Calculate performance metrics
        cache_hit_rate = total_cache_hits / total_operations
        avg_latency = statistics.mean(all_latencies)
        p99_latency = statistics.quantiles(all_latencies, n=100)[98]
        
        print(f"Concurrent Cache Performance ({CONCURRENT_USERS} users):")
        print(f"  Total operations: {total_operations}")
        print(f"  Cache hit rate: {cache_hit_rate:.1%}")
        print(f"  Average latency: {avg_latency:.3f}ms")
        print(f"  P99 latency: {p99_latency:.3f}ms")
        print(f"  Targets: >{CACHE_HIT_RATE_TARGET:.0%} hit rate, <{LATENCY_TARGET_MS}ms P99")
        
        # Assert performance targets under load
        assert cache_hit_rate >= CACHE_HIT_RATE_TARGET, f"Concurrent cache hit rate {cache_hit_rate:.1%} below target {CACHE_HIT_RATE_TARGET:.0%}"
        assert p99_latency < LATENCY_TARGET_MS, f"Concurrent P99 latency {p99_latency:.3f}ms exceeds target {LATENCY_TARGET_MS}ms"

    @pytest.mark.asyncio
    async def test_cache_warming_effectiveness(self, cache_instance):
        """Test cache warming improves performance"""
        cache = cache_instance
        
        # Test constitutional hash validation performance after warming
        start_time = time.perf_counter()
        result = await cache.get("constitutional_hash_validation", "constitutional_hash")
        end_time = time.perf_counter()
        
        latency_ms = (end_time - start_time) * 1000
        
        print(f"Cache Warming Effectiveness:")
        print(f"  Constitutional hash validation latency: {latency_ms:.3f}ms")
        print(f"  Cache warmed: {cache.cache_warmed}")
        print(f"  Target: <{PERFORMANCE_TARGETS['l1_cache_latency_ms']}ms")
        
        # Assert cache warming is effective
        assert cache.cache_warmed, "Cache should be warmed during initialization"
        assert result is not None, "Pre-warmed constitutional validation should be available"
        assert latency_ms < PERFORMANCE_TARGETS['l1_cache_latency_ms'], f"Warmed cache latency {latency_ms:.3f}ms exceeds target"

    @pytest.mark.asyncio
    async def test_cache_metrics_accuracy(self, cache_instance):
        """Test cache metrics are accurately tracked"""
        cache = cache_instance
        
        # Perform known cache operations
        test_key = "metrics_test"
        test_value = {"constitutional_hash": CONSTITUTIONAL_HASH}
        
        # Cache miss (first access)
        result1 = await cache.get(test_key, "test")
        assert result1 is None
        
        # Cache set
        await cache.set(test_key, test_value, "test")
        
        # Cache hit (L1)
        result2 = await cache.get(test_key, "test")
        assert result2 is not None
        
        # Get metrics
        metrics = await cache.get_metrics()
        
        print(f"Cache Metrics:")
        print(f"  L1 hits: {metrics.l1_hits}")
        print(f"  L1 misses: {metrics.l1_misses}")
        print(f"  L2 hits: {metrics.l2_hits}")
        print(f"  L2 misses: {metrics.l2_misses}")
        print(f"  Total requests: {metrics.total_requests}")
        print(f"  Average latency: {metrics.avg_latency_ms:.3f}ms")
        print(f"  Constitutional hash: {metrics.constitutional_hash}")
        
        # Assert metrics accuracy
        assert metrics.constitutional_hash == CONSTITUTIONAL_HASH
        assert metrics.total_requests > 0
        assert metrics.avg_latency_ms > 0
        assert (metrics.l1_hits + metrics.l1_misses + metrics.l2_hits + metrics.l2_misses) > 0


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "--tb=short"])
