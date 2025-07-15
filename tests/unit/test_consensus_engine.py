"""
Unit tests for ConsensusEngine and consensus mechanisms.
"""

# Constitutional Hash: cdd01ef066bc6cf2

import asyncio
import os
import sys
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
import pytest_asyncio

sys.path.append(os.path.join(os.path.dirname(__file__), "../../../.."))

from services.core.consensus_engine.consensus_mechanisms import (
    ConsensusAlgorithm,
    ConsensusEngine,
    ConsensusSession,
    ConsensusThresholdConsensus,
    ConstitutionalPriorityConsensus,
    ExpertMediationConsensus,
    HierarchicalOverrideConsensus,
    MajorityVoteConsensus,
    RankedChoiceConsensus,
    Vote,
    VoteOption,
    WeightedVoteConsensus,
)
from services.shared.blackboard.blackboard_service import ConflictItem
from tests.fixtures.mock_services import MockRedis


class TestConsensusEngine:
    """Test cases for ConsensusEngine and consensus mechanisms"""

    @pytest_asyncio.fixture
    async def mock_blackboard(self):
        """Create mock blackboard service"""
        from services.shared.blackboard.blackboard_service import BlackboardService

        mock_redis = MockRedis()
        blackboard = BlackboardService()
        # Replace the Redis client with our mock
        blackboard.redis_client = mock_redis
        return blackboard

    @pytest_asyncio.fixture
    async def consensus_engine(self, mock_blackboard):
        """Create ConsensusEngine with mock blackboard"""
        return ConsensusEngine(mock_blackboard)

    @pytest.fixture
    def sample_conflict(self):
        """Create sample conflict for testing"""
        return ConflictItem(
            involved_agents=["ethics_agent_1", "legal_agent_1", "operational_agent_1"],
            involved_tasks=[str(uuid4())],
            conflict_type="risk_assessment_disagreement",
            description="Agents disagree on risk level for AI model deployment",
            severity="medium",
        )

    @pytest.fixture
    def sample_vote_options(self):
        """Create sample vote options"""
        return [
            VoteOption(
                option_name="Approve with monitoring",
                description="Approve deployment with enhanced monitoring",
                proposed_by="ethics_agent_1",
                constitutional_score=0.85,
                risk_assessment={"level": "low", "mitigation": "monitoring"},
            ),
            VoteOption(
                option_name="Require additional review",
                description="Conduct extended compliance review",
                proposed_by="legal_agent_1",
                constitutional_score=0.90,
                risk_assessment={"level": "medium", "mitigation": "review"},
            ),
            VoteOption(
                option_name="Approve immediately",
                description="Approve without additional conditions",
                proposed_by="operational_agent_1",
                constitutional_score=0.70,
                risk_assessment={"level": "medium", "mitigation": "standard"},
            ),
        ]

    # ConsensusEngine Core Tests

    @pytest.mark.asyncio
    async def test_initiate_consensus(
        self, consensus_engine, sample_conflict, sample_vote_options
    ):
        """Test initiating a consensus session"""
        participants = ["ethics_agent_1", "legal_agent_1", "operational_agent_1"]

        session_id = await consensus_engine.initiate_consensus(
            conflict=sample_conflict,
            algorithm=ConsensusAlgorithm.MAJORITY_VOTE,
            participants=participants,
            options=sample_vote_options,
            deadline_hours=24,
        )

        assert session_id is not None
        assert isinstance(session_id, str)

        # Verify session was created
        session_status = await consensus_engine.get_session_status(session_id)
        assert session_status is not None
        assert session_status["status"] == "active"
        assert session_status["algorithm"] == ConsensusAlgorithm.MAJORITY_VOTE
        assert len(session_status["participants"]) == 3

    @pytest.mark.asyncio
    async def test_cast_vote(
        self, consensus_engine, sample_conflict, sample_vote_options
    ):
        """Test casting votes in a consensus session"""
        participants = ["ethics_agent_1", "legal_agent_1", "operational_agent_1"]

        session_id = await consensus_engine.initiate_consensus(
            conflict=sample_conflict,
            algorithm=ConsensusAlgorithm.MAJORITY_VOTE,
            participants=participants,
            options=sample_vote_options,
        )

        # Cast vote
        vote_success = await consensus_engine.cast_vote(
            session_id=session_id,
            voter_id="ethics_agent_1",
            voter_type="agent",
            option_id=sample_vote_options[0].option_id,
            confidence=0.85,
            reasoning="This option provides good balance of safety and functionality",
        )

        assert vote_success is True

        # Verify vote was recorded
        session_status = await consensus_engine.get_session_status(session_id)
        assert session_status["votes_count"] == 1

    @pytest.mark.asyncio
    async def test_cast_invalid_vote(
        self, consensus_engine, sample_conflict, sample_vote_options
    ):
        """Test error handling for invalid votes"""
        participants = ["ethics_agent_1", "legal_agent_1"]

        session_id = await consensus_engine.initiate_consensus(
            conflict=sample_conflict,
            algorithm=ConsensusAlgorithm.MAJORITY_VOTE,
            participants=participants,
            options=sample_vote_options,
        )

        # Try to vote with unauthorized voter
        unauthorized_vote = await consensus_engine.cast_vote(
            session_id=session_id,
            voter_id="unauthorized_agent",
            voter_type="agent",
            option_id=sample_vote_options[0].option_id,
            confidence=0.85,
        )
        assert unauthorized_vote is False

        # Try to vote for non-existent option
        invalid_option_vote = await consensus_engine.cast_vote(
            session_id=session_id,
            voter_id="ethics_agent_1",
            voter_type="agent",
            option_id="non_existent_option",
            confidence=0.85,
        )
        assert invalid_option_vote is False

    @pytest.mark.asyncio
    async def test_vote_change(
        self, consensus_engine, sample_conflict, sample_vote_options
    ):
        """Test changing a vote"""
        participants = ["ethics_agent_1"]

        session_id = await consensus_engine.initiate_consensus(
            conflict=sample_conflict,
            algorithm=ConsensusAlgorithm.MAJORITY_VOTE,
            participants=participants,
            options=sample_vote_options,
        )

        # Cast initial vote
        await consensus_engine.cast_vote(
            session_id=session_id,
            voter_id="ethics_agent_1",
            voter_type="agent",
            option_id=sample_vote_options[0].option_id,
            confidence=0.85,
        )

        # Change vote
        vote_change_success = await consensus_engine.cast_vote(
            session_id=session_id,
            voter_id="ethics_agent_1",
            voter_type="agent",
            option_id=sample_vote_options[1].option_id,
            confidence=0.90,
            reasoning="Changed mind after further analysis",
        )

        assert vote_change_success is True

        # Verify only one vote exists and it's for the new option
        session_status = await consensus_engine.get_session_status(session_id)
        assert session_status["votes_count"] == 1

    # Majority Vote Consensus Tests

    @pytest.mark.asyncio
    async def test_majority_vote_success(
        self, consensus_engine, sample_conflict, sample_vote_options
    ):
        """Test successful majority vote consensus"""
        participants = ["ethics_agent_1", "legal_agent_1", "operational_agent_1"]

        session_id = await consensus_engine.initiate_consensus(
            conflict=sample_conflict,
            algorithm=ConsensusAlgorithm.MAJORITY_VOTE,
            participants=participants,
            options=sample_vote_options,
        )

        # Cast majority votes for option 0
        await consensus_engine.cast_vote(
            session_id,
            "ethics_agent_1",
            "agent",
            sample_vote_options[0].option_id,
            0.85,
        )
        await consensus_engine.cast_vote(
            session_id, "legal_agent_1", "agent", sample_vote_options[0].option_id, 0.80
        )
        await consensus_engine.cast_vote(
            session_id,
            "operational_agent_1",
            "agent",
            sample_vote_options[1].option_id,
            0.75,
        )

        # Execute consensus
        result = await consensus_engine.execute_consensus(session_id)

        assert result is not None
        assert result["success"] is True
        assert result["algorithm"] == "majority_vote"
        assert result["majority_achieved"] is True
        assert result["winning_votes"] == 2
        assert result["total_votes"] == 3

    @pytest.mark.asyncio
    async def test_majority_vote_failure(
        self, consensus_engine, sample_conflict, sample_vote_options
    ):
        """Test majority vote consensus failure (tie)"""
        participants = ["ethics_agent_1", "legal_agent_1"]

        session_id = await consensus_engine.initiate_consensus(
            conflict=sample_conflict,
            algorithm=ConsensusAlgorithm.MAJORITY_VOTE,
            participants=participants,
            options=sample_vote_options,
        )

        # Cast tie votes
        await consensus_engine.cast_vote(
            session_id,
            "ethics_agent_1",
            "agent",
            sample_vote_options[0].option_id,
            0.85,
        )
        await consensus_engine.cast_vote(
            session_id, "legal_agent_1", "agent", sample_vote_options[1].option_id, 0.80
        )

        # Execute consensus
        result = await consensus_engine.execute_consensus(session_id)

        assert result is not None
        assert result["success"] is False
        assert result["majority_achieved"] is False
        assert "next_steps" in result

    # Weighted Vote Consensus Tests

    @pytest.mark.asyncio
    async def test_weighted_vote_success(
        self, consensus_engine, sample_conflict, sample_vote_options
    ):
        """Test weighted vote consensus"""
        participants = ["ethics_agent_1", "legal_agent_1", "human_expert_1"]

        session_id = await consensus_engine.initiate_consensus(
            conflict=sample_conflict,
            algorithm=ConsensusAlgorithm.WEIGHTED_VOTE,
            participants=participants,
            options=sample_vote_options,
            session_config={"weighted_threshold": 0.6},
        )

        # Cast weighted votes (human expert has higher weight)
        await consensus_engine.cast_vote(
            session_id,
            "ethics_agent_1",
            "agent",
            sample_vote_options[0].option_id,
            0.85,
            weight=1.0,
        )
        await consensus_engine.cast_vote(
            session_id,
            "legal_agent_1",
            "agent",
            sample_vote_options[1].option_id,
            0.80,
            weight=1.0,
        )
        await consensus_engine.cast_vote(
            session_id,
            "human_expert_1",
            "human_expert",
            sample_vote_options[0].option_id,
            0.90,
            weight=2.0,
        )

        # Execute consensus
        result = await consensus_engine.execute_consensus(session_id)

        assert result is not None
        assert result["success"] is True
        assert result["algorithm"] == "weighted_vote"
        assert result["weighted_percentage"] >= 0.6

    # Constitutional Priority Consensus Tests

    @pytest.mark.asyncio
    async def test_constitutional_priority_consensus(
        self, consensus_engine, sample_conflict, sample_vote_options
    ):
        """Test constitutional priority consensus mechanism"""
        participants = ["ethics_agent_1", "legal_agent_1", "operational_agent_1"]

        session_id = await consensus_engine.initiate_consensus(
            conflict=sample_conflict,
            algorithm=ConsensusAlgorithm.CONSTITUTIONAL_PRIORITY,
            participants=participants,
            options=sample_vote_options,
            session_config={"min_constitutional_score": 0.8},
        )

        # Cast some votes
        await consensus_engine.cast_vote(
            session_id,
            "ethics_agent_1",
            "agent",
            sample_vote_options[1].option_id,
            0.85,
        )  # Option with highest constitutional score
        await consensus_engine.cast_vote(
            session_id, "legal_agent_1", "agent", sample_vote_options[0].option_id, 0.80
        )

        # Execute consensus
        result = await consensus_engine.execute_consensus(session_id)

        assert result is not None
        assert result["algorithm"] == "constitutional_priority"
        assert "constitutional_ranking" in result
        assert result["winning_constitutional_score"] >= 0.8

    # Hierarchical Override Consensus Tests

    @pytest.mark.asyncio
    async def test_hierarchical_override_consensus(
        self, consensus_engine, sample_conflict, sample_vote_options
    ):
        """Test hierarchical override consensus mechanism"""
        participants = ["ethics_agent_1", "legal_agent_1", "coordinator_1"]

        session_id = await consensus_engine.initiate_consensus(
            conflict=sample_conflict,
            algorithm=ConsensusAlgorithm.HIERARCHICAL_OVERRIDE,
            participants=participants,
            options=sample_vote_options,
            session_config={"override_threshold": 60},
        )

        # Cast votes with different authority levels
        await consensus_engine.cast_vote(
            session_id,
            "ethics_agent_1",
            "agent",
            sample_vote_options[0].option_id,
            0.85,
        )
        await consensus_engine.cast_vote(
            session_id, "legal_agent_1", "agent", sample_vote_options[1].option_id, 0.80
        )
        await consensus_engine.cast_vote(
            session_id,
            "coordinator_1",
            "coordinator",
            sample_vote_options[2].option_id,
            0.90,
        )  # Highest authority

        # Execute consensus
        result = await consensus_engine.execute_consensus(session_id)

        assert result is not None
        assert result["algorithm"] == "hierarchical_override"
        assert result["override_applied"] is True
        assert result["highest_authority_level"] == 100  # Coordinator level

    # Expert Mediation Consensus Tests

    @pytest.mark.asyncio
    async def test_expert_mediation_consensus(
        self, consensus_engine, sample_conflict, sample_vote_options
    ):
        """Test expert mediation consensus mechanism"""
        participants = [
            "ethics_agent_1",
            "legal_agent_1",
            "human_expert_1",
            "human_expert_2",
        ]

        session_id = await consensus_engine.initiate_consensus(
            conflict=sample_conflict,
            algorithm=ConsensusAlgorithm.EXPERT_MEDIATION,
            participants=participants,
            options=sample_vote_options,
            session_config={"expert_consensus_threshold": 0.7},
        )

        # Cast votes including expert votes
        await consensus_engine.cast_vote(
            session_id,
            "ethics_agent_1",
            "agent",
            sample_vote_options[0].option_id,
            0.85,
        )
        await consensus_engine.cast_vote(
            session_id, "legal_agent_1", "agent", sample_vote_options[1].option_id, 0.80
        )
        await consensus_engine.cast_vote(
            session_id,
            "human_expert_1",
            "human_expert",
            sample_vote_options[0].option_id,
            0.90,
        )
        await consensus_engine.cast_vote(
            session_id,
            "human_expert_2",
            "human_expert",
            sample_vote_options[0].option_id,
            0.88,
        )

        # Execute consensus
        result = await consensus_engine.execute_consensus(session_id)

        assert result is not None
        assert result["algorithm"] == "expert_mediation"
        assert result["expert_consensus_achieved"] is True
        assert result["expert_agreement_level"] >= 0.7

    # Ranked Choice Consensus Tests

    @pytest.mark.asyncio
    async def test_ranked_choice_consensus(
        self, consensus_engine, sample_conflict, sample_vote_options
    ):
        """Test ranked choice consensus mechanism"""
        participants = ["ethics_agent_1", "legal_agent_1", "operational_agent_1"]

        session_id = await consensus_engine.initiate_consensus(
            conflict=sample_conflict,
            algorithm=ConsensusAlgorithm.RANKED_CHOICE,
            participants=participants,
            options=sample_vote_options,
            session_config={"min_confidence": 0.6},
        )

        # Cast votes with different confidence levels (used as ranking proxy)
        await consensus_engine.cast_vote(
            session_id,
            "ethics_agent_1",
            "agent",
            sample_vote_options[0].option_id,
            0.90,
        )
        await consensus_engine.cast_vote(
            session_id, "legal_agent_1", "agent", sample_vote_options[0].option_id, 0.85
        )
        await consensus_engine.cast_vote(
            session_id,
            "operational_agent_1",
            "agent",
            sample_vote_options[1].option_id,
            0.70,
        )

        # Execute consensus
        result = await consensus_engine.execute_consensus(session_id)

        assert result is not None
        assert result["algorithm"] == "ranked_choice"
        assert "option_rankings" in result
        assert result["confidence_score"] >= 0.6

    # Consensus Threshold Tests

    @pytest.mark.asyncio
    async def test_consensus_threshold_mechanism(
        self, consensus_engine, sample_conflict, sample_vote_options
    ):
        """Test consensus threshold mechanism"""
        participants = [
            "ethics_agent_1",
            "legal_agent_1",
            "operational_agent_1",
            "coordinator_1",
        ]

        session_id = await consensus_engine.initiate_consensus(
            conflict=sample_conflict,
            algorithm=ConsensusAlgorithm.CONSENSUS_THRESHOLD,
            participants=participants,
            options=sample_vote_options,
            session_config={"consensus_threshold": 0.75},
        )

        # Cast votes to achieve consensus threshold
        await consensus_engine.cast_vote(
            session_id,
            "ethics_agent_1",
            "agent",
            sample_vote_options[0].option_id,
            0.90,
        )
        await consensus_engine.cast_vote(
            session_id, "legal_agent_1", "agent", sample_vote_options[0].option_id, 0.85
        )
        await consensus_engine.cast_vote(
            session_id,
            "operational_agent_1",
            "agent",
            sample_vote_options[0].option_id,
            0.80,
        )
        await consensus_engine.cast_vote(
            session_id,
            "coordinator_1",
            "coordinator",
            sample_vote_options[1].option_id,
            0.75,
        )

        # Execute consensus
        result = await consensus_engine.execute_consensus(session_id)

        assert result is not None
        assert result["algorithm"] == "consensus_threshold"
        assert "option_support" in result
        assert result["consensus_threshold"] == 0.75

    # Session Management Tests

    @pytest.mark.asyncio
    async def test_session_deadline_expiry(
        self, consensus_engine, sample_conflict, sample_vote_options
    ):
        """Test session deadline handling"""
        participants = ["ethics_agent_1", "legal_agent_1"]

        # Create session with short deadline
        session_id = await consensus_engine.initiate_consensus(
            conflict=sample_conflict,
            algorithm=ConsensusAlgorithm.MAJORITY_VOTE,
            participants=participants,
            options=sample_vote_options,
            deadline_hours=0.0001,  # Very short deadline (0.36 seconds)
        )

        # Wait for deadline to pass
        await asyncio.sleep(0.5)  # Wait 500ms to ensure deadline passes

        # Check for expired sessions
        expired_sessions = await consensus_engine.check_session_deadlines()
        assert session_id in expired_sessions

        # Verify session status (should be escalated after deadline expiry)
        session_status = await consensus_engine.get_session_status(session_id)
        assert session_status["status"] == "escalated"
        # Check that the session was initially failed due to deadline
        assert (
            "deadline" in session_status["result"]["reason"]
            or "escalation" in session_status["result"]
        )

    @pytest.mark.asyncio
    async def test_manual_escalation(
        self, consensus_engine, sample_conflict, sample_vote_options
    ):
        """Test manual escalation of consensus session"""
        participants = ["ethics_agent_1", "legal_agent_1"]

        session_id = await consensus_engine.initiate_consensus(
            conflict=sample_conflict,
            algorithm=ConsensusAlgorithm.MAJORITY_VOTE,
            participants=participants,
            options=sample_vote_options,
        )

        # Escalate session
        escalation_success = await consensus_engine.escalate_session(
            session_id=session_id,
            escalation_type="human_review",
            escalation_data={"reason": "Complex ethical considerations"},
        )

        assert escalation_success is True

        # Verify escalation
        session_status = await consensus_engine.get_session_status(session_id)
        assert session_status["status"] == "escalated"
        assert "escalation" in session_status["result"]

    @pytest.mark.asyncio
    async def test_consensus_metrics(
        self, consensus_engine, sample_conflict, sample_vote_options
    ):
        """Test consensus metrics collection"""
        participants = ["ethics_agent_1", "legal_agent_1", "operational_agent_1"]

        # Create and complete a session
        session_id = await consensus_engine.initiate_consensus(
            conflict=sample_conflict,
            algorithm=ConsensusAlgorithm.MAJORITY_VOTE,
            participants=participants,
            options=sample_vote_options,
        )

        # Cast votes and execute
        await consensus_engine.cast_vote(
            session_id,
            "ethics_agent_1",
            "agent",
            sample_vote_options[0].option_id,
            0.85,
        )
        await consensus_engine.cast_vote(
            session_id, "legal_agent_1", "agent", sample_vote_options[0].option_id, 0.80
        )
        await consensus_engine.cast_vote(
            session_id,
            "operational_agent_1",
            "agent",
            sample_vote_options[1].option_id,
            0.75,
        )

        await consensus_engine.execute_consensus(session_id)

        # Get metrics
        metrics = await consensus_engine.get_consensus_metrics()

        assert metrics["total_sessions"] >= 1
        assert metrics["completed_sessions"] >= 1
        assert metrics["successful_sessions"] >= 0
        assert "algorithm_distribution" in metrics
        assert "average_resolution_time_hours" in metrics
        assert ConsensusAlgorithm.MAJORITY_VOTE in metrics["algorithm_distribution"]

    @pytest.mark.asyncio
    async def test_session_cleanup(
        self, consensus_engine, sample_conflict, sample_vote_options
    ):
        """Test cleanup of old sessions"""
        participants = ["ethics_agent_1", "legal_agent_1"]

        # Create a session
        session_id = await consensus_engine.initiate_consensus(
            conflict=sample_conflict,
            algorithm=ConsensusAlgorithm.MAJORITY_VOTE,
            participants=participants,
            options=sample_vote_options,
        )

        # Mock the session as old
        session = consensus_engine.active_sessions[session_id]
        session.created_at = datetime.now(timezone.utc) - timedelta(days=8)  # 8 days old
        session.status = "completed"

        # Run cleanup
        cleaned_count = consensus_engine.cleanup_old_sessions(max_age_days=7)

        assert cleaned_count == 1
        assert session_id not in consensus_engine.active_sessions

    # Error Handling Tests

    @pytest.mark.asyncio
    async def test_execute_consensus_invalid_session(self, consensus_engine):
        """Test executing consensus on invalid session"""
        result = await consensus_engine.execute_consensus("non_existent_session")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_status_invalid_session(self, consensus_engine):
        """Test getting status of invalid session"""
        status = await consensus_engine.get_session_status("non_existent_session")
        assert status is None

    @pytest.mark.asyncio
    async def test_consensus_algorithm_error_handling(
        self, consensus_engine, sample_conflict, sample_vote_options
    ):
        """Test error handling in consensus algorithms"""
        participants = ["ethics_agent_1"]

        session_id = await consensus_engine.initiate_consensus(
            conflict=sample_conflict,
            algorithm=ConsensusAlgorithm.MAJORITY_VOTE,
            participants=participants,
            options=sample_vote_options,
        )

        # Execute consensus without any votes
        result = await consensus_engine.execute_consensus(session_id)

        assert result is not None
        assert result["success"] is False
        assert "No votes cast" in result["reason"]

    @pytest.mark.asyncio
    async def test_concurrent_voting(
        self, consensus_engine, sample_conflict, sample_vote_options
    ):
        """Test concurrent voting scenarios"""
        participants = ["ethics_agent_1", "legal_agent_1", "operational_agent_1"]

        session_id = await consensus_engine.initiate_consensus(
            conflict=sample_conflict,
            algorithm=ConsensusAlgorithm.MAJORITY_VOTE,
            participants=participants,
            options=sample_vote_options,
        )

        # Cast votes concurrently
        vote_tasks = [
            consensus_engine.cast_vote(
                session_id,
                "ethics_agent_1",
                "agent",
                sample_vote_options[0].option_id,
                0.85,
            ),
            consensus_engine.cast_vote(
                session_id,
                "legal_agent_1",
                "agent",
                sample_vote_options[1].option_id,
                0.80,
            ),
            consensus_engine.cast_vote(
                session_id,
                "operational_agent_1",
                "agent",
                sample_vote_options[0].option_id,
                0.75,
            ),
        ]

        results = await asyncio.gather(*vote_tasks)
        assert all(results)  # All votes should succeed

        # Execute consensus
        result = await consensus_engine.execute_consensus(session_id)
        assert result["total_votes"] == 3
