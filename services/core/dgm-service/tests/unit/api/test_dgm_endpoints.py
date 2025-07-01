"""
Unit tests for DGM API endpoints.

Comprehensive test suite for DGM service REST API endpoints including
improvement requests, performance monitoring, and archive management.
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import status


@pytest.mark.unit
@pytest.mark.api
class TestDGMEndpoints:
    """Test suite for DGM API endpoints."""

    @pytest.fixture
    def mock_dgm_dependencies(self):
        """Mock DGM service dependencies."""
        with patch.multiple(
            "dgm_service.api.v1.dgm",
            get_dgm_engine=MagicMock(),
            get_performance_monitor=MagicMock(),
            get_archive_manager=MagicMock(),
            get_current_user=MagicMock(),
        ) as mocks:
            # Setup mock returns
            mocks["get_dgm_engine"].return_value = AsyncMock()
            mocks["get_performance_monitor"].return_value = AsyncMock()
            mocks["get_archive_manager"].return_value = AsyncMock()
            mocks["get_current_user"].return_value = {
                "user_id": str(uuid4()),
                "username": "test_user",
                "permissions": ["dgm:read", "dgm:write", "dgm:execute"],
            }
            yield mocks

    async def test_create_improvement_request_success(
        self, async_test_client, mock_dgm_dependencies
    ):
        """Test successful improvement request creation."""
        # Setup mock DGM engine
        dgm_engine = mock_dgm_dependencies["get_dgm_engine"].return_value
        dgm_engine.generate_improvement_proposal.return_value = {
            "strategy": "performance_optimization",
            "target_services": ["gs-service"],
            "priority": "medium",
            "expected_improvement": 0.15,
            "risk_assessment": {"risk_level": "low", "confidence": 0.85},
        }

        request_data = {
            "target_services": ["gs-service"],
            "priority": "medium",
            "strategy_hint": "performance_optimization",
            "constraints": {"max_risk_level": "medium", "max_execution_time": 300},
        }

        response = await async_test_client.post(
            "/api/v1/dgm/improve", json=request_data
        )

        assert response.status_code == status.HTTP_200_OK

        response_data = response.json()
        assert response_data["strategy"] == "performance_optimization"
        assert response_data["target_services"] == ["gs-service"]
        assert response_data["expected_improvement"] == 0.15

        # Verify DGM engine was called
        dgm_engine.generate_improvement_proposal.assert_called_once()

    async def test_create_improvement_request_validation_error(
        self, async_test_client, mock_dgm_dependencies
    ):
        """Test improvement request with validation errors."""
        invalid_request = {
            "target_services": [],  # Empty list should be invalid
            "priority": "invalid_priority",  # Invalid priority
            "constraints": {
                "max_execution_time": -100
            },  # Negative time should be invalid
        }

        response = await async_test_client.post(
            "/api/v1/dgm/improve", json=invalid_request
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_execute_improvement_success(
        self, async_test_client, mock_dgm_dependencies
    ):
        """Test successful improvement execution."""
        improvement_id = str(uuid4())

        # Setup mock DGM engine
        dgm_engine = mock_dgm_dependencies["get_dgm_engine"].return_value
        dgm_engine.execute_improvement.return_value = {
            "success": True,
            "improvement_metrics": {"overall_improvement": 0.12},
            "performance_before": {"response_time": 150.0},
            "performance_after": {"response_time": 125.0},
            "execution_time": 45.2,
        }

        # Mock archive manager
        archive_manager = mock_dgm_dependencies["get_archive_manager"].return_value
        archive_manager.get_improvement.return_value = {
            "id": improvement_id,
            "strategy": "performance_optimization",
            "status": "approved",
            "proposal": {
                "target_services": ["gs-service"],
                "proposed_changes": {"type": "algorithm_optimization"},
            },
        }

        response = await async_test_client.post(f"/api/v1/dgm/execute/{improvement_id}")

        assert response.status_code == status.HTTP_200_OK

        response_data = response.json()
        assert response_data["success"] is True
        assert response_data["improvement_metrics"]["overall_improvement"] == 0.12

        # Verify execution was called
        dgm_engine.execute_improvement.assert_called_once()

    async def test_execute_improvement_not_found(
        self, async_test_client, mock_dgm_dependencies
    ):
        """Test execution of non-existent improvement."""
        improvement_id = str(uuid4())

        # Mock archive manager to return None
        archive_manager = mock_dgm_dependencies["get_archive_manager"].return_value
        archive_manager.get_improvement.return_value = None

        response = await async_test_client.post(f"/api/v1/dgm/execute/{improvement_id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_improvement_status(
        self, async_test_client, mock_dgm_dependencies
    ):
        """Test improvement status retrieval."""
        improvement_id = str(uuid4())

        # Mock archive manager
        archive_manager = mock_dgm_dependencies["get_archive_manager"].return_value
        archive_manager.get_improvement.return_value = {
            "id": improvement_id,
            "strategy": "performance_optimization",
            "status": "completed",
            "created_at": datetime.utcnow().isoformat(),
            "completed_at": (datetime.utcnow() + timedelta(minutes=5)).isoformat(),
            "performance_metrics": {
                "overall_improvement": 0.12,
                "execution_time": 45.2,
            },
        }

        response = await async_test_client.get(
            f"/api/v1/dgm/improvements/{improvement_id}"
        )

        assert response.status_code == status.HTTP_200_OK

        response_data = response.json()
        assert response_data["id"] == improvement_id
        assert response_data["strategy"] == "performance_optimization"
        assert response_data["status"] == "completed"

    async def test_list_improvements(self, async_test_client, mock_dgm_dependencies):
        """Test improvement listing with pagination."""
        # Mock archive manager
        archive_manager = mock_dgm_dependencies["get_archive_manager"].return_value
        archive_manager.list_improvements.return_value = {
            "improvements": [
                {
                    "id": str(uuid4()),
                    "strategy": "performance_optimization",
                    "status": "completed",
                    "created_at": datetime.utcnow().isoformat(),
                },
                {
                    "id": str(uuid4()),
                    "strategy": "code_refactoring",
                    "status": "in_progress",
                    "created_at": datetime.utcnow().isoformat(),
                },
            ],
            "total": 2,
            "page": 1,
            "per_page": 10,
        }

        response = await async_test_client.get(
            "/api/v1/dgm/improvements?page=1&per_page=10"
        )

        assert response.status_code == status.HTTP_200_OK

        response_data = response.json()
        assert len(response_data["improvements"]) == 2
        assert response_data["total"] == 2
        assert response_data["page"] == 1

    async def test_rollback_improvement(self, async_test_client, mock_dgm_dependencies):
        """Test improvement rollback."""
        improvement_id = str(uuid4())

        # Mock DGM engine
        dgm_engine = mock_dgm_dependencies["get_dgm_engine"].return_value
        dgm_engine.rollback_improvement.return_value = {
            "success": True,
            "rollback_time": 15.3,
            "restored_state": "baseline",
            "performance_after_rollback": {"response_time": 150.0},
        }

        # Mock archive manager
        archive_manager = mock_dgm_dependencies["get_archive_manager"].return_value
        archive_manager.get_improvement.return_value = {
            "id": improvement_id,
            "status": "completed",
            "can_rollback": True,
        }

        rollback_request = {
            "reason": "Performance degradation detected",
            "force": False,
        }

        response = await async_test_client.post(
            f"/api/v1/dgm/rollback/{improvement_id}", json=rollback_request
        )

        assert response.status_code == status.HTTP_200_OK

        response_data = response.json()
        assert response_data["success"] is True
        assert response_data["rollback_time"] == 15.3

    async def test_get_performance_metrics(
        self, async_test_client, mock_dgm_dependencies
    ):
        """Test performance metrics retrieval."""
        # Mock performance monitor
        performance_monitor = mock_dgm_dependencies[
            "get_performance_monitor"
        ].return_value
        performance_monitor.query_metrics.return_value = {
            "data_points": [
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "value": 125.5,
                    "tags": {"endpoint": "/api/v1/dgm/improve"},
                }
            ],
            "summary": {"average": 125.5, "min": 95.0, "max": 180.0, "count": 100},
        }

        query_params = {
            "metric_name": "response_time",
            "start_time": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
            "end_time": datetime.utcnow().isoformat(),
            "aggregation": "avg",
        }

        response = await async_test_client.get(
            "/api/v1/dgm/metrics", params=query_params
        )

        assert response.status_code == status.HTTP_200_OK

        response_data = response.json()
        assert "data_points" in response_data
        assert "summary" in response_data
        assert response_data["summary"]["average"] == 125.5

    async def test_get_performance_report(
        self, async_test_client, mock_dgm_dependencies
    ):
        """Test performance report generation."""
        # Mock performance monitor
        performance_monitor = mock_dgm_dependencies[
            "get_performance_monitor"
        ].return_value
        performance_monitor.generate_report.return_value = {
            "period_start": (datetime.utcnow() - timedelta(days=7)).isoformat(),
            "period_end": datetime.utcnow().isoformat(),
            "metrics": {
                "response_time": {"avg": 125.0, "trend": "improving"},
                "throughput": {"avg": 850.0, "trend": "stable"},
                "error_rate": {"avg": 0.002, "trend": "improving"},
            },
            "summary": {
                "overall_performance": "good",
                "key_insights": ["Response time improved by 15%"],
            },
            "trends": {"performance_trend": "positive", "stability_trend": "stable"},
        }

        response = await async_test_client.get(
            "/api/v1/dgm/performance?days=7&service_name=dgm-service"
        )

        assert response.status_code == status.HTTP_200_OK

        response_data = response.json()
        assert "metrics" in response_data
        assert "summary" in response_data
        assert "trends" in response_data
        assert response_data["metrics"]["response_time"]["avg"] == 125.0

    async def test_get_bandit_statistics(
        self, async_test_client, mock_dgm_dependencies
    ):
        """Test bandit algorithm statistics retrieval."""
        # Mock DGM engine
        dgm_engine = mock_dgm_dependencies["get_dgm_engine"].return_value
        dgm_engine.get_bandit_statistics.return_value = {
            "algorithm_type": "UCB1",
            "total_pulls": 150,
            "arms": {
                "performance_optimization": {
                    "pulls": 75,
                    "rewards": 58.5,
                    "success_rate": 0.78,
                    "average_reward": 0.78,
                },
                "code_refactoring": {
                    "pulls": 45,
                    "rewards": 32.4,
                    "success_rate": 0.72,
                    "average_reward": 0.72,
                },
                "architecture_improvement": {
                    "pulls": 30,
                    "rewards": 24.0,
                    "success_rate": 0.80,
                    "average_reward": 0.80,
                },
            },
            "exploration_parameter": 1.414,
            "last_updated": datetime.utcnow().isoformat(),
        }

        response = await async_test_client.get("/api/v1/dgm/bandit/stats")

        assert response.status_code == status.HTTP_200_OK

        response_data = response.json()
        assert response_data["algorithm_type"] == "UCB1"
        assert response_data["total_pulls"] == 150
        assert len(response_data["arms"]) == 3
        assert "performance_optimization" in response_data["arms"]

    async def test_unauthorized_access(self, async_test_client):
        """Test unauthorized access to protected endpoints."""
        # Mock authentication failure
        with patch("dgm_service.api.v1.dgm.get_current_user") as mock_auth:
            mock_auth.side_effect = Exception("Unauthorized")

            response = await async_test_client.post(
                "/api/v1/dgm/improve", json={"target_services": ["gs-service"]}
            )

            assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_insufficient_permissions(
        self, async_test_client, mock_dgm_dependencies
    ):
        """Test access with insufficient permissions."""
        # Mock user with limited permissions
        mock_dgm_dependencies["get_current_user"].return_value = {
            "user_id": str(uuid4()),
            "username": "limited_user",
            "permissions": ["dgm:read"],  # No write or execute permissions
        }

        with patch("dgm_service.api.v1.dgm.require_permission") as mock_perm:
            mock_perm.side_effect = Exception("Insufficient permissions")

            response = await async_test_client.post(
                "/api/v1/dgm/improve", json={"target_services": ["gs-service"]}
            )

            assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_rate_limiting(self, async_test_client, mock_dgm_dependencies):
        """Test API rate limiting."""
        # Mock rate limiter
        with patch("dgm_service.api.v1.dgm.rate_limiter") as mock_limiter:
            mock_limiter.side_effect = Exception("Rate limit exceeded")

            response = await async_test_client.post(
                "/api/v1/dgm/improve", json={"target_services": ["gs-service"]}
            )

            assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS

    async def test_internal_server_error_handling(
        self, async_test_client, mock_dgm_dependencies
    ):
        """Test internal server error handling."""
        # Mock DGM engine failure
        dgm_engine = mock_dgm_dependencies["get_dgm_engine"].return_value
        dgm_engine.generate_improvement_proposal.side_effect = Exception(
            "Internal error"
        )

        response = await async_test_client.post(
            "/api/v1/dgm/improve", json={"target_services": ["gs-service"]}
        )

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    async def test_request_validation_edge_cases(
        self, async_test_client, mock_dgm_dependencies
    ):
        """Test request validation edge cases."""
        # Test with maximum allowed values
        large_request = {
            "target_services": ["service-" + str(i) for i in range(10)],  # Max services
            "priority": "critical",
            "strategy_hint": "performance_optimization",
            "constraints": {
                "max_risk_level": "high",
                "max_execution_time": 3600,  # 1 hour
                "rollback_threshold": -0.5,
            },
            "metadata": {
                "key_" + str(i): f"value_{i}" for i in range(20)
            },  # Large metadata
        }

        # Mock successful processing
        dgm_engine = mock_dgm_dependencies["get_dgm_engine"].return_value
        dgm_engine.generate_improvement_proposal.return_value = {
            "strategy": "performance_optimization",
            "target_services": large_request["target_services"],
            "expected_improvement": 0.25,
        }

        response = await async_test_client.post(
            "/api/v1/dgm/improve", json=large_request
        )

        assert response.status_code == status.HTTP_200_OK

    async def test_concurrent_requests_handling(
        self, async_test_client, mock_dgm_dependencies
    ):
        """Test handling of concurrent API requests."""
        import asyncio

        # Mock DGM engine
        dgm_engine = mock_dgm_dependencies["get_dgm_engine"].return_value
        dgm_engine.generate_improvement_proposal.return_value = {
            "strategy": "performance_optimization",
            "target_services": ["gs-service"],
            "expected_improvement": 0.15,
        }

        # Create multiple concurrent requests
        request_data = {"target_services": ["gs-service"], "priority": "medium"}

        tasks = [
            async_test_client.post("/api/v1/dgm/improve", json=request_data)
            for _ in range(10)
        ]

        responses = await asyncio.gather(*tasks)

        # Verify all requests were processed successfully
        assert all(response.status_code == status.HTTP_200_OK for response in responses)

        # Verify DGM engine was called for each request
        assert dgm_engine.generate_improvement_proposal.call_count == 10
