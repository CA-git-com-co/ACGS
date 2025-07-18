"""
Multi-Agent Coordination Service
Constitutional Hash: cdd01ef066bc6cf2

FastAPI service for coordinating multiple agents using various patterns
including hierarchical, flat, and blackboard coordination.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import asyncio
import os

from .models import (
    AgentProfile, CoordinationTask, CoordinationPlan,
    CoordinationRequest, CoordinationResponse, AgentMessage,
    CoordinationMetrics, WorkloadDistribution, TeamFormation,
    AgentStatus, TaskStatus, CoordinationPattern,
    CONSTITUTIONAL_HASH
)
from .services import (
    MultiAgentCoordinator, AgentRegistry, TaskScheduler,
    WorkloadBalancer, ConflictResolver
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize coordinator
coordinator = MultiAgentCoordinator()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    logger.info("Starting Multi-Agent Coordination Service")
    logger.info(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    
    # Initialize sample agents for testing
    await initialize_sample_agents()
    
    # Start background tasks
    asyncio.create_task(health_monitor())
    asyncio.create_task(message_processor())
    
    yield
    
    logger.info("Shutting down Multi-Agent Coordination Service")

app = FastAPI(
    title="Multi-Agent Coordination Service",
    description="Coordinate multiple agents using various patterns",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def initialize_sample_agents():
    """Initialize sample agents for testing"""
    sample_agents = [
        AgentProfile(
            agent_name="coordinator-alpha",
            agent_type="coordinator",
            capabilities=[{
                "name": "task_coordination",
                "category": "coordination",
                "performance_score": 0.95,
                "max_concurrent_tasks": 10,
                "specializations": ["hierarchical", "team_formation"]
            }]
        ),
        AgentProfile(
            agent_name="worker-beta",
            agent_type="worker",
            capabilities=[{
                "name": "data_processing",
                "category": "computation",
                "performance_score": 0.90,
                "max_concurrent_tasks": 5,
                "specializations": ["analytics", "transformation"]
            }]
        ),
        AgentProfile(
            agent_name="worker-gamma",
            agent_type="worker",
            capabilities=[{
                "name": "policy_evaluation",
                "category": "governance",
                "performance_score": 0.88,
                "max_concurrent_tasks": 3,
                "specializations": ["constitutional_compliance", "risk_assessment"]
            }]
        ),
        AgentProfile(
            agent_name="specialist-delta",
            agent_type="specialist",
            capabilities=[{
                "name": "security_validation",
                "category": "security",
                "performance_score": 0.92,
                "max_concurrent_tasks": 4,
                "specializations": ["threat_detection", "compliance_verification"]
            }]
        ),
        AgentProfile(
            agent_name="monitor-epsilon",
            agent_type="monitor",
            capabilities=[{
                "name": "performance_monitoring",
                "category": "observability",
                "performance_score": 0.87,
                "max_concurrent_tasks": 8,
                "specializations": ["metrics_collection", "anomaly_detection"]
            }]
        )
    ]
    
    for agent in sample_agents:
        await coordinator.registry.register_agent(agent)
    
    logger.info(f"Initialized {len(sample_agents)} sample agents")

async def health_monitor():
    """Monitor agent health in background"""
    while True:
        try:
            # Update agent health metrics
            for agent_id, agent in coordinator.registry.agents.items():
                # Check if agent is responsive (simulated)
                time_since_heartbeat = (datetime.utcnow() - agent.last_heartbeat).total_seconds()
                
                if time_since_heartbeat > 60:  # 1 minute timeout
                    await coordinator.registry.update_agent_status(
                        agent_id, AgentStatus.OFFLINE
                    )
                elif time_since_heartbeat > 30:  # 30 second warning
                    logger.warning(f"Agent {agent_id} heartbeat delayed")
            
            await asyncio.sleep(10)  # Check every 10 seconds
            
        except Exception as e:
            logger.error(f"Health monitor error: {e}")
            await asyncio.sleep(30)

async def message_processor():
    """Process inter-agent messages"""
    while True:
        try:
            if not coordinator.message_queue.empty():
                message = await coordinator.message_queue.get()
                
                # Route message to recipients
                for recipient_id in message.recipient_ids:
                    if recipient_id in coordinator.registry.agents:
                        logger.info(
                            f"Delivered message {message.message_id} "
                            f"from {message.sender_id} to {recipient_id}"
                        )
            
            await asyncio.sleep(0.1)  # 100ms processing interval
            
        except Exception as e:
            logger.error(f"Message processor error: {e}")
            await asyncio.sleep(1)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    agent_count = len(coordinator.registry.agents)
    online_agents = sum(
        1 for agent in coordinator.registry.agents.values()
        if agent.status != AgentStatus.OFFLINE
    )
    
    return {
        "status": "healthy",
        "service": "multi-agent-coordination",
        "version": "1.0.0",
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "timestamp": datetime.utcnow().isoformat(),
        "agents": {
            "total": agent_count,
            "online": online_agents,
            "offline": agent_count - online_agents
        }
    }

@app.post("/api/v1/agents/register", response_model=Dict[str, Any])
async def register_agent(agent: AgentProfile):
    """Register a new agent"""
    success = await coordinator.registry.register_agent(agent)
    
    if not success:
        raise HTTPException(status_code=409, detail="Agent already registered")
    
    return {
        "agent_id": agent.agent_id,
        "status": "registered",
        "constitutional_hash": CONSTITUTIONAL_HASH
    }

@app.get("/api/v1/agents", response_model=List[AgentProfile])
async def list_agents(
    agent_type: Optional[str] = None,
    status: Optional[str] = None,
    capability: Optional[str] = None
):
    """List registered agents with optional filters"""
    agents = list(coordinator.registry.agents.values())
    
    # Apply filters
    if agent_type:
        agents = [a for a in agents if a.agent_type == agent_type]
    
    if status:
        agents = [a for a in agents if a.status == status]
    
    if capability:
        agents = await coordinator.registry.find_agents_by_capability(capability)
    
    return agents

@app.post("/api/v1/coordinate", response_model=CoordinationResponse)
async def coordinate_task(request: CoordinationRequest):
    """Coordinate a task among agents"""
    
    # Create coordination task
    task = CoordinationTask(
        task_type=request.tasks[0].get("type", "general"),
        priority=request.tasks[0].get("priority", "medium"),
        requirements=request.tasks[0].get("requirements", {}),
        constraints=request.constraints,
        deadline=request.deadline,
        constitutional_validation=request.constitutional_validation_required
    )
    
    # Add constitutional hash to requirements
    task.requirements["constitutional_hash"] = CONSTITUTIONAL_HASH
    
    # Coordinate task
    plan = await coordinator.coordinate(task, request.pattern)
    
    if not plan:
        return CoordinationResponse(
            request_id=request.request_id,
            status="failed",
            message="No suitable agents available",
            constitutional_compliance=False
        )
    
    # Get assigned agents
    assigned_agent_ids = list(plan.agent_assignments.keys())
    assigned_agents = [
        coordinator.registry.agents[aid] 
        for aid in assigned_agent_ids 
        if aid in coordinator.registry.agents
    ]
    
    return CoordinationResponse(
        request_id=request.request_id,
        plan=plan,
        status="success",
        message=f"Task coordinated using {request.pattern} pattern",
        assigned_agents=assigned_agents,
        constitutional_compliance=plan.constitutional_compliance_score >= 0.95,
        performance_estimate={
            "estimated_completion_ms": 1000,  # Placeholder
            "confidence": 0.85
        }
    )

@app.get("/api/v1/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Get task execution status"""
    task = coordinator.scheduler.active_tasks.get(task_id)
    
    if not task:
        # Check history
        for hist_task in coordinator.scheduler.task_history:
            if hist_task.task_id == task_id:
                task = hist_task
                break
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "task_id": task.task_id,
        "status": task.status,
        "assigned_agents": task.assigned_agents,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
        "results": task.results,
        "constitutional_validation": task.constitutional_validation
    }

