"""
Unit tests for APGF (Agentic Policy Generation Feature) integration.

Tests the core functionality of the dynamic agent system, policy generation,
and tool routing components within the ACGS constitutional AI framework.
"""
# Constitutional Hash: cdd01ef066bc6cf2

import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, Mock

import pytest

from services.shared.agents import (
    AgentCommunication,
    AgentConfig,
    AgentTask,
    APGFOrchestrator,
    DynamicAgent,
    GeneratedPolicy,
    PolicyBuilder,
    ToolRouter,
)
from services.shared.agents.dynamic_agent import AgentState, TaskPriority, TaskStatus
from services.shared.agents.policy_builder import PolicyScope, PolicyType
from services.shared.agents.tool_router import (
    PermissionLevel,
    ToolExecutionStatus,
    ToolSafetyLevel,
)
from services.shared.constitutional_safety_framework import (
    ConstitutionalSafetyFramework,
)
from services.shared.monitoring.intelligent_alerting_system import (
    IntelligentAlertingSystem,
)
from services.shared.security.enhanced_audit_logging import EnhancedAuditLogger
from services.shared.security.unified_input_validation import EnhancedInputValidator


class TestPolicyBuilder:
    """Test PolicyBuilder functionality"""

    @pytest.fixture
    async def policy_builder(self):
        """Create PolicyBuilder instance for testing"""
        constitutional_framework = Mock(spec=ConstitutionalSafetyFramework)
        audit_logger = Mock(spec=EnhancedAuditLogger)
        alerting_system = Mock(spec=IntelligentAlertingSystem)

        # Mock async methods
        constitutional_framework.get_principles = AsyncMock(
            return_value=[
                {"id": "transparency", "name": "Transparency"},
                {"id": "accountability", "name": "Accountability"},
            ]
        )
        constitutional_framework.evaluate_compliance = AsyncMock(return_value=0.85)
        audit_logger.log_security_event = AsyncMock()
        alerting_system.send_alert = AsyncMock()

        builder = PolicyBuilder(constitutional_framework, audit_logger, alerting_system)
        await builder.initialize()
        return builder

    @pytest.mark.asyncio
    async def test_agent_config_creation(self, policy_builder):
        """Test agent configuration creation"""
        agent_request = {
            "name": "Test Agent",
            "role": "policy_analyst",
            "capabilities": ["policy_analysis", "data_processing"],
            "domain": "governance",
            "priority": "high",
        }

        config = await policy_builder.create_agent_config(agent_request)

        assert isinstance(config, AgentConfig)
        assert config.name == "Test Agent"
        assert config.role == "policy_analyst"
        assert "policy_analysis" in config.capabilities
        assert "constitutional_compliance_required" in config.constraints
        assert len(config.tools_allowed) > 0

    @pytest.mark.asyncio
    async def test_policy_generation(self, policy_builder):
        """Test policy generation"""
        request = {
            "type": "governance",
            "scope": "domain_specific",
            "priority": "medium",
            "requirements": {
                "objective": "Improve democratic participation",
                "rules": ["ensure_transparency", "protect_privacy"],
            },
        }

        context = {
            "domain": "digital_governance",
            "stakeholders": ["citizens", "government"],
        }

        policy = await policy_builder.generate_policy(request, context)

        assert isinstance(policy, GeneratedPolicy)
        assert policy.policy_type == PolicyType.GOVERNANCE
        assert policy.scope == PolicyScope.DOMAIN_SPECIFIC
        assert policy.constitutional_compliance_score > 0
        assert policy.policy_id in policy_builder.generated_policies

    @pytest.mark.asyncio
    async def test_policy_validation(self, policy_builder):
        """Test policy validation"""
        # First generate a policy
        request = {
            "type": "governance",
            "scope": "global",
            "priority": "high",
            "requirements": {"objective": "Test policy"},
        }

        policy = await policy_builder.generate_policy(request, {})

        # Now validate it
        validation_result = await policy_builder.validate_policy(policy)

        assert "constitutional_compliance" in validation_result
        assert "safety_checks" in validation_result
        assert "conflict_analysis" in validation_result
        assert "recommendations" in validation_result
        assert isinstance(validation_result["approval_required"], bool)


