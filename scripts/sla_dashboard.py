#!/usr/bin/env python3
"""
ACGS-1 SLA Dashboard
Real-time SLA monitoring dashboard for constitutional governance system
"""

import asyncio
import glob
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Add the monitoring directory to the path
sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "infrastructure", "monitoring")
)

try:
    from sla_monitor import ACGSSLAMonitor
except ImportError:
    print("❌ Could not import SLA monitoring service")
    print("Please ensure the sla_monitor.py is available")
    sys.exit(1)


class SLADashboard:
    """Real-time SLA dashboard for ACGS-1 system."""

    def __init__(self):
        self.monitor = ACGSSLAMonitor()
        self.refresh_interval = 10  # seconds

    def clear_screen(self):
        """Clear the terminal screen."""
        os.system("cls" if os.name == "nt" else "clear")

    def format_sla_status(self, status: str) -> str:
        """Format SLA status with colors."""
        status_map = {
            "compliant": "🟢 COMPLIANT",
            "warning": "🟡 WARNING",
            "breach": "🔴 BREACH",
            "unknown": "⚪ UNKNOWN",
        }
        return status_map.get(status.lower(), "❓ UNKNOWN")

    def format_percentage(self, value: float, target: float) -> str:
        """Format percentage with color coding."""
        if value >= target:
            return f"🟢 {value:.2f}%"
        elif value >= target * 0.98:  # Within 2% of target
            return f"🟡 {value:.2f}%"
        else:
            return f"🔴 {value:.2f}%"

    def format_response_time(self, value: float, target: float) -> str:
        """Format response time with color coding."""
        if value <= target:
            return f"🟢 {value:.1f}ms"
        elif value <= target * 1.2:  # Within 20% of target
            return f"🟡 {value:.1f}ms"
        else:
            return f"🔴 {value:.1f}ms"

    def format_sol_cost(self, value: float, target: float) -> str:
        """Format SOL cost with color coding."""
        if value <= target:
            return f"🟢 {value:.4f} SOL"
        elif value <= target * 1.2:
            return f"🟡 {value:.4f} SOL"
        else:
            return f"🔴 {value:.4f} SOL"

    def display_header(self):
        """Display dashboard header."""
        print("=" * 80)
        print("📊 ACGS-1 SLA MONITORING DASHBOARD")
        print("=" * 80)
        print(f"📅 {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(
            f"🔄 Auto-refresh every {self.refresh_interval} seconds (Press Ctrl+C to exit)"
        )
        print("=" * 80)

    def display_sla_overview(self, sla_status: dict[str, Any]):
        """Display SLA overview."""
        print("\n🎯 SLA OVERVIEW")
        print("-" * 50)

        overall_status = sla_status.get("overall_status", "unknown")
        print(f"Overall SLA Status: {self.format_sla_status(overall_status)}")

        breach_count = sla_status.get("breach_count_24h", 0)
        warning_count = sla_status.get("warning_count_24h", 0)

        print(f"24h Breaches:       🔴 {breach_count}")
        print(f"24h Warnings:       🟡 {warning_count}")

        if breach_count == 0 and warning_count == 0:
            print("✅ No SLA violations in the last 24 hours")
        elif breach_count > 0:
            print("⚠️  SLA breaches detected - immediate attention required")
        else:
            print("⚠️  SLA warnings detected - monitoring recommended")

    def display_sla_metrics(self, sla_status: dict[str, Any]):
        """Display detailed SLA metrics."""
        print("\n📈 SLA METRICS")
        print("-" * 50)

        metrics = sla_status.get("metrics", {})

        # Uptime
        uptime_metric = metrics.get("uptime_percentage", {})
        if uptime_metric:
            current = uptime_metric.get("current_value", 0)
            target = uptime_metric.get("target_value", 99.5)
            status = uptime_metric.get("status", "unknown")

            print(
                f"Uptime:             {self.format_percentage(current, target)} "
                f"(Target: {target}%) {self.format_sla_status(status)}"
            )

        # Response Time
        response_metric = metrics.get("response_time_ms", {})
        if response_metric:
            current = response_metric.get("current_value", 0)
            target = response_metric.get("target_value", 500)
            status = response_metric.get("status", "unknown")

            print(
                f"Response Time:      {self.format_response_time(current, target)} "
                f"(Target: {target}ms) {self.format_sla_status(status)}"
            )

        # Concurrent Actions
        capacity_metric = metrics.get("concurrent_actions", {})
        if capacity_metric:
            current = capacity_metric.get("current_value", 0)
            target = capacity_metric.get("target_value", 1000)
            status = capacity_metric.get("status", "unknown")

            capacity_color = (
                "🟢" if current >= target else "🟡" if current >= target * 0.8 else "🔴"
            )
            print(
                f"Concurrent Capacity: {capacity_color} {int(current)} actions "
                f"(Target: {int(target)}) {self.format_sla_status(status)}"
            )

        # SOL Transaction Cost
        cost_metric = metrics.get("sol_transaction_cost", {})
        if cost_metric:
            current = cost_metric.get("current_value", 0)
            target = cost_metric.get("target_value", 0.01)
            status = cost_metric.get("status", "unknown")

            print(
                f"SOL Cost:           {self.format_sol_cost(current, target)} "
                f"(Target: {target} SOL) {self.format_sla_status(status)}"
            )

        # Compliance Accuracy
        compliance_metric = metrics.get("compliance_accuracy", {})
        if compliance_metric:
            current = compliance_metric.get("current_value", 0)
            target = compliance_metric.get("target_value", 95)
            status = compliance_metric.get("status", "unknown")

            print(
                f"Compliance:         {self.format_percentage(current, target)} "
                f"(Target: {target}%) {self.format_sla_status(status)}"
            )

    def display_trends(self):
        """Display SLA trends."""
        print("\n📊 SLA TRENDS (Last 24 Hours)")
        print("-" * 50)

        try:
            # Load recent SLA reports
            report_files = sorted(glob.glob("logs/sla_reports/sla_report_*.json"))
            if len(report_files) < 2:
                print("Insufficient data for trend analysis")
                return

            # Analyze last 10 reports
            recent_files = report_files[-10:]
            uptime_values = []
            response_times = []
            breach_counts = []

            for file in recent_files:
                try:
                    with open(file) as f:
                        report = json.load(f)
                        uptime_values.append(report.get("uptime_percentage", 0))
                        response_times.append(report.get("avg_response_time_ms", 0))
                        breach_counts.append(report.get("breach_count_24h", 0))
                except Exception:
                    continue

            if uptime_values:
                uptime_trend = (
                    "📈"
                    if uptime_values[-1] > uptime_values[0]
                    else "📉" if uptime_values[-1] < uptime_values[0] else "➡️"
                )
                print(
                    f"Uptime Trend:       {uptime_trend} Avg: {sum(uptime_values)/len(uptime_values):.2f}% "
                    f"(Min: {min(uptime_values):.2f}%, Max: {max(uptime_values):.2f}%)"
                )

            if response_times:
                response_trend = (
                    "📉"
                    if response_times[-1] < response_times[0]
                    else "📈" if response_times[-1] > response_times[0] else "➡️"
                )
                print(
                    f"Response Trend:     {response_trend} Avg: {sum(response_times)/len(response_times):.1f}ms "
                    f"(Min: {min(response_times):.1f}ms, Max: {max(response_times):.1f}ms)"
                )

            if breach_counts:
                total_breaches = sum(breach_counts)
                breach_trend = "🔴" if total_breaches > 0 else "🟢"
                print(
                    f"Breach Trend:       {breach_trend} Total: {total_breaches} breaches in analyzed period"
                )

        except Exception as e:
            print(f"Error analyzing trends: {e}")

    def display_alerts(self):
        """Display recent alerts."""
        print("\n🚨 RECENT ALERTS")
        print("-" * 50)

        # This would integrate with actual alert system
        # For now, show placeholder
        print("No critical alerts in the last hour")
        print("Monitor logs for detailed alert information")

    def load_latest_sla_status(self) -> dict[str, Any]:
        """Load the latest SLA status."""
        try:
            latest_file = Path("logs/sla_reports/latest_sla_report.json")
            if latest_file.exists():
                with open(latest_file) as f:
                    return json.load(f)
            else:
                return {"error": "No SLA reports found"}
        except Exception as e:
            return {"error": f"Failed to load SLA status: {e}"}

    async def run_single_check(self):
        """Run a single SLA check and display results."""
        print("🔍 Loading SLA status...")

        # Load latest SLA status
        sla_status = self.load_latest_sla_status()

        if "error" in sla_status:
            print(f"❌ {sla_status['error']}")
            print("Please ensure the SLA monitor is running:")
            print("  ./scripts/start_sla_monitor.sh start")
            return

        # Display results
        self.clear_screen()
        self.display_header()
        self.display_sla_overview(sla_status)
        self.display_sla_metrics(sla_status)
        self.display_trends()
        self.display_alerts()

        timestamp = sla_status.get("timestamp", datetime.now(UTC).isoformat())
        print(f"\n🔄 Last updated: {timestamp}")

    async def run_dashboard(self):
        """Run the interactive dashboard."""
        try:
            while True:
                await self.run_single_check()
                await asyncio.sleep(self.refresh_interval)
        except KeyboardInterrupt:
            print("\n\n👋 SLA Dashboard stopped by user")
        except Exception as e:
            print(f"\n❌ Dashboard error: {e}")


async def main():
    """Main function."""
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        # Run single check
        dashboard = SLADashboard()
        await dashboard.run_single_check()
    else:
        # Run interactive dashboard
        dashboard = SLADashboard()
        print("🚀 Starting ACGS-1 SLA Dashboard...")
        print("Press Ctrl+C to exit")
        await dashboard.run_dashboard()


if __name__ == "__main__":
    asyncio.run(main())
