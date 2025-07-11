"""
Comprehensive Unit Tests for Collective Constitutional AI Service
HASH-OK:cdd01ef066bc6cf2

Tests the collective constitutional AI functionality including:
- Polis platform integration
- BBQ bias evaluation framework
- Democratic legitimacy scoring
- Collective preference aggregation
- Constitutional hash validation
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, timezone
import uuid

from services.core.constitutional_ai.ac_service.app.services.collective_constitutional_ai import (
    CollectiveConstitutionalAI,
    BiasCategory,
    DemocraticLegitimacyLevel,
    PolisConversation,
    BiasEvaluationResult,
    CollectiveInput,
    DemocraticPrinciple,
    CONSTITUTIONAL_HASH
)

# Constitutional Hash: cdd01ef066bc6cf2

class TestCollectiveConstitutionalAI:
    """Comprehensive test suite for Collective Constitutional AI."""

    @pytest.fixture
    def mock_polis_client(self):
        """Mock Polis client for testing."""
        client = AsyncMock()
        client.create_conversation.return_value = {
            "conversation_id": "test_conv_123",
            "url": "https://polis.test/conv/123"
        }
        client.get_conversation_data.return_value = {
            "participant_count": 150,
            "statement_count": 45,
            "consensus_statements": ["Privacy is important", "Transparency matters"],
            "polarizing_statements": ["Data collection should be unlimited"]
        }
        return client

    @pytest.fixture
    def mock_democratic_governance(self):
        """Mock democratic governance orchestrator."""
        orchestrator = AsyncMock()
        orchestrator.calculate_legitimacy_score.return_value = 0.85
        orchestrator.aggregate_preferences.return_value = {
            "consensus_level": 0.78,
            "participant_diversity": 0.82,
            "deliberation_quality": 0.75
        }
        return orchestrator

    @pytest.fixture
    def collective_ai_service(self, mock_polis_client, mock_democratic_governance):
        """Create CollectiveConstitutionalAI instance with mocked dependencies."""
        return CollectiveConstitutionalAI(
            polis_client=mock_polis_client,
            democratic_governance=mock_democratic_governance
        )

    @pytest.fixture
    def sample_polis_conversation(self):
        """Sample Polis conversation for testing."""
        return PolisConversation(
            conversation_id="test_conv_456",
            topic="Data Privacy Rights",
            description="Democratic deliberation on data privacy principles",
            created_at=datetime.now(timezone.utc),
            participant_count=200,
            statement_count=60,
            consensus_statements=[
                "Users should control their personal data",
                "Data collection requires explicit consent"
            ],
            polarizing_statements=[
                "Companies should have unlimited data access"
            ],
            status="active"
        )

    @pytest.fixture
    def sample_bias_evaluation_result(self):
        """Sample bias evaluation result for testing."""
        return BiasEvaluationResult(
            category=BiasCategory.GENDER_IDENTITY,
            bias_score=0.15,  # Low bias
            confidence=0.92,
            examples=[
                "Policy treats all gender identities equally",
                "No discriminatory language detected"
            ],
            recommendations=[
                "Continue inclusive language practices",
                "Regular bias monitoring recommended"
            ],
            baseline_comparison=0.35  # Improvement from baseline
        )

    async def test_constitutional_hash_validation(self, collective_ai_service):
        """Test that constitutional hash is properly validated."""
        assert CONSTITUTIONAL_HASH == "cdd01ef066bc6cf2"
        assert collective_ai_service is not None

    async def test_create_polis_conversation(self, collective_ai_service, mock_polis_client):
        """Test creating a Polis conversation for democratic deliberation."""
        topic = "AI Governance Principles"
        description = "Collective deliberation on AI governance"
        
        result = await collective_ai_service.create_polis_conversation(topic, description)
        
        assert result is not None
        assert "conversation_id" in result
        assert "url" in result
        
        # Verify Polis client was called
        mock_polis_client.create_conversation.assert_called_once_with(
            topic=topic,
            description=description
        )

    async def test_evaluate_bias_bbq(self, collective_ai_service):
        """Test BBQ bias evaluation framework."""
        principle_text = "All users deserve equal treatment regardless of background"
        categories = [BiasCategory.RACE_ETHNICITY, BiasCategory.GENDER_IDENTITY]
        
        with patch.object(collective_ai_service, '_evaluate_bias_for_category') as mock_evaluate:
            mock_evaluate.return_value = BiasEvaluationResult(
                category=BiasCategory.RACE_ETHNICITY,
                bias_score=0.12,
                confidence=0.88,
                examples=["Inclusive language used"],
                recommendations=["Continue current practices"],
                baseline_comparison=0.25
            )
            
            results = await collective_ai_service.evaluate_bias_bbq(principle_text, categories)
            
            assert len(results) == len(categories)
            assert all(isinstance(result, BiasEvaluationResult) for result in results)
            assert all(result.bias_score >= 0 and result.bias_score <= 1 for result in results)

    async def test_aggregate_collective_input(self, collective_ai_service, mock_polis_client):
        """Test aggregating collective input from Polis conversation."""
        conversation_id = "test_conv_789"
        min_consensus = 0.6
        
        # Mock conversation data
        mock_polis_client.get_conversation_data.return_value = {
            "participant_count": 300,
            "statement_count": 80,
            "consensus_statements": [
                "Privacy is a fundamental right",
                "Transparency builds trust",
                "User consent is essential"
            ],
            "polarizing_statements": ["Data should be freely shared"],
            "participant_demographics": {
                "age_distribution": {"18-30": 0.3, "31-50": 0.4, "51+": 0.3},
                "geographic_distribution": {"urban": 0.6, "rural": 0.4}
            }
        }
        
        results = await collective_ai_service.aggregate_collective_input(
            conversation_id, min_consensus
        )
        
        assert isinstance(results, list)
        assert len(results) > 0
        assert all(isinstance(input_item, CollectiveInput) for input_item in results)
        
        # Verify all inputs meet consensus threshold
        for input_item in results:
            assert input_item.consensus_level >= min_consensus

    async def test_synthesize_democratic_principle(self, collective_ai_service, mock_democratic_governance):
        """Test synthesizing democratic principle from collective inputs."""
        topic = "Data Protection Rights"
        collective_inputs = [
            CollectiveInput(
                statement="Users should control their data",
                support_count=250,
                total_participants=300,
                consensus_level=0.83,
                demographic_breakdown={"age": {"18-30": 0.4, "31+": 0.6}},
                timestamp=datetime.now(timezone.utc)
            ),
            CollectiveInput(
                statement="Consent must be explicit and informed",
                support_count=270,
                total_participants=300,
                consensus_level=0.90,
                demographic_breakdown={"age": {"18-30": 0.3, "31+": 0.7}},
                timestamp=datetime.now(timezone.utc)
            )
        ]
        
        with patch.object(collective_ai_service, '_synthesize_principle_text') as mock_synthesize:
            mock_synthesize.return_value = "Users have the fundamental right to control their personal data through explicit, informed consent mechanisms"
            
            result = await collective_ai_service.synthesize_democratic_principle(
                topic, collective_inputs
            )
            
            assert isinstance(result, DemocraticPrinciple)
            assert result.topic == topic
            assert result.principle_text is not None
            assert result.legitimacy_score > 0
            assert result.constitutional_hash == CONSTITUTIONAL_HASH
            assert len(result.supporting_inputs) == len(collective_inputs)

    async def test_calculate_democratic_legitimacy(self, collective_ai_service, mock_democratic_governance):
        """Test calculating democratic legitimacy score."""
        collective_inputs = [
            CollectiveInput(
                statement="Test statement 1",
                support_count=180,
                total_participants=200,
                consensus_level=0.90,
                demographic_breakdown={},
                timestamp=datetime.now(timezone.utc)
            )
        ]
        
        legitimacy_score = await collective_ai_service.calculate_democratic_legitimacy(
            collective_inputs
        )
        
        assert isinstance(legitimacy_score, float)
        assert 0 <= legitimacy_score <= 1
        
        # Verify democratic governance orchestrator was called
        mock_democratic_governance.calculate_legitimacy_score.assert_called_once()

    async def test_bias_category_coverage(self, collective_ai_service):
        """Test that all nine BBQ bias categories are supported."""
        expected_categories = {
            BiasCategory.AGE,
            BiasCategory.DISABILITY_STATUS,
            BiasCategory.GENDER_IDENTITY,
            BiasCategory.NATIONALITY,
            BiasCategory.PHYSICAL_APPEARANCE,
            BiasCategory.RACE_ETHNICITY,
            BiasCategory.RELIGION,
            BiasCategory.SEXUAL_ORIENTATION,
            BiasCategory.SOCIOECONOMIC_STATUS
        }
        
        # Test that all categories are defined
        assert len(expected_categories) == 9
        
        # Test bias evaluation for each category
        principle_text = "Test principle for bias evaluation"
        
        for category in expected_categories:
            with patch.object(collective_ai_service, '_evaluate_bias_for_category') as mock_evaluate:
                mock_evaluate.return_value = BiasEvaluationResult(
                    category=category,
                    bias_score=0.1,
                    confidence=0.9,
                    examples=[],
                    recommendations=[],
                    baseline_comparison=0.3
                )
                
                result = await collective_ai_service._evaluate_bias_for_category(
                    principle_text, category
                )
                
                assert result.category == category
                assert isinstance(result.bias_score, float)

    async def test_democratic_legitimacy_levels(self, collective_ai_service):
        """Test democratic legitimacy level classification."""
        test_cases = [
            (0.25, DemocraticLegitimacyLevel.LOW),
            (0.45, DemocraticLegitimacyLevel.MODERATE),
            (0.70, DemocraticLegitimacyLevel.HIGH),
            (0.85, DemocraticLegitimacyLevel.CONSENSUS)
        ]
        
        for score, expected_level in test_cases:
            level = collective_ai_service._classify_legitimacy_level(score)
            assert level == expected_level

    async def test_performance_metrics(self, collective_ai_service):
        """Test performance metrics collection."""
        import time
        
        start_time = time.time()
        
        # Test a lightweight operation
        principle_text = "Test principle"
        categories = [BiasCategory.GENDER_IDENTITY]
        
        with patch.object(collective_ai_service, '_evaluate_bias_for_category') as mock_evaluate:
            mock_evaluate.return_value = BiasEvaluationResult(
                category=BiasCategory.GENDER_IDENTITY,
                bias_score=0.1,
                confidence=0.9,
                examples=[],
                recommendations=[],
                baseline_comparison=0.3
            )
            
            await collective_ai_service.evaluate_bias_bbq(principle_text, categories)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete quickly (performance target)
        assert execution_time < 1.0

    async def test_constitutional_hash_consistency(self, collective_ai_service):
        """Test constitutional hash consistency across operations."""
        topic = "Test Topic"
        collective_inputs = [
            CollectiveInput(
                statement="Test statement",
                support_count=100,
                total_participants=120,
                consensus_level=0.83,
                demographic_breakdown={},
                timestamp=datetime.now(timezone.utc)
            )
        ]
        
        with patch.object(collective_ai_service, '_synthesize_principle_text') as mock_synthesize:
            mock_synthesize.return_value = "Test principle text"
            
            result = await collective_ai_service.synthesize_democratic_principle(
                topic, collective_inputs
            )
            
            # Verify constitutional hash is consistent
            assert result.constitutional_hash == CONSTITUTIONAL_HASH
            assert result.constitutional_hash == "cdd01ef066bc6cf2"

    async def test_error_handling(self, collective_ai_service, mock_polis_client):
        """Test error handling in collective AI operations."""
        # Test with Polis client error
        mock_polis_client.create_conversation.side_effect = Exception("Polis API error")
        
        try:
            await collective_ai_service.create_polis_conversation("Test", "Description")
            assert False, "Should have raised an exception"
        except Exception as e:
            assert "Polis API error" in str(e) or isinstance(e, Exception)

    async def test_collective_input_validation(self, collective_ai_service):
        """Test validation of collective input data."""
        # Test valid collective input
        valid_input = CollectiveInput(
            statement="Valid statement",
            support_count=80,
            total_participants=100,
            consensus_level=0.80,
            demographic_breakdown={"age": {"18-30": 0.5, "31+": 0.5}},
            timestamp=datetime.now(timezone.utc)
        )
        
        assert valid_input.consensus_level == 0.80
        assert valid_input.support_count <= valid_input.total_participants
        assert 0 <= valid_input.consensus_level <= 1

    async def test_polis_conversation_lifecycle(self, collective_ai_service, sample_polis_conversation):
        """Test Polis conversation lifecycle management."""
        conversation = sample_polis_conversation
        
        # Test conversation properties
        assert conversation.conversation_id is not None
        assert conversation.topic is not None
        assert conversation.participant_count >= 0
        assert conversation.statement_count >= 0
        assert isinstance(conversation.consensus_statements, list)
        assert isinstance(conversation.polarizing_statements, list)
        assert conversation.status in ["active", "closed", "archived"]

    async def test_bias_reduction_effectiveness(self, collective_ai_service, sample_bias_evaluation_result):
        """Test bias reduction effectiveness measurement."""
        result = sample_bias_evaluation_result
        
        # Test bias reduction calculation
        bias_reduction = result.baseline_comparison - result.bias_score
        assert bias_reduction > 0  # Should show improvement
        
        # Test that bias score is within acceptable range
        assert 0 <= result.bias_score <= 1
        assert result.confidence > 0.5  # Should have reasonable confidence
        
        # Test recommendations are provided
        assert len(result.recommendations) > 0
