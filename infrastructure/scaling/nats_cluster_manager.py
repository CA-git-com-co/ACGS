#!/usr/bin/env python3
"""
ACGS NATS Cluster Manager
Advanced NATS clustering with constitutional compliance, auto-scaling, and high availability.
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Any

import nats
from nats.errors import TimeoutError, NoServersError
from prometheus_client import (
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    start_http_server,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constitutional hash for compliance validation
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class NodeStatus(Enum):
    """NATS node status."""

    ACTIVE = "active"
    STANDBY = "standby"
    OFFLINE = "offline"
    JOINING = "joining"
    LEAVING = "leaving"


class ClusterMode(Enum):
    """NATS cluster mode."""

    STANDALONE = "standalone"
    CLUSTER = "cluster"
    SUPERCLUSTER = "supercluster"


@dataclass
class NATSNode:
    """NATS cluster node configuration."""

    node_id: str
    host: str
    port: int
    cluster_port: int
    monitor_port: int

    # Node properties
    status: NodeStatus = NodeStatus.OFFLINE
    is_leader: bool = False
    weight: float = 1.0

    # Cluster configuration
    cluster_routes: List[str] = field(default_factory=list)
    cluster_name: str = "acgs-cluster"

    # Constitutional compliance
    constitutional_compliance_enabled: bool = True
    constitutional_hash: str = CONSTITUTIONAL_HASH

    # Metrics
    connection_count: int = 0
    message_count: int = 0
    bytes_sent: int = 0
    bytes_received: int = 0
    last_health_check: Optional[datetime] = None


@dataclass
class StreamConfig:
    """NATS JetStream configuration."""

    stream_name: str
    subjects: List[str]
    retention_policy: str = "limits"  # limits, interest, workqueue
    max_msgs: int = 1000000
    max_bytes: int = 1024 * 1024 * 1024  # 1GB
    max_age: int = 86400 * 7  # 7 days

    # Replication
    replicas: int = 3

    # Constitutional compliance
    constitutional_validation_required: bool = False
    constitutional_hash: str = CONSTITUTIONAL_HASH


class NATSClusterManager:
    """Advanced NATS cluster manager for ACGS."""

    def __init__(self):
        # Metrics
        self.registry = CollectorRegistry()
        self.setup_metrics()

        # Cluster configuration
        self.cluster_nodes: Dict[str, NATSNode] = {}
        self.stream_configs: Dict[str, StreamConfig] = {}
        self.nats_connections: Dict[str, nats.NATS] = {}

        # Cluster state
        self.cluster_mode = ClusterMode.CLUSTER
        self.leader_node_id: Optional[str] = None
        self.cluster_health_score: float = 100.0

        # Auto-scaling configuration
        self.min_nodes = 3
        self.max_nodes = 9
        self.scale_up_threshold = 80.0  # CPU/Memory percentage
        self.scale_down_threshold = 30.0

        # Initialize default cluster
        self.initialize_default_cluster()
        self.initialize_stream_configs()

        logger.info("NATS Cluster Manager initialized")

    def setup_metrics(self):
        """Setup Prometheus metrics for NATS clustering."""
        self.cluster_nodes_count = Gauge(
            "acgs_nats_cluster_nodes_count",
            "Number of NATS cluster nodes",
            ["status"],
            registry=self.registry,
        )

        self.cluster_messages_total = Counter(
            "acgs_nats_cluster_messages_total",
            "Total messages processed by cluster",
            ["node_id", "subject"],
            registry=self.registry,
        )

        self.cluster_connections_count = Gauge(
            "acgs_nats_cluster_connections_count",
            "Active connections per node",
            ["node_id"],
            registry=self.registry,
        )

        self.cluster_health_score = Gauge(
            "acgs_nats_cluster_health_score",
            "Overall cluster health score",
            registry=self.registry,
        )

        self.constitutional_compliance_nats = Gauge(
            "acgs_nats_constitutional_compliance",
            "Constitutional compliance for NATS operations",
            ["node_id", "stream"],
            registry=self.registry,
        )

        self.stream_lag = Gauge(
            "acgs_nats_stream_lag",
            "Stream consumer lag",
            ["stream", "consumer"],
            registry=self.registry,
        )

    def initialize_default_cluster(self):
        """Initialize default NATS cluster configuration."""
        # Create 3-node cluster for high availability
        base_port = 4222
        base_cluster_port = 6222
        base_monitor_port = 8222

        for i in range(3):
            node_id = f"nats-node-{i+1}"

            # Calculate cluster routes (connect to other nodes)
            cluster_routes = []
            for j in range(3):
                if j != i:
                    cluster_routes.append(f"nats://localhost:{base_cluster_port + j}")

            node = NATSNode(
                node_id=node_id,
                host="localhost",
                port=base_port + i,
                cluster_port=base_cluster_port + i,
                monitor_port=base_monitor_port + i,
                cluster_routes=cluster_routes,
                weight=1.0 if i < 2 else 0.5,  # Third node has lower weight
            )

            self.cluster_nodes[node_id] = node

    def initialize_stream_configs(self):
        """Initialize JetStream configurations for ACGS."""
        # Constitutional compliance stream
        constitutional_stream = StreamConfig(
            stream_name="CONSTITUTIONAL_EVENTS",
            subjects=["constitutional.>", "compliance.>"],
            retention_policy="limits",
            max_msgs=100000,
            max_bytes=512 * 1024 * 1024,  # 512MB
            replicas=3,
            constitutional_validation_required=True,
        )
        self.stream_configs["constitutional"] = constitutional_stream

        # Service events stream
        service_stream = StreamConfig(
            stream_name="SERVICE_EVENTS",
            subjects=["service.>", "health.>", "metrics.>"],
            retention_policy="limits",
            max_msgs=1000000,
            replicas=2,
        )
        self.stream_configs["services"] = service_stream

        # Audit logs stream
        audit_stream = StreamConfig(
            stream_name="AUDIT_LOGS",
            subjects=["audit.>", "security.>"],
            retention_policy="limits",
            max_msgs=500000,
            max_age=86400 * 30,  # 30 days
            replicas=3,
        )
        self.stream_configs["audit"] = audit_stream

        # Evolution events stream
        evolution_stream = StreamConfig(
            stream_name="EVOLUTION_EVENTS",
            subjects=["evolution.>", "policy.generation.>"],
            retention_policy="workqueue",
            max_msgs=50000,
            replicas=3,
            constitutional_validation_required=True,
        )
        self.stream_configs["evolution"] = evolution_stream

    async def start_cluster_manager(self):
        """Start the NATS cluster manager."""
        logger.info("Starting NATS Cluster Manager...")

        # Start metrics server
        start_http_server(8109, registry=self.registry)
        logger.info("NATS cluster metrics server started on port 8109")

        # Start cluster nodes
        await self.start_cluster_nodes()

        # Initialize JetStream
        await self.initialize_jetstream()

        # Start monitoring tasks
        asyncio.create_task(self.cluster_health_monitoring_loop())
        asyncio.create_task(self.auto_scaling_loop())
        asyncio.create_task(self.leader_election_loop())
        asyncio.create_task(self.constitutional_compliance_loop())

        logger.info("NATS Cluster Manager started")

    async def start_cluster_nodes(self):
        """Start all cluster nodes."""
        for node_id, node in self.cluster_nodes.items():
            try:
                await self.start_node(node_id)
            except Exception as e:
                logger.error(f"Failed to start node {node_id}: {e}")

    async def start_node(self, node_id: str) -> bool:
        """Start a specific NATS node."""
        node = self.cluster_nodes.get(node_id)
        if not node:
            logger.error(f"Node {node_id} not found")
            return False

        try:
            logger.info(f"Starting NATS node {node_id}")

            # Generate NATS configuration
            config = self.generate_node_config(node)

            # In a real implementation, this would start the NATS server process
            # For now, we'll simulate by creating a connection
            nc = await nats.connect(
                servers=[f"nats://{node.host}:{node.port}"],
                name=f"acgs-{node_id}",
                max_reconnect_attempts=10,
                reconnect_time_wait=2,
            )

            self.nats_connections[node_id] = nc
            node.status = NodeStatus.ACTIVE
            node.last_health_check = datetime.now(timezone.utc)

            logger.info(f"NATS node {node_id} started successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to start NATS node {node_id}: {e}")
            node.status = NodeStatus.OFFLINE
            return False

    def generate_node_config(self, node: NATSNode) -> str:
        """Generate NATS server configuration for a node."""
        config = f"""
