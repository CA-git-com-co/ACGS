#!/usr/bin/env python3
"""
ACGS Documentation Quality Alert Monitor
Constitutional Hash: cdd01ef066bc6cf2

This script monitors documentation quality metrics and sends alerts when
quality degrades below established thresholds.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Configuration
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
REPO_ROOT = Path(__file__).parent.parent.parent
METRICS_DIR = REPO_ROOT / "metrics"

# Quality thresholds
THRESHOLDS = {
    "constitutional_compliance": 100,  # Must be 100%
    "link_validity": 100,  # Must be 100%
    "documentation_freshness": 85,  # Target: 85%
    "documentation_coverage": 80,  # Target: 80%
    "overall_quality": 85,  # Target: 85%
}

# Alert severity levels
SEVERITY_CRITICAL = "CRITICAL"
SEVERITY_HIGH = "HIGH"
SEVERITY_MEDIUM = "MEDIUM"
SEVERITY_LOW = "LOW"


def load_latest_metrics() -> dict[str, Any]:
    """Load the latest metrics from the metrics directory."""
    latest_metrics_file = METRICS_DIR / "latest_metrics.json"

    if not latest_metrics_file.exists():
        print(f"❌ Latest metrics file not found: {latest_metrics_file}")
        return {}

    try:
        with open(latest_metrics_file) as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading metrics: {e}")
        return {}


def check_quality_issues(metrics: dict[str, Any]) -> list[dict[str, Any]]:
    """Check for quality issues based on thresholds."""
    issues = []

    if not metrics or "metrics" not in metrics:
        issues.append({
            "severity": SEVERITY_CRITICAL,
            "category": "system",
            "message": "No metrics data available",
            "details": "Metrics collection may have failed",
        })
        return issues

    metrics_data = metrics["metrics"]

    # Check constitutional compliance
    compliance = metrics_data.get("constitutional_compliance", {})
    compliance_rate = compliance.get("rate", 0)
    if compliance_rate < THRESHOLDS["constitutional_compliance"]:
        issues.append({
            "severity": SEVERITY_CRITICAL,
            "category": "constitutional_compliance",
            "message": f"Constitutional compliance below 100% ({compliance_rate}%)",
            "details": (
                "Missing constitutional hash in"
                f" {compliance.get('total_docs', 0) - compliance.get('compliant_docs', 0)} files"
            ),
            "action": (
                f"Add constitutional hash '{CONSTITUTIONAL_HASH}' to all documentation"
                " files"
            ),
        })

    # Check link validity
    link_validity = metrics_data.get("link_validity", {})
    link_rate = link_validity.get("rate", 0)
    if link_rate < THRESHOLDS["link_validity"]:
        broken_links = link_validity.get("broken_links", 0)
        issues.append({
            "severity": SEVERITY_HIGH,
            "category": "link_validity",
            "message": f"Link validity below 100% ({link_rate}%)",
            "details": f"{broken_links} broken internal links found",
            "action": "Fix broken documentation links to maintain navigation integrity",
        })

    # Check documentation freshness
    freshness = metrics_data.get("documentation_freshness", {})
    freshness_rate = freshness.get("rate", 0)
    if freshness_rate < THRESHOLDS["documentation_freshness"]:
        stale_docs = freshness.get("stale_docs", 0)
        severity = SEVERITY_HIGH if freshness_rate < 70 else SEVERITY_MEDIUM
        issues.append({
            "severity": severity,
            "category": "documentation_freshness",
            "message": f"Documentation freshness below 85% ({freshness_rate}%)",
            "details": f"{stale_docs} documents not updated in >90 days",
            "action": "Review and update stale documentation",
        })

    # Check documentation coverage
    coverage = metrics_data.get("documentation_coverage", {})
    coverage_rate = coverage.get("rate", 0)
    if coverage_rate < THRESHOLDS["documentation_coverage"]:
        missing_docs = coverage.get("total_expected", 0) - coverage.get(
            "documented_services", 0
        )
        severity = SEVERITY_HIGH if coverage_rate < 60 else SEVERITY_MEDIUM
        issues.append({
            "severity": severity,
            "category": "documentation_coverage",
            "message": f"Documentation coverage below 80% ({coverage_rate}%)",
            "details": f"{missing_docs} services missing API documentation",
            "action": "Create missing service API documentation",
        })

    # Check overall quality score
    overall = metrics_data.get("overall_quality", {})
    overall_score = overall.get("score", 0)
    if overall_score < THRESHOLDS["overall_quality"]:
        if overall_score < 70:
            severity = SEVERITY_CRITICAL
        elif overall_score < 80:
            severity = SEVERITY_HIGH
        else:
            severity = SEVERITY_MEDIUM

        issues.append({
            "severity": severity,
            "category": "overall_quality",
            "message": f"Overall quality score below 85% ({overall_score}%)",
            "details": f"Quality status: {overall.get('status', 'UNKNOWN')}",
            "action": "Address individual metric issues to improve overall quality",
        })

    return issues


def generate_alert_report(metrics: dict[str, Any], issues: list[dict[str, Any]]) -> str:
    """Generate a formatted alert report."""
    date = metrics.get("date", datetime.now().strftime("%Y-%m-%d"))
    constitutional_hash = metrics.get("constitutional_hash", CONSTITUTIONAL_HASH)

    report = f"""# ACGS Documentation Quality Alert Report

