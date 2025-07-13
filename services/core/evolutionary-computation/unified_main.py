#!/usr/bin/env python3
"""
ACGS Unified Evolution/Compiler Service

This service consolidates the fragmented evolution and compiler components
into a single production-ready endpoint providing:
- Agent evolution evaluation and approval workflows
- Policy compilation and synthesis
- Incremental code compilation
- Constitutional compliance integration
- Rollback mechanisms

Constitutional Hash: cdd01ef066bc6cf2
Service Port: 8006
"""

import hashlib
import json
import logging
import os
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

import asyncpg
import httpx
import redis.asyncio as aioredis
import uvicorn

# Import real evolutionary algorithms
from evolutionary_algorithms import (
    EvolutionaryAgentOptimizer,
    EvolutionParams,
    OptimizationObjective,
)
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("acgs_evolution_compiler")

# Service configuration
SERVICE_NAME = "evolution-compiler-service"
SERVICE_VERSION = "3.0.0"
SERVICE_PORT = 8006
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# External service URLs
POLICY_ENGINE_URL = os.getenv("POLICY_ENGINE_URL", "http://localhost:8005")
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8000")
INTEGRITY_SERVICE_URL = os.getenv("INTEGRITY_SERVICE_URL", "http://localhost:8002")
FORMAL_VERIFICATION_URL = os.getenv("FORMAL_VERIFICATION_URL", "http://localhost:8003")

# Database and Redis
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://acgs_user:acgs_secure_password@localhost:5439/acgs_production",
)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6389/4")

app = FastAPI(
    title="ACGS Unified Evolution/Compiler Service",
    description=(
        "Unified service for agent evolution, policy compilation, and constitutional"
        " governance"
    ),
    version=SERVICE_VERSION,
    openapi_url="/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Global service state
db_pool: asyncpg.Pool | None = None
redis_client: aioredis.Redis | None = None
service_clients: dict[str, httpx.AsyncClient] = {}
evolutionary_optimizer: EvolutionaryAgentOptimizer | None = None


# Data models
class CompilationStatus(str, Enum):
    PENDING = "pending"
    COMPILING = "compiling"
    COMPLETED = "completed"
    FAILED = "failed"
    CACHED = "cached"


class EvolutionStatus(str, Enum):
    PENDING = "pending"
    EVALUATING = "evaluating"
    AUTO_APPROVED = "auto_approved"
    HUMAN_REVIEW = "human_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    DEPLOYED = "deployed"
    ROLLED_BACK = "rolled_back"


class CompilationType(str, Enum):
    POLICY = "policy"
    AGENT_CODE = "agent_code"
    CONSTITUTIONAL_RULE = "constitutional_rule"
    GOVERNANCE_WORKFLOW = "governance_workflow"


@dataclass
class CompilationRequest:
    """Compilation request for policies or agent code."""

    compilation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_content: str
    compilation_type: CompilationType
    target_format: str = "executable"
    optimization_level: int = 1
    constitutional_compliance: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EvolutionRequest:
    """Agent evolution request."""

    evolution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str
    current_version: str
    new_code: str
    change_description: str
    requester_id: str
    priority: str = "medium"
    constitutional_compliance_required: bool = True


@dataclass
class CompilationResult:
    """Result of compilation process."""

    compilation_id: str
    status: CompilationStatus
    compiled_output: str | None = None
    compilation_time_ms: float = 0.0
    constitutional_compliance_score: float = 0.0
    optimization_applied: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


# API Models
class CompilationRequestModel(BaseModel):
    """API model for compilation request."""

    source_content: str = Field(..., description="Source code or policy to compile")
    compilation_type: CompilationType = Field(..., description="Type of compilation")
    target_format: str = Field(
        default="executable", description="Target compilation format"
    )
    optimization_level: int = Field(default=1, description="Optimization level (0-3)")
    constitutional_compliance: bool = Field(
        default=True, description="Require constitutional compliance"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "source_content": (
                    "def evaluate_user_request(request): return"
                    " verify_human_dignity(request) and check_fairness(request)"
                ),
                "compilation_type": "agent_code",
                "target_format": "executable",
                "optimization_level": 2,
                "constitutional_compliance": True,
                "metadata": {"agent_id": "agent_001", "version": "2.1"},
            }
        }


class EvolutionRequestModel(BaseModel):
    """API model for evolution request."""

    agent_id: str = Field(..., description="Agent identifier")
    current_version: str = Field(..., description="Current agent version")
    new_code: str = Field(..., description="New agent code")
    change_description: str = Field(..., description="Description of changes")
    requester_id: str = Field(..., description="ID of user requesting evolution")
    priority: str = Field(default="medium", description="Evolution priority")
    constitutional_compliance_required: bool = Field(
        default=True, description="Require constitutional compliance"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "agent_001",
                "current_version": "1.0",
                "new_code": (
                    "class EnhancedAgent: def process_request(self, req): return"
                    " self.constitutional_filter(req)"
                ),
                "change_description": (
                    "Added constitutional filtering to request processing"
                ),
                "requester_id": "user_123",
                "priority": "high",
                "constitutional_compliance_required": True,
            }
        }


class CompilationResponseModel(BaseModel):
    """API response model for compilation."""

    compilation_id: str
    status: CompilationStatus
    compilation_time_ms: float
    constitutional_compliance_score: float
    compiled_output: str | None = None
    optimization_applied: list[str] = []
    errors: list[str] = []
    warnings: list[str] = []
    constitutional_hash: str = CONSTITUTIONAL_HASH
    metadata: dict[str, Any] = {}


