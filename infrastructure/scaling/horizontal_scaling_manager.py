#!/usr/bin/env python3
"""
ACGS Horizontal Scaling Manager
Comprehensive horizontal scaling capabilities with auto-scaling, load balancing, and constitutional compliance.
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Any

import aiohttp
import docker
import psutil
from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, start_http_server

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constitutional hash for compliance validation
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

class ScalingDirection(Enum):
    """Scaling direction."""
    UP = "up"
    DOWN = "down"
    STABLE = "stable"

class ScalingTrigger(Enum):
    """Scaling trigger types."""
    CPU_UTILIZATION = "cpu_utilization"
    MEMORY_UTILIZATION = "memory_utilization"
    REQUEST_RATE = "request_rate"
    RESPONSE_TIME = "response_time"
    QUEUE_LENGTH = "queue_length"
    CONSTITUTIONAL_LOAD = "constitutional_load"

@dataclass
class ScalingPolicy:
    """Auto-scaling policy definition."""
    service_name: str
    min_instances: int
    max_instances: int
    target_cpu_utilization: float = 70.0
    target_memory_utilization: float = 80.0
    target_response_time_ms: float = 500.0
    scale_up_threshold: float = 80.0
    scale_down_threshold: float = 30.0
    scale_up_cooldown: int = 300  # seconds
    scale_down_cooldown: int = 600  # seconds
    
    # Constitutional compliance scaling
    constitutional_compliance_threshold: float = 95.0
    constitutional_scaling_enabled: bool = True
    
    # Advanced settings
    scale_up_step: int = 1
    scale_down_step: int = 1
    health_check_grace_period: int = 60
    
    # Constitutional compliance
    constitutional_hash: str = CONSTITUTIONAL_HASH

@dataclass
class ServiceInstance:
    """Service instance information."""
    instance_id: str
    service_name: str
    container_id: str
    port: int
    status: str  # starting, healthy, unhealthy, terminating
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    request_count: int = 0
    response_time: float = 0.0
    constitutional_compliance_score: float = 100.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_health_check: Optional[datetime] = None

@dataclass
class LoadBalancerConfig:
    """Load balancer configuration."""
    service_name: str
    algorithm: str = "round_robin"  # round_robin, least_connections, weighted
    health_check_path: str = "/health"
    health_check_interval: int = 30
    health_check_timeout: int = 5
    sticky_sessions: bool = False
    constitutional_routing: bool = True  # Route based on constitutional compliance

class HorizontalScalingManager:
    """Comprehensive horizontal scaling manager for ACGS."""
    
    def __init__(self):
        self.docker_client = docker.from_env()
        
        # Metrics
        self.registry = CollectorRegistry()
        self.setup_metrics()
        
        # ACGS services configuration
        self.services = {
            "auth-service": {"port": 8000, "critical": True, "base_image": "acgs/auth-service"},
            "ac-service": {"port": 8001, "critical": True, "base_image": "acgs/ac-service"},
            "integrity-service": {"port": 8002, "critical": False, "base_image": "acgs/integrity-service"},
            "fv-service": {"port": 8003, "critical": False, "base_image": "acgs/fv-service"},
            "gs-service": {"port": 8004, "critical": False, "base_image": "acgs/gs-service"},
            "pgc-service": {"port": 8005, "critical": True, "base_image": "acgs/pgc-service"},
            "ec-service": {"port": 8006, "critical": True, "base_image": "acgs/ec-service"}
        }
        
        # Scaling policies
        self.scaling_policies: Dict[str, ScalingPolicy] = {}
        self.service_instances: Dict[str, List[ServiceInstance]] = {}
        self.load_balancer_configs: Dict[str, LoadBalancerConfig] = {}
        
        # Scaling state
        self.last_scaling_action: Dict[str, datetime] = {}
        self.scaling_history: List[Dict] = []
        
        # Initialize default policies
        self.initialize_default_scaling_policies()
        self.initialize_load_balancer_configs()
        
        logger.info("Horizontal Scaling Manager initialized")

    def setup_metrics(self):
        """Setup Prometheus metrics for horizontal scaling."""
        self.service_instances_count = Gauge(
            'acgs_service_instances_count',
            'Number of service instances',
            ['service', 'status'],
            registry=self.registry
        )
        
        self.scaling_actions_total = Counter(
            'acgs_scaling_actions_total',
            'Total scaling actions performed',
            ['service', 'direction', 'trigger'],
            registry=self.registry
        )
        
        self.load_balancer_requests = Counter(
            'acgs_load_balancer_requests_total',
            'Total requests through load balancer',
            ['service', 'instance', 'status'],
            registry=self.registry
        )
        
        self.constitutional_compliance_scaling = Gauge(
            'acgs_constitutional_compliance_scaling_score',
            'Constitutional compliance score affecting scaling decisions',
            ['service'],
            registry=self.registry
        )
        
        self.scaling_efficiency = Gauge(
            'acgs_scaling_efficiency',
            'Scaling efficiency metric',
            ['service'],
            registry=self.registry
        )

    def initialize_default_scaling_policies(self):
        """Initialize default scaling policies for services."""
        for service_name, config in self.services.items():
            if config["critical"]:
                # Critical services have more conservative scaling
                policy = ScalingPolicy(
                    service_name=service_name,
                    min_instances=2,
                    max_instances=10,
                    target_cpu_utilization=60.0,
                    target_memory_utilization=70.0,
                    scale_up_threshold=70.0,
                    scale_down_threshold=20.0,
                    constitutional_compliance_threshold=98.0
                )
            else:
                # Non-critical services can scale more aggressively
                policy = ScalingPolicy(
                    service_name=service_name,
                    min_instances=1,
                    max_instances=8,
                    target_cpu_utilization=70.0,
                    target_memory_utilization=80.0,
                    scale_up_threshold=80.0,
                    scale_down_threshold=30.0,
                    constitutional_compliance_threshold=95.0
                )
            
            self.scaling_policies[service_name] = policy
            self.service_instances[service_name] = []

    def initialize_load_balancer_configs(self):
        """Initialize load balancer configurations."""
        for service_name in self.services.keys():
            config = LoadBalancerConfig(
                service_name=service_name,
                algorithm="round_robin",
                health_check_path="/health",
                constitutional_routing=service_name in ["ac-service", "pgc-service", "ec-service"]
            )
            self.load_balancer_configs[service_name] = config

    async def start_scaling_manager(self):
        """Start the horizontal scaling manager."""
        logger.info("Starting Horizontal Scaling Manager...")
        
        # Start metrics server
        start_http_server(8107, registry=self.registry)
        logger.info("Scaling manager metrics server started on port 8107")
        
        # Start scaling tasks
        asyncio.create_task(self.scaling_monitoring_loop())
        asyncio.create_task(self.health_check_loop())
        asyncio.create_task(self.load_balancing_loop())
        asyncio.create_task(self.constitutional_compliance_scaling_loop())
        
        logger.info("Horizontal Scaling Manager started")

    async def scale_service(self, service_name: str, direction: ScalingDirection, trigger: ScalingTrigger) -> bool:
        """Scale a service up or down."""
        logger.info(f"Scaling {service_name} {direction.value} (trigger: {trigger.value})")
        
        try:
            policy = self.scaling_policies.get(service_name)
            if not policy:
                logger.error(f"No scaling policy found for {service_name}")
                return False
            
            current_instances = len(self.service_instances[service_name])
            
            # Check cooldown period
            if not self.check_scaling_cooldown(service_name, direction):
                logger.info(f"Scaling cooldown active for {service_name}")
                return False
            
            # Determine target instance count
            if direction == ScalingDirection.UP:
                target_instances = min(current_instances + policy.scale_up_step, policy.max_instances)
            elif direction == ScalingDirection.DOWN:
                target_instances = max(current_instances - policy.scale_down_step, policy.min_instances)
            else:
                return True  # No scaling needed
            
            if target_instances == current_instances:
                logger.info(f"No scaling needed for {service_name} (already at limit)")
                return True
            
            # Perform scaling
            if direction == ScalingDirection.UP:
                success = await self.scale_up_service(service_name, target_instances - current_instances)
            else:
                success = await self.scale_down_service(service_name, current_instances - target_instances)
            
            if success:
                # Record scaling action
                self.record_scaling_action(service_name, direction, trigger, current_instances, target_instances)
                
                # Update metrics
                self.scaling_actions_total.labels(
                    service=service_name,
                    direction=direction.value,
                    trigger=trigger.value
                ).inc()
                
                # Update last scaling time
                self.last_scaling_action[service_name] = datetime.now(timezone.utc)
            
            return success
            
        except Exception as e:
            logger.error(f"Error scaling {service_name}: {e}")
            return False

    async def scale_up_service(self, service_name: str, instances_to_add: int) -> bool:
        """Scale up a service by adding instances."""
        logger.info(f"Adding {instances_to_add} instances to {service_name}")
        
        try:
            service_config = self.services.get(service_name)
            if not service_config:
                return False
            
            base_port = service_config["port"]
            base_image = service_config["base_image"]
            
            for i in range(instances_to_add):
                # Find available port
                new_port = await self.find_available_port(base_port)
                
                # Create new container
                container = self.docker_client.containers.run(
                    base_image,
                    detach=True,
                    ports={f"{base_port}/tcp": new_port},
                    environment={
                        "CONSTITUTIONAL_HASH": CONSTITUTIONAL_HASH,
                        "SERVICE_PORT": str(new_port),
                        "SCALING_INSTANCE": "true"
                    },
                    name=f"{service_name}-{int(time.time())}-{i}",
                    labels={
                        "acgs.service": service_name,
                        "acgs.scaling": "auto",
                        "acgs.constitutional_hash": CONSTITUTIONAL_HASH
                    }
                )
                
                # Create service instance
                instance = ServiceInstance(
                    instance_id=f"{service_name}-{container.id[:12]}",
                    service_name=service_name,
                    container_id=container.id,
                    port=new_port,
                    status="starting"
                )
                
                self.service_instances[service_name].append(instance)
                
                # Wait for instance to be healthy
                await self.wait_for_instance_health(instance)
                
                logger.info(f"Added instance {instance.instance_id} for {service_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error scaling up {service_name}: {e}")
            return False

    async def scale_down_service(self, service_name: str, instances_to_remove: int) -> bool:
        """Scale down a service by removing instances."""
        logger.info(f"Removing {instances_to_remove} instances from {service_name}")
        
        try:
            instances = self.service_instances[service_name]
            
            if len(instances) <= instances_to_remove:
                logger.warning(f"Cannot remove {instances_to_remove} instances from {service_name} (only {len(instances)} available)")
                return False
            
            # Select instances to remove (prefer unhealthy instances)
            instances_to_remove_list = self.select_instances_for_removal(instances, instances_to_remove)
            
            for instance in instances_to_remove_list:
                try:
                    # Graceful shutdown
                    await self.graceful_shutdown_instance(instance)
                    
                    # Remove from tracking
                    self.service_instances[service_name].remove(instance)
                    
                    logger.info(f"Removed instance {instance.instance_id} from {service_name}")
                    
                except Exception as e:
                    logger.error(f"Error removing instance {instance.instance_id}: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error scaling down {service_name}: {e}")
            return False

    def select_instances_for_removal(self, instances: List[ServiceInstance], count: int) -> List[ServiceInstance]:
        """Select instances for removal based on health and performance."""
        # Sort by health status and performance metrics
        sorted_instances = sorted(instances, key=lambda x: (
            x.status != "healthy",  # Unhealthy instances first
            -x.constitutional_compliance_score,  # Lower compliance score first
            -x.cpu_usage,  # Higher CPU usage first
            x.created_at  # Newer instances first
        ))
        
        return sorted_instances[:count]

    async def graceful_shutdown_instance(self, instance: ServiceInstance):
        """Gracefully shutdown a service instance."""
        try:
            instance.status = "terminating"
            
            # Get container
            container = self.docker_client.containers.get(instance.container_id)
            
            # Send graceful shutdown signal
            container.kill(signal="SIGTERM")
            
            # Wait for graceful shutdown
            await asyncio.sleep(10)
            
            # Force kill if still running
            try:
                container.reload()
                if container.status == "running":
                    container.kill(signal="SIGKILL")
            except:
                pass
            
            # Remove container
            container.remove(force=True)
            
        except Exception as e:
            logger.error(f"Error during graceful shutdown of {instance.instance_id}: {e}")

    async def find_available_port(self, base_port: int) -> int:
        """Find an available port starting from base_port."""
        port = base_port + 1000  # Start from base + 1000 for scaling instances
        
        while port < base_port + 2000:  # Limit search range
            try:
                # Check if port is in use
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                
                if result != 0:  # Port is available
                    return port
                
                port += 1
                
            except Exception:
                port += 1
        
        raise RuntimeError(f"No available ports found near {base_port}")

    async def wait_for_instance_health(self, instance: ServiceInstance, timeout: int = 60):
        """Wait for instance to become healthy."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Check health endpoint
                async with aiohttp.ClientSession() as session:
                    health_url = f"http://localhost:{instance.port}/health"
                    async with session.get(health_url, timeout=5) as response:
                        if response.status == 200:
                            instance.status = "healthy"
                            instance.last_health_check = datetime.now(timezone.utc)
                            logger.info(f"Instance {instance.instance_id} is healthy")
                            return
                
            except Exception:
                pass
            
            await asyncio.sleep(2)
        
        # Timeout reached
        instance.status = "unhealthy"
        logger.warning(f"Instance {instance.instance_id} failed to become healthy within {timeout}s")

    def check_scaling_cooldown(self, service_name: str, direction: ScalingDirection) -> bool:
        """Check if scaling cooldown period has passed."""
        if service_name not in self.last_scaling_action:
            return True
        
        policy = self.scaling_policies[service_name]
        last_action = self.last_scaling_action[service_name]
        current_time = datetime.now(timezone.utc)
        
        if direction == ScalingDirection.UP:
            cooldown = policy.scale_up_cooldown
        else:
            cooldown = policy.scale_down_cooldown
        
        time_since_last = (current_time - last_action).total_seconds()
        return time_since_last >= cooldown

    def record_scaling_action(self, service_name: str, direction: ScalingDirection, trigger: ScalingTrigger, 
                            from_instances: int, to_instances: int):
        """Record scaling action for history and analysis."""
        action = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service_name": service_name,
            "direction": direction.value,
            "trigger": trigger.value,
            "from_instances": from_instances,
            "to_instances": to_instances,
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
        
        self.scaling_history.append(action)
        
        # Keep only last 1000 actions
        if len(self.scaling_history) > 1000:
            self.scaling_history = self.scaling_history[-1000:]

    async def scaling_monitoring_loop(self):
        """Monitor services and trigger scaling decisions."""
        while True:
            try:
                for service_name in self.services.keys():
                    await self.evaluate_scaling_decision(service_name)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in scaling monitoring loop: {e}")
                await asyncio.sleep(60)

    async def evaluate_scaling_decision(self, service_name: str):
        """Evaluate whether a service needs scaling."""
        try:
            policy = self.scaling_policies[service_name]
            instances = self.service_instances[service_name]
            
            if not instances:
                # No instances, scale up to minimum
                await self.scale_service(service_name, ScalingDirection.UP, ScalingTrigger.CPU_UTILIZATION)
                return
            
            # Calculate average metrics
            healthy_instances = [i for i in instances if i.status == "healthy"]
            
            if not healthy_instances:
                return
            
            avg_cpu = sum(i.cpu_usage for i in healthy_instances) / len(healthy_instances)
            avg_memory = sum(i.memory_usage for i in healthy_instances) / len(healthy_instances)
            avg_response_time = sum(i.response_time for i in healthy_instances) / len(healthy_instances)
            avg_constitutional_compliance = sum(i.constitutional_compliance_score for i in healthy_instances) / len(healthy_instances)
            
            # Update metrics
            self.service_instances_count.labels(
                service=service_name,
                status="healthy"
            ).set(len(healthy_instances))
            
            self.constitutional_compliance_scaling.labels(
                service=service_name
            ).set(avg_constitutional_compliance)
            
            # Scaling decisions
            scale_up_needed = (
                avg_cpu > policy.scale_up_threshold or
                avg_memory > policy.scale_up_threshold or
                avg_response_time > policy.target_response_time_ms
            )
            
            scale_down_needed = (
                avg_cpu < policy.scale_down_threshold and
                avg_memory < policy.scale_down_threshold and
                avg_response_time < policy.target_response_time_ms * 0.5 and
                len(healthy_instances) > policy.min_instances
            )
            
            # Constitutional compliance scaling
            if policy.constitutional_scaling_enabled and avg_constitutional_compliance < policy.constitutional_compliance_threshold:
                scale_up_needed = True
            
            # Execute scaling
            if scale_up_needed and len(instances) < policy.max_instances:
                trigger = ScalingTrigger.CPU_UTILIZATION if avg_cpu > policy.scale_up_threshold else ScalingTrigger.CONSTITUTIONAL_LOAD
                await self.scale_service(service_name, ScalingDirection.UP, trigger)
            elif scale_down_needed:
                await self.scale_service(service_name, ScalingDirection.DOWN, ScalingTrigger.CPU_UTILIZATION)
            
        except Exception as e:
            logger.error(f"Error evaluating scaling for {service_name}: {e}")

    def get_scaling_status(self) -> Dict[str, Any]:
        """Get horizontal scaling status."""
        status = {
            "services": {},
            "total_instances": 0,
            "scaling_actions_last_hour": 0,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Service status
        for service_name, instances in self.service_instances.items():
            healthy_instances = len([i for i in instances if i.status == "healthy"])
            
            status["services"][service_name] = {
                "total_instances": len(instances),
                "healthy_instances": healthy_instances,
                "scaling_policy": {
                    "min_instances": self.scaling_policies[service_name].min_instances,
                    "max_instances": self.scaling_policies[service_name].max_instances
                }
            }
            
            status["total_instances"] += len(instances)
        
        # Recent scaling actions
        one_hour_ago = datetime.now(timezone.utc).timestamp() - 3600
        recent_actions = [
            action for action in self.scaling_history
            if datetime.fromisoformat(action["timestamp"].replace('Z', '+00:00')).timestamp() > one_hour_ago
        ]
        status["scaling_actions_last_hour"] = len(recent_actions)
        
        return status

# Global horizontal scaling manager instance
scaling_manager = HorizontalScalingManager()

if __name__ == "__main__":
    async def main():
        await scaling_manager.start_scaling_manager()
        
        try:
            # Keep running
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down horizontal scaling manager...")
    
    asyncio.run(main())
