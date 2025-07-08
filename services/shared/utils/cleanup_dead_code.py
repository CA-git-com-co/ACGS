#!/usr/bin/env python3
"""
Dead Code Cleanup Utility
Constitutional Hash: cdd01ef066bc6cf2

This script identifies and helps remove unused imports and dead code
from the ACGS codebase using ruff.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def run_ruff_check(path: str) -> dict:
    """Run ruff check and return results as JSON."""
    try:
        result = subprocess.run(
            ["ruff", "check", path, "--output-format=json"],
            capture_output=True,
            text=True,
            check=False
        )

        if result.stdout:
            return json.loads(result.stdout)
        return []
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        print(f"Error running ruff: {e}")
        return []


def run_ruff_fix(path: str, unsafe: bool = False) -> bool:
    """Run ruff with --fix flag."""
    try:
        cmd = ["ruff", "check", "--fix", path]
        if unsafe:
            cmd.append("--unsafe-fixes")

        result = subprocess.run(cmd, check=False, capture_output=True, text=True)
        return result.returncode == 0
    except subprocess.CalledProcessError:
        return False


def analyze_dead_code(base_path: str) -> dict[str, list[dict]]:
    """Analyze the codebase for dead code patterns."""
    issues = run_ruff_check(base_path)

    dead_code_patterns = {
        "unused_imports": [],
        "unused_variables": [],
        "unreachable_code": [],
        "redundant_code": []
    }

    for issue in issues:
        code = issue.get("code", "")

        if code in ["F401", "F811"]:  # Unused imports
            dead_code_patterns["unused_imports"].append(issue)
        elif code == "F841":  # Unused variables
            dead_code_patterns["unused_variables"].append(issue)
        elif code in ["F401", "F811", "F821", "F822", "F823"]:  # Various unused patterns
            dead_code_patterns["redundant_code"].append(issue)

    return dead_code_patterns


def get_python_files(base_path: str) -> list[str]:
    """Get all Python files in the codebase."""
    path_obj = Path(base_path)
    python_files = []

    for file_path in path_obj.rglob("*.py"):
        # Skip test files and certain directories
        if any(skip in str(file_path) for skip in [
            "__pycache__", ".venv", ".git", "node_modules",
            ".pytest_cache", ".mypy_cache", "build", "dist"
        ]):
            continue
        python_files.append(str(file_path))

    return python_files


def clean_file(file_path: str, dry_run: bool = True) -> dict:
    """Clean a single file and return statistics."""
    stats = {
        "file": file_path,
        "issues_found": 0,
        "issues_fixed": 0,
        "errors": []
    }

    # Get issues before fixing
    issues_before = run_ruff_check(file_path)
    stats["issues_found"] = len(issues_before)

    if not dry_run and stats["issues_found"] > 0:
        # Try to fix automatically
        success = run_ruff_fix(file_path, unsafe=False)
        if success:
            # Check how many issues remain
            issues_after = run_ruff_check(file_path)
            stats["issues_fixed"] = stats["issues_found"] - len(issues_after)
        else:
            stats["errors"].append("Failed to run ruff fix")

    return stats


def generate_report(dead_code_analysis: dict, cleanup_stats: list[dict]) -> str:
    """Generate a comprehensive report."""
    report = []
    report.append("=" * 60)
    report.append("ACGS Dead Code Cleanup Report")
    report.append("Constitutional Hash: cdd01ef066bc6cf2")
    report.append("=" * 60)
    report.append("")

    # Summary of dead code patterns
    report.append("DEAD CODE ANALYSIS:")
    report.append("-" * 30)
    for pattern, issues in dead_code_analysis.items():
        report.append(f"{pattern.replace('_', ' ').title()}: {len(issues)} issues")
    report.append("")

    # File-by-file cleanup stats
    total_files = len(cleanup_stats)
    files_with_issues = sum(1 for stat in cleanup_stats if stat["issues_found"] > 0)
    total_issues = sum(stat["issues_found"] for stat in cleanup_stats)
    total_fixed = sum(stat["issues_fixed"] for stat in cleanup_stats)

    report.append("CLEANUP STATISTICS:")
    report.append("-" * 30)
    report.append(f"Total files processed: {total_files}")
    report.append(f"Files with issues: {files_with_issues}")
    report.append(f"Total issues found: {total_issues}")
    report.append(f"Issues automatically fixed: {total_fixed}")
    report.append(f"Remaining issues: {total_issues - total_fixed}")
    report.append("")

    # Top problematic files
    problematic_files = sorted(
        [stat for stat in cleanup_stats if stat["issues_found"] > 0],
        key=lambda x: x["issues_found"],
        reverse=True
    )[:10]

    if problematic_files:
        report.append("TOP PROBLEMATIC FILES:")
        report.append("-" * 30)
        for stat in problematic_files:
            report.append(f"{stat['file']}: {stat['issues_found']} issues")
        report.append("")

    # Detailed dead code examples
    report.append("DETAILED DEAD CODE EXAMPLES:")
    report.append("-" * 30)
    for pattern, issues in dead_code_analysis.items():
        if issues:
            report.append(f"\n{pattern.replace('_', ' ').title()}:")
            for issue in issues[:5]:  # Show first 5 examples
                filename = issue.get("filename", "unknown")
                line = issue.get("location", {}).get("row", "?")
                message = issue.get("message", "")
                report.append(f"  {filename}:{line} - {message}")
            if len(issues) > 5:
                report.append(f"  ... and {len(issues) - 5} more")

    return "\n".join(report)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Clean up dead code in ACGS codebase")
    parser.add_argument("path", help="Path to the codebase directory")
    parser.add_argument("--dry-run", action="store_true",
                       help="Only analyze, don't fix issues")
    parser.add_argument("--output", "-o", help="Output file for report")
    parser.add_argument("--fix", action="store_true",
                       help="Actually fix issues (opposite of dry-run)")

    args = parser.parse_args()

    if not Path(args.path).exists():
        print(f"Error: Path {args.path} does not exist")
        return 1

    dry_run = args.dry_run or not args.fix

    print("ACGS Dead Code Cleanup Tool")
    print("Constitutional Hash: cdd01ef066bc6cf2")
    print("=" * 50)
    print(f"Analyzing codebase at: {args.path}")
    print(f"Mode: {'DRY RUN' if dry_run else 'FIX MODE'}")
    print()

    # Get all Python files
    print("Discovering Python files...")
    python_files = get_python_files(args.path)
    print(f"Found {len(python_files)} Python files")

    # Analyze dead code patterns
    print("Analyzing dead code patterns...")
    dead_code_analysis = analyze_dead_code(args.path)

    # Clean files
    print("Processing files...")
    cleanup_stats = []
    for i, file_path in enumerate(python_files, 1):
        if i % 50 == 0:
            print(f"Processed {i}/{len(python_files)} files...")

        stats = clean_file(file_path, dry_run=dry_run)
        cleanup_stats.append(stats)

    # Generate report
    print("Generating report...")
    report = generate_report(dead_code_analysis, cleanup_stats)

    # Output report
    if args.output:
        with open(args.output, "w") as f:
            f.write(report)
        print(f"Report saved to: {args.output}")
    else:
        print("\n" + report)

    return 0


if __name__ == "__main__":
    sys.exit(main())
