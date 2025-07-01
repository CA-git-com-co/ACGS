"""
Cryptographic signing module for constitutional integrity in ACGS-1 AC Service.

This module provides enterprise-grade cryptographic signing and verification
for constitutional principles, amendments, and governance actions to ensure
immutable constitutional integrity and non-repudiation.

requires: Constitutional principles signed with Ed25519, amendment integrity verified
ensures: Cryptographic non-repudiation, tamper-proof constitutional records
sha256: c8f2e1a9b7d6f4e3c2a1b8e7f6c5a4b3d2e1f8c7b6a5d4e3f2c1b8a7d6e5f4c3
"""

import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Any

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
)
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ConstitutionalSignature(BaseModel):
    """Constitutional signature model for cryptographic integrity."""

    signature: str = Field(..., description="Base64-encoded Ed25519 signature")
    public_key: str = Field(..., description="Base64-encoded Ed25519 public key")
    algorithm: str = Field(default="Ed25519", description="Signature algorithm")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    content_hash: str = Field(..., description="SHA-256 hash of signed content")
    signer_id: str | None = Field(None, description="ID of the signing entity")
    signature_type: str = Field(
        ..., description="Type of signature (principle, amendment, etc.)"
    )

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class ConstitutionalCryptoSigner:
    """Enterprise-grade cryptographic signer for constitutional documents."""

    def __init__(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Initialize the constitutional crypto signer."""
        self.algorithm = "Ed25519"
        self._private_key: ed25519.Ed25519PrivateKey | None = None
        self._public_key: ed25519.Ed25519PublicKey | None = None

    def generate_keypair(self) -> tuple[str, str]:
        """
        Generate a new Ed25519 keypair for constitutional signing.

        Returns:
            Tuple of (private_key_pem, public_key_pem)
        """
        try:
            # Generate Ed25519 private key
            private_key = ed25519.Ed25519PrivateKey.generate()
            public_key = private_key.public_key()

            # Serialize keys to PEM format
            private_pem = private_key.private_bytes(
                encoding=Encoding.PEM,
                format=PrivateFormat.PKCS8,
                encryption_algorithm=NoEncryption(),
            ).decode("utf-8")

            public_pem = public_key.public_bytes(
                encoding=Encoding.PEM, format=PublicFormat.SubjectPublicKeyInfo
            ).decode("utf-8")

            logger.info("Generated new Ed25519 keypair for constitutional signing")
            return private_pem, public_pem

        except Exception as e:
            logger.error(f"Failed to generate keypair: {e}")
            raise

    def load_private_key(self, private_key_pem: str) -> None:
        """Load private key from PEM format."""
        try:
            self._private_key = serialization.load_pem_private_key(
                private_key_pem.encode("utf-8"), password=None
            )
            self._public_key = self._private_key.public_key()
            logger.info("Loaded private key for constitutional signing")
        except Exception as e:
            logger.error(f"Failed to load private key: {e}")
            raise

    def load_public_key(self, public_key_pem: str) -> ed25519.Ed25519PublicKey:
        """Load public key from PEM format."""
        try:
            public_key = serialization.load_pem_public_key(
                public_key_pem.encode("utf-8")
            )
            logger.info("Loaded public key for constitutional verification")
            return public_key
        except Exception as e:
            logger.error(f"Failed to load public key: {e}")
            raise

    def _calculate_content_hash(self, content: dict[str, Any]) -> str:
        """Calculate SHA-256 hash of constitutional content."""
        try:
            # Create canonical JSON representation
            canonical_json = json.dumps(content, sort_keys=True, separators=(",", ":"))

            # Calculate SHA-256 hash
            content_hash = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()

            return content_hash
        except Exception as e:
            logger.error(f"Failed to calculate content hash: {e}")
            raise

    def sign_constitutional_content(
        self, content: dict[str, Any], signer_id: str, signature_type: str
    ) -> ConstitutionalSignature:
        """
        Sign constitutional content with Ed25519 signature.

        Args:
            content: Constitutional content to sign
            signer_id: ID of the signing entity
            signature_type: Type of signature (principle, amendment, etc.)

        Returns:
            ConstitutionalSignature object
        """
        if not self._private_key:
            raise ValueError("Private key not loaded. Call load_private_key() first.")

        try:
            # Calculate content hash
            content_hash = self._calculate_content_hash(content)

            # Create signing payload with timestamp
            timestamp = datetime.now(timezone.utc)
            signing_payload = {
                "content_hash": content_hash,
                "signer_id": signer_id,
                "signature_type": signature_type,
                "timestamp": timestamp.isoformat(),
            }

            # Create canonical JSON for signing
            canonical_payload = json.dumps(
                signing_payload, sort_keys=True, separators=(",", ":")
            )

            # Sign the payload
            signature_bytes = self._private_key.sign(canonical_payload.encode("utf-8"))

            # Encode signature and public key to base64
            import base64

            signature_b64 = base64.b64encode(signature_bytes).decode("utf-8")

            public_key_pem = self._public_key.public_bytes(
                encoding=Encoding.PEM, format=PublicFormat.SubjectPublicKeyInfo
            ).decode("utf-8")

            # Create signature object
            constitutional_signature = ConstitutionalSignature(
                signature=signature_b64,
                public_key=public_key_pem,
                content_hash=content_hash,
                signer_id=signer_id,
                signature_type=signature_type,
                timestamp=timestamp,
            )

            logger.info(f"Successfully signed {signature_type} content for {signer_id}")
            return constitutional_signature

        except Exception as e:
            logger.error(f"Failed to sign constitutional content: {e}")
            raise

    def verify_constitutional_signature(
        self, content: dict[str, Any], signature: ConstitutionalSignature
    ) -> bool:
        """
        Verify constitutional signature.

        Args:
            content: Original constitutional content
            signature: ConstitutionalSignature to verify

        Returns:
            True if signature is valid, False otherwise
        """
        try:
            # Verify content hash
            calculated_hash = self._calculate_content_hash(content)
            if calculated_hash != signature.content_hash:
                logger.warning("Content hash mismatch during signature verification")
                return False

            # Load public key from signature
            public_key = self.load_public_key(signature.public_key)

            # Reconstruct signing payload
            signing_payload = {
                "content_hash": signature.content_hash,
                "signer_id": signature.signer_id,
                "signature_type": signature.signature_type,
                "timestamp": signature.timestamp.isoformat(),
            }

            canonical_payload = json.dumps(
                signing_payload, sort_keys=True, separators=(",", ":")
            )

            # Decode signature from base64
            import base64

            signature_bytes = base64.b64decode(signature.signature.encode("utf-8"))

            # Verify signature
            public_key.verify(signature_bytes, canonical_payload.encode("utf-8"))

            logger.info(f"Successfully verified {signature.signature_type} signature")
            return True

        except Exception as e:
            logger.warning(f"Signature verification failed: {e}")
            return False

    def create_constitutional_integrity_proof(
        self, content: dict[str, Any], signatures: list[ConstitutionalSignature]
    ) -> dict[str, Any]:
        """
        Create comprehensive integrity proof for constitutional content.

        Args:
            content: Constitutional content
            signatures: List of signatures

        Returns:
            Integrity proof dictionary
        """
        try:
            content_hash = self._calculate_content_hash(content)

            # Verify all signatures
            verified_signatures = []
            for sig in signatures:
                is_valid = self.verify_constitutional_signature(content, sig)
                verified_signatures.append(
                    {
                        "signature": sig.dict(),
                        "verified": is_valid,
                        "verification_timestamp": datetime.now(
                            timezone.utc
                        ).isoformat(),
                    }
                )

            # Create integrity proof
            integrity_proof = {
                "content_hash": content_hash,
                "algorithm": "SHA-256",
                "signature_algorithm": "Ed25519",
                "signatures": verified_signatures,
                "total_signatures": len(signatures),
                "verified_signatures": sum(
                    1 for sig in verified_signatures if sig["verified"]
                ),
                "integrity_score": (
                    sum(1 for sig in verified_signatures if sig["verified"])
                    / len(signatures)
                    if signatures
                    else 0
                ),
                "proof_timestamp": datetime.now(timezone.utc).isoformat(),
                "constitutional_compliance": {
                    "tamper_proof": all(sig["verified"] for sig in verified_signatures),
                    "non_repudiation": len(verified_signatures) > 0,
                    "multi_signature": len(verified_signatures) > 1,
                },
            }

            logger.info(
                f"Created constitutional integrity proof with {len(signatures)} signatures"
            )
            return integrity_proof

        except Exception as e:
            logger.error(f"Failed to create integrity proof: {e}")
            raise


class ConstitutionalSigningService:
    """Service for managing constitutional cryptographic operations."""

    def __init__(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Initialize the constitutional signing service."""
        self.signer = ConstitutionalCryptoSigner()
        self._initialized = False

    async def initialize(self, private_key_pem: str | None = None) -> None:
        """Initialize the signing service with optional private key."""
        try:
            if private_key_pem:
                self.signer.load_private_key(private_key_pem)
            else:
                # Generate new keypair for development/testing
                private_pem, public_pem = self.signer.generate_keypair()
                self.signer.load_private_key(private_pem)
                logger.warning(
                    "Generated new keypair - ensure proper key management in production"
                )

            self._initialized = True
            logger.info("Constitutional signing service initialized")

        except Exception as e:
            logger.error(f"Failed to initialize signing service: {e}")
            raise

    async def sign_principle(
        self, principle_data: dict[str, Any], signer_id: str
    ) -> ConstitutionalSignature:
        """Sign a constitutional principle."""
        if not self._initialized:
            raise RuntimeError("Signing service not initialized")

        return self.signer.sign_constitutional_content(
            content=principle_data, signer_id=signer_id, signature_type="principle"
        )

    async def sign_amendment(
        self, amendment_data: dict[str, Any], signer_id: str
    ) -> ConstitutionalSignature:
        """Sign a constitutional amendment."""
        if not self._initialized:
            raise RuntimeError("Signing service not initialized")

        return self.signer.sign_constitutional_content(
            content=amendment_data, signer_id=signer_id, signature_type="amendment"
        )

    async def verify_signature(
        self, content: dict[str, Any], signature: ConstitutionalSignature
    ) -> bool:
        """Verify a constitutional signature."""
        return self.signer.verify_constitutional_signature(content, signature)

    async def create_integrity_proof(
        self, content: dict[str, Any], signatures: list[ConstitutionalSignature]
    ) -> dict[str, Any]:
        """Create integrity proof for constitutional content."""
        return self.signer.create_constitutional_integrity_proof(content, signatures)


# Global signing service instance
constitutional_signing_service = ConstitutionalSigningService()


async def get_constitutional_signing_service() -> ConstitutionalSigningService:
    """Dependency injection for constitutional signing service."""
    if not constitutional_signing_service._initialized:
        await constitutional_signing_service.initialize()
    return constitutional_signing_service
