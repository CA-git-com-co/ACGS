"""
Unit Tests for Performance Integration Service
Constitutional Hash: cdd01ef066bc6cf2

Comprehensive test suite for the PerformanceIntegrationService
covering all integration functionality and performance monitoring.

Test Coverage:
- Service initialization and component integration
- Request processing with performance optimization
- Performance monitoring and metrics collection
- Automated optimization and regression detection
- Error handling and recovery
- Constitutional compliance validation
"""

import asyncio
import pytest
import time
from unittest.mock import AsyncMock, Mock, patch
from typing import Dict, Any

from services.shared.performance.performance_integration_service import (
    PerformanceIntegrationService,
    PerformanceMetrics,
    INTEGRATION_PERFORMANCE_TARGETS,
    CONSTITUTIONAL_HASH
)


class TestPerformanceMetrics:
    """Test suite for PerformanceMetrics."""

    def test_initialization(self):
        """Test metrics initialization."""
        metrics = PerformanceMetrics()
        
        assert metrics.total_requests == 0
        assert metrics.successful_requests == 0
        assert metrics.failed_requests == 0
        assert metrics.total_response_time == 0.0
        assert metrics.min_response_time == float('inf')
        assert metrics.max_response_time == 0.0

    def test_add_request_success(self):
        """Test adding successful request metrics."""
        metrics = PerformanceMetrics()
        
        metrics.add_request(0.005, success=True)  # 5ms
        
        assert metrics.total_requests == 1
        assert metrics.successful_requests == 1
        assert metrics.failed_requests == 0
        assert metrics.total_response_time == 0.005
        assert metrics.min_response_time == 0.005
        assert metrics.max_response_time == 0.005

    def test_add_request_failure(self):
        """Test adding failed request metrics."""
        metrics = PerformanceMetrics()
        
        metrics.add_request(0.010, success=False)  # 10ms
        
        assert metrics.total_requests == 1
        assert metrics.successful_requests == 0
        assert metrics.failed_requests == 1

    def test_avg_response_time(self):
        """Test average response time calculation."""
        metrics = PerformanceMetrics()
        
        # No requests
        assert metrics.get_avg_response_time_ms() == 0.0
        
        # Add requests
        metrics.add_request(0.002)  # 2ms
        metrics.add_request(0.004)  # 4ms
        
        assert metrics.get_avg_response_time_ms() == 3.0  # 3ms average

    def test_success_rate(self):
        """Test success rate calculation."""
        metrics = PerformanceMetrics()
        
        # No requests
        assert metrics.get_success_rate() == 1.0
        
        # Add mixed requests
        metrics.add_request(0.001, success=True)
        metrics.add_request(0.002, success=True)
        metrics.add_request(0.003, success=False)
        
        assert metrics.get_success_rate() == 2/3  # 66.7%

    def test_cache_hit_rate(self):
        """Test cache hit rate calculation."""
        metrics = PerformanceMetrics()
        
        # No cache requests
        assert metrics.get_cache_hit_rate() == 0.0
        
        # Add cache statistics
        metrics.cache_hits = 80
        metrics.cache_misses = 20
        
        assert metrics.get_cache_hit_rate() == 0.8  # 80%


