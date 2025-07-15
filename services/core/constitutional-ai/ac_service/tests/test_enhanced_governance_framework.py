"""
Comprehensive Tests for Enhanced Constitutional Governance Framework
Constitutional Hash: cdd01ef066bc6cf2

This module provides comprehensive unit tests, integration tests, and performance
validation tests for the enhanced governance framework, targeting >80% coverage
and constitutional compliance verification.

Key Test Areas:
- 4-step algorithm validation (diversity generation, consensus, OOB, causal insights)
- Domain-adaptive governance testing
- Production hardening features
- Performance target validation
- Constitutional compliance verification
- Integration with existing ACGS services
"""

import asyncio
import time
from unittest.mock import AsyncMock

import numpy as np
import pytest
from app.services.enhanced_governance_framework import (

# Add parent directory to path to handle dash-named directories
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../..'))

    DomainAdaptiveGovernance,
    DomainType,
    GovernanceConfig,
    GovernanceFrameworkIntegration,
    GovernanceResult,
    ProductionGovernanceFramework,
)
from app.services.governance_monitoring import (
    GovernanceMonitor,
    HealthStatus,
    PerformanceMetrics,
)

# Constitutional hash constant
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class TestProductionGovernanceFramework:
    """Test suite for ProductionGovernanceFramework"""

    @pytest.fixture
    def sample_principles(self) -> list[str]:
        """Sample constitutional principles for testing"""
        return [
            "democratic_participation",
            "transparency_requirement",
            "constitutional_compliance",
            "accountability_framework",
            "rights_protection",
            "due_process",
            "equal_protection",
        ]

    @pytest.fixture
    def governance_config(self) -> GovernanceConfig:
        """Test governance configuration"""
        return GovernanceConfig(
            confidence_threshold=0.6,
            violation_threshold=0.1,
            cache_ttl=300,
            max_retries=3,
            timeout_seconds=5,
        )

    @pytest.fixture
    def mock_audit_logger(self) -> AsyncMock:
        """Mock audit logger"""
        logger = AsyncMock()
        logger.log_governance_decision = AsyncMock()
        return logger

    @pytest.fixture
    def mock_alerting_system(self) -> AsyncMock:
        """Mock alerting system"""
        alerting = AsyncMock()
        alerting.send_alert = AsyncMock()
        return alerting

    @pytest.fixture
    def governance_framework(
        self,
        sample_principles,
        governance_config,
        mock_audit_logger,
        mock_alerting_system,
    ) -> ProductionGovernanceFramework:
        """Create governance framework instance for testing"""
        return ProductionGovernanceFramework(
            principles=sample_principles,
            B=5,
            config=governance_config,
            audit_logger=mock_audit_logger,
            alerting_system=mock_alerting_system,
        )

    def test_framework_initialization(self, governance_framework):
        """Test framework initialization"""
        assert governance_framework.principles is not None
        assert len(governance_framework.principles) == 7
        assert governance_framework.B == 5
        assert governance_framework.m == 3  # sqrt(7) + 1
        assert governance_framework.forest is not None
        assert len(governance_framework.forest) == 5
        assert governance_framework.correlation_matrix is not None

    def test_correlation_aware_bootstrap(self, governance_framework):
        """Test correlation-aware bootstrap sampling"""
        max_correlation = 0.5
        sampled = governance_framework._correlation_aware_bootstrap(max_correlation)

        assert isinstance(sampled, list)
        assert len(sampled) <= governance_framework.m
        assert all(
            principle in governance_framework.principles for principle in sampled
        )
        # Should have unique principles
        assert len(sampled) == len(set(sampled))

    @pytest.mark.asyncio
    async def test_govern_basic_functionality(self, governance_framework):
        """Test basic governance functionality"""
        query = "Should we implement new privacy policy?"
        context = {"domain": "privacy", "urgency": "high"}

        result = await governance_framework.govern(query, context)

        assert isinstance(result, GovernanceResult)
        assert result.governance_id.startswith("gov_")
        assert result.consensus_result in {"comply", "violate", "uncertain"}
        assert 0.0 <= result.confidence <= 1.0
        assert 0.0 <= result.compliance_score <= 1.0
        assert result.constitutional_hash == CONSTITUTIONAL_HASH
        assert isinstance(result.decisions, list)
        assert isinstance(result.principle_importance, dict)
        assert isinstance(result.recommendations, list)

    @pytest.mark.asyncio
    async def test_consensus_aggregation(self, governance_framework):
        """Test consensus aggregation with confidence calibration"""
        query = "Test query"
        context = {}

        decisions, consensus, confidence = (
            await governance_framework._consensus_aggregation(query, context)
        )

        assert isinstance(decisions, list)
        assert len(decisions) == governance_framework.B
        assert consensus in {"comply", "violate", "uncertain"}
        assert 0.0 <= confidence <= 1.0
        # Confidence should be calibrated (lower than raw confidence)
        raw_confidence = decisions.count(consensus) / len(decisions)
        assert confidence <= raw_confidence

    @pytest.mark.asyncio
    async def test_oob_compliance_check(self, governance_framework):
        """Test out-of-bag compliance diagnostics"""
        query = "Test query"
        context = {}

        violation_rates, flagged_trees = (
            await governance_framework._oob_compliance_check(query, context)
        )

        assert isinstance(violation_rates, list)
        assert len(violation_rates) == governance_framework.B
        assert all(0.0 <= rate <= 1.0 for rate in violation_rates)
        assert isinstance(flagged_trees, list)
        assert all(isinstance(tree_id, int) for tree_id in flagged_trees)

    @pytest.mark.asyncio
    async def test_principle_importance_analysis(self, governance_framework):
        """Test principle importance analysis with causal insights"""
        query = "Test query"
        context = {}
        flagged_trees = [0, 2]

        importance_scores, helpful_principles = (
            await governance_framework._principle_importance_analysis(
                query, context, flagged_trees
            )
        )

        assert isinstance(importance_scores, dict)
        assert len(importance_scores) == len(governance_framework.principles)
        assert all(
            principle in governance_framework.principles
            for principle in importance_scores
        )
        assert isinstance(helpful_principles, list)
        # Helpful principles should have negative importance
        assert all(importance_scores[principle] < 0 for principle in helpful_principles)

    def test_confidence_calibration(self, governance_framework):
        """Test confidence calibration"""
        raw_confidence = 0.8
        sample_size = 5

        calibrated = governance_framework._calibrate_confidence(
            raw_confidence, sample_size
        )

        assert 0.0 <= calibrated <= 1.0
        assert calibrated <= raw_confidence  # Should be more conservative

    def test_compliance_score_calculation(self, governance_framework):
        """Test compliance score calculation"""
        violation_rates = [0.1, 0.05, 0.2, 0.0, 0.15]
        confidence = 0.8

        compliance_score = governance_framework._calculate_compliance_score(
            violation_rates, confidence
        )

        assert 0.0 <= compliance_score <= 1.0
        # Should be weighted by confidence
        expected_compliance = (
            1.0 - sum(violation_rates) / len(violation_rates)
        ) * confidence
        assert abs(compliance_score - expected_compliance) < 0.01

    def test_recommendation_generation(self, governance_framework):
        """Test recommendation generation"""
        consensus_result = "violate"
        confidence = 0.4  # Below threshold
        flagged_trees = [0, 2]
        importance_scores = {"principle1": -0.2, "principle2": 0.1}

        recommendations = governance_framework._generate_recommendations(
            consensus_result, confidence, flagged_trees, importance_scores
        )

        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        # Should include recommendations for low confidence and violations
        assert any("confidence" in rec.lower() for rec in recommendations)
        assert any(
            "violate" in rec.lower() or "revision" in rec.lower()
            for rec in recommendations
        )


