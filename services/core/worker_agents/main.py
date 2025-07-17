#!/usr/bin/env python3
"""
Worker Agents Service - Main Application
Constitutional Hash: cdd01ef066bc6cf2

This service manages specialized agent pools (Ethics, Legal, Operational) 
within the ACGS-2 constitutional AI governance framework providing 
domain-specific expertise for governance decisions.

Port: 8009
Performance Targets: P99 <2s for standard tasks, >500 tasks/second
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

import aioredis
import asyncpg
from fastapi import FastAPI, HTTPException, WebSocket, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Shared imports
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
class AgentType(str, Enum):
    ETHICS_AGENT = "ethics_agent"
    LEGAL_AGENT = "legal_agent"
    OPERATIONAL_AGENT = "operational_agent"
    CONSTITUTIONAL_AGENT = "constitutional_agent"
    COMPLIANCE_AGENT = "compliance_agent"
    RISK_ASSESSMENT_AGENT = "risk_assessment_agent"

class AgentStatus(str, Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"
    ERROR = "error"
    MAINTENANCE = "maintenance"

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

class EthicsCapabilities(str, Enum):
    BIAS_ASSESSMENT = "bias_assessment"
    FAIRNESS_EVALUATION = "fairness_evaluation"
    HARM_ANALYSIS = "harm_analysis"
    STAKEHOLDER_IMPACT = "stakeholder_impact"
    CULTURAL_SENSITIVITY = "cultural_sensitivity"

class LegalCapabilities(str, Enum):
    REGULATORY_COMPLIANCE = "regulatory_compliance"
    GDPR_ANALYSIS = "gdpr_analysis"
    CCPA_COMPLIANCE = "ccpa_compliance"
    EU_AI_ACT = "eu_ai_act"
    JURISDICTION_ANALYSIS = "jurisdiction_analysis"
    CONTRACT_COMPLIANCE = "contract_compliance"

class OperationalCapabilities(str, Enum):
    PERFORMANCE_ANALYSIS = "performance_analysis"
    SCALABILITY_ASSESSMENT = "scalability_assessment"
    RELIABILITY_EVALUATION = "reliability_evaluation"
    COST_OPTIMIZATION = "cost_optimization"
    DEPLOYMENT_VALIDATION = "deployment_validation"

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

class PerformanceMetrics(BaseModel):
    average_response_time: float = Field(default=0.0)
    success_rate: float = Field(ge=0, le=1, default=1.0)
    error_rate: float = Field(ge=0, le=1, default=0.0)
    throughput: float = Field(default=0.0)
    tasks_completed: int = Field(default=0)
    constitutional_compliance_rate: float = Field(ge=0, le=1, default=1.0)

class AgentCapability(BaseModel):
    capability_id: str
    name: str
    description: str
    proficiency_level: float = Field(ge=0, le=1)
    constitutional_certified: bool = Field(default=False)

class SpecializedAgent(BaseModel):
    agent_id: str = Field(default_factory=lambda: str(uuid4()))
    agent_type: AgentType
    specializations: List[str] = Field(default_factory=list)
    capabilities: List[AgentCapability] = Field(default_factory=list)
    current_capacity: int = Field(default=0)
    max_capacity: int = Field(default=5)
    performance_metrics: PerformanceMetrics = Field(default_factory=PerformanceMetrics)
    constitutional_compliance_score: float = Field(ge=0, le=1, default=1.0)
    status: AgentStatus = Field(default=AgentStatus.AVAILABLE)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TaskResult(BaseModel):
    result_id: str = Field(default_factory=lambda: str(uuid4()))
    task_id: str
    agent_id: str
    output_data: Dict[str, Any]
    confidence_score: float = Field(ge=0, le=1)
    constitutional_compliance: ConstitutionalValidation
    execution_time: float  # in seconds
    error_details: Optional[str] = None
    completed_at: datetime = Field(default_factory=datetime.utcnow)

class AgentTask(BaseModel):
    task_id: str = Field(default_factory=lambda: str(uuid4()))
    agent_id: Optional[str] = None
    task_type: str
    constitutional_context: ConstitutionalContext = Field(default_factory=ConstitutionalContext)
    input_data: Dict[str, Any]
    expected_output_schema: Optional[str] = None
    deadline: Optional[datetime] = None
    priority: Priority = Field(default=Priority.MEDIUM)
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    result: Optional[TaskResult] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class TaskSubmission(BaseModel):
    task_type: str
    input_data: Dict[str, Any]
    priority: Priority = Field(default=Priority.MEDIUM)
    deadline: Optional[datetime] = None
    required_agent_type: Optional[AgentType] = None
    constitutional_context: ConstitutionalContext = Field(default_factory=ConstitutionalContext)

class BiasAssessmentRequest(BaseModel):
    model_data: Dict[str, Any]
    protected_attributes: List[str]
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)

class BiasAssessmentResult(BaseModel):
    bias_score: float = Field(ge=0, le=1)
    protected_group_analysis: Dict[str, Any]
    recommendations: List[str]
    constitutional_compliance: ConstitutionalValidation

class RegulatoryComplianceRequest(BaseModel):
    regulations: List[str]  # GDPR, CCPA, EU_AI_ACT, HIPAA
    data_processing_description: str
    jurisdiction: str
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)

class ComplianceViolation(BaseModel):
    regulation: str
    violation_type: str
    severity: str
    description: str
    recommendation: str

class RegulatoryComplianceResult(BaseModel):
    compliance_score: float = Field(ge=0, le=1)
    violations: List[ComplianceViolation]
    recommendations: List[str]
    constitutional_compliance: ConstitutionalValidation

class PerformanceAnalysisRequest(BaseModel):
    system_metrics: Dict[str, Any]
    performance_targets: Dict[str, float]
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)

class PerformanceAnalysisResult(BaseModel):
    performance_score: float = Field(ge=0, le=1)
    bottlenecks: List[str]
    optimization_recommendations: List[str]
    constitutional_compliance: bool

# Specialized Agent Implementations
class EthicsAgent:
    """Specialized agent for ethical analysis and bias assessment."""
    
    def __init__(self, agent_info: SpecializedAgent):
        self.agent_info = agent_info
        self.capabilities = [
            EthicsCapabilities.BIAS_ASSESSMENT,
            EthicsCapabilities.FAIRNESS_EVALUATION,
            EthicsCapabilities.HARM_ANALYSIS,
            EthicsCapabilities.STAKEHOLDER_IMPACT,
            EthicsCapabilities.CULTURAL_SENSITIVITY
        ]
    
    async def assess_bias(self, request: BiasAssessmentRequest) -> BiasAssessmentResult:
        """Perform bias assessment analysis."""
        start_time = time.time()
        
        # Validate constitutional compliance
        if request.constitutional_hash != CONSTITUTIONAL_HASH:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid constitutional hash: {request.constitutional_hash}"
            )
        
        # Mock bias assessment (in production, this would use ML bias detection)
        bias_score = 0.15  # Lower is better
        
        protected_group_analysis = {}
        for attr in request.protected_attributes:
            # Simulate analysis of protected attribute
            protected_group_analysis[attr] = {
                "group_representation": 0.85,
                "outcome_parity": 0.92,
                "equalized_odds": 0.88,
                "demographic_parity": 0.90
            }
        
        recommendations = [
            "Implement fairness constraints during model training",
            "Use bias mitigation techniques for protected attributes",
            "Regular monitoring of model outcomes across demographic groups",
            "Establish bias remediation protocols"
        ]
        
        # Constitutional compliance validation
        constitutional_compliance = ConstitutionalValidation(
            is_compliant=bias_score < 0.2,  # Threshold for acceptable bias
            compliance_score=1.0 - bias_score,
            violations=[] if bias_score < 0.2 else ["Bias score exceeds constitutional threshold"],
            recommendations=recommendations
        )
        
        execution_time = time.time() - start_time
        
        # Update agent metrics
        self.agent_info.performance_metrics.tasks_completed += 1
        self.agent_info.performance_metrics.average_response_time = (
            (self.agent_info.performance_metrics.average_response_time * 
             (self.agent_info.performance_metrics.tasks_completed - 1) + execution_time) /
            self.agent_info.performance_metrics.tasks_completed
        )
        
        return BiasAssessmentResult(
            bias_score=bias_score,
            protected_group_analysis=protected_group_analysis,
            recommendations=recommendations,
            constitutional_compliance=constitutional_compliance
        )
    
    async def evaluate_fairness(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate fairness across demographic groups."""
        # Mock fairness evaluation
        fairness_metrics = {
            "demographic_parity": 0.92,
            "equalized_opportunity": 0.89,
            "equalized_odds": 0.87,
            "individual_fairness": 0.94
        }
        
        return {
            "fairness_score": sum(fairness_metrics.values()) / len(fairness_metrics),
            "fairness_metrics": fairness_metrics,
            "recommendations": [
                "Monitor fairness metrics continuously",
                "Implement fairness-aware algorithms",
                "Regular bias audits"
            ]
        }

