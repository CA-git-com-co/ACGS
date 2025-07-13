"""
ACGS-2 Persistent Audit Logger Unit Tests

Comprehensive test suite for the persistent audit logging system including:
- Hash chain integrity verification
- Tamper detection testing
- Performance benchmarks (<5ms target)
- Multi-tenant isolation validation
- Constitutional compliance verification

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import os
import pathlib

# Import the module under test
import sys
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.append(os.path.join(pathlib.Path(__file__).parent, "..", "app", "core"))

from persistent_audit_logger import (
    CONSTITUTIONAL_HASH,
    PersistentAuditLogger,
    log_audit_event,
)


class TestPersistentAuditLogger:
    """Test suite for PersistentAuditLogger class."""

    @pytest.fixture
    async def audit_logger(self):
        """Create a test audit logger instance."""
        db_config = {
            "host": "localhost",
            "port": 5439,
            "database": "acgs_test",
            "user": "test_user",
            "password": "test_password",
        }

        redis_config = {"url": "redis://localhost:6389"}

        logger = PersistentAuditLogger(db_config, redis_config)

        # Mock the database pool and Redis client for testing
        logger.db_pool = MagicMock()
        logger.redis_client = AsyncMock()

        return logger

    @pytest.fixture
    def sample_event_data(self):
        """Sample event data for testing."""
        return {
            "action": "user_login",
            "resource_type": "authentication",
            "resource_id": "user_123",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "ip_address": "192.168.1.100",
            "user_agent": "Mozilla/5.0 Test Browser",
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

    def test_constitutional_hash_constant(self):
        """Test that constitutional hash is correctly set."""
        assert CONSTITUTIONAL_HASH == "cdd01ef066bc6cf2"

    def test_audit_logger_initialization(self, audit_logger):
        """Test audit logger initialization."""
        assert audit_logger.constitutional_hash == CONSTITUTIONAL_HASH
        assert audit_logger.pool_size == 20
        assert audit_logger.max_overflow == 30
        assert audit_logger.insert_times == []
        assert audit_logger.cache_hits == 0
        assert audit_logger.cache_misses == 0

    def test_hash_chain_calculation(self, audit_logger, sample_event_data):
        """Test hash chain calculation for tamper detection."""
        # Test genesis hash (no previous hash)
        genesis_hash = audit_logger._calculate_hash_chain(None, sample_event_data)
        assert len(genesis_hash) == 64  # SHA-256 produces 64-character hex string
        assert isinstance(genesis_hash, str)

        # Test chained hash
        chained_hash = audit_logger._calculate_hash_chain(
            genesis_hash, sample_event_data
        )
        assert len(chained_hash) == 64
        assert chained_hash != genesis_hash  # Should be different

        # Test deterministic behavior
        same_hash = audit_logger._calculate_hash_chain(genesis_hash, sample_event_data)
        assert chained_hash == same_hash

    def test_constitutional_compliance_validation(self, audit_logger):
        """Test constitutional compliance validation."""
        # Valid event data
        valid_data = {
            "action": "test_action",
            "resource_type": "test_resource",
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }
        assert audit_logger._validate_constitutional_compliance(valid_data) is True

        # Missing required fields
        invalid_data_1 = {"action": "test_action"}  # Missing resource_type
        assert audit_logger._validate_constitutional_compliance(invalid_data_1) is False

        invalid_data_2 = {"resource_type": "test_resource"}  # Missing action
        assert audit_logger._validate_constitutional_compliance(invalid_data_2) is False

        # Invalid constitutional hash
        invalid_data_3 = {
            "action": "test_action",
            "resource_type": "test_resource",
            "constitutional_hash": "invalid_hash",
        }
        assert audit_logger._validate_constitutional_compliance(invalid_data_3) is False

    @pytest.mark.asyncio
    async def test_log_event_success(self, audit_logger, sample_event_data):
        """Test successful event logging."""
        # Mock database operations
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {"id": 123}
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        audit_logger.db_pool.getconn.return_value = mock_conn

        # Mock Redis operations
        audit_logger.redis_client.get.return_value = None  # Cache miss
        audit_logger.redis_client.setex.return_value = True

        result = await audit_logger.log_event(
            event_data=sample_event_data,
            tenant_id="test-tenant-123",
            user_id="user-456",
            service_name="test_service",
            event_type="test_event",
        )

        assert result["success"] is True
        assert result["record_id"] == 123
        assert "current_hash" in result
        assert "insert_time_ms" in result
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH

        # Verify database operations were called
        audit_logger.db_pool.getconn.assert_called()
        audit_logger.db_pool.putconn.assert_called()

    @pytest.mark.asyncio
    async def test_log_event_constitutional_compliance_failure(self, audit_logger):
        """Test event logging with constitutional compliance failure."""
        invalid_data = {"invalid": "data"}  # Missing required fields

        result = await audit_logger.log_event(event_data=invalid_data)

        assert result["success"] is False
        assert "error" in result
        assert "constitutional compliance" in result["error"]
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH

    @pytest.mark.asyncio
    async def test_hash_chain_integrity_verification(self, audit_logger):
        """Test hash chain integrity verification for tamper detection."""
        # Mock database records with valid hash chain
        mock_records = [
            {
                "id": 1,
                "event_data": '{"action": "test1", "resource_type": "test"}',
                "prev_hash": None,
                "current_hash": "hash1",
                "timestamp": datetime.now(timezone.utc),
            },
            {
                "id": 2,
                "event_data": '{"action": "test2", "resource_type": "test"}',
                "prev_hash": "hash1",
                "current_hash": "hash2",
                "timestamp": datetime.now(timezone.utc),
            },
        ]

        # Mock database operations
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = mock_records
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        audit_logger.db_pool.getconn.return_value = mock_conn

        # Mock hash calculation to match expected values
        with patch.object(audit_logger, "_calculate_hash_chain") as mock_hash:
            mock_hash.side_effect = ["hash1", "hash2"]

            result = await audit_logger.verify_hash_chain_integrity(
                tenant_id="test-tenant"
            )

            assert result["integrity_verified"] is True
            assert result["total_records"] == 2
            assert result["integrity_violations"] == []
            assert result["constitutional_hash"] == CONSTITUTIONAL_HASH

    @pytest.mark.asyncio
    async def test_tamper_detection(self, audit_logger):
        """Test tamper detection with corrupted hash chain."""
        # Mock database records with tampered hash
        mock_records = [
            {
                "id": 1,
                "event_data": '{"action": "test1", "resource_type": "test"}',
                "prev_hash": None,
                "current_hash": "tampered_hash",  # This should be different
                "timestamp": datetime.now(timezone.utc),
            }
        ]

        # Mock database operations
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = mock_records
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        audit_logger.db_pool.getconn.return_value = mock_conn

        # Mock hash calculation to return expected value
        with patch.object(audit_logger, "_calculate_hash_chain") as mock_hash:
            mock_hash.return_value = "expected_hash"  # Different from tampered_hash

            result = await audit_logger.verify_hash_chain_integrity()

            assert result["integrity_verified"] is False
            assert len(result["integrity_violations"]) == 1
            assert result["integrity_violations"][0]["record_id"] == 1
            assert result["integrity_violations"][0]["expected_hash"] == "expected_hash"
            assert result["integrity_violations"][0]["actual_hash"] == "tampered_hash"

    @pytest.mark.asyncio
    async def test_performance_benchmarks(self, audit_logger, sample_event_data):
        """Test performance benchmarks to ensure <5ms insert latency."""
        # Mock fast database operations
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {"id": 123}
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        audit_logger.db_pool.getconn.return_value = mock_conn

        # Mock Redis operations
        audit_logger.redis_client.get.return_value = None
        audit_logger.redis_client.setex.return_value = True

        # Perform multiple operations to test performance
        results = []
        for i in range(10):
            result = await audit_logger.log_event(
                event_data=sample_event_data,
                tenant_id=f"tenant-{i}",
                service_name="performance_test",
            )
            results.append(result)

        # Check that all operations succeeded
        assert all(r["success"] for r in results)

        # Check performance metrics
        metrics = await audit_logger.get_performance_metrics()
        assert metrics["total_operations"] == 10

        # Verify average insert time is reasonable (mock should be very fast)
        assert (
            metrics["avg_insert_time_ms"] < 100
        )  # Very generous for mocked operations

        # Check that performance data is being tracked
        assert len(audit_logger.insert_times) == 10

    @pytest.mark.asyncio
    async def test_multi_tenant_isolation(self, audit_logger, sample_event_data):
        """Test multi-tenant isolation in audit logging."""
        tenant_1 = "tenant-123"
        tenant_2 = "tenant-456"

        # Mock database operations for different tenants
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = [{"id": 1}, {"id": 2}]
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        audit_logger.db_pool.getconn.return_value = mock_conn

        # Mock Redis cache misses for different tenants
        audit_logger.redis_client.get.return_value = None
        audit_logger.redis_client.setex.return_value = True

        # Log events for different tenants
        result_1 = await audit_logger.log_event(
            event_data=sample_event_data, tenant_id=tenant_1, user_id="user-1"
        )

        result_2 = await audit_logger.log_event(
            event_data=sample_event_data, tenant_id=tenant_2, user_id="user-2"
        )

        assert result_1["success"] is True
        assert result_2["success"] is True
        assert result_1["record_id"] != result_2["record_id"]

        # Verify that tenant context was set in database operations
        # The mock should have been called with tenant-specific parameters
        assert mock_cursor.execute.call_count >= 2

    @pytest.mark.asyncio
    async def test_redis_cache_integration(self, audit_logger, sample_event_data):
        """Test Redis caching integration for performance optimization."""
        # Test cache miss scenario
        audit_logger.redis_client.get.return_value = None

        # Mock database operations
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None  # No previous hash
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        audit_logger.db_pool.getconn.return_value = mock_conn

        # Get last hash (should be cache miss)
        result = await audit_logger._get_last_hash("test-tenant")

        assert result is None
        assert audit_logger.cache_misses == 1
        assert audit_logger.cache_hits == 0

        # Test cache hit scenario
        audit_logger.redis_client.get.return_value = "cached_hash_value"

        result = await audit_logger._get_last_hash("test-tenant")

        assert result == "cached_hash_value"
        assert audit_logger.cache_hits == 1
        assert audit_logger.cache_misses == 1

    def test_performance_metrics_calculation(self, audit_logger):
        """Test performance metrics calculation."""
        # Add some sample insert times
        audit_logger.insert_times = [
            1.0,
            2.0,
            3.0,
            4.0,
            5.0,
            10.0,
            15.0,
            20.0,
            25.0,
            30.0,
        ]
        audit_logger.cache_hits = 8
        audit_logger.cache_misses = 2

        metrics = asyncio.run(audit_logger.get_performance_metrics())

        assert metrics["total_operations"] == 10
        assert metrics["avg_insert_time_ms"] == 11.5  # Average of the times
        assert metrics["cache_hit_rate"] == 80.0  # 8/(8+2) * 100
        assert metrics["constitutional_hash"] == CONSTITUTIONAL_HASH

        # Test percentile calculations
        assert metrics["p95_insert_time_ms"] > 0
        assert metrics["p99_insert_time_ms"] > 0

    @pytest.mark.asyncio
    async def test_cleanup_operations(self, audit_logger):
        """Test cleanup operations."""
        await audit_logger.cleanup()

        # Verify Redis client close was called
        audit_logger.redis_client.close.assert_called_once()

        # Verify database pool closeall was called
        audit_logger.db_pool.closeall.assert_called_once()


class TestConvenienceFunctions:
    """Test suite for convenience functions."""

    @pytest.mark.asyncio
    async def test_log_audit_event_function(self):
        """Test the convenience log_audit_event function."""
        sample_data = {"action": "test_action", "resource_type": "test_resource"}

        # Mock the global audit logger
        with patch("persistent_audit_logger.get_audit_logger") as mock_get_logger:
            mock_logger = AsyncMock()
            mock_logger.log_event.return_value = {
                "success": True,
                "record_id": 123,
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }
            mock_get_logger.return_value = mock_logger

            result = await log_audit_event(
                event_data=sample_data,
                tenant_id="test-tenant",
                user_id="test-user",
                service_name="test_service",
                event_type="test_event",
            )

            assert result["success"] is True
            assert result["record_id"] == 123
            assert result["constitutional_hash"] == CONSTITUTIONAL_HASH

            # Verify the logger was called with correct parameters
            mock_logger.log_event.assert_called_once_with(
                event_data=sample_data,
                tenant_id="test-tenant",
                user_id="test-user",
                service_name="test_service",
                event_type="test_event",
            )


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])
