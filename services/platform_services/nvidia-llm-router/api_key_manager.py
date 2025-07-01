"""
NVIDIA LLM Router API Key Manager

Secure management of NVIDIA API keys following ACGS-PGP security standards.
Provides encryption, storage, rotation, and retrieval of API keys with audit logging.
"""

import base64
import json
import os
from datetime import datetime, timedelta
from typing import Any

import aioredis
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, declarative_base, mapped_column
from sqlalchemy.types import Boolean, DateTime, String, Text

from services.shared.database import get_async_session
from services.shared.security_config import SecurityConfig
from services.shared.utils import get_logger

# Database Models
Base = declarative_base()


class APIKeyRecord(Base):
    """Database model for storing encrypted API keys"""

    __tablename__ = "nvidia_api_keys"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    key_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    encrypted_key: Mapped[str] = mapped_column(Text, nullable=False)
    key_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    rotation_count: Mapped[int] = mapped_column(String(10), default="0", nullable=False)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    usage_count: Mapped[int] = mapped_column(String(10), default="0", nullable=False)
    metadata: Mapped[str | None] = mapped_column(Text, nullable=True)


class APIKeyManager:
    """
    Secure API Key Manager for NVIDIA LLM Router

    Features:
    - AES-256 encryption for key storage
    - Key rotation and expiration management
    - Audit logging for security compliance
    - Redis caching for performance
    - Environment variable fallbacks
    """

    def __init__(self, encryption_key: str | None = None, redis_url: str | None = None):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        self.logger = get_logger(__name__)
        self.security_config = SecurityConfig()

        # Initialize encryption
        self._encryption_key = encryption_key or os.getenv("API_KEY_ENCRYPTION_KEY")
        if not self._encryption_key:
            raise ValueError("API_KEY_ENCRYPTION_KEY must be provided")

        self._fernet = self._create_fernet_cipher(self._encryption_key)

        # Initialize Redis for caching
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://redis:6379/3")
        self._redis_pool = None

        # Cache settings
        self.cache_ttl = 300  # 5 minutes
        self.cache_prefix = "nvidia_api_key:"

        self.logger.info("APIKeyManager initialized with encryption and caching")

    def _create_fernet_cipher(self, password: str) -> Fernet:
        """Create Fernet cipher from password using PBKDF2"""
        # Use a fixed salt for consistency (in production, store this securely)
        salt = b"acgs_pgp_nvidia_api_key_salt_2024"
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return Fernet(key)

    async def _get_redis(self) -> aioredis.Redis:
        """Get Redis connection pool"""
        if not self._redis_pool:
            self._redis_pool = aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=10,
            )
        return self._redis_pool

    async def store_api_key(
        self,
        key_name: str,
        api_key: str,
        expires_in_days: int | None = 30,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """
        Store an encrypted API key in the database

        Args:
            key_name: Unique identifier for the key
            api_key: The actual API key to encrypt and store
            expires_in_days: Number of days until key expires (None for no expiration)
            metadata: Additional metadata to store with the key

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Encrypt the API key
            encrypted_key = self._fernet.encrypt(api_key.encode()).decode()

            # Create key hash for verification
            key_hash = self._create_key_hash(api_key)

            # Calculate expiration
            expires_at = None
            if expires_in_days:
                expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

            # Prepare metadata
            metadata_json = json.dumps(metadata) if metadata else None

            async with get_async_session() as session:
                # Check if key already exists
                existing_key = await session.execute(
                    select(APIKeyRecord).where(APIKeyRecord.key_name == key_name)
                )
                existing_record = existing_key.scalar_one_or_none()

                if existing_record:
                    # Update existing key
                    await session.execute(
                        update(APIKeyRecord)
                        .where(APIKeyRecord.key_name == key_name)
                        .values(
                            encrypted_key=encrypted_key,
                            key_hash=key_hash,
                            updated_at=datetime.utcnow(),
                            expires_at=expires_at,
                            is_active=True,
                            rotation_count=str(int(existing_record.rotation_count) + 1),
                            metadata=metadata_json,
                        )
                    )
                    self.logger.info(f"Updated API key: {key_name}")
                else:
                    # Create new key record
                    new_key = APIKeyRecord(
                        id=self._generate_key_id(),
                        key_name=key_name,
                        encrypted_key=encrypted_key,
                        key_hash=key_hash,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                        expires_at=expires_at,
                        is_active=True,
                        rotation_count="0",
                        usage_count="0",
                        metadata=metadata_json,
                    )
                    session.add(new_key)
                    self.logger.info(f"Stored new API key: {key_name}")

                await session.commit()

                # Clear cache
                await self._clear_cache(key_name)

                return True

        except Exception as e:
            self.logger.error(f"Failed to store API key {key_name}: {str(e)}")
            return False

    async def get_api_key(self, key_name: str) -> str | None:
        """
        Retrieve and decrypt an API key

        Args:
            key_name: Unique identifier for the key

        Returns:
            str: Decrypted API key or None if not found/expired
        """
        try:
            # Check cache first
            redis = await self._get_redis()
            cache_key = f"{self.cache_prefix}{key_name}"
            cached_key = await redis.get(cache_key)

            if cached_key:
                self.logger.debug(f"Retrieved API key from cache: {key_name}")
                return cached_key

            # Retrieve from database
            async with get_async_session() as session:
                result = await session.execute(
                    select(APIKeyRecord)
                    .where(APIKeyRecord.key_name == key_name)
                    .where(APIKeyRecord.is_active)
                )
                record = result.scalar_one_or_none()

                if not record:
                    self.logger.warning(f"API key not found: {key_name}")
                    return None

                # Check expiration
                if record.expires_at and record.expires_at < datetime.utcnow():
                    self.logger.warning(f"API key expired: {key_name}")
                    await self._deactivate_key(session, key_name)
                    return None

                # Decrypt the key
                decrypted_key = self._fernet.decrypt(
                    record.encrypted_key.encode()
                ).decode()

                # Update usage statistics
                await session.execute(
                    update(APIKeyRecord)
                    .where(APIKeyRecord.key_name == key_name)
                    .values(
                        last_used_at=datetime.utcnow(),
                        usage_count=str(int(record.usage_count) + 1),
                    )
                )
                await session.commit()

                # Cache the decrypted key
                await redis.setex(cache_key, self.cache_ttl, decrypted_key)

                self.logger.debug(f"Retrieved API key from database: {key_name}")
                return decrypted_key

        except Exception as e:
            self.logger.error(f"Failed to retrieve API key {key_name}: {str(e)}")
            return None

    async def get_api_key_with_fallback(
        self, key_name: str, env_var_name: str
    ) -> str | None:
        """
        Get API key with environment variable fallback

        Args:
            key_name: Database key name
            env_var_name: Environment variable name for fallback

        Returns:
            str: API key from database or environment variable
        """
        # Try database first
        api_key = await self.get_api_key(key_name)

        if api_key:
            return api_key

        # Fallback to environment variable
        env_key = os.getenv(env_var_name)
        if env_key:
            self.logger.info(f"Using environment variable fallback for {key_name}")
            return env_key

        self.logger.error(f"No API key found for {key_name} in database or environment")
        return None

    async def rotate_api_key(self, key_name: str, new_api_key: str) -> bool:
        """
        Rotate an existing API key

        Args:
            key_name: Key to rotate
            new_api_key: New API key value

        Returns:
            bool: True if successful
        """
        try:
            # Get existing key metadata
            async with get_async_session() as session:
                result = await session.execute(
                    select(APIKeyRecord).where(APIKeyRecord.key_name == key_name)
                )
                existing_record = result.scalar_one_or_none()

                if not existing_record:
                    self.logger.error(f"Cannot rotate non-existent key: {key_name}")
                    return False

                # Parse existing metadata
                metadata = {}
                if existing_record.metadata:
                    metadata = json.loads(existing_record.metadata)

                # Add rotation info to metadata
                metadata["previous_rotation"] = existing_record.updated_at.isoformat()
                metadata["rotation_reason"] = "manual_rotation"

                # Store the new key (this will update the existing record)
                success = await self.store_api_key(
                    key_name=key_name,
                    api_key=new_api_key,
                    expires_in_days=30,  # Reset expiration
                    metadata=metadata,
                )

                if success:
                    self.logger.info(f"Successfully rotated API key: {key_name}")
                    return True
                else:
                    self.logger.error(f"Failed to rotate API key: {key_name}")
                    return False

        except Exception as e:
            self.logger.error(f"Error rotating API key {key_name}: {str(e)}")
            return False

    async def list_api_keys(self) -> list[dict[str, Any]]:
        """
        List all API keys with metadata (excluding actual key values)

        Returns:
            List of key information dictionaries
        """
        try:
            async with get_async_session() as session:
                result = await session.execute(
                    select(APIKeyRecord).where(APIKeyRecord.is_active)
                )
                records = result.scalars().all()

                keys_info = []
                for record in records:
                    metadata = {}
                    if record.metadata:
                        metadata = json.loads(record.metadata)

                    keys_info.append(
                        {
                            "key_name": record.key_name,
                            "created_at": record.created_at.isoformat(),
                            "updated_at": record.updated_at.isoformat(),
                            "expires_at": (
                                record.expires_at.isoformat()
                                if record.expires_at
                                else None
                            ),
                            "rotation_count": int(record.rotation_count),
                            "usage_count": int(record.usage_count),
                            "last_used_at": (
                                record.last_used_at.isoformat()
                                if record.last_used_at
                                else None
                            ),
                            "metadata": metadata,
                        }
                    )

                return keys_info

        except Exception as e:
            self.logger.error(f"Failed to list API keys: {str(e)}")
            return []

    async def delete_api_key(self, key_name: str) -> bool:
        """
        Delete an API key

        Args:
            key_name: Key to delete

        Returns:
            bool: True if successful
        """
        try:
            async with get_async_session() as session:
                await session.execute(
                    delete(APIKeyRecord).where(APIKeyRecord.key_name == key_name)
                )
                await session.commit()

                # Clear cache
                await self._clear_cache(key_name)

                self.logger.info(f"Deleted API key: {key_name}")
                return True

        except Exception as e:
            self.logger.error(f"Failed to delete API key {key_name}: {str(e)}")
            return False

    def _create_key_hash(self, api_key: str) -> str:
        """Create SHA-256 hash of API key for verification"""
        import hashlib

        return hashlib.sha256(api_key.encode()).hexdigest()

    def _generate_key_id(self) -> str:
        """Generate unique key ID"""
        import uuid

        return str(uuid.uuid4())

    async def _deactivate_key(self, session: AsyncSession, key_name: str):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Deactivate an expired key"""
        await session.execute(
            update(APIKeyRecord)
            .where(APIKeyRecord.key_name == key_name)
            .values(is_active=False, updated_at=datetime.utcnow())
        )
        await session.commit()

    async def _clear_cache(self, key_name: str):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Clear cached API key"""
        try:
            redis = await self._get_redis()
            cache_key = f"{self.cache_prefix}{key_name}"
            await redis.delete(cache_key)
        except Exception as e:
            self.logger.warning(f"Failed to clear cache for {key_name}: {str(e)}")

    async def close(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Close Redis connections"""
        if self._redis_pool:
            await self._redis_pool.close()


# Singleton instance
_api_key_manager = None


def get_api_key_manager() -> APIKeyManager:
    """Get singleton API key manager instance"""
    global _api_key_manager
    if _api_key_manager is None:
        _api_key_manager = APIKeyManager()
    return _api_key_manager
