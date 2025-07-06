"""
ACGS Compliance Test Runner

Automated test execution framework for comprehensive compliance validation
including constitutional compliance, multi-tenant isolation, and regulatory standards.

Constitutional Hash: cdd01ef066bc6cf2
"""

import json
import logging
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Constitutional compliance hash
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Test configuration
TEST_SUITES = {
    "constitutional_compliance": {
        "module": "test_constitutional_compliance",
        "description": "Constitutional compliance and formal verification tests",
        "priority": "critical",
        "estimated_duration_minutes": 5,
    },
    "multi_tenant_isolation": {
        "module": "test_multi_tenant_isolation",
        "description": "Multi-tenant data isolation and security boundary tests",
        "priority": "critical",
        "estimated_duration_minutes": 3,
    },
    "regulatory_compliance": {
        "module": "test_regulatory_compliance",
        "description": "SOC2, GDPR, ISO27001 regulatory compliance tests",
        "priority": "high",
        "estimated_duration_minutes": 4,
    },
}


class ComplianceTestRunner:
    """
    Automated compliance test runner for ACGS.

    Executes comprehensive compliance validation tests and generates
    detailed compliance test reports with constitutional verification.
    """

    def __init__(
        self,
        test_directory: str = "/home/dislove/ACGS-2/tests/compliance",
        output_directory: str = "/tmp/compliance_test_results",
    ):
        self.test_directory = Path(test_directory)
        self.output_directory = Path(output_directory)

        # Ensure output directory exists
        self.output_directory.mkdir(parents=True, exist_ok=True)

        # Test execution metadata
        self.test_session = {
            "session_id": f"compliance_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "started_at": datetime.now(timezone.utc),
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "test_suites": TEST_SUITES,
            "results": {},
        }

        logger.info(
            f"Compliance test runner initialized: {self.test_session['session_id']}"
        )

    def run_single_test_suite(self, suite_name: str) -> dict[str, Any]:
        """Run a single compliance test suite."""

        if suite_name not in TEST_SUITES:
            raise ValueError(f"Unknown test suite: {suite_name}")

        suite_config = TEST_SUITES[suite_name]
        test_module = suite_config["module"]

        logger.info(f"Running test suite: {suite_name} ({test_module})")

        # Prepare pytest command
        test_file = self.test_directory / f"{test_module}.py"

        if not test_file.exists():
            logger.error(f"Test file not found: {test_file}")
            return {
                "suite_name": suite_name,
                "status": "failed",
                "error": f"Test file not found: {test_file}",
                "duration_seconds": 0,
                "tests_passed": 0,
                "tests_failed": 1,
                "tests_total": 1,
            }

        # Prepare output files
        junit_output = self.output_directory / f"{suite_name}_junit.xml"
        json_output = self.output_directory / f"{suite_name}_results.json"

        # Build pytest command
        pytest_cmd = [
            sys.executable,
            "-m",
            "pytest",
            str(test_file),
            "-v",
            "--tb=short",
            "--asyncio-mode=auto",
            f"--junitxml={junit_output}",
            f"--json-report={json_output}",
            "--json-report-summary",
        ]

        # Execute tests
        start_time = datetime.now()

        try:
            result = subprocess.run(
                pytest_cmd,
                cwd=self.test_directory,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout
            )

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # Parse results
            test_result = {
                "suite_name": suite_name,
                "module": test_module,
                "description": suite_config["description"],
                "priority": suite_config["priority"],
                "status": "passed" if result.returncode == 0 else "failed",
                "return_code": result.returncode,
                "duration_seconds": duration,
                "started_at": start_time.isoformat(),
                "completed_at": end_time.isoformat(),
                "stdout": result.stdout,
                "stderr": result.stderr,
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }

            # Parse JSON report if available
            if json_output.exists():
                try:
                    with open(json_output) as f:
                        json_report = json.load(f)

                    test_result.update({
                        "tests_passed": json_report.get("summary", {}).get("passed", 0),
                        "tests_failed": json_report.get("summary", {}).get("failed", 0),
                        "tests_skipped": json_report.get("summary", {}).get(
                            "skipped", 0
                        ),
                        "tests_total": json_report.get("summary", {}).get("total", 0),
                        "test_details": json_report.get("tests", []),
                    })
                except Exception as e:
                    logger.warning(f"Failed to parse JSON report: {e}")

            logger.info(f"Test suite {suite_name} completed: {test_result['status']}")
            return test_result

        except subprocess.TimeoutExpired:
            logger.error(f"Test suite {suite_name} timed out")
            return {
                "suite_name": suite_name,
                "status": "timeout",
                "error": "Test execution timed out (10 minutes)",
                "duration_seconds": 600,
                "tests_passed": 0,
                "tests_failed": 1,
                "tests_total": 1,
            }

        except Exception as e:
            logger.error(f"Error running test suite {suite_name}: {e}")
            return {
                "suite_name": suite_name,
                "status": "error",
                "error": str(e),
                "duration_seconds": 0,
                "tests_passed": 0,
                "tests_failed": 1,
                "tests_total": 1,
            }

    def run_all_test_suites(self) -> dict[str, Any]:
        """Run all compliance test suites."""

        logger.info("Starting comprehensive compliance test execution")

        overall_start_time = datetime.now()
        suite_results = {}

        # Run each test suite
        for suite_name in TEST_SUITES:
            suite_result = self.run_single_test_suite(suite_name)
            suite_results[suite_name] = suite_result

        overall_end_time = datetime.now()
        overall_duration = (overall_end_time - overall_start_time).total_seconds()

        # Calculate overall statistics
        total_tests_passed = sum(
            result.get("tests_passed", 0) for result in suite_results.values()
        )
        total_tests_failed = sum(
            result.get("tests_failed", 0) for result in suite_results.values()
        )
        total_tests_skipped = sum(
            result.get("tests_skipped", 0) for result in suite_results.values()
        )
        total_tests = sum(
            result.get("tests_total", 0) for result in suite_results.values()
        )

        # Determine overall status
        critical_suites_failed = [
            name
            for name, result in suite_results.items()
            if TEST_SUITES[name]["priority"] == "critical"
            and result["status"] != "passed"
        ]

        high_priority_suites_failed = [
            name
            for name, result in suite_results.items()
            if TEST_SUITES[name]["priority"] == "high" and result["status"] != "passed"
        ]

        if critical_suites_failed:
            overall_status = "critical_failure"
        elif high_priority_suites_failed:
            overall_status = "high_priority_failure"
        elif total_tests_failed > 0:
            overall_status = "some_failures"
        else:
            overall_status = "all_passed"

        # Compile comprehensive results
        comprehensive_results = {
            "session_id": self.test_session["session_id"],
            "execution_summary": {
                "overall_status": overall_status,
                "started_at": overall_start_time.isoformat(),
                "completed_at": overall_end_time.isoformat(),
                "total_duration_seconds": overall_duration,
                "constitutional_hash": CONSTITUTIONAL_HASH,
            },
            "test_statistics": {
                "total_tests": total_tests,
                "tests_passed": total_tests_passed,
                "tests_failed": total_tests_failed,
                "tests_skipped": total_tests_skipped,
                "pass_rate_percentage": (
                    total_tests_passed / max(total_tests, 1)
                ) * 100,
                "suites_total": len(TEST_SUITES),
                "suites_passed": sum(
                    1
                    for result in suite_results.values()
                    if result["status"] == "passed"
                ),
                "suites_failed": sum(
                    1
                    for result in suite_results.values()
                    if result["status"] != "passed"
                ),
            },
            "compliance_validation": {
                "constitutional_compliance": suite_results.get(
                    "constitutional_compliance", {}
                ).get("status", "unknown"),
                "multi_tenant_isolation": suite_results.get(
                    "multi_tenant_isolation", {}
                ).get("status", "unknown"),
                "regulatory_compliance": suite_results.get(
                    "regulatory_compliance", {}
                ).get("status", "unknown"),
                "constitutional_hash_verified": CONSTITUTIONAL_HASH,
            },
            "suite_results": suite_results,
            "recommendations": self._generate_recommendations(
                suite_results, overall_status
            ),
        }

        # Save comprehensive results
        results_file = (
            self.output_directory
            / f"comprehensive_compliance_results_{self.test_session['session_id']}.json"
        )
        with open(results_file, "w") as f:
            json.dump(comprehensive_results, f, indent=2, default=str)

        logger.info(f"Comprehensive compliance test results saved: {results_file}")
        return comprehensive_results

    def _generate_recommendations(
        self, suite_results: dict[str, Any], overall_status: str
    ) -> list[str]:
        """Generate recommendations based on test results."""

        recommendations = []

        if overall_status == "critical_failure":
            recommendations.append(
                "🚨 CRITICAL: Constitutional compliance or multi-tenant isolation"
                " failures detected"
            )
            recommendations.append(
                "⚠️ Do not deploy to production until critical issues are resolved"
            )

        if overall_status in ["critical_failure", "high_priority_failure"]:
            recommendations.append(
                "📋 Review failed test details and implement necessary fixes"
            )
            recommendations.append(
                "🔍 Run additional security validation before proceeding"
            )

        # Specific recommendations based on suite failures
        for suite_name, result in suite_results.items():
            if result["status"] != "passed":
                if suite_name == "constitutional_compliance":
                    recommendations.append(
                        "🏛️ Constitutional compliance issues: Verify Z3 solver"
                        " integration and formal verification"
                    )
                elif suite_name == "multi_tenant_isolation":
                    recommendations.append(
                        "🔒 Multi-tenant isolation issues: Review tenant boundary"
                        " enforcement"
                    )
                elif suite_name == "regulatory_compliance":
                    recommendations.append(
                        "📊 Regulatory compliance issues: Review SOC2/GDPR/ISO27001"
                        " controls"
                    )

        if overall_status == "all_passed":
            recommendations.extend([
                "✅ All compliance tests passed successfully",
                "🚀 System is ready for production deployment",
                "📈 Consider running performance tests under load",
                "🔄 Schedule regular compliance validation",
            ])

        return recommendations

    def generate_executive_summary(self, results: dict[str, Any]) -> str:
        """Generate executive summary of compliance test results."""

        summary = f"""
# ACGS Compliance Test Executive Summary

**Session ID:** {results['session_id']}
**Constitutional Hash:** {results['execution_summary']['constitutional_hash']}
**Test Completion:** {results['execution_summary']['completed_at']}

## Overall Status: {results['execution_summary']['overall_status'].upper().replace('_', ' ')}

### Key Metrics
- **Total Tests:** {results['test_statistics']['total_tests']}
- **Pass Rate:** {results['test_statistics']['pass_rate_percentage']:.1f}%
- **Duration:** {results['execution_summary']['total_duration_seconds']:.1f} seconds

### Compliance Areas Tested
- **Constitutional Compliance:** {results['compliance_validation']['constitutional_compliance'].upper()}
- **Multi-Tenant Isolation:** {results['compliance_validation']['multi_tenant_isolation'].upper()}
- **Regulatory Standards:** {results['compliance_validation']['regulatory_compliance'].upper()}

### Recommendations
"""
        for rec in results["recommendations"]:
            summary += f"- {rec}\n"

        return summary


