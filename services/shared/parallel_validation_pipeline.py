#!/usr/bin/env python3
"""
Parallel Validation Pipeline for ACGS-PGP

Implements concurrent validation stages from GEMINI.md analysis to achieve
sub-2s response time guarantee while maintaining constitutional compliance >95%.

Pipeline Stages (Concurrent):
1. Syntax Validation - Basic structure and format checks
2. Semantic Validation - Content meaning and context analysis  
3. Constitutional Rules Compliance - Full constitutional AI validation

Architecture:
- Concurrent execution of all validation stages
- Multi-level caching integration for performance
- Aggregated results with confidence scoring
- Circuit breaker for cascade failure prevention
- Constitutional hash integrity maintenance
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from services.shared.multi_level_cache import get_cache_manager, MultiLevelCacheManager
from services.shared.utils import get_config

logger = logging.getLogger(__name__)


class ValidationStage(Enum):
    """Validation pipeline stages."""
    SYNTAX = "syntax"
    SEMANTIC = "semantic"
    CONSTITUTIONAL = "constitutional"


class ValidationResult(Enum):
    """Validation result types."""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class StageResult:
    """Result from individual validation stage."""
    stage: ValidationStage
    result: ValidationResult
    confidence: float
    execution_time_ms: float
    details: Dict[str, Any] = field(default_factory=dict)
    violations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class PipelineResult:
    """Aggregated result from parallel validation pipeline."""
    overall_result: ValidationResult
    overall_confidence: float
    total_execution_time_ms: float
    stage_results: List[StageResult]
    constitutional_hash: str
    cache_hit: bool = False
    cache_level: Optional[str] = None
    
    def is_compliant(self) -> bool:
        """Check if validation result indicates compliance."""
        return self.overall_result in [ValidationResult.PASS, ValidationResult.WARNING]
    
    def get_violations(self) -> List[str]:
        """Get all violations from all stages."""
        violations = []
        for stage_result in self.stage_results:
            violations.extend(stage_result.violations)
        return violations


class CircuitBreaker:
    """Circuit breaker for cascade failure prevention."""
    
    def __init__(self, failure_threshold: int = 100, recovery_timeout: int = 30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "closed"  # closed, open, half_open
    
    def can_execute(self) -> bool:
        """Check if execution is allowed."""
        if self.state == "closed":
            return True
        elif self.state == "open":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "half_open"
                return True
            return False
        else:  # half_open
            return True
    
    def record_success(self):
        """Record successful execution."""
        self.failure_count = 0
        self.state = "closed"
    
    def record_failure(self):
        """Record failed execution."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")


class SyntaxValidator:
    """Syntax validation stage - basic structure and format checks."""
    
    def __init__(self):
        self.circuit_breaker = CircuitBreaker()
    
    async def validate(self, content: str, context: Dict[str, Any]) -> StageResult:
        """Perform syntax validation."""
        start_time = time.time()
        
        if not self.circuit_breaker.can_execute():
            return StageResult(
                stage=ValidationStage.SYNTAX,
                result=ValidationResult.ERROR,
                confidence=0.0,
                execution_time_ms=0.0,
                details={"error": "Circuit breaker open"}
            )
        
        try:
            violations = []
            warnings = []
            
            # Basic syntax checks
            if not content or not content.strip():
                violations.append("Empty content")
            
            if len(content) > 100000:  # 100KB limit
                violations.append("Content too large")
            
            # Check for basic structure
            if not any(char.isalpha() for char in content):
                warnings.append("No alphabetic characters found")
            
            # Check encoding
            try:
                content.encode('utf-8')
            except UnicodeEncodeError:
                violations.append("Invalid UTF-8 encoding")
            
            # Determine result
            if violations:
                result = ValidationResult.FAIL
                confidence = 0.0
            elif warnings:
                result = ValidationResult.WARNING
                confidence = 0.8
            else:
                result = ValidationResult.PASS
                confidence = 1.0
            
            execution_time = (time.time() - start_time) * 1000
            
            self.circuit_breaker.record_success()
            
            return StageResult(
                stage=ValidationStage.SYNTAX,
                result=result,
                confidence=confidence,
                execution_time_ms=execution_time,
                details={
                    "content_length": len(content),
                    "word_count": len(content.split()),
                    "line_count": len(content.splitlines())
                },
                violations=violations,
                warnings=warnings
            )
            
        except Exception as e:
            self.circuit_breaker.record_failure()
            execution_time = (time.time() - start_time) * 1000
            
            return StageResult(
                stage=ValidationStage.SYNTAX,
                result=ValidationResult.ERROR,
                confidence=0.0,
                execution_time_ms=execution_time,
                details={"error": str(e)},
                violations=[f"Syntax validation error: {e}"]
            )


