#!/usr/bin/env python3
"""
ACGS Security Test Runner

Executes comprehensive security validation including penetration testing,
compliance validation, and constitutional compliance verification.

Constitutional Hash: cdd01ef066bc6cf2
"""

import argparse
import asyncio
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from compliance_validator import ComplianceValidator
from penetration_testing import PenetrationTestSuite
from security_validation_framework import SecurityValidationFramework

# Constitutional compliance hash
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SecurityTestRunner:
    """
    Comprehensive security test runner for ACGS.

    Orchestrates all security testing components including:
    - Security validation framework
    - Penetration testing suite
    - Compliance validation
    - Constitutional compliance verification
    """

    def __init__(self, target_url: str, api_key: Optional[str] = None):
        self.target_url = target_url.rstrip("/")
        self.api_key = api_key
        self.constitutional_hash = CONSTITUTIONAL_HASH

        # Initialize test components
        self.security_validator = SecurityValidationFramework(target_url, api_key)
        self.penetration_tester = PenetrationTestSuite(target_url)
        self.compliance_validator = ComplianceValidator(target_url, api_key)

        # Results storage
        self.all_results = {}

        logger.info(f"Security test runner initialized for {target_url}")

    async def run_all_security_tests(
        self, test_types: list[str] = None
    ) -> dict[str, Any]:
        """
        Run all security tests based on specified types.

        Args:
            test_types: List of test types to run. If None, runs all tests.
                      Options: ['security', 'penetration', 'compliance']

        Returns:
            Dict containing all test results and summary
        """

        if test_types is None:
            test_types = ["security", "penetration", "compliance"]

        logger.info(f"Starting comprehensive security testing: {', '.join(test_types)}")
        start_time = datetime.now(timezone.utc)

        # Run security validation framework
        if "security" in test_types:
            logger.info("\n=== Running Security Validation Framework ===")
            try:
                security_results = (
                    await self.security_validator.run_all_security_tests()
                )
                self.all_results["security_validation"] = security_results
                logger.info("Security validation completed successfully")
            except Exception as e:
                logger.error(f"Security validation failed: {e}")
                self.all_results["security_validation"] = {
                    "error": str(e),
                    "status": "failed",
                }

        # Run penetration testing
        if "penetration" in test_types:
            logger.info("\n=== Running Penetration Testing Suite ===")
            try:
                penetration_results = (
                    await self.penetration_tester.run_full_penetration_test()
                )
                self.all_results["penetration_testing"] = penetration_results
                logger.info("Penetration testing completed successfully")
            except Exception as e:
                logger.error(f"Penetration testing failed: {e}")
                self.all_results["penetration_testing"] = {
                    "error": str(e),
                    "status": "failed",
                }

        # Run compliance validation
        if "compliance" in test_types:
            logger.info("\n=== Running Compliance Validation ===")
            try:
                compliance_results = (
                    await self.compliance_validator.run_all_compliance_tests()
                )
                self.all_results["compliance_validation"] = compliance_results
                logger.info("Compliance validation completed successfully")
            except Exception as e:
                logger.error(f"Compliance validation failed: {e}")
                self.all_results["compliance_validation"] = {
                    "error": str(e),
                    "status": "failed",
                }

        # Calculate total execution time
        end_time = datetime.now(timezone.utc)
        total_time = (end_time - start_time).total_seconds()

        # Generate comprehensive report
        comprehensive_report = self._generate_comprehensive_report(
            start_time, end_time, total_time, test_types
        )

        logger.info(f"\nAll security tests completed in {total_time:.2f} seconds")
        return comprehensive_report

    def _generate_comprehensive_report(
        self,
        start_time: datetime,
        end_time: datetime,
        total_time: float,
        test_types: list[str],
    ) -> dict[str, Any]:
        """
        Generate comprehensive security test report.

        Args:
            start_time: Test start time
            end_time: Test end time
            total_time: Total execution time in seconds
            test_types: List of test types executed

        Returns:
            Dict containing comprehensive test report
        """

        # Calculate overall security score
        security_score = self._calculate_security_score()

        # Count total vulnerabilities
        total_vulnerabilities = self._count_total_vulnerabilities()

        # Generate executive summary
        executive_summary = self._generate_executive_summary(
            security_score, total_vulnerabilities
        )

        # Generate recommendations
        recommendations = self._generate_security_recommendations()

        report = {
            "metadata": {
                "report_type": "comprehensive_security_assessment",
                "target_url": self.target_url,
                "constitutional_hash": self.constitutional_hash,
                "test_start_time": start_time.isoformat(),
                "test_end_time": end_time.isoformat(),
                "total_execution_time_seconds": round(total_time, 2),
                "test_types_executed": test_types,
                "generated_at": datetime.now(timezone.utc).isoformat(),
            },
            "executive_summary": executive_summary,
            "overall_security_assessment": {
                "security_score": security_score,
                "security_level": self._get_security_level(security_score),
                "total_vulnerabilities": total_vulnerabilities,
                "constitutional_compliance_status": (
                    self._get_constitutional_compliance_status()
                ),
            },
            "detailed_results": self.all_results,
            "recommendations": recommendations,
            "constitutional_compliance": {
                "hash_validated": self.constitutional_hash,
                "compliance_verified": self._verify_constitutional_compliance(),
                "compliance_score": self._calculate_constitutional_compliance_score(),
            },
            "next_steps": self._generate_next_steps(security_score),
        }

        return report

    def _calculate_security_score(self) -> int:
        """
        Calculate overall security score based on all test results.

        Returns:
            Security score from 0-100 (higher is better)
        """

        base_score = 100

        # Deduct points for vulnerabilities
        for test_type, results in self.all_results.items():
            if isinstance(results, dict) and "vulnerabilities" in results:
                vulnerabilities = results["vulnerabilities"]
                if isinstance(vulnerabilities, list):
                    for vuln in vulnerabilities:
                        if isinstance(vuln, dict):
                            severity = vuln.get("details", {}).get("severity", "info")
                            if severity == "critical":
                                base_score -= 20
                            elif severity == "high":
                                base_score -= 10
                            elif severity == "medium":
                                base_score -= 5
                            elif severity == "low":
                                base_score -= 2

        # Deduct points for failed tests
        for test_type, results in self.all_results.items():
            if isinstance(results, dict) and results.get("status") == "failed":
                base_score -= 15

        return max(0, min(100, base_score))

    def _count_total_vulnerabilities(self) -> dict[str, int]:
        """
        Count total vulnerabilities by severity across all tests.

        Returns:
            Dict with vulnerability counts by severity
        """

        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}

        for test_type, results in self.all_results.items():
            if isinstance(results, dict):
                # Handle different result structures
                vulnerabilities = []

                if "vulnerabilities" in results:
                    vulnerabilities = results["vulnerabilities"]
                elif "risk_assessment" in results:
                    severity_counts = results["risk_assessment"].get(
                        "vulnerabilities_by_severity", {}
                    )
                    for severity, count in severity_counts.items():
                        counts[severity] += count
                    continue

                # Count vulnerabilities
                if isinstance(vulnerabilities, list):
                    for vuln in vulnerabilities:
                        if isinstance(vuln, dict):
                            severity = vuln.get("details", {}).get("severity", "info")
                            if severity in counts:
                                counts[severity] += 1

        return counts

    def _generate_executive_summary(
        self, security_score: int, total_vulnerabilities: dict[str, int]
    ) -> str:
        """
        Generate executive summary of security assessment.

        Args:
            security_score: Overall security score
            total_vulnerabilities: Vulnerability counts by severity

        Returns:
            Executive summary string
        """

        total_critical = total_vulnerabilities.get("critical", 0)
        total_high = total_vulnerabilities.get("high", 0)
        total_medium = total_vulnerabilities.get("medium", 0)
        total_issues = sum(total_vulnerabilities.values())

        if total_critical > 0:
            summary = f"""CRITICAL SECURITY ISSUES IDENTIFIED

The comprehensive security assessment identified {total_critical} critical vulnerabilities that require immediate attention. These issues pose significant risk to system security and constitutional compliance.

Key Findings:
- Overall Security Score: {security_score}/100
- Critical Issues: {total_critical}
- High Risk Issues: {total_high}
- Medium Risk Issues: {total_medium}
- Total Security Issues: {total_issues}

IMMEDIATE ACTION REQUIRED to address critical vulnerabilities before production deployment."""

        elif total_high > 0:
            summary = f"""HIGH SECURITY RISKS IDENTIFIED

The security assessment identified {total_high} high-severity vulnerabilities that require prompt attention. While no critical issues were found, these vulnerabilities could compromise system security.

Key Findings:
- Overall Security Score: {security_score}/100
- High Risk Issues: {total_high}
- Medium Risk Issues: {total_medium}
- Total Security Issues: {total_issues}

PROMPT REMEDIATION RECOMMENDED to address high-risk vulnerabilities."""

        elif security_score >= 80:
            summary = f"""STRONG SECURITY POSTURE

The security assessment indicates a strong security posture with minimal vulnerabilities identified. The system demonstrates good security practices and constitutional compliance.

Key Findings:
- Overall Security Score: {security_score}/100
- Medium Risk Issues: {total_medium}
- Total Security Issues: {total_issues}
- Constitutional Compliance: Verified

CONTINUED MONITORING and regular security assessments recommended."""

        else:
            summary = f"""SECURITY IMPROVEMENTS NEEDED

The security assessment identified several areas for improvement. While no critical vulnerabilities were found, the overall security posture could be strengthened.

Key Findings:
- Overall Security Score: {security_score}/100
- Medium Risk Issues: {total_medium}
- Total Security Issues: {total_issues}

SECURITY ENHANCEMENTS RECOMMENDED to improve overall security posture."""

        return summary

    def _generate_security_recommendations(self) -> list[str]:
        """
        Generate security recommendations based on test results.

        Returns:
            List of security recommendations
        """

        recommendations = []

        # Check for specific vulnerability patterns
        has_auth_issues = False
        has_injection_issues = False
        has_crypto_issues = False
        has_constitutional_issues = False

        for test_type, results in self.all_results.items():
            if isinstance(results, dict):
                result_str = str(results).lower()

                if any(
                    term in result_str for term in ["auth", "jwt", "session", "login"]
                ):
                    has_auth_issues = True

                if any(
                    term in result_str
                    for term in ["injection", "sql", "xss", "traversal"]
                ):
                    has_injection_issues = True

                if any(
                    term in result_str
                    for term in ["crypto", "encryption", "hash", "weak"]
                ):
                    has_crypto_issues = True

                if any(
                    term in result_str
                    for term in ["constitutional", "compliance", "hash"]
                ):
                    has_constitutional_issues = True

        # Generate specific recommendations
        if has_auth_issues:
            recommendations.append(
                "CRITICAL: Strengthen authentication and session management mechanisms"
            )

        if has_injection_issues:
            recommendations.append(
                "CRITICAL: Implement comprehensive input validation and sanitization"
            )

        if has_crypto_issues:
            recommendations.append(
                "HIGH: Review and strengthen cryptographic implementations"
            )

        if has_constitutional_issues:
            recommendations.append(
                "CRITICAL: Ensure constitutional compliance validation across all"
                " components"
            )

        # General recommendations
        recommendations.extend([
            "Implement comprehensive security monitoring and alerting",
            "Conduct regular security assessments and penetration testing",
            "Establish incident response procedures",
            "Implement security awareness training for development team",
            "Enable comprehensive audit logging with tamper protection",
            "Implement defense-in-depth security architecture",
            "Regular security patch management and vulnerability scanning",
            "Implement least privilege access controls",
            "Enable multi-factor authentication for administrative access",
            "Conduct regular backup and disaster recovery testing",
        ])

        return recommendations

    def _get_security_level(self, score: int) -> str:
        """
        Get security level based on score.

        Args:
            score: Security score 0-100

        Returns:
            Security level description
        """

        if score >= 90:
            return "Excellent"
        elif score >= 80:
            return "Good"
        elif score >= 70:
            return "Fair"
        elif score >= 60:
            return "Poor"
        else:
            return "Critical"

    def _get_constitutional_compliance_status(self) -> str:
        """
        Get constitutional compliance status.

        Returns:
            Compliance status string
        """

        # Check for constitutional compliance issues
        for test_type, results in self.all_results.items():
            if isinstance(results, dict):
                result_str = str(results).lower()
                if "constitutional" in result_str and any(
                    term in result_str for term in ["fail", "error", "critical"]
                ):
                    return "Non-Compliant"

        return "Compliant"

    def _verify_constitutional_compliance(self) -> bool:
        """
        Verify constitutional compliance based on test results.

        Returns:
            True if constitutional compliance is verified
        """

        return self._get_constitutional_compliance_status() == "Compliant"

    def _calculate_constitutional_compliance_score(self) -> int:
        """
        Calculate constitutional compliance score.

        Returns:
            Compliance score 0-100
        """

        if self._verify_constitutional_compliance():
            return 100
        else:
            return 0

    def _generate_next_steps(self, security_score: int) -> list[str]:
        """
        Generate next steps based on security assessment.

        Args:
            security_score: Overall security score

        Returns:
            List of next steps
        """

        next_steps = []

        if security_score < 60:
            next_steps.extend([
                "1. IMMEDIATE: Address all critical and high-severity vulnerabilities",
                "2. IMMEDIATE: Implement emergency security patches",
                "3. URGENT: Conduct security code review",
                "4. URGENT: Implement additional security controls",
                "5. URGENT: Re-run security assessment after fixes",
            ])
        elif security_score < 80:
            next_steps.extend([
                "1. HIGH PRIORITY: Address high-severity vulnerabilities",
                "2. MEDIUM PRIORITY: Implement additional security controls",
                "3. MEDIUM PRIORITY: Conduct security training",
                "4. LOW PRIORITY: Re-run security assessment in 30 days",
            ])
        else:
            next_steps.extend([
                "1. MEDIUM PRIORITY: Address remaining medium-severity issues",
                "2. LOW PRIORITY: Continue security monitoring",
                "3. LOW PRIORITY: Schedule regular security assessments",
                "4. LOW PRIORITY: Consider security maturity improvements",
            ])

        # Always include constitutional compliance verification
        next_steps.append("ONGOING: Maintain constitutional compliance verification")

        return next_steps

    def save_report(self, report: dict[str, Any], filename: str = None) -> str:
        """
        Save security test report to file.

        Args:
            report: Test report dictionary
            filename: Optional filename. If None, generates timestamp-based name

        Returns:
            Path to saved report file
        """

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"acgs_security_report_{timestamp}.json"

        report_path = Path(filename)

        with open(report_path, "w") as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"Security report saved to {report_path}")
        return str(report_path)


