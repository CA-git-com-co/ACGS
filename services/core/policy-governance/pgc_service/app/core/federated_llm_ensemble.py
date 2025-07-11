"""
Federated LLM Ensemble Simulation System

Provides federated ensemble simulation with GPT-4, Claude, and Llama-3 models
for enhanced reliability, bias reduction, and constitutional compliance in ACGS-2.

Constitutional Hash: cdd01ef066bc6cf2

Key Features:
- Multi-model ensemble with GPT-4, Claude, Llama-3 simulation
- Federated learning and consensus mechanisms
- Bias reduction through diverse model perspectives
- 99.92% reliability target with ensemble voting
- Constitutional compliance validation across all models
- Performance optimization and load balancing
"""

import asyncio
import json
import logging
import random
import statistics
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

# Constitutional compliance hash for ACGS-2
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


class LLMModelType(Enum):
    """Supported LLM model types."""
    GPT_4 = "gpt-4"
    CLAUDE_3 = "claude-3"
    LLAMA_3 = "llama-3"


class EnsembleStrategy(Enum):
    """Ensemble voting strategies."""
    MAJORITY_VOTE = "majority_vote"
    WEIGHTED_AVERAGE = "weighted_average"
    CONFIDENCE_WEIGHTED = "confidence_weighted"
    CONSTITUTIONAL_PRIORITY = "constitutional_priority"


class BiasType(Enum):
    """Types of bias to detect and mitigate."""
    DEMOGRAPHIC = "demographic"
    CULTURAL = "cultural"
    LINGUISTIC = "linguistic"
    TEMPORAL = "temporal"
    CONFIRMATION = "confirmation"


@dataclass
class ModelResponse:
    """Response from an individual LLM model."""
    
    model_type: LLMModelType
    response_id: str
    content: str
    confidence_score: float
    reasoning: str
    constitutional_compliance_score: float
    bias_scores: Dict[BiasType, float] = field(default_factory=dict)
    response_time_ms: float = 0.0
    token_count: int = 0
    constitutional_hash: str = CONSTITUTIONAL_HASH


@dataclass
class EnsembleResponse:
    """Aggregated response from the LLM ensemble."""
    
    ensemble_id: str
    final_content: str
    consensus_confidence: float
    individual_responses: List[ModelResponse]
    ensemble_strategy: EnsembleStrategy
    bias_mitigation_applied: bool
    constitutional_compliance_score: float
    reliability_score: float
    processing_time_ms: float
    constitutional_hash: str = CONSTITUTIONAL_HASH


@dataclass
class FederatedLearningMetrics:
    """Metrics for federated learning performance."""
    
    total_queries: int = 0
    successful_consensus: int = 0
    bias_detections: int = 0
    constitutional_violations: int = 0
    avg_reliability_score: float = 0.0
    avg_consensus_confidence: float = 0.0
    model_performance: Dict[LLMModelType, Dict[str, float]] = field(default_factory=dict)
    constitutional_hash: str = CONSTITUTIONAL_HASH


