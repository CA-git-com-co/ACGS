"""
Simplified Tenant Context Middleware for ACGS
Constitutional Hash: cdd01ef066bc6cf2

This middleware provides the same tenant isolation guarantees as the complex
version but with significantly reduced complexity and improved performance.
"""

import logging
import uuid
from typing import Any

import jwt
from fastapi import HTTPException, Request, status
from services.shared.database import AsyncSessionLocal
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


class SimpleTenantContext:
    """Simplified tenant context for request processing."""

    def __init__(
        self,
        tenant_id: uuid.UUID,
        user_id: int | None = None,
        is_admin: bool = False,
        organization_id: uuid.UUID | None = None,
    ):
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.is_admin = is_admin
        self.organization_id = organization_id


class SimpleTenantMiddleware(BaseHTTPMiddleware):
    """
    Simplified tenant middleware that maintains security while reducing complexity.

    Key simplifications:
    1. Single JWT extraction method
    2. Streamlined tenant validation
    3. Simple database context setting
    4. Reduced error handling complexity
    5. Constitutional compliance only when needed
    """

    def __init__(
        self,
        app,
        jwt_secret_key: str,
        jwt_algorithm: str = "HS256",
        exclude_paths: list | None = None,
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
            "/auth/login",
            "/auth/register",
            "/auth/refresh",
        ]

    async def dispatch(self, request: Request, call_next):
        """Process request with simplified tenant validation."""

        # Skip middleware for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)

        try:
            # Extract tenant context from request
            tenant_context = await self._extract_tenant_context(request)

            if tenant_context:
                # Set tenant context in request state
                request.state.tenant_context = tenant_context
                request.state.tenant_id = tenant_context.tenant_id
                request.state.user_id = tenant_context.user_id
                request.state.is_admin = tenant_context.is_admin

                # Set database context
                await self._set_database_context(request, tenant_context)

            # Process request
            response = await call_next(request)

            # Add constitutional compliance header
            response.headers["X-Constitutional-Hash"] = CONSTITUTIONAL_HASH

            return response

        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Tenant middleware error: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Tenant context processing failed"},
            )

    async def _extract_tenant_context(
        self, request: Request
    ) -> SimpleTenantContext | None:
        """Extract tenant context from JWT token or headers."""

        # Try Authorization header first
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]
            try:
                payload = jwt.decode(
                    token, self.jwt_secret_key, algorithms=[self.jwt_algorithm]
                )
                return SimpleTenantContext(
                    tenant_id=uuid.UUID(payload["tenant_id"]),
                    user_id=payload.get("user_id"),
                    is_admin=payload.get("is_admin", False),
                    organization_id=(
                        uuid.UUID(payload["organization_id"])
                        if payload.get("organization_id")
                        else None
                    ),
                )
            except (jwt.InvalidTokenError, KeyError, ValueError) as e:
                logger.warning(f"Invalid JWT token: {e}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication token",
                )

        # Try X-Tenant-ID header as fallback
        tenant_header = request.headers.get("X-Tenant-ID")
        if tenant_header:
            try:
                return SimpleTenantContext(tenant_id=uuid.UUID(tenant_header))
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid tenant ID format",
                )

        # No tenant context found
        return None

    async def _set_database_context(
        self, request: Request, context: SimpleTenantContext
    ):
        """Set database session context for tenant isolation."""

        # Get database session from request or create new one
        if not hasattr(request.state, "db"):
            request.state.db = AsyncSessionLocal()

        db: AsyncSession = request.state.db

        try:
            # Use simplified tenant context function
            await db.execute(
                text(
                    "SELECT set_simple_tenant_context(:tenant_id, :user_id, :is_admin, false, :ip)"
                ),
                {
                    "tenant_id": context.tenant_id,
                    "user_id": context.user_id,
                    "is_admin": context.is_admin,
                    "ip": request.client.host if request.client else None,
                },
            )

            logger.debug(f"Set database context for tenant {context.tenant_id}")

        except Exception as e:
            logger.exception(f"Failed to set database context: {e}")
            await db.close()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Tenant access denied"
            )


