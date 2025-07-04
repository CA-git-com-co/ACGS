#!/usr/bin/env python3
"""
Fix Test Import Issues Script
Systematically fixes import path issues in test files that use hyphens instead of underscores.
"""

import os

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"



def fix_import_paths(file_path):
    """Fix import paths in a single file."""
    print(f"Fixing imports in: {file_path}")

    with open(file_path) as f:
        content = f.read()

    # Define the replacements for hyphened directory names
    replacements = [
        # Core service directory fixes
        ("services.core.governance-synthesis", "services.core.governance_synthesis"),
        ("services.core.constitutional-ai", "services.core.constitutional_ai"),
        ("services.core.formal-verification", "services.core.formal_verification"),
        ("services.core.policy-governance", "services.core.policy_governance"),
        ("services.core.self-evolving-ai", "services.core.self_evolving_ai"),
        (
            "services.core.evolutionary-computation",
            "services.core.evolutionary_computation",
        ),
        ("services.core.governance-workflows", "services.core.governance_workflows"),
        # Platform service directory fixes
        ("services.platform.pgc", "services.platform.pgc"),
        # Integration directory fixes
        ("integrations.alphaevolve-engine", "integrations.alphaevolve_engine"),
    ]

    # Apply replacements
    original_content = content
    for old_path, new_path in replacements:
        content = content.replace(old_path, new_path)

    # Write back if changes were made
    if content != original_content:
        with open(file_path, "w") as f:
            f.write(content)
        print(f"  ✅ Fixed imports in {file_path}")
        return True
    print(f"  ⏭️  No changes needed in {file_path}")
    return False


def find_test_files_with_import_issues():
    """Find all test files that might have import issues."""
    test_dirs = [
        "tests/integration",
        "tests/unit",
        "tests/performance",
        "tests/enhanced",
        "tests/adversarial",
    ]

    files_with_issues = []

    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            for root, dirs, files in os.walk(test_dir):
                for file in files:
                    if file.endswith(".py"):
                        file_path = os.path.join(root, file)

                        # Check if file contains problematic imports
                        try:
                            with open(file_path) as f:
                                content = f.read()

                            # Look for hyphened imports
                            if any(
                                pattern in content
                                for pattern in [
                                    "governance-synthesis",
                                    "constitutional-ai",
                                    "formal-verification",
                                    "policy-governance",
                                    "self-evolving-ai",
                                    "evolutionary-computation",
                                    "governance-workflows",
                                    "alphaevolve-engine",
                                ]
                            ):
                                files_with_issues.append(file_path)

                        except Exception as e:
                            print(f"Warning: Could not read {file_path}: {e}")

    return files_with_issues


def main():
    """Main execution function."""
    print("🔧 ACGS-1 Test Import Path Fixer")
    print("=" * 50)

    # Find files with import issues
    print("🔍 Scanning for test files with import issues...")
    files_with_issues = find_test_files_with_import_issues()

    if not files_with_issues:
        print("✅ No test files with import issues found!")
        return

    print(f"📋 Found {len(files_with_issues)} files with import issues:")
    for file_path in files_with_issues:
        print(f"  - {file_path}")

    print("\n🔧 Fixing import paths...")

    # Fix each file
    fixed_count = 0
    for file_path in files_with_issues:
        if fix_import_paths(file_path):
            fixed_count += 1

    print("\n📊 Summary:")
    print(f"  📁 Files scanned: {len(files_with_issues)}")
    print(f"  ✅ Files fixed: {fixed_count}")
    print(f"  ⏭️  Files unchanged: {len(files_with_issues) - fixed_count}")

    if fixed_count > 0:
        print(f"\n🎉 Successfully fixed import paths in {fixed_count} test files!")
        print("🧪 You can now run the test suite to verify the fixes.")
    else:
        print("\n⚠️  No files were modified. Import issues may be more complex.")


if __name__ == "__main__":
    main()
