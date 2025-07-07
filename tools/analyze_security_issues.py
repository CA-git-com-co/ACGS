#!/usr/bin/env python3
"""
ACGS-1 Phase A2: Security Vulnerability Analysis and Remediation
Analyzes Bandit security report and creates remediation plan
"""

import json
import sys
from collections import Counter, defaultdict
from datetime import datetime

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


def analyze_bandit_report(report_file):
    """Analyze Bandit security report and categorize issues."""

    try:
        with open(report_file) as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: Report file {report_file} not found")
        return None
    except json.JSONDecodeError:
        print(f"❌ Error: Invalid JSON in {report_file}")
        return None

    results = data.get("results", [])

    # Categorize issues
    issues_by_severity = defaultdict(list)
    issues_by_type = defaultdict(list)
    issues_by_file = defaultdict(list)

    for issue in results:
        severity = issue.get("issue_severity", "UNKNOWN")
        test_name = issue.get("test_name", "unknown")
        filename = issue.get("filename", "unknown")

        issues_by_severity[severity].append(issue)
        issues_by_type[test_name].append(issue)
        issues_by_file[filename].append(issue)

    return {
        "total_issues": len(results),
        "by_severity": dict(issues_by_severity),
        "by_type": dict(issues_by_type),
        "by_file": dict(issues_by_file),
        "errors": data.get("errors", []),
    }


def generate_remediation_plan(analysis):
    """Generate specific remediation plan for security issues."""

    remediation_plan = {
        "critical_actions": [],
        "high_priority_fixes": [],
        "medium_priority_fixes": [],
        "low_priority_fixes": [],
        "summary": {},
    }

    high_issues = analysis["by_severity"].get("HIGH", [])
    medium_issues = analysis["by_severity"].get("MEDIUM", [])
    low_issues = analysis["by_severity"].get("LOW", [])

    # Analyze HIGH severity issues
    for issue in high_issues:
        test_name = issue.get("test_name", "")
        filename = issue.get("filename", "")
        line_number = issue.get("line_number", 0)
        issue_text = issue.get("issue_text", "")

        if "hashlib" in test_name and "MD5" in issue_text:
            remediation_plan["critical_actions"].append(
                {
                    "type": "Weak Cryptography",
                    "file": filename,
                    "line": line_number,
                    "issue": "MD5 hash usage detected",
                    "fix": "Replace MD5 with SHA-256 or stronger hash algorithm",
                    "code_change": "hashlib.md5() → hashlib.sha256()",
                    "priority": "CRITICAL",
                }
            )

        elif "hardcoded_password" in test_name:
            remediation_plan["critical_actions"].append(
                {
                    "type": "Hardcoded Secrets",
                    "file": filename,
                    "line": line_number,
                    "issue": "Hardcoded password/secret detected",
                    "fix": "Move secrets to environment variables or secure vault",
                    "code_change": "Use os.environ.get() or secure configuration",
                    "priority": "CRITICAL",
                }
            )

        elif "sql_injection" in test_name:
            remediation_plan["critical_actions"].append(
                {
                    "type": "SQL Injection",
                    "file": filename,
                    "line": line_number,
                    "issue": "Potential SQL injection vulnerability",
                    "fix": "Use parameterized queries or ORM",
                    "code_change": "Replace string formatting with parameterized queries",
                    "priority": "CRITICAL",
                }
            )

        else:
            remediation_plan["high_priority_fixes"].append(
                {
                    "type": test_name,
                    "file": filename,
                    "line": line_number,
                    "issue": issue_text,
                    "priority": "HIGH",
                }
            )

    # Count issues by type for summary
    type_counts = Counter()
    for test_name, issues in analysis["by_type"].items():
        type_counts[test_name] = len(issues)

    remediation_plan["summary"] = {
        "total_issues": analysis["total_issues"],
        "critical_count": len(remediation_plan["critical_actions"]),
        "high_count": len(high_issues),
        "medium_count": len(medium_issues),
        "low_count": len(low_issues),
        "most_common_issues": type_counts.most_common(5),
        "files_affected": len(analysis["by_file"]),
    }

    return remediation_plan


