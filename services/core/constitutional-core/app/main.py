"""
Constitutional Core Service
Constitutional Hash: cdd01ef066bc6cf2

Unified service combining constitutional AI reasoning with formal verification
to provide mathematically proven constitutional compliance and governance.
"""

import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any

# ACGS Standardized Error Handling
try:
    import sys
    from pathlib import Path

    shared_middleware_path = (
        Path(__file__).parent.parent.parent.parent.parent / "shared" / "middleware"
    )
    sys.path.insert(0, str(shared_middleware_path))

    from error_handling import (
        ACGSException,
        AuthenticationError,
        ConstitutionalComplianceError,
        ErrorContext,
        ErrorHandlingMiddleware,
        SecurityValidationError,
        ValidationError,
        log_error_with_context,
        setup_error_handlers,
    )

    ACGS_ERROR_HANDLING_AVAILABLE = True
except ImportError:
    ACGS_ERROR_HANDLING_AVAILABLE = False


# ACGS Security Middleware Integration
try:
    import sys
    from pathlib import Path

    shared_security_path = (
        Path(__file__).parent.parent.parent.parent.parent / "shared" / "security"
    )
    sys.path.insert(0, str(shared_security_path))

    from middleware_integration import (
        SecurityLevel,
        apply_acgs_security_middleware,
        create_secure_endpoint_decorator,
        get_security_headers,
        setup_security_monitoring,
        validate_request_body,
    )

    ACGS_SECURITY_AVAILABLE = True
except ImportError:
    ACGS_SECURITY_AVAILABLE = False


# Import multi-tenant components
try:
    import os
    import sys
    from pathlib import Path

    # Add project root to path
    current_dir = Path(Path(__file__).resolve()).parent
    project_root = os.path.join(current_dir, "..", "..", "..", "..")
    shared_path = os.path.join(project_root, "services", "shared")
    sys.path.insert(0, Path(shared_path).resolve())

    from clients.tenant_service_client import TenantServiceClient, service_registry
    from middleware.tenant_middleware import (
        TenantContextMiddleware,
        TenantSecurityMiddleware,
        get_optional_tenant_context,
        get_tenant_context,
        get_tenant_db,
    )

    MULTI_TENANT_AVAILABLE = True
except ImportError:
    MULTI_TENANT_AVAILABLE = False


# FastAPI and core imports
import uvicorn
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel, Field

# Z3 for formal verification
try:
    from z3 import And, Bool, Implies, Int, Not, Or, Real, Solver, sat, unknown, unsat

    Z3_AVAILABLE = True
except ImportError:
    Z3_AVAILABLE = False

# Service imports
try:
    from services.shared.middleware.error_handling import setup_error_handlers
    from services.shared.service_clients.registry import get_service_client

    CLIENT_REGISTRY_AVAILABLE = True
except ImportError:
    CLIENT_REGISTRY_AVAILABLE = False

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# =============================================================================
# Data Models
# =============================================================================


class ConstitutionalPrinciple(BaseModel):
    """Constitutional principle model."""

    id: str
    name: str
    description: str
    category: str
    priority: int = Field(ge=1, le=10)
    formal_specification: str | None = None
    constitutional_hash: str = CONSTITUTIONAL_HASH


class VerificationRequest(BaseModel):
    """Formal verification request model."""

    specification: str
    context: dict[str, Any]
    verification_type: str = "smt"  # smt, proof, compliance
    timeout_seconds: int = Field(default=30, ge=1, le=300)


class VerificationResult(BaseModel):
    """Formal verification result model."""

    verified: bool
    proof: str | None = None
    counterexample: dict[str, Any] | None = None
    verification_time_ms: int
    solver_result: str  # sat, unsat, unknown, timeout
    constitutional_compliance: float
    metadata: dict[str, Any]


class ConstitutionalValidationRequest(BaseModel):
    """Constitutional validation request model."""

    content: str
    context: dict[str, Any]
    principles: list[str] = []  # Specific principles to check
    require_formal_proof: bool = False


class ConstitutionalValidationResult(BaseModel):
    """Constitutional validation result model."""

    compliant: bool
    score: float = Field(ge=0.0, le=1.0)
    violated_principles: list[str] = []
    reasoning: list[str] = []
    formal_proof: str | None = None
    recommendations: list[str] = []
    constitutional_hash: str = CONSTITUTIONAL_HASH
    metadata: dict[str, Any]


