#!/usr/bin/env python3
"""
Fix common GitHub Actions workflow issues
Version: 3.0.0
Last Updated: 2025-06-27
"""

import os
from pathlib import Path

import yaml


def fix_python_version_issues():
    """Fix Python version issues in workflows."""
    workflow_dir = Path(".github/workflows")
    fixed_files = []

    for workflow_file in workflow_dir.glob("*.yml"):
        try:
            with open(workflow_file) as f:
                content = f.read()

            # Fix Python 3.13 to 3.11 (3.13 may not be available)
            if "PYTHON_VERSION: '3.13'" in content:
                content = content.replace(
                    "PYTHON_VERSION: '3.13'", "PYTHON_VERSION: '3.11'"
                )
                with open(workflow_file, "w") as f:
                    f.write(content)
                fixed_files.append(f"{workflow_file.name}: Fixed Python version")

            # Fix invalid Python versions
            if "python-version: '3.13'" in content:
                content = content.replace(
                    "python-version: '3.13'", "python-version: '3.11'"
                )
                with open(workflow_file, "w") as f:
                    f.write(content)
                fixed_files.append(f"{workflow_file.name}: Fixed setup-python version")

        except Exception as e:
            print(f"Error processing {workflow_file}: {e}")

    return fixed_files


def check_yaml_syntax():
    """Check YAML syntax in all workflow files."""
    workflow_dir = Path(".github/workflows")
    issues = []

    for workflow_file in workflow_dir.glob("*.yml"):
        try:
            with open(workflow_file) as f:
                yaml.safe_load(f)
        except yaml.YAMLError as e:
            issues.append(f"{workflow_file.name}: YAML syntax error - {e}")
        except Exception as e:
            issues.append(f"{workflow_file.name}: General error - {e}")

    return issues


def main():
    """Main function to fix workflow issues."""
    print("🔧 Fixing GitHub Actions workflow issues...")
    print("=" * 50)

    os.chdir(Path(__file__).parent.parent)

    # Fix Python version issues
    print("🐍 Fixing Python version issues...")
    python_fixes = fix_python_version_issues()

    if python_fixes:
        print("Fixed Python version issues:")
        for fix in python_fixes:
            print(f"  ✅ {fix}")
    else:
        print("  ✅ No Python version issues found")

    # Check YAML syntax
    print("\n📝 Checking YAML syntax...")
    yaml_issues = check_yaml_syntax()

    if yaml_issues:
        print("YAML syntax issues found:")
        for issue in yaml_issues:
            print(f"  ❌ {issue}")
        return 1
    print("  ✅ All YAML files have valid syntax")

    print("\n🎉 Workflow fixes completed!")
    return 0


if __name__ == "__main__":
    exit(main())
