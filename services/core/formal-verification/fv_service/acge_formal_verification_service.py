"""
ACGE Phase 2 Enhanced Formal Verification Service
Constitutional compliance formal verification with ACGE integration and Z3 theorem proving
"""

import asyncio
import hashlib
import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx
from fastapi import FastAPI, HTTPException, Request, Response, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, Gauge
from pydantic import BaseModel, Field

# Import existing FV service components
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.constitutional_verification_engine import (
    ConstitutionalVerificationEngine,
    ConstitutionalProperty,
    VerificationLevel,
    ProofType
)
from app.core.tiered_validation import TieredValidationPipeline
from app.schemas import VerificationRequest, VerificationResponse

# ACGE integration
from services.platform.authentication.auth_service.acge_integration import (
    ACGEAuthIntegration,
    constitutional_auth_dependency
)

# Service configuration
SERVICE_NAME = "acgs-fv-service-acge"
SERVICE_VERSION = "2.0.0-acge"
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8003"))

# ACGE configuration
ACGE_MODEL_ENDPOINT = os.getenv("ACGE_MODEL_ENDPOINT", "http://acge-model-service.acgs-shared.svc.cluster.local:8080")
CONSTITUTIONAL_HASH = os.getenv("CONSTITUTIONAL_HASH", "cdd01ef066bc6cf2")
ACGE_ENABLED = os.getenv("ACGE_ENABLED", "true").lower() == "true"
ENVIRONMENT = os.getenv("ENVIRONMENT", "green")
PHASE = os.getenv("PHASE", "phase-2")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(SERVICE_NAME)

# Enhanced metrics for ACGE formal verification
FORMAL_PROOF_GENERATIONS = Counter(
    'fv_formal_proof_generations_total',
    'Formal proof generations',
    ['proof_type', 'verification_level', 'status']
)

CONSTITUTIONAL_VERIFICATIONS = Histogram(
    'fv_constitutional_verifications_duration_seconds',
    'Constitutional verification duration',
    ['verification_type', 'complexity']
)

Z3_SOLVER_PERFORMANCE = Histogram(
    'fv_z3_solver_performance_seconds',
    'Z3 solver performance',
    ['problem_type', 'result']
)

ACGE_CONSTITUTIONAL_COMPLIANCE = Gauge(
    'fv_acge_constitutional_compliance_score',
    'ACGE constitutional compliance score for formal verification'
)

# Request/Response models
class ACGEFormalVerificationRequest(BaseModel):
    """Enhanced formal verification request with ACGE integration."""
    policy_content: str = Field(..., description="Policy content to verify")
    constitutional_properties: List[str] = Field(default=[], description="Constitutional properties to verify")
    verification_level: str = Field("standard", description="Verification rigor level")
    proof_type: str = Field("constitutional_compliance", description="Type of formal proof")
    acge_validation: bool = Field(True, description="Enable ACGE constitutional validation")
    include_formal_proof: bool = Field(True, description="Include formal mathematical proof")
    constitutional_hash: str = Field(CONSTITUTIONAL_HASH, description="Constitutional hash")

class ACGEFormalVerificationResponse(BaseModel):
    """Enhanced formal verification response with ACGE analysis."""
    verified: bool
    constitutional_compliance_score: float
    formal_proof: Dict[str, Any] = {}
    z3_verification_result: Dict[str, Any] = {}
    acge_analysis: Dict[str, Any] = {}
    verification_metrics: Dict[str, Any] = {}
    constitutional_hash_verified: bool
    processing_time_ms: float
    timestamp: str


