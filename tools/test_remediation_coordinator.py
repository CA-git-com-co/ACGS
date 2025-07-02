#!/usr/bin/env python3
"""
ACGS-1 Test Remediation Coordinator

Systematically fixes and executes tests with proper error handling and reporting.
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TestRemediationCoordinator:
    """Coordinates systematic test remediation and execution."""

    def __init__(self):
        self.project_root = Path()
        self.results = {
            "execution_id": f"test_remediation_{int(time.time())}",
            "start_time": datetime.now().isoformat(),
            "test_categories": {},
            "fixes_applied": [],
            "summary": {},
        }

    def setup_python_paths(self):
        """Setup Python paths for proper imports."""
        paths_to_add = [
            str(self.project_root / "services" / "shared"),
            str(
                self.project_root
                / "services"
                / "core"
                / "governance-synthesis"
                / "gs_service"
            ),
            str(
                self.project_root
                / "services"
                / "core"
                / "constitutional-ai"
                / "ac_service"
            ),
            str(
                self.project_root
                / "services"
                / "core"
                / "formal-verification"
                / "fv_service"
            ),
            str(
                self.project_root
                / "services"
                / "core"
                / "policy-governance"
                / "pgc_service"
            ),
            str(self.project_root / "src" / "backend" / "shared"),
        ]

        for path in paths_to_add:
            if os.path.exists(path) and path not in sys.path:
                sys.path.insert(0, path)
                logger.info(f"Added to Python path: {path}")

    def run_test_subset(
        self, test_pattern: str, max_failures: int = 5
    ) -> dict[str, Any]:
        """Run a subset of tests with error handling."""
        logger.info(f"Running tests matching pattern: {test_pattern}")

        cmd = [
            "python",
            "-m",
            "pytest",
            test_pattern,
            "-v",
            "--tb=short",
            f"--maxfail={max_failures}",
            "--timeout=60",
            "--json-report",
            f"--json-report-file=temp_results_{int(time.time())}.json",
        ]

        try:
            # Activate virtual environment
            env = os.environ.copy()
            venv_python = self.project_root / "venv" / "bin" / "python"
            if venv_python.exists():
                cmd[0] = str(venv_python)

            result = subprocess.run(
                cmd, check=False, capture_output=True, text=True, timeout=300, env=env
            )

            return {
                "pattern": test_pattern,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0,
            }

        except subprocess.TimeoutExpired:
            logger.error(f"Test execution timed out for pattern: {test_pattern}")
            return {
                "pattern": test_pattern,
                "return_code": -1,
                "stdout": "",
                "stderr": "Test execution timed out",
                "success": False,
            }
        except Exception as e:
            logger.error(f"Error running tests for pattern {test_pattern}: {e}")
            return {
                "pattern": test_pattern,
                "return_code": -1,
                "stdout": "",
                "stderr": str(e),
                "success": False,
            }

    def analyze_test_failures(self, test_result: dict[str, Any]) -> list[str]:
        """Analyze test failures and categorize issues."""
        issues = []

        stderr = test_result.get("stderr", "")
        test_result.get("stdout", "")

        # Check for common import errors
        if "ModuleNotFoundError" in stderr:
            issues.append("missing_modules")
        if "ImportError" in stderr:
            issues.append("import_errors")
        if "FileNotFoundError" in stderr:
            issues.append("missing_files")
        if "insufficient funds" in stderr.lower():
            issues.append("blockchain_funding")
        if "AttributeError" in stderr:
            issues.append("attribute_errors")

        return issues

    def execute_test_categories(self) -> dict[str, Any]:
        """Execute tests by category with systematic error handling."""

        test_categories = [
            {
                "name": "basic_functionality",
                "pattern": "test_basic_functionality.py",
                "priority": "critical",
            },
            {
                "name": "unit_main",
                "pattern": "tests/unit/test_main.py",
                "priority": "high",
            },
            {
                "name": "unit_token",
                "pattern": "tests/unit/test_token.py",
                "priority": "high",
            },
            {
                "name": "unit_users",
                "pattern": "tests/unit/test_users.py",
                "priority": "high",
            },
            {
                "name": "unit_auth",
                "pattern": "tests/unit/test_auth*.py",
                "priority": "high",
            },
            {
                "name": "unit_config",
                "pattern": "tests/unit/test_centralized_config*.py",
                "priority": "medium",
            },
            {
                "name": "integration_simple",
                "pattern": "tests/integration/test_ai_model_integration.py",
                "priority": "medium",
            },
            {"name": "performance", "pattern": "tests/performance/", "priority": "low"},
        ]

        results = {}

        for category in test_categories:
            logger.info(f"Executing test category: {category['name']}")

            result = self.run_test_subset(category["pattern"])
            issues = self.analyze_test_failures(result)

            results[category["name"]] = {
                **result,
                "priority": category["priority"],
                "issues": issues,
                "timestamp": datetime.now().isoformat(),
            }

            # Log results
            if result["success"]:
                logger.info(f"✅ {category['name']}: PASSED")
            else:
                logger.warning(
                    f"❌ {category['name']}: FAILED - Issues: {', '.join(issues)}"
                )

        return results

    def generate_summary_report(self, test_results: dict[str, Any]) -> dict[str, Any]:
        """Generate comprehensive summary report."""

        total_categories = len(test_results)
        passed_categories = sum(1 for r in test_results.values() if r["success"])

        # Categorize issues
        all_issues = []
        for result in test_results.values():
            all_issues.extend(result.get("issues", []))

        issue_counts = {}
        for issue in all_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1

        summary = {
            "total_test_categories": total_categories,
            "passed_categories": passed_categories,
            "failed_categories": total_categories - passed_categories,
            "success_rate": (
                (passed_categories / total_categories) * 100
                if total_categories > 0
                else 0
            ),
            "top_issues": sorted(
                issue_counts.items(), key=lambda x: x[1], reverse=True
            )[:5],
            "recommendations": self.generate_recommendations(issue_counts),
            "next_actions": self.generate_next_actions(test_results),
        }

        return summary

    def generate_recommendations(self, issue_counts: dict[str, int]) -> list[str]:
        """Generate specific recommendations based on issues found."""
        recommendations = []

        if issue_counts.get("missing_modules", 0) > 0:
            recommendations.append("Install missing Python modules and dependencies")

        if issue_counts.get("import_errors", 0) > 0:
            recommendations.append("Fix import paths and module structure")

        if issue_counts.get("missing_files", 0) > 0:
            recommendations.append("Create missing directories and files")

        if issue_counts.get("blockchain_funding", 0) > 0:
            recommendations.append("Fund Solana devnet wallet for blockchain tests")

        if issue_counts.get("attribute_errors", 0) > 0:
            recommendations.append("Update test code for API compatibility")

        return recommendations

    def generate_next_actions(self, test_results: dict[str, Any]) -> list[str]:
        """Generate prioritized next actions."""
        actions = []

        # Check critical tests first
        critical_failed = [
            name
            for name, result in test_results.items()
            if result.get("priority") == "critical" and not result["success"]
        ]

        if critical_failed:
            actions.append(
                f"URGENT: Fix critical test failures: {', '.join(critical_failed)}"
            )

        # Check for systematic issues
        high_priority_failed = [
            name
            for name, result in test_results.items()
            if result.get("priority") == "high" and not result["success"]
        ]

        if high_priority_failed:
            actions.append(
                f"HIGH: Address high-priority test failures: {', '.join(high_priority_failed)}"
            )

        actions.extend(
            [
                "Create comprehensive mock implementations for missing modules",
                "Systematically fix import paths across all test files",
                "Set up proper test environment configuration",
                "Implement test coverage measurement and reporting",
            ]
        )

        return actions

    async def execute_full_analysis(self) -> dict[str, Any]:
        """Execute full test analysis and remediation workflow."""
        logger.info("🚀 Starting ACGS-1 Test Remediation Analysis")

        # Setup environment
        self.setup_python_paths()

        # Execute test categories
        test_results = self.execute_test_categories()

        # Generate summary
        summary = self.generate_summary_report(test_results)

        # Compile final results
        self.results.update(
            {
                "test_results": test_results,
                "summary": summary,
                "end_time": datetime.now().isoformat(),
                "duration_seconds": (
                    datetime.now() - datetime.fromisoformat(self.results["start_time"])
                ).total_seconds(),
            }
        )

        # Save results
        results_file = f"test_remediation_results_{int(time.time())}.json"
        with open(results_file, "w") as f:
            json.dump(self.results, f, indent=2, default=str)

        logger.info(f"📊 Analysis complete. Results saved to: {results_file}")

        return self.results


async def main():
    """Main execution function."""
    coordinator = TestRemediationCoordinator()
    results = await coordinator.execute_full_analysis()

    # Print summary
    summary = results["summary"]
    print("\n" + "=" * 70)
    print("ACGS-1 TEST REMEDIATION ANALYSIS SUMMARY")
    print("=" * 70)
    print(f"Success Rate: {summary['success_rate']:.1f}%")
    print(
        f"Categories Passed: {summary['passed_categories']}/{summary['total_test_categories']}"
    )
    print("\nTop Issues:")
    for issue, count in summary["top_issues"]:
        print(f"  - {issue}: {count} occurrences")

    print("\nNext Actions:")
    for i, action in enumerate(summary["next_actions"][:5], 1):
        print(f"  {i}. {action}")

    print("=" * 70)

    return results


if __name__ == "__main__":
    asyncio.run(main())
