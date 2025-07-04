#!/usr/bin/env python3
"""
Comprehensive Service Restart Strategy

This script implements a systematic approach to restart all ACGS-1 services
and resolve the critical connectivity issues.
"""

import asyncio
import json
import subprocess
import sys
import time
from typing import Any

import httpx

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"



class ACGSServiceManager:
    """Manages ACGS-1 service lifecycle and health monitoring."""

    def __init__(self):
        self.services = {
            "auth_service": {"port": 8000, "status": "unknown"},
            "ac_service": {"port": 8001, "status": "unknown"},
            "integrity_service": {"port": 8002, "status": "unknown"},
            "fv_service": {"port": 8003, "status": "unknown"},
            "gs_service": {"port": 8004, "status": "unknown"},
            "pgc_service": {"port": 8005, "status": "unknown"},
            "ec_service": {"port": 8006, "status": "unknown"},
        }

    def check_docker_containers(self) -> dict[str, Any]:
        """Check status of Docker containers."""
        print("🐳 Checking Docker container status...")

        try:
            result = subprocess.run(
                ["docker", "ps", "-a"], capture_output=True, text=True, check=True
            )

            containers = {}
            lines = result.stdout.strip().split("\n")[1:]  # Skip header

            for line in lines:
                if "acgs_" in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        container_name = parts[-1]  # Last column is name
                        status = (
                            parts[4] if len(parts) > 4 else "unknown"
                        )  # Status column
                        containers[container_name] = {"status": status, "line": line}
                        print(f"  📦 {container_name}: {status}")

            return containers

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to check Docker containers: {e}")
            return {}

    def restart_docker_containers(self, containers: dict[str, Any]) -> dict[str, bool]:
        """Restart Docker containers."""
        print("🔄 Restarting Docker containers...")

        restart_results = {}

        # Priority order for restart
        priority_containers = [
            "acgs_ac_service",
            "acgs_integrity_service",
            "acgs_fv_service",
            "acgs_gs_service",
        ]

        for container_name in priority_containers:
            if container_name in containers:
                print(f"🔄 Restarting {container_name}...")
                try:
                    # Stop container
                    subprocess.run(
                        ["docker", "stop", container_name],
                        capture_output=True,
                        check=False,
                    )
                    time.sleep(2)

                    # Start container
                    subprocess.run(
                        ["docker", "start", container_name],
                        capture_output=True,
                        text=True,
                        check=True,
                    )

                    print(f"  ✅ {container_name} restarted successfully")
                    restart_results[container_name] = True

                    # Wait between restarts
                    time.sleep(5)

                except subprocess.CalledProcessError as e:
                    print(f"  ❌ Failed to restart {container_name}: {e}")
                    restart_results[container_name] = False
            else:
                print(f"  ⚠️ Container {container_name} not found")
                restart_results[container_name] = False

        return restart_results

    async def test_service_health(self, service_name: str, port: int) -> dict[str, Any]:
        """Test health of a single service."""
        url = f"http://localhost:{port}/health"

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                start_time = time.time()
                response = await client.get(url)
                response_time = (time.time() - start_time) * 1000

                return {
                    "service": service_name,
                    "port": port,
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "status_code": response.status_code,
                    "response_time_ms": round(response_time, 2),
                    "reachable": True,
                }
        except Exception as e:
            return {
                "service": service_name,
                "port": port,
                "status": "unreachable",
                "error": str(e),
                "reachable": False,
            }

    async def test_all_services(self) -> dict[str, Any]:
        """Test health of all services."""
        print("🏥 Testing service health...")

        results = {}
        for service_name, config in self.services.items():
            result = await self.test_service_health(service_name, config["port"])
            results[service_name] = result

            if result["reachable"]:
                status_icon = "✅" if result["status"] == "healthy" else "⚠️"
                print(
                    f"  {status_icon} {service_name}: {result['status']} ({result['response_time_ms']}ms)"
                )
            else:
                print(f"  ❌ {service_name}: unreachable - {result['error']}")

        return results

    def generate_service_summary(
        self, health_results: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate service health summary."""

        healthy = sum(
            1 for r in health_results.values() if r.get("status") == "healthy"
        )
        unhealthy = sum(
            1 for r in health_results.values() if r.get("status") == "unhealthy"
        )
        unreachable = sum(
            1 for r in health_results.values() if r.get("status") == "unreachable"
        )
        total = len(health_results)

        availability = (healthy / total) * 100 if total > 0 else 0

        summary = {
            "total_services": total,
            "healthy_services": healthy,
            "unhealthy_services": unhealthy,
            "unreachable_services": unreachable,
            "availability_percentage": round(availability, 1),
            "meets_target": availability >= 99.5,
            "critical_services_down": unreachable > 0,
            "timestamp": time.time(),
        }

        return summary

    async def run_comprehensive_restart(self) -> dict[str, Any]:
        """Run comprehensive service restart and validation."""

        print("🚀 ACGS-1 Comprehensive Service Restart")
        print("=" * 45)

        results = {
            "timestamp": time.time(),
            "initial_health": {},
            "docker_containers": {},
            "restart_results": {},
            "final_health": {},
            "summary": {},
            "success": False,
        }

        # Step 1: Initial health check
        print("\n📊 Step 1: Initial health assessment...")
        initial_health = await self.test_all_services()
        results["initial_health"] = initial_health

        initial_summary = self.generate_service_summary(initial_health)
        print(
            f"  📈 Initial status: {initial_summary['healthy_services']}/{initial_summary['total_services']} healthy ({initial_summary['availability_percentage']}%)"
        )

        # Step 2: Check Docker containers
        print("\n🐳 Step 2: Docker container assessment...")
        containers = self.check_docker_containers()
        results["docker_containers"] = containers

        # Step 3: Restart containers
        print("\n🔄 Step 3: Restarting Docker containers...")
        restart_results = self.restart_docker_containers(containers)
        results["restart_results"] = restart_results

        successful_restarts = sum(1 for success in restart_results.values() if success)
        print(
            f"  📈 Restart results: {successful_restarts}/{len(restart_results)} successful"
        )

        # Step 4: Wait for services to start
        print("\n⏳ Step 4: Waiting for services to start...")
        await asyncio.sleep(15)  # Give services time to start

        # Step 5: Final health check
        print("\n🏥 Step 5: Final health assessment...")
        final_health = await self.test_all_services()
        results["final_health"] = final_health

        final_summary = self.generate_service_summary(final_health)
        results["summary"] = final_summary

        # Step 6: Determine success
        improvement = (
            final_summary["healthy_services"] - initial_summary["healthy_services"]
        )
        results["improvement"] = improvement
        results["success"] = (
            final_summary["healthy_services"] >= 5
        )  # At least 5/7 services healthy

        # Summary
        print("\n📋 SUMMARY")
        print("=" * 15)
        print(
            f"Initial: {initial_summary['healthy_services']}/{initial_summary['total_services']} healthy ({initial_summary['availability_percentage']}%)"
        )
        print(
            f"Final:   {final_summary['healthy_services']}/{final_summary['total_services']} healthy ({final_summary['availability_percentage']}%)"
        )
        print(f"Improvement: +{improvement} services")

        if results["success"]:
            print("✅ Service restart successful!")
        else:
            print(
                "⚠️ Service restart partially successful - some services still need attention"
            )

        return results


async def main():
    """Main execution function."""
    manager = ACGSServiceManager()
    results = await manager.run_comprehensive_restart()

    # Save results
    results_file = f"service_restart_results_{int(time.time())}.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n📄 Results saved to: {results_file}")

    return 0 if results["success"] else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
