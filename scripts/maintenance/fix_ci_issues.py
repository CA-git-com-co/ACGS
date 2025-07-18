#!/usr/bin/env python3
"""
Fix common CI/CD issues in ACGS workflows.
"""

import os
from pathlib import Path

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


def fix_python_dependencies():
    """Update Python dependencies to fix security vulnerabilities."""
    print("🔧 Fixing Python dependencies...")

    critical_updates = {
        "cryptography": "45.0.4",
        "pyjwt": "2.10.0",
        "fastapi": "0.115.6",
        "uvicorn": "0.34.0",
        "pydantic": "2.10.5",
        "httpx": "0.28.1",
        "python-multipart": "0.0.10",
    }

    # Update main config/environments/requirements.txt
    req_file = Path("config/environments/requirements.txt")
    if req_file.exists():
        lines = req_file.read_text().splitlines()
        updated_lines = []

        for line in lines:
            if line.strip() and not line.startswith("#"):
                for pkg, version in critical_updates.items():
                    if line.startswith(pkg):
                        line = f"{pkg}>={version}"
                        print(f"  ✅ Updated {pkg} to >={version}")
                        break
            updated_lines.append(line)

        req_file.write_text("\n".join(updated_lines) + "\n")
        print("  ✅ Updated config/environments/requirements.txt")


def fix_github_actions():
    """Update GitHub Actions to latest versions."""
    print("🔧 Fixing GitHub Actions versions...")

    workflows_dir = Path(".github/workflows")
    if not workflows_dir.exists():
        print("  ❌ No .github/workflows directory found")
        return

    action_updates = {
        "actions/checkout@v3": "actions/checkout@v4",
        "actions/setup-python@v4": "actions/setup-python@v5",
        "actions/setup-node@v3": "actions/setup-node@v4",
        "actions/upload-artifact@v3": "actions/upload-artifact@v4",
        "actions/download-artifact@v3": "actions/download-artifact@v4",
        "docker/setup-buildx-action@v2": "docker/setup-buildx-action@v3",
        "docker/login-action@v2": "docker/login-action@v3",
        "docker/build-push-action@v4": "docker/build-push-action@v5",
    }

    for workflow_file in workflows_dir.glob("*.yml"):
        content = workflow_file.read_text()
        updated = False

        for old_action, new_action in action_updates.items():
            if old_action in content:
                content = content.replace(old_action, new_action)
                updated = True
                print(
                    f"  ✅ Updated {old_action} to {new_action} in {workflow_file.name}"
                )

        if updated:
            workflow_file.write_text(content)


def add_pip_configuration():
    """Add pip configuration to prevent common issues."""
    print("🔧 Adding pip configuration...")

    pip_conf = """[global]
disable-pip-version-check = true
no-cache-dir = false
timeout = 60

[install]
user = false
"""

    pip_dir = Path.home() / ".pip"
    pip_dir.mkdir(exist_ok=True)

    pip_conf_file = pip_dir / "pip.conf"
    pip_conf_file.write_text(pip_conf)
    print("  ✅ Created pip configuration")


def check_workflow_syntax():
    """Check workflow syntax for common issues."""
    print("🔍 Checking workflow syntax...")

    workflows_dir = Path(".github/workflows")
    if not workflows_dir.exists():
        return

    for workflow_file in workflows_dir.glob("*.yml"):
        print(f"  📄 Checking {workflow_file.name}...")

        # Check for common syntax issues
        content = workflow_file.read_text()
        lines = content.splitlines()

        issues = []
        for i, line in enumerate(lines):
            # Check for tabs (should use spaces)
            if "\t" in line:
                issues.append(f"    Line {i + 1}: Contains tabs (use spaces instead)")

            # Check for trailing whitespace
            if line.rstrip() != line:
                issues.append(f"    Line {i + 1}: Has trailing whitespace")

        if issues:
            print(f"  ⚠️  Issues found in {workflow_file.name}:")
            for issue in issues:
                print(issue)
        else:
            print(f"  ✅ {workflow_file.name} syntax looks good")


def main():
    """Main function to fix CI/CD issues."""
    print("🚀 ACGS CI/CD Issue Fixer")
    print("=" * 50)

    # Change to repository root
    repo_root = Path(__file__).parent.parent
    os.chdir(repo_root)

    # Run fixes
    fix_python_dependencies()
    fix_github_actions()
    add_pip_configuration()
    check_workflow_syntax()

    print("\n✅ CI/CD fixes completed!")
    print("\nNext steps:")
    print("1. Review the changes")
    print("2. Run tests locally")
    print("3. Commit and push the fixes")


if __name__ == "__main__":
    main()