**Date**: {date}
**Constitutional Hash**: `{constitutional_hash}`
**Alert Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Alert Summary

"""

    if not issues:
        report += """✅ **ALL QUALITY METRICS WITHIN ACCEPTABLE RANGES**

No quality issues detected. All metrics are meeting or exceeding targets.

"""
    else:
        # Group issues by severity
        critical_issues = [i for i in issues if i["severity"] == SEVERITY_CRITICAL]
        high_issues = [i for i in issues if i["severity"] == SEVERITY_HIGH]
        medium_issues = [i for i in issues if i["severity"] == SEVERITY_MEDIUM]
        low_issues = [i for i in issues if i["severity"] == SEVERITY_LOW]

        report += f"""⚠️ **{len(issues)} QUALITY ISSUES DETECTED**

- 🚨 Critical: {len(critical_issues)}
- ⚠️ High: {len(high_issues)}
- 📋 Medium: {len(medium_issues)}
- ℹ️ Low: {len(low_issues)}

## Issues by Severity

"""

        for severity, emoji in [
            (SEVERITY_CRITICAL, "🚨"),
            (SEVERITY_HIGH, "⚠️"),
            (SEVERITY_MEDIUM, "📋"),
            (SEVERITY_LOW, "ℹ️"),
        ]:
            severity_issues = [i for i in issues if i["severity"] == severity]
            if severity_issues:
                report += f"### {emoji} {severity} Issues\n\n"
                for issue in severity_issues:
                    report += (
                        f"**{issue['category'].replace('_', ' ').title()}**:"
                        f" {issue['message']}\n"
                    )
                    report += f"- Details: {issue['details']}\n"
                    if "action" in issue:
                        report += f"- Action: {issue['action']}\n"
                    report += "\n"

    # Add current metrics summary
    if "metrics" in metrics:
        metrics_data = metrics["metrics"]
        report += """## Current Metrics Summary

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
"""

        for metric_name, threshold in THRESHOLDS.items():
            if metric_name == "overall_quality":
                current_value = metrics_data.get("overall_quality", {}).get("score", 0)
            else:
                current_value = metrics_data.get(metric_name, {}).get("rate", 0)

            status = "✅ PASS" if current_value >= threshold else "❌ FAIL"
            report += (
                f"| {metric_name.replace('_', ' ').title()} | {current_value}% |"
                f" {threshold}% | {status} |\n"
            )

    report += f"""

## Constitutional Compliance

All ACGS documentation must include constitutional hash `{constitutional_hash}` to maintain compliance and security standards.

---

**Automated Alert**: Generated by ACGS Documentation Quality Monitor
**Constitutional Hash**: `{constitutional_hash}` ✅
"""

    return report


def main():
    """Main execution function."""
    print("🔍 ACGS Documentation Quality Alert Monitor")
    print("=" * 50)
    print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print(f"Repository: {REPO_ROOT}")
    print()

    # Load latest metrics
    metrics = load_latest_metrics()
    if not metrics:
        print("❌ Failed to load metrics data")
        sys.exit(1)

    # Check for quality issues
    issues = check_quality_issues(metrics)

    # Generate alert report
    report = generate_alert_report(metrics, issues)

    # Save alert report
    alert_date = datetime.now().strftime("%Y-%m-%d")
    alert_file = METRICS_DIR / f"quality_alert_{alert_date}.md"

    with open(alert_file, "w") as f:
        f.write(report)

    print(f"📊 Alert report saved to: {alert_file}")

    # Print summary
    if not issues:
        print("✅ All quality metrics within acceptable ranges")
        print("🎯 Overall status: EXCELLENT")
        sys.exit(0)
    else:
        critical_count = len([i for i in issues if i["severity"] == SEVERITY_CRITICAL])
        high_count = len([i for i in issues if i["severity"] == SEVERITY_HIGH])

        print(f"⚠️ {len(issues)} quality issues detected:")
        print(f"  🚨 Critical: {critical_count}")
        print(f"  ⚠️ High: {high_count}")
        print(f"  📋 Medium/Low: {len(issues) - critical_count - high_count}")

        if critical_count > 0:
            print("🚨 CRITICAL ISSUES REQUIRE IMMEDIATE ATTENTION")
            sys.exit(2)
        elif high_count > 0:
            print("⚠️ High priority issues need attention")
            sys.exit(1)
        else:
            print("📋 Medium/low priority issues detected")
            sys.exit(0)


if __name__ == "__main__":
    main()
