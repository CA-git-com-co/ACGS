"""
Key management service for ACGS Integrity Service.
Constitutional Hash: cdd01ef066bc6cf2
"""

import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


class KeyManager:
    """Key management service for cryptographic operations."""

    def __init__(self):
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.keys: Dict[str, Dict[str, Any]] = {}
        self.supported_key_types = ["RSA", "ECDSA", "EdDSA"]
        self.supported_key_sizes = {
            "RSA": [2048, 3072, 4096],
            "ECDSA": [256, 384, 521],
            "EdDSA": [256],
        }

    async def create_key(
        self,
        key_type: str = "RSA",
        key_size: int = 2048,
        purpose: str = "signing",
        expires_in_days: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Create a new cryptographic key."""
        try:
            if key_type not in self.supported_key_types:
                raise ValueError(f"Unsupported key type: {key_type}")

            if key_size not in self.supported_key_sizes.get(key_type, []):
                raise ValueError(f"Unsupported key size {key_size} for type {key_type}")

            key_id = str(uuid.uuid4())
            created_at = datetime.now(timezone.utc)
            expires_at = None

            if expires_in_days:
                expires_at = created_at + timedelta(days=expires_in_days)

            # Generate mock key data (in production, use actual cryptographic libraries)
            public_key_data = f"-----BEGIN PUBLIC KEY-----\n{key_id}_{key_type}_{key_size}_PUBLIC\n-----END PUBLIC KEY-----"
            private_key_data = f"-----BEGIN PRIVATE KEY-----\n{key_id}_{key_type}_{key_size}_PRIVATE\n-----END PRIVATE KEY-----"

            key_info = {
                "key_id": key_id,
                "key_type": key_type,
                "key_size": key_size,
                "purpose": purpose,
                "public_key": public_key_data,
                "private_key": private_key_data,  # In production, store securely
                "created_at": created_at,
                "expires_at": expires_at,
                "is_active": True,
                "usage_count": 0,
                "last_used": None,
                "metadata": {
                    "creator": "integrity_service",
                    "constitutional_hash": self.constitutional_hash,
                },
            }

            self.keys[key_id] = key_info

            # Return public information only
            return {
                "key_id": key_id,
                "key_type": key_type,
                "key_size": key_size,
                "purpose": purpose,
                "public_key": public_key_data,
                "created_at": created_at,
                "expires_at": expires_at,
                "is_active": True,
                "constitutional_hash": self.constitutional_hash,
            }

        except Exception as e:
            logger.error(f"Key creation failed: {e}")
            raise

    async def get_key(
        self, key_id: str, include_private: bool = False
    ) -> Dict[str, Any]:
        """Get key information."""
        try:
            if key_id not in self.keys:
                raise ValueError(f"Key {key_id} not found")

            key_info = self.keys[key_id].copy()

            if not include_private:
                key_info.pop("private_key", None)

            return key_info

        except Exception as e:
            logger.error(f"Key retrieval failed: {e}")
            raise

    async def list_keys(
        self,
        key_type: Optional[str] = None,
        purpose: Optional[str] = None,
        active_only: bool = True,
    ) -> Dict[str, Any]:
        """List keys with optional filtering."""
        try:
            filtered_keys = []

            for key_info in self.keys.values():
                # Apply filters
                if key_type and key_info["key_type"] != key_type:
                    continue

                if purpose and key_info["purpose"] != purpose:
                    continue

                if active_only and not key_info["is_active"]:
                    continue

                # Check expiration
                if key_info["expires_at"] and key_info["expires_at"] < datetime.now(
                    timezone.utc
                ):
                    continue

                # Remove private key from listing
                public_key_info = key_info.copy()
                public_key_info.pop("private_key", None)
                filtered_keys.append(public_key_info)

            return {
                "keys": filtered_keys,
                "total_count": len(filtered_keys),
                "constitutional_hash": self.constitutional_hash,
            }

        except Exception as e:
            logger.error(f"Key listing failed: {e}")
            raise

    async def deactivate_key(self, key_id: str) -> Dict[str, Any]:
        """Deactivate a key."""
        try:
            if key_id not in self.keys:
                raise ValueError(f"Key {key_id} not found")

            self.keys[key_id]["is_active"] = False
            self.keys[key_id]["deactivated_at"] = datetime.now(timezone.utc)

            return {
                "key_id": key_id,
                "status": "deactivated",
                "deactivated_at": self.keys[key_id]["deactivated_at"],
                "constitutional_hash": self.constitutional_hash,
            }

        except Exception as e:
            logger.error(f"Key deactivation failed: {e}")
            raise

    async def rotate_key(
        self, old_key_id: str, expires_in_days: Optional[int] = None
    ) -> Dict[str, Any]:
        """Rotate a key by creating a new one and deactivating the old one."""
        try:
            if old_key_id not in self.keys:
                raise ValueError(f"Key {old_key_id} not found")

            old_key = self.keys[old_key_id]

            # Create new key with same parameters
            new_key = await self.create_key(
                key_type=old_key["key_type"],
                key_size=old_key["key_size"],
                purpose=old_key["purpose"],
                expires_in_days=expires_in_days,
            )

            # Deactivate old key
            await self.deactivate_key(old_key_id)

            return {
                "old_key_id": old_key_id,
                "new_key_id": new_key["key_id"],
                "rotated_at": datetime.now(timezone.utc),
                "constitutional_hash": self.constitutional_hash,
            }

        except Exception as e:
            logger.error(f"Key rotation failed: {e}")
            raise

    async def update_key_usage(self, key_id: str) -> None:
        """Update key usage statistics."""
        try:
            if key_id in self.keys:
                self.keys[key_id]["usage_count"] += 1
                self.keys[key_id]["last_used"] = datetime.now(timezone.utc)

        except Exception as e:
            logger.error(f"Key usage update failed: {e}")

    async def get_key_statistics(self) -> Dict[str, Any]:
        """Get key management statistics."""
        try:
            total_keys = len(self.keys)
            active_keys = sum(1 for key in self.keys.values() if key["is_active"])
            expired_keys = sum(
                1
                for key in self.keys.values()
                if key["expires_at"] and key["expires_at"] < datetime.now(timezone.utc)
            )

            key_types = {}
            for key in self.keys.values():
                key_type = key["key_type"]
                key_types[key_type] = key_types.get(key_type, 0) + 1

            return {
                "total_keys": total_keys,
                "active_keys": active_keys,
                "expired_keys": expired_keys,
                "key_types": key_types,
                "constitutional_hash": self.constitutional_hash,
            }

        except Exception as e:
            logger.error(f"Key statistics retrieval failed: {e}")
            raise


# Global key manager instance
key_manager = KeyManager()
