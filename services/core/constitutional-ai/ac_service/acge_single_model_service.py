"""
ACGE Phase 2 Single Model Constitutional AI Service
Transition from multi-model consensus to single highly-aligned ACGE model architecture
"""

import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx
from fastapi import FastAPI, HTTPException, Request, Response, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, Gauge
from pydantic import BaseModel

# Import existing AC service components
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.constitutional_validation_service import ConstitutionalValidationService
from app.api.v1.constitutional_validation import ConstitutionalValidationRequest

# ACGE integration
from services.platform.authentication.auth_service.acge_integration import (
    ACGEAuthIntegration,
    constitutional_auth_dependency
)

# Service configuration
SERVICE_NAME = "acgs-ac-service-acge"
SERVICE_VERSION = "2.0.0-single-model"
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8001"))

# ACGE configuration
ACGE_MODEL_ENDPOINT = os.getenv("ACGE_MODEL_ENDPOINT", "http://acge-model-service.acgs-shared.svc.cluster.local:8080")
CONSTITUTIONAL_HASH = os.getenv("CONSTITUTIONAL_HASH", "cdd01ef066bc6cf2")
ACGE_ENABLED = os.getenv("ACGE_ENABLED", "true").lower() == "true"
SINGLE_MODEL_MODE = os.getenv("SINGLE_MODEL_MODE", "true").lower() == "true"
MULTI_MODEL_DISABLED = os.getenv("MULTI_MODEL_DISABLED", "true").lower() == "true"
ENVIRONMENT = os.getenv("ENVIRONMENT", "green")
PHASE = os.getenv("PHASE", "phase-2")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(SERVICE_NAME)

# Enhanced metrics for ACGE single model
CONSTITUTIONAL_COMPLIANCE_SCORE = Histogram(
    'ac_constitutional_compliance_score',
    'Constitutional compliance score from ACGE model',
    ['operation', 'policy_type']
)

ACGE_MODEL_LATENCY = Histogram(
    'ac_acge_model_latency_seconds',
    'ACGE model inference latency',
    ['operation']
)

ACGE_MODEL_REQUESTS = Counter(
    'ac_acge_model_requests_total',
    'Total requests to ACGE model',
    ['operation', 'status']
)

MULTI_MODEL_FALLBACK = Counter(
    'ac_multi_model_fallback_total',
    'Fallback to multi-model consensus',
    ['reason']
)

SINGLE_MODEL_SUCCESS_RATE = Gauge(
    'ac_single_model_success_rate',
    'Success rate of single ACGE model'
)

# Request/Response models
class ACGEValidationRequest(BaseModel):
    """Enhanced validation request for ACGE single model."""
    policy: Dict[str, Any]
    validation_mode: str = "comprehensive"
    include_reasoning: bool = True
    principles: Optional[List[Dict]] = None
    acge_enabled: bool = True
    single_model_mode: bool = True
    constitutional_hash: str = CONSTITUTIONAL_HASH

class ACGEValidationResponse(BaseModel):
    """Enhanced validation response from ACGE single model."""
    valid: bool
    compliance_score: float
    confidence_score: float
    constitutional_alignment: float
    violations: List[Dict] = []
    recommendations: List[str] = []
    acge_analysis: Dict[str, Any] = {}
    model_type: str = "acge_single"
    processing_time_ms: float
    constitutional_hash: str
    fallback_used: bool = False


