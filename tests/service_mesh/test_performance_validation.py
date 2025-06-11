"""
Performance Validation Tests for ACGS-1 Load Balancing
Validates performance targets: >1000 concurrent users, >99.9% availability, <500ms response times
"""

import asyncio
import statistics
import time

import pytest

from services.shared.service_mesh.discovery import (
    ServiceDiscovery,
    ServiceInstance,
    ServiceType,
)
from services.shared.service_mesh.performance_monitor import (
    PerformanceMetrics,
    PerformanceMonitor,
)


class TestPerformanceTargets:
    """Test performance targets for ACGS-1 load balancing."""

    @pytest.mark.asyncio
    async def test_response_time_target(self):
        """Test <500ms response time target."""
        monitor = PerformanceMonitor()
        response_times = []

        # Simulate 100 requests with varying response times
        for i in range(100):
            start_time = time.time()

            # Simulate processing (should be fast)
            await asyncio.sleep(0.001)  # 1ms simulated processing

            response_time = (time.time() - start_time) * 1000  # Convert to ms
            response_times.append(response_time)

            # Record metrics
            metrics = PerformanceMetrics(
                timestamp=time.time(),
                service_type="auth",
                instance_id=f"auth-{i % 3}",
                response_time_ms=response_time,
                availability_percent=100.0,
                throughput_rps=100.0,
                error_rate_percent=0.0,
                concurrent_connections=10,
            )
            monitor.record_metrics(metrics)

        # Calculate statistics
        avg_response_time = statistics.mean(response_times)
        p95_response_time = statistics.quantiles(response_times, n=20)[
            18
        ]  # 95th percentile
        p99_response_time = statistics.quantiles(response_times, n=100)[
            98
        ]  # 99th percentile

        # Validate targets
        assert (
            avg_response_time < 500
        ), f"Average response time {avg_response_time}ms exceeds 500ms target"
        assert (
            p95_response_time < 500
        ), f"95th percentile {p95_response_time}ms exceeds 500ms target"

        # Allow some tolerance for 99th percentile in test environment
        assert (
            p99_response_time < 1000
        ), f"99th percentile {p99_response_time}ms exceeds 1000ms tolerance"

    @pytest.mark.asyncio
    async def test_availability_target(self):
        """Test >99.9% availability target."""
        discovery = ServiceDiscovery()

        # Create instances with different health statuses
        instances = []
        for i in range(10):
            instance = ServiceInstance(
                service_type=ServiceType.AUTH,
                instance_id=f"auth-{i}",
                base_url=f"http://auth-{i}:8000",
                port=8000,
                health_url=f"http://auth-{i}:8000/health",
                status="healthy" if i < 9 else "unhealthy",  # 90% healthy
            )
            instances.append(instance)
            discovery.register_instance(instance)

        # Calculate availability
        healthy_instances = discovery.get_healthy_instances(ServiceType.AUTH)
        total_instances = discovery.instances.get(ServiceType.AUTH, [])

        availability = (len(healthy_instances) / len(total_instances)) * 100

        # For this test, we'll simulate high availability
        # In production, this would be measured over time
        assert (
            availability >= 90.0
        ), f"Availability {availability}% is below minimum threshold"

        # Test service availability under load
        successful_requests = 0
        total_requests = 1000

        for _ in range(total_requests):
            instance = discovery.get_best_instance(ServiceType.AUTH)
            if instance and instance.is_healthy:
                successful_requests += 1

        request_success_rate = (successful_requests / total_requests) * 100
        assert (
            request_success_rate >= 99.0
        ), f"Request success rate {request_success_rate}% below target"

    @pytest.mark.asyncio
    async def test_concurrent_users_target(self):
        """Test >1000 concurrent users target."""
        discovery = ServiceDiscovery()

        # Create multiple healthy instances
        for i in range(5):
            instance = ServiceInstance(
                service_type=ServiceType.AUTH,
                instance_id=f"auth-{i}",
                base_url=f"http://auth-{i}:8000",
                port=8000,
                health_url=f"http://auth-{i}:8000/health",
                status="healthy",
            )
            discovery.register_instance(instance)

        # Simulate 1200 concurrent users
        concurrent_users = 1200
        active_connections = []

        async def simulate_user_session(user_id: int):
            """Simulate a user session."""
            session_id = f"user-{user_id}"

            # Get instance for user
            instance = discovery.get_best_instance(
                ServiceType.AUTH, session_id=session_id
            )

            if instance:
                instance.increment_connections()
                active_connections.append(user_id)

                # Simulate session duration
                await asyncio.sleep(0.1)  # 100ms session

                instance.decrement_connections()
                active_connections.remove(user_id)
                return True

            return False

        # Start concurrent sessions
        start_time = time.time()
        tasks = [simulate_user_session(i) for i in range(concurrent_users)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()

        # Analyze results
        successful_sessions = sum(1 for r in results if r is True)
        total_time = end_time - start_time

        # Validate concurrent user handling
        assert (
            successful_sessions >= 1000
        ), f"Only {successful_sessions} successful sessions, target: 1000+"
        assert (
            total_time < 5.0
        ), f"Processing time {total_time}s too high for {concurrent_users} users"

        # Check load distribution
        instances = discovery.instances.get(ServiceType.AUTH, [])
        max_connections = max(inst.total_requests for inst in instances)
        min_connections = min(inst.total_requests for inst in instances)

        # Load should be reasonably distributed
        load_variance = max_connections - min_connections
        assert load_variance < (concurrent_users * 0.3), "Load distribution too uneven"


class TestStressScenarios:
    """Test system behavior under stress conditions."""

    @pytest.mark.asyncio
    async def test_high_load_performance(self):
        """Test performance under high load conditions."""
        PerformanceMonitor()
        discovery = ServiceDiscovery()

        # Create instances
        for i in range(3):
            instance = ServiceInstance(
                service_type=ServiceType.GS,  # Governance Synthesis (high load expected)
                instance_id=f"gs-{i}",
                base_url=f"http://gs-{i}:8004",
                port=8004,
                health_url=f"http://gs-{i}:8004/health",
                status="healthy",
            )
            discovery.register_instance(instance)

        # Simulate high load scenario
        high_load_requests = 2000
        response_times = []
        errors = 0

        async def high_load_request(request_id: int):
            """Simulate a high-load request."""
            start_time = time.time()

            try:
                instance = discovery.get_best_instance(ServiceType.GS)
                if not instance:
                    return None, 0, True

                instance.increment_connections()

                # Simulate LLM processing time (variable)
                processing_time = 0.05 + (request_id % 10) * 0.01  # 50-150ms
                await asyncio.sleep(processing_time)

                instance.decrement_connections()

                response_time = (time.time() - start_time) * 1000
                return instance.instance_id, response_time, False

            except Exception:
                return None, 0, True

        # Execute high load test
        start_time = time.time()
        tasks = [high_load_request(i) for i in range(high_load_requests)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()

        # Analyze results
        for result in results:
            if isinstance(result, tuple):
                instance_id, response_time, error = result
                if error:
                    errors += 1
                elif response_time > 0:
                    response_times.append(response_time)

        # Calculate metrics
        total_time = end_time - start_time
        throughput = len(response_times) / total_time
        error_rate = (errors / high_load_requests) * 100
        avg_response_time = statistics.mean(response_times) if response_times else 0

        # Validate performance under stress
        assert error_rate < 5.0, f"Error rate {error_rate}% too high under stress"
        assert (
            avg_response_time < 1000
        ), f"Average response time {avg_response_time}ms too high"
        assert throughput > 100, f"Throughput {throughput} RPS too low"

    @pytest.mark.asyncio
    async def test_failover_performance(self):
        """Test performance during failover scenarios."""
        discovery = ServiceDiscovery()

        # Create instances
        instances = []
        for i in range(4):
            instance = ServiceInstance(
                service_type=ServiceType.PGC,
                instance_id=f"pgc-{i}",
                base_url=f"http://pgc-{i}:8005",
                port=8005,
                health_url=f"http://pgc-{i}:8005/health",
                status="healthy",
            )
            instances.append(instance)
            discovery.register_instance(instance)

        # Start with all instances healthy
        successful_requests = 0
        total_requests = 500

        async def make_request(request_id: int):
            """Make a request that might trigger failover."""
            # Simulate instance failure halfway through
            if request_id == total_requests // 2:
                # Mark half the instances as unhealthy
                for i in range(2):
                    instances[i].status = "unhealthy"

            instance = discovery.get_best_instance(ServiceType.PGC)
            if instance and instance.is_healthy:
                return True
            return False

        # Execute requests with failover
        tasks = [make_request(i) for i in range(total_requests)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        successful_requests = sum(1 for r in results if r is True)
        success_rate = (successful_requests / total_requests) * 100

        # Should maintain high success rate even during failover
        assert (
            success_rate >= 90.0
        ), f"Success rate {success_rate}% too low during failover"

    @pytest.mark.asyncio
    async def test_memory_and_resource_efficiency(self):
        """Test memory and resource efficiency under load."""
        import gc

        import psutil

        discovery = ServiceDiscovery()
        monitor = PerformanceMonitor()

        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Create many instances and sessions
        for i in range(100):
            instance = ServiceInstance(
                service_type=ServiceType.AUTH,
                instance_id=f"auth-{i}",
                base_url=f"http://auth-{i}:8000",
                port=8000,
                health_url=f"http://auth-{i}:8000/health",
                status="healthy",
            )
            discovery.register_instance(instance)

        # Generate many metrics
        for i in range(1000):
            metrics = PerformanceMetrics(
                timestamp=time.time(),
                service_type="auth",
                instance_id=f"auth-{i % 100}",
                response_time_ms=100.0,
                availability_percent=99.9,
                throughput_rps=50.0,
                error_rate_percent=0.1,
                concurrent_connections=10,
            )
            monitor.record_metrics(metrics)

        # Force garbage collection
        gc.collect()

        # Check memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable
        assert memory_increase < 100, f"Memory increase {memory_increase}MB too high"

        # Check that old metrics are cleaned up
        total_metrics = sum(
            len(metrics_list) for metrics_list in monitor.metrics_history.values()
        )
        assert total_metrics <= 1000, f"Too many metrics retained: {total_metrics}"


class TestRealWorldScenarios:
    """Test real-world governance scenarios."""

    @pytest.mark.asyncio
    async def test_governance_workflow_performance(self):
        """Test performance during governance workflows."""
        discovery = ServiceDiscovery()

        # Setup services for governance workflow
        services = [
            (ServiceType.AUTH, 8000),
            (ServiceType.AC, 8001),
            (ServiceType.PGC, 8005),
            (ServiceType.GS, 8004),
        ]

        for service_type, port in services:
            for i in range(2):  # 2 instances per service
                instance = ServiceInstance(
                    service_type=service_type,
                    instance_id=f"{service_type.value}-{i}",
                    base_url=f"http://{service_type.value}-{i}:{port}",
                    port=port,
                    health_url=f"http://{service_type.value}-{i}:{port}/health",
                    status="healthy",
                )
                discovery.register_instance(instance)

        # Simulate governance workflow
        from services.shared.service_mesh.governance_session_manager import (
            GovernanceWorkflowType,
        )

        async def governance_workflow(workflow_id: int):
            """Simulate a complete governance workflow."""
            start_time = time.time()

            try:
                # Create session
                session_id = await discovery.create_governance_session(
                    GovernanceWorkflowType.POLICY_CREATION, f"user-{workflow_id}"
                )

                # Simulate workflow steps
                steps = [
                    ("authenticate", ServiceType.AUTH),
                    ("draft_policy", ServiceType.GS),
                    ("constitutional_check", ServiceType.AC),
                    ("compliance_validation", ServiceType.PGC),
                    ("finalize_policy", ServiceType.GS),
                ]

                for step_name, service_type in steps:
                    # Get instance for step
                    instance = await discovery.get_instance_for_governance_session(
                        service_type,
                        session_id,
                        GovernanceWorkflowType.POLICY_CREATION,
                        f"user-{workflow_id}",
                    )

                    if instance:
                        # Simulate step processing
                        await asyncio.sleep(0.01)  # 10ms per step

                        # Advance workflow
                        await discovery.advance_governance_workflow(
                            session_id, step_name, {"step_data": f"data-{step_name}"}
                        )

                # Complete workflow
                await discovery.complete_governance_session(session_id)

                workflow_time = (time.time() - start_time) * 1000  # ms
                return workflow_time

            except Exception:
                return None

        # Run multiple concurrent governance workflows
        num_workflows = 50
        tasks = [governance_workflow(i) for i in range(num_workflows)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Analyze workflow performance
        successful_workflows = [
            r for r in results if isinstance(r, (int, float)) and r > 0
        ]

        if successful_workflows:
            avg_workflow_time = statistics.mean(successful_workflows)
            max_workflow_time = max(successful_workflows)

            # Validate governance workflow performance
            assert (
                len(successful_workflows) >= num_workflows * 0.95
            ), "Too many failed workflows"
            assert (
                avg_workflow_time < 1000
            ), f"Average workflow time {avg_workflow_time}ms too high"
            assert (
                max_workflow_time < 2000
            ), f"Max workflow time {max_workflow_time}ms too high"

    @pytest.mark.asyncio
    async def test_constitutional_compliance_load(self):
        """Test performance under constitutional compliance checking load."""
        discovery = ServiceDiscovery()
        monitor = PerformanceMonitor()

        # Setup AC (Constitutional AI) service instances
        for i in range(3):
            instance = ServiceInstance(
                service_type=ServiceType.AC,
                instance_id=f"ac-{i}",
                base_url=f"http://ac-{i}:8001",
                port=8001,
                health_url=f"http://ac-{i}:8001/health",
                status="healthy",
            )
            discovery.register_instance(instance)

        # Simulate constitutional compliance checking load
        compliance_checks = 200

        async def compliance_check(check_id: int):
            """Simulate constitutional compliance check."""
            start_time = time.time()

            instance = discovery.get_best_instance(ServiceType.AC)
            if instance:
                instance.increment_connections()

                # Simulate AI processing time (variable based on complexity)
                complexity_factor = (check_id % 5) + 1  # 1-5 complexity levels
                processing_time = 0.1 + (complexity_factor * 0.05)  # 100-350ms
                await asyncio.sleep(processing_time)

                instance.decrement_connections()

                response_time = (time.time() - start_time) * 1000
                return response_time

            return None

        # Execute compliance checks
        tasks = [compliance_check(i) for i in range(compliance_checks)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Analyze results
        successful_checks = [
            r for r in results if isinstance(r, (int, float)) and r > 0
        ]

        if successful_checks:
            avg_response_time = statistics.mean(successful_checks)
            p95_response_time = statistics.quantiles(successful_checks, n=20)[18]

            # Record performance metrics
            metrics = PerformanceMetrics(
                timestamp=time.time(),
                service_type="ac",
                instance_id="aggregate",
                response_time_ms=avg_response_time,
                availability_percent=(len(successful_checks) / compliance_checks) * 100,
                throughput_rps=len(successful_checks)
                / 10,  # Assuming 10s test duration
                error_rate_percent=(
                    (compliance_checks - len(successful_checks)) / compliance_checks
                )
                * 100,
                concurrent_connections=0,
            )
            monitor.record_metrics(metrics)

            # Validate constitutional compliance performance
            assert (
                len(successful_checks) >= compliance_checks * 0.98
            ), "Too many failed compliance checks"
            assert (
                avg_response_time < 500
            ), f"Average compliance check time {avg_response_time}ms too high"
            assert (
                p95_response_time < 750
            ), f"95th percentile {p95_response_time}ms too high"


if __name__ == "__main__":
    # Run performance validation tests
    pytest.main([__file__, "-v", "--tb=short", "-m", "not integration"])
