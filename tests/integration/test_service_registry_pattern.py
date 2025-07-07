"""
Integration Tests for ACGS Service Registry Pattern
Constitutional Hash: cdd01ef066bc6cf2

Tests the complete service discovery and registration flow.
"""

import asyncio
import json
import time
from typing import Any, Dict
from unittest.mock import AsyncMock, patch

import pytest

from services.shared.middleware.service_discovery_middleware import (
    ServiceDiscoveryClient,
    setup_service_discovery,
)
from services.shared.service_registry import (
    CONSTITUTIONAL_HASH,
    ACGSServiceRegistry,
    ServiceInstance,
    ServiceStatus,
)

# Test configuration
TEST_REDIS_URL = "redis://localhost:6389"
TEST_REDIS_DB = 15  # Use different DB for testing


@pytest.fixture
async def service_registry():
    """Create a test service registry."""
    registry = ACGSServiceRegistry(redis_url=TEST_REDIS_URL, redis_db=TEST_REDIS_DB)

    try:
        await registry.initialize()
        yield registry
    finally:
        await registry.close()


@pytest.fixture
async def discovery_client():
    """Create a test service discovery client."""
    client = ServiceDiscoveryClient(redis_url=TEST_REDIS_URL)

    try:
        await client.initialize()
        yield client
    finally:
        await client.close()


class TestServiceRegistry:
    """Test service registry core functionality."""

    async def test_service_registration(self, service_registry):
        """Test basic service registration."""

        # Register a service
        success = await service_registry.register_service(
            service_name="test-service",
            instance_id="test-instance-1",
            host="localhost",
            port=8001,
            version="1.0.0",
            capabilities=["test_capability"],
            metadata={"test": "data"},
        )

        assert success is True

        # Discover the service
        services = await service_registry.discover_services("test-service")
        assert len(services) == 1

        service = services[0]
        assert service.service_name == "test-service"
        assert service.instance_id == "test-instance-1"
        assert service.host == "localhost"
        assert service.port == 8001
        assert service.version == "1.0.0"
        assert service.capabilities == ["test_capability"]
        assert service.constitutional_hash == CONSTITUTIONAL_HASH

    async def test_service_heartbeat(self, service_registry):
        """Test service heartbeat functionality."""

        # Register service
        await service_registry.register_service(
            service_name="heartbeat-service",
            instance_id="heartbeat-instance",
            host="localhost",
            port=8002,
            version="1.0.0",
            capabilities=["heartbeat"],
        )

        # Send heartbeat
        success = await service_registry.heartbeat(
            service_name="heartbeat-service",
            instance_id="heartbeat-instance",
            status=ServiceStatus.HEALTHY,
            metadata={"last_activity": "active"},
        )

        assert success is True

        # Check service status
        services = await service_registry.discover_services("heartbeat-service")
        assert len(services) == 1
        assert services[0].status == ServiceStatus.HEALTHY

    async def test_service_unregistration(self, service_registry):
        """Test service unregistration."""

        # Register service
        await service_registry.register_service(
            service_name="temp-service",
            instance_id="temp-instance",
            host="localhost",
            port=8003,
            version="1.0.0",
            capabilities=["temporary"],
        )

        # Verify registration
        services = await service_registry.discover_services("temp-service")
        assert len(services) == 1

        # Unregister service
        success = await service_registry.unregister_service(
            service_name="temp-service", instance_id="temp-instance"
        )

        assert success is True

        # Verify unregistration
        services = await service_registry.discover_services("temp-service")
        assert len(services) == 0

    async def test_multiple_instances(self, service_registry):
        """Test multiple instances of the same service."""

        # Register multiple instances
        for i in range(3):
            await service_registry.register_service(
                service_name="multi-service",
                instance_id=f"instance-{i}",
                host="localhost",
                port=8010 + i,
                version="1.0.0",
                capabilities=["multi"],
            )

        # Discover all instances
        services = await service_registry.discover_services("multi-service")
        assert len(services) == 3

        # Check each instance
        instance_ids = [s.instance_id for s in services]
        assert "instance-0" in instance_ids
        assert "instance-1" in instance_ids
        assert "instance-2" in instance_ids

    async def test_healthy_instances_filter(self, service_registry):
        """Test filtering for healthy instances only."""

        # Register instances with different statuses
        await service_registry.register_service(
            service_name="health-test",
            instance_id="healthy-1",
            host="localhost",
            port=8020,
            version="1.0.0",
            capabilities=["health"],
        )

        await service_registry.register_service(
            service_name="health-test",
            instance_id="unhealthy-1",
            host="localhost",
            port=8021,
            version="1.0.0",
            capabilities=["health"],
        )

        # Send heartbeats with different statuses
        await service_registry.heartbeat(
            "health-test", "healthy-1", ServiceStatus.HEALTHY
        )
        await service_registry.heartbeat(
            "health-test", "unhealthy-1", ServiceStatus.UNHEALTHY
        )

        # Get only healthy instances
        healthy_instances = await service_registry.get_healthy_instances("health-test")
        assert len(healthy_instances) == 1
        assert healthy_instances[0].instance_id == "healthy-1"
        assert healthy_instances[0].status == ServiceStatus.HEALTHY

    async def test_service_capabilities_aggregation(self, service_registry):
        """Test aggregation of service capabilities."""

        # Register instances with different capabilities
        await service_registry.register_service(
            service_name="capability-test",
            instance_id="cap-1",
            host="localhost",
            port=8030,
            version="1.0.0",
            capabilities=["read", "write"],
        )

        await service_registry.register_service(
            service_name="capability-test",
            instance_id="cap-2",
            host="localhost",
            port=8031,
            version="1.0.0",
            capabilities=["write", "delete"],
        )

        # Get aggregated capabilities
        capabilities = await service_registry.get_service_capabilities(
            "capability-test"
        )
        assert "read" in capabilities
        assert "write" in capabilities
        assert "delete" in capabilities
        assert len(capabilities) == 3

    async def test_registry_stats(self, service_registry):
        """Test service registry statistics."""

        # Register test services
        await service_registry.register_service(
            service_name="stats-service-1",
            instance_id="stats-1",
            host="localhost",
            port=8040,
            version="1.0.0",
            capabilities=["stats"],
        )

        await service_registry.register_service(
            service_name="stats-service-2",
            instance_id="stats-2",
            host="localhost",
            port=8041,
            version="1.0.0",
            capabilities=["metrics"],
        )

        # Get registry stats
        stats = await service_registry.get_registry_stats()

        assert stats["constitutional_hash"] == CONSTITUTIONAL_HASH
        assert stats["total_services"] >= 2
        assert "stats-service-1" in stats["services"]
        assert "stats-service-2" in stats["services"]
        assert stats["registry_health"] == "healthy"

    async def test_constitutional_compliance_validation(self, service_registry):
        """Test constitutional compliance validation."""

        # Test with correct hash
        registry_with_correct_hash = ACGSServiceRegistry(
            redis_url=TEST_REDIS_URL, redis_db=TEST_REDIS_DB
        )
        registry_with_correct_hash.constitutional_hash = CONSTITUTIONAL_HASH

        assert registry_with_correct_hash._validate_constitutional_compliance() is True

        # Test with incorrect hash
        registry_with_wrong_hash = ACGSServiceRegistry(
            redis_url=TEST_REDIS_URL, redis_db=TEST_REDIS_DB
        )
        registry_with_wrong_hash.constitutional_hash = "wrong_hash"

        assert registry_with_wrong_hash._validate_constitutional_compliance() is False