class ACGESingleModelService:
    """ACGE Single Model Constitutional AI Service."""
    
    def __init__(self):
        self.acge_client = httpx.AsyncClient(timeout=5.0)
        self.acge_model_endpoint = ACGE_MODEL_ENDPOINT
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.fallback_service = None
        
        # Initialize fallback service if needed
        if not MULTI_MODEL_DISABLED:
            try:
                self.fallback_service = ConstitutionalValidationService()
                logger.info("Multi-model fallback service initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize fallback service: {e}")
    
    async def validate_constitutional_compliance(
        self, 
        request: ACGEValidationRequest
    ) -> ACGEValidationResponse:
        """
        Validate constitutional compliance using single ACGE model.
        
        Args:
            request: Validation request with policy and parameters
            
        Returns:
            Validation response with ACGE analysis
        """
        start_time = time.time()
        
        try:
            # Primary validation using ACGE single model
            if ACGE_ENABLED and SINGLE_MODEL_MODE:
                result = await self._validate_with_acge_model(request)
                
                # Record success metrics
                SINGLE_MODEL_SUCCESS_RATE.set(1.0)
                ACGE_MODEL_REQUESTS.labels(
                    operation="constitutional_validation",
                    status="success"
                ).inc()
                
                return result
            else:
                # Fallback to multi-model if ACGE disabled
                return await self._fallback_to_multi_model(request, "acge_disabled")
                
        except Exception as e:
            logger.error(f"ACGE model validation failed: {e}")
            
            # Record failure metrics
            ACGE_MODEL_REQUESTS.labels(
                operation="constitutional_validation",
                status="error"
            ).inc()
            
            # Attempt fallback if available
            if self.fallback_service and not MULTI_MODEL_DISABLED:
                return await self._fallback_to_multi_model(request, "acge_error")
            else:
                # Return error response
                processing_time = (time.time() - start_time) * 1000
                return ACGEValidationResponse(
                    valid=False,
                    compliance_score=0.0,
                    confidence_score=0.0,
                    constitutional_alignment=0.0,
                    violations=[{"type": "validation_error", "message": str(e)}],
                    recommendations=["Review policy and retry validation"],
                    acge_analysis={"error": str(e)},
                    processing_time_ms=processing_time,
                    constitutional_hash=self.constitutional_hash,
                    fallback_used=False
                )
    
    async def _validate_with_acge_model(
        self, 
        request: ACGEValidationRequest
    ) -> ACGEValidationResponse:
        """Validate using ACGE single model."""
        start_time = time.time()
        
        # Prepare ACGE model request
        acge_request = {
            "operation": "constitutional_validation",
            "policy": request.policy,
            "validation_mode": request.validation_mode,
            "include_reasoning": request.include_reasoning,
            "principles": request.principles or [],
            "constitutional_hash": self.constitutional_hash,
            "single_model_mode": True,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Call ACGE model
        response = await self.acge_client.post(
            f"{self.acge_model_endpoint}/validate/constitutional",
            json=acge_request,
            headers={
                "X-Constitutional-Hash": self.constitutional_hash,
                "X-Service": "ac-service",
                "X-Single-Model": "true"
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"ACGE model validation failed: {response.text}"
            )
        
        acge_result = response.json()
        processing_time = (time.time() - start_time) * 1000
        
        # Record latency metrics
        ACGE_MODEL_LATENCY.labels(operation="constitutional_validation").observe(
            processing_time / 1000
        )
        
        # Record compliance metrics
        compliance_score = acge_result.get("compliance_score", 0.0)
        CONSTITUTIONAL_COMPLIANCE_SCORE.labels(
            operation="validation",
            policy_type=request.policy.get("category", "unknown")
        ).observe(compliance_score)
        
        # Transform ACGE result to response format
        return ACGEValidationResponse(
            valid=acge_result.get("compliant", False),
            compliance_score=compliance_score,
            confidence_score=acge_result.get("confidence_score", 0.0),
            constitutional_alignment=acge_result.get("constitutional_alignment", compliance_score),
            violations=acge_result.get("violations", []),
            recommendations=acge_result.get("recommendations", []),
            acge_analysis={
                "model_version": acge_result.get("model_version", "acge-v2"),
                "reasoning": acge_result.get("reasoning", ""),
                "constitutional_principles": acge_result.get("constitutional_principles", []),
                "risk_assessment": acge_result.get("risk_assessment", {}),
                "single_model_confidence": acge_result.get("confidence_score", 0.0)
            },
            processing_time_ms=processing_time,
            constitutional_hash=self.constitutional_hash,
            fallback_used=False
        )
    
    async def _fallback_to_multi_model(
        self, 
        request: ACGEValidationRequest, 
        reason: str
    ) -> ACGEValidationResponse:
        """Fallback to multi-model consensus validation."""
        start_time = time.time()
        
        logger.warning(f"Falling back to multi-model consensus: {reason}")
        
        # Record fallback metrics
        MULTI_MODEL_FALLBACK.labels(reason=reason).inc()
        SINGLE_MODEL_SUCCESS_RATE.set(0.0)
        
        if not self.fallback_service:
            raise HTTPException(
                status_code=503,
                detail="ACGE model unavailable and no fallback service configured"
            )
        
        try:
            # Convert to legacy request format
            legacy_request = ConstitutionalValidationRequest(
                policy=request.policy,
                validation_mode=request.validation_mode,
                include_reasoning=request.include_reasoning,
                principles=request.principles or []
            )
            
            # Use legacy validation service
            legacy_result = await self.fallback_service.validate_constitutional_compliance(
                legacy_request
            )
            
            processing_time = (time.time() - start_time) * 1000
            
            # Transform legacy result to ACGE response format
            return ACGEValidationResponse(
                valid=legacy_result.get("valid", False),
                compliance_score=legacy_result.get("compliance_score", 0.0),
                confidence_score=legacy_result.get("confidence_score", 0.0),
                constitutional_alignment=legacy_result.get("constitutional_alignment", 0.0),
                violations=legacy_result.get("violations", []),
                recommendations=legacy_result.get("recommendations", []),
                acge_analysis={
                    "fallback_reason": reason,
                    "legacy_validation": True,
                    "multi_model_consensus": True
                },
                model_type="multi_model_fallback",
                processing_time_ms=processing_time,
                constitutional_hash=self.constitutional_hash,
                fallback_used=True
            )
            
        except Exception as e:
            logger.error(f"Fallback validation failed: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Both ACGE and fallback validation failed: {e}"
            )
    
    async def get_model_status(self) -> Dict[str, Any]:
        """Get current model status and configuration."""
        try:
            # Check ACGE model health
            acge_health = await self.acge_client.get(
                f"{self.acge_model_endpoint}/health",
                timeout=2.0
            )
            acge_status = "healthy" if acge_health.status_code == 200 else "unhealthy"
        except Exception as e:
            acge_status = "unreachable"
            logger.error(f"ACGE model health check failed: {e}")
        
        return {
            "service": SERVICE_NAME,
            "version": SERVICE_VERSION,
            "constitutional_hash": self.constitutional_hash,
            "acge_enabled": ACGE_ENABLED,
            "single_model_mode": SINGLE_MODEL_MODE,
            "multi_model_disabled": MULTI_MODEL_DISABLED,
            "environment": ENVIRONMENT,
            "phase": PHASE,
            "acge_model_status": acge_status,
            "acge_model_endpoint": self.acge_model_endpoint,
            "fallback_available": self.fallback_service is not None,
            "model_configuration": {
                "primary": "acge_single_model",
                "fallback": "multi_model_consensus" if self.fallback_service else None,
                "mode": "single_model" if SINGLE_MODEL_MODE else "hybrid"
            }
        }


# Initialize service
acge_service = ACGESingleModelService()

# FastAPI app
app = FastAPI(
    title="ACGS Constitutional AI Service - ACGE Single Model",
    description="Constitutional compliance validation using single ACGE model architecture",
    version=SERVICE_VERSION
)

# Add secure CORS middleware with environment-based configuration
cors_origins = os.getenv("BACKEND_CORS_ORIGINS", "http://localhost:3000,http://localhost:8080").split(",")
cors_origins = [origin.strip() for origin in cors_origins if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,  # Restricted to configured origins only
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Accept",
        "Accept-Language", 
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Request-ID",
        "X-Constitutional-Hash"
    ],
    expose_headers=["X-Request-ID", "X-Response-Time", "X-Compliance-Score"],
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
    response.headers["X-ACGE-Single-Model"] = str(SINGLE_MODEL_MODE)
    response.headers["X-Multi-Model-Disabled"] = str(MULTI_MODEL_DISABLED)
    response.headers["X-Environment"] = ENVIRONMENT
    response.headers["X-Phase"] = PHASE
    
    return response

# Health endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return await acge_service.get_model_status()

@app.get("/health/constitutional")
async def constitutional_health():
    """Constitutional compliance health check."""
    try:
        # Test ACGE model with simple validation
        test_request = ACGEValidationRequest(
            policy={"id": "test", "content": "test policy", "category": "test"},
            validation_mode="basic"
        )
        
        result = await acge_service.validate_constitutional_compliance(test_request)
        
        return {
            "constitutional_compliance": "active",
            "acge_model_status": "operational",
            "single_model_mode": SINGLE_MODEL_MODE,
            "compliance_score": result.compliance_score,
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
    except Exception as e:
        return {
            "constitutional_compliance": "error",
            "error": str(e),
            "fallback_available": acge_service.fallback_service is not None
        }

# Main validation endpoint
@app.post("/api/v1/constitutional/validate", response_model=ACGEValidationResponse)
async def validate_constitutional_compliance(request: ACGEValidationRequest):
    """Enhanced constitutional validation with ACGE single model."""
    return await acge_service.validate_constitutional_compliance(request)

# ACGE-specific validation endpoint
@app.post("/api/v1/constitutional/acge-validate", response_model=ACGEValidationResponse)
async def acge_validate_constitutional_compliance(request: ACGEValidationRequest):
    """Direct ACGE model validation (no fallback)."""
    if not ACGE_ENABLED:
        raise HTTPException(
            status_code=503,
            detail="ACGE model validation disabled"
        )
    
    return await acge_service._validate_with_acge_model(request)

# Service info endpoint
@app.get("/api/v1/constitutional/info")
async def service_info():
    """Service information and configuration."""
    return await acge_service.get_model_status()

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"🚀 Starting {SERVICE_NAME} v{SERVICE_VERSION}")
    logger.info(f"🏛️ Constitutional Hash: {CONSTITUTIONAL_HASH}")
    logger.info(f"🤖 ACGE Single Model: {'Enabled' if SINGLE_MODEL_MODE else 'Disabled'}")
    logger.info(f"🔄 Multi-Model Disabled: {MULTI_MODEL_DISABLED}")
    
    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)
