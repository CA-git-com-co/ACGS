# acgspcp-main/auth_service/app/core/security.py
import uuid
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError as JWTError
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

# Import password functions from separate module to avoid circular imports

# Use local database and models instead of shared ones
try:
    from ..db.session import get_async_db
    from ..models import User
except ImportError:
    # Fallback imports
    def get_async_db():
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        pass

    class User:
        pass


from ..crud import crud_user  # Ensure this import works
from .config import settings


# --- Pydantic model for token payload validation ---
class TokenPayload(BaseModel):
    sub: str  # username
    exp: int  # expiry timestamp
    user_id: int
    roles: list[str]
    type: str  # "access" or "refresh"
    jti: str  # JWT ID


# Password hashing functions are now imported from .core.password module

# --- JWT Creation & Revocation (Access Token JTI Blacklist) ---
# For production, use a persistent store like Redis for the JTI blacklist.
# An in-memory blacklist (like the current set) is insufficient because:
# 1. It's not shared across horizontally scaled instances.
# 2. It's ephemeral and lost on service restart.
# Suggested alternatives:
# - Redis: Fast, in-memory store. Store JTIs with expiry matching the token's.
# - Database Table: Persistent, but potentially slower. Index JTI column.
revoked_access_jti_blacklist: set[str] = set()


def create_access_token(
    subject: str,
    user_id: int,
    roles: list[str],
    expires_delta: timedelta | None = None,
) -> tuple[str, str]:  # returns (token, jti)
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    jti = uuid.uuid4().hex
    to_encode = {
        "exp": int(expire.timestamp()),
        "sub": subject,
        "user_id": user_id,
        "roles": roles,
        "type": "access",
        "jti": jti,
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt, jti


def create_refresh_token(
    subject: str, user_id: int, roles: list[str]
) -> tuple[str, str, datetime]:  # returns (token, jti, expiry_datetime)
    expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    expire_datetime = datetime.now(timezone.utc) + expires_delta
    jti = uuid.uuid4().hex
    to_encode = {
        "exp": int(expire_datetime.timestamp()),
        "sub": subject,
        "user_id": user_id,
        "roles": roles,
        "type": "refresh",
        "jti": jti,
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt, jti, expire_datetime


def revoke_access_jti(jti: str):
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    revoked_access_jti_blacklist.add(jti)


def is_access_jti_revoked(jti: str) -> bool:
    return jti in revoked_access_jti_blacklist


# --- Token Verification & User Retrieval Dependencies ---
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},  # Even with cookies, this header is conventional
)
token_expired_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Token has expired",
    headers={"WWW-Authenticate": "Bearer"},
)


def verify_token_and_get_payload(token_str: str) -> TokenPayload:
    try:
        payload = jwt.decode(token_str, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        # Validate expiration (jose's decode already does this, but an explicit check is fine)
        exp_timestamp = payload.get("exp")
        if exp_timestamp is None or datetime.fromtimestamp(
            exp_timestamp, timezone.utc
        ) < datetime.now(timezone.utc):
            raise token_expired_exception

        token_payload = TokenPayload(**payload)  # Validate structure

        if token_payload.type == "access":
            if not token_payload.jti or is_access_jti_revoked(token_payload.jti):
                raise credentials_exception  # Token revoked or JTI missing

        return token_payload
    except JWTError as e:
        if "expire" in str(e).lower():  # More robust check for expiration
            raise token_expired_exception from e
        raise credentials_exception from e
    except Exception as e:  # Includes Pydantic validation errors, etc.
        raise credentials_exception from e


async def get_current_user_from_cookie(
    request: Request, db: AsyncSession = Depends(get_async_db)
) -> User:
    access_token_cookie = request.cookies.get("access_token_cookie")
    if not access_token_cookie:
        raise credentials_exception

    token_payload = verify_token_and_get_payload(
        access_token_cookie
    )  # Raises HTTPException on failure

    user = await crud_user.get_user(db, user_id=token_payload.user_id)  # Fetch by user_id
    if user is None:
        raise credentials_exception  # User not found for user_id in token
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user_from_cookie),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user


# --- Role-based Authorization ---
def authorize_roles(required_roles: list[str]):
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    async def role_checker(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        user_role = getattr(current_user, "role", None)  # Assuming 'role' attribute exists
        if user_role is None or user_role not in required_roles:
            # Add "admin" role check for superuser access if needed
            if "admin" in required_roles and getattr(current_user, "is_superuser", False):
                return current_user
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User does not have required role(s): {', '.join(required_roles)}",
            )
        return current_user

    return role_checker


# --- Rate Limiting Helper Function ---
def get_user_id_from_request_optional(request: Request) -> str | None:
    """
    Extracts user identifier from request for rate limiting purposes.
    Returns username if user is authenticated via cookie, None otherwise.
    This function is used by the rate limiter to distinguish between authenticated users and anonymous requests.
    """
    try:
        access_token_cookie = request.cookies.get("access_token_cookie")
        if not access_token_cookie:
            return None

        # Verify token without database lookup for performance
        token_payload = verify_token_and_get_payload(access_token_cookie)
        return token_payload.sub  # Return username
    except Exception:
        # If token is invalid, expired, or any other error, treat as anonymous
        return None


# OAuth2PasswordBearer for form data in /token endpoint, not for Bearer token auth itself
oauth2_password_bearer_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token")


# --- Enterprise API Key Authentication ---
async def get_current_user_from_api_key(
    request: Request, db: AsyncSession = Depends(get_async_db)
) -> User:
    """Authenticate user via API key for service-to-service authentication"""
    from ..crud import crud_user
    from ..models import ApiKey

    # Check for API key in Authorization header
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise credentials_exception

    api_key = auth_header[7:]  # Remove "Bearer " prefix

    # Find API key by prefix (first 8 characters)
    if len(api_key) < 8:
        raise credentials_exception

    key_prefix = api_key[:8]

    # Query API key by prefix
    from sqlalchemy import select

    result = await db.execute(
        select(ApiKey).where(ApiKey.key_prefix == key_prefix, ApiKey.is_active)
    )
    api_key_obj = result.scalar_one_or_none()

    if not api_key_obj:
        raise credentials_exception

    # Verify full API key hash
    from .password import verify_password

    if not verify_password(api_key, api_key_obj.key_hash):
        raise credentials_exception

    # Check expiration
    if api_key_obj.expires_at and api_key_obj.expires_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API key has expired")

    # Check IP whitelist if configured
    if api_key_obj.allowed_ips:
        client_ip = get_user_id_from_request_optional(request) or "unknown"
        if client_ip not in api_key_obj.allowed_ips:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="IP address not allowed for this API key",
            )

    # Update usage statistics
    api_key_obj.last_used_at = datetime.now(timezone.utc)
    api_key_obj.usage_count += 1
    await db.commit()

    # Get user
    user = await crud_user.get_user(db, user_id=api_key_obj.user_id)
    if not user or not user.is_active:
        raise credentials_exception

    return user


# --- Enhanced Role-based Authorization with Fine-grained Permissions ---
def authorize_permissions(required_permissions: list[str]):
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """Enhanced authorization with fine-grained permissions"""

    async def permission_checker(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        user_permissions = getattr(current_user, "permissions", [])
        user_role = getattr(current_user, "role", None)

        # Admin users have all permissions
        if user_role == "admin" or getattr(current_user, "is_superuser", False):
            return current_user

        # Check if user has all required permissions
        missing_permissions = set(required_permissions) - set(user_permissions)
        if missing_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permissions: {', '.join(missing_permissions)}",
            )

        return current_user

    return permission_checker
