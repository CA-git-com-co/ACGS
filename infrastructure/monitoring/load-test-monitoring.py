#!/usr/bin/env python3
"""
ACGS-1 Monitoring Infrastructure Load Testing Script
Subtask 13.7: Specialized load testing for Prometheus/Grafana monitoring system

This script performs targeted load testing on the monitoring infrastructure
to validate performance under high concurrent load scenarios.
"""

import asyncio
import json
import logging
import random
import statistics
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import aiohttp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/var/log/acgs/monitoring-load-test.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


@dataclass
class LoadTestConfig:
    """Configuration for monitoring infrastructure load testing."""

    # Load test parameters
    concurrent_users: int = 1000
    test_duration_seconds: int = 300  # 5 minutes
    ramp_up_seconds: int = 60

    # Target endpoints
    prometheus_url: str = "http://localhost:9090"
    grafana_url: str = "http://localhost:3000"
    alertmanager_url: str = "http://localhost:9093"
    haproxy_exporter_url: str = "http://localhost:9101"

    # Test scenarios
    prometheus_query_weight: float = 0.4  # 40% of requests
    grafana_dashboard_weight: float = 0.3  # 30% of requests
    metrics_scraping_weight: float = 0.2  # 20% of requests
    alertmanager_weight: float = 0.1  # 10% of requests


@dataclass
class LoadTestResult:
    """Container for load test results."""

    scenario_name: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    response_times: list[float] = field(default_factory=list)
    error_details: list[str] = field(default_factory=list)
    start_time: float = 0
    end_time: float = 0

    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100

    @property
    def avg_response_time(self) -> float:
        return statistics.mean(self.response_times) if self.response_times else 0.0

    @property
    def p95_response_time(self) -> float:
        if not self.response_times:
            return 0.0
        sorted_times = sorted(self.response_times)
        index = int(0.95 * len(sorted_times))
        return sorted_times[index] if index < len(sorted_times) else sorted_times[-1]

    @property
    def requests_per_second(self) -> float:
        duration = self.end_time - self.start_time
        return self.total_requests / duration if duration > 0 else 0.0


