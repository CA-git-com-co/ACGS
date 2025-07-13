"""
Persistent Audit Trail with Cryptographic Hash Chaining for ACGS Integrity Service.
Constitutional Hash: cdd01ef066bc6cf2
"""

import hashlib
import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


class AuditEventType(str, Enum):
    """Types of audit events."""

    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    SYSTEM_EVENT = "system_event"
    SECURITY_EVENT = "security_event"
    COMPLIANCE_CHECK = "compliance_check"
    ERROR = "error"


class AuditSeverity(str, Enum):
    """Severity levels for audit events."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AuditEvent:
    """Represents a single audit event."""

    def __init__(
        self,
        event_type: AuditEventType,
        service_name: str,
        action: str,
        user_id: str | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
        details: dict[str, Any] | None = None,
        severity: AuditSeverity = AuditSeverity.MEDIUM,
        correlation_id: str | None = None,
    ):
        self.event_id = str(uuid.uuid4())
        self.event_type = event_type
        self.service_name = service_name
        self.action = action
        self.user_id = user_id
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.details = details or {}
        self.severity = severity
        self.correlation_id = correlation_id
        self.timestamp = datetime.now(timezone.utc)
        self.constitutional_hash = CONSTITUTIONAL_HASH

    def to_dict(self) -> dict[str, Any]:
        """Convert audit event to dictionary."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "service_name": self.service_name,
            "action": self.action,
            "user_id": self.user_id,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "details": self.details,
            "severity": self.severity.value,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp.isoformat(),
            "constitutional_hash": self.constitutional_hash,
        }

    def get_hash_content(self) -> str:
        """Get content for hash calculation."""
        content_parts = [
            self.event_id,
            self.event_type.value,
            self.service_name,
            self.action,
            str(self.user_id or ""),
            str(self.resource_type or ""),
            str(self.resource_id or ""),
            str(self.details),
            self.severity.value,
            str(self.correlation_id or ""),
            self.timestamp.isoformat(),
            self.constitutional_hash,
        ]
        return "|".join(content_parts)


