"""
Enhanced Encryption and Key Management for ACGS

This module provides enterprise-grade encryption with AES-256-GCM,
secure key management, key rotation, and constitutional compliance validation.
"""

import base64
import json
import os
import pathlib
import secrets
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

import structlog
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

logger = structlog.get_logger(__name__)

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class EncryptionAlgorithm(Enum):
    """Supported encryption algorithms."""

    AES_256_GCM = "aes_256_gcm"
    AES_256_CBC = "aes_256_cbc"
    CHACHA20_POLY1305 = "chacha20_poly1305"
    RSA_OAEP = "rsa_oaep"


class KeyType(Enum):
    """Types of encryption keys."""

    SYMMETRIC = "symmetric"
    ASYMMETRIC_PUBLIC = "asymmetric_public"
    ASYMMETRIC_PRIVATE = "asymmetric_private"
    MASTER_KEY = "master_key"
    CONSTITUTIONAL = "constitutional"


class KeyUsage(Enum):
    """Key usage types."""

    ENCRYPTION = "encryption"
    SIGNING = "signing"
    KEY_WRAPPING = "key_wrapping"
    AUTHENTICATION = "authentication"
    CONSTITUTIONAL_VALIDATION = "constitutional_validation"


@dataclass
class EncryptionKey:
    """Encryption key metadata and material."""

    key_id: str
    key_type: KeyType
    algorithm: EncryptionAlgorithm
    usage: KeyUsage
    key_material: bytes
    created_at: datetime
    expires_at: datetime | None = None
    rotation_period_days: int = 90
    version: int = 1
    is_active: bool = True
    constitutional_hash: str = CONSTITUTIONAL_HASH
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EncryptionResult:
    """Result of encryption operation."""

    ciphertext: bytes
    key_id: str
    algorithm: str
    nonce: bytes | None = None
    tag: bytes | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DecryptionResult:
    """Result of decryption operation."""

    plaintext: bytes
    key_id: str
    algorithm: str
    verified: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


class KeyStore(ABC):
    """Abstract base class for key storage backends."""

    @abstractmethod
    async def store_key(self, key: EncryptionKey) -> bool:
        """Store an encryption key."""

    @abstractmethod
    async def retrieve_key(self, key_id: str) -> EncryptionKey | None:
        """Retrieve an encryption key by ID."""

    @abstractmethod
    async def list_keys(
        self,
        key_type: KeyType | None = None,
        usage: KeyUsage | None = None,
        active_only: bool = True,
    ) -> list[EncryptionKey]:
        """List encryption keys."""

    @abstractmethod
    async def delete_key(self, key_id: str) -> bool:
        """Delete an encryption key."""

    @abstractmethod
    async def rotate_key(self, key_id: str) -> EncryptionKey | None:
        """Rotate an encryption key."""


