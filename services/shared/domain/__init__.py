"""
Domain Model Foundation for ACGS
Constitutional Hash: cdd01ef066bc6cf2

This module provides the base classes for Domain-Driven Design implementation.
"""

from .base import (
    Entity,
    ValueObject,
    AggregateRoot,
    DomainException,
    CONSTITUTIONAL_HASH
)
from .events import (
    DomainEvent,
    DomainEventHandler,
    EventMetadata
)
from .specifications import (
    Specification,
    AndSpecification,
    OrSpecification,
    NotSpecification
)

__all__ = [
    # Base classes
    "Entity",
    "ValueObject", 
    "AggregateRoot",
    "DomainException",
    "CONSTITUTIONAL_HASH",
    
    # Events
    "DomainEvent",
    "DomainEventHandler",
    "EventMetadata",
    
    # Specifications
    "Specification",
    "AndSpecification",
    "OrSpecification",
    "NotSpecification"
]