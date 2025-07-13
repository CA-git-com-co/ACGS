# backend/auth_service/app/api/v1/endpoints_unified.py
# Updated Authentication Service with Unified Response Format

import pathlib

# Application-specific imports
from app.core import security
from app.core.config import settings
from app.crud import crud_refresh_token, crud_user
from app.models import User  # RefreshToken model not directly used here, but in crud
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_csrf_protect import CsrfProtect
from jose import JWTError, jwt  # For decoding in /logout and /token/refresh

# Create simple schemas locally since shared ones are not available
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from . import deps  # Assuming deps.get_db is correctly defined for AsyncSession

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Import unified response utilities
try:
    from services.shared.response.unified_response import (
        ResponseBuilder,
        UnifiedJSONResponse,
        create_auth_response_builder,
        get_response_builder,
    )

    UNIFIED_RESPONSE_AVAILABLE = True
except ImportError:
    # Fallback for when shared module is not available
    UNIFIED_RESPONSE_AVAILABLE = False


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str | None = None


class TokenValidationRequest(BaseModel):
    token: str
    constitutional_hash: str


class TokenValidationResponse(BaseModel):
    valid: bool
    user_id: int | None = None
    username: str | None = None
    roles: list[str] | None = None
    reason: str | None = None
    constitutional_hash: str
    validated_at: str


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    first_name: str | None = None
    last_name: str | None = None


class UserInDB(BaseModel):
    id: int
    username: str
    email: str
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool
    is_superuser: bool

    class Config:
        from_attributes = True


router = APIRouter()

# Determine if cookies should be secure based on environment setting
# Fallback to True if not explicitly set to "development"
SECURE_COOKIE = getattr(settings, "ENVIRONMENT", "production") != "development"


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(
    user: UserCreate, db: AsyncSession = Depends(deps.get_db), request: Request = None
):
    """Register a new user with unified response format."""

    # Create response builder
    if UNIFIED_RESPONSE_AVAILABLE:
        response_builder = create_auth_response_builder()
        if request:
            response_builder.set_request_context(request)

    try:
        # Check if username already exists
        db_user_by_username = await crud_user.get_user_by_username(
            db, username=user.username
        )
        if db_user_by_username:
            if UNIFIED_RESPONSE_AVAILABLE:
                error_response = response_builder.error(
                    message="Username already registered", error_code="USERNAME_EXISTS"
                )
                return UnifiedJSONResponse(content=error_response, status_code=400)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )

        # Check if email already exists
        db_user_by_email = await crud_user.get_user_by_email(db, email=user.email)
        if db_user_by_email:
            if UNIFIED_RESPONSE_AVAILABLE:
                error_response = response_builder.error(
                    message="Email already registered", error_code="EMAIL_EXISTS"
                )
                return UnifiedJSONResponse(content=error_response, status_code=400)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Create user
        created_user = await crud_user.create_user(db=db, obj_in=user)

        # Convert to response format
        user_data = {
            "id": created_user.id,
            "username": created_user.username,
            "email": created_user.email,
            "first_name": created_user.first_name,
            "last_name": created_user.last_name,
            "is_active": created_user.is_active,
            "is_superuser": created_user.is_superuser,
        }

        if UNIFIED_RESPONSE_AVAILABLE:
            success_response = response_builder.success(
                data=user_data, message="User registered successfully"
            )
            return UnifiedJSONResponse(content=success_response, status_code=201)
        return user_data

    except Exception as e:
        if UNIFIED_RESPONSE_AVAILABLE:
            error_response = response_builder.error(
                message="Failed to register user",
                data={"error_details": str(e)},
                error_code="REGISTRATION_FAILED",
            )
            return UnifiedJSONResponse(content=error_response, status_code=500)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user",
        )


