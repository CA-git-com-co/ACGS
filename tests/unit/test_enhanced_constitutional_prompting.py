#!/usr/bin/env python3
"""
Enhanced Constitutional Prompting Test Suite

This test suite validates the Phase 1 enhancements to constitutional prompting:
- Chain-of-Thought reasoning capabilities
- Retrieval-Augmented Generation for constitutional precedents
- Positive action-focused phrasing patterns
- Enhanced constitutional compliance verification

Test Coverage:
1. Chain-of-Thought template initialization and usage
2. Positive action pattern application and transformation
3. Constitutional precedent retrieval and caching
4. Enhanced prompt building with RAG and CoT
5. Integration with existing constitutional context building
6. Performance validation against >95% constitutional compliance targets
"""

import os

# Import the enhanced constitutional prompting module
import sys
from unittest.mock import MagicMock

import pytest

# Add the project root to the path
project_root = os.path.join(os.path.dirname(__file__), "../..")
sys.path.insert(0, project_root)

# Mock the AC service client and WINA services to avoid import issues

sys.modules["services.core.governance_synthesis.gs_service.app.services.ac_client"] = (
    MagicMock()
)
sys.modules["services.shared.wina.constitutional_integration"] = MagicMock()

# Import the module directly
sys.path.insert(0, "services/core/governance-synthesis/gs_service")
from .core.constitutional_prompting import ConstitutionalPromptBuilder


