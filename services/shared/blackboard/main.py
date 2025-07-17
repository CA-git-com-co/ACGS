#!/usr/bin/env python3
"""
Blackboard Service - Main Application
Constitutional Hash: cdd01ef066bc6cf2

This service implements shared knowledge coordination for multi-agent systems
within the ACGS-2 constitutional AI governance framework using the blackboard
pattern for knowledge sharing and coordination.

Port: 8010
Performance Targets: P99 <10ms for knowledge retrieval, >10K operations/second
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, UUID
from uuid import uuid4
import json

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
class KnowledgeType(str, Enum):
    CONSTITUTIONAL_PRINCIPLE = "constitutional_principle"
    LEGAL_PRECEDENT = "legal_precedent"
    ETHICAL_GUIDELINE = "ethical_guideline"
    OPERATIONAL_PROCEDURE = "operational_procedure"
    RISK_ASSESSMENT = "risk_assessment"
    STAKEHOLDER_FEEDBACK = "stakeholder_feedback"
    GOVERNANCE_DECISION = "governance_decision"
    POLICY_RECOMMENDATION = "policy_recommendation"
    COMPLIANCE_REQUIREMENT = "compliance_requirement"

class ContributionType(str, Enum):
    NEW_KNOWLEDGE = "new_knowledge"
    KNOWLEDGE_UPDATE = "knowledge_update"
    KNOWLEDGE_REFINEMENT = "knowledge_refinement"
    PEER_VALIDATION = "peer_validation"
    CONSTITUTIONAL_VERIFICATION = "constitutional_verification"
    KNOWLEDGE_SYNTHESIS = "knowledge_synthesis"

class CoordinationState(str, Enum):
    INITIALIZING = "initializing"
    KNOWLEDGE_GATHERING = "knowledge_gathering"
    CONSENSUS_BUILDING = "consensus_building"
    DECISION_SYNTHESIS = "decision_synthesis"
    VALIDATION = "validation"
    COMPLETED = "completed"
    ESCALATED = "escalated"

class ValidationStatus(str, Enum):
    PENDING = "pending"
    VALIDATED = "validated"
    REJECTED = "rejected"
    REQUIRES_REVIEW = "requires_review"

class AccessLevel(str, Enum):
    PUBLIC = "public"
    RESTRICTED = "restricted"
    CONFIDENTIAL = "confidential"
    CONSTITUTIONAL_ONLY = "constitutional_only"

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

class AccessControl(BaseModel):
    access_level: AccessLevel = Field(default=AccessLevel.PUBLIC)
    allowed_agents: List[str] = Field(default_factory=list)
    restricted_operations: List[str] = Field(default_factory=list)
    requires_constitutional_clearance: bool = Field(default=False)

class KnowledgeEntry(BaseModel):
    entry_id: str = Field(default_factory=lambda: str(uuid4()))
    knowledge_type: KnowledgeType
    content: Dict[str, Any]
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)
    source_agent: str
    confidence_level: float = Field(ge=0, le=1)
    expiration: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    access_control: AccessControl = Field(default_factory=AccessControl)
    tags: List[str] = Field(default_factory=list)
    references: List[str] = Field(default_factory=list)

class PeerReview(BaseModel):
    review_id: str = Field(default_factory=lambda: str(uuid4()))
    reviewer_agent: str
    entry_id: str
    review_score: float = Field(ge=0, le=1)
    comments: str = ""
    constitutional_assessment: Optional[ConstitutionalValidation] = None
    reviewed_at: datetime = Field(default_factory=datetime.utcnow)

class AgentContribution(BaseModel):
    contribution_id: str = Field(default_factory=lambda: str(uuid4()))
    agent_id: str
    knowledge_entry_id: str
    contribution_type: ContributionType
    validation_status: ValidationStatus = Field(default=ValidationStatus.PENDING)
    peer_reviews: List[PeerReview] = Field(default_factory=list)
    constitutional_compliance: Optional[ConstitutionalValidation] = None
    contributed_at: datetime = Field(default_factory=datetime.utcnow)

class ConsensusRequirements(BaseModel):
    minimum_participants: int = Field(default=2)
    consensus_threshold: float = Field(ge=0.5, le=1.0, default=0.7)
    timeout_minutes: int = Field(default=30)
    requires_constitutional_validation: bool = Field(default=True)

class ConstitutionalConstraint(BaseModel):
    constraint_id: str = Field(default_factory=lambda: str(uuid4()))
    constraint_type: str
    description: str
    enforcement_level: str = Field(default="strict")
    parameters: Dict[str, Any] = Field(default_factory=dict)

class CoordinationContext(BaseModel):
    context_id: str = Field(default_factory=lambda: str(uuid4()))
    coordination_session: str
    participants: List[str] = Field(default_factory=list)
    shared_knowledge: List[str] = Field(default_factory=list)  # Knowledge entry IDs
    coordination_state: CoordinationState = Field(default=CoordinationState.INITIALIZING)
    consensus_requirements: ConsensusRequirements = Field(default_factory=ConsensusRequirements)
    constitutional_constraints: List[ConstitutionalConstraint] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class KnowledgeQuery(BaseModel):
    knowledge_type: Optional[KnowledgeType] = None
    agent_id: Optional[str] = None
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)
    min_confidence: float = Field(ge=0, le=1, default=0.0)
    tags: List[str] = Field(default_factory=list)
    access_level: Optional[AccessLevel] = None
    include_expired: bool = Field(default=False)

class KnowledgeUpdate(BaseModel):
    content: Optional[Dict[str, Any]] = None
    confidence_level: Optional[float] = None
    tags: Optional[List[str]] = None
    access_control: Optional[AccessControl] = None
    constitutional_context: Optional[ConstitutionalContext] = None

# Core Blackboard Components
class ConstitutionalValidator:
    """Validates knowledge and operations for constitutional compliance."""
    
    def __init__(self):
        self.constitutional_hash = CONSTITUTIONAL_HASH
    
    async def validate_knowledge(self, entry: KnowledgeEntry) -> ConstitutionalValidation:
        """Validate a knowledge entry for constitutional compliance."""
        violations = []
        recommendations = []
        compliance_score = 1.0
        
        # Validate constitutional hash
        if entry.constitutional_hash != self.constitutional_hash:
            violations.append(f"Invalid constitutional hash: {entry.constitutional_hash}")
            compliance_score -= 0.5
        
        # Validate content for constitutional principles
        content = entry.content
        if isinstance(content, dict):
            # Check for constitutional violations in content
            if any(violation_term in str(content).lower() for violation_term in ["discriminatory", "biased", "harmful"]):
                violations.append("Content contains potentially constitutional violations")
                compliance_score -= 0.3
        
        # Validate confidence level
        if entry.confidence_level < 0.5:
            recommendations.append("Low confidence knowledge should be peer-reviewed")
            compliance_score -= 0.1
        
        # Validate access control
        if entry.knowledge_type == KnowledgeType.CONSTITUTIONAL_PRINCIPLE and entry.access_control.access_level != AccessLevel.CONSTITUTIONAL_ONLY:
            recommendations.append("Constitutional principles should have constitutional-only access")
            compliance_score -= 0.1
        
        is_compliant = len(violations) == 0 and compliance_score >= 0.8
        
        return ConstitutionalValidation(
            is_compliant=is_compliant,
            compliance_score=max(0.0, compliance_score),
            violations=violations,
            recommendations=recommendations
        )
    
    async def validate_coordination_result(self, context: CoordinationContext) -> ConstitutionalValidation:
        """Validate coordination result for constitutional compliance."""
        violations = []
        recommendations = []
        compliance_score = 1.0
        
        # Check if consensus requirements were met
        if len(context.participants) < context.consensus_requirements.minimum_participants:
            violations.append("Insufficient participants for valid consensus")
            compliance_score -= 0.4
        
        # Validate constitutional constraints
        for constraint in context.constitutional_constraints:
            if constraint.enforcement_level == "strict":
                # Mock constraint validation
                compliance_score -= 0.1
                recommendations.append(f"Strict constraint {constraint.constraint_type} requires careful validation")
        
        is_compliant = len(violations) == 0 and compliance_score >= 0.8
        
        return ConstitutionalValidation(
            is_compliant=is_compliant,
            compliance_score=max(0.0, compliance_score),
            violations=violations,
            recommendations=recommendations
        )

class KnowledgeStore:
    """Manages storage and retrieval of knowledge entries."""
    
    def __init__(self):
        self.knowledge_entries: Dict[str, KnowledgeEntry] = {}
        self.knowledge_index: Dict[KnowledgeType, Set[str]] = {kt: set() for kt in KnowledgeType}
        self.agent_index: Dict[str, Set[str]] = {}
        self.tag_index: Dict[str, Set[str]] = {}
        
        # Mock vector storage for semantic search
        self.semantic_index: Dict[str, List[float]] = {}
    
    async def store(self, entry: KnowledgeEntry) -> KnowledgeEntry:
        """Store a knowledge entry."""
        self.knowledge_entries[entry.entry_id] = entry
        
        # Update indexes
        self.knowledge_index[entry.knowledge_type].add(entry.entry_id)
        
        if entry.source_agent not in self.agent_index:
            self.agent_index[entry.source_agent] = set()
        self.agent_index[entry.source_agent].add(entry.entry_id)
        
        for tag in entry.tags:
            if tag not in self.tag_index:
                self.tag_index[tag] = set()
            self.tag_index[tag].add(entry.entry_id)
        
        # Mock semantic embedding (in production, use actual embedding model)
        self.semantic_index[entry.entry_id] = [0.1] * 768  # Mock 768-dim embedding
        
        logger.info(f"Stored knowledge entry {entry.entry_id} of type {entry.knowledge_type}")
        return entry
    
    async def get(self, entry_id: str) -> Optional[KnowledgeEntry]:
        """Get a knowledge entry by ID."""
        return self.knowledge_entries.get(entry_id)
    
    async def query(self, query: KnowledgeQuery) -> List[KnowledgeEntry]:
        """Query knowledge entries based on criteria."""
        candidate_ids = set(self.knowledge_entries.keys())
        
        # Filter by knowledge type
        if query.knowledge_type:
            candidate_ids &= self.knowledge_index[query.knowledge_type]
        
        # Filter by agent
        if query.agent_id:
            candidate_ids &= self.agent_index.get(query.agent_id, set())
        
        # Filter by tags
        if query.tags:
            for tag in query.tags:
                candidate_ids &= self.tag_index.get(tag, set())
        
        # Filter entries and apply additional criteria
        results = []
        current_time = datetime.utcnow()
        
        for entry_id in candidate_ids:
            entry = self.knowledge_entries[entry_id]
            
            # Check expiration
            if not query.include_expired and entry.expiration and entry.expiration < current_time:
                continue
            
            # Check confidence level
            if entry.confidence_level < query.min_confidence:
                continue
            
            # Check access level
            if query.access_level and entry.access_control.access_level != query.access_level:
                continue
            
            # Check constitutional hash
            if entry.constitutional_hash != query.constitutional_hash:
                continue
            
            results.append(entry)
        
        # Sort by confidence and recency
        results.sort(key=lambda e: (e.confidence_level, e.created_at), reverse=True)
        return results
    
    async def update(self, entry_id: str, update: KnowledgeUpdate) -> Optional[KnowledgeEntry]:
        """Update a knowledge entry."""
        entry = self.knowledge_entries.get(entry_id)
        if not entry:
            return None
        
        # Apply updates
        if update.content is not None:
            entry.content = update.content
        
        if update.confidence_level is not None:
            entry.confidence_level = update.confidence_level
        
        if update.tags is not None:
            # Update tag index
            for old_tag in entry.tags:
                self.tag_index[old_tag].discard(entry_id)
            
            entry.tags = update.tags
            
            for new_tag in entry.tags:
                if new_tag not in self.tag_index:
                    self.tag_index[new_tag] = set()
                self.tag_index[new_tag].add(entry_id)
        
        if update.access_control is not None:
            entry.access_control = update.access_control
        
        entry.updated_at = datetime.utcnow()
        
        logger.info(f"Updated knowledge entry {entry_id}")
        return entry
    
    async def query_relevant(
        self, 
        constitutional_constraints: List[ConstitutionalConstraint],
        coordination_type: str
    ) -> List[KnowledgeEntry]:
        """Query knowledge relevant to constitutional constraints and coordination type."""
        relevant_entries = []
        
        # Find entries related to constitutional principles
        constitutional_entries = await self.query(KnowledgeQuery(
            knowledge_type=KnowledgeType.CONSTITUTIONAL_PRINCIPLE,
            min_confidence=0.7
        ))
        relevant_entries.extend(constitutional_entries)
        
        # Find entries related to specific constraints
        for constraint in constitutional_constraints:
            constraint_entries = await self.query(KnowledgeQuery(
                tags=[constraint.constraint_type, coordination_type],
                min_confidence=0.6
            ))
            relevant_entries.extend(constraint_entries)
        
        # Remove duplicates
        seen_ids = set()
        unique_entries = []
        for entry in relevant_entries:
            if entry.entry_id not in seen_ids:
                unique_entries.append(entry)
                seen_ids.add(entry.entry_id)
        
        return unique_entries

class CoordinationEngine:
    """Manages coordination contexts and consensus building."""
    
    def __init__(self, knowledge_store: KnowledgeStore, constitutional_validator: ConstitutionalValidator):
        self.knowledge_store = knowledge_store
        self.constitutional_validator = constitutional_validator
        self.coordination_contexts: Dict[str, CoordinationContext] = {}
        self.active_sessions: Dict[str, Set[str]] = {}  # session_id -> agent_ids
    
    async def create_coordination_context(
        self, 
        session_id: str,
        participants: List[str],
        coordination_type: str = "consensus",
        constitutional_constraints: List[ConstitutionalConstraint] = None
    ) -> CoordinationContext:
        """Create a new coordination context."""
        context = CoordinationContext(
            coordination_session=session_id,
            participants=participants,
            constitutional_constraints=constitutional_constraints or []
        )
        
        self.coordination_contexts[context.context_id] = context
        self.active_sessions[session_id] = set(participants)
        
        logger.info(f"Created coordination context {context.context_id} for session {session_id}")
        return context
    
    async def share_knowledge_with_participants(
        self, 
        context: CoordinationContext, 
        knowledge_entries: List[KnowledgeEntry]
    ) -> bool:
        """Share knowledge with all participants in a coordination context."""
        for entry in knowledge_entries:
            # Validate access permissions
            if entry.access_control.access_level == AccessLevel.RESTRICTED:
                # Check if participants have access
                allowed_agents = set(entry.access_control.allowed_agents)
                if not set(context.participants).issubset(allowed_agents):
                    logger.warning(f"Access denied for knowledge entry {entry.entry_id}")
                    continue
            
            context.shared_knowledge.append(entry.entry_id)
        
        context.updated_at = datetime.utcnow()
        logger.info(f"Shared {len(knowledge_entries)} knowledge entries with context {context.context_id}")
        return True
    
    async def get_coordination_context(self, context_id: str) -> Optional[CoordinationContext]:
        """Get a coordination context by ID."""
        return self.coordination_contexts.get(context_id)
    
    async def update_coordination_state(
        self, 
        context_id: str, 
        new_state: CoordinationState
    ) -> bool:
        """Update the state of a coordination context."""
        context = self.coordination_contexts.get(context_id)
        if not context:
            return False
        
        context.coordination_state = new_state
        context.updated_at = datetime.utcnow()
        
        logger.info(f"Updated coordination context {context_id} state to {new_state}")
        return True

class NotificationService:
    """Manages notifications and real-time updates."""
    
    def __init__(self):
        self.subscribers: Dict[str, Set[WebSocket]] = {}  # topic -> websockets
        self.agent_subscriptions: Dict[str, Set[str]] = {}  # agent_id -> topics
    
    async def subscribe(self, agent_id: str, topic: str, websocket: WebSocket):
        """Subscribe an agent to a topic."""
        if topic not in self.subscribers:
            self.subscribers[topic] = set()
        self.subscribers[topic].add(websocket)
        
        if agent_id not in self.agent_subscriptions:
            self.agent_subscriptions[agent_id] = set()
        self.agent_subscriptions[agent_id].add(topic)
        
        logger.info(f"Agent {agent_id} subscribed to topic {topic}")
    
    async def unsubscribe(self, agent_id: str, topic: str, websocket: WebSocket):
        """Unsubscribe an agent from a topic."""
        if topic in self.subscribers:
            self.subscribers[topic].discard(websocket)
        
        if agent_id in self.agent_subscriptions:
            self.agent_subscriptions[agent_id].discard(topic)
        
        logger.info(f"Agent {agent_id} unsubscribed from topic {topic}")
    
    async def notify_knowledge_added(self, entry: KnowledgeEntry):
        """Notify subscribers about new knowledge."""
        topic = f"knowledge.{entry.knowledge_type.value}"
        message = {
            "type": "knowledge.added",
            "entry_id": entry.entry_id,
            "knowledge_type": entry.knowledge_type,
            "source_agent": entry.source_agent,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self._broadcast_to_topic(topic, message)
    
    async def notify_coordination_update(self, context: CoordinationContext):
        """Notify subscribers about coordination updates."""
        topic = f"coordination.{context.coordination_session}"
        message = {
            "type": "coordination.updated",
            "context_id": context.context_id,
            "state": context.coordination_state,
            "participants": context.participants,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self._broadcast_to_topic(topic, message)
    
    async def _broadcast_to_topic(self, topic: str, message: Dict[str, Any]):
        """Broadcast a message to all subscribers of a topic."""
        if topic not in self.subscribers:
            return
        
        disconnected_sockets = set()
        for websocket in self.subscribers[topic]:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send message to websocket: {e}")
                disconnected_sockets.add(websocket)
        
        # Remove disconnected sockets
        for websocket in disconnected_sockets:
            self.subscribers[topic].discard(websocket)

class BlackboardController:
    """Main controller for blackboard operations."""
    
    def __init__(self):
        self.knowledge_store = KnowledgeStore()
        self.constitutional_validator = ConstitutionalValidator()
        self.coordination_engine = CoordinationEngine(self.knowledge_store, self.constitutional_validator)
        self.notification_service = NotificationService()
        self.performance_monitor = PerformanceMonitor() if SHARED_AVAILABLE else None
    
    async def add_knowledge(self, entry: KnowledgeEntry) -> Dict[str, Any]:
        """Add knowledge entry to blackboard."""
        start_time = time.time()
        
        # Constitutional validation
        validation = await self.constitutional_validator.validate_knowledge(entry)
        if not validation.is_compliant:
            return {
                "success": False,
                "entry_id": entry.entry_id,
                "violations": validation.violations,
                "compliance_score": validation.compliance_score
            }
        
        # Store knowledge
        stored_entry = await self.knowledge_store.store(entry)
        
        # Notify interested parties
        await self.notification_service.notify_knowledge_added(stored_entry)
        
        # Record performance metrics
        if self.performance_monitor:
            await self.performance_monitor.record_operation(
                "add_knowledge",
                time.time() - start_time,
                {"knowledge_type": entry.knowledge_type, "agent": entry.source_agent}
            )
        
        return {
            "success": True,
            "entry_id": stored_entry.entry_id,
            "validation": validation.dict()
        }
    
    async def coordinate_agents(
        self, 
        session_id: str,
        participants: List[str],
        coordination_type: str = "consensus",
        constitutional_constraints: List[ConstitutionalConstraint] = None
    ) -> Dict[str, Any]:
        """Coordinate agents through blackboard."""
        start_time = time.time()
        
        # Create coordination context
        context = await self.coordination_engine.create_coordination_context(
            session_id, participants, coordination_type, constitutional_constraints
        )
        
        # Gather relevant knowledge
        relevant_knowledge = await self.knowledge_store.query_relevant(
            constitutional_constraints or [], coordination_type
        )
        
        # Share knowledge with participants
        await self.coordination_engine.share_knowledge_with_participants(context, relevant_knowledge)
        
        # Notify participants
        await self.notification_service.notify_coordination_update(context)
        
        # Record performance metrics
        if self.performance_monitor:
            await self.performance_monitor.record_operation(
                "coordinate_agents",
                time.time() - start_time,
                {"participants": len(participants), "knowledge_entries": len(relevant_knowledge)}
            )
        
        return {
            "success": True,
            "context_id": context.context_id,
            "shared_knowledge_count": len(context.shared_knowledge),
            "coordination_state": context.coordination_state
        }

# Global blackboard controller
blackboard = BlackboardController()

# FastAPI Application Setup
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    logger.info("Starting Blackboard Service")
    
    # Initialize connections (Redis, PostgreSQL, Elasticsearch)
    try:
        # Here you would initialize actual database connections
        logger.info("Initialized blackboard infrastructure")
    except Exception as e:
        logger.error(f"Failed to initialize infrastructure: {e}")
        raise
    
    yield
    
    # Cleanup
    logger.info("Shutting down Blackboard Service")

app = FastAPI(
    title="Blackboard Service",
    description="ACGS-2 Shared Knowledge Coordination Service for constitutional AI governance",
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
        max_requests=10000,
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
        "service": "blackboard",
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "knowledge_entries": len(blackboard.knowledge_store.knowledge_entries),
        "active_contexts": len(blackboard.coordination_engine.coordination_contexts),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/metrics", include_in_schema=False)
async def metrics():
    """Prometheus metrics endpoint."""
    knowledge_type_counts = {}
    for kt in KnowledgeType:
        count = len(blackboard.knowledge_store.knowledge_index[kt])
        knowledge_type_counts[f"bb_knowledge_{kt.value}_total"] = count
    
    return {
        "bb_knowledge_entries_total": len(blackboard.knowledge_store.knowledge_entries),
        "bb_coordination_contexts_total": len(blackboard.coordination_engine.coordination_contexts),
        "bb_active_sessions_total": len(blackboard.coordination_engine.active_sessions),
        "bb_constitutional_hash": CONSTITUTIONAL_HASH,
        **knowledge_type_counts
    }

@app.post("/api/v1/knowledge", response_model=Dict[str, Any])
async def add_knowledge(
    entry: KnowledgeEntry,
    current_user = Depends(get_current_user)
):
    """Add knowledge entry to blackboard."""
    result = await blackboard.add_knowledge(entry)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result)
    return result

@app.get("/api/v1/knowledge", response_model=List[KnowledgeEntry])
async def query_knowledge(
    knowledge_type: Optional[KnowledgeType] = None,
    agent_id: Optional[str] = None,
    constitutional_hash: str = CONSTITUTIONAL_HASH,
    min_confidence: float = 0.0,
    current_user = Depends(get_current_user)
):
    """Query knowledge entries."""
    query = KnowledgeQuery(
        knowledge_type=knowledge_type,
        agent_id=agent_id,
        constitutional_hash=constitutional_hash,
        min_confidence=min_confidence
    )
    
    results = await blackboard.knowledge_store.query(query)
    return results

@app.get("/api/v1/knowledge/{entry_id}", response_model=KnowledgeEntry)
async def get_knowledge(
    entry_id: str,
    current_user = Depends(get_current_user)
):
    """Get specific knowledge entry."""
    entry = await blackboard.knowledge_store.get(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Knowledge entry not found")
    return entry

@app.put("/api/v1/knowledge/{entry_id}", response_model=KnowledgeEntry)
async def update_knowledge(
    entry_id: str,
    update: KnowledgeUpdate,
    current_user = Depends(get_current_user)
):
    """Update knowledge entry."""
    updated_entry = await blackboard.knowledge_store.update(entry_id, update)
    if not updated_entry:
        raise HTTPException(status_code=404, detail="Knowledge entry not found")
    return updated_entry

@app.post("/api/v1/knowledge/{entry_id}/validate")
async def validate_knowledge(
    entry_id: str,
    current_user = Depends(get_current_user)
):
    """Validate knowledge entry for constitutional compliance."""
    entry = await blackboard.knowledge_store.get(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Knowledge entry not found")
    
    validation = await blackboard.constitutional_validator.validate_knowledge(entry)
    return {
        "entry_id": entry_id,
        "is_compliant": validation.is_compliant,
        "validation_details": validation.dict()
    }

@app.post("/api/v1/coordination", response_model=Dict[str, Any])
async def create_coordination(
    session_id: str,
    participants: List[str],
    coordination_type: str = "consensus",
    constitutional_constraints: List[ConstitutionalConstraint] = None,
    current_user = Depends(get_current_user)
):
    """Create coordination context."""
    result = await blackboard.coordinate_agents(
        session_id, participants, coordination_type, constitutional_constraints
    )
    return result

@app.get("/api/v1/coordination/{context_id}/knowledge", response_model=Dict[str, Any])
async def get_coordination_knowledge(
    context_id: str,
    current_user = Depends(get_current_user)
):
    """Get shared knowledge for coordination context."""
    context = await blackboard.coordination_engine.get_coordination_context(context_id)
    if not context:
        raise HTTPException(status_code=404, detail="Coordination context not found")
    
    # Get shared knowledge entries
    shared_knowledge = []
    for entry_id in context.shared_knowledge:
        entry = await blackboard.knowledge_store.get(entry_id)
        if entry:
            shared_knowledge.append(entry)
    
    return {
        "context_id": context_id,
        "shared_knowledge": shared_knowledge,
        "coordination_state": context.coordination_state,
        "participants": context.participants
    }

@app.post("/api/v1/coordination/{context_id}/knowledge")
async def contribute_knowledge(
    context_id: str,
    knowledge_entry_id: str,
    contribution_type: ContributionType,
    agent_id: str,
    current_user = Depends(get_current_user)
):
    """Contribute knowledge to coordination context."""
    context = await blackboard.coordination_engine.get_coordination_context(context_id)
    if not context:
        raise HTTPException(status_code=404, detail="Coordination context not found")
    
    if agent_id not in context.participants:
        raise HTTPException(status_code=403, detail="Agent not participating in context")
    
    # Add knowledge to context
    if knowledge_entry_id not in context.shared_knowledge:
        context.shared_knowledge.append(knowledge_entry_id)
        context.updated_at = datetime.utcnow()
    
    # Create contribution record
    contribution = AgentContribution(
        agent_id=agent_id,
        knowledge_entry_id=knowledge_entry_id,
        contribution_type=contribution_type
    )
    
    return {"success": True, "contribution_id": contribution.contribution_id}

# WebSocket endpoints for real-time updates
@app.websocket("/ws/knowledge/{knowledge_type}")
async def knowledge_websocket(websocket: WebSocket, knowledge_type: str):
    """WebSocket for knowledge stream by type."""
    await websocket.accept()
    
    # Subscribe to knowledge type
    await blackboard.notification_service.subscribe(
        "websocket_client", f"knowledge.{knowledge_type}", websocket
    )
    
    try:
        while True:
            await asyncio.sleep(1)  # Keep connection alive
    
    except Exception as e:
        logger.error(f"WebSocket error for knowledge type {knowledge_type}: {e}")
    finally:
        await blackboard.notification_service.unsubscribe(
            "websocket_client", f"knowledge.{knowledge_type}", websocket
        )
        await websocket.close()

@app.websocket("/ws/coordination/{session_id}")
async def coordination_websocket(websocket: WebSocket, session_id: str):
    """WebSocket for coordination updates."""
    await websocket.accept()
    
    # Subscribe to coordination session
    await blackboard.notification_service.subscribe(
        "websocket_client", f"coordination.{session_id}", websocket
    )
    
    try:
        while True:
            await asyncio.sleep(1)  # Keep connection alive
    
    except Exception as e:
        logger.error(f"WebSocket error for coordination {session_id}: {e}")
    finally:
        await blackboard.notification_service.unsubscribe(
            "websocket_client", f"coordination.{session_id}", websocket
        )
        await websocket.close()

# Main execution
if __name__ == "__main__":
    import sys
    
    logger.info(f"Starting Blackboard Service on port 8010")
    logger.info(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    logger.info(f"Shared components available: {SHARED_AVAILABLE}")
    
    # Configuration
    host = "0.0.0.0"
    port = 8010
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