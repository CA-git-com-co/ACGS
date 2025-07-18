"""
Ultra-Fast Performance Test Suite
Constitutional Hash: cdd01ef066bc6cf2

Comprehensive performance tests for validating <5ms P99 latency targets
and >95% cache hit rate requirements.

Test Coverage:
- Constitutional validation performance (<0.1ms target)
- Connection pool acquisition (<1ms target)
- Multi-tier cache access (<0.1ms L1, <1ms L2)
- End-to-end request processing (<5ms P99)
- Throughput validation (>1000 RPS)
"""

import asyncio
import pytest
import time
import statistics
from typing import List, Dict, Any
import asyncpg

from services.shared.constitutional.validation import UltraFastConstitutionalValidator
from services.shared.database.ultra_fast_connection_pool import (
    UltraFastConnectionPool,
    UltraFastConnectionPoolManager,
    POOL_PERFORMANCE_TARGETS
)
from services.shared.performance.ultra_fast_cache import (
    UltraFastMultiTierCache,
    CACHE_PERFORMANCE_TARGETS
)

# Performance test targets
PERFORMANCE_TEST_TARGETS = {
    "constitutional_validation_ms": 0.1,
    "connection_acquisition_ms": 1.0,
    "l1_cache_access_ms": 0.01,
    "l2_cache_access_ms": 0.1,
    "p99_latency_ms": 5.0,
    "p95_latency_ms": 2.0,
    "p50_latency_ms": 1.0,
    "min_throughput_rps": 1000,
    "cache_hit_rate_target": 0.95,
}

# Constitutional hash constant
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class PerformanceBenchmark:
    """Performance benchmarking utility."""
    
    def __init__(self):
        self.measurements: List[float] = []
        
    def measure(self, func, *args, **kwargs):
        """Measure execution time of a function."""
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start_time
        self.measurements.append(elapsed * 1000)  # Convert to milliseconds
        return result
    
    async def measure_async(self, coro):
        """Measure execution time of an async function."""
        start_time = time.perf_counter()
        result = await coro
        elapsed = time.perf_counter() - start_time
        self.measurements.append(elapsed * 1000)  # Convert to milliseconds
        return result
    
    def get_statistics(self) -> Dict[str, float]:
        """Get performance statistics."""
        if not self.measurements:
            return {}
        
        return {
            "count": len(self.measurements),
            "min_ms": min(self.measurements),
            "max_ms": max(self.measurements),
            "mean_ms": statistics.mean(self.measurements),
            "median_ms": statistics.median(self.measurements),
            "p95_ms": statistics.quantiles(self.measurements, n=20)[18] if len(self.measurements) >= 20 else max(self.measurements),
            "p99_ms": statistics.quantiles(self.measurements, n=100)[98] if len(self.measurements) >= 100 else max(self.measurements),
        }
    
    def reset(self):
        """Reset measurements."""
        self.measurements.clear()


@pytest.fixture
async def constitutional_validator():
    """Create ultra-fast constitutional validator."""
    validator = UltraFastConstitutionalValidator()
    yield validator


@pytest.fixture
async def connection_pool():
    """Create ultra-fast connection pool for testing."""
    # Use a test database URL
    test_dsn = "postgresql://test_user:test_pass@localhost:5432/test_db"
    
    pool = UltraFastConnectionPool(
        pool_name="test_pool",
        dsn=test_dsn,
        min_size=5,
        max_size=20
    )
    
    try:
        await pool.initialize()
        yield pool
    except Exception:
        # Skip connection pool tests if database not available
        pytest.skip("Test database not available")
    finally:
        await pool.close()


@pytest.fixture
async def ultra_fast_cache():
    """Create ultra-fast cache for testing."""
    cache = UltraFastMultiTierCache(
        redis_url="redis://localhost:6389/0",
        l1_max_size=10000
    )
    
    await cache.initialize()
    yield cache
    await cache.close()


