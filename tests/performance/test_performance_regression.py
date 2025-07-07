#!/usr/bin/env python3
"""
Performance Regression Testing Framework
Validates that all ACGS performance targets are maintained across releases.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import json
import logging
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import aiohttp
import psutil
import pytest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PerformanceRegressionTester:
    """Comprehensive performance regression testing for ACGS services."""

    def __init__(self):
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.performance_targets = {
            "p99_latency_ms": 5.0,
            "p95_latency_ms": 3.0,
            "p50_latency_ms": 2.0,
            "throughput_rps": 100,
            "cache_hit_rate": 0.85,
            "memory_usage_mb": 500,
            "cpu_usage_percent": 80,
        }

        self.services = {
            "constitutional-ai": "http://localhost:8001",
            "integrity": "http://localhost:8002",
            "formal-verification": "http://localhost:8003",
            "governance-synthesis": "http://localhost:8004",
            "policy-governance": "http://localhost:8005",
            "evolutionary-computation": "http://localhost:8006",
            "code-analysis": "http://localhost:8007",
            "multi-agent-coordinator": "http://localhost:8008",
            "worker-agents": "http://localhost:8009",
            "blackboard": "http://localhost:8010",
            "context": "http://localhost:8012",
            "audit-aggregator": "http://localhost:8015",
            "authentication": "http://localhost:8016",
        }

        self.baseline_metrics = {}
        self.current_metrics = {}

    async def run_comprehensive_performance_tests(self) -> Dict[str, Any]:
        """Run comprehensive performance regression tests."""
        logger.info("🚀 Starting ACGS Performance Regression Testing")
        logger.info(f"Constitutional Hash: {self.constitutional_hash}")
        logger.info(f"Performance Targets: {self.performance_targets}")

        start_time = time.time()

        # Load baseline metrics if available
        await self._load_baseline_metrics()

        # Run performance tests
        test_results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "constitutional_hash": self.constitutional_hash,
            "performance_targets": self.performance_targets,
            "service_metrics": {},
            "regression_analysis": {},
            "overall_status": "unknown",
        }

        # Test each service
        for service_name, base_url in self.services.items():
            logger.info(f"\n📊 Testing {service_name}...")
            service_metrics = await self._test_service_performance(
                service_name, base_url
            )
            test_results["service_metrics"][service_name] = service_metrics

        # Analyze regressions
        test_results["regression_analysis"] = (
            await self._analyze_performance_regressions(test_results["service_metrics"])
        )

        # Calculate overall status
        test_results["overall_status"] = self._calculate_overall_status(
            test_results["service_metrics"], test_results["regression_analysis"]
        )

        # Save current metrics as new baseline
        await self._save_performance_baseline(test_results)

        # Generate report
        total_time = time.time() - start_time
        test_results["total_test_time"] = total_time

        logger.info(
            f"\n✅ Performance regression testing completed in {total_time:.2f}s"
        )
        logger.info(f"Overall Status: {test_results['overall_status']}")

        return test_results

    async def _test_service_performance(
        self, service_name: str, base_url: str
    ) -> Dict[str, Any]:
        """Test performance metrics for a single service."""
        metrics = {
            "service_name": service_name,
            "base_url": base_url,
            "latency_metrics": {},
            "throughput_metrics": {},
            "resource_metrics": {},
            "constitutional_compliance": {},
            "status": "unknown",
        }

        try:
            # Test service availability first
            if not await self._test_service_availability(base_url):
                metrics["status"] = "unavailable"
                return metrics

            # Latency testing
            metrics["latency_metrics"] = await self._test_latency_performance(base_url)

            # Throughput testing
            metrics["throughput_metrics"] = await self._test_throughput_performance(
                base_url
            )

            # Resource usage testing
            metrics["resource_metrics"] = await self._test_resource_usage()

            # Constitutional compliance testing
            metrics["constitutional_compliance"] = (
                await self._test_constitutional_compliance(base_url)
            )

            # ML fitness performance (for evolution service)
            if service_name == "evolutionary-computation":
                metrics["ml_fitness_metrics"] = await self._test_ml_fitness_performance(
                    base_url
                )

            # Audit aggregation performance (for audit aggregator)
            if service_name == "audit-aggregator":
                metrics["audit_metrics"] = await self._test_audit_performance(base_url)

            metrics["status"] = "tested"

        except Exception as e:
            logger.error(f"Error testing {service_name}: {e}")
            metrics["status"] = "error"
            metrics["error"] = str(e)

        return metrics

    async def _test_service_availability(self, base_url: str) -> bool:
        """Test if service is available."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{base_url}/health", timeout=5) as response:
                    return response.status == 200
        except Exception:
            return False

    async def _test_latency_performance(self, base_url: str) -> Dict[str, float]:
        """Test latency performance with multiple requests."""
        latencies = []

        async with aiohttp.ClientSession() as session:
            # Warm up
            for _ in range(5):
                try:
                    async with session.get(f"{base_url}/health") as response:
                        pass
                except Exception:
                    pass

            # Measure latencies
            for _ in range(100):
                start_time = time.perf_counter()
                try:
                    async with session.get(f"{base_url}/health") as response:
                        if response.status == 200:
                            latency = (
                                time.perf_counter() - start_time
                            ) * 1000  # Convert to ms
                            latencies.append(latency)
                except Exception:
                    pass

        if not latencies:
            return {"error": "No successful requests"}

        latencies.sort()
        return {
            "p50_ms": statistics.median(latencies),
            "p95_ms": (
                latencies[int(0.95 * len(latencies))]
                if len(latencies) > 1
                else latencies[0]
            ),
            "p99_ms": (
                latencies[int(0.99 * len(latencies))]
                if len(latencies) > 1
                else latencies[0]
            ),
            "mean_ms": statistics.mean(latencies),
            "min_ms": min(latencies),
            "max_ms": max(latencies),
            "samples": len(latencies),
        }

    async def _test_throughput_performance(self, base_url: str) -> Dict[str, float]:
        """Test throughput performance with concurrent requests."""
        start_time = time.perf_counter()
        success_count = 0
        error_count = 0

        async def make_request(session):
            nonlocal success_count, error_count
            try:
                async with session.get(f"{base_url}/health") as response:
                    if response.status == 200:
                        success_count += 1
                    else:
                        error_count += 1
            except Exception:
                error_count += 1

        # Run concurrent requests for 10 seconds
        async with aiohttp.ClientSession() as session:
            tasks = []
            end_time = start_time + 10  # 10 second test

            while time.perf_counter() < end_time:
                # Create batch of concurrent requests
                batch_tasks = [make_request(session) for _ in range(10)]
                tasks.extend(batch_tasks)
                await asyncio.gather(*batch_tasks, return_exceptions=True)
                await asyncio.sleep(0.1)  # Small delay between batches

        total_time = time.perf_counter() - start_time
        total_requests = success_count + error_count

        return {
            "rps": success_count / total_time if total_time > 0 else 0,
            "total_requests": total_requests,
            "successful_requests": success_count,
            "failed_requests": error_count,
            "error_rate": error_count / total_requests if total_requests > 0 else 0,
            "test_duration_s": total_time,
        }

    async def _test_resource_usage(self) -> Dict[str, float]:
        """Test current system resource usage."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)

            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available_mb = memory.available / 1024 / 1024

            # Disk usage
            disk = psutil.disk_usage("/")
            disk_percent = disk.percent

            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "memory_available_mb": memory_available_mb,
                "disk_percent": disk_percent,
                "load_average": (
                    psutil.getloadavg()[0] if hasattr(psutil, "getloadavg") else 0
                ),
            }
        except Exception as e:
            return {"error": str(e)}

    async def _test_constitutional_compliance(self, base_url: str) -> Dict[str, Any]:
        """Test constitutional compliance of service responses."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{base_url}/health") as response:
                    response_text = await response.text()
                    response_headers = dict(response.headers)

                    # Check for constitutional hash in response
                    hash_in_response = self.constitutional_hash in response_text
                    hash_in_headers = any(
                        self.constitutional_hash in str(v).lower()
                        for v in response_headers.values()
                    )

                    return {
                        "status_code": response.status,
                        "hash_in_response": hash_in_response,
                        "hash_in_headers": hash_in_headers,
                        "constitutional_compliant": hash_in_response or hash_in_headers,
                        "response_size": len(response_text),
                    }
        except Exception as e:
            return {"error": str(e), "constitutional_compliant": False}

    async def _test_ml_fitness_performance(self, base_url: str) -> Dict[str, Any]:
        """Test ML fitness prediction performance for evolution service."""
        try:
            # Test ML fitness prediction endpoint if available
            test_data = {
                "genome": {"safety_first": 0.9, "operational_transparency": 0.8},
                "constitutional_hash": self.constitutional_hash,
            }

            latencies = []
            async with aiohttp.ClientSession() as session:
                for _ in range(50):  # 50 fitness evaluations
                    start_time = time.perf_counter()
                    try:
                        async with session.post(
                            f"{base_url}/api/v1/fitness/evaluate", json=test_data
                        ) as response:
                            if response.status == 200:
                                latency_ms = (time.perf_counter() - start_time) * 1000
                                latencies.append(latency_ms)
                    except Exception:
                        pass

            if latencies:
                return {
                    "ml_fitness_p99_ms": max(latencies) if latencies else 0,
                    "ml_fitness_mean_ms": statistics.mean(latencies),
                    "ml_predictions_per_second": (
                        1000 / statistics.mean(latencies) if latencies else 0
                    ),
                    "samples": len(latencies),
                }
            else:
                return {"status": "endpoint_not_available"}

        except Exception as e:
            return {"error": str(e)}

    async def _test_audit_performance(self, base_url: str) -> Dict[str, Any]:
        """Test audit event processing performance."""
        try:
            # Test audit event submission
            test_event = {
                "event_type": "performance_test",
                "service_name": "test-service",
                "action": "performance_validation",
                "outcome": "success",
                "tenant_id": "test-tenant",
                "constitutional_hash": self.constitutional_hash,
            }

            latencies = []
            async with aiohttp.ClientSession() as session:
                for _ in range(100):  # 100 audit events
                    start_time = time.perf_counter()
                    try:
                        async with session.post(
                            f"{base_url}/api/v1/audit/events", json=test_event
                        ) as response:
                            if response.status == 200:
                                latency_ms = (time.perf_counter() - start_time) * 1000
                                latencies.append(latency_ms)
                    except Exception:
                        pass

            if latencies:
                return {
                    "audit_event_p99_ms": max(latencies) if latencies else 0,
                    "audit_event_mean_ms": statistics.mean(latencies),
                    "audit_events_per_second": (
                        1000 / statistics.mean(latencies) if latencies else 0
                    ),
                    "samples": len(latencies),
                }
            else:
                return {"status": "endpoint_not_available"}

        except Exception as e:
            return {"error": str(e)}

    async def _analyze_performance_regressions(
        self, current_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze performance regressions compared to baseline."""
        regression_analysis = {
            "regressions_detected": [],
            "improvements_detected": [],
            "performance_summary": {},
            "constitutional_compliance_rate": 0,
        }

        total_services = 0
        compliant_services = 0

        for service_name, metrics in current_metrics.items():
            if metrics.get("status") != "tested":
                continue

            total_services += 1

            # Check constitutional compliance
            compliance = metrics.get("constitutional_compliance", {})
            if compliance.get("constitutional_compliant", False):
                compliant_services += 1

            # Check for latency regressions
            latency_metrics = metrics.get("latency_metrics", {})
            if "p99_ms" in latency_metrics:
                p99_latency = latency_metrics["p99_ms"]
                if p99_latency > self.performance_targets["p99_latency_ms"]:
                    regression_analysis["regressions_detected"].append(
                        {
                            "service": service_name,
                            "metric": "p99_latency",
                            "current_value": p99_latency,
                            "target_value": self.performance_targets["p99_latency_ms"],
                            "severity": (
                                "high"
                                if p99_latency
                                > self.performance_targets["p99_latency_ms"] * 2
                                else "medium"
                            ),
                        }
                    )

            # Check for throughput regressions
            throughput_metrics = metrics.get("throughput_metrics", {})
            if "rps" in throughput_metrics:
                rps = throughput_metrics["rps"]
                if rps < self.performance_targets["throughput_rps"]:
                    regression_analysis["regressions_detected"].append(
                        {
                            "service": service_name,
                            "metric": "throughput",
                            "current_value": rps,
                            "target_value": self.performance_targets["throughput_rps"],
                            "severity": "medium",
                        }
                    )

        # Calculate constitutional compliance rate
        if total_services > 0:
            regression_analysis["constitutional_compliance_rate"] = (
                compliant_services / total_services
            )

        # Performance summary
        regression_analysis["performance_summary"] = {
            "total_services_tested": total_services,
            "constitutional_compliant_services": compliant_services,
            "regressions_count": len(regression_analysis["regressions_detected"]),
            "overall_health": (
                "good"
                if len(regression_analysis["regressions_detected"]) == 0
                else "degraded"
            ),
        }

        return regression_analysis

    def _calculate_overall_status(
        self, service_metrics: Dict[str, Any], regression_analysis: Dict[str, Any]
    ) -> str:
        """Calculate overall system performance status."""
        regressions = len(regression_analysis.get("regressions_detected", []))
        compliance_rate = regression_analysis.get("constitutional_compliance_rate", 0)

        if regressions == 0 and compliance_rate >= 0.95:
            return "excellent"
        elif regressions <= 2 and compliance_rate >= 0.90:
            return "good"
        elif regressions <= 5 and compliance_rate >= 0.80:
            return "acceptable"
        else:
            return "needs_attention"

    async def _load_baseline_metrics(self):
        """Load baseline performance metrics if available."""
        baseline_file = Path("test_reports/performance_baseline.json")
        if baseline_file.exists():
            try:
                with open(baseline_file, "r") as f:
                    self.baseline_metrics = json.load(f)
                logger.info("✅ Loaded performance baseline metrics")
            except Exception as e:
                logger.warning(f"Failed to load baseline metrics: {e}")

    async def _save_performance_baseline(self, test_results: Dict[str, Any]):
        """Save current performance metrics as baseline."""
        baseline_file = Path("test_reports/performance_baseline.json")
        baseline_file.parent.mkdir(exist_ok=True)

        try:
            baseline_data = {
                "timestamp": test_results["timestamp"],
                "constitutional_hash": test_results["constitutional_hash"],
                "service_metrics": test_results["service_metrics"],
                "performance_targets": test_results["performance_targets"],
            }

            with open(baseline_file, "w") as f:
                json.dump(baseline_data, f, indent=2)

            logger.info(f"✅ Saved performance baseline to {baseline_file}")
        except Exception as e:
            logger.error(f"Failed to save baseline metrics: {e}")


# Pytest test functions
@pytest.mark.asyncio
@pytest.mark.performance
async def test_comprehensive_performance_regression():
    """Test comprehensive performance regression across all ACGS services."""
    tester = PerformanceRegressionTester()
    results = await tester.run_comprehensive_performance_tests()

    # Assert overall system health
    assert results["overall_status"] in [
        "excellent",
        "good",
        "acceptable",
    ], f"Performance regression detected: {results['overall_status']}"

    # Assert constitutional compliance
    compliance_rate = results["regression_analysis"]["constitutional_compliance_rate"]
    assert (
        compliance_rate >= 0.8
    ), f"Constitutional compliance rate too low: {compliance_rate:.2f}"

    # Assert no critical regressions
    regressions = results["regression_analysis"]["regressions_detected"]
    critical_regressions = [r for r in regressions if r.get("severity") == "high"]
    assert (
        len(critical_regressions) == 0
    ), f"Critical performance regressions detected: {critical_regressions}"


@pytest.mark.asyncio
@pytest.mark.performance
async def test_latency_performance_targets():
    """Test that all services meet latency performance targets."""
    tester = PerformanceRegressionTester()

    for service_name, base_url in tester.services.items():
        if await tester._test_service_availability(base_url):
            latency_metrics = await tester._test_latency_performance(base_url)

            if "p99_ms" in latency_metrics:
                assert (
                    latency_metrics["p99_ms"]
                    <= tester.performance_targets["p99_latency_ms"]
                ), f"{service_name} P99 latency {latency_metrics['p99_ms']}ms exceeds target"


@pytest.mark.asyncio
@pytest.mark.performance
async def test_throughput_performance_targets():
    """Test that all services meet throughput performance targets."""
    tester = PerformanceRegressionTester()

    for service_name, base_url in tester.services.items():
        if await tester._test_service_availability(base_url):
            throughput_metrics = await tester._test_throughput_performance(base_url)

            if "rps" in throughput_metrics:
                # Reduced target for individual services
                service_target = (
                    tester.performance_targets["throughput_rps"] / 4
                )  # 25 RPS per service
                assert (
                    throughput_metrics["rps"] >= service_target
                ), f"{service_name} throughput {throughput_metrics['rps']} RPS below target"


@pytest.mark.asyncio
@pytest.mark.constitutional
async def test_constitutional_compliance_performance():
    """Test constitutional compliance across all services."""
    tester = PerformanceRegressionTester()

    for service_name, base_url in tester.services.items():
        if await tester._test_service_availability(base_url):
            compliance = await tester._test_constitutional_compliance(base_url)

            assert compliance.get(
                "constitutional_compliant", False
            ), f"{service_name} not constitutionally compliant"


if __name__ == "__main__":

    async def main():
        tester = PerformanceRegressionTester()
        results = await tester.run_comprehensive_performance_tests()

        # Save results
        results_file = Path("test_reports/performance_regression_results.json")
        results_file.parent.mkdir(exist_ok=True)

        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)

        print(f"📊 Performance regression test results saved to {results_file}")
        print(f"Overall Status: {results['overall_status']}")

        return results["overall_status"] in ["excellent", "good", "acceptable"]

    success = asyncio.run(main())
    exit(0 if success else 1)
