"""
Consensus Engine for Multi-Agent Conflict Resolution
"""

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

from .consensus_mechanisms import (
    ConsensusEngine,
    ConsensusAlgorithm,
    ConsensusSession,
    VoteOption,
    Vote,
    MajorityVoteConsensus,
    WeightedVoteConsensus,
    RankedChoiceConsensus,
    ConsensusThresholdConsensus,
    HierarchicalOverrideConsensus,
    ConstitutionalPriorityConsensus,
    ExpertMediationConsensus
)

__all__ = [
    'ConsensusEngine',
    'ConsensusAlgorithm',
    'ConsensusSession',
    'VoteOption',
    'Vote',
    'MajorityVoteConsensus',
    'WeightedVoteConsensus',
    'RankedChoiceConsensus',
    'ConsensusThresholdConsensus',
    'HierarchicalOverrideConsensus',
    'ConstitutionalPriorityConsensus',
    'ExpertMediationConsensus'
]