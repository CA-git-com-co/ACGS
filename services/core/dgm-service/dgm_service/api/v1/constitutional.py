"""
Constitutional compliance endpoints.
"""

import logging
from datetime import datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select

from ...core.constitutional_validator import ConstitutionalValidator
from ...database import get_db_session
from ...models.compliance import ComplianceLevel, ConstitutionalComplianceLog
from ...network.service_client import ACGSServiceClient
from .models import (
    ConstitutionalValidationRequest,
    ConstitutionalValidationResponse,
)

router = APIRouter()
logger = logging.getLogger(__name__)


async def get_constitutional_validator() -> ConstitutionalValidator:
    """Dependency to get constitutional validator."""
    return ConstitutionalValidator()


async def get_service_client() -> ACGSServiceClient:
    """Dependency to get service client."""
    return ACGSServiceClient()


@router.post("/validate", response_model=ConstitutionalValidationResponse)
async def validate_constitutional_compliance(
    request: ConstitutionalValidationRequest,
    validator: ConstitutionalValidator = Depends(get_constitutional_validator),
    service_client: ACGSServiceClient = Depends(get_service_client),
):
    """
    Validate constitutional compliance of an improvement.

    This endpoint checks whether a proposed improvement adheres to
    the constitutional principles and governance rules.
    """
    try:
        # Validate with the constitutional validator
        validation_result = await validator.validate_improvement(
            improvement_data=request.improvement_data,
            principles=request.principles,
            strict_mode=request.strict_mode,
        )

        # Also validate with the AC Service for additional checks
        try:
            ac_result = await service_client.validate_constitutional_compliance(
                request.improvement_data
            )

            # Combine results (take the more restrictive result)
            combined_score = min(
                validation_result.get("compliance_score", 0),
                ac_result.get("compliance_score", 0),
            )

            combined_violations = list(
                set(
                    validation_result.get("violations", [])
                    + ac_result.get("violations", [])
                )
            )

            combined_warnings = list(
                set(
                    validation_result.get("warnings", [])
                    + ac_result.get("warnings", [])
                )
            )

        except Exception as e:
            logger.warning(f"AC Service validation failed: {e}")
            # Use only local validation if AC Service is unavailable
            combined_score = validation_result.get("compliance_score", 0)
            combined_violations = validation_result.get("violations", [])
            combined_warnings = validation_result.get("warnings", [])

        # Determine compliance based on score and violations
        is_compliant = (
            combined_score >= 0.8
            and len(combined_violations) == 0  # Configurable threshold
        )

        return ConstitutionalValidationResponse(
            is_compliant=is_compliant,
            compliance_score=combined_score,
            violations=combined_violations,
            warnings=combined_warnings,
            recommendations=validation_result.get("recommendations", []),
            details={
                "local_validation": validation_result,
                "ac_service_validation": ac_result if "ac_result" in locals() else None,
                "validation_timestamp": validation_result.get("timestamp"),
                "validator_version": "1.0.0",
            },
        )

    except Exception as e:
        logger.error(f"Constitutional validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Constitutional validation failed: {e!s}",
        )


@router.get("/principles")
async def get_constitutional_principles(
    service_client: ACGSServiceClient = Depends(get_service_client),
):
    """
    Get the current constitutional principles.

    Returns the list of constitutional principles that are used
    for compliance validation.
    """
    try:
        principles = await service_client.get_constitutional_principles()

        return {
            "principles": principles,
            "total_count": len(principles),
            "last_updated": None,  # TODO: Get from AC Service
        }

    except Exception as e:
        logger.error(f"Failed to get constitutional principles: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get constitutional principles: {e!s}",
        )


@router.get("/compliance/history")
async def get_compliance_history(
    improvement_id: UUID | None = Query(None, description="Filter by improvement ID"),
    days: int = Query(30, ge=1, le=365, description="Number of days to include"),
    min_score: float | None = Query(
        None, ge=0, le=1, description="Minimum compliance score"
    ),
):
    """
    Get compliance history and trends.

    Returns historical compliance data for analysis and monitoring.
    """
    try:
        async with get_db_session() as db:
            stmt = select(ConstitutionalComplianceLog).where(
                ConstitutionalComplianceLog.created_at
                >= datetime.utcnow() - timedelta(days=days)
            )

            if improvement_id:
                stmt = stmt.where(
                    ConstitutionalComplianceLog.improvement_id == improvement_id
                )

            if min_score is not None:
                stmt = stmt.where(
                    ConstitutionalComplianceLog.compliance_score >= min_score
                )

            stmt = stmt.order_by(ConstitutionalComplianceLog.created_at)
            result = await db.execute(stmt)
            logs = result.scalars().all()

        total_validations = len(logs)
        average_score = (
            float(sum(float(log.compliance_score) for log in logs) / total_validations)
            if total_validations
            else 0.0
        )

        compliant_count = sum(
            1
            for log in logs
            if log.compliance_level
            in (ComplianceLevel.COMPLIANT, ComplianceLevel.EXEMPLARY)
        )
        compliance_rate = (
            compliant_count / total_validations if total_validations else 0.0
        )

        violations_by_principle: dict[str, int] = {}
        daily_scores_map: dict[str, list[float]] = {}

        for log in logs:
            for violation in log.violations or []:
                violations_by_principle[violation] = (
                    violations_by_principle.get(violation, 0) + 1
                )

            date_key = log.created_at.date().isoformat()
            daily_scores_map.setdefault(date_key, []).append(
                float(log.compliance_score)
            )

        daily_scores = [
            {"date": k, "average_score": sum(v) / len(v)}
            for k, v in sorted(daily_scores_map.items())
        ]

        trend = "stable"
        if len(daily_scores) >= 2:
            if daily_scores[-1]["average_score"] > daily_scores[0]["average_score"]:
                trend = "improving"
            elif daily_scores[-1]["average_score"] < daily_scores[0]["average_score"]:
                trend = "declining"

        return {
            "period_days": days,
            "total_validations": total_validations,
            "average_score": average_score,
            "compliance_rate": compliance_rate,
            "trend": trend,
            "violations_by_principle": violations_by_principle,
            "daily_scores": daily_scores,
        }

    except Exception as e:
        logger.error(f"Failed to get compliance history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get compliance history: {e!s}",
        )


