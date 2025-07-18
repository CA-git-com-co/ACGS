"""
Consensus Engine Models
Constitutional Hash: cdd01ef066bc6cf2

Data models for distributed consensus mechanisms including PBFT, Raft,
constitutional consensus, and multi-agent decision making.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Set
from enum import Enum
from pydantic import BaseModel, Field, validator
import uuid

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

class ConsensusAlgorithm(str, Enum):
    """Consensus algorithms supported"""
    PBFT = "pbft"  # Practical Byzantine Fault Tolerance
    RAFT = "raft"  # Raft consensus
    CONSTITUTIONAL = "constitutional"  # Constitutional governance consensus
    PROOF_OF_STAKE = "proof_of_stake"  # Proof of Stake
    DELEGATED_PROOF_OF_STAKE = "delegated_proof_of_stake"  # DPoS
    MULTI_AGENT_VOTING = "multi_agent_voting"  # Multi-agent voting
    WEIGHTED_VOTING = "weighted_voting"  # Weighted voting based on reputation
    FEDERATED_CONSENSUS = "federated_consensus"  # Federated Byzantine Agreement

class NodeRole(str, Enum):
    """Node roles in consensus"""
    LEADER = "leader"
    FOLLOWER = "follower"
    CANDIDATE = "candidate"
    VALIDATOR = "validator"
    OBSERVER = "observer"
    DELEGATE = "delegate"
    CONSTITUTIONAL_GUARDIAN = "constitutional_guardian"

class ProposalType(str, Enum):
    """Types of proposals for consensus"""
    POLICY_CHANGE = "policy_change"
    SYSTEM_UPGRADE = "system_upgrade"
    RESOURCE_ALLOCATION = "resource_allocation"
    CONSTITUTIONAL_AMENDMENT = "constitutional_amendment"
    AGENT_REGISTRATION = "agent_registration"
    SERVICE_DEPLOYMENT = "service_deployment"
    PARAMETER_ADJUSTMENT = "parameter_adjustment"
    EMERGENCY_ACTION = "emergency_action"

class VoteType(str, Enum):
    """Vote types"""
    YES = "yes"
    NO = "no"
    ABSTAIN = "abstain"
    CONDITIONAL = "conditional"
    VETO = "veto"  # Constitutional veto power

class ConsensusStatus(str, Enum):
    """Consensus process status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    ACHIEVED = "achieved"
    FAILED = "failed"
    TIMEOUT = "timeout"
    VETOED = "vetoed"
    CONSTITUTIONAL_VIOLATION = "constitutional_violation"

class NodeIdentity(BaseModel):
    """Identity of a consensus node"""
    node_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    role: NodeRole
    public_key: str
    stake_amount: float = Field(ge=0.0, default=0.0)
    reputation_score: float = Field(ge=0.0, le=1.0, default=0.5)
    constitutional_compliance: float = Field(ge=0.0, le=1.0, default=1.0)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    voting_power: float = Field(ge=0.0, le=1.0, default=1.0)
    constitutional_hash: str = CONSTITUTIONAL_HASH
    
    @validator('constitutional_hash')
    def validate_constitutional_hash(cls, v):
        if v != CONSTITUTIONAL_HASH:
            raise ValueError(f"Invalid constitutional hash. Expected {CONSTITUTIONAL_HASH}")
        return v

class Proposal(BaseModel):
    """Consensus proposal"""
    proposal_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    proposer_id: str
    proposal_type: ProposalType
    title: str
    description: str
    content: Dict[str, Any]
    algorithm: ConsensusAlgorithm
    required_threshold: float = Field(ge=0.0, le=1.0, default=0.67)  # 2/3 majority
    timeout_seconds: int = Field(ge=60, default=300)  # 5 minutes default
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    priority: int = Field(ge=1, le=10, default=5)
    constitutional_impact: bool = False
    emergency: bool = False
    metadata: Dict[str, Any] = {}
    dependencies: List[str] = []  # Other proposal IDs this depends on
    
    def __post_init__(self):
        if not self.expires_at:
            self.expires_at = self.created_at + timedelta(seconds=self.timeout_seconds)

