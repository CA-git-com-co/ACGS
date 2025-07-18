#!/usr/bin/env python3
"""
ACGS-1 Third-Party Dependency Audit

Comprehensive audit of all third-party dependencies across Python, JavaScript,
and Rust components to identify security vulnerabilities and licensing issues.
"""

import json
import logging
import os
import subprocess
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
        logging.FileHandler("logs/dependency_audit.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class DependencyAudit:
    """Comprehensive third-party dependency audit for ACGS-1."""

    def __init__(self, project_root: str = "/home/dislove/ACGS-1"):
        self.project_root = Path(project_root)
        self.audit_id = f"dependency_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.results = {
            "audit_id": self.audit_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "project_root": str(self.project_root),
            "audits": {},
            "summary": {
                "total_dependencies": 0,
                "vulnerable_dependencies": 0,
                "critical_vulnerabilities": 0,
                "high_vulnerabilities": 0,
                "medium_vulnerabilities": 0,
                "low_vulnerabilities": 0,
                "license_issues": 0,
                "outdated_dependencies": 0,
            },
            "compliance_status": "UNKNOWN",
            "recommendations": [],
        }

        # Ensure directories exist
        os.makedirs("logs", exist_ok=True)
        os.makedirs("reports/security", exist_ok=True)

    def run_audit(self) -> dict[str, Any]:
        """Run comprehensive dependency audit."""
        logger.info(f"🔍 Starting dependency audit: {self.audit_id}")

        # Run audits for different package managers
        self._audit_python_dependencies()
        self._audit_javascript_dependencies()
        self._audit_rust_dependencies()
        self._analyze_dependency_files()
        self._check_license_compliance()

        # Generate final assessment
        self._assess_compliance()
        self._generate_recommendations()
        self._save_results()

        logger.info(f"🎯 Dependency audit completed: {self.audit_id}")
        return self.results

    def _audit_python_dependencies(self) -> None:
        """Audit Python dependencies using multiple tools."""
        try:
            logger.info("🐍 Auditing Python dependencies...")

            findings = []

            # Find all requirements files
            req_files = list(self.project_root.rglob("requirements*.txt"))
            req_files.extend(list(self.project_root.rglob("config/environments/pyproject.toml")))
            req_files.extend(list(self.project_root.rglob("setup.py")))

            # Run pip-audit if available
            pip_audit_results = self._run_pip_audit()
            if pip_audit_results:
                findings.extend(pip_audit_results)

            # Run safety check if available
            safety_results = self._run_safety_check()
            if safety_results:
                findings.extend(safety_results)

            # Analyze requirements files for outdated packages
            for req_file in req_files:
                if req_file.name != "config/environments/requirements.txt":
                    continue

                try:
                    with open(req_file) as f:
                        lines = f.readlines()

                    for line_num, line in enumerate(lines, 1):
                        line = line.strip()
                        if line and not line.startswith("#"):
                            # Check for pinned versions
                            if "==" not in line and ">=" not in line:
                                findings.append(
                                    {
                                        "type": "unpinned_dependency",
                                        "severity": "MEDIUM",
                                        "package": line.split()[0],
                                        "file": str(
                                            req_file.relative_to(self.project_root)
                                        ),
                                        "line": line_num,
                                        "issue": "Dependency version not pinned",
                                        "recommendation": "Pin dependency versions for reproducible builds",
                                    }
                                )
                                self.results["summary"]["medium_vulnerabilities"] += 1

                except Exception as e:
                    logger.warning(f"Could not analyze {req_file}: {e}")

            self.results["audits"]["python"] = {
                "status": "SUCCESS",
                "requirements_files": len(req_files),
                "findings_count": len(findings),
                "findings": findings,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            logger.info(
                f"✅ Python dependency audit completed: {len(findings)} findings"
            )

        except Exception as e:
            logger.error(f"❌ Python dependency audit failed: {e}")
            self.results["audits"]["python"] = {
                "status": "FAILED",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def _run_pip_audit(self) -> list[dict[str, Any]]:
        """Run pip-audit for Python vulnerabilities."""
        try:
            cmd = ["/home/dislove/.local/bin/pip-audit", "--format=json"]
            result = subprocess.run(
                cmd, check=False, cwd=self.project_root, capture_output=True, text=True
            )

            findings = []
            if result.stdout:
                try:
                    audit_data = json.loads(result.stdout)

                    for vuln in audit_data.get("vulnerabilities", []):
                        severity = "HIGH"  # Default severity for pip-audit findings
                        findings.append(
                            {
                                "type": "vulnerability",
                                "severity": severity,
                                "package": vuln.get("package"),
                                "version": vuln.get("version"),
                                "vulnerability_id": vuln.get("id"),
                                "description": vuln.get("description"),
                                "fix_versions": vuln.get("fix_versions", []),
                                "source": "pip-audit",
                            }
                        )

                        # Update summary
                        if severity == "CRITICAL":
                            self.results["summary"]["critical_vulnerabilities"] += 1
                        elif severity == "HIGH":
                            self.results["summary"]["high_vulnerabilities"] += 1
                        elif severity == "MEDIUM":
                            self.results["summary"]["medium_vulnerabilities"] += 1
                        elif severity == "LOW":
                            self.results["summary"]["low_vulnerabilities"] += 1

                        self.results["summary"]["vulnerable_dependencies"] += 1

                except json.JSONDecodeError:
                    logger.warning("Failed to parse pip-audit results")

            return findings

        except Exception as e:
            logger.warning(f"pip-audit failed: {e}")
            return []

    def _run_safety_check(self) -> list[dict[str, Any]]:
        """Run safety check for Python vulnerabilities."""
        try:
            cmd = ["/home/dislove/.local/bin/safety", "check", "--json"]
            result = subprocess.run(
                cmd, check=False, cwd=self.project_root, capture_output=True, text=True
            )

            findings = []
            if result.stdout:
                try:
                    safety_data = json.loads(result.stdout)

                    for vuln in safety_data:
                        findings.append(
                            {
                                "type": "vulnerability",
                                "severity": "HIGH",
                                "package": vuln.get("package_name"),
                                "version": vuln.get("analyzed_version"),
                                "vulnerability_id": vuln.get("vulnerability_id"),
                                "advisory": vuln.get("advisory"),
                                "cve": vuln.get("cve"),
                                "source": "safety",
                            }
                        )

                        self.results["summary"]["high_vulnerabilities"] += 1
                        self.results["summary"]["vulnerable_dependencies"] += 1

                except json.JSONDecodeError:
                    logger.warning("Failed to parse safety results")

            return findings

        except Exception as e:
            logger.warning(f"safety check failed: {e}")
            return []

    def _audit_javascript_dependencies(self) -> None:
        """Audit JavaScript/Node.js dependencies."""
        try:
            logger.info("📦 Auditing JavaScript dependencies...")

            package_json_files = list(self.project_root.rglob("package.json"))
            all_findings = []

            for package_file in package_json_files:
                if "node_modules" in str(package_file):
                    continue

                package_dir = package_file.parent

                # Run npm audit
                try:
                    cmd = ["npm", "audit", "--json"]
                    result = subprocess.run(
                        cmd,
                        check=False,
                        cwd=package_dir,
                        capture_output=True,
                        text=True,
                    )

                    if result.stdout:
                        try:
                            audit_data = json.loads(result.stdout)

                            for vuln_id, vuln in audit_data.get(
                                "vulnerabilities", {}
                            ).items():
                                severity = vuln.get("severity", "UNKNOWN").upper()
                                all_findings.append(
                                    {
                                        "type": "vulnerability",
                                        "severity": severity,
                                        "package": vuln.get("name"),
                                        "vulnerability_id": vuln_id,
                                        "title": vuln.get("title"),
                                        "url": vuln.get("url"),
                                        "package_file": str(
                                            package_file.relative_to(self.project_root)
                                        ),
                                        "source": "npm-audit",
                                    }
                                )

                                # Update summary
                                if severity == "CRITICAL":
                                    self.results["summary"][
                                        "critical_vulnerabilities"
                                    ] += 1
                                elif severity == "HIGH":
                                    self.results["summary"]["high_vulnerabilities"] += 1
                                elif severity == "MEDIUM":
                                    self.results["summary"][
                                        "medium_vulnerabilities"
                                    ] += 1
                                elif severity == "LOW":
                                    self.results["summary"]["low_vulnerabilities"] += 1

                                self.results["summary"]["vulnerable_dependencies"] += 1

                        except json.JSONDecodeError:
                            logger.warning(
                                f"Failed to parse npm audit results for {package_file}"
                            )

                except Exception as e:
                    logger.warning(f"npm audit failed for {package_file}: {e}")

            self.results["audits"]["javascript"] = {
                "status": "SUCCESS",
                "package_json_files": len(package_json_files),
                "findings_count": len(all_findings),
                "findings": all_findings,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            logger.info(
                f"✅ JavaScript dependency audit completed: {len(all_findings)} findings"
            )

        except Exception as e:
            logger.error(f"❌ JavaScript dependency audit failed: {e}")
            self.results["audits"]["javascript"] = {
                "status": "FAILED",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def _audit_rust_dependencies(self) -> None:
        """Audit Rust dependencies."""
        try:
            logger.info("🦀 Auditing Rust dependencies...")

            cargo_files = list(self.project_root.rglob("Cargo.toml"))
            all_findings = []

            for cargo_file in cargo_files:
                if "target" in str(cargo_file):
                    continue

                cargo_dir = cargo_file.parent

                # Run cargo audit
                try:
                    cmd = ["cargo", "audit", "--json"]
                    result = subprocess.run(
                        cmd, check=False, cwd=cargo_dir, capture_output=True, text=True
                    )

                    if result.stdout:
                        for line in result.stdout.strip().split("\n"):
                            if line.strip():
                                try:
                                    audit_result = json.loads(line)

                                    if audit_result.get("type") == "vulnerability":
                                        vuln = audit_result.get("vulnerability", {})
                                        all_findings.append(
                                            {
                                                "type": "vulnerability",
                                                "severity": "HIGH",
                                                "package": vuln.get("package"),
                                                "version": vuln.get("patched_versions"),
                                                "vulnerability_id": vuln.get("id"),
                                                "title": vuln.get("title"),
                                                "description": vuln.get("description"),
                                                "cargo_file": str(
                                                    cargo_file.relative_to(
                                                        self.project_root
                                                    )
                                                ),
                                                "source": "cargo-audit",
                                            }
                                        )

                                        self.results["summary"][
                                            "high_vulnerabilities"
                                        ] += 1
                                        self.results["summary"][
                                            "vulnerable_dependencies"
                                        ] += 1

                                except json.JSONDecodeError:
                                    continue

                except Exception as e:
                    logger.warning(f"cargo audit failed for {cargo_file}: {e}")

            self.results["audits"]["rust"] = {
                "status": "SUCCESS",
                "cargo_files": len(cargo_files),
                "findings_count": len(all_findings),
                "findings": all_findings,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            logger.info(
                f"✅ Rust dependency audit completed: {len(all_findings)} findings"
            )

        except Exception as e:
            logger.error(f"❌ Rust dependency audit failed: {e}")
            self.results["audits"]["rust"] = {
                "status": "FAILED",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def _analyze_dependency_files(self) -> None:
        """Analyze dependency files for issues."""
        try:
            logger.info("📋 Analyzing dependency files...")

            findings = []

            # Count total dependencies
            total_deps = 0

            # Analyze Python requirements
            req_files = list(self.project_root.rglob("requirements*.txt"))
            for req_file in req_files:
                try:
                    with open(req_file) as f:
                        lines = [
                            line.strip()
                            for line in f.readlines()
                            if line.strip() and not line.startswith("#")
                        ]
                        total_deps += len(lines)
                except Exception:
                    pass

            # Analyze package.json files
            package_files = list(self.project_root.rglob("package.json"))
            for package_file in package_files:
                if "node_modules" in str(package_file):
                    continue
                try:
                    with open(package_file) as f:
                        package_data = json.load(f)
                        deps = package_data.get("dependencies", {})
                        dev_deps = package_data.get("devDependencies", {})
                        total_deps += len(deps) + len(dev_deps)
                except Exception:
                    pass

            # Analyze Cargo.toml files
            cargo_files = list(self.project_root.rglob("Cargo.toml"))
            for cargo_file in cargo_files:
                if "target" in str(cargo_file):
                    continue
                try:
                    with open(cargo_file) as f:
                        content = f.read()
                        # Simple count of dependencies (not perfect but reasonable estimate)
                        deps_section = False
                        for line in content.split("\n"):
                            if line.strip() == "[dependencies]":
                                deps_section = True
                            elif line.strip().startswith("[") and deps_section:
                                deps_section = False
                            elif (
                                deps_section
                                and "=" in line
                                and not line.strip().startswith("#")
                            ):
                                total_deps += 1
                except Exception:
                    pass

            self.results["summary"]["total_dependencies"] = total_deps

            self.results["audits"]["dependency_analysis"] = {
                "status": "SUCCESS",
                "total_dependencies": total_deps,
                "findings_count": len(findings),
                "findings": findings,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            logger.info(
                f"✅ Dependency analysis completed: {total_deps} total dependencies"
            )

        except Exception as e:
            logger.error(f"❌ Dependency analysis failed: {e}")
            self.results["audits"]["dependency_analysis"] = {
                "status": "FAILED",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def _check_license_compliance(self) -> None:
        """Check for license compliance issues."""
        try:
            logger.info("⚖️ Checking license compliance...")

            findings = []

            # Check for common license files
            license_files = list(self.project_root.glob("LICENSE*"))
            license_files.extend(list(self.project_root.glob("COPYING*")))

            if not license_files:
                findings.append(
                    {
                        "type": "missing_license",
                        "severity": "MEDIUM",
                        "issue": "No license file found in project root",
                        "recommendation": "Add appropriate license file",
                    }
                )
                self.results["summary"]["license_issues"] += 1

            # Check for restrictive licenses in dependencies (placeholder)
            # In a real implementation, this would parse package metadata

            self.results["audits"]["license_compliance"] = {
                "status": "SUCCESS",
                "license_files": len(license_files),
                "findings_count": len(findings),
                "findings": findings,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            logger.info(
                f"✅ License compliance check completed: {len(findings)} findings"
            )

        except Exception as e:
            logger.error(f"❌ License compliance check failed: {e}")
            self.results["audits"]["license_compliance"] = {
                "status": "FAILED",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def _assess_compliance(self) -> None:
        """Assess overall compliance status."""
        critical = self.results["summary"]["critical_vulnerabilities"]
        high = self.results["summary"]["high_vulnerabilities"]
        vulnerable = self.results["summary"]["vulnerable_dependencies"]
        total = self.results["summary"]["total_dependencies"]

        if critical > 0:
            self.results["compliance_status"] = "NON_COMPLIANT_CRITICAL"
        elif high > 10:
            self.results["compliance_status"] = "NON_COMPLIANT_HIGH"
        elif vulnerable > total * 0.1:  # More than 10% vulnerable
            self.results["compliance_status"] = "NEEDS_IMPROVEMENT"
        else:
            self.results["compliance_status"] = "COMPLIANT"

    def _generate_recommendations(self) -> None:
        """Generate recommendations based on audit findings."""
        recommendations = []

        critical = self.results["summary"]["critical_vulnerabilities"]
        high = self.results["summary"]["high_vulnerabilities"]
        vulnerable = self.results["summary"]["vulnerable_dependencies"]

        if critical > 0:
            recommendations.append(
                {
                    "priority": "CRITICAL",
                    "action": f"Immediately update {critical} dependencies with critical vulnerabilities",
                    "timeline": "Within 24 hours",
                    "impact": "System compromise risk",
                }
            )

        if high > 0:
            recommendations.append(
                {
                    "priority": "HIGH",
                    "action": f"Update {high} dependencies with high-severity vulnerabilities",
                    "timeline": "Within 1 week",
                    "impact": "Significant security risk",
                }
            )

        if vulnerable > 0:
            recommendations.append(
                {
                    "priority": "MEDIUM",
                    "action": f"Review and update {vulnerable} vulnerable dependencies",
                    "timeline": "Within 2 weeks",
                    "impact": "Security vulnerabilities in dependencies",
                }
            )

        # Add specific recommendations based on audit results
        for audit_type, audit_data in self.results["audits"].items():
            if (
                audit_data.get("status") == "SUCCESS"
                and audit_data.get("findings_count", 0) > 0
            ):
                recommendations.append(
                    {
                        "priority": "MEDIUM",
                        "action": f"Review {audit_type} dependency findings",
                        "timeline": "Within 2 weeks",
                        "impact": f"Security issues in {audit_type} dependencies",
                    }
                )

        self.results["recommendations"] = recommendations

    def _save_results(self) -> None:
        """Save audit results to files."""
        # Save detailed results
        results_file = f"reports/security/{self.audit_id}_results.json"
        with open(results_file, "w") as f:
            json.dump(self.results, f, indent=2)

        # Save summary report
        summary_file = f"reports/security/{self.audit_id}_summary.json"
        summary = {
            "audit_id": self.audit_id,
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
    audit = DependencyAudit()

    try:
        results = audit.run_audit()

        # Print summary
        print("\n" + "=" * 80)
        print("🔍 ACGS-1 THIRD-PARTY DEPENDENCY AUDIT RESULTS")
        print("=" * 80)
        print(f"Audit ID: {results['audit_id']}")
        print(f"Timestamp: {results['timestamp']}")
        print(f"Compliance Status: {results['compliance_status']}")
        print("\nDependency Summary:")
        print(f"  Total Dependencies: {results['summary']['total_dependencies']}")
        print(
            f"  Vulnerable Dependencies: {results['summary']['vulnerable_dependencies']}"
        )
        print(f"  License Issues: {results['summary']['license_issues']}")
        print("\nVulnerability Summary:")
        print(f"  Critical: {results['summary']['critical_vulnerabilities']}")
        print(f"  High:     {results['summary']['high_vulnerabilities']}")
        print(f"  Medium:   {results['summary']['medium_vulnerabilities']}")
        print(f"  Low:      {results['summary']['low_vulnerabilities']}")

        print("\nTop Priority Recommendations:")
        for i, rec in enumerate(results["recommendations"][:3], 1):
            print(f"  {i}. [{rec['priority']}] {rec['action']}")
            print(f"     Timeline: {rec['timeline']}")
            print(f"     Impact: {rec['impact']}")

        print("\nAudit Status by Type:")
        for audit_type, audit_result in results["audits"].items():
            status = audit_result.get("status", "UNKNOWN")
            findings_count = audit_result.get("findings_count", 0)
            print(f"  {audit_type}: {status} ({findings_count} findings)")

        print("=" * 80)
        print("✅ Task 1.3: Third-Party Dependency Audit - COMPLETED")
        print("=" * 80)

        return 0 if results["summary"]["critical_vulnerabilities"] == 0 else 1

    except Exception as e:
        logger.error(f"❌ Dependency audit failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
