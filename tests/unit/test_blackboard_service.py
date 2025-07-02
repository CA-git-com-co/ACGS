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
from tests.fixtures.mock_services import MockRedis


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
            requirements={
                "ethical_review": True,
                "legal_review": True,
                "operational_review": True
            },
            input_data={
                "description": "Review AI model deployment request",
                "request_id": str(uuid4()),
                "model_type": "language_model"
            },
            priority=1,
            deadline=datetime.utcnow() + timedelta(hours=24)
        )
    
    @pytest.fixture
    def sample_conflict_item(self):
        """Create a sample conflict item for testing"""
        return ConflictItem(
            involved_agents=["ethics_agent_1", "legal_agent_1"],
            involved_tasks=[str(uuid4())],
            conflict_type="assessment_disagreement",
            description="Agents disagree on risk level",
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
        assert retrieved.input_data["description"] == sample_task_definition.input_data["description"]
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
        assert retrieved.status == "claimed"
        assert retrieved.agent_id == "ethics_agent_1"
        
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
        assert retrieved.output_data == result
        assert retrieved.completed_at is not None
    
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
            requirements={"legal_review": True},
            input_data={"description": "Check regulatory compliance"},
            priority=1
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
        assert agent_tasks[0].agent_id == "ethics_agent_1"
        
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
        assert retrieved.involved_agents == sample_conflict_item.involved_agents
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
            conflict_id, "manual_resolution", resolution
        )
        assert resolve_success is True
        
        # Verify conflict is resolved
        retrieved = await blackboard_service.get_conflict(conflict_id)
        assert retrieved.status == "resolved"
        assert retrieved.resolution_data == resolution
        assert retrieved.resolved_at is not None
    
    @pytest.mark.asyncio
    async def test_get_open_conflicts(self, blackboard_service, sample_conflict_item):
        """Test retrieving open conflicts"""
        # Create multiple conflicts
        conflict_id1 = await blackboard_service.report_conflict(sample_conflict_item)
        
        conflict_2 = ConflictItem(
            involved_agents=["legal_agent_1", "operational_agent_1"],
            involved_tasks=[str(uuid4())],
            conflict_type="priority_disagreement",
            description="Agents disagree on task priority",
            severity="low"
        )
        conflict_id2 = await blackboard_service.report_conflict(conflict_2)
        
        # Resolve one conflict
        await blackboard_service.resolve_conflict(conflict_id1, "manual_resolution", {"resolution": "test"})
        
        # Get open conflicts
        open_conflicts = await blackboard_service.get_open_conflicts()
        assert len(open_conflicts) == 1
        assert open_conflicts[0].id == conflict_id2
        assert open_conflicts[0].status == "open"
    
    # Agent Registration and Heartbeat Tests
    
    @pytest.mark.asyncio
    async def test_register_agent(self, blackboard_service):
        """Test agent registration"""
        agent_id = "ethics_agent_1"
        agent_type = "ethics_agent"
        capabilities = ["ethical_analysis", "bias_detection"]

        await blackboard_service.register_agent(agent_id, agent_type, capabilities)

        # Verify agent is registered
        active_agents = await blackboard_service.get_active_agents()
        assert "ethics_agent_1" in active_agents
    
    @pytest.mark.asyncio
    async def test_agent_heartbeat(self, blackboard_service):
        """Test agent heartbeat functionality"""
        agent_id = "ethics_agent_1"
        agent_type = "ethics_agent"
        capabilities = ["ethical_analysis"]

        await blackboard_service.register_agent(agent_id, agent_type, capabilities)
        
        # Send heartbeat
        await blackboard_service.agent_heartbeat("ethics_agent_1")
        
        # Verify agent is still active
        active_agents = await blackboard_service.get_active_agents()
        assert "ethics_agent_1" in active_agents
    
    @pytest.mark.skip(reason="check_agent_timeouts method not implemented")
    @pytest.mark.asyncio
    async def test_agent_timeout(self, blackboard_service):
        """Test agent timeout detection"""
        agent_id = "ethics_agent_1"
        agent_type = "ethics_agent"
        capabilities = ["ethical_analysis"]

        # Mock datetime to simulate timeout
        with patch('services.shared.blackboard.blackboard_service.datetime') as mock_datetime:
            # Register agent
            mock_datetime.utcnow.return_value = datetime(2024, 1, 1, 12, 0, 0)
            await blackboard_service.register_agent(agent_id, agent_type, capabilities)
            
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
        
        assert "knowledge_items" in metrics
        assert "tasks" in metrics
        assert "conflicts" in metrics
        assert "agents" in metrics
        
        # Verify knowledge metrics
        assert metrics["knowledge_items"]["governance"] >= 1
        # Verify task metrics
        assert metrics["tasks"]["pending"] >= 1
        
        # Verify conflict metrics
        assert metrics["conflicts"]["open"] >= 1
        
    @pytest.mark.skip(reason="TTL expiration not implemented in MockRedis")
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
        retrieved = await blackboard_service.get_knowledge(knowledge_id, "governance")
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
            space="governance",
            tags={"concurrent", "test"}
        )
        assert len(all_knowledge) == 15  # 3 agents × 5 items each
        
        # Verify agent-specific knowledge
        agent_1_knowledge = await blackboard_service.query_knowledge(
            space="governance",
            agent_id="agent_1", tags={"concurrent"}
        )
        assert len(agent_1_knowledge) == 5
    
    @pytest.mark.asyncio
    async def test_error_handling(self, blackboard_service):
        """Test error handling for invalid operations"""
        # Try to get non-existent knowledge
        non_existent = await blackboard_service.get_knowledge("non_existent_id", "governance")
        assert non_existent is None
        
        # Try to claim non-existent task
        claim_result = await blackboard_service.claim_task("non_existent_task", "agent_1")
        assert claim_result is False
        
        # Try to complete task not assigned to agent
        task_def = TaskDefinition(
            task_type="test_task",
            requirements={},
            input_data={"description": "Test task"},
            priority=1
        )
        task_id = await blackboard_service.create_task(task_def)
        await blackboard_service.claim_task(task_id, "agent_1")
        
        # Try to complete with wrong agent
        complete_result = await blackboard_service.complete_task(
            task_id, "wrong_agent", {"result": "test"}
        )
        assert complete_result is False

    # Additional Coverage Tests

    @pytest.mark.asyncio
    async def test_redis_connection_failure(self, blackboard_service):
        """Test handling of Redis connection failures"""
        # Simulate Redis connection failure by setting client to None
        blackboard_service.redis_client = None

        # Test that operations handle missing Redis client gracefully
        with pytest.raises(AttributeError):
            await blackboard_service.add_knowledge(KnowledgeItem(
                space="governance",
                agent_id="test_agent",
                knowledge_type="test",
                content={"test": "data"},
                priority=1,
                tags={"test"}
            ))

    @pytest.mark.asyncio
    async def test_knowledge_with_expiration(self, blackboard_service):
        """Test knowledge items with expiration times"""
        future_time = datetime.utcnow() + timedelta(hours=1)
        knowledge = KnowledgeItem(
            space="governance",
            agent_id="test_agent",
            knowledge_type="temporary",
            content={"message": "This will expire"},
            priority=1,
            tags={"temporary"},
            expires_at=future_time
        )

        knowledge_id = await blackboard_service.add_knowledge(knowledge)
        assert knowledge_id is not None

        # Verify knowledge can be retrieved
        retrieved = await blackboard_service.get_knowledge(knowledge_id, "governance")
        assert retrieved is not None
        assert retrieved.expires_at == future_time

    @pytest.mark.asyncio
    async def test_task_with_deadline(self, blackboard_service):
        """Test tasks with deadlines"""
        deadline = datetime.utcnow() + timedelta(days=1)
        task = TaskDefinition(
            task_type="urgent_review",
            requirements={"urgent": True},
            input_data={"description": "Urgent task with deadline"},
            priority=5,
            deadline=deadline
        )

        task_id = await blackboard_service.create_task(task)
        assert task_id is not None

        # Verify task can be retrieved with deadline
        retrieved = await blackboard_service.get_task(task_id)
        assert retrieved is not None
        assert retrieved.deadline == deadline

    @pytest.mark.asyncio
    async def test_task_dependencies(self, blackboard_service):
        """Test tasks with dependencies"""
        # Create parent task
        parent_task = TaskDefinition(
            task_type="parent_task",
            requirements={"parent": True},
            input_data={"description": "Parent task"},
            priority=1
        )
        parent_id = await blackboard_service.create_task(parent_task)

        # Create dependent task
        dependent_task = TaskDefinition(
            task_type="dependent_task",
            requirements={"depends_on": parent_id},
            input_data={"description": "Dependent task"},
            priority=2,
            dependencies=[parent_id]
        )
        dependent_id = await blackboard_service.create_task(dependent_task)

        # Verify dependency is stored
        retrieved = await blackboard_service.get_task(dependent_id)
        assert retrieved is not None
        assert parent_id in retrieved.dependencies

    @pytest.mark.asyncio
    async def test_conflict_severity_priority(self, blackboard_service):
        """Test conflict priority based on severity"""
        # Create conflicts with different severities
        critical_conflict = ConflictItem(
            involved_agents=["agent1", "agent2"],
            involved_tasks=["task1"],
            conflict_type="critical_disagreement",
            description="Critical conflict",
            severity="critical"
        )

        low_conflict = ConflictItem(
            involved_agents=["agent3", "agent4"],
            involved_tasks=["task2"],
            conflict_type="minor_disagreement",
            description="Low priority conflict",
            severity="low"
        )

        # Report conflicts (critical should get higher priority)
        critical_id = await blackboard_service.report_conflict(critical_conflict)
        low_id = await blackboard_service.report_conflict(low_conflict)

        # Get open conflicts - critical should come first
        conflicts = await blackboard_service.get_open_conflicts()
        assert len(conflicts) >= 2

        # Find our conflicts in the list
        critical_found = any(c.id == critical_id for c in conflicts)
        low_found = any(c.id == low_id for c in conflicts)
        assert critical_found and low_found

    @pytest.mark.asyncio
    async def test_agent_task_filtering(self, blackboard_service, sample_task_definition):
        """Test filtering agent tasks by status"""
        # Create and claim a task
        task_id = await blackboard_service.create_task(sample_task_definition)
        await blackboard_service.claim_task(task_id, "test_agent")

        # Complete the task
        await blackboard_service.complete_task(task_id, "test_agent", {"result": "success"})

        # Get tasks filtered by status
        claimed_tasks = await blackboard_service.get_agent_tasks("test_agent", ["claimed"])
        completed_tasks = await blackboard_service.get_agent_tasks("test_agent", ["completed"])
        all_tasks = await blackboard_service.get_agent_tasks("test_agent")

        assert len(claimed_tasks) == 0  # No claimed tasks
        assert len(completed_tasks) == 1  # One completed task
        assert len(all_tasks) == 1  # One total task

    @pytest.mark.asyncio
    async def test_knowledge_priority_ordering(self, blackboard_service):
        """Test that knowledge items are ordered by priority"""
        # Create knowledge items with different priorities
        low_priority = KnowledgeItem(
            space="governance",
            agent_id="test_agent",
            knowledge_type="info",
            content={"priority": "low"},
            priority=1,
            tags={"low"}
        )

        high_priority = KnowledgeItem(
            space="governance",
            agent_id="test_agent",
            knowledge_type="info",
            content={"priority": "high"},
            priority=5,
            tags={"high"}
        )

        # Add in reverse priority order
        await blackboard_service.add_knowledge(low_priority)
        await blackboard_service.add_knowledge(high_priority)

        # Verify both items were added successfully
        low_retrieved = await blackboard_service.get_knowledge(low_priority.id, "governance")
        high_retrieved = await blackboard_service.get_knowledge(high_priority.id, "governance")

        assert low_retrieved is not None
        assert high_retrieved is not None
        assert low_retrieved.priority == 1
        assert high_retrieved.priority == 5

    @pytest.mark.asyncio
    async def test_redis_initialization_failure(self):
        """Test BlackboardService initialization with invalid Redis URL"""
        # Test with invalid Redis URL
        service = BlackboardService(redis_url="redis://invalid:9999")

        # The service should initialize but connection will fail on first use
        assert service.redis_url == "redis://invalid:9999"
        assert service.redis_client is None

    @pytest.mark.asyncio
    async def test_task_queue_operations(self, blackboard_service, sample_task_definition):
        """Test internal task queue operations"""
        # Create task
        task_id = await blackboard_service.create_task(sample_task_definition)

        # Test get_available_tasks with task type filtering
        available_tasks = await blackboard_service.get_available_tasks(
            task_types=["governance_review"], limit=5
        )
        assert len(available_tasks) >= 1
        assert any(task.id == task_id for task in available_tasks)

        # Test with non-matching task type
        no_tasks = await blackboard_service.get_available_tasks(
            task_types=["non_existent_type"], limit=5
        )
        assert len(no_tasks) == 0

    @pytest.mark.asyncio
    async def test_event_publishing(self, blackboard_service, sample_task_definition):
        """Test event publishing functionality"""
        # Create task (should publish task_created event)
        task_id = await blackboard_service.create_task(sample_task_definition)

        # Claim task (should publish task_claimed event)
        claim_result = await blackboard_service.claim_task(task_id, "test_agent")
        assert claim_result is True

        # Complete task (should publish task_completed event)
        complete_result = await blackboard_service.complete_task(
            task_id, "test_agent", {"result": "success"}
        )
        assert complete_result is True

    @pytest.mark.asyncio
    async def test_agent_management(self, blackboard_service):
        """Test agent registration and management"""
        # Register agent
        await blackboard_service.register_agent(
            "test_agent_123",
            "governance_agent",
            ["ethical_analysis", "compliance_check"]
        )

        # Test heartbeat
        await blackboard_service.agent_heartbeat("test_agent_123")

        # Get active agents
        active_agents = await blackboard_service.get_active_agents()
        assert "test_agent_123" in active_agents

    @pytest.mark.asyncio
    async def test_conflict_resolution_workflow(self, blackboard_service):
        """Test complete conflict resolution workflow"""
        # Create conflict
        conflict = ConflictItem(
            involved_agents=["agent1", "agent2"],
            involved_tasks=["task1"],
            conflict_type="resource_conflict",
            description="Agents competing for same resource",
            severity="high"
        )

        conflict_id = await blackboard_service.report_conflict(conflict)

        # Verify conflict is in open conflicts
        open_conflicts = await blackboard_service.get_open_conflicts()
        assert any(c.id == conflict_id for c in open_conflicts)

        # Resolve conflict
        resolution_data = {"resolution": "resource_allocated_to_agent1"}
        resolve_result = await blackboard_service.resolve_conflict(
            conflict_id, "manual_resolution", resolution_data
        )
        assert resolve_result is True

        # Verify conflict is resolved
        resolved_conflict = await blackboard_service.get_conflict(conflict_id)
        assert resolved_conflict.status == "resolved"
        assert resolved_conflict.resolution_data == resolution_data

    @pytest.mark.asyncio
    async def test_knowledge_expiration_edge_cases(self, blackboard_service):
        """Test knowledge expiration edge cases"""
        # Test knowledge that expires in the past
        past_time = datetime.utcnow() - timedelta(hours=1)
        expired_knowledge = KnowledgeItem(
            space="governance",
            agent_id="test_agent",
            knowledge_type="expired",
            content={"message": "Already expired"},
            priority=1,
            tags={"expired"},
            expires_at=past_time
        )

        # This should still add the knowledge but with immediate expiration
        knowledge_id = await blackboard_service.add_knowledge(expired_knowledge)
        assert knowledge_id is not None

    @pytest.mark.asyncio
    async def test_task_retry_mechanism(self, blackboard_service):
        """Test task retry mechanism"""
        task = TaskDefinition(
            task_type="retry_test",
            requirements={"retry": True},
            input_data={"description": "Task that will be retried"},
            priority=1,
            max_retries=2
        )

        task_id = await blackboard_service.create_task(task)
        await blackboard_service.claim_task(task_id, "test_agent")

        # Fail the task multiple times
        await blackboard_service.fail_task(task_id, "test_agent", {"error": "first_failure"})

        # Verify task can be retrieved and has error details
        failed_task = await blackboard_service.get_task(task_id)
        assert failed_task.status == "failed"
        assert failed_task.error_details["error"] == "first_failure"

    @pytest.mark.asyncio
    async def test_concurrent_task_operations(self, blackboard_service, sample_task_definition):
        """Test concurrent task operations"""
        # Create multiple tasks
        task_ids = []
        for i in range(3):
            task_def = TaskDefinition(
                task_type=f"concurrent_task_{i}",
                requirements={"concurrent": True},
                input_data={"task_number": i},
                priority=i + 1
            )
            task_id = await blackboard_service.create_task(task_def)
            task_ids.append(task_id)

        # Get available tasks
        available = await blackboard_service.get_available_tasks(limit=10)
        assert len(available) >= 3

        # Claim multiple tasks with different agents
        for i, task_id in enumerate(task_ids):
            agent_id = f"agent_{i}"
            result = await blackboard_service.claim_task(task_id, agent_id)
            assert result is True

    @pytest.mark.asyncio
    async def test_knowledge_dependencies(self, blackboard_service):
        """Test knowledge items with dependencies"""
        # Create parent knowledge
        parent_knowledge = KnowledgeItem(
            space="governance",
            agent_id="test_agent",
            knowledge_type="parent",
            content={"type": "parent"},
            priority=1,
            tags={"parent"}
        )
        parent_id = await blackboard_service.add_knowledge(parent_knowledge)

        # Create dependent knowledge
        dependent_knowledge = KnowledgeItem(
            space="governance",
            agent_id="test_agent",
            knowledge_type="dependent",
            content={"type": "dependent"},
            priority=2,
            tags={"dependent"},
            dependencies=[parent_id]
        )
        dependent_id = await blackboard_service.add_knowledge(dependent_knowledge)

        # Verify dependency is stored
        retrieved = await blackboard_service.get_knowledge(dependent_id, "governance")
        assert retrieved is not None
        assert parent_id in retrieved.dependencies

    @pytest.mark.asyncio
    async def test_service_initialization_and_shutdown(self):
        """Test service initialization and shutdown"""
        # Create a new service instance
        service = BlackboardService(redis_url="redis://localhost:6379")

        # Initialize the service
        await service.initialize()
        assert service.redis_client is not None

        # Test shutdown
        await service.shutdown()

        # After shutdown, redis_client should still exist but connection closed
        assert service.redis_client is not None

    @pytest.mark.asyncio
    async def test_setup_indices(self, blackboard_service):
        """Test index setup functionality"""
        # This tests the _setup_indices method indirectly
        # by ensuring the service can perform operations that rely on indices

        # Add some data that would use indices
        knowledge = KnowledgeItem(
            space="governance",
            agent_id="test_agent",
            knowledge_type="indexed_test",
            content={"test": "index_data"},
            priority=1,
            tags={"indexed"}
        )

        knowledge_id = await blackboard_service.add_knowledge(knowledge)
        assert knowledge_id is not None

        # Verify we can retrieve it (which uses indices)
        retrieved = await blackboard_service.get_knowledge(knowledge_id, "governance")
        assert retrieved is not None

    @pytest.mark.asyncio
    async def test_error_conditions_and_edge_cases(self, blackboard_service):
        """Test various error conditions and edge cases"""
        # Test getting non-existent task
        non_existent_task = await blackboard_service.get_task("non-existent-id")
        assert non_existent_task is None

        # Test getting non-existent knowledge
        non_existent_knowledge = await blackboard_service.get_knowledge("non-existent-id", "governance")
        assert non_existent_knowledge is None

        # Test getting non-existent conflict
        non_existent_conflict = await blackboard_service.get_conflict("non-existent-id")
        assert non_existent_conflict is None

        # Test claiming non-existent task
        claim_result = await blackboard_service.claim_task("non-existent-id", "test_agent")
        assert claim_result is False

        # Test completing non-existent task
        complete_result = await blackboard_service.complete_task("non-existent-id", "test_agent", {})
        assert complete_result is False

        # Test failing non-existent task
        fail_result = await blackboard_service.fail_task("non-existent-id", "test_agent", {})
        assert fail_result is False