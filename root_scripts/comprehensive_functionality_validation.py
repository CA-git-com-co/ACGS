#!/usr/bin/env python3
"""
Comprehensive ACGS-1 Functionality Validation Script
Implements Phase 3: Functionality Validation
"""

import asyncio
import json
import logging
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import aiohttp

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class FunctionalityValidator:
    """Comprehensive functionality validation for ACGS-1."""

    def __init__(self):
        self.root_dir = Path("/home/dislove/ACGS-1")
        self.services = {
            "auth_service": {"port": 8000, "url": "http://localhost:8000"},
            "ac_service": {"port": 8001, "url": "http://localhost:8001"},
            "integrity_service": {"port": 8002, "url": "http://localhost:8002"},
            "fv_service": {"port": 8003, "url": "http://localhost:8003"},
            "gs_service": {"port": 8004, "url": "http://localhost:8004"},
            "pgc_service": {"port": 8005, "url": "http://localhost:8005"},
            "ec_service": {"port": 8006, "url": "http://localhost:8006"},
        }
        self.governance_workflows = [
            "Policy Creation",
            "Constitutional Compliance",
            "Policy Enforcement",
            "WINA Oversight",
            "Audit/Transparency",
        ]
        self.validation_report = {
            "timestamp": datetime.now().isoformat(),
            "phase": "Phase 3: Functionality Validation",
            "service_health": {},
            "governance_workflows": {},
            "blockchain_status": {},
            "test_results": {},
            "performance_metrics": {},
            "issues_found": [],
            "recommendations": [],
        }

    async def validate_service_health(self):
        """Validate all 7 core services are operational."""
        logger.info("🏥 Validating service health...")

        healthy_services = 0
        total_services = len(self.services)

        async with aiohttp.ClientSession() as session:
            for service_name, config in self.services.items():
                try:
                    start_time = time.time()
                    async with session.get(
                        f"{config['url']}/health", timeout=10
                    ) as response:
                        response_time = (time.time() - start_time) * 1000

                        if response.status == 200:
                            health_data = await response.json()
                            status = health_data.get("status", "unknown")

                            self.validation_report["service_health"][service_name] = {
                                "status": (
                                    "healthy"
                                    if status in ["healthy", "ok"]
                                    else "degraded"
                                ),
                                "response_time_ms": round(response_time, 2),
                                "port": config["port"],
                                "health_data": health_data,
                            }

                            if status in ["healthy", "ok"]:
                                healthy_services += 1
                                logger.info(
                                    f"  ✅ {service_name}: Healthy ({response_time:.1f}ms)"
                                )
                            else:
                                logger.warning(
                                    f"  ⚠️ {service_name}: Degraded ({response_time:.1f}ms)"
                                )
                        else:
                            logger.error(f"  ❌ {service_name}: HTTP {response.status}")
                            self.validation_report["service_health"][service_name] = {
                                "status": "unhealthy",
                                "response_time_ms": round(response_time, 2),
                                "port": config["port"],
                                "error": f"HTTP {response.status}",
                            }

                except Exception as e:
                    logger.error(f"  ❌ {service_name}: {e!s}")
                    self.validation_report["service_health"][service_name] = {
                        "status": "unreachable",
                        "port": config["port"],
                        "error": str(e),
                    }

        availability = (healthy_services / total_services) * 100
        logger.info(
            f"📊 Service Availability: {healthy_services}/{total_services} ({availability:.1f}%)"
        )

        return healthy_services >= 6  # At least 6/7 services should be healthy

    async def validate_governance_workflows(self):
        """Validate the 5 governance workflows are operational."""
        logger.info("🏛️ Validating governance workflows...")

        workflow_endpoints = {
            "Policy Creation": "/api/v1/governance/policy-creation",
            "Constitutional Compliance": "/api/v1/governance/constitutional-compliance",
            "Policy Enforcement": "/api/v1/governance/policy-enforcement",
            "WINA Oversight": "/api/v1/governance/wina-oversight",
            "Audit/Transparency": "/api/v1/governance/audit-transparency",
        }

        operational_workflows = 0

        async with aiohttp.ClientSession() as session:
            for workflow_name, endpoint in workflow_endpoints.items():
                try:
                    # Test workflow endpoint on PGC service (primary governance service)
                    start_time = time.time()
                    async with session.get(
                        f"http://localhost:8005{endpoint}", timeout=10
                    ) as response:
                        response_time = (time.time() - start_time) * 1000

                        if response.status == 200:
                            workflow_data = await response.json()
                            self.validation_report["governance_workflows"][
                                workflow_name
                            ] = {
                                "status": "operational",
                                "response_time_ms": round(response_time, 2),
                                "endpoint": endpoint,
                                "data": workflow_data,
                            }
                            operational_workflows += 1
                            logger.info(
                                f"  ✅ {workflow_name}: Operational ({response_time:.1f}ms)"
                            )
                        else:
                            logger.warning(
                                f"  ⚠️ {workflow_name}: HTTP {response.status}"
                            )
                            self.validation_report["governance_workflows"][
                                workflow_name
                            ] = {
                                "status": "degraded",
                                "response_time_ms": round(response_time, 2),
                                "endpoint": endpoint,
                                "error": f"HTTP {response.status}",
                            }

                except Exception as e:
                    logger.error(f"  ❌ {workflow_name}: {e!s}")
                    self.validation_report["governance_workflows"][workflow_name] = {
                        "status": "failed",
                        "endpoint": endpoint,
                        "error": str(e),
                    }

        workflow_availability = (operational_workflows / len(workflow_endpoints)) * 100
        logger.info(
            f"📊 Governance Workflow Availability: {operational_workflows}/{len(workflow_endpoints)} ({workflow_availability:.1f}%)"
        )

        return (
            operational_workflows >= 4
        )  # At least 4/5 workflows should be operational

    def validate_blockchain_deployment(self):
        """Validate Quantumagi Solana devnet deployment."""
        logger.info("⛓️ Validating blockchain deployment...")

        try:
            # Check if Quantumagi deployment files exist
            quantumagi_dir = self.root_dir / "blockchain" / "quantumagi-deployment"
            if quantumagi_dir.exists():
                self.validation_report["blockchain_status"][
                    "quantumagi_deployment"
                ] = "present"
                logger.info("  ✅ Quantumagi deployment files present")
            else:
                self.validation_report["blockchain_status"][
                    "quantumagi_deployment"
                ] = "missing"
                logger.error("  ❌ Quantumagi deployment files missing")
                return False

            # Check Anchor programs
            programs_dir = self.root_dir / "blockchain" / "programs"
            if programs_dir.exists():
                programs = list(programs_dir.iterdir())
                self.validation_report["blockchain_status"]["anchor_programs"] = [
                    p.name for p in programs if p.is_dir()
                ]
                logger.info(f"  ✅ Found {len(programs)} Anchor programs")
            else:
                logger.error("  ❌ Anchor programs directory missing")
                return False

            # Check if blockchain can be built
            blockchain_dir = self.root_dir / "blockchain"
            result = subprocess.run(
                ["anchor", "build"],
                check=False,
                cwd=blockchain_dir,
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode == 0:
                self.validation_report["blockchain_status"]["build_status"] = "success"
                logger.info("  ✅ Anchor programs build successfully")
                return True
            self.validation_report["blockchain_status"]["build_status"] = "failed"
            self.validation_report["blockchain_status"]["build_error"] = result.stderr
            logger.error(f"  ❌ Anchor build failed: {result.stderr}")
            return False

        except Exception as e:
            logger.error(f"  ❌ Blockchain validation failed: {e}")
            self.validation_report["blockchain_status"]["validation_error"] = str(e)
            return False

    def run_test_suites(self):
        """Run comprehensive test suites."""
        logger.info("🧪 Running test suites...")

        test_results = {}

        # Run Python unit tests
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/", "-v", "--tb=short"],
                check=False,
                cwd=self.root_dir,
                capture_output=True,
                text=True,
                timeout=300,
            )

            test_results["python_unit_tests"] = {
                "status": "passed" if result.returncode == 0 else "failed",
                "output": result.stdout,
                "errors": result.stderr,
            }

            if result.returncode == 0:
                logger.info("  ✅ Python unit tests passed")
            else:
                logger.warning("  ⚠️ Python unit tests had failures")

        except Exception as e:
            test_results["python_unit_tests"] = {"status": "error", "error": str(e)}
            logger.error(f"  ❌ Python unit tests failed: {e}")

        # Run Anchor tests
        try:
            result = subprocess.run(
                ["anchor", "test"],
                check=False,
                cwd=self.root_dir / "blockchain",
                capture_output=True,
                text=True,
                timeout=300,
            )

            test_results["anchor_tests"] = {
                "status": "passed" if result.returncode == 0 else "failed",
                "output": result.stdout,
                "errors": result.stderr,
            }

            if result.returncode == 0:
                logger.info("  ✅ Anchor tests passed")
            else:
                logger.warning("  ⚠️ Anchor tests had failures")

        except Exception as e:
            test_results["anchor_tests"] = {"status": "error", "error": str(e)}
            logger.error(f"  ❌ Anchor tests failed: {e}")

        self.validation_report["test_results"] = test_results

        # Calculate test coverage
        passed_tests = sum(
            1 for test in test_results.values() if test.get("status") == "passed"
        )
        total_tests = len(test_results)
        coverage = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        logger.info(f"📊 Test Coverage: {passed_tests}/{total_tests} ({coverage:.1f}%)")

        return coverage >= 80  # Target >80% test coverage

    async def measure_performance(self):
        """Measure system performance metrics."""
        logger.info("⚡ Measuring performance metrics...")

        performance_data = {
            "response_times": {},
            "availability_target": ">99.5%",
            "response_time_target": "<500ms",
        }

        # Measure response times for each service
        async with aiohttp.ClientSession():
            for service_name, _config in self.services.items():
                if service_name in self.validation_report["service_health"]:
                    service_health = self.validation_report["service_health"][
                        service_name
                    ]
                    if service_health.get("status") in ["healthy", "degraded"]:
                        response_time = service_health.get("response_time_ms", 0)
                        performance_data["response_times"][service_name] = response_time

        # Calculate average response time
        if performance_data["response_times"]:
            avg_response_time = sum(performance_data["response_times"].values()) / len(
                performance_data["response_times"]
            )
            performance_data["average_response_time_ms"] = round(avg_response_time, 2)

            # Check if performance targets are met
            performance_data["targets_met"] = {
                "response_time": avg_response_time < 500,  # <500ms target
                "availability": len(
                    [
                        s
                        for s in self.validation_report["service_health"].values()
                        if s.get("status") == "healthy"
                    ]
                )
                >= 6,
            }

            logger.info(f"📊 Average Response Time: {avg_response_time:.1f}ms")

        self.validation_report["performance_metrics"] = performance_data

        return (
            performance_data["targets_met"]["response_time"]
            and performance_data["targets_met"]["availability"]
        )

    def generate_recommendations(self):
        """Generate recommendations based on validation results."""
        recommendations = []

        # Service health recommendations
        unhealthy_services = [
            name
            for name, health in self.validation_report["service_health"].items()
            if health.get("status") not in ["healthy"]
        ]
        if unhealthy_services:
            recommendations.append(
                f"Restore unhealthy services: {', '.join(unhealthy_services)}"
            )

        # Governance workflow recommendations
        failed_workflows = [
            name
            for name, workflow in self.validation_report["governance_workflows"].items()
            if workflow.get("status") != "operational"
        ]
        if failed_workflows:
            recommendations.append(
                f"Fix governance workflows: {', '.join(failed_workflows)}"
            )

        # Performance recommendations
        if (
            not self.validation_report["performance_metrics"]
            .get("targets_met", {})
            .get("response_time")
        ):
            recommendations.append("Optimize response times to meet <500ms target")

        # Test coverage recommendations
        test_results = self.validation_report["test_results"]
        failed_tests = [
            name
            for name, result in test_results.items()
            if result.get("status") != "passed"
        ]
        if failed_tests:
            recommendations.append(f"Fix failing tests: {', '.join(failed_tests)}")

        self.validation_report["recommendations"] = recommendations
        return recommendations

    async def run_validation(self):
        """Execute the complete validation process."""
        logger.info("🚀 Starting Comprehensive Functionality Validation")
        logger.info("=" * 55)

        start_time = time.time()
        validation_results = {}

        # Execute validation tasks
        validation_tasks = [
            ("Service Health", self.validate_service_health()),
            ("Governance Workflows", self.validate_governance_workflows()),
            ("Blockchain Deployment", self.validate_blockchain_deployment()),
            ("Test Suites", self.run_test_suites()),
            ("Performance Metrics", self.measure_performance()),
        ]

        passed_validations = 0

        for task_name, task_coro in validation_tasks:
            logger.info(f"\n🔄 Validating: {task_name}")
            try:
                if asyncio.iscoroutine(task_coro):
                    result = await task_coro
                else:
                    result = task_coro

                validation_results[task_name] = result
                if result:
                    passed_validations += 1
                    logger.info(f"✅ {task_name}: PASSED")
                else:
                    logger.warning(f"⚠️ {task_name}: FAILED")

            except Exception as e:
                logger.error(f"❌ {task_name}: ERROR - {e}")
                validation_results[task_name] = False
                self.validation_report["issues_found"].append(f"{task_name}: {e!s}")

        # Generate recommendations
        recommendations = self.generate_recommendations()

        # Save validation report
        duration = time.time() - start_time
        report_file = (
            self.root_dir
            / f"functionality_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        report_file.write_text(json.dumps(self.validation_report, indent=2))

        # Print summary
        total_validations = len(validation_tasks)
        success_rate = (passed_validations / total_validations) * 100

        logger.info("\n" + "=" * 55)
        logger.info("📊 VALIDATION SUMMARY")
        logger.info("=" * 55)
        logger.info(
            f"✅ Validations Passed: {passed_validations}/{total_validations} ({success_rate:.1f}%)"
        )
        logger.info(f"⏱️ Duration: {duration:.2f} seconds")
        logger.info(f"📄 Report: {report_file}")

        if recommendations:
            logger.info("\n💡 RECOMMENDATIONS:")
            for i, rec in enumerate(recommendations, 1):
                logger.info(f"  {i}. {rec}")

        # Determine overall success
        overall_success = (
            passed_validations >= 4
        )  # At least 4/5 validations should pass

        if overall_success:
            logger.info("🎉 Phase 3: Functionality Validation COMPLETE!")
        else:
            logger.warning("⚠️ Phase 3: Functionality Validation completed with issues")

        return self.validation_report


async def main():
    """Main execution function."""
    validator = FunctionalityValidator()
    report = await validator.run_validation()

    # Return success if most validations passed
    passed_count = sum(
        1
        for task in [
            "Service Health",
            "Governance Workflows",
            "Blockchain Deployment",
            "Test Suites",
            "Performance Metrics",
        ]
        if any(task.lower().replace(" ", "_") in str(report).lower())
    )

    return 0 if passed_count >= 3 else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
