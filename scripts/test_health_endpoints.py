#!/usr/bin/env python3
"""Test health endpoints across all services."""

import sys
import urllib.error
import urllib.request


def test_health_endpoint(service_name: str, port: int) -> bool:
    """Test a single service health endpoint."""
    try:
        url = f"http://localhost:{port}/health"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                print(f"✅ {service_name} health endpoint OK")
                return True
            print(f"❌ {service_name} health endpoint failed: {response.status}")
            return False
    except Exception as e:
        print(f"❌ {service_name} health endpoint error: {e}")
        return False


def main():
    """Test all service health endpoints."""
    services = {
        "auth_service": 8000,
        "ac_service": 8001,
        "integrity_service": 8002,
        "fv_service": 8003,
        "gs_service": 8004,
        "pgc_service": 8005,
        "ec_service": 8006,
    }

    results = []
    for service_name, port in services.items():
        result = test_health_endpoint(service_name, port)
        results.append(result)

    healthy_count = sum(results)
    total_count = len(results)

    print(f"\n📊 Health Check Summary: {healthy_count}/{total_count} services healthy")

    if healthy_count == total_count:
        print("🎉 All services healthy!")
        sys.exit(0)
    else:
        print("⚠️ Some services unhealthy")
        sys.exit(1)


if __name__ == "__main__":
    main()
