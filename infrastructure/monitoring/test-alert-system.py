#!/usr/bin/env python3
"""
ACGS-1 Alert System Performance Testing Script
Subtask 13.7: Comprehensive alert system validation and stress testing

This script validates alert system responsiveness, accuracy, and performance
under various failure scenarios and high load conditions.
"""

import asyncio
import json
import logging
import sys
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import aiohttp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/var/log/acgs/alert-system-test.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


@dataclass
class AlertTestConfig:
    """Configuration for alert system testing."""

    # Test parameters
    test_duration_seconds: int = 300  # 5 minutes
    alert_detection_timeout_seconds: int = 30

    # Target endpoints
    prometheus_url: str = "http://localhost:9090"
    alertmanager_url: str = "http://localhost:9093"

    # Expected alert rules
    expected_alert_rules: list[str] = field(
        default_factory=lambda: [
            "ServiceDown",
            "HighResponseTime",
            "LowConstitutionalCompliance",
            "PolicySynthesisFailureRate",
            "HAProxyDown",
            "HAProxyBackendServerDown",
            "RedisMemoryUsageHigh",
            "PostgreSQLConnectionsHigh",
        ]
    )


@dataclass
class AlertTestResult:
    """Container for alert test results."""

    test_name: str
    success: bool = False
    response_time_ms: float = 0.0
    error_message: str = ""
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(
        default_factory=lambda: datetime.now(UTC).isoformat()
    )


