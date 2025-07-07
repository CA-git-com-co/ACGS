"""
Authentication Security Integration for ACGS

This module provides seamless integration between the authentication service
and the enhanced security validation system.
"""

import asyncio
from typing import Any, Dict, Optional

import structlog
from fastapi import HTTPException, Request, Response, status

from .csrf_protection import CSRFConfig, CSRFProtection
from .unified_input_validation import (
    EnhancedInputValidator,
    SecurityConfig,
    SecurityLevel,
    ValidationResult,
)

logger = structlog.get_logger(__name__)

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class AuthSecurityIntegration:
    """Integrated security validation for authentication service."""

    def __init__(
        self, security_config: SecurityConfig = None, csrf_config: CSRFConfig = None
    ):
        self.security_config = security_config or SecurityConfig()
        self.csrf_config = csrf_config or CSRFConfig()
        self.validator = EnhancedInputValidator(self.security_config)
        self.csrf_protection = CSRFProtection(self.csrf_config)

    def validate_user_registration(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate user registration data with comprehensive security checks.

        Args:
            user_data: User registration data

        Returns:
            Sanitized user data

        Raises:
            HTTPException: If validation fails
        """
        try:
            # Validate username
            username_result = self.validator.validate_string(
                user_data.get("username", ""),
                min_length=3,
                max_length=50,
                allowed_chars="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-",
                security_level=SecurityLevel.HIGH,
            )

            if not username_result.is_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Username validation failed: {', '.join(username_result.errors)}",
                )

            # Validate email
            email_result = self.validator.validate_email(user_data.get("email", ""))
            if not email_result.is_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Email validation failed: {', '.join(email_result.errors)}",
                )

            # Validate password strength
            password = user_data.get("password", "")
            password_result = self._validate_password_strength(password)
            if not password_result.is_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Password validation failed: {', '.join(password_result.errors)}",
                )

            # Validate optional fields
            sanitized_data = {
                "username": username_result.sanitized_value,
                "email": email_result.sanitized_value,
                "password": password,  # Don't sanitize password - keep original
            }

            # Handle optional name fields
            for field in ["first_name", "last_name"]:
                if field in user_data and user_data[field]:
                    name_result = self.validator.validate_string(
                        user_data[field],
                        max_length=100,
                        security_level=SecurityLevel.MEDIUM,
                    )
                    if name_result.is_valid:
                        sanitized_data[field] = name_result.sanitized_value
                    else:
                        logger.warning(
                            f"Name field {field} validation failed",
                            errors=name_result.errors,
                            constitutional_hash=CONSTITUTIONAL_HASH,
                        )

            logger.info(
                "User registration data validated successfully",
                username=sanitized_data["username"],
                email=sanitized_data["email"],
                constitutional_hash=CONSTITUTIONAL_HASH,
            )

            return sanitized_data

        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                "User registration validation error",
                error=str(e),
                constitutional_hash=CONSTITUTIONAL_HASH,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal validation error",
            )

    def validate_login_request(self, username: str, password: str) -> tuple[str, str]:
        """
        Validate login credentials with security checks.

        Args:
            username: Username to validate
            password: Password to validate

        Returns:
            Tuple of (sanitized_username, password)

        Raises:
            HTTPException: If validation fails
        """
        try:
            # Validate username
            username_result = self.validator.validate_string(
                username, min_length=3, max_length=50, security_level=SecurityLevel.HIGH
            )

            if not username_result.is_valid:
                logger.warning(
                    "Login username validation failed",
                    errors=username_result.errors,
                    risk_score=username_result.risk_score,
                    constitutional_hash=CONSTITUTIONAL_HASH,
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid username format",
                )

            # Basic password validation (don't reveal password policy during login)
            if not password or len(password) < 8 or len(password) > 128:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid password format",
                )

            # Check for obvious injection attempts in password
            password_result = self.validator.validate_string(
                password, security_level=SecurityLevel.MEDIUM
            )

            if password_result.risk_score > 0.7:
                logger.warning(
                    "High-risk login attempt detected",
                    username=username_result.sanitized_value,
                    risk_score=password_result.risk_score,
                    warnings=password_result.security_warnings,
                    constitutional_hash=CONSTITUTIONAL_HASH,
                )
                # Still allow login but log the attempt

            return username_result.sanitized_value, password

        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                "Login validation error",
                error=str(e),
                constitutional_hash=CONSTITUTIONAL_HASH,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal validation error",
            )

    def _validate_password_strength(self, password: str) -> ValidationResult:
        """Validate password strength requirements."""
        result = ValidationResult(is_valid=True)

        if not password:
            result.is_valid = False
            result.errors.append("Password is required")
            return result

        # Length validation
        if len(password) < 8:
            result.is_valid = False
            result.errors.append("Password must be at least 8 characters long")

        if len(password) > 128:
            result.is_valid = False
            result.errors.append("Password must be less than 128 characters")

        # Strength requirements
        import re

        if not re.search(r"[A-Z]", password):
            result.is_valid = False
            result.errors.append("Password must contain at least one uppercase letter")

        if not re.search(r"[a-z]", password):
            result.is_valid = False
            result.errors.append("Password must contain at least one lowercase letter")

        if not re.search(r"\d", password):
            result.is_valid = False
            result.errors.append("Password must contain at least one digit")

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            result.is_valid = False
            result.errors.append("Password must contain at least one special character")

        # Check for common weak passwords
        weak_passwords = {
            "password",
            "password123",
            "12345678",
            "qwerty",
            "admin",
            "letmein",
            "welcome",
            "monkey",
            "1234567890",
            "abc123",
            "password1",
            "123456789",
        }

        if password.lower() in weak_passwords:
            result.is_valid = False
            result.errors.append("Password is too common")

        # Security pattern validation
        security_result = self.validator.validate_string(
            password, security_level=SecurityLevel.MEDIUM
        )

        if security_result.risk_score > 0.5:
            result.security_warnings.extend(security_result.security_warnings)
            result.risk_score = security_result.risk_score

        return result

    def validate_token_request(self, token: str) -> str:
        """
        Validate JWT token format and security.

        Args:
            token: JWT token to validate

        Returns:
            Sanitized token

        Raises:
            HTTPException: If validation fails
        """
        try:
            if not token:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Token is required"
                )

            # Basic JWT format check (3 parts separated by dots)
            parts = token.split(".")
            if len(parts) != 3:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid token format",
                )

            # Security validation
            token_result = self.validator.validate_string(
                token,
                max_length=2048,  # JWT tokens can be quite long
                security_level=SecurityLevel.MEDIUM,
            )

            if not token_result.is_valid:
                logger.warning(
                    "Token validation failed",
                    errors=token_result.errors,
                    constitutional_hash=CONSTITUTIONAL_HASH,
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid token format",
                )

            if token_result.risk_score > 0.3:
                logger.warning(
                    "Suspicious token detected",
                    risk_score=token_result.risk_score,
                    warnings=token_result.security_warnings,
                    constitutional_hash=CONSTITUTIONAL_HASH,
                )

            return token.strip()

        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                "Token validation error",
                error=str(e),
                constitutional_hash=CONSTITUTIONAL_HASH,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal validation error",
            )

    def generate_csrf_tokens(self, session_id: Optional[str] = None) -> Dict[str, str]:
        """Generate CSRF token pair for authentication flows."""
        return self.csrf_protection.generate_token_pair(session_id)

    def validate_csrf_tokens(
        self, token: str, signed_token: str, session_id: Optional[str] = None
    ) -> bool:
        """Validate CSRF tokens for authentication flows."""
        return self.csrf_protection.validate_request(token, signed_token, session_id)

    async def log_security_event(
        self,
        event_type: str,
        details: Dict[str, Any],
        request: Optional[Request] = None,
        severity: str = "warning",
    ):
        """Log security events with structured logging."""
        log_data = {
            "event_type": event_type,
            "details": details,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "timestamp": "now",
        }

        if request:
            log_data.update(
                {
                    "client_ip": request.client.host if request.client else None,
                    "user_agent": request.headers.get("user-agent", ""),
                    "path": request.url.path,
                    "method": request.method,
                }
            )

        if severity == "error":
            logger.error("Authentication security event", **log_data)
        elif severity == "warning":
            logger.warning("Authentication security event", **log_data)
        else:
            logger.info("Authentication security event", **log_data)


# Utility functions for easy integration
def create_auth_security_integration(
    max_password_length: int = 128, csrf_secret: str = "change-in-production", **kwargs
) -> AuthSecurityIntegration:
    """Create authentication security integration with custom configuration."""
    security_config = SecurityConfig(max_string_length=max_password_length, **kwargs)

    csrf_config = CSRFConfig(secret_key=csrf_secret, **kwargs)

    return AuthSecurityIntegration(security_config, csrf_config)


def validate_user_input_secure(
    data: Dict[str, Any], security_level: SecurityLevel = SecurityLevel.HIGH
) -> Dict[str, Any]:
    """Quick utility for validating user input data."""
    integration = AuthSecurityIntegration()

    if "username" in data and "email" in data and "password" in data:
        # This looks like registration data
        return integration.validate_user_registration(data)
    else:
        # Generic validation
        from .unified_input_validation import sanitize_dict

        return sanitize_dict(data, security_level)
