"""
Constitutional Principle Mock Implementation

Provides mock ConstitutionalPrinciple class for testing and fallback scenarios.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class ConstitutionalPrinciple:
    """Mock ConstitutionalPrinciple for type compatibility."""

    principle_id: str
    principle_text: str
    scope: str = "general"
    severity: str = "medium"
    distance_score: float | None = None
    priority_weight: float = 1.0
    constraints: dict[str, Any] | None = None

    def __post_init__(self):
        if self.constraints is None:
            self.constraints = {}

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "principle_id": self.principle_id,
            "principle_text": self.principle_text,
            "scope": self.scope,
            "severity": self.severity,
            "distance_score": self.distance_score,
            "priority_weight": self.priority_weight,
            "constraints": self.constraints,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ConstitutionalPrinciple":
        """Create from dictionary representation."""
        return cls(
            principle_id=data.get("principle_id", ""),
            principle_text=data.get("principle_text", ""),
            scope=data.get("scope", "general"),
            severity=data.get("severity", "medium"),
            distance_score=data.get("distance_score"),
            priority_weight=data.get("priority_weight", 1.0),
            constraints=data.get("constraints", {}),
        )
