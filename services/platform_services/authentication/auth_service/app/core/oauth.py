# Enterprise OAuth 2.0 and OpenID Connect Integration
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import urlencode

import httpx
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..crud import crud_user
from .security import create_access_token, create_refresh_token

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"



class OAuthProvider:
    """Base OAuth 2.0 provider implementation"""

    def __init__(
        self,
        name: str,
        client_id: str,
        client_secret: str,
        authorize_url: str,
        token_url: str,
        userinfo_url: str,
    ):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        self.name = name
        self.client_id = client_id
        self.client_secret = client_secret
        self.authorize_url = authorize_url
        self.token_url = token_url
        self.userinfo_url = userinfo_url

    def generate_authorization_url(
        self, redirect_uri: str, state: str, scopes: list = None
    ) -> str:
        """Generate OAuth authorization URL"""
        if scopes is None:
            scopes = ["openid", "email", "profile"]

        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "scope": " ".join(scopes),
            "state": state,
        }

        return f"{self.authorize_url}?{urlencode(params)}"

    async def exchange_code_for_token(
        self, code: str, redirect_uri: str
    ) -> dict[str, Any]:
        """Exchange authorization code for access token"""
        data = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": redirect_uri,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(self.token_url, data=data)
            response.raise_for_status()
            return response.json()

    async def get_user_info(self, access_token: str) -> dict[str, Any]:
        """Get user information from OAuth provider"""
        headers = {"Authorization": f"Bearer {access_token}"}

        async with httpx.AsyncClient() as client:
            response = await client.get(self.userinfo_url, headers=headers)
            response.raise_for_status()
            return response.json()


class GoogleOAuthProvider(OAuthProvider):
    """Google OAuth 2.0 provider"""

    def __init__(self, client_id: str, client_secret: str):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        super().__init__(
            name="google",
            client_id=client_id,
            client_secret=client_secret,
            authorize_url="https://accounts.google.com/o/oauth2/v2/auth",
            token_url="https://oauth2.googleapis.com/token",
            userinfo_url="https://www.googleapis.com/oauth2/v2/userinfo",
        )


class MicrosoftOAuthProvider(OAuthProvider):
    """Microsoft Azure AD OAuth 2.0 provider"""

    def __init__(self, client_id: str, client_secret: str, tenant_id: str = "common"):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        super().__init__(
            name="microsoft",
            client_id=client_id,
            client_secret=client_secret,
            authorize_url=f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize",
            token_url=f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token",
            userinfo_url="https://graph.microsoft.com/v1.0/me",
        )


class GitHubOAuthProvider(OAuthProvider):
    """GitHub OAuth 2.0 provider"""

    def __init__(self, client_id: str, client_secret: str):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        super().__init__(
            name="github",
            client_id=client_id,
            client_secret=client_secret,
            authorize_url="https://github.com/login/oauth/authorize",
            token_url="https://github.com/login/oauth/access_token",
            userinfo_url="https://api.github.com/user",
        )

    async def exchange_code_for_token(
        self, code: str, redirect_uri: str
    ) -> dict[str, Any]:
        """GitHub-specific token exchange"""
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
        }

        headers = {"Accept": "application/json"}

        async with httpx.AsyncClient() as client:
            response = await client.post(self.token_url, data=data, headers=headers)
            response.raise_for_status()
            return response.json()


