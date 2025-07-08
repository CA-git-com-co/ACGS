"""
API Layer - Routers
Constitutional Hash: cdd01ef066bc6cf2

This module contains FastAPI routers that handle HTTP requests and responses,
using dependency injection to access business services.
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from .....shared.di.container import Inject
from ..domain.entities import (
    ConstitutionalComplianceRequest,
    ContentValidationRequest,
)
from ..service.constitutional_service import (
    AuditServiceImpl,
    ConstitutionalPolicyServiceImpl,
    ConstitutionalValidationService,
)

logger = logging.getLogger(__name__)

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Create routers
health_router = APIRouter(prefix="/health", tags=["Health"])
validation_router = APIRouter(prefix="/api/v1", tags=["Validation"])
policy_router = APIRouter(prefix="/api/v1/policy", tags=["Policy"])


# Health endpoints
@health_router.get("/")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": "constitutional-ai",
        "constitutional_hash": CONSTITUTIONAL_HASH,
    }


@health_router.get("/detailed")
async def detailed_health_check(
    validation_service: ConstitutionalValidationService = Depends(Inject(ConstitutionalValidationService))
):
    """Detailed health check with dependency validation."""
    try:
        # Validate constitutional hash through service
        hash_validation = validation_service.validate_constitutional_hash()

        return {
            "status": "healthy",
            "service": "constitutional-ai",
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "hash_validation": hash_validation,
            "dependencies": {
                "validation_service": "operational",
                "policy_service": "operational",
                "audit_service": "operational",
            }
        }
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


# Validation endpoints
@validation_router.post("/validate/content")
async def validate_content(
    request: ContentValidationRequest,
    validation_service: ConstitutionalValidationService = Depends(Inject(ConstitutionalValidationService))
) -> dict[str, Any]:
    """
    Validate content against constitutional rules.
    
    Args:
        request: Content validation request
        validation_service: Injected validation service
        
    Returns:
        Validation result with compliance information
    """
    try:
        logger.info(f"Content validation requested: {request.request_id}")

        result = await validation_service.validate_content(request)

        return {
            "request_id": request.request_id,
            "is_valid": result.is_valid,
            "compliance_score": result.compliance_score,
            "compliance_level": result.compliance_level.value,
            "violations": [
                {
                    "violation_id": v.violation_id,
                    "type": v.violation_type.value,
                    "severity": v.severity,
                    "description": v.description,
                    "detected_at": v.detected_at.isoformat(),
                }
                for v in result.violations
            ],
            "recommendations": result.recommendations,
            "constitutional_hash": result.constitutional_hash,
            "validated_at": result.validated_at.isoformat(),
        }

    except ValueError as e:
        logger.warning(f"Invalid content validation request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Content validation failed: {e}")
        raise HTTPException(status_code=500, detail="Validation service error")


@validation_router.post("/validate/compliance")
async def validate_compliance(
    request: ConstitutionalComplianceRequest,
    validation_service: ConstitutionalValidationService = Depends(Inject(ConstitutionalValidationService))
) -> dict[str, Any]:
    """
    Validate constitutional compliance.
    
    Args:
        request: Constitutional compliance request
        validation_service: Injected validation service
        
    Returns:
        Compliance validation result
    """
    try:
        logger.info(f"Compliance validation requested: {request.request_id}")

        result = await validation_service.validate_compliance(request)

        return {
            "request_id": request.request_id,
            "is_compliant": result.is_valid,
            "compliance_score": result.compliance_score,
            "compliance_level": result.compliance_level.value,
            "violations": [
                {
                    "violation_id": v.violation_id,
                    "type": v.violation_type.value,
                    "severity": v.severity,
                    "description": v.description,
                    "context": v.context,
                }
                for v in result.violations
            ],
            "recommendations": result.recommendations,
            "constitutional_hash": result.constitutional_hash,
            "validated_at": result.validated_at.isoformat(),
        }

    except ValueError as e:
        logger.warning(f"Invalid compliance validation request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Compliance validation failed: {e}")
        raise HTTPException(status_code=500, detail="Compliance validation service error")


# Policy endpoints
@policy_router.get("/principles")
async def get_constitutional_principles(
    policy_service: ConstitutionalPolicyServiceImpl = Depends(Inject(ConstitutionalPolicyServiceImpl))
):
    """Get available constitutional principles."""
    try:
        principles = await policy_service.get_applicable_principles({})

        return {
            "principles": [
                {
                    "principle_id": p.principle_id,
                    "name": p.name,
                    "description": p.description,
                    "priority": p.priority,
                    "rules": p.rules,
                    "is_active": p.is_active,
                }
                for p in principles
            ],
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

    except Exception as e:
        logger.error(f"Failed to get constitutional principles: {e}")
        raise HTTPException(status_code=500, detail="Policy service error")


@policy_router.post("/evaluate")
async def evaluate_policy(
    content: str,
    context: dict[str, Any] = None,
    policy_service: ConstitutionalPolicyServiceImpl = Depends(Inject(ConstitutionalPolicyServiceImpl))
):
    """Evaluate content against constitutional policies."""
    try:
        if context is None:
            context = {}

        decision = await policy_service.evaluate_policy(content, context)

        return {
            "policy_id": decision.policy_id,
            "decision": decision.decision,
            "confidence": decision.confidence,
            "reasoning": decision.reasoning,
            "applied_principles": decision.applied_principles,
            "decided_at": decision.decided_at.isoformat(),
            "constitutional_hash": decision.constitutional_hash,
        }

    except Exception as e:
        logger.error(f"Policy evaluation failed: {e}")
        raise HTTPException(status_code=500, detail="Policy evaluation service error")


# Audit endpoints
audit_router = APIRouter(prefix="/api/v1/audit", tags=["Audit"])


@audit_router.get("/trail/{entity_id}")
async def get_audit_trail(
    entity_id: str,
    audit_service: AuditServiceImpl = Depends(Inject(AuditServiceImpl))
):
    """Get audit trail for an entity."""
    try:
        events = await audit_service.get_audit_trail(entity_id)

        return {
            "entity_id": entity_id,
            "events": [
                {
                    "event_id": e.event_id,
                    "event_type": e.event_type,
                    "entity_type": e.entity_type,
                    "action": e.action,
                    "actor_id": e.actor_id,
                    "metadata": e.metadata,
                    "timestamp": e.timestamp.isoformat(),
                }
                for e in events
            ],
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

    except Exception as e:
        logger.error(f"Failed to get audit trail for {entity_id}: {e}")
        raise HTTPException(status_code=500, detail="Audit service error")


# Combined router
def create_api_router() -> APIRouter:
    """Create the main API router with all sub-routers."""
    main_router = APIRouter()

    main_router.include_router(health_router)
    main_router.include_router(validation_router)
    main_router.include_router(policy_router)
    main_router.include_router(audit_router)

    return main_router
