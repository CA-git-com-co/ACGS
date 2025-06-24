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

    id: Optional[int] = None
    title: str = ""
    description: str = ""
    status: str = "draft"
    created_at: Optional[datetime] = None


@dataclass
class ACAmendmentComment:
    """Mock ACAmendmentComment model for testing."""

    id: Optional[int] = None
    amendment_id: Optional[int] = None
    content: str = ""
    created_at: Optional[datetime] = None


@dataclass
class ACAmendmentVote:
    """Mock ACAmendmentVote model for testing."""

    id: Optional[int] = None
    amendment_id: Optional[int] = None
    vote: str = "abstain"
    created_at: Optional[datetime] = None


@dataclass
class ACConflictResolution:
    """Mock ACConflictResolution model for testing."""

    id: Optional[int] = None
    conflict_type: str = ""
    resolution: str = ""
    status: str = "pending"


@dataclass
class ACMetaRule:
    """Mock ACMetaRule model for testing."""

    id: Optional[int] = None
    rule_type: str = ""
    content: str = ""
    priority: int = 0


@dataclass
class Principle:
    """Mock Principle model for testing."""

    id: Optional[int] = None
    title: str = ""
    content: str = ""
    category: str = ""


@dataclass
class User:
    """Mock User model for testing."""

    id: Optional[int] = None
    username: str = ""
    email: str = ""
    role: str = "user"


@dataclass
class RefreshToken:
    """Mock RefreshToken model for testing."""

    id: Optional[int] = None
    user_id: Optional[int] = None
    token: str = ""
    jti: str = ""
    expires_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    is_revoked: bool = False


__all__ = [
    "ACAmendment",
    "ACAmendmentComment",
    "ACAmendmentVote",
    "ACConflictResolution",
    "ACMetaRule",
    "Principle",
    "User",
    "RefreshToken",
]