def print_security_report(analysis, remediation_plan):
    """Print comprehensive security analysis report."""

    print("🔒 ACGS-1 Phase A2: Security Vulnerability Assessment")
    print("=" * 60)
    print(f"📊 Analysis Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📋 Total Issues Found: {analysis['total_issues']}")
    print(f"📁 Files Affected: {len(analysis['by_file'])}")

    # Severity breakdown
    print("\n🎯 Severity Breakdown:")
    for severity in ["HIGH", "MEDIUM", "LOW"]:
        count = len(analysis["by_severity"].get(severity, []))
        if count > 0:
            print(f"  {severity}: {count} issues")

    # Critical actions needed
    critical_actions = remediation_plan["critical_actions"]
    if critical_actions:
        print(f"\n🚨 CRITICAL ACTIONS REQUIRED ({len(critical_actions)} issues):")
        for i, action in enumerate(critical_actions, 1):
            print(f"  {i}. {action['type']}: {action['file']}:{action['line']}")
            print(f"     Issue: {action['issue']}")
            print(f"     Fix: {action['fix']}")
            if "code_change" in action:
                print(f"     Code: {action['code_change']}")
            print()

    # Most common issue types
    print("\n📈 Most Common Issue Types:")
    for test_name, count in remediation_plan["summary"]["most_common_issues"]:
        print(f"  • {test_name}: {count} occurrences")

    # Files with most issues
    print("\n📁 Files with Most Issues:")
    file_counts = [
        (len(issues), filename) for filename, issues in analysis["by_file"].items()
    ]
    file_counts.sort(reverse=True)

    for count, filename in file_counts[:10]:  # Top 10 files
        if count > 0:
            print(f"  • {filename}: {count} issues")

    # Remediation priority
    print("\n🎯 Remediation Priority:")
    print(f"  1. CRITICAL: {len(critical_actions)} issues (immediate action required)")
    print(
        f"  2. HIGH: {len(analysis['by_severity'].get('HIGH', []))} issues (fix within 24 hours)"
    )
    print(
        f"  3. MEDIUM: {len(analysis['by_severity'].get('MEDIUM', []))} issues (fix within 1 week)"
    )
    print(
        f"  4. LOW: {len(analysis['by_severity'].get('LOW', []))} issues (fix within 1 month)"
    )

    # Security score calculation
    total_issues = analysis["total_issues"]
    critical_weight = len(critical_actions) * 10
    high_weight = len(analysis["by_severity"].get("HIGH", [])) * 5
    medium_weight = len(analysis["by_severity"].get("MEDIUM", [])) * 2
    low_weight = len(analysis["by_severity"].get("LOW", [])) * 1

    weighted_score = critical_weight + high_weight + medium_weight + low_weight
    max_possible_score = total_issues * 10  # If all were critical

    if max_possible_score > 0:
        security_score = max(0, 100 - (weighted_score / max_possible_score * 100))
    else:
        security_score = 100

    print(f"\n📊 Security Score: {security_score:.1f}/100")

    if security_score >= 90:
        print("✅ EXCELLENT: Minimal security issues")
    elif security_score >= 70:
        print("⚠️  GOOD: Some security improvements needed")
    elif security_score >= 50:
        print("🔶 FAIR: Significant security improvements required")
    else:
        print("🚨 POOR: Critical security remediation required")


def main():
    """Main execution function."""

    report_file = "bandit_security_report_after_fixes.json"

    print("🔍 Analyzing Bandit security report...")
    analysis = analyze_bandit_report(report_file)

    if not analysis:
        sys.exit(1)

    print("📋 Generating remediation plan...")
    remediation_plan = generate_remediation_plan(analysis)

    print_security_report(analysis, remediation_plan)

    # Save detailed remediation plan
    output_file = "security_remediation_plan.json"
    with open(output_file, "w") as f:
        json.dump(
            {
                "analysis": analysis,
                "remediation_plan": remediation_plan,
                "timestamp": datetime.now().isoformat(),
            },
            f,
            indent=2,
        )

    print(f"\n💾 Detailed remediation plan saved to: {output_file}")

    # Return exit code based on security score
    security_score = remediation_plan["summary"].get("security_score", 0)
    if len(remediation_plan["critical_actions"]) > 0:
        print(
            "\n🚨 BLOCKING: Critical security issues must be resolved before deployment"
        )
        sys.exit(1)
    elif security_score < 70:
        print("\n⚠️  WARNING: Security score below acceptable threshold")
        sys.exit(1)
    else:
        print("\n✅ Security assessment completed successfully")
        sys.exit(0)


if __name__ == "__main__":
    main()
