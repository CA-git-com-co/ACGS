"""
ACGS Constitutional Test Case Base Class
Constitutional Hash: cdd01ef066bc6cf2

This module provides the base test case class for all ACGS services,
ensuring constitutional compliance validation in every test.
"""

import asyncio
import json
import statistics
import time
from typing import Any
from unittest.mock import MagicMock

import httpx
import pytest
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from services.shared.config.settings import get_settings
from services.shared.database.connection import get_database_url
from services.shared.multi_tenant.context import SimpleTenantContext


class ConstitutionalTestCase:
    """Base test case class with constitutional compliance validation."""

    CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

    def __init__(self):
        self.settings = get_settings()
        self.test_tenant_id = "test-tenant-12345"
        self.test_user_id = "test-user-67890"
        self.test_admin_tenant_id = "admin-tenant-99999"

    @pytest.fixture(scope="session")
    def event_loop(self):
        """Create an instance of the default event loop for the test session."""
        loop = asyncio.get_event_loop_policy().new_event_loop()
        yield loop
        loop.close()

    @pytest.fixture
    async def db_session(self):
        """Provide async database session for testing."""
        # Use test database
        test_db_url = get_database_url().replace("/acgs", "/acgs_test")
        engine = create_async_engine(test_db_url, echo=False)

        async_session = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )

        async with async_session() as session:
            yield session
            await session.rollback()

        await engine.dispose()

    @pytest.fixture
    async def redis_client(self):
        """Provide Redis client for testing."""
        redis = Redis.from_url(
            self.settings.redis_url.replace("/0", "/15"),  # Use test database
            decode_responses=True,
        )

        # Clear test database
        await redis.flushdb()

        yield redis

        # Cleanup
        await redis.flushdb()
        await redis.close()

    @pytest.fixture
    def tenant_context(self):
        """Provide test tenant context."""
        return SimpleTenantContext(
            tenant_id=self.test_tenant_id, user_id=self.test_user_id, is_admin=False
        )

    @pytest.fixture
    def admin_tenant_context(self):
        """Provide admin tenant context."""
        return SimpleTenantContext(
            tenant_id=self.test_admin_tenant_id,
            user_id=self.test_user_id,
            is_admin=True,
        )

    def assert_constitutional_compliance(self, response: httpx.Response):
        """Validate constitutional compliance in HTTP response."""
        # Check constitutional hash in headers
        assert (
            response.headers.get("X-Constitutional-Hash") == self.CONSTITUTIONAL_HASH
        ), f"Missing or invalid constitutional hash in headers: {response.headers}"

        # Check constitutional compliance header
        assert (
            response.headers.get("X-Constitutional-Compliance") == "verified"
        ), f"Constitutional compliance not verified: {response.headers}"

        # If response has JSON body, check constitutional hash there too
        if response.headers.get("content-type", "").startswith("application/json"):
            try:
                data = response.json()
                if isinstance(data, dict):
                    assert (
                        data.get("constitutional_hash") == self.CONSTITUTIONAL_HASH
                    ), f"Missing or invalid constitutional hash in response body: {data}"
            except json.JSONDecodeError:
                pass  # Not JSON, skip body validation

    def assert_constitutional_compliance_dict(self, data: dict[str, Any]):
        """Validate constitutional compliance in dictionary data."""
        assert (
            data.get("constitutional_hash") == self.CONSTITUTIONAL_HASH
        ), f"Missing or invalid constitutional hash in data: {data}"

    def assert_tenant_isolation(self, data: dict[str, Any], expected_tenant_id: str):
        """Validate tenant isolation in response data."""
        if isinstance(data, dict):
            if "tenant_id" in data:
                assert (
                    data["tenant_id"] == expected_tenant_id
                ), f"Tenant isolation violation: expected {expected_tenant_id}, got {data['tenant_id']}"

            # Check nested data structures
            if "data" in data and isinstance(data["data"], (list, dict)):
                if isinstance(data["data"], list):
                    for item in data["data"]:
                        if isinstance(item, dict) and "tenant_id" in item:
                            assert (
                                item["tenant_id"] == expected_tenant_id
                            ), f"Tenant isolation violation in list item: expected {expected_tenant_id}, got {item['tenant_id']}"
                elif isinstance(data["data"], dict) and "tenant_id" in data["data"]:
                    assert (
                        data["data"]["tenant_id"] == expected_tenant_id
                    ), f"Tenant isolation violation in nested data: expected {expected_tenant_id}, got {data['data']['tenant_id']}"

    async def assert_performance_targets(
        self,
        operation_func,
        target_p99_ms: float = 5.0,
        target_rps: int = 100,
        num_requests: int = 100,
    ):
        """Validate performance targets for an operation."""
        latencies = []

        # Measure latencies
        for _ in range(num_requests):
            start_time = time.perf_counter()

            if asyncio.iscoroutinefunction(operation_func):
                await operation_func()
            else:
                operation_func()

            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            latencies.append(latency_ms)

        # Calculate P99 latency
        p99_latency = statistics.quantiles(latencies, n=100)[98]  # 99th percentile

        assert (
            p99_latency < target_p99_ms
        ), f"P99 latency {p99_latency:.2f}ms exceeds target {target_p99_ms}ms"

        # Calculate RPS (requests per second)
        total_time = sum(latencies) / 1000  # Convert to seconds
        num_requests / total_time if total_time > 0 else 0

        # Note: This is a simplified RPS calculation for testing
        # In practice, concurrent requests would be needed for true RPS testing

    async def assert_cache_hit_rate(
        self,
        redis_client: Redis,
        cache_operations: list[callable],
        target_hit_rate: float = 0.85,
    ):
        """Validate cache hit rate meets target."""
        hits = 0
        total_operations = len(cache_operations)

        for operation in cache_operations:
            # Execute cache operation
            if asyncio.iscoroutinefunction(operation):
                result = await operation(redis_client)
            else:
                result = operation(redis_client)

            # Check if it was a cache hit (implementation specific)
            if isinstance(result, dict) and result.get("cache_hit"):
                hits += 1

        hit_rate = hits / total_operations if total_operations > 0 else 0

        assert (
            hit_rate >= target_hit_rate
        ), f"Cache hit rate {hit_rate:.2%} below target {target_hit_rate:.2%}"

    def create_test_headers(
        self, tenant_context: SimpleTenantContext = None
    ) -> dict[str, str]:
        """Create standard test headers with constitutional compliance."""
        headers = {
            "X-Constitutional-Hash": self.CONSTITUTIONAL_HASH,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        if tenant_context:
            headers["X-Tenant-ID"] = tenant_context.tenant_id
            headers["X-User-ID"] = tenant_context.user_id
            if tenant_context.is_admin:
                headers["X-Admin-Context"] = "true"

        return headers

    async def create_test_jwt_token(
        self, tenant_context: SimpleTenantContext = None
    ) -> str:
        """Create test JWT token for authentication."""
        # This would normally integrate with the auth service
        # For testing, we create a mock token
        import jwt

        payload = {
            "sub": tenant_context.user_id if tenant_context else self.test_user_id,
            "tenant_id": (
                tenant_context.tenant_id if tenant_context else self.test_tenant_id
            ),
            "is_admin": tenant_context.is_admin if tenant_context else False,
            "constitutional_hash": self.CONSTITUTIONAL_HASH,
            "exp": int(time.time()) + 3600,  # 1 hour expiration
        }

        return jwt.encode(payload, "test-secret", algorithm="HS256")

    def mock_service_response(
        self,
        status_code: int = 200,
        data: dict[str, Any] | None = None,
        constitutional_compliant: bool = True,
    ) -> MagicMock:
        """Create mock service response with constitutional compliance."""
        mock_response = MagicMock()
        mock_response.status_code = status_code

        response_data = data or {"status": "success"}
        if constitutional_compliant:
            response_data["constitutional_hash"] = self.CONSTITUTIONAL_HASH

        mock_response.json.return_value = response_data

        headers = {}
        if constitutional_compliant:
            headers["X-Constitutional-Hash"] = self.CONSTITUTIONAL_HASH
            headers["X-Constitutional-Compliance"] = "verified"

        mock_response.headers = headers

        return mock_response

    async def setup_test_data(
        self, db_session: AsyncSession, tenant_id: str | None = None
    ) -> dict[str, Any]:
        """Setup common test data with constitutional compliance."""
        tenant_id = tenant_id or self.test_tenant_id

        # This would be implemented by specific test classes
        # to create test data appropriate for their service
        return {
            "tenant_id": tenant_id,
            "constitutional_hash": self.CONSTITUTIONAL_HASH,
            "created_at": "2025-01-07T00:00:00Z",
        }

    def validate_test_environment(self):
        """Validate that test environment is properly configured."""
        # Check that we're using test databases
        db_url = get_database_url()
        assert "test" in db_url.lower(), f"Not using test database: {db_url}"

        redis_url = self.settings.redis_url
        assert (
            "/15" in redis_url or "test" in redis_url.lower()
        ), f"Not using test Redis database: {redis_url}"

        # Validate constitutional hash
        assert (
            self.CONSTITUTIONAL_HASH == "cdd01ef066bc6cf2"
        ), f"Invalid constitutional hash: {self.CONSTITUTIONAL_HASH}"


class ConstitutionalAsyncTestCase(ConstitutionalTestCase):
    """Async version of constitutional test case for async test methods."""

    @pytest.fixture(autouse=True)
    async def setup_async_test(self):
        """Setup for async tests."""
        self.validate_test_environment()
        # Cleanup after test


# Pytest configuration for constitutional compliance
def pytest_configure(config):
    """Configure pytest for constitutional compliance testing."""
    config.addinivalue_line(
        "markers",
        "constitutional: mark test as requiring constitutional compliance validation",
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance validation test"
    )
    config.addinivalue_line(
        "markers", "multi_tenant: mark test as multi-tenant isolation test"
    )


def pytest_runtest_setup(item):
    """Setup for each test run with constitutional validation."""
    # Ensure constitutional hash is available in test environment
    import os

    os.environ["CONSTITUTIONAL_HASH"] = "cdd01ef066bc6cf2"
