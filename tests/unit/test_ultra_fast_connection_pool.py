"""
Unit Tests for Ultra-Fast Connection Pool
Constitutional Hash: cdd01ef066bc6cf2

Comprehensive test suite for the UltraFastConnectionPool and
UltraFastConnectionPoolManager covering all functionality.

Test Coverage:
- Connection pool initialization and configuration
- Connection acquisition and release performance
- Health monitoring and metrics
- Concurrent access and thread safety
- Error handling and recovery
- Performance optimization
"""

import asyncio
import pytest
import time
from unittest.mock import AsyncMock, Mock, patch
from typing import Dict, Any

from services.shared.database.ultra_fast_connection_pool import (
    UltraFastConnectionPool,
    UltraFastConnectionPoolManager,
    ConnectionMetrics,
    POOL_PERFORMANCE_TARGETS,
    CONSTITUTIONAL_HASH
)
from services.shared.constitutional.validation import UltraFastConstitutionalValidator


class TestConnectionMetrics:
    """Test suite for ConnectionMetrics."""

    def test_initialization(self):
        """Test metrics initialization."""
        metrics = ConnectionMetrics()
        
        assert metrics.total_acquisitions == 0
        assert metrics.successful_acquisitions == 0
        assert metrics.failed_acquisitions == 0
        assert metrics.total_acquisition_time == 0.0
        assert metrics.peak_connections == 0
        assert metrics.current_connections == 0

    def test_avg_acquisition_time(self):
        """Test average acquisition time calculation."""
        metrics = ConnectionMetrics()
        
        # No acquisitions
        assert metrics.get_avg_acquisition_time_ms() == 0.0
        
        # Add some acquisition times
        metrics.total_acquisitions = 3
        metrics.total_acquisition_time = 0.003  # 3ms total
        
        assert metrics.get_avg_acquisition_time_ms() == 1.0  # 1ms average

    def test_success_rate(self):
        """Test success rate calculation."""
        metrics = ConnectionMetrics()
        
        # No acquisitions
        assert metrics.get_success_rate() == 1.0
        
        # Add some acquisitions
        metrics.total_acquisitions = 10
        metrics.successful_acquisitions = 8
        metrics.failed_acquisitions = 2
        
        assert metrics.get_success_rate() == 0.8