class MonitoringLoadTester:
    """Specialized load tester for monitoring infrastructure."""

    def __init__(self, config: LoadTestConfig):
        self.config = config
        self.results: dict[str, LoadTestResult] = {}
        self.active_sessions = 0

        # Prometheus test queries
        self.prometheus_queries = [
            "up",
            "rate(http_requests_total[5m])",
            "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "acgs_constitutional_compliance_score",
            "acgs_policy_synthesis_operations_total",
            "haproxy_backend_response_time_average_seconds",
            "redis_memory_used_bytes",
            "postgresql_connections_active",
            "node_cpu_seconds_total",
            "node_memory_MemAvailable_bytes",
        ]

        # Grafana dashboard endpoints
        self.grafana_endpoints = [
            "/api/search?query=ACGS",
            "/api/dashboards/uid/acgs-services-overview",
            "/api/dashboards/uid/acgs-governance-workflows",
            "/api/dashboards/uid/acgs-infrastructure",
            "/api/dashboards/uid/acgs-performance",
            "/api/health",
            "/api/org",
            "/api/user",
        ]

    async def run_load_test(self) -> dict[str, LoadTestResult]:
        """Execute comprehensive load test on monitoring infrastructure."""
        logger.info("🚀 Starting monitoring infrastructure load test")
        logger.info(
            f"📊 Configuration: {self.config.concurrent_users} users, {self.config.test_duration_seconds}s duration"
        )

        # Initialize results
        self.results = {
            "prometheus_queries": LoadTestResult("Prometheus Queries"),
            "grafana_dashboards": LoadTestResult("Grafana Dashboards"),
            "metrics_scraping": LoadTestResult("Metrics Scraping"),
            "alertmanager_api": LoadTestResult("Alertmanager API"),
        }

        # Create load test tasks
        tasks = []

        # Calculate number of workers per scenario
        total_workers = self.config.concurrent_users
        prometheus_workers = int(total_workers * self.config.prometheus_query_weight)
        grafana_workers = int(total_workers * self.config.grafana_dashboard_weight)
        metrics_workers = int(total_workers * self.config.metrics_scraping_weight)
        alertmanager_workers = (
            total_workers - prometheus_workers - grafana_workers - metrics_workers
        )

        logger.info("📈 Worker distribution:")
        logger.info(f"  Prometheus queries: {prometheus_workers} workers")
        logger.info(f"  Grafana dashboards: {grafana_workers} workers")
        logger.info(f"  Metrics scraping: {metrics_workers} workers")
        logger.info(f"  Alertmanager API: {alertmanager_workers} workers")

        # Create worker tasks
        for i in range(prometheus_workers):
            tasks.append(self.prometheus_query_worker(f"prometheus_{i}"))

        for i in range(grafana_workers):
            tasks.append(self.grafana_dashboard_worker(f"grafana_{i}"))

        for i in range(metrics_workers):
            tasks.append(self.metrics_scraping_worker(f"metrics_{i}"))

        for i in range(alertmanager_workers):
            tasks.append(self.alertmanager_api_worker(f"alertmanager_{i}"))

        # Execute load test with ramp-up
        start_time = time.time()

        # Gradual ramp-up
        if self.config.ramp_up_seconds > 0:
            logger.info(f"⏰ Ramping up over {self.config.ramp_up_seconds} seconds...")
            batch_size = max(1, len(tasks) // 10)  # 10 batches
            batch_delay = self.config.ramp_up_seconds / 10

            for i in range(0, len(tasks), batch_size):
                batch = tasks[i : i + batch_size]
                for task in batch:
                    asyncio.create_task(task)

                if i + batch_size < len(tasks):  # Don't delay after last batch
                    await asyncio.sleep(batch_delay)

        # Wait for test completion
        await asyncio.sleep(self.config.test_duration_seconds)

        end_time = time.time()
        total_duration = end_time - start_time

        logger.info(f"✅ Load test completed in {total_duration:.2f} seconds")

        # Generate summary
        self.generate_load_test_summary()

        return self.results

    async def prometheus_query_worker(self, worker_id: str):
        """Worker for Prometheus query load testing."""
        result = self.results["prometheus_queries"]
        result.start_time = time.time()

        end_time = (
            time.time()
            + self.config.test_duration_seconds
            + self.config.ramp_up_seconds
        )

        async with aiohttp.ClientSession() as session:
            while time.time() < end_time:
                try:
                    # Select random query
                    query = random.choice(self.prometheus_queries)

                    start_request = time.time()
                    timeout = aiohttp.ClientTimeout(total=10)

                    async with session.get(
                        f"{self.config.prometheus_url}/api/v1/query",
                        params={"query": query},
                        timeout=timeout,
                    ) as response:
                        response_time = (time.time() - start_request) * 1000

                        result.total_requests += 1
                        result.response_times.append(response_time)

                        if response.status == 200:
                            result.successful_requests += 1
                        else:
                            result.failed_requests += 1
                            result.error_details.append(f"HTTP {response.status}")

                except Exception as e:
                    result.total_requests += 1
                    result.failed_requests += 1
                    result.error_details.append(str(e))

                # Variable delay to simulate realistic usage
                await asyncio.sleep(random.uniform(0.1, 0.5))

        result.end_time = time.time()

    async def grafana_dashboard_worker(self, worker_id: str):
        """Worker for Grafana dashboard load testing."""
        result = self.results["grafana_dashboards"]
        result.start_time = time.time()

        end_time = (
            time.time()
            + self.config.test_duration_seconds
            + self.config.ramp_up_seconds
        )

        async with aiohttp.ClientSession() as session:
            while time.time() < end_time:
                try:
                    # Select random endpoint
                    endpoint = random.choice(self.grafana_endpoints)

                    start_request = time.time()
                    timeout = aiohttp.ClientTimeout(total=15)

                    async with session.get(
                        f"{self.config.grafana_url}{endpoint}",
                        headers={"Authorization": "Bearer admin:admin"},
                        timeout=timeout,
                    ) as response:
                        response_time = (time.time() - start_request) * 1000

                        result.total_requests += 1
                        result.response_times.append(response_time)

                        if response.status in [
                            200,
                            404,
                        ]:  # 404 acceptable for non-existent dashboards
                            result.successful_requests += 1
                        else:
                            result.failed_requests += 1
                            result.error_details.append(f"HTTP {response.status}")

                except Exception as e:
                    result.total_requests += 1
                    result.failed_requests += 1
                    result.error_details.append(str(e))

                # Longer delay for dashboard requests
                await asyncio.sleep(random.uniform(0.5, 2.0))

        result.end_time = time.time()

    async def metrics_scraping_worker(self, worker_id: str):
        """Worker for metrics endpoint load testing."""
        result = self.results["metrics_scraping"]
        result.start_time = time.time()

        end_time = (
            time.time()
            + self.config.test_duration_seconds
            + self.config.ramp_up_seconds
        )

        # Metrics endpoints to test
        metrics_endpoints = [
            f"{self.config.prometheus_url}/metrics",
            f"{self.config.haproxy_exporter_url}/metrics",
            "http://localhost:8000/metrics",  # Auth service
            "http://localhost:8001/metrics",  # AC service
            "http://localhost:8004/metrics",  # GS service
            "http://localhost:8005/metrics",  # PGC service
        ]

        async with aiohttp.ClientSession() as session:
            while time.time() < end_time:
                try:
                    # Select random metrics endpoint
                    endpoint = random.choice(metrics_endpoints)

                    start_request = time.time()
                    timeout = aiohttp.ClientTimeout(total=5)

                    async with session.get(endpoint, timeout=timeout) as response:
                        response_time = (time.time() - start_request) * 1000

                        result.total_requests += 1
                        result.response_times.append(response_time)

                        if response.status == 200:
                            result.successful_requests += 1
                        else:
                            result.failed_requests += 1
                            result.error_details.append(f"HTTP {response.status}")

                except Exception as e:
                    result.total_requests += 1
                    result.failed_requests += 1
                    result.error_details.append(str(e))

                # Fast polling for metrics
                await asyncio.sleep(random.uniform(0.05, 0.2))

        result.end_time = time.time()

    async def alertmanager_api_worker(self, worker_id: str):
        """Worker for Alertmanager API load testing."""
        result = self.results["alertmanager_api"]
        result.start_time = time.time()

        end_time = (
            time.time()
            + self.config.test_duration_seconds
            + self.config.ramp_up_seconds
        )

        # Alertmanager endpoints to test
        alertmanager_endpoints = [
            "/api/v1/status",
            "/api/v1/alerts",
            "/api/v1/alerts/groups",
            "/-/healthy",
        ]

        async with aiohttp.ClientSession() as session:
            while time.time() < end_time:
                try:
                    # Select random endpoint
                    endpoint = random.choice(alertmanager_endpoints)

                    start_request = time.time()
                    timeout = aiohttp.ClientTimeout(total=10)

                    async with session.get(
                        f"{self.config.alertmanager_url}{endpoint}", timeout=timeout
                    ) as response:
                        response_time = (time.time() - start_request) * 1000

                        result.total_requests += 1
                        result.response_times.append(response_time)

                        if response.status == 200:
                            result.successful_requests += 1
                        else:
                            result.failed_requests += 1
                            result.error_details.append(f"HTTP {response.status}")

                except Exception as e:
                    result.total_requests += 1
                    result.failed_requests += 1
                    result.error_details.append(str(e))

                # Medium delay for alertmanager requests
                await asyncio.sleep(random.uniform(0.2, 1.0))

        result.end_time = time.time()

    def generate_load_test_summary(self):
        """Generate comprehensive load test summary."""
        logger.info("\n" + "=" * 80)
        logger.info("📊 MONITORING INFRASTRUCTURE LOAD TEST SUMMARY")
        logger.info("=" * 80)

        total_requests = sum(result.total_requests for result in self.results.values())
        total_successful = sum(
            result.successful_requests for result in self.results.values()
        )
        total_failed = sum(result.failed_requests for result in self.results.values())

        overall_success_rate = (
            (total_successful / total_requests * 100) if total_requests > 0 else 0
        )

        logger.info("🎯 Overall Statistics:")
        logger.info(f"  Total Requests: {total_requests:,}")
        logger.info(f"  Successful: {total_successful:,}")
        logger.info(f"  Failed: {total_failed:,}")
        logger.info(f"  Success Rate: {overall_success_rate:.2f}%")

        logger.info("\n📈 Scenario Results:")

        for scenario_name, result in self.results.items():
            if result.total_requests > 0:
                logger.info(f"\n  {scenario_name}:")
                logger.info(f"    Requests: {result.total_requests:,}")
                logger.info(f"    Success Rate: {result.success_rate:.2f}%")
                logger.info(f"    Avg Response Time: {result.avg_response_time:.2f}ms")
                logger.info(f"    95th Percentile: {result.p95_response_time:.2f}ms")
                logger.info(f"    Requests/sec: {result.requests_per_second:.2f}")

                # Performance assessment
                if result.p95_response_time < 500:
                    status = "✅ EXCELLENT"
                elif result.p95_response_time < 1000:
                    status = "✅ GOOD"
                elif result.p95_response_time < 2000:
                    status = "⚠️ ACCEPTABLE"
                else:
                    status = "❌ POOR"

                logger.info(f"    Performance: {status}")

        # Save detailed results
        self.save_load_test_results()

        logger.info("=" * 80)

    def save_load_test_results(self):
        """Save detailed load test results to file."""
        report = {
            "test_metadata": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "test_duration_seconds": self.config.test_duration_seconds,
                "concurrent_users": self.config.concurrent_users,
                "ramp_up_seconds": self.config.ramp_up_seconds,
                "test_type": "monitoring_infrastructure_load_test",
            },
            "configuration": {
                "prometheus_url": self.config.prometheus_url,
                "grafana_url": self.config.grafana_url,
                "alertmanager_url": self.config.alertmanager_url,
                "haproxy_exporter_url": self.config.haproxy_exporter_url,
                "scenario_weights": {
                    "prometheus_queries": self.config.prometheus_query_weight,
                    "grafana_dashboards": self.config.grafana_dashboard_weight,
                    "metrics_scraping": self.config.metrics_scraping_weight,
                    "alertmanager_api": self.config.alertmanager_weight,
                },
            },
            "results": {},
        }

        # Add detailed results for each scenario
        for scenario_name, result in self.results.items():
            report["results"][scenario_name] = {
                "total_requests": result.total_requests,
                "successful_requests": result.successful_requests,
                "failed_requests": result.failed_requests,
                "success_rate_percent": result.success_rate,
                "avg_response_time_ms": result.avg_response_time,
                "p95_response_time_ms": result.p95_response_time,
                "requests_per_second": result.requests_per_second,
                "error_summary": self.summarize_errors(result.error_details),
            }

        # Save to file
        report_file = "/var/log/acgs/monitoring-load-test-results.json"
        try:
            Path("/var/log/acgs").mkdir(parents=True, exist_ok=True)
            with open(report_file, "w") as f:
                json.dump(report, f, indent=2)

            logger.info(f"📄 Detailed results saved to: {report_file}")
        except Exception as e:
            logger.error(f"❌ Failed to save results: {e!s}")

    def summarize_errors(self, error_details: list[str]) -> dict[str, int]:
        """Summarize error details for reporting."""
        error_summary = {}
        for error in error_details:
            error_summary[error] = error_summary.get(error, 0) + 1
        return error_summary