# ACGS NATS Node Configuration
# Constitutional Hash: {CONSTITUTIONAL_HASH}

server_name: {node.node_id}
host: {node.host}
port: {node.port}

# Cluster Configuration
cluster {{
    name: {node.cluster_name}
    host: {node.host}
    port: {node.cluster_port}
    
    routes: [
        {', '.join(f'"{route}"' for route in node.cluster_routes)}
    ]
    
    # Constitutional compliance
    authorization {{
        users: [
            {{
                user: "acgs_service"
                password: "constitutional_hash_{CONSTITUTIONAL_HASH}"
                permissions: {{
                    publish: ["constitutional.>", "service.>", "audit.>"]
                    subscribe: ["constitutional.>", "service.>", "audit.>"]
                }}
            }}
        ]
    }}
}}

# JetStream Configuration
jetstream {{
    store_dir: "/data/nats/{node.node_id}"
    max_memory_store: 1GB
    max_file_store: 10GB
}}

# Monitoring
monitor_port: {node.monitor_port}

# Logging
log_file: "/logs/nats/{node.node_id}.log"
log_size_limit: 100MB
max_traced_msg_len: 1024

# Constitutional compliance settings
accounts {{
    ACGS: {{
        users: [
            {{
                user: "constitutional_validator"
                password: "{CONSTITUTIONAL_HASH}"
                permissions: {{
                    publish: ["constitutional.>"]
                    subscribe: ["constitutional.>"]
                }}
            }}
        ]
        jetstream: enabled
    }}
}}
        """.strip()

        return config

    async def initialize_jetstream(self):
        """Initialize JetStream on all nodes."""
        logger.info("Initializing JetStream...")

        for stream_name, config in self.stream_configs.items():
            try:
                await self.create_stream(config)
            except Exception as e:
                logger.error(f"Failed to create stream {stream_name}: {e}")

    async def create_stream(self, config: StreamConfig) -> bool:
        """Create a JetStream stream."""
        try:
            # Use the first available connection
            nc = None
            for node_id, connection in self.nats_connections.items():
                if connection and not connection.is_closed:
                    nc = connection
                    break

            if not nc:
                logger.error("No available NATS connections for stream creation")
                return False

            # Create JetStream context
            js = nc.jetstream()

            # Stream configuration
            stream_config = {
                "name": config.stream_name,
                "subjects": config.subjects,
                "retention": config.retention_policy,
                "max_msgs": config.max_msgs,
                "max_bytes": config.max_bytes,
                "max_age": config.max_age * 1_000_000_000,  # Convert to nanoseconds
                "replicas": config.replicas,
            }

            # Create stream
            await js.add_stream(**stream_config)

            logger.info(f"Created JetStream stream: {config.stream_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to create stream {config.stream_name}: {e}")
            return False

    async def publish_constitutional_event(self, subject: str, data: dict) -> bool:
        """Publish constitutional compliance event."""
        try:
            # Validate constitutional hash
            if data.get("constitutional_hash") != CONSTITUTIONAL_HASH:
                logger.error("Invalid constitutional hash in event data")
                return False

            # Add metadata
            event_data = {
                **data,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "node_id": self.leader_node_id or "unknown",
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }

            # Publish to constitutional stream
            nc = await self.get_healthy_connection()
            if not nc:
                return False

            js = nc.jetstream()
            await js.publish(
                f"constitutional.{subject}", json.dumps(event_data).encode()
            )

            logger.debug(f"Published constitutional event: {subject}")
            return True

        except Exception as e:
            logger.error(f"Failed to publish constitutional event: {e}")
            return False

    async def get_healthy_connection(self) -> Optional[nats.NATS]:
        """Get a healthy NATS connection."""
        for node_id, connection in self.nats_connections.items():
            node = self.cluster_nodes.get(node_id)
            if (
                node
                and node.status == NodeStatus.ACTIVE
                and connection
                and not connection.is_closed
            ):
                return connection
        return None

    async def scale_cluster(self, target_nodes: int) -> bool:
        """Scale the NATS cluster to target number of nodes."""
        current_nodes = len(
            [n for n in self.cluster_nodes.values() if n.status == NodeStatus.ACTIVE]
        )

        if target_nodes == current_nodes:
            return True

        logger.info(
            f"Scaling NATS cluster from {current_nodes} to {target_nodes} nodes"
        )

        try:
            if target_nodes > current_nodes:
                # Scale up
                return await self.scale_up_cluster(target_nodes - current_nodes)
            else:
                # Scale down
                return await self.scale_down_cluster(current_nodes - target_nodes)

        except Exception as e:
            logger.error(f"Error scaling cluster: {e}")
            return False

    async def scale_up_cluster(self, nodes_to_add: int) -> bool:
        """Add nodes to the cluster."""
        logger.info(f"Adding {nodes_to_add} nodes to NATS cluster")

        try:
            base_port = 4222
            base_cluster_port = 6222
            base_monitor_port = 8222

            current_count = len(self.cluster_nodes)

            for i in range(nodes_to_add):
                node_index = current_count + i
                node_id = f"nats-node-{node_index + 1}"

                # Calculate cluster routes
                cluster_routes = []
                for existing_node in self.cluster_nodes.values():
                    if existing_node.status == NodeStatus.ACTIVE:
                        cluster_routes.append(
                            f"nats://{existing_node.host}:{existing_node.cluster_port}"
                        )

                # Create new node
                node = NATSNode(
                    node_id=node_id,
                    host="localhost",
                    port=base_port + node_index,
                    cluster_port=base_cluster_port + node_index,
                    monitor_port=base_monitor_port + node_index,
                    cluster_routes=cluster_routes,
                    weight=0.5,  # New nodes start with lower weight
                )

                self.cluster_nodes[node_id] = node

                # Start the node
                await self.start_node(node_id)

            return True

        except Exception as e:
            logger.error(f"Error scaling up cluster: {e}")
            return False

    async def scale_down_cluster(self, nodes_to_remove: int) -> bool:
        """Remove nodes from the cluster."""
        logger.info(f"Removing {nodes_to_remove} nodes from NATS cluster")

        try:
            # Select nodes to remove (prefer nodes with lower weight)
            active_nodes = [
                (node_id, node)
                for node_id, node in self.cluster_nodes.items()
                if node.status == NodeStatus.ACTIVE
            ]

            # Sort by weight (ascending) and connection count (ascending)
            active_nodes.sort(key=lambda x: (x[1].weight, x[1].connection_count))

            nodes_to_remove_list = active_nodes[:nodes_to_remove]

            for node_id, node in nodes_to_remove_list:
                await self.stop_node(node_id)
                del self.cluster_nodes[node_id]

            return True

        except Exception as e:
            logger.error(f"Error scaling down cluster: {e}")
            return False

    async def stop_node(self, node_id: str) -> bool:
        """Stop a NATS node gracefully."""
        try:
            node = self.cluster_nodes.get(node_id)
            if not node:
                return False

            logger.info(f"Stopping NATS node {node_id}")

            node.status = NodeStatus.LEAVING

            # Close connection
            connection = self.nats_connections.get(node_id)
            if connection and not connection.is_closed:
                await connection.close()

            # Remove from connections
            if node_id in self.nats_connections:
                del self.nats_connections[node_id]

            node.status = NodeStatus.OFFLINE

            logger.info(f"NATS node {node_id} stopped")
            return True

        except Exception as e:
            logger.error(f"Error stopping node {node_id}: {e}")
            return False

    async def cluster_health_monitoring_loop(self):
        """Monitor cluster health continuously."""
        while True:
            try:
                await self.check_cluster_health()
                await self.update_cluster_metrics()

                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                logger.error(f"Error in cluster health monitoring: {e}")
                await asyncio.sleep(60)

    async def check_cluster_health(self):
        """Check health of all cluster nodes."""
        healthy_nodes = 0
        total_nodes = len(self.cluster_nodes)

        for node_id, node in self.cluster_nodes.items():
            try:
                connection = self.nats_connections.get(node_id)

                if connection and not connection.is_closed:
                    # Simple health check
                    await connection.flush(timeout=5)
                    node.status = NodeStatus.ACTIVE
                    node.last_health_check = datetime.now(timezone.utc)
                    healthy_nodes += 1
                else:
                    node.status = NodeStatus.OFFLINE

            except Exception as e:
                logger.warning(f"Health check failed for node {node_id}: {e}")
                node.status = NodeStatus.OFFLINE

        # Calculate cluster health score
        if total_nodes > 0:
            self.cluster_health_score = (healthy_nodes / total_nodes) * 100
        else:
            self.cluster_health_score = 0

        # Update metrics
        self.cluster_health_score.set(self.cluster_health_score)

    async def update_cluster_metrics(self):
        """Update cluster metrics."""
        try:
            # Count nodes by status
            status_counts = {}
            for status in NodeStatus:
                status_counts[status.value] = 0

            for node in self.cluster_nodes.values():
                status_counts[node.status.value] += 1

            # Update metrics
            for status, count in status_counts.items():
                self.cluster_nodes_count.labels(status=status).set(count)

            # Update connection counts
            for node_id, node in self.cluster_nodes.items():
                self.cluster_connections_count.labels(node_id=node_id).set(
                    node.connection_count
                )

        except Exception as e:
            logger.error(f"Error updating cluster metrics: {e}")

    def get_cluster_status(self) -> Dict[str, Any]:
        """Get NATS cluster status."""
        return {
            "cluster_mode": self.cluster_mode.value,
            "total_nodes": len(self.cluster_nodes),
            "active_nodes": len(
                [
                    n
                    for n in self.cluster_nodes.values()
                    if n.status == NodeStatus.ACTIVE
                ]
            ),
            "leader_node": self.leader_node_id,
            "health_score": self.cluster_health_score,
            "streams": len(self.stream_configs),
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "nodes": {
                node_id: {
                    "status": node.status.value,
                    "is_leader": node.is_leader,
                    "connection_count": node.connection_count,
                    "last_health_check": (
                        node.last_health_check.isoformat()
                        if node.last_health_check
                        else None
                    ),
                }
                for node_id, node in self.cluster_nodes.items()
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# Global NATS cluster manager instance
nats_cluster_manager = NATSClusterManager()

if __name__ == "__main__":

    async def main():
        await nats_cluster_manager.start_cluster_manager()

        try:
            # Keep running
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down NATS cluster manager...")

    asyncio.run(main())
