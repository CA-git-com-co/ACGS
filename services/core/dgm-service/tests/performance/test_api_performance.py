"""
API Performance Tests for DGM Service.

Tests API endpoint performance against SLA requirements:
- Response time < 500ms
- Throughput requirements
- Concurrent request handling
- Error rate validation
"""

import asyncio
import statistics
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List

import httpx
import pytest
from dgm_service.config import settings


class APIPerformanceTest:
    """API performance testing utilities."""

    def __init__(self, base_url: str = None):
        self.base_url = base_url or f"http://localhost:{settings.PORT}"
        self.client = None

    async def setup(self):
        """Setup test client."""
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)

    async def teardown(self):
        """Cleanup test client."""
        if self.client:
            await self.client.aclose()

    async def measure_response_time(
        self, endpoint: str, method: str = "GET", data: Dict = None, headers: Dict = None
    ) -> Dict:
        """Measure response time for a single request."""
        start_time = time.perf_counter()

        try:
            if method.upper() == "GET":
                response = await self.client.get(endpoint, headers=headers)
            elif method.upper() == "POST":
                response = await self.client.post(endpoint, json=data, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")

            end_time = time.perf_counter()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds

            return {
                "response_time_ms": response_time,
                "status_code": response.status_code,
                "success": response.status_code < 400,
                "content_length": len(response.content),
            }
        except Exception as e:
            end_time = time.perf_counter()
            response_time = (end_time - start_time) * 1000

            return {
                "response_time_ms": response_time,
                "status_code": 0,
                "success": False,
                "error": str(e),
                "content_length": 0,
            }

    async def load_test_endpoint(
        self,
        endpoint: str,
        concurrent_requests: int = 10,
        total_requests: int = 100,
        method: str = "GET",
        data: Dict = None,
    ) -> Dict:
        """Perform load testing on an endpoint."""
        results = []

        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(concurrent_requests)

        async def make_request():
            async with semaphore:
                return await self.measure_response_time(endpoint, method, data)

        # Execute all requests
        tasks = [make_request() for _ in range(total_requests)]
        results = await asyncio.gather(*tasks)

        # Calculate statistics
        response_times = [r["response_time_ms"] for r in results]
        success_count = sum(1 for r in results if r["success"])

        return {
            "total_requests": total_requests,
            "successful_requests": success_count,
            "failed_requests": total_requests - success_count,
            "success_rate": (success_count / total_requests) * 100,
            "avg_response_time_ms": statistics.mean(response_times),
            "median_response_time_ms": statistics.median(response_times),
            "p95_response_time_ms": self._percentile(response_times, 95),
            "p99_response_time_ms": self._percentile(response_times, 99),
            "min_response_time_ms": min(response_times),
            "max_response_time_ms": max(response_times),
            "concurrent_requests": concurrent_requests,
        }

    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of data."""
        sorted_data = sorted(data)
        index = int((percentile / 100) * len(sorted_data))
        return sorted_data[min(index, len(sorted_data) - 1)]


@pytest.fixture
async def api_test():
    """Fixture for API performance testing."""
    test = APIPerformanceTest()
    await test.setup()
    yield test
    await test.teardown()


@pytest.mark.performance
@pytest.mark.asyncio
async def test_health_endpoint_performance(api_test):
    """Test health endpoint performance."""
    result = await api_test.measure_response_time("/health")

    # SLA requirement: < 500ms response time
    assert (
        result["response_time_ms"] < 500
    ), f"Health endpoint too slow: {result['response_time_ms']}ms"
    assert result["success"], f"Health endpoint failed: {result.get('error', 'Unknown error')}"
    assert result["status_code"] == 200


@pytest.mark.performance
@pytest.mark.asyncio
async def test_status_endpoint_performance(api_test):
    """Test status endpoint performance."""
    result = await api_test.measure_response_time("/api/v1/dgm/status")

    # SLA requirement: < 500ms response time
    assert (
        result["response_time_ms"] < 500
    ), f"Status endpoint too slow: {result['response_time_ms']}ms"
    assert result["success"], f"Status endpoint failed: {result.get('error', 'Unknown error')}"


@pytest.mark.performance
@pytest.mark.asyncio
async def test_metrics_endpoint_performance(api_test):
    """Test metrics endpoint performance."""
    result = await api_test.measure_response_time("/metrics")

    # Metrics endpoint should be fast for monitoring
    assert (
        result["response_time_ms"] < 200
    ), f"Metrics endpoint too slow: {result['response_time_ms']}ms"
    assert result["success"], f"Metrics endpoint failed: {result.get('error', 'Unknown error')}"


@pytest.mark.performance
@pytest.mark.asyncio
async def test_performance_report_endpoint(api_test):
    """Test performance report endpoint."""
    result = await api_test.measure_response_time("/api/v1/dgm/performance")

    # Performance reports can be slightly slower due to data aggregation
    assert (
        result["response_time_ms"] < 1000
    ), f"Performance report too slow: {result['response_time_ms']}ms"
    assert result["success"], f"Performance report failed: {result.get('error', 'Unknown error')}"


@pytest.mark.performance
@pytest.mark.asyncio
async def test_concurrent_health_checks(api_test):
    """Test concurrent health check performance."""
    load_result = await api_test.load_test_endpoint(
        "/health", concurrent_requests=50, total_requests=200
    )

    # Validate SLA requirements
    assert (
        load_result["success_rate"] >= 99.9
    ), f"Success rate too low: {load_result['success_rate']}%"
    assert (
        load_result["p95_response_time_ms"] < 500
    ), f"P95 response time too high: {load_result['p95_response_time_ms']}ms"
    assert (
        load_result["avg_response_time_ms"] < 250
    ), f"Average response time too high: {load_result['avg_response_time_ms']}ms"


@pytest.mark.performance
@pytest.mark.asyncio
async def test_concurrent_status_requests(api_test):
    """Test concurrent status request performance."""
    load_result = await api_test.load_test_endpoint(
        "/api/v1/dgm/status", concurrent_requests=20, total_requests=100
    )

    # Status endpoint should handle moderate load
    assert (
        load_result["success_rate"] >= 99.0
    ), f"Success rate too low: {load_result['success_rate']}%"
    assert (
        load_result["p95_response_time_ms"] < 750
    ), f"P95 response time too high: {load_result['p95_response_time_ms']}ms"


@pytest.mark.performance
@pytest.mark.asyncio
async def test_metrics_under_load(api_test):
    """Test metrics endpoint under load."""
    load_result = await api_test.load_test_endpoint(
        "/metrics", concurrent_requests=30, total_requests=150
    )

    # Metrics should be highly available and fast
    assert (
        load_result["success_rate"] >= 99.9
    ), f"Metrics success rate too low: {load_result['success_rate']}%"
    assert (
        load_result["p99_response_time_ms"] < 300
    ), f"P99 response time too high: {load_result['p99_response_time_ms']}ms"


@pytest.mark.performance
@pytest.mark.slow
@pytest.mark.asyncio
async def test_sustained_load_performance(api_test):
    """Test sustained load performance over time."""
    # Run multiple rounds of load testing
    rounds = 5
    all_results = []

    for round_num in range(rounds):
        print(f"Running load test round {round_num + 1}/{rounds}")

        result = await api_test.load_test_endpoint(
            "/health", concurrent_requests=25, total_requests=100
        )
        all_results.append(result)

        # Brief pause between rounds
        await asyncio.sleep(2)

    # Analyze sustained performance
    avg_success_rates = [r["success_rate"] for r in all_results]
    avg_response_times = [r["avg_response_time_ms"] for r in all_results]

    overall_success_rate = statistics.mean(avg_success_rates)
    overall_avg_response_time = statistics.mean(avg_response_times)

    # Validate sustained performance meets SLA
    assert overall_success_rate >= 99.9, f"Sustained success rate too low: {overall_success_rate}%"
    assert (
        overall_avg_response_time < 300
    ), f"Sustained response time too high: {overall_avg_response_time}ms"

    # Check for performance degradation over time
    first_half_avg = statistics.mean(avg_response_times[: rounds // 2])
    second_half_avg = statistics.mean(avg_response_times[rounds // 2 :])
    degradation_percent = ((second_half_avg - first_half_avg) / first_half_avg) * 100

    assert (
        degradation_percent < 20
    ), f"Performance degraded too much over time: {degradation_percent}%"
