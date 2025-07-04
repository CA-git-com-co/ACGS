#!/usr/bin/env python3
"""
Comprehensive Dependency Audit Script
Performs thorough dependency vulnerability scanning and reporting.
"""

import json
import subprocess
import sys

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"



def run_dependency_audit():
    """Run comprehensive dependency vulnerability audit."""
    print("🔍 Running comprehensive dependency audit...")

    # Run pip-audit with detailed output
    try:
        result = subprocess.run(
            [
                "pip-audit",
                "--format=json",
                "--desc",
                "--output=dependency-audit-detailed.json",
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print("⚠️  Dependency vulnerabilities found")
            print(result.stdout)

            # Parse and categorize vulnerabilities
            with open("dependency-audit-detailed.json") as f:
                audit_data = json.load(f)

            critical_vulns = []
            high_vulns = []

            for vuln in audit_data.get("vulnerabilities", []):
                severity = vuln.get("severity", "unknown").lower()
                if severity in ["critical", "high"]:
                    if severity == "critical":
                        critical_vulns.append(vuln)
                    else:
                        high_vulns.append(vuln)

            print("📊 Vulnerability Summary:")
            print(f"  Critical: {len(critical_vulns)}")
            print(f"  High: {len(high_vulns)}")

            # Fail if critical vulnerabilities found
            if critical_vulns:
                print("❌ Critical vulnerabilities found - failing audit")
                sys.exit(1)
            elif high_vulns:
                print("⚠️  High severity vulnerabilities found - review required")
                sys.exit(1)
        else:
            print("✅ No dependency vulnerabilities found")

    except Exception as e:
        print(f"❌ Dependency audit failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_dependency_audit()
