# Enterprise Multi-Factor Authentication API Endpoints

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.mfa import mfa_service
from ...core.security import get_current_active_user
from ...core.security_audit import security_audit
from ...db.session import get_async_db
from ...models import User

router = APIRouter()


# Pydantic models for MFA endpoints
class MFASetupResponse(BaseModel):
    secret: str
    qr_code: str
    backup_codes: list[str]
    provisioning_uri: str


class MFAEnableRequest(BaseModel):
    totp_code: str


class MFAVerifyRequest(BaseModel):
    code: str


class MFAVerifyResponse(BaseModel):
    method: str
    valid: bool
    remaining_codes: int | None = None


class MFADisableRequest(BaseModel):
    verification_code: str


class BackupCodesRequest(BaseModel):
    totp_code: str


@router.post("/setup", response_model=MFASetupResponse)
async def setup_mfa(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Setup MFA for the current user.
    Returns TOTP secret, QR code, and backup codes.
    """
    try:
        result = await mfa_service.setup_mfa(db, current_user.id)

        # Log MFA setup event
        await security_audit.log_event(
            db=db,
            event_type="mfa_setup",
            user_id=current_user.id,
            request=request,
            success=True,
            metadata={"method": "totp"},
            severity="info",
        )

        return MFASetupResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        await security_audit.log_event(
            db=db,
            event_type="mfa_setup",
            user_id=current_user.id,
            request=request,
            success=False,
            error_message=str(e),
            severity="error",
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to setup MFA",
        )


@router.post("/enable")
async def enable_mfa(
    mfa_request: MFAEnableRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Enable MFA for the current user after verifying TOTP code.
    """
    try:
        success = await mfa_service.enable_mfa(
            db, current_user.id, mfa_request.totp_code
        )

        if success:
            await security_audit.log_event(
                db=db,
                event_type="mfa_enabled",
                user_id=current_user.id,
                request=request,
                success=True,
                metadata={"method": "totp"},
                severity="info",
            )

            return {"message": "MFA enabled successfully"}
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to enable MFA"
        )

    except HTTPException:
        await security_audit.log_event(
            db=db,
            event_type="mfa_enabled",
            user_id=current_user.id,
            request=request,
            success=False,
            error_message="Invalid TOTP code",
            severity="warning",
        )
        raise
    except Exception as e:
        await security_audit.log_event(
            db=db,
            event_type="mfa_enabled",
            user_id=current_user.id,
            request=request,
            success=False,
            error_message=str(e),
            severity="error",
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to enable MFA",
        )


@router.post("/disable")
async def disable_mfa(
    mfa_request: MFADisableRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Disable MFA for the current user after verification.
    """
    try:
        success = await mfa_service.disable_mfa(
            db, current_user.id, mfa_request.verification_code
        )

        if success:
            await security_audit.log_event(
                db=db,
                event_type="mfa_disabled",
                user_id=current_user.id,
                request=request,
                success=True,
                severity="warning",  # Disabling MFA is a security-relevant event
            )

            return {"message": "MFA disabled successfully"}
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to disable MFA"
        )

    except HTTPException:
        await security_audit.log_event(
            db=db,
            event_type="mfa_disabled",
            user_id=current_user.id,
            request=request,
            success=False,
            error_message="Invalid verification code",
            severity="warning",
        )
        raise
    except Exception as e:
        await security_audit.log_event(
            db=db,
            event_type="mfa_disabled",
            user_id=current_user.id,
            request=request,
            success=False,
            error_message=str(e),
            severity="error",
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to disable MFA",
        )


@router.post("/verify", response_model=MFAVerifyResponse)
async def verify_mfa(
    mfa_request: MFAVerifyRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Verify MFA code during authentication.
    """
    try:
        result = await mfa_service.verify_mfa(db, current_user.id, mfa_request.code)

        if result["valid"]:
            await security_audit.log_event(
                db=db,
                event_type="mfa_verification_success",
                user_id=current_user.id,
                request=request,
                success=True,
                metadata={"method": result["method"]},
                severity="info",
            )
        else:
            await security_audit.log_event(
                db=db,
                event_type="mfa_verification_failure",
                user_id=current_user.id,
                request=request,
                success=False,
                error_message="Invalid MFA code",
                severity="warning",
            )

        return MFAVerifyResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        await security_audit.log_event(
            db=db,
            event_type="mfa_verification_failure",
            user_id=current_user.id,
            request=request,
            success=False,
            error_message=str(e),
            severity="error",
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify MFA",
        )


@router.post("/backup-codes/regenerate")
async def regenerate_backup_codes(
    backup_request: BackupCodesRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Regenerate MFA backup codes after TOTP verification.
    """
    try:
        backup_codes = await mfa_service.regenerate_backup_codes(
            db, current_user.id, backup_request.totp_code
        )

        await security_audit.log_event(
            db=db,
            event_type="backup_codes_regenerated",
            user_id=current_user.id,
            request=request,
            success=True,
            metadata={"codes_count": len(backup_codes)},
            severity="info",
        )

        return {
            "message": "Backup codes regenerated successfully",
            "backup_codes": backup_codes,
        }

    except HTTPException:
        await security_audit.log_event(
            db=db,
            event_type="backup_codes_regenerated",
            user_id=current_user.id,
            request=request,
            success=False,
            error_message="Invalid TOTP code",
            severity="warning",
        )
        raise
    except Exception as e:
        await security_audit.log_event(
            db=db,
            event_type="backup_codes_regenerated",
            user_id=current_user.id,
            request=request,
            success=False,
            error_message=str(e),
            severity="error",
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to regenerate backup codes",
        )


@router.get("/status")
async def get_mfa_status(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Get current MFA status for the user.
    """
    return {
        "mfa_enabled": current_user.mfa_enabled,
        "backup_codes_count": (
            len(current_user.backup_codes) if current_user.backup_codes else 0
        ),
    }