class CryptographicAuditChain:
    """Cryptographic audit chain with hash chaining for integrity."""

    def __init__(self):
        self.chain: list[dict[str, Any]] = []
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.genesis_hash = self._calculate_genesis_hash()

    def _calculate_genesis_hash(self) -> str:
        """Calculate genesis hash for the chain."""
        genesis_content = f"ACGS_AUDIT_CHAIN_GENESIS:{self.constitutional_hash}:{datetime.now(timezone.utc).isoformat()}"
        return hashlib.sha256(genesis_content.encode("utf-8")).hexdigest()

    def _calculate_event_hash(self, event: AuditEvent, previous_hash: str) -> str:
        """Calculate hash for an audit event."""
        event_content = event.get_hash_content()
        combined_content = f"{previous_hash}:{event_content}"
        return hashlib.sha256(combined_content.encode("utf-8")).hexdigest()

    async def add_event(self, event: AuditEvent) -> dict[str, Any]:
        """Add an event to the audit chain."""
        try:
            # Get previous hash
            if not self.chain:
                previous_hash = self.genesis_hash
                chain_position = 0
            else:
                previous_hash = self.chain[-1]["event_hash"]
                chain_position = len(self.chain)

            # Calculate event hash
            event_hash = self._calculate_event_hash(event, previous_hash)

            # Create chain entry
            chain_entry = {
                "chain_position": chain_position,
                "event": event.to_dict(),
                "previous_hash": previous_hash,
                "event_hash": event_hash,
                "added_at": datetime.now(timezone.utc).isoformat(),
                "constitutional_hash": self.constitutional_hash,
            }

            # Add to chain
            self.chain.append(chain_entry)

            logger.info(
                f"Added audit event {event.event_id} to chain at position {chain_position}"
            )

            return {
                "event_id": event.event_id,
                "chain_position": chain_position,
                "event_hash": event_hash,
                "constitutional_hash": self.constitutional_hash,
            }

        except Exception as e:
            logger.exception(f"Failed to add event to audit chain: {e}")
            raise

    async def verify_chain_integrity(self) -> dict[str, Any]:
        """Verify the integrity of the entire audit chain."""
        try:
            if not self.chain:
                return {
                    "is_valid": True,
                    "chain_length": 0,
                    "verified_at": datetime.now(timezone.utc).isoformat(),
                    "constitutional_hash": self.constitutional_hash,
                }

            violations = []

            for i, entry in enumerate(self.chain):
                # Verify previous hash
                if i == 0:
                    expected_previous = self.genesis_hash
                else:
                    expected_previous = self.chain[i - 1]["event_hash"]

                if entry["previous_hash"] != expected_previous:
                    violations.append(f"Position {i}: Previous hash mismatch")

                # Verify event hash
                event_data = entry["event"]
                event = AuditEvent(
                    event_type=AuditEventType(event_data["event_type"]),
                    service_name=event_data["service_name"],
                    action=event_data["action"],
                    user_id=event_data["user_id"],
                    resource_type=event_data["resource_type"],
                    resource_id=event_data["resource_id"],
                    details=event_data["details"],
                    severity=AuditSeverity(event_data["severity"]),
                    correlation_id=event_data["correlation_id"],
                )
                event.event_id = event_data["event_id"]
                event.timestamp = datetime.fromisoformat(
                    event_data["timestamp"].replace("Z", "+00:00")
                )

                expected_hash = self._calculate_event_hash(
                    event, entry["previous_hash"]
                )
                if entry["event_hash"] != expected_hash:
                    violations.append(f"Position {i}: Event hash mismatch")

            is_valid = len(violations) == 0

            return {
                "is_valid": is_valid,
                "chain_length": len(self.chain),
                "violations": violations,
                "verified_at": datetime.now(timezone.utc).isoformat(),
                "constitutional_hash": self.constitutional_hash,
            }

        except Exception as e:
            logger.exception(f"Chain integrity verification failed: {e}")
            raise

    async def get_chain_stats(self) -> dict[str, Any]:
        """Get statistics about the audit chain."""
        try:
            if not self.chain:
                return {
                    "chain_length": 0,
                    "genesis_hash": self.genesis_hash,
                    "constitutional_hash": self.constitutional_hash,
                }

            # Count events by type
            event_types = {}
            severities = {}
            services = {}

            for entry in self.chain:
                event = entry["event"]

                event_type = event["event_type"]
                event_types[event_type] = event_types.get(event_type, 0) + 1

                severity = event["severity"]
                severities[severity] = severities.get(severity, 0) + 1

                service = event["service_name"]
                services[service] = services.get(service, 0) + 1

            first_event = self.chain[0]["event"]["timestamp"]
            last_event = self.chain[-1]["event"]["timestamp"]

            return {
                "chain_length": len(self.chain),
                "genesis_hash": self.genesis_hash,
                "latest_hash": self.chain[-1]["event_hash"],
                "first_event_timestamp": first_event,
                "last_event_timestamp": last_event,
                "event_type_distribution": event_types,
                "severity_distribution": severities,
                "service_distribution": services,
                "constitutional_hash": self.constitutional_hash,
            }

        except Exception as e:
            logger.exception(f"Chain statistics retrieval failed: {e}")
            raise


# Global audit chain instance
_global_audit_chain = CryptographicAuditChain()


async def log_audit_event(
    event_type: AuditEventType,
    service_name: str,
    action: str,
    user_id: str | None = None,
    resource_type: str | None = None,
    resource_id: str | None = None,
    details: dict[str, Any] | None = None,
    severity: AuditSeverity = AuditSeverity.MEDIUM,
    correlation_id: str | None = None,
) -> dict[str, Any]:
    """Log an audit event to the global audit chain."""
    try:
        event = AuditEvent(
            event_type=event_type,
            service_name=service_name,
            action=action,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            severity=severity,
            correlation_id=correlation_id,
        )

        result = await _global_audit_chain.add_event(event)

        return {
            "success": True,
            "event_id": result["event_id"],
            "chain_position": result["chain_position"],
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

    except Exception as e:
        logger.exception(f"Audit event logging failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }


async def get_audit_chain() -> CryptographicAuditChain:
    """Get the global audit chain instance."""
    return _global_audit_chain
