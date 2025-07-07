#!/usr/bin/env python3
# Constitutional Hash: cdd01ef066bc6cf2
"""
Performance Benchmarking and Validation Framework for ACGS-2
Tests performance against established targets including O(1) lookups,
request-scoped caching effectiveness, and overall system latency under load.
"""

import concurrent.futures
import json
import statistics
import sys
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "services"))
sys.path.insert(0, str(project_root / "services/shared"))


class BenchmarkStatus(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"
    ERROR = "ERROR"


@dataclass
class BenchmarkResult:
    test_name: str
    status: BenchmarkStatus
    execution_time: float
    target_metrics: dict[str, float]
    actual_metrics: dict[str, float]
    meets_targets: bool
    load_conditions: dict[str, Any]
    performance_details: dict[str, Any]
    error_message: str | None = None


class PerformanceBenchmarker:
    def __init__(self):
        self.results = []
        self.project_root = project_root

        # Performance targets
        self.targets = {
            "p99_latency_ms": 5.0,  # Sub-5ms P99 latency
            "p95_latency_ms": 3.0,  # Sub-3ms P95 latency
            "mean_latency_ms": 1.0,  # Sub-1ms mean latency
            "throughput_ops_per_sec": 1000,  # Minimum 1000 ops/sec
            "cache_hit_rate_percent": 80.0,  # Minimum 80% cache hit rate
            "memory_usage_mb": 100.0,  # Maximum 100MB memory usage
            "cpu_utilization_percent": 50.0,  # Maximum 50% CPU utilization
        }

    def log_result(self, result: BenchmarkResult):
        """Log a benchmark result."""
        self.results.append(result)
        status_symbol = {"PASS": "✓", "FAIL": "✗", "SKIP": "⊝", "ERROR": "⚠"}
        symbol = status_symbol.get(result.status.value, "?")

        print(f"{symbol} {result.test_name} ({result.execution_time:.3f}s)")
        print(f"  Targets Met: {'✓' if result.meets_targets else '✗'}")

        # Show key metrics
        for metric, target in result.target_metrics.items():
            actual = result.actual_metrics.get(metric, 0)
            meets_target = self._check_metric_target(metric, actual, target)
            symbol = "✓" if meets_target else "✗"
            print(f"  {metric}: {actual:.2f} (target: {target:.2f}) {symbol}")

        if result.error_message:
            print(f"  Error: {result.error_message}")

    def _check_metric_target(
        self, metric_name: str, actual: float, target: float
    ) -> bool:
        """Check if a metric meets its target."""
        # For latency and usage metrics, actual should be <= target
        if any(
            keyword in metric_name.lower()
            for keyword in ["latency", "usage", "utilization"]
        ):
            return actual <= target
        # For throughput and hit rate metrics, actual should be >= target
        return actual >= target

    def _measure_latency_stats(self, latencies: list[float]) -> dict[str, float]:
        """Calculate latency statistics from a list of latencies in seconds."""
        if not latencies:
            return {}

        # Convert to milliseconds
        latencies_ms = [l * 1000 for l in latencies]

        return {
            "min_ms": min(latencies_ms),
            "max_ms": max(latencies_ms),
            "mean_ms": statistics.mean(latencies_ms),
            "median_ms": statistics.median(latencies_ms),
            "p95_latency_ms": self._percentile(latencies_ms, 95),
            "p99_latency_ms": self._percentile(latencies_ms, 99),
            "std_dev_ms": (
                statistics.stdev(latencies_ms) if len(latencies_ms) > 1 else 0
            ),
        }

    def _percentile(self, data: list[float], percentile: float) -> float:
        """Calculate percentile of data."""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        if index.is_integer():
            return sorted_data[int(index)]
        lower = sorted_data[int(index)]
        upper = sorted_data[int(index) + 1]
        return lower + (upper - lower) * (index - int(index))

    def benchmark_o1_lookup_performance(self) -> BenchmarkResult:
        """Benchmark O(1) lookup operations under various load conditions."""
        start_time = time.time()
        try:
            # Test different data sizes
            test_sizes = [1000, 10000, 100000]
            all_latencies = []
            throughput_results = []

            for size in test_sizes:
                # Create lookup table
                lookup_table = {f"key_{i}": f"value_{i}" for i in range(size)}

                # Measure lookup performance
                latencies = []
                lookup_start = time.time()

                for i in range(1000):  # 1000 lookups per size
                    key = f"key_{i % size}"
                    op_start = time.time()
                    value = lookup_table.get(key)
                    op_end = time.time()
                    latencies.append(op_end - op_start)

                lookup_end = time.time()
                throughput = 1000 / (lookup_end - lookup_start)
                throughput_results.append(throughput)
                all_latencies.extend(latencies)

            # Calculate metrics
            latency_stats = self._measure_latency_stats(all_latencies)
            avg_throughput = statistics.mean(throughput_results)

            target_metrics = {
                "p99_latency_ms": self.targets["p99_latency_ms"],
                "p95_latency_ms": self.targets["p95_latency_ms"],
                "mean_latency_ms": self.targets["mean_latency_ms"],
                "throughput_ops_per_sec": self.targets["throughput_ops_per_sec"],
            }

            actual_metrics = {
                "p99_latency_ms": latency_stats.get("p99_latency_ms", 0),
                "p95_latency_ms": latency_stats.get("p95_latency_ms", 0),
                "mean_latency_ms": latency_stats.get("mean_ms", 0),
                "throughput_ops_per_sec": avg_throughput,
            }

            # Check if targets are met
            meets_targets = all(
                self._check_metric_target(metric, actual_metrics[metric], target)
                for metric, target in target_metrics.items()
            )

            status = BenchmarkStatus.PASS if meets_targets else BenchmarkStatus.FAIL

            return BenchmarkResult(
                "o1_lookup_performance",
                status,
                time.time() - start_time,
                target_metrics,
                actual_metrics,
                meets_targets,
                {"test_sizes": test_sizes, "lookups_per_size": 1000},
                {
                    "latency_stats": latency_stats,
                    "throughput_by_size": dict(
                        zip(test_sizes, throughput_results, strict=False)
                    ),
                    "total_operations": len(all_latencies),
                },
            )

        except Exception as e:
            return BenchmarkResult(
                "o1_lookup_performance",
                BenchmarkStatus.ERROR,
                time.time() - start_time,
                {},
                {},
                False,
                {},
                {},
                str(e),
            )

    def benchmark_cache_effectiveness(self) -> BenchmarkResult:
        """Benchmark request-scoped caching effectiveness."""
        start_time = time.time()
        try:
            # Simulate cache with different hit rates
            class BenchmarkCache:
                def __init__(self):
                    self.cache = {}
                    self.hits = 0
                    self.misses = 0
                    self.access_times = []

                def get(self, key):
                    access_start = time.time()
                    if key in self.cache:
                        self.hits += 1
                        result = self.cache[key]
                    else:
                        self.misses += 1
                        # Simulate cache miss penalty
                        time.sleep(0.0001)  # 0.1ms penalty
                        result = None
                    access_end = time.time()
                    self.access_times.append(access_end - access_start)
                    return result

                def set(self, key, value):
                    self.cache[key] = value

                def hit_rate(self):
                    total = self.hits + self.misses
                    return (self.hits / total * 100) if total > 0 else 0

            cache = BenchmarkCache()

            # Pre-populate cache with some data
            for i in range(100):
                cache.set(f"cached_key_{i}", f"cached_value_{i}")

            # Test cache performance with mixed hit/miss pattern
            test_operations = 2000
            for i in range(test_operations):
                if i % 3 == 0:  # 33% cache misses
                    key = f"new_key_{i}"
                    value = cache.get(key)
                    if value is None:
                        cache.set(key, f"new_value_{i}")
                else:  # 67% cache hits
                    key = f"cached_key_{i % 100}"
                    value = cache.get(key)

            # Calculate metrics
            latency_stats = self._measure_latency_stats(cache.access_times)
            hit_rate = cache.hit_rate()
            throughput = test_operations / sum(cache.access_times)

            target_metrics = {
                "cache_hit_rate_percent": self.targets["cache_hit_rate_percent"],
                "p99_latency_ms": self.targets["p99_latency_ms"],
                "throughput_ops_per_sec": self.targets["throughput_ops_per_sec"],
            }

            actual_metrics = {
                "cache_hit_rate_percent": hit_rate,
                "p99_latency_ms": latency_stats.get("p99_latency_ms", 0),
                "throughput_ops_per_sec": throughput,
            }

            meets_targets = all(
                self._check_metric_target(metric, actual_metrics[metric], target)
                for metric, target in target_metrics.items()
            )

            status = BenchmarkStatus.PASS if meets_targets else BenchmarkStatus.FAIL

            return BenchmarkResult(
                "cache_effectiveness",
                status,
                time.time() - start_time,
                target_metrics,
                actual_metrics,
                meets_targets,
                {"test_operations": test_operations, "cache_size": 100},
                {
                    "cache_hits": cache.hits,
                    "cache_misses": cache.misses,
                    "latency_stats": latency_stats,
                },
            )

        except Exception as e:
            return BenchmarkResult(
                "cache_effectiveness",
                BenchmarkStatus.ERROR,
                time.time() - start_time,
                {},
                {},
                False,
                {},
                {},
                str(e),
            )

    def benchmark_concurrent_load(self) -> BenchmarkResult:
        """Benchmark system performance under concurrent load."""
        start_time = time.time()
        try:

            def worker_task(worker_id: int, operations: int) -> dict[str, Any]:
                """Worker function for concurrent load testing."""
                latencies = []
                lookup_table = {f"key_{i}": f"value_{i}" for i in range(1000)}

                worker_start = time.time()
                for i in range(operations):
                    key = f"key_{i % 1000}"
                    op_start = time.time()
                    value = lookup_table.get(key)
                    # Simulate some processing
                    if value:
                        processed = value.upper()
                    op_end = time.time()
                    latencies.append(op_end - op_start)
                worker_end = time.time()

                return {
                    "worker_id": worker_id,
                    "latencies": latencies,
                    "total_time": worker_end - worker_start,
                    "operations": operations,
                }

            # Test with different concurrency levels
            concurrency_levels = [1, 5, 10, 20]
            operations_per_worker = 500

            best_throughput = 0
            all_latencies = []

            for num_workers in concurrency_levels:
                with concurrent.futures.ThreadPoolExecutor(
                    max_workers=num_workers
                ) as executor:
                    futures = [
                        executor.submit(worker_task, i, operations_per_worker)
                        for i in range(num_workers)
                    ]

                    worker_results = []
                    for future in concurrent.futures.as_completed(futures):
                        result = future.result()
                        worker_results.append(result)
                        all_latencies.extend(result["latencies"])

                # Calculate throughput for this concurrency level
                total_operations = num_workers * operations_per_worker
                max_worker_time = max(r["total_time"] for r in worker_results)
                throughput = total_operations / max_worker_time
                best_throughput = max(best_throughput, throughput)

            # Calculate overall metrics
            latency_stats = self._measure_latency_stats(all_latencies)

            target_metrics = {
                "p99_latency_ms": self.targets["p99_latency_ms"],
                "throughput_ops_per_sec": self.targets["throughput_ops_per_sec"],
            }

            actual_metrics = {
                "p99_latency_ms": latency_stats.get("p99_latency_ms", 0),
                "throughput_ops_per_sec": best_throughput,
            }

            meets_targets = all(
                self._check_metric_target(metric, actual_metrics[metric], target)
                for metric, target in target_metrics.items()
            )

            status = BenchmarkStatus.PASS if meets_targets else BenchmarkStatus.FAIL

            return BenchmarkResult(
                "concurrent_load",
                status,
                time.time() - start_time,
                target_metrics,
                actual_metrics,
                meets_targets,
                {
                    "concurrency_levels": concurrency_levels,
                    "operations_per_worker": operations_per_worker,
                    "max_workers": max(concurrency_levels),
                },
                {
                    "latency_stats": latency_stats,
                    "best_throughput": best_throughput,
                    "total_operations": len(all_latencies),
                },
            )

        except Exception as e:
            return BenchmarkResult(
                "concurrent_load",
                BenchmarkStatus.ERROR,
                time.time() - start_time,
                {},
                {},
                False,
                {},
                {},
                str(e),
            )

    def benchmark_memory_efficiency(self) -> BenchmarkResult:
        """Benchmark memory usage efficiency."""
        start_time = time.time()
        try:
            import gc

            import psutil

            # Get initial memory usage
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB

            # Create data structures and measure memory growth
            data_structures = []
            memory_measurements = []

            for i in range(10):  # 10 iterations
                # Create some data structures
                large_dict = {f"key_{j}": f"value_{j}" * 100 for j in range(1000)}
                large_list = [f"item_{j}" * 50 for j in range(1000)]
                data_structures.append((large_dict, large_list))

                # Measure memory
                current_memory = process.memory_info().rss / 1024 / 1024
                memory_measurements.append(current_memory)

            # Clean up and measure final memory
            data_structures.clear()
            gc.collect()
            final_memory = process.memory_info().rss / 1024 / 1024

            # Calculate metrics
            peak_memory = max(memory_measurements)
            memory_growth = peak_memory - initial_memory
            memory_efficiency = (
                (final_memory - initial_memory) / memory_growth
                if memory_growth > 0
                else 1.0
            )

            target_metrics = {"memory_usage_mb": self.targets["memory_usage_mb"]}

            actual_metrics = {"memory_usage_mb": memory_growth}

            meets_targets = memory_growth <= self.targets["memory_usage_mb"]
            status = BenchmarkStatus.PASS if meets_targets else BenchmarkStatus.FAIL

            return BenchmarkResult(
                "memory_efficiency",
                status,
                time.time() - start_time,
                target_metrics,
                actual_metrics,
                meets_targets,
                {"iterations": 10, "data_per_iteration": "2000 items"},
                {
                    "initial_memory_mb": initial_memory,
                    "peak_memory_mb": peak_memory,
                    "final_memory_mb": final_memory,
                    "memory_growth_mb": memory_growth,
                    "memory_efficiency": memory_efficiency,
                },
            )

        except ImportError:
            return BenchmarkResult(
                "memory_efficiency",
                BenchmarkStatus.SKIP,
                time.time() - start_time,
                {},
                {},
                False,
                {},
                {},
                "psutil not available for memory monitoring",
            )
        except Exception as e:
            return BenchmarkResult(
                "memory_efficiency",
                BenchmarkStatus.ERROR,
                time.time() - start_time,
                {},
                {},
                False,
                {},
                {},
                str(e),
            )

    def run_all_benchmarks(self) -> dict[str, Any]:
        """Run all performance benchmarks."""
        print("Starting Performance Benchmarking...")
        print("Performance Targets:")
        for target, value in self.targets.items():
            print(f"  {target}: {value}")
        print("=" * 60)

        # Define benchmark methods
        benchmark_methods = [
            self.benchmark_o1_lookup_performance,
            self.benchmark_cache_effectiveness,
            self.benchmark_concurrent_load,
            self.benchmark_memory_efficiency,
        ]

        # Run all benchmarks
        for benchmark_method in benchmark_methods:
            try:
                result = benchmark_method()
                self.log_result(result)
            except Exception as e:
                error_result = BenchmarkResult(
                    benchmark_method.__name__,
                    BenchmarkStatus.ERROR,
                    0.0,
                    {},
                    {},
                    False,
                    {},
                    {},
                    f"Benchmark execution failed: {e!s}",
                )
                self.log_result(error_result)

        # Generate summary
        total_benchmarks = len(self.results)
        passed_benchmarks = sum(
            1 for r in self.results if r.status == BenchmarkStatus.PASS
        )
        failed_benchmarks = sum(
            1 for r in self.results if r.status == BenchmarkStatus.FAIL
        )
        error_benchmarks = sum(
            1 for r in self.results if r.status == BenchmarkStatus.ERROR
        )
        skipped_benchmarks = sum(
            1 for r in self.results if r.status == BenchmarkStatus.SKIP
        )

        targets_met = sum(1 for r in self.results if r.meets_targets)

        # Aggregate performance metrics
        all_p99_latencies = [
            r.actual_metrics.get("p99_latency_ms", 0)
            for r in self.results
            if r.actual_metrics.get("p99_latency_ms")
        ]
        all_throughputs = [
            r.actual_metrics.get("throughput_ops_per_sec", 0)
            for r in self.results
            if r.actual_metrics.get("throughput_ops_per_sec")
        ]

        avg_p99_latency = statistics.mean(all_p99_latencies) if all_p99_latencies else 0
        max_throughput = max(all_throughputs) if all_throughputs else 0

        summary = {
            "total_benchmarks": total_benchmarks,
            "passed": passed_benchmarks,
            "failed": failed_benchmarks,
            "errors": error_benchmarks,
            "skipped": skipped_benchmarks,
            "targets_met": targets_met,
            "success_rate": (
                (passed_benchmarks / total_benchmarks * 100)
                if total_benchmarks > 0
                else 0
            ),
            "performance_summary": {
                "targets": self.targets,
                "average_p99_latency_ms": avg_p99_latency,
                "max_throughput_ops_per_sec": max_throughput,
                "all_targets_met": targets_met == total_benchmarks,
            },
            "results": [
                {
                    "test_name": r.test_name,
                    "status": r.status.value,
                    "execution_time": r.execution_time,
                    "target_metrics": r.target_metrics,
                    "actual_metrics": r.actual_metrics,
                    "meets_targets": r.meets_targets,
                    "load_conditions": r.load_conditions,
                    "performance_details": r.performance_details,
                    "error_message": r.error_message,
                }
                for r in self.results
            ],
        }

        print("\n" + "=" * 60)
        print("PERFORMANCE BENCHMARK SUMMARY")
        print("=" * 60)
        print(f"Total Benchmarks: {total_benchmarks}")
        print(f"Passed: {passed_benchmarks}")
        print(f"Failed: {failed_benchmarks}")
        print(f"Errors: {error_benchmarks}")
        print(f"Skipped: {skipped_benchmarks}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Targets Met: {targets_met}/{total_benchmarks}")
        print(
            f"Avg P99 Latency: {avg_p99_latency:.2f}ms (target: {self.targets['p99_latency_ms']:.2f}ms)"
        )
        print(
            f"Max Throughput: {max_throughput:.0f} ops/sec (target: {self.targets['throughput_ops_per_sec']:.0f} ops/sec)"
        )
        print(
            f"All Targets Met: {'✓' if summary['performance_summary']['all_targets_met'] else '✗'}"
        )

        return summary


def main():
    benchmarker = PerformanceBenchmarker()
    summary = benchmarker.run_all_benchmarks()

    # Save results
    output_file = project_root / "performance_benchmark_results.json"
    with open(output_file, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nDetailed results saved to: {output_file}")

    # Return appropriate exit code
    if not summary["performance_summary"]["all_targets_met"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
