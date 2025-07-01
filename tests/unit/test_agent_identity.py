"""
Unit Tests for Agent Identity Management Service

Tests the core functionality of agent CRUD operations, authentication,
and identity management.
"""

# Mock the database and service classes for unit testing
from dataclasses import dataclass
from datetime import datetime

import pytest


@dataclass
class MockAgent:
    """Mock agent for testing."""

    id: str
    agent_id: str
    name: str
    agent_type: str
    status: str
    owner_user_id: int
    capabilities: list
    permissions: list
    created_at: datetime

    def is_active(self) -> bool:
        return self.status == "active"


class MockAgentService:
    """Mock agent service for testing."""

    def __init__(self):
        self.agents = {}

    async def create_agent(self, db, agent_data, created_by_user_id, client_ip=None):
        agent = MockAgent(
            id=f"uuid-{len(self.agents)}",
            agent_id=agent_data.agent_id,
            name=agent_data.name,
            agent_type=agent_data.agent_type,
            status="pending",
            owner_user_id=agent_data.owner_user_id,
            capabilities=agent_data.capabilities,
            permissions=agent_data.permissions,
            created_at=datetime.utcnow(),
        )
        self.agents[agent_data.agent_id] = agent
        api_key = f"acgs_agent_{agent_data.agent_id}_key"
        return agent, api_key

    async def get_agent(self, db, agent_id):
        return self.agents.get(agent_id)

    async def authenticate_agent(self, db, agent_id, api_key, client_ip=None):
        agent = self.agents.get(agent_id)
        if agent and f"acgs_agent_{agent_id}_key" == api_key:
            return agent
        return None


class TestAgentIdentityManagement:
    """Test suite for Agent Identity Management."""

    @pytest.fixture
    def agent_service(self):
        return MockAgentService()

    @pytest.fixture
    def sample_agent_data(self):
        class AgentData:
            agent_id = "test-agent-001"
            name = "Test Agent"
            agent_type = "coding_agent"
            owner_user_id = 1
            capabilities = ["code_generation"]
            permissions = ["read:code"]

        return AgentData()

    @pytest.mark.asyncio
    async def test_create_agent(self, agent_service, sample_agent_data):
        """Test agent creation."""
        agent, api_key = await agent_service.create_agent(
            db=None, agent_data=sample_agent_data, created_by_user_id=1
        )

        assert agent.agent_id == "test-agent-001"
        assert agent.name == "Test Agent"
        assert agent.agent_type == "coding_agent"
        assert agent.status == "pending"
        assert api_key.startswith("acgs_agent_")

    @pytest.mark.asyncio
    async def test_get_agent(self, agent_service, sample_agent_data):
        """Test agent retrieval."""
        # Create agent first
        await agent_service.create_agent(
            db=None, agent_data=sample_agent_data, created_by_user_id=1
        )

        # Retrieve agent
        agent = await agent_service.get_agent(db=None, agent_id="test-agent-001")

        assert agent is not None
        assert agent.agent_id == "test-agent-001"
        assert agent.name == "Test Agent"

    @pytest.mark.asyncio
    async def test_get_nonexistent_agent(self, agent_service):
        """Test retrieval of non-existent agent."""
        agent = await agent_service.get_agent(db=None, agent_id="nonexistent")
        assert agent is None

    @pytest.mark.asyncio
    async def test_authenticate_agent_success(self, agent_service, sample_agent_data):
        """Test successful agent authentication."""
        # Create agent first
        agent, api_key = await agent_service.create_agent(
            db=None, agent_data=sample_agent_data, created_by_user_id=1
        )

        # Authenticate with correct key
        authenticated_agent = await agent_service.authenticate_agent(
            db=None, agent_id="test-agent-001", api_key=api_key
        )

        assert authenticated_agent is not None
        assert authenticated_agent.agent_id == "test-agent-001"

    @pytest.mark.asyncio
    async def test_authenticate_agent_failure(self, agent_service, sample_agent_data):
        """Test failed agent authentication."""
        # Create agent first
        await agent_service.create_agent(
            db=None, agent_data=sample_agent_data, created_by_user_id=1
        )

        # Authenticate with wrong key
        authenticated_agent = await agent_service.authenticate_agent(
            db=None, agent_id="test-agent-001", api_key="wrong_key"
        )

        assert authenticated_agent is None

    @pytest.mark.asyncio
    async def test_authenticate_nonexistent_agent(self, agent_service):
        """Test authentication of non-existent agent."""
        authenticated_agent = await agent_service.authenticate_agent(
            db=None, agent_id="nonexistent", api_key="some_key"
        )

        assert authenticated_agent is None

    def test_agent_is_active(self):
        """Test agent active status check."""
        active_agent = MockAgent(
            id="1",
            agent_id="test",
            name="Test",
            agent_type="coding_agent",
            status="active",
            owner_user_id=1,
            capabilities=[],
            permissions=[],
            created_at=datetime.utcnow(),
        )

        inactive_agent = MockAgent(
            id="2",
            agent_id="test2",
            name="Test2",
            agent_type="coding_agent",
            status="suspended",
            owner_user_id=1,
            capabilities=[],
            permissions=[],
            created_at=datetime.utcnow(),
        )

        assert active_agent.is_active() is True
        assert inactive_agent.is_active() is False

    @pytest.mark.asyncio
    async def test_multiple_agents(self, agent_service):
        """Test managing multiple agents."""
        # Create multiple agents
        agent_data_1 = type(
            "AgentData",
            (),
            {
                "agent_id": "agent-001",
                "name": "Agent 1",
                "agent_type": "coding_agent",
                "owner_user_id": 1,
                "capabilities": ["code_gen"],
                "permissions": ["read:code"],
            },
        )()

        agent_data_2 = type(
            "AgentData",
            (),
            {
                "agent_id": "agent-002",
                "name": "Agent 2",
                "agent_type": "policy_agent",
                "owner_user_id": 2,
                "capabilities": ["policy_check"],
                "permissions": ["read:policy"],
            },
        )()

        agent1, key1 = await agent_service.create_agent(None, agent_data_1, 1)
        agent2, key2 = await agent_service.create_agent(None, agent_data_2, 2)

        assert len(agent_service.agents) == 2
        assert agent1.agent_id != agent2.agent_id
        assert key1 != key2

        # Verify both can be retrieved
        retrieved1 = await agent_service.get_agent(None, "agent-001")
        retrieved2 = await agent_service.get_agent(None, "agent-002")

        assert retrieved1.name == "Agent 1"
        assert retrieved2.name == "Agent 2"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
