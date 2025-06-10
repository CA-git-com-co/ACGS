#!/usr/bin/env python3
"""
ACGS-1 Phase 1: Security & Compliance Audit Script

This script implements comprehensive security auditing for the ACGS-1 codebase:
1. License compliance audit across all requirements.txt files
2. CVE vulnerability assessment
3. Dependency security scanning
4. GPL conflict detection and resolution

Usage:
    python scripts/phase1_security_audit.py --full-audit
    python scripts/phase1_security_audit.py --license-only
    python scripts/phase1_security_audit.py --cve-only
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("phase1_security_audit.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


class SecurityAuditor:
    """Comprehensive security auditor for ACGS-1 codebase."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.audit_results = {
            "timestamp": datetime.now().isoformat(),
            "license_audit": {},
            "cve_assessment": {},
            "dependency_scan": {},
            "gpl_conflicts": [],
            "recommendations": [],
        }

    def find_requirements_files(self) -> List[Path]:
        """Find all requirements.txt files in the project."""
        requirements_files = []

        # Search patterns for requirements files
        patterns = [
            "**/requirements.txt",
            "**/requirements-*.txt",
            "**/requirements/*.txt",
        ]

        for pattern in patterns:
            for file_path in self.project_root.glob(pattern):
                if file_path.is_file() and file_path.stat().st_size > 0:
                    requirements_files.append(file_path)

        # Remove duplicates and sort
        requirements_files = sorted(list(set(requirements_files)))
        logger.info(f"Found {len(requirements_files)} requirements files")

        return requirements_files

    def audit_licenses(self) -> Dict:
        """Audit licenses for all dependencies."""
        logger.info("Starting license compliance audit...")

        requirements_files = self.find_requirements_files()
        license_results = {
            "total_files": len(requirements_files),
            "files_analyzed": [],
            "license_summary": {},
            "gpl_conflicts": [],
            "unknown_licenses": [],
        }

        for req_file in requirements_files:
            logger.info(
                f"Analyzing licenses in: {req_file.relative_to(self.project_root)}"
            )

            try:
                # Use pip-licenses to analyze the requirements file
                cmd = [sys.executable, "-m", "pip", "install", "pip-licenses"]
                subprocess.run(cmd, capture_output=True, check=True)

                # Analyze licenses
                cmd = [
                    sys.executable,
                    "-m",
                    "pip_licenses",
                    "--from=file",
                    str(req_file),
                    "--format=json",
                ]
                result = subprocess.run(cmd, capture_output=True, text=True)

                if result.returncode == 0:
                    licenses_data = json.loads(result.stdout)
                    file_analysis = {
                        "file": str(req_file.relative_to(self.project_root)),
                        "packages": len(licenses_data),
                        "licenses": {},
                    }

                    for package in licenses_data:
                        license_name = package.get("License", "Unknown")
                        package_name = package.get("Name", "Unknown")

                        # Check for GPL conflicts
                        if (
                            "GPL" in license_name.upper()
                            or "GNU" in license_name.upper()
                        ):
                            license_results["gpl_conflicts"].append(
                                {
                                    "package": package_name,
                                    "license": license_name,
                                    "file": str(
                                        req_file.relative_to(self.project_root)
                                    ),
                                }
                            )

                        # Track license distribution
                        if license_name not in license_results["license_summary"]:
                            license_results["license_summary"][license_name] = 0
                        license_results["license_summary"][license_name] += 1

                        file_analysis["licenses"][package_name] = license_name

                    license_results["files_analyzed"].append(file_analysis)

                else:
                    logger.warning(f"Failed to analyze {req_file}: {result.stderr}")

            except Exception as e:
                logger.error(f"Error analyzing {req_file}: {e}")

        self.audit_results["license_audit"] = license_results
        return license_results

    def assess_cve_vulnerabilities(self) -> Dict:
        """Assess CVE vulnerabilities in dependencies."""
        logger.info("Starting CVE vulnerability assessment...")

        cve_results = {
            "scan_timestamp": datetime.now().isoformat(),
            "vulnerabilities": [],
            "critical_count": 0,
            "high_count": 0,
            "medium_count": 0,
            "low_count": 0,
        }

        requirements_files = self.find_requirements_files()

        for req_file in requirements_files:
            logger.info(
                f"Scanning vulnerabilities in: {req_file.relative_to(self.project_root)}"
            )

            try:
                # Use safety to scan for vulnerabilities
                cmd = [sys.executable, "-m", "pip", "install", "safety"]
                subprocess.run(cmd, capture_output=True, check=True)

                # Run safety check
                cmd = [
                    sys.executable,
                    "-m",
                    "safety",
                    "check",
                    "--requirements",
                    str(req_file),
                    "--json",
                ]
                result = subprocess.run(cmd, capture_output=True, text=True)

                if result.stdout:
                    try:
                        safety_data = json.loads(result.stdout)
                        for vuln in safety_data:
                            severity = self._determine_severity(vuln)
                            vulnerability = {
                                "package": vuln.get("package_name", "Unknown"),
                                "version": vuln.get("installed_version", "Unknown"),
                                "vulnerability_id": vuln.get(
                                    "vulnerability_id", "Unknown"
                                ),
                                "severity": severity,
                                "description": vuln.get("advisory", "No description"),
                                "file": str(req_file.relative_to(self.project_root)),
                            }

                            cve_results["vulnerabilities"].append(vulnerability)
                            cve_results[f"{severity.lower()}_count"] += 1

                    except json.JSONDecodeError:
                        logger.warning(f"Could not parse safety output for {req_file}")

            except Exception as e:
                logger.error(f"Error scanning {req_file} for vulnerabilities: {e}")

        self.audit_results["cve_assessment"] = cve_results
        return cve_results

    def _determine_severity(self, vulnerability: Dict) -> str:
        """Determine vulnerability severity based on available data."""
        advisory = vulnerability.get("advisory", "").lower()

        if any(
            word in advisory for word in ["critical", "remote code execution", "rce"]
        ):
            return "CRITICAL"
        elif any(
            word in advisory
            for word in ["high", "privilege escalation", "sql injection"]
        ):
            return "HIGH"
        elif any(word in advisory for word in ["medium", "denial of service", "dos"]):
            return "MEDIUM"
        else:
            return "LOW"

    def scan_dependencies(self) -> Dict:
        """Comprehensive dependency scanning."""
        logger.info("Starting comprehensive dependency scan...")

        dependency_results = {
            "total_dependencies": 0,
            "outdated_packages": [],
            "security_issues": [],
            "recommendations": [],
        }

        try:
            # Use pip-audit for comprehensive scanning
            cmd = [sys.executable, "-m", "pip", "install", "pip-audit"]
            subprocess.run(cmd, capture_output=True, check=True)

            # Run pip-audit
            cmd = [sys.executable, "-m", "pip_audit", "--desc", "--format=json"]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0 and result.stdout:
                audit_data = json.loads(result.stdout)
                dependency_results.update(audit_data)

        except Exception as e:
            logger.error(f"Error running dependency scan: {e}")

        self.audit_results["dependency_scan"] = dependency_results
        return dependency_results

    def generate_recommendations(self) -> List[str]:
        """Generate security recommendations based on audit results."""
        recommendations = []

        # License recommendations
        gpl_conflicts = self.audit_results["license_audit"].get("gpl_conflicts", [])
        if gpl_conflicts:
            recommendations.append(
                f"CRITICAL: Found {len(gpl_conflicts)} GPL license conflicts. "
                "Review and replace GPL-licensed dependencies to maintain MIT compatibility."
            )

        # CVE recommendations
        cve_data = self.audit_results["cve_assessment"]
        critical_vulns = cve_data.get("critical_count", 0)
        high_vulns = cve_data.get("high_count", 0)

        if critical_vulns > 0:
            recommendations.append(
                f"CRITICAL: {critical_vulns} critical vulnerabilities found. "
                "Update affected packages immediately."
            )

        if high_vulns > 0:
            recommendations.append(
                f"HIGH: {high_vulns} high-severity vulnerabilities found. "
                "Schedule updates for affected packages within 48 hours."
            )

        # General recommendations
        recommendations.extend(
            [
                "Implement automated dependency updates using Dependabot",
                "Add security scanning to CI/CD pipeline",
                "Create NOTICE.md file with complete license attributions",
                "Establish security review process for new dependencies",
            ]
        )

        self.audit_results["recommendations"] = recommendations
        return recommendations

    def generate_report(self, output_file: Optional[Path] = None) -> Path:
        """Generate comprehensive security audit report."""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.project_root / f"security_audit_report_{timestamp}.json"

        # Generate recommendations
        self.generate_recommendations()

        # Write report
        with open(output_file, "w") as f:
            json.dump(self.audit_results, f, indent=2)

        logger.info(f"Security audit report generated: {output_file}")
        return output_file

    def run_full_audit(self) -> Dict:
        """Run complete security audit."""
        logger.info("Starting full security audit...")

        # Run all audit components
        self.audit_licenses()
        self.assess_cve_vulnerabilities()
        self.scan_dependencies()

        # Generate report
        report_file = self.generate_report()

        # Print summary
        self._print_summary()

        return self.audit_results

    def _print_summary(self):
        """Print audit summary to console."""
        print("\n" + "=" * 60)
        print("ACGS-1 SECURITY AUDIT SUMMARY")
        print("=" * 60)

        # License summary
        license_data = self.audit_results["license_audit"]
        gpl_conflicts = len(license_data.get("gpl_conflicts", []))
        print(f"📄 License Audit:")
        print(f"   - Files analyzed: {license_data.get('total_files', 0)}")
        print(f"   - GPL conflicts: {gpl_conflicts}")

        # CVE summary
        cve_data = self.audit_results["cve_assessment"]
        print(f"🔒 CVE Assessment:")
        print(f"   - Critical: {cve_data.get('critical_count', 0)}")
        print(f"   - High: {cve_data.get('high_count', 0)}")
        print(f"   - Medium: {cve_data.get('medium_count', 0)}")
        print(f"   - Low: {cve_data.get('low_count', 0)}")

        # Recommendations
        recommendations = self.audit_results.get("recommendations", [])
        print(f"💡 Recommendations: {len(recommendations)} items")

        print("=" * 60)


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description="ACGS-1 Security Audit Tool")
    parser.add_argument(
        "--full-audit", action="store_true", help="Run complete security audit"
    )
    parser.add_argument(
        "--license-only", action="store_true", help="Run license audit only"
    )
    parser.add_argument(
        "--cve-only", action="store_true", help="Run CVE assessment only"
    )
    parser.add_argument(
        "--project-root", type=Path, default=Path.cwd(), help="Project root directory"
    )

    args = parser.parse_args()

    # Initialize auditor
    auditor = SecurityAuditor(args.project_root)

    try:
        if args.full_audit or (not args.license_only and not args.cve_only):
            auditor.run_full_audit()
        elif args.license_only:
            auditor.audit_licenses()
            auditor.generate_report()
        elif args.cve_only:
            auditor.assess_cve_vulnerabilities()
            auditor.generate_report()

    except KeyboardInterrupt:
        logger.info("Audit interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Audit failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
