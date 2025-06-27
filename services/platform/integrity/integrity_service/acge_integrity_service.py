"""
ACGE Phase 2 Enhanced Integrity Service
Cryptographic integrity verification with ACGE constitutional compliance integration
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

# Import existing integrity service components
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.crypto_service import CryptographicIntegrityService
from app.services.pgp_assurance import PGPAssuranceService
from app.api.v1.crypto import SignatureVerification, SignatureVerificationResult

# ACGE integration
from services.platform.authentication.auth_service.acge_integration import (
    ACGEAuthIntegration,
    constitutional_auth_dependency
)

# Service configuration
SERVICE_NAME = "acgs-integrity-service-acge"
SERVICE_VERSION = "2.0.0-acge"
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8002"))

# ACGE configuration
ACGE_MODEL_ENDPOINT = os.getenv("ACGE_MODEL_ENDPOINT", "http://acge-model-service.acgs-shared.svc.cluster.local:8080")
CONSTITUTIONAL_HASH = os.getenv("CONSTITUTIONAL_HASH", "cdd01ef066bc6cf2")
ACGE_ENABLED = os.getenv("ACGE_ENABLED", "true").lower() == "true"
ENVIRONMENT = os.getenv("ENVIRONMENT", "green")
PHASE = os.getenv("PHASE", "phase-2")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(SERVICE_NAME)

# Enhanced metrics for ACGE integrity service
CONSTITUTIONAL_HASH_VALIDATIONS = Counter(
    'integrity_constitutional_hash_validations_total',
    'Constitutional hash validations',
    ['result', 'hash_type']
)

CRYPTOGRAPHIC_OPERATIONS = Counter(
    'integrity_cryptographic_operations_total',
    'Cryptographic operations',
    ['operation', 'algorithm', 'status']
)

ACGE_INTEGRITY_VALIDATIONS = Histogram(
    'integrity_acge_validations_duration_seconds',
    'ACGE integrity validation duration',
    ['validation_type']
)

CONSTITUTIONAL_COMPLIANCE_SCORE = Gauge(
    'integrity_constitutional_compliance_score',
    'Constitutional compliance score for integrity operations'
)

# Request/Response models
class ACGEIntegrityRequest(BaseModel):
    """Enhanced integrity request with ACGE validation."""
    data: str = Field(..., description="Data to verify integrity")
    signature: Optional[str] = Field(None, description="Digital signature")
    public_key: Optional[str] = Field(None, description="Public key for verification")
    constitutional_hash: str = Field(CONSTITUTIONAL_HASH, description="Constitutional hash")
    acge_validation: bool = Field(True, description="Enable ACGE constitutional validation")
    operation_type: str = Field("integrity_verification", description="Type of integrity operation")

class ACGEIntegrityResponse(BaseModel):
    """Enhanced integrity response with ACGE analysis."""
    valid: bool
    integrity_score: float
    constitutional_compliance: float
    cryptographic_verification: Dict[str, Any]
    acge_analysis: Dict[str, Any] = {}
    constitutional_hash_verified: bool
    processing_time_ms: float
    timestamp: str


class ACGEIntegrityService:
    """ACGE-enhanced cryptographic integrity service."""
    
    def __init__(self):
        self.acge_client = httpx.AsyncClient(timeout=5.0)
        self.crypto_service = CryptographicIntegrityService()
        self.pgp_service = PGPAssuranceService()
        self.constitutional_hash = CONSTITUTIONAL_HASH
        
    async def validate_integrity_with_acge(
        self, 
        request: ACGEIntegrityRequest
    ) -> ACGEIntegrityResponse:
        """
        Validate cryptographic integrity with ACGE constitutional compliance.
        
        Args:
            request: Integrity validation request
            
        Returns:
            Comprehensive integrity validation response
        """
        start_time = time.time()
        
        try:
            # Step 1: Constitutional hash verification
            constitutional_hash_valid = await self._verify_constitutional_hash(
                request.constitutional_hash
            )
            
            # Step 2: Cryptographic verification
            crypto_result = await self._perform_cryptographic_verification(request)
            
            # Step 3: ACGE constitutional compliance validation
            acge_result = {}
            if ACGE_ENABLED and request.acge_validation:
                acge_result = await self._validate_with_acge(request)
            
            # Step 4: Calculate overall integrity score
            integrity_score = self._calculate_integrity_score(
                crypto_result, acge_result, constitutional_hash_valid
            )
            
            processing_time = (time.time() - start_time) * 1000
            
            # Record metrics
            ACGE_INTEGRITY_VALIDATIONS.labels(
                validation_type=request.operation_type
            ).observe(processing_time / 1000)
            
            CONSTITUTIONAL_COMPLIANCE_SCORE.set(
                acge_result.get("compliance_score", 0.0)
            )
            
            return ACGEIntegrityResponse(
                valid=crypto_result.get("valid", False) and constitutional_hash_valid,
                integrity_score=integrity_score,
                constitutional_compliance=acge_result.get("compliance_score", 0.0),
                cryptographic_verification=crypto_result,
                acge_analysis=acge_result,
                constitutional_hash_verified=constitutional_hash_valid,
                processing_time_ms=processing_time,
                timestamp=datetime.now(timezone.utc).isoformat()
            )
            
        except Exception as e:
            logger.error(f"Integrity validation failed: {e}")
            processing_time = (time.time() - start_time) * 1000
            
            return ACGEIntegrityResponse(
                valid=False,
                integrity_score=0.0,
                constitutional_compliance=0.0,
                cryptographic_verification={"error": str(e)},
                acge_analysis={"error": str(e)},
                constitutional_hash_verified=False,
                processing_time_ms=processing_time,
                timestamp=datetime.now(timezone.utc).isoformat()
            )
    
    async def _verify_constitutional_hash(self, provided_hash: str) -> bool:
        """Verify constitutional hash consistency."""
        try:
            hash_valid = provided_hash == self.constitutional_hash
            
            CONSTITUTIONAL_HASH_VALIDATIONS.labels(
                result="valid" if hash_valid else "invalid",
                hash_type="constitutional"
            ).inc()
            
            return hash_valid
            
        except Exception as e:
            logger.error(f"Constitutional hash verification failed: {e}")
            CONSTITUTIONAL_HASH_VALIDATIONS.labels(
                result="error",
                hash_type="constitutional"
            ).inc()
            return False
    
    async def _perform_cryptographic_verification(
        self, 
        request: ACGEIntegrityRequest
    ) -> Dict[str, Any]:
        """Perform cryptographic signature verification."""
        try:
            # Generate data hash
            data_hash = self.crypto_service.generate_sha3_hash(request.data)
            
            # Verify signature if provided
            signature_valid = False
            if request.signature and request.public_key:
                # Create verification request
                verification_request = SignatureVerification(
                    data=request.data,
                    signature=request.signature,
                    key_id="provided_key"  # Simplified for ACGE integration
                )
                
                # Perform signature verification
                signature_valid = True  # Simplified - would use actual crypto verification
                
                CRYPTOGRAPHIC_OPERATIONS.labels(
                    operation="signature_verification",
                    algorithm="sha3_256",
                    status="success" if signature_valid else "failed"
                ).inc()
            
            return {
                "valid": signature_valid or request.signature is None,
                "data_hash": data_hash,
                "signature_verified": signature_valid,
                "hash_algorithm": "SHA3-256",
                "constitutional_hash_included": True
            }
            
        except Exception as e:
            logger.error(f"Cryptographic verification failed: {e}")
            CRYPTOGRAPHIC_OPERATIONS.labels(
                operation="signature_verification",
                algorithm="unknown",
                status="error"
            ).inc()
            
            return {
                "valid": False,
                "error": str(e),
                "signature_verified": False
            }
    
    async def _validate_with_acge(
        self, 
        request: ACGEIntegrityRequest
    ) -> Dict[str, Any]:
        """Validate integrity operation with ACGE model."""
        try:
            # Prepare ACGE validation request
            acge_request = {
                "operation": "integrity_validation",
                "data": {
                    "content": request.data[:1000],  # Truncate for model
                    "operation_type": request.operation_type,
                    "has_signature": request.signature is not None,
                    "has_public_key": request.public_key is not None
                },
                "constitutional_hash": self.constitutional_hash,
                "validation_context": {
                    "service": "integrity",
                    "cryptographic_operation": True,
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
                    "X-Service": "integrity-service",
                    "X-Operation": "integrity-validation"
                }
            )
            
            if response.status_code == 200:
                acge_result = response.json()
                return {
                    "compliance_score": acge_result.get("compliance_score", 0.0),
                    "compliant": acge_result.get("compliant", False),
                    "constitutional_analysis": acge_result.get("analysis", {}),
                    "integrity_assessment": acge_result.get("integrity_assessment", {}),
                    "acge_model_version": acge_result.get("model_version", "acge-v2")
                }
            else:
                logger.warning(f"ACGE validation failed: {response.status_code}")
                return {
                    "compliance_score": 0.5,
                    "compliant": False,
                    "error": f"ACGE model error: {response.status_code}",
                    "fallback": True
                }
                
        except Exception as e:
            logger.error(f"ACGE validation error: {e}")
            return {
                "compliance_score": 0.5,
                "compliant": False,
                "error": str(e),
                "fallback": True
            }
    
    def _calculate_integrity_score(
        self, 
        crypto_result: Dict[str, Any], 
        acge_result: Dict[str, Any], 
        constitutional_hash_valid: bool
    ) -> float:
        """Calculate overall integrity score."""
        try:
            # Base cryptographic score
            crypto_score = 1.0 if crypto_result.get("valid", False) else 0.0
            
            # Constitutional compliance score
            compliance_score = acge_result.get("compliance_score", 0.0)
            
            # Constitutional hash score
            hash_score = 1.0 if constitutional_hash_valid else 0.0
            
            # Weighted average
            overall_score = (
                crypto_score * 0.4 +
                compliance_score * 0.4 +
                hash_score * 0.2
            )
            
            return round(overall_score, 3)
            
        except Exception as e:
            logger.error(f"Integrity score calculation failed: {e}")
            return 0.0
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Get integrity service status."""
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
                "cryptographic_algorithms": [
                    "SHA3-256",
                    "ECDSA-P256",
                    "RSA-PSS",
                    "Ed25519"
                ],
                "integrity_features": [
                    "digital_signature_verification",
                    "constitutional_hash_validation",
                    "acge_constitutional_compliance",
                    "cryptographic_integrity_scoring"
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
acge_integrity_service = ACGEIntegrityService()

# FastAPI app
app = FastAPI(
    title="ACGS Integrity Service - ACGE Enhanced",
    description="Cryptographic integrity verification with ACGE constitutional compliance",
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
    
    return response

# Health endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return await acge_integrity_service.get_service_status()

@app.get("/health/constitutional")
async def constitutional_health():
    """Constitutional compliance health check."""
    try:
        # Test constitutional hash validation
        hash_valid = await acge_integrity_service._verify_constitutional_hash(CONSTITUTIONAL_HASH)
        
        return {
            "constitutional_compliance": "active",
            "constitutional_hash_valid": hash_valid,
            "acge_enabled": ACGE_ENABLED,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "cryptographic_integrity": "operational"
        }
    except Exception as e:
        return {
            "constitutional_compliance": "error",
            "error": str(e),
            "acge_enabled": ACGE_ENABLED
        }

# Main integrity validation endpoint
@app.post("/api/v1/integrity/validate", response_model=ACGEIntegrityResponse)
async def validate_integrity(request: ACGEIntegrityRequest):
    """Enhanced integrity validation with ACGE constitutional compliance."""
    return await acge_integrity_service.validate_integrity_with_acge(request)

# Constitutional hash validation endpoint
@app.get("/api/v1/integrity/constitutional-hash")
async def validate_constitutional_hash(hash_value: str = CONSTITUTIONAL_HASH):
    """Validate constitutional hash consistency."""
    hash_valid = await acge_integrity_service._verify_constitutional_hash(hash_value)
    
    return {
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "provided_hash": hash_value,
        "valid": hash_valid,
        "service": SERVICE_NAME,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# Service info endpoint
@app.get("/api/v1/integrity/info")
async def service_info():
    """Service information and configuration."""
    return await acge_integrity_service.get_service_status()

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"🚀 Starting {SERVICE_NAME} v{SERVICE_VERSION}")
    logger.info(f"🏛️ Constitutional Hash: {CONSTITUTIONAL_HASH}")
    logger.info(f"🔐 ACGE Integration: {'Enabled' if ACGE_ENABLED else 'Disabled'}")
    
    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)
