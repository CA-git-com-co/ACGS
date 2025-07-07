#!/usr/bin/env python3
"""
ACGS Security CI/CD Integration

Integrates security testing into CI/CD pipelines with automated
reporting, threshold enforcement, and constitutional compliance validation.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from run_security_tests import SecurityTestRunner

# Constitutional compliance hash
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SecurityCIIntegration:
    """
    CI/CD integration for ACGS security testing.

    Provides automated security testing integration with:
    - Threshold-based pass/fail criteria
    - Constitutional compliance enforcement
    - Automated reporting and notifications
    - Integration with popular CI/CD platforms
    """

    def __init__(self, config: dict[str, Any] = None):
        self.config = config or self._load_default_config()
        self.constitutional_hash = CONSTITUTIONAL_HASH

        # CI/CD environment detection
        self.ci_environment = self._detect_ci_environment()

        logger.info(f"Security CI integration initialized for {self.ci_environment}")

    def _load_default_config(self) -> dict[str, Any]:
        """
        Load default configuration for security CI integration.

        Returns:
            Default configuration dictionary
        """

        return {
            "security_thresholds": {
                "minimum_score": 80,
                "max_critical_vulnerabilities": 0,
                "max_high_vulnerabilities": 2,
                "max_medium_vulnerabilities": 5,
                "constitutional_compliance_required": True,
            },
            "test_configuration": {
                "test_types": ["security", "penetration", "compliance"],
                "timeout_seconds": 1800,  # 30 minutes
                "retry_attempts": 2,
            },
            "reporting": {
                "generate_html_report": True,
                "generate_json_report": True,
                "generate_junit_xml": True,
                "upload_to_artifacts": True,
            },
            "notifications": {
                "slack_webhook": os.getenv("SLACK_WEBHOOK_URL"),
                "email_recipients": [],
                "github_comment": True,
            },
            "constitutional_compliance": {
                "enforce_hash_validation": True,
                "required_hash": CONSTITUTIONAL_HASH,
                "fail_on_non_compliance": True,
            },
        }

    def _detect_ci_environment(self) -> str:
        """
        Detect the CI/CD environment.

        Returns:
            CI/CD platform name
        """

        # GitHub Actions
        if os.getenv("GITHUB_ACTIONS"):
            return "github-actions"

        # GitLab CI
        elif os.getenv("GITLAB_CI"):
            return "gitlab-ci"

        # Jenkins
        elif os.getenv("JENKINS_URL"):
            return "jenkins"

        # CircleCI
        elif os.getenv("CIRCLECI"):
            return "circleci"

        # Azure DevOps
        elif os.getenv("AZURE_HTTP_USER_AGENT"):
            return "azure-devops"

        # Travis CI
        elif os.getenv("TRAVIS"):
            return "travis-ci"

        else:
            return "unknown"

    async def run_security_tests_with_ci_integration(
        self, target_url: str, api_key: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Run security tests with full CI/CD integration.

        Args:
            target_url: Target URL for security testing
            api_key: Optional API key for authenticated testing

        Returns:
            Dict containing test results and CI integration data
        """

        logger.info(f"Starting CI-integrated security testing for {target_url}")

        # Create test runner
        runner = SecurityTestRunner(target_url, api_key)

        # Run tests with timeout
        try:
            test_results = await asyncio.wait_for(
                runner.run_all_security_tests(
                    self.config["test_configuration"]["test_types"]
                ),
                timeout=self.config["test_configuration"]["timeout_seconds"],
            )
        except asyncio.TimeoutError:
            logger.error("Security tests timed out")
            return self._generate_timeout_result()

        # Evaluate results against thresholds
        evaluation_result = self._evaluate_security_results(test_results)

        # Generate CI-specific reports
        ci_reports = await self._generate_ci_reports(test_results, evaluation_result)

        # Send notifications
        await self._send_notifications(test_results, evaluation_result)

        # Prepare CI integration result
        ci_result = {
            "test_results": test_results,
            "evaluation": evaluation_result,
            "ci_reports": ci_reports,
            "ci_environment": self.ci_environment,
            "constitutional_compliance": {
                "hash": self.constitutional_hash,
                "verified": test_results.get("constitutional_compliance", {}).get(
                    "compliance_verified", False
                ),
            },
        }

        logger.info(
            "CI-integrated security testing completed:"
            f" {evaluation_result['overall_status']}"
        )
        return ci_result

    def _evaluate_security_results(
        self, test_results: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Evaluate security test results against configured thresholds.

        Args:
            test_results: Security test results

        Returns:
            Evaluation result with pass/fail status
        """

        evaluation = {
            "overall_status": "PASS",
            "threshold_violations": [],
            "constitutional_compliance_status": "COMPLIANT",
            "security_score": test_results.get("overall_security_assessment", {}).get(
                "security_score", 0
            ),
            "vulnerability_counts": test_results.get(
                "overall_security_assessment", {}
            ).get("total_vulnerabilities", {}),
        }

        thresholds = self.config["security_thresholds"]

        # Check minimum security score
        if evaluation["security_score"] < thresholds["minimum_score"]:
            evaluation["threshold_violations"].append(
                {
                    "type": "minimum_score",
                    "threshold": thresholds["minimum_score"],
                    "actual": evaluation["security_score"],
                    "severity": "HIGH",
                }
            )

        # Check vulnerability counts
        vuln_counts = evaluation["vulnerability_counts"]

        if vuln_counts.get("critical", 0) > thresholds["max_critical_vulnerabilities"]:
            evaluation["threshold_violations"].append(
                {
                    "type": "critical_vulnerabilities",
                    "threshold": thresholds["max_critical_vulnerabilities"],
                    "actual": vuln_counts.get("critical", 0),
                    "severity": "CRITICAL",
                }
            )

        if vuln_counts.get("high", 0) > thresholds["max_high_vulnerabilities"]:
            evaluation["threshold_violations"].append(
                {
                    "type": "high_vulnerabilities",
                    "threshold": thresholds["max_high_vulnerabilities"],
                    "actual": vuln_counts.get("high", 0),
                    "severity": "HIGH",
                }
            )

        if vuln_counts.get("medium", 0) > thresholds["max_medium_vulnerabilities"]:
            evaluation["threshold_violations"].append(
                {
                    "type": "medium_vulnerabilities",
                    "threshold": thresholds["max_medium_vulnerabilities"],
                    "actual": vuln_counts.get("medium", 0),
                    "severity": "MEDIUM",
                }
            )

        # Check constitutional compliance
        constitutional_compliance = test_results.get("constitutional_compliance", {})
        if not constitutional_compliance.get("compliance_verified", False):
            evaluation["constitutional_compliance_status"] = "NON_COMPLIANT"

            if thresholds["constitutional_compliance_required"]:
                evaluation["threshold_violations"].append(
                    {
                        "type": "constitutional_compliance",
                        "threshold": "REQUIRED",
                        "actual": "NON_COMPLIANT",
                        "severity": "CRITICAL",
                    }
                )

        # Determine overall status
        if evaluation["threshold_violations"]:
            critical_violations = [
                v
                for v in evaluation["threshold_violations"]
                if v["severity"] == "CRITICAL"
            ]
            if critical_violations:
                evaluation["overall_status"] = "FAIL"
            else:
                evaluation["overall_status"] = "WARN"

        return evaluation

    async def _generate_ci_reports(
        self, test_results: dict[str, Any], evaluation_result: dict[str, Any]
    ) -> dict[str, str]:
        """
        Generate CI-specific reports.

        Args:
            test_results: Security test results
            evaluation_result: Evaluation result

        Returns:
            Dict containing paths to generated reports
        """

        reports = {}

        # Generate JSON report
        if self.config["reporting"]["generate_json_report"]:
            json_path = self._generate_json_report(test_results, evaluation_result)
            reports["json_report"] = json_path

        # Generate HTML report
        if self.config["reporting"]["generate_html_report"]:
            html_path = self._generate_html_report(test_results, evaluation_result)
            reports["html_report"] = html_path

        # Generate JUnit XML report
        if self.config["reporting"]["generate_junit_xml"]:
            junit_path = self._generate_junit_xml_report(
                test_results, evaluation_result
            )
            reports["junit_xml"] = junit_path

        # Upload to CI artifacts
        if self.config["reporting"]["upload_to_artifacts"]:
            await self._upload_to_artifacts(reports)

        return reports

    def _generate_json_report(
        self, test_results: dict[str, Any], evaluation_result: dict[str, Any]
    ) -> str:
        """
        Generate JSON report for CI integration.

        Args:
            test_results: Security test results
            evaluation_result: Evaluation result

        Returns:
            Path to generated JSON report
        """

        report_data = {
            "metadata": {
                "report_type": "ci_security_report",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "ci_environment": self.ci_environment,
                "constitutional_hash": self.constitutional_hash,
            },
            "test_results": test_results,
            "evaluation": evaluation_result,
            "ci_integration": {
                "thresholds": self.config["security_thresholds"],
                "status": evaluation_result["overall_status"],
            },
        }

        report_path = Path("security_report.json")
        with open(report_path, "w") as f:
            json.dump(report_data, f, indent=2, default=str)

        return str(report_path)

    def _generate_html_report(
        self, test_results: dict[str, Any], evaluation_result: dict[str, Any]
    ) -> str:
        """
        Generate HTML report for CI integration.

        Args:
            test_results: Security test results
            evaluation_result: Evaluation result

        Returns:
            Path to generated HTML report
        """

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>ACGS Security Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .status-pass {{ color: green; font-weight: bold; }}
        .status-fail {{ color: red; font-weight: bold; }}
        .status-warn {{ color: orange; font-weight: bold; }}
        .vulnerability {{ margin: 10px 0; padding: 10px; border-left: 4px solid #ccc; }}
        .critical {{ border-color: #dc3545; }}
        .high {{ border-color: #fd7e14; }}
        .medium {{ border-color: #ffc107; }}
        .low {{ border-color: #28a745; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>ACGS Security Test Report</h1>
        <p><strong>Status:</strong> <span class="status-{evaluation_result['overall_status'].lower()}">{evaluation_result['overall_status']}</span></p>
        <p><strong>Security Score:</strong> {evaluation_result['security_score']}/100</p>
        <p><strong>Constitutional Compliance:</strong> {evaluation_result['constitutional_compliance_status']}</p>
        <p><strong>Constitutional Hash:</strong> {self.constitutional_hash}</p>
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <h2>Executive Summary</h2>
    <p>{test_results.get('executive_summary', 'No executive summary available')}</p>

    <h2>Vulnerability Summary</h2>
    <table>
        <tr><th>Severity</th><th>Count</th><th>Threshold</th><th>Status</th></tr>
        <tr><td>Critical</td><td>{evaluation_result['vulnerability_counts'].get('critical', 0)}</td><td>{self.config['security_thresholds']['max_critical_vulnerabilities']}</td><td>{'FAIL' if evaluation_result['vulnerability_counts'].get('critical', 0) > self.config['security_thresholds']['max_critical_vulnerabilities'] else 'PASS'}</td></tr>
        <tr><td>High</td><td>{evaluation_result['vulnerability_counts'].get('high', 0)}</td><td>{self.config['security_thresholds']['max_high_vulnerabilities']}</td><td>{'FAIL' if evaluation_result['vulnerability_counts'].get('high', 0) > self.config['security_thresholds']['max_high_vulnerabilities'] else 'PASS'}</td></tr>
        <tr><td>Medium</td><td>{evaluation_result['vulnerability_counts'].get('medium', 0)}</td><td>{self.config['security_thresholds']['max_medium_vulnerabilities']}</td><td>{'FAIL' if evaluation_result['vulnerability_counts'].get('medium', 0) > self.config['security_thresholds']['max_medium_vulnerabilities'] else 'PASS'}</td></tr>
    </table>

    <h2>Threshold Violations</h2>
    {'<p>No threshold violations found.</p>' if not evaluation_result['threshold_violations'] else ''}
    {''.join([f'<div class="vulnerability {v["severity"].lower()}"><strong>{v["type"].replace("_", " ").title()}:</strong> {v["actual"]} (threshold: {v["threshold"]})</div>' for v in evaluation_result['threshold_violations']])}

    <h2>Recommendations</h2>
    <ul>
        {''.join([f'<li>{rec}</li>' for rec in test_results.get('recommendations', [])])}
    </ul>

    <h2>Next Steps</h2>
    <ul>
        {''.join([f'<li>{step}</li>' for step in test_results.get('next_steps', [])])}
    </ul>

    <div class="footer">
        <p><em>Generated by ACGS Security CI Integration - Constitutional Hash: {self.constitutional_hash}</em></p>
    </div>
</body>
</html>
"""

        report_path = Path("security_report.html")
        with open(report_path, "w") as f:
            f.write(html_content)

        return str(report_path)

    def _generate_junit_xml_report(
        self, test_results: dict[str, Any], evaluation_result: dict[str, Any]
    ) -> str:
        """
        Generate JUnit XML report for CI integration.

        Args:
            test_results: Security test results
            evaluation_result: Evaluation result

        Returns:
            Path to generated JUnit XML report
        """

        # Count test cases
        total_tests = 1  # Overall security test
        failures = len(evaluation_result["threshold_violations"])

        xml_content = f"""
<?xml version="1.0" encoding="UTF-8"?>
<testsuites name="ACGS Security Tests" tests="{total_tests}" failures="{failures}" time="{test_results.get('metadata', {}).get('total_execution_time_seconds', 0)}">
    <testsuite name="Security Assessment" tests="{total_tests}" failures="{failures}" time="{test_results.get('metadata', {}).get('total_execution_time_seconds', 0)}">
        <testcase name="Overall Security Assessment" classname="ACGS.Security" time="{test_results.get('metadata', {}).get('total_execution_time_seconds', 0)}">
            {''.join([f'<failure message="{v["type"]}: {v["actual"]} exceeds threshold {v["threshold"]}" type="{v["severity"]}">{v["type"]}: {v["actual"]} exceeds threshold {v["threshold"]}</failure>' for v in evaluation_result['threshold_violations']])}
        </testcase>
        <testcase name="Constitutional Compliance" classname="ACGS.Constitutional" time="1">
            {'<failure message="Constitutional compliance verification failed" type="CRITICAL">Constitutional compliance verification failed</failure>' if evaluation_result['constitutional_compliance_status'] == 'NON_COMPLIANT' else ''}
        </testcase>
    </testsuite>
</testsuites>
"""

        report_path = Path("security_report.xml")
        with open(report_path, "w") as f:
            f.write(xml_content)

        return str(report_path)

    async def _upload_to_artifacts(self, reports: dict[str, str]):
        """
        Upload reports to CI artifacts.

        Args:
            reports: Dict of report paths
        """

        # GitHub Actions
        if self.ci_environment == "github-actions":
            for report_type, report_path in reports.items():
                print(
                    f"::notice file={report_path}::Security report generated:"
                    f" {report_type}"
                )

        # GitLab CI
        elif self.ci_environment == "gitlab-ci":
            # GitLab CI automatically collects artifacts from specified paths
            pass

        # Other CI systems can be implemented here

        logger.info(f"Reports uploaded to CI artifacts: {list(reports.keys())}")

    async def _send_notifications(
        self, test_results: dict[str, Any], evaluation_result: dict[str, Any]
    ):
        """
        Send notifications based on test results.

        Args:
            test_results: Security test results
            evaluation_result: Evaluation result
        """

        # Skip notifications if no violations
        if not evaluation_result["threshold_violations"]:
            return

        # Slack notification
        if self.config["notifications"]["slack_webhook"]:
            await self._send_slack_notification(test_results, evaluation_result)

        # GitHub comment
        if (
            self.config["notifications"]["github_comment"]
            and self.ci_environment == "github-actions"
        ):
            await self._send_github_comment(test_results, evaluation_result)

        logger.info("Notifications sent for security test results")

    async def _send_slack_notification(
        self, test_results: dict[str, Any], evaluation_result: dict[str, Any]
    ):
        """
        Send Slack notification for security test results.

        Args:
            test_results: Security test results
            evaluation_result: Evaluation result
        """

        # Implementation would use actual Slack webhook
        logger.info("Slack notification sent (placeholder)")

    async def _send_github_comment(
        self, test_results: dict[str, Any], evaluation_result: dict[str, Any]
    ):
        """
        Send GitHub comment for security test results.

        Args:
            test_results: Security test results
            evaluation_result: Evaluation result
        """

        # Implementation would use GitHub API
        logger.info("GitHub comment sent (placeholder)")

    def _generate_timeout_result(self) -> dict[str, Any]:
        """
        Generate result for timed out tests.

        Returns:
            Timeout result dictionary
        """

        return {
            "metadata": {
                "status": "timeout",
                "generated_at": datetime.now(timezone.utc).isoformat(),
            },
            "overall_security_assessment": {
                "security_score": 0,
                "security_level": "Unknown",
                "total_vulnerabilities": {
                    "critical": 0,
                    "high": 0,
                    "medium": 0,
                    "low": 0,
                    "info": 0,
                },
            },
            "constitutional_compliance": {"compliance_verified": False},
            "error": "Security tests timed out",
        }


async def main():
    """
    Main function for CI integration.
    """

    # Get target URL from environment or command line
    target_url = os.getenv("ACGS_TARGET_URL", "http://localhost:8080")
    api_key = os.getenv("ACGS_API_KEY")

    # Initialize CI integration
    ci_integration = SecurityCIIntegration()

    # Run security tests with CI integration
    result = await ci_integration.run_security_tests_with_ci_integration(
        target_url, api_key
    )

    # Output results for CI
    print(f"\nSecurity Test Status: {result['evaluation']['overall_status']}")
    print(f"Security Score: {result['evaluation']['security_score']}/100")
    print(
        "Constitutional Compliance:"
        f" {result['evaluation']['constitutional_compliance_status']}"
    )

    # Set CI environment variables
    if result["evaluation"]["overall_status"] == "FAIL":
        print("::error::Security tests failed - critical vulnerabilities found")
        sys.exit(1)
    elif result["evaluation"]["overall_status"] == "WARN":
        print("::warning::Security tests passed with warnings")
        sys.exit(0)
    else:
        print("::notice::Security tests passed successfully")
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
