#!/usr/bin/env python3
"""
ACGS E2E Test Runner with Service Coverage

This script runs E2E tests with appropriate coverage configuration for service testing.
It distinguishes between framework testing (no coverage) and service integration testing (with coverage).
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional


class E2ETestRunner:
    """Enhanced E2E test runner with coverage options."""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()
        self.e2e_dir = self.project_root / "tests/e2e"

    def run_tests(
        self,
        test_mode: str = "offline",
        test_suite: str = "all",
        coverage_mode: str = "none",
        markers: Optional[List[str]] = None,
        verbose: bool = True,
        max_failures: int = 10,
        timeout: int = 300,
    ) -> bool:
        """Run E2E tests with specified configuration."""

        print(f"🚀 Running ACGS E2E Tests")
        print(f"Mode: {test_mode}, Suite: {test_suite}, Coverage: {coverage_mode}")
        print("=" * 60)

        # Build pytest command
        cmd = self._build_pytest_command(
            test_mode=test_mode,
            test_suite=test_suite,
            coverage_mode=coverage_mode,
            markers=markers,
            verbose=verbose,
            max_failures=max_failures,
            timeout=timeout,
        )

        # Set environment variables
        env = self._setup_environment(test_mode)

        # Run the command
        print(f"Command: {' '.join(cmd)}")
        print()

        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                env=env,
                timeout=timeout * 2,  # Allow extra time for setup
            )

            success = result.returncode == 0
            if success:
                print("\n✅ E2E tests completed successfully!")
            else:
                print(f"\n❌ E2E tests failed with exit code {result.returncode}")

            return success

        except subprocess.TimeoutExpired:
            print(f"\n⏰ Tests timed out after {timeout * 2} seconds")
            return False
        except Exception as e:
            print(f"\n💥 Error running tests: {e}")
            return False

    def _build_pytest_command(
        self,
        test_mode: str,
        test_suite: str,
        coverage_mode: str,
        markers: Optional[List[str]],
        verbose: bool,
        max_failures: int,
        timeout: int,
    ) -> List[str]:
        """Build the pytest command with appropriate options."""

        cmd = ["python", "-m", "pytest", "tests/e2e/tests/"]

        # Basic options
        if verbose:
            cmd.append("-v")

        cmd.extend(["--tb=short", f"--maxfail={max_failures}", f"--timeout={timeout}"])

        # Test suite selection
        if test_suite != "all":
            if markers:
                markers.append(test_suite)
            else:
                markers = [test_suite]

        # Marker filtering
        if markers:
            marker_expr = " or ".join(markers)
            cmd.extend(["-m", marker_expr])

        # Coverage configuration
        if coverage_mode == "services":
            cmd.extend(
                [
                    "--cov=services",
                    "--cov-report=xml:reports/e2e-service-coverage.xml",
                    "--cov-report=term-missing",
                    "--cov-report=html:reports/e2e-service-coverage-html",
                ]
            )
        elif coverage_mode == "framework":
            cmd.extend(
                [
                    "--cov=tests/e2e/framework",
                    "--cov-report=xml:reports/e2e-framework-coverage.xml",
                    "--cov-report=term-missing",
                ]
            )
        # coverage_mode == "none" adds no coverage options

        # Output options
        cmd.extend(["--junitxml=reports/e2e-test-results.xml"])

        return cmd

    def _setup_environment(self, test_mode: str) -> Dict[str, str]:
        """Setup environment variables for test execution."""
        env = os.environ.copy()

        # Core E2E configuration
        env.update(
            {
                "E2E_TEST_MODE": test_mode,
                "CONSTITUTIONAL_HASH": "cdd01ef066bc6cf2",
                "PYTHONPATH": str(self.project_root),
            }
        )

        # Test-specific configuration
        if test_mode == "offline":
            env.update(
                {
                    "POSTGRES_HOST": "localhost",
                    "POSTGRES_PORT": "5439",
                    "REDIS_HOST": "localhost",
                    "REDIS_PORT": "6389",
                }
            )
        elif test_mode == "online":
            # Use actual service endpoints
            env.update(
                {
                    "AUTH_SERVICE_URL": "http://localhost:8016",
                    "CONSTITUTIONAL_AI_URL": "http://localhost:8001",
                    "POLICY_GOVERNANCE_URL": "http://localhost:8005",
                    "GOVERNANCE_SYNTHESIS_URL": "http://localhost:8004",
                }
            )

        return env

    def validate_environment(self) -> bool:
        """Validate that the test environment is properly configured."""
        print("🔍 Validating E2E test environment...")

        # Check required directories
        required_dirs = [
            self.e2e_dir,
            self.e2e_dir / "tests",
            self.e2e_dir / "framework",
        ]

        for dir_path in required_dirs:
            if not dir_path.exists():
                print(f"❌ Missing required directory: {dir_path}")
                return False

        # Check pytest configuration
        pytest_ini = self.e2e_dir / "config/environments/pytest.ini"
        if not pytest_ini.exists():
            print(f"❌ Missing pytest configuration: {pytest_ini}")
            return False

        # Create reports directory
        reports_dir = self.project_root / "reports"
        reports_dir.mkdir(exist_ok=True)

        print("✅ Environment validation passed")
        return True


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="ACGS E2E Test Runner with Coverage")

    parser.add_argument(
        "--mode",
        choices=["offline", "online", "hybrid"],
        default="offline",
        help="Test execution mode",
    )

    parser.add_argument(
        "--suite",
        choices=[
            "all",
            "smoke",
            "constitutional",
            "performance",
            "security",
            "integration",
        ],
        default="all",
        help="Test suite to run",
    )

    parser.add_argument(
        "--coverage",
        choices=["none", "services", "framework"],
        default="none",
        help="Coverage measurement mode",
    )

    parser.add_argument(
        "--markers", nargs="*", help="Additional pytest markers to include"
    )

    parser.add_argument(
        "--timeout", type=int, default=300, help="Test timeout in seconds"
    )

    parser.add_argument(
        "--max-failures",
        type=int,
        default=10,
        help="Maximum number of test failures before stopping",
    )

    parser.add_argument("--quiet", action="store_true", help="Reduce output verbosity")

    args = parser.parse_args()

    # Initialize runner
    runner = E2ETestRunner()

    # Validate environment
    if not runner.validate_environment():
        print("❌ Environment validation failed")
        sys.exit(1)

    # Run tests
    success = runner.run_tests(
        test_mode=args.mode,
        test_suite=args.suite,
        coverage_mode=args.coverage,
        markers=args.markers,
        verbose=not args.quiet,
        max_failures=args.max_failures,
        timeout=args.timeout,
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
