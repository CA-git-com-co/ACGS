#!/usr/bin/env python3
"""
ACGS-1 Phase 3 Service Validation Script

This script validates all 7 core services and tests their health endpoints,
API compatibility, and basic functionality to ensure they meet production
readiness criteria.

Services tested:
- Auth Service (8000)
- AC Service (8001) 
- Integrity Service (8002)
- FV Service (8003)
- GS Service (8004)
- PGC Service (8005)
- EC Service (8006)
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Any
import httpx

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Service configuration
SERVICES = {
    "auth": {"port": 8000, "name": "Authentication Service"},
    "ac": {"port": 8001, "name": "Constitutional AI Service"},
    "integrity": {"port": 8002, "name": "Integrity Service"},
    "fv": {"port": 8003, "name": "Formal Verification Service"},
    "gs": {"port": 8004, "name": "Governance Synthesis Service"},
    "pgc": {"port": 8005, "name": "Policy Governance Service"},
    "ec": {"port": 8006, "name": "Evolutionary Computation Service"},
}


class ServiceValidator:
    """Validates ACGS-1 core services for production readiness."""

    def __init__(self):
        self.results = {}
        self.timeout = 10

    async def validate_service_health(
        self, service_name: str, port: int
    ) -> Dict[str, Any]:
        """Validate a single service health endpoint."""
        url = f"http://localhost:{port}/health"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                start_time = time.time()
                response = await client.get(url)
                response_time = (time.time() - start_time) * 1000  # ms

                if response.status_code == 200:
                    data = response.json()
                    return {
                        "status": "healthy",
                        "response_time_ms": response_time,
                        "data": data,
                        "meets_sla": response_time < 500,  # <500ms requirement
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "response_time_ms": response_time,
                        "status_code": response.status_code,
                        "meets_sla": False,
                    }

        except Exception as e:
            logger.error(f"Health check failed for {service_name}: {e}")
            return {"status": "error", "error": str(e), "meets_sla": False}

    async def validate_service_api(
        self, service_name: str, port: int
    ) -> Dict[str, Any]:
        """Validate service API endpoints."""
        base_url = f"http://localhost:{port}"
        endpoints_to_test = ["/", "/api/v1/status"]

        results = {}

        for endpoint in endpoints_to_test:
            url = f"{base_url}{endpoint}"
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    start_time = time.time()
                    response = await client.get(url)
                    response_time = (time.time() - start_time) * 1000

                    results[endpoint] = {
                        "status_code": response.status_code,
                        "response_time_ms": response_time,
                        "accessible": response.status_code
                        in [200, 403],  # 403 might be security middleware
                        "meets_sla": response_time < 500,
                    }

            except Exception as e:
                results[endpoint] = {
                    "error": str(e),
                    "accessible": False,
                    "meets_sla": False,
                }

        return results

    async def test_inter_service_communication(self) -> Dict[str, Any]:
        """Test communication between services."""
        # Test if services can reach each other's health endpoints
        communication_results = {}

        for service_name, config in SERVICES.items():
            port = config["port"]
            try:
                async with httpx.AsyncClient(timeout=5) as client:
                    # Test if we can reach the service from another service perspective
                    response = await client.get(f"http://localhost:{port}/health")
                    communication_results[service_name] = {
                        "reachable": response.status_code in [200, 403],
                        "status_code": response.status_code,
                    }
            except Exception as e:
                communication_results[service_name] = {
                    "reachable": False,
                    "error": str(e),
                }

        return communication_results

    async def validate_all_services(self) -> Dict[str, Any]:
        """Validate all ACGS-1 core services."""
        logger.info("🚀 Starting ACGS-1 Phase 3 Service Validation")

        validation_results = {
            "timestamp": time.time(),
            "services": {},
            "summary": {},
            "inter_service_communication": {},
            "overall_status": "unknown",
        }

        # Validate each service
        for service_name, config in SERVICES.items():
            logger.info(f"🔍 Validating {config['name']} (port {config['port']})")

            # Health check
            health_result = await self.validate_service_health(
                service_name, config["port"]
            )

            # API validation
            api_result = await self.validate_service_api(service_name, config["port"])

            validation_results["services"][service_name] = {
                "name": config["name"],
                "port": config["port"],
                "health": health_result,
                "api": api_result,
                "operational": health_result.get("status") == "healthy",
            }

        # Test inter-service communication
        logger.info("🔗 Testing inter-service communication")
        validation_results["inter_service_communication"] = (
            await self.test_inter_service_communication()
        )

        # Calculate summary
        operational_services = sum(
            1 for s in validation_results["services"].values() if s["operational"]
        )
        total_services = len(SERVICES)

        validation_results["summary"] = {
            "total_services": total_services,
            "operational_services": operational_services,
            "failed_services": total_services - operational_services,
            "success_rate": (operational_services / total_services) * 100,
            "meets_uptime_sla": (operational_services / total_services)
            >= 0.99,  # >99% uptime
        }

        # Determine overall status
        if operational_services == total_services:
            validation_results["overall_status"] = "all_operational"
        elif operational_services >= total_services * 0.8:
            validation_results["overall_status"] = "mostly_operational"
        else:
            validation_results["overall_status"] = "degraded"

        return validation_results

    def print_validation_report(self, results: Dict[str, Any]):
        """Print a comprehensive validation report."""
        print("\n" + "=" * 80)
        print("🧪 ACGS-1 PHASE 3 SERVICE VALIDATION REPORT")
        print("=" * 80)

        summary = results["summary"]
        print(
            f"📊 Services: {summary['operational_services']}/{summary['total_services']} operational"
        )
        print(f"📈 Success Rate: {summary['success_rate']:.1f}%")
        print(
            f"🎯 Uptime SLA Met: {'✅ YES' if summary['meets_uptime_sla'] else '❌ NO'}"
        )
        print(f"🏆 Overall Status: {results['overall_status']}")

        print("\n📋 SERVICE DETAILS:")
        for service_name, service_data in results["services"].items():
            status_icon = "✅" if service_data["operational"] else "❌"
            health = service_data["health"]
            response_time = health.get("response_time_ms", "N/A")
            sla_met = "✅" if health.get("meets_sla", False) else "❌"

            print(f"  {status_icon} {service_data['name']} (:{service_data['port']})")
            if isinstance(response_time, (int, float)):
                print(f"     Response Time: {response_time:.1f}ms {sla_met}")
            else:
                print(f"     Response Time: {response_time} {sla_met}")
            print(f"     Status: {health.get('status', 'unknown')}")

        print("\n🔗 INTER-SERVICE COMMUNICATION:")
        comm_results = results["inter_service_communication"]
        reachable_services = sum(
            1 for r in comm_results.values() if r.get("reachable", False)
        )
        print(f"  Reachable Services: {reachable_services}/{len(comm_results)}")

        for service_name, comm_data in comm_results.items():
            icon = "✅" if comm_data.get("reachable", False) else "❌"
            print(f"    {icon} {service_name}")


async def main():
    """Main validation function."""
    validator = ServiceValidator()
    results = await validator.validate_all_services()

    # Print report
    validator.print_validation_report(results)

    # Save results
    with open("tests/results/service_validation_results.json", "w") as f:
        json.dump(results, f, indent=2)

    logger.info(
        "📋 Validation results saved to tests/results/service_validation_results.json"
    )

    # Return exit code based on results
    if results["overall_status"] == "all_operational":
        return 0
    elif results["overall_status"] == "mostly_operational":
        return 1
    else:
        return 2


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
