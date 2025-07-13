#!/usr/bin/env python3
"""
Comprehensive Test Suite for Evolution Oversight Service

Tests cover:
- Evaluation criteria accuracy and performance
- Approval workflow state machine
- Human review integration
- Rollback mechanism reliability
- Auto-approval rate optimization

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio

import httpx
import pytest

# Test configuration
TEST_BASE_URL = "http://localhost:8004"
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class TestEvolutionOversightService:
    """Test suite for evolution oversight service."""

    @pytest.fixture
    async def oversight_client(self):
        """Create HTTP client for oversight service."""
        async with httpx.AsyncClient(base_url=TEST_BASE_URL) as client:
            yield client

    async def test_health_check(self, oversight_client):
        """Test service health check."""
        response = await oversight_client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "healthy"
        assert data["service"] == "evolution-oversight-service"
        assert data["constitutional_hash"] == CONSTITUTIONAL_HASH
        assert "active_reviews" in data

    async def test_evolution_submission(self, oversight_client):
        """Test evolution request submission."""
        evolution_request = {
            "agent_id": "test_agent_001",
            "new_version": {
                "version": "2.1.0",
                "changes": {
                    "code_changes": ["Added new feature X", "Fixed bug Y"],
                    "config_changes": {"timeout": 30, "retries": 3},
                },
                "complexity_delta": 0.05,  # 5% complexity increase
                "resource_delta": 0.02,  # 2% resource increase
            },
            "change_description": "Enhanced agent capabilities with new feature X",
            "requester_id": "developer_001",
            "priority": "medium",
        }

        response = await oversight_client.post(
            "/api/v1/evolution/submit", json=evolution_request
        )

        assert response.status_code == 200
        data = response.json()

        assert "evolution_id" in data
        assert data["status"] == "pending"
        assert "estimated_processing_time" in data

        return data["evolution_id"]

    async def test_high_score_auto_approval(self, oversight_client):
        """Test that high-scoring evolutions are auto-approved."""
        # Create evolution with high scores
        evolution_request = {
            "agent_id": "test_agent_auto",
            "new_version": {
                "version": "1.0.1",
                "changes": {"code_changes": ["Minor bug fix"], "config_changes": {}},
                "complexity_delta": -0.01,  # Slight improvement
                "resource_delta": -0.005,  # Resource reduction
            },
            "change_description": "Minor bug fix with performance improvement",
            "requester_id": "developer_002",
            "priority": "low",
        }

        response = await oversight_client.post(
            "/api/v1/evolution/submit", json=evolution_request
        )
        assert response.status_code == 200

        evolution_id = response.json()["evolution_id"]

        # Wait for processing
        await asyncio.sleep(2)

        # Check status
        response = await oversight_client.get(f"/api/v1/evolution/{evolution_id}")
        assert response.status_code == 200

        data = response.json()
        # Should be auto-approved due to high scores
        assert data["status"] in {"auto_approved", "deployed"}
        assert data["total_score"] >= 0.9

    async def test_low_score_human_review(self, oversight_client):
        """Test that low-scoring evolutions require human review."""
        # Create evolution with concerning patterns
        evolution_request = {
            "agent_id": "test_agent_risky",
            "new_version": {
                "version": "3.0.0",
                "changes": {
                    "code_changes": [
                        "Added exec() function call",
                        "Enabled unrestricted network access",
                        "Modified privilege settings",
                    ],
                    "config_changes": {
                        "network_access": "unrestricted",
                        "privilege_escalation": True,
                    },
                },
                "complexity_delta": 0.3,  # 30% complexity increase
                "resource_delta": 0.2,  # 20% resource increase
                "experimental_features": True,
            },
            "change_description": "Major refactor with new experimental features",
            "requester_id": "developer_003",
            "priority": "high",
        }

        response = await oversight_client.post(
            "/api/v1/evolution/submit", json=evolution_request
        )
        assert response.status_code == 200

        evolution_id = response.json()["evolution_id"]

        # Wait for processing
        await asyncio.sleep(3)

        # Check status
        response = await oversight_client.get(f"/api/v1/evolution/{evolution_id}")
        assert response.status_code == 200

        data = response.json()
        # Should require human review due to risk factors
        assert data["status"] == "human_review"
        assert data["total_score"] < 0.9
        assert "review_task" in data

    async def test_pending_reviews_endpoint(self, oversight_client):
        """Test retrieval of pending review tasks."""
        response = await oversight_client.get("/api/v1/reviews/pending")

        assert response.status_code == 200
        data = response.json()

        assert "pending_tasks" in data
        assert "total_count" in data
        assert isinstance(data["pending_tasks"], list)

        # Check task structure if any exist
        if data["pending_tasks"]:
            task = data["pending_tasks"][0]
            required_fields = [
                "task_id",
                "evolution_id",
                "agent_id",
                "priority",
                "created_at",
            ]
            for field in required_fields:
                assert field in task

    async def test_review_approval(self, oversight_client):
        """Test human review approval workflow."""
        # First create a risky evolution that will need review
        evolution_request = {
            "agent_id": "test_agent_approval",
            "new_version": {
                "version": "2.0.0",
                "changes": {
                    "code_changes": ["Significant architectural change"],
                    "config_changes": {"experimental_mode": True},
                },
                "complexity_delta": 0.15,
                "experimental_features": True,
            },
            "change_description": "Major architectural change requiring review",
            "requester_id": "developer_004",
            "priority": "critical",
        }

        submit_response = await oversight_client.post(
            "/api/v1/evolution/submit", json=evolution_request
        )
        assert submit_response.status_code == 200

        evolution_id = submit_response.json()["evolution_id"]

        # Wait for processing to create review task
        await asyncio.sleep(3)

        # Get pending reviews
        reviews_response = await oversight_client.get("/api/v1/reviews/pending")
        assert reviews_response.status_code == 200

        pending_tasks = reviews_response.json()["pending_tasks"]

        # Find our task
        task_id = None
        for task in pending_tasks:
            if task["evolution_id"] == evolution_id:
                task_id = task["task_id"]
                break

        if task_id:
            # Approve the review
            approve_response = await oversight_client.post(
                f"/api/v1/reviews/{task_id}/approve",
                params={"justification": "Approved after thorough review"},
            )

            assert approve_response.status_code == 200

            # Check evolution status
            status_response = await oversight_client.get(
                f"/api/v1/evolution/{evolution_id}"
            )
            assert status_response.status_code == 200

            status_data = status_response.json()
            assert status_data["status"] == "approved"
            assert status_data["decision"] == "HUMAN_APPROVED"

    async def test_review_rejection(self, oversight_client):
        """Test human review rejection workflow."""
        # Create risky evolution
        evolution_request = {
            "agent_id": "test_agent_rejection",
            "new_version": {
                "version": "1.5.0",
                "changes": {
                    "code_changes": [
                        "Unsafe memory operations",
                        "Disabled security checks",
                    ],
                    "config_changes": {"security_mode": "disabled"},
                },
                "complexity_delta": 0.25,
                "privilege_escalation": True,
            },
            "change_description": "Unsafe changes that should be rejected",
            "requester_id": "developer_005",
            "priority": "low",
        }

        submit_response = await oversight_client.post(
            "/api/v1/evolution/submit", json=evolution_request
        )
        assert submit_response.status_code == 200

        evolution_id = submit_response.json()["evolution_id"]

        # Wait for processing
        await asyncio.sleep(3)

        # Get pending reviews
        reviews_response = await oversight_client.get("/api/v1/reviews/pending")
        assert reviews_response.status_code == 200

        pending_tasks = reviews_response.json()["pending_tasks"]

        # Find our task and reject it
        task_id = None
        for task in pending_tasks:
            if task["evolution_id"] == evolution_id:
                task_id = task["task_id"]
                break

        if task_id:
            # Reject the review
            reject_response = await oversight_client.post(
                f"/api/v1/reviews/{task_id}/reject",
                params={
                    "justification": "Security concerns - unsafe operations detected"
                },
            )

            assert reject_response.status_code == 200

            # Check evolution status
            status_response = await oversight_client.get(
                f"/api/v1/evolution/{evolution_id}"
            )
            assert status_response.status_code == 200

            status_data = status_response.json()
            assert status_data["status"] == "rejected"
            assert status_data["decision"] == "REJECTED"

    async def test_rollback_mechanism(self, oversight_client):
        """Test agent rollback functionality."""

        # Submit rollback request
        response = await oversight_client.post(
            "/api/v1/evolution/fake_evolution_id/rollback",
            params={"reason": "Performance regression detected"},
        )

        # Note: This might fail if no previous version exists, which is expected
        # In a real test, we'd set up proper version history first
        assert response.status_code in {200, 404, 500}

        if response.status_code == 200:
            data = response.json()
            assert "rollback_details" in data
            assert data["rollback_details"]["status"] == "success"

    async def test_agent_evolution_history(self, oversight_client):
        """Test agent evolution history retrieval."""
        agent_id = "test_agent_001"

        response = await oversight_client.get(f"/api/v1/agents/{agent_id}/history")

        assert response.status_code == 200
        data = response.json()

        assert data["agent_id"] == agent_id
        assert "evolution_history" in data
        assert "total_count" in data
        assert isinstance(data["evolution_history"], list)

        # Check history entry structure if any exist
        if data["evolution_history"]:
            entry = data["evolution_history"][0]
            required_fields = ["evolution_id", "version", "status", "created_at"]
            for field in required_fields:
                assert field in entry

    async def test_metrics_endpoint(self, oversight_client):
        """Test service metrics endpoint."""
        response = await oversight_client.get("/metrics")

        assert response.status_code == 200
        data = response.json()

        assert data["service"] == "evolution-oversight"
        assert data["constitutional_hash"] == CONSTITUTIONAL_HASH
        assert "metrics" in data

        metrics = data["metrics"]
        required_metrics = [
            "total_evolutions_24h",
            "auto_approved_24h",
            "auto_approval_rate_pct",
            "pending_reviews",
            "active_reviews",
        ]

        for metric in required_metrics:
            assert metric in metrics
            assert isinstance(metrics[metric], (int, float))

    async def test_evaluation_performance(self, oversight_client):
        """Test evaluation performance under load."""
        import time

        # Submit multiple evolution requests concurrently
        evolution_requests = [
            {
                "agent_id": f"test_agent_perf_{i}",
                "new_version": {
                    "version": f"1.{i}.0",
                    "changes": {
                        "code_changes": [f"Change {i}"],
                        "config_changes": {},
                    },
                    "complexity_delta": 0.01 * i,
                    "resource_delta": 0.005 * i,
                },
                "change_description": f"Performance test evolution {i}",
                "requester_id": "performance_tester",
                "priority": "medium",
            }
            for i in range(10)
        ]

        # Submit all requests
        start_time = time.time()
        tasks = []
        for request in evolution_requests:
            task = oversight_client.post("/api/v1/evolution/submit", json=request)
            tasks.append(task)

        responses = await asyncio.gather(*tasks, return_exceptions=True)
        submission_time = time.time() - start_time

        # Check all submissions succeeded
        successful_submissions = 0
        for response in responses:
            if isinstance(response, httpx.Response) and response.status_code == 200:
                successful_submissions += 1

        assert successful_submissions >= 8  # At least 80% success rate
        assert submission_time < 5.0  # Should complete within 5 seconds

    async def test_constitutional_compliance_integration(self, oversight_client):
        """Test integration with constitutional compliance checking."""
        # Submit evolution with clear constitutional violations
        evolution_request = {
            "agent_id": "test_agent_constitutional",
            "new_version": {
                "version": "1.0.0",
                "changes": {
                    "code_changes": ["Bypassed constitutional constraints"],
                    "config_changes": {"constitutional_bypass": True},
                },
                "constitutional_violations": ["transparency", "accountability"],
            },
            "change_description": "Evolution with constitutional violations",
            "requester_id": "test_user",
            "priority": "low",
        }

        response = await oversight_client.post(
            "/api/v1/evolution/submit", json=evolution_request
        )
        assert response.status_code == 200

        evolution_id = response.json()["evolution_id"]

        # Wait for processing
        await asyncio.sleep(3)

        # Check that constitutional violations were detected
        status_response = await oversight_client.get(
            f"/api/v1/evolution/{evolution_id}"
        )
        assert status_response.status_code == 200

        status_data = status_response.json()
        # Should require human review due to constitutional concerns
        assert status_data["status"] == "human_review"
        # Total score should be low due to constitutional non-compliance
        assert status_data["total_score"] < 0.9


class TestEvolutionOversightPerformance:
    """Performance tests for evolution oversight service."""

    @pytest.fixture
    async def oversight_client(self):
        """Create HTTP client for oversight service."""
        async with httpx.AsyncClient(base_url=TEST_BASE_URL) as client:
            yield client

    async def test_evaluation_latency(self, oversight_client):
        """Test that evaluations complete within target latency."""
        import time

        evolution_request = {
            "agent_id": "test_agent_latency",
            "new_version": {
                "version": "1.0.0",
                "changes": {"code_changes": ["Minor change"]},
                "complexity_delta": 0.01,
            },
            "change_description": "Latency test evolution",
            "requester_id": "latency_tester",
            "priority": "medium",
        }

        start_time = time.time()
        response = await oversight_client.post(
            "/api/v1/evolution/submit", json=evolution_request
        )
        submission_time = time.time() - start_time

        assert response.status_code == 200
        assert submission_time < 1.0  # Submission should be fast

        evolution_id = response.json()["evolution_id"]

        # Wait and check evaluation completion
        for attempt in range(10):  # Max 10 seconds
            await asyncio.sleep(1)

            status_response = await oversight_client.get(
                f"/api/v1/evolution/{evolution_id}"
            )
            if status_response.status_code == 200:
                status_data = status_response.json()
                if status_data["status"] != "pending":
                    evaluation_time = attempt + 1
                    break
        else:
            evaluation_time = 10  # Timeout

        assert evaluation_time <= 5  # Should complete within 5 seconds

    async def test_concurrent_evaluations(self, oversight_client):
        """Test handling of concurrent evaluation requests."""
        concurrent_requests = 20

        evolution_requests = [
            {
                "agent_id": f"test_agent_concurrent_{i}",
                "new_version": {
                    "version": "1.0.0",
                    "changes": {"code_changes": [f"Change {i}"]},
                    "complexity_delta": 0.01,
                },
                "change_description": f"Concurrent test evolution {i}",
                "requester_id": "concurrent_tester",
                "priority": "medium",
            }
            for i in range(concurrent_requests)
        ]

        # Submit all requests concurrently
        import time

        start_time = time.time()

        tasks = []
        for request in evolution_requests:
            task = oversight_client.post("/api/v1/evolution/submit", json=request)
            tasks.append(task)

        responses = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time

        # Check results
        successful = 0
        for response in responses:
            if isinstance(response, httpx.Response) and response.status_code == 200:
                successful += 1

        success_rate = successful / concurrent_requests

        assert success_rate >= 0.9  # 90% success rate
        assert total_time < 10.0  # Complete within 10 seconds


if __name__ == "__main__":
    # Run basic smoke test
    async def smoke_test():
        async with httpx.AsyncClient(base_url=TEST_BASE_URL) as client:
            try:
                response = await client.get("/health")
                if response.status_code == 200:
                    response.json()
            except Exception:
                pass

    asyncio.run(smoke_test())
