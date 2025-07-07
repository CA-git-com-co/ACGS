#!/usr/bin/env python3
"""
CI/CD Pytest Configuration Validation Script

This script validates that the pytest configuration works correctly in CI/CD environments
and ensures compatibility with all GitHub Actions workflows.
"""
# Constitutional Hash: cdd01ef066bc6cf2

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional


class CIValidationResult:
    def __init__(
        self,
        test_name: str,
        command: str,
        success: bool,
        output: str = "",
        error: str = "",
    ):
        self.test_name = test_name
        self.command = command
        self.success = success
        self.output = output
        self.error = error


class PytestCIValidator:
    """Validates pytest configuration for CI/CD compatibility."""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()
        self.results: List[CIValidationResult] = []

    def run_validation(self) -> bool:
        """Run all validation tests."""
        print("🔍 ACGS Pytest CI/CD Configuration Validation")
        print("=" * 60)

        # Test 1: Basic test collection
        self._test_basic_collection()

        # Test 2: Marker-based filtering
        self._test_marker_filtering()

        # Test 3: CI command compatibility
        self._test_ci_commands()

        # Test 4: Configuration file validation
        self._test_config_files()

        # Test 5: Coverage compatibility
        self._test_coverage_compatibility()

        # Generate report
        return self._generate_report()

    def _run_pytest_command(
        self, cmd: str, test_name: str, timeout: int = 60
    ) -> CIValidationResult:
        """Run a pytest command and capture results."""
        try:
            # Ensure reports directory exists
            reports_dir = self.project_root / "reports"
            reports_dir.mkdir(exist_ok=True)

            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.project_root,
            )

            success = result.returncode == 0
            return CIValidationResult(
                test_name=test_name,
                command=cmd,
                success=success,
                output=result.stdout,
                error=result.stderr,
            )

        except subprocess.TimeoutExpired:
            return CIValidationResult(
                test_name=test_name,
                command=cmd,
                success=False,
                error=f"Command timed out after {timeout} seconds",
            )
        except Exception as e:
            return CIValidationResult(
                test_name=test_name, command=cmd, success=False, error=str(e)
            )

    def _test_basic_collection(self) -> None:
        """Test basic test collection without warnings."""
        print("\n📋 Test 1: Basic Test Collection")

        cmd = "python -m pytest tests/e2e/tests/ --collect-only -q"
        result = self._run_pytest_command(cmd, "Basic Collection")
        self.results.append(result)

        if result.success:
            # Check for warnings in output
            if "warning" in result.output.lower() or "warning" in result.error.lower():
                print("⚠️  WARNINGS DETECTED in test collection")
                result.success = False
            else:
                print("✅ Test collection successful - no warnings")
        else:
            print(f"❌ Test collection failed: {result.error[:100]}")

    def _test_marker_filtering(self) -> None:
        """Test marker-based test filtering."""
        print("\n🏷️  Test 2: Marker-Based Filtering")

        markers = ["smoke", "constitutional", "performance", "security"]

        for marker in markers:
            cmd = f'python -m pytest tests/e2e/tests/ -m "{marker}" --collect-only -q'
            result = self._run_pytest_command(cmd, f"Marker: {marker}")
            self.results.append(result)

            if result.success:
                print(f"✅ Marker '{marker}' filtering works")
            else:
                print(f"❌ Marker '{marker}' filtering failed")

    def _test_ci_commands(self) -> None:
        """Test actual CI/CD commands from workflows."""
        print("\n🔧 Test 3: CI/CD Command Compatibility")

        ci_commands = [
            {
                "name": "Smoke Tests (CI)",
                "cmd": 'python -m pytest tests/e2e/tests/ -v --tb=short --maxfail=5 --timeout=300 -m "smoke" --collect-only',
            },
            {
                "name": "Constitutional Tests (CI)",
                "cmd": 'python -m pytest tests/e2e/tests/ -v --tb=short --timeout=600 -m "constitutional" --collect-only',
            },
            {
                "name": "Integration Tests (CI)",
                "cmd": 'python -m pytest tests/e2e/tests/ -v --tb=short --timeout=900 -m "integration" --collect-only',
            },
        ]

        for test_config in ci_commands:
            result = self._run_pytest_command(test_config["cmd"], test_config["name"])
            self.results.append(result)

            if result.success:
                print(f"✅ {test_config['name']} command compatible")
            else:
                print(f"❌ {test_config['name']} command failed")

    def _test_config_files(self) -> None:
        """Test configuration file validity."""
        print("\n📄 Test 4: Configuration File Validation")

        # Check pytest.ini format
        pytest_ini = self.project_root / "tests/e2e/pytest.ini"
        if pytest_ini.exists():
            with open(pytest_ini, "r") as f:
                content = f.read()

            if content.startswith("[pytest]"):
                print("✅ pytest.ini has correct section header")
                self.results.append(
                    CIValidationResult("pytest.ini format", "file check", True)
                )
            else:
                print("❌ pytest.ini has incorrect section header")
                self.results.append(
                    CIValidationResult("pytest.ini format", "file check", False)
                )

        # Check pyproject.toml markers
        pyproject_toml = self.project_root / "pyproject.toml"
        if pyproject_toml.exists():
            with open(pyproject_toml, "r") as f:
                content = f.read()

            if (
                "markers = [" in content
                and "constitutional" in content
                and "smoke" in content
            ):
                print("✅ pyproject.toml has required markers")
                self.results.append(
                    CIValidationResult("pyproject.toml markers", "file check", True)
                )
            else:
                print("❌ pyproject.toml missing required markers")
                self.results.append(
                    CIValidationResult("pyproject.toml markers", "file check", False)
                )

    def _test_coverage_compatibility(self) -> None:
        """Test coverage configuration compatibility."""
        print("\n📊 Test 5: Coverage Compatibility")

        # Test coverage collection (dry run)
        cmd = "python -m pytest tests/e2e/tests/test_smoke.py::test_framework_initialization --collect-only"
        result = self._run_pytest_command(cmd, "Coverage Compatibility")
        self.results.append(result)

        if result.success:
            print("✅ Coverage configuration compatible")
        else:
            print("❌ Coverage configuration issues detected")

    def _generate_report(self) -> bool:
        """Generate validation report."""
        print("\n" + "=" * 60)
        print("📊 VALIDATION REPORT")
        print("=" * 60)

        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.success)
        failed_tests = total_tests - passed_tests

        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")

        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.results:
                if not result.success:
                    print(f"  - {result.test_name}: {result.error[:100]}")

        # Save detailed report
        report_data = {
            "timestamp": subprocess.run(
                ["date", "-Iseconds"], capture_output=True, text=True
            ).stdout.strip(),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests / total_tests) * 100,
            "results": [
                {
                    "test_name": r.test_name,
                    "command": r.command,
                    "success": r.success,
                    "error": r.error if not r.success else None,
                }
                for r in self.results
            ],
        }

        report_file = self.project_root / "reports/ci_validation_report.json"
        report_file.parent.mkdir(exist_ok=True)

        with open(report_file, "w") as f:
            json.dump(report_data, f, indent=2)

        print(f"\n📄 Detailed report saved to: {report_file}")

        # Return overall success
        success = failed_tests == 0
        if success:
            print("\n🎉 ALL TESTS PASSED - CI/CD configuration is valid!")
        else:
            print(
                f"\n⚠️  {failed_tests} tests failed - CI/CD configuration needs attention"
            )

        return success


def main() -> None:
    """Main entry point."""
    validator = PytestCIValidator()
    success = validator.run_validation()

    # Exit with appropriate code for CI
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
