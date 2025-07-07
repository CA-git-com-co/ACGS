"""
Constitutional Augmentation Pipeline
Constitutional Hash: cdd01ef066bc6cf2

Comprehensive data augmentation pipeline for training constitutionally robust validators.
Implements CARMA-inspired methodology for generating causal and neutral augmentations
to mitigate constitutional reward hacking.
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from uuid import uuid4

from pydantic import BaseModel, Field

from .ai_model_service import AIModelService
from .blackboard import BlackboardService, KnowledgeItem
from .causal_constitutional_framework import (
    CausalConstitutionalFramework,
    ConstitutionalAttribute,
    SpuriousAttribute,
)
from .constitutional_counterfactual_generator import (
    CausalAugmentationPair,
    ConstitutionalCounterfactualGenerator,
    GenerationStrategy,
    NeutralAugmentationPair,
)
from .constitutional_safety_framework import ConstitutionalSafetyValidator

# Configure logging
logger = logging.getLogger(__name__)


class TrainingDataType(Enum):
    """Types of training data in the augmentation pipeline"""

    ORIGINAL_PREFERENCE = "original_preference"
    CAUSAL_AUGMENTATION = "causal_augmentation"
    NEUTRAL_AUGMENTATION = "neutral_augmentation"
    FILTERED_AUGMENTATION = "filtered_augmentation"


class AugmentationConfig(BaseModel):
    """Configuration for augmentation pipeline"""

    constitutional_hash: str = "cdd01ef066bc6cf2"

    # Causal augmentation settings
    causal_attributes: List[ConstitutionalAttribute] = Field(
        default_factory=lambda: [
            ConstitutionalAttribute.SAFETY,
            ConstitutionalAttribute.TRANSPARENCY,
            ConstitutionalAttribute.ACCOUNTABILITY,
            ConstitutionalAttribute.FAIRNESS,
            ConstitutionalAttribute.GOVERNANCE_COMPLIANCE,
        ]
    )

    # Spurious invariance settings
    spurious_attributes: List[SpuriousAttribute] = Field(
        default_factory=lambda: [
            SpuriousAttribute.RESPONSE_LENGTH,
            SpuriousAttribute.FORMATTING_STYLE,
            SpuriousAttribute.TECHNICAL_JARGON,
            SpuriousAttribute.VERBOSITY_LEVEL,
        ]
    )

    # Pipeline settings
    generation_strategy: GenerationStrategy = GenerationStrategy.ATTRIBUTE_ISOLATION
    quality_threshold: float = 0.7
    filtering_enabled: bool = True
    augmentation_ratio: float = 2.0  # ratio of augmented to original data

    # Loss function weights (following CARMA methodology)
    preference_loss_weight: float = 1.0
    neutral_tie_loss_weight: float = 1.0  # lambda in CARMA paper


@dataclass
class ConstitutionalTrainingExample:
    """Single training example for constitutional robustness"""

    example_id: str
    data_type: TrainingDataType
    scenario: Dict[str, Any]
    comparison_scenario: Optional[Dict[str, Any]] = None
    preference_label: str = "equivalent"  # "preferred", "dispreferred", "equivalent"
    constitutional_attributes: List[str] = field(default_factory=list)
    spurious_attributes: List[str] = field(default_factory=list)
    constitutional_hash: str = "cdd01ef066bc6cf2"
    metadata: Dict[str, Any] = field(default_factory=dict)


class ConstitutionalTrainingDataset(BaseModel):
    """Complete dataset for constitutional robustness training"""

    dataset_id: str
    constitutional_hash: str = "cdd01ef066bc6cf2"

    # Data splits
    original_examples: List[ConstitutionalTrainingExample] = Field(default_factory=list)
    causal_examples: List[ConstitutionalTrainingExample] = Field(default_factory=list)
    neutral_examples: List[ConstitutionalTrainingExample] = Field(default_factory=list)

    # Dataset statistics
    dataset_statistics: Dict[str, Any] = Field(default_factory=dict)
    augmentation_config: AugmentationConfig
    creation_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class ConstitutionalAugmentationPipeline:
    """Complete pipeline for generating constitutional robustness training data"""

    def __init__(
        self,
        constitutional_validator: ConstitutionalSafetyValidator,
        ai_model_service: AIModelService,
        blackboard_service: BlackboardService,
        config: Optional[AugmentationConfig] = None,
    ):
        """Initialize constitutional augmentation pipeline"""
        self.constitutional_validator = constitutional_validator
        self.ai_model_service = ai_model_service
        self.blackboard = blackboard_service
        self.config = config or AugmentationConfig()
        self.logger = logging.getLogger(__name__)

        # Initialize sub-components
        self.causal_framework = CausalConstitutionalFramework(
            constitutional_validator, blackboard_service, ai_model_service
        )
        self.counterfactual_generator = ConstitutionalCounterfactualGenerator(
            ai_model_service, blackboard_service
        )

        # Pipeline statistics
        self.pipeline_stats = {
            "datasets_created": 0,
            "examples_processed": 0,
            "augmentations_generated": 0,
            "filtering_rejections": 0,
            "constitutional_validations": 0,
        }

    async def create_constitutional_training_dataset(
        self,
        original_preference_data: List[Dict[str, Any]],
        dataset_name: str = "constitutional_robustness_dataset",
    ) -> ConstitutionalTrainingDataset:
        """Create complete training dataset with causal and neutral augmentations"""

        dataset_id = f"{dataset_name}_{uuid4()}"
        self.logger.info(f"Creating constitutional training dataset: {dataset_id}")

        # Step 1: Process original preference data
        original_examples = await self._process_original_data(original_preference_data)

        # Step 2: Generate causal augmentations
        causal_examples = await self._generate_causal_training_examples(
            original_preference_data
        )

        # Step 3: Generate neutral augmentations
        neutral_examples = await self._generate_neutral_training_examples(
            original_preference_data, causal_examples
        )

        # Step 4: Apply quality filtering if enabled
        if self.config.filtering_enabled:
            causal_examples = await self._apply_quality_filtering(causal_examples)
            neutral_examples = await self._apply_quality_filtering(neutral_examples)

        # Step 5: Calculate dataset statistics
        dataset_statistics = self._calculate_dataset_statistics(
            original_examples, causal_examples, neutral_examples
        )

        # Step 6: Create final dataset
        dataset = ConstitutionalTrainingDataset(
            dataset_id=dataset_id,
            original_examples=original_examples,
            causal_examples=causal_examples,
            neutral_examples=neutral_examples,
            dataset_statistics=dataset_statistics,
            augmentation_config=self.config,
        )

        # Step 7: Log dataset creation
        await self._log_dataset_creation(dataset)

        self.pipeline_stats["datasets_created"] += 1

        return dataset

    async def _process_original_data(
        self, original_data: List[Dict[str, Any]]
    ) -> List[ConstitutionalTrainingExample]:
        """Process original preference data into training examples"""

        original_examples = []

        for i, data_point in enumerate(original_data):
            example = ConstitutionalTrainingExample(
                example_id=f"original_{i}_{uuid4()}",
                data_type=TrainingDataType.ORIGINAL_PREFERENCE,
                scenario=data_point,
                preference_label="preferred",  # Original data is considered preferred
                metadata={
                    "source": "original_preference_data",
                    "index": i,
                    "constitutional_validation_required": True,
                },
            )
            original_examples.append(example)
            self.pipeline_stats["examples_processed"] += 1

        return original_examples

    async def _generate_causal_training_examples(
        self, original_data: List[Dict[str, Any]]
    ) -> List[ConstitutionalTrainingExample]:
        """Generate causal augmentation training examples"""

        causal_examples = []

        # Generate causal augmentations using counterfactual generator
        generation_result = (
            await self.counterfactual_generator.generate_constitutional_training_data(
                original_scenarios=original_data,
                causal_attributes=self.config.causal_attributes,
                spurious_attributes=[],  # Only causal for this step
                generation_strategy=self.config.generation_strategy,
                quality_threshold=self.config.quality_threshold,
            )
        )

        # Convert causal augmentation pairs to training examples
        for causal_pair in generation_result.causal_augmentations:
            # Create preference pair example
            example = ConstitutionalTrainingExample(
                example_id=f"causal_{causal_pair.scenario_id}",
                data_type=TrainingDataType.CAUSAL_AUGMENTATION,
                scenario=causal_pair.original,
                comparison_scenario=causal_pair.modified,
                preference_label=causal_pair.preference_label,
                constitutional_attributes=[causal_pair.causal_attribute.value],
                metadata={
                    "causal_attribute": causal_pair.causal_attribute.value,
                    "intervention_type": causal_pair.intervention_type,
                    "constitutional_focus": True,
                },
            )
            causal_examples.append(example)
            self.pipeline_stats["augmentations_generated"] += 1

        return causal_examples

    async def _generate_neutral_training_examples(
        self,
        original_data: List[Dict[str, Any]],
        causal_examples: List[ConstitutionalTrainingExample],
    ) -> List[ConstitutionalTrainingExample]:
        """Generate neutral augmentation training examples for spurious invariance"""

        neutral_examples = []

        # Generate neutral augmentations from original data
        original_neutral_result = (
            await self.counterfactual_generator.generate_constitutional_training_data(
                original_scenarios=original_data,
                causal_attributes=[],  # No causal for neutrals
                spurious_attributes=self.config.spurious_attributes,
                generation_strategy=self.config.generation_strategy,
                quality_threshold=self.config.quality_threshold,
            )
        )

        # Convert neutral pairs to training examples with tie labels
        for neutral_pair in original_neutral_result.neutral_augmentations:
            example = ConstitutionalTrainingExample(
                example_id=f"neutral_{neutral_pair.scenario_id}",
                data_type=TrainingDataType.NEUTRAL_AUGMENTATION,
                scenario=neutral_pair.variant_a,
                comparison_scenario=neutral_pair.variant_b,
                preference_label="equivalent",  # Tie label for neutrals
                spurious_attributes=[neutral_pair.spurious_variation.value],
                metadata={
                    "spurious_variation": neutral_pair.spurious_variation.value,
                    "causal_content_preserved": neutral_pair.causal_content_preserved,
                    "tie_label": True,
                    "invariance_target": True,
                },
            )
            neutral_examples.append(example)
            self.pipeline_stats["augmentations_generated"] += 1

        # Generate neutrals from causal augmentations (following CARMA methodology)
        causal_scenarios = [
            ex.scenario for ex in causal_examples if ex.comparison_scenario
        ]

        if causal_scenarios:
            causal_neutral_result = await self.counterfactual_generator.generate_constitutional_training_data(
                original_scenarios=causal_scenarios,
                causal_attributes=[],
                spurious_attributes=self.config.spurious_attributes,
                generation_strategy=self.config.generation_strategy,
                quality_threshold=self.config.quality_threshold,
            )

            # Convert causal-based neutrals
            for neutral_pair in causal_neutral_result.neutral_augmentations:
                example = ConstitutionalTrainingExample(
                    example_id=f"causal_neutral_{neutral_pair.scenario_id}",
                    data_type=TrainingDataType.NEUTRAL_AUGMENTATION,
                    scenario=neutral_pair.variant_a,
                    comparison_scenario=neutral_pair.variant_b,
                    preference_label="equivalent",
                    spurious_attributes=[neutral_pair.spurious_variation.value],
                    metadata={
                        "source": "causal_augmentation_derived",
                        "spurious_variation": neutral_pair.spurious_variation.value,
                        "causal_content_preserved": neutral_pair.causal_content_preserved,
                        "tie_label": True,
                    },
                )
                neutral_examples.append(example)
                self.pipeline_stats["augmentations_generated"] += 1

        return neutral_examples

    async def _apply_quality_filtering(
        self, examples: List[ConstitutionalTrainingExample]
    ) -> List[ConstitutionalTrainingExample]:
        """Apply quality filtering using baseline constitutional validator"""

        filtered_examples = []

        for example in examples:
            # Validate example quality
            quality_score = await self._calculate_example_quality(example)

            if quality_score >= self.config.quality_threshold:
                example.metadata["quality_score"] = quality_score
                example.data_type = TrainingDataType.FILTERED_AUGMENTATION
                filtered_examples.append(example)
            else:
                self.pipeline_stats["filtering_rejections"] += 1

        self.logger.info(
            f"Quality filtering: {len(examples)} -> {len(filtered_examples)} "
            f"({len(examples) - len(filtered_examples)} rejected)"
        )

        return filtered_examples

    async def _calculate_example_quality(
        self, example: ConstitutionalTrainingExample
    ) -> float:
        """Calculate quality score for training example"""

        quality_components = []

        # 1. Constitutional hash validation
        if example.constitutional_hash == "cdd01ef066bc6cf2":
            quality_components.append(0.2)

        # 2. Scenario validity
        if example.scenario and isinstance(example.scenario, dict):
            quality_components.append(0.2)

        # 3. Constitutional validation consistency
        if example.data_type == TrainingDataType.CAUSAL_AUGMENTATION:
            # For causal examples, validate constitutional responsiveness
            original_validation = await self.constitutional_validator.validate_request(
                request_data=example.scenario, context={"source": "quality_assessment"}
            )

            if example.comparison_scenario:
                modified_validation = (
                    await self.constitutional_validator.validate_request(
                        request_data=example.comparison_scenario,
                        context={"source": "quality_assessment"},
                    )
                )

                # Check if validation appropriately responds to causal changes
                original_approved = original_validation.get("approved", False)
                modified_approved = modified_validation.get("approved", False)

                if example.preference_label == "modified_preferred":
                    # Modified should be better
                    if modified_approved and not original_approved:
                        quality_components.append(0.4)
                    elif modified_approved == original_approved:
                        quality_components.append(0.2)
                elif example.preference_label == "original_preferred":
                    # Original should be better
                    if original_approved and not modified_approved:
                        quality_components.append(0.4)
                    elif modified_approved == original_approved:
                        quality_components.append(0.2)

            self.pipeline_stats["constitutional_validations"] += 2

        elif example.data_type == TrainingDataType.NEUTRAL_AUGMENTATION:
            # For neutral examples, validate equivalence
            if example.comparison_scenario:
                original_validation = (
                    await self.constitutional_validator.validate_request(
                        request_data=example.scenario,
                        context={"source": "quality_assessment"},
                    )
                )
                variant_validation = (
                    await self.constitutional_validator.validate_request(
                        request_data=example.comparison_scenario,
                        context={"source": "quality_assessment"},
                    )
                )

                # Should have equivalent constitutional compliance
                if original_validation.get("approved") == variant_validation.get(
                    "approved"
                ):
                    quality_components.append(0.4)
                else:
                    quality_components.append(0.1)  # Poor neutrality

                self.pipeline_stats["constitutional_validations"] += 2

        # 4. Metadata completeness
        if example.metadata and len(example.metadata) > 0:
            quality_components.append(0.2)

        return sum(quality_components)

    def _calculate_dataset_statistics(
        self,
        original_examples: List[ConstitutionalTrainingExample],
        causal_examples: List[ConstitutionalTrainingExample],
        neutral_examples: List[ConstitutionalTrainingExample],
    ) -> Dict[str, Any]:
        """Calculate comprehensive dataset statistics"""

        total_examples = (
            len(original_examples) + len(causal_examples) + len(neutral_examples)
        )

        # Attribute distribution analysis
        causal_attr_distribution = {}
        for attr in self.config.causal_attributes:
            count = sum(
                1
                for ex in causal_examples
                if attr.value in ex.constitutional_attributes
            )
            causal_attr_distribution[attr.value] = count

        spurious_attr_distribution = {}
        for attr in self.config.spurious_attributes:
            count = sum(
                1 for ex in neutral_examples if attr.value in ex.spurious_attributes
            )
            spurious_attr_distribution[attr.value] = count

        statistics = {
            "constitutional_hash": "cdd01ef066bc6cf2",
            "total_examples": total_examples,
            "original_examples": len(original_examples),
            "causal_examples": len(causal_examples),
            "neutral_examples": len(neutral_examples),
            "augmentation_ratio": (len(causal_examples) + len(neutral_examples))
            / max(1, len(original_examples)),
            "causal_attribute_distribution": causal_attr_distribution,
            "spurious_attribute_distribution": spurious_attr_distribution,
            "preference_label_distribution": {
                "preferred": len(
                    [
                        ex
                        for ex in causal_examples
                        if ex.preference_label == "modified_preferred"
                    ]
                ),
                "dispreferred": len(
                    [
                        ex
                        for ex in causal_examples
                        if ex.preference_label == "original_preferred"
                    ]
                ),
                "equivalent": len(neutral_examples),
            },
            "quality_metrics": {
                "filtering_enabled": self.config.filtering_enabled,
                "quality_threshold": self.config.quality_threshold,
                "rejection_rate": self.pipeline_stats.get("filtering_rejections", 0)
                / max(1, total_examples),
            },
        }

        return statistics

    async def create_loss_function_data(
        self, dataset: ConstitutionalTrainingDataset
    ) -> Dict[str, Any]:
        """Create data structure optimized for CARMA-style loss function training"""

        # Separate data for different loss components following CARMA methodology
        preference_data = []  # For preference loss (causal sensitivity)
        neutral_data = []  # For neutral tie loss (spurious invariance)

        # Process original and causal examples for preference loss
        for example in dataset.original_examples + dataset.causal_examples:
            if example.comparison_scenario:
                preference_data.append(
                    {
                        "query": example.scenario,
                        "preferred_response": (
                            example.comparison_scenario
                            if example.preference_label == "modified_preferred"
                            else example.scenario
                        ),
                        "dispreferred_response": (
                            example.scenario
                            if example.preference_label == "modified_preferred"
                            else example.comparison_scenario
                        ),
                        "constitutional_attributes": example.constitutional_attributes,
                        "constitutional_hash": "cdd01ef066bc6cf2",
                    }
                )

        # Process neutral examples for tie loss
        for example in dataset.neutral_examples:
            if example.comparison_scenario:
                neutral_data.append(
                    {
                        "query": example.scenario,
                        "response_a": example.scenario,
                        "response_b": example.comparison_scenario,
                        "tie_label": True,
                        "spurious_attributes": example.spurious_attributes,
                        "constitutional_hash": "cdd01ef066bc6cf2",
                    }
                )

        loss_data = {
            "preference_loss_data": preference_data,
            "neutral_tie_loss_data": neutral_data,
            "loss_weights": {
                "preference_weight": self.config.preference_loss_weight,
                "neutral_tie_weight": self.config.neutral_tie_loss_weight,
            },
            "dataset_id": dataset.dataset_id,
            "constitutional_hash": "cdd01ef066bc6cf2",
            "carma_methodology": True,
        }

        return loss_data

    async def _log_dataset_creation(
        self, dataset: ConstitutionalTrainingDataset
    ) -> None:
        """Log dataset creation to blackboard"""

        knowledge_item = KnowledgeItem(
            id=str(uuid4()),
            content={
                "type": "constitutional_training_dataset_created",
                "dataset_id": dataset.dataset_id,
                "dataset_statistics": dataset.dataset_statistics,
                "augmentation_config": dataset.augmentation_config.dict(),
                "pipeline_statistics": self.pipeline_stats,
                "constitutional_hash": "cdd01ef066bc6cf2",
            },
            metadata={
                "source": "constitutional_augmentation_pipeline",
                "timestamp": dataset.creation_timestamp.isoformat(),
                "dataset_quality": (
                    "high"
                    if dataset.dataset_statistics.get("total_examples", 0) > 100
                    else "medium"
                ),
            },
            tags=[
                "constitutional",
                "training_data",
                "carma",
                "augmentation",
                "dataset",
            ],
        )

        await self.blackboard.add_knowledge(knowledge_item)

    def get_pipeline_statistics(self) -> Dict[str, Any]:
        """Get comprehensive pipeline statistics"""

        stats = self.pipeline_stats.copy()
        stats.update(
            {
                "constitutional_hash": "cdd01ef066bc6cf2",
                "pipeline_version": "1.0.0_carma_inspired",
                "config": self.config.dict(),
                "augmentation_efficiency": (
                    stats.get("augmentations_generated", 0)
                    / max(1, stats.get("examples_processed", 1))
                ),
            }
        )

        return stats
