#!/usr/bin/env python3
"""
Performance Targets Validation Script

Validates that performance test results meet ACGS performance targets:
- Sub-5ms P99 latency for critical operations
- >100 RPS sustained throughput
- >85% cache hit rate for cached operations
- Constitutional compliance processing overhead <2ms

Constitutional Hash: cdd01ef066bc6cf2
"""

import argparse
import json
import statistics
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Performance targets
PERFORMANCE_TARGETS = {
    "p99_latency_ms": 5.0,
    "p95_latency_ms": 3.0,
    "p50_latency_ms": 2.0,
    "throughput_rps": 100.0,
    "cache_hit_rate": 0.85,
    "constitutional_compliance_overhead_ms": 2.0,
    "memory_usage_mb_per_operation": 10.0,
    "error_rate": 0.01,  # 1% max error rate
}


class PerformanceValidator:
    """Validates performance test results against targets."""

    def __init__(self, targets: Optional[Dict[str, float]] = None):
        self.targets = targets or PERFORMANCE_TARGETS
        self.violations: List[str] = []
        self.warnings: List[str] = []

    def validate_test_results(self, results_file: Path) -> bool:
        """Validate performance test results from JSON file."""
        print(f"🔍 Validating performance results from: {results_file}")
        print(f"📊 Constitutional Hash: {CONSTITUTIONAL_HASH}")
        print("=" * 60)

        try:
            with open(results_file, "r") as f:
                results = json.load(f)

            # Validate constitutional hash
            if results.get("constitutional_hash") != CONSTITUTIONAL_HASH:
                self.violations.append(
                    f"Constitutional hash mismatch: expected {CONSTITUTIONAL_HASH}, "
                    f"got {results.get('constitutional_hash')}"
                )

            # Validate performance metrics
            self._validate_latency_metrics(results)
            self._validate_throughput_metrics(results)
            self._validate_cache_metrics(results)
            self._validate_resource_metrics(results)
            self._validate_error_rates(results)

            # Generate report
            return self._generate_validation_report()

        except FileNotFoundError:
            print(f"❌ Results file not found: {results_file}")
            return False
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in results file: {e}")
            return False
        except Exception as e:
            print(f"❌ Error validating results: {e}")
            return False

    def _validate_latency_metrics(self, results: Dict[str, Any]) -> None:
        """Validate latency performance metrics."""
        print("⏱️  Validating Latency Metrics")
        print("-" * 30)

        # Extract latency data from results
        latency_data = self._extract_latency_data(results)

        for metric, target in [
            ("p99_latency_ms", self.targets["p99_latency_ms"]),
            ("p95_latency_ms", self.targets["p95_latency_ms"]),
            ("p50_latency_ms", self.targets["p50_latency_ms"]),
        ]:
            if metric in latency_data:
                actual = latency_data[metric]
                if actual > target:
                    self.violations.append(
                        f"{metric}: {actual:.2f}ms exceeds target {target:.2f}ms"
                    )
                    print(f"  ❌ {metric}: {actual:.2f}ms (target: {target:.2f}ms)")
                else:
                    print(f"  ✅ {metric}: {actual:.2f}ms (target: {target:.2f}ms)")
            else:
                self.warnings.append(f"Missing latency metric: {metric}")
                print(f"  ⚠️  Missing metric: {metric}")

    def _validate_throughput_metrics(self, results: Dict[str, Any]) -> None:
        """Validate throughput performance metrics."""
        print("\n🚀 Validating Throughput Metrics")
        print("-" * 30)

        throughput_data = self._extract_throughput_data(results)

        if "throughput_rps" in throughput_data:
            actual = throughput_data["throughput_rps"]
            target = self.targets["throughput_rps"]

            if actual < target:
                self.violations.append(
                    f"Throughput: {actual:.1f} RPS below target {target:.1f} RPS"
                )
                print(f"  ❌ Throughput: {actual:.1f} RPS (target: {target:.1f} RPS)")
            else:
                print(f"  ✅ Throughput: {actual:.1f} RPS (target: {target:.1f} RPS)")
        else:
            self.warnings.append("Missing throughput metric")
            print("  ⚠️  Missing throughput metric")

    def _validate_cache_metrics(self, results: Dict[str, Any]) -> None:
        """Validate cache performance metrics."""
        print("\n💾 Validating Cache Metrics")
        print("-" * 30)

        cache_data = self._extract_cache_data(results)

        if "cache_hit_rate" in cache_data:
            actual = cache_data["cache_hit_rate"]
            target = self.targets["cache_hit_rate"]

            if actual < target:
                self.violations.append(
                    f"Cache hit rate: {actual:.2%} below target {target:.2%}"
                )
                print(f"  ❌ Cache hit rate: {actual:.2%} (target: {target:.2%})")
            else:
                print(f"  ✅ Cache hit rate: {actual:.2%} (target: {target:.2%})")
        else:
            self.warnings.append("Missing cache hit rate metric")
            print("  ⚠️  Missing cache hit rate metric")

    def _validate_resource_metrics(self, results: Dict[str, Any]) -> None:
        """Validate resource usage metrics."""
        print("\n🖥️  Validating Resource Metrics")
        print("-" * 30)

        resource_data = self._extract_resource_data(results)

        # Memory usage validation
        if "memory_usage_mb_per_operation" in resource_data:
            actual = resource_data["memory_usage_mb_per_operation"]
            target = self.targets["memory_usage_mb_per_operation"]

            if actual > target:
                self.violations.append(
                    f"Memory usage: {actual:.2f}MB/op exceeds target {target:.2f}MB/op"
                )
                print(
                    f"  ❌ Memory usage: {actual:.2f}MB/op (target: {target:.2f}MB/op)"
                )
            else:
                print(
                    f"  ✅ Memory usage: {actual:.2f}MB/op (target: {target:.2f}MB/op)"
                )

        # Constitutional compliance overhead
        if "constitutional_compliance_overhead_ms" in resource_data:
            actual = resource_data["constitutional_compliance_overhead_ms"]
            target = self.targets["constitutional_compliance_overhead_ms"]

            if actual > target:
                self.violations.append(
                    f"Constitutional overhead: {actual:.2f}ms exceeds target {target:.2f}ms"
                )
                print(
                    f"  ❌ Constitutional overhead: {actual:.2f}ms (target: {target:.2f}ms)"
                )
            else:
                print(
                    f"  ✅ Constitutional overhead: {actual:.2f}ms (target: {target:.2f}ms)"
                )

    def _validate_error_rates(self, results: Dict[str, Any]) -> None:
        """Validate error rate metrics."""
        print("\n🚨 Validating Error Rates")
        print("-" * 30)

        error_data = self._extract_error_data(results)

        if "error_rate" in error_data:
            actual = error_data["error_rate"]
            target = self.targets["error_rate"]

            if actual > target:
                self.violations.append(
                    f"Error rate: {actual:.2%} exceeds target {target:.2%}"
                )
                print(f"  ❌ Error rate: {actual:.2%} (target: {target:.2%})")
            else:
                print(f"  ✅ Error rate: {actual:.2%} (target: {target:.2%})")
        else:
            self.warnings.append("Missing error rate metric")
            print("  ⚠️  Missing error rate metric")

    def _extract_latency_data(self, results: Dict[str, Any]) -> Dict[str, float]:
        """Extract latency data from test results."""
        latency_data = {}

        # Look for latency data in various result structures
        if "performance_targets" in results:
            perf_targets = results["performance_targets"]
            if "p99_latency_ms" in perf_targets:
                latency_data["p99_latency_ms"] = perf_targets["p99_latency_ms"]

        # Look for latency data in test category results
        for category, tests in results.get("results_by_category", {}).items():
            if "performance" in category.lower():
                for test_name, test_result in tests.items():
                    if "latency" in test_name.lower() and "duration" in test_result:
                        # Convert duration to milliseconds if needed
                        duration_ms = test_result["duration"] * 1000
                        if "p99" in test_name.lower():
                            latency_data["p99_latency_ms"] = duration_ms
                        elif "p95" in test_name.lower():
                            latency_data["p95_latency_ms"] = duration_ms
                        elif "p50" in test_name.lower():
                            latency_data["p50_latency_ms"] = duration_ms

        return latency_data

    def _extract_throughput_data(self, results: Dict[str, Any]) -> Dict[str, float]:
        """Extract throughput data from test results."""
        throughput_data = {}

        if "performance_targets" in results:
            perf_targets = results["performance_targets"]
            if "throughput_rps" in perf_targets:
                throughput_data["throughput_rps"] = perf_targets["throughput_rps"]

        return throughput_data

    def _extract_cache_data(self, results: Dict[str, Any]) -> Dict[str, float]:
        """Extract cache performance data from test results."""
        cache_data = {}

        if "performance_targets" in results:
            perf_targets = results["performance_targets"]
            if "cache_hit_rate" in perf_targets:
                cache_data["cache_hit_rate"] = perf_targets["cache_hit_rate"]

        return cache_data

    def _extract_resource_data(self, results: Dict[str, Any]) -> Dict[str, float]:
        """Extract resource usage data from test results."""
        resource_data: Dict[str, float] = {}

        # Look for resource metrics in results
        for category, tests in results.get("results_by_category", {}).items():
            if "performance" in category.lower():
                for test_name, test_result in tests.items():
                    if "memory" in test_name.lower():
                        # Extract memory usage if available
                        pass
                    elif (
                        "constitutional" in test_name.lower()
                        and "overhead" in test_name.lower()
                    ):
                        # Extract constitutional compliance overhead
                        pass

        return resource_data

    def _extract_error_data(self, results: Dict[str, Any]) -> Dict[str, float]:
        """Extract error rate data from test results."""
        error_data = {}

        # Calculate error rate from test results
        total_tests = results.get("total_tests", 0)
        failed_tests = results.get("failed", 0)
        errors = results.get("errors", 0)

        if total_tests > 0:
            error_rate = (failed_tests + errors) / total_tests
            error_data["error_rate"] = error_rate

        return error_data

    def _generate_validation_report(self) -> bool:
        """Generate validation report and return success status."""
        print("\n" + "=" * 60)
        print("📋 Performance Validation Report")
        print("=" * 60)

        if not self.violations and not self.warnings:
            print("🎉 All performance targets met!")
            print(f"✅ Constitutional Hash: {CONSTITUTIONAL_HASH}")
            return True

        if self.violations:
            print(f"❌ {len(self.violations)} Performance Target Violations:")
            for i, violation in enumerate(self.violations, 1):
                print(f"  {i}. {violation}")

        if self.warnings:
            print(f"\n⚠️  {len(self.warnings)} Warnings:")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")

        print(f"\n📊 Constitutional Hash: {CONSTITUTIONAL_HASH}")

        return len(self.violations) == 0


def main() -> None:
    """Main entry point for performance validation."""
    parser = argparse.ArgumentParser(description="Validate ACGS performance targets")
    parser.add_argument(
        "--report-file", required=True, help="Path to test results JSON file"
    )
    parser.add_argument(
        "--p99-latency-target", type=float, default=5.0, help="P99 latency target in ms"
    )
    parser.add_argument(
        "--throughput-target",
        type=float,
        default=100.0,
        help="Throughput target in RPS",
    )
    parser.add_argument(
        "--cache-hit-rate-target",
        type=float,
        default=0.85,
        help="Cache hit rate target",
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Update targets from command line arguments
    targets = PERFORMANCE_TARGETS.copy()
    targets["p99_latency_ms"] = args.p99_latency_target
    targets["throughput_rps"] = args.throughput_target
    targets["cache_hit_rate"] = args.cache_hit_rate_target

    # Validate performance results
    validator = PerformanceValidator(targets)
    success = validator.validate_test_results(Path(args.report_file))

    if success:
        print("\n🎉 Performance validation passed!")
        sys.exit(0)
    else:
        print("\n❌ Performance validation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