class LegalAgent:
    """Specialized agent for legal analysis and regulatory compliance."""
    
    def __init__(self, agent_info: SpecializedAgent):
        self.agent_info = agent_info
        self.capabilities = [
            LegalCapabilities.REGULATORY_COMPLIANCE,
            LegalCapabilities.GDPR_ANALYSIS,
            LegalCapabilities.CCPA_COMPLIANCE,
            LegalCapabilities.EU_AI_ACT,
            LegalCapabilities.JURISDICTION_ANALYSIS,
            LegalCapabilities.CONTRACT_COMPLIANCE
        ]
    
    async def analyze_regulatory_compliance(
        self, 
        request: RegulatoryComplianceRequest
    ) -> RegulatoryComplianceResult:
        """Analyze regulatory compliance."""
        start_time = time.time()
        
        # Validate constitutional compliance
        if request.constitutional_hash != CONSTITUTIONAL_HASH:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid constitutional hash: {request.constitutional_hash}"
            )
        
        violations = []
        recommendations = []
        compliance_scores = []
        
        # Analyze each regulation
        for regulation in request.regulations:
            if regulation == "GDPR":
                # Mock GDPR analysis
                gdpr_score = 0.85
                compliance_scores.append(gdpr_score)
                
                if "data subject consent" not in request.data_processing_description.lower():
                    violations.append(ComplianceViolation(
                        regulation="GDPR",
                        violation_type="consent",
                        severity="high",
                        description="Missing explicit data subject consent mechanism",
                        recommendation="Implement clear consent collection and management"
                    ))
                
                recommendations.extend([
                    "Implement data subject rights (access, rectification, erasure)",
                    "Conduct privacy impact assessments",
                    "Establish lawful basis for processing"
                ])
            
            elif regulation == "CCPA":
                # Mock CCPA analysis
                ccpa_score = 0.90
                compliance_scores.append(ccpa_score)
                
                recommendations.extend([
                    "Implement consumer rights disclosure",
                    "Establish opt-out mechanisms",
                    "Data minimization practices"
                ])
            
            elif regulation == "EU_AI_ACT":
                # Mock EU AI Act analysis
                ai_act_score = 0.75
                compliance_scores.append(ai_act_score)
                
                violations.append(ComplianceViolation(
                    regulation="EU_AI_ACT",
                    violation_type="transparency",
                    severity="medium",
                    description="Insufficient AI system transparency documentation",
                    recommendation="Provide clear AI system documentation and risk assessment"
                ))
                
                recommendations.extend([
                    "Implement AI system risk assessment",
                    "Establish human oversight mechanisms",
                    "Ensure AI system transparency"
                ])
        
        overall_score = sum(compliance_scores) / len(compliance_scores) if compliance_scores else 0.0
        
        # Constitutional compliance validation
        constitutional_compliance = ConstitutionalValidation(
            is_compliant=len(violations) == 0 and overall_score >= 0.8,
            compliance_score=overall_score,
            violations=[v.description for v in violations],
            recommendations=recommendations
        )
        
        execution_time = time.time() - start_time
        
        # Update agent metrics
        self.agent_info.performance_metrics.tasks_completed += 1
        self.agent_info.performance_metrics.average_response_time = (
            (self.agent_info.performance_metrics.average_response_time * 
             (self.agent_info.performance_metrics.tasks_completed - 1) + execution_time) /
            self.agent_info.performance_metrics.tasks_completed
        )
        
        return RegulatoryComplianceResult(
            compliance_score=overall_score,
            violations=violations,
            recommendations=recommendations,
            constitutional_compliance=constitutional_compliance
        )

