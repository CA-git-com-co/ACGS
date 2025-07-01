#!/usr/bin/env python3
"""
ACGS-1 Lite Policy Engine Optimization Service
Embedded OPA evaluation with two-tier caching and partial evaluation
Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import json
import logging
import os
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import redis.asyncio as redis
import uvicorn
import xxhash
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

try:
    import opa_wasm

    OPA_WASM_AVAILABLE = True
except ImportError:
    OPA_WASM_AVAILABLE = False
    logging.warning("OPA WebAssembly not available. Install with: pip install opa-wasm")

# Constitutional constants
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
VERSION = "1.0.0"

# Performance configuration
DEFAULT_CACHE_TTL = 300  # 5 minutes
L1_CACHE_SIZE = 10000
BATCH_SIZE = 10
BATCH_WINDOW_MS = 5
TARGET_P99_LATENCY_MS = 1.0

# Logging configuration
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Track performance metrics for policy evaluation"""

    request_count: int = 0
    total_latency_ns: int = 0
    latencies: list[float] = field(default_factory=list)
    cache_hits: int = 0
    cache_misses: int = 0
    l1_hits: int = 0
    l2_hits: int = 0
    batch_count: int = 0
    batch_size_sum: int = 0
    partial_eval_hits: int = 0
    full_eval_count: int = 0

    def add_latency(self, latency_ns: int):
        """Add a latency measurement"""
        self.request_count += 1
        self.total_latency_ns += latency_ns
        self.latencies.append(latency_ns / 1_000_000)  # Convert to ms

        # Keep only last 10k measurements
        if len(self.latencies) > 10000:
            self.latencies = self.latencies[-10000:]

    def get_percentiles(self) -> dict[str, float]:
        """Calculate latency percentiles"""
        if not self.latencies:
            return {"p50": 0.0, "p95": 0.0, "p99": 0.0}

        sorted_latencies = sorted(self.latencies)
        n = len(sorted_latencies)

        return {
            "p50": sorted_latencies[int(0.5 * n)],
            "p95": sorted_latencies[int(0.95 * n)],
            "p99": sorted_latencies[int(0.99 * n)],
        }

    def get_cache_hit_rate(self) -> float:
        """Calculate overall cache hit rate"""
        total = self.cache_hits + self.cache_misses
        return self.cache_hits / total if total > 0 else 0.0

    def get_avg_latency_ms(self) -> float:
        """Get average latency in milliseconds"""
        return (
            (self.total_latency_ns / self.request_count / 1_000_000)
            if self.request_count > 0
            else 0.0
        )