class TestToolRouter:
    """Test ToolRouter functionality"""

    @pytest.fixture
    def tool_router(self):
        """Create ToolRouter instance for testing"""
        audit_logger = Mock(spec=EnhancedAuditLogger)
        alerting_system = Mock(spec=IntelligentAlertingSystem)
        input_validator = Mock(spec=EnhancedInputValidator)

        # Mock async methods
        audit_logger.log_security_event = AsyncMock()
        alerting_system.send_alert = AsyncMock()
        input_validator.validate_and_sanitize = AsyncMock(
            return_value={
                "is_valid": True,
                "sanitized_data": {"test": "data"},
                "sanitization_applied": False,
            }
        )

        return ToolRouter(audit_logger, alerting_system, input_validator)

    def test_tool_registry(self, tool_router):
        """Test tool registry functionality"""
        registry = tool_router.registry

        # Check that default tools are registered
        assert len(registry.tools) > 0
        assert "data_analyzer" in registry.tools
        assert "report_generator" in registry.tools

        # Test tool retrieval
        data_analyzer = registry.get_tool("data_analyzer")
        assert data_analyzer is not None
        assert data_analyzer.safety_level == ToolSafetyLevel.MEDIUM

    def test_tool_filtering(self, tool_router):
        """Test tool filtering by safety level and permissions"""
        registry = tool_router.registry

        # Filter by safety level
        safe_tools = registry.list_tools(safety_level=ToolSafetyLevel.LOW)
        assert len(safe_tools) > 0
        assert all(tool.safety_level == ToolSafetyLevel.LOW for tool in safe_tools)

        # Filter by permissions
        readonly_tools = registry.list_tools(
            required_permissions=[PermissionLevel.READ_ONLY]
        )
        assert len(readonly_tools) > 0
        assert all(
            PermissionLevel.READ_ONLY in tool.required_permissions
            for tool in readonly_tools
        )

    @pytest.mark.asyncio
    async def test_tool_execution_request(self, tool_router):
        """Test tool execution request handling"""
        from services.shared.agents.tool_router import ToolExecutionRequest

        request = ToolExecutionRequest(
            request_id="test-request-001",
            agent_id="test-agent-001",
            tool_id="report_generator",
            parameters={"template": "default", "data": {"test": "value"}},
            priority=5,
            timeout_seconds=30,
            callback_url=None,
            metadata={"test": True},
            requested_at=datetime.utcnow(),
        )

        result = await tool_router.route_tool_request(request)

        assert result.request_id == request.request_id
        assert result.tool_id == request.tool_id
        assert result.agent_id == request.agent_id
        assert result.status in [
            ToolExecutionStatus.COMPLETED,
            ToolExecutionStatus.FAILED,
        ]


