"""
Domain Model Foundation for ACGS
Constitutional Hash: cdd01ef066bc6cf2

This module provides the base classes for Domain-Driven Design implementation.
"""

from .base import (
    CONSTITUTIONAL_HASH,
    AggregateRoot,
    DomainException,
    Entity,
    ValueObject,
)
from .events import DomainEvent, DomainEventHandler, EventMetadata
from .specifications import (
    AndSpecification,
    NotSpecification,
    OrSpecification,
    Specification,
)

__all__ = [
    "CONSTITUTIONAL_HASH",
    "AggregateRoot",
    "AndSpecification",
    # Events
    "DomainEvent",
    "DomainEventHandler",
    "DomainException",
    # Base classes
    "Entity",
    "EventMetadata",
    "NotSpecification",
    "OrSpecification",
    # Specifications
    "Specification",
    "ValueObject",
]