@app.get("/api/v1/workload", response_model=WorkloadDistribution)
async def get_workload_distribution():
    """Get current workload distribution"""
    return await coordinator.balancer.analyze_workload()

@app.post("/api/v1/workload/rebalance")
async def rebalance_workload():
    """Trigger workload rebalancing"""
    distribution = await coordinator.balancer.analyze_workload()
    
    if not distribution.rebalancing_needed:
        return {"status": "not_needed", "message": "Workload is balanced"}
    
    success = await coordinator.balancer.rebalance_workload(distribution)
    
    return {
        "status": "success" if success else "failed",
        "overloaded_agents": distribution.overloaded_agents,
        "underutilized_agents": distribution.underutilized_agents
    }

@app.get("/api/v1/metrics", response_model=CoordinationMetrics)
async def get_metrics():
    """Get coordination metrics"""
    return await coordinator.get_metrics()

@app.post("/api/v1/messages/send")
async def send_message(message: AgentMessage):
    """Send message between agents"""
    # Validate sender exists
    if message.sender_id not in coordinator.registry.agents:
        raise HTTPException(status_code=404, detail="Sender not found")
    
    # Validate recipients exist
    for recipient_id in message.recipient_ids:
        if recipient_id not in coordinator.registry.agents:
            raise HTTPException(
                status_code=404, 
                detail=f"Recipient {recipient_id} not found"
            )
    
    # Queue message for processing
    await coordinator.message_queue.put(message)
    
    return {
        "message_id": message.message_id,
        "status": "queued",
        "recipients": len(message.recipient_ids)
    }

