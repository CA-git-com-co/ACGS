"""
Base Domain Model Classes for ACGS
Constitutional Hash: cdd01ef066bc6cf2

Provides Entity, ValueObject, and AggregateRoot base classes for DDD implementation.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, TypeVar, Generic
from uuid import UUID, uuid4
import hashlib
import json

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

T = TypeVar('T')


class DomainException(Exception):
    """Base exception for domain-related errors."""
    pass


class InvalidEntityStateException(DomainException):
    """Raised when an entity is in an invalid state."""
    pass


class ConcurrencyException(DomainException):
    """Raised when there's a concurrency conflict."""
    pass


@dataclass(frozen=True)
class EntityId:
    """Strongly-typed entity identifier."""
    value: UUID
    
    @classmethod
    def generate(cls) -> 'EntityId':
        """Generate a new entity ID."""
        return cls(value=uuid4())
    
    def __str__(self) -> str:
        return str(self.value)


class Entity(ABC):
    """
    Base class for all entities in the domain model.
    
    Entities have identity and are mutable. Two entities are equal
    if they have the same identity, regardless of their attributes.
    """
    
    def __init__(self, entity_id: Optional[EntityId] = None):
        """Initialize entity with an ID."""
        self._id = entity_id or EntityId.generate()
        self._version = 0
        self._created_at = datetime.utcnow()
        self._updated_at = datetime.utcnow()
    
    @property
    def id(self) -> EntityId:
        """Get the entity's unique identifier."""
        return self._id
    
    @property
    def version(self) -> int:
        """Get the entity's version for optimistic concurrency control."""
        return self._version
    
    @property
    def created_at(self) -> datetime:
        """Get the entity's creation timestamp."""
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        """Get the entity's last update timestamp."""
        return self._updated_at
    
    def increment_version(self) -> None:
        """Increment version for optimistic concurrency control."""
        self._version += 1
        self._updated_at = datetime.utcnow()
    
    def __eq__(self, other: Any) -> bool:
        """Entities are equal if they have the same ID."""
        if not isinstance(other, Entity):
            return False
        return self._id == other._id
    
    def __hash__(self) -> int:
        """Hash based on entity ID."""
        return hash(self._id)
    
    def validate_invariants(self) -> None:
        """
        Validate entity invariants. Override in subclasses.
        Raises InvalidEntityStateException if invariants are violated.
        """
        pass


class ValueObject(ABC):
    """
    Base class for value objects in the domain model.
    
    Value objects are immutable and have no identity. Two value objects
    are equal if all their attributes are equal.
    """
    
    def __init__(self):
        """Initialize value object. Should be overridden to freeze after init."""
        self._validate()
    
    @abstractmethod
    def _validate(self) -> None:
        """
        Validate the value object's state.
        Raises ValueError if validation fails.
        """
        pass
    
    def __eq__(self, other: Any) -> bool:
        """Value objects are equal if all attributes are equal."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__
    
    def __hash__(self) -> int:
        """Hash based on all attributes."""
        values = tuple(sorted(self.__dict__.items()))
        return hash(values)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert value object to dictionary."""
        return {
            k: v for k, v in self.__dict__.items() 
            if not k.startswith('_')
        }


class DomainEvent:
    """Base class for domain events."""
    
    def __init__(self, aggregate_id: EntityId, occurred_at: Optional[datetime] = None):
        """Initialize domain event."""
        self.event_id = EntityId.generate()
        self.aggregate_id = aggregate_id
        self.occurred_at = occurred_at or datetime.utcnow()
        self.event_type = self.__class__.__name__
        self.event_version = "1.0"
        self.constitutional_hash = CONSTITUTIONAL_HASH
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            "event_id": str(self.event_id),
            "aggregate_id": str(self.aggregate_id),
            "occurred_at": self.occurred_at.isoformat(),
            "event_type": self.event_type,
            "event_version": self.event_version,
            "constitutional_hash": self.constitutional_hash,
            "data": self._get_event_data()
        }
    
    def _get_event_data(self) -> Dict[str, Any]:
        """Get event-specific data. Override in subclasses."""
        return {}


