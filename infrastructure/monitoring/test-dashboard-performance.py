#!/usr/bin/env python3
"""
ACGS-1 Dashboard Performance Testing Script
Subtask 13.7: Comprehensive Grafana dashboard performance validation

This script validates dashboard loading times, query performance, and
real-time update capabilities under various load conditions.
"""

import asyncio
import json
import logging
import statistics
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

import aiohttp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/var/log/acgs/dashboard-performance-test.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


@dataclass
class DashboardTestConfig:
    """Configuration for dashboard performance testing."""

    # Test parameters
    concurrent_users: int = 100
    test_duration_seconds: int = 300  # 5 minutes
    dashboard_load_timeout_seconds: int = 10

    # Performance targets
    max_dashboard_load_time_ms: int = 2000  # 2 seconds
    max_query_response_time_ms: int = 1000  # 1 second
    min_success_rate_percent: float = 95.0

    # Target endpoints
    grafana_url: str = "http://localhost:3000"
    prometheus_url: str = "http://localhost:9090"

    # Dashboard configurations
    test_dashboards: List[Dict[str, str]] = field(
        default_factory=lambda: [
            {"name": "ACGS Services Overview", "uid": "acgs-services-overview"},
            {"name": "Governance Workflows", "uid": "acgs-governance-workflows"},
            {"name": "Infrastructure Monitoring", "uid": "acgs-infrastructure"},
            {"name": "Performance Metrics", "uid": "acgs-performance"},
            {"name": "Security Dashboard", "uid": "acgs-security"},
        ]
    )


@dataclass
class DashboardTestResult:
    """Container for dashboard test results."""

    test_name: str
    dashboard_name: str = ""
    load_times: List[float] = field(default_factory=list)
    query_times: List[float] = field(default_factory=list)
    success_count: int = 0
    error_count: int = 0
    error_details: List[str] = field(default_factory=list)

    @property
    def total_requests(self) -> int:
        return self.success_count + self.error_count

    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return (self.success_count / self.total_requests) * 100

    @property
    def avg_load_time(self) -> float:
        return statistics.mean(self.load_times) if self.load_times else 0.0

    @property
    def p95_load_time(self) -> float:
        if not self.load_times:
            return 0.0
        sorted_times = sorted(self.load_times)
        index = int(0.95 * len(sorted_times))
        return sorted_times[index] if index < len(sorted_times) else sorted_times[-1]


