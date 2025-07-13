"""
Audit & Integrity Domain Entities
Constitutional Hash: cdd01ef066bc6cf2

Core entities for audit trail management and system integrity verification.
"""

import hashlib
import json
from datetime import datetime
from typing import Any

from services.shared.domain.base import (
    Entity,
    EntityId,
    MultiTenantAggregateRoot,
    TenantId,
)

from .events import (
    AuditEntryCreatedEvent,
    AuditTrailArchivedEvent,
    HashChainVerifiedEvent,
    IntegrityViolationDetectedEvent,
)
from .value_objects import (
    AuditCategory,
    AuditContext,
    AuditLevel,
    HashChain,
    IntegrityCheckResult,
)


class AuditEntry(Entity):
    """
    Entity representing a single audit log entry.

    Immutable record of system activities for compliance and forensic analysis.
    """

    def __init__(
        self,
        entry_id: EntityId,
        tenant_id: TenantId,
        event_type: str,
        event_source: str,
        event_data: dict[str, Any],
        context: AuditContext,
        level: AuditLevel,
        category: AuditCategory,
    ):
        super().__init__(entry_id)
        self.tenant_id = tenant_id
        self.event_type = event_type
        self.event_source = event_source
        self.event_data = event_data.copy()
        self.context = context
        self.level = level
        self.category = category
        self.timestamp = datetime.utcnow()
        self._hash = self._calculate_hash()
        self._immutable = True

    @property
    def hash(self) -> str:
        """Get cryptographic hash of the audit entry."""
        return self._hash

    @property
    def is_immutable(self) -> bool:
        """Check if entry is immutable."""
        return self._immutable

    def _calculate_hash(self) -> str:
        """Calculate SHA-256 hash of the audit entry."""
        data = {
            "entry_id": str(self.id),
            "tenant_id": str(self.tenant_id),
            "event_type": self.event_type,
            "event_source": self.event_source,
            "event_data": self.event_data,
            "context": self.context.to_dict(),
            "level": self.level.value,
            "category": self.category.value,
            "timestamp": self.timestamp.isoformat(),
        }

        # Sort keys for consistent hashing
        canonical_data = json.dumps(data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical_data.encode("utf-8")).hexdigest()

    def verify_integrity(self) -> bool:
        """Verify entry integrity by recalculating hash."""
        return self._hash == self._calculate_hash()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "entry_id": str(self.id),
            "tenant_id": str(self.tenant_id),
            "event_type": self.event_type,
            "event_source": self.event_source,
            "event_data": self.event_data,
            "context": self.context.to_dict(),
            "level": self.level.value,
            "category": self.category.value,
            "timestamp": self.timestamp.isoformat(),
            "hash": self._hash,
        }


