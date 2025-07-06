"""
ACGS Code Analysis Engine - Performance Validation Tests
Comprehensive performance testing to validate P99 latency targets and throughput requirements.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import gc
import statistics
import time
from typing import Any

import psutil
import pytest
from httpx import AsyncClient

from tests.conftest import *


class PerformanceMetrics:
    """Collect and analyze performance metrics"""

    def __init__(self):
        self.response_times: list[float] = []
        self.memory_usage: list[float] = []
        self.cpu_usage: list[float] = []
        self.cache_hits = 0
        self.cache_misses = 0
        self.errors = 0
        self.start_time = None
        self.end_time = None

    def start_collection(self):
        """Start metrics collection"""
        self.start_time = time.time()
        self.response_times.clear()
        self.memory_usage.clear()
        self.cpu_usage.clear()
        self.cache_hits = 0
        self.cache_misses = 0
        self.errors = 0

    def record_response(
        self, response_time: float, cache_hit: bool = False, error: bool = False
    ):
        """Record a response metric"""
        self.response_times.append(response_time)

        if cache_hit:
            self.cache_hits += 1
        else:
            self.cache_misses += 1

        if error:
            self.errors += 1

        # Record system metrics
        process = psutil.Process()
        self.memory_usage.append(process.memory_info().rss / 1024 / 1024)  # MB
        self.cpu_usage.append(process.cpu_percent())

    def stop_collection(self):
        """Stop metrics collection"""
        self.end_time = time.time()

    @property
    def duration_seconds(self) -> float:
        """Total test duration"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0

    @property
    def total_requests(self) -> int:
        """Total number of requests"""
        return len(self.response_times)

    @property
    def requests_per_second(self) -> float:
        """Calculate requests per second"""
        if self.duration_seconds > 0:
            return self.total_requests / self.duration_seconds
        return 0.0

    @property
    def p99_latency_ms(self) -> float:
        """Calculate P99 latency in milliseconds"""
        if self.response_times:
            return statistics.quantiles(self.response_times, n=100)[98] * 1000
        return 0.0

    @property
    def p95_latency_ms(self) -> float:
        """Calculate P95 latency in milliseconds"""
        if self.response_times:
            return statistics.quantiles(self.response_times, n=100)[94] * 1000
        return 0.0

    @property
    def mean_latency_ms(self) -> float:
        """Calculate mean latency in milliseconds"""
        if self.response_times:
            return statistics.mean(self.response_times) * 1000
        return 0.0

    @property
    def cache_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total = self.cache_hits + self.cache_misses
        if total > 0:
            return self.cache_hits / total
        return 0.0

    @property
    def error_rate(self) -> float:
        """Calculate error rate"""
        if self.total_requests > 0:
            return self.errors / self.total_requests
        return 0.0

    @property
    def max_memory_usage_mb(self) -> float:
        """Maximum memory usage in MB"""
        if self.memory_usage:
            return max(self.memory_usage)
        return 0.0

    @property
    def mean_cpu_usage(self) -> float:
        """Mean CPU usage percentage"""
        if self.cpu_usage:
            return statistics.mean(self.cpu_usage)
        return 0.0

    def get_summary(self) -> dict[str, Any]:
        """Get performance summary"""
        return {
            "duration_seconds": self.duration_seconds,
            "total_requests": self.total_requests,
            "requests_per_second": self.requests_per_second,
            "p99_latency_ms": self.p99_latency_ms,
            "p95_latency_ms": self.p95_latency_ms,
            "mean_latency_ms": self.mean_latency_ms,
            "cache_hit_rate": self.cache_hit_rate,
            "error_rate": self.error_rate,
            "max_memory_usage_mb": self.max_memory_usage_mb,
            "mean_cpu_usage": self.mean_cpu_usage,
        }


