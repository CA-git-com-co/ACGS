"""
Infrastructure Layer - Gateways
Constitutional Hash: cdd01ef066bc6cf2

This module contains gateways that isolate side-effects and external dependencies,
making the domain and service layers easily testable through mock injection.
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from ....shared.config.settings import get_settings
from ....shared.di.container import ServiceLifetime, injectable
from ..domain.entities import (
    AuditEvent,
    ConstitutionalPrinciple,
    ContentValidationRequest,
    PolicyDecision,
    ValidationResult,
)

logger = logging.getLogger(__name__)

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


# Repository Interfaces (Ports)
class ConstitutionalRepository(ABC):
    """Repository interface for constitutional data."""

    @abstractmethod
    async def get_principles(self) -> list[ConstitutionalPrinciple]:
        """Get all constitutional principles."""

    @abstractmethod
    async def get_principle_by_id(
        self, principle_id: str
    ) -> ConstitutionalPrinciple | None:
        """Get a constitutional principle by ID."""

    @abstractmethod
    async def save_principle(self, principle: ConstitutionalPrinciple) -> None:
        """Save a constitutional principle."""


class PolicyRepository(ABC):
    """Repository interface for policy data."""

    @abstractmethod
    async def get_policies(self, context: dict[str, Any]) -> list[dict[str, Any]]:
        """Get policies applicable to the given context."""

    @abstractmethod
    async def save_decision(self, decision: PolicyDecision) -> None:
        """Save a policy decision."""


class AuditRepository(ABC):
    """Repository interface for audit data."""

    @abstractmethod
    async def save_event(self, event: AuditEvent) -> None:
        """Save an audit event."""

    @abstractmethod
    async def get_events_by_entity(self, entity_id: str) -> list[AuditEvent]:
        """Get audit events for an entity."""

    @abstractmethod
    async def get_events_by_type(
        self, event_type: str, limit: int = 100
    ) -> list[AuditEvent]:
        """Get audit events by type."""


class ExternalValidationGateway(ABC):
    """Gateway interface for external validation services."""

    @abstractmethod
    async def validate_content(
        self, request: ContentValidationRequest
    ) -> ValidationResult | None:
        """Validate content using external services."""

    @abstractmethod
    async def check_content_safety(self, content: str) -> dict[str, Any]:
        """Check content safety using external services."""


# Database Implementation
@injectable(ServiceLifetime.SCOPED)
class DatabaseConstitutionalRepository(ConstitutionalRepository):
    """Database implementation of constitutional repository."""

    def __init__(self):
        self.settings = get_settings()
        logger.debug("DatabaseConstitutionalRepository initialized")

    async def get_principles(self) -> list[ConstitutionalPrinciple]:
        """Get all constitutional principles from database."""
        # In a real implementation, this would query the database
        # For now, return mock data
        return [
            ConstitutionalPrinciple(
                principle_id="transparency-001",
                name="Transparency",
                description="AI systems must be transparent and explainable",
                priority=1.0,
                rules=["explain_decisions", "audit_trail", "transparency_required"],
            ),
            ConstitutionalPrinciple(
                principle_id="safety-001",
                name="Safety",
                description="AI systems must not cause harm",
                priority=1.5,
                rules=["harmful_content", "bias_detection", "safety_checks"],
            ),
            ConstitutionalPrinciple(
                principle_id="privacy-001",
                name="Privacy",
                description="Protect user privacy and data",
                priority=1.2,
                rules=["privacy_protection", "data_minimization", "consent_required"],
            ),
        ]

    async def get_principle_by_id(
        self, principle_id: str
    ) -> ConstitutionalPrinciple | None:
        """Get a constitutional principle by ID."""
        principles = await self.get_principles()
        return next((p for p in principles if p.principle_id == principle_id), None)

    async def save_principle(self, principle: ConstitutionalPrinciple) -> None:
        """Save a constitutional principle to database."""
        # In a real implementation, this would save to database
        logger.info(f"Saving constitutional principle: {principle.name}")


@injectable(ServiceLifetime.SCOPED)
class DatabasePolicyRepository(PolicyRepository):
    """Database implementation of policy repository."""

    def __init__(self):
        self.settings = get_settings()
        logger.debug("DatabasePolicyRepository initialized")

    async def get_policies(self, context: dict[str, Any]) -> list[dict[str, Any]]:
        """Get policies applicable to the given context."""
        # Mock policy data
        return [
            {
                "policy_id": "content-safety-001",
                "name": "Content Safety Policy",
                "rules": ["no_harmful_content", "no_illegal_content"],
                "weight": 1.0,
            },
            {
                "policy_id": "bias-prevention-001",
                "name": "Bias Prevention Policy",
                "rules": ["bias_detection", "fairness_check"],
                "weight": 0.8,
            },
        ]

    async def save_decision(self, decision: PolicyDecision) -> None:
        """Save a policy decision to database."""
        logger.info(
            f"Saving policy decision: {decision.decision} for {decision.policy_id}"
        )


@injectable(ServiceLifetime.SCOPED)
class DatabaseAuditRepository(AuditRepository):
    """Database implementation of audit repository."""

    def __init__(self):
        self.settings = get_settings()
        logger.debug("DatabaseAuditRepository initialized")

    async def save_event(self, event: AuditEvent) -> None:
        """Save an audit event to database."""
        # In a real implementation, this would save to database
        logger.debug(
            f"Audit event saved: {event.event_type} for"
            f" {event.entity_type}:{event.entity_id}"
        )

    async def get_events_by_entity(self, entity_id: str) -> list[AuditEvent]:
        """Get audit events for an entity."""
        # Mock audit data
        return [
            AuditEvent(
                event_type="validation_request",
                entity_type="content",
                entity_id=entity_id,
                action="validate",
                metadata={"constitutional_hash": CONSTITUTIONAL_HASH},
            )
        ]

    async def get_events_by_type(
        self, event_type: str, limit: int = 100
    ) -> list[AuditEvent]:
        """Get audit events by type."""
        # Mock audit data
        return []


# External Service Implementations
@injectable(ServiceLifetime.SCOPED)
class HTTPExternalValidationGateway(ExternalValidationGateway):
    """HTTP implementation of external validation gateway."""

    def __init__(self):
        self.settings = get_settings()
        logger.debug("HTTPExternalValidationGateway initialized")

    async def validate_content(
        self, request: ContentValidationRequest
    ) -> ValidationResult | None:
        """Validate content using external HTTP services."""
        try:
            # In a real implementation, this would make HTTP calls to external services
            # For now, return None (no external validation)
            logger.debug(f"External validation requested for {request.request_id}")
            return None
        except Exception as e:
            logger.error(f"External validation failed: {e}")
            return None

    async def check_content_safety(self, content: str) -> dict[str, Any]:
        """Check content safety using external services."""
        try:
            # Mock safety check response
            return {
                "is_safe": True,
                "confidence": 0.95,
                "categories": [],
                "service": "mock_safety_service",
            }
        except Exception as e:
            logger.error(f"Content safety check failed: {e}")
            return {"is_safe": False, "error": str(e)}


# File System Implementations (for development/testing)
@injectable(ServiceLifetime.SCOPED)
class FileSystemAuditRepository(AuditRepository):
    """File system implementation of audit repository for development."""

    def __init__(self):
        self.settings = get_settings()
        self.audit_file = "/tmp/acgs_audit.log"
        logger.debug("FileSystemAuditRepository initialized")

    async def save_event(self, event: AuditEvent) -> None:
        """Save an audit event to file."""
        try:
            import json

            event_data = {
                "event_id": event.event_id,
                "event_type": event.event_type,
                "entity_type": event.entity_type,
                "entity_id": event.entity_id,
                "action": event.action,
                "actor_id": event.actor_id,
                "metadata": event.metadata,
                "timestamp": event.timestamp.isoformat(),
                "constitutional_hash": event.constitutional_hash,
            }

            with open(self.audit_file, "a") as f:
                f.write(json.dumps(event_data) + "\n")

            logger.debug(f"Audit event saved to file: {event.event_type}")
        except Exception as e:
            logger.error(f"Failed to save audit event to file: {e}")

    async def get_events_by_entity(self, entity_id: str) -> list[AuditEvent]:
        """Get audit events for an entity from file."""
        try:
            import json

            events = []
            with open(self.audit_file) as f:
                for line in f:
                    event_data = json.loads(line.strip())
                    if event_data["entity_id"] == entity_id:
                        events.append(
                            AuditEvent(
                                event_id=event_data["event_id"],
                                event_type=event_data["event_type"],
                                entity_type=event_data["entity_type"],
                                entity_id=event_data["entity_id"],
                                action=event_data["action"],
                                actor_id=event_data["actor_id"],
                                metadata=event_data["metadata"],
                                timestamp=datetime.fromisoformat(
                                    event_data["timestamp"]
                                ),
                                constitutional_hash=event_data["constitutional_hash"],
                            )
                        )
            return events
        except FileNotFoundError:
            return []
        except Exception as e:
            logger.error(f"Failed to read audit events from file: {e}")
            return []

    async def get_events_by_type(
        self, event_type: str, limit: int = 100
    ) -> list[AuditEvent]:
        """Get audit events by type from file."""
        try:
            import json

            events = []
            count = 0
            with open(self.audit_file) as f:
                for line in f:
                    if count >= limit:
                        break
                    event_data = json.loads(line.strip())
                    if event_data["event_type"] == event_type:
                        events.append(
                            AuditEvent(
                                event_id=event_data["event_id"],
                                event_type=event_data["event_type"],
                                entity_type=event_data["entity_type"],
                                entity_id=event_data["entity_id"],
                                action=event_data["action"],
                                actor_id=event_data["actor_id"],
                                metadata=event_data["metadata"],
                                timestamp=datetime.fromisoformat(
                                    event_data["timestamp"]
                                ),
                                constitutional_hash=event_data["constitutional_hash"],
                            )
                        )
                        count += 1
            return events
        except FileNotFoundError:
            return []
        except Exception as e:
            logger.error(f"Failed to read audit events from file: {e}")
            return []


# Cache Implementations
@injectable(ServiceLifetime.SCOPED)
class RedisConstitutionalRepository(ConstitutionalRepository):
    """Redis-cached implementation of constitutional repository."""

    def __init__(self, db_repo: DatabaseConstitutionalRepository):
        self.db_repo = db_repo
        self.settings = get_settings()
        self.cache_ttl = 3600  # 1 hour
        logger.debug("RedisConstitutionalRepository initialized")

    async def get_principles(self) -> list[ConstitutionalPrinciple]:
        """Get constitutional principles with Redis caching."""
        # In a real implementation, this would check Redis cache first
        # then fall back to database if cache miss
        return await self.db_repo.get_principles()

    async def get_principle_by_id(
        self, principle_id: str
    ) -> ConstitutionalPrinciple | None:
        """Get a constitutional principle by ID with caching."""
        return await self.db_repo.get_principle_by_id(principle_id)

    async def save_principle(self, principle: ConstitutionalPrinciple) -> None:
        """Save a constitutional principle and invalidate cache."""
        await self.db_repo.save_principle(principle)
        # In a real implementation, this would invalidate the Redis cache


# Gateway Factory for easy switching between implementations
class GatewayFactory:
    """Factory for creating gateway implementations."""

    @staticmethod
    def create_audit_repository(use_file_system: bool = False) -> AuditRepository:
        """Create audit repository implementation."""
        if use_file_system:
            return FileSystemAuditRepository()
        return DatabaseAuditRepository()

    @staticmethod
    def create_constitutional_repository(
        use_cache: bool = True,
    ) -> ConstitutionalRepository:
        """Create constitutional repository implementation."""
        db_repo = DatabaseConstitutionalRepository()
        if use_cache:
            return RedisConstitutionalRepository(db_repo)
        return db_repo

    @staticmethod
    def create_policy_repository() -> PolicyRepository:
        """Create policy repository implementation."""
        return DatabasePolicyRepository()

    @staticmethod
    def create_external_validation_gateway() -> ExternalValidationGateway:
        """Create external validation gateway implementation."""
        return HTTPExternalValidationGateway()