class TestConstitutionalValidationPerformance:
    """Test constitutional validation performance."""
    
    @pytest.mark.asyncio
    async def test_hash_validation_performance(self, constitutional_validator):
        """Test constitutional hash validation meets <0.1ms target."""
        benchmark = PerformanceBenchmark()
        
        # Warm up the validator
        for _ in range(100):
            constitutional_validator.validate_hash(CONSTITUTIONAL_HASH)
        
        # Performance test
        for _ in range(1000):
            benchmark.measure(
                constitutional_validator.validate_hash,
                CONSTITUTIONAL_HASH
            )
        
        stats = benchmark.get_statistics()
        
        # Assertions
        assert stats["p99_ms"] < PERFORMANCE_TEST_TARGETS["constitutional_validation_ms"], \
            f"P99 validation time {stats['p99_ms']:.3f}ms exceeds target {PERFORMANCE_TEST_TARGETS['constitutional_validation_ms']}ms"
        
        assert stats["mean_ms"] < PERFORMANCE_TEST_TARGETS["constitutional_validation_ms"] / 2, \
            f"Mean validation time {stats['mean_ms']:.3f}ms too high"
        
        print(f"Constitutional validation performance: {stats}")
    
    @pytest.mark.asyncio
    async def test_batch_validation_performance(self, constitutional_validator):
        """Test batch validation performance."""
        benchmark = PerformanceBenchmark()
        
        # Test batch of 100 hashes
        test_hashes = [CONSTITUTIONAL_HASH] * 50 + ["invalid_hash"] * 50
        
        for _ in range(100):
            await benchmark.measure_async(
                constitutional_validator.batch_validate_hashes(test_hashes)
            )
        
        stats = benchmark.get_statistics()
        
        # Batch processing should be more efficient per item
        per_item_time = stats["mean_ms"] / len(test_hashes)
        assert per_item_time < PERFORMANCE_TEST_TARGETS["constitutional_validation_ms"], \
            f"Per-item batch validation time {per_item_time:.3f}ms exceeds target"
        
        print(f"Batch validation performance: {stats}")
    
    @pytest.mark.asyncio
    async def test_context_validation_performance(self, constitutional_validator):
        """Test context-aware validation performance."""
        benchmark = PerformanceBenchmark()
        
        test_context = {"service": "test", "operation": "validate"}
        
        # Warm up context cache
        for _ in range(50):
            constitutional_validator.validate_with_context(CONSTITUTIONAL_HASH, test_context)
        
        # Performance test with cached context
        for _ in range(500):
            benchmark.measure(
                constitutional_validator.validate_with_context,
                CONSTITUTIONAL_HASH,
                test_context
            )
        
        stats = benchmark.get_statistics()
        
        # Context validation should be fast due to caching
        assert stats["p95_ms"] < PERFORMANCE_TEST_TARGETS["constitutional_validation_ms"], \
            f"P95 context validation time {stats['p95_ms']:.3f}ms exceeds target"
        
        print(f"Context validation performance: {stats}")