class SemanticValidator:
    """Semantic validation stage - content meaning and context analysis."""
    
    def __init__(self):
        self.circuit_breaker = CircuitBreaker()
    
    async def validate(self, content: str, context: Dict[str, Any]) -> StageResult:
        """Perform semantic validation."""
        start_time = time.time()
        
        if not self.circuit_breaker.can_execute():
            return StageResult(
                stage=ValidationStage.SEMANTIC,
                result=ValidationResult.ERROR,
                confidence=0.0,
                execution_time_ms=0.0,
                details={"error": "Circuit breaker open"}
            )
        
        try:
            violations = []
            warnings = []
            
            # Semantic analysis
            words = content.lower().split()
            
            # Check for meaningful content
            if len(words) < 3:
                warnings.append("Very short content")
            
            # Check for repetitive content
            unique_words = set(words)
            if len(unique_words) < len(words) * 0.3:
                warnings.append("Highly repetitive content")
            
            # Check for context relevance
            if context.get("expected_topic"):
                topic_keywords = context["expected_topic"].lower().split()
                if not any(keyword in content.lower() for keyword in topic_keywords):
                    warnings.append("Content may not match expected topic")
            
            # Check for coherence (simplified)
            sentences = content.split('.')
            if len(sentences) > 10:
                avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
                if avg_sentence_length < 3:
                    warnings.append("Very short sentences may indicate poor coherence")
            
            # Determine result
            if violations:
                result = ValidationResult.FAIL
                confidence = 0.0
            elif warnings:
                result = ValidationResult.WARNING
                confidence = 0.7
            else:
                result = ValidationResult.PASS
                confidence = 0.9
            
            execution_time = (time.time() - start_time) * 1000
            
            self.circuit_breaker.record_success()
            
            return StageResult(
                stage=ValidationStage.SEMANTIC,
                result=result,
                confidence=confidence,
                execution_time_ms=execution_time,
                details={
                    "word_count": len(words),
                    "unique_words": len(unique_words),
                    "sentence_count": len(sentences),
                    "vocabulary_diversity": len(unique_words) / len(words) if words else 0
                },
                violations=violations,
                warnings=warnings
            )
            
        except Exception as e:
            self.circuit_breaker.record_failure()
            execution_time = (time.time() - start_time) * 1000
            
            return StageResult(
                stage=ValidationStage.SEMANTIC,
                result=ValidationResult.ERROR,
                confidence=0.0,
                execution_time_ms=execution_time,
                details={"error": str(e)},
                violations=[f"Semantic validation error: {e}"]
            )