class MockLLMSimulator:
    """Mock LLM simulator for testing federated ensemble."""
    
    def __init__(self, model_type: LLMModelType):
        self.model_type = model_type
        self.model_characteristics = self._get_model_characteristics()
        
        # Model-specific performance characteristics
        self.base_confidence = self.model_characteristics["base_confidence"]
        self.response_time_range = self.model_characteristics["response_time_range"]
        self.bias_tendencies = self.model_characteristics["bias_tendencies"]
        self.constitutional_alignment = self.model_characteristics["constitutional_alignment"]
    
    def _get_model_characteristics(self) -> Dict[str, Any]:
        """Get model-specific characteristics for simulation."""
        characteristics = {
            LLMModelType.GPT_4: {
                "base_confidence": 0.85,
                "response_time_range": (100, 300),  # ms
                "bias_tendencies": {
                    BiasType.DEMOGRAPHIC: 0.15,
                    BiasType.CULTURAL: 0.20,
                    BiasType.LINGUISTIC: 0.10,
                    BiasType.TEMPORAL: 0.25,
                    BiasType.CONFIRMATION: 0.18
                },
                "constitutional_alignment": 0.90,
                "strengths": ["reasoning", "context_understanding"],
                "weaknesses": ["potential_bias", "training_cutoff"]
            },
            LLMModelType.CLAUDE_3: {
                "base_confidence": 0.88,
                "response_time_range": (80, 250),  # ms
                "bias_tendencies": {
                    BiasType.DEMOGRAPHIC: 0.10,
                    BiasType.CULTURAL: 0.12,
                    BiasType.LINGUISTIC: 0.08,
                    BiasType.TEMPORAL: 0.15,
                    BiasType.CONFIRMATION: 0.12
                },
                "constitutional_alignment": 0.95,
                "strengths": ["constitutional_ai", "safety", "helpfulness"],
                "weaknesses": ["conservative_responses"]
            },
            LLMModelType.LLAMA_3: {
                "base_confidence": 0.82,
                "response_time_range": (120, 400),  # ms
                "bias_tendencies": {
                    BiasType.DEMOGRAPHIC: 0.18,
                    BiasType.CULTURAL: 0.25,
                    BiasType.LINGUISTIC: 0.15,
                    BiasType.TEMPORAL: 0.20,
                    BiasType.CONFIRMATION: 0.22
                },
                "constitutional_alignment": 0.85,
                "strengths": ["open_source", "customizable", "diverse_training"],
                "weaknesses": ["higher_bias_risk", "variable_quality"]
            }
        }
        
        return characteristics[self.model_type]
    
    async def generate_response(self, prompt: str, context: Dict[str, Any] = None) -> ModelResponse:
        """Generate a mock response from the LLM model."""
        response_id = f"{self.model_type.value}-{int(time.time())}-{str(uuid4())[:8]}"
        start_time = time.time()
        
        # Simulate response time
        response_time = random.uniform(*self.response_time_range)
        await asyncio.sleep(response_time / 1000.0)  # Convert to seconds
        
        # Generate mock content based on model characteristics
        content = await self._generate_mock_content(prompt, context)
        
        # Calculate confidence score with some randomness
        confidence_variation = random.uniform(-0.1, 0.1)
        confidence_score = max(0.0, min(1.0, self.base_confidence + confidence_variation))
        
        # Calculate bias scores
        bias_scores = {}
        for bias_type, base_tendency in self.bias_tendencies.items():
            variation = random.uniform(-0.05, 0.05)
            bias_scores[bias_type] = max(0.0, min(1.0, base_tendency + variation))
        
        # Calculate constitutional compliance
        constitutional_variation = random.uniform(-0.05, 0.05)
        constitutional_compliance = max(0.0, min(1.0, self.constitutional_alignment + constitutional_variation))
        
        # Generate reasoning
        reasoning = f"Response generated by {self.model_type.value} with {confidence_score:.2f} confidence. " \
                   f"Constitutional alignment: {constitutional_compliance:.2f}. " \
                   f"Bias mitigation applied for {len([b for b in bias_scores.values() if b > 0.2])} bias types."
        
        actual_response_time = (time.time() - start_time) * 1000
        
        return ModelResponse(
            model_type=self.model_type,
            response_id=response_id,
            content=content,
            confidence_score=confidence_score,
            reasoning=reasoning,
            constitutional_compliance_score=constitutional_compliance,
            bias_scores=bias_scores,
            response_time_ms=actual_response_time,
            token_count=len(content.split())
        )
    
    async def _generate_mock_content(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """Generate mock content based on model type and prompt."""
        base_content = f"""package policy.{context.get('category', 'general') if context else 'general'}

default allow = false

allow {{
    input.constitutional_hash == "{CONSTITUTIONAL_HASH}"
    input.validated == true
    # Generated by {self.model_type.value}
    # Prompt: {prompt[:50]}...
}}"""
        
        # Add model-specific variations
        if self.model_type == LLMModelType.GPT_4:
            base_content += "\n    # GPT-4: Enhanced reasoning and context understanding"
        elif self.model_type == LLMModelType.CLAUDE_3:
            base_content += "\n    # Claude-3: Constitutional AI alignment and safety focus"
        elif self.model_type == LLMModelType.LLAMA_3:
            base_content += "\n    # Llama-3: Open-source flexibility and diverse perspectives"
        
        return base_content


class BiasDetectionEngine:
    """Engine for detecting and mitigating bias across LLM responses."""
    
    def __init__(self):
        self.bias_thresholds = {
            BiasType.DEMOGRAPHIC: 0.3,
            BiasType.CULTURAL: 0.3,
            BiasType.LINGUISTIC: 0.25,
            BiasType.TEMPORAL: 0.35,
            BiasType.CONFIRMATION: 0.3
        }
        
        self.mitigation_strategies = {
            BiasType.DEMOGRAPHIC: "demographic_balancing",
            BiasType.CULTURAL: "cultural_perspective_weighting",
            BiasType.LINGUISTIC: "linguistic_normalization",
            BiasType.TEMPORAL: "temporal_context_adjustment",
            BiasType.CONFIRMATION: "diverse_viewpoint_integration"
        }
    
    async def detect_bias(self, responses: List[ModelResponse]) -> Dict[BiasType, float]:
        """Detect bias across ensemble responses."""
        ensemble_bias_scores = {}
        
        for bias_type in BiasType:
            # Calculate average bias score across models
            bias_scores = [response.bias_scores.get(bias_type, 0.0) for response in responses]
            avg_bias = statistics.mean(bias_scores)
            
            # Calculate variance to detect inconsistency
            bias_variance = statistics.variance(bias_scores) if len(bias_scores) > 1 else 0.0
            
            # Combine average and variance for final bias score
            ensemble_bias_scores[bias_type] = avg_bias + (bias_variance * 0.5)
        
        return ensemble_bias_scores
    
    async def apply_bias_mitigation(
        self,
        responses: List[ModelResponse],
        detected_bias: Dict[BiasType, float]
    ) -> List[ModelResponse]:
        """Apply bias mitigation strategies to responses."""
        mitigated_responses = []
        
        for response in responses:
            mitigated_response = ModelResponse(
                model_type=response.model_type,
                response_id=response.response_id,
                content=response.content,
                confidence_score=response.confidence_score,
                reasoning=response.reasoning,
                constitutional_compliance_score=response.constitutional_compliance_score,
                bias_scores=response.bias_scores.copy(),
                response_time_ms=response.response_time_ms,
                token_count=response.token_count
            )
            
            # Apply mitigation for each bias type above threshold
            for bias_type, bias_score in detected_bias.items():
                if bias_score > self.bias_thresholds[bias_type]:
                    mitigation_factor = 1.0 - (bias_score - self.bias_thresholds[bias_type])
                    
                    # Reduce bias score
                    mitigated_response.bias_scores[bias_type] *= mitigation_factor
                    
                    # Adjust confidence based on bias mitigation
                    confidence_adjustment = 0.95  # Slight confidence reduction for mitigation
                    mitigated_response.confidence_score *= confidence_adjustment
                    
                    # Update reasoning
                    strategy = self.mitigation_strategies[bias_type]
                    mitigated_response.reasoning += f" Applied {strategy} for {bias_type.value} bias mitigation."
            
            mitigated_responses.append(mitigated_response)
        
        return mitigated_responses
    
    def calculate_bias_reduction(
        self,
        original_responses: List[ModelResponse],
        mitigated_responses: List[ModelResponse]
    ) -> Dict[BiasType, float]:
        """Calculate bias reduction achieved through mitigation."""
        bias_reduction = {}
        
        for bias_type in BiasType:
            original_avg = statistics.mean([r.bias_scores.get(bias_type, 0.0) for r in original_responses])
            mitigated_avg = statistics.mean([r.bias_scores.get(bias_type, 0.0) for r in mitigated_responses])
            
            reduction = max(0.0, original_avg - mitigated_avg)
            bias_reduction[bias_type] = reduction
        
        return bias_reduction


class FederatedLLMEnsemble:
    """Federated LLM ensemble system for enhanced reliability and bias reduction."""
    
    def __init__(self, ensemble_strategy: EnsembleStrategy = EnsembleStrategy.CONSTITUTIONAL_PRIORITY):
        self.ensemble_strategy = ensemble_strategy
        self.models = {
            LLMModelType.GPT_4: MockLLMSimulator(LLMModelType.GPT_4),
            LLMModelType.CLAUDE_3: MockLLMSimulator(LLMModelType.CLAUDE_3),
            LLMModelType.LLAMA_3: MockLLMSimulator(LLMModelType.LLAMA_3)
        }
        
        self.bias_detection_engine = BiasDetectionEngine()
        self.federated_metrics = FederatedLearningMetrics()
        
        # Model weights for ensemble voting
        self.model_weights = {
            LLMModelType.GPT_4: 0.35,
            LLMModelType.CLAUDE_3: 0.40,  # Higher weight for constitutional alignment
            LLMModelType.LLAMA_3: 0.25
        }
        
        # Reliability targets
        self.target_reliability = 0.9992  # 99.92%
        self.target_consensus_confidence = 0.85
        self.target_bias_reduction = 0.5  # 50% bias reduction
        
        logger.info("Federated LLM Ensemble initialized with constitutional priority")
    
    async def generate_ensemble_response(
        self,
        prompt: str,
        context: Dict[str, Any] = None,
        models_to_use: Optional[List[LLMModelType]] = None
    ) -> EnsembleResponse:
        """Generate ensemble response from multiple LLM models."""
        ensemble_id = f"ensemble-{int(time.time())}-{str(uuid4())[:8]}"
        start_time = time.time()
        
        # Use all models if not specified
        if models_to_use is None:
            models_to_use = list(self.models.keys())
        
        # Generate responses from all selected models concurrently
        tasks = []
        for model_type in models_to_use:
            if model_type in self.models:
                task = self.models[model_type].generate_response(prompt, context)
                tasks.append(task)
        
        individual_responses = await asyncio.gather(*tasks)
        
        # Detect bias across responses
        detected_bias = await self.bias_detection_engine.detect_bias(individual_responses)
        
        # Apply bias mitigation
        mitigated_responses = await self.bias_detection_engine.apply_bias_mitigation(
            individual_responses, detected_bias
        )
        
        # Generate ensemble consensus
        final_content, consensus_confidence = await self._generate_consensus(mitigated_responses)
        
        # Calculate ensemble metrics
        constitutional_compliance = await self._calculate_ensemble_constitutional_compliance(mitigated_responses)
        reliability_score = await self._calculate_reliability_score(mitigated_responses, consensus_confidence)
        
        processing_time = (time.time() - start_time) * 1000
        
        # Update federated learning metrics
        await self._update_federated_metrics(mitigated_responses, consensus_confidence, detected_bias)
        
        ensemble_response = EnsembleResponse(
            ensemble_id=ensemble_id,
            final_content=final_content,
            consensus_confidence=consensus_confidence,
            individual_responses=mitigated_responses,
            ensemble_strategy=self.ensemble_strategy,
            bias_mitigation_applied=any(bias > 0.2 for bias in detected_bias.values()),
            constitutional_compliance_score=constitutional_compliance,
            reliability_score=reliability_score,
            processing_time_ms=processing_time
        )
        
        logger.info(f"Ensemble response generated: {ensemble_id}, "
                   f"reliability: {reliability_score:.3f}, "
                   f"constitutional compliance: {constitutional_compliance:.3f}")
        
        return ensemble_response
    
    async def _generate_consensus(self, responses: List[ModelResponse]) -> Tuple[str, float]:
        """Generate consensus from multiple model responses."""
        if not responses:
            return "", 0.0
        
        if self.ensemble_strategy == EnsembleStrategy.MAJORITY_VOTE:
            return await self._majority_vote_consensus(responses)
        elif self.ensemble_strategy == EnsembleStrategy.WEIGHTED_AVERAGE:
            return await self._weighted_average_consensus(responses)
        elif self.ensemble_strategy == EnsembleStrategy.CONFIDENCE_WEIGHTED:
            return await self._confidence_weighted_consensus(responses)
        elif self.ensemble_strategy == EnsembleStrategy.CONSTITUTIONAL_PRIORITY:
            return await self._constitutional_priority_consensus(responses)
        else:
            # Default to constitutional priority
            return await self._constitutional_priority_consensus(responses)
    
    async def _constitutional_priority_consensus(self, responses: List[ModelResponse]) -> Tuple[str, float]:
        """Generate consensus prioritizing constitutional compliance."""
        # Sort responses by constitutional compliance score
        sorted_responses = sorted(responses, key=lambda r: r.constitutional_compliance_score, reverse=True)
        
        # Use the response with highest constitutional compliance as base
        best_response = sorted_responses[0]
        
        # Calculate consensus confidence based on constitutional alignment
        constitutional_scores = [r.constitutional_compliance_score for r in responses]
        consensus_confidence = statistics.mean(constitutional_scores)
        
        # Enhance content with constitutional validation
        enhanced_content = best_response.content
        if CONSTITUTIONAL_HASH not in enhanced_content:
            enhanced_content = enhanced_content.replace(
                "input.validated == true",
                f"input.constitutional_hash == \"{CONSTITUTIONAL_HASH}\"\n    input.validated == true"
            )
        
        return enhanced_content, consensus_confidence
    
    async def _weighted_average_consensus(self, responses: List[ModelResponse]) -> Tuple[str, float]:
        """Generate consensus using weighted average of model responses."""
        if not responses:
            return "", 0.0
        
        # Calculate weighted confidence
        total_weight = 0.0
        weighted_confidence = 0.0
        
        for response in responses:
            weight = self.model_weights.get(response.model_type, 0.33)
            weighted_confidence += response.confidence_score * weight
            total_weight += weight
        
        consensus_confidence = weighted_confidence / total_weight if total_weight > 0 else 0.0
        
        # Select content from highest weighted model
        best_response = max(responses, key=lambda r: self.model_weights.get(r.model_type, 0.33))
        
        return best_response.content, consensus_confidence
    
    async def _confidence_weighted_consensus(self, responses: List[ModelResponse]) -> Tuple[str, float]:
        """Generate consensus weighted by individual model confidence."""
        if not responses:
            return "", 0.0
        
        # Use response with highest confidence
        best_response = max(responses, key=lambda r: r.confidence_score)
        
        # Calculate consensus confidence as average of all confidences
        consensus_confidence = statistics.mean([r.confidence_score for r in responses])
        
        return best_response.content, consensus_confidence
    
    async def _majority_vote_consensus(self, responses: List[ModelResponse]) -> Tuple[str, float]:
        """Generate consensus using majority vote (simplified for mock)."""
        if not responses:
            return "", 0.0
        
        # For simplicity, use the response with median confidence
        sorted_responses = sorted(responses, key=lambda r: r.confidence_score)
        median_response = sorted_responses[len(sorted_responses) // 2]
        
        consensus_confidence = statistics.mean([r.confidence_score for r in responses])
        
        return median_response.content, consensus_confidence
    
    async def _calculate_ensemble_constitutional_compliance(self, responses: List[ModelResponse]) -> float:
        """Calculate ensemble constitutional compliance score."""
        if not responses:
            return 0.0
        
        compliance_scores = [r.constitutional_compliance_score for r in responses]
        
        # Use minimum compliance to ensure all models meet standards
        min_compliance = min(compliance_scores)
        avg_compliance = statistics.mean(compliance_scores)
        
        # Weighted combination favoring minimum compliance
        ensemble_compliance = (min_compliance * 0.7) + (avg_compliance * 0.3)
        
        return ensemble_compliance
    
    async def _calculate_reliability_score(
        self,
        responses: List[ModelResponse],
        consensus_confidence: float
    ) -> float:
        """Calculate ensemble reliability score targeting 99.92%."""
        if not responses:
            return 0.0
        
        # Base reliability from consensus confidence
        base_reliability = consensus_confidence
        
        # Boost from multiple models (ensemble effect)
        ensemble_boost = min(0.1, len(responses) * 0.03)
        
        # Constitutional compliance boost
        constitutional_scores = [r.constitutional_compliance_score for r in responses]
        constitutional_boost = statistics.mean(constitutional_scores) * 0.05
        
        # Bias mitigation boost
        avg_bias = statistics.mean([
            statistics.mean(list(r.bias_scores.values())) for r in responses
        ])
        bias_mitigation_boost = max(0.0, (0.3 - avg_bias) * 0.1)
        
        reliability_score = base_reliability + ensemble_boost + constitutional_boost + bias_mitigation_boost
        
        return min(reliability_score, 1.0)
    
    async def _update_federated_metrics(
        self,
        responses: List[ModelResponse],
        consensus_confidence: float,
        detected_bias: Dict[BiasType, float]
    ):
        """Update federated learning metrics."""
        self.federated_metrics.total_queries += 1
        
        # Update consensus tracking
        if consensus_confidence >= self.target_consensus_confidence:
            self.federated_metrics.successful_consensus += 1
        
        # Update bias detection tracking
        if any(bias > 0.3 for bias in detected_bias.values()):
            self.federated_metrics.bias_detections += 1
        
        # Update constitutional violations
        constitutional_violations = sum(1 for r in responses if r.constitutional_compliance_score < 0.95)
        self.federated_metrics.constitutional_violations += constitutional_violations
        
        # Update running averages
        current_reliability = await self._calculate_reliability_score(responses, consensus_confidence)
        
        total_queries = self.federated_metrics.total_queries
        self.federated_metrics.avg_reliability_score = (
            (self.federated_metrics.avg_reliability_score * (total_queries - 1) + current_reliability) / total_queries
        )
        
        self.federated_metrics.avg_consensus_confidence = (
            (self.federated_metrics.avg_consensus_confidence * (total_queries - 1) + consensus_confidence) / total_queries
        )
        
        # Update per-model performance
        for response in responses:
            model_type = response.model_type
            if model_type not in self.federated_metrics.model_performance:
                self.federated_metrics.model_performance[model_type] = {
                    "avg_confidence": 0.0,
                    "avg_constitutional_compliance": 0.0,
                    "avg_response_time": 0.0,
                    "query_count": 0
                }
            
            model_metrics = self.federated_metrics.model_performance[model_type]
            query_count = model_metrics["query_count"] + 1
            
            model_metrics["avg_confidence"] = (
                (model_metrics["avg_confidence"] * model_metrics["query_count"] + response.confidence_score) / query_count
            )
            model_metrics["avg_constitutional_compliance"] = (
                (model_metrics["avg_constitutional_compliance"] * model_metrics["query_count"] + response.constitutional_compliance_score) / query_count
            )
            model_metrics["avg_response_time"] = (
                (model_metrics["avg_response_time"] * model_metrics["query_count"] + response.response_time_ms) / query_count
            )
            model_metrics["query_count"] = query_count
    
    def get_federated_metrics(self) -> Dict[str, Any]:
        """Get comprehensive federated learning metrics."""
        success_rate = 0.0
        if self.federated_metrics.total_queries > 0:
            success_rate = self.federated_metrics.successful_consensus / self.federated_metrics.total_queries
        
        bias_detection_rate = 0.0
        if self.federated_metrics.total_queries > 0:
            bias_detection_rate = self.federated_metrics.bias_detections / self.federated_metrics.total_queries
        
        constitutional_violation_rate = 0.0
        if self.federated_metrics.total_queries > 0:
            constitutional_violation_rate = self.federated_metrics.constitutional_violations / self.federated_metrics.total_queries
        
        return {
            "ensemble_strategy": self.ensemble_strategy.value,
            "target_reliability": self.target_reliability,
            "current_reliability": self.federated_metrics.avg_reliability_score,
            "reliability_target_met": self.federated_metrics.avg_reliability_score >= self.target_reliability,
            "total_queries": self.federated_metrics.total_queries,
            "consensus_success_rate": success_rate,
            "avg_consensus_confidence": self.federated_metrics.avg_consensus_confidence,
            "bias_detection_rate": bias_detection_rate,
            "constitutional_violation_rate": constitutional_violation_rate,
            "model_performance": dict(self.federated_metrics.model_performance),
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of federated ensemble."""
        health_status = {
            "status": "healthy",
            "models_available": len(self.models),
            "ensemble_strategy": self.ensemble_strategy.value,
            "target_reliability": self.target_reliability,
            "current_reliability": self.federated_metrics.avg_reliability_score,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "timestamp": time.time()
        }
        
        try:
            # Test each model
            model_health = {}
            for model_type, model in self.models.items():
                test_response = await model.generate_response("health check test")
                model_health[model_type.value] = {
                    "available": True,
                    "response_time_ms": test_response.response_time_ms,
                    "constitutional_compliance": test_response.constitutional_compliance_score
                }
            
            health_status["model_health"] = model_health
            
            # Check if reliability target is met
            if self.federated_metrics.avg_reliability_score < self.target_reliability:
                health_status["status"] = "degraded"
                health_status["warning"] = f"Reliability {self.federated_metrics.avg_reliability_score:.4f} below target {self.target_reliability}"
            
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)
            logger.error(f"Federated ensemble health check failed: {e}")
        
        return health_status


# Global instance for service integration
_federated_ensemble: Optional[FederatedLLMEnsemble] = None


async def get_federated_ensemble(
    strategy: EnsembleStrategy = EnsembleStrategy.CONSTITUTIONAL_PRIORITY
) -> FederatedLLMEnsemble:
    """Get or create global federated ensemble instance."""
    global _federated_ensemble
    
    if _federated_ensemble is None:
        _federated_ensemble = FederatedLLMEnsemble(strategy)
    
    return _federated_ensemble


# Integration with existing RAG system
async def integrate_with_rag_system(
    ensemble: FederatedLLMEnsemble,
    rag_query: str,
    retrieved_principles: List[Any],
    context: Dict[str, Any] = None
) -> EnsembleResponse:
    """Integrate federated ensemble with existing RAG system."""
    # Enhance prompt with retrieved principles
    enhanced_prompt = f"""
Generate a Rego policy rule based on the following constitutional principles:

Retrieved Principles:
{json.dumps([str(p) for p in retrieved_principles[:3]], indent=2)}

Query: {rag_query}

Requirements:
- Must include constitutional hash validation: {CONSTITUTIONAL_HASH}
- Must follow Rego syntax standards
- Must ensure constitutional compliance
- Must be explainable and auditable

Generate the policy rule:
"""

    # Generate ensemble response
    ensemble_response = await ensemble.generate_ensemble_response(
        enhanced_prompt, context
    )

    return ensemble_response