@app.post("/api/v1/teams/form")
async def form_team(
    task_requirements: Dict[str, Any],
    team_size: int = 3
):
    """Form a team for complex tasks"""
    # Create a task that requires team formation
    task = CoordinationTask(
        task_type="team_task",
        priority="high",
        requirements={
            **task_requirements,
            "team_size": team_size
        }
    )
    
    # Use team scheduling
    plan = await coordinator.scheduler._team_scheduling(task)
    
    if not plan:
        raise HTTPException(status_code=400, detail="Cannot form suitable team")
    
    # Create team formation object
    team_members = list(plan.agent_assignments.keys())
    team = TeamFormation(
        team_name=f"team-{task.task_id[:8]}",
        coordinator_id=team_members[0] if team_members else "",
        member_ids=team_members,
        team_capabilities=set(task_requirements.get("capabilities", [])),
        formation_strategy="capability_optimization",
        team_goals=task_requirements.get("goals", []),
        constitutional_alignment=plan.constitutional_compliance_score
    )
    
    return team

@app.get("/api/v1/patterns")
async def list_coordination_patterns():
    """List available coordination patterns"""
    return {
        "patterns": [
            {
                "name": pattern.value,
                "description": get_pattern_description(pattern),
                "suitable_for": get_pattern_use_cases(pattern)
            }
            for pattern in CoordinationPattern
        ]
    }

def get_pattern_description(pattern: CoordinationPattern) -> str:
    """Get description for coordination pattern"""
    descriptions = {
        CoordinationPattern.HIERARCHICAL: "Coordinator-worker hierarchy with centralized control",
        CoordinationPattern.FLAT: "Peer-to-peer coordination with distributed decision making",
        CoordinationPattern.BLACKBOARD: "Shared workspace where agents collaborate asynchronously",
        CoordinationPattern.CONTRACT_NET: "Task announcement and bidding protocol",
        CoordinationPattern.AUCTION: "Competitive bidding for task allocation",
        CoordinationPattern.TEAM: "Dynamic team formation with complementary skills"
    }
    return descriptions.get(pattern, "Unknown pattern")

def get_pattern_use_cases(pattern: CoordinationPattern) -> List[str]:
    """Get use cases for coordination pattern"""
    use_cases = {
        CoordinationPattern.HIERARCHICAL: [
            "Complex workflows with dependencies",
            "Tasks requiring oversight",
            "Sequential processing pipelines"
        ],
        CoordinationPattern.FLAT: [
            "Independent parallel tasks",
            "Load distribution",
            "Fault-tolerant processing"
        ],
        CoordinationPattern.BLACKBOARD: [
            "Collaborative problem solving",
            "Knowledge sharing",
            "Iterative refinement"
        ],
        CoordinationPattern.CONTRACT_NET: [
            "Dynamic task allocation",
            "Resource optimization",
            "Service discovery"
        ],
        CoordinationPattern.AUCTION: [
            "Competitive resource allocation",
            "Cost optimization",
            "Priority-based scheduling"
        ],
        CoordinationPattern.TEAM: [
            "Complex multi-skill tasks",
            "Collaborative projects",
            "Adaptive problem solving"
        ]
    }
    return use_cases.get(pattern, [])

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8008))
    uvicorn.run(app, host="0.0.0.0", port=port)