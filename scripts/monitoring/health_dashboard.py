#!/usr/bin/env python3
"""
ACGS-1 Health Dashboard
Real-time health monitoring dashboard for constitutional governance system
"""

import asyncio
import os
import sys
from datetime import datetime, timezone
from typing import Any

import aiohttp

# Add the monitoring directory to the path
sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "infrastructure", "monitoring")
)

try:
    from health_check_service import ACGSHealthMonitor, HealthStatus
except ImportError:
    print("❌ Could not import health monitoring service")
    print("Please ensure the health_check_service.py is available")
    sys.exit(1)


class HealthDashboard:
    """Real-time health dashboard for ACGS-1 system."""

    def __init__(self):
        self.monitor = ACGSHealthMonitor()
        self.refresh_interval = 5  # seconds

    def clear_screen(self):
        """Clear the terminal screen."""
        os.system("cls" if os.name == "nt" else "clear")

    def format_status(self, status: HealthStatus) -> str:
        """Format health status with colors."""
        status_map = {
            HealthStatus.HEALTHY: "🟢 HEALTHY",
            HealthStatus.DEGRADED: "🟡 DEGRADED",
            HealthStatus.UNHEALTHY: "🔴 UNHEALTHY",
            HealthStatus.UNKNOWN: "⚪ UNKNOWN",
        }
        return status_map.get(status, "❓ UNKNOWN")

    def format_response_time(self, response_time_ms: float) -> str:
        """Format response time with color coding."""
        if response_time_ms < 100:
            return f"🟢 {response_time_ms:.1f}ms"
        if response_time_ms < 500:
            return f"🟡 {response_time_ms:.1f}ms"
        return f"🔴 {response_time_ms:.1f}ms"

    def display_header(self):
        """Display dashboard header."""
        print("=" * 80)
        print("🏛️  ACGS-1 CONSTITUTIONAL GOVERNANCE SYSTEM HEALTH DASHBOARD")
        print("=" * 80)
        print(
            f"📅 {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S timezone.utc')}"
        )
        print(
            f"🔄 Auto-refresh every {self.refresh_interval} seconds (Press Ctrl+C to exit)"
        )
        print("=" * 80)

    def display_services_health(self, health_results: dict[str, Any]):
        """Display ACGS services health status."""
        print("\n🔧 ACGS SERVICES STATUS")
        print("-" * 50)

        services = [
            "auth_service",
            "ac_service",
            "integrity_service",
            "fv_service",
            "gs_service",
            "pgc_service",
            "ec_service",
        ]

        healthy_count = 0
        total_count = len(services)

        for service in services:
            if service in health_results:
                result = health_results[service]
                status = HealthStatus(result["status"])
                response_time = result["response_time_ms"]

                if status == HealthStatus.HEALTHY:
                    healthy_count += 1

                print(
                    f"  {service:20} {self.format_status(status):15} {self.format_response_time(response_time):15}"
                )

                if result.get("error_message"):
                    print(f"    ⚠️  Error: {result['error_message']}")
            else:
                print(f"  {service:20} ⚪ NOT MONITORED")

        print(f"\n📊 Services Summary: {healthy_count}/{total_count} healthy")

    def display_infrastructure_health(self, health_results: dict[str, Any]):
        """Display infrastructure components health."""
        print("\n🏗️  INFRASTRUCTURE STATUS")
        print("-" * 50)

        infrastructure = ["postgresql", "redis", "prometheus", "grafana"]

        for component in infrastructure:
            if component in health_results:
                result = health_results[component]
                status = HealthStatus(result["status"])
                response_time = result["response_time_ms"]

                print(
                    f"  {component:20} {self.format_status(status):15} {self.format_response_time(response_time):15}"
                )

                if result.get("error_message"):
                    print(f"    ⚠️  Error: {result['error_message']}")
            else:
                print(f"  {component:20} ⚪ NOT MONITORED")

    def display_blockchain_health(self, health_results: dict[str, Any]):
        """Display blockchain components health."""
        print("\n⛓️  BLOCKCHAIN STATUS")
        print("-" * 50)

        blockchain_components = [
            "solana_network",
            "quantumagi_programs",
            "constitution_hash",
        ]

        for component in blockchain_components:
            if component in health_results:
                result = health_results[component]
                status = HealthStatus(result["status"])
                response_time = result["response_time_ms"]

                print(
                    f"  {component:20} {self.format_status(status):15} {self.format_response_time(response_time):15}"
                )

                if result.get("error_message"):
                    print(f"    ⚠️  Error: {result['error_message']}")

                # Show additional details for specific components
                if component == "quantumagi_programs" and "details" in result:
                    details = result["details"]
                    healthy = details.get("healthy_programs", 0)
                    total = details.get("total_programs", 0)
                    print(f"    📋 Programs: {healthy}/{total} deployed")

                elif component == "constitution_hash" and "details" in result:
                    details = result["details"]
                    hash_value = details.get("hash", "N/A")
                    print(f"    🔐 Hash: {hash_value}")
            else:
                print(f"  {component:20} ⚪ NOT MONITORED")

    def display_performance_metrics(self, health_results: dict[str, Any]):
        """Display performance metrics summary."""
        print("\n📈 PERFORMANCE METRICS")
        print("-" * 50)

        # Calculate overall metrics
        all_results = list(health_results.values())
        if all_results:
            avg_response_time = sum(r["response_time_ms"] for r in all_results) / len(
                all_results
            )
            healthy_services = sum(1 for r in all_results if r["status"] == "healthy")
            total_services = len(all_results)
            uptime_percentage = (
                (healthy_services / total_services) * 100 if total_services > 0 else 0
            )

            print(
                f"  Average Response Time: {self.format_response_time(avg_response_time)}"
            )
            print(
                f"  System Uptime:         {'🟢' if uptime_percentage >= 99.5 else '🟡' if uptime_percentage >= 95 else '🔴'} {uptime_percentage:.1f}%"
            )
            print(f"  Healthy Components:    {healthy_services}/{total_services}")

            # Performance targets
            print("\n🎯 TARGETS:")
            print(
                f"  Response Time:         {'✅' if avg_response_time < 500 else '❌'} <500ms (current: {avg_response_time:.1f}ms)"
            )
            print(
                f"  Uptime:               {'✅' if uptime_percentage >= 99.5 else '❌'} >99.5% (current: {uptime_percentage:.1f}%)"
            )
            print(
                f"  Constitution Hash:     {'✅' if 'constitution_hash' in health_results and health_results['constitution_hash']['status'] == 'healthy' else '❌'} cdd01ef066bc6cf2"
            )

    def display_recent_alerts(self):
        """Display recent alerts if any."""
        # This would integrate with the actual alert system
        print("\n🚨 RECENT ALERTS")
        print("-" * 50)
        print("  No recent alerts (last 24 hours)")

    async def run_single_check(self):
        """Run a single health check and display results."""
        print("🔍 Running health checks...")

        # Simulate running health checks
        tasks = []

        # Check services
        for service_name, config in self.monitor.services.items():
            task = self.monitor._check_service_health(
                aiohttp.ClientSession(), service_name, config
            )
            tasks.append(task)

        # Run all checks
        try:
            async with aiohttp.ClientSession() as session:
                for service_name, config in self.monitor.services.items():
                    result = await self.monitor._check_service_health(
                        session, service_name, config
                    )
                    self.monitor.health_results[service_name] = result

                # Check infrastructure
                await self.monitor._check_postgresql_health()
                await self.monitor._check_redis_health()
                await self.monitor._check_prometheus_health()
                await self.monitor._check_grafana_health()

                # Check blockchain
                await self.monitor._check_solana_health()
                await self.monitor._check_quantumagi_health()
                await self.monitor._check_constitution_hash()

        except Exception as e:
            print(f"❌ Error during health checks: {e}")
            return

        # Get summary
        summary = self.monitor.get_health_summary()

        # Display results
        self.clear_screen()
        self.display_header()
        self.display_services_health(summary["services"])
        self.display_infrastructure_health(summary["services"])
        self.display_blockchain_health(summary["services"])
        self.display_performance_metrics(summary["services"])
        self.display_recent_alerts()

        print(f"\n🔄 Last updated: {summary['timestamp']}")

    async def run_dashboard(self):
        """Run the interactive dashboard."""
        try:
            while True:
                await self.run_single_check()
                await asyncio.sleep(self.refresh_interval)
        except KeyboardInterrupt:
            print("\n\n👋 Dashboard stopped by user")
        except Exception as e:
            print(f"\n❌ Dashboard error: {e}")


async def main():
    """Main function."""
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        # Run single check
        dashboard = HealthDashboard()
        await dashboard.run_single_check()
    else:
        # Run interactive dashboard
        dashboard = HealthDashboard()
        print("🚀 Starting ACGS-1 Health Dashboard...")
        print("Press Ctrl+C to exit")
        await dashboard.run_dashboard()


if __name__ == "__main__":
    asyncio.run(main())
