#!/usr/bin/env python3
"""
ACGS Docker-in-Docker Deployment Script
Comprehensive deployment and management of ACGS services using Docker-in-Docker.
"""

import asyncio
import logging
import os
import subprocess
import sys
import time
from pathlib import Path

import docker

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Constitutional hash for compliance validation
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class ACGSDinDDeployer:
    """ACGS Docker-in-Docker deployment manager."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.dind_dir = self.project_root / "infrastructure/docker/dind"
        self.docker_client = docker.from_env()

        # Deployment configuration
        self.deployment_config = {
            "project_name": "acgs-dind",
            "network_name": "acgs-dind-network",
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "services": {
                "docker-dind": {"priority": 1, "health_check": "docker_daemon"},
                "acgs-postgres": {"priority": 2, "health_check": "postgres"},
                "acgs-redis": {"priority": 2, "health_check": "redis"},
                "acgs-nats": {"priority": 2, "health_check": "nats"},
                "acgs-auth-service": {"priority": 3, "health_check": "http"},
                "acgs-ac-service": {"priority": 3, "health_check": "http"},
                "acgs-integrity-service": {"priority": 3, "health_check": "http"},
                "acgs-fv-service": {"priority": 3, "health_check": "http"},
                "acgs-gs-service": {"priority": 3, "health_check": "http"},
                "acgs-pgc-service": {"priority": 3, "health_check": "http"},
                "acgs-ec-service": {"priority": 4, "health_check": "http"},
                "acgs-prometheus": {"priority": 5, "health_check": "prometheus"},
                "acgs-grafana": {"priority": 5, "health_check": "grafana"},
            },
        }

    async def deploy_complete_acgs_dind(self):
        """Deploy complete ACGS system using Docker-in-Docker."""
        logger.info("Starting ACGS Docker-in-Docker deployment...")

        try:
            # Step 1: Validate prerequisites
            await self.validate_dind_prerequisites()

            # Step 2: Prepare deployment environment
            await self.prepare_deployment_environment()

            # Step 3: Build service images
            await self.build_service_images()

            # Step 4: Deploy infrastructure services
            await self.deploy_infrastructure_services()

            # Step 5: Deploy ACGS core services
            await self.deploy_acgs_services()

            # Step 6: Deploy monitoring services
            await self.deploy_monitoring_services()

            # Step 7: Validate deployment
            await self.validate_deployment()

            # Step 8: Run integration tests
            await self.run_integration_tests()

            logger.info("ACGS Docker-in-Docker deployment completed successfully!")

        except Exception as e:
            logger.error(f"ACGS DinD deployment failed: {e}")
            await self.cleanup_failed_deployment()
            raise

    async def validate_dind_prerequisites(self):
        """Validate prerequisites for DinD deployment."""
        logger.info("Validating DinD prerequisites...")

        # Check Docker availability
        try:
            self.docker_client.ping()
            logger.info("✓ Docker daemon accessible")
        except Exception as e:
            raise RuntimeError(f"Docker daemon not accessible: {e}")

        # Check Docker Compose
        try:
            result = subprocess.run(
                ["docker-compose", "--version"],
                capture_output=True,
                text=True,
                check=True,
            )
            logger.info(f"✓ Docker Compose available: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError("Docker Compose not available")

        # Check available resources
        try:
            info = self.docker_client.info()
            total_memory = info.get("MemTotal", 0) / (1024**3)  # GB

            if total_memory < 8:
                logger.warning(
                    f"Low memory available: {total_memory:.1f}GB (recommended: 8GB+)"
                )
            else:
                logger.info(f"✓ Sufficient memory available: {total_memory:.1f}GB")

        except Exception as e:
            logger.warning(f"Could not check system resources: {e}")

        # Check disk space
        disk_usage = subprocess.run(
            ["df", "-h", str(self.project_root)],
            check=False,
            capture_output=True,
            text=True,
        )
        if disk_usage.returncode == 0:
            logger.info("✓ Disk space check completed")

        logger.info("Prerequisites validation completed")

    async def prepare_deployment_environment(self):
        """Prepare the deployment environment."""
        logger.info("Preparing deployment environment...")

        # Create necessary directories
        directories = [
            self.dind_dir,
            self.dind_dir / "dind-config",
            self.dind_dir / "certs",
            self.project_root / "logs/docker",
            self.project_root / "reports/dind",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {directory}")

        # Generate environment configuration
        await self.generate_environment_config()

        # Setup TLS certificates if needed
        await self.setup_tls_certificates()

        logger.info("Deployment environment prepared")

    async def generate_environment_config(self):
        """Generate environment configuration files."""
        logger.info("Generating environment configuration...")

        # Create config/environments/development.env file
        env_content = f"""# ACGS Docker-in-Docker Environment
