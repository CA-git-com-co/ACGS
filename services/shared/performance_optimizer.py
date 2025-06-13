#!/usr/bin/env python3
"""
Performance Optimizer for ACGS-1 Phase 2 Multi-Model Integration

This module provides performance optimization capabilities for multi-model consensus
operations, targeting <2s response times for 95% of operations while maintaining
>95% consensus accuracy and constitutional compliance.

Key Features:
- Parallel model execution with async/await patterns
- Intelligent caching with TTL-based invalidation
- Request batching and connection pooling
- Circuit breaker pattern for failing models
- Performance monitoring and adaptive optimization
- Fallback strategies for degraded performance
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Callable, Awaitable
import structlog

logger = structlog.get_logger(__name__)


class OptimizationStrategy(str, Enum):
    """Available performance optimization strategies."""
    
    PARALLEL_EXECUTION = "parallel_execution"
    CACHED_RESPONSES = "cached_responses"
    BATCHED_REQUESTS = "batched_requests"
    CIRCUIT_BREAKER = "circuit_breaker"
    ADAPTIVE_TIMEOUT = "adaptive_timeout"
    PRIORITY_ROUTING = "priority_routing"


@dataclass
class PerformanceMetrics:
    """Performance metrics for optimization tracking."""
    
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time_ms: float = 0.0
    p95_response_time_ms: float = 0.0
    p99_response_time_ms: float = 0.0
    cache_hit_rate: float = 0.0
    circuit_breaker_trips: int = 0
    timeout_events: int = 0
    
    # Response time tracking
    response_times: List[float] = field(default_factory=list)
    
    def add_response_time(self, response_time_ms: float):
        """Add a response time measurement."""
        self.response_times.append(response_time_ms)
        
        # Keep only last 1000 measurements for memory efficiency
        if len(self.response_times) > 1000:
            self.response_times = self.response_times[-1000:]
        
        # Update metrics
        self.avg_response_time_ms = sum(self.response_times) / len(self.response_times)
        
        if len(self.response_times) >= 20:  # Need sufficient data for percentiles
            sorted_times = sorted(self.response_times)
            self.p95_response_time_ms = sorted_times[int(len(sorted_times) * 0.95)]
            self.p99_response_time_ms = sorted_times[int(len(sorted_times) * 0.99)]
    
    def meets_performance_targets(self) -> bool:
        """Check if current metrics meet Phase 2 performance targets."""
        return (
            self.p95_response_time_ms < 2000 and  # <2s for 95% of requests
            self.avg_response_time_ms < 1500 and  # <1.5s average
            self.cache_hit_rate > 70.0  # >70% cache hit rate
        )


@dataclass
class CircuitBreakerState:
    """Circuit breaker state for model failure handling."""
    
    failure_count: int = 0
    last_failure_time: float = 0.0
    state: str = "closed"  # closed, open, half_open
    failure_threshold: int = 5
    recovery_timeout: float = 60.0  # seconds
    
    def should_allow_request(self) -> bool:
        """Check if requests should be allowed through the circuit breaker."""
        current_time = time.time()
        
        if self.state == "closed":
            return True
        elif self.state == "open":
            if current_time - self.last_failure_time > self.recovery_timeout:
                self.state = "half_open"
                return True
            return False
        elif self.state == "half_open":
            return True
        
        return False
    
    def record_success(self):
        """Record a successful request."""
        self.failure_count = 0
        self.state = "closed"
    
    def record_failure(self):
        """Record a failed request."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "open"


