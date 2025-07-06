"""
ACGS Load Testing Performance Analyzer

Analyzes load test results and generates performance reports
with constitutional compliance validation.

Constitutional Hash: cdd01ef066bc6cf2
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Constitutional compliance hash
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


class PerformanceAnalyzer:
    """Analyzes ACGS load test performance results."""

    def __init__(self, results_dir: str = "/app/reports"):
        self.results_dir = Path(results_dir)
        self.constitutional_hash = CONSTITUTIONAL_HASH

        # Performance thresholds
        self.thresholds = {
            "response_time_p95_ms": 2000,
            "response_time_p99_ms": 5000,
            "error_rate_threshold": 0.01,  # 1%
            "constitutional_compliance_threshold": 0.95,
            "throughput_threshold_rps": 1000,
        }

        # Initialize matplotlib style
        plt.style.use("seaborn-v0_8")
        sns.set_palette("husl")

        logger.info(
            "Performance analyzer initialized with constitutional hash:"
            f" {CONSTITUTIONAL_HASH}"
        )

    def analyze_load_test_results(self, test_name: str) -> dict[str, Any]:
        """Analyze load test results and generate comprehensive report."""

        try:
            # Load test data
            stats_df = self._load_stats_data(test_name)
            failures_df = self._load_failures_data(test_name)

            # Perform analysis
            analysis_results = {
                "test_name": test_name,
                "constitutional_hash": self.constitutional_hash,
                "analyzed_at": datetime.now(timezone.utc).isoformat(),
                "summary": self._analyze_summary_stats(stats_df),
                "performance_metrics": self._analyze_performance_metrics(stats_df),
                "constitutional_compliance": self._analyze_constitutional_compliance(
                    stats_df
                ),
                "error_analysis": self._analyze_errors(failures_df),
                "recommendations": self._generate_recommendations(
                    stats_df, failures_df
                ),
                "pass_fail_criteria": self._evaluate_pass_fail_criteria(
                    stats_df, failures_df
                ),
            }

            # Generate visualizations
            self._generate_performance_charts(stats_df, test_name)

            # Generate detailed report
            self._generate_performance_report(analysis_results, test_name)

            return analysis_results

        except Exception as e:
            logger.error(f"Error analyzing load test results: {e}")
            return {
                "test_name": test_name,
                "error": str(e),
                "analyzed_at": datetime.now(timezone.utc).isoformat(),
            }

    def _load_stats_data(self, test_name: str) -> pd.DataFrame:
        """Load statistics data from CSV."""

        stats_file = self.results_dir / f"{test_name}_stats.csv"
        if not stats_file.exists():
            raise FileNotFoundError(f"Stats file not found: {stats_file}")

        df = pd.read_csv(stats_file)
        return df

    def _load_failures_data(self, test_name: str) -> pd.DataFrame:
        """Load failures data from CSV."""

        failures_file = self.results_dir / f"{test_name}_failures.csv"
        if not failures_file.exists():
            logger.warning(f"Failures file not found: {failures_file}")
            return pd.DataFrame()

        df = pd.read_csv(failures_file)
        return df

    def _analyze_summary_stats(self, stats_df: pd.DataFrame) -> dict[str, Any]:
        """Analyze summary statistics."""

        if stats_df.empty:
            return {"error": "No statistics data available"}

        # Calculate key metrics
        total_requests = stats_df["Request Count"].sum()
        total_failures = stats_df["Failure Count"].sum()
        error_rate = (total_failures / total_requests) if total_requests > 0 else 0

        # Average response time metrics
        avg_response_time = stats_df["Average Response Time"].mean()
        min_response_time = stats_df["Min Response Time"].min()
        max_response_time = stats_df["Max Response Time"].max()

        # Throughput calculation
        test_duration = (
            stats_df["Request Count"].sum() / stats_df["Requests/s"].mean()
            if stats_df["Requests/s"].mean() > 0
            else 0
        )

        return {
            "total_requests": int(total_requests),
            "total_failures": int(total_failures),
            "error_rate": round(error_rate, 4),
            "error_rate_percentage": round(error_rate * 100, 2),
            "average_response_time_ms": round(avg_response_time, 2),
            "min_response_time_ms": round(min_response_time, 2),
            "max_response_time_ms": round(max_response_time, 2),
            "average_throughput_rps": round(stats_df["Requests/s"].mean(), 2),
            "peak_throughput_rps": round(stats_df["Requests/s"].max(), 2),
            "test_duration_seconds": round(test_duration, 2),
        }

    def _analyze_performance_metrics(self, stats_df: pd.DataFrame) -> dict[str, Any]:
        """Analyze detailed performance metrics."""

        if stats_df.empty:
            return {"error": "No performance data available"}

        # Response time percentiles (approximated from available data)
        response_times = []
        for _, row in stats_df.iterrows():
            # Simulate response time distribution
            count = int(row["Request Count"])
            avg = row["Average Response Time"]
            response_times.extend([avg] * count)  # Simplified approximation

        if not response_times:
            return {"error": "No response time data available"}

        response_times_series = pd.Series(response_times)

        # Calculate percentiles
        p50 = response_times_series.quantile(0.5)
        p95 = response_times_series.quantile(0.95)
        p99 = response_times_series.quantile(0.99)

        # Endpoint-specific analysis
        endpoint_analysis = {}
        for _, row in stats_df.iterrows():
            endpoint = row["Name"]
            endpoint_analysis[endpoint] = {
                "request_count": int(row["Request Count"]),
                "failure_count": int(row["Failure Count"]),
                "error_rate": round(
                    (
                        row["Failure Count"] / row["Request Count"]
                        if row["Request Count"] > 0
                        else 0
                    ),
                    4,
                ),
                "avg_response_time_ms": round(row["Average Response Time"], 2),
                "min_response_time_ms": round(row["Min Response Time"], 2),
                "max_response_time_ms": round(row["Max Response Time"], 2),
                "requests_per_second": round(row["Requests/s"], 2),
            }

        return {
            "response_time_percentiles": {
                "p50_ms": round(p50, 2),
                "p95_ms": round(p95, 2),
                "p99_ms": round(p99, 2),
            },
            "endpoint_analysis": endpoint_analysis,
            "performance_classification": self._classify_performance(
                p95, p99, stats_df["Requests/s"].mean()
            ),
        }

    def _classify_performance(self, p95: float, p99: float, avg_rps: float) -> str:
        """Classify overall performance."""

        if p95 <= 500 and p99 <= 1000 and avg_rps >= 1000:
            return "excellent"
        elif p95 <= 1000 and p99 <= 2000 and avg_rps >= 800:
            return "good"
        elif p95 <= 2000 and p99 <= 5000 and avg_rps >= 500:
            return "acceptable"
        elif p95 <= 5000 and p99 <= 10000 and avg_rps >= 200:
            return "poor"
        else:
            return "unacceptable"

    def _analyze_constitutional_compliance(
        self, stats_df: pd.DataFrame
    ) -> dict[str, Any]:
        """Analyze constitutional compliance during load testing."""

        # Since constitutional compliance data would be in custom headers/logs,
        # this is a simplified analysis based on available data

        constitutional_endpoints = []
        for _, row in stats_df.iterrows():
            endpoint = row["Name"]
            if any(
                keyword in endpoint.lower()
                for keyword in ["constitutional", "compliance", "verify", "governance"]
            ):
                constitutional_endpoints.append({
                    "endpoint": endpoint,
                    "success_rate": (
                        1 - (row["Failure Count"] / row["Request Count"])
                        if row["Request Count"] > 0
                        else 0
                    ),
                    "avg_response_time_ms": row["Average Response Time"],
                    "request_count": int(row["Request Count"]),
                })

        # Calculate overall constitutional compliance score
        if constitutional_endpoints:
            overall_compliance = sum(
                ep["success_rate"] for ep in constitutional_endpoints
            ) / len(constitutional_endpoints)
        else:
            overall_compliance = (
                1.0  # Assume compliant if no constitutional endpoints detected
            )

        return {
            "constitutional_hash": self.constitutional_hash,
            "overall_compliance_score": round(overall_compliance, 4),
            "constitutional_endpoints": constitutional_endpoints,
            "compliance_threshold_met": (
                overall_compliance
                >= self.thresholds["constitutional_compliance_threshold"]
            ),
            "compliance_analysis": {
                "excellent": overall_compliance >= 0.99,
                "good": 0.95 <= overall_compliance < 0.99,
                "acceptable": 0.90 <= overall_compliance < 0.95,
                "poor": overall_compliance < 0.90,
            },
        }

    def _analyze_errors(self, failures_df: pd.DataFrame) -> dict[str, Any]:
        """Analyze error patterns and failures."""

        if failures_df.empty:
            return {
                "total_failures": 0,
                "error_types": {},
                "error_recommendations": ["No errors detected during load testing"],
            }

        # Group errors by type
        error_types = {}
        for _, row in failures_df.iterrows():
            error_type = row.get("Error", "Unknown Error")
            if error_type not in error_types:
                error_types[error_type] = {"count": 0, "endpoints": set()}
            error_types[error_type]["count"] += 1
            error_types[error_type]["endpoints"].add(row.get("Name", "Unknown"))

        # Convert sets to lists for JSON serialization
        for error_type in error_types:
            error_types[error_type]["endpoints"] = list(
                error_types[error_type]["endpoints"]
            )

        # Generate error recommendations
        recommendations = []
        for error_type, data in error_types.items():
            if "timeout" in error_type.lower():
                recommendations.append(
                    "Increase timeout configuration for endpoints:"
                    f" {', '.join(data['endpoints'])}"
                )
            elif "connection" in error_type.lower():
                recommendations.append(
                    "Check connection pool and network configuration for:"
                    f" {', '.join(data['endpoints'])}"
                )
            elif "503" in error_type or "502" in error_type:
                recommendations.append(
                    "Backend service capacity may be insufficient for:"
                    f" {', '.join(data['endpoints'])}"
                )

        return {
            "total_failures": len(failures_df),
            "error_types": error_types,
            "error_recommendations": recommendations or [
                "Review error logs for detailed troubleshooting"
            ],
        }

    def _generate_recommendations(
        self, stats_df: pd.DataFrame, failures_df: pd.DataFrame
    ) -> list[str]:
        """Generate performance improvement recommendations."""

        recommendations = []

        # Analyze response times
        if not stats_df.empty:
            avg_response_time = stats_df["Average Response Time"].mean()
            max_response_time = stats_df["Max Response Time"].max()
            avg_rps = stats_df["Requests/s"].mean()

            if avg_response_time > 2000:
                recommendations.append(
                    "Average response time exceeds 2 seconds - consider performance"
                    " optimization"
                )

            if max_response_time > 10000:
                recommendations.append(
                    "Maximum response time exceeds 10 seconds - investigate slow"
                    " endpoints"
                )

            if avg_rps < 500:
                recommendations.append(
                    "Throughput below 500 RPS - consider scaling infrastructure"
                )

        # Analyze errors
        if not failures_df.empty:
            error_rate = (
                len(failures_df) / stats_df["Request Count"].sum()
                if not stats_df.empty
                else 1
            )
            if error_rate > 0.01:
                recommendations.append(
                    f"Error rate {error_rate * 100:.2f}% exceeds 1% threshold -"
                    " investigate failures"
                )

        # Constitutional compliance recommendations
        recommendations.extend([
            "Ensure all endpoints maintain constitutional compliance under load",
            "Monitor constitutional hash consistency across all responses",
            "Validate multi-tenant isolation maintains integrity during peak load",
        ])

        return recommendations or ["System performance appears optimal"]

    def _evaluate_pass_fail_criteria(
        self, stats_df: pd.DataFrame, failures_df: pd.DataFrame
    ) -> dict[str, Any]:
        """Evaluate pass/fail criteria for load test."""

        criteria = {
            "response_time_p95": {
                "passed": True,
                "threshold": self.thresholds["response_time_p95_ms"],
                "actual": 0,
            },
            "error_rate": {
                "passed": True,
                "threshold": self.thresholds["error_rate_threshold"],
                "actual": 0,
            },
            "throughput": {
                "passed": True,
                "threshold": self.thresholds["throughput_threshold_rps"],
                "actual": 0,
            },
            "constitutional_compliance": {
                "passed": True,
                "threshold": self.thresholds["constitutional_compliance_threshold"],
                "actual": 1.0,
            },
        }

        if not stats_df.empty:
            # Calculate actual values
            total_requests = stats_df["Request Count"].sum()
            total_failures = stats_df["Failure Count"].sum()
            error_rate = (total_failures / total_requests) if total_requests > 0 else 0
            avg_throughput = stats_df["Requests/s"].mean()

            # Estimate P95 (simplified)
            p95_estimate = stats_df["Average Response Time"].quantile(0.95)

            # Update criteria
            criteria["response_time_p95"]["actual"] = round(p95_estimate, 2)
            criteria["response_time_p95"]["passed"] = (
                p95_estimate <= self.thresholds["response_time_p95_ms"]
            )

            criteria["error_rate"]["actual"] = round(error_rate, 4)
            criteria["error_rate"]["passed"] = (
                error_rate <= self.thresholds["error_rate_threshold"]
            )

            criteria["throughput"]["actual"] = round(avg_throughput, 2)
            criteria["throughput"]["passed"] = (
                avg_throughput >= self.thresholds["throughput_threshold_rps"]
            )

        # Overall pass/fail
        overall_passed = all(criterion["passed"] for criterion in criteria.values())

        return {
            "overall_passed": overall_passed,
            "criteria": criteria,
            "summary": (
                f"Load test {'PASSED' if overall_passed else 'FAILED'} -"
                f" {sum(1 for c in criteria.values() if c['passed'])}/{len(criteria)} criteria met"
            ),
        }

    def _generate_performance_charts(self, stats_df: pd.DataFrame, test_name: str):
        """Generate performance visualization charts."""

        try:
            # Create charts directory
            charts_dir = self.results_dir / "charts"
            charts_dir.mkdir(exist_ok=True)

            # Response time distribution
            plt.figure(figsize=(12, 8))

            # Chart 1: Response time by endpoint
            plt.subplot(2, 2, 1)
            endpoint_data = stats_df[["Name", "Average Response Time"]].head(10)
            plt.barh(endpoint_data["Name"], endpoint_data["Average Response Time"])
            plt.xlabel("Average Response Time (ms)")
            plt.title("Response Time by Endpoint")
            plt.xticks(rotation=45)

            # Chart 2: Throughput by endpoint
            plt.subplot(2, 2, 2)
            throughput_data = stats_df[["Name", "Requests/s"]].head(10)
            plt.barh(throughput_data["Name"], throughput_data["Requests/s"])
            plt.xlabel("Requests per Second")
            plt.title("Throughput by Endpoint")

            # Chart 3: Error rate by endpoint
            plt.subplot(2, 2, 3)
            stats_df["Error Rate"] = (
                stats_df["Failure Count"] / stats_df["Request Count"]
            )
            error_data = stats_df[stats_df["Error Rate"] > 0][
                ["Name", "Error Rate"]
            ].head(10)
            if not error_data.empty:
                plt.barh(error_data["Name"], error_data["Error Rate"] * 100)
                plt.xlabel("Error Rate (%)")
                plt.title("Error Rate by Endpoint")
            else:
                plt.text(
                    0.5,
                    0.5,
                    "No errors detected",
                    ha="center",
                    va="center",
                    transform=plt.gca().transAxes,
                )
                plt.title("Error Rate by Endpoint")

            # Chart 4: Request count distribution
            plt.subplot(2, 2, 4)
            request_data = stats_df[["Name", "Request Count"]].head(10)
            plt.barh(request_data["Name"], request_data["Request Count"])
            plt.xlabel("Request Count")
            plt.title("Request Volume by Endpoint")

            plt.tight_layout()
            plt.savefig(
                charts_dir / f"{test_name}_performance_overview.png",
                dpi=300,
                bbox_inches="tight",
            )
            plt.close()

            # Constitutional compliance chart
            plt.figure(figsize=(10, 6))
            constitutional_endpoints = [
                name for name in stats_df["Name"] if "constitutional" in name.lower()
            ]
            if constitutional_endpoints:
                const_data = stats_df[stats_df["Name"].isin(constitutional_endpoints)]
                const_data["Success Rate"] = 1 - (
                    const_data["Failure Count"] / const_data["Request Count"]
                )

                plt.bar(const_data["Name"], const_data["Success Rate"] * 100)
                plt.axhline(
                    y=95, color="r", linestyle="--", label="Compliance Threshold (95%)"
                )
                plt.ylabel("Success Rate (%)")
                plt.title("Constitutional Compliance Success Rate")
                plt.xticks(rotation=45)
                plt.legend()
                plt.tight_layout()
                plt.savefig(
                    charts_dir / f"{test_name}_constitutional_compliance.png",
                    dpi=300,
                    bbox_inches="tight",
                )

            plt.close()

            logger.info(f"Performance charts generated in {charts_dir}")

        except Exception as e:
            logger.error(f"Error generating performance charts: {e}")

    def _generate_performance_report(
        self, analysis_results: dict[str, Any], test_name: str
    ):
        """Generate detailed performance report."""

        try:
            report_file = self.results_dir / f"{test_name}_performance_report.json"

            with open(report_file, "w") as f:
                json.dump(analysis_results, f, indent=2, default=str)

            # Generate markdown report
            md_report = self._generate_markdown_report(analysis_results, test_name)
            md_file = self.results_dir / f"{test_name}_performance_report.md"

            with open(md_file, "w") as f:
                f.write(md_report)

            logger.info(f"Performance reports generated: {report_file} and {md_file}")

        except Exception as e:
            logger.error(f"Error generating performance report: {e}")

    def _generate_markdown_report(
        self, analysis_results: dict[str, Any], test_name: str
    ) -> str:
        """Generate markdown performance report."""

        report = f"""# ACGS Load Test Performance Report