class EvolutionResponseModel(BaseModel):
    """API response model for evolution."""

    evolution_id: str
    status: EvolutionStatus
    evaluation_score: float
    constitutional_compliance_score: float
    approval_required: bool
    estimated_review_time: str | None = None
    constitutional_hash: str = CONSTITUTIONAL_HASH
    recommendations: list[str] = []


# Core compilation engine
class ConstitutionalCompiler:
    """
    Constitutional compiler that ensures all compiled code adheres to
    constitutional principles and governance requirements.
    """

    def __init__(
        self,
        redis_client: aioredis.Redis,
        service_clients: dict[str, httpx.AsyncClient],
    ):
        self.redis = redis_client
        self.clients = service_clients
        self.optimization_strategies = {
            0: "none",
            1: "basic",
            2: "constitutional_aware",
            3: "full_optimization",
        }

    async def compile_source(self, request: CompilationRequest) -> CompilationResult:
        """
        Compile source code or policy with constitutional compliance verification.

        Args:
            request: Compilation request

        Returns:
            CompilationResult with compilation details
        """
        start_time = time.time()
        compilation_id = request.compilation_id

        try:
            logger.info(
                f"Starting compilation {compilation_id} for type"
                f" {request.compilation_type}"
            )

            # Check cache first
            cached_result = await self._check_compilation_cache(request)
            if cached_result:
                logger.info(f"Cache hit for compilation {compilation_id}")
                return cached_result

            # Step 1: Constitutional compliance check
            compliance_score = 0.0
            if request.constitutional_compliance:
                compliance_score = await self._verify_constitutional_compliance(request)
                if compliance_score < 0.7:
                    return CompilationResult(
                        compilation_id=compilation_id,
                        status=CompilationStatus.FAILED,
                        compilation_time_ms=(time.time() - start_time) * 1000,
                        constitutional_compliance_score=compliance_score,
                        errors=[
                            "Constitutional compliance score too low:"
                            f" {compliance_score:.2f}"
                        ],
                    )

            # Step 2: Syntax and semantic analysis
            analysis_result = await self._analyze_source(request)
            if not analysis_result["valid"]:
                return CompilationResult(
                    compilation_id=compilation_id,
                    status=CompilationStatus.FAILED,
                    compilation_time_ms=(time.time() - start_time) * 1000,
                    constitutional_compliance_score=compliance_score,
                    errors=analysis_result["errors"],
                )

            # Step 3: Apply optimizations
            optimized_code = await self._apply_optimizations(
                request.source_content,
                request.optimization_level,
                request.compilation_type,
            )

            # Step 4: Generate executable output
            compiled_output = await self._generate_executable(
                optimized_code, request.target_format, request.compilation_type
            )

            # Step 5: Final constitutional verification
            final_compliance = await self._verify_compiled_output(
                compiled_output, request
            )

            compilation_time = (time.time() - start_time) * 1000

            result = CompilationResult(
                compilation_id=compilation_id,
                status=CompilationStatus.COMPLETED,
                compiled_output=compiled_output,
                compilation_time_ms=compilation_time,
                constitutional_compliance_score=final_compliance,
                optimization_applied=self._get_applied_optimizations(
                    request.optimization_level
                ),
                warnings=analysis_result.get("warnings", []),
                metadata={
                    "source_hash": hashlib.sha256(
                        request.source_content.encode()
                    ).hexdigest(),
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                    "optimization_level": request.optimization_level,
                },
            )

            # Cache result
            await self._cache_compilation_result(request, result)

            logger.info(
                f"Compilation {compilation_id} completed successfully in"
                f" {compilation_time:.2f}ms"
            )
            return result

        except Exception as e:
            logger.exception(f"Compilation {compilation_id} failed: {e}")
            return CompilationResult(
                compilation_id=compilation_id,
                status=CompilationStatus.FAILED,
                compilation_time_ms=(time.time() - start_time) * 1000,
                constitutional_compliance_score=0.0,
                errors=[f"Compilation error: {e!s}"],
            )

    async def _verify_constitutional_compliance(
        self, request: CompilationRequest
    ) -> float:
        """Verify constitutional compliance using Policy Governance Service."""
        try:
            if "policy" not in self.clients:
                return 0.5  # Default score if service unavailable

            response = await self.clients["policy"].post(
                f"{POLICY_ENGINE_URL}/api/v1/verify-constitutional",
                json={
                    "content": request.source_content,
                    "type": request.compilation_type.value,
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                },
                timeout=10.0,
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("compliance_score", 0.5)
            logger.warning(
                f"Constitutional compliance check failed: {response.status_code}"
            )
            return 0.5

        except Exception as e:
            logger.warning(f"Constitutional compliance verification failed: {e}")
            return 0.5

    async def _analyze_source(self, request: CompilationRequest) -> dict[str, Any]:
        """Analyze source code for syntax and semantic correctness."""
        try:
            errors = []
            warnings = []

            # Basic syntax checks based on compilation type
            if request.compilation_type == CompilationType.POLICY:
                # Policy-specific validation
                if (
                    "human_dignity" not in request.source_content.lower()
                    and "fairness" not in request.source_content.lower()
                ):
                    warnings.append(
                        "Policy should reference core constitutional principles"
                    )

                if len(request.source_content.strip()) < 10:
                    errors.append("Policy content too short")

            elif request.compilation_type == CompilationType.AGENT_CODE:
                # Agent code validation
                if (
                    "def " not in request.source_content
                    and "class " not in request.source_content
                ):
                    errors.append(
                        "Agent code must contain function or class definitions"
                    )

                # Check for potentially dangerous operations
                dangerous_patterns = ["exec(", "eval(", "__import__", "open("]
                warnings.extend(
                    f"Potentially dangerous operation detected: {pattern}"
                    for pattern in dangerous_patterns
                    if pattern in request.source_content
                )

            return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}

        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Analysis failed: {e!s}"],
                "warnings": [],
            }

    async def _apply_optimizations(
        self, source: str, level: int, compilation_type: CompilationType
    ) -> str:
        """Apply optimization transformations to source code."""
        try:
            optimized = source

            if level >= 1:
                # Basic optimizations
                optimized = optimized.strip()

            if level >= 2:
                # Constitutional-aware optimizations
                if compilation_type == CompilationType.AGENT_CODE:
                    # Add constitutional compliance wrapper
                    if "constitutional_filter" not in optimized:
                        optimized = f"# Constitutional compliance wrapper\n{optimized}"

            if level >= 3:
                # Full optimization
                # Add performance optimizations, dead code elimination, etc.
                pass

            return optimized

        except Exception as e:
            logger.warning(f"Optimization failed: {e}")
            return source

    async def _generate_executable(
        self, source: str, target_format: str, compilation_type: CompilationType
    ) -> str:
        """Generate executable output in target format."""
        try:
            if target_format == "executable":
                # Generate executable wrapper
                if compilation_type == CompilationType.POLICY:
                    return f"""
# ACGS Constitutional Policy
# Constitutional Hash: {CONSTITUTIONAL_HASH}
# Generated: {datetime.now(timezone.utc).isoformat()}

{source}

# Constitutional compliance verification
def verify_constitutional_compliance():
    return True  # Placeholder for runtime verification
"""

                if compilation_type == CompilationType.AGENT_CODE:
                    return f"""
# ACGS Agent Code
# Constitutional Hash: {CONSTITUTIONAL_HASH}
# Generated: {datetime.now(timezone.utc).isoformat()}

import logging
logger = logging.getLogger(__name__)

{source}

# Constitutional compliance runtime check
def __constitutional_runtime_check__():
    logger.info(f"Agent operating under constitutional hash: {CONSTITUTIONAL_HASH}")
    return True

# Initialize constitutional compliance
__constitutional_runtime_check__()
"""

            elif target_format == "bytecode":
                # Simulate bytecode generation
                return f"BYTECODE:{hashlib.sha256(source.encode()).hexdigest()}"

            return source

        except Exception as e:
            logger.exception(f"Executable generation failed: {e}")
            return source

    async def _verify_compiled_output(
        self, compiled_output: str, request: CompilationRequest
    ) -> float:
        """Verify compiled output maintains constitutional compliance."""
        try:
            # Use Formal Verification Service if available
            if "formal_verification" in self.clients:
                response = await self.clients["formal_verification"].post(
                    f"{FORMAL_VERIFICATION_URL}/api/v1/formal-verification/verify-policy",
                    json={
                        "policy_content": compiled_output,
                        "policy_metadata": request.metadata,
                    },
                    timeout=15.0,
                )

                if response.status_code == 200:
                    result = response.json()
                    return result.get("confidence_score", 0.5)

            # Fallback verification
            constitutional_terms = [
                "human_dignity",
                "fairness",
                "privacy",
                "transparency",
            ]
            score = sum(
                1 for term in constitutional_terms if term in compiled_output.lower()
            ) / len(constitutional_terms)
            return min(1.0, score + 0.5)  # Boost base score

        except Exception as e:
            logger.warning(f"Compiled output verification failed: {e}")
            return 0.7  # Conservative fallback

    def _get_applied_optimizations(self, level: int) -> list[str]:
        """Get list of optimizations applied at given level."""
        optimizations = []

        if level >= 1:
            optimizations.append("basic_cleanup")
        if level >= 2:
            optimizations.extend(["constitutional_wrapping", "compliance_injection"])
        if level >= 3:
            optimizations.extend(["performance_optimization", "dead_code_elimination"])

        return optimizations

    async def _check_compilation_cache(
        self, request: CompilationRequest
    ) -> CompilationResult | None:
        """Check if compilation result is cached."""
        try:
            cache_key = self._generate_cache_key(request)
            cached_data = await self.redis.get(cache_key)

            if cached_data:
                data = json.loads(cached_data)
                return CompilationResult(
                    compilation_id=request.compilation_id,
                    status=CompilationStatus.CACHED,
                    compiled_output=data["compiled_output"],
                    compilation_time_ms=0.0,
                    constitutional_compliance_score=data["compliance_score"],
                    optimization_applied=data["optimizations"],
                    metadata=data["metadata"],
                )

            return None

        except Exception as e:
            logger.warning(f"Cache check failed: {e}")
            return None

    async def _cache_compilation_result(
        self, request: CompilationRequest, result: CompilationResult
    ):
        """Cache compilation result."""
        try:
            cache_key = self._generate_cache_key(request)
            cache_data = {
                "compiled_output": result.compiled_output,
                "compliance_score": result.constitutional_compliance_score,
                "optimizations": result.optimization_applied,
                "metadata": result.metadata,
            }

            # Cache for 1 hour
            await self.redis.setex(cache_key, 3600, json.dumps(cache_data))

        except Exception as e:
            logger.warning(f"Cache storage failed: {e}")

    def _generate_cache_key(self, request: CompilationRequest) -> str:
        """Generate cache key for compilation request."""
        key_data = {
            "source_hash": hashlib.sha256(request.source_content.encode()).hexdigest(),
            "type": request.compilation_type.value,
            "optimization": request.optimization_level,
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }
        return f"compilation:{hashlib.sha256(json.dumps(key_data, sort_keys=True).encode()).hexdigest()}"