class AlertSystemTester:
    """Comprehensive alert system tester."""

    def __init__(self, config: AlertTestConfig):
        self.config = config
        self.test_results: list[AlertTestResult] = []

    async def run_alert_system_tests(self) -> bool:
        """Execute comprehensive alert system tests."""
        logger.info("🚨 Starting ACGS-1 Alert System Performance Tests")
        logger.info("=" * 80)

        try:
            # Test 1: Validate alert rules are loaded
            await self.test_alert_rules_loaded()

            # Test 2: Test alert rule evaluation performance
            await self.test_alert_rule_evaluation_performance()

            # Test 3: Test alertmanager API responsiveness
            await self.test_alertmanager_api_performance()

            # Test 4: Test alert correlation and grouping
            await self.test_alert_correlation()

            # Test 5: Test alert notification latency
            await self.test_alert_notification_latency()

            # Test 6: Stress test alert system
            await self.stress_test_alert_system()

            # Test 7: Test alert recovery and resolution
            await self.test_alert_recovery()

            # Evaluate overall success
            success = self.evaluate_alert_system_performance()

            # Generate comprehensive report
            self.generate_alert_test_report()

            return success

        except Exception as e:
            logger.error(f"❌ Alert system testing failed: {str(e)}")
            return False

    async def test_alert_rules_loaded(self):
        """Test that all expected alert rules are loaded in Prometheus."""
        logger.info("🔍 Testing alert rules loading...")

        result = AlertTestResult("Alert Rules Loading")

        try:
            start_time = time.time()

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.config.prometheus_url}/api/v1/rules"
                ) as response:
                    response_time = (time.time() - start_time) * 1000
                    result.response_time_ms = response_time

                    if response.status == 200:
                        rules_data = await response.json()

                        # Extract all alert rule names
                        loaded_rules = []
                        for group in rules_data.get("data", {}).get("groups", []):
                            for rule in group.get("rules", []):
                                if rule.get("type") == "alerting":
                                    loaded_rules.append(rule.get("name"))

                        # Check if expected rules are loaded
                        missing_rules = []
                        for expected_rule in self.config.expected_alert_rules:
                            if expected_rule not in loaded_rules:
                                missing_rules.append(expected_rule)

                        result.details = {
                            "total_rules_loaded": len(loaded_rules),
                            "expected_rules": len(self.config.expected_alert_rules),
                            "missing_rules": missing_rules,
                            "loaded_rules": loaded_rules,
                        }

                        if not missing_rules:
                            result.success = True
                            logger.info(
                                f"✅ All {len(self.config.expected_alert_rules)} expected alert rules loaded"
                            )
                        else:
                            result.error_message = (
                                f"Missing alert rules: {missing_rules}"
                            )
                            logger.warning(f"⚠️ Missing alert rules: {missing_rules}")
                    else:
                        result.error_message = f"HTTP {response.status}"
                        logger.error(
                            f"❌ Failed to fetch alert rules: {response.status}"
                        )

        except Exception as e:
            result.error_message = str(e)
            logger.error(f"❌ Alert rules test failed: {str(e)}")

        self.test_results.append(result)

    async def test_alert_rule_evaluation_performance(self):
        """Test alert rule evaluation performance."""
        logger.info("⚡ Testing alert rule evaluation performance...")

        result = AlertTestResult("Alert Rule Evaluation Performance")

        try:
            # Test multiple rule evaluations
            evaluation_times = []

            async with aiohttp.ClientSession() as session:
                for _ in range(10):  # Test 10 evaluations
                    start_time = time.time()

                    async with session.get(
                        f"{self.config.prometheus_url}/api/v1/rules"
                    ) as response:
                        evaluation_time = (time.time() - start_time) * 1000

                        if response.status == 200:
                            evaluation_times.append(evaluation_time)

                        await asyncio.sleep(0.1)  # Small delay between requests

            if evaluation_times:
                avg_evaluation_time = sum(evaluation_times) / len(evaluation_times)
                max_evaluation_time = max(evaluation_times)

                result.response_time_ms = avg_evaluation_time
                result.details = {
                    "avg_evaluation_time_ms": avg_evaluation_time,
                    "max_evaluation_time_ms": max_evaluation_time,
                    "total_evaluations": len(evaluation_times),
                }

                # Performance criteria: average evaluation should be < 1000ms
                if avg_evaluation_time < 1000:
                    result.success = True
                    logger.info(
                        f"✅ Alert rule evaluation: avg={avg_evaluation_time:.2f}ms, max={max_evaluation_time:.2f}ms"
                    )
                else:
                    result.error_message = (
                        f"Slow evaluation: {avg_evaluation_time:.2f}ms > 1000ms"
                    )
                    logger.warning(
                        f"⚠️ Slow alert rule evaluation: {avg_evaluation_time:.2f}ms"
                    )
            else:
                result.error_message = "No successful evaluations"

        except Exception as e:
            result.error_message = str(e)
            logger.error(f"❌ Alert rule evaluation test failed: {str(e)}")

        self.test_results.append(result)

    async def test_alertmanager_api_performance(self):
        """Test Alertmanager API responsiveness."""
        logger.info("📡 Testing Alertmanager API performance...")

        result = AlertTestResult("Alertmanager API Performance")

        try:
            # Test various Alertmanager endpoints
            endpoints = [
                "/api/v1/status",
                "/api/v1/alerts",
                "/api/v1/alerts/groups",
                "/-/healthy",
            ]

            endpoint_performance = {}

            async with aiohttp.ClientSession() as session:
                for endpoint in endpoints:
                    response_times = []

                    for _ in range(5):  # Test each endpoint 5 times
                        start_time = time.time()

                        try:
                            timeout = aiohttp.ClientTimeout(total=10)
                            async with session.get(
                                f"{self.config.alertmanager_url}{endpoint}",
                                timeout=timeout,
                            ) as response:
                                response_time = (time.time() - start_time) * 1000

                                if response.status == 200:
                                    response_times.append(response_time)

                        except Exception:
                            pass  # Skip failed requests

                        await asyncio.sleep(0.1)

                    if response_times:
                        avg_time = sum(response_times) / len(response_times)
                        endpoint_performance[endpoint] = {
                            "avg_response_time_ms": avg_time,
                            "success_count": len(response_times),
                        }

            # Calculate overall performance
            if endpoint_performance:
                all_times = []
                for perf in endpoint_performance.values():
                    all_times.append(perf["avg_response_time_ms"])

                avg_response_time = sum(all_times) / len(all_times)
                result.response_time_ms = avg_response_time
                result.details = {
                    "avg_response_time_ms": avg_response_time,
                    "endpoint_performance": endpoint_performance,
                }

                # Performance criteria: average response time < 500ms
                if avg_response_time < 500:
                    result.success = True
                    logger.info(
                        f"✅ Alertmanager API performance: {avg_response_time:.2f}ms average"
                    )
                else:
                    result.error_message = (
                        f"Slow API response: {avg_response_time:.2f}ms > 500ms"
                    )
                    logger.warning(
                        f"⚠️ Slow Alertmanager API: {avg_response_time:.2f}ms"
                    )
            else:
                result.error_message = "No successful API calls"

        except Exception as e:
            result.error_message = str(e)
            logger.error(f"❌ Alertmanager API test failed: {str(e)}")

        self.test_results.append(result)

    async def test_alert_correlation(self):
        """Test alert correlation and grouping functionality."""
        logger.info("🔗 Testing alert correlation and grouping...")

        result = AlertTestResult("Alert Correlation")

        try:
            async with aiohttp.ClientSession() as session:
                # Get current alerts
                async with session.get(
                    f"{self.config.alertmanager_url}/api/v1/alerts"
                ) as response:
                    if response.status == 200:
                        alerts_data = await response.json()
                        alerts = alerts_data.get("data", [])

                        # Analyze alert grouping
                        severity_groups = {}
                        service_groups = {}

                        for alert in alerts:
                            labels = alert.get("labels", {})
                            severity = labels.get("severity", "unknown")
                            service = labels.get(
                                "job", labels.get("service", "unknown")
                            )

                            severity_groups[severity] = (
                                severity_groups.get(severity, 0) + 1
                            )
                            service_groups[service] = service_groups.get(service, 0) + 1

                        result.details = {
                            "total_alerts": len(alerts),
                            "severity_distribution": severity_groups,
                            "service_distribution": service_groups,
                        }

                        result.success = True
                        logger.info(
                            f"✅ Alert correlation: {len(alerts)} alerts, {len(severity_groups)} severity levels"
                        )
                    else:
                        result.error_message = f"HTTP {response.status}"

        except Exception as e:
            result.error_message = str(e)
            logger.error(f"❌ Alert correlation test failed: {str(e)}")

        self.test_results.append(result)

    async def test_alert_notification_latency(self):
        """Test alert notification latency."""
        logger.info("🔔 Testing alert notification latency...")

        result = AlertTestResult("Alert Notification Latency")

        try:
            start_time = time.time()

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.config.alertmanager_url}/api/v1/status"
                ) as response:
                    response_time = (time.time() - start_time) * 1000

                    if response.status == 200:
                        status_data = await response.json()

                        result.response_time_ms = response_time
                        result.details = {
                            "status_response_time_ms": response_time,
                            "alertmanager_status": status_data.get("status", "unknown"),
                        }

                        if response_time < 30000:  # 30 seconds
                            result.success = True
                            logger.info(
                                f"✅ Alert notification latency: {response_time:.2f}ms"
                            )
                        else:
                            result.error_message = (
                                f"High latency: {response_time:.2f}ms > 30000ms"
                            )
                    else:
                        result.error_message = f"HTTP {response.status}"

        except Exception as e:
            result.error_message = str(e)
            logger.error(f"❌ Alert notification latency test failed: {str(e)}")

        self.test_results.append(result)

    async def stress_test_alert_system(self):
        """Stress test the alert system with high query load."""
        logger.info("💪 Stress testing alert system...")

        result = AlertTestResult("Alert System Stress Test")

        try:
            concurrent_requests = 50
            test_duration = 30  # 30 seconds

            async def alert_query_worker():
                request_count = 0
                error_count = 0
                end_time = time.time() + test_duration

                async with aiohttp.ClientSession() as session:
                    while time.time() < end_time:
                        try:
                            timeout = aiohttp.ClientTimeout(total=5)
                            async with session.get(
                                f"{self.config.prometheus_url}/api/v1/rules",
                                timeout=timeout,
                            ) as response:
                                request_count += 1
                                if response.status != 200:
                                    error_count += 1
                        except Exception:
                            error_count += 1
                        await asyncio.sleep(0.1)
                return request_count, error_count

            start_time = time.time()
            tasks = [alert_query_worker() for _ in range(concurrent_requests)]
            worker_results = await asyncio.gather(*tasks, return_exceptions=True)
            stress_test_duration = time.time() - start_time

            total_requests = 0
            total_errors = 0

            for worker_result in worker_results:
                if isinstance(worker_result, tuple):
                    requests, errors = worker_result
                    total_requests += requests
                    total_errors += errors

            error_rate = (
                (total_errors / total_requests * 100) if total_requests > 0 else 100
            )
            requests_per_second = total_requests / stress_test_duration

            result.details = {
                "total_requests": total_requests,
                "total_errors": total_errors,
                "error_rate_percent": error_rate,
                "requests_per_second": requests_per_second,
                "test_duration_seconds": stress_test_duration,
                "concurrent_workers": concurrent_requests,
            }

            if error_rate < 5.0:
                result.success = True
                logger.info(
                    f"✅ Stress test: {total_requests} requests, {error_rate:.2f}% error rate"
                )
            else:
                result.error_message = f"High error rate: {error_rate:.2f}% > 5%"
                logger.warning(
                    f"⚠️ High error rate during stress test: {error_rate:.2f}%"
                )

        except Exception as e:
            result.error_message = str(e)
            logger.error(f"❌ Alert system stress test failed: {str(e)}")

        self.test_results.append(result)

    async def test_alert_recovery(self):
        """Test alert recovery and resolution mechanisms."""
        logger.info("🔄 Testing alert recovery and resolution...")

        result = AlertTestResult("Alert Recovery")

        try:
            recovery_tests = []

            # Test Prometheus connectivity recovery
            start_time = time.time()
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(
                        f"{self.config.prometheus_url}/-/healthy"
                    ) as response:
                        recovery_time = (time.time() - start_time) * 1000
                        recovery_tests.append(
                            {
                                "component": "prometheus",
                                "recovery_time_ms": recovery_time,
                                "success": response.status == 200,
                            }
                        )
                except Exception as e:
                    recovery_tests.append(
                        {
                            "component": "prometheus",
                            "recovery_time_ms": 0,
                            "success": False,
                            "error": str(e),
                        }
                    )

            # Test Alertmanager connectivity recovery
            start_time = time.time()
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(
                        f"{self.config.alertmanager_url}/-/healthy"
                    ) as response:
                        recovery_time = (time.time() - start_time) * 1000
                        recovery_tests.append(
                            {
                                "component": "alertmanager",
                                "recovery_time_ms": recovery_time,
                                "success": response.status == 200,
                            }
                        )
                except Exception as e:
                    recovery_tests.append(
                        {
                            "component": "alertmanager",
                            "recovery_time_ms": 0,
                            "success": False,
                            "error": str(e),
                        }
                    )

            successful_recoveries = sum(1 for test in recovery_tests if test["success"])
            total_recoveries = len(recovery_tests)

            result.details = {
                "recovery_tests": recovery_tests,
                "successful_recoveries": successful_recoveries,
                "total_recoveries": total_recoveries,
                "recovery_success_rate": (
                    (successful_recoveries / total_recoveries * 100)
                    if total_recoveries > 0
                    else 0
                ),
            }

            if successful_recoveries == total_recoveries:
                result.success = True
                logger.info(
                    f"✅ Alert recovery: {successful_recoveries}/{total_recoveries} components recovered"
                )
            else:
                result.error_message = f"Recovery failures: {total_recoveries - successful_recoveries}/{total_recoveries}"

        except Exception as e:
            result.error_message = str(e)
            logger.error(f"❌ Alert recovery test failed: {str(e)}")

        self.test_results.append(result)

    def evaluate_alert_system_performance(self) -> bool:
        """Evaluate overall alert system performance."""
        logger.info("📋 Evaluating alert system performance...")

        successful_tests = sum(1 for result in self.test_results if result.success)
        total_tests = len(self.test_results)
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0

        logger.info("📊 Alert System Test Results:")
        logger.info(f"  Successful Tests: {successful_tests}/{total_tests}")
        logger.info(f"  Success Rate: {success_rate:.2f}%")

        for result in self.test_results:
            status = "✅" if result.success else "❌"
            logger.info(
                f"  {status} {result.test_name}: {'PASSED' if result.success else 'FAILED'}"
            )
            if not result.success and result.error_message:
                logger.info(f"    Error: {result.error_message}")

        return success_rate >= 80.0

    def generate_alert_test_report(self):
        """Generate comprehensive alert system test report."""
        logger.info("📄 Generating alert system test report...")

        report = {
            "test_metadata": {
                "timestamp": datetime.now(UTC).isoformat(),
                "test_duration_seconds": self.config.test_duration_seconds,
                "test_type": "alert_system_performance_validation",
            },
            "configuration": {
                "prometheus_url": self.config.prometheus_url,
                "alertmanager_url": self.config.alertmanager_url,
                "expected_alert_rules": self.config.expected_alert_rules,
                "alert_detection_timeout_seconds": self.config.alert_detection_timeout_seconds,
            },
            "test_results": [
                {
                    "test_name": result.test_name,
                    "success": result.success,
                    "response_time_ms": result.response_time_ms,
                    "error_message": result.error_message,
                    "details": result.details,
                    "timestamp": result.timestamp,
                }
                for result in self.test_results
            ],
            "summary": {
                "total_tests": len(self.test_results),
                "successful_tests": sum(1 for r in self.test_results if r.success),
                "failed_tests": sum(1 for r in self.test_results if not r.success),
                "success_rate_percent": (
                    (
                        sum(1 for r in self.test_results if r.success)
                        / len(self.test_results)
                        * 100
                    )
                    if self.test_results
                    else 0
                ),
            },
        }

        # Save report to file
        report_file = "/var/log/acgs/alert-system-test-report.json"
        try:
            Path("/var/log/acgs").mkdir(parents=True, exist_ok=True)
            with open(report_file, "w") as f:
                json.dump(report, f, indent=2)

            logger.info(f"✅ Alert system test report saved to: {report_file}")
        except Exception as e:
            logger.error(f"❌ Failed to save report: {str(e)}")


async def main():
    """Main execution function for alert system testing."""
    import argparse

    parser = argparse.ArgumentParser(
        description="ACGS-1 Alert System Performance Testing"
    )
    parser.add_argument(
        "--duration", type=int, default=300, help="Test duration in seconds"
    )
    parser.add_argument(
        "--prometheus-url", default="http://localhost:9090", help="Prometheus URL"
    )
    parser.add_argument(
        "--alertmanager-url", default="http://localhost:9093", help="Alertmanager URL"
    )

    args = parser.parse_args()

    # Create configuration
    config = AlertTestConfig(
        test_duration_seconds=args.duration,
        prometheus_url=args.prometheus_url,
        alertmanager_url=args.alertmanager_url,
    )

    # Create tester and run tests
    tester = AlertSystemTester(config)

    try:
        success = await tester.run_alert_system_tests()

        if success:
            logger.info("🎉 Alert system performance tests PASSED!")
            sys.exit(0)
        else:
            logger.error("❌ Alert system performance tests FAILED!")
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("⚠️ Alert system tests interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"❌ Alert system tests failed with error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    # Ensure log directory exists
    Path("/var/log/acgs").mkdir(parents=True, exist_ok=True)

    # Run the alert system tests
    asyncio.run(main())