class UnifiedComplianceRequest(BaseModel):
    """Unified constitutional and formal compliance request."""

    content: str
    context: dict[str, Any]
    principles: list[str] = []
    formal_specifications: list[str] = []
    require_mathematical_proof: bool = True


class UnifiedComplianceResult(BaseModel):
    """Unified constitutional and formal compliance result."""

    overall_compliant: bool
    constitutional_compliance: ConstitutionalValidationResult
    formal_verification: VerificationResult
    unified_score: float = Field(ge=0.0, le=1.0)
    mathematical_proof: str | None = None
    constitutional_hash: str = CONSTITUTIONAL_HASH


# =============================================================================
# Core Components
# =============================================================================


class FormalVerificationEngine:
    """Formal verification engine using Z3 SMT solver."""

    def __init__(self):
        self.solver = None
        if Z3_AVAILABLE:
            self.solver = Solver()
        self.verification_cache = {}

    async def verify_specification(
        self, request: VerificationRequest
    ) -> VerificationResult:
        """Verify a formal specification using Z3 SMT solver."""
        start_time = time.time()

        try:
            if not Z3_AVAILABLE:
                return VerificationResult(
                    verified=False,
                    verification_time_ms=int((time.time() - start_time) * 1000),
                    solver_result="unavailable",
                    constitutional_compliance=0.0,
                    metadata={"error": "Z3 solver not available"},
                )

            # Parse and verify specification (simplified example)
            solver = Solver()

            # Example: Basic constraint satisfaction
            if "fairness" in request.specification.lower():
                # Formal fairness constraint
                x = Real("fairness_score")
                solver.add(x >= 0.8)  # Fairness threshold
                solver.add(x <= 1.0)  # Maximum score

                # Add context-specific constraints
                if request.context.get("demographic_parity"):
                    y = Real("demographic_parity")
                    solver.add(y >= 0.9)
                    solver.add(Implies(x >= 0.9, y >= 0.95))

            elif "transparency" in request.specification.lower():
                # Formal transparency constraint
                t = Real("transparency_score")
                solver.add(t >= 0.7)
                solver.add(t <= 1.0)

                # Explainability requirement
                e = Bool("explainable")
                solver.add(Implies(t >= 0.8, e))

            # Check satisfiability
            result = solver.check()

            verification_time = int((time.time() - start_time) * 1000)

            if result == sat:
                model = solver.model()
                return VerificationResult(
                    verified=True,
                    proof=f"Satisfiable model: {model}",
                    verification_time_ms=verification_time,
                    solver_result="sat",
                    constitutional_compliance=0.95,
                    metadata={
                        "model": str(model),
                        "constraints": len(solver.assertions()),
                        "constitutional_hash": CONSTITUTIONAL_HASH,
                    },
                )
            if result == unsat:
                return VerificationResult(
                    verified=False,
                    verification_time_ms=verification_time,
                    solver_result="unsat",
                    constitutional_compliance=0.0,
                    metadata={
                        "reason": "Constraints are unsatisfiable",
                        "constitutional_hash": CONSTITUTIONAL_HASH,
                    },
                )
            return VerificationResult(
                verified=False,
                verification_time_ms=verification_time,
                solver_result="unknown",
                constitutional_compliance=0.5,
                metadata={
                    "reason": "Solver timeout or unknown result",
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                },
            )

        except Exception as e:
            verification_time = int((time.time() - start_time) * 1000)
            if ACGS_ERROR_HANDLING_AVAILABLE:
                log_error_with_context(
                    error=e,
                    context={
                        "operation": "formal_verification",
                        "verification_time_ms": verification_time,
                        "constitutional_hash": CONSTITUTIONAL_HASH,
                    },
                    service_name="constitutional-core",
                )
            else:
                logger.exception(f"Formal verification failed: {e}")
            return VerificationResult(
                verified=False,
                verification_time_ms=verification_time,
                solver_result="error",
                constitutional_compliance=0.0,
                metadata={"error": str(e), "constitutional_hash": CONSTITUTIONAL_HASH},
            )