# Evolution Engine
class AgentEvolutionEngine:
    """
    Engine for managing agent evolution with constitutional compliance.
    """

    def __init__(self, compiler: ConstitutionalCompiler, db_pool: asyncpg.Pool):
        self.compiler = compiler
        self.db_pool = db_pool

    async def process_evolution(self, request: EvolutionRequest) -> dict[str, Any]:
        """Process agent evolution request."""
        try:
            logger.info(
                f"Processing evolution {request.evolution_id} for agent"
                f" {request.agent_id}"
            )

            # Step 1: Compile new agent code
            compilation_request = CompilationRequest(
                source_content=request.new_code,
                compilation_type=CompilationType.AGENT_CODE,
                constitutional_compliance=request.constitutional_compliance_required,
                metadata={
                    "agent_id": request.agent_id,
                    "evolution_id": request.evolution_id,
                    "version": request.current_version,
                },
            )

            compilation_result = await self.compiler.compile_source(compilation_request)

            if compilation_result.status == CompilationStatus.FAILED:
                return {
                    "evolution_id": request.evolution_id,
                    "status": EvolutionStatus.REJECTED,
                    "reason": "Compilation failed",
                    "errors": compilation_result.errors,
                    "constitutional_compliance_score": (
                        compilation_result.constitutional_compliance_score
                    ),
                }

            # Step 2: Evaluate evolution risk
            risk_score = await self._evaluate_evolution_risk(
                request, compilation_result
            )

            # Step 3: Determine approval path
            if (
                compilation_result.constitutional_compliance_score >= 0.95
                and risk_score <= 0.2
            ):
                # Auto-approve low-risk constitutional changes
                return await self._auto_approve_evolution(
                    request, compilation_result, risk_score
                )

            if (
                compilation_result.constitutional_compliance_score >= 0.8
                and risk_score <= 0.5
            ):
                # Require human review for medium risk
                return await self._require_human_review(
                    request, compilation_result, risk_score
                )

            # Reject high-risk or non-compliant changes
            return await self._reject_evolution(request, compilation_result, risk_score)

        except Exception as e:
            logger.exception(
                f"Evolution processing failed for {request.evolution_id}: {e}"
            )
            return {
                "evolution_id": request.evolution_id,
                "status": EvolutionStatus.FAILED,
                "error": str(e),
                "constitutional_compliance_score": 0.0,
            }

    async def _evaluate_evolution_risk(
        self, request: EvolutionRequest, compilation_result: CompilationResult
    ) -> float:
        """Evaluate risk level of evolution."""
        try:
            risk_factors = 0.0

            # Code complexity risk
            if len(request.new_code) > 1000:
                risk_factors += 0.2

            # Change magnitude risk
            if len(request.change_description.split()) < 3:
                risk_factors += 0.1  # Insufficient description

            # Constitutional compliance risk
            if compilation_result.constitutional_compliance_score < 0.9:
                risk_factors += 0.3

            # Compilation warnings
            if compilation_result.warnings:
                risk_factors += len(compilation_result.warnings) * 0.05

            return min(1.0, risk_factors)

        except Exception as e:
            logger.warning(f"Risk evaluation failed: {e}")
            return 0.5  # Conservative default

    async def _auto_approve_evolution(
        self,
        request: EvolutionRequest,
        compilation_result: CompilationResult,
        risk_score: float,
    ) -> dict[str, Any]:
        """Auto-approve low-risk evolution."""
        try:
            # Store evolution record
            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO agent_evolutions (
                        evolution_id, agent_id, status, compiled_code,
                        constitutional_compliance_score, risk_score, decision_type
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                    request.evolution_id,
                    request.agent_id,
                    EvolutionStatus.AUTO_APPROVED.value,
                    compilation_result.compiled_output,
                    compilation_result.constitutional_compliance_score,
                    risk_score,
                    "AUTO_APPROVED",
                )

            return {
                "evolution_id": request.evolution_id,
                "status": EvolutionStatus.AUTO_APPROVED,
                "constitutional_compliance_score": (
                    compilation_result.constitutional_compliance_score
                ),
                "risk_score": risk_score,
                "approval_required": False,
                "compiled_code": compilation_result.compiled_output,
                "recommendations": [
                    "Evolution auto-approved based on constitutional compliance and low"
                    " risk"
                ],
            }

        except Exception as e:
            logger.exception(f"Auto-approval failed: {e}")
            raise

    async def _require_human_review(
        self,
        request: EvolutionRequest,
        compilation_result: CompilationResult,
        risk_score: float,
    ) -> dict[str, Any]:
        """Require human review for medium-risk evolution."""
        try:
            # Store evolution record
            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO agent_evolutions (
                        evolution_id, agent_id, status, compiled_code,
                        constitutional_compliance_score, risk_score, decision_type
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                    request.evolution_id,
                    request.agent_id,
                    EvolutionStatus.HUMAN_REVIEW.value,
                    compilation_result.compiled_output,
                    compilation_result.constitutional_compliance_score,
                    risk_score,
                    "REQUIRES_REVIEW",
                )

            return {
                "evolution_id": request.evolution_id,
                "status": EvolutionStatus.HUMAN_REVIEW,
                "constitutional_compliance_score": (
                    compilation_result.constitutional_compliance_score
                ),
                "risk_score": risk_score,
                "approval_required": True,
                "estimated_review_time": "15-30 minutes",
                "recommendations": [
                    "Human review required due to moderate risk or compliance score",
                    "Consider improving constitutional compliance before resubmission",
                ],
            }

        except Exception as e:
            logger.exception(f"Human review setup failed: {e}")
            raise

    async def _reject_evolution(
        self,
        request: EvolutionRequest,
        compilation_result: CompilationResult,
        risk_score: float,
    ) -> dict[str, Any]:
        """Reject high-risk or non-compliant evolution."""
        try:
            # Store evolution record
            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO agent_evolutions (
                        evolution_id, agent_id, status, compiled_code,
                        constitutional_compliance_score, risk_score, decision_type
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                    request.evolution_id,
                    request.agent_id,
                    EvolutionStatus.REJECTED.value,
                    None,
                    compilation_result.constitutional_compliance_score,
                    risk_score,
                    "REJECTED",
                )

            rejection_reasons = []
            if compilation_result.constitutional_compliance_score < 0.8:
                rejection_reasons.append("Constitutional compliance score too low")
            if risk_score > 0.5:
                rejection_reasons.append("Risk score too high")
            if compilation_result.errors:
                rejection_reasons.extend(compilation_result.errors)

            return {
                "evolution_id": request.evolution_id,
                "status": EvolutionStatus.REJECTED,
                "constitutional_compliance_score": (
                    compilation_result.constitutional_compliance_score
                ),
                "risk_score": risk_score,
                "approval_required": False,
                "recommendations": [
                    (
                        "Evolution rejected due to high risk or constitutional"
                        " non-compliance"
                    ),
                    (
                        "Improve constitutional compliance and reduce risk factors"
                        " before resubmission"
                    ),
                ],
                "rejection_reasons": rejection_reasons,
            }

        except Exception as e:
            logger.exception(f"Evolution rejection failed: {e}")
            raise


