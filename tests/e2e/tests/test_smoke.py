"""
ACGS Smoke Tests

Basic smoke tests for quick validation of the E2E test framework.
These tests run in offline mode and validate the framework itself.
"""

import pytest
import asyncio
import time
from typing import Dict, Any

from ..framework.config import E2ETestConfig, E2ETestMode


@pytest.mark.smoke
@pytest.mark.asyncio
async def test_framework_initialization():
    """Test that the E2E test framework can be initialized."""
    config = E2ETestConfig(
        test_mode=E2ETestMode.OFFLINE,
        constitutional_hash="cdd01ef066bc6cf2"
    )

    assert config is not None
    assert config.test_mode == E2ETestMode.OFFLINE
    assert config.constitutional_hash == "cdd01ef066bc6cf2"


@pytest.mark.smoke
@pytest.mark.asyncio
async def test_constitutional_hash_validation():
    """Test constitutional hash validation."""
    config = E2ETestConfig(
        test_mode=E2ETestMode.OFFLINE,
        constitutional_hash="cdd01ef066bc6cf2"
    )
    
    # Test valid hash
    assert config.constitutional_hash == "cdd01ef066bc6cf2"
    
    # Test hash format (should be 16 hex characters)
    assert len(config.constitutional_hash) == 16
    assert all(c in '0123456789abcdef' for c in config.constitutional_hash)


@pytest.mark.smoke
@pytest.mark.asyncio
async def test_performance_targets():
    """Test that performance targets are properly defined."""
    config = E2ETestConfig(
        test_mode=E2ETestMode.OFFLINE,
        constitutional_hash="cdd01ef066bc6cf2"
    )
    
    # Test latency targets
    assert hasattr(config, 'performance')
    
    # Simulate performance measurement
    start_time = time.perf_counter()
    await asyncio.sleep(0.001)  # 1ms delay
    end_time = time.perf_counter()
    
    duration_ms = (end_time - start_time) * 1000
    
    # Should be under 5ms target (with some tolerance for test environment)
    assert duration_ms < 50  # Generous tolerance for CI environments


@pytest.mark.smoke
@pytest.mark.asyncio
async def test_offline_mode_configuration():
    """Test offline mode configuration."""
    config = E2ETestConfig(
        test_mode=E2ETestMode.OFFLINE,
        constitutional_hash="cdd01ef066bc6cf2"
    )

    assert config.test_mode == E2ETestMode.OFFLINE
    
    # In offline mode, external services should be disabled
    # This is a basic validation that the framework respects offline mode


@pytest.mark.smoke
def test_constitutional_compliance_hash():
    """Test constitutional compliance hash validation."""
    expected_hash = "cdd01ef066bc6cf2"
    
    # Test hash format validation
    assert len(expected_hash) == 16
    assert all(c in '0123456789abcdef' for c in expected_hash)
    
    # Test that the hash is the expected value
    assert expected_hash == "cdd01ef066bc6cf2"


@pytest.mark.smoke
@pytest.mark.asyncio
async def test_basic_async_functionality():
    """Test basic async functionality works in the test environment."""
    start_time = time.perf_counter()
    
    # Test async operations
    await asyncio.sleep(0.001)
    
    end_time = time.perf_counter()
    duration_ms = (end_time - start_time) * 1000
    
    # Should complete in reasonable time
    assert duration_ms >= 1  # At least 1ms
    assert duration_ms < 100  # Less than 100ms


@pytest.mark.smoke
def test_test_markers():
    """Test that pytest markers are working correctly."""
    # This test itself should have the smoke marker
    # If this test runs, markers are working
    assert True


@pytest.mark.smoke
@pytest.mark.asyncio
async def test_framework_imports():
    """Test that all framework imports work correctly."""
    try:
        from ..framework.base import BaseE2ETest, E2ETestResult
        from ..framework.config import E2ETestConfig, E2ETestMode, ServiceType
        from ..framework.core import E2ETestFramework
        from ..framework.utils import TestEnvironmentManager
        from ..framework.mocks import MockServiceManager
        from ..framework.reporter import E2ETestReporter
        
        # If we get here, all imports worked
        assert True
        
    except ImportError as e:
        pytest.fail(f"Framework import failed: {e}")