class TestServiceDiscoveryClient:
    """Test service discovery client functionality."""

    async def test_service_discovery(self, service_registry, discovery_client):
        """Test service discovery through client."""

        # Register a service through registry
        await service_registry.register_service(
            service_name="discovered-service",
            instance_id="discovered-instance",
            host="localhost",
            port=8050,
            version="1.0.0",
            capabilities=["discovery"],
        )

        # Send heartbeat to mark as healthy
        await service_registry.heartbeat(
            "discovered-service", "discovered-instance", ServiceStatus.HEALTHY
        )

        # Discover service through client
        service_url = await discovery_client.discover_service("discovered-service")
        assert service_url == "http://localhost:8050"

    async def test_discover_all_services(self, service_registry, discovery_client):
        """Test discovering all services."""

        # Register multiple services
        services_data = [
            ("service-a", "instance-a", 8060),
            ("service-b", "instance-b", 8061),
            ("service-c", "instance-c", 8062),
        ]

        for service_name, instance_id, port in services_data:
            await service_registry.register_service(
                service_name=service_name,
                instance_id=instance_id,
                host="localhost",
                port=port,
                version="1.0.0",
                capabilities=["test"],
            )

            # Mark as healthy
            await service_registry.heartbeat(
                service_name, instance_id, ServiceStatus.HEALTHY
            )

        # Discover all services
        all_services = await discovery_client.discover_all_services()

        assert "service-a" in all_services
        assert "service-b" in all_services
        assert "service-c" in all_services
        assert all_services["service-a"] == "http://localhost:8060"
        assert all_services["service-b"] == "http://localhost:8061"
        assert all_services["service-c"] == "http://localhost:8062"

    async def test_get_service_capabilities_through_client(
        self, service_registry, discovery_client
    ):
        """Test getting service capabilities through client."""

        # Register service with capabilities
        await service_registry.register_service(
            service_name="capability-service",
            instance_id="capability-instance",
            host="localhost",
            port=8070,
            version="1.0.0",
            capabilities=["read", "write", "execute"],
        )

        # Get capabilities through client
        capabilities = await discovery_client.get_service_capabilities(
            "capability-service"
        )

        assert "read" in capabilities
        assert "write" in capabilities
        assert "execute" in capabilities
        assert len(capabilities) == 3


