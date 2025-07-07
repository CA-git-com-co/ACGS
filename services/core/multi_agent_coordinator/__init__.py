"""
Multi-Agent Coordinator for ACGS Hybrid Hierarchical-Blackboard Policy
"""

from .coordinator_agent import (
    CoordinatorAgent,
    GovernanceRequest,
    TaskDecompositionStrategy,
)

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


__all__ = ["CoordinatorAgent", "GovernanceRequest", "TaskDecompositionStrategy"]