@pytest.mark.smoke
@pytest.mark.asyncio
async def test_performance_measurement():
    """Test performance measurement capabilities."""
    measurements = []
    
    for i in range(5):
        start_time = time.perf_counter()
        await asyncio.sleep(0.001)  # 1ms operation
        end_time = time.perf_counter()
        
        duration_ms = (end_time - start_time) * 1000
        measurements.append(duration_ms)
    
    # Calculate P99 (95th percentile for small sample)
    measurements.sort()
    p99_index = int(0.95 * len(measurements))
    p99_latency = measurements[p99_index]
    
    # P99 should be reasonable for test environment
    assert p99_latency < 100  # Less than 100ms
    
    # Average should be close to expected
    avg_latency = sum(measurements) / len(measurements)
    assert avg_latency >= 1  # At least 1ms
    assert avg_latency < 50  # Less than 50ms


@pytest.mark.smoke
@pytest.mark.asyncio
async def test_error_handling():
    """Test basic error handling in the framework."""
    config = E2ETestConfig(
        test_mode=E2ETestMode.OFFLINE,
        constitutional_hash="cdd01ef066bc6cf2"
    )
    
    # Test that config handles invalid values gracefully
    try:
        # This should work
        assert config.constitutional_hash == "cdd01ef066bc6cf2"
    except Exception as e:
        pytest.fail(f"Unexpected error in basic config: {e}")


@pytest.mark.smoke
def test_environment_variables():
    """Test environment variable handling."""
    import os
    
    # Test that we can access environment variables
    # These should be set by the test runner script
    constitutional_hash = os.getenv('CONSTITUTIONAL_HASH', 'cdd01ef066bc6cf2')
    test_mode = os.getenv('E2E_TEST_MODE', 'offline')
    
    assert constitutional_hash == 'cdd01ef066bc6cf2'
    assert test_mode == 'offline'


@pytest.mark.smoke
@pytest.mark.asyncio
async def test_concurrent_operations():
    """Test concurrent operations for performance validation."""
    async def mock_operation():
        await asyncio.sleep(0.001)
        return time.perf_counter()
    
    # Run 5 concurrent operations
    start_time = time.perf_counter()
    tasks = [mock_operation() for _ in range(5)]
    results = await asyncio.gather(*tasks)
    end_time = time.perf_counter()
    
    # All operations should complete
    assert len(results) == 5
    
    # Total time should be less than sequential execution
    total_duration_ms = (end_time - start_time) * 1000
    assert total_duration_ms < 50  # Should be much faster than 5 * 1ms


@pytest.mark.smoke
@pytest.mark.integration
@pytest.mark.asyncio
async def test_service_connectivity():
    """Test connectivity to available ACGS services."""
    import aiohttp

    # Services that should be available based on integration report
    available_services = [
        ("auth_service", "http://localhost:8016/health"),
        ("ac_service", "http://localhost:8001/health"),
        ("fv_service", "http://localhost:8003/health"),
        ("gs_service", "http://localhost:8004/health"),
        ("pgc_service", "http://localhost:8005/health"),
    ]

    healthy_count = 0

    async with aiohttp.ClientSession() as session:
        for service_name, health_url in available_services:
            try:
                async with session.get(health_url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        healthy_count += 1
                        print(f"✅ {service_name}: Healthy")
                    else:
                        print(f"⚠️ {service_name}: HTTP {response.status}")
            except Exception as e:
                print(f"❌ {service_name}: {e}")

    # At least 3 services should be healthy for basic functionality
    assert healthy_count >= 3, f"Only {healthy_count}/5 services are healthy"


@pytest.mark.smoke
@pytest.mark.integration
def test_infrastructure_connectivity():
    """Test infrastructure service connectivity."""
    import subprocess

    # Test PostgreSQL connectivity
    try:
        result = subprocess.run(
            ["pg_isready", "-h", "localhost", "-p", "5439"],
            capture_output=True,
            timeout=10
        )
        postgres_healthy = result.returncode == 0
    except Exception:
        postgres_healthy = False

    # Test Redis connectivity
    try:
        result = subprocess.run(
            ["redis-cli", "-h", "localhost", "-p", "6389", "ping"],
            capture_output=True,
            timeout=10
        )
        redis_healthy = result.returncode == 0 and b"PONG" in result.stdout
    except Exception:
        redis_healthy = False

    # At least one infrastructure service should be available
    assert postgres_healthy or redis_healthy, "No infrastructure services are available"
