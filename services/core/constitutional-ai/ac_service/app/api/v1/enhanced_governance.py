"""
Enhanced Governance Framework API Endpoints
Constitutional Hash: cdd01ef066bc6cf2

This module provides FastAPI endpoints for the enhanced constitutional governance
framework with production monitoring and domain-adaptive capabilities.

Key Features:
- RESTful API for governance evaluation
- Domain-specific governance endpoints
- Health checks and monitoring endpoints
- Performance metrics and diagnostics
- Integration with existing ACGS-2 services
"""

import logging
import time
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from services.shared.middleware.constitutional_validation import validate_constitutional_hash
from services.shared.validation.constitutional_validator import CONSTITUTIONAL_HASH
from ..services.enhanced_governance_framework import (
    DomainType,
    GovernanceFrameworkIntegration,
    create_enhanced_governance_integration,
)
from ..services.governance_monitoring import GovernanceMonitor

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/enhanced-governance", tags=["Enhanced Governance"])

# Global instances (initialized in main.py)
governance_integration: Optional[GovernanceFrameworkIntegration] = None
governance_monitor: Optional[GovernanceMonitor] = None


# Pydantic models
class GovernanceRequest(BaseModel):
    """Request model for governance evaluation"""
    query: str = Field(..., description="Query to evaluate for governance compliance")
    domain: str = Field(default="general", description="Domain type (general, healthcare, finance, research, legal)")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context for evaluation")
    include_formal_verification: bool = Field(default=False, description="Include formal verification in evaluation")
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH, description="Constitutional compliance hash")


class GovernanceResponse(BaseModel):
    """Response model for governance evaluation"""
    evaluation_id: str
    domain: str
    final_decision: str
    overall_compliance_score: float
    confidence: float
    enhanced_governance: Dict[str, Any]
    constitutional_validation: Optional[Dict[str, Any]]
    formal_verification: Optional[Dict[str, Any]]
    recommendations: List[str]
    processing_time_ms: float
    constitutional_hash: str
    timestamp: str


class HealthResponse(BaseModel):
    """Response model for health checks"""
    status: str
    timestamp: str
    metrics: Dict[str, float]
    circuit_breaker: Dict[str, Any]
    issues: List[str]
    constitutional_hash: str


class MetricsResponse(BaseModel):
    """Response model for performance metrics"""
    p99_latency_ms: float
    p95_latency_ms: float
    p50_latency_ms: float
    throughput_rps: float
    cache_hit_rate: float
    error_rate: float
    constitutional_compliance_rate: float
    timestamp: str
    constitutional_hash: str


# Dependency injection
async def get_governance_integration() -> GovernanceFrameworkIntegration:
    """Get governance integration instance"""
    if governance_integration is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Governance integration not initialized"
        )
    return governance_integration


async def get_governance_monitor() -> GovernanceMonitor:
    """Get governance monitor instance"""
    if governance_monitor is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Governance monitor not initialized"
        )
    return governance_monitor


# Circuit breaker check
async def check_circuit_breaker(monitor: GovernanceMonitor = Depends(get_governance_monitor)):
    """Check if circuit breaker is open"""
    if monitor.is_circuit_breaker_open():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service temporarily unavailable - circuit breaker is open"
        )


# API Endpoints
@router.post("/evaluate", response_model=GovernanceResponse)
async def evaluate_governance(
    request: GovernanceRequest,
    integration: GovernanceFrameworkIntegration = Depends(get_governance_integration),
    monitor: GovernanceMonitor = Depends(get_governance_monitor),
    _: None = Depends(check_circuit_breaker),
) -> GovernanceResponse:
    """
    Evaluate governance compliance using enhanced framework.
    
    This endpoint provides comprehensive governance evaluation using the 4-step
    algorithm with domain-adaptive capabilities and constitutional compliance.
    """
    start_time = time.time()
    
    try:
        # Validate constitutional hash
        if not validate_constitutional_hash(request.constitutional_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid constitutional hash. Expected: {CONSTITUTIONAL_HASH}"
            )
        
        # Parse domain type
        try:
            domain = DomainType(request.domain.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid domain type. Must be one of: {[d.value for d in DomainType]}"
            )
        
        # Perform governance evaluation
        result = await integration.evaluate_governance(
            query=request.query,
            domain=domain,
            context=request.context,
            include_formal_verification=request.include_formal_verification,
        )
        
        # Record monitoring metrics
        processing_time_ms = (time.time() - start_time) * 1000
        await monitor.record_request(
            latency_ms=processing_time_ms,
            success=True,
            cache_hit=processing_time_ms < 1.0,  # Assume cache hit if very fast
            constitutional_compliant=result["overall_compliance_score"] >= 0.8,
        )
        
        return GovernanceResponse(**result)
        
    except HTTPException:
        # Record failed request
        processing_time_ms = (time.time() - start_time) * 1000
        await monitor.record_request(
            latency_ms=processing_time_ms,
            success=False,
            cache_hit=False,
            constitutional_compliant=False,
        )
        raise
    except Exception as e:
        # Record failed request
        processing_time_ms = (time.time() - start_time) * 1000
        await monitor.record_request(
            latency_ms=processing_time_ms,
            success=False,
            cache_hit=False,
            constitutional_compliant=False,
        )
        
        logger.error("Governance evaluation failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during governance evaluation"
        )


