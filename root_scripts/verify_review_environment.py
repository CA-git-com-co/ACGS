#!/usr/bin/env python3
"""
Review Environment Verification Script
Ensures reviewers have the correct setup for PR #143 validation
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, capture_output=True):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=capture_output, text=True, check=False
        )
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)


def check_git_branch():
    """Verify we're on the correct branch"""
    print("🔍 Checking Git Branch...")

    success, branch, error = run_command("git branch --show-current")
    if not success:
        print(f"   ❌ Failed to get current branch: {error}")
        return False

    expected_branch = "feature/applications-directory-restructuring"
    if branch == expected_branch:
        print(f"   ✅ On correct branch: {branch}")
        return True
    else:
        print(f"   ❌ Wrong branch: {branch}")
        print(f"   Expected: {expected_branch}")
        print(f"   Run: git checkout {expected_branch}")
        return False


def check_required_files():
    """Check that all required review files exist"""
    print("\n🔍 Checking Required Files...")

    required_files = [
        "test_restructured_applications.py",
        "REVIEWER_CHECKLIST.md",
        "APPLICATIONS_RESTRUCTURING_REPORT.md",
        "REVIEW_COORDINATION.md",
        "restructure_applications.py",
    ]

    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"   ✅ Found: {file_path}")
        else:
            print(f"   ❌ Missing: {file_path}")
            all_exist = False

    return all_exist


def check_applications_structure():
    """Verify the applications directory structure"""
    print("\n🔍 Checking Applications Structure...")

    required_dirs = [
        "applications/shared",
        "applications/shared/components",
        "applications/shared/hooks",
        "applications/shared/types",
        "applications/governance-dashboard",
        "applications/legacy-frontend",
    ]

    all_exist = True
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"   ✅ Found: {dir_path}")
        else:
            print(f"   ❌ Missing: {dir_path}")
            all_exist = False

    return all_exist


def check_python_environment():
    """Check Python environment and dependencies"""
    print("\n🔍 Checking Python Environment...")

    # Check Python version
    success, version, error = run_command("python --version")
    if success:
        print(f"   ✅ Python version: {version}")
    else:
        print(f"   ❌ Python not found: {error}")
        return False

    # Check if we can import required modules
    try:
        import json
        import pathlib
        import subprocess

        print("   ✅ Required Python modules available")
        return True
    except ImportError as e:
        print(f"   ❌ Missing Python modules: {e}")
        return False


def check_git_status():
    """Check git status for any uncommitted changes"""
    print("\n🔍 Checking Git Status...")

    success, status, error = run_command("git status --porcelain")
    if not success:
        print(f"   ❌ Failed to get git status: {error}")
        return False

    if status.strip():
        print("   ⚠️  Uncommitted changes detected:")
        for line in status.split("\n"):
            if line.strip():
                print(f"      {line}")
        print("   Consider committing or stashing changes before review")
        return True  # Not a blocker, just a warning
    else:
        print("   ✅ Working directory clean")
        return True


def run_quick_validation():
    """Run a quick validation test"""
    print("\n🔍 Running Quick Validation...")

    if not Path("test_restructured_applications.py").exists():
        print("   ❌ Validation script not found")
        return False

    print("   🧪 Running automated tests...")
    success, output, error = run_command("python test_restructured_applications.py")

    if success and "ALL TESTS PASSED" in output:
        print("   ✅ Quick validation successful")
        return True
    else:
        print("   ❌ Validation failed")
        if error:
            print(f"   Error: {error}")
        return False


def main():
    """Main verification function"""
    print("🔧 ACGS-PGP PR #143 Review Environment Verification")
    print("=" * 60)

    checks = [
        ("Git Branch", check_git_branch),
        ("Required Files", check_required_files),
        ("Applications Structure", check_applications_structure),
        ("Python Environment", check_python_environment),
        ("Git Status", check_git_status),
        ("Quick Validation", run_quick_validation),
    ]

    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"   ❌ {check_name} failed with exception: {e}")
            results.append((check_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {check_name}")

    print(f"\nOverall: {passed}/{total} checks passed")

    if passed == total:
        print("\n🎉 ENVIRONMENT READY FOR REVIEW!")
        print("✅ You can proceed with the PR review process")
        print("\nNext steps:")
        print("1. Follow REVIEWER_CHECKLIST.md")
        print("2. Run: python test_restructured_applications.py")
        print("3. Complete manual verification")
        return True
    else:
        print("\n⚠️  ENVIRONMENT NEEDS ATTENTION")
        print(f"❌ {total - passed} check(s) failed")
        print("\nPlease resolve the issues above before proceeding with review")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