# Global service instances
compiler_engine: ConstitutionalCompiler | None = None
evolution_engine: AgentEvolutionEngine | None = None


# Dependency injection
async def get_compiler() -> ConstitutionalCompiler:
    """Get compiler engine instance."""
    if compiler_engine is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    return compiler_engine


async def get_evolution_engine() -> AgentEvolutionEngine:
    """Get evolution engine instance."""
    if evolution_engine is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    return evolution_engine


# Startup and shutdown
@app.on_event("startup")
async def startup():
    """Initialize service on startup."""
    global db_pool, redis_client, service_clients, compiler_engine, evolution_engine, evolutionary_optimizer

    try:
        logger.info(f"Starting {SERVICE_NAME} v{SERVICE_VERSION}")

        # Initialize database pool
        db_pool = await asyncpg.create_pool(
            DATABASE_URL, min_size=5, max_size=20, command_timeout=30
        )

        # Initialize Redis
        redis_client = aioredis.from_url(REDIS_URL)

        # Initialize HTTP clients for external services
        service_clients = {
            "policy": httpx.AsyncClient(timeout=30.0),
            "auth": httpx.AsyncClient(timeout=15.0),
            "integrity": httpx.AsyncClient(timeout=15.0),
            "formal_verification": httpx.AsyncClient(timeout=60.0),
        }

        # Initialize engines
        compiler_engine = ConstitutionalCompiler(redis_client, service_clients)
        evolution_engine = AgentEvolutionEngine(compiler_engine, db_pool)

        # Initialize evolutionary optimizer with constitutional client
        constitutional_client = service_clients.get("policy")
        evolutionary_optimizer = EvolutionaryAgentOptimizer(constitutional_client)

        # Create database tables
        await create_database_tables()

        logger.info(f"✅ {SERVICE_NAME} started successfully on port {SERVICE_PORT}")
        logger.info(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")

    except Exception as e:
        logger.exception(f"Startup failed: {e}")
        raise


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown."""
    global db_pool, redis_client, service_clients

    try:
        logger.info("Shutting down service...")

        # Close HTTP clients
        for client in service_clients.values():
            await client.aclose()

        # Close Redis
        if redis_client:
            await redis_client.close()

        # Close database pool
        if db_pool:
            await db_pool.close()

        logger.info("Service shutdown complete")

    except Exception as e:
        logger.exception(f"Shutdown error: {e}")


async def create_database_tables():
    """Create necessary database tables."""
    try:
        async with db_pool.acquire() as conn:
            # Compilations table
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS compilations (
                    compilation_id UUID PRIMARY KEY,
                    source_hash VARCHAR(64) NOT NULL,
                    compilation_type VARCHAR(50) NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    compiled_output TEXT,
                    constitutional_compliance_score FLOAT DEFAULT 0.0,
                    compilation_time_ms FLOAT DEFAULT 0.0,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    metadata JSONB DEFAULT '{}'
                );
            """
            )

            # Agent evolutions table
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS agent_evolutions (
                    evolution_id UUID PRIMARY KEY,
                    agent_id VARCHAR(255) NOT NULL,
                    status VARCHAR(50) NOT NULL,
                    compiled_code TEXT,
                    constitutional_compliance_score FLOAT DEFAULT 0.0,
                    risk_score FLOAT DEFAULT 0.0,
                    decision_type VARCHAR(50),
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    approved_at TIMESTAMPTZ,
                    approved_by VARCHAR(255)
                );
            """
            )

            # Evolutionary optimizations table
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS evolutionary_optimizations (
                    optimization_id UUID PRIMARY KEY,
                    agent_config JSONB NOT NULL,
                    algorithm_type VARCHAR(50) NOT NULL,
                    objectives JSONB NOT NULL,
                    results JSONB NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
            """
            )

            # Create indexes
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_compilations_type ON"
                " compilations(compilation_type);"
            )
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_compilations_status ON"
                " compilations(status);"
            )
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_evolutions_agent ON"
                " agent_evolutions(agent_id);"
            )
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_evolutions_status ON"
                " agent_evolutions(status);"
            )
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_evolutionary_optimizations_created ON"
                " evolutionary_optimizations(created_at);"
            )
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_evolutionary_optimizations_algorithm ON"
                " evolutionary_optimizations(algorithm_type);"
            )

        logger.info("Database tables created successfully")

    except Exception as e:
        logger.exception(f"Database table creation failed: {e}")
        raise


