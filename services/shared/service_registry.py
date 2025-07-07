"""
ACGS Service Registry Pattern Implementation
Constitutional Hash: cdd01ef066bc6cf2

Provides centralized service discovery and coordination for all ACGS services.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, asdict
from enum import Enum
import redis.asyncio as redis
from contextlib import asynccontextmanager

# Configure logging
logger = logging.getLogger(__name__)

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

class ServiceStatus(Enum):
    """Service status enumeration."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    STARTING = "starting"
    STOPPING = "stopping"
    MAINTENANCE = "maintenance"

@dataclass
class ServiceInstance:
    """Represents a service instance in the registry."""
    service_name: str
    instance_id: str
    host: str
    port: int
    status: ServiceStatus
    version: str
    constitutional_hash: str
    metadata: Dict[str, Any]
    last_heartbeat: datetime
    registration_time: datetime
    health_check_url: str
    capabilities: List[str]

    def is_expired(self, ttl_seconds: int = 30) -> bool:
        """Check if service instance has expired based on last heartbeat."""
        return (datetime.utcnow() - self.last_heartbeat).total_seconds() > ttl_seconds

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['last_heartbeat'] = self.last_heartbeat.isoformat()
        data['registration_time'] = self.registration_time.isoformat()
        data['status'] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ServiceInstance':
        """Create instance from dictionary."""
        data['last_heartbeat'] = datetime.fromisoformat(data['last_heartbeat'])
        data['registration_time'] = datetime.fromisoformat(data['registration_time'])
        data['status'] = ServiceStatus(data['status'])
        return cls(**data)