class Vote(BaseModel):
    """Vote on a proposal"""
    vote_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    proposal_id: str
    voter_id: str
    vote_type: VoteType
    weight: float = Field(ge=0.0, le=1.0, default=1.0)
    reasoning: Optional[str] = None
    conditions: Optional[Dict[str, Any]] = None  # For conditional votes
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    signature: Optional[str] = None
    constitutional_basis: Optional[str] = None  # For constitutional votes

class ConsensusRound(BaseModel):
    """A round of consensus for a proposal"""
    round_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    proposal_id: str
    round_number: int = Field(ge=1)
    algorithm: ConsensusAlgorithm
    leader_id: Optional[str] = None
    participants: List[str] = []
    votes: Dict[str, Vote] = {}
    status: ConsensusStatus = ConsensusStatus.PENDING
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    vote_tally: Dict[str, int] = {}
    threshold_met: bool = False
    constitutional_validation: bool = False

class ConsensusResult(BaseModel):
    """Final result of consensus process"""
    result_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    proposal_id: str
    status: ConsensusStatus
    final_decision: bool  # True if proposal accepted
    vote_summary: Dict[str, Any]
    winning_votes: int
    total_votes: int
    participation_rate: float = Field(ge=0.0, le=1.0)
    consensus_achieved_at: Optional[datetime] = None
    execution_scheduled: bool = False
    constitutional_compliance: bool = True
    audit_trail: List[Dict[str, Any]] = []

class ConstitutionalRule(BaseModel):
    """Constitutional rule for governance"""
    rule_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    category: str
    rule_text: str
    priority: int = Field(ge=1, le=10)
    enforced: bool = True
    applicable_proposal_types: List[ProposalType] = []
    violation_consequences: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_modified: datetime = Field(default_factory=datetime.utcnow)
    constitutional_hash: str = CONSTITUTIONAL_HASH

class Delegate(BaseModel):
    """Delegated voting representative"""
    delegate_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    delegator_ids: List[str] = []  # Who delegated to this delegate
    total_delegated_power: float = Field(ge=0.0, default=0.0)
    specializations: List[str] = []  # Areas of expertise
    performance_history: List[Dict[str, Any]] = []
    active: bool = True
    constitutional_alignment: float = Field(ge=0.0, le=1.0, default=1.0)

class VotingPool(BaseModel):
    """Pool for specific voting scenarios"""
    pool_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    eligible_voters: List[str] = []
    proposal_types: List[ProposalType] = []
    voting_rules: Dict[str, Any] = {}
    quorum_requirement: float = Field(ge=0.0, le=1.0, default=0.51)
    threshold_requirement: float = Field(ge=0.0, le=1.0, default=0.67)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    active: bool = True

class ConsensusMetrics(BaseModel):
    """Performance metrics for consensus"""
    total_proposals: int = 0
    successful_consensus: int = 0
    failed_consensus: int = 0
    timeout_consensus: int = 0
    vetoed_proposals: int = 0
    average_consensus_time_seconds: float = 0.0
    average_participation_rate: float = Field(ge=0.0, le=1.0, default=0.0)
    constitutional_violations: int = 0
    p95_consensus_time_seconds: float = 0.0
    throughput_proposals_per_hour: float = 0.0
    success_rate: float = Field(ge=0.0, le=1.0, default=0.0)

class ByzantineFaultTolerance(BaseModel):
    """Byzantine fault tolerance configuration"""
    max_byzantine_nodes: int = Field(ge=0)
    total_nodes: int = Field(ge=1)
    fault_tolerance_percentage: float = Field(ge=0.0, le=0.5)
    detection_mechanisms: List[str] = []
    recovery_protocols: List[str] = []
    quarantine_policy: Dict[str, Any] = {}

