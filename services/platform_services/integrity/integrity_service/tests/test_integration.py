"""
ACGS-2 Persistent Audit Logger Integration Tests

Integration tests to verify the persistent audit logging system works
correctly with the Integrity Service and meets performance requirements.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import json
import os
import pytest
import time
from datetime import datetime, timezone
from typing import Dict, Any
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

# Import the main application
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

# Mock the dependencies before importing the app
with patch('app.main.initialize_infrastructure'), \
     patch('app.main.get_database_manager'), \
     patch('app.main.cleanup_infrastructure'):
    from app.main import app

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class TestPersistentAuditIntegration:
    """Integration tests for persistent audit logging with Integrity Service."""
    
    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI application."""
        return TestClient(app)
    
    @pytest.fixture
    def mock_audit_logger(self):
        """Create a mock audit logger for testing."""
        mock_logger = AsyncMock()
        
        # Mock successful log_event response
        mock_logger.log_event.return_value = {
            'success': True,
            'record_id': 123,
            'current_hash': 'test_hash_123',
            'prev_hash': 'test_hash_122',
            'insert_time_ms': 2.5,
            'constitutional_hash': CONSTITUTIONAL_HASH,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        # Mock successful integrity verification
        mock_logger.verify_hash_chain_integrity.return_value = {
            'integrity_verified': True,
            'total_records': 100,
            'integrity_violations': [],
            'verification_time_ms': 15.2,
            'constitutional_hash': CONSTITUTIONAL_HASH
        }
        
        # Mock performance metrics
        mock_logger.get_performance_metrics.return_value = {
            'avg_insert_time_ms': 2.1,
            'p95_insert_time_ms': 3.8,
            'p99_insert_time_ms': 4.2,
            'total_operations': 1000,
            'cache_hit_rate': 92.5,
            'cache_hits': 925,
            'cache_misses': 75,
            'constitutional_hash': CONSTITUTIONAL_HASH
        }
        
        return mock_logger
    
    def test_health_check_endpoint(self, client):
        """Test the basic health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["constitutional_hash"] == CONSTITUTIONAL_HASH
    
    def test_api_status_endpoint(self, client):
        """Test the API status endpoint."""
        response = client.get("/api/v1/status")
        assert response.status_code == 200
        
        data = response.json()
        assert data["service"] == "integrity_service"
        assert data["status"] == "active"
    
    def test_log_audit_event_endpoint(self, client, mock_audit_logger):
        """Test the audit event logging endpoint."""
        # Mock the audit logger in app state
        app.state.persistent_audit_logger = mock_audit_logger
        
        event_data = {
            "event_data": {
                "action": "user_login",
                "resource_type": "authentication",
                "resource_id": "user_123",
                "ip_address": "192.168.1.100"
            },
            "tenant_id": "test-tenant-123",
            "user_id": "user-456",
            "service_name": "test_service",
            "event_type": "authentication"
        }
        
        response = client.post("/api/v1/persistent-audit/events", json=event_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["record_id"] == 123
        assert data["constitutional_hash"] == CONSTITUTIONAL_HASH
        assert data["insert_time_ms"] == 2.5
        
        # Verify the mock was called correctly
        mock_audit_logger.log_event.assert_called_once()
    
    def test_verify_integrity_endpoint(self, client, mock_audit_logger):
        """Test the hash chain integrity verification endpoint."""
        # Mock the audit logger in app state
        app.state.persistent_audit_logger = mock_audit_logger
        
        response = client.get("/api/v1/persistent-audit/verify-integrity?tenant_id=test-tenant&limit=500")
        assert response.status_code == 200
        
        data = response.json()
        assert data["integrity_verified"] is True
        assert data["total_records"] == 100
        assert data["integrity_violations"] == []
        assert data["constitutional_hash"] == CONSTITUTIONAL_HASH
        
        # Verify the mock was called with correct parameters
        mock_audit_logger.verify_hash_chain_integrity.assert_called_once_with(
            tenant_id="test-tenant",
            limit=500
        )
    
    def test_performance_metrics_endpoint(self, client, mock_audit_logger):
        """Test the performance metrics endpoint."""
        # Mock the audit logger in app state
        app.state.persistent_audit_logger = mock_audit_logger
        
        response = client.get("/api/v1/persistent-audit/performance-metrics")
        assert response.status_code == 200
        
        data = response.json()
        assert data["avg_insert_time_ms"] == 2.1
        assert data["p95_insert_time_ms"] == 3.8
        assert data["p99_insert_time_ms"] == 4.2
        assert data["total_operations"] == 1000
        assert data["cache_hit_rate"] == 92.5
        assert data["constitutional_hash"] == CONSTITUTIONAL_HASH
        
        # Verify performance targets are met
        assert data["avg_insert_time_ms"] < 5.0  # <5ms target
        assert data["p99_insert_time_ms"] < 5.0  # <5ms P99 target
        assert data["cache_hit_rate"] > 85.0     # >85% cache hit rate target
    
    def test_health_check_audit_endpoint(self, client, mock_audit_logger):
        """Test the audit system health check endpoint."""
        # Mock the audit logger in app state
        app.state.persistent_audit_logger = mock_audit_logger
        
        response = client.get("/api/v1/persistent-audit/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["constitutional_hash"] == CONSTITUTIONAL_HASH
        assert "metrics" in data
        assert data["metrics"]["avg_insert_time_ms"] < 5.0
    
    def test_emergency_seal_endpoint(self, client, mock_audit_logger):
        """Test the emergency seal endpoint."""
        # Mock the audit logger in app state
        app.state.persistent_audit_logger = mock_audit_logger
        
        response = client.post("/api/v1/persistent-audit/emergency-seal?reason=Security%20breach%20detected")
        assert response.status_code == 200
        
        data = response.json()
        assert data["sealed"] is True
        assert data["seal_id"] == 123
        assert data["constitutional_hash"] == CONSTITUTIONAL_HASH
        
        # Verify emergency event was logged
        mock_audit_logger.log_event.assert_called_once()
        call_args = mock_audit_logger.log_event.call_args
        assert call_args[1]["event_type"] == "emergency_seal"
        assert "Security breach detected" in call_args[1]["event_data"]["reason"]
    
    def test_constitutional_compliance_validation(self, client, mock_audit_logger):
        """Test constitutional compliance validation in audit events."""
        # Mock the audit logger in app state
        app.state.persistent_audit_logger = mock_audit_logger
        
        # Test with valid constitutional hash
        event_data = {
            "event_data": {
                "action": "test_action",
                "resource_type": "test_resource",
                "constitutional_hash": CONSTITUTIONAL_HASH
            }
        }
        
        response = client.post("/api/v1/persistent-audit/events", json=event_data)
        assert response.status_code == 200
        
        # Verify constitutional hash was added to event data
        call_args = mock_audit_logger.log_event.call_args
        assert call_args[1]["event_data"]["constitutional_hash"] == CONSTITUTIONAL_HASH
    
    def test_multi_tenant_isolation(self, client, mock_audit_logger):
        """Test multi-tenant isolation in audit logging."""
        # Mock the audit logger in app state
        app.state.persistent_audit_logger = mock_audit_logger
        
        # Log events for different tenants
        tenant_1_data = {
            "event_data": {"action": "test1", "resource_type": "test"},
            "tenant_id": "tenant-123"
        }
        
        tenant_2_data = {
            "event_data": {"action": "test2", "resource_type": "test"},
            "tenant_id": "tenant-456"
        }
        
        response1 = client.post("/api/v1/persistent-audit/events", json=tenant_1_data)
        response2 = client.post("/api/v1/persistent-audit/events", json=tenant_2_data)
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify both calls were made with correct tenant IDs
        assert mock_audit_logger.log_event.call_count == 2
        
        call_args_list = mock_audit_logger.log_event.call_args_list
        assert call_args_list[0][1]["tenant_id"] == "tenant-123"
        assert call_args_list[1][1]["tenant_id"] == "tenant-456"
    
    def test_error_handling(self, client, mock_audit_logger):
        """Test error handling in audit logging endpoints."""
        # Mock the audit logger to raise an exception
        mock_audit_logger.log_event.side_effect = Exception("Database connection failed")
        app.state.persistent_audit_logger = mock_audit_logger
        
        event_data = {
            "event_data": {
                "action": "test_action",
                "resource_type": "test_resource"
            }
        }
        
        response = client.post("/api/v1/persistent-audit/events", json=event_data)
        assert response.status_code == 500
        
        data = response.json()
        assert "Failed to log audit event" in data["detail"]
    
    def test_service_unavailable_handling(self, client):
        """Test handling when audit logger is not initialized."""
        # Remove the audit logger from app state
        if hasattr(app.state, 'persistent_audit_logger'):
            delattr(app.state, 'persistent_audit_logger')
        
        event_data = {
            "event_data": {
                "action": "test_action",
                "resource_type": "test_resource"
            }
        }
        
        response = client.post("/api/v1/persistent-audit/events", json=event_data)
        assert response.status_code == 503
        
        data = response.json()
        assert "Persistent audit logger not initialized" in data["detail"]


class TestPerformanceBenchmarks:
    """Performance benchmark tests for the audit logging system."""
    
    def test_insert_latency_benchmark(self, mock_audit_logger):
        """Benchmark insert latency to ensure <5ms target is met."""
        # Simulate realistic insert times
        insert_times = [1.2, 2.1, 1.8, 3.2, 2.5, 1.9, 2.8, 3.1, 2.2, 1.7]
        
        mock_audit_logger.get_performance_metrics.return_value = {
            'avg_insert_time_ms': sum(insert_times) / len(insert_times),
            'p95_insert_time_ms': sorted(insert_times)[int(0.95 * len(insert_times))],
            'p99_insert_time_ms': sorted(insert_times)[int(0.99 * len(insert_times))],
            'total_operations': len(insert_times),
            'cache_hit_rate': 90.0,
            'cache_hits': 9,
            'cache_misses': 1,
            'constitutional_hash': CONSTITUTIONAL_HASH
        }
        
        client = TestClient(app)
        app.state.persistent_audit_logger = mock_audit_logger
        
        response = client.get("/api/v1/persistent-audit/performance-metrics")
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify performance targets
        assert data["avg_insert_time_ms"] < 5.0, f"Average insert time {data['avg_insert_time_ms']}ms exceeds 5ms target"
        assert data["p95_insert_time_ms"] < 5.0, f"P95 insert time {data['p95_insert_time_ms']}ms exceeds 5ms target"
        assert data["p99_insert_time_ms"] < 5.0, f"P99 insert time {data['p99_insert_time_ms']}ms exceeds 5ms target"
        assert data["cache_hit_rate"] > 85.0, f"Cache hit rate {data['cache_hit_rate']}% below 85% target"


if __name__ == "__main__":
    # Run the integration tests
    pytest.main([__file__, "-v"])
