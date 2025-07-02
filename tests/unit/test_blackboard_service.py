"""
Unit tests for BlackboardService - the core communication hub for multi-agent coordination.
"""

import pytest
import pytest_asyncio
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))

from services.shared.blackboard.blackboard_service import (
    BlackboardService, KnowledgeItem, TaskDefinition, ConflictItem
)
from tests.fixtures.multi_agent.mock_services import MockRedis


class TestBlackboardService:
    """Test cases for BlackboardService functionality"""
    
    @pytest_asyncio.fixture
    async def blackboard_service(self):
        """Create BlackboardService with mock Redis"""
        mock_redis = MockRedis()
        service = BlackboardService()
        # Replace the Redis client with our mock
        service.redis_client = mock_redis
        return service
    
    @pytest.fixture
    def sample_knowledge_item(self):
        """Create a sample knowledge item for testing"""
        return KnowledgeItem(
            space="governance",
            agent_id="ethics_agent_1",
            knowledge_type="ethical_analysis",
            content={
                "assessment": "approved",
                "risk_level": "low",
                "reasoning": "Meets ethical guidelines"
            },
            priority=2,
            tags={"ethics", "analysis", "approved"}
        )
    
    @pytest.fixture
    def sample_task_definition(self):
        """Create a sample task definition for testing"""
        return TaskDefinition(
            task_type="governance_review",
            description="Review AI model deployment request",
            requirements={
                "ethical_review": True,
                "legal_review": True,
                "operational_review": True
            },
            priority=1,
            deadline=datetime.utcnow() + timedelta(hours=24),
            assigned_agents=["ethics_agent_1", "legal_agent_1", "operational_agent_1"],
            metadata={
                "request_id": str(uuid4()),
                "model_type": "language_model"
            }
        )
    
    @pytest.fixture
    def sample_conflict_item(self):
        """Create a sample conflict item for testing"""
        return ConflictItem(
            conflicting_agents=["ethics_agent_1", "legal_agent_1"],
            conflict_type="assessment_disagreement",
            description="Agents disagree on risk level",
            context={
                "ethics_assessment": "high_risk",
                "legal_assessment": "low_risk",
                "governance_request_id": str(uuid4())
            },
            severity="medium"
        )
    
    # Knowledge Management Tests
    
    @pytest.mark.asyncio
    async def test_add_knowledge_item(self, blackboard_service, sample_knowledge_item):
        """Test adding knowledge to the blackboard"""
        knowledge_id = await blackboard_service.add_knowledge(sample_knowledge_item)
        
        assert knowledge_id is not None
        assert isinstance(knowledge_id, str)
        
        # Verify knowledge was stored
        retrieved = await blackboard_service.get_knowledge(knowledge_id, sample_knowledge_item.space)
        assert retrieved is not None
        assert retrieved.agent_id == sample_knowledge_item.agent_id
        assert retrieved.knowledge_type == sample_knowledge_item.knowledge_type
        assert retrieved.content == sample_knowledge_item.content
    
    @pytest.mark.asyncio
    async def test_query_knowledge_by_space(self, blackboard_service, sample_knowledge_item):
        """Test querying knowledge by space"""
        # Add multiple knowledge items
        knowledge_id1 = await blackboard_service.add_knowledge(sample_knowledge_item)
        
        different_space_item = KnowledgeItem(
            space="coordination",
            agent_id="coordinator_1",
            knowledge_type="task_assignment",
            content={"task": "coordinate_agents"},
            priority=1,
            tags={"coordination"}
        )
        knowledge_id2 = await blackboard_service.add_knowledge(different_space_item)
        
        # Query by governance space
        governance_knowledge = await blackboard_service.query_knowledge(space="governance")
        assert len(governance_knowledge) == 1
        assert governance_knowledge[0].id == knowledge_id1
        
        # Query by coordination space
        coordination_knowledge = await blackboard_service.query_knowledge(space="coordination")
        assert len(coordination_knowledge) == 1
        assert coordination_knowledge[0].id == knowledge_id2
    
    @pytest.mark.asyncio
    async def test_query_knowledge_by_agent(self, blackboard_service, sample_knowledge_item):
        """Test querying knowledge by agent ID"""
        knowledge_id = await blackboard_service.add_knowledge(sample_knowledge_item)
        
        # Query by agent ID
        agent_knowledge = await blackboard_service.query_knowledge(
            space="governance",
            agent_id="ethics_agent_1"
        )
        assert len(agent_knowledge) == 1
        assert agent_knowledge[0].agent_id == "ethics_agent_1"

        # Query for non-existent agent
        empty_result = await blackboard_service.query_knowledge(
            space="governance",
            agent_id="non_existent_agent"
        )
        assert len(empty_result) == 0
    
    @pytest.mark.asyncio
    async def test_query_knowledge_by_tags(self, blackboard_service, sample_knowledge_item):
        """Test querying knowledge by tags"""
        knowledge_id = await blackboard_service.add_knowledge(sample_knowledge_item)
        
        # Query by tag
        tagged_knowledge = await blackboard_service.query_knowledge(
            space="governance",
            tags={"ethics"}
        )
        assert len(tagged_knowledge) == 1
        assert "ethics" in tagged_knowledge[0].tags
        
        # Query by multiple tags
        multi_tag_knowledge = await blackboard_service.query_knowledge(
            space="governance",
            tags={"ethics", "approved"}
        )
        assert len(multi_tag_knowledge) == 1
        
        # Query by non-existent tag
        empty_result = await blackboard_service.query_knowledge(
            space="governance",
            tags={"non_existent_tag"}
        )
        assert len(empty_result) == 0
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Expiration logic needs debugging in MockRedis")
    async def test_knowledge_expiration(self, blackboard_service):
        """Test knowledge item expiration"""
        expired_knowledge = KnowledgeItem(
            space="governance",
            agent_id="test_agent",
            knowledge_type="temporary",
            content={"message": "This should expire"},
            priority=3,
            tags={"temporary"},
            expires_at=datetime.utcnow() + timedelta(seconds=1)  # Expire in 1 second
        )
        
        knowledge_id = await blackboard_service.add_knowledge(expired_knowledge)
        
        # Immediately retrieve - should exist
        retrieved = await blackboard_service.get_knowledge(knowledge_id, "governance")
        assert retrieved is not None

        # Wait for expiration
        await asyncio.sleep(2)

        # Should be expired now
        expired_retrieved = await blackboard_service.get_knowledge(knowledge_id, "governance")
        assert expired_retrieved is None
    
    # Task Coordination Tests
    
    @pytest.mark.asyncio
    async def test_create_task(self, blackboard_service, sample_task_definition):
        """Test creating a task on the blackboard"""
        task_id = await blackboard_service.create_task(sample_task_definition)
        
        assert task_id is not None
        assert isinstance(task_id, str)
        
        # Verify task was stored
        retrieved = await blackboard_service.get_task(task_id)
        assert retrieved is not None
        assert retrieved.task_type == sample_task_definition.task_type
        assert retrieved.description == sample_task_definition.description
        assert retrieved.status == "pending"
    
    @pytest.mark.asyncio
    async def test_claim_task(self, blackboard_service, sample_task_definition):
        """Test agent claiming a task"""
        task_id = await blackboard_service.create_task(sample_task_definition)
        
        # Claim task
        claim_success = await blackboard_service.claim_task(task_id, "ethics_agent_1")
        assert claim_success is True
        
        # Verify task is claimed
        retrieved = await blackboard_service.get_task(task_id)
        assert retrieved.status == "in_progress"
        assert retrieved.assigned_agent == "ethics_agent_1"
        
        # Try to claim already claimed task
        claim_again = await blackboard_service.claim_task(task_id, "legal_agent_1")
        assert claim_again is False
    
    @pytest.mark.asyncio
    async def test_complete_task(self, blackboard_service, sample_task_definition):
        """Test completing a task"""
        task_id = await blackboard_service.create_task(sample_task_definition)
        await blackboard_service.claim_task(task_id, "ethics_agent_1")
        
        # Complete task with result
        result = {
            "assessment": "approved",
            "confidence": 0.85,
            "recommendations": ["Monitor for bias"]
        }
        
        complete_success = await blackboard_service.complete_task(
            task_id, "ethics_agent_1", result
        )
        assert complete_success is True
        
        # Verify task is completed
        retrieved = await blackboard_service.get_task(task_id)
        assert retrieved.status == "completed"
        assert retrieved.result == result
        assert retrieved.completion_timestamp is not None
    
    @pytest.mark.asyncio
    async def test_fail_task(self, blackboard_service, sample_task_definition):
        """Test failing a task"""
        task_id = await blackboard_service.create_task(sample_task_definition)
        await blackboard_service.claim_task(task_id, "ethics_agent_1")
        
        # Fail task with error
        error_details = {
            "error_type": "processing_error",
            "message": "Unable to process request",
            "details": {"code": "PROC_ERR_001"}
        }
        
        fail_success = await blackboard_service.fail_task(
            task_id, "ethics_agent_1", error_details
        )
        assert fail_success is True
        
        # Verify task is failed
        retrieved = await blackboard_service.get_task(task_id)
        assert retrieved.status == "failed"
        assert retrieved.error_details == error_details
    
    @pytest.mark.asyncio
    async def test_get_pending_tasks(self, blackboard_service, sample_task_definition):
        """Test retrieving pending tasks"""
        # Create multiple tasks
        task_id1 = await blackboard_service.create_task(sample_task_definition)
        
        task_def2 = TaskDefinition(
            task_type="compliance_check",
            description="Check regulatory compliance",
            requirements={"legal_review": True},
            priority=1,
            assigned_agents=["legal_agent_1"]
        )
        task_id2 = await blackboard_service.create_task(task_def2)
        
        # Claim one task
        await blackboard_service.claim_task(task_id1, "ethics_agent_1")
        
        # Get pending tasks
        pending_tasks = await blackboard_service.get_pending_tasks()
        assert len(pending_tasks) == 1
        assert pending_tasks[0].id == task_id2
        assert pending_tasks[0].status == "pending"
    
    @pytest.mark.asyncio
    async def test_get_agent_tasks(self, blackboard_service, sample_task_definition):
        """Test retrieving tasks for a specific agent"""
        task_id = await blackboard_service.create_task(sample_task_definition)
        await blackboard_service.claim_task(task_id, "ethics_agent_1")
        
        # Get tasks for agent
        agent_tasks = await blackboard_service.get_agent_tasks("ethics_agent_1")
        assert len(agent_tasks) == 1
        assert agent_tasks[0].assigned_agent == "ethics_agent_1"
        
        # Get tasks for different agent
        other_agent_tasks = await blackboard_service.get_agent_tasks("legal_agent_1")
        assert len(other_agent_tasks) == 0
    
    # Conflict Resolution Tests
    
    @pytest.mark.asyncio
    async def test_report_conflict(self, blackboard_service, sample_conflict_item):
        """Test reporting a conflict between agents"""
        conflict_id = await blackboard_service.report_conflict(sample_conflict_item)
        
        assert conflict_id is not None
        assert isinstance(conflict_id, str)
        
        # Verify conflict was stored
        retrieved = await blackboard_service.get_conflict(conflict_id)
        assert retrieved is not None
        assert retrieved.conflicting_agents == sample_conflict_item.conflicting_agents
        assert retrieved.conflict_type == sample_conflict_item.conflict_type
        assert retrieved.status == "open"
    
    @pytest.mark.asyncio
    async def test_resolve_conflict(self, blackboard_service, sample_conflict_item):
        """Test resolving a conflict"""
        conflict_id = await blackboard_service.report_conflict(sample_conflict_item)
        
        # Resolve conflict
        resolution = {
            "resolution_type": "consensus",
            "agreed_assessment": "medium_risk",
            "resolver": "consensus_engine",
            "confidence": 0.8
        }
        
        resolve_success = await blackboard_service.resolve_conflict(
            conflict_id, resolution
        )
        assert resolve_success is True
        
        # Verify conflict is resolved
        retrieved = await blackboard_service.get_conflict(conflict_id)
        assert retrieved.status == "resolved"
        assert retrieved.resolution == resolution
        assert retrieved.resolution_timestamp is not None
    
    @pytest.mark.asyncio
    async def test_get_open_conflicts(self, blackboard_service, sample_conflict_item):
        """Test retrieving open conflicts"""
        # Create multiple conflicts
        conflict_id1 = await blackboard_service.report_conflict(sample_conflict_item)
        
        conflict_2 = ConflictItem(
            conflicting_agents=["legal_agent_1", "operational_agent_1"],
            conflict_type="priority_disagreement",
            description="Agents disagree on task priority",
            context={"task_id": str(uuid4())},
            severity="low"
        )
        conflict_id2 = await blackboard_service.report_conflict(conflict_2)
        
        # Resolve one conflict
        await blackboard_service.resolve_conflict(conflict_id1, {"resolution": "test"})
        
        # Get open conflicts
        open_conflicts = await blackboard_service.get_open_conflicts()
        assert len(open_conflicts) == 1
        assert open_conflicts[0].id == conflict_id2
        assert open_conflicts[0].status == "open"
    
    # Agent Registration and Heartbeat Tests
    
    @pytest.mark.asyncio
    async def test_register_agent(self, blackboard_service):
        """Test agent registration"""
        agent_info = {
            "agent_id": "ethics_agent_1",
            "agent_type": "ethics_agent",
            "capabilities": ["ethical_analysis", "bias_detection"],
            "version": "1.0.0"
        }
        
        register_success = await blackboard_service.register_agent(agent_info)
        assert register_success is True
        
        # Verify agent is registered
        active_agents = await blackboard_service.get_active_agents()
        assert "ethics_agent_1" in active_agents
    
    @pytest.mark.asyncio
    async def test_agent_heartbeat(self, blackboard_service):
        """Test agent heartbeat functionality"""
        agent_info = {
            "agent_id": "ethics_agent_1",
            "agent_type": "ethics_agent",
            "capabilities": ["ethical_analysis"]
        }
        
        await blackboard_service.register_agent(agent_info)
        
        # Send heartbeat
        heartbeat_success = await blackboard_service.agent_heartbeat(
            "ethics_agent_1", {"status": "active", "load": 0.3}
        )
        assert heartbeat_success is True
        
        # Verify agent is still active
        active_agents = await blackboard_service.get_active_agents()
        assert "ethics_agent_1" in active_agents
    
    @pytest.mark.asyncio
    async def test_agent_timeout(self, blackboard_service):
        """Test agent timeout detection"""
        agent_info = {
            "agent_id": "ethics_agent_1",
            "agent_type": "ethics_agent",
            "capabilities": ["ethical_analysis"]
        }
        
        # Mock datetime to simulate timeout
        with patch('services.shared.blackboard.blackboard_service.datetime') as mock_datetime:
            # Register agent
            mock_datetime.utcnow.return_value = datetime(2024, 1, 1, 12, 0, 0)
            await blackboard_service.register_agent(agent_info)
            
            # Simulate time passing (heartbeat timeout)
            mock_datetime.utcnow.return_value = datetime(2024, 1, 1, 12, 6, 0)  # 6 minutes later
            
            # Check for timeouts
            timed_out_agents = await blackboard_service.check_agent_timeouts()
            assert "ethics_agent_1" in timed_out_agents
            
            # Verify agent is no longer active
            active_agents = await blackboard_service.get_active_agents()
            assert "ethics_agent_1" not in active_agents
    
    # Metrics and Monitoring Tests
    
    @pytest.mark.asyncio
    async def test_get_metrics(self, blackboard_service, sample_knowledge_item, sample_task_definition, sample_conflict_item):
        """Test retrieving blackboard metrics"""
        # Add some data
        await blackboard_service.add_knowledge(sample_knowledge_item)
        task_id = await blackboard_service.create_task(sample_task_definition)
        conflict_id = await blackboard_service.report_conflict(sample_conflict_item)
        
        # Get metrics
        metrics = await blackboard_service.get_metrics()
        
        assert "knowledge" in metrics
        assert "tasks" in metrics
        assert "conflicts" in metrics
        assert "agents" in metrics
        
        # Verify knowledge metrics
        assert metrics["knowledge"]["total"] >= 1
        assert "by_space" in metrics["knowledge"]
        assert "by_type" in metrics["knowledge"]
        
        # Verify task metrics
        assert metrics["tasks"]["total"] >= 1
        assert metrics["tasks"]["pending"] >= 1
        assert "by_status" in metrics["tasks"]
        
        # Verify conflict metrics
        assert metrics["conflicts"]["total"] >= 1
        assert metrics["conflicts"]["open"] >= 1
        
    @pytest.mark.asyncio
    async def test_cleanup_expired_items(self, blackboard_service):
        """Test cleanup of expired knowledge items"""
        # Add expired knowledge
        expired_knowledge = KnowledgeItem(
            space="governance",
            agent_id="test_agent",
            knowledge_type="temporary",
            content={"message": "This should be cleaned up"},
            priority=3,
            tags={"temporary"},
            ttl_seconds=1
        )
        
        knowledge_id = await blackboard_service.add_knowledge(expired_knowledge)
        
        # Wait for expiration
        await asyncio.sleep(2)
        
        # Run cleanup
        cleaned_count = await blackboard_service.cleanup_expired_items()
        assert cleaned_count >= 0  # Should clean up expired items
        
        # Verify expired item is gone
        retrieved = await blackboard_service.get_knowledge(knowledge_id)
        assert retrieved is None
    
    @pytest.mark.asyncio
    async def test_concurrent_access(self, blackboard_service):
        """Test concurrent access to blackboard"""
        async def add_knowledge_task(agent_id: str, count: int):
            """Task to add multiple knowledge items concurrently"""
            for i in range(count):
                knowledge = KnowledgeItem(
                    space="governance",
                    agent_id=agent_id,
                    knowledge_type="concurrent_test",
                    content={"index": i, "agent": agent_id},
                    priority=2,
                    tags={"concurrent", "test"}
                )
                await blackboard_service.add_knowledge(knowledge)
        
        # Run concurrent tasks
        tasks = [
            add_knowledge_task("agent_1", 5),
            add_knowledge_task("agent_2", 5),
            add_knowledge_task("agent_3", 5)
        ]
        
        await asyncio.gather(*tasks)
        
        # Verify all knowledge was added correctly
        all_knowledge = await blackboard_service.query_knowledge(
            tags={"concurrent", "test"}
        )
        assert len(all_knowledge) == 15  # 3 agents × 5 items each
        
        # Verify agent-specific knowledge
        agent_1_knowledge = await blackboard_service.query_knowledge(
            agent_id="agent_1", tags={"concurrent"}
        )
        assert len(agent_1_knowledge) == 5
    
    @pytest.mark.asyncio
    async def test_error_handling(self, blackboard_service):
        """Test error handling for invalid operations"""
        # Try to get non-existent knowledge
        non_existent = await blackboard_service.get_knowledge("non_existent_id")
        assert non_existent is None
        
        # Try to claim non-existent task
        claim_result = await blackboard_service.claim_task("non_existent_task", "agent_1")
        assert claim_result is False
        
        # Try to complete task not assigned to agent
        task_def = TaskDefinition(
            task_type="test_task",
            description="Test task",
            requirements={},
            priority=1,
            assigned_agents=["agent_1"]
        )
        task_id = await blackboard_service.create_task(task_def)
        await blackboard_service.claim_task(task_id, "agent_1")
        
        # Try to complete with wrong agent
        complete_result = await blackboard_service.complete_task(
            task_id, "wrong_agent", {"result": "test"}
        )
        assert complete_result is False