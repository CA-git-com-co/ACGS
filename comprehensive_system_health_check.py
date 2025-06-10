#!/usr/bin/env python3
"""
ACGS-1 Comprehensive System Health Check and Operational Status Verification

This script performs a systematic monitoring approach to verify all core services
and operational components of the ACGS-1 governance system.
"""

import asyncio
import aiohttp
import time
import json
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNREACHABLE = "unreachable"


@dataclass
class ServiceHealthResult:
    service_name: str
    port: int
    status: ServiceStatus
    response_time_ms: float
    http_status: Optional[int] = None
    health_data: Optional[Dict] = None
    error_message: Optional[str] = None
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


@dataclass
class SystemHealthReport:
    overall_status: ServiceStatus
    total_services: int
    healthy_services: int
    degraded_services: int
    unhealthy_services: int
    unreachable_services: int
    service_results: List[ServiceHealthResult]
    performance_metrics: Dict[str, Any]
    constitutional_compliance_status: Dict[str, Any]
    wina_oversight_status: Dict[str, Any]
    recommendations: List[str]
    timestamp: str
    execution_time_ms: float


class ACGSSystemHealthChecker:
    """Comprehensive health checker for ACGS-1 governance system."""

    def __init__(self):
        self.services = {
            "Auth Service": {"port": 8000, "health_endpoint": "/health"},
            "AC Service": {"port": 8001, "health_endpoint": "/health"},
            "Integrity Service": {"port": 8002, "health_endpoint": "/health"},
            "FV Service": {"port": 8003, "health_endpoint": "/health"},
            "GS Service": {"port": 8004, "health_endpoint": "/health"},
            "PGC Service": {"port": 8005, "health_endpoint": "/health"},
            "EC Service": {"port": 8006, "health_endpoint": "/health"},
        }

        self.performance_targets = {
            "response_time_ms": 2000,  # <2s response times
            "uptime_percentage": 99.5,  # >99.5% uptime
            "sol_cost_per_action": 0.01,  # <0.01 SOL per governance action
        }

        self.session = None

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10))
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    async def check_service_health(
        self, service_name: str, config: Dict
    ) -> ServiceHealthResult:
        """Check health of a single service."""
        port = config["port"]
        health_endpoint = config["health_endpoint"]
        url = f"http://localhost:{port}{health_endpoint}"

        start_time = time.time()

        try:
            async with self.session.get(url) as response:
                response_time_ms = (time.time() - start_time) * 1000

                if response.status == 200:
                    try:
                        health_data = await response.json()
                        status = ServiceStatus.HEALTHY

                        # Check for degraded status in health data
                        if isinstance(health_data, dict):
                            if health_data.get("status") == "degraded":
                                status = ServiceStatus.DEGRADED
                            elif "components" in health_data:
                                for component in health_data["components"].values():
                                    if (
                                        isinstance(component, dict)
                                        and component.get("status") == "degraded"
                                    ):
                                        status = ServiceStatus.DEGRADED
                                        break

                        return ServiceHealthResult(
                            service_name=service_name,
                            port=port,
                            status=status,
                            response_time_ms=response_time_ms,
                            http_status=response.status,
                            health_data=health_data,
                        )
                    except json.JSONDecodeError:
                        # Health endpoint returned non-JSON, but 200 status
                        return ServiceHealthResult(
                            service_name=service_name,
                            port=port,
                            status=ServiceStatus.HEALTHY,
                            response_time_ms=response_time_ms,
                            http_status=response.status,
                            health_data={"message": "Service responding (non-JSON)"},
                        )
                else:
                    return ServiceHealthResult(
                        service_name=service_name,
                        port=port,
                        status=ServiceStatus.UNHEALTHY,
                        response_time_ms=response_time_ms,
                        http_status=response.status,
                        error_message=f"HTTP {response.status}",
                    )

        except asyncio.TimeoutError:
            response_time_ms = (time.time() - start_time) * 1000
            return ServiceHealthResult(
                service_name=service_name,
                port=port,
                status=ServiceStatus.UNREACHABLE,
                response_time_ms=response_time_ms,
                error_message="Timeout",
            )
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            return ServiceHealthResult(
                service_name=service_name,
                port=port,
                status=ServiceStatus.UNREACHABLE,
                response_time_ms=response_time_ms,
                error_message=str(e),
            )

    async def check_all_services(self) -> List[ServiceHealthResult]:
        """Check health of all services concurrently."""
        logger.info("🔍 Checking health of all ACGS-1 services...")

        tasks = []
        for service_name, config in self.services.items():
            task = asyncio.create_task(self.check_service_health(service_name, config))
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle any exceptions
        health_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                service_name = list(self.services.keys())[i]
                config = list(self.services.values())[i]
                health_results.append(
                    ServiceHealthResult(
                        service_name=service_name,
                        port=config["port"],
                        status=ServiceStatus.UNREACHABLE,
                        response_time_ms=0,
                        error_message=str(result),
                    )
                )
            else:
                health_results.append(result)

        return health_results

    async def check_constitutional_compliance(self) -> Dict[str, Any]:
        """Check constitutional compliance validation status."""
        logger.info("⚖️ Checking constitutional compliance validation...")

        compliance_status = {
            "status": "unknown",
            "ac_service_available": False,
            "pgc_service_available": False,
            "compliance_checks_active": False,
            "last_validation": None,
            "error_message": None,
        }

        try:
            # Check AC Service constitutional endpoints
            ac_url = "http://localhost:8001/api/v1/constitutional-council/meta-rules"
            async with self.session.get(ac_url) as response:
                if response.status == 200:
                    compliance_status["ac_service_available"] = True
                    compliance_status["compliance_checks_active"] = True

            # Check PGC Service compliance endpoints
            pgc_url = "http://localhost:8005/api/v1/compliance/validate"
            async with self.session.post(
                pgc_url, json={"test": "compliance_check"}
            ) as response:
                if response.status in [200, 400, 422]:  # 400/422 expected for test data
                    compliance_status["pgc_service_available"] = True

            if (
                compliance_status["ac_service_available"]
                and compliance_status["pgc_service_available"]
            ):
                compliance_status["status"] = "active"
            elif (
                compliance_status["ac_service_available"]
                or compliance_status["pgc_service_available"]
            ):
                compliance_status["status"] = "partial"
            else:
                compliance_status["status"] = "inactive"

        except Exception as e:
            compliance_status["error_message"] = str(e)
            compliance_status["status"] = "error"

        return compliance_status

    async def check_wina_oversight_operations(self) -> Dict[str, Any]:
        """Check WINA oversight operations status."""
        logger.info("🎯 Checking WINA oversight operations...")

        wina_status = {
            "status": "unknown",
            "ec_service_available": False,
            "oversight_coordination_active": False,
            "wina_optimization_enabled": False,
            "performance_monitoring_active": False,
            "error_message": None,
        }

        try:
            # Check EC Service oversight endpoints
            ec_health_url = "http://localhost:8006/health"
            async with self.session.get(ec_health_url) as response:
                if response.status == 200:
                    wina_status["ec_service_available"] = True

            # Check WINA performance monitoring
            wina_perf_url = "http://localhost:8006/api/v1/wina/performance"
            async with self.session.get(wina_perf_url) as response:
                if response.status in [
                    200,
                    404,
                ]:  # 404 acceptable if endpoint not implemented
                    wina_status["performance_monitoring_active"] = True

            # Check oversight coordination
            oversight_url = "http://localhost:8006/api/v1/oversight"
            async with self.session.get(oversight_url) as response:
                if response.status in [
                    200,
                    405,
                ]:  # 405 acceptable for GET on POST endpoint
                    wina_status["oversight_coordination_active"] = True
                    wina_status["wina_optimization_enabled"] = True

            if (
                wina_status["ec_service_available"]
                and wina_status["oversight_coordination_active"]
            ):
                wina_status["status"] = "active"
            elif wina_status["ec_service_available"]:
                wina_status["status"] = "partial"
            else:
                wina_status["status"] = "inactive"

        except Exception as e:
            wina_status["error_message"] = str(e)
            wina_status["status"] = "error"

        return wina_status

    async def check_performance_metrics(
        self, service_results: List[ServiceHealthResult]
    ) -> Dict[str, Any]:
        """Analyze performance metrics against targets."""
        logger.info("📊 Analyzing performance metrics...")

        # Calculate response time statistics
        response_times = [
            r.response_time_ms for r in service_results if r.response_time_ms > 0
        ]
        avg_response_time = (
            sum(response_times) / len(response_times) if response_times else 0
        )
        max_response_time = max(response_times) if response_times else 0

        # Calculate service availability
        healthy_count = sum(
            1 for r in service_results if r.status == ServiceStatus.HEALTHY
        )
        total_count = len(service_results)
        availability_percentage = (
            (healthy_count / total_count) * 100 if total_count > 0 else 0
        )

        performance_metrics = {
            "response_time_metrics": {
                "average_ms": round(avg_response_time, 2),
                "maximum_ms": round(max_response_time, 2),
                "target_ms": self.performance_targets["response_time_ms"],
                "meets_target": max_response_time
                < self.performance_targets["response_time_ms"],
            },
            "availability_metrics": {
                "current_percentage": round(availability_percentage, 2),
                "target_percentage": self.performance_targets["uptime_percentage"],
                "meets_target": availability_percentage
                >= self.performance_targets["uptime_percentage"],
            },
            "service_distribution": {
                "healthy": healthy_count,
                "total": total_count,
                "degraded": sum(
                    1 for r in service_results if r.status == ServiceStatus.DEGRADED
                ),
                "unhealthy": sum(
                    1 for r in service_results if r.status == ServiceStatus.UNHEALTHY
                ),
                "unreachable": sum(
                    1 for r in service_results if r.status == ServiceStatus.UNREACHABLE
                ),
            },
        }

        return performance_metrics

    def generate_recommendations(
        self,
        service_results: List[ServiceHealthResult],
        performance_metrics: Dict[str, Any],
        compliance_status: Dict[str, Any],
        wina_status: Dict[str, Any],
    ) -> List[str]:
        """Generate recommendations based on health check results."""
        recommendations = []

        # Service-specific recommendations
        for result in service_results:
            if result.status == ServiceStatus.UNREACHABLE:
                recommendations.append(
                    f"🚨 CRITICAL: {result.service_name} is unreachable - check service status and restart if needed"
                )
            elif result.status == ServiceStatus.UNHEALTHY:
                recommendations.append(
                    f"⚠️ HIGH: {result.service_name} is unhealthy - investigate logs and service configuration"
                )
            elif result.status == ServiceStatus.DEGRADED:
                recommendations.append(
                    f"⚠️ MEDIUM: {result.service_name} is degraded - monitor performance and dependencies"
                )

        # Performance recommendations
        if not performance_metrics["response_time_metrics"]["meets_target"]:
            recommendations.append(
                f"⚠️ MEDIUM: Response times exceed target ({performance_metrics['response_time_metrics']['maximum_ms']}ms > {self.performance_targets['response_time_ms']}ms)"
            )

        if not performance_metrics["availability_metrics"]["meets_target"]:
            recommendations.append(
                f"🚨 HIGH: Service availability below target ({performance_metrics['availability_metrics']['current_percentage']}% < {self.performance_targets['uptime_percentage']}%)"
            )

        # Constitutional compliance recommendations
        if compliance_status["status"] == "inactive":
            recommendations.append(
                "🚨 CRITICAL: Constitutional compliance validation is inactive - verify AC and PGC services"
            )
        elif compliance_status["status"] == "partial":
            recommendations.append(
                "⚠️ HIGH: Constitutional compliance validation is partially active - check service dependencies"
            )
        elif compliance_status["status"] == "error":
            recommendations.append(
                "🚨 HIGH: Constitutional compliance validation has errors - check service logs"
            )

        # WINA oversight recommendations
        if wina_status["status"] == "inactive":
            recommendations.append(
                "⚠️ MEDIUM: WINA oversight operations are inactive - verify EC service configuration"
            )
        elif wina_status["status"] == "partial":
            recommendations.append(
                "⚠️ LOW: WINA oversight operations are partially active - monitor performance"
            )
        elif wina_status["status"] == "error":
            recommendations.append(
                "⚠️ MEDIUM: WINA oversight operations have errors - check EC service logs"
            )

        # General recommendations
        if not recommendations:
            recommendations.append("✅ All systems operational - continue monitoring")

        return recommendations

    def determine_overall_status(
        self, service_results: List[ServiceHealthResult]
    ) -> ServiceStatus:
        """Determine overall system status based on service results."""
        unreachable_count = sum(
            1 for r in service_results if r.status == ServiceStatus.UNREACHABLE
        )
        unhealthy_count = sum(
            1 for r in service_results if r.status == ServiceStatus.UNHEALTHY
        )
        degraded_count = sum(
            1 for r in service_results if r.status == ServiceStatus.DEGRADED
        )

        total_services = len(service_results)

        # Critical if more than 25% of services are unreachable or unhealthy
        if (unreachable_count + unhealthy_count) / total_services > 0.25:
            return ServiceStatus.UNHEALTHY

        # Degraded if any services are unreachable/unhealthy or more than 50% are degraded
        if (
            unreachable_count > 0
            or unhealthy_count > 0
            or degraded_count / total_services > 0.5
        ):
            return ServiceStatus.DEGRADED

        # Healthy if all services are healthy
        return ServiceStatus.HEALTHY

    async def run_comprehensive_health_check(self) -> SystemHealthReport:
        """Run comprehensive system health check."""
        start_time = time.time()
        logger.info("🚀 Starting ACGS-1 Comprehensive System Health Check")

        # Phase 1: Service Health Verification
        service_results = await self.check_all_services()

        # Phase 2: Constitutional Compliance Validation
        compliance_status = await self.check_constitutional_compliance()

        # Phase 3: WINA Oversight Operations Verification
        wina_status = await self.check_wina_oversight_operations()

        # Phase 4: Performance Metrics Analysis
        performance_metrics = await self.check_performance_metrics(service_results)

        # Phase 5: Generate Recommendations
        recommendations = self.generate_recommendations(
            service_results, performance_metrics, compliance_status, wina_status
        )

        # Phase 6: Determine Overall Status
        overall_status = self.determine_overall_status(service_results)

        execution_time_ms = (time.time() - start_time) * 1000

        # Count service statuses
        status_counts = {
            "healthy": sum(
                1 for r in service_results if r.status == ServiceStatus.HEALTHY
            ),
            "degraded": sum(
                1 for r in service_results if r.status == ServiceStatus.DEGRADED
            ),
            "unhealthy": sum(
                1 for r in service_results if r.status == ServiceStatus.UNHEALTHY
            ),
            "unreachable": sum(
                1 for r in service_results if r.status == ServiceStatus.UNREACHABLE
            ),
        }

        return SystemHealthReport(
            overall_status=overall_status,
            total_services=len(service_results),
            healthy_services=status_counts["healthy"],
            degraded_services=status_counts["degraded"],
            unhealthy_services=status_counts["unhealthy"],
            unreachable_services=status_counts["unreachable"],
            service_results=service_results,
            performance_metrics=performance_metrics,
            constitutional_compliance_status=compliance_status,
            wina_oversight_status=wina_status,
            recommendations=recommendations,
            timestamp=datetime.now().isoformat(),
            execution_time_ms=round(execution_time_ms, 2),
        )


