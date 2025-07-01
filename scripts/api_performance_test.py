#!/usr/bin/env python3
"""
ACGS-1 API Performance Testing and Optimization
Measures current API response times and identifies optimization opportunities
"""

import asyncio
import json
import logging
import statistics
import time
from datetime import datetime
from typing import Any

import aiohttp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class APIPerformanceTester:
    def __init__(self):
        self.base_url = "http://localhost"
        self.services = {
            "auth": 8000,
            "ac": 8001,
            "integrity": 8002,
            "fv": 8003,
            "gs": 8004,
            "pgc": 8005,
            "ec": 8006,
        }
        self.results = {}

    async def test_service_health(
        self, session: aiohttp.ClientSession, service: str, port: int
    ) -> dict[str, Any]:
        """Test individual service health endpoint performance."""
        url = f"{self.base_url}:{port}/health"
        response_times = []
        errors = 0

        logger.info(f"Testing {service} service at {url}")

        # Run 10 requests to get average response time
        for i in range(10):
            try:
                start_time = time.time()
                async with session.get(
                    url, timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    await response.text()
                    response_time = (time.time() - start_time) * 1000  # Convert to ms
                    response_times.append(response_time)

                    if response.status != 200:
                        errors += 1

            except Exception as e:
                logger.warning(f"Request {i + 1} failed for {service}: {e}")
                errors += 1

        if response_times:
            return {
                "service": service,
                "port": port,
                "avg_response_time_ms": round(statistics.mean(response_times), 2),
                "min_response_time_ms": round(min(response_times), 2),
                "max_response_time_ms": round(max(response_times), 2),
                "median_response_time_ms": round(statistics.median(response_times), 2),
                "success_rate": round((10 - errors) / 10 * 100, 2),
                "total_requests": 10,
                "errors": errors,
            }
        return {
            "service": service,
            "port": port,
            "status": "unavailable",
            "errors": errors,
        }

    async def test_load_balancer_performance(
        self, session: aiohttp.ClientSession
    ) -> dict[str, Any]:
        """Test HAProxy load balancer performance."""
        url = f"{self.base_url}:8090/health"
        response_times = []
        errors = 0

        logger.info(f"Testing HAProxy load balancer at {url}")

        for i in range(20):
            try:
                start_time = time.time()
                async with session.get(
                    url, timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    await response.text()
                    response_time = (time.time() - start_time) * 1000
                    response_times.append(response_time)

                    if response.status not in [
                        200,
                        503,
                    ]:  # 503 is expected if no backend available
                        errors += 1

            except Exception as e:
                logger.warning(f"Load balancer request {i + 1} failed: {e}")
                errors += 1

        if response_times:
            return {
                "service": "haproxy_load_balancer",
                "port": 8090,
                "avg_response_time_ms": round(statistics.mean(response_times), 2),
                "min_response_time_ms": round(min(response_times), 2),
                "max_response_time_ms": round(max(response_times), 2),
                "median_response_time_ms": round(statistics.median(response_times), 2),
                "success_rate": round((20 - errors) / 20 * 100, 2),
                "total_requests": 20,
                "errors": errors,
            }
        return {
            "service": "haproxy_load_balancer",
            "port": 8090,
            "status": "unavailable",
            "errors": errors,
        }

    async def run_concurrent_load_test(
        self,
        session: aiohttp.ClientSession,
        service: str,
        port: int,
        concurrent_requests: int = 50,
    ) -> dict[str, Any]:
        """Run concurrent load test on a service."""
        url = f"{self.base_url}:{port}/health"

        async def single_request():
            try:
                start_time = time.time()
                async with session.get(
                    url, timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    await response.text()
                    return (time.time() - start_time) * 1000, response.status == 200
            except Exception:
                return None, False

        logger.info(
            f"Running concurrent load test on {service} with {concurrent_requests} requests"
        )

        start_time = time.time()
        tasks = [single_request() for _ in range(concurrent_requests)]
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time

        response_times = [r[0] for r in results if r[0] is not None]
        successful_requests = sum(1 for r in results if r[1])

        if response_times:
            return {
                "service": service,
                "concurrent_requests": concurrent_requests,
                "successful_requests": successful_requests,
                "success_rate": round(
                    successful_requests / concurrent_requests * 100, 2
                ),
                "avg_response_time_ms": round(statistics.mean(response_times), 2),
                "median_response_time_ms": round(statistics.median(response_times), 2),
                "p95_response_time_ms": (
                    round(statistics.quantiles(response_times, n=20)[18], 2)
                    if len(response_times) > 10
                    else 0
                ),
                "total_duration_seconds": round(total_time, 2),
                "requests_per_second": round(concurrent_requests / total_time, 2),
            }
        return {
            "service": service,
            "status": "failed_load_test",
            "concurrent_requests": concurrent_requests,
            "successful_requests": 0,
        }

    async def run_performance_tests(self):
        """Run comprehensive performance tests."""
        logger.info("🚀 Starting ACGS-1 API Performance Tests")

        async with aiohttp.ClientSession() as session:
            # Test individual service health endpoints
            health_results = []
            for service, port in self.services.items():
                result = await self.test_service_health(session, service, port)
                health_results.append(result)

            # Test load balancer
            lb_result = await self.test_load_balancer_performance(session)

            # Run concurrent load tests on available services
            load_test_results = []
            for service, port in self.services.items():
                # Only test services that are responding
                health_result = next(
                    (r for r in health_results if r["service"] == service), None
                )
                if health_result and health_result.get("success_rate", 0) > 0:
                    load_result = await self.run_concurrent_load_test(
                        session, service, port
                    )
                    load_test_results.append(load_result)

            self.results = {
                "timestamp": datetime.now().isoformat(),
                "health_check_results": health_results,
                "load_balancer_result": lb_result,
                "concurrent_load_test_results": load_test_results,
                "summary": self._generate_summary(health_results, load_test_results),
            }

    def _generate_summary(
        self, health_results: list[dict], load_results: list[dict]
    ) -> dict[str, Any]:
        """Generate performance summary."""
        available_services = [r for r in health_results if r.get("success_rate", 0) > 0]
        avg_response_times = [
            r["avg_response_time_ms"]
            for r in available_services
            if "avg_response_time_ms" in r
        ]

        load_test_summary = {}
        if load_results:
            successful_load_tests = [
                r for r in load_results if r.get("success_rate", 0) > 80
            ]
            if successful_load_tests:
                load_test_summary = {
                    "avg_concurrent_response_time_ms": round(
                        statistics.mean(
                            [r["avg_response_time_ms"] for r in successful_load_tests]
                        ),
                        2,
                    ),
                    "avg_requests_per_second": round(
                        statistics.mean(
                            [r["requests_per_second"] for r in successful_load_tests]
                        ),
                        2,
                    ),
                    "services_passing_load_test": len(successful_load_tests),
                }

        return {
            "total_services_tested": len(self.services),
            "available_services": len(available_services),
            "avg_health_response_time_ms": (
                round(statistics.mean(avg_response_times), 2)
                if avg_response_times
                else 0
            ),
            "fastest_service_ms": min(avg_response_times) if avg_response_times else 0,
            "slowest_service_ms": max(avg_response_times) if avg_response_times else 0,
            "target_response_time_ms": 500,
            "services_meeting_target": len([t for t in avg_response_times if t < 500]),
            **load_test_summary,
        }

    def save_results(self, filename: str = "api_performance_results.json"):
        """Save performance test results to file."""
        with open(filename, "w") as f:
            json.dump(self.results, f, indent=2)
        logger.info(f"Performance test results saved to {filename}")

    def print_results(self):
        """Print formatted performance test results."""
        print("\n" + "=" * 80)
        print("🎯 ACGS-1 API PERFORMANCE TEST RESULTS")
        print("=" * 80)

        # Health check results
        print("\n📊 Service Health Check Results:")
        print("-" * 50)
        for result in self.results["health_check_results"]:
            if "avg_response_time_ms" in result:
                status = (
                    "✅ HEALTHY"
                    if result["success_rate"] == 100
                    else f"⚠️  {result['success_rate']}% SUCCESS"
                )
                print(
                    f"{result['service'].upper():>12} (:{result['port']}) | {result['avg_response_time_ms']:>6.1f}ms | {status}"
                )
            else:
                print(
                    f"{result['service'].upper():>12} (:{result['port']}) | {'N/A':>6} | ❌ UNAVAILABLE"
                )

        # Load balancer results
        lb_result = self.results["load_balancer_result"]
        if "avg_response_time_ms" in lb_result:
            status = (
                "✅ OPERATIONAL" if lb_result["success_rate"] > 50 else "⚠️  DEGRADED"
            )
            print(
                f"{'LOAD BALANCER':>12} (:{lb_result['port']}) | {lb_result['avg_response_time_ms']:>6.1f}ms | {status}"
            )

        # Load test results
        if self.results["concurrent_load_test_results"]:
            print("\n🚀 Concurrent Load Test Results (50 concurrent requests):")
            print("-" * 70)
            for result in self.results["concurrent_load_test_results"]:
                if "avg_response_time_ms" in result:
                    print(
                        f"{result['service'].upper():>12} | {result['avg_response_time_ms']:>6.1f}ms avg | {result['requests_per_second']:>6.1f} RPS | {result['success_rate']:>5.1f}% success"
                    )

        # Summary
        summary = self.results["summary"]
        print("\n📈 Performance Summary:")
        print("-" * 30)
        print(
            f"Available Services: {summary['available_services']}/{summary['total_services_tested']}"
        )
        print(f"Average Response Time: {summary['avg_health_response_time_ms']:.1f}ms")
        print(
            f"Services Meeting <500ms Target: {summary['services_meeting_target']}/{summary['available_services']}"
        )

        if "avg_requests_per_second" in summary:
            print(f"Average Throughput: {summary['avg_requests_per_second']:.1f} RPS")

        # Performance assessment
        avg_time = summary["avg_health_response_time_ms"]
        if avg_time < 100:
            print("🎉 EXCELLENT: All services performing well under 100ms")
        elif avg_time < 500:
            print("✅ GOOD: Services meeting 500ms target")
        else:
            print("⚠️  NEEDS OPTIMIZATION: Some services exceeding 500ms target")


async def main():
    """Main function to run performance tests."""
    tester = APIPerformanceTester()
    await tester.run_performance_tests()
    tester.print_results()
    tester.save_results()


if __name__ == "__main__":
    asyncio.run(main())
