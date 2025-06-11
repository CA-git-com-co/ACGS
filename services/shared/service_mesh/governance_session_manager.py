"""
Governance Session Management for ACGS-1 Constitutional Governance System
Ensures workflow continuity and state consistency across service instances
"""

import asyncio
import hashlib
import json
import logging
import time
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from ..advanced_redis_client import AdvancedRedisClient
from .common_types import ServiceType

logger = logging.getLogger(__name__)


class GovernanceWorkflowType(Enum):
    """Types of governance workflows requiring session affinity."""

    POLICY_CREATION = "policy_creation"
    CONSTITUTIONAL_COMPLIANCE = "constitutional_compliance"
    POLICY_ENFORCEMENT = "policy_enforcement"
    WINA_OVERSIGHT = "wina_oversight"
    AUDIT_TRANSPARENCY = "audit_transparency"


class SessionState(Enum):
    """Session states for governance workflows."""

    ACTIVE = "active"
    SUSPENDED = "suspended"
    COMPLETED = "completed"
    EXPIRED = "expired"
    FAILED = "failed"


@dataclass
class GovernanceSession:
    """Represents a governance workflow session."""

    session_id: str
    workflow_type: GovernanceWorkflowType
    user_id: str
    created_at: float
    last_activity: float
    state: SessionState = SessionState.ACTIVE

    # Service affinities
    service_affinities: Dict[str, str] = field(
        default_factory=dict
    )  # service_type -> instance_id

    # Workflow state
    current_step: str = "initial"
    completed_steps: List[str] = field(default_factory=list)
    workflow_data: Dict[str, Any] = field(default_factory=dict)

    # Performance tracking
    step_durations: Dict[str, float] = field(default_factory=dict)
    total_duration: Optional[float] = None

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_active(self) -> bool:
        """Check if session is active."""
        return self.state == SessionState.ACTIVE

    @property
    def age_seconds(self) -> float:
        """Get session age in seconds."""
        return time.time() - self.created_at

    @property
    def idle_seconds(self) -> float:
        """Get idle time in seconds."""
        return time.time() - self.last_activity

    def update_activity(self):
        """Update last activity timestamp."""
        self.last_activity = time.time()

    def add_service_affinity(self, service_type: ServiceType, instance_id: str):
        """Add service affinity for the session."""
        self.service_affinities[service_type.value] = instance_id
        self.update_activity()

    def get_service_affinity(self, service_type: ServiceType) -> Optional[str]:
        """Get service affinity for a service type."""
        return self.service_affinities.get(service_type.value)

    def advance_step(self, step_name: str, step_data: Optional[Dict[str, Any]] = None):
        """Advance to the next workflow step."""
        # Record duration of previous step
        if self.current_step != "initial":
            step_start = self.workflow_data.get(
                f"{self.current_step}_start_time", self.last_activity
            )
            duration = time.time() - step_start
            self.step_durations[self.current_step] = duration

        # Mark current step as completed
        if self.current_step not in self.completed_steps:
            self.completed_steps.append(self.current_step)

        # Advance to new step
        self.current_step = step_name
        self.workflow_data[f"{step_name}_start_time"] = time.time()

        if step_data:
            self.workflow_data.update(step_data)

        self.update_activity()

    def complete_workflow(self):
        """Mark workflow as completed."""
        self.state = SessionState.COMPLETED
        self.total_duration = self.age_seconds
        self.update_activity()

    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GovernanceSession":
        """Create session from dictionary."""
        # Convert enum fields
        data["workflow_type"] = GovernanceWorkflowType(data["workflow_type"])
        data["state"] = SessionState(data["state"])
        return cls(**data)


