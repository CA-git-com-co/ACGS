"""
Base E2E Test Classes

Provides base classes and utilities for ACGS end-to-end testing with
standardized setup, teardown, and assertion patterns.
"""

import asyncio
import time
import uuid
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional, Union, AsyncGenerator
from dataclasses import dataclass
from datetime import datetime, timedelta

import pytest
import httpx
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from redis.asyncio import Redis

from .config import E2ETestConfig, E2ETestMode, ServiceType


@dataclass
class E2ETestResult:
    """Test execution result."""
    test_name: str
    success: bool
    duration_ms: float
    error_message: Optional[str] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    constitutional_compliance: Optional[bool] = None


@dataclass
class PerformanceMetrics:
    """Performance measurement results."""
    latency_p50_ms: float
    latency_p95_ms: float
    latency_p99_ms: float
    throughput_rps: float
    success_rate: float
    cache_hit_rate: Optional[float] = None
    resource_utilization: Optional[float] = None


class BaseE2ETest(ABC):
    """Base class for all ACGS E2E tests."""
    
    def __init__(self, config: E2ETestConfig):
        self.config = config
        self.test_id = str(uuid.uuid4())
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.results: List[E2ETestResult] = []
        
        # HTTP client for service communication
        self.http_client: httpx.AsyncClient
        
        # Database and cache connections
        self.db_engine = None
        self.redis_client: Optional[Redis] = None
    
    async def setup(self):
        """Setup test environment."""
        self.start_time = datetime.utcnow()
        
        # Initialize HTTP client
        self.http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20)
        )
        
        # Setup database connection if needed
        if self.config.test_mode in [E2ETestMode.ONLINE, E2ETestMode.HYBRID]:
            await self._setup_database()
            await self._setup_redis()
        
        # Custom setup
        await self.custom_setup()
    
    async def teardown(self):
        """Cleanup test environment."""
        self.end_time = datetime.utcnow()
        
        # Custom teardown
        await self.custom_teardown()
        
        # Cleanup connections
        if self.http_client:
            await self.http_client.aclose()
        
        if self.db_engine:
            await self.db_engine.dispose()
        
        if self.redis_client:
            await self.redis_client.aclose()
    
    async def custom_setup(self):
        """Custom setup logic for specific test types."""
        pass
    
    async def custom_teardown(self):
        """Custom teardown logic for specific test types."""
        pass
    
    async def _setup_database(self):
        """Setup database connection."""
        if self.config.test_mode == E2ETestMode.OFFLINE:
            return
        
        database_url = self.config.get_test_database_url()
        self.db_engine = create_async_engine(
            database_url,
            echo=self.config.debug_mode,
            pool_size=5,
            max_overflow=10
        )
    
    async def _setup_redis(self):
        """Setup Redis connection."""
        if self.config.test_mode == E2ETestMode.OFFLINE:
            return
        
        self.redis_client = Redis.from_url(
            self.config.infrastructure.redis_url,
            decode_responses=True,
            socket_timeout=5.0,
            socket_connect_timeout=5.0
        )
    
    @asynccontextmanager
    async def measure_performance(self, operation_name: str) -> AsyncGenerator[PerformanceMetrics, None]:
        """Context manager for measuring operation performance."""
        start_time = time.perf_counter()
        metrics = PerformanceMetrics(0, 0, 0, 0, 0)
        
        try:
            yield metrics
        finally:
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            
            # Update metrics with actual measurements
            metrics.latency_p50_ms = duration_ms
            metrics.latency_p95_ms = duration_ms
            metrics.latency_p99_ms = duration_ms
    
    async def check_service_health(self, service_type: ServiceType) -> bool:
        """Check if a service is healthy."""
        if not self.config.is_service_enabled(service_type):
            return False
        
        service = self.config.services[service_type]
        
        try:
            response = await self.http_client.get(
                service.health_url,
                timeout=5.0
            )
            return response.status_code == 200
        except Exception:
            return False
    
    async def wait_for_service(self, service_type: ServiceType, timeout_seconds: int = 30) -> bool:
        """Wait for a service to become healthy."""
        start_time = time.time()
        
        while time.time() - start_time < timeout_seconds:
            if await self.check_service_health(service_type):
                return True
            await asyncio.sleep(1.0)
        
        return False
    
    async def make_service_request(
        self,
        service_type: ServiceType,
        method: str,
        path: str,
        **kwargs
    ) -> httpx.Response:
        """Make HTTP request to a service."""
        service_url = self.config.get_service_url(service_type)
        url = f"{service_url}{path}"
        
        response = await self.http_client.request(method, url, **kwargs)
        return response
    
    def assert_constitutional_compliance(self, response_data: Dict[str, Any]):
        """Assert constitutional compliance in response."""
        if "constitutional_hash" in response_data:
            assert response_data["constitutional_hash"] == self.config.constitutional_hash
        
        if "constitutional_compliance" in response_data:
            assert response_data["constitutional_compliance"] is True
    
    def assert_performance_targets(self, metrics: PerformanceMetrics):
        """Assert performance targets are met."""
        targets = self.config.performance
        
        assert metrics.latency_p99_ms <= targets.p99_latency_ms, (
            f"P99 latency {metrics.latency_p99_ms}ms exceeds target {targets.p99_latency_ms}ms"
        )
        
        assert metrics.success_rate >= targets.success_rate, (
            f"Success rate {metrics.success_rate} below target {targets.success_rate}"
        )
        
        if metrics.cache_hit_rate is not None:
            assert metrics.cache_hit_rate >= targets.cache_hit_rate, (
                f"Cache hit rate {metrics.cache_hit_rate} below target {targets.cache_hit_rate}"
            )
        
        if metrics.throughput_rps > 0:
            assert metrics.throughput_rps >= targets.throughput_rps, (
                f"Throughput {metrics.throughput_rps} RPS below target {targets.throughput_rps} RPS"
            )
    
    def record_test_result(self, result: E2ETestResult):
        """Record a test result."""
        self.results.append(result)
    
    @abstractmethod
    async def run_test(self) -> List[E2ETestResult]:
        """Run the actual test logic."""
        pass
    
    async def execute(self) -> List[E2ETestResult]:
        """Execute the complete test with setup and teardown."""
        try:
            await self.setup()
            results = await self.run_test()
            return results
        finally:
            await self.teardown()


