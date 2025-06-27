#!/usr/bin/env python3
"""
Simple Performance Test for ACGS-1 Phase 4 Optimizations

Tests core performance metrics without complex imports.
"""

import asyncio
import json
import logging
import statistics
import time
from dataclasses import dataclass
from typing import Any

import aiohttp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PerformanceTestResults:
    """Test results container."""

    service_name: str
    endpoint: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    response_times: list[float]
    errors: list[str]

    @property
    def success_rate(self) -> float:
        return (
            (self.successful_requests / self.total_requests * 100)
            if self.total_requests > 0
            else 0.0
        )

    @property
    def avg_response_time_ms(self) -> float:
        return (
            statistics.mean(self.response_times) * 1000 if self.response_times else 0.0
        )

    @property
    def p95_response_time_ms(self) -> float:
        if len(self.response_times) >= 20:
            return statistics.quantiles(self.response_times, n=20)[18] * 1000
        return self.avg_response_time_ms


async def test_endpoint_performance(
    session: aiohttp.ClientSession,
    url: str,
    method: str = "GET",
    data: dict[str, Any] = None,
    concurrent_requests: int = 100,
) -> PerformanceTestResults:
    """Test endpoint performance with concurrent requests."""

    results = PerformanceTestResults(
        service_name=url.split(":")[1].split("/")[0] if ":" in url else "unknown",
        endpoint=url,
        total_requests=0,
        successful_requests=0,
        failed_requests=0,
        response_times=[],
        errors=[],
    )

    async def make_request():
        try:
            start_time = time.time()

            if method.upper() == "POST" and data:
                async with session.post(url, json=data) as response:
                    response_time = time.time() - start_time
                    await response.text()  # Consume response
            else:
                async with session.get(url) as response:
                    response_time = time.time() - start_time
                    await response.text()  # Consume response

            results.total_requests += 1
            results.response_times.append(response_time)

            if response.status == 200:
                results.successful_requests += 1
            else:
                results.failed_requests += 1
                results.errors.append(f"HTTP {response.status}")

        except Exception as e:
            results.total_requests += 1
            results.failed_requests += 1
            results.errors.append(str(e))

    # Execute concurrent requests
    tasks = [make_request() for _ in range(concurrent_requests)]
    await asyncio.gather(*tasks, return_exceptions=True)

    return results


async def test_redis_connectivity():
    """Test Redis connectivity and basic operations."""
    try:
        import redis.asyncio as redis

        client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

        # Test basic operations
        start_time = time.time()
        await client.ping()
        ping_time = time.time() - start_time

        # Test set/get
        start_time = time.time()
        await client.set("test_key", "test_value", ex=60)
        set_time = time.time() - start_time

        start_time = time.time()
        value = await client.get("test_key")
        get_time = time.time() - start_time

        await client.close()

        return {
            "available": True,
            "ping_time_ms": ping_time * 1000,
            "set_time_ms": set_time * 1000,
            "get_time_ms": get_time * 1000,
            "value_correct": value == "test_value",
        }

    except Exception as e:
        return {"available": False, "error": str(e)}


