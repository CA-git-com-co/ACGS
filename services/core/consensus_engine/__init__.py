"""
Consensus Engine for Multi-Agent Conflict Resolution
"""

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

from .consensus_mechanisms import (
    ConsensusAlgorithm,
    ConsensusEngine,
    ConsensusSession,
    ConsensusThresholdConsensus,
    ConstitutionalPriorityConsensus,
    ExpertMediationConsensus,
    HierarchicalOverrideConsensus,
    MajorityVoteConsensus,
    RankedChoiceConsensus,
    Vote,
    VoteOption,
    WeightedVoteConsensus,
)

__all__ = [
    "ConsensusEngine",
    "ConsensusAlgorithm",
    "ConsensusSession",
    "VoteOption",
    "Vote",
    "MajorityVoteConsensus",
    "WeightedVoteConsensus",
    "RankedChoiceConsensus",
    "ConsensusThresholdConsensus",
    "HierarchicalOverrideConsensus",
    "ConstitutionalPriorityConsensus",
    "ExpertMediationConsensus",
]