@pytest.mark.performance
@pytest.mark.asyncio
async def test_semantic_search_latency_target(
    test_async_client: AsyncClient,
    auth_headers: dict[str, str],
    load_test_queries: list[str],
    performance_test_data: dict[str, Any],
):
    """Test semantic search P99 latency target (<10ms)"""
    metrics = PerformanceMetrics()
    metrics.start_collection()

    # Warm up the service
    for _ in range(10):
        response = await test_async_client.get(
            "/api/v1/search/semantic",
            params={"query": "test function", "limit": 5},
            headers=auth_headers,
        )
        assert response.status_code == 200

    # Performance test
    for query in load_test_queries * 10:  # 100 requests total
        start_time = time.time()

        response = await test_async_client.get(
            "/api/v1/search/semantic",
            params={"query": query, "limit": 10},
            headers=auth_headers,
        )

        end_time = time.time()
        response_time = end_time - start_time

        # Check if response was successful
        is_error = response.status_code != 200

        # Check if response was cached
        cache_hit = response.headers.get("X-Cache-Hit", "false").lower() == "true"

        metrics.record_response(response_time, cache_hit, is_error)

    metrics.stop_collection()
    summary = metrics.get_summary()

    # Print performance summary
    print("\n=== Semantic Search Performance Summary ===")
    print(f"Total Requests: {summary['total_requests']}")
    print(f"Duration: {summary['duration_seconds']:.2f}s")
    print(f"RPS: {summary['requests_per_second']:.2f}")
    print(f"P99 Latency: {summary['p99_latency_ms']:.2f}ms")
    print(f"P95 Latency: {summary['p95_latency_ms']:.2f}ms")
    print(f"Mean Latency: {summary['mean_latency_ms']:.2f}ms")
    print(f"Cache Hit Rate: {summary['cache_hit_rate']:.2%}")
    print(f"Error Rate: {summary['error_rate']:.2%}")
    print(f"Max Memory: {summary['max_memory_usage_mb']:.2f}MB")

    # Validate performance targets
    target_p99_ms = performance_test_data["target_p99_latency_ms"]
    assert (
        summary["p99_latency_ms"] <= target_p99_ms
    ), f"P99 latency {summary['p99_latency_ms']:.2f}ms exceeds target {target_p99_ms}ms"

    assert (
        summary["error_rate"] <= 0.01
    ), f"Error rate {summary['error_rate']:.2%} exceeds 1% threshold"


@pytest.mark.performance
@pytest.mark.asyncio
async def test_symbol_lookup_performance(
    test_async_client: AsyncClient,
    auth_headers: dict[str, str],
    sample_code_symbols: list[dict[str, Any]],
):
    """Test symbol lookup performance (should be <5ms for cached lookups)"""
    metrics = PerformanceMetrics()

    # First, ensure we have symbols to look up
    # (In real test, these would be pre-populated)
    symbol_ids = [symbol["id"] for symbol in sample_code_symbols]

    metrics.start_collection()

    # Test symbol lookups
    for _ in range(100):
        for symbol_id in symbol_ids:
            start_time = time.time()

            response = await test_async_client.get(
                f"/api/v1/symbols/{symbol_id}", headers=auth_headers
            )

            end_time = time.time()
            response_time = end_time - start_time

            is_error = response.status_code not in [
                200,
                404,
            ]  # 404 is acceptable for test
            cache_hit = response.headers.get("X-Cache-Hit", "false").lower() == "true"

            metrics.record_response(response_time, cache_hit, is_error)

    metrics.stop_collection()
    summary = metrics.get_summary()

    print("\n=== Symbol Lookup Performance Summary ===")
    print(f"P99 Latency: {summary['p99_latency_ms']:.2f}ms")
    print(f"Cache Hit Rate: {summary['cache_hit_rate']:.2%}")

    # Symbol lookups should be very fast, especially when cached
    assert (
        summary["p99_latency_ms"] <= 5.0
    ), f"Symbol lookup P99 latency {summary['p99_latency_ms']:.2f}ms exceeds 5ms target"


