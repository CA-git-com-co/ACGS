#!/usr/bin/env python3
"""
Parse validation_check.json and create a triaged volume mount analysis.
Groups broken paths by compose file and categorizes each path.
"""

import csv
import json
import re

import yaml


def categorize_path(path: str, compose_file: str) -> str:
    """
    Categorize a broken path into one of three categories:
    - "wrong relative root": path should start with infrastructure/docker/
    - "missing host directory": directory should be created
    - "legacy/unused": safe to delete
    """

    # Clean the path - remove container path part after :
    host_path = path.split(":")[0]

    # Patterns that indicate wrong relative root
    wrong_root_patterns = [
        r"^config/",
        r"^services/",
        r"^tests/",
        r"^tools/",
        r"^docs/",
        r"^infrastructure/(?!docker)",
        r"^opencode_source/",
        r"^validation_reports/",
        r"^arxiv_submission_package/",
        r"^reorganization-tools/",
    ]

    # Patterns that indicate legacy/unused paths
    legacy_patterns = [
        r"node_modules",
        r"\.git",
        r"target/",
        r"dist/",
        r"build/",
        r"\.log$",
        r"\.cache",
        r"\.tmp",
        r"backup_\d+",
        r"_backup_",
        r"\.old$",
        r"\.bak$",
        r"test_\w+\.db",
        r"cli_backup_",
        r"opencode_adapter",
        r"gemini_cli",
    ]

    # Patterns that should probably be created (infrastructure-like paths)
    create_patterns = [
        r"^infrastructure/docker/",
        r"prometheus\.yml",
        r"grafana/",
        r"alertmanager\.yml",
        r"monitoring/",
        r"ssl/",
        r"certs/",
        r"policies/",
        r"init-scripts/",
        r"schemas?\.sql",
        r"migrations/",
    ]

    # Check for wrong relative root first
    for pattern in wrong_root_patterns:
        if re.match(pattern, host_path):
            return "wrong relative root"

    # Check for legacy/unused patterns
    for pattern in legacy_patterns:
        if re.search(pattern, host_path):
            return "legacy/unused"

    # Check if it matches create patterns
    for pattern in create_patterns:
        if re.search(pattern, host_path):
            return "missing host directory"

    # Special cases based on compose file context
    if "docker-compose" in compose_file:
        # If it's in a docker-compose file and we haven't categorized it yet,
        # it's likely a missing directory that should be created
        return "missing host directory"

    # Default to legacy/unused for unclear cases
    return "legacy/unused"


def load_validation_data(file_path: str) -> dict:
    """Load and parse the validation_check.json file."""
    with open(file_path) as f:
        return json.load(f)


def create_triaged_analysis(data: dict) -> list[dict]:
    """Create triaged analysis of broken volume mounts."""
    broken_refs = data.get("broken_references", {})
    results = []

    for compose_file, paths in broken_refs.items():
        for path in paths:
            category = categorize_path(path, compose_file)

            # Extract host and container paths
            path_parts = path.split(":")
            host_path = path_parts[0]
            container_path = path_parts[1] if len(path_parts) > 1 else ""
            mount_options = path_parts[2] if len(path_parts) > 2 else ""

            results.append({
                "compose_file": compose_file,
                "host_path": host_path,
                "container_path": container_path,
                "mount_options": mount_options,
                "full_mount": path,
                "category": category,
                "recommended_action": get_recommended_action(
                    category, host_path, compose_file
                ),
            })

    return results


def get_recommended_action(category: str, host_path: str, compose_file: str) -> str:
    """Get recommended action based on category."""
    actions = {
        "wrong relative root": "Update path to start with infrastructure/docker/",
        "missing host directory": f"Create directory: {host_path}",
        "legacy/unused": f"Remove mount from {compose_file}",
    }
    return actions.get(category, "Review manually")