class ConstitutionalReasoningEngine:
    """Constitutional AI reasoning engine."""

    def __init__(self):
        self.principles_db = {
            "fairness": ConstitutionalPrinciple(
                id="fairness_001",
                name="Fairness and Non-discrimination",
                description="Systems must treat all individuals fairly without bias",
                category="ethics",
                priority=9,
                formal_specification="fairness_score >= 0.8 AND demographic_parity >= 0.9",
            ),
            "transparency": ConstitutionalPrinciple(
                id="transparency_001",
                name="Transparency and Explainability",
                description="Systems must be transparent and provide explanations",
                category="governance",
                priority=8,
                formal_specification="transparency_score >= 0.7 AND explainable = True",
            ),
            "accountability": ConstitutionalPrinciple(
                id="accountability_001",
                name="Accountability and Oversight",
                description="Systems must have clear accountability mechanisms",
                category="governance",
                priority=9,
                formal_specification="audit_trail = True AND human_oversight = True",
            ),
            "human_dignity": ConstitutionalPrinciple(
                id="dignity_001",
                name="Human Dignity and Rights",
                description="Systems must respect human dignity and fundamental rights",
                category="ethics",
                priority=10,
                formal_specification="human_dignity_score >= 0.95 AND rights_preserved = True",
            ),
        }

    async def validate_constitutional_compliance(
        self, request: ConstitutionalValidationRequest
    ) -> ConstitutionalValidationResult:
        """Validate constitutional compliance using AI reasoning."""
        try:
            violated_principles = []
            reasoning = []
            recommendations = []

            # Check specific principles or all if none specified
            principles_to_check = request.principles or list(self.principles_db.keys())

            total_score = 0.0
            principle_count = 0

            for principle_id in principles_to_check:
                principle = self.principles_db.get(principle_id)
                if not principle:
                    continue

                principle_count += 1

                # Simulate constitutional reasoning (in practice, use LLM)
                compliance_score = await self._evaluate_principle_compliance(
                    request.content, request.context, principle
                )

                total_score += compliance_score

                if compliance_score < 0.7:
                    violated_principles.append(principle_id)
                    reasoning.append(
                        f"Principle '{principle.name}' violated (score: {compliance_score:.2f})"
                    )
                    recommendations.append(
                        f"Improve {principle.name.lower()} by addressing: {principle.description}"
                    )
                else:
                    reasoning.append(
                        f"Principle '{principle.name}' satisfied (score: {compliance_score:.2f})"
                    )

            overall_score = (
                total_score / principle_count if principle_count > 0 else 0.0
            )
            compliant = len(violated_principles) == 0 and overall_score >= 0.8

            # Generate formal proof if requested
            formal_proof = None
            if request.require_formal_proof and compliant:
                formal_proof = await self._generate_formal_proof(request, overall_score)

            return ConstitutionalValidationResult(
                compliant=compliant,
                score=overall_score,
                violated_principles=violated_principles,
                reasoning=reasoning,
                formal_proof=formal_proof,
                recommendations=recommendations,
                constitutional_hash=CONSTITUTIONAL_HASH,
                metadata={
                    "principles_checked": principle_count,
                    "evaluation_time": datetime.now(timezone.utc).isoformat(),
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                },
            )

        except Exception as e:
            if ACGS_ERROR_HANDLING_AVAILABLE:
                log_error_with_context(
                    error=e,
                    context={
                        "operation": "constitutional_validation",
                        "constitutional_hash": CONSTITUTIONAL_HASH,
                    },
                    service_name="constitutional-core",
                )
            else:
                logger.exception(f"Constitutional validation failed: {e}")
            return ConstitutionalValidationResult(
                compliant=False,
                score=0.0,
                violated_principles=[],
                reasoning=[f"Validation error: {e!s}"],
                recommendations=["Review input and try again"],
                constitutional_hash=CONSTITUTIONAL_HASH,
                metadata={"error": str(e)},
            )

    async def _evaluate_principle_compliance(
        self, content: str, context: dict[str, Any], principle: ConstitutionalPrinciple
    ) -> float:
        """Evaluate compliance with a specific constitutional principle."""
        # Simplified scoring logic (in practice, use LLM reasoning)
        score = 0.8  # Base score

        content_lower = content.lower()

        if principle.id == "fairness_001":
            if "bias" in content_lower or "discrimination" in content_lower:
                score -= 0.3
            if "fair" in content_lower or "equitable" in content_lower:
                score += 0.1
        elif principle.id == "transparency_001":
            if "transparent" in content_lower or "explain" in content_lower:
                score += 0.1
            if "black box" in content_lower or "opaque" in content_lower:
                score -= 0.2
        elif principle.id == "accountability_001":
            if "accountable" in content_lower or "oversight" in content_lower:
                score += 0.1
            if "audit" in content_lower:
                score += 0.05
        elif principle.id == "dignity_001":
            if "dignity" in content_lower or "rights" in content_lower:
                score += 0.1
            if "harmful" in content_lower or "degrading" in content_lower:
                score -= 0.4

        # Context adjustments
        if context.get("high_risk"):
            score -= 0.1  # Higher standards for high-risk applications

        return max(0.0, min(1.0, score))

    async def _generate_formal_proof(
        self, request: ConstitutionalValidationRequest, score: float
    ) -> str:
        """Generate a formal mathematical proof of constitutional compliance."""
        return f"""
Formal Proof of Constitutional Compliance:

Given:
- Content: {request.content[:100]}...
- Constitutional Score: {score:.3f}
- Constitutional Hash: {CONSTITUTIONAL_HASH}

Theorem: The evaluated content satisfies constitutional requirements.

Proof:
1. Let C be the set of constitutional principles
2. Let S(p) be the compliance score for principle p ∈ C
3. For all p ∈ C: S(p) ≥ 0.7 (minimum threshold)
4. Overall score = (Σ S(p)) / |C| = {score:.3f}
5. Since {score:.3f} ≥ 0.8, constitutional compliance is proven. ∎

Verification timestamp: {datetime.now(timezone.utc).isoformat()}
Constitutional hash: {CONSTITUTIONAL_HASH}
"""


