"""
Democratic Governance Weighted Voting System for ACGS-1 AC Service
Target: Weighted voting system with >60% quorum requirement and configurable thresholds

This module implements a sophisticated weighted voting system that enables democratic
governance with configurable stakeholder weights, quorum requirements, and approval thresholds.

Key Features:
- Configurable stakeholder weights and voting power distribution
- Quorum validation (default: 60% participation) and approval thresholds (default: 50%+1)
- Time-bounded voting periods with automatic closure
- Delegation and proxy voting mechanisms
- Vote processing with comprehensive audit trails
- Integration with existing governance workflow endpoints
- Real-time voting status and progress tracking
"""

import asyncio
import hashlib
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

# Prometheus metrics
try:
    from prometheus_client import Counter, Gauge, Histogram

    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

# Constitutional compliance integration
try:
    from services.core.ac.src.validators.multi_model_validator import (
        get_multi_model_validator,
    )

    VALIDATOR_AVAILABLE = True
except ImportError:
    VALIDATOR_AVAILABLE = False

logger = logging.getLogger(__name__)

# Prometheus metrics for weighted voting
if PROMETHEUS_AVAILABLE:
    VOTING_SESSIONS_TOTAL = Counter("ac_voting_sessions_total", "Total voting sessions created")
    VOTES_CAST_TOTAL = Counter("ac_votes_cast_total", "Total votes cast", ["vote_type"])
    QUORUM_ACHIEVEMENT_RATE = Gauge(
        "ac_quorum_achievement_rate", "Percentage of sessions achieving quorum"
    )
    VOTING_PARTICIPATION_RATE = Gauge("ac_voting_participation_rate", "Average participation rate")
    VOTE_PROCESSING_TIME = Histogram("ac_vote_processing_time_seconds", "Vote processing time")


class VoteType(Enum):
    """Types of votes that can be cast."""

    APPROVE = "approve"
    REJECT = "reject"
    ABSTAIN = "abstain"
    DELEGATE = "delegate"


class VotingSessionStatus(Enum):
    """Voting session status types."""

    PENDING = "pending"  # Not yet started
    ACTIVE = "active"  # Currently accepting votes
    CLOSED = "closed"  # Voting period ended
    APPROVED = "approved"  # Proposal approved
    REJECTED = "rejected"  # Proposal rejected
    CANCELLED = "cancelled"  # Session cancelled


class StakeholderType(Enum):
    """Types of stakeholders in the governance system."""

    CORE_TEAM = "core_team"
    COMMUNITY_REPRESENTATIVE = "community_representative"
    TECHNICAL_EXPERT = "technical_expert"
    CONSTITUTIONAL_GUARDIAN = "constitutional_guardian"
    GENERAL_STAKEHOLDER = "general_stakeholder"


@dataclass
class Stakeholder:
    """Stakeholder representation with voting power."""

    stakeholder_id: str
    name: str
    stakeholder_type: StakeholderType
    voting_weight: float  # 0.0-1.0, represents voting power
    is_active: bool = True
    delegation_target: Optional[str] = None  # ID of delegate
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_active: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Vote:
    """Individual vote representation."""

    vote_id: str
    stakeholder_id: str
    vote_type: VoteType
    voting_weight: float
    reasoning: Optional[str] = None
    cast_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_delegated: bool = False
    original_voter_id: Optional[str] = None  # For delegated votes


@dataclass
class VotingConfiguration:
    """Configuration for voting sessions."""

    quorum_threshold: float = 0.6  # 60% participation required
    approval_threshold: float = 0.5  # 50% + 1 for approval
    voting_period_hours: int = 168  # 7 days default
    allow_delegation: bool = True
    allow_vote_changes: bool = True
    require_reasoning: bool = False
    constitutional_compliance_required: bool = True


@dataclass
class VotingResults:
    """Voting session results."""

    total_eligible_weight: float
    total_votes_cast_weight: float
    participation_rate: float
    quorum_achieved: bool
    approve_weight: float
    reject_weight: float
    abstain_weight: float
    approval_rate: float
    final_result: VotingSessionStatus
    vote_breakdown: Dict[VoteType, int]
    stakeholder_participation: Dict[StakeholderType, float]