class PerformanceOptimizer:
    """
    Advanced performance optimizer for multi-model consensus operations.
    
    Implements various optimization strategies to achieve <2s response times
    while maintaining high accuracy and constitutional compliance.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize performance optimizer."""
        self.config = config or {}
        
        # Performance targets
        self.target_response_time_ms = self.config.get("target_response_time_ms", 2000)
        self.target_cache_hit_rate = self.config.get("target_cache_hit_rate", 70.0)
        self.max_parallel_requests = self.config.get("max_parallel_requests", 10)
        
        # Circuit breakers for each model
        self.circuit_breakers: Dict[str, CircuitBreakerState] = {}
        
        # Performance metrics
        self.metrics = PerformanceMetrics()
        
        # Adaptive timeout settings
        self.base_timeout = self.config.get("base_timeout", 30.0)
        self.adaptive_timeout_enabled = self.config.get("adaptive_timeout", True)
        
        # Cache for response optimization
        self.response_cache: Dict[str, Tuple[Any, float]] = {}
        self.cache_ttl = self.config.get("cache_ttl", 300)  # 5 minutes
    
    async def optimize_multi_model_request(
        self,
        model_requests: Dict[str, Callable[[], Awaitable[Dict[str, Any]]]],
        optimization_strategies: List[OptimizationStrategy] = None
    ) -> Dict[str, Any]:
        """
        Optimize multi-model request execution with various strategies.
        
        Args:
            model_requests: Dictionary of model_id -> async request function
            optimization_strategies: List of optimization strategies to apply
            
        Returns:
            Dictionary with optimized results and performance metadata
        """
        start_time = time.time()
        self.metrics.total_requests += 1
        
        strategies = optimization_strategies or [
            OptimizationStrategy.PARALLEL_EXECUTION,
            OptimizationStrategy.CACHED_RESPONSES,
            OptimizationStrategy.CIRCUIT_BREAKER,
            OptimizationStrategy.ADAPTIVE_TIMEOUT
        ]
        
        try:
            # Apply optimization strategies
            optimized_requests = await self._apply_optimization_strategies(
                model_requests, strategies
            )
            
            # Execute optimized requests
            results = await self._execute_optimized_requests(optimized_requests)
            
            # Calculate performance metrics
            response_time_ms = (time.time() - start_time) * 1000
            self.metrics.add_response_time(response_time_ms)
            self.metrics.successful_requests += 1
            
            logger.info(
                "Multi-model request optimized",
                response_time_ms=response_time_ms,
                strategies_used=[s.value for s in strategies],
                models_executed=len(results),
                cache_hits=self._count_cache_hits(results)
            )
            
            return {
                "results": results,
                "performance": {
                    "response_time_ms": response_time_ms,
                    "strategies_used": [s.value for s in strategies],
                    "models_executed": len(results),
                    "cache_hits": self._count_cache_hits(results),
                    "meets_targets": response_time_ms < self.target_response_time_ms
                },
                "metadata": {
                    "optimization_applied": True,
                    "circuit_breaker_states": {
                        model: cb.state for model, cb in self.circuit_breakers.items()
                    }
                }
            }
            
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            self.metrics.failed_requests += 1
            
            logger.error(
                "Multi-model request optimization failed",
                error=str(e),
                response_time_ms=response_time_ms
            )
            
            return {
                "results": {},
                "performance": {
                    "response_time_ms": response_time_ms,
                    "error": str(e),
                    "meets_targets": False
                },
                "metadata": {"optimization_applied": False}
            }
    
    async def _apply_optimization_strategies(
        self,
        model_requests: Dict[str, Callable[[], Awaitable[Dict[str, Any]]]],
        strategies: List[OptimizationStrategy]
    ) -> Dict[str, Callable[[], Awaitable[Dict[str, Any]]]]:
        """Apply optimization strategies to model requests."""
        
        optimized_requests = model_requests.copy()
        
        for strategy in strategies:
            if strategy == OptimizationStrategy.CACHED_RESPONSES:
                optimized_requests = await self._apply_caching(optimized_requests)
            elif strategy == OptimizationStrategy.CIRCUIT_BREAKER:
                optimized_requests = self._apply_circuit_breaker(optimized_requests)
            elif strategy == OptimizationStrategy.ADAPTIVE_TIMEOUT:
                optimized_requests = self._apply_adaptive_timeout(optimized_requests)
        
        return optimized_requests
    
    async def _apply_caching(
        self,
        model_requests: Dict[str, Callable[[], Awaitable[Dict[str, Any]]]]
    ) -> Dict[str, Callable[[], Awaitable[Dict[str, Any]]]]:
        """Apply response caching optimization."""
        
        cached_requests = {}
        current_time = time.time()
        
        for model_id, request_func in model_requests.items():
            # Generate cache key (simplified - in production would hash request parameters)
            cache_key = f"{model_id}_{hash(str(request_func))}"
            
            # Check cache
            if cache_key in self.response_cache:
                cached_result, cache_time = self.response_cache[cache_key]
                if current_time - cache_time < self.cache_ttl:
                    # Return cached result
                    async def cached_response():
                        return {**cached_result, "cached": True}
                    cached_requests[model_id] = cached_response
                    continue
            
            # Wrap request with caching
            async def cached_request_wrapper():
                result = await request_func()
                self.response_cache[cache_key] = (result, current_time)
                return {**result, "cached": False}
            
            cached_requests[model_id] = cached_request_wrapper
        
        return cached_requests
    
    def _apply_circuit_breaker(
        self,
        model_requests: Dict[str, Callable[[], Awaitable[Dict[str, Any]]]]
    ) -> Dict[str, Callable[[], Awaitable[Dict[str, Any]]]]:
        """Apply circuit breaker pattern to model requests."""
        
        protected_requests = {}
        
        for model_id, request_func in model_requests.items():
            # Initialize circuit breaker if not exists
            if model_id not in self.circuit_breakers:
                self.circuit_breakers[model_id] = CircuitBreakerState()
            
            circuit_breaker = self.circuit_breakers[model_id]
            
            async def protected_request():
                if not circuit_breaker.should_allow_request():
                    return {
                        "error": "Circuit breaker open",
                        "model_id": model_id,
                        "circuit_breaker_state": circuit_breaker.state
                    }
                
                try:
                    result = await request_func()
                    circuit_breaker.record_success()
                    return result
                except Exception as e:
                    circuit_breaker.record_failure()
                    return {
                        "error": str(e),
                        "model_id": model_id,
                        "circuit_breaker_tripped": True
                    }
            
            protected_requests[model_id] = protected_request
        
        return protected_requests
    
    def _apply_adaptive_timeout(
        self,
        model_requests: Dict[str, Callable[[], Awaitable[Dict[str, Any]]]]
    ) -> Dict[str, Callable[[], Awaitable[Dict[str, Any]]]]:
        """Apply adaptive timeout based on historical performance."""
        
        if not self.adaptive_timeout_enabled:
            return model_requests
        
        # Calculate adaptive timeout based on recent performance
        if self.metrics.avg_response_time_ms > 0:
            adaptive_timeout = min(
                self.base_timeout,
                max(5.0, self.metrics.avg_response_time_ms / 1000 * 1.5)  # 1.5x average
            )
        else:
            adaptive_timeout = self.base_timeout
        
        timeout_requests = {}
        
        for model_id, request_func in model_requests.items():
            async def timeout_request():
                try:
                    return await asyncio.wait_for(request_func(), timeout=adaptive_timeout)
                except asyncio.TimeoutError:
                    self.metrics.timeout_events += 1
                    return {
                        "error": "Request timeout",
                        "model_id": model_id,
                        "timeout_seconds": adaptive_timeout
                    }
            
            timeout_requests[model_id] = timeout_request
        
        return timeout_requests
    
    async def _execute_optimized_requests(
        self,
        optimized_requests: Dict[str, Callable[[], Awaitable[Dict[str, Any]]]]
    ) -> Dict[str, Dict[str, Any]]:
        """Execute optimized requests in parallel."""
        
        # Limit parallel execution to prevent resource exhaustion
        semaphore = asyncio.Semaphore(self.max_parallel_requests)
        
        async def execute_with_semaphore(model_id: str, request_func: Callable):
            async with semaphore:
                return model_id, await request_func()
        
        # Execute all requests in parallel
        tasks = [
            execute_with_semaphore(model_id, request_func)
            for model_id, request_func in optimized_requests.items()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        final_results = {}
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Request execution failed: {result}")
                continue
            
            model_id, response = result
            final_results[model_id] = response
        
        return final_results
    
    def _count_cache_hits(self, results: Dict[str, Dict[str, Any]]) -> int:
        """Count cache hits in results."""
        return sum(1 for result in results.values() if result.get("cached", False))
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        return {
            "total_requests": self.metrics.total_requests,
            "successful_requests": self.metrics.successful_requests,
            "failed_requests": self.metrics.failed_requests,
            "success_rate_percentage": (
                self.metrics.successful_requests / max(1, self.metrics.total_requests)
            ) * 100,
            "avg_response_time_ms": self.metrics.avg_response_time_ms,
            "p95_response_time_ms": self.metrics.p95_response_time_ms,
            "p99_response_time_ms": self.metrics.p99_response_time_ms,
            "cache_hit_rate": self.metrics.cache_hit_rate,
            "circuit_breaker_trips": self.metrics.circuit_breaker_trips,
            "timeout_events": self.metrics.timeout_events,
            "meets_performance_targets": self.metrics.meets_performance_targets(),
            "circuit_breaker_states": {
                model: cb.state for model, cb in self.circuit_breakers.items()
            }
        }
    
    def reset_metrics(self):
        """Reset performance metrics."""
        self.metrics = PerformanceMetrics()
        logger.info("Performance metrics reset")


# Global performance optimizer instance
_performance_optimizer: Optional[PerformanceOptimizer] = None


def get_performance_optimizer() -> PerformanceOptimizer:
    """Get global performance optimizer instance."""
    global _performance_optimizer
    
    if _performance_optimizer is None:
        _performance_optimizer = PerformanceOptimizer()
    
    return _performance_optimizer
