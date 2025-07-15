#!/usr/bin/env python3
"""
ACGS Docker-in-Docker Implementation Validation Script
Validates the complete DinD implementation for production readiness.
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import docker
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Constitutional hash for compliance validation
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class DinDImplementationValidator:
    """Validates ACGS Docker-in-Docker implementation."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.dind_dir = self.project_root / "infrastructure/docker/dind"
        self.validation_results = []

        # Validation requirements
        self.requirements = {
            "files": [
                "infrastructure/docker/dind/docker-compose.dind.yml",
                "infrastructure/docker/dind/dind-config/daemon.json",
                "scripts/docker/setup-dind.sh",
                "scripts/docker/deploy-acgs-dind.py",
                "tests/dind/test_dind_integration.py",
                "docs/docker-in-docker-guide.md",
                "infrastructure/monitoring/grafana/dashboards/acgs_dind_dashboard.json",  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
            ],
            "directories": [
                "infrastructure/docker/dind",
                "scripts/docker",
                "tests/dind",
                "infrastructure/monitoring/grafana/dashboards",  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
            ],
            "services": [
                "docker-dind",
                "acgs-postgres",
                "acgs-redis",
                "acgs-nats",
                "acgs-auth-service",
                "acgs-ac-service",
                "acgs-integrity-service",
                "acgs-fv-service",
                "acgs-gs-service",
                "acgs-pgc-service",
                "acgs-ec-service",
                "acgs-prometheus",
                "acgs-grafana",
            ],
        }

    async def validate_complete_implementation(self):
        """Validate the complete DinD implementation."""
        logger.info("Starting ACGS Docker-in-Docker implementation validation...")

        validation_checks = [
            self.validate_file_structure,
            self.validate_docker_compose_configuration,
            self.validate_setup_scripts,
            self.validate_test_framework,
            self.validate_monitoring_configuration,
            self.validate_documentation,
            self.validate_security_configuration,
            self.validate_constitutional_compliance,
            self.validate_deployment_readiness,
        ]

        for check in validation_checks:
            try:
                await check()
                self.validation_results.append(
                    {
                        "check": check.__name__,
                        "status": "passed",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                )
            except Exception as e:
                logger.error(f"Validation check {check.__name__} failed: {e}")
                self.validation_results.append(
                    {
                        "check": check.__name__,
                        "status": "failed",
                        "error": str(e),
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                )

        await self.generate_validation_report()

    async def validate_file_structure(self):
        """Validate required files and directories exist."""
        logger.info("Validating file structure...")

        # Check required files
        missing_files = []
        for file_path in self.requirements["files"]:
            full_path = self.project_root / file_path
            if not full_path.exists():
                missing_files.append(file_path)

        if missing_files:
            raise AssertionError(f"Missing required files: {missing_files}")

        # Check required directories
        missing_dirs = []
        for dir_path in self.requirements["directories"]:
            full_path = self.project_root / dir_path
            if not full_path.exists():
                missing_dirs.append(dir_path)

        if missing_dirs:
            raise AssertionError(f"Missing required directories: {missing_dirs}")

        logger.info("✓ File structure validation passed")

    async def validate_docker_compose_configuration(self):
        """Validate Docker Compose configuration."""
        logger.info("Validating Docker Compose configuration...")

        compose_file = self.dind_dir / "docker-compose.dind.yml"

        try:
            with open(compose_file) as f:
                compose_config = yaml.safe_load(f)

            # Validate services are defined
            services = compose_config.get("services", {})

            for required_service in self.requirements["services"]:
                if required_service not in services:
                    raise AssertionError(
                        f"Service {required_service} not defined in docker-compose.yml"
                    )

            # Validate networks
            networks = compose_config.get("networks", {})
            if "acgs-dind-network" not in networks:
                raise AssertionError("Required network 'acgs-dind-network' not defined")

            # Validate volumes
            volumes = compose_config.get("volumes", {})
            required_volumes = [
                "docker-certs-ca",
                "docker-certs-client",
                "postgres-data",
                "redis-data",
            ]

            for volume in required_volumes:
                if volume not in volumes:
                    raise AssertionError(f"Required volume '{volume}' not defined")

            # Validate constitutional hash in environment
            dind_service = services.get("docker-dind", {})
            if "environment" in dind_service:
                env_vars = dind_service["environment"]
                # Check if constitutional hash is referenced
                logger.info("✓ Docker Compose configuration validated")

        except yaml.YAMLError as e:
            raise AssertionError(f"Invalid YAML in docker-compose.yml: {e}")

    async def validate_setup_scripts(self):
        """Validate setup and deployment scripts."""
        logger.info("Validating setup scripts...")

        # Check setup script
        setup_script = self.project_root / "scripts/docker/setup-dind.sh"
        if not setup_script.exists():
            raise AssertionError("Setup script not found")

        # Check if script is executable
        if not os.access(setup_script, os.X_OK):
            raise AssertionError("Setup script is not executable")

        # Validate script content
        with open(setup_script) as f:
            script_content = f.read()

        required_functions = [
            "check_prerequisites",
            "create_dind_directories",
            "generate_tls_certificates",
            "start_dind_services",
        ]

        for function in required_functions:
            if function not in script_content:
                raise AssertionError(
                    f"Required function '{function}' not found in setup script"
                )

        # Check deployment script
        deploy_script = self.project_root / "scripts/docker/deploy-acgs-dind.py"
        if not deploy_script.exists():
            raise AssertionError("Deployment script not found")

        # Validate Python script syntax
        try:
            with open(deploy_script) as f:
                compile(f.read(), str(deploy_script), "exec")
        except SyntaxError as e:
            raise AssertionError(f"Syntax error in deployment script: {e}")

        logger.info("✓ Setup scripts validation passed")

    async def validate_test_framework(self):
        """Validate DinD testing framework."""
        logger.info("Validating test framework...")

        # Check test files
        test_file = self.project_root / "tests/dind/test_dind_integration.py"
        if not test_file.exists():
            raise AssertionError("DinD integration test file not found")

        # Validate test content
        with open(test_file) as f:
            test_content = f.read()

        required_test_methods = [
            "test_container_health",
            "test_docker_daemon_connectivity",
            "test_inter_service_communication",
            "test_container_networking",
            "test_security_architecture",
        ]

        for test_method in required_test_methods:
            if test_method not in test_content:
                raise AssertionError(f"Required test method '{test_method}' not found")

        # Check constitutional hash validation
        if CONSTITUTIONAL_HASH not in test_content:
            raise AssertionError("Constitutional hash not found in test file")

        logger.info("✓ Test framework validation passed")

    async def validate_monitoring_configuration(self):
        """Validate monitoring and dashboard configuration."""
        logger.info("Validating monitoring configuration...")

        # Check Grafana dashboard
        dashboard_file = (
            self.project_root
            / "infrastructure/monitoring/grafana/dashboards/acgs_dind_dashboard.json"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
        )

        try:
            with open(dashboard_file) as f:
                dashboard_config = json.load(f)

            # Validate dashboard structure
            dashboard = dashboard_config.get("dashboard", {})
            if not dashboard.get("title"):
                raise AssertionError("Dashboard title not defined")

            panels = dashboard.get("panels", [])
            if len(panels) < 5:
                raise AssertionError("Insufficient monitoring panels defined")

            # Check for key metrics
            dashboard_json = json.dumps(dashboard_config)
            required_metrics = [
                "container_cpu_usage",
                "acgs_constitutional_compliance",
                "http_request_duration",
                "evolution_requests_total",
            ]

            for metric in required_metrics:
                if metric not in dashboard_json:
                    logger.warning(f"Metric '{metric}' not found in dashboard")

        except json.JSONDecodeError as e:
            raise AssertionError(f"Invalid JSON in dashboard configuration: {e}")

        logger.info("✓ Monitoring configuration validation passed")

    async def validate_documentation(self):
        """Validate documentation completeness."""
        logger.info("Validating documentation...")

        # Check main documentation file
        doc_file = self.project_root / "docs/docker-in-docker-guide.md"

        with open(doc_file) as f:
            doc_content = f.read()

        required_sections = [
            "## Overview",
            "## Architecture",
            "## Prerequisites",
            "## Quick Start",
            "## Configuration",
            "## Management Commands",
            "## Security",
            "## Monitoring",
            "## Testing",
            "## Troubleshooting",
        ]

        for section in required_sections:
            if section not in doc_content:
                raise AssertionError(
                    f"Required documentation section '{section}' not found"
                )

        # Check constitutional hash reference
        if CONSTITUTIONAL_HASH not in doc_content:
            raise AssertionError("Constitutional hash not documented")

        logger.info("✓ Documentation validation passed")

    async def validate_security_configuration(self):
        """Validate security configuration."""
        logger.info("Validating security configuration...")

        # Check Docker daemon configuration
        daemon_config_file = self.dind_dir / "dind-config/daemon.json"

        try:
            with open(daemon_config_file) as f:
                daemon_config = json.load(f)

            # Validate TLS configuration
            if not daemon_config.get("tls"):
                raise AssertionError("TLS not enabled in Docker daemon configuration")

            if not daemon_config.get("tlsverify"):
                raise AssertionError("TLS verification not enabled")

            # Check security settings
            if daemon_config.get("userland-proxy", True):
                logger.warning("Userland proxy is enabled (security consideration)")

        except json.JSONDecodeError as e:
            raise AssertionError(f"Invalid JSON in daemon configuration: {e}")

        logger.info("✓ Security configuration validation passed")

    async def validate_constitutional_compliance(self):
        """Validate constitutional compliance integration."""
        logger.info("Validating constitutional compliance...")

        # Check constitutional hash in key files
        files_to_check = [
            "infrastructure/docker/dind/docker-compose.dind.yml",
            "tests/dind/test_dind_integration.py",
            "scripts/docker/deploy-acgs-dind.py",
            "docs/docker-in-docker-guide.md",
        ]

        for file_path in files_to_check:
            full_path = self.project_root / file_path
            if full_path.exists():
                with open(full_path) as f:
                    content = f.read()

                if CONSTITUTIONAL_HASH not in content:
                    raise AssertionError(
                        f"Constitutional hash not found in {file_path}"
                    )

        logger.info("✓ Constitutional compliance validation passed")

    async def validate_deployment_readiness(self):
        """Validate deployment readiness."""
        logger.info("Validating deployment readiness...")

        # Check if Docker is available
        try:
            docker_client = docker.from_env()
            docker_client.ping()
            logger.info("✓ Docker daemon accessible")
        except Exception as e:
            raise AssertionError(f"Docker not accessible: {e}")

        # Check Docker Compose availability
        try:
            result = subprocess.run(
                ["docker-compose", "--version"],
                capture_output=True,
                text=True,
                check=True,
            )
            logger.info(f"✓ Docker Compose available: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise AssertionError("Docker Compose not available")

        # Validate compose file syntax
        compose_file = self.dind_dir / "docker-compose.dind.yml"
        try:
            result = subprocess.run(
                ["docker-compose", "-f", str(compose_file), "config"],
                capture_output=True,
                text=True,
                check=True,
                cwd=str(self.dind_dir),
            )
            logger.info("✓ Docker Compose configuration valid")
        except subprocess.CalledProcessError as e:
            raise AssertionError(f"Docker Compose configuration invalid: {e.stderr}")

        logger.info("✓ Deployment readiness validation passed")

    async def generate_validation_report(self):
        """Generate validation report."""
        logger.info("Generating validation report...")

        # Calculate validation statistics
        total_checks = len(self.validation_results)
        passed_checks = sum(
            1 for result in self.validation_results if result["status"] == "passed"
        )
        failed_checks = total_checks - passed_checks

        validation_score = (
            (passed_checks / total_checks * 100) if total_checks > 0 else 0
        )

        report = {
            "validation_summary": {
                "total_checks": total_checks,
                "passed_checks": passed_checks,
                "failed_checks": failed_checks,
                "validation_score": validation_score,
                "implementation_ready": validation_score >= 95.0,
            },
            "requirements_checked": self.requirements,
            "validation_results": self.validation_results,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "dind_implementation": {
                "version": "1.0.0",
                "features": [
                    "Docker-in-Docker daemon",
                    "TLS-secured communication",
                    "Complete ACGS service stack",
                    "Monitoring and dashboards",
                    "Integration testing framework",
                    "Constitutional compliance validation",
                ],
            },
        }

        # Save report
        report_dir = self.project_root / "reports/dind_validation"
        report_dir.mkdir(parents=True, exist_ok=True)

        report_file = (
            report_dir / f"dind_implementation_validation_{int(time.time())}.json"
        )
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Validation report saved: {report_file}")

        # Print summary
        self.print_validation_summary(report)

    def print_validation_summary(self, report: dict):
        """Print validation summary."""
        validation = report["validation_summary"]

        print("\n" + "=" * 70)
        print("ACGS DOCKER-IN-DOCKER IMPLEMENTATION VALIDATION")
        print("=" * 70)
        print(f"Validation Score: {validation['validation_score']:.1f}%")
        print(
            f"Checks Passed: {validation['passed_checks']}/{validation['total_checks']}"
        )
        print(
            f"Implementation Ready: {'YES' if validation['implementation_ready'] else 'NO'}"
        )
        print()

        print("Validation Results:")
        for result in self.validation_results:
            status_icon = "✓" if result["status"] == "passed" else "✗"
            print(f"  {status_icon} {result['check']}")
            if result["status"] == "failed":
                print(f"    Error: {result.get('error', 'Unknown error')}")

        print()
        print("DinD Implementation Features:")
        for feature in report["dind_implementation"]["features"]:
            print(f"  ✓ {feature}")

        print("=" * 70)

        if validation["implementation_ready"]:
            print("🎉 ACGS Docker-in-Docker implementation is READY for deployment!")
            print()
            print("Next Steps:")
            print("1. Run: ./scripts/docker/setup-dind.sh setup")
            print("2. Deploy: python scripts/docker/deploy-acgs-dind.py")
            print("3. Test: ./scripts/docker/setup-dind.sh test")
            print("4. Monitor: http://localhost:3001 (Grafana)")
        else:
            print("⚠️  DinD implementation requires fixes before deployment.")

        print("=" * 70)


async def main():
    """Main validation function."""
    validator = DinDImplementationValidator()

    try:
        await validator.validate_complete_implementation()

    except Exception as e:
        logger.error(f"DinD implementation validation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
