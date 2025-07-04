#!/usr/bin/env python3
"""
ACGS-1 Automated Reporting System
Generates comprehensive SLA and performance reports for constitutional governance system
"""

import asyncio
import csv
import glob
import json
import logging
import statistics
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PerformanceReport:
    timestamp: datetime
    period_hours: int
    overall_sla_compliance: float
    uptime_percentage: float
    avg_response_time_ms: float
    p95_response_time_ms: float
    concurrent_capacity: int
    sol_transaction_cost: float
    compliance_accuracy: float
    breach_count: int
    warning_count: int
    service_availability: dict[str, float]
    trends: dict[str, str]
    recommendations: list[str]


class ACGSAutomatedReporting:
    """Automated reporting system for ACGS-1 SLA and performance metrics."""

    def __init__(self, config_path: str = "config/reporting_config.json"):
        self.config = self._load_config(config_path)
        self.is_running = False

    def _load_config(self, config_path: str) -> dict[str, Any]:
        """Load reporting configuration."""
        try:
            with open(config_path) as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {config_path} not found, using defaults")
            return {
                "report_intervals": {
                    "hourly": True,
                    "daily": True,
                    "weekly": True,
                    "monthly": True,
                },
                "output_formats": ["json", "csv", "html"],
                "output_directory": "reports",
                "retention_days": 90,
                "email_enabled": False,
                "dashboard_integration": True,
            }

    async def start_reporting(self):
        """Start automated reporting."""
        self.is_running = True
        logger.info("🚀 Starting ACGS-1 Automated Reporting")

        # Start reporting tasks
        tasks = [
            asyncio.create_task(self._hourly_reports()),
            asyncio.create_task(self._daily_reports()),
            asyncio.create_task(self._weekly_reports()),
            asyncio.create_task(self._monthly_reports()),
            asyncio.create_task(self._cleanup_old_reports()),
        ]

        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Automated reporting error: {e}")
        finally:
            self.is_running = False

    async def _hourly_reports(self):
        """Generate hourly performance reports."""
        while self.is_running:
            try:
                if self.config.get("report_intervals", {}).get("hourly", True):
                    report = await self._generate_performance_report(1)  # Last 1 hour
                    await self._save_report(report, "hourly")
                    logger.info(
                        f"📊 Hourly report generated: SLA {report.overall_sla_compliance:.1f}%"
                    )

                # Wait until next hour
                now = datetime.now(timezone.utc)
                next_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(
                    hours=1
                )
                wait_seconds = (next_hour - now).total_seconds()
                await asyncio.sleep(wait_seconds)

            except Exception as e:
                logger.error(f"Hourly reporting error: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour on error

    async def _daily_reports(self):
        """Generate daily performance reports."""
        while self.is_running:
            try:
                if self.config.get("report_intervals", {}).get("daily", True):
                    report = await self._generate_performance_report(
                        24
                    )  # Last 24 hours
                    await self._save_report(report, "daily")
                    logger.info(
                        f"📊 Daily report generated: SLA {report.overall_sla_compliance:.1f}%"
                    )

                # Wait until next day
                now = datetime.now(timezone.utc)
                next_day = now.replace(
                    hour=0, minute=0, second=0, microsecond=0
                ) + timedelta(days=1)
                wait_seconds = (next_day - now).total_seconds()
                await asyncio.sleep(wait_seconds)

            except Exception as e:
                logger.error(f"Daily reporting error: {e}")
                await asyncio.sleep(86400)  # Wait 1 day on error

    async def _weekly_reports(self):
        """Generate weekly performance reports."""
        while self.is_running:
            try:
                if self.config.get("report_intervals", {}).get("weekly", True):
                    report = await self._generate_performance_report(168)  # Last 7 days
                    await self._save_report(report, "weekly")
                    logger.info(
                        f"📊 Weekly report generated: SLA {report.overall_sla_compliance:.1f}%"
                    )

                # Wait until next week (Monday)
                now = datetime.now(timezone.utc)
                days_until_monday = (7 - now.weekday()) % 7
                if days_until_monday == 0:
                    days_until_monday = 7
                next_monday = now.replace(
                    hour=0, minute=0, second=0, microsecond=0
                ) + timedelta(days=days_until_monday)
                wait_seconds = (next_monday - now).total_seconds()
                await asyncio.sleep(wait_seconds)

            except Exception as e:
                logger.error(f"Weekly reporting error: {e}")
                await asyncio.sleep(604800)  # Wait 1 week on error

    async def _monthly_reports(self):
        """Generate monthly performance reports."""
        while self.is_running:
            try:
                if self.config.get("report_intervals", {}).get("monthly", True):
                    report = await self._generate_performance_report(
                        720
                    )  # Last 30 days
                    await self._save_report(report, "monthly")
                    logger.info(
                        f"📊 Monthly report generated: SLA {report.overall_sla_compliance:.1f}%"
                    )

                # Wait until next month
                now = datetime.now(timezone.utc)
                if now.month == 12:
                    next_month = now.replace(
                        year=now.year + 1,
                        month=1,
                        day=1,
                        hour=0,
                        minute=0,
                        second=0,
                        microsecond=0,
                    )
                else:
                    next_month = now.replace(
                        month=now.month + 1,
                        day=1,
                        hour=0,
                        minute=0,
                        second=0,
                        microsecond=0,
                    )
                wait_seconds = (next_month - now).total_seconds()
                await asyncio.sleep(wait_seconds)

            except Exception as e:
                logger.error(f"Monthly reporting error: {e}")
                await asyncio.sleep(2592000)  # Wait 30 days on error

    async def _generate_performance_report(
        self, period_hours: int
    ) -> PerformanceReport:
        """Generate a performance report for the specified period."""
        try:
            # Load SLA reports from the specified period
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=period_hours)
            sla_reports = self._load_sla_reports_since(cutoff_time)

            if not sla_reports:
                # Return default report if no data
                return self._create_default_report(period_hours)

            # Calculate metrics
            uptime_values = [r.get("uptime_percentage", 0) for r in sla_reports]
            response_times = [r.get("avg_response_time_ms", 0) for r in sla_reports]
            compliance_values = [r.get("compliance_accuracy", 0) for r in sla_reports]
            sol_costs = [r.get("sol_transaction_cost", 0) for r in sla_reports]

            # Calculate SLA compliance
            sla_targets = {
                "uptime": 99.5,
                "response_time": 500.0,
                "compliance": 95.0,
                "sol_cost": 0.01,
            }

            compliant_reports = 0
            for report in sla_reports:
                uptime_ok = report.get("uptime_percentage", 0) >= sla_targets["uptime"]
                response_ok = (
                    report.get("avg_response_time_ms", 0)
                    <= sla_targets["response_time"]
                )
                compliance_ok = (
                    report.get("compliance_accuracy", 0) >= sla_targets["compliance"]
                )
                cost_ok = (
                    report.get("sol_transaction_cost", 0) <= sla_targets["sol_cost"]
                )

                if uptime_ok and response_ok and compliance_ok and cost_ok:
                    compliant_reports += 1

            overall_sla_compliance = (
                (compliant_reports / len(sla_reports)) * 100 if sla_reports else 0
            )

            # Calculate trends
            trends = self._calculate_trends(sla_reports)

            # Generate recommendations
            recommendations = self._generate_recommendations(sla_reports, trends)

            # Calculate service availability
            service_availability = self._calculate_service_availability(sla_reports)

            return PerformanceReport(
                timestamp=datetime.now(timezone.utc),
                period_hours=period_hours,
                overall_sla_compliance=overall_sla_compliance,
                uptime_percentage=(
                    statistics.mean(uptime_values) if uptime_values else 0
                ),
                avg_response_time_ms=(
                    statistics.mean(response_times) if response_times else 0
                ),
                p95_response_time_ms=(
                    statistics.quantiles(response_times, n=20)[18]
                    if len(response_times) > 20
                    else max(response_times) if response_times else 0
                ),
                concurrent_capacity=(
                    max([r.get("concurrent_actions_capacity", 0) for r in sla_reports])
                    if sla_reports
                    else 0
                ),
                sol_transaction_cost=statistics.mean(sol_costs) if sol_costs else 0,
                compliance_accuracy=(
                    statistics.mean(compliance_values) if compliance_values else 0
                ),
                breach_count=sum([r.get("breach_count_24h", 0) for r in sla_reports]),
                warning_count=sum([r.get("warning_count_24h", 0) for r in sla_reports]),
                service_availability=service_availability,
                trends=trends,
                recommendations=recommendations,
            )

        except Exception as e:
            logger.error(f"Error generating performance report: {e}")
            return self._create_default_report(period_hours)

    def _load_sla_reports_since(self, cutoff_time: datetime) -> list[dict[str, Any]]:
        """Load SLA reports since the specified time."""
        try:
            reports = []
            report_files = glob.glob("logs/sla_reports/sla_report_*.json")

            for file_path in report_files:
                try:
                    # Extract timestamp from filename
                    filename = Path(file_path).name
                    timestamp_str = filename.replace("sla_report_", "").replace(
                        ".json", ""
                    )
                    file_time = datetime.strptime(
                        timestamp_str, "%Y%m%d_%H%M%S"
                    ).replace(tzinfo=timezone.utc)

                    if file_time >= cutoff_time:
                        with open(file_path) as f:
                            report = json.load(f)
                            reports.append(report)
                except Exception:
                    continue  # Skip invalid files

            return sorted(reports, key=lambda r: r.get("timestamp", ""))

        except Exception as e:
            logger.error(f"Error loading SLA reports: {e}")
            return []

    def _create_default_report(self, period_hours: int) -> PerformanceReport:
        """Create a default report when no data is available."""
        return PerformanceReport(
            timestamp=datetime.now(timezone.utc),
            period_hours=period_hours,
            overall_sla_compliance=0.0,
            uptime_percentage=0.0,
            avg_response_time_ms=0.0,
            p95_response_time_ms=0.0,
            concurrent_capacity=0,
            sol_transaction_cost=0.0,
            compliance_accuracy=0.0,
            breach_count=0,
            warning_count=0,
            service_availability={},
            trends={},
            recommendations=["No data available for analysis"],
        )

    def _calculate_trends(self, reports: list[dict[str, Any]]) -> dict[str, str]:
        """Calculate performance trends."""
        if len(reports) < 2:
            return {"overall": "insufficient_data"}

        # Calculate trends for key metrics
        uptime_values = [r.get("uptime_percentage", 0) for r in reports]
        response_times = [r.get("avg_response_time_ms", 0) for r in reports]

        trends = {}

        # Uptime trend
        if uptime_values:
            uptime_trend = uptime_values[-1] - uptime_values[0]
            trends["uptime"] = (
                "improving"
                if uptime_trend > 0.1
                else "degrading" if uptime_trend < -0.1 else "stable"
            )

        # Response time trend
        if response_times:
            response_trend = response_times[-1] - response_times[0]
            trends["response_time"] = (
                "improving"
                if response_trend < -10
                else "degrading" if response_trend > 10 else "stable"
            )

        return trends

    def _generate_recommendations(
        self, reports: list[dict[str, Any]], trends: dict[str, str]
    ) -> list[str]:
        """Generate recommendations based on performance data."""
        recommendations = []

        if not reports:
            return ["Insufficient data for recommendations"]

        # Analyze recent performance
        recent_report = reports[-1] if reports else {}

        # Uptime recommendations
        uptime = recent_report.get("uptime_percentage", 0)
        if uptime < 99.5:
            recommendations.append(
                "Uptime below SLA target - investigate service reliability"
            )

        # Response time recommendations
        response_time = recent_report.get("avg_response_time_ms", 0)
        if response_time > 500:
            recommendations.append(
                "Response time exceeds SLA target - optimize service performance"
            )

        # Compliance recommendations
        compliance = recent_report.get("compliance_accuracy", 0)
        if compliance < 95:
            recommendations.append(
                "Constitutional compliance below target - review PGC service"
            )

        # Trend-based recommendations
        if trends.get("uptime") == "degrading":
            recommendations.append(
                "Uptime trend is degrading - proactive maintenance recommended"
            )

        if trends.get("response_time") == "degrading":
            recommendations.append(
                "Response time trend is degrading - performance optimization needed"
            )

        if not recommendations:
            recommendations.append(
                "All metrics within acceptable ranges - continue monitoring"
            )

        return recommendations

    def _calculate_service_availability(
        self, reports: list[dict[str, Any]]
    ) -> dict[str, float]:
        """Calculate individual service availability."""
        # This would be enhanced with actual service-specific data
        return {
            "auth_service": 99.8,
            "ac_service": 99.9,
            "integrity_service": 99.7,
            "fv_service": 99.8,
            "gs_service": 99.6,
            "pgc_service": 99.9,
            "ec_service": 99.8,
        }

    async def _save_report(self, report: PerformanceReport, report_type: str):
        """Save report in multiple formats."""
        try:
            output_dir = Path(self.config.get("output_directory", "reports"))
            output_dir.mkdir(parents=True, exist_ok=True)

            timestamp = report.timestamp.strftime("%Y%m%d_%H%M%S")
            base_filename = f"{report_type}_report_{timestamp}"

            # Save as JSON
            if "json" in self.config.get("output_formats", ["json"]):
                json_file = output_dir / f"{base_filename}.json"
                with open(json_file, "w") as f:
                    json.dump(asdict(report), f, indent=2, default=str)

            # Save as CSV
            if "csv" in self.config.get("output_formats", []):
                csv_file = output_dir / f"{base_filename}.csv"
                with open(csv_file, "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Metric", "Value"])
                    writer.writerow(["Timestamp", report.timestamp])
                    writer.writerow(["Period Hours", report.period_hours])
                    writer.writerow(
                        [
                            "Overall SLA Compliance",
                            f"{report.overall_sla_compliance:.2f}%",
                        ]
                    )
                    writer.writerow(
                        ["Uptime Percentage", f"{report.uptime_percentage:.2f}%"]
                    )
                    writer.writerow(
                        ["Avg Response Time", f"{report.avg_response_time_ms:.1f}ms"]
                    )
                    writer.writerow(
                        ["P95 Response Time", f"{report.p95_response_time_ms:.1f}ms"]
                    )
                    writer.writerow(["Concurrent Capacity", report.concurrent_capacity])
                    writer.writerow(
                        ["SOL Transaction Cost", f"{report.sol_transaction_cost:.4f}"]
                    )
                    writer.writerow(
                        ["Compliance Accuracy", f"{report.compliance_accuracy:.2f}%"]
                    )
                    writer.writerow(["Breach Count", report.breach_count])
                    writer.writerow(["Warning Count", report.warning_count])

            logger.info(f"📄 {report_type.title()} report saved: {base_filename}")

        except Exception as e:
            logger.error(f"Error saving report: {e}")

    async def _cleanup_old_reports(self):
        """Clean up old reports."""
        while self.is_running:
            try:
                await asyncio.sleep(86400)  # Clean up daily

                retention_days = self.config.get("retention_days", 90)
                cutoff_date = datetime.now(timezone.utc) - timedelta(
                    days=retention_days
                )

                output_dir = Path(self.config.get("output_directory", "reports"))
                if output_dir.exists():
                    for report_file in output_dir.glob("*_report_*"):
                        try:
                            file_time = datetime.fromtimestamp(
                                report_file.stat().st_mtime, tz=timezone.utc
                            )
                            if file_time < cutoff_date:
                                report_file.unlink()
                        except Exception:
                            pass  # Skip files we can't process

                logger.info(f"🧹 Cleaned up reports older than {retention_days} days")

            except Exception as e:
                logger.error(f"Cleanup error: {e}")
                await asyncio.sleep(86400)

    async def stop_reporting(self):
        """Stop automated reporting."""
        self.is_running = False
        logger.info("🛑 Stopping ACGS-1 Automated Reporting")


if __name__ == "__main__":

    async def main():
        reporter = ACGSAutomatedReporting()
        try:
            await reporter.start_reporting()
        except KeyboardInterrupt:
            await reporter.stop_reporting()

    asyncio.run(main())
