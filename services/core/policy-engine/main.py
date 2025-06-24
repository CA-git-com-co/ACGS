#!/usr/bin/env python3
"""
ACGS-1 Lite Policy Engine Service
Provides real-time constitutional policy decisions with OPA integration
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import aiohttp
import aioredis
import pybreaker
import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Gauge, Histogram, generate_latest
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Prometheus metrics
POLICY_EVALUATIONS_TOTAL = Counter(
    "policy_evaluations_total",
    "Total number of policy evaluations",
    ["result", "policy_name", "cache_hit"],
)

POLICY_EVALUATION_DURATION = Histogram(
    "policy_evaluation_duration_seconds",
    "Time spent evaluating policies",
    ["policy_name", "cache_hit"],
)

CONSTITUTIONAL_COMPLIANCE_RATE = Gauge(
    "constitutional_compliance_rate", "Current constitutional compliance rate"
)

OPA_CIRCUIT_BREAKER_STATE = Gauge(
    "opa_circuit_breaker_state", "OPA circuit breaker state (0=closed, 1=open, 2=half-open)"
)

CACHE_HIT_RATE = Gauge("policy_cache_hit_rate", "Policy evaluation cache hit rate")


# Request/Response Models
class PolicyEvaluationRequest(BaseModel):
    action: str = Field(..., description="Action to evaluate")
    agent_id: str = Field(..., description="Agent identifier")
    input_data: Dict[str, Any] = Field(
        default_factory=dict, description="Input data for evaluation"
    )
    context: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional context"
    )


class PolicyEvaluationResponse(BaseModel):
    allow: bool = Field(..., description="Whether the action is allowed")
    violations: List[str] = Field(default_factory=list, description="List of policy violations")
    reason: Optional[str] = Field(None, description="Reason for the decision")
    confidence_score: Optional[float] = Field(None, description="Confidence score (0-1)")
    evaluation_time_ms: int = Field(..., description="Evaluation time in milliseconds")
    cache_hit: bool = Field(..., description="Whether result came from cache")
    policy_version: str = Field(..., description="Version of policies used")


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    dependencies: Dict[str, str]


# Policy Engine Service
class PolicyEngineService:
    def __init__(self):
        self.redis_client: Optional[aioredis.Redis] = None
        self.opa_session: Optional[aiohttp.ClientSession] = None
        self.opa_url = "http://opa:8181"
        self.cache_ttl = 300  # 5 minutes
        self.version = "1.0.0"

        # Circuit breaker for OPA
        self.opa_breaker = pybreaker.CircuitBreaker(
            fail_max=5,
            reset_timeout=30,
            exclude=[aiohttp.ClientTimeout, aiohttp.ClientConnectorError],
        )

        # Compliance tracking
        self.evaluation_count = 0
        self.allowed_count = 0
        self.cache_hits = 0
        self.cache_misses = 0

    async def initialize(self):
        """Initialize connections to Redis and OPA"""
        try:
            # Initialize Redis connection
            self.redis_client = aioredis.from_url(
                "redis://redis:6379/0", encoding="utf-8", decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("Connected to Redis")

            # Initialize OPA session
            self.opa_session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5.0))

            # Test OPA connection
            await self._test_opa_connection()
            logger.info("Connected to OPA")

        except Exception as e:
            logger.error(f"Failed to initialize connections: {e}")
            raise

    async def _test_opa_connection(self):
        """Test connection to OPA"""
        try:
            async with self.opa_session.get(f"{self.opa_url}/health") as response:
                if response.status != 200:
                    raise Exception(f"OPA health check failed: {response.status}")
        except Exception as e:
            logger.error(f"OPA connection test failed: {e}")
            raise

    async def evaluate_policy(self, request: PolicyEvaluationRequest) -> PolicyEvaluationResponse:
        """Evaluate a policy request"""
        start_time = time.time()
        evaluation_id = str(uuid.uuid4())

        try:
            # Generate cache key
            cache_key = self._generate_cache_key(request)

            # Try cache first
            cached_result = await self._get_cached_result(cache_key)
            if cached_result:
                self.cache_hits += 1
                result = PolicyEvaluationResponse(**cached_result)
                result.cache_hit = True
                result.evaluation_time_ms = int((time.time() - start_time) * 1000)

                # Update metrics
                POLICY_EVALUATIONS_TOTAL.labels(
                    result=("allow" if result.allow else "deny"),
                    policy_name="cached",
                    cache_hit="true",
                ).inc()

                POLICY_EVALUATION_DURATION.labels(policy_name="cached", cache_hit="true").observe(
                    time.time() - start_time
                )

                return result

            # Cache miss - evaluate with OPA
            self.cache_misses += 1
            result = await self._evaluate_with_opa(request, evaluation_id)
            result.cache_hit = False
            result.evaluation_time_ms = int((time.time() - start_time) * 1000)

            # Cache the result
            await self._cache_result(cache_key, result)

            # Update metrics
            self.evaluation_count += 1
            if result.allow:
                self.allowed_count += 1

            POLICY_EVALUATIONS_TOTAL.labels(
                result=("allow" if result.allow else "deny"), policy_name="opa", cache_hit="false"
            ).inc()

            POLICY_EVALUATION_DURATION.labels(policy_name="opa", cache_hit="false").observe(
                time.time() - start_time
            )

            # Update compliance rate
            if self.evaluation_count > 0:
                compliance_rate = self.allowed_count / self.evaluation_count
                CONSTITUTIONAL_COMPLIANCE_RATE.set(compliance_rate)

            # Update cache hit rate
            total_requests = self.cache_hits + self.cache_misses
            if total_requests > 0:
                cache_hit_rate = self.cache_hits / total_requests
                CACHE_HIT_RATE.set(cache_hit_rate)

            return result

        except Exception as e:
            logger.error(f"Policy evaluation failed: {e}")
            # Return safe default (deny)
            return PolicyEvaluationResponse(
                allow=False,
                violations=["evaluation_error"],
                reason=f"Policy evaluation failed: {str(e)}",
                confidence_score=0.0,
                evaluation_time_ms=int((time.time() - start_time) * 1000),
                cache_hit=False,
                policy_version=self.version,
            )

    @pybreaker.CircuitBreaker(fail_max=5, reset_timeout=30)
    async def _evaluate_with_opa(
        self, request: PolicyEvaluationRequest, evaluation_id: str
    ) -> PolicyEvaluationResponse:
        """Evaluate policy using OPA"""
        try:
            # Prepare OPA input
            opa_input = {
                "input": {
                    "action": request.action,
                    "agent_id": request.agent_id,
                    "data": request.input_data,
                    "context": request.context,
                    "evaluation_id": evaluation_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            }

            # Query OPA
            async with self.opa_session.post(
                f"{self.opa_url}/v1/data/acgs/constitutional/evaluate", json=opa_input
            ) as response:
                if response.status != 200:
                    raise Exception(f"OPA request failed: {response.status}")

                opa_result = await response.json()

                # Parse OPA response
                result_data = opa_result.get("result", {})

                return PolicyEvaluationResponse(
                    allow=result_data.get("allow", False),
                    violations=result_data.get("violations", []),
                    reason=result_data.get("reason"),
                    confidence_score=result_data.get("confidence_score"),
                    evaluation_time_ms=0,  # Will be set by caller
                    cache_hit=False,
                    policy_version=result_data.get("policy_version", self.version),
                )

        except Exception as e:
            # Update circuit breaker state metric
            OPA_CIRCUIT_BREAKER_STATE.set(1 if self.opa_breaker.current_state == "open" else 0)
            logger.error(f"OPA evaluation failed: {e}")
            raise

    def _generate_cache_key(self, request: PolicyEvaluationRequest) -> str:
        """Generate cache key for request"""
        # Create deterministic hash of request
        key_data = {
            "action": request.action,
            "agent_id": request.agent_id,
            "input_data": request.input_data,
            "context": request.context,
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return f"policy_eval:{hash(key_str)}"

    async def _get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached evaluation result"""
        try:
            if not self.redis_client:
                return None

            cached_data = await self.redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
            return None
        except Exception as e:
            logger.warning(f"Cache get failed: {e}")
            return None

    async def _cache_result(self, cache_key: str, result: PolicyEvaluationResponse):
        """Cache evaluation result"""
        try:
            if not self.redis_client:
                return

            # Only cache successful evaluations
            if result.confidence_score and result.confidence_score > 0.8:
                cache_data = result.dict()
                await self.redis_client.setex(cache_key, self.cache_ttl, json.dumps(cache_data))
        except Exception as e:
            logger.warning(f"Cache set failed: {e}")

    async def get_health(self) -> HealthResponse:
        """Get service health status"""
        dependencies = {}

        # Check Redis
        try:
            await self.redis_client.ping()
            dependencies["redis"] = "healthy"
        except Exception:
            dependencies["redis"] = "unhealthy"

        # Check OPA
        try:
            async with self.opa_session.get(f"{self.opa_url}/health") as response:
                dependencies["opa"] = "healthy" if response.status == 200 else "unhealthy"
        except Exception:
            dependencies["opa"] = "unhealthy"

        overall_status = (
            "healthy"
            if all(status == "healthy" for status in dependencies.values())
            else "degraded"
        )

        return HealthResponse(
            status=overall_status,
            timestamp=datetime.now(timezone.utc).isoformat(),
            version=self.version,
            dependencies=dependencies,
        )

    async def cleanup(self):
        """Cleanup connections"""
        if self.opa_session:
            await self.opa_session.close()
        if self.redis_client:
            await self.redis_client.close()


# FastAPI Application
app = FastAPI(
    title="ACGS-1 Lite Policy Engine",
    description="Constitutional policy evaluation service",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global service instance
policy_service = PolicyEngineService()


@app.on_event("startup")
async def startup_event():
    """Initialize service on startup"""
    await policy_service.initialize()
    logger.info("Policy Engine Service started")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await policy_service.cleanup()
    logger.info("Policy Engine Service stopped")


@app.post("/v1/evaluate", response_model=PolicyEvaluationResponse)
async def evaluate_policy(request: PolicyEvaluationRequest):
    """Evaluate a constitutional policy"""
    return await policy_service.evaluate_policy(request)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return await policy_service.get_health()


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type="text/plain")


@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    health = await policy_service.get_health()
    if health.status == "healthy":
        return {"status": "ready"}
    else:
        raise HTTPException(status_code=503, detail="Service not ready")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, log_level="info", access_log=True)