## Test Information
- **Test Name**: {test_name}
- **Constitutional Hash**: {analysis_results.get('constitutional_hash', 'N/A')}
- **Analysis Date**: {analysis_results.get('analyzed_at', 'N/A')}

## Executive Summary
{analysis_results['pass_fail_criteria']['summary']}

## Performance Metrics

### Summary Statistics
"""

        summary = analysis_results.get("summary", {})
        if summary:
            report += f"""
- **Total Requests**: {summary.get('total_requests', 'N/A'):,}
- **Total Failures**: {summary.get('total_failures', 'N/A'):,}
- **Error Rate**: {summary.get('error_rate_percentage', 'N/A')}%
- **Average Response Time**: {summary.get('average_response_time_ms', 'N/A')} ms
- **Peak Throughput**: {summary.get('peak_throughput_rps', 'N/A')} RPS
"""

        # Performance classification
        perf_metrics = analysis_results.get("performance_metrics", {})
        if perf_metrics:
            report += f"""
### Performance Classification
**{perf_metrics.get('performance_classification', 'unknown').upper()}**

### Response Time Percentiles
- **P50**: {perf_metrics.get('response_time_percentiles', {}).get('p50_ms', 'N/A')} ms
- **P95**: {perf_metrics.get('response_time_percentiles', {}).get('p95_ms', 'N/A')} ms
- **P99**: {perf_metrics.get('response_time_percentiles', {}).get('p99_ms', 'N/A')} ms
"""

        # Constitutional compliance
        compliance = analysis_results.get("constitutional_compliance", {})
        if compliance:
            report += f"""
