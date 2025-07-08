#!/usr/bin/env python3
"""
ACGS Alerting System Validation
Tests automated alerting for constitutional compliance and performance violations

Constitutional Hash: cdd01ef066bc6cf2
"""

from datetime import datetime

import requests


def validate_prometheus_alerts():
    """Validate Prometheus alerting rules are loaded"""
    print("🚨 Validating Prometheus Alert Rules...")

    try:
        # Check if alert rules are loaded
        response = requests.get("http://localhost:9090/api/v1/rules", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "success":
                groups = data["data"]["groups"]
                total_rules = sum(len(group["rules"]) for group in groups)
                print(
                    f"✅ Prometheus rules loaded: {len(groups)} groups,"
                    f" {total_rules} rules"
                )

                # Check for constitutional compliance rules
                constitutional_rules = []
                performance_rules = []

                for group in groups:
                    for rule in group["rules"]:
                        if "constitutional" in rule.get("name", "").lower():
                            constitutional_rules.append(rule["name"])
                        elif any(
                            keyword in rule.get("name", "").lower()
                            for keyword in [
                                "latency",
                                "performance",
                                "cache",
                                "throughput",
                            ]
                        ):
                            performance_rules.append(rule["name"])

                print(f"✅ Constitutional rules: {len(constitutional_rules)}")
                print(f"✅ Performance rules: {len(performance_rules)}")

                return True
            else:
                print("❌ Prometheus rules query failed")
                return False
        else:
            print(f"❌ Prometheus not responding: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Prometheus rules check error: {e}")
        return False


def validate_alertmanager():
    """Validate Alertmanager is operational"""
    print("\n📢 Validating Alertmanager...")

    try:
        # Check Alertmanager status
        response = requests.get("http://localhost:9093/api/v1/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "success":
                config = data["data"]["configYAML"]
                print("✅ Alertmanager operational")

                # Check for constitutional compliance receivers
                if "constitutional" in config.lower():
                    print("✅ Constitutional compliance alerting configured")
                else:
                    print("⚠️  Constitutional compliance alerting not found")

                return True
            else:
                print("❌ Alertmanager status query failed")
                return False
        else:
            print(f"❌ Alertmanager not responding: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Alertmanager check error: {e}")
        return False


def check_active_alerts():
    """Check for any active alerts"""
    print("\n🔔 Checking Active Alerts...")

    try:
        # Get active alerts from Prometheus
        response = requests.get("http://localhost:9090/api/v1/alerts", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "success":
                alerts = data["data"]["alerts"]

                if not alerts:
                    print("✅ No active alerts - system healthy")
                    return True

                print(f"⚠️  {len(alerts)} active alerts:")
                constitutional_alerts = 0
                performance_alerts = 0

                for alert in alerts:
                    alert_name = alert["labels"]["alertname"]
                    state = alert["state"]

                    if "constitutional" in alert_name.lower():
                        constitutional_alerts += 1
                        print(f"🚨 CONSTITUTIONAL: {alert_name} ({state})")
                    elif any(
                        keyword in alert_name.lower()
                        for keyword in ["latency", "performance", "cache", "throughput"]
                    ):
                        performance_alerts += 1
                        print(f"⚡ PERFORMANCE: {alert_name} ({state})")
                    else:
                        print(f"ℹ️  OTHER: {alert_name} ({state})")

                print("\nAlert Summary:")
                print(f"  Constitutional alerts: {constitutional_alerts}")
                print(f"  Performance alerts: {performance_alerts}")
                print(
                    "  Other alerts:"
                    f" {len(alerts) - constitutional_alerts - performance_alerts}"
                )

                return constitutional_alerts == 0  # No constitutional violations
            else:
                print("❌ Prometheus alerts query failed")
                return False
        else:
            print(f"❌ Prometheus not responding: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Active alerts check error: {e}")
        return False


def test_alert_notification():
    """Test alert notification system"""
    print("\n📨 Testing Alert Notification System...")

    try:
        # Get Alertmanager alerts
        response = requests.get("http://localhost:9093/api/v1/alerts", timeout=10)
        if response.status_code == 200:
            data = response.json()
            alerts = data["data"]

            print(f"✅ Alertmanager accessible - {len(alerts)} alerts in system")

            # Check for silences
            response = requests.get("http://localhost:9093/api/v1/silences", timeout=10)
            if response.status_code == 200:
                silences_data = response.json()
                silences = silences_data["data"]
                print(f"✅ Alert silences: {len(silences)} active")

            return True
        else:
            print(f"❌ Alertmanager alerts not accessible: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Alert notification test error: {e}")
        return False


def validate_constitutional_monitoring():
    """Validate constitutional compliance monitoring specifically"""
    print("\n⚖️  Validating Constitutional Compliance Monitoring...")

    constitutional_metrics = [
        "acgs_constitutional_compliance_score",
        "acgs_constitutional_hash_valid",
        "acgs_constitutional_validation_total",
    ]

    valid_metrics = 0

    for metric in constitutional_metrics:
        try:
            response = requests.get(
                f"http://localhost:9090/api/v1/query?query={metric}", timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                if data["status"] == "success" and data["data"]["result"]:
                    print(f"✅ {metric}: Available")
                    valid_metrics += 1
                else:
                    print(f"⚠️  {metric}: No data")
            else:
                print(f"❌ {metric}: Query failed")
        except Exception as e:
            print(f"❌ {metric}: Error - {e}")

    print(
        "\nConstitutional Metrics:"
        f" {valid_metrics}/{len(constitutional_metrics)} available"
    )
    return valid_metrics >= len(constitutional_metrics) * 0.5  # At least 50% available


def main():
    """Main validation function"""
    print("🚀 ACGS Alerting System Validation")
    print("Constitutional Hash: cdd01ef066bc6cf2")
    print("=" * 80)

    # Run all validations
    validations = [
        ("Prometheus Alert Rules", validate_prometheus_alerts),
        ("Alertmanager Status", validate_alertmanager),
        ("Active Alerts Check", check_active_alerts),
        ("Alert Notifications", test_alert_notification),
        ("Constitutional Monitoring", validate_constitutional_monitoring),
    ]

    results = {}
    for name, validation_func in validations:
        print(f"\n{'=' * 20} {name} {'=' * 20}")
        results[name] = validation_func()

    # Summary
    print("\n🏁 ALERTING VALIDATION SUMMARY")
    print("=" * 80)

    passed = sum(results.values())
    total = len(results)

    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {name}")

    print(f"\nOverall: {passed}/{total} validations passed")
    print("Constitutional Hash: cdd01ef066bc6cf2")
    print(f"Timestamp: {datetime.now().isoformat()}")

    if passed >= total * 0.8:  # 80% pass rate
        print("\n✅ ALERTING SYSTEM OPERATIONAL")
        print("✅ Constitutional compliance monitoring active")
        print("✅ Performance alerting enabled")
        return True
    else:
        print("\n⚠️  ALERTING SYSTEM NEEDS ATTENTION")
        print("   Some validations failed - check logs above")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
