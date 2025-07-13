"""
Constitutional Counterfactual Generator
Constitutional Hash: cdd01ef066bc6cf2

Advanced counterfactual generation service inspired by CARMA research for creating
robust constitutional compliance training data. Generates causal and neutral
augmentations to train constitutional validators resistant to reward hacking.
"""

import json
import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from .ai_model_service import AIModelService
from .blackboard import BlackboardService, KnowledgeItem
from .causal_constitutional_framework import (
    CausalAugmentationPair,
    ConstitutionalAttribute,
    ConstitutionalCounterfactual,
    NeutralAugmentationPair,
    SpuriousAttribute,
)

# Configure logging
logger = logging.getLogger(__name__)


class CounterfactualType(Enum):
    """Types of counterfactuals for constitutional training"""

    CAUSAL_UPGRADE = "causal_upgrade"
    CAUSAL_DEGRADE = "causal_degrade"
    NEUTRAL_SPURIOUS = "neutral_spurious"
    IRRELEVANT_QUERY = "irrelevant_query"
    CAUSALLY_ALIGNED = "causally_aligned"


class GenerationStrategy(Enum):
    """Strategies for counterfactual generation"""

    ATTRIBUTE_ISOLATION = "attribute_isolation"  # Focus on single attribute
    MINIMAL_EDIT = "minimal_edit"  # Minimal changes preserving context
    SYSTEMATIC_VARIATION = "systematic_variation"  # Systematic exploration
    ADVERSARIAL_PROBING = "adversarial_probing"  # Edge case testing


