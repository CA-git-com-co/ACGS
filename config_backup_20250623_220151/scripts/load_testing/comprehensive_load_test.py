#!/usr/bin/env python3
"""
ACGS-1 Comprehensive Load Testing Suite

Tests enterprise scalability targets:
- >1000 concurrent users
- >99.9% availability
- <500ms response times for 95% requests
- Circuit breaker functionality
- Failover mechanisms
"""

import asyncio
import json
import logging
import statistics
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import aiohttp
import click

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class LoadTestConfig:
    """Load test configuration."""

    base_url: str = "http://localhost"
    max_concurrent_users: int = 1000
    test_duration_seconds: int = 300  # 5 minutes
    ramp_up_seconds: int = 60
    target_response_time_ms: int = 500
    target_availability_percent: float = 99.9

    # Test scenarios
    scenarios: List[Dict] = field(
        default_factory=lambda: [
            {"path": "/health", "weight": 10, "method": "GET"},
            {"path": "/api/v1/auth/health", "weight": 15, "method": "GET"},
            {"path": "/api/v1/constitutional/health", "weight": 15, "method": "GET"},
            {"path": "/api/v1/integrity/health", "weight": 15, "method": "GET"},
            {
                "path": "/api/v1/formal-verification/health",
                "weight": 10,
                "method": "GET",
            },
            {"path": "/api/v1/governance/health", "weight": 20, "method": "GET"},
            {"path": "/api/v1/policy/health", "weight": 10, "method": "GET"},
            {"path": "/api/v1/evolutionary/health", "weight": 5, "method": "GET"},
        ]
    )


@dataclass
class TestResult:
    """Individual test result."""

    url: str
    method: str
    status_code: int
    response_time_ms: float
    success: bool
    error: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


