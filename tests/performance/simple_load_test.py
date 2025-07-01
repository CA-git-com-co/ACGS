#!/usr/bin/env python3
"""
ACGS-1 Simple Load Testing Script
Phase 2 - Basic Load Testing Implementation

A simple, self-contained load testing script that doesn't require external tools.
Tests all 7 core ACGS services with configurable concurrent users and duration.

Usage:
    python tests/performance/simple_load_test.py --users 50 --duration 60
    python tests/performance/simple_load_test.py --scenario health_check
"""

import argparse
import asyncio
import json
import logging
import statistics
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import aiohttp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class LoadTestResult:
    """Individual request result."""

    service: str
    endpoint: str
    response_time_ms: float
    status_code: int
    success: bool
    timestamp: float
    error: str | None = None


@dataclass
class LoadTestConfig:
    """Load test configuration."""

    concurrent_users: int = 50
    duration_seconds: int = 60
    target_response_time_ms: float = 500.0
    services: dict[str, int] = None

    def __post_init__(self):
        if self.services is None:
            self.services = {
                "auth": 8000,
                "ac": 8001,
                "integrity": 8002,
                "fv": 8003,
                "gs": 8004,
                "pgc": 8005,
                "ec": 8006,
            }


class SimpleLoadTester:
    """Simple load testing implementation."""

    def __init__(self, config: LoadTestConfig):
        self.config = config
        self.results: list[LoadTestResult] = []
        self.start_time = 0
        self.end_time = 0

    async def make_request(
        self, session: aiohttp.ClientSession, service: str, port: int, user_id: int
    ) -> LoadTestResult:
        """Make a single HTTP request and record the result."""
        url = f"http://localhost:{port}/health"
        start_time = time.time()

        try:
            async with session.get(url, timeout=10) as response:
                response_time_ms = (time.time() - start_time) * 1000
                success = response.status == 200

                return LoadTestResult(
                    service=service,
                    endpoint="/health",
                    response_time_ms=response_time_ms,
                    status_code=response.status,
                    success=success,
                    timestamp=start_time,
                )

        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            return LoadTestResult(
                service=service,
                endpoint="/health",
                response_time_ms=response_time_ms,
                status_code=0,
                success=False,
                timestamp=start_time,
                error=str(e),
            )

    async def user_simulation(self, user_id: int, session: aiohttp.ClientSession):
        """Simulate a single user making requests."""
        user_results = []
        end_time = self.start_time + self.config.duration_seconds

        while time.time() < end_time:
            # Randomly select a service to test
            import random

            service, port = random.choice(list(self.config.services.items()))

            # Make request
            result = await self.make_request(session, service, port, user_id)
            user_results.append(result)

            # Wait between requests (1-3 seconds)
            await asyncio.sleep(random.uniform(1, 3))

        return user_results

    async def run_load_test(self) -> dict[str, Any]:
        """Execute the load test with multiple concurrent users."""
        logger.info(
            f"🚀 Starting load test with {self.config.concurrent_users} users for {self.config.duration_seconds}s"
        )

        self.start_time = time.time()

        # Create HTTP session with connection pooling
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=20)
        timeout = aiohttp.ClientTimeout(total=30)

        async with aiohttp.ClientSession(
            connector=connector, timeout=timeout
        ) as session:
            # Create tasks for all users
            tasks = []
            for user_id in range(self.config.concurrent_users):
                task = asyncio.create_task(self.user_simulation(user_id, session))
                tasks.append(task)

            # Wait for all users to complete
            logger.info(
                f"⏳ Running load test for {self.config.duration_seconds} seconds..."
            )
            user_results = await asyncio.gather(*tasks, return_exceptions=True)

        self.end_time = time.time()

        # Flatten results
        for user_result in user_results:
            if isinstance(user_result, list):
                self.results.extend(user_result)
            elif isinstance(user_result, Exception):
                logger.error(f"User simulation failed: {user_result}")

        # Generate report
        return self.generate_report()

    def generate_report(self) -> dict[str, Any]:
        """Generate comprehensive load test report."""
        if not self.results:
            return {"error": "No results collected"}

        # Basic statistics
        total_requests = len(self.results)
        successful_requests = sum(1 for r in self.results if r.success)
        failed_requests = total_requests - successful_requests

        success_rate = (
            (successful_requests / total_requests * 100) if total_requests > 0 else 0
        )
        error_rate = (
            (failed_requests / total_requests * 100) if total_requests > 0 else 0
        )

        # Response time statistics
        response_times = [r.response_time_ms for r in self.results if r.success]
        if response_times:
            avg_response_time = statistics.mean(response_times)
            median_response_time = statistics.median(response_times)
            p95_response_time = (
                statistics.quantiles(response_times, n=20)[18]
                if len(response_times) >= 20
                else max(response_times)
            )
            p99_response_time = (
                statistics.quantiles(response_times, n=100)[98]
                if len(response_times) >= 100
                else max(response_times)
            )
            min_response_time = min(response_times)
            max_response_time = max(response_times)
        else:
            avg_response_time = median_response_time = p95_response_time = (
                p99_response_time
            ) = 0
            min_response_time = max_response_time = 0

        # Throughput
        duration = self.end_time - self.start_time
        requests_per_second = total_requests / duration if duration > 0 else 0

        # Service-specific statistics
        service_stats = {}
        for service in self.config.services.keys():
            service_results = [r for r in self.results if r.service == service]
            if service_results:
                service_successful = sum(1 for r in service_results if r.success)
                service_total = len(service_results)
                service_success_rate = (
                    (service_successful / service_total * 100)
                    if service_total > 0
                    else 0
                )
                service_response_times = [
                    r.response_time_ms for r in service_results if r.success
                ]
                service_avg_response = (
                    statistics.mean(service_response_times)
                    if service_response_times
                    else 0
                )

                service_stats[service] = {
                    "total_requests": service_total,
                    "success_rate": round(service_success_rate, 2),
                    "avg_response_time": round(service_avg_response, 2),
                }

        # Performance evaluation
        performance_grade = "A"
        if p95_response_time > self.config.target_response_time_ms:
            performance_grade = "B"
        if success_rate < 99.0:
            performance_grade = "C"
        if success_rate < 95.0:
            performance_grade = "D"
        if success_rate < 90.0:
            performance_grade = "F"

        report = {
            "test_configuration": {
                "concurrent_users": self.config.concurrent_users,
                "duration_seconds": self.config.duration_seconds,
                "target_response_time_ms": self.config.target_response_time_ms,
                "services_tested": list(self.config.services.keys()),
            },
            "execution_summary": {
                "start_time": datetime.fromtimestamp(
                    self.start_time, timezone.utc
                ).isoformat(),
                "end_time": datetime.fromtimestamp(
                    self.end_time, timezone.utc
                ).isoformat(),
                "actual_duration": round(duration, 2),
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "failed_requests": failed_requests,
            },
            "performance_metrics": {
                "success_rate": round(success_rate, 2),
                "error_rate": round(error_rate, 2),
                "requests_per_second": round(requests_per_second, 2),
                "avg_response_time_ms": round(avg_response_time, 2),
                "median_response_time_ms": round(median_response_time, 2),
                "p95_response_time_ms": round(p95_response_time, 2),
                "p99_response_time_ms": round(p99_response_time, 2),
                "min_response_time_ms": round(min_response_time, 2),
                "max_response_time_ms": round(max_response_time, 2),
            },
            "service_statistics": service_stats,
            "performance_evaluation": {
                "grade": performance_grade,
                "target_met": p95_response_time <= self.config.target_response_time_ms
                and success_rate >= 99.0,
                "recommendations": self.generate_recommendations(
                    success_rate, p95_response_time
                ),
            },
        }

        return report

    def generate_recommendations(
        self, success_rate: float, p95_response_time: float
    ) -> list[str]:
        """Generate performance improvement recommendations."""
        recommendations = []

        if success_rate < 99.0:
            recommendations.append("Investigate and fix service reliability issues")
        if p95_response_time > self.config.target_response_time_ms:
            recommendations.append("Optimize service response times")
        if p95_response_time > 1000:
            recommendations.append("Consider implementing caching mechanisms")
        if success_rate < 95.0:
            recommendations.append("Review error handling and circuit breaker patterns")

        if not recommendations:
            recommendations.append(
                "System performance meets targets - consider scaling tests"
            )

        return recommendations


