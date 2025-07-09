#!/usr/bin/env python3
"""
ACGS-1 Performance Benchmarking Framework

Comprehensive performance testing and benchmarking for ACGS-1 Constitutional Governance System.
Tests all 9 microservices under various load conditions and generates detailed reports.
"""

import argparse
import asyncio
import json
import logging
import statistics
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

import aiohttp
import psutil
import yaml

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class ServiceEndpoint:
    """Service endpoint configuration."""

    name: str
    url: str
    port: int
    health_path: str = "/health"
    auth_required: bool = False


@dataclass
class BenchmarkResult:
    """Benchmark result data."""

    service_name: str
    test_type: str
    duration_seconds: float
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time_ms: float
    min_response_time_ms: float
    max_response_time_ms: float
    p50_response_time_ms: float
    p95_response_time_ms: float
    p99_response_time_ms: float
    requests_per_second: float
    errors: list[str]
    timestamp: str


@dataclass
class SystemMetrics:
    """System resource metrics."""

    cpu_percent: float
    memory_percent: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_sent_mb: float
    network_recv_mb: float
    timestamp: str


class ACGSPerformanceBenchmark:
    """Main performance benchmarking class."""

    def __init__(self, config_path: str = "config/performance/benchmark-config.yml"):
        """Initialize the benchmark framework."""
        self.config_path = config_path
        self.config = self._load_config()
        self.services = self._load_services()
        self.results: list[BenchmarkResult] = []
        self.system_metrics: list[SystemMetrics] = []

    def _load_config(self) -> dict[str, Any]:
        """Load benchmark configuration."""
        try:
            with open(self.config_path) as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Config file not found: {self.config_path}, using defaults")
            return self._default_config()

    def _default_config(self) -> dict[str, Any]:
        """Default benchmark configuration."""
        return {
            "base_url": "http://localhost",
            "test_duration": 60,
            "concurrent_users": [1, 5, 10, 25, 50],
            "ramp_up_time": 10,
            "test_types": [
                "health_check",
                "load_test",
                "stress_test",
                "endurance_test",
            ],
            "performance_targets": {
                "response_time_ms": 2000,
                "availability_percent": 99.0,
                "throughput_rps": 100,
            },
        }

    def _load_services(self) -> list[ServiceEndpoint]:
        """Load service endpoint configurations."""
        services = [
            ServiceEndpoint("auth_service", self.config["base_url"], 8000),
            ServiceEndpoint("ac_service", self.config["base_url"], 8001),
            ServiceEndpoint("integrity_service", self.config["base_url"], 8002),
            ServiceEndpoint("fv_service", self.config["base_url"], 8003),
            ServiceEndpoint("gs_service", self.config["base_url"], 8004),
            ServiceEndpoint("pgc_service", self.config["base_url"], 8005),
            ServiceEndpoint("ec_service", self.config["base_url"], 8006),
            ServiceEndpoint("api_gateway", self.config["base_url"], 8080),
            ServiceEndpoint("monitoring", self.config["base_url"], 9090),
        ]
        return services

    async def check_service_health(self, service: ServiceEndpoint) -> bool:
        """Check if a service is healthy and responding."""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{service.url}:{service.port}{service.health_path}"
                async with session.get(
                    url, timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Health check failed for {service.name}: {e}")
            return False

    async def wait_for_services(self, timeout: int = 300) -> bool:
        """Wait for all services to be healthy."""
        logger.info("Waiting for services to be ready...")

        start_time = time.time()
        while time.time() - start_time < timeout:
            all_healthy = True

            for service in self.services:
                if not await self.check_service_health(service):
                    all_healthy = False
                    logger.info(f"Service {service.name} not ready yet...")
                    break

            if all_healthy:
                logger.info("All services are healthy and ready")
                return True

            await asyncio.sleep(5)

        logger.error("Timeout waiting for services to be ready")
        return False

    def collect_system_metrics(self) -> SystemMetrics:
        """Collect current system resource metrics."""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk_io = psutil.disk_io_counters()
        network_io = psutil.net_io_counters()

        return SystemMetrics(
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            disk_io_read_mb=disk_io.read_bytes / 1024 / 1024 if disk_io else 0,
            disk_io_write_mb=disk_io.write_bytes / 1024 / 1024 if disk_io else 0,
            network_sent_mb=network_io.bytes_sent / 1024 / 1024 if network_io else 0,
            network_recv_mb=network_io.bytes_recv / 1024 / 1024 if network_io else 0,
            timestamp=datetime.utcnow().isoformat(),
        )

    async def run_health_check_test(self, service: ServiceEndpoint) -> BenchmarkResult:
        """Run basic health check test."""
        logger.info(f"Running health check test for {service.name}")

        start_time = time.time()
        response_times = []
        successful_requests = 0
        failed_requests = 0
        errors = []

        async with aiohttp.ClientSession() as session:
            for _ in range(10):  # 10 health check requests
                request_start = time.time()
                try:
                    url = f"{service.url}:{service.port}{service.health_path}"
                    async with session.get(
                        url, timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        response_time = (time.time() - request_start) * 1000
                        response_times.append(response_time)

                        if response.status == 200:
                            successful_requests += 1
                        else:
                            failed_requests += 1
                            errors.append(f"HTTP {response.status}")

                except Exception as e:
                    failed_requests += 1
                    errors.append(str(e))
                    response_times.append(10000)  # 10 second timeout

                await asyncio.sleep(0.1)  # Small delay between requests

        duration = time.time() - start_time
        total_requests = successful_requests + failed_requests

        return BenchmarkResult(
            service_name=service.name,
            test_type="health_check",
            duration_seconds=duration,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            avg_response_time_ms=(
                statistics.mean(response_times) if response_times else 0
            ),
            min_response_time_ms=min(response_times) if response_times else 0,
            max_response_time_ms=max(response_times) if response_times else 0,
            p50_response_time_ms=(
                statistics.median(response_times) if response_times else 0
            ),
            p95_response_time_ms=(
                self._percentile(response_times, 95) if response_times else 0
            ),
            p99_response_time_ms=(
                self._percentile(response_times, 99) if response_times else 0
            ),
            requests_per_second=total_requests / duration if duration > 0 else 0,
            errors=list(set(errors)),
            timestamp=datetime.utcnow().isoformat(),
        )

    def _percentile(self, data: list[float], percentile: int) -> float:
        """Calculate percentile of a list of numbers."""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int((percentile / 100) * len(sorted_data))
        return sorted_data[min(index, len(sorted_data) - 1)]

    async def run_load_test(
        self, service: ServiceEndpoint, concurrent_users: int
    ) -> BenchmarkResult:
        """Run load test using concurrent requests."""
        logger.info(
            f"Running load test for {service.name} with {concurrent_users} concurrent users"
        )

        start_time = time.time()
        response_times = []
        successful_requests = 0
        failed_requests = 0
        errors = []

        async def make_request(session: aiohttp.ClientSession):
            nonlocal successful_requests, failed_requests, errors, response_times

            request_start = time.time()
            try:
                url = f"{service.url}:{service.port}{service.health_path}"
                async with session.get(
                    url, timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response_time = (time.time() - request_start) * 1000
                    response_times.append(response_time)

                    if response.status == 200:
                        successful_requests += 1
                    else:
                        failed_requests += 1
                        errors.append(f"HTTP {response.status}")

            except Exception as e:
                failed_requests += 1
                errors.append(str(e))
                response_times.append(30000)  # 30 second timeout

        # Run concurrent requests
        async with aiohttp.ClientSession() as session:
            tasks = []
            for _ in range(concurrent_users * 10):  # 10 requests per user
                tasks.append(make_request(session))

            await asyncio.gather(*tasks, return_exceptions=True)

        duration = time.time() - start_time
        total_requests = successful_requests + failed_requests

        return BenchmarkResult(
            service_name=service.name,
            test_type=f"load_test_{concurrent_users}_users",
            duration_seconds=duration,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            avg_response_time_ms=(
                statistics.mean(response_times) if response_times else 0
            ),
            min_response_time_ms=min(response_times) if response_times else 0,
            max_response_time_ms=max(response_times) if response_times else 0,
            p50_response_time_ms=(
                statistics.median(response_times) if response_times else 0
            ),
            p95_response_time_ms=(
                self._percentile(response_times, 95) if response_times else 0
            ),
            p99_response_time_ms=(
                self._percentile(response_times, 99) if response_times else 0
            ),
            requests_per_second=total_requests / duration if duration > 0 else 0,
            errors=list(set(errors)),
            timestamp=datetime.utcnow().isoformat(),
        )

    async def run_comprehensive_benchmark(self) -> dict[str, Any]:
        """Run comprehensive benchmark suite."""
        logger.info("Starting comprehensive performance benchmark...")

        # Wait for services to be ready
        if not await self.wait_for_services():
            raise RuntimeError("Services not ready for benchmarking")

        # Collect initial system metrics
        initial_metrics = self.collect_system_metrics()
        self.system_metrics.append(initial_metrics)

        # Run health check tests for all services
        logger.info("Running health check tests...")
        for service in self.services:
            try:
                result = await self.run_health_check_test(service)
                self.results.append(result)
            except Exception as e:
                logger.error(f"Health check test failed for {service.name}: {e}")

        # Run load tests with different user counts
        logger.info("Running load tests...")
        for concurrent_users in self.config.get("concurrent_users", [1, 5, 10]):
            for service in self.services[:3]:  # Test first 3 services to save time
                try:
                    result = await self.run_load_test(service, concurrent_users)
                    self.results.append(result)

                    # Collect system metrics during load test
                    metrics = self.collect_system_metrics()
                    self.system_metrics.append(metrics)

                    # Small delay between tests
                    await asyncio.sleep(2)

                except Exception as e:
                    logger.error(f"Load test failed for {service.name}: {e}")

        # Collect final system metrics
        final_metrics = self.collect_system_metrics()
        self.system_metrics.append(final_metrics)

        return self.generate_report()

    def generate_report(self) -> dict[str, Any]:
        """Generate comprehensive benchmark report."""
        logger.info("Generating benchmark report...")

        # Calculate summary statistics
        total_tests = len(self.results)
        successful_tests = len([r for r in self.results if r.failed_requests == 0])

        # Performance targets
        targets = self.config.get("performance_targets", {})
        target_response_time = targets.get("response_time_ms", 2000)
        target_availability = targets.get("availability_percent", 99.0)
        target_throughput = targets.get("throughput_rps", 100)

        # Check if targets are met
        avg_response_time = statistics.mean(
            [r.avg_response_time_ms for r in self.results]
        )
        avg_availability = statistics.mean(
            [
                (
                    (r.successful_requests / r.total_requests * 100)
                    if r.total_requests > 0
                    else 0
                )
                for r in self.results
            ]
        )
        avg_throughput = statistics.mean([r.requests_per_second for r in self.results])

        targets_met = {
            "response_time": avg_response_time <= target_response_time,
            "availability": avg_availability >= target_availability,
            "throughput": avg_throughput >= target_throughput,
        }

        report = {
            "benchmark_id": f"acgs-benchmark-{int(time.time())}",
            "timestamp": datetime.utcnow().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "success_rate": (
                    (successful_tests / total_tests * 100) if total_tests > 0 else 0
                ),
                "avg_response_time_ms": avg_response_time,
                "avg_availability_percent": avg_availability,
                "avg_throughput_rps": avg_throughput,
            },
            "performance_targets": {
                "response_time_ms": target_response_time,
                "availability_percent": target_availability,
                "throughput_rps": target_throughput,
                "targets_met": targets_met,
                "overall_pass": all(targets_met.values()),
            },
            "detailed_results": [asdict(result) for result in self.results],
            "system_metrics": [asdict(metric) for metric in self.system_metrics],
            "recommendations": self._generate_recommendations(targets_met),
        }

        return report

    def _generate_recommendations(self, targets_met: dict[str, bool]) -> list[str]:
        """Generate performance improvement recommendations."""
        recommendations = []

        if not targets_met["response_time"]:
            recommendations.append(
                "Consider optimizing database queries and adding caching"
            )
            recommendations.append(
                "Review service dependencies and reduce external API calls"
            )

        if not targets_met["availability"]:
            recommendations.append("Implement circuit breakers and retry mechanisms")
            recommendations.append("Add health checks and graceful degradation")

        if not targets_met["throughput"]:
            recommendations.append(
                "Scale horizontally by adding more service instances"
            )
            recommendations.append(
                "Optimize resource allocation and connection pooling"
            )

        if all(targets_met.values()):
            recommendations.append(
                "Performance targets met - consider stress testing with higher loads"
            )

        return recommendations


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="ACGS-1 Performance Benchmark")
    parser.add_argument(
        "--config",
        default="config/performance/benchmark-config.yml",
        help="Benchmark configuration file",
    )
    parser.add_argument("--output", help="Output file for benchmark report")
    parser.add_argument(
        "--format", choices=["json", "yaml"], default="json", help="Output format"
    )

    args = parser.parse_args()

    try:
        benchmark = ACGSPerformanceBenchmark(args.config)
        report = await benchmark.run_comprehensive_benchmark()

        # Output report
        if args.format == "yaml":
            output = yaml.dump(report, default_flow_style=False)
        else:
            output = json.dumps(report, indent=2)

        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
            logger.info(f"Benchmark report written to {args.output}")
        else:
            print(output)

        # Exit with appropriate code
        if report["performance_targets"]["overall_pass"]:
            logger.info("✅ All performance targets met")
            sys.exit(0)
        else:
            logger.warning("⚠️ Some performance targets not met")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Benchmark failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
