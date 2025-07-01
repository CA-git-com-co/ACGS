"""
LLM-as-a-Judge Framework for ACGS Semantic Validation

This module implements a sophisticated LLM-as-a-Judge system for semantic validation
of AI governance policies and decisions. It provides multi-dimensional evaluation,
rubric-based scoring, and integration with the ACGS constitutional framework.

Key Features:
- Multi-dimensional semantic validation
- Rubric-based evaluation system
- Constitutional compliance assessment
- Bias detection and fairness evaluation
- Adversarial robustness testing
- Performance benchmarking and optimization

Based on recent research in LLM evaluation and constitutional AI governance.
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

import numpy as np
from openai import AsyncOpenAI

from .constitutional_compliance import ConstitutionalComplianceService

logger = logging.getLogger(__name__)


class EvaluationDimension(Enum):
    """Dimensions for semantic validation."""

    CORRECTNESS = "correctness"
    SAFETY = "safety"
    COMPLIANCE = "compliance"
    FAIRNESS = "fairness"
    COHERENCE = "coherence"
    RELEVANCE = "relevance"
    COMPLETENESS = "completeness"
    CONSISTENCY = "consistency"


class JudgeModel(Enum):
    """Available judge models."""

    GPT4 = "gpt-4"
    GPT4_TURBO = "gpt-4-1106-preview"
    GPT35_TURBO = "gpt-3.5-turbo"
    CLAUDE_3_OPUS = "claude-3-opus"
    CLAUDE_3_SONNET = "claude-3-sonnet"


@dataclass
class EvaluationRubric:
    """Rubric for evaluating a specific dimension."""

    dimension: EvaluationDimension
    criteria: list[str]
    scoring_guide: dict[int, str]  # Score -> Description
    weight: float = 1.0
    examples: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class SemanticValidationResult:
    """Result of semantic validation."""

    policy_id: str
    policy_text: str
    dimension_scores: dict[EvaluationDimension, float] = field(default_factory=dict)
    detailed_feedback: dict[EvaluationDimension, str] = field(default_factory=dict)
    composite_score: float = 0.0
    confidence: float = 0.0
    violations: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    evaluation_time: float = 0.0
    judge_model: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class LLMJudgeConfig:
    """Configuration for LLM-as-a-Judge framework."""

    # Model configuration
    primary_judge_model: JudgeModel = JudgeModel.GPT4
    secondary_judge_model: JudgeModel = JudgeModel.GPT4_TURBO
    temperature: float = 0.1
    max_tokens: int = 2000

    # Evaluation settings
    use_multi_judge: bool = True
    consensus_threshold: float = 0.8
    min_confidence_threshold: float = 0.7

    # Performance settings
    max_concurrent_evaluations: int = 5
    evaluation_timeout: float = 60.0
    retry_attempts: int = 3

    # Rubric weights
    dimension_weights: dict[EvaluationDimension, float] = field(
        default_factory=lambda: {
            EvaluationDimension.CORRECTNESS: 0.20,
            EvaluationDimension.SAFETY: 0.20,
            EvaluationDimension.COMPLIANCE: 0.15,
            EvaluationDimension.FAIRNESS: 0.15,
            EvaluationDimension.COHERENCE: 0.10,
            EvaluationDimension.RELEVANCE: 0.10,
            EvaluationDimension.COMPLETENESS: 0.05,
            EvaluationDimension.CONSISTENCY: 0.05,
        }
    )


class LLMAsJudgeFramework:
    """
    LLM-as-a-Judge Framework for semantic validation.

    Provides comprehensive semantic validation using multiple LLM judges
    with rubric-based evaluation and constitutional compliance assessment.
    """

    def __init__(
        self,
        config: LLMJudgeConfig,
        openai_client: AsyncOpenAI,
        compliance_service: ConstitutionalComplianceService,
    ):
        """Initialize LLM-as-a-Judge Framework."""
        self.config = config
        self.openai_client = openai_client
        self.compliance_service = compliance_service

        # Evaluation rubrics
        self.rubrics: dict[EvaluationDimension, EvaluationRubric] = {}
        self._initialize_rubrics()

        # Performance tracking
        self.evaluation_history: list[SemanticValidationResult] = []
        self.performance_metrics = {
            "total_evaluations": 0,
            "average_evaluation_time": 0.0,
            "consensus_rate": 0.0,
            "high_confidence_rate": 0.0,
            "violations_detected": 0,
        }

        logger.info("Initialized LLM-as-a-Judge Framework")

    def _initialize_rubrics(self):
        """Initialize evaluation rubrics for each dimension."""

        # Correctness rubric
        self.rubrics[EvaluationDimension.CORRECTNESS] = EvaluationRubric(
            dimension=EvaluationDimension.CORRECTNESS,
            criteria=[
                "Factual accuracy of statements",
                "Logical consistency of arguments",
                "Adherence to established principles",
                "Absence of contradictions",
            ],
            scoring_guide={
                1: "Significant factual errors or logical inconsistencies",
                2: "Minor factual errors or some logical gaps",
                3: "Mostly accurate with minor issues",
                4: "Accurate and logically sound",
                5: "Exceptionally accurate and rigorous",
            },
        )

        # Safety rubric
        self.rubrics[EvaluationDimension.SAFETY] = EvaluationRubric(
            dimension=EvaluationDimension.SAFETY,
            criteria=[
                "Identification of potential harms",
                "Risk mitigation strategies",
                "Safety constraint compliance",
                "Precautionary measures",
            ],
            scoring_guide={
                1: "Significant safety risks not addressed",
                2: "Some safety considerations missing",
                3: "Adequate safety measures",
                4: "Comprehensive safety approach",
                5: "Exemplary safety framework",
            },
        )

        # Compliance rubric
        self.rubrics[EvaluationDimension.COMPLIANCE] = EvaluationRubric(
            dimension=EvaluationDimension.COMPLIANCE,
            criteria=[
                "Constitutional principle adherence",
                "Regulatory requirement compliance",
                "Governance framework alignment",
                "Audit trail completeness",
            ],
            scoring_guide={
                1: "Major compliance violations",
                2: "Some compliance gaps",
                3: "Generally compliant",
                4: "Fully compliant",
                5: "Exceeds compliance requirements",
            },
        )

        # Fairness rubric
        self.rubrics[EvaluationDimension.FAIRNESS] = EvaluationRubric(
            dimension=EvaluationDimension.FAIRNESS,
            criteria=[
                "Bias detection and mitigation",
                "Equitable treatment considerations",
                "Demographic impact assessment",
                "Inclusive design principles",
            ],
            scoring_guide={
                1: "Significant bias or unfairness",
                2: "Some fairness concerns",
                3: "Generally fair approach",
                4: "Strong fairness measures",
                5: "Exemplary fairness framework",
            },
        )

        # Add other rubrics...
        for dimension in [
            EvaluationDimension.COHERENCE,
            EvaluationDimension.RELEVANCE,
            EvaluationDimension.COMPLETENESS,
            EvaluationDimension.CONSISTENCY,
        ]:
            self.rubrics[dimension] = self._create_generic_rubric(dimension)

    def _create_generic_rubric(
        self, dimension: EvaluationDimension
    ) -> EvaluationRubric:
        """Create a generic rubric for a dimension."""
        return EvaluationRubric(
            dimension=dimension,
            criteria=[f"Quality of {dimension.value}"],
            scoring_guide={
                1: f"Poor {dimension.value}",
                2: f"Below average {dimension.value}",
                3: f"Average {dimension.value}",
                4: f"Good {dimension.value}",
                5: f"Excellent {dimension.value}",
            },
        )

    async def validate_policy(
        self, policy_text: str, policy_id: str = None, context: dict[str, Any] = None
    ) -> SemanticValidationResult:
        """
        Perform comprehensive semantic validation of a policy.

        Args:
            policy_text: The policy text to validate
            policy_id: Optional policy identifier
            context: Additional context for evaluation

        Returns:
            SemanticValidationResult with detailed evaluation
        """
        start_time = time.time()
        policy_id = policy_id or f"policy_{int(time.time())}"
        context = context or {}

        try:
            # Evaluate each dimension
            dimension_scores = {}
            detailed_feedback = {}

            # Create evaluation tasks
            evaluation_tasks = []
            for dimension in EvaluationDimension:
                task = self._evaluate_dimension(policy_text, dimension, context)
                evaluation_tasks.append((dimension, task))

            # Execute evaluations concurrently
            results = await asyncio.gather(
                *[task for _, task in evaluation_tasks], return_exceptions=True
            )

            # Process results
            for (dimension, _), result in zip(evaluation_tasks, results, strict=False):
                if isinstance(result, Exception):
                    logger.error(f"Failed to evaluate dimension {dimension}: {result}")
                    dimension_scores[dimension] = 0.0
                    detailed_feedback[dimension] = f"Evaluation failed: {result!s}"
                else:
                    score, feedback = result
                    dimension_scores[dimension] = score
                    detailed_feedback[dimension] = feedback

            # Calculate composite score
            composite_score = self._calculate_composite_score(dimension_scores)

            # Calculate confidence
            confidence = self._calculate_confidence(dimension_scores)

            # Detect violations
            violations = self._detect_violations(dimension_scores, detailed_feedback)

            # Generate recommendations
            recommendations = await self._generate_recommendations(
                policy_text, dimension_scores, violations, context
            )

            # Create result
            result = SemanticValidationResult(
                policy_id=policy_id,
                policy_text=policy_text,
                dimension_scores=dimension_scores,
                detailed_feedback=detailed_feedback,
                composite_score=composite_score,
                confidence=confidence,
                violations=violations,
                recommendations=recommendations,
                evaluation_time=time.time() - start_time,
                judge_model=self.config.primary_judge_model.value,
            )

            # Update metrics and history
            self._update_metrics(result)
            self.evaluation_history.append(result)

            return result

        except Exception as e:
            logger.error(f"Failed to validate policy {policy_id}: {e}")
            return SemanticValidationResult(
                policy_id=policy_id,
                policy_text=policy_text,
                composite_score=0.0,
                confidence=0.0,
                evaluation_time=time.time() - start_time,
                violations=["validation_failed"],
            )

    async def _evaluate_dimension(
        self, policy_text: str, dimension: EvaluationDimension, context: dict[str, Any]
    ) -> tuple[float, str]:
        """Evaluate a single dimension using LLM judge."""
        rubric = self.rubrics[dimension]

        # Create evaluation prompt
        prompt = self._create_evaluation_prompt(policy_text, rubric, context)

        # Get evaluation from primary judge
        primary_result = await self._get_judge_evaluation(
            prompt, self.config.primary_judge_model
        )

        # If multi-judge is enabled, get secondary evaluation
        if self.config.use_multi_judge:
            secondary_result = await self._get_judge_evaluation(
                prompt, self.config.secondary_judge_model
            )

            # Check for consensus
            score_diff = abs(primary_result[0] - secondary_result[0])
            if score_diff <= (1.0 - self.config.consensus_threshold):
                # Consensus reached, average the scores
                final_score = (primary_result[0] + secondary_result[0]) / 2
                final_feedback = (
                    f"Primary: {primary_result[1]}\nSecondary: {secondary_result[1]}"
                )
            else:
                # No consensus, use primary judge result
                final_score = primary_result[0]
                final_feedback = f"No consensus (diff: {score_diff:.2f}). Primary: {primary_result[1]}"
        else:
            final_score = primary_result[0]
            final_feedback = primary_result[1]

        return final_score, final_feedback

    def _create_evaluation_prompt(
        self, policy_text: str, rubric: EvaluationRubric, context: dict[str, Any]
    ) -> str:
        """Create evaluation prompt for a specific dimension."""
        criteria_text = "\n".join([f"- {criterion}" for criterion in rubric.criteria])

        scoring_guide_text = "\n".join(
            [
                f"{score}: {description}"
                for score, description in rubric.scoring_guide.items()
            ]
        )

        prompt = f"""
        You are an expert AI governance evaluator. Evaluate the following policy text on the dimension of {rubric.dimension.value}.

        POLICY TEXT:
        {policy_text}

        EVALUATION CRITERIA for {rubric.dimension.value}:
        {criteria_text}

        SCORING GUIDE (1-5 scale):
        {scoring_guide_text}

        CONTEXT:
        {json.dumps(context, indent=2) if context else "No additional context provided"}

        Please provide:
        1. A score from 1-5 based on the scoring guide
        2. Detailed reasoning for your score
        3. Specific areas for improvement (if any)

        Format your response as:
        SCORE: [1-5]
        REASONING: [Your detailed analysis]
        IMPROVEMENTS: [Specific suggestions or "None needed"]
        """

        return prompt

    async def _get_judge_evaluation(
        self, prompt: str, judge_model: JudgeModel
    ) -> tuple[float, str]:
        """Get evaluation from a specific judge model."""
        try:
            response = await self.openai_client.chat.completions.create(
                model=judge_model.value,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
            )

            response_text = response.choices[0].message.content.strip()

            # Parse the response
            score, feedback = self._parse_judge_response(response_text)

            return score, feedback

        except Exception as e:
            logger.error(f"Failed to get evaluation from {judge_model.value}: {e}")
            return 0.0, f"Evaluation failed: {e!s}"

    def _parse_judge_response(self, response_text: str) -> tuple[float, str]:
        """Parse judge response to extract score and feedback."""
        try:
            lines = response_text.split("\n")
            score = 0.0
            reasoning = ""
            improvements = ""

            for line in lines:
                line = line.strip()
                if line.startswith("SCORE:"):
                    score_text = line.replace("SCORE:", "").strip()
                    score = float(score_text)
                elif line.startswith("REASONING:"):
                    reasoning = line.replace("REASONING:", "").strip()
                elif line.startswith("IMPROVEMENTS:"):
                    improvements = line.replace("IMPROVEMENTS:", "").strip()

            # Normalize score to 0-1 range
            score = max(0.0, min(1.0, (score - 1) / 4))

            feedback = f"Reasoning: {reasoning}"
            if improvements and improvements.lower() != "none needed":
                feedback += f"\nImprovements: {improvements}"

            return score, feedback

        except Exception as e:
            logger.warning(f"Failed to parse judge response: {e}")
            return 0.0, response_text

    def _calculate_composite_score(
        self, dimension_scores: dict[EvaluationDimension, float]
    ) -> float:
        """Calculate weighted composite score."""
        total_score = 0.0
        total_weight = 0.0

        for dimension, score in dimension_scores.items():
            weight = self.config.dimension_weights.get(dimension, 1.0)
            total_score += score * weight
            total_weight += weight

        return total_score / total_weight if total_weight > 0 else 0.0

    def _calculate_confidence(
        self, dimension_scores: dict[EvaluationDimension, float]
    ) -> float:
        """Calculate confidence in the evaluation."""
        scores = list(dimension_scores.values())

        if not scores:
            return 0.0

        # Confidence based on score variance (lower variance = higher confidence)
        score_variance = np.var(scores)
        confidence = 1.0 - min(score_variance, 1.0)

        # Boost confidence if scores are consistently high or low
        mean_score = np.mean(scores)
        if mean_score > 0.8 or mean_score < 0.2:
            confidence = min(1.0, confidence + 0.1)

        return confidence

    def _detect_violations(
        self,
        dimension_scores: dict[EvaluationDimension, float],
        detailed_feedback: dict[EvaluationDimension, str],
    ) -> list[str]:
        """Detect violations based on scores and feedback."""
        violations = []

        # Check for low scores
        for dimension, score in dimension_scores.items():
            if score < 0.5:  # Below average
                violations.append(f"Low {dimension.value} score: {score:.2f}")

        # Check for critical safety issues
        if dimension_scores.get(EvaluationDimension.SAFETY, 1.0) < 0.3:
            violations.append("Critical safety concerns detected")

        # Check for compliance issues
        if dimension_scores.get(EvaluationDimension.COMPLIANCE, 1.0) < 0.3:
            violations.append("Significant compliance violations detected")

        return violations

    async def _generate_recommendations(
        self,
        policy_text: str,
        dimension_scores: dict[EvaluationDimension, float],
        violations: list[str],
        context: dict[str, Any],
    ) -> list[str]:
        """Generate improvement recommendations."""
        if not violations and all(score >= 0.8 for score in dimension_scores.values()):
            return ["Policy meets high standards across all dimensions"]

        # Identify lowest scoring dimensions
        low_scoring_dimensions = [
            dimension for dimension, score in dimension_scores.items() if score < 0.7
        ]

        if not low_scoring_dimensions:
            return ["Minor improvements possible but policy is generally sound"]

        recommendations = []
        for dimension in low_scoring_dimensions:
            rubric = self.rubrics[dimension]
            rec = (
                f"Improve {dimension.value}: Focus on {', '.join(rubric.criteria[:2])}"
            )
            recommendations.append(rec)

        return recommendations[:5]  # Limit to 5 recommendations

    def _update_metrics(self, result: SemanticValidationResult):
        """Update performance metrics."""
        self.performance_metrics["total_evaluations"] += 1

        # Update average evaluation time
        total_time = (
            self.performance_metrics["average_evaluation_time"]
            * (self.performance_metrics["total_evaluations"] - 1)
            + result.evaluation_time
        )
        self.performance_metrics["average_evaluation_time"] = (
            total_time / self.performance_metrics["total_evaluations"]
        )

        # Update other metrics
        if result.violations:
            self.performance_metrics["violations_detected"] += 1

        if result.confidence >= self.config.min_confidence_threshold:
            self.performance_metrics["high_confidence_rate"] = (
                self.performance_metrics["high_confidence_rate"]
                * (self.performance_metrics["total_evaluations"] - 1)
                + 1
            ) / self.performance_metrics["total_evaluations"]

    def get_performance_metrics(self) -> dict[str, Any]:
        """Get performance metrics for monitoring."""
        return {
            **self.performance_metrics,
            "evaluation_history_size": len(self.evaluation_history),
            "rubrics_loaded": len(self.rubrics),
        }