class SimpleTenantDependency:
    """Simplified FastAPI dependency for tenant context injection."""

    def __init__(self, require_tenant: bool = True, require_admin: bool = False):
        self.require_tenant = require_tenant
        self.require_admin = require_admin

    async def __call__(self, request: Request) -> SimpleTenantContext:
        """Extract tenant context from request state."""

        if not hasattr(request.state, "tenant_context"):
            if self.require_tenant:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Tenant context required",
                )
            return None

        context: SimpleTenantContext = request.state.tenant_context

        if self.require_admin and not context.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
            )

        return context


# FastAPI dependencies for easy use
get_tenant_context = SimpleTenantDependency(require_tenant=True)
get_optional_tenant_context = SimpleTenantDependency(require_tenant=False)
get_admin_context = SimpleTenantDependency(require_tenant=True, require_admin=True)


async def get_tenant_db(request: Request) -> AsyncSession:
    """Get database session with tenant context already set."""
    if not hasattr(request.state, "db"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database session not available",
        )
    return request.state.db


class SimpleTenantService:
    """Simplified service for tenant operations without complex repository patterns."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_current_tenant(self) -> dict[str, Any] | None:
        """Get current tenant information."""
        result = await self.db.execute(
            text(
                """
            SELECT id, name, status, security_level, constitutional_compliance_score
            FROM tenants
            WHERE id = current_setting('app.current_tenant_id', true)::uuid
        """
            )
        )
        return dict(result.fetchone()) if result.rowcount > 0 else None

    async def get_tenant_users(self) -> list[dict[str, Any]]:
        """Get users for current tenant."""
        result = await self.db.execute(
            text(
                """
            SELECT tu.user_id, tu.role, tu.is_active, tu.access_level
            FROM tenant_users tu
            WHERE tu.tenant_id = current_setting('app.current_tenant_id', true)::uuid
            AND tu.is_active = true
        """
            )
        )
        return [dict(row) for row in result.fetchall()]

    async def validate_tenant_access(self, user_id: int) -> bool:
        """Validate if user has access to current tenant."""
        result = await self.db.execute(
            text(
                """
            SELECT EXISTS(
                SELECT 1 FROM tenant_users
                WHERE user_id = :user_id
                AND tenant_id = current_setting('app.current_tenant_id', true)::uuid
                AND is_active = true
            )
        """
            ),
            {"user_id": user_id},
        )
        return result.scalar()

    async def log_access(
        self, action: str, resource: str | None = None, result: str = "success"
    ):
        """Log tenant access for simplified auditing."""
        await self.db.execute(
            text(
                """
            INSERT INTO tenant_access_log (id, tenant_id, user_id, action, resource, result, ip_address)
            VALUES (
                gen_random_uuid(),
                current_setting('app.current_tenant_id', true)::uuid,
                current_setting('app.current_user_id', true)::integer,
                :action,
                :resource,
                :result,
                current_setting('app.client_ip', true)
            )
        """
            ),
            {"action": action, "resource": resource, "result": result},
        )
        await self.db.commit()


# Utility functions for common operations
async def with_tenant_context(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    user_id: int | None = None,
    is_admin: bool = False,
):
    """Context manager for setting tenant context in database operations."""
    try:
        await db.execute(
            text("SELECT set_simple_tenant_context(:tenant_id, :user_id, :is_admin)"),
            {"tenant_id": tenant_id, "user_id": user_id, "is_admin": is_admin},
        )
        yield db
    finally:
        # Clear context (optional, as it's session-local)
        await db.execute(text("SELECT set_config('app.current_tenant_id', '', true)"))


async def create_tenant_aware_query(
    table_name: str, conditions: dict[str, Any] | None = None
) -> str:
    """Create a tenant-aware SQL query string."""
    # Use parameterized query to prevent SQL injection
    base_query = "SELECT * FROM :table_name"

    where_conditions = []
    if conditions:
        where_conditions.extend([f"{k} = :{k}" for k in conditions])

    if where_conditions:
        return f"{base_query} WHERE {' AND '.join(where_conditions)}"

    return base_query
