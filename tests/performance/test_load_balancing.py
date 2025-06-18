"""
Comprehensive Load Balancing Test Suite for ACGS-1
Tests load balancing scenarios, failover, and performance validation
"""

import asyncio
import time
from unittest.mock import Mock, patch

import pytest

from services.shared.service_mesh.discovery import (
    LoadBalancingStrategy,
    ServiceDiscovery,
    ServiceInstance,
    ServiceType,
)
from services.shared.service_mesh.failover_circuit_breaker import (
    FailoverCircuitBreaker,
    FailoverConfig,
    FailoverStrategy,
)
from services.shared.service_mesh.load_balancer import LoadBalancer
from services.shared.service_mesh.performance_monitor import (
    AlertSeverity,
    PerformanceMetrics,
    PerformanceMonitor,
)


@pytest.fixture
async def service_discovery():
    """Create service discovery instance for testing."""
    discovery = ServiceDiscovery()
    yield discovery
    await discovery.stop()


@pytest.fixture
def mock_service_instances() -> list[ServiceInstance]:
    """Create mock service instances for testing."""
    return [
        ServiceInstance(
            service_type=ServiceType.AUTH,
            instance_id="auth-1",
            base_url="http://auth-1:8000",
            port=8000,
            health_url="http://auth-1:8000/health",
            status="healthy",
            response_time=50.0,
            weight=100,
            priority=1,
        ),
        ServiceInstance(
            service_type=ServiceType.AUTH,
            instance_id="auth-2",
            base_url="http://auth-2:8000",
            port=8000,
            health_url="http://auth-2:8000/health",
            status="healthy",
            response_time=75.0,
            weight=100,
            priority=2,
        ),
        ServiceInstance(
            service_type=ServiceType.AUTH,
            instance_id="auth-3",
            base_url="http://auth-3:8000",
            port=8000,
            health_url="http://auth-3:8000/health",
            status="unhealthy",
            response_time=None,
            weight=100,
            priority=1,
        ),
    ]


class TestLoadBalancingStrategies:
    """Test different load balancing strategies."""

    def test_round_robin_selection(self, mock_service_instances):
        """Test round robin load balancing."""
        load_balancer = LoadBalancer(LoadBalancingStrategy.ROUND_ROBIN)
        healthy_instances = [inst for inst in mock_service_instances if inst.is_healthy]

        # Test multiple selections
        selections = []
        for _ in range(6):
            selected = load_balancer.select_instance(
                healthy_instances, LoadBalancingStrategy.ROUND_ROBIN
            )
            selections.append(selected.instance_id)

        # Should cycle through instances
        expected = ["auth-1", "auth-2", "auth-1", "auth-2", "auth-1", "auth-2"]
        assert selections == expected

    def test_least_connections_selection(self, mock_service_instances):
        """Test least connections load balancing."""
        load_balancer = LoadBalancer(LoadBalancingStrategy.LEAST_CONNECTIONS)
        healthy_instances = [inst for inst in mock_service_instances if inst.is_healthy]

        # Set different connection counts
        healthy_instances[0].current_connections = 5
        healthy_instances[1].current_connections = 2

        selected = load_balancer.select_instance(
            healthy_instances, LoadBalancingStrategy.LEAST_CONNECTIONS
        )

        # Should select instance with fewer connections
        assert selected.instance_id == "auth-2"
        assert selected.current_connections == 2

    def test_least_response_time_selection(self, mock_service_instances):
        """Test least response time load balancing."""
        load_balancer = LoadBalancer(LoadBalancingStrategy.LEAST_RESPONSE_TIME)
        healthy_instances = [inst for inst in mock_service_instances if inst.is_healthy]

        selected = load_balancer.select_instance(
            healthy_instances, LoadBalancingStrategy.LEAST_RESPONSE_TIME
        )

        # Should select instance with better response time
        assert selected.instance_id == "auth-1"
        assert selected.response_time == 50.0

    def test_consistent_hash_selection(self, mock_service_instances):
        """Test consistent hash load balancing for session affinity."""
        load_balancer = LoadBalancer(LoadBalancingStrategy.CONSISTENT_HASH)
        healthy_instances = [inst for inst in mock_service_instances if inst.is_healthy]

        # Test with same session ID multiple times
        session_id = "user-session-123"
        selections = []

        for _ in range(5):
            selected = load_balancer.select_instance(
                healthy_instances,
                LoadBalancingStrategy.CONSISTENT_HASH,
                hash_key=session_id,
            )
            selections.append(selected.instance_id)

        # Should always select the same instance for same session
        assert len(set(selections)) == 1

    def test_weighted_round_robin_selection(self, mock_service_instances):
        """Test weighted round robin load balancing."""
        load_balancer = LoadBalancer(LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN)
        healthy_instances = [inst for inst in mock_service_instances if inst.is_healthy]

        # Set different weights
        healthy_instances[0].weight = 200  # Higher weight
        healthy_instances[1].weight = 100  # Lower weight

        selections = []
        for _ in range(30):  # More selections to see weight distribution
            selected = load_balancer.select_instance(
                healthy_instances, LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN
            )
            selections.append(selected.instance_id)

        # Higher weight instance should be selected more often
        auth1_count = selections.count("auth-1")
        auth2_count = selections.count("auth-2")

        assert auth1_count > auth2_count