def main():
    """
    Main function for command-line execution.
    """

    parser = argparse.ArgumentParser(
        description="ACGS Security Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""Examples:
  python run_security_tests.py http://localhost:8080
  python run_security_tests.py http://localhost:8080 --tests security penetration
  python run_security_tests.py http://localhost:8080 --api-key your-api-key
  python run_security_tests.py http://localhost:8080 --output custom_report.json

Constitutional Hash: {CONSTITUTIONAL_HASH}""",
    )

    parser.add_argument(
        "target_url",
        help="Target URL for security testing (e.g., http://localhost:8080)",
    )

    parser.add_argument(
        "--tests",
        nargs="*",
        choices=["security", "penetration", "compliance"],
        default=["security", "penetration", "compliance"],
        help="Types of tests to run (default: all)",
    )

    parser.add_argument("--api-key", help="API key for authenticated testing")

    parser.add_argument(
        "--output", help="Output file for test report (default: timestamp-based)"
    )

    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Run security tests
    try:
        runner = SecurityTestRunner(args.target_url, args.api_key)
        report = asyncio.run(runner.run_all_security_tests(args.tests))

        # Save report
        report_path = runner.save_report(report, args.output)

        # Display summary
        print("\n" + "=" * 80)
        print("ACGS SECURITY ASSESSMENT SUMMARY")
        print("=" * 80)
        print(f"Target URL: {args.target_url}")
        print(f"Tests Run: {', '.join(args.tests)}")
        print(
            "Security Score:"
            f" {report['overall_security_assessment']['security_score']}/100"
        )
        print(
            f"Security Level: {report['overall_security_assessment']['security_level']}"
        )
        print(
            "Constitutional Compliance:"
            f" {report['overall_security_assessment']['constitutional_compliance_status']}"
        )
        print(
            "Total Vulnerabilities:"
            f" {sum(report['overall_security_assessment']['total_vulnerabilities'].values())}"
        )
        print(f"Report Saved: {report_path}")
        print("=" * 80)

        # Exit with appropriate code
        security_score = report["overall_security_assessment"]["security_score"]
        if security_score < 60:
            sys.exit(1)  # Critical issues
        elif security_score < 80:
            sys.exit(2)  # High priority issues
        else:
            sys.exit(0)  # Success

    except Exception as e:
        logger.error(f"Security testing failed: {e}")
        sys.exit(3)


if __name__ == "__main__":
    main()