class OperationalAgent:
    """Specialized agent for operational analysis and performance validation."""
    
    def __init__(self, agent_info: SpecializedAgent):
        self.agent_info = agent_info
        self.capabilities = [
            OperationalCapabilities.PERFORMANCE_ANALYSIS,
            OperationalCapabilities.SCALABILITY_ASSESSMENT,
            OperationalCapabilities.RELIABILITY_EVALUATION,
            OperationalCapabilities.COST_OPTIMIZATION,
            OperationalCapabilities.DEPLOYMENT_VALIDATION
        ]
    
    async def analyze_performance(
        self, 
        request: PerformanceAnalysisRequest
    ) -> PerformanceAnalysisResult:
        """Analyze system performance requirements."""
        start_time = time.time()
        
        # Validate constitutional compliance
        if request.constitutional_hash != CONSTITUTIONAL_HASH:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid constitutional hash: {request.constitutional_hash}"
            )
        
        bottlenecks = []
        recommendations = []
        
        # Analyze performance metrics
        metrics = request.system_metrics
        targets = request.performance_targets
        
        performance_score = 1.0
        
        # Check latency
        if "latency_p99_ms" in metrics and "latency_p99_ms" in targets:
            actual_latency = metrics["latency_p99_ms"]
            target_latency = targets["latency_p99_ms"]
            
            if actual_latency > target_latency:
                bottlenecks.append(f"P99 latency {actual_latency}ms exceeds target {target_latency}ms")
                recommendations.append("Optimize query performance and implement caching")
                performance_score *= 0.8
        
        # Check throughput
        if "throughput_rps" in metrics and "throughput_rps" in targets:
            actual_throughput = metrics["throughput_rps"]
            target_throughput = targets["throughput_rps"]
            
            if actual_throughput < target_throughput:
                bottlenecks.append(f"Throughput {actual_throughput} RPS below target {target_throughput} RPS")
                recommendations.append("Implement horizontal scaling and load balancing")
                performance_score *= 0.9
        
        # Check memory usage
        if "memory_usage_percent" in metrics:
            memory_usage = metrics["memory_usage_percent"]
            if memory_usage > 80:
                bottlenecks.append(f"High memory usage: {memory_usage}%")
                recommendations.append("Optimize memory usage and implement garbage collection tuning")
                performance_score *= 0.85
        
        # Check error rate
        if "error_rate_percent" in metrics:
            error_rate = metrics["error_rate_percent"]
            if error_rate > 1:
                bottlenecks.append(f"High error rate: {error_rate}%")
                recommendations.append("Implement error handling and retry mechanisms")
                performance_score *= 0.7
        
        if not bottlenecks:
            recommendations.append("System performance meets constitutional requirements")
        
        execution_time = time.time() - start_time
        
        # Update agent metrics
        self.agent_info.performance_metrics.tasks_completed += 1
        self.agent_info.performance_metrics.average_response_time = (
            (self.agent_info.performance_metrics.average_response_time * 
             (self.agent_info.performance_metrics.tasks_completed - 1) + execution_time) /
            self.agent_info.performance_metrics.tasks_completed
        )
        
        return PerformanceAnalysisResult(
            performance_score=performance_score,
            bottlenecks=bottlenecks,
            optimization_recommendations=recommendations,
            constitutional_compliance=performance_score >= 0.8
        )

