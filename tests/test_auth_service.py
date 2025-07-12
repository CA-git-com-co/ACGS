import os

"""
Unit Tests for ACGS Auth Service

Tests core authentication functionality including input validation,
JWT security, and constitutional compliance validation.
"""

import asyncio
import time
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, Mock, patch

import pytest

# Test the enhanced security modules we created
from services.platform_services.authentication.auth_service.app.core.input_validation import (
    InputValidator,
    SecureLoginRequest,
    SecureTokenRequest,
)
from services.platform_services.authentication.auth_service.app.core.jwt_security import (
    EnhancedTokenPayload,
    JWTAlgorithm,
    JWTSecurityManager,
    TokenType,
)

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class TestInputValidation:
    """Test input validation functionality."""

    def test_validate_username_valid(self):
        """Test valid username validation."""
        valid_usernames = ["testuser", "user123", "test_user", "user-name"]

        for username in valid_usernames:
            result = InputValidator.validate_username(username)
            assert result == username.strip()

    def test_validate_username_invalid(self):
        """Test invalid username validation."""
        invalid_usernames = [
            "",  # Empty
            "ab",  # Too short
            "a" * 51,  # Too long
            "user@domain",  # Invalid characters
            "user;DROP TABLE",  # SQL injection attempt
            "user--comment",  # SQL comment
        ]

        for username in invalid_usernames:
            with pytest.raises(ValueError):
                InputValidator.validate_username(username)

    def test_validate_password_valid(self):
        """Test valid password validation."""
        valid_passwords = ["Password123!", "MySecure@Pass1", "Complex#Password9"]

        for password in valid_passwords:
            result = InputValidator.validate_password(password)
            assert result == password

    def test_validate_password_invalid(self):
        """Test invalid password validation."""
        invalid_passwords = [
            "",  # Empty
            "short",  # Too short
            "password",  # Common weak password
            "PASSWORD123",  # No lowercase
            "password123",  # No uppercase
            "Password",  # No digit
            "Password123",  # No special character
        ]

        for password in invalid_passwords:
            with pytest.raises(ValueError):
                InputValidator.validate_password(password)

    def test_validate_email_valid(self):
        """Test valid email validation."""
        valid_emails = [
            "test@example.com",
            "user.name@domain.org",
            "admin+test@company.co.uk",
        ]

        for email in valid_emails:
            result = InputValidator.validate_email(email)
            assert result == email.lower().strip()

    def test_validate_email_invalid(self):
        """Test invalid email validation."""
        invalid_emails = [
            "",  # Empty
            "invalid-email",  # No @ symbol
            "@domain.com",  # No local part
            "user@",  # No domain
            "user@domain",  # No TLD
            "user;DROP@domain.com",  # SQL injection attempt
        ]

        for email in invalid_emails:
            with pytest.raises(ValueError):
                InputValidator.validate_email(email)

    def test_secure_login_request_valid(self):
        """Test valid secure login request."""
        # Use a valid password that meets all requirements:
        # - At least 8 characters
        # - Contains uppercase, lowercase, digit, and special character
        # - Constitutional hash validation maintained
        valid_password = "Password123!"
        request = SecureLoginRequest(
            username="testuser", password=valid_password
        )

        assert request.username == "testuser"
        assert request.password == "Password123!"

    def test_secure_login_request_invalid(self):
        """Test invalid secure login request."""
        with pytest.raises(ValueError):
            SecureLoginRequest(
                username="ab",  # Too short
                password=os.getenv("PASSWORD", ""),  # Weak password
            )