@router.post("/token")
@router.post("/login")  # Add alias for compatibility
async def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(deps.get_db),
    csrf_protect: CsrfProtect = Depends(),
    request: Request = None,
):
    """Authenticate user and return access token with unified response format."""

    # Create response builder
    if UNIFIED_RESPONSE_AVAILABLE:
        response_builder = create_auth_response_builder()
        if request:
            response_builder.set_request_context(request)

    try:
        # Authenticate user
        user_obj = await crud_user.get_user_by_username(db, username=form_data.username)
        if not user_obj or not security.verify_password(
            form_data.password, user_obj.hashed_password
        ):
            if UNIFIED_RESPONSE_AVAILABLE:
                error_response = response_builder.error(
                    message="Incorrect username or password",
                    error_code="INVALID_CREDENTIALS",
                )
                return UnifiedJSONResponse(content=error_response, status_code=401)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user_obj.is_active:
            if UNIFIED_RESPONSE_AVAILABLE:
                error_response = response_builder.error(
                    message="User account is inactive", error_code="INACTIVE_USER"
                )
                return UnifiedJSONResponse(content=error_response, status_code=400)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
            )

        # Create access token
        access_token_str, _access_jti = security.create_access_token(
            subject=user_obj.username, user_id=user_obj.id, roles=[user_obj.role]
        )

        # Create refresh token
        refresh_token_str, refresh_jti, refresh_expires_at = (
            security.create_refresh_token(
                subject=user_obj.username, user_id=user_obj.id, roles=[user_obj.role]
            )
        )
        await crud_refresh_token.create_refresh_token(
            db,
            user_id=user_obj.id,
            token=refresh_token_str,
            jti=refresh_jti,
            expires_at=refresh_expires_at,
        )

        # Set CSRF token using correct API
        _csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
        csrf_protect.set_csrf_cookie(signed_token, response)

        # Set HttpOnly cookies for tokens
        access_token_expires_seconds = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        refresh_token_expires_seconds = (
            settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        )

        response.set_cookie(
            key="access_token_cookie",
            value=access_token_str,
            httponly=True,
            max_age=access_token_expires_seconds,
            expires=access_token_expires_seconds,  # For older browsers
            path="/",
            secure=SECURE_COOKIE,
            samesite="lax",  # Or "strict"
        )
        response.set_cookie(
            key="refresh_token_cookie",
            value=refresh_token_str,
            httponly=True,
            max_age=refresh_token_expires_seconds,
            expires=refresh_token_expires_seconds,  # For older browsers
            path="/auth/token/refresh",  # Path specific to refresh endpoint
            secure=SECURE_COOKIE,
            samesite="lax",  # Or "strict"
        )

        # Prepare token data
        token_data = {
            "access_token": access_token_str,
            "token_type": "bearer",
            "expires_in": access_token_expires_seconds,
            "user": {
                "id": user_obj.id,
                "username": user_obj.username,
                "email": user_obj.email,
                "role": user_obj.role,
            },
        }

        if UNIFIED_RESPONSE_AVAILABLE:
            success_response = response_builder.success(
                data=token_data, message="Authentication successful"
            )
            return UnifiedJSONResponse(content=success_response)
        return Token(
            access_token=access_token_str, token_type="bearer", refresh_token=None
        )

    except Exception as e:
        if UNIFIED_RESPONSE_AVAILABLE:
            error_response = response_builder.error(
                message="Authentication failed",
                data={"error_details": str(e)},
                error_code="AUTH_FAILED",
            )
            return UnifiedJSONResponse(content=error_response, status_code=500)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed",
        )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(deps.get_db),
    csrf_protect: CsrfProtect = Depends(),
):
    """Logout user and revoke tokens with unified response format."""

    # Create response builder
    if UNIFIED_RESPONSE_AVAILABLE:
        response_builder = create_auth_response_builder()
        response_builder.set_request_context(request)

    try:
        await csrf_protect.validate_csrf(request)

        access_token_cookie = request.cookies.get("access_token_cookie")
        if access_token_cookie:
            try:
                # Decode access token to get JTI, ignore expiration for revocation
                payload = jwt.decode(
                    access_token_cookie,
                    settings.SECRET_KEY,
                    algorithms=[settings.ALGORITHM],
                    options={"verify_exp": False},
                )
                token_data = security.TokenPayload(**payload)
                if token_data.type == "access" and token_data.jti:
                    security.revoke_access_jti(token_data.jti)
            except JWTError:
                pass  # Ignore if token is invalid, just try to delete cookie

        refresh_token_cookie = request.cookies.get("refresh_token_cookie")
        if refresh_token_cookie:
            try:
                # Decode refresh token to get JTI and user_id for targeted revocation
                payload = jwt.decode(
                    refresh_token_cookie,
                    settings.SECRET_KEY,
                    algorithms=[settings.ALGORITHM],
                    options={"verify_exp": False},
                )
                token_data = security.TokenPayload(**payload)
                if (
                    token_data.type == "refresh"
                    and token_data.jti
                    and token_data.user_id
                ):
                    await crud_refresh_token.revoke_refresh_token(
                        db, jti=token_data.jti, user_id=token_data.user_id
                    )
            except JWTError:
                pass  # Ignore if token is invalid

        # Delete cookies
        response.delete_cookie(
            key="access_token_cookie",
            path="/",
            secure=SECURE_COOKIE,
            httponly=True,
            samesite="lax",
        )
        response.delete_cookie(
            key="refresh_token_cookie",
            path="/auth/token/refresh",
            secure=SECURE_COOKIE,
            httponly=True,
            samesite="lax",
        )
        csrf_protect.unset_csrf_cookie(
            response
        )  # Deletes CSRF cookie to prevent token reuse

        if UNIFIED_RESPONSE_AVAILABLE:
            success_response = response_builder.success(
                data={"logout": True}, message="Logout successful"
            )
            return UnifiedJSONResponse(content=success_response)
        return {"message": "Logout successful"}

    except Exception:
        if UNIFIED_RESPONSE_AVAILABLE:
            error_response = response_builder.error(
                message="Logout failed", error_code="LOGOUT_ERROR"
            )
            return UnifiedJSONResponse(content=error_response, status_code=500)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed",
        )


