"""
Test Suite for Specialized Agent Roles

Tests the implementation of domain-specific agent roles following MetaGPT patterns:
- Policy Manager role functionality
- Architect role functionality
- Validator role functionality
- Implementer role functionality
- Role factory and registry operations
- Constitutional compliance integration
"""

import asyncio
from unittest.mock import AsyncMock

import pytest
from services.shared.agents.specialized_agent_roles import (
    AgentRoleType,
    PolicyManagerRole,
    SpecializedRoleFactory,
    SpecializedRoleRegistry,
)
from services.shared.constitutional_safety_framework import (
    ConstitutionalSafetyValidator,
)
from services.shared.monitoring.enhanced_performance_monitor import (
    EnhancedPerformanceMonitor,
)
from services.shared.security.enhanced_audit_logging import EnhancedAuditLogger


class TestSpecializedAgentRoles:
    """Test suite for specialized agent roles"""

    @pytest.fixture
    async def mock_dependencies(self):
        """Create mock dependencies for testing"""
        safety_validator = AsyncMock(spec=ConstitutionalSafetyValidator)
        safety_validator.validate_content.return_value = {
            "is_compliant": True,
            "score": 0.95,
        }

        audit_logger = AsyncMock(spec=EnhancedAuditLogger)
        audit_logger.log_security_event.return_value = None

        performance_monitor = AsyncMock(spec=EnhancedPerformanceMonitor)
        performance_monitor.record_metric.return_value = None

        return safety_validator, audit_logger, performance_monitor

    @pytest.mark.asyncio
    async def test_policy_manager_role_creation(self, mock_dependencies):
        """Test Policy Manager role creation and initialization"""
        safety_validator, audit_logger, performance_monitor = mock_dependencies

        # Create Policy Manager role
        role = SpecializedRoleFactory.create_role(
            AgentRoleType.POLICY_MANAGER,
            "test_policy_manager_001",
            safety_validator,
            audit_logger,
            performance_monitor,
        )

        assert isinstance(role, PolicyManagerRole)
        assert role.role_id == "test_policy_manager_001"
        assert role.role_spec.role_type == AgentRoleType.POLICY_MANAGER
        assert not role.is_active

        # Initialize role
        await role.initialize()
        assert role.is_active

        # Verify audit logging
        audit_logger.log_security_event.assert_called_once()
        call_args = audit_logger.log_security_event.call_args[0][0]
        assert call_args["event_type"] == "specialized_role_activated"
        assert call_args["role_type"] == "policy_manager"

    @pytest.mark.asyncio
    async def test_policy_manager_requirements_analysis(self, mock_dependencies):
        """Test Policy Manager requirements analysis functionality"""
        safety_validator, audit_logger, performance_monitor = mock_dependencies

        role = SpecializedRoleFactory.create_role(
            AgentRoleType.POLICY_MANAGER,
            "test_policy_manager_002",
            safety_validator,
            audit_logger,
            performance_monitor,
        )

        await role.initialize()

        # Test requirements analysis task
        task_data = {
            "task_id": "req_analysis_001",
            "task_type": "requirements_analysis",
            "requirements": {
                "functional": ["user_authentication", "data_processing"],
                "non_functional": ["performance", "security"],
                "constraints": ["budget_limit", "timeline"],
            },
        }

        result = await role.execute_task(task_data)

        assert result["task_result"] == "requirements_analysis_completed"
        assert "analysis" in result
        assert "recommendations" in result
        assert result["constitutional_hash"] == "cdd01ef066bc6cf2"

        # Verify performance tracking
        performance_monitor.record_metric.assert_called()

    @pytest.mark.asyncio
    async def test_architect_role_system_design(self, mock_dependencies):
        """Test Architect role system design functionality"""
        safety_validator, audit_logger, performance_monitor = mock_dependencies

        role = SpecializedRoleFactory.create_role(
            AgentRoleType.ARCHITECT,
            "test_architect_001",
            safety_validator,
            audit_logger,
            performance_monitor,
        )

        await role.initialize()

        # Test system design task
        task_data = {
            "task_id": "sys_design_001",
            "task_type": "system_design",
            "requirements": {
                "scalability": "high",
                "performance": "sub_5ms_latency",
                "security": "enterprise_grade",
            },
        }

        result = await role.execute_task(task_data)

        assert result["task_result"] == "system_architecture_designed"
        assert "architecture" in result
        assert "technical_decisions" in result
        assert result["constitutional_hash"] == "cdd01ef066bc6cf2"

    @pytest.mark.asyncio
    async def test_validator_role_compliance_validation(self, mock_dependencies):
        """Test Validator role compliance validation functionality"""
        safety_validator, audit_logger, performance_monitor = mock_dependencies

        role = SpecializedRoleFactory.create_role(
            AgentRoleType.VALIDATOR,
            "test_validator_001",
            safety_validator,
            audit_logger,
            performance_monitor,
        )

        await role.initialize()

        # Test compliance validation task
        task_data = {
            "task_id": "compliance_val_001",
            "task_type": "compliance_validation",
            "validation_target": {
                "implementation": "policy_engine_v1",
                "requirements": ["gdpr_compliance", "security_standards"],
            },
        }

        result = await role.execute_task(task_data)

        assert result["task_result"] == "compliance_validation_completed"
        assert "compliance_results" in result
        assert "overall_score" in result
        assert result["constitutional_hash"] == "cdd01ef066bc6cf2"

    @pytest.mark.asyncio
    async def test_implementer_role_policy_implementation(self, mock_dependencies):
        """Test Implementer role policy implementation functionality"""
        safety_validator, audit_logger, performance_monitor = mock_dependencies

        role = SpecializedRoleFactory.create_role(
            AgentRoleType.IMPLEMENTER,
            "test_implementer_001",
            safety_validator,
            audit_logger,
            performance_monitor,
        )

        await role.initialize()

        # Test policy implementation task
        task_data = {
            "task_id": "policy_impl_001",
            "task_type": "policy_implementation",
            "policy_specification": {
                "policy_name": "data_governance_policy",
                "implementation_steps": [
                    "configure_access_controls",
                    "setup_audit_logging",
                ],
                "deployment_target": "production",
            },
        }

        result = await role.execute_task(task_data)

        assert result["task_result"] == "policy_implementation_completed"
        assert "implementation_result" in result
        assert "deployment_status" in result
        assert result["constitutional_hash"] == "cdd01ef066bc6cf2"

    @pytest.mark.asyncio
    async def test_role_registry_operations(self, mock_dependencies):
        """Test role registry functionality"""
        safety_validator, audit_logger, performance_monitor = mock_dependencies

        registry = SpecializedRoleRegistry()

        # Create and register multiple roles
        policy_manager = SpecializedRoleFactory.create_role(
            AgentRoleType.POLICY_MANAGER,
            "pm_001",
            safety_validator,
            audit_logger,
            performance_monitor,
        )

        architect = SpecializedRoleFactory.create_role(
            AgentRoleType.ARCHITECT,
            "arch_001",
            safety_validator,
            audit_logger,
            performance_monitor,
        )

        registry.register_role(policy_manager)
        registry.register_role(architect)

        # Test registry operations
        assert registry.get_role("pm_001") == policy_manager
        assert registry.get_role("arch_001") == architect
        assert registry.get_role("nonexistent") is None

        # Test role type filtering
        policy_managers = registry.get_roles_by_type(AgentRoleType.POLICY_MANAGER)
        assert len(policy_managers) == 1
        assert policy_managers[0] == policy_manager

        architects = registry.get_roles_by_type(AgentRoleType.ARCHITECT)
        assert len(architects) == 1
        assert architects[0] == architect

        # Test workflow assignment
        registry.assign_roles_to_workflow("workflow_001", ["pm_001", "arch_001"])
        workflow_roles = registry.get_workflow_roles("workflow_001")
        assert len(workflow_roles) == 2
        assert policy_manager in workflow_roles
        assert architect in workflow_roles

    @pytest.mark.asyncio
    async def test_constitutional_compliance_validation(self, mock_dependencies):
        """Test constitutional compliance validation across all roles"""
        safety_validator, audit_logger, performance_monitor = mock_dependencies

        # Test with non-compliant task
        safety_validator.validate_content.return_value = {
            "is_compliant": False,
            "score": 0.3,
        }

        role = SpecializedRoleFactory.create_role(
            AgentRoleType.POLICY_MANAGER,
            "test_compliance_001",
            safety_validator,
            audit_logger,
            performance_monitor,
        )

        await role.initialize()

        # Task should fail due to constitutional compliance violation
        task_data = {
            "task_id": "non_compliant_task",
            "task_type": "requirements_analysis",
            "requirements": {"malicious": "content"},
        }

        with pytest.raises(
            ValueError, match="Task violates constitutional constraints"
        ):
            await role.execute_task(task_data)

    @pytest.mark.asyncio
    async def test_role_performance_metrics(self, mock_dependencies):
        """Test role performance metrics tracking"""
        safety_validator, audit_logger, performance_monitor = mock_dependencies

        role = SpecializedRoleFactory.create_role(
            AgentRoleType.VALIDATOR,
            "test_metrics_001",
            safety_validator,
            audit_logger,
            performance_monitor,
        )

        await role.initialize()

        # Execute successful task
        task_data = {
            "task_id": "metrics_test_001",
            "task_type": "compliance_validation",
            "validation_target": {"test": "data"},
        }

        await role.execute_task(task_data)

        # Check role status and metrics
        status = role.get_role_status()
        assert status["role_id"] == "test_metrics_001"
        assert status["role_type"] == "validator"
        assert status["is_active"] is True
        assert status["completed_tasks"] == 1
        assert status["performance_metrics"]["tasks_completed"] == 1
        assert status["performance_metrics"]["tasks_failed"] == 0
        assert status["constitutional_hash"] == "cdd01ef066bc6cf2"