async def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description="ACGS-1 Simple Load Testing")
    parser.add_argument(
        "--users", type=int, default=50, help="Number of concurrent users"
    )
    parser.add_argument(
        "--duration", type=int, default=60, help="Test duration in seconds"
    )
    parser.add_argument(
        "--target-time", type=float, default=500.0, help="Target response time in ms"
    )
    parser.add_argument(
        "--output",
        default="tests/performance/results/simple_load_test_report.json",
        help="Output file for results",
    )

    args = parser.parse_args()

    # Create results directory
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Configure and run test
    config = LoadTestConfig(
        concurrent_users=args.users,
        duration_seconds=args.duration,
        target_response_time_ms=args.target_time,
    )

    tester = SimpleLoadTester(config)
    report = await tester.run_load_test()

    # Save report
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)

    # Print summary
    print("\n" + "=" * 60)
    print("SIMPLE LOAD TEST RESULTS")
    print("=" * 60)

    if "error" in report:
        print(f"❌ Test failed: {report['error']}")
        return

    metrics = report["performance_metrics"]
    evaluation = report["performance_evaluation"]

    print(f"Concurrent Users: {config.concurrent_users}")
    print(f"Duration: {config.duration_seconds}s")
    print(f"Total Requests: {report['execution_summary']['total_requests']}")
    print(f"Success Rate: {metrics['success_rate']:.2f}%")
    print(f"Requests/Second: {metrics['requests_per_second']:.2f}")
    print(f"Average Response Time: {metrics['avg_response_time_ms']:.2f}ms")
    print(f"95th Percentile Response Time: {metrics['p95_response_time_ms']:.2f}ms")
    print(f"Performance Grade: {evaluation['grade']}")
    print(f"Target Met: {'✅' if evaluation['target_met'] else '❌'}")

    print(f"\nReport saved to: {output_path}")

    if evaluation["recommendations"]:
        print("\nRecommendations:")
        for rec in evaluation["recommendations"]:
            print(f"  • {rec}")


if __name__ == "__main__":
    asyncio.run(main())
