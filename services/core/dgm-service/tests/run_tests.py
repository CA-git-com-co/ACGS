#!/usr/bin/env python3
"""
Test runner script for DGM Service.

Provides comprehensive test execution with coverage reporting,
performance benchmarking, and detailed result analysis.
"""

import argparse
import asyncio
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

import pytest


def run_command(cmd: List[str], cwd: str = None) -> Dict[str, Any]:
    """Run a command and return the result."""
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)
        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except Exception as e:
        return {"success": False, "returncode": -1, "stdout": "", "stderr": str(e)}


def setup_test_environment():
    """Setup test environment and dependencies."""
    print("Setting up test environment...")

    # Install test dependencies
    cmd = [sys.executable, "-m", "pip", "install", "-r", "requirements-dev.txt"]
    result = run_command(cmd)

    if not result["success"]:
        print(f"Failed to install test dependencies: {result['stderr']}")
        return False

    print("Test environment setup complete.")
    return True


def run_unit_tests(args) -> Dict[str, Any]:
    """Run unit tests with coverage."""
    print("\n" + "=" * 60)
    print("RUNNING UNIT TESTS")
    print("=" * 60)

    pytest_args = [
        "-v",
        "--tb=short",
        "--cov=dgm_service",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
        "--cov-report=xml",
        "--cov-fail-under=90",
        "-m",
        "unit",
    ]

    if args.parallel:
        pytest_args.extend(["-n", "auto"])

    if args.verbose:
        pytest_args.append("-vv")

    if args.fast:
        pytest_args.extend(["-x", "--tb=line"])

    # Add specific test paths
    test_paths = [
        "tests/unit/core/",
        "tests/unit/api/",
        "tests/unit/models/",
        "tests/unit/auth/",
        "tests/unit/database/",
        "tests/unit/monitoring/",
        "tests/unit/utils/",
    ]

    for path in test_paths:
        if os.path.exists(path):
            pytest_args.append(path)

    return_code = pytest.main(pytest_args)

    return {"success": return_code == 0, "return_code": return_code, "test_type": "unit"}


def run_integration_tests(args) -> Dict[str, Any]:
    """Run integration tests."""
    print("\n" + "=" * 60)
    print("RUNNING INTEGRATION TESTS")
    print("=" * 60)

    pytest_args = ["-v", "--tb=short", "-m", "integration"]

    if args.parallel:
        pytest_args.extend(["-n", "auto"])

    if args.verbose:
        pytest_args.append("-vv")

    pytest_args.append("tests/integration/")

    return_code = pytest.main(pytest_args)

    return {"success": return_code == 0, "return_code": return_code, "test_type": "integration"}


def run_constitutional_tests(args) -> Dict[str, Any]:
    """Run constitutional compliance tests."""
    print("\n" + "=" * 60)
    print("RUNNING CONSTITUTIONAL COMPLIANCE TESTS")
    print("=" * 60)

    pytest_args = ["-v", "--tb=short", "-m", "constitutional"]

    if args.verbose:
        pytest_args.append("-vv")

    pytest_args.append("tests/")

    return_code = pytest.main(pytest_args)

    return {"success": return_code == 0, "return_code": return_code, "test_type": "constitutional"}


def run_performance_tests(args) -> Dict[str, Any]:
    """Run performance tests."""
    print("\n" + "=" * 60)
    print("RUNNING PERFORMANCE TESTS")
    print("=" * 60)

    if args.comprehensive_performance:
        # Run comprehensive performance test suite
        print("Running comprehensive performance test suite...")
        try:
            import subprocess
            import sys

            cmd = [sys.executable, "tests/performance/run_performance_tests.py"]

            if args.quick:
                cmd.append("--quick")
            if args.no_load:
                cmd.append("--no-load")

            result = subprocess.run(cmd, capture_output=True, text=True)

            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)

            return {
                "success": result.returncode == 0,
                "return_code": result.returncode,
                "test_type": "comprehensive_performance",
            }

        except Exception as e:
            print(f"Error running comprehensive performance tests: {e}")
            return {
                "success": False,
                "return_code": 1,
                "test_type": "comprehensive_performance",
                "error": str(e),
            }
    else:
        # Run basic pytest performance tests
        pytest_args = [
            "-v",
            "--tb=short",
            "--benchmark-only",
            "--benchmark-sort=mean",
            "-m",
            "performance",
        ]

        if args.verbose:
            pytest_args.append("-vv")

        pytest_args.append("tests/performance/")

        return_code = pytest.main(pytest_args)

        return {"success": return_code == 0, "return_code": return_code, "test_type": "performance"}


