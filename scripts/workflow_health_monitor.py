#!/usr/bin/env python3
"""
GitHub Actions Workflow Health Monitor
Comprehensive inspection of all workflow statuses and issues
"""

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

import yaml


def check_workflow_runs():
    """Check recent workflow runs using git log and file analysis."""
    try:
        # Get recent commits that might have triggered workflows
        result = subprocess.run(
            ["git", "log", "--oneline", "-10"],
            check=False,
            capture_output=True,
            text=True,
            cwd="/home/ubuntu/ACGS",
        )

        recent_commits = result.stdout.strip().split("\n") if result.stdout else []

        return {
            "recent_commits": recent_commits,
            "latest_commit": (
                recent_commits[0] if recent_commits else "No commits found"
            ),
        }
    except Exception as e:
        return {"error": f"Failed to check workflow runs: {e}"}


def analyze_workflow_files():
    """Analyze all workflow files for potential issues."""
    workflow_dir = Path("/home/ubuntu/ACGS/.github/workflows")
    analysis = {
        "total_workflows": 0,
        "valid_syntax": 0,
        "syntax_errors": 0,
        "potential_issues": [],
        "workflow_details": [],
    }

    for workflow_file in workflow_dir.glob("*.yml"):
        analysis["total_workflows"] += 1
        workflow_name = workflow_file.name

        try:
            with open(workflow_file) as f:
                content = f.read()
                workflow_data = yaml.safe_load(content)

            analysis["valid_syntax"] += 1

            # Analyze workflow for common issues
            issues = []
            workflow_info = {
                "file": workflow_name,
                "name": workflow_data.get("name", "No name"),
                "has_on_trigger": bool(workflow_data.get("on")),
                "has_jobs": bool(workflow_data.get("jobs")),
                "job_count": len(workflow_data.get("jobs", {})),
                "issues": [],
                "complexity": "simple",
            }

            # Check for common problematic patterns
            content_lower = content.lower()

            # Check for timeout-prone operations
            if "cargo install" in content and "timeout" not in content:
                issues.append("cargo install without timeout protection")

            if "curl" in content and (
                "timeout" not in content and "--max-time" not in content
            ):
                issues.append("curl operations without timeout")

            if "npm install" in content and (
                "timeout" not in content and "--timeout" not in content
            ):
                issues.append("npm install without timeout protection")

            # Check for Solana CLI issues
            if "solana" in content_lower and "release.solana.com" in content:
                if "fallback" not in content_lower and "||" not in content:
                    issues.append("Solana CLI installation without fallback")

            # Check for complex builds
            if "anchor build" in content or "cargo build" in content:
                if workflow_info["job_count"] > 3:
                    workflow_info["complexity"] = "complex"
                    if "continue-on-error" not in content:
                        issues.append("Complex build without continue-on-error")

            # Check for missing error handling
            if "pip install" in content and "||" not in content:
                issues.append("pip install without error handling")

            # Check for resource-intensive operations
            if any(
                term in content for term in ["sphinx", "mkdocs", "trivy", "semgrep"]
            ):
                if "timeout" not in content:
                    issues.append("Resource-intensive tools without timeout")

            workflow_info["issues"] = issues
            if issues:
                analysis["potential_issues"].extend(
                    [f"{workflow_name}: {issue}" for issue in issues]
                )

            analysis["workflow_details"].append(workflow_info)

        except yaml.YAMLError as e:
            analysis["syntax_errors"] += 1
            analysis["workflow_details"].append(
                {
                    "file": workflow_name,
                    "name": "YAML Error",
                    "error": str(e),
                    "issues": ["YAML syntax error"],
                }
            )
        except Exception as e:
            analysis["workflow_details"].append(
                {
                    "file": workflow_name,
                    "name": "Analysis Error",
                    "error": str(e),
                    "issues": ["Analysis failed"],
                }
            )

    return analysis


def check_dependencies():
    """Check for dependency-related issues."""
    issues = []

    # Check if critical files exist
    critical_files = [
        "/home/ubuntu/ACGS/requirements.txt",
        "/home/ubuntu/ACGS/pyproject.toml",
        "/home/ubuntu/ACGS/package.json",
    ]

    for file_path in critical_files:
        if not os.path.exists(file_path):
            issues.append(f"Missing critical file: {file_path}")

    # Check for common dependency conflicts
    if os.path.exists("/home/ubuntu/ACGS/pyproject.toml"):
        try:
            with open("/home/ubuntu/ACGS/pyproject.toml") as f:
                content = f.read()
                if (
                    "nemo-skills" in content
                    and "#" not in content.split("nemo-skills")[0].split("\n")[-1]
                ):
                    issues.append("NeMo-Skills dependency conflict may cause issues")
        except:
            pass

    return issues