class TestJWTSecurity:
    """Test JWT security functionality."""

    @pytest.fixture
    def jwt_manager(self):
        """Create JWT security manager for testing."""
        return JWTSecurityManager(
            primary_secret=os.getenv("SECRET_KEY", ""),
            algorithm=JWTAlgorithm.HS256,
            access_token_expire_minutes=30,
            refresh_token_expire_days=7,
        )

    def test_create_access_token(self, jwt_manager):
        """Test access token creation."""
        token, jti, session_id = jwt_manager.create_access_token(
            subject="testuser", user_id=123, roles=["user"], client_ip="127.0.0.1"
        )

        assert isinstance(token, str)
        assert len(token) > 0
        assert isinstance(jti, str)
        assert isinstance(session_id, str)

    def test_create_refresh_token(self, jwt_manager):
        """Test refresh token creation."""
        token, jti, expire_datetime = jwt_manager.create_refresh_token(
            subject="testuser", user_id=123, roles=["user"], client_ip="127.0.0.1"
        )

        assert isinstance(token, str)
        assert len(token) > 0
        assert isinstance(jti, str)
        assert isinstance(expire_datetime, datetime)

    def test_verify_token_valid(self, jwt_manager):
        """Test valid token verification."""
        # Create token
        token, jti, session_id = jwt_manager.create_access_token(
            subject="testuser", user_id=123, roles=["user"], client_ip="127.0.0.1"
        )

        # Verify token
        payload = jwt_manager.verify_token(token, client_ip="127.0.0.1")

        assert payload.sub == "testuser"
        assert payload.user_id == 123
        assert payload.roles == ["user"]
        assert payload.type == TokenType.ACCESS
        assert payload.constitutional_hash == CONSTITUTIONAL_HASH

    def test_verify_token_invalid_ip(self, jwt_manager):
        """Test token verification with invalid IP."""
        # Create token with specific IP
        token, jti, session_id = jwt_manager.create_access_token(
            subject="testuser", user_id=123, roles=["user"], client_ip="127.0.0.1"
        )

        # Try to verify with different IP
        with pytest.raises(Exception):  # Should raise InvalidTokenError
            jwt_manager.verify_token(token, client_ip="192.168.1.1")

    def test_revoke_token(self, jwt_manager):
        """Test token revocation."""
        # Create token
        token, jti, session_id = jwt_manager.create_access_token(
            subject="testuser", user_id=123, roles=["user"]
        )

        # Revoke token
        jwt_manager.revoke_token(jti, session_id)

        # Verify revoked token fails
        with pytest.raises(Exception):  # Should raise InvalidTokenError
            jwt_manager.verify_token(token)

    def test_constitutional_compliance(self, jwt_manager):
        """Test constitutional compliance in tokens."""
        token, jti, session_id = jwt_manager.create_access_token(
            subject="testuser", user_id=123, roles=["user"]
        )

        payload = jwt_manager.verify_token(token)
        assert payload.constitutional_hash == CONSTITUTIONAL_HASH

    def test_key_rotation(self, jwt_manager):
        """Test JWT key rotation functionality."""
        # Create token with original key
        token1, jti1, session_id1 = jwt_manager.create_access_token(
            subject="testuser", user_id=123, roles=["user"]
        )

        # Rotate keys
        new_key = jwt_manager.rotate_keys()
        assert new_key != "test-secret-key-for-testing-only"

        # Old token should still work (secondary key)
        payload1 = jwt_manager.verify_token(token1)
        assert payload1.sub == "testuser"

        # New token should work with new key
        token2, jti2, session_id2 = jwt_manager.create_access_token(
            subject="testuser2", user_id=124, roles=["user"]
        )

        payload2 = jwt_manager.verify_token(token2)
        assert payload2.sub == "testuser2"