class TestDomainAdaptiveGovernance:
    """Test suite for DomainAdaptiveGovernance"""

    @pytest.fixture
    def sample_principles(self) -> list[str]:
        """Sample constitutional principles for testing"""
        return [
            "democratic_participation",
            "transparency_requirement",
            "constitutional_compliance",
            "accountability_framework",
            "rights_protection",
        ]

    def test_domain_specific_configuration(self, sample_principles):
        """Test domain-specific configuration"""
        # Test healthcare domain
        healthcare_framework = DomainAdaptiveGovernance(
            principles=sample_principles,
            domain=DomainType.HEALTHCARE,
        )
        assert healthcare_framework.config.confidence_threshold == 0.8
        assert healthcare_framework.config.violation_threshold == 0.05

        # Test finance domain
        finance_framework = DomainAdaptiveGovernance(
            principles=sample_principles,
            domain=DomainType.FINANCE,
        )
        assert finance_framework.config.confidence_threshold == 0.7
        assert finance_framework.config.violation_threshold == 0.08

        # Test general domain (default)
        general_framework = DomainAdaptiveGovernance(
            principles=sample_principles,
            domain=DomainType.GENERAL,
        )
        assert general_framework.config.confidence_threshold == 0.6

    @pytest.mark.asyncio
    async def test_domain_specific_governance(self, sample_principles):
        """Test governance behavior varies by domain"""
        query = "Should we implement new data collection policy?"

        # Healthcare should be more strict
        healthcare_framework = DomainAdaptiveGovernance(
            principles=sample_principles,
            domain=DomainType.HEALTHCARE,
        )
        healthcare_result = await healthcare_framework.govern(query)

        # General domain should be less strict
        general_framework = DomainAdaptiveGovernance(
            principles=sample_principles,
            domain=DomainType.GENERAL,
        )
        general_result = await general_framework.govern(query)

        # Both should return valid results
        assert isinstance(healthcare_result, GovernanceResult)
        assert isinstance(general_result, GovernanceResult)
        assert healthcare_result.constitutional_hash == CONSTITUTIONAL_HASH
        assert general_result.constitutional_hash == CONSTITUTIONAL_HASH


