"""
Tenant Context Middleware for ACGS Multi-Tenant Architecture

This middleware automatically extracts tenant context from requests,
validates tenant access, and sets up proper isolation for all database
operations and API responses.

Constitutional Hash: cdd01ef066bc6cf2
"""

import logging
import uuid
from collections.abc import Callable
from contextlib import asynccontextmanager

import jwt
from fastapi import HTTPException, Request, Response, status
from fastapi.security import HTTPBearer
from services.shared.database import AsyncSessionLocal
from services.shared.repositories.tenant_repository import (
    ConstitutionalComplianceError,
    TenantContext,
    TenantIsolationError,
    validate_tenant_context,
)
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


class TenantContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware that extracts and validates tenant context from requests.

    This middleware:
    1. Extracts tenant information from JWT tokens or headers
    2. Validates user access to the requested tenant
    3. Sets up tenant context for database operations
    4. Ensures constitutional compliance
    5. Provides tenant isolation enforcement
    """

    def __init__(
        self,
        app,
        jwt_secret_key: str,
        jwt_algorithm: str = "HS256",
        exclude_paths: list | None = None,
        require_tenant: bool = True,
        bypass_paths: list | None = None,
    ):
        super().__init__(app)
        self.jwt_secret_key = jwt_secret_key
        self.jwt_algorithm = jwt_algorithm
        self.exclude_paths = exclude_paths or [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
            "/metrics",
        ]
        self.require_tenant = require_tenant
        self.bypass_paths = bypass_paths or [
            "/auth/login",
            "/auth/register",
            "/auth/refresh",
            "/tenants/validate",
            "/organizations/create",
        ]
        self.security = HTTPBearer(auto_error=False)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process each request with tenant context validation."""

        # Skip middleware for excluded paths
        if self._should_exclude_path(request.url.path):
            return await call_next(request)

        try:
            # Extract tenant context from request
            tenant_context = await self._extract_tenant_context(request)

            # Set tenant context in request state
            request.state.tenant_context = tenant_context

            # Set database session context if tenant context exists
            if tenant_context:
                request.state.tenant_id = tenant_context.tenant_id
                request.state.user_id = tenant_context.user_id
                request.state.organization_id = tenant_context.organization_id
                request.state.security_level = tenant_context.security_level

            # Process request
            response = await call_next(request)

            # Add tenant-related headers to response
            if tenant_context:
                response.headers["X-Tenant-ID"] = str(tenant_context.tenant_id)
                response.headers["X-Constitutional-Hash"] = CONSTITUTIONAL_HASH
                response.headers["X-Security-Level"] = (
                    tenant_context.security_level or "basic"
                )

            return response

        except TenantIsolationError as e:
            logger.warning(f"Tenant isolation error: {e}")
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "error": "tenant_access_denied",
                    "message": str(e),
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                },
            )

        except ConstitutionalComplianceError as e:
            logger.exception(f"Constitutional compliance error: {e}")
            return JSONResponse(
                status_code=status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS,
                content={
                    "error": "constitutional_compliance_violation",
                    "message": str(e),
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                },
            )

        except HTTPException:
            raise

        except Exception as e:
            logger.exception(f"Tenant middleware error: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "tenant_context_error",
                    "message": "Failed to establish tenant context",
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                },
            )

    def _should_exclude_path(self, path: str) -> bool:
        """Check if path should be excluded from tenant validation."""
        return any(path.startswith(excluded) for excluded in self.exclude_paths)

    def _should_bypass_tenant_requirement(self, path: str) -> bool:
        """Check if path should bypass tenant requirement."""
        return any(path.startswith(bypass) for bypass in self.bypass_paths)

    async def _extract_tenant_context(self, request: Request) -> TenantContext | None:
        """Extract tenant context from request headers and JWT token."""

        # Check if tenant requirement can be bypassed
        if self._should_bypass_tenant_requirement(request.url.path):
            return None

        # Extract tenant ID from headers (primary method)
        tenant_id_header = request.headers.get("X-Tenant-ID")

        # Extract JWT token for user authentication
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            if self.require_tenant:
                raise TenantIsolationError("Missing or invalid authorization token")
            return None

        token = authorization.split(" ")[1]

        try:
            # Decode JWT token
            payload = jwt.decode(
                token, self.jwt_secret_key, algorithms=[self.jwt_algorithm]
            )

            user_id = payload.get("sub")
            if not user_id:
                raise TenantIsolationError("Invalid token: missing user ID")

            # Get tenant ID from token or header
            tenant_id_token = payload.get("tenant_id")
            tenant_id = tenant_id_header or tenant_id_token

            if not tenant_id and self.require_tenant:
                raise TenantIsolationError("Tenant ID required but not provided")

            if not tenant_id:
                return None

            # Convert tenant_id to UUID
            try:
                tenant_uuid = uuid.UUID(tenant_id)
            except ValueError:
                raise TenantIsolationError("Invalid tenant ID format")

            # Validate tenant context with database
            async with AsyncSessionLocal() as session:
                return await validate_tenant_context(
                    session=session, tenant_id=tenant_uuid, user_id=int(user_id)
                )

        except jwt.ExpiredSignatureError:
            raise TenantIsolationError("Token has expired")
        except jwt.InvalidTokenError:
            raise TenantIsolationError("Invalid token")
        except ValueError as e:
            raise TenantIsolationError(f"Invalid user ID in token: {e}")