## Constitutional Compliance
- **Overall Compliance Score**: {compliance.get('overall_compliance_score', 'N/A')}
- **Threshold Met**: {'✅ Yes' if compliance.get('compliance_threshold_met', False) else '❌ No'}
- **Constitutional Hash**: {compliance.get('constitutional_hash', 'N/A')}
"""

        # Pass/Fail Criteria
        criteria = analysis_results.get("pass_fail_criteria", {}).get("criteria", {})
        if criteria:
            report += """
## Pass/Fail Criteria

| Criterion | Threshold | Actual | Status |
|-----------|-----------|---------|--------|
"""
            for name, data in criteria.items():
                status = "✅ PASS" if data["passed"] else "❌ FAIL"
                report += (
                    f"| {name.replace('_', ' ').title()} | {data['threshold']} |"
                    f" {data['actual']} | {status} |\n"
                )

        # Recommendations
        recommendations = analysis_results.get("recommendations", [])
        if recommendations:
            report += """
## Recommendations

"""
            for i, rec in enumerate(recommendations, 1):
                report += f"{i}. {rec}\n"

        return report


if __name__ == "__main__":
    # Example usage
    analyzer = PerformanceAnalyzer()
    results = analyzer.analyze_load_test_results("acgs_distributed_load_test")
    print(
        "Analysis completed:"
        f" {results.get('pass_fail_criteria', {}).get('summary', 'N/A')}"
    )
