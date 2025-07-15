#!/usr/bin/env python3
"""
ACGS-1 Service Stabilization Manager

Command-line tool for managing service architecture stabilization:
- Real-time service health monitoring
- Manual failover triggering
- Performance metrics analysis
- System status reporting
- Service recovery operations

Usage:
    python service_stabilization_manager.py status
    python service_stabilization_manager.py monitor
    python service_stabilization_manager.py failover <service_name>
    python service_stabilization_manager.py recover <service_name>
    python service_stabilization_manager.py metrics
"""

import argparse
import asyncio
import logging
import sys
import time
from datetime import datetime

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


# Add the services directory to the path
sys.path.append("/home/dislove/ACGS-1/services")

from services.shared.service_mesh.enhanced_service_stabilizer import get_service_stabilizer
from services.shared.service_mesh.registry import ServiceType
from services.shared.service_mesh.service_orchestrator import (
    OrchestrationConfig,
    OrchestrationMode,
    get_service_orchestrator,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ServiceStabilizationManager:
    """CLI manager for ACGS-1 service stabilization."""

    def __init__(self):
        self.orchestrator = None
        self.stabilizer = None

    async def initialize(self):
        """Initialize the service components."""
        try:
            # Initialize orchestrator in production mode
            config = OrchestrationConfig(
                mode=OrchestrationMode.PRODUCTION,
                enable_service_discovery=True,
                enable_load_balancing=True,
                enable_circuit_breakers=True,
                enable_auto_failover=True,
                enable_health_monitoring=True,
                enable_performance_monitoring=True,
                enable_predictive_analysis=True,
                target_availability_percent=99.5,
                target_response_time_ms=2000.0,
                health_check_interval_seconds=10.0,
            )

            self.orchestrator = await get_service_orchestrator(config)
            self.stabilizer = await get_service_stabilizer()

            print("✅ Service stabilization components initialized")

        except Exception as e:
            print(f"❌ Failed to initialize components: {e}")
            raise

    async def cleanup(self):
        """Cleanup resources."""
        try:
            if self.orchestrator:
                await self.orchestrator.stop()
            if self.stabilizer:
                await self.stabilizer.stop()
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

    async def show_status(self):
        """Show comprehensive system status."""
        print("\n🔍 ACGS-1 Service Architecture Status")
        print("=" * 60)

        try:
            # Get orchestration status
            orchestration_status = self.orchestrator.get_orchestration_status()

            print(
                f"🎛️  Orchestrator Status: {'Running' if orchestration_status['running'] else 'Stopped'}"
            )
            print(f"🏗️  Mode: {orchestration_status['mode']}")
            print(f"⏱️  Uptime: {orchestration_status['uptime_seconds']:.0f} seconds")
            print()

            # Get service health
            service_health = await self.orchestrator.get_service_status()

            print("🏥 Service Health Status:")
            print("-" * 40)

            healthy_count = 0
            total_services = len(service_health)

            for service_name, health in service_health.items():
                status = health.get("status", "unknown")
                response_time = health.get("response_time_ms", 0)
                availability = health.get("availability_percent", 0)

                status_icon = self._get_status_icon(status)
                print(
                    f"{status_icon} {service_name:<20} | {status:<10} | {response_time:>6.1f}ms | {availability:>5.1f}%"
                )

                if status == "healthy":
                    healthy_count += 1

            print("-" * 40)
            print(f"📊 Summary: {healthy_count}/{total_services} services healthy")

            # System metrics
            metrics = orchestration_status.get("metrics", {})
            print(
                f"⚡ Avg Response Time: {metrics.get('average_response_time_ms', 0):.1f}ms"
            )
            print(
                f"📈 System Availability: {metrics.get('system_availability_percent', 0):.2f}%"
            )
            print(f"🔄 Failovers Executed: {metrics.get('failovers_executed', 0)}")

            # Performance targets
            config = orchestration_status.get("configuration", {})
            print("\n🎯 Performance Targets:")
            print(
                f"   Availability: ≥{config.get('target_availability_percent', 99.5)}%"
            )
            print(f"   Response Time: ≤{config.get('target_response_time_ms', 2000)}ms")
            print(f"   Error Rate: ≤{config.get('target_error_rate_percent', 1.0)}%")

        except Exception as e:
            print(f"❌ Error getting status: {e}")

    async def monitor_services(self, duration: int = 60):
        """Monitor services in real-time."""
        print(f"\n📊 Real-time Service Monitoring ({duration}s)")
        print("=" * 60)
        print("Press Ctrl+C to stop monitoring")
        print()

        try:
            start_time = time.time()

            while time.time() - start_time < duration:
                # Clear screen (simple version)
                print("\033[H\033[J", end="")

                # Show current time
                print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("-" * 40)

                # Get current service status
                service_health = await self.orchestrator.get_service_status()

                for service_name, health in service_health.items():
                    status = health.get("status", "unknown")
                    response_time = health.get("response_time_ms", 0)
                    availability = health.get("availability_percent", 0)
                    failures = health.get("consecutive_failures", 0)

                    status_icon = self._get_status_icon(status)
                    failure_indicator = (
                        f" ({failures} failures)" if failures > 0 else ""
                    )

                    print(
                        f"{status_icon} {service_name:<18} | {response_time:>6.1f}ms | {availability:>5.1f}%{failure_indicator}"
                    )

                await asyncio.sleep(5)  # Update every 5 seconds

        except KeyboardInterrupt:
            print("\n\n⏹️  Monitoring stopped by user")
        except Exception as e:
            print(f"\n❌ Monitoring error: {e}")

    async def trigger_failover(self, service_name: str):
        """Trigger manual failover for a service."""
        print(f"\n🔄 Triggering failover for {service_name}")
        print("-" * 40)

        try:
            # Convert service name to ServiceType
            service_type = self._get_service_type(service_name)
            if not service_type:
                print(f"❌ Unknown service: {service_name}")
                return

            # Trigger failover
            result = await self.orchestrator.trigger_manual_failover(service_type)

            if result.get("success"):
                print(f"✅ {result.get('message')}")

                # Wait a moment and show updated status
                await asyncio.sleep(2)
                print("\n📊 Updated service status:")
                service_health = await self.orchestrator.get_service_status(
                    service_type
                )

                if service_health:
                    status = service_health.get("status", "unknown")
                    response_time = service_health.get("response_time_ms", 0)
                    print(f"   Status: {status}")
                    print(f"   Response Time: {response_time:.1f}ms")

            else:
                print(f"❌ Failover failed: {result.get('error')}")

        except Exception as e:
            print(f"❌ Error triggering failover: {e}")

    async def recover_service(self, service_name: str):
        """Attempt to recover a failed service."""
        print(f"\n🔧 Attempting to recover {service_name}")
        print("-" * 40)

        try:
            service_type = self._get_service_type(service_name)
            if not service_type:
                print(f"❌ Unknown service: {service_name}")
                return

            # Get current service status
            service_health = await self.orchestrator.get_service_status(service_type)

            if not service_health:
                print(f"❌ No health information available for {service_name}")
                return

            current_status = service_health.get("status", "unknown")
            print(f"Current status: {current_status}")

            if current_status == "healthy":
                print(f"✅ Service {service_name} is already healthy")
                return

            # Show recommendations if available
            recommendations = service_health.get("recommendations", [])
            if recommendations:
                print("\n💡 Recommendations:")
                for i, rec in enumerate(recommendations, 1):
                    print(f"   {i}. {rec}")

            print("\n🔄 Recovery attempt in progress...")

            # The stabilizer will automatically attempt recovery
            # We'll monitor for a few seconds to see if it recovers
            for i in range(6):  # Check for 30 seconds
                await asyncio.sleep(5)
                updated_health = await self.orchestrator.get_service_status(
                    service_type
                )
                updated_status = updated_health.get("status", "unknown")

                print(f"   Check {i + 1}/6: {updated_status}")

                if updated_status == "healthy":
                    print(f"✅ Service {service_name} recovered successfully!")
                    return

            print(f"⚠️  Service {service_name} did not recover automatically")
            print("   Manual intervention may be required")

        except Exception as e:
            print(f"❌ Error during recovery: {e}")

    async def show_metrics(self):
        """Show detailed performance metrics."""
        print("\n📈 ACGS-1 Performance Metrics")
        print("=" * 50)

        try:
            orchestration_status = self.orchestrator.get_orchestration_status()
            metrics = orchestration_status.get("metrics", {})

            print("🎯 System Metrics:")
            print(f"   Services Managed: {metrics.get('services_managed', 0)}")
            print(f"   Total Requests: {metrics.get('total_requests_routed', 0)}")
            print(f"   Successful Requests: {metrics.get('successful_requests', 0)}")
            print(f"   Failed Requests: {metrics.get('failed_requests', 0)}")
            print(f"   Failovers Executed: {metrics.get('failovers_executed', 0)}")
            print(
                f"   Average Response Time: {metrics.get('average_response_time_ms', 0):.2f}ms"
            )
            print(
                f"   System Availability: {metrics.get('system_availability_percent', 0):.3f}%"
            )
            print(f"   Uptime: {metrics.get('uptime_seconds', 0):.0f} seconds")

            # Service-specific metrics
            print("\n🏥 Service Health Metrics:")
            service_health = await self.orchestrator.get_service_status()

            for service_name, health in service_health.items():
                print(f"\n   {service_name}:")
                print(f"     Status: {health.get('status', 'unknown')}")
                print(f"     Response Time: {health.get('response_time_ms', 0):.2f}ms")
                print(
                    f"     Availability: {health.get('availability_percent', 0):.2f}%"
                )
                print(f"     Error Rate: {health.get('error_rate_percent', 0):.2f}%")
                print(
                    f"     Consecutive Failures: {health.get('consecutive_failures', 0)}"
                )
                print(
                    f"     Failure Risk: {health.get('predicted_failure_risk', 0):.2f}"
                )

        except Exception as e:
            print(f"❌ Error getting metrics: {e}")

    def _get_status_icon(self, status: str) -> str:
        """Get status icon for display."""
        icons = {"healthy": "✅", "degraded": "⚠️", "unhealthy": "❌", "unknown": "❓"}
        return icons.get(status, "❓")

    def _get_service_type(self, service_name: str) -> ServiceType | None:
        """Convert service name to ServiceType enum."""
        service_mapping = {
            "auth": ServiceType.AUTH,
            "auth_service": ServiceType.AUTH,
            "ac": ServiceType.AC,
            "ac_service": ServiceType.AC,
            "fv": ServiceType.FV,
            "fv_service": ServiceType.FV,
            "gs": ServiceType.GS,
            "gs_service": ServiceType.GS,
            "pgc": ServiceType.PGC,
            "pgc_service": ServiceType.PGC,
            "integrity": ServiceType.INTEGRITY,
            "integrity_service": ServiceType.INTEGRITY,
            "ec": ServiceType.EC,
            "ec_service": ServiceType.EC,
        }
        return service_mapping.get(service_name.lower())


async def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="ACGS-1 Service Stabilization Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python service_stabilization_manager.py status
  python service_stabilization_manager.py monitor --duration 120
  python service_stabilization_manager.py failover ac_service
  python service_stabilization_manager.py recover pgc_service
  python service_stabilization_manager.py metrics
        """,
    )

    parser.add_argument(
        "command",
        choices=["status", "monitor", "failover", "recover", "metrics"],
        help="Command to execute",
    )

    parser.add_argument(
        "service",
        nargs="?",
        help="Service name (required for failover and recover commands)",
    )

    parser.add_argument(
        "--duration",
        type=int,
        default=60,
        help="Monitoring duration in seconds (default: 60)",
    )

    args = parser.parse_args()

    # Validate arguments
    if args.command in ["failover", "recover"] and not args.service:
        print(f"❌ Service name required for {args.command} command")
        sys.exit(1)

    manager = ServiceStabilizationManager()

    try:
        print("🚀 Initializing ACGS-1 Service Stabilization Manager...")
        await manager.initialize()

        if args.command == "status":
            await manager.show_status()
        elif args.command == "monitor":
            await manager.monitor_services(args.duration)
        elif args.command == "failover":
            await manager.trigger_failover(args.service)
        elif args.command == "recover":
            await manager.recover_service(args.service)
        elif args.command == "metrics":
            await manager.show_metrics()

    except KeyboardInterrupt:
        print("\n\n⏹️  Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    finally:
        await manager.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
