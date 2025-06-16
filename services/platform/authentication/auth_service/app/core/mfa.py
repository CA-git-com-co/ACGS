# Enterprise Multi-Factor Authentication (MFA) Implementation
import base64
import io
import secrets
from typing import List, Optional, Tuple

import pyotp
import qrcode
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..crud import crud_user


class MFAService:
    """Enterprise Multi-Factor Authentication Service"""

    def __init__(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        self.issuer_name = "ACGS-1 Constitutional Governance"
        self.backup_codes_count = 10

    def generate_totp_secret(self) -> str:
        """Generate a new TOTP secret for a user."""
        return pyotp.random_base32()

    def generate_provisioning_uri(self, user_email: str, secret: str) -> str:
        """Generate TOTP provisioning URI for QR code."""
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=user_email, issuer_name=self.issuer_name)

    def generate_qr_code(self, provisioning_uri: str) -> str:
        """Generate QR code image as base64 string."""
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        return base64.b64encode(buffer.getvalue()).decode()

    def verify_totp_code(self, secret: str, code: str, window: int = 1) -> bool:
        """Verify TOTP code with time window tolerance."""
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=window)

    def generate_backup_codes(self) -> List[str]:
        """Generate backup codes for MFA recovery."""
        codes = []
        for _ in range(self.backup_codes_count):
            # Generate 8-character alphanumeric codes
            code = "".join(secrets.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") for _ in range(8))
            codes.append(code)
        return codes

    def hash_backup_codes(self, codes: List[str]) -> List[str]:
        """Hash backup codes for secure storage."""
        from ..core.password import get_password_hash

        return [get_password_hash(code) for code in codes]

    def verify_backup_code(
        self, hashed_codes: List[str], provided_code: str
    ) -> Tuple[bool, Optional[int]]:
        """Verify backup code and return index if valid."""
        from ..core.password import verify_password

        for i, hashed_code in enumerate(hashed_codes):
            if verify_password(provided_code, hashed_code):
                return True, i
        return False, None

    async def setup_mfa(self, db: AsyncSession, user_id: int) -> dict:
        """Setup MFA for a user."""
        user = await crud_user.get_user(db, user_id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if user.mfa_enabled:
            raise HTTPException(status_code=400, detail="MFA already enabled")

        # Generate secret and backup codes
        secret = self.generate_totp_secret()
        backup_codes = self.generate_backup_codes()
        hashed_backup_codes = self.hash_backup_codes(backup_codes)

        # Generate QR code
        provisioning_uri = self.generate_provisioning_uri(user.email, secret)
        qr_code = self.generate_qr_code(provisioning_uri)

        # Store secret and backup codes (not yet enabled)
        user.mfa_secret = secret
        user.backup_codes = hashed_backup_codes
        await db.commit()

        return {
            "secret": secret,
            "qr_code": qr_code,
            "backup_codes": backup_codes,  # Return unhashed codes to user
            "provisioning_uri": provisioning_uri,
        }

    async def enable_mfa(self, db: AsyncSession, user_id: int, totp_code: str) -> bool:
        """Enable MFA after verifying TOTP code."""
        user = await crud_user.get_user(db, user_id=user_id)
        if not user or not user.mfa_secret:
            raise HTTPException(status_code=400, detail="MFA setup not initiated")

        if user.mfa_enabled:
            raise HTTPException(status_code=400, detail="MFA already enabled")

        # Verify TOTP code
        if not self.verify_totp_code(user.mfa_secret, totp_code):
            raise HTTPException(status_code=400, detail="Invalid TOTP code")

        # Enable MFA
        user.mfa_enabled = True
        await db.commit()

        return True

    async def disable_mfa(self, db: AsyncSession, user_id: int, verification_code: str) -> bool:
        """Disable MFA after verification."""
        user = await crud_user.get_user(db, user_id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not user.mfa_enabled:
            raise HTTPException(status_code=400, detail="MFA not enabled")

        # Verify with TOTP or backup code
        totp_valid = self.verify_totp_code(user.mfa_secret, verification_code)
        backup_valid, _ = self.verify_backup_code(user.backup_codes or [], verification_code)

        if not (totp_valid or backup_valid):
            raise HTTPException(status_code=400, detail="Invalid verification code")

        # Disable MFA
        user.mfa_enabled = False
        user.mfa_secret = None
        user.backup_codes = None
        await db.commit()

        return True

    async def verify_mfa(self, db: AsyncSession, user_id: int, code: str) -> dict:
        """Verify MFA code during login."""
        user = await crud_user.get_user(db, user_id=user_id)
        if not user or not user.mfa_enabled:
            raise HTTPException(status_code=400, detail="MFA not enabled")

        # Try TOTP first
        if self.verify_totp_code(user.mfa_secret, code):
            return {"method": "totp", "valid": True}

        # Try backup code
        backup_valid, backup_index = self.verify_backup_code(user.backup_codes or [], code)
        if backup_valid:
            # Remove used backup code
            backup_codes = user.backup_codes.copy()
            backup_codes.pop(backup_index)
            user.backup_codes = backup_codes
            await db.commit()

            return {
                "method": "backup",
                "valid": True,
                "remaining_codes": len(backup_codes),
            }

        return {"method": None, "valid": False}

    async def regenerate_backup_codes(
        self, db: AsyncSession, user_id: int, totp_code: str
    ) -> List[str]:
        """Regenerate backup codes after TOTP verification."""
        user = await crud_user.get_user(db, user_id=user_id)
        if not user or not user.mfa_enabled:
            raise HTTPException(status_code=400, detail="MFA not enabled")

        # Verify TOTP code
        if not self.verify_totp_code(user.mfa_secret, totp_code):
            raise HTTPException(status_code=400, detail="Invalid TOTP code")

        # Generate new backup codes
        backup_codes = self.generate_backup_codes()
        hashed_backup_codes = self.hash_backup_codes(backup_codes)

        user.backup_codes = hashed_backup_codes
        await db.commit()

        return backup_codes


# Global MFA service instance
mfa_service = MFAService()
