"""
Kafka Configuration Manager

Centralized configuration management for Kafka clusters and streaming infrastructure,
implementing production-ready configuration patterns and environmental adaptability
as recommended by the ACGE technical validation report.

Key Features:
- Environment-specific configuration management
- Security configuration with encryption and authentication
- Performance tuning and optimization presets
- Configuration validation and testing
- Dynamic configuration updates and rollback
- Integration with service discovery and monitoring
"""

import asyncio
import json
import logging
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Union

import yaml

from services.shared.monitoring.intelligent_alerting_system import IntelligentAlertingSystem
from services.shared.security.enhanced_audit_logging import EnhancedAuditLogger

logger = logging.getLogger(__name__)


class EnvironmentType(Enum):
    """Deployment environment types"""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    DISASTER_RECOVERY = "disaster_recovery"


class SecurityProtocol(Enum):
    """Kafka security protocols"""

    PLAINTEXT = "PLAINTEXT"
    SSL = "SSL"
    SASL_PLAINTEXT = "SASL_PLAINTEXT"
    SASL_SSL = "SASL_SSL"


class SASLMechanism(Enum):
    """SASL authentication mechanisms"""

    PLAIN = "PLAIN"
    SCRAM_SHA_256 = "SCRAM-SHA-256"
    SCRAM_SHA_512 = "SCRAM-SHA-512"
    GSSAPI = "GSSAPI"
    OAUTHBEARER = "OAUTHBEARER"


@dataclass
class KafkaClusterConfig:
    """Kafka cluster configuration"""

    cluster_id: str
    bootstrap_servers: list[str]
    environment: EnvironmentType
    security_protocol: SecurityProtocol
    sasl_mechanism: Optional[SASLMechanism]
    ssl_config: Optional[dict[str, Any]]
    sasl_config: Optional[dict[str, Any]]
    performance_config: Optional[dict[str, Any]]
    monitoring_config: Optional[dict[str, Any]]
    replication_factor: int
    min_insync_replicas: int
    retention_hours: int
    segment_size_mb: int
    compression_type: str
    created_at: datetime
    updated_at: datetime


@dataclass
class ProducerConfig:
    """Kafka producer configuration"""

    acks: Union[str, int]
    retries: int
    batch_size: int
    linger_ms: int
    buffer_memory: int
    max_request_size: int
    compression_type: str
    max_in_flight_requests_per_connection: int
    request_timeout_ms: int
    delivery_timeout_ms: int
    enable_idempotence: bool
    transactional_id: Optional[str]


@dataclass
class ConsumerConfig:
    """Kafka consumer configuration"""

    group_id: str
    auto_offset_reset: str
    enable_auto_commit: bool
    auto_commit_interval_ms: int
    max_poll_records: int
    max_poll_interval_ms: int
    session_timeout_ms: int
    heartbeat_interval_ms: int
    fetch_min_bytes: int
    fetch_max_wait_ms: int
    max_partition_fetch_bytes: int
    isolation_level: str


@dataclass
class TopicConfig:
    """Kafka topic configuration"""

    name: str
    partitions: int
    replication_factor: int
    cleanup_policy: str
    retention_ms: int
    segment_ms: int
    max_message_bytes: int
    min_insync_replicas: int
    compression_type: str
    config_overrides: Optional[dict[str, str]]


