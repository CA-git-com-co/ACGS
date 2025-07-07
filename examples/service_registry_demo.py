#!/usr/bin/env python3
"""
ACGS Service Registry Pattern Demo
Constitutional Hash: cdd01ef066bc6cf2

Demonstrates the service registry pattern implementation with multiple services.
"""

import asyncio
import logging
import json
from datetime import datetime
from typing import List

from services.shared.service_registry import (
    ACGSServiceRegistry,
    ServiceStatus,
    register_current_service,
    send_heartbeat
)
from services.shared.middleware.service_discovery_middleware import (
    ServiceDiscoveryClient
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

class MockService:
    """Mock service for demonstration."""
    
    def __init__(self, name: str, instance_id: str, port: int, capabilities: List[str]):
        self.name = name
        self.instance_id = instance_id
        self.port = port
        self.capabilities = capabilities
        self.running = False
        self.heartbeat_task = None

    async def start(self):
        """Start the mock service."""
        logger.info(f"Starting service {self.name}/{self.instance_id}")
        
        # Register with service registry
        success = await register_current_service(
            service_name=self.name,
            instance_id=self.instance_id,
            host="localhost",
            port=self.port,
            version="1.0.0",
            capabilities=self.capabilities,
            metadata={
                "started_at": datetime.utcnow().isoformat(),
                "service_type": "demo",
                "constitutional_hash": CONSTITUTIONAL_HASH
            }
        )
        
        if success:
            logger.info(f"Service {self.name}/{self.instance_id} registered successfully")
            self.running = True
            
            # Start heartbeat task
            self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        else:
            logger.error(f"Failed to register service {self.name}/{self.instance_id}")

    async def stop(self):
        """Stop the mock service."""
        logger.info(f"Stopping service {self.name}/{self.instance_id}")
        
        self.running = False
        
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            try:
                await self.heartbeat_task
            except asyncio.CancelledError:
                pass
        
        # Unregister from service registry
        try:
            registry = ACGSServiceRegistry()
            await registry.initialize()
            await registry.unregister_service(self.name, self.instance_id)
            await registry.close()
            logger.info(f"Service {self.name}/{self.instance_id} unregistered")
        except Exception as e:
            logger.error(f"Failed to unregister service: {e}")

    async def _heartbeat_loop(self):
        """Send regular heartbeats."""
        while self.running:
            try:
                await asyncio.sleep(10)  # Heartbeat every 10 seconds
                
                success = await send_heartbeat(
                    service_name=self.name,
                    instance_id=self.instance_id,
                    status=ServiceStatus.HEALTHY,
                    metadata={
                        "last_heartbeat": datetime.utcnow().isoformat(),
                        "uptime_seconds": int(asyncio.get_event_loop().time()),
                        "status": "active"
                    }
                )
                
                if success:
                    logger.debug(f"Heartbeat sent for {self.name}/{self.instance_id}")
                else:
                    logger.warning(f"Heartbeat failed for {self.name}/{self.instance_id}")
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Heartbeat error for {self.name}/{self.instance_id}: {e}")

async def demo_service_registry():
    """Demonstrate the service registry pattern."""
    
    logger.info("=== ACGS Service Registry Pattern Demo ===")
    logger.info(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    
    # Initialize service registry
    registry = ACGSServiceRegistry()
    await registry.initialize()
    
    # Initialize service discovery client
    discovery_client = ServiceDiscoveryClient()
    await discovery_client.initialize()
    
    try:
        # Create mock services
        services = [
            MockService("constitutional-ai", "demo-instance-1", 8001, 
                       ["constitutional_validation", "hash_verification"]),
            MockService("api-gateway", "demo-instance-1", 8010, 
                       ["request_routing", "authentication", "rate_limiting"]),
            MockService("integrity", "demo-instance-1", 8002, 
                       ["audit_logging", "hash_chaining"]),
            MockService("governance-synthesis", "demo-instance-1", 8008, 
                       ["policy_synthesis", "conflict_resolution"]),
            MockService("multi-agent-coordinator", "demo-instance-1", 8008, 
                       ["agent_coordination", "task_decomposition"]),
        ]
        
        # Start all services
        logger.info("Starting demo services...")
        start_tasks = [service.start() for service in services]
        await asyncio.gather(*start_tasks)
        
        # Wait for services to settle
        await asyncio.sleep(2)
        
        # Demonstrate service discovery
        logger.info("\n=== Service Discovery Demo ===")
        
        # Discover all services
        all_services = await discovery_client.discover_all_services()
        logger.info(f"Discovered {len(all_services)} services:")
        for service_name, service_url in all_services.items():
            logger.info(f"  - {service_name}: {service_url}")
        
        # Get capabilities for each service
        logger.info("\n=== Service Capabilities ===")
        for service_name in all_services.keys():
            capabilities = await discovery_client.get_service_capabilities(service_name)
            logger.info(f"{service_name} capabilities: {capabilities}")
        
        # Demonstrate service registry statistics
        logger.info("\n=== Service Registry Statistics ===")
        stats = await registry.get_registry_stats()
        logger.info(f"Registry Statistics:\n{json.dumps(stats, indent=2)}")
        
        # Demonstrate specific service discovery
        logger.info("\n=== Specific Service Discovery ===")
        for service_name in ["constitutional-ai", "api-gateway", "integrity"]:
            url = await discovery_client.discover_service(service_name)
            if url:
                logger.info(f"Found {service_name} at: {url}")
            else:
                logger.warning(f"Service {service_name} not found")
        
        # Demonstrate healthy instance filtering
        logger.info("\n=== Healthy Instances ===")
        healthy_instances = await registry.get_healthy_instances("constitutional-ai")
        logger.info(f"Healthy constitutional-ai instances: {len(healthy_instances)}")
        for instance in healthy_instances:
            logger.info(f"  - {instance.instance_id} at {instance.host}:{instance.port}")
        
        # Wait to observe heartbeats
        logger.info("\n=== Monitoring Heartbeats (15 seconds) ===")
        await asyncio.sleep(15)
        
        # Show updated statistics
        logger.info("\n=== Updated Statistics ===")
        stats = await registry.get_registry_stats()
        logger.info(f"Updated Registry Statistics:\n{json.dumps(stats, indent=2)}")
        
        # Demonstrate service lifecycle: stop one service
        logger.info("\n=== Service Lifecycle Demo ===")
        logger.info("Stopping integrity service...")
        await services[2].stop()  # Stop integrity service
        
        await asyncio.sleep(2)
        
        # Show services after one stopped
        remaining_services = await discovery_client.discover_all_services()
        logger.info(f"Remaining services: {list(remaining_services.keys())}")
        
        # Restart the service
        logger.info("Restarting integrity service...")
        await services[2].start()
        
        await asyncio.sleep(2)
        
        # Show services after restart
        final_services = await discovery_client.discover_all_services()
        logger.info(f"Final services: {list(final_services.keys())}")
        
    except Exception as e:
        logger.error(f"Demo error: {e}")
        
    finally:
        # Clean up
        logger.info("\n=== Cleanup ===")
        cleanup_tasks = [service.stop() for service in services if service.running]
        if cleanup_tasks:
            await asyncio.gather(*cleanup_tasks, return_exceptions=True)
        
        await discovery_client.close()
        await registry.close()
        
        logger.info("Demo completed!")

async def demo_service_failure_handling():
    """Demonstrate service failure handling and resilience."""
    
    logger.info("\n=== Service Failure Handling Demo ===")
    
    registry = ACGSServiceRegistry()
    await registry.initialize()
    
    try:
        # Register a service
        service = MockService("failure-test", "failure-instance", 9000, ["test"])
        await service.start()
        
        # Verify it's healthy
        healthy = await registry.get_healthy_instances("failure-test")
        logger.info(f"Healthy instances before failure: {len(healthy)}")
        
        # Simulate service failure (stop heartbeats but don't unregister)
        service.running = False
        if service.heartbeat_task:
            service.heartbeat_task.cancel()
        
        logger.info("Simulated service failure (no more heartbeats)")
        
        # Wait for service to be considered expired
        logger.info("Waiting for service to expire...")
        await asyncio.sleep(registry.ttl_seconds + 5)
        
        # Trigger cleanup
        await registry._cleanup_expired_services()
        
        # Check if service was cleaned up
        remaining = await registry.discover_services("failure-test")
        logger.info(f"Remaining instances after cleanup: {len(remaining)}")
        
        if len(remaining) == 0:
            logger.info("✅ Failed service was successfully cleaned up")
        else:
            logger.warning("❌ Failed service was not cleaned up")
            
    finally:
        await registry.close()

async def main():
    """Run the complete demo."""
    try:
        await demo_service_registry()
        await demo_service_failure_handling()
    except KeyboardInterrupt:
        logger.info("Demo interrupted by user")
    except Exception as e:
        logger.error(f"Demo failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())