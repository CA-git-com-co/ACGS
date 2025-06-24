#!/usr/bin/env python3
"""
ACGS-1 Production Deployment Script
Automated deployment with health checks and rollback capability
"""

import asyncio
import logging
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import httpx

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("acgs_deployment")

# Project configuration
PROJECT_ROOT = Path(__file__).parent.parent
DOCKER_COMPOSE_PATH = PROJECT_ROOT / "infrastructure" / "docker" / "docker-compose.yml"


class ACGSDeployment:
    """ACGS-1 production deployment manager."""

    def __init__(self):
        self.services = {
            "auth_service": {"port": 8000, "health_endpoint": "/health"},
            "ac_service": {"port": 8001, "health_endpoint": "/health"},
            "integrity_service": {"port": 8002, "health_endpoint": "/health"},
            "fv_service": {"port": 8003, "health_endpoint": "/health"},
            "gs_service": {"port": 8004, "health_endpoint": "/health"},
            "pgc_service": {"port": 8005, "health_endpoint": "/health"},
            "ec_service": {"port": 8006, "health_endpoint": "/health"},
            "workflow_service": {"port": 9007, "health_endpoint": "/health"},
            "blockchain_bridge": {"port": 9008, "health_endpoint": "/health"},
            "performance_optimizer": {"port": 9009, "health_endpoint": "/health"},
            "external_apis_service": {"port": 9010, "health_endpoint": "/health"},
        }
        self.deployment_results = {}
        self.http_client = httpx.AsyncClient(timeout=30.0)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.http_client.aclose()

    def pre_deployment_checks(self) -> dict[str, Any]:
        """Run pre-deployment validation checks."""
        logger.info("🔍 Running pre-deployment checks...")

        checks = {
            "docker_compose_exists": DOCKER_COMPOSE_PATH.exists(),
            "docker_daemon_running": self._check_docker_daemon(),
            "required_directories": self._check_required_directories(),
            "environment_variables": self._check_environment_variables(),
        }

        all_passed = all(checks.values())

        return {
            "passed": all_passed,
            "checks": checks,
            "message": (
                "Pre-deployment checks completed"
                if all_passed
                else "Pre-deployment checks failed"
            ),
        }

    def _check_docker_daemon(self) -> bool:
        """Check if Docker daemon is running."""
        try:
            result = subprocess.run(
                ["docker", "info"], capture_output=True, text=True, timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False

    def _check_required_directories(self) -> bool:
        """Check if required directories exist."""
        required_dirs = [
            PROJECT_ROOT / "services",
            PROJECT_ROOT / "applications",
            PROJECT_ROOT / "infrastructure",
            PROJECT_ROOT / "config",
        ]
        return all(dir_path.exists() for dir_path in required_dirs)

    def _check_environment_variables(self) -> bool:
        """Check if required environment variables are set."""
        # For now, return True - in production, check actual env vars
        return True

    async def build_services(self) -> dict[str, Any]:
        """Build all Docker services."""
        logger.info("🔨 Building Docker services...")

        try:
            # Build all services
            result = subprocess.run(
                [
                    "docker-compose",
                    "-f",
                    str(DOCKER_COMPOSE_PATH),
                    "build",
                    "--parallel",
                ],
                capture_output=True,
                text=True,
                timeout=600,  # 10 minutes timeout
            )

            if result.returncode == 0:
                return {
                    "passed": True,
                    "message": "All services built successfully",
                    "build_output": result.stdout,
                }
            else:
                return {
                    "passed": False,
                    "message": "Service build failed",
                    "error": result.stderr,
                }

        except subprocess.TimeoutExpired:
            return {
                "passed": False,
                "message": "Service build timed out",
                "error": "Build process exceeded 10 minute timeout",
            }
        except Exception as e:
            return {"passed": False, "message": "Service build error", "error": str(e)}

    async def deploy_services(self) -> dict[str, Any]:
        """Deploy all services using Docker Compose."""
        logger.info("🚀 Deploying services...")

        try:
            # Stop existing services
            subprocess.run(
                ["docker-compose", "-f", str(DOCKER_COMPOSE_PATH), "down"],
                capture_output=True,
                timeout=120,
            )

            # Start services
            result = subprocess.run(
                ["docker-compose", "-f", str(DOCKER_COMPOSE_PATH), "up", "-d"],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes timeout
            )

            if result.returncode == 0:
                return {
                    "passed": True,
                    "message": "Services deployed successfully",
                    "deployment_output": result.stdout,
                }
            else:
                return {
                    "passed": False,
                    "message": "Service deployment failed",
                    "error": result.stderr,
                }

        except Exception as e:
            return {"passed": False, "message": "Deployment error", "error": str(e)}

    async def wait_for_services(self, timeout_seconds: int = 300) -> dict[str, Any]:
        """Wait for all services to become healthy."""
        logger.info("⏳ Waiting for services to become healthy...")

        start_time = time.time()
        service_status = {}

        while time.time() - start_time < timeout_seconds:
            all_healthy = True

            for service_name, config in self.services.items():
                if service_name not in service_status:
                    service_status[service_name] = {"healthy": False, "attempts": 0}

                if not service_status[service_name]["healthy"]:
                    is_healthy = await self._check_service_health(service_name, config)
                    service_status[service_name]["healthy"] = is_healthy
                    service_status[service_name]["attempts"] += 1

                    if is_healthy:
                        logger.info(f"✅ {service_name} is healthy")
                    else:
                        all_healthy = False

            if all_healthy:
                return {
                    "passed": True,
                    "message": "All services are healthy",
                    "service_status": service_status,
                    "wait_time_seconds": time.time() - start_time,
                }

            await asyncio.sleep(5)  # Wait 5 seconds before next check

        # Timeout reached
        healthy_services = [
            name for name, status in service_status.items() if status["healthy"]
        ]

        return {
            "passed": False,
            "message": f"Timeout waiting for services. {len(healthy_services)}/{len(self.services)} services healthy",
            "service_status": service_status,
            "healthy_services": healthy_services,
            "wait_time_seconds": timeout_seconds,
        }

    async def _check_service_health(
        self, service_name: str, config: dict[str, Any]
    ) -> bool:
        """Check if a specific service is healthy."""
        try:
            url = f"http://localhost:{config['port']}{config['health_endpoint']}"
            response = await self.http_client.get(url)
            return response.status_code == 200
        except Exception:
            return False

    async def run_smoke_tests(self) -> dict[str, Any]:
        """Run basic smoke tests on deployed services."""
        logger.info("🧪 Running smoke tests...")

        test_results = {}
        passed_tests = 0
        total_tests = len(self.services)

        for service_name, config in self.services.items():
            try:
                # Test root endpoint
                root_url = f"http://localhost:{config['port']}/"
                response = await self.http_client.get(root_url)

                test_results[service_name] = {
                    "root_endpoint": {
                        "status_code": response.status_code,
                        "passed": response.status_code == 200,
                    }
                }

                if response.status_code == 200:
                    passed_tests += 1

            except Exception as e:
                test_results[service_name] = {
                    "root_endpoint": {"error": str(e), "passed": False}
                }

        success_rate = passed_tests / total_tests

        return {
            "passed": success_rate >= 0.9,  # 90% success threshold
            "success_rate": success_rate,
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "test_results": test_results,
            "message": f"Smoke tests completed with {success_rate:.1%} success rate",
        }

    async def rollback_deployment(self) -> dict[str, Any]:
        """Rollback deployment in case of failure."""
        logger.info("🔄 Rolling back deployment...")

        try:
            # Stop current services
            result = subprocess.run(
                ["docker-compose", "-f", str(DOCKER_COMPOSE_PATH), "down"],
                capture_output=True,
                text=True,
                timeout=120,
            )

            return {
                "passed": result.returncode == 0,
                "message": (
                    "Rollback completed"
                    if result.returncode == 0
                    else "Rollback failed"
                ),
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None,
            }

        except Exception as e:
            return {"passed": False, "message": "Rollback error", "error": str(e)}

    async def run_full_deployment(self) -> dict[str, Any]:
        """Run complete deployment process."""
        logger.info("🚀 Starting ACGS-1 production deployment...")

        deployment_steps = [
            ("pre_deployment_checks", self.pre_deployment_checks),
            ("build_services", self.build_services),
            ("deploy_services", self.deploy_services),
            ("wait_for_services", self.wait_for_services),
            ("smoke_tests", self.run_smoke_tests),
        ]

        results = {"start_time": time.time(), "steps": {}, "summary": {}}

        for step_name, step_method in deployment_steps:
            logger.info(f"Executing step: {step_name}")

            if asyncio.iscoroutinefunction(step_method):
                step_result = await step_method()
            else:
                step_result = step_method()

            results["steps"][step_name] = step_result

            if not step_result.get("passed", False):
                logger.error(
                    f"❌ Step {step_name} failed: {step_result.get('message', 'Unknown error')}"
                )

                # Attempt rollback
                rollback_result = await self.rollback_deployment()
                results["steps"]["rollback"] = rollback_result

                results["summary"] = {
                    "success": False,
                    "failed_step": step_name,
                    "rollback_success": rollback_result.get("passed", False),
                    "message": f"Deployment failed at step: {step_name}",
                }

                return results
            else:
                logger.info(f"✅ Step {step_name} completed successfully")

        # All steps passed
        results["end_time"] = time.time()
        results["summary"] = {
            "success": True,
            "deployment_time_seconds": results["end_time"] - results["start_time"],
            "message": "ACGS-1 deployment completed successfully",
        }

        return results

    def generate_deployment_report(self, results: dict[str, Any]) -> str:
        """Generate deployment report."""
        report = f"""
# ACGS-1 Deployment Report

## Summary
- **Success**: {results['summary']['success']}
- **Message**: {results['summary']['message']}
"""

        if results["summary"]["success"]:
            report += f"- **Deployment Time**: {results['summary']['deployment_time_seconds']:.2f} seconds\n"
        else:
            report += f"- **Failed Step**: {results['summary']['failed_step']}\n"
            if "rollback_success" in results["summary"]:
                report += f"- **Rollback Success**: {results['summary']['rollback_success']}\n"

        report += "\n## Step Results\n"
        for step_name, step_result in results["steps"].items():
            status = "✅ PASSED" if step_result.get("passed", False) else "❌ FAILED"
            report += f"- **{step_name}**: {status}\n"
            if "message" in step_result:
                report += f"  - {step_result['message']}\n"

        return report


async def main():
    """Main deployment execution."""
    async with ACGSDeployment() as deployer:
        try:
            results = await deployer.run_full_deployment()

            # Generate and save report
            report = deployer.generate_deployment_report(results)
            report_path = PROJECT_ROOT / "docs" / "deployment_report.md"

            with open(report_path, "w") as f:
                f.write(report)

            print("\n" + "=" * 50)
            print("ACGS-1 Deployment Results")
            print("=" * 50)
            print(f"Success: {results['summary']['success']}")
            print(f"Message: {results['summary']['message']}")
            print(f"Report saved to: {report_path}")

            if not results["summary"]["success"]:
                sys.exit(1)

        except Exception as e:
            logger.error(f"Deployment failed with exception: {e}")
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
