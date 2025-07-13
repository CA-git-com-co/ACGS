"""
Multi-Model Coordinator for Phase 2 AlphaEvolve-ACGS Integration

This module implements advanced multi-model ensemble coordination for policy synthesis
with WINA optimization, targeting >99.9% reliability and constitutional compliance.

Key Features:
- Weighted voting ensemble strategy
- WINA-optimized model selection
- Real-time performance monitoring
- Constitutional fidelity tracking
- Adaptive fallback mechanisms
"""

import asyncio
import hashlib
import json
import logging
import operator
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


try:
    import redis.asyncio as redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)


class EnsembleStrategy(Enum):
    """Ensemble coordination strategies."""

    WEIGHTED_VOTING = "weighted_voting"
    CONSENSUS_BASED = "consensus_based"
    PERFORMANCE_ADAPTIVE = "performance_adaptive"
    CONSTITUTIONAL_PRIORITY = "constitutional_priority"
    WINA_OPTIMIZED = "wina_optimized"


class RequestComplexity(Enum):
    """Request complexity classification for adaptive routing."""

    SIMPLE = "simple"  # Basic policies, single model sufficient
    COMPLEX = "complex"  # Multi-faceted policies, ensemble needed
    HIGH_STAKES = "high_stakes"  # Critical policies, full ensemble + verification


class RequestClassifier:
    """Lightweight classifier for synthesis request complexity."""

    def __init__(self):
        self.complexity_keywords = {
            RequestComplexity.HIGH_STAKES: [
                "safety",
                "critical",
                "emergency",
                "security",
                "constitutional",
                "violation",
                "breach",
                "audit",
                "compliance",
                "legal",
            ],
            RequestComplexity.COMPLEX: [
                "multi",
                "integration",
                "workflow",
                "process",
                "stakeholder",
                "consensus",
                "governance",
                "policy",
                "framework",
                "system",
            ],
            RequestComplexity.SIMPLE: [
                "basic",
                "simple",
                "standard",
                "routine",
                "default",
                "template",
            ],
        }

    def classify_request(self, synthesis_request: dict[str, Any]) -> RequestComplexity:
        """Classify request complexity based on content analysis."""
        request_text = str(synthesis_request).lower()

        # Count keyword matches for each complexity level
        complexity_scores = {}
        for complexity, keywords in self.complexity_keywords.items():
            score = sum(1 for keyword in keywords if keyword in request_text)
            complexity_scores[complexity] = score

        # Determine complexity based on highest score
        if complexity_scores[RequestComplexity.HIGH_STAKES] > 0:
            return RequestComplexity.HIGH_STAKES
        if complexity_scores[RequestComplexity.COMPLEX] > 1:
            return RequestComplexity.COMPLEX
        return RequestComplexity.SIMPLE


@dataclass
class ModelPerformanceMetrics:
    """Enhanced performance metrics for individual models with cost and capability tracking."""

    model_id: str
    synthesis_accuracy: float
    constitutional_compliance: float
    response_time_ms: float
    gflops_usage: float
    reliability_score: float
    last_updated: datetime

    # Enhanced metrics for router optimization
    cost_per_token: float = 0.0
    api_latency_ms: float = 0.0
    error_rate: float = 0.0
    specialized_capabilities: dict[str, float] = (
        None  # e.g., {"creative": 0.9, "analytical": 0.7}
    )
    operational_status: str = "healthy"  # healthy, degraded, unavailable

    def __post_init__(self):
        if self.specialized_capabilities is None:
            self.specialized_capabilities = {"general": 0.8}


@dataclass
class EnsembleResult:
    """Result from ensemble model coordination."""

    synthesized_policy: str
    confidence_score: float
    contributing_models: list[str]
    ensemble_strategy_used: EnsembleStrategy
    performance_metrics: dict[str, Any]
    constitutional_fidelity: float
    wina_optimization_applied: bool
    synthesis_time_ms: float