class AuditTrail(MultiTenantAggregateRoot):
    """
    Aggregate root representing an audit trail for a specific context.

    Manages a sequence of audit entries with cryptographic integrity verification.
    """

    def __init__(
        self,
        trail_id: EntityId,
        tenant_id: TenantId,
        trail_name: str,
        description: str,
        category: AuditCategory,
    ):
        super().__init__(trail_id, tenant_id)
        self.trail_name = trail_name
        self.description = description
        self.category = category
        self._entries: list[AuditEntry] = []
        self._hash_chain = HashChain()
        self.created_at = datetime.utcnow()
        self.last_updated = datetime.utcnow()
        self._sealed = False
        self._archive_date: datetime | None = None

    @property
    def entries(self) -> list[AuditEntry]:
        """Get audit entries (read-only)."""
        return self._entries.copy()

    @property
    def entry_count(self) -> int:
        """Get number of audit entries."""
        return len(self._entries)

    @property
    def hash_chain(self) -> HashChain:
        """Get current hash chain."""
        return self._hash_chain

    @property
    def is_sealed(self) -> bool:
        """Check if trail is sealed (immutable)."""
        return self._sealed

    @property
    def archive_date(self) -> datetime | None:
        """Get archive date if archived."""
        return self._archive_date

    def add_entry(
        self,
        event_type: str,
        event_source: str,
        event_data: dict[str, Any],
        context: AuditContext,
        level: AuditLevel = AuditLevel.INFO,
    ) -> EntityId:
        """Add new audit entry to the trail."""
        if self._sealed:
            raise ValueError("Cannot add entries to sealed audit trail")

        # Create new audit entry
        entry = AuditEntry(
            entry_id=EntityId(),
            tenant_id=self.tenant_id,
            event_type=event_type,
            event_source=event_source,
            event_data=event_data,
            context=context,
            level=level,
            category=self.category,
        )

        # Add to trail
        self._entries.append(entry)

        # Update hash chain
        self._hash_chain = self._hash_chain.add_hash(entry.hash)

        # Update timestamps
        self.last_updated = datetime.utcnow()

        # Raise domain event
        self._add_domain_event(
            AuditEntryCreatedEvent(
                aggregate_id=self.id,
                trail_id=self.id,
                entry_id=entry.id,
                event_type=event_type,
                level=level.value,
                hash=entry.hash,
                occurred_at=datetime.utcnow(),
            )
        )

        return entry.id

    def verify_integrity(self) -> IntegrityCheckResult:
        """Verify integrity of the entire audit trail."""
        errors = []
        warnings = []

        # Verify each entry
        for i, entry in enumerate(self._entries):
            if not entry.verify_integrity():
                errors.append(f"Entry {i + 1} (ID: {entry.id}) has invalid hash")

        # Verify hash chain
        if not self._verify_hash_chain():
            errors.append("Hash chain verification failed")

        # Check for gaps in timestamps
        timestamp_gaps = self._check_timestamp_gaps()
        if timestamp_gaps:
            warnings.extend(timestamp_gaps)

        is_valid = len(errors) == 0

        result = IntegrityCheckResult(
            trail_id=self.id,
            is_valid=is_valid,
            entry_count=len(self._entries),
            verified_entries=len(self._entries)
            - len([e for e in errors if "has invalid hash" in e]),
            errors=errors,
            warnings=warnings,
            check_timestamp=datetime.utcnow(),
        )

        # Raise integrity event
        if not is_valid:
            self._add_domain_event(
                IntegrityViolationDetectedEvent(
                    aggregate_id=self.id,
                    trail_id=self.id,
                    violation_type="integrity_check_failed",
                    details=errors,
                    occurred_at=datetime.utcnow(),
                )
            )
        else:
            self._add_domain_event(
                HashChainVerifiedEvent(
                    aggregate_id=self.id,
                    trail_id=self.id,
                    chain_length=len(self._entries),
                    final_hash=self._hash_chain.current_hash,
                    occurred_at=datetime.utcnow(),
                )
            )

        return result

    def seal_trail(self) -> None:
        """Seal the audit trail to prevent further modifications."""
        if self._sealed:
            raise ValueError("Audit trail is already sealed")

        self._sealed = True
        self.last_updated = datetime.utcnow()

        # Verify integrity before sealing
        integrity_result = self.verify_integrity()
        if not integrity_result.is_valid:
            raise ValueError("Cannot seal audit trail with integrity violations")

    def archive(self) -> None:
        """Archive the audit trail."""
        if not self._sealed:
            raise ValueError("Audit trail must be sealed before archiving")

        self._archive_date = datetime.utcnow()

        self._add_domain_event(
            AuditTrailArchivedEvent(
                aggregate_id=self.id,
                trail_id=self.id,
                entry_count=len(self._entries),
                archive_date=self._archive_date,
                occurred_at=datetime.utcnow(),
            )
        )

    def get_entries_by_level(self, level: AuditLevel) -> list[AuditEntry]:
        """Get entries filtered by audit level."""
        return [entry for entry in self._entries if entry.level == level]

    def get_entries_by_timerange(
        self, start_time: datetime, end_time: datetime
    ) -> list[AuditEntry]:
        """Get entries within specified time range."""
        return [
            entry
            for entry in self._entries
            if start_time <= entry.timestamp <= end_time
        ]

    def get_entries_by_source(self, event_source: str) -> list[AuditEntry]:
        """Get entries from specific event source."""
        return [entry for entry in self._entries if entry.event_source == event_source]

    def search_entries(self, query: dict[str, Any]) -> list[AuditEntry]:
        """Search entries based on query criteria."""
        results = self._entries.copy()

        # Filter by event type
        if "event_type" in query:
            results = [e for e in results if e.event_type == query["event_type"]]

        # Filter by level
        if "level" in query:
            level = AuditLevel(query["level"])
            results = [e for e in results if e.level == level]

        # Filter by source
        if "event_source" in query:
            results = [e for e in results if e.event_source == query["event_source"]]

        # Filter by time range
        if "start_time" in query and "end_time" in query:
            start_time = datetime.fromisoformat(query["start_time"])
            end_time = datetime.fromisoformat(query["end_time"])
            results = [e for e in results if start_time <= e.timestamp <= end_time]

        # Filter by context fields
        if "context" in query:
            context_filters = query["context"]
            for key, value in context_filters.items():
                results = [
                    e
                    for e in results
                    if hasattr(e.context, key) and getattr(e.context, key) == value
                ]

        return results

    def get_trail_statistics(self) -> dict[str, Any]:
        """Get statistics about the audit trail."""
        if not self._entries:
            return {
                "entry_count": 0,
                "level_distribution": {},
                "source_distribution": {},
                "time_span": None,
            }

        # Level distribution
        level_counts = {}
        for entry in self._entries:
            level = entry.level.value
            level_counts[level] = level_counts.get(level, 0) + 1

        # Source distribution
        source_counts = {}
        for entry in self._entries:
            source = entry.event_source
            source_counts[source] = source_counts.get(source, 0) + 1

        # Time span
        timestamps = [entry.timestamp for entry in self._entries]
        time_span = {
            "start": min(timestamps).isoformat(),
            "end": max(timestamps).isoformat(),
            "duration_hours": (max(timestamps) - min(timestamps)).total_seconds()
            / 3600,
        }

        return {
            "entry_count": len(self._entries),
            "level_distribution": level_counts,
            "source_distribution": source_counts,
            "time_span": time_span,
            "is_sealed": self._sealed,
            "is_archived": self._archive_date is not None,
            "integrity_status": (
                "verified" if self.verify_integrity().is_valid else "compromised"
            ),
        }

    def _verify_hash_chain(self) -> bool:
        """Verify the integrity of the hash chain."""
        if not self._entries:
            return True

        # Rebuild hash chain and compare
        rebuilt_chain = HashChain()
        for entry in self._entries:
            rebuilt_chain = rebuilt_chain.add_hash(entry.hash)

        return rebuilt_chain.current_hash == self._hash_chain.current_hash

    def _check_timestamp_gaps(self) -> list[str]:
        """Check for unusual gaps in timestamps."""
        if len(self._entries) < 2:
            return []

        warnings = []
        sorted_entries = sorted(self._entries, key=lambda x: x.timestamp)

        for i in range(1, len(sorted_entries)):
            time_diff = sorted_entries[i].timestamp - sorted_entries[i - 1].timestamp

            # Flag gaps longer than 1 hour
            if time_diff.total_seconds() > 3600:
                warnings.append(
                    f"Large time gap ({time_diff}) between entries "
                    f"{sorted_entries[i - 1].id} and {sorted_entries[i].id}"
                )

        return warnings


