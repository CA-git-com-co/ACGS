#!/usr/bin/env python3
"""
ACGS Alert Notification Testing Script
Constitutional Hash: cdd01ef066bc6cf2

This script tests the alert notification channels for ACGS monitoring system.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional

import aiohttp
import requests

# Constitutional compliance hash
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Monitoring endpoints
PROMETHEUS_URL = "http://localhost:9090"
ALERTMANAGER_URL = "http://localhost:9093"
GRAFANA_URL = "http://localhost:3000"

# Test alert configurations
TEST_ALERTS = [
    {
        "name": "ConstitutionalHashMissing",
        "severity": "critical",
        "description": "Test constitutional hash coverage alert",
        "metric": "constitutional_hash_coverage",
        "threshold": 0.95,
        "test_value": 0.90,
    },
    {
        "name": "P99LatencyExceeded",
        "severity": "warning",
        "description": "Test P99 latency alert",
        "metric": "acgs_request_duration_seconds",
        "threshold": 0.005,
        "test_value": 0.008,
    },
    {
        "name": "CacheHitRateLow",
        "severity": "warning",
        "description": "Test cache hit rate alert",
        "metric": "acgs_cache_hit_rate",
        "threshold": 0.85,
        "test_value": 0.80,
    },
]


class AlertNotificationTester:
    """Test alert notification channels for ACGS monitoring."""

    def __init__(self):
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.test_results = []
        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )
        return logging.getLogger(__name__)

    async def test_prometheus_connectivity(self) -> bool:
        """Test Prometheus connectivity and query capability."""
        self.logger.info("Testing Prometheus connectivity...")

        try:
            async with aiohttp.ClientSession() as session:
                # Test basic connectivity
                async with session.get(
                    f"{PROMETHEUS_URL}/api/v1/query", params={"query": "up"}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.logger.info("✅ Prometheus connectivity successful")
                        return True
                    else:
                        self.logger.error(
                            f"❌ Prometheus returned status {response.status}"
                        )
                        return False
        except Exception as e:
            self.logger.error(f"❌ Prometheus connectivity failed: {e}")
            return False

    async def test_alertmanager_connectivity(self) -> bool:
        """Test Alertmanager connectivity."""
        self.logger.info("Testing Alertmanager connectivity...")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{ALERTMANAGER_URL}/api/v2/status") as response:
                    if response.status == 200:
                        self.logger.info("✅ Alertmanager connectivity successful")
                        return True
                    else:
                        self.logger.error(
                            f"❌ Alertmanager returned status {response.status}"
                        )
                        return False
        except Exception as e:
            self.logger.error(f"❌ Alertmanager connectivity failed: {e}")
            return False

    async def test_grafana_connectivity(self) -> bool:
        """Test Grafana connectivity."""
        self.logger.info("Testing Grafana connectivity...")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{GRAFANA_URL}/api/health") as response:
                    if response.status == 200:
                        self.logger.info("✅ Grafana connectivity successful")
                        return True
                    else:
                        self.logger.error(
                            f"❌ Grafana returned status {response.status}"
                        )
                        return False
        except Exception as e:
            self.logger.error(f"❌ Grafana connectivity failed: {e}")
            return False

    async def simulate_constitutional_violation(self) -> bool:
        """Simulate a constitutional compliance violation."""
        self.logger.info("Simulating constitutional violation alert...")

        # Create test alert payload (v2 API expects array directly)
        alert_payload = [
            {
                "labels": {
                    "alertname": "ConstitutionalViolationDetected",
                    "severity": "critical",
                    "component": "constitutional_compliance",
                    "constitutional_hash": self.constitutional_hash,
                },
                "annotations": {
                    "summary": "Test constitutional violation detected",
                    "description": "This is a test alert for constitutional compliance monitoring",
                },
                "startsAt": datetime.now(timezone.utc).isoformat(),
                "generatorURL": f"{PROMETHEUS_URL}/graph",
            }
        ]

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{ALERTMANAGER_URL}/api/v2/alerts", json=alert_payload
                ) as response:
                    if response.status == 200:
                        self.logger.info(
                            "✅ Constitutional violation alert sent successfully"
                        )
                        return True
                    else:
                        self.logger.error(f"❌ Failed to send alert: {response.status}")
                        return False
        except Exception as e:
            self.logger.error(f"❌ Failed to simulate constitutional violation: {e}")
            return False

    async def test_performance_alert(self) -> bool:
        """Test performance degradation alert."""
        self.logger.info("Testing performance degradation alert...")

        alert_payload = [
            {
                "labels": {
                    "alertname": "P99LatencyExceeded",
                    "severity": "warning",
                    "component": "performance",
                    "constitutional_hash": self.constitutional_hash,
                },
                "annotations": {
                    "summary": "Test P99 latency exceeds 5ms target",
                    "description": "P99 latency is 8ms, exceeding the 5ms constitutional requirement",
                },
                "startsAt": datetime.now(timezone.utc).isoformat(),
                "generatorURL": f"{PROMETHEUS_URL}/graph",
            }
        ]

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{ALERTMANAGER_URL}/api/v2/alerts", json=alert_payload
                ) as response:
                    if response.status == 200:
                        self.logger.info("✅ Performance alert sent successfully")
                        return True
                    else:
                        self.logger.error(
                            f"❌ Failed to send performance alert: {response.status}"
                        )
                        return False
        except Exception as e:
            self.logger.error(f"❌ Failed to test performance alert: {e}")
            return False

    async def verify_alert_routing(self) -> bool:
        """Verify alert routing and notification channels."""
        self.logger.info("Verifying alert routing...")

        try:
            async with aiohttp.ClientSession() as session:
                # Check active alerts
                async with session.get(f"{ALERTMANAGER_URL}/api/v2/alerts") as response:
                    if response.status == 200:
                        alerts = await response.json()
                        # v2 API returns alerts directly as array
                        active_alerts = alerts if isinstance(alerts, list) else []

                        constitutional_alerts = [
                            alert
                            for alert in active_alerts
                            if alert.get("labels", {}).get("constitutional_hash")
                            == self.constitutional_hash
                        ]

                        if constitutional_alerts:
                            self.logger.info(
                                f"✅ Found {len(constitutional_alerts)} constitutional alerts"
                            )
                            return True
                        else:
                            self.logger.warning("⚠️ No constitutional alerts found")
                            return False
                    else:
                        self.logger.error(
                            f"❌ Failed to retrieve alerts: {response.status}"
                        )
                        return False
        except Exception as e:
            self.logger.error(f"❌ Failed to verify alert routing: {e}")
            return False

    async def test_dashboard_accessibility(self) -> bool:
        """Test constitutional compliance dashboard accessibility."""
        self.logger.info("Testing dashboard accessibility...")

        try:
            # Use basic auth for Grafana
            auth = aiohttp.BasicAuth("admin", "admin")
            async with aiohttp.ClientSession(auth=auth) as session:
                # Test dashboard API endpoint
                async with session.get(
                    f"{GRAFANA_URL}/api/dashboards/uid/constitutional-compliance"
                ) as response:
                    if response.status == 200:
                        self.logger.info(
                            "✅ Constitutional compliance dashboard accessible"
                        )
                        return True
                    elif response.status == 404:
                        self.logger.warning(
                            "⚠️ Constitutional compliance dashboard not found"
                        )
                        return False
                    else:
                        self.logger.error(
                            f"❌ Dashboard access failed: {response.status}"
                        )
                        return False
        except Exception as e:
            self.logger.error(f"❌ Failed to test dashboard accessibility: {e}")
            return False

    async def run_comprehensive_test(self) -> Dict:
        """Run comprehensive alert notification testing."""
        self.logger.info("🚀 Starting ACGS Alert Notification Testing")
        self.logger.info(f"📋 Constitutional Hash: {self.constitutional_hash}")
        self.logger.info("=" * 60)

        test_results = {
            "constitutional_hash": self.constitutional_hash,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tests": {},
        }

        # Test connectivity
        test_results["tests"][
            "prometheus_connectivity"
        ] = await self.test_prometheus_connectivity()
        test_results["tests"][
            "alertmanager_connectivity"
        ] = await self.test_alertmanager_connectivity()
        test_results["tests"][
            "grafana_connectivity"
        ] = await self.test_grafana_connectivity()

        # Test alert generation
        test_results["tests"][
            "constitutional_violation_alert"
        ] = await self.simulate_constitutional_violation()
        test_results["tests"]["performance_alert"] = await self.test_performance_alert()

        # Wait for alerts to propagate
        self.logger.info("⏳ Waiting for alerts to propagate...")
        await asyncio.sleep(10)

        # Verify alert routing
        test_results["tests"]["alert_routing"] = await self.verify_alert_routing()
        test_results["tests"][
            "dashboard_accessibility"
        ] = await self.test_dashboard_accessibility()

        # Calculate overall success
        successful_tests = sum(1 for result in test_results["tests"].values() if result)
        total_tests = len(test_results["tests"])
        success_rate = (successful_tests / total_tests) * 100

        test_results["summary"] = {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": success_rate,
            "overall_status": "PASS" if success_rate >= 80 else "FAIL",
        }

        self.logger.info("=" * 60)
        self.logger.info(
            f"📊 Test Summary: {successful_tests}/{total_tests} tests passed ({success_rate:.1f}%)"
        )
        self.logger.info(f"🔐 Constitutional Hash: {self.constitutional_hash}")

        if test_results["summary"]["overall_status"] == "PASS":
            self.logger.info("✅ Alert notification testing PASSED")
        else:
            self.logger.error("❌ Alert notification testing FAILED")

        return test_results


async def main():
    """Main function to run alert notification tests."""
    tester = AlertNotificationTester()
    results = await tester.run_comprehensive_test()

    # Save results to file
    with open("alert_notification_test_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n📁 Test results saved to: alert_notification_test_results.json")

    # Exit with appropriate code
    exit_code = 0 if results["summary"]["overall_status"] == "PASS" else 1
    exit(exit_code)


if __name__ == "__main__":
    asyncio.run(main())
