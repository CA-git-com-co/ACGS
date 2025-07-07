"""
Tests for Unified Governance Engine
Constitutional Hash: cdd01ef066bc6cf2
"""

import os

# Import the app
import sys
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["constitutional_hash"] == "cdd01ef066bc6cf2"
    assert data["service"] == "unified-governance-engine"


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Unified Governance Engine"
    assert data["constitutional_hash"] == "cdd01ef066bc6cf2"
    assert "endpoints" in data


def test_policy_synthesis():
    """Test policy synthesis endpoint."""
    synthesis_request = {
        "context": "user_access_control",
        "policy_type": "authorization",
        "requirements": [
            "authenticated_user",
            "valid_permissions",
            "constitutional_compliance",
        ],
    }

    response = client.post("/api/v1/synthesis/synthesize", json=synthesis_request)
    assert response.status_code == 200
    data = response.json()
    assert "policy_id" in data
    assert data["constitutional_compliance"] > 0.9
    assert "synthesized_policy" in data


def test_policy_enforcement():
    """Test policy enforcement endpoint."""
    enforcement_request = {
        "policy_id": "test_policy_123",
        "context": {"user_id": "user123", "resource": "data"},
        "action": "read",
    }

    response = client.post("/api/v1/enforcement/enforce", json=enforcement_request)
    assert response.status_code == 200
    data = response.json()
    assert "allowed" in data
    assert "decision" in data
    assert data["constitutional_compliance"] > 0.9


def test_compliance_check():
    """Test compliance checking endpoint."""
    compliance_request = {
        "context": {"user_id": "user123", "action": "read"},
        "policies": ["policy1", "policy2"],
        "action": "read",
    }

    response = client.post("/api/v1/compliance/check", json=compliance_request)
    assert response.status_code == 200
    data = response.json()
    assert "compliant" in data
    assert "violations" in data
    assert data["constitutional_compliance"] > 0.9


def test_list_workflows():
    """Test workflow listing endpoint."""
    response = client.get("/api/v1/workflows")
    assert response.status_code == 200
    data = response.json()
    assert "workflows" in data
    assert len(data["workflows"]) > 0
    assert data["constitutional_hash"] == "cdd01ef066bc6cf2"


def test_execute_workflow():
    """Test workflow execution endpoint."""
    parameters = {"param1": "value1", "param2": "value2"}

    response = client.post(
        "/api/v1/workflows/policy_synthesis/execute", json=parameters
    )
    assert response.status_code == 200
    data = response.json()
    assert data["workflow_id"] == "policy_synthesis"
    assert "execution_id" in data
    assert data["status"] == "completed"


def test_constitutional_hash_consistency():
    """Test that constitutional hash is consistent across all endpoints."""
    endpoints = ["/health", "/", "/api/v1/workflows", "/api/v1/compliance/status"]

    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == 200
        data = response.json()
        assert data["constitutional_hash"] == "cdd01ef066bc6cf2"


if __name__ == "__main__":
    pytest.main([__file__])