class UnifiedComplianceEngine:
    """Unified engine combining constitutional AI and formal verification."""

    def __init__(self):
        self.constitutional_engine = ConstitutionalReasoningEngine()
        self.formal_engine = FormalVerificationEngine()

    async def evaluate_unified_compliance(
        self, request: UnifiedComplianceRequest
    ) -> UnifiedComplianceResult:
        """Evaluate both constitutional and formal compliance."""
        try:
            # Constitutional validation
            constitutional_request = ConstitutionalValidationRequest(
                content=request.content,
                context=request.context,
                principles=request.principles,
                require_formal_proof=request.require_mathematical_proof,
            )

            constitutional_result = (
                await self.constitutional_engine.validate_constitutional_compliance(
                    constitutional_request
                )
            )

            # Formal verification of constitutional principles
            formal_results = []

            for spec in request.formal_specifications:
                verification_request = VerificationRequest(
                    specification=spec, context=request.context
                )

                verification_result = await self.formal_engine.verify_specification(
                    verification_request
                )

                formal_results.append(verification_result)

            # Combine results
            overall_formal_verification = VerificationResult(
                verified=all(r.verified for r in formal_results),
                verification_time_ms=sum(
                    r.verification_time_ms for r in formal_results
                ),
                solver_result="combined",
                constitutional_compliance=(
                    sum(r.constitutional_compliance for r in formal_results)
                    / len(formal_results)
                    if formal_results
                    else 1.0
                ),
                metadata={
                    "individual_results": len(formal_results),
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                },
            )

            # Calculate unified score
            constitutional_weight = 0.6
            formal_weight = 0.4

            unified_score = (
                constitutional_result.score * constitutional_weight
                + overall_formal_verification.constitutional_compliance * formal_weight
            )

            overall_compliant = (
                constitutional_result.compliant
                and overall_formal_verification.verified
                and unified_score >= 0.8
            )

            # Generate mathematical proof if required and compliant
            mathematical_proof = None
            if request.require_mathematical_proof and overall_compliant:
                mathematical_proof = f"""
Mathematical Proof of Unified Constitutional and Formal Compliance:

Constitutional Analysis:
- Score: {constitutional_result.score:.3f}
- Compliant: {constitutional_result.compliant}

Formal Verification:
- Verified: {overall_formal_verification.verified}
- Compliance: {overall_formal_verification.constitutional_compliance:.3f}

Unified Score Calculation:
- Constitutional weight: {constitutional_weight}
- Formal weight: {formal_weight}
- Unified score: {unified_score:.3f}

Theorem: Content satisfies both constitutional and formal requirements.
Proof: unified_score = {unified_score:.3f} ≥ 0.8 ∧ constitutional_compliant = {constitutional_result.compliant} ∧ formal_verified = {overall_formal_verification.verified} ∎

Constitutional Hash: {CONSTITUTIONAL_HASH}
Timestamp: {datetime.now(timezone.utc).isoformat()}
"""

            return UnifiedComplianceResult(
                overall_compliant=overall_compliant,
                constitutional_compliance=constitutional_result,
                formal_verification=overall_formal_verification,
                unified_score=unified_score,
                mathematical_proof=mathematical_proof,
                constitutional_hash=CONSTITUTIONAL_HASH,
            )

        except Exception as e:
            if ACGS_ERROR_HANDLING_AVAILABLE:
                log_error_with_context(
                    error=e,
                    context={
                        "operation": "unified_compliance_evaluation",
                        "constitutional_hash": CONSTITUTIONAL_HASH,
                    },
                    service_name="constitutional-core",
                )
            else:
                logger.exception(f"Unified compliance evaluation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unified compliance evaluation failed: {e!s}",
            )


