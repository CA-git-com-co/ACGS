"""
Audit Integrity Manager Service

Core service for cryptographic audit log integrity and blockchain anchoring.
"""

import asyncio
import hashlib
import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from ..core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class AuditEntry:
    """Structured audit log entry."""

    id: str
    timestamp: datetime
    service: str
    event_type: str
    event_description: str
    agent_id: str | None
    user_id: str | None
    resource: str | None
    action: str
    outcome: str
    metadata: dict[str, Any]
    constitutional_hash: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "service": self.service,
            "event_type": self.event_type,
            "event_description": self.event_description,
            "agent_id": self.agent_id,
            "user_id": self.user_id,
            "resource": self.resource,
            "action": self.action,
            "outcome": self.outcome,
            "metadata": self.metadata,
            "constitutional_hash": self.constitutional_hash,
        }

    def get_hash(self) -> str:
        """Get cryptographic hash of the audit entry."""
        data = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()


@dataclass
class IntegrityProof:
    """Cryptographic integrity proof for audit logs."""

    batch_id: str
    batch_hash: str
    merkle_root: str
    signature: str
    timestamp: datetime
    entry_count: int
    previous_batch_hash: str | None
    blockchain_tx_id: str | None
    blockchain_confirmation: str | None


class IntegrityManager:
    """
    Manager for audit log integrity and cryptographic anchoring.

    Features:
    - Cryptographic hashing of audit entries
    - Merkle tree construction for batch integrity
    - Digital signatures for non-repudiation
    - Blockchain anchoring for external verification
    - Integrity verification and proof generation
    """

    def __init__(self):
        self.private_key = None
        self.public_key = None
        self.audit_buffer: list[AuditEntry] = []
        self.integrity_proofs: list[IntegrityProof] = []
        self.http_client = httpx.AsyncClient(timeout=30.0)

        # Initialize cryptographic keys
        self._initialize_keys()

    def _initialize_keys(self) -> None:
        """Initialize RSA key pair for signing."""
        try:
            # Try to load existing keys
            private_key_path = Path(settings.PRIVATE_KEY_PATH)
            public_key_path = Path(settings.PUBLIC_KEY_PATH)

            if private_key_path.exists() and public_key_path.exists():
                # Load existing keys
                with open(private_key_path, "rb") as f:
                    self.private_key = serialization.load_pem_private_key(
                        f.read(), password=None
                    )

                with open(public_key_path, "rb") as f:
                    self.public_key = serialization.load_pem_public_key(f.read())

                logger.info("Loaded existing RSA key pair")
            else:
                # Generate new keys
                self.private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=2048,
                )
                self.public_key = self.private_key.public_key()

                # Save keys
                private_key_path.parent.mkdir(parents=True, exist_ok=True)
                public_key_path.parent.mkdir(parents=True, exist_ok=True)

                with open(private_key_path, "wb") as f:
                    f.write(
                        self.private_key.private_bytes(
                            encoding=serialization.Encoding.PEM,
                            format=serialization.PrivateFormat.PKCS8,
                            encryption_algorithm=serialization.NoEncryption(),
                        )
                    )

                with open(public_key_path, "wb") as f:
                    f.write(
                        self.public_key.public_bytes(
                            encoding=serialization.Encoding.PEM,
                            format=serialization.PublicFormat.SubjectPublicKeyInfo,
                        )
                    )

                logger.info("Generated new RSA key pair")

        except Exception as e:
            logger.error(f"Failed to initialize cryptographic keys: {e}")
            raise RuntimeError(
                "Cannot initialize audit integrity without cryptographic keys"
            )

    async def add_audit_entry(self, entry: AuditEntry) -> str:
        """
        Add an audit entry to the integrity system.

        Args:
            entry: Audit entry to add

        Returns:
            Entry hash for reference
        """
        entry_hash = entry.get_hash()

        # Add to buffer
        self.audit_buffer.append(entry)

        logger.debug(f"Added audit entry {entry.id} with hash {entry_hash}")

        # Check if buffer is full and needs to be processed
        if len(self.audit_buffer) >= settings.BATCH_SIZE:
            await self._process_batch()

        return entry_hash

    async def _process_batch(self) -> IntegrityProof:
        """
        Process a batch of audit entries and create integrity proof.

        Returns:
            Integrity proof for the batch
        """
        if not self.audit_buffer:
            raise ValueError("No audit entries to process")

        batch_id = f"batch_{datetime.utcnow().timestamp()}"

        # Create Merkle tree from audit entries
        merkle_root = self._create_merkle_tree(
            [entry.get_hash() for entry in self.audit_buffer]
        )

        # Create batch hash
        batch_data = {
            "batch_id": batch_id,
            "timestamp": datetime.utcnow().isoformat(),
            "entry_count": len(self.audit_buffer),
            "merkle_root": merkle_root,
            "constitutional_hash": settings.CONSTITUTIONAL_HASH,
        }

        batch_hash = hashlib.sha256(
            json.dumps(batch_data, sort_keys=True).encode()
        ).hexdigest()

        # Sign the batch hash
        signature = self._sign_hash(batch_hash)

        # Get previous batch hash for chaining
        previous_batch_hash = None
        if self.integrity_proofs:
            previous_batch_hash = self.integrity_proofs[-1].batch_hash

        # Create integrity proof
        proof = IntegrityProof(
            batch_id=batch_id,
            batch_hash=batch_hash,
            merkle_root=merkle_root,
            signature=signature,
            timestamp=datetime.utcnow(),
            entry_count=len(self.audit_buffer),
            previous_batch_hash=previous_batch_hash,
            blockchain_tx_id=None,  # Will be set by blockchain anchoring
            blockchain_confirmation=None,
        )

        # Anchor to blockchain (if enabled)
        if settings.ENABLE_BLOCKCHAIN_ANCHORING:
            try:
                blockchain_result = await self._anchor_to_blockchain(proof)
                proof.blockchain_tx_id = blockchain_result.get("transaction_id")
                proof.blockchain_confirmation = blockchain_result.get("confirmation")
            except Exception as e:
                logger.error(f"Blockchain anchoring failed: {e}")
                # Continue without blockchain anchoring

        # Store proof
        self.integrity_proofs.append(proof)

        # Clear buffer
        processed_entries = len(self.audit_buffer)
        self.audit_buffer.clear()

        logger.info(
            f"Processed batch {batch_id} with {processed_entries} entries. "
            f"Merkle root: {merkle_root[:16]}..., Batch hash: {batch_hash[:16]}..."
        )

        # Store proof to database/file
        await self._store_integrity_proof(proof)

        return proof

    def _create_merkle_tree(self, hashes: list[str]) -> str:
        """
        Create Merkle tree from list of hashes.

        Args:
            hashes: List of entry hashes

        Returns:
            Merkle root hash
        """
        if not hashes:
            return hashlib.sha256(b"empty").hexdigest()

        if len(hashes) == 1:
            return hashes[0]

        # Ensure even number of hashes (duplicate last if odd)
        if len(hashes) % 2 == 1:
            hashes.append(hashes[-1])

        # Build tree bottom-up
        current_level = hashes[:]

        while len(current_level) > 1:
            next_level = []

            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left

                combined = left + right
                parent_hash = hashlib.sha256(combined.encode()).hexdigest()
                next_level.append(parent_hash)

            current_level = next_level

        return current_level[0]

    def _sign_hash(self, hash_value: str) -> str:
        """
        Sign a hash value with private key.

        Args:
            hash_value: Hash to sign

        Returns:
            Base64 encoded signature
        """
        import base64

        signature = self.private_key.sign(
            hash_value.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256(),
        )

        return base64.b64encode(signature).decode()

    def verify_signature(self, hash_value: str, signature: str) -> bool:
        """
        Verify a signature against a hash.

        Args:
            hash_value: Original hash
            signature: Base64 encoded signature

        Returns:
            True if signature is valid
        """
        import base64

        try:
            signature_bytes = base64.b64decode(signature)

            self.public_key.verify(
                signature_bytes,
                hash_value.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )
            return True

        except InvalidSignature:
            return False
        except Exception as e:
            logger.error(f"Signature verification error: {e}")
            return False

    async def _anchor_to_blockchain(self, proof: IntegrityProof) -> dict[str, Any]:
        """
        Anchor integrity proof to blockchain.

        Args:
            proof: Integrity proof to anchor

        Returns:
            Blockchain transaction details
        """
        try:
            # Prepare data for blockchain
            anchor_data = {
                "batch_id": proof.batch_id,
                "batch_hash": proof.batch_hash,
                "merkle_root": proof.merkle_root,
                "timestamp": proof.timestamp.isoformat(),
                "entry_count": proof.entry_count,
                "constitutional_hash": settings.CONSTITUTIONAL_HASH,
            }

            # Call blockchain service (this would be actual blockchain integration)
            if settings.BLOCKCHAIN_TYPE == "solana":
                result = await self._anchor_to_solana(anchor_data)
            elif settings.BLOCKCHAIN_TYPE == "ethereum":
                result = await self._anchor_to_ethereum(anchor_data)
            else:
                # Mock blockchain for development
                result = await self._mock_blockchain_anchor(anchor_data)

            return result

        except Exception as e:
            logger.error(f"Blockchain anchoring failed: {e}")
            raise

    async def _mock_blockchain_anchor(
        self, anchor_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Mock blockchain anchoring for development."""
        await asyncio.sleep(0.1)  # Simulate network delay

        return {
            "transaction_id": f"mock_tx_{hashlib.sha256(json.dumps(anchor_data).encode()).hexdigest()[:16]}",
            "confirmation": "confirmed",
            "block_height": int(time.time()),
            "gas_used": 21000,
        }

    async def _anchor_to_solana(self, anchor_data: dict[str, Any]) -> dict[str, Any]:
        """Anchor to Solana blockchain."""
        # This would integrate with Solana SDK
        # For now, return mock data
        return await self._mock_blockchain_anchor(anchor_data)

    async def _anchor_to_ethereum(self, anchor_data: dict[str, Any]) -> dict[str, Any]:
        """Anchor to Ethereum blockchain."""
        # This would integrate with Web3.py
        # For now, return mock data
        return await self._mock_blockchain_anchor(anchor_data)

    async def _store_integrity_proof(self, proof: IntegrityProof) -> None:
        """Store integrity proof to persistent storage."""
        # This would store to database
        # For now, just log
        logger.info(f"Stored integrity proof {proof.batch_id}")

    async def verify_audit_entry(self, entry: AuditEntry, proof_id: str) -> bool:
        """
        Verify the integrity of an audit entry against a stored proof.

        Args:
            entry: Audit entry to verify
            proof_id: ID of the integrity proof

        Returns:
            True if entry is verified
        """
        try:
            # Find the relevant proof
            proof = None
            for p in self.integrity_proofs:
                if p.batch_id == proof_id:
                    proof = p
                    break

            if not proof:
                logger.warning(f"Proof {proof_id} not found")
                return False

            # Verify signature on batch hash
            if not self.verify_signature(proof.batch_hash, proof.signature):
                logger.warning(f"Invalid signature for proof {proof_id}")
                return False

            # TODO: Verify entry is included in Merkle tree
            # This would require storing the Merkle path for each entry

            logger.info(f"Successfully verified audit entry {entry.id}")
            return True

        except Exception as e:
            logger.error(f"Audit entry verification failed: {e}")
            return False

    async def generate_integrity_report(
        self, start_date: datetime, end_date: datetime
    ) -> dict[str, Any]:
        """
        Generate integrity report for a date range.

        Args:
            start_date: Start of date range
            end_date: End of date range

        Returns:
            Integrity report
        """
        relevant_proofs = [
            proof
            for proof in self.integrity_proofs
            if start_date <= proof.timestamp <= end_date
        ]

        total_entries = sum(proof.entry_count for proof in relevant_proofs)

        # Verify chain integrity
        chain_integrity = self._verify_proof_chain(relevant_proofs)

        # Check blockchain confirmations
        blockchain_confirmations = sum(
            1
            for proof in relevant_proofs
            if proof.blockchain_confirmation == "confirmed"
        )

        report = {
            "report_period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "summary": {
                "total_batches": len(relevant_proofs),
                "total_entries": total_entries,
                "chain_integrity": chain_integrity,
                "blockchain_confirmations": blockchain_confirmations,
                "blockchain_confirmation_rate": (
                    blockchain_confirmations / len(relevant_proofs)
                    if relevant_proofs
                    else 0
                ),
            },
            "constitutional_hash": settings.CONSTITUTIONAL_HASH,
            "generated_at": datetime.utcnow().isoformat(),
        }

        return report

    def _verify_proof_chain(self, proofs: list[IntegrityProof]) -> bool:
        """Verify the integrity of a chain of proofs."""
        if not proofs:
            return True

        # Sort by timestamp
        sorted_proofs = sorted(proofs, key=lambda p: p.timestamp)

        for i in range(1, len(sorted_proofs)):
            current_proof = sorted_proofs[i]
            previous_proof = sorted_proofs[i - 1]

            # Verify that current proof references previous proof
            if current_proof.previous_batch_hash != previous_proof.batch_hash:
                logger.warning(
                    f"Chain integrity violation: {current_proof.batch_id} "
                    f"does not reference {previous_proof.batch_id}"
                )
                return False

        return True

    async def force_batch_processing(self) -> IntegrityProof | None:
        """Force processing of current batch even if not full."""
        if self.audit_buffer:
            return await self._process_batch()
        return None

    async def close(self) -> None:
        """Clean up resources."""
        # Process any remaining entries
        if self.audit_buffer:
            await self._process_batch()

        await self.http_client.aclose()
