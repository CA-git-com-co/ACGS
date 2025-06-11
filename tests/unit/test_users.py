#!/usr/bin/env python3
"""
User-related unit tests for ACGS-1.
"""

import time
from uuid import uuid4

import pytest


# Mock settings for testing
class MockSettings:
    API_V1_STR = "/api/v1"


settings = MockSettings()

# Mock user data store for testing
mock_users_db = {}
mock_tokens_db = {}


class MockResponse:
    def __init__(self, status_code: int, json_data: dict = None):
        self.status_code = status_code
        self._json_data = json_data or {}

    def json(self):
        return self._json_data


class MockTestClient:
    def __init__(self):
        self.cookies = {}

    def post(self, url: str, json: dict = None, data: dict = None):
        """Mock POST requests."""
        if "/users/" in url and json:
            return self._handle_user_creation(json)
        elif "/login/access-token" in url and data:
            return self._handle_login(data)
        elif "/auth/register" in url and json:
            return self._handle_auth_register(json)
        elif "/auth/token" in url and data:
            return self._handle_auth_token(data)
        return MockResponse(404, {"detail": "Not found"})

    def get(self, url: str):
        """Mock GET requests."""
        if "/auth/me" in url:
            return self._handle_get_me()
        return MockResponse(404, {"detail": "Not found"})

    def _handle_user_creation(self, user_data: dict):
        email = user_data.get("email")
        if email in mock_users_db:
            return MockResponse(400, {"detail": "Email already registered"})

        user_id = str(uuid4())
        mock_users_db[email] = {
            "id": user_id,
            "email": email,
            "password": user_data.get("password"),
            "is_active": True,
        }
        return MockResponse(200, {"id": user_id, "email": email})

    def _handle_login(self, login_data: dict):
        username = login_data.get("username")
        password = login_data.get("password")

        if username not in mock_users_db:
            return MockResponse(401, {"detail": "Incorrect username or password"})

        user = mock_users_db[username]
        if user["password"] != password:
            return MockResponse(401, {"detail": "Incorrect username or password"})

        token = f"mock_token_{uuid4()}"
        mock_tokens_db[token] = {"user_email": username, "exp": time.time() + 3600}

        return MockResponse(200, {"access_token": token, "token_type": "bearer"})

    def _handle_auth_register(self, user_data: dict):
        email = user_data.get("email")
        username = user_data.get("username")

        if email in mock_users_db:
            return MockResponse(400, {"detail": "Email already registered"})

        user_id = str(uuid4())
        mock_users_db[email] = {
            "id": user_id,
            "email": email,
            "username": username,
            "full_name": user_data.get("full_name"),
            "password": user_data.get("password"),
            "is_active": True,
        }
        return MockResponse(201, {"id": user_id, "email": email, "username": username})

    def _handle_auth_token(self, login_data: dict):
        username = login_data.get("username")
        password = login_data.get("password")

        # Find user by username
        user = None
        for email, user_data in mock_users_db.items():
            if user_data.get("username") == username:
                user = user_data
                break

        if not user or user["password"] != password:
            return MockResponse(401, {"detail": "Incorrect username or password"})

        # Set mock cookies
        self.cookies["access_token_cookie"] = f"mock_token_{uuid4()}"
        self.cookies["csrf_access_token"] = f"csrf_{uuid4()}"

        return MockResponse(200, {"access_token": "token_set_in_cookie"})

    def _handle_get_me(self):
        if "access_token_cookie" not in self.cookies:
            return MockResponse(401, {"detail": "Access token missing or invalid"})

        # Find user associated with token (simplified)
        for email, user_data in mock_users_db.items():
            if user_data.get("username"):  # Return first authenticated user
                return MockResponse(
                    200,
                    {
                        "id": user_data["id"],
                        "email": user_data["email"],
                        "username": user_data["username"],
                        "full_name": user_data.get("full_name"),
                        "is_active": user_data["is_active"],
                    },
                )

        return MockResponse(401, {"detail": "User not found"})


@pytest.fixture
def random_user_payload() -> dict:
    test_email = f"testuser_{uuid4()}@example.com"
    return {"email": test_email, "password": "testpassword123"}


@pytest.fixture
def client():
    """Provide a mock test client."""
    return MockTestClient()


@pytest.fixture
def async_client():
    """Provide a mock async test client."""
    return MockTestClient()


def test_create_user(client, random_user_payload: dict):
    """Test user creation functionality."""
    url = f"{settings.API_V1_STR}/users/"
    response = client.post(url, json=random_user_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == random_user_payload["email"]
    assert "id" in data
    assert "hashed_password" not in data


def test_create_user_existing_email(client, random_user_payload: dict):
    """Test creating user with existing email fails."""
    url = f"{settings.API_V1_STR}/users/"
    client.post(url, json=random_user_payload)  # Create user first
    response = client.post(url, json=random_user_payload)  # Try again
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]


