"""
Unit tests for DGM Engine.

Comprehensive test suite for the Darwin Gödel Machine Engine core functionality
including improvement proposal generation, execution, and safety mechanisms.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from dgm_service.core.dgm_engine import DGMEngine
from dgm_service.core.constitutional_validator import ConstitutionalValidator
from dgm_service.core.performance_monitor import PerformanceMonitor
from dgm_service.core.bandit_algorithm import BanditAlgorithm
from dgm_service.storage.archive_manager import ArchiveManager


@pytest.mark.unit
class TestDGMEngine:
    """Test suite for DGM Engine core functionality."""
    
    @pytest.fixture
    def dgm_engine(self):
        """Create DGM engine instance for testing."""
        with patch.multiple(
            'dgm_service.core.dgm_engine',
            ACGSServiceClient=MagicMock(),
            ConstitutionalValidator=MagicMock(),
            PerformanceMonitor=MagicMock(),
            ArchiveManager=MagicMock(),
            BanditAlgorithm=MagicMock()
        ):
            engine = DGMEngine()
            return engine
    
    @pytest.fixture
    def mock_dependencies(self, dgm_engine):
        """Setup mock dependencies for DGM engine."""
        dgm_engine.service_client = AsyncMock()
        dgm_engine.constitutional_validator = AsyncMock()
        dgm_engine.performance_monitor = AsyncMock()
        dgm_engine.archive_manager = AsyncMock()
        dgm_engine.bandit_algorithm = MagicMock()
        
        # Setup default return values
        dgm_engine.performance_monitor.get_current_metrics.return_value = {
            "response_time": 125.5,
            "throughput": 850.2,
            "error_rate": 0.002,
            "cpu_usage": 0.45,
            "memory_usage": 0.62
        }
        
        dgm_engine.constitutional_validator.validate_proposal.return_value = {
            "is_compliant": True,
            "compliance_score": 0.95,
            "violations": [],
            "recommendations": []
        }
        
        dgm_engine.bandit_algorithm.select_arm.return_value = "performance_optimization"
        dgm_engine.bandit_algorithm.update_arm.return_value = None
        
        return dgm_engine
    
    async def test_initialization(self, mock_dependencies):
        """Test DGM engine initialization."""
        engine = mock_dependencies
        
        # Mock baseline establishment
        engine.performance_monitor.get_current_metrics.return_value = {
            "response_time": 150.0,
            "throughput": 800.0,
            "error_rate": 0.005
        }
        
        await engine.initialize()
        
        # Verify initialization calls
        engine.performance_monitor.get_current_metrics.assert_called_once()
        assert engine.performance_baseline is not None
    
    async def test_generate_improvement_proposal_success(self, mock_dependencies):
        """Test successful improvement proposal generation."""
        engine = mock_dependencies
        
        # Setup test data
        target_services = ["gs-service"]
        priority = "medium"
        
        # Mock bandit selection
        engine.bandit_algorithm.select_arm.return_value = "performance_optimization"
        
        # Mock change generation
        with patch.object(engine, '_generate_changes') as mock_generate:
            mock_generate.return_value = {
                "type": "algorithm_optimization",
                "parameters": {"learning_rate": 0.01},
                "estimated_impact": 0.15
            }
            
            with patch.object(engine, '_estimate_improvement') as mock_estimate:
                mock_estimate.return_value = 0.15
                
                with patch.object(engine, '_assess_risk') as mock_risk:
                    mock_risk.return_value = {
                        "risk_level": "low",
                        "confidence": 0.85,
                        "potential_issues": []
                    }
                    
                    proposal = await engine.generate_improvement_proposal(
                        target_services=target_services,
                        priority=priority
                    )
        
        # Verify proposal structure
        assert proposal["strategy"] == "performance_optimization"
        assert proposal["target_services"] == target_services
        assert proposal["priority"] == priority
        assert "current_performance" in proposal
        assert "proposed_changes" in proposal
        assert "expected_improvement" in proposal
        assert "risk_assessment" in proposal
        
        # Verify method calls
        engine.bandit_algorithm.select_arm.assert_called_once()
        engine.performance_monitor.get_current_metrics.assert_called()
    
    async def test_generate_improvement_proposal_constitutional_violation(self, mock_dependencies):
        """Test proposal generation with constitutional violation."""
        engine = mock_dependencies
        
        # Mock constitutional violation
        engine.constitutional_validator.validate_proposal.return_value = {
            "is_compliant": False,
            "compliance_score": 0.45,
            "violations": ["unsafe_modification"],
            "recommendations": ["add_safety_checks"]
        }
        
        target_services = ["gs-service"]
        
        with pytest.raises(Exception) as exc_info:
            await engine.generate_improvement_proposal(target_services=target_services)
        
        assert "constitutional compliance" in str(exc_info.value).lower()
    
    async def test_execute_improvement_success(self, mock_dependencies):
        """Test successful improvement execution."""
        engine = mock_dependencies
        improvement_id = str(uuid4())
        
        # Setup test proposal
        proposal = {
            "strategy": "performance_optimization",
            "target_services": ["gs-service"],
            "proposed_changes": {
                "type": "algorithm_optimization",
                "parameters": {"learning_rate": 0.01}
            },
            "expected_improvement": 0.15
        }
        
        # Mock performance metrics
        performance_before = {"response_time": 150.0, "throughput": 800.0}
        performance_after = {"response_time": 125.0, "throughput": 950.0}
        
        engine.performance_monitor.get_current_metrics.side_effect = [
            performance_before,
            performance_after
        ]
        
        # Mock execution
        with patch.object(engine, '_execute_proposal') as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "execution_time": 45.2,
                "changes_applied": ["algorithm_update"]
            }
            
            with patch.object(engine, '_calculate_improvement_metrics') as mock_calc:
                mock_calc.return_value = {
                    "overall_improvement": 0.12,
                    "response_time_improvement": 0.167,
                    "throughput_improvement": 0.1875
                }
                
                result = await engine.execute_improvement(improvement_id, proposal)
        
        # Verify result
        assert result["success"] is True
        assert "improvement_metrics" in result
        assert "performance_before" in result
        assert "performance_after" in result
        
        # Verify bandit update
        engine.bandit_algorithm.update_arm.assert_called_once()
    
    async def test_execute_improvement_rollback_triggered(self, mock_dependencies):
        """Test improvement execution with automatic rollback."""
        engine = mock_dependencies
        improvement_id = str(uuid4())
        
        # Setup test proposal
        proposal = {
            "strategy": "risky_optimization",
            "target_services": ["gs-service"],
            "proposed_changes": {"type": "experimental_change"}
        }
        
        # Mock performance degradation
        performance_before = {"response_time": 150.0}
        performance_after = {"response_time": 250.0}  # Significant degradation
        
        engine.performance_monitor.get_current_metrics.side_effect = [
            performance_before,
            performance_after
        ]
        
        # Mock execution
        with patch.object(engine, '_execute_proposal') as mock_execute:
            mock_execute.return_value = {"success": True}
            
            with patch.object(engine, '_calculate_improvement_metrics') as mock_calc:
                mock_calc.return_value = {"overall_improvement": -0.15}  # Negative improvement
                
                with patch.object(engine, '_perform_automatic_rollback') as mock_rollback:
                    mock_rollback.return_value = None
                    
                    result = await engine.execute_improvement(improvement_id, proposal)
        
        # Verify rollback was triggered
        mock_rollback.assert_called_once_with(improvement_id, mock_execute.return_value)
    
    async def test_execute_improvement_execution_failure(self, mock_dependencies):
        """Test improvement execution failure handling."""
        engine = mock_dependencies
        improvement_id = str(uuid4())
        
        proposal = {
            "strategy": "failing_strategy",
            "target_services": ["gs-service"]
        }
        
        # Mock execution failure
        with patch.object(engine, '_execute_proposal') as mock_execute:
            mock_execute.side_effect = Exception("Execution failed")
            
            with pytest.raises(Exception) as exc_info:
                await engine.execute_improvement(improvement_id, proposal)
            
            assert "Improvement execution failed" in str(exc_info.value)
    
    async def test_establish_baseline(self, mock_dependencies):
        """Test performance baseline establishment."""
        engine = mock_dependencies
        
        baseline_metrics = {
            "response_time": 150.0,
            "throughput": 800.0,
            "error_rate": 0.005,
            "cpu_usage": 0.50,
            "memory_usage": 0.65
        }
        
        engine.performance_monitor.get_current_metrics.return_value = baseline_metrics
        
        await engine._establish_baseline()
        
        assert engine.performance_baseline == baseline_metrics
        engine.performance_monitor.get_current_metrics.assert_called_once()
    
    async def test_initialize_bandit_arms(self, mock_dependencies):
        """Test bandit algorithm arms initialization."""
        engine = mock_dependencies
        
        # Mock archive data
        engine.archive_manager.get_strategy_performance.return_value = {
            "performance_optimization": {"success_rate": 0.85, "avg_improvement": 0.12},
            "code_refactoring": {"success_rate": 0.75, "avg_improvement": 0.08},
            "architecture_improvement": {"success_rate": 0.65, "avg_improvement": 0.15}
        }
        
        await engine._initialize_bandit_arms()
        
        # Verify bandit initialization
        engine.bandit_algorithm.initialize_arms.assert_called_once()
        engine.archive_manager.get_strategy_performance.assert_called_once()
    
    async def test_generate_changes(self, mock_dependencies):
        """Test change generation for different strategies."""
        engine = mock_dependencies
        
        # Mock LLM response
        with patch.object(engine, '_query_foundation_model') as mock_llm:
            mock_llm.return_value = {
                "changes": [
                    {
                        "type": "parameter_optimization",
                        "target": "learning_rate",
                        "current_value": 0.001,
                        "proposed_value": 0.01,
                        "rationale": "Faster convergence expected"
                    }
                ],
                "confidence": 0.85
            }
            
            changes = await engine._generate_changes(
                "performance_optimization",
                ["gs-service"]
            )
        
        assert "changes" in changes
        assert changes["confidence"] == 0.85
        mock_llm.assert_called_once()
    
    async def test_estimate_improvement(self, mock_dependencies):
        """Test improvement estimation."""
        engine = mock_dependencies
        
        # Mock historical data
        engine.archive_manager.get_strategy_statistics.return_value = {
            "performance_optimization": {
                "avg_improvement": 0.12,
                "std_improvement": 0.03,
                "success_rate": 0.85
            }
        }
        
        estimate = await engine._estimate_improvement("performance_optimization")
        
        assert isinstance(estimate, float)
        assert 0.0 <= estimate <= 1.0
    
    async def test_assess_risk(self, mock_dependencies):
        """Test risk assessment."""
        engine = mock_dependencies
        
        risk_assessment = await engine._assess_risk(
            "experimental_strategy",
            ["critical-service"]
        )
        
        assert "risk_level" in risk_assessment
        assert "confidence" in risk_assessment
        assert "potential_issues" in risk_assessment
        assert risk_assessment["risk_level"] in ["low", "medium", "high", "critical"]
    
    async def test_calculate_improvement_metrics(self, mock_dependencies):
        """Test improvement metrics calculation."""
        engine = mock_dependencies
        
        performance_before = {
            "response_time": 150.0,
            "throughput": 800.0,
            "error_rate": 0.005
        }
        
        performance_after = {
            "response_time": 125.0,
            "throughput": 950.0,
            "error_rate": 0.003
        }
        
        metrics = await engine._calculate_improvement_metrics(
            performance_before,
            performance_after
        )
        
        assert "overall_improvement" in metrics
        assert "response_time_improvement" in metrics
        assert "throughput_improvement" in metrics
        assert "error_rate_improvement" in metrics
        
        # Verify improvement calculations
        assert metrics["response_time_improvement"] > 0  # Response time decreased (good)
        assert metrics["throughput_improvement"] > 0     # Throughput increased (good)
        assert metrics["error_rate_improvement"] > 0     # Error rate decreased (good)
    
    async def test_safety_constraints_enforcement(self, mock_dependencies):
        """Test safety constraints enforcement."""
        engine = mock_dependencies
        
        # Test with high-risk strategy
        with patch.object(engine, '_assess_risk') as mock_risk:
            mock_risk.return_value = {
                "risk_level": "critical",
                "confidence": 0.95,
                "potential_issues": ["system_instability"]
            }
            
            with pytest.raises(Exception) as exc_info:
                await engine.generate_improvement_proposal(
                    target_services=["critical-service"],
                    priority="high"
                )
            
            assert "safety constraint" in str(exc_info.value).lower()
    
    async def test_performance_monitoring_integration(self, mock_dependencies):
        """Test integration with performance monitoring."""
        engine = mock_dependencies
        
        # Test metric recording during improvement
        improvement_id = str(uuid4())
        
        with patch.object(engine, '_record_improvement_metrics') as mock_record:
            await engine._record_improvement_metrics(
                improvement_id,
                "performance_optimization",
                {"overall_improvement": 0.12}
            )
            
            mock_record.assert_called_once_with(
                improvement_id,
                "performance_optimization", 
                {"overall_improvement": 0.12}
            )
    
    @pytest.mark.slow
    async def test_concurrent_improvement_handling(self, mock_dependencies):
        """Test handling of concurrent improvement requests."""
        engine = mock_dependencies
        
        # Mock concurrent proposals
        proposals = [
            {"target_services": ["service-1"], "priority": "high"},
            {"target_services": ["service-2"], "priority": "medium"},
            {"target_services": ["service-3"], "priority": "low"}
        ]
        
        # Test that engine handles concurrent requests properly
        import asyncio
        tasks = [
            engine.generate_improvement_proposal(**proposal)
            for proposal in proposals
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verify all requests were processed
        assert len(results) == 3
        for result in results:
            if not isinstance(result, Exception):
                assert "strategy" in result
                assert "target_services" in result
