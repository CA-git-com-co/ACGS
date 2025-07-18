#!/usr/bin/env python3
"""
ACGS-1 Workflow Modernization Validation Script

This script provides a comprehensive validation of the workflow modernization
process and generates a final status report.
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class WorkflowModernizationValidator:
    """Validate the complete workflow modernization process."""

    def __init__(self):
        self.project_root = Path.cwd()
        self.workflows_dir = self.project_root / ".github" / "workflows"

        # Expected modern workflows
        self.expected_modern = {
            "unified-ci-modern.yml": "Primary CI/CD pipeline with UV and smart detection",
            "deployment-modern.yml": "Environment-specific deployment orchestration",
            "security-focused.yml": "Comprehensive security scanning with zero-tolerance",
            "solana-anchor.yml": "Blockchain-specific Rust and Anchor validation",
        }

        # Files that should exist post-modernization
        self.expected_files = [
            ".github/workflows/README.md",
            "scripts/monitor_workflows.py",
            "scripts/fix_vulnerabilities.py",
            "scripts/setup_branch_protection.py",
            "scripts/deprecate_legacy_workflows.py",
            "BRANCH_PROTECTION_GUIDE.md",
            "WORKFLOW_TRANSITION_GUIDE.md",
        ]

        # Legacy workflows that should be deprecated
        self.legacy_workflows = [
            "ci-legacy.yml",
            "security-comprehensive.yml",
            "enhanced-parallel-ci.yml",
            "cost-optimized-ci.yml",
            "optimized-ci.yml",
            "ci-uv.yml",
            "enterprise-ci.yml",
        ]

    def check_modern_workflows(self) -> Dict[str, Dict]:
        """Check if all modern workflows exist and are properly configured."""
        print("🔍 Validating modern workflows...")

        results = {}

        for workflow, description in self.expected_modern.items():
            workflow_path = self.workflows_dir / workflow

            if not workflow_path.exists():
                results[workflow] = {
                    "exists": False,
                    "description": description,
                    "issues": ["File not found"],
                }
                continue

            # Check workflow content for key features
            with open(workflow_path, "r") as f:
                content = f.read()

            issues = []
            features = {
                "timeout configurations": "timeout-minutes:" in content,
                "UV package manager": "astral-sh/setup-uv" in content,
                "security scanning": any(
                    tool in content for tool in ["bandit", "safety", "semgrep"]
                ),
                "proper permissions": "permissions:" in content,
                "environment variables": "env:" in content,
            }

            for feature, present in features.items():
                if not present:
                    issues.append(f"Missing {feature}")

            results[workflow] = {
                "exists": True,
                "description": description,
                "features": features,
                "issues": issues,
                "size": len(content.splitlines()),
            }

        return results

    def check_supporting_files(self) -> Dict[str, bool]:
        """Check if all supporting files exist."""
        print("📋 Validating supporting files...")

        results = {}
        for file_path in self.expected_files:
            full_path = self.project_root / file_path
            results[file_path] = full_path.exists()

        return results

    def check_legacy_workflow_status(self) -> Dict[str, str]:
        """Check the status of legacy workflows."""
        print("🗑️ Checking legacy workflow status...")

        results = {}
        archive_dir = self.workflows_dir / "deprecated"

        for workflow in self.legacy_workflows:
            active_path = self.workflows_dir / workflow
            archived_path = archive_dir / workflow

            if active_path.exists():
                results[workflow] = "active"
            elif archived_path.exists():
                results[workflow] = "archived"
            else:
                results[workflow] = "not_found"

        return results

    def check_security_improvements(self) -> Dict[str, bool]:
        """Check if security improvements are in place."""
        print("🔒 Validating security improvements...")

        improvements = {
            "vulnerability_fixes": os.path.exists("SECURITY_REMEDIATION_REPORT.md"),
            "security_policy": os.path.exists("SECURITY_POLICY.yml"),
            "modern_security_workflow": (
                self.workflows_dir / "security-focused.yml"
            ).exists(),
            "branch_protection_guide": os.path.exists("BRANCH_PROTECTION_GUIDE.md"),
        }

        return improvements

    def get_github_actions_status(self) -> Dict:
        """Get GitHub Actions billing and run status."""
        print("💰 Checking GitHub Actions status...")

        status = {
            "billing_check": "unknown",
            "recent_runs": 0,
            "workflow_health": "unknown",
        }

        try:
            # Check if gh CLI is available
            result = subprocess.run(["gh", "--version"], capture_output=True, text=True)
            if result.returncode != 0:
                status["billing_check"] = "gh_cli_unavailable"
                return status

            # Try to get recent runs
            result = subprocess.run(
                ["gh", "run", "list", "--limit", "5", "--json", "status,conclusion"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                runs = json.loads(result.stdout)
                status["recent_runs"] = len(runs)

                if runs:
                    successful = sum(
                        1 for run in runs if run.get("conclusion") == "success"
                    )
                    success_rate = (successful / len(runs)) * 100

                    if success_rate >= 80:
                        status["workflow_health"] = "healthy"
                    elif success_rate >= 50:
                        status["workflow_health"] = "warning"
                    else:
                        status["workflow_health"] = "poor"
                else:
                    status["workflow_health"] = "no_data"

                status["billing_check"] = "accessible"
            else:
                # Check if it's a billing issue
                if (
                    "spending limit" in result.stderr.lower()
                    or "payment" in result.stderr.lower()
                ):
                    status["billing_check"] = "billing_issue"
                else:
                    status["billing_check"] = "other_issue"

        except Exception as e:
            status["billing_check"] = f"error: {str(e)}"

        return status

    def generate_modernization_report(self) -> str:
        """Generate comprehensive modernization validation report."""
        print("\n📊 Generating Modernization Validation Report")
        print("=" * 60)

        # Collect all validation data
        modern_workflows = self.check_modern_workflows()
        supporting_files = self.check_supporting_files()
        legacy_status = self.check_legacy_workflow_status()
        security_improvements = self.check_security_improvements()
        actions_status = self.get_github_actions_status()

        # Calculate completion scores
        modern_score = (
            sum(1 for w in modern_workflows.values() if w["exists"])
            / len(self.expected_modern)
            * 100
        )
        files_score = sum(supporting_files.values()) / len(self.expected_files) * 100
        security_score = (
            sum(security_improvements.values()) / len(security_improvements) * 100
        )

        # Generate report
        report = []
        report.append("# ACGS-1 Workflow Modernization Validation Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        report.append("")

        # Executive Summary
        overall_score = (modern_score + files_score + security_score) / 3
        report.append("## 🎯 Executive Summary")
        report.append(f"**Overall Modernization Score: {overall_score:.1f}%**")
        report.append("")
        report.append(
            f"- Modern Workflows: {modern_score:.1f}% ({sum(1 for w in modern_workflows.values() if w['exists'])}/{len(self.expected_modern)} complete)"
        )
        report.append(
            f"- Supporting Files: {files_score:.1f}% ({sum(supporting_files.values())}/{len(self.expected_files)} present)"
        )
        report.append(
            f"- Security Improvements: {security_score:.1f}% ({sum(security_improvements.values())}/{len(security_improvements)} implemented)"
        )
        report.append("")

        # Modern Workflows Status
        report.append("## 🚀 Modern Workflows")
        for workflow, data in modern_workflows.items():
            status = "✅" if data["exists"] else "❌"
            report.append(f"{status} **{workflow}**")
            report.append(f"   - {data['description']}")

            if data["exists"]:
                report.append(f"   - Size: {data['size']} lines")
                if data["issues"]:
                    for issue in data["issues"]:
                        report.append(f"   - ⚠️ {issue}")
                else:
                    report.append("   - ✅ All key features present")
            report.append("")

        # Supporting Files Status
        report.append("## 📋 Supporting Files")
        for file_path, exists in supporting_files.items():
            status = "✅" if exists else "❌"
            report.append(f"{status} {file_path}")
        report.append("")

        # Legacy Workflow Status
        report.append("## 🗑️ Legacy Workflows")
        legacy_counts = {"active": 0, "archived": 0, "not_found": 0}
        for workflow, status in legacy_status.items():
            legacy_counts[status] += 1
            status_emoji = {"active": "⚠️", "archived": "✅", "not_found": "❓"}
            report.append(f"{status_emoji[status]} {workflow}: {status}")

        report.append("")
        report.append(
            f"**Summary**: {legacy_counts['archived']} archived, {legacy_counts['active']} still active, {legacy_counts['not_found']} not found"
        )
        report.append("")

        # Security Improvements
        report.append("## 🔒 Security Improvements")
        for improvement, implemented in security_improvements.items():
            status = "✅" if implemented else "❌"
            formatted_name = improvement.replace("_", " ").title()
            report.append(f"{status} {formatted_name}")
        report.append("")

        # GitHub Actions Status
        report.append("## 💰 GitHub Actions Status")
        billing_status = actions_status["billing_check"]
        if billing_status == "billing_issue":
            report.append("❌ **Billing/Quota Issue Detected**")
            report.append("   - GitHub Actions spending limit reached or payment issue")
            report.append("   - Workflows cannot run until billing is resolved")
        elif billing_status == "accessible":
            report.append("✅ **GitHub Actions Accessible**")
            report.append(f"   - Recent runs: {actions_status['recent_runs']}")
            report.append(f"   - Workflow health: {actions_status['workflow_health']}")
        else:
            report.append(f"⚠️ **Status Unknown**: {billing_status}")
        report.append("")

        # Next Steps
        report.append("## 📋 Next Steps")

        if overall_score >= 90:
            report.append("🎉 **Modernization Complete!**")

            if legacy_counts["active"] > 0:
                report.append("1. **Deprecate remaining legacy workflows**")
                report.append("   ```bash")
                report.append(
                    "   python scripts/deprecate_legacy_workflows.py --dry-run"
                )
                report.append("   python scripts/deprecate_legacy_workflows.py")
                report.append("   ```")

            if billing_status == "billing_issue":
                report.append("2. **Resolve GitHub Actions billing issues**")
                report.append(
                    "   - Check spending limits in GitHub organization settings"
                )
                report.append("   - Verify payment methods are up to date")
                report.append("   - Contact GitHub support if needed")

            report.append("3. **Enable branch protection rules**")
            report.append("   ```bash")
            report.append("   python scripts/setup_branch_protection.py")
            report.append("   ```")

            report.append("4. **Monitor workflow performance**")
            report.append("   ```bash")
            report.append("   python scripts/monitor_workflows.py")
            report.append("   ```")

        else:
            report.append("⚠️ **Modernization Incomplete**")

            missing_workflows = [
                w for w, d in modern_workflows.items() if not d["exists"]
            ]
            if missing_workflows:
                report.append(
                    f"1. **Create missing workflows**: {', '.join(missing_workflows)}"
                )

            missing_files = [f for f, exists in supporting_files.items() if not exists]
            if missing_files:
                report.append(
                    f"2. **Create missing files**: {', '.join(missing_files)}"
                )

            if not all(security_improvements.values()):
                report.append("3. **Complete security improvements**")
                report.append("   ```bash")
                report.append("   python scripts/fix_vulnerabilities.py")
                report.append("   ```")

        # Rollback Plan
        report.append("## 🔄 Emergency Rollback Plan")
        report.append("If modern workflows fail and immediate rollback is needed:")
        report.append("")
        report.append("```bash")
        report.append("# Quick rollback to working state")
        report.append(
            "cp .github/workflows/deprecated/*.yml .github/workflows/ 2>/dev/null || true"
        )
        report.append("git add .github/workflows/")
        report.append("git commit -m 'Emergency rollback to legacy workflows'")
        report.append("git push")
        report.append("```")
        report.append("")

        # Success Criteria
        report.append("## ✅ Success Criteria")
        report.append("Modernization is considered complete when:")
        report.append("- [ ] All modern workflows created and functional")
        report.append("- [ ] Legacy workflows safely deprecated")
        report.append("- [ ] Security vulnerabilities addressed")
        report.append("- [ ] Branch protection rules updated")
        report.append("- [ ] Team trained on new workflows")
        report.append("- [ ] Documentation updated")
        report.append("- [ ] Performance improvements validated")

        return "\n".join(report)

    def run_validation(self) -> bool:
        """Run complete validation and generate report."""
        print("🔍 ACGS-1 Workflow Modernization Validation")
        print("=" * 50)

        try:
            # Generate comprehensive report
            report = self.generate_modernization_report()

            # Save report
            report_path = self.project_root / "WORKFLOW_MODERNIZATION_REPORT.md"
            with open(report_path, "w") as f:
                f.write(report)

            print(f"\n📊 Validation report generated: {report_path}")

            # Print summary to console
            modern_workflows = self.check_modern_workflows()
            supporting_files = self.check_supporting_files()

            modern_score = (
                sum(1 for w in modern_workflows.values() if w["exists"])
                / len(self.expected_modern)
                * 100
            )
            files_score = (
                sum(supporting_files.values()) / len(self.expected_files) * 100
            )
            overall_score = (modern_score + files_score) / 2

            print(f"\n🎯 Overall Score: {overall_score:.1f}%")

            if overall_score >= 90:
                print("🎉 Modernization is complete!")
                print("📋 Ready for legacy workflow deprecation")
                return True
            elif overall_score >= 70:
                print("⚠️ Modernization mostly complete with minor issues")
                return True
            else:
                print("❌ Modernization incomplete - review report for details")
                return False

        except Exception as e:
            print(f"❌ Validation failed: {e}")
            return False


def main():
    """Main validation function."""
    validator = WorkflowModernizationValidator()

    try:
        success = validator.run_validation()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Fatal error during validation: {e}")
        sys.exit(2)


if __name__ == "__main__":
    main()