class PolicyCache:
    """Two-tier caching system for policy evaluation results"""

    def __init__(self, redis_client: redis.Redis | None = None):
        self.redis_client = redis_client
        self.l1_cache: dict[str, tuple[dict[str, Any], float]] = (
            {}
        )  # (result, timestamp)
        self.l1_size = 0
        self.max_l1_size = L1_CACHE_SIZE

    def _generate_cache_key(self, input_data: dict[str, Any]) -> str:
        """Generate fast cache key using decision-affecting fields only"""
        # Extract only fields that affect policy decisions
        cache_fields = {
            "type": input_data.get("type"),
            "constitutional_hash": input_data.get("constitutional_hash"),
            "action": input_data.get("action"),
        }

        # Add context fields that affect decisions
        if "context" in input_data:
            context = input_data["context"]
            cache_fields["context"] = {
                "environment": context.get("environment", {}),
                "agent": context.get("agent", {}),
            }

        # Add evolution/data request fields if present
        if "evolution_request" in input_data:
            evolution = input_data["evolution_request"]
            cache_fields["evolution_request"] = {
                "type": evolution.get("type"),
                "constitutional_hash": evolution.get("constitutional_hash"),
            }

        if "data_request" in input_data:
            data_req = input_data["data_request"]
            cache_fields["data_request"] = {
                "data_fields": data_req.get("data_fields", []),
                "requester_clearance_level": data_req.get("requester_clearance_level"),
                "purpose": data_req.get("purpose"),
            }

        # Use xxhash for fast hashing
        json_str = json.dumps(cache_fields, sort_keys=True, separators=(",", ":"))
        return xxhash.xxh64(json_str.encode()).hexdigest()

    async def get(
        self, input_data: dict[str, Any], metrics: PerformanceMetrics
    ) -> dict[str, Any] | None:
        """Get cached result with L1 -> L2 fallback"""
        cache_key = self._generate_cache_key(input_data)
        current_time = time.time()

        # Check L1 cache first
        if cache_key in self.l1_cache:
            result, timestamp = self.l1_cache[cache_key]
            if current_time - timestamp < DEFAULT_CACHE_TTL:
                metrics.cache_hits += 1
                metrics.l1_hits += 1
                return result
            # Expired, remove from L1
            del self.l1_cache[cache_key]
            self.l1_size -= 1

        # Check L2 cache (Redis)
        if self.redis_client:
            try:
                cached_data = await self.redis_client.get(cache_key)
                if cached_data:
                    result = json.loads(cached_data)
                    # Promote to L1
                    self._set_l1(cache_key, result, current_time)
                    metrics.cache_hits += 1
                    metrics.l2_hits += 1
                    return result
            except Exception as e:
                logger.warning(f"Redis cache get failed: {e}")

        metrics.cache_misses += 1
        return None

    async def set(self, input_data: dict[str, Any], result: dict[str, Any]) -> None:
        """Set result in both L1 and L2 caches"""
        cache_key = self._generate_cache_key(input_data)
        current_time = time.time()

        # Set in L1
        self._set_l1(cache_key, result, current_time)

        # Set in L2 (Redis)
        if self.redis_client:
            try:
                await self.redis_client.setex(
                    cache_key,
                    DEFAULT_CACHE_TTL,
                    json.dumps(result, separators=(",", ":")),
                )
            except Exception as e:
                logger.warning(f"Redis cache set failed: {e}")

    def _set_l1(self, cache_key: str, result: dict[str, Any], timestamp: float) -> None:
        """Set result in L1 cache with LRU eviction"""
        # Remove if already exists
        if cache_key in self.l1_cache:
            del self.l1_cache[cache_key]
            self.l1_size -= 1

        # Evict LRU if at capacity
        while self.l1_size >= self.max_l1_size:
            oldest_key = min(self.l1_cache.keys(), key=lambda k: self.l1_cache[k][1])
            del self.l1_cache[oldest_key]
            self.l1_size -= 1

        # Add new entry
        self.l1_cache[cache_key] = (result, timestamp)
        self.l1_size += 1

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics"""
        return {
            "l1_size": self.l1_size,
            "l1_max_size": self.max_l1_size,
            "l1_utilization": self.l1_size / self.max_l1_size,
        }


class PartialEvaluator:
    """Partial evaluation for common policy scenarios"""

    def __init__(self):
        # Pre-computed results for common safe actions
        self.safe_actions = {
            "data.read_public",
            "data.read_analytics",
            "compute.analyze_metrics",
            "report.generate_summary",
        }

        # Dangerous actions that always fail
        self.dangerous_actions = {
            "system.execute_shell",
            "network.bypass_firewall",
            "auth.escalate_privileges",
            "file.delete_system",
            "network.raw_socket",
            "process.spawn_root",
        }

    def can_partial_evaluate(self, input_data: dict[str, Any]) -> bool:
        """Check if request can be partially evaluated"""
        request_type = input_data.get("type")
        action = input_data.get("action")

        # Only constitutional evaluations with known actions
        if request_type != "constitutional_evaluation":
            return False

        # Must have constitutional hash
        if input_data.get("constitutional_hash") != CONSTITUTIONAL_HASH:
            return False

        # Must be a known safe or dangerous action
        return action in self.safe_actions or action in self.dangerous_actions

    def partial_evaluate(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Perform partial evaluation for known scenarios"""
        action = input_data.get("action")
        context = input_data.get("context", {})
        environment = context.get("environment", {})
        agent = context.get("agent", {})

        # Dangerous actions are always blocked
        if action in self.dangerous_actions:
            return {
                "allow": False,
                "compliance_score": 0.0,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "reasons": [f"Action '{action}' is inherently dangerous"],
                "evaluation_details": {
                    "safety": {"passed": False, "score": 0.0},
                    "constitutional": {"passed": False, "score": 0.0},
                },
                "partial_evaluation": True,
            }

        # Safe actions with proper context
        if action in self.safe_actions:
            # Check minimum safety requirements
            sandbox_enabled = environment.get("sandbox_enabled", False)
            audit_enabled = environment.get("audit_enabled", False)
            trust_level = agent.get("trust_level", 0.0)

            if sandbox_enabled and audit_enabled and trust_level >= 0.8:
                return {
                    "allow": True,
                    "compliance_score": 0.95,
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                    "reasons": [],
                    "evaluation_details": {
                        "safety": {"passed": True, "score": 1.0},
                        "constitutional": {"passed": True, "score": 0.95},
                        "resources": {"passed": True, "score": 1.0},
                        "transparency": {"passed": True, "score": 0.9},
                    },
                    "partial_evaluation": True,
                }

        # Fallback to full evaluation
        raise ValueError("Cannot partial evaluate")


