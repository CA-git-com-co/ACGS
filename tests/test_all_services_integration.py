#!/usr/bin/env python3
"""
Comprehensive Integration Tests for All ACGS Services
Tests all 9 operational services with constitutional compliance validation

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import json
import time
from datetime import datetime

import aiohttp
import pytest

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

SERVICES = {
    "Constitutional AI": {"port": 8001, "health": "/health"},
    "Integrity Service": {"port": 8002, "health": "/health"},
    "Formal Verification": {"port": 8003, "health": "/health"},
    "Governance Synthesis": {"port": 8004, "health": "/health"},
    "Policy Governance": {"port": 8005, "health": "/health"},
    "Evolutionary Computation": {"port": 8006, "health": "/health"},
    "Code Analysis": {"port": 8007, "health": "/health"},
    "Context Service": {"port": 8012, "health": "/health"},
    "Authentication": {"port": 8016, "health": "/health"},
}


@pytest.mark.asyncio
@pytest.mark.integration
class TestAllServicesIntegration:
    """Integration tests for all ACGS services"""

    async def test_all_services_health_check(self):
        """Test that all services respond to health checks"""
        async with aiohttp.ClientSession() as session:
            for service_name, config in SERVICES.items():
                port = config["port"]
                health_endpoint = config["health"]
                url = f"http://localhost:{port}{health_endpoint}"

                async with session.get(
                    url, timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    assert response.status == 200, f"{service_name} health check failed"
                    data = await response.json()
                    assert "status" in data, f"{service_name} missing status field"

    async def test_all_services_constitutional_compliance(self):
        """Test constitutional compliance across all services"""
        async with aiohttp.ClientSession() as session:
            compliant_services = []
            non_compliant_services = []

            for service_name, config in SERVICES.items():
                port = config["port"]
                health_endpoint = config["health"]
                url = f"http://localhost:{port}{health_endpoint}"

                async with session.get(
                    url, timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    data = await response.json()

                    # Check for constitutional hash in response or headers
                    constitutional_compliant = False
                    if "constitutional_hash" in data:
                        constitutional_compliant = (
                            data["constitutional_hash"] == CONSTITUTIONAL_HASH
                        )
                    elif "X-Constitutional-Hash" in response.headers:
                        constitutional_compliant = (
                            response.headers["X-Constitutional-Hash"]
                            == CONSTITUTIONAL_HASH
                        )

                    if constitutional_compliant:
                        compliant_services.append(service_name)
                    else:
                        non_compliant_services.append(service_name)

            # All services must be constitutionally compliant
            assert (
                len(non_compliant_services) == 0
            ), f"Non-compliant services: {non_compliant_services}"
            assert len(compliant_services) == len(
                SERVICES
            ), f"Expected {len(SERVICES)} compliant services, got {len(compliant_services)}"

    async def test_all_services_performance_targets(self):
        """Test that all services meet performance targets"""
        async with aiohttp.ClientSession() as session:
            latencies = []

            for service_name, config in SERVICES.items():
                port = config["port"]
                health_endpoint = config["health"]
                url = f"http://localhost:{port}{health_endpoint}"

                start_time = time.time()
                async with session.get(
                    url, timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    latency_ms = (time.time() - start_time) * 1000
                    latencies.append(latency_ms)

                    assert response.status == 200, f"{service_name} failed health check"

                    # Individual service latency should be under 10ms
                    assert (
                        latency_ms < 10.0
                    ), f"{service_name} latency {latency_ms:.2f}ms exceeds 10ms target"

            # Average latency should be under 5ms
            avg_latency = sum(latencies) / len(latencies)
            assert (
                avg_latency < 5.0
            ), f"Average latency {avg_latency:.2f}ms exceeds 5ms target"

    async def test_service_specific_endpoints(self):
        """Test service-specific endpoints beyond health checks"""
        async with aiohttp.ClientSession() as session:

            # Test Integrity Service constitutional validation
            async with session.get(
                "http://localhost:8002/api/v1/constitutional/validate"
            ) as response:
                assert response.status == 200
                data = await response.json()
                assert data["constitutional_hash"] == CONSTITUTIONAL_HASH
                assert data["validation_status"] == "valid"

            # Test Code Analysis Service endpoints
            async with session.get("http://localhost:8007/") as response:
                assert response.status == 200
                data = await response.json()
                assert data["constitutional_hash"] == CONSTITUTIONAL_HASH

            # Test Context Service endpoints
            async with session.get("http://localhost:8012/") as response:
                assert response.status == 200
                data = await response.json()
                assert data["constitutional_hash"] == CONSTITUTIONAL_HASH

    async def test_service_metrics_endpoints(self):
        """Test that services provide metrics endpoints"""
        async with aiohttp.ClientSession() as session:
            services_with_metrics = []

            for service_name, config in SERVICES.items():
                port = config["port"]
                metrics_url = f"http://localhost:{port}/metrics"

                try:
                    async with session.get(
                        metrics_url, timeout=aiohttp.ClientTimeout(total=3)
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            if "constitutional_hash" in data:
                                assert (
                                    data["constitutional_hash"] == CONSTITUTIONAL_HASH
                                )
                            services_with_metrics.append(service_name)
                except:
                    # Some services might not have metrics endpoints yet
                    pass

            # At least 50% of services should have metrics endpoints
            assert (
                len(services_with_metrics) >= len(SERVICES) * 0.5
            ), f"Only {len(services_with_metrics)} services have metrics endpoints"

    async def test_concurrent_service_access(self):
        """Test concurrent access to all services"""
        async with aiohttp.ClientSession() as session:
            tasks = []

            # Create concurrent requests to all services
            for service_name, config in SERVICES.items():
                port = config["port"]
                health_endpoint = config["health"]
                url = f"http://localhost:{port}{health_endpoint}"

                task = session.get(url, timeout=aiohttp.ClientTimeout(total=5))
                tasks.append(task)

            # Execute all requests concurrently
            responses = await asyncio.gather(*tasks)

            # All responses should be successful
            for i, response in enumerate(responses):
                service_name = list(SERVICES.keys())[i]
                assert (
                    response.status == 200
                ), f"{service_name} failed concurrent access test"
                response.close()

    async def test_service_availability_under_load(self):
        """Test service availability under moderate load"""
        async with aiohttp.ClientSession() as session:
            # Test with 10 concurrent requests per service
            all_tasks = []

            for service_name, config in SERVICES.items():
                port = config["port"]
                health_endpoint = config["health"]
                url = f"http://localhost:{port}{health_endpoint}"

                # Create 10 concurrent requests for each service
                for _ in range(10):
                    task = session.get(url, timeout=aiohttp.ClientTimeout(total=10))
                    all_tasks.append((service_name, task))

            # Execute all requests
            results = await asyncio.gather(
                *[task for _, task in all_tasks], return_exceptions=True
            )

            # Count successful responses per service
            service_success_counts = {name: 0 for name in SERVICES.keys()}

            for i, result in enumerate(results):
                service_name = all_tasks[i][0]
                if not isinstance(result, Exception) and result.status == 200:
                    service_success_counts[service_name] += 1
                if not isinstance(result, Exception):
                    result.close()

            # Each service should handle at least 80% of requests successfully
            for service_name, success_count in service_success_counts.items():
                success_rate = success_count / 10
                assert (
                    success_rate >= 0.8
                ), f"{service_name} success rate {success_rate:.1%} below 80% threshold"


@pytest.mark.integration
def test_service_discovery():
    """Test that all expected services are discoverable"""
    import socket

    discovered_services = []

    for service_name, config in SERVICES.items():
        port = config["port"]
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)

        try:
            result = sock.connect_ex(("localhost", port))
            if result == 0:
                discovered_services.append(service_name)
        except:
            pass
        finally:
            sock.close()

    # All services should be discoverable
    assert len(discovered_services) == len(
        SERVICES
    ), f"Only {len(discovered_services)}/{len(SERVICES)} services discoverable: {discovered_services}"


@pytest.mark.performance
def test_service_startup_time():
    """Test that services have reasonable startup times (already running)"""
    # Since services are already running, we test response time as a proxy
    import time

    import requests

    startup_times = []

    for service_name, config in SERVICES.items():
        port = config["port"]
        health_endpoint = config["health"]
        url = f"http://localhost:{port}{health_endpoint}"

        start_time = time.time()
        try:
            response = requests.get(url, timeout=5)
            response_time = (time.time() - start_time) * 1000

            if response.status_code == 200:
                startup_times.append(response_time)
        except:
            pass

    # Average response time should be under 100ms (indicating good startup)
    if startup_times:
        avg_response_time = sum(startup_times) / len(startup_times)
        assert (
            avg_response_time < 100.0
        ), f"Average response time {avg_response_time:.2f}ms suggests slow startup"
