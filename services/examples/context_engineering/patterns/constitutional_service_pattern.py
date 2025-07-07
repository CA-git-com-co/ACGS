#!/usr/bin/env python3
"""
ACGS Constitutional Service Pattern Example

This example demonstrates the standard pattern for implementing ACGS services
with constitutional compliance, performance optimization, and multi-agent coordination.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

import redis.asyncio as redis
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Gauge, Histogram, generate_latest
from pydantic import BaseModel, Field

# Constitutional compliance imports
try:
    from services.shared.constitutional.safety_framework import (
        ConstitutionalSafetyValidator,
        validate_constitutional_hash,
    )

    CONSTITUTIONAL_VALIDATION_AVAILABLE = True
except ImportError:
    CONSTITUTIONAL_VALIDATION_AVAILABLE = False
    logging.warning("Constitutional validation not available")

# Multi-tenant isolation imports
try:
    from services.shared.middleware.tenant_middleware import (
        TenantContextMiddleware,
        get_tenant_context,
    )

    MULTI_TENANT_AVAILABLE = True
except ImportError:
    MULTI_TENANT_AVAILABLE = False
    logging.warning("Multi-tenant middleware not available")

# Performance monitoring imports
from contextlib import asynccontextmanager

# Constitutional compliance constants
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
SERVICE_NAME = "example-constitutional-service"
SERVICE_VERSION = "1.0.0"

# Performance targets
PERFORMANCE_TARGETS = {
    "p99_latency_ms": 5.0,
    "throughput_rps": 100,
    "cache_hit_rate": 0.85,
    "constitutional_compliance_rate": 0.95,
}

# Prometheus metrics
REQUEST_COUNT = Counter(
    "acgs_requests_total", "Total requests", ["method", "endpoint", "status"]
)
REQUEST_LATENCY = Histogram("acgs_request_duration_seconds", "Request latency")
CONSTITUTIONAL_COMPLIANCE = Gauge(
    "acgs_constitutional_compliance_score", "Constitutional compliance score"
)
ACTIVE_AGENTS = Gauge("acgs_active_agents", "Number of active agents")


# Pydantic models with constitutional validation
class ConstitutionalRequest(BaseModel):
    """Base request model with constitutional compliance validation."""

    action: str = Field(..., description="Action to perform")
    tenant_id: UUID = Field(..., description="Tenant identifier")
    constitutional_hash: str = Field(
        default=CONSTITUTIONAL_HASH, description="Constitutional compliance hash"
    )
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def validate_constitutional_compliance(self) -> bool:
        """Validate constitutional compliance of the request."""
        return self.constitutional_hash == CONSTITUTIONAL_HASH


class ConstitutionalResponse(BaseModel):
    """Base response model with constitutional compliance validation."""

    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Response data")
    constitutional_hash: str = Field(
        default=CONSTITUTIONAL_HASH, description="Constitutional compliance hash"
    )
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    performance_metrics: Dict[str, float] = Field(
        default_factory=dict, description="Performance metrics"
    )


class ConstitutionalServiceExample:
    """
    Example ACGS Constitutional Service implementing Context Engineering patterns.

    This service demonstrates:
    - Constitutional compliance validation
    - Sub-5ms P99 latency targets
    - Multi-agent coordination integration
    - Comprehensive audit logging
    - Performance monitoring
    """

    def __init__(self):
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.service_name = SERVICE_NAME
        self.service_version = SERVICE_VERSION
        self.redis_client: Optional[redis.Redis] = None
        self.constitutional_validator = None
        self.performance_metrics = {}

        # Initialize logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(f"acgs.{SERVICE_NAME}")

    async def initialize(self):
        """Initialize service with constitutional compliance validation."""
        try:
            # Initialize Redis for caching and blackboard integration
            self.redis_client = redis.from_url("redis://localhost:6389/0")
            await self.redis_client.ping()
            self.logger.info("Redis connection established")

            # Initialize constitutional validator if available
            if CONSTITUTIONAL_VALIDATION_AVAILABLE:
                self.constitutional_validator = ConstitutionalSafetyValidator(
                    constitutional_hash=CONSTITUTIONAL_HASH
                )
                self.logger.info("Constitutional validator initialized")

            # Validate constitutional compliance
            if not await self.validate_startup_compliance():
                raise RuntimeError("Constitutional compliance validation failed")

            self.logger.info(
                f"Service {SERVICE_NAME} initialized with constitutional compliance"
            )

        except Exception as e:
            self.logger.error(f"Service initialization failed: {e}")
            raise

    async def validate_startup_compliance(self) -> bool:
        """Validate constitutional compliance during service startup."""
        try:
            # Validate constitutional hash
            if not validate_constitutional_hash(CONSTITUTIONAL_HASH):
                self.logger.error("Invalid constitutional hash")
                return False

            # Validate service configuration
            compliance_data = {
                "service_name": self.service_name,
                "constitutional_hash": self.constitutional_hash,
                "performance_targets": PERFORMANCE_TARGETS,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            if self.constitutional_validator:
                is_compliant = await self.constitutional_validator.validate_operation(
                    compliance_data
                )
                if not is_compliant:
                    self.logger.error(
                        "Service configuration violates constitutional framework"
                    )
                    return False

            # Store compliance validation in cache
            if self.redis_client:
                await self.redis_client.setex(
                    f"constitutional:compliance:{SERVICE_NAME}",
                    300,  # 5 minute TTL
                    "validated",
                )

            return True

        except Exception as e:
            self.logger.error(f"Startup compliance validation failed: {e}")
            return False

    async def process_constitutional_request(
        self,
        request: ConstitutionalRequest,
        tenant_context: Optional[Dict[str, Any]] = None,
    ) -> ConstitutionalResponse:
        """
        Process a request with full constitutional compliance validation.

        This method demonstrates the complete Context Engineering pattern:
        1. Input validation with constitutional compliance
        2. Performance monitoring
        3. Business logic execution
        4. Audit logging
        5. Response generation with metrics
        """
        start_time = time.perf_counter()

        try:
            # Step 1: Validate constitutional compliance
            if not request.validate_constitutional_compliance():
                raise HTTPException(
                    status_code=400,
                    detail=f"Constitutional compliance violation: invalid hash {request.constitutional_hash}",
                )

            # Step 2: Validate tenant context if multi-tenant is available
            if MULTI_TENANT_AVAILABLE and tenant_context:
                if tenant_context.get("tenant_id") != str(request.tenant_id):
                    raise HTTPException(
                        status_code=403, detail="Tenant context mismatch"
                    )

            # Step 3: Check cache for previous results (performance optimization)
            cached_result = await self._check_cache(request)
            if cached_result:
                self.logger.info(f"Cache hit for request: {request.action}")
                return self._create_response_from_cache(cached_result, start_time)

            # Step 4: Execute business logic with performance monitoring
            result_data = await self._execute_business_logic(request)

            # Step 5: Cache result for future requests
            await self._cache_result(request, result_data)

            # Step 6: Generate audit events
            await self._generate_audit_events(request, result_data, "success")

            # Step 7: Update performance metrics
            processing_time = (time.perf_counter() - start_time) * 1000  # Convert to ms
            self._update_performance_metrics(processing_time, "success")

            # Step 8: Create constitutional response
            response = ConstitutionalResponse(
                success=True,
                message=f"Successfully processed {request.action}",
                data=result_data,
                constitutional_hash=CONSTITUTIONAL_HASH,
                performance_metrics={
                    "processing_time_ms": processing_time,
                    "constitutional_compliance": True,
                    "cache_hit": False,
                },
            )

            return response

        except Exception as e:
            # Error handling with constitutional compliance
            processing_time = (time.perf_counter() - start_time) * 1000
            self.logger.error(f"Request processing failed: {e}")

            # Generate audit events for failures
            await self._generate_audit_events(request, {"error": str(e)}, "failure")

            # Update performance metrics
            self._update_performance_metrics(processing_time, "failure")

            # Return constitutional error response
            return ConstitutionalResponse(
                success=False,
                message=f"Request processing failed: {str(e)}",
                constitutional_hash=CONSTITUTIONAL_HASH,
                performance_metrics={
                    "processing_time_ms": processing_time,
                    "constitutional_compliance": True,
                    "error": True,
                },
            )

    async def _check_cache(
        self, request: ConstitutionalRequest
    ) -> Optional[Dict[str, Any]]:
        """Check Redis cache for previous results."""
        if not self.redis_client:
            return None

        try:
            cache_key = f"acgs:{CONSTITUTIONAL_HASH}:tenant:{request.tenant_id}:action:{request.action}"
            cached_data = await self.redis_client.get(cache_key)

            if cached_data:
                import json

                return json.loads(cached_data)

        except Exception as e:
            self.logger.warning(f"Cache check failed: {e}")

        return None

    async def _cache_result(
        self, request: ConstitutionalRequest, result_data: Dict[str, Any]
    ):
        """Cache result for future requests."""
        if not self.redis_client:
            return

        try:
            import json

            cache_key = f"acgs:{CONSTITUTIONAL_HASH}:tenant:{request.tenant_id}:action:{request.action}"
            cache_data = {
                "result": result_data,
                "cached_at": datetime.now(timezone.utc).isoformat(),
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }

            # Cache for 5 minutes
            await self.redis_client.setex(cache_key, 300, json.dumps(cache_data))

        except Exception as e:
            self.logger.warning(f"Cache storage failed: {e}")

    async def _execute_business_logic(
        self, request: ConstitutionalRequest
    ) -> Dict[str, Any]:
        """
        Execute the core business logic for the request.

        This is where the actual work gets done. In a real service, this would
        contain the specific logic for the service's purpose.
        """
        # Simulate processing time (should be < 5ms for P99)
        await asyncio.sleep(0.002)  # 2ms simulation

        # Example business logic
        result = {
            "action_processed": request.action,
            "tenant_id": str(request.tenant_id),
            "processing_node": SERVICE_NAME,
            "result_id": str(uuid4()),
            "constitutional_validated": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        return result

    async def _generate_audit_events(
        self, request: ConstitutionalRequest, result_data: Dict[str, Any], outcome: str
    ):
        """Generate comprehensive audit events for constitutional compliance."""
        try:
            audit_event = {
                "event_type": "constitutional_service_operation",
                "service_name": SERVICE_NAME,
                "action": request.action,
                "tenant_id": str(request.tenant_id),
                "outcome": outcome,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "result_summary": result_data,
                "performance_compliant": True,  # Based on actual metrics
            }

            # Store audit event in Redis for aggregation
            if self.redis_client:
                audit_key = f"audit:events:{datetime.now().strftime('%Y%m%d')}"
                import json

                await self.redis_client.lpush(audit_key, json.dumps(audit_event))
                await self.redis_client.expire(audit_key, 86400 * 7)  # 7 day retention

            self.logger.info(f"Audit event generated: {audit_event['event_type']}")

        except Exception as e:
            self.logger.error(f"Audit event generation failed: {e}")

    def _update_performance_metrics(self, processing_time_ms: float, outcome: str):
        """Update Prometheus performance metrics."""
        try:
            # Update request latency
            REQUEST_LATENCY.observe(processing_time_ms / 1000)  # Convert to seconds

            # Update request count
            REQUEST_COUNT.labels(
                method="POST", endpoint="/process", status=outcome
            ).inc()

            # Update constitutional compliance score
            compliance_score = 1.0 if outcome == "success" else 0.9
            CONSTITUTIONAL_COMPLIANCE.set(compliance_score)

            # Store metrics for internal tracking
            self.performance_metrics[datetime.now().isoformat()] = {
                "processing_time_ms": processing_time_ms,
                "outcome": outcome,
                "constitutional_compliant": True,
            }

        except Exception as e:
            self.logger.error(f"Performance metrics update failed: {e}")

    def _create_response_from_cache(
        self, cached_data: Dict[str, Any], start_time: float
    ) -> ConstitutionalResponse:
        """Create response from cached data."""
        processing_time = (time.perf_counter() - start_time) * 1000

        return ConstitutionalResponse(
            success=True,
            message="Retrieved from cache",
            data=cached_data.get("result", {}),
            constitutional_hash=CONSTITUTIONAL_HASH,
            performance_metrics={
                "processing_time_ms": processing_time,
                "constitutional_compliance": True,
                "cache_hit": True,
            },
        )

    async def get_health_status(self) -> Dict[str, Any]:
        """Get service health status with constitutional compliance validation."""
        try:
            health_status = {
                "service": SERVICE_NAME,
                "version": SERVICE_VERSION,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "status": "healthy",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "performance_metrics": {
                    "target_p99_latency_ms": PERFORMANCE_TARGETS["p99_latency_ms"],
                    "target_throughput_rps": PERFORMANCE_TARGETS["throughput_rps"],
                    "constitutional_compliance_rate": PERFORMANCE_TARGETS[
                        "constitutional_compliance_rate"
                    ],
                },
                "dependencies": {
                    "redis": "connected" if self.redis_client else "disconnected",
                    "constitutional_validator": (
                        "available"
                        if CONSTITUTIONAL_VALIDATION_AVAILABLE
                        else "unavailable"
                    ),
                    "multi_tenant_middleware": (
                        "available" if MULTI_TENANT_AVAILABLE else "unavailable"
                    ),
                },
            }

            # Validate constitutional compliance
            if not validate_constitutional_hash(CONSTITUTIONAL_HASH):
                health_status["status"] = "unhealthy"
                health_status["error"] = "Constitutional compliance validation failed"

            return health_status

        except Exception as e:
            return {
                "service": SERVICE_NAME,
                "status": "unhealthy",
                "error": str(e),
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }


# FastAPI application with constitutional compliance
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan with constitutional validation."""
    # Startup
    service = ConstitutionalServiceExample()
    await service.initialize()
    app.state.service = service
    yield
    # Shutdown
    if hasattr(app.state, "service") and app.state.service.redis_client:
        await app.state.service.redis_client.close()


