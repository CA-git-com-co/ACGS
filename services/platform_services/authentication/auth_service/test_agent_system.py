#!/usr/bin/env python3
"""
Agent Identity Management System Test

Simple test script to validate the agent management system functionality.
Tests agent creation, authentication, and basic operations.
"""

import asyncio
import sys

# Add the app directory to the path
sys.path.append("app")

from app.models.agent import AgentStatus, AgentType
from app.schemas.agent import AgentCreate, AgentStatusUpdate, AgentUpdate
from app.services.agent_service import AgentService


class MockUser:
    """Mock user for testing."""

    def __init__(self, user_id: int, username: str, email: str):
        self.id = user_id
        self.username = username
        self.email = email
        self.is_superuser = False
        self.permissions = [
            "agent:create",
            "agent:read",
            "agent:update",
            "agent:manage_status",
        ]


class MockDB:
    """Mock database session for testing."""

    def __init__(self):
        self.users = {1: MockUser(1, "test_user", "test@example.com")}
        self.agents = {}
        self.audit_logs = []
        self.committed = False

    async def execute(self, query):
        """Mock execute method."""

        class MockResult:
            def scalar_one_or_none(self):
                # Return user if querying for user
                if hasattr(query, "column_descriptions"):
                    return self.users.get(1)
                return None

            def scalars(self):
                class MockScalars:
                    def all(self):
                        return list(self.agents.values())

                return MockScalars()

            def scalar(self):
                return len(self.agents)

        return MockResult()

    async def flush(self):
        """Mock flush method."""
        pass

    async def commit(self):
        """Mock commit method."""
        self.committed = True

    def add(self, obj):
        """Mock add method."""
        if hasattr(obj, "agent_id"):
            # It's an agent
            if not hasattr(obj, "id"):
                obj.id = f"agent-{len(self.agents) + 1}"
            self.agents[obj.agent_id] = obj
        elif hasattr(obj, "event_type"):
            # It's an audit log
            self.audit_logs.append(obj)


async def test_agent_creation():
    """Test agent creation functionality."""
    print("🧪 Testing Agent Creation...")

    service = AgentService()
    db = MockDB()

    # Create test agent data
    agent_data = AgentCreate(
        agent_id="test-coding-agent-001",
        name="Test Coding Agent",
        description="A test coding agent for validation",
        agent_type=AgentType.CODING_AGENT,
        version="1.0.0",
        owner_user_id=1,
        responsible_team="Test Team",
        contact_email="test@example.com",
        capabilities=["code_generation", "code_review", "testing"],
        permissions=["read:code", "write:code"],
        role_assignments=["developer"],
        allowed_services=["github", "gitlab"],
        allowed_operations=["create_pr", "review_code"],
        max_requests_per_minute=50,
        max_concurrent_operations=3,
        compliance_level="high",
        requires_human_approval=True,
        tags=["coding", "test", "development"],
    )

    try:
        # Create agent
        agent, api_key = await service.create_agent(
            db=db, agent_data=agent_data, created_by_user_id=1, client_ip="127.0.0.1"
        )

        print("✅ Agent created successfully:")
        print(f"   - Agent ID: {agent.agent_id}")
        print(f"   - Name: {agent.name}")
        print(f"   - Type: {agent.agent_type}")
        print(f"   - Status: {agent.status}")
        print(f"   - API Key: {api_key[:20]}...")
        print(f"   - Owner: {agent.owner_user_id}")
        print(f"   - Capabilities: {agent.capabilities}")
        print(f"   - Compliance Level: {agent.compliance_level}")

        # Verify agent properties
        assert agent.agent_id == "test-coding-agent-001"
        assert agent.name == "Test Coding Agent"
        assert agent.agent_type == AgentType.CODING_AGENT.value
        assert agent.status == AgentStatus.PENDING.value
        assert agent.owner_user_id == 1
        assert len(agent.capabilities) == 3
        assert agent.compliance_level == "high"
        assert agent.requires_human_approval is True
        assert api_key.startswith("acgs_agent_")

        print("✅ All agent creation assertions passed!")
        return agent, api_key

    except Exception as e:
        print(f"❌ Agent creation failed: {e}")
        raise