@router.get("/health", response_model=HealthResponse)
async def get_health_status(
    monitor: GovernanceMonitor = Depends(get_governance_monitor),
) -> HealthResponse:
    """
    Get comprehensive health status for the governance framework.
    
    This endpoint provides health information for readiness and liveness probes,
    including performance metrics and circuit breaker status.
    """
    try:
        health_data = monitor.get_health_status()
        return HealthResponse(**health_data)
    except Exception as e:
        logger.error("Health check failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Health check failed"
        )


@router.get("/metrics", response_model=MetricsResponse)
async def get_performance_metrics(
    monitor: GovernanceMonitor = Depends(get_governance_monitor),
) -> MetricsResponse:
    """
    Get current performance metrics for the governance framework.
    
    This endpoint provides detailed performance metrics including latency,
    throughput, cache hit rates, and constitutional compliance rates.
    """
    try:
        current_metrics = monitor.get_current_metrics()
        return MetricsResponse(
            p99_latency_ms=current_metrics.p99_latency_ms,
            p95_latency_ms=current_metrics.p95_latency_ms,
            p50_latency_ms=current_metrics.p50_latency_ms,
            throughput_rps=current_metrics.throughput_rps,
            cache_hit_rate=current_metrics.cache_hit_rate,
            error_rate=current_metrics.error_rate,
            constitutional_compliance_rate=current_metrics.constitutional_compliance_rate,
            timestamp=current_metrics.timestamp.isoformat(),
            constitutional_hash=CONSTITUTIONAL_HASH,
        )
    except Exception as e:
        logger.error("Metrics collection failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Metrics collection failed"
        )


@router.get("/domains")
async def get_supported_domains() -> Dict[str, Any]:
    """
    Get list of supported governance domains.
    
    Returns information about available domain types and their configurations.
    """
    return {
        "domains": [
            {
                "name": domain.value,
                "description": f"Governance framework optimized for {domain.value} domain",
                "confidence_threshold": getattr(
                    DomainAdaptiveGovernance.DOMAIN_CONFIGS.get(domain, GovernanceConfig()),
                    "confidence_threshold",
                    0.6
                ),
            }
            for domain in DomainType
        ],
        "constitutional_hash": CONSTITUTIONAL_HASH,
    }


@router.post("/domains/{domain}/evaluate", response_model=GovernanceResponse)
async def evaluate_domain_governance(
    domain: str,
    query: str,
    context: Optional[Dict[str, Any]] = None,
    include_formal_verification: bool = False,
    integration: GovernanceFrameworkIntegration = Depends(get_governance_integration),
    monitor: GovernanceMonitor = Depends(get_governance_monitor),
    _: None = Depends(check_circuit_breaker),
) -> GovernanceResponse:
    """
    Evaluate governance for a specific domain.
    
    Convenience endpoint for domain-specific governance evaluation.
    """
    request = GovernanceRequest(
        query=query,
        domain=domain,
        context=context,
        include_formal_verification=include_formal_verification,
    )
    
    return await evaluate_governance(request, integration, monitor, _)


# Initialization function
def initialize_enhanced_governance_api(
    constitutional_validator=None,
    audit_logger=None,
    alerting_system=None,
    formal_verification_client=None,
) -> None:
    """
    Initialize enhanced governance API with dependencies.
    
    Args:
        constitutional_validator: ACGS constitutional validation service
        audit_logger: ACGS audit logging system
        alerting_system: ACGS monitoring and alerting system
        formal_verification_client: Formal verification service client
    """
    global governance_integration, governance_monitor
    
    try:
        # Initialize governance integration
        governance_integration = create_enhanced_governance_integration(
            constitutional_validator=constitutional_validator,
            audit_logger=audit_logger,
            alerting_system=alerting_system,
            formal_verification_client=formal_verification_client,
        )
        
        # Initialize governance monitor
        governance_monitor = GovernanceMonitor(
            alerting_system=alerting_system,
        )
        
        logger.info("Enhanced governance API initialized successfully")
        
    except Exception as e:
        logger.error("Failed to initialize enhanced governance API: %s", e)
        raise
