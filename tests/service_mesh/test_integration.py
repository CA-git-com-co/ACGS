"""
Integration Tests for ACGS-1 Load Balancing System
End-to-end testing of load balancing, failover, and infrastructure integration
"""

import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest

from services.shared.service_mesh.discovery import (
    ServiceDiscovery,
    ServiceInstance,
    ServiceType,
)
from services.shared.service_mesh.governance_session_manager import (
    GovernanceWorkflowType,
)


@pytest.fixture
async def integrated_system():
    """Create integrated load balancing system for testing."""
    discovery = ServiceDiscovery()

    # Mock Redis and database connections
    with patch(
        "services.shared.advanced_redis_client.AdvancedRedisClient"
    ) as mock_redis:
        mock_redis_instance = Mock()
        mock_redis_instance.setex = AsyncMock()
        mock_redis_instance.get = AsyncMock(return_value=None)
        mock_redis_instance.keys = AsyncMock(return_value=[])
        mock_redis_instance.delete = AsyncMock()
        mock_redis_instance.info = AsyncMock(return_value={})
        mock_redis.return_value = mock_redis_instance

        await discovery.start()
        yield discovery
        await discovery.stop()


@pytest.fixture
def mock_http_responses():
    """Mock HTTP responses for health checks."""

    def create_response(status_code=200, response_time=0.1):
        response = Mock()
        response.status_code = status_code
        response.elapsed.total_seconds.return_value = response_time
        response.json.return_value = {"status": "healthy"}
        return response

    return create_response


