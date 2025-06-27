#!/usr/bin/env python3
"""
Intelligent Routing System for ACGS-PGP Multimodal AI

Advanced routing system that automatically selects the optimal AI model
based on request characteristics, load balancing, and performance metrics.

Features:
- Smart model selection based on content analysis
- Dynamic load balancing with circuit breaker patterns
- Performance-based routing optimization
- Fallback mechanisms and error handling
- Real-time metrics collection and adaptation
- Constitutional compliance priority routing

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class RoutingStrategy(Enum):
    """Available routing strategies."""
    PERFORMANCE_OPTIMIZED = "performance_optimized"
    QUALITY_OPTIMIZED = "quality_optimized"
    COST_OPTIMIZED = "cost_optimized"
    BALANCED = "balanced"
    CONSTITUTIONAL_PRIORITY = "constitutional_priority"


class ModelHealth(Enum):
    """Model health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CIRCUIT_OPEN = "circuit_open"


@dataclass
class ModelPerformanceMetrics:
    """Real-time performance metrics for a model."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time_ms: float = 0.0
    p95_response_time_ms: float = 0.0
    error_rate: float = 0.0
    constitutional_compliance_rate: float = 0.0
    cost_per_request: float = 0.0
    quality_score: float = 0.0
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Recent performance tracking
    recent_response_times: deque = field(default_factory=lambda: deque(maxlen=100))
    recent_errors: deque = field(default_factory=lambda: deque(maxlen=50))
    recent_compliance: deque = field(default_factory=lambda: deque(maxlen=100))


@dataclass
class CircuitBreakerState:
    """Circuit breaker state for model health management."""
    failure_count: int = 0
    last_failure_time: Optional[datetime] = None
    state: ModelHealth = ModelHealth.HEALTHY
    failure_threshold: int = 5
    recovery_timeout_seconds: int = 60
    half_open_max_requests: int = 3
    half_open_requests: int = 0


@dataclass
class RoutingDecision:
    """Result of routing decision with reasoning."""
    selected_model: 'ModelType'
    confidence: float
    reasoning: List[str]
    fallback_models: List['ModelType']
    estimated_response_time_ms: float
    estimated_cost: float
    routing_strategy_used: RoutingStrategy


class ContentAnalyzer:
    """Analyzes content to determine optimal routing."""
    
    def __init__(self):
        self.complexity_keywords = {
            "high": ["comprehensive", "detailed", "analysis", "audit", "critical", "complex"],
            "medium": ["analyze", "evaluate", "assess", "review", "examine"],
            "low": ["check", "quick", "simple", "basic", "fast"]
        }
        
        self.constitutional_keywords = [
            "constitutional", "compliance", "policy", "governance", "democratic",
            "rights", "legal", "regulatory", "audit", "violation"
        ]
        
        self.priority_keywords = {
            "critical": ["emergency", "urgent", "critical", "immediate"],
            "high": ["important", "priority", "significant", "major"],
            "normal": ["standard", "regular", "routine"],
            "low": ["minor", "optional", "background"]
        }
    
    def analyze_content_complexity(self, text: str) -> Tuple[str, float]:
        """Analyze content complexity level."""
        if not text:
            return "low", 0.3
        
        text_lower = text.lower()
        word_count = len(text.split())
        
        # Base complexity on length
        if word_count > 500:
            base_complexity = "high"
            base_score = 0.8
        elif word_count > 100:
            base_complexity = "medium"
            base_score = 0.6
        else:
            base_complexity = "low"
            base_score = 0.4
        
        # Adjust based on keywords
        complexity_score = base_score
        
        for level, keywords in self.complexity_keywords.items():
            keyword_count = sum(1 for keyword in keywords if keyword in text_lower)
            if level == "high" and keyword_count > 0:
                complexity_score += 0.2
            elif level == "medium" and keyword_count > 0:
                complexity_score += 0.1
            elif level == "low" and keyword_count > 0:
                complexity_score -= 0.1
        
        # Constitutional content increases complexity
        constitutional_count = sum(1 for keyword in self.constitutional_keywords if keyword in text_lower)
        if constitutional_count > 2:
            complexity_score += 0.15
        
        complexity_score = max(0.1, min(1.0, complexity_score))
        
        if complexity_score >= 0.7:
            return "high", complexity_score
        elif complexity_score >= 0.5:
            return "medium", complexity_score
        else:
            return "low", complexity_score
    
    def detect_constitutional_content(self, text: str) -> Tuple[bool, float]:
        """Detect if content requires constitutional analysis."""
        if not text:
            return False, 0.0
        
        text_lower = text.lower()
        constitutional_count = sum(1 for keyword in self.constitutional_keywords if keyword in text_lower)
        
        # Calculate constitutional relevance score
        relevance_score = min(1.0, constitutional_count / 10.0)
        
        is_constitutional = constitutional_count >= 2 or relevance_score >= 0.3
        
        return is_constitutional, relevance_score
    
    def analyze_priority_indicators(self, text: str, explicit_priority: str = "normal") -> Tuple[str, float]:
        """Analyze priority indicators in content."""
        if not text:
            return explicit_priority, 0.5
        
        text_lower = text.lower()
        priority_scores = {}
        
        for priority, keywords in self.priority_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            priority_scores[priority] = score
        
        # Find highest scoring priority
        max_priority = max(priority_scores.items(), key=lambda x: x[1])
        
        if max_priority[1] > 0:
            detected_priority = max_priority[0]
            confidence = min(1.0, max_priority[1] / 3.0)
        else:
            detected_priority = explicit_priority
            confidence = 0.5
        
        # Explicit priority takes precedence if specified
        if explicit_priority != "normal":
            return explicit_priority, 0.9
        
        return detected_priority, confidence


class IntelligentRouter:
    """Advanced intelligent routing system for multimodal AI models."""
    
    def __init__(self):
        from services.shared.multimodal_ai_service import ModelType
        
        self.ModelType = ModelType
        self.content_analyzer = ContentAnalyzer()
        
        # Model performance tracking
        self.model_metrics = {
            ModelType.DEEPSEEK_R1: ModelPerformanceMetrics(),
            ModelType.FLASH_FULL: ModelPerformanceMetrics(),
            ModelType.FLASH_LITE: ModelPerformanceMetrics()
        }

        # Circuit breaker states
        self.circuit_breakers = {
            ModelType.DEEPSEEK_R1: CircuitBreakerState(),
            ModelType.FLASH_FULL: CircuitBreakerState(),
            ModelType.FLASH_LITE: CircuitBreakerState()
        }
        
        # Load balancing
        self.current_loads = {
            ModelType.DEEPSEEK_R1: 0,
            ModelType.FLASH_FULL: 0,
            ModelType.FLASH_LITE: 0
        }

        self.max_loads = {
            ModelType.DEEPSEEK_R1: 150,  # Highest capacity for cost-effective model
            ModelType.FLASH_FULL: 50,    # Conservative limit for detailed analysis
            ModelType.FLASH_LITE: 100    # Higher limit for fast responses
        }
        
        # Routing configuration
        self.routing_config = {
            "default_strategy": RoutingStrategy.BALANCED,
            "performance_weight": 0.3,
            "quality_weight": 0.3,
            "cost_weight": 0.2,
            "constitutional_weight": 0.2,
            "response_time_threshold_ms": 2000,
            "quality_threshold": 0.8,
            "constitutional_threshold": 0.95
        }
        
        logger.info("Intelligent Router initialized")
    
    async def route_request(self, request: 'MultimodalRequest', 
                          strategy: RoutingStrategy = None) -> RoutingDecision:
        """Make intelligent routing decision for a request."""
        
        strategy = strategy or self.routing_config["default_strategy"]
        
        # Analyze request characteristics
        content_analysis = self._analyze_request_content(request)
        
        # Check model health and availability
        available_models = self._get_available_models()
        
        if not available_models:
            raise Exception("No healthy models available")
        
        # Apply routing strategy
        routing_scores = self._calculate_routing_scores(
            request, content_analysis, available_models, strategy
        )
        
        # Select best model
        selected_model = max(routing_scores.items(), key=lambda x: x[1][0])[0]
        confidence, reasoning = routing_scores[selected_model]
        
        # Prepare fallback models
        fallback_models = [
            model for model, (score, _) in sorted(routing_scores.items(), 
                                                key=lambda x: x[1][0], reverse=True)
            if model != selected_model
        ]
        
        # Estimate performance
        estimated_response_time = self._estimate_response_time(selected_model, content_analysis)
        estimated_cost = self._estimate_cost(selected_model, content_analysis)
        
        decision = RoutingDecision(
            selected_model=selected_model,
            confidence=confidence,
            reasoning=reasoning,
            fallback_models=fallback_models,
            estimated_response_time_ms=estimated_response_time,
            estimated_cost=estimated_cost,
            routing_strategy_used=strategy
        )
        
        # Update load tracking
        self._update_load(selected_model, 1)
        
        logger.debug(f"Routed request {request.request_id} to {selected_model.value} "
                    f"(confidence: {confidence:.2f}, strategy: {strategy.value})")
        
        return decision
    
    def _analyze_request_content(self, request: 'MultimodalRequest') -> Dict[str, Any]:
        """Analyze request content for routing decisions."""
        
        text_content = request.text_content or ""
        
        # Content complexity analysis
        complexity_level, complexity_score = self.content_analyzer.analyze_content_complexity(text_content)
        
        # Constitutional content detection
        is_constitutional, constitutional_score = self.content_analyzer.detect_constitutional_content(text_content)
        
        # Priority analysis
        priority_level, priority_confidence = self.content_analyzer.analyze_priority_indicators(
            text_content, request.priority
        )
        
        # Request type characteristics
        request_characteristics = {
            "requires_detailed_analysis": request.request_type.value in [
                "detailed_analysis", "policy_analysis", "audit_validation"
            ],
            "requires_speed": request.request_type.value in [
                "quick_analysis", "content_moderation"
            ],
            "is_multimodal": request.content_type.value in [
                "text_and_image", "image_only"
            ],
            "is_policy_document": request.content_type.value == "policy_document"
        }
        
        return {
            "complexity_level": complexity_level,
            "complexity_score": complexity_score,
            "is_constitutional": is_constitutional,
            "constitutional_score": constitutional_score,
            "priority_level": priority_level,
            "priority_confidence": priority_confidence,
            "characteristics": request_characteristics,
            "content_length": len(text_content),
            "has_image": bool(request.image_url or request.image_data)
        }
    
    def _get_available_models(self) -> List['ModelType']:
        """Get list of currently available (healthy) models."""
        
        available = []
        
        for model_type in self.ModelType:
            circuit_breaker = self.circuit_breakers[model_type]
            current_load = self.current_loads[model_type]
            max_load = self.max_loads[model_type]
            
            # Check circuit breaker state
            if circuit_breaker.state == ModelHealth.CIRCUIT_OPEN:
                # Check if recovery timeout has passed
                if (circuit_breaker.last_failure_time and 
                    datetime.now(timezone.utc) - circuit_breaker.last_failure_time > 
                    timedelta(seconds=circuit_breaker.recovery_timeout_seconds)):
                    
                    # Move to half-open state
                    circuit_breaker.state = ModelHealth.HEALTHY
                    circuit_breaker.half_open_requests = 0
                    logger.info(f"Circuit breaker for {model_type.value} moved to half-open state")
                else:
                    continue  # Skip this model
            
            # Check load capacity
            if current_load >= max_load:
                logger.warning(f"Model {model_type.value} at capacity ({current_load}/{max_load})")
                continue
            
            available.append(model_type)
        
        return available

    def _calculate_routing_scores(self, request: 'MultimodalRequest',
                                content_analysis: Dict[str, Any],
                                available_models: List['ModelType'],
                                strategy: RoutingStrategy) -> Dict['ModelType', Tuple[float, List[str]]]:
        """Calculate routing scores for available models."""

        scores = {}

        for model in available_models:
            score, reasoning = self._score_model_for_request(
                model, request, content_analysis, strategy
            )
            scores[model] = (score, reasoning)

        return scores

    def _score_model_for_request(self, model: 'ModelType', request: 'MultimodalRequest',
                               content_analysis: Dict[str, Any],
                               strategy: RoutingStrategy) -> Tuple[float, List[str]]:
        """Score a specific model for a request."""

        reasoning = []
        base_score = 0.5

        # Get model metrics
        metrics = self.model_metrics[model]

        # Strategy-specific scoring
        if strategy == RoutingStrategy.PERFORMANCE_OPTIMIZED:
            score, reasons = self._score_for_performance(model, content_analysis, metrics)
        elif strategy == RoutingStrategy.QUALITY_OPTIMIZED:
            score, reasons = self._score_for_quality(model, content_analysis, metrics)
        elif strategy == RoutingStrategy.COST_OPTIMIZED:
            score, reasons = self._score_for_cost(model, content_analysis, metrics)
        elif strategy == RoutingStrategy.CONSTITUTIONAL_PRIORITY:
            score, reasons = self._score_for_constitutional(model, content_analysis, metrics)
        else:  # BALANCED
            score, reasons = self._score_balanced(model, content_analysis, metrics)

        reasoning.extend(reasons)

        # Apply load balancing penalty
        load_factor = self.current_loads[model] / self.max_loads[model]
        if load_factor > 0.7:
            load_penalty = (load_factor - 0.7) * 0.3
            score -= load_penalty
            reasoning.append(f"Load penalty applied: -{load_penalty:.2f} (load: {load_factor:.1%})")

        # Apply circuit breaker considerations
        circuit_state = self.circuit_breakers[model].state
        if circuit_state == ModelHealth.DEGRADED:
            score *= 0.8
            reasoning.append("Model in degraded state: -20% score")
        elif circuit_state == ModelHealth.UNHEALTHY:
            score *= 0.5
            reasoning.append("Model unhealthy: -50% score")

        return max(0.0, min(1.0, score)), reasoning

    def _score_for_performance(self, model: 'ModelType', content_analysis: Dict[str, Any],
                             metrics: ModelPerformanceMetrics) -> Tuple[float, List[str]]:
        """Score model for performance-optimized routing."""

        reasoning = []

        # Flash Lite generally faster
        if model == self.ModelType.FLASH_LITE:
            base_score = 0.8
            reasoning.append("Flash Lite: optimized for speed")
        else:
            base_score = 0.6
            reasoning.append("Flash Full: detailed but slower")

        # Adjust based on actual performance metrics
        if metrics.avg_response_time_ms > 0:
            if metrics.avg_response_time_ms < 1000:
                base_score += 0.1
                reasoning.append("Fast response time history")
            elif metrics.avg_response_time_ms > 3000:
                base_score -= 0.2
                reasoning.append("Slow response time history")

        # Consider content complexity
        if content_analysis["complexity_level"] == "low" and model == self.ModelType.FLASH_LITE:
            base_score += 0.1
            reasoning.append("Simple content matches Flash Lite capabilities")

        return base_score, reasoning

    def _score_for_quality(self, model: 'ModelType', content_analysis: Dict[str, Any],
                         metrics: ModelPerformanceMetrics) -> Tuple[float, List[str]]:
        """Score model for quality-optimized routing."""

        reasoning = []

        # Flash Full generally higher quality
        if model == self.ModelType.FLASH_FULL:
            base_score = 0.8
            reasoning.append("Flash Full: optimized for quality")
        else:
            base_score = 0.6
            reasoning.append("Flash Lite: good quality but less detailed")

        # Adjust based on content requirements
        if content_analysis["characteristics"]["requires_detailed_analysis"]:
            if model == self.ModelType.FLASH_FULL:
                base_score += 0.15
                reasoning.append("Detailed analysis required: Flash Full preferred")
            else:
                base_score -= 0.1
                reasoning.append("Detailed analysis required: Flash Lite less suitable")

        # Constitutional content needs high quality
        if content_analysis["is_constitutional"] and model == self.ModelType.FLASH_FULL:
            base_score += 0.1
            reasoning.append("Constitutional content: Flash Full preferred for accuracy")

        # Consider historical quality metrics
        if metrics.quality_score > 0.8:
            base_score += 0.05
            reasoning.append("High historical quality score")

        return base_score, reasoning

    def _score_for_cost(self, model: 'ModelType', content_analysis: Dict[str, Any],
                       metrics: ModelPerformanceMetrics) -> Tuple[float, List[str]]:
        """Score model for cost-optimized routing."""

        reasoning = []

        # Flash Lite is more cost-effective
        if model == self.ModelType.FLASH_LITE:
            base_score = 0.9
            reasoning.append("Flash Lite: ~50% cost savings")
        else:
            base_score = 0.4
            reasoning.append("Flash Full: higher cost but better quality")

        # For simple content, cost optimization makes sense
        if content_analysis["complexity_level"] == "low":
            if model == self.ModelType.FLASH_LITE:
                base_score += 0.1
                reasoning.append("Simple content: cost optimization appropriate")

        # For critical content, quality may justify cost
        if content_analysis["priority_level"] == "critical":
            if model == self.ModelType.FLASH_FULL:
                base_score += 0.2
                reasoning.append("Critical priority: quality justifies cost")

        return base_score, reasoning

    def _score_for_constitutional(self, model: 'ModelType', content_analysis: Dict[str, Any],
                                metrics: ModelPerformanceMetrics) -> Tuple[float, List[str]]:
        """Score model for constitutional compliance priority."""

        reasoning = []

        # Constitutional content strongly favors Flash Full
        if content_analysis["is_constitutional"]:
            if model == self.ModelType.FLASH_FULL:
                base_score = 0.9
                reasoning.append("Constitutional content: Flash Full for highest accuracy")
            else:
                base_score = 0.5
                reasoning.append("Constitutional content: Flash Lite acceptable but less preferred")
        else:
            # Non-constitutional content can use either
            base_score = 0.7
            reasoning.append("Non-constitutional content: both models suitable")

        # Consider compliance history
        if metrics.constitutional_compliance_rate > 0.95:
            base_score += 0.05
            reasoning.append("Excellent compliance history")
        elif metrics.constitutional_compliance_rate < 0.9:
            base_score -= 0.1
            reasoning.append("Lower compliance history")

        # High priority constitutional content
        if (content_analysis["is_constitutional"] and
            content_analysis["priority_level"] in ["critical", "high"]):
            if model == self.ModelType.FLASH_FULL:
                base_score += 0.1
                reasoning.append("High-priority constitutional: Flash Full strongly preferred")

        return base_score, reasoning

    def _score_balanced(self, model: 'ModelType', content_analysis: Dict[str, Any],
                       metrics: ModelPerformanceMetrics) -> Tuple[float, List[str]]:
        """Score model using balanced approach."""

        reasoning = []

        # Get individual scores
        perf_score, perf_reasons = self._score_for_performance(model, content_analysis, metrics)
        quality_score, quality_reasons = self._score_for_quality(model, content_analysis, metrics)
        cost_score, cost_reasons = self._score_for_cost(model, content_analysis, metrics)
        const_score, const_reasons = self._score_for_constitutional(model, content_analysis, metrics)

        # Weighted combination
        config = self.routing_config
        balanced_score = (
            perf_score * config["performance_weight"] +
            quality_score * config["quality_weight"] +
            cost_score * config["cost_weight"] +
            const_score * config["constitutional_weight"]
        )

        reasoning.append(f"Balanced score: P:{perf_score:.2f} Q:{quality_score:.2f} C:{cost_score:.2f} Const:{const_score:.2f}")
        reasoning.extend(perf_reasons[:1])  # Include top reason from each category
        reasoning.extend(quality_reasons[:1])
        reasoning.extend(cost_reasons[:1])
        reasoning.extend(const_reasons[:1])

        return balanced_score, reasoning

    def _estimate_response_time(self, model: 'ModelType', content_analysis: Dict[str, Any]) -> float:
        """Estimate response time for model and content."""

        metrics = self.model_metrics[model]

        # Base estimate from historical data
        if metrics.avg_response_time_ms > 0:
            base_time = metrics.avg_response_time_ms
        else:
            # Default estimates
            base_time = 1500 if model == self.ModelType.FLASH_LITE else 3000

        # Adjust for content complexity
        complexity_multiplier = {
            "low": 0.8,
            "medium": 1.0,
            "high": 1.5
        }

        estimated_time = base_time * complexity_multiplier[content_analysis["complexity_level"]]

        # Adjust for content length
        if content_analysis["content_length"] > 1000:
            estimated_time *= 1.2

        # Adjust for multimodal content
        if content_analysis["has_image"]:
            estimated_time *= 1.3

        return estimated_time

    def _estimate_cost(self, model: 'ModelType', content_analysis: Dict[str, Any]) -> float:
        """Estimate cost for model and content."""

        # Base cost estimates (per request)
        base_costs = {
            self.ModelType.FLASH_FULL: 0.002,  # $0.002 per request
            self.ModelType.FLASH_LITE: 0.001   # $0.001 per request
        }

        base_cost = base_costs[model]

        # Adjust for content length (token usage)
        token_multiplier = max(1.0, content_analysis["content_length"] / 1000)
        estimated_cost = base_cost * token_multiplier

        # Multimodal content costs more
        if content_analysis["has_image"]:
            estimated_cost *= 1.5

        return estimated_cost

    def _update_load(self, model: 'ModelType', delta: int):
        """Update current load for a model."""
        self.current_loads[model] = max(0, self.current_loads[model] + delta)

    async def record_request_result(self, model: 'ModelType', success: bool,
                                  response_time_ms: float, constitutional_compliant: bool,
                                  quality_score: float, cost: float):
        """Record the result of a request for metrics tracking."""

        metrics = self.model_metrics[model]
        circuit_breaker = self.circuit_breakers[model]

        # Update basic metrics
        metrics.total_requests += 1

        if success:
            metrics.successful_requests += 1

            # Update response time
            metrics.recent_response_times.append(response_time_ms)
            if metrics.recent_response_times:
                metrics.avg_response_time_ms = sum(metrics.recent_response_times) / len(metrics.recent_response_times)
                sorted_times = sorted(metrics.recent_response_times)
                p95_index = int(len(sorted_times) * 0.95)
                metrics.p95_response_time_ms = sorted_times[p95_index] if sorted_times else 0

            # Update compliance tracking
            metrics.recent_compliance.append(constitutional_compliant)
            if metrics.recent_compliance:
                metrics.constitutional_compliance_rate = sum(metrics.recent_compliance) / len(metrics.recent_compliance)

            # Update quality and cost
            metrics.quality_score = (metrics.quality_score * 0.9) + (quality_score * 0.1)  # Exponential moving average
            metrics.cost_per_request = (metrics.cost_per_request * 0.9) + (cost * 0.1)

            # Reset circuit breaker on success
            if circuit_breaker.state != ModelHealth.HEALTHY:
                circuit_breaker.failure_count = 0
                circuit_breaker.state = ModelHealth.HEALTHY
                logger.info(f"Circuit breaker for {model.value} reset to healthy")

        else:
            metrics.failed_requests += 1
            metrics.recent_errors.append(datetime.now(timezone.utc))

            # Update circuit breaker
            circuit_breaker.failure_count += 1
            circuit_breaker.last_failure_time = datetime.now(timezone.utc)

            if circuit_breaker.failure_count >= circuit_breaker.failure_threshold:
                circuit_breaker.state = ModelHealth.CIRCUIT_OPEN
                logger.warning(f"Circuit breaker opened for {model.value} after {circuit_breaker.failure_count} failures")

        # Update error rate
        if metrics.total_requests > 0:
            metrics.error_rate = metrics.failed_requests / metrics.total_requests

        metrics.last_updated = datetime.now(timezone.utc)

        # Decrease load
        self._update_load(model, -1)

    def get_routing_metrics(self) -> Dict[str, Any]:
        """Get comprehensive routing metrics."""

        return {
            "model_metrics": {
                model.value: {
                    "total_requests": metrics.total_requests,
                    "success_rate": metrics.successful_requests / metrics.total_requests if metrics.total_requests > 0 else 0,
                    "avg_response_time_ms": metrics.avg_response_time_ms,
                    "p95_response_time_ms": metrics.p95_response_time_ms,
                    "error_rate": metrics.error_rate,
                    "constitutional_compliance_rate": metrics.constitutional_compliance_rate,
                    "quality_score": metrics.quality_score,
                    "cost_per_request": metrics.cost_per_request,
                    "current_load": self.current_loads[model],
                    "max_load": self.max_loads[model],
                    "circuit_breaker_state": self.circuit_breakers[model].state.value
                }
                for model, metrics in self.model_metrics.items()
            },
            "routing_config": {
                key: value.value if hasattr(value, 'value') else value
                for key, value in self.routing_config.items()
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