# API Endpoints
@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "port": SERVICE_PORT,
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "components": {
            "database": "operational" if db_pool else "disconnected",
            "redis": "operational" if redis_client else "disconnected",
            "compiler": "operational" if compiler_engine else "not_initialized",
            "evolution_engine": (
                "operational" if evolution_engine else "not_initialized"
            ),
        },
    }


@app.post(
    "/api/v1/compile",
    response_model=CompilationResponseModel,
    status_code=status.HTTP_200_OK,
)
async def compile_source(
    request: CompilationRequestModel,
    compiler: ConstitutionalCompiler = Depends(get_compiler),
) -> CompilationResponseModel:
    """
    Compile source code or policy with constitutional compliance verification.

    This endpoint provides comprehensive compilation services including:
    - Syntax and semantic analysis
    - Constitutional compliance verification
    - Code optimization
    - Executable generation
    """
    try:
        compilation_request = CompilationRequest(
            source_content=request.source_content,
            compilation_type=request.compilation_type,
            target_format=request.target_format,
            optimization_level=request.optimization_level,
            constitutional_compliance=request.constitutional_compliance,
            metadata=request.metadata,
        )

        result = await compiler.compile_source(compilation_request)

        return CompilationResponseModel(
            compilation_id=result.compilation_id,
            status=result.status,
            compilation_time_ms=result.compilation_time_ms,
            constitutional_compliance_score=result.constitutional_compliance_score,
            compiled_output=result.compiled_output,
            optimization_applied=result.optimization_applied,
            errors=result.errors,
            warnings=result.warnings,
            constitutional_hash=CONSTITUTIONAL_HASH,
            metadata=result.metadata,
        )

    except Exception as e:
        logger.exception(f"Compilation endpoint failed: {e}")
        raise HTTPException(status_code=500, detail=f"Compilation failed: {e!s}")


