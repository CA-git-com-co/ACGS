"""
ACGS-1 Read Replica Configuration and Routing
Phase 2 - Enterprise Scalability & Performance

Implements read replica routing, load balancing, and failover mechanisms
for improved read performance and scalability.
"""

import asyncio
import logging
import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple
import asyncpg

logger = logging.getLogger(__name__)


class ReplicaType(Enum):
    """Database replica types."""
    PRIMARY = "primary"
    READ_REPLICA = "read_replica"
    STANDBY = "standby"


class LoadBalancingStrategy(Enum):
    """Load balancing strategies for read replicas."""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    RANDOM = "random"
    WEIGHTED = "weighted"
    GEOGRAPHIC = "geographic"


@dataclass
class DatabaseNode:
    """Database node configuration."""
    host: str
    port: int
    database: str
    username: str
    password: str
    replica_type: ReplicaType
    weight: float = 1.0
    max_connections: int = 100
    
    # Health status
    is_healthy: bool = True
    last_health_check: Optional[float] = None
    current_connections: int = 0
    avg_response_time: float = 0.0
    
    # Geographic information
    region: str = "default"
    availability_zone: str = "default"
    
    def get_connection_url(self) -> str:
        """Get connection URL for this node."""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    def get_pgbouncer_url(self, pgbouncer_port: int = 6432) -> str:
        """Get PgBouncer connection URL for this node."""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{pgbouncer_port}/{self.database}"


@dataclass
class ReadReplicaConfig:
    """Configuration for read replica setup."""
    primary_node: DatabaseNode
    read_replicas: List[DatabaseNode] = field(default_factory=list)
    
    # Load balancing configuration
    load_balancing_strategy: LoadBalancingStrategy = LoadBalancingStrategy.ROUND_ROBIN
    
    # Health check configuration
    health_check_interval: int = 30
    health_check_timeout: float = 5.0
    max_health_check_failures: int = 3
    
    # Failover configuration
    auto_failover_enabled: bool = True
    failover_timeout: float = 10.0
    
    # Connection routing rules
    read_preference: str = "replica_preferred"  # replica_preferred, replica_only, primary_only
    write_preference: str = "primary_only"
    
    # Performance thresholds
    max_replica_lag: float = 5.0  # seconds
    max_response_time: float = 1.0  # seconds


