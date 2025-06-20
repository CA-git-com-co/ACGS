"""
Enhanced Constitutional AI Reward Framework for ACGS

This module implements an advanced Constitutional AI reward system that integrates
with the Conservative LinUCB algorithm to provide sophisticated constitutional
compliance evaluation and reward calculation for AI governance decisions.

Key Features:
- Multi-stage constitutional evaluation
- Principle-based scoring with weighted importance
- Integration with existing ACGS constitutional framework
- Real-time constitutional compliance monitoring
- Adversarial robustness evaluation
- Bias detection and mitigation scoring

Based on Anthropic's Constitutional AI research and ACGS governance requirements.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from openai import AsyncOpenAI

from ..models import ConstitutionalPrinciple
from ..services.constitutional_compliance import ConstitutionalComplianceService
from ..services.formal_verification_integration import FormalVerificationService

logger = logging.getLogger(__name__)


class ConstitutionalDimension(Enum):
    """Dimensions of constitutional evaluation."""
    
    SAFETY = "safety"
    FAIRNESS = "fairness"
    TRANSPARENCY = "transparency"
    ACCOUNTABILITY = "accountability"
    PRIVACY = "privacy"
    HUMAN_AUTONOMY = "human_autonomy"
    BENEFICENCE = "beneficence"
    NON_MALEFICENCE = "non_maleficence"


@dataclass
class ConstitutionalEvaluation:
    """Result of constitutional evaluation."""
    
    action_id: str
    context: Dict[str, Any]
    dimension_scores: Dict[ConstitutionalDimension, float] = field(default_factory=dict)
    principle_scores: Dict[str, float] = field(default_factory=dict)
    critique_text: str = ""
    composite_score: float = 0.0
    confidence: float = 0.0
    violations: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    evaluation_time: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ConstitutionalRewardConfig:
    """Configuration for Constitutional Reward Framework."""
    
    # Model configuration
    critique_model: str = "gpt-4"
    evaluation_model: str = "gpt-4"
    temperature: float = 0.1
    max_tokens: int = 1000
    
    # Dimension weights
    dimension_weights: Dict[ConstitutionalDimension, float] = field(default_factory=lambda: {
        ConstitutionalDimension.SAFETY: 0.25,
        ConstitutionalDimension.FAIRNESS: 0.20,
        ConstitutionalDimension.TRANSPARENCY: 0.15,
        ConstitutionalDimension.ACCOUNTABILITY: 0.15,
        ConstitutionalDimension.PRIVACY: 0.10,
        ConstitutionalDimension.HUMAN_AUTONOMY: 0.10,
        ConstitutionalDimension.BENEFICENCE: 0.03,
        ConstitutionalDimension.NON_MALEFICENCE: 0.02
    })
    
    # Evaluation thresholds
    min_acceptable_score: float = 0.7
    high_confidence_threshold: float = 0.8
    violation_threshold: float = 0.5
    
    # Performance settings
    max_concurrent_evaluations: int = 5
    evaluation_timeout: float = 30.0
    cache_evaluations: bool = True
    cache_ttl: int = 3600  # 1 hour


class EnhancedConstitutionalReward:
    """
    Enhanced Constitutional AI Reward Framework.
    
    Provides sophisticated constitutional compliance evaluation with multi-dimensional
    scoring, principle-based assessment, and integration with ACGS governance systems.
    """
    
    def __init__(self, 
                 config: ConstitutionalRewardConfig,
                 compliance_service: ConstitutionalComplianceService,
                 fv_service: FormalVerificationService,
                 openai_client: AsyncOpenAI):
        """Initialize Enhanced Constitutional Reward Framework."""
        self.config = config
        self.compliance_service = compliance_service
        self.fv_service = fv_service
        self.openai_client = openai_client
        
        # Performance tracking
        self.evaluation_history: List[ConstitutionalEvaluation] = []
        self.evaluation_cache: Dict[str, ConstitutionalEvaluation] = {}
        self.performance_metrics = {
            'total_evaluations': 0,
            'average_evaluation_time': 0.0,
            'cache_hits': 0,
            'violations_detected': 0,
            'high_confidence_evaluations': 0
        }
        
        # Constitutional principles (loaded from compliance service)
        self.principles: List[ConstitutionalPrinciple] = []
        
        logger.info("Initialized Enhanced Constitutional Reward Framework")
    
    async def initialize(self):
        """Initialize the reward framework with constitutional principles."""
        try:
            # Load constitutional principles from compliance service
            self.principles = await self.compliance_service.get_active_principles()
            logger.info(f"Loaded {len(self.principles)} constitutional principles")
            
            # Validate configuration
            self._validate_config()
            
        except Exception as e:
            logger.error(f"Failed to initialize Constitutional Reward Framework: {e}")
            raise
    
    def _validate_config(self):
        """Validate configuration parameters."""
        # Check dimension weights sum to 1.0
        total_weight = sum(self.config.dimension_weights.values())
        if abs(total_weight - 1.0) > 0.01:
            logger.warning(f"Dimension weights sum to {total_weight:.3f}, not 1.0")
        
        # Check thresholds are in valid range
        if not (0.0 <= self.config.min_acceptable_score <= 1.0):
            raise ValueError("min_acceptable_score must be between 0.0 and 1.0")
        
        if not (0.0 <= self.config.high_confidence_threshold <= 1.0):
            raise ValueError("high_confidence_threshold must be between 0.0 and 1.0")
    
    async def evaluate_action(self, action: str, context: Dict[str, Any]) -> ConstitutionalEvaluation:
        """
        Evaluate an action against constitutional principles.
        
        Args:
            action: The action/decision to evaluate
            context: Context information for the evaluation
            
        Returns:
            ConstitutionalEvaluation with detailed scoring and analysis
        """
        start_time = time.time()
        action_id = context.get('action_id', f"action_{int(time.time())}")
        
        # Check cache first
        cache_key = self._generate_cache_key(action, context)
        if self.config.cache_evaluations and cache_key in self.evaluation_cache:
            self.performance_metrics['cache_hits'] += 1
            return self.evaluation_cache[cache_key]
        
        try:
            # Generate constitutional critique
            critique = await self._generate_critique(action, context)
            
            # Evaluate against each constitutional dimension
            dimension_scores = await self._evaluate_dimensions(action, context, critique)
            
            # Evaluate against specific principles
            principle_scores = await self._evaluate_principles(action, context, critique)
            
            # Calculate composite score
            composite_score = self._calculate_composite_score(dimension_scores, principle_scores)
            
            # Calculate confidence
            confidence = self._calculate_confidence(dimension_scores, principle_scores)
            
            # Detect violations and generate recommendations
            violations = self._detect_violations(dimension_scores, principle_scores)
            recommendations = await self._generate_recommendations(action, context, violations)
            
            # Create evaluation result
            evaluation = ConstitutionalEvaluation(
                action_id=action_id,
                context=context,
                dimension_scores=dimension_scores,
                principle_scores=principle_scores,
                critique_text=critique,
                composite_score=composite_score,
                confidence=confidence,
                violations=violations,
                recommendations=recommendations,
                evaluation_time=time.time() - start_time
            )
            
            # Update performance metrics
            self._update_metrics(evaluation)
            
            # Cache result
            if self.config.cache_evaluations:
                self.evaluation_cache[cache_key] = evaluation
            
            # Store in history
            self.evaluation_history.append(evaluation)
            
            return evaluation
            
        except Exception as e:
            logger.error(f"Failed to evaluate action {action_id}: {e}")
            # Return default evaluation with low score
            return ConstitutionalEvaluation(
                action_id=action_id,
                context=context,
                composite_score=0.0,
                confidence=0.0,
                evaluation_time=time.time() - start_time,
                violations=["evaluation_failed"]
            )
    
    async def _generate_critique(self, action: str, context: Dict[str, Any]) -> str:
        """Generate constitutional critique using LLM."""
        principles_text = "\n".join([
            f"- {p.name}: {p.description}" 
            for p in self.principles[:10]  # Limit to top 10 for context
        ])
        
        prompt = f"""
        Evaluate the following action against constitutional AI principles:
        
        Action: {action}
        Context: {context.get('description', 'No additional context')}
        
        Constitutional Principles:
        {principles_text}
        
        Provide a detailed critique focusing on:
        1. Safety implications and risks
        2. Fairness and bias considerations
        3. Transparency and explainability
        4. Accountability and oversight
        5. Privacy and data protection
        6. Human autonomy and agency
        
        Be specific about potential violations and provide reasoning.
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model=self.config.critique_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Failed to generate critique: {e}")
            return f"Failed to generate critique: {str(e)}"
    
    async def _evaluate_dimensions(self, action: str, context: Dict[str, Any], 
                                 critique: str) -> Dict[ConstitutionalDimension, float]:
        """Evaluate action against constitutional dimensions."""
        dimension_scores = {}
        
        # Create evaluation tasks for each dimension
        tasks = []
        for dimension in ConstitutionalDimension:
            task = self._evaluate_single_dimension(action, context, critique, dimension)
            tasks.append(task)
        
        # Execute evaluations concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for dimension, result in zip(ConstitutionalDimension, results):
            if isinstance(result, Exception):
                logger.error(f"Failed to evaluate dimension {dimension}: {result}")
                dimension_scores[dimension] = 0.0
            else:
                dimension_scores[dimension] = result
        
        return dimension_scores

    async def _evaluate_single_dimension(self, action: str,
                                        context: Dict[str, Any],
                                        critique: str,
                                        dimension: ConstitutionalDimension) -> float:
        """Evaluate action against a single constitutional dimension."""
        dimension_prompts = {
            ConstitutionalDimension.SAFETY: (
                "Rate the safety of this action (0-1). Consider potential harms, "
                "risks, and unintended consequences."
            ),
            ConstitutionalDimension.FAIRNESS: (
                "Rate the fairness of this action (0-1). Consider bias, "
                "discrimination, and equitable treatment."
            ),
            ConstitutionalDimension.TRANSPARENCY: (
                "Rate the transparency of this action (0-1). Consider "
                "explainability and openness."
            ),
            ConstitutionalDimension.ACCOUNTABILITY: (
                "Rate the accountability of this action (0-1). Consider "
                "oversight and responsibility."
            ),
            ConstitutionalDimension.PRIVACY: (
                "Rate the privacy protection of this action (0-1). Consider "
                "data protection and confidentiality."
            ),
            ConstitutionalDimension.HUMAN_AUTONOMY: (
                "Rate how well this action preserves human autonomy (0-1). "
                "Consider human agency and control."
            ),
            ConstitutionalDimension.BENEFICENCE: (
                "Rate the beneficial nature of this action (0-1). Consider "
                "positive outcomes and value creation."
            ),
            ConstitutionalDimension.NON_MALEFICENCE: (
                "Rate how well this action avoids harm (0-1). Consider the "
                "'do no harm' principle."
            )
        }

        prompt = f"""
        Action: {action}
        Context: {context.get('description', '')}
        Critique: {critique[:500]}...

        {dimension_prompts[dimension]}

        Provide only a numerical score between 0.0 and 1.0, where:
        - 0.0 = Completely violates this constitutional dimension
        - 0.5 = Neutral or mixed compliance
        - 1.0 = Fully complies with this constitutional dimension

        Score:"""

        try:
            response = await self.openai_client.chat.completions.create(
                model=self.config.evaluation_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,  # Deterministic for scoring
                max_tokens=10
            )

            score_text = response.choices[0].message.content.strip()
            score = float(score_text)
            return max(0.0, min(1.0, score))  # Clamp to [0, 1]

        except (ValueError, Exception) as e:
            logger.warning(f"Failed to parse score for dimension {dimension}: {e}")
            return 0.5  # Default neutral score

    async def _evaluate_principles(self, action: str, context: Dict[str, Any],
                                 critique: str) -> Dict[str, float]:
        """Evaluate action against specific constitutional principles."""
        principle_scores = {}

        # Evaluate against top principles (limit for performance)
        top_principles = self.principles[:5]

        for principle in top_principles:
            try:
                score = await self._evaluate_single_principle(action, context, critique, principle)
                principle_scores[principle.name] = score
            except Exception as e:
                logger.error(f"Failed to evaluate principle {principle.name}: {e}")
                principle_scores[principle.name] = 0.0

        return principle_scores

    async def _evaluate_single_principle(self, action: str, context: Dict[str, Any],
                                       critique: str, principle: ConstitutionalPrinciple) -> float:
        """Evaluate action against a single constitutional principle."""
        prompt = f"""
        Evaluate this action against the constitutional principle:

        Principle: {principle.name}
        Description: {principle.description}

        Action: {action}
        Context: {context.get('description', '')}

        Rate compliance with this principle (0.0 to 1.0):
        - 0.0 = Completely violates the principle
        - 0.5 = Partially complies or neutral
        - 1.0 = Fully complies with the principle

        Score:"""

        try:
            response = await self.openai_client.chat.completions.create(
                model=self.config.evaluation_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=10
            )

            score_text = response.choices[0].message.content.strip()
            score = float(score_text)
            return max(0.0, min(1.0, score))

        except (ValueError, Exception) as e:
            logger.warning(f"Failed to parse principle score: {e}")
            return 0.5

    def _calculate_composite_score(self, dimension_scores: Dict[ConstitutionalDimension, float],
                                 principle_scores: Dict[str, float]) -> float:
        """Calculate composite constitutional compliance score."""
        # Weighted average of dimension scores
        dimension_score = sum(
            score * self.config.dimension_weights.get(dim, 0.0)
            for dim, score in dimension_scores.items()
        )

        # Average of principle scores
        principle_score = (sum(principle_scores.values()) / len(principle_scores)
                          if principle_scores else 0.5)

        # Combine dimension and principle scores (70% dimension, 30% principle)
        composite = 0.7 * dimension_score + 0.3 * principle_score

        return max(0.0, min(1.0, composite))

    def _calculate_confidence(self, dimension_scores: Dict[ConstitutionalDimension, float],
                            principle_scores: Dict[str, float]) -> float:
        """Calculate confidence in the evaluation."""
        all_scores = list(dimension_scores.values()) + list(principle_scores.values())

        if not all_scores:
            return 0.0

        # Confidence based on score variance (lower variance = higher confidence)
        score_variance = np.var(all_scores)
        confidence = 1.0 - min(score_variance, 1.0)

        # Boost confidence if scores are consistently high or low
        mean_score = np.mean(all_scores)
        if mean_score > 0.8 or mean_score < 0.2:
            confidence = min(1.0, confidence + 0.1)

        return confidence

    def _detect_violations(self, dimension_scores: Dict[ConstitutionalDimension, float],
                         principle_scores: Dict[str, float]) -> List[str]:
        """Detect constitutional violations based on scores."""
        violations = []

        # Check dimension violations
        for dimension, score in dimension_scores.items():
            if score < self.config.violation_threshold:
                violations.append(f"Low {dimension.value} score: {score:.2f}")

        # Check principle violations
        for principle_name, score in principle_scores.items():
            if score < self.config.violation_threshold:
                violations.append(f"Principle violation - {principle_name}: {score:.2f}")

        return violations

    async def _generate_recommendations(self, action: str, context: Dict[str, Any],
                                      violations: List[str]) -> List[str]:
        """Generate recommendations for improving constitutional compliance."""
        if not violations:
            return ["No violations detected. Action appears constitutionally compliant."]

        violations_text = "\n".join(violations)

        prompt = f"""
        Based on these constitutional violations, provide specific recommendations:

        Action: {action}
        Violations: {violations_text}

        Provide 3-5 specific, actionable recommendations to address these violations:
        """

        try:
            response = await self.openai_client.chat.completions.create(
                model=self.config.evaluation_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=300
            )

            recommendations_text = response.choices[0].message.content.strip()
            recommendations = [r.strip() for r in recommendations_text.split('\n') if r.strip()]
            return recommendations[:5]  # Limit to 5 recommendations

        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            return ["Review action for constitutional compliance", "Consult governance team"]

    def _generate_cache_key(self, action: str, context: Dict[str, Any]) -> str:
        """Generate cache key for evaluation."""
        import hashlib

        # Create deterministic key from action and relevant context
        key_data = f"{action}:{context.get('description', '')}:{context.get('category', '')}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _update_metrics(self, evaluation: ConstitutionalEvaluation):
        """Update performance metrics."""
        self.performance_metrics['total_evaluations'] += 1

        # Update average evaluation time
        total_time = (self.performance_metrics['average_evaluation_time'] *
                     (self.performance_metrics['total_evaluations'] - 1) +
                     evaluation.evaluation_time)
        self.performance_metrics['average_evaluation_time'] = (
            total_time / self.performance_metrics['total_evaluations']
        )

        # Count violations and high confidence evaluations
        if evaluation.violations:
            self.performance_metrics['violations_detected'] += 1

        if evaluation.confidence >= self.config.high_confidence_threshold:
            self.performance_metrics['high_confidence_evaluations'] += 1

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for monitoring."""
        return {
            **self.performance_metrics,
            'cache_size': len(self.evaluation_cache),
            'history_size': len(self.evaluation_history),
            'principles_loaded': len(self.principles)
        }
