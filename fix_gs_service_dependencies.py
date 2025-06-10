#!/usr/bin/env python3
"""
Fix GS Service Dependencies

This script addresses the critical issue where GS Service cannot connect to AC and Integrity services
by updating the service configuration and testing connectivity.
"""

import asyncio
import os
import sys
import json
import httpx
import time
from pathlib import Path
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


class GSServiceDependencyFixer:
    """Fixes GS Service dependency connectivity issues."""

    def __init__(self):
        self.services = {
            "ac_service": {"url": "http://localhost:8001", "port": 8001},
            "integrity_service": {"url": "http://localhost:8002", "port": 8002},
            "fv_service": {"url": "http://localhost:8003", "port": 8003},
            "gs_service": {"url": "http://localhost:8004", "port": 8004},
            "pgc_service": {"url": "http://localhost:8005", "port": 8005},
            "ec_service": {"url": "http://localhost:8006", "port": 8006},
        }

    async def test_service_connectivity(
        self, service_name: str, service_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Test connectivity to a specific service."""
        url = service_config["url"]
        health_url = f"{url}/health"

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                start_time = time.time()
                response = await client.get(health_url)
                response_time = (time.time() - start_time) * 1000

                return {
                    "service": service_name,
                    "url": url,
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "status_code": response.status_code,
                    "response_time_ms": round(response_time, 2),
                    "reachable": True,
                }
        except Exception as e:
            return {
                "service": service_name,
                "url": url,
                "status": "unreachable",
                "error": str(e),
                "reachable": False,
            }

    async def test_all_services(self) -> Dict[str, Any]:
        """Test connectivity to all services."""
        print("🔍 Testing connectivity to all services...")

        results = {}
        for service_name, config in self.services.items():
            result = await self.test_service_connectivity(service_name, config)
            results[service_name] = result

            if result["reachable"]:
                status_icon = "✅" if result["status"] == "healthy" else "⚠️"
                print(
                    f"{status_icon} {service_name}: {result['status']} ({result['response_time_ms']}ms)"
                )
            else:
                print(f"❌ {service_name}: unreachable - {result['error']}")

        return results

    async def update_gs_service_config(self) -> bool:
        """Update GS Service configuration with correct URLs."""
        print("🔧 Updating GS Service configuration...")

        # The .env file has already been created, now we need to check if the service
        # can reload its configuration or if we need to restart it

        # First, let's try to send a configuration reload signal if the service supports it
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Try to call a config reload endpoint if it exists
                reload_url = "http://localhost:8004/api/v1/admin/reload-config"
                response = await client.post(reload_url)

                if response.status_code == 200:
                    print("✅ GS Service configuration reloaded successfully")
                    return True
                else:
                    print(f"⚠️ Config reload endpoint returned {response.status_code}")
        except Exception as e:
            print(f"⚠️ Config reload not available: {e}")

        # If reload doesn't work, we'll need to restart the service
        print("🔄 Service restart required for configuration changes")
        return False

    async def verify_gs_service_health(self) -> Dict[str, Any]:
        """Verify GS Service health after configuration update."""
        print("🏥 Verifying GS Service health...")

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get("http://localhost:8004/health")

                if response.status_code == 200:
                    health_data = response.json()
                    print("📊 GS Service Health Status:")
                    print(json.dumps(health_data, indent=2))
                    return health_data
                else:
                    print(
                        f"❌ GS Service health check failed: HTTP {response.status_code}"
                    )
                    return {
                        "status": "unhealthy",
                        "error": f"HTTP {response.status_code}",
                    }
        except Exception as e:
            print(f"❌ GS Service health check failed: {e}")
            return {"status": "unreachable", "error": str(e)}

    async def create_service_restart_script(self):
        """Create a script to restart GS Service with new configuration."""
        restart_script = """#!/bin/bash
# GS Service Restart Script
# This script restarts the GS Service with updated configuration

echo "🔄 Restarting GS Service with updated configuration..."

# Change to GS Service directory
cd /home/dislove/ACGS-1/services/core/governance-synthesis/gs_service

# Load environment variables
export $(cat .env | xargs)

# Kill existing GS Service process (if running as current user)
pkill -f "uvicorn.*8004" 2>/dev/null || true

# Wait for process to stop
sleep 3

# Start GS Service with new configuration
echo "🚀 Starting GS Service..."
nohup uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload > gs_service.log 2>&1 &

# Wait for service to start
sleep 5

# Test service health
echo "🏥 Testing service health..."
curl -s http://localhost:8004/health | jq .

echo "✅ GS Service restart complete"
"""

        script_path = "restart_gs_service.sh"
        with open(script_path, "w") as f:
            f.write(restart_script)

        os.chmod(script_path, 0o755)
        print(f"📝 Created restart script: {script_path}")
        return script_path

    async def fix_service_discovery_config(self):
        """Fix service discovery configuration."""
        print("🔧 Fixing service discovery configuration...")

        # Update service registry configuration
        service_registry_config = {
            "services": {
                "auth_service": {
                    "url": "http://localhost:8000",
                    "health_endpoint": "/health",
                },
                "ac_service": {
                    "url": "http://localhost:8001",
                    "health_endpoint": "/health",
                },
                "integrity_service": {
                    "url": "http://localhost:8002",
                    "health_endpoint": "/health",
                },
                "fv_service": {
                    "url": "http://localhost:8003",
                    "health_endpoint": "/health",
                },
                "gs_service": {
                    "url": "http://localhost:8004",
                    "health_endpoint": "/health",
                },
                "pgc_service": {
                    "url": "http://localhost:8005",
                    "health_endpoint": "/health",
                },
                "ec_service": {
                    "url": "http://localhost:8006",
                    "health_endpoint": "/health",
                },
            },
            "environment": "development",
            "discovery_enabled": True,
            "health_check_interval": 30,
        }

        config_path = "service_registry_config.json"
        with open(config_path, "w") as f:
            json.dump(service_registry_config, f, indent=2)

        print(f"📝 Created service registry config: {config_path}")
        return config_path

    async def run_comprehensive_fix(self) -> Dict[str, Any]:
        """Run comprehensive fix for GS Service dependencies."""
        print("🚀 Starting GS Service Dependency Fix")
        print("=" * 50)

        results = {
            "timestamp": time.time(),
            "fixes_applied": [],
            "connectivity_results": {},
            "gs_service_health": {},
            "success": False,
        }

        # Step 1: Test initial connectivity
        print("\n📊 Step 1: Testing initial service connectivity")
        initial_connectivity = await self.test_all_services()
        results["connectivity_results"]["initial"] = initial_connectivity

        # Step 2: Update GS Service configuration
        print("\n🔧 Step 2: Updating GS Service configuration")
        config_updated = await self.update_gs_service_config()
        if config_updated:
            results["fixes_applied"].append("gs_service_config_reloaded")
        else:
            results["fixes_applied"].append(
                "gs_service_config_updated_restart_required"
            )

        # Step 3: Create restart script
        print("\n📝 Step 3: Creating service restart script")
        restart_script = await self.create_service_restart_script()
        results["fixes_applied"].append(f"restart_script_created: {restart_script}")

        # Step 4: Fix service discovery
        print("\n🔧 Step 4: Fixing service discovery configuration")
        registry_config = await self.fix_service_discovery_config()
        results["fixes_applied"].append(
            f"service_registry_config_created: {registry_config}"
        )

        # Step 5: Wait and test connectivity again
        print("\n⏳ Step 5: Waiting for configuration to take effect...")
        await asyncio.sleep(5)

        final_connectivity = await self.test_all_services()
        results["connectivity_results"]["final"] = final_connectivity

        # Step 6: Verify GS Service health
        print("\n🏥 Step 6: Verifying GS Service health")
        gs_health = await self.verify_gs_service_health()
        results["gs_service_health"] = gs_health

        # Determine success
        gs_deps_healthy = (
            gs_health.get("dependencies", {}).get("ac_service", {}).get("status")
            == "healthy"
            and gs_health.get("dependencies", {})
            .get("integrity_service", {})
            .get("status")
            == "healthy"
        )

        results["success"] = gs_deps_healthy

        # Summary
        print("\n📋 SUMMARY")
        print("=" * 20)
        if results["success"]:
            print("✅ GS Service dependencies fixed successfully!")
        else:
            print("⚠️ GS Service dependencies still need attention")
            print("💡 Manual restart may be required using: ./restart_gs_service.sh")

        print(f"\n📊 Fixes applied: {len(results['fixes_applied'])}")
        for fix in results["fixes_applied"]:
            print(f"  - {fix}")

        return results


async def main():
    """Main execution function."""
    fixer = GSServiceDependencyFixer()
    results = await fixer.run_comprehensive_fix()

    # Save results
    results_file = f"gs_dependency_fix_results_{int(time.time())}.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n📄 Results saved to: {results_file}")

    return 0 if results["success"] else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