class ReadReplicaRouter:
    """Routes database connections to appropriate nodes based on operation type."""
    
    def __init__(self, config: ReadReplicaConfig):
        self.config = config
        self.current_replica_index = 0
        self.connection_counts: Dict[str, int] = {}
        self.health_status: Dict[str, bool] = {}
        self.last_health_checks: Dict[str, float] = {}
        
        # Initialize health status
        self._initialize_health_status()
        
        logger.info(f"Read replica router initialized with {len(config.read_replicas)} replicas")
    
    def _initialize_health_status(self):
        """Initialize health status for all nodes."""
        # Primary node
        primary_key = f"{self.config.primary_node.host}:{self.config.primary_node.port}"
        self.health_status[primary_key] = True
        self.connection_counts[primary_key] = 0
        
        # Read replicas
        for replica in self.config.read_replicas:
            replica_key = f"{replica.host}:{replica.port}"
            self.health_status[replica_key] = True
            self.connection_counts[replica_key] = 0
    
    async def get_read_connection(self) -> DatabaseNode:
        """Get database node for read operations."""
        if self.config.read_preference == "primary_only":
            return self.config.primary_node
        
        # Get healthy read replicas
        healthy_replicas = await self._get_healthy_replicas()
        
        if not healthy_replicas:
            if self.config.read_preference == "replica_preferred":
                logger.warning("No healthy replicas available, falling back to primary")
                return self.config.primary_node
            else:
                raise Exception("No healthy read replicas available")
        
        # Select replica based on load balancing strategy
        return await self._select_replica(healthy_replicas)
    
    async def get_write_connection(self) -> DatabaseNode:
        """Get database node for write operations."""
        if self.config.write_preference == "primary_only":
            # Check if primary is healthy
            primary_key = f"{self.config.primary_node.host}:{self.config.primary_node.port}"
            if not self.health_status.get(primary_key, False):
                await self._check_node_health(self.config.primary_node)
            
            if self.health_status.get(primary_key, False):
                return self.config.primary_node
            else:
                raise Exception("Primary database node is not healthy")
        
        # For other write preferences, implement additional logic here
        return self.config.primary_node
    
    async def _get_healthy_replicas(self) -> List[DatabaseNode]:
        """Get list of healthy read replicas."""
        healthy_replicas = []
        
        for replica in self.config.read_replicas:
            replica_key = f"{replica.host}:{replica.port}"
            
            # Check if health check is needed
            last_check = self.last_health_checks.get(replica_key, 0)
            if time.time() - last_check > self.config.health_check_interval:
                await self._check_node_health(replica)
            
            # Add to healthy list if healthy
            if self.health_status.get(replica_key, False):
                healthy_replicas.append(replica)
        
        return healthy_replicas
    
    async def _select_replica(self, healthy_replicas: List[DatabaseNode]) -> DatabaseNode:
        """Select replica based on load balancing strategy."""
        if not healthy_replicas:
            raise Exception("No healthy replicas available")
        
        if self.config.load_balancing_strategy == LoadBalancingStrategy.ROUND_ROBIN:
            replica = healthy_replicas[self.current_replica_index % len(healthy_replicas)]
            self.current_replica_index += 1
            return replica
        
        elif self.config.load_balancing_strategy == LoadBalancingStrategy.RANDOM:
            return random.choice(healthy_replicas)
        
        elif self.config.load_balancing_strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            # Select replica with least connections
            min_connections = float('inf')
            selected_replica = healthy_replicas[0]
            
            for replica in healthy_replicas:
                replica_key = f"{replica.host}:{replica.port}"
                connections = self.connection_counts.get(replica_key, 0)
                
                if connections < min_connections:
                    min_connections = connections
                    selected_replica = replica
            
            return selected_replica
        
        elif self.config.load_balancing_strategy == LoadBalancingStrategy.WEIGHTED:
            # Weighted random selection
            total_weight = sum(replica.weight for replica in healthy_replicas)
            random_weight = random.uniform(0, total_weight)
            
            current_weight = 0
            for replica in healthy_replicas:
                current_weight += replica.weight
                if random_weight <= current_weight:
                    return replica
            
            return healthy_replicas[-1]  # Fallback
        
        else:
            # Default to round robin
            return healthy_replicas[self.current_replica_index % len(healthy_replicas)]
    
    async def _check_node_health(self, node: DatabaseNode) -> bool:
        """Check health of a database node."""
        node_key = f"{node.host}:{node.port}"
        
        try:
            start_time = time.time()
            
            # Try to connect and execute a simple query
            conn = await asyncpg.connect(
                host=node.host,
                port=node.port,
                database=node.database,
                user=node.username,
                password=node.password,
                timeout=self.config.health_check_timeout
            )
            
            # Execute health check query
            result = await conn.fetchval("SELECT 1")
            await conn.close()
            
            # Calculate response time
            response_time = time.time() - start_time
            node.avg_response_time = response_time
            
            # Update health status
            is_healthy = (result == 1 and response_time < self.config.max_response_time)
            self.health_status[node_key] = is_healthy
            self.last_health_checks[node_key] = time.time()
            node.last_health_check = time.time()
            node.is_healthy = is_healthy
            
            if is_healthy:
                logger.debug(f"Health check passed for {node_key} ({response_time:.3f}s)")
            else:
                logger.warning(f"Health check failed for {node_key} (slow response: {response_time:.3f}s)")
            
            return is_healthy
            
        except Exception as e:
            logger.error(f"Health check failed for {node_key}: {e}")
            self.health_status[node_key] = False
            self.last_health_checks[node_key] = time.time()
            node.is_healthy = False
            return False
    
    def increment_connection_count(self, node: DatabaseNode):
        """Increment connection count for a node."""
        node_key = f"{node.host}:{node.port}"
        self.connection_counts[node_key] = self.connection_counts.get(node_key, 0) + 1
        node.current_connections += 1
    
    def decrement_connection_count(self, node: DatabaseNode):
        """Decrement connection count for a node."""
        node_key = f"{node.host}:{node.port}"
        self.connection_counts[node_key] = max(0, self.connection_counts.get(node_key, 0) - 1)
        node.current_connections = max(0, node.current_connections - 1)
    
    async def get_cluster_status(self) -> Dict[str, any]:
        """Get comprehensive cluster status."""
        # Check health of all nodes
        await self._check_node_health(self.config.primary_node)
        
        for replica in self.config.read_replicas:
            await self._check_node_health(replica)
        
        # Compile status
        primary_key = f"{self.config.primary_node.host}:{self.config.primary_node.port}"
        
        status = {
            "primary": {
                "host": self.config.primary_node.host,
                "port": self.config.primary_node.port,
                "healthy": self.health_status.get(primary_key, False),
                "connections": self.connection_counts.get(primary_key, 0),
                "response_time": self.config.primary_node.avg_response_time,
                "last_check": self.last_health_checks.get(primary_key),
            },
            "replicas": [],
            "total_healthy_replicas": 0,
            "load_balancing_strategy": self.config.load_balancing_strategy.value,
        }
        
        healthy_replica_count = 0
        for replica in self.config.read_replicas:
            replica_key = f"{replica.host}:{replica.port}"
            is_healthy = self.health_status.get(replica_key, False)
            
            if is_healthy:
                healthy_replica_count += 1
            
            status["replicas"].append({
                "host": replica.host,
                "port": replica.port,
                "healthy": is_healthy,
                "connections": self.connection_counts.get(replica_key, 0),
                "response_time": replica.avg_response_time,
                "weight": replica.weight,
                "region": replica.region,
                "last_check": self.last_health_checks.get(replica_key),
            })
        
        status["total_healthy_replicas"] = healthy_replica_count
        
        return status


# Default configuration for ACGS-1
def get_default_read_replica_config() -> ReadReplicaConfig:
    """Get default read replica configuration for ACGS-1."""
    
    # Primary database node
    primary = DatabaseNode(
        host="localhost",
        port=5432,
        database="acgs_db",
        username="acgs_user",
        password="acgs_password",
        replica_type=ReplicaType.PRIMARY,
        weight=1.0,
        max_connections=100,
        region="primary",
    )
    
    # Read replica nodes (for future implementation)
    read_replicas = [
        # DatabaseNode(
        #     host="localhost",
        #     port=5433,
        #     database="acgs_db",
        #     username="acgs_user",
        #     password="acgs_password",
        #     replica_type=ReplicaType.READ_REPLICA,
        #     weight=1.0,
        #     max_connections=80,
        #     region="replica-1",
        # ),
        # DatabaseNode(
        #     host="localhost",
        #     port=5434,
        #     database="acgs_db",
        #     username="acgs_user",
        #     password="acgs_password",
        #     replica_type=ReplicaType.READ_REPLICA,
        #     weight=0.8,
        #     max_connections=80,
        #     region="replica-2",
        # ),
    ]
    
    return ReadReplicaConfig(
        primary_node=primary,
        read_replicas=read_replicas,
        load_balancing_strategy=LoadBalancingStrategy.LEAST_CONNECTIONS,
        health_check_interval=30,
        auto_failover_enabled=True,
        read_preference="replica_preferred",
    )
