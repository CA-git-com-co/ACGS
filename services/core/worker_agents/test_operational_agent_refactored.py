"""
Test suite for the refactored operational agent implementation.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import pytest
from datetime import datetime, timezone
from unittest.mock import Mock, AsyncMock

from .operational_agent_refactored import (
    OperationalAgentRefactored,
    create_operational_agent,
    CONSTITUTIONAL_HASH,
)
from .operational_agent_handlers import (
    OperationalValidationHandler,
    PerformanceAnalysisHandler,
    InfrastructureAssessmentHandler,
    ImplementationPlanningHandler,
    DeploymentHandler,
    ConstitutionalComplianceHandler,
)
from ...shared.blackboard import BlackboardService, KnowledgeItem, TaskDefinition


class TestOperationalAgentRefactored:
    """Test suite for the refactored operational agent."""

    @pytest.fixture
    def mock_blackboard(self):
        """Mock blackboard service."""
        blackboard = Mock(spec=BlackboardService)
        blackboard.register_agent = AsyncMock()
        blackboard.unregister_agent = AsyncMock()
        blackboard.update_agent_status = AsyncMock()
        blackboard.get_available_tasks = AsyncMock(return_value=[])
        blackboard.claim_task = AsyncMock(return_value=True)
        blackboard.update_task_status = AsyncMock()
        blackboard.add_knowledge = AsyncMock()
        blackboard.get_agent_status = AsyncMock(return_value={"status": "active"})
        return blackboard

    @pytest.fixture
    def mock_constitutional_framework(self):
        """Mock constitutional safety validator."""
        framework = Mock()
        framework.validate_action = AsyncMock(return_value={"compliant": True})
        return framework

    @pytest.fixture
    def mock_performance_monitor(self):
        """Mock performance monitor."""
        monitor = Mock()
        monitor.get_agent_metrics = AsyncMock(return_value={"performance": "good"})
        return monitor

    @pytest.fixture
    def operational_agent(self, mock_blackboard, mock_constitutional_framework, mock_performance_monitor):
        """Create operational agent instance for testing."""
        return OperationalAgentRefactored(
            agent_id="test_agent",
            blackboard_service=mock_blackboard,
            constitutional_framework=mock_constitutional_framework,
            performance_monitor=mock_performance_monitor,
        )

    def test_initialization(self, operational_agent):
        """Test operational agent initialization."""
        assert operational_agent.agent_id == "test_agent"
        assert operational_agent.agent_type == "operational_agent"
        assert not operational_agent.is_running
        assert len(operational_agent.capabilities) > 0
        assert len(operational_agent.constitutional_principles) > 0
        assert len(operational_agent.task_handlers) > 0

    def test_handlers_initialization(self, operational_agent):
        """Test that all handlers are properly initialized."""
        assert isinstance(operational_agent.validation_handler, OperationalValidationHandler)
        assert isinstance(operational_agent.performance_handler, PerformanceAnalysisHandler)
        assert isinstance(operational_agent.infrastructure_handler, InfrastructureAssessmentHandler)
        assert isinstance(operational_agent.implementation_handler, ImplementationPlanningHandler)
        assert isinstance(operational_agent.deployment_handler, DeploymentHandler)
        assert isinstance(operational_agent.compliance_handler, ConstitutionalComplianceHandler)

    @pytest.mark.asyncio
    async def test_start_agent(self, operational_agent, mock_blackboard):
        """Test starting the operational agent."""
        await operational_agent.start()
        
        assert operational_agent.is_running
        mock_blackboard.register_agent.assert_called_once()
        
        # Verify registration parameters
        call_args = mock_blackboard.register_agent.call_args
        assert call_args[1]["agent_id"] == "test_agent"
        assert call_args[1]["agent_type"] == "operational_agent"
        assert len(call_args[1]["capabilities"]) > 0
        assert len(call_args[1]["constitutional_principles"]) > 0

    @pytest.mark.asyncio
    async def test_stop_agent(self, operational_agent, mock_blackboard):
        """Test stopping the operational agent."""
        await operational_agent.start()
        await operational_agent.stop()
        
        assert not operational_agent.is_running
        mock_blackboard.unregister_agent.assert_called_once_with("test_agent")

    @pytest.mark.asyncio
    async def test_process_operational_validation_task(self, operational_agent):
        """Test processing operational validation task."""
        task = TaskDefinition(
            task_id="test_task_1",
            task_type="operational_validation",
            task_data={
                "governance_request": {
                    "model_info": {
                        "resource_usage": {"memory_gb": 16, "cpu_cores": 4},
                        "performance": {"avg_latency_ms": 100},
                        "scalability": {"max_concurrent_requests": 200},
                    }
                }
            },
            priority=1,
        )
        
        result = await operational_agent.process_task(task)
        
        assert "approved" in result
        assert "risk_level" in result
        assert "confidence" in result
        assert "constitutional_compliance" in result
        assert result["constitutional_compliance"]["constitutional_hash"] == CONSTITUTIONAL_HASH

    @pytest.mark.asyncio
    async def test_process_performance_analysis_task(self, operational_agent):
        """Test processing performance analysis task."""
        task = TaskDefinition(
            task_id="test_task_2",
            task_type="performance_analysis",
            task_data={
                "governance_request": {
                    "model_info": {
                        "performance": {
                            "avg_latency_ms": 50,
                            "rps": 150,
                            "cpu_usage": 60,
                            "memory_gb": 8,
                        }
                    }
                }
            },
            priority=1,
        )
        
        result = await operational_agent.process_task(task)
        
        assert "analysis_complete" in result
        assert "performance_score" in result
        assert "latency_analysis" in result
        assert "throughput_analysis" in result
        assert "constitutional_compliance" in result

    @pytest.mark.asyncio
    async def test_process_infrastructure_assessment_task(self, operational_agent):
        """Test processing infrastructure assessment task."""
        task = TaskDefinition(
            task_id="test_task_3",
            task_type="infrastructure_assessment",
            task_data={
                "governance_request": {
                    "model_info": {
                        "resource_usage": {"cpu_cores": 8, "memory_gb": 16, "storage_gb": 500},
                        "network_requirements": {"bandwidth_mbps": 500},
                        "security": {"encryption_enabled": True},
                        "monitoring": {"metrics_enabled": True},
                    }
                }
            },
            priority=1,
        )
        
        result = await operational_agent.process_task(task)
        
        assert "assessment_complete" in result
        assert "overall_readiness" in result
        assert "readiness_score" in result
        assert "component_readiness" in result
        assert "constitutional_compliance" in result

    @pytest.mark.asyncio
    async def test_process_implementation_planning_task(self, operational_agent):
        """Test processing implementation planning task."""
        task = TaskDefinition(
            task_id="test_task_4",
            task_type="implementation_planning",
            task_data={
                "governance_request": {
                    "model_info": {
                        "resource_usage": {"cpu_cores": 4, "memory_gb": 8, "storage_gb": 200}
                    }
                }
            },
            priority=1,
        )
        
        result = await operational_agent.process_task(task)
        
        assert "plan_created" in result
        assert "plan_id" in result
        assert "phases" in result
        assert "resource_requirements" in result
        assert "rollback_plan" in result
        assert "constitutional_compliance" in result

    @pytest.mark.asyncio
    async def test_process_deployment_planning_task(self, operational_agent):
        """Test processing deployment planning task."""
        task = TaskDefinition(
            task_id="test_task_5",
            task_type="deployment_planning",
            task_data={
                "governance_request": {
                    "model_info": {
                        "resource_usage": {"cpu_cores": 4, "memory_gb": 8}
                    }
                }
            },
            priority=1,
        )
        
        result = await operational_agent.process_task(task)
        
        assert "deployment_plan_created" in result
        assert "deployment_id" in result
        assert "deployment_strategy" in result
        assert "deployment_steps" in result
        assert "scaling_configuration" in result
        assert "constitutional_compliance" in result

    @pytest.mark.asyncio
    async def test_process_unknown_task_type(self, operational_agent):
        """Test processing unknown task type."""
        task = TaskDefinition(
            task_id="test_task_unknown",
            task_type="unknown_task_type",
            task_data={},
            priority=1,
        )
        
        result = await operational_agent.process_task(task)
        
        assert "error" in result
        assert "No handler for task type" in result["error"]

    @pytest.mark.asyncio
    async def test_get_agent_status(self, operational_agent):
        """Test getting agent status."""
        status = await operational_agent.get_agent_status()
        
        assert status["agent_id"] == "test_agent"
        assert status["agent_type"] == "operational_agent"
        assert "is_running" in status
        assert "capabilities" in status
        assert "constitutional_principles" in status
        assert "handlers" in status
        assert status["constitutional_hash"] == CONSTITUTIONAL_HASH

    @pytest.mark.asyncio
    async def test_health_check(self, operational_agent):
        """Test health check functionality."""
        health = await operational_agent.health_check()
        
        assert "healthy" in health
        assert "agent_id" in health
        assert "handlers" in health
        assert "blackboard_connected" in health
        assert health["constitutional_hash"] == CONSTITUTIONAL_HASH

    @pytest.mark.asyncio
    async def test_get_performance_metrics(self, operational_agent):
        """Test getting performance metrics."""
        metrics = await operational_agent.get_performance_metrics()
        
        assert "agent_id" in metrics
        assert "uptime_seconds" in metrics
        assert "tasks_processed" in metrics
        assert metrics["constitutional_hash"] == CONSTITUTIONAL_HASH

    @pytest.mark.asyncio
    async def test_constitutional_compliance_check(self, operational_agent):
        """Test constitutional compliance checking."""
        governance_request = {
            "model_info": {
                "resource_usage": {"cpu_cores": 4, "memory_gb": 8, "storage_gb": 200}
            },
            "deployment_config": {"rollback_enabled": True},
            "security": {"encryption_enabled": True, "access_control_enabled": True},
        }
        
        compliance_result = await operational_agent.compliance_handler.check_constitutional_compliance(
            governance_request
        )
        
        assert "compliant" in compliance_result
        assert "compliance_score" in compliance_result
        assert "principle_checks" in compliance_result
        assert compliance_result["constitutional_hash"] == CONSTITUTIONAL_HASH

    def test_factory_function(self):
        """Test the factory function for creating operational agents."""
        agent = create_operational_agent(agent_id="factory_test_agent")
        
        assert isinstance(agent, OperationalAgentRefactored)
        assert agent.agent_id == "factory_test_agent"
        assert agent.agent_type == "operational_agent"


class TestOperationalAgentHandlers:
    """Test suite for individual operational agent handlers."""

    @pytest.fixture
    def mock_blackboard(self):
        """Mock blackboard service."""
        blackboard = Mock(spec=BlackboardService)
        blackboard.add_knowledge = AsyncMock()
        return blackboard

    @pytest.fixture
    def sample_task(self):
        """Sample task for testing."""
        return TaskDefinition(
            task_id="sample_task",
            task_type="test_task",
            task_data={
                "governance_request": {
                    "model_info": {
                        "resource_usage": {"cpu_cores": 4, "memory_gb": 8, "storage_gb": 200},
                        "performance": {"avg_latency_ms": 100, "rps": 150},
                        "network_requirements": {"bandwidth_mbps": 500},
                        "security": {"encryption_enabled": True},
                        "monitoring": {"metrics_enabled": True},
                    }
                }
            },
            priority=1,
        )

    @pytest.mark.asyncio
    async def test_validation_handler(self, mock_blackboard, sample_task):
        """Test validation handler."""
        handler = OperationalValidationHandler(
            agent_id="test_agent",
            blackboard_service=mock_blackboard,
        )
        
        result = await handler.handle_operational_validation(sample_task)
        
        assert "approved" in result
        assert "risk_level" in result
        assert "validation_checks" in result
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH

    @pytest.mark.asyncio
    async def test_performance_handler(self, mock_blackboard, sample_task):
        """Test performance handler."""
        handler = PerformanceAnalysisHandler(
            agent_id="test_agent",
            blackboard_service=mock_blackboard,
        )
        
        result = await handler.handle_performance_analysis(sample_task)
        
        assert "analysis_complete" in result
        assert "performance_score" in result
        assert "latency_analysis" in result
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH

    @pytest.mark.asyncio
    async def test_infrastructure_handler(self, mock_blackboard, sample_task):
        """Test infrastructure handler."""
        handler = InfrastructureAssessmentHandler(
            agent_id="test_agent",
            blackboard_service=mock_blackboard,
        )
        
        result = await handler.handle_infrastructure_assessment(sample_task)
        
        assert "assessment_complete" in result
        assert "overall_readiness" in result
        assert "component_readiness" in result
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH

    @pytest.mark.asyncio
    async def test_implementation_handler(self, mock_blackboard, sample_task):
        """Test implementation handler."""
        handler = ImplementationPlanningHandler(
            agent_id="test_agent",
            blackboard_service=mock_blackboard,
        )
        
        result = await handler.handle_implementation_planning(sample_task)
        
        assert "plan_created" in result
        assert "phases" in result
        assert "rollback_plan" in result
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH

    @pytest.mark.asyncio
    async def test_deployment_handler(self, mock_blackboard, sample_task):
        """Test deployment handler."""
        handler = DeploymentHandler(
            agent_id="test_agent",
            blackboard_service=mock_blackboard,
        )
        
        result = await handler.handle_deployment_planning(sample_task)
        
        assert "deployment_plan_created" in result
        assert "deployment_steps" in result
        assert "scaling_configuration" in result
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH

    @pytest.mark.asyncio
    async def test_compliance_handler(self, mock_blackboard, sample_task):
        """Test compliance handler."""
        handler = ConstitutionalComplianceHandler(
            agent_id="test_agent",
            blackboard_service=mock_blackboard,
        )
        
        governance_request = sample_task.task_data["governance_request"]
        governance_request["deployment_config"] = {"rollback_enabled": True}
        governance_request["security"]["access_control_enabled"] = True
        
        result = await handler.check_constitutional_compliance(governance_request)
        
        assert "compliant" in result
        assert "compliance_score" in result
        assert "principle_checks" in result
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH


if __name__ == "__main__":
    # Run basic tests
    print("Testing refactored operational agent...")
    print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    
    # Simple smoke test
    async def smoke_test():
        agent = create_operational_agent("smoke_test_agent")
        status = await agent.get_agent_status()
        print(f"Agent Status: {status['agent_id']} - {status['agent_type']}")
        
        health = await agent.health_check()
        print(f"Health Status: {'Healthy' if health['healthy'] else 'Unhealthy'}")
        
        metrics = await agent.get_performance_metrics()
        print(f"Performance Metrics: {metrics['agent_id']}")
        
        print("Smoke test completed successfully!")
    
    asyncio.run(smoke_test())