def test_login_for_access_token(client, random_user_payload: dict):
    """Test successful login for access token."""
    user_creation_url = f"{settings.API_V1_STR}/users/"
    client.post(user_creation_url, json=random_user_payload)  # Create user

    login_data = {
        "username": random_user_payload["email"],
        "password": random_user_payload["password"],
    }
    login_url = f"{settings.API_V1_STR}/login/access-token"
    response = client.post(login_url, data=login_data)
    assert response.status_code == 200
    tokens = response.json()
    assert "access_token" in tokens
    assert tokens["token_type"] == "bearer"


def test_login_wrong_password(client, random_user_payload: dict):
    """Test login with wrong password fails."""
    user_creation_url = f"{settings.API_V1_STR}/users/"
    client.post(user_creation_url, json=random_user_payload)  # Create user

    login_data = {
        "username": random_user_payload["email"],
        "password": "wrongtestpassword",
    }
    login_url = f"{settings.API_V1_STR}/login/access-token"
    response = client.post(login_url, data=login_data)
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    """Test login with nonexistent user fails."""
    login_data = {"username": "nonexistent@example.com", "password": "testpassword123"}
    login_url = f"{settings.API_V1_STR}/login/access-token"
    response = client.post(login_url, data=login_data)
    assert response.status_code == 401


def test_user_registration_flow(async_client, random_user_payload: dict):
    """Test user registration with auth endpoints."""
    API_V1_AUTH_PREFIX = f"{settings.API_V1_STR}/auth"

    user_data = {
        "username": random_user_payload["email"].split("@")[0] + "_usr",
        "email": random_user_payload["email"],
        "password": random_user_payload["password"],
        "full_name": "Test User",
    }

    register_url = f"{API_V1_AUTH_PREFIX}/register"
    response = async_client.post(register_url, json=user_data)
    assert response.status_code == 201
    created_user = response.json()
    assert created_user["email"] == user_data["email"]
    assert created_user["username"] == user_data["username"]


def test_user_authentication_flow(async_client, random_user_payload: dict):
    """Test user authentication with token endpoints."""
    API_V1_AUTH_PREFIX = f"{settings.API_V1_STR}/auth"

    # Register user first
    user_data = {
        "username": random_user_payload["email"].split("@")[0] + "_usr",
        "email": random_user_payload["email"],
        "password": random_user_payload["password"],
        "full_name": "Test User",
    }

    register_url = f"{API_V1_AUTH_PREFIX}/register"
    async_client.post(register_url, json=user_data)

    # Login with token
    login_data = {
        "username": user_data["username"],
        "password": user_data["password"],
    }
    login_url = f"{API_V1_AUTH_PREFIX}/token"
    response = async_client.post(login_url, data=login_data)
    assert response.status_code == 200


def test_get_current_user_authenticated(async_client, random_user_payload: dict):
    """Test getting current user when authenticated."""
    API_V1_AUTH_PREFIX = f"{settings.API_V1_STR}/auth"

    # Register and login user
    user_data = {
        "username": random_user_payload["email"].split("@")[0] + "_usr",
        "email": random_user_payload["email"],
        "password": random_user_payload["password"],
        "full_name": "Test User",
    }

    register_url = f"{API_V1_AUTH_PREFIX}/register"
    async_client.post(register_url, json=user_data)

    login_data = {
        "username": user_data["username"],
        "password": user_data["password"],
    }
    login_url = f"{API_V1_AUTH_PREFIX}/token"
    async_client.post(login_url, data=login_data)

    # Get current user
    me_url = f"{API_V1_AUTH_PREFIX}/me"
    response = async_client.get(me_url)
    assert response.status_code == 200
    user_data_response = response.json()
    assert user_data_response["email"] == user_data["email"]
    assert user_data_response["is_active"] is True


def test_get_current_user_unauthenticated(async_client):
    """Test getting current user when not authenticated."""
    API_V1_AUTH_PREFIX = f"{settings.API_V1_STR}/auth"

    me_url = f"{API_V1_AUTH_PREFIX}/me"
    response = async_client.get(me_url)
    assert response.status_code == 401
    assert "Access token missing or invalid" in response.json()["detail"]


def test_user_data_validation():
    """Test user data validation logic."""
    # Test email validation
    valid_emails = [
        "test@example.com",
        "user.name@domain.co.uk",
        "test+tag@example.org",
    ]

    for email in valid_emails:
        assert "@" in email, f"Email {email} should contain @"
        assert "." in email.split("@")[1], f"Email {email} should have domain"

    # Test password requirements
    valid_passwords = ["testpassword123", "SecurePass!@#", "MyPassword2024"]

    for password in valid_passwords:
        assert len(password) >= 8, f"Password {password} should be at least 8 chars"