async def test_agent_update():
    """Test agent update functionality."""
    print("\n🧪 Testing Agent Update...")

    service = AgentService()
    db = MockDB()

    # First create an agent
    agent_data = AgentCreate(
        agent_id="test-update-agent",
        name="Original Name",
        description="Original description",
        agent_type=AgentType.POLICY_AGENT,
        owner_user_id=1,
        capabilities=["policy_enforcement"],
        permissions=["read:policies"],
        compliance_level="standard",
    )

    agent, _ = await service.create_agent(
        db=db, agent_data=agent_data, created_by_user_id=1
    )

    # Update agent
    update_data = AgentUpdate(
        name="Updated Name",
        description="Updated description",
        capabilities=["policy_enforcement", "compliance_monitoring"],
        permissions=["read:policies", "write:policies"],
        compliance_level="high",
    )

    try:
        updated_agent = await service.update_agent(
            db=db,
            agent_id="test-update-agent",
            agent_data=update_data,
            updated_by_user_id=1,
        )

        print("✅ Agent updated successfully:")
        print(f"   - Name: {updated_agent.name}")
        print(f"   - Description: {updated_agent.description}")
        print(f"   - Capabilities: {updated_agent.capabilities}")
        print(f"   - Compliance Level: {updated_agent.compliance_level}")

        # Verify updates
        assert updated_agent.name == "Updated Name"
        assert updated_agent.description == "Updated description"
        assert len(updated_agent.capabilities) == 2
        assert "compliance_monitoring" in updated_agent.capabilities
        assert updated_agent.compliance_level == "high"

        print("✅ All agent update assertions passed!")
        return updated_agent

    except Exception as e:
        print(f"❌ Agent update failed: {e}")
        raise


async def test_agent_status_management():
    """Test agent status management."""
    print("\n🧪 Testing Agent Status Management...")

    service = AgentService()
    db = MockDB()

    # Create agent
    agent_data = AgentCreate(
        agent_id="test-status-agent",
        name="Status Test Agent",
        agent_type=AgentType.MONITORING_AGENT,
        owner_user_id=1,
    )

    agent, _ = await service.create_agent(
        db=db, agent_data=agent_data, created_by_user_id=1
    )

    # Test status transitions
    status_updates = [
        (AgentStatus.ACTIVE, "Activating agent for testing"),
        (AgentStatus.SUSPENDED, "Temporarily suspending for maintenance"),
        (AgentStatus.ACTIVE, "Reactivating after maintenance"),
        (AgentStatus.RETIRED, "Retiring agent after testing"),
    ]

    try:
        for new_status, reason in status_updates:
            status_update = AgentStatusUpdate(status=new_status, reason=reason)

            updated_agent = await service.update_agent_status(
                db=db,
                agent_id="test-status-agent",
                status_update=status_update,
                updated_by_user_id=1,
            )

            print(f"✅ Status updated to {new_status.value}: {reason}")
            assert updated_agent.status == new_status.value

        print("✅ All status transition assertions passed!")
        return updated_agent

    except Exception as e:
        print(f"❌ Agent status management failed: {e}")
        raise


async def test_agent_authentication():
    """Test agent authentication."""
    print("\n🧪 Testing Agent Authentication...")

    service = AgentService()
    db = MockDB()

    # Create agent
    agent_data = AgentCreate(
        agent_id="test-auth-agent",
        name="Auth Test Agent",
        agent_type=AgentType.INTEGRATION_AGENT,
        owner_user_id=1,
    )

    agent, api_key = await service.create_agent(
        db=db, agent_data=agent_data, created_by_user_id=1
    )

    # Activate agent
    status_update = AgentStatusUpdate(
        status=AgentStatus.ACTIVE, reason="Activating for auth test"
    )
    await service.update_agent_status(
        db=db,
        agent_id="test-auth-agent",
        status_update=status_update,
        updated_by_user_id=1,
    )

    try:
        # Test successful authentication
        auth_agent = await service.authenticate_agent(
            db=db, agent_id="test-auth-agent", api_key=api_key, client_ip="127.0.0.1"
        )

        assert auth_agent is not None
        assert auth_agent.agent_id == "test-auth-agent"
        print("✅ Agent authentication successful")

        # Test failed authentication with wrong key
        failed_auth = await service.authenticate_agent(
            db=db,
            agent_id="test-auth-agent",
            api_key="wrong_key",
            client_ip="127.0.0.1",
        )

        assert failed_auth is None
        print("✅ Failed authentication with wrong key (expected)")

        print("✅ All authentication assertions passed!")
        return auth_agent

    except Exception as e:
        print(f"❌ Agent authentication failed: {e}")
        raise


async def main():
    """Run all tests."""
    print("🚀 Starting Agent Identity Management System Tests")
    print("=" * 60)

    try:
        # Run all tests
        await test_agent_creation()
        await test_agent_update()
        await test_agent_status_management()
        await test_agent_authentication()

        print("\n" + "=" * 60)
        print("🎉 All tests passed successfully!")
        print("\n📋 Test Summary:")
        print("   ✅ Agent Creation")
        print("   ✅ Agent Update")
        print("   ✅ Status Management")
        print("   ✅ Authentication")
        print("\n🏗️ Agent Identity Management System is ready for deployment!")

    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
