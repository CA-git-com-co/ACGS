"""
Service Refactoring Example
Constitutional Hash: cdd01ef066bc6cf2

This module demonstrates how to refactor large service classes into smaller,
focused classes following the Single Responsibility Principle (SRP).

Example refactoring of the 810-line ConstitutionalComplianceService.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Protocol

from services.shared.configuration.settings import (
    get_constitutional_hash,
    get_performance_targets,
    validate_constitutional_compliance
)

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of constitutional validation."""
    
    is_valid: bool
    score: float
    violations: List[str]
    confidence: float
    evaluated_at: datetime
    performance_metrics: Dict[str, Any]


class PrincipleRepository(Protocol):
    """Protocol for principle repository."""
    
    async def find_by_tenant(self, tenant_id: str) -> List[Any]:
        """Find principles by tenant ID."""
        ...


class MetaRuleRepository(Protocol):
    """Protocol for meta-rule repository."""
    
    async def find_by_tenant(self, tenant_id: str) -> List[Any]:
        """Find meta-rules by tenant ID."""
        ...


class ConstitutionalValidator(ABC):
    """Abstract base class for constitutional validators."""
    
    @abstractmethod
    async def validate(self, action: Dict[str, Any], context: Dict[str, Any]) -> ValidationResult:
        """Validate constitutional compliance."""
        ...


