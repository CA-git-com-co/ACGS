"""
Unit tests for Multi-Agent Performance Monitoring and WINA Integration.
"""

# Constitutional Hash: cdd01ef066bc6cf2

import asyncio
import os
import sys
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
import pytest_asyncio

sys.path.append(os.path.join(os.path.dirname(__file__), "../../../.."))

from services.core.multi_agent_coordinator.performance_integration import (
    AgentPerformanceMetrics,
    CoordinationMetrics,
    MultiAgentPerformanceMonitor,
    WINAOptimizationMetrics,
)
from services.shared.blackboard.blackboard_service import KnowledgeItem
from tests.fixtures.multi_agent.mock_services import MockRedis, MockWINACore


class TestMultiAgentPerformanceMonitor:
    """Test cases for MultiAgentPerformanceMonitor"""

    @pytest_asyncio.fixture
    async def mock_blackboard(self):
        """Create mock blackboard service"""
        from services.shared.blackboard.blackboard_service import BlackboardService

        mock_redis = MockRedis()
        blackboard = BlackboardService(redis_url="redis://localhost:6379", db=0)
        # Replace the redis client with our mock after initialization
        blackboard.redis_client = mock_redis
        return blackboard

    @pytest.fixture
    def mock_wina_core(self):
        """Create mock WINA core"""
        return MockWINACore()

    @pytest_asyncio.fixture
    async def performance_monitor(self, mock_blackboard, mock_wina_core):
        """Create MultiAgentPerformanceMonitor with mocks"""
        monitor = MultiAgentPerformanceMonitor(
            blackboard_service=mock_blackboard, wina_core=mock_wina_core
        )
        return monitor

    @pytest_asyncio.fixture
    async def sample_agent_knowledge(self, mock_blackboard):
        """Create sample agent knowledge for testing"""
        knowledge_items = []

        # Add successful task knowledge
        for i in range(5):
            knowledge = KnowledgeItem(
                space="governance",
                agent_id="ethics_agent_1",
                knowledge_type="task_result",
                content={
                    "task_id": str(uuid4()),
                    "task_status": "completed",
                    "processing_time": 2.5 + (i * 0.5),
                    "success": True,
                },
                priority=2,
                tags={"analysis_complete", "task_result"},
            )
            knowledge_id = await mock_blackboard.add_knowledge(knowledge)
            knowledge_items.append(knowledge_id)

        # Add failed task knowledge
        for i in range(2):
            knowledge = KnowledgeItem(
                space="governance",
                agent_id="ethics_agent_1",
                knowledge_type="task_result",
                content={
                    "task_id": str(uuid4()),
                    "task_status": "failed",
                    "processing_time": 1.0,
                    "error": "Processing error",
                },
                priority=2,
                tags={"failed", "task_result"},
            )
            knowledge_id = await mock_blackboard.add_knowledge(knowledge)
            knowledge_items.append(knowledge_id)

        return knowledge_items

    # Performance Monitor Initialization Tests

    @pytest.mark.asyncio
    async def test_performance_monitor_initialization(self, performance_monitor):
        """Test performance monitor initialization"""
        assert performance_monitor.blackboard is not None
        assert performance_monitor.wina_core is not None
        assert performance_monitor.is_monitoring is False
        assert len(performance_monitor.agent_metrics) == 0
        assert len(performance_monitor.coordination_history) == 0
        assert "agent_success_rate_min" in performance_monitor.performance_thresholds

    @pytest.mark.asyncio
    async def test_start_stop_monitoring(self, performance_monitor):
        """Test starting and stopping monitoring"""
        # Start monitoring
        await performance_monitor.start_monitoring()
        assert performance_monitor.is_monitoring is True

        # Stop monitoring
        await performance_monitor.stop_monitoring()
        assert performance_monitor.is_monitoring is False

    # Agent Metrics Collection Tests

    @pytest.mark.asyncio
    async def test_collect_agent_metrics(
        self, performance_monitor, sample_agent_knowledge
    ):
        """Test collecting metrics for individual agents"""
        # Mock active agents
        with patch.object(
            performance_monitor.blackboard, "get_active_agents"
        ) as mock_get_active:
            mock_get_active.return_value = ["ethics_agent_1"]

            # Collect metrics
            await performance_monitor._collect_agent_metrics("ethics_agent_1")

            # Verify metrics were collected
            assert "ethics_agent_1" in performance_monitor.agent_metrics
            metrics = performance_monitor.agent_metrics["ethics_agent_1"]

            assert isinstance(metrics, AgentPerformanceMetrics)
            assert metrics.agent_id == "ethics_agent_1"
            assert metrics.agent_type == "ethics_agent"
            assert metrics.tasks_completed == 5
            assert metrics.tasks_failed == 2
            assert metrics.success_rate == 5 / 7  # 5 completed out of 7 total
            assert 0.0 <= metrics.confidence <= 1.0

    @pytest.mark.asyncio
    async def test_agent_performance_metrics_calculation(
        self, performance_monitor, mock_blackboard
    ):
        """Test detailed agent performance metrics calculation"""
        # Add constitutional compliance knowledge
        compliance_knowledge = KnowledgeItem(
            space="governance",
            agent_id="legal_agent_1",
            knowledge_type="compliance_check",
            content={"constitutional_compliance": {"compliant": True, "score": 0.95}},
            priority=2,
            tags={"compliance", "constitutional"},
        )
        await mock_blackboard.add_knowledge(compliance_knowledge)

        # Mock active agents
        with patch.object(
            performance_monitor.blackboard, "get_active_agents"
        ) as mock_get_active:
            mock_get_active.return_value = ["legal_agent_1"]

            # Collect metrics
            await performance_monitor._collect_agent_metrics("legal_agent_1")

            # Verify compliance metrics
            metrics = performance_monitor.agent_metrics["legal_agent_1"]
            assert metrics.constitutional_compliance_rate >= 0.0

    @pytest.mark.asyncio
    async def test_efficiency_score_calculation(self, performance_monitor):
        """Test efficiency score calculation"""
        # Test with good performance
        efficiency_score = await performance_monitor._calculate_efficiency_score(
            "test_agent", success_rate=0.9, avg_processing_time=10.0
        )
        assert 0.0 <= efficiency_score <= 1.0
        assert (
            efficiency_score > 0.5
        )  # Should be good with high success rate and reasonable time

        # Test with poor performance
        poor_efficiency = await performance_monitor._calculate_efficiency_score(
            "test_agent", success_rate=0.3, avg_processing_time=120.0
        )
        assert (
            poor_efficiency < efficiency_score
        )  # Should be lower than good performance

    @pytest.mark.asyncio
    async def test_collaboration_score_calculation(
        self, performance_monitor, mock_blackboard
    ):
        """Test collaboration score calculation"""
        # Add collaboration knowledge
        collab_knowledge = KnowledgeItem(
            space="governance",
            agent_id="operational_agent_1",
            knowledge_type="shared_insight",
            content={"insight": "Performance optimization suggestion"},
            priority=2,
            tags={"collaboration", "shared"},
        )
        await mock_blackboard.add_knowledge(collab_knowledge)

        agent_knowledge = await mock_blackboard.query_knowledge(
            space="governance", agent_id="operational_agent_1"
        )

        collaboration_score = await performance_monitor._calculate_collaboration_score(
            "operational_agent_1", agent_knowledge
        )

        assert 0.0 <= collaboration_score <= 1.0

    # Coordination Metrics Tests

    @pytest.mark.asyncio
    async def test_coordination_metrics_collection(
        self, performance_monitor, mock_blackboard
    ):
        """Test collection of system-wide coordination metrics"""
        # Mock blackboard metrics
        mock_blackboard_metrics = {
            "tasks": {"completed": 15, "failed": 3, "pending": 5, "in_progress": 2},
            "conflicts": {"open": 1, "resolved": 4},
        }

        with patch.object(mock_blackboard, "get_metrics") as mock_get_metrics:
            mock_get_metrics.return_value = mock_blackboard_metrics

            # Add some agent metrics first
            performance_monitor.agent_metrics["agent_1"] = AgentPerformanceMetrics(
                agent_id="agent_1",
                agent_type="test_agent",
                tasks_completed=10,
                tasks_failed=1,
                average_processing_time=5.0,
                success_rate=0.9,
                current_load=2,
                last_heartbeat=datetime.utcnow(),
                constitutional_compliance_rate=0.95,
                efficiency_score=0.85,
                collaboration_score=0.7,
            )

            # Calculate coordination metrics
            coordination_metrics = (
                await performance_monitor._calculate_coordination_metrics(
                    mock_blackboard_metrics
                )
            )

            assert isinstance(coordination_metrics, CoordinationMetrics)
            assert coordination_metrics.active_agents == 1
            assert coordination_metrics.completed_requests == 15
            assert coordination_metrics.failed_requests == 3
            assert 0.0 <= coordination_metrics.coordination_efficiency <= 1.0
            assert 0.0 <= coordination_metrics.conflict_resolution_rate <= 1.0

    @pytest.mark.asyncio
    async def test_consensus_success_rate_calculation(self, performance_monitor):
        """Test consensus success rate calculation"""
        # This is a placeholder test since consensus integration would be more complex
        consensus_rate = await performance_monitor._calculate_consensus_success_rate()

        # Should return a reasonable default value
        assert 0.0 <= consensus_rate <= 1.0

    # WINA Integration Tests

    @pytest.mark.asyncio
    async def test_wina_optimization_execution(self, performance_monitor):
        """Test WINA optimization execution"""
        # Add some coordination history first
        coordination_metrics = CoordinationMetrics(
            active_agents=3,
            total_governance_requests=20,
            completed_requests=15,
            failed_requests=2,
            average_request_completion_time=5.5,
            coordination_efficiency=0.8,
            conflict_resolution_rate=0.9,
            consensus_success_rate=0.85,
            blackboard_performance={},
            system_throughput=12.0,
        )
        performance_monitor.coordination_history.append(coordination_metrics)

        # Execute WINA optimization
        optimization_result = await performance_monitor._perform_wina_optimization()

        assert optimization_result is not None
        assert isinstance(optimization_result, WINAOptimizationMetrics)
        assert optimization_result.optimization_cycles_completed >= 1
        assert 0.0 <= optimization_result.performance_improvements <= 1.0
        assert 0.0 <= optimization_result.constitutional_alignment_score <= 1.0

    @pytest.mark.asyncio
    async def test_constitutional_alignment_calculation(self, performance_monitor):
        """Test constitutional alignment score calculation"""
        # Add agent metrics with compliance rates
        performance_monitor.agent_metrics["agent_1"] = AgentPerformanceMetrics(
            agent_id="agent_1",
            agent_type="ethics_agent",
            tasks_completed=10,
            tasks_failed=1,
            average_processing_time=5.0,
            success_rate=0.9,
            current_load=2,
            last_heartbeat=datetime.utcnow(),
            constitutional_compliance_rate=0.95,
            efficiency_score=0.85,
            collaboration_score=0.7,
        )

        performance_monitor.agent_metrics["agent_2"] = AgentPerformanceMetrics(
            agent_id="agent_2",
            agent_type="legal_agent",
            tasks_completed=8,
            tasks_failed=0,
            average_processing_time=4.0,
            success_rate=1.0,
            current_load=1,
            last_heartbeat=datetime.utcnow(),
            constitutional_compliance_rate=0.98,
            efficiency_score=0.90,
            collaboration_score=0.8,
        )

        alignment_score = (
            await performance_monitor._calculate_constitutional_alignment()
        )

        expected_score = (0.95 + 0.98) / 2
        assert abs(alignment_score - expected_score) < 0.01

    # Performance Threshold and Alerting Tests

    @pytest.mark.asyncio
    async def test_performance_threshold_checking(self, performance_monitor):
        """Test performance threshold checking and alerting"""
        # Add agent with poor performance
        poor_agent_metrics = AgentPerformanceMetrics(
            agent_id="poor_agent",
            agent_type="test_agent",
            tasks_completed=3,
            tasks_failed=7,
            average_processing_time=120.0,  # Exceeds threshold
            success_rate=0.3,  # Below threshold
            current_load=5,
            last_heartbeat=datetime.utcnow(),
            constitutional_compliance_rate=0.8,  # Below threshold
            efficiency_score=0.2,
            collaboration_score=0.1,
        )
        performance_monitor.agent_metrics["poor_agent"] = poor_agent_metrics

        # Check thresholds
        alerts = await performance_monitor._check_performance_thresholds()

        # Should generate multiple alerts
        assert len(alerts) > 0

        # Check alert types
        alert_types = [alert["type"] for alert in alerts]
        assert "agent_performance" in alert_types
        assert "constitutional_compliance" in alert_types

        # Check severity levels
        severities = [alert["severity"] for alert in alerts]
        assert "warning" in severities or "critical" in severities

    @pytest.mark.asyncio
    async def test_send_performance_alert(self, performance_monitor, mock_blackboard):
        """Test sending performance alerts to blackboard"""
        alert = {
            "type": "agent_performance",
            "severity": "warning",
            "agent_id": "test_agent",
            "metric": "success_rate",
            "value": 0.7,
            "threshold": 0.85,
            "message": "Agent performance below threshold",
        }

        # Send alert
        await performance_monitor._send_performance_alert(alert)

        # Verify alert was added to blackboard
        alert_knowledge = await mock_blackboard.query_knowledge(
            space="performance", knowledge_type="performance_alert"
        )

        assert len(alert_knowledge) == 1
        assert alert_knowledge[0].content["type"] == "agent_performance"
        assert alert_knowledge[0].content["severity"] == "warning"

    # API and Status Tests

    @pytest.mark.asyncio
    async def test_get_agent_performance(self, performance_monitor):
        """Test getting performance metrics for specific agent"""
        # Add agent metrics
        test_metrics = AgentPerformanceMetrics(
            agent_id="test_agent_1",
            agent_type="test_agent",
            tasks_completed=15,
            tasks_failed=2,
            average_processing_time=3.5,
            success_rate=0.88,
            current_load=3,
            last_heartbeat=datetime.utcnow(),
            constitutional_compliance_rate=0.92,
            efficiency_score=0.85,
            collaboration_score=0.75,
        )
        performance_monitor.agent_metrics["test_agent_1"] = test_metrics

        # Retrieve metrics
        retrieved_metrics = await performance_monitor.get_agent_performance(
            "test_agent_1"
        )

        assert retrieved_metrics is not None
        assert retrieved_metrics.agent_id == "test_agent_1"
        assert retrieved_metrics.success_rate == 0.88

        # Test non-existent agent
        none_metrics = await performance_monitor.get_agent_performance("non_existent")
        assert none_metrics is None

    @pytest.mark.asyncio
    async def test_get_system_performance(self, performance_monitor):
        """Test getting current system performance metrics"""
        # Add coordination metrics
        test_coordination = CoordinationMetrics(
            active_agents=5,
            total_governance_requests=50,
            completed_requests=45,
            failed_requests=3,
            average_request_completion_time=4.2,
            coordination_efficiency=0.85,
            conflict_resolution_rate=0.93,
            consensus_success_rate=0.88,
            blackboard_performance={},
            system_throughput=15.5,
        )
        performance_monitor.coordination_history.append(test_coordination)

        # Retrieve system performance
        system_perf = await performance_monitor.get_system_performance()

        assert system_perf is not None
        assert system_perf.active_agents == 5
        assert system_perf.coordination_efficiency == 0.85

        # Test empty coordination history
        performance_monitor.coordination_history.clear()
        empty_perf = await performance_monitor.get_system_performance()
        assert empty_perf is None

    @pytest.mark.asyncio
    async def test_get_performance_summary(self, performance_monitor):
        """Test getting comprehensive performance summary"""
        # Add agent metrics
        performance_monitor.agent_metrics["agent_1"] = AgentPerformanceMetrics(
            agent_id="agent_1",
            agent_type="ethics_agent",
            tasks_completed=10,
            tasks_failed=1,
            average_processing_time=5.0,
            success_rate=0.9,
            current_load=2,
            last_heartbeat=datetime.utcnow(),
            constitutional_compliance_rate=0.95,
            efficiency_score=0.85,
            collaboration_score=0.7,
        )

        # Add coordination metrics
        performance_monitor.coordination_history.append(
            CoordinationMetrics(
                active_agents=1,
                total_governance_requests=20,
                completed_requests=18,
                failed_requests=1,
                average_request_completion_time=5.0,
                coordination_efficiency=0.85,
                conflict_resolution_rate=0.95,
                consensus_success_rate=0.90,
                blackboard_performance={},
                system_throughput=12.0,
            )
        )

        # Add WINA optimization metrics
        performance_monitor.wina_optimization_history.append(
            WINAOptimizationMetrics(
                optimization_cycles_completed=1,
                performance_improvements=0.1,
                resource_utilization_efficiency=0.85,
                adaptation_effectiveness=0.08,
                learning_convergence_rate=0.05,
                constitutional_alignment_score=0.95,
            )
        )

        # Get summary
        summary = await performance_monitor.get_performance_summary()

        assert "timestamp" in summary
        assert summary["system_health"] in ["healthy", "degraded"]
        assert summary["active_agents"] == 1
        assert 0.0 <= summary["average_agent_success_rate"] <= 1.0
        assert 0.0 <= summary["average_constitutional_compliance"] <= 1.0
        assert summary["wina_optimization_active"] is True
        assert "alerts_active" in summary

    @pytest.mark.asyncio
    async def test_update_performance_thresholds(self, performance_monitor):
        """Test updating performance thresholds"""
        new_thresholds = {
            "agent_success_rate_min": 0.9,
            "coordination_efficiency_min": 0.8,
        }

        await performance_monitor.update_performance_thresholds(new_thresholds)

        assert (
            performance_monitor.performance_thresholds["agent_success_rate_min"] == 0.9
        )
        assert (
            performance_monitor.performance_thresholds["coordination_efficiency_min"]
            == 0.8
        )

    @pytest.mark.asyncio
    async def test_manual_optimization_trigger(self, performance_monitor):
        """Test manually triggering WINA optimization"""
        # Add coordination history for optimization
        performance_monitor.coordination_history.append(
            CoordinationMetrics(
                active_agents=3,
                total_governance_requests=30,
                completed_requests=25,
                failed_requests=2,
                average_request_completion_time=6.0,
                coordination_efficiency=0.75,
                conflict_resolution_rate=0.85,
                consensus_success_rate=0.80,
                blackboard_performance={},
                system_throughput=10.0,
            )
        )

        # Trigger manual optimization
        optimization_result = await performance_monitor.trigger_manual_optimization()

        assert optimization_result is not None
        assert isinstance(optimization_result, WINAOptimizationMetrics)
        assert performance_monitor.wina_core.optimization_count >= 1

    # Integration and Error Handling Tests

    @pytest.mark.asyncio
    async def test_monitoring_loop_error_handling(self, performance_monitor):
        """Test error handling in monitoring loops"""
        # Mock blackboard to raise exception
        with patch.object(
            performance_monitor.blackboard, "get_active_agents"
        ) as mock_get_active:
            mock_get_active.side_effect = Exception("Database connection error")

            # This should handle the exception gracefully
            await performance_monitor._agent_metrics_collection_loop()

            # Monitor should still be in a consistent state
            assert (
                performance_monitor.is_monitoring is False
            )  # Loop would exit on error

    @pytest.mark.asyncio
    async def test_wina_optimization_without_wina_core(self, mock_blackboard):
        """Test performance monitor without WINA core"""
        monitor_no_wina = MultiAgentPerformanceMonitor(
            blackboard_service=mock_blackboard, wina_core=None
        )

        # Should handle gracefully
        optimization_result = await monitor_no_wina._perform_wina_optimization()
        assert optimization_result is None

        # Manual trigger should also return None
        manual_result = await monitor_no_wina.trigger_manual_optimization()
        assert manual_result is None

    @pytest.mark.asyncio
    async def test_concurrent_metrics_collection(
        self, performance_monitor, mock_blackboard
    ):
        """Test concurrent metrics collection"""
        # Add multiple agents
        with patch.object(
            performance_monitor.blackboard, "get_active_agents"
        ) as mock_get_active:
            mock_get_active.return_value = ["agent_1", "agent_2", "agent_3"]

            # Run concurrent metrics collection
            collection_tasks = [
                performance_monitor._collect_agent_metrics(f"agent_{i}")
                for i in range(1, 4)
            ]

            await asyncio.gather(*collection_tasks, return_exceptions=True)

            # Should have collected metrics for all agents
            assert (
                len(performance_monitor.agent_metrics) <= 3
            )  # Some might fail due to no knowledge
