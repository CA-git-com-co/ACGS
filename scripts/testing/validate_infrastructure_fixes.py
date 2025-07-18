#!/usr/bin/env python3
"""
Quick Infrastructure Validation Script
Validates that the critical infrastructure fixes are working correctly.
"""

import asyncio
import json
import logging
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InfrastructureValidator:
    """Quick validator for infrastructure fixes."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.validation_results = {
            "validation_id": f"infra_validation_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tests": {},
            "overall_status": "UNKNOWN",
        }

    async def run_validation(self) -> dict[str, Any]:
        """Run all infrastructure validation tests."""
        logger.info("🔍 Starting Infrastructure Validation")

        tests = [
            ("Database Connectivity", self.test_database_connectivity),
            ("Service Health Endpoints", self.test_health_endpoints),
            ("Security Middleware", self.test_security_middleware),
            ("Docker Container Status", self.test_container_status),
            ("Environment Configuration", self.test_environment_config),
        ]

        passed_tests = 0

        for test_name, test_func in tests:
            logger.info(f"🧪 Running {test_name}")

            try:
                test_result = await test_func()
                self.validation_results["tests"][test_name] = test_result

                if test_result["status"] == "PASS":
                    passed_tests += 1
                    logger.info(f"✅ {test_name}: PASSED")
                else:
                    logger.error(
                        f"❌ {test_name}: FAILED - {test_result.get('message', 'Unknown error')}"
                    )

            except Exception as e:
                logger.error(f"💥 {test_name}: CRASHED - {e!s}")
                self.validation_results["tests"][test_name] = {
                    "status": "CRASH",
                    "message": str(e),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }

        # Calculate overall status
        success_rate = (passed_tests / len(tests)) * 100
        if success_rate >= 100:
            self.validation_results["overall_status"] = "ALL_PASS"
        elif success_rate >= 80:
            self.validation_results["overall_status"] = "MOSTLY_PASS"
        else:
            self.validation_results["overall_status"] = "FAIL"

        self.validation_results["success_rate"] = success_rate
        self.validation_results["passed_tests"] = passed_tests
        self.validation_results["total_tests"] = len(tests)

        # Save validation report
        report_path = (
            self.project_root
            / f"reports/infrastructure_validation_{self.validation_results['validation_id']}.json"
        )
        report_path.parent.mkdir(exist_ok=True)
        with open(report_path, "w") as f:
            json.dump(self.validation_results, f, indent=2)

        logger.info(
            f"📊 Validation completed: {passed_tests}/{len(tests)} tests passed ({success_rate:.1f}%)"
        )
        logger.info(f"📄 Report saved to: {report_path}")

        return self.validation_results

    async def test_database_connectivity(self) -> dict[str, Any]:
        """Test database connectivity with the fixed configuration."""
        try:
            # Test database connection using Docker exec
            result = subprocess.run(
                [
                    "docker",
                    "exec",
                    "acgs_postgres_db",
                    "psql",
                    "-U",
                    "acgs_user",
                    "-d",
                    "acgs_pgp_db",
                    "-c",
                    "SELECT 1 as test;",
                ],
                check=False,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0 and "1" in result.stdout:
                return {
                    "status": "PASS",
                    "message": "Database connection successful",
                    "details": "PostgreSQL responding correctly",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            return {
                "status": "FAIL",
                "message": f"Database connection failed: {result.stderr}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            return {
                "status": "FAIL",
                "message": f"Database test error: {e!s}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    async def test_health_endpoints(self) -> dict[str, Any]:
        """Test all service health endpoints."""
        health_endpoints = {
            "auth_service": "http://localhost:8000/health",
            "ac_service": "http://localhost:8001/health",
            "integrity_service": "http://localhost:8002/health",
            "fv_service": "http://localhost:8003/health",
            "gs_service": "http://localhost:8004/health",
            "pgc_service": "http://localhost:8005/health",
            "ec_service": "http://localhost:8006/health",
        }

        healthy_services = []
        unhealthy_services = []

        for service, endpoint in health_endpoints.items():
            try:
                response = requests.get(endpoint, timeout=10)
                if response.status_code == 200:
                    healthy_services.append(service)
                else:
                    unhealthy_services.append(f"{service}: HTTP {response.status_code}")
            except Exception as e:
                unhealthy_services.append(f"{service}: {e!s}")

        if not unhealthy_services:
            return {
                "status": "PASS",
                "message": f"All {len(healthy_services)} services healthy",
                "healthy_services": healthy_services,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        return {
            "status": "FAIL",
            "message": f"{len(unhealthy_services)} services unhealthy",
            "healthy_services": healthy_services,
            "unhealthy_services": unhealthy_services,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def test_security_middleware(self) -> dict[str, Any]:
        """Test security middleware health endpoint bypass."""
        try:
            # Test that health endpoints bypass security middleware
            test_endpoints = [
                "http://localhost:8002/health",
                "http://localhost:8001/health",
            ]

            bypass_working = []
            bypass_failed = []

            for endpoint in test_endpoints:
                try:
                    # Test with various query parameters that might trigger security
                    test_response = requests.get(f"{endpoint}?test=bypass", timeout=5)
                    if test_response.status_code == 200:
                        bypass_working.append(endpoint)
                    else:
                        bypass_failed.append(
                            f"{endpoint}: HTTP {test_response.status_code}"
                        )
                except Exception as e:
                    bypass_failed.append(f"{endpoint}: {e!s}")

            if not bypass_failed:
                return {
                    "status": "PASS",
                    "message": "Security middleware bypass working correctly",
                    "working_endpoints": bypass_working,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            return {
                "status": "FAIL",
                "message": "Security middleware bypass issues detected",
                "working_endpoints": bypass_working,
                "failed_endpoints": bypass_failed,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            return {
                "status": "FAIL",
                "message": f"Security middleware test error: {e!s}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    async def test_container_status(self) -> dict[str, Any]:
        """Test Docker container status."""
        try:
            # Get container status
            result = subprocess.run(
                [
                    "docker-compose",
                    "-f",
                    "infrastructure/docker/docker-compose.yml",
                    "ps",
                ],
                check=False,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                # Parse container status
                lines = result.stdout.strip().split("\n")
                running_containers = []
                stopped_containers = []

                for line in lines[1:]:  # Skip header
                    if "Up" in line:
                        container_name = line.split()[0]
                        running_containers.append(container_name)
                    elif "Exit" in line or "Exited" in line:
                        container_name = line.split()[0]
                        stopped_containers.append(container_name)

                if not stopped_containers:
                    return {
                        "status": "PASS",
                        "message": f"All {len(running_containers)} containers running",
                        "running_containers": running_containers,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                return {
                    "status": "FAIL",
                    "message": f"{len(stopped_containers)} containers stopped",
                    "running_containers": running_containers,
                    "stopped_containers": stopped_containers,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            return {
                "status": "FAIL",
                "message": f"Docker compose status check failed: {result.stderr}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            return {
                "status": "FAIL",
                "message": f"Container status test error: {e!s}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    async def test_environment_config(self) -> dict[str, Any]:
        """Test environment configuration."""
        try:
            # Check if config/environments/development.env file exists and has required variables
            env_file = self.project_root / "config/environments/development.env"
            if not env_file.exists():
                return {
                    "status": "FAIL",
                    "message": "config/environments/development.env file not found",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }

            # Read and validate key environment variables
            with open(env_file) as f:
                env_content = f.read()

            required_vars = [
                "DATABASE_URL",
                "JWT_SECRET_KEY",
                "REDIS_URL",
                "ENVIRONMENT",
            ]

            missing_vars = []
            for var in required_vars:
                if var not in env_content:
                    missing_vars.append(var)

            if not missing_vars:
                return {
                    "status": "PASS",
                    "message": "Environment configuration complete",
                    "required_vars_found": required_vars,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            return {
                "status": "FAIL",
                "message": f"Missing environment variables: {missing_vars}",
                "missing_vars": missing_vars,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            return {
                "status": "FAIL",
                "message": f"Environment config test error: {e!s}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }


async def main():
    """Main validation function."""
    validator = InfrastructureValidator()
    results = await validator.run_validation()

    print("\n" + "=" * 80)
    print("🔍 ACGS-1 INFRASTRUCTURE VALIDATION RESULTS")
    print("=" * 80)
    print(f"Overall Status: {results['overall_status']}")
    print(f"Success Rate: {results['success_rate']:.1f}%")
    print(f"Tests Passed: {results['passed_tests']}/{results['total_tests']}")

    print("\n📋 Test Results:")
    for test_name, test_result in results["tests"].items():
        status_icon = "✅" if test_result["status"] == "PASS" else "❌"
        print(f"{status_icon} {test_name}: {test_result['status']}")
        if test_result["status"] != "PASS":
            print(f"   └─ {test_result.get('message', 'No details')}")

    if results["overall_status"] == "ALL_PASS":
        print("\n🎉 All infrastructure fixes validated successfully!")
        return 0
    print("\n⚠️  Some infrastructure issues detected. Check the detailed report.")
    return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