async def main():
    """Main performance test execution."""
    logger.info("🚀 Starting ACGS-1 Simple Performance Test")

    # Create HTTP session
    connector = aiohttp.TCPConnector(limit=200, limit_per_host=50)
    timeout = aiohttp.ClientTimeout(total=30)

    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:

        # Test endpoints
        test_cases = [
            {
                "name": "Constitutional Validation",
                "url": "http://localhost:8005/api/v1/constitutional/validate",
                "method": "GET",
                "concurrent": 100,
            },
            {
                "name": "Policy Validation",
                "url": "http://localhost:8005/api/v1/constitutional/validate-policy",
                "method": "POST",
                "data": {
                    "title": "Test Policy",
                    "description": "Performance test policy",
                    "constitutional_hash": "cdd01ef066bc6cf2",
                    "constitutional_principles": ["performance"],
                    "content": "Test policy content",
                },
                "concurrent": 75,
            },
            {
                "name": "Constitutional Council",
                "url": "http://localhost:8001/api/v1/constitutional-council/members",
                "method": "GET",
                "concurrent": 50,
            },
            {
                "name": "Voting Mechanisms",
                "url": "http://localhost:8001/api/v1/voting/mechanisms",
                "method": "GET",
                "concurrent": 50,
            },
            {
                "name": "PGC Health Check",
                "url": "http://localhost:8005/health",
                "method": "GET",
                "concurrent": 25,
            },
        ]

        results = {}

        # Test Redis
        logger.info("🗄️ Testing Redis connectivity...")
        results["redis"] = await test_redis_connectivity()

        # Test each endpoint
        for test_case in test_cases:
            logger.info(
                f"📊 Testing {test_case['name']} with {test_case['concurrent']} concurrent requests..."
            )

            test_result = await test_endpoint_performance(
                session,
                test_case["url"],
                test_case["method"],
                test_case.get("data"),
                test_case["concurrent"],
            )

            results[test_case["name"]] = {
                "success_rate": test_result.success_rate,
                "avg_response_time_ms": test_result.avg_response_time_ms,
                "p95_response_time_ms": test_result.p95_response_time_ms,
                "total_requests": test_result.total_requests,
                "successful_requests": test_result.successful_requests,
                "failed_requests": test_result.failed_requests,
                "error_count": len(test_result.errors),
                "sample_errors": test_result.errors[:3],
            }

    # Calculate overall performance
    performance_summary = calculate_performance_summary(results)

    # Save results
    full_results = {
        "timestamp": time.time(),
        "test_results": results,
        "performance_summary": performance_summary,
    }

    with open("simple_performance_results.json", "w") as f:
        json.dump(full_results, f, indent=2, default=str)

    # Display results
    print("\n" + "=" * 80)
    print("🏁 ACGS-1 Simple Performance Test Results")
    print("=" * 80)

    for test_name, result in results.items():
        if test_name == "redis":
            if result.get("available"):
                print(f"✅ Redis: Available (ping: {result['ping_time_ms']:.1f}ms)")
            else:
                print(f"❌ Redis: Unavailable - {result.get('error', 'Unknown error')}")
            continue

        status = (
            "✅"
            if result["success_rate"] >= 95 and result["p95_response_time_ms"] < 500
            else "⚠️"
        )
        print(f"{status} {test_name}:")
        print(f"   Success Rate: {result['success_rate']:.1f}%")
        print(f"   Avg Response: {result['avg_response_time_ms']:.1f}ms")
        print(f"   P95 Response: {result['p95_response_time_ms']:.1f}ms")
        print(
            f"   Requests: {result['successful_requests']}/{result['total_requests']}"
        )

        if result["error_count"] > 0:
            print(
                f"   Errors: {result['error_count']} (samples: {result['sample_errors']})"
            )

    print("\n📊 Performance Summary:")
    print(f"   Overall Grade: {performance_summary['grade']}")
    print(
        f"   Targets Met: {'✅ YES' if performance_summary['targets_met'] else '❌ NO'}"
    )
    print(
        f"   Average P95 Response Time: {performance_summary['avg_p95_response_time']:.1f}ms"
    )
    print(f"   Average Success Rate: {performance_summary['avg_success_rate']:.1f}%")

    if performance_summary["issues"]:
        print("\n⚠️ Issues:")
        for issue in performance_summary["issues"]:
            print(f"   - {issue}")

    print("\n📄 Detailed results saved: simple_performance_results.json")
    print("=" * 80)

    return performance_summary["targets_met"]


def calculate_performance_summary(results: dict[str, Any]) -> dict[str, Any]:
    """Calculate performance summary."""
    test_results = [
        r for name, r in results.items() if name != "redis" and isinstance(r, dict)
    ]

    if not test_results:
        return {"grade": "F", "targets_met": False, "issues": ["No test results"]}

    avg_success_rate = sum(r["success_rate"] for r in test_results) / len(test_results)
    avg_p95_response_time = sum(r["p95_response_time_ms"] for r in test_results) / len(
        test_results
    )

    issues = []
    score = 100

    # Check response time target (<500ms for P95)
    if avg_p95_response_time > 500:
        score -= 30
        issues.append(
            f"Average P95 response time {avg_p95_response_time:.1f}ms > 500ms target"
        )

    # Check success rate target (>99.5%)
    if avg_success_rate < 99.5:
        score -= 25
        issues.append(f"Average success rate {avg_success_rate:.1f}% < 99.5% target")

    # Check individual test failures
    failed_tests = [
        name
        for name, r in results.items()
        if name != "redis" and isinstance(r, dict) and r["success_rate"] < 95
    ]
    if failed_tests:
        score -= 20
        issues.append(f"Tests with <95% success rate: {', '.join(failed_tests)}")

    # Check Redis availability
    if not results.get("redis", {}).get("available", False):
        score -= 15
        issues.append("Redis cache unavailable")

    grade = (
        "A"
        if score >= 90
        else "B" if score >= 80 else "C" if score >= 70 else "D" if score >= 60 else "F"
    )

    return {
        "grade": grade,
        "score": max(0, score),
        "targets_met": score >= 90,
        "avg_success_rate": avg_success_rate,
        "avg_p95_response_time": avg_p95_response_time,
        "issues": issues,
    }


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