class TestDynamicAgent:
    """Test DynamicAgent functionality"""

    @pytest.fixture
    async def dynamic_agent(self):
        """Create DynamicAgent instance for testing"""
        # Create mock dependencies
        config = AgentConfig(
            agent_id="test-agent-001",
            name="Test Agent",
            role="test_role",
            capabilities=["policy_analysis", "data_processing"],
            constraints={"constitutional_compliance_required": True},
            tools_allowed=["data_analyzer", "report_generator"],
            resource_limits={"max_memory_mb": 512, "max_cpu_percent": 20},
            reporting_level="standard",
            escalation_threshold=0.8,
            created_at=datetime.utcnow(),
        )

        policy_builder = Mock(spec=PolicyBuilder)
        tool_router = Mock(spec=ToolRouter)
        constitutional_framework = Mock(spec=ConstitutionalSafetyFramework)
        audit_logger = Mock(spec=EnhancedAuditLogger)
        alerting_system = Mock(spec=IntelligentAlertingSystem)

        # Mock async methods
        constitutional_framework.evaluate_compliance = AsyncMock(return_value=0.85)
        audit_logger.log_security_event = AsyncMock()
        alerting_system.send_alert = AsyncMock()

        agent = DynamicAgent(
            config=config,
            policy_builder=policy_builder,
            tool_router=tool_router,
            constitutional_framework=constitutional_framework,
            audit_logger=audit_logger,
            alerting_system=alerting_system,
        )

        await agent.initialize()
        return agent

    @pytest.mark.asyncio
    async def test_agent_initialization(self, dynamic_agent):
        """Test agent initialization"""
        assert dynamic_agent.state == AgentState.ACTIVE
        assert dynamic_agent.config.agent_id == "test-agent-001"
        assert len(dynamic_agent.task_queue) == 0
        assert len(dynamic_agent.active_tasks) == 0

    @pytest.mark.asyncio
    async def test_task_assignment(self, dynamic_agent):
        """Test task assignment to agent"""
        task = AgentTask(
            task_id="test-task-001",
            agent_id=dynamic_agent.config.agent_id,
            task_type="analysis",
            description="Test task",
            priority=TaskPriority.MEDIUM,
            parameters={"test_param": "value"},
            required_tools=["data_analyzer"],
            constitutional_constraints=["transparency"],
            deadline=None,
            dependencies=[],
            status=TaskStatus.PENDING,
            result=None,
            error_message=None,
            created_at=datetime.utcnow(),
            started_at=None,
            completed_at=None,
            execution_logs=[],
        )

        success = await dynamic_agent.assign_task(task)

        assert success is True
        assert len(dynamic_agent.task_queue) == 1
        assert task in dynamic_agent.task_queue

    @pytest.mark.asyncio
    async def test_agent_communication(self, dynamic_agent):
        """Test agent communication"""
        message = AgentCommunication(
            communication_id="test-comm-001",
            sender_agent_id="other-agent-001",
            receiver_agent_id=dynamic_agent.config.agent_id,
            message_type="status_inquiry",
            content={"request": "status"},
            priority=TaskPriority.MEDIUM,
            requires_response=True,
            response=None,
            timestamp=datetime.utcnow(),
            resolved=False,
        )

        await dynamic_agent.receive_message(message)

        assert len(dynamic_agent.message_inbox) == 1
        assert message in dynamic_agent.message_inbox

    @pytest.mark.asyncio
    async def test_agent_status(self, dynamic_agent):
        """Test agent status retrieval"""
        status = await dynamic_agent.get_status()

        assert "agent_id" in status
        assert "state" in status
        assert "role" in status
        assert "capabilities" in status
        assert "uptime_seconds" in status
        assert status["agent_id"] == dynamic_agent.config.agent_id
        assert status["state"] == AgentState.ACTIVE.value