class GovernanceSessionManager:
    """
    Manages governance workflow sessions with Redis persistence.

    Provides session affinity, state management, and workflow continuity
    for constitutional governance operations.
    """

    def __init__(
        self,
        redis_client: Optional[AdvancedRedisClient] = None,
        session_ttl: int = 3600,  # 1 hour default
        cleanup_interval: int = 300,  # 5 minutes
    ):
        """
        Initialize governance session manager.

        Args:
            redis_client: Redis client for persistence
            session_ttl: Session time-to-live in seconds
            cleanup_interval: Cleanup interval in seconds
        """
        self.redis_client = redis_client
        self.session_ttl = session_ttl
        self.cleanup_interval = cleanup_interval

        # In-memory cache for active sessions
        self._sessions: Dict[str, GovernanceSession] = {}

        # Cleanup task
        self._cleanup_task: Optional[asyncio.Task] = None
        self._running = False

    async def start(self):
        """Start session manager."""
        if self._running:
            return

        self._running = True

        # Start cleanup task
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())

        logger.info("Governance session manager started")

    async def stop(self):
        """Stop session manager."""
        if not self._running:
            return

        self._running = False

        # Cancel cleanup task
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        logger.info("Governance session manager stopped")

    async def create_session(
        self,
        workflow_type: GovernanceWorkflowType,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> GovernanceSession:
        """
        Create a new governance session.

        Args:
            workflow_type: Type of governance workflow
            user_id: User identifier
            metadata: Optional session metadata

        Returns:
            Created governance session
        """
        # Generate session ID
        session_id = self._generate_session_id(workflow_type, user_id)

        # Create session
        session = GovernanceSession(
            session_id=session_id,
            workflow_type=workflow_type,
            user_id=user_id,
            created_at=time.time(),
            last_activity=time.time(),
            metadata=metadata or {},
        )

        # Store in cache and Redis
        self._sessions[session_id] = session
        await self._persist_session(session)

        logger.info(
            f"Created governance session {session_id} for {workflow_type.value}"
        )
        return session

    async def get_session(self, session_id: str) -> Optional[GovernanceSession]:
        """
        Get governance session by ID.

        Args:
            session_id: Session identifier

        Returns:
            Governance session or None
        """
        # Check cache first
        if session_id in self._sessions:
            session = self._sessions[session_id]
            if session.is_active and session.idle_seconds < self.session_ttl:
                return session
            else:
                # Remove expired session
                del self._sessions[session_id]

        # Try to load from Redis
        if self.redis_client:
            session_data = await self._load_session(session_id)
            if session_data:
                session = GovernanceSession.from_dict(session_data)
                if session.is_active and session.idle_seconds < self.session_ttl:
                    self._sessions[session_id] = session
                    return session

        return None

    async def update_session(self, session: GovernanceSession):
        """
        Update governance session.

        Args:
            session: Session to update
        """
        session.update_activity()
        self._sessions[session.session_id] = session
        await self._persist_session(session)

    async def set_service_affinity(
        self, session_id: str, service_type: ServiceType, instance_id: str
    ):
        """
        Set service affinity for a session.

        Args:
            session_id: Session identifier
            service_type: Type of service
            instance_id: Instance identifier
        """
        session = await self.get_session(session_id)
        if session:
            session.add_service_affinity(service_type, instance_id)
            await self.update_session(session)

    async def get_service_affinity(
        self, session_id: str, service_type: ServiceType
    ) -> Optional[str]:
        """
        Get service affinity for a session.

        Args:
            session_id: Session identifier
            service_type: Type of service

        Returns:
            Instance ID or None
        """
        session = await self.get_session(session_id)
        if session:
            return session.get_service_affinity(service_type)
        return None

    async def advance_workflow_step(
        self,
        session_id: str,
        step_name: str,
        step_data: Optional[Dict[str, Any]] = None,
    ):
        """
        Advance workflow to next step.

        Args:
            session_id: Session identifier
            step_name: Name of the next step
            step_data: Optional step data
        """
        session = await self.get_session(session_id)
        if session:
            session.advance_step(step_name, step_data)
            await self.update_session(session)

    async def complete_session(self, session_id: str):
        """
        Complete governance session.

        Args:
            session_id: Session identifier
        """
        session = await self.get_session(session_id)
        if session:
            session.complete_workflow()
            await self.update_session(session)

    async def get_active_sessions(
        self, user_id: Optional[str] = None
    ) -> List[GovernanceSession]:
        """
        Get active governance sessions.

        Args:
            user_id: Optional user filter

        Returns:
            List of active sessions
        """
        active_sessions = []

        for session in self._sessions.values():
            if session.is_active and session.idle_seconds < self.session_ttl:
                if user_id is None or session.user_id == user_id:
                    active_sessions.append(session)

        return active_sessions

    async def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics."""
        active_sessions = await self.get_active_sessions()

        workflow_counts = {}
        for session in active_sessions:
            workflow_type = session.workflow_type.value
            workflow_counts[workflow_type] = workflow_counts.get(workflow_type, 0) + 1

        return {
            "total_active_sessions": len(active_sessions),
            "workflow_distribution": workflow_counts,
            "average_session_age": sum(s.age_seconds for s in active_sessions)
            / max(len(active_sessions), 1),
            "session_ttl": self.session_ttl,
        }

    def _generate_session_id(
        self, workflow_type: GovernanceWorkflowType, user_id: str
    ) -> str:
        """Generate unique session ID."""
        timestamp = str(time.time())
        data = f"{workflow_type.value}:{user_id}:{timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    async def _persist_session(self, session: GovernanceSession):
        """Persist session to Redis."""
        if self.redis_client:
            key = f"governance_session:{session.session_id}"
            data = json.dumps(session.to_dict())
            await self.redis_client.setex(key, self.session_ttl, data)

    async def _load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load session from Redis."""
        if self.redis_client:
            key = f"governance_session:{session_id}"
            data = await self.redis_client.get(key)
            if data:
                return json.loads(data)
        return None

    async def _cleanup_loop(self):
        """Cleanup expired sessions."""
        while self._running:
            try:
                await self._cleanup_expired_sessions()
                await asyncio.sleep(self.cleanup_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in session cleanup: {e}")
                await asyncio.sleep(5)

    async def _cleanup_expired_sessions(self):
        """Remove expired sessions."""
        current_time = time.time()
        expired_sessions = []

        for session_id, session in self._sessions.items():
            if (current_time - session.last_activity) > self.session_ttl:
                expired_sessions.append(session_id)

        for session_id in expired_sessions:
            del self._sessions[session_id]
            logger.debug(f"Cleaned up expired session {session_id}")


# Global governance session manager
_governance_session_manager: Optional[GovernanceSessionManager] = None


async def get_governance_session_manager() -> GovernanceSessionManager:
    """Get the global governance session manager."""
    global _governance_session_manager

    if _governance_session_manager is None:
        _governance_session_manager = GovernanceSessionManager()
        await _governance_session_manager.start()

    return _governance_session_manager