class TestFailoverMechanisms:
    """Test failover and circuit breaker mechanisms."""

    @pytest.mark.asyncio
    async def test_circuit_breaker_failover(self, mock_service_instances):
        """Test circuit breaker failover functionality."""
        config = FailoverConfig(
            strategy=FailoverStrategy.CIRCUIT_BREAK,
            circuit_breaker_threshold=3,
            max_retries=2,
        )

        failover_breaker = FailoverCircuitBreaker(ServiceType.AUTH, config)
        failover_breaker.register_instances(mock_service_instances)

        # Mock operation that fails
        async def failing_operation():
            raise Exception("Service unavailable")

        # Test multiple failures to trigger circuit breaker
        with pytest.raises(Exception):
            for _ in range(5):
                try:
                    await failover_breaker.execute_with_failover(
                        failing_operation, "auth-1"
                    )
                except Exception:
                    pass

        # Circuit breaker should be open for the failing instance
        breaker = failover_breaker.instance_breakers["auth-1"]
        assert breaker.failure_count >= config.circuit_breaker_threshold

    @pytest.mark.asyncio
    async def test_graceful_failover(self, mock_service_instances):
        """Test graceful failover with retries."""
        config = FailoverConfig(
            strategy=FailoverStrategy.GRACEFUL, max_retries=2, retry_delay=0.1
        )

        failover_breaker = FailoverCircuitBreaker(ServiceType.AUTH, config)
        failover_breaker.register_instances(mock_service_instances)

        call_count = 0

        async def intermittent_operation():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise Exception("Temporary failure")
            return "success"

        # Should succeed after retries
        result = await failover_breaker.execute_with_failover(
            intermittent_operation, "auth-1"
        )

        assert result == "success"
        assert call_count == 3  # Initial + 2 retries

    @pytest.mark.asyncio
    async def test_immediate_failover(self, mock_service_instances):
        """Test immediate failover to backup instances."""
        config = FailoverConfig(strategy=FailoverStrategy.IMMEDIATE)

        failover_breaker = FailoverCircuitBreaker(ServiceType.AUTH, config)
        failover_breaker.register_instances(mock_service_instances)

        async def failing_primary():
            raise Exception("Primary failed")

        # Should failover to backup immediately
        with patch.object(
            failover_breaker, "_immediate_failover", return_value="backup_success"
        ) as mock_failover:
            await failover_breaker.execute_with_failover(failing_primary, "auth-1")

            mock_failover.assert_called_once()


class TestPerformanceMonitoring:
    """Test performance monitoring and alerting."""

    @pytest.mark.asyncio
    async def test_performance_metrics_recording(self):
        """Test performance metrics recording."""
        monitor = PerformanceMonitor(monitoring_interval=1.0)

        # Create test metrics
        metrics = PerformanceMetrics(
            timestamp=time.time(),
            service_type="auth",
            instance_id="auth-1",
            response_time_ms=600.0,  # Above threshold
            availability_percent=98.0,  # Below threshold
            throughput_rps=100.0,
            error_rate_percent=2.0,
            concurrent_connections=50,
        )

        # Record metrics
        monitor.record_metrics(metrics)

        # Check that metrics were recorded
        key = "auth:auth-1"
        assert key in monitor.metrics_history
        assert len(monitor.metrics_history[key]) == 1
        assert monitor.metrics_history[key][0] == metrics

    @pytest.mark.asyncio
    async def test_alert_triggering(self):
        """Test alert triggering for threshold violations."""
        monitor = PerformanceMonitor()
        alerts_triggered = []

        def alert_callback(alert):
            alerts_triggered.append(alert)

        monitor.register_alert_callback(alert_callback)

        # Create metrics that exceed thresholds
        metrics = PerformanceMetrics(
            timestamp=time.time(),
            service_type="auth",
            instance_id="auth-1",
            response_time_ms=600.0,  # Above 500ms threshold
            availability_percent=98.0,  # Below 99.9% threshold
            throughput_rps=100.0,
            error_rate_percent=6.0,  # Above 5% threshold
            concurrent_connections=1100,  # Above 1000 threshold
        )

        monitor.record_metrics(metrics)

        # Should trigger multiple alerts
        assert len(alerts_triggered) >= 3

        # Check alert severities
        severities = [alert.severity for alert in alerts_triggered]
        assert AlertSeverity.CRITICAL in severities

    def test_performance_summary_calculation(self):
        """Test performance summary calculation."""
        monitor = PerformanceMonitor()

        # Add multiple metrics
        for i in range(5):
            metrics = PerformanceMetrics(
                timestamp=time.time() - (i * 60),  # Spread over time
                service_type="auth",
                instance_id=f"auth-{i}",
                response_time_ms=100.0 + (i * 50),
                availability_percent=99.0 + (i * 0.1),
                throughput_rps=50.0,
                error_rate_percent=0.5,
                concurrent_connections=100 + (i * 10),
            )
            monitor.record_metrics(metrics)

        summary = monitor.get_current_performance_summary()

        assert summary["status"] in ["healthy", "degraded", "unhealthy"]
        assert "health_score" in summary
        assert "metrics" in summary
        assert "targets" in summary


