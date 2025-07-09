#!/usr/bin/env python3
"""
ACGS-2 Code Quality and Linting Script

This script runs all code quality checks including:
- Ruff linting and formatting
- Black formatting
- MyPy type checking
- Bandit security analysis
- Import sorting

Usage:
    python scripts/lint.py [--fix] [--check-only]

Options:
    --fix        Apply automatic fixes where possible
    --check-only Only check, don't apply fixes (CI mode)
"""

import argparse
import subprocess
import sys
from pathlib import Path

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


def run_command(cmd: list[str], description: str, fix_mode: bool = False) -> bool:
    """Run a command and return success status."""
    print(f"\n🔍 {description}")
    print(f"Running: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        if result.returncode == 0:
            print(f"✅ {description} passed")
            if result.stdout.strip():
                print(result.stdout)
            return True
        print(f"❌ {description} failed")
        if result.stdout.strip():
            print("STDOUT:", result.stdout)
        if result.stderr.strip():
            print("STDERR:", result.stderr)
        return False

    except FileNotFoundError:
        print(f"❌ Command not found: {cmd[0]}")
        return False
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return False


def main():
    """Main function to run all linting and formatting checks."""
    parser = argparse.ArgumentParser(description="Run ACGS-2 code quality checks")
    parser.add_argument("--fix", action="store_true", help="Apply automatic fixes")
    parser.add_argument(
        "--check-only", action="store_true", help="Check only, no fixes"
    )
    args = parser.parse_args()

    # Change to project root
    project_root = Path(__file__).parent.parent
    print(f"🏠 Working directory: {project_root}")

    success_count = 0
    total_checks = 0

    # Define checks to run
    checks = [
        {
            "cmd": [
                "ruff",
                "check",
                ".",
                "--fix" if args.fix and not args.check_only else "",
            ],
            "description": "Ruff linting",
            "fix_mode": args.fix and not args.check_only,
        },
        {
            "cmd": [
                "ruff",
                "format",
                "." if args.fix and not args.check_only else "--check",
                ".",
            ],
            "description": "Ruff formatting",
            "fix_mode": args.fix and not args.check_only,
        },
        {
            "cmd": [
                "black",
                "." if args.fix and not args.check_only else "--check",
                ".",
            ],
            "description": "Black formatting",
            "fix_mode": args.fix and not args.check_only,
        },
        {
            "cmd": ["mypy", "services", "--ignore-missing-imports"],
            "description": "MyPy type checking",
            "fix_mode": False,
        },
        {
            "cmd": [
                "bandit",
                "-r",
                "services",
                "-f",
                "json",
                "-o",
                "bandit-report.json",
            ],
            "description": "Bandit security analysis",
            "fix_mode": False,
        },
    ]

    print("🚀 Starting ACGS-2 Code Quality Checks")
    print("=" * 50)

    for check in checks:
        # Filter out empty strings from command
        cmd = [arg for arg in check["cmd"] if arg]
        total_checks += 1

        if run_command(cmd, check["description"], check["fix_mode"]):
            success_count += 1

    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Summary: {success_count}/{total_checks} checks passed")

    if success_count == total_checks:
        print("🎉 All code quality checks passed!")
        return 0
    print("💥 Some checks failed. Please review and fix the issues.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
