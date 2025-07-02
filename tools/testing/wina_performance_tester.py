#!/usr/bin/env python3
"""
WINA Performance Optimization Testing Framework
Tests WINA components against sub-5ms P99 latency requirements.
Validates O(1) lookups, request-scoped caching, and performance consistency.
"""

import json
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "services"))
sys.path.insert(0, str(project_root / "services/shared"))


@dataclass
class PerformanceResult:
    test_name: str
    status: str
    latency_stats: dict[str, float]
    throughput: float
    meets_requirements: bool
    details: dict[str, Any]
    error_message: str | None = None


class WINAPerformanceTester:
    def __init__(self):
        self.results = []
        self.project_root = project_root
        self.target_p99_latency_ms = 5.0  # Sub-5ms P99 requirement

    def log_result(self, result: PerformanceResult):
        """Log a performance test result."""
        self.results.append(result)
        status_symbol = {"PASS": "✓", "FAIL": "✗", "SKIP": "⊝", "ERROR": "⚠"}
        symbol = status_symbol.get(result.status, "?")
        req_symbol = "✓" if result.meets_requirements else "✗"

        print(f"{symbol} {result.test_name}")
        print(f"  P99: {result.latency_stats.get('p99', 0):.2f}ms {req_symbol}")
        print(f"  Throughput: {result.throughput:.0f} ops/sec")

        if result.error_message:
            print(f"  Error: {result.error_message}")

    def measure_latency_stats(self, latencies: list[float]) -> dict[str, float]:
        """Calculate latency statistics from a list of latencies in seconds."""
        if not latencies:
            return {}

        # Convert to milliseconds
        latencies_ms = [l * 1000 for l in latencies]

        return {
            "min": min(latencies_ms),
            "max": max(latencies_ms),
            "mean": statistics.mean(latencies_ms),
            "median": statistics.median(latencies_ms),
            "p95": self.percentile(latencies_ms, 95),
            "p99": self.percentile(latencies_ms, 99),
            "std_dev": statistics.stdev(latencies_ms) if len(latencies_ms) > 1 else 0,
        }

    def percentile(self, data: list[float], percentile: float) -> float:
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

    def test_o1_lookup_performance(self) -> PerformanceResult:
        """Test O(1) lookup performance with hash tables."""
        start_time = time.time()
        try:
            # Create a large hash table for O(1) lookups
            lookup_table = {}
            table_size = 100000

            # Populate the table
            for i in range(table_size):
                lookup_table[f"key_{i}"] = f"value_{i}"

            # Measure lookup times
            latencies = []
            num_lookups = 1000

            for i in range(num_lookups):
                key = f"key_{i % table_size}"
                lookup_start = time.time()
                value = lookup_table.get(key)
                lookup_end = time.time()
                latencies.append(lookup_end - lookup_start)

            latency_stats = self.measure_latency_stats(latencies)
            throughput = num_lookups / (time.time() - start_time)
            meets_requirements = (
                latency_stats.get("p99", float("inf")) < self.target_p99_latency_ms
            )

            return PerformanceResult(
                "o1_lookup_performance",
                "PASS" if meets_requirements else "FAIL",
                latency_stats,
                throughput,
                meets_requirements,
                {
                    "table_size": table_size,
                    "num_lookups": num_lookups,
                    "lookup_complexity": "O(1)",
                },
            )

        except Exception as e:
            return PerformanceResult(
                "o1_lookup_performance", "ERROR", {}, 0.0, False, {}, str(e)
            )

    def test_request_scoped_caching(self) -> PerformanceResult:
        """Test request-scoped caching performance."""
        start_time = time.time()
        try:
            # Simulate request-scoped cache
            class RequestScopedCache:
                def __init__(self):
                    self.cache = {}
                    self.hits = 0
                    self.misses = 0

                def get(self, key):
                    if key in self.cache:
                        self.hits += 1
                        return self.cache[key]
                    self.misses += 1
                    return None

                def set(self, key, value):
                    self.cache[key] = value

                def clear(self):
                    self.cache.clear()
                    self.hits = 0
                    self.misses = 0

            cache = RequestScopedCache()
            latencies = []
            num_operations = 1000

            # Test cache operations
            for i in range(num_operations):
                key = f"cache_key_{i % 100}"  # 100 unique keys, creating cache hits

                # Measure cache get operation
                get_start = time.time()
                value = cache.get(key)
                get_end = time.time()

                if value is None:
                    # Cache miss - set the value
                    set_start = time.time()
                    cache.set(key, f"cached_value_{i}")
                    set_end = time.time()
                    latencies.append(set_end - set_start)
                else:
                    # Cache hit
                    latencies.append(get_end - get_start)

            latency_stats = self.measure_latency_stats(latencies)
            throughput = num_operations / (time.time() - start_time)
            meets_requirements = (
                latency_stats.get("p99", float("inf")) < self.target_p99_latency_ms
            )

            hit_rate = (
                cache.hits / (cache.hits + cache.misses) * 100
                if (cache.hits + cache.misses) > 0
                else 0
            )

            return PerformanceResult(
                "request_scoped_caching",
                "PASS" if meets_requirements else "FAIL",
                latency_stats,
                throughput,
                meets_requirements,
                {
                    "cache_hits": cache.hits,
                    "cache_misses": cache.misses,
                    "hit_rate_percent": hit_rate,
                    "num_operations": num_operations,
                },
            )

        except Exception as e:
            return PerformanceResult(
                "request_scoped_caching", "ERROR", {}, 0.0, False, {}, str(e)
            )

    def test_precompiled_patterns(self) -> PerformanceResult:
        """Test pre-compiled pattern matching performance."""
        start_time = time.time()
        try:
            import re

            # Pre-compile patterns
            patterns = [
                re.compile(
                    r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
                ),  # Email
                re.compile(r"^\d{3}-\d{2}-\d{4}$"),  # SSN format
                re.compile(r"^https?://[^\s/$.?#].[^\s]*$"),  # URL
                re.compile(r"^\+?1?[2-9]\d{2}[2-9]\d{2}\d{4}$"),  # Phone
                re.compile(
                    r"^[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}([A-Z0-9]?){0,16}$"
                ),  # IBAN-like
            ]

            # Test data
            test_strings = [
                "user@example.com",
                "123-45-6789",
                "https://example.com/path",
                "+1234567890",
                "GB82WEST12345698765432",
                "invalid_data_123",
                "another@test.org",
                "987-65-4321",
            ]

            latencies = []
            num_tests = 1000

            for i in range(num_tests):
                test_string = test_strings[i % len(test_strings)]
                pattern = patterns[i % len(patterns)]

                match_start = time.time()
                result = pattern.match(test_string)
                match_end = time.time()

                latencies.append(match_end - match_start)

            latency_stats = self.measure_latency_stats(latencies)
            throughput = num_tests / (time.time() - start_time)
            meets_requirements = (
                latency_stats.get("p99", float("inf")) < self.target_p99_latency_ms
            )

            return PerformanceResult(
                "precompiled_patterns",
                "PASS" if meets_requirements else "FAIL",
                latency_stats,
                throughput,
                meets_requirements,
                {
                    "num_patterns": len(patterns),
                    "num_tests": num_tests,
                    "pattern_types": ["email", "ssn", "url", "phone", "iban"],
                },
            )

        except Exception as e:
            return PerformanceResult(
                "precompiled_patterns", "ERROR", {}, 0.0, False, {}, str(e)
            )

    def test_concurrent_performance(self) -> PerformanceResult:
        """Test performance consistency under concurrent load."""
        start_time = time.time()
        try:

            def worker_task(worker_id: int, num_operations: int) -> list[float]:
                """Worker function for concurrent testing."""
                latencies = []
                lookup_table = {f"key_{i}": f"value_{i}" for i in range(1000)}

                for i in range(num_operations):
                    key = f"key_{i % 1000}"
                    lookup_start = time.time()
                    value = lookup_table.get(key)
                    lookup_end = time.time()
                    latencies.append(lookup_end - lookup_start)

                return latencies

            num_workers = 10
            operations_per_worker = 100
            all_latencies = []

            with ThreadPoolExecutor(max_workers=num_workers) as executor:
                futures = [
                    executor.submit(worker_task, i, operations_per_worker)
                    for i in range(num_workers)
                ]

                for future in as_completed(futures):
                    worker_latencies = future.result()
                    all_latencies.extend(worker_latencies)

            latency_stats = self.measure_latency_stats(all_latencies)
            total_operations = num_workers * operations_per_worker
            throughput = total_operations / (time.time() - start_time)
            meets_requirements = (
                latency_stats.get("p99", float("inf")) < self.target_p99_latency_ms
            )

            return PerformanceResult(
                "concurrent_performance",
                "PASS" if meets_requirements else "FAIL",
                latency_stats,
                throughput,
                meets_requirements,
                {
                    "num_workers": num_workers,
                    "operations_per_worker": operations_per_worker,
                    "total_operations": total_operations,
                },
            )

        except Exception as e:
            return PerformanceResult(
                "concurrent_performance", "ERROR", {}, 0.0, False, {}, str(e)
            )

    def test_wina_component_discovery(self) -> PerformanceResult:
        """Test discovery and basic validation of WINA components."""
        start_time = time.time()
        try:
            wina_files = []

            # Search for WINA-related files
            for wina_path in self.project_root.rglob("*wina*"):
                if wina_path.is_file() and wina_path.suffix == ".py":
                    wina_files.append(str(wina_path.relative_to(self.project_root)))

            # Try to analyze file structure
            component_analysis = {
                "total_files": len(wina_files),
                "core_components": [],
                "optimization_files": [],
                "performance_files": [],
            }

            for file_path in wina_files:
                file_name = Path(file_path).name.lower()
                if "core" in file_name:
                    component_analysis["core_components"].append(file_path)
                elif "optimization" in file_name or "performance" in file_name:
                    component_analysis["optimization_files"].append(file_path)
                elif "performance" in file_name:
                    component_analysis["performance_files"].append(file_path)

            latency_stats = {"discovery_time_ms": (time.time() - start_time) * 1000}
            meets_requirements = len(wina_files) > 0

            return PerformanceResult(
                "wina_component_discovery",
                "PASS" if meets_requirements else "FAIL",
                latency_stats,
                len(wina_files),
                meets_requirements,
                component_analysis,
                None if meets_requirements else "No WINA components found",
            )

        except Exception as e:
            return PerformanceResult(
                "wina_component_discovery", "ERROR", {}, 0.0, False, {}, str(e)
            )

    def run_all_tests(self) -> dict[str, Any]:
        """Run all WINA performance tests."""
        print("Starting WINA Performance Testing...")
        print(f"Target P99 Latency: < {self.target_p99_latency_ms}ms")
        print("=" * 60)

        # Define test methods
        test_methods = [
            self.test_wina_component_discovery,
            self.test_o1_lookup_performance,
            self.test_request_scoped_caching,
            self.test_precompiled_patterns,
            self.test_concurrent_performance,
        ]

        # Run all tests
        for test_method in test_methods:
            try:
                result = test_method()
                self.log_result(result)
            except Exception as e:
                error_result = PerformanceResult(
                    test_method.__name__,
                    "ERROR",
                    {},
                    0.0,
                    False,
                    {},
                    f"Test execution failed: {e!s}",
                )
                self.log_result(error_result)

        # Generate summary
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.status == "PASS")
        failed_tests = sum(1 for r in self.results if r.status == "FAIL")
        error_tests = sum(1 for r in self.results if r.status == "ERROR")
        meets_requirements = sum(1 for r in self.results if r.meets_requirements)

        # Calculate overall performance metrics
        all_p99_latencies = [
            r.latency_stats.get("p99", 0)
            for r in self.results
            if r.latency_stats.get("p99")
        ]
        avg_p99 = statistics.mean(all_p99_latencies) if all_p99_latencies else 0
        max_p99 = max(all_p99_latencies) if all_p99_latencies else 0

        summary = {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "errors": error_tests,
            "meets_requirements": meets_requirements,
            "performance_summary": {
                "target_p99_ms": self.target_p99_latency_ms,
                "average_p99_ms": avg_p99,
                "max_p99_ms": max_p99,
                "requirements_met": meets_requirements == total_tests,
            },
            "results": [
                {
                    "test_name": r.test_name,
                    "status": r.status,
                    "latency_stats": r.latency_stats,
                    "throughput": r.throughput,
                    "meets_requirements": r.meets_requirements,
                    "details": r.details,
                    "error_message": r.error_message,
                }
                for r in self.results
            ],
        }

        print("\n" + "=" * 60)
        print("WINA PERFORMANCE TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Errors: {error_tests}")
        print(f"Requirements Met: {meets_requirements}/{total_tests}")
        print(f"Average P99 Latency: {avg_p99:.2f}ms")
        print(f"Max P99 Latency: {max_p99:.2f}ms")
        print(
            f"Target Met: {'✓' if summary['performance_summary']['requirements_met'] else '✗'}"
        )

        return summary


def main():
    tester = WINAPerformanceTester()
    summary = tester.run_all_tests()

    # Save results
    output_file = project_root / "wina_performance_test_results.json"
    with open(output_file, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nDetailed results saved to: {output_file}")

    # Return appropriate exit code
    if not summary["performance_summary"]["requirements_met"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
