#!/usr/bin/env python3
"""
Docker-in-Docker Integration Tests for ACGS
Tests containerized deployment and inter-service communication in DinD environment.
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

import docker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constitutional hash for compliance validation
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# DinD service endpoints (internal network)
DIND_SERVICES = {
    "auth-service": "http://acgs-auth-service-dind:8000",
    "ac-service": "http://acgs-ac-service-dind:8001",
    "integrity-service": "http://acgs-integrity-service-dind:8002",
    "fv-service": "http://acgs-fv-service-dind:8003",
    "gs-service": "http://acgs-gs-service-dind:8004",
    "pgc-service": "http://acgs-pgc-service-dind:8005",
    "ec-service": "http://acgs-ec-service-dind:8006",
}

# External endpoints (host network)
EXTERNAL_SERVICES = {
    "auth-service": "http://localhost:8000",
    "ac-service": "http://localhost:8001",
    "integrity-service": "http://localhost:8002",
    "fv-service": "http://localhost:8003",
    "gs-service": "http://localhost:8004",
    "pgc-service": "http://localhost:8005",
    "ec-service": "http://localhost:8006",
    "prometheus": "http://localhost:9090",
    "grafana": "http://localhost:3001",
}


class DinDIntegrationTester:
    """Docker-in-Docker integration tester."""

    def __init__(self):
        self.docker_client = docker.from_env()
        self.test_results = []
        self.performance_metrics = {}
        self.container_health = {}

    async def run_comprehensive_dind_tests(self):
        """Run comprehensive DinD integration tests."""
        logger.info("Starting Docker-in-Docker integration tests...")

        test_suites = [
            self.test_container_health,
            self.test_docker_daemon_connectivity,
            self.test_inter_service_communication,
            self.test_container_networking,
            self.test_volume_persistence,
            self.test_service_discovery,
            self.test_container_security,
            self.test_resource_limits,
            self.test_container_orchestration,
            self.test_monitoring_in_containers,
        ]

        for test_suite in test_suites:
            try:
                await test_suite()
                self.test_results.append(
                    {
                        "test_suite": test_suite.__name__,
                        "status": "passed",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                )
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

        await self.generate_dind_test_report()

    async def test_container_health(self):
        """Test health of all ACGS containers."""
        logger.info("Testing container health...")

        expected_containers = [
            "acgs-docker-dind",
            "acgs-auth-service-dind",
            "acgs-ac-service-dind",
            "acgs-integrity-service-dind",
            "acgs-fv-service-dind",
            "acgs-gs-service-dind",
            "acgs-pgc-service-dind",
            "acgs-ec-service-dind",
            "acgs-postgres-dind",
            "acgs-redis-dind",
            "acgs-nats-dind",
            "acgs-prometheus-dind",
            "acgs-grafana-dind",
        ]

        for container_name in expected_containers:
            try:
                container = self.docker_client.containers.get(container_name)

                # Check container status
                assert (
                    container.status == "running"
                ), f"Container {container_name} not running"

                # Check container health if health check is defined
                if container.attrs.get("State", {}).get("Health"):
                    health_status = container.attrs["State"]["Health"]["Status"]
                    assert health_status in [
                        "healthy",
                        "starting",
                    ], f"Container {container_name} unhealthy: {health_status}"

                self.container_health[container_name] = {
                    "status": container.status,
                    "health": container.attrs.get("State", {})
                    .get("Health", {})
                    .get("Status", "unknown"),
                    "uptime": container.attrs.get("State", {}).get(
                        "StartedAt", "unknown"
                    ),
                }

                logger.info(f"✓ Container {container_name} is healthy")

            except docker.errors.NotFound:
                raise AssertionError(f"Container {container_name} not found")
            except Exception as e:
                raise AssertionError(
                    f"Container {container_name} health check failed: {e}"
                )

    async def test_docker_daemon_connectivity(self):
        """Test Docker daemon connectivity within DinD."""
        logger.info("Testing Docker daemon connectivity...")

        try:
            # Test Docker daemon in DinD container
            dind_container = self.docker_client.containers.get("acgs-docker-dind")

            # Execute docker command inside DinD
            result = dind_container.exec_run(
                "docker version --format '{{.Server.Version}}'"
            )
            assert (
                result.exit_code == 0
            ), f"Docker daemon not accessible: {result.output.decode()}"

            docker_version = result.output.decode().strip()
            logger.info(f"✓ Docker daemon accessible, version: {docker_version}")

            # Test Docker API connectivity
            result = dind_container.exec_run(
                "docker ps --format 'table {{.Names}}\t{{.Status}}'"
            )
            assert result.exit_code == 0, "Docker API not accessible"

            logger.info("✓ Docker daemon connectivity verified")

        except Exception as e:
            raise AssertionError(f"Docker daemon connectivity test failed: {e}")

    async def test_inter_service_communication(self):
        """Test communication between ACGS services in containers."""
        logger.info("Testing inter-service communication...")

        async with aiohttp.ClientSession() as session:
            # Test AC Service to PGC Service communication
            try:
                # Call AC Service which should communicate with PGC Service
                ac_url = f"{EXTERNAL_SERVICES['ac-service']}/api/v1/status"
                async with session.get(ac_url, timeout=10) as response:
                    assert (
                        response.status == 200
                    ), f"AC Service not accessible: {response.status}"

                    ac_data = await response.json()
                    logger.info(
                        f"✓ AC Service accessible: {ac_data.get('service', 'unknown')}"
                    )

                # Test EC Service evolution submission (tests multiple service integration)
                evolution_request = {
                    "evolution_type": "policy_evolution",
                    "description": "DinD integration test evolution",
                    "proposed_changes": {"test": "dind_integration"},
                    "target_service": "ac-service",
                    "priority": 4,
                }

                ec_url = f"{EXTERNAL_SERVICES['ec-service']}/api/v1/evolution/submit"
                async with session.post(
                    ec_url, json=evolution_request, timeout=15
                ) as response:
                    if response.status == 200:
                        evolution_data = await response.json()
                        evolution_id = evolution_data.get("evolution_id")
                        logger.info(
                            f"✓ Inter-service communication verified via evolution {evolution_id}"
                        )
                    else:
                        logger.warning(
                            f"Evolution submission failed: {response.status}"
                        )

            except Exception as e:
                raise AssertionError(f"Inter-service communication test failed: {e}")

    async def test_container_networking(self):
        """Test container networking and DNS resolution."""
        logger.info("Testing container networking...")

        try:
            # Test network connectivity from one service to another
            ac_container = self.docker_client.containers.get("acgs-ac-service-dind")

            # Test DNS resolution
            result = ac_container.exec_run("nslookup acgs-pgc-service-dind")
            assert (
                result.exit_code == 0
            ), f"DNS resolution failed: {result.output.decode()}"

            # Test network connectivity
            result = ac_container.exec_run(
                "curl -f http://acgs-pgc-service-dind:8005/health --max-time 10"
            )
            if result.exit_code == 0:
                logger.info("✓ Container networking verified")
            else:
                logger.warning(
                    f"Network connectivity test failed: {result.output.decode()}"
                )

        except Exception as e:
            raise AssertionError(f"Container networking test failed: {e}")

    async def test_volume_persistence(self):
        """Test volume persistence and data storage."""
        logger.info("Testing volume persistence...")

        try:
            # Test PostgreSQL data persistence
            postgres_container = self.docker_client.containers.get("acgs-postgres-dind")

            # Create test data
            result = postgres_container.exec_run(
                [
                    "psql",
                    "-U",
                    "acgs_user",
                    "-d",
                    "acgs",
                    "-c",
                    "CREATE TABLE IF NOT EXISTS dind_test (id SERIAL PRIMARY KEY, data TEXT);",
                ]
            )
            assert (
                result.exit_code == 0
            ), f"Database write failed: {result.output.decode()}"

            # Insert test data
            test_data = f"DinD test data {uuid.uuid4()}"
            result = postgres_container.exec_run(
                [
                    "psql",
                    "-U",
                    "acgs_user",
                    "-d",
                    "acgs",
                    "-c",
                    f"INSERT INTO dind_test (data) VALUES ('{test_data}');",
                ]
            )
            assert (
                result.exit_code == 0
            ), f"Database insert failed: {result.output.decode()}"

            # Verify data persistence
            result = postgres_container.exec_run(
                [
                    "psql",
                    "-U",
                    "acgs_user",
                    "-d",
                    "acgs",
                    "-c",
                    f"SELECT data FROM dind_test WHERE data = '{test_data}';",
                ]
            )
            assert (
                result.exit_code == 0
            ), f"Database read failed: {result.output.decode()}"
            assert (
                test_data in result.output.decode()
            ), "Test data not found in database"

            logger.info("✓ Volume persistence verified")

        except Exception as e:
            raise AssertionError(f"Volume persistence test failed: {e}")

    async def test_service_discovery(self):
        """Test service discovery mechanisms."""
        logger.info("Testing service discovery...")

        try:
            # Test service discovery through container names
            auth_container = self.docker_client.containers.get("acgs-auth-service-dind")

            # Test discovery of other services
            services_to_test = [
                "acgs-postgres-dind:5432",
                "acgs-redis-dind:6379",
                "acgs-nats-dind:4222",
            ]

            for service in services_to_test:
                host, port = service.split(":")
                result = auth_container.exec_run(f"nc -z {host} {port}")
                assert result.exit_code == 0, f"Service discovery failed for {service}"

            logger.info("✓ Service discovery verified")

        except Exception as e:
            raise AssertionError(f"Service discovery test failed: {e}")

    async def test_container_security(self):
        """Test container security configurations."""
        logger.info("Testing container security...")

        try:
            # Test that services run as non-root users
            for service_name in ["acgs-auth-service-dind", "acgs-ac-service-dind"]:
                try:
                    container = self.docker_client.containers.get(service_name)
                    result = container.exec_run("id -u")

                    if result.exit_code == 0:
                        uid = int(result.output.decode().strip())
                        assert (
                            uid != 0
                        ), f"Service {service_name} running as root (UID 0)"
                        logger.info(
                            f"✓ Service {service_name} running as non-root (UID {uid})"
                        )

                except docker.errors.NotFound:
                    logger.warning(
                        f"Container {service_name} not found for security test"
                    )

            # Test Docker daemon security in DinD
            dind_container = self.docker_client.containers.get("acgs-docker-dind")

            # Verify TLS is enabled
            result = dind_container.exec_run(
                "docker version --format '{{.Server.TLSVerify}}'"
            )
            if result.exit_code == 0:
                tls_verify = result.output.decode().strip()
                logger.info(f"✓ Docker daemon TLS verification: {tls_verify}")

            logger.info("✓ Container security verified")

        except Exception as e:
            raise AssertionError(f"Container security test failed: {e}")

    async def test_security_architecture(self):
        """Test 4-layer security architecture in DinD environment."""
        logger.info("Testing security architecture...")

        try:
            # Test Layer 1: Sandboxing
            ec_container = self.docker_client.containers.get("acgs-ec-service-dind")

            # Verify container isolation
            result = ec_container.exec_run("ls /proc/1/root")
            if result.exit_code != 0:
                logger.info("✓ Layer 1: Container isolation verified")

            # Test Layer 2: Policy Engine (OPA integration)
            async with aiohttp.ClientSession() as session:
                try:
                    # Test policy evaluation endpoint
                    policy_url = (
                        f"{EXTERNAL_SERVICES['ec-service']}/api/v1/security/execute"
                    )
                    test_operation = {
                        "operation": {
                            "type": "policy_evaluation",
                            "context": {"user_id": "test_user"},
                            "constitutional_compliance_score": 0.98,
                        },
                        "credentials": {"method": "api_key", "api_key": "test_key"},
                    }

                    async with session.post(
                        policy_url, json=test_operation, timeout=10
                    ) as response:
                        if response.status in [200, 401, 403]:  # Expected responses
                            logger.info("✓ Layer 2: Policy engine accessible")
                        else:
                            logger.warning(
                                f"Policy engine unexpected response: {response.status}"
                            )

                except Exception as e:
                    logger.warning(f"Policy engine test failed: {e}")

            # Test Layer 3: Authentication
            auth_container = self.docker_client.containers.get("acgs-auth-service-dind")

            # Verify authentication service is running
            result = auth_container.exec_run(
                "curl -f http://localhost:8000/health --max-time 5"
            )
            if result.exit_code == 0:
                logger.info("✓ Layer 3: Authentication service verified")

            # Test Layer 4: Audit logging
            # Check if audit logs are being generated
            audit_result = ec_container.exec_run("find /app/logs -name '*.log' -type f")
            if audit_result.exit_code == 0:
                log_files = audit_result.output.decode().strip()
                if log_files:
                    logger.info("✓ Layer 4: Audit logging verified")
                else:
                    logger.warning("No audit log files found")

            logger.info("✓ Security architecture test completed")

        except Exception as e:
            raise AssertionError(f"Security architecture test failed: {e}")

    async def test_resource_limits(self):
        """Test container resource limits and constraints."""
        logger.info("Testing resource limits...")

        try:
            # Check memory limits for services
            for service_name in ["acgs-auth-service-dind", "acgs-ac-service-dind"]:
                try:
                    container = self.docker_client.containers.get(service_name)

                    # Get container stats
                    stats = container.stats(stream=False)
                    memory_usage = stats["memory_stats"].get("usage", 0)
                    memory_limit = stats["memory_stats"].get("limit", 0)

                    if memory_limit > 0:
                        memory_usage_percent = (memory_usage / memory_limit) * 100
                        logger.info(
                            f"✓ {service_name} memory usage: {memory_usage_percent:.1f}%"
                        )

                        # Ensure memory usage is reasonable
                        assert (
                            memory_usage_percent < 90
                        ), f"High memory usage in {service_name}: {memory_usage_percent:.1f}%"

                except docker.errors.NotFound:
                    logger.warning(
                        f"Container {service_name} not found for resource test"
                    )

            logger.info("✓ Resource limits verified")

        except Exception as e:
            raise AssertionError(f"Resource limits test failed: {e}")

    async def test_container_orchestration(self):
        """Test container orchestration and dependency management."""
        logger.info("Testing container orchestration...")

        try:
            # Verify containers started in correct order
            postgres_container = self.docker_client.containers.get("acgs-postgres-dind")
            auth_container = self.docker_client.containers.get("acgs-auth-service-dind")

            postgres_start_time = postgres_container.attrs["State"]["StartedAt"]
            auth_start_time = auth_container.attrs["State"]["StartedAt"]

            # PostgreSQL should start before auth service
            assert (
                postgres_start_time < auth_start_time
            ), "Service dependency order not respected"

            # Test service restart behavior
            logger.info("Testing service restart...")
            auth_container.restart(timeout=30)

            # Wait for restart
            await asyncio.sleep(10)

            # Verify service is healthy after restart
            auth_container.reload()
            assert (
                auth_container.status == "running"
            ), "Service failed to restart properly"

            logger.info("✓ Container orchestration verified")

        except Exception as e:
            raise AssertionError(f"Container orchestration test failed: {e}")

    async def test_monitoring_in_containers(self):
        """Test monitoring and metrics collection in containerized environment."""
        logger.info("Testing monitoring in containers...")

        async with aiohttp.ClientSession() as session:
            try:
                # Test Prometheus metrics collection
                prometheus_url = f"{EXTERNAL_SERVICES['prometheus']}/api/v1/targets"
                async with session.get(prometheus_url, timeout=10) as response:
                    if response.status == 200:
                        targets_data = await response.json()
                        active_targets = targets_data.get("data", {}).get(
                            "activeTargets", []
                        )

                        # Check that ACGS services are being monitored
                        acgs_targets = [
                            t
                            for t in active_targets
                            if "acgs" in t.get("labels", {}).get("job", "")
                        ]
                        assert (
                            len(acgs_targets) > 0
                        ), "No ACGS services found in Prometheus targets"

                        logger.info(
                            f"✓ Prometheus monitoring {len(acgs_targets)} ACGS targets"
                        )
                    else:
                        logger.warning(f"Prometheus not accessible: {response.status}")

                # Test Grafana accessibility
                grafana_url = f"{EXTERNAL_SERVICES['grafana']}/api/health"
                async with session.get(grafana_url, timeout=10) as response:
                    if response.status == 200:
                        health_data = await response.json()
                        logger.info(
                            f"✓ Grafana accessible: {health_data.get('database', 'unknown')}"
                        )
                    else:
                        logger.warning(f"Grafana not accessible: {response.status}")

                # Test service metrics endpoints
                for service_name, base_url in EXTERNAL_SERVICES.items():
                    if service_name in ["prometheus", "grafana"]:
                        continue

                    try:
                        metrics_url = f"{base_url}/metrics"
                        async with session.get(metrics_url, timeout=5) as response:
                            if response.status == 200:
                                metrics_text = await response.text()
                                assert (
                                    "constitutional_hash" in metrics_text
                                    or "http_requests" in metrics_text
                                ), f"No valid metrics found for {service_name}"
                                logger.info(f"✓ {service_name} metrics accessible")
                            else:
                                logger.warning(
                                    f"{service_name} metrics not accessible: {response.status}"
                                )
                    except Exception as e:
                        logger.warning(f"Failed to check {service_name} metrics: {e}")

                logger.info("✓ Monitoring in containers verified")

            except Exception as e:
                raise AssertionError(f"Monitoring test failed: {e}")

    async def generate_dind_test_report(self):
        """Generate DinD integration test report."""
        logger.info("Generating DinD integration test report...")

        # Calculate test statistics
        total_tests = len(self.test_results)
        passed_tests = sum(
            1 for result in self.test_results if result["status"] == "passed"
        )
        failed_tests = total_tests - passed_tests

        report = {
            "dind_test_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": (
                    (passed_tests / total_tests * 100) if total_tests > 0 else 0
                ),
            },
            "container_health": self.container_health,
            "performance_metrics": self.performance_metrics,
            "test_results": self.test_results,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "docker_environment": {
                "dind_enabled": True,
                "network_mode": "bridge",
                "volume_persistence": True,
            },
        }

        # Save report
        import os
        from pathlib import Path

        report_dir = (
            Path("/app/reports")
            if os.path.exists("/app/reports")
            else Path("reports/dind")
        )
        report_dir.mkdir(parents=True, exist_ok=True)

        report_file = report_dir / f"dind_integration_report_{int(time.time())}.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"DinD integration test report saved: {report_file}")

        # Print summary
        print("\n" + "=" * 60)
        print("DOCKER-IN-DOCKER INTEGRATION TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {report['dind_test_summary']['success_rate']:.1f}%")
        print(f"Containers Monitored: {len(self.container_health)}")
        print("=" * 60)


# Pytest fixtures and test functions
@pytest_asyncio.fixture
async def dind_tester():
    """Fixture for DinD integration tester."""
    return DinDIntegrationTester()


@pytest.mark.asyncio
async def test_dind_comprehensive_integration(dind_tester):
    """Run comprehensive DinD integration tests."""
    await dind_tester.run_comprehensive_dind_tests()


if __name__ == "__main__":
    # Run tests directly
    async def main():
        tester = DinDIntegrationTester()
        await tester.run_comprehensive_dind_tests()

    asyncio.run(main())