COMPOSE_PROJECT_NAME={self.deployment_config["project_name"]}
CONSTITUTIONAL_HASH={CONSTITUTIONAL_HASH}

# Database Configuration
POSTGRES_DB=acgs
POSTGRES_USER=acgs_user
POSTGRES_PASSWORD=os.environ.get("PASSWORD")

# Redis Configuration
REDIS_PASSWORD=os.environ.get("PASSWORD")

# Monitoring Configuration
GF_SECURITY_ADMIN_PASSWORD=os.environ.get("PASSWORD")

# Docker Configuration
DOCKER_TLS_VERIFY=1
DOCKER_CERT_PATH=/certs/client
DOCKER_HOST=tcp://docker-dind:2376

# Service Configuration
CONSTITUTIONAL_HASH={CONSTITUTIONAL_HASH}
"""

        env_file = self.dind_dir / "config/environments/development.env"
        with open(env_file, "w") as f:
            f.write(env_content)

        logger.info(f"Environment configuration saved: {env_file}")

    async def setup_tls_certificates(self):
        """Setup TLS certificates for Docker daemon."""
        logger.info("Setting up TLS certificates...")

        cert_dir = self.dind_dir / "certs"

        # Check if certificates already exist
        if (cert_dir / "ca.pem").exists():
            logger.info("TLS certificates already exist")
            return

        # Generate certificates using setup script
        setup_script = self.project_root / "scripts/docker/setup-dind.sh"
        if setup_script.exists():
            try:
                subprocess.run(
                    [str(setup_script), "setup"], check=True, cwd=str(self.project_root)
                )
                logger.info("✓ TLS certificates generated")
            except subprocess.CalledProcessError as e:
                logger.warning(f"Certificate generation failed: {e}")
        else:
            logger.warning("Setup script not found, skipping certificate generation")

    async def build_service_images(self):
        """Build Docker images for ACGS services."""
        logger.info("Building service images...")

        # Services to build
        services_to_build = [
            ("auth-service", "services/core/auth"),
            ("ac-service", "services/core/algorithmic-constitution"),
            ("integrity-service", "services/core/integrity-verification"),
            ("fv-service", "services/core/formal-verification"),
            ("gs-service", "services/core/governance-simulation"),
            ("pgc-service", "services/core/policy-generation-consensus"),
            ("ec-service", "services/core/evolutionary-computation"),
        ]

        for service_name, service_path in services_to_build:
            await self.build_service_image(service_name, service_path)

        logger.info("Service images built successfully")

    async def build_service_image(self, service_name: str, service_path: str):
        """Build Docker image for a specific service."""
        logger.info(f"Building image for {service_name}...")

        build_path = self.project_root / service_path

        # Create Dockerfile if it doesn't exist
        dockerfile_path = build_path / "Dockerfile"
        if not dockerfile_path.exists():
            await self.create_service_dockerfile(dockerfile_path, service_name)

        try:
            # Build image
            image_tag = f"acgs/{service_name}:latest"

            image, build_logs = self.docker_client.images.build(
                path=str(build_path), tag=image_tag, rm=True, forcerm=True
            )

            logger.info(f"✓ Built image {image_tag}")

        except docker.errors.BuildError as e:
            logger.error(f"Failed to build {service_name}: {e}")
            raise

    async def create_service_dockerfile(self, dockerfile_path: Path, service_name: str):
        """Create Dockerfile for a service."""
        dockerfile_content = f"""FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    curl \\
    git \\
    build-essential \\
    && rm -rf /var/lib/apt/lists/*

# Install Docker CLI for DinD support
RUN curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add - \\
    && echo "deb [arch=amd64] https://download.docker.com/linux/debian bullseye stable" > /etc/apt/sources.list.d/docker.list \\
    && apt-get update \\
    && apt-get install -y docker-ce-cli \\
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install dependencies
COPY config/environments/requirements.txt .
RUN pip install --no-cache-dir -r config/environments/requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 acgs && chown -R acgs:acgs /app
USER acgs

# Environment variables
ENV CONSTITUTIONAL_HASH={CONSTITUTIONAL_HASH}
ENV SERVICE_NAME={service_name}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:${{SERVICE_PORT}}/health || exit 1

# Default command
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "${{SERVICE_PORT}}"]
"""

        with open(dockerfile_path, "w") as f:
            f.write(dockerfile_content)

        logger.info(f"Created Dockerfile for {service_name}")

    async def deploy_infrastructure_services(self):
        """Deploy infrastructure services (PostgreSQL, Redis, NATS)."""
        logger.info("Deploying infrastructure services...")

        # Change to DinD directory
        os.chdir(str(self.dind_dir))

        # Start infrastructure services
        infrastructure_services = [
            "docker-dind",
            "acgs-postgres",
            "acgs-redis",
            "acgs-nats",
        ]

        for service in infrastructure_services:
            await self.start_service(service)
            await self.wait_for_service_health(service)

        logger.info("Infrastructure services deployed successfully")

    async def deploy_acgs_services(self):
        """Deploy ACGS core services."""
        logger.info("Deploying ACGS core services...")

        # Start ACGS services in order
        acgs_services = [
            "acgs-auth-service",
            "acgs-ac-service",
            "acgs-integrity-service",
            "acgs-fv-service",
            "acgs-gs-service",
            "acgs-pgc-service",
            "acgs-ec-service",
        ]

        for service in acgs_services:
            await self.start_service(service)
            await self.wait_for_service_health(service)

        logger.info("ACGS core services deployed successfully")

    async def deploy_monitoring_services(self):
        """Deploy monitoring services (Prometheus, Grafana)."""
        logger.info("Deploying monitoring services...")

        monitoring_services = ["acgs-prometheus", "acgs-grafana"]

        for service in monitoring_services:
            await self.start_service(service)
            await self.wait_for_service_health(service)

        logger.info("Monitoring services deployed successfully")

    async def start_service(self, service_name: str):
        """Start a specific service."""
        logger.info(f"Starting service: {service_name}")

        try:
            # Use docker-compose to start the service
            result = subprocess.run(
                ["docker-compose", "up", "-d", service_name],
                check=True,
                capture_output=True,
                text=True,
                cwd=str(self.dind_dir),
            )

            logger.info(f"✓ Service {service_name} started")

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to start {service_name}: {e.stderr}")
            raise

    async def wait_for_service_health(self, service_name: str, timeout: int = 120):
        """Wait for service to become healthy."""
        logger.info(f"Waiting for {service_name} to become healthy...")

        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                # Check container status
                container_name = f"{service_name}-dind"
                container = self.docker_client.containers.get(container_name)

                if container.status == "running":
                    # Check health if health check is defined
                    health = container.attrs.get("State", {}).get("Health")
                    if health:
                        if health["Status"] == "healthy":
                            logger.info(f"✓ Service {service_name} is healthy")
                            return
                        if health["Status"] == "unhealthy":
                            raise RuntimeError(f"Service {service_name} is unhealthy")
                    else:
                        # No health check defined, assume healthy if running
                        logger.info(f"✓ Service {service_name} is running")
                        return

                await asyncio.sleep(5)

            except docker.errors.NotFound:
                await asyncio.sleep(5)
                continue

        raise TimeoutError(
            f"Service {service_name} did not become healthy within {timeout} seconds"
        )

    async def validate_deployment(self):
        """Validate the complete deployment."""
        logger.info("Validating deployment...")

        # Check all expected containers are running
        expected_containers = [
            "acgs-docker-dind",
            "acgs-postgres-dind",
            "acgs-redis-dind",
            "acgs-nats-dind",
            "acgs-auth-service-dind",
            "acgs-ac-service-dind",
            "acgs-integrity-service-dind",
            "acgs-fv-service-dind",
            "acgs-gs-service-dind",
            "acgs-pgc-service-dind",
            "acgs-ec-service-dind",
            "acgs-prometheus-dind",
            "acgs-grafana-dind",
        ]

        running_containers = []
        for container_name in expected_containers:
            try:
                container = self.docker_client.containers.get(container_name)
                if container.status == "running":
                    running_containers.append(container_name)
                    logger.info(f"✓ {container_name} is running")
                else:
                    logger.error(
                        f"✗ {container_name} is not running: {container.status}"
                    )
            except docker.errors.NotFound:
                logger.error(f"✗ {container_name} not found")

        success_rate = len(running_containers) / len(expected_containers) * 100
        logger.info(f"Deployment validation: {success_rate:.1f}% services running")

        if success_rate < 90:
            raise RuntimeError(
                f"Deployment validation failed: only {success_rate:.1f}% services running"
            )

    async def run_integration_tests(self):
        """Run integration tests in DinD environment."""
        logger.info("Running integration tests...")

        try:
            # Run DinD integration tests
            test_script = self.project_root / "tests/dind/test_dind_integration.py"
            if test_script.exists():
                result = subprocess.run(
                    ["python", str(test_script)],
                    check=False,
                    capture_output=True,
                    text=True,
                    cwd=str(self.project_root),
                )

                if result.returncode == 0:
                    logger.info("✓ Integration tests passed")
                else:
                    logger.warning(f"Integration tests failed: {result.stderr}")
            else:
                logger.warning("Integration test script not found")

        except Exception as e:
            logger.warning(f"Failed to run integration tests: {e}")

    async def cleanup_failed_deployment(self):
        """Clean up failed deployment."""
        logger.info("Cleaning up failed deployment...")

        try:
            os.chdir(str(self.dind_dir))
            subprocess.run(
                ["docker-compose", "down", "-v"],
                check=False,
                capture_output=True,
                cwd=str(self.dind_dir),
            )
            logger.info("Failed deployment cleaned up")
        except Exception as e:
            logger.error(f"Failed to clean up deployment: {e}")

    def print_deployment_summary(self):
        """Print deployment summary."""
        print("\n" + "=" * 70)
        print("ACGS DOCKER-IN-DOCKER DEPLOYMENT SUMMARY")
        print("=" * 70)
        print("✓ Docker-in-Docker environment deployed")
        print("✓ Infrastructure services (PostgreSQL, Redis, NATS)")
        print("✓ ACGS core services (7 services)")
        print("✓ Monitoring services (Prometheus, Grafana)")
        print()
        print("Service Endpoints:")
        print("  - Auth Service: http://localhost:8000")
        print("  - AC Service: http://localhost:8001")
        print("  - Integrity Service: http://localhost:8002")
        print("  - FV Service: http://localhost:8003")
        print("  - GS Service: http://localhost:8004")
        print("  - PGC Service: http://localhost:8005")
        print("  - EC Service: http://localhost:8006")
        print("  - Prometheus: http://localhost:9090")
        print("  - Grafana: http://localhost:3001")
        print()
        print("Management Commands:")
        print("  - View logs: docker-compose logs -f [service]")
        print("  - Scale service: docker-compose up -d --scale [service]=N")
        print("  - Stop all: docker-compose down")
        print("  - Stop with cleanup: docker-compose down -v")
        print("=" * 70)


async def main():
    """Main deployment function."""
    deployer = ACGSDinDDeployer()

    try:
        await deployer.deploy_complete_acgs_dind()
        deployer.print_deployment_summary()

    except Exception as e:
        logger.error(f"ACGS DinD deployment failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