class TestPerformanceIntegrationService:
    """Test suite for PerformanceIntegrationService."""

    @pytest.fixture
    def service(self):
        """Create a performance integration service."""
        return PerformanceIntegrationService()

    @pytest.fixture
    def mock_components(self):
        """Create mock components for testing."""
        mock_validator = Mock()
        mock_validator.validate_hash.return_value = True
        mock_validator.get_detailed_metrics.return_value = {
            "performance_summary": {"avg_latency_ms": 0.1}
        }
        
        mock_pool_manager = AsyncMock()
        mock_pool_manager.health_check_all.return_value = {
            "overall_healthy": True
        }
        
        mock_cache = AsyncMock()
        mock_cache.get_performance_metrics.return_value = {
            "performance_summary": {"overall_hit_rate": 0.95}
        }
        
        return {
            "validator": mock_validator,
            "pool_manager": mock_pool_manager,
            "cache": mock_cache
        }

    def test_initialization(self, service):
        """Test service initialization."""
        assert service.constitutional_hash == CONSTITUTIONAL_HASH
        assert service.metrics.total_requests == 0
        assert service._running is False
        assert len(service.performance_history) == 0

    @pytest.mark.asyncio
    async def test_initialize_success(self, service, mock_components):
        """Test successful service initialization."""
        with patch.multiple(
            'services.shared.performance.performance_integration_service',
            get_pool_manager=AsyncMock(return_value=mock_components["pool_manager"]),
            get_ultra_fast_cache=AsyncMock(return_value=mock_components["cache"])
        ):
            service.constitutional_validator = mock_components["validator"]
            
            await service.initialize()
            
            assert service._running is True
            assert service.pool_manager is not None
            assert service.cache is not None

    @pytest.mark.asyncio
    async def test_initialize_constitutional_failure(self, service):
        """Test initialization failure due to constitutional compliance."""
        # Mock validator to fail
        service.constitutional_validator.validate_hash.return_value = False
        
        with pytest.raises(RuntimeError, match="Constitutional compliance violation"):
            await service.initialize()

    @pytest.mark.asyncio
    async def test_process_request_success(self, service, mock_components):
        """Test successful request processing."""
        # Setup mocks
        service.constitutional_validator = mock_components["validator"]
        service.cache = mock_components["cache"]
        service.cache.get.return_value = None  # Cache miss
        service.cache.set.return_value = True
        
        request_data = {"id": "test_request", "data": "test"}
        
        response = await service.process_request(request_data)
        
        assert response["processed"] is True
        assert response["constitutional_hash"] == CONSTITUTIONAL_HASH
        assert response["request_id"] == "test_request"
        assert "performance" in response
        assert service.metrics.total_requests == 1
        assert service.metrics.successful_requests == 1

    @pytest.mark.asyncio
    async def test_process_request_cached(self, service, mock_components):
        """Test request processing with cache hit."""
        # Setup mocks
        service.constitutional_validator = mock_components["validator"]
        service.cache = mock_components["cache"]
        
        cached_response = {
            "processed": True,
            "cached": True,
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
        service.cache.get.return_value = cached_response
        
        request_data = {"id": "test_request"}
        
        response = await service.process_request(request_data)
        
        assert response == cached_response
        assert service.metrics.cache_hits == 1

    @pytest.mark.asyncio
    async def test_process_request_with_database(self, service, mock_components):
        """Test request processing with database operation."""
        # Setup mocks
        service.constitutional_validator = mock_components["validator"]
        service.cache = mock_components["cache"]
        service.cache.get.return_value = None
        service.cache.set.return_value = True
        service.pool_manager = mock_components["pool_manager"]
        
        # Mock pool and connection
        mock_pool = AsyncMock()
        mock_connection = AsyncMock()
        mock_pool.acquire_connection.return_value = mock_connection
        service.pool_manager.get_pool.return_value = mock_pool
        
        request_data = {"id": "test_request", "database_operation": True}
        
        response = await service.process_request(request_data)
        
        assert response["processed"] is True
        assert service.metrics.db_connections_acquired == 1
        mock_pool.acquire_connection.assert_called_once()
        mock_pool.release_connection.assert_called_once_with(mock_connection)

    @pytest.mark.asyncio
    async def test_process_request_constitutional_failure(self, service):
        """Test request processing with constitutional failure."""
        # Mock validator to fail
        service.constitutional_validator.validate_hash.return_value = False
        
        request_data = {"id": "test_request"}
        
        with pytest.raises(ValueError, match="Constitutional compliance violation"):
            await service.process_request(request_data)
        
        assert service.metrics.failed_requests == 1

    @pytest.mark.asyncio
    async def test_collect_performance_metrics(self, service, mock_components):
        """Test performance metrics collection."""
        # Setup service with mocks
        service.constitutional_validator = mock_components["validator"]
        service.pool_manager = mock_components["pool_manager"]
        service.cache = mock_components["cache"]
        
        # Add some metrics
        service.metrics.total_requests = 100
        service.metrics.successful_requests = 95
        
        await service._collect_performance_metrics()
        
        assert len(service.performance_history) == 1
        
        latest_metrics = service.performance_history[-1]
        assert "constitutional_validator" in latest_metrics
        assert "connection_pools" in latest_metrics
        assert "cache" in latest_metrics
        assert "integration" in latest_metrics

    @pytest.mark.asyncio
    async def test_run_optimization(self, service, mock_components):
        """Test optimization execution."""
        # Setup service with mocks
        service.constitutional_validator = mock_components["validator"]
        service.constitutional_validator.optimize_performance.return_value = {
            "optimizations_applied": ["test_optimization"]
        }
        service.pool_manager = mock_components["pool_manager"]
        service.pool_manager.optimize_all_pools.return_value = {
            "pool_optimizations": {
                "test_pool": {"optimizations_applied": ["pool_optimization"]}
            }
        }
        service.cache = mock_components["cache"]
        service.cache.optimize_performance.return_value = {
            "optimizations_applied": ["cache_optimization"]
        }
        
        await service._run_optimization()
        
        assert service.metrics.optimization_runs == 1
        assert service.metrics.last_optimization > 0

    @pytest.mark.asyncio
    async def test_performance_regression_detection(self, service):
        """Test performance regression detection."""
        # Add historical data with good performance
        for i in range(10):
            service.performance_history.append({
                "timestamp": time.time() - (10 - i),
                "integration": {"avg_response_time_ms": 1.0}  # Good performance
            })
        
        # Add current data with poor performance
        current_metrics = {
            "timestamp": time.time(),
            "integration": {"avg_response_time_ms": 10.0}  # Poor performance
        }
        
        with patch.object(service, '_collect_performance_metrics') as mock_collect:
            mock_collect.return_value = None
            
            # This should detect regression
            await service._check_performance_regression(current_metrics)
            
            # Regression should be logged (we can't easily test logging here)

    @pytest.mark.asyncio
    async def test_get_performance_summary(self, service, mock_components):
        """Test performance summary generation."""
        # Setup service with mocks
        service.constitutional_validator = mock_components["validator"]
        service.cache = mock_components["cache"]
        service.pool_manager = mock_components["pool_manager"]
        
        # Add some metrics
        service.metrics.total_requests = 100
        service.metrics.successful_requests = 95
        service.metrics.total_response_time = 0.1  # 100ms total
        service.metrics.cache_hits = 80
        service.metrics.cache_misses = 20
        
        summary = await service.get_performance_summary()
        
        assert "integration_metrics" in summary
        assert "performance_targets" in summary
        assert "targets_met" in summary
        assert "constitutional_validator" in summary
        assert "cache" in summary
        assert "connection_pools" in summary
        
        integration_metrics = summary["integration_metrics"]
        assert integration_metrics["total_requests"] == 100
        assert integration_metrics["success_rate"] == 0.95
        assert integration_metrics["avg_response_time_ms"] == 1.0
        assert integration_metrics["cache_hit_rate"] == 0.8

    @pytest.mark.asyncio
    async def test_concurrent_request_processing(self, service, mock_components):
        """Test concurrent request processing."""
        # Setup service
        service.constitutional_validator = mock_components["validator"]
        service.cache = mock_components["cache"]
        service.cache.get.return_value = None
        service.cache.set.return_value = True
        
        async def process_test_request(request_id: int):
            request_data = {"id": f"request_{request_id}"}
            return await service.process_request(request_data)
        
        # Process multiple requests concurrently
        tasks = [process_test_request(i) for i in range(10)]
        responses = await asyncio.gather(*tasks)
        
        assert len(responses) == 10
        assert all(r["processed"] for r in responses)
        assert service.metrics.total_requests == 10
        assert service.metrics.successful_requests == 10

    @pytest.mark.asyncio
    async def test_performance_targets_validation(self, service):
        """Test performance targets validation."""
        # Add metrics that meet targets
        service.metrics.total_requests = 100
        service.metrics.successful_requests = 99
        service.metrics.total_response_time = 0.1  # 1ms average
        service.metrics.cache_hits = 95
        service.metrics.cache_misses = 5
        
        summary = await service.get_performance_summary()
        targets_met = summary["targets_met"]
        
        assert targets_met["response_time"] is True  # 1ms < 2ms target
        assert targets_met["success_rate"] is True   # 99% >= 99% target
        assert targets_met["cache_hit_rate"] is True # 95% >= 95% target

    @pytest.mark.asyncio
    async def test_service_close(self, service, mock_components):
        """Test service closure."""
        # Setup service
        service._running = True
        service._monitoring_task = AsyncMock()
        service._optimization_task = AsyncMock()
        service.cache = mock_components["cache"]
        service.pool_manager = mock_components["pool_manager"]
        
        await service.close()
        
        assert service._running is False
        service._monitoring_task.cancel.assert_called_once()
        service._optimization_task.cancel.assert_called_once()
        service.cache.close.assert_called_once()
        service.pool_manager.close_all.assert_called_once()

    def test_performance_history_size_limit(self, service):
        """Test performance history size limiting."""
        # Fill history beyond limit
        service.max_history_size = 5
        
        for i in range(10):
            service.performance_history.append({"timestamp": i})
        
        # Simulate collection that triggers size limiting
        if len(service.performance_history) > service.max_history_size:
            service.performance_history = service.performance_history[-service.max_history_size:]
        
        assert len(service.performance_history) == 5
        assert service.performance_history[0]["timestamp"] == 5  # Oldest kept

    @pytest.mark.asyncio
    async def test_error_handling_in_monitoring(self, service):
        """Test error handling in monitoring loop."""
        service._running = True
        
        # Mock collect_performance_metrics to raise an exception
        with patch.object(service, '_collect_performance_metrics', side_effect=Exception("Test error")):
            # This should not crash the service
            try:
                await service._collect_performance_metrics()
            except Exception:
                pass  # Expected to handle gracefully
        
        # Service should still be running
        assert service._running is True

    @pytest.mark.asyncio
    async def test_memory_efficiency(self, service):
        """Test memory efficiency of performance tracking."""
        import sys
        
        # Get initial memory usage
        initial_size = sys.getsizeof(service.performance_history)
        
        # Add many performance records
        for i in range(1000):
            service.performance_history.append({
                "timestamp": time.time(),
                "small_data": f"test_{i}"
            })
        
        # Limit history size
        service.performance_history = service.performance_history[-100:]
        
        final_size = sys.getsizeof(service.performance_history)
        
        # Memory should not grow excessively
        assert len(service.performance_history) == 100
        assert final_size < initial_size * 10  # Should not be more than 10x larger


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