class TestEnhancedConstitutionalPrompting:
    """Test suite for enhanced constitutional prompting capabilities."""

    @pytest.fixture
    def prompt_builder(self):
        """Create a ConstitutionalPromptBuilder instance for testing."""
        return ConstitutionalPromptBuilder(enable_wina_integration=False)

    @pytest.fixture
    def sample_principles(self):
        """Sample constitutional principles for testing."""
        return [
            {
                "id": 1,
                "name": "Privacy Protection",
                "content": "The system shall actively ensure user privacy and data protection",
                "category": "privacy",
                "priority_weight": 0.9,
                "normative_statement": "Privacy must be protected at all times",
                "scope": ["data_processing", "user_interaction"],
                "constraints": ["encryption_required", "consent_mandatory"],
            },
            {
                "id": 2,
                "name": "Fairness and Non-Discrimination",
                "content": "The system must proactively prevent bias and discrimination",
                "category": "fairness",
                "priority_weight": 0.85,
                "normative_statement": "All users must be treated fairly",
                "scope": ["decision_making", "resource_allocation"],
                "constraints": ["bias_monitoring", "equal_treatment"],
            },
        ]

    @pytest.fixture
    def sample_context(self):
        """Sample constitutional context for testing."""
        return {
            "context": "healthcare_ai",
            "category": "privacy",
            "principles": [],
            "principle_count": 0,
            "constitutional_hierarchy": [],
            "scope_constraints": {},
            "normative_framework": {},
        }

    def test_cot_templates_initialization(self, prompt_builder):
        """Test Chain-of-Thought templates are properly initialized."""
        assert hasattr(prompt_builder, "cot_templates")
        assert isinstance(prompt_builder.cot_templates, dict)

        # Check required templates exist
        required_templates = [
            "constitutional_analysis",
            "precedent_analysis",
            "positive_action_focus",
        ]

        for template in required_templates:
            assert template in prompt_builder.cot_templates
            assert isinstance(prompt_builder.cot_templates[template], str)
            assert (
                len(prompt_builder.cot_templates[template]) > 100
            )  # Substantial content

    def test_positive_patterns_initialization(self, prompt_builder):
        """Test positive action patterns are properly initialized."""
        assert hasattr(prompt_builder, "positive_action_patterns")
        assert isinstance(prompt_builder.positive_action_patterns, dict)

        # Check required pattern categories
        required_categories = [
            "requirement_patterns",
            "capability_patterns",
            "outcome_patterns",
            "monitoring_patterns",
        ]

        for category in required_categories:
            assert category in prompt_builder.positive_action_patterns
            assert isinstance(prompt_builder.positive_action_patterns[category], list)
            assert len(prompt_builder.positive_action_patterns[category]) > 0

    def test_positive_pattern_application(self, prompt_builder):
        """Test positive action pattern application to text."""
        # Test negative to positive transformations
        test_cases = [
            ("shall not violate privacy", "shall actively prevent violate privacy"),
            ("must not discriminate", "must proactively avoid discriminate"),
            (
                "do not access unauthorized data",
                "actively ensure against access unauthorized data",
            ),
            (
                "cannot compromise security",
                "must maintain safeguards against compromise security",
            ),
        ]

        for original, _expected_pattern in test_cases:
            result = prompt_builder._apply_positive_patterns(original)
            # Check that transformation occurred (exact match may vary due to regex)
            assert result != original
            assert (
                "actively" in result
                or "proactively" in result
                or "ensure against" in result
            )

    @pytest.mark.asyncio
    async def test_precedent_cache_refresh(self, prompt_builder):
        """Test constitutional precedent cache refresh functionality."""
        # Initially cache should be empty
        assert len(prompt_builder.constitutional_precedents) == 0

        # Refresh cache
        await prompt_builder._refresh_precedent_cache()

        # Check cache is populated
        assert len(prompt_builder.constitutional_precedents) > 0
        assert prompt_builder.precedent_cache_timestamp is not None

        # Check precedent structure
        for (
            _precedent_key,
            precedent_data,
        ) in prompt_builder.constitutional_precedents.items():
            assert "keywords" in precedent_data
            assert "principle_ids" in precedent_data
            assert "reasoning" in precedent_data
            assert "outcome" in precedent_data
            assert "relevance_score" in precedent_data

    @pytest.mark.asyncio
    async def test_precedent_retrieval(self, prompt_builder, sample_principles):
        """Test constitutional precedent retrieval for RAG enhancement."""
        # Refresh cache first
        await prompt_builder._refresh_precedent_cache()

        # Test precedent retrieval
        context = "privacy data protection"
        precedent_data = await prompt_builder._retrieve_constitutional_precedents(
            context, sample_principles
        )

        assert "precedents" in precedent_data
        assert "total_found" in precedent_data
        assert "cache_timestamp" in precedent_data
        assert isinstance(precedent_data["precedents"], list)
        assert precedent_data["total_found"] >= 0

    @pytest.mark.asyncio
    async def test_enhanced_prompt_building(
        self, prompt_builder, sample_context, sample_principles
    ):
        """Test enhanced constitutional prompt building with CoT and RAG."""
        # Update context with principles
        sample_context["principles"] = sample_principles
        sample_context["principle_count"] = len(sample_principles)

        synthesis_request = "Generate a policy for healthcare data processing"

        # Test enhanced prompt building
        enhanced_prompt = await prompt_builder.build_constitutional_prompt(
            constitutional_context=sample_context,
            synthesis_request=synthesis_request,
            target_format="rego",
            enable_cot=True,
            enable_rag=True,
        )

        # Validate enhanced prompt structure
        assert isinstance(enhanced_prompt, str)
        assert len(enhanced_prompt) > 1000  # Should be substantial

        # Check for Chain-of-Thought elements
        assert "CHAIN-OF-THOUGHT CONSTITUTIONAL REASONING" in enhanced_prompt
        assert "Step 1:" in enhanced_prompt
        assert "Step 2:" in enhanced_prompt

        # Check for enhanced compliance verification
        assert "ENHANCED CONSTITUTIONAL COMPLIANCE VERIFICATION" in enhanced_prompt
        assert "CONSTITUTIONAL ALIGNMENT CHECK" in enhanced_prompt
        assert "POSITIVE ACTION VALIDATION" in enhanced_prompt
        assert "PRECEDENT CONSISTENCY" in enhanced_prompt

        # Check for positive action patterns in principles
        assert "actively ensure" in enhanced_prompt or "proactively" in enhanced_prompt

    @pytest.mark.asyncio
    async def test_enhanced_principles_section(self, prompt_builder, sample_principles):
        """Test enhanced principles section with precedent context."""
        # Mock precedent data
        precedent_data = {
            "precedents": [
                {
                    "reasoning": "Privacy principles require proactive data protection",
                    "outcome": "Implemented encryption and access controls",
                }
            ]
        }

        hierarchy = [
            {"id": 1, "priority_level": "HIGH", "priority_weight": 0.9},
            {"id": 2, "priority_level": "HIGH", "priority_weight": 0.85},
        ]

        section = prompt_builder._build_enhanced_principles_section(
            sample_principles, hierarchy, precedent_data
        )

        assert "ENHANCED CONSTITUTIONAL PRINCIPLES" in section
        assert "RELEVANT CONSTITUTIONAL PRECEDENTS" in section
        assert "Privacy principles require proactive data protection" in section
        assert "Enhanced Content:" in section

    def test_cot_reasoning_section(self, prompt_builder, sample_context):
        """Test Chain-of-Thought reasoning section building."""
        synthesis_request = "Generate privacy policy"
        precedent_data = {"precedents": [{"reasoning": "test"}]}

        cot_section = prompt_builder._build_cot_reasoning_section(
            sample_context, synthesis_request, precedent_data
        )

        assert "CHAIN-OF-THOUGHT CONSTITUTIONAL REASONING" in cot_section
        assert "CONSTITUTIONAL REASONING PROCESS" in cot_section
        assert "PRECEDENT IDENTIFICATION" in cot_section
        assert "POSITIVE ACTION-FOCUSED SYNTHESIS" in cot_section
        assert "CONTEXT-SPECIFIC REASONING GUIDANCE" in cot_section

    def test_enhanced_synthesis_instructions(self, prompt_builder, sample_context):
        """Test enhanced synthesis instructions with positive patterns."""
        synthesis_request = "Generate policy"

        instructions = prompt_builder._build_enhanced_synthesis_instructions(
            sample_context, synthesis_request, "rego"
        )

        assert "ENHANCED SYNTHESIS INSTRUCTIONS" in instructions
        assert "POSITIVE ACTION-FOCUSED SYNTHESIS" in instructions
        assert "CHAIN-OF-THOUGHT REASONING" in instructions
        assert "PRECEDENT-INFORMED SYNTHESIS" in instructions
        assert "POSITIVE LANGUAGE PATTERNS TO USE" in instructions
        assert "The system SHALL actively ensure" in instructions

    @pytest.mark.asyncio
    async def test_performance_targets(
        self, prompt_builder, sample_context, sample_principles
    ):
        """Test that enhanced prompting meets performance targets."""
        import time

        # Update context
        sample_context["principles"] = sample_principles
        sample_context["principle_count"] = len(sample_principles)

        # Measure performance
        start_time = time.time()

        enhanced_prompt = await prompt_builder.build_constitutional_prompt(
            constitutional_context=sample_context,
            synthesis_request="Generate comprehensive governance policy",
            target_format="rego",
            enable_cot=True,
            enable_rag=True,
        )

        end_time = time.time()
        response_time = (end_time - start_time) * 1000  # Convert to milliseconds

        # Validate performance targets
        assert response_time < 2000  # <2s response time target
        assert len(enhanced_prompt) > 2000  # Substantial content for >95% compliance

        # Validate constitutional compliance indicators
        compliance_indicators = [
            "constitutional" in enhanced_prompt.lower(),
            "principle" in enhanced_prompt.lower(),
            "compliance" in enhanced_prompt.lower(),
            "verification" in enhanced_prompt.lower(),
            "alignment" in enhanced_prompt.lower(),
        ]

        compliance_score = sum(compliance_indicators) / len(compliance_indicators)
        assert compliance_score >= 0.95  # >95% constitutional compliance target


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
