#!/usr/bin/env python3
"""
ACGS Service Integration Testing Setup

This script sets up and validates service integration testing for the ACGS platform.
It handles service discovery, health checks, and connectivity validation.
"""

import asyncio
import json
import logging
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import aiohttp


@dataclass
class ServiceEndpoint:
    """Service endpoint configuration."""

    name: str
    port: int
    url: str
    health_endpoint: str
    required: bool = True
    timeout: int = 30


@dataclass
class ServiceStatus:
    """Service status information."""

    name: str
    healthy: bool
    response_time: Optional[float] = None
    status_code: Optional[int] = None
    error: Optional[str] = None


class ACGSServiceIntegrationSetup:
    """ACGS Service Integration Testing Setup and Validation."""

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.logger = self._setup_logging()

        # ACGS Service Configuration
        self.services = [
            ServiceEndpoint("auth_service", 8016, "http://localhost:8016", "/health"),
            ServiceEndpoint("ac_service", 8001, "http://localhost:8001", "/health"),
            ServiceEndpoint(
                "integrity_service", 8002, "http://localhost:8002", "/health"
            ),
            ServiceEndpoint("fv_service", 8003, "http://localhost:8003", "/health"),
            ServiceEndpoint("gs_service", 8004, "http://localhost:8004", "/health"),
            ServiceEndpoint("pgc_service", 8005, "http://localhost:8005", "/health"),
            ServiceEndpoint("ec_service", 8006, "http://localhost:8006", "/health"),
        ]

        # Infrastructure services
        self.infrastructure = [
            ServiceEndpoint("postgres", 5439, "postgresql://localhost:5439", "", False),
            ServiceEndpoint("redis", 6389, "redis://localhost:6389", "", False),
        ]

        self.constitutional_hash = "cdd01ef066bc6cf2"

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        return logging.getLogger(__name__)

    async def check_service_health(self, service: ServiceEndpoint) -> ServiceStatus:
        """Check health of a single service."""
        start_time = time.time()

        try:
            timeout = aiohttp.ClientTimeout(total=service.timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                health_url = f"{service.url}{service.health_endpoint}"

                async with session.get(health_url) as response:
                    response_time = time.time() - start_time

                    if response.status == 200:
                        return ServiceStatus(
                            name=service.name,
                            healthy=True,
                            response_time=response_time,
                            status_code=response.status,
                        )
                    else:
                        return ServiceStatus(
                            name=service.name,
                            healthy=False,
                            response_time=response_time,
                            status_code=response.status,
                            error=f"HTTP {response.status}",
                        )

        except asyncio.TimeoutError:
            return ServiceStatus(
                name=service.name,
                healthy=False,
                error=f"Timeout after {service.timeout}s",
            )
        except Exception as e:
            return ServiceStatus(name=service.name, healthy=False, error=str(e))

    async def check_all_services(self) -> Dict[str, ServiceStatus]:
        """Check health of all services concurrently."""
        self.logger.info("🔍 Checking health of all ACGS services...")

        tasks = [self.check_service_health(service) for service in self.services]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        status_map = {}
        for result in results:
            if isinstance(result, ServiceStatus):
                status_map[result.name] = result
            else:
                self.logger.error(f"Error checking service: {result}")

        return status_map

    def check_infrastructure_connectivity(self) -> Dict[str, bool]:
        """Check infrastructure service connectivity."""
        self.logger.info("🔧 Checking infrastructure connectivity...")

        results = {}

        # Check PostgreSQL
        try:
            result = subprocess.run(
                ["pg_isready", "-h", "localhost", "-p", "5439"],
                capture_output=True,
                timeout=10,
            )
            results["postgres"] = result.returncode == 0
        except Exception as e:
            self.logger.warning(f"PostgreSQL check failed: {e}")
            results["postgres"] = False

        # Check Redis
        try:
            result = subprocess.run(
                ["redis-cli", "-h", "localhost", "-p", "6389", "ping"],
                capture_output=True,
                timeout=10,
            )
            results["redis"] = result.returncode == 0 and b"PONG" in result.stdout
        except Exception as e:
            self.logger.warning(f"Redis check failed: {e}")
            results["redis"] = False

        return results

    def start_infrastructure_services(self) -> bool:
        """Start infrastructure services if not running."""
        self.logger.info("🚀 Starting infrastructure services...")

        try:
            # Check if Docker Compose is available
            docker_compose_file = (
                self.project_root / "infrastructure/docker/docker-compose.acgs.yml"
            )

            if docker_compose_file.exists():
                cmd = [
                    "docker-compose",
                    "-f",
                    str(docker_compose_file),
                    "up",
                    "-d",
                    "postgres",
                    "redis",
                ]

                result = subprocess.run(cmd, capture_output=True, timeout=120)

                if result.returncode == 0:
                    self.logger.info("✅ Infrastructure services started successfully")
                    # Wait for services to be ready
                    time.sleep(10)
                    return True
                else:
                    self.logger.error(
                        f"Failed to start infrastructure: {result.stderr.decode()}"
                    )
                    return False
            else:
                self.logger.warning(
                    "Docker Compose file not found, assuming services are running"
                )
                return True

        except Exception as e:
            self.logger.error(f"Error starting infrastructure: {e}")
            return False

    def start_acgs_services(self) -> bool:
        """Start ACGS services."""
        self.logger.info("🚀 Starting ACGS services...")

        try:
            docker_compose_file = (
                self.project_root / "infrastructure/docker/docker-compose.acgs.yml"
            )

            if docker_compose_file.exists():
                cmd = ["docker-compose", "-f", str(docker_compose_file), "up", "-d"]

                result = subprocess.run(cmd, capture_output=True, timeout=300)

                if result.returncode == 0:
                    self.logger.info("✅ ACGS services started successfully")
                    # Wait for services to be ready
                    time.sleep(30)
                    return True
                else:
                    self.logger.error(
                        f"Failed to start ACGS services: {result.stderr.decode()}"
                    )
                    return False
            else:
                self.logger.warning("Docker Compose file not found")
                return False

        except Exception as e:
            self.logger.error(f"Error starting ACGS services: {e}")
            return False

    async def validate_service_integration(self) -> Tuple[bool, Dict]:
        """Validate complete service integration."""
        self.logger.info("🔍 Validating ACGS service integration...")

        # Check infrastructure
        infra_status = self.check_infrastructure_connectivity()

        # Check service health
        service_status = await self.check_all_services()

        # Calculate overall health
        healthy_services = sum(
            1 for status in service_status.values() if status.healthy
        )
        total_services = len(service_status)

        healthy_infra = sum(1 for status in infra_status.values() if status)
        total_infra = len(infra_status)

        overall_healthy = (
            healthy_services == total_services and healthy_infra == total_infra
        )

        report = {
            "overall_healthy": overall_healthy,
            "services": {
                "healthy": healthy_services,
                "total": total_services,
                "details": {
                    name: {
                        "healthy": status.healthy,
                        "response_time": status.response_time,
                        "error": status.error,
                    }
                    for name, status in service_status.items()
                },
            },
            "infrastructure": {
                "healthy": healthy_infra,
                "total": total_infra,
                "details": infra_status,
            },
            "constitutional_hash": self.constitutional_hash,
        }

        return overall_healthy, report

    def generate_integration_report(self, report: Dict) -> str:
        """Generate human-readable integration report."""
        lines = [
            "🏥 ACGS Service Integration Report",
            "=" * 50,
            f"Overall Status: {'✅ HEALTHY' if report['overall_healthy'] else '❌ UNHEALTHY'}",
            f"Constitutional Hash: {report['constitutional_hash']}",
            "",
            "📊 Service Status:",
            f"  Healthy: {report['services']['healthy']}/{report['services']['total']}",
            "",
        ]

        for name, details in report["services"]["details"].items():
            status_icon = "✅" if details["healthy"] else "❌"
            response_time = (
                f" ({details['response_time']:.3f}s)"
                if details["response_time"]
                else ""
            )
            error_info = f" - {details['error']}" if details["error"] else ""
            lines.append(f"  {status_icon} {name}{response_time}{error_info}")

        lines.extend(
            [
                "",
                "🔧 Infrastructure Status:",
                f"  Healthy: {report['infrastructure']['healthy']}/{report['infrastructure']['total']}",
                "",
            ]
        )

        for name, healthy in report["infrastructure"]["details"].items():
            status_icon = "✅" if healthy else "❌"
            lines.append(f"  {status_icon} {name}")

        return "\n".join(lines)

    async def setup_integration_testing(self, start_services: bool = False) -> bool:
        """Complete integration testing setup."""
        self.logger.info("🚀 Setting up ACGS integration testing environment...")

        if start_services:
            # Start infrastructure services
            if not self.start_infrastructure_services():
                self.logger.error("Failed to start infrastructure services")
                return False

            # Start ACGS services
            if not self.start_acgs_services():
                self.logger.error("Failed to start ACGS services")
                return False

        # Validate integration
        healthy, report = await self.validate_service_integration()

        # Generate and save report
        report_text = self.generate_integration_report(report)
        print(report_text)

        # Save detailed report
        reports_dir = self.project_root / "reports"
        reports_dir.mkdir(exist_ok=True)

        with open(reports_dir / "service_integration_report.json", "w") as f:
            json.dump(report, f, indent=2)

        with open(reports_dir / "service_integration_report.txt", "w") as f:
            f.write(report_text)

        if healthy:
            self.logger.info("✅ Service integration setup completed successfully!")
        else:
            self.logger.error(
                "❌ Service integration setup failed - some services are unhealthy"
            )

        return healthy


async def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="ACGS Service Integration Setup")
    parser.add_argument(
        "--start-services", action="store_true", help="Start services automatically"
    )
    parser.add_argument("--project-root", type=Path, help="Project root directory")

    args = parser.parse_args()

    setup = ACGSServiceIntegrationSetup(args.project_root)
    success = await setup.setup_integration_testing(args.start_services)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