class AgentPoolManager:
    """Manages the pool of specialized agents."""
    
    def __init__(self):
        self.agents: Dict[str, SpecializedAgent] = {}
        self.ethics_agents: Dict[str, EthicsAgent] = {}
        self.legal_agents: Dict[str, LegalAgent] = {}
        self.operational_agents: Dict[str, OperationalAgent] = {}
        self.task_queue: List[AgentTask] = []
        self.performance_monitor = PerformanceMonitor() if SHARED_AVAILABLE else None
    
    async def initialize_default_agents(self):
        """Initialize default agent pool."""
        # Create default ethics agent
        ethics_agent_info = SpecializedAgent(
            agent_type=AgentType.ETHICS_AGENT,
            specializations=["bias_assessment", "fairness_evaluation", "harm_analysis"],
            max_capacity=10
        )
        ethics_agent = EthicsAgent(ethics_agent_info)
        
        self.agents[ethics_agent_info.agent_id] = ethics_agent_info
        self.ethics_agents[ethics_agent_info.agent_id] = ethics_agent
        
        # Create default legal agent
        legal_agent_info = SpecializedAgent(
            agent_type=AgentType.LEGAL_AGENT,
            specializations=["regulatory_compliance", "gdpr_analysis", "jurisdiction_analysis"],
            max_capacity=10
        )
        legal_agent = LegalAgent(legal_agent_info)
        
        self.agents[legal_agent_info.agent_id] = legal_agent_info
        self.legal_agents[legal_agent_info.agent_id] = legal_agent
        
        # Create default operational agent
        ops_agent_info = SpecializedAgent(
            agent_type=AgentType.OPERATIONAL_AGENT,
            specializations=["performance_analysis", "scalability_assessment", "deployment_validation"],
            max_capacity=10
        )
        ops_agent = OperationalAgent(ops_agent_info)
        
        self.agents[ops_agent_info.agent_id] = ops_agent_info
        self.operational_agents[ops_agent_info.agent_id] = ops_agent
        
        logger.info(f"Initialized agent pool with {len(self.agents)} agents")
    
    async def register_agent(self, agent_info: SpecializedAgent) -> bool:
        """Register a new agent in the pool."""
        self.agents[agent_info.agent_id] = agent_info
        
        # Create specialized agent instance
        if agent_info.agent_type == AgentType.ETHICS_AGENT:
            self.ethics_agents[agent_info.agent_id] = EthicsAgent(agent_info)
        elif agent_info.agent_type == AgentType.LEGAL_AGENT:
            self.legal_agents[agent_info.agent_id] = LegalAgent(agent_info)
        elif agent_info.agent_type == AgentType.OPERATIONAL_AGENT:
            self.operational_agents[agent_info.agent_id] = OperationalAgent(agent_info)
        
        logger.info(f"Registered agent {agent_info.agent_id} of type {agent_info.agent_type}")
        return True
    
    async def submit_task(self, task_submission: TaskSubmission) -> AgentTask:
        """Submit a task to the agent pool."""
        task = AgentTask(
            task_type=task_submission.task_type,
            input_data=task_submission.input_data,
            priority=task_submission.priority,
            deadline=task_submission.deadline,
            constitutional_context=task_submission.constitutional_context
        )
        
        # Find suitable agent
        suitable_agent = await self._find_suitable_agent(task, task_submission.required_agent_type)
        
        if suitable_agent:
            task.agent_id = suitable_agent.agent_id
            task.status = TaskStatus.ASSIGNED
            suitable_agent.current_capacity += 1
            suitable_agent.status = AgentStatus.BUSY if suitable_agent.current_capacity >= suitable_agent.max_capacity else AgentStatus.AVAILABLE
        else:
            # Add to queue if no suitable agent available
            self.task_queue.append(task)
        
        task.updated_at = datetime.utcnow()
        return task
    
    async def _find_suitable_agent(
        self, 
        task: AgentTask, 
        required_type: Optional[AgentType] = None
    ) -> Optional[SpecializedAgent]:
        """Find the most suitable agent for a task."""
        available_agents = [
            agent for agent in self.agents.values()
            if (agent.status == AgentStatus.AVAILABLE and 
                agent.current_capacity < agent.max_capacity and
                agent.constitutional_compliance_score >= 0.8)
        ]
        
        if required_type:
            available_agents = [a for a in available_agents if a.agent_type == required_type]
        
        if not available_agents:
            return None
        
        # Score agents based on suitability
        agent_scores = []
        for agent in available_agents:
            score = 0.0
            
            # Type matching
            if task.task_type in ["bias_assessment", "fairness_evaluation"] and agent.agent_type == AgentType.ETHICS_AGENT:
                score += 1.0
            elif task.task_type in ["regulatory_compliance", "legal_analysis"] and agent.agent_type == AgentType.LEGAL_AGENT:
                score += 1.0
            elif task.task_type in ["performance_analysis", "deployment_validation"] and agent.agent_type == AgentType.OPERATIONAL_AGENT:
                score += 1.0
            else:
                score += 0.5  # Can handle but not specialized
            
            # Load balancing
            load_factor = 1.0 - (agent.current_capacity / agent.max_capacity)
            score *= load_factor
            
            # Performance factor
            score *= agent.performance_metrics.success_rate
            
            agent_scores.append((agent, score))
        
        # Return agent with highest score
        if agent_scores:
            agent_scores.sort(key=lambda x: x[1], reverse=True)
            return agent_scores[0][0]
        
        return None
    
    async def get_agent(self, agent_id: str) -> Optional[SpecializedAgent]:
        """Get agent by ID."""
        return self.agents.get(agent_id)
    
    async def list_agents(
        self, 
        agent_type: Optional[AgentType] = None,
        available_only: bool = False
    ) -> List[SpecializedAgent]:
        """List agents with optional filtering."""
        agents = list(self.agents.values())
        
        if agent_type:
            agents = [a for a in agents if a.agent_type == agent_type]
        
        if available_only:
            agents = [a for a in agents if a.status == AgentStatus.AVAILABLE]
        
        return agents

