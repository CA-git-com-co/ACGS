# Import models from shared module to maintain consistency across services
from services.shared.models import (
    ACAmendment,
    ACAmendmentComment,
    ACAmendmentVote,
    ACConflictResolution,
    ACMetaRule,
    Principle,
    User,
)

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Re-export models for use in this service
__all__ = [
    "CONSTITUTIONAL_HASH",
    "ACAmendment",
    "ACAmendmentComment",
    "ACAmendmentVote",
    "ACConflictResolution",
    "ACMetaRule",
    "Principle",
    "User",
]