class EmbeddedOPAEvaluator:
    """Embedded OPA evaluation using WebAssembly"""

    def __init__(self, policy_bundle_path: str):
        if not OPA_WASM_AVAILABLE:
            raise RuntimeError(
                "OPA WebAssembly not available. Install with: pip install opa-wasm"
            )

        self.policy_bundle_path = policy_bundle_path
        self.opa = None
        self._load_policies()

    def _load_policies(self):
        """Load OPA policies from bundle"""
        if not Path(self.policy_bundle_path).exists():
            raise FileNotFoundError(
                f"Policy bundle not found: {self.policy_bundle_path}"
            )

        # Load the Wasm policy bundle
        with open(self.policy_bundle_path, "rb") as f:
            policy_data = f.read()

        self.opa = opa_wasm.OPAPolicy(policy_data)
        logger.info(f"Loaded OPA policies from {self.policy_bundle_path}")

    def evaluate(
        self, input_data: dict[str, Any], query: str = "data.acgs.main.decision"
    ) -> dict[str, Any]:
        """Evaluate policy using embedded OPA"""
        if not self.opa:
            raise RuntimeError("OPA policies not loaded")

        try:
            # Execute the policy
            result = self.opa.evaluate(input_data, query)
            return result
        except Exception as e:
            logger.error(f"OPA evaluation failed: {e}")
            # Return safe default (deny)
            return {
                "allow": False,
                "compliance_score": 0.0,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "reasons": [f"Policy evaluation error: {e!s}"],
                "evaluation_details": {},
                "error": True,
            }