class AggregateRoot(Entity):
    """
    Base class for aggregate roots in the domain model.
    
    Aggregate roots are the entry points to aggregates and maintain
    consistency boundaries. They can emit domain events.
    """
    
    def __init__(self, entity_id: Optional[EntityId] = None):
        """Initialize aggregate root."""
        super().__init__(entity_id)
        self._uncommitted_events: List[DomainEvent] = []
        self._event_version = 0
    
    @property
    def uncommitted_events(self) -> List[DomainEvent]:
        """Get uncommitted domain events."""
        return self._uncommitted_events.copy()
    
    def mark_events_as_committed(self) -> None:
        """Clear uncommitted events after they've been persisted."""
        self._uncommitted_events.clear()
    
    def add_domain_event(self, event: DomainEvent) -> None:
        """Add a domain event to be published."""
        self._uncommitted_events.append(event)
        self._event_version += 1
    
    def apply_event(self, event: DomainEvent) -> None:
        """
        Apply a domain event to update aggregate state.
        Override in subclasses to handle specific events.
        """
        # Default implementation - subclasses should override
        self._event_version += 1
    
    def load_from_history(self, events: List[DomainEvent]) -> None:
        """Rebuild aggregate state from event history."""
        for event in events:
            self.apply_event(event)
        # Clear uncommitted events since we're loading from history
        self._uncommitted_events.clear()
    
    def get_aggregate_hash(self) -> str:
        """Get a hash representing the current state of the aggregate."""
        state_dict = self._get_state_for_hash()
        state_json = json.dumps(state_dict, sort_keys=True, default=str)
        return hashlib.sha256(state_json.encode()).hexdigest()
    
    def _get_state_for_hash(self) -> Dict[str, Any]:
        """
        Get the state to be included in the aggregate hash.
        Override in subclasses to include relevant state.
        """
        return {
            "id": str(self._id),
            "version": self._version,
            "event_version": self._event_version,
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
    
    @abstractmethod
    def validate_invariants(self) -> None:
        """
        Validate aggregate invariants.
        Must be implemented by subclasses.
        """
        pass


@dataclass(frozen=True)
class TenantId(ValueObject):
    """Value object representing a tenant identifier."""
    value: UUID
    
    def _validate(self) -> None:
        """Validate tenant ID."""
        if not isinstance(self.value, UUID):
            raise ValueError("Tenant ID must be a UUID")
    
    @classmethod
    def from_string(cls, tenant_id: str) -> 'TenantId':
        """Create TenantId from string."""
        return cls(value=UUID(tenant_id))
    
    def __str__(self) -> str:
        return str(self.value)


class MultiTenantEntity(Entity):
    """Base class for multi-tenant entities."""
    
    def __init__(self, entity_id: Optional[EntityId], tenant_id: TenantId):
        """Initialize multi-tenant entity."""
        super().__init__(entity_id)
        self._tenant_id = tenant_id
    
    @property
    def tenant_id(self) -> TenantId:
        """Get the entity's tenant ID."""
        return self._tenant_id
    
    def ensure_same_tenant(self, other_tenant_id: TenantId) -> None:
        """Ensure operation is within same tenant boundary."""
        if self._tenant_id != other_tenant_id:
            raise DomainException(
                f"Cross-tenant operation not allowed. "
                f"Entity tenant: {self._tenant_id}, "
                f"Operation tenant: {other_tenant_id}"
            )


class MultiTenantAggregateRoot(AggregateRoot):
    """Base class for multi-tenant aggregate roots."""
    
    def __init__(self, entity_id: Optional[EntityId], tenant_id: TenantId):
        """Initialize multi-tenant aggregate root."""
        super().__init__(entity_id)
        self._tenant_id = tenant_id
    
    @property
    def tenant_id(self) -> TenantId:
        """Get the aggregate's tenant ID."""
        return self._tenant_id
    
    def ensure_same_tenant(self, other_tenant_id: TenantId) -> None:
        """Ensure operation is within same tenant boundary."""
        if self._tenant_id != other_tenant_id:
            raise DomainException(
                f"Cross-tenant operation not allowed. "
                f"Aggregate tenant: {self._tenant_id}, "
                f"Operation tenant: {other_tenant_id}"
            )