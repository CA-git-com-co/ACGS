"""
Enhanced Input Validation for ACGS Auth Service

Provides comprehensive input validation and sanitization to prevent
injection attacks, XSS, and other security vulnerabilities.
"""

import html
import logging
import re
from typing import Any

from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)

# Security patterns for detection
SQL_INJECTION_PATTERNS = [
    r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
    r"(\b(UNION|OR|AND)\s+\d+\s*=\s*\d+)",
    r"(--|#|/\*|\*/)",
    r"(\bxp_|\bsp_)",
    r"(\bCAST\s*\(|\bCONVERT\s*\()",
    r"(\bCHAR\s*\(|\bASCII\s*\()",
]

XSS_PATTERNS = [
    r"<script[^>]*>.*?</script>",
    r"javascript:",
    r"vbscript:",
    r"onload\s*=",
    r"onerror\s*=",
    r"onclick\s*=",
    r"onmouseover\s*=",
    r"<iframe[^>]*>",
    r"<object[^>]*>",
    r"<embed[^>]*>",
]

LDAP_INJECTION_PATTERNS = [
    r"[()&|!]",
    r"\*",
    r"\\",
]


class InputValidator:
    """Comprehensive input validation and sanitization."""

    @staticmethod
    def sanitize_string(value: str, max_length: int = 255) -> str:
        """Sanitize string input to prevent various attacks."""
        if not isinstance(value, str):
            raise ValueError("Input must be a string")

        # Trim whitespace
        value = value.strip()

        # Check length
        if len(value) > max_length:
            raise ValueError(f"Input exceeds maximum length of {max_length}")

        # HTML encode to prevent XSS
        return html.escape(value)

    @staticmethod
    def validate_username(username: str) -> str:
        """Validate username format and security."""
        if not username:
            raise ValueError("Username is required")

        # Length check
        if len(username) < 3 or len(username) > 50:
            raise ValueError("Username must be between 3 and 50 characters")

        # Character validation
        if not re.match(r"^[a-zA-Z0-9_-]+$", username):
            raise ValueError(
                "Username can only contain letters, numbers, underscores, and hyphens"
            )

        # Check for SQL injection patterns
        username_lower = username.lower()
        for pattern in SQL_INJECTION_PATTERNS:
            if re.search(pattern, username_lower, re.IGNORECASE):
                raise ValueError("Username contains invalid characters")

        return username.strip()

    @staticmethod
    def validate_password(password: str) -> str:
        """Validate password strength and security."""
        if not password:
            raise ValueError("Password is required")

        # Length check
        if len(password) < 8 or len(password) > 128:
            raise ValueError("Password must be between 8 and 128 characters")

        # Strength requirements
        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must contain at least one uppercase letter")

        if not re.search(r"[a-z]", password):
            raise ValueError("Password must contain at least one lowercase letter")

        if not re.search(r"\d", password):
            raise ValueError("Password must contain at least one digit")

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValueError("Password must contain at least one special character")

        # Check for common weak passwords
        weak_passwords = [
            "password",
            "12345678",
            "qwerty",
            "admin",
            "letmein",
            "welcome",
            "monkey",
            "1234567890",
            "password123",
        ]
        if password.lower() in weak_passwords:
            raise ValueError("Password is too common")

        return password

    @staticmethod
    def validate_email(email: str) -> str:
        """Validate email format and security."""
        if not email:
            raise ValueError("Email is required")

        # Length check
        if len(email) > 254:
            raise ValueError("Email address is too long")

        # Basic format validation
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, email):
            raise ValueError("Invalid email format")

        # Check for injection patterns
        email_lower = email.lower()
        for pattern in SQL_INJECTION_PATTERNS:
            if re.search(pattern, email_lower, re.IGNORECASE):
                raise ValueError("Email contains invalid characters")

        return email.lower().strip()

    @staticmethod
    def validate_jwt_token(token: str) -> str:
        """Validate JWT token format."""
        if not token:
            raise ValueError("Token is required")

        # Basic JWT format check (3 parts separated by dots)
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Invalid token format")

        # Check for suspicious patterns
        token_lower = token.lower()
        suspicious_patterns = ["<script", "javascript:", "data:", "vbscript:"]
        for pattern in suspicious_patterns:
            if pattern in token_lower:
                raise ValueError("Token contains invalid characters")

        return token.strip()

    @staticmethod
    def validate_api_key(api_key: str) -> str:
        """Validate API key format."""
        if not api_key:
            raise ValueError("API key is required")

        # Length check
        if len(api_key) < 16 or len(api_key) > 128:
            raise ValueError("API key must be between 16 and 128 characters")

        # Character validation (alphanumeric and some special chars)
        if not re.match(r"^[a-zA-Z0-9_-]+$", api_key):
            raise ValueError("API key contains invalid characters")

        return api_key.strip()

    @staticmethod
    def sanitize_request_data(data: dict[str, Any]) -> dict[str, Any]:
        """Sanitize request data dictionary."""
        sanitized = {}

        for key, value in data.items():
            # Sanitize key
            if not isinstance(key, str):
                continue

            clean_key = InputValidator.sanitize_string(key, 100)

            # Sanitize value based on type
            if isinstance(value, str):
                clean_value = InputValidator.sanitize_string(value)
            elif isinstance(value, (int, float, bool)):
                clean_value = value
            elif isinstance(value, list):
                clean_value = [
                    (
                        InputValidator.sanitize_string(item)
                        if isinstance(item, str)
                        else item
                    )
                    for item in value
                ]
            elif isinstance(value, dict):
                clean_value = InputValidator.sanitize_request_data(value)
            else:
                clean_value = str(value)

            sanitized[clean_key] = clean_value

        return sanitized


class SecureLoginRequest(BaseModel):
    """Secure login request with enhanced validation."""

    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("username")
    @classmethod
    def validate_username_field(cls, v: str) -> str:
        return InputValidator.validate_username(v)

    @field_validator("password")
    @classmethod
    def validate_password_field(cls, v: str) -> str:
        return InputValidator.validate_password(v)


class SecureTokenRequest(BaseModel):
    """Secure token validation request."""

    token: str = Field(..., min_length=10)

    @field_validator("token")
    @classmethod
    def validate_token_field(cls, v: str) -> str:
        return InputValidator.validate_jwt_token(v)


def log_security_event(
    event_type: str, details: dict[str, Any], client_ip: str | None = None
):
    """Log security events for monitoring."""
    log_data = {
        "event_type": event_type,
        "timestamp": "now",
        "client_ip": client_ip,
        "details": details,
        "constitutional_hash": "cdd01ef066bc6cf2",  # Constitutional compliance
    }
    logger.warning(f"Security Event: {log_data}")
