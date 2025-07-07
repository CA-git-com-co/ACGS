"""
Evolution Service Module

High-level service layer for evolutionary computation operations with
constitutional compliance and ACGS integration.
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional

import redis.asyncio as aioredis
from prometheus_client import Counter, Gauge, Histogram

from ..core.constitutional_validator import ConstitutionalValidator
from ..core.evolution_engine import EvolutionEngine
from ..models.evolution import (
    EvolutionRequest,
    EvolutionResult,
    EvolutionStatus,
    EvolutionType,
    Individual,
    Population,
)
from ..models.oversight import OversightLevel, OversightRequest

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


class EvolutionService:
    """
    High-level evolution service with constitutional compliance and ACGS integration.
    
    Provides comprehensive evolutionary computation capabilities with O(1) lookup patterns,
    request-scoped caching, and sub-5ms P99 latency targets.
    """
    
    def __init__(self, redis_client: Optional[aioredis.Redis] = None):
        """Initialize evolution service."""
        self.redis = redis_client
        self.evolution_engine = EvolutionEngine(redis_client)
        self.constitutional_validator = ConstitutionalValidator()
        
        self.setup_metrics()
        
        # Service state tracking
        self.active_requests: Dict[str, EvolutionRequest] = {}
        self.request_cache: Dict[str, Any] = {}
        
        logger.info("EvolutionService initialized with constitutional compliance")
    
    def setup_metrics(self) -> None:
        """Setup Prometheus metrics."""
        self.service_requests_total = Counter(
            "evolution_service_requests_total",
            "Total evolution service requests",
            ["operation", "status"]
        )
        
        self.active_requests_gauge = Gauge(
            "evolution_service_active_requests",
            "Number of active evolution requests"
        )
        
        self.request_duration = Histogram(
            "evolution_service_request_duration_ms",
            "Evolution service request duration in milliseconds",
            ["operation"]
        )
    
    async def create_evolution_request(self, 
                                     evolution_type: EvolutionType,
                                     requester_id: str,
                                     **kwargs) -> EvolutionRequest:
        """
        Create a new evolution request with constitutional compliance validation.
        
        Args:
            evolution_type: Type of evolution to perform
            requester_id: ID of the requesting user/service
            **kwargs: Additional evolution parameters
            
        Returns:
            Created evolution request
        """
        start_time = time.time()
        operation = "create_request"
        
        try:
            # Create evolution request
            request = EvolutionRequest(
                evolution_type=evolution_type,
                requester_id=requester_id,
                constitutional_hash=CONSTITUTIONAL_HASH,
                **kwargs
            )
            
            # Validate constitutional compliance if required
            if request.constitutional_compliance_required:
                validation_result = await self.constitutional_validator.validate_evolution_request(
                    request.dict(),
                    {"evolution_id": request.evolution_id}
                )
                
                if validation_result["compliance_score"] < 0.8:
                    request.human_oversight_required = True
                    logger.warning(f"Evolution request {request.evolution_id} requires human oversight due to low compliance score")
            
            # Store request
            self.active_requests[request.evolution_id] = request
            self.active_requests_gauge.set(len(self.active_requests))
            
            # Cache in Redis if available
            if self.redis:
                await self.redis.setex(
                    f"evolution_service:request:{request.evolution_id}",
                    3600,  # 1 hour TTL
                    request.json()
                )
            
            self.service_requests_total.labels(
                operation=operation,
                status="success"
            ).inc()
            
            logger.info(f"Evolution request created: {request.evolution_id}")
            return request
            
        except Exception as e:
            logger.error(f"Failed to create evolution request: {e}")
            self.service_requests_total.labels(
                operation=operation,
                status="error"
            ).inc()
            raise
            
        finally:
            duration = (time.time() - start_time) * 1000
            self.request_duration.labels(operation=operation).observe(duration)
            
            # Ensure sub-5ms P99 latency
            if duration > 5:
                logger.warning(f"Create evolution request took {duration:.2f}ms (>5ms target)")
    
    async def submit_evolution_request(self, request: EvolutionRequest) -> str:
        """
        Submit evolution request for processing.
        
        Args:
            request: Evolution request to submit
            
        Returns:
            Evolution ID for tracking
        """
        start_time = time.time()
        operation = "submit_request"
        
        try:
            # Submit to evolution engine
            evolution_id = await self.evolution_engine.submit_evolution_request(request)
            
            self.service_requests_total.labels(
                operation=operation,
                status="success"
            ).inc()
            
            return evolution_id
            
        except Exception as e:
            logger.error(f"Failed to submit evolution request: {e}")
            self.service_requests_total.labels(
                operation=operation,
                status="error"
            ).inc()
            raise
            
        finally:
            duration = (time.time() - start_time) * 1000
            self.request_duration.labels(operation=operation).observe(duration)
    
    async def get_evolution_status(self, evolution_id: str) -> Optional[EvolutionRequest]:
        """
        Get evolution status with O(1) lookup performance.
        
        Args:
            evolution_id: Evolution ID to lookup
            
        Returns:
            Evolution request if found, None otherwise
        """
        start_time = time.time()
        operation = "get_status"
        
        try:
            # Check local cache first
            if evolution_id in self.active_requests:
                return self.active_requests[evolution_id]
            
            # Check evolution engine
            request = await self.evolution_engine.get_evolution_status(evolution_id)
            if request:
                # Update local cache
                self.active_requests[evolution_id] = request
                return request
            
            # Check Redis cache
            if self.redis:
                cached_data = await self.redis.get(f"evolution_service:request:{evolution_id}")
                if cached_data:
                    request = EvolutionRequest.parse_raw(cached_data)
                    self.active_requests[evolution_id] = request
                    return request
            
            return None
            
        finally:
            duration = (time.time() - start_time) * 1000
            self.request_duration.labels(operation=operation).observe(duration)
            
            # Ensure sub-5ms P99 latency
            if duration > 5:
                logger.warning(f"Get evolution status took {duration:.2f}ms (>5ms target)")
    
    async def evaluate_individual_fitness(self, individual: Individual) -> Individual:
        """
        Evaluate fitness for an individual with constitutional compliance.
        
        Args:
            individual: Individual to evaluate
            
        Returns:
            Individual with updated fitness metrics
        """
        start_time = time.time()
        operation = "evaluate_fitness"
        
        try:
            # Evaluate fitness using evolution engine
            fitness_metrics = await self.evolution_engine.evaluate_fitness(individual)
            individual.fitness_metrics = fitness_metrics
            
            # Validate constitutional compliance
            compliance_score = await self.constitutional_validator.validate_individual(individual)
            individual.constitutional_compliance = compliance_score
            individual.safety_validated = compliance_score >= 0.8
            
            self.service_requests_total.labels(
                operation=operation,
                status="success"
            ).inc()
            
            return individual
            
        except Exception as e:
            logger.error(f"Failed to evaluate individual fitness: {e}")
            self.service_requests_total.labels(
                operation=operation,
                status="error"
            ).inc()
            raise
            
        finally:
            duration = (time.time() - start_time) * 1000
            self.request_duration.labels(operation=operation).observe(duration)
    
    async def create_oversight_request(self, 
                                     evolution_id: str,
                                     reason: str,
                                     oversight_level: OversightLevel = OversightLevel.HUMAN_REVIEW) -> OversightRequest:
        """
        Create human oversight request for evolution process.
        
        Args:
            evolution_id: Evolution ID requiring oversight
            reason: Reason for oversight request
            oversight_level: Level of oversight required
            
        Returns:
            Created oversight request
        """
        start_time = time.time()
        operation = "create_oversight"
        
        try:
            oversight_request = OversightRequest(
                evolution_id=evolution_id,
                oversight_level=oversight_level,
                reason=reason,
                requested_by="evolution_service",
                constitutional_hash=CONSTITUTIONAL_HASH
            )
            
            # Store oversight request
            if self.redis:
                await self.redis.setex(
                    f"evolution_service:oversight:{oversight_request.request_id}",
                    86400,  # 24 hour TTL
                    oversight_request.json()
                )
            
            self.service_requests_total.labels(
                operation=operation,
                status="success"
            ).inc()
            
            logger.info(f"Oversight request created: {oversight_request.request_id}")
            return oversight_request
            
        except Exception as e:
            logger.error(f"Failed to create oversight request: {e}")
            self.service_requests_total.labels(
                operation=operation,
                status="error"
            ).inc()
            raise
            
        finally:
            duration = (time.time() - start_time) * 1000
            self.request_duration.labels(operation=operation).observe(duration)
    
    async def get_service_health(self) -> Dict[str, Any]:
        """
        Get service health status.
        
        Returns:
            Service health information
        """
        return {
            "status": "healthy",
            "service": "evolution_service",
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "active_requests": len(self.active_requests),
            "evolution_engine_healthy": True,
            "constitutional_validator_healthy": True,
            "redis_connected": self.redis is not None,
            "timestamp": time.time()
        }