class MultiModelCoordinator:
    """
    Advanced multi-model coordinator for Phase 2 AlphaEvolve-ACGS integration.

    Coordinates multiple LLM models for policy synthesis with WINA optimization,
    constitutional compliance monitoring, and adaptive performance optimization.
    """

    def __init__(self, config: dict[str, Any]):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """
        Initialize multi-model coordinator with enhanced routing capabilities.

        Args:
            config: Configuration dictionary with model settings
        """
        self.config = config
        self.primary_model = config.get("primary_model", "gemini-2.5-pro")
        self.fallback_models = config.get("fallback_models", ["gemini-2.0-flash"])
        self.ensemble_strategy = EnsembleStrategy(
            config.get("ensemble_strategy", "weighted_voting")
        )
        self.wina_optimization_enabled = config.get("wina_optimization_enabled", True)

        # Enhanced router optimization components
        self.request_classifier = RequestClassifier()
        self.cache_enabled = config.get("cache_enabled", True) and REDIS_AVAILABLE
        self.cache_ttl = config.get("cache_ttl", 3600)  # 1 hour default
        self.redis_client = None

        # Model performance tracking
        self.model_metrics: dict[str, ModelPerformanceMetrics] = {}
        self.ensemble_history: list[EnsembleResult] = []

        # Performance targets
        self.target_reliability = config.get("target_reliability", 0.999)
        self.target_constitutional_compliance = config.get(
            "target_constitutional_compliance", 0.85
        )
        self.target_response_time_ms = config.get("target_response_time_ms", 200)

        # Coordination state
        self._initialized = False
        self.active_models = set()

        # Enhanced model configurations with cost and capability data
        self.model_configs = {
            "gemini-2.5-pro": {
                "cost_per_token": 0.002,
                "capabilities": {
                    "analytical": 0.95,
                    "creative": 0.85,
                    "constitutional": 0.92,
                },
                "max_tokens": 8192,
            },
            "gemini-2.0-flash": {
                "cost_per_token": 0.0005,
                "capabilities": {
                    "analytical": 0.80,
                    "creative": 0.90,
                    "constitutional": 0.75,
                },
                "max_tokens": 4096,
            },
            "deepseek-r1": {
                "cost_per_token": 0.001,
                "capabilities": {
                    "analytical": 0.90,
                    "creative": 0.70,
                    "constitutional": 0.88,
                },
                "max_tokens": 6144,
            },
        }

    async def initialize(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Initialize the multi-model coordinator with enhanced capabilities."""
        if self._initialized:
            return

        try:
            # Initialize Redis cache if enabled
            if self.cache_enabled:
                try:
                    redis_url = self.config.get("redis_url", "redis://localhost:6379/0")
                    self.redis_client = redis.from_url(redis_url)
                    await self.redis_client.ping()
                    logger.info("Redis cache initialized successfully")
                except Exception as e:
                    logger.warning(f"Redis cache initialization failed: {e}")
                    self.cache_enabled = False

            # Initialize enhanced model performance metrics
            all_models = [self.primary_model, *self.fallback_models]
            for model_id in all_models:
                model_config = self.model_configs.get(model_id, {})

                self.model_metrics[model_id] = ModelPerformanceMetrics(
                    model_id=model_id,
                    synthesis_accuracy=0.95,  # Initial baseline
                    constitutional_compliance=0.85,
                    response_time_ms=150.0,
                    gflops_usage=1.0,
                    reliability_score=0.95,
                    last_updated=datetime.now(),
                    # Enhanced metrics
                    cost_per_token=model_config.get("cost_per_token", 0.001),
                    api_latency_ms=100.0,
                    error_rate=0.02,
                    specialized_capabilities=model_config.get(
                        "capabilities", {"general": 0.8}
                    ),
                    operational_status="healthy",
                )
                self.active_models.add(model_id)

            self._initialized = True
            logger.info(
                f"Enhanced multi-model coordinator initialized with {len(all_models)} models"
            )
            logger.info(f"Cache enabled: {self.cache_enabled}")

        except Exception as e:
            logger.exception(f"Failed to initialize multi-model coordinator: {e}")
            raise

    async def coordinate_synthesis(
        self, synthesis_request: dict[str, Any], enable_wina: bool = True
    ) -> EnsembleResult:
        """
        Enhanced multi-model policy synthesis with caching and adaptive routing.

        Args:
            synthesis_request: Policy synthesis request
            enable_wina: Whether to apply WINA optimization

        Returns:
            EnsembleResult with synthesized policy and metrics
        """
        if not self._initialized:
            await self.initialize()

        start_time = time.time()

        try:
            # Classify request complexity for adaptive routing
            request_complexity = self.request_classifier.classify_request(
                synthesis_request
            )
            logger.info(f"Request classified as: {request_complexity.value}")

            # Check cache first if enabled
            cache_key = None
            if self.cache_enabled and self.redis_client:
                cache_key = await self._generate_cache_key(
                    synthesis_request, request_complexity
                )
                cached_result = await self._get_cached_result(cache_key)
                if cached_result:
                    logger.info("Returning cached synthesis result")
                    return cached_result

            logger.info(
                f"Starting multi-model synthesis with strategy: {self.ensemble_strategy.value}"
            )

            # Select models based on request complexity and performance
            selected_models = await self._select_models_for_synthesis(
                synthesis_request, request_complexity
            )

            # Execute synthesis across selected models
            model_results = await self._execute_parallel_synthesis(
                synthesis_request, selected_models, enable_wina
            )

            # Apply ensemble strategy to combine results
            ensemble_result = await self._apply_ensemble_strategy(
                model_results, synthesis_request
            )

            # Update performance metrics
            await self._update_model_metrics(model_results, ensemble_result)

            # Calculate final metrics
            synthesis_time_ms = (time.time() - start_time) * 1000
            ensemble_result.synthesis_time_ms = synthesis_time_ms

            # Cache result if enabled
            if (
                self.cache_enabled
                and cache_key
                and ensemble_result.confidence_score > 0.8
            ):
                await self._cache_result(cache_key, ensemble_result)

            # Store in history
            self.ensemble_history.append(ensemble_result)
            if len(self.ensemble_history) > 1000:  # Keep last 1000 results
                self.ensemble_history.pop(0)

            logger.info(
                f"Multi-model synthesis completed in {synthesis_time_ms:.2f}ms "
                f"with confidence {ensemble_result.confidence_score:.3f}"
            )

            return ensemble_result

        except Exception as e:
            logger.exception(f"Multi-model synthesis failed: {e}")
            # Return fallback result
            return EnsembleResult(
                synthesized_policy="# Synthesis failed - fallback policy",
                confidence_score=0.0,
                contributing_models=[],
                ensemble_strategy_used=self.ensemble_strategy,
                performance_metrics={"error": str(e)},
                constitutional_fidelity=0.0,
                wina_optimization_applied=False,
                synthesis_time_ms=(time.time() - start_time) * 1000,
            )

    async def _select_models_for_synthesis(
        self, request: dict[str, Any], complexity: RequestComplexity = None
    ) -> list[str]:
        """Enhanced model selection with adaptive routing based on request complexity."""

        # Filter out unhealthy models
        healthy_models = {
            model_id: metrics
            for model_id, metrics in self.model_metrics.items()
            if metrics.operational_status == "healthy"
        }

        if not healthy_models:
            logger.warning("No healthy models available, using all models")
            healthy_models = self.model_metrics

        # Adaptive routing based on request complexity
        if complexity == RequestComplexity.SIMPLE:
            # Use single fast, cost-effective model
            cost_efficient = sorted(
                healthy_models.items(),
                key=lambda x: (x[1].cost_per_token, x[1].response_time_ms),
            )
            return [cost_efficient[0][0]] if cost_efficient else [self.primary_model]

        if complexity == RequestComplexity.HIGH_STAKES:
            # Use full ensemble with constitutional priority
            constitutional_sorted = sorted(
                healthy_models.items(),
                key=lambda x: x[1].constitutional_compliance,
                reverse=True,
            )
            return [model_id for model_id, _ in constitutional_sorted[:3]]

        # Complex requests - use ensemble strategy
        if self.ensemble_strategy == EnsembleStrategy.WEIGHTED_VOTING:
            # Select top performing models
            sorted_models = sorted(
                healthy_models.items(),
                key=lambda x: x[1].reliability_score,
                reverse=True,
            )
            return [model_id for model_id, _ in sorted_models[:3]]

        if self.ensemble_strategy == EnsembleStrategy.CONSTITUTIONAL_PRIORITY:
            # Prioritize models with high constitutional compliance
            sorted_models = sorted(
                healthy_models.items(),
                key=lambda x: x[1].constitutional_compliance,
                reverse=True,
            )
            return [model_id for model_id, _ in sorted_models[:2]]

        if self.ensemble_strategy == EnsembleStrategy.WINA_OPTIMIZED:
            # Select models optimized for WINA performance
            wina_optimized = [
                model_id
                for model_id, metrics in healthy_models.items()
                if metrics.gflops_usage < 0.7  # Models with good GFLOPs efficiency
            ]
            return wina_optimized[:2] if wina_optimized else [self.primary_model]

        # Default: use primary + one fallback
        return [self.primary_model, self.fallback_models[0]]

    async def _execute_parallel_synthesis(
        self, request: dict[str, Any], models: list[str], enable_wina: bool
    ) -> dict[str, dict[str, Any]]:
        """Execute synthesis in parallel across selected models."""
        tasks = []
        for model_id in models:
            task = self._synthesize_with_model(request, model_id, enable_wina)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        model_results = {}
        for i, result in enumerate(results):
            model_id = models[i]
            if isinstance(result, Exception):
                logger.warning(f"Model {model_id} synthesis failed: {result}")
                model_results[model_id] = {"error": str(result)}
            else:
                model_results[model_id] = result

        return model_results

    async def _synthesize_with_model(
        self, request: dict[str, Any], model_id: str, enable_wina: bool
    ) -> dict[str, Any]:
        """Synthesize policy using a specific model."""
        start_time = time.time()

        try:
            # This would integrate with actual model APIs
            # For now, we'll simulate the synthesis
            await asyncio.sleep(0.1)  # Simulate API call

            synthesis_time = (time.time() - start_time) * 1000

            # Simulate model-specific results
            if model_id == "gemini-2.5-pro":
                policy_content = f"""
                package acgs.governance.{model_id.replace("-", "_")}

                # High-quality policy synthesis from {model_id}
                default allow := false

                allow if {{
                    constitutional_compliance
                    governance_requirements_met
                }}

                constitutional_compliance if {{
                    input.constitutional_principles_verified == true
                    input.stakeholder_consensus >= 0.8
                }}
                """
                accuracy = 0.96
                constitutional_compliance = 0.92
            else:
                policy_content = f"""
                package acgs.governance.fallback

                # Fallback policy from {model_id}
                default allow := false

                allow if {{
                    basic_governance_check
                }}
                """
                accuracy = 0.88
                constitutional_compliance = 0.82

            return {
                "policy_content": policy_content,
                "model_id": model_id,
                "synthesis_time_ms": synthesis_time,
                "accuracy": accuracy,
                "constitutional_compliance": constitutional_compliance,
                "wina_optimization_applied": enable_wina,
                "gflops_reduction": 0.5 if enable_wina else 0.0,
            }

        except Exception as e:
            logger.exception(f"Synthesis with model {model_id} failed: {e}")
            raise

    async def _apply_ensemble_strategy(
        self, model_results: dict[str, dict[str, Any]], request: dict[str, Any]
    ) -> EnsembleResult:
        """Apply ensemble strategy to combine model results."""
        valid_results = {k: v for k, v in model_results.items() if "error" not in v}

        if not valid_results:
            raise Exception("No valid model results available")

        if self.ensemble_strategy == EnsembleStrategy.WEIGHTED_VOTING:
            return await self._weighted_voting_ensemble(valid_results)
        if self.ensemble_strategy == EnsembleStrategy.CONSTITUTIONAL_PRIORITY:
            return await self._constitutional_priority_ensemble(valid_results)
        # Default: select best performing result
        best_model = max(valid_results.items(), key=lambda x: x[1].get("accuracy", 0))
        result = best_model[1]

        return EnsembleResult(
            synthesized_policy=result["policy_content"],
            confidence_score=result.get("accuracy", 0.0),
            contributing_models=[result["model_id"]],
            ensemble_strategy_used=self.ensemble_strategy,
            performance_metrics=result,
            constitutional_fidelity=result.get("constitutional_compliance", 0.0),
            wina_optimization_applied=result.get("wina_optimization_applied", False),
            synthesis_time_ms=0.0,  # Will be set by caller
        )

    async def _weighted_voting_ensemble(
        self, results: dict[str, dict[str, Any]]
    ) -> EnsembleResult:
        """Apply weighted voting ensemble strategy."""
        # Calculate weights based on model performance
        total_weight = 0
        weighted_policies = []

        for model_id, result in results.items():
            metrics = self.model_metrics.get(model_id)
            if metrics:
                weight = metrics.reliability_score * metrics.constitutional_compliance
                total_weight += weight
                weighted_policies.append((result["policy_content"], weight, model_id))

        # Select policy with highest weight
        if weighted_policies:
            best_policy = max(weighted_policies, key=operator.itemgetter(1))

            return EnsembleResult(
                synthesized_policy=best_policy[0],
                confidence_score=(
                    best_policy[1] / total_weight if total_weight > 0 else 0.0
                ),
                contributing_models=[p[2] for p in weighted_policies],
                ensemble_strategy_used=EnsembleStrategy.WEIGHTED_VOTING,
                performance_metrics={
                    "total_weight": total_weight,
                    "model_count": len(weighted_policies),
                },
                constitutional_fidelity=sum(
                    r.get("constitutional_compliance", 0) for r in results.values()
                )
                / len(results),
                wina_optimization_applied=any(
                    r.get("wina_optimization_applied", False) for r in results.values()
                ),
                synthesis_time_ms=0.0,
            )

        # Fallback
        return await self._constitutional_priority_ensemble(results)

    async def _constitutional_priority_ensemble(
        self, results: dict[str, dict[str, Any]]
    ) -> EnsembleResult:
        """Apply constitutional priority ensemble strategy."""
        # Select result with highest constitutional compliance
        best_result = max(
            results.items(), key=lambda x: x[1].get("constitutional_compliance", 0)
        )
        result = best_result[1]

        return EnsembleResult(
            synthesized_policy=result["policy_content"],
            confidence_score=result.get("constitutional_compliance", 0.0),
            contributing_models=[result["model_id"]],
            ensemble_strategy_used=EnsembleStrategy.CONSTITUTIONAL_PRIORITY,
            performance_metrics=result,
            constitutional_fidelity=result.get("constitutional_compliance", 0.0),
            wina_optimization_applied=result.get("wina_optimization_applied", False),
            synthesis_time_ms=0.0,
        )

    async def _update_model_metrics(
        self, model_results: dict[str, dict[str, Any]], ensemble_result: EnsembleResult
    ):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Update model performance metrics based on results."""
        for model_id, result in model_results.items():
            if "error" not in result and model_id in self.model_metrics:
                metrics = self.model_metrics[model_id]

                # Update metrics with exponential moving average
                alpha = 0.1  # Learning rate
                metrics.synthesis_accuracy = (
                    1 - alpha
                ) * metrics.synthesis_accuracy + alpha * result.get("accuracy", 0)
                metrics.constitutional_compliance = (
                    1 - alpha
                ) * metrics.constitutional_compliance + alpha * result.get(
                    "constitutional_compliance", 0
                )
                metrics.response_time_ms = (
                    1 - alpha
                ) * metrics.response_time_ms + alpha * result.get(
                    "synthesis_time_ms", 0
                )
                metrics.gflops_usage = (1 - alpha) * metrics.gflops_usage + alpha * (
                    1.0 - result.get("gflops_reduction", 0)
                )

                # Calculate overall reliability score
                metrics.reliability_score = (
                    metrics.synthesis_accuracy * 0.4
                    + metrics.constitutional_compliance * 0.4
                    + (
                        1.0
                        - min(
                            metrics.response_time_ms / self.target_response_time_ms, 1.0
                        )
                    )
                    * 0.2
                )

                metrics.last_updated = datetime.now()

    async def _generate_cache_key(
        self, synthesis_request: dict[str, Any], complexity: RequestComplexity
    ) -> str:
        """Generate cache key for synthesis request."""
        # Create deterministic hash of request content and complexity
        request_str = json.dumps(synthesis_request, sort_keys=True)
        content = f"{request_str}:{complexity.value}:{self.ensemble_strategy.value}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    async def _get_cached_result(self, cache_key: str) -> EnsembleResult | None:
        """Retrieve cached synthesis result."""
        try:
            if not self.redis_client:
                return None

            cached_data = await self.redis_client.get(f"synthesis:{cache_key}")
            if cached_data:
                data = json.loads(cached_data)
                return EnsembleResult(
                    synthesized_policy=data["synthesized_policy"],
                    confidence_score=data["confidence_score"],
                    contributing_models=data["contributing_models"],
                    ensemble_strategy_used=EnsembleStrategy(
                        data["ensemble_strategy_used"]
                    ),
                    performance_metrics=data["performance_metrics"],
                    constitutional_fidelity=data["constitutional_fidelity"],
                    wina_optimization_applied=data["wina_optimization_applied"],
                    synthesis_time_ms=data["synthesis_time_ms"],
                )
        except Exception as e:
            logger.warning(f"Cache retrieval failed: {e}")
        return None

    async def _cache_result(self, cache_key: str, result: EnsembleResult):
        """Cache synthesis result."""
        try:
            if not self.redis_client:
                return

            cache_data = {
                "synthesized_policy": result.synthesized_policy,
                "confidence_score": result.confidence_score,
                "contributing_models": result.contributing_models,
                "ensemble_strategy_used": result.ensemble_strategy_used.value,
                "performance_metrics": result.performance_metrics,
                "constitutional_fidelity": result.constitutional_fidelity,
                "wina_optimization_applied": result.wina_optimization_applied,
                "synthesis_time_ms": result.synthesis_time_ms,
            }

            await self.redis_client.setex(
                f"synthesis:{cache_key}", self.cache_ttl, json.dumps(cache_data)
            )
        except Exception as e:
            logger.warning(f"Cache storage failed: {e}")

    def get_performance_summary(self) -> dict[str, Any]:
        """Get comprehensive performance summary with enhanced metrics."""
        if not self.ensemble_history:
            return {"status": "no_data"}

        recent_results = self.ensemble_history[-10:]  # Last 10 results

        return {
            "total_syntheses": len(self.ensemble_history),
            "recent_average_confidence": sum(r.confidence_score for r in recent_results)
            / len(recent_results),
            "recent_average_fidelity": sum(
                r.constitutional_fidelity for r in recent_results
            )
            / len(recent_results),
            "recent_average_time_ms": sum(r.synthesis_time_ms for r in recent_results)
            / len(recent_results),
            "wina_optimization_rate": sum(
                1 for r in recent_results if r.wina_optimization_applied
            )
            / len(recent_results),
            "cache_enabled": self.cache_enabled,
            "model_metrics": {
                model_id: {
                    "accuracy": metrics.synthesis_accuracy,
                    "compliance": metrics.constitutional_compliance,
                    "response_time": metrics.response_time_ms,
                    "reliability": metrics.reliability_score,
                    "cost_per_token": metrics.cost_per_token,
                    "error_rate": metrics.error_rate,
                    "operational_status": metrics.operational_status,
                    "capabilities": metrics.specialized_capabilities,
                }
                for model_id, metrics in self.model_metrics.items()
            },
            "target_achievement": {
                "reliability_target": self.target_reliability,
                "compliance_target": self.target_constitutional_compliance,
                "response_time_target": self.target_response_time_ms,
            },
        }