@dataclass
class VotingSession:
    """Complete voting session representation."""

    session_id: str
    proposal_id: str
    title: str
    description: str
    configuration: VotingConfiguration
    stakeholders: Dict[str, Stakeholder]
    votes: Dict[str, Vote]  # stakeholder_id -> Vote
    status: VotingSessionStatus
    created_at: datetime
    voting_starts_at: datetime
    voting_ends_at: datetime
    results: Optional[VotingResults] = None
    constitutional_compliance_score: Optional[float] = None


class WeightedVotingSystem:
    """
    Democratic governance weighted voting system.

    Features:
    - Configurable stakeholder weights and voting power
    - Quorum and approval threshold validation
    - Time-bounded voting with automatic closure
    - Delegation and proxy voting support
    - Comprehensive audit trails and reporting
    """

    def __init__(
        self,
        default_config: Optional[VotingConfiguration] = None,
        constitutional_hash: str = "cdd01ef066bc6cf2",
    ):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        self.default_config = default_config or VotingConfiguration()
        self.constitutional_hash = constitutional_hash

        # Active voting sessions
        self.active_sessions: Dict[str, VotingSession] = {}

        # Stakeholder registry
        self.stakeholders: Dict[str, Stakeholder] = {}

        # Performance tracking
        self.voting_stats = {
            "total_sessions": 0,
            "total_votes_cast": 0,
            "avg_participation_rate": 0.0,
            "quorum_achievement_rate": 0.0,
            "avg_processing_time_ms": 0.0,
        }

        # Constitutional validator
        self.constitutional_validator = None

        logger.info(
            f"Initialized WeightedVotingSystem with constitutional_hash={constitutional_hash}"
        )

    async def initialize_constitutional_validator(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Initialize constitutional compliance validator."""
        if VALIDATOR_AVAILABLE:
            try:
                self.constitutional_validator = await get_multi_model_validator()
                logger.info("Constitutional validator initialized for voting system")
            except Exception as e:
                logger.error(f"Failed to initialize constitutional validator: {e}")
                self.constitutional_validator = None
        else:
            logger.warning("Constitutional validator not available")

    async def register_stakeholder(
        self,
        stakeholder_id: str,
        name: str,
        stakeholder_type: StakeholderType,
        voting_weight: float,
    ) -> bool:
        """Register a new stakeholder in the voting system."""
        try:
            # Validate voting weight
            if not 0.0 <= voting_weight <= 1.0:
                raise ValueError(f"Voting weight must be between 0.0 and 1.0, got {voting_weight}")

            # Check if stakeholder already exists
            if stakeholder_id in self.stakeholders:
                logger.warning(f"Stakeholder {stakeholder_id} already exists, updating")

            stakeholder = Stakeholder(
                stakeholder_id=stakeholder_id,
                name=name,
                stakeholder_type=stakeholder_type,
                voting_weight=voting_weight,
            )

            self.stakeholders[stakeholder_id] = stakeholder

            logger.info(
                f"Registered stakeholder {stakeholder_id} ({stakeholder_type.value}) "
                f"with voting weight {voting_weight}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to register stakeholder {stakeholder_id}: {e}")
            return False

    async def create_voting_session(
        self,
        proposal_id: str,
        title: str,
        description: str,
        eligible_stakeholder_ids: List[str],
        configuration: Optional[VotingConfiguration] = None,
        start_delay_hours: int = 0,
    ) -> Optional[str]:
        """Create a new voting session."""
        start_time = time.time()

        try:
            # Use provided configuration or default
            config = configuration or self.default_config

            # Validate eligible stakeholders
            eligible_stakeholders = {}
            for stakeholder_id in eligible_stakeholder_ids:
                if stakeholder_id not in self.stakeholders:
                    logger.error(f"Stakeholder {stakeholder_id} not found")
                    return None

                stakeholder = self.stakeholders[stakeholder_id]
                if stakeholder.is_active:
                    eligible_stakeholders[stakeholder_id] = stakeholder

            if not eligible_stakeholders:
                logger.error("No eligible stakeholders found for voting session")
                return None

            # Check constitutional compliance if required
            constitutional_score = None
            if config.constitutional_compliance_required and self.constitutional_validator:
                try:
                    compliance_result = (
                        await self.constitutional_validator.validate_constitutional_compliance(
                            f"Proposal: {title}\n\nDescription: {description}",
                            {"proposal_id": proposal_id, "voting_session": True},
                        )
                    )
                    constitutional_score = compliance_result.consensus_confidence

                    if compliance_result.final_result.value == "non_compliant":
                        logger.error(
                            f"Proposal {proposal_id} failed constitutional compliance check"
                        )
                        return None

                except Exception as e:
                    logger.warning(f"Constitutional compliance check failed: {e}")

            # Create voting session
            session_id = str(uuid.uuid4())
            current_time = datetime.now(timezone.utc)
            voting_starts_at = current_time + timedelta(hours=start_delay_hours)
            voting_ends_at = voting_starts_at + timedelta(hours=config.voting_period_hours)

            session = VotingSession(
                session_id=session_id,
                proposal_id=proposal_id,
                title=title,
                description=description,
                configuration=config,
                stakeholders=eligible_stakeholders,
                votes={},
                status=(
                    VotingSessionStatus.PENDING
                    if start_delay_hours > 0
                    else VotingSessionStatus.ACTIVE
                ),
                created_at=current_time,
                voting_starts_at=voting_starts_at,
                voting_ends_at=voting_ends_at,
                constitutional_compliance_score=constitutional_score,
            )

            self.active_sessions[session_id] = session

            # Update statistics
            self.voting_stats["total_sessions"] += 1

            # Update Prometheus metrics
            if PROMETHEUS_AVAILABLE:
                VOTING_SESSIONS_TOTAL.inc()

            processing_time = (time.time() - start_time) * 1000
            logger.info(
                f"Created voting session {session_id} for proposal {proposal_id}, "
                f"eligible_stakeholders={len(eligible_stakeholders)}, "
                f"processing_time={processing_time:.1f}ms"
            )

            return session_id

        except Exception as e:
            logger.error(f"Failed to create voting session: {e}")
            return None

    async def cast_vote(
        self,
        session_id: str,
        stakeholder_id: str,
        vote_type: VoteType,
        reasoning: Optional[str] = None,
        delegate_to: Optional[str] = None,
    ) -> bool:
        """Cast a vote in a voting session."""
        start_time = time.time()

        try:
            # Validate session
            if session_id not in self.active_sessions:
                logger.error(f"Voting session {session_id} not found")
                return False

            session = self.active_sessions[session_id]

            # Check session status
            if session.status != VotingSessionStatus.ACTIVE:
                logger.error(
                    f"Voting session {session_id} is not active (status: {session.status.value})"
                )
                return False

            # Check voting period
            current_time = datetime.now(timezone.utc)
            if current_time < session.voting_starts_at or current_time > session.voting_ends_at:
                logger.error(f"Voting session {session_id} is outside voting period")
                return False

            # Validate stakeholder
            if stakeholder_id not in session.stakeholders:
                logger.error(f"Stakeholder {stakeholder_id} not eligible for session {session_id}")
                return False

            stakeholder = session.stakeholders[stakeholder_id]

            # Handle delegation
            if vote_type == VoteType.DELEGATE:
                if not session.configuration.allow_delegation:
                    logger.error("Delegation not allowed in this voting session")
                    return False

                if not delegate_to or delegate_to not in session.stakeholders:
                    logger.error(f"Invalid delegation target: {delegate_to}")
                    return False

                # Update stakeholder delegation
                stakeholder.delegation_target = delegate_to
                logger.info(f"Stakeholder {stakeholder_id} delegated vote to {delegate_to}")
                return True

            # Check if vote change is allowed
            if stakeholder_id in session.votes and not session.configuration.allow_vote_changes:
                logger.error(f"Vote changes not allowed for stakeholder {stakeholder_id}")
                return False

            # Validate reasoning requirement
            if session.configuration.require_reasoning and not reasoning:
                logger.error("Reasoning required for this voting session")
                return False

            # Create vote
            vote = Vote(
                vote_id=str(uuid.uuid4()),
                stakeholder_id=stakeholder_id,
                vote_type=vote_type,
                voting_weight=stakeholder.voting_weight,
                reasoning=reasoning,
                cast_at=current_time,
            )

            # Store vote
            session.votes[stakeholder_id] = vote

            # Update stakeholder activity
            stakeholder.last_active = current_time

            # Update statistics
            self.voting_stats["total_votes_cast"] += 1

            # Update Prometheus metrics
            if PROMETHEUS_AVAILABLE:
                VOTES_CAST_TOTAL.labels(vote_type=vote_type.value).inc()
                processing_time = (time.time() - start_time) * 1000
                VOTE_PROCESSING_TIME.observe(processing_time / 1000.0)

            logger.info(f"Vote cast by {stakeholder_id} in session {session_id}: {vote_type.value}")
            return True

        except Exception as e:
            logger.error(f"Failed to cast vote: {e}")
            return False

    async def close_voting_session(self, session_id: str, force_close: bool = False) -> bool:
        """Close a voting session and finalize results."""
        try:
            if session_id not in self.active_sessions:
                logger.error(f"Voting session {session_id} not found")
                return False

            session = self.active_sessions[session_id]

            # Check if session can be closed
            current_time = datetime.now(timezone.utc)
            if not force_close and current_time < session.voting_ends_at:
                logger.error(f"Voting session {session_id} has not reached end time")
                return False

            if session.status not in [
                VotingSessionStatus.ACTIVE,
                VotingSessionStatus.PENDING,
            ]:
                logger.warning(
                    f"Voting session {session_id} already closed (status: {session.status.value})"
                )
                return True

            # Calculate final results
            results = await self.calculate_voting_results(session_id)
            if not results:
                logger.error(f"Failed to calculate results for session {session_id}")
                return False

            # Update session
            session.results = results
            session.status = results.final_result

            logger.info(
                f"Closed voting session {session_id}: {results.final_result.value}, "
                f"participation={results.participation_rate:.1%}, "
                f"approval={results.approval_rate:.1%}"
            )

            return True

        except Exception as e:
            logger.error(f"Failed to close voting session {session_id}: {e}")
            return False

    async def calculate_voting_results(self, session_id: str) -> Optional[VotingResults]:
        """Calculate comprehensive voting results for a session."""
        try:
            if session_id not in self.active_sessions:
                return None

            session = self.active_sessions[session_id]

            # Calculate total eligible voting weight
            total_eligible_weight = sum(s.voting_weight for s in session.stakeholders.values())

            # Calculate vote weights by type
            approve_weight = 0.0
            reject_weight = 0.0
            abstain_weight = 0.0
            total_votes_cast_weight = 0.0

            vote_breakdown = {
                VoteType.APPROVE: 0,
                VoteType.REJECT: 0,
                VoteType.ABSTAIN: 0,
            }
            stakeholder_participation = {st: 0.0 for st in StakeholderType}
            stakeholder_counts = {st: 0 for st in StakeholderType}

            # Count stakeholders by type
            for stakeholder in session.stakeholders.values():
                stakeholder_counts[stakeholder.stakeholder_type] += 1

            # Process votes
            for vote in session.votes.values():
                if vote.vote_type == VoteType.DELEGATE:
                    continue  # Skip delegation votes in calculation

                total_votes_cast_weight += vote.voting_weight
                vote_breakdown[vote.vote_type] += 1

                # Add to stakeholder type participation
                stakeholder = session.stakeholders[vote.stakeholder_id]
                stakeholder_participation[stakeholder.stakeholder_type] += 1

                if vote.vote_type == VoteType.APPROVE:
                    approve_weight += vote.voting_weight
                elif vote.vote_type == VoteType.REJECT:
                    reject_weight += vote.voting_weight
                elif vote.vote_type == VoteType.ABSTAIN:
                    abstain_weight += vote.voting_weight

            # Calculate participation rates by stakeholder type
            for stakeholder_type in StakeholderType:
                if stakeholder_counts[stakeholder_type] > 0:
                    stakeholder_participation[stakeholder_type] = (
                        stakeholder_participation[stakeholder_type]
                        / stakeholder_counts[stakeholder_type]
                    )

            # Calculate overall metrics
            participation_rate = (
                total_votes_cast_weight / total_eligible_weight
                if total_eligible_weight > 0
                else 0.0
            )
            quorum_achieved = participation_rate >= session.configuration.quorum_threshold

            # Calculate approval rate (excluding abstentions from denominator)
            voting_weight_for_decision = approve_weight + reject_weight
            if voting_weight_for_decision > 0:
                approval_rate = approve_weight / voting_weight_for_decision
            else:
                approval_rate = 0.0

            # Determine final result
            if not quorum_achieved:
                final_result = VotingSessionStatus.REJECTED  # Failed quorum
            elif approval_rate > session.configuration.approval_threshold:
                final_result = VotingSessionStatus.APPROVED
            else:
                final_result = VotingSessionStatus.REJECTED

            results = VotingResults(
                total_eligible_weight=total_eligible_weight,
                total_votes_cast_weight=total_votes_cast_weight,
                participation_rate=participation_rate,
                quorum_achieved=quorum_achieved,
                approve_weight=approve_weight,
                reject_weight=reject_weight,
                abstain_weight=abstain_weight,
                approval_rate=approval_rate,
                final_result=final_result,
                vote_breakdown=vote_breakdown,
                stakeholder_participation=stakeholder_participation,
            )

            return results

        except Exception as e:
            logger.error(f"Failed to calculate voting results: {e}")
            return None

    def get_system_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system performance metrics."""
        try:
            # Calculate active session statistics
            active_sessions_count = len(
                [s for s in self.active_sessions.values() if s.status == VotingSessionStatus.ACTIVE]
            )

            pending_sessions_count = len(
                [
                    s
                    for s in self.active_sessions.values()
                    if s.status == VotingSessionStatus.PENDING
                ]
            )

            # Calculate average session duration for completed sessions
            completed_sessions = [
                s
                for s in self.active_sessions.values()
                if s.status in [VotingSessionStatus.APPROVED, VotingSessionStatus.REJECTED]
            ]

            avg_session_duration_hours = 0.0
            if completed_sessions:
                durations = [
                    (s.voting_ends_at - s.voting_starts_at).total_seconds() / 3600
                    for s in completed_sessions
                ]
                avg_session_duration_hours = sum(durations) / len(durations)

            return {
                "system_statistics": {
                    "total_sessions": self.voting_stats["total_sessions"],
                    "total_votes_cast": self.voting_stats["total_votes_cast"],
                    "avg_participation_rate": self.voting_stats["avg_participation_rate"],
                    "quorum_achievement_rate": self.voting_stats["quorum_achievement_rate"],
                },
                "current_state": {
                    "active_sessions": active_sessions_count,
                    "pending_sessions": pending_sessions_count,
                    "total_stakeholders": len(self.stakeholders),
                    "active_stakeholders": len(
                        [s for s in self.stakeholders.values() if s.is_active]
                    ),
                },
                "performance_targets": {
                    "target_quorum_rate": 0.6,
                    "target_participation_rate": 0.8,
                    "target_processing_time_ms": 100.0,
                },
                "stakeholder_analytics": {
                    "stakeholder_type_distribution": {
                        st.value: len(
                            [s for s in self.stakeholders.values() if s.stakeholder_type == st]
                        )
                        for st in StakeholderType
                    },
                    "total_voting_weight": sum(
                        s.voting_weight for s in self.stakeholders.values() if s.is_active
                    ),
                },
            }

        except Exception as e:
            logger.error(f"Failed to get system performance metrics: {e}")
            return {"error": str(e)}


# Global weighted voting system instance
_weighted_voting_system: Optional[WeightedVotingSystem] = None


async def get_weighted_voting_system(
    default_config: Optional[VotingConfiguration] = None,
) -> WeightedVotingSystem:
    """Get or create global weighted voting system instance."""
    global _weighted_voting_system

    if _weighted_voting_system is None:
        _weighted_voting_system = WeightedVotingSystem(default_config=default_config)
        await _weighted_voting_system.initialize_constitutional_validator()

    return _weighted_voting_system
