"""
Advanced CSRF Protection for ACGS

This module provides comprehensive Cross-Site Request Forgery (CSRF) protection
with double-submit cookies, SameSite attributes, and origin validation.
"""

import hashlib
import hmac
import secrets
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Optional, Set, Tuple

import structlog
from fastapi import HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger(__name__)

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class CSRFMethod(Enum):
    """CSRF protection methods."""

    DOUBLE_SUBMIT_COOKIE = "double_submit_cookie"
    SYNCHRONIZER_TOKEN = "synchronizer_token"
    ORIGIN_HEADER = "origin_header"
    SAMESITE_COOKIE = "samesite_cookie"


@dataclass
class CSRFConfig:
    """Configuration for CSRF protection."""

    token_name: str = "csrf_token"
    cookie_name: str = "csrf_cookie"
    header_name: str = "X-CSRF-Token"
    secret_key: str = "your-secret-key-change-in-production"
    token_length: int = 32
    token_expiry: int = 3600  # 1 hour
    cookie_secure: bool = True
    cookie_samesite: str = "Strict"  # Strict, Lax, None
    require_origin_header: bool = True
    allowed_origins: Set[str] = None
    excluded_paths: Set[str] = None

    def __post_init__(self):
        if self.allowed_origins is None:
            self.allowed_origins = {
                "http://localhost:3000",
                "http://localhost:8000",
                "https://acgs.example.com",
            }

        if self.excluded_paths is None:
            self.excluded_paths = {
                "/health",
                "/metrics",
                "/api/auth/login",
                "/api/auth/refresh",
                "/docs",
                "/openapi.json",
            }


class CSRFTokenManager:
    """Manages CSRF tokens with various protection methods."""

    def __init__(self, config: CSRFConfig):
        self.config = config
        self.tokens: Dict[str, datetime] = {}

    def generate_token(self, session_id: Optional[str] = None) -> Tuple[str, str]:
        """
        Generate CSRF token and signature.

        Returns:
            Tuple of (token, signed_token)
        """
        # Generate random token
        token = secrets.token_urlsafe(self.config.token_length)

        # Create signature
        timestamp = str(int(time.time()))
        session_data = session_id or "anonymous"

        message = f"{token}:{timestamp}:{session_data}:{CONSTITUTIONAL_HASH}"
        signature = hmac.new(
            self.config.secret_key.encode(), message.encode(), hashlib.sha256
        ).hexdigest()

        signed_token = f"{token}:{timestamp}:{signature}"

        # Store token with expiry
        self.tokens[token] = datetime.now() + timedelta(
            seconds=self.config.token_expiry
        )

        logger.debug(
            "CSRF token generated",
            token_prefix=token[:8],
            session_id=session_id,
            constitutional_hash=CONSTITUTIONAL_HASH,
        )

        return token, signed_token

    def validate_token(
        self, token: str, signed_token: str, session_id: Optional[str] = None
    ) -> bool:
        """
        Validate CSRF token with signature verification.

        Args:
            token: The raw token
            signed_token: The signed token from cookie/header
            session_id: Optional session identifier

        Returns:
            True if token is valid
        """
        try:
            # Parse signed token
            parts = signed_token.split(":")
            if len(parts) != 3:
                logger.warning("Invalid signed token format")
                return False

            token_part, timestamp_part, signature_part = parts

            # Verify token matches
            if token != token_part:
                logger.warning("Token mismatch in CSRF validation")
                return False

            # Check expiry
            try:
                timestamp = int(timestamp_part)
                token_age = time.time() - timestamp

                if token_age > self.config.token_expiry:
                    logger.warning("CSRF token expired", age=token_age)
                    return False
            except ValueError:
                logger.warning("Invalid timestamp in CSRF token")
                return False

            # Verify signature
            session_data = session_id or "anonymous"
            message = (
                f"{token_part}:{timestamp_part}:{session_data}:{CONSTITUTIONAL_HASH}"
            )
            expected_signature = hmac.new(
                self.config.secret_key.encode(), message.encode(), hashlib.sha256
            ).hexdigest()

            if not hmac.compare_digest(signature_part, expected_signature):
                logger.warning("CSRF token signature verification failed")
                return False

            # Check if token exists in our store
            if token not in self.tokens:
                logger.warning("CSRF token not found in store")
                return False

            # Check token expiry in store
            if datetime.now() > self.tokens[token]:
                del self.tokens[token]
                logger.warning("CSRF token expired in store")
                return False

            logger.debug(
                "CSRF token validated successfully",
                token_prefix=token[:8],
                session_id=session_id,
            )

            return True

        except Exception as e:
            logger.error("CSRF token validation error", error=str(e))
            return False

    def invalidate_token(self, token: str):
        """Invalidate a specific token."""
        if token in self.tokens:
            del self.tokens[token]
            logger.debug("CSRF token invalidated", token_prefix=token[:8])

    def cleanup_expired_tokens(self):
        """Clean up expired tokens from memory."""
        now = datetime.now()
        expired_tokens = [
            token for token, expiry in self.tokens.items() if now > expiry
        ]

        for token in expired_tokens:
            del self.tokens[token]

        if expired_tokens:
            logger.debug("Cleaned up expired CSRF tokens", count=len(expired_tokens))


