#!/usr/bin/env python3
"""
Test Runner for ACGS-PGP v8

Comprehensive test execution with performance validation and reporting.
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run_command(command: str, capture_output: bool = True) -> tuple[int, str, str]:
    """Run shell command and return exit code, stdout, stderr."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=capture_output,
            text=True,
            cwd=Path(__file__).parent,
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)


def run_unit_tests(verbose: bool = False) -> dict:
    """Run unit tests and return results."""
    print("🧪 Running unit tests...")

    cmd = "python -m pytest tests/test_generation_engine.py -m unit"
    if verbose:
        cmd += " -v"
    cmd += " --tb=short"

    exit_code, stdout, stderr = run_command(cmd)

    return {
        "test_type": "unit",
        "exit_code": exit_code,
        "passed": exit_code == 0,
        "output": stdout,
        "errors": stderr,
    }


def run_integration_tests(verbose: bool = False) -> dict:
    """Run integration tests and return results."""
    print("🔗 Running integration tests...")

    cmd = "python -m pytest tests/test_integration.py -m integration"
    if verbose:
        cmd += " -v"
    cmd += " --tb=short"

    exit_code, stdout, stderr = run_command(cmd)

    return {
        "test_type": "integration",
        "exit_code": exit_code,
        "passed": exit_code == 0,
        "output": stdout,
        "errors": stderr,
    }


def run_performance_tests(verbose: bool = False) -> dict:
    """Run performance tests and return results."""
    print("⚡ Running performance tests...")

    cmd = "python -m pytest tests/test_performance.py -m performance"
    if verbose:
        cmd += " -v"
    cmd += " --tb=short"

    exit_code, stdout, stderr = run_command(cmd)

    return {
        "test_type": "performance",
        "exit_code": exit_code,
        "passed": exit_code == 0,
        "output": stdout,
        "errors": stderr,
    }


def run_coverage_tests() -> dict:
    """Run tests with coverage reporting."""
    print("📊 Running tests with coverage...")

    cmd = "python -m pytest tests/ --cov=src --cov-report=term-missing --cov-report=html:htmlcov"

    exit_code, stdout, stderr = run_command(cmd)

    return {
        "test_type": "coverage",
        "exit_code": exit_code,
        "passed": exit_code == 0,
        "output": stdout,
        "errors": stderr,
    }


def validate_performance_targets(test_results: list) -> dict:
    """Validate that performance targets are met."""
    print("🎯 Validating performance targets...")

    performance_validation = {
        "response_time_target": {"target": 500, "actual": None, "passed": False},
        "cache_hit_rate_target": {"target": 70, "actual": None, "passed": False},
        "compliance_score_target": {"target": 80, "actual": None, "passed": False},
        "concurrent_requests_target": {"target": 10, "actual": None, "passed": False},
    }

    # Extract performance metrics from test output
    for result in test_results:
        if result["test_type"] == "performance" and result["passed"]:
            output = result["output"]

            # Parse performance metrics from output
            # This is a simplified parser - in production, you'd use structured output
            if "Average response time:" in output:
                try:
                    line = [
                        l for l in output.split("\n") if "Average response time:" in l
                    ][0]
                    actual_time = float(line.split(":")[1].strip().replace("ms", ""))
                    performance_validation["response_time_target"][
                        "actual"
                    ] = actual_time
                    performance_validation["response_time_target"]["passed"] = (
                        actual_time <= 500
                    )
                except:
                    pass

            if "Throughput:" in output:
                try:
                    line = [l for l in output.split("\n") if "Throughput:" in l][0]
                    actual_throughput = float(line.split(":")[1].strip().split()[0])
                    performance_validation["concurrent_requests_target"][
                        "actual"
                    ] = actual_throughput
                    performance_validation["concurrent_requests_target"]["passed"] = (
                        actual_throughput >= 5
                    )
                except:
                    pass

    # Overall performance validation
    all_targets_met = all(
        target["passed"]
        for target in performance_validation.values()
        if target["actual"] is not None
    )

    performance_validation["overall_passed"] = all_targets_met

    return performance_validation


