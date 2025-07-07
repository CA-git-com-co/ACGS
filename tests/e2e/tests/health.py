"""
ACGS Health Check Tests

Basic health and connectivity tests for all ACGS services to ensure
infrastructure is properly configured and services are responsive.
"""

# Constitutional Hash: cdd01ef066bc6cf2

import asyncio
import time
from typing import Any, Dict, List

from ..framework.base import BaseE2ETest, E2ETestResult
from ..framework.config import ServiceType


class HealthCheckTest(BaseE2ETest):
    """Basic health check test for all ACGS services."""

    test_type = "health"
    tags = ["smoke", "health", "basic"]

    async def run_test(self) -> List[E2ETestResult]:
        """Run health checks for all configured services."""
        results = []

        for service_type in ServiceType:
            if self.config.is_service_enabled(service_type):
                result = await self._test_service_health(service_type)
                results.append(result)

        return results

    async def _test_service_health(self, service_type: ServiceType) -> E2ETestResult:
        """Test health of a specific service."""
        start_time = time.perf_counter()

        try:
            # Check service health
            is_healthy = await self.check_service_health(service_type)

            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000

            if is_healthy:
                # Get additional health metrics
                response = await self.make_service_request(
                    service_type, "GET", "/health"
                )

                health_data = response.json() if response.status_code == 200 else {}

                # Validate constitutional hash if present
                constitutional_compliance = None
                if "constitutional_hash" in health_data:
                    constitutional_compliance = (
                        health_data["constitutional_hash"]
                        == self.config.constitutional_hash
                    )

                return E2ETestResult(
                    test_name=f"health_check_{service_type.value}",
                    success=True,
                    duration_ms=duration_ms,
                    constitutional_compliance=constitutional_compliance,
                    performance_metrics={
                        "response_time_ms": duration_ms,
                        "status_code": response.status_code,
                    },
                )
            else:
                return E2ETestResult(
                    test_name=f"health_check_{service_type.value}",
                    success=False,
                    duration_ms=duration_ms,
                    error_message=f"Service {service_type.value} is not healthy",
                )

        except Exception as e:
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000

            return E2ETestResult(
                test_name=f"health_check_{service_type.value}",
                success=False,
                duration_ms=duration_ms,
                error_message=f"Health check failed: {str(e)}",
            )


class ServiceConnectivityTest(BaseE2ETest):
    """Test inter-service connectivity and communication."""

    test_type = "connectivity"
    tags = ["smoke", "connectivity", "integration"]

    async def run_test(self) -> List[E2ETestResult]:
        """Test connectivity between services."""
        results = []

        # Test auth service connectivity
        if self.config.is_service_enabled(ServiceType.AUTH):
            result = await self._test_auth_connectivity()
            results.append(result)

        # Test constitutional AI service connectivity
        if self.config.is_service_enabled(ServiceType.CONSTITUTIONAL_AI):
            result = await self._test_constitutional_ai_connectivity()
            results.append(result)

        # Test policy governance service connectivity
        if self.config.is_service_enabled(ServiceType.POLICY_GOVERNANCE):
            result = await self._test_policy_governance_connectivity()
            results.append(result)

        return results

    async def _test_auth_connectivity(self) -> E2ETestResult:
        """Test authentication service connectivity."""
        start_time = time.perf_counter()

        try:
            # Test basic auth endpoint
            response = await self.make_service_request(
                ServiceType.AUTH, "GET", "/api/v1/auth/info"
            )

            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000

            success = response.status_code in [200, 401]  # 401 is expected without auth

            return E2ETestResult(
                test_name="connectivity_auth_service",
                success=success,
                duration_ms=duration_ms,
                performance_metrics={
                    "response_time_ms": duration_ms,
                    "status_code": response.status_code,
                },
            )

        except Exception as e:
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000

            return E2ETestResult(
                test_name="connectivity_auth_service",
                success=False,
                duration_ms=duration_ms,
                error_message=f"Auth connectivity failed: {str(e)}",
            )

    async def _test_constitutional_ai_connectivity(self) -> E2ETestResult:
        """Test Constitutional AI service connectivity."""
        start_time = time.perf_counter()

        try:
            # Test constitutional validation endpoint
            test_policy = {
                "policy_id": "test_connectivity_policy",
                "content": "Test policy for connectivity validation",
            }

            response = await self.make_service_request(
                ServiceType.CONSTITUTIONAL_AI,
                "POST",
                "/api/v1/constitutional/validate",
                json=test_policy,
            )

            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000

            success = response.status_code in [
                200,
                400,
                401,
            ]  # Various expected responses

            constitutional_compliance = None
            if response.status_code == 200:
                data = response.json()
                constitutional_compliance = data.get("constitutional_compliance", False)

            return E2ETestResult(
                test_name="connectivity_constitutional_ai_service",
                success=success,
                duration_ms=duration_ms,
                constitutional_compliance=constitutional_compliance,
                performance_metrics={
                    "response_time_ms": duration_ms,
                    "status_code": response.status_code,
                },
            )

        except Exception as e:
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000

            return E2ETestResult(
                test_name="connectivity_constitutional_ai_service",
                success=False,
                duration_ms=duration_ms,
                error_message=f"Constitutional AI connectivity failed: {str(e)}",
            )

    async def _test_policy_governance_connectivity(self) -> E2ETestResult:
        """Test Policy Governance service connectivity."""
        start_time = time.perf_counter()

        try:
            # Test governance metrics endpoint
            response = await self.make_service_request(
                ServiceType.POLICY_GOVERNANCE, "GET", "/api/v1/governance/metrics"
            )

            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000

            success = response.status_code in [200, 401]

            cache_hit_rate = None
            if response.status_code == 200:
                data = response.json()
                cache_hit_rate = data.get("cache_hit_rate", 0)

            return E2ETestResult(
                test_name="connectivity_policy_governance_service",
                success=success,
                duration_ms=duration_ms,
                performance_metrics={
                    "response_time_ms": duration_ms,
                    "status_code": response.status_code,
                    "cache_hit_rate": cache_hit_rate,
                },
            )

        except Exception as e:
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000

            return E2ETestResult(
                test_name="connectivity_policy_governance_service",
                success=False,
                duration_ms=duration_ms,
                error_message=f"Policy Governance connectivity failed: {str(e)}",
            )


