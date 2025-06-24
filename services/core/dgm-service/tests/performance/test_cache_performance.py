"""
Cache Performance Tests for DGM Service.

Tests Redis cache performance:
- Cache hit/miss ratios
- Response times for cached data
- Cache invalidation performance
- Memory usage optimization
- Concurrent cache access
"""

import asyncio
import statistics
import time
from typing import Any, Dict, List
from unittest.mock import AsyncMock

import pytest
import redis.asyncio as redis
from dgm_service.cache.performance_cache import PerformanceCache
from dgm_service.cache.redis_cache import RedisCache
from dgm_service.config import settings


class CachePerformanceTest:
    """Cache performance testing utilities."""

    def __init__(self):
        self.redis_client = None
        self.cache = None
        self.performance_cache = None

    async def setup(self):
        """Setup cache connections."""
        self.redis_client = redis.from_url(
            settings.REDIS_URL, encoding="utf-8", decode_responses=True
        )
        self.cache = RedisCache(self.redis_client)
        self.performance_cache = PerformanceCache(self.redis_client)

        # Test connection
        await self.redis_client.ping()

    async def teardown(self):
        """Cleanup cache connections."""
        if self.redis_client:
            await self.redis_client.close()

    async def measure_cache_operation(
        self, operation: str, key: str, value: Any = None, ttl: int = None
    ) -> Dict:
        """Measure cache operation performance."""
        start_time = time.perf_counter()

        try:
            if operation == "set":
                await self.cache.set(key, value, ttl=ttl)
                result_value = value
            elif operation == "get":
                result_value = await self.cache.get(key)
            elif operation == "delete":
                await self.cache.delete(key)
                result_value = None
            elif operation == "exists":
                result_value = await self.cache.exists(key)
            else:
                raise ValueError(f"Unsupported operation: {operation}")

            end_time = time.perf_counter()
            execution_time = (end_time - start_time) * 1000  # Convert to milliseconds

            return {
                "operation": operation,
                "execution_time_ms": execution_time,
                "success": True,
                "hit": result_value is not None if operation == "get" else None,
                "key": key,
            }
        except Exception as e:
            end_time = time.perf_counter()
            execution_time = (end_time - start_time) * 1000

            return {
                "operation": operation,
                "execution_time_ms": execution_time,
                "success": False,
                "error": str(e),
                "key": key,
            }

    async def cache_hit_ratio_test(self, num_keys: int = 100, cache_percentage: int = 70) -> Dict:
        """Test cache hit ratio performance."""
        # Populate cache with some keys
        cached_keys = []
        for i in range(int(num_keys * cache_percentage / 100)):
            key = f"test_key_{i}"
            await self.cache.set(key, f"value_{i}", ttl=300)
            cached_keys.append(key)

        # Test all keys (some cached, some not)
        all_keys = [f"test_key_{i}" for i in range(num_keys)]

        start_time = time.perf_counter()
        results = []

        for key in all_keys:
            result = await self.measure_cache_operation("get", key)
            results.append(result)

        end_time = time.perf_counter()
        total_time = (end_time - start_time) * 1000

        # Calculate statistics
        hits = sum(1 for r in results if r.get("hit"))
        misses = len(results) - hits
        hit_ratio = (hits / len(results)) * 100

        avg_hit_time = statistics.mean([r["execution_time_ms"] for r in results if r.get("hit")])
        avg_miss_time = statistics.mean(
            [r["execution_time_ms"] for r in results if not r.get("hit")]
        )

        return {
            "total_keys": num_keys,
            "cached_keys": len(cached_keys),
            "hits": hits,
            "misses": misses,
            "hit_ratio": hit_ratio,
            "avg_hit_time_ms": avg_hit_time,
            "avg_miss_time_ms": avg_miss_time,
            "total_time_ms": total_time,
            "operations_per_second": len(results) / ((end_time - start_time) or 0.001),
        }

    async def concurrent_cache_test(
        self, concurrent_operations: int = 50, operations_per_worker: int = 20
    ) -> Dict:
        """Test concurrent cache access performance."""

        async def cache_worker(worker_id: int):
            results = []
            for i in range(operations_per_worker):
                key = f"worker_{worker_id}_key_{i}"
                value = f"worker_{worker_id}_value_{i}"

                # Mix of operations
                if i % 3 == 0:
                    result = await self.measure_cache_operation("set", key, value, ttl=300)
                elif i % 3 == 1:
                    result = await self.measure_cache_operation("get", key)
                else:
                    result = await self.measure_cache_operation("exists", key)

                results.append(result)
            return results

        start_time = time.perf_counter()

        # Create concurrent workers
        tasks = [cache_worker(i) for i in range(concurrent_operations)]
        all_results = await asyncio.gather(*tasks)

        end_time = time.perf_counter()
        total_time = (end_time - start_time) * 1000

        # Flatten results
        flat_results = [result for worker_results in all_results for result in worker_results]

        execution_times = [r["execution_time_ms"] for r in flat_results if r["success"]]
        success_count = sum(1 for r in flat_results if r["success"])

        return {
            "total_time_ms": total_time,
            "concurrent_workers": concurrent_operations,
            "operations_per_worker": operations_per_worker,
            "total_operations": len(flat_results),
            "successful_operations": success_count,
            "success_rate": (success_count / len(flat_results)) * 100,
            "avg_operation_time_ms": statistics.mean(execution_times) if execution_times else 0,
            "p95_operation_time_ms": (
                self._percentile(execution_times, 95) if execution_times else 0
            ),
            "operations_per_second": len(flat_results) / ((end_time - start_time) or 0.001),
        }

    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of data."""
        sorted_data = sorted(data)
        index = int((percentile / 100) * len(sorted_data))
        return sorted_data[min(index, len(sorted_data) - 1)]


@pytest.fixture
async def cache_test():
    """Fixture for cache performance testing."""
    test = CachePerformanceTest()
    await test.setup()
    yield test
    await test.teardown()


@pytest.mark.performance
@pytest.mark.cache
@pytest.mark.asyncio
async def test_basic_cache_operations_performance(cache_test):
    """Test basic cache operations performance."""
    # Test SET operation
    set_result = await cache_test.measure_cache_operation(
        "set", "perf_test_key", "test_value", ttl=300
    )
    assert set_result["success"], f"Cache SET failed: {set_result.get('error', 'Unknown error')}"
    assert (
        set_result["execution_time_ms"] < 10
    ), f"Cache SET too slow: {set_result['execution_time_ms']}ms"

    # Test GET operation (cache hit)
    get_result = await cache_test.measure_cache_operation("get", "perf_test_key")
    assert get_result["success"], f"Cache GET failed: {get_result.get('error', 'Unknown error')}"
    assert get_result["hit"], "Cache GET should be a hit"
    assert (
        get_result["execution_time_ms"] < 5
    ), f"Cache GET too slow: {get_result['execution_time_ms']}ms"

    # Test EXISTS operation
    exists_result = await cache_test.measure_cache_operation("exists", "perf_test_key")
    assert exists_result[
        "success"
    ], f"Cache EXISTS failed: {exists_result.get('error', 'Unknown error')}"
    assert (
        exists_result["execution_time_ms"] < 5
    ), f"Cache EXISTS too slow: {exists_result['execution_time_ms']}ms"

    # Test DELETE operation
    delete_result = await cache_test.measure_cache_operation("delete", "perf_test_key")
    assert delete_result[
        "success"
    ], f"Cache DELETE failed: {delete_result.get('error', 'Unknown error')}"
    assert (
        delete_result["execution_time_ms"] < 10
    ), f"Cache DELETE too slow: {delete_result['execution_time_ms']}ms"


@pytest.mark.performance
@pytest.mark.cache
@pytest.mark.asyncio
async def test_cache_miss_performance(cache_test):
    """Test cache miss performance."""
    # Test GET operation on non-existent key (cache miss)
    miss_result = await cache_test.measure_cache_operation("get", "non_existent_key")

    assert miss_result[
        "success"
    ], f"Cache miss GET failed: {miss_result.get('error', 'Unknown error')}"
    assert not miss_result["hit"], "Should be a cache miss"
    assert (
        miss_result["execution_time_ms"] < 5
    ), f"Cache miss too slow: {miss_result['execution_time_ms']}ms"


@pytest.mark.performance
@pytest.mark.cache
@pytest.mark.asyncio
async def test_cache_hit_ratio_performance(cache_test):
    """Test cache hit ratio and performance."""
    result = await cache_test.cache_hit_ratio_test(num_keys=200, cache_percentage=75)

    # Validate hit ratio
    expected_hit_ratio = 75  # We cached 75% of keys
    assert (
        abs(result["hit_ratio"] - expected_hit_ratio) < 5
    ), f"Hit ratio not as expected: {result['hit_ratio']}%"

    # Cache hits should be faster than misses
    assert (
        result["avg_hit_time_ms"] < result["avg_miss_time_ms"]
    ), "Cache hits should be faster than misses"
    assert result["avg_hit_time_ms"] < 5, f"Cache hits too slow: {result['avg_hit_time_ms']}ms"

    # Overall performance should be good
    assert (
        result["operations_per_second"] > 1000
    ), f"Cache operations too slow: {result['operations_per_second']} ops/sec"


@pytest.mark.performance
@pytest.mark.cache
@pytest.mark.asyncio
async def test_concurrent_cache_access(cache_test):
    """Test concurrent cache access performance."""
    result = await cache_test.concurrent_cache_test(
        concurrent_operations=30, operations_per_worker=15
    )

    # Concurrent access should maintain high success rate
    assert (
        result["success_rate"] >= 99.0
    ), f"Concurrent cache success rate too low: {result['success_rate']}%"
    assert (
        result["avg_operation_time_ms"] < 10
    ), f"Average concurrent operation too slow: {result['avg_operation_time_ms']}ms"
    assert (
        result["p95_operation_time_ms"] < 20
    ), f"P95 concurrent operation too slow: {result['p95_operation_time_ms']}ms"
    assert (
        result["operations_per_second"] > 500
    ), f"Concurrent operations too slow: {result['operations_per_second']} ops/sec"


@pytest.mark.performance
@pytest.mark.cache
@pytest.mark.asyncio
async def test_large_value_cache_performance(cache_test):
    """Test caching performance with large values."""
    # Create a large value (1MB)
    large_value = "x" * (1024 * 1024)  # 1MB string

    # Test SET with large value
    set_result = await cache_test.measure_cache_operation(
        "set", "large_value_key", large_value, ttl=300
    )
    assert set_result[
        "success"
    ], f"Large value SET failed: {set_result.get('error', 'Unknown error')}"
    assert (
        set_result["execution_time_ms"] < 100
    ), f"Large value SET too slow: {set_result['execution_time_ms']}ms"

    # Test GET with large value
    get_result = await cache_test.measure_cache_operation("get", "large_value_key")
    assert get_result[
        "success"
    ], f"Large value GET failed: {get_result.get('error', 'Unknown error')}"
    assert get_result["hit"], "Large value should be cached"
    assert (
        get_result["execution_time_ms"] < 50
    ), f"Large value GET too slow: {get_result['execution_time_ms']}ms"


@pytest.mark.performance
@pytest.mark.cache
@pytest.mark.asyncio
async def test_performance_cache_specific_operations(cache_test):
    """Test performance cache specific operations."""
    # Test performance metrics caching
    metrics_data = {
        "response_time": 150.5,
        "throughput": 1250.0,
        "error_rate": 0.01,
        "cpu_usage": 45.2,
        "memory_usage": 67.8,
    }

    start_time = time.perf_counter()

    # Cache performance metrics
    await cache_test.performance_cache.cache_metrics("dgm-service", metrics_data, ttl=300)

    # Retrieve cached metrics
    cached_metrics = await cache_test.performance_cache.get_cached_metrics("dgm-service")

    end_time = time.perf_counter()
    total_time = (end_time - start_time) * 1000

    # Validate performance
    assert cached_metrics is not None, "Performance metrics should be cached"
    assert total_time < 20, f"Performance cache operations too slow: {total_time}ms"

    # Test metrics aggregation caching
    aggregation_start = time.perf_counter()

    await cache_test.performance_cache.cache_aggregated_metrics(
        "dgm-service", "hourly", {"avg_response_time": 145.2, "total_requests": 5000}
    )

    cached_aggregation = await cache_test.performance_cache.get_cached_aggregation(
        "dgm-service", "hourly"
    )

    aggregation_end = time.perf_counter()
    aggregation_time = (aggregation_end - aggregation_start) * 1000

    assert cached_aggregation is not None, "Aggregated metrics should be cached"
    assert aggregation_time < 15, f"Aggregation cache operations too slow: {aggregation_time}ms"


@pytest.mark.performance
@pytest.mark.cache
@pytest.mark.slow
@pytest.mark.asyncio
async def test_cache_memory_usage_performance(cache_test):
    """Test cache memory usage and cleanup performance."""
    # Fill cache with many keys
    num_keys = 1000
    key_size = 1024  # 1KB per value

    start_time = time.perf_counter()

    # Populate cache
    for i in range(num_keys):
        key = f"memory_test_key_{i}"
        value = "x" * key_size
        await cache_test.cache.set(key, value, ttl=60)

    populate_time = time.perf_counter() - start_time

    # Test memory info retrieval
    memory_start = time.perf_counter()
    memory_info = await cache_test.redis_client.info("memory")
    memory_time = (time.perf_counter() - memory_start) * 1000

    # Test cleanup performance
    cleanup_start = time.perf_counter()

    # Delete all test keys
    keys_to_delete = [f"memory_test_key_{i}" for i in range(num_keys)]
    if keys_to_delete:
        await cache_test.redis_client.delete(*keys_to_delete)

    cleanup_time = (time.perf_counter() - cleanup_start) * 1000

    # Validate performance
    assert populate_time < 30, f"Cache population too slow: {populate_time}s"
    assert memory_time < 50, f"Memory info retrieval too slow: {memory_time}ms"
    assert cleanup_time < 1000, f"Cache cleanup too slow: {cleanup_time}ms"

    # Validate memory usage is reasonable
    used_memory_mb = int(memory_info.get("used_memory", 0)) / (1024 * 1024)
    assert used_memory_mb < 500, f"Cache using too much memory: {used_memory_mb}MB"
