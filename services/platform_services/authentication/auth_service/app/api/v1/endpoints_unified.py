# backend/auth_service/app/api/v1/endpoints_unified.py
# Updated Authentication Service with Unified Response Format

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_csrf_protect import CsrfProtect
from jose import JWTError, jwt  # For decoding in /logout and /token/refresh

# Create simple schemas locally since shared ones are not available
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

# Application-specific imports
from ...core import security
from ...core.config import settings
from ...crud import (  # crud_refresh_token was created earlier
    crud_refresh_token,
    crud_user,
)
from ...models import User  # RefreshToken model not directly used here, but in crud
from . import deps  # Assuming deps.get_db is correctly defined for AsyncSession

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
    print("Warning: Unified response module not available, using legacy format")


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str | None = None


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
            else:
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
            else:
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
        else:
            return user_data

    except Exception as e:
        if UNIFIED_RESPONSE_AVAILABLE:
            error_response = response_builder.error(
                message="Failed to register user",
                data={"error_details": str(e)},
                error_code="REGISTRATION_FAILED",
            )
            return UnifiedJSONResponse(content=error_response, status_code=500)
        else:
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
            else:
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
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
                )

        # Create access token
        access_token_str, access_jti = security.create_access_token(
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
        csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
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
        else:
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
        else:
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
        else:
            return {"message": "Logout successful"}

    except Exception as e:
        if UNIFIED_RESPONSE_AVAILABLE:
            error_response = response_builder.error(
                message="Logout failed",
                data={"error_details": str(e)},
                error_code="LOGOUT_FAILED",
            )
            return UnifiedJSONResponse(content=error_response, status_code=500)
        else:
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
        else:
            return user_data

    except Exception as e:
        if UNIFIED_RESPONSE_AVAILABLE:
            error_response = response_builder.error(
                message="Failed to retrieve user information",
                data={"error_details": str(e)},
                error_code="USER_INFO_FAILED",
            )
            return UnifiedJSONResponse(content=error_response, status_code=500)
        else:
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
    else:
        return health_data


# Include this router in the main FastAPI app
# Example: app.include_router(endpoints_unified.router, prefix="/api/v1/auth", tags=["auth"])
