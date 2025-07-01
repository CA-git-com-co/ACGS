# Models module - simplified to avoid circular imports
# This module provides access to shared models without circular import issues

# For now, we'll create simple mock classes to avoid import issues
# These can be replaced with proper imports once the circular dependency is resolved

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class ACAmendment:
    """Mock ACAmendment model for testing."""

    id: int | None = None
    title: str = ""
    description: str = ""
    status: str = "draft"
    created_at: datetime | None = None


@dataclass
class ACAmendmentComment:
    """Mock ACAmendmentComment model for testing."""

    id: int | None = None
    amendment_id: int | None = None
    content: str = ""
    created_at: datetime | None = None


@dataclass
class ACAmendmentVote:
    """Mock ACAmendmentVote model for testing."""

    id: int | None = None
    amendment_id: int | None = None
    vote: str = "abstain"
    created_at: datetime | None = None


@dataclass
class ACConflictResolution:
    """Mock ACConflictResolution model for testing."""

    id: int | None = None
    conflict_type: str = ""
    resolution: str = ""
    status: str = "pending"


@dataclass
class ACMetaRule:
    """Mock ACMetaRule model for testing."""

    id: int | None = None
    rule_type: str = ""
    content: str = ""
    priority: int = 0


@dataclass
class Principle:
    """Mock Principle model for testing."""

    id: int | None = None
    title: str = ""
    content: str = ""
    category: str = ""


@dataclass
class User:
    """Mock User model for testing."""

    id: int | None = None
    username: str = ""
    email: str = ""
    role: str = "user"


@dataclass
class RefreshToken:
    """Mock RefreshToken model for testing."""

    id: int | None = None
    user_id: int | None = None
    token: str = ""
    jti: str = ""
    expires_at: datetime | None = None
    created_at: datetime | None = None
    is_revoked: bool = False


__all__ = [
    "ACAmendment",
    "ACAmendmentComment",
    "ACAmendmentVote",
    "ACConflictResolution",
    "ACMetaRule",
    "Principle",
    "RefreshToken",
    "User",
]