class TenantDatabaseMiddleware:
    """
    Middleware for setting tenant context in database sessions.

    This middleware ensures that all database operations within a request
    are automatically filtered by the current tenant context.
    """

    @staticmethod
    async def set_session_context(session: AsyncSession, tenant_context: TenantContext):
        """Set tenant context for a database session."""
        if tenant_context:
            # Set PostgreSQL session variables for RLS
            await session.execute(
                "SELECT set_tenant_context(:user_id, :tenant_id, false)",
                {
                    "user_id": tenant_context.user_id,
                    "tenant_id": tenant_context.tenant_id,
                },
            )

    @staticmethod
    async def clear_session_context(session: AsyncSession):
        """Clear tenant context from a database session."""
        try:
            await session.execute("SELECT set_tenant_context(NULL, NULL, true)")
        except Exception:
            # Ignore errors when clearing context
            pass


# Dependency for FastAPI routes to get tenant context
async def get_tenant_context(request: Request) -> TenantContext:
    """
    FastAPI dependency to get the current tenant context.

    Raises HTTPException if no tenant context is available.
    """
    tenant_context = getattr(request.state, "tenant_context", None)
    if not tenant_context:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Tenant context required"
        )
    return tenant_context


async def get_optional_tenant_context(request: Request) -> TenantContext | None:
    """
    FastAPI dependency to get the current tenant context (optional).

    Returns None if no tenant context is available.
    """
    return getattr(request.state, "tenant_context", None)


# Dependency for FastAPI routes to get tenant-aware database session
async def get_tenant_db(request: Request) -> AsyncSession:
    """
    FastAPI dependency to get a tenant-aware database session.

    The session will have tenant context automatically applied.
    """
    tenant_context = getattr(request.state, "tenant_context", None)

    async with AsyncSessionLocal() as session:
        try:
            # Set tenant context if available
            if tenant_context:
                await TenantDatabaseMiddleware.set_session_context(
                    session, tenant_context
                )

            yield session

        except Exception:
            await session.rollback()
            raise
        finally:
            # Clear tenant context
            if tenant_context:
                await TenantDatabaseMiddleware.clear_session_context(session)


@asynccontextmanager
async def tenant_database_session(tenant_context: TenantContext):
    """
    Context manager for creating tenant-aware database sessions.

    Usage:
        async with tenant_database_session(tenant_context) as session:
            # Database operations here will be tenant-filtered
            pass
    """
    async with AsyncSessionLocal() as session:
        try:
            await TenantDatabaseMiddleware.set_session_context(session, tenant_context)
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await TenantDatabaseMiddleware.clear_session_context(session)


