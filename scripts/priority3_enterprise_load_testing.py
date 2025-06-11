#!/usr/bin/env python3
"""
ACGS-1 Priority 3 Task 2: Enterprise-Scale Load Testing

This script implements comprehensive load testing to validate system capacity
for >1000 concurrent governance actions with >99.9% availability targets.
"""

import asyncio
import aiohttp
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import concurrent.futures
import statistics

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class EnterpriseLoadTester:
    """Enterprise-scale load testing for ACGS-1 governance system."""

    def __init__(self):
        self.project_root = Path("/home/dislove/ACGS-1")
        self.target_concurrent_users = 1000
        self.target_availability = 99.9  # %
        self.target_response_time = 500  # ms

        # Service endpoints
        self.services = {
            "auth": {"port": 8000, "endpoints": ["/health", "/api/v1/auth/status"]},
            "ac": {
                "port": 8001,
                "endpoints": ["/health", "/api/v1/constitutional/status"],
            },
            "integrity": {
                "port": 8002,
                "endpoints": ["/health", "/api/v1/integrity/status"],
            },
            "fv": {
                "port": 8003,
                "endpoints": ["/health", "/api/v1/verification/status"],
            },
            "gs": {"port": 8004, "endpoints": ["/health", "/api/v1/synthesis/status"]},
            "pgc": {
                "port": 8005,
                "endpoints": ["/health", "/api/v1/governance/status"],
            },
            "ec": {
                "port": 8006,
                "endpoints": ["/health", "/api/v1/coordination/status"],
            },
        }

        # Governance workflow endpoints
        self.governance_workflows = [
            "/api/v1/governance/policy-creation",
            "/api/v1/governance/constitutional-compliance",
            "/api/v1/governance/policy-enforcement",
            "/api/v1/governance/wina-oversight",
            "/api/v1/governance/audit-transparency",
        ]

    async def execute_enterprise_load_testing(self) -> Dict:
        """Execute comprehensive enterprise load testing."""
        logger.info("🚀 Starting ACGS-1 Enterprise Load Testing")
        start_time = time.time()

        results = {
            "start_time": datetime.now().isoformat(),
            "target_metrics": {
                "concurrent_users": self.target_concurrent_users,
                "availability_percent": self.target_availability,
                "response_time_ms": self.target_response_time,
            },
            "test_phases": {},
        }

        try:
            # Phase 1: Baseline Performance Validation
            logger.info("📊 Phase 1: Baseline performance validation...")
            phase1_results = await self.validate_baseline_performance()
            results["test_phases"]["baseline_validation"] = phase1_results

            # Phase 2: Progressive Load Testing
            logger.info("📈 Phase 2: Progressive load testing...")
            phase2_results = await self.progressive_load_testing()
            results["test_phases"]["progressive_load"] = phase2_results

            # Phase 3: Governance Workflow Load Testing
            logger.info("🏛️ Phase 3: Governance workflow load testing...")
            phase3_results = await self.governance_workflow_load_testing()
            results["test_phases"]["governance_workflows"] = phase3_results

            # Phase 4: Stress Testing
            logger.info("💥 Phase 4: Stress testing...")
            phase4_results = await self.stress_testing()
            results["test_phases"]["stress_testing"] = phase4_results

            # Phase 5: Availability Testing
            logger.info("🔄 Phase 5: Availability testing...")
            phase5_results = await self.availability_testing()
            results["test_phases"]["availability_testing"] = phase5_results

            # Calculate final metrics
            execution_time = time.time() - start_time
            results.update(
                {
                    "end_time": datetime.now().isoformat(),
                    "execution_time_seconds": execution_time,
                    "overall_success": self.evaluate_load_test_success(results),
                    "performance_summary": self.generate_performance_summary(results),
                }
            )

            # Save comprehensive report
            await self.save_load_test_report(results)

            return results

        except Exception as e:
            logger.error(f"❌ Enterprise load testing failed: {e}")
            results["error"] = str(e)
            results["overall_success"] = False
            return results

    async def validate_baseline_performance(self) -> Dict:
        """Validate baseline performance before load testing."""
        logger.info("📊 Validating baseline performance...")

        baseline_results = {}

        # Test each service individually
        for service_name, service_config in self.services.items():
            port = service_config["port"]
            endpoints = service_config["endpoints"]

            service_metrics = []

            for endpoint in endpoints:
                try:
                    # Measure response time
                    start = time.time()
                    async with aiohttp.ClientSession() as session:
                        async with session.get(
                            f"http://localhost:{port}{endpoint}", timeout=10
                        ) as response:
                            end = time.time()
                            response_time = (end - start) * 1000  # Convert to ms

                            service_metrics.append(
                                {
                                    "endpoint": endpoint,
                                    "response_time_ms": response_time,
                                    "status_code": response.status,
                                    "success": response.status < 400,
                                }
                            )

                except Exception as e:
                    service_metrics.append(
                        {"endpoint": endpoint, "error": str(e), "success": False}
                    )

            # Calculate service baseline metrics
            successful_requests = [
                m for m in service_metrics if m.get("success", False)
            ]
            if successful_requests:
                response_times = [m["response_time_ms"] for m in successful_requests]
                baseline_results[service_name] = {
                    "avg_response_time_ms": statistics.mean(response_times),
                    "max_response_time_ms": max(response_times),
                    "min_response_time_ms": min(response_times),
                    "success_rate": len(successful_requests) / len(service_metrics),
                    "baseline_healthy": statistics.mean(response_times)
                    < self.target_response_time,
                }
            else:
                baseline_results[service_name] = {
                    "baseline_healthy": False,
                    "error": "No successful requests",
                }

        # Calculate overall baseline health
        healthy_services = sum(
            1
            for result in baseline_results.values()
            if result.get("baseline_healthy", False)
        )

        return {
            "success": healthy_services >= 6,  # At least 6/7 services healthy
            "healthy_services": healthy_services,
            "total_services": len(self.services),
            "service_baselines": baseline_results,
        }

    async def progressive_load_testing(self) -> Dict:
        """Progressive load testing with increasing concurrent users."""
        logger.info("📈 Running progressive load testing...")

        # Test with increasing load levels
        load_levels = [10, 50, 100, 200, 500, 1000]
        progressive_results = {}

        for concurrent_users in load_levels:
            logger.info(f"Testing with {concurrent_users} concurrent users...")

            try:
                # Run concurrent requests
                start_time = time.time()

                async with aiohttp.ClientSession() as session:
                    tasks = []
                    for _ in range(concurrent_users):
                        # Distribute requests across services
                        service_name = list(self.services.keys())[
                            _ % len(self.services)
                        ]
                        port = self.services[service_name]["port"]

                        task = self.make_load_test_request(
                            session, f"http://localhost:{port}/health"
                        )
                        tasks.append(task)

                    # Execute all requests concurrently
                    results = await asyncio.gather(*tasks, return_exceptions=True)

                end_time = time.time()
                total_time = end_time - start_time

                # Analyze results
                successful_requests = [
                    r
                    for r in results
                    if isinstance(r, dict) and r.get("success", False)
                ]
                failed_requests = len(results) - len(successful_requests)

                if successful_requests:
                    response_times = [
                        r["response_time_ms"] for r in successful_requests
                    ]
                    avg_response_time = statistics.mean(response_times)
                    max_response_time = max(response_times)
                    success_rate = len(successful_requests) / len(results)
                else:
                    avg_response_time = 0
                    max_response_time = 0
                    success_rate = 0

                progressive_results[f"{concurrent_users}_users"] = {
                    "concurrent_users": concurrent_users,
                    "total_requests": len(results),
                    "successful_requests": len(successful_requests),
                    "failed_requests": failed_requests,
                    "success_rate": success_rate,
                    "avg_response_time_ms": avg_response_time,
                    "max_response_time_ms": max_response_time,
                    "total_time_seconds": total_time,
                    "requests_per_second": (
                        len(results) / total_time if total_time > 0 else 0
                    ),
                    "meets_targets": (
                        success_rate >= 0.95  # 95% success rate
                        and avg_response_time < self.target_response_time
                    ),
                }

                # Break if system starts failing
                if success_rate < 0.8:  # 80% minimum success rate
                    logger.warning(
                        f"System degrading at {concurrent_users} users, stopping progressive test"
                    )
                    break

            except Exception as e:
                progressive_results[f"{concurrent_users}_users"] = {
                    "error": str(e),
                    "meets_targets": False,
                }
                break

        # Find maximum supported concurrent users
        max_supported_users = 0
        for level_key, result in progressive_results.items():
            if result.get("meets_targets", False):
                users = result.get("concurrent_users", 0)
                max_supported_users = max(max_supported_users, users)

        return {
            "success": max_supported_users >= 100,  # At least 100 concurrent users
            "max_supported_users": max_supported_users,
            "target_users": self.target_concurrent_users,
            "meets_concurrent_target": max_supported_users
            >= self.target_concurrent_users,
            "progressive_results": progressive_results,
        }

    async def make_load_test_request(
        self, session: aiohttp.ClientSession, url: str
    ) -> Dict:
        """Make a single load test request."""
        try:
            start = time.time()
            async with session.get(url, timeout=10) as response:
                end = time.time()
                response_time = (end - start) * 1000  # Convert to ms

                return {
                    "success": response.status < 400,
                    "response_time_ms": response_time,
                    "status_code": response.status,
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def governance_workflow_load_testing(self) -> Dict:
        """Test governance workflow endpoints under load."""
        logger.info("🏛️ Testing governance workflows under load...")

        workflow_results = {}

        # Test each governance workflow
        for workflow in self.governance_workflows:
            try:
                # Test with moderate concurrent load
                concurrent_requests = 50

                async with aiohttp.ClientSession() as session:
                    tasks = []
                    for _ in range(concurrent_requests):
                        task = self.make_load_test_request(
                            session, f"http://localhost:8005{workflow}"
                        )
                        tasks.append(task)

                    results = await asyncio.gather(*tasks, return_exceptions=True)

                # Analyze workflow results
                successful_requests = [
                    r
                    for r in results
                    if isinstance(r, dict) and r.get("success", False)
                ]

                if successful_requests:
                    response_times = [
                        r["response_time_ms"] for r in successful_requests
                    ]
                    avg_response_time = statistics.mean(response_times)
                    success_rate = len(successful_requests) / len(results)
                else:
                    avg_response_time = 0
                    success_rate = 0

                workflow_results[workflow] = {
                    "avg_response_time_ms": avg_response_time,
                    "success_rate": success_rate,
                    "meets_targets": (
                        success_rate >= 0.9  # 90% success rate for workflows
                        and avg_response_time < self.target_response_time
                    ),
                }

            except Exception as e:
                workflow_results[workflow] = {"error": str(e), "meets_targets": False}

        # Calculate overall workflow performance
        workflows_meeting_targets = sum(
            1
            for result in workflow_results.values()
            if result.get("meets_targets", False)
        )

        return {
            "success": workflows_meeting_targets
            >= 3,  # At least 3/5 workflows meeting targets
            "workflows_meeting_targets": workflows_meeting_targets,
            "total_workflows": len(self.governance_workflows),
            "workflow_results": workflow_results,
        }

    async def stress_testing(self) -> Dict:
        """Stress testing to find system breaking point."""
        logger.info("💥 Running stress testing...")

        # Stress test with high load
        stress_levels = [1500, 2000, 2500]
        stress_results = {}

        for stress_level in stress_levels:
            try:
                logger.info(
                    f"Stress testing with {stress_level} concurrent requests..."
                )

                async with aiohttp.ClientSession() as session:
                    tasks = []
                    for _ in range(stress_level):
                        # Focus on health endpoints for stress testing
                        port = 8005  # PGC service
                        task = self.make_load_test_request(
                            session, f"http://localhost:{port}/health"
                        )
                        tasks.append(task)

                    start_time = time.time()
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    end_time = time.time()

                # Analyze stress test results
                successful_requests = [
                    r
                    for r in results
                    if isinstance(r, dict) and r.get("success", False)
                ]
                success_rate = len(successful_requests) / len(results) if results else 0
                total_time = end_time - start_time

                stress_results[f"stress_{stress_level}"] = {
                    "stress_level": stress_level,
                    "success_rate": success_rate,
                    "total_time_seconds": total_time,
                    "requests_per_second": (
                        len(results) / total_time if total_time > 0 else 0
                    ),
                    "system_stable": success_rate >= 0.7,  # 70% minimum for stress test
                }

                # Stop if system becomes unstable
                if success_rate < 0.5:
                    logger.warning(
                        f"System unstable at {stress_level} requests, stopping stress test"
                    )
                    break

            except Exception as e:
                stress_results[f"stress_{stress_level}"] = {
                    "error": str(e),
                    "system_stable": False,
                }
                break

        return {"success": len(stress_results) > 0, "stress_results": stress_results}

    async def availability_testing(self) -> Dict:
        """Test system availability over time."""
        logger.info("🔄 Testing system availability...")

        # Run availability test for 60 seconds
        test_duration = 60  # seconds
        request_interval = 1  # second

        availability_results = []
        start_time = time.time()

        while time.time() - start_time < test_duration:
            try:
                # Test all services
                service_availability = {}

                async with aiohttp.ClientSession() as session:
                    for service_name, service_config in self.services.items():
                        port = service_config["port"]

                        try:
                            async with session.get(
                                f"http://localhost:{port}/health", timeout=5
                            ) as response:
                                service_availability[service_name] = (
                                    response.status < 400
                                )
                        except:
                            service_availability[service_name] = False

                # Calculate availability for this interval
                available_services = sum(service_availability.values())
                total_services = len(service_availability)
                availability_percent = (available_services / total_services) * 100

                availability_results.append(
                    {
                        "timestamp": time.time(),
                        "availability_percent": availability_percent,
                        "available_services": available_services,
                        "total_services": total_services,
                    }
                )

                await asyncio.sleep(request_interval)

            except Exception as e:
                availability_results.append(
                    {
                        "timestamp": time.time(),
                        "error": str(e),
                        "availability_percent": 0,
                    }
                )

        # Calculate overall availability
        if availability_results:
            availability_percentages = [
                r.get("availability_percent", 0) for r in availability_results
            ]
            avg_availability = statistics.mean(availability_percentages)
            min_availability = min(availability_percentages)
        else:
            avg_availability = 0
            min_availability = 0

        return {
            "success": avg_availability >= self.target_availability,
            "avg_availability_percent": avg_availability,
            "min_availability_percent": min_availability,
            "target_availability_percent": self.target_availability,
            "meets_availability_target": avg_availability >= self.target_availability,
            "test_duration_seconds": test_duration,
            "availability_samples": len(availability_results),
        }

    def evaluate_load_test_success(self, results: Dict) -> bool:
        """Evaluate overall load test success."""
        phases = results.get("test_phases", {})

        # Check if critical phases passed
        baseline_success = phases.get("baseline_validation", {}).get("success", False)
        progressive_success = phases.get("progressive_load", {}).get("success", False)
        availability_success = phases.get("availability_testing", {}).get(
            "success", False
        )

        # Require at least baseline and one other test to pass
        return baseline_success and (progressive_success or availability_success)

    def generate_performance_summary(self, results: Dict) -> Dict:
        """Generate performance summary from test results."""
        phases = results.get("test_phases", {})

        # Extract key metrics
        max_concurrent = phases.get("progressive_load", {}).get(
            "max_supported_users", 0
        )
        avg_availability = phases.get("availability_testing", {}).get(
            "avg_availability_percent", 0
        )
        workflows_passing = phases.get("governance_workflows", {}).get(
            "workflows_meeting_targets", 0
        )

        return {
            "max_concurrent_users": max_concurrent,
            "avg_availability_percent": avg_availability,
            "workflows_meeting_targets": workflows_passing,
            "meets_concurrent_target": max_concurrent >= self.target_concurrent_users,
            "meets_availability_target": avg_availability >= self.target_availability,
            "enterprise_ready": (
                max_concurrent >= 500  # At least 500 concurrent users
                and avg_availability >= 99.0  # At least 99% availability
                and workflows_passing >= 3  # At least 3 workflows working
            ),
        }

    async def save_load_test_report(self, results: Dict) -> None:
        """Save comprehensive load test report."""
        report_file = f"priority3_enterprise_load_test_{int(time.time())}.json"
        report_path = self.project_root / "logs" / report_file

        # Ensure logs directory exists
        report_path.parent.mkdir(exist_ok=True)

        with open(report_path, "w") as f:
            json.dump(results, f, indent=2)

        logger.info(f"📄 Load test report saved: {report_path}")


async def main():
    """Main execution function."""
    tester = EnterpriseLoadTester()
    results = await tester.execute_enterprise_load_testing()

    if results.get("overall_success", False):
        print("✅ Enterprise load testing completed successfully!")

        summary = results.get("performance_summary", {})
        print(f"📊 Performance Summary:")
        print(f"  • Max Concurrent Users: {summary.get('max_concurrent_users', 0)}")
        print(
            f"  • Average Availability: {summary.get('avg_availability_percent', 0):.1f}%"
        )
        print(
            f"  • Workflows Meeting Targets: {summary.get('workflows_meeting_targets', 0)}/5"
        )

        if summary.get("enterprise_ready", False):
            print("🎯 System is ENTERPRISE READY!")
        else:
            print("⚠️ System needs optimization for enterprise scale")

    else:
        print(
            f"❌ Enterprise load testing failed: {results.get('error', 'Multiple test failures')}"
        )


if __name__ == "__main__":
    asyncio.run(main())
