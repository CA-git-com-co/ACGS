#!/usr/bin/env python3
"""
ACGS Observability Stack Deployment Script
Deploy and configure the complete observability stack with constitutional compliance monitoring.
"""

import argparse
import asyncio
import logging
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Constitutional hash for compliance validation
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class ObservabilityStackDeployer:
    """Deploy and manage the ACGS observability stack."""

    def __init__(self, constitutional_hash: str = CONSTITUTIONAL_HASH):
        self.constitutional_hash = constitutional_hash
        self.stack_components = [
            "jaeger",
            "elasticsearch",
            "prometheus",
            "grafana",
            "otel-collector",
            "loki",
            "promtail",
            "alertmanager",
            "node-exporter",
            "cadvisor",
            "constitutional-monitor",
            "observability-dashboard",
        ]

        # Deployment configuration
        self.deployment_config = {
            "environment": "production",
            "namespace": "acgs-observability",
            "retention_days": 30,
            "high_availability": True,
            "constitutional_monitoring": True,
        }

    async def deploy_observability_stack(self, components: list = None) -> bool:
        """Deploy the complete observability stack."""
        logger.info("Starting ACGS Observability Stack deployment...")

        if components is None:
            components = self.stack_components

        try:
            # Pre-deployment checks
            if not await self.pre_deployment_checks():
                logger.error("Pre-deployment checks failed")
                return False

            # Create necessary directories
            await self.create_directories()

            # Generate configuration files
            await self.generate_configurations()

            # Deploy infrastructure components first
            infrastructure_components = ["elasticsearch", "prometheus", "loki"]
            for component in infrastructure_components:
                if component in components:
                    success = await self.deploy_component(component)
                    if not success:
                        logger.error(f"Failed to deploy {component}")
                        return False
                    await asyncio.sleep(10)  # Wait for component to stabilize

            # Deploy observability components
            observability_components = [
                "jaeger",
                "otel-collector",
                "grafana",
                "alertmanager",
            ]
            for component in observability_components:
                if component in components:
                    success = await self.deploy_component(component)
                    if not success:
                        logger.error(f"Failed to deploy {component}")
                        return False
                    await asyncio.sleep(5)

            # Deploy monitoring components
            monitoring_components = ["node-exporter", "cadvisor", "promtail"]
            for component in monitoring_components:
                if component in components:
                    success = await self.deploy_component(component)
                    if not success:
                        logger.error(f"Failed to deploy {component}")
                        return False

            # Deploy constitutional compliance components
            constitutional_components = [
                "constitutional-monitor",
                "observability-dashboard",
            ]
            for component in constitutional_components:
                if component in components:
                    success = await self.deploy_component(component)
                    if not success:
                        logger.error(f"Failed to deploy {component}")
                        return False

            # Post-deployment configuration
            await self.post_deployment_configuration()

            # Verify deployment
            if await self.verify_deployment(components):
                logger.info("✅ Observability stack deployment completed successfully")
                await self.print_deployment_summary()
                return True
            logger.error("❌ Deployment verification failed")
            return False

        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            return False

    async def pre_deployment_checks(self) -> bool:
        """Perform pre-deployment checks."""
        logger.info("Performing pre-deployment checks...")

        try:
            # Check Docker
            result = subprocess.run(
                ["docker", "--version"], check=False, capture_output=True, text=True
            )
            if result.returncode != 0:
                logger.error("Docker is not installed or not running")
                return False

            # Check Docker Compose
            result = subprocess.run(
                ["docker-compose", "--version"],
                check=False,
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                logger.error("Docker Compose is not installed")
                return False

            # Check available disk space (minimum 10GB)
            import shutil

            free_space = shutil.disk_usage(".").free / (1024**3)  # GB
            if free_space < 10:
                logger.error(
                    f"Insufficient disk space: {free_space:.1f}GB available, 10GB required"
                )
                return False

            # Check available memory (minimum 4GB)
            import psutil

            available_memory = psutil.virtual_memory().available / (1024**3)  # GB
            if available_memory < 4:
                logger.error(
                    f"Insufficient memory: {available_memory:.1f}GB available, 4GB required"
                )
                return False

            # Validate constitutional hash
            if self.constitutional_hash != CONSTITUTIONAL_HASH:
                logger.error("Invalid constitutional hash")
                return False

            logger.info("✅ Pre-deployment checks passed")
            return True

        except Exception as e:
            logger.error(f"Pre-deployment checks failed: {e}")
            return False

    async def create_directories(self):
        """Create necessary directories for the observability stack."""
        directories = [
            "infrastructure/observability/grafana/dashboards",  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
            "infrastructure/observability/grafana/datasources",  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
            "infrastructure/observability/prometheus-rules",
            "logs/observability",
            "data/prometheus",
            "data/grafana",
            "data/elasticsearch",
            "data/loki",
            "reports/observability",
        ]

        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created directory: {directory}")

    async def generate_configurations(self):
        """Generate configuration files for observability components."""
        logger.info("Generating configuration files...")

        # Generate Prometheus configuration
        await self.generate_prometheus_config()

        # Generate Grafana datasources
        await self.generate_grafana_datasources()

        # Generate AlertManager configuration
        await self.generate_alertmanager_config()

        # Generate Loki configuration
        await self.generate_loki_config()

        # Generate Promtail configuration
        await self.generate_promtail_config()

    async def generate_prometheus_config(self):
        """Generate Prometheus configuration."""
        config = {
            "global": {
                "scrape_interval": "15s",
                "evaluation_interval": "15s",
                "external_labels": {
                    "constitutional_hash": self.constitutional_hash,
                    "environment": "production",
                    "cluster": "acgs-observability",
                },
            },
            "rule_files": ["/etc/prometheus/rules/*.yml"],
            "alerting": {
                "alertmanagers": [
                    {"static_configs": [{"targets": ["alertmanager:9093"]}]}
                ]
            },
            "scrape_configs": [
                {
                    "job_name": "acgs-services",
                    "static_configs": [
                        {
                            "targets": [
                                "host.docker.internal:8000",  # auth-service
                                "host.docker.internal:8001",  # ac-service
                                "host.docker.internal:8002",  # integrity-service
                                "host.docker.internal:8003",  # fv-service
                                "host.docker.internal:8004",  # gs-service
                                "host.docker.internal:8005",  # pgc-service
                                "host.docker.internal:8006",  # ec-service
                            ]
                        }
                    ],
                    "scrape_interval": "10s",
                    "metrics_path": "/metrics",
                    "labels": {"constitutional_hash": self.constitutional_hash},
                },
                {
                    "job_name": "observability-stack",
                    "static_configs": [
                        {
                            "targets": [
                                "prometheus:9090",
                                "node-exporter:9100",
                                "cadvisor:8080",
                                "otel-collector:8889",
                                "constitutional-monitor:8111",
                                "observability-dashboard:8112",
                            ]
                        }
                    ],
                    "scrape_interval": "30s",
                },
            ],
        }

        config_path = Path("infrastructure/observability/prometheus-observability.yml")
        with open(config_path, "w") as f:
            import yaml

            yaml.dump(config, f, default_flow_style=False)

        logger.info("Generated Prometheus configuration")

    async def generate_grafana_datasources(self):
        """Generate Grafana datasource configurations."""
        datasources = {
            "apiVersion": 1,
            "datasources": [
                {
                    "name": "Prometheus",
                    "type": "prometheus",
                    "access": "proxy",
                    "url": "http://prometheus:9090",
                    "isDefault": True,
                    "jsonData": {
                        "httpMethod": "POST",
                        "customQueryParameters": f"constitutional_hash={self.constitutional_hash}",
                    },
                },
                {
                    "name": "Jaeger",
                    "type": "jaeger",
                    "access": "proxy",
                    "url": "http://jaeger:16686",
                    "jsonData": {
                        "tracesToLogs": {
                            "datasourceUid": "loki",
                            "tags": ["constitutional_hash"],
                        }
                    },
                },
                {
                    "name": "Loki",
                    "type": "loki",
                    "access": "proxy",
                    "url": "http://loki:3100",
                    "jsonData": {
                        "derivedFields": [
                            {
                                "matcherRegex": "trace_id=(\\w+)",
                                "name": "TraceID",
                                "url": "http://jaeger:16686/trace/${__value.raw}",
                                "datasourceUid": "jaeger",
                            }
                        ]
                    },
                },
            ],
        }

        datasources_path = Path(
            "infrastructure/observability/grafana/datasources/datasources.yml"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
        )
        datasources_path.parent.mkdir(parents=True, exist_ok=True)

        with open(datasources_path, "w") as f:
            import yaml

            yaml.dump(datasources, f, default_flow_style=False)

        logger.info("Generated Grafana datasources configuration")

    async def deploy_component(self, component: str) -> bool:
        """Deploy a specific observability component."""
        logger.info(f"Deploying {component}...")

        try:
            # Use docker-compose to deploy the component
            cmd = [
                "docker-compose",
                "-f",
                "infrastructure/observability/docker-compose.observability.yml",
                "up",
                "-d",
                component,
            ]

            result = subprocess.run(
                cmd, check=False, capture_output=True, text=True, timeout=300
            )

            if result.returncode == 0:
                logger.info(f"✅ {component} deployed successfully")
                return True
            logger.error(f"❌ Failed to deploy {component}: {result.stderr}")
            return False

        except subprocess.TimeoutExpired:
            logger.error(f"❌ Deployment of {component} timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Error deploying {component}: {e}")
            return False

    async def post_deployment_configuration(self):
        """Perform post-deployment configuration."""
        logger.info("Performing post-deployment configuration...")

        try:
            # Wait for services to be ready
            await asyncio.sleep(30)

            # Configure Grafana dashboards
            await self.configure_grafana_dashboards()

            # Configure Prometheus rules
            await self.configure_prometheus_rules()

            # Validate constitutional compliance monitoring
            await self.validate_constitutional_monitoring()

            logger.info("✅ Post-deployment configuration completed")

        except Exception as e:
            logger.error(f"Post-deployment configuration failed: {e}")

    async def configure_grafana_dashboards(self):
        """Configure Grafana dashboards."""
        # This would typically import pre-built dashboards
        # For now, we'll create a simple dashboard configuration

        dashboard_config = {
            "apiVersion": 1,
            "providers": [
                {
                    "name": "ACGS Dashboards",
                    "orgId": 1,
                    "folder": "ACGS",
                    "type": "file",
                    "disableDeletion": False,
                    "updateIntervalSeconds": 10,
                    "allowUiUpdates": True,
                    "options": {"path": "/etc/grafana/provisioning/dashboards"},
                }
            ],
        }

        config_path = Path(
            "infrastructure/observability/grafana/dashboards/dashboard-config.yml"
        )
        with open(config_path, "w") as f:
            import yaml

            yaml.dump(dashboard_config, f, default_flow_style=False)

        logger.info("Configured Grafana dashboards")

    async def verify_deployment(self, components: list) -> bool:
        """Verify that all components are running correctly."""
        logger.info("Verifying deployment...")

        try:
            # Check component health
            for component in components:
                if not await self.check_component_health(component):
                    logger.error(f"Health check failed for {component}")
                    return False

            # Check constitutional compliance monitoring
            if not await self.verify_constitutional_monitoring():
                logger.error("Constitutional compliance monitoring verification failed")
                return False

            logger.info("✅ All components are healthy")
            return True

        except Exception as e:
            logger.error(f"Deployment verification failed: {e}")
            return False

    async def check_component_health(self, component: str) -> bool:
        """Check health of a specific component."""
        try:
            # Get container status
            cmd = [
                "docker",
                "ps",
                "--filter",
                f"name=acgs-{component}",
                "--format",
                "{{.Status}}",
            ]
            result = subprocess.run(cmd, check=False, capture_output=True, text=True)

            if result.returncode == 0 and "Up" in result.stdout:
                logger.debug(f"✅ {component} is running")
                return True
            logger.warning(f"❌ {component} is not running properly")
            return False

        except Exception as e:
            logger.error(f"Error checking health of {component}: {e}")
            return False

    async def verify_constitutional_monitoring(self) -> bool:
        """Verify constitutional compliance monitoring is working."""
        try:
            # Check if constitutional monitor is responding
            import aiohttp

            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(
                        "http://localhost:8111/health", timeout=10
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            if (
                                data.get("constitutional_hash")
                                == self.constitutional_hash
                            ):
                                logger.info("✅ Constitutional monitoring is active")
                                return True
                except:
                    pass

            logger.warning("❌ Constitutional monitoring verification failed")
            return False

        except Exception as e:
            logger.error(f"Error verifying constitutional monitoring: {e}")
            return False

    async def print_deployment_summary(self):
        """Print deployment summary."""
        print(f"\n{'=' * 60}")
        print("ACGS OBSERVABILITY STACK DEPLOYMENT SUMMARY")
        print(f"{'=' * 60}")
        print(f"Constitutional Hash: {self.constitutional_hash}")
        print(f"Deployment Time: {datetime.now(timezone.utc).isoformat()}")
        print("\nACCESS URLS:")
        print("  Grafana Dashboard:     http://localhost:3000")
        print("  Prometheus:            http://localhost:9090")
        print("  Jaeger UI:             http://localhost:16686")
        print("  AlertManager:          http://localhost:9093")
        print("  Constitutional Monitor: http://localhost:8111")
        print("  Observability Dashboard: http://localhost:8112")
        print("\nCREDENTIALS:")
        print("  Grafana: admin / acgs_observability_admin")
        print("\nCOMPONENTS DEPLOYED:")
        for component in self.stack_components:
            print(f"  ✅ {component}")
        print(f"{'=' * 60}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Deploy ACGS Observability Stack")
    parser.add_argument(
        "--components", nargs="+", help="Specific components to deploy (default: all)"
    )
    parser.add_argument(
        "--constitutional-hash",
        default=CONSTITUTIONAL_HASH,
        help="Constitutional hash for validation",
    )
    parser.add_argument(
        "--verify-only", action="store_true", help="Only verify existing deployment"
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    async def deploy():
        try:
            deployer = ObservabilityStackDeployer(args.constitutional_hash)

            if args.verify_only:
                components = args.components or deployer.stack_components
                success = await deployer.verify_deployment(components)
            else:
                success = await deployer.deploy_observability_stack(args.components)

            if success:
                print("\n🎉 Observability stack deployment successful!")
                exit(0)
            else:
                print("\n💥 Observability stack deployment failed!")
                exit(1)

        except Exception as e:
            logger.error(f"Deployment script failed: {e}")
            exit(1)

    asyncio.run(deploy())


if __name__ == "__main__":
    main()
