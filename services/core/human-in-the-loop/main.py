"""
Human-in-the-Loop Service
Constitutional Hash: cdd01ef066bc6cf2

FastAPI service for human oversight, intervention, and collaboration
in AI governance systems with constitutional compliance.
"""

from fastapi import (
    FastAPI,
    HTTPException,
    BackgroundTasks,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
import asyncio
import json
import os
from collections import defaultdict

from .models import (
    InterventionType,
    InterventionStatus,
    UserRole,
    InterventionRequest,
    InterventionResponse,
    User,
    WorkflowStep,
    OversightWorkflow,
    CONSTITUTIONAL_HASH,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global storage
hitl_storage = {
    "intervention_requests": {},
    "intervention_responses": {},
    "users": {},
    "workflows": {},
    "active_sessions": set(),
    "metrics": defaultdict(int),
}

# WebSocket connections
active_connections: Dict[str, WebSocket] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    logger.info("Starting Human-in-the-Loop Service")
    logger.info(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")

    # Initialize sample users and workflows
    await initialize_sample_users()
    await initialize_sample_workflows()

    # Start background tasks
    asyncio.create_task(process_timeouts())
    asyncio.create_task(escalation_monitor())

    yield

    logger.info("Shutting down Human-in-the-Loop Service")


app = FastAPI(
    title="Human-in-the-Loop Service",
    description="Human oversight and intervention for AI governance",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def initialize_sample_users():
    """Initialize sample users"""
    sample_users = [
        User(
            username="admin_alpha",
            email="admin@acgs-2.ai",
            full_name="Administrative Alpha",
            role=UserRole.ADMINISTRATOR,
            specializations=["system_administration", "policy_management"],
            constitutional_expertise=0.9,
        ),
        User(
            username="constitutional_expert_beta",
            email="constitutional@acgs-2.ai",
            full_name="Constitutional Expert Beta",
            role=UserRole.CONSTITUTIONAL_EXPERT,
            specializations=["constitutional_law", "governance", "compliance"],
            constitutional_expertise=0.98,
        ),
        User(
            username="domain_expert_gamma",
            email="domain@acgs-2.ai",
            full_name="Domain Expert Gamma",
            role=UserRole.DOMAIN_EXPERT,
            specializations=["artificial_intelligence", "machine_learning", "ethics"],
            constitutional_expertise=0.7,
        ),
        User(
            username="operator_delta",
            email="operator@acgs-2.ai",
            full_name="Operator Delta",
            role=UserRole.OPERATOR,
            specializations=["system_operations", "monitoring"],
            constitutional_expertise=0.6,
        ),
        User(
            username="auditor_epsilon",
            email="auditor@acgs-2.ai",
            full_name="Auditor Epsilon",
            role=UserRole.AUDITOR,
            specializations=["compliance_auditing", "risk_assessment"],
            constitutional_expertise=0.85,
        ),
    ]

    for user in sample_users:
        hitl_storage["users"][user.user_id] = user

    logger.info(f"Initialized {len(sample_users)} sample users")


async def initialize_sample_workflows():
    """Initialize sample oversight workflows"""
    sample_workflows = [
        OversightWorkflow(
            name="Constitutional Amendment Review",
            description="Multi-stage review for constitutional amendments",
            trigger_conditions=["constitutional_amendment_proposed"],
            steps=[
                WorkflowStep(
                    step_name="Constitutional Expert Review",
                    required_role=UserRole.CONSTITUTIONAL_EXPERT,
                    timeout_minutes=120,
                ),
                WorkflowStep(
                    step_name="Administrator Approval",
                    required_role=UserRole.ADMINISTRATOR,
                    timeout_minutes=60,
                ),
                WorkflowStep(
                    step_name="Auditor Verification",
                    required_role=UserRole.AUDITOR,
                    timeout_minutes=30,
                    optional=True,
                ),
            ],
            constitutional_requirements=["supermajority_consensus", "hash_validation"],
        ),
        OversightWorkflow(
            name="Emergency Response Protocol",
            description="Rapid response for emergency situations",
            trigger_conditions=["emergency_intervention_required"],
            steps=[
                WorkflowStep(
                    step_name="Emergency Responder Assessment",
                    required_role=UserRole.EMERGENCY_RESPONDER,
                    timeout_minutes=15,
                ),
                WorkflowStep(
                    step_name="Administrator Override",
                    required_role=UserRole.ADMINISTRATOR,
                    timeout_minutes=10,
                    parallel=True,
                ),
            ],
        ),
        OversightWorkflow(
            name="Policy Review Standard",
            description="Standard review process for policy changes",
            trigger_conditions=["policy_change_proposed"],
            steps=[
                WorkflowStep(
                    step_name="Domain Expert Analysis",
                    required_role=UserRole.DOMAIN_EXPERT,
                    timeout_minutes=90,
                ),
                WorkflowStep(
                    step_name="Constitutional Compliance Check",
                    required_role=UserRole.CONSTITUTIONAL_EXPERT,
                    timeout_minutes=60,
                ),
                WorkflowStep(
                    step_name="Final Approval",
                    required_role=UserRole.ADMINISTRATOR,
                    timeout_minutes=30,
                ),
            ],
            constitutional_requirements=[
                "constitutional_compliance",
                "performance_impact_assessment",
            ],
        ),
    ]

    for workflow in sample_workflows:
        hitl_storage["workflows"][workflow.workflow_id] = workflow

    logger.info(f"Initialized {len(sample_workflows)} sample workflows")


async def process_timeouts():
    """Process expired intervention requests"""
    while True:
        try:
            current_time = datetime.utcnow()
            expired_requests = []

            for request_id, request in hitl_storage["intervention_requests"].items():
                if request.expires_at and request.expires_at <= current_time:
                    expired_requests.append(request_id)

            for request_id in expired_requests:
                request = hitl_storage["intervention_requests"][request_id]
                logger.warning(f"Intervention request {request_id} expired")

                # Create timeout response
                timeout_response = InterventionResponse(
                    request_id=request_id,
                    responder_id="system",
                    responder_role=UserRole.ADMINISTRATOR,
                    status=InterventionStatus.TIMEOUT,
                    reasoning="Request expired without human response",
                    confidence_level=0.0,
                )

                hitl_storage["intervention_responses"][
                    timeout_response.response_id
                ] = timeout_response
                hitl_storage["metrics"]["timeouts"] += 1

                # Notify connected clients
                await broadcast_notification(
                    {
                        "type": "timeout",
                        "request_id": request_id,
                        "message": f"Intervention request '{request.title}' has expired",
                    }
                )

            await asyncio.sleep(30)  # Check every 30 seconds

        except Exception as e:
            logger.error(f"Timeout processor error: {e}")
            await asyncio.sleep(60)


async def escalation_monitor():
    """Monitor for escalation conditions"""
    while True:
        try:
            # Check for high-priority pending requests
            high_priority_pending = [
                req
                for req in hitl_storage["intervention_requests"].values()
                if req.priority >= 8
                and not any(
                    resp.request_id == req.request_id
                    for resp in hitl_storage["intervention_responses"].values()
                )
            ]

            # Escalate if pending too long
            for request in high_priority_pending:
                time_pending = datetime.utcnow() - request.created_at
                if time_pending > timedelta(minutes=30):  # 30 minutes for high priority
                    logger.warning(
                        f"Escalating high-priority request: {request.request_id}"
                    )

                    await broadcast_notification(
                        {
                            "type": "escalation",
                            "request_id": request.request_id,
                            "priority": request.priority,
                            "time_pending_minutes": time_pending.total_seconds() / 60,
                        }
                    )

            await asyncio.sleep(300)  # Check every 5 minutes

        except Exception as e:
            logger.error(f"Escalation monitor error: {e}")
            await asyncio.sleep(300)


async def broadcast_notification(notification: Dict[str, Any]):
    """Broadcast notification to all connected clients"""
    if active_connections:
        message = json.dumps(notification)
        disconnected = []

        for user_id, websocket in active_connections.items():
            try:
                await websocket.send_text(message)
            except:
                disconnected.append(user_id)

        # Clean up disconnected clients
        for user_id in disconnected:
            if user_id in active_connections:
                del active_connections[user_id]


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    total_users = len(hitl_storage["users"])
    active_users = sum(1 for u in hitl_storage["users"].values() if u.active)
    pending_requests = len(
        [
            r
            for r in hitl_storage["intervention_requests"].values()
            if not any(
                resp.request_id == r.request_id
                for resp in hitl_storage["intervention_responses"].values()
            )
        ]
    )

    return {
        "status": "healthy",
        "service": "human-in-the-loop",
        "version": "1.0.0",
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "timestamp": datetime.utcnow().isoformat(),
        "statistics": {
            "total_users": total_users,
            "active_users": active_users,
            "pending_requests": pending_requests,
            "active_connections": len(active_connections),
            "total_workflows": len(hitl_storage["workflows"]),
        },
    }


# User Management
@app.post("/api/v1/users/register", response_model=Dict[str, Any])
async def register_user(user: User):
    """Register a new user"""
    hitl_storage["users"][user.user_id] = user

    return {
        "user_id": user.user_id,
        "status": "registered",
        "role": user.role.value,
        "constitutional_hash": CONSTITUTIONAL_HASH,
    }


@app.get("/api/v1/users", response_model=List[User])
async def list_users(role: Optional[str] = None, active_only: bool = True):
    """List users with optional filters"""
    users = list(hitl_storage["users"].values())

    if role:
        try:
            role_enum = UserRole(role)
            users = [u for u in users if u.role == role_enum]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid user role")

    if active_only:
        users = [u for u in users if u.active]

    return users


@app.get("/api/v1/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    """Get specific user details"""
    if user_id not in hitl_storage["users"]:
        raise HTTPException(status_code=404, detail="User not found")

    return hitl_storage["users"][user_id]


# Intervention Management
@app.post("/api/v1/interventions/request", response_model=Dict[str, Any])
async def request_intervention(request: InterventionRequest):
    """Request human intervention"""

    # Set expiration if not provided
    if not request.expires_at:
        request.expires_at = request.created_at + timedelta(
            minutes=request.timeout_minutes
        )

    # Constitutional impact requires constitutional expert
    if (
        request.constitutional_impact
        and UserRole.CONSTITUTIONAL_EXPERT not in request.required_roles
    ):
        request.required_roles.append(UserRole.CONSTITUTIONAL_EXPERT)

    # Emergency requests get priority and administrator involvement
    if request.emergency:
        request.priority = max(request.priority, 9)
        if UserRole.ADMINISTRATOR not in request.required_roles:
            request.required_roles.append(UserRole.ADMINISTRATOR)

    # Store request
    hitl_storage["intervention_requests"][request.request_id] = request
    hitl_storage["metrics"]["total_requests"] += 1

    # Auto-assign if possible
    await auto_assign_request(request)

    # Notify connected users
    await broadcast_notification(
        {
            "type": "new_request",
            "request_id": request.request_id,
            "intervention_type": request.intervention_type.value,
            "priority": request.priority,
            "emergency": request.emergency,
            "title": request.title,
            "required_roles": [role.value for role in request.required_roles],
        }
    )

    logger.info(
        f"Intervention requested: {request.request_id} ({request.intervention_type.value})"
    )

    return {
        "request_id": request.request_id,
        "status": "submitted",
        "priority": request.priority,
        "expires_at": request.expires_at.isoformat(),
        "assigned_to": request.assigned_to,
        "constitutional_hash": CONSTITUTIONAL_HASH,
    }


async def auto_assign_request(request: InterventionRequest):
    """Auto-assign request to appropriate user"""

    # Find eligible users
    eligible_users = []
    for user in hitl_storage["users"].values():
        if user.active and (
            not request.required_roles or user.role in request.required_roles
        ):
            eligible_users.append(user)

    if eligible_users:
        # Assign to user with highest constitutional expertise for constitutional matters
        if request.constitutional_impact:
            best_user = max(eligible_users, key=lambda u: u.constitutional_expertise)
        else:
            # Assign to user with lowest current workload
            workloads = {}
            for user in eligible_users:
                workloads[user.user_id] = sum(
                    1
                    for req in hitl_storage["intervention_requests"].values()
                    if req.assigned_to == user.user_id
                    and not any(
                        resp.request_id == req.request_id
                        for resp in hitl_storage["intervention_responses"].values()
                    )
                )

            best_user = min(eligible_users, key=lambda u: workloads.get(u.user_id, 0))

        request.assigned_to = best_user.user_id
        logger.info(
            f"Auto-assigned request {request.request_id} to {best_user.username}"
        )


@app.post("/api/v1/interventions/{request_id}/respond", response_model=Dict[str, Any])
async def respond_to_intervention(request_id: str, response: InterventionResponse):
    """Respond to intervention request"""

    if request_id not in hitl_storage["intervention_requests"]:
        raise HTTPException(status_code=404, detail="Intervention request not found")

    request = hitl_storage["intervention_requests"][request_id]
    response.request_id = request_id

    # Validate responder authorization
    if response.responder_id not in hitl_storage["users"]:
        raise HTTPException(status_code=404, detail="Responder not found")

    user = hitl_storage["users"][response.responder_id]

    # Check if user has required role
    if request.required_roles and user.role not in request.required_roles:
        raise HTTPException(
            status_code=403,
            detail=f"User role {user.role.value} not authorized for this intervention",
        )

    # Constitutional interventions require constitutional basis
    if (
        request.constitutional_impact
        and response.status == InterventionStatus.APPROVED
        and not response.constitutional_basis
    ):
        raise HTTPException(
            status_code=400,
            detail="Constitutional basis required for constitutional interventions",
        )

    # Store response
    hitl_storage["intervention_responses"][response.response_id] = response

    # Update user metrics
    user.intervention_count += 1
    user.last_activity = datetime.utcnow()

    # Update approval rate
    user_responses = [
        resp
        for resp in hitl_storage["intervention_responses"].values()
        if resp.responder_id == user.user_id
    ]

    if user_responses:
        approvals = sum(
            1 for resp in user_responses if resp.status == InterventionStatus.APPROVED
        )
        user.approval_rate = approvals / len(user_responses)

    # Update metrics
    hitl_storage["metrics"]["total_responses"] += 1
    if response.status == InterventionStatus.APPROVED:
        hitl_storage["metrics"]["approvals"] += 1
    elif response.status == InterventionStatus.REJECTED:
        hitl_storage["metrics"]["rejections"] += 1

    # Notify connected clients
    await broadcast_notification(
        {
            "type": "response_received",
            "request_id": request_id,
            "response_id": response.response_id,
            "status": response.status.value,
            "responder": user.username,
            "response_time": response.response_time.isoformat(),
        }
    )

    logger.info(f"Intervention response: {request_id} -> {response.status.value}")

    return {
        "response_id": response.response_id,
        "status": response.status.value,
        "processed_at": response.response_time.isoformat(),
        "constitutional_compliance": (
            bool(response.constitutional_basis)
            if request.constitutional_impact
            else True
        ),
    }


@app.get("/api/v1/interventions/pending", response_model=List[InterventionRequest])
async def list_pending_interventions(
    assigned_to: Optional[str] = None,
    intervention_type: Optional[str] = None,
    priority_min: Optional[int] = None,
):
    """List pending intervention requests"""

    # Get requests without responses
    pending_requests = []
    for request in hitl_storage["intervention_requests"].values():
        has_response = any(
            resp.request_id == request.request_id
            for resp in hitl_storage["intervention_responses"].values()
        )

        if not has_response:
            pending_requests.append(request)

    # Apply filters
    if assigned_to:
        pending_requests = [r for r in pending_requests if r.assigned_to == assigned_to]

    if intervention_type:
        try:
            type_enum = InterventionType(intervention_type)
            pending_requests = [
                r for r in pending_requests if r.intervention_type == type_enum
            ]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid intervention type")

    if priority_min:
        pending_requests = [r for r in pending_requests if r.priority >= priority_min]

    # Sort by priority (high first) then by creation time
    pending_requests.sort(key=lambda r: (-r.priority, r.created_at))

    return pending_requests


@app.get("/api/v1/interventions/{request_id}")
async def get_intervention_details(request_id: str):
    """Get detailed intervention information"""

    if request_id not in hitl_storage["intervention_requests"]:
        raise HTTPException(status_code=404, detail="Intervention request not found")

    request = hitl_storage["intervention_requests"][request_id]

    # Get responses
    responses = [
        resp
        for resp in hitl_storage["intervention_responses"].values()
        if resp.request_id == request_id
    ]

    # Calculate time metrics
    time_pending = datetime.utcnow() - request.created_at
    time_remaining = None
    if request.expires_at:
        time_remaining = max(
            0, (request.expires_at - datetime.utcnow()).total_seconds()
        )

    return {
        "request": request,
        "responses": responses,
        "status": "completed" if responses else "pending",
        "time_pending_minutes": time_pending.total_seconds() / 60,
        "time_remaining_seconds": time_remaining,
        "response_count": len(responses),
    }


# Workflow Management
@app.get("/api/v1/workflows", response_model=List[OversightWorkflow])
async def list_workflows(active_only: bool = True):
    """List oversight workflows"""
    workflows = list(hitl_storage["workflows"].values())

    if active_only:
        workflows = [w for w in workflows if w.active]

    return workflows


@app.post("/api/v1/workflows/trigger")
async def trigger_workflow(
    workflow_name: str, context: Dict[str, Any], requesting_service: str
):
    """Trigger an oversight workflow"""

    # Find matching workflow
    workflow = None
    for w in hitl_storage["workflows"].values():
        if w.name == workflow_name and w.active:
            workflow = w
            break

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    # Create intervention requests for each step
    request_ids = []

    for i, step in enumerate(workflow.steps):
        intervention_request = InterventionRequest(
            requesting_service=requesting_service,
            intervention_type=InterventionType.APPROVAL_REQUIRED,
            priority=8 if "emergency" in workflow.name.lower() else 6,
            title=f"{workflow.name} - {step.step_name}",
            description=f"Workflow step {i+1}: {step.step_name}",
            context=context,
            constitutional_impact="constitutional" in workflow.name.lower(),
            timeout_minutes=step.timeout_minutes,
            required_roles=[step.required_role],
        )

        # Store request
        hitl_storage["intervention_requests"][
            intervention_request.request_id
        ] = intervention_request
        request_ids.append(intervention_request.request_id)

        # Auto-assign
        await auto_assign_request(intervention_request)

    return {
        "workflow_triggered": workflow.name,
        "steps_created": len(request_ids),
        "request_ids": request_ids,
        "estimated_completion_minutes": sum(
            step.timeout_minutes for step in workflow.steps
        ),
    }


# Real-time Communication
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time updates"""

    if user_id not in hitl_storage["users"]:
        await websocket.close(code=4004, reason="User not found")
        return

    await websocket.accept()
    active_connections[user_id] = websocket

    try:
        # Send initial status
        user = hitl_storage["users"][user_id]
        await websocket.send_text(
            json.dumps(
                {
                    "type": "connection_established",
                    "user_id": user_id,
                    "role": user.role.value,
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                }
            )
        )

        # Keep connection alive and handle messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)

                # Handle ping/pong for connection maintenance
                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))

                # Update user activity
                user.last_activity = datetime.utcnow()

            except Exception as e:
                logger.error(f"WebSocket message error: {e}")
                break

    except WebSocketDisconnect:
        logger.info(f"User {user_id} disconnected")
    finally:
        if user_id in active_connections:
            del active_connections[user_id]


# Analytics and Metrics
@app.get("/api/v1/metrics")
async def get_metrics():
    """Get human-in-the-loop metrics"""

    total_requests = hitl_storage["metrics"]["total_requests"]
    total_responses = hitl_storage["metrics"]["total_responses"]

    # Calculate response rate
    response_rate = (total_responses / total_requests) if total_requests > 0 else 0

    # Calculate average response time
    response_times = []
    for response in hitl_storage["intervention_responses"].values():
        request = hitl_storage["intervention_requests"].get(response.request_id)
        if request:
            response_time = (
                response.response_time - request.created_at
            ).total_seconds()
            response_times.append(response_time)

    avg_response_time = (
        sum(response_times) / len(response_times) if response_times else 0
    )

    return {
        "total_requests": total_requests,
        "total_responses": total_responses,
        "response_rate": response_rate,
        "approval_rate": (
            (hitl_storage["metrics"]["approvals"] / total_responses)
            if total_responses > 0
            else 0
        ),
        "rejection_rate": (
            (hitl_storage["metrics"]["rejections"] / total_responses)
            if total_responses > 0
            else 0
        ),
        "timeout_rate": (
            (hitl_storage["metrics"]["timeouts"] / total_requests)
            if total_requests > 0
            else 0
        ),
        "average_response_time_seconds": avg_response_time,
        "active_connections": len(active_connections),
        "constitutional_hash": CONSTITUTIONAL_HASH,
    }


@app.get("/api/v1/dashboard")
async def get_dashboard_data():
    """Get dashboard data for UI"""

    # Recent activity
    recent_requests = sorted(
        hitl_storage["intervention_requests"].values(),
        key=lambda r: r.created_at,
        reverse=True,
    )[:10]

    recent_responses = sorted(
        hitl_storage["intervention_responses"].values(),
        key=lambda r: r.response_time,
        reverse=True,
    )[:10]

    # User activity
    user_activity = []
    for user in hitl_storage["users"].values():
        if user.active:
            user_activity.append(
                {
                    "user_id": user.user_id,
                    "username": user.username,
                    "role": user.role.value,
                    "intervention_count": user.intervention_count,
                    "approval_rate": user.approval_rate,
                    "last_activity": user.last_activity.isoformat(),
                    "online": user.user_id in active_connections,
                }
            )

    return {
        "recent_requests": recent_requests,
        "recent_responses": recent_responses,
        "user_activity": user_activity,
        "system_status": {
            "total_users": len(hitl_storage["users"]),
            "active_users": len(
                [u for u in hitl_storage["users"].values() if u.active]
            ),
            "online_users": len(active_connections),
            "pending_interventions": len(
                [
                    r
                    for r in hitl_storage["intervention_requests"].values()
                    if not any(
                        resp.request_id == r.request_id
                        for resp in hitl_storage["intervention_responses"].values()
                    )
                ]
            ),
            "constitutional_hash": CONSTITUTIONAL_HASH,
        },
    }


@app.get("/")
async def dashboard_ui():
    """Simple dashboard UI"""
    return HTMLResponse(
        """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ACGS-2 Human-in-the-Loop Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .header { background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }
            .metrics { display: flex; gap: 20px; margin: 20px 0; }
            .metric { background: #ecf0f1; padding: 15px; border-radius: 5px; flex: 1; }
            .requests { background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0; }
            .emergency { color: #e74c3c; font-weight: bold; }
            .constitutional { color: #9b59b6; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🤖 ACGS-2 Human-in-the-Loop Dashboard</h1>
            <p>Constitutional Hash: cdd01ef066bc6cf2</p>
        </div>
        
        <div class="metrics">
            <div class="metric">
                <h3>📊 System Status</h3>
                <p>Service: Active</p>
                <p>Users: <span id="user-count">Loading...</span></p>
                <p>Pending: <span id="pending-count">Loading...</span></p>
            </div>
            <div class="metric">
                <h3>⚡ Response Metrics</h3>
                <p>Response Rate: <span id="response-rate">Loading...</span></p>
                <p>Avg Time: <span id="avg-time">Loading...</span></p>
                <p>Approval Rate: <span id="approval-rate">Loading...</span></p>
            </div>
        </div>
        
        <div class="requests">
            <h3>🚨 Recent Intervention Requests</h3>
            <div id="recent-requests">Loading...</div>
        </div>
        
        <script>
            async function updateDashboard() {
                try {
                    const response = await fetch('/api/v1/dashboard');
                    const data = await response.json();
                    
                    // Update metrics
                    document.getElementById('user-count').textContent = 
                        `${data.system_status.online_users}/${data.system_status.active_users}`;
                    document.getElementById('pending-count').textContent = 
                        data.system_status.pending_interventions;
                    
                    const metricsResponse = await fetch('/api/v1/metrics');
                    const metrics = await metricsResponse.json();
                    
                    document.getElementById('response-rate').textContent = 
                        `${(metrics.response_rate * 100).toFixed(1)}%`;
                    document.getElementById('avg-time').textContent = 
                        `${(metrics.average_response_time_seconds / 60).toFixed(1)}m`;
                    document.getElementById('approval-rate').textContent = 
                        `${(metrics.approval_rate * 100).toFixed(1)}%`;
                    
                    // Update recent requests
                    const requestsHtml = data.recent_requests.map(req => `
                        <div style="border-left: 3px solid ${req.emergency ? '#e74c3c' : req.constitutional_impact ? '#9b59b6' : '#3498db'}; padding: 10px; margin: 10px 0;">
                            <strong>${req.title}</strong>
                            ${req.emergency ? '<span class="emergency">[EMERGENCY]</span>' : ''}
                            ${req.constitutional_impact ? '<span class="constitutional">[CONSTITUTIONAL]</span>' : ''}
                            <br>
                            <small>Priority: ${req.priority} | Type: ${req.intervention_type} | Created: ${new Date(req.created_at).toLocaleString()}</small>
                        </div>
                    `).join('');
                    
                    document.getElementById('recent-requests').innerHTML = requestsHtml || '<p>No recent requests</p>';
                    
                } catch (error) {
                    console.error('Dashboard update error:', error);
                }
            }
            
            // Update every 30 seconds
            updateDashboard();
            setInterval(updateDashboard, 30000);
        </script>
    </body>
    </html>
    """
    )


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8012))
    uvicorn.run(app, host="0.0.0.0", port=port)
