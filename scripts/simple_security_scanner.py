#!/usr/bin/env python3
"""
ACGS-1 Simple Security Scanner

A reliable security scanner that uses available tools to identify vulnerabilities
and security issues across the ACGS-1 system.
"""

import json
import logging
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/simple_security_scan.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class SimpleSecurityScanner:
    """Simple security scanner for ACGS-1."""

    def __init__(self, project_root: str = "/home/dislove/ACGS-1"):
        self.project_root = Path(project_root)
        self.scan_id = (
            f"simple_security_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        self.results = {
            "scan_id": self.scan_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "project_root": str(self.project_root),
            "scans": {},
            "summary": {
                "critical_findings": 0,
                "high_findings": 0,
                "medium_findings": 0,
                "low_findings": 0,
                "total_findings": 0,
            },
            "compliance_status": "UNKNOWN",
            "recommendations": [],
        }

        # Ensure directories exist
        os.makedirs("logs", exist_ok=True)
        os.makedirs("reports/security", exist_ok=True)

    def run_comprehensive_scan(self) -> Dict[str, Any]:
        """Run comprehensive security scan."""
        logger.info(f"🔍 Starting simple security scan: {self.scan_id}")

        # Run individual scans
        self._run_bandit_scan()
        self._run_safety_scan()
        self._run_pip_audit_scan()
        self._run_npm_audit_scan()
        self._run_infrastructure_scan()
        self._run_service_security_check()

        # Generate assessment
        self._assess_compliance()
        self._generate_recommendations()
        self._save_results()

        logger.info(f"🎯 Security scan completed: {self.scan_id}")
        return self.results

    def _run_bandit_scan(self) -> None:
        """Run Bandit security scan for Python code."""
        try:
            logger.info("🔍 Running Bandit scan...")

            cmd = [
                "/home/dislove/.local/bin/bandit",
                "-r",
                ".",
                "-f",
                "json",
                "-o",
                f"logs/{self.scan_id}_bandit.json",
                "--exclude",
                "./venv,./node_modules,./target,./blockchain/target",
            ]

            result = subprocess.run(
                cmd, cwd=self.project_root, capture_output=True, text=True
            )

            findings = []
            result_file = f"logs/{self.scan_id}_bandit.json"

            if os.path.exists(result_file):
                try:
                    with open(result_file, "r") as f:
                        bandit_results = json.load(f)

                    for result_item in bandit_results.get("results", []):
                        severity = result_item.get("issue_severity", "UNKNOWN").upper()
                        findings.append(
                            {
                                "file": result_item.get("filename"),
                                "line": result_item.get("line_number"),
                                "severity": severity,
                                "confidence": result_item.get(
                                    "issue_confidence", "UNKNOWN"
                                ).upper(),
                                "test_id": result_item.get("test_id"),
                                "test_name": result_item.get("test_name"),
                                "issue_text": result_item.get("issue_text"),
                            }
                        )

                        # Update summary
                        if severity == "HIGH":
                            self.results["summary"]["high_findings"] += 1
                        elif severity == "MEDIUM":
                            self.results["summary"]["medium_findings"] += 1
                        elif severity == "LOW":
                            self.results["summary"]["low_findings"] += 1

                except json.JSONDecodeError:
                    logger.warning("Failed to parse Bandit results")

            self.results["scans"]["bandit"] = {
                "status": "SUCCESS",
                "tool": "bandit",
                "findings_count": len(findings),
                "findings": findings,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            logger.info(f"✅ Bandit scan completed: {len(findings)} findings")

        except Exception as e:
            logger.error(f"❌ Bandit scan failed: {e}")
            self.results["scans"]["bandit"] = {
                "status": "FAILED",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def _run_safety_scan(self) -> None:
        """Run Safety scan for Python dependencies."""
        try:
            logger.info("🔍 Running Safety scan...")

            cmd = ["/home/dislove/.local/bin/safety", "check", "--json"]
            result = subprocess.run(
                cmd, cwd=self.project_root, capture_output=True, text=True
            )

            findings = []
            if result.stdout:
                try:
                    safety_results = json.loads(result.stdout)

                    for vuln in safety_results:
                        findings.append(
                            {
                                "package": vuln.get("package_name"),
                                "version": vuln.get("analyzed_version"),
                                "vulnerability_id": vuln.get("vulnerability_id"),
                                "advisory": vuln.get("advisory"),
                                "severity": "HIGH",
                                "cve": vuln.get("cve"),
                            }
                        )
                        self.results["summary"]["high_findings"] += 1

                except json.JSONDecodeError:
                    logger.warning("Failed to parse Safety results")

            self.results["scans"]["safety"] = {
                "status": "SUCCESS",
                "tool": "safety",
                "findings_count": len(findings),
                "findings": findings,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            logger.info(f"✅ Safety scan completed: {len(findings)} findings")

        except Exception as e:
            logger.error(f"❌ Safety scan failed: {e}")
            self.results["scans"]["safety"] = {
                "status": "FAILED",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def _run_pip_audit_scan(self) -> None:
        """Run pip-audit scan for Python dependencies."""
        try:
            logger.info("🔍 Running pip-audit scan...")

            cmd = ["/home/dislove/.local/bin/pip-audit", "--format=json"]
            result = subprocess.run(
                cmd, cwd=self.project_root, capture_output=True, text=True
            )

            findings = []
            if result.stdout:
                try:
                    audit_results = json.loads(result.stdout)

                    for vuln in audit_results.get("vulnerabilities", []):
                        findings.append(
                            {
                                "package": vuln.get("package"),
                                "version": vuln.get("version"),
                                "vulnerability_id": vuln.get("id"),
                                "description": vuln.get("description"),
                                "severity": "HIGH",
                                "fix_versions": vuln.get("fix_versions", []),
                            }
                        )
                        self.results["summary"]["high_findings"] += 1

                except json.JSONDecodeError:
                    logger.warning("Failed to parse pip-audit results")

            self.results["scans"]["pip_audit"] = {
                "status": "SUCCESS",
                "tool": "pip-audit",
                "findings_count": len(findings),
                "findings": findings,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            logger.info(f"✅ pip-audit scan completed: {len(findings)} findings")

        except Exception as e:
            logger.error(f"❌ pip-audit scan failed: {e}")
            self.results["scans"]["pip_audit"] = {
                "status": "FAILED",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def _run_npm_audit_scan(self) -> None:
        """Run npm audit scan for JavaScript dependencies."""
        try:
            logger.info("🔍 Running npm audit scan...")

            package_json_files = list(self.project_root.rglob("package.json"))
            all_findings = []

            for package_file in package_json_files:
                if "node_modules" in str(package_file):
                    continue

                package_dir = package_file.parent
                cmd = ["npm", "audit", "--json"]

                result = subprocess.run(
                    cmd, cwd=package_dir, capture_output=True, text=True
                )

                if result.stdout:
                    try:
                        audit_results = json.loads(result.stdout)

                        for vuln_id, vuln in audit_results.get(
                            "vulnerabilities", {}
                        ).items():
                            severity = vuln.get("severity", "UNKNOWN").upper()
                            all_findings.append(
                                {
                                    "package": vuln.get("name"),
                                    "severity": severity,
                                    "vulnerability_id": vuln_id,
                                    "title": vuln.get("title"),
                                    "url": vuln.get("url"),
                                    "package_file": str(
                                        package_file.relative_to(self.project_root)
                                    ),
                                }
                            )

                            # Update summary
                            if severity == "HIGH":
                                self.results["summary"]["high_findings"] += 1
                            elif severity == "MEDIUM":
                                self.results["summary"]["medium_findings"] += 1
                            elif severity == "LOW":
                                self.results["summary"]["low_findings"] += 1

                    except json.JSONDecodeError:
                        continue

            self.results["scans"]["npm_audit"] = {
                "status": "SUCCESS",
                "tool": "npm-audit",
                "findings_count": len(all_findings),
                "findings": all_findings,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            logger.info(f"✅ npm audit scan completed: {len(all_findings)} findings")

        except Exception as e:
            logger.error(f"❌ npm audit scan failed: {e}")
            self.results["scans"]["npm_audit"] = {
                "status": "FAILED",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def _run_infrastructure_scan(self) -> None:
        """Run infrastructure security scan."""
        try:
            logger.info("🔍 Running infrastructure scan...")

            findings = []

            # Check SSL/TLS configuration
            ssl_cert_path = self.project_root / "ssl" / "certs" / "acgs.pem"
            ssl_key_path = self.project_root / "ssl" / "private" / "acgs.key"

            if not ssl_cert_path.exists():
                findings.append(
                    {
                        "type": "ssl_configuration",
                        "severity": "HIGH",
                        "issue": "SSL certificate not found",
                        "file": str(ssl_cert_path),
                        "recommendation": "Generate or install SSL certificate",
                    }
                )
                self.results["summary"]["high_findings"] += 1

            if not ssl_key_path.exists():
                findings.append(
                    {
                        "type": "ssl_configuration",
                        "severity": "HIGH",
                        "issue": "SSL private key not found",
                        "file": str(ssl_key_path),
                        "recommendation": "Generate or install SSL private key",
                    }
                )
                self.results["summary"]["high_findings"] += 1

            # Check for exposed configuration files
            sensitive_files = [".env", "config.json", "secrets.json", "private.key"]

            for sensitive_file in sensitive_files:
                for found_file in self.project_root.rglob(sensitive_file):
                    if "node_modules" not in str(found_file) and "target" not in str(
                        found_file
                    ):
                        findings.append(
                            {
                                "type": "sensitive_file_exposure",
                                "severity": "MEDIUM",
                                "issue": f"Potentially sensitive file found: {sensitive_file}",
                                "file": str(found_file.relative_to(self.project_root)),
                                "recommendation": "Review file permissions and consider moving to secure location",
                            }
                        )
                        self.results["summary"]["medium_findings"] += 1

            self.results["scans"]["infrastructure"] = {
                "status": "SUCCESS",
                "tool": "infrastructure-scan",
                "findings_count": len(findings),
                "findings": findings,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            logger.info(f"✅ Infrastructure scan completed: {len(findings)} findings")

        except Exception as e:
            logger.error(f"❌ Infrastructure scan failed: {e}")
            self.results["scans"]["infrastructure"] = {
                "status": "FAILED",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def _run_service_security_check(self) -> None:
        """Run security check on running services."""
        try:
            logger.info("🔍 Running service security check...")

            import requests

            services = [
                ("auth", 8000),
                ("ac", 8001),
                ("integrity", 8002),
                ("fv", 8003),
                ("gs", 8004),
                ("pgc", 8005),
                ("ec", 8006),
            ]

            findings = []

            for service_name, port in services:
                try:
                    # Check health endpoint
                    response = requests.get(
                        f"http://localhost:{port}/health", timeout=5
                    )
                    headers = dict(response.headers)

                    # Check for missing security headers
                    required_headers = [
                        "X-Content-Type-Options",
                        "X-Frame-Options",
                        "X-XSS-Protection",
                        "Strict-Transport-Security",
                        "Content-Security-Policy",
                    ]

                    for header in required_headers:
                        if header not in headers:
                            findings.append(
                                {
                                    "service": service_name,
                                    "port": port,
                                    "type": "missing_security_header",
                                    "severity": "MEDIUM",
                                    "issue": f"Missing security header: {header}",
                                    "recommendation": "Implement security middleware",
                                }
                            )
                            self.results["summary"]["medium_findings"] += 1

                    # Check for HTTP instead of HTTPS
                    if response.url.startswith("http://"):
                        findings.append(
                            {
                                "service": service_name,
                                "port": port,
                                "type": "insecure_protocol",
                                "severity": "HIGH",
                                "issue": "Service accessible over HTTP instead of HTTPS",
                                "recommendation": "Enforce HTTPS for all services",
                            }
                        )
                        self.results["summary"]["high_findings"] += 1

                except Exception as e:
                    findings.append(
                        {
                            "service": service_name,
                            "port": port,
                            "type": "service_unavailable",
                            "severity": "LOW",
                            "issue": f"Service not accessible: {e}",
                            "recommendation": "Verify service is running and accessible",
                        }
                    )
                    self.results["summary"]["low_findings"] += 1

            self.results["scans"]["service_security"] = {
                "status": "SUCCESS",
                "tool": "service-security-check",
                "findings_count": len(findings),
                "findings": findings,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            logger.info(
                f"✅ Service security check completed: {len(findings)} findings"
            )

        except Exception as e:
            logger.error(f"❌ Service security check failed: {e}")
            self.results["scans"]["service_security"] = {
                "status": "FAILED",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

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
        elif high > 10:
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
                    "action": "Immediately address all critical security vulnerabilities",
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

        # Specific recommendations based on scan results
        service_scan = self.results["scans"].get("service_security", {})
        if service_scan.get("status") == "SUCCESS":
            missing_headers = sum(
                1
                for finding in service_scan.get("findings", [])
                if finding.get("type") == "missing_security_header"
            )
            if missing_headers > 0:
                recommendations.append(
                    {
                        "priority": "HIGH",
                        "action": "Implement security middleware across all services",
                        "timeline": "Within 3 days",
                        "impact": "XSS, CSRF, and other web vulnerabilities",
                    }
                )

        self.results["recommendations"] = recommendations

    def _save_results(self) -> None:
        """Save scan results to files."""
        # Save detailed results
        results_file = f"reports/security/{self.scan_id}_results.json"
        with open(results_file, "w") as f:
            json.dump(self.results, f, indent=2)

        # Save summary report
        summary_file = f"reports/security/{self.scan_id}_summary.json"
        summary = {
            "scan_id": self.scan_id,
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
    scanner = SimpleSecurityScanner()

    try:
        results = scanner.run_comprehensive_scan()

        # Print summary
        print("\n" + "=" * 80)
        print("🔍 ACGS-1 SECURITY VULNERABILITY SCAN RESULTS")
        print("=" * 80)
        print(f"Scan ID: {results['scan_id']}")
        print(f"Timestamp: {results['timestamp']}")
        print(f"Compliance Status: {results['compliance_status']}")
        print("\nFindings Summary:")
        print(f"  Critical: {results['summary']['critical_findings']}")
        print(f"  High:     {results['summary']['high_findings']}")
        print(f"  Medium:   {results['summary']['medium_findings']}")
        print(f"  Low:      {results['summary']['low_findings']}")
        print(f"  Total:    {results['summary']['total_findings']}")

        print("\nRecommendations:")
        for i, rec in enumerate(results["recommendations"], 1):
            print(f"  {i}. [{rec['priority']}] {rec['action']}")
            print(f"     Timeline: {rec['timeline']}")
            print(f"     Impact: {rec['impact']}")

        print("\nScan Status:")
        for scan_name, scan_result in results["scans"].items():
            status = scan_result.get("status", "UNKNOWN")
            findings_count = scan_result.get("findings_count", 0)
            print(f"  {scan_name}: {status} ({findings_count} findings)")

        print("=" * 80)

        return 0 if results["summary"]["critical_findings"] == 0 else 1

    except Exception as e:
        logger.error(f"❌ Security scan failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
