import os

#!/usr/bin/env python3
"""
ACGS Grafana Dashboard Setup Script
Imports constitutional compliance dashboard into Grafana

Constitutional Hash: cdd01ef066bc6cf2
"""

import json
import time
from datetime import datetime

import requests


def setup_grafana_dashboard():
    """Set up ACGS constitutional compliance dashboard in Grafana"""

    # Grafana configuration
    grafana_url = "http://localhost:3001"
    grafana_user = "admin"
    grafana_password = os.getenv("PASSWORD", "")

    print("🔧 Setting up ACGS Constitutional Compliance Dashboard")
    print(f"📊 Grafana URL: {grafana_url}")
    print("🔐 Constitutional Hash: cdd01ef066bc6cf2")
    print("=" * 80)

    # Wait for Grafana to be ready
    print("⏳ Waiting for Grafana to be ready...")
    for attempt in range(30):
        try:
            response = requests.get(f"{grafana_url}/api/health", timeout=5)
            if response.status_code == 200:
                print("✅ Grafana is ready!")
                break
        except:
            pass
        time.sleep(2)
        print(f"   Attempt {attempt + 1}/30...")
    else:
        print("❌ Grafana not ready after 60 seconds")
        return False

    # Set up Prometheus data source
    print("\n📡 Setting up Prometheus data source...")
    datasource_config = {
        "name": "Prometheus",
        "type": "prometheus",
        "url": "http://localhost:9090",
        "access": "proxy",
        "isDefault": True,
        "jsonData": {
            "httpMethod": "POST",
            "manageAlerts": True,
            "alertmanagerUid": "alertmanager",
        },
    }

    try:
        response = requests.post(
            f"{grafana_url}/api/datasources",
            auth=(grafana_user, grafana_password),
            headers={"Content-Type": "application/json"},
            json=datasource_config,
            timeout=10,
        )

        if response.status_code in [200, 409]:  # 409 = already exists
            print("✅ Prometheus data source configured")
        else:
            print(f"⚠️  Data source setup response: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Data source setup error: {e}")

    # Load dashboard configuration
    print("\n📋 Loading dashboard configuration...")
    try:
        with open("acgs_constitutional_compliance_dashboard.json") as f:
            dashboard_config = json.load(f)
        print("✅ Dashboard configuration loaded")
    except Exception as e:
        print(f"❌ Failed to load dashboard config: {e}")
        return False

    # Import dashboard
    print("\n📊 Importing ACGS Constitutional Compliance Dashboard...")
    dashboard_payload = {
        "dashboard": dashboard_config["dashboard"],
        "overwrite": True,
        "message": (
            f"ACGS Constitutional Compliance Dashboard - {datetime.now().isoformat()}"
        ),
    }

    try:
        response = requests.post(
            f"{grafana_url}/api/dashboards/db",
            auth=(grafana_user, grafana_password),
            headers={"Content-Type": "application/json"},
            json=dashboard_payload,
            timeout=15,
        )

        if response.status_code == 200:
            result = response.json()
            dashboard_url = f"{grafana_url}/d/{result['uid']}"
            print("✅ Dashboard imported successfully!")
            print(f"🔗 Dashboard URL: {dashboard_url}")
            return True
        else:
            print(f"❌ Dashboard import failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Dashboard import error: {e}")
        return False


def validate_monitoring_setup():
    """Validate that monitoring is working correctly"""

    print("\n🔍 MONITORING VALIDATION")
    print("=" * 80)

    # Check Prometheus
    print("📊 Checking Prometheus...")
    try:
        response = requests.get(
            "http://localhost:9090/api/v1/query?query=up", timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "success":
                targets = len(data["data"]["result"])
                print(f"✅ Prometheus operational - {targets} targets discovered")
            else:
                print("❌ Prometheus query failed")
        else:
            print(f"❌ Prometheus not responding: {response.status_code}")
    except Exception as e:
        print(f"❌ Prometheus check error: {e}")

    # Check Grafana
    print("\n📈 Checking Grafana...")
    try:
        response = requests.get("http://localhost:3001/api/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(
                f"✅ Grafana operational - Version {health.get('version', 'unknown')}"
            )
        else:
            print(f"❌ Grafana not responding: {response.status_code}")
    except Exception as e:
        print(f"❌ Grafana check error: {e}")

    # Check ACGS services
    print("\n🏛️  Checking ACGS Services...")
    services = [
        ("Constitutional AI", 8001),
        ("Integrity Service", 8002),
        ("Formal Verification", 8003),
        ("Governance Synthesis", 8004),
        ("Policy Governance", 8005),
        ("Evolutionary Computation", 8006),
        ("Code Analysis", 8007),
        ("Context Service", 8012),
        ("Authentication", 8016),
    ]

    operational_services = 0
    for service_name, port in services:
        try:
            response = requests.get(f"http://localhost:{port}/health", timeout=3)
            if response.status_code == 200:
                data = response.json()
                constitutional_hash = data.get("constitutional_hash", "missing")
                if constitutional_hash == "cdd01ef066bc6cf2":
                    print(f"✅ {service_name:25} Port {port:4} | Constitutional ✅")
                    operational_services += 1
                else:
                    print(f"⚠️  {service_name:25} Port {port:4} | Constitutional ❌")
            else:
                print(f"❌ {service_name:25} Port {port:4} | Not responding")
        except:
            print(f"❌ {service_name:25} Port {port:4} | Connection failed")

    print("\n📊 MONITORING SUMMARY")
    print("=" * 80)
    print(f"Operational Services: {operational_services}/{len(services)}")
    print("Constitutional Hash: cdd01ef066bc6cf2")
    print("Prometheus: http://localhost:9090")
    print("Grafana: http://localhost:3001 (admin/acgs_admin_2024)")
    print(f"Timestamp: {datetime.now().isoformat()}")

    return operational_services >= len(services) * 0.8  # 80% services operational


if __name__ == "__main__":
    print("🚀 ACGS Monitoring Setup")
    print("Constitutional Hash: cdd01ef066bc6cf2")
    print("=" * 80)

    # Setup dashboard
    dashboard_success = setup_grafana_dashboard()

    # Validate setup
    monitoring_success = validate_monitoring_setup()

    # Final status
    print("\n🏁 SETUP COMPLETE")
    print("=" * 80)
    if dashboard_success and monitoring_success:
        print("✅ ACGS monitoring fully operational!")
        print("✅ Constitutional compliance tracking active")
        print("✅ Performance monitoring enabled")
        exit(0)
    else:
        print("⚠️  Setup completed with issues")
        print("   Check logs above for details")
        exit(1)