if __name__ == "__main__":
    # Run basic functionality test
    async def test_basic_functionality():
        """Basic functionality test for specialized roles"""
        print("Testing Specialized Agent Roles...")

        # Mock dependencies
        safety_validator = AsyncMock()
        safety_validator.validate_content.return_value = {
            "is_compliant": True,
            "score": 0.95,
        }

        audit_logger = AsyncMock()
        performance_monitor = AsyncMock()

        # Test role creation
        role = SpecializedRoleFactory.create_role(
            AgentRoleType.POLICY_MANAGER,
            "test_role_001",
            safety_validator,
            audit_logger,
            performance_monitor,
        )

        await role.initialize()
        print(f"✓ Created and initialized {role.role_spec.role_type.value} role")

        # Test task execution
        task_data = {
            "task_id": "test_task_001",
            "task_type": "requirements_analysis",
            "requirements": {"test": "data"},
        }

        result = await role.execute_task(task_data)
        print(f"✓ Executed task: {result['task_result']}")

        # Test registry
        registry = SpecializedRoleRegistry()
        registry.register_role(role)
        retrieved_role = registry.get_role("test_role_001")
        assert retrieved_role == role
        print("✓ Role registry operations working")

        print("All tests passed! ✅")

    # Run the test
    asyncio.run(test_basic_functionality())
