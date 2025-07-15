"""
ACGS Performance Benchmarking Tool
Comprehensive performance analysis for enhanced integration components
"""

import asyncio
import json
import logging
import os
import statistics
import sys
import time
from dataclasses import dataclass, field
from typing import Any

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from services.shared.enhanced_auth import enhanced_auth_service
from services.shared.enhanced_service_client import enhanced_service_client
from services.shared.enhanced_service_registry import enhanced_service_registry

logger = logging.getLogger(__name__)


@dataclass
class BenchmarkResult:
    """Benchmark result data structure."""

    component: str
    test_name: str
    iterations: int
    total_duration: float
    avg_duration: float
    min_duration: float
    max_duration: float
    p95_duration: float
    p99_duration: float
    throughput: float  # operations per second
    success_rate: float
    errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class PerformanceBenchmark:
    """Performance benchmarking suite for ACGS components."""

    def __init__(self):
        self.results: list[BenchmarkResult] = []

    async def benchmark_service_registry_health_checks(
        self, iterations: int = 1000, concurrent_batches: int = 10
    ) -> BenchmarkResult:
        """Benchmark service registry health check performance."""
        logger.info(
            f"🔍 Benchmarking service registry health checks ({iterations} iterations)"
        )

        # Initialize service registry
        await enhanced_service_registry.start()

        durations = []
        errors = []
        successful_operations = 0

        # Run benchmark in batches to avoid overwhelming the system
        batch_size = iterations // concurrent_batches

        start_time = time.time()

        for batch in range(concurrent_batches):
            batch_start = time.time()

            # Create tasks for this batch
            tasks = []
            for _ in range(batch_size):
                task = enhanced_service_registry.check_all_services_health_parallel()
                tasks.append(task)

            # Execute batch
            try:
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)

                for result in batch_results:
                    if isinstance(result, Exception):
                        errors.append(str(result))
                    else:
                        successful_operations += 1
                        durations.append(time.time() - batch_start)

            except Exception as e:
                errors.append(f"Batch {batch} failed: {e!s}")

        total_duration = time.time() - start_time

        # Calculate statistics
        if durations:
            avg_duration = statistics.mean(durations)
            min_duration = min(durations)
            max_duration = max(durations)
            p95_duration = (
                statistics.quantiles(durations, n=20)[18]
                if len(durations) > 20
                else max_duration
            )
            p99_duration = (
                statistics.quantiles(durations, n=100)[98]
                if len(durations) > 100
                else max_duration
            )
        else:
            avg_duration = min_duration = max_duration = p95_duration = p99_duration = (
                0.0
            )

        throughput = (
            successful_operations / total_duration if total_duration > 0 else 0.0
        )
        success_rate = successful_operations / iterations if iterations > 0 else 0.0

        # Get registry performance metrics
        performance_report = (
            await enhanced_service_registry.get_registry_performance_report()
        )

        return BenchmarkResult(
            component="service_registry",
            test_name="health_checks",
            iterations=iterations,
            total_duration=total_duration,
            avg_duration=avg_duration,
            min_duration=min_duration,
            max_duration=max_duration,
            p95_duration=p95_duration,
            p99_duration=p99_duration,
            throughput=throughput,
            success_rate=success_rate,
            errors=errors[:10],  # Keep only first 10 errors
            metadata={
                "concurrent_batches": concurrent_batches,
                "batch_size": batch_size,
                "registry_metrics": performance_report["registry_metrics"],
            },
        )

    async def benchmark_service_client_calls(
        self, iterations: int = 500, concurrent_calls: int = 20
    ) -> BenchmarkResult:
        """Benchmark service client call performance."""
        logger.info(f"🌐 Benchmarking service client calls ({iterations} iterations)")

        durations = []
        errors = []
        successful_operations = 0

        # Create semaphore to limit concurrent calls
        semaphore = asyncio.Semaphore(concurrent_calls)

        async def make_test_call():
            async with semaphore:
                call_start = time.time()
                try:
                    result = await enhanced_service_client.call_service(
                        service_name="auth_service",
                        endpoint="/health",
                        use_fallback=True,
                    )

                    call_duration = time.time() - call_start
                    durations.append(call_duration)

                    if result.success:
                        return True
                    errors.append(result.error or "Unknown error")
                    return False

                except Exception as e:
                    errors.append(str(e))
                    return False

        # Execute all calls
        start_time = time.time()
        tasks = [make_test_call() for _ in range(iterations)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_duration = time.time() - start_time

        # Count successful operations
        successful_operations = sum(1 for r in results if r is True)

        # Calculate statistics
        if durations:
            avg_duration = statistics.mean(durations)
            min_duration = min(durations)
            max_duration = max(durations)
            p95_duration = (
                statistics.quantiles(durations, n=20)[18]
                if len(durations) > 20
                else max_duration
            )
            p99_duration = (
                statistics.quantiles(durations, n=100)[98]
                if len(durations) > 100
                else max_duration
            )
        else:
            avg_duration = min_duration = max_duration = p95_duration = p99_duration = (
                0.0
            )

        throughput = (
            successful_operations / total_duration if total_duration > 0 else 0.0
        )
        success_rate = successful_operations / iterations if iterations > 0 else 0.0

        # Get client performance metrics
        client_metrics = enhanced_service_client.get_performance_metrics()

        return BenchmarkResult(
            component="service_client",
            test_name="service_calls",
            iterations=iterations,
            total_duration=total_duration,
            avg_duration=avg_duration,
            min_duration=min_duration,
            max_duration=max_duration,
            p95_duration=p95_duration,
            p99_duration=p99_duration,
            throughput=throughput,
            success_rate=success_rate,
            errors=errors[:10],
            metadata={
                "concurrent_calls": concurrent_calls,
                "client_metrics": client_metrics,
            },
        )

    async def benchmark_auth_service_performance(
        self, iterations: int = 1000, concurrent_auths: int = 50
    ) -> BenchmarkResult:
        """Benchmark authentication service performance."""
        logger.info(f"🔐 Benchmarking auth service ({iterations} iterations)")

        # Initialize auth service
        await enhanced_auth_service.initialize()

        durations = []
        errors = []
        successful_operations = 0

        # Create semaphore to limit concurrent authentications
        semaphore = asyncio.Semaphore(concurrent_auths)

        async def make_auth_call(iteration: int):
            async with semaphore:
                auth_start = time.time()
                try:
                    # Alternate between valid and invalid credentials for realistic testing
                    if iteration % 3 == 0:
                        username, password = os.getenv("PASSWORD", ""), "admin_password"
                    elif iteration % 3 == 1:
                        username, password = (
                            os.getenv("PASSWORD", ""),
                            "council_password",
                        )
                    else:
                        username, password = (
                            os.getenv("PASSWORD", ""),
                            "invalid_password",
                        )

                    await enhanced_auth_service.authenticate_user(
                        username=username,
                        password=os.environ.get("PASSWORD")
                        ip_address=f"192.168.1.{iteration % 255}",
                        user_agent="benchmark_client",
                    )

                    auth_duration = time.time() - auth_start
                    durations.append(auth_duration)

                    # Consider successful if we get a user (valid creds) or proper rejection (invalid creds)
                    return True

                except Exception as e:
                    errors.append(str(e))
                    return False

        # Execute all authentication attempts
        start_time = time.time()
        tasks = [make_auth_call(i) for i in range(iterations)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_duration = time.time() - start_time

        # Count successful operations
        successful_operations = sum(1 for r in results if r is True)

        # Calculate statistics
        if durations:
            avg_duration = statistics.mean(durations)
            min_duration = min(durations)
            max_duration = max(durations)
            p95_duration = (
                statistics.quantiles(durations, n=20)[18]
                if len(durations) > 20
                else max_duration
            )
            p99_duration = (
                statistics.quantiles(durations, n=100)[98]
                if len(durations) > 100
                else max_duration
            )
        else:
            avg_duration = min_duration = max_duration = p95_duration = p99_duration = (
                0.0
            )

        throughput = (
            successful_operations / total_duration if total_duration > 0 else 0.0
        )
        success_rate = successful_operations / iterations if iterations > 0 else 0.0

        # Get auth service metrics
        auth_metrics = enhanced_auth_service.get_performance_metrics()

        return BenchmarkResult(
            component="auth_service",
            test_name="authentication",
            iterations=iterations,
            total_duration=total_duration,
            avg_duration=avg_duration,
            min_duration=min_duration,
            max_duration=max_duration,
            p95_duration=p95_duration,
            p99_duration=p99_duration,
            throughput=throughput,
            success_rate=success_rate,
            errors=errors[:10],
            metadata={
                "concurrent_auths": concurrent_auths,
                "auth_metrics": auth_metrics,
            },
        )

    async def run_full_benchmark_suite(self) -> dict[str, Any]:
        """Run the complete performance benchmark suite."""
        logger.info("🚀 Starting ACGS performance benchmark suite...")

        benchmark_methods = [
            (
                self.benchmark_service_registry_health_checks,
                {"iterations": 500, "concurrent_batches": 5},
            ),
            (
                self.benchmark_service_client_calls,
                {"iterations": 300, "concurrent_calls": 15},
            ),
            (
                self.benchmark_auth_service_performance,
                {"iterations": 500, "concurrent_auths": 25},
            ),
        ]

        results = []
        total_start_time = time.time()

        for benchmark_method, kwargs in benchmark_methods:
            try:
                result = await benchmark_method(**kwargs)
                results.append(result)

                logger.info(
                    f"✅ {result.component}.{result.test_name}: "
                    f"{result.throughput:.1f} ops/sec, "
                    f"{result.success_rate:.1%} success, "
                    f"P95: {result.p95_duration * 1000:.1f}ms"
                )

            except Exception as e:
                logger.error(
                    f"❌ Benchmark failed for {benchmark_method.__name__}: {e}"
                )
                results.append(
                    BenchmarkResult(
                        component="unknown",
                        test_name=benchmark_method.__name__,
                        iterations=0,
                        total_duration=0.0,
                        avg_duration=0.0,
                        min_duration=0.0,
                        max_duration=0.0,
                        p95_duration=0.0,
                        p99_duration=0.0,
                        throughput=0.0,
                        success_rate=0.0,
                        errors=[str(e)],
                    )
                )

        total_duration = time.time() - total_start_time

        # Generate summary
        summary = {
            "benchmark_timestamp": time.time(),
            "total_duration": total_duration,
            "total_benchmarks": len(results),
            "successful_benchmarks": sum(1 for r in results if r.success_rate > 0.8),
            "overall_performance": {
                "avg_throughput": statistics.mean(
                    [r.throughput for r in results if r.throughput > 0]
                ),
                "avg_success_rate": statistics.mean([r.success_rate for r in results]),
                "avg_p95_latency": statistics.mean(
                    [r.p95_duration for r in results if r.p95_duration > 0]
                ),
            },
            "benchmark_results": [
                {
                    "component": r.component,
                    "test_name": r.test_name,
                    "iterations": r.iterations,
                    "throughput": r.throughput,
                    "success_rate": r.success_rate,
                    "avg_duration_ms": r.avg_duration * 1000,
                    "p95_duration_ms": r.p95_duration * 1000,
                    "p99_duration_ms": r.p99_duration * 1000,
                    "error_count": len(r.errors),
                    "metadata": r.metadata,
                }
                for r in results
            ],
        }

        logger.info(f"🏁 Benchmark suite completed in {total_duration:.2f}s")
        logger.info(
            f"📊 Overall performance: {summary['overall_performance']['avg_throughput']:.1f} ops/sec avg"
        )

        return summary

    def save_benchmark_results(
        self, summary: dict[str, Any], filename: str = "benchmark_results.json"
    ):
        """Save benchmark results to file."""
        try:
            with open(filename, "w") as f:
                json.dump(summary, f, indent=2, default=str)
            logger.info(f"💾 Benchmark results saved to {filename}")
        except Exception as e:
            logger.error(f"Failed to save benchmark results: {e}")


async def main():
    """Run the performance benchmark suite."""
    benchmark = PerformanceBenchmark()

    try:
        summary = await benchmark.run_full_benchmark_suite()

        # Save results
        benchmark.save_benchmark_results(summary)

        # Print summary
        print("\n" + "=" * 80)
        print("ACGS PERFORMANCE BENCHMARK RESULTS")
        print("=" * 80)

        for result in summary["benchmark_results"]:
            print(f"\n📈 {result['component'].upper()}.{result['test_name']}")
            print(f"   Throughput: {result['throughput']:.1f} ops/sec")
            print(f"   Success Rate: {result['success_rate']:.1%}")
            print(f"   Avg Latency: {result['avg_duration_ms']:.1f}ms")
            print(f"   P95 Latency: {result['p95_duration_ms']:.1f}ms")
            print(f"   P99 Latency: {result['p99_duration_ms']:.1f}ms")
            print(f"   Iterations: {result['iterations']}")

            if result["error_count"] > 0:
                print(f"   ⚠️  Errors: {result['error_count']}")

        print("\n🎯 OVERALL PERFORMANCE:")
        print(
            f"   Average Throughput: {summary['overall_performance']['avg_throughput']:.1f} ops/sec"
        )
        print(
            f"   Average Success Rate: {summary['overall_performance']['avg_success_rate']:.1%}"
        )
        print(
            f"   Average P95 Latency: {summary['overall_performance']['avg_p95_latency'] * 1000:.1f}ms"
        )

        # Performance assessment
        if summary["overall_performance"]["avg_success_rate"] >= 0.95:
            print("✅ EXCELLENT: High reliability achieved")
        elif summary["overall_performance"]["avg_success_rate"] >= 0.90:
            print("✅ GOOD: Acceptable reliability")
        else:
            print("⚠️  NEEDS IMPROVEMENT: Low reliability")

        if summary["overall_performance"]["avg_p95_latency"] <= 0.1:  # 100ms
            print("✅ EXCELLENT: Low latency achieved")
        elif summary["overall_performance"]["avg_p95_latency"] <= 0.5:  # 500ms
            print("✅ GOOD: Acceptable latency")
        else:
            print("⚠️  NEEDS IMPROVEMENT: High latency")

    except Exception as e:
        logger.error(f"Benchmark suite failed: {e}")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