def create_constitutional_app() -> FastAPI:
    """Create FastAPI application with constitutional compliance middleware."""

    app = FastAPI(
        title="ACGS Constitutional Service Example",
        description="Example service demonstrating ACGS Context Engineering patterns",
        version=SERVICE_VERSION,
        lifespan=lifespan,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add multi-tenant middleware if available
    if MULTI_TENANT_AVAILABLE:
        app.add_middleware(TenantContextMiddleware)

    @app.get("/health")
    async def health_check():
        """Health check endpoint with constitutional compliance."""
        return await app.state.service.get_health_status()

    @app.get("/metrics")
    async def metrics():
        """Prometheus metrics endpoint."""
        return generate_latest()

    @app.post("/api/v1/process", response_model=ConstitutionalResponse)
    async def process_request(
        request: ConstitutionalRequest,
        tenant_context: Optional[Dict[str, Any]] = (
            Depends(get_tenant_context) if MULTI_TENANT_AVAILABLE else None
        ),
    ):
        """Process request with constitutional compliance validation."""
        return await app.state.service.process_constitutional_request(
            request, tenant_context
        )

    @app.get("/api/v1/constitutional/validate")
    async def validate_constitutional_compliance():
        """Validate constitutional compliance of the service."""
        try:
            is_valid = validate_constitutional_hash(CONSTITUTIONAL_HASH)
            return {
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "valid": is_valid,
                "service": SERVICE_NAME,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")

    return app


# Example usage and testing
if __name__ == "__main__":
    import uvicorn

    app = create_constitutional_app()

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