class CounterfactualGenerationResult(BaseModel):
    """Result of counterfactual generation process"""

    original_scenario: dict[str, Any]
    generated_counterfactuals: list[ConstitutionalCounterfactual]
    causal_augmentations: list[CausalAugmentationPair]
    neutral_augmentations: list[NeutralAugmentationPair]
    generation_statistics: dict[str, Any]
    constitutional_hash: str = "cdd01ef066bc6cf2"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ConstitutionalCounterfactualGenerator:
    """Advanced counterfactual generator for constitutional robustness training"""

    # Prompt templates for different types of interventions
    CAUSAL_INTERVENTION_PROMPTS = {
        ConstitutionalAttribute.SAFETY: {
            "upgrade": """
            Enhance the safety aspects of this constitutional scenario while keeping other factors constant:
            {scenario}

            Focus specifically on:
            - Risk mitigation and harm prevention
            - Safety protocol compliance
            - Protective measures for all stakeholders

            Maintain constitutional hash: cdd01ef066bc6cf2
            Preserve: formatting, length, style, technical complexity
            Change only: safety-related constitutional compliance
            """,
            "degrade": """
            Reduce the safety compliance in this constitutional scenario while preserving other aspects:
            {scenario}

            Focus specifically on:
            - Introducing safety risks or inadequate protections
            - Reducing harm prevention measures
            - Compromising safety protocols

            Maintain constitutional hash: cdd01ef066bc6cf2
            Preserve: formatting, length, style, technical complexity
            Change only: safety-related constitutional aspects
            """,
        },
        ConstitutionalAttribute.TRANSPARENCY: {
            "upgrade": """
            Improve transparency and explainability in this constitutional scenario:
            {scenario}

            Focus specifically on:
            - Clearer decision-making processes
            - Better explanation of reasoning
            - More accessible governance information

            Maintain constitutional hash: cdd01ef066bc6cf2
            Preserve: formatting, length, style, technical complexity
            Change only: transparency-related constitutional elements
            """,
            "degrade": """
            Reduce transparency while maintaining other constitutional aspects:
            {scenario}

            Focus specifically on:
            - Making decision processes less clear
            - Reducing explanation quality
            - Limiting access to governance information

            Maintain constitutional hash: cdd01ef066bc6cf2
            Preserve: formatting, length, style, technical complexity
            Change only: transparency-related constitutional elements
            """,
        },
        ConstitutionalAttribute.ACCOUNTABILITY: {
            "upgrade": """
            Strengthen accountability mechanisms in this constitutional scenario:
            {scenario}

            Focus specifically on:
            - Clear responsibility assignment
            - Robust audit trails
            - Effective oversight mechanisms

            Maintain constitutional hash: cdd01ef066bc6cf2
            Preserve: formatting, length, style, technical complexity
            Change only: accountability-related constitutional aspects
            """,
            "degrade": """
            Weaken accountability while preserving other constitutional factors:
            {scenario}

            Focus specifically on:
            - Unclear responsibility chains
            - Incomplete audit mechanisms
            - Reduced oversight effectiveness

            Maintain constitutional hash: cdd01ef066bc6cf2
            Preserve: formatting, length, style, technical complexity
            Change only: accountability-related constitutional aspects
            """,
        },
    }

    SPURIOUS_VARIATION_PROMPTS = {
        SpuriousAttribute.RESPONSE_LENGTH: """
        Create a variation of this constitutional scenario that changes the response length
        while preserving all constitutional content and meaning:
        {scenario}

        Variation type: {variation_type}
        - If expanding: Add relevant but non-essential details, examples, or elaboration
        - If condensing: Remove redundant content while keeping constitutional essence

        Maintain constitutional hash: cdd01ef066bc6cf2
        Preserve: all constitutional compliance aspects, meaning, decisions
        Change only: length and verbosity level
        """,
        SpuriousAttribute.FORMATTING_STYLE: """
        Reformat this constitutional scenario using a different style while preserving content:
        {scenario}

        Variation type: {variation_type}
        - Change formatting structure (bullet points ↔ paragraphs, headers, etc.)
        - Adjust presentation style (formal ↔ informal, technical ↔ plain language)

        Maintain constitutional hash: cdd01ef066bc6cf2
        Preserve: all constitutional content, compliance decisions, meaning
        Change only: formatting and presentation style
        """,
        SpuriousAttribute.TECHNICAL_JARGON: """
        Adjust the technical complexity of this constitutional scenario:
        {scenario}

        Variation type: {variation_type}
        - If simplifying: Use plain language while preserving constitutional precision
        - If technicalizing: Use more domain-specific terminology

        Maintain constitutional hash: cdd01ef066bc6cf2
        Preserve: constitutional compliance decisions, core meaning
        Change only: technical language complexity
        """,
    }

    def __init__(
        self, ai_model_service: AIModelService, blackboard_service: BlackboardService
    ):
        """Initialize constitutional counterfactual generator"""
        self.ai_model_service = ai_model_service
        self.blackboard = blackboard_service
        self.logger = logging.getLogger(__name__)

        # Generation statistics
        self.generation_stats = {
            "total_scenarios_processed": 0,
            "causal_augmentations_generated": 0,
            "neutral_augmentations_generated": 0,
            "generation_failures": 0,
            "quality_filter_rejections": 0,
        }

    async def generate_constitutional_training_data(
        self,
        original_scenarios: list[dict[str, Any]],
        causal_attributes: list[ConstitutionalAttribute] | None = None,
        spurious_attributes: list[SpuriousAttribute] | None = None,
        generation_strategy: GenerationStrategy = GenerationStrategy.ATTRIBUTE_ISOLATION,
        quality_threshold: float = 0.7,
    ) -> CounterfactualGenerationResult:
        """Generate comprehensive training data for constitutional robustness"""

        if causal_attributes is None:
            causal_attributes = [
                ConstitutionalAttribute.SAFETY,
                ConstitutionalAttribute.TRANSPARENCY,
                ConstitutionalAttribute.ACCOUNTABILITY,
                ConstitutionalAttribute.FAIRNESS,
                ConstitutionalAttribute.GOVERNANCE_COMPLIANCE,
            ]

        if spurious_attributes is None:
            spurious_attributes = [
                SpuriousAttribute.RESPONSE_LENGTH,
                SpuriousAttribute.FORMATTING_STYLE,
                SpuriousAttribute.TECHNICAL_JARGON,
                SpuriousAttribute.VERBOSITY_LEVEL,
            ]

        all_counterfactuals = []
        all_causal_augmentations = []
        all_neutral_augmentations = []

        for scenario in original_scenarios:
            # Generate causal augmentations
            causal_pairs = await self._generate_causal_augmentations(
                scenario, causal_attributes, generation_strategy
            )
            all_causal_augmentations.extend(causal_pairs)

            # Generate neutral augmentations
            neutral_pairs = await self._generate_neutral_augmentations(
                scenario, spurious_attributes, generation_strategy
            )
            all_neutral_augmentations.extend(neutral_pairs)

            # Create counterfactuals for evaluation
            scenario_counterfactuals = await self._create_counterfactuals(
                scenario, causal_pairs, neutral_pairs
            )
            all_counterfactuals.extend(scenario_counterfactuals)

            self.generation_stats["total_scenarios_processed"] += 1

        # Apply quality filtering
        filtered_causal = await self._apply_quality_filter(
            all_causal_augmentations, quality_threshold
        )
        filtered_neutral = await self._apply_quality_filter(
            all_neutral_augmentations, quality_threshold
        )

        # Log generation results
        await self._log_generation_results(
            len(original_scenarios), len(filtered_causal), len(filtered_neutral)
        )

        return CounterfactualGenerationResult(
            original_scenario={"batch_size": len(original_scenarios)},
            generated_counterfactuals=all_counterfactuals,
            causal_augmentations=filtered_causal,
            neutral_augmentations=filtered_neutral,
            generation_statistics=self.generation_stats.copy(),
        )

    async def _generate_causal_augmentations(
        self,
        scenario: dict[str, Any],
        causal_attributes: list[ConstitutionalAttribute],
        strategy: GenerationStrategy,
    ) -> list[CausalAugmentationPair]:
        """Generate causal augmentation pairs for constitutional attributes"""

        causal_pairs = []
        scenario_id = str(uuid4())

        for attribute in causal_attributes:
            # Generate upgrade intervention
            try:
                upgrade_scenario = await self._generate_causal_intervention(
                    scenario, attribute, "upgrade", strategy
                )

                upgrade_pair = CausalAugmentationPair(
                    scenario_id=f"{scenario_id}_{attribute.value}_upgrade",
                    original=scenario,
                    modified=upgrade_scenario,
                    causal_attribute=attribute,
                    intervention_type="upgrade",
                    preference_label="modified_preferred",
                )
                causal_pairs.append(upgrade_pair)
                self.generation_stats["causal_augmentations_generated"] += 1

            except Exception as e:
                self.logger.warning(
                    f"Failed to generate upgrade for {attribute.value}: {e}"
                )
                self.generation_stats["generation_failures"] += 1

            # Generate degrade intervention
            try:
                degrade_scenario = await self._generate_causal_intervention(
                    scenario, attribute, "degrade", strategy
                )

                degrade_pair = CausalAugmentationPair(
                    scenario_id=f"{scenario_id}_{attribute.value}_degrade",
                    original=scenario,
                    modified=degrade_scenario,
                    causal_attribute=attribute,
                    intervention_type="degrade",
                    preference_label="original_preferred",
                )
                causal_pairs.append(degrade_pair)
                self.generation_stats["causal_augmentations_generated"] += 1

            except Exception as e:
                self.logger.warning(
                    f"Failed to generate degrade for {attribute.value}: {e}"
                )
                self.generation_stats["generation_failures"] += 1

        return causal_pairs

    async def _generate_neutral_augmentations(
        self,
        scenario: dict[str, Any],
        spurious_attributes: list[SpuriousAttribute],
        strategy: GenerationStrategy,
    ) -> list[NeutralAugmentationPair]:
        """Generate neutral augmentation pairs for spurious invariance"""

        neutral_pairs = []
        scenario_id = str(uuid4())

        for spurious_attr in spurious_attributes:
            try:
                # Generate spurious variation
                variation_scenario = await self._generate_spurious_variation(
                    scenario, spurious_attr, strategy
                )

                neutral_pair = NeutralAugmentationPair(
                    scenario_id=f"{scenario_id}_{spurious_attr.value}_neutral",
                    variant_a=scenario,
                    variant_b=variation_scenario,
                    spurious_variation=spurious_attr,
                    causal_content_preserved=True,
                )
                neutral_pairs.append(neutral_pair)
                self.generation_stats["neutral_augmentations_generated"] += 1

            except Exception as e:
                self.logger.warning(
                    f"Failed to generate neutral variation for {spurious_attr.value}: {e}"
                )
                self.generation_stats["generation_failures"] += 1

        # Generate irrelevant query neutrals (CARMA methodology)
        try:
            irrelevant_scenario = await self._generate_irrelevant_query_neutral(
                scenario, strategy
            )

            irrelevant_pair = NeutralAugmentationPair(
                scenario_id=f"{scenario_id}_irrelevant_query",
                variant_a=scenario,
                variant_b=irrelevant_scenario,
                spurious_variation=SpuriousAttribute.FORMATTING_STYLE,
                causal_content_preserved=False,  # Query is changed
            )
            neutral_pairs.append(irrelevant_pair)
            self.generation_stats["neutral_augmentations_generated"] += 1

        except Exception as e:
            self.logger.warning(f"Failed to generate irrelevant query neutral: {e}")
            self.generation_stats["generation_failures"] += 1

        return neutral_pairs

    async def _generate_causal_intervention(
        self,
        scenario: dict[str, Any],
        attribute: ConstitutionalAttribute,
        intervention_type: str,
        strategy: GenerationStrategy,
    ) -> dict[str, Any]:
        """Generate causal intervention for specific constitutional attribute"""

        # Get appropriate prompt template
        prompt_template = self.CAUSAL_INTERVENTION_PROMPTS.get(attribute, {}).get(
            intervention_type
        )

        if not prompt_template:
            # Fallback generic prompt
            prompt_template = f"""
            {intervention_type.title()} the {attribute.value} aspect of this constitutional scenario:
            {{scenario}}

            Focus on {attribute.value} while preserving other constitutional aspects.
            Maintain constitutional hash: cdd01ef066bc6cf2
            """

        # Format prompt with scenario
        formatted_prompt = prompt_template.format(
            scenario=json.dumps(scenario, indent=2)
        )

        # Apply strategy-specific modifications
        if strategy == GenerationStrategy.MINIMAL_EDIT:
            formatted_prompt += "\nUse minimal edits - change only what's necessary for the intervention."
        elif strategy == GenerationStrategy.ADVERSARIAL_PROBING:
            formatted_prompt += (
                "\nCreate challenging edge cases that test constitutional boundaries."
            )

        # Generate intervention using AI model
        intervention_result = await self.ai_model_service.generate_response(
            formatted_prompt
        )

        # Parse and structure the result
        modified_scenario = scenario.copy()
        modified_scenario.update(
            {
                "causal_intervention": {
                    "attribute": attribute.value,
                    "type": intervention_type,
                    "generated_content": intervention_result,
                    "strategy": strategy.value,
                },
                "constitutional_hash": "cdd01ef066bc6cf2",
                "generation_timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

        return modified_scenario

    async def _generate_spurious_variation(
        self,
        scenario: dict[str, Any],
        spurious_attr: SpuriousAttribute,
        strategy: GenerationStrategy,
    ) -> dict[str, Any]:
        """Generate spurious variation preserving constitutional content"""

        # Determine variation type based on current scenario characteristics
        variation_type = self._determine_variation_type(scenario, spurious_attr)

        # Get appropriate prompt template
        prompt_template = self.SPURIOUS_VARIATION_PROMPTS.get(spurious_attr)

        if not prompt_template:
            # Fallback generic prompt
            prompt_template = f"""
            Create a variation of this constitutional scenario that changes {spurious_attr.value}
            while preserving all constitutional content:
            {{scenario}}

            Maintain constitutional hash: cdd01ef066bc6cf2
            Change only: {spurious_attr.value}
            Preserve: all constitutional decisions and compliance aspects
            """

        # Format prompt
        formatted_prompt = prompt_template.format(
            scenario=json.dumps(scenario, indent=2), variation_type=variation_type
        )

        # Generate variation
        variation_result = await self.ai_model_service.generate_response(
            formatted_prompt
        )

        # Create variation scenario
        variation_scenario = scenario.copy()
        variation_scenario.update(
            {
                "spurious_variation": {
                    "attribute": spurious_attr.value,
                    "variation_type": variation_type,
                    "generated_content": variation_result,
                    "strategy": strategy.value,
                },
                "constitutional_hash": "cdd01ef066bc6cf2",
                "causal_content_preserved": True,
                "generation_timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

        return variation_scenario

    async def _generate_irrelevant_query_neutral(
        self, scenario: dict[str, Any], strategy: GenerationStrategy
    ) -> dict[str, Any]:
        """Generate irrelevant query neutral following CARMA methodology"""

        irrelevant_prompt = f"""
        Create an irrelevant query version of this constitutional scenario by changing
        the context to something unrelated while maintaining the response structure:
        {json.dumps(scenario, indent=2)}

        Instructions:
        - Change the query/context to something constitutionally irrelevant
        - Keep the same response format and constitutional structure
        - Ensure both responses would receive the same constitutional compliance score
        - Maintain constitutional hash: cdd01ef066bc6cf2

        This creates a neutral pair for training spurious invariance.
        """

        irrelevant_result = await self.ai_model_service.generate_response(
            irrelevant_prompt
        )

        return {
            "irrelevant_query_neutral": True,
            "original_scenario_ref": scenario.get("scenario_id", "unknown"),
            "generated_content": irrelevant_result,
            "constitutional_hash": "cdd01ef066bc6cf2",
            "expected_compliance_equivalence": True,
            "generation_timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _determine_variation_type(
        self, scenario: dict[str, Any], spurious_attr: SpuriousAttribute
    ) -> str:
        """Determine appropriate variation type for spurious attribute"""

        scenario_str = str(scenario)

        if spurious_attr == SpuriousAttribute.RESPONSE_LENGTH:
            return "expand" if len(scenario_str) < 1000 else "condense"
        if spurious_attr == SpuriousAttribute.FORMATTING_STYLE:
            return "formal" if "informal" in scenario_str.lower() else "informal"
        if spurious_attr == SpuriousAttribute.TECHNICAL_JARGON:
            return "simplify" if "technical" in scenario_str.lower() else "technify"
        if spurious_attr == SpuriousAttribute.VERBOSITY_LEVEL:
            return "verbose" if len(scenario_str) < 500 else "concise"
        return "alternative"

    async def _create_counterfactuals(
        self,
        scenario: dict[str, Any],
        causal_pairs: list[CausalAugmentationPair],
        neutral_pairs: list[NeutralAugmentationPair],
    ) -> list[ConstitutionalCounterfactual]:
        """Create counterfactual objects from augmentation pairs"""

        counterfactuals = []

        # Convert causal pairs to counterfactuals
        for pair in causal_pairs:
            counterfactual = ConstitutionalCounterfactual(
                original_scenario=pair.original,
                intervention_type=f"causal_{pair.intervention_type}",
                target_attribute=pair.causal_attribute,
                modified_scenario=pair.modified,
                expected_outcome=(
                    "compliant" if pair.intervention_type == "upgrade" else "violation"
                ),
            )
            counterfactuals.append(counterfactual)

        # Convert neutral pairs to counterfactuals
        for pair in neutral_pairs:
            counterfactual = ConstitutionalCounterfactual(
                original_scenario=pair.variant_a,
                intervention_type="neutral_variation",
                target_attribute=pair.spurious_variation,
                modified_scenario=pair.variant_b,
                expected_outcome="equivalent",
            )
            counterfactuals.append(counterfactual)

        return counterfactuals

    async def _apply_quality_filter(
        self,
        augmentations: list[CausalAugmentationPair | NeutralAugmentationPair],
        quality_threshold: float,
    ) -> list[CausalAugmentationPair | NeutralAugmentationPair]:
        """Apply quality filtering to generated augmentations"""

        # Simplified quality filtering - in production, this would use more sophisticated metrics
        filtered = []

        for aug in augmentations:
            quality_score = self._calculate_quality_score(aug)

            if quality_score >= quality_threshold:
                filtered.append(aug)
            else:
                self.generation_stats["quality_filter_rejections"] += 1

        return filtered

    def _calculate_quality_score(
        self, augmentation: CausalAugmentationPair | NeutralAugmentationPair
    ) -> float:
        """Calculate quality score for generated augmentation"""

        # Simplified quality scoring - checks for basic requirements
        score = 0.0

        # Check constitutional hash preservation
        if hasattr(augmentation, "constitutional_hash"):
            if augmentation.constitutional_hash == "cdd01ef066bc6cf2":
                score += 0.3

        # Check content validity
        if isinstance(augmentation, CausalAugmentationPair):
            if augmentation.modified and augmentation.original:
                score += 0.4
            if augmentation.causal_attribute and augmentation.intervention_type:
                score += 0.3
        elif isinstance(augmentation, NeutralAugmentationPair):
            if augmentation.variant_a and augmentation.variant_b:
                score += 0.4
            if augmentation.causal_content_preserved:
                score += 0.3

        return min(1.0, score)

    async def _log_generation_results(
        self, original_count: int, causal_count: int, neutral_count: int
    ) -> None:
        """Log generation results to blackboard"""

        knowledge_item = KnowledgeItem(
            id=str(uuid4()),
            content={
                "type": "constitutional_counterfactual_generation",
                "original_scenarios": original_count,
                "causal_augmentations_generated": causal_count,
                "neutral_augmentations_generated": neutral_count,
                "generation_statistics": self.generation_stats,
                "constitutional_hash": "cdd01ef066bc6cf2",
            },
            metadata={
                "source": "constitutional_counterfactual_generator",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "generation_quality": (
                    "high"
                    if (causal_count + neutral_count) > original_count
                    else "medium"
                ),
            },
            tags=["constitutional", "counterfactual", "carma", "training_data"],
        )

        await self.blackboard.add_knowledge(knowledge_item)

    def get_generation_statistics(self) -> dict[str, Any]:
        """Get detailed generation statistics"""

        stats = self.generation_stats.copy()
        stats.update(
            {
                "constitutional_hash": "cdd01ef066bc6cf2",
                "generator_version": "1.0.0_carma_inspired",
                "success_rate": (
                    (
                        stats["causal_augmentations_generated"]
                        + stats["neutral_augmentations_generated"]
                    )
                    / max(
                        1, stats["total_scenarios_processed"] * 8
                    )  # Estimate expected generations
                ),
            }
        )

        return stats
