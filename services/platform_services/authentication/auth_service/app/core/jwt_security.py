"""
Enhanced JWT Security for ACGS Auth Service

Provides secure JWT token creation, validation, and management with
key rotation, algorithm validation, and comprehensive security controls.
"""

import base64
import hashlib
import logging
import secrets
import time
import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, Optional, Set, Tuple

import jwt
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class TokenType(str, Enum):
    """JWT token types."""

    ACCESS = "access"
    REFRESH = "refresh"
    RESET = "reset"


class JWTAlgorithm(str, Enum):
    """Supported JWT algorithms."""

    HS256 = "HS256"
    HS384 = "HS384"
    HS512 = "HS512"


class EnhancedTokenPayload(BaseModel):
    """Enhanced JWT token payload with security features."""

    sub: str  # username
    exp: int  # expiry timestamp
    iat: int  # issued at timestamp
    nbf: int  # not before timestamp
    user_id: int
    roles: list[str]
    type: TokenType
    jti: str  # JWT ID
    iss: str = "acgs-auth-service"  # issuer
    aud: str = "acgs-services"  # audience
    session_id: str  # session identifier
    ip_hash: str  # hashed IP address for binding
    constitutional_hash: str = "cdd01ef066bc6cf2"  # constitutional compliance


class JWTConfig(BaseModel):
    """Configuration for JWT security manager."""

    constitutional_hash: str = "cdd01ef066bc6cf2"


