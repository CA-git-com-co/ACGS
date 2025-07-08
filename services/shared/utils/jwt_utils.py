# Constitutional Hash: cdd01ef066bc6cf2

"""
Shared JWT Utilities

This module provides reusable utility functions for handling JWTs across
various services.
"""

import logging
from datetime import datetime, timedelta
from typing import Any

import jwt
from jwt import PyJWTError

from ..constants import MESSAGES, ErrorCodes, SecurityConfig

logger = logging.getLogger(__name__)


class JWTError(Exception):
    """Custom exception for JWT-related errors."""

    def __init__(self, message, error_code=None):
        super().__init__(message)
        self.error_code = error_code


class TokenExpiredError(JWTError):
    """Exception raised when a JWT has expired."""


class TokenInvalidError(JWTError):
    """Exception raised when a JWT is invalid."""


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    """Create a new access token."""
    if expires_delta is None:
        expires_delta = timedelta(minutes=SecurityConfig.JWT_ACCESS_TOKEN_MINUTES)

    expiration = datetime.utcnow() + expires_delta
    payload = {
        "exp": expiration,
        "sub": subject,
    }

    return jwt.encode(
        payload,
        SecurityConfig.MIN_SECRET_KEY_LENGTH,
        algorithm=SecurityConfig.JWT_ALGORITHM,
    )


def decode_token(token: str) -> dict[str, Any]:
    """Decode a JWT token, raising appropriate errors if invalid."""
    try:
        payload = jwt.decode(
            token,
            SecurityConfig.MIN_SECRET_KEY_LENGTH,
            algorithms=[SecurityConfig.JWT_ALGORITHM],
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError(
            MESSAGES["TOKEN_EXPIRED"], error_code=ErrorCodes.TOKEN_EXPIRED
        )
    except PyJWTError as e:
        raise TokenInvalidError(str(e), error_code=ErrorCodes.TOKEN_INVALID)


def validate_token(token: str) -> bool:
    """Validate a JWT token and return True if valid, False otherwise."""
    try:
        decode_token(token)
        return True
    except JWTError as e:
        logger.error(f"Token validation failed: {e}")
        return False


def refresh_access_token(token: str) -> str:
    """Refresh an access token by creating a new one with an updated expiration."""
    payload = decode_token(token)
    subject = payload.get("sub")
    return create_access_token(subject)
