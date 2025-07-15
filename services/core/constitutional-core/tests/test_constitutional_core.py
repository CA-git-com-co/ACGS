"""
Tests for Constitutional Core Service
Constitutional Hash: cdd01ef066bc6cf2
"""

import pathlib

# Import the app
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.append(
    pathlib.Path(pathlib.Path(pathlib.Path(__file__).resolve()).parent).parent
)

from app.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["constitutional_hash"] == "cdd01ef066bc6cf2"
    assert data["service"] == "constitutional-core"
    assert "capabilities" in data


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Constitutional Core Service"
    assert data["constitutional_hash"] == "cdd01ef066bc6cf2"
    assert "endpoints" in data


def test_constitutional_validation():
    """Test constitutional validation endpoint."""
    validation_request = {
        "content": "This system treats all users fairly and transparently",
        "context": {"domain": "healthcare", "high_risk": False},
        "principles": ["fairness", "transparency"],
    }

    response = client.post("/api/v1/constitutional/validate", json=validation_request)
    assert response.status_code == 200
    data = response.json()
    assert "compliant" in data
    assert "score" in data
    assert data["constitutional_hash"] == "cdd01ef066bc6cf2"
    assert data["score"] >= 0.0
    assert data["score"] <= 1.0


def test_constitutional_validation_with_violations():
    """Test constitutional validation with violations."""
    validation_request = {
        "content": "This biased system discriminates against certain groups",
        "context": {"domain": "hiring", "high_risk": True},
        "principles": ["fairness", "human_dignity"],
    }

    response = client.post("/api/v1/constitutional/validate", json=validation_request)
    assert response.status_code == 200
    data = response.json()
    assert "compliant" in data
    assert "violated_principles" in data
    assert len(data["reasoning"]) > 0


def test_formal_verification():
    """Test formal verification endpoint."""
    verification_request = {
        "specification": "fairness_score >= 0.8",
        "context": {"demographic_parity": True},
        "verification_type": "smt",
        "timeout_seconds": 10,
    }

    response = client.post("/api/v1/verification/verify", json=verification_request)
    assert response.status_code == 200
    data = response.json()
    assert "verified" in data
    assert "solver_result" in data
    assert "constitutional_compliance" in data
    assert data["verification_time_ms"] >= 0


def test_verification_capabilities():
    """Test verification capabilities endpoint."""
    response = client.get("/api/v1/verification/capabilities")
    assert response.status_code == 200
    data = response.json()
    assert "z3_available" in data
    assert "supported_logics" in data
    assert data["constitutional_hash"] == "cdd01ef066bc6cf2"
    assert "verification_types" in data


def test_unified_compliance():
    """Test unified compliance endpoint."""
    unified_request = {
        "content": "Fair and transparent AI system with accountability",
        "context": {"domain": "finance", "high_risk": True},
        "principles": ["fairness", "transparency", "accountability"],
        "formal_specifications": ["fairness_score >= 0.8", "transparency_score >= 0.7"],
        "require_mathematical_proof": True,
    }

    response = client.post("/api/v1/unified/compliance", json=unified_request)
    assert response.status_code == 200
    data = response.json()
    assert "overall_compliant" in data
    assert "constitutional_compliance" in data
    assert "formal_verification" in data
    assert "unified_score" in data
    assert data["constitutional_hash"] == "cdd01ef066bc6cf2"


def test_unified_compliance_with_proof():
    """Test unified compliance with mathematical proof."""
    unified_request = {
        "content": "Highly compliant constitutional AI system",
        "context": {"domain": "governance"},
        "principles": ["fairness", "transparency"],
        "formal_specifications": ["fairness_score >= 0.8"],
        "require_mathematical_proof": True,
    }

    response = client.post("/api/v1/unified/compliance", json=unified_request)
    assert response.status_code == 200
    data = response.json()

    if data["overall_compliant"]:
        assert data["mathematical_proof"] is not None
        assert "Formal Proof" in data["mathematical_proof"]
        assert data["constitutional_hash"] in data["mathematical_proof"]


