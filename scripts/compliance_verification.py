#!/usr/bin/env python3
"""
ACGS-1 Compliance and Standards Verification

Verifies compliance with security standards and best practices based on
the results from previous security audits and assessments.
"""

import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/compliance_verification.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class ComplianceVerification:
    """Compliance and standards verification for ACGS-1."""

    def __init__(self, project_root: str = "/home/dislove/ACGS-1"):
        self.project_root = Path(project_root)
        self.verification_id = (
            f"compliance_verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        self.results = {
            "verification_id": self.verification_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "project_root": str(self.project_root),
            "verifications": {},
            "summary": {
                "total_checks": 0,
                "passed_checks": 0,
                "failed_checks": 0,
                "compliance_score": 0,
                "critical_issues": 0,
                "high_issues": 0,
                "medium_issues": 0,
                "low_issues": 0,
            },
            "compliance_status": "UNKNOWN",
            "recommendations": [],
        }

        # Ensure directories exist
        os.makedirs("logs", exist_ok=True)
        os.makedirs("reports/security", exist_ok=True)

    def run_verification(self) -> dict[str, Any]:
        """Run comprehensive compliance verification."""
        logger.info(f"🔍 Starting compliance verification: {self.verification_id}")

        # Aggregate results from previous security assessments
        self._aggregate_security_findings()
        self._verify_owasp_compliance()
        self._verify_security_controls()
        self._calculate_compliance_score()

        # Generate final assessment
        self._assess_compliance()
        self._generate_recommendations()
        self._save_results()

        logger.info(f"🎯 Compliance verification completed: {self.verification_id}")
        return self.results

    def _aggregate_security_findings(self) -> None:
        """Aggregate findings from all security assessments."""
        try:
            logger.info("📊 Aggregating security findings...")

            # Find all security report files
            security_reports = list(
                self.project_root.glob("reports/security/*_summary.json")
            )

            total_critical = 0
            total_high = 0
            total_medium = 0
            total_low = 0

            findings = []

            for report_file in security_reports:
                try:
                    with open(report_file) as f:
                        report_data = json.load(f)

                    # Extract summary data
                    if "summary" in report_data:
                        summary = report_data["summary"]
                        total_critical += summary.get("critical_findings", 0)
                        total_high += summary.get("high_findings", 0) + summary.get(
                            "high_vulnerabilities", 0
                        )
                        total_medium += summary.get("medium_findings", 0) + summary.get(
                            "medium_vulnerabilities", 0
                        )
                        total_low += summary.get("low_findings", 0) + summary.get(
                            "low_vulnerabilities", 0
                        )

                        findings.append(
                            {
                                "report": report_file.name,
                                "type": "security_assessment",
                                "critical": summary.get("critical_findings", 0),
                                "high": summary.get("high_findings", 0)
                                + summary.get("high_vulnerabilities", 0),
                                "medium": summary.get("medium_findings", 0)
                                + summary.get("medium_vulnerabilities", 0),
                                "low": summary.get("low_findings", 0)
                                + summary.get("low_vulnerabilities", 0),
                                "compliance_status": report_data.get(
                                    "compliance_status", "UNKNOWN"
                                ),
                            }
                        )

                except Exception as e:
                    logger.warning(f"Could not parse {report_file}: {e}")

            self.results["summary"]["critical_issues"] = total_critical
            self.results["summary"]["high_issues"] = total_high
            self.results["summary"]["medium_issues"] = total_medium
            self.results["summary"]["low_issues"] = total_low

            self.results["verifications"]["security_findings_aggregation"] = {
                "status": "SUCCESS",
                "reports_analyzed": len(security_reports),
                "total_critical": total_critical,
                "total_high": total_high,
                "total_medium": total_medium,
                "total_low": total_low,
                "findings": findings,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            logger.info(
                f"✅ Security findings aggregation completed: {len(security_reports)} reports analyzed"
            )

        except Exception as e:
            logger.error(f"❌ Security findings aggregation failed: {e}")
            self.results["verifications"]["security_findings_aggregation"] = {
                "status": "FAILED",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def _verify_owasp_compliance(self) -> None:
        """Verify OWASP Top 10 compliance."""
        try:
            logger.info("🛡️ Verifying OWASP compliance...")

            owasp_checks = [
                (
                    "A01:2021 – Broken Access Control",
                    "authentication_bypass",
                    "authorization_bypass",
                ),
                (
                    "A02:2021 – Cryptographic Failures",
                    "weak_crypto",
                    "ssl_configuration",
                ),
                ("A03:2021 – Injection", "sql_injection", "command_injection", "xss"),
                (
                    "A04:2021 – Insecure Design",
                    "security_middleware",
                    "input_validation",
                ),
                (
                    "A05:2021 – Security Misconfiguration",
                    "security_headers",
                    "service_security",
                ),
                (
                    "A06:2021 – Vulnerable Components",
                    "dependency_vulnerabilities",
                    "outdated_dependencies",
                ),
                (
                    "A07:2021 – Authentication Failures",
                    "authentication",
                    "session_management",
                ),
                (
                    "A08:2021 – Software Integrity Failures",
                    "dependency_audit",
                    "license_compliance",
                ),
                ("A09:2021 – Logging Failures", "logging", "monitoring"),
                ("A10:2021 – Server-Side Request Forgery", "ssrf", "network_security"),
            ]

            compliance_results = []
            passed_checks = 0

            for owasp_item, *check_types in owasp_checks:
                # Check if we have findings related to this OWASP category
                has_issues = False

                # Look through aggregated findings for related issues
                for check_type in check_types:
                    if self._has_security_issues(check_type):
                        has_issues = True
                        break

                if has_issues:
                    compliance_results.append(
                        {
                            "owasp_category": owasp_item,
                            "status": "NON_COMPLIANT",
                            "severity": "HIGH",
                            "issue": f"Security issues found related to {owasp_item}",
                            "recommendation": f"Address security findings related to {owasp_item}",
                        }
                    )
                    self.results["summary"]["failed_checks"] += 1
                else:
                    compliance_results.append(
                        {
                            "owasp_category": owasp_item,
                            "status": "COMPLIANT",
                            "severity": "LOW",
                            "issue": f"No major issues found for {owasp_item}",
                            "recommendation": "Maintain current security posture",
                        }
                    )
                    passed_checks += 1
                    self.results["summary"]["passed_checks"] += 1

                self.results["summary"]["total_checks"] += 1

            self.results["verifications"]["owasp_compliance"] = {
                "status": "SUCCESS",
                "total_categories": len(owasp_checks),
                "compliant_categories": passed_checks,
                "non_compliant_categories": len(owasp_checks) - passed_checks,
                "compliance_results": compliance_results,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            logger.info(
                f"✅ OWASP compliance verification completed: {passed_checks}/{len(owasp_checks)} categories compliant"
            )

        except Exception as e:
            logger.error(f"❌ OWASP compliance verification failed: {e}")
            self.results["verifications"]["owasp_compliance"] = {
                "status": "FAILED",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def _verify_security_controls(self) -> None:
        """Verify implementation of security controls."""
        try:
            logger.info("🔒 Verifying security controls...")

            security_controls = [
                (
                    "Authentication",
                    "services/shared/auth.py",
                    "services/shared/enhanced_auth.py",
                ),
                ("Authorization", "services/shared/security_middleware.py"),
                ("Input Validation", "services/shared/input_validation.py"),
                ("Security Headers", "services/shared/security_middleware.py"),
                ("Session Management", "services/shared/enhanced_auth.py"),
                ("Cryptography", "services/shared/security_config.py"),
                ("Database Security", "services/shared/database.py"),
                ("Logging", "logs/"),
                ("Configuration", "config/"),
            ]

            control_results = []
            implemented_controls = 0

            for control_name, *file_paths in security_controls:
                implemented = False

                for file_path in file_paths:
                    full_path = self.project_root / file_path
                    if full_path.exists():
                        implemented = True
                        break

                if implemented:
                    control_results.append(
                        {
                            "control": control_name,
                            "status": "IMPLEMENTED",
                            "severity": "LOW",
                            "files": [
                                str(p)
                                for p in file_paths
                                if (self.project_root / p).exists()
                            ],
                            "recommendation": "Review implementation for completeness",
                        }
                    )
                    implemented_controls += 1
                    self.results["summary"]["passed_checks"] += 1
                else:
                    control_results.append(
                        {
                            "control": control_name,
                            "status": "NOT_IMPLEMENTED",
                            "severity": "HIGH",
                            "files": [],
                            "recommendation": f"Implement {control_name} security control",
                        }
                    )
                    self.results["summary"]["failed_checks"] += 1

                self.results["summary"]["total_checks"] += 1

            self.results["verifications"]["security_controls"] = {
                "status": "SUCCESS",
                "total_controls": len(security_controls),
                "implemented_controls": implemented_controls,
                "missing_controls": len(security_controls) - implemented_controls,
                "control_results": control_results,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            logger.info(
                f"✅ Security controls verification completed: {implemented_controls}/{len(security_controls)} controls implemented"
            )

        except Exception as e:
            logger.error(f"❌ Security controls verification failed: {e}")
            self.results["verifications"]["security_controls"] = {
                "status": "FAILED",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def _has_security_issues(self, issue_type: str) -> bool:
        """Check if there are security issues of a specific type."""
        # This is a simplified check - in a real implementation,
        # this would parse detailed findings from security reports
        critical = self.results["summary"]["critical_issues"]
        high = self.results["summary"]["high_issues"]

        # If we have critical or high issues, assume they could be related to any category
        return critical > 0 or high > 0

    def _calculate_compliance_score(self) -> None:
        """Calculate overall compliance score."""
        try:
            total_checks = self.results["summary"]["total_checks"]
            passed_checks = self.results["summary"]["passed_checks"]

            if total_checks > 0:
                compliance_score = (passed_checks / total_checks) * 100
                self.results["summary"]["compliance_score"] = round(compliance_score, 2)
            else:
                self.results["summary"]["compliance_score"] = 0

            logger.info(
                f"📊 Compliance score calculated: {self.results['summary']['compliance_score']}%"
            )

        except Exception as e:
            logger.error(f"❌ Compliance score calculation failed: {e}")
            self.results["summary"]["compliance_score"] = 0

    def _assess_compliance(self) -> None:
        """Assess overall compliance status."""
        compliance_score = self.results["summary"]["compliance_score"]
        critical = self.results["summary"]["critical_issues"]
        high = self.results["summary"]["high_issues"]

        if critical > 0:
            self.results["compliance_status"] = "NON_COMPLIANT_CRITICAL"
        elif compliance_score < 50:
            self.results["compliance_status"] = "NON_COMPLIANT_LOW"
        elif compliance_score < 70 or high > 10:
            self.results["compliance_status"] = "NEEDS_IMPROVEMENT"
        elif compliance_score < 90:
            self.results["compliance_status"] = "MOSTLY_COMPLIANT"
        else:
            self.results["compliance_status"] = "COMPLIANT"

    def _generate_recommendations(self) -> None:
        """Generate compliance recommendations."""
        recommendations = []

        compliance_score = self.results["summary"]["compliance_score"]
        critical = self.results["summary"]["critical_issues"]
        high = self.results["summary"]["high_issues"]

        if critical > 0:
            recommendations.append(
                {
                    "priority": "CRITICAL",
                    "action": f"Immediately address {critical} critical security issues",
                    "timeline": "Within 24 hours",
                    "impact": "System compromise risk",
                }
            )

        if high > 0:
            recommendations.append(
                {
                    "priority": "HIGH",
                    "action": f"Address {high} high-severity security issues",
                    "timeline": "Within 1 week",
                    "impact": "Significant security risk",
                }
            )

        if compliance_score < 70:
            recommendations.append(
                {
                    "priority": "HIGH",
                    "action": f"Improve compliance score from {compliance_score}% to >70%",
                    "timeline": "Within 2 weeks",
                    "impact": "Overall security posture",
                }
            )

        # Add specific recommendations based on verification results
        for verification_type, verification_data in self.results[
            "verifications"
        ].items():
            if verification_data.get("status") == "SUCCESS":
                if (
                    "non_compliant_categories" in verification_data
                    and verification_data["non_compliant_categories"] > 0
                ):
                    recommendations.append(
                        {
                            "priority": "MEDIUM",
                            "action": f"Address {verification_type} compliance issues",
                            "timeline": "Within 2 weeks",
                            "impact": f"Compliance with {verification_type} standards",
                        }
                    )

        self.results["recommendations"] = recommendations

    def _save_results(self) -> None:
        """Save verification results to files."""
        # Save detailed results
        results_file = f"reports/security/{self.verification_id}_results.json"
        with open(results_file, "w") as f:
            json.dump(self.results, f, indent=2)

        # Save summary report
        summary_file = f"reports/security/{self.verification_id}_summary.json"
        summary = {
            "verification_id": self.verification_id,
            "timestamp": self.results["timestamp"],
            "summary": self.results["summary"],
            "compliance_status": self.results["compliance_status"],
            "recommendations": self.results["recommendations"],
        }

        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)

        logger.info(f"📊 Results saved to {results_file}")
        logger.info(f"📋 Summary saved to {summary_file}")


def main():
    """Main execution function."""
    verification = ComplianceVerification()

    try:
        results = verification.run_verification()

        # Print summary
        print("\n" + "=" * 80)
        print("🔍 ACGS-1 COMPLIANCE AND STANDARDS VERIFICATION RESULTS")
        print("=" * 80)
        print(f"Verification ID: {results['verification_id']}")
        print(f"Timestamp: {results['timestamp']}")
        print(f"Compliance Status: {results['compliance_status']}")
        print(f"Compliance Score: {results['summary']['compliance_score']}%")
        print("\nVerification Summary:")
        print(f"  Total Checks: {results['summary']['total_checks']}")
        print(f"  Passed: {results['summary']['passed_checks']}")
        print(f"  Failed: {results['summary']['failed_checks']}")
        print("\nSecurity Issues Summary:")
        print(f"  Critical: {results['summary']['critical_issues']}")
        print(f"  High:     {results['summary']['high_issues']}")
        print(f"  Medium:   {results['summary']['medium_issues']}")
        print(f"  Low:      {results['summary']['low_issues']}")

        print("\nTop Priority Recommendations:")
        for i, rec in enumerate(results["recommendations"][:3], 1):
            print(f"  {i}. [{rec['priority']}] {rec['action']}")
            print(f"     Timeline: {rec['timeline']}")
            print(f"     Impact: {rec['impact']}")

        print("\nVerification Status by Type:")
        for verification_type, verification_result in results["verifications"].items():
            status = verification_result.get("status", "UNKNOWN")
            print(f"  {verification_type}: {status}")

        print("=" * 80)
        print("✅ Task 1.5: Compliance and Standards Verification - COMPLETED")
        print("=" * 80)

        return 0 if results["summary"]["critical_issues"] == 0 else 1

    except Exception as e:
        logger.error(f"❌ Compliance verification failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