class TestGovernanceFrameworkIntegration:
    """Test suite for GovernanceFrameworkIntegration"""

    @pytest.fixture
    def mock_constitutional_validator(self) -> AsyncMock:
        """Mock constitutional validator"""
        validator = AsyncMock()
        validator.validate_constitutional_compliance = AsyncMock(
            return_value={
                "overall_compliant": True,
                "compliance_score": 0.9,
                "next_steps": ["Proceed to implementation"],
            }
        )
        return validator

    @pytest.fixture
    def mock_formal_verification_client(self) -> AsyncMock:
        """Mock formal verification client"""
        client = AsyncMock()
        client.verify_governance_decision = AsyncMock(
            return_value={
                "verified": True,
                "verification_score": 0.95,
                "recommendations": ["Formal verification passed"],
            }
        )
        return client

    @pytest.fixture
    def integration(
        self, mock_constitutional_validator, mock_formal_verification_client
    ) -> GovernanceFrameworkIntegration:
        """Create integration instance for testing"""
        return GovernanceFrameworkIntegration(
            constitutional_validator=mock_constitutional_validator,
            formal_verification_client=mock_formal_verification_client,
        )

    def test_integration_initialization(self, integration):
        """Test integration initialization"""
        assert integration.constitutional_validator is not None
        assert integration.formal_verification_client is not None
        assert len(integration.frameworks) == len(DomainType)
        # All domain frameworks should be initialized
        for domain in DomainType:
            assert domain in integration.frameworks

    @pytest.mark.asyncio
    async def test_comprehensive_governance_evaluation(self, integration):
        """Test comprehensive governance evaluation with all components"""
        query = "Should we implement new AI governance policy?"
        domain = DomainType.GENERAL
        context = {"priority": "high"}

        result = await integration.evaluate_governance(
            query=query,
            domain=domain,
            context=context,
            include_formal_verification=True,
        )

        assert isinstance(result, dict)
        assert "evaluation_id" in result
        assert "domain" in result
        assert "final_decision" in result
        assert "overall_compliance_score" in result
        assert "enhanced_governance" in result
        assert "constitutional_validation" in result
        assert "formal_verification" in result
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH

        # Verify constitutional validator was called
        integration.constitutional_validator.validate_constitutional_compliance.assert_called_once()

        # Verify formal verification was called
        integration.formal_verification_client.verify_governance_decision.assert_called_once()

    @pytest.mark.asyncio
    async def test_evaluation_without_formal_verification(self, integration):
        """Test evaluation without formal verification"""
        query = "Test query"

        result = await integration.evaluate_governance(
            query=query,
            include_formal_verification=False,
        )

        assert result["formal_verification"] is None
        # Formal verification should not be called
        integration.formal_verification_client.verify_governance_decision.assert_not_called()