@router.post("/validate", response_model=TokenValidationResponse)
async def validate_token(
    request: TokenValidationRequest,
    db: AsyncSession = Depends(deps.get_db),
):
    """
    Validate JWT token with constitutional compliance.

    Critical security endpoint that validates tokens from other services.
    Optimized with multi-tier caching for sub-5ms P99 latency.
    """
    import hashlib
    import os

    # Import multi-tier cache
    import sys
    import time
    from datetime import datetime

    sys.path.append(
        os.path.join(
            pathlib.Path(__file__).parent, "../../../../../../shared/performance"
        )
    )
    try:
        from multi_tier_cache import cache_jwt_validation, get_cached_jwt_validation
    except ImportError:
        # Fallback if cache not available
        get_cached_jwt_validation = None
        cache_jwt_validation = None

    start_time = time.perf_counter()

    # Validate constitutional hash in request
    if request.constitutional_hash != CONSTITUTIONAL_HASH:
        return TokenValidationResponse(
            valid=False,
            reason="Invalid constitutional hash",
            constitutional_hash=CONSTITUTIONAL_HASH,
            validated_at=datetime.now().isoformat(),
        )

    try:
        # Generate cache key for token validation
        token_hash = hashlib.sha256(request.token.encode()).hexdigest()[:16]

        # Check cache first for JWT validation result
        cached_result = None
        if get_cached_jwt_validation:
            try:
                cached_result = await get_cached_jwt_validation(token_hash)
                if cached_result:
                    # Return cached validation result
                    cached_result["validated_at"] = datetime.now().isoformat()
                    cached_result["cache_hit"] = True
                    processing_time = (time.perf_counter() - start_time) * 1000
                    cached_result["processing_time_ms"] = processing_time
                    return TokenValidationResponse(**cached_result)
            except Exception:
                # Log cache error but continue with validation
                pass

        # Validate the JWT token
        payload = security.verify_token(request.token)

        if not payload:
            validation_result = {
                "valid": False,
                "reason": "Invalid or expired token",
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "validated_at": datetime.now().isoformat(),
            }
            return TokenValidationResponse(**validation_result)

        # Get user information (this is the expensive database operation)
        user_obj = await crud_user.get_user_by_id(db, user_id=payload.user_id)
        if not user_obj or not user_obj.is_active:
            validation_result = {
                "valid": False,
                "reason": "User not found or inactive",
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "validated_at": datetime.now().isoformat(),
            }
            return TokenValidationResponse(**validation_result)

        # Create successful validation result
        validation_result = {
            "valid": True,
            "user_id": user_obj.id,
            "username": user_obj.username,
            "roles": [user_obj.role] if user_obj.role else [],
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "validated_at": datetime.now().isoformat(),
            "cache_hit": False,
        }

        # Cache the successful validation result (1 hour TTL)
        if cache_jwt_validation:
            try:
                await cache_jwt_validation(token_hash, validation_result)
            except Exception:
                # Log cache error but don't fail the request
                pass

        processing_time = (time.perf_counter() - start_time) * 1000
        validation_result["processing_time_ms"] = processing_time

        return TokenValidationResponse(**validation_result)

    except Exception as e:
        validation_result = {
            "valid": False,
            "reason": f"Token validation error: {e!s}",
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "validated_at": datetime.now().isoformat(),
        }
        return TokenValidationResponse(**validation_result)

    except Exception as e:
        if UNIFIED_RESPONSE_AVAILABLE:
            error_response = response_builder.error(
                message="Logout failed",
                data={"error_details": str(e)},
                error_code="LOGOUT_FAILED",
            )
            return UnifiedJSONResponse(content=error_response, status_code=500)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed",
        )


