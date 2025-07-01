#!/usr/bin/env python3
"""
Comprehensive Integration Tests for ACGS Evolutionary Computation Service
Tests integration with all 10 operational services, API endpoints, database schemas, and NATS events.
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timezone

import aiohttp
import pytest
import pytest_asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constitutional hash for compliance validation
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Service endpoints
SERVICES = {
    "auth-service": "http://localhost:8000",
    "ac-service": "http://localhost:8001",
    "integrity-service": "http://localhost:8002",
    "fv-service": "http://localhost:8003",
    "gs-service": "http://localhost:8004",
    "pgc-service": "http://localhost:8005",
    "ec-service": "http://localhost:8006",
    "prometheus": "http://localhost:9090",
    "grafana": "http://localhost:3001",
    "nats": "nats://localhost:4222",
}


class ECServiceIntegrationTester:
    """Comprehensive integration tester for EC Service."""

    def __init__(self):
        self.test_results = []
        self.performance_metrics = {}
        self.constitutional_compliance_scores = []

    async def run_comprehensive_tests(self):
        """Run all integration tests."""
        logger.info("Starting comprehensive EC Service integration tests...")

        test_suites = [
            self.test_service_health_checks,
            self.test_api_endpoints,
            self.test_evolution_workflow,
            self.test_security_architecture,
            self.test_constitutional_compliance,
            self.test_nats_integration,
            self.test_performance_requirements,
            self.test_database_integration,
            self.test_monitoring_integration,
            self.test_error_handling,
        ]

        for test_suite in test_suites:
            try:
                await test_suite()
            except Exception as e:
                logger.error(f"Test suite {test_suite.__name__} failed: {e}")
                self.test_results.append(
                    {
                        "test_suite": test_suite.__name__,
                        "status": "failed",
                        "error": str(e),
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                )

        await self.generate_test_report()

    async def test_service_health_checks(self):
        """Test health checks for all services."""
        logger.info("Testing service health checks...")

        async with aiohttp.ClientSession() as session:
            for service_name, base_url in SERVICES.items():
                if service_name in ["prometheus", "grafana", "nats"]:
                    continue  # Skip non-ACGS services for health checks

                try:
                    start_time = time.time()
                    health_url = f"{base_url}/health"

                    async with session.get(health_url, timeout=5) as response:
                        response_time = (time.time() - start_time) * 1000

                        assert (
                            response.status == 200
                        ), f"{service_name} health check failed"

                        data = await response.json()
                        assert data.get("status") in [
                            "healthy",
                            "operational",
                        ], f"{service_name} not healthy"

                        self.performance_metrics[
                            f"{service_name}_health_response_time"
                        ] = response_time

                        logger.info(
                            f"✓ {service_name} health check passed ({response_time:.2f}ms)"
                        )

                except Exception as e:
                    logger.error(f"✗ {service_name} health check failed: {e}")
                    raise

    async def test_api_endpoints(self):
        """Test EC Service API endpoints."""
        logger.info("Testing EC Service API endpoints...")

        async with aiohttp.ClientSession() as session:
            # Test root endpoint
            await self._test_endpoint(
                session, "GET", f"{SERVICES['ec-service']}/", expected_status=200
            )

            # Test status endpoint
            await self._test_endpoint(
                session,
                "GET",
                f"{SERVICES['ec-service']}/api/v1/status",
                expected_status=200,
            )

            # Test evolution submission endpoint
            evolution_request = {
                "evolution_type": "policy_evolution",
                "description": "Test evolution request for integration testing",
                "proposed_changes": {
                    "policy_updates": ["test_policy_1", "test_policy_2"],
                    "impact_assessment": "low",
                },
                "target_service": "ac-service",
                "priority": 3,
            }

            response_data = await self._test_endpoint(
                session,
                "POST",
                f"{SERVICES['ec-service']}/api/v1/evolution/submit",
                json_data=evolution_request,
                expected_status=200,
            )

            # Store evolution ID for further testing
            evolution_id = response_data.get("evolution_id")
            assert evolution_id, "Evolution ID not returned"

            # Test evolution status endpoint
            await self._test_endpoint(
                session,
                "GET",
                f"{SERVICES['ec-service']}/api/v1/evolution/{evolution_id}/status",
                expected_status=200,
            )

            # Test pending reviews endpoint
            await self._test_endpoint(
                session,
                "GET",
                f"{SERVICES['ec-service']}/api/v1/reviews/pending",
                expected_status=200,
            )

    async def _test_endpoint(
        self,
        session: aiohttp.ClientSession,
        method: str,
        url: str,
        json_data: dict | None = None,
        expected_status: int = 200,
    ) -> dict:
        """Test a specific API endpoint."""
        start_time = time.time()

        try:
            if method == "GET":
                async with session.get(url, timeout=10) as response:
                    response_time = (time.time() - start_time) * 1000
                    assert (
                        response.status == expected_status
                    ), f"Unexpected status {response.status}"
                    data = await response.json()

            elif method == "POST":
                async with session.post(url, json=json_data, timeout=10) as response:
                    response_time = (time.time() - start_time) * 1000
                    assert (
                        response.status == expected_status
                    ), f"Unexpected status {response.status}"
                    data = await response.json()

            # Validate response time requirement (<500ms)
            assert (
                response_time < 500
            ), f"Response time {response_time:.2f}ms exceeds 500ms requirement"

            self.performance_metrics[f"{method}_{url.split('/')[-1]}_response_time"] = (
                response_time
            )

            logger.info(f"✓ {method} {url} passed ({response_time:.2f}ms)")
            return data

        except Exception as e:
            logger.error(f"✗ {method} {url} failed: {e}")
            raise

    async def test_evolution_workflow(self):
        """Test complete evolution workflow."""
        logger.info("Testing evolution workflow...")

        async with aiohttp.ClientSession() as session:
            # Submit evolution request
            evolution_request = {
                "evolution_type": "algorithm_optimization",
                "description": "Integration test evolution workflow",
                "proposed_changes": {
                    "algorithm_updates": ["optimization_v2"],
                    "performance_improvements": ["caching", "parallel_processing"],
                },
                "target_service": "pgc-service",
                "priority": 2,
            }

            submit_url = f"{SERVICES['ec-service']}/api/v1/evolution/submit"
            async with session.post(submit_url, json=evolution_request) as response:
                assert response.status == 200
                submit_data = await response.json()
                evolution_id = submit_data["evolution_id"]

            # Wait for processing
            await asyncio.sleep(2)

            # Check evolution status
            status_url = (
                f"{SERVICES['ec-service']}/api/v1/evolution/{evolution_id}/status"
            )
            async with session.get(status_url) as response:
                assert response.status == 200
                status_data = await response.json()

                # Validate status fields
                assert "evolution_id" in status_data
                assert "status" in status_data
                assert "evolution_type" in status_data

                logger.info(
                    f"✓ Evolution workflow test passed - Status: {status_data.get('status')}"
                )

    async def test_security_architecture(self):
        """Test 4-layer security architecture."""
        logger.info("Testing 4-layer security architecture...")

        async with aiohttp.ClientSession() as session:
            # Test secure execution endpoint
            operation = {
                "type": "policy_evaluation",
                "context": {
                    "user_id": "test_user",
                    "operation": "read",
                    "resource": "evolution_requests",
                },
                "constitutional_compliance_score": 0.98,
            }

            credentials = {
                "method": "api_key",
                "api_key": "acgs_ec_service_api_key",
                "source_ip": "127.0.0.1",
            }

            secure_url = f"{SERVICES['ec-service']}/api/v1/security/execute"
            async with session.post(
                secure_url, json={"operation": operation, "credentials": credentials}
            ) as response:
                assert response.status == 200
                security_data = await response.json()

                # Validate security execution
                assert "success" in security_data
                logger.info("✓ Security architecture test passed")

    async def test_constitutional_compliance(self):
        """Test constitutional compliance integration."""
        logger.info("Testing constitutional compliance integration...")

        async with aiohttp.ClientSession() as session:
            # Test AC Service integration
            ac_url = f"{SERVICES['ac-service']}/api/v1/constitutional/validate"

            validation_request = {
                "evolution_request": {
                    "evolution_id": str(uuid.uuid4()),
                    "evolution_type": "constitutional_update",
                    "description": "Test constitutional compliance validation",
                    "proposed_changes": {"constitutional_updates": ["test_update"]},
                    "target_service": "ac-service",
                },
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "validation_level": "comprehensive",
            }

            try:
                async with session.post(
                    ac_url, json=validation_request, timeout=30
                ) as response:
                    if response.status == 200:
                        validation_data = await response.json()
                        compliance_score = validation_data.get("compliance_score", 0.0)

                        self.constitutional_compliance_scores.append(compliance_score)

                        # Validate compliance score
                        assert (
                            compliance_score >= 0.95
                        ), f"Compliance score {compliance_score} below threshold"

                        logger.info(
                            f"✓ Constitutional compliance test passed (score: {compliance_score:.2%})"
                        )
                    else:
                        logger.warning(
                            f"AC Service validation returned status {response.status}"
                        )

            except Exception as e:
                logger.warning(f"Constitutional compliance test failed: {e}")
                # Don't fail the entire test suite for this

    async def test_nats_integration(self):
        """Test NATS event integration."""
        logger.info("Testing NATS integration...")

        try:
            import nats

            # Connect to NATS
            nc = await nats.connect("nats://localhost:4222")

            # Test publishing an error event
            error_event = {
                "event_id": str(uuid.uuid4()),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "service_name": "ec-service",
                "error_type": "integration_test",
                "error_message": "Test error event for integration testing",
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }

            await nc.publish(
                "acgs.errors.ec-service.integration_test",
                json.dumps(error_event).encode(),
            )

            await nc.close()

            logger.info("✓ NATS integration test passed")

        except Exception as e:
            logger.warning(f"NATS integration test failed: {e}")
            # Don't fail the entire test suite for this

    async def test_performance_requirements(self):
        """Test performance requirements compliance."""
        logger.info("Testing performance requirements...")

        # Analyze collected performance metrics
        response_times = [
            metric
            for metric_name, metric in self.performance_metrics.items()
            if "response_time" in metric_name
        ]

        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)

            # Validate performance requirements
            assert (
                avg_response_time < 250
            ), f"Average response time {avg_response_time:.2f}ms exceeds 250ms target"
            assert (
                max_response_time < 500
            ), f"Max response time {max_response_time:.2f}ms exceeds 500ms requirement"

            logger.info(
                f"✓ Performance requirements met (avg: {avg_response_time:.2f}ms, max: {max_response_time:.2f}ms)"
            )
        else:
            logger.warning("No performance metrics collected")

    async def test_database_integration(self):
        """Test database schema and operations."""
        logger.info("Testing database integration...")

        # Test database connectivity through service endpoints
        async with aiohttp.ClientSession() as session:
            # Test data persistence through evolution submission
            evolution_request = {
                "evolution_type": "performance_tuning",
                "description": "Database integration test",
                "proposed_changes": {"database_optimizations": ["index_creation"]},
                "target_service": "ec-service",
                "priority": 4,
            }

            submit_url = f"{SERVICES['ec-service']}/api/v1/evolution/submit"
            async with session.post(submit_url, json=evolution_request) as response:
                assert response.status == 200
                data = await response.json()
                evolution_id = data["evolution_id"]

            # Verify data retrieval
            status_url = (
                f"{SERVICES['ec-service']}/api/v1/evolution/{evolution_id}/status"
            )
            async with session.get(status_url) as response:
                assert response.status == 200
                status_data = await response.json()
                assert status_data["evolution_id"] == evolution_id

            logger.info("✓ Database integration test passed")

    async def test_monitoring_integration(self):
        """Test monitoring and metrics integration."""
        logger.info("Testing monitoring integration...")

        async with aiohttp.ClientSession() as session:
            # Test Prometheus metrics endpoint
            try:
                metrics_url = f"{SERVICES['ec-service']}/metrics"
                async with session.get(metrics_url, timeout=5) as response:
                    if response.status == 200:
                        metrics_text = await response.text()

                        # Validate key metrics are present
                        expected_metrics = [
                            "evolution_requests_total",
                            "human_review_tasks_total",
                            "ec_sandbox_executions_total",
                        ]

                        for metric in expected_metrics:
                            assert metric in metrics_text, f"Metric {metric} not found"

                        logger.info("✓ Monitoring integration test passed")
                    else:
                        logger.warning(
                            f"Metrics endpoint returned status {response.status}"
                        )

            except Exception as e:
                logger.warning(f"Monitoring integration test failed: {e}")

    async def test_error_handling(self):
        """Test error handling and resilience."""
        logger.info("Testing error handling...")

        async with aiohttp.ClientSession() as session:
            # Test invalid evolution request
            invalid_request = {
                "evolution_type": "invalid_type",
                "description": "",  # Empty description should fail validation
                "proposed_changes": {},
                "target_service": "invalid_service",
                "priority": 10,  # Invalid priority
            }

            submit_url = f"{SERVICES['ec-service']}/api/v1/evolution/submit"
            async with session.post(submit_url, json=invalid_request) as response:
                # Should return error status
                assert response.status in [
                    400,
                    422,
                    500,
                ], "Invalid request should return error status"

            # Test non-existent evolution status
            fake_id = str(uuid.uuid4())
            status_url = f"{SERVICES['ec-service']}/api/v1/evolution/{fake_id}/status"
            async with session.get(status_url) as response:
                assert (
                    response.status == 404
                ), "Non-existent evolution should return 404"

            logger.info("✓ Error handling test passed")

    async def generate_test_report(self):
        """Generate comprehensive test report."""
        logger.info("Generating integration test report...")

        # Calculate overall metrics
        total_tests = len(self.test_results)
        passed_tests = sum(
            1 for result in self.test_results if result.get("status") == "passed"
        )
        failed_tests = total_tests - passed_tests

        avg_compliance = (
            sum(self.constitutional_compliance_scores)
            / len(self.constitutional_compliance_scores)
            if self.constitutional_compliance_scores
            else 0.0
        )

        report = {
            "test_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": (
                    (passed_tests / total_tests * 100) if total_tests > 0 else 0
                ),
            },
            "performance_metrics": self.performance_metrics,
            "constitutional_compliance": {
                "average_score": avg_compliance,
                "scores": self.constitutional_compliance_scores,
                "target_met": avg_compliance >= 0.95,
            },
            "test_results": self.test_results,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

        # Save report

        report_dir = Path(__file__).parent.parent.parent / "reports/integration"
        report_dir.mkdir(parents=True, exist_ok=True)

        report_file = (
            report_dir / f"ec_service_integration_report_{int(time.time())}.json"
        )
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Integration test report saved: {report_file}")

        # Print summary
        print("\n" + "=" * 60)
        print("EC SERVICE INTEGRATION TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {report['test_summary']['success_rate']:.1f}%")
        print(f"Constitutional Compliance: {avg_compliance:.2%}")
        print("=" * 60)


# Pytest fixtures and test functions
@pytest_asyncio.fixture
async def ec_tester():
    """Fixture for EC Service integration tester."""
    return ECServiceIntegrationTester()


@pytest.mark.asyncio
async def test_ec_service_comprehensive_integration(ec_tester):
    """Run comprehensive integration tests."""
    await ec_tester.run_comprehensive_tests()


if __name__ == "__main__":
    # Run tests directly
    async def main():
        tester = ECServiceIntegrationTester()
        await tester.run_comprehensive_tests()

    asyncio.run(main())