def generate_test_report(test_results: list, performance_validation: dict) -> dict:
    """Generate comprehensive test report."""
    report = {
        "timestamp": datetime.now().isoformat(),
        "constitutional_hash": "cdd01ef066bc6cf2",
        "service": "acgs-pgp-v8",
        "version": "8.0.0",
        "test_summary": {
            "total_test_suites": len(test_results),
            "passed_test_suites": sum(1 for r in test_results if r["passed"]),
            "failed_test_suites": sum(1 for r in test_results if not r["passed"]),
            "overall_passed": all(r["passed"] for r in test_results),
        },
        "test_results": test_results,
        "performance_validation": performance_validation,
        "recommendations": [],
    }

    # Add recommendations based on results
    if not report["test_summary"]["overall_passed"]:
        report["recommendations"].append("Fix failing tests before deployment")

    if not performance_validation.get("overall_passed", False):
        report["recommendations"].append("Address performance issues before production")

    if report["test_summary"]["overall_passed"] and performance_validation.get(
        "overall_passed", False
    ):
        report["recommendations"].append("All tests passed - ready for deployment")

    return report


def save_test_report(report: dict, output_file: str = "test_report.json"):
    """Save test report to file."""
    output_path = Path(__file__).parent / "reports" / output_file
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"📄 Test report saved to: {output_path}")


def print_test_summary(report: dict):
    """Print test summary to console."""
    print("\n" + "=" * 60)
    print("🎉 ACGS-PGP v8 Test Summary")
    print("=" * 60)

    summary = report["test_summary"]
    print(f"Total test suites: {summary['total_test_suites']}")
    print(f"Passed: {summary['passed_test_suites']}")
    print(f"Failed: {summary['failed_test_suites']}")
    print(
        f"Overall status: {'✅ PASSED' if summary['overall_passed'] else '❌ FAILED'}"
    )

    print("\n📊 Performance Validation:")
    perf = report["performance_validation"]
    for target_name, target_data in perf.items():
        if target_name != "overall_passed" and target_data.get("actual") is not None:
            status = "✅" if target_data["passed"] else "❌"
            print(
                f"  {status} {target_name}: {target_data['actual']} (target: {target_data['target']})"
            )

    print(
        f"\nPerformance targets: {'✅ MET' if perf.get('overall_passed', False) else '❌ NOT MET'}"
    )

    if report["recommendations"]:
        print("\n💡 Recommendations:")
        for rec in report["recommendations"]:
            print(f"  • {rec}")

    print("=" * 60)


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="ACGS-PGP v8 Test Runner")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument(
        "--integration", action="store_true", help="Run integration tests only"
    )
    parser.add_argument(
        "--performance", action="store_true", help="Run performance tests only"
    )
    parser.add_argument(
        "--coverage", action="store_true", help="Run tests with coverage"
    )
    parser.add_argument("--all", action="store_true", help="Run all test suites")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--report", default="test_report.json", help="Output report file"
    )

    args = parser.parse_args()

    # Default to running all tests if no specific test type is specified
    if not any([args.unit, args.integration, args.performance, args.coverage]):
        args.all = True

    print("🚀 Starting ACGS-PGP v8 Test Suite")
    print("Constitutional Hash: cdd01ef066bc6cf2")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("-" * 60)

    test_results = []

    try:
        # Run selected test suites
        if args.unit or args.all:
            test_results.append(run_unit_tests(args.verbose))

        if args.integration or args.all:
            test_results.append(run_integration_tests(args.verbose))

        if args.performance or args.all:
            test_results.append(run_performance_tests(args.verbose))

        if args.coverage:
            test_results.append(run_coverage_tests())

        # Validate performance targets
        performance_validation = validate_performance_targets(test_results)

        # Generate and save report
        report = generate_test_report(test_results, performance_validation)
        save_test_report(report, args.report)

        # Print summary
        print_test_summary(report)

        # Exit with appropriate code
        overall_success = report["test_summary"][
            "overall_passed"
        ] and performance_validation.get("overall_passed", True)

        sys.exit(0 if overall_success else 1)

    except KeyboardInterrupt:
        print("\n⚠️ Test execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