def run_security_tests(args) -> Dict[str, Any]:
    """Run security tests."""
    print("\n" + "=" * 60)
    print("RUNNING SECURITY TESTS")
    print("=" * 60)

    # Run bandit security linter
    print("Running Bandit security analysis...")
    bandit_cmd = ["bandit", "-r", "dgm_service/", "-f", "json", "-o", "bandit-report.json"]
    bandit_result = run_command(bandit_cmd)

    # Run safety check
    print("Running Safety dependency check...")
    safety_cmd = ["safety", "check", "--json", "--output", "safety-report.json"]
    safety_result = run_command(safety_cmd)

    # Run security-focused tests
    pytest_args = ["-v", "--tb=short", "-m", "security"]

    if args.verbose:
        pytest_args.append("-vv")

    pytest_args.append("tests/")

    pytest_return_code = pytest.main(pytest_args)

    return {
        "success": (
            bandit_result["success"] and safety_result["success"] and pytest_return_code == 0
        ),
        "return_code": pytest_return_code,
        "test_type": "security",
        "bandit_result": bandit_result,
        "safety_result": safety_result,
    }


def run_code_quality_checks(args) -> Dict[str, Any]:
    """Run code quality checks."""
    print("\n" + "=" * 60)
    print("RUNNING CODE QUALITY CHECKS")
    print("=" * 60)

    results = {}

    # Black formatting check
    print("Checking code formatting with Black...")
    black_cmd = ["black", "--check", "--diff", "dgm_service/", "tests/"]
    results["black"] = run_command(black_cmd)

    # isort import sorting check
    print("Checking import sorting with isort...")
    isort_cmd = ["isort", "--check-only", "--diff", "dgm_service/", "tests/"]
    results["isort"] = run_command(isort_cmd)

    # Flake8 linting
    print("Running Flake8 linting...")
    flake8_cmd = ["flake8", "dgm_service/", "tests/"]
    results["flake8"] = run_command(flake8_cmd)

    # MyPy type checking
    print("Running MyPy type checking...")
    mypy_cmd = ["mypy", "dgm_service/"]
    results["mypy"] = run_command(mypy_cmd)

    all_passed = all(result["success"] for result in results.values())

    return {"success": all_passed, "results": results, "test_type": "code_quality"}


def generate_test_report(results: List[Dict[str, Any]]):
    """Generate comprehensive test report."""
    print("\n" + "=" * 60)
    print("TEST EXECUTION SUMMARY")
    print("=" * 60)

    total_tests = len(results)
    passed_tests = sum(1 for result in results if result["success"])
    failed_tests = total_tests - passed_tests

    print(f"Total test suites: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")

    print("\nDetailed Results:")
    print("-" * 40)

    for result in results:
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        test_type = result.get("test_type", "unknown").upper()
        print(f"{status} {test_type}")

        if not result["success"] and "return_code" in result:
            print(f"    Return code: {result['return_code']}")

    # Coverage information
    if os.path.exists("htmlcov/index.html"):
        print(f"\n📊 Coverage report available at: htmlcov/index.html")

    # Security reports
    if os.path.exists("bandit-report.json"):
        print(f"🔒 Security report available at: bandit-report.json")

    if os.path.exists("safety-report.json"):
        print(f"🛡️  Dependency security report available at: safety-report.json")

    return passed_tests == total_tests


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="DGM Service Test Runner")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument(
        "--constitutional", action="store_true", help="Run constitutional compliance tests only"
    )
    parser.add_argument("--performance", action="store_true", help="Run performance tests only")
    parser.add_argument(
        "--comprehensive-performance",
        action="store_true",
        help="Run comprehensive performance test suite with load testing",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run quick tests (shorter duration for performance tests)",
    )
    parser.add_argument(
        "--no-load", action="store_true", help="Skip load testing in performance tests"
    )
    parser.add_argument("--security", action="store_true", help="Run security tests only")
    parser.add_argument("--quality", action="store_true", help="Run code quality checks only")
    parser.add_argument("--all", action="store_true", help="Run all test suites (default)")
    parser.add_argument(
        "--fast", action="store_true", help="Run tests in fast mode (stop on first failure)"
    )
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--no-setup", action="store_true", help="Skip test environment setup")

    args = parser.parse_args()

    # Change to the service directory
    service_dir = Path(__file__).parent.parent
    os.chdir(service_dir)

    # Setup test environment
    if not args.no_setup:
        if not setup_test_environment():
            sys.exit(1)

    # Determine which tests to run
    run_all = args.all or not any(
        [
            args.unit,
            args.integration,
            args.constitutional,
            args.performance,
            args.security,
            args.quality,
        ]
    )

    results = []

    # Run selected test suites
    if args.unit or run_all:
        results.append(run_unit_tests(args))

    if args.integration or run_all:
        results.append(run_integration_tests(args))

    if args.constitutional or run_all:
        results.append(run_constitutional_tests(args))

    if args.performance or run_all:
        results.append(run_performance_tests(args))

    if args.security or run_all:
        results.append(run_security_tests(args))

    if args.quality or run_all:
        results.append(run_code_quality_checks(args))

    # Generate final report
    all_passed = generate_test_report(results)

    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
