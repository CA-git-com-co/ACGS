# Enterprise API Key Management Endpoints

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.api_key_manager import api_key_manager
from ...core.security import authorize_permissions
from ...core.security_audit import security_audit
from ...db.session import get_async_db
from ...models import User

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


router = APIRouter()


# Pydantic models for API key endpoints
class ApiKeyCreateRequest(BaseModel):
    name: str
    scopes: list[str] | None = ["read"]
    rate_limit_per_minute: int | None = 1000
    allowed_ips: list[str] | None = None
    expires_in_days: int | None = None


class ApiKeyCreateResponse(BaseModel):
    id: int
    name: str
    api_key: str
    prefix: str
    scopes: list[str]
    rate_limit_per_minute: int
    allowed_ips: list[str]
    expires_at: str | None
    created_at: str


class ApiKeyResponse(BaseModel):
    id: int
    name: str
    prefix: str
    scopes: list[str]
    rate_limit_per_minute: int
    allowed_ips: list[str]
    is_active: bool
    expires_at: str | None
    last_used_at: str | None
    usage_count: int
    created_at: str


class ApiKeyUpdateRequest(BaseModel):
    name: str | None = None
    scopes: list[str] | None = None
    rate_limit_per_minute: int | None = None
    allowed_ips: list[str] | None = None
    is_active: bool | None = None


class ApiKeyUsageResponse(BaseModel):
    total_keys: int
    active_keys: int
    expired_keys: int
    total_usage: int
    period: dict


@router.post("/", response_model=ApiKeyCreateResponse)
async def create_api_key(
    key_request: ApiKeyCreateRequest,
    request: Request,
    current_user: User = Depends(authorize_permissions(["api_key:create"])),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Create a new API key for the current user.
    """
    try:
        result = await api_key_manager.create_api_key(
            db=db,
            user_id=current_user.id,
            name=key_request.name,
            scopes=key_request.scopes,
            rate_limit_per_minute=key_request.rate_limit_per_minute,
            allowed_ips=key_request.allowed_ips,
            expires_in_days=key_request.expires_in_days,
        )

        # Log API key creation
        await security_audit.log_event(
            db=db,
            event_type="api_key_created",
            user_id=current_user.id,
            request=request,
            success=True,
            metadata={
                "api_key_name": key_request.name,
                "scopes": key_request.scopes,
                "rate_limit": key_request.rate_limit_per_minute,
            },
            severity="info",
        )

        return ApiKeyCreateResponse(**result)

    except Exception as e:
        await security_audit.log_event(
            db=db,
            event_type="api_key_created",
            user_id=current_user.id,
            request=request,
            success=False,
            error_message=str(e),
            metadata={"api_key_name": key_request.name},
            severity="error",
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create API key",
        )


@router.get("/", response_model=list[ApiKeyResponse])
async def get_api_keys(
    current_user: User = Depends(authorize_permissions(["api_key:read"])),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Get all API keys for the current user.
    """
    try:
        api_keys = await api_key_manager.get_api_keys(db, current_user.id)
        return [ApiKeyResponse(**key) for key in api_keys]

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve API keys",
        )


@router.get("/{key_id}", response_model=ApiKeyResponse)
async def get_api_key(
    key_id: int,
    current_user: User = Depends(authorize_permissions(["api_key:read"])),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Get specific API key details.
    """
    try:
        api_key = await api_key_manager.get_api_key(db, key_id, current_user.id)

        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="API key not found"
            )

        return ApiKeyResponse(**api_key)

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve API key",
        )


@router.put("/{key_id}")
async def update_api_key(
    key_id: int,
    update_request: ApiKeyUpdateRequest,
    request: Request,
    current_user: User = Depends(authorize_permissions(["api_key:update"])),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Update API key settings.
    """
    try:
        success = await api_key_manager.update_api_key(
            db=db,
            key_id=key_id,
            user_id=current_user.id,
            name=update_request.name,
            scopes=update_request.scopes,
            rate_limit_per_minute=update_request.rate_limit_per_minute,
            allowed_ips=update_request.allowed_ips,
            is_active=update_request.is_active,
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="API key not found"
            )

        # Log API key update
        await security_audit.log_event(
            db=db,
            event_type="api_key_updated",
            user_id=current_user.id,
            request=request,
            success=True,
            metadata={
                "api_key_id": key_id,
                "updated_fields": update_request.dict(exclude_unset=True),
            },
            severity="info",
        )

        return {"message": "API key updated successfully"}

    except HTTPException:
        raise
    except Exception as e:
        await security_audit.log_event(
            db=db,
            event_type="api_key_updated",
            user_id=current_user.id,
            request=request,
            success=False,
            error_message=str(e),
            metadata={"api_key_id": key_id},
            severity="error",
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update API key",
        )


@router.post("/{key_id}/revoke")
async def revoke_api_key(
    key_id: int,
    request: Request,
    current_user: User = Depends(authorize_permissions(["api_key:revoke"])),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Revoke (deactivate) an API key.
    """
    try:
        success = await api_key_manager.revoke_api_key(db, key_id, current_user.id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="API key not found"
            )

        # Log API key revocation
        await security_audit.log_event(
            db=db,
            event_type="api_key_revoked",
            user_id=current_user.id,
            request=request,
            success=True,
            metadata={"api_key_id": key_id},
            severity="warning",
        )

        return {"message": "API key revoked successfully"}

    except HTTPException:
        raise
    except Exception as e:
        await security_audit.log_event(
            db=db,
            event_type="api_key_revoked",
            user_id=current_user.id,
            request=request,
            success=False,
            error_message=str(e),
            metadata={"api_key_id": key_id},
            severity="error",
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to revoke API key",
        )


@router.delete("/{key_id}")
async def delete_api_key(
    key_id: int,
    request: Request,
    current_user: User = Depends(authorize_permissions(["api_key:delete"])),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Permanently delete an API key.
    """
    try:
        success = await api_key_manager.delete_api_key(db, key_id, current_user.id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="API key not found"
            )

        # Log API key deletion
        await security_audit.log_event(
            db=db,
            event_type="api_key_deleted",
            user_id=current_user.id,
            request=request,
            success=True,
            metadata={"api_key_id": key_id},
            severity="warning",
        )

        return {"message": "API key deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        await security_audit.log_event(
            db=db,
            event_type="api_key_deleted",
            user_id=current_user.id,
            request=request,
            success=False,
            error_message=str(e),
            metadata={"api_key_id": key_id},
            severity="error",
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete API key",
        )


@router.get("/usage/statistics", response_model=ApiKeyUsageResponse)
async def get_api_key_usage_statistics(
    current_user: User = Depends(authorize_permissions(["api_key:read"])),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Get API key usage statistics for the current user.
    """
    try:
        stats = await api_key_manager.get_usage_statistics(db, current_user.id)
        return ApiKeyUsageResponse(**stats)

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve usage statistics",
        )