# CLI Interface
def main():
    """Main CLI interface for compliance test runner."""

    import argparse

    parser = argparse.ArgumentParser(description="ACGS Compliance Test Runner")
    parser.add_argument(
        "--suite",
        choices=list(TEST_SUITES.keys()) + ["all"],
        default="all",
        help="Test suite to run (default: all)",
    )
    parser.add_argument(
        "--output-dir",
        default="/tmp/compliance_test_results",
        help="Output directory for test results",
    )
    parser.add_argument(
        "--summary", action="store_true", help="Generate executive summary"
    )

    args = parser.parse_args()

    # Initialize test runner
    runner = ComplianceTestRunner(output_directory=args.output_dir)

    # Run tests
    if args.suite == "all":
        results = runner.run_all_test_suites()
    else:
        single_result = runner.run_single_test_suite(args.suite)
        results = {
            "session_id": runner.test_session["session_id"],
            "suite_results": {args.suite: single_result},
            "execution_summary": {"constitutional_hash": CONSTITUTIONAL_HASH},
        }

    # Display results
    print(f"\n{'=' * 80}")
    print("ACGS COMPLIANCE TEST RESULTS")
    print(f"{'=' * 80}")

    if args.suite == "all":
        print(
            f"Overall Status: {results['execution_summary']['overall_status'].upper()}"
        )
        print(
            "Tests Passed:"
            f" {results['test_statistics']['tests_passed']}/{results['test_statistics']['total_tests']}"
        )
        print(f"Pass Rate: {results['test_statistics']['pass_rate_percentage']:.1f}%")
    else:
        single_result = results["suite_results"][args.suite]
        print(f"Suite: {args.suite}")
        print(f"Status: {single_result['status'].upper()}")
        print(f"Duration: {single_result.get('duration_seconds', 0):.1f}s")

    print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")

    # Generate executive summary if requested
    if args.summary and args.suite == "all":
        summary = runner.generate_executive_summary(results)
        print("\n" + summary)

    # Exit with appropriate code
    if args.suite == "all":
        exit_code = (
            0 if results["execution_summary"]["overall_status"] == "all_passed" else 1
        )
    else:
        exit_code = (
            0 if results["suite_results"][args.suite]["status"] == "passed" else 1
        )

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
