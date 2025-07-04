#!/usr/bin/env python3
"""
Debug GS Service Connectivity Issues

This script debugs the exact connectivity issues between GS Service and its dependencies.
"""

import asyncio
import os
import sys
from pathlib import Path

import httpx

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def test_connectivity_from_gs_perspective():
    """Test connectivity exactly as GS Service would."""

    print("🔍 Testing connectivity from GS Service perspective")
    print("=" * 55)

    # Test the exact same way GS Service does
    services_to_test = [
        {
            "name": "AC Service",
            "env_var": "AC_SERVICE_URL",
            "default": "http://localhost:8001",
            "endpoint": "/health",
        },
        {
            "name": "Integrity Service",
            "env_var": "INTEGRITY_SERVICE_URL",
            "default": "http://localhost:8002",
            "endpoint": "/health",
        },
    ]

    for service in services_to_test:
        print(f"\n🔍 Testing {service['name']}")
        print("-" * 30)

        # Get URL exactly as GS Service would
        service_url = os.getenv(service["env_var"], service["default"])
        full_url = f"{service_url}{service['endpoint']}"

        print(f"Environment variable: {service['env_var']}")
        print(f"Environment value: {os.getenv(service['env_var'], 'NOT SET')}")
        print(f"Default value: {service['default']}")
        print(f"Resolved URL: {service_url}")
        print(f"Full URL: {full_url}")

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                print(f"Making request to: {full_url}")
                response = await client.get(full_url)

                print(f"✅ Status Code: {response.status_code}")
                print(
                    f"✅ Response Time: {response.elapsed.total_seconds() * 1000:.2f}ms"
                )

                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"✅ Response Data: {data}")
                    except:
                        print(f"✅ Response Text: {response.text[:200]}")
                else:
                    print(f"⚠️ Non-200 response: {response.text[:200]}")

        except Exception as e:
            print(f"❌ Connection failed: {e}")
            print(f"❌ Error type: {type(e).__name__}")

            # Additional debugging
            import traceback

            print("❌ Full traceback:")
            traceback.print_exc()


async def test_direct_service_calls():
    """Test direct calls to services."""

    print("\n\n🔍 Testing direct service calls")
    print("=" * 35)

    services = [
        "http://localhost:8000/health",
        "http://localhost:8001/health",
        "http://localhost:8002/health",
        "http://localhost:8003/health",
        "http://localhost:8004/health",
        "http://localhost:8005/health",
        "http://localhost:8006/health",
    ]

    for url in services:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
                status = "✅" if response.status_code == 200 else "⚠️"
                print(f"{status} {url}: {response.status_code}")
        except Exception as e:
            print(f"❌ {url}: {e}")


async def simulate_gs_health_check():
    """Simulate the exact GS Service health check logic."""

    print("\n\n🔍 Simulating GS Service health check logic")
    print("=" * 45)

    health_status = {
        "status": "healthy",
        "service": "gs_service",
        "version": "1.0.0",
        "timestamp": "2024-01-20T00:00:00Z",
        "dependencies": {},
        "components": {},
    }

    # Test AC Service connectivity (exact same logic as GS Service)
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            ac_url = os.getenv("AC_SERVICE_URL", "http://localhost:8001")
            print(f"🔍 Testing AC Service at: {ac_url}/health")

            ac_response = await client.get(f"{ac_url}/health")
            health_status["dependencies"]["ac_service"] = {
                "status": "healthy" if ac_response.status_code == 200 else "unhealthy",
                "response_time_ms": (
                    ac_response.elapsed.total_seconds() * 1000
                    if hasattr(ac_response, "elapsed")
                    else 0
                ),
            }
            print(
                f"✅ AC Service result: {health_status['dependencies']['ac_service']}"
            )
    except Exception as e:
        health_status["dependencies"]["ac_service"] = {
            "status": "unhealthy",
            "error": str(e),
        }
        print(f"❌ AC Service error: {e}")

    # Test Integrity Service connectivity
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            integrity_url = os.getenv("INTEGRITY_SERVICE_URL", "http://localhost:8002")
            print(f"🔍 Testing Integrity Service at: {integrity_url}/health")

            integrity_response = await client.get(f"{integrity_url}/health")
            health_status["dependencies"]["integrity_service"] = {
                "status": (
                    "healthy" if integrity_response.status_code == 200 else "unhealthy"
                ),
                "response_time_ms": (
                    integrity_response.elapsed.total_seconds() * 1000
                    if hasattr(integrity_response, "elapsed")
                    else 0
                ),
            }
            print(
                f"✅ Integrity Service result: {health_status['dependencies']['integrity_service']}"
            )
    except Exception as e:
        health_status["dependencies"]["integrity_service"] = {
            "status": "unhealthy",
            "error": str(e),
        }
        print(f"❌ Integrity Service error: {e}")

    # Check if any critical dependencies are unhealthy
    critical_deps = ["ac_service"]
    unhealthy_critical = [
        dep
        for dep in critical_deps
        if health_status["dependencies"].get(dep, {}).get("status") == "unhealthy"
    ]

    if unhealthy_critical:
        health_status["status"] = "degraded"
        health_status["message"] = (
            f"Critical dependencies unhealthy: {', '.join(unhealthy_critical)}"
        )
    else:
        health_status["message"] = (
            "GS Service is operational with all dependencies healthy."
        )

    print("\n📊 Simulated Health Status:")
    import json

    print(json.dumps(health_status, indent=2))

    return health_status


async def check_environment_variables():
    """Check environment variables that might affect connectivity."""

    print("\n\n🔍 Checking environment variables")
    print("=" * 35)

    env_vars = [
        "AC_SERVICE_URL",
        "INTEGRITY_SERVICE_URL",
        "FV_SERVICE_URL",
        "PGC_SERVICE_URL",
        "EC_SERVICE_URL",
        "AUTH_SERVICE_URL",
        "SERVICE_DISCOVERY_ENABLED",
        "HEALTH_CHECK_TIMEOUT",
    ]

    for var in env_vars:
        value = os.getenv(var, "NOT SET")
        print(f"{var}: {value}")


async def main():
    """Main debugging function."""

    print("🚀 GS Service Connectivity Debug")
    print("=" * 35)

    # Check environment variables
    await check_environment_variables()

    # Test connectivity from GS perspective
    await test_connectivity_from_gs_perspective()

    # Test direct service calls
    await test_direct_service_calls()

    # Simulate GS health check
    simulated_health = await simulate_gs_health_check()

    print("\n📋 SUMMARY")
    print("=" * 15)

    if simulated_health["status"] == "healthy":
        print("✅ Simulated health check shows services should be healthy")
        print("🤔 There may be an issue with the actual GS Service process")
        print("💡 Consider restarting the GS Service process")
    else:
        print("❌ Simulated health check also shows issues")
        print("🔍 The connectivity problems are real and need investigation")

    return simulated_health


if __name__ == "__main__":
    result = asyncio.run(main())
