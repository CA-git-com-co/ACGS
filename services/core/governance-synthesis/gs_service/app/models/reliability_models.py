from dataclasses import dataclass, field
from typing import Any


@dataclass
class ConstitutionalPrinciple:
    """Represents a constitutional principle for policy synthesis."""

    id: str
    text: str
    version: str | None = None
    source: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SynthesisContext:
    """Context information for policy synthesis."""

    domain: str | None = None
    jurisdiction: str | None = None
    target_audience: str | None = None
    application_scenario: str | None = None
    historical_data: list[dict[str, Any]] | None = field(default_factory=list)
    related_policies: list[str] | None = field(default_factory=list)
    custom_instructions: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