class ACGSServiceRegistry:
    """
    Centralized service registry for ACGS microservices.
    
    Provides service discovery, health monitoring, and constitutional compliance validation.
    """

    def __init__(self, redis_url: str = "redis://localhost:6389", redis_db: int = 7):
        self.redis_url = redis_url
        self.redis_db = redis_db
        self.redis_client: Optional[redis.Redis] = None
        self.registry_key_prefix = "acgs:service_registry"
        self.heartbeat_key_prefix = "acgs:heartbeat"
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.ttl_seconds = 30  # Service instance TTL
        self.cleanup_interval = 10  # Cleanup expired services every 10 seconds
        self._cleanup_task: Optional[asyncio.Task] = None

    async def initialize(self) -> None:
        """Initialize the service registry."""
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                db=self.redis_db,
                decode_responses=True,
                health_check_interval=30
            )
            await self.redis_client.ping()
            logger.info(f"Service registry initialized (Constitutional Hash: {self.constitutional_hash})")
            
            # Start cleanup task
            self._cleanup_task = asyncio.create_task(self._cleanup_expired_services())
            
        except Exception as e:
            logger.error(f"Failed to initialize service registry: {e}")
            raise

    async def close(self) -> None:
        """Close the service registry and cleanup resources."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        if self.redis_client:
            await self.redis_client.close()
            logger.info("Service registry closed")

    @asynccontextmanager
    async def registry_context(self):
        """Context manager for service registry lifecycle."""
        try:
            await self.initialize()
            yield self
        finally:
            await self.close()

    async def register_service(
        self,
        service_name: str,
        instance_id: str,
        host: str,
        port: int,
        version: str,
        capabilities: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Register a service instance.
        
        Args:
            service_name: Name of the service
            instance_id: Unique identifier for this instance
            host: Host address
            port: Port number
            version: Service version
            capabilities: List of service capabilities
            metadata: Additional metadata
            
        Returns:
            True if registration successful, False otherwise
        """
        try:
            # Validate constitutional compliance
            if not self._validate_constitutional_compliance():
                logger.error(f"Constitutional compliance validation failed for {service_name}")
                return False

            current_time = datetime.utcnow()
            health_check_url = f"http://{host}:{port}/health"
            
            service_instance = ServiceInstance(
                service_name=service_name,
                instance_id=instance_id,
                host=host,
                port=port,
                status=ServiceStatus.STARTING,
                version=version,
                constitutional_hash=self.constitutional_hash,
                metadata=metadata or {},
                last_heartbeat=current_time,
                registration_time=current_time,
                health_check_url=health_check_url,
                capabilities=capabilities
            )

            # Store in Redis
            key = f"{self.registry_key_prefix}:{service_name}:{instance_id}"
            await self.redis_client.setex(
                key,
                self.ttl_seconds * 2,  # Set TTL longer than heartbeat interval
                json.dumps(service_instance.to_dict())
            )

            # Add to service set
            await self.redis_client.sadd(
                f"{self.registry_key_prefix}:services",
                service_name
            )

            # Add to instance set for this service
            await self.redis_client.sadd(
                f"{self.registry_key_prefix}:{service_name}:instances",
                instance_id
            )

            logger.info(f"Registered service instance: {service_name}/{instance_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to register service {service_name}/{instance_id}: {e}")
            return False

    async def unregister_service(self, service_name: str, instance_id: str) -> bool:
        """
        Unregister a service instance.
        
        Args:
            service_name: Name of the service
            instance_id: Instance identifier
            
        Returns:
            True if unregistration successful, False otherwise
        """
        try:
            # Remove from Redis
            key = f"{self.registry_key_prefix}:{service_name}:{instance_id}"
            await self.redis_client.delete(key)

            # Remove from instance set
            await self.redis_client.srem(
                f"{self.registry_key_prefix}:{service_name}:instances",
                instance_id
            )

            # Check if this was the last instance, remove service from services set
            instances = await self.redis_client.smembers(
                f"{self.registry_key_prefix}:{service_name}:instances"
            )
            if not instances:
                await self.redis_client.srem(
                    f"{self.registry_key_prefix}:services",
                    service_name
                )

            logger.info(f"Unregistered service instance: {service_name}/{instance_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to unregister service {service_name}/{instance_id}: {e}")
            return False

    async def heartbeat(
        self,
        service_name: str,
        instance_id: str,
        status: ServiceStatus = ServiceStatus.HEALTHY,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send heartbeat for a service instance.
        
        Args:
            service_name: Name of the service
            instance_id: Instance identifier
            status: Current service status
            metadata: Updated metadata
            
        Returns:
            True if heartbeat successful, False otherwise
        """
        try:
            key = f"{self.registry_key_prefix}:{service_name}:{instance_id}"
            service_data = await self.redis_client.get(key)
            
            if not service_data:
                logger.warning(f"Service not found for heartbeat: {service_name}/{instance_id}")
                return False

            # Update service instance
            service_dict = json.loads(service_data)
            service_instance = ServiceInstance.from_dict(service_dict)
            
            service_instance.last_heartbeat = datetime.utcnow()
            service_instance.status = status
            if metadata:
                service_instance.metadata.update(metadata)

            # Update in Redis
            await self.redis_client.setex(
                key,
                self.ttl_seconds * 2,
                json.dumps(service_instance.to_dict())
            )

            # Store heartbeat timestamp
            heartbeat_key = f"{self.heartbeat_key_prefix}:{service_name}:{instance_id}"
            await self.redis_client.setex(
                heartbeat_key,
                self.ttl_seconds,
                int(time.time())
            )

            return True

        except Exception as e:
            logger.error(f"Failed to send heartbeat for {service_name}/{instance_id}: {e}")
            return False

    async def discover_services(self, service_name: Optional[str] = None) -> List[ServiceInstance]:
        """
        Discover available service instances.
        
        Args:
            service_name: Optional service name filter
            
        Returns:
            List of available service instances
        """
        try:
            services = []
            
            if service_name:
                service_names = [service_name]
            else:
                service_names = await self.redis_client.smembers(
                    f"{self.registry_key_prefix}:services"
                )

            for svc_name in service_names:
                instances = await self.redis_client.smembers(
                    f"{self.registry_key_prefix}:{svc_name}:instances"
                )
                
                for instance_id in instances:
                    key = f"{self.registry_key_prefix}:{svc_name}:{instance_id}"
                    service_data = await self.redis_client.get(key)
                    
                    if service_data:
                        service_dict = json.loads(service_data)
                        service_instance = ServiceInstance.from_dict(service_dict)
                        
                        # Only return non-expired instances
                        if not service_instance.is_expired(self.ttl_seconds):
                            services.append(service_instance)

            return services

        except Exception as e:
            logger.error(f"Failed to discover services: {e}")
            return []

    async def get_healthy_instances(self, service_name: str) -> List[ServiceInstance]:
        """
        Get healthy instances of a specific service.
        
        Args:
            service_name: Name of the service
            
        Returns:
            List of healthy service instances
        """
        all_instances = await self.discover_services(service_name)
        return [
            instance for instance in all_instances
            if instance.status == ServiceStatus.HEALTHY
        ]

    async def get_service_capabilities(self, service_name: str) -> Set[str]:
        """
        Get aggregated capabilities for a service.
        
        Args:
            service_name: Name of the service
            
        Returns:
            Set of all capabilities provided by service instances
        """
        instances = await self.discover_services(service_name)
        capabilities = set()
        for instance in instances:
            capabilities.update(instance.capabilities)
        return capabilities

    async def get_registry_stats(self) -> Dict[str, Any]:
        """
        Get service registry statistics.
        
        Returns:
            Dictionary with registry statistics
        """
        try:
            services = await self.redis_client.smembers(
                f"{self.registry_key_prefix}:services"
            )
            
            stats = {
                "constitutional_hash": self.constitutional_hash,
                "total_services": len(services),
                "services": {},
                "registry_health": "healthy"
            }

            for service_name in services:
                instances = await self.discover_services(service_name)
                healthy_count = len([i for i in instances if i.status == ServiceStatus.HEALTHY])
                
                stats["services"][service_name] = {
                    "total_instances": len(instances),
                    "healthy_instances": healthy_count,
                    "capabilities": list(await self.get_service_capabilities(service_name))
                }

            return stats

        except Exception as e:
            logger.error(f"Failed to get registry stats: {e}")
            return {"error": str(e)}

    def _validate_constitutional_compliance(self) -> bool:
        """Validate constitutional compliance."""
        return self.constitutional_hash == CONSTITUTIONAL_HASH

    async def _cleanup_expired_services(self) -> None:
        """Background task to cleanup expired service instances."""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                
                services = await self.redis_client.smembers(
                    f"{self.registry_key_prefix}:services"
                )
                
                for service_name in services:
                    instances = await self.redis_client.smembers(
                        f"{self.registry_key_prefix}:{service_name}:instances"
                    )
                    
                    expired_instances = []
                    for instance_id in instances:
                        key = f"{self.registry_key_prefix}:{service_name}:{instance_id}"
                        service_data = await self.redis_client.get(key)
                        
                        if service_data:
                            service_dict = json.loads(service_data)
                            service_instance = ServiceInstance.from_dict(service_dict)
                            
                            if service_instance.is_expired(self.ttl_seconds):
                                expired_instances.append(instance_id)
                        else:
                            # Data missing, consider expired
                            expired_instances.append(instance_id)
                    
                    # Remove expired instances
                    for instance_id in expired_instances:
                        await self.unregister_service(service_name, instance_id)
                        logger.info(f"Cleaned up expired service: {service_name}/{instance_id}")

            except asyncio.CancelledError:
                logger.info("Service registry cleanup task cancelled")
                break
            except Exception as e:
                logger.error(f"Error in service registry cleanup: {e}")

# Global service registry instance
_service_registry: Optional[ACGSServiceRegistry] = None

async def get_service_registry() -> ACGSServiceRegistry:
    """Get the global service registry instance."""
    global _service_registry
    if _service_registry is None:
        _service_registry = ACGSServiceRegistry()
        await _service_registry.initialize()
    return _service_registry

async def register_current_service(
    service_name: str,
    instance_id: str,
    host: str,
    port: int,
    version: str,
    capabilities: List[str],
    metadata: Optional[Dict[str, Any]] = None
) -> bool:
    """Convenience function to register the current service."""
    registry = await get_service_registry()
    return await registry.register_service(
        service_name, instance_id, host, port, version, capabilities, metadata
    )

async def send_heartbeat(
    service_name: str,
    instance_id: str,
    status: ServiceStatus = ServiceStatus.HEALTHY,
    metadata: Optional[Dict[str, Any]] = None
) -> bool:
    """Convenience function to send heartbeat."""
    registry = await get_service_registry()
    return await registry.heartbeat(service_name, instance_id, status, metadata)