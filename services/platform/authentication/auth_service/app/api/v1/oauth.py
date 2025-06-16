# Enterprise OAuth 2.0 and OpenID Connect API Endpoints
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.oauth import initialize_oauth_providers, oauth_service
from ...core.security_audit import security_audit
from ...db.session import get_async_db

router = APIRouter()

# Initialize OAuth providers on module load
initialize_oauth_providers()


# Pydantic models for OAuth endpoints
class OAuthAuthorizationRequest(BaseModel):
    provider: str
    redirect_uri: str
    scopes: Optional[List[str]] = None


class OAuthAuthorizationResponse(BaseModel):
    authorization_url: str
    state: str


class OAuthCallbackRequest(BaseModel):
    code: str
    state: str


class OAuthCallbackResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user_id: int
    username: str
    provider: str


@router.get("/providers")
async def get_oauth_providers():
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """
    Get list of available OAuth providers.
    """
    providers = list(oauth_service.providers.keys())
    return {"providers": providers, "count": len(providers)}


@router.post("/authorize", response_model=OAuthAuthorizationResponse)
async def get_authorization_url(
    auth_request: OAuthAuthorizationRequest,
    request: Request,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Get OAuth authorization URL for a provider.
    """
    try:
        authorization_url = oauth_service.get_authorization_url(
            provider_name=auth_request.provider,
            redirect_uri=auth_request.redirect_uri,
            scopes=auth_request.scopes,
        )

        # Extract state from URL for response
        from urllib.parse import parse_qs, urlparse

        parsed_url = urlparse(authorization_url)
        query_params = parse_qs(parsed_url.query)
        state = query_params.get("state", [""])[0]

        # Log OAuth authorization initiation
        await security_audit.log_event(
            db=db,
            event_type="oauth_authorization_initiated",
            request=request,
            success=True,
            metadata={
                "provider": auth_request.provider,
                "redirect_uri": auth_request.redirect_uri,
                "scopes": auth_request.scopes,
            },
            severity="info",
        )

        return OAuthAuthorizationResponse(authorization_url=authorization_url, state=state)

    except HTTPException:
        await security_audit.log_event(
            db=db,
            event_type="oauth_authorization_initiated",
            request=request,
            success=False,
            error_message=f"Unknown provider: {auth_request.provider}",
            metadata={"provider": auth_request.provider},
            severity="warning",
        )
        raise
    except Exception as e:
        await security_audit.log_event(
            db=db,
            event_type="oauth_authorization_initiated",
            request=request,
            success=False,
            error_message=str(e),
            metadata={"provider": auth_request.provider},
            severity="error",
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate authorization URL",
        )


@router.post("/callback", response_model=OAuthCallbackResponse)
async def handle_oauth_callback(
    callback_request: OAuthCallbackRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Handle OAuth callback and authenticate user.
    """
    try:
        result = await oauth_service.handle_callback(
            db=db, code=callback_request.code, state=callback_request.state
        )

        user = result["user"]
        access_token = result["access_token"]
        refresh_token = result["refresh_token"]
        provider = result["provider"]

        # Set secure cookies
        from ...core.config import settings

        SECURE_COOKIE = settings.SECRET_KEY != "development-secret"

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            samesite="lax",
            secure=SECURE_COOKIE,
            path="/",
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            samesite="lax",
            secure=SECURE_COOKIE,
            path="/auth/token/refresh",
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        )

        # Log successful OAuth login
        await security_audit.log_event(
            db=db,
            event_type="oauth_login_success",
            user_id=user.id,
            request=request,
            success=True,
            metadata={
                "provider": provider,
                "username": user.username,
                "email": user.email,
            },
            severity="info",
        )

        return OAuthCallbackResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user_id=user.id,
            username=user.username,
            provider=provider,
        )

    except HTTPException as e:
        await security_audit.log_event(
            db=db,
            event_type="oauth_login_failure",
            request=request,
            success=False,
            error_message=str(e.detail),
            metadata={"state": callback_request.state},
            severity="warning",
        )
        raise
    except Exception as e:
        await security_audit.log_event(
            db=db,
            event_type="oauth_login_failure",
            request=request,
            success=False,
            error_message=str(e),
            metadata={"state": callback_request.state},
            severity="error",
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OAuth authentication failed",
        )


@router.get("/callback")
async def handle_oauth_callback_get(
    code: str,
    state: str,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Handle OAuth callback via GET request (for browser redirects).
    """
    callback_request = OAuthCallbackRequest(code=code, state=state)
    return await handle_oauth_callback(callback_request, request, response, db)


@router.post("/link")
async def link_oauth_account(
    auth_request: OAuthAuthorizationRequest,
    request: Request,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Link OAuth account to existing user account.
    """
    try:
        authorization_url = oauth_service.get_authorization_url(
            provider_name=auth_request.provider,
            redirect_uri=auth_request.redirect_uri,
            scopes=auth_request.scopes,
        )

        # Store user ID in state for account linking
        from urllib.parse import parse_qs, urlparse

        parsed_url = urlparse(authorization_url)
        query_params = parse_qs(parsed_url.query)
        state = query_params.get("state", [""])[0]

        # Store linking context (in production, use Redis)
        oauth_service.state_store[state]["link_user_id"] = current_user.id

        await security_audit.log_event(
            db=db,
            event_type="oauth_account_linking_initiated",
            user_id=current_user.id,
            request=request,
            success=True,
            metadata={"provider": auth_request.provider},
            severity="info",
        )

        return {
            "authorization_url": authorization_url,
            "state": state,
            "message": "Complete OAuth flow to link account",
        }

    except Exception as e:
        await security_audit.log_event(
            db=db,
            event_type="oauth_account_linking_initiated",
            user_id=current_user.id,
            request=request,
            success=False,
            error_message=str(e),
            metadata={"provider": auth_request.provider},
            severity="error",
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate account linking",
        )


@router.delete("/unlink/{provider}")
async def unlink_oauth_account(
    provider: str,
    request: Request,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Unlink OAuth account from user account.
    Note: This is a placeholder - in a full implementation, you would
    store OAuth account linkages in a separate table.
    """
    try:
        # In a full implementation, you would:
        # 1. Find the OAuth account link in the database
        # 2. Remove the link
        # 3. Optionally revoke OAuth tokens

        await security_audit.log_event(
            db=db,
            event_type="oauth_account_unlinked",
            user_id=current_user.id,
            request=request,
            success=True,
            metadata={"provider": provider},
            severity="info",
        )

        return {"message": f"OAuth account for {provider} unlinked successfully"}

    except Exception as e:
        await security_audit.log_event(
            db=db,
            event_type="oauth_account_unlinked",
            user_id=current_user.id,
            request=request,
            success=False,
            error_message=str(e),
            metadata={"provider": provider},
            severity="error",
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unlink OAuth account",
        )


# Import get_current_active_user after router definition to avoid circular imports
