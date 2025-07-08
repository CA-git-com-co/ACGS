# Constitutional Hash: cdd01ef066bc6cf2

import json
import os
import re
from datetime import datetime

import yaml


def parse_markdown(file_path):
    """Parse markdown reports for metrics data with traceability."""
    metrics = {}
    source_info = {}

    with open(file_path) as f:
        lines = f.readlines()

    for i, line in enumerate(lines, 1):
        # Latency patterns - more flexible matching
        if re.search(r"P99.*Latency.*Ms?.*:", line, re.IGNORECASE):
            match = re.search(r"(\d+\.?\d*)", line)
            if match:
                metrics["latency_p99"] = f"{match.group(1)}ms"
                source_info["latency_p99"] = {"file": file_path, "line": i}

        if re.search(r"P95.*Latency.*Ms?.*:", line, re.IGNORECASE):
            match = re.search(r"(\d+\.?\d*)", line)
            if match:
                metrics["latency_p95"] = f"{match.group(1)}ms"
                source_info["latency_p95"] = {"file": file_path, "line": i}

        if re.search(r"P50.*Latency.*Ms?.*:", line, re.IGNORECASE):
            match = re.search(r"(\d+\.?\d*)", line)
            if match:
                metrics["latency_p50"] = f"{match.group(1)}ms"
                source_info["latency_p50"] = {"file": file_path, "line": i}

        # Avg Latency as fallback for P50
        if "latency_p50" not in metrics and re.search(
            r"Avg.*Latency.*Ms?.*:", line, re.IGNORECASE
        ):
            match = re.search(r"(\d+\.?\d*)", line)
            if match:
                metrics["latency_p50"] = f"{match.group(1)}ms"
                source_info["latency_p50"] = {"file": file_path, "line": i}

        # Throughput patterns
        if re.search(r"Throughput.*Rps.*:", line, re.IGNORECASE) or re.search(
            r"Avg.*Throughput.*Rps.*:", line, re.IGNORECASE
        ):
            match = re.search(r"(\d+\.?\d*)", line)
            if match:
                metrics["throughput_rps"] = int(float(match.group(1)))
                source_info["throughput_rps"] = {"file": file_path, "line": i}

        # Cache Hit Rate patterns
        if re.search(r"Cache.*Hit.*Rate.*Percent.*:", line, re.IGNORECASE):
            match = re.search(r"(\d+\.?\d*)", line)
            if match:
                metrics["cache_hit_rate"] = f"{int(float(match.group(1)))}%"
                source_info["cache_hit_rate"] = {"file": file_path, "line": i}

        # Security Score patterns
        if re.search(r"Security.*Score.*Percent.*:", line, re.IGNORECASE):
            match = re.search(r"(\d+\.?\d*)", line)
            if match:
                score = float(match.group(1))
                if score >= 90:
                    metrics["owasp_score"] = "A"
                elif score >= 80:
                    metrics["owasp_score"] = "B"
                elif score >= 70:
                    metrics["owasp_score"] = "C"
                else:
                    metrics["owasp_score"] = "D"
                source_info["owasp_score"] = {"file": file_path, "line": i}

        # Overall Security Score (alternative pattern)
        if re.search(r"Overall.*Security.*Score.*:", line, re.IGNORECASE):
            match = re.search(r"(\d+\.?\d*)", line)
            if match:
                score = float(match.group(1)) * 100  # Convert from decimal if needed
                if score >= 90:
                    metrics["owasp_score"] = "A"
                elif score >= 80:
                    metrics["owasp_score"] = "B"
                elif score >= 70:
                    metrics["owasp_score"] = "C"
                else:
                    metrics["owasp_score"] = "D"
                source_info["owasp_score"] = {"file": file_path, "line": i}

        # Hardening status
        if re.search(r"hardening.*passed", line, re.IGNORECASE) or re.search(
            r"production.*ready", line, re.IGNORECASE
        ):
            metrics["hardening"] = "passed"
            source_info["hardening"] = {"file": file_path, "line": i}

        # Constitutional hash
        if re.search(r"constitutional.*hash", line, re.IGNORECASE):
            match = re.search(r"`?([a-f0-9]{16})`?", line)
            if match:
                metrics["acgs_hash"] = match.group(1)
                source_info["acgs_hash"] = {"file": file_path, "line": i}

        # Date patterns
        if re.search(r"Generated.*:", line) or re.search(r"Report.*Date.*:", line):
            match = re.search(r"(\d{4}-\d{2}-\d{2})", line)
            if match:
                metrics["date"] = match.group(1)
                source_info["date"] = {"file": file_path, "line": i}

    return metrics, source_info


