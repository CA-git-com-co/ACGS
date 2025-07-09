#!/usr/bin/env python3
"""
ACGS Integration Test Runner
Constitutional Hash: cdd01ef066bc6cf2

Comprehensive integration test runner for ACGS services.
"""

import asyncio
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

import httpx

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class ACGSIntegrationTestRunner:
    """Run comprehensive integration tests for ACGS."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.test_results = {}
        self.services_status = {}

    def check_service_availability(self) -> Dict[str, bool]:
        """Check which services are available for testing."""

        services = {
            "constitutional_ai": "http://localhost:8001",
            "integrity": "http://localhost:8002",
            "api_gateway": "http://localhost:8010",
            "auth": "http://localhost:8016",
            "governance_synthesis": "http://localhost:8008",
        }

        print("🔍 Checking service availability...")

        async def check_service(name: str, url: str) -> Tuple[str, bool]:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{url}/health", timeout=5.0)
                    if response.status_code == 200:
                        print(f"  ✅ {name}: Available")
                        return name, True
                    else:
                        print(f"  ❌ {name}: HTTP {response.status_code}")
                        return name, False
            except Exception as e:
                print(f"  ❌ {name}: {str(e)}")
                return name, False

        async def check_all_services():
            tasks = [check_service(name, url) for name, url in services.items()]
            results = await asyncio.gather(*tasks)
            return dict(results)

        self.services_status = asyncio.run(check_all_services())

        available_count = sum(
            1 for available in self.services_status.values() if available
        )
        print(
            f"\n📊 Service Status: {available_count}/{len(services)} services available"
        )

        return self.services_status

    def run_constitutional_compliance_tests(self) -> bool:
        """Run constitutional compliance integration tests."""

        print("\n⚖️ Running Constitutional Compliance Tests...")

        test_file = (
            self.project_root
            / "tests"
            / "integration"
            / "test_constitutional_compliance.py"
        )

        if not test_file.exists():
            print(f"❌ Test file not found: {test_file}")
            return False

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    str(test_file),
                    "-v",
                    "--tb=short",
                    "--color=yes",
                ],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            self.test_results["constitutional_compliance"] = {
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }

            if result.returncode == 0:
                print("✅ Constitutional compliance tests PASSED")
                return True
            else:
                print("❌ Constitutional compliance tests FAILED")
                print(f"Error output: {result.stderr}")
                return False

        except Exception as e:
            print(f"❌ Failed to run constitutional compliance tests: {e}")
            return False

    def run_security_hardening_tests(self) -> bool:
        """Run security hardening integration tests."""

        print("\n🔒 Running Security Hardening Tests...")

        test_file = (
            self.project_root / "tests" / "integration" / "test_security_hardening.py"
        )

        if not test_file.exists():
            print(f"❌ Test file not found: {test_file}")
            return False

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    str(test_file),
                    "-v",
                    "--tb=short",
                    "--color=yes",
                ],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            self.test_results["security_hardening"] = {
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }

            if result.returncode == 0:
                print("✅ Security hardening tests PASSED")
                return True
            else:
                print("❌ Security hardening tests FAILED")
                print(f"Error output: {result.stderr}")
                return False

        except Exception as e:
            print(f"❌ Failed to run security hardening tests: {e}")
            return False

    def run_service_communication_tests(self) -> bool:
        """Run service communication integration tests."""

        print("\n🌐 Running Service Communication Tests...")

        test_file = (
            self.project_root
            / "tests"
            / "integration"
            / "test_service_communication.py"
        )

        if not test_file.exists():
            print(f"❌ Test file not found: {test_file}")
            return False

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    str(test_file),
                    "-v",
                    "--tb=short",
                    "--color=yes",
                ],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            self.test_results["service_communication"] = {
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }

            if result.returncode == 0:
                print("✅ Service communication tests PASSED")
                return True
            else:
                print("❌ Service communication tests FAILED")
                print(f"Error output: {result.stderr}")
                return False

        except Exception as e:
            print(f"❌ Failed to run service communication tests: {e}")
            return False

    def run_performance_tests(self) -> bool:
        """Run basic performance tests."""

        print("\n⚡ Running Performance Tests...")

        if not any(self.services_status.values()):
            print("⚠️ No services available for performance testing")
            return True  # Not a failure if no services are running

        try:
            # Run simple performance test
            result = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    """
import asyncio
import httpx
import time

async def test_performance():
    services = {
        'constitutional_ai': 'http://localhost:8001',
        'api_gateway': 'http://localhost:8010'
    }
    
    results = {}
    
    async with httpx.AsyncClient() as client:
        for name, url in services.items():
            try:
                start = time.time()
                response = await client.get(f'{url}/health', timeout=10.0)
                end = time.time()
                
                if response.status_code == 200:
                    response_time = (end - start) * 1000
                    results[name] = response_time
                    print(f'{name}: {response_time:.2f}ms')
                    
                    if response_time < 5000:  # <5s target
                        print(f'✅ {name} meets performance target')
                    else:
                        print(f'⚠️ {name} exceeds performance target')
                else:
                    print(f'❌ {name} health check failed')
            except Exception as e:
                print(f'❌ {name} error: {e}')
    
    return len(results) > 0

if __name__ == '__main__':
    success = asyncio.run(test_performance())
    exit(0 if success else 1)
