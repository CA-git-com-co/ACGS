"""
Persistent Audit Trail with Cryptographic Hash Chaining

This module implements a production-grade persistent audit trail system
that maintains cryptographic integrity through hash chaining and provides
tamper-evident storage for all ACGS governance operations.

Constitutional Hash: cdd01ef066bc6cf2
"""

import hashlib
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

import asyncpg
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


class AuditEventType(str, Enum):
    """Types of audit events."""

    POLICY_CREATION = "policy_creation"
    POLICY_MODIFICATION = "policy_modification"
    POLICY_DELETION = "policy_deletion"
    AGENT_EVOLUTION = "agent_evolution"
    CONSTITUTIONAL_VALIDATION = "constitutional_validation"
    ACCESS_CONTROL = "access_control"
    CRYPTOGRAPHIC_OPERATION = "cryptographic_operation"
    SYSTEM_CONFIGURATION = "system_configuration"
    USER_AUTHENTICATION = "user_authentication"
    GOVERNANCE_DECISION = "governance_decision"
    ROLLBACK_OPERATION = "rollback_operation"
    EMERGENCY_ACTION = "emergency_action"


class AuditSeverity(str, Enum):
    """Severity levels for audit events."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AuditEvent:
    """Represents an audit event with full metadata."""

    event_type: AuditEventType
    service_name: str
    action: str
    resource_type: str
    description: str
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    resource_id: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    severity: AuditSeverity = AuditSeverity.MEDIUM
    constitutional_hash: str = CONSTITUTIONAL_HASH
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_id: Optional[str] = None


@dataclass
class AuditBlock:
    """Represents a block in the audit trail chain."""

    block_id: str
    block_number: int
    timestamp: datetime
    events: list[AuditEvent]
    previous_hash: str
    merkle_root: str
    block_hash: str
    signature: str
    constitutional_hash: str = CONSTITUTIONAL_HASH


@dataclass
class IntegrityVerificationResult:
    """Result of audit trail integrity verification."""

    is_valid: bool
    total_blocks: int
    verified_blocks: int
    broken_chains: list[tuple[int, str]]  # (block_number, reason)
    tampered_events: list[tuple[str, str]]  # (event_id, reason)
    verification_time_ms: float
    constitutional_compliance: bool


class CryptographicAuditChain:
    """
    Cryptographic audit chain implementation with persistent storage.

    Provides tamper-evident audit trail with:
    - Hash chaining between blocks
    - Merkle tree verification for events within blocks
    - Digital signatures for block integrity
    - Constitutional compliance verification
    """

    def __init__(self, db_pool: asyncpg.Pool):
        """
        Initialize the cryptographic audit chain.

        Args:
            db_pool: Database connection pool
        """
        self.db_pool = db_pool
        self.signing_key = None
        self.verification_key = None
        self._initialize_cryptographic_keys()

        logger.info(
            f"Cryptographic Audit Chain initialized with hash: {CONSTITUTIONAL_HASH}"
        )

    def _initialize_cryptographic_keys(self):
        """Initialize RSA key pair for signing audit blocks."""
        try:
            # Generate RSA key pair for audit trail signing
            self.signing_key = rsa.generate_private_key(
                public_exponent=65537, key_size=2048
            )
            self.verification_key = self.signing_key.public_key()

            logger.info("Cryptographic keys initialized for audit trail signing")

        except Exception as e:
            logger.error(f"Failed to initialize cryptographic keys: {e}")
            raise

    async def append_event(self, event: AuditEvent) -> str:
        """
        Append an audit event to the persistent trail.

        Args:
            event: Audit event to append

        Returns:
            Block ID where the event was stored
        """
        try:
            # Store individual event first
            await self._store_audit_event(event)

            # Check if we need to create a new block
            current_block = await self._get_current_block()

            if current_block is None or await self._should_create_new_block(
                current_block
            ):
                # Create new block with pending events
                block = await self._create_new_block()
            else:
                # Update existing block
                block = await self._add_event_to_block(current_block, event)

            logger.debug(
                f"Audit event {event.event_id} appended to block {block.block_id}"
            )
            return block.block_id

        except Exception as e:
            logger.error(f"Failed to append audit event: {e}")
            raise

    async def _store_audit_event(self, event: AuditEvent):
        """Store individual audit event in database."""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO audit_events (
                        event_id, event_type, timestamp, service_name, user_id, session_id,
                        action, resource_type, resource_id, description, metadata, severity,
                        constitutional_hash, ip_address, user_agent, request_id
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
                """,
                    event.event_id,
                    event.event_type.value,
                    event.timestamp,
                    event.service_name,
                    event.user_id,
                    event.session_id,
                    event.action,
                    event.resource_type,
                    event.resource_id,
                    event.description,
                    json.dumps(event.metadata),
                    event.severity.value,
                    event.constitutional_hash,
                    event.ip_address,
                    event.user_agent,
                    event.request_id,
                )

        except Exception as e:
            logger.error(f"Failed to store audit event: {e}")
            raise

    async def _get_current_block(self) -> Optional[AuditBlock]:
        """Get the current active audit block."""
        try:
            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT * FROM audit_blocks
                    WHERE finalized = FALSE
                    ORDER BY block_number DESC
                    LIMIT 1
                """)

                if row:
                    return await self._row_to_audit_block(row)
                return None

        except Exception as e:
            logger.error(f"Failed to get current block: {e}")
            return None

    async def _should_create_new_block(self, current_block: AuditBlock) -> bool:
        """Determine if a new block should be created."""
        try:
            # Create new block if:
            # 1. Current block has too many events (>100)
            # 2. Current block is too old (>1 hour)
            # 3. Critical event requires immediate sealing

            if len(current_block.events) >= 100:
                return True

            block_age = datetime.now(timezone.utc) - current_block.timestamp
            if block_age.total_seconds() > 3600:  # 1 hour
                return True

            return False

        except Exception as e:
            logger.warning(f"Error checking block creation criteria: {e}")
            return True  # Conservative approach

    async def _create_new_block(self) -> AuditBlock:
        """Create a new audit block with pending events."""
        try:
            # Get pending events
            pending_events = await self._get_pending_events()

            # Get previous block hash
            previous_hash = await self._get_last_block_hash()

            # Create block
            block_number = await self._get_next_block_number()
            block_id = str(uuid.uuid4())
            timestamp = datetime.now(timezone.utc)

            # Calculate Merkle root
            merkle_root = self._calculate_merkle_root(pending_events)

            # Calculate block hash
            block_data = {
                "block_id": block_id,
                "block_number": block_number,
                "timestamp": timestamp.isoformat(),
                "previous_hash": previous_hash,
                "merkle_root": merkle_root,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "event_count": len(pending_events),
            }
            block_hash = hashlib.sha256(
                json.dumps(block_data, sort_keys=True).encode()
            ).hexdigest()

            # Sign block
            signature = self._sign_block(block_hash)

            # Create block object
            block = AuditBlock(
                block_id=block_id,
                block_number=block_number,
                timestamp=timestamp,
                events=pending_events,
                previous_hash=previous_hash,
                merkle_root=merkle_root,
                block_hash=block_hash,
                signature=signature,
                constitutional_hash=CONSTITUTIONAL_HASH,
            )

            # Store block in database
            await self._store_audit_block(block)

            # Mark events as included in block
            await self._mark_events_included(
                [e.event_id for e in pending_events], block_id
            )

            logger.info(
                f"Created new audit block {block_id} with {len(pending_events)} events"
            )
            return block

        except Exception as e:
            logger.error(f"Failed to create new audit block: {e}")
            raise

    async def _get_pending_events(self) -> list[AuditEvent]:
        """Get events not yet included in a finalized block."""
        try:
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT * FROM audit_events
                    WHERE block_id IS NULL
                    ORDER BY timestamp ASC
                    LIMIT 100
                """)

                events = []
                for row in rows:
                    event = AuditEvent(
                        event_id=row["event_id"],
                        event_type=AuditEventType(row["event_type"]),
                        timestamp=row["timestamp"],
                        service_name=row["service_name"],
                        user_id=row["user_id"],
                        session_id=row["session_id"],
                        action=row["action"],
                        resource_type=row["resource_type"],
                        resource_id=row["resource_id"],
                        description=row["description"],
                        metadata=json.loads(row["metadata"]) if row["metadata"] else {},
                        severity=AuditSeverity(row["severity"]),
                        constitutional_hash=row["constitutional_hash"],
                        ip_address=row["ip_address"],
                        user_agent=row["user_agent"],
                        request_id=row["request_id"],
                    )
                    events.append(event)

                return events

        except Exception as e:
            logger.error(f"Failed to get pending events: {e}")
            return []

    async def _get_last_block_hash(self) -> str:
        """Get hash of the last finalized block."""
        try:
            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT block_hash FROM audit_blocks
                    WHERE finalized = TRUE
                    ORDER BY block_number DESC
                    LIMIT 1
                """)

                if row:
                    return row["block_hash"]
                else:
                    # Genesis block hash
                    return hashlib.sha256(
                        f"genesis_block:{CONSTITUTIONAL_HASH}".encode()
                    ).hexdigest()

        except Exception as e:
            logger.error(f"Failed to get last block hash: {e}")
            return "0000000000000000000000000000000000000000000000000000000000000000"

    async def _get_next_block_number(self) -> int:
        """Get the next block number in sequence."""
        try:
            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT MAX(block_number) as max_number FROM audit_blocks
                """)

                if row and row["max_number"] is not None:
                    return row["max_number"] + 1
                else:
                    return 1  # First block

        except Exception as e:
            logger.error(f"Failed to get next block number: {e}")
            return 1

    def _calculate_merkle_root(self, events: list[AuditEvent]) -> str:
        """Calculate Merkle root hash for events in block."""
        try:
            if not events:
                return hashlib.sha256(b"empty_block").hexdigest()

            # Calculate hash for each event
            event_hashes = []
            for event in events:
                event_data = {
                    "event_id": event.event_id,
                    "event_type": event.event_type.value,
                    "timestamp": event.timestamp.isoformat(),
                    "action": event.action,
                    "resource_type": event.resource_type,
                    "constitutional_hash": event.constitutional_hash,
                }
                event_hash = hashlib.sha256(
                    json.dumps(event_data, sort_keys=True).encode()
                ).hexdigest()
                event_hashes.append(event_hash)

            # Build Merkle tree
            while len(event_hashes) > 1:
                next_level = []
                for i in range(0, len(event_hashes), 2):
                    if i + 1 < len(event_hashes):
                        combined = event_hashes[i] + event_hashes[i + 1]
                    else:
                        combined = (
                            event_hashes[i] + event_hashes[i]
                        )  # Duplicate last hash

                    next_hash = hashlib.sha256(combined.encode()).hexdigest()
                    next_level.append(next_hash)

                event_hashes = next_level

            return event_hashes[0]

        except Exception as e:
            logger.error(f"Failed to calculate Merkle root: {e}")
            return hashlib.sha256(b"error_calculating_merkle_root").hexdigest()

    def _sign_block(self, block_hash: str) -> str:
        """Sign block hash with private key."""
        try:
            signature = self.signing_key.sign(
                block_hash.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )

            # Return base64 encoded signature
            import base64

            return base64.b64encode(signature).decode()

        except Exception as e:
            logger.error(f"Failed to sign block: {e}")
            return "signature_error"

    async def _store_audit_block(self, block: AuditBlock):
        """Store audit block in database."""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO audit_blocks (
                        block_id, block_number, timestamp, previous_hash, merkle_root,
                        block_hash, signature, constitutional_hash, event_count, finalized
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """,
                    block.block_id,
                    block.block_number,
                    block.timestamp,
                    block.previous_hash,
                    block.merkle_root,
                    block.block_hash,
                    block.signature,
                    block.constitutional_hash,
                    len(block.events),
                    True,
                )  # Mark as finalized immediately

        except Exception as e:
            logger.error(f"Failed to store audit block: {e}")
            raise

    async def _mark_events_included(self, event_ids: list[str], block_id: str):
        """Mark events as included in a specific block."""
        try:
            async with self.db_pool.acquire() as conn:
                for event_id in event_ids:
                    await conn.execute(
                        """
                        UPDATE audit_events SET block_id = $1 WHERE event_id = $2
                    """,
                        block_id,
                        event_id,
                    )

        except Exception as e:
            logger.error(f"Failed to mark events as included: {e}")
            raise

    async def _add_event_to_block(
        self, current_block: AuditBlock, event: AuditEvent
    ) -> AuditBlock:
        """Add event to existing unfinalised block (placeholder implementation)."""
        # For now, we finalize blocks immediately, so this is not used
        # In a full implementation, this would update an unfinalised block
        return current_block

    async def verify_integrity(
        self, start_block: int = 1, end_block: Optional[int] = None
    ) -> IntegrityVerificationResult:
        """
        Verify integrity of the audit trail chain.

        Args:
            start_block: Starting block number for verification
            end_block: Ending block number (None for latest)

        Returns:
            IntegrityVerificationResult with verification details
        """
        start_time = time.time()

        try:
            logger.info(
                f"Starting audit trail integrity verification from block {start_block}"
            )

            # Get blocks to verify
            blocks = await self._get_blocks_for_verification(start_block, end_block)

            total_blocks = len(blocks)
            verified_blocks = 0
            broken_chains = []
            tampered_events = []

            previous_hash = None
            if start_block > 1:
                previous_hash = await self._get_block_hash(start_block - 1)

            for block_data in blocks:
                block_valid = True

                # Verify block hash chain
                if (
                    previous_hash is not None
                    and block_data["previous_hash"] != previous_hash
                ):
                    broken_chains.append(
                        (block_data["block_number"], "Hash chain broken")
                    )
                    block_valid = False

                # Verify block signature
                if not await self._verify_block_signature(block_data):
                    broken_chains.append(
                        (block_data["block_number"], "Invalid signature")
                    )
                    block_valid = False

                # Verify Merkle root
                block_events = await self._get_block_events(block_data["block_id"])
                calculated_merkle = self._calculate_merkle_root(block_events)
                if calculated_merkle != block_data["merkle_root"]:
                    broken_chains.append(
                        (block_data["block_number"], "Merkle root mismatch")
                    )
                    block_valid = False

                # Verify constitutional compliance
                if block_data["constitutional_hash"] != CONSTITUTIONAL_HASH:
                    broken_chains.append(
                        (block_data["block_number"], "Constitutional hash mismatch")
                    )
                    block_valid = False

                if block_valid:
                    verified_blocks += 1

                previous_hash = block_data["block_hash"]

            verification_time = (time.time() - start_time) * 1000

            result = IntegrityVerificationResult(
                is_valid=len(broken_chains) == 0 and len(tampered_events) == 0,
                total_blocks=total_blocks,
                verified_blocks=verified_blocks,
                broken_chains=broken_chains,
                tampered_events=tampered_events,
                verification_time_ms=verification_time,
                constitutional_compliance=all(
                    b["constitutional_hash"] == CONSTITUTIONAL_HASH for b in blocks
                ),
            )

            logger.info(
                "Integrity verification completed:"
                f" {verified_blocks}/{total_blocks} blocks verified in"
                f" {verification_time:.2f}ms"
            )
            return result

        except Exception as e:
            logger.error(f"Integrity verification failed: {e}")
            verification_time = (time.time() - start_time) * 1000
            return IntegrityVerificationResult(
                is_valid=False,
                total_blocks=0,
                verified_blocks=0,
                broken_chains=[(0, f"Verification error: {e!s}")],
                tampered_events=[],
                verification_time_ms=verification_time,
                constitutional_compliance=False,
            )

    async def _get_blocks_for_verification(
        self, start_block: int, end_block: Optional[int]
    ) -> list[dict[str, Any]]:
        """Get blocks for integrity verification."""
        try:
            async with self.db_pool.acquire() as conn:
                if end_block is not None:
                    rows = await conn.fetch(
                        """
                        SELECT * FROM audit_blocks
                        WHERE block_number >= $1 AND block_number <= $2
                        ORDER BY block_number ASC
                    """,
                        start_block,
                        end_block,
                    )
                else:
                    rows = await conn.fetch(
                        """
                        SELECT * FROM audit_blocks
                        WHERE block_number >= $1
                        ORDER BY block_number ASC
                    """,
                        start_block,
                    )

                return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Failed to get blocks for verification: {e}")
            return []

    async def _get_block_hash(self, block_number: int) -> Optional[str]:
        """Get hash of specific block."""
        try:
            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow(
                    """
                    SELECT block_hash FROM audit_blocks WHERE block_number = $1
                """,
                    block_number,
                )

                return row["block_hash"] if row else None

        except Exception as e:
            logger.error(f"Failed to get block hash: {e}")
            return None

    async def _verify_block_signature(self, block_data: dict[str, Any]) -> bool:
        """Verify digital signature of block."""
        try:
            import base64

            signature = base64.b64decode(block_data["signature"])
            block_hash = block_data["block_hash"]

            self.verification_key.verify(
                signature,
                block_hash.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )

            return True

        except Exception as e:
            logger.warning(f"Block signature verification failed: {e}")
            return False

    async def _get_block_events(self, block_id: str) -> list[AuditEvent]:
        """Get all events in a specific block."""
        try:
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch(
                    """
                    SELECT * FROM audit_events WHERE block_id = $1 ORDER BY timestamp ASC
                """,
                    block_id,
                )

                events = []
                for row in rows:
                    event = AuditEvent(
                        event_id=row["event_id"],
                        event_type=AuditEventType(row["event_type"]),
                        timestamp=row["timestamp"],
                        service_name=row["service_name"],
                        user_id=row["user_id"],
                        session_id=row["session_id"],
                        action=row["action"],
                        resource_type=row["resource_type"],
                        resource_id=row["resource_id"],
                        description=row["description"],
                        metadata=json.loads(row["metadata"]) if row["metadata"] else {},
                        severity=AuditSeverity(row["severity"]),
                        constitutional_hash=row["constitutional_hash"],
                        ip_address=row["ip_address"],
                        user_agent=row["user_agent"],
                        request_id=row["request_id"],
                    )
                    events.append(event)

                return events

        except Exception as e:
            logger.error(f"Failed to get block events: {e}")
            return []

    async def _row_to_audit_block(self, row) -> AuditBlock:
        """Convert database row to AuditBlock object."""
        try:
            events = await self._get_block_events(row["block_id"])

            return AuditBlock(
                block_id=row["block_id"],
                block_number=row["block_number"],
                timestamp=row["timestamp"],
                events=events,
                previous_hash=row["previous_hash"],
                merkle_root=row["merkle_root"],
                block_hash=row["block_hash"],
                signature=row["signature"],
                constitutional_hash=row["constitutional_hash"],
            )

        except Exception as e:
            logger.error(f"Failed to convert row to audit block: {e}")
            raise

    async def get_audit_trail_stats(self) -> dict[str, Any]:
        """Get statistics about the audit trail."""
        try:
            async with self.db_pool.acquire() as conn:
                # Block statistics
                block_stats = await conn.fetchrow("""
                    SELECT
                        COUNT(*) as total_blocks,
                        MIN(block_number) as first_block,
                        MAX(block_number) as latest_block,
                        SUM(event_count) as total_events
                    FROM audit_blocks
                """)

                # Event statistics by type
                event_type_stats = await conn.fetch("""
                    SELECT event_type, COUNT(*) as count
                    FROM audit_events
                    GROUP BY event_type
                    ORDER BY count DESC
                """)

                # Recent activity
                recent_events = await conn.fetchval("""
                    SELECT COUNT(*) FROM audit_events
                    WHERE timestamp > NOW() - INTERVAL '24 hours'
                """)

                return {
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                    "blocks": {
                        "total": block_stats["total_blocks"] or 0,
                        "first_block": block_stats["first_block"] or 0,
                        "latest_block": block_stats["latest_block"] or 0,
                    },
                    "events": {
                        "total": block_stats["total_events"] or 0,
                        "recent_24h": recent_events or 0,
                        "by_type": {
                            row["event_type"]: row["count"] for row in event_type_stats
                        },
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }

        except Exception as e:
            logger.error(f"Failed to get audit trail stats: {e}")
            return {
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }


# Helper functions for easy integration
async def create_audit_tables(db_pool: asyncpg.Pool):
    """Create database tables for persistent audit trail."""
    try:
        async with db_pool.acquire() as conn:
            # Audit events table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_events (
                    event_id UUID PRIMARY KEY,
                    event_type VARCHAR(50) NOT NULL,
                    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    service_name VARCHAR(100) NOT NULL,
                    user_id VARCHAR(255),
                    session_id VARCHAR(255),
                    action VARCHAR(255) NOT NULL,
                    resource_type VARCHAR(100) NOT NULL,
                    resource_id VARCHAR(255),
                    description TEXT NOT NULL,
                    metadata JSONB DEFAULT '{}',
                    severity VARCHAR(20) DEFAULT 'medium',
                    constitutional_hash VARCHAR(64) NOT NULL,
                    ip_address INET,
                    user_agent TEXT,
                    request_id VARCHAR(255),
                    block_id UUID REFERENCES audit_blocks(block_id),
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
            """)

            # Audit blocks table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_blocks (
                    block_id UUID PRIMARY KEY,
                    block_number INTEGER UNIQUE NOT NULL,
                    timestamp TIMESTAMPTZ NOT NULL,
                    previous_hash VARCHAR(64) NOT NULL,
                    merkle_root VARCHAR(64) NOT NULL,
                    block_hash VARCHAR(64) UNIQUE NOT NULL,
                    signature TEXT NOT NULL,
                    constitutional_hash VARCHAR(64) NOT NULL,
                    event_count INTEGER DEFAULT 0,
                    finalized BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
            """)

            # Create indexes for performance
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_audit_events_timestamp ON"
                " audit_events(timestamp);"
            )
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_audit_events_service ON"
                " audit_events(service_name);"
            )
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_audit_events_type ON"
                " audit_events(event_type);"
            )
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_audit_events_user ON"
                " audit_events(user_id);"
            )
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_audit_events_block ON"
                " audit_events(block_id);"
            )
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_audit_blocks_number ON"
                " audit_blocks(block_number);"
            )
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_audit_blocks_hash ON"
                " audit_blocks(block_hash);"
            )
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_audit_blocks_finalized ON"
                " audit_blocks(finalized);"
            )

        logger.info("Audit trail database tables created successfully")

    except Exception as e:
        logger.error(f"Failed to create audit trail tables: {e}")
        raise


async def log_audit_event(
    audit_chain: CryptographicAuditChain,
    event_type: AuditEventType,
    service_name: str,
    action: str,
    resource_type: str,
    description: str,
    user_id: Optional[str] = None,
    resource_id: Optional[str] = None,
    metadata: Optional[dict[str, Any]] = None,
    severity: AuditSeverity = AuditSeverity.MEDIUM,
    session_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    request_id: Optional[str] = None,
) -> str:
    """
    Convenience function to log an audit event.

    Returns:
        Event ID of the created audit event
    """
    event = AuditEvent(
        event_type=event_type,
        service_name=service_name,
        user_id=user_id,
        session_id=session_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        description=description,
        metadata=metadata or {},
        severity=severity,
        ip_address=ip_address,
        user_agent=user_agent,
        request_id=request_id,
    )

    await audit_chain.append_event(event)
    return event.event_id
