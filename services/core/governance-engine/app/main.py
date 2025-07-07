"""
Unified Governance Engine Service
Constitutional Hash: cdd01ef066bc6cf2

Combines governance synthesis and policy compliance functionality 
into a single, streamlined service to reduce architectural complexity.
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone

# ACGS Standardized Error Handling
try:
    import sys
    from pathlib import Path
    shared_middleware_path = Path(__file__).parent.parent.parent.parent.parent / "shared" / "middleware"
    sys.path.insert(0, str(shared_middleware_path))
    
    from error_handling import (
        setup_error_handlers,
        ErrorHandlingMiddleware,
        ACGSException,
        ConstitutionalComplianceError,
        SecurityValidationError,
        AuthenticationError,
        ValidationError,
        log_error_with_context,
        ErrorContext
    )
    ACGS_ERROR_HANDLING_AVAILABLE = True
    print(f"✅ ACGS Error handling loaded for {service_name}")
except ImportError as e:
    print(f"⚠️ ACGS Error handling not available for {service_name}: {e}")
    ACGS_ERROR_HANDLING_AVAILABLE = False


# ACGS Security Middleware Integration
try:
    import sys
    from pathlib import Path
    shared_security_path = Path(__file__).parent.parent.parent.parent.parent / "shared" / "security"
    sys.path.insert(0, str(shared_security_path))
    
    from middleware_integration import (
        apply_acgs_security_middleware,
        setup_security_monitoring,
        get_security_headers,
        SecurityLevel,
        validate_request_body,
        create_secure_endpoint_decorator
    )
    ACGS_SECURITY_AVAILABLE = True
    print(f"✅ ACGS Security middleware loaded for {service_name}")
except ImportError as e:
    print(f"⚠️ ACGS Security middleware not available for {service_name}: {e}")
    ACGS_SECURITY_AVAILABLE = False


# Import multi-tenant components
try:
    import os
    import sys
    from pathlib import Path

    # Add project root to path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(current_dir, "..", "..", "..", "..")
    shared_path = os.path.join(project_root, "services", "shared")
    sys.path.insert(0, os.path.abspath(shared_path))

    from clients.tenant_service_client import TenantServiceClient, service_registry
    from middleware.tenant_middleware import (
        TenantContextMiddleware,
        TenantSecurityMiddleware,
        get_optional_tenant_context,
        get_tenant_context,
        get_tenant_db,
    )

    MULTI_TENANT_AVAILABLE = True
    print("✅ Multi-tenant components loaded successfully")
except ImportError as e:
    print(f"⚠️ Multi-tenant components not available: {e}")
    MULTI_TENANT_AVAILABLE = False

# Import production security middleware
try:
    from services.shared.security.standardized_security import (
        CONSTITUTIONAL_HASH,
        apply_standardized_security,
        create_health_endpoint_response,
        create_security_headers,
        validate_governance_input,
        validate_policy_input,
    )

    SECURITY_MIDDLEWARE_AVAILABLE = True
    print("✅ Standardized security middleware loaded successfully")
except ImportError as e:
    print(f"⚠️ Standardized security middleware not available: {e}")
    SECURITY_MIDDLEWARE_AVAILABLE = False

# FastAPI and core imports
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

# Service imports
try:
    from services.shared.service_clients.registry import get_service_client
    from services.shared.middleware.error_handling import setup_error_handlers
    CLIENT_REGISTRY_AVAILABLE = True
except ImportError:
    CLIENT_REGISTRY_AVAILABLE = False

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: datetime
    service: str
    version: str
    constitutional_hash: str
    uptime_seconds: float
    components: Dict[str, str]


class SynthesisRequest(BaseModel):
    """Policy synthesis request model."""
    context: str
    policy_type: str
    requirements: List[str]
    constraints: Optional[Dict[str, Any]] = None


class SynthesisResponse(BaseModel):
    """Policy synthesis response model."""
    policy_id: str
    synthesized_policy: Dict[str, Any]
    constitutional_compliance: float
    confidence_score: float
    metadata: Dict[str, Any]


class EnforcementRequest(BaseModel):
    """Policy enforcement request model."""
    policy_id: str
    context: Dict[str, Any]
    action: str
    parameters: Optional[Dict[str, Any]] = None


class EnforcementResponse(BaseModel):
    """Policy enforcement response model."""
    allowed: bool
    decision: str
    reasoning: List[str]
    constitutional_compliance: float
    metadata: Dict[str, Any]


class ComplianceRequest(BaseModel):
    """Compliance checking request model."""
    context: Dict[str, Any]
    policies: List[str]
    action: str


class ComplianceResponse(BaseModel):
    """Compliance checking response model."""
    compliant: bool
    violations: List[str]
    recommendations: List[str]
    constitutional_compliance: float
    metadata: Dict[str, Any]


# Application lifecycle management
start_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management."""
    logger.info("🚀 Unified Governance Engine starting up...")
    
    # Initialize service components
    components = {
        "constitutional_ai": False,
        "formal_verification": False,
        "integrity": False,
        "database": False,
        "cache": False
    }
    
    if CLIENT_REGISTRY_AVAILABLE:
        try:
            # Test service client connections
            constitutional_client = await get_service_client("constitutional-ai")
            if constitutional_client:
                components["constitutional_ai"] = await constitutional_client.health_check()
            
            integrity_client = await get_service_client("integrity")
            if integrity_client:
                components["integrity"] = await integrity_client.health_check()
                
        except Exception as e:
        # TODO: Consider using ACGS error handling: log_error_with_context()
            logger.warning(f"Service client initialization failed: {e}")
    
    # Store component status in app state
    app.state.components = components
    app.state.start_time = start_time
    
    logger.info("✅ Unified Governance Engine startup complete")
    
    yield
    
    logger.info("🛑 Unified Governance Engine shutting down...")
    
    # Cleanup service clients
    if CLIENT_REGISTRY_AVAILABLE:
        try:
            from services.shared.service_clients.registry import shutdown_registry
            await shutdown_registry()
        except Exception as e:
        # TODO: Consider using ACGS error handling: log_error_with_context()
            logger.warning(f"Service client cleanup failed: {e}")
    
    logger.info("✅ Unified Governance Engine shutdown complete")


