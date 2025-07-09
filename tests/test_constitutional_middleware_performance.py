"""
Performance tests for constitutional middleware with FastConstitutionalValidator.
Constitutional Hash: cdd01ef066bc6cf2

Tests the performance improvements from baseline 3.299ms to target <0.5ms.
"""

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI, Request, Response
from fastapi.testclient import TestClient

from services.shared.middleware.constitutional_validation import (
    ConstitutionalValidationMiddleware,
    CONSTITUTIONAL_HASH,
)


class MockRequest:
    """Mock request for performance testing."""
    
    def __init__(self, headers=None, body=None):
        self.headers = headers or {}
        self.method = "POST"
        self.url = MagicMock()
        self.url.path = "/test"
        self.state = MagicMock()
        self.state.service_name = "test-service"
        if body:
            self._body = body


class MockResponse:
    """Mock response for performance testing."""
    
    def __init__(self):
        self.headers = {}
        self.status_code = 200


@pytest.fixture
def middleware():
    """Create middleware instance for testing."""
    app = FastAPI()
    return ConstitutionalValidationMiddleware(
        app,
        constitutional_hash=CONSTITUTIONAL_HASH,
        performance_target_ms=0.5,  # Target <0.5ms
        enable_strict_validation=True,
    )


@pytest.fixture
def mock_call_next():
    """Mock call_next function."""
    async def call_next(request):
        return MockResponse()
    return call_next


class TestConstitutionalMiddlewarePerformance:
    """Performance tests for constitutional middleware."""

    @pytest.mark.asyncio
    async def test_header_validation_performance(self, middleware):
        """Test header validation performance with fast validator."""
        request = MockRequest(headers={
            "X-Constitutional-Hash": CONSTITUTIONAL_HASH,
            "Content-Type": "application/json"
        })
        
        # Warm up
        for _ in range(10):
            await middleware._validate_request_headers(
                request, "test-service", "/test", "POST"
            )
        
        # Performance test
        start_time = time.perf_counter()
        iterations = 1000
        
        for _ in range(iterations):
            await middleware._validate_request_headers(
                request, "test-service", "/test", "POST"
            )
        
        end_time = time.perf_counter()
        avg_time_ms = ((end_time - start_time) / iterations) * 1000
        
        print(f"Header validation average time: {avg_time_ms:.4f}ms")
        assert avg_time_ms < 0.5, f"Header validation too slow: {avg_time_ms:.4f}ms"

    @pytest.mark.asyncio
    async def test_body_validation_performance(self, middleware):
        """Test body validation performance with fast validator."""
        body = b'{"constitutional_hash": "cdd01ef066bc6cf2", "data": "test"}'
        request = MockRequest(
            headers={"Content-Type": "application/json"},
            body=body
        )
        
        # Warm up
        for _ in range(10):
            await middleware._validate_request_body(
                request, "test-service", "/test", "POST"
            )
        
        # Performance test
        start_time = time.perf_counter()
        iterations = 1000
        
        for _ in range(iterations):
            await middleware._validate_request_body(
                request, "test-service", "/test", "POST"
            )
        
        end_time = time.perf_counter()
        avg_time_ms = ((end_time - start_time) / iterations) * 1000
        
        print(f"Body validation average time: {avg_time_ms:.4f}ms")
        assert avg_time_ms < 0.5, f"Body validation too slow: {avg_time_ms:.4f}ms"

    @pytest.mark.asyncio
    async def test_full_middleware_performance(self, middleware, mock_call_next):
        """Test full middleware dispatch performance."""
        request = MockRequest(headers={
            "X-Constitutional-Hash": CONSTITUTIONAL_HASH,
            "Content-Type": "application/json"
        })
        
        # Warm up
        for _ in range(10):
            await middleware.dispatch(request, mock_call_next)
        
        # Performance test
        start_time = time.perf_counter()
        iterations = 100  # Fewer iterations for full middleware test
        
        for _ in range(iterations):
            await middleware.dispatch(request, mock_call_next)
        
        end_time = time.perf_counter()
        avg_time_ms = ((end_time - start_time) / iterations) * 1000
        
        print(f"Full middleware average time: {avg_time_ms:.4f}ms")
        assert avg_time_ms < 0.5, f"Full middleware too slow: {avg_time_ms:.4f}ms"

    @pytest.mark.asyncio
    async def test_performance_comparison_baseline(self, middleware):
        """Test performance improvement from baseline 3.299ms."""
        request = MockRequest(headers={
            "X-Constitutional-Hash": CONSTITUTIONAL_HASH,
            "Content-Type": "application/json"
        })
        
        # Simulate baseline performance (old implementation)
        baseline_ms = 3.299
        
        # Test current performance
        start_time = time.perf_counter()
        iterations = 100
        
        for _ in range(iterations):
            await middleware._validate_request_headers(
                request, "test-service", "/test", "POST"
            )
        
        end_time = time.perf_counter()
        current_ms = ((end_time - start_time) / iterations) * 1000
        
        improvement_factor = baseline_ms / current_ms
        improvement_percent = ((baseline_ms - current_ms) / baseline_ms) * 100
        
        print(f"Baseline: {baseline_ms:.3f}ms")
        print(f"Current: {current_ms:.4f}ms")
        print(f"Improvement: {improvement_factor:.1f}x faster")
        print(f"Improvement: {improvement_percent:.1f}% reduction")
        
        assert current_ms < baseline_ms, "Performance should be better than baseline"
        assert improvement_factor > 6, f"Should be >6x faster, got {improvement_factor:.1f}x"

    @pytest.mark.asyncio
    async def test_constitutional_compliance_maintained(self, middleware):
        """Test that constitutional compliance is maintained with fast validation."""
        # Test valid hash
        valid_request = MockRequest(headers={
            "X-Constitutional-Hash": CONSTITUTIONAL_HASH
        })
        
        # Should not raise exception
        await middleware._validate_request_headers(
            valid_request, "test-service", "/test", "POST"
        )
        
        # Test invalid hash
        invalid_request = MockRequest(headers={
            "X-Constitutional-Hash": "invalid-hash"
        })
        
        # Should raise HTTPException for invalid hash
        with pytest.raises(Exception):  # HTTPException or similar
            await middleware._validate_request_headers(
                invalid_request, "test-service", "/test", "POST"
            )

    def test_fast_validator_integration(self, middleware):
        """Test that fast validator is properly integrated."""
        # Verify fast validator is initialized
        assert middleware.fast_validator is not None
        
        # Verify constitutional hash is set correctly
        assert middleware.constitutional_hash == CONSTITUTIONAL_HASH
        
        # Verify performance target is set
        assert middleware.performance_target_ms == 0.5