def generate_csv_report(results: list[dict], output_file: str):
    """Generate CSV report of triaged volume mounts."""
    fieldnames = [
        "compose_file",
        "host_path",
        "container_path",
        "mount_options",
        "full_mount",
        "category",
        "recommended_action",
    ]

    with open(output_file, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


def generate_yaml_report(results: list[dict], output_file: str):
    """Generate YAML report grouped by compose file."""
    grouped = {}

    for result in results:
        compose_file = result["compose_file"]
        if compose_file not in grouped:
            grouped[compose_file] = {
                "wrong_relative_root": [],
                "missing_host_directory": [],
                "legacy_unused": [],
            }

        category_key = result["category"].replace("/", "_").replace(" ", "_")
        grouped[compose_file][category_key].append({
            "host_path": result["host_path"],
            "container_path": result["container_path"],
            "mount_options": result["mount_options"],
            "full_mount": result["full_mount"],
            "recommended_action": result["recommended_action"],
        })

    # Create summary statistics
    summary = {
        "total_broken_mounts": len(results),
        "compose_files_affected": len(grouped),
        "categories": {
            "wrong_relative_root": len([
                r for r in results if r["category"] == "wrong relative root"
            ]),
            "missing_host_directory": len([
                r for r in results if r["category"] == "missing host directory"
            ]),
            "legacy_unused": len([
                r for r in results if r["category"] == "legacy/unused"
            ]),
        },
    }

    final_report = {"summary": summary, "broken_volume_mounts_by_compose_file": grouped}

    with open(output_file, "w") as yamlfile:
        yaml.dump(
            final_report, yamlfile, default_flow_style=False, sort_keys=True, indent=2
        )


def generate_summary_stats(results: list[dict]) -> dict:
    """Generate summary statistics."""
    stats = {
        "total_broken_mounts": len(results),
        "compose_files_affected": len(set(r["compose_file"] for r in results)),
        "categories": {},
        "top_problematic_compose_files": {},
        "category_breakdown_by_file": {},
    }

    # Count by category
    for result in results:
        category = result["category"]
        compose_file = result["compose_file"]

        # Category totals
        stats["categories"][category] = stats["categories"].get(category, 0) + 1

        # Per-file totals
        stats["top_problematic_compose_files"][compose_file] = (
            stats["top_problematic_compose_files"].get(compose_file, 0) + 1
        )

        # Category breakdown by file
        if compose_file not in stats["category_breakdown_by_file"]:
            stats["category_breakdown_by_file"][compose_file] = {}
        stats["category_breakdown_by_file"][compose_file][category] = (
            stats["category_breakdown_by_file"][compose_file].get(category, 0) + 1
        )

    # Sort top problematic files
    stats["top_problematic_compose_files"] = dict(
        sorted(
            stats["top_problematic_compose_files"].items(),
            key=lambda x: x[1],
            reverse=True,
        )
    )

    return stats


def main():
    """Main function to process validation data and generate reports."""
    input_file = "validation_check.json"

    # Load data
    print("Loading validation data...")
    data = load_validation_data(input_file)

    # Create triaged analysis
    print("Analyzing and categorizing broken volume mounts...")
    results = create_triaged_analysis(data)

    # Generate summary statistics
    stats = generate_summary_stats(results)

    # Print summary to console
    print(f"\n{'=' * 60}")
    print("VOLUME MOUNT TRIAGE SUMMARY")
    print(f"{'=' * 60}")
    print(f"Total broken mounts: {stats['total_broken_mounts']}")
    print(f"Compose files affected: {stats['compose_files_affected']}")
    print("\nCategory breakdown:")
    for category, count in stats["categories"].items():
        percentage = (count / stats["total_broken_mounts"]) * 100
        print(f"  {category}: {count} ({percentage:.1f}%)")

    print("\nTop 10 most problematic compose files:")
    for i, (file, count) in enumerate(
        list(stats["top_problematic_compose_files"].items())[:10]
    ):
        print(f"  {i + 1:2d}. {file}: {count} issues")

    # Generate reports
    print("\nGenerating reports...")

    # CSV report
    csv_file = "volume_mount_triage.csv"
    generate_csv_report(results, csv_file)
    print(f"✓ CSV report: {csv_file}")

    # YAML report
    yaml_file = "volume_mount_triage.yaml"
    generate_yaml_report(results, yaml_file)
    print(f"✓ YAML report: {yaml_file}")

    # Summary stats YAML
    summary_file = "volume_mount_triage_summary.yaml"
    with open(summary_file, "w") as f:
        yaml.dump(stats, f, default_flow_style=False, sort_keys=True, indent=2)
    print(f"✓ Summary stats: {summary_file}")

    print(f"\n{'=' * 60}")
    print("Reports generated successfully!")
    print("Use these artifacts to drive surgical edits in subsequent steps.")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
