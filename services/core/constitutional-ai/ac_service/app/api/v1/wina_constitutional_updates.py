"""
WINA Constitutional Updates API endpoints for ACGS-PGP

This module provides API endpoints for WINA-informed constitutional principle updates,
integrating with the Constitutional Council and AC service for governance workflows.
"""

import logging
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from services.shared.database import get_async_db
from services.shared.wina.constitutional_integration import (  # Constitutional compliance hash for ACGS
    CONSTITUTIONAL_HASH,
    WINAConstitutionalPrincipleAnalyzer,
    WINAConstitutionalUpdateService,
    "cdd01ef066bc6cf2",
    =,
)

from ...core.auth import require_admin_role, require_constitutional_council_role
from ...crud import get_principle, get_principles
from ...models import User

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize WINA services
wina_analyzer = WINAConstitutionalPrincipleAnalyzer()
wina_update_service = WINAConstitutionalUpdateService(analyzer=wina_analyzer)


def _principle_to_dict(principle: Any) -> dict[str, Any]:
    """Convert a Principle ORM object to a dictionary for WINA analysis."""
    dependencies: list[str] = []
    metadata = getattr(principle, "constitutional_metadata", None)
    if isinstance(metadata, dict):
        dependencies = (
            metadata.get("related_principles") or metadata.get("dependencies") or []
        )

    constraints = getattr(principle, "constraints", None)
    if not dependencies and isinstance(constraints, dict):
        dependencies = constraints.get("dependencies", [])

    return {
        "principle_id": str(principle.id),
        "name": principle.name,
        "description": principle.description,
        "category": principle.category,
        "policy_code": getattr(principle, "policy_code", "") or "",
        "dependencies": dependencies,
    }


@router.post("/analyze-principles", response_model=dict[str, Any])
async def analyze_principles_for_wina_optimization(
    principle_ids: list[str] | None = None,
    optimization_context: dict[str, Any] | None = None,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_admin_role),
):
    """
    Analyze constitutional principles for WINA optimization opportunities.

    Args:
        principle_ids: Optional list of specific principle IDs to analyze
        optimization_context: Context for optimization analysis
        current_user: Current authenticated user (admin required)

    Returns:
        Analysis results for each principle
    """
    logger.info(f"Analyzing principles for WINA optimization by user {current_user.id}")

    try:
        # Get principles to analyze
        if principle_ids:
            principles = []
            for principle_id in principle_ids:
                principle = await get_principle(db, int(principle_id))
                if principle:
                    principles.append(_principle_to_dict(principle))
        else:
            # Get all principles
            db_principles = await get_principles(db)
            principles = [_principle_to_dict(p) for p in db_principles]

        if not principles:
            raise HTTPException(
                status_code=404, detail="No principles found for analysis"
            )

        # Set default optimization context
        if not optimization_context:
            optimization_context = {
                "target_gflops_reduction": 0.5,
                "min_accuracy_retention": 0.95,
                "optimization_mode": "conservative",
                "safety_critical_domains": ["safety", "security"],
            }

        # Analyze each principle
        analysis_results = {}
        for principle in principles:
            try:
                analysis = await wina_analyzer.analyze_principle_for_wina_optimization(
                    principle, optimization_context
                )
                analysis_results[principle["principle_id"]] = analysis

            except Exception as e:
                logger.error(
                    f"Error analyzing principle {principle['principle_id']}: {e}"
                )
                analysis_results[principle["principle_id"]] = {
                    "error": str(e),
                    "optimization_potential": 0.0,
                }

        return {
            "success": True,
            "analyzed_principles": len(principles),
            "optimization_context": optimization_context,
            "analysis_results": analysis_results,
            "summary": {
                "high_potential": len(
                    [
                        r
                        for r in analysis_results.values()
                        if r.get("optimization_potential", 0) > 0.7
                    ]
                ),
                "medium_potential": len(
                    [
                        r
                        for r in analysis_results.values()
                        if 0.4 <= r.get("optimization_potential", 0) <= 0.7
                    ]
                ),
                "low_potential": len(
                    [
                        r
                        for r in analysis_results.values()
                        if r.get("optimization_potential", 0) < 0.4
                    ]
                ),
            },
        }

    except Exception as e:
        logger.error(f"Error in WINA principle analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e!s}")