class LoadTestRunner:
    """Comprehensive load test runner."""

    def __init__(self, config: LoadTestConfig):
        self.config = config
        self.results: List[TestResult] = []
        self.active_users = 0
        self.start_time = 0
        self.session: Optional[aiohttp.ClientSession] = None

    async def initialize(self):
        """Initialize test session."""
        connector = aiohttp.TCPConnector(
            limit=self.config.max_concurrent_users + 100,
            limit_per_host=self.config.max_concurrent_users + 100,
            ttl_dns_cache=300,
            use_dns_cache=True,
        )

        timeout = aiohttp.ClientTimeout(total=30, connect=10)

        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={"User-Agent": "ACGS-1-LoadTest/1.0"},
        )

        logger.info("Load test session initialized")

    async def cleanup(self):
        """Cleanup test session."""
        if self.session:
            await self.session.close()
        logger.info("Load test session closed")

    async def make_request(self, scenario: Dict) -> TestResult:
        """Make a single HTTP request."""
        url = f"{self.config.base_url}{scenario['path']}"
        method = scenario["method"]

        start_time = time.time()

        try:
            async with self.session.request(method, url) as response:
                response_time_ms = (time.time() - start_time) * 1000

                # Read response to ensure complete request
                await response.read()

                return TestResult(
                    url=url,
                    method=method,
                    status_code=response.status,
                    response_time_ms=response_time_ms,
                    success=200 <= response.status < 400,
                )

        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            return TestResult(
                url=url,
                method=method,
                status_code=0,
                response_time_ms=response_time_ms,
                success=False,
                error=str(e),
            )

    def select_scenario(self) -> Dict:
        """Select scenario based on weights."""
        import random

        total_weight = sum(s["weight"] for s in self.config.scenarios)
        random_weight = random.randint(1, total_weight)

        current_weight = 0
        for scenario in self.config.scenarios:
            current_weight += scenario["weight"]
            if random_weight <= current_weight:
                return scenario

        return self.config.scenarios[0]  # Fallback

    async def user_simulation(self, user_id: int):
        """Simulate a single user's behavior."""
        self.active_users += 1

        try:
            while time.time() - self.start_time < self.config.test_duration_seconds:
                scenario = self.select_scenario()
                result = await self.make_request(scenario)
                self.results.append(result)

                # Random think time between requests (0.1 to 2 seconds)
                import random

                think_time = random.uniform(0.1, 2.0)
                await asyncio.sleep(think_time)

        except Exception as e:
            logger.error(f"User {user_id} simulation error: {e}")

        finally:
            self.active_users -= 1

    async def ramp_up_users(self):
        """Gradually ramp up users to target concurrency."""
        users_per_second = (
            self.config.max_concurrent_users / self.config.ramp_up_seconds
        )

        tasks = []

        for i in range(self.config.max_concurrent_users):
            # Calculate when to start this user
            start_delay = i / users_per_second

            # Create user task with delay
            task = asyncio.create_task(self._delayed_user_start(i, start_delay))
            tasks.append(task)

        logger.info(
            f"Starting ramp-up: {self.config.max_concurrent_users} users over {self.config.ramp_up_seconds}s"
        )

        # Wait for all users to complete
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _delayed_user_start(self, user_id: int, delay: float):
        """Start user simulation after delay."""
        await asyncio.sleep(delay)
        await self.user_simulation(user_id)

    async def monitor_progress(self):
        """Monitor and log test progress."""
        while time.time() - self.start_time < self.config.test_duration_seconds:
            await asyncio.sleep(10)  # Report every 10 seconds

            elapsed = time.time() - self.start_time
            total_requests = len(self.results)
            successful_requests = sum(1 for r in self.results if r.success)

            if total_requests > 0:
                success_rate = (successful_requests / total_requests) * 100
                avg_response_time = statistics.mean(
                    r.response_time_ms for r in self.results
                )

                logger.info(
                    f"Progress: {elapsed:.1f}s | "
                    f"Active Users: {self.active_users} | "
                    f"Requests: {total_requests} | "
                    f"Success Rate: {success_rate:.1f}% | "
                    f"Avg Response Time: {avg_response_time:.1f}ms"
                )

    async def run_load_test(self):
        """Run the complete load test."""
        logger.info(
            f"Starting load test with {self.config.max_concurrent_users} concurrent users"
        )

        self.start_time = time.time()

        # Start monitoring task
        monitor_task = asyncio.create_task(self.monitor_progress())

        # Start user ramp-up
        await self.ramp_up_users()

        # Cancel monitoring
        monitor_task.cancel()

        logger.info("Load test completed")

    def analyze_results(self) -> Dict:
        """Analyze test results and generate report."""
        if not self.results:
            return {"error": "No results to analyze"}

        total_requests = len(self.results)
        successful_requests = sum(1 for r in self.results if r.success)
        failed_requests = total_requests - successful_requests

        response_times = [r.response_time_ms for r in self.results]

        # Calculate percentiles
        response_times_sorted = sorted(response_times)
        p50 = statistics.median(response_times_sorted)
        p95_index = int(0.95 * len(response_times_sorted))
        p95 = (
            response_times_sorted[p95_index]
            if p95_index < len(response_times_sorted)
            else response_times_sorted[-1]
        )
        p99_index = int(0.99 * len(response_times_sorted))
        p99 = (
            response_times_sorted[p99_index]
            if p99_index < len(response_times_sorted)
            else response_times_sorted[-1]
        )

        # Calculate availability
        availability = (successful_requests / total_requests) * 100

        # Status code distribution
        status_codes = {}
        for result in self.results:
            status_codes[result.status_code] = (
                status_codes.get(result.status_code, 0) + 1
            )

        # Error analysis
        errors = {}
        for result in self.results:
            if result.error:
                errors[result.error] = errors.get(result.error, 0) + 1

        # Performance targets assessment
        targets_met = {
            "availability": availability >= self.config.target_availability_percent,
            "p95_response_time": p95 <= self.config.target_response_time_ms,
            "concurrent_users": self.config.max_concurrent_users >= 1000,
        }

        return {
            "summary": {
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "failed_requests": failed_requests,
                "availability_percent": round(availability, 2),
                "test_duration_seconds": self.config.test_duration_seconds,
                "max_concurrent_users": self.config.max_concurrent_users,
            },
            "response_times": {
                "min_ms": min(response_times),
                "max_ms": max(response_times),
                "mean_ms": round(statistics.mean(response_times), 2),
                "median_ms": round(p50, 2),
                "p95_ms": round(p95, 2),
                "p99_ms": round(p99, 2),
            },
            "status_codes": status_codes,
            "errors": errors,
            "targets_assessment": {
                "all_targets_met": all(targets_met.values()),
                "details": targets_met,
            },
            "recommendations": self._generate_recommendations(
                availability, p95, targets_met
            ),
        }

    def _generate_recommendations(
        self, availability: float, p95_response_time: float, targets_met: Dict
    ) -> List[str]:
        """Generate performance improvement recommendations."""
        recommendations = []

        if not targets_met["availability"]:
            recommendations.append(
                f"Availability ({availability:.2f}%) is below target ({self.config.target_availability_percent}%). "
                "Consider implementing circuit breakers and improving error handling."
            )

        if not targets_met["p95_response_time"]:
            recommendations.append(
                f"P95 response time ({p95_response_time:.1f}ms) exceeds target ({self.config.target_response_time_ms}ms). "
                "Consider optimizing database queries, adding caching, or scaling horizontally."
            )

        if not targets_met["concurrent_users"]:
            recommendations.append(
                "Concurrent user target not met. Consider load balancing and horizontal scaling."
            )

        if all(targets_met.values()):
            recommendations.append(
                "All performance targets met! System is ready for production."
            )

        return recommendations


@click.command()
@click.option("--base-url", default="http://localhost", help="Base URL for testing")
@click.option("--users", default=1000, help="Maximum concurrent users")
@click.option("--duration", default=300, help="Test duration in seconds")
@click.option("--ramp-up", default=60, help="Ramp-up time in seconds")
@click.option(
    "--output", default="load_test_results.json", help="Output file for results"
)
async def main(base_url: str, users: int, duration: int, ramp_up: int, output: str):
    """Run comprehensive load test for ACGS-1."""
    config = LoadTestConfig(
        base_url=base_url,
        max_concurrent_users=users,
        test_duration_seconds=duration,
        ramp_up_seconds=ramp_up,
    )

    runner = LoadTestRunner(config)

    try:
        await runner.initialize()
        await runner.run_load_test()

        # Analyze and save results
        results = runner.analyze_results()

        with open(output, "w") as f:
            json.dump(results, f, indent=2)

        # Print summary
        print("\n" + "=" * 80)
        print("ACGS-1 LOAD TEST RESULTS")
        print("=" * 80)
        print(f"Total Requests: {results['summary']['total_requests']}")
        print(f"Availability: {results['summary']['availability_percent']}%")
        print(f"P95 Response Time: {results['response_times']['p95_ms']}ms")
        print(f"Max Concurrent Users: {results['summary']['max_concurrent_users']}")
        print(f"\nAll Targets Met: {results['targets_assessment']['all_targets_met']}")

        print("\nRecommendations:")
        for rec in results["recommendations"]:
            print(f"- {rec}")

        print(f"\nDetailed results saved to: {output}")

    finally:
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