class TestAPGFOrchestrator:
    """Test APGFOrchestrator functionality"""

    @pytest.fixture
    async def apgf_orchestrator(self):
        """Create APGFOrchestrator instance for testing"""
        constitutional_framework = Mock(spec=ConstitutionalSafetyFramework)
        audit_logger = Mock(spec=EnhancedAuditLogger)
        alerting_system = Mock(spec=IntelligentAlertingSystem)
        input_validator = Mock(spec=EnhancedInputValidator)
        service_orchestrator = Mock()

        # Mock async methods
        constitutional_framework.get_principles = AsyncMock(return_value=[])
        constitutional_framework.evaluate_compliance = AsyncMock(return_value=0.85)
        audit_logger.log_security_event = AsyncMock()
        alerting_system.send_alert = AsyncMock()
        input_validator.validate_and_sanitize = AsyncMock(
            return_value={
                "is_valid": True,
                "sanitized_data": {
                    "name": "Test Workflow",
                    "requirements": {"objective": "Test"},
                    "coordination_strategy": "sequential",
                },
                "sanitization_applied": False,
            }
        )

        orchestrator = APGFOrchestrator(
            constitutional_framework=constitutional_framework,
            audit_logger=audit_logger,
            alerting_system=alerting_system,
            input_validator=input_validator,
            service_orchestrator=service_orchestrator,
        )

        await orchestrator.initialize()
        return orchestrator

    @pytest.mark.asyncio
    async def test_workflow_initiation(self, apgf_orchestrator):
        """Test policy generation workflow initiation"""
        request = {
            "name": "Test Policy Generation",
            "description": "Test workflow for policy generation",
            "requirements": {
                "objective": "Improve governance processes",
                "domain": "digital_governance",
            },
            "coordination_strategy": "sequential",
        }

        workflow_id = await apgf_orchestrator.initiate_policy_generation_workflow(
            request
        )

        assert workflow_id is not None
        assert workflow_id in apgf_orchestrator.active_workflows

        workflow = apgf_orchestrator.active_workflows[workflow_id]
        assert workflow.name == "Test Policy Generation"
        assert workflow.coordination_strategy.value == "sequential"

    @pytest.mark.asyncio
    async def test_agent_creation_through_orchestrator(self, apgf_orchestrator):
        """Test dynamic agent creation through orchestrator"""
        agent_spec = {
            "name": "Policy Analyst Agent",
            "role": "policy_analyst",
            "capabilities": ["policy_analysis", "research"],
            "priority": "medium",
        }

        agent_id = await apgf_orchestrator.create_dynamic_agent(agent_spec)

        assert agent_id is not None
        assert agent_id in apgf_orchestrator.active_agents
        assert agent_id in apgf_orchestrator.agent_pool

        agent = apgf_orchestrator.active_agents[agent_id]
        assert agent.config.name == "Policy Analyst Agent"
        assert agent.config.role == "policy_analyst"

    @pytest.mark.asyncio
    async def test_workflow_status_retrieval(self, apgf_orchestrator):
        """Test workflow status retrieval"""
        # First create a workflow
        request = {
            "name": "Status Test Workflow",
            "requirements": {"objective": "Test status"},
            "coordination_strategy": "sequential",
        }

        workflow_id = await apgf_orchestrator.initiate_policy_generation_workflow(
            request
        )

        # Wait a moment for workflow to start
        await asyncio.sleep(0.1)

        status = await apgf_orchestrator.get_workflow_status(workflow_id)

        assert "workflow_id" in status
        assert "name" in status
        assert "state" in status
        assert "progress_percentage" in status
        assert status["workflow_id"] == workflow_id
        assert status["name"] == "Status Test Workflow"


class TestIntegration:
    """Integration tests for APGF components"""

    @pytest.mark.asyncio
    async def test_end_to_end_policy_generation(self):
        """Test end-to-end policy generation workflow"""
        # This would be a comprehensive integration test
        # that tests the entire flow from workflow initiation
        # to policy generation and validation

        # For now, this is a placeholder that demonstrates
        # the expected integration flow

        # 1. Initialize orchestrator
        # 2. Create workflow
        # 3. Create agents
        # 4. Execute policy generation
        # 5. Validate results

        # This would require more setup and mocking
        # of external dependencies

    @pytest.mark.asyncio
    async def test_multi_agent_coordination(self):
        """Test multi-agent coordination"""
        # Test coordinating multiple agents
        # for complex policy generation tasks

    @pytest.mark.asyncio
    async def test_constitutional_compliance_integration(self):
        """Test constitutional compliance throughout the process"""
        # Test that constitutional compliance is maintained
        # throughout the entire policy generation process


if __name__ == "__main__":
    # Run tests with: python -m pytest tests/unit/test_apgf_integration.py -v
    pytest.main([__file__, "-v"])
