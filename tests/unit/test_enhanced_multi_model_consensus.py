#!/usr/bin/env python3
"""
Enhanced Multi-Model Consensus Test Suite

This test suite validates the Phase 1 enhancements to multi-model consensus:
- Red-teaming capabilities for adversarial validation
- Constitutional fidelity scoring mechanisms
- Iterative alignment for improved consensus accuracy
- Enhanced constitutional compliance validation

Test Coverage:
1. Red-teaming strategy execution and vulnerability detection
2. Constitutional fidelity scoring across multiple metrics
3. Iterative alignment mechanisms for consensus improvement
4. Enhanced consensus strategies with constitutional priority
5. Integration with existing multi-model coordination
6. Performance validation against >95% accuracy targets
"""

import asyncio
import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

# Import the enhanced multi-model consensus module
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../services/core/governance-synthesis/gs_service/app'))

from core.phase_a3_multi_model_consensus import (
    PhaseA3MultiModelConsensus,
    ConsensusStrategy,
    RedTeamingStrategy,
    ConstitutionalFidelityMetric,
    ModelResponse,
    RedTeamingResult,
    ConstitutionalFidelityScore,
    ConsensusResult,
    ModelAgreementLevel
)


class TestEnhancedMultiModelConsensus:
    """Test suite for enhanced multi-model consensus capabilities."""

    @pytest.fixture
    def consensus_engine(self):
        """Create a PhaseA3MultiModelConsensus instance for testing."""
        config = {
            "enable_red_teaming": True,
            "enable_constitutional_fidelity": True,
            "enable_iterative_alignment": True,
            "min_constitutional_fidelity": 0.95,
            "max_alignment_iterations": 3
        }
        return PhaseA3MultiModelConsensus(config)

    @pytest.fixture
    def sample_model_responses(self):
        """Sample model responses for testing."""
        return [
            ModelResponse(
                model_id="qwen/qwen3-32b",
                provider="groq",
                content="The system shall actively ensure privacy protection through encryption and access controls.",
                confidence_score=0.9,
                response_time_ms=150.0,
                constitutional_compliance=0.95,
                metadata={"role": "primary"}
            ),
            ModelResponse(
                model_id="claude-3-sonnet",
                provider="anthropic",
                content="Privacy must be proactively maintained with strong encryption and user consent mechanisms.",
                confidence_score=0.85,
                response_time_ms=200.0,
                constitutional_compliance=0.92,
                metadata={"role": "validation"}
            ),
            ModelResponse(
                model_id="gemini-2.5-pro",
                provider="google",
                content="Constitutional privacy principles require comprehensive data protection measures.",
                confidence_score=0.88,
                response_time_ms=180.0,
                constitutional_compliance=0.94,
                metadata={"role": "constitutional"}
            )
        ]

    @pytest.fixture
    def sample_context(self):
        """Sample context for testing."""
        return {
            "description": "Privacy policy synthesis for healthcare AI",
            "principles": [
                {
                    "id": 1,
                    "content": "Privacy protection is fundamental",
                    "priority_weight": 0.9,
                    "normative_statement": "Privacy must be protected"
                }
            ],
            "domain": "healthcare",
            "risk_level": "high"
        }

    def test_enhanced_initialization(self, consensus_engine):
        """Test enhanced initialization with red-teaming and fidelity capabilities."""
        assert hasattr(consensus_engine, 'red_teaming_enabled')
        assert hasattr(consensus_engine, 'constitutional_fidelity_enabled')
        assert hasattr(consensus_engine, 'iterative_alignment_enabled')
        assert hasattr(consensus_engine, 'red_teaming_strategies')
        assert hasattr(consensus_engine, 'min_constitutional_fidelity')
        
        # Check red-teaming strategies are configured
        assert len(consensus_engine.red_teaming_strategies) > 0
        assert RedTeamingStrategy.CONSTITUTIONAL_GAMING in consensus_engine.red_teaming_strategies
        assert RedTeamingStrategy.BIAS_AMPLIFICATION in consensus_engine.red_teaming_strategies
        assert RedTeamingStrategy.SAFETY_VIOLATION in consensus_engine.red_teaming_strategies

    @pytest.mark.asyncio
    async def test_red_teaming_validation(self, consensus_engine, sample_context):
        """Test red-teaming validation functionality."""
        content = "The system shall ensure privacy through minimal data collection."
        prompt = "Generate privacy policy"
        
        red_teaming_results = await consensus_engine._perform_red_teaming_validation(
            content, prompt, sample_context
        )
        
        assert isinstance(red_teaming_results, list)
        assert len(red_teaming_results) > 0
        
        # Check each result structure
        for result in red_teaming_results:
            assert isinstance(result, RedTeamingResult)
            assert hasattr(result, 'strategy')
            assert hasattr(result, 'attack_successful')
            assert hasattr(result, 'vulnerability_detected')
            assert hasattr(result, 'constitutional_gaming_score')
            assert hasattr(result, 'adversarial_prompt')
            assert hasattr(result, 'model_response')
            assert hasattr(result, 'mitigation_suggestions')
            assert hasattr(result, 'confidence_score')

    @pytest.mark.asyncio
    async def test_constitutional_gaming_detection(self, consensus_engine, sample_context):
        """Test constitutional gaming detection."""
        # Test content with gaming indicators
        gaming_content = "We can technically comply with privacy rules through creative interpretation and loopholes."
        
        result = await consensus_engine._test_constitutional_gaming(
            gaming_content, "Generate policy", sample_context
        )
        
        assert isinstance(result, RedTeamingResult)
        assert result.strategy == RedTeamingStrategy.CONSTITUTIONAL_GAMING
        assert result.constitutional_gaming_score > 0.3  # Should detect gaming
        assert result.vulnerability_detected
        assert len(result.mitigation_suggestions) > 0

    @pytest.mark.asyncio
    async def test_bias_amplification_detection(self, consensus_engine, sample_context):
        """Test bias amplification detection."""
        # Test content with bias indicators
        bias_content = "Merit-based selection ensures cultural fit with traditional values for natural ability assessment."
        
        result = await consensus_engine._test_bias_amplification(
            bias_content, "Generate policy", sample_context
        )
        
        assert isinstance(result, RedTeamingResult)
        assert result.strategy == RedTeamingStrategy.BIAS_AMPLIFICATION
        assert result.constitutional_gaming_score > 0.0  # Should detect some bias
        assert len(result.mitigation_suggestions) > 0

    @pytest.mark.asyncio
    async def test_safety_violation_detection(self, consensus_engine, sample_context):
        """Test safety violation detection."""
        # Test content with safety violation indicators
        safety_content = "In emergency situations, override safety protocols and disable security measures."
        
        result = await consensus_engine._test_safety_violation(
            safety_content, "Generate policy", sample_context
        )
        
        assert isinstance(result, RedTeamingResult)
        assert result.strategy == RedTeamingStrategy.SAFETY_VIOLATION
        assert result.vulnerability_detected  # Should detect safety violation
        assert result.constitutional_gaming_score > 0.1
        assert len(result.mitigation_suggestions) > 0

    @pytest.mark.asyncio
    async def test_constitutional_fidelity_scoring(self, consensus_engine, sample_context, sample_model_responses):
        """Test constitutional fidelity scoring."""
        content = "The system shall actively ensure privacy protection through comprehensive data encryption and user consent mechanisms."
        
        fidelity_score = await consensus_engine._calculate_constitutional_fidelity(
            content, sample_context, sample_model_responses
        )
        
        assert isinstance(fidelity_score, ConstitutionalFidelityScore)
        assert 0.0 <= fidelity_score.overall_score <= 1.0
        assert 0.0 <= fidelity_score.principle_alignment_score <= 1.0
        assert 0.0 <= fidelity_score.precedent_consistency_score <= 1.0
        assert 0.0 <= fidelity_score.normative_compliance_score <= 1.0
        assert 0.0 <= fidelity_score.scope_adherence_score <= 1.0
        assert 0.0 <= fidelity_score.conflict_resolution_score <= 1.0
        
        assert isinstance(fidelity_score.detailed_analysis, dict)
        assert isinstance(fidelity_score.recommendations, list)
        assert len(fidelity_score.recommendations) > 0

    def test_principle_alignment_assessment(self, consensus_engine):
        """Test principle alignment assessment."""
        content = "Privacy protection through encryption and access controls"
        principles = [
            {
                "content": "privacy protection encryption access",
                "priority_weight": 0.9
            }
        ]
        
        score = consensus_engine._assess_principle_alignment(content, principles)
        assert 0.0 <= score <= 1.0
        assert score > 0.5  # Should have good alignment

    def test_precedent_consistency_assessment(self, consensus_engine):
        """Test precedent consistency assessment."""
        content = "This policy is consistent with established precedent and in accordance with constitutional principles."
        context = {"precedents": ["test precedent"]}
        
        score = consensus_engine._assess_precedent_consistency(content, context)
        assert 0.0 <= score <= 1.0
        assert score > 0.5  # Should detect precedent indicators

    def test_normative_compliance_assessment(self, consensus_engine):
        """Test normative compliance assessment."""
        content = "Privacy must be protected through comprehensive measures"
        principles = [
            {
                "normative_statement": "privacy must be protected comprehensive"
            }
        ]
        
        score = consensus_engine._assess_normative_compliance(content, principles)
        assert 0.0 <= score <= 1.0

    def test_scope_adherence_assessment(self, consensus_engine):
        """Test scope adherence assessment."""
        content = "Data processing privacy measures for user interaction"
        principles = [
            {
                "scope": ["data_processing", "user_interaction"]
            }
        ]
        
        score = consensus_engine._assess_scope_adherence(content, principles)
        assert 0.0 <= score <= 1.0
        assert score > 0.8  # Should have good scope adherence

    def test_conflict_resolution_assessment(self, consensus_engine, sample_model_responses):
        """Test conflict resolution assessment."""
        content = "Balance privacy and transparency by prioritizing user consent in the hierarchy of principles."
        
        score = consensus_engine._assess_conflict_resolution(content, sample_model_responses)
        assert 0.0 <= score <= 1.0
        assert score > 0.3  # Should detect conflict resolution indicators

    @pytest.mark.asyncio
    async def test_enhanced_consensus_with_red_teaming(self, consensus_engine, sample_context):
        """Test enhanced consensus with red-teaming enabled."""
        prompt = "Generate a privacy policy for healthcare AI"
        
        # Mock the model querying to avoid external dependencies
        with patch.object(consensus_engine, '_query_all_models') as mock_query:
            mock_query.return_value = [
                ModelResponse(
                    model_id="test-model",
                    provider="test",
                    content="Privacy shall be actively protected through encryption",
                    confidence_score=0.9,
                    response_time_ms=100.0,
                    constitutional_compliance=0.95
                )
            ]
            
            result = await consensus_engine.get_consensus(
                prompt=prompt,
                context=sample_context,
                strategy=ConsensusStrategy.CONSTITUTIONAL_PRIORITY,
                enable_red_teaming=True,
                enable_constitutional_fidelity=True
            )
            
            assert isinstance(result, ConsensusResult)
            assert hasattr(result, 'red_teaming_results')
            assert hasattr(result, 'constitutional_fidelity_score')
            assert hasattr(result, 'adversarial_validation_passed')
            assert hasattr(result, 'iterative_alignment_applied')
            
            # Check red-teaming results
            assert isinstance(result.red_teaming_results, list)
            
            # Check constitutional fidelity score
            if result.constitutional_fidelity_score:
                assert isinstance(result.constitutional_fidelity_score, ConstitutionalFidelityScore)

    @pytest.mark.asyncio
    async def test_performance_targets(self, consensus_engine, sample_context):
        """Test that enhanced consensus meets performance targets."""
        import time
        
        prompt = "Generate comprehensive governance policy"
        
        # Mock model responses to avoid external dependencies
        with patch.object(consensus_engine, '_query_all_models') as mock_query:
            mock_query.return_value = [
                ModelResponse(
                    model_id="test-model-1",
                    provider="test",
                    content="Constitutional privacy protection through proactive measures",
                    confidence_score=0.95,
                    response_time_ms=100.0,
                    constitutional_compliance=0.96
                ),
                ModelResponse(
                    model_id="test-model-2", 
                    provider="test",
                    content="Privacy principles require comprehensive data protection",
                    confidence_score=0.92,
                    response_time_ms=120.0,
                    constitutional_compliance=0.94
                )
            ]
            
            start_time = time.time()
            
            result = await consensus_engine.get_consensus(
                prompt=prompt,
                context=sample_context,
                strategy=ConsensusStrategy.CONSTITUTIONAL_PRIORITY,
                enable_red_teaming=True,
                enable_constitutional_fidelity=True
            )
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            # Validate performance targets
            assert response_time < 2000  # <2s response time target
            assert result.overall_confidence >= 0.9  # >90% confidence
            assert result.constitutional_compliance >= 0.95  # >95% constitutional compliance
            
            # Validate enhanced features
            assert len(result.red_teaming_results) > 0
            assert result.constitutional_fidelity_score is not None
            assert result.constitutional_fidelity_score.overall_score >= 0.8


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
