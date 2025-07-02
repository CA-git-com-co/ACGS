#!/usr/bin/env python3
"""
ACGS-2 Comprehensive Test Runner

This script provides a unified interface for running all types of tests:
- Unit tests
- Integration tests
- End-to-end tests
- Performance tests
- Security tests
- Coverage analysis

Usage:
    python scripts/test_runner.py [--type TYPE] [--coverage] [--parallel] [--verbose]
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path


class TestRunner:
    """Comprehensive test runner for ACGS-2."""

    def __init__(self, project_root: Path, verbose: bool = False):
        self.project_root = project_root
        self.verbose = verbose
        self.results = {}

    def run_command(
        self, cmd: list[str], description: str, timeout: int = 300
    ) -> dict[str, any]:
        """Run a command and capture results."""
        print(f"\n🔍 {description}")
        if self.verbose:
            print(f"Command: {' '.join(cmd)}")

        start_time = time.time()

        try:
            result = subprocess.run(
                cmd,
                check=False,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.project_root,
            )

            duration = time.time() - start_time

            success = result.returncode == 0

            if success:
                print(f"✅ {description} passed ({duration:.2f}s)")
            else:
                print(f"❌ {description} failed ({duration:.2f}s)")
                if self.verbose and result.stderr:
                    print(f"Error: {result.stderr}")

            return {
                "success": success,
                "duration": duration,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }

        except subprocess.TimeoutExpired:
            print(f"⏰ {description} timed out after {timeout}s")
            return {"success": False, "duration": timeout, "error": "timeout"}
        except Exception as e:
            print(f"💥 {description} failed with error: {e}")
            return {
                "success": False,
                "duration": time.time() - start_time,
                "error": str(e),
            }

    def run_unit_tests(
        self, parallel: bool = False, coverage: bool = False
    ) -> dict[str, any]:
        """Run unit tests."""
        cmd = ["pytest", "tests/unit/"]

        if parallel:
            cmd.extend(["-n", "auto"])

        if coverage:
            cmd.extend(
                [
                    "--cov=services",
                    "--cov=scripts",
                    "--cov-report=term-missing",
                    "--cov-report=html:htmlcov",
                    "--cov-report=json:coverage.json",
                ]
            )

        cmd.extend(["-v", "--tb=short"])

        return self.run_command(cmd, "Unit Tests")

    def run_integration_tests(self, parallel: bool = False) -> dict[str, any]:
        """Run integration tests."""
        cmd = ["pytest", "tests/integration/", "-v", "--tb=short"]

        if parallel:
            cmd.extend(["-n", "auto"])

        return self.run_command(cmd, "Integration Tests", timeout=600)

    def run_e2e_tests(self) -> dict[str, any]:
        """Run end-to-end tests."""
        cmd = ["pytest", "tests/e2e/", "-v", "--tb=short", "-s"]

        return self.run_command(cmd, "End-to-End Tests", timeout=900)

    def run_performance_tests(self) -> dict[str, any]:
        """Run performance tests."""
        cmd = ["pytest", "tests/performance/", "-v", "--tb=short", "-m", "not slow"]

        return self.run_command(cmd, "Performance Tests", timeout=600)

    def run_security_tests(self) -> dict[str, any]:
        """Run security tests."""
        cmd = ["pytest", "tests/security/", "-v", "--tb=short"]

        return self.run_command(cmd, "Security Tests")

    def run_linting(self) -> dict[str, any]:
        """Run linting checks."""
        cmd = ["python", "scripts/lint.py", "--check-only"]

        return self.run_command(cmd, "Code Quality Checks")

    def generate_coverage_report(self) -> dict[str, any]:
        """Generate comprehensive coverage report."""
        cmd = [
            "pytest",
            "tests/unit/",
            "tests/integration/",
            "--cov=services",
            "--cov=scripts",
            "--cov-report=html:htmlcov",
            "--cov-report=json:coverage.json",
            "--cov-report=term",
            "--cov-fail-under=60",  # Minimum 60% coverage
        ]

        return self.run_command(cmd, "Coverage Analysis", timeout=600)

    def run_all_tests(
        self, parallel: bool = False, coverage: bool = False
    ) -> dict[str, any]:
        """Run all test suites."""
        print("🚀 Running Complete ACGS-2 Test Suite")
        print("=" * 50)

        # Run linting first
        self.results["linting"] = self.run_linting()

        # Run unit tests
        self.results["unit"] = self.run_unit_tests(parallel=parallel, coverage=coverage)

        # Run integration tests
        self.results["integration"] = self.run_integration_tests(parallel=parallel)

        # Run security tests
        self.results["security"] = self.run_security_tests()

        # Run performance tests
        self.results["performance"] = self.run_performance_tests()

        # Run e2e tests (if unit and integration pass)
        if self.results["unit"]["success"] and self.results["integration"]["success"]:
            self.results["e2e"] = self.run_e2e_tests()
        else:
            print("⏭️  Skipping E2E tests due to unit/integration failures")
            self.results["e2e"] = {"success": False, "skipped": True}

        # Generate coverage report if requested
        if coverage:
            self.results["coverage"] = self.generate_coverage_report()

        return self.results

    def print_summary(self) -> None:
        """Print test results summary."""
        print("\n" + "=" * 50)
        print("📊 Test Results Summary")
        print("=" * 50)

        total_tests = 0
        passed_tests = 0
        total_duration = 0

        for test_type, result in self.results.items():
            if result.get("skipped"):
                status = "⏭️  SKIPPED"
            elif result["success"]:
                status = "✅ PASSED"
                passed_tests += 1
            else:
                status = "❌ FAILED"

            duration = result.get("duration", 0)
            total_duration += duration
            total_tests += 1

            print(f"{test_type.upper():15} {status:10} ({duration:.2f}s)")

        print("-" * 50)
        print(
            f"TOTAL:          {passed_tests}/{total_tests} passed ({total_duration:.2f}s)"
        )

        if passed_tests == total_tests:
            print("\n🎉 All tests passed!")
            return True
        print(f"\n💥 {total_tests - passed_tests} test suite(s) failed")
        return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Run ACGS-2 test suites")
    parser.add_argument(
        "--type",
        choices=["unit", "integration", "e2e", "performance", "security", "all"],
        default="all",
        help="Type of tests to run",
    )
    parser.add_argument(
        "--coverage", action="store_true", help="Generate coverage report"
    )
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    runner = TestRunner(project_root, verbose=args.verbose)

    # Run specified tests
    if args.type == "unit":
        runner.results["unit"] = runner.run_unit_tests(
            parallel=args.parallel, coverage=args.coverage
        )
    elif args.type == "integration":
        runner.results["integration"] = runner.run_integration_tests(
            parallel=args.parallel
        )
    elif args.type == "e2e":
        runner.results["e2e"] = runner.run_e2e_tests()
    elif args.type == "performance":
        runner.results["performance"] = runner.run_performance_tests()
    elif args.type == "security":
        runner.results["security"] = runner.run_security_tests()
    else:  # all
        runner.run_all_tests(parallel=args.parallel, coverage=args.coverage)

    # Print summary and exit with appropriate code
    success = runner.print_summary()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