@pytest.mark.asyncio
class TestAuthServiceIntegration:
    """Integration tests for Auth service components."""

    async def test_login_flow_with_validation(self):
        """Test complete login flow with input validation."""
        # Test valid login with constitutional compliance
        # Use valid password meeting all security requirements
        valid_password = "SecurePass123!"
        request = SecureLoginRequest(
            username="testuser", password=valid_password
        )

        # Simulate authentication logic
        assert request.username == "testuser"
        assert request.password == "SecurePass123!"

        # Create JWT manager
        jwt_manager = JWTSecurityManager(
            primary_secret=os.getenv("SECRET_KEY", ""), algorithm=JWTAlgorithm.HS256
        )

        # Create token for authenticated user
        token, jti, session_id = jwt_manager.create_access_token(
            subject=request.username, user_id=123, roles=["user"], client_ip="127.0.0.1"
        )

        # Verify token
        payload = jwt_manager.verify_token(token, client_ip="127.0.0.1")
        assert payload.sub == request.username
        assert payload.constitutional_hash == CONSTITUTIONAL_HASH

    async def test_constitutional_compliance_validation(self):
        """Test constitutional compliance validation."""
        jwt_manager = JWTSecurityManager(
            primary_secret=os.getenv("SECRET_KEY", ""), algorithm=JWTAlgorithm.HS256
        )

        # Create token
        token, jti, session_id = jwt_manager.create_access_token(
            subject="testuser", user_id=123, roles=["user"]
        )

        # Verify constitutional compliance
        payload = jwt_manager.verify_token(token)
        assert payload.constitutional_hash == CONSTITUTIONAL_HASH

        # Test constitutional compliance validation
        is_compliant = await jwt_manager._validate_constitutional_compliance()
        assert is_compliant is True


@pytest.mark.performance
class TestAuthServicePerformance:
    """Performance tests for Auth service."""

    def test_input_validation_performance(self):
        """Test input validation performance."""
        start_time = time.time()

        # Validate 1000 usernames
        for i in range(1000):
            InputValidator.validate_username(f"testuser{i}")

        elapsed_time = (time.time() - start_time) * 1000  # Convert to ms

        # Should complete in under 100ms
        assert elapsed_time < 100, f"Input validation took {elapsed_time:.2f}ms"

    def test_jwt_creation_performance(self):
        """Test JWT creation performance."""
        jwt_manager = JWTSecurityManager(
            primary_secret=os.getenv("SECRET_KEY", ""), algorithm=JWTAlgorithm.HS256
        )

        start_time = time.time()

        # Create 100 tokens
        for i in range(100):
            jwt_manager.create_access_token(
                subject=f"testuser{i}", user_id=i, roles=["user"]
            )

        elapsed_time = (time.time() - start_time) * 1000  # Convert to ms

        # Should complete in under 50ms (0.5ms per token)
        assert elapsed_time < 50, f"JWT creation took {elapsed_time:.2f}ms"


@pytest.mark.constitutional
class TestConstitutionalCompliance:
    """Test constitutional compliance across Auth service."""

    def test_constitutional_hash_consistency(self):
        """Test constitutional hash consistency with constitutional compliance."""
        # Test in input validation with valid password
        # Ensure constitutional hash validation is maintained
        valid_password = "Constitutional123!"
        request = SecureLoginRequest(
            username="testuser", password=valid_password
        )

        # Test in JWT security
        jwt_manager = JWTSecurityManager(
            primary_secret=os.getenv("SECRET_KEY", ""), algorithm=JWTAlgorithm.HS256
        )

        token, jti, session_id = jwt_manager.create_access_token(
            subject="testuser", user_id=123, roles=["user"]
        )

        payload = jwt_manager.verify_token(token)

        # Verify constitutional hash is consistent
        assert payload.constitutional_hash == CONSTITUTIONAL_HASH

    @pytest.mark.asyncio
    async def test_constitutional_compliance_validation(self):
        """Test constitutional compliance validation."""
        jwt_manager = JWTSecurityManager(
            primary_secret=os.getenv("SECRET_KEY", ""), algorithm=JWTAlgorithm.HS256
        )

        # Test constitutional compliance
        is_compliant = await jwt_manager._validate_constitutional_compliance()
        assert is_compliant is True

        # Test with wrong hash
        jwt_manager.config.constitutional_hash = "wrong_hash"
        is_compliant = await jwt_manager._validate_constitutional_compliance()
        assert is_compliant is False