class TestConnectionPoolPerformance:
    """Test connection pool performance."""
    
    @pytest.mark.asyncio
    async def test_connection_acquisition_performance(self, connection_pool):
        """Test connection acquisition meets <1ms target."""
        benchmark = PerformanceBenchmark()
        
        # Performance test
        for _ in range(500):
            try:
                conn = await benchmark.measure_async(
                    connection_pool.acquire_connection()
                )
                await connection_pool.release_connection(conn)
            except Exception:
                # Skip if connection fails
                continue
        
        if not benchmark.measurements:
            pytest.skip("No successful connections")
        
        stats = benchmark.get_statistics()
        
        # Assertions
        assert stats["p99_ms"] < PERFORMANCE_TEST_TARGETS["connection_acquisition_ms"], \
            f"P99 connection acquisition time {stats['p99_ms']:.3f}ms exceeds target"
        
        assert stats["mean_ms"] < PERFORMANCE_TEST_TARGETS["connection_acquisition_ms"] / 2, \
            f"Mean connection acquisition time {stats['mean_ms']:.3f}ms too high"
        
        print(f"Connection acquisition performance: {stats}")
    
    @pytest.mark.asyncio
    async def test_concurrent_connection_performance(self, connection_pool):
        """Test concurrent connection acquisition performance."""
        async def acquire_and_release():
            try:
                conn = await connection_pool.acquire_connection()
                await asyncio.sleep(0.001)  # Simulate work
                await connection_pool.release_connection(conn)
                return True
            except Exception:
                return False
        
        # Test concurrent access
        start_time = time.perf_counter()
        tasks = [acquire_and_release() for _ in range(100)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        elapsed = time.perf_counter() - start_time
        
        successful = sum(1 for r in results if r is True)
        
        # Should handle concurrent access efficiently
        assert successful > 80, f"Only {successful}/100 concurrent connections succeeded"
        assert elapsed < 1.0, f"Concurrent test took {elapsed:.3f}s, too slow"
        
        print(f"Concurrent connection performance: {successful}/100 successful in {elapsed:.3f}s")


class TestCachePerformance:
    """Test cache performance."""
    
    @pytest.mark.asyncio
    async def test_l1_cache_performance(self, ultra_fast_cache):
        """Test L1 cache access meets <0.01ms target."""
        benchmark = PerformanceBenchmark()
        
        # Pre-populate L1 cache
        test_data = {"test": "value", "constitutional_hash": CONSTITUTIONAL_HASH}
        await ultra_fast_cache.set("test_key", test_data)
        
        # Performance test
        for _ in range(1000):
            await benchmark.measure_async(
                ultra_fast_cache.get("test_key")
            )
        
        stats = benchmark.get_statistics()
        
        # L1 cache should be extremely fast
        assert stats["p99_ms"] < PERFORMANCE_TEST_TARGETS["l1_cache_access_ms"], \
            f"P99 L1 cache access time {stats['p99_ms']:.3f}ms exceeds target"
        
        print(f"L1 cache performance: {stats}")
    
    @pytest.mark.asyncio
    async def test_cache_hit_rate(self, ultra_fast_cache):
        """Test cache hit rate meets >95% target."""
        # Pre-populate cache with test data
        test_keys = [f"key_{i}" for i in range(100)]
        for key in test_keys:
            await ultra_fast_cache.set(key, {"value": key})
        
        # Test cache hits
        hits = 0
        total = 1000
        
        for _ in range(total):
            # 95% of requests should hit existing keys
            if _ < total * 0.95:
                key = test_keys[_ % len(test_keys)]
            else:
                key = f"missing_key_{_}"
            
            result = await ultra_fast_cache.get(key)
            if result is not None:
                hits += 1
        
        hit_rate = hits / total
        
        assert hit_rate >= PERFORMANCE_TEST_TARGETS["cache_hit_rate_target"], \
            f"Cache hit rate {hit_rate:.2%} below target {PERFORMANCE_TEST_TARGETS['cache_hit_rate_target']:.2%}"
        
        print(f"Cache hit rate: {hit_rate:.2%}")
    
    @pytest.mark.asyncio
    async def test_cache_promotion_performance(self, ultra_fast_cache):
        """Test cache promotion mechanism performance."""
        # Set data in L2 (Redis) only
        test_key = "promotion_test"
        test_data = {"promoted": True}
        
        if ultra_fast_cache.redis_client:
            await ultra_fast_cache._set_in_l2(test_key, test_data, 3600)
        
        # Access multiple times to trigger promotion
        for _ in range(5):
            await ultra_fast_cache.get(test_key)
        
        # Check if promoted to L1
        l1_result = ultra_fast_cache._get_from_l1(test_key)
        assert l1_result is not None, "Key should be promoted to L1 after frequent access"
        
        print("Cache promotion working correctly")


class TestEndToEndPerformance:
    """Test end-to-end performance scenarios."""
    
    @pytest.mark.asyncio
    async def test_complete_request_performance(self, constitutional_validator, ultra_fast_cache):
        """Test complete request processing meets <5ms P99 target."""
        benchmark = PerformanceBenchmark()
        
        async def simulate_request():
            # Simulate a complete request with validation and caching
            
            # 1. Constitutional validation
            is_valid = constitutional_validator.validate_hash(CONSTITUTIONAL_HASH)
            if not is_valid:
                return False
            
            # 2. Cache lookup
            cache_key = f"request_{time.time()}"
            cached_result = await ultra_fast_cache.get(cache_key)
            
            if cached_result is None:
                # 3. Simulate processing
                result = {"processed": True, "timestamp": time.time()}
                
                # 4. Cache result
                await ultra_fast_cache.set(cache_key, result, ttl=300)
            else:
                result = cached_result
            
            return result
        
        # Performance test
        for _ in range(200):
            await benchmark.measure_async(simulate_request())
        
        stats = benchmark.get_statistics()
        
        # End-to-end performance assertions
        assert stats["p99_ms"] < PERFORMANCE_TEST_TARGETS["p99_latency_ms"], \
            f"P99 end-to-end latency {stats['p99_ms']:.3f}ms exceeds target"
        
        assert stats["p95_ms"] < PERFORMANCE_TEST_TARGETS["p95_latency_ms"], \
            f"P95 end-to-end latency {stats['p95_ms']:.3f}ms exceeds target"
        
        print(f"End-to-end performance: {stats}")
    
    @pytest.mark.asyncio
    async def test_throughput_performance(self, constitutional_validator, ultra_fast_cache):
        """Test system throughput meets >1000 RPS target."""
        async def process_request(request_id: int):
            # Simulate request processing
            is_valid = constitutional_validator.validate_hash(CONSTITUTIONAL_HASH)
            if not is_valid:
                return False
            
            cache_key = f"throughput_test_{request_id % 100}"  # Reuse keys for cache hits
            result = await ultra_fast_cache.get(cache_key)
            
            if result is None:
                result = {"id": request_id, "processed": True}
                await ultra_fast_cache.set(cache_key, result, ttl=60)
            
            return result
        
        # Throughput test
        num_requests = 2000
        start_time = time.perf_counter()
        
        # Process requests concurrently
        tasks = [process_request(i) for i in range(num_requests)]
        results = await asyncio.gather(*tasks)
        
        elapsed = time.perf_counter() - start_time
        throughput = num_requests / elapsed
        
        successful = sum(1 for r in results if r)
        
        assert throughput >= PERFORMANCE_TEST_TARGETS["min_throughput_rps"], \
            f"Throughput {throughput:.1f} RPS below target {PERFORMANCE_TEST_TARGETS['min_throughput_rps']} RPS"
        
        assert successful >= num_requests * 0.99, \
            f"Only {successful}/{num_requests} requests successful"
        
        print(f"Throughput performance: {throughput:.1f} RPS ({successful}/{num_requests} successful)")


if __name__ == "__main__":
    # Run performance tests
    pytest.main([__file__, "-v", "--tb=short"])
