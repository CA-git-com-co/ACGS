"""
ACGS Distributed Load Testing Configuration

Configuration for distributed load testing across multiple nodes
with constitutional compliance monitoring.

Constitutional Hash: cdd01ef066bc6cf2
"""

import logging
import os
from dataclasses import dataclass
from typing import Any, Optional

# Constitutional compliance hash
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


@dataclass
class LoadTestNode:
    """Configuration for a load test node."""

    host: str
    port: int
    workers: int
    max_users: int
    node_id: str
    region: Optional[str] = None


class DistributedLoadTestConfig:
    """Configuration for distributed load testing."""

    # Test execution configuration
    MASTER_HOST = os.getenv("LOCUST_MASTER_HOST", "localhost")
    MASTER_PORT = int(os.getenv("LOCUST_MASTER_PORT", "5557"))
    WEB_PORT = int(os.getenv("LOCUST_WEB_PORT", "8089"))

    # Target configuration
    TARGET_HOST = os.getenv("ACGS_TARGET_HOST", "http://localhost:8080")
    TARGET_RPS = int(os.getenv("ACGS_TARGET_RPS", "1000"))
    TEST_DURATION = os.getenv("ACGS_TEST_DURATION", "30m")

    # Distributed nodes configuration
    LOAD_TEST_NODES = [
        LoadTestNode(
            host="load-node-1",
            port=5557,
            workers=4,
            max_users=250,
            node_id="node-1",
            region="us-east-1",
        ),
        LoadTestNode(
            host="load-node-2",
            port=5557,
            workers=4,
            max_users=250,
            node_id="node-2",
            region="us-west-2",
        ),
        LoadTestNode(
            host="load-node-3",
            port=5557,
            workers=4,
            max_users=250,
            node_id="node-3",
            region="eu-west-1",
        ),
        LoadTestNode(
            host="load-node-4",
            port=5557,
            workers=4,
            max_users=250,
            node_id="node-4",
            region="ap-southeast-1",
        ),
    ]

    # Constitutional compliance monitoring
    CONSTITUTIONAL_COMPLIANCE_MONITORING = True
    COMPLIANCE_THRESHOLD = 0.95
    COMPLIANCE_CHECK_INTERVAL = 30  # seconds

    # Performance thresholds
    RESPONSE_TIME_THRESHOLD_MS = 2000
    ERROR_RATE_THRESHOLD = 0.01  # 1%
    CPU_THRESHOLD = 80  # %
    MEMORY_THRESHOLD = 85  # %

    # Monitoring configuration
    PROMETHEUS_ENDPOINT = os.getenv("PROMETHEUS_ENDPOINT", "http://prometheus:9090")
    GRAFANA_ENDPOINT = os.getenv("GRAFANA_ENDPOINT", "http://grafana:3000")

    # Test scenarios distribution
    SCENARIO_DISTRIBUTION = {
        "constitutional_verification": 0.25,
        "multi_tenant_operations": 0.30,
        "policy_governance": 0.20,
        "formal_verification": 0.15,
        "integrity_operations": 0.10,
    }

    # Load patterns
    LOAD_PATTERNS = {
        "steady_state": {"duration": "10m", "users": 800, "spawn_rate": 10},
        "peak_load": {"duration": "5m", "users": 1500, "spawn_rate": 25},
        "stress_test": {"duration": "3m", "users": 2000, "spawn_rate": 50},
    }

    # Docker configuration for distributed testing
    DOCKER_CONFIG = {
        "master_image": "acgs/load-test-master:latest",
        "worker_image": "acgs/load-test-worker:latest",
        "network": "acgs-load-test-network",
        "volume_mounts": [
            "/var/log/acgs-load-test:/app/logs",
            "/var/lib/acgs-load-test:/app/data",
        ],
    }

    @classmethod
    def get_total_max_users(cls) -> int:
        """Get total maximum users across all nodes."""
        return sum(node.max_users for node in cls.LOAD_TEST_NODES)

    @classmethod
    def get_total_workers(cls) -> int:
        """Get total workers across all nodes."""
        return sum(node.workers for node in cls.LOAD_TEST_NODES)

    @classmethod
    def get_node_by_id(cls, node_id: str) -> Optional[LoadTestNode]:
        """Get node configuration by ID."""
        return next(
            (node for node in cls.LOAD_TEST_NODES if node.node_id == node_id), None
        )

    @classmethod
    def get_master_command(cls) -> list[str]:
        """Get command to run Locust master."""
        return [
            "locust",
            "-f",
            "/app/locustfile.py",
            "--master",
            "--host",
            cls.TARGET_HOST,
            "--web-port",
            str(cls.WEB_PORT),
            "--master-bind-port",
            str(cls.MASTER_PORT),
            "--html",
            "/app/reports/acgs_distributed_load_test.html",
            "--csv",
            "/app/reports/acgs_distributed_load_test",
        ]

    @classmethod
    def get_worker_command(cls, node_id: str) -> list[str]:
        """Get command to run Locust worker."""
        node = cls.get_node_by_id(node_id)
        if not node:
            raise ValueError(f"Node {node_id} not found")

        return [
            "locust",
            "-f",
            "/app/locustfile.py",
            "--worker",
            "--master-host",
            cls.MASTER_HOST,
            "--master-port",
            str(cls.MASTER_PORT),
            "--processes",
            str(node.workers),
        ]

    @classmethod
    def get_docker_compose_config(cls) -> dict[str, Any]:
        """Get Docker Compose configuration for distributed testing."""

        services = {
            "locust-master": {
                "image": cls.DOCKER_CONFIG["master_image"],
                "ports": [f"{cls.WEB_PORT}:8089", f"{cls.MASTER_PORT}:5557"],
                "environment": {
                    "LOCUST_MODE": "master",
                    "ACGS_TARGET_HOST": cls.TARGET_HOST,
                    "CONSTITUTIONAL_HASH": CONSTITUTIONAL_HASH,
                },
                "volumes": cls.DOCKER_CONFIG["volume_mounts"],
                "networks": [cls.DOCKER_CONFIG["network"]],
                "depends_on": ["prometheus", "grafana"],
            }
        }

        # Add worker services
        for node in cls.LOAD_TEST_NODES:
            services[f"locust-worker-{node.node_id}"] = {
                "image": cls.DOCKER_CONFIG["worker_image"],
                "environment": {
                    "LOCUST_MODE": "worker",
                    "LOCUST_MASTER_HOST": "locust-master",
                    "LOCUST_MASTER_PORT": str(cls.MASTER_PORT),
                    "LOCUST_PROCESSES": str(node.workers),
                    "CONSTITUTIONAL_HASH": CONSTITUTIONAL_HASH,
                    "NODE_ID": node.node_id,
                    "NODE_REGION": node.region,
                },
                "volumes": cls.DOCKER_CONFIG["volume_mounts"],
                "networks": [cls.DOCKER_CONFIG["network"]],
                "depends_on": ["locust-master"],
            }

        # Add monitoring services
        services.update(
            {
                "prometheus": {
                    "image": "prom/prometheus:latest",
                    "ports": ["9090:9090"],
                    "volumes": [
                        "./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml",
                        "prometheus_data:/prometheus",
                    ],
                    "networks": [cls.DOCKER_CONFIG["network"]],
                },
                "grafana": {
                    "image": "grafana/grafana:latest",
                    "ports": ["3000:3000"],
                    "environment": {"GF_SECURITY_ADMIN_PASSWORD": "admin"},
                    "volumes": [
                        "./monitoring/grafana/dashboards:/var/lib/grafana/dashboards",
                        "./monitoring/grafana/provisioning:/etc/grafana/provisioning",
                        "grafana_data:/var/lib/grafana",
                    ],
                    "networks": [cls.DOCKER_CONFIG["network"]],
                },
            }
        )

        return {
            "version": "3.8",
            "services": services,
            "networks": {cls.DOCKER_CONFIG["network"]: {"driver": "bridge"}},
            "volumes": {"prometheus_data": {}, "grafana_data": {}},
        }

    @classmethod
    def validate_configuration(cls) -> dict[str, Any]:
        """Validate distributed load test configuration."""

        validation_results = {"valid": True, "errors": [], "warnings": []}

        # Validate total capacity
        total_users = cls.get_total_max_users()
        if total_users < cls.TARGET_RPS:
            validation_results["warnings"].append(
                f"Total max users ({total_users}) may be insufficient for target RPS"
                f" ({cls.TARGET_RPS})"
            )

        # Validate node configuration
        for node in cls.LOAD_TEST_NODES:
            if node.workers <= 0:
                validation_results["errors"].append(
                    f"Node {node.node_id} has invalid worker count: {node.workers}"
                )
                validation_results["valid"] = False

            if node.max_users <= 0:
                validation_results["errors"].append(
                    f"Node {node.node_id} has invalid max users: {node.max_users}"
                )
                validation_results["valid"] = False

        # Validate target configuration
        if not cls.TARGET_HOST.startswith(("http://", "https://")):
            validation_results["errors"].append("Invalid target host format")
            validation_results["valid"] = False

        # Validate scenario distribution
        total_distribution = sum(cls.SCENARIO_DISTRIBUTION.values())
        if abs(total_distribution - 1.0) > 0.01:
            validation_results["warnings"].append(
                f"Scenario distribution total is {total_distribution}, should be 1.0"
            )

        return validation_results

    @classmethod
    def log_configuration(cls):
        """Log distributed load test configuration."""

        logger.info("=== ACGS Distributed Load Test Configuration ===")
        logger.info(f"Target: {cls.TARGET_HOST}")
        logger.info(f"Target RPS: {cls.TARGET_RPS}")
        logger.info(f"Test Duration: {cls.TEST_DURATION}")
        logger.info(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")

        logger.info(f"Total Nodes: {len(cls.LOAD_TEST_NODES)}")
        logger.info(f"Total Workers: {cls.get_total_workers()}")
        logger.info(f"Total Max Users: {cls.get_total_max_users()}")

        # Log node details
        for node in cls.LOAD_TEST_NODES:
            logger.info(
                f"  Node {node.node_id}: {node.workers} workers, {node.max_users} max"
                f" users ({node.region})"
            )

        # Log scenario distribution
        logger.info("Scenario Distribution:")
        for scenario, percentage in cls.SCENARIO_DISTRIBUTION.items():
            logger.info(f"  {scenario}: {percentage * 100:.1f}%")

        # Validate configuration
        validation = cls.validate_configuration()
        if validation["errors"]:
            logger.error(f"Configuration errors: {validation['errors']}")
        if validation["warnings"]:
            logger.warning(f"Configuration warnings: {validation['warnings']}")


# Initialize and log configuration
if __name__ == "__main__":
    DistributedLoadTestConfig.log_configuration()
