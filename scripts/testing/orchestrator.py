#!/usr/bin/env python3
"""
ACGS Unified Test Orchestrator
Constitutional Hash: cdd01ef066bc6cf2

Comprehensive test orchestrator that consolidates all test runners into a single,
unified framework with consistent configuration and reporting.
"""

import argparse
import asyncio
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import HTTPClient, get_config, get_logger
from core.utils import format_duration

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


@dataclass
class TestSuiteConfig:
    """Configuration for test suite execution."""

    name: str
    description: str
    command: list[str]
    timeout: int = 300
    required_files: list[Path] = field(default_factory=list)
    environment_vars: dict[str, str] = field(default_factory=dict)
    markers: list[str] = field(default_factory=list)
    coverage_enabled: bool = False
    critical: bool = False  # If True, failure stops entire test run


@dataclass
class TestResult:
    """Result of a test suite execution."""

    suite_name: str
    success: bool
    duration_ms: float
    exit_code: int
    stdout: str = ""
    stderr: str = ""
    coverage_data: Optional[dict[str, Any]] = None
    metrics: dict[str, Any] = field(default_factory=dict)
    constitutional_hash: str = CONSTITUTIONAL_HASH

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "suite_name": self.suite_name,
            "success": self.success,
            "duration_ms": self.duration_ms,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "coverage_data": self.coverage_data,
            "metrics": self.metrics,
            "constitutional_hash": self.constitutional_hash,
        }


@dataclass
class TestOrchestrationResult:
    """Overall result of test orchestration."""

    total_suites: int
    passed_suites: int
    failed_suites: int
    skipped_suites: int
    total_duration_ms: float
    success_rate: float
    results: list[TestResult] = field(default_factory=list)
    constitutional_hash: str = CONSTITUTIONAL_HASH

    @property
    def overall_success(self) -> bool:
        """Check if all tests passed."""
        return self.failed_suites == 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_suites": self.total_suites,
            "passed_suites": self.passed_suites,
            "failed_suites": self.failed_suites,
            "skipped_suites": self.skipped_suites,
            "total_duration_ms": self.total_duration_ms,
            "success_rate": self.success_rate,
            "overall_success": self.overall_success,
            "results": [r.to_dict() for r in self.results],
            "constitutional_hash": self.constitutional_hash,
        }


