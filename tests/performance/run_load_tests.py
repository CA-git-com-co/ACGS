#!/usr/bin/env python3
"""
ACGS-1 Load Test Execution Script
Phase 2 - Load Testing Tools Configuration

This script orchestrates comprehensive load testing for ACGS-1 using Locust
and custom Python load testing frameworks.

Usage:
    python tests/performance/run_load_tests.py --scenario health_check
    python tests/performance/run_load_tests.py --scenario full_system
    python tests/performance/run_load_tests.py --all-scenarios

Features:
- Automated test scenario execution
- Real-time monitoring integration
- Performance metrics collection
- Comprehensive reporting
- Success criteria validation
"""

import argparse
import asyncio
import json
import logging
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import aiohttp

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from tests.performance.load_test_scenarios import (
    LOAD_TEST_SCENARIOS,
    create_load_test_report,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class LoadTestOrchestrator:
    """Orchestrates load testing execution and monitoring."""

    def __init__(self, results_dir: str = "tests/performance/results"):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.prometheus_url = "http://localhost:9090"
        self.services_health_checked = False

    async def check_system_health(self) -> bool:
        """Check if all ACGS services are healthy before load testing."""
        logger.info("🏥 Checking system health before load testing...")

        services = [
            ("auth", 8000),
            ("ac", 8001),
            ("integrity", 8002),
            ("fv", 8003),
            ("gs", 8004),
            ("pgc", 8005),
            ("ec", 8006),
        ]

        healthy_services = 0
        total_services = len(services)

        async with aiohttp.ClientSession() as session:
            for service_name, port in services:
                try:
                    async with session.get(
                        f"http://localhost:{port}/health", timeout=5
                    ) as response:
                        if response.status == 200:
                            healthy_services += 1
                            logger.info(f"✅ {service_name} service healthy")
                        else:
                            logger.warning(
                                f"⚠️ {service_name} service unhealthy: {response.status}"
                            )
                except Exception as e:
                    logger.error(f"❌ {service_name} service unreachable: {e}")

        health_percentage = (healthy_services / total_services) * 100
        logger.info(
            f"System health: {healthy_services}/{total_services} services ({health_percentage:.1f}%)"
        )

        if health_percentage < 85:
            logger.error("❌ System health insufficient for load testing")
            return False

        self.services_health_checked = True
        return True

    def run_locust_test(self, scenario_name: str, user_class: str) -> dict[str, Any]:
        """Run Locust load test for specific scenario."""
        scenario = LOAD_TEST_SCENARIOS[scenario_name]

        logger.info(f"🚀 Starting Locust test: {scenario.name}")
        logger.info(
            f"Target users: {scenario.target_users}, Duration: {scenario.duration_seconds}s"
        )

        # Create Locust command
        locust_file = "tests/performance/load_test_scenarios.py"
        cmd = [
            "locust",
            "-f",
            locust_file,
            user_class,
            "--users",
            str(scenario.target_users),
            "--spawn-rate",
            str(scenario.spawn_rate),
            "--run-time",
            f"{scenario.duration_seconds}s",
            "--headless",
            "--csv",
            str(self.results_dir / f"{scenario_name}_results"),
            "--html",
            str(self.results_dir / f"{scenario_name}_report.html"),
        ]

        try:
            # Run Locust test
            start_time = time.time()
            result = subprocess.run(
                cmd,
                check=False,
                capture_output=True,
                text=True,
                timeout=scenario.duration_seconds + 120,
            )
            end_time = time.time()

            # Parse results
            stats = self._parse_locust_results(scenario_name)
            stats["execution_time"] = end_time - start_time
            stats["exit_code"] = result.returncode

            if result.returncode == 0:
                logger.info(f"✅ Locust test completed successfully: {scenario_name}")
            else:
                logger.error(f"❌ Locust test failed: {scenario_name}")
                logger.error(f"Error output: {result.stderr}")

            return stats

        except subprocess.TimeoutExpired:
            logger.error(f"❌ Locust test timed out: {scenario_name}")
            return {
                "error": "timeout",
                "execution_time": scenario.duration_seconds + 120,
            }
        except Exception as e:
            logger.error(f"❌ Locust test execution failed: {e}")
            return {"error": str(e), "execution_time": 0}

    def _parse_locust_results(self, scenario_name: str) -> dict[str, Any]:
        """Parse Locust CSV results into structured data."""
        stats_file = self.results_dir / f"{scenario_name}_results_stats.csv"

        if not stats_file.exists():
            logger.warning(f"Stats file not found: {stats_file}")
            return {"error": "stats_file_not_found"}

        try:
            import pandas as pd

            df = pd.read_csv(stats_file)

            # Calculate key metrics
            total_requests = df["Request Count"].sum()
            total_failures = df["Failure Count"].sum()
            success_rate = (
                ((total_requests - total_failures) / total_requests * 100)
                if total_requests > 0
                else 0
            )
            error_rate = (
                (total_failures / total_requests * 100) if total_requests > 0 else 0
            )

            # Get response time percentiles
            avg_response_time = df["Average Response Time"].mean()
            response_time_95th = (
                df["95%"].mean() if "95%" in df.columns else avg_response_time * 1.5
            )

            return {
                "total_requests": int(total_requests),
                "total_failures": int(total_failures),
                "success_rate": round(success_rate, 2),
                "error_rate": round(error_rate, 2),
                "average_response_time": round(avg_response_time, 2),
                "response_time_95th_percentile": round(response_time_95th, 2),
                "requests_per_second": round(df["Requests/s"].mean(), 2),
            }

        except Exception as e:
            logger.error(f"Error parsing Locust results: {e}")
            return {"error": f"parsing_failed: {e}"}

    async def collect_prometheus_metrics(self, duration_seconds: int) -> dict[str, Any]:
        """Collect Prometheus metrics during load test."""
        logger.info("📊 Collecting Prometheus metrics...")

        metrics = {}

        try:
            # Query Prometheus for key metrics
            queries = {
                "cpu_usage": 'avg(100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100))',
                "memory_usage": "avg((1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100)",
                "http_requests_total": "sum(rate(http_requests_total[5m]))",
                "http_request_duration": "histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))",
            }

            async with aiohttp.ClientSession() as session:
                for metric_name, query in queries.items():
                    try:
                        url = f"{self.prometheus_url}/api/v1/query"
                        params = {"query": query}

                        async with session.get(url, params=params) as response:
                            if response.status == 200:
                                data = await response.json()
                                if data.get("status") == "success" and data.get(
                                    "data", {}
                                ).get("result"):
                                    value = data["data"]["result"][0]["value"][1]
                                    metrics[metric_name] = float(value)
                                else:
                                    metrics[metric_name] = 0.0
                            else:
                                logger.warning(
                                    f"Failed to query {metric_name}: {response.status}"
                                )
                                metrics[metric_name] = 0.0
                    except Exception as e:
                        logger.warning(f"Error querying {metric_name}: {e}")
                        metrics[metric_name] = 0.0

        except Exception as e:
            logger.error(f"Error collecting Prometheus metrics: {e}")

        return metrics

    async def run_scenario(self, scenario_name: str) -> dict[str, Any]:
        """Run complete load test scenario with monitoring."""
        if not self.services_health_checked:
            if not await self.check_system_health():
                return {"error": "system_health_check_failed"}

        scenario = LOAD_TEST_SCENARIOS[scenario_name]
        logger.info(f"🎯 Executing load test scenario: {scenario.name}")

        # Map scenario to user class
        user_class_mapping = {
            "health_check": "ACGSHealthCheckUser",
            "authentication_flow": "ACGSAuthenticationUser",
            "governance_workflow": "ACGSGovernanceWorkflowUser",
            "policy_synthesis": "ACGSPolicySynthesisUser",
            "full_system": "ACGSHealthCheckUser",  # Use health check for full system baseline
        }

        user_class = user_class_mapping.get(scenario_name, "ACGSHealthCheckUser")

        # Start monitoring
        monitoring_task = asyncio.create_task(
            self.collect_prometheus_metrics(scenario.duration_seconds)
        )

        # Run load test
        load_test_stats = self.run_locust_test(scenario_name, user_class)

        # Wait for monitoring to complete
        prometheus_metrics = await monitoring_task

        # Combine results
        results = {
            "load_test_stats": load_test_stats,
            "prometheus_metrics": prometheus_metrics,
            "scenario_config": {
                "name": scenario.name,
                "target_users": scenario.target_users,
                "duration_seconds": scenario.duration_seconds,
                "spawn_rate": scenario.spawn_rate,
            },
        }

        # Generate report
        report = create_load_test_report(scenario_name, load_test_stats)
        report["prometheus_metrics"] = prometheus_metrics

        # Save report
        report_file = self.results_dir / f"{scenario_name}_comprehensive_report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"📋 Report saved: {report_file}")

        return report

    async def run_all_scenarios(self) -> dict[str, Any]:
        """Run all load test scenarios sequentially."""
        logger.info("🚀 Running all load test scenarios...")

        all_results = {}

        # Check system health once
        if not await self.check_system_health():
            return {"error": "system_health_check_failed"}

        # Run scenarios in order of increasing complexity
        scenario_order = [
            "health_check",
            "authentication_flow",
            "policy_synthesis",
            "governance_workflow",
        ]

        for scenario_name in scenario_order:
            logger.info(f"\n{'=' * 60}")
            logger.info(f"Running scenario: {scenario_name}")
            logger.info(f"{'=' * 60}")

            result = await self.run_scenario(scenario_name)
            all_results[scenario_name] = result

            # Brief pause between scenarios
            await asyncio.sleep(30)

        # Generate summary report
        summary_report = {
            "execution_timestamp": datetime.now(timezone.utc).isoformat(),
            "total_scenarios": len(scenario_order),
            "scenarios_executed": len(all_results),
            "results": all_results,
        }

        summary_file = self.results_dir / "load_test_summary.json"
        with open(summary_file, "w") as f:
            json.dump(summary_report, f, indent=2)

        logger.info(f"📋 Summary report saved: {summary_file}")

        return summary_report


async def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description="ACGS-1 Load Testing Orchestrator")
    parser.add_argument(
        "--scenario",
        choices=list(LOAD_TEST_SCENARIOS.keys()),
        help="Specific scenario to run",
    )
    parser.add_argument(
        "--all-scenarios", action="store_true", help="Run all scenarios sequentially"
    )
    parser.add_argument(
        "--results-dir",
        default="tests/performance/results",
        help="Directory to save results",
    )

    args = parser.parse_args()

    orchestrator = LoadTestOrchestrator(args.results_dir)

    if args.all_scenarios:
        results = await orchestrator.run_all_scenarios()
    elif args.scenario:
        results = await orchestrator.run_scenario(args.scenario)
    else:
        logger.error("Please specify --scenario or --all-scenarios")
        return

    # Print summary
    print("\n" + "=" * 60)
    print("LOAD TEST EXECUTION SUMMARY")
    print("=" * 60)

    if "error" in results:
        print(f"❌ Execution failed: {results['error']}")
    else:
        print("✅ Execution completed successfully")
        if args.scenario:
            stats = results.get("load_test_stats", {})
            print(f"Success Rate: {stats.get('success_rate', 0):.2f}%")
            print(
                f"95th Percentile Response Time: {stats.get('response_time_95th_percentile', 0):.2f}ms"
            )
            print(f"Requests/Second: {stats.get('requests_per_second', 0):.2f}")


if __name__ == "__main__":
    asyncio.run(main())