class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """CSRF protection middleware with multiple validation methods."""

    def __init__(self, app, config: CSRFConfig = None):
        super().__init__(app)
        self.config = config or CSRFConfig()
        self.token_manager = CSRFTokenManager(self.config)

    async def dispatch(self, request: Request, call_next):
        """Process request through CSRF protection."""
        # Skip excluded paths
        if self._should_skip_csrf(request):
            return await call_next(request)

        # For state-changing methods, validate CSRF
        if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            if not await self._validate_csrf_protection(request):
                logger.warning(
                    "CSRF validation failed",
                    method=request.method,
                    path=request.url.path,
                    client_ip=request.client.host if request.client else None,
                    user_agent=request.headers.get("user-agent", ""),
                    constitutional_hash=CONSTITUTIONAL_HASH,
                )

                raise HTTPException(
                    status_code=403, detail="CSRF token validation failed"
                )

        # Process request
        response = await call_next(request)

        # Add CSRF token to safe responses
        if request.method == "GET" and response.status_code == 200:
            response = await self._add_csrf_token(request, response)

        return response

    def _should_skip_csrf(self, request: Request) -> bool:
        """Check if CSRF protection should be skipped for this request."""
        # Skip excluded paths
        if request.url.path in self.config.excluded_paths:
            return True

        # Skip API endpoints with proper authentication
        if request.url.path.startswith("/api/"):
            auth_header = request.headers.get("authorization")
            if auth_header and auth_header.startswith("Bearer "):
                # For API endpoints with bearer tokens, CSRF is less critical
                # but we still validate origin if configured
                if self.config.require_origin_header:
                    return self._validate_origin(request)
                return True

        return False

    async def _validate_csrf_protection(self, request: Request) -> bool:
        """Validate CSRF protection using multiple methods."""
        # Method 1: Origin header validation
        if self.config.require_origin_header:
            if not self._validate_origin(request):
                return False

        # Method 2: Double-submit cookie validation
        if not await self._validate_double_submit_cookie(request):
            return False

        # Method 3: Synchronizer token validation
        if not await self._validate_synchronizer_token(request):
            return False

        return True

    def _validate_origin(self, request: Request) -> bool:
        """Validate Origin or Referer header."""
        origin = request.headers.get("origin")
        referer = request.headers.get("referer")

        # Check Origin header first
        if origin:
            if origin in self.config.allowed_origins:
                return True
            logger.warning("Invalid Origin header", origin=origin)
            return False

        # Fallback to Referer header
        if referer:
            for allowed_origin in self.config.allowed_origins:
                if referer.startswith(allowed_origin):
                    return True
            logger.warning("Invalid Referer header", referer=referer)
            return False

        # No origin or referer - reject
        logger.warning("Missing Origin and Referer headers")
        return False

    async def _validate_double_submit_cookie(self, request: Request) -> bool:
        """Validate double-submit cookie method."""
        # Get token from header
        token_header = request.headers.get(self.config.header_name.lower())
        if not token_header:
            # Try alternative header names
            token_header = request.headers.get("x-csrftoken")

        # Get token from cookie
        token_cookie = request.cookies.get(self.config.cookie_name)

        if not token_header or not token_cookie:
            logger.warning(
                "Missing CSRF tokens",
                has_header=bool(token_header),
                has_cookie=bool(token_cookie),
            )
            return False

        # Tokens must match
        if not hmac.compare_digest(token_header, token_cookie):
            logger.warning("CSRF token mismatch between header and cookie")
            return False

        return True

    async def _validate_synchronizer_token(self, request: Request) -> bool:
        """Validate synchronizer token method."""
        # Get token from request
        token = request.headers.get(self.config.header_name.lower())
        if not token:
            # Try form data for non-JSON requests
            if (
                request.headers.get("content-type")
                == "application/x-www-form-urlencoded"
            ):
                form_data = await request.form()
                token = form_data.get(self.config.token_name)

        if not token:
            logger.warning("No synchronizer token found")
            return False

        # Get signed token from cookie
        signed_token = request.cookies.get(self.config.cookie_name)
        if not signed_token:
            logger.warning("No signed CSRF token in cookie")
            return False

        # Get session ID
        session_id = request.cookies.get("session_id")

        # Validate token
        return self.token_manager.validate_token(token, signed_token, session_id)

    async def _add_csrf_token(self, request: Request, response: Response) -> Response:
        """Add CSRF token to response for safe requests."""
        try:
            # Get session ID
            session_id = request.cookies.get("session_id")

            # Generate new token
            token, signed_token = self.token_manager.generate_token(session_id)

            # Set cookie with signed token
            response.set_cookie(
                key=self.config.cookie_name,
                value=signed_token,
                httponly=True,
                secure=self.config.cookie_secure,
                samesite=self.config.cookie_samesite,
                max_age=self.config.token_expiry,
            )

            # Add token to response headers for JavaScript access
            response.headers[self.config.header_name] = token

            # Add meta tag for HTML pages (if response is HTML)
            content_type = response.headers.get("content-type", "")
            if "text/html" in content_type:
                # Note: This would require response body modification
                # which is complex in FastAPI middleware
                pass

            logger.debug(
                "CSRF token added to response",
                token_prefix=token[:8],
                session_id=session_id,
            )

        except Exception as e:
            logger.error("Failed to add CSRF token to response", error=str(e))

        return response