class TestGovernanceMonitor:
    """Test suite for GovernanceMonitor"""

    @pytest.fixture
    def mock_alerting_system(self) -> AsyncMock:
        """Mock alerting system"""
        alerting = AsyncMock()
        alerting.send_alert = AsyncMock()
        return alerting

    @pytest.fixture
    def monitor(self, mock_alerting_system) -> GovernanceMonitor:
        """Create monitor instance for testing"""
        return GovernanceMonitor(alerting_system=mock_alerting_system)

    @pytest.mark.asyncio
    async def test_request_recording(self, monitor):
        """Test request metrics recording"""
        await monitor.record_request(
            latency_ms=2.5,
            success=True,
            cache_hit=True,
            constitutional_compliant=True,
        )

        assert len(monitor.latency_samples) == 1
        assert len(monitor.error_samples) == 1
        assert len(monitor.cache_samples) == 1
        assert len(monitor.compliance_samples) == 1

    def test_performance_metrics_calculation(self, monitor):
        """Test performance metrics calculation"""
        # Add sample data
        current_time = time.time()
        monitor.latency_samples.extend(
            [
                (current_time, 1.0),
                (current_time, 2.0),
                (current_time, 3.0),
                (current_time, 4.0),
                (current_time, 5.0),
            ]
        )
        monitor.error_samples.extend(
            [
                (current_time, False),
                (current_time, False),
                (current_time, True),
                (current_time, False),
                (current_time, False),
            ]
        )
        monitor.cache_samples.extend(
            [
                (current_time, True),
                (current_time, True),
                (current_time, False),
                (current_time, True),
                (current_time, True),
            ]
        )
        monitor.compliance_samples.extend(
            [
                (current_time, True),
                (current_time, True),
                (current_time, True),
                (current_time, True),
                (current_time, False),
            ]
        )

        metrics = monitor.get_current_metrics()

        assert isinstance(metrics, PerformanceMetrics)
        assert metrics.p99_latency_ms == 5.0
        assert metrics.p50_latency_ms == 3.0
        assert metrics.error_rate == 0.2  # 1 error out of 5
        assert metrics.cache_hit_rate == 0.8  # 4 hits out of 5
        assert metrics.constitutional_compliance_rate == 0.8  # 4 compliant out of 5

    def test_health_status_healthy(self, monitor):
        """Test health status when system is healthy"""
        health = monitor.get_health_status()

        assert health["status"] == HealthStatus.HEALTHY.value
        assert "timestamp" in health
        assert "metrics" in health
        assert "circuit_breaker" in health
        assert health["constitutional_hash"] == CONSTITUTIONAL_HASH

    def test_circuit_breaker_functionality(self, monitor):
        """Test circuit breaker functionality"""
        # Initially closed
        assert not monitor.is_circuit_breaker_open()

        # Simulate failures to open circuit breaker
        for _ in range(5):  # failure_threshold = 5
            asyncio.run(monitor._update_circuit_breaker(False))

        assert monitor.circuit_breaker.is_open
        assert monitor.is_circuit_breaker_open()

    @pytest.mark.asyncio
    async def test_performance_violation_alerting(self, monitor):
        """Test alerting for performance violations"""
        # Simulate high latency
        current_time = time.time()
        monitor.latency_samples.extend(
            [
                (current_time, 10.0),  # Above 5ms target
                (current_time, 15.0),
                (current_time, 20.0),
            ]
        )

        await monitor._check_performance_violations()

        # Should trigger alert for P99 latency violation
        monitor.alerting_system.send_alert.assert_called()


class TestPerformanceValidation:
    """Performance validation tests for ACGS-2 targets"""

    @pytest.mark.asyncio
    async def test_latency_target_validation(self):
        """Test P99 latency < 5ms target"""
        principles = ["test_principle_1", "test_principle_2"]
        framework = ProductionGovernanceFramework(principles=principles, B=3)

        # Measure latency for multiple requests
        latencies = []
        for _ in range(10):
            start_time = time.time()
            await framework.govern("test query")
            latency_ms = (time.time() - start_time) * 1000
            latencies.append(latency_ms)

        # Calculate P99 latency
        p99_latency = float(np.percentile(latencies, 99))

        # Should meet ACGS-2 target
        assert p99_latency < 5.0, f"P99 latency {p99_latency:.2f}ms exceeds 5ms target"

    @pytest.mark.asyncio
    async def test_constitutional_compliance_validation(self):
        """Test 100% constitutional compliance requirement"""
        principles = ["test_principle"]
        framework = ProductionGovernanceFramework(principles=principles)

        result = await framework.govern("test query")

        # All results must include constitutional hash
        assert result.constitutional_hash == CONSTITUTIONAL_HASH
        assert hasattr(result, "constitutional_hash")

        # Compliance score should be calculated
        assert 0.0 <= result.compliance_score <= 1.0

    def test_cache_hit_rate_target(self):
        """Test >85% cache hit rate target"""
        monitor = GovernanceMonitor()

        # Simulate cache hits
        current_time = time.time()
        cache_samples = [True] * 90 + [False] * 10  # 90% hit rate
        monitor.cache_samples.extend([(current_time, hit) for hit in cache_samples])

        metrics = monitor.get_current_metrics()

        # Should meet ACGS-2 target
        assert (
            metrics.cache_hit_rate >= 0.85
        ), f"Cache hit rate {metrics.cache_hit_rate:.2%} below 85% target"


# Test configuration
@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


if __name__ == "__main__":
    pytest.main(
        [
            __file__,
            "-v",
            "--cov=services.core.constitutional-ai.ac_service.app.services",
        ]
    )
