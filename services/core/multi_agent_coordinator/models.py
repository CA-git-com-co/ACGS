"""
Multi-Agent Coordinator Domain Models
Constitutional Hash: cdd01ef066bc6cf2

Domain models for the Multi-Agent Coordinator service implementing 
constitutional AI governance coordination patterns.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, UUID
from uuid import uuid4

# Constitutional compliance constant
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Core Enums
class CoordinationType(str, Enum):
    """Types of coordination patterns available."""
    HIERARCHICAL = "hierarchical"
    CONSENSUS = "consensus"
    DEMOCRATIC = "democratic"
    EMERGENCY = "emergency"

class TaskType(str, Enum):
    """Types of tasks that can be coordinated."""
    ETHICS_REVIEW = "ethics_review"
    LEGAL_ANALYSIS = "legal_analysis"
    OPERATIONAL_VALIDATION = "operational_validation"
    CONSTITUTIONAL_COMPLIANCE = "constitutional_compliance"
    MULTI_STAKEHOLDER_DECISION = "multi_stakeholder_decision"
    POLICY_SYNTHESIS = "policy_synthesis"
    RISK_ASSESSMENT = "risk_assessment"

class TaskStatus(str, Enum):
    """Status of coordination tasks."""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ESCALATED = "escalated"
    CANCELLED = "cancelled"

class Priority(str, Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class AgentRole(str, Enum):
    """Roles that agents can fulfill in coordination."""
    ORCHESTRATOR = "orchestrator"
    DOMAIN_SPECIALIST = "domain_specialist"
    WORKER = "worker"
    ETHICS_AGENT = "ethics_agent"
    LEGAL_AGENT = "legal_agent"
    OPERATIONAL_AGENT = "operational_agent"
    CONSTITUTIONAL_AGENT = "constitutional_agent"
    COMPLIANCE_AGENT = "compliance_agent"

class AgentStatus(str, Enum):
    """Current status of agents."""
    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"
    ERROR = "error"
    MAINTENANCE = "maintenance"

class DecisionType(str, Enum):
    """Types of governance decisions."""
    APPROVE = "approve"
    REJECT = "reject"
    CONDITIONAL_APPROVE = "conditional_approve"
    ESCALATE = "escalate"
    DEFER = "defer"

class VoteType(str, Enum):
    """Types of votes in consensus."""
    APPROVE = "approve"
    REJECT = "reject"
    ABSTAIN = "abstain"
    CONDITIONAL = "conditional"

# Value Objects
@dataclass(frozen=True)
class ConstitutionalContext:
    """Constitutional context for coordination operations."""
    constitutional_hash: str = CONSTITUTIONAL_HASH
    compliance_level: str = "strict"
    principles: tuple = ()
    validation_required: bool = True
    escalation_threshold: float = 0.8

@dataclass(frozen=True)
class ConstitutionalValidation:
    """Result of constitutional compliance validation."""
    is_compliant: bool
    compliance_score: float
    violations: tuple = ()
    recommendations: tuple = ()
    validated_at: datetime = field(default_factory=datetime.utcnow)
    validator_id: Optional[str] = None

@dataclass(frozen=True)
class AgentCapability:
    """Capability that an agent possesses."""
    capability_id: str
    name: str
    description: str
    proficiency_level: float  # 0.0 to 1.0
    constitutional_certified: bool = False

@dataclass(frozen=True)
class PerformanceMetrics:
    """Performance metrics for agents and coordination."""
    average_response_time: float
    success_rate: float
    error_rate: float
    throughput: float
    availability: float
    constitutional_compliance_rate: float

# Entity Objects
@dataclass
class AgentInfo:
    """Information about an agent in the coordination system."""
    agent_id: str = field(default_factory=lambda: str(uuid4()))
    agent_type: AgentRole = AgentRole.WORKER
    status: AgentStatus = AgentStatus.AVAILABLE
    capabilities: List[AgentCapability] = field(default_factory=list)
    current_tasks: List[str] = field(default_factory=list)
    capacity: int = 5
    performance_metrics: Optional[PerformanceMetrics] = None
    constitutional_compliance_score: float = 1.0
    last_activity: datetime = field(default_factory=datetime.utcnow)
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_available(self) -> bool:
        """Check if agent is available for new tasks."""
        return (
            self.status == AgentStatus.AVAILABLE and
            len(self.current_tasks) < self.capacity and
            self.constitutional_compliance_score >= 0.8
        )

    def can_handle_task(self, task_type: TaskType) -> bool:
        """Check if agent can handle a specific task type."""
        if self.agent_type == AgentRole.ETHICS_AGENT:
            return task_type in [TaskType.ETHICS_REVIEW, TaskType.CONSTITUTIONAL_COMPLIANCE]
        elif self.agent_type == AgentRole.LEGAL_AGENT:
            return task_type in [TaskType.LEGAL_ANALYSIS, TaskType.CONSTITUTIONAL_COMPLIANCE]
        elif self.agent_type == AgentRole.OPERATIONAL_AGENT:
            return task_type in [TaskType.OPERATIONAL_VALIDATION, TaskType.RISK_ASSESSMENT]
        else:
            return True  # Generic agents can handle any task

@dataclass
class AgentTask:
    """A task assigned to agents in coordination."""
    id: str = field(default_factory=lambda: str(uuid4()))
    task_type: TaskType = TaskType.CONSTITUTIONAL_COMPLIANCE
    priority: Priority = Priority.MEDIUM
    constitutional_hash: str = CONSTITUTIONAL_HASH
    status: TaskStatus = TaskStatus.PENDING
    assigned_agents: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    requirements: List[str] = field(default_factory=list)
    deadline: Optional[datetime] = None
    estimated_duration: Optional[timedelta] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    result: Optional[Dict[str, Any]] = None
    error_details: Optional[str] = None
    constitutional_validation: Optional[ConstitutionalValidation] = None

    def is_overdue(self) -> bool:
        """Check if task is past its deadline."""
        if self.deadline:
            return datetime.utcnow() > self.deadline
        return False

    def get_age(self) -> timedelta:
        """Get the age of the task."""
        return datetime.utcnow() - self.created_at

@dataclass
class ConsensusVote:
    """A vote in a consensus decision process."""
    agent_id: str
    vote: VoteType
    confidence: float = 1.0  # 0.0 to 1.0
    reasoning: Optional[str] = None
    constitutional_assessment: Optional[ConstitutionalValidation] = None
    cast_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GovernanceDecision:
    """A governance decision made through coordination."""
    decision_id: str = field(default_factory=lambda: str(uuid4()))
    decision_type: DecisionType = DecisionType.APPROVE
    coordination_session_id: str = ""
    agent_votes: List[ConsensusVote] = field(default_factory=list)
    consensus_score: float = 0.0
    constitutional_compliance: Optional[ConstitutionalValidation] = None
    decision_rationale: str = ""
    decided_at: datetime = field(default_factory=datetime.utcnow)
    effective_at: Optional[datetime] = None
    audit_trail: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class AgentCoordination:
    """Coordination configuration for a group of agents."""
    coordination_id: str = field(default_factory=lambda: str(uuid4()))
    primary_agent: Optional[str] = None
    supporting_agents: List[str] = field(default_factory=list)
    coordination_type: CoordinationType = CoordinationType.CONSENSUS
    consensus_required: bool = True
    voting_threshold: float = 0.7
    timeout_duration: timedelta = field(default_factory=lambda: timedelta(minutes=30))
    constitutional_compliance: ConstitutionalContext = field(default_factory=ConstitutionalContext)
    created_at: datetime = field(default_factory=datetime.utcnow)
    status: str = "active"

@dataclass
class CoordinationSession:
    """A coordination session managing multiple agents and tasks."""
    session_id: str = field(default_factory=lambda: str(uuid4()))
    coordination_type: CoordinationType = CoordinationType.CONSENSUS
    primary_agent: Optional[str] = None
    participating_agents: List[str] = field(default_factory=list)
    tasks: List[AgentTask] = field(default_factory=list)
    decisions: List[GovernanceDecision] = field(default_factory=list)
    status: str = "active"
    consensus_threshold: float = 0.7
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    consensus_score: float = 0.0
    constitutional_compliance: Optional[ConstitutionalValidation] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_active(self) -> bool:
        """Check if coordination session is still active."""
        return self.status == "active" and self.completed_at is None

    def get_pending_tasks(self) -> List[AgentTask]:
        """Get all pending tasks in this session."""
        return [task for task in self.tasks if task.status == TaskStatus.PENDING]

    def get_completion_rate(self) -> float:
        """Get the completion rate of tasks in this session."""
        if not self.tasks:
            return 0.0
        completed = len([task for task in self.tasks if task.status == TaskStatus.COMPLETED])
        return completed / len(self.tasks)

@dataclass
class ConsensusResult:
    """Result of a consensus process."""
    consensus_reached: bool
    final_decision: DecisionType
    consensus_score: float
    participating_agents: List[str]
    votes: List[ConsensusVote]
    constitutional_compliance: ConstitutionalValidation
    decision_rationale: str = ""
    computed_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

# Aggregate Root
@dataclass
class MultiAgentOrchestration:
    """Root aggregate for multi-agent coordination."""
    orchestration_id: str = field(default_factory=lambda: str(uuid4()))
    coordination_sessions: List[CoordinationSession] = field(default_factory=list)
    registered_agents: List[AgentInfo] = field(default_factory=list)
    active_tasks: List[AgentTask] = field(default_factory=list)
    governance_decisions: List[GovernanceDecision] = field(default_factory=list)
    performance_metrics: Optional[PerformanceMetrics] = None
    constitutional_compliance_status: ConstitutionalValidation = field(
        default_factory=lambda: ConstitutionalValidation(
            is_compliant=True,
            compliance_score=1.0
        )
    )
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def get_available_agents(self) -> List[AgentInfo]:
        """Get all available agents."""
        return [agent for agent in self.registered_agents if agent.is_available()]

    def get_active_sessions(self) -> List[CoordinationSession]:
        """Get all active coordination sessions."""
        return [session for session in self.coordination_sessions if session.is_active()]

    def get_overdue_tasks(self) -> List[AgentTask]:
        """Get all overdue tasks."""
        return [task for task in self.active_tasks if task.is_overdue()]

# Domain Events
@dataclass(frozen=True)
class DomainEvent:
    """Base class for domain events."""
    event_id: str = field(default_factory=lambda: str(uuid4()))
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    constitutional_hash: str = CONSTITUTIONAL_HASH

@dataclass(frozen=True)
class AgentRegisteredEvent(DomainEvent):
    """Event raised when an agent is registered."""
    agent_id: str
    agent_type: AgentRole

@dataclass(frozen=True)
class TaskAssignedEvent(DomainEvent):
    """Event raised when a task is assigned to an agent."""
    task_id: str
    agent_id: str
    coordination_session_id: str

@dataclass(frozen=True)
class ConsensusReachedEvent(DomainEvent):
    """Event raised when consensus is reached."""
    session_id: str
    decision: DecisionType
    consensus_score: float

@dataclass(frozen=True)
class ConstitutionalViolationEvent(DomainEvent):
    """Event raised when constitutional violation is detected."""
    violation_type: str
    severity: str
    affected_session_id: Optional[str] = None
    affected_agent_id: Optional[str] = None

# Repository Interfaces (to be implemented by infrastructure layer)
class AgentRepository:
    """Repository interface for agent persistence."""
    
    async def save_agent(self, agent: AgentInfo) -> None:
        """Save an agent to the repository."""
        raise NotImplementedError
    
    async def get_agent(self, agent_id: str) -> Optional[AgentInfo]:
        """Get an agent by ID."""
        raise NotImplementedError
    
    async def list_agents(
        self, 
        status: Optional[AgentStatus] = None,
        agent_type: Optional[AgentRole] = None
    ) -> List[AgentInfo]:
        """List agents with optional filtering."""
        raise NotImplementedError

class CoordinationSessionRepository:
    """Repository interface for coordination session persistence."""
    
    async def save_session(self, session: CoordinationSession) -> None:
        """Save a coordination session."""
        raise NotImplementedError
    
    async def get_session(self, session_id: str) -> Optional[CoordinationSession]:
        """Get a coordination session by ID."""
        raise NotImplementedError
    
    async def list_active_sessions(self) -> List[CoordinationSession]:
        """List all active coordination sessions."""
        raise NotImplementedError

class TaskRepository:
    """Repository interface for task persistence."""
    
    async def save_task(self, task: AgentTask) -> None:
        """Save a task."""
        raise NotImplementedError
    
    async def get_task(self, task_id: str) -> Optional[AgentTask]:
        """Get a task by ID."""
        raise NotImplementedError
    
    async def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        assigned_agent: Optional[str] = None
    ) -> List[AgentTask]:
        """List tasks with optional filtering."""
        raise NotImplementedError

# Domain Services
class CoordinationDomainService:
    """Domain service for coordination logic."""
    
    @staticmethod
    def calculate_agent_suitability(agent: AgentInfo, task: AgentTask) -> float:
        """Calculate how suitable an agent is for a task."""
        if not agent.can_handle_task(task.task_type):
            return 0.0
        
        suitability = 1.0
        
        # Consider current load
        load_factor = 1.0 - (len(agent.current_tasks) / agent.capacity)
        suitability *= load_factor
        
        # Consider performance metrics
        if agent.performance_metrics:
            suitability *= agent.performance_metrics.success_rate
        
        # Consider constitutional compliance
        suitability *= agent.constitutional_compliance_score
        
        return min(1.0, max(0.0, suitability))
    
    @staticmethod
    def calculate_consensus_score(votes: List[ConsensusVote]) -> float:
        """Calculate consensus score from votes."""
        if not votes:
            return 0.0
        
        # Weight votes by confidence
        total_weight = sum(vote.confidence for vote in votes)
        if total_weight == 0:
            return 0.0
        
        approval_weight = sum(
            vote.confidence for vote in votes 
            if vote.vote == VoteType.APPROVE
        )
        
        return approval_weight / total_weight
    
    @staticmethod
    def validate_coordination_feasibility(
        agents: List[AgentInfo], 
        coordination_type: CoordinationType
    ) -> bool:
        """Validate if coordination is feasible with given agents."""
        if coordination_type == CoordinationType.CONSENSUS:
            return len(agents) >= 2
        elif coordination_type == CoordinationType.DEMOCRATIC:
            return len(agents) >= 3
        elif coordination_type == CoordinationType.HIERARCHICAL:
            return len(agents) >= 1
        elif coordination_type == CoordinationType.EMERGENCY:
            return len(agents) >= 1
        
        return False