class CSRFProtection:
    """High-level CSRF protection interface."""

    def __init__(self, config: CSRFConfig = None):
        self.config = config or CSRFConfig()
        self.token_manager = CSRFTokenManager(self.config)

    def generate_token_pair(self, session_id: Optional[str] = None) -> Dict[str, str]:
        """Generate CSRF token pair for manual handling."""
        token, signed_token = self.token_manager.generate_token(session_id)

        return {
            "token": token,
            "signed_token": signed_token,
            "cookie_name": self.config.cookie_name,
            "header_name": self.config.header_name,
        }

    def validate_request(
        self, token: str, signed_token: str, session_id: Optional[str] = None
    ) -> bool:
        """Validate CSRF tokens manually."""
        return self.token_manager.validate_token(token, signed_token, session_id)

    def get_middleware(self) -> CSRFProtectionMiddleware:
        """Get CSRF middleware instance."""
        return CSRFProtectionMiddleware(None, self.config)


# Utility functions for easy integration
def create_csrf_protection(
    secret_key: str, allowed_origins: Set[str] = None, **kwargs
) -> CSRFProtection:
    """Create CSRF protection with custom configuration."""
    config = CSRFConfig(
        secret_key=secret_key, allowed_origins=allowed_origins, **kwargs
    )
    return CSRFProtection(config)


def generate_csrf_meta_tag(token: str, header_name: str = "X-CSRF-Token") -> str:
    """Generate HTML meta tag for CSRF token."""
    return f'<meta name="csrf-token" content="{token}" data-header="{header_name}">'


def get_csrf_headers(token: str, header_name: str = "X-CSRF-Token") -> Dict[str, str]:
    """Get headers for CSRF-protected requests."""
    return {header_name: token}


# JavaScript snippet for automatic CSRF token handling
CSRF_JAVASCRIPT_SNIPPET = """
// Automatic CSRF token handling
(function() {
    const csrfMeta = document.querySelector('meta[name="csrf-token"]');
    if (!csrfMeta) return;
    
    const token = csrfMeta.getAttribute('content');
    const headerName = csrfMeta.getAttribute('data-header') || 'X-CSRF-Token';
    
    // Override fetch to include CSRF token
    const originalFetch = window.fetch;
    window.fetch = function(url, options = {}) {
        if (!options.headers) options.headers = {};
        
        // Add CSRF token for state-changing methods
        if (options.method && ['POST', 'PUT', 'PATCH', 'DELETE'].includes(options.method.toUpperCase())) {
            options.headers[headerName] = token;
        }
        
        return originalFetch(url, options);
    };
    
    // Override XMLHttpRequest
    const originalOpen = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function(method, url, ...args) {
        this._method = method;
        return originalOpen.call(this, method, url, ...args);
    };
    
    const originalSend = XMLHttpRequest.prototype.send;
    XMLHttpRequest.prototype.send = function(data) {
        if (this._method && ['POST', 'PUT', 'PATCH', 'DELETE'].includes(this._method.toUpperCase())) {
            this.setRequestHeader(headerName, token);
        }
        return originalSend.call(this, data);
    };
})();
"""