def identify_high_risk_workflows():
    """Identify workflows most likely to fail based on patterns."""
    high_risk = []
    workflow_dir = Path("/home/ubuntu/ACGS/.github/workflows")

    risk_patterns = {
        "solana_cli": ["solana-cli", "release.solana.com"],
        "cargo_heavy": ["cargo install", "cargo build"],
        "network_intensive": ["curl", "wget", "git clone"],
        "complex_builds": ["anchor", "rust", "blockchain"],
        "security_tools": ["trivy", "semgrep", "bandit"],
        "documentation": ["sphinx", "mkdocs", "mermaid"],
    }

    for workflow_file in workflow_dir.glob("*.yml"):
        try:
            with open(workflow_file) as f:
                content = f.read().lower()

            risk_score = 0
            risk_factors = []

            for risk_type, patterns in risk_patterns.items():
                if any(pattern in content for pattern in patterns):
                    risk_score += 1
                    risk_factors.append(risk_type)

            if risk_score >= 2:  # High risk threshold
                high_risk.append(
                    {
                        "file": workflow_file.name,
                        "risk_score": risk_score,
                        "risk_factors": risk_factors,
                    }
                )
        except:
            continue

    return sorted(high_risk, key=lambda x: x["risk_score"], reverse=True)


def create_health_report():
    """Create comprehensive health report."""
    print("🔍 Inspecting GitHub Actions workflows...")

    # Run all checks
    workflow_runs = check_workflow_runs()
    workflow_analysis = analyze_workflow_files()
    dependency_issues = check_dependencies()
    high_risk_workflows = identify_high_risk_workflows()

    # Create comprehensive report
    report = {
        "inspection_timestamp": datetime.utcnow().isoformat(),
        "summary": {
            "total_workflows": workflow_analysis["total_workflows"],
            "valid_syntax": workflow_analysis["valid_syntax"],
            "syntax_errors": workflow_analysis["syntax_errors"],
            "potential_issues_count": len(workflow_analysis["potential_issues"]),
            "high_risk_workflows": len(high_risk_workflows),
            "dependency_issues": len(dependency_issues),
        },
        "workflow_runs": workflow_runs,
        "workflow_analysis": workflow_analysis,
        "dependency_issues": dependency_issues,
        "high_risk_workflows": high_risk_workflows,
        "recommendations": [],
    }

    # Generate recommendations
    if workflow_analysis["syntax_errors"] > 0:
        report["recommendations"].append("Fix YAML syntax errors in workflow files")

    if len(workflow_analysis["potential_issues"]) > 5:
        report["recommendations"].append("Address timeout and error handling issues")

    if len(high_risk_workflows) > 3:
        report["recommendations"].append(
            "Implement fallback strategies for high-risk workflows"
        )

    if dependency_issues:
        report["recommendations"].append("Resolve dependency configuration issues")

    return report


if __name__ == "__main__":
    health_report = create_health_report()

    # Save detailed report
    with open("/home/ubuntu/ACGS/workflow_health_report_detailed.json", "w") as f:
        json.dump(health_report, f, indent=2)

    # Print summary
    summary = health_report["summary"]
    print("\n📊 GitHub Actions Health Summary:")
    print(f"  Total Workflows: {summary['total_workflows']}")
    print(f"  Valid Syntax: {summary['valid_syntax']}")
    print(f"  Syntax Errors: {summary['syntax_errors']}")
    print(f"  Potential Issues: {summary['potential_issues_count']}")
    print(f"  High Risk Workflows: {summary['high_risk_workflows']}")
    print(f"  Dependency Issues: {summary['dependency_issues']}")

    if health_report["high_risk_workflows"]:
        print("\n⚠️ High Risk Workflows:")
        for workflow in health_report["high_risk_workflows"][:5]:
            print(
                f"  - {workflow['file']} (risk: {workflow['risk_score']}, factors: {', '.join(workflow['risk_factors'])})"
            )

    if health_report["workflow_analysis"]["potential_issues"]:
        print("\n🔧 Issues Found:")
        for issue in health_report["workflow_analysis"]["potential_issues"][:10]:
            print(f"  - {issue}")

    if health_report["recommendations"]:
        print("\n💡 Recommendations:")
        for rec in health_report["recommendations"]:
            print(f"  - {rec}")

    print("\n📋 Detailed report saved to: workflow_health_report_detailed.json")