# Global agent pool manager
agent_pool = AgentPoolManager()

# FastAPI Application Setup
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    logger.info("Starting Worker Agents Service")
    
    # Initialize default agent pool
    await agent_pool.initialize_default_agents()
    
    yield
    
    # Cleanup
    logger.info("Shutting down Worker Agents Service")

app = FastAPI(
    title="Worker Agents Service",
    description="ACGS-2 Specialized Agent Pool Service for constitutional AI governance",
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
        max_requests=500,
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
        "service": "worker-agents",
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "total_agents": len(agent_pool.agents),
        "available_agents": len([a for a in agent_pool.agents.values() if a.status == AgentStatus.AVAILABLE]),
        "queued_tasks": len(agent_pool.task_queue),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/metrics", include_in_schema=False)
async def metrics():
    """Prometheus metrics endpoint."""
    agent_counts = {}
    for agent_type in AgentType:
        count = len([a for a in agent_pool.agents.values() if a.agent_type == agent_type])
        agent_counts[f"wa_agents_{agent_type.value}_total"] = count
    
    status_counts = {}
    for status in AgentStatus:
        count = len([a for a in agent_pool.agents.values() if a.status == status])
        status_counts[f"wa_agents_{status.value}_total"] = count
    
    return {
        "wa_total_agents": len(agent_pool.agents),
        "wa_queued_tasks_total": len(agent_pool.task_queue),
        "wa_constitutional_hash": CONSTITUTIONAL_HASH,
        **agent_counts,
        **status_counts
    }

@app.get("/api/v1/agents", response_model=List[SpecializedAgent])
async def list_agents(
    agent_type: Optional[AgentType] = None,
    available_only: bool = False,
    current_user = Depends(get_current_user)
):
    """List all available agents."""
    agents = await agent_pool.list_agents(agent_type, available_only)
    return agents

@app.get("/api/v1/agents/{agent_id}", response_model=SpecializedAgent)
async def get_agent(
    agent_id: str,
    current_user = Depends(get_current_user)
):
    """Get agent details and status."""
    agent = await agent_pool.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@app.post("/api/v1/agents/register")
async def register_agent(
    agent_info: SpecializedAgent,
    current_user = Depends(get_current_user)
):
    """Register a new agent with the pool."""
    success = await agent_pool.register_agent(agent_info)
    return {"success": success, "agent_id": agent_info.agent_id}

@app.post("/api/v1/tasks", response_model=AgentTask)
async def submit_task(
    task_submission: TaskSubmission,
    current_user = Depends(get_current_user)
):
    """Submit task to agent pool."""
    task = await agent_pool.submit_task(task_submission)
    return task

@app.get("/api/v1/tasks/{task_id}")
async def get_task(
    task_id: str,
    current_user = Depends(get_current_user)
):
    """Get task status and results."""
    # In a real implementation, you would retrieve from a database
    return {"task_id": task_id, "status": "pending", "message": "Task tracking not yet implemented"}

# Specialized Agent Endpoints
@app.post("/api/v1/ethics/bias-assessment", response_model=BiasAssessmentResult)
async def ethics_bias_assessment(
    request: BiasAssessmentRequest,
    current_user = Depends(get_current_user)
):
    """Perform bias assessment analysis."""
    # Find available ethics agent
    ethics_agents = [a for a in agent_pool.ethics_agents.values()]
    if not ethics_agents:
        raise HTTPException(status_code=503, detail="No ethics agents available")
    
    # Use the first available ethics agent
    ethics_agent = ethics_agents[0]
    result = await ethics_agent.assess_bias(request)
    return result

@app.post("/api/v1/legal/regulatory-compliance", response_model=RegulatoryComplianceResult)
async def legal_regulatory_compliance(
    request: RegulatoryComplianceRequest,
    current_user = Depends(get_current_user)
):
    """Analyze regulatory compliance."""
    # Find available legal agent
    legal_agents = [a for a in agent_pool.legal_agents.values()]
    if not legal_agents:
        raise HTTPException(status_code=503, detail="No legal agents available")
    
    # Use the first available legal agent
    legal_agent = legal_agents[0]
    result = await legal_agent.analyze_regulatory_compliance(request)
    return result

@app.post("/api/v1/operational/performance-analysis", response_model=PerformanceAnalysisResult)
async def operational_performance_analysis(
    request: PerformanceAnalysisRequest,
    current_user = Depends(get_current_user)
):
    """Analyze system performance requirements."""
    # Find available operational agent
    ops_agents = [a for a in agent_pool.operational_agents.values()]
    if not ops_agents:
        raise HTTPException(status_code=503, detail="No operational agents available")
    
    # Use the first available operational agent
    ops_agent = ops_agents[0]
    result = await ops_agent.analyze_performance(request)
    return result

# WebSocket for real-time agent status updates
@app.websocket("/ws/agents")
async def agent_status_websocket(websocket: WebSocket):
    """WebSocket for real-time agent status updates."""
    await websocket.accept()
    
    try:
        while True:
            # Send agent status update
            agent_status = {
                "timestamp": datetime.utcnow().isoformat(),
                "total_agents": len(agent_pool.agents),
                "available_agents": len([a for a in agent_pool.agents.values() if a.status == AgentStatus.AVAILABLE]),
                "busy_agents": len([a for a in agent_pool.agents.values() if a.status == AgentStatus.BUSY]),
                "queued_tasks": len(agent_pool.task_queue)
            }
            
            await websocket.send_json(agent_status)
            await asyncio.sleep(5)  # Update every 5 seconds
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await websocket.close()

# Main execution
if __name__ == "__main__":
    import sys
    
    logger.info(f"Starting Worker Agents Service on port 8009")
    logger.info(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    logger.info(f"Shared components available: {SHARED_AVAILABLE}")
    
    # Configuration
    host = "0.0.0.0"
    port = 8009
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