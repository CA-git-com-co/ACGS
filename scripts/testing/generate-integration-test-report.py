#!/usr/bin/env python3
"""
Constitutional Trainer Integration Test Report Generator

Generates comprehensive test reports from integration test results,
including performance metrics, compliance scores, and detailed analysis.

Usage:
    python generate-integration-test-report.py [OPTIONS]

Options:
    --input-file FILE       Input JSON test results file
    --output-dir DIR        Output directory for reports (default: ./reports)
    --format FORMAT         Report format: json, html, markdown (default: all)
    --include-metrics       Include detailed performance metrics
    --include-charts        Generate performance charts (requires matplotlib)
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import matplotlib.dates as mdates
    import matplotlib.pyplot as plt

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class IntegrationTestReportGenerator:
    """Generates comprehensive integration test reports."""

    def __init__(self, output_dir: str = "./reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def generate_report(
        self,
        test_results: dict[str, Any],
        formats: list[str] = ["json", "html", "markdown"],
        include_metrics: bool = True,
        include_charts: bool = False,
    ) -> dict[str, str]:
        """Generate test reports in specified formats."""

        generated_files = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Generate JSON report
        if "json" in formats:
            json_file = self.output_dir / f"integration_test_report_{timestamp}.json"
            self._generate_json_report(test_results, json_file)
            generated_files["json"] = str(json_file)

        # Generate HTML report
        if "html" in formats:
            html_file = self.output_dir / f"integration_test_report_{timestamp}.html"
            self._generate_html_report(test_results, html_file, include_metrics)
            generated_files["html"] = str(html_file)

        # Generate Markdown report
        if "markdown" in formats:
            md_file = self.output_dir / f"integration_test_report_{timestamp}.md"
            self._generate_markdown_report(test_results, md_file, include_metrics)
            generated_files["markdown"] = str(md_file)

        # Generate performance charts
        if include_charts and MATPLOTLIB_AVAILABLE:
            charts_dir = self.output_dir / f"charts_{timestamp}"
            charts_dir.mkdir(exist_ok=True)
            chart_files = self._generate_performance_charts(test_results, charts_dir)
            generated_files["charts"] = chart_files

        return generated_files

    def _generate_json_report(self, test_results: dict[str, Any], output_file: Path):
        """Generate JSON format report."""

        enhanced_results = {
            **test_results,
            "report_metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "generator_version": "1.0.0",
                "report_type": "constitutional_trainer_integration",
            },
        }

        with open(output_file, "w") as f:
            json.dump(enhanced_results, f, indent=2, default=str)

    def _generate_html_report(
        self,
        test_results: dict[str, Any],
        output_file: Path,
        include_metrics: bool = True,
    ):
        """Generate HTML format report."""

        summary = test_results.get("summary", {})
        performance = test_results.get("performance", {})
        test_cases = test_results.get("test_cases", [])

        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Constitutional Trainer Integration Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f4f4f4; padding: 20px; border-radius: 5px; }}
        .summary {{ display: flex; gap: 20px; margin: 20px 0; }}
        .metric-card {{ 
            background: white; 
            border: 1px solid #ddd; 
            border-radius: 5px; 
            padding: 15px; 
            flex: 1;
            text-align: center;
        }}
        .metric-value {{ font-size: 2em; font-weight: bold; }}
        .metric-label {{ color: #666; }}
        .test-case {{ 
            border: 1px solid #ddd; 
            margin: 10px 0; 
            padding: 15px; 
            border-radius: 5px;
        }}
        .status-passed {{ border-left: 5px solid #4CAF50; }}
        .status-failed {{ border-left: 5px solid #f44336; }}
        .status-error {{ border-left: 5px solid #ff9800; }}
        .performance-table {{ width: 100%; border-collapse: collapse; }}
        .performance-table th, .performance-table td {{ 
            border: 1px solid #ddd; 
            padding: 8px; 
            text-align: left; 
        }}
        .performance-table th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Constitutional Trainer Integration Test Report</h1>
        <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}</p>
        <p>Environment: {test_results.get("environment", {}).get("constitutional_trainer_url", "N/A")}</p>
    </div>
    
    <div class="summary">
        <div class="metric-card">
            <div class="metric-value">{summary.get("total_tests", 0)}</div>
            <div class="metric-label">Total Tests</div>
        </div>
        <div class="metric-card">
            <div class="metric-value" style="color: #4CAF50;">{summary.get("passed", 0)}</div>
            <div class="metric-label">Passed</div>
        </div>
        <div class="metric-card">
            <div class="metric-value" style="color: #f44336;">{summary.get("failed", 0)}</div>
            <div class="metric-label">Failed</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{summary.get("success_rate", 0):.1f}%</div>
            <div class="metric-label">Success Rate</div>
        </div>
    </div>
"""

        if include_metrics and performance:
            html_content += f"""
    <h2>Performance Metrics</h2>
    <table class="performance-table">
        <tr>
            <th>Metric</th>
            <th>Value</th>
            <th>Target</th>
            <th>Status</th>
        </tr>
        <tr>
            <td>Average Response Time</td>
            <td>{performance.get("avg_response_time_ms", 0):.2f} ms</td>
            <td>&lt; 2000 ms</td>
            <td>{"✅ Pass" if performance.get("avg_response_time_ms", 0) < 2000 else "❌ Fail"}</td>
        </tr>
        <tr>
            <td>Max Response Time</td>
            <td>{performance.get("max_response_time_ms", 0):.2f} ms</td>
            <td>&lt; 2000 ms</td>
            <td>{"✅ Pass" if performance.get("performance_target_met", False) else "❌ Fail"}</td>
        </tr>
    </table>
"""

        html_content += """
    <h2>Test Cases</h2>
"""

        for test_case in test_cases:
            status = test_case.get("status", "unknown")
            status_class = f"status-{status}"

            html_content += f"""
    <div class="test-case {status_class}">
        <h3>{test_case.get("name", "Unknown Test")}</h3>
        <p><strong>Status:</strong> {status.upper()}</p>
        <p><strong>Duration:</strong> {test_case.get("duration", 0):.2f} seconds</p>
"""

            if "response_time_ms" in test_case:
                html_content += f"<p><strong>Response Time:</strong> {test_case['response_time_ms']:.2f} ms</p>"

            if "error" in test_case:
                html_content += f"<p><strong>Error:</strong> {test_case['error']}</p>"

            html_content += "</div>"

        html_content += """
</body>
</html>
"""

        with open(output_file, "w") as f:
            f.write(html_content)

    def _generate_markdown_report(
        self,
        test_results: dict[str, Any],
        output_file: Path,
        include_metrics: bool = True,
    ):
        """Generate Markdown format report."""

        summary = test_results.get("summary", {})
        performance = test_results.get("performance", {})
        test_cases = test_results.get("test_cases", [])

        md_content = f"""# Constitutional Trainer Integration Test Report

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}  
**Environment:** {test_results.get("environment", {}).get("constitutional_trainer_url", "N/A")}

## Summary

| Metric | Value |
|--------|-------|
| Total Tests | {summary.get("total_tests", 0)} |
| Passed | {summary.get("passed", 0)} |
| Failed | {summary.get("failed", 0)} |
| Errors | {summary.get("errors", 0)} |
| Success Rate | {summary.get("success_rate", 0):.1f}% |

"""

        if include_metrics and performance:
            md_content += f"""## Performance Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Average Response Time | {performance.get("avg_response_time_ms", 0):.2f} ms | < 2000 ms | {"✅ Pass" if performance.get("avg_response_time_ms", 0) < 2000 else "❌ Fail"} |
| Max Response Time | {performance.get("max_response_time_ms", 0):.2f} ms | < 2000 ms | {"✅ Pass" if performance.get("performance_target_met", False) else "❌ Fail"} |

"""

        md_content += "## Test Cases\n\n"

        for test_case in test_cases:
            status = test_case.get("status", "unknown")
            status_emoji = {"passed": "✅", "failed": "❌", "error": "⚠️"}.get(
                status, "❓"
            )

            md_content += f"""### {status_emoji} {test_case.get("name", "Unknown Test")}

- **Status:** {status.upper()}
- **Duration:** {test_case.get("duration", 0):.2f} seconds
"""

            if "response_time_ms" in test_case:
                md_content += (
                    f"- **Response Time:** {test_case['response_time_ms']:.2f} ms\n"
                )

            if "error" in test_case:
                md_content += f"- **Error:** {test_case['error']}\n"

            md_content += "\n"

        with open(output_file, "w") as f:
            f.write(md_content)

    def _generate_performance_charts(
        self, test_results: dict[str, Any], charts_dir: Path
    ) -> list[str]:
        """Generate performance charts."""

        if not MATPLOTLIB_AVAILABLE:
            return []

        chart_files = []
        test_cases = test_results.get("test_cases", [])

        # Response time chart
        response_times = []
        test_names = []

        for test_case in test_cases:
            if "response_time_ms" in test_case:
                response_times.append(test_case["response_time_ms"])
                test_names.append(test_case.get("name", "Unknown"))

        if response_times:
            plt.figure(figsize=(12, 6))
            plt.bar(test_names, response_times)
            plt.title("Response Times by Test Case")
            plt.xlabel("Test Case")
            plt.ylabel("Response Time (ms)")
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()

            chart_file = charts_dir / "response_times.png"
            plt.savefig(chart_file)
            plt.close()
            chart_files.append(str(chart_file))

        return chart_files


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Generate Constitutional Trainer integration test reports"
    )

    parser.add_argument("--input-file", type=str, help="Input JSON test results file")

    parser.add_argument(
        "--output-dir",
        type=str,
        default="./reports",
        help="Output directory for reports (default: ./reports)",
    )

    parser.add_argument(
        "--format",
        choices=["json", "html", "markdown", "all"],
        default="all",
        help="Report format (default: all)",
    )

    parser.add_argument(
        "--include-metrics",
        action="store_true",
        default=True,
        help="Include detailed performance metrics",
    )

    parser.add_argument(
        "--include-charts",
        action="store_true",
        help="Generate performance charts (requires matplotlib)",
    )

    args = parser.parse_args()

    # Load test results
    if args.input_file:
        if not os.path.exists(args.input_file):
            print(f"Error: Input file not found: {args.input_file}")
            sys.exit(1)

        with open(args.input_file) as f:
            test_results = json.load(f)
    else:
        # Look for recent test results
        pattern = "constitutional_trainer_integration_report_*.json"
        import glob

        files = glob.glob(pattern)
        if not files:
            print("Error: No test results file specified and no recent results found")
            sys.exit(1)

        latest_file = max(files, key=os.path.getctime)
        print(f"Using latest test results: {latest_file}")

        with open(latest_file) as f:
            test_results = json.load(f)

    # Determine formats
    if args.format == "all":
        formats = ["json", "html", "markdown"]
    else:
        formats = [args.format]

    # Generate reports
    generator = IntegrationTestReportGenerator(args.output_dir)

    generated_files = generator.generate_report(
        test_results,
        formats=formats,
        include_metrics=args.include_metrics,
        include_charts=args.include_charts,
    )

    print("Generated reports:")
    for format_type, file_path in generated_files.items():
        if isinstance(file_path, list):
            print(f"  {format_type}: {len(file_path)} files")
            for f in file_path:
                print(f"    - {f}")
        else:
            print(f"  {format_type}: {file_path}")


if __name__ == "__main__":
    main()