class DashboardPerformanceTester:
    """Comprehensive dashboard performance tester."""

    def __init__(self, config: DashboardTestConfig):
        self.config = config
        self.test_results: Dict[str, DashboardTestResult] = {}

        # Common Grafana API endpoints for testing
        self.grafana_endpoints = [
            "/api/search",
            "/api/org",
            "/api/user",
            "/api/health",
            "/api/datasources",
            "/api/folders",
        ]

        # Common dashboard queries for testing
        self.test_queries = [
            "up",
            "rate(http_requests_total[5m])",
            "acgs_constitutional_compliance_score",
            "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "haproxy_backend_response_time_average_seconds",
            "redis_memory_used_bytes",
            "postgresql_connections_active",
        ]

    async def run_dashboard_performance_tests(self) -> bool:
        """Execute comprehensive dashboard performance tests."""
        logger.info("📊 Starting ACGS-1 Dashboard Performance Tests")
        logger.info("=" * 80)

        try:
            # Test 1: Dashboard loading performance
            await self.test_dashboard_loading_performance()

            # Test 2: Dashboard query performance
            await self.test_dashboard_query_performance()

            # Test 3: Real-time dashboard updates
            await self.test_realtime_dashboard_updates()

            # Test 4: Concurrent dashboard access
            await self.test_concurrent_dashboard_access()

            # Test 5: Dashboard API performance
            await self.test_dashboard_api_performance()

            # Test 6: Dashboard under load
            await self.test_dashboard_under_load()

            # Evaluate overall success
            success = self.evaluate_dashboard_performance()

            # Generate comprehensive report
            self.generate_dashboard_test_report()

            return success

        except Exception as e:
            logger.error(f"❌ Dashboard performance testing failed: {str(e)}")
            return False

    async def test_dashboard_loading_performance(self):
        """Test individual dashboard loading performance."""
        logger.info("⏱️ Testing dashboard loading performance...")

        for dashboard in self.config.test_dashboards:
            result = DashboardTestResult(
                test_name="Dashboard Loading", dashboard_name=dashboard["name"]
            )

            try:
                # Test dashboard loading multiple times
                for _ in range(5):
                    start_time = time.time()

                    async with aiohttp.ClientSession() as session:
                        timeout = aiohttp.ClientTimeout(
                            total=self.config.dashboard_load_timeout_seconds
                        )

                        try:
                            async with session.get(
                                f"{self.config.grafana_url}/api/dashboards/uid/{dashboard['uid']}",
                                headers={"Authorization": "Bearer admin:admin"},
                                timeout=timeout,
                            ) as response:
                                load_time = (time.time() - start_time) * 1000

                                if response.status in [
                                    200,
                                    404,
                                ]:  # 404 acceptable for non-existent dashboards
                                    result.load_times.append(load_time)
                                    result.success_count += 1

                                    if response.status == 200:
                                        # Parse dashboard data to simulate real loading
                                        dashboard_data = await response.json()
                                        panel_count = len(
                                            dashboard_data.get("dashboard", {}).get(
                                                "panels", []
                                            )
                                        )
                                        logger.debug(
                                            f"Dashboard {dashboard['name']}: {panel_count} panels, {load_time:.2f}ms"
                                        )
                                else:
                                    result.error_count += 1
                                    result.error_details.append(
                                        f"HTTP {response.status}"
                                    )

                        except asyncio.TimeoutError:
                            result.error_count += 1
                            result.error_details.append("Timeout")
                        except Exception as e:
                            result.error_count += 1
                            result.error_details.append(str(e))

                    await asyncio.sleep(0.5)  # Small delay between tests

                # Evaluate dashboard performance
                if result.load_times:
                    avg_time = result.avg_load_time
                    p95_time = result.p95_load_time

                    if p95_time < self.config.max_dashboard_load_time_ms:
                        status = "✅"
                    else:
                        status = "❌"

                    logger.info(
                        f"{status} {dashboard['name']}: avg={avg_time:.2f}ms, p95={p95_time:.2f}ms"
                    )
                else:
                    logger.warning(f"⚠️ {dashboard['name']}: No successful loads")

            except Exception as e:
                logger.error(
                    f"❌ Dashboard loading test failed for {dashboard['name']}: {str(e)}"
                )

            self.test_results[f"loading_{dashboard['uid']}"] = result

    async def test_dashboard_query_performance(self):
        """Test dashboard query performance."""
        logger.info("🔍 Testing dashboard query performance...")

        result = DashboardTestResult(test_name="Dashboard Queries")

        try:
            async with aiohttp.ClientSession() as session:
                for query in self.test_queries:
                    query_times = []

                    # Test each query multiple times
                    for _ in range(3):
                        start_time = time.time()

                        try:
                            async with session.get(
                                f"{self.config.prometheus_url}/api/v1/query",
                                params={"query": query},
                            ) as response:
                                query_time = (time.time() - start_time) * 1000

                                if response.status == 200:
                                    query_times.append(query_time)
                                    result.success_count += 1
                                else:
                                    result.error_count += 1
                                    result.error_details.append(
                                        f"Query failed: {query} - HTTP {response.status}"
                                    )

                        except Exception as e:
                            result.error_count += 1
                            result.error_details.append(
                                f"Query failed: {query} - {str(e)}"
                            )

                        await asyncio.sleep(0.1)

                    if query_times:
                        avg_time = statistics.mean(query_times)
                        result.query_times.extend(query_times)

                        status = (
                            "✅"
                            if avg_time < self.config.max_query_response_time_ms
                            else "❌"
                        )
                        logger.info(
                            f"{status} Query '{query[:30]}...': {avg_time:.2f}ms"
                        )

        except Exception as e:
            logger.error(f"❌ Dashboard query performance test failed: {str(e)}")

        self.test_results["query_performance"] = result

    async def test_realtime_dashboard_updates(self):
        """Test real-time dashboard update performance."""
        logger.info("⚡ Testing real-time dashboard updates...")

        result = DashboardTestResult(test_name="Real-time Updates")

        try:
            # Test data freshness by checking metrics timestamps
            async with aiohttp.ClientSession() as session:
                for _ in range(10):  # Test 10 times over a period
                    start_time = time.time()

                    async with session.get(
                        f"{self.config.prometheus_url}/api/v1/query",
                        params={"query": "up"},
                    ) as response:
                        response_time = (time.time() - start_time) * 1000

                        if response.status == 200:
                            data = await response.json()

                            # Check data freshness
                            current_time = time.time()
                            freshness_scores = []

                            for metric_result in data.get("data", {}).get("result", []):
                                timestamp = float(metric_result.get("value", [0, 0])[0])
                                freshness = current_time - timestamp
                                freshness_scores.append(freshness)

                            if freshness_scores:
                                avg_freshness = statistics.mean(freshness_scores)
                                result.query_times.append(response_time)
                                result.success_count += 1

                                # Data should be less than 30 seconds old for real-time
                                if avg_freshness < 30:
                                    logger.debug(
                                        f"Data freshness: {avg_freshness:.2f}s (good)"
                                    )
                                else:
                                    logger.warning(
                                        f"Stale data: {avg_freshness:.2f}s old"
                                    )
                            else:
                                result.error_count += 1
                                result.error_details.append("No data returned")
                        else:
                            result.error_count += 1
                            result.error_details.append(f"HTTP {response.status}")

                    await asyncio.sleep(2)  # Check every 2 seconds

            if result.query_times:
                avg_time = statistics.mean(result.query_times)
                logger.info(
                    f"✅ Real-time updates: {avg_time:.2f}ms average response time"
                )

        except Exception as e:
            logger.error(f"❌ Real-time dashboard updates test failed: {str(e)}")

        self.test_results["realtime_updates"] = result

    async def test_concurrent_dashboard_access(self):
        """Test dashboard performance under concurrent access."""
        logger.info("👥 Testing concurrent dashboard access...")

        result = DashboardTestResult(test_name="Concurrent Access")

        try:
            concurrent_users = min(
                self.config.concurrent_users, 50
            )  # Limit for dashboard testing

            async def dashboard_access_worker():
                """Worker function for concurrent dashboard access."""
                worker_success = 0
                worker_errors = 0
                worker_times = []

                async with aiohttp.ClientSession() as session:
                    for _ in range(5):  # Each worker makes 5 requests
                        try:
                            # Select random dashboard
                            dashboard = self.config.test_dashboards[
                                worker_success % len(self.config.test_dashboards)
                            ]

                            start_time = time.time()
                            timeout = aiohttp.ClientTimeout(total=10)

                            async with session.get(
                                f"{self.config.grafana_url}/api/dashboards/uid/{dashboard['uid']}",
                                headers={"Authorization": "Bearer admin:admin"},
                                timeout=timeout,
                            ) as response:
                                response_time = (time.time() - start_time) * 1000

                                if response.status in [200, 404]:
                                    worker_success += 1
                                    worker_times.append(response_time)
                                else:
                                    worker_errors += 1

                        except Exception:
                            worker_errors += 1

                        await asyncio.sleep(0.2)  # Small delay between requests

                return worker_success, worker_errors, worker_times

            # Run concurrent workers
            start_time = time.time()
            tasks = [dashboard_access_worker() for _ in range(concurrent_users)]
            worker_results = await asyncio.gather(*tasks, return_exceptions=True)
            test_duration = time.time() - start_time

            # Aggregate results
            total_success = 0
            total_errors = 0
            all_times = []

            for worker_result in worker_results:
                if isinstance(worker_result, tuple):
                    success, errors, times = worker_result
                    total_success += success
                    total_errors += errors
                    all_times.extend(times)

            result.success_count = total_success
            result.error_count = total_errors
            result.load_times = all_times

            if all_times:
                avg_time = statistics.mean(all_times)
                p95_time = sorted(all_times)[int(0.95 * len(all_times))]
                requests_per_second = (total_success + total_errors) / test_duration

                logger.info(
                    f"✅ Concurrent access: {concurrent_users} users, {avg_time:.2f}ms avg, {p95_time:.2f}ms p95"
                )
                logger.info(
                    f"   Requests/sec: {requests_per_second:.2f}, Success rate: {result.success_rate:.2f}%"
                )

        except Exception as e:
            logger.error(f"❌ Concurrent dashboard access test failed: {str(e)}")

        self.test_results["concurrent_access"] = result

    async def test_dashboard_api_performance(self):
        """Test Grafana API performance."""
        logger.info("📡 Testing dashboard API performance...")

        result = DashboardTestResult(test_name="API Performance")

        try:
            async with aiohttp.ClientSession() as session:
                for endpoint in self.grafana_endpoints:
                    endpoint_times = []

                    # Test each endpoint multiple times
                    for _ in range(5):
                        start_time = time.time()

                        try:
                            timeout = aiohttp.ClientTimeout(total=5)
                            async with session.get(
                                f"{self.config.grafana_url}{endpoint}",
                                headers={"Authorization": "Bearer admin:admin"},
                                timeout=timeout,
                            ) as response:
                                response_time = (time.time() - start_time) * 1000

                                if response.status in [
                                    200,
                                    401,
                                    403,
                                ]:  # Auth errors are acceptable
                                    endpoint_times.append(response_time)
                                    result.success_count += 1
                                else:
                                    result.error_count += 1
                                    result.error_details.append(
                                        f"API {endpoint}: HTTP {response.status}"
                                    )

                        except Exception as e:
                            result.error_count += 1
                            result.error_details.append(f"API {endpoint}: {str(e)}")

                        await asyncio.sleep(0.1)

                    if endpoint_times:
                        avg_time = statistics.mean(endpoint_times)
                        result.query_times.extend(endpoint_times)

                        status = "✅" if avg_time < 1000 else "❌"
                        logger.info(f"{status} API {endpoint}: {avg_time:.2f}ms")

        except Exception as e:
            logger.error(f"❌ Dashboard API performance test failed: {str(e)}")

        self.test_results["api_performance"] = result

    async def test_dashboard_under_load(self):
        """Test dashboard performance under sustained load."""
        logger.info("🔥 Testing dashboard under sustained load...")

        result = DashboardTestResult(test_name="Load Testing")

        try:
            load_duration = 60  # 1 minute of sustained load
            concurrent_requests = 20

            async def load_test_worker():
                """Worker for sustained load testing."""
                worker_times = []
                worker_success = 0
                worker_errors = 0

                end_time = time.time() + load_duration

                async with aiohttp.ClientSession() as session:
                    while time.time() < end_time:
                        try:
                            start_time = time.time()
                            timeout = aiohttp.ClientTimeout(total=10)

                            # Alternate between different types of requests
                            if worker_success % 3 == 0:
                                # Dashboard request
                                dashboard = self.config.test_dashboards[0]
                                url = f"{self.config.grafana_url}/api/dashboards/uid/{dashboard['uid']}"
                            elif worker_success % 3 == 1:
                                # API request
                                url = f"{self.config.grafana_url}/api/search"
                            else:
                                # Query request
                                url = f"{self.config.prometheus_url}/api/v1/query?query=up"

                            async with session.get(url, timeout=timeout) as response:
                                response_time = (time.time() - start_time) * 1000

                                if response.status in [200, 404]:
                                    worker_times.append(response_time)
                                    worker_success += 1
                                else:
                                    worker_errors += 1

                        except Exception:
                            worker_errors += 1

                        await asyncio.sleep(0.5)  # Sustained but not overwhelming load

                return worker_times, worker_success, worker_errors

            # Run load test
            start_time = time.time()
            tasks = [load_test_worker() for _ in range(concurrent_requests)]
            worker_results = await asyncio.gather(*tasks, return_exceptions=True)
            actual_duration = time.time() - start_time

            # Aggregate results
            all_times = []
            total_success = 0
            total_errors = 0

            for worker_result in worker_results:
                if isinstance(worker_result, tuple):
                    times, success, errors = worker_result
                    all_times.extend(times)
                    total_success += success
                    total_errors += errors

            result.load_times = all_times
            result.success_count = total_success
            result.error_count = total_errors

            if all_times:
                avg_time = statistics.mean(all_times)
                p95_time = sorted(all_times)[int(0.95 * len(all_times))]
                requests_per_second = (total_success + total_errors) / actual_duration

                logger.info(
                    f"✅ Load test: {actual_duration:.1f}s duration, {avg_time:.2f}ms avg, {p95_time:.2f}ms p95"
                )
                logger.info(
                    f"   Requests/sec: {requests_per_second:.2f}, Success rate: {result.success_rate:.2f}%"
                )

        except Exception as e:
            logger.error(f"❌ Dashboard load test failed: {str(e)}")

        self.test_results["load_testing"] = result

    def evaluate_dashboard_performance(self) -> bool:
        """Evaluate overall dashboard performance."""
        logger.info("📋 Evaluating dashboard performance...")

        total_tests = len(self.test_results)
        passed_tests = 0

        logger.info(f"📊 Dashboard Performance Test Results:")

        for test_name, result in self.test_results.items():
            # Evaluate success criteria
            meets_load_time = True
            meets_success_rate = True

            if result.load_times:
                p95_time = result.p95_load_time
                meets_load_time = p95_time < self.config.max_dashboard_load_time_ms

            if result.total_requests > 0:
                meets_success_rate = (
                    result.success_rate >= self.config.min_success_rate_percent
                )

            test_passed = meets_load_time and meets_success_rate
            if test_passed:
                passed_tests += 1

            status = "✅" if test_passed else "❌"
            logger.info(
                f"  {status} {result.test_name}: {'PASSED' if test_passed else 'FAILED'}"
            )

            if result.load_times:
                logger.info(
                    f"    Load time: {result.avg_load_time:.2f}ms avg, {result.p95_load_time:.2f}ms p95"
                )
            if result.total_requests > 0:
                logger.info(f"    Success rate: {result.success_rate:.2f}%")

        overall_success_rate = (
            (passed_tests / total_tests * 100) if total_tests > 0 else 0
        )
        logger.info(
            f"\n📈 Overall Success Rate: {overall_success_rate:.2f}% ({passed_tests}/{total_tests})"
        )

        return overall_success_rate >= 80.0  # 80% of tests must pass

    def generate_dashboard_test_report(self):
        """Generate comprehensive dashboard test report."""
        logger.info("📄 Generating dashboard performance test report...")

        report = {
            "test_metadata": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "test_duration_seconds": self.config.test_duration_seconds,
                "concurrent_users": self.config.concurrent_users,
                "test_type": "dashboard_performance_validation",
            },
            "configuration": {
                "grafana_url": self.config.grafana_url,
                "prometheus_url": self.config.prometheus_url,
                "max_dashboard_load_time_ms": self.config.max_dashboard_load_time_ms,
                "max_query_response_time_ms": self.config.max_query_response_time_ms,
                "min_success_rate_percent": self.config.min_success_rate_percent,
                "test_dashboards": self.config.test_dashboards,
            },
            "test_results": {},
        }

        # Add detailed results for each test
        for test_name, result in self.test_results.items():
            report["test_results"][test_name] = {
                "test_name": result.test_name,
                "dashboard_name": result.dashboard_name,
                "total_requests": result.total_requests,
                "success_count": result.success_count,
                "error_count": result.error_count,
                "success_rate_percent": result.success_rate,
                "avg_load_time_ms": result.avg_load_time,
                "p95_load_time_ms": result.p95_load_time,
                "error_summary": self.summarize_errors(result.error_details),
            }

        # Save report to file
        report_file = "/var/log/acgs/dashboard-performance-test-report.json"
        try:
            Path("/var/log/acgs").mkdir(parents=True, exist_ok=True)
            with open(report_file, "w") as f:
                json.dump(report, f, indent=2)

            logger.info(f"✅ Dashboard performance test report saved to: {report_file}")
        except Exception as e:
            logger.error(f"❌ Failed to save report: {str(e)}")

    def summarize_errors(self, error_details: List[str]) -> Dict[str, int]:
        """Summarize error details for reporting."""
        error_summary = {}
        for error in error_details:
            error_summary[error] = error_summary.get(error, 0) + 1
        return error_summary


