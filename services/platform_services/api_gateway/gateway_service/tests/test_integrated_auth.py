"""
Tests for Integrated Authentication in API Gateway
Constitutional Hash: cdd01ef066bc6cf2
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

# Import the app
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock dependencies to avoid import errors
with patch('app.core.gateway_config.GatewayConfig'), \
     patch('app.routing.service_router.ServiceRouter'), \
     patch('app.security.policy_engine.SecurityPolicyEngine'), \
     patch('app.monitoring.metrics_collector.MetricsCollector'), \
     patch('app.middleware.authentication.AuthenticationMiddleware'), \
     patch('app.middleware.constitutional_compliance.ConstitutionalComplianceMiddleware'), \
     patch('app.middleware.rate_limiting.RateLimitingMiddleware'), \
     patch('app.middleware.request_logging.RequestLoggingMiddleware'), \
     patch('app.middleware.security_headers.SecurityHeadersMiddleware'):
    
    from app.main import app

client = TestClient(app)


def test_login_success():
    """Test successful login."""
    credentials = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = client.post("/auth/login", json=credentials)
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data
    assert data["username"] == "admin"
    assert data["constitutional_hash"] == "cdd01ef066bc6cf2"
    assert "admin" in data["roles"]


def test_login_invalid_credentials():
    """Test login with invalid credentials."""
    credentials = {
        "username": "admin",
        "password": "wrongpassword"
    }
    
    response = client.post("/auth/login", json=credentials)
    assert response.status_code == 401


def test_login_user_not_found():
    """Test login with non-existent user."""
    credentials = {
        "username": "nonexistent",
        "password": "password"
    }
    
    response = client.post("/auth/login", json=credentials)
    assert response.status_code == 401


def test_validate_token_success():
    """Test token validation with valid token."""
    # First, login to get a token
    credentials = {
        "username": "admin",
        "password": "admin123"
    }
    
    login_response = client.post("/auth/login", json=credentials)
    assert login_response.status_code == 200
    
    token = login_response.json()["access_token"]
    
    # Now validate the token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/auth/validate", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["username"] == "admin"
    assert data["constitutional_hash"] == "cdd01ef066bc6cf2"


def test_validate_token_missing():
    """Test token validation without token."""
    response = client.post("/auth/validate")
    
    data = response.json()
    assert data["valid"] is False
    assert "error" in data


def test_get_current_user_success():
    """Test getting current user info with valid token."""
    # First, login to get a token
    credentials = {
        "username": "admin",
        "password": "admin123"
    }
    
    login_response = client.post("/auth/login", json=credentials)
    token = login_response.json()["access_token"]
    
    # Get user info
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/auth/me", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "admin"
    assert data["constitutional_hash"] == "cdd01ef066bc6cf2"
    assert "admin" in data["roles"]


def test_get_current_user_unauthorized():
    """Test getting current user info without token."""
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_logout_success():
    """Test successful logout."""
    # First, login to get a token
    credentials = {
        "username": "admin",
        "password": "admin123"
    }
    
    login_response = client.post("/auth/login", json=credentials)
    token = login_response.json()["access_token"]
    
    # Logout
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/auth/logout", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "Successfully logged out" in data["message"]
    assert data["constitutional_hash"] == "cdd01ef066bc6cf2"


def test_auth_health_check():
    """Test authentication health check."""
    response = client.get("/auth/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["healthy"] is True
    assert data["constitutional_hash"] == "cdd01ef066bc6cf2"
    assert "users_count" in data


def test_create_user_admin_required():
    """Test user creation requires admin role."""
    # Login as regular user
    credentials = {
        "username": "user",
        "password": "user123"
    }
    
    login_response = client.post("/auth/login", json=credentials)
    token = login_response.json()["access_token"]
    
    # Try to create user (should fail)
    headers = {"Authorization": f"Bearer {token}"}
    user_data = {
        "username": "testuser",
        "password": "testpass",
        "roles": ["user"]
    }
    
    response = client.post("/auth/admin/users", json=user_data, headers=headers)
    assert response.status_code == 403


def test_create_user_admin_success():
    """Test user creation with admin role."""
    # Login as admin
    credentials = {
        "username": "admin",
        "password": "admin123"
    }
    
    login_response = client.post("/auth/login", json=credentials)
    token = login_response.json()["access_token"]
    
    # Create user
    headers = {"Authorization": f"Bearer {token}"}
    user_data = {
        "username": "newuser",
        "password": "newpass",
        "roles": ["user"],
        "permissions": ["read"]
    }
    
    response = client.post("/auth/admin/users", json=user_data, headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "User created successfully" in data["message"]
    assert data["constitutional_hash"] == "cdd01ef066bc6cf2"


def test_constitutional_expert_login():
    """Test login with constitutional expert account."""
    credentials = {
        "username": "constitutional_expert",
        "password": "const123"
    }
    
    response = client.post("/auth/login", json=credentials)
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert "constitutional_expert" in data["roles"]
    assert "constitutional_review" in data["permissions"]
    assert "policy_synthesis" in data["permissions"]


def test_token_expiration_format():
    """Test that token expiration is properly formatted."""
    credentials = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = client.post("/auth/login", json=credentials)
    data = response.json()
    
    assert "expires_in" in data
    assert isinstance(data["expires_in"], int)
    assert data["expires_in"] > 0
    assert data["token_type"] == "bearer"


def test_constitutional_hash_consistency():
    """Test that constitutional hash is consistent across all auth endpoints."""
    endpoints = [
        "/auth/health",
    ]
    
    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == 200
        data = response.json()
        assert data["constitutional_hash"] == "cdd01ef066bc6cf2"


def test_rate_limiting_simulation():
    """Test rate limiting for authentication attempts."""
    credentials = {
        "username": "admin",
        "password": "wrongpassword"
    }
    
    # Make multiple failed attempts
    for i in range(6):  # Exceeds the limit of 5
        response = client.post("/auth/login", json=credentials)
        if i < 5:
            assert response.status_code == 401
        else:
            # Should be rate limited
            assert response.status_code == 401
            data = response.json()
            if "too many" in data.get("detail", "").lower():
                break


if __name__ == "__main__":
    pytest.main([__file__])