@router.post("/propose-updates", response_model=dict[str, Any])
async def propose_constitutional_updates(
    principle_ids: list[str],
    optimization_context: dict[str, Any] | None = None,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_admin_role),
):
    """
    Propose constitutional principle updates based on WINA analysis.

    Args:
        principle_ids: List of principle IDs to propose updates for
        optimization_context: Context for optimization analysis
        background_tasks: Background tasks for async processing
        current_user: Current authenticated user (admin required)

    Returns:
        Proposed constitutional principle updates
    """
    logger.info(
        f"Proposing constitutional updates for {len(principle_ids)} principles by user {current_user.id}"
    )

    try:
        # Get principles
        principles = []
        for principle_id in principle_ids:
            principle = await get_principle(db, int(principle_id))
            if principle:
                principles.append(_principle_to_dict(principle))

        if not principles:
            raise HTTPException(
                status_code=404, detail="No valid principles found for update proposal"
            )

        # Set default optimization context
        if not optimization_context:
            optimization_context = {
                "target_gflops_reduction": 0.5,
                "min_accuracy_retention": 0.95,
                "optimization_mode": "conservative",
                "proposer_user_id": current_user.id,
            }

        # Propose updates
        proposed_updates = await wina_update_service.propose_constitutional_updates(
            principles, optimization_context
        )

        # Convert to serializable format
        updates_data = []
        for update in proposed_updates:
            updates_data.append(
                {
                    "principle_id": update.principle_id,
                    "update_type": update.update_type,
                    "rationale": update.rationale,
                    "efficiency_impact": update.efficiency_impact,
                    "constitutional_distance": update.constitutional_distance,
                    "risk_assessment": update.risk_assessment,
                    "approval_status": update.approval_status,
                    "timestamp": update.timestamp.isoformat(),
                    "optimization_potential": (
                        update.wina_analysis.get("optimization_potential", 0.0)
                        if update.wina_analysis
                        else 0.0
                    ),
                }
            )

        return {
            "success": True,
            "proposed_updates": len(proposed_updates),
            "updates": updates_data,
            "optimization_context": optimization_context,
            "next_steps": [
                "Review proposed updates",
                "Submit for Constitutional Council approval",
                "Monitor implementation performance",
            ],
        }

    except Exception as e:
        logger.error(f"Error proposing constitutional updates: {e}")
        raise HTTPException(status_code=500, detail=f"Update proposal failed: {e!s}")


@router.post("/submit-for-approval/{principle_id}", response_model=dict[str, Any])
async def submit_update_for_approval(
    principle_id: str,
    approval_context: dict[str, Any] | None = None,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_constitutional_council_role),
):
    """
    Submit a constitutional update for approval through the Constitutional Council.

    Args:
        principle_id: ID of the principle with pending update
        approval_context: Additional context for approval process
        current_user: Current authenticated user (Constitutional Council member required)

    Returns:
        Submission result with approval tracking information
    """
    logger.info(
        f"Submitting constitutional update for principle {principle_id} for approval by user {current_user.id}"
    )

    try:
        # Get pending update
        if principle_id not in wina_update_service.pending_updates:
            raise HTTPException(
                status_code=404,
                detail=f"No pending update found for principle {principle_id}",
            )

        update = wina_update_service.pending_updates[principle_id]

        # Set approval context
        if not approval_context:
            approval_context = {
                "submitter_user_id": current_user.id,
                "submission_timestamp": update.timestamp.isoformat(),
                "priority": "normal",
            }

        # Submit for approval
        submission_result = await wina_update_service.submit_update_for_approval(
            update, approval_context
        )

        return {
            "success": submission_result["success"],
            "principle_id": principle_id,
            "submission_result": submission_result,
            "approval_tracking": {
                "status": submission_result.get("approval_status"),
                "estimated_review_time": submission_result.get("estimated_review_time"),
                "submission_id": submission_result.get("submission_id"),
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting update for approval: {e}")
        raise HTTPException(
            status_code=500, detail=f"Approval submission failed: {e!s}"
        )


@router.get("/pending-updates", response_model=dict[str, Any])
async def get_pending_updates(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_admin_role),
):
    """
    Get all pending WINA constitutional updates.

    Returns:
        List of pending constitutional principle updates
    """
    logger.info(f"Getting pending constitutional updates for user {current_user.id}")

    try:
        pending_updates = []
        for _principle_id, update in wina_update_service.pending_updates.items():
            pending_updates.append(
                {
                    "principle_id": update.principle_id,
                    "update_type": update.update_type,
                    "rationale": update.rationale,
                    "approval_status": update.approval_status,
                    "constitutional_distance": update.constitutional_distance,
                    "risk_level": (
                        update.risk_assessment.get("overall_risk_level")
                        if update.risk_assessment
                        else "unknown"
                    ),
                    "timestamp": update.timestamp.isoformat(),
                    "optimization_potential": (
                        update.wina_analysis.get("optimization_potential", 0.0)
                        if update.wina_analysis
                        else 0.0
                    ),
                }
            )

        return {
            "success": True,
            "pending_updates_count": len(pending_updates),
            "pending_updates": pending_updates,
            "summary": {
                "high_risk": len(
                    [u for u in pending_updates if u["risk_level"] == "high"]
                ),
                "medium_risk": len(
                    [u for u in pending_updates if u["risk_level"] == "medium"]
                ),
                "low_risk": len(
                    [u for u in pending_updates if u["risk_level"] == "low"]
                ),
            },
        }

    except Exception as e:
        logger.error(f"Error getting pending updates: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve pending updates: {e!s}"
        )


@router.get("/update-history", response_model=dict[str, Any])
async def get_update_history(
    limit: int = 50,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_admin_role),
):
    """
    Get history of WINA constitutional updates.

    Args:
        limit: Maximum number of history entries to return

    Returns:
        History of constitutional principle updates
    """
    logger.info(f"Getting constitutional update history for user {current_user.id}")

    try:
        history = (
            wina_update_service.update_history[-limit:]
            if wina_update_service.update_history
            else []
        )

        return {
            "success": True,
            "history_count": len(history),
            "update_history": history,
            "summary": {
                "total_updates": len(wina_update_service.update_history),
                "approved_updates": len(wina_update_service.approved_updates),
                "pending_updates": len(wina_update_service.pending_updates),
            },
        }

    except Exception as e:
        logger.error(f"Error getting update history: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve update history: {e!s}"
        )
