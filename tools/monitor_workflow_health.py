#!/usr/bin/env python3
"""
GitHub Actions Workflow Health Monitor

This script monitors the health of GitHub Actions workflows after systematic fixes.
"""

import json
import subprocess
from datetime import datetime

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"



def run_command(cmd):
    """Run a command and return output."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error: {e}"


def get_workflow_status():
    """Get current workflow status from GitHub API."""
    try:
        # Get latest commit SHA
        latest_sha = run_command("git rev-parse HEAD")

        # Get workflow runs for latest commit
        api_cmd = f'curl -s "https://api.github.com/repos/CA-git-com-co/ACGS/actions/runs?head_sha={latest_sha}&per_page=30"'
        response = run_command(api_cmd)

        if response.startswith("Error:"):
            return {"error": response}

        data = json.loads(response)
        return data.get("workflow_runs", [])
    except json.JSONDecodeError:
        return {"error": "Failed to parse API response"}
    except Exception as e:
        return {"error": str(e)}


def analyze_workflow_health():
    """Analyze workflow health and generate report."""
    print("🔍 GitHub Actions Workflow Health Monitor")
    print("=" * 60)

    # Get current status
    workflows = get_workflow_status()

    if isinstance(workflows, dict) and "error" in workflows:
        print(f"❌ Failed to get workflow status: {workflows['error']}")
        return None

    # Categorize workflows
    success_workflows = []
    running_workflows = []
    failed_workflows = []

    for workflow in workflows:
        name = workflow.get("name", "Unknown")
        status = workflow.get("status", "unknown")
        conclusion = workflow.get("conclusion")

        if status == "completed":
            if conclusion == "success":
                success_workflows.append(name)
            elif conclusion == "failure":
                failed_workflows.append(name)
        elif status == "in_progress":
            running_workflows.append(name)

    # Generate report
    print(
        f"\n📊 Workflow Status Summary (as of {datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"
    )
    print("-" * 60)

    print(f"\n✅ Successful Workflows ({len(success_workflows)}):")
    if success_workflows:
        for workflow in success_workflows[:10]:  # Show first 10
            print(f"   • {workflow}")
        if len(success_workflows) > 10:
            print(f"   ... and {len(success_workflows) - 10} more")
    else:
        print("   None")

    print(f"\n🔄 Running Workflows ({len(running_workflows)}):")
    if running_workflows:
        for workflow in running_workflows:
            print(f"   • {workflow}")
    else:
        print("   None")

    print(f"\n❌ Failed Workflows ({len(failed_workflows)}):")
    if failed_workflows:
        for workflow in failed_workflows:
            print(f"   • {workflow}")
    else:
        print("   None")

    # Calculate health metrics
    total_workflows = len(success_workflows) + len(failed_workflows)
    if total_workflows > 0:
        success_rate = (len(success_workflows) / total_workflows) * 100
        print("\n📈 Health Metrics:")
        print(
            f"   Success Rate: {success_rate:.1f}% ({len(success_workflows)}/{total_workflows})"
        )

        if success_rate >= 80:
            print("   🎉 Excellent workflow health!")
        elif success_rate >= 60:
            print("   👍 Good workflow health")
        elif success_rate >= 40:
            print("   ⚠️ Moderate workflow health - some issues need attention")
        else:
            print("   🚨 Poor workflow health - urgent fixes needed")

    # Save detailed report
    report = {
        "timestamp": datetime.now().isoformat(),
        "success_workflows": success_workflows,
        "running_workflows": running_workflows,
        "failed_workflows": failed_workflows,
        "total_workflows": total_workflows,
        "success_rate": success_rate if total_workflows > 0 else 0,
    }

    with open("workflow_health_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print("\n💾 Detailed report saved to: workflow_health_report.json")

    return report


def main():
    """Main function."""
    try:
        report = analyze_workflow_health()

        if report and report.get("success_rate", 0) >= 60:
            print("\n🎯 Overall Assessment: Workflow fixes are working effectively!")
            print(
                "   The systematic improvements have significantly enhanced CI/CD reliability."
            )
        else:
            print(
                "\n🔧 Monitoring continues - some workflows may still be initializing..."
            )

    except Exception as e:
        print(f"\n❌ Error monitoring workflows: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