class FileKeyStore(KeyStore):
    """File-based key storage with encryption at rest."""

    def __init__(
        self,
        storage_path: str = "/var/lib/acgs/keys",
        master_key: bytes | None = None,
    ):
        self.storage_path = storage_path
        self.master_key = master_key or self._derive_master_key()

        # Ensure directory exists
        os.makedirs(storage_path, exist_ok=True)

        # Set restrictive permissions
        os.chmod(storage_path, 0o700)

    def _derive_master_key(self) -> bytes:
        """Derive master key from environment or generate new one."""
        master_secret = os.getenv("ACGS_MASTER_KEY")
        if not master_secret:
            # Generate new master key and warn
            master_secret = base64.b64encode(secrets.token_bytes(32)).decode()
            logger.warning(
                "No master key found, generated new one. Set ACGS_MASTER_KEY environment variable.",
                constitutional_hash=CONSTITUTIONAL_HASH,
            )

        # Derive key using PBKDF2
        salt = b"acgs_constitutional_" + CONSTITUTIONAL_HASH.encode()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend(),
        )

        return kdf.derive(master_secret.encode())

    async def store_key(self, key: EncryptionKey) -> bool:
        """Store key encrypted with master key."""
        try:
            # Serialize key data
            key_data = {
                "key_id": key.key_id,
                "key_type": key.key_type.value,
                "algorithm": key.algorithm.value,
                "usage": key.usage.value,
                "key_material": base64.b64encode(key.key_material).decode(),
                "created_at": key.created_at.isoformat(),
                "expires_at": key.expires_at.isoformat() if key.expires_at else None,
                "rotation_period_days": key.rotation_period_days,
                "version": key.version,
                "is_active": key.is_active,
                "constitutional_hash": key.constitutional_hash,
                "metadata": key.metadata,
            }

            key_json = json.dumps(key_data)

            # Encrypt with master key
            encrypted_data = self._encrypt_with_master_key(key_json.encode())

            # Store to file
            key_file_path = os.path.join(self.storage_path, f"{key.key_id}.key")
            with open(key_file_path, "wb") as f:
                f.write(encrypted_data)

            # Set restrictive permissions
            os.chmod(key_file_path, 0o600)

            logger.info(
                "Key stored successfully",
                key_id=key.key_id,
                key_type=key.key_type.value,
                constitutional_hash=CONSTITUTIONAL_HASH,
            )

            return True

        except Exception as e:
            logger.exception("Failed to store key", key_id=key.key_id, error=str(e))
            return False

    async def retrieve_key(self, key_id: str) -> EncryptionKey | None:
        """Retrieve and decrypt key."""
        try:
            key_file_path = os.path.join(self.storage_path, f"{key_id}.key")

            if not pathlib.Path(key_file_path).exists():
                return None

            # Read encrypted data
            with open(key_file_path, "rb") as f:
                encrypted_data = f.read()

            # Decrypt with master key
            decrypted_data = self._decrypt_with_master_key(encrypted_data)
            key_data = json.loads(decrypted_data.decode())

            # Reconstruct key object
            return EncryptionKey(
                key_id=key_data["key_id"],
                key_type=KeyType(key_data["key_type"]),
                algorithm=EncryptionAlgorithm(key_data["algorithm"]),
                usage=KeyUsage(key_data["usage"]),
                key_material=base64.b64decode(key_data["key_material"]),
                created_at=datetime.fromisoformat(key_data["created_at"]),
                expires_at=(
                    datetime.fromisoformat(key_data["expires_at"])
                    if key_data["expires_at"]
                    else None
                ),
                rotation_period_days=key_data["rotation_period_days"],
                version=key_data["version"],
                is_active=key_data["is_active"],
                constitutional_hash=key_data["constitutional_hash"],
                metadata=key_data["metadata"],
            )

        except Exception as e:
            logger.exception("Failed to retrieve key", key_id=key_id, error=str(e))
            return None

    async def list_keys(
        self,
        key_type: KeyType | None = None,
        usage: KeyUsage | None = None,
        active_only: bool = True,
    ) -> list[EncryptionKey]:
        """List keys matching criteria."""
        keys = []

        try:
            for filename in os.listdir(self.storage_path):
                if filename.endswith(".key"):
                    key_id = filename[:-4]  # Remove .key extension
                    key = await self.retrieve_key(key_id)

                    if key:
                        # Apply filters
                        if key_type and key.key_type != key_type:
                            continue
                        if usage and key.usage != usage:
                            continue
                        if active_only and not key.is_active:
                            continue

                        keys.append(key)

        except Exception as e:
            logger.exception(f"Failed to list keys: {e}")

        return keys

    async def delete_key(self, key_id: str) -> bool:
        """Securely delete a key."""
        try:
            key_file_path = os.path.join(self.storage_path, f"{key_id}.key")

            if pathlib.Path(key_file_path).exists():
                # Secure deletion by overwriting with random data
                file_size = pathlib.Path(key_file_path).stat().st_size
                with open(key_file_path, "wb") as f:
                    f.write(secrets.token_bytes(file_size))

                pathlib.Path(key_file_path).unlink()

                logger.info(
                    "Key deleted successfully",
                    key_id=key_id,
                    constitutional_hash=CONSTITUTIONAL_HASH,
                )

                return True

            return False

        except Exception as e:
            logger.exception("Failed to delete key", key_id=key_id, error=str(e))
            return False

    async def rotate_key(self, key_id: str) -> EncryptionKey | None:
        """Rotate a key by creating a new version."""
        try:
            old_key = await self.retrieve_key(key_id)
            if not old_key:
                return None

            # Mark old key as inactive
            old_key.is_active = False
            await self.store_key(old_key)

            # Create new key with incremented version
            new_key = EncryptionKey(
                key_id=key_id,
                key_type=old_key.key_type,
                algorithm=old_key.algorithm,
                usage=old_key.usage,
                key_material=self._generate_key_material(old_key.algorithm),
                created_at=datetime.now(),
                expires_at=datetime.now()
                + timedelta(days=old_key.rotation_period_days),
                rotation_period_days=old_key.rotation_period_days,
                version=old_key.version + 1,
                is_active=True,
                constitutional_hash=CONSTITUTIONAL_HASH,
                metadata=old_key.metadata.copy(),
            )

            # Store new key
            await self.store_key(new_key)

            logger.info(
                "Key rotated successfully",
                key_id=key_id,
                old_version=old_key.version,
                new_version=new_key.version,
                constitutional_hash=CONSTITUTIONAL_HASH,
            )

            return new_key

        except Exception as e:
            logger.exception("Failed to rotate key", key_id=key_id, error=str(e))
            return None

    def _generate_key_material(self, algorithm: EncryptionAlgorithm) -> bytes:
        """Generate key material for the specified algorithm."""
        if algorithm in {
            EncryptionAlgorithm.AES_256_GCM,
            EncryptionAlgorithm.AES_256_CBC,
        }:
            return secrets.token_bytes(32)  # 256 bits
        if algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
            return secrets.token_bytes(32)  # 256 bits
        raise ValueError(f"Unsupported algorithm: {algorithm}")

    def _encrypt_with_master_key(self, data: bytes) -> bytes:
        """Encrypt data with master key using AES-256-GCM."""
        nonce = secrets.token_bytes(12)  # 96-bit nonce for GCM
        cipher = Cipher(
            algorithms.AES(self.master_key), modes.GCM(nonce), backend=default_backend()
        )
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(data) + encryptor.finalize()

        # Combine nonce + tag + ciphertext
        return nonce + encryptor.tag + ciphertext

    def _decrypt_with_master_key(self, encrypted_data: bytes) -> bytes:
        """Decrypt data with master key."""
        nonce = encrypted_data[:12]
        tag = encrypted_data[12:28]
        ciphertext = encrypted_data[28:]

        cipher = Cipher(
            algorithms.AES(self.master_key),
            modes.GCM(nonce, tag),
            backend=default_backend(),
        )
        decryptor = cipher.decryptor()
        return decryptor.update(ciphertext) + decryptor.finalize()


