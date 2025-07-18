"""
Worker Agents Models
Constitutional Hash: cdd01ef066bc6cf2

Data models for worker agent implementation including task execution,
skill management, and performance tracking.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from pydantic import BaseModel, Field, validator
import uuid

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

class WorkerType(str, Enum):
    """Types of worker agents"""
    GENERAL_PURPOSE = "general_purpose"
    SPECIALIZED = "specialized"
    COMPUTATIONAL = "computational"
    ANALYTICAL = "analytical"
    POLICY_EXECUTOR = "policy_executor"
    DATA_PROCESSOR = "data_processor"
    VALIDATOR = "validator"

class TaskType(str, Enum):
    """Types of tasks workers can execute"""
    DATA_ANALYSIS = "data_analysis"
    POLICY_EVALUATION = "policy_evaluation"
    COMPUTATION = "computation"
    VALIDATION = "validation"
    TRANSFORMATION = "transformation"
    AGGREGATION = "aggregation"
    MONITORING = "monitoring"
    REPORTING = "reporting"

class ExecutionStatus(str, Enum):
    """Task execution status"""
    QUEUED = "queued"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"

class SkillLevel(str, Enum):
    """Skill proficiency levels"""
    NOVICE = "novice"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    MASTER = "master"

class ResourceType(str, Enum):
    """Resource types for workers"""
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    GPU = "gpu"
    CUSTOM = "custom"

class Skill(BaseModel):
    """Worker skill definition"""
    name: str
    category: str
    level: SkillLevel
    proficiency_score: float = Field(ge=0.0, le=1.0)
    experience_hours: int = Field(ge=0)
    certifications: List[str] = []
    last_used: Optional[datetime] = None
    improvement_rate: float = Field(ge=0.0, le=1.0, default=0.1)

class ResourceRequirement(BaseModel):
    """Resource requirement specification"""
    resource_type: ResourceType
    amount: float
    unit: str
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    priority: str = "normal"  # low, normal, high, critical

class TaskExecution(BaseModel):
    """Task execution tracking"""
    execution_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str
    worker_id: str
    task_type: TaskType
    status: ExecutionStatus = ExecutionStatus.QUEUED
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    resource_usage: Dict[str, float] = {}
    progress_percentage: float = Field(ge=0.0, le=100.0, default=0.0)
    error_message: Optional[str] = None
    retry_count: int = Field(ge=0, default=0)
    max_retries: int = Field(ge=0, default=3)
    constitutional_validation: bool = False
    results: Optional[Dict[str, Any]] = None

class WorkerCapability(BaseModel):
    """Worker capability definition"""
    capability_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    supported_task_types: List[TaskType]
    required_skills: List[str]
    resource_requirements: List[ResourceRequirement]
    performance_metrics: Dict[str, float] = {}
    constitutional_compliance: bool = True
    throughput_estimate: float = Field(ge=0.0, default=1.0)  # tasks per second
    accuracy_rate: float = Field(ge=0.0, le=1.0, default=0.95)

class WorkerProfile(BaseModel):
    """Complete worker agent profile"""
    worker_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    worker_type: WorkerType
    version: str = "1.0.0"
    skills: List[Skill] = []
    capabilities: List[WorkerCapability] = []
    max_concurrent_tasks: int = Field(ge=1, default=3)
    current_task_count: int = Field(ge=0, default=0)
    available_resources: Dict[str, float] = {}
    performance_history: List[Dict[str, Any]] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: datetime = Field(default_factory=datetime.utcnow)
    status: str = "idle"  # idle, busy, maintenance, offline
    constitutional_hash: str = CONSTITUTIONAL_HASH
    
    @validator('constitutional_hash')
    def validate_constitutional_hash(cls, v):
        if v != CONSTITUTIONAL_HASH:
            raise ValueError(f"Invalid constitutional hash. Expected {CONSTITUTIONAL_HASH}")
        return v

class TaskRequest(BaseModel):
    """Request for task execution"""
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_type: TaskType
    priority: int = Field(ge=1, le=10, default=5)
    payload: Dict[str, Any]
    resource_requirements: List[ResourceRequirement] = []
    timeout_seconds: Optional[int] = None
    retry_policy: Dict[str, Any] = {}
    constitutional_validation_required: bool = True
    context: Dict[str, Any] = {}
    deadline: Optional[datetime] = None

class TaskResult(BaseModel):
    """Task execution result"""
    execution_id: str
    task_id: str
    worker_id: str
    status: ExecutionStatus
    results: Optional[Dict[str, Any]] = None
    error_details: Optional[Dict[str, Any]] = None
    performance_metrics: Dict[str, float] = {}
    resource_consumption: Dict[str, float] = {}
    constitutional_compliance: bool = True
    quality_score: float = Field(ge=0.0, le=1.0, default=1.0)
    execution_time_ms: float = Field(ge=0.0)

class WorkerMetrics(BaseModel):
    """Performance metrics for worker"""
    worker_id: str
    total_tasks_completed: int = 0
    total_tasks_failed: int = 0
    average_execution_time_ms: float = 0.0
    success_rate: float = Field(ge=0.0, le=1.0, default=1.0)
    resource_efficiency: Dict[str, float] = {}
    skill_improvement: Dict[str, float] = {}
    uptime_percentage: float = Field(ge=0.0, le=100.0, default=100.0)
    constitutional_compliance_rate: float = Field(ge=0.0, le=1.0, default=1.0)
    p95_latency_ms: float = 0.0
    throughput_rps: float = 0.0

class WorkerPool(BaseModel):
    """Pool of worker agents"""
    pool_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    worker_ids: List[str] = []
    pool_type: str = "dynamic"  # static, dynamic, elastic
    min_workers: int = Field(ge=1, default=1)
    max_workers: int = Field(ge=1, default=10)
    current_workers: int = Field(ge=0, default=0)
    scaling_policy: Dict[str, Any] = {}
    load_balancing_strategy: str = "round_robin"  # round_robin, least_loaded, random
    health_check_interval: int = Field(ge=1, default=30)

class LoadBalancingStrategy(BaseModel):
    """Load balancing configuration"""
    strategy_name: str
    parameters: Dict[str, Any] = {}
    weight_factors: Dict[str, float] = {}
    performance_bias: float = Field(ge=0.0, le=1.0, default=0.7)
    availability_bias: float = Field(ge=0.0, le=1.0, default=0.3)

class ScalingPolicy(BaseModel):
    """Auto-scaling policy for worker pools"""
    policy_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    scale_up_threshold: float = Field(ge=0.0, le=1.0, default=0.8)
    scale_down_threshold: float = Field(ge=0.0, le=1.0, default=0.2)
    scale_up_cooldown_seconds: int = Field(ge=0, default=300)
    scale_down_cooldown_seconds: int = Field(ge=0, default=600)
    max_scale_up_step: int = Field(ge=1, default=2)
    max_scale_down_step: int = Field(ge=1, default=1)
    metrics: List[str] = ["cpu_utilization", "queue_depth", "response_time"]

class TaskQueue(BaseModel):
    """Task queue management"""
    queue_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    priority_levels: int = Field(ge=1, default=5)
    max_queue_size: int = Field(ge=1, default=1000)
    current_size: int = Field(ge=0, default=0)
    processing_strategy: str = "priority_fifo"  # fifo, lifo, priority_fifo, shortest_first
    retry_policy: Dict[str, Any] = {}
    dead_letter_queue: bool = False

class HealthStatus(BaseModel):
    """Worker health status"""
    worker_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    is_healthy: bool = True
    cpu_usage: float = Field(ge=0.0, le=100.0, default=0.0)
    memory_usage: float = Field(ge=0.0, le=100.0, default=0.0)
    disk_usage: float = Field(ge=0.0, le=100.0, default=0.0)
    active_tasks: int = Field(ge=0, default=0)
    queue_depth: int = Field(ge=0, default=0)
    last_task_completion: Optional[datetime] = None
    error_rate: float = Field(ge=0.0, le=1.0, default=0.0)
    response_time_ms: float = Field(ge=0.0, default=0.0)

class WorkerCommand(BaseModel):
    """Command to control worker behavior"""
    command_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    worker_id: str
    command_type: str  # start, stop, pause, resume, restart, update
    parameters: Dict[str, Any] = {}
    issued_by: str
    issued_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    status: str = "pending"  # pending, executing, completed, failed

class SkillAssessment(BaseModel):
    """Assessment of worker skills"""
    assessment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    worker_id: str
    skill_name: str
    assessment_type: str = "performance_based"  # test_based, performance_based, peer_review
    score: float = Field(ge=0.0, le=1.0)
    assessor: str
    assessment_date: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = None
    improvement_recommendations: List[str] = []

class WorkerTraining(BaseModel):
    """Training program for workers"""
    training_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    worker_id: str
    skill_target: str
    training_type: str = "online"  # online, simulation, mentoring
    duration_hours: int = Field(ge=1)
    progress_percentage: float = Field(ge=0.0, le=100.0, default=0.0)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    effectiveness_score: Optional[float] = Field(ge=0.0, le=1.0, default=None)

class ResourceAllocation(BaseModel):
    """Resource allocation for task execution"""
    allocation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    worker_id: str
    task_id: str
    allocated_resources: Dict[str, float]
    allocation_time: datetime = Field(default_factory=datetime.utcnow)
    expected_duration_seconds: int = Field(ge=0)
    actual_duration_seconds: Optional[int] = None
    efficiency_score: Optional[float] = Field(ge=0.0, le=1.0, default=None)

class CollaborationRequest(BaseModel):
    """Request for worker collaboration"""
    collaboration_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    requesting_worker_id: str
    target_worker_ids: List[str]
    collaboration_type: str  # assistance, knowledge_sharing, joint_execution
    task_context: Dict[str, Any]
    urgency: str = "normal"  # low, normal, high, critical
    expected_duration_minutes: Optional[int] = None
    constitutional_approval_required: bool = True