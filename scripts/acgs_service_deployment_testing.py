#!/usr/bin/env python3
"""
ACGS Service Deployment and Integration Testing
Constitutional Hash: cdd01ef066bc6cf2

Deploy individual ACGS services using Docker Compose and test
service-to-service communication with constitutional compliance validation.
"""

import json
import logging
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path

import requests

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
REPO_ROOT = Path("/home/dislove/ACGS-2")

# ACGS service configurations
ACGS_SERVICES = {
    "constitutional-ai": {
        "port": 8001,
        "health_endpoint": "/health",
        "required": True,
        "description": "Constitutional AI core service",
    },
    "integrity": {
        "port": 8200,
        "health_endpoint": "/health",
        "required": True,
        "description": "Integrity validation service",
    },
    "auth": {
        "port": 8100,
        "health_endpoint": "/health",
        "required": True,
        "description": "Authentication service",
    },
    "api-gateway": {
        "port": 8300,
        "health_endpoint": "/health",
        "required": False,
        "description": "API Gateway service",
    },
    "governance-synthesis": {
        "port": 8400,
        "health_endpoint": "/health",
        "required": False,
        "description": "Governance synthesis service",
    },
}

# Infrastructure services
INFRASTRUCTURE_SERVICES = {
    "postgres": {"port": 5432, "required": True},
    "redis": {"port": 6379, "required": True},
    "opa": {"port": 8181, "required": False},
    "nats": {"port": 4222, "required": False},
}


