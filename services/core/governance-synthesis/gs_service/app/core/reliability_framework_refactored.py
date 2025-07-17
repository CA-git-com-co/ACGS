"""
Refactored LLM Reliability Framework for ACGS-2

This is a refactored version of the monolithic LLM reliability framework,
split into multiple modules for better maintainability and code organization.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from collections import defaultdict, deque

# Import from refactored modules
from .reliability_enums import (
    CONSTITUTIONAL_HASH,
    ReliabilityLevel,
    RecoveryStrategy,
    RecoveryTrigger,
    RecoveryStatus,
    CriticalFailureMode,
)
from .reliability_models import (
    RecoveryAction,
    RecoveryExecution,
    LLMReliabilityConfig,
    ReliabilityMetrics,
    UltraReliableResult,
)
from .reliability_utils import (
    calculate_wilson_interval,
    calculate_reliability_score,
    generate_cache_key,
    calculate_consensus_score,
    calculate_semantic_faithfulness,
    calculate_bias_score,
    validate_constitutional_hash,
    create_metrics_summary,
)

logger = logging.getLogger(__name__)


class ReliabilityFrameworkCore:
    """Core reliability framework for LLM processing."""

    def __init__(self, config: Optional[LLMReliabilityConfig] = None):
        """Initialize the reliability framework."""
        self.config = config or LLMReliabilityConfig()
        self.metrics = ReliabilityMetrics()
        self.recovery_history: List[RecoveryExecution] = []
        self.cache: Dict[str, UltraReliableResult] = {}
        self.active_recoveries: Dict[str, RecoveryExecution] = {}
        
        # Circuit breaker state
        self.circuit_breaker_open = False
        self.circuit_breaker_failures = 0
        self.circuit_breaker_last_failure = None
        
        logger.info(f"Reliability framework initialized with config: {self.config.target_reliability}")

    async def process_with_reliability(
        self,
        content: str,
        model_names: Optional[List[str]] = None,
        request_id: Optional[str] = None,
    ) -> UltraReliableResult:
        """
        Process content with ultra-reliability guarantees.
        
        Args:
            content: Content to process
            model_names: List of model names to use
            request_id: Optional request identifier
            
        Returns:
            UltraReliableResult with processing results
        """
        start_time = datetime.now(timezone.utc)
        processing_start = start_time.timestamp()
        
        try:
            # Validate constitutional hash
            if not validate_constitutional_hash(self.config.constitutional_hash):
                raise ValueError("Invalid constitutional hash")
            
            # Check circuit breaker
            if self.circuit_breaker_open:
                return self._handle_circuit_breaker_response(content, request_id)
            
            # Check cache first
            cache_key = generate_cache_key(content, str(self.config.__dict__))
            if self.config.cache_enabled and cache_key in self.cache:
                logger.debug(f"Cache hit for request {request_id}")
                return self.cache[cache_key]
            
            # Process with ensemble
            result = await self._process_with_ensemble(content, model_names, request_id)
            
            # Cache result if enabled
            if self.config.cache_enabled:
                self.cache[cache_key] = result
            
            # Update metrics
            self._update_metrics(result, processing_start)
            
            return result
            
        except Exception as e:
            logger.error(f"Reliability processing failed: {e}")
            return await self._handle_failure(content, str(e), request_id)

    async def _process_with_ensemble(
        self,
        content: str,
        model_names: Optional[List[str]],
        request_id: Optional[str],
    ) -> UltraReliableResult:
        """Process content using model ensemble."""
        # Mock implementation - in production would call actual models
        model_outputs = []
        models_used = model_names or ["gpt-4", "claude-3", "gemini-pro"]
        
        for model in models_used[:self.config.ensemble_size]:
            try:
                # Simulate model processing
                await asyncio.sleep(0.1)  # Simulate processing time
                output = f"Processed by {model}: {content[:100]}..."
                model_outputs.append(output)
            except Exception as e:
                logger.warning(f"Model {model} failed: {e}")
                self.circuit_breaker_failures += 1
        
        # Calculate consensus
        consensus_score = calculate_consensus_score(model_outputs, self.config.consensus_threshold)
        consensus_achieved = consensus_score >= self.config.consensus_threshold
        
        # Calculate reliability metrics
        bias_score = calculate_bias_score(content)
        semantic_score = calculate_semantic_faithfulness(content, model_outputs[0] if model_outputs else "")
        
        # Determine final output
        final_output = model_outputs[0] if model_outputs else "Fallback response"
        
        processing_time = 0.5  # Mock processing time
        
        # Calculate overall reliability
        reliability_score = calculate_reliability_score(
            consensus_score, bias_score, semantic_score, processing_time
        )
        
        return UltraReliableResult(
            content=final_output,
            confidence=consensus_score,
            reliability_score=reliability_score,
            consensus_achieved=consensus_achieved,
            models_used=models_used,
            processing_time=processing_time,
            bias_score=bias_score,
            semantic_faithfulness=semantic_score,
            fallback_used=False,
            request_id=request_id or "",
        )

    async def _handle_failure(
        self,
        content: str,
        error: str,
        request_id: Optional[str],
    ) -> UltraReliableResult:
        """Handle processing failure with fallback."""
        logger.error(f"Processing failure: {error}")
        
        # Update failure metrics
        self.metrics.failed_requests += 1
        self.metrics.fallback_activations += 1
        
        # Trigger recovery if needed
        recovery_action = RecoveryAction(
            strategy=RecoveryStrategy.FALLBACK_ACTIVATION,
            trigger=RecoveryTrigger.MODEL_FAILURE_RATE_HIGH,
            priority=1,
            target_component="system",
            parameters={"error": error},
        )
        
        await self._execute_recovery(recovery_action)
        
        return UltraReliableResult(
            content=f"Fallback response for: {content[:50]}...",
            confidence=0.5,
            reliability_score=0.5,
            consensus_achieved=False,
            models_used=["fallback"],
            processing_time=0.1,
            bias_score=0.0,
            semantic_faithfulness=0.8,
            fallback_used=True,
            recovery_actions=[recovery_action],
            request_id=request_id or "",
        )

    async def _execute_recovery(self, action: RecoveryAction):
        """Execute a recovery action."""
        execution = RecoveryExecution(
            action=action,
            status=RecoveryStatus.INITIATED,
            started_at=datetime.now(timezone.utc),
        )
        
        self.active_recoveries[action.target_component] = execution
        
        try:
            # Mock recovery execution
            await asyncio.sleep(0.1)
            execution.status = RecoveryStatus.SUCCESSFUL
            execution.completed_at = datetime.now(timezone.utc)
            execution.effectiveness_score = 0.8
            
            logger.info(f"Recovery action completed: {action.strategy}")
            
        except Exception as e:
            execution.status = RecoveryStatus.FAILED
            execution.error_message = str(e)
            execution.completed_at = datetime.now(timezone.utc)
            logger.error(f"Recovery action failed: {e}")
        
        finally:
            self.recovery_history.append(execution)
            if action.target_component in self.active_recoveries:
                del self.active_recoveries[action.target_component]

    def _handle_circuit_breaker_response(
        self,
        content: str,
        request_id: Optional[str],
    ) -> UltraReliableResult:
        """Handle response when circuit breaker is open."""
        return UltraReliableResult(
            content=f"Circuit breaker active for: {content[:50]}...",
            confidence=0.3,
            reliability_score=0.3,
            consensus_achieved=False,
            models_used=["circuit_breaker"],
            processing_time=0.01,
            bias_score=0.0,
            semantic_faithfulness=0.5,
            fallback_used=True,
            request_id=request_id or "",
        )

    def _update_metrics(self, result: UltraReliableResult, start_time: float):
        """Update reliability metrics."""
        self.metrics.total_requests += 1
        
        # Update reliability scores
        self.metrics.overall_reliability_score = (
            (self.metrics.overall_reliability_score * (self.metrics.total_requests - 1) + result.reliability_score)
            / self.metrics.total_requests
        )
        
        self.metrics.consensus_success_rate = (
            (self.metrics.consensus_success_rate * (self.metrics.total_requests - 1) + (1.0 if result.consensus_achieved else 0.0))
            / self.metrics.total_requests
        )
        
        # Update response time metrics
        response_time = result.processing_time
        self.metrics.average_response_time = (
            (self.metrics.average_response_time * (self.metrics.total_requests - 1) + response_time)
            / self.metrics.total_requests
        )
        
        # Calculate throughput
        current_time = datetime.now(timezone.utc)
        window_duration = (current_time - self.metrics.measurement_window_start).total_seconds()
        if window_duration > 0:
            self.metrics.throughput_rps = self.metrics.total_requests / window_duration
        
        self.metrics.last_updated = current_time

    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status."""
        return create_metrics_summary(self.metrics.__dict__)

    def get_detailed_metrics(self) -> Dict[str, Any]:
        """Get detailed metrics."""
        return {
            "reliability_metrics": self.metrics.__dict__,
            "recovery_history": [
                {
                    "strategy": exec.action.strategy.value,
                    "status": exec.status.value,
                    "started_at": exec.started_at.isoformat(),
                    "completed_at": exec.completed_at.isoformat() if exec.completed_at else None,
                    "effectiveness_score": exec.effectiveness_score,
                }
                for exec in self.recovery_history[-10:]  # Last 10 recoveries
            ],
            "active_recoveries": len(self.active_recoveries),
            "circuit_breaker_status": {
                "open": self.circuit_breaker_open,
                "failures": self.circuit_breaker_failures,
            },
            "cache_size": len(self.cache),
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }


# Factory function for easy initialization
def create_reliability_framework(
    reliability_level: ReliabilityLevel = ReliabilityLevel.SAFETY_CRITICAL,
    ensemble_size: int = 5,
    consensus_threshold: float = 0.8,
) -> ReliabilityFrameworkCore:
    """
    Create a reliability framework instance with specified configuration.
    
    Args:
        reliability_level: Target reliability level
        ensemble_size: Number of models in ensemble
        consensus_threshold: Consensus threshold for decisions
        
    Returns:
        Configured ReliabilityFrameworkCore instance
    """
    config = LLMReliabilityConfig(
        target_reliability=reliability_level,
        ensemble_size=ensemble_size,
        consensus_threshold=consensus_threshold,
    )
    
    return ReliabilityFrameworkCore(config)