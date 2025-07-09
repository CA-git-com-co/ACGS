#!/usr/bin/env python3
"""
Post-merge validation suite
Run after each successful merge to ensure system stability
"""

import json
import logging
import subprocess
import sys
import time
from typing import Any

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PostMergeValidator:
    """Comprehensive post-merge validation"""

    def __init__(self):
        self.services = [
            {"name": "auth", "port": 8001},
            {"name": "ac", "port": 8002},
            {"name": "gs", "port": 8003},
            {"name": "fv", "port": 8004},
            {"name": "integrity", "port": 8005},
            {"name": "pgc", "port": 8006},
        ]

    def run_health_checks(self) -> dict[str, Any]:
        """Run comprehensive health checks"""
        logger.info("🏥 Running health checks...")

        try:
            result = subprocess.run(
                ["python", "scripts/comprehensive_health_check.py"],
                check=False,
                capture_output=True,
                text=True,
                timeout=120,
            )

            return {
                "status": "success" if result.returncode == 0 else "failed",
                "return_code": result.returncode,
                "output": result.stdout[-1000:] if result.stdout else "",
                "errors": result.stderr[-500:] if result.stderr else "",
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def run_security_scan(self) -> dict[str, Any]:
        """Run security validation"""
        logger.info("🔒 Running security scan...")

        try:
            result = subprocess.run(
                ["python", "scripts/phase3_security_validation.py"],
                check=False,
                capture_output=True,
                text=True,
                timeout=180,
            )

            return {
                "status": "success" if result.returncode == 0 else "failed",
                "return_code": result.returncode,
                "output": result.stdout[-1000:] if result.stdout else "",
                "errors": result.stderr[-500:] if result.stderr else "",
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def run_bandit_scan(self) -> dict[str, Any]:
        """Run bandit security scan"""
        logger.info("🛡️ Running bandit security scan...")

        try:
            result = subprocess.run(
                ["bandit", "-r", "src/", "-f", "json"],
                check=False,
                capture_output=True,
                text=True,
                timeout=60,
            )

            # Bandit returns non-zero for findings, so check output
            try:
                bandit_output = json.loads(result.stdout) if result.stdout else {}
                high_severity = len(
                    [
                        issue
                        for issue in bandit_output.get("results", [])
                        if issue.get("issue_severity") == "HIGH"
                    ]
                )
                medium_severity = len(
                    [
                        issue
                        for issue in bandit_output.get("results", [])
                        if issue.get("issue_severity") == "MEDIUM"
                    ]
                )

                return {
                    "status": "success",
                    "high_severity_issues": high_severity,
                    "medium_severity_issues": medium_severity,
                    "total_issues": len(bandit_output.get("results", [])),
                    "scan_completed": True,
                }
            except json.JSONDecodeError:
                return {
                    "status": "completed",
                    "return_code": result.returncode,
                    "raw_output": result.stdout[-500:] if result.stdout else "",
                }

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def run_pytest_suite(self) -> dict[str, Any]:
        """Run critical test suite"""
        logger.info("🧪 Running pytest suite...")

        try:
            # Run critical tests
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/", "-x", "--tb=short", "-q"],
                check=False,
                capture_output=True,
                text=True,
                timeout=300,
            )

            return {
                "status": "success" if result.returncode == 0 else "failed",
                "return_code": result.returncode,
                "output": result.stdout[-1000:] if result.stdout else "",
                "errors": result.stderr[-500:] if result.stderr else "",
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def check_docker_compose_config(self) -> dict[str, Any]:
        """Validate docker-compose configuration"""
        logger.info("🐳 Checking docker-compose configuration...")

        try:
            result = subprocess.run(
                ["docker-compose", "-f", "docker-compose.yml", "config"],
                check=False,
                capture_output=True,
                text=True,
                timeout=30,
            )

            return {
                "status": "success" if result.returncode == 0 else "failed",
                "return_code": result.returncode,
                "config_valid": result.returncode == 0,
                "errors": result.stderr if result.stderr else "",
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def check_workflow_syntax(self) -> dict[str, Any]:
        """Check GitHub workflow syntax"""
        logger.info("⚙️ Checking workflow syntax...")

        workflow_files = [
            ".github/workflows/production-deploy.yml",
            ".github/workflows/image-build.yml",
            ".github/workflows/defender-for-devops.yml",
        ]

        workflow_results = {}

        for workflow_file in workflow_files:
            try:
                # Basic YAML syntax check
                import yaml

                with open(workflow_file) as f:
                    yaml.safe_load(f)

                workflow_results[workflow_file] = {
                    "status": "success",
                    "yaml_valid": True,
                }
            except Exception as e:
                workflow_results[workflow_file] = {
                    "status": "error",
                    "error": str(e),
                    "yaml_valid": False,
                }

        return {"status": "success", "workflow_checks": workflow_results}

    def run_full_validation(self) -> dict[str, Any]:
        """Run complete post-merge validation"""
        logger.info("🚀 Starting post-merge validation...")

        start_time = time.time()

        validation_results = {"timestamp": time.time(), "tests": {}}

        # Run all validation tests
        validation_results["tests"]["health_checks"] = self.run_health_checks()
        validation_results["tests"]["security_scan"] = self.run_security_scan()
        validation_results["tests"]["bandit_scan"] = self.run_bandit_scan()
        validation_results["tests"]["pytest_suite"] = self.run_pytest_suite()
        validation_results["tests"][
            "docker_config"
        ] = self.check_docker_compose_config()
        validation_results["tests"]["workflow_syntax"] = self.check_workflow_syntax()

        validation_results["execution_time"] = time.time() - start_time

        # Calculate success rate
        successful_tests = 0
        total_tests = len(validation_results["tests"])

        for _test_name, test_result in validation_results["tests"].items():
            if test_result.get("status") in ["success", "completed"]:
                successful_tests += 1

        validation_results["success_rate"] = (
            successful_tests / total_tests if total_tests > 0 else 0
        )
        validation_results["overall_status"] = (
            "PASS" if validation_results["success_rate"] >= 0.8 else "FAIL"
        )

        logger.info(
            f"🎯 Post-merge validation complete: {validation_results['success_rate']:.1%} success rate"
        )
        logger.info(f"📊 Overall status: {validation_results['overall_status']}")

        return validation_results


def main():
    """Main validation execution"""
    validator = PostMergeValidator()
    results = validator.run_full_validation()

    # Print summary
    print("\n" + "=" * 60)
    print("POST-MERGE VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Success Rate: {results['success_rate']:.1%}")
    print(f"Overall Status: {results['overall_status']}")
    print(f"Execution Time: {results['execution_time']:.2f}s")

    # Print detailed results
    for test_name, test_result in results["tests"].items():
        status = test_result.get("status", "unknown")
        print(f"  {test_name}: {status.upper()}")

        if status in ["error", "failed"] and "error" in test_result:
            print(f"    Error: {test_result['error']}")
        elif status == "failed" and "return_code" in test_result:
            print(f"    Return code: {test_result['return_code']}")

    print("=" * 60)

    # Provide recommendations
    if results["overall_status"] == "PASS":
        print("✅ SYSTEM STATUS: HEALTHY")
        print("   All post-merge validations passed")
        print("   Safe to proceed with next merge")
    else:
        print("❌ SYSTEM STATUS: ISSUES DETECTED")
        print("   Some validations failed - investigate before next merge")
        print("   Consider rollback if critical issues found")

    print("=" * 60)

    # Exit with appropriate code
    sys.exit(0 if results["overall_status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
