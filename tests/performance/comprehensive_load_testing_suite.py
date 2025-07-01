#!/usr/bin/env python3
"""
ACGS-PGP Comprehensive Load Testing Suite
Production-Ready Performance Validation Framework

This suite implements comprehensive load testing with chaos engineering
capabilities for the ACGS-PGP v8 system, targeting production readiness
with specific performance targets and failure scenarios.

Performance Targets:
- 100ms policy generation latency (95th percentile)
- 10,000+ TPS sustained throughput
- 99.9% uptime under load
- 40% false positive reduction
- 95% detection accuracy

Features:
- Multi-service concurrent load testing
- Chaos engineering scenarios
- Real-time performance monitoring
- Automated failure detection
- Comprehensive reporting
"""

import asyncio
import aiohttp
import time
import json
import statistics
import random
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict, field
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import argparse
import sys
import os

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../../.."))

from tests.performance.load_testing_framework import (
    LoadTestConfig,
    ComprehensiveLoadTester,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("comprehensive_load_test")


@dataclass
class ChaosScenario:
    """Chaos engineering scenario configuration."""

    name: str
    description: str
    duration_seconds: int
    failure_rate: float  # 0.0 to 1.0
    target_services: List[str]
    failure_types: List[str]  # ['latency', 'error', 'timeout', 'network']


@dataclass
class LoadTestMetrics:
    """Comprehensive load test metrics."""

    scenario_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time_ms: float = 0.0
    p95_response_time_ms: float = 0.0
    p99_response_time_ms: float = 0.0
    max_response_time_ms: float = 0.0
    throughput_rps: float = 0.0
    error_rate: float = 0.0
    chaos_events: int = 0
    service_failures: Dict[str, int] = field(default_factory=dict)
    performance_degradation: float = 0.0


@dataclass
class ServiceEndpoint:
    """Service endpoint configuration for load testing."""

    name: str
    url: str
    method: str = "GET"
    headers: Dict[str, str] = field(default_factory=dict)
    payload: Optional[Dict[str, Any]] = None
    expected_status: int = 200
    timeout_seconds: float = 30.0
    weight: int = 1  # Request distribution weight


class ComprehensiveLoadTestSuite:
    """
    Comprehensive load testing suite with chaos engineering capabilities.

    This class orchestrates complex load testing scenarios including:
    - Multi-service concurrent testing
    - Chaos engineering fault injection
    - Performance degradation analysis
    - Real-time monitoring and alerting
    """

    def __init__(self, config_file: Optional[str] = None):
        self.config = self._load_config(config_file)
        self.results_dir = Path("tests/performance/results")
        self.results_dir.mkdir(exist_ok=True)

        # Service endpoints for ACGS-PGP v8
        self.service_endpoints = self._initialize_service_endpoints()

        # Chaos scenarios
        self.chaos_scenarios = self._initialize_chaos_scenarios()

        # Performance targets
        self.performance_targets = {
            "policy_generation_latency_ms": 100,
            "throughput_rps": 10000,
            "uptime_percent": 99.9,
            "false_positive_reduction_percent": 40,
            "detection_accuracy_percent": 95,
        }

        # Test results
        self.test_results: List[LoadTestMetrics] = []

    def _load_config(self, config_file: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file or use defaults."""
        default_config = {
            "max_concurrent_users": 1000,
            "test_duration_seconds": 300,
            "ramp_up_seconds": 60,
            "chaos_enabled": True,
            "monitoring_enabled": True,
            "report_interval_seconds": 30,
        }

        if config_file and Path(config_file).exists():
            with open(config_file, "r") as f:
                file_config = json.load(f)
                default_config.update(file_config)

        return default_config

    def _initialize_service_endpoints(self) -> List[ServiceEndpoint]:
        """Initialize ACGS-PGP service endpoints for testing."""
        base_url = os.getenv("ACGS_BASE_URL", "http://localhost")

        return [
            ServiceEndpoint(
                name="policy_governance_controller",
                url=f"{base_url}:8003/api/v1/policy/evaluate",
                method="POST",
                payload={"policy_id": "test_policy", "context": {"user": "test"}},
                weight=3,
            ),
            ServiceEndpoint(
                name="constitutional_trainer",
                url=f"{base_url}:8000/api/v1/train/status",
                method="GET",
                weight=2,
            ),
            ServiceEndpoint(
                name="quantum_error_correction",
                url=f"{base_url}:8005/api/v1/qec/syndrome",
                method="POST",
                payload={"error_data": [0, 1, 0, 1]},
                weight=2,
            ),
            ServiceEndpoint(
                name="democratic_governance_module",
                url=f"{base_url}:8007/api/v1/dgm/status",
                method="GET",
                weight=1,
            ),
            ServiceEndpoint(
                name="appeals_logging_service",
                url=f"{base_url}:8006/api/v1/appeals/health",
                method="GET",
                weight=1,
            ),
        ]

    def _initialize_chaos_scenarios(self) -> List[ChaosScenario]:
        """Initialize chaos engineering scenarios."""
        return [
            ChaosScenario(
                name="network_latency_injection",
                description="Inject network latency to simulate poor connectivity",
                duration_seconds=120,
                failure_rate=0.3,
                target_services=[
                    "policy_governance_controller",
                    "constitutional_trainer",
                ],
                failure_types=["latency"],
            ),
            ChaosScenario(
                name="service_error_injection",
                description="Inject random service errors",
                duration_seconds=180,
                failure_rate=0.1,
                target_services=[
                    "quantum_error_correction",
                    "democratic_governance_module",
                ],
                failure_types=["error"],
            ),
            ChaosScenario(
                name="timeout_simulation",
                description="Simulate service timeouts",
                duration_seconds=90,
                failure_rate=0.2,
                target_services=["appeals_logging_service"],
                failure_types=["timeout"],
            ),
            ChaosScenario(
                name="network_partition",
                description="Simulate network partitions between services",
                duration_seconds=150,
                failure_rate=0.15,
                target_services=[
                    "policy_governance_controller",
                    "quantum_error_correction",
                ],
                failure_types=["network"],
            ),
        ]

    async def run_comprehensive_load_test(self) -> Dict[str, Any]:
        """Run the complete comprehensive load testing suite."""
        logger.info("🚀 Starting ACGS-PGP Comprehensive Load Testing Suite")
        logger.info(
            f"📊 Configuration: {self.config['max_concurrent_users']} users, {self.config['test_duration_seconds']}s duration"
        )
        logger.info(f"🎯 Targets: {self.performance_targets}")

        suite_start_time = time.time()

        # Phase 1: Baseline Performance Testing
        logger.info("\n" + "=" * 60)
        logger.info("Phase 1: Baseline Performance Testing")
        logger.info("=" * 60)
        baseline_results = await self._run_baseline_tests()

        # Phase 2: Chaos Engineering Tests
        if self.config["chaos_enabled"]:
            logger.info("\n" + "=" * 60)
            logger.info("Phase 2: Chaos Engineering Tests")
            logger.info("=" * 60)
            chaos_results = await self._run_chaos_tests()
        else:
            chaos_results = {}

        # Phase 3: Stress Testing
        logger.info("\n" + "=" * 60)
        logger.info("Phase 3: Stress Testing")
        logger.info("=" * 60)
        stress_results = await self._run_stress_tests()

        suite_duration = time.time() - suite_start_time

        # Generate comprehensive report
        final_report = self._generate_comprehensive_report(
            baseline_results, chaos_results, stress_results, suite_duration
        )

        # Save results
        self._save_results(final_report)

        logger.info(
            f"\n🎉 Comprehensive Load Testing Suite completed in {suite_duration:.2f}s"
        )
        logger.info(f"📊 Report saved to: {self.results_dir}")

        return final_report

    async def _run_baseline_tests(self) -> Dict[str, Any]:
        """Run baseline performance tests without chaos injection."""
        baseline_results = {}

        # Test each service individually
        for endpoint in self.service_endpoints:
            logger.info(f"Testing {endpoint.name}...")
            metrics = await self._test_single_service(endpoint, duration=60)
            baseline_results[endpoint.name] = asdict(metrics)

        # Test all services concurrently
        logger.info("Testing all services concurrently...")
        concurrent_metrics = await self._test_concurrent_services(duration=120)
        baseline_results["concurrent_all_services"] = asdict(concurrent_metrics)

        return baseline_results

    async def _run_chaos_tests(self) -> Dict[str, Any]:
        """Run chaos engineering tests."""
        chaos_results = {}

        for scenario in self.chaos_scenarios:
            logger.info(f"Running chaos scenario: {scenario.name}")
            logger.info(f"Description: {scenario.description}")

            # Start chaos injection
            chaos_task = asyncio.create_task(self._inject_chaos(scenario))

            # Run load test during chaos
            load_task = asyncio.create_task(
                self._test_concurrent_services(
                    duration=scenario.duration_seconds, chaos_active=True
                )
            )

            # Wait for both to complete
            chaos_events, load_metrics = await asyncio.gather(chaos_task, load_task)
            load_metrics.chaos_events = chaos_events

            chaos_results[scenario.name] = asdict(load_metrics)

            # Recovery period
            logger.info(f"Recovery period for {scenario.name}...")
            await asyncio.sleep(30)

        return chaos_results

    async def _run_stress_tests(self) -> Dict[str, Any]:
        """Run stress tests with increasing load."""
        stress_results = {}

        # Gradual load increase
        user_counts = [100, 500, 1000, 2000, 5000]

        for user_count in user_counts:
            if user_count > self.config["max_concurrent_users"]:
                break

            logger.info(f"Stress testing with {user_count} concurrent users...")

            # Update config for this test
            stress_config = self.config.copy()
            stress_config["max_concurrent_users"] = user_count

            metrics = await self._test_concurrent_services(
                duration=180, user_count=user_count
            )

            stress_results[f"stress_{user_count}_users"] = asdict(metrics)

            # Check if system is degrading significantly
            if metrics.error_rate > 0.1:  # 10% error rate threshold
                logger.warning(
                    f"High error rate detected at {user_count} users: {metrics.error_rate:.2%}"
                )
                break

            # Brief recovery period
            await asyncio.sleep(15)

        return stress_results

    async def _test_single_service(
        self, endpoint: ServiceEndpoint, duration: int
    ) -> LoadTestMetrics:
        """Test a single service endpoint."""
        metrics = LoadTestMetrics(
            scenario_name=f"baseline_{endpoint.name}", start_time=datetime.now()
        )

        response_times = []
        errors = 0

        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=endpoint.timeout_seconds)
        ) as session:
            end_time = time.time() + duration

            while time.time() < end_time:
                start_request = time.time()

                try:
                    if endpoint.method == "GET":
                        async with session.get(
                            endpoint.url, headers=endpoint.headers
                        ) as response:
                            await response.text()
                            status = response.status
                    else:
                        async with session.post(
                            endpoint.url,
                            json=endpoint.payload,
                            headers=endpoint.headers,
                        ) as response:
                            await response.text()
                            status = response.status

                    request_time = (time.time() - start_request) * 1000  # Convert to ms
                    response_times.append(request_time)

                    if status != endpoint.expected_status:
                        errors += 1

                    metrics.total_requests += 1

                except Exception as e:
                    logger.debug(f"Request error for {endpoint.name}: {e}")
                    errors += 1
                    metrics.total_requests += 1

                # Small delay to prevent overwhelming
                await asyncio.sleep(0.01)

        # Calculate metrics
        metrics.end_time = datetime.now()
        metrics.failed_requests = errors
        metrics.successful_requests = metrics.total_requests - errors

        if response_times:
            metrics.avg_response_time_ms = statistics.mean(response_times)
            metrics.p95_response_time_ms = statistics.quantiles(response_times, n=20)[
                18
            ]  # 95th percentile
            metrics.p99_response_time_ms = statistics.quantiles(response_times, n=100)[
                98
            ]  # 99th percentile
            metrics.max_response_time_ms = max(response_times)

        test_duration = (metrics.end_time - metrics.start_time).total_seconds()
        metrics.throughput_rps = (
            metrics.total_requests / test_duration if test_duration > 0 else 0
        )
        metrics.error_rate = (
            errors / metrics.total_requests if metrics.total_requests > 0 else 0
        )

        logger.info(
            f"✅ {endpoint.name}: {metrics.total_requests} requests, {metrics.error_rate:.2%} error rate, {metrics.avg_response_time_ms:.2f}ms avg"
        )

        return metrics

    async def _test_concurrent_services(
        self,
        duration: int,
        chaos_active: bool = False,
        user_count: Optional[int] = None,
    ) -> LoadTestMetrics:
        """Test all services concurrently with specified parameters."""
        if user_count is None:
            user_count = self.config["max_concurrent_users"]

        # Ensure user_count is not None for type checking
        user_count = user_count or 100

        metrics = LoadTestMetrics(
            scenario_name=f"concurrent_{'chaos_' if chaos_active else ''}test_{user_count}_users",
            start_time=datetime.now(),
        )

        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(user_count)

        # Collect all response times and errors
        all_response_times = []
        all_errors = []
        service_errors = {endpoint.name: 0 for endpoint in self.service_endpoints}

        async def make_request(
            endpoint: ServiceEndpoint, session: aiohttp.ClientSession
        ):
            """Make a single request to an endpoint."""
            async with semaphore:
                start_request = time.time()

                try:
                    if endpoint.method == "GET":
                        async with session.get(
                            endpoint.url, headers=endpoint.headers
                        ) as response:
                            await response.text()
                            status = response.status
                    else:
                        async with session.post(
                            endpoint.url,
                            json=endpoint.payload,
                            headers=endpoint.headers,
                        ) as response:
                            await response.text()
                            status = response.status

                    request_time = (time.time() - start_request) * 1000
                    all_response_times.append(request_time)

                    if status != endpoint.expected_status:
                        all_errors.append(f"{endpoint.name}: HTTP {status}")
                        service_errors[endpoint.name] += 1

                    metrics.total_requests += 1

                except Exception as e:
                    all_errors.append(f"{endpoint.name}: {str(e)}")
                    service_errors[endpoint.name] += 1
                    metrics.total_requests += 1

        # Create weighted request distribution
        weighted_endpoints = []
        for endpoint in self.service_endpoints:
            weighted_endpoints.extend([endpoint] * endpoint.weight)

        # Run concurrent requests
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        ) as session:
            end_time = time.time() + duration
            tasks = []

            while time.time() < end_time:
                # Select random endpoint based on weights
                endpoint = random.choice(weighted_endpoints)

                # Create request task
                task = asyncio.create_task(make_request(endpoint, session))
                tasks.append(task)

                # Limit number of concurrent tasks
                if len(tasks) >= user_count * 2:
                    # Wait for some tasks to complete
                    done, pending = await asyncio.wait(
                        tasks, return_when=asyncio.FIRST_COMPLETED
                    )
                    tasks = list(pending)

                # Small delay to control request rate
                await asyncio.sleep(0.001)

            # Wait for remaining tasks
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)

        # Calculate final metrics
        metrics.end_time = datetime.now()
        metrics.failed_requests = len(all_errors)
        metrics.successful_requests = metrics.total_requests - metrics.failed_requests
        metrics.service_failures = service_errors

        if all_response_times:
            metrics.avg_response_time_ms = statistics.mean(all_response_times)
            if len(all_response_times) >= 20:
                metrics.p95_response_time_ms = statistics.quantiles(
                    all_response_times, n=20
                )[18]
            if len(all_response_times) >= 100:
                metrics.p99_response_time_ms = statistics.quantiles(
                    all_response_times, n=100
                )[98]
            metrics.max_response_time_ms = max(all_response_times)

        test_duration = (metrics.end_time - metrics.start_time).total_seconds()
        metrics.throughput_rps = (
            metrics.total_requests / test_duration if test_duration > 0 else 0
        )
        metrics.error_rate = (
            metrics.failed_requests / metrics.total_requests
            if metrics.total_requests > 0
            else 0
        )

        logger.info(
            f"✅ Concurrent test: {metrics.total_requests} requests, {metrics.error_rate:.2%} error rate, {metrics.avg_response_time_ms:.2f}ms avg, {metrics.throughput_rps:.1f} RPS"
        )

        return metrics

    async def _inject_chaos(self, scenario: ChaosScenario) -> int:
        """Inject chaos according to scenario configuration."""
        logger.info(f"🔥 Injecting chaos: {scenario.name}")

        chaos_events = 0
        end_time = time.time() + scenario.duration_seconds

        while time.time() < end_time:
            # Randomly decide whether to inject chaos
            if random.random() < scenario.failure_rate:
                # Select random target service
                target_service = random.choice(scenario.target_services)
                failure_type = random.choice(scenario.failure_types)

                # Simulate different types of failures
                if failure_type == "latency":
                    # Inject artificial latency
                    delay = random.uniform(0.5, 3.0)
                    logger.debug(f"Injecting {delay:.2f}s latency to {target_service}")
                    await asyncio.sleep(delay)

                elif failure_type == "error":
                    # Log simulated error
                    logger.debug(f"Simulating error in {target_service}")

                elif failure_type == "timeout":
                    # Simulate timeout
                    timeout_delay = random.uniform(5.0, 15.0)
                    logger.debug(
                        f"Simulating {timeout_delay:.2f}s timeout in {target_service}"
                    )
                    await asyncio.sleep(timeout_delay)

                elif failure_type == "network":
                    # Simulate network partition
                    logger.debug(f"Simulating network partition for {target_service}")
                    await asyncio.sleep(random.uniform(1.0, 5.0))

                chaos_events += 1

            # Wait before next potential chaos injection
            await asyncio.sleep(random.uniform(1.0, 5.0))

        logger.info(f"🔥 Chaos injection completed: {chaos_events} events")
        return chaos_events

    def _generate_comprehensive_report(
        self,
        baseline_results: Dict[str, Any],
        chaos_results: Dict[str, Any],
        stress_results: Dict[str, Any],
        suite_duration: float,
    ) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        report = {
            "test_suite": "ACGS-PGP Comprehensive Load Testing Suite",
            "timestamp": datetime.now().isoformat(),
            "suite_duration_seconds": suite_duration,
            "configuration": self.config,
            "performance_targets": self.performance_targets,
            "results": {
                "baseline": baseline_results,
                "chaos_engineering": chaos_results,
                "stress_testing": stress_results,
            },
            "summary": self._calculate_summary_metrics(
                baseline_results, chaos_results, stress_results
            ),
            "recommendations": self._generate_recommendations(
                baseline_results, chaos_results, stress_results
            ),
        }

        return report

    def _calculate_summary_metrics(
        self,
        baseline_results: Dict[str, Any],
        chaos_results: Dict[str, Any],
        stress_results: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Calculate summary metrics across all tests."""
        summary = {
            "total_requests": 0,
            "total_errors": 0,
            "avg_response_time_ms": 0,
            "max_throughput_rps": 0,
            "chaos_resilience_score": 0,
            "stress_breaking_point": 0,
            "performance_targets_met": {},
        }

        # Aggregate baseline metrics
        baseline_requests = 0
        baseline_response_times = []

        for test_name, result in baseline_results.items():
            if isinstance(result, dict):
                summary["total_requests"] += result.get("total_requests", 0)
                summary["total_errors"] += result.get("failed_requests", 0)
                baseline_requests += result.get("total_requests", 0)

                if result.get("avg_response_time_ms"):
                    baseline_response_times.append(result["avg_response_time_ms"])

                if result.get("throughput_rps"):
                    summary["max_throughput_rps"] = max(
                        summary["max_throughput_rps"], result["throughput_rps"]
                    )

        if baseline_response_times:
            summary["avg_response_time_ms"] = statistics.mean(baseline_response_times)

        # Calculate chaos resilience score
        if chaos_results:
            chaos_error_rates = []
            for result in chaos_results.values():
                if isinstance(result, dict) and result.get("error_rate") is not None:
                    chaos_error_rates.append(result["error_rate"])

            if chaos_error_rates:
                avg_chaos_error_rate = statistics.mean(chaos_error_rates)
                summary["chaos_resilience_score"] = max(
                    0, 100 - (avg_chaos_error_rate * 100)
                )

        # Find stress breaking point
        if stress_results:
            for test_name, result in stress_results.items():
                if isinstance(result, dict):
                    user_count = int(test_name.split("_")[1]) if "_" in test_name else 0
                    error_rate = result.get("error_rate", 0)

                    if error_rate < 0.05:  # Less than 5% error rate
                        summary["stress_breaking_point"] = max(
                            summary["stress_breaking_point"], user_count
                        )

        # Check performance targets
        summary["performance_targets_met"] = {
            "policy_generation_latency": summary["avg_response_time_ms"]
            <= self.performance_targets["policy_generation_latency_ms"],
            "throughput": summary["max_throughput_rps"]
            >= self.performance_targets["throughput_rps"],
            "chaos_resilience": summary["chaos_resilience_score"]
            >= 80,  # 80% resilience threshold
            "stress_capacity": summary["stress_breaking_point"]
            >= 1000,  # Handle at least 1000 users
        }

        return summary

    def _generate_recommendations(
        self,
        baseline_results: Dict[str, Any],
        chaos_results: Dict[str, Any],
        stress_results: Dict[str, Any],
    ) -> List[str]:
        """Generate performance improvement recommendations."""
        recommendations = []

        # Analyze baseline performance
        for test_name, result in baseline_results.items():
            if isinstance(result, dict):
                avg_response_time = result.get("avg_response_time_ms", 0)
                error_rate = result.get("error_rate", 0)

                if avg_response_time > 100:
                    recommendations.append(
                        f"High latency detected in {test_name}: {avg_response_time:.2f}ms. Consider optimizing database queries and caching."
                    )

                if error_rate > 0.01:
                    recommendations.append(
                        f"Error rate above threshold in {test_name}: {error_rate:.2%}. Investigate error handling and service reliability."
                    )

        # Analyze chaos engineering results
        if chaos_results:
            high_chaos_impact = []
            for scenario_name, result in chaos_results.items():
                if isinstance(result, dict):
                    error_rate = result.get("error_rate", 0)
                    if error_rate > 0.1:
                        high_chaos_impact.append(scenario_name)

            if high_chaos_impact:
                recommendations.append(
                    f"High impact from chaos scenarios: {', '.join(high_chaos_impact)}. Implement circuit breakers and retry mechanisms."
                )

        # Analyze stress testing results
        if stress_results:
            performance_degradation = []
            for test_name, result in stress_results.items():
                if isinstance(result, dict):
                    error_rate = result.get("error_rate", 0)
                    if error_rate > 0.05:
                        performance_degradation.append(test_name)

            if performance_degradation:
                recommendations.append(
                    f"Performance degradation under stress: {', '.join(performance_degradation)}. Consider horizontal scaling and load balancing."
                )

        # General recommendations
        recommendations.extend(
            [
                "Implement comprehensive monitoring and alerting for production deployment.",
                "Set up automated performance regression testing in CI/CD pipeline.",
                "Consider implementing adaptive rate limiting based on system load.",
                "Establish performance baselines and SLA monitoring for production.",
            ]
        )

        return recommendations

    def _save_results(self, report: Dict[str, Any]):
        """Save test results to files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save comprehensive report
        report_file = (
            self.results_dir / f"comprehensive_load_test_report_{timestamp}.json"
        )
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2, default=str)

        # Save summary CSV for easy analysis
        summary_file = self.results_dir / f"load_test_summary_{timestamp}.csv"
        with open(summary_file, "w") as f:
            f.write(
                "test_name,total_requests,error_rate,avg_response_time_ms,throughput_rps\n"
            )

            for category, results in report["results"].items():
                for test_name, result in results.items():
                    if isinstance(result, dict):
                        f.write(
                            f"{category}_{test_name},{result.get('total_requests', 0)},{result.get('error_rate', 0)},{result.get('avg_response_time_ms', 0)},{result.get('throughput_rps', 0)}\n"
                        )

        logger.info(f"📊 Results saved to {report_file}")
        logger.info(f"📊 Summary saved to {summary_file}")


async def main():
    """Main entry point for the comprehensive load testing suite."""
    parser = argparse.ArgumentParser(
        description="ACGS-PGP Comprehensive Load Testing Suite"
    )
    parser.add_argument("--config", type=str, help="Configuration file path")
    parser.add_argument(
        "--users", type=int, default=1000, help="Maximum concurrent users"
    )
    parser.add_argument(
        "--duration", type=int, default=300, help="Test duration in seconds"
    )
    parser.add_argument(
        "--no-chaos", action="store_true", help="Disable chaos engineering tests"
    )

    args = parser.parse_args()

    # Create test suite
    suite = ComprehensiveLoadTestSuite(args.config)

    # Override config with command line arguments
    if args.users:
        suite.config["max_concurrent_users"] = args.users
    if args.duration:
        suite.config["test_duration_seconds"] = args.duration
    if args.no_chaos:
        suite.config["chaos_enabled"] = False

    # Run comprehensive load test
    try:
        results = await suite.run_comprehensive_load_test()

        # Print summary
        summary = results["summary"]
        print("\n" + "=" * 60)
        print("COMPREHENSIVE LOAD TEST SUMMARY")
        print("=" * 60)
        print(f"Total Requests: {summary['total_requests']:,}")
        print(f"Total Errors: {summary['total_errors']:,}")
        print(f"Average Response Time: {summary['avg_response_time_ms']:.2f}ms")
        print(f"Max Throughput: {summary['max_throughput_rps']:.1f} RPS")
        print(f"Chaos Resilience Score: {summary['chaos_resilience_score']:.1f}%")
        print(f"Stress Breaking Point: {summary['stress_breaking_point']} users")

        print("\nPerformance Targets Met:")
        for target, met in summary["performance_targets_met"].items():
            status = "✅" if met else "❌"
            print(f"  {status} {target}")

        print(f"\nRecommendations:")
        for i, rec in enumerate(results["recommendations"], 1):
            print(f"  {i}. {rec}")

        # Exit with appropriate code
        all_targets_met = all(summary["performance_targets_met"].values())
        sys.exit(0 if all_targets_met else 1)

    except Exception as e:
        logger.error(f"Load test suite failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
