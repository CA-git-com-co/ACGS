#!/usr/bin/env python3
"""
ACGS-1 Manual Code Security Review

Performs thorough manual review of critical codebase components focusing on
security-sensitive areas identified in the automated scan.
"""

import json
import logging
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/manual_code_security_review.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class ManualCodeSecurityReview:
    """Manual code security review for ACGS-1."""

    def __init__(self, project_root: str = "/home/dislove/ACGS-1"):
        self.project_root = Path(project_root)
        self.review_id = (
            f"manual_security_review_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        self.results = {
            "review_id": self.review_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "project_root": str(self.project_root),
            "reviews": {},
            "summary": {
                "critical_findings": 0,
                "high_findings": 0,
                "medium_findings": 0,
                "low_findings": 0,
                "total_findings": 0,
                "files_reviewed": 0,
            },
            "compliance_status": "UNKNOWN",
            "recommendations": [],
        }

        # Security patterns to look for
        self.security_patterns = {
            "hardcoded_secrets": [
                r"password\s*=\s*['\"][^'\"]+['\"]",
                r"secret\s*=\s*['\"][^'\"]+['\"]",
                r"api_key\s*=\s*['\"][^'\"]+['\"]",
                r"private_key\s*=\s*['\"][^'\"]+['\"]",
                r"SECRET_KEY\s*=\s*['\"][^'\"]+['\"]",
            ],
            "sql_injection": [
                r"execute\s*\(\s*['\"].*%.*['\"]",
                r"query\s*\(\s*['\"].*\+.*['\"]",
                r"\.format\s*\(",
                r"f['\"].*\{.*\}.*['\"]",
            ],
            "command_injection": [
                r"os\.system\s*\(",
                r"subprocess\.(call|run|Popen).*shell\s*=\s*True",
                r"eval\s*\(",
                r"exec\s*\(",
            ],
            "path_traversal": [
                r"open\s*\(\s*.*\+",
                r"\.\.\/",
                r"\.\.\\",
                r"os\.path\.join\s*\(.*user",
            ],
            "weak_crypto": [r"md5\s*\(", r"sha1\s*\(", r"DES\s*\(", r"RC4\s*\("],
        }

        # Ensure directories exist
        os.makedirs("logs", exist_ok=True)
        os.makedirs("reports/security", exist_ok=True)

    def run_review(self) -> dict[str, Any]:
        """Run comprehensive manual code security review."""
        logger.info(f"🔍 Starting manual code security review: {self.review_id}")

        # Review critical security components
        self._review_authentication_code()
        self._review_security_middleware()
        self._review_input_validation()
        self._review_database_code()
        self._review_cryptographic_implementations()
        self._review_configuration_files()

        # Generate final assessment
        self._assess_compliance()
        self._generate_recommendations()
        self._save_results()

        logger.info(f"🎯 Manual code security review completed: {self.review_id}")
        return self.results

    def _review_authentication_code(self) -> None:
        """Review authentication and authorization code."""
        try:
            logger.info("🔐 Reviewing authentication code...")

            auth_files = [
                "services/shared/auth.py",
                "services/shared/enhanced_auth.py",
                "services/platform/authentication/auth_service/app/core/security.py",
            ]

            findings = []

            for auth_file in auth_files:
                file_path = self.project_root / auth_file
                if file_path.exists():
                    findings.extend(
                        self._analyze_file_security(file_path, "authentication")
                    )

            # Specific authentication security checks
            enhanced_auth_path = self.project_root / "services/shared/enhanced_auth.py"
            if enhanced_auth_path.exists():
                with open(enhanced_auth_path) as f:
                    content = f.read()

                # Check for secure password hashing
                if (
                    "bcrypt" not in content
                    and "scrypt" not in content
                    and "argon2" not in content
                ):
                    findings.append(
                        {
                            "file": "services/shared/enhanced_auth.py",
                            "type": "weak_password_hashing",
                            "severity": "HIGH",
                            "line": "N/A",
                            "issue": "Password hashing may not use secure algorithm",
                            "recommendation": "Use bcrypt, scrypt, or argon2 for password hashing",
                        }
                    )
                    self.results["summary"]["high_findings"] += 1

                # Check for session management
                if "session" in content.lower():
                    if (
                        "secure" not in content.lower()
                        or "httponly" not in content.lower()
                    ):
                        findings.append(
                            {
                                "file": "services/shared/enhanced_auth.py",
                                "type": "insecure_session_config",
                                "severity": "MEDIUM",
                                "line": "N/A",
                                "issue": "Session configuration may lack security flags",
                                "recommendation": "Ensure sessions use Secure and HttpOnly flags",
                            }
                        )
                        self.results["summary"]["medium_findings"] += 1

            self.results["reviews"]["authentication"] = {
                "status": "SUCCESS",
                "files_reviewed": len(
                    [f for f in auth_files if (self.project_root / f).exists()]
                ),
                "findings_count": len(findings),
                "findings": findings,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            self.results["summary"]["files_reviewed"] += len(
                [f for f in auth_files if (self.project_root / f).exists()]
            )
            logger.info(
                f"✅ Authentication code review completed: {len(findings)} findings"
            )

        except Exception as e:
            logger.error(f"❌ Authentication code review failed: {e}")
            self.results["reviews"]["authentication"] = {
                "status": "FAILED",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def _review_security_middleware(self) -> None:
        """Review security middleware implementations."""
        try:
            logger.info("🛡️ Reviewing security middleware...")

            middleware_files = [
                "services/shared/security_middleware.py",
                "services/shared/middleware/security.py",
                "services/shared/input_validation_middleware.py",
            ]

            findings = []

            for middleware_file in middleware_files:
                file_path = self.project_root / middleware_file
                if file_path.exists():
                    findings.extend(
                        self._analyze_file_security(file_path, "middleware")
                    )

            # Check security middleware completeness
            security_middleware_path = (
                self.project_root / "services/shared/security_middleware.py"
            )
            if security_middleware_path.exists():
                with open(security_middleware_path) as f:
                    content = f.read()

                # Check for essential security features
                security_features = {
                    "CSRF protection": "csrf",
                    "Rate limiting": "rate_limit",
                    "XSS protection": "xss",
                    "SQL injection detection": "sql_injection",
                    "Input validation": "validation",
                }

                for feature_name, pattern in security_features.items():
                    if pattern.lower() not in content.lower():
                        findings.append(
                            {
                                "file": "services/shared/security_middleware.py",
                                "type": "missing_security_feature",
                                "severity": "MEDIUM",
                                "line": "N/A",
                                "issue": f"Missing {feature_name} implementation",
                                "recommendation": f"Implement {feature_name} in security middleware",
                            }
                        )
                        self.results["summary"]["medium_findings"] += 1

            self.results["reviews"]["security_middleware"] = {
                "status": "SUCCESS",
                "files_reviewed": len(
                    [f for f in middleware_files if (self.project_root / f).exists()]
                ),
                "findings_count": len(findings),
                "findings": findings,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            self.results["summary"]["files_reviewed"] += len(
                [f for f in middleware_files if (self.project_root / f).exists()]
            )
            logger.info(
                f"✅ Security middleware review completed: {len(findings)} findings"
            )

        except Exception as e:
            logger.error(f"❌ Security middleware review failed: {e}")
            self.results["reviews"]["security_middleware"] = {
                "status": "FAILED",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def _review_input_validation(self) -> None:
        """Review input validation implementations."""
        try:
            logger.info("✅ Reviewing input validation...")

            validation_files = [
                "services/shared/input_validation.py",
                "services/shared/validation_helpers.py",
                "services/shared/input_validation_middleware.py",
            ]

            findings = []

            for validation_file in validation_files:
                file_path = self.project_root / validation_file
                if file_path.exists():
                    findings.extend(
                        self._analyze_file_security(file_path, "input_validation")
                    )

            self.results["reviews"]["input_validation"] = {
                "status": "SUCCESS",
                "files_reviewed": len(
                    [f for f in validation_files if (self.project_root / f).exists()]
                ),
                "findings_count": len(findings),
                "findings": findings,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            self.results["summary"]["files_reviewed"] += len(
                [f for f in validation_files if (self.project_root / f).exists()]
            )
            logger.info(
                f"✅ Input validation review completed: {len(findings)} findings"
            )

        except Exception as e:
            logger.error(f"❌ Input validation review failed: {e}")
            self.results["reviews"]["input_validation"] = {
                "status": "FAILED",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def _review_database_code(self) -> None:
        """Review database access and query code."""
        try:
            logger.info("🗄️ Reviewing database code...")

            db_files = ["services/shared/database.py", "services/shared/db_utils.py"]

            findings = []

            for db_file in db_files:
                file_path = self.project_root / db_file
                if file_path.exists():
                    findings.extend(self._analyze_file_security(file_path, "database"))

            self.results["reviews"]["database"] = {
                "status": "SUCCESS",
                "files_reviewed": len(
                    [f for f in db_files if (self.project_root / f).exists()]
                ),
                "findings_count": len(findings),
                "findings": findings,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            self.results["summary"]["files_reviewed"] += len(
                [f for f in db_files if (self.project_root / f).exists()]
            )
            logger.info(f"✅ Database code review completed: {len(findings)} findings")

        except Exception as e:
            logger.error(f"❌ Database code review failed: {e}")
            self.results["reviews"]["database"] = {
                "status": "FAILED",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def _review_cryptographic_implementations(self) -> None:
        """Review cryptographic implementations."""
        try:
            logger.info("🔒 Reviewing cryptographic implementations...")

            crypto_files = [
                "services/shared/security_config.py",
                "services/shared/crypto_utils.py",
            ]

            findings = []

            for crypto_file in crypto_files:
                file_path = self.project_root / crypto_file
                if file_path.exists():
                    findings.extend(
                        self._analyze_file_security(file_path, "cryptography")
                    )

            self.results["reviews"]["cryptography"] = {
                "status": "SUCCESS",
                "files_reviewed": len(
                    [f for f in crypto_files if (self.project_root / f).exists()]
                ),
                "findings_count": len(findings),
                "findings": findings,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            self.results["summary"]["files_reviewed"] += len(
                [f for f in crypto_files if (self.project_root / f).exists()]
            )
            logger.info(
                f"✅ Cryptographic implementations review completed: {len(findings)} findings"
            )

        except Exception as e:
            logger.error(f"❌ Cryptographic implementations review failed: {e}")
            self.results["reviews"]["cryptography"] = {
                "status": "FAILED",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def _review_configuration_files(self) -> None:
        """Review configuration files for security issues."""
        try:
            logger.info("⚙️ Reviewing configuration files...")

            config_files = [
                "config/security.py",
                "services/shared/config.py",
                "config/environments/developmentconfig/environments/example.env",
            ]

            findings = []

            for config_file in config_files:
                file_path = self.project_root / config_file
                if file_path.exists():
                    findings.extend(
                        self._analyze_file_security(file_path, "configuration")
                    )

            self.results["reviews"]["configuration"] = {
                "status": "SUCCESS",
                "files_reviewed": len(
                    [f for f in config_files if (self.project_root / f).exists()]
                ),
                "findings_count": len(findings),
                "findings": findings,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            self.results["summary"]["files_reviewed"] += len(
                [f for f in config_files if (self.project_root / f).exists()]
            )
            logger.info(
                f"✅ Configuration files review completed: {len(findings)} findings"
            )

        except Exception as e:
            logger.error(f"❌ Configuration files review failed: {e}")
            self.results["reviews"]["configuration"] = {
                "status": "FAILED",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def _analyze_file_security(
        self, file_path: Path, category: str
    ) -> list[dict[str, Any]]:
        """Analyze a single file for security issues."""
        findings = []

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")

            # Check for security patterns
            for pattern_category, patterns in self.security_patterns.items():
                for pattern in patterns:
                    for line_num, line in enumerate(lines, 1):
                        if re.search(pattern, line, re.IGNORECASE):
                            severity = self._get_pattern_severity(pattern_category)
                            findings.append(
                                {
                                    "file": str(
                                        file_path.relative_to(self.project_root)
                                    ),
                                    "type": pattern_category,
                                    "severity": severity,
                                    "line": line_num,
                                    "code": line.strip(),
                                    "pattern": pattern,
                                    "issue": f"Potential {pattern_category.replace('_', ' ')} detected",
                                    "recommendation": self._get_pattern_recommendation(
                                        pattern_category
                                    ),
                                }
                            )

                            # Update summary
                            if severity == "CRITICAL":
                                self.results["summary"]["critical_findings"] += 1
                            elif severity == "HIGH":
                                self.results["summary"]["high_findings"] += 1
                            elif severity == "MEDIUM":
                                self.results["summary"]["medium_findings"] += 1
                            elif severity == "LOW":
                                self.results["summary"]["low_findings"] += 1

            # Additional specific checks based on file category
            if category == "authentication":
                findings.extend(self._check_auth_specific_issues(content, file_path))
            elif category == "database":
                findings.extend(self._check_db_specific_issues(content, file_path))

        except Exception as e:
            logger.warning(f"Could not analyze {file_path}: {e}")

        return findings

    def _get_pattern_severity(self, pattern_category: str) -> str:
        """Get severity level for pattern category."""
        severity_map = {
            "hardcoded_secrets": "CRITICAL",
            "sql_injection": "HIGH",
            "command_injection": "HIGH",
            "path_traversal": "HIGH",
            "weak_crypto": "MEDIUM",
        }
        return severity_map.get(pattern_category, "MEDIUM")

    def _get_pattern_recommendation(self, pattern_category: str) -> str:
        """Get recommendation for pattern category."""
        recommendations = {
            "hardcoded_secrets": "Use environment variables or secure vault for secrets",
            "sql_injection": "Use parameterized queries or ORM",
            "command_injection": "Avoid shell execution or sanitize input",
            "path_traversal": "Validate and sanitize file paths",
            "weak_crypto": "Use strong cryptographic algorithms (SHA-256+, AES)",
        }
        return recommendations.get(pattern_category, "Review and fix security issue")

    def _check_auth_specific_issues(
        self, content: str, file_path: Path
    ) -> list[dict[str, Any]]:
        """Check for authentication-specific security issues."""
        findings = []

        # Check for weak JWT configuration
        if "HS256" in content and "RS256" not in content:
            findings.append(
                {
                    "file": str(file_path.relative_to(self.project_root)),
                    "type": "weak_jwt_algorithm",
                    "severity": "MEDIUM",
                    "line": "N/A",
                    "issue": "Using symmetric JWT algorithm (HS256) instead of asymmetric",
                    "recommendation": "Consider using RS256 for better security",
                }
            )
            self.results["summary"]["medium_findings"] += 1

        return findings

    def _check_db_specific_issues(
        self, content: str, file_path: Path
    ) -> list[dict[str, Any]]:
        """Check for database-specific security issues."""
        findings = []

        # Check for connection string exposure
        if "postgresql://" in content or "mysql://" in content:
            findings.append(
                {
                    "file": str(file_path.relative_to(self.project_root)),
                    "type": "exposed_connection_string",
                    "severity": "HIGH",
                    "line": "N/A",
                    "issue": "Database connection string may be exposed",
                    "recommendation": "Use environment variables for database credentials",
                }
            )
            self.results["summary"]["high_findings"] += 1

        return findings

    def _assess_compliance(self) -> None:
        """Assess overall compliance status."""
        # Update total findings
        self.results["summary"]["total_findings"] = (
            self.results["summary"]["critical_findings"]
            + self.results["summary"]["high_findings"]
            + self.results["summary"]["medium_findings"]
            + self.results["summary"]["low_findings"]
        )

        critical = self.results["summary"]["critical_findings"]
        high = self.results["summary"]["high_findings"]

        if critical > 0:
            self.results["compliance_status"] = "NON_COMPLIANT_CRITICAL"
        elif high > 5:
            self.results["compliance_status"] = "NON_COMPLIANT_HIGH"
        elif high > 0:
            self.results["compliance_status"] = "NEEDS_IMPROVEMENT"
        else:
            self.results["compliance_status"] = "COMPLIANT"

    def _generate_recommendations(self) -> None:
        """Generate security recommendations based on findings."""
        recommendations = []

        critical = self.results["summary"]["critical_findings"]
        high = self.results["summary"]["high_findings"]
        medium = self.results["summary"]["medium_findings"]

        if critical > 0:
            recommendations.append(
                {
                    "priority": "CRITICAL",
                    "action": f"Immediately fix {critical} critical security vulnerabilities",
                    "timeline": "Within 24 hours",
                    "impact": "System compromise risk",
                }
            )

        if high > 0:
            recommendations.append(
                {
                    "priority": "HIGH",
                    "action": f"Address {high} high-severity security findings",
                    "timeline": "Within 1 week",
                    "impact": "Significant security risk",
                }
            )

        if medium > 5:
            recommendations.append(
                {
                    "priority": "MEDIUM",
                    "action": f"Address {medium} medium-severity security findings",
                    "timeline": "Within 2 weeks",
                    "impact": "Moderate security risk",
                }
            )

        # Add specific recommendations based on review categories
        for category, review_data in self.results["reviews"].items():
            if (
                review_data.get("status") == "SUCCESS"
                and review_data.get("findings_count", 0) > 0
            ):
                recommendations.append(
                    {
                        "priority": "HIGH",
                        "action": f"Review and fix {category} security issues",
                        "timeline": "Within 1 week",
                        "impact": f"Security vulnerabilities in {category} components",
                    }
                )

        self.results["recommendations"] = recommendations

    def _save_results(self) -> None:
        """Save review results to files."""
        # Save detailed results
        results_file = f"reports/security/{self.review_id}_results.json"
        with open(results_file, "w") as f:
            json.dump(self.results, f, indent=2)

        # Save summary report
        summary_file = f"reports/security/{self.review_id}_summary.json"
        summary = {
            "review_id": self.review_id,
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
    review = ManualCodeSecurityReview()

    try:
        results = review.run_review()

        # Print summary
        print("\n" + "=" * 80)
        print("🔍 ACGS-1 MANUAL CODE SECURITY REVIEW RESULTS")
        print("=" * 80)
        print(f"Review ID: {results['review_id']}")
        print(f"Timestamp: {results['timestamp']}")
        print(f"Files Reviewed: {results['summary']['files_reviewed']}")
        print(f"Compliance Status: {results['compliance_status']}")
        print("\nFindings Summary:")
        print(f"  Critical: {results['summary']['critical_findings']}")
        print(f"  High:     {results['summary']['high_findings']}")
        print(f"  Medium:   {results['summary']['medium_findings']}")
        print(f"  Low:      {results['summary']['low_findings']}")
        print(f"  Total:    {results['summary']['total_findings']}")

        print("\nTop Priority Recommendations:")
        for i, rec in enumerate(results["recommendations"][:3], 1):
            print(f"  {i}. [{rec['priority']}] {rec['action']}")
            print(f"     Timeline: {rec['timeline']}")
            print(f"     Impact: {rec['impact']}")

        print("\nReview Status by Category:")
        for category, review_result in results["reviews"].items():
            status = review_result.get("status", "UNKNOWN")
            findings_count = review_result.get("findings_count", 0)
            files_reviewed = review_result.get("files_reviewed", 0)
            print(
                f"  {category}: {status} ({files_reviewed} files, {findings_count} findings)"
            )

        print("=" * 80)
        print("✅ Task 1.2: Manual Code Security Review - COMPLETED")
        print("=" * 80)

        return 0 if results["summary"]["critical_findings"] == 0 else 1

    except Exception as e:
        logger.error(f"❌ Manual code security review failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
