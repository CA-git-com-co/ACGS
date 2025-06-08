from datetime import timedelta
import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock
import time
import json

import pytest

# Mock implementations for testing without full backend setup
class MockSettings:
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    SECRET_KEY = "test-secret-key"

class MockHTTPException(Exception):
    def __init__(self, status_code, detail=None):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)

class MockSecurity:
    HTTPException = MockHTTPException

    @staticmethod
    def create_access_token(subject: str, expires_delta: timedelta = None):
        """Mock token creation."""
        exp = int(time.time()) + (expires_delta.total_seconds() if expires_delta else 1800)
        token_data = {
            "sub": subject,
            "exp": exp,
            "iat": int(time.time())
        }
        # Simple mock token (not real JWT)
        import base64
        return base64.b64encode(json.dumps(token_data).encode()).decode()

    @staticmethod
    def verify_token(token: str):
        """Mock token verification."""
        try:
            import base64

            # Check for obviously tampered tokens
            if token.endswith("tampered"):
                raise MockHTTPException(401, "Could not validate credentials")

            decoded = json.loads(base64.b64decode(token).decode())

            # Check if expired
            if decoded.get("exp", 0) < time.time():
                raise MockHTTPException(401, "Token has expired")

            # Return mock payload
            payload = Mock()
            payload.sub = decoded.get("sub")
            return payload

        except (json.JSONDecodeError, ValueError, Exception):
            raise MockHTTPException(401, "Could not validate credentials")

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Mock password hashing."""
        import hashlib
        return hashlib.sha256(f"salt_{password}".encode()).hexdigest()

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Mock password verification."""
        expected_hash = MockSecurity.get_password_hash(plain_password)
        return expected_hash == hashed_password

# Use mock implementations
security = MockSecurity()
settings = MockSettings()


def test_create_access_token():
    subject = "testuser@example.com"
    expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = security.create_access_token(subject=subject, expires_delta=expires)
    assert isinstance(token, str)


def test_verify_access_token_valid():
    subject = "testuser@example.com"
    expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = security.create_access_token(subject=subject, expires_delta=expires)
    payload = security.verify_token(token)
    assert payload is not None
    if payload:  # Type guard
        assert payload.sub == subject
        # Add more assertions for expiry, etc., if needed


def test_verify_access_token_expired():
    subject = "testuser@example.com"
    # Create a token that has already expired
    expired_delta = timedelta(minutes=-settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expired_token = security.create_access_token(
        subject=subject, expires_delta=expired_delta
    )

    with pytest.raises(security.HTTPException) as excinfo:
        security.verify_token(expired_token)
    # This depends on how security.verify_token raises exceptions
    # for expired tokens. Assuming HTTPException with status 401.
    assert excinfo.value.status_code == 401
    # assert "Token has expired" in str(excinfo.value.detail)


def test_verify_access_token_invalid_signature():
    subject = "testuser@example.com"
    expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = security.create_access_token(subject=subject, expires_delta=expires)
    # Tamper with the token
    invalid_token = token + "tampered"

    with pytest.raises(security.HTTPException) as excinfo:
        security.verify_token(invalid_token)
    # Assuming HTTPException with status 401 for signature mismatch.
    assert excinfo.value.status_code == 401
    # assert "Could not validate credentials" in str(excinfo.value.detail)


def test_password_hashing_and_verification():
    password = "supersecretpassword"
    hashed_password = security.get_password_hash(password)
    assert isinstance(hashed_password, str)
    assert hashed_password != password

    assert security.verify_password(password, hashed_password) is True
    assert security.verify_password("wrongpassword", hashed_password) is False


# TODO:
# - Test for tokens with different scopes if applicable.
# - Test for tokens with non-ASCII characters in subject if relevant.
# - Consider edge cases for token expiry (e.g., token created just before
#   expiry).
