#!/usr/bin/env python3
"""
ACGS-PGP Production Monitoring Dashboard
Native Python implementation for constitutional compliance and performance monitoring
"""

import asyncio
import aiohttp
import json
import time
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Any
import argparse
from dataclasses import dataclass, asdict

# ACGS-PGP Configuration
SERVICES = {
    "auth_service": {"port": 8000, "name": "Authentication Service"},
    "ac_service": {"port": 8001, "name": "Constitutional AI Service"},
    "integrity_service": {"port": 8002, "name": "Integrity Service"},
    "fv_service": {"port": 8003, "name": "Formal Verification Service"},
    "gs_service": {"port": 8004, "name": "Governance Synthesis Service"},
    "pgc_service": {"port": 8005, "name": "Policy Governance Service"},
    "ec_service": {"port": 8006, "name": "Evolutionary Computation Service"},
}

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
COMPLIANCE_THRESHOLD = 0.75
RESPONSE_TIME_TARGET = 2.0  # seconds


@dataclass
class ServiceMetrics:
    """Service performance metrics."""

    name: str
    port: int
    status: str
    response_time: float
    constitutional_compliance: float
    last_check: datetime
    error_count: int = 0
    success_count: int = 0


class ACGSMonitor:
    """ACGS-PGP System Monitor."""

    def __init__(self):
        self.metrics_history = []
        self.alerts = []
        self.start_time = datetime.now()

    async def check_service_health(
        self, session: aiohttp.ClientSession, service_name: str, port: int
    ) -> ServiceMetrics:
        """Check health of a single service."""
        url = f"http://localhost:{port}/health"
        start_time = time.time()

        try:
            headers = {"X-Constitutional-Hash": CONSTITUTIONAL_HASH}
            async with session.get(
                url, headers=headers, timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                response_time = time.time() - start_time

                if response.status == 200:
                    data = await response.json()

                    # Extract constitutional compliance
                    compliance = 1.0  # Default compliant
                    if "constitutional_hash" in data:
                        compliance = (
                            1.0
                            if data.get("constitutional_hash") == CONSTITUTIONAL_HASH
                            else 0.0
                        )
                    elif "compliance_score" in data:
                        compliance = float(data.get("compliance_score", 1.0))

                    return ServiceMetrics(
                        name=service_name,
                        port=port,
                        status="healthy",
                        response_time=response_time,
                        constitutional_compliance=compliance,
                        last_check=datetime.now(),
                        success_count=1,
                    )
                else:
                    return ServiceMetrics(
                        name=service_name,
                        port=port,
                        status=f"unhealthy_http_{response.status}",
                        response_time=response_time,
                        constitutional_compliance=0.0,
                        last_check=datetime.now(),
                        error_count=1,
                    )

        except Exception as e:
            response_time = time.time() - start_time
            return ServiceMetrics(
                name=service_name,
                port=port,
                status=f"error_{str(e)[:20]}",
                response_time=response_time,
                constitutional_compliance=0.0,
                last_check=datetime.now(),
                error_count=1,
            )

    async def collect_metrics(self) -> List[ServiceMetrics]:
        """Collect metrics from all services."""
        metrics = []

        async with aiohttp.ClientSession() as session:
            tasks = []
            for service_name, config in SERVICES.items():
                task = self.check_service_health(session, service_name, config["port"])
                tasks.append(task)

            metrics = await asyncio.gather(*tasks, return_exceptions=True)

            # Filter out exceptions
            valid_metrics = [m for m in metrics if isinstance(m, ServiceMetrics)]

        return valid_metrics

    def analyze_system_health(self, metrics: List[ServiceMetrics]) -> Dict[str, Any]:
        """Analyze overall system health."""
        healthy_services = sum(1 for m in metrics if m.status == "healthy")
        total_services = len(metrics)

        response_times = [m.response_time for m in metrics if m.status == "healthy"]
        compliance_scores = [m.constitutional_compliance for m in metrics]

        avg_response_time = (
            statistics.mean(response_times) if response_times else float("inf")
        )
        avg_compliance = (
            statistics.mean(compliance_scores) if compliance_scores else 0.0
        )

        # Calculate system health score
        health_score = (
            (healthy_services / total_services) * 100 if total_services > 0 else 0
        )

        # Performance assessment
        response_time_pass = avg_response_time <= RESPONSE_TIME_TARGET
        compliance_pass = avg_compliance >= COMPLIANCE_THRESHOLD

        return {
            "timestamp": datetime.now().isoformat(),
            "healthy_services": healthy_services,
            "total_services": total_services,
            "health_percentage": health_score,
            "avg_response_time": avg_response_time,
            "avg_constitutional_compliance": avg_compliance,
            "response_time_target_met": response_time_pass,
            "compliance_threshold_met": compliance_pass,
            "production_ready": health_score >= 90
            and response_time_pass
            and compliance_pass,
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

    def check_alerts(
        self, metrics: List[ServiceMetrics], system_health: Dict[str, Any]
    ):
        """Check for alert conditions."""
        current_time = datetime.now()

        # Critical alerts
        if system_health["health_percentage"] < 50:
            self.alerts.append(
                {
                    "severity": "CRITICAL",
                    "message": f"System health critical: {system_health['health_percentage']:.1f}%",
                    "timestamp": current_time.isoformat(),
                    "type": "system_health",
                }
            )

        # High priority alerts
        if not system_health["response_time_target_met"]:
            self.alerts.append(
                {
                    "severity": "HIGH",
                    "message": f"Response time target exceeded: {system_health['avg_response_time']:.3f}s > {RESPONSE_TIME_TARGET}s",
                    "timestamp": current_time.isoformat(),
                    "type": "performance",
                }
            )

        if not system_health["compliance_threshold_met"]:
            self.alerts.append(
                {
                    "severity": "HIGH",
                    "message": f"Constitutional compliance below threshold: {system_health['avg_constitutional_compliance']:.3f} < {COMPLIANCE_THRESHOLD}",
                    "timestamp": current_time.isoformat(),
                    "type": "constitutional_compliance",
                }
            )

        # Service-specific alerts
        for metric in metrics:
            if metric.status != "healthy":
                self.alerts.append(
                    {
                        "severity": "MODERATE",
                        "message": f"Service {metric.name} unhealthy: {metric.status}",
                        "timestamp": current_time.isoformat(),
                        "type": "service_health",
                    }
                )

    def display_dashboard(
        self, metrics: List[ServiceMetrics], system_health: Dict[str, Any]
    ):
        """Display monitoring dashboard."""
        print("\n" + "=" * 80)
        print("🏛️  ACGS-PGP PRODUCTION MONITORING DASHBOARD")
        print("=" * 80)
        print(f"📅 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f"🔗 Constitutional Hash: {CONSTITUTIONAL_HASH}")
        print(f"⏱️  Uptime: {datetime.now() - self.start_time}")

        # System Overview
        print(f"\n📊 SYSTEM OVERVIEW")
        print("-" * 40)
        health_status = (
            "🟢 HEALTHY" if system_health["production_ready"] else "🔴 DEGRADED"
        )
        print(f"Status: {health_status}")
        print(f"Health Score: {system_health['health_percentage']:.1f}%")
        print(
            f"Services Online: {system_health['healthy_services']}/{system_health['total_services']}"
        )
        print(
            f"Avg Response Time: {system_health['avg_response_time']:.3f}s (target: ≤{RESPONSE_TIME_TARGET}s)"
        )
        print(
            f"Constitutional Compliance: {system_health['avg_constitutional_compliance']:.3f} (threshold: ≥{COMPLIANCE_THRESHOLD})"
        )

        # Service Status
        print(f"\n🔧 SERVICE STATUS")
        print("-" * 40)
        for metric in metrics:
            status_icon = "🟢" if metric.status == "healthy" else "🔴"
            compliance_icon = (
                "✅"
                if metric.constitutional_compliance >= COMPLIANCE_THRESHOLD
                else "❌"
            )
            response_icon = (
                "⚡" if metric.response_time <= RESPONSE_TIME_TARGET else "🐌"
            )

            print(
                f"{status_icon} {metric.name:25} | Port {metric.port} | {metric.response_time:.3f}s {response_icon} | Compliance: {metric.constitutional_compliance:.2f} {compliance_icon}"
            )

        # Recent Alerts
        if self.alerts:
            recent_alerts = [
                a
                for a in self.alerts
                if datetime.fromisoformat(a["timestamp"])
                > datetime.now() - timedelta(minutes=5)
            ]
            if recent_alerts:
                print(f"\n🚨 RECENT ALERTS (Last 5 minutes)")
                print("-" * 40)
                for alert in recent_alerts[-5:]:  # Show last 5 alerts
                    severity_icon = {
                        "CRITICAL": "🔴",
                        "HIGH": "🟠",
                        "MODERATE": "🟡",
                    }.get(alert["severity"], "ℹ️")
                    print(f"{severity_icon} [{alert['severity']}] {alert['message']}")

        # Performance Targets
        print(f"\n🎯 PERFORMANCE TARGETS")
        print("-" * 40)
        print(
            f"Response Time: {'✅ PASS' if system_health['response_time_target_met'] else '❌ FAIL'} (≤{RESPONSE_TIME_TARGET}s)"
        )
        print(
            f"Constitutional Compliance: {'✅ PASS' if system_health['compliance_threshold_met'] else '❌ FAIL'} (≥{COMPLIANCE_THRESHOLD})"
        )
        print(
            f"System Health: {'✅ PASS' if system_health['health_percentage'] >= 90 else '❌ FAIL'} (≥90%)"
        )
        print(
            f"Production Ready: {'✅ YES' if system_health['production_ready'] else '❌ NO'}"
        )

    def save_metrics(
        self, metrics: List[ServiceMetrics], system_health: Dict[str, Any]
    ):
        """Save metrics to file."""
        report = {
            "system_health": system_health,
            "service_metrics": [asdict(m) for m in metrics],
            "alerts": self.alerts[-10:],  # Last 10 alerts
            "monitoring_config": {
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "compliance_threshold": COMPLIANCE_THRESHOLD,
                "response_time_target": RESPONSE_TIME_TARGET,
            },
        }

        with open("/home/ubuntu/ACGS/monitoring_report.json", "w") as f:
            json.dump(report, f, indent=2, default=str)


async def main():
    parser = argparse.ArgumentParser(description="ACGS-PGP Monitoring Dashboard")
    parser.add_argument(
        "--interval", type=int, default=30, help="Monitoring interval in seconds"
    )
    parser.add_argument("--continuous", action="store_true", help="Run continuously")
    parser.add_argument("--output", type=str, help="Output file for metrics")

    args = parser.parse_args()

    monitor = ACGSMonitor()

    print("🚀 Starting ACGS-PGP Production Monitoring")
    print(f"📊 Monitoring {len(SERVICES)} services")
    print(f"🔄 Interval: {args.interval}s")
    print(
        f"🎯 Targets: ≤{RESPONSE_TIME_TARGET}s response time, ≥{COMPLIANCE_THRESHOLD} constitutional compliance"
    )

    try:
        while True:
            # Collect metrics
            metrics = await monitor.collect_metrics()
            system_health = monitor.analyze_system_health(metrics)

            # Check for alerts
            monitor.check_alerts(metrics, system_health)

            # Display dashboard
            monitor.display_dashboard(metrics, system_health)

            # Save metrics
            monitor.save_metrics(metrics, system_health)

            if not args.continuous:
                break

            print(f"\n⏳ Next check in {args.interval} seconds... (Ctrl+C to stop)")
            await asyncio.sleep(args.interval)

    except KeyboardInterrupt:
        print("\n\n🛑 Monitoring stopped by user")
        print("📄 Final report saved to: /home/ubuntu/ACGS/monitoring_report.json")


if __name__ == "__main__":
    asyncio.run(main())
