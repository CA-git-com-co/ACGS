# Enterprise API Key Management for Service-to-Service Authentication
import secrets
from datetime import datetime, timedelta, timezone

from app.crud import crud_user
from app.models import ApiKey
from fastapi import HTTPException
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from .password import get_password_hash, verify_password

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class ApiKeyManager:
    """Enterprise API Key Management Service"""

    def __init__(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        self.key_length = 32  # Length of generated API keys
        self.prefix_length = 8  # Length of key prefix for identification
        self.default_rate_limit = 1000  # Default requests per minute

    def generate_api_key(self) -> tuple[str, str]:
        """Generate API key and its prefix"""
        # Generate cryptographically secure API key
        api_key = secrets.token_urlsafe(self.key_length)
        prefix = api_key[: self.prefix_length]
        return api_key, prefix

    async def create_api_key(
        self,
        db: AsyncSession,
        user_id: int,
        name: str,
        scopes: list[str] | None = None,
        rate_limit_per_minute: int | None = None,
        allowed_ips: list[str] | None = None,
        expires_in_days: int | None = None,
    ) -> dict:
        """Create new API key for user"""

        # Verify user exists
        user = await crud_user.get_user(db, user_id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Generate API key
        api_key, prefix = self.generate_api_key()
        key_hash = get_password_hash(api_key)

        # Set defaults
        if scopes is None:
            scopes = ["read"]  # Default to read-only access

        if rate_limit_per_minute is None:
            rate_limit_per_minute = self.default_rate_limit

        # Calculate expiration
        expires_at = None
        if expires_in_days:
            expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days)

        # Create API key record
        api_key_obj = ApiKey(
            user_id=user_id,
            name=name,
            key_hash=key_hash,
            key_prefix=prefix,
            scopes=scopes,
            rate_limit_per_minute=rate_limit_per_minute,
            allowed_ips=allowed_ips or [],
            expires_at=expires_at,
        )

        db.add(api_key_obj)
        await db.commit()
        await db.refresh(api_key_obj)

        return {
            "id": api_key_obj.id,
            "name": api_key_obj.name,
            "api_key": api_key,  # Return the actual key only once
            "prefix": prefix,
            "scopes": scopes,
            "rate_limit_per_minute": rate_limit_per_minute,
            "allowed_ips": allowed_ips,
            "expires_at": expires_at.isoformat() if expires_at else None,
            "created_at": api_key_obj.created_at.isoformat(),
        }

    async def get_api_keys(self, db: AsyncSession, user_id: int) -> list[dict]:
        """Get all API keys for a user (without the actual key values)"""
        result = await db.execute(select(ApiKey).where(ApiKey.user_id == user_id))
        api_keys = result.scalars().all()

        return [
            {
                "id": key.id,
                "name": key.name,
                "prefix": key.key_prefix,
                "scopes": key.scopes,
                "rate_limit_per_minute": key.rate_limit_per_minute,
                "allowed_ips": key.allowed_ips,
                "is_active": key.is_active,
                "expires_at": key.expires_at.isoformat() if key.expires_at else None,
                "last_used_at": (
                    key.last_used_at.isoformat() if key.last_used_at else None
                ),
                "usage_count": key.usage_count,
                "created_at": key.created_at.isoformat(),
            }
            for key in api_keys
        ]

    async def get_api_key(
        self, db: AsyncSession, key_id: int, user_id: int
    ) -> dict | None:
        """Get specific API key details"""
        result = await db.execute(
            select(ApiKey).where(and_(ApiKey.id == key_id, ApiKey.user_id == user_id))
        )
        api_key = result.scalar_one_or_none()

        if not api_key:
            return None

        return {
            "id": api_key.id,
            "name": api_key.name,
            "prefix": api_key.key_prefix,
            "scopes": api_key.scopes,
            "rate_limit_per_minute": api_key.rate_limit_per_minute,
            "allowed_ips": api_key.allowed_ips,
            "is_active": api_key.is_active,
            "expires_at": (
                api_key.expires_at.isoformat() if api_key.expires_at else None
            ),
            "last_used_at": (
                api_key.last_used_at.isoformat() if api_key.last_used_at else None
            ),
            "usage_count": api_key.usage_count,
            "created_at": api_key.created_at.isoformat(),
            "updated_at": api_key.updated_at.isoformat(),
        }

    async def update_api_key(
        self,
        db: AsyncSession,
        key_id: int,
        user_id: int,
        name: str | None = None,
        scopes: list[str] | None = None,
        rate_limit_per_minute: int | None = None,
        allowed_ips: list[str] | None = None,
        is_active: bool | None = None,
    ) -> bool:
        """Update API key settings"""
        result = await db.execute(
            select(ApiKey).where(and_(ApiKey.id == key_id, ApiKey.user_id == user_id))
        )
        api_key = result.scalar_one_or_none()

        if not api_key:
            return False

        # Update fields if provided
        if name is not None:
            api_key.name = name

        if scopes is not None:
            api_key.scopes = scopes

        if rate_limit_per_minute is not None:
            api_key.rate_limit_per_minute = rate_limit_per_minute

        if allowed_ips is not None:
            api_key.allowed_ips = allowed_ips

        if is_active is not None:
            api_key.is_active = is_active

        await db.commit()
        return True

    async def revoke_api_key(self, db: AsyncSession, key_id: int, user_id: int) -> bool:
        """Revoke (deactivate) an API key"""
        return await self.update_api_key(db, key_id, user_id, is_active=False)

    async def delete_api_key(self, db: AsyncSession, key_id: int, user_id: int) -> bool:
        """Permanently delete an API key"""
        result = await db.execute(
            select(ApiKey).where(and_(ApiKey.id == key_id, ApiKey.user_id == user_id))
        )
        api_key = result.scalar_one_or_none()

        if not api_key:
            return False

        await db.delete(api_key)
        await db.commit()
        return True

    async def verify_api_key(
        self, db: AsyncSession, api_key: str, required_scopes: list[str] | None = None
    ) -> dict | None:
        """Verify API key and return user/key information"""
        if len(api_key) < self.prefix_length:
            return None

        prefix = api_key[: self.prefix_length]

        # Find API key by prefix
        result = await db.execute(
            select(ApiKey).where(and_(ApiKey.key_prefix == prefix, ApiKey.is_active))
        )
        api_key_obj = result.scalar_one_or_none()

        if not api_key_obj:
            return None

        # Verify full API key
        if not verify_password(api_key, api_key_obj.key_hash):
            return None

        # Check expiration
        if api_key_obj.expires_at and api_key_obj.expires_at <= datetime.now(
            timezone.utc
        ):
            return None

        # Check scopes if required
        if required_scopes:
            api_key_scopes = set(api_key_obj.scopes)
            required_scopes_set = set(required_scopes)

            if not required_scopes_set.issubset(api_key_scopes):
                return None

        # Get user information
        user = await crud_user.get_user(db, user_id=api_key_obj.user_id)
        if not user or not user.is_active:
            return None

        return {
            "api_key_id": api_key_obj.id,
            "user_id": user.id,
            "username": user.username,
            "scopes": api_key_obj.scopes,
            "rate_limit_per_minute": api_key_obj.rate_limit_per_minute,
            "allowed_ips": api_key_obj.allowed_ips,
        }

    async def cleanup_expired_keys(self, db: AsyncSession) -> int:
        """Clean up expired API keys"""
        current_time = datetime.now(timezone.utc)

        result = await db.execute(
            select(ApiKey).where(
                and_(ApiKey.expires_at <= current_time, ApiKey.is_active)
            )
        )
        expired_keys = result.scalars().all()

        for key in expired_keys:
            key.is_active = False

        await db.commit()
        return len(expired_keys)

    async def get_usage_statistics(
        self,
        db: AsyncSession,
        user_id: int,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> dict:
        """Get API key usage statistics"""
        if not start_date:
            start_date = datetime.now(timezone.utc) - timedelta(days=30)

        if not end_date:
            end_date = datetime.now(timezone.utc)

        # Get all API keys for user
        result = await db.execute(select(ApiKey).where(ApiKey.user_id == user_id))
        api_keys = result.scalars().all()

        total_usage = sum(key.usage_count for key in api_keys)
        active_keys = sum(1 for key in api_keys if key.is_active)
        expired_keys = sum(
            1
            for key in api_keys
            if key.expires_at and key.expires_at <= datetime.now(timezone.utc)
        )

        return {
            "total_keys": len(api_keys),
            "active_keys": active_keys,
            "expired_keys": expired_keys,
            "total_usage": total_usage,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
        }


# Global API key manager instance
api_key_manager = ApiKeyManager()