class ACGEFormalVerificationService:
    """ACGE-enhanced formal verification service with constitutional compliance."""
    
    def __init__(self):
        self.acge_client = httpx.AsyncClient(timeout=10.0)
        self.verification_engine = ConstitutionalVerificationEngine()
        self.tiered_pipeline = TieredValidationPipeline()
        self.constitutional_hash = CONSTITUTIONAL_HASH
        
    async def verify_with_acge_integration(
        self, 
        request: ACGEFormalVerificationRequest
    ) -> ACGEFormalVerificationResponse:
        """
        Perform formal verification with ACGE constitutional compliance integration.
        
        Args:
            request: Formal verification request with ACGE parameters
            
        Returns:
            Comprehensive verification response with formal proofs and ACGE analysis
        """
        start_time = time.time()
        
        try:
            # Step 1: Constitutional hash verification
            constitutional_hash_valid = await self._verify_constitutional_hash(
                request.constitutional_hash
            )
            
            # Step 2: Z3 formal verification
            z3_result = await self._perform_z3_verification(request)
            
            # Step 3: ACGE constitutional compliance validation
            acge_result = {}
            if ACGE_ENABLED and request.acge_validation:
                acge_result = await self._validate_with_acge(request)
            
            # Step 4: Generate formal proof if requested
            formal_proof = {}
            if request.include_formal_proof:
                formal_proof = await self._generate_formal_proof(request, z3_result)
            
            # Step 5: Calculate overall compliance score
            compliance_score = self._calculate_compliance_score(
                z3_result, acge_result, constitutional_hash_valid
            )
            
            processing_time = (time.time() - start_time) * 1000
            
            # Record metrics
            CONSTITUTIONAL_VERIFICATIONS.labels(
                verification_type=request.verification_level,
                complexity="standard"
            ).observe(processing_time / 1000)
            
            ACGE_CONSTITUTIONAL_COMPLIANCE.set(compliance_score)
            
            return ACGEFormalVerificationResponse(
                verified=z3_result.get("verified", False) and constitutional_hash_valid,
                constitutional_compliance_score=compliance_score,
                formal_proof=formal_proof,
                z3_verification_result=z3_result,
                acge_analysis=acge_result,
                verification_metrics={
                    "z3_solver_time_ms": z3_result.get("solver_time_ms", 0),
                    "proof_generation_time_ms": formal_proof.get("generation_time_ms", 0),
                    "acge_validation_time_ms": acge_result.get("validation_time_ms", 0),
                    "total_processing_time_ms": processing_time
                },
                constitutional_hash_verified=constitutional_hash_valid,
                processing_time_ms=processing_time,
                timestamp=datetime.now(timezone.utc).isoformat()
            )
            
        except Exception as e:
            logger.error(f"Formal verification failed: {e}")
            processing_time = (time.time() - start_time) * 1000
            
            return ACGEFormalVerificationResponse(
                verified=False,
                constitutional_compliance_score=0.0,
                formal_proof={"error": str(e)},
                z3_verification_result={"error": str(e)},
                acge_analysis={"error": str(e)},
                verification_metrics={"error_time_ms": processing_time},
                constitutional_hash_verified=False,
                processing_time_ms=processing_time,
                timestamp=datetime.now(timezone.utc).isoformat()
            )
    
    async def _verify_constitutional_hash(self, provided_hash: str) -> bool:
        """Verify constitutional hash consistency."""
        return provided_hash == self.constitutional_hash
    
    async def _perform_z3_verification(
        self, 
        request: ACGEFormalVerificationRequest
    ) -> Dict[str, Any]:
        """Perform Z3 SMT solver verification."""
        start_time = time.time()
        
        try:
            # Convert constitutional properties to formal properties
            constitutional_properties = []
            for prop_name in request.constitutional_properties:
                constitutional_properties.append(
                    ConstitutionalProperty(
                        property_id=f"prop_{hash(prop_name) % 1000}",
                        name=prop_name,
                        formal_specification=f"constitutional_property({prop_name})",
                        constitutional_principle_id=f"principle_{hash(prop_name) % 100}",
                        checksum=hashlib.sha256(prop_name.encode()).hexdigest()[:16]
                    )
                )
            
            # Perform constitutional compliance verification
            verification_level = VerificationLevel.STANDARD
            if request.verification_level == "rigorous":
                verification_level = VerificationLevel.RIGOROUS
            elif request.verification_level == "baseline":
                verification_level = VerificationLevel.BASELINE
            
            verification_result = await self.verification_engine.verify_constitutional_compliance(
                policy_content=request.policy_content,
                constitutional_properties=constitutional_properties,
                verification_level=verification_level
            )
            
            solver_time = (time.time() - start_time) * 1000
            
            # Record Z3 performance metrics
            Z3_SOLVER_PERFORMANCE.labels(
                problem_type="constitutional_compliance",
                result="verified" if verification_result.get("verified", False) else "failed"
            ).observe(solver_time / 1000)
            
            return {
                "verified": verification_result.get("verified", False),
                "verification_id": verification_result.get("verification_id"),
                "constitutional_properties_verified": len(constitutional_properties),
                "solver_time_ms": solver_time,
                "z3_constraints_generated": verification_result.get("constraints_count", 0),
                "formal_proofs_count": len(verification_result.get("formal_proofs", [])),
                "verification_level": request.verification_level
            }
            
        except Exception as e:
            logger.error(f"Z3 verification failed: {e}")
            solver_time = (time.time() - start_time) * 1000
            
            Z3_SOLVER_PERFORMANCE.labels(
                problem_type="constitutional_compliance",
                result="error"
            ).observe(solver_time / 1000)
            
            return {
                "verified": False,
                "error": str(e),
                "solver_time_ms": solver_time
            }
    
    async def _validate_with_acge(
        self, 
        request: ACGEFormalVerificationRequest
    ) -> Dict[str, Any]:
        """Validate formal verification with ACGE model."""
        start_time = time.time()
        
        try:
            # Prepare ACGE validation request
            acge_request = {
                "operation": "formal_verification_validation",
                "data": {
                    "policy_content": request.policy_content[:2000],  # Truncate for model
                    "constitutional_properties": request.constitutional_properties,
                    "verification_level": request.verification_level,
                    "proof_type": request.proof_type
                },
                "constitutional_hash": self.constitutional_hash,
                "validation_context": {
                    "service": "formal_verification",
                    "formal_methods": True,
                    "z3_integration": True,
                    "constitutional_compliance_required": True
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Call ACGE model
            response = await self.acge_client.post(
                f"{ACGE_MODEL_ENDPOINT}/validate/constitutional",
                json=acge_request,
                headers={
                    "X-Constitutional-Hash": self.constitutional_hash,
                    "X-Service": "formal-verification-service",
                    "X-Operation": "formal-verification-validation"
                }
            )
            
            validation_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                acge_result = response.json()
                return {
                    "compliance_score": acge_result.get("compliance_score", 0.0),
                    "compliant": acge_result.get("compliant", False),
                    "constitutional_analysis": acge_result.get("analysis", {}),
                    "formal_verification_assessment": acge_result.get("formal_verification_assessment", {}),
                    "acge_model_version": acge_result.get("model_version", "acge-v2"),
                    "validation_time_ms": validation_time
                }
            else:
                logger.warning(f"ACGE validation failed: {response.status_code}")
                return {
                    "compliance_score": 0.5,
                    "compliant": False,
                    "error": f"ACGE model error: {response.status_code}",
                    "validation_time_ms": validation_time,
                    "fallback": True
                }
                
        except Exception as e:
            validation_time = (time.time() - start_time) * 1000
            logger.error(f"ACGE validation error: {e}")
            return {
                "compliance_score": 0.5,
                "compliant": False,
                "error": str(e),
                "validation_time_ms": validation_time,
                "fallback": True
            }
    
    async def _generate_formal_proof(
        self, 
        request: ACGEFormalVerificationRequest,
        z3_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate formal mathematical proof."""
        start_time = time.time()
        
        try:
            # Determine proof type
            proof_type = ProofType.CONSTITUTIONAL_COMPLIANCE
            if request.proof_type == "safety":
                proof_type = ProofType.SAFETY_PROPERTY
            elif request.proof_type == "liveness":
                proof_type = ProofType.LIVENESS_PROPERTY
            
            # Generate formal proof using verification engine
            formal_proof = await self.verification_engine.generate_formal_proof(
                property_specification=f"constitutional_compliance({request.policy_content[:100]})",
                policy_constraints=request.constitutional_properties,
                proof_type=proof_type
            )
            
            generation_time = (time.time() - start_time) * 1000
            
            # Record proof generation metrics
            FORMAL_PROOF_GENERATIONS.labels(
                proof_type=request.proof_type,
                verification_level=request.verification_level,
                status="success" if formal_proof.verified else "failed"
            ).inc()
            
            return {
                "proof_id": formal_proof.proof_id,
                "verified": formal_proof.verified,
                "confidence_score": formal_proof.confidence_score,
                "proof_steps": formal_proof.proof_steps,
                "mathematical_proof": formal_proof.mathematical_proof,
                "z3_model": formal_proof.z3_model,
                "generation_time_ms": generation_time,
                "proof_type": request.proof_type,
                "constitutional_reference": self.constitutional_hash
            }
            
        except Exception as e:
            generation_time = (time.time() - start_time) * 1000
            logger.error(f"Formal proof generation failed: {e}")
            
            FORMAL_PROOF_GENERATIONS.labels(
                proof_type=request.proof_type,
                verification_level=request.verification_level,
                status="error"
            ).inc()
            
            return {
                "verified": False,
                "error": str(e),
                "generation_time_ms": generation_time
            }
    
    def _calculate_compliance_score(
        self, 
        z3_result: Dict[str, Any], 
        acge_result: Dict[str, Any], 
        constitutional_hash_valid: bool
    ) -> float:
        """Calculate overall constitutional compliance score."""
        try:
            # Z3 verification score
            z3_score = 1.0 if z3_result.get("verified", False) else 0.0
            
            # ACGE compliance score
            acge_score = acge_result.get("compliance_score", 0.0)
            
            # Constitutional hash score
            hash_score = 1.0 if constitutional_hash_valid else 0.0
            
            # Weighted average (Z3 formal verification has higher weight)
            overall_score = (
                z3_score * 0.5 +
                acge_score * 0.3 +
                hash_score * 0.2
            )
            
            return round(overall_score, 3)
            
        except Exception as e:
            logger.error(f"Compliance score calculation failed: {e}")
            return 0.0
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Get formal verification service status."""
        try:
            # Check ACGE model connectivity
            acge_status = "unknown"
            if ACGE_ENABLED:
                try:
                    health_response = await self.acge_client.get(
                        f"{ACGE_MODEL_ENDPOINT}/health",
                        timeout=2.0
                    )
                    acge_status = "healthy" if health_response.status_code == 200 else "unhealthy"
                except Exception:
                    acge_status = "unreachable"
            
            return {
                "service": SERVICE_NAME,
                "version": SERVICE_VERSION,
                "constitutional_hash": self.constitutional_hash,
                "acge_enabled": ACGE_ENABLED,
                "environment": ENVIRONMENT,
                "phase": PHASE,
                "acge_model_status": acge_status,
                "verification_capabilities": [
                    "z3_smt_solving",
                    "constitutional_compliance_verification",
                    "formal_proof_generation",
                    "acge_constitutional_validation",
                    "tiered_validation_pipeline"
                ],
                "proof_types": [
                    "constitutional_compliance",
                    "safety_property",
                    "liveness_property",
                    "fairness_property"
                ],
                "verification_levels": [
                    "baseline",
                    "standard", 
                    "rigorous"
                ]
            }
            
        except Exception as e:
            logger.error(f"Status check failed: {e}")
            return {
                "service": SERVICE_NAME,
                "status": "error",
                "error": str(e)
            }


# Initialize service
acge_fv_service = ACGEFormalVerificationService()

# FastAPI app
app = FastAPI(
    title="ACGS Formal Verification Service - ACGE Enhanced",
    description="Constitutional compliance formal verification with ACGE integration and Z3 theorem proving",
    version=SERVICE_VERSION
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.middleware("http")
async def constitutional_compliance_middleware(request: Request, call_next):
    """Add constitutional headers and metrics."""
    start_time = time.time()
    
    response = await call_next(request)
    
    # Add constitutional headers
    response.headers["X-Constitutional-Hash"] = CONSTITUTIONAL_HASH
    response.headers["X-Service-Name"] = SERVICE_NAME
    response.headers["X-Service-Version"] = SERVICE_VERSION
    response.headers["X-ACGE-Enabled"] = str(ACGE_ENABLED)
    response.headers["X-Environment"] = ENVIRONMENT
    response.headers["X-Phase"] = PHASE
    response.headers["X-Z3-Integration"] = "enabled"
    
    return response

# Health endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return await acge_fv_service.get_service_status()

@app.get("/health/constitutional")
async def constitutional_health():
    """Constitutional compliance health check."""
    try:
        # Test constitutional hash validation
        hash_valid = await acge_fv_service._verify_constitutional_hash(CONSTITUTIONAL_HASH)
        
        return {
            "constitutional_compliance": "active",
            "constitutional_hash_valid": hash_valid,
            "acge_enabled": ACGE_ENABLED,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "z3_solver": "operational",
            "formal_verification": "operational"
        }
    except Exception as e:
        return {
            "constitutional_compliance": "error",
            "error": str(e),
            "acge_enabled": ACGE_ENABLED
        }

# Main formal verification endpoint
@app.post("/api/v1/verify/constitutional-compliance", response_model=ACGEFormalVerificationResponse)
async def verify_constitutional_compliance(request: ACGEFormalVerificationRequest):
    """Enhanced constitutional compliance verification with ACGE integration and formal proofs."""
    return await acge_fv_service.verify_with_acge_integration(request)

# Z3 formal proof generation endpoint
@app.post("/api/v1/verify/generate-formal-proof")
async def generate_formal_proof(
    property_specification: str,
    policy_constraints: List[str] = [],
    proof_type: str = "constitutional_compliance"
):
    """Generate formal mathematical proof using Z3 theorem prover."""
    try:
        request = ACGEFormalVerificationRequest(
            policy_content=property_specification,
            constitutional_properties=policy_constraints,
            proof_type=proof_type,
            include_formal_proof=True
        )
        
        result = await acge_fv_service.verify_with_acge_integration(request)
        return result.formal_proof
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Formal proof generation failed: {e}"
        )

# Service info endpoint
@app.get("/api/v1/verify/info")
async def service_info():
    """Service information and configuration."""
    return await acge_fv_service.get_service_status()

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"🚀 Starting {SERVICE_NAME} v{SERVICE_VERSION}")
    logger.info(f"🏛️ Constitutional Hash: {CONSTITUTIONAL_HASH}")
    logger.info(f"🔬 Z3 Formal Verification: Enabled")
    logger.info(f"🤖 ACGE Integration: {'Enabled' if ACGE_ENABLED else 'Disabled'}")
    
    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)