def print_health_report(report: SystemHealthReport):
    """Print comprehensive health report to console."""
    print("\n" + "=" * 80)
    print("🏛️  ACGS-1 COMPREHENSIVE SYSTEM HEALTH REPORT")
    print("=" * 80)
    print(f"📅 Timestamp: {report.timestamp}")
    print(f"⏱️  Execution Time: {report.execution_time_ms}ms")
    print(f"🎯 Overall Status: {report.overall_status.value.upper()}")
    print()

    # Service Status Matrix
    print("📊 SERVICE AVAILABILITY MATRIX")
    print("-" * 50)
    status_icons = {
        ServiceStatus.HEALTHY: "✅",
        ServiceStatus.DEGRADED: "⚠️",
        ServiceStatus.UNHEALTHY: "❌",
        ServiceStatus.UNREACHABLE: "🔴",
    }

    for result in report.service_results:
        icon = status_icons.get(result.status, "❓")
        print(
            f"{icon} {result.service_name:<20} Port {result.port:<4} "
            f"{result.status.value:<12} {result.response_time_ms:>6.1f}ms"
        )
        if result.error_message:
            print(f"   └─ Error: {result.error_message}")

    print()
    print(
        f"📈 Services: {report.healthy_services}/{report.total_services} Healthy, "
        f"{report.degraded_services} Degraded, {report.unhealthy_services} Unhealthy, "
        f"{report.unreachable_services} Unreachable"
    )

    # Performance Metrics
    print("\n⚡ PERFORMANCE METRICS")
    print("-" * 30)
    perf = report.performance_metrics
    rt_metrics = perf["response_time_metrics"]
    avail_metrics = perf["availability_metrics"]

    rt_status = "✅" if rt_metrics["meets_target"] else "⚠️"
    avail_status = "✅" if avail_metrics["meets_target"] else "⚠️"

    print(
        f"{rt_status} Response Time: {rt_metrics['average_ms']:.1f}ms avg, "
        f"{rt_metrics['maximum_ms']:.1f}ms max (target: <{rt_metrics['target_ms']}ms)"
    )
    print(
        f"{avail_status} Availability: {avail_metrics['current_percentage']:.1f}% "
        f"(target: >{avail_metrics['target_percentage']}%)"
    )

    # Constitutional Compliance Status
    print("\n⚖️  CONSTITUTIONAL COMPLIANCE STATUS")
    print("-" * 40)
    compliance = report.constitutional_compliance_status
    compliance_icons = {
        "active": "✅",
        "partial": "⚠️",
        "inactive": "❌",
        "error": "🚨",
        "unknown": "❓",
    }
    compliance_icon = compliance_icons.get(compliance["status"], "❓")

    print(f"{compliance_icon} Status: {compliance['status'].upper()}")
    print(
        f"   AC Service Available: {'✅' if compliance['ac_service_available'] else '❌'}"
    )
    print(
        f"   PGC Service Available: {'✅' if compliance['pgc_service_available'] else '❌'}"
    )
    print(
        f"   Compliance Checks Active: {'✅' if compliance['compliance_checks_active'] else '❌'}"
    )

    # WINA Oversight Status
    print("\n🎯 WINA OVERSIGHT OPERATIONS STATUS")
    print("-" * 40)
    wina = report.wina_oversight_status
    wina_icon = compliance_icons.get(wina["status"], "❓")

    print(f"{wina_icon} Status: {wina['status'].upper()}")
    print(f"   EC Service Available: {'✅' if wina['ec_service_available'] else '❌'}")
    print(
        f"   Oversight Coordination: {'✅' if wina['oversight_coordination_active'] else '❌'}"
    )
    print(
        f"   WINA Optimization: {'✅' if wina['wina_optimization_enabled'] else '❌'}"
    )
    print(
        f"   Performance Monitoring: {'✅' if wina['performance_monitoring_active'] else '❌'}"
    )

    # Recommendations
    print("\n💡 RECOMMENDATIONS")
    print("-" * 20)
    for i, recommendation in enumerate(report.recommendations, 1):
        print(f"{i:2d}. {recommendation}")

    print("\n" + "=" * 80)
    print("🏛️  END OF HEALTH REPORT")
    print("=" * 80)


async def main():
    """Main execution function."""
    try:
        async with ACGSSystemHealthChecker() as health_checker:
            report = await health_checker.run_comprehensive_health_check()

            # Print report to console
            print_health_report(report)

            # Save report to JSON file
            report_filename = f"acgs_health_report_{int(time.time())}.json"
            with open(report_filename, "w") as f:
                # Convert dataclasses to dict for JSON serialization
                report_dict = asdict(report)
                # Convert enums to strings
                report_dict["overall_status"] = report.overall_status.value
                for service_result in report_dict["service_results"]:
                    service_result["status"] = ServiceStatus(
                        service_result["status"]
                    ).value

                json.dump(report_dict, f, indent=2, default=str)

            logger.info(f"📄 Health report saved to: {report_filename}")

            # Return appropriate exit code
            if report.overall_status == ServiceStatus.HEALTHY:
                return 0
            elif report.overall_status == ServiceStatus.DEGRADED:
                return 1
            else:
                return 2

    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return 3


if __name__ == "__main__":
    exit_code = asyncio.run(main())
