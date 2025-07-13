"""
Real User Service Implementation for ACGS Authentication

Provides real user authentication, authorization, and user management
operations to replace mock implementations throughout the system.

Constitutional Hash: cdd01ef066bc6cf2
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from sqlalchemy import and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

logger = logging.getLogger(__name__)

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class UserService:
    """
    Real user service providing authentication and user management.
    Replaces mock implementations with actual database operations.
    """

    def __init__(self):
        self.pwd_context = bcrypt

    async def authenticate_user(
        self, session: AsyncSession, username: str, password: str
    ) -> User | None:
        """
        Authenticate a user with username/email and password.
        Returns None if authentication fails.
        """
        try:
            # Find user by username or email
            query = select(User).where(
                and_(
                    or_(User.username == username, User.email == username),
                    User.is_active,
                )
            )
            result = await session.execute(query)
            user = result.scalar_one_or_none()

            if not user:
                logger.warning(f"User not found: {username}")
                return None

            # Check if account is locked
            if user.locked_until and user.locked_until > datetime.now(timezone.utc):
                logger.warning(f"Account locked: {username}")
                return None

            # Verify password
            if not self._verify_password(password, user.hashed_password):
                # Increment failed login attempts
                await self._handle_failed_login(session, user)
                logger.warning(f"Invalid password for user: {username}")
                return None

            # Reset failed login attempts on successful auth
            if user.failed_login_attempts > 0:
                user.failed_login_attempts = 0
                user.locked_until = None
                await session.commit()

            # Update last login
            user.last_login_at = datetime.now(timezone.utc)
            await session.commit()

            logger.info(f"User authenticated successfully: {username}")
            return user

        except Exception as e:
            logger.exception(f"Error authenticating user {username}: {e}")
            return None

    async def get_user_by_id(self, session: AsyncSession, user_id: int) -> User | None:
        """Get user by ID."""
        try:
            query = select(User).where(and_(User.id == user_id, User.is_active))
            result = await session.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.exception(f"Error fetching user {user_id}: {e}")
            return None

    async def get_user_by_username(
        self, session: AsyncSession, username: str
    ) -> User | None:
        """Get user by username."""
        try:
            query = select(User).where(and_(User.username == username, User.is_active))
            result = await session.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.exception(f"Error fetching user by username {username}: {e}")
            return None

    async def get_user_by_email(self, session: AsyncSession, email: str) -> User | None:
        """Get user by email."""
        try:
            query = select(User).where(and_(User.email == email, User.is_active))
            result = await session.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.exception(f"Error fetching user by email {email}: {e}")
            return None

    async def create_user(
        self, session: AsyncSession, user_data: UserCreate
    ) -> User | None:
        """Create a new user."""
        try:
            # Check if username or email already exists
            existing_user = await self.get_user_by_username(session, user_data.username)
            if existing_user:
                logger.warning(f"Username already exists: {user_data.username}")
                return None

            existing_email = await self.get_user_by_email(session, user_data.email)
            if existing_email:
                logger.warning(f"Email already exists: {user_data.email}")
                return None

            # Hash password
            hashed_password = self._hash_password(user_data.password)

            # Create user
            db_user = User(
                username=user_data.username,
                email=user_data.email,
                hashed_password=hashed_password,
                full_name=user_data.full_name,
                is_active=user_data.is_active,
                is_superuser=user_data.is_superuser,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )

            session.add(db_user)
            await session.commit()
            await session.refresh(db_user)

            logger.info(f"User created successfully: {user_data.username}")
            return db_user

        except Exception as e:
            logger.exception(f"Error creating user {user_data.username}: {e}")
            await session.rollback()
            return None

    async def update_user(
        self, session: AsyncSession, user_id: int, user_data: UserUpdate
    ) -> User | None:
        """Update user information."""
        try:
            user = await self.get_user_by_id(session, user_id)
            if not user:
                return None

            # Update fields
            for field, value in user_data.dict(exclude_unset=True).items():
                if field == "password" and value:
                    user.hashed_password = self._hash_password(value)
                    user.password_changed_at = datetime.now(timezone.utc)
                else:
                    setattr(user, field, value)

            user.updated_at = datetime.now(timezone.utc)
            await session.commit()
            await session.refresh(user)

            logger.info(f"User updated successfully: {user.username}")
            return user

        except Exception as e:
            logger.exception(f"Error updating user {user_id}: {e}")
            await session.rollback()
            return None

    async def delete_user(self, session: AsyncSession, user_id: int) -> bool:
        """Soft delete a user by setting is_active to False."""
        try:
            user = await self.get_user_by_id(session, user_id)
            if not user:
                return False

            user.is_active = False
            user.updated_at = datetime.now(timezone.utc)
            await session.commit()

            logger.info(f"User soft deleted: {user.username}")
            return True

        except Exception as e:
            logger.exception(f"Error deleting user {user_id}: {e}")
            await session.rollback()
            return False

    async def validate_user_permissions(
        self, session: AsyncSession, user_id: int, required_permissions: list[str]
    ) -> bool:
        """Validate that user has required permissions."""
        try:
            user = await self.get_user_by_id(session, user_id)
            if not user:
                return False

            # Superuser has all permissions
            if user.is_superuser:
                return True

            # Check explicit permissions
            user_permissions = user.permissions or []
            return all(perm in user_permissions for perm in required_permissions)

        except Exception as e:
            logger.exception(f"Error validating permissions for user {user_id}: {e}")
            return False

    async def get_user_profile(
        self, session: AsyncSession, user_id: int
    ) -> dict[str, Any] | None:
        """Get complete user profile information."""
        try:
            user = await self.get_user_by_id(session, user_id)
            if not user:
                return None

            return {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_active": user.is_active,
                "is_superuser": user.is_superuser,
                "is_verified": user.is_verified,
                "role": user.role,
                "permissions": user.permissions,
                "mfa_enabled": user.mfa_enabled,
                "created_at": user.created_at,
                "last_login_at": user.last_login_at,
                "constitutional_compliance": True,
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }

        except Exception as e:
            logger.exception(f"Error getting user profile {user_id}: {e}")
            return None

    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    def _verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

    async def _handle_failed_login(self, session: AsyncSession, user: User) -> None:
        """Handle failed login attempt."""
        user.failed_login_attempts += 1

        # Lock account after 5 failed attempts for 15 minutes
        if user.failed_login_attempts >= 5:
            user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=15)
            logger.warning(f"Account locked due to failed attempts: {user.username}")

        await session.commit()


class UserServiceClient:
    """
    HTTP client for accessing user service from other services.
    Replaces mock service calls with actual HTTP requests.
    """

    def __init__(self, base_url: str = "http://auth-service:8000/api/v1"):
        import httpx

        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url, timeout=30.0)

    async def authenticate_user(
        self, username: str, password: str
    ) -> dict[str, Any] | None:
        """Authenticate user via HTTP API."""
        try:
            response = await self.client.post(
                "/auth/login", data={"username": username, "password": password}
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.exception(f"Error calling auth service: {e}")
            return None

    async def get_user_by_id(
        self, user_id: int, auth_token: str | None = None
    ) -> dict[str, Any] | None:
        """Get user by ID via HTTP API."""
        try:
            headers = {}
            if auth_token:
                headers["Authorization"] = f"Bearer {auth_token}"

            response = await self.client.get(f"/users/{user_id}", headers=headers)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.exception(f"Error fetching user {user_id}: {e}")
            return None

    async def get_user_profile(
        self, user_id: int, auth_token: str | None = None
    ) -> dict[str, Any] | None:
        """Get user profile via HTTP API."""
        try:
            headers = {}
            if auth_token:
                headers["Authorization"] = f"Bearer {auth_token}"

            response = await self.client.get(
                f"/users/{user_id}/profile", headers=headers
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.exception(f"Error fetching user profile {user_id}: {e}")
            return None

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()


# Factory function for creating user service
def get_user_service() -> UserService:
    """Factory function to create a user service."""
    return UserService()


# Factory function for creating user service client
def get_user_service_client(base_url: str | None = None) -> UserServiceClient:
    """Factory function to create a user service client."""
    return UserServiceClient(base_url) if base_url else UserServiceClient()