class TestServiceRegistryIntegration:
    """Test complete service registry integration scenarios."""

    async def test_service_lifecycle(self, service_registry):
        """Test complete service lifecycle."""

        service_name = "lifecycle-service"
        instance_id = "lifecycle-instance"

        # 1. Register service
        success = await service_registry.register_service(
            service_name=service_name,
            instance_id=instance_id,
            host="localhost",
            port=8080,
            version="1.0.0",
            capabilities=["lifecycle"],
        )
        assert success is True

        # 2. Service should be discoverable
        services = await service_registry.discover_services(service_name)
        assert len(services) == 1
        assert services[0].status == ServiceStatus.STARTING

        # 3. Send heartbeat to mark as healthy
        await service_registry.heartbeat(
            service_name, instance_id, ServiceStatus.HEALTHY
        )

        # 4. Service should be healthy
        healthy_services = await service_registry.get_healthy_instances(service_name)
        assert len(healthy_services) == 1
        assert healthy_services[0].status == ServiceStatus.HEALTHY

        # 5. Update metadata through heartbeat
        await service_registry.heartbeat(
            service_name,
            instance_id,
            ServiceStatus.HEALTHY,
            metadata={"updated": "true"},
        )

        # 6. Verify metadata update
        services = await service_registry.discover_services(service_name)
        assert services[0].metadata.get("updated") == "true"

        # 7. Unregister service
        await service_registry.unregister_service(service_name, instance_id)

        # 8. Service should no longer be discoverable
        services = await service_registry.discover_services(service_name)
        assert len(services) == 0

    async def test_service_registry_resilience(self, service_registry):
        """Test service registry resilience and cleanup."""

        # Register service
        await service_registry.register_service(
            service_name="resilience-test",
            instance_id="resilience-instance",
            host="localhost",
            port=8090,
            version="1.0.0",
            capabilities=["resilience"],
        )

        # Verify registration
        services = await service_registry.discover_services("resilience-test")
        assert len(services) == 1

        # Simulate service going offline (no heartbeat)
        # Wait longer than TTL
        await asyncio.sleep(service_registry.ttl_seconds + 1)

        # Trigger cleanup (normally done by background task)
        await service_registry._cleanup_expired_services()

        # Service should be cleaned up
        services = await service_registry.discover_services("resilience-test")
        assert len(services) == 0

    async def test_concurrent_operations(self, service_registry):
        """Test concurrent service registry operations."""

        async def register_service(i):
            return await service_registry.register_service(
                service_name=f"concurrent-service-{i}",
                instance_id=f"concurrent-instance-{i}",
                host="localhost",
                port=9000 + i,
                version="1.0.0",
                capabilities=[f"concurrent-{i}"],
            )

        async def send_heartbeat(i):
            return await service_registry.heartbeat(
                f"concurrent-service-{i}",
                f"concurrent-instance-{i}",
                ServiceStatus.HEALTHY,
            )

        # Register 10 services concurrently
        registration_tasks = [register_service(i) for i in range(10)]
        registration_results = await asyncio.gather(*registration_tasks)

        # All registrations should succeed
        assert all(registration_results)

        # Send heartbeats concurrently
        heartbeat_tasks = [send_heartbeat(i) for i in range(10)]
        heartbeat_results = await asyncio.gather(*heartbeat_tasks)

        # All heartbeats should succeed
        assert all(heartbeat_results)

        # Verify all services are discoverable
        all_services = await service_registry.discover_services()
        concurrent_services = [
            s for s in all_services if s.service_name.startswith("concurrent-service-")
        ]
        assert len(concurrent_services) == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
