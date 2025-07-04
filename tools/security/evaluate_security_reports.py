#!/usr/bin/env python3
"""
Security Reports Evaluation Script
Evaluates security scan results and enforces security gates.
"""

import json
import sys
from pathlib import Path

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"



def evaluate_security_reports():
    """Evaluate all security reports and determine if security gates pass."""
    reports_dir = Path()
    security_issues = []

    # Evaluate Bandit report
    bandit_report = reports_dir / "bandit-report.json"
    if bandit_report.exists():
        with open(bandit_report) as f:
            bandit_data = json.load(f)
            high_severity = [
                issue
                for issue in bandit_data.get("results", [])
                if issue.get("issue_severity") == "HIGH"
            ]
            if high_severity:
                security_issues.extend(high_severity)

    # Evaluate Safety report
    safety_report = reports_dir / "safety-report.json"
    if safety_report.exists():
        with open(safety_report) as f:
            safety_data = json.load(f)
            vulnerabilities = safety_data.get("vulnerabilities", [])
            if vulnerabilities:
                security_issues.extend(vulnerabilities)

    # Evaluate Semgrep report
    semgrep_report = reports_dir / "semgrep-report.json"
    if semgrep_report.exists():
        with open(semgrep_report) as f:
            semgrep_data = json.load(f)
            results = semgrep_data.get("results", [])
            critical_issues = [
                r for r in results if r.get("extra", {}).get("severity") == "ERROR"
            ]
            if critical_issues:
                security_issues.extend(critical_issues)

    # Security gate decision
    if security_issues:
        print(f"❌ Security gate FAILED: {len(security_issues)} critical issues found")
        for issue in security_issues[:5]:  # Show first 5 issues
            print(f"  - {issue}")
        sys.exit(1)
    else:
        print("✅ Security gate PASSED: No critical security issues found")
        sys.exit(0)


if __name__ == "__main__":
    evaluate_security_reports()
