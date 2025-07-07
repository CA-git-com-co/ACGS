"""
Fitness Service Module

Specialized service for fitness evaluation with constitutional compliance,
performance optimization, and automated scoring for evolutionary computation.
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, Tuple

import redis.asyncio as aioredis
from prometheus_client import Counter, Histogram

from ..models.evolution import FitnessMetrics, Individual
from ..core.constitutional_validator import ConstitutionalValidator

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


class FitnessService:
    """
    Specialized fitness evaluation service with constitutional compliance.
    
    Provides automated fitness scoring with O(1) lookup patterns and
    sub-5ms P99 latency targets for optimal ACGS performance.
    """
    
    def __init__(self, redis_client: Optional[aioredis.Redis] = None):
        """Initialize fitness service."""
        self.redis = redis_client
        self.constitutional_validator = ConstitutionalValidator()
        
        self.setup_metrics()
        
        # Fitness evaluation cache for O(1) lookups
        self.fitness_cache: Dict[str, FitnessMetrics] = {}
        self.evaluation_cache: Dict[str, Dict[str, float]] = {}
        
        # Fitness evaluation weights (configurable)
        self.fitness_weights = {
            "constitutional_compliance": 0.30,
            "performance_score": 0.20,
            "safety_score": 0.10,
            "fairness_score": 0.10,
            "efficiency_score": 0.10,
            "robustness_score": 0.10,
            "transparency_score": 0.05,
            "user_satisfaction": 0.05
        }
        
        logger.info("FitnessService initialized with constitutional compliance")
    
    def setup_metrics(self) -> None:
        """Setup Prometheus metrics."""
        self.fitness_evaluations_total = Counter(
            "fitness_evaluations_total",
            "Total fitness evaluations",
            ["evaluation_type", "status"]
        )
        
        self.fitness_evaluation_duration = Histogram(
            "fitness_evaluation_duration_ms",
            "Fitness evaluation duration in milliseconds",
            ["evaluation_component"]
        )
        
        self.fitness_score_histogram = Histogram(
            "fitness_score_distribution",
            "Distribution of fitness scores",
            ["score_type"],
            buckets=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        )
    
    async def evaluate_comprehensive_fitness(self, individual: Individual) -> FitnessMetrics:
        """
        Perform comprehensive fitness evaluation with constitutional compliance.
        
        Args:
            individual: Individual to evaluate
            
        Returns:
            Comprehensive fitness metrics
        """
        start_time = time.time()
        
        try:
            # Check cache first for O(1) performance
            cache_key = self._get_fitness_cache_key(individual.genotype)
            if cache_key in self.fitness_cache:
                cached_metrics = self.fitness_cache[cache_key]
                self.fitness_evaluations_total.labels(
                    evaluation_type="comprehensive",
                    status="cached"
                ).inc()
                return cached_metrics
            
            # Perform parallel evaluation of all fitness components
            evaluation_tasks = [
                self._evaluate_constitutional_compliance(individual),
                self._evaluate_performance(individual),
                self._evaluate_safety(individual),
                self._evaluate_fairness(individual),
                self._evaluate_efficiency(individual),
                self._evaluate_robustness(individual),
                self._evaluate_transparency(individual),
                self._evaluate_user_satisfaction(individual)
            ]
            
            # Execute evaluations in parallel for optimal performance
            results = await asyncio.gather(*evaluation_tasks, return_exceptions=True)
            
            # Extract scores (handle exceptions)
            scores = {}
            component_names = [
                "constitutional_compliance", "performance_score", "safety_score",
                "fairness_score", "efficiency_score", "robustness_score",
                "transparency_score", "user_satisfaction"
            ]
            
            for i, (component, result) in enumerate(zip(component_names, results)):
                if isinstance(result, Exception):
                    logger.warning(f"Fitness evaluation failed for {component}: {result}")
                    scores[component] = 0.0  # Fail-safe score
                else:
                    scores[component] = min(1.0, max(0.0, result))  # Clamp to [0,1]
            
            # Calculate weighted overall fitness
            overall_fitness = sum(
                scores[component] * self.fitness_weights[component]
                for component in component_names
            )
            
            # Create fitness metrics
            fitness_metrics = FitnessMetrics(
                constitutional_compliance=scores["constitutional_compliance"],
                performance_score=scores["performance_score"],
                safety_score=scores["safety_score"],
                fairness_score=scores["fairness_score"],
                efficiency_score=scores["efficiency_score"],
                robustness_score=scores["robustness_score"],
                transparency_score=scores["transparency_score"],
                user_satisfaction=scores["user_satisfaction"],
                overall_fitness=overall_fitness,
                constitutional_hash=CONSTITUTIONAL_HASH
            )
            
            # Cache result for future O(1) lookups
            self.fitness_cache[cache_key] = fitness_metrics
            
            # Cache in Redis if available
            if self.redis:
                await self.redis.setex(
                    f"fitness:{cache_key}",
                    1800,  # 30 minute TTL
                    fitness_metrics.json()
                )
            
            # Record metrics
            self.fitness_evaluations_total.labels(
                evaluation_type="comprehensive",
                status="success"
            ).inc()
            
            for component, score in scores.items():
                self.fitness_score_histogram.labels(score_type=component).observe(score)
            
            self.fitness_score_histogram.labels(score_type="overall").observe(overall_fitness)
            
            return fitness_metrics
            
        except Exception as e:
            logger.error(f"Comprehensive fitness evaluation failed: {e}")
            self.fitness_evaluations_total.labels(
                evaluation_type="comprehensive",
                status="error"
            ).inc()
            
            # Return fail-safe fitness metrics
            return FitnessMetrics(
                constitutional_compliance=0.0,
                performance_score=0.0,
                safety_score=0.0,
                fairness_score=0.0,
                efficiency_score=0.0,
                robustness_score=0.0,
                transparency_score=0.0,
                user_satisfaction=0.0,
                overall_fitness=0.0,
                constitutional_hash=CONSTITUTIONAL_HASH
            )
            
        finally:
            duration = (time.time() - start_time) * 1000
            self.fitness_evaluation_duration.labels(
                evaluation_component="comprehensive"
            ).observe(duration)
            
            # Ensure sub-5ms P99 latency target
            if duration > 5:
                logger.warning(f"Comprehensive fitness evaluation took {duration:.2f}ms (>5ms target)")
    
    async def evaluate_quick_fitness(self, individual: Individual) -> float:
        """
        Perform quick fitness evaluation for performance-critical scenarios.
        
        Args:
            individual: Individual to evaluate
            
        Returns:
            Quick fitness score (0.0 to 1.0)
        """
        start_time = time.time()
        
        try:
            # Quick evaluation focusing on key metrics
            constitutional_score = await self.constitutional_validator.validate_individual(individual)
            performance_score = await self._evaluate_performance_quick(individual)
            safety_score = await self._evaluate_safety_quick(individual)
            
            # Weighted quick score
            quick_fitness = (
                constitutional_score * 0.5 +
                performance_score * 0.3 +
                safety_score * 0.2
            )
            
            self.fitness_evaluations_total.labels(
                evaluation_type="quick",
                status="success"
            ).inc()
            
            return quick_fitness
            
        except Exception as e:
            logger.error(f"Quick fitness evaluation failed: {e}")
            self.fitness_evaluations_total.labels(
                evaluation_type="quick",
                status="error"
            ).inc()
            return 0.0
            
        finally:
            duration = (time.time() - start_time) * 1000
            self.fitness_evaluation_duration.labels(
                evaluation_component="quick"
            ).observe(duration)
    
    async def _evaluate_constitutional_compliance(self, individual: Individual) -> float:
        """Evaluate constitutional compliance score."""
        start_time = time.time()
        
        try:
            score = await self.constitutional_validator.validate_individual(individual)
            return score
            
        finally:
            duration = (time.time() - start_time) * 1000
            self.fitness_evaluation_duration.labels(
                evaluation_component="constitutional"
            ).observe(duration)
    
    async def _evaluate_performance(self, individual: Individual) -> float:
        """Evaluate performance score."""
        # Simplified performance evaluation
        genotype = individual.genotype
        
        # Performance indicators
        efficiency = genotype.get("efficiency", 0.8)
        speed = genotype.get("speed", 0.85)
        accuracy = genotype.get("accuracy", 0.9)
        scalability = genotype.get("scalability", 0.75)
        
        # Weighted performance score
        performance_score = (
            efficiency * 0.3 +
            speed * 0.3 +
            accuracy * 0.3 +
            scalability * 0.1
        )
        
        return min(1.0, max(0.0, performance_score))
    
    async def _evaluate_performance_quick(self, individual: Individual) -> float:
        """Quick performance evaluation."""
        genotype = individual.genotype
        return genotype.get("performance_score", 0.8)
    
    async def _evaluate_safety(self, individual: Individual) -> float:
        """Evaluate safety score."""
        genotype = individual.genotype
        
        # Safety indicators
        harm_prevention = 1.0 - genotype.get("harm_potential", 0.1)
        risk_mitigation = genotype.get("risk_mitigation", 0.9)
        fail_safe = genotype.get("fail_safe", 0.85)
        
        safety_score = (harm_prevention + risk_mitigation + fail_safe) / 3
        return min(1.0, max(0.0, safety_score))
    
    async def _evaluate_safety_quick(self, individual: Individual) -> float:
        """Quick safety evaluation."""
        genotype = individual.genotype
        return genotype.get("safety_score", 0.9)
    
    async def _evaluate_fairness(self, individual: Individual) -> float:
        """Evaluate fairness score."""
        genotype = individual.genotype
        
        bias_score = 1.0 - genotype.get("bias_level", 0.1)
        equal_treatment = genotype.get("equal_treatment", 0.9)
        non_discrimination = genotype.get("non_discrimination", 0.95)
        
        fairness_score = (bias_score + equal_treatment + non_discrimination) / 3
        return min(1.0, max(0.0, fairness_score))
    
    async def _evaluate_efficiency(self, individual: Individual) -> float:
        """Evaluate efficiency score."""
        genotype = individual.genotype
        
        resource_usage = 1.0 - genotype.get("resource_consumption", 0.3)
        time_efficiency = genotype.get("time_efficiency", 0.8)
        energy_efficiency = genotype.get("energy_efficiency", 0.85)
        
        efficiency_score = (resource_usage + time_efficiency + energy_efficiency) / 3
        return min(1.0, max(0.0, efficiency_score))
    
    async def _evaluate_robustness(self, individual: Individual) -> float:
        """Evaluate robustness score."""
        genotype = individual.genotype
        
        error_handling = genotype.get("error_handling", 0.8)
        fault_tolerance = genotype.get("fault_tolerance", 0.85)
        adaptability = genotype.get("adaptability", 0.75)
        
        robustness_score = (error_handling + fault_tolerance + adaptability) / 3
        return min(1.0, max(0.0, robustness_score))
    
    async def _evaluate_transparency(self, individual: Individual) -> float:
        """Evaluate transparency score."""
        genotype = individual.genotype
        
        explainability = genotype.get("explainability", 0.7)
        auditability = genotype.get("auditability", 0.8)
        interpretability = genotype.get("interpretability", 0.75)
        
        transparency_score = (explainability + auditability + interpretability) / 3
        return min(1.0, max(0.0, transparency_score))
    
    async def _evaluate_user_satisfaction(self, individual: Individual) -> float:
        """Evaluate user satisfaction score."""
        genotype = individual.genotype
        
        # Placeholder for user satisfaction - would integrate with feedback systems
        usability = genotype.get("usability", 0.8)
        user_experience = genotype.get("user_experience", 0.85)
        
        satisfaction_score = (usability + user_experience) / 2
        return min(1.0, max(0.0, satisfaction_score))
    
    def _get_fitness_cache_key(self, genotype: Dict[str, Any]) -> str:
        """Generate cache key for fitness evaluation."""
        import hashlib
        import json
        
        genotype_str = json.dumps(genotype, sort_keys=True)
        return hashlib.md5(genotype_str.encode()).hexdigest()