class ConstitutionalComplianceTest(BaseE2ETest):
    """Base class for constitutional compliance testing."""
    
    async def validate_constitutional_response(self, response: httpx.Response) -> bool:
        """Validate constitutional compliance in API response."""
        if response.status_code != 200:
            return False
        
        try:
            data = response.json()
            self.assert_constitutional_compliance(data)
            return True
        except Exception:
            return False


class PerformanceTest(BaseE2ETest):
    """Base class for performance testing."""
    
    def __init__(self, config: E2ETestConfig, load_duration_seconds: int = 60):
        super().__init__(config)
        self.load_duration_seconds = load_duration_seconds
        self.concurrent_requests = 10
    
    async def run_load_test(
        self,
        target_function,
        concurrent_requests: Optional[int] = None
    ) -> PerformanceMetrics:
        """Run load test against target function."""
        concurrent = concurrent_requests or self.concurrent_requests
        
        start_time = time.time()
        end_time = start_time + self.load_duration_seconds
        
        latencies = []
        successes = 0
        total_requests = 0
        
        async def worker():
            nonlocal successes, total_requests
            
            while time.time() < end_time:
                request_start = time.perf_counter()
                try:
                    await target_function()
                    successes += 1
                except Exception:
                    pass
                finally:
                    request_end = time.perf_counter()
                    latencies.append((request_end - request_start) * 1000)
                    total_requests += 1
                
                # Small delay to prevent overwhelming
                await asyncio.sleep(0.01)
        
        # Run concurrent workers
        tasks = [worker() for _ in range(concurrent)]
        await asyncio.gather(*tasks)
        
        # Calculate metrics
        latencies.sort()
        n = len(latencies)
        
        if n == 0:
            return PerformanceMetrics(0, 0, 0, 0, 0)
        
        p50_idx = int(n * 0.5)
        p95_idx = int(n * 0.95)
        p99_idx = int(n * 0.99)
        
        duration = time.time() - start_time
        throughput = total_requests / duration if duration > 0 else 0
        success_rate = successes / total_requests if total_requests > 0 else 0
        
        return PerformanceMetrics(
            latency_p50_ms=latencies[p50_idx],
            latency_p95_ms=latencies[p95_idx],
            latency_p99_ms=latencies[p99_idx],
            throughput_rps=throughput,
            success_rate=success_rate
        )


class SecurityTest(BaseE2ETest):
    """Base class for security testing."""

    async def test_authentication_required(self, endpoint: str) -> bool:
        """Test that endpoint requires authentication."""
        response = await self.http_client.get(endpoint)
        return response.status_code in [401, 403]

    async def test_input_validation(self, endpoint: str, invalid_payload: Dict[str, Any]) -> bool:
        """Test input validation with invalid payload."""
        response = await self.http_client.post(endpoint, json=invalid_payload)
        return response.status_code in [400, 422]

    async def test_sql_injection_protection(self, endpoint: str) -> bool:
        """Test SQL injection protection."""
        malicious_payloads = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'/*",
            "' UNION SELECT * FROM users --"
        ]

        for payload in malicious_payloads:
            response = await self.http_client.get(f"{endpoint}?id={payload}")
            if response.status_code == 500:  # Server error indicates potential vulnerability
                return False

        return True