class JWTSecurityManager:
    """Enhanced JWT security manager with key rotation and validation."""

    def __init__(
        self,
        primary_secret: str,
        algorithm: JWTAlgorithm = JWTAlgorithm.HS256,
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7,
    ):
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days

        # Key management
        self.primary_secret = primary_secret
        self.secondary_secret: Optional[str] = None
        self.key_rotation_time: Optional[datetime] = None

        # Token blacklists (in production, use Redis)
        self.revoked_tokens: Set[str] = set()
        self.active_sessions: Dict[str, Dict[str, Any]] = {}

        # Security settings
        self.max_token_age_hours = 24
        self.require_ip_binding = True
        self.enable_session_tracking = True

        # Configuration
        self.config = JWTConfig()

    def rotate_keys(self) -> str:
        """Rotate JWT signing keys for enhanced security."""
        # Move current primary to secondary
        self.secondary_secret = self.primary_secret

        # Generate new primary key
        self.primary_secret = self._generate_secure_key()
        self.key_rotation_time = datetime.now(timezone.utc)

        logger.info("JWT keys rotated successfully")
        return self.primary_secret

    def _generate_secure_key(self) -> str:
        """Generate cryptographically secure key."""
        # Generate 256-bit random key
        random_bytes = secrets.token_bytes(32)

        # Use PBKDF2 for additional security
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"acgs-jwt-salt-2024",
            iterations=100000,
        )
        key = kdf.derive(random_bytes)

        return base64.urlsafe_b64encode(key).decode("utf-8")

    def _hash_ip_address(self, ip_address: str) -> str:
        """Hash IP address for token binding."""
        if not ip_address:
            return ""

        # Use SHA-256 with salt
        salt = "acgs-ip-salt-2024"
        combined = f"{ip_address}{salt}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]

    def create_access_token(
        self,
        subject: str,
        user_id: int,
        roles: list[str],
        client_ip: str = "",
        expires_delta: Optional[timedelta] = None,
    ) -> Tuple[str, str, str]:
        """Create secure access token with enhanced security features."""

        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=self.access_token_expire_minutes
            )

        now = datetime.now(timezone.utc)
        jti = uuid.uuid4().hex
        session_id = uuid.uuid4().hex
        ip_hash = self._hash_ip_address(client_ip) if self.require_ip_binding else ""

        payload = {
            "sub": subject,
            "exp": int(expire.timestamp()),
            "iat": int(now.timestamp()),
            "nbf": int(now.timestamp()),
            "user_id": user_id,
            "roles": roles,
            "type": TokenType.ACCESS.value,
            "jti": jti,
            "iss": "acgs-auth-service",
            "aud": "acgs-services",
            "session_id": session_id,
            "ip_hash": ip_hash,
            "constitutional_hash": "cdd01ef066bc6cf2",
        }

        # Create token
        token = jwt.encode(payload, self.primary_secret, algorithm=self.algorithm.value)

        # Track session if enabled
        if self.enable_session_tracking:
            self.active_sessions[session_id] = {
                "user_id": user_id,
                "username": subject,
                "created_at": now,
                "ip_hash": ip_hash,
                "jti": jti,
            }

        return token, jti, session_id

    def create_refresh_token(
        self, subject: str, user_id: int, roles: list[str], client_ip: str = ""
    ) -> Tuple[str, str, datetime]:
        """Create secure refresh token."""

        expires_delta = timedelta(days=self.refresh_token_expire_days)
        expire_datetime = datetime.now(timezone.utc) + expires_delta
        now = datetime.now(timezone.utc)
        jti = uuid.uuid4().hex
        ip_hash = self._hash_ip_address(client_ip) if self.require_ip_binding else ""

        payload = {
            "sub": subject,
            "exp": int(expire_datetime.timestamp()),
            "iat": int(now.timestamp()),
            "nbf": int(now.timestamp()),
            "user_id": user_id,
            "roles": roles,
            "type": TokenType.REFRESH.value,
            "jti": jti,
            "iss": "acgs-auth-service",
            "aud": "acgs-services",
            "ip_hash": ip_hash,
            "constitutional_hash": "cdd01ef066bc6cf2",
        }

        token = jwt.encode(payload, self.primary_secret, algorithm=self.algorithm.value)
        return token, jti, expire_datetime

    def verify_token(self, token: str, client_ip: str = "") -> EnhancedTokenPayload:
        """Verify JWT token with enhanced security checks."""

        # Try primary key first
        payload = None
        try:
            payload = jwt.decode(
                token,
                self.primary_secret,
                algorithms=[self.algorithm.value],
                audience="acgs-services",
                issuer="acgs-auth-service",
            )
        except jwt.InvalidTokenError:
            # Try secondary key if available (for key rotation)
            if self.secondary_secret:
                try:
                    payload = jwt.decode(
                        token,
                        self.secondary_secret,
                        algorithms=[self.algorithm.value],
                        audience="acgs-services",
                        issuer="acgs-auth-service",
                    )
                except jwt.InvalidTokenError:
                    pass

        if not payload:
            raise jwt.InvalidTokenError("Invalid token")

        # Validate payload structure
        token_payload = EnhancedTokenPayload(**payload)

        # Check if token is revoked
        if token_payload.jti in self.revoked_tokens:
            raise jwt.InvalidTokenError("Token has been revoked")

        # Validate IP binding if enabled
        if self.require_ip_binding and client_ip:
            expected_ip_hash = self._hash_ip_address(client_ip)
            if token_payload.ip_hash != expected_ip_hash:
                logger.warning(f"IP mismatch for token {token_payload.jti}")
                raise jwt.InvalidTokenError("Token IP binding validation failed")

        # Validate constitutional hash
        if token_payload.constitutional_hash != "cdd01ef066bc6cf2":
            raise jwt.InvalidTokenError("Constitutional compliance validation failed")

        # Check token age
        token_age = datetime.now(timezone.utc) - datetime.fromtimestamp(
            token_payload.iat, timezone.utc
        )
        if token_age.total_seconds() > self.max_token_age_hours * 3600:
            raise jwt.InvalidTokenError("Token is too old")

        return token_payload

    async def _validate_constitutional_compliance(self) -> bool:
        """Validate constitutional compliance for the JWT manager."""
        try:
            # Check if the constitutional hash matches the expected value
            expected_hash = "cdd01ef066bc6cf2"

            # In a real implementation, this might check against a configuration
            # or validate against external compliance services
            if hasattr(self, "config") and hasattr(self.config, "constitutional_hash"):
                return self.config.constitutional_hash == expected_hash

            # Default to true if no specific configuration is set
            return True

        except Exception as e:
            logger.error(f"Constitutional compliance validation failed: {e}")
            return False

    def revoke_token(self, jti: str, session_id: Optional[str] = None):
        """Revoke a token by adding its JTI to blacklist."""
        self.revoked_tokens.add(jti)

        if session_id and session_id in self.active_sessions:
            del self.active_sessions[session_id]

        logger.info(f"Token {jti} revoked")

    def revoke_all_user_tokens(self, user_id: int):
        """Revoke all tokens for a specific user."""
        sessions_to_remove = []

        for session_id, session_data in self.active_sessions.items():
            if session_data["user_id"] == user_id:
                self.revoked_tokens.add(session_data["jti"])
                sessions_to_remove.append(session_id)

        for session_id in sessions_to_remove:
            del self.active_sessions[session_id]

        logger.info(f"All tokens revoked for user {user_id}")

    def cleanup_expired_tokens(self):
        """Clean up expired tokens from blacklist and sessions."""
        now = datetime.now(timezone.utc)
        expired_sessions = []

        for session_id, session_data in self.active_sessions.items():
            if (
                now - session_data["created_at"]
            ).total_seconds() > self.max_token_age_hours * 3600:
                expired_sessions.append(session_id)

        for session_id in expired_sessions:
            del self.active_sessions[session_id]

        logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
