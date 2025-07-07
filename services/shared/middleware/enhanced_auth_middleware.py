"""
Enhanced authentication middleware with JWT and service-to-service authentication.
Constitutional Hash: cdd01ef066bc6cf2
"""

import logging
import time
from typing import Any, Callable, Dict, List, Optional

import httpx
import jwt
from fastapi import HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Constitutional compliance hash
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Authentication headers
USER_AUTH_HEADER = "Authorization"
SERVICE_AUTH_HEADER = "X-Service-Auth"
CONSTITUTIONAL_HEADER = "X-Constitutional-Hash"

logger = logging.getLogger(__name__)


class EnhancedAuthMiddleware(BaseHTTPMiddleware):
    """Enhanced authentication middleware with constitutional compliance."""

    def __init__(
        self,
        app,
        service_name: str,
        service_secret: str,
        auth_service_url: str = "http://localhost:8016",
        public_paths: List[str] = None,
        service_only_paths: List[str] = None,
    ):
        super().__init__(app)
        self.service_name = service_name
        self.service_secret = service_secret
        self.auth_service_url = auth_service_url.rstrip("/")
        self.public_paths = public_paths or [
            "/health",
            "/metrics",
            "/docs",
            "/openapi.json",
        ]
        self.service_only_paths = service_only_paths or []
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.http_client = httpx.AsyncClient(timeout=5.0)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip authentication for public paths
        if request.url.path in self.public_paths:
            response = await call_next(request)
            self._add_constitutional_headers(response)
            return response

        # Add constitutional hash to request state
        request.state.constitutional_hash = self.constitutional_hash

        # Check if path requires service authentication only
        service_only = request.url.path in self.service_only_paths

        try:
            # Validate service authentication for service-only paths
            if service_only:
                await self._validate_service_auth(request)
            else:
                # For other paths, validate either user or service authentication
                user_auth = request.headers.get(USER_AUTH_HEADER)
                service_auth = request.headers.get(SERVICE_AUTH_HEADER)

                if service_auth:
                    await self._validate_service_auth(request)
                elif user_auth:
                    await self._validate_user_auth(request)
                else:
                    raise HTTPException(
                        status_code=401, detail="Authentication required"
                    )

            # Continue processing
            response = await call_next(request)

            # Add constitutional hash to response
            self._add_constitutional_headers(response)

            return response

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise HTTPException(status_code=500, detail="Authentication service error")

    async def _validate_service_auth(self, request: Request):
        """Validate service-to-service authentication."""
        token = request.headers.get(SERVICE_AUTH_HEADER)
        if not token:
            raise HTTPException(
                status_code=401, detail="Service authentication required"
            )

        try:
            # Decode service token (simple JWT for service auth)
            payload = jwt.decode(
                token,
                self.service_secret,
                algorithms=["HS256"],
                options={"verify_exp": True},
            )

            # Validate constitutional hash in token
            if payload.get("constitutional_hash") != self.constitutional_hash:
                raise HTTPException(
                    status_code=403, detail="Constitutional compliance violation"
                )

            # Add service info to request state
            request.state.service_name = payload.get("service_name")
            request.state.auth_type = "service"

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Service token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid service token")

    async def _validate_user_auth(self, request: Request):
        """Validate user authentication via Auth Service."""
        auth_header = request.headers.get(USER_AUTH_HEADER)
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header")

        token = auth_header[7:]  # Remove "Bearer " prefix

        try:
            # Validate token with Auth Service
            response = await self.http_client.post(
                f"{self.auth_service_url}/api/v1/auth/validate",
                json={"token": token},
                headers={
                    "Content-Type": "application/json",
                    CONSTITUTIONAL_HEADER: self.constitutional_hash,
                },
            )

            if response.status_code != 200:
                raise HTTPException(status_code=401, detail="Token validation failed")

            user_info = response.json()

            # Validate constitutional compliance
            if not user_info.get("valid", False):
                raise HTTPException(status_code=401, detail="Invalid token")

            if user_info.get("constitutional_hash") != self.constitutional_hash:
                raise HTTPException(
                    status_code=403, detail="Constitutional compliance violation"
                )

            # Add user info to request state
            request.state.user_id = user_info.get("user_id")
            request.state.username = user_info.get("username")
            request.state.roles = user_info.get("roles", [])
            request.state.auth_type = "user"

        except httpx.RequestError as e:
            logger.error(f"Auth service request error: {e}")
            raise HTTPException(
                status_code=503, detail="Authentication service unavailable"
            )

    def _add_constitutional_headers(self, response: Response):
        """Add constitutional compliance headers to response."""
        response.headers[CONSTITUTIONAL_HEADER] = self.constitutional_hash
        response.headers["X-Service-Name"] = self.service_name
        response.headers["X-Auth-Required"] = "true"


def create_service_token(
    service_name: str, service_secret: str, expires_in_hours: int = 24
) -> str:
    """
    Create a service-to-service authentication token.

    Args:
        service_name: Name of the service
        service_secret: Secret key for signing
        expires_in_hours: Token expiration time in hours

    Returns:
        JWT token for service authentication
    """
    payload = {
        "service_name": service_name,
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "iat": time.time(),
        "exp": time.time() + (expires_in_hours * 3600),
        "type": "service",
    }

    return jwt.encode(payload, service_secret, algorithm="HS256")


def validate_constitutional_compliance(request: Request) -> bool:
    """
    Validate constitutional compliance in request.

    Args:
        request: FastAPI request object

    Returns:
        True if compliant, False otherwise
    """
    # Check if constitutional hash is in request state
    return getattr(request.state, "constitutional_hash", None) == CONSTITUTIONAL_HASH


class ServiceAuthManager:
    """Manager for service-to-service authentication."""

    def __init__(self, service_name: str, service_secret: str):
        self.service_name = service_name
        self.service_secret = service_secret
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self._token_cache: Optional[str] = None
        self._token_expires: float = 0

    def get_service_token(self) -> str:
        """Get a valid service token, creating new one if needed."""
        current_time = time.time()

        # Check if current token is still valid (with 1 hour buffer)
        if self._token_cache and current_time < (self._token_expires - 3600):
            return self._token_cache

        # Create new token
        self._token_cache = create_service_token(
            self.service_name, self.service_secret, expires_in_hours=24
        )
        self._token_expires = current_time + (24 * 3600)

        return self._token_cache

    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for service requests."""
        return {
            SERVICE_AUTH_HEADER: self.get_service_token(),
            CONSTITUTIONAL_HEADER: self.constitutional_hash,
            "X-Service-Name": self.service_name,
        }

    async def make_authenticated_request(
        self, method: str, url: str, **kwargs
    ) -> httpx.Response:
        """
        Make an authenticated HTTP request to another service.

        Args:
            method: HTTP method
            url: Request URL
            **kwargs: Additional arguments for httpx request

        Returns:
            HTTP response
        """
        headers = kwargs.get("headers", {})
        headers.update(self.get_auth_headers())
        kwargs["headers"] = headers

        async with httpx.AsyncClient() as client:
            response = await client.request(method, url, **kwargs)
            return response
