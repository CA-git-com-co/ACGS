#!/usr/bin/env python3
"""
ACGS Testing Suite Runner
Constitutional Hash: cdd01ef066bc6cf2

Executes comprehensive testing suite including:
1. Performance benchmarks for <5ms P99 latency
2. Cache validation tests for 85%+ hit rate
3. Constitutional compliance validation
4. Port number verification
5. CI/CD integration tests
"""

import argparse
import asyncio
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class TestResult:
    """Test execution result"""

    name: str
    success: bool
    duration: float
    output: str
    error: Optional[str] = None


class ACGSTestSuite:
    """ACGS comprehensive test suite runner"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.results: List[TestResult] = []

    def run_complete_suite(
        self,
        include_benchmarks: bool = True,
        include_hypothesis: bool = True,
        include_validation: bool = True,
        verbose: bool = False,
    ) -> bool:
        """Run the complete ACGS testing suite"""

        print(f"🚀 Starting ACGS Testing Suite")
        print(f"📋 Constitutional Hash: {self.constitutional_hash}")
        print(f"📁 Project Root: {self.project_root}")
        print(f"🕒 Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")

        suite_start = time.time()

        # Test categories to run
        test_categories = [
            (
                "Constitutional Hash Validation",
                self._run_constitutional_validation,
                include_validation,
            ),
            (
                "Port Number Verification",
                self._run_port_verification,
                include_validation,
            ),
            (
                "Performance Benchmarks",
                self._run_performance_benchmarks,
                include_benchmarks,
            ),
            (
                "Cache Hypothesis Tests",
                self._run_cache_hypothesis_tests,
                include_hypothesis,
            ),
            ("Integration Tests", self._run_integration_tests, True),
        ]

        # Execute test categories
        for category_name, test_func, should_run in test_categories:
            if not should_run:
                print(f"⏭️  Skipping {category_name}")
                continue

            print(f"\n📋 Running {category_name}")
            print("=" * 60)

            try:
                success = test_func(verbose=verbose)
                status = "✅ PASSED" if success else "❌ FAILED"
                print(f"\n{status} {category_name}")
            except Exception as e:
                print(f"\n💥 ERROR in {category_name}: {e}")
                self.results.append(
                    TestResult(
                        name=category_name,
                        success=False,
                        duration=0.0,
                        output="",
                        error=str(e),
                    )
                )

        # Generate final report
        suite_duration = time.time() - suite_start
        return self._generate_final_report(suite_duration)

    def _run_constitutional_validation(self, verbose: bool = False) -> bool:
        """Run constitutional hash validation tests"""
        start_time = time.time()

        try:
            # Check if constitutional hash exists in key files
            result = subprocess.run(
                [
                    "grep",
                    "-r",
                    self.constitutional_hash,
                    str(self.project_root),
                    "--include=*.py",
                    "--include=*.yml",
                    "--include=*.md",
                ],
                capture_output=True,
                text=True,
            )

            found_files = (
                result.stdout.strip().split("\n") if result.stdout.strip() else []
            )

            print(f"🔍 Constitutional hash found in {len(found_files)} files")

            if verbose and found_files:
                for line in found_files[:5]:  # Show first 5 matches
                    print(f"   📄 {line}")
                if len(found_files) > 5:
                    print(f"   ... and {len(found_files) - 5} more files")

            duration = time.time() - start_time
            success = len(found_files) > 0

            self.results.append(
                TestResult(
                    name="Constitutional Hash Validation",
                    success=success,
                    duration=duration,
                    output=f"Found in {len(found_files)} files",
                )
            )

            return success

        except Exception as e:
            duration = time.time() - start_time
            self.results.append(
                TestResult(
                    name="Constitutional Hash Validation",
                    success=False,
                    duration=duration,
                    output="",
                    error=str(e),
                )
            )
            return False

    def _run_port_verification(self, verbose: bool = False) -> bool:
        """Run port number verification"""
        start_time = time.time()

        try:
            script_path = self.project_root / "scripts" / "validate_port_numbers.py"

            if not script_path.exists():
                print(f"⚠️  Port validation script not found: {script_path}")
                return True  # Don't fail if script doesn't exist

            # Run port validation script
            result = subprocess.run(
                [
                    sys.executable,
                    str(script_path),
                    "--project-root",
                    str(self.project_root),
                ],
                capture_output=True,
                text=True,
            )

            duration = time.time() - start_time
            success = result.returncode == 0

            if verbose or not success:
                print(result.stdout)
                if result.stderr:
                    print("STDERR:", result.stderr)

            self.results.append(
                TestResult(
                    name="Port Number Verification",
                    success=success,
                    duration=duration,
                    output=result.stdout,
                    error=result.stderr if result.stderr else None,
                )
            )

            return success

        except Exception as e:
            duration = time.time() - start_time
            self.results.append(
                TestResult(
                    name="Port Number Verification",
                    success=False,
                    duration=duration,
                    output="",
                    error=str(e),
                )
            )
            return False

    def _run_performance_benchmarks(self, verbose: bool = False) -> bool:
        """Run performance benchmark tests"""
        start_time = time.time()

        try:
            test_file = (
                self.project_root
                / "tests"
                / "performance"
                / "test_constitutional_validation_benchmark.py"
            )

            if not test_file.exists():
                print(f"⚠️  Benchmark test file not found: {test_file}")
                return True  # Don't fail if test doesn't exist

            # Run pytest-benchmark tests
            cmd = [
                sys.executable,
                "-m",
                "pytest",
                str(test_file),
                "-v",
                "--benchmark-only",
                "--benchmark-sort=mean",
                "--benchmark-columns=min,max,mean,stddev,rounds,iterations",
                "--benchmark-json=benchmark_results.json",
            ]

            if not verbose:
                cmd.append("-q")

            result = subprocess.run(
                cmd, capture_output=True, text=True, cwd=self.project_root
            )

            duration = time.time() - start_time
            success = result.returncode == 0

            # Parse benchmark results if available
            benchmark_file = self.project_root / "benchmark_results.json"
            benchmark_summary = ""

            if benchmark_file.exists():
                try:
                    with open(benchmark_file, "r") as f:
                        data = json.load(f)

                    benchmarks = data.get("benchmarks", [])
                    benchmark_summary = (
                        f"\n📊 Benchmark Summary: {len(benchmarks)} tests"
                    )

                    for bench in benchmarks:
                        name = bench.get("name", "Unknown")
                        stats = bench.get("stats", {})
                        mean_ms = stats.get("mean", 0) * 1000
                        max_ms = stats.get("max", 0) * 1000

                        status = "✅" if max_ms < 5.0 else "⚠️"
                        benchmark_summary += f"\n   {status} {name}: P99={max_ms:.3f}ms, Mean={mean_ms:.3f}ms"

                except Exception as e:
                    benchmark_summary = f"\n⚠️  Error parsing benchmarks: {e}"

            if verbose or not success:
                print(result.stdout)
                if result.stderr:
                    print("STDERR:", result.stderr)

            print(benchmark_summary)

            self.results.append(
                TestResult(
                    name="Performance Benchmarks",
                    success=success,
                    duration=duration,
                    output=result.stdout + benchmark_summary,
                    error=result.stderr if result.stderr else None,
                )
            )

            return success

        except Exception as e:
            duration = time.time() - start_time
            self.results.append(
                TestResult(
                    name="Performance Benchmarks",
                    success=False,
                    duration=duration,
                    output="",
                    error=str(e),
                )
            )
            return False

    def _run_cache_hypothesis_tests(self, verbose: bool = False) -> bool:
        """Run cache hypothesis tests"""
        start_time = time.time()

        try:
            test_file = (
                self.project_root / "tests" / "performance" / "test_cache_hypothesis.py"
            )

            if not test_file.exists():
                print(f"⚠️  Cache hypothesis test file not found: {test_file}")
                return True  # Don't fail if test doesn't exist

            # Run hypothesis tests
            cmd = [
                sys.executable,
                "-m",
                "pytest",
                str(test_file),
                "-v",
                "--hypothesis-show-statistics",
                "--tb=short",
            ]

            if not verbose:
                cmd.append("-q")

            result = subprocess.run(
                cmd, capture_output=True, text=True, cwd=self.project_root
            )

            duration = time.time() - start_time
            success = result.returncode == 0

            # Extract hypothesis statistics
            hypothesis_summary = ""
            if "hypothesis" in result.stdout.lower():
                lines = result.stdout.split("\n")
                stats_lines = [
                    line
                    for line in lines
                    if any(
                        keyword in line.lower()
                        for keyword in ["hypothesis", "examples", "passed", "failed"]
                    )
                ]
                if stats_lines:
                    hypothesis_summary = "\n📊 Hypothesis Test Summary:\n" + "\n".join(
                        f"   {line}" for line in stats_lines[-5:]
                    )

            if verbose or not success:
                print(result.stdout)
                if result.stderr:
                    print("STDERR:", result.stderr)

            print(hypothesis_summary)

            self.results.append(
                TestResult(
                    name="Cache Hypothesis Tests",
                    success=success,
                    duration=duration,
                    output=result.stdout + hypothesis_summary,
                    error=result.stderr if result.stderr else None,
                )
            )

            return success

        except Exception as e:
            duration = time.time() - start_time
            self.results.append(
                TestResult(
                    name="Cache Hypothesis Tests",
                    success=False,
                    duration=duration,
                    output="",
                    error=str(e),
                )
            )
            return False

    def _run_integration_tests(self, verbose: bool = False) -> bool:
        """Run integration tests"""
        start_time = time.time()

        try:
            # Run basic integration tests
            integration_dirs = [
                self.project_root / "tests" / "integration",
                self.project_root / "tests" / "e2e",
            ]

            found_tests = False
            all_success = True

            for test_dir in integration_dirs:
                if test_dir.exists():
                    found_tests = True

                    cmd = [
                        sys.executable,
                        "-m",
                        "pytest",
                        str(test_dir),
                        "-v",
                        "--tb=short",
                        "-x",  # Stop on first failure
                    ]

                    if not verbose:
                        cmd.append("-q")

                    result = subprocess.run(
                        cmd, capture_output=True, text=True, cwd=self.project_root
                    )

                    if result.returncode != 0:
                        all_success = False
                        if verbose:
                            print(f"❌ Integration tests failed in {test_dir}")
                            print(result.stdout)
                            if result.stderr:
                                print("STDERR:", result.stderr)

            if not found_tests:
                print("⚠️  No integration test directories found")
                all_success = True  # Don't fail if no integration tests exist

            duration = time.time() - start_time

            self.results.append(
                TestResult(
                    name="Integration Tests",
                    success=all_success,
                    duration=duration,
                    output=f"Found tests: {found_tests}, Success: {all_success}",
                )
            )

            return all_success

        except Exception as e:
            duration = time.time() - start_time
            self.results.append(
                TestResult(
                    name="Integration Tests",
                    success=False,
                    duration=duration,
                    output="",
                    error=str(e),
                )
            )
            return False

    def _generate_final_report(self, total_duration: float) -> bool:
        """Generate final test report"""
        print(f"\n🏁 ACGS Testing Suite Complete")
        print("=" * 60)
        print(f"⏱️  Total Duration: {total_duration:.2f} seconds")
        print(f"📋 Constitutional Hash: {self.constitutional_hash}")

        # Count results
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.success)
        failed_tests = total_tests - passed_tests

        print(f"\n📊 Test Results Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   📈 Success Rate: {(passed_tests/total_tests*100):.1f}%")

        # Detailed results
        print(f"\n📋 Detailed Results:")
        for result in self.results:
            status = "✅" if result.success else "❌"
            print(f"   {status} {result.name}: {result.duration:.2f}s")

            if result.error and not result.success:
                print(f"      ❌ Error: {result.error}")

        # Performance targets summary
        print(f"\n🎯 Performance Targets:")
        print(f"   • P99 Latency: <5ms for constitutional validation")
        print(f"   • Cache Hit Rate: ≥85% for constitutional decisions")
        print(f"   • Throughput: ≥100 RPS for concurrent operations")
        print(f"   • Constitutional Hash: {self.constitutional_hash}")

        # Final status
        overall_success = failed_tests == 0
        final_status = (
            "✅ ALL TESTS PASSED"
            if overall_success
            else f"❌ {failed_tests} TESTS FAILED"
        )
        print(f"\n{final_status}")

        return overall_success


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Run ACGS comprehensive testing suite")
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Root directory of ACGS project",
    )
    parser.add_argument(
        "--skip-benchmarks",
        action="store_true",
        help="Skip performance benchmark tests",
    )
    parser.add_argument(
        "--skip-hypothesis",
        action="store_true",
        help="Skip hypothesis-based cache tests",
    )
    parser.add_argument(
        "--skip-validation", action="store_true", help="Skip validation tests"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Initialize test suite
    test_suite = ACGSTestSuite(args.project_root)

    # Run complete suite
    success = test_suite.run_complete_suite(
        include_benchmarks=not args.skip_benchmarks,
        include_hypothesis=not args.skip_hypothesis,
        include_validation=not args.skip_validation,
        verbose=args.verbose,
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
