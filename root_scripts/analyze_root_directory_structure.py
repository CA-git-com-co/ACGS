#!/usr/bin/env python3
"""
ACGS-1 Root Directory Analysis Script
Analyzes all files in the root directory and categorizes them for cleanup and reorganization.
"""

import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path


def analyze_root_directory():
    """Analyze all files in the root directory and categorize them."""

    root_path = Path()
    analysis = {
        "timestamp": datetime.now().isoformat(),
        "total_files": 0,
        "categories": defaultdict(list),
        "file_types": defaultdict(int),
        "size_analysis": {},
        "age_analysis": {},
        "critical_files": [],
        "temporary_files": [],
        "duplicate_candidates": [],
        "cleanup_recommendations": [],
    }

    # Critical files that must be preserved
    critical_patterns = [
        r"^package\.json$",
        r"^package-lock\.json$",
        r"^requirements.*\.txt$",
        r"^Cargo\.toml$",
        r"^Cargo\.lock$",
        r"^pyproject\.toml$",
        r"^uv\.lock$",
        r"^\.env.*",
        r"^docker-compose.*\.yml$",
        r"^docker-compose.*\.yaml$",
        r"^Dockerfile.*",
        r"^Makefile$",
        r"^README\.md$",
        r"^SECURITY\.md$",
        r"^LICENSE$",
        r"^CONTRIBUTING\.md$",
        r"^CHANGELOG\.md$",
        r"^\.github/",
        r"^jest\.config\.js$",
        r"^pytest\.ini$",
        r"^tsconfig\.json$",
    ]

    # Temporary/cleanup candidates
    temp_patterns = [
        r"__pycache__",
        r"\.pyc$",
        r"\.pyo$",
        r"\.tmp$",
        r"\.temp$",
        r"_temp_",
        r"test-ledger",
        r"venv/",
        r"node_modules/",
        r"\.log$",
        r"_\d{8}_\d{6}\.json$",  # Timestamped JSON files
        r"_\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}\.md$",  # Timestamped MD files
    ]

    # Report file patterns
    report_patterns = [
        r".*_report.*\.json$",
        r".*_report.*\.md$",
        r".*_analysis.*\.json$",
        r".*_results.*\.json$",
        r".*_summary.*\.json$",
        r".*_completion.*\.md$",
        r".*REPORT.*\.md$",
        r".*ANALYSIS.*\.md$",
        r".*SUMMARY.*\.md$",
    ]

    # Script patterns
    script_patterns = [r".*\.py$", r".*\.sh$", r".*\.js$"]

    # Get all files in root directory (excluding subdirectories)
    for item in root_path.iterdir():
        if item.is_file():
            analysis["total_files"] += 1
            file_path = str(item)
            file_name = item.name
            file_size = item.stat().st_size
            file_mtime = datetime.fromtimestamp(item.stat().st_mtime)
            file_age_days = (datetime.now() - file_mtime).days

            # File type analysis
            file_ext = item.suffix.lower()
            analysis["file_types"][file_ext] += 1

            # Size analysis
            if file_size > 10 * 1024 * 1024:  # > 10MB
                analysis["size_analysis"][
                    file_name
                ] = f"{file_size / (1024 * 1024):.1f}MB"

            # Age analysis
            if file_age_days > 30:
                analysis["age_analysis"][file_name] = f"{file_age_days} days old"

            # Categorize files
            file_info = {
                "name": file_name,
                "path": file_path,
                "size": file_size,
                "age_days": file_age_days,
                "modified": file_mtime.isoformat(),
            }

            # Check if critical file
            is_critical = any(
                re.match(pattern, file_name) for pattern in critical_patterns
            )
            if is_critical:
                analysis["critical_files"].append(file_info)
                analysis["categories"]["critical"].append(file_info)
                continue

            # Check if temporary file
            is_temp = any(re.search(pattern, file_name) for pattern in temp_patterns)
            if is_temp:
                analysis["temporary_files"].append(file_info)
                analysis["categories"]["temporary"].append(file_info)
                continue

            # Check if report file
            is_report = any(
                re.search(pattern, file_name) for pattern in report_patterns
            )
            if is_report:
                analysis["categories"]["reports"].append(file_info)
                continue

            # Check if script file
            is_script = any(
                re.search(pattern, file_name) for pattern in script_patterns
            )
            if is_script and not is_critical:
                analysis["categories"]["scripts"].append(file_info)
                continue

            # Documentation files
            if file_ext in [".md", ".txt", ".rst"]:
                analysis["categories"]["documentation"].append(file_info)
                continue

            # Configuration files
            if file_ext in [".json", ".yaml", ".yml", ".toml", ".ini", ".conf"]:
                analysis["categories"]["configuration"].append(file_info)
                continue

            # Log files
            if ".log" in file_name or "log" in file_name.lower():
                analysis["categories"]["logs"].append(file_info)
                continue

            # Everything else
            analysis["categories"]["other"].append(file_info)

    # Generate cleanup recommendations
    analysis["cleanup_recommendations"] = generate_cleanup_recommendations(analysis)

    return analysis