class KafkaConfigManager:
    """
    Production-ready Kafka configuration manager
    """

    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = (
            Path(config_dir) if config_dir else Path(__file__).parent / "configs"
        )
        self.alerting = IntelligentAlertingSystem()
        self.audit_logger = EnhancedAuditLogger()

        # Configuration storage
        self.cluster_configs = {}
        self.producer_configs = {}
        self.consumer_configs = {}
        self.topic_configs = {}

        # Default configurations
        self.default_configs = self._load_default_configs()

        # Configuration validation cache
        self.validation_cache = {}
        self.cache_ttl_minutes = 30

    def _load_default_configs(self) -> dict[str, Any]:
        """Load default configuration templates"""
        return {
            "producer": {
                "development": ProducerConfig(
                    acks=1,
                    retries=3,
                    batch_size=16384,
                    linger_ms=5,
                    buffer_memory=33554432,  # 32MB
                    max_request_size=1048576,  # 1MB
                    compression_type="gzip",
                    max_in_flight_requests_per_connection=5,
                    request_timeout_ms=30000,
                    delivery_timeout_ms=120000,
                    enable_idempotence=False,
                    transactional_id=None,
                ),
                "production": ProducerConfig(
                    acks="all",
                    retries=10,
                    batch_size=32768,
                    linger_ms=10,
                    buffer_memory=67108864,  # 64MB
                    max_request_size=2097152,  # 2MB
                    compression_type="zstd",
                    max_in_flight_requests_per_connection=1,
                    request_timeout_ms=30000,
                    delivery_timeout_ms=300000,
                    enable_idempotence=True,
                    transactional_id="acgs-producer",
                ),
            },
            "consumer": {
                "development": ConsumerConfig(
                    group_id="acgs-dev-group",
                    auto_offset_reset="latest",
                    enable_auto_commit=True,
                    auto_commit_interval_ms=5000,
                    max_poll_records=500,
                    max_poll_interval_ms=300000,
                    session_timeout_ms=30000,
                    heartbeat_interval_ms=3000,
                    fetch_min_bytes=1,
                    fetch_max_wait_ms=500,
                    max_partition_fetch_bytes=1048576,
                    isolation_level="read_uncommitted",
                ),
                "production": ConsumerConfig(
                    group_id="acgs-prod-group",
                    auto_offset_reset="earliest",
                    enable_auto_commit=False,
                    auto_commit_interval_ms=5000,
                    max_poll_records=1000,
                    max_poll_interval_ms=300000,
                    session_timeout_ms=45000,
                    heartbeat_interval_ms=3000,
                    fetch_min_bytes=10240,
                    fetch_max_wait_ms=1000,
                    max_partition_fetch_bytes=2097152,
                    isolation_level="read_committed",
                ),
            },
            "cluster": {
                "security": {
                    "ssl": {
                        "ssl_check_hostname": True,
                        "ssl_ca_location": "/etc/kafka/ssl/ca-cert.pem",
                        "ssl_certificate_location": "/etc/kafka/ssl/client-cert.pem",
                        "ssl_key_location": "/etc/kafka/ssl/client-key.pem",
                        "ssl_key_password": None,
                    },
                    "sasl": {
                        "sasl_username": os.getenv("KAFKA_SASL_USERNAME"),
                        "sasl_password": os.getenv("KAFKA_SASL_PASSWORD"),
                    },
                },
                "performance": {
                    "development": {
                        "socket_keepalive_enable": True,
                        "socket_timeout_ms": 30000,
                        "socket_connection_setup_timeout_ms": 10000,
                        "connections_max_idle_ms": 540000,
                        "reconnect_backoff_ms": 50,
                        "reconnect_backoff_max_ms": 1000,
                    },
                    "production": {
                        "socket_keepalive_enable": True,
                        "socket_timeout_ms": 30000,
                        "socket_connection_setup_timeout_ms": 30000,
                        "connections_max_idle_ms": 600000,
                        "reconnect_backoff_ms": 100,
                        "reconnect_backoff_max_ms": 5000,
                    },
                },
            },
        }

    async def load_cluster_config(
        self, cluster_id: str, environment: EnvironmentType
    ) -> KafkaClusterConfig:
        """
        Load Kafka cluster configuration

        Args:
            cluster_id: Unique cluster identifier
            environment: Target environment

        Returns:
            Kafka cluster configuration
        """
        try:
            config_key = f"{cluster_id}_{environment.value}"

            # Check cache first
            if config_key in self.cluster_configs:
                cached_config = self.cluster_configs[config_key]
                # Check if cache is still valid (updated within last hour)
                if (
                    datetime.utcnow() - cached_config.updated_at
                ).total_seconds() < 3600:
                    return cached_config

            # Load configuration from file
            config_file = (
                self.config_dir / f"clusters/{cluster_id}_{environment.value}.yaml"
            )

            if config_file.exists():
                config_data = await self._load_config_file(config_file)
            else:
                # Generate default configuration
                config_data = await self._generate_default_cluster_config(
                    cluster_id, environment
                )
                await self._save_config_file(config_file, config_data)

            # Create cluster configuration
            cluster_config = KafkaClusterConfig(
                cluster_id=cluster_id,
                bootstrap_servers=config_data.get(
                    "bootstrap_servers",
                    self._get_default_bootstrap_servers(environment),
                ),
                environment=environment,
                security_protocol=SecurityProtocol(
                    config_data.get("security_protocol", "PLAINTEXT")
                ),
                sasl_mechanism=(
                    SASLMechanism(config_data["sasl_mechanism"])
                    if config_data.get("sasl_mechanism")
                    else None
                ),
                ssl_config=config_data.get("ssl_config"),
                sasl_config=config_data.get("sasl_config"),
                performance_config=config_data.get("performance_config"),
                monitoring_config=config_data.get("monitoring_config"),
                replication_factor=config_data.get(
                    "replication_factor",
                    3 if environment == EnvironmentType.PRODUCTION else 1,
                ),
                min_insync_replicas=config_data.get(
                    "min_insync_replicas",
                    2 if environment == EnvironmentType.PRODUCTION else 1,
                ),
                retention_hours=config_data.get("retention_hours", 168),  # 7 days
                segment_size_mb=config_data.get("segment_size_mb", 1024),  # 1GB
                compression_type=config_data.get("compression_type", "gzip"),
                created_at=datetime.fromisoformat(
                    config_data.get("created_at", datetime.utcnow().isoformat())
                ),
                updated_at=datetime.utcnow(),
            )

            # Validate configuration
            validation_result = await self._validate_cluster_config(cluster_config)
            if not validation_result["valid"]:
                raise ValueError(
                    f"Invalid cluster configuration: {validation_result['errors']}"
                )

            # Cache the configuration
            self.cluster_configs[config_key] = cluster_config

            # Log configuration loading
            await self.audit_logger.log_config_event({
                "event_type": "cluster_config_loaded",
                "cluster_id": cluster_id,
                "environment": environment.value,
                "config_file": str(config_file),
                "timestamp": datetime.utcnow().isoformat(),
            })

            return cluster_config

        except Exception as e:
            logger.error(
                f"Failed to load cluster config for {cluster_id} in {environment}: {e}"
            )
            raise

    async def get_producer_config(
        self, cluster_id: str, environment: EnvironmentType, **overrides
    ) -> dict[str, Any]:
        """
        Get optimized producer configuration

        Args:
            cluster_id: Kafka cluster identifier
            environment: Target environment
            **overrides: Configuration overrides

        Returns:
            Producer configuration dictionary
        """
        try:
            # Get base configuration
            env_key = (
                "production"
                if environment == EnvironmentType.PRODUCTION
                else "development"
            )
            base_config = asdict(self.default_configs["producer"][env_key])

            # Get cluster-specific configuration
            cluster_config = await self.load_cluster_config(cluster_id, environment)

            # Merge with cluster security settings
            if cluster_config.security_protocol != SecurityProtocol.PLAINTEXT:
                base_config.update({
                    "security_protocol": cluster_config.security_protocol.value,
                    "ssl_check_hostname": True,
                })

                if cluster_config.ssl_config:
                    base_config.update(cluster_config.ssl_config)

                if cluster_config.sasl_config:
                    base_config.update(cluster_config.sasl_config)
                    base_config["sasl_mechanism"] = cluster_config.sasl_mechanism.value

            # Apply performance optimizations
            if cluster_config.performance_config:
                base_config.update(cluster_config.performance_config)

            # Apply user overrides
            base_config.update(overrides)

            # Add cluster bootstrap servers
            base_config["bootstrap_servers"] = cluster_config.bootstrap_servers

            logger.info(
                f"Generated producer config for {cluster_id} in {environment.value}"
            )

            return base_config

        except Exception as e:
            logger.error(f"Failed to generate producer config: {e}")
            raise

    async def get_consumer_config(
        self, cluster_id: str, environment: EnvironmentType, group_id: str, **overrides
    ) -> dict[str, Any]:
        """
        Get optimized consumer configuration

        Args:
            cluster_id: Kafka cluster identifier
            environment: Target environment
            group_id: Consumer group ID
            **overrides: Configuration overrides

        Returns:
            Consumer configuration dictionary
        """
        try:
            # Get base configuration
            env_key = (
                "production"
                if environment == EnvironmentType.PRODUCTION
                else "development"
            )
            base_config = asdict(self.default_configs["consumer"][env_key])

            # Set group ID
            base_config["group_id"] = group_id

            # Get cluster-specific configuration
            cluster_config = await self.load_cluster_config(cluster_id, environment)

            # Merge with cluster security settings
            if cluster_config.security_protocol != SecurityProtocol.PLAINTEXT:
                base_config.update({
                    "security_protocol": cluster_config.security_protocol.value,
                    "ssl_check_hostname": True,
                })

                if cluster_config.ssl_config:
                    base_config.update(cluster_config.ssl_config)

                if cluster_config.sasl_config:
                    base_config.update(cluster_config.sasl_config)
                    base_config["sasl_mechanism"] = cluster_config.sasl_mechanism.value

            # Apply performance optimizations
            if cluster_config.performance_config:
                base_config.update(cluster_config.performance_config)

            # Apply user overrides
            base_config.update(overrides)

            # Add cluster bootstrap servers
            base_config["bootstrap_servers"] = cluster_config.bootstrap_servers

            logger.info(
                f"Generated consumer config for {cluster_id} in {environment.value}"
            )

            return base_config

        except Exception as e:
            logger.error(f"Failed to generate consumer config: {e}")
            raise

    async def create_topic_config(
        self,
        cluster_id: str,
        topic_name: str,
        environment: EnvironmentType,
        **config_overrides,
    ) -> TopicConfig:
        """
        Create topic configuration

        Args:
            cluster_id: Kafka cluster identifier
            topic_name: Topic name
            environment: Target environment
            **config_overrides: Topic configuration overrides

        Returns:
            Topic configuration
        """
        try:
            cluster_config = await self.load_cluster_config(cluster_id, environment)

            # Determine partitions based on environment and topic type
            if environment == EnvironmentType.PRODUCTION:
                default_partitions = 12 if "high-throughput" in topic_name else 6
            else:
                default_partitions = 3

            # Determine retention based on topic type
            if "audit" in topic_name or "compliance" in topic_name:
                default_retention_ms = 7 * 24 * 60 * 60 * 1000  # 7 days
            elif "metrics" in topic_name or "monitoring" in topic_name:
                default_retention_ms = 3 * 24 * 60 * 60 * 1000  # 3 days
            else:
                default_retention_ms = 24 * 60 * 60 * 1000  # 1 day

            topic_config = TopicConfig(
                name=topic_name,
                partitions=config_overrides.get("partitions", default_partitions),
                replication_factor=config_overrides.get(
                    "replication_factor", cluster_config.replication_factor
                ),
                cleanup_policy=config_overrides.get("cleanup_policy", "delete"),
                retention_ms=config_overrides.get("retention_ms", default_retention_ms),
                segment_ms=config_overrides.get("segment_ms", 86400000),  # 1 day
                max_message_bytes=config_overrides.get(
                    "max_message_bytes", 1048576
                ),  # 1MB
                min_insync_replicas=config_overrides.get(
                    "min_insync_replicas", cluster_config.min_insync_replicas
                ),
                compression_type=config_overrides.get(
                    "compression_type", cluster_config.compression_type
                ),
                config_overrides=config_overrides.get("config_overrides"),
            )

            # Validate topic configuration
            validation_result = await self._validate_topic_config(
                topic_config, cluster_config
            )
            if not validation_result["valid"]:
                raise ValueError(
                    f"Invalid topic configuration: {validation_result['errors']}"
                )

            # Store topic configuration
            config_key = f"{cluster_id}_{topic_name}"
            self.topic_configs[config_key] = topic_config

            # Log topic configuration creation
            await self.audit_logger.log_config_event({
                "event_type": "topic_config_created",
                "cluster_id": cluster_id,
                "topic_name": topic_name,
                "environment": environment.value,
                "partitions": topic_config.partitions,
                "replication_factor": topic_config.replication_factor,
                "timestamp": datetime.utcnow().isoformat(),
            })

            return topic_config

        except Exception as e:
            logger.error(f"Failed to create topic config for {topic_name}: {e}")
            raise

    async def _validate_cluster_config(
        self, config: KafkaClusterConfig
    ) -> dict[str, Any]:
        """Validate cluster configuration"""
        try:
            errors = []
            warnings = []

            # Validate bootstrap servers
            if not config.bootstrap_servers:
                errors.append("Bootstrap servers cannot be empty")

            # Validate replication factor
            if config.replication_factor < 1:
                errors.append("Replication factor must be at least 1")
            elif (
                config.environment == EnvironmentType.PRODUCTION
                and config.replication_factor < 3
            ):
                warnings.append(
                    "Production environments should have replication factor >= 3"
                )

            # Validate min.insync.replicas
            if config.min_insync_replicas > config.replication_factor:
                errors.append("min.insync.replicas cannot exceed replication factor")

            # Validate security configuration
            if config.security_protocol in [
                SecurityProtocol.SSL,
                SecurityProtocol.SASL_SSL,
            ]:
                if not config.ssl_config:
                    errors.append(
                        "SSL configuration required for SSL-enabled security protocol"
                    )

            if config.security_protocol in [
                SecurityProtocol.SASL_PLAINTEXT,
                SecurityProtocol.SASL_SSL,
            ]:
                if not config.sasl_mechanism:
                    errors.append(
                        "SASL mechanism required for SASL-enabled security protocol"
                    )
                if not config.sasl_config:
                    errors.append(
                        "SASL configuration required for SASL-enabled security protocol"
                    )

            return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}

        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Validation failed: {e!s}"],
                "warnings": [],
            }

    async def _validate_topic_config(
        self, topic_config: TopicConfig, cluster_config: KafkaClusterConfig
    ) -> dict[str, Any]:
        """Validate topic configuration"""
        try:
            errors = []
            warnings = []

            # Validate partitions
            if topic_config.partitions < 1:
                errors.append("Partitions must be at least 1")

            # Validate replication factor
            if topic_config.replication_factor > len(cluster_config.bootstrap_servers):
                errors.append("Replication factor cannot exceed number of brokers")

            # Validate min.insync.replicas
            if topic_config.min_insync_replicas > topic_config.replication_factor:
                errors.append("min.insync.replicas cannot exceed replication factor")

            # Validate retention
            if topic_config.retention_ms < 1000:  # Less than 1 second
                warnings.append("Very short retention period")

            # Validate message size
            if topic_config.max_message_bytes > 10 * 1024 * 1024:  # 10MB
                warnings.append("Large message size may impact performance")

            return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}

        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Validation failed: {e!s}"],
                "warnings": [],
            }

    def _get_default_bootstrap_servers(self, environment: EnvironmentType) -> list[str]:
        """Get default bootstrap servers for environment"""
        server_map = {
            EnvironmentType.DEVELOPMENT: ["localhost:9092"],
            EnvironmentType.TESTING: ["kafka-test-1:9092", "kafka-test-2:9092"],
            EnvironmentType.STAGING: [
                "kafka-staging-1:9092",
                "kafka-staging-2:9092",
                "kafka-staging-3:9092",
            ],
            EnvironmentType.PRODUCTION: [
                "kafka-prod-1:9092",
                "kafka-prod-2:9092",
                "kafka-prod-3:9092",
            ],
            EnvironmentType.DISASTER_RECOVERY: [
                "kafka-dr-1:9092",
                "kafka-dr-2:9092",
                "kafka-dr-3:9092",
            ],
        }
        return server_map.get(environment, ["localhost:9092"])

    async def _generate_default_cluster_config(
        self, cluster_id: str, environment: EnvironmentType
    ) -> dict[str, Any]:
        """Generate default cluster configuration"""
        return {
            "bootstrap_servers": self._get_default_bootstrap_servers(environment),
            "security_protocol": (
                "SASL_SSL" if environment == EnvironmentType.PRODUCTION else "PLAINTEXT"
            ),
            "sasl_mechanism": (
                "SCRAM-SHA-256" if environment == EnvironmentType.PRODUCTION else None
            ),
            "ssl_config": (
                self.default_configs["cluster"]["security"]["ssl"]
                if environment == EnvironmentType.PRODUCTION
                else None
            ),
            "sasl_config": (
                self.default_configs["cluster"]["security"]["sasl"]
                if environment == EnvironmentType.PRODUCTION
                else None
            ),
            "performance_config": self.default_configs["cluster"]["performance"][
                (
                    "production"
                    if environment == EnvironmentType.PRODUCTION
                    else "development"
                )
            ],
            "monitoring_config": {
                "jmx_port": 9999,
                "metrics_reporters": ["prometheus"],
            },
            "replication_factor": 3 if environment == EnvironmentType.PRODUCTION else 1,
            "min_insync_replicas": (
                2 if environment == EnvironmentType.PRODUCTION else 1
            ),
            "retention_hours": 168,  # 7 days
            "segment_size_mb": 1024,  # 1GB
            "compression_type": (
                "zstd" if environment == EnvironmentType.PRODUCTION else "gzip"
            ),
            "created_at": datetime.utcnow().isoformat(),
        }

    async def _load_config_file(self, config_file: Path) -> dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(config_file) as f:
                if config_file.suffix == ".yaml" or config_file.suffix == ".yml":
                    return yaml.safe_load(f)
                else:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config file {config_file}: {e}")
            raise

    async def _save_config_file(self, config_file: Path, config_data: dict[str, Any]):
        """Save configuration to YAML file"""
        try:
            # Ensure directory exists
            config_file.parent.mkdir(parents=True, exist_ok=True)

            with open(config_file, "w") as f:
                if config_file.suffix == ".yaml" or config_file.suffix == ".yml":
                    yaml.dump(config_data, f, default_flow_style=False)
                else:
                    json.dump(config_data, f, indent=2, default=str)

        except Exception as e:
            logger.error(f"Failed to save config file {config_file}: {e}")
            raise

    async def test_connection(
        self, cluster_id: str, environment: EnvironmentType
    ) -> bool:
        """
        Test connection to Kafka cluster

        Args:
            cluster_id: Kafka cluster identifier
            environment: Target environment

        Returns:
            Connection test result
        """
        try:
            cluster_config = await self.load_cluster_config(cluster_id, environment)

            # Simple connection test (would use actual Kafka client in production)
            # For now, just validate that bootstrap servers are reachable
            for server in cluster_config.bootstrap_servers:
                host, port = server.split(":")
                try:
                    # Test TCP connection
                    _, writer = await asyncio.wait_for(
                        asyncio.open_connection(host, int(port)), timeout=5.0
                    )
                    writer.close()
                    await writer.wait_closed()
                except Exception as e:
                    logger.warning(f"Failed to connect to {server}: {e}")
                    return False

            logger.info(f"Successfully connected to Kafka cluster {cluster_id}")
            return True

        except Exception as e:
            logger.error(f"Kafka connection test failed: {e}")
            return False

    def get_config_summary(self) -> dict[str, Any]:
        """Get configuration manager summary"""
        return {
            "cluster_configs": len(self.cluster_configs),
            "producer_configs": len(self.producer_configs),
            "consumer_configs": len(self.consumer_configs),
            "topic_configs": len(self.topic_configs),
            "validation_cache_size": len(self.validation_cache),
            "config_directory": str(self.config_dir),
            "supported_environments": [env.value for env in EnvironmentType],
            "supported_security_protocols": [proto.value for proto in SecurityProtocol],
            "supported_sasl_mechanisms": [mech.value for mech in SASLMechanism],
        }


# Example usage
async def example_usage():
    """Example of how to use the Kafka configuration manager"""
    # Initialize configuration manager
    config_manager = KafkaConfigManager()

    # Load cluster configuration
    cluster_config = await config_manager.load_cluster_config(
        "acgs-main", EnvironmentType.PRODUCTION
    )

    # Get producer configuration
    producer_config = await config_manager.get_producer_config(
        "acgs-main",
        EnvironmentType.PRODUCTION,
        batch_size=32768,  # Override default
        compression_type="zstd",
    )

    # Get consumer configuration
    consumer_config = await config_manager.get_consumer_config(
        "acgs-main", EnvironmentType.PRODUCTION, "governance-group"
    )

    # Create topic configuration
    topic_config = await config_manager.create_topic_config(
        "acgs-main",
        "constitutional-decisions",
        EnvironmentType.PRODUCTION,
        partitions=12,
        retention_ms=7 * 24 * 60 * 60 * 1000,  # 7 days
    )

    # Test connection
    connection_ok = await config_manager.test_connection(
        "acgs-main", EnvironmentType.PRODUCTION
    )

    print(f"Cluster config: {cluster_config}")
    print(f"Connection test: {connection_ok}")
    print(f"Topic config: {topic_config}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(example_usage())