@router.get("/me")
async def read_users_me(
    current_user: User = Depends(security.get_current_active_user),
    request: Request = None,
):
    """Get current user information with unified response format."""

    # Create response builder
    if UNIFIED_RESPONSE_AVAILABLE:
        response_builder = create_auth_response_builder()
        if request:
            response_builder.set_request_context(request)

    try:
        # Convert user to response format
        user_data = {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
            "is_active": current_user.is_active,
            "is_superuser": current_user.is_superuser,
            "role": current_user.role,
        }

        if UNIFIED_RESPONSE_AVAILABLE:
            success_response = response_builder.success(
                data=user_data, message="User information retrieved successfully"
            )
            return UnifiedJSONResponse(content=success_response)
        return user_data

    except Exception as e:
        if UNIFIED_RESPONSE_AVAILABLE:
            error_response = response_builder.error(
                message="Failed to retrieve user information",
                data={"error_details": str(e)},
                error_code="USER_INFO_FAILED",
            )
            return UnifiedJSONResponse(content=error_response, status_code=500)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user information",
        )


# Health endpoint with unified response format
@router.get("/health")
async def health_check(request: Request = None):
    """Health check endpoint with unified response format."""

    # Create response builder
    if UNIFIED_RESPONSE_AVAILABLE:
        response_builder = create_auth_response_builder()
        if request:
            response_builder.set_request_context(request)

    health_data = {
        "status": "healthy",
        "service": "authentication-service",
        "version": "2.1.0",
        "timestamp": "2025-06-22T10:30:00Z",
    }

    if UNIFIED_RESPONSE_AVAILABLE:
        success_response = response_builder.success(
            data=health_data, message="Authentication service is healthy"
        )
        return UnifiedJSONResponse(content=success_response)
    return health_data


# Include this router in the main FastAPI app
# Example: app.include_router(endpoints_unified.router, prefix="/api/v1/auth", tags=["auth"])