class OAuthService:
    """Enterprise OAuth 2.0 and OpenID Connect Service"""

    def __init__(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        self.providers: dict[str, OAuthProvider] = {}
        self.state_store: dict[str, dict[str, Any]] = {}  # In production, use Redis

    def register_provider(self, provider: OAuthProvider):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Register an OAuth provider"""
        self.providers[provider.name] = provider

    def generate_state(self, provider_name: str, redirect_uri: str) -> str:
        """Generate and store OAuth state parameter"""
        state = secrets.token_urlsafe(32)
        self.state_store[state] = {
            "provider": provider_name,
            "redirect_uri": redirect_uri,
            "created_at": datetime.now(timezone.utc),
            "expires_at": datetime.now(timezone.utc) + timedelta(minutes=10),
        }
        return state

    def verify_state(self, state: str) -> dict[str, Any] | None:
        """Verify OAuth state parameter"""
        state_data = self.state_store.get(state)
        if not state_data:
            return None

        if datetime.now(timezone.utc) > state_data["expires_at"]:
            del self.state_store[state]
            return None

        return state_data

    def get_authorization_url(
        self, provider_name: str, redirect_uri: str, scopes: list = None
    ) -> str:
        """Get OAuth authorization URL"""
        provider = self.providers.get(provider_name)
        if not provider:
            raise HTTPException(
                status_code=400, detail=f"Unknown OAuth provider: {provider_name}"
            )

        state = self.generate_state(provider_name, redirect_uri)
        return provider.generate_authorization_url(redirect_uri, state, scopes)

    async def handle_callback(
        self, db: AsyncSession, code: str, state: str
    ) -> dict[str, Any]:
        """Handle OAuth callback and create/login user"""
        # Verify state
        state_data = self.verify_state(state)
        if not state_data:
            raise HTTPException(status_code=400, detail="Invalid or expired state")

        provider_name = state_data["provider"]
        redirect_uri = state_data["redirect_uri"]

        # Clean up state
        del self.state_store[state]

        provider = self.providers.get(provider_name)
        if not provider:
            raise HTTPException(
                status_code=400, detail=f"Unknown OAuth provider: {provider_name}"
            )

        try:
            # Exchange code for token
            token_data = await provider.exchange_code_for_token(code, redirect_uri)
            access_token = token_data.get("access_token")

            if not access_token:
                raise HTTPException(
                    status_code=400, detail="Failed to obtain access token"
                )

            # Get user info
            user_info = await provider.get_user_info(access_token)

            # Find or create user
            email = user_info.get("email")
            if not email:
                raise HTTPException(
                    status_code=400, detail="Email not provided by OAuth provider"
                )

            user = await crud_user.get_user_by_email(db, email=email)

            if not user:
                # Create new user
                username = email.split("@")[0]  # Use email prefix as username
                full_name = user_info.get("name", "")

                # Ensure username is unique
                existing_user = await crud_user.get_user_by_username(
                    db, username=username
                )
                if existing_user:
                    username = f"{username}_{secrets.token_hex(4)}"

                user_data = {
                    "username": username,
                    "email": email,
                    "full_name": full_name,
                    "hashed_password": secrets.token_hex(
                        32
                    ),  # Random password for OAuth users
                    "is_active": True,
                    "role": "user",
                }

                user = await crud_user.create_user(db, user_data)

            # Update last login
            user.last_login_at = datetime.now(timezone.utc)
            await db.commit()

            # Create tokens
            access_token_str, access_jti = create_access_token(
                subject=user.username, user_id=user.id, roles=[user.role]
            )

            refresh_token_str, refresh_jti, refresh_expires_at = create_refresh_token(
                subject=user.username, user_id=user.id, roles=[user.role]
            )

            return {
                "user": user,
                "access_token": access_token_str,
                "refresh_token": refresh_token_str,
                "token_type": "bearer",
                "provider": provider_name,
            }

        except httpx.HTTPError as e:
            raise HTTPException(status_code=400, detail=f"OAuth provider error: {e!s}")
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"OAuth authentication failed: {e!s}"
            )


# Global OAuth service instance
oauth_service = OAuthService()


# Initialize providers (in production, load from environment variables)
def initialize_oauth_providers():
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """Initialize OAuth providers from configuration"""
    import os

    # Google OAuth
    google_client_id = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
    google_client_secret = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")
    if google_client_id and google_client_secret:
        oauth_service.register_provider(
            GoogleOAuthProvider(google_client_id, google_client_secret)
        )

    # Microsoft OAuth
    microsoft_client_id = os.getenv("MICROSOFT_OAUTH_CLIENT_ID")
    microsoft_client_secret = os.getenv("MICROSOFT_OAUTH_CLIENT_SECRET")
    microsoft_tenant_id = os.getenv("MICROSOFT_TENANT_ID", "common")
    if microsoft_client_id and microsoft_client_secret:
        oauth_service.register_provider(
            MicrosoftOAuthProvider(
                microsoft_client_id, microsoft_client_secret, microsoft_tenant_id
            )
        )

    # GitHub OAuth
    github_client_id = os.getenv("GITHUB_OAUTH_CLIENT_ID")
    github_client_secret = os.getenv("GITHUB_OAUTH_CLIENT_SECRET")
    if github_client_id and github_client_secret:
        oauth_service.register_provider(
            GitHubOAuthProvider(github_client_id, github_client_secret)
        )