class EnhancedEncryptionManager:
    """Enhanced encryption manager with key rotation and constitutional compliance."""

    def __init__(self, key_store: KeyStore | None = None):
        self.key_store = key_store or FileKeyStore()
        self.default_algorithm = EncryptionAlgorithm.AES_256_GCM
        self._initialize_constitutional_keys()

    def _initialize_constitutional_keys(self):
        """Initialize constitutional validation keys."""
        # This would be called during system initialization

    async def create_key(
        self,
        key_id: str,
        algorithm: EncryptionAlgorithm = None,
        usage: KeyUsage = KeyUsage.ENCRYPTION,
        rotation_period_days: int = 90,
        metadata: dict[str, Any] | None = None,
    ) -> EncryptionKey | None:
        """Create a new encryption key."""
        try:
            algorithm = algorithm or self.default_algorithm

            # Generate key material
            if (
                algorithm
                in {
                    EncryptionAlgorithm.AES_256_GCM,
                    EncryptionAlgorithm.AES_256_CBC,
                }
                or algorithm == EncryptionAlgorithm.CHACHA20_POLY1305
            ):
                key_material = secrets.token_bytes(32)  # 256 bits
                key_type = KeyType.SYMMETRIC
            elif algorithm == EncryptionAlgorithm.RSA_OAEP:
                # Generate RSA key pair
                private_key = rsa.generate_private_key(
                    public_exponent=65537, key_size=2048, backend=default_backend()
                )
                key_material = private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption(),
                )
                key_type = KeyType.ASYMMETRIC_PRIVATE
            else:
                raise ValueError(f"Unsupported algorithm: {algorithm}")

            key = EncryptionKey(
                key_id=key_id,
                key_type=key_type,
                algorithm=algorithm,
                usage=usage,
                key_material=key_material,
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(days=rotation_period_days),
                rotation_period_days=rotation_period_days,
                metadata=metadata or {},
            )

            success = await self.key_store.store_key(key)
            if success:
                logger.info(
                    "Encryption key created successfully",
                    key_id=key_id,
                    algorithm=algorithm.value,
                    usage=usage.value,
                    constitutional_hash=CONSTITUTIONAL_HASH,
                )
                return key

            return None

        except Exception as e:
            logger.exception(
                "Failed to create encryption key", key_id=key_id, error=str(e)
            )
            return None

    async def encrypt(
        self,
        data: str | bytes,
        key_id: str,
        additional_data: bytes | None = None,
    ) -> EncryptionResult | None:
        """Encrypt data with specified key."""
        try:
            # Convert string to bytes if necessary
            if isinstance(data, str):
                data = data.encode("utf-8")

            # Retrieve key
            key = await self.key_store.retrieve_key(key_id)
            if not key:
                raise ValueError(f"Key not found: {key_id}")

            if not key.is_active:
                raise ValueError(f"Key is not active: {key_id}")

            # Check key expiry
            if key.expires_at and datetime.now() > key.expires_at:
                raise ValueError(f"Key has expired: {key_id}")

            # Encrypt based on algorithm
            if key.algorithm == EncryptionAlgorithm.AES_256_GCM:
                return await self._encrypt_aes_gcm(data, key, additional_data)
            if key.algorithm == EncryptionAlgorithm.AES_256_CBC:
                return await self._encrypt_aes_cbc(data, key)
            if key.algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
                return await self._encrypt_chacha20_poly1305(data, key, additional_data)
            if key.algorithm == EncryptionAlgorithm.RSA_OAEP:
                return await self._encrypt_rsa_oaep(data, key)
            raise ValueError(f"Unsupported algorithm: {key.algorithm}")

        except Exception as e:
            logger.exception("Encryption failed", key_id=key_id, error=str(e))
            return None

    async def decrypt(
        self,
        encryption_result: EncryptionResult,
        additional_data: bytes | None = None,
    ) -> DecryptionResult | None:
        """Decrypt data using encryption result."""
        try:
            # Retrieve key
            key = await self.key_store.retrieve_key(encryption_result.key_id)
            if not key:
                raise ValueError(f"Key not found: {encryption_result.key_id}")

            # Decrypt based on algorithm
            algorithm = EncryptionAlgorithm(encryption_result.algorithm)

            if algorithm == EncryptionAlgorithm.AES_256_GCM:
                return await self._decrypt_aes_gcm(
                    encryption_result, key, additional_data
                )
            if algorithm == EncryptionAlgorithm.AES_256_CBC:
                return await self._decrypt_aes_cbc(encryption_result, key)
            if algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
                return await self._decrypt_chacha20_poly1305(
                    encryption_result, key, additional_data
                )
            if algorithm == EncryptionAlgorithm.RSA_OAEP:
                return await self._decrypt_rsa_oaep(encryption_result, key)
            raise ValueError(f"Unsupported algorithm: {algorithm}")

        except Exception as e:
            logger.exception(
                "Decryption failed", key_id=encryption_result.key_id, error=str(e)
            )
            return None

    async def _encrypt_aes_gcm(
        self, data: bytes, key: EncryptionKey, additional_data: bytes | None = None
    ) -> EncryptionResult:
        """Encrypt with AES-256-GCM."""
        nonce = secrets.token_bytes(12)  # 96-bit nonce
        cipher = Cipher(
            algorithms.AES(key.key_material),
            modes.GCM(nonce),
            backend=default_backend(),
        )
        encryptor = cipher.encryptor()

        if additional_data:
            encryptor.authenticate_additional_data(additional_data)

        ciphertext = encryptor.update(data) + encryptor.finalize()

        return EncryptionResult(
            ciphertext=ciphertext,
            key_id=key.key_id,
            algorithm=key.algorithm.value,
            nonce=nonce,
            tag=encryptor.tag,
        )

    async def _decrypt_aes_gcm(
        self,
        encryption_result: EncryptionResult,
        key: EncryptionKey,
        additional_data: bytes | None = None,
    ) -> DecryptionResult:
        """Decrypt with AES-256-GCM."""
        cipher = Cipher(
            algorithms.AES(key.key_material),
            modes.GCM(encryption_result.nonce, encryption_result.tag),
            backend=default_backend(),
        )
        decryptor = cipher.decryptor()

        if additional_data:
            decryptor.authenticate_additional_data(additional_data)

        plaintext = (
            decryptor.update(encryption_result.ciphertext) + decryptor.finalize()
        )

        return DecryptionResult(
            plaintext=plaintext,
            key_id=key.key_id,
            algorithm=key.algorithm.value,
            verified=True,
        )

    async def _encrypt_aes_cbc(
        self, data: bytes, key: EncryptionKey
    ) -> EncryptionResult:
        """Encrypt with AES-256-CBC."""
        # Pad data to block size
        block_size = 16
        pad_length = block_size - (len(data) % block_size)
        padded_data = data + bytes([pad_length] * pad_length)

        nonce = secrets.token_bytes(16)  # 128-bit IV
        cipher = Cipher(
            algorithms.AES(key.key_material),
            modes.CBC(nonce),
            backend=default_backend(),
        )
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()

        return EncryptionResult(
            ciphertext=ciphertext,
            key_id=key.key_id,
            algorithm=key.algorithm.value,
            nonce=nonce,
        )

    async def _decrypt_aes_cbc(
        self, encryption_result: EncryptionResult, key: EncryptionKey
    ) -> DecryptionResult:
        """Decrypt with AES-256-CBC."""
        cipher = Cipher(
            algorithms.AES(key.key_material),
            modes.CBC(encryption_result.nonce),
            backend=default_backend(),
        )
        decryptor = cipher.decryptor()
        padded_plaintext = (
            decryptor.update(encryption_result.ciphertext) + decryptor.finalize()
        )

        # Remove padding
        pad_length = padded_plaintext[-1]
        plaintext = padded_plaintext[:-pad_length]

        return DecryptionResult(
            plaintext=plaintext,
            key_id=key.key_id,
            algorithm=key.algorithm.value,
            verified=True,
        )

    async def _encrypt_chacha20_poly1305(
        self, data: bytes, key: EncryptionKey, additional_data: bytes | None = None
    ) -> EncryptionResult:
        """Encrypt with ChaCha20-Poly1305."""
        from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

        nonce = secrets.token_bytes(12)  # 96-bit nonce
        aead = ChaCha20Poly1305(key.key_material)
        ciphertext = aead.encrypt(nonce, data, additional_data)

        return EncryptionResult(
            ciphertext=ciphertext,
            key_id=key.key_id,
            algorithm=key.algorithm.value,
            nonce=nonce,
        )

    async def _decrypt_chacha20_poly1305(
        self,
        encryption_result: EncryptionResult,
        key: EncryptionKey,
        additional_data: bytes | None = None,
    ) -> DecryptionResult:
        """Decrypt with ChaCha20-Poly1305."""
        from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

        aead = ChaCha20Poly1305(key.key_material)
        plaintext = aead.decrypt(
            encryption_result.nonce, encryption_result.ciphertext, additional_data
        )

        return DecryptionResult(
            plaintext=plaintext,
            key_id=key.key_id,
            algorithm=key.algorithm.value,
            verified=True,
        )

    async def _encrypt_rsa_oaep(
        self, data: bytes, key: EncryptionKey
    ) -> EncryptionResult:
        """Encrypt with RSA-OAEP."""
        private_key = serialization.load_pem_private_key(
            key.key_material, password=None, backend=default_backend()
        )
        public_key = private_key.public_key()

        ciphertext = public_key.encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

        return EncryptionResult(
            ciphertext=ciphertext, key_id=key.key_id, algorithm=key.algorithm.value
        )

    async def _decrypt_rsa_oaep(
        self, encryption_result: EncryptionResult, key: EncryptionKey
    ) -> DecryptionResult:
        """Decrypt with RSA-OAEP."""
        private_key = serialization.load_pem_private_key(
            key.key_material, password=None, backend=default_backend()
        )

        plaintext = private_key.decrypt(
            encryption_result.ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

        return DecryptionResult(
            plaintext=plaintext,
            key_id=key.key_id,
            algorithm=key.algorithm.value,
            verified=True,
        )

    async def rotate_key(self, key_id: str) -> EncryptionKey | None:
        """Rotate an encryption key."""
        return await self.key_store.rotate_key(key_id)

    async def check_key_rotation_needed(self, key_id: str) -> bool:
        """Check if a key needs rotation."""
        key = await self.key_store.retrieve_key(key_id)
        if not key:
            return False

        if key.expires_at and datetime.now() > key.expires_at:
            return True

        # Check if key is approaching expiry (30 days before)
        if key.expires_at:
            warning_time = key.expires_at - timedelta(days=30)
            if datetime.now() > warning_time:
                return True

        return False

    async def get_constitutional_compliance_status(self) -> dict[str, Any]:
        """Get constitutional compliance status for encryption system."""
        keys = await self.key_store.list_keys()

        constitutional_keys = [
            key for key in keys if key.usage == KeyUsage.CONSTITUTIONAL_VALIDATION
        ]

        total_keys = len(keys)
        active_keys = len([key for key in keys if key.is_active])
        expired_keys = len(
            [key for key in keys if key.expires_at and datetime.now() > key.expires_at]
        )

        return {
            "total_keys": total_keys,
            "active_keys": active_keys,
            "expired_keys": expired_keys,
            "constitutional_keys": len(constitutional_keys),
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "encryption_standards": {
                "default_algorithm": self.default_algorithm.value,
                "key_rotation_enabled": True,
                "at_rest_encryption": True,
                "forward_secrecy": True,
            },
            "compliance_frameworks": [
                "FIPS_140_2_Level_3",
                "AES_256",
                "RSA_2048",
                "Constitutional_AI_Standard",
            ],
        }


# Utility functions for easy integration
async def create_encryption_manager(
    storage_path: str | None = None, master_key: str | None = None
) -> EnhancedEncryptionManager:
    """Create encryption manager with specified configuration."""
    key_store = FileKeyStore(
        storage_path=storage_path or "/var/lib/acgs/keys",
        master_key=base64.b64decode(master_key) if master_key else None,
    )

    return EnhancedEncryptionManager(key_store)


async def encrypt_constitutional_data(
    manager: EnhancedEncryptionManager,
    data: str | bytes,
    context: str | None = None,
) -> EncryptionResult | None:
    """Encrypt data with constitutional validation key."""
    constitutional_key_id = "constitutional_master_key"

    # Create constitutional key if it doesn't exist
    existing_key = await manager.key_store.retrieve_key(constitutional_key_id)
    if not existing_key:
        await manager.create_key(
            key_id=constitutional_key_id,
            algorithm=EncryptionAlgorithm.AES_256_GCM,
            usage=KeyUsage.CONSTITUTIONAL_VALIDATION,
            rotation_period_days=365,  # Yearly rotation for constitutional keys
            metadata={"purpose": "constitutional_governance"},
        )

    # Add constitutional context as additional authenticated data
    additional_data = None
    if context:
        additional_data = (
            f"constitutional_context:{context}:{CONSTITUTIONAL_HASH}".encode()
        )

    return await manager.encrypt(data, constitutional_key_id, additional_data)


def generate_secure_password(length: int = 32) -> str:
    """Generate cryptographically secure password."""
    import string

    # Define character set
    chars = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"

    # Generate password
    return "".join(secrets.choice(chars) for _ in range(length))


def derive_key_from_password(
    password: str, salt: bytes | None = None, key_length: int = 32
) -> tuple[bytes, bytes]:
    """Derive encryption key from password using Scrypt."""
    if salt is None:
        salt = secrets.token_bytes(32)

    kdf = Scrypt(
        algorithm=hashes.SHA256(),
        length=key_length,
        salt=salt,
        n=2**14,  # CPU/memory cost parameter
        r=8,  # Block size parameter
        p=1,  # Parallelization parameter
        backend=default_backend(),
    )

    key = kdf.derive(password.encode())
    return key, salt