class TestFullSystemIntegration:
    """Test complete system integration."""

    @pytest.mark.asyncio
    async def test_service_discovery_with_load_balancing(
        self, integrated_system, mock_http_responses
    ):
        """Test service discovery integrated with load balancing."""
        discovery = integrated_system

        # Register multiple instances for each service
        services_config = [
            (ServiceType.AUTH, 8000, 3),
            (ServiceType.AC, 8001, 2),
            (ServiceType.GS, 8004, 3),
            (ServiceType.PGC, 8005, 2),
        ]

        for service_type, port, instance_count in services_config:
            for i in range(instance_count):
                instance = ServiceInstance(
                    service_type=service_type,
                    instance_id=f"{service_type.value}-{i}",
                    base_url=f"http://{service_type.value}-{i}:{port}",
                    port=port,
                    health_url=f"http://{service_type.value}-{i}:{port}/health",
                    status="healthy",
                    weight=(
                        100 if i < instance_count - 1 else 150
                    ),  # Last instance has higher weight
                )
                discovery.register_instance(instance)

        # Test load balancing across services
        for service_type, _, _ in services_config:
            # Test multiple selections
            selections = []
            for _ in range(10):
                instance = discovery.get_best_instance(service_type)
                if instance:
                    selections.append(instance.instance_id)

            # Should distribute load
            assert (
                len(set(selections)) > 1
            ), f"No load distribution for {service_type.value}"

            # Test session affinity
            session_selections = []
            session_id = f"test-session-{service_type.value}"
            for _ in range(5):
                instance = discovery.get_best_instance(
                    service_type, session_id=session_id
                )
                if instance:
                    session_selections.append(instance.instance_id)

            # Session affinity should route to same instance
            assert (
                len(set(session_selections)) == 1
            ), f"Session affinity failed for {service_type.value}"

    @pytest.mark.asyncio
    async def test_health_monitoring_integration(
        self, integrated_system, mock_http_responses
    ):
        """Test health monitoring integration."""
        discovery = integrated_system

        # Register instances
        instances = []
        for i in range(3):
            instance = ServiceInstance(
                service_type=ServiceType.AUTH,
                instance_id=f"auth-{i}",
                base_url=f"http://auth-{i}:8000",
                port=8000,
                health_url=f"http://auth-{i}:8000/health",
                status="unknown",
            )
            instances.append(instance)
            discovery.register_instance(instance)

        # Mock health check responses
        with patch("httpx.AsyncClient.get") as mock_get:
            # First instance healthy
            mock_get.side_effect = [
                mock_http_responses(200, 0.05),  # auth-0: healthy, fast
                mock_http_responses(200, 0.15),  # auth-1: healthy, slower
                mock_http_responses(500, 0.30),  # auth-2: unhealthy
            ]

            # Perform health checks
            for instance in instances:
                await discovery._check_instance_health(instance)

        # Verify health status
        healthy_instances = discovery.get_healthy_instances(ServiceType.AUTH)
        assert len(healthy_instances) == 2

        # Verify response times recorded
        assert instances[0].response_time == 50.0  # 0.05s -> 50ms
        assert instances[1].response_time == 150.0  # 0.15s -> 150ms
        assert instances[2].status == "unhealthy"

        # Test load balancing with health status
        selected_instances = []
        for _ in range(10):
            instance = discovery.get_best_instance(ServiceType.AUTH)
            if instance:
                selected_instances.append(instance.instance_id)

        # Should only select healthy instances
        assert "auth-2" not in selected_instances
        assert "auth-0" in selected_instances or "auth-1" in selected_instances

    @pytest.mark.asyncio
    async def test_failover_integration(self, integrated_system):
        """Test failover integration with load balancing."""
        discovery = integrated_system

        # Register instances with different priorities
        primary_instance = ServiceInstance(
            service_type=ServiceType.PGC,
            instance_id="pgc-primary",
            base_url="http://pgc-primary:8005",
            port=8005,
            health_url="http://pgc-primary:8005/health",
            status="healthy",
            priority=1,  # Primary
        )

        backup_instance = ServiceInstance(
            service_type=ServiceType.PGC,
            instance_id="pgc-backup",
            base_url="http://pgc-backup:8005",
            port=8005,
            health_url="http://pgc-backup:8005/health",
            status="healthy",
            priority=2,  # Backup
        )

        discovery.register_instance(primary_instance)
        discovery.register_instance(backup_instance)

        # Test normal operation (should prefer primary)
        instance = discovery.get_best_instance(ServiceType.PGC)
        assert instance.instance_id == "pgc-primary"

        # Simulate primary failure
        primary_instance.status = "unhealthy"

        # Should failover to backup
        instance = discovery.get_best_instance(ServiceType.PGC)
        assert instance.instance_id == "pgc-backup"

        # Test failover with circuit breaker
        async def failing_operation():
            raise Exception("Service failure")

        # Execute with failover
        try:
            await discovery.execute_with_failover(
                ServiceType.PGC, failing_operation, "pgc-primary"
            )
        except Exception:
            pass  # Expected to fail

        # Check failover status
        failover_status = discovery.get_failover_status(ServiceType.PGC)
        assert "degraded_mode" in failover_status

    @pytest.mark.asyncio
    async def test_governance_session_integration(self, integrated_system):
        """Test governance session integration."""
        discovery = integrated_system

        # Register governance services
        governance_services = [
            ServiceType.AUTH,
            ServiceType.AC,
            ServiceType.GS,
            ServiceType.PGC,
        ]

        for service_type in governance_services:
            for i in range(2):
                instance = ServiceInstance(
                    service_type=service_type,
                    instance_id=f"{service_type.value}-{i}",
                    base_url=f"http://{service_type.value}-{i}:800{i}",
                    port=8000 + i,
                    health_url=f"http://{service_type.value}-{i}:800{i}/health",
                    status="healthy",
                )
                discovery.register_instance(instance)

        # Create governance session
        session_id = await discovery.create_governance_session(
            GovernanceWorkflowType.POLICY_CREATION,
            "test-user-123",
            {"policy_type": "constitutional"},
        )

        assert session_id is not None

        # Test service affinity for governance workflow
        service_affinities = {}

        for service_type in governance_services:
            instance = await discovery.get_instance_for_governance_session(
                service_type,
                session_id,
                GovernanceWorkflowType.POLICY_CREATION,
                "test-user-123",
            )

            assert instance is not None
            service_affinities[service_type.value] = instance.instance_id

        # Verify session affinity consistency
        for service_type in governance_services:
            instance = await discovery.get_instance_for_governance_session(
                service_type,
                session_id,
                GovernanceWorkflowType.POLICY_CREATION,
                "test-user-123",
            )

            # Should get same instance for same session
            assert instance.instance_id == service_affinities[service_type.value]

        # Test workflow progression
        workflow_steps = [
            "authenticate",
            "draft_policy",
            "constitutional_review",
            "compliance_check",
            "finalize",
        ]

        for step in workflow_steps:
            await discovery.advance_governance_workflow(
                session_id, step, {"step_data": f"data-{step}"}
            )

        # Complete session
        await discovery.complete_governance_session(session_id)

        # Verify session statistics
        stats = await discovery.get_governance_session_stats()
        assert "total_active_sessions" in stats

    @pytest.mark.asyncio
    async def test_performance_monitoring_integration(self, integrated_system):
        """Test performance monitoring integration."""
        discovery = integrated_system

        # Register instances
        for i in range(3):
            instance = ServiceInstance(
                service_type=ServiceType.GS,
                instance_id=f"gs-{i}",
                base_url=f"http://gs-{i}:8004",
                port=8004,
                health_url=f"http://gs-{i}:8004/health",
                status="healthy",
            )
            discovery.register_instance(instance)

        # Simulate load and monitor performance
        request_count = 100

        for i in range(request_count):
            instance = discovery.get_best_instance(ServiceType.GS)
            if instance:
                # Simulate request processing
                instance.increment_connections()
                instance.total_requests += 1

                # Simulate variable response times
                if i % 10 == 0:  # 10% slow requests
                    instance.response_time = 800.0  # Slow response
                    instance.failed_requests += 1
                else:
                    instance.response_time = 100.0  # Fast response

                instance.decrement_connections()

        # Check performance monitoring
        if discovery.performance_monitor:
            summary = discovery.performance_monitor.get_current_performance_summary()

            # Should have performance data
            assert "status" in summary
            assert "metrics" in summary or summary["status"] in [
                "no_data",
                "no_recent_data",
            ]

        # Check load balancing stats
        stats = discovery.get_load_balancing_stats(ServiceType.GS)
        assert "total_instances" in stats
        assert "healthy_instances" in stats
        assert "total_requests" in stats