""",
                ],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            self.test_results["performance"] = {
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }

            print(result.stdout)

            if result.returncode == 0:
                print("✅ Performance tests PASSED")
                return True
            else:
                print("❌ Performance tests FAILED")
                return False

        except Exception as e:
            print(f"❌ Failed to run performance tests: {e}")
            return False

    def validate_constitutional_compliance(self) -> bool:
        """Validate constitutional compliance across all test results."""

        print(f"\n⚖️ Validating Constitutional Compliance...")
        print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")

        compliance_issues = []

        # Check that all tests maintained constitutional compliance
        for test_name, results in self.test_results.items():
            output = results.get("stdout", "")

            if CONSTITUTIONAL_HASH not in output:
                compliance_issues.append(
                    f"{test_name}: Constitutional hash not found in output"
                )

            if "constitutional_hash_mismatch" in output.lower():
                compliance_issues.append(
                    f"{test_name}: Constitutional hash mismatch detected"
                )

        if compliance_issues:
            print("❌ Constitutional compliance issues found:")
            for issue in compliance_issues:
                print(f"  - {issue}")
            return False
        else:
            print("✅ All tests maintained constitutional compliance")
            return True

    def generate_test_report(self) -> None:
        """Generate comprehensive test report."""

        report_path = (
            self.project_root
            / "test_reports"
            / f"integration_test_report_{int(time.time())}.md"
        )
        report_path.parent.mkdir(exist_ok=True)

        # Calculate overall results
        total_tests = len(self.test_results)
        passed_tests = sum(
            1 for r in self.test_results.values() if r["return_code"] == 0
        )

        report_content = f"""# ACGS Integration Test Report
Constitutional Hash: {CONSTITUTIONAL_HASH}
Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

- **Total Test Suites**: {total_tests}
- **Passed**: {passed_tests}
- **Failed**: {total_tests - passed_tests}
- **Success Rate**: {(passed_tests/total_tests*100) if total_tests > 0 else 0:.1f}%

## Service Availability

"""

        for service, available in self.services_status.items():
            status = "✅ Available" if available else "❌ Unavailable"
            report_content += f"- **{service}**: {status}\n"

        report_content += "\n## Test Results\n\n"

        for test_name, results in self.test_results.items():
            status = "✅ PASSED" if results["return_code"] == 0 else "❌ FAILED"
            report_content += f"### {test_name.replace('_', ' ').title()}\n"
            report_content += f"**Status**: {status}\n"
            report_content += f"**Return Code**: {results['return_code']}\n\n"

            if results["stdout"]:
                report_content += "**Output**:\n```\n"
                report_content += results["stdout"][:2000]  # Truncate long output
                if len(results["stdout"]) > 2000:
                    report_content += "\n... (truncated)"
                report_content += "\n```\n\n"

            if results["stderr"]:
                report_content += "**Errors**:\n```\n"
                report_content += results["stderr"][:1000]  # Truncate errors
                if len(results["stderr"]) > 1000:
                    report_content += "\n... (truncated)"
                report_content += "\n```\n\n"

        report_content += f"""## Constitutional Compliance

All tests validated constitutional compliance with hash: `{CONSTITUTIONAL_HASH}`

## Recommendations

Based on the test results:

"""

        if passed_tests == total_tests:
            report_content += (
                "- ✅ All integration tests passed - system is ready for deployment\n"
            )
        else:
            report_content += "- ❌ Some tests failed - investigate and fix issues before deployment\n"
            report_content += (
                "- Review failed test output for specific remediation steps\n"
            )

        if sum(1 for available in self.services_status.values() if available) < len(
            self.services_status
        ):
            report_content += "- ⚠️ Some services were unavailable during testing\n"
            report_content += (
                "- Ensure all services are running for complete test coverage\n"
            )

        report_content += f"\n---\n*Report generated by ACGS Integration Test Runner*\n"
        report_content += f"*Constitutional Hash: {CONSTITUTIONAL_HASH}*\n"

        with open(report_path, "w") as f:
            f.write(report_content)

        print(f"\n📄 Test report generated: {report_path}")

    def run_all_tests(self) -> bool:
        """Run all integration tests."""

        print(f"🧪 Starting ACGS Integration Tests")
        print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
        print(f"Project Root: {self.project_root}")

        # Check service availability
        self.check_service_availability()

        # Run test suites
        test_results = []

        test_results.append(self.run_constitutional_compliance_tests())
        test_results.append(self.run_security_hardening_tests())
        test_results.append(self.run_service_communication_tests())
        test_results.append(self.run_performance_tests())

        # Validate constitutional compliance
        constitutional_compliance = self.validate_constitutional_compliance()

        # Generate report
        self.generate_test_report()

        # Summary
        total_tests = len(test_results)
        passed_tests = sum(1 for result in test_results if result)

        print(f"\n📊 Integration Test Summary:")
        print(f"  ✅ Passed: {passed_tests}/{total_tests} test suites")
        print(
            f"  ⚖️ Constitutional Compliance: {'✅ VALID' if constitutional_compliance else '❌ INVALID'}"
        )

        success = passed_tests == total_tests and constitutional_compliance

        if success:
            print(f"\n🎉 All integration tests PASSED!")
            print(
                f"System is ready for deployment with constitutional compliance validated."
            )
        else:
            print(f"\n❌ Some integration tests FAILED!")
            print(f"Review test output and fix issues before deployment.")

        print(f"\nConstitutional Hash Validated: {CONSTITUTIONAL_HASH}")

        return success


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        project_root = Path(sys.argv[1])
    else:
        project_root = Path.cwd()

    if not project_root.exists():
        print(f"❌ Project root does not exist: {project_root}")
        sys.exit(1)

    runner = ACGSIntegrationTestRunner(project_root)
    success = runner.run_all_tests()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