class BatchProcessor:
    """Batch multiple requests for efficient processing"""

    def __init__(
        self, evaluator, cache: PolicyCache, partial_evaluator: PartialEvaluator
    ):
        self.evaluator = evaluator
        self.cache = cache
        self.partial_evaluator = partial_evaluator
        self.pending_requests: list[tuple[dict[str, Any], asyncio.Future]] = []
        self.batch_timer: asyncio.Task | None = None

    async def evaluate(
        self, input_data: dict[str, Any], metrics: PerformanceMetrics
    ) -> dict[str, Any]:
        """Add request to batch or process immediately"""
        # Create future for result
        future = asyncio.Future()

        # Add to pending batch
        self.pending_requests.append((input_data, future))

        # Start batch timer if not running
        if not self.batch_timer or self.batch_timer.done():
            self.batch_timer = asyncio.create_task(
                self._process_batch_after_delay(metrics)
            )

        # Process immediately if batch is full
        if len(self.pending_requests) >= BATCH_SIZE:
            if self.batch_timer and not self.batch_timer.done():
                self.batch_timer.cancel()
            await self._process_current_batch(metrics)

        return await future

    async def _process_batch_after_delay(self, metrics: PerformanceMetrics):
        """Process batch after delay"""
        await asyncio.sleep(BATCH_WINDOW_MS / 1000.0)
        await self._process_current_batch(metrics)

    async def _process_current_batch(self, metrics: PerformanceMetrics):
        """Process current batch of requests"""
        if not self.pending_requests:
            return

        batch = self.pending_requests[:]
        self.pending_requests.clear()

        metrics.batch_count += 1
        metrics.batch_size_sum += len(batch)

        # Process each request in parallel
        tasks = []
        for input_data, future in batch:
            task = asyncio.create_task(self._evaluate_single(input_data, metrics))
            tasks.append((task, future))

        # Wait for all tasks and set results
        for task, future in tasks:
            try:
                result = await task
                if not future.done():
                    future.set_result(result)
            except Exception as e:
                if not future.done():
                    future.set_exception(e)

    async def _evaluate_single(
        self, input_data: dict[str, Any], metrics: PerformanceMetrics
    ) -> dict[str, Any]:
        """Evaluate single request with caching and partial evaluation"""
        start_time = time.perf_counter_ns()

        try:
            # Check cache first
            cached_result = await self.cache.get(input_data, metrics)
            if cached_result:
                return cached_result

            # Try partial evaluation
            if self.partial_evaluator.can_partial_evaluate(input_data):
                try:
                    result = self.partial_evaluator.partial_evaluate(input_data)
                    metrics.partial_eval_hits += 1
                    # Cache the result
                    await self.cache.set(input_data, result)
                    return result
                except ValueError:
                    pass  # Fall through to full evaluation

            # Full OPA evaluation
            metrics.full_eval_count += 1
            if hasattr(self.evaluator, "evaluate"):
                # Embedded OPA
                result = self.evaluator.evaluate(input_data)
            else:
                # Fallback evaluation (mock for now)
                result = self._fallback_evaluate(input_data)

            # Cache the result
            await self.cache.set(input_data, result)
            return result

        finally:
            end_time = time.perf_counter_ns()
            metrics.add_latency(end_time - start_time)

    def _fallback_evaluate(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Fallback evaluation when OPA is not available"""
        # Basic safety check
        action = input_data.get("action", "")
        dangerous_actions = {
            "system.execute_shell",
            "network.bypass_firewall",
            "auth.escalate_privileges",
            "file.delete_system",
        }

        if action in dangerous_actions:
            return {
                "allow": False,
                "compliance_score": 0.0,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "reasons": [f"Dangerous action blocked: {action}"],
                "evaluation_details": {"safety": {"passed": False, "score": 0.0}},
                "fallback_evaluation": True,
            }

        return {
            "allow": True,
            "compliance_score": 0.9,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "reasons": [],
            "evaluation_details": {"safety": {"passed": True, "score": 0.9}},
            "fallback_evaluation": True,
        }


# Pydantic models
class PolicyRequest(BaseModel):
    """Policy evaluation request"""

    type: str = Field(
        ...,
        description="Request type (constitutional_evaluation, evolution_approval, data_access)",
    )
    constitutional_hash: str = Field(
        ..., description="Constitutional hash for verification"
    )
    action: str | None = Field(None, description="Action to evaluate")
    context: dict[str, Any] | None = Field(None, description="Evaluation context")
    evolution_request: dict[str, Any] | None = Field(
        None, description="Evolution request details"
    )
    data_request: dict[str, Any] | None = Field(
        None, description="Data access request details"
    )


class PolicyResponse(BaseModel):
    """Policy evaluation response"""

    allow: bool = Field(..., description="Whether the request is allowed")
    compliance_score: float = Field(..., description="Compliance score (0.0-1.0)")
    constitutional_hash: str = Field(..., description="Constitutional hash")
    reasons: list[str] = Field(
        default_factory=list, description="Reasons for the decision"
    )
    evaluation_details: dict[str, Any] = Field(
        default_factory=dict, description="Detailed evaluation results"
    )
    partial_evaluation: bool | None = Field(
        None, description="Whether partial evaluation was used"
    )
    cache_hit: bool | None = Field(None, description="Whether result came from cache")
    latency_ms: float | None = Field(
        None, description="Evaluation latency in milliseconds"
    )


class HealthResponse(BaseModel):
    """Health check response"""

    status: str = Field(..., description="Service status")
    constitutional_hash: str = Field(..., description="Constitutional hash")
    version: str = Field(..., description="Service version")
    performance: dict[str, Any] = Field(..., description="Performance metrics")
    cache_stats: dict[str, Any] = Field(..., description="Cache statistics")


class MetricsResponse(BaseModel):
    """Performance metrics response"""

    request_count: int = Field(..., description="Total requests processed")
    avg_latency_ms: float = Field(..., description="Average latency in milliseconds")
    percentiles: dict[str, float] = Field(..., description="Latency percentiles")
    cache_hit_rate: float = Field(..., description="Overall cache hit rate")
    l1_hit_rate: float = Field(..., description="L1 cache hit rate")
    l2_hit_rate: float = Field(..., description="L2 cache hit rate")
    partial_eval_rate: float = Field(..., description="Partial evaluation rate")
    batch_stats: dict[str, float] = Field(
        ..., description="Batch processing statistics"
    )
    targets_met: dict[str, bool] = Field(
        ..., description="Whether performance targets are met"
    )


# Global state
metrics = PerformanceMetrics()
cache: PolicyCache | None = None
batch_processor: BatchProcessor | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global cache, batch_processor

    # Startup
    logger.info("Starting ACGS-1 Lite Policy Engine Optimization Service")
    logger.info(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")

    # Initialize Redis connection
    redis_client = None
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    try:
        redis_client = redis.from_url(redis_url)
        await redis_client.ping()
        logger.info(f"Connected to Redis: {redis_url}")
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}. Proceeding with L1 cache only.")
        redis_client = None

    # Initialize cache
    cache = PolicyCache(redis_client)

    # Initialize evaluator
    policy_bundle_path = os.getenv(
        "POLICY_BUNDLE_PATH", "/app/policies/acgs-constitutional-policies-1.0.0.wasm"
    )

    try:
        evaluator = (
            EmbeddedOPAEvaluator(policy_bundle_path) if OPA_WASM_AVAILABLE else None
        )
    except Exception as e:
        logger.warning(f"Failed to load embedded OPA: {e}. Using fallback evaluator.")
        evaluator = None

    # Initialize partial evaluator
    partial_evaluator = PartialEvaluator()

    # Initialize batch processor
    batch_processor = BatchProcessor(evaluator, cache, partial_evaluator)

    logger.info("Policy Engine Optimization Service started successfully")

    yield

    # Shutdown
    if redis_client:
        await redis_client.close()
    logger.info("Policy Engine Optimization Service stopped")


# FastAPI app
app = FastAPI(
    title="ACGS-1 Lite Policy Engine Optimization",
    description="High-performance embedded policy evaluation with caching and optimization",
    version=VERSION,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_performance_headers(request: Request, call_next):
    """Add performance metrics to response headers"""
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = (time.perf_counter() - start_time) * 1000  # Convert to ms
    response.headers["X-Process-Time-Ms"] = str(round(process_time, 3))
    response.headers["X-Constitutional-Hash"] = CONSTITUTIONAL_HASH
    return response


@app.post("/v1/data/acgs/main/decision", response_model=PolicyResponse)
async def evaluate_policy(request: PolicyRequest) -> PolicyResponse:
    """Evaluate policy with high-performance optimizations"""
    if not batch_processor:
        raise HTTPException(status_code=500, detail="Policy engine not initialized")

    # Verify constitutional hash
    if request.constitutional_hash != CONSTITUTIONAL_HASH:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid constitutional hash. Expected: {CONSTITUTIONAL_HASH}",
        )

    start_time = time.perf_counter()

    # Convert to dict for processing
    input_data = request.dict(exclude_unset=True)

    # Evaluate using batch processor
    result = await batch_processor.evaluate(input_data, metrics)

    # Calculate latency
    latency_ms = (time.perf_counter() - start_time) * 1000

    # Add metadata
    result["cache_hit"] = result.get("cache_hit", False)
    result["latency_ms"] = round(latency_ms, 3)

    return PolicyResponse(**result)


@app.get("/v1/data/acgs/main/allow")
async def evaluate_policy_simple(
    type: str, constitutional_hash: str, action: str | None = None
) -> dict[str, bool]:
    """Simple boolean policy evaluation"""
    if constitutional_hash != CONSTITUTIONAL_HASH:
        return {"allow": False}

    # Create minimal request
    request_data = {
        "type": type,
        "constitutional_hash": constitutional_hash,
        "action": action,
    }

    if not batch_processor:
        return {"allow": False}

    result = await batch_processor.evaluate(request_data, metrics)
    return {"allow": result.get("allow", False)}


@app.get("/v1/data/acgs/main/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check with performance metrics"""
    percentiles = metrics.get_percentiles()
    cache_stats = cache.get_stats() if cache else {}

    return HealthResponse(
        status="healthy",
        constitutional_hash=CONSTITUTIONAL_HASH,
        version=VERSION,
        performance={
            "request_count": metrics.request_count,
            "avg_latency_ms": round(metrics.get_avg_latency_ms(), 3),
            "p99_latency_ms": round(percentiles["p99"], 3),
            "targets_met": {
                "p99_under_1ms": percentiles["p99"] < TARGET_P99_LATENCY_MS
            },
        },
        cache_stats=cache_stats,
    )


@app.get("/v1/metrics", response_model=MetricsResponse)
async def get_metrics() -> MetricsResponse:
    """Detailed performance metrics"""
    percentiles = metrics.get_percentiles()
    cache_hit_rate = metrics.get_cache_hit_rate()

    # Calculate rates
    total_cache_ops = metrics.cache_hits + metrics.cache_misses
    l1_hit_rate = metrics.l1_hits / total_cache_ops if total_cache_ops > 0 else 0.0
    l2_hit_rate = metrics.l2_hits / total_cache_ops if total_cache_ops > 0 else 0.0

    total_evals = metrics.partial_eval_hits + metrics.full_eval_count
    partial_eval_rate = (
        metrics.partial_eval_hits / total_evals if total_evals > 0 else 0.0
    )

    avg_batch_size = (
        metrics.batch_size_sum / metrics.batch_count if metrics.batch_count > 0 else 0.0
    )

    return MetricsResponse(
        request_count=metrics.request_count,
        avg_latency_ms=round(metrics.get_avg_latency_ms(), 3),
        percentiles=percentiles,
        cache_hit_rate=round(cache_hit_rate, 3),
        l1_hit_rate=round(l1_hit_rate, 3),
        l2_hit_rate=round(l2_hit_rate, 3),
        partial_eval_rate=round(partial_eval_rate, 3),
        batch_stats={
            "batch_count": metrics.batch_count,
            "avg_batch_size": round(avg_batch_size, 2),
            "total_batched_requests": metrics.batch_size_sum,
        },
        targets_met={
            "p50_under_0_5ms": percentiles["p50"] < 0.5,
            "p95_under_0_8ms": percentiles["p95"] < 0.8,
            "p99_under_1ms": percentiles["p99"] < 1.0,
            "cache_hit_rate_over_95": cache_hit_rate > 0.95,
        },
    )


@app.get("/v1/cache/warm")
async def warm_cache():
    """Warm cache with common policy scenarios"""
    if not cache or not batch_processor:
        raise HTTPException(status_code=500, detail="Cache not initialized")

    # Common scenarios to pre-cache
    scenarios = [
        {
            "type": "constitutional_evaluation",
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "action": "data.read_public",
            "context": {
                "environment": {"sandbox_enabled": True, "audit_enabled": True},
                "agent": {"trust_level": 0.9, "requested_resources": {"cpu_cores": 1}},
                "responsible_party": "system",
                "explanation": "Public data read",
            },
        },
        {
            "type": "constitutional_evaluation",
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "action": "compute.analyze_metrics",
            "context": {
                "environment": {"sandbox_enabled": True, "audit_enabled": True},
                "agent": {"trust_level": 0.85, "requested_resources": {"cpu_cores": 2}},
                "responsible_party": "analytics",
                "explanation": "Metrics analysis",
            },
        },
    ]

    warmed_count = 0
    for scenario in scenarios:
        try:
            await batch_processor.evaluate(scenario, metrics)
            warmed_count += 1
        except Exception as e:
            logger.warning(f"Cache warming failed for scenario: {e}")

    return {"warmed_scenarios": warmed_count, "total_scenarios": len(scenarios)}


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8004"))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        access_log=True,
        log_level="info",
    )
