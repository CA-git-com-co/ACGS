#!/usr/bin/env python3
"""
ACGS-1 Cleanup Results Analyzer

This script analyzes the cleanup analysis results and generates actionable recommendations.
"""

import json
import os
from pathlib import Path


def analyze_cleanup_results(results_file: str):
    """Analyze cleanup results and generate actionable recommendations."""

    print(f"📊 Analyzing cleanup results from {results_file}")

    with open(results_file) as f:
        data = json.load(f)

    summary = data.get("summary", {})

    print("\n🔍 CLEANUP ANALYSIS SUMMARY")
    print("=" * 50)
    print(f"Total exact duplicate groups: {summary.get('total_exact_duplicates', 0)}")
    print(f"Total similar file groups: {summary.get('total_similar_files', 0)}")
    print(f"Total obsolete files: {summary.get('total_obsolete_files', 0)}")
    print(f"Files safe to remove: {summary.get('total_safe_to_remove', 0)}")
    print(f"Critical files preserved: {summary.get('critical_files_preserved', 0)}")

    # Analyze duplicate groups
    print("\n🔄 TOP DUPLICATE GROUPS")
    print("=" * 30)

    duplicates = data.get("duplicates", {}).get("exact_duplicates", [])

    # Sort by number of files in each group
    sorted_duplicates = sorted(
        duplicates, key=lambda x: len(x.get("files", [])), reverse=True
    )

    for i, dup_group in enumerate(sorted_duplicates[:10]):  # Top 10
        files = dup_group.get("files", [])
        critical_files = dup_group.get("critical_files", [])
        non_critical_files = dup_group.get("non_critical_files", [])

        print(f"\n{i + 1}. Duplicate group with {len(files)} files:")
        print(f"   Critical files: {len(critical_files)}")
        print(f"   Non-critical files: {len(non_critical_files)}")

        # Show first few files as examples
        for j, file_path in enumerate(files[:3]):
            print(f"   - {Path(file_path).name}")
        if len(files) > 3:
            print(f"   ... and {len(files) - 3} more")

    # Analyze service duplicates specifically
    print("\n🏗️ SERVICE DUPLICATE ANALYSIS")
    print("=" * 35)

    service_duplicates = {}
    for dup_group in duplicates:
        files = dup_group.get("files", [])
        for file_path in files:
            if "services/core/" in file_path:
                service_name = extract_service_name(file_path)
                if service_name:
                    if service_name not in service_duplicates:
                        service_duplicates[service_name] = []
                    service_duplicates[service_name].append(file_path)

    for service, files in service_duplicates.items():
        if len(files) > 1:
            print(f"\n{service}: {len(files)} duplicate instances")
            for file_path in files:
                print(f"   - {file_path}")

    # Analyze obsolete files
    print("\n🗑️ OBSOLETE FILES BREAKDOWN")
    print("=" * 32)

    obsolete = data.get("obsolete_files", {})
    for category, files in obsolete.items():
        if files:
            print(f"{category}: {len(files)} files")
            # Show examples
            for file_path in files[:3]:
                print(f"   - {Path(file_path).name}")
            if len(files) > 3:
                print(f"   ... and {len(files) - 3} more")

    # Generate specific recommendations
    print("\n💡 SPECIFIC CLEANUP RECOMMENDATIONS")
    print("=" * 42)

    recommendations = generate_specific_recommendations(data)

    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec['title']}")
        print(f"   Priority: {rec['priority']}")
        print(f"   Action: {rec['action']}")
        print(f"   Files affected: {rec['file_count']}")
        if rec.get("examples"):
            print(f"   Examples: {', '.join(rec['examples'][:3])}")


def extract_service_name(file_path: str) -> str:
    """Extract service name from file path."""
    if "services/core/" in file_path:
        parts = file_path.split("services/core/")[1].split("/")
        if parts:
            return parts[0]
    return ""


def generate_specific_recommendations(data):
    """Generate specific cleanup recommendations."""
    recommendations = []

    # Service duplicates
    duplicates = data.get("duplicates", {}).get("exact_duplicates", [])
    service_dups = []

    for dup_group in duplicates:
        files = dup_group.get("files", [])
        service_files = [f for f in files if "services/core/" in f]
        if len(service_files) > 1:
            service_dups.extend(service_files)

    if service_dups:
        recommendations.append(
            {
                "title": "Consolidate Duplicate Service Implementations",
                "priority": "HIGH",
                "action": "Keep the most recent/enhanced version, remove duplicates",
                "file_count": len(service_dups),
                "examples": [Path(f).name for f in service_dups[:5]],
            }
        )

    # Cache and temp files
    obsolete = data.get("obsolete_files", {})
    cache_files = obsolete.get("cache_files", [])
    temp_files = obsolete.get("temp_files", [])

    if cache_files:
        recommendations.append(
            {
                "title": "Remove Cache Files",
                "priority": "LOW",
                "action": "Safe to delete - will be regenerated",
                "file_count": len(cache_files),
                "examples": [Path(f).name for f in cache_files[:5]],
            }
        )

    if temp_files:
        recommendations.append(
            {
                "title": "Remove Temporary Files",
                "priority": "LOW",
                "action": "Safe to delete",
                "file_count": len(temp_files),
                "examples": [Path(f).name for f in temp_files[:5]],
            }
        )

    # Log files
    log_files = obsolete.get("log_files", [])
    if log_files:
        recommendations.append(
            {
                "title": "Archive or Remove Old Log Files",
                "priority": "MEDIUM",
                "action": "Archive important logs, remove old ones",
                "file_count": len(log_files),
                "examples": [Path(f).name for f in log_files[:5]],
            }
        )

    return recommendations


if __name__ == "__main__":
    # Find the most recent analysis file
    analysis_files = [
        f
        for f in os.listdir(".")
        if f.startswith("acgs_cleanup_analysis_") and f.endswith(".json")
    ]
    if analysis_files:
        latest_file = sorted(analysis_files)[-1]
        analyze_cleanup_results(latest_file)
    else:
        print("No cleanup analysis files found!")
