#!/usr/bin/env python3
"""
Comprehensive Load Testing for ACGS-2
Tests system performance under 10x baseline load.
"""

import asyncio
import logging
import statistics
import time
from typing import Any

import aiohttp

logger = logging.getLogger(__name__)


class LoadTester:
    """Comprehensive load testing system."""

    def __init__(self):
        self.baseline_rps = 100  # requests per second
        self.target_multiplier = 10
        self.test_duration_seconds = 1800  # 30 minutes
        self.latency_target_ms = 5

        self.results = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "response_times": [],
            "error_rates": [],
            "throughput_rps": 0,
        }

    async def run_load_test(self) -> dict[str, Any]:
        """Run comprehensive load test."""
        target_rps = self.baseline_rps * self.target_multiplier

        logger.info(
            f"Starting load test: {target_rps} RPS for {self.test_duration_seconds}s"
        )

        # Test endpoints
        endpoints = [
            {
                "url": "http://localhost:8001/api/v1/constitutional-ai/health",
                "weight": 0.3,
            },
            {
                "url": "http://localhost:8005/api/v1/policy-governance/health",
                "weight": 0.3,
            },
            {
                "url": "http://localhost:8004/api/v1/governance-synthesis/health",
                "weight": 0.4,
            },
        ]

        # Create semaphore to control concurrency
        semaphore = asyncio.Semaphore(target_rps)

        # Start load test
        start_time = time.time()
        tasks = []

        async with aiohttp.ClientSession() as session:
            while time.time() - start_time < self.test_duration_seconds:
                for endpoint in endpoints:
                    if time.time() - start_time >= self.test_duration_seconds:
                        break

                    # Create request task
                    task = asyncio.create_task(
                        self._make_request(session, endpoint["url"], semaphore)
                    )
                    tasks.append(task)

                    # Control request rate
                    await asyncio.sleep(1.0 / target_rps)

            # Wait for all requests to complete
            await asyncio.gather(*tasks, return_exceptions=True)

        # Calculate results
        return self._calculate_results()

    async def _make_request(
        self, session: aiohttp.ClientSession, url: str, semaphore: asyncio.Semaphore
    ):
        """Make individual HTTP request."""
        async with semaphore:
            start_time = time.time()
            try:
                async with session.get(
                    url, timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    response_time = (time.time() - start_time) * 1000  # Convert to ms

                    self.results["total_requests"] += 1
                    self.results["response_times"].append(response_time)

                    if response.status == 200:
                        self.results["successful_requests"] += 1
                    else:
                        self.results["failed_requests"] += 1

            except Exception:
                response_time = (time.time() - start_time) * 1000
                self.results["total_requests"] += 1
                self.results["failed_requests"] += 1
                self.results["response_times"].append(response_time)

    def _calculate_results(self) -> dict[str, Any]:
        """Calculate load test results."""
        if not self.results["response_times"]:
            return {"error": "No response times recorded"}

        response_times = self.results["response_times"]

        # Calculate percentiles
        p50 = statistics.median(response_times)
        p95 = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
        p99 = statistics.quantiles(response_times, n=100)[98]  # 99th percentile

        # Calculate error rate
        error_rate = (
            self.results["failed_requests"] / self.results["total_requests"]
            if self.results["total_requests"] > 0
            else 0
        )

        # Calculate throughput
        throughput = self.results["successful_requests"] / self.test_duration_seconds

        results = {
            "total_requests": self.results["total_requests"],
            "successful_requests": self.results["successful_requests"],
            "failed_requests": self.results["failed_requests"],
            "error_rate": error_rate,
            "throughput_rps": throughput,
            "response_time_p50_ms": p50,
            "response_time_p95_ms": p95,
            "response_time_p99_ms": p99,
            "latency_target_achieved": p99 <= self.latency_target_ms,
            "load_multiplier_achieved": throughput
            >= (self.baseline_rps * self.target_multiplier * 0.8),  # 80% of target
        }

        return results


async def main():
    """Main load testing function."""
    tester = LoadTester()

    print("🔥 Starting comprehensive load test...")
    print(
        f"Target: {tester.baseline_rps * tester.target_multiplier} RPS for {tester.test_duration_seconds}s"
    )

    # Run load test (shortened for demo)
    tester.test_duration_seconds = 60  # 1 minute for demo
    results = await tester.run_load_test()

    print("📊 Load Test Results:")
    print(f"  Total Requests: {results['total_requests']}")
    print(f"  Success Rate: {(1 - results['error_rate']) * 100:.1f}%")
    print(f"  Throughput: {results['throughput_rps']:.1f} RPS")
    print(f"  P99 Latency: {results['response_time_p99_ms']:.1f}ms")

    if results["latency_target_achieved"]:
        print("🎯 Latency target achieved!")
    else:
        print(
            f"⚠️  Latency target missed: {results['response_time_p99_ms']:.1f}ms > {tester.latency_target_ms}ms"
        )

    return results


if __name__ == "__main__":
    asyncio.run(main())