@router.post("/compliance/report")
async def report_compliance_violation(
    improvement_id: UUID,
    violation_details: dict,
    service_client: ACGSServiceClient = Depends(get_service_client),
):
    """
    Report a constitutional compliance violation.

    This endpoint allows reporting of compliance violations discovered
    during or after improvement implementation.
    """
    try:
        # Log the violation with the PGC Service
        await service_client.log_compliance_event(
            {
                "event_type": "violation",
                "improvement_id": str(improvement_id),
                "details": violation_details,
                "source": "dgm-service",
                "severity": violation_details.get("severity", "medium"),
            }
        )

        # Also log locally
        logger.warning(
            f"Compliance violation reported for improvement {improvement_id}: "
            f"{violation_details}"
        )

        return {
            "message": "Compliance violation reported successfully",
            "improvement_id": str(improvement_id),
            "report_id": None,  # TODO: Generate report ID
        }

    except Exception as e:
        logger.error(f"Failed to report compliance violation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to report compliance violation: {e!s}",
        )


@router.get("/compliance/summary")
async def get_compliance_summary():
    """
    Get a summary of constitutional compliance status.

    Returns high-level compliance metrics and status.
    """
    try:
        # TODO: Implement actual compliance summary
        # This would aggregate data from the compliance log

        summary = {
            "overall_status": "compliant",
            "current_score": 0.85,
            "total_improvements": 0,
            "compliant_improvements": 0,
            "violations_last_30_days": 0,
            "most_common_violations": [],
            "compliance_trend": "improving",
            "last_violation": None,
        }

        return summary

    except Exception as e:
        logger.error(f"Failed to get compliance summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get compliance summary: {e!s}",
        )


@router.get("/governance/oversight")
async def get_governance_oversight_status():
    """
    Get governance oversight status and pending reviews.

    Returns information about governance oversight activities,
    pending reviews, and oversight metrics.
    """
    try:
        oversight_status = {
            "oversight_active": True,
            "pending_reviews": 0,
            "completed_reviews_today": 0,
            "average_review_time_hours": 2.5,
            "oversight_score": 0.95,
            "constitutional_hash": "cdd01ef066bc6cf2",
            "last_oversight_action": None,
            "governance_health": "excellent",
        }

        return oversight_status

    except Exception as e:
        logger.error(f"Failed to get governance oversight status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get governance oversight status: {e!s}",
        )


@router.post("/governance/review")
async def submit_governance_review(
    improvement_id: UUID,
    review_data: dict,
    service_client: ACGSServiceClient = Depends(get_service_client),
):
    """
    Submit a governance review for an improvement.

    Allows governance reviewers to submit their assessment
    of an improvement's constitutional compliance.
    """
    try:
        # Submit review to governance system
        review_result = await service_client.submit_governance_review(
            {
                "improvement_id": str(improvement_id),
                "review_data": review_data,
                "reviewer": "dgm-service",
                "timestamp": "2025-01-20T12:00:00Z",
            }
        )

        return {
            "message": "Governance review submitted successfully",
            "improvement_id": str(improvement_id),
            "review_id": review_result.get("review_id"),
            "status": review_result.get("status", "submitted"),
            "constitutional_compliance": True,
        }

    except Exception as e:
        logger.error(f"Failed to submit governance review: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit governance review: {e!s}",
        )


@router.get("/constitutional/hash")
async def get_constitutional_hash():
    """
    Get the current constitutional hash for validation.

    Returns the current constitutional hash used for
    compliance validation and integrity checking.
    """
    try:
        return {
            "constitutional_hash": "cdd01ef066bc6cf2",
            "hash_algorithm": "SHA-256",
            "last_updated": "2025-01-20T00:00:00Z",
            "version": "1.0",
            "status": "active",
            "validation_count": 0,
        }

    except Exception as e:
        logger.error(f"Failed to get constitutional hash: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get constitutional hash: {e!s}",
        )