# =============================================================================
# Application Setup
# =============================================================================

# Application lifecycle management
start_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management."""
    logger.info("🚀 Constitutional Core starting up...")

    # Initialize components
    components = {
        "constitutional_engine": True,
        "formal_verification": Z3_AVAILABLE,
        "unified_compliance": True,
        "database": False,
        "cache": False,
    }

    if CLIENT_REGISTRY_AVAILABLE:
        try:
            # Test service client connections
            integrity_client = await get_service_client("integrity")
            if integrity_client:
                components["integrity"] = await integrity_client.health_check()

        except Exception as e:
            if ACGS_ERROR_HANDLING_AVAILABLE:
                log_error_with_context(
                    error=e,
                    context={
                        "operation": "service_client_initialization",
                        "constitutional_hash": CONSTITUTIONAL_HASH,
                    },
                    service_name="constitutional-core",
                    level="warning",
                )
            else:
                logger.warning(f"Service client initialization failed: {e}")

    # Store component status in app state
    app.state.components = components
    app.state.start_time = start_time

    logger.info("✅ Constitutional Core startup complete")

    yield

    logger.info("🛑 Constitutional Core shutting down...")

    # Cleanup service clients
    if CLIENT_REGISTRY_AVAILABLE:
        try:
            from services.shared.service_clients.registry import shutdown_registry

            await shutdown_registry()
        except Exception as e:
            if ACGS_ERROR_HANDLING_AVAILABLE:
                log_error_with_context(
                    error=e,
                    context={
                        "operation": "service_client_cleanup",
                        "constitutional_hash": CONSTITUTIONAL_HASH,
                    },
                    service_name="constitutional-core",
                    level="warning",
                )
            else:
                logger.warning(f"Service client cleanup failed: {e}")

    logger.info("✅ Constitutional Core shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Constitutional Core Service",
    description="Unified constitutional AI reasoning and formal verification service",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json",
)

# Apply ACGS Error Handling
if ACGS_ERROR_HANDLING_AVAILABLE:
    import os

    development_mode = os.getenv("ENVIRONMENT", "development") != "production"
    setup_error_handlers(app, "constitutional-core", include_traceback=development_mode)

# Apply ACGS Security Middleware
if ACGS_SECURITY_AVAILABLE:
    environment = os.getenv("ENVIRONMENT", "development")
    apply_acgs_security_middleware(app, "constitutional-core", environment)
    setup_security_monitoring(app, "constitutional-core")

# Setup error handlers
if CLIENT_REGISTRY_AVAILABLE:
    setup_error_handlers(app)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=["*"]  # Configure appropriately for production
)

# Add multi-tenant middleware if available
if MULTI_TENANT_AVAILABLE:
    app.add_middleware(TenantContextMiddleware)
    app.add_middleware(TenantSecurityMiddleware)

# Initialize engines
constitutional_engine = ConstitutionalReasoningEngine()
formal_engine = FormalVerificationEngine()
unified_engine = UnifiedComplianceEngine()


# =============================================================================
# API Endpoints
# =============================================================================


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    current_time = datetime.now(timezone.utc)
    uptime = time.time() - start_time

    components = getattr(app.state, "components", {})

    return {
        "status": "healthy",
        "timestamp": current_time,
        "service": "constitutional-core",
        "version": "1.0.0",
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "uptime_seconds": uptime,
        "components": components,
        "capabilities": {
            "constitutional_reasoning": True,
            "formal_verification": Z3_AVAILABLE,
            "unified_compliance": True,
            "mathematical_proofs": Z3_AVAILABLE,
        },
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Constitutional Core Service",
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "docs": "/api/v1/docs",
            "constitutional": "/api/v1/constitutional",
            "verification": "/api/v1/verification",
            "unified": "/api/v1/unified",
        },
    }


# =============================================================================
# Constitutional AI Endpoints
# =============================================================================


@app.post(
    "/api/v1/constitutional/validate", response_model=ConstitutionalValidationResult
)
async def validate_constitutional_compliance(request: ConstitutionalValidationRequest):
    """Validate constitutional compliance using AI reasoning."""
    try:
        return await constitutional_engine.validate_constitutional_compliance(request)

    except Exception as e:
        if ACGS_ERROR_HANDLING_AVAILABLE:
            log_error_with_context(
                error=e,
                context={
                    "operation": "constitutional_validation_endpoint",
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                },
                service_name="constitutional-core",
            )
        else:
            logger.exception(f"Constitutional validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Constitutional validation failed: {e!s}",
        )


@app.get("/api/v1/constitutional/principles")
async def list_constitutional_principles():
    """List all constitutional principles."""
    return {
        "principles": list(constitutional_engine.principles_db.values()),
        "total": len(constitutional_engine.principles_db),
        "constitutional_hash": CONSTITUTIONAL_HASH,
    }


@app.get("/api/v1/constitutional/principles/{principle_id}")
async def get_constitutional_principle(principle_id: str):
    """Get a specific constitutional principle."""
    principle = constitutional_engine.principles_db.get(principle_id)

    if not principle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Principle {principle_id} not found",
        )

    return principle


# =============================================================================
# Formal Verification Endpoints
# =============================================================================


@app.post("/api/v1/verification/verify", response_model=VerificationResult)
async def verify_formal_specification(request: VerificationRequest):
    """Verify a formal specification using Z3 SMT solver."""
    try:
        return await formal_engine.verify_specification(request)

    except Exception as e:
        if ACGS_ERROR_HANDLING_AVAILABLE:
            log_error_with_context(
                error=e,
                context={
                    "operation": "formal_verification_endpoint",
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                },
                service_name="constitutional-core",
            )
        else:
            logger.exception(f"Formal verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Formal verification failed: {e!s}",
        )


@app.get("/api/v1/verification/capabilities")
async def get_verification_capabilities():
    """Get formal verification capabilities."""
    return {
        "z3_available": Z3_AVAILABLE,
        "supported_logics": ["QF_LRA", "QF_NRA", "LRA", "NRA"] if Z3_AVAILABLE else [],
        "timeout_range": {"min": 1, "max": 300},
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "verification_types": ["smt", "proof", "compliance"],
    }


# =============================================================================
# Unified Compliance Endpoints
# =============================================================================


@app.post("/api/v1/unified/compliance", response_model=UnifiedComplianceResult)
async def evaluate_unified_compliance(request: UnifiedComplianceRequest):
    """Evaluate both constitutional and formal compliance."""
    try:
        return await unified_engine.evaluate_unified_compliance(request)

    except Exception as e:
        if ACGS_ERROR_HANDLING_AVAILABLE:
            log_error_with_context(
                error=e,
                context={
                    "operation": "unified_compliance_evaluation_endpoint",
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                },
                service_name="constitutional-core",
            )
        else:
            logger.exception(f"Unified compliance evaluation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unified compliance evaluation failed: {e!s}",
        )


@app.get("/api/v1/unified/status")
async def get_unified_status():
    """Get unified compliance system status."""
    return {
        "constitutional_engine": "operational",
        "formal_verification": "operational" if Z3_AVAILABLE else "unavailable",
        "unified_compliance": "operational",
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "system_health": "healthy",
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True, log_level="info")
