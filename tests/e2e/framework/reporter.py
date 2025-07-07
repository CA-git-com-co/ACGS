"""
ACGS E2E Test Reporter

Provides comprehensive test reporting capabilities including performance
metrics, constitutional compliance tracking, and regression detection.
"""

# Constitutional Hash: cdd01ef066bc6cf2

import json
import statistics
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .base import E2ETestResult, PerformanceMetrics
from .config import E2ETestConfig


@dataclass
class PerformanceBaseline:
    """Performance baseline for regression detection."""

    test_name: str
    p99_latency_ms: float
    throughput_rps: float
    success_rate: float
    cache_hit_rate: Optional[float] = None
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()


@dataclass
class RegressionAlert:
    """Performance regression alert."""

    test_name: str
    metric_name: str
    baseline_value: float
    current_value: float
    regression_percentage: float
    severity: str  # "warning", "critical"
    threshold_exceeded: bool


class E2ETestReporter:
    """
    Comprehensive test reporter for ACGS E2E tests.

    Provides:
    - Performance metrics analysis
    - Constitutional compliance tracking
    - Regression detection
    - Multi-format reporting (JSON, HTML, XML)
    - Trend analysis
    """

    def __init__(self, config: E2ETestConfig):
        self.config = config
        self.baselines: Dict[str, PerformanceBaseline] = {}
        self.regression_alerts: List[RegressionAlert] = []

        # Load existing baselines
        self._load_baselines()

    def _load_baselines(self):
        """Load performance baselines from file."""
        baseline_file = self.config.report_directory / "performance_baselines.json"

        if baseline_file.exists():
            try:
                with open(baseline_file, "r") as f:
                    data = json.load(f)

                for test_name, baseline_data in data.items():
                    self.baselines[test_name] = PerformanceBaseline(**baseline_data)

            except Exception as e:
                print(f"Warning: Failed to load baselines: {e}")

    def _save_baselines(self):
        """Save performance baselines to file."""
        baseline_file = self.config.report_directory / "performance_baselines.json"
        baseline_file.parent.mkdir(parents=True, exist_ok=True)

        data = {
            test_name: asdict(baseline)
            for test_name, baseline in self.baselines.items()
        }

        with open(baseline_file, "w") as f:
            json.dump(data, f, indent=2)

    def update_baseline(self, test_name: str, metrics: PerformanceMetrics):
        """Update performance baseline for a test."""
        baseline = PerformanceBaseline(
            test_name=test_name,
            p99_latency_ms=metrics.latency_p99_ms,
            throughput_rps=metrics.throughput_rps,
            success_rate=metrics.success_rate,
            cache_hit_rate=metrics.cache_hit_rate,
        )

        self.baselines[test_name] = baseline
        self._save_baselines()

    def detect_regressions(self, results: List[E2ETestResult]) -> List[RegressionAlert]:
        """Detect performance regressions against baselines."""
        alerts = []

        for result in results:
            if not result.performance_metrics:
                continue

            baseline = self.baselines.get(result.test_name)
            if not baseline:
                continue

            metrics = result.performance_metrics

            # Check P99 latency regression
            if "latency_p99_ms" in metrics:
                current_latency = metrics["latency_p99_ms"]
                regression_pct = (
                    (current_latency - baseline.p99_latency_ms)
                    / baseline.p99_latency_ms
                ) * 100

                if regression_pct > 20:  # 20% regression threshold
                    alerts.append(
                        RegressionAlert(
                            test_name=result.test_name,
                            metric_name="p99_latency_ms",
                            baseline_value=baseline.p99_latency_ms,
                            current_value=current_latency,
                            regression_percentage=regression_pct,
                            severity="critical" if regression_pct > 50 else "warning",
                            threshold_exceeded=current_latency
                            > self.config.performance.p99_latency_ms,
                        )
                    )

            # Check throughput regression
            if "throughput_rps" in metrics:
                current_throughput = metrics["throughput_rps"]
                regression_pct = (
                    (baseline.throughput_rps - current_throughput)
                    / baseline.throughput_rps
                ) * 100

                if regression_pct > 15:  # 15% throughput drop threshold
                    alerts.append(
                        RegressionAlert(
                            test_name=result.test_name,
                            metric_name="throughput_rps",
                            baseline_value=baseline.throughput_rps,
                            current_value=current_throughput,
                            regression_percentage=regression_pct,
                            severity="critical" if regression_pct > 30 else "warning",
                            threshold_exceeded=current_throughput
                            < self.config.performance.throughput_rps,
                        )
                    )

            # Check success rate regression
            if "success_rate" in metrics:
                current_success_rate = metrics["success_rate"]
                regression_pct = (
                    (baseline.success_rate - current_success_rate)
                    / baseline.success_rate
                ) * 100

                if regression_pct > 5:  # 5% success rate drop threshold
                    alerts.append(
                        RegressionAlert(
                            test_name=result.test_name,
                            metric_name="success_rate",
                            baseline_value=baseline.success_rate,
                            current_value=current_success_rate,
                            regression_percentage=regression_pct,
                            severity="critical",
                            threshold_exceeded=current_success_rate
                            < self.config.performance.success_rate,
                        )
                    )

        self.regression_alerts = alerts
        return alerts

    def generate_performance_report(
        self, results: List[E2ETestResult]
    ) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        performance_results = [r for r in results if r.performance_metrics]

        if not performance_results:
            return {"error": "No performance metrics available"}

        # Calculate aggregate metrics
        all_latencies = []
        all_throughputs = []
        all_success_rates = []
        all_cache_hit_rates = []

        for result in performance_results:
            metrics = result.performance_metrics

            if "latency_p99_ms" in metrics:
                all_latencies.append(metrics["latency_p99_ms"])

            if "throughput_rps" in metrics:
                all_throughputs.append(metrics["throughput_rps"])

            if "success_rate" in metrics:
                all_success_rates.append(metrics["success_rate"])

            if "cache_hit_rate" in metrics and metrics["cache_hit_rate"] is not None:
                all_cache_hit_rates.append(metrics["cache_hit_rate"])

        # Calculate statistics
        report = {
            "summary": {
                "total_performance_tests": len(performance_results),
                "timestamp": datetime.utcnow().isoformat(),
                "constitutional_hash": self.config.constitutional_hash,
            },
            "latency_analysis": (
                self._calculate_stats(all_latencies, "ms") if all_latencies else None
            ),
            "throughput_analysis": (
                self._calculate_stats(all_throughputs, "RPS")
                if all_throughputs
                else None
            ),
            "success_rate_analysis": (
                self._calculate_stats(all_success_rates, "%")
                if all_success_rates
                else None
            ),
            "cache_hit_rate_analysis": (
                self._calculate_stats(all_cache_hit_rates, "%")
                if all_cache_hit_rates
                else None
            ),
            "target_compliance": {
                "p99_latency_target_ms": self.config.performance.p99_latency_ms,
                "throughput_target_rps": self.config.performance.throughput_rps,
                "success_rate_target": self.config.performance.success_rate,
                "cache_hit_rate_target": self.config.performance.cache_hit_rate,
                "tests_meeting_latency_target": sum(
                    1
                    for l in all_latencies
                    if l <= self.config.performance.p99_latency_ms
                ),
                "tests_meeting_throughput_target": sum(
                    1
                    for t in all_throughputs
                    if t >= self.config.performance.throughput_rps
                ),
                "tests_meeting_success_rate_target": sum(
                    1
                    for s in all_success_rates
                    if s >= self.config.performance.success_rate
                ),
                "tests_meeting_cache_hit_rate_target": sum(
                    1
                    for c in all_cache_hit_rates
                    if c >= self.config.performance.cache_hit_rate
                ),
            },
            "regression_alerts": [asdict(alert) for alert in self.regression_alerts],
            "individual_test_results": [
                {
                    "test_name": result.test_name,
                    "success": result.success,
                    "duration_ms": result.duration_ms,
                    "performance_metrics": result.performance_metrics,
                }
                for result in performance_results
            ],
        }

        return report

    def _calculate_stats(self, values: List[float], unit: str) -> Dict[str, Any]:
        """Calculate statistical summary for a list of values."""
        if not values:
            return {}

        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
            "unit": unit,
        }

    def generate_constitutional_compliance_report(
        self, results: List[E2ETestResult]
    ) -> Dict[str, Any]:
        """Generate constitutional compliance report."""
        constitutional_results = [
            r for r in results if r.constitutional_compliance is not None
        ]

        if not constitutional_results:
            return {"error": "No constitutional compliance data available"}

        compliant_tests = [
            r for r in constitutional_results if r.constitutional_compliance
        ]
        non_compliant_tests = [
            r for r in constitutional_results if not r.constitutional_compliance
        ]

        compliance_rate = len(compliant_tests) / len(constitutional_results)

        report = {
            "summary": {
                "total_tests_with_compliance_data": len(constitutional_results),
                "compliant_tests": len(compliant_tests),
                "non_compliant_tests": len(non_compliant_tests),
                "compliance_rate": compliance_rate,
                "constitutional_hash": self.config.constitutional_hash,
                "timestamp": datetime.utcnow().isoformat(),
            },
            "compliance_status": "PASS" if compliance_rate >= 0.95 else "FAIL",
            "target_compliance_rate": 0.95,
            "compliant_test_names": [r.test_name for r in compliant_tests],
            "non_compliant_test_names": [r.test_name for r in non_compliant_tests],
            "recommendations": self._generate_compliance_recommendations(
                non_compliant_tests
            ),
        }

        return report

    def _generate_compliance_recommendations(
        self, non_compliant_tests: List[E2ETestResult]
    ) -> List[str]:
        """Generate recommendations for improving constitutional compliance."""
        recommendations = []

        if non_compliant_tests:
            recommendations.append(
                f"Review {len(non_compliant_tests)} non-compliant tests for constitutional violations"
            )
            recommendations.append(
                "Verify constitutional hash consistency across all services"
            )
            recommendations.append(
                "Check policy validation logic in Constitutional AI service"
            )
            recommendations.append(
                "Ensure all governance decisions follow constitutional principles"
            )

        return recommendations

    def generate_comprehensive_report(
        self, results: List[E2ETestResult]
    ) -> Dict[str, Any]:
        """Generate comprehensive test report with all metrics."""
        # Detect regressions
        self.detect_regressions(results)

        # Generate individual reports
        performance_report = self.generate_performance_report(results)
        compliance_report = self.generate_constitutional_compliance_report(results)

        # Calculate overall summary
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.success)
        failed_tests = total_tests - passed_tests

        total_duration = sum(r.duration_ms for r in results)
        avg_duration = total_duration / total_tests if total_tests > 0 else 0

        comprehensive_report = {
            "report_metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "framework_version": "1.0.0",
                "test_mode": self.config.test_mode,
                "constitutional_hash": self.config.constitutional_hash,
                "total_execution_time_ms": total_duration,
            },
            "executive_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": passed_tests / total_tests if total_tests > 0 else 0,
                "average_test_duration_ms": avg_duration,
                "regression_alerts_count": len(self.regression_alerts),
                "critical_regressions": len(
                    [a for a in self.regression_alerts if a.severity == "critical"]
                ),
                "overall_status": (
                    "PASS"
                    if failed_tests == 0
                    and len(
                        [a for a in self.regression_alerts if a.severity == "critical"]
                    )
                    == 0
                    else "FAIL"
                ),
            },
            "performance_analysis": performance_report,
            "constitutional_compliance": compliance_report,
            "regression_analysis": {
                "alerts": [asdict(alert) for alert in self.regression_alerts],
                "baseline_count": len(self.baselines),
                "tests_with_baselines": list(self.baselines.keys()),
            },
            "test_results": [
                {
                    "test_name": r.test_name,
                    "success": r.success,
                    "duration_ms": r.duration_ms,
                    "error_message": r.error_message,
                    "constitutional_compliance": r.constitutional_compliance,
                    "performance_metrics": r.performance_metrics,
                }
                for r in results
            ],
        }

        return comprehensive_report

    def export_report(
        self, report: Dict[str, Any], output_path: Path, format_type: str = "json"
    ):
        """Export report to file in specified format."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if format_type.lower() == "json":
            with open(output_path, "w") as f:
                json.dump(report, f, indent=2, default=str)

        elif format_type.lower() == "yaml":
            import yaml

            with open(output_path, "w") as f:
                yaml.dump(report, f, default_flow_style=False)

        else:
            raise ValueError(f"Unsupported format: {format_type}")

    def should_block_deployment(self, results: List[E2ETestResult]) -> bool:
        """Determine if deployment should be blocked based on test results."""
        # Check for test failures
        failed_tests = [r for r in results if not r.success]
        if failed_tests:
            return True

        # Check for critical regressions
        critical_regressions = [
            a for a in self.regression_alerts if a.severity == "critical"
        ]
        if critical_regressions:
            return True

        # Check constitutional compliance
        compliance_report = self.generate_constitutional_compliance_report(results)
        if compliance_report.get("compliance_status") == "FAIL":
            return True

        # Check performance targets
        performance_report = self.generate_performance_report(results)
        if "target_compliance" in performance_report:
            targets = performance_report["target_compliance"]

            # Check if critical performance targets are met
            if (
                targets.get("tests_meeting_latency_target", 0) < len(results) * 0.8
            ):  # 80% of tests must meet latency target
                return True

        return False