async def main():
    """Main execution function for monitoring load testing."""
    import argparse

    parser = argparse.ArgumentParser(
        description="ACGS-1 Monitoring Infrastructure Load Testing"
    )
    parser.add_argument(
        "--users", type=int, default=1000, help="Number of concurrent users"
    )
    parser.add_argument(
        "--duration", type=int, default=300, help="Test duration in seconds"
    )
    parser.add_argument(
        "--ramp-up", type=int, default=60, help="Ramp-up duration in seconds"
    )
    parser.add_argument(
        "--prometheus-url", default="http://localhost:9090", help="Prometheus URL"
    )
    parser.add_argument(
        "--grafana-url", default="http://localhost:3000", help="Grafana URL"
    )

    args = parser.parse_args()

    # Create configuration
    config = LoadTestConfig(
        concurrent_users=args.users,
        test_duration_seconds=args.duration,
        ramp_up_seconds=args.ramp_up,
        prometheus_url=args.prometheus_url,
        grafana_url=args.grafana_url,
    )

    # Create load tester and run tests
    tester = MonitoringLoadTester(config)

    try:
        results = await tester.run_load_test()

        # Evaluate success criteria
        overall_success_rate = sum(r.success_rate for r in results.values()) / len(
            results
        )
        overall_p95_time = max(r.p95_response_time for r in results.values())

        if overall_success_rate >= 95.0 and overall_p95_time < 2000:
            logger.info("🎉 Monitoring infrastructure load test PASSED!")
            sys.exit(0)
        else:
            logger.error("❌ Monitoring infrastructure load test FAILED!")
            logger.error(f"   Success rate: {overall_success_rate:.2f}% (target: ≥95%)")
            logger.error(f"   Max P95 time: {overall_p95_time:.2f}ms (target: <2000ms)")
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("⚠️ Load test interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"❌ Load test failed with error: {e!s}")
        sys.exit(1)


if __name__ == "__main__":
    # Ensure log directory exists
    Path("/var/log/acgs").mkdir(parents=True, exist_ok=True)

    # Run the load test
    asyncio.run(main())