class TestUltraFastConnectionPool:
    """Test suite for UltraFastConnectionPool."""

    @pytest.fixture
    def mock_validator(self):
        """Create a mock constitutional validator."""
        validator = Mock(spec=UltraFastConstitutionalValidator)
        validator.validate_hash.return_value = True
        return validator

    @pytest.fixture
    def pool_config(self):
        """Connection pool configuration for testing."""
        return {
            "pool_name": "test_pool",
            "dsn": "postgresql://test:test@localhost:5432/test",
            "min_size": 2,
            "max_size": 5
        }

    def test_initialization(self, pool_config, mock_validator):
        """Test connection pool initialization."""
        pool = UltraFastConnectionPool(
            constitutional_validator=mock_validator,
            **pool_config
        )
        
        assert pool.pool_name == "test_pool"
        assert pool.min_size == 2
        assert pool.max_size == 5
        assert pool.constitutional_hash == CONSTITUTIONAL_HASH
        assert pool.is_initialized is False
        assert pool.is_healthy is True

    @pytest.mark.asyncio
    async def test_initialization_with_mock_pool(self, pool_config, mock_validator):
        """Test pool initialization with mocked asyncpg."""
        with patch('services.shared.database.ultra_fast_connection_pool.asyncpg') as mock_asyncpg:
            # Mock the pool creation
            mock_pool = AsyncMock()
            mock_asyncpg.create_pool.return_value = mock_pool
            
            pool = UltraFastConnectionPool(
                constitutional_validator=mock_validator,
                **pool_config
            )
            
            await pool.initialize()
            
            assert pool.is_initialized is True
            assert pool.pool is not None
            mock_asyncpg.create_pool.assert_called_once()

    @pytest.mark.asyncio
    async def test_initialization_failure(self, pool_config, mock_validator):
        """Test pool initialization failure handling."""
        # Mock validator to fail constitutional check
        mock_validator.validate_hash.return_value = False
        
        pool = UltraFastConnectionPool(
            constitutional_validator=mock_validator,
            **pool_config
        )
        
        with pytest.raises(RuntimeError, match="Constitutional compliance violation"):
            await pool.initialize()
        
        assert pool.is_healthy is False

    @pytest.mark.asyncio
    async def test_connection_acquisition_success(self, pool_config, mock_validator):
        """Test successful connection acquisition."""
        with patch('services.shared.database.ultra_fast_connection_pool.asyncpg') as mock_asyncpg:
            # Mock the pool and connection
            mock_connection = AsyncMock()
            mock_pool = AsyncMock()
            mock_pool.acquire.return_value = mock_connection
            mock_asyncpg.create_pool.return_value = mock_pool
            
            pool = UltraFastConnectionPool(
                constitutional_validator=mock_validator,
                **pool_config
            )
            await pool.initialize()
            
            # Test connection acquisition
            connection = await pool.acquire_connection()
            
            assert connection == mock_connection
            assert pool.metrics.total_acquisitions == 1
            assert pool.metrics.successful_acquisitions == 1
            assert pool.metrics.current_connections == 1

    @pytest.mark.asyncio
    async def test_connection_acquisition_timeout(self, pool_config, mock_validator):
        """Test connection acquisition timeout."""
        with patch('services.shared.database.ultra_fast_connection_pool.asyncpg') as mock_asyncpg:
            # Mock the pool to timeout
            mock_pool = AsyncMock()
            mock_pool.acquire.side_effect = asyncio.TimeoutError()
            mock_asyncpg.create_pool.return_value = mock_pool
            
            pool = UltraFastConnectionPool(
                constitutional_validator=mock_validator,
                **pool_config
            )
            await pool.initialize()
            
            # Test connection acquisition timeout
            with pytest.raises(RuntimeError, match="Connection acquisition timeout"):
                await pool.acquire_connection()
            
            assert pool.metrics.total_acquisitions == 1
            assert pool.metrics.failed_acquisitions == 1

    @pytest.mark.asyncio
    async def test_connection_release(self, pool_config, mock_validator):
        """Test connection release."""
        with patch('services.shared.database.ultra_fast_connection_pool.asyncpg') as mock_asyncpg:
            mock_connection = AsyncMock()
            mock_pool = AsyncMock()
            mock_pool.acquire.return_value = mock_connection
            mock_asyncpg.create_pool.return_value = mock_pool
            
            pool = UltraFastConnectionPool(
                constitutional_validator=mock_validator,
                **pool_config
            )
            await pool.initialize()
            
            # Acquire and release connection
            connection = await pool.acquire_connection()
            await pool.release_connection(connection)
            
            mock_pool.release.assert_called_once_with(connection)
            assert pool.metrics.current_connections == 0

    @pytest.mark.asyncio
    async def test_health_check_success(self, pool_config, mock_validator):
        """Test successful health check."""
        with patch('services.shared.database.ultra_fast_connection_pool.asyncpg') as mock_asyncpg:
            mock_connection = AsyncMock()
            mock_connection.fetchval.return_value = 1
            mock_pool = AsyncMock()
            mock_pool.acquire.return_value.__aenter__.return_value = mock_connection
            mock_pool.get_size.return_value = 3
            mock_pool.get_min_size.return_value = 2
            mock_pool.get_max_size.return_value = 5
            mock_asyncpg.create_pool.return_value = mock_pool
            
            pool = UltraFastConnectionPool(
                constitutional_validator=mock_validator,
                **pool_config
            )
            await pool.initialize()
            
            health = await pool.health_check()
            
            assert health["healthy"] is True
            assert health["pool_name"] == "test_pool"
            assert health["pool_size"] == 3
            assert "health_check_time_ms" in health

    @pytest.mark.asyncio
    async def test_health_check_failure(self, pool_config, mock_validator):
        """Test health check failure."""
        with patch('services.shared.database.ultra_fast_connection_pool.asyncpg') as mock_asyncpg:
            mock_pool = AsyncMock()
            mock_pool.acquire.side_effect = Exception("Connection failed")
            mock_asyncpg.create_pool.return_value = mock_pool
            
            pool = UltraFastConnectionPool(
                constitutional_validator=mock_validator,
                **pool_config
            )
            await pool.initialize()
            
            health = await pool.health_check()
            
            assert health["healthy"] is False
            assert "error" in health
            assert pool.metrics.health_check_failures > 0

    def test_performance_metrics(self, pool_config, mock_validator):
        """Test performance metrics collection."""
        pool = UltraFastConnectionPool(
            constitutional_validator=mock_validator,
            **pool_config
        )
        
        # Simulate some metrics
        pool.metrics.total_acquisitions = 100
        pool.metrics.successful_acquisitions = 95
        pool.metrics.total_acquisition_time = 0.05  # 50ms total
        pool.metrics.current_connections = 3
        pool.metrics.peak_connections = 5
        
        metrics = pool.get_performance_metrics()
        
        assert "performance_summary" in metrics
        assert "pool_status" in metrics
        assert "optimization_status" in metrics
        
        perf_summary = metrics["performance_summary"]
        assert perf_summary["avg_acquisition_time_ms"] == 0.5  # 0.5ms average
        assert perf_summary["success_rate"] == 0.95
        assert perf_summary["total_acquisitions"] == 100

    @pytest.mark.asyncio
    async def test_performance_optimization(self, pool_config, mock_validator):
        """Test performance optimization."""
        with patch('services.shared.database.ultra_fast_connection_pool.asyncpg') as mock_asyncpg:
            mock_pool = AsyncMock()
            mock_asyncpg.create_pool.return_value = mock_pool
            
            pool = UltraFastConnectionPool(
                constitutional_validator=mock_validator,
                **pool_config
            )
            await pool.initialize()
            
            # Simulate poor performance
            pool.metrics.total_acquisitions = 100
            pool.metrics.successful_acquisitions = 80  # 80% success rate
            pool.metrics.total_acquisition_time = 0.2   # 2ms average (above target)
            
            optimization = await pool.optimize_performance()
            
            assert "optimizations_applied" in optimization
            assert "recommendations" in optimization
            assert "current_metrics" in optimization

    @pytest.mark.asyncio
    async def test_concurrent_connections(self, pool_config, mock_validator):
        """Test concurrent connection handling."""
        with patch('services.shared.database.ultra_fast_connection_pool.asyncpg') as mock_asyncpg:
            mock_connections = [AsyncMock() for _ in range(10)]
            mock_pool = AsyncMock()
            mock_pool.acquire.side_effect = mock_connections
            mock_asyncpg.create_pool.return_value = mock_pool
            
            pool = UltraFastConnectionPool(
                constitutional_validator=mock_validator,
                **pool_config
            )
            await pool.initialize()
            
            # Acquire multiple connections concurrently
            async def acquire_connection():
                return await pool.acquire_connection()
            
            tasks = [acquire_connection() for _ in range(5)]
            connections = await asyncio.gather(*tasks)
            
            assert len(connections) == 5
            assert pool.metrics.total_acquisitions == 5
            assert pool.metrics.successful_acquisitions == 5

    @pytest.mark.asyncio
    async def test_pool_close(self, pool_config, mock_validator):
        """Test pool closure."""
        with patch('services.shared.database.ultra_fast_connection_pool.asyncpg') as mock_asyncpg:
            mock_pool = AsyncMock()
            mock_asyncpg.create_pool.return_value = mock_pool
            
            pool = UltraFastConnectionPool(
                constitutional_validator=mock_validator,
                **pool_config
            )
            await pool.initialize()
            
            await pool.close()
            
            mock_pool.close.assert_called_once()
            assert pool.pool is None
            assert pool.is_initialized is False
            assert pool.is_healthy is False


