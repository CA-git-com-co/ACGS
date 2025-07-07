#!/usr/bin/env python3
"""
Comprehensive Test Runner for ACGS Enhanced Services

Executes all test suites with:
- Coverage reporting
- Performance benchmarks
- Test result aggregation
- Constitutional compliance validation
- HTML report generation

Constitutional Hash: cdd01ef066bc6cf2
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import coverage
import pytest


class ACGSTestRunner:
    """Comprehensive test runner for ACGS services."""

    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.test_suites = {
            "constitutional_ai": "tests/services/test_constitutional_ai_service.py",
            "evolutionary_computation": (
                "tests/services/test_evolutionary_computation_service.py"
            ),
            "governance_synthesis": (
                "tests/services/test_governance_synthesis_service.py"
            ),
            "formal_verification": "tests/services/test_formal_verification_service.py",
            "policy_governance": "tests/services/test_policy_governance_service.py",
        }
        self.results = {}
        self.coverage_data = None

    def run_all_tests(
        self, verbose: bool = True, coverage_enabled: bool = True
    ) -> dict[str, Any]:
        """Run all test suites."""
        print("🚀 Starting ACGS Comprehensive Test Suite")
        print("   Constitutional Hash: cdd01ef066bc6cf2")
        print(f"   Timestamp: {datetime.now(timezone.utc).isoformat()}")
        print("=" * 80)

        start_time = time.time()

        # Initialize coverage if enabled
        if coverage_enabled:
            self.coverage_data = coverage.Coverage(
                source=["services/core"],
                omit=["*/tests/*", "*/test_*", "*/__pycache__/*"],
            )
            self.coverage_data.start()

        # Run each test suite
        for suite_name, test_path in self.test_suites.items():
            self.run_test_suite(suite_name, test_path, verbose)

        # Stop coverage
        if coverage_enabled:
            self.coverage_data.stop()
            self.coverage_data.save()

        # Generate reports
        total_time = time.time() - start_time
        summary = self.generate_summary(total_time, coverage_enabled)

        return summary

    def run_test_suite(
        self, suite_name: str, test_path: str, verbose: bool
    ) -> dict[str, Any]:
        """Run a single test suite."""
        print(f"\n📋 Running {suite_name} tests...")
        print("-" * 60)

        full_path = self.base_path / test_path
        if not full_path.exists():
            print(f"⚠️  Test file not found: {full_path}")
            self.results[suite_name] = {
                "status": "not_found",
                "tests_run": 0,
                "failures": 0,
                "errors": 0,
                "skipped": 0,
                "duration": 0,
            }
            return self.results[suite_name]

        # Configure pytest arguments
        pytest_args = [
            str(full_path),
            "-v" if verbose else "-q",
            "--tb=short",
            "--json-report",
            f"--json-report-file=test_results_{suite_name}.json",
            "-p",
            "no:warnings",  # Suppress warnings for cleaner output
        ]

        # Add markers based on suite
        if suite_name in ["constitutional_ai", "evolutionary_computation"]:
            pytest_args.extend(["-m", "not benchmark"])  # Skip benchmarks by default

        # Run tests
        start_time = time.time()
        exit_code = pytest.main(pytest_args)
        duration = time.time() - start_time

        # Parse results
        result = self.parse_test_results(suite_name, exit_code, duration)
        self.results[suite_name] = result

        # Print suite summary
        self.print_suite_summary(suite_name, result)

        return result

    def parse_test_results(
        self, suite_name: str, exit_code: int, duration: float
    ) -> dict[str, Any]:
        """Parse test results from pytest json report."""
        try:
            report_file = f"test_results_{suite_name}.json"
            if os.path.exists(report_file):
                with open(report_file) as f:
                    report_data = json.load(f)

                # Extract summary
                summary = report_data.get("summary", {})
                tests = report_data.get("tests", [])

                result = {
                    "status": "passed" if exit_code == 0 else "failed",
                    "tests_run": summary.get("total", 0),
                    "passed": summary.get("passed", 0),
                    "failures": summary.get("failed", 0),
                    "errors": summary.get("error", 0),
                    "skipped": summary.get("skipped", 0),
                    "duration": duration,
                    "exit_code": exit_code,
                }

                # Extract performance metrics if available
                perf_tests = [
                    t for t in tests if "performance" in t.get("keywords", [])
                ]
                if perf_tests:
                    result["performance_tests"] = len(perf_tests)
                    result["avg_performance"] = self.calculate_avg_performance(
                        perf_tests
                    )

                # Clean up report file
                os.remove(report_file)

                return result
            else:
                # Fallback if no json report
                return {
                    "status": "completed",
                    "tests_run": "unknown",
                    "failures": 0 if exit_code == 0 else "unknown",
                    "errors": 0,
                    "skipped": 0,
                    "duration": duration,
                    "exit_code": exit_code,
                }
        except Exception as e:
            print(f"⚠️  Error parsing results: {e}")
            return {
                "status": "error",
                "error": str(e),
                "duration": duration,
                "exit_code": exit_code,
            }

    def calculate_avg_performance(self, perf_tests: list[dict]) -> float:
        """Calculate average performance from performance tests."""
        durations = []
        for test in perf_tests:
            if "duration" in test:
                durations.append(test["duration"])

        return sum(durations) / len(durations) if durations else 0

    def print_suite_summary(self, suite_name: str, result: dict[str, Any]):
        """Print summary for a test suite."""
        status_symbol = "✅" if result["status"] == "passed" else "❌"

        print(f"\n{status_symbol} {suite_name}:")
        print(f"   Tests run: {result.get('tests_run', 'unknown')}")
        if result.get("passed"):
            print(f"   Passed: {result['passed']}")
        if result.get("failures"):
            print(f"   Failed: {result['failures']}")
        if result.get("errors"):
            print(f"   Errors: {result['errors']}")
        if result.get("skipped"):
            print(f"   Skipped: {result['skipped']}")
        print(f"   Duration: {result['duration']:.2f}s")

        if result.get("performance_tests"):
            print(f"   Performance tests: {result['performance_tests']}")
            print(f"   Avg performance: {result['avg_performance']:.3f}s")

    def generate_summary(
        self, total_time: float, coverage_enabled: bool
    ) -> dict[str, Any]:
        """Generate comprehensive test summary."""
        print("\n" + "=" * 80)
        print("📊 ACGS Test Suite Summary")
        print("=" * 80)

        # Calculate totals
        total_tests = 0
        total_passed = 0
        total_failed = 0
        total_errors = 0
        total_skipped = 0
        all_passed = True

        for suite_name, result in self.results.items():
            if isinstance(result.get("tests_run"), int):
                total_tests += result["tests_run"]
            if isinstance(result.get("passed"), int):
                total_passed += result["passed"]
            if isinstance(result.get("failures"), int):
                total_failed += result["failures"]
            if isinstance(result.get("errors"), int):
                total_errors += result["errors"]
            if isinstance(result.get("skipped"), int):
                total_skipped += result["skipped"]

            if result.get("status") != "passed":
                all_passed = False

        # Print summary
        print(f"Total test suites: {len(self.results)}")
        print(f"Total tests run: {total_tests}")
        print(f"Total passed: {total_passed}")
        print(f"Total failed: {total_failed}")
        print(f"Total errors: {total_errors}")
        print(f"Total skipped: {total_skipped}")
        print(f"Total duration: {total_time:.2f}s")

        # Coverage report
        coverage_summary = {}
        if coverage_enabled and self.coverage_data:
            print("\n📈 Coverage Report:")
            print("-" * 60)
            try:
                coverage_summary = self.generate_coverage_report()
            except Exception as e:
                print(f"⚠️  Coverage report error: {e}")

        # Constitutional compliance
        print("\n🏛️ Constitutional Compliance:")
        print("-" * 60)
        print("Constitutional Hash: cdd01ef066bc6cf2")
        print(f"All services validated: {'✅ Yes' if all_passed else '❌ No'}")
        print(f"Compliance status: {'COMPLIANT' if all_passed else 'NON-COMPLIANT'}")

        # Generate summary object
        summary = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "constitutional_hash": "cdd01ef066bc6cf2",
            "total_suites": len(self.results),
            "total_tests": total_tests,
            "total_passed": total_passed,
            "total_failed": total_failed,
            "total_errors": total_errors,
            "total_skipped": total_skipped,
            "total_duration": total_time,
            "all_passed": all_passed,
            "constitutional_compliance": all_passed,
            "suite_results": self.results,
            "coverage": coverage_summary,
        }

        # Save summary to file
        self.save_summary(summary)

        return summary

    def generate_coverage_report(self) -> dict[str, Any]:
        """Generate coverage report."""
        # Generate text report
        print("\nGenerating coverage report...")
        self.coverage_data.report()

        # Get coverage percentage
        total_coverage = self.coverage_data.report(show_missing=False)

        # Generate HTML report
        html_dir = self.base_path / "htmlcov"
        self.coverage_data.html_report(directory=str(html_dir))
        print(f"\nHTML coverage report generated in: {html_dir}")

        # Generate JSON report for parsing
        json_report = self.base_path / "coverage.json"
        self.coverage_data.json_report(outfile=str(json_report))

        # Parse coverage data
        coverage_summary = {
            "total_coverage": total_coverage,
            "html_report": str(html_dir),
            "json_report": str(json_report),
        }

        # Parse per-file coverage if available
        try:
            with open(json_report) as f:
                coverage_data = json.load(f)
                files = coverage_data.get("files", {})

                service_coverage = {}
                for file_path, file_data in files.items():
                    if "services/core" in file_path:
                        service_name = file_path.split("/")[2]
                        if service_name not in service_coverage:
                            service_coverage[service_name] = []
                        service_coverage[service_name].append(
                            {
                                "file": os.path.basename(file_path),
                                "coverage": file_data["summary"]["percent_covered"],
                            }
                        )

                coverage_summary["service_coverage"] = service_coverage
        except Exception as e:
            print(f"⚠️  Error parsing coverage data: {e}")

        return coverage_summary

    def save_summary(self, summary: dict[str, Any]):
        """Save test summary to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_file = self.base_path / f"test_results_summary_{timestamp}.json"

        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)

        print(f"\n💾 Test summary saved to: {summary_file}")

        # Also save latest summary
        latest_file = self.base_path / "test_results_latest.json"
        with open(latest_file, "w") as f:
            json.dump(summary, f, indent=2)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="ACGS Comprehensive Test Runner")
    parser.add_argument(
        "--suite",
        choices=[
            "all",
            "constitutional_ai",
            "evolutionary_computation",
            "governance_synthesis",
            "formal_verification",
            "policy_governance",
        ],
        default="all",
        help="Test suite to run",
    )
    parser.add_argument(
        "--no-coverage", action="store_true", help="Disable coverage reporting"
    )
    parser.add_argument("--quiet", action="store_true", help="Reduce output verbosity")
    parser.add_argument(
        "--benchmarks", action="store_true", help="Include performance benchmarks"
    )

    args = parser.parse_args()

    # Create test runner
    runner = ACGSTestRunner()

    # Configure based on arguments
    if args.benchmarks:
        # Modify pytest args to include benchmarks
        for suite in runner.test_suites:
            runner.test_suites[suite] += " -m 'performance or benchmark'"

    # Run tests
    if args.suite == "all":
        summary = runner.run_all_tests(
            verbose=not args.quiet, coverage_enabled=not args.no_coverage
        )
    else:
        # Run single suite
        test_path = runner.test_suites.get(args.suite)
        if test_path:
            runner.run_test_suite(args.suite, test_path, not args.quiet)
            summary = runner.generate_summary(0, not args.no_coverage)
        else:
            print(f"❌ Unknown test suite: {args.suite}")
            sys.exit(1)

    # Exit with appropriate code
    sys.exit(0 if summary["all_passed"] else 1)


if __name__ == "__main__":
    main()
