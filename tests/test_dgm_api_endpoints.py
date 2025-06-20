"""
Test suite for DGM API endpoints.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from fastapi.testclient import TestClient
from fastapi import status

from services.core.dgm_service.dgm_service.main import app


class TestDGMAPIEndpoints:
    """Test suite for DGM API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def mock_dgm_engine(self):
        """Create mock DGM engine."""
        mock_engine = AsyncMock()
        mock_engine.get_status.return_value = {
            "status": "operational",
            "uptime_seconds": 3600,
            "active_improvements": 2,
            "constitutional_compliance_score": 0.95,
            "system_health": {"status": "healthy"},
            "last_optimization": datetime.utcnow()
        }
        mock_engine.start_improvement.return_value = {
            "improvement_id": str(uuid4()),
            "status": "started",
            "estimated_completion": datetime.utcnow() + timedelta(hours=1)
        }
        return mock_engine
    
    @pytest.fixture
    def mock_performance_monitor(self):
        """Create mock performance monitor."""
        mock_monitor = AsyncMock()
        mock_monitor.get_current_metrics.return_value = {
            "response_time_avg": 150.5,
            "throughput": 1000,
            "error_rate": 0.01
        }
        mock_monitor.query_metrics.return_value = {
            "data_points": [
                {"timestamp": "2025-01-20T12:00:00Z", "value": 150.0},
                {"timestamp": "2025-01-20T12:01:00Z", "value": 155.0}
            ],
            "summary": {"avg": 152.5, "min": 150.0, "max": 155.0}
        }
        mock_monitor.get_metrics_summary.return_value = {
            "metrics": {"response_time": 150.5},
            "trends": {"response_time": "stable"},
            "alerts": [],
            "constitutional_compliance_score": 0.95
        }
        return mock_monitor
    
    @pytest.fixture
    def mock_archive_manager(self):
        """Create mock archive manager."""
        mock_manager = AsyncMock()
        mock_manager.get_statistics.return_value = {
            "total_improvements": 100,
            "successful_improvements": 85,
            "failed_improvements": 15
        }
        return mock_manager
    
    @pytest.fixture
    def mock_bandit_manager(self):
        """Create mock bandit manager."""
        mock_manager = AsyncMock()
        mock_manager.select_arm.return_value = {
            "selected_arm": "code_optimization",
            "confidence": 0.85,
            "expected_reward": 0.75,
            "exploration_factor": 0.1,
            "safety_validated": True,
            "constitutional_compliance": True
        }
        mock_manager.update_reward.return_value = {
            "success": True,
            "updated_stats": {"total_pulls": 11, "average_reward": 0.8}
        }
        return mock_manager
    
    def test_get_dgm_status(self, client, mock_dgm_engine, mock_performance_monitor, mock_archive_manager):
        """Test DGM status endpoint."""
        with patch('services.core.dgm_service.dgm_service.api.v1.dgm.get_dgm_engine', return_value=mock_dgm_engine), \
             patch('services.core.dgm_service.dgm_service.api.v1.dgm.get_performance_monitor', return_value=mock_performance_monitor), \
             patch('services.core.dgm_service.dgm_service.api.v1.dgm.get_archive_manager', return_value=mock_archive_manager):
            
            response = client.get("/api/v1/dgm/status")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            
            assert data["status"] == "operational"
            assert data["version"] == "1.0.0"
            assert data["active_improvements"] == 2
            assert data["total_improvements"] == 100
            assert data["success_rate"] == 85.0
            assert data["constitutional_compliance_score"] == 0.95
            assert "performance_metrics" in data
            assert "system_health" in data
    
    def test_trigger_improvement(self, client, mock_dgm_engine):
        """Test improvement trigger endpoint."""
        with patch('services.core.dgm_service.dgm_service.api.v1.dgm.get_dgm_engine', return_value=mock_dgm_engine):
            
            improvement_request = {
                "target_service": "dgm-service",
                "improvement_type": "code_optimization",
                "priority": "medium",
                "description": "Optimize query performance",
                "safety_threshold": 0.8
            }
            
            response = client.post("/api/v1/dgm/improve", json=improvement_request)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            
            assert "improvement_id" in data
            assert data["status"] == "started"
            assert data["safety_score"] >= 0.8
            assert data["constitutional_compliance_score"] >= 0.8
            assert "estimated_completion_time" in data
    
    def test_select_bandit_arm(self, client, mock_bandit_manager):
        """Test bandit arm selection endpoint."""
        with patch('services.core.dgm_service.dgm_service.api.v1.dgm.get_bandit_manager', return_value=mock_bandit_manager):
            
            bandit_request = {
                "context_key": "improvement_context",
                "algorithm_type": "conservative_bandit",
                "exploration_rate": 0.1,
                "safety_threshold": 0.8
            }
            
            response = client.post("/api/v1/dgm/bandit/select-arm", json=bandit_request)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            
            assert data["selected_arm"] == "code_optimization"
            assert data["confidence"] == 0.85
            assert data["expected_reward"] == 0.75
            assert data["safety_validated"] is True
            assert data["constitutional_compliance"] is True
    
    def test_provide_reward_feedback(self, client, mock_bandit_manager):
        """Test reward feedback endpoint."""
        with patch('services.core.dgm_service.dgm_service.api.v1.dgm.get_bandit_manager', return_value=mock_bandit_manager):
            
            feedback_request = {
                "context_key": "improvement_context",
                "arm_id": "code_optimization",
                "reward": 0.9,
                "metadata": {"execution_time": 120}
            }
            
            response = client.post("/api/v1/dgm/bandit/reward-feedback", json=feedback_request)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            
            assert data["success"] is True
            assert "message" in data
            assert "updated_stats" in data
    
    def test_query_performance_metrics(self, client, mock_performance_monitor):
        """Test performance metrics query endpoint."""
        with patch('services.core.dgm_service.dgm_service.api.v1.dgm.get_performance_monitor', return_value=mock_performance_monitor):
            
            metrics_request = {
                "metric_name": "response_time",
                "start_time": "2025-01-20T12:00:00Z",
                "end_time": "2025-01-20T13:00:00Z",
                "aggregation": "avg"
            }
            
            response = client.post("/api/v1/dgm/metrics/query", json=metrics_request)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            
            assert data["metric_name"] == "response_time"
            assert data["aggregation"] == "avg"
            assert "data_points" in data
            assert "summary" in data
            assert data["constitutional_compliance"] is True
    
    def test_get_metrics_summary(self, client, mock_performance_monitor):
        """Test metrics summary endpoint."""
        with patch('services.core.dgm_service.dgm_service.api.v1.dgm.get_performance_monitor', return_value=mock_performance_monitor):
            
            response = client.get("/api/v1/dgm/metrics/summary?hours=24")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            
            assert data["time_period"]["hours"] == 24
            assert "metrics" in data
            assert "trends" in data
            assert "alerts" in data
            assert "constitutional_compliance_score" in data
    
    def test_optimize_database(self, client):
        """Test database optimization endpoint."""
        mock_optimizer = AsyncMock()
        mock_optimizer.optimize_database.return_value = {
            "status": "completed",
            "optimizations_applied": ["index_creation", "vacuum_tuning"],
            "performance_improvement": {"query_time_reduction": 25.0},
            "recommendations": ["Consider partitioning large tables"],
            "duration_seconds": 120.5
        }
        
        with patch('services.core.dgm_service.dgm_service.api.v1.dgm.get_performance_optimizer', return_value=mock_optimizer):
            
            response = client.post("/api/v1/dgm/optimize/database")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            
            assert data["status"] == "completed"
            assert "optimization_id" in data
            assert "optimizations_applied" in data
            assert "performance_improvement" in data
            assert "recommendations" in data
            assert data["constitutional_compliance"] is True
    
    def test_get_cache_statistics(self, client):
        """Test cache statistics endpoint."""
        mock_cache_manager = AsyncMock()
        mock_cache_manager.get_stats.return_value = {
            "memory_cache": {"size": 750, "max_size": 1000, "utilization": 75.0},
            "redis_cache": {"available": True, "memory_usage": "256MB"},
            "metrics": {"hits": 8500, "misses": 1500, "hit_rate": 85.0},
            "constitutional_compliance": {"hash": "cdd01ef066bc6cf2", "validated": True}
        }
        
        with patch('services.core.dgm_service.dgm_service.api.v1.dgm.get_cache_manager', return_value=mock_cache_manager):
            
            response = client.get("/api/v1/dgm/cache/stats")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            
            assert "memory_cache" in data
            assert "redis_cache" in data
            assert "metrics" in data
            assert data["metrics"]["hit_rate"] == 85.0
    
    def test_clear_cache(self, client):
        """Test cache clear endpoint."""
        mock_cache_manager = AsyncMock()
        mock_cache_manager.clear.return_value = 150
        
        with patch('services.core.dgm_service.dgm_service.api.v1.dgm.get_cache_manager', return_value=mock_cache_manager):
            
            response = client.post("/api/v1/dgm/cache/clear?pattern=dgm:metrics:*")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            
            assert data["success"] is True
            assert data["cleared_count"] == 150
            assert data["pattern"] == "dgm:metrics:*"
    
    def test_invalid_improvement_type(self, client):
        """Test invalid improvement type validation."""
        improvement_request = {
            "target_service": "dgm-service",
            "improvement_type": "invalid_type",
            "priority": "medium"
        }
        
        response = client.post("/api/v1/dgm/improve", json=improvement_request)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_invalid_bandit_algorithm(self, client):
        """Test invalid bandit algorithm validation."""
        bandit_request = {
            "context_key": "test_context",
            "algorithm_type": "invalid_algorithm"
        }
        
        response = client.post("/api/v1/dgm/bandit/select-arm", json=bandit_request)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_service_unavailable_error(self, client):
        """Test service unavailable error handling."""
        with patch('services.core.dgm_service.dgm_service.api.v1.dgm.get_performance_optimizer', return_value=None):
            
            response = client.post("/api/v1/dgm/optimize/database")
            
            assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
            assert "not available" in response.json()["detail"]