class TestInfrastructureIntegration:
    """Test infrastructure integration components."""

    @pytest.mark.asyncio
    async def test_redis_caching_integration(self):
        """Test Redis caching integration."""
        # Mock Redis client
        with patch(
            "services.shared.advanced_redis_client.AdvancedRedisClient"
        ) as mock_redis_class:
            mock_redis = Mock()
            mock_redis.setex = AsyncMock()
            mock_redis.get = AsyncMock()
            mock_redis.keys = AsyncMock(return_value=[])
            mock_redis_class.return_value = mock_redis

            from services.shared.service_mesh.infrastructure_integration import (
                RedisLoadBalancingCache,
            )

            cache = RedisLoadBalancingCache(mock_redis)

            # Test service instance caching
            instances = [
                ServiceInstance(
                    service_type=ServiceType.AUTH,
                    instance_id="auth-1",
                    base_url="http://auth-1:8000",
                    port=8000,
                    health_url="http://auth-1:8000/health",
                    status="healthy",
                )
            ]

            await cache.cache_service_instances(ServiceType.AUTH, instances)

            # Verify Redis calls
            mock_redis.setex.assert_called()
            call_args = mock_redis.setex.call_args
            assert "lb:instances:auth" in call_args[0][0]

            # Test session affinity caching
            await cache.cache_session_affinity(
                "session-123", ServiceType.AUTH, "auth-1"
            )

            # Verify session affinity call
            assert mock_redis.setex.call_count >= 2

    @pytest.mark.asyncio
    async def test_database_integration(self):
        """Test database integration for metrics storage."""
        # Mock database connection
        with patch("asyncpg.create_pool") as mock_create_pool:
            mock_pool = Mock()
            mock_connection = Mock()
            mock_connection.fetch = AsyncMock(return_value=[])
            mock_pool.acquire.return_value.__aenter__ = AsyncMock(
                return_value=mock_connection
            )
            mock_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=None)
            mock_create_pool.return_value = mock_pool

            from services.shared.service_mesh.infrastructure_integration import (
                ConnectionPoolConfig,
                DatabaseConnectionManager,
            )

            config = ConnectionPoolConfig(min_connections=1, max_connections=5)
            db_manager = DatabaseConnectionManager(config)

            # Test pool creation
            pool = await db_manager.create_pool("test_pool", "postgresql://test")
            assert pool is not None

            # Test query execution
            await db_manager.execute_query("test_pool", "SELECT 1")

            # Verify database calls
            mock_create_pool.assert_called_once()
            mock_connection.fetch.assert_called_once()