class ACGSServiceDeploymentTester:
    """ACGS service deployment and integration testing."""

    def __init__(self):
        self.logger = self._setup_logging()
        self.deployment_results = {
            "infrastructure": {},
            "services": {},
            "integration_tests": {},
            "constitutional_compliance": {},
        }

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for deployment testing."""
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )
        return logging.getLogger(__name__)

    def _run_command(
        self, command: str, cwd: Path = None, timeout: int = 60
    ) -> tuple[bool, str, str]:
        """Run shell command safely."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd or REPO_ROOT,
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)

    def check_docker_availability(self) -> bool:
        """Check if Docker and Docker Compose are available."""
        self.logger.info("🐳 Checking Docker availability...")

        # Check Docker
        success, stdout, stderr = self._run_command("docker --version")
        if not success:
            self.logger.error("Docker not available")
            return False

        # Check Docker Compose
        success, stdout, stderr = self._run_command("docker-compose --version")
        if not success:
            self.logger.error("Docker Compose not available")
            return False

        # Check Docker daemon
        success, stdout, stderr = self._run_command("docker info")
        if not success:
            self.logger.error("Docker daemon not running")
            return False

        self.logger.info("✅ Docker and Docker Compose available")
        return True

    def setup_environment_variables(self) -> bool:
        """Setup required environment variables."""
        self.logger.info("⚙️ Setting up environment variables...")

        env_vars = {
            "CONSTITUTIONAL_HASH": CONSTITUTIONAL_HASH,
            "ENVIRONMENT": "development",
            "POSTGRES_PASSWORD": "acgs_dev_password",
            "REDIS_PASSWORD": "acgs_dev_redis",
            "SECRET_KEY": "acgs_dev_secret_key_12345",
            "JWT_SECRET_KEY": "acgs_dev_jwt_secret_12345",
            "CSRF_SECRET_KEY": "acgs_dev_csrf_secret_12345",
        }

        for key, value in env_vars.items():
            os.environ[key] = value
            self.logger.info(f"  Set {key}")

        return True

    def create_docker_network(self) -> bool:
        """Create Docker network for ACGS services."""
        self.logger.info("🌐 Creating Docker network...")

        # Check if network exists
        success, stdout, stderr = self._run_command(
            "docker network ls --filter name=acgs_network --format '{{.Name}}'"
        )
        if success and "acgs_network" in stdout:
            self.logger.info("  ✅ ACGS network already exists")
            return True

        # Create network
        success, stdout, stderr = self._run_command(
            "docker network create acgs_network"
        )
        if success:
            self.logger.info("  ✅ Created ACGS network")
            return True
        else:
            self.logger.error(f"  ❌ Failed to create network: {stderr}")
            return False

    def deploy_infrastructure_services(self) -> dict[str, bool]:
        """Deploy infrastructure services (PostgreSQL, Redis, etc.)."""
        self.logger.info("🏗️ Deploying infrastructure services...")

        # Create a minimal infrastructure compose file
        infra_compose = """version: '3.8'
services:
  postgres:
    image: postgres:15
    container_name: acgs_postgres
    environment:
      - POSTGRES_DB=acgs
      - POSTGRES_USER=acgs_user
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-acgs_dev_password}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U acgs_user -d acgs"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - acgs_network
    labels:
      - acgs.service=infrastructure
      - acgs.constitutional_hash=cdd01ef066bc6cf2

  redis:
    image: redis:7-alpine
    container_name: acgs_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - acgs_network
    labels:
      - acgs.service=infrastructure
      - acgs.constitutional_hash=cdd01ef066bc6cf2

networks:
  acgs_network:
    external: true

volumes:
  postgres_data:
  redis_data:
"""

        # Write infrastructure compose file
        infra_compose_path = REPO_ROOT / "docker-compose.infrastructure.yml"
        with open(infra_compose_path, "w") as f:
            f.write(infra_compose)

        # Deploy infrastructure
        success, stdout, stderr = self._run_command(
            f"docker-compose -f {infra_compose_path} up -d", timeout=120
        )

        if not success:
            self.logger.error(f"Failed to deploy infrastructure: {stderr}")
            return {"postgres": False, "redis": False}

        # Wait for services to be healthy
        self.logger.info("  ⏳ Waiting for infrastructure services to be healthy...")
        time.sleep(30)

        # Check service health
        results = {}
        for service, config in INFRASTRUCTURE_SERVICES.items():
            if service in ["postgres", "redis"]:
                success, stdout, stderr = self._run_command(
                    f"docker-compose -f {infra_compose_path} ps {service}"
                )
                healthy = success and "healthy" in stdout.lower()
                results[service] = healthy

                if healthy:
                    self.logger.info(f"  ✅ {service} is healthy")
                else:
                    self.logger.warning(f"  ⚠️ {service} is not healthy")

        self.deployment_results["infrastructure"] = results
        return results

    def check_service_health(
        self, service_name: str, port: int, endpoint: str = "/health"
    ) -> bool:
        """Check if a service is healthy."""
        url = f"http://localhost:{port}{endpoint}"

        try:
            response = requests.get(url, timeout=10)
            return response.status_code == 200
        except Exception:
            return False

    def test_constitutional_compliance(
        self, service_name: str, port: int
    ) -> dict[str, bool]:
        """Test constitutional compliance for a service."""
        self.logger.info(f"🔍 Testing constitutional compliance for {service_name}...")

        compliance_results = {
            "hash_in_response": False,
            "health_endpoint": False,
            "constitutional_headers": False,
        }

        try:
            # Test health endpoint
            health_url = f"http://localhost:{port}/health"
            response = requests.get(health_url, timeout=10)

            if response.status_code == 200:
                compliance_results["health_endpoint"] = True

                # Check for constitutional hash in response
                response_text = response.text.lower()
                if CONSTITUTIONAL_HASH in response_text:
                    compliance_results["hash_in_response"] = True

                # Check for constitutional headers
                headers = response.headers
                constitutional_headers = [
                    h for h in headers.keys() if "constitutional" in h.lower()
                ]
                if constitutional_headers:
                    compliance_results["constitutional_headers"] = True

        except Exception as e:
            self.logger.warning(
                f"  ⚠️ Failed to test compliance for {service_name}: {e}"
            )

        return compliance_results

    def test_service_integration(self) -> dict[str, bool]:
        """Test service-to-service integration."""
        self.logger.info("🔗 Testing service integration...")

        integration_results = {}

        # Test basic connectivity between services
        # This is a simplified test - in production you'd test actual API calls

        for service_name, config in ACGS_SERVICES.items():
            if self.deployment_results["services"].get(service_name, False):
                # Test if service can be reached
                healthy = self.check_service_health(service_name, config["port"])
                integration_results[f"{service_name}_reachable"] = healthy

                if healthy:
                    self.logger.info(f"  ✅ {service_name} integration test passed")
                else:
                    self.logger.warning(f"  ⚠️ {service_name} integration test failed")

        self.deployment_results["integration_tests"] = integration_results
        return integration_results

    def generate_deployment_report(self) -> str:
        """Generate deployment and testing report."""
        self.logger.info("📄 Generating deployment report...")

        report = {
            "timestamp": datetime.now().isoformat(),
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "deployment_results": self.deployment_results,
            "summary": {
                "infrastructure_services": len([
                    s for s in self.deployment_results["infrastructure"].values() if s
                ]),
                "acgs_services": len([
                    s for s in self.deployment_results["services"].values() if s
                ]),
                "integration_tests_passed": len([
                    t
                    for t in self.deployment_results["integration_tests"].values()
                    if t
                ]),
                "overall_success": self._calculate_overall_success(),
            },
        }

        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = REPO_ROOT / f"acgs_deployment_report_{timestamp}.json"

        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        self.logger.info(f"  📄 Report saved: {report_path.relative_to(REPO_ROOT)}")
        return str(report_path.relative_to(REPO_ROOT))

    def _calculate_overall_success(self) -> bool:
        """Calculate overall deployment success."""
        # Check if critical infrastructure is running
        postgres_ok = self.deployment_results["infrastructure"].get("postgres", False)
        redis_ok = self.deployment_results["infrastructure"].get("redis", False)

        # Check if at least one ACGS service is running
        any_service_ok = any(self.deployment_results["services"].values())

        return postgres_ok and redis_ok and any_service_ok

    def run_deployment_and_testing(self) -> dict:
        """Run complete deployment and testing."""
        self.logger.info("🚀 Starting ACGS Service Deployment and Testing...")
        self.logger.info(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")

        # Pre-deployment checks
        if not self.check_docker_availability():
            return {"error": "Docker not available"}

        self.setup_environment_variables()

        if not self.create_docker_network():
            return {"error": "Failed to create Docker network"}

        # Deploy infrastructure
        infra_results = self.deploy_infrastructure_services()

        # For now, we'll focus on infrastructure deployment
        # ACGS services would need actual service code to be built
        self.deployment_results["services"] = {
            service: False for service in ACGS_SERVICES
        }

        # Test what we can
        self.test_service_integration()

        # Generate report
        report_path = self.generate_deployment_report()

        # Summary
        overall_success = self._calculate_overall_success()

        self.logger.info("📊 Deployment Summary:")
        self.logger.info(
            "  Infrastructure Services:"
            f" {len([s for s in infra_results.values() if s])}/2"
        )
        self.logger.info(
            f"  ACGS Services: 0/{len(ACGS_SERVICES)} (services need to be built)"
        )
        self.logger.info(
            f"  Overall Success: {'✅ PASS' if overall_success else '❌ FAIL'}"
        )
        self.logger.info(f"  Report: {report_path}")

        return self.deployment_results


def main():
    """Main deployment function."""
    print("🚀 ACGS Service Deployment and Integration Testing")
    print("=" * 55)
    print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print()

    deployer = ACGSServiceDeploymentTester()
    results = deployer.run_deployment_and_testing()

    if "error" not in results:
        print("\n✅ Deployment and testing completed!")
    else:
        print(f"\n❌ Deployment failed: {results['error']}")

    return results


if __name__ == "__main__":
    main()