class StakingInfo(BaseModel):
    """Staking information for PoS consensus"""
    staker_id: str
    staked_amount: float = Field(ge=0.0)
    staking_duration_days: int = Field(ge=0)
    rewards_earned: float = Field(ge=0.0, default=0.0)
    slashing_history: List[Dict[str, Any]] = []
    delegation_received: float = Field(ge=0.0, default=0.0)
    validator_status: bool = False
    minimum_stake_required: float = Field(ge=0.0, default=1000.0)

class FederatedConsensusNode(BaseModel):
    """Node in federated consensus network"""
    node_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization: str
    trust_level: float = Field(ge=0.0, le=1.0, default=0.5)
    quorum_slices: List[List[str]] = []  # Nested quorum structure
    dependencies: List[str] = []
    last_agreement: Optional[datetime] = None
    agreement_history: List[Dict[str, Any]] = []

class ConsensusConfig(BaseModel):
    """Configuration for consensus engine"""
    algorithm: ConsensusAlgorithm
    parameters: Dict[str, Any] = {}
    node_requirements: Dict[str, Any] = {}
    timeout_config: Dict[str, int] = {}
    threshold_config: Dict[str, float] = {}
    constitutional_enforcement: bool = True
    byzantine_tolerance: bool = True
    max_proposal_size_kb: int = Field(ge=1, default=1024)
    max_concurrent_proposals: int = Field(ge=1, default=10)

class ConstitutionalChallenge(BaseModel):
    """Challenge to constitutional compliance"""
    challenge_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    challenger_id: str
    proposal_id: str
    constitutional_rule_ids: List[str]
    violation_description: str
    evidence: Dict[str, Any] = {}
    severity: str = "medium"  # low, medium, high, critical
    status: str = "pending"  # pending, under_review, upheld, dismissed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolution: Optional[Dict[str, Any]] = None

class EmergencyProtocol(BaseModel):
    """Emergency consensus protocol"""
    protocol_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    trigger_conditions: List[str]
    authorized_initiators: List[str]
    emergency_powers: List[str]
    time_limit_minutes: int = Field(ge=1, default=60)
    approval_threshold: float = Field(ge=0.0, le=1.0, default=0.9)
    constitutional_override: bool = False
    audit_requirements: List[str] = []

class ConsensusAuditTrail(BaseModel):
    """Audit trail for consensus decisions"""
    audit_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    proposal_id: str
    action_type: str
    actor_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    action_details: Dict[str, Any]
    before_state: Optional[Dict[str, Any]] = None
    after_state: Optional[Dict[str, Any]] = None
    constitutional_impact: bool = False
    signature: Optional[str] = None

class ReputationScore(BaseModel):
    """Reputation scoring for consensus participants"""
    participant_id: str
    current_score: float = Field(ge=0.0, le=1.0, default=0.5)
    voting_accuracy: float = Field(ge=0.0, le=1.0, default=0.5)
    participation_rate: float = Field(ge=0.0, le=1.0, default=0.0)
    constitutional_alignment: float = Field(ge=0.0, le=1.0, default=1.0)
    leadership_effectiveness: float = Field(ge=0.0, le=1.0, default=0.5)
    peer_ratings: List[Dict[str, Any]] = []
    historical_performance: List[Dict[str, Any]] = []
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class QuorumSlice(BaseModel):
    """Quorum slice for federated consensus"""
    slice_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    members: List[str]
    threshold: int = Field(ge=1)
    dependencies: List[str] = []
    trust_requirements: Dict[str, float] = {}
    active: bool = True

class ConsensusNetwork(BaseModel):
    """Network topology for consensus"""
    network_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    nodes: List[NodeIdentity] = []
    algorithm: ConsensusAlgorithm
    topology_type: str = "full_mesh"  # full_mesh, ring, star, hierarchical
    fault_tolerance: ByzantineFaultTolerance
    performance_requirements: Dict[str, float] = {}
    constitutional_governance: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_reconfiguration: datetime = Field(default_factory=datetime.utcnow)