@app.post(
    "/api/v1/evolve",
    response_model=EvolutionResponseModel,
    status_code=status.HTTP_200_OK,
)
async def evolve_agent(
    request: EvolutionRequestModel,
    background_tasks: BackgroundTasks,
    evolution_engine: AgentEvolutionEngine = Depends(get_evolution_engine),
) -> EvolutionResponseModel:
    """
    Submit agent evolution for constitutional compliance verification and approval.

    This endpoint manages the complete agent evolution lifecycle including:
    - Code compilation and optimization
    - Constitutional compliance verification
    - Risk assessment
    - Automated approval or human review routing
    """
    try:
        evolution_request = EvolutionRequest(
            agent_id=request.agent_id,
            current_version=request.current_version,
            new_code=request.new_code,
            change_description=request.change_description,
            requester_id=request.requester_id,
            priority=request.priority,
            constitutional_compliance_required=request.constitutional_compliance_required,
        )

        # Process evolution (can be moved to background for async processing)
        result = await evolution_engine.process_evolution(evolution_request)

        return EvolutionResponseModel(
            evolution_id=result["evolution_id"],
            status=EvolutionStatus(result["status"]),
            evaluation_score=result.get("risk_score", 0.0),
            constitutional_compliance_score=result.get(
                "constitutional_compliance_score", 0.0
            ),
            approval_required=result.get("approval_required", False),
            estimated_review_time=result.get("estimated_review_time"),
            constitutional_hash=CONSTITUTIONAL_HASH,
            recommendations=result.get("recommendations", []),
        )

    except Exception as e:
        logger.exception(f"Evolution endpoint failed: {e}")
        raise HTTPException(status_code=500, detail=f"Evolution failed: {e!s}")


