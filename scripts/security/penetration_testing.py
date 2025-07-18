#!/usr/bin/env python3
"""
ACGS-1 Penetration Testing

Automated penetration testing suite for ACGS-1 services focusing on
common web application vulnerabilities and security misconfigurations.
"""

import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
import urllib3

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


# Disable SSL warnings for testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/penetration_testing.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class PenetrationTesting:
    """Automated penetration testing for ACGS-1."""

    def __init__(self, project_root: str = "/home/dislove/ACGS-1"):
        self.project_root = Path(project_root)
        self.test_id = f"pentest_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.results = {
            "test_id": self.test_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "project_root": str(self.project_root),
            "tests": {},
            "summary": {
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "critical_findings": 0,
                "high_findings": 0,
                "medium_findings": 0,
                "low_findings": 0,
                "services_tested": 0,
            },
            "compliance_status": "UNKNOWN",
            "recommendations": [],
        }

        # ACGS services to test
        self.services = [
            ("auth", 8000),
            ("ac", 8001),
            ("integrity", 8002),
            ("fv", 8003),
            ("gs", 8004),
            ("pgc", 8005),
            ("ec", 8006),
        ]

        # Common attack payloads
        self.payloads = {
            "sql_injection": [
                "' OR '1'='1",
                "'; DROP TABLE users; --",
                "' UNION SELECT * FROM users --",
                "1' OR 1=1 --",
            ],
            "xss": [
                "<script>alert('XSS')</script>",
                "javascript:alert('XSS')",
                "<img src=x onerror=alert('XSS')>",
                "';alert('XSS');//",
            ],
            "command_injection": ["; ls -la", "| whoami", "&& cat /etc/passwd", "`id`"],
            "path_traversal": [
                "../../../etc/passwd",
                "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
                "....//....//....//etc/passwd",
                "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            ],
        }

        # Ensure directories exist
        os.makedirs("logs", exist_ok=True)
        os.makedirs("reports/security", exist_ok=True)

    def run_penetration_tests(self) -> dict[str, Any]:
        """Run comprehensive penetration tests."""
        logger.info(f"🔍 Starting penetration testing: {self.test_id}")

        # Run different types of tests
        self._test_service_availability()
        self._test_authentication_bypass()
        self._test_injection_vulnerabilities()
        self._test_security_headers()
        self._test_session_management()
        self._test_authorization_bypass()

        # Generate final assessment
        self._assess_compliance()
        self._generate_recommendations()
        self._save_results()

        logger.info(f"🎯 Penetration testing completed: {self.test_id}")
        return self.results

    def _test_service_availability(self) -> None:
        """Test service availability and basic responses."""
        try:
            logger.info("🌐 Testing service availability...")

            findings = []
            available_services = 0

            for service_name, port in self.services:
                try:
                    response = requests.get(
                        f"http://localhost:{port}/health", timeout=5
                    )

                    if response.status_code == 200:
                        available_services += 1
                        findings.append(
                            {
                                "service": service_name,
                                "port": port,
                                "type": "service_available",
                                "severity": "LOW",
                                "status_code": response.status_code,
                                "response_time": response.elapsed.total_seconds(),
                                "issue": "Service is accessible",
                                "recommendation": "Ensure proper authentication is required",
                            }
                        )
                        self.results["summary"]["low_findings"] += 1
                    else:
                        findings.append(
                            {
                                "service": service_name,
                                "port": port,
                                "type": "service_error",
                                "severity": "MEDIUM",
                                "status_code": response.status_code,
                                "issue": f"Service returned error status: {response.status_code}",
                                "recommendation": "Investigate service health issues",
                            }
                        )
                        self.results["summary"]["medium_findings"] += 1

                except Exception as e:
                    findings.append(
                        {
                            "service": service_name,
                            "port": port,
                            "type": "service_unavailable",
                            "severity": "HIGH",
                            "error": str(e),
                            "issue": "Service is not accessible",
                            "recommendation": "Verify service is running and accessible",
                        }
                    )
                    self.results["summary"]["high_findings"] += 1

            self.results["summary"]["services_tested"] = available_services
            self.results["summary"]["total_tests"] += len(self.services)
            self.results["summary"]["passed_tests"] += available_services
            self.results["summary"]["failed_tests"] += (
                len(self.services) - available_services
            )

            self.results["tests"]["service_availability"] = {
                "status": "SUCCESS",
                "services_tested": len(self.services),
                "available_services": available_services,
                "findings_count": len(findings),
                "findings": findings,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            logger.info(
                f"✅ Service availability testing completed: {available_services}/{len(self.services)} services available"
            )

        except Exception as e:
            logger.error(f"❌ Service availability testing failed: {e}")
            self.results["tests"]["service_availability"] = {
                "status": "FAILED",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def _test_authentication_bypass(self) -> None:
        """Test for authentication bypass vulnerabilities."""
        try:
            logger.info("🔐 Testing authentication bypass...")

            findings = []

            for service_name, port in self.services:
                # Test endpoints without authentication
                test_endpoints = [
                    "/api/users",
                    "/api/admin",
                    "/api/config",
                    "/api/data",
                ]

                for endpoint in test_endpoints:
                    try:
                        response = requests.get(
                            f"http://localhost:{port}{endpoint}", timeout=5
                        )

                        if response.status_code == 200:
                            findings.append(
                                {
                                    "service": service_name,
                                    "port": port,
                                    "endpoint": endpoint,
                                    "type": "authentication_bypass",
                                    "severity": "HIGH",
                                    "status_code": response.status_code,
                                    "issue": "Endpoint accessible without authentication",
                                    "recommendation": "Implement proper authentication checks",
                                }
                            )
                            self.results["summary"]["high_findings"] += 1
                        elif response.status_code == 401 or response.status_code == 403:
                            # Good - authentication required
                            pass

                    except Exception:
                        # Service might not have this endpoint
                        pass

            self.results["tests"]["authentication_bypass"] = {
                "status": "SUCCESS",
                "findings_count": len(findings),
                "findings": findings,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            logger.info(
                f"✅ Authentication bypass testing completed: {len(findings)} findings"
            )

        except Exception as e:
            logger.error(f"❌ Authentication bypass testing failed: {e}")
            self.results["tests"]["authentication_bypass"] = {
                "status": "FAILED",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def _test_injection_vulnerabilities(self) -> None:
        """Test for injection vulnerabilities."""
        try:
            logger.info("💉 Testing injection vulnerabilities...")

            findings = []

            for service_name, port in self.services:
                # Test SQL injection in query parameters
                for payload in self.payloads["sql_injection"]:
                    try:
                        response = requests.get(
                            f"http://localhost:{port}/health",
                            params={"id": payload},
                            timeout=5,
                        )

                        # Check for SQL error messages
                        if any(
                            error in response.text.lower()
                            for error in [
                                "sql",
                                "mysql",
                                "postgresql",
                                "sqlite",
                                "syntax error",
                            ]
                        ):
                            findings.append(
                                {
                                    "service": service_name,
                                    "port": port,
                                    "type": "sql_injection",
                                    "severity": "CRITICAL",
                                    "payload": payload,
                                    "issue": "Potential SQL injection vulnerability detected",
                                    "recommendation": "Use parameterized queries and input validation",
                                }
                            )
                            self.results["summary"]["critical_findings"] += 1

                    except Exception:
                        pass

                # Test XSS in parameters
                for payload in self.payloads["xss"]:
                    try:
                        response = requests.get(
                            f"http://localhost:{port}/health",
                            params={"message": payload},
                            timeout=5,
                        )

                        if payload in response.text:
                            findings.append(
                                {
                                    "service": service_name,
                                    "port": port,
                                    "type": "xss",
                                    "severity": "HIGH",
                                    "payload": payload,
                                    "issue": "Potential XSS vulnerability detected",
                                    "recommendation": "Implement proper input sanitization and output encoding",
                                }
                            )
                            self.results["summary"]["high_findings"] += 1

                    except Exception:
                        pass

            self.results["tests"]["injection_vulnerabilities"] = {
                "status": "SUCCESS",
                "findings_count": len(findings),
                "findings": findings,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            logger.info(
                f"✅ Injection vulnerability testing completed: {len(findings)} findings"
            )

        except Exception as e:
            logger.error(f"❌ Injection vulnerability testing failed: {e}")
            self.results["tests"]["injection_vulnerabilities"] = {
                "status": "FAILED",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def _test_security_headers(self) -> None:
        """Test for missing security headers."""
        try:
            logger.info("🛡️ Testing security headers...")

            findings = []
            required_headers = [
                "X-Content-Type-Options",
                "X-Frame-Options",
                "X-XSS-Protection",
                "Strict-Transport-Security",
                "Content-Security-Policy",
            ]

            for service_name, port in self.services:
                try:
                    response = requests.get(
                        f"http://localhost:{port}/health", timeout=5
                    )
                    headers = dict(response.headers)

                    missing_headers = []
                    for header in required_headers:
                        if header not in headers:
                            missing_headers.append(header)

                    if missing_headers:
                        findings.append(
                            {
                                "service": service_name,
                                "port": port,
                                "type": "missing_security_headers",
                                "severity": "MEDIUM",
                                "missing_headers": missing_headers,
                                "issue": f"Missing {len(missing_headers)} security headers",
                                "recommendation": "Implement security middleware with proper headers",
                            }
                        )
                        self.results["summary"]["medium_findings"] += 1

                except Exception:
                    pass

            self.results["tests"]["security_headers"] = {
                "status": "SUCCESS",
                "findings_count": len(findings),
                "findings": findings,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            logger.info(
                f"✅ Security headers testing completed: {len(findings)} findings"
            )

        except Exception as e:
            logger.error(f"❌ Security headers testing failed: {e}")
            self.results["tests"]["security_headers"] = {
                "status": "FAILED",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def _test_session_management(self) -> None:
        """Test session management security."""
        try:
            logger.info("🍪 Testing session management...")

            findings = []

            for service_name, port in self.services:
                try:
                    response = requests.get(
                        f"http://localhost:{port}/health", timeout=5
                    )

                    # Check for session cookies
                    if response.cookies:
                        for cookie in response.cookies:
                            # Check for secure flag
                            if not cookie.secure:
                                findings.append(
                                    {
                                        "service": service_name,
                                        "port": port,
                                        "type": "insecure_cookie",
                                        "severity": "MEDIUM",
                                        "cookie_name": cookie.name,
                                        "issue": "Cookie missing Secure flag",
                                        "recommendation": "Set Secure flag on all cookies",
                                    }
                                )
                                self.results["summary"]["medium_findings"] += 1

                            # Check for HttpOnly flag
                            if not getattr(cookie, "httponly", False):
                                findings.append(
                                    {
                                        "service": service_name,
                                        "port": port,
                                        "type": "non_httponly_cookie",
                                        "severity": "MEDIUM",
                                        "cookie_name": cookie.name,
                                        "issue": "Cookie missing HttpOnly flag",
                                        "recommendation": "Set HttpOnly flag on session cookies",
                                    }
                                )
                                self.results["summary"]["medium_findings"] += 1

                except Exception:
                    pass

            self.results["tests"]["session_management"] = {
                "status": "SUCCESS",
                "findings_count": len(findings),
                "findings": findings,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            logger.info(
                f"✅ Session management testing completed: {len(findings)} findings"
            )

        except Exception as e:
            logger.error(f"❌ Session management testing failed: {e}")
            self.results["tests"]["session_management"] = {
                "status": "FAILED",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def _test_authorization_bypass(self) -> None:
        """Test for authorization bypass vulnerabilities."""
        try:
            logger.info("🔒 Testing authorization bypass...")

            findings = []

            # Test with invalid/expired tokens
            invalid_tokens = [
                "Bearer invalid_token",
                "Bearer expired_token_12345",
                "Bearer " + "a" * 100,  # Very long token
                "Basic invalid_credentials",
            ]

            for service_name, port in self.services:
                for token in invalid_tokens:
                    try:
                        headers = {"Authorization": token}
                        response = requests.get(
                            f"http://localhost:{port}/health",
                            headers=headers,
                            timeout=5,
                        )

                        # Should return 401 or 403 for invalid tokens
                        if response.status_code == 200:
                            findings.append(
                                {
                                    "service": service_name,
                                    "port": port,
                                    "type": "authorization_bypass",
                                    "severity": "HIGH",
                                    "token_type": token.split()[0],
                                    "issue": "Service accepts invalid authorization token",
                                    "recommendation": "Implement proper token validation",
                                }
                            )
                            self.results["summary"]["high_findings"] += 1

                    except Exception:
                        pass

            self.results["tests"]["authorization_bypass"] = {
                "status": "SUCCESS",
                "findings_count": len(findings),
                "findings": findings,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            logger.info(
                f"✅ Authorization bypass testing completed: {len(findings)} findings"
            )

        except Exception as e:
            logger.error(f"❌ Authorization bypass testing failed: {e}")
            self.results["tests"]["authorization_bypass"] = {
                "status": "FAILED",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def _assess_compliance(self) -> None:
        """Assess overall compliance status."""
        critical = self.results["summary"]["critical_findings"]
        high = self.results["summary"]["high_findings"]
        medium = self.results["summary"]["medium_findings"]

        if critical > 0:
            self.results["compliance_status"] = "NON_COMPLIANT_CRITICAL"
        elif high > 5:
            self.results["compliance_status"] = "NON_COMPLIANT_HIGH"
        elif high > 0 or medium > 10:
            self.results["compliance_status"] = "NEEDS_IMPROVEMENT"
        else:
            self.results["compliance_status"] = "COMPLIANT"

    def _generate_recommendations(self) -> None:
        """Generate recommendations based on test findings."""
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

        # Add specific recommendations based on test results
        for test_type, test_data in self.results["tests"].items():
            if (
                test_data.get("status") == "SUCCESS"
                and test_data.get("findings_count", 0) > 0
            ):
                recommendations.append(
                    {
                        "priority": "HIGH",
                        "action": f"Review and fix {test_type} security issues",
                        "timeline": "Within 1 week",
                        "impact": f"Security vulnerabilities in {test_type}",
                    }
                )

        self.results["recommendations"] = recommendations

    def _save_results(self) -> None:
        """Save test results to files."""
        # Save detailed results
        results_file = f"reports/security/{self.test_id}_results.json"
        with open(results_file, "w") as f:
            json.dump(self.results, f, indent=2)

        # Save summary report
        summary_file = f"reports/security/{self.test_id}_summary.json"
        summary = {
            "test_id": self.test_id,
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
    pentest = PenetrationTesting()

    try:
        results = pentest.run_penetration_tests()

        # Print summary
        print("\n" + "=" * 80)
        print("🔍 ACGS-1 PENETRATION TESTING RESULTS")
        print("=" * 80)
        print(f"Test ID: {results['test_id']}")
        print(f"Timestamp: {results['timestamp']}")
        print(f"Services Tested: {results['summary']['services_tested']}")
        print(f"Compliance Status: {results['compliance_status']}")
        print("\nTest Summary:")
        print(f"  Total Tests: {results['summary']['total_tests']}")
        print(f"  Passed: {results['summary']['passed_tests']}")
        print(f"  Failed: {results['summary']['failed_tests']}")
        print("\nFindings Summary:")
        print(f"  Critical: {results['summary']['critical_findings']}")
        print(f"  High:     {results['summary']['high_findings']}")
        print(f"  Medium:   {results['summary']['medium_findings']}")
        print(f"  Low:      {results['summary']['low_findings']}")

        print("\nTop Priority Recommendations:")
        for i, rec in enumerate(results["recommendations"][:3], 1):
            print(f"  {i}. [{rec['priority']}] {rec['action']}")
            print(f"     Timeline: {rec['timeline']}")
            print(f"     Impact: {rec['impact']}")

        print("\nTest Status by Type:")
        for test_type, test_result in results["tests"].items():
            status = test_result.get("status", "UNKNOWN")
            findings_count = test_result.get("findings_count", 0)
            print(f"  {test_type}: {status} ({findings_count} findings)")

        print("=" * 80)
        print("✅ Task 1.4: Penetration Testing - COMPLETED")
        print("=" * 80)

        return 0 if results["summary"]["critical_findings"] == 0 else 1

    except Exception as e:
        logger.error(f"❌ Penetration testing failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
