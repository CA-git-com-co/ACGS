#!/usr/bin/env python3
"""
ACGS-1 Dependency Management Overhaul
=====================================

Comprehensive dependency audit, security scanning, and update management
for all package managers (npm, pip, cargo) across the ACGS-1 system.
"""

import json
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DependencyManager:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.audit_report = {
            "timestamp": datetime.now().isoformat(),
            "python_dependencies": {},
            "node_dependencies": {},
            "rust_dependencies": {},
            "security_vulnerabilities": [],
            "outdated_packages": [],
            "recommendations": [],
            "actions_taken": [],
        }

    def run_python_dependency_audit(self):
        """Audit Python dependencies for security and updates"""
        logger.info("🐍 Auditing Python dependencies...")

        # Find all requirements files
        req_files = list(self.project_root.rglob("requirements*.txt"))
        self.audit_report["python_dependencies"]["requirements_files"] = len(req_files)

        # Run pip-audit for security vulnerabilities
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "pip-audit"],
                check=False,
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode == 0:
                # Run security audit
                audit_result = subprocess.run(
                    [sys.executable, "-m", "pip_audit", "--format=json", "--desc"],
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=180,
                )

                if audit_result.returncode == 0 and audit_result.stdout:
                    try:
                        audit_data = json.loads(audit_result.stdout)
                        self.audit_report["security_vulnerabilities"].extend(
                            audit_data.get("vulnerabilities", [])
                        )
                        logger.info(
                            f"✅ Found {len(audit_data.get('vulnerabilities', []))} Python security issues"
                        )
                    except json.JSONDecodeError:
                        logger.warning("⚠️ Could not parse pip-audit output")

        except Exception as e:
            logger.error(f"❌ Python security audit failed: {e}")

        # Check for outdated packages
        try:
            outdated_result = subprocess.run(
                [sys.executable, "-m", "pip", "list", "--outdated", "--format=json"],
                check=False,
                capture_output=True,
                text=True,
                timeout=120,
            )

            if outdated_result.returncode == 0 and outdated_result.stdout:
                outdated_data = json.loads(outdated_result.stdout)
                self.audit_report["outdated_packages"].extend(
                    [
                        {
                            "package": pkg["name"],
                            "current": pkg["version"],
                            "latest": pkg["latest_version"],
                            "type": "python",
                        }
                        for pkg in outdated_data
                    ]
                )
                logger.info(f"📦 Found {len(outdated_data)} outdated Python packages")

        except Exception as e:
            logger.error(f"❌ Python outdated check failed: {e}")

    def run_node_dependency_audit(self):
        """Audit Node.js dependencies for security and updates"""
        logger.info("📦 Auditing Node.js dependencies...")

        # Find all package.json files
        package_files = list(self.project_root.rglob("package.json"))
        self.audit_report["node_dependencies"]["package_files"] = len(package_files)

        for package_file in package_files:
            package_dir = package_file.parent
            logger.info(f"  Checking {package_dir}")

            try:
                # Run npm audit
                audit_result = subprocess.run(
                    ["npm", "audit", "--json"],
                    check=False,
                    cwd=package_dir,
                    capture_output=True,
                    text=True,
                    timeout=120,
                )

                if audit_result.stdout:
                    try:
                        audit_data = json.loads(audit_result.stdout)
                        vulnerabilities = audit_data.get("vulnerabilities", {})
                        if vulnerabilities:
                            for vuln_name, vuln_data in vulnerabilities.items():
                                self.audit_report["security_vulnerabilities"].append(
                                    {
                                        "package": vuln_name,
                                        "severity": vuln_data.get(
                                            "severity", "unknown"
                                        ),
                                        "type": "node",
                                        "location": str(package_dir),
                                    }
                                )
                        logger.info(
                            f"✅ Found {len(vulnerabilities)} Node.js security issues in {package_dir}"
                        )
                    except json.JSONDecodeError:
                        logger.warning(
                            f"⚠️ Could not parse npm audit output for {package_dir}"
                        )

                # Check for outdated packages
                outdated_result = subprocess.run(
                    ["npm", "outdated", "--json"],
                    check=False,
                    cwd=package_dir,
                    capture_output=True,
                    text=True,
                    timeout=120,
                )

                if outdated_result.stdout:
                    try:
                        outdated_data = json.loads(outdated_result.stdout)
                        for pkg_name, pkg_data in outdated_data.items():
                            self.audit_report["outdated_packages"].append(
                                {
                                    "package": pkg_name,
                                    "current": pkg_data.get("current", "unknown"),
                                    "latest": pkg_data.get("latest", "unknown"),
                                    "type": "node",
                                    "location": str(package_dir),
                                }
                            )
                    except json.JSONDecodeError:
                        pass

            except Exception as e:
                logger.error(f"❌ Node.js audit failed for {package_dir}: {e}")

    def run_rust_dependency_audit(self):
        """Audit Rust dependencies for security and updates"""
        logger.info("🦀 Auditing Rust dependencies...")

        # Find all Cargo.toml files
        cargo_files = list(self.project_root.rglob("Cargo.toml"))
        self.audit_report["rust_dependencies"]["cargo_files"] = len(cargo_files)

        try:
            # Install cargo-audit if not present
            subprocess.run(
                ["cargo", "install", "cargo-audit"],
                check=False,
                capture_output=True,
                timeout=300,
            )

            # Run cargo audit
            audit_result = subprocess.run(
                ["cargo", "audit", "--format", "json"],
                check=False,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=120,
            )

            if audit_result.stdout:
                try:
                    audit_data = json.loads(audit_result.stdout)
                    vulnerabilities = audit_data.get("vulnerabilities", {}).get(
                        "list", []
                    )
                    for vuln in vulnerabilities:
                        self.audit_report["security_vulnerabilities"].append(
                            {
                                "package": vuln.get("package", {}).get(
                                    "name", "unknown"
                                ),
                                "severity": vuln.get("advisory", {}).get(
                                    "severity", "unknown"
                                ),
                                "type": "rust",
                                "advisory": vuln.get("advisory", {}).get("id", ""),
                            }
                        )
                    logger.info(f"✅ Found {len(vulnerabilities)} Rust security issues")
                except json.JSONDecodeError:
                    logger.warning("⚠️ Could not parse cargo audit output")

        except Exception as e:
            logger.error(f"❌ Rust audit failed: {e}")

    def apply_security_updates(self):
        """Apply critical security updates"""
        logger.info("🔒 Applying critical security updates...")

        critical_vulns = [
            v
            for v in self.audit_report["security_vulnerabilities"]
            if v.get("severity", "").lower() in ["critical", "high"]
        ]

        if not critical_vulns:
            logger.info("✅ No critical security vulnerabilities found")
            return

        logger.info(f"🚨 Found {len(critical_vulns)} critical vulnerabilities")

        # Group by package manager
        python_vulns = [v for v in critical_vulns if v.get("type") == "python"]
        node_vulns = [v for v in critical_vulns if v.get("type") == "node"]
        rust_vulns = [v for v in critical_vulns if v.get("type") == "rust"]

        # Apply Python security updates
        if python_vulns:
            logger.info(f"🐍 Updating {len(python_vulns)} Python packages...")
            for vuln in python_vulns[:5]:  # Limit to first 5 for safety
                package = vuln.get("package", "")
                if package:
                    try:
                        result = subprocess.run(
                            [
                                sys.executable,
                                "-m",
                                "pip",
                                "install",
                                "--upgrade",
                                package,
                            ],
                            check=False,
                            capture_output=True,
                            text=True,
                            timeout=120,
                        )

                        if result.returncode == 0:
                            self.audit_report["actions_taken"].append(
                                f"Updated Python package: {package}"
                            )
                            logger.info(f"✅ Updated {package}")
                        else:
                            logger.warning(
                                f"⚠️ Failed to update {package}: {result.stderr}"
                            )
                    except Exception as e:
                        logger.error(f"❌ Error updating {package}: {e}")

        # Apply Node.js security updates
        if node_vulns:
            logger.info(f"📦 Updating {len(node_vulns)} Node.js packages...")
            # Group by location
            locations = set(
                v.get("location", "") for v in node_vulns if v.get("location")
            )
            for location in locations:
                try:
                    result = subprocess.run(
                        ["npm", "audit", "fix", "--force"],
                        check=False,
                        cwd=location,
                        capture_output=True,
                        text=True,
                        timeout=300,
                    )

                    if result.returncode == 0:
                        self.audit_report["actions_taken"].append(
                            f"Applied npm audit fix in {location}"
                        )
                        logger.info(f"✅ Applied npm audit fix in {location}")
                    else:
                        logger.warning(f"⚠️ npm audit fix failed in {location}")
                except Exception as e:
                    logger.error(f"❌ Error applying npm fixes in {location}: {e}")

    def generate_recommendations(self):
        """Generate dependency management recommendations"""
        logger.info("💡 Generating recommendations...")

        recommendations = []

        # Security recommendations
        critical_count = len(
            [
                v
                for v in self.audit_report["security_vulnerabilities"]
                if v.get("severity", "").lower() in ["critical", "high"]
            ]
        )

        if critical_count > 0:
            recommendations.append(
                {
                    "priority": "CRITICAL",
                    "category": "Security",
                    "description": f"Address {critical_count} critical/high severity vulnerabilities immediately",
                    "action": "Run security updates and review vulnerable packages",
                }
            )

        # Outdated packages recommendations
        outdated_count = len(self.audit_report["outdated_packages"])
        if outdated_count > 20:
            recommendations.append(
                {
                    "priority": "HIGH",
                    "category": "Maintenance",
                    "description": f"{outdated_count} packages are outdated",
                    "action": "Schedule regular dependency updates",
                }
            )

        # Dependency consolidation
        req_files = self.audit_report["python_dependencies"].get(
            "requirements_files", 0
        )
        if req_files > 10:
            recommendations.append(
                {
                    "priority": "MEDIUM",
                    "category": "Organization",
                    "description": f"Found {req_files} requirements.txt files",
                    "action": "Consolidate duplicate dependency files",
                }
            )

        self.audit_report["recommendations"] = recommendations

        for rec in recommendations:
            logger.info(f"💡 {rec['priority']}: {rec['description']}")

    def save_audit_report(self):
        """Save comprehensive audit report"""
        report_path = self.project_root / "reports" / "dependency_audit_report.json"
        report_path.parent.mkdir(exist_ok=True)

        with open(report_path, "w") as f:
            json.dump(self.audit_report, f, indent=2)

        logger.info(f"📊 Audit report saved: {report_path}")

        # Print summary
        print("\n" + "=" * 60)
        print("🔍 DEPENDENCY AUDIT SUMMARY")
        print("=" * 60)
        print(
            f"📦 Python requirements files: {self.audit_report['python_dependencies'].get('requirements_files', 0)}"
        )
        print(
            f"📦 Node.js package files: {self.audit_report['node_dependencies'].get('package_files', 0)}"
        )
        print(
            f"🦀 Rust cargo files: {self.audit_report['rust_dependencies'].get('cargo_files', 0)}"
        )
        print(
            f"🚨 Security vulnerabilities: {len(self.audit_report['security_vulnerabilities'])}"
        )
        print(f"📈 Outdated packages: {len(self.audit_report['outdated_packages'])}")
        print(f"✅ Actions taken: {len(self.audit_report['actions_taken'])}")
        print(f"💡 Recommendations: {len(self.audit_report['recommendations'])}")

    def run_complete_audit(self):
        """Run complete dependency management audit"""
        logger.info("🚀 Starting ACGS-1 Dependency Management Overhaul...")

        self.run_python_dependency_audit()
        self.run_node_dependency_audit()
        self.run_rust_dependency_audit()
        self.apply_security_updates()
        self.generate_recommendations()
        self.save_audit_report()

        logger.info("✅ Dependency management overhaul complete!")


if __name__ == "__main__":
    manager = DependencyManager()
    manager.run_complete_audit()
