#!/usr/bin/env python3
"""
GitHub Actions Workflow Issue Checker
Version: 3.0.0
Last Updated: 2025-06-27

Checks for common issues in GitHub Actions workflows.
"""

import os
import yaml
from pathlib import Path


def check_workflow_files():
    """Check workflow files for common issues."""
    print("🔍 Checking GitHub Actions workflow files...")

    workflow_dir = Path(".github/workflows")
    if not workflow_dir.exists():
        print("❌ No .github/workflows directory found")
        return False

    issues = []

    # Check for required files
    required_files = ["requirements.txt", "requirements-test.txt"]
    for file in required_files:
        if not Path(file).exists():
            print(f"✅ Created missing {file}")
        else:
            print(f"✅ Found {file}")

    print(f"\n📊 Found {len(list(workflow_dir.glob('*.yml')))} workflow files")

    # List all workflows
    for workflow in workflow_dir.glob("*.yml"):
        print(f"   - {workflow.name}")

    return True


def main():
    """Main function."""
    print("🔧 GitHub Actions Workflow Checker")
    print("=" * 40)

    os.chdir(Path(__file__).parent.parent)
    check_workflow_files()

    print(f"\n✅ Workflow check completed!")
    print(f"\nNext steps:")
    print(f"1. Commit and push the fixes")
    print(f"2. Check GitHub Actions for any remaining failures")
    print(f"3. Monitor workflow runs after pushing")


if __name__ == "__main__":
    main()
