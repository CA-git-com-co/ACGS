# backend/auth_service/app/api/v1/deps.py
from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession  # For type hinting

from services.shared.database import get_async_db
from services.shared.models import User

from ...core.security import get_current_active_user

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"



# Wrapper for get_async_db to provide the session.
# Endpoints will depend on this to get an AsyncSession.
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for db_session in get_async_db():
        yield db_session


# Re-export get_current_active_user from security.py for direct use in endpoints.
# This avoids endpoints having to import from .core.security directly,
# if that is the preferred style.
# Example of creating a pre-defined dependency for even cleaner use in endpoints:
# current_active_user_dependency = Depends(get_current_active_user)


async def get_current_active_superuser(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Dependency to get current active user and verify they are a superuser."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user


# If there are other common dependencies, they can be added here.
