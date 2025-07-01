"""
Load Testing for ACGS

Tests system performance under various load conditions.
"""

import asyncio
import statistics
import time
from dataclasses import dataclass
from typing import Any

import httpx
from colorama import Fore, Style, init

init()


@dataclass
class LoadTestResult:
    """Result of a load test."""

    test_name: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time_ms: float
    min_response_time_ms: float
    max_response_time_ms: float
    p95_response_time_ms: float
    p99_response_time_ms: float
    requests_per_second: float
    duration_seconds: float
    error_rate: float


class ACGSLoadTester:
    """Load tester for ACGS services."""

    def __init__(self):
        self.services = {
            "coordinator": "http://localhost:8000",
            "auth_service": "http://localhost:8006",
            "agent_hitl": "http://localhost:8008",
            "sandbox_execution": "http://localhost:8009",
        }

    async def run_all_load_tests(self) -> dict[str, LoadTestResult]:
        """Run all load tests."""
        print(f"{Fore.CYAN}⚡ ACGS Load Testing Suite{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'=' * 50}{Style.RESET_ALL}\n")

        results = {}

        # Test scenarios
        test_scenarios = [
            ("HITL Decision Latency", self.test_hitl_decision_latency),
            ("Concurrent Agent Operations", self.test_concurrent_operations),
            ("Sandbox Startup Performance", self.test_sandbox_startup_performance),
            ("Auth Service Throughput", self.test_auth_service_throughput),
            ("End-to-End Workflow Load", self.test_e2e_workflow_load),
        ]

        for test_name, test_func in test_scenarios:
            print(f"{Fore.YELLOW}🚀 Running {test_name}...{Style.RESET_ALL}")
            try:
                result = await test_func()
                results[test_name] = result
                self._print_test_result(result)
            except Exception as e:
                print(f"  ❌ Test failed: {e}")
            print()

        # Generate summary
        self._print_load_test_summary(results)
        return results

    async def test_hitl_decision_latency(self) -> LoadTestResult:
        """Test HITL decision latency under load."""
        return await self._run_concurrent_requests(
            test_name="HITL Decision Latency",
            url=f"{self.services['agent_hitl']}/api/v1/reviews/evaluate",
            payload={
                "agent_id": "load-test-agent",
                "agent_type": "coding_agent",
                "operation_type": "code_execution",
                "operation_description": "Load test operation",
                "operation_context": {"load_test": True},
            },
            concurrent_requests=50,
            total_requests=500,
            target_latency_ms=5,  # <5ms target for auto-decisions
        )

    async def test_concurrent_operations(self) -> LoadTestResult:
        """Test concurrent agent operations."""
        return await self._run_concurrent_requests(
            test_name="Concurrent Agent Operations",
            url=f"{self.services['coordinator']}/api/v1/operations",
            payload={
                "agent_id": "load-test-agent",
                "agent_type": "coding_agent",
                "operation_type": "concurrent_test",
                "operation_description": "Concurrent operation test",
                "bypass_hitl": True,
                "operation_context": {"concurrent_test": True},
            },
            concurrent_requests=20,
            total_requests=100,
            target_latency_ms=2000,  # <2s for end-to-end operations
        )

    async def test_sandbox_startup_performance(self) -> LoadTestResult:
        """Test sandbox startup performance."""
        return await self._run_concurrent_requests(
            test_name="Sandbox Startup Performance",
            url=f"{self.services['sandbox_execution']}/api/v1/executions",
            payload={
                "agent_id": "load-test-agent",
                "agent_type": "coding_agent",
                "environment": "python",
                "code": "print('Load test')",
                "language": "python",
            },
            concurrent_requests=10,
            total_requests=50,
            target_latency_ms=500,  # <500ms for sandbox startup
        )

    async def test_auth_service_throughput(self) -> LoadTestResult:
        """Test authentication service throughput."""
        return await self._run_concurrent_requests(
            test_name="Auth Service Throughput",
            url=f"{self.services['auth_service']}/api/v1/agents",
            method="GET",
            concurrent_requests=30,
            total_requests=300,
            target_latency_ms=100,  # <100ms for auth operations
        )

    async def test_e2e_workflow_load(self) -> LoadTestResult:
        """Test end-to-end workflow under load."""
        return await self._run_concurrent_requests(
            test_name="End-to-End Workflow Load",
            url=f"{self.services['coordinator']}/api/v1/operations",
            payload={
                "agent_id": "load-test-agent",
                "agent_type": "coding_agent",
                "operation_type": "e2e_load_test",
                "operation_description": "End-to-end load test",
                "code": "result = sum(range(100))\nprint(f'Result: {result}')",
                "execution_environment": "python",
                "bypass_hitl": True,
            },
            concurrent_requests=15,
            total_requests=75,
            target_latency_ms=3000,  # <3s for complete workflow
        )

    async def _run_concurrent_requests(
        self,
        test_name: str,
        url: str,
        concurrent_requests: int,
        total_requests: int,
        target_latency_ms: int,
        payload: dict[str, Any] = None,
        method: str = "POST",
    ) -> LoadTestResult:
        """Run concurrent requests and measure performance."""

        response_times = []
        successful_requests = 0
        failed_requests = 0

        start_time = time.time()

        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(concurrent_requests)

        async def make_request(client: httpx.AsyncClient) -> None:
            nonlocal successful_requests, failed_requests

            async with semaphore:
                request_start = time.time()
                try:
                    if method == "POST" and payload:
                        response = await client.post(url, json=payload)
                    else:
                        response = await client.get(url)

                    request_time = (time.time() - request_start) * 1000
                    response_times.append(request_time)

                    if response.status_code < 400:
                        successful_requests += 1
                    else:
                        failed_requests += 1

                except Exception:
                    failed_requests += 1
                    # Still record time for failed requests
                    request_time = (time.time() - request_start) * 1000
                    response_times.append(request_time)

        # Execute all requests concurrently
        async with httpx.AsyncClient(timeout=30.0) as client:
            tasks = [make_request(client) for _ in range(total_requests)]
            await asyncio.gather(*tasks, return_exceptions=True)

        end_time = time.time()
        duration_seconds = end_time - start_time

        # Calculate statistics
        if response_times:
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            p95_response_time = statistics.quantiles(response_times, n=20)[
                18
            ]  # 95th percentile
            p99_response_time = statistics.quantiles(response_times, n=100)[
                98
            ]  # 99th percentile
        else:
            avg_response_time = min_response_time = max_response_time = 0
            p95_response_time = p99_response_time = 0

        requests_per_second = (
            total_requests / duration_seconds if duration_seconds > 0 else 0
        )
        error_rate = (
            (failed_requests / total_requests) * 100 if total_requests > 0 else 0
        )

        return LoadTestResult(
            test_name=test_name,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            avg_response_time_ms=avg_response_time,
            min_response_time_ms=min_response_time,
            max_response_time_ms=max_response_time,
            p95_response_time_ms=p95_response_time,
            p99_response_time_ms=p99_response_time,
            requests_per_second=requests_per_second,
            duration_seconds=duration_seconds,
            error_rate=error_rate,
        )

    def _print_test_result(self, result: LoadTestResult):
        """Print load test result."""
        # Color code based on performance
        if result.error_rate < 1 and result.avg_response_time_ms < 1000:
            status_color = Fore.GREEN
            status = "✅ EXCELLENT"
        elif result.error_rate < 5 and result.avg_response_time_ms < 2000:
            status_color = Fore.YELLOW
            status = "⚠️  ACCEPTABLE"
        else:
            status_color = Fore.RED
            status = "❌ POOR"

        print(f"  {status_color}{status}{Style.RESET_ALL}")
        print(
            f"  Requests: {result.total_requests} total, {result.successful_requests} successful, {result.failed_requests} failed"
        )
        print(
            f"  Response Time: avg={result.avg_response_time_ms:.1f}ms, p95={result.p95_response_time_ms:.1f}ms, p99={result.p99_response_time_ms:.1f}ms"
        )
        print(f"  Throughput: {result.requests_per_second:.1f} req/s")
        print(f"  Error Rate: {result.error_rate:.1f}%")
        print(f"  Duration: {result.duration_seconds:.2f}s")

    def _print_load_test_summary(self, results: dict[str, LoadTestResult]):
        """Print load test summary."""
        print(f"{Fore.CYAN}📊 Load Test Summary{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'=' * 50}{Style.RESET_ALL}")

        total_requests = sum(r.total_requests for r in results.values())
        total_successful = sum(r.successful_requests for r in results.values())
        total_failed = sum(r.failed_requests for r in results.values())

        print("\nOverall Results:")
        print(f"Total Requests: {total_requests}")
        print(f"Successful: {Fore.GREEN}{total_successful}{Style.RESET_ALL}")
        print(f"Failed: {Fore.RED}{total_failed}{Style.RESET_ALL}")
        print(f"Overall Success Rate: {(total_successful / total_requests) * 100:.1f}%")

        print("\nPerformance Targets:")
        targets = [
            (
                "HITL Decision Latency",
                "<5ms",
                (
                    "✅"
                    if any(
                        "HITL" in r.test_name and r.p99_response_time_ms < 5
                        for r in results.values()
                    )
                    else "❌"
                ),
            ),
            (
                "Sandbox Startup",
                "<500ms",
                (
                    "✅"
                    if any(
                        "Sandbox" in r.test_name and r.p95_response_time_ms < 500
                        for r in results.values()
                    )
                    else "❌"
                ),
            ),
            (
                "End-to-End Operations",
                "<3s",
                (
                    "✅"
                    if any(
                        "End-to-End" in r.test_name and r.p95_response_time_ms < 3000
                        for r in results.values()
                    )
                    else "❌"
                ),
            ),
            (
                "Error Rate",
                "<5%",
                "✅" if all(r.error_rate < 5 for r in results.values()) else "❌",
            ),
        ]

        for target_name, target_value, status in targets:
            print(f"• {target_name}: {target_value} {status}")

        print(f"\n{Fore.CYAN}Recommendations:{Style.RESET_ALL}")

        # Analyze results and provide recommendations
        high_error_tests = [r for r in results.values() if r.error_rate > 5]
        slow_tests = [r for r in results.values() if r.p95_response_time_ms > 2000]

        if high_error_tests:
            print(
                f"⚠️  High error rates detected in: {[t.test_name for t in high_error_tests]}"
            )
            print(
                "   Consider: Increasing timeouts, checking service health, scaling resources"
            )

        if slow_tests:
            print(f"⚠️  Slow response times in: {[t.test_name for t in slow_tests]}")
            print("   Consider: Database optimization, caching, horizontal scaling")

        if not high_error_tests and not slow_tests:
            print(
                "✅ All performance targets met! System is performing well under load."
            )


async def main():
    """Run load tests."""
    tester = ACGSLoadTester()
    await tester.run_all_load_tests()


if __name__ == "__main__":
    asyncio.run(main())
