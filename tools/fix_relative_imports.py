#!/usr/bin/env python3
"""
Fix Relative Import Issues in Service Mesh Module
Converts relative imports to absolute imports to fix pytest collection errors.
"""

import os
import re

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"



def fix_relative_imports_in_file(file_path):
    """Fix relative imports in a single file."""
    print(f"Fixing relative imports in: {file_path}")

    with open(file_path) as f:
        content = f.read()

    # Define patterns and replacements for relative imports
    replacements = [
        # Common relative import patterns
        (
            r"from \.\.common\.error_handling import",
            "from services.shared.common.error_handling import",
        ),
        (
            r"from \.\.common\.formatting import",
            "from services.shared.common.formatting import",
        ),
        (
            r"from \.\.common\.validation import",
            "from services.shared.common.validation import",
        ),
        (
            r"from \.\.common\.logging import",
            "from services.shared.common.logging import",
        ),
        (
            r"from \.\.common\.config import",
            "from services.shared.common.config import",
        ),
        (r"from \.\.common\.utils import", "from services.shared.common.utils import"),
        # Service mesh internal imports
        (
            r"from \.circuit_breaker import",
            "from services.shared.service_mesh.circuit_breaker import",
        ),
        (
            r"from \.registry import",
            "from services.shared.service_mesh.registry import",
        ),
        (
            r"from \.discovery import",
            "from services.shared.service_mesh.discovery import",
        ),
        (r"from \.client import", "from services.shared.service_mesh.client import"),
        # Other common patterns
        (r"from \.\.di\.", "from services.shared.di."),
        (r"from \.\.events\.", "from services.shared.events."),
        (r"from \.\.models\.", "from services.shared.models."),
        (r"from \.\.schemas\.", "from services.shared.schemas."),
        (r"from \.\.utils\.", "from services.shared.utils."),
    ]

    # Apply replacements
    original_content = content
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)

    # Write back if changes were made
    if content != original_content:
        with open(file_path, "w") as f:
            f.write(content)
        print(f"  ✅ Fixed relative imports in {file_path}")
        return True
    print(f"  ⏭️  No relative imports found in {file_path}")
    return False


def find_files_with_relative_imports():
    """Find all Python files that might have relative import issues."""
    directories_to_check = [
        "services/shared/service_mesh",
        "services/shared/common",
        "services/shared/di",
        "services/shared/events",
    ]

    files_with_issues = []

    for directory in directories_to_check:
        if os.path.exists(directory):
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith(".py") and file != "__init__.py":
                        file_path = os.path.join(root, file)

                        # Check if file contains relative imports
                        try:
                            with open(file_path) as f:
                                content = f.read()

                            # Look for relative import patterns
                            if any(
                                pattern in content
                                for pattern in [
                                    "from ..",
                                    "from .",
                                ]
                            ):
                                files_with_issues.append(file_path)

                        except Exception as e:
                            print(f"Warning: Could not read {file_path}: {e}")

    return files_with_issues


def main():
    """Main execution function."""
    print("🔧 ACGS-1 Relative Import Fixer")
    print("=" * 50)

    # Find files with relative import issues
    print("🔍 Scanning for files with relative import issues...")
    files_with_issues = find_files_with_relative_imports()

    if not files_with_issues:
        print("✅ No files with relative import issues found!")
        return

    print(f"📋 Found {len(files_with_issues)} files with relative imports:")
    for file_path in files_with_issues:
        print(f"  - {file_path}")

    print("\n🔧 Fixing relative imports...")

    # Fix each file
    fixed_count = 0
    for file_path in files_with_issues:
        if fix_relative_imports_in_file(file_path):
            fixed_count += 1

    print("\n📊 Summary:")
    print(f"  📁 Files scanned: {len(files_with_issues)}")
    print(f"  ✅ Files fixed: {fixed_count}")
    print(f"  ⏭️  Files unchanged: {len(files_with_issues) - fixed_count}")

    if fixed_count > 0:
        print(f"\n🎉 Successfully fixed relative imports in {fixed_count} files!")
        print("🧪 You can now run the test suite to verify the fixes.")
    else:
        print("\n⚠️  No files were modified. Import issues may be more complex.")


if __name__ == "__main__":
    main()