class TestConstitutionalAPIEndpoints:
    """Test suite for constitutional compliance API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def mock_constitutional_validator(self):
        """Create mock constitutional validator."""
        mock_validator = AsyncMock()
        mock_validator.get_compliance_status.return_value = {
            "compliance_score": 0.95,
            "last_validation": datetime.utcnow(),
            "total_validations": 100,
            "violation_count": 2,
            "system_health": "healthy"
        }
        mock_validator.validate_content.return_value = {
            "is_compliant": True,
            "compliance_score": 0.92,
            "violations": [],
            "recommendations": ["Consider additional safety checks"],
            "assessment_details": {"method": "automated", "confidence": 0.95}
        }
        return mock_validator
    
    def test_get_compliance_status(self, client, mock_constitutional_validator):
        """Test compliance status endpoint."""
        with patch('services.core.dgm_service.dgm_service.api.v1.constitutional.get_constitutional_validator', 
                   return_value=mock_constitutional_validator):
            
            response = client.get("/api/v1/constitutional/compliance/status")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            
            assert data["compliance_status"] == "validated"
            assert data["constitutional_hash"] == "cdd01ef066bc6cf2"
            assert data["compliance_score"] == 0.95
            assert data["governance_active"] is True
    
    def test_validate_compliance(self, client, mock_constitutional_validator):
        """Test compliance validation endpoint."""
        with patch('services.core.dgm_service.dgm_service.api.v1.constitutional.get_constitutional_validator', 
                   return_value=mock_constitutional_validator):
            
            validation_request = {
                "content": "Proposed algorithm improvement",
                "context": {"service": "dgm", "type": "optimization"},
                "validation_type": "improvement",
                "strict_mode": True
            }
            
            response = client.post("/api/v1/constitutional/compliance/validate", json=validation_request)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            
            assert "validation_id" in data
            assert data["is_compliant"] is True
            assert data["compliance_score"] == 0.92
            assert data["constitutional_hash"] == "cdd01ef066bc6cf2"
            assert "violations" in data
            assert "recommendations" in data
    
    def test_get_constitutional_hash(self, client):
        """Test constitutional hash endpoint."""
        response = client.get("/api/v1/constitutional/constitutional/hash")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["constitutional_hash"] == "cdd01ef066bc6cf2"
        assert data["hash_algorithm"] == "SHA-256"
        assert data["status"] == "active"
        assert data["version"] == "1.0"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