class PrincipleEvaluator:
    """
    Focused class for evaluating individual principles.
    
    Single Responsibility: Evaluate how well an action adheres to specific principles.
    """
    
    def __init__(self):
        self.performance_targets = get_performance_targets()
        self.constitutional_hash = get_constitutional_hash()
    
    async def evaluate_principle(
        self, 
        principle: Any, 
        action: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> float:
        """
        Evaluate a single principle against an action.
        
        Args:
            principle: The principle to evaluate
            action: The action being evaluated
            context: The context of the action
            
        Returns:
            float: Score between 0.0 and 1.0
        """
        start_time = asyncio.get_event_loop().time()
        
        # Simplified evaluation logic
        score = await self._calculate_principle_score(principle, action, context)
        
        elapsed = asyncio.get_event_loop().time() - start_time
        
        # Log performance metrics
        logger.debug(
            f"Principle evaluation completed in {elapsed*1000:.2f}ms "
            f"(target: <{self.performance_targets['p99_latency_ms']}ms)"
        )
        
        return score
    
    async def _calculate_principle_score(
        self, 
        principle: Any, 
        action: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> float:
        """Calculate principle score (implementation-specific)."""
        # This would contain the actual evaluation logic
        await asyncio.sleep(0.001)  # Simulate processing
        return 0.85  # Example score


class ConflictResolver:
    """
    Focused class for resolving conflicts between principles.
    
    Single Responsibility: Detect and resolve conflicts between principles.
    """
    
    def __init__(self, meta_rule_repository: MetaRuleRepository):
        self.meta_rule_repo = meta_rule_repository
        self.constitutional_hash = get_constitutional_hash()
    
    async def resolve_conflicts(
        self, 
        principle_scores: Dict[str, float], 
        tenant_id: str
    ) -> Dict[str, float]:
        """
        Resolve conflicts between principles.
        
        Args:
            principle_scores: Scores for each principle
            tenant_id: Tenant identifier
            
        Returns:
            Dict with resolved scores
        """
        start_time = asyncio.get_event_loop().time()
        
        # Detect conflicts
        conflicts = await self._detect_conflicts(principle_scores)
        
        if not conflicts:
            return principle_scores
        
        # Apply meta-rules to resolve conflicts
        resolved_scores = await self._apply_meta_rules(
            principle_scores, conflicts, tenant_id
        )
        
        elapsed = asyncio.get_event_loop().time() - start_time
        logger.debug(f"Conflict resolution completed in {elapsed*1000:.2f}ms")
        
        return resolved_scores
    
    async def _detect_conflicts(self, scores: Dict[str, float]) -> List[str]:
        """Detect conflicts between principles."""
        conflicts = []
        
        # Simple conflict detection logic
        for principle_name, score in scores.items():
            if score < 0.5:  # Threshold for conflict
                conflicts.append(principle_name)
        
        return conflicts
    
    async def _apply_meta_rules(
        self, 
        scores: Dict[str, float], 
        conflicts: List[str], 
        tenant_id: str
    ) -> Dict[str, float]:
        """Apply meta-rules to resolve conflicts."""
        meta_rules = await self.meta_rule_repo.find_by_tenant(tenant_id)
        
        resolved_scores = scores.copy()
        
        # Apply resolution logic
        for conflict in conflicts:
            if conflict in resolved_scores:
                # Example: Boost score by 0.1 if meta-rule applies
                resolved_scores[conflict] = min(1.0, resolved_scores[conflict] + 0.1)
        
        return resolved_scores


class ComplianceScoreCalculator:
    """
    Focused class for calculating final compliance scores.
    
    Single Responsibility: Calculate weighted compliance scores.
    """
    
    def __init__(self):
        self.constitutional_hash = get_constitutional_hash()
        self.performance_targets = get_performance_targets()
    
    async def calculate_final_score(
        self, 
        principle_scores: Dict[str, float], 
        weights: Optional[Dict[str, float]] = None
    ) -> float:
        """
        Calculate final weighted compliance score.
        
        Args:
            principle_scores: Scores for each principle
            weights: Optional weights for each principle
            
        Returns:
            float: Final compliance score
        """
        start_time = asyncio.get_event_loop().time()
        
        if not principle_scores:
            return 0.0
        
        # Use equal weights if not provided
        if weights is None:
            weights = {name: 1.0 for name in principle_scores.keys()}
        
        # Calculate weighted average
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for principle_name, score in principle_scores.items():
            weight = weights.get(principle_name, 1.0)
            total_weighted_score += score * weight
            total_weight += weight
        
        final_score = total_weighted_score / total_weight if total_weight > 0 else 0.0
        
        elapsed = asyncio.get_event_loop().time() - start_time
        logger.debug(f"Score calculation completed in {elapsed*1000:.2f}ms")
        
        return final_score


class OptimizedConstitutionalComplianceService(ConstitutionalValidator):
    """
    Refactored constitutional compliance service.
    
    This service demonstrates the improved architecture with:
    - Single Responsibility Principle
    - Dependency Injection
    - Focused classes
    - Better performance monitoring
    - Reduced complexity
    """
    
    def __init__(
        self,
        principle_repository: PrincipleRepository,
        meta_rule_repository: MetaRuleRepository,
        principle_evaluator: Optional[PrincipleEvaluator] = None,
        conflict_resolver: Optional[ConflictResolver] = None,
        score_calculator: Optional[ComplianceScoreCalculator] = None,
    ):
        """Initialize with dependencies."""
        self.principle_repo = principle_repository
        self.meta_rule_repo = meta_rule_repository
        
        # Use dependency injection or create default instances
        self.principle_evaluator = principle_evaluator or PrincipleEvaluator()
        self.conflict_resolver = conflict_resolver or ConflictResolver(meta_rule_repository)
        self.score_calculator = score_calculator or ComplianceScoreCalculator()
        
        # Ensure constitutional compliance
        validate_constitutional_compliance()
        
        logger.info("OptimizedConstitutionalComplianceService initialized")
    
    async def validate(
        self, 
        action: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate constitutional compliance with optimized architecture.
        
        Args:
            action: Action to validate
            context: Context of the action
            
        Returns:
            ValidationResult with validation details
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # 1. Get applicable principles
            tenant_id = context.get('tenant_id', 'default')
            principles = await self.principle_repo.find_by_tenant(tenant_id)
            
            # 2. Evaluate each principle
            principle_scores = {}
            violations = []
            
            for principle in principles:
                score = await self.principle_evaluator.evaluate_principle(
                    principle, action, context
                )
                principle_scores[principle.name] = score
                
                if score < 0.5:  # Violation threshold
                    violations.append(f"Principle '{principle.name}' violated (score: {score:.2f})")
            
            # 3. Resolve conflicts
            resolved_scores = await self.conflict_resolver.resolve_conflicts(
                principle_scores, tenant_id
            )
            
            # 4. Calculate final score
            final_score = await self.score_calculator.calculate_final_score(
                resolved_scores
            )
            
            # 5. Calculate confidence
            confidence = self._calculate_confidence(resolved_scores)
            
            elapsed = asyncio.get_event_loop().time() - start_time
            
            # Performance metrics
            performance_metrics = {
                'total_time_ms': elapsed * 1000,
                'principles_evaluated': len(principles),
                'violations_found': len(violations),
                'final_score': final_score,
                'confidence': confidence,
                'meets_latency_target': elapsed * 1000 < self.principle_evaluator.performance_targets['p99_latency_ms']
            }
            
            logger.info(
                f"Constitutional validation completed in {elapsed*1000:.2f}ms "
                f"(score: {final_score:.2f}, violations: {len(violations)})"
            )
            
            return ValidationResult(
                is_valid=final_score >= 0.7,  # Compliance threshold
                score=final_score,
                violations=violations,
                confidence=confidence,
                evaluated_at=datetime.utcnow(),
                performance_metrics=performance_metrics
            )
            
        except Exception as e:
            logger.error(f"Constitutional validation failed: {e}")
            elapsed = asyncio.get_event_loop().time() - start_time
            
            return ValidationResult(
                is_valid=False,
                score=0.0,
                violations=[f"Validation error: {str(e)}"],
                confidence=0.0,
                evaluated_at=datetime.utcnow(),
                performance_metrics={
                    'total_time_ms': elapsed * 1000,
                    'error': str(e)
                }
            )
    
    def _calculate_confidence(self, scores: Dict[str, float]) -> float:
        """Calculate confidence interval for the validation."""
        if not scores:
            return 0.0
        
        # Simple confidence calculation based on score variance
        values = list(scores.values())
        mean_score = sum(values) / len(values)
        variance = sum((x - mean_score) ** 2 for x in values) / len(values)
        
        # Higher variance = lower confidence
        confidence = max(0.0, 1.0 - variance)
        return confidence


# Performance monitoring decorator
def monitor_performance(func):
    """Decorator to monitor service performance."""
    async def wrapper(*args, **kwargs):
        start_time = asyncio.get_event_loop().time()
        
        try:
            result = await func(*args, **kwargs)
            
            elapsed = asyncio.get_event_loop().time() - start_time
            targets = get_performance_targets()
            
            logger.info(
                f"{func.__name__} completed in {elapsed*1000:.2f}ms "
                f"(target: <{targets['p99_latency_ms']}ms)"
            )
            
            return result
            
        except Exception as e:
            elapsed = asyncio.get_event_loop().time() - start_time
            logger.error(f"{func.__name__} failed after {elapsed*1000:.2f}ms: {e}")
            raise
    
    return wrapper


# Example usage
async def example_usage():
    """Example usage of the refactored service."""
    
    # Mock repositories (in real implementation, these would be actual repositories)
    class MockPrincipleRepository:
        async def find_by_tenant(self, tenant_id: str):
            # Mock principle objects
            class MockPrinciple:
                def __init__(self, name):
                    self.name = name
            
            return [
                MockPrinciple("fairness"),
                MockPrinciple("transparency"), 
                MockPrinciple("accountability")
            ]
    
    class MockMetaRuleRepository:
        async def find_by_tenant(self, tenant_id: str):
            return []  # Mock meta-rules
    
    # Create service with dependency injection
    service = OptimizedConstitutionalComplianceService(
        principle_repository=MockPrincipleRepository(),
        meta_rule_repository=MockMetaRuleRepository()
    )
    
    # Example validation
    action = {"type": "decision", "impact": "high"}
    context = {"tenant_id": "example_tenant", "user_id": "user123"}
    
    result = await service.validate(action, context)
    
    print(f"Validation Result:")
    print(f"  Valid: {result.is_valid}")
    print(f"  Score: {result.score:.2f}")
    print(f"  Violations: {len(result.violations)}")
    print(f"  Confidence: {result.confidence:.2f}")
    print(f"  Performance: {result.performance_metrics}")


if __name__ == "__main__":
    asyncio.run(example_usage())