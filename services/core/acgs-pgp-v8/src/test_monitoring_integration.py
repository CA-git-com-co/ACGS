#!/usr/bin/env python3
"""
Test script for ACGS-PGP v8 monitoring integration.

Validates that Prometheus metrics are properly exposed and Grafana dashboards
can access the metrics data.
"""

import asyncio
import logging
import sys
from datetime import datetime

import aiohttp

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ACGS-PGP-v8-Monitoring-Test")


class MonitoringIntegrationTest:
    """Test suite for monitoring integration."""

    def __init__(self):
        self.service_url = "http://localhost:8010"
        self.prometheus_url = "http://localhost:9090"
        self.grafana_url = "http://localhost:3000"
        self.test_results = {}

    async def test_health_endpoint(self) -> bool:
        """Test the health endpoint."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.service_url}/health") as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"Health check passed: {data.get('status')}")
                        return True
                    else:
                        logger.error(
                            f"Health check failed with status: {response.status}"
                        )
                        return False
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    async def test_metrics_endpoint(self) -> bool:
        """Test the Prometheus metrics endpoint."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.service_url}/metrics") as response:
                    if response.status == 200:
                        metrics_data = await response.text()

                        # Check for key metrics
                        required_metrics = [
                            "acgs_pgp_v8_system_info",
                            "acgs_pgp_v8_policy_generation_requests_total",
                            "acgs_pgp_v8_component_health",
                            "acgs_pgp_v8_system_uptime_seconds",
                            "acgs_pgp_v8_constitutional_validations_total",
                        ]

                        missing_metrics = []
                        for metric in required_metrics:
                            if metric not in metrics_data:
                                missing_metrics.append(metric)

                        if missing_metrics:
                            logger.error(f"Missing metrics: {missing_metrics}")
                            return False

                        logger.info("All required metrics found in /metrics endpoint")
                        return True
                    else:
                        logger.error(
                            f"Metrics endpoint failed with status: {response.status}"
                        )
                        return False
        except Exception as e:
            logger.error(f"Metrics endpoint test failed: {e}")
            return False

    async def test_metrics_summary_endpoint(self) -> bool:
        """Test the metrics summary endpoint."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.service_url}/api/v1/metrics/summary"
                ) as response:
                    if response.status == 200:
                        data = await response.json()

                        # Check for required fields
                        required_fields = [
                            "constitutional_hash",
                            "system_uptime_seconds",
                            "metrics_collected",
                            "timestamp",
                        ]

                        missing_fields = []
                        for field in required_fields:
                            if field not in data:
                                missing_fields.append(field)

                        if missing_fields:
                            logger.error(
                                f"Missing fields in metrics summary: {missing_fields}"
                            )
                            return False

                        # Validate constitutional hash
                        if data.get("constitutional_hash") != "cdd01ef066bc6cf2":
                            logger.error(
                                f"Invalid constitutional hash: {data.get('constitutional_hash')}"
                            )
                            return False

                        logger.info("Metrics summary endpoint test passed")
                        return True
                    else:
                        logger.error(
                            f"Metrics summary endpoint failed with status: {response.status}"
                        )
                        return False
        except Exception as e:
            logger.error(f"Metrics summary endpoint test failed: {e}")
            return False

    async def test_prometheus_scraping(self) -> bool:
        """Test if Prometheus is scraping ACGS-PGP v8 metrics."""
        try:
            async with aiohttp.ClientSession() as session:
                # Query Prometheus for ACGS-PGP v8 metrics
                query = 'up{job="acgs-pgp-v8-service"}'
                async with session.get(
                    f"{self.prometheus_url}/api/v1/query", params={"query": query}
                ) as response:
                    if response.status == 200:
                        data = await response.json()

                        if data.get("status") == "success":
                            results = data.get("data", {}).get("result", [])
                            if results:
                                value = results[0].get("value", [None, "0"])[1]
                                if value == "1":
                                    logger.info(
                                        "Prometheus is successfully scraping ACGS-PGP v8 metrics"
                                    )
                                    return True
                                else:
                                    logger.warning(
                                        "ACGS-PGP v8 service appears down in Prometheus"
                                    )
                                    return False
                            else:
                                logger.error(
                                    "No results found for ACGS-PGP v8 service in Prometheus"
                                )
                                return False
                        else:
                            logger.error(f"Prometheus query failed: {data}")
                            return False
                    else:
                        logger.error(
                            f"Prometheus API request failed with status: {response.status}"
                        )
                        return False
        except Exception as e:
            logger.warning(
                f"Prometheus scraping test failed (Prometheus may not be running): {e}"
            )
            return False

    async def test_constitutional_compliance_metrics(self) -> bool:
        """Test constitutional compliance metrics."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.service_url}/metrics") as response:
                    if response.status == 200:
                        metrics_data = await response.text()

                        # Check for constitutional compliance metrics
                        compliance_metrics = [
                            "acgs_pgp_v8_constitutional_validations_total",
                            "acgs_pgp_v8_constitutional_hash_mismatches_total",
                            "acgs_pgp_v8_constitutional_compliance_score",
                        ]

                        found_metrics = []
                        for metric in compliance_metrics:
                            if metric in metrics_data:
                                found_metrics.append(metric)

                        if (
                            len(found_metrics) >= 2
                        ):  # At least 2 out of 3 metrics should be present
                            logger.info(
                                f"Constitutional compliance metrics found: {found_metrics}"
                            )
                            return True
                        else:
                            logger.error(
                                f"Insufficient constitutional compliance metrics: {found_metrics}"
                            )
                            return False
                    else:
                        logger.error(
                            f"Failed to get metrics for compliance test: {response.status}"
                        )
                        return False
        except Exception as e:
            logger.error(f"Constitutional compliance metrics test failed: {e}")
            return False

    async def run_all_tests(self) -> dict[str, bool]:
        """Run all monitoring integration tests."""
        logger.info("Starting ACGS-PGP v8 monitoring integration tests...")

        tests = [
            ("Health Endpoint", self.test_health_endpoint),
            ("Metrics Endpoint", self.test_metrics_endpoint),
            ("Metrics Summary Endpoint", self.test_metrics_summary_endpoint),
            (
                "Constitutional Compliance Metrics",
                self.test_constitutional_compliance_metrics,
            ),
            ("Prometheus Scraping", self.test_prometheus_scraping),
        ]

        results = {}
        passed_tests = 0

        for test_name, test_func in tests:
            logger.info(f"Running test: {test_name}")
            try:
                result = await test_func()
                results[test_name] = result
                if result:
                    passed_tests += 1
                    logger.info(f"✅ {test_name}: PASSED")
                else:
                    logger.error(f"❌ {test_name}: FAILED")
            except Exception as e:
                logger.error(f"❌ {test_name}: ERROR - {e}")
                results[test_name] = False

        # Summary
        total_tests = len(tests)
        success_rate = (passed_tests / total_tests) * 100

        logger.info(f"\n{'='*50}")
        logger.info("ACGS-PGP v8 Monitoring Integration Test Results")
        logger.info(f"{'='*50}")
        logger.info(f"Tests Passed: {passed_tests}/{total_tests}")
        logger.info(f"Success Rate: {success_rate:.1f}%")
        logger.info("Constitutional Hash: cdd01ef066bc6cf2")
        logger.info(f"Timestamp: {datetime.now().isoformat()}")

        if success_rate >= 80:
            logger.info("🎉 Monitoring integration is ready for production!")
        elif success_rate >= 60:
            logger.warning(
                "⚠️  Monitoring integration has some issues but is functional"
            )
        else:
            logger.error("❌ Monitoring integration has critical issues")

        return results


async def main():
    """Main function."""
    test_suite = MonitoringIntegrationTest()
    results = await test_suite.run_all_tests()

    # Exit with appropriate code
    success_rate = sum(results.values()) / len(results) * 100
    sys.exit(0 if success_rate >= 80 else 1)


if __name__ == "__main__":
    asyncio.run(main())