class TestUltraFastConnectionPoolManager:
    """Test suite for UltraFastConnectionPoolManager."""

    @pytest.fixture
    def manager(self):
        """Create a connection pool manager."""
        return UltraFastConnectionPoolManager()

    def test_initialization(self, manager):
        """Test manager initialization."""
        assert len(manager.pools) == 0
        assert manager.constitutional_hash == CONSTITUTIONAL_HASH
        assert manager._monitoring_enabled is True

    @pytest.mark.asyncio
    async def test_create_pool(self, manager):
        """Test pool creation."""
        with patch('services.shared.database.ultra_fast_connection_pool.asyncpg'):
            pool = await manager.create_pool(
                "test_pool",
                "postgresql://test:test@localhost:5432/test",
                min_size=2,
                max_size=5
            )
            
            assert pool.pool_name == "test_pool"
            assert "test_pool" in manager.pools
            assert len(manager.pools) == 1

    @pytest.mark.asyncio
    async def test_create_duplicate_pool(self, manager):
        """Test creating duplicate pool raises error."""
        with patch('services.shared.database.ultra_fast_connection_pool.asyncpg'):
            await manager.create_pool(
                "test_pool",
                "postgresql://test:test@localhost:5432/test"
            )
            
            with pytest.raises(ValueError, match="Pool 'test_pool' already exists"):
                await manager.create_pool(
                    "test_pool",
                    "postgresql://test:test@localhost:5432/test"
                )

    @pytest.mark.asyncio
    async def test_get_pool(self, manager):
        """Test getting existing pool."""
        with patch('services.shared.database.ultra_fast_connection_pool.asyncpg'):
            created_pool = await manager.create_pool(
                "test_pool",
                "postgresql://test:test@localhost:5432/test"
            )
            
            retrieved_pool = await manager.get_pool("test_pool")
            assert retrieved_pool == created_pool

    @pytest.mark.asyncio
    async def test_get_nonexistent_pool(self, manager):
        """Test getting non-existent pool raises error."""
        with pytest.raises(ValueError, match="Pool 'nonexistent' not found"):
            await manager.get_pool("nonexistent")

    @pytest.mark.asyncio
    async def test_health_check_all(self, manager):
        """Test health check for all pools."""
        with patch('services.shared.database.ultra_fast_connection_pool.asyncpg'):
            # Create multiple pools
            await manager.create_pool("pool1", "postgresql://test:test@localhost:5432/test1")
            await manager.create_pool("pool2", "postgresql://test:test@localhost:5432/test2")
            
            # Mock health checks
            for pool in manager.pools.values():
                pool.health_check = AsyncMock(return_value={"healthy": True})
            
            health_results = await manager.health_check_all()
            
            assert health_results["overall_healthy"] is True
            assert len(health_results["pools"]) == 2
            assert health_results["total_pools"] == 2

    @pytest.mark.asyncio
    async def test_health_check_with_unhealthy_pool(self, manager):
        """Test health check with one unhealthy pool."""
        with patch('services.shared.database.ultra_fast_connection_pool.asyncpg'):
            await manager.create_pool("healthy_pool", "postgresql://test:test@localhost:5432/test1")
            await manager.create_pool("unhealthy_pool", "postgresql://test:test@localhost:5432/test2")
            
            # Mock health checks
            manager.pools["healthy_pool"].health_check = AsyncMock(
                return_value={"healthy": True}
            )
            manager.pools["unhealthy_pool"].health_check = AsyncMock(
                return_value={"healthy": False}
            )
            
            health_results = await manager.health_check_all()
            
            assert health_results["overall_healthy"] is False
            assert health_results["pools"]["healthy_pool"]["healthy"] is True
            assert health_results["pools"]["unhealthy_pool"]["healthy"] is False

    @pytest.mark.asyncio
    async def test_optimize_all_pools(self, manager):
        """Test optimization of all pools."""
        with patch('services.shared.database.ultra_fast_connection_pool.asyncpg'):
            await manager.create_pool("pool1", "postgresql://test:test@localhost:5432/test1")
            await manager.create_pool("pool2", "postgresql://test:test@localhost:5432/test2")
            
            # Mock optimization
            for pool in manager.pools.values():
                pool.optimize_performance = AsyncMock(return_value={
                    "optimizations_applied": ["test_optimization"],
                    "recommendations": ["test_recommendation"]
                })
            
            optimization_results = await manager.optimize_all_pools()
            
            assert "pool_optimizations" in optimization_results
            assert len(optimization_results["pool_optimizations"]) == 2

    @pytest.mark.asyncio
    async def test_close_all(self, manager):
        """Test closing all pools."""
        with patch('services.shared.database.ultra_fast_connection_pool.asyncpg'):
            await manager.create_pool("pool1", "postgresql://test:test@localhost:5432/test1")
            await manager.create_pool("pool2", "postgresql://test:test@localhost:5432/test2")
            
            # Mock close methods
            for pool in manager.pools.values():
                pool.close = AsyncMock()
            
            await manager.close_all()
            
            # Verify all pools were closed
            for pool in manager.pools.values():
                pool.close.assert_called_once()
            
            assert len(manager.pools) == 0
            assert manager._monitoring_enabled is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