class TestEndToEndScenarios:
    """Test complete end-to-end scenarios."""

    @pytest.mark.asyncio
    async def test_complete_governance_workflow(self, integrated_system):
        """Test complete governance workflow end-to-end."""
        discovery = integrated_system

        # Setup complete service ecosystem
        all_services = [
            ServiceType.AUTH,
            ServiceType.AC,
            ServiceType.INTEGRITY,
            ServiceType.FV,
            ServiceType.GS,
            ServiceType.PGC,
            ServiceType.EC,
        ]

        for service_type in all_services:
            for i in range(2):  # 2 instances per service
                instance = ServiceInstance(
                    service_type=service_type,
                    instance_id=f"{service_type.value}-{i}",
                    base_url=f"http://{service_type.value}-{i}:800{i}",
                    port=8000 + i,
                    health_url=f"http://{service_type.value}-{i}:800{i}/health",
                    status="healthy",
                )
                discovery.register_instance(instance)

        # Execute complete governance workflow

        async def complete_governance_workflow(user_id: str):
            """Execute a complete governance workflow."""
            try:
                # 1. Create governance session
                session_id = await discovery.create_governance_session(
                    GovernanceWorkflowType.CONSTITUTIONAL_COMPLIANCE, user_id
                )

                # 2. Authentication
                auth_instance = await discovery.get_instance_for_governance_session(
                    ServiceType.AUTH,
                    session_id,
                    GovernanceWorkflowType.CONSTITUTIONAL_COMPLIANCE,
                    user_id,
                )
                assert auth_instance is not None

                # 3. Constitutional AI Review
                ac_instance = await discovery.get_instance_for_governance_session(
                    ServiceType.AC,
                    session_id,
                    GovernanceWorkflowType.CONSTITUTIONAL_COMPLIANCE,
                    user_id,
                )
                assert ac_instance is not None

                # 4. Policy Governance Control
                pgc_instance = await discovery.get_instance_for_governance_session(
                    ServiceType.PGC,
                    session_id,
                    GovernanceWorkflowType.CONSTITUTIONAL_COMPLIANCE,
                    user_id,
                )
                assert pgc_instance is not None

                # 5. Governance Synthesis
                gs_instance = await discovery.get_instance_for_governance_session(
                    ServiceType.GS,
                    session_id,
                    GovernanceWorkflowType.CONSTITUTIONAL_COMPLIANCE,
                    user_id,
                )
                assert gs_instance is not None

                # 6. Complete workflow
                await discovery.complete_governance_session(session_id)

                return True

            except Exception:
                return False

        # Run multiple concurrent workflows
        num_workflows = 20
        tasks = [
            complete_governance_workflow(f"user-{i}") for i in range(num_workflows)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Analyze results
        successful_workflows = sum(1 for r in results if r is True)
        success_rate = (successful_workflows / num_workflows) * 100

        # Validate end-to-end performance
        assert success_rate >= 95.0, f"Workflow success rate {success_rate}% too low"

        # Check system health after load
        system_status = discovery.get_system_failover_status()
        assert "services" in system_status

        # Verify session statistics
        session_stats = await discovery.get_governance_session_stats()
        assert "total_active_sessions" in session_stats


if __name__ == "__main__":
    # Run integration tests
    pytest.main([__file__, "-v", "--tb=short"])
