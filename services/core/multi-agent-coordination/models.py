"""
Multi-Agent Coordination Models
Constitutional Hash: cdd01ef066bc6cf2

Defines data models for multi-agent coordination patterns including
hierarchical, flat, and blackboard-based coordination.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from enum import Enum
from pydantic import BaseModel, Field, validator
import uuid

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

class AgentType(str, Enum):
    """Types of agents in the system"""
    COORDINATOR = "coordinator"
    WORKER = "worker"
    SPECIALIST = "specialist"
    MONITOR = "monitor"
    VALIDATOR = "validator"

class AgentStatus(str, Enum):
    """Agent operational status"""
    IDLE = "idle"
    BUSY = "busy"
    COORDINATING = "coordinating"
    EXECUTING = "executing"
    VALIDATING = "validating"
    ERROR = "error"
    OFFLINE = "offline"

class CoordinationPattern(str, Enum):
    """Multi-agent coordination patterns"""
    HIERARCHICAL = "hierarchical"
    FLAT = "flat"
    BLACKBOARD = "blackboard"
    CONTRACT_NET = "contract_net"
    AUCTION = "auction"
    TEAM = "team"

class TaskPriority(str, Enum):
    """Task priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    BACKGROUND = "background"

class TaskStatus(str, Enum):
    """Task execution status"""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class AgentCapability(BaseModel):
    """Agent capability definition"""
    name: str
    category: str
    performance_score: float = Field(ge=0.0, le=1.0)
    max_concurrent_tasks: int = Field(ge=1)
    specializations: List[str] = []
    constitutional_compliance: bool = True

class AgentProfile(BaseModel):
    """Complete agent profile"""
    agent_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_name: str
    agent_type: AgentType
    status: AgentStatus = AgentStatus.IDLE
    capabilities: List[AgentCapability]
    current_tasks: List[str] = []
    performance_metrics: Dict[str, float] = {}
    last_heartbeat: datetime = Field(default_factory=datetime.utcnow)
    constitutional_hash: str = CONSTITUTIONAL_HASH
    
    @validator('constitutional_hash')
    def validate_constitutional_hash(cls, v):
        if v != CONSTITUTIONAL_HASH:
            raise ValueError(f"Invalid constitutional hash. Expected {CONSTITUTIONAL_HASH}")
        return v

class CoordinationTask(BaseModel):
    """Task to be coordinated among agents"""
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_type: str
    priority: TaskPriority
    status: TaskStatus = TaskStatus.PENDING
    requirements: Dict[str, Any]
    constraints: Dict[str, Any] = {}
    assigned_agents: List[str] = []
    subtasks: List[str] = []
    parent_task_id: Optional[str] = None
    deadline: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completion_criteria: Dict[str, Any] = {}
    results: Optional[Dict[str, Any]] = None
    constitutional_validation: bool = False

class CoordinationPlan(BaseModel):
    """Execution plan for coordinated tasks"""
    plan_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    pattern: CoordinationPattern
    tasks: List[CoordinationTask]
    agent_assignments: Dict[str, List[str]]  # agent_id -> task_ids
    dependencies: Dict[str, List[str]]  # task_id -> dependent_task_ids
    estimated_completion_time: Optional[datetime] = None
    optimization_metrics: Dict[str, float] = {}
    constitutional_compliance_score: float = Field(ge=0.0, le=1.0, default=0.0)

class AgentMessage(BaseModel):
    """Inter-agent communication message"""
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str
    recipient_ids: List[str]
    message_type: str
    content: Dict[str, Any]
    priority: TaskPriority = TaskPriority.MEDIUM
    requires_response: bool = False
    timeout_seconds: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    constitutional_hash: str = CONSTITUTIONAL_HASH

class CoordinationMetrics(BaseModel):
    """Performance metrics for coordination"""
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    average_completion_time_ms: float = 0.0
    agent_utilization: Dict[str, float] = {}
    coordination_efficiency: float = Field(ge=0.0, le=1.0, default=0.0)
    constitutional_compliance_rate: float = Field(ge=0.0, le=1.0, default=1.0)
    p99_latency_ms: float = 0.0
    throughput_rps: float = 0.0

class WorkloadDistribution(BaseModel):
    """Workload distribution among agents"""
    agent_workloads: Dict[str, int]  # agent_id -> task_count
    load_balance_score: float = Field(ge=0.0, le=1.0)
    overloaded_agents: List[str] = []
    underutilized_agents: List[str] = []
    rebalancing_needed: bool = False

class CoordinationRequest(BaseModel):
    """Request for multi-agent coordination"""
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    pattern: CoordinationPattern
    tasks: List[Dict[str, Any]]
    constraints: Dict[str, Any] = {}
    optimization_goals: List[str] = ["efficiency", "reliability"]
    deadline: Optional[datetime] = None
    requester_id: str
    context: Dict[str, Any] = {}
    constitutional_validation_required: bool = True

class CoordinationResponse(BaseModel):
    """Response to coordination request"""
    request_id: str
    plan: Optional[CoordinationPlan] = None
    status: str
    message: str
    estimated_completion_time: Optional[datetime] = None
    assigned_agents: List[AgentProfile] = []
    constitutional_compliance: bool = True
    performance_estimate: Dict[str, float] = {}

class TeamFormation(BaseModel):
    """Dynamic team formation for complex tasks"""
    team_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    team_name: str
    coordinator_id: str
    member_ids: List[str]
    team_capabilities: Set[str]
    formation_strategy: str
    team_goals: List[str]
    performance_history: List[Dict[str, Any]] = []
    constitutional_alignment: float = Field(ge=0.0, le=1.0, default=1.0)

class BlackboardEntry(BaseModel):
    """Entry in blackboard coordination system"""
    entry_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    author_id: str
    entry_type: str
    content: Dict[str, Any]
    visibility: str = "public"  # public, team, private
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    tags: List[str] = []
    subscribers: List[str] = []
    version: int = 1
    constitutional_validated: bool = False

class NegotiationProtocol(BaseModel):
    """Protocol for agent negotiations"""
    protocol_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    protocol_type: str  # contract_net, auction, bargaining
    participants: List[str]
    subject: Dict[str, Any]
    rules: Dict[str, Any]
    current_state: str
    bids: List[Dict[str, Any]] = []
    winner: Optional[str] = None
    settlement: Optional[Dict[str, Any]] = None
    constitutional_constraints: Dict[str, Any] = {}

class ConflictResolution(BaseModel):
    """Conflict resolution between agents"""
    conflict_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conflicting_agents: List[str]
    conflict_type: str
    conflict_subject: Dict[str, Any]
    resolution_strategy: str
    mediator_id: Optional[str] = None
    proposed_solutions: List[Dict[str, Any]] = []
    selected_solution: Optional[Dict[str, Any]] = None
    constitutional_override: bool = False

class AgentHealth(BaseModel):
    """Agent health and monitoring data"""
    agent_id: str
    status: AgentStatus
    cpu_usage: float = Field(ge=0.0, le=100.0)
    memory_usage_mb: float = Field(ge=0.0)
    active_connections: int = Field(ge=0)
    task_queue_size: int = Field(ge=0)
    error_rate: float = Field(ge=0.0, le=1.0)
    response_time_ms: float = Field(ge=0.0)
    last_error: Optional[str] = None
    constitutional_compliance_status: bool = True