@pytest.mark.performance
@pytest.mark.asyncio
async def test_concurrent_load_performance(
    test_async_client: AsyncClient,
    auth_headers: dict[str, str],
    load_test_queries: list[str],
    performance_test_data: dict[str, Any],
):
    """Test performance under concurrent load"""
    concurrent_users = performance_test_data["concurrent_users"]
    test_duration = 30  # 30 seconds for CI/CD compatibility

    metrics = PerformanceMetrics()
    metrics.start_collection()

    async def user_session(user_id: int):
        """Simulate a user session with mixed requests"""
        session_metrics = []
        end_time = time.time() + test_duration

        while time.time() < end_time:
            # Mix of different request types
            request_types = [
                (
                    "semantic_search",
                    "/api/v1/search/semantic",
                    {"query": f"test query {user_id}", "limit": 5},
                ),
                (
                    "symbol_search",
                    "/api/v1/search/symbol",
                    {"name": "test*", "limit": 10},
                ),
                ("health_check", "/health", {}),
            ]

            for req_type, endpoint, params in request_types:
                start_time = time.time()

                try:
                    if endpoint == "/health":
                        response = await test_async_client.get(endpoint)
                    else:
                        response = await test_async_client.get(
                            endpoint, params=params, headers=auth_headers
                        )

                    end_time_req = time.time()
                    response_time = end_time_req - start_time

                    is_error = response.status_code >= 400
                    cache_hit = (
                        response.headers.get("X-Cache-Hit", "false").lower() == "true"
                    )

                    session_metrics.append((response_time, cache_hit, is_error))

                except Exception:
                    session_metrics.append((1.0, False, True))  # Record as error

                # Small delay between requests
                await asyncio.sleep(0.1)

        return session_metrics

    # Run concurrent user sessions
    tasks = [user_session(i) for i in range(concurrent_users)]
    results = await asyncio.gather(*tasks)

    # Aggregate results
    for user_results in results:
        for response_time, cache_hit, is_error in user_results:
            metrics.record_response(response_time, cache_hit, is_error)

    metrics.stop_collection()
    summary = metrics.get_summary()

    print("\n=== Concurrent Load Performance Summary ===")
    print(f"Concurrent Users: {concurrent_users}")
    print(f"Test Duration: {test_duration}s")
    print(f"Total Requests: {summary['total_requests']}")
    print(f"RPS: {summary['requests_per_second']:.2f}")
    print(f"P99 Latency: {summary['p99_latency_ms']:.2f}ms")
    print(f"Error Rate: {summary['error_rate']:.2%}")
    print(f"Cache Hit Rate: {summary['cache_hit_rate']:.2%}")

    # Validate performance under load
    target_rps = performance_test_data["target_throughput_rps"]
    assert (
        summary["requests_per_second"] >= target_rps * 0.8
    ), f"RPS {summary['requests_per_second']:.2f} is below 80% of target {target_rps}"

    assert (
        summary["error_rate"] <= 0.05
    ), f"Error rate {summary['error_rate']:.2%} exceeds 5% threshold under load"


@pytest.mark.performance
@pytest.mark.asyncio
async def test_cache_performance_validation(
    test_async_client: AsyncClient,
    auth_headers: dict[str, str],
    performance_test_data: dict[str, Any],
):
    """Test cache hit rate performance target (>85%)"""
    metrics = PerformanceMetrics()

    # Test query that should be cacheable
    test_query = "authentication function validation"

    metrics.start_collection()

    # First request (cache miss)
    start_time = time.time()
    response = await test_async_client.get(
        "/api/v1/search/semantic",
        params={"query": test_query, "limit": 10},
        headers=auth_headers,
    )
    end_time = time.time()

    assert response.status_code == 200
    metrics.record_response(
        end_time - start_time, False, False
    )  # First request is cache miss

    # Subsequent requests (should be cache hits)
    for _ in range(20):
        start_time = time.time()
        response = await test_async_client.get(
            "/api/v1/search/semantic",
            params={"query": test_query, "limit": 10},
            headers=auth_headers,
        )
        end_time = time.time()

        cache_hit = response.headers.get("X-Cache-Hit", "false").lower() == "true"
        metrics.record_response(
            end_time - start_time, cache_hit, response.status_code != 200
        )

    metrics.stop_collection()
    summary = metrics.get_summary()

    print("\n=== Cache Performance Summary ===")
    print(f"Cache Hit Rate: {summary['cache_hit_rate']:.2%}")
    print(f"Cache Hits: {metrics.cache_hits}")
    print(f"Cache Misses: {metrics.cache_misses}")

    target_cache_hit_rate = performance_test_data["target_cache_hit_rate"]
    assert summary["cache_hit_rate"] >= target_cache_hit_rate, (
        f"Cache hit rate {summary['cache_hit_rate']:.2%} below target"
        f" {target_cache_hit_rate:.2%}"
    )