class TestConcurrentLoadHandling:
    """Test handling of concurrent load and >1000 users."""

    @pytest.mark.asyncio
    async def test_concurrent_user_handling(
        self, service_discovery, mock_service_instances
    ):
        """Test system behavior under high concurrent load."""
        # Register instances
        for instance in mock_service_instances:
            service_discovery.register_instance(instance)

        # Simulate concurrent requests
        async def simulate_request(session_id: str):
            instance = service_discovery.get_best_instance(
                ServiceType.AUTH, session_id=session_id
            )
            if instance:
                instance.increment_connections()
                await asyncio.sleep(0.01)  # Simulate processing time
                instance.decrement_connections()
                return True
            return False

        # Create 1200 concurrent requests (above 1000 target)
        tasks = [simulate_request(f"session-{i}") for i in range(1200)]

        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()

        # Check results
        successful_requests = sum(1 for r in results if r is True)
        processing_time = end_time - start_time

        # Should handle most requests successfully
        assert successful_requests >= 1000

        # Should complete within reasonable time (target: <500ms for 95% of requests)
        assert processing_time < 5.0  # Allow some overhead for testing

    @pytest.mark.asyncio
    async def test_load_distribution_under_stress(self, mock_service_instances):
        """Test load distribution under stress conditions."""
        load_balancer = LoadBalancer(LoadBalancingStrategy.LEAST_CONNECTIONS)
        healthy_instances = [inst for inst in mock_service_instances if inst.is_healthy]

        # Simulate high load
        for _ in range(1000):
            selected = load_balancer.select_instance(healthy_instances)
            selected.increment_connections()

        # Check load distribution
        total_connections = sum(inst.current_connections for inst in healthy_instances)
        assert total_connections == 1000

        # Load should be distributed (not all on one instance)
        max_connections = max(inst.current_connections for inst in healthy_instances)
        min_connections = min(inst.current_connections for inst in healthy_instances)

        # Difference shouldn't be too large (good distribution)
        assert (max_connections - min_connections) < 200


class TestSessionAffinity:
    """Test session affinity and governance workflow continuity."""

    @pytest.mark.asyncio
    async def test_session_affinity_consistency(
        self, service_discovery, mock_service_instances
    ):
        """Test that session affinity maintains consistency."""
        # Register instances
        for instance in mock_service_instances:
            service_discovery.register_instance(instance)

        session_id = "governance-session-123"

        # Multiple requests with same session should go to same instance
        selected_instances = []
        for _ in range(10):
            instance = service_discovery.get_best_instance(
                ServiceType.AUTH,
                strategy=LoadBalancingStrategy.CONSISTENT_HASH,
                session_id=session_id,
            )
            if instance:
                selected_instances.append(instance.instance_id)

        # All requests should go to the same instance
        assert len(set(selected_instances)) == 1

    @pytest.mark.asyncio
    async def test_governance_workflow_continuity(self, service_discovery):
        """Test governance workflow session continuity."""
        from services.shared.service_mesh.governance_session_manager import (
            GovernanceWorkflowType,
        )

        # Create governance session
        session_id = await service_discovery.create_governance_session(
            GovernanceWorkflowType.POLICY_CREATION, "user-123"
        )

        assert session_id is not None
        assert len(session_id) > 0

        # Advance workflow
        await service_discovery.advance_governance_workflow(
            session_id, "draft_policy", {"policy_type": "constitutional"}
        )

        # Complete session
        await service_discovery.complete_governance_session(session_id)

        # Get session stats
        stats = await service_discovery.get_governance_session_stats()
        assert "total_active_sessions" in stats


@pytest.mark.integration
class TestEndToEndLoadBalancing:
    """End-to-end integration tests for load balancing system."""

    @pytest.mark.asyncio
    async def test_full_system_integration(self):
        """Test complete load balancing system integration."""
        # This would test the full system with real HTTP requests
        # For now, we'll create a comprehensive mock test

        discovery = ServiceDiscovery()

        try:
            await discovery.start()

            # Test service registration
            instance = ServiceInstance(
                service_type=ServiceType.AUTH,
                instance_id="auth-test",
                base_url="http://localhost:8000",
                port=8000,
                health_url="http://localhost:8000/health",
            )

            discovery.register_instance(instance)

            # Test service discovery
            found_instance = discovery.get_best_instance(ServiceType.AUTH)
            assert found_instance is not None
            assert found_instance.instance_id == "auth-test"

            # Test health checking (mocked)
            with patch("httpx.AsyncClient.get") as mock_get:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.elapsed.total_seconds.return_value = 0.1
                mock_get.return_value = mock_response

                await discovery._check_instance_health(instance)
                assert instance.status == "healthy"
                assert instance.response_time == 100.0

        finally:
            await discovery.stop()


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