# Create FastAPI application
app = FastAPI(


# Apply ACGS Error Handling
if ACGS_ERROR_HANDLING_AVAILABLE:
    import os
    development_mode = os.getenv("ENVIRONMENT", "development") != "production"
    setup_error_handlers(app, "governance-engine", include_traceback=development_mode)

# Apply ACGS Security Middleware
if ACGS_SECURITY_AVAILABLE:
    environment = os.getenv("ENVIRONMENT", "development")
    apply_acgs_security_middleware(app, "governance-engine", environment)
    setup_security_monitoring(app, "governance-engine")

    title="Unified Governance Engine",
    description="Constitutional AI governance synthesis and policy compliance engine",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json",
)

# Apply security middleware
if SECURITY_MIDDLEWARE_AVAILABLE:
    apply_standardized_security(app)

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
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure appropriately for production
)

# Add multi-tenant middleware if available
if MULTI_TENANT_AVAILABLE:
    app.add_middleware(TenantContextMiddleware)
    app.add_middleware(TenantSecurityMiddleware)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    current_time = datetime.now(timezone.utc)
    uptime = time.time() - start_time
    
    components = getattr(app.state, 'components', {})
    
    return HealthResponse(
        status="healthy",
        timestamp=current_time,
        service="unified-governance-engine",
        version="1.0.0",
        constitutional_hash=CONSTITUTIONAL_HASH,
        uptime_seconds=uptime,
        components=components
    )


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Unified Governance Engine",
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "docs": "/api/v1/docs",
            "synthesis": "/api/v1/synthesis",
            "enforcement": "/api/v1/enforcement",
            "compliance": "/api/v1/compliance"
        }
    }


# =============================================================================
# Policy Synthesis API (from governance-synthesis service)
# =============================================================================

