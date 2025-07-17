#!/usr/bin/env python3
"""
Multi-Agent Coordinator Service - Main Application
Constitutional Hash: cdd01ef066bc6cf2

This service orchestrates collaboration between multiple AI agents within the 
ACGS-2 constitutional AI governance framework implementing a hybrid 
hierarchical-blackboard coordination model for complex governance requests.

Port: 8008
Performance Targets: P99 <5ms, >1000 coordination sessions/second
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, UUID
from uuid import uuid4

import aioredis
import asyncpg
from fastapi import FastAPI, HTTPException, WebSocket, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Shared imports - assuming constitutional compliance validation is available
try:
    from services.shared.middleware.tenant_middleware import (
        TenantContextMiddleware,
        get_tenant_context,
    )
    from services.shared.middleware.error_handling import setup_error_handlers
    from services.shared.security.enhanced_security_middleware import EnhancedSecurityMiddleware
    from services.shared.monitoring.performance_monitoring import PerformanceMonitor
    from services.shared.auth import get_current_user, require_auth
    SHARED_AVAILABLE = True
except ImportError:
    SHARED_AVAILABLE = False
    def get_current_user(): return {"user_id": "system"}
    def require_auth(): return lambda: None

# Constitutional hash constant
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Domain Models
class CoordinationType(str, Enum):
    HIERARCHICAL = "hierarchical"
    CONSENSUS = "consensus"
    DEMOCRATIC = "democratic"
    EMERGENCY = "emergency"

class TaskType(str, Enum):
    ETHICS_REVIEW = "ethics_review"
    LEGAL_ANALYSIS = "legal_analysis"
    OPERATIONAL_VALIDATION = "operational_validation"
    CONSTITUTIONAL_COMPLIANCE = "constitutional_compliance"
    MULTI_STAKEHOLDER_DECISION = "multi_stakeholder_decision"

class TaskStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ESCALATED = "escalated"

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class AgentRole(str, Enum):
    ORCHESTRATOR = "orchestrator"
    DOMAIN_SPECIALIST = "domain_specialist"
    WORKER = "worker"
    ETHICS_AGENT = "ethics_agent"
    LEGAL_AGENT = "legal_agent"
    OPERATIONAL_AGENT = "operational_agent"

class AgentStatus(str, Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"
    ERROR = "error"

# Pydantic Models
class ConstitutionalContext(BaseModel):
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)
    compliance_level: str = Field(default="strict")
    principles: List[str] = Field(default_factory=list)
    validation_required: bool = Field(default=True)

class ConstitutionalValidation(BaseModel):
    is_compliant: bool
    compliance_score: float = Field(ge=0, le=1)
    violations: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    validated_at: datetime = Field(default_factory=datetime.utcnow)

class AgentInfo(BaseModel):
    agent_id: str
    agent_type: AgentRole
    status: AgentStatus
    current_tasks: List[str] = Field(default_factory=list)
    capacity: int = Field(default=5)
    performance_score: float = Field(ge=0, le=1, default=1.0)
    last_activity: datetime = Field(default_factory=datetime.utcnow)

class AgentTask(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    task_type: TaskType
    priority: Priority
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    assigned_agents: List[str] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)
    deadline: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    result: Optional[Dict[str, Any]] = None

class CoordinationRequest(BaseModel):
    coordination_type: CoordinationType = Field(default=CoordinationType.CONSENSUS)
    task_type: TaskType
    priority: Priority = Field(default=Priority.MEDIUM)
    context: Dict[str, Any]
    required_agents: List[AgentRole] = Field(default_factory=list)
    deadline: Optional[datetime] = None
    constitutional_context: ConstitutionalContext = Field(default_factory=ConstitutionalContext)
    consensus_threshold: float = Field(ge=0.5, le=1.0, default=0.7)

class CoordinationSession(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid4()))
    coordination_type: CoordinationType
    primary_agent: Optional[str] = None
    participating_agents: List[str] = Field(default_factory=list)
    tasks: List[AgentTask] = Field(default_factory=list)
    status: str = Field(default="active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    consensus_score: float = Field(default=0.0)
    constitutional_compliance: Optional[ConstitutionalValidation] = None

class ConsensusVote(BaseModel):
    agent_id: str
    vote: str  # "approve", "reject", "abstain"
    confidence: float = Field(ge=0, le=1)
    reasoning: Optional[str] = None
    constitutional_assessment: Optional[ConstitutionalValidation] = None

class ConsensusResult(BaseModel):
    consensus_reached: bool
    final_decision: str
    consensus_score: float
    participating_agents: List[str]
    votes: List[ConsensusVote]
    constitutional_compliance: ConstitutionalValidation

# Core Coordinator Classes
@dataclass
class AgentCoordination:
    coordination_id: UUID = field(default_factory=uuid4)
    primary_agent: Optional[str] = None
    supporting_agents: List[str] = field(default_factory=list)
    coordination_type: CoordinationType = CoordinationType.CONSENSUS
    consensus_required: bool = True
    voting_threshold: float = 0.7
    constitutional_compliance: ConstitutionalContext = field(default_factory=ConstitutionalContext)

class ConsensusEngine:
    """Implements voting mechanisms and consensus calculation."""
    
    def __init__(self):
        self.active_votes: Dict[str, List[ConsensusVote]] = {}
        self.consensus_thresholds = {
            CoordinationType.CONSENSUS: 0.7,
            CoordinationType.DEMOCRATIC: 0.51,
            CoordinationType.HIERARCHICAL: 0.6,
            CoordinationType.EMERGENCY: 0.8
        }
    
    async def initiate_consensus(
        self, 
        session_id: str, 
        coordination_type: CoordinationType,
        threshold: float = None
    ) -> bool:
        """Initialize a consensus voting session."""
        actual_threshold = threshold or self.consensus_thresholds[coordination_type]
        self.active_votes[session_id] = []
        logger.info(f"Initiated consensus for session {session_id} with threshold {actual_threshold}")
        return True
    
    async def submit_vote(self, session_id: str, vote: ConsensusVote) -> bool:
        """Submit a vote for a consensus session."""
        if session_id not in self.active_votes:
            raise HTTPException(status_code=404, detail="Consensus session not found")
        
        # Validate constitutional compliance of vote
        if vote.constitutional_assessment and not vote.constitutional_assessment.is_compliant:
            logger.warning(f"Vote from {vote.agent_id} failed constitutional compliance")
            return False
        
        self.active_votes[session_id].append(vote)
        logger.info(f"Vote submitted by {vote.agent_id} for session {session_id}")
        return True
    
    async def calculate_consensus(
        self, 
        session_id: str, 
        coordination_type: CoordinationType
    ) -> ConsensusResult:
        """Calculate consensus from all submitted votes."""
        if session_id not in self.active_votes:
            raise HTTPException(status_code=404, detail="Consensus session not found")
        
        votes = self.active_votes[session_id]
        threshold = self.consensus_thresholds[coordination_type]
        
        # Calculate approval percentage
        total_votes = len(votes)
        if total_votes == 0:
            return ConsensusResult(
                consensus_reached=False,
                final_decision="no_votes",
                consensus_score=0.0,
                participating_agents=[],
                votes=[],
                constitutional_compliance=ConstitutionalValidation(
                    is_compliant=False,
                    compliance_score=0.0,
                    violations=["No votes received"]
                )
            )
        
        approval_votes = [v for v in votes if v.vote == "approve"]
        approval_rate = len(approval_votes) / total_votes
        
        # Weight by confidence scores
        weighted_score = sum(v.confidence for v in approval_votes) / total_votes
        
        consensus_reached = weighted_score >= threshold
        final_decision = "approved" if consensus_reached else "rejected"
        
        # Aggregate constitutional compliance
        constitutional_compliance = await self._aggregate_constitutional_compliance(votes)
        
        return ConsensusResult(
            consensus_reached=consensus_reached,
            final_decision=final_decision,
            consensus_score=weighted_score,
            participating_agents=[v.agent_id for v in votes],
            votes=votes,
            constitutional_compliance=constitutional_compliance
        )
    
    async def _aggregate_constitutional_compliance(
        self, 
        votes: List[ConsensusVote]
    ) -> ConstitutionalValidation:
        """Aggregate constitutional compliance from all votes."""
        all_violations = []
        all_recommendations = []
        compliance_scores = []
        
        for vote in votes:
            if vote.constitutional_assessment:
                compliance_scores.append(vote.constitutional_assessment.compliance_score)
                all_violations.extend(vote.constitutional_assessment.violations)
                all_recommendations.extend(vote.constitutional_assessment.recommendations)
        
        if not compliance_scores:
            return ConstitutionalValidation(
                is_compliant=True,
                compliance_score=1.0,
                violations=[],
                recommendations=[]
            )
        
        avg_compliance = sum(compliance_scores) / len(compliance_scores)
        is_compliant = avg_compliance >= 0.8 and len(all_violations) == 0
        
        return ConstitutionalValidation(
            is_compliant=is_compliant,
            compliance_score=avg_compliance,
            violations=list(set(all_violations)),
            recommendations=list(set(all_recommendations))
        )

class TaskScheduler:
    """Prioritizes and schedules tasks across agents."""
    
    def __init__(self):
        self.task_queue: List[AgentTask] = []
        self.agent_assignments: Dict[str, List[str]] = {}
    
    async def schedule_task(self, task: AgentTask, available_agents: List[AgentInfo]) -> Optional[str]:
        """Schedule a task to the most appropriate available agent."""
        if not available_agents:
            self.task_queue.append(task)
            return None
        
        # Find best agent based on type compatibility and load
        best_agent = await self._select_best_agent(task, available_agents)
        
        if best_agent:
            task.assigned_agents = [best_agent.agent_id]
            task.status = TaskStatus.ASSIGNED
            task.updated_at = datetime.utcnow()
            
            # Track assignment
            if best_agent.agent_id not in self.agent_assignments:
                self.agent_assignments[best_agent.agent_id] = []
            self.agent_assignments[best_agent.agent_id].append(task.id)
            
            logger.info(f"Task {task.id} assigned to agent {best_agent.agent_id}")
            return best_agent.agent_id
        
        self.task_queue.append(task)
        return None
    
    async def _select_best_agent(self, task: AgentTask, agents: List[AgentInfo]) -> Optional[AgentInfo]:
        """Select the best agent for a given task."""
        # Filter available agents
        available_agents = [a for a in agents if a.status == AgentStatus.AVAILABLE]
        
        if not available_agents:
            return None
        
        # Score agents based on type compatibility and current load
        agent_scores = []
        for agent in available_agents:
            score = 0.0
            
            # Type compatibility scoring
            if task.task_type == TaskType.ETHICS_REVIEW and agent.agent_type == AgentRole.ETHICS_AGENT:
                score += 1.0
            elif task.task_type == TaskType.LEGAL_ANALYSIS and agent.agent_type == AgentRole.LEGAL_AGENT:
                score += 1.0
            elif task.task_type == TaskType.OPERATIONAL_VALIDATION and agent.agent_type == AgentRole.OPERATIONAL_AGENT:
                score += 1.0
            else:
                score += 0.5  # Can handle but not specialized
            
            # Load balancing - prefer agents with fewer current tasks
            current_load = len(agent.current_tasks)
            load_factor = 1.0 - (current_load / agent.capacity)
            score *= load_factor
            
            # Performance factor
            score *= agent.performance_score
            
            agent_scores.append((agent, score))
        
        # Sort by score descending and return best agent
        agent_scores.sort(key=lambda x: x[1], reverse=True)
        return agent_scores[0][0] if agent_scores else None
    
    async def get_queued_tasks(self) -> List[AgentTask]:
        """Get all tasks currently in the queue."""
        return self.task_queue.copy()
    
    async def complete_task(self, task_id: str, agent_id: str) -> bool:
        """Mark a task as completed and remove from agent assignment."""
        if agent_id in self.agent_assignments:
            if task_id in self.agent_assignments[agent_id]:
                self.agent_assignments[agent_id].remove(task_id)
                logger.info(f"Task {task_id} completed by agent {agent_id}")
                return True
        return False

class ConstitutionalValidator:
    """Validates coordination decisions against constitutional principles."""
    
    def __init__(self):
        self.constitutional_hash = CONSTITUTIONAL_HASH
    
    async def validate_coordination_request(
        self, 
        request: CoordinationRequest
    ) -> ConstitutionalValidation:
        """Validate a coordination request for constitutional compliance."""
        violations = []
        recommendations = []
        compliance_score = 1.0
        
        # Validate constitutional hash
        if request.constitutional_context.constitutional_hash != self.constitutional_hash:
            violations.append(f"Invalid constitutional hash: {request.constitutional_context.constitutional_hash}")
            compliance_score -= 0.5
        
        # Validate coordination type appropriateness
        if request.priority == Priority.EMERGENCY and request.coordination_type != CoordinationType.EMERGENCY:
            recommendations.append("Consider using emergency coordination for critical priority tasks")
            compliance_score -= 0.1
        
        # Validate consensus threshold
        if request.coordination_type == CoordinationType.CONSENSUS and request.consensus_threshold < 0.6:
            violations.append("Consensus threshold too low for constitutional governance")
            compliance_score -= 0.2
        
        is_compliant = len(violations) == 0 and compliance_score >= 0.8
        
        return ConstitutionalValidation(
            is_compliant=is_compliant,
            compliance_score=max(0.0, compliance_score),
            violations=violations,
            recommendations=recommendations
        )
    
    async def validate_task(self, task: AgentTask) -> ConstitutionalValidation:
        """Validate a task for constitutional compliance."""
        violations = []
        recommendations = []
        compliance_score = 1.0
        
        # Validate constitutional hash
        if task.constitutional_hash != self.constitutional_hash:
            violations.append(f"Task has invalid constitutional hash: {task.constitutional_hash}")
            compliance_score -= 0.5
        
        # Validate task urgency and type alignment
        if task.priority == Priority.EMERGENCY and task.task_type != TaskType.CONSTITUTIONAL_COMPLIANCE:
            recommendations.append("Emergency tasks should include constitutional compliance review")
            compliance_score -= 0.1
        
        is_compliant = len(violations) == 0 and compliance_score >= 0.8
        
        return ConstitutionalValidation(
            is_compliant=is_compliant,
            compliance_score=max(0.0, compliance_score),
            violations=violations,
            recommendations=recommendations
        )

class CoordinationOrchestrator:
    """Main orchestrator for multi-agent coordination."""
    
    def __init__(self):
        self.active_sessions: Dict[str, CoordinationSession] = {}
        self.registered_agents: Dict[str, AgentInfo] = {}
        self.consensus_engine = ConsensusEngine()
        self.task_scheduler = TaskScheduler()
        self.constitutional_validator = ConstitutionalValidator()
        self.performance_monitor = PerformanceMonitor() if SHARED_AVAILABLE else None
    
    async def register_agent(self, agent_info: AgentInfo) -> bool:
        """Register a new agent with the coordinator."""
        self.registered_agents[agent_info.agent_id] = agent_info
        logger.info(f"Registered agent {agent_info.agent_id} of type {agent_info.agent_type}")
        return True
    
    async def create_coordination_session(
        self, 
        request: CoordinationRequest
    ) -> CoordinationSession:
        """Create a new coordination session."""
        start_time = time.time()
        
        # Validate constitutional compliance
        validation = await self.constitutional_validator.validate_coordination_request(request)
        if not validation.is_compliant:
            raise HTTPException(
                status_code=400, 
                detail=f"Constitutional compliance violation: {validation.violations}"
            )
        
        # Create session
        session = CoordinationSession(
            coordination_type=request.coordination_type,
            constitutional_compliance=validation
        )
        
        # Select and assign agents
        required_agents = await self._select_agents_for_request(request)
        session.participating_agents = [agent.agent_id for agent in required_agents]
        
        # Create initial task
        task = AgentTask(
            task_type=request.task_type,
            priority=request.priority,
            context=request.context,
            deadline=request.deadline
        )
        
        # Validate and schedule task
        task_validation = await self.constitutional_validator.validate_task(task)
        if not task_validation.is_compliant:
            raise HTTPException(
                status_code=400,
                detail=f"Task constitutional compliance violation: {task_validation.violations}"
            )
        
        assigned_agent = await self.task_scheduler.schedule_task(task, required_agents)
        session.tasks.append(task)
        
        # Store session
        self.active_sessions[session.session_id] = session
        
        # Record performance metrics
        if self.performance_monitor:
            await self.performance_monitor.record_operation(
                "create_coordination_session",
                time.time() - start_time,
                {"session_id": session.session_id, "coordination_type": request.coordination_type}
            )
        
        logger.info(f"Created coordination session {session.session_id}")
        return session
    
    async def _select_agents_for_request(self, request: CoordinationRequest) -> List[AgentInfo]:
        """Select appropriate agents for a coordination request."""
        available_agents = [
            agent for agent in self.registered_agents.values()
            if agent.status == AgentStatus.AVAILABLE
        ]
        
        selected_agents = []
        
        # Add specifically requested agent types
        for required_role in request.required_agents:
            matching_agents = [a for a in available_agents if a.agent_type == required_role]
            if matching_agents:
                # Select best performing agent of this type
                best_agent = max(matching_agents, key=lambda a: a.performance_score)
                selected_agents.append(best_agent)
        
        # If no specific agents requested, select based on task type
        if not selected_agents:
            if request.task_type == TaskType.ETHICS_REVIEW:
                ethics_agents = [a for a in available_agents if a.agent_type == AgentRole.ETHICS_AGENT]
                if ethics_agents:
                    selected_agents.append(max(ethics_agents, key=lambda a: a.performance_score))
            
            elif request.task_type == TaskType.LEGAL_ANALYSIS:
                legal_agents = [a for a in available_agents if a.agent_type == AgentRole.LEGAL_AGENT]
                if legal_agents:
                    selected_agents.append(max(legal_agents, key=lambda a: a.performance_score))
            
            elif request.task_type == TaskType.OPERATIONAL_VALIDATION:
                ops_agents = [a for a in available_agents if a.agent_type == AgentRole.OPERATIONAL_AGENT]
                if ops_agents:
                    selected_agents.append(max(ops_agents, key=lambda a: a.performance_score))
        
        # For consensus coordination, ensure we have multiple agents
        if request.coordination_type == CoordinationType.CONSENSUS and len(selected_agents) < 2:
            # Add additional agents for consensus
            remaining_agents = [a for a in available_agents if a not in selected_agents]
            needed = min(3 - len(selected_agents), len(remaining_agents))
            selected_agents.extend(remaining_agents[:needed])
        
        return selected_agents
    
    async def get_session(self, session_id: str) -> Optional[CoordinationSession]:
        """Get a coordination session by ID."""
        return self.active_sessions.get(session_id)
    
    async def initiate_consensus(
        self, 
        session_id: str, 
        threshold: Optional[float] = None
    ) -> bool:
        """Initiate consensus voting for a session."""
        session = await self.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return await self.consensus_engine.initiate_consensus(
            session_id, 
            session.coordination_type, 
            threshold
        )
    
    async def submit_vote(self, session_id: str, vote: ConsensusVote) -> bool:
        """Submit a vote for consensus in a session."""
        session = await self.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if vote.agent_id not in session.participating_agents:
            raise HTTPException(status_code=403, detail="Agent not participating in session")
        
        return await self.consensus_engine.submit_vote(session_id, vote)
    
    async def get_consensus_result(self, session_id: str) -> ConsensusResult:
        """Get consensus result for a session."""
        session = await self.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        result = await self.consensus_engine.calculate_consensus(
            session_id, 
            session.coordination_type
        )
        
        # Update session with consensus result
        session.consensus_score = result.consensus_score
        session.constitutional_compliance = result.constitutional_compliance
        
        return result

# Global coordinator instance
coordinator = CoordinationOrchestrator()

# FastAPI Application Setup
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    logger.info("Starting Multi-Agent Coordinator Service")
    
    # Initialize connections (Redis, PostgreSQL)
    try:
        # Here you would initialize actual database connections
        # For now, we'll use in-memory coordination
        logger.info("Initialized coordination infrastructure")
    except Exception as e:
        logger.error(f"Failed to initialize infrastructure: {e}")
        raise
    
    yield
    
    # Cleanup
    logger.info("Shutting down Multi-Agent Coordinator Service")

app = FastAPI(
    title="Multi-Agent Coordinator Service",
    description="ACGS-2 Multi-Agent Coordination Service for constitutional AI governance",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if SHARED_AVAILABLE:
    app.add_middleware(
        EnhancedSecurityMiddleware,
        max_requests=1000,
        window_seconds=60,
        max_request_size=10 * 1024 * 1024
    )
    app.add_middleware(TenantContextMiddleware)
    setup_error_handlers(app)

# API Endpoints
@app.get("/health", include_in_schema=False)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "multi-agent-coordinator",
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "active_sessions": len(coordinator.active_sessions),
        "registered_agents": len(coordinator.registered_agents),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/metrics", include_in_schema=False)
async def metrics():
    """Prometheus metrics endpoint."""
    metrics_data = {
        "mac_active_sessions_total": len(coordinator.active_sessions),
        "mac_registered_agents_total": len(coordinator.registered_agents),
        "mac_queued_tasks_total": len(await coordinator.task_scheduler.get_queued_tasks()),
        "mac_constitutional_hash": CONSTITUTIONAL_HASH,
    }
    
    # Add agent status breakdown
    agent_status_counts = {}
    for agent in coordinator.registered_agents.values():
        status = agent.status.value
        agent_status_counts[f"mac_agents_{status}_total"] = agent_status_counts.get(f"mac_agents_{status}_total", 0) + 1
    
    metrics_data.update(agent_status_counts)
    return metrics_data

@app.post("/api/v1/coordination", response_model=CoordinationSession)
async def create_coordination(
    request: CoordinationRequest,
    current_user = Depends(get_current_user)
):
    """Create a new agent coordination session."""
    try:
        session = await coordinator.create_coordination_session(request)
        return session
    except Exception as e:
        logger.error(f"Failed to create coordination session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/coordination/{session_id}", response_model=CoordinationSession)
async def get_coordination(
    session_id: str,
    current_user = Depends(get_current_user)
):
    """Get coordination session details."""
    session = await coordinator.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@app.post("/api/v1/coordination/{session_id}/consensus")
async def initiate_consensus(
    session_id: str,
    threshold: Optional[float] = None,
    current_user = Depends(get_current_user)
):
    """Initiate consensus voting for a session."""
    result = await coordinator.initiate_consensus(session_id, threshold)
    return {"success": result, "session_id": session_id}

@app.post("/api/v1/coordination/{session_id}/vote")
async def submit_vote(
    session_id: str,
    vote: ConsensusVote,
    current_user = Depends(get_current_user)
):
    """Submit a vote for consensus in a session."""
    result = await coordinator.submit_vote(session_id, vote)
    return {"success": result, "session_id": session_id, "agent_id": vote.agent_id}

@app.get("/api/v1/coordination/{session_id}/consensus", response_model=ConsensusResult)
async def get_consensus_result(
    session_id: str,
    current_user = Depends(get_current_user)
):
    """Get consensus result for a session."""
    return await coordinator.get_consensus_result(session_id)

@app.post("/api/v1/agents/register")
async def register_agent(
    agent_info: AgentInfo,
    current_user = Depends(get_current_user)
):
    """Register a new agent with the coordinator."""
    result = await coordinator.register_agent(agent_info)
    return {"success": result, "agent_id": agent_info.agent_id}

@app.get("/api/v1/agents")
async def list_agents(
    status: Optional[AgentStatus] = None,
    agent_type: Optional[AgentRole] = None,
    current_user = Depends(get_current_user)
):
    """List registered agents with optional filtering."""
    agents = list(coordinator.registered_agents.values())
    
    if status:
        agents = [a for a in agents if a.status == status]
    
    if agent_type:
        agents = [a for a in agents if a.agent_type == agent_type]
    
    return {"agents": agents, "total": len(agents)}

@app.get("/api/v1/agents/{agent_id}", response_model=AgentInfo)
async def get_agent(
    agent_id: str,
    current_user = Depends(get_current_user)
):
    """Get agent details and status."""
    agent = coordinator.registered_agents.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@app.put("/api/v1/agents/{agent_id}/status")
async def update_agent_status(
    agent_id: str,
    status: AgentStatus,
    current_user = Depends(get_current_user)
):
    """Update agent status."""
    agent = coordinator.registered_agents.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent.status = status
    agent.last_activity = datetime.utcnow()
    
    return {"success": True, "agent_id": agent_id, "new_status": status}

@app.get("/api/v1/tasks")
async def list_tasks(
    status: Optional[TaskStatus] = None,
    task_type: Optional[TaskType] = None,
    current_user = Depends(get_current_user)
):
    """List tasks across all sessions."""
    all_tasks = []
    for session in coordinator.active_sessions.values():
        all_tasks.extend(session.tasks)
    
    if status:
        all_tasks = [t for t in all_tasks if t.status == status]
    
    if task_type:
        all_tasks = [t for t in all_tasks if t.task_type == task_type]
    
    return {"tasks": all_tasks, "total": len(all_tasks)}

# WebSocket endpoints for real-time coordination updates
@app.websocket("/ws/coordination/{session_id}")
async def coordination_websocket(websocket: WebSocket, session_id: str):
    """WebSocket for real-time coordination updates."""
    await websocket.accept()
    
    try:
        while True:
            # Check for session updates and send to client
            session = await coordinator.get_session(session_id)
            if session:
                await websocket.send_json({
                    "type": "session_update",
                    "session": session.dict(),
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            await asyncio.sleep(1)  # Update interval
    
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}")
    finally:
        await websocket.close()

@app.websocket("/ws/agents/{agent_id}")
async def agent_websocket(websocket: WebSocket, agent_id: str):
    """WebSocket for real-time agent status updates."""
    await websocket.accept()
    
    try:
        while True:
            agent = coordinator.registered_agents.get(agent_id)
            if agent:
                await websocket.send_json({
                    "type": "agent_update",
                    "agent": agent.dict(),
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            await asyncio.sleep(1)  # Update interval
    
    except Exception as e:
        logger.error(f"WebSocket error for agent {agent_id}: {e}")
    finally:
        await websocket.close()

# Main execution
if __name__ == "__main__":
    import sys
    
    logger.info(f"Starting Multi-Agent Coordinator Service on port 8008")
    logger.info(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    logger.info(f"Shared components available: {SHARED_AVAILABLE}")
    
    # Configuration
    host = "0.0.0.0"
    port = 8008
    reload = "--reload" in sys.argv
    log_level = "info"
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level,
        access_log=True
    )