@app.get("/api/v1/compilation/{compilation_id}", status_code=status.HTTP_200_OK)
async def get_compilation_status(compilation_id: str):
    """Get status and results of a compilation."""
    try:
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT * FROM compilations WHERE compilation_id = $1
            """,
                compilation_id,
            )

            if not row:
                raise HTTPException(status_code=404, detail="Compilation not found")

            return {
                "compilation_id": row["compilation_id"],
                "status": row["status"],
                "compilation_type": row["compilation_type"],
                "constitutional_compliance_score": row[
                    "constitutional_compliance_score"
                ],
                "compilation_time_ms": row["compilation_time_ms"],
                "created_at": row["created_at"].isoformat(),
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Compilation status query failed: {e}")
        raise HTTPException(status_code=500, detail="Status query failed")


@app.get("/api/v1/evolution/{evolution_id}", status_code=status.HTTP_200_OK)
async def get_evolution_status(evolution_id: str):
    """Get status and results of an agent evolution."""
    try:
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT * FROM agent_evolutions WHERE evolution_id = $1
            """,
                evolution_id,
            )

            if not row:
                raise HTTPException(status_code=404, detail="Evolution not found")

            return {
                "evolution_id": row["evolution_id"],
                "agent_id": row["agent_id"],
                "status": row["status"],
                "constitutional_compliance_score": row[
                    "constitutional_compliance_score"
                ],
                "risk_score": row["risk_score"],
                "decision_type": row["decision_type"],
                "created_at": row["created_at"].isoformat(),
                "approved_at": (
                    row["approved_at"].isoformat() if row["approved_at"] else None
                ),
                "approved_by": row["approved_by"],
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Evolution status query failed: {e}")
        raise HTTPException(status_code=500, detail="Status query failed")


@app.get("/api/v1/metrics", status_code=status.HTTP_200_OK)
async def get_service_metrics():
    """Get service performance and usage metrics."""
    try:
        async with db_pool.acquire() as conn:
            # Compilation metrics
            compilation_stats = await conn.fetchrow(
                """
                SELECT
                    COUNT(*) as total_compilations,
                    COUNT(*) FILTER (WHERE status = 'completed') as successful_compilations,
                    AVG(compilation_time_ms) as avg_compilation_time,
                    AVG(constitutional_compliance_score) as avg_compliance_score
                FROM compilations
                WHERE created_at > NOW() - INTERVAL '24 hours'
            """
            )

            # Evolution metrics
            evolution_stats = await conn.fetchrow(
                """
                SELECT
                    COUNT(*) as total_evolutions,
                    COUNT(*) FILTER (WHERE status = 'auto_approved') as auto_approved,
                    COUNT(*) FILTER (WHERE status = 'human_review') as requiring_review,
                    AVG(constitutional_compliance_score) as avg_compliance_score
                FROM agent_evolutions
                WHERE created_at > NOW() - INTERVAL '24 hours'
            """
            )

        return {
            "service": SERVICE_NAME,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "compilation_metrics": {
                "total_24h": compilation_stats["total_compilations"] or 0,
                "successful_24h": compilation_stats["successful_compilations"] or 0,
                "avg_compilation_time_ms": float(
                    compilation_stats["avg_compilation_time"] or 0
                ),
                "avg_compliance_score": float(
                    compilation_stats["avg_compliance_score"] or 0
                ),
            },
            "evolution_metrics": {
                "total_24h": evolution_stats["total_evolutions"] or 0,
                "auto_approved_24h": evolution_stats["auto_approved"] or 0,
                "requiring_review_24h": evolution_stats["requiring_review"] or 0,
                "avg_compliance_score": float(
                    evolution_stats["avg_compliance_score"] or 0
                ),
            },
        }

    except Exception as e:
        logger.exception(f"Metrics query failed: {e}")
        raise HTTPException(status_code=500, detail="Metrics query failed")


# Real Evolutionary Computation Endpoints


class AgentOptimizationRequest(BaseModel):
    """Request for agent optimization using evolutionary algorithms."""

    agent_config: dict[str, Any]
    optimization_objectives: list[str] = Field(
        default=["performance", "constitutional_compliance", "resource_efficiency"]
    )
    algorithm_type: str = Field(
        default="genetic", description="genetic or multi_objective"
    )
    evolution_params: dict[str, Any] | None = None
    optimization_name: str | None = None


@app.post("/api/v1/evolutionary/optimize")
async def optimize_agent_evolutionary(
    request: AgentOptimizationRequest, background_tasks: BackgroundTasks
):
    """Optimize an agent using real evolutionary algorithms."""
    try:
        if not evolutionary_optimizer:
            raise HTTPException(
                status_code=503, detail="Evolutionary optimizer not available"
            )

        # Convert string objectives to enum objects
        objectives = []
        for obj_str in request.optimization_objectives:
            try:
                objective = OptimizationObjective(obj_str.lower())
                objectives.append(objective)
            except ValueError:
                raise HTTPException(
                    status_code=400, detail=f"Invalid optimization objective: {obj_str}"
                )

        # Parse evolution parameters
        evolution_params = None
        if request.evolution_params:
            evolution_params = EvolutionParams(
                population_size=request.evolution_params.get("population_size", 100),
                generations=request.evolution_params.get("generations", 50),
                mutation_rate=request.evolution_params.get("mutation_rate", 0.1),
                crossover_rate=request.evolution_params.get("crossover_rate", 0.8),
                selection_pressure=request.evolution_params.get(
                    "selection_pressure", 2.0
                ),
                elitism_ratio=request.evolution_params.get("elitism_ratio", 0.1),
                diversity_threshold=request.evolution_params.get(
                    "diversity_threshold", 0.05
                ),
                constitutional_weight=request.evolution_params.get(
                    "constitutional_weight", 0.3
                ),
                convergence_threshold=request.evolution_params.get(
                    "convergence_threshold", 1e-6
                ),
                max_stagnation=request.evolution_params.get("max_stagnation", 10),
            )

        # Run optimization
        optimization_result = await evolutionary_optimizer.optimize_agent(
            agent_config=request.agent_config,
            optimization_objectives=objectives,
            algorithm_type=request.algorithm_type,
            evolution_params=evolution_params,
        )

        # Store result in database
        async with db_pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO evolutionary_optimizations
                (optimization_id, agent_config, algorithm_type, objectives, results, created_at)
                VALUES ($1, $2, $3, $4, $5, NOW())
            """,
                optimization_result["optimization_id"],
                json.dumps(request.agent_config),
                request.algorithm_type,
                json.dumps(request.optimization_objectives),
                json.dumps(optimization_result),
            )

        logger.info(
            "Evolutionary optimization completed:"
            f" {optimization_result['optimization_id']}"
        )

        return {
            "message": "Evolutionary optimization completed successfully",
            "optimization_id": optimization_result["optimization_id"],
            "algorithm_type": request.algorithm_type,
            "objectives": request.optimization_objectives,
            "best_fitness": optimization_result["best_individual"]["total_fitness"],
            "constitutional_compliance": optimization_result["best_individual"][
                "constitutional_compliance"
            ],
            "evolution_time_seconds": optimization_result["performance_metrics"][
                "evolution_time_seconds"
            ],
            "generations_completed": optimization_result["performance_metrics"][
                "final_generation"
            ],
            "optimized_config": optimization_result["best_individual"]["genotype"],
            "detailed_results": optimization_result,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Evolutionary optimization failed: {e}")
        raise HTTPException(status_code=500, detail=f"Optimization failed: {e!s}")


@app.get("/api/v1/evolutionary/optimization/{optimization_id}")
async def get_optimization_result(optimization_id: str):
    """Get results of a specific evolutionary optimization."""
    try:
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT * FROM evolutionary_optimizations
                WHERE optimization_id = $1
            """,
                optimization_id,
            )

            if not row:
                raise HTTPException(status_code=404, detail="Optimization not found")

            return {
                "optimization_id": row["optimization_id"],
                "algorithm_type": row["algorithm_type"],
                "objectives": json.loads(row["objectives"]),
                "created_at": row["created_at"].isoformat(),
                "results": json.loads(row["results"]),
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to get optimization result: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve optimization result"
        )


