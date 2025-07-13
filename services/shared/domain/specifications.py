"""
Specification Pattern Implementation for ACGS
Constitutional Hash: cdd01ef066bc6cf2

Provides specification pattern for complex domain queries and validations.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class Specification(ABC, Generic[T]):
    """
    Base specification pattern for domain logic encapsulation.

    Specifications are predicates that determine if an object
    satisfies certain criteria.
    """

    @abstractmethod
    def is_satisfied_by(self, candidate: T) -> bool:
        """Check if the candidate satisfies this specification."""

    def and_(self, other: "Specification[T]") -> "Specification[T]":
        """Create an AND specification combining this and another."""
        return AndSpecification(self, other)

    def or_(self, other: "Specification[T]") -> "Specification[T]":
        """Create an OR specification combining this and another."""
        return OrSpecification(self, other)

    def not_(self) -> "Specification[T]":
        """Create a NOT specification inverting this one."""
        return NotSpecification(self)

    def __and__(self, other: "Specification[T]") -> "Specification[T]":
        """Support & operator for AND specifications."""
        return self.and_(other)

    def __or__(self, other: "Specification[T]") -> "Specification[T]":
        """Support | operator for OR specifications."""
        return self.or_(other)

    def __invert__(self) -> "Specification[T]":
        """Support ~ operator for NOT specifications."""
        return self.not_()


class AndSpecification(Specification[T]):
    """Specification that requires both specifications to be satisfied."""

    def __init__(self, left: Specification[T], right: Specification[T]):
        """Initialize AND specification."""
        self._left = left
        self._right = right

    def is_satisfied_by(self, candidate: T) -> bool:
        """Check if candidate satisfies both specifications."""
        return self._left.is_satisfied_by(candidate) and self._right.is_satisfied_by(
            candidate
        )


class OrSpecification(Specification[T]):
    """Specification that requires at least one specification to be satisfied."""

    def __init__(self, left: Specification[T], right: Specification[T]):
        """Initialize OR specification."""
        self._left = left
        self._right = right

    def is_satisfied_by(self, candidate: T) -> bool:
        """Check if candidate satisfies at least one specification."""
        return self._left.is_satisfied_by(candidate) or self._right.is_satisfied_by(
            candidate
        )


class NotSpecification(Specification[T]):
    """Specification that inverts another specification."""

    def __init__(self, spec: Specification[T]):
        """Initialize NOT specification."""
        self._spec = spec

    def is_satisfied_by(self, candidate: T) -> bool:
        """Check if candidate does not satisfy the specification."""
        return not self._spec.is_satisfied_by(candidate)


class AlwaysTrueSpecification(Specification[T]):
    """Specification that is always satisfied."""

    def is_satisfied_by(self, candidate: T) -> bool:
        """Always returns True."""
        return True


class AlwaysFalseSpecification(Specification[T]):
    """Specification that is never satisfied."""

    def is_satisfied_by(self, candidate: T) -> bool:
        """Always returns False."""
        return False


class CompositeSpecification(Specification[T]):
    """Base class for composite specifications with helper methods."""

    def __init__(self):
        """Initialize composite specification."""
        self._specifications: list[Specification[T]] = []

    def add(self, specification: Specification[T]) -> "CompositeSpecification[T]":
        """Add a specification to the composite."""
        self._specifications.append(specification)
        return self


class AllOfSpecification(CompositeSpecification[T]):
    """Specification that requires all sub-specifications to be satisfied."""

    def is_satisfied_by(self, candidate: T) -> bool:
        """Check if candidate satisfies all specifications."""
        return all(spec.is_satisfied_by(candidate) for spec in self._specifications)


class AnyOfSpecification(CompositeSpecification[T]):
    """Specification that requires any sub-specification to be satisfied."""

    def is_satisfied_by(self, candidate: T) -> bool:
        """Check if candidate satisfies any specification."""
        return any(spec.is_satisfied_by(candidate) for spec in self._specifications)


class NoneOfSpecification(CompositeSpecification[T]):
    """Specification that requires no sub-specifications to be satisfied."""

    def is_satisfied_by(self, candidate: T) -> bool:
        """Check if candidate satisfies no specifications."""
        return not any(spec.is_satisfied_by(candidate) for spec in self._specifications)
