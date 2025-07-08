#!/usr/bin/env python3
# Constitutional Hash: cdd01ef066bc6cf2
r"""
ACGS Paper Metrics Transformation Script

This script takes the mapping table & production_metrics.yml, opens the paper source,
and replaces each theoretical placeholder with the actual metric, adding \cite{perf-report}
style citations to the corresponding report anchors.

Adds "(see Appendix B)" cross-references where raw data is large.
"""

import argparse
import re
import shutil
from datetime import datetime
from pathlib import Path

import yaml


def load_yaml(file_path):
    """Load YAML file safely."""
    with open(file_path) as file:
        return yaml.safe_load(file)


def get_nested_value(data, path):
    """Get nested value from dictionary using dot notation."""
    keys = path.split(".")
    value = data
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return None
    return value


def format_metric_value(value, metric_type=None):
    """Format metric value appropriately."""
    if isinstance(value, str):
        return value
    elif isinstance(value, (int, float)):
        if metric_type == "percentage":
            return f"{value}%"
        elif metric_type == "latency":
            return f"{value}ms"
        elif metric_type == "throughput":
            return f"{value}"
        else:
            return str(value)
    else:
        return str(value)


def replace_placeholders_in_paper(paper_path, production_metrics, mapping_table):
    """Replace theoretical placeholders with production metrics."""
    # Create backup
    backup_path = f"{paper_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(paper_path, backup_path)
    print(f"Created backup: {backup_path}")

    # Read the content of the paper
    with open(paper_path, encoding="utf-8") as file:
        content = file.read()

    replacements_made = []

    # Process theoretical placeholders
    if "theoretical_placeholders" in mapping_table:
        for placeholder_pattern, mapping_info in mapping_table[
            "theoretical_placeholders"
        ].items():
            # Get the production metric value
            production_path = mapping_info.get("production_metric")
            if production_path:
                actual_value = get_nested_value(production_metrics, production_path)
                if actual_value is not None:
                    # Use the formatted value from mapping or format the actual value
                    formatted_value = mapping_info.get("formatted_value")
                    if not formatted_value:
                        formatted_value = format_metric_value(actual_value)

                    # Build replacement string with citation and appendix reference
                    citation = mapping_info.get("citation", "")
                    appendix_ref = mapping_info.get("appendix_ref", "")
                    replacement = f"{formatted_value}{citation}{appendix_ref}"

                    # Count matches before replacement
                    matches = len(re.findall(placeholder_pattern, content))
                    if matches > 0:
                        # Escape backslashes in replacement string for regex
                        escaped_replacement = replacement.replace("\\", "\\\\")
                        content = re.sub(
                            placeholder_pattern, escaped_replacement, content
                        )
                        replacements_made.append({
                            "placeholder": placeholder_pattern,
                            "replacement": replacement,
                            "matches": matches,
                            "description": mapping_info.get(
                                "description", "No description"
                            ),
                        })
                        print(
                            f"Replaced {matches} instances of '{placeholder_pattern}'"
                            f" with '{replacement}'"
                        )

    # Write updated content back to the paper
    with open(paper_path, "w", encoding="utf-8") as file:
        file.write(content)

    return replacements_made


def generate_report(replacements_made, report_path):
    """Generate a report of all replacements made."""
    with open(report_path, "w") as f:
        f.write("# Paper Metrics Update Report\n\n")
        f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Total Replacements**: {len(replacements_made)}\n\n")

        f.write("## Replacements Made\n\n")
        for replacement in replacements_made:
            f.write(f"### {replacement['placeholder']}\n")
            f.write(f"- **Replaced with**: {replacement['replacement']}\n")
            f.write(f"- **Instances**: {replacement['matches']}\n")
            f.write(f"- **Description**: {replacement['description']}\n\n")

        if not replacements_made:
            f.write("No replacements were made.\n")


def main():
    parser = argparse.ArgumentParser(
        description="Update paper metrics with production data"
    )
    parser.add_argument(
        "--mapping-table",
        default="mapping_table.yml",
        help="Path to mapping table YAML file",
    )
    parser.add_argument(
        "--production-metrics",
        default="production_metrics.yml",
        help="Path to production metrics YAML file",
    )
    parser.add_argument(
        "--paper-source",
        default="docs/research/arxiv_submission_package/main.tex",
        help="Path to paper source file",
    )
    parser.add_argument(
        "--report", default="metrics_update_report.md", help="Path for output report"
    )

    args = parser.parse_args()

    # Load configuration files
    try:
        production_metrics = load_yaml(args.production_metrics)
        mapping_table = load_yaml(args.mapping_table)
    except FileNotFoundError as e:
        print(f"Error: Could not find file {e.filename}")
        return 1
    except yaml.YAMLError as e:
        print(f"Error parsing YAML: {e}")
        return 1

    # Check if paper source exists
    if not Path(args.paper_source).exists():
        print(f"Error: Paper source file not found: {args.paper_source}")
        return 1

    print(f"Loading production metrics from: {args.production_metrics}")
    print(f"Loading mapping table from: {args.mapping_table}")
    print(f"Updating paper source: {args.paper_source}")

    # Perform replacements
    replacements_made = replace_placeholders_in_paper(
        args.paper_source, production_metrics, mapping_table
    )

    # Generate report
    generate_report(replacements_made, args.report)
    print(f"\nUpdate complete! Report saved to: {args.report}")
    print(f"Total replacements made: {len(replacements_made)}")

    return 0


if __name__ == "__main__":
    exit(main())