class ConstitutionalValidator:
    """Constitutional validation stage - full constitutional AI compliance."""
    
    def __init__(self, cache_manager: MultiLevelCacheManager):
        self.cache_manager = cache_manager
        self.circuit_breaker = CircuitBreaker()
        self.constitutional_hash = "cdd01ef066bc6cf2"
    
    async def validate(self, content: str, context: Dict[str, Any]) -> StageResult:
        """Perform constitutional validation with caching."""
        start_time = time.time()
        
        if not self.circuit_breaker.can_execute():
            return StageResult(
                stage=ValidationStage.CONSTITUTIONAL,
                result=ValidationResult.ERROR,
                confidence=0.0,
                execution_time_ms=0.0,
                details={"error": "Circuit breaker open"}
            )
        
        try:
            # Use cache manager for constitutional ruling
            cache_result = await self.cache_manager.get_constitutional_ruling(
                "constitutional_validation", content, context
            )
            
            execution_time = (time.time() - start_time) * 1000
            
            # Convert cache result to stage result
            if cache_result.get("result", {}).get("compliant", False):
                result = ValidationResult.PASS
                violations = []
            else:
                result = ValidationResult.FAIL
                violations = cache_result.get("result", {}).get("violations", ["Constitutional violation detected"])
            
            confidence = cache_result.get("confidence_score", 0.95)
            
            self.circuit_breaker.record_success()
            
            return StageResult(
                stage=ValidationStage.CONSTITUTIONAL,
                result=result,
                confidence=confidence,
                execution_time_ms=execution_time,
                details={
                    "constitutional_hash": self.constitutional_hash,
                    "cache_level": cache_result.get("cache_level"),
                    "cached": cache_result.get("cache_level") is not None,
                    "reasoning": cache_result.get("result", {}).get("reasoning", "")
                },
                violations=violations
            )
            
        except Exception as e:
            self.circuit_breaker.record_failure()
            execution_time = (time.time() - start_time) * 1000
            
            return StageResult(
                stage=ValidationStage.CONSTITUTIONAL,
                result=ValidationResult.ERROR,
                confidence=0.0,
                execution_time_ms=execution_time,
                details={"error": str(e)},
                violations=[f"Constitutional validation error: {e}"]
            )