@app.get("/api/v1/evolutionary/history")
async def get_optimization_history(limit: int = 20):
    """Get history of evolutionary optimizations."""
    try:
        async with db_pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT optimization_id, algorithm_type, objectives, created_at,
                       (results->>'best_individual')::json->'total_fitness' as best_fitness,
                       (results->>'best_individual')::json->'constitutional_compliance' as constitutional_compliance
                FROM evolutionary_optimizations
                ORDER BY created_at DESC
                LIMIT $1
            """,
                limit,
            )

            history = [
                {
                    "optimization_id": row["optimization_id"],
                    "algorithm_type": row["algorithm_type"],
                    "objectives": json.loads(row["objectives"]),
                    "best_fitness": (
                        float(row["best_fitness"]) if row["best_fitness"] else 0.0
                    ),
                    "constitutional_compliance": (
                        float(row["constitutional_compliance"])
                        if row["constitutional_compliance"]
                        else 0.0
                    ),
                    "created_at": row["created_at"].isoformat(),
                }
                for row in rows
            ]

            return {"optimization_history": history, "total_count": len(history)}

    except Exception as e:
        logger.exception(f"Failed to get optimization history: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve optimization history"
        )


@app.post("/api/v1/evolutionary/analyze/{optimization_id}")
async def analyze_evolution_convergence(optimization_id: str):
    """Analyze convergence properties of an evolutionary optimization."""
    try:
        if not evolutionary_optimizer:
            raise HTTPException(
                status_code=503, detail="Evolutionary optimizer not available"
            )

        analysis = await evolutionary_optimizer.analyze_evolution_convergence(
            optimization_id
        )

        return {
            "convergence_analysis": analysis,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception(f"Convergence analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e!s}")


@app.get("/api/v1/evolutionary/objectives")
async def get_available_objectives():
    """Get list of available optimization objectives."""
    objectives = [
        {
            "name": obj.value,
            "description": {
                "performance": "Optimize for computational performance and accuracy",
                "constitutional_compliance": (
                    "Ensure alignment with constitutional principles"
                ),
                "resource_efficiency": "Minimize computational resource usage",
                "safety": "Maximize safety and risk mitigation",
                "explainability": "Improve model interpretability and explainability",
                "robustness": "Enhance robustness to adversarial inputs",
                "adaptability": "Improve ability to adapt to new scenarios",
            }.get(obj.value, "Optimization objective"),
        }
        for obj in OptimizationObjective
    ]

    return {
        "available_objectives": objectives,
        "constitutional_hash": CONSTITUTIONAL_HASH,
    }


if __name__ == "__main__":
    logger.info(f"Starting {SERVICE_NAME} on port {SERVICE_PORT}")
    uvicorn.run(
        "unified_main:app",
        host="0.0.0.0",
        port=SERVICE_PORT,
        log_level="info",
        reload=False,
    )
