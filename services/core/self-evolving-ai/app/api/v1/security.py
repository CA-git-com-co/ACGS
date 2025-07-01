"""
Security API endpoints for ACGS-1 Self-Evolving AI Architecture Foundation.

This module provides REST API endpoints for security management, threat
assessment, mitigation, and monitoring within the self-evolving AI architecture.
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ...core.security_manager import SecurityManager
from ...dependencies import get_security_manager

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response Models
class ThreatDetectionRequest(BaseModel):
    """Request model for threat detection."""

    event_data: dict[str, Any] = Field(
        ..., description="Event data to analyze for threats"
    )
    source: str = Field(..., description="Source of the event")
    event_type: str = Field(..., description="Type of event")


class ThreatMitigationRequest(BaseModel):
    """Request model for threat mitigation."""

    threat_id: str = Field(..., description="Threat identifier to mitigate")
    additional_actions: list[str] = Field(
        default_factory=list, description="Additional mitigation actions"
    )


class SecurityAssessmentRequest(BaseModel):
    """Request model for security assessment."""

    assessment_type: str = Field(..., description="Type of security assessment")
    target_resource: str = Field(..., description="Target resource for assessment")
    assessment_data: dict[str, Any] = Field(
        default_factory=dict, description="Assessment data"
    )


class SecurityResponse(BaseModel):
    """Response model for security operations."""

    success: bool
    message: str
    data: dict[str, Any] | None = None


class ThreatDetectionResponse(BaseModel):
    """Response model for threat detection."""

    threat_detected: bool
    threat_assessment: dict[str, Any] | None = None
    message: str


class SecurityStatusResponse(BaseModel):
    """Response model for security status."""

    security_status: dict[str, Any]
    timestamp: str


# API Endpoints
@router.post("/threat-detection", response_model=ThreatDetectionResponse)
async def detect_threat(
    request: ThreatDetectionRequest,
    security_manager: SecurityManager = Depends(get_security_manager),
):
    """
    Detect potential security threats from event data.

    This endpoint analyzes event data for potential security threats using
    the multi-layer security framework. It returns threat assessments with
    recommended mitigation actions.
    """
    try:
        threat_assessment = await security_manager.detect_threat(request.event_data)

        if threat_assessment:
            return ThreatDetectionResponse(
                threat_detected=True,
                threat_assessment={
                    "threat_id": threat_assessment.threat_id,
                    "threat_level": threat_assessment.threat_level.value,
                    "threat_type": threat_assessment.threat_type,
                    "description": threat_assessment.description,
                    "affected_layers": [
                        layer.value for layer in threat_assessment.affected_layers
                    ],
                    "mitigation_required": threat_assessment.mitigation_required,
                    "mitigation_actions": threat_assessment.mitigation_actions,
                    "confidence_score": threat_assessment.confidence_score,
                    "detected_at": threat_assessment.detected_at.isoformat(),
                },
                message="Threat detected and assessed",
            )
        return ThreatDetectionResponse(
            threat_detected=False,
            threat_assessment=None,
            message="No threats detected",
        )

    except Exception as e:
        logger.error(f"Threat detection failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/threat-mitigation", response_model=SecurityResponse)
async def mitigate_threat(
    request: ThreatMitigationRequest,
    security_manager: SecurityManager = Depends(get_security_manager),
):
    """
    Mitigate an identified security threat.

    This endpoint executes mitigation actions for identified threats,
    implementing the appropriate security controls across all security layers.
    """
    try:
        mitigation_result = await security_manager.mitigate_threat(request.threat_id)

        if mitigation_result.get("success", False):
            return SecurityResponse(
                success=True,
                message="Threat mitigated successfully",
                data=mitigation_result,
            )
        return SecurityResponse(
            success=False,
            message="Failed to mitigate threat",
            data=mitigation_result,
        )

    except Exception as e:
        logger.error(f"Threat mitigation failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/assessment", response_model=SecurityResponse)
async def perform_security_assessment(
    request: SecurityAssessmentRequest,
    security_manager: SecurityManager = Depends(get_security_manager),
):
    """
    Perform a comprehensive security assessment.

    This endpoint conducts security assessments across all four security layers,
    providing detailed analysis and recommendations for security improvements.
    """
    try:
        # Create mock evolution request for assessment
        from ...core.evolution_engine import EvolutionRequest, EvolutionType

        mock_evolution = EvolutionRequest(
            evolution_type=EvolutionType.SECURITY_UPDATE,
            description=f"Security assessment for {request.target_resource}",
            justification="Security assessment request",
            requester_id="security_assessment_api",
        )

        assessment_result = await security_manager.assess_evolution_security(
            mock_evolution
        )

        return SecurityResponse(
            success=True,
            message="Security assessment completed",
            data={
                "assessment_type": request.assessment_type,
                "target_resource": request.target_resource,
                "assessment_result": assessment_result,
            },
        )

    except Exception as e:
        logger.error(f"Security assessment failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/status", response_model=SecurityStatusResponse)
async def get_security_status(
    security_manager: SecurityManager = Depends(get_security_manager),
):
    """
    Get current security status and metrics.

    This endpoint provides comprehensive security status information,
    including the state of all security layers, active threats, and
    security metrics.
    """
    try:
        security_status = await security_manager.get_security_status()

        return SecurityStatusResponse(
            security_status=security_status,
            timestamp=security_status.get("last_updated", ""),
        )

    except Exception as e:
        logger.error(f"Get security status failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/threats")
async def get_active_threats(
    security_manager: SecurityManager = Depends(get_security_manager),
):
    """
    Get all active security threats.

    This endpoint returns information about all currently active threats,
    including their severity, affected systems, and mitigation status.
    """
    try:
        active_threats = []

        for threat_id, threat in security_manager.active_threats.items():
            active_threats.append(
                {
                    "threat_id": threat_id,
                    "threat_level": threat.threat_level.value,
                    "threat_type": threat.threat_type,
                    "description": threat.description,
                    "affected_layers": [
                        layer.value for layer in threat.affected_layers
                    ],
                    "mitigation_required": threat.mitigation_required,
                    "mitigation_actions": threat.mitigation_actions,
                    "confidence_score": threat.confidence_score,
                    "detected_at": threat.detected_at.isoformat(),
                }
            )

        return {
            "success": True,
            "message": f"Retrieved {len(active_threats)} active threats",
            "data": {
                "active_threats": active_threats,
                "total_count": len(active_threats),
                "threat_levels": {
                    "critical": len(
                        [t for t in active_threats if t["threat_level"] == "critical"]
                    ),
                    "high": len(
                        [t for t in active_threats if t["threat_level"] == "high"]
                    ),
                    "medium": len(
                        [t for t in active_threats if t["threat_level"] == "medium"]
                    ),
                    "low": len(
                        [t for t in active_threats if t["threat_level"] == "low"]
                    ),
                },
            },
        }

    except Exception as e:
        logger.error(f"Get active threats failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/events")
async def get_security_events(
    limit: int = 100, security_manager: SecurityManager = Depends(get_security_manager)
):
    """
    Get recent security events.

    This endpoint returns recent security events from the audit log,
    providing visibility into security-related activities and incidents.
    """
    try:
        # Get recent security events (limited)
        recent_events = (
            security_manager.security_events[-limit:]
            if security_manager.security_events
            else []
        )

        events_data = []
        for event in recent_events:
            events_data.append(
                {
                    "event_id": event.event_id,
                    "event_type": event.event_type,
                    "severity": event.severity.value,
                    "source": event.source,
                    "description": event.description,
                    "timestamp": event.timestamp.isoformat(),
                    "metadata": event.metadata,
                }
            )

        return {
            "success": True,
            "message": f"Retrieved {len(events_data)} security events",
            "data": {
                "security_events": events_data,
                "total_count": len(events_data),
                "limit": limit,
            },
        }

    except Exception as e:
        logger.error(f"Get security events failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/layers")
async def get_security_layers_status(
    security_manager: SecurityManager = Depends(get_security_manager),
):
    """
    Get status of all security layers.

    This endpoint provides detailed status information for each of the
    four security layers: sandboxing, policy engine, authentication, and audit.
    """
    try:
        security_status = await security_manager.get_security_status()
        layers_status = security_status.get("security_layers", {})

        return {
            "success": True,
            "message": "Security layers status retrieved",
            "data": {
                "layers": layers_status,
                "total_layers": len(layers_status),
                "active_layers": len(
                    [
                        layer
                        for layer in layers_status.values()
                        if layer.get("status") == "active"
                    ]
                ),
                "layer_health": {
                    layer_name: layer_info.get("status", "unknown")
                    for layer_name, layer_info in layers_status.items()
                },
            },
        }

    except Exception as e:
        logger.error(f"Get security layers status failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/metrics")
async def get_security_metrics(
    security_manager: SecurityManager = Depends(get_security_manager),
):
    """
    Get security performance metrics.

    This endpoint provides comprehensive security metrics including
    threat detection rates, mitigation success rates, and security
    event statistics.
    """
    try:
        return {
            "success": True,
            "message": "Security metrics retrieved successfully",
            "data": {
                "metrics": security_manager.security_metrics,
                "threat_categories": list(security_manager.threat_categories.keys()),
                "active_threats_count": len(security_manager.active_threats),
                "security_events_count": len(security_manager.security_events),
            },
        }

    except Exception as e:
        logger.error(f"Get security metrics failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/health")
async def security_health_check(
    security_manager: SecurityManager = Depends(get_security_manager),
):
    """
    Health check for the security manager.

    This endpoint provides health status information for the security manager,
    including the status of all security layers and threat detection capabilities.
    """
    try:
        health_status = await security_manager.health_check()

        if health_status.get("healthy", False):
            return {
                "status": "healthy",
                "message": "Security manager is operational",
                "data": health_status,
            }
        return {
            "status": "unhealthy",
            "message": "Security manager has issues",
            "data": health_status,
        }

    except Exception as e:
        logger.error(f"Security health check failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