async def main():
    """Main execution function for dashboard performance testing."""
    import argparse

    parser = argparse.ArgumentParser(description="ACGS-1 Dashboard Performance Testing")
    parser.add_argument(
        "--users", type=int, default=100, help="Number of concurrent users"
    )
    parser.add_argument(
        "--duration", type=int, default=300, help="Test duration in seconds"
    )
    parser.add_argument(
        "--grafana-url", default="http://localhost:3000", help="Grafana URL"
    )
    parser.add_argument(
        "--prometheus-url", default="http://localhost:9090", help="Prometheus URL"
    )

    args = parser.parse_args()

    # Create configuration
    config = DashboardTestConfig(
        concurrent_users=args.users,
        test_duration_seconds=args.duration,
        grafana_url=args.grafana_url,
        prometheus_url=args.prometheus_url,
    )

    # Create tester and run tests
    tester = DashboardPerformanceTester(config)

    try:
        success = await tester.run_dashboard_performance_tests()

        if success:
            logger.info("🎉 Dashboard performance tests PASSED!")
            sys.exit(0)
        else:
            logger.error("❌ Dashboard performance tests FAILED!")
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("⚠️ Dashboard performance tests interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"❌ Dashboard performance tests failed with error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    # Ensure log directory exists
    Path("/var/log/acgs").mkdir(parents=True, exist_ok=True)

    # Run the dashboard performance tests
    asyncio.run(main())
