#!/usr/bin/env python3
"""
ACGS-1 Workflow Monitoring Script

This script monitors the status of GitHub Actions workflows and provides
actionable insights for maintaining CI/CD pipeline health.
"""

import json
import subprocess
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class WorkflowMonitor:
    """Monitor GitHub Actions workflows for the ACGS-1 project."""

    def __init__(self):
        self.primary_workflows = [
            "unified-ci-modern.yml",
            "deployment-modern.yml",
            "security-focused.yml",
            "solana-anchor.yml",
        ]

        self.deprecated_workflows = [
            "ci-legacy.yml",
            "security-comprehensive.yml",
            "enhanced-parallel-ci.yml",
            "cost-optimized-ci.yml",
            "optimized-ci.yml",
            "ci-uv.yml",
            "enterprise-ci.yml",
        ]

    def check_gh_cli_available(self) -> bool:
        """Check if GitHub CLI is available."""
        try:
            result = subprocess.run(["gh", "--version"], capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def get_recent_runs(self, limit: int = 10) -> List[Dict]:
        """Get recent workflow runs."""
        if not self.check_gh_cli_available():
            print(
                "❌ GitHub CLI not available. Install with: curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg"
            )
            return []

        try:
            result = subprocess.run(
                [
                    "gh",
                    "run",
                    "list",
                    "--limit",
                    str(limit),
                    "--json",
                    "databaseId,status,conclusion,workflowName,headBranch,event,createdAt",
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                print(f"❌ Failed to fetch workflow runs: {result.stderr}")
                return []
        except Exception as e:
            print(f"❌ Error fetching workflow runs: {e}")
            return []

    def analyze_workflow_health(self, runs: List[Dict]) -> Dict:
        """Analyze workflow health metrics."""
        if not runs:
            return {"status": "no_data", "message": "No workflow data available"}

        total_runs = len(runs)
        successful_runs = sum(1 for run in runs if run.get("conclusion") == "success")
        failed_runs = sum(1 for run in runs if run.get("conclusion") == "failure")

        # Categorize by workflow type
        primary_runs = [
            run
            for run in runs
            if any(
                workflow in run.get("workflowName", "")
                for workflow in [
                    "unified-ci-modern",
                    "deployment-modern",
                    "security-focused",
                ]
            )
        ]
        deprecated_runs = [
            run
            for run in runs
            if any(
                workflow in run.get("workflowName", "")
                for workflow in self.deprecated_workflows
            )
        ]

        success_rate = (successful_runs / total_runs) * 100 if total_runs > 0 else 0

        # Determine health status
        if success_rate >= 90:
            health_status = "excellent"
        elif success_rate >= 75:
            health_status = "good"
        elif success_rate >= 50:
            health_status = "fair"
        else:
            health_status = "poor"

        return {
            "status": health_status,
            "success_rate": success_rate,
            "total_runs": total_runs,
            "successful_runs": successful_runs,
            "failed_runs": failed_runs,
            "primary_workflow_runs": len(primary_runs),
            "deprecated_workflow_runs": len(deprecated_runs),
            "recent_failures": [
                run for run in runs[:5] if run.get("conclusion") == "failure"
            ],
        }

    def get_workflow_recommendations(self, health_data: Dict) -> List[str]:
        """Generate actionable recommendations based on workflow health."""
        recommendations = []

        if health_data["status"] == "no_data":
            recommendations.extend(
                [
                    "🔧 Install GitHub CLI to enable workflow monitoring",
                    "📊 Set up workflow monitoring dashboard",
                    "🔍 Check GitHub Actions billing and limits",
                ]
            )
            return recommendations

        success_rate = health_data["success_rate"]

        if success_rate < 50:
            recommendations.extend(
                [
                    "🚨 CRITICAL: Workflow success rate below 50%",
                    "🔍 Investigate billing/quota issues with GitHub Actions",
                    "🛠️ Review recent failures and fix critical issues immediately",
                    "💰 Check GitHub Actions spending limits and billing status",
                ]
            )
        elif success_rate < 75:
            recommendations.extend(
                [
                    "⚠️ Workflow reliability needs improvement",
                    "🔧 Review and fix recent workflow failures",
                    "📈 Implement additional error handling and retries",
                ]
            )
        elif success_rate < 90:
            recommendations.extend(
                [
                    "✅ Workflows are mostly healthy",
                    "🔍 Monitor occasional failures for patterns",
                    "🔧 Fine-tune timeout and retry configurations",
                ]
            )
        else:
            recommendations.extend(
                [
                    "🎉 Excellent workflow health!",
                    "📊 Continue monitoring for sustained performance",
                    "🔄 Consider optimizing workflows for even better performance",
                ]
            )

        # Specific recommendations based on run data
        if health_data["deprecated_workflow_runs"] > 0:
            recommendations.append(
                "🗑️ Disable deprecated workflows to reduce noise and costs"
            )

        if health_data["failed_runs"] > 0:
            recommendations.append("🔍 Review recent failures for actionable insights")

        # Add billing-specific recommendations if patterns suggest billing issues
        recent_failures = health_data.get("recent_failures", [])
        if len(recent_failures) >= 3:  # Multiple recent failures suggest systemic issue
            recommendations.extend(
                [
                    "💳 Check GitHub Actions billing status and spending limits",
                    "📋 Review account permissions and payment methods",
                    "🔄 Consider workflow optimization to reduce compute usage",
                ]
            )

        return recommendations

    def generate_monitoring_report(self) -> str:
        """Generate a comprehensive monitoring report."""
        print("🔍 ACGS-1 Workflow Monitoring Report")
        print("=" * 50)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print()

        # Get recent workflow runs
        print("📊 Fetching recent workflow runs...")
        runs = self.get_recent_runs(20)

        if not runs:
            print("❌ Unable to fetch workflow data")
            print("\n🔧 Setup Instructions:")
            print("1. Install GitHub CLI: https://cli.github.com/")
            print("2. Authenticate: gh auth login")
            print("3. Re-run this monitoring script")
            return ""

        # Analyze workflow health
        health_data = self.analyze_workflow_health(runs)

        print(f"📈 Workflow Health Status: {health_data['status'].upper()}")
        print(f"✅ Success Rate: {health_data['success_rate']:.1f}%")
        print(f"📊 Total Runs Analyzed: {health_data['total_runs']}")
        print(f"✅ Successful: {health_data['successful_runs']}")
        print(f"❌ Failed: {health_data['failed_runs']}")
        print()

        # Show recent workflow activity
        print("🕒 Recent Workflow Activity:")
        for i, run in enumerate(runs[:5], 1):
            status_emoji = "✅" if run.get("conclusion") == "success" else "❌"
            workflow_name = run.get("workflowName", "Unknown")
            created_at = run.get("createdAt", "")
            print(f"  {i}. {status_emoji} {workflow_name} ({created_at})")
        print()

        # Generate recommendations
        recommendations = self.get_workflow_recommendations(health_data)
        print("💡 Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
        print()

        # Primary vs deprecated workflow usage
        print("🔧 Workflow Usage Analysis:")
        print(f"  📊 Primary workflows: {health_data['primary_workflow_runs']} runs")
        print(
            f"  🗑️ Deprecated workflows: {health_data['deprecated_workflow_runs']} runs"
        )

        if health_data["deprecated_workflow_runs"] > 0:
            print("  ⚠️ Deprecated workflows still active - consider disabling")
        print()

        # Billing and cost insights
        print("💰 Cost & Billing Insights:")

        # Check for patterns that suggest billing issues
        recent_failures = health_data.get("recent_failures", [])
        billing_related_failures = 0

        if len(recent_failures) >= 3:
            print("  🚨 Multiple recent failures detected")
            print("  💳 Possible billing/quota issues with GitHub Actions")
            print("  📋 Action Required: Check billing and spending limits")
        else:
            print("  ✅ No obvious billing-related issues detected")

        print("  📈 Optimization opportunities:")
        print("    - Use conditional job execution for better cost efficiency")
        print("    - Implement smart caching to reduce build times")
        print("    - Consider workflow consolidation to reduce redundancy")
        print()

        return f"Workflow health: {health_data['status']} ({health_data['success_rate']:.1f}% success)"


def main():
    """Main monitoring function."""
    monitor = WorkflowMonitor()

    try:
        result = monitor.generate_monitoring_report()

        # Exit with appropriate code based on workflow health
        runs = monitor.get_recent_runs(10)
        if runs:
            health_data = monitor.analyze_workflow_health(runs)
            if health_data["success_rate"] < 50:
                sys.exit(1)  # Critical failure
            elif health_data["success_rate"] < 75:
                sys.exit(2)  # Warning
            else:
                sys.exit(0)  # Success
        else:
            sys.exit(3)  # No data available

    except Exception as e:
        print(f"❌ Error running workflow monitor: {e}")
        sys.exit(4)


if __name__ == "__main__":
    main()