if __name__ == "__main__":
    # Run performance tests directly
    import sys
    
    async def run_performance_tests():
        """Run performance tests directly."""
        print("HASH-OK:cdd01ef066bc6cf2")
        print("Running Constitutional Middleware Performance Tests...")
        print("=" * 60)
        
        # Create middleware
        app = FastAPI()
        middleware = ConstitutionalValidationMiddleware(
            app,
            constitutional_hash=CONSTITUTIONAL_HASH,
            performance_target_ms=0.5,
        )
        
        # Test header validation performance
        request = MockRequest(headers={
            "X-Constitutional-Hash": CONSTITUTIONAL_HASH,
            "Content-Type": "application/json"
        })
        
        start_time = time.perf_counter()
        iterations = 1000
        
        for _ in range(iterations):
            await middleware._validate_request_headers(
                request, "test-service", "/test", "POST"
            )
        
        end_time = time.perf_counter()
        avg_time_ms = ((end_time - start_time) / iterations) * 1000
        
        print(f"Header validation: {avg_time_ms:.4f}ms (target: <0.5ms)")
        print(f"Performance target met: {avg_time_ms < 0.5}")
        print(f"Improvement from baseline 3.299ms: {3.299/avg_time_ms:.1f}x faster")
        print("HASH-OK:cdd01ef066bc6cf2")
    
    if len(sys.argv) > 1 and sys.argv[1] == "--run":
        asyncio.run(run_performance_tests())