class TenantSecurityMiddleware(BaseHTTPMiddleware):
    """
    Additional security middleware for tenant-specific security policies.

    Enforces tenant-specific security controls such as:
    - Rate limiting per tenant
    - IP whitelisting per tenant
    - Security level enforcement
    - Constitutional compliance validation
    """

    def __init__(self, app):
        super().__init__(app)
        self.rate_limiter = {}  # Simple in-memory rate limiter

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Apply tenant-specific security controls."""

        tenant_context = getattr(request.state, "tenant_context", None)

        # Apply security controls if tenant context exists
        if tenant_context:
            # Check constitutional compliance
            if tenant_context.constitutional_compliance_required:
                if not await self._validate_constitutional_compliance(tenant_context):
                    return JSONResponse(
                        status_code=status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS,
                        content={
                            "error": "constitutional_compliance_required",
                            "message": (
                                "Tenant does not meet constitutional compliance"
                                " requirements"
                            ),
                            "constitutional_hash": CONSTITUTIONAL_HASH,
                        },
                    )

            # Apply rate limiting
            if not await self._check_rate_limit(request, tenant_context):
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "error": "rate_limit_exceeded",
                        "message": "Tenant rate limit exceeded",
                        "constitutional_hash": CONSTITUTIONAL_HASH,
                    },
                )

            # Apply security level controls
            if not await self._check_security_level(request, tenant_context):
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={
                        "error": "security_level_insufficient",
                        "message": "Request requires higher security level",
                        "constitutional_hash": CONSTITUTIONAL_HASH,
                    },
                )

        return await call_next(request)

    async def _validate_constitutional_compliance(
        self, tenant_context: TenantContext
    ) -> bool:
        """Validate that tenant meets constitutional compliance requirements."""
        try:
            # Check constitutional hash compliance
            if not hasattr(tenant_context, "constitutional_hash"):
                return False

            # Validate constitutional hash matches current version
            tenant_hash = getattr(tenant_context, "constitutional_hash", None)
            if tenant_hash != CONSTITUTIONAL_HASH:
                logger.warning(
                    "Constitutional hash mismatch for tenant"
                    f" {tenant_context.tenant_id}: expected {CONSTITUTIONAL_HASH}, got"
                    f" {tenant_hash}"
                )
                return False

            # Check if tenant has valid compliance score
            compliance_score = getattr(tenant_context, "compliance_score", 0)
            minimum_compliance_score = 80  # 80% minimum compliance

            if compliance_score < minimum_compliance_score:
                logger.warning(
                    f"Tenant {tenant_context.tenant_id} compliance score too low: "
                    f"{compliance_score} < {minimum_compliance_score}"
                )
                return False

            return True

        except Exception as e:
            logger.exception(f"Constitutional compliance validation error: {e}")
            return False

    async def _check_rate_limit(
        self, request: Request, tenant_context: TenantContext
    ) -> bool:
        """Check if request is within tenant rate limits."""
        try:
            import time
            from collections import defaultdict

            # Simple sliding window rate limiter
            if not hasattr(self, "_rate_limit_windows"):
                self._rate_limit_windows = defaultdict(list)

            tenant_id = str(tenant_context.tenant_id)
            client_ip = request.client.host if request.client else "unknown"
            key = f"{tenant_id}:{client_ip}"

            current_time = time.time()
            window_size = 3600  # 1 hour window

            # Get tenant-specific rate limit (requests per hour)
            rate_limit = getattr(tenant_context, "api_rate_limit_per_hour", 1000)

            # Clean old entries from sliding window
            self._rate_limit_windows[key] = [
                timestamp
                for timestamp in self._rate_limit_windows[key]
                if current_time - timestamp < window_size
            ]

            # Check if within rate limit
            current_requests = len(self._rate_limit_windows[key])
            if current_requests >= rate_limit:
                logger.warning(
                    f"Rate limit exceeded for tenant {tenant_id} from {client_ip}: "
                    f"{current_requests}/{rate_limit} requests in last hour"
                )
                return False

            # Add current request to window
            self._rate_limit_windows[key].append(current_time)

            # Log high usage warnings
            if current_requests > rate_limit * 0.8:  # 80% of limit
                logger.warning(
                    f"High API usage for tenant {tenant_id}: "
                    f"{current_requests}/{rate_limit} requests"
                )

            return True

        except Exception as e:
            logger.exception(f"Rate limiting check failed: {e}")
            # Fail open - allow request if rate limiting fails
            return True

    async def _check_security_level(
        self, request: Request, tenant_context: TenantContext
    ) -> bool:
        """Check if request meets tenant security level requirements."""
        # Implement security level checks based on endpoint and tenant configuration

        security_level = tenant_context.security_level

        # Define security requirements for different endpoints
        high_security_paths = ["/admin", "/constitutional", "/governance"]

        if any(request.url.path.startswith(path) for path in high_security_paths):
            return security_level in {"strict", "maximum"}

        return True


# Utility functions for tenant context management
def get_current_tenant_id(request: Request) -> uuid.UUID | None:
    """Get the current tenant ID from request state."""
    return getattr(request.state, "tenant_id", None)


def get_current_user_id(request: Request) -> int | None:
    """Get the current user ID from request state."""
    return getattr(request.state, "user_id", None)


def get_current_organization_id(request: Request) -> uuid.UUID | None:
    """Get the current organization ID from request state."""
    return getattr(request.state, "organization_id", None)


def require_tenant_context(func):
    """
    Decorator to ensure a route has tenant context.

    Usage:
        @app.get("/protected")
        @require_tenant_context
        async def protected_endpoint(request: Request):
            # This endpoint requires tenant context
            pass
    """

    async def wrapper(request: Request, *args, **kwargs):
        tenant_context = getattr(request.state, "tenant_context", None)
        if not tenant_context:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tenant context required for this operation",
            )
        return await func(request, *args, **kwargs)

    return wrapper


def require_security_level(min_level: str):
    """
    Decorator to ensure a route meets minimum security level.

    Usage:
        @app.get("/high-security")
        @require_security_level("strict")
        async def high_security_endpoint(request: Request):
            # This endpoint requires strict security level
            pass
    """

    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            tenant_context = getattr(request.state, "tenant_context", None)
            if not tenant_context:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Tenant context required",
                )

            security_levels = {"basic": 1, "moderate": 2, "strict": 3, "maximum": 4}
            current_level = security_levels.get(tenant_context.security_level, 0)
            required_level = security_levels.get(min_level, 4)

            if current_level < required_level:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Security level '{min_level}' required",
                )

            return await func(request, *args, **kwargs)

        return wrapper

    return decorator