class InfrastructureHealthTest(BaseE2ETest):
    """Test infrastructure component health (database, cache, etc.)."""

    test_type = "infrastructure"
    tags = ["smoke", "infrastructure", "database", "redis"]

    async def run_test(self) -> List[E2ETestResult]:
        """Test infrastructure component health."""
        results = []

        # Test database connectivity
        if self.config.test_mode != "offline":
            result = await self._test_database_health()
            results.append(result)

            # Test Redis connectivity
            result = await self._test_redis_health()
            results.append(result)

        return results

    async def _test_database_health(self) -> E2ETestResult:
        """Test database connectivity and basic operations."""
        start_time = time.perf_counter()

        try:
            if self.db_engine:
                async with self.db_engine.begin() as conn:
                    # Test basic query
                    result = await conn.execute("SELECT 1 as test_value")
                    row = result.fetchone()

                    success = row is not None and row[0] == 1
            else:
                success = False

            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000

            return E2ETestResult(
                test_name="infrastructure_database_health",
                success=success,
                duration_ms=duration_ms,
                performance_metrics={
                    "query_time_ms": duration_ms,
                    "connection_successful": success,
                },
            )

        except Exception as e:
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000

            return E2ETestResult(
                test_name="infrastructure_database_health",
                success=False,
                duration_ms=duration_ms,
                error_message=f"Database health check failed: {str(e)}",
            )

    async def _test_redis_health(self) -> E2ETestResult:
        """Test Redis connectivity and basic operations."""
        start_time = time.perf_counter()

        try:
            if self.redis_client:
                # Test ping
                pong = await self.redis_client.ping()

                # Test set/get
                test_key = "acgs_e2e_test_key"
                test_value = "test_value"

                await self.redis_client.set(test_key, test_value, ex=60)
                retrieved_value = await self.redis_client.get(test_key)

                success = pong and retrieved_value == test_value

                # Cleanup
                await self.redis_client.delete(test_key)
            else:
                success = False

            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000

            return E2ETestResult(
                test_name="infrastructure_redis_health",
                success=success,
                duration_ms=duration_ms,
                performance_metrics={
                    "operation_time_ms": duration_ms,
                    "ping_successful": success,
                },
            )

        except Exception as e:
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000

            return E2ETestResult(
                test_name="infrastructure_redis_health",
                success=False,
                duration_ms=duration_ms,
                error_message=f"Redis health check failed: {str(e)}",
            )