class ACGSTestOrchestrator:
    """Unified test orchestrator for all ACGS test suites."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = get_logger("test-orchestrator")
        self.test_suites: list[TestSuiteConfig] = []
        self.results: list[TestResult] = []

    def register_standard_suites(self) -> None:
        """Register all standard ACGS test suites."""

        # Constitutional Compliance Tests
        self.test_suites.append(
            TestSuiteConfig(
                name="constitutional_compliance",
                description="Constitutional compliance validation across all services",
                command=[
                    sys.executable,
                    "-m",
                    "pytest",
                    "-v",
                    "-m",
                    "constitutional",
                    "--tb=short",
                    "--json-report",
                    "--json-report-file=reports/constitutional-report.json",
                ],
                timeout=300,
                markers=["constitutional"],
                critical=True,
            )
        )

        # Unit Tests with Coverage
        self.test_suites.append(
            TestSuiteConfig(
                name="unit_tests",
                description="Unit tests with comprehensive coverage analysis",
                command=[
                    sys.executable,
                    "-m",
                    "pytest",
                    "-v",
                    "-m",
                    "unit",
                    "--cov=services",
                    "--cov=scripts",
                    "--cov-report=json:reports/unit-coverage.json",
                    "--cov-report=html:reports/unit-coverage-html",
                    "--cov-report=term-missing",
                    "--tb=short",
                    "--json-report",
                    "--json-report-file=reports/unit-report.json",
                ],
                timeout=900,
                markers=["unit"],
                coverage_enabled=True,
            )
        )

        # Integration Tests
        self.test_suites.append(
            TestSuiteConfig(
                name="integration_tests",
                description="Service integration and communication tests",
                command=[
                    sys.executable,
                    "-m",
                    "pytest",
                    "-v",
                    "-m",
                    "integration",
                    "--tb=short",
                    "--json-report",
                    "--json-report-file=reports/integration-report.json",
                ],
                timeout=1200,
                markers=["integration"],
            )
        )

        # Performance Tests
        self.test_suites.append(
            TestSuiteConfig(
                name="performance_tests",
                description="Performance benchmarks and latency validation",
                command=[
                    sys.executable,
                    "-m",
                    "pytest",
                    "-v",
                    "-m",
                    "performance",
                    "--benchmark-only",
                    "--benchmark-sort=mean",
                    "--benchmark-json=reports/benchmark-results.json",
                    "--tb=short",
                ],
                timeout=1800,
                markers=["performance"],
            )
        )

        # Security Tests
        self.test_suites.append(
            TestSuiteConfig(
                name="security_tests",
                description="Security hardening and vulnerability tests",
                command=[
                    sys.executable,
                    "-m",
                    "pytest",
                    "-v",
                    "-m",
                    "security",
                    "--tb=short",
                    "--json-report",
                    "--json-report-file=reports/security-report.json",
                ],
                timeout=600,
                markers=["security"],
            )
        )

        # Multi-Tenant Tests
        self.test_suites.append(
            TestSuiteConfig(
                name="multi_tenant_tests",
                description="Multi-tenant isolation and security tests",
                command=[
                    sys.executable,
                    "-m",
                    "pytest",
                    "-v",
                    "-m",
                    "multi_tenant",
                    "--tb=short",
                    "--json-report",
                    "--json-report-file=reports/multi-tenant-report.json",
                ],
                timeout=900,
                markers=["multi_tenant"],
            )
        )

        # E2E Tests
        self.test_suites.append(
            TestSuiteConfig(
                name="e2e_tests",
                description="End-to-end workflow and integration tests",
                command=[
                    sys.executable,
                    "-m",
                    "pytest",
                    "tests/e2e/",
                    "-v",
                    "--tb=short",
                    "--json-report",
                    "--json-report-file=reports/e2e-report.json",
                ],
                timeout=1800,
                required_files=[Path("tests/e2e")],
            )
        )

    def register_custom_suite(self, suite: TestSuiteConfig) -> None:
        """Register a custom test suite."""
        self.test_suites.append(suite)
        self.logger.info(f"Registered custom test suite: {suite.name}")

    async def check_service_availability(self) -> dict[str, bool]:
        """Check which ACGS services are available for testing."""
        config = get_config()
        service_status = {}

        self.logger.info("Checking service availability...")

        async with HTTPClient(validate_constitutional_compliance=False) as client:
            services = config.get_all_services()

            for service in services:
                try:
                    response = await client.get(service.health_url, timeout=5.0)
                    service_status[service.name] = response.status == 200
                    status = "✅" if service_status[service.name] else "❌"
                    self.logger.info(f"  {status} {service.name}")
                except Exception as e:
                    service_status[service.name] = False
                    self.logger.warning(f"  ❌ {service.name}: {e}")

        available_count = sum(1 for available in service_status.values() if available)
        total_count = len(service_status)
        self.logger.info(
            f"Service availability: {available_count}/{total_count} services available"
        )

        return service_status

    async def run_test_suite(self, suite: TestSuiteConfig) -> TestResult:
        """Run a single test suite."""
        self.logger.info(f"Running test suite: {suite.name}")
        self.logger.info(f"Description: {suite.description}")

        # Check required files
        for required_file in suite.required_files:
            full_path = self.project_root / required_file
            if not full_path.exists():
                self.logger.warning(f"Required file missing: {full_path}")
                return TestResult(
                    suite_name=suite.name,
                    success=False,
                    duration_ms=0.0,
                    exit_code=-1,
                    stderr=f"Required file missing: {full_path}",
                )

        # Prepare environment
        env = os.environ.copy()
        env.update(suite.environment_vars)
        env.update({
            "ACGS_CONSTITUTIONAL_HASH": CONSTITUTIONAL_HASH,
            "PYTHONPATH": str(self.project_root),
            "ACGS_ENVIRONMENT": "test",
        })

        # Create reports directory
        reports_dir = self.project_root / "reports"
        reports_dir.mkdir(exist_ok=True)

        start_time = time.time()

        try:
            self.logger.debug(f"Executing command: {' '.join(suite.command)}")

            # Run the test suite
            result = subprocess.run(
                suite.command,
                cwd=self.project_root,
                env=env,
                capture_output=True,
                text=True,
                timeout=suite.timeout,
            )

            duration_ms = (time.time() - start_time) * 1000
            success = result.returncode == 0

            # Parse coverage data if available
            coverage_data = None
            if suite.coverage_enabled:
                coverage_file = (
                    reports_dir / f"{suite.name.replace('_', '-')}-coverage.json"
                )
                if coverage_file.exists():
                    try:
                        with open(coverage_file) as f:
                            coverage_data = json.load(f)
                    except Exception as e:
                        self.logger.warning(f"Failed to parse coverage data: {e}")

            # Extract metrics from output
            metrics = self._extract_metrics(result.stdout, suite)

            test_result = TestResult(
                suite_name=suite.name,
                success=success,
                duration_ms=duration_ms,
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                coverage_data=coverage_data,
                metrics=metrics,
            )

            status = "✅ PASSED" if success else "❌ FAILED"
            self.logger.info(f"{status} {suite.name} ({duration_ms:.0f}ms)")

            return test_result

        except subprocess.TimeoutExpired:
            duration_ms = (time.time() - start_time) * 1000
            self.logger.error(f"Test suite timed out: {suite.name}")

            return TestResult(
                suite_name=suite.name,
                success=False,
                duration_ms=duration_ms,
                exit_code=-1,
                stderr=f"Test suite timed out after {suite.timeout} seconds",
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.logger.error(f"Test suite failed: {suite.name}", error=e)

            return TestResult(
                suite_name=suite.name,
                success=False,
                duration_ms=duration_ms,
                exit_code=-1,
                stderr=str(e),
            )

    def _extract_metrics(self, output: str, suite: TestSuiteConfig) -> dict[str, Any]:
        """Extract metrics from test output."""
        metrics = {}

        # Extract pytest metrics
        lines = output.split("\n")
        for line in lines:
            if " passed" in line or " failed" in line:
                # Parse pytest result line
                if "passed" in line:
                    try:
                        passed = int(line.split()[0])
                        metrics["tests_passed"] = passed
                    except (ValueError, IndexError):
                        pass

                if "failed" in line:
                    try:
                        failed = int(line.split()[0])
                        metrics["tests_failed"] = failed
                    except (ValueError, IndexError):
                        pass

        # Extract coverage percentage
        if suite.coverage_enabled:
            for line in lines:
                if "TOTAL" in line and "%" in line:
                    try:
                        # Extract coverage percentage from coverage report
                        parts = line.split()
                        for part in parts:
                            if part.endswith("%"):
                                coverage = float(part.rstrip("%"))
                                metrics["coverage_percentage"] = coverage
                                break
                    except ValueError:
                        pass

        # Extract benchmark data
        if "benchmark" in suite.name.lower():
            # Look for benchmark timing information
            for line in lines:
                if "ms" in line.lower() and any(
                    word in line.lower() for word in ["mean", "min", "max"]
                ):
                    metrics["benchmark_line"] = line.strip()
                    break

        return metrics

    async def run_all_suites(
        self,
        suite_filter: Optional[list[str]] = None,
        fail_fast: bool = False,
        parallel: bool = False,
    ) -> TestOrchestrationResult:
        """Run all or filtered test suites."""

        self.logger.info("Starting ACGS Test Orchestration")
        self.logger.info(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
        self.logger.info(f"Project Root: {self.project_root}")

        # Filter suites if specified
        suites_to_run = self.test_suites
        if suite_filter:
            suites_to_run = [s for s in self.test_suites if s.name in suite_filter]
            self.logger.info(
                f"Running filtered suites: {[s.name for s in suites_to_run]}"
            )

        # Check service availability first
        service_status = await self.check_service_availability()

        start_time = time.time()
        results = []
        skipped_count = 0

        if parallel and len(suites_to_run) > 1:
            # Run suites in parallel (non-critical ones only)
            non_critical = [s for s in suites_to_run if not s.critical]
            critical = [s for s in suites_to_run if s.critical]

            # Run critical suites first (sequentially)
            for suite in critical:
                result = await self.run_test_suite(suite)
                results.append(result)

                if fail_fast and not result.success:
                    self.logger.error(
                        f"Critical test suite failed, stopping: {suite.name}"
                    )
                    break

            # Run non-critical suites in parallel if no critical failures
            if not fail_fast or all(r.success for r in results):
                if non_critical:
                    self.logger.info(
                        f"Running {len(non_critical)} non-critical suites in parallel"
                    )
                    tasks = [self.run_test_suite(suite) for suite in non_critical]
                    parallel_results = await asyncio.gather(
                        *tasks, return_exceptions=True
                    )

                    for result in parallel_results:
                        if isinstance(result, Exception):
                            self.logger.error(f"Parallel test failed: {result}")
                        else:
                            results.append(result)
        else:
            # Run suites sequentially
            for suite in suites_to_run:
                result = await self.run_test_suite(suite)
                results.append(result)

                if fail_fast and not result.success and suite.critical:
                    self.logger.error(
                        f"Critical test suite failed, stopping: {suite.name}"
                    )
                    break

        total_duration_ms = (time.time() - start_time) * 1000

        # Calculate summary statistics
        total_suites = len(results)
        passed_suites = sum(1 for r in results if r.success)
        failed_suites = total_suites - passed_suites
        success_rate = (passed_suites / total_suites * 100) if total_suites > 0 else 0.0

        orchestration_result = TestOrchestrationResult(
            total_suites=total_suites,
            passed_suites=passed_suites,
            failed_suites=failed_suites,
            skipped_suites=skipped_count,
            total_duration_ms=total_duration_ms,
            success_rate=success_rate,
            results=results,
        )

        # Log summary
        self.logger.info("Test Orchestration Complete")
        self.logger.info(
            f"Total: {total_suites}, Passed: {passed_suites}, Failed: {failed_suites}"
        )
        self.logger.info(f"Success Rate: {success_rate:.1f}%")
        self.logger.info(f"Duration: {format_duration(total_duration_ms / 1000)}")

        if orchestration_result.overall_success:
            self.logger.success("🎉 All test suites passed!")
        else:
            self.logger.error(f"❌ {failed_suites} test suite(s) failed")

        return orchestration_result

    def save_report(self, result: TestOrchestrationResult, output_path: Path) -> None:
        """Save comprehensive test report."""

        # Ensure reports directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            report_data = {
                "timestamp": datetime.now().isoformat(),
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "orchestration_result": result.to_dict(),
                "environment": {
                    "project_root": str(self.project_root),
                    "python_version": sys.version,
                    "platform": sys.platform,
                },
            }

            with open(output_path, "w") as f:
                json.dump(report_data, f, indent=2, default=str)

            self.logger.success(f"Test report saved: {output_path}")

        except Exception as e:
            self.logger.error(f"Failed to save test report: {e}")

    def print_summary(self, result: TestOrchestrationResult) -> None:
        """Print detailed test summary to console."""
        print("\n" + "=" * 80)
        print("🧪 ACGS TEST ORCHESTRATION SUMMARY")
        print("=" * 80)
        print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
        print(f"Duration: {format_duration(result.total_duration_ms / 1000)}")
        print(f"Success Rate: {result.success_rate:.1f}%")
        print(
            f"Overall Status: {'✅ PASSED' if result.overall_success else '❌ FAILED'}"
        )
        print("=" * 80)

        # Individual suite results
        for test_result in result.results:
            status = "✅ PASS" if test_result.success else "❌ FAIL"
            duration = format_duration(test_result.duration_ms / 1000)
            print(f"{status} {test_result.suite_name} ({duration})")

            # Show key metrics
            if test_result.metrics:
                metrics_str = []
                for key, value in test_result.metrics.items():
                    if key == "coverage_percentage":
                        metrics_str.append(f"Coverage: {value:.1f}%")
                    elif key in ["tests_passed", "tests_failed"]:
                        metrics_str.append(f"{key.replace('_', ' ').title()}: {value}")

                if metrics_str:
                    print(f"    {', '.join(metrics_str)}")

            # Show errors for failed tests
            if not test_result.success and test_result.stderr:
                error_lines = test_result.stderr.split("\n")
                # Show first few lines of error
                for line in error_lines[:3]:
                    if line.strip():
                        print(f"    ❌ {line.strip()}")
                if len(error_lines) > 3:
                    print("    ... (see full report for details)")

            print()

        print("=" * 80)

        if result.overall_success:
            print("🎉 ALL TESTS PASSED - SYSTEM READY FOR DEPLOYMENT")
        else:
            print("❌ SOME TESTS FAILED - REVIEW ISSUES BEFORE DEPLOYMENT")

        print("=" * 80 + "\n")


async def main():
    """Main entry point for test orchestrator."""
    parser = argparse.ArgumentParser(
        description="ACGS Unified Test Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  {sys.argv[0]} --all                        # Run all test suites
  {sys.argv[0]} --suites unit_tests performance_tests  # Run specific suites
  {sys.argv[0]} --parallel --fail-fast      # Run in parallel, stop on critical failure
  {sys.argv[0]} --output reports/test-results.json     # Save to custom location

Constitutional Hash: {CONSTITUTIONAL_HASH}
        """,
    )

    # Suite selection
    suite_group = parser.add_mutually_exclusive_group()
    suite_group.add_argument("--all", action="store_true", help="Run all test suites")
    suite_group.add_argument("--suites", nargs="+", help="Specific test suites to run")

    # Execution options
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Run non-critical test suites in parallel",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop on first critical test suite failure",
    )

    # Output options
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports/test-orchestration-results.json"),
        help="Output file for test results",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Quiet output (errors only)"
    )

    # Project configuration
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="ACGS project root directory",
    )

    args = parser.parse_args()

    # Set up logging
    log_level = "DEBUG" if args.verbose else "ERROR" if args.quiet else "INFO"
    logger = get_logger("orchestrator-main", level=log_level)

    # Validate project root
    if not args.project_root.exists():
        logger.error(f"Project root does not exist: {args.project_root}")
        sys.exit(1)

    # Initialize orchestrator
    orchestrator = ACGSTestOrchestrator(args.project_root)
    orchestrator.register_standard_suites()

    # Determine which suites to run
    suite_filter = None
    if args.suites:
        suite_filter = args.suites
        available_suites = [s.name for s in orchestrator.test_suites]
        invalid_suites = [s for s in suite_filter if s not in available_suites]
        if invalid_suites:
            logger.error(f"Invalid test suites: {invalid_suites}")
            logger.error(f"Available suites: {available_suites}")
            sys.exit(1)
    elif not args.all:
        logger.error("Must specify --all or --suites")
        sys.exit(1)

    try:
        # Run test orchestration
        result = await orchestrator.run_all_suites(
            suite_filter=suite_filter, fail_fast=args.fail_fast, parallel=args.parallel
        )

        # Save and display results
        orchestrator.save_report(result, args.output)
        orchestrator.print_summary(result)

        # Exit with appropriate code
        sys.exit(0 if result.overall_success else 1)

    except KeyboardInterrupt:
        logger.warning("Test orchestration interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Test orchestration failed: {e}")
        if args.verbose:
            import traceback

            logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