class ParallelValidationPipeline:
    """
    Parallel validation pipeline orchestrating concurrent validation stages.
    
    Implements the validation strategy from GEMINI.md analysis to achieve
    sub-2s response time guarantee with constitutional compliance >95%.
    """
    
    def __init__(self, cache_manager: Optional[MultiLevelCacheManager] = None):
        self.cache_manager = cache_manager
        self.config = get_config()
        
        # Initialize validators
        self.syntax_validator = SyntaxValidator()
        self.semantic_validator = SemanticValidator()
        self.constitutional_validator = None  # Will be initialized async
        
        # Performance tracking
        self.total_validations = 0
        self.total_execution_time = 0.0
        self.compliance_rate = 0.0
        
        logger.info("Parallel validation pipeline initialized")
    
    async def initialize(self):
        """Initialize async components."""
        if not self.cache_manager:
            self.cache_manager = await get_cache_manager()
        
        self.constitutional_validator = ConstitutionalValidator(self.cache_manager)
        
        logger.info("Parallel validation pipeline ready")
    
    async def validate(self, content: str, context: Optional[Dict[str, Any]] = None) -> PipelineResult:
        """
        Execute parallel validation pipeline.
        
        Runs syntax, semantic, and constitutional validation concurrently
        and aggregates results with confidence scoring.
        """
        start_time = time.time()
        context = context or {}
        
        # Execute all validation stages concurrently
        tasks = [
            self.syntax_validator.validate(content, context),
            self.semantic_validator.validate(content, context),
            self.constitutional_validator.validate(content, context)
        ]
        
        stage_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions
        processed_results = []
        for i, result in enumerate(stage_results):
            if isinstance(result, Exception):
                stage = [ValidationStage.SYNTAX, ValidationStage.SEMANTIC, ValidationStage.CONSTITUTIONAL][i]
                processed_results.append(StageResult(
                    stage=stage,
                    result=ValidationResult.ERROR,
                    confidence=0.0,
                    execution_time_ms=0.0,
                    violations=[f"Stage execution error: {result}"]
                ))
            else:
                processed_results.append(result)
        
        # Aggregate results
        total_execution_time = (time.time() - start_time) * 1000
        aggregated_result = self._aggregate_results(processed_results, total_execution_time)
        
        # Update performance metrics
        self._update_metrics(aggregated_result)
        
        logger.debug(f"Parallel validation completed: {aggregated_result.overall_result.value} "
                    f"({total_execution_time:.2f}ms, confidence: {aggregated_result.overall_confidence:.3f})")
        
        return aggregated_result
    
    def _aggregate_results(self, stage_results: List[StageResult], total_time: float) -> PipelineResult:
        """Aggregate results from all validation stages."""
        # Determine overall result based on stage results
        has_errors = any(r.result == ValidationResult.ERROR for r in stage_results)
        has_failures = any(r.result == ValidationResult.FAIL for r in stage_results)
        has_warnings = any(r.result == ValidationResult.WARNING for r in stage_results)
        
        if has_errors:
            overall_result = ValidationResult.ERROR
            overall_confidence = 0.0
        elif has_failures:
            overall_result = ValidationResult.FAIL
            overall_confidence = min(r.confidence for r in stage_results if r.result != ValidationResult.ERROR)
        elif has_warnings:
            overall_result = ValidationResult.WARNING
            overall_confidence = sum(r.confidence for r in stage_results) / len(stage_results)
        else:
            overall_result = ValidationResult.PASS
            overall_confidence = sum(r.confidence for r in stage_results) / len(stage_results)
        
        # Check for cache hits
        cache_hit = any(r.details.get("cached", False) for r in stage_results)
        cache_level = None
        for r in stage_results:
            if r.details.get("cache_level"):
                cache_level = r.details["cache_level"]
                break
        
        return PipelineResult(
            overall_result=overall_result,
            overall_confidence=overall_confidence,
            total_execution_time_ms=total_time,
            stage_results=stage_results,
            constitutional_hash="cdd01ef066bc6cf2",
            cache_hit=cache_hit,
            cache_level=cache_level
        )
    
    def _update_metrics(self, result: PipelineResult):
        """Update pipeline performance metrics."""
        self.total_validations += 1
        self.total_execution_time += result.total_execution_time_ms
        
        # Update compliance rate
        if result.is_compliant():
            self.compliance_rate = ((self.compliance_rate * (self.total_validations - 1)) + 1) / self.total_validations
        else:
            self.compliance_rate = (self.compliance_rate * (self.total_validations - 1)) / self.total_validations
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get pipeline performance metrics."""
        avg_execution_time = self.total_execution_time / self.total_validations if self.total_validations > 0 else 0

        cache_stats = {}
        if self.cache_manager:
            try:
                cache_stats = await self.cache_manager.get_cache_statistics()
            except Exception as e:
                cache_stats = {"error": str(e)}

        return {
            "total_validations": self.total_validations,
            "average_execution_time_ms": avg_execution_time,
            "compliance_rate": self.compliance_rate,
            "sub_2s_target_met": avg_execution_time < 2000,
            "compliance_target_met": self.compliance_rate >= 0.95,
            "cache_manager_stats": cache_stats
        }
    
    async def warm_pipeline(self, sample_requests: List[Dict[str, Any]]):
        """Warm up the pipeline with sample requests."""
        logger.info(f"Warming pipeline with {len(sample_requests)} sample requests...")
        
        for request in sample_requests:
            await self.validate(
                request.get("content", ""),
                request.get("context", {})
            )
        
        logger.info("Pipeline warming completed")


# Global pipeline instance
_pipeline: Optional[ParallelValidationPipeline] = None


async def get_validation_pipeline() -> ParallelValidationPipeline:
    """Get global validation pipeline instance."""
    global _pipeline
    
    if _pipeline is None:
        _pipeline = ParallelValidationPipeline()
        await _pipeline.initialize()
    
    return _pipeline


async def reset_validation_pipeline():
    """Reset global validation pipeline (useful for testing)."""
    global _pipeline
    _pipeline = None
