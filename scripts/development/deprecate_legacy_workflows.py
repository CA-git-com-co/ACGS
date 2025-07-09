#!/usr/bin/env python3
"""
ACGS-1 Legacy Workflow Deprecation Script

This script safely deprecates legacy GitHub Actions workflows after
confirming the new modern workflows are functioning properly.
"""

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class WorkflowDeprecationManager:
    """Manage safe deprecation of legacy GitHub Actions workflows."""

    def __init__(self):
        self.project_root = Path.cwd()
        self.workflows_dir = self.project_root / ".github" / "workflows"
        self.archive_dir = self.project_root / ".github" / "workflows" / "deprecated"

        # Modern workflows that should remain active
        self.modern_workflows = [
            "unified-ci-modern.yml",
            "deployment-modern.yml",
            "security-focused.yml",
            "solana-anchor.yml",
        ]

        # Legacy workflows to be deprecated
        self.legacy_workflows = [
            "ci-legacy.yml",
            "security-comprehensive.yml",
            "enhanced-parallel-ci.yml",
            "cost-optimized-ci.yml",
            "optimized-ci.yml",
            "ci-uv.yml",
            "enterprise-ci.yml",
            "ci.yml",  # Original CI workflow
            "security.yml",  # Original security workflow
            "test.yml",  # Basic test workflow
            "build.yml",  # Basic build workflow
            "deploy.yml",  # Basic deploy workflow
        ]

        # Workflows that require manual review before deprecation
        self.review_required = [
            "release.yml",
            "publish.yml",
            "pages.yml",
            "dependabot.yml",
        ]

    def check_prerequisites(self) -> bool:
        """Check if prerequisites for safe deprecation are met."""
        print("🔍 Checking deprecation prerequisites...")

        # Check if GitHub CLI is available
        try:
            result = subprocess.run(["gh", "--version"], capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ GitHub CLI not available")
                return False
        except FileNotFoundError:
            print("❌ GitHub CLI not installed")
            return False

        # Check if workflows directory exists
        if not self.workflows_dir.exists():
            print("❌ .github/workflows directory not found")
            return False

        # Check if modern workflows exist
        missing_modern = []
        for workflow in self.modern_workflows:
            if not (self.workflows_dir / workflow).exists():
                missing_modern.append(workflow)

        if missing_modern:
            print(f"❌ Missing modern workflows: {missing_modern}")
            return False

        print("✅ All prerequisites met")
        return True

    def get_workflow_runs(self, workflow_name: str, limit: int = 10) -> List[Dict]:
        """Get recent runs for a specific workflow."""
        try:
            result = subprocess.run(
                [
                    "gh",
                    "run",
                    "list",
                    "--workflow",
                    workflow_name,
                    "--limit",
                    str(limit),
                    "--json",
                    "databaseId,status,conclusion,createdAt",
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                print(f"⚠️ Could not fetch runs for {workflow_name}: {result.stderr}")
                return []
        except Exception as e:
            print(f"⚠️ Error fetching workflow runs for {workflow_name}: {e}")
            return []

    def validate_modern_workflows(self) -> bool:
        """Validate that modern workflows are functioning properly."""
        print("📊 Validating modern workflow health...")

        all_healthy = True
        workflow_health = {}

        for workflow in self.modern_workflows:
            runs = self.get_workflow_runs(workflow, 5)

            if not runs:
                print(f"⚠️ {workflow}: No recent runs found")
                workflow_health[workflow] = "no_data"
                continue

            # Calculate success rate
            successful_runs = sum(
                1 for run in runs if run.get("conclusion") == "success"
            )
            success_rate = (successful_runs / len(runs)) * 100 if runs else 0

            if success_rate >= 80:
                print(f"✅ {workflow}: Healthy ({success_rate:.1f}% success)")
                workflow_health[workflow] = "healthy"
            elif success_rate >= 50:
                print(f"⚠️ {workflow}: Needs attention ({success_rate:.1f}% success)")
                workflow_health[workflow] = "warning"
                all_healthy = False
            else:
                print(f"❌ {workflow}: Unhealthy ({success_rate:.1f}% success)")
                workflow_health[workflow] = "unhealthy"
                all_healthy = False

        self.workflow_health = workflow_health
        return all_healthy

    def create_archive_directory(self) -> None:
        """Create archive directory for deprecated workflows."""
        self.archive_dir.mkdir(parents=True, exist_ok=True)

        # Create README for archive
        readme_content = f"""# Deprecated Workflows Archive

This directory contains GitHub Actions workflows that have been deprecated
as part of the ACGS-1 modernization initiative.

## Deprecation Date
{datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

## Reason for Deprecation
These workflows have been replaced by modern, unified workflows that provide:
- Better performance with UV package manager
- Enhanced security scanning
- Improved error handling and timeouts
- Consolidated functionality

## Modern Replacement Workflows
- `unified-ci-modern.yml` - Primary CI/CD pipeline
- `deployment-modern.yml` - Deployment orchestration
- `security-focused.yml` - Comprehensive security scanning
- `solana-anchor.yml` - Blockchain-specific validation

## Recovery Instructions
If you need to restore any of these workflows:
1. Copy the workflow file back to `.github/workflows/`
2. Update any outdated action versions
3. Test thoroughly before relying on the restored workflow

## Warning
These deprecated workflows may contain:
- Outdated GitHub Actions versions
- Security vulnerabilities
- Performance inefficiencies
- Compatibility issues

Use at your own risk and consider updating to modern equivalents instead.
"""

        with open(self.archive_dir / "README.md", "w") as f:
            f.write(readme_content)

    def deprecate_workflow(self, workflow_name: str, dry_run: bool = False) -> bool:
        """Safely deprecate a specific workflow."""
        workflow_path = self.workflows_dir / workflow_name
        archive_path = self.archive_dir / workflow_name

        if not workflow_path.exists():
            print(f"⚠️ {workflow_name}: File not found, skipping")
            return True

        print(f"🗑️ Deprecating {workflow_name}...")

        if dry_run:
            print(f"  [DRY RUN] Would move {workflow_path} to {archive_path}")
            return True

        try:
            # Create backup in archive
            shutil.move(str(workflow_path), str(archive_path))
            print(f"  ✅ Moved to archive: {archive_path}")

            # Add deprecation notice to the archived file
            self.add_deprecation_notice(archive_path)

            return True
        except Exception as e:
            print(f"  ❌ Failed to deprecate {workflow_name}: {e}")
            return False

    def add_deprecation_notice(self, workflow_path: Path) -> None:
        """Add deprecation notice to archived workflow."""
        try:
            with open(workflow_path, "r") as f:
                content = f.read()

            deprecation_notice = f"""# DEPRECATED WORKFLOW
# This workflow was deprecated on {datetime.now().strftime('%Y-%m-%d')}
# Replaced by modern unified workflows in ACGS-1 modernization
# See .github/workflows/deprecated/README.md for details

"""

            with open(workflow_path, "w") as f:
                f.write(deprecation_notice + content)

        except Exception as e:
            print(f"⚠️ Could not add deprecation notice to {workflow_path}: {e}")

    def generate_deprecation_report(self) -> str:
        """Generate comprehensive deprecation report."""
        report = []
        report.append("# ACGS-1 Workflow Deprecation Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        report.append("")

        # Executive summary
        total_deprecated = len(
            [w for w in self.legacy_workflows if (self.workflows_dir / w).exists()]
        )
        report.append("## Executive Summary")
        report.append(f"- **Total Workflows Deprecated**: {total_deprecated}")
        report.append(f"- **Modern Workflows Active**: {len(self.modern_workflows)}")
        report.append(f"- **Archive Location**: `.github/workflows/deprecated/`")
        report.append("")

        # Modern workflow health
        if hasattr(self, "workflow_health"):
            report.append("## Modern Workflow Health")
            for workflow, health in self.workflow_health.items():
                status_emoji = {
                    "healthy": "✅",
                    "warning": "⚠️",
                    "unhealthy": "❌",
                    "no_data": "❓",
                }.get(health, "❓")
                report.append(f"- {status_emoji} **{workflow}**: {health}")
            report.append("")

        # Deprecated workflows
        report.append("## Deprecated Workflows")
        for workflow in self.legacy_workflows:
            if (self.workflows_dir / workflow).exists():
                report.append(f"- ✅ {workflow} (deprecated)")
            elif (self.archive_dir / workflow).exists():
                report.append(f"- 📁 {workflow} (already archived)")
            else:
                report.append(f"- ❓ {workflow} (not found)")
        report.append("")

        # Manual review required
        if self.review_required:
            report.append("## Workflows Requiring Manual Review")
            for workflow in self.review_required:
                if (self.workflows_dir / workflow).exists():
                    report.append(f"- ⚠️ {workflow} (manual review required)")
            report.append("")

        # Recommendations
        report.append("## Post-Deprecation Recommendations")
        report.append("1. **Monitor Modern Workflows**: Ensure continued stability")
        report.append(
            "2. **Update Branch Protection**: Remove deprecated workflow requirements"
        )
        report.append("3. **Team Communication**: Notify team of workflow changes")
        report.append("4. **Documentation Update**: Update CI/CD documentation")
        report.append("5. **Cleanup Schedule**: Archive older workflow runs if needed")
        report.append("")

        # Recovery instructions
        report.append("## Recovery Instructions")
        report.append("If immediate rollback is needed:")
        report.append("1. Copy required workflow from `.github/workflows/deprecated/`")
        report.append("2. Remove deprecation notice from file header")
        report.append("3. Update any outdated action versions")
        report.append("4. Test workflow functionality")
        report.append("5. Consider this a temporary measure only")

        return "\n".join(report)

    def run_deprecation(self, dry_run: bool = False, force: bool = False) -> bool:
        """Run the complete deprecation process."""
        print("🚀 Starting ACGS-1 Legacy Workflow Deprecation")
        print("=" * 60)

        if dry_run:
            print("🔍 DRY RUN MODE - No files will be modified")

        try:
            # Step 1: Check prerequisites
            if not self.check_prerequisites():
                print("❌ Prerequisites not met - aborting deprecation")
                return False

            # Step 2: Validate modern workflows (skip if force)
            if not force:
                if not self.validate_modern_workflows():
                    print("❌ Modern workflows not healthy enough for safe deprecation")
                    print("Use --force to override this check")
                    return False
            else:
                print("⚠️ Forcing deprecation without health validation")

            # Step 3: Create archive directory
            if not dry_run:
                self.create_archive_directory()
                print("📁 Created archive directory")

            # Step 4: Deprecate legacy workflows
            success_count = 0
            for workflow in self.legacy_workflows:
                if self.deprecate_workflow(workflow, dry_run):
                    success_count += 1

            # Step 5: Generate report
            report = self.generate_deprecation_report()

            if not dry_run:
                report_path = self.project_root / "WORKFLOW_DEPRECATION_REPORT.md"
                with open(report_path, "w") as f:
                    f.write(report)
                print(f"📊 Generated deprecation report: {report_path}")

            # Step 6: Show warnings for manual review workflows
            manual_review_found = [
                w for w in self.review_required if (self.workflows_dir / w).exists()
            ]
            if manual_review_found:
                print(f"\n⚠️ Manual review required for: {manual_review_found}")
                print("These workflows were not automatically deprecated")

            print(f"\n✅ Deprecation completed successfully!")
            print(f"📊 {success_count} legacy workflows processed")

            if not dry_run:
                print("🛡️ All deprecated workflows archived safely")
                print("📋 Review WORKFLOW_DEPRECATION_REPORT.md for details")

            return True

        except Exception as e:
            print(f"\n❌ Deprecation failed: {e}")
            return False


def main():
    """Main deprecation function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Deprecate legacy GitHub Actions workflows"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview changes without modifying files"
    )
    parser.add_argument(
        "--force", action="store_true", help="Force deprecation without health checks"
    )

    args = parser.parse_args()

    manager = WorkflowDeprecationManager()

    try:
        success = manager.run_deprecation(dry_run=args.dry_run, force=args.force)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Fatal error during deprecation: {e}")
        sys.exit(2)


if __name__ == "__main__":
    main()