def test_list_constitutional_principles():
    """Test listing constitutional principles."""
    response = client.get("/api/v1/constitutional/principles")
    assert response.status_code == 200
    data = response.json()
    assert "principles" in data
    assert "total" in data
    assert data["constitutional_hash"] == "cdd01ef066bc6cf2"
    assert len(data["principles"]) > 0


def test_get_specific_principle():
    """Test getting a specific constitutional principle."""
    response = client.get("/api/v1/constitutional/principles/fairness")  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "fairness_001"
    assert data["name"] == "Fairness and Non-discrimination"
    assert data["constitutional_hash"] == "cdd01ef066bc6cf2"


def test_get_nonexistent_principle():
    """Test getting a non-existent principle."""
    response = client.get("/api/v1/constitutional/principles/nonexistent")  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    assert response.status_code == 404


def test_unified_status():
    """Test unified system status."""
    response = client.get("/api/v1/unified/status")
    assert response.status_code == 200
    data = response.json()
    assert data["constitutional_engine"] == "operational"
    assert data["unified_compliance"] == "operational"
    assert data["constitutional_hash"] == "cdd01ef066bc6cf2"
    assert data["system_health"] == "healthy"


def test_constitutional_hash_consistency():
    """Test that constitutional hash is consistent across all endpoints."""
    endpoints = [
        "/health",
        "/api/v1/constitutional/principles",
        "/api/v1/verification/capabilities",
        "/api/v1/unified/status",
    ]

    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == 200
        data = response.json()
        assert data["constitutional_hash"] == "cdd01ef066bc6cf2"


def test_validation_with_formal_proof():
    """Test constitutional validation with formal proof requirement."""
    validation_request = {
        "content": "Fair and transparent AI system",
        "context": {"domain": "education"},
        "principles": ["fairness", "transparency"],
        "require_formal_proof": True,
    }

    response = client.post("/api/v1/constitutional/validate", json=validation_request)
    assert response.status_code == 200
    data = response.json()

    if data["compliant"]:
        assert data["formal_proof"] is not None
        assert "Formal Proof" in data["formal_proof"]


def test_error_handling():
    """Test error handling for invalid requests."""
    # Invalid verification request
    invalid_request = {
        "specification": "",  # Empty specification
        "context": {},
        "timeout_seconds": -1,  # Invalid timeout
    }

    response = client.post("/api/v1/verification/verify", json=invalid_request)
    # Should handle gracefully, either with validation error or processed result
    assert response.status_code in {200, 422}  # 422 for validation error


def test_high_risk_context():
    """Test constitutional validation with high-risk context."""
    validation_request = {
        "content": "AI system for critical infrastructure",
        "context": {"domain": "critical_infrastructure", "high_risk": True},
        "principles": ["fairness", "accountability", "human_dignity"],
    }

    response = client.post("/api/v1/constitutional/validate", json=validation_request)
    assert response.status_code == 200
    data = response.json()

    # High-risk contexts should have higher standards
    assert "metadata" in data
    assert data["constitutional_hash"] == "cdd01ef066bc6cf2"


def test_multiple_formal_specifications():
    """Test unified compliance with multiple formal specifications."""
    unified_request = {
        "content": "Multi-faceted AI governance system",
        "context": {"domain": "multi_domain"},
        "principles": ["fairness", "transparency", "accountability"],
        "formal_specifications": [
            "fairness_score >= 0.8",
            "transparency_score >= 0.7",
            "audit_trail = True",
        ],
        "require_mathematical_proof": False,
    }

    response = client.post("/api/v1/unified/compliance", json=unified_request)
    assert response.status_code == 200
    data = response.json()
    assert "formal_verification" in data
    assert data["constitutional_hash"] == "cdd01ef066bc6cf2"


if __name__ == "__main__":
    pytest.main([__file__])