@pytest.mark.performance
@pytest.mark.asyncio
async def test_memory_usage_validation(
    test_async_client: AsyncClient,
    auth_headers: dict[str, str],
    load_test_queries: list[str],
):
    """Test memory usage remains within acceptable limits"""
    initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB

    # Force garbage collection before test
    gc.collect()

    # Perform memory-intensive operations
    for _ in range(5):  # 5 rounds of queries
        for query in load_test_queries:
            response = await test_async_client.get(
                "/api/v1/search/semantic",
                params={"query": query, "limit": 50},  # Larger result set
                headers=auth_headers,
            )
            assert response.status_code == 200

    # Force garbage collection after test
    gc.collect()

    final_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
    memory_increase = final_memory - initial_memory

    print("\n=== Memory Usage Summary ===")
    print(f"Initial Memory: {initial_memory:.2f}MB")
    print(f"Final Memory: {final_memory:.2f}MB")
    print(f"Memory Increase: {memory_increase:.2f}MB")

    # Memory increase should be reasonable (less than 100MB for this test)
    assert (
        memory_increase <= 100
    ), f"Memory increase {memory_increase:.2f}MB exceeds 100MB threshold"

    # Total memory usage should be reasonable
    assert (
        final_memory <= 512
    ), f"Final memory usage {final_memory:.2f}MB exceeds 512MB threshold"


@pytest.mark.performance
@pytest.mark.slow
@pytest.mark.asyncio
async def test_sustained_load_performance(
    test_async_client: AsyncClient,
    auth_headers: dict[str, str],
    load_test_queries: list[str],
):
    """Test performance under sustained load (longer duration test)"""
    test_duration = 120  # 2 minutes
    target_rps = 50  # Conservative target for sustained load

    metrics = PerformanceMetrics()
    metrics.start_collection()

    end_time = time.time() + test_duration
    request_count = 0

    while time.time() < end_time:
        query = load_test_queries[request_count % len(load_test_queries)]

        start_time = time.time()
        response = await test_async_client.get(
            "/api/v1/search/semantic",
            params={"query": query, "limit": 10},
            headers=auth_headers,
        )
        end_time_req = time.time()

        response_time = end_time_req - start_time
        is_error = response.status_code != 200
        cache_hit = response.headers.get("X-Cache-Hit", "false").lower() == "true"

        metrics.record_response(response_time, cache_hit, is_error)
        request_count += 1

        # Control request rate
        await asyncio.sleep(1.0 / target_rps)

    metrics.stop_collection()
    summary = metrics.get_summary()

    print("\n=== Sustained Load Performance Summary ===")
    print(f"Test Duration: {summary['duration_seconds']:.2f}s")
    print(f"Total Requests: {summary['total_requests']}")
    print(f"RPS: {summary['requests_per_second']:.2f}")
    print(f"P99 Latency: {summary['p99_latency_ms']:.2f}ms")
    print(f"Error Rate: {summary['error_rate']:.2%}")
    print(f"Max Memory: {summary['max_memory_usage_mb']:.2f}MB")

    # Validate sustained performance
    assert (
        summary["error_rate"] <= 0.01
    ), f"Error rate {summary['error_rate']:.2%} exceeds 1% under sustained load"

    assert summary["p99_latency_ms"] <= 20.0, (
        f"P99 latency {summary['p99_latency_ms']:.2f}ms exceeds 20ms under sustained"
        " load"
    )
