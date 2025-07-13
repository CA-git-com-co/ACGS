"""
Test suite for Policy Synthesis Enhancement system.

Tests the comprehensive Policy Synthesis Enhancement system including:
- Proactive error prediction
- Risk-based strategy selection
- Multi-model consensus engine
- Performance optimization and tracking
"""

# Constitutional Hash: cdd01ef066bc6cf2

from unittest.mock import Mock

import pytest
from services.core.governance_synthesis.gs_service.core.performance_optimizer import (
    SynthesisPerformanceMetrics,
    WINAPerformanceOptimizer,
)
from services.core.governance_synthesis.gs_service.services.qec_error_correction_service import (
    QECErrorCorrectionService,
)

from services.shared.models import Principle


class TestProactiveErrorPrediction:
    """Test proactive error prediction functionality."""

    @pytest.fixture
    def qec_service(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Create QEC service instance for testing."""
        return QECErrorCorrectionService()

    @pytest.fixture
    def sample_principles(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Create sample principles for testing."""
        principles = []
        for i in range(3):
            principle = Mock(spec=Principle)
            principle.id = i + 1
            principle.content = (
                f"Test principle {i + 1} content with some complexity and requirements."
            )
            principle.description = f"Description for principle {i + 1}"
            principle.priority_weight = 0.5 + (i * 0.2)
            principle.constraints = {"type": "test"} if i == 0 else None
            principle.scope = ["governance", "policy"] if i < 2 else ["governance"]
            principles.append(principle)
        return principles

    @pytest.mark.asyncio
    async def test_predict_synthesis_errors_basic(self, qec_service, sample_principles):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Test basic error prediction functionality."""
        context_data = {
            "high_stakes": True,
            "regulatory_compliance": True,
            "multi_stakeholder": True,
        }

        result = await qec_service.predict_synthesis_errors(
            sample_principles, context_data
        )

        # Verify result structure
        assert "risk_assessment" in result
        assert "recommended_strategy" in result
        assert "prediction_metadata" in result
        assert "risk_factors" in result

        # Verify risk assessment components
        risk_assessment = result["risk_assessment"]
        assert "ambiguity_risk" in risk_assessment
        assert "misalignment_risk" in risk_assessment
        assert "implementation_risk" in risk_assessment
        assert "overall_risk" in risk_assessment

        # Verify all risk scores are between 0 and 1
        for score in risk_assessment.values():
            assert 0.0 <= score <= 1.0

        # Verify strategy recommendation is valid
        valid_strategies = [
            "standard_synthesis",
            "enhanced_validation",
            "multi_model_consensus",
            "human_review_required",
        ]
        assert result["recommended_strategy"] in valid_strategies

    @pytest.mark.asyncio
    async def test_extract_principle_features(self, qec_service, sample_principles):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Test principle feature extraction."""
        features = await qec_service._extract_principle_features(sample_principles)

        assert len(features) == len(sample_principles)

        for feature in features:
            assert "principle_id" in feature
            assert "word_count" in feature
            assert "ambiguity_score" in feature
            assert "complexity_score" in feature
            assert "conflict_potential" in feature
            assert "technical_complexity" in feature

            # Verify feature values are reasonable
            assert feature["word_count"] > 0
            assert 0.0 <= feature["ambiguity_score"] <= 1.0
            assert 0.0 <= feature["complexity_score"] <= 1.0

    @pytest.mark.asyncio
    async def test_risk_calculation_methods(self, qec_service):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Test individual risk calculation methods."""
        # Sample feature data
        principle_features = [
            {
                "principle_id": "1",
                "ambiguity_score": 0.3,
                "conflict_potential": 0.4,
                "technical_complexity": 0.5,
                "complexity_score": 0.6,
                "priority_weight": 0.8,
                "scope_breadth": 2,
            },
            {
                "principle_id": "2",
                "ambiguity_score": 0.7,
                "conflict_potential": 0.8,
                "technical_complexity": 0.9,
                "complexity_score": 0.8,
                "priority_weight": 0.6,
                "scope_breadth": 3,
            },
        ]

        # Test ambiguity risk calculation
        ambiguity_risk = await qec_service._calculate_ambiguity_risk(principle_features)
        assert 0.0 <= ambiguity_risk <= 1.0

        # Test misalignment risk calculation
        misalignment_risk = await qec_service._calculate_misalignment_risk(
            principle_features
        )
        assert 0.0 <= misalignment_risk <= 1.0

        # Test implementation risk calculation
        context_data = {"high_stakes": True, "regulatory_compliance": True}
        implementation_risk = await qec_service._calculate_implementation_risk(
            principle_features, context_data
        )
        assert 0.0 <= implementation_risk <= 1.0

    def test_recommend_strategy(self, qec_service):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Test strategy recommendation logic."""
        # Test low risk
        strategy = qec_service._recommend_strategy(0.2)
        assert strategy == "standard_synthesis"

        # Test medium risk
        strategy = qec_service._recommend_strategy(0.5)
        assert strategy == "enhanced_validation"

        # Test high risk
        strategy = qec_service._recommend_strategy(0.7)
        assert strategy == "multi_model_consensus"

        # Test critical risk
        strategy = qec_service._recommend_strategy(0.9)
        assert strategy == "human_review_required"


class TestPerformanceOptimizer:
    """Test performance optimization and tracking functionality."""

    @pytest.fixture
    def performance_optimizer(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Create performance optimizer instance for testing."""
        config = {
            "target_synthesis_response_time": 2.0,
            "target_synthesis_success_rate": 0.95,
            "target_synthesis_quality_score": 0.85,
            "max_recent_metrics": 100,
            "min_synthesis_samples": 5,
        }
        return WINAPerformanceOptimizer(config)

    @pytest.mark.asyncio
    async def test_track_synthesis_performance(self, performance_optimizer):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Test synthesis performance tracking."""
        await performance_optimizer.track_synthesis_performance(
            strategy_used="multi_model_consensus",
            response_time_seconds=1.5,
            success=True,
            quality_score=0.9,
            error_count=0,
            principle_count=3,
            context_complexity=0.7,
        )

        # Verify metrics were recorded
        assert len(performance_optimizer.recent_synthesis_metrics) == 1
        assert "multi_model_consensus" in performance_optimizer.strategy_performance

        strategy_perf = performance_optimizer.strategy_performance[
            "multi_model_consensus"
        ]
        assert strategy_perf.total_uses == 1
        assert strategy_perf.success_count == 1
        assert strategy_perf.success_rate == 1.0
        assert strategy_perf.average_response_time == 1.5
        assert strategy_perf.average_quality_score == 0.9

    @pytest.mark.asyncio
    async def test_strategy_weight_adjustment(self, performance_optimizer):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Test dynamic strategy weight adjustment."""
        # Add multiple performance records
        strategies = [
            "standard_synthesis",
            "enhanced_validation",
            "multi_model_consensus",
        ]

        for i, strategy in enumerate(strategies):
            for _j in range(10):  # Add 10 records per strategy
                await performance_optimizer.track_synthesis_performance(
                    strategy_used=strategy,
                    response_time_seconds=1.0 + (i * 0.5),  # Different response times
                    success=True,
                    quality_score=0.8 + (i * 0.05),  # Different quality scores
                    error_count=0,
                    principle_count=2,
                    context_complexity=0.5,
                )

        # Trigger weight adjustment
        weights = await performance_optimizer.adjust_strategy_weights()

        # Verify weights were adjusted
        assert len(weights) == len(performance_optimizer.synthesis_strategy_weights)

        # Better performing strategies should have higher weights
        # multi_model_consensus should have highest weight (best quality, acceptable time)
        assert weights["multi_model_consensus"] >= weights["enhanced_validation"]
        assert weights["enhanced_validation"] >= weights["standard_synthesis"]

    def test_synthesis_performance_summary(self, performance_optimizer):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Test synthesis performance summary generation."""
        # Add some test data
        test_metrics = [
            SynthesisPerformanceMetrics(
                strategy_used="multi_model_consensus",
                response_time_seconds=1.8,
                quality_score=0.92,
                success=True,
                error_count=0,
                principle_count=2,
                context_complexity=0.6,
            ),
            SynthesisPerformanceMetrics(
                strategy_used="enhanced_validation",
                response_time_seconds=1.2,
                quality_score=0.88,
                success=True,
                error_count=0,
                principle_count=1,
                context_complexity=0.4,
            ),
        ]

        for metrics in test_metrics:
            performance_optimizer.recent_synthesis_metrics.append(metrics)
            performance_optimizer.strategy_performance[metrics.strategy_used] = Mock()
            performance_optimizer.strategy_performance[
                metrics.strategy_used
            ].total_uses = 1
            performance_optimizer.strategy_performance[
                metrics.strategy_used
            ].success_rate = 1.0
            performance_optimizer.strategy_performance[
                metrics.strategy_used
            ].average_response_time = metrics.response_time_seconds
            performance_optimizer.strategy_performance[
                metrics.strategy_used
            ].average_quality_score = metrics.quality_score

        summary = performance_optimizer.get_synthesis_performance_summary()

        # Verify summary structure
        assert summary["status"] == "active"
        assert "overall_metrics" in summary
        assert "targets" in summary
        assert "targets_met" in summary
        assert "strategy_performance" in summary
        assert "current_strategy_weights" in summary

        # Verify metrics calculation
        overall_metrics = summary["overall_metrics"]
        assert overall_metrics["total_operations"] == 2
        assert overall_metrics["success_rate"] == 1.0
        assert 1.0 <= overall_metrics["average_response_time_seconds"] <= 2.0
        assert 0.85 <= overall_metrics["average_quality_score"] <= 0.95


class TestIntegration:
    """Integration tests for the complete Policy Synthesis Enhancement system."""

    @pytest.mark.asyncio
    async def test_end_to_end_synthesis_enhancement(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Test complete end-to-end synthesis enhancement workflow."""
        # This would test the full integration from error prediction through
        # strategy selection to performance tracking

        # Mock the necessary components
        qec_service = QECErrorCorrectionService()

        # Create test principles
        principles = []
        for i in range(2):
            principle = Mock(spec=Principle)
            principle.id = i + 1
            principle.content = (
                f"Complex governance principle {i + 1} with regulatory requirements."
            )
            principle.description = f"Detailed description for principle {i + 1}"
            principle.priority_weight = 0.7
            principle.constraints = {"compliance": True}
            principle.scope = ["governance", "compliance", "policy"]
            principles.append(principle)

        # Test error prediction
        context_data = {
            "high_stakes": True,
            "regulatory_compliance": True,
            "multi_stakeholder": True,
            "time_sensitive": False,
        }

        prediction_result = await qec_service.predict_synthesis_errors(
            principles, context_data
        )

        # Verify prediction result
        assert prediction_result["risk_assessment"]["overall_risk"] > 0.0
        assert prediction_result["recommended_strategy"] in {
            "standard_synthesis",
            "enhanced_validation",
            "multi_model_consensus",
            "human_review_required",
        }

        # Verify the system recommends appropriate strategy for high-stakes context
        if prediction_result["risk_assessment"]["overall_risk"] > 0.6:
            assert prediction_result["recommended_strategy"] in {
                "multi_model_consensus",
                "human_review_required",
            }

        # Test that metadata is properly populated
        assert prediction_result["prediction_metadata"]["principles_analyzed"] == 2
        assert prediction_result["prediction_metadata"]["context_factors"] == 4
        assert "prediction_time_seconds" in prediction_result["prediction_metadata"]
