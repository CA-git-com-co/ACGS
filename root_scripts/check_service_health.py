#!/usr/bin/env python3
"""
ACGS-1 Service Health Check Script

This script checks the health and readiness of all 7 core services.
"""

import requests
import time
from pathlib import Path


def check_service_health():
    services = {
        "constitutional-ai": {"port": 8001, "path": "/health"},
        "governance-synthesis": {"port": 8004, "path": "/health"},
        "formal-verification": {"port": 8003, "path": "/health"},
        "policy-governance": {"port": 8005, "path": "/health"},
        "evolutionary-computation": {"port": 8006, "path": "/health"},
        "self-evolving-ai": {"port": 8007, "path": "/health"},
        "acgs-pgp-v8": {"port": 8010, "path": "/health"},
    }

    print("🏥 ACGS-1 Service Health Check")
    print("=" * 40)

    healthy_services = 0
    total_services = len(services)

    for service_name, config in services.items():
        try:
            url = f"http://localhost:{config['port']}{config['path']}"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                print(f"✅ {service_name}: Healthy")
                healthy_services += 1
            else:
                print(f"⚠️  {service_name}: Unhealthy (HTTP {response.status_code})")
        except requests.exceptions.ConnectionError:
            print(f"❌ {service_name}: Not running")
        except Exception as e:
            print(f"❌ {service_name}: Error - {e}")

    print(f"\n📊 Health Summary: {healthy_services}/{total_services} services healthy")

    if healthy_services == total_services:
        print("🎉 All services are healthy!")
        return True
    else:
        print("⚠️  Some services need attention")
        return False


if __name__ == "__main__":
    check_service_health()