def generate_cleanup_recommendations(analysis):
    """Generate specific cleanup recommendations based on analysis."""
    recommendations = []

    # Temporary files cleanup
    temp_count = len(analysis["categories"]["temporary"])
    if temp_count > 0:
        recommendations.append(
            {
                "action": "DELETE_TEMPORARY",
                "description": f"Delete {temp_count} temporary files including __pycache__, .pyc files, and temp directories",
                "files": [f["name"] for f in analysis["categories"]["temporary"]],
                "priority": "HIGH",
            }
        )

    # Reports consolidation
    report_count = len(analysis["categories"]["reports"])
    if report_count > 10:
        recommendations.append(
            {
                "action": "CONSOLIDATE_REPORTS",
                "description": f"Move {report_count} report files to reports/ directory and consolidate similar reports",
                "files": [f["name"] for f in analysis["categories"]["reports"]],
                "priority": "HIGH",
            }
        )

    # Scripts organization
    script_count = len(analysis["categories"]["scripts"])
    if script_count > 5:
        recommendations.append(
            {
                "action": "ORGANIZE_SCRIPTS",
                "description": f"Move {script_count} script files to scripts/ directory with proper categorization",
                "files": [f["name"] for f in analysis["categories"]["scripts"]],
                "priority": "MEDIUM",
            }
        )

    # Old files archival
    old_files = [f for f in analysis["age_analysis"].keys()]
    if len(old_files) > 0:
        recommendations.append(
            {
                "action": "ARCHIVE_OLD_FILES",
                "description": f"Archive {len(old_files)} files older than 30 days",
                "files": old_files,
                "priority": "MEDIUM",
            }
        )

    # Large files review
    large_files = list(analysis["size_analysis"].keys())
    if len(large_files) > 0:
        recommendations.append(
            {
                "action": "REVIEW_LARGE_FILES",
                "description": f"Review {len(large_files)} large files for potential cleanup",
                "files": large_files,
                "priority": "LOW",
            }
        )

    return recommendations


def main():
    """Main execution function."""
    print("🔍 Analyzing ACGS-1 root directory structure...")

    analysis = analyze_root_directory()

    # Save analysis to file
    output_file = (
        f"root_directory_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    with open(output_file, "w") as f:
        json.dump(analysis, f, indent=2, default=str)

    # Print summary
    print(f"\n📊 Analysis Complete - Results saved to {output_file}")
    print(f"Total files analyzed: {analysis['total_files']}")
    print(f"Critical files (preserve): {len(analysis['critical_files'])}")
    print(f"Temporary files (delete): {len(analysis['categories']['temporary'])}")
    print(f"Report files: {len(analysis['categories']['reports'])}")
    print(f"Script files: {len(analysis['categories']['scripts'])}")
    print(f"Documentation files: {len(analysis['categories']['documentation'])}")
    print(f"Configuration files: {len(analysis['categories']['configuration'])}")
    print(f"Log files: {len(analysis['categories']['logs'])}")
    print(f"Other files: {len(analysis['categories']['other'])}")

    print(f"\n�� Cleanup Recommendations: {len(analysis['cleanup_recommendations'])}")
    for i, rec in enumerate(analysis["cleanup_recommendations"], 1):
        print(
            f"{i}. {rec['action']}: {rec['description']} (Priority: {rec['priority']})"
        )

    return output_file


if __name__ == "__main__":
    main()
