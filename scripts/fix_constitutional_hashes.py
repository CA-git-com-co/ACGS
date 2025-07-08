#!/usr/bin/env python3
"""
Fix Constitutional Hash Compliance
Constitutional Hash: cdd01ef066bc6cf2

This script adds the constitutional hash to files that are missing it.
"""

import os

# Constitutional hash
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Files that need constitutional hash (from validation report)
FILES_TO_FIX = [
    "docs/research/arxiv_submission_package/compilation_report.md",
    "docs/research/arxiv_submission_package/FINAL_POLISHING_REPORT.md",
    "docs/research/arxiv_submission_package/FINAL_SUBMISSION_REPORT.md",
    "docs/research/arxiv_submission_package/RESEARCH_INTEGRATION_REPORT.md",
    "docs/research/arxiv_submission_package/WARNINGS_OPTIMIZATION_FINAL_REPORT.md",
    "docs/research/arxiv_submission_package/COMPILER_README.md",
    "docs/research/arxiv_submission_package/COMPILATION_REPORT.md",
    "docs/research/arxiv_submission_package/cli/README.md",
]


def add_constitutional_hash_to_file(filepath):
    """Add constitutional hash to a file if it doesn't already have it."""
    if not os.path.exists(filepath):
        print(f"⚠️  File not found: {filepath}")
        return False

    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        # Check if constitutional hash already exists
        if CONSTITUTIONAL_HASH in content:
            print(f"✅ {filepath} already has constitutional hash")
            return True

        # Add constitutional hash based on file type
        if filepath.endswith(".md"):
            # For Markdown files, add as HTML comment after title
            lines = content.split("\n")
            if lines and lines[0].startswith("#"):
                lines.insert(1, f"<!-- Constitutional Hash: {CONSTITUTIONAL_HASH} -->")
                lines.insert(2, "")
            else:
                lines.insert(0, f"<!-- Constitutional Hash: {CONSTITUTIONAL_HASH} -->")
                lines.insert(1, "")
            content = "\n".join(lines)

        # Write back to file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"✅ Added constitutional hash to {filepath}")
        return True

    except Exception as e:
        print(f"❌ Error processing {filepath}: {e}")
        return False


def main():
    """Main function to fix constitutional hash compliance."""
    print("🔧 Fixing Constitutional Hash Compliance")
    print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print("=" * 60)

    total_files = len(FILES_TO_FIX)
    fixed_files = 0

    for filepath in FILES_TO_FIX:
        if add_constitutional_hash_to_file(filepath):
            fixed_files += 1

    print("=" * 60)
    print(f"📊 Results: {fixed_files}/{total_files} files processed successfully")

    if fixed_files == total_files:
        print("🎉 All files now have constitutional hash compliance!")
    else:
        print("⚠️  Some files could not be processed. Please review manually.")


if __name__ == "__main__":
    main()
