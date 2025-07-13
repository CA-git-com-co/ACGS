"""
ACGS Code Analysis Engine - Authentication Middleware
JWT token validation with Auth Service integration and constitutional compliance.

Constitutional Hash: cdd01ef066bc6cf2
"""

import time
from typing import Any

import httpx
from app.utils.constitutional import CONSTITUTIONAL_HASH, validate_constitutional_hash
from app.utils.logging import get_logger, security_logger
from fastapi import HTTPException, Request, Response, status
from fastapi.security import HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware

logger = get_logger("middleware.auth")


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Authentication middleware for ACGS Code Analysis Engine.

    Validates JWT tokens with Auth Service and enforces constitutional compliance.
    """

    def __init__(
        self,
        app,
        auth_service_url: str = "http://localhost:8016",
        excluded_paths: list[str] | None = None,
        timeout_seconds: float = 5.0,
    ):
        """
        Initialize authentication middleware.

        Args:
            app: FastAPI application
            auth_service_url: URL of ACGS Auth Service
            excluded_paths: Paths to exclude from authentication
            timeout_seconds: Timeout for auth service requests
        """
        super().__init__(app)
        self.auth_service_url = auth_service_url.rstrip("/")
        self.excluded_paths = excluded_paths or [
            "/health",
            "/metrics",
            "/docs",
            "/redoc",
            "/openapi.json",
        ]
        self.timeout_seconds = timeout_seconds
        self.http_client = httpx.AsyncClient(timeout=timeout_seconds)
        self.security = HTTPBearer(auto_error=False)

        # Cache for token validation results (simple in-memory cache)
        self._token_cache: dict[str, dict[str, Any]] = {}
        self._cache_ttl = 300  # 5 minutes

        logger.info(
            "Authentication middleware initialized",
            extra={
                "auth_service_url": auth_service_url,
                "excluded_paths": self.excluded_paths,
                "constitutional_hash": CONSTITUTIONAL_HASH,
            },
        )

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request through authentication middleware."""
        start_time = time.time()

        try:
            # Check if path is excluded from authentication
            if self._is_path_excluded(request.url.path):
                response = await call_next(request)
                self._add_constitutional_headers(response)
                return response

            # Extract and validate JWT token
            token = await self._extract_token(request)
            if not token:
                return self._create_auth_error_response("Missing authentication token")

            # Validate token with Auth Service
            user_info = await self._validate_token(token)
            if not user_info:
                return self._create_auth_error_response("Invalid authentication token")

            # Add user context to request
            request.state.user = user_info
            request.state.user_id = user_info.get("user_id")
            request.state.username = user_info.get("username")
            request.state.roles = user_info.get("roles", [])
            request.state.permissions = user_info.get("permissions", [])

            # Log successful authentication
            security_logger.log_authentication_event(
                event_type="token_validation",
                user_id=user_info.get("user_id"),
                success=True,
                request_path=request.url.path,
                request_method=request.method,
            )

            # Process request
            response = await call_next(request)

            # Add constitutional compliance headers
            self._add_constitutional_headers(response)

            # Log response
            duration_ms = (time.time() - start_time) * 1000
            logger.info(
                "Authentication middleware completed",
                extra={
                    "user_id": user_info.get("user_id"),
                    "duration_ms": round(duration_ms, 2),
                    "status_code": response.status_code,
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                },
            )

            return response

        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                f"Authentication middleware error: {e}",
                extra={
                    "error_type": type(e).__name__,
                    "request_path": request.url.path,
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                },
                exc_info=True,
            )
            return self._create_auth_error_response("Authentication service error")

    def _is_path_excluded(self, path: str) -> bool:
        """Check if path is excluded from authentication."""
        return any(path.startswith(excluded) for excluded in self.excluded_paths)

    async def _extract_token(self, request: Request) -> str | None:
        """Extract JWT token from request headers."""
        authorization = request.headers.get("Authorization")
        if not authorization:
            return None

        if not authorization.startswith("Bearer "):
            return None

        return authorization[7:]  # Remove "Bearer " prefix

    async def _validate_token(self, token: str) -> dict[str, Any] | None:
        """
        Validate JWT token with Auth Service.

        Args:
            token: JWT token to validate

        Returns:
            dict: User information if valid, None otherwise
        """
        # Check cache first
        cached_result = self._get_cached_token(token)
        if cached_result:
            return cached_result

        try:
            # Validate with Auth Service
            response = await self.http_client.post(
                f"{self.auth_service_url}/api/v1/auth/validate",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                json={
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                    "service": "acgs-code-analysis-engine",
                },
            )

            if response.status_code == 200:
                user_info = response.json()

                # Validate constitutional compliance
                if not self._validate_auth_response(user_info):
                    logger.warning(
                        "Auth service response failed constitutional validation",
                        extra={"constitutional_hash": CONSTITUTIONAL_HASH},
                    )
                    return None

                # Cache successful validation
                self._cache_token(token, user_info)

                return user_info
            logger.warning(
                f"Auth service validation failed: {response.status_code}",
                extra={
                    "status_code": response.status_code,
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                },
            )
            return None

        except httpx.RequestError as e:
            logger.error(
                f"Auth service request error: {e}",
                extra={
                    "auth_service_url": self.auth_service_url,
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                },
                exc_info=True,
            )
            return None

    def _validate_auth_response(self, user_info: dict[str, Any]) -> bool:
        """Validate constitutional compliance of auth service response."""
        # Check for constitutional hash
        auth_hash = user_info.get("constitutional_hash")
        if not auth_hash or not validate_constitutional_hash(auth_hash):
            return False

        # Check for required fields
        required_fields = ["user_id", "username", "valid"]
        for field in required_fields:
            if field not in user_info:
                return False

        # Check if token is marked as valid
        return user_info.get("valid", False)

    def _get_cached_token(self, token: str) -> dict[str, Any] | None:
        """Get cached token validation result."""
        if token not in self._token_cache:
            return None

        cached_data = self._token_cache[token]
        if time.time() - cached_data["timestamp"] > self._cache_ttl:
            del self._token_cache[token]
            return None

        return cached_data["user_info"]

    def _cache_token(self, token: str, user_info: dict[str, Any]) -> None:
        """Cache token validation result."""
        # Simple cache cleanup - remove oldest entries if cache is too large
        if len(self._token_cache) > 1000:
            oldest_token = min(
                self._token_cache.keys(),
                key=lambda k: self._token_cache[k]["timestamp"],
            )
            del self._token_cache[oldest_token]

        self._token_cache[token] = {"user_info": user_info, "timestamp": time.time()}

    def _add_constitutional_headers(self, response: Response) -> None:
        """Add constitutional compliance headers to response."""
        response.headers["X-Constitutional-Hash"] = CONSTITUTIONAL_HASH
        response.headers["X-Constitutional-Compliance"] = "validated"
        response.headers["X-Service"] = "acgs-code-analysis-engine"

    def _create_auth_error_response(self, message: str) -> Response:
        """Create standardized authentication error response."""
        error_response = {
            "error": "authentication_required",
            "message": message,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "service": "acgs-code-analysis-engine",
        }

        return Response(
            content=str(error_response).replace("'", '"'),
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={
                "Content-Type": "application/json",
                "WWW-Authenticate": "Bearer",
                "X-Constitutional-Hash": CONSTITUTIONAL_HASH,
            },
        )

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.http_client.aclose()