class IntegrityMonitor(MultiTenantAggregateRoot):
    """
    Aggregate root for monitoring system integrity across multiple components.

    Tracks integrity checks, violations, and compliance status.
    """

    def __init__(
        self,
        monitor_id: EntityId,
        tenant_id: TenantId,
        monitor_name: str,
        monitored_components: list[str],
    ):
        super().__init__(monitor_id, tenant_id)
        self.monitor_name = monitor_name
        self.monitored_components = monitored_components.copy()
        self._integrity_checks: list[IntegrityCheckResult] = []
        self._violation_count = 0
        self.last_check = datetime.utcnow()
        self.created_at = datetime.utcnow()

    @property
    def integrity_checks(self) -> list[IntegrityCheckResult]:
        """Get integrity check history."""
        return self._integrity_checks.copy()

    @property
    def violation_count(self) -> int:
        """Get total violation count."""
        return self._violation_count

    def record_integrity_check(self, result: IntegrityCheckResult) -> None:
        """Record integrity check result."""
        self._integrity_checks.append(result)

        if not result.is_valid:
            self._violation_count += 1

        self.last_check = datetime.utcnow()

    def get_integrity_status(self) -> dict[str, Any]:
        """Get current integrity status."""
        if not self._integrity_checks:
            return {"status": "unknown", "last_check": None, "violation_rate": 0.0}

        recent_checks = self._integrity_checks[-10:]  # Last 10 checks
        valid_checks = sum(1 for check in recent_checks if check.is_valid)

        violation_rate = 1.0 - (valid_checks / len(recent_checks))

        if violation_rate == 0.0:
            status = "healthy"
        elif violation_rate < 0.1:
            status = "warning"
        else:
            status = "critical"

        return {
            "status": status,
            "last_check": self.last_check.isoformat(),
            "violation_rate": violation_rate,
            "total_violations": self._violation_count,
            "total_checks": len(self._integrity_checks),
        }