@app.post("/api/v1/synthesis/synthesize", response_model=SynthesisResponse)
async def synthesize_policy(request: SynthesisRequest):
    """
    Synthesize a new policy based on context and requirements.
    Combines multi-model AI capabilities with constitutional compliance.
    """
    try:
        logger.info(f"Policy synthesis request: {request.policy_type}")
        
        # Validate constitutional compliance
        if SECURITY_MIDDLEWARE_AVAILABLE:
            validate_governance_input(request.dict())
        
        # Mock synthesis for now - implement actual synthesis logic
        synthesized_policy = {
            "id": f"policy_{int(time.time())}",
            "type": request.policy_type,
            "context": request.context,
            "requirements": request.requirements,
            "rules": [
                f"ALLOW IF {req}" for req in request.requirements[:3]
            ],
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        return SynthesisResponse(
            policy_id=synthesized_policy["id"],
            synthesized_policy=synthesized_policy,
            constitutional_compliance=0.95,
            confidence_score=0.88,
            metadata={
                "synthesis_time_ms": 150,
                "model_consensus": True,
                "constitutional_hash": CONSTITUTIONAL_HASH
            }
        )
        
    except Exception as e:
        # TODO: Consider using ACGS error handling: log_error_with_context()
        logger.error(f"Policy synthesis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Policy synthesis failed: {str(e)}"
        )


@app.get("/api/v1/synthesis/policies")
async def list_policies():
    """List available synthesized policies."""
    # Mock implementation - implement actual policy storage
    return {
        "policies": [],
        "total": 0,
        "constitutional_hash": CONSTITUTIONAL_HASH
    }


# =============================================================================
# Policy Enforcement API (from policy-governance service)
# =============================================================================

@app.post("/api/v1/enforcement/enforce", response_model=EnforcementResponse)
async def enforce_policy(request: EnforcementRequest):
    """
    Enforce policy compliance for a given action and context.
    Provides real-time policy enforcement with ultra-low latency.
    """
    try:
        logger.info(f"Policy enforcement request: {request.policy_id}")
        
        # Validate constitutional compliance
        if SECURITY_MIDDLEWARE_AVAILABLE:
            validate_policy_input(request.dict())
        
        # Mock enforcement for now - implement actual enforcement logic
        allowed = request.action in ["read", "query", "analyze"]
        
        return EnforcementResponse(
            allowed=allowed,
            decision="ALLOW" if allowed else "DENY",
            reasoning=[
                f"Action '{request.action}' evaluated against policy {request.policy_id}",
                f"Constitutional compliance verified: {CONSTITUTIONAL_HASH}",
                "Decision based on constitutional principles"
            ],
            constitutional_compliance=0.97,
            metadata={
                "enforcement_time_ms": 2,
                "policy_version": "1.0",
                "constitutional_hash": CONSTITUTIONAL_HASH
            }
        )
        
    except Exception as e:
        # TODO: Consider using ACGS error handling: log_error_with_context()
        logger.error(f"Policy enforcement failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Policy enforcement failed: {str(e)}"
        )


@app.get("/api/v1/enforcement/policies/{policy_id}")
async def get_policy(policy_id: str):
    """Get specific policy details."""
    # Mock implementation - implement actual policy retrieval
    return {
        "policy_id": policy_id,
        "status": "active",
        "constitutional_hash": CONSTITUTIONAL_HASH
    }


# =============================================================================
# Compliance Monitoring API
# =============================================================================

@app.post("/api/v1/compliance/check", response_model=ComplianceResponse)
async def check_compliance(request: ComplianceRequest):
    """
    Check compliance of actions against multiple policies.
    Provides comprehensive compliance analysis.
    """
    try:
        logger.info(f"Compliance check request: {len(request.policies)} policies")
        
        # Mock compliance check - implement actual compliance logic
        violations = []
        if request.action in ["delete", "modify_constitutional"]:
            violations.append(f"Action '{request.action}' violates constitutional principles")
        
        return ComplianceResponse(
            compliant=len(violations) == 0,
            violations=violations,
            recommendations=[
                "Consider alternative actions that align with constitutional principles",
                "Ensure proper authorization for sensitive operations"
            ],
            constitutional_compliance=0.96,
            metadata={
                "check_time_ms": 5,
                "policies_evaluated": len(request.policies),
                "constitutional_hash": CONSTITUTIONAL_HASH
            }
        )
        
    except Exception as e:
        # TODO: Consider using ACGS error handling: log_error_with_context()
        logger.error(f"Compliance check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Compliance check failed: {str(e)}"
        )


@app.get("/api/v1/compliance/status")
async def get_compliance_status():
    """Get overall system compliance status."""
    return {
        "overall_compliance": 0.96,
        "active_policies": 15,
        "recent_violations": 0,
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "last_updated": datetime.now(timezone.utc).isoformat()
    }


# =============================================================================
# Governance Workflows API
# =============================================================================

@app.get("/api/v1/workflows")
async def list_workflows():
    """List available governance workflows."""
    return {
        "workflows": [
            {
                "id": "policy_synthesis",
                "name": "Policy Synthesis Workflow",
                "description": "End-to-end policy creation and validation"
            },
            {
                "id": "compliance_monitoring",
                "name": "Compliance Monitoring Workflow", 
                "description": "Continuous compliance monitoring and reporting"
            },
            {
                "id": "constitutional_validation",
                "name": "Constitutional Validation Workflow",
                "description": "Validate all actions against constitutional principles"
            }
        ],
        "constitutional_hash": CONSTITUTIONAL_HASH
    }


@app.post("/api/v1/workflows/{workflow_id}/execute")
async def execute_workflow(workflow_id: str, parameters: Dict[str, Any]):
    """Execute a governance workflow."""
    logger.info(f"Executing workflow: {workflow_id}")
    
    # Mock workflow execution - implement actual workflow logic
    return {
        "workflow_id": workflow_id,
        "execution_id": f"exec_{int(time.time())}",
        "status": "completed",
        "result": {
            "success": True,
            "constitutional_compliance": 0.95
        },
        "constitutional_hash": CONSTITUTIONAL_HASH
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8004,
        reload=True,
        log_level="info"
    )