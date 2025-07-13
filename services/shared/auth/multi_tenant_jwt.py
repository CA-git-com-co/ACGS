"""
Multi-Tenant JWT Handler for ACGS

This module provides a JWT handler specifically designed for multi-tenant
authentication with a simplified interface for testing.

Constitutional Hash: cdd01ef066bc6cf2
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class MultiTenantJWTHandler:
    """JWT handler for multi-tenant authentication."""

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
    ):
        """Initialize the JWT handler."""
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes

    async def create_access_token(
        self, data: dict[str, Any], expires_delta: timedelta | None = None
    ) -> str:
        """Create a JWT access token with the provided data."""
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=self.access_token_expire_minutes
            )

        to_encode.update(
            {
                "exp": int(expire.timestamp()),
                "iat": int(datetime.now(timezone.utc).timestamp()),
                "jti": str(uuid.uuid4()),
            }
        )

        # Ensure constitutional hash is included
        if "constitutional_hash" not in to_encode:
            to_encode["constitutional_hash"] = CONSTITUTIONAL_HASH

        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    async def decode_token(self, token: str) -> dict[str, Any]:
        """Decode and verify a JWT token."""
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Invalid token: {e!s}")

    def decode_token_sync(self, token: str) -> dict[str, Any]:
        """Synchronous version of decode_token for compatibility."""
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Invalid token: {e!s}")