def parse_json(file_path):
    """Parse JSON reports for metrics data with traceability."""
    metrics = {}
    source_info = {}

    with open(file_path) as f:
        data = json.load(f)

    # Parse different JSON report structures
    def extract_from_nested(obj, path=""):
        for key, value in obj.items():
            current_path = f"{path}.{key}" if path else key

            if isinstance(value, dict):
                extract_from_nested(value, current_path)
            else:
                # Performance metrics
                if "p99_latency_ms" in key.lower():
                    metrics["latency_p99"] = f"{value}ms"
                    source_info["latency_p99"] = {
                        "file": file_path,
                        "path": current_path,
                    }
                elif "p95_latency_ms" in key.lower():
                    metrics["latency_p95"] = f"{value}ms"
                    source_info["latency_p95"] = {
                        "file": file_path,
                        "path": current_path,
                    }
                elif "p50_latency_ms" in key.lower():
                    metrics["latency_p50"] = f"{value}ms"
                    source_info["latency_p50"] = {
                        "file": file_path,
                        "path": current_path,
                    }
                elif "throughput_rps" in key.lower():
                    metrics["throughput_rps"] = int(float(value))
                    source_info["throughput_rps"] = {
                        "file": file_path,
                        "path": current_path,
                    }
                elif "cache_hit_rate" in key.lower():
                    if isinstance(value, float) and value <= 1.0:
                        metrics["cache_hit_rate"] = f"{int(value * 100)}%"
                    else:
                        metrics["cache_hit_rate"] = f"{int(float(value))}%"
                    source_info["cache_hit_rate"] = {
                        "file": file_path,
                        "path": current_path,
                    }
                elif "security_score" in key.lower():
                    score = float(value)
                    if score <= 1.0:  # Convert decimal to percentage
                        score *= 100
                    if score >= 90:
                        metrics["owasp_score"] = "A"
                    elif score >= 80:
                        metrics["owasp_score"] = "B"
                    elif score >= 70:
                        metrics["owasp_score"] = "C"
                    else:
                        metrics["owasp_score"] = "D"
                    source_info["owasp_score"] = {
                        "file": file_path,
                        "path": current_path,
                    }
                elif "constitutional_hash" in key.lower():
                    metrics["acgs_hash"] = str(value)
                    source_info["acgs_hash"] = {"file": file_path, "path": current_path}
                elif key.lower() in ["timestamp", "generated", "execution_start"]:
                    # Extract date from timestamp
                    date_match = re.search(r"(\d{4}-\d{2}-\d{2})", str(value))
                    if date_match:
                        metrics["date"] = date_match.group(1)
                        source_info["date"] = {"file": file_path, "path": current_path}

    # Check for hardening status
    if (
        "overall_summary" in data
        and "constitutional_compliance" in data["overall_summary"]
    ):
        if data["overall_summary"]["constitutional_compliance"]:
            metrics["hardening"] = "passed"
            source_info["hardening"] = {
                "file": file_path,
                "path": "overall_summary.constitutional_compliance",
            }

    extract_from_nested(data)
    return metrics, source_info


files_to_parse = [
    "/home/dislove/ACGS-2/reports/ACGS_PRODUCTION_DEPLOYMENT_FINAL_REPORT.md",
    "/home/dislove/ACGS-2/reports/acgs_production_readiness_certification.md",
    "/home/dislove/ACGS-2/reports/acgs_production_readiness_final_certification.md",
    "/home/dislove/ACGS-2/reports/cache_optimization_deployment.md",
    "/home/dislove/ACGS-2/reports/performance_validation_report.md",
    "/home/dislove/ACGS-2/reports/security_hardening_assessment.md",
    "/home/dislove/ACGS-2/infrastructure/quantumagi-validation/reports/quantumagi-validation-20250615_003851.json",
    "/home/dislove/ACGS-2/reports/compliance/compliance_result_20250707_085954.json",
    "/home/dislove/ACGS-2/reports/unified_orchestrator/acgs_comprehensive_suite_20250707_090004.json",
    "/home/dislove/ACGS-2/reports/unified_orchestrator/latest_comprehensive_suite.json",
]


def main():
    """Main execution function to extract and consolidate metrics."""
    all_metrics = {}
    all_source_info = {}

    print("Extracting metrics from report files...")

    for file_path in files_to_parse:
        if not os.path.exists(file_path):
            print(f"Warning: File not found - {file_path}")
            continue

        print(f"Processing: {os.path.basename(file_path)}")

        try:
            if file_path.endswith(".md"):
                metrics, source_info = parse_markdown(file_path)
            elif file_path.endswith(".json"):
                metrics, source_info = parse_json(file_path)
            else:
                continue

            # Update metrics with priority given to later files (more recent data)
            all_metrics.update(metrics)
            all_source_info.update(source_info)

            # Report what was found
            if metrics:
                print(f"  Found: {', '.join(metrics.keys())}")
            else:
                print("  No metrics found")

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    print(f"\nExtracted metrics: {list(all_metrics.keys())}")

    # Structuring the output as per the spec with traceability
    output = {
        "latency": {
            "p50": all_metrics.get("latency_p50"),
            "p95": all_metrics.get("latency_p95"),
            "p99": all_metrics.get("latency_p99"),
        },
        "throughput_rps": all_metrics.get("throughput_rps"),
        "cache_hit_rate": all_metrics.get("cache_hit_rate"),
        "security": {
            "owasp_score": all_metrics.get("owasp_score"),
            "hardening": all_metrics.get("hardening"),
        },
        "certification": {
            "acgs_hash": all_metrics.get("acgs_hash"),
            "date": all_metrics.get("date"),
        },
        # Add metadata for traceability
        "_metadata": {
            "generated_at": datetime.now().isoformat(),
            "source_files": len([f for f in files_to_parse if os.path.exists(f)]),
            "extracted_metrics": len(all_metrics),
            "sources": all_source_info,
        },
    }

    # Write the YAML file
    with open("production_metrics.yml", "w") as f:
        yaml.dump(output, f, default_flow_style=False, sort_keys=False)

    print("\nMetrics summary:")
    for key, value in all_metrics.items():
        source = all_source_info.get(key, {})
        if "file" in source:
            file_name = os.path.basename(source["file"])
            if "line" in source:
                print(f"  {key}: {value} (from {file_name}:{source['line']})")
            else:
                print(
                    f"  {key}: {value} (from"
                    f" {file_name}:{source.get('path', 'unknown')})"
                )
        else:
            print(f"  {key}: {value} (source unknown)")

    print("\nproduction_metrics.yml created successfully with traceability metadata.")


if __name__ == "__main__":
    main()
