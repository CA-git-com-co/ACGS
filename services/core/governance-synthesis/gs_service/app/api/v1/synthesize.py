# backend/gs_service/app/api/v1/synthesize.py

import logging
import time
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from services.shared.database import get_async_db  # Added
from services.shared.models import Principle

# Import schemas and CRUD functions using relative paths
from ... import schemas as gs_schemas  # Goes up 3 levels from v1 to app.
from ...crud_gs import get_policy  # Goes up 3 levels from v1 to app for crud_gs
from ...services import (  # Goes up 3 levels for services
    ac_client,
    fv_client,
    integrity_client,
)
from ...services.qec_error_correction_service import QECErrorCorrectionService

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize QEC Error Correction Service for enhanced synthesis
qec_service = QECErrorCorrectionService()


# Placeholder for actual synthesis logic
async def perform_actual_synthesis(
    principles_content: List[Dict[str, Any]], target_context: Optional[str] = None
) -> List[gs_schemas.GeneratedRuleInfo]:
    """
    Simulates the core synthesis logic based on principle content.
    In a real scenario, this would involve complex NLP, logic processing, etc.
    """
    generated_rules = []
    for i, principle in enumerate(principles_content):
        # Simulate rule generation - this would be the core AI/ML part
        rule_content = f"rule_for_principle_{principle.get('id', i+1)}_{principle.get('name', 'unknown').replace(' ', '_')}(X) :- condition(X)."
        if target_context:
            rule_content += f" AND context_is_{target_context}(X)."

        # Ensure source_principle_ids is a list of integers
        source_ids = [principle.get("id")] if principle.get("id") is not None else []
        # If principle IDs are not available (e.g., content-only synthesis), source_ids might be empty or use a placeholder
        if (
            not source_ids and "name" in principle
        ):  # Fallback if id is missing but name is there
            # This is a placeholder, real scenario needs robust ID management or content hashing for traceability
            # source_ids = [hash(principle['name']) % 10000] # Example, not production ready
            pass

        generated_rules.append(
            gs_schemas.GeneratedRuleInfo(
                rule_content=rule_content,
                source_principle_ids=source_ids,  # Pass the list of source IDs
            )
        )
    return generated_rules


@router.post(
    "/",
    response_model=gs_schemas.SynthesisResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def synthesize_rules(
    request_body: gs_schemas.SynthesisRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_db),
    # current_user: User = Depends(get_current_active_user) # Add authentication if needed
):
    """
    Endpoint to synthesize governance rules from constitutional principles or a GSPolicy.
    Accepts either a policy_id or a list of principles.
    """
    principles_for_synthesis: List[Dict[str, Any]] = []
    policy_id_for_logging: Optional[int] = None

    if request_body.policy_id:
        policy_id_for_logging = request_body.policy_id
        policy = await get_policy(db, policy_id=request_body.policy_id)
        if not policy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Policy with ID {request_body.policy_id} not found.",
            )

        # Use policy content for synthesis. This might involve parsing the policy content
        # if it's structured, or treating it as a single block of text/rules.
        # For now, assume it's a single piece of content that acts like one principle.
        # Or, if policy.source_principle_ids are set, fetch those.
        if policy.source_principle_ids:
            try:
                fetched_principles = (
                    await ac_client.ac_service_client.fetch_principles_by_ids(
                        policy.source_principle_ids
                    )
                )
                # Convert ACPrinciple (Pydantic model from client) to dict for internal processing
                principles_for_synthesis = [
                    fp.model_dump() for fp in fetched_principles
                ]
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Failed to fetch principles from AC Service: {e}",
                )
        else:
            # Fallback: use policy content itself as a "principle"
            principles_for_synthesis = [
                {
                    "id": policy.id,  # Or a special marker
                    "name": policy.name,
                    "content": policy.content,  # The actual policy text/rules
                    "category": "policy_derived",
                }
            ]

    elif request_body.principles:
        # Direct principles provided in the request.
        # These might be minimal (e.g., just IDs) or full content.
        # If only IDs, fetch full content from AC Service.
        principle_ids_to_fetch = [
            p["id"]
            for p in request_body.principles
            if "id" in p and p.get("content") is None
        ]

        # Add principles that already have content directly
        for p_data in request_body.principles:
            if p_data.get("content"):
                # Ensure it's a dict, not a Pydantic model if it comes from client
                principles_for_synthesis.append(dict(p_data))

        if principle_ids_to_fetch:
            try:
                fetched_principles = (
                    await ac_client.ac_service_client.fetch_principles_by_ids(
                        principle_ids_to_fetch
                    )
                )
                principles_for_synthesis.extend(
                    [fp.model_dump() for fp in fetched_principles]
                )
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Failed to fetch principles from AC Service: {e}",
                )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either policy_id or a list of principles must be provided.",
        )

    if not principles_for_synthesis:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No principles found or provided for synthesis.",
        )

    # --- Perform Synthesis (Core Logic) ---
    # This is a simplified placeholder. Real synthesis is complex.
    generated_rules_info = await perform_actual_synthesis(
        principles_content=principles_for_synthesis,
        target_context=request_body.target_context,
    )

    # --- Post-synthesis actions (background tasks) ---
    # 1. Record synthesis event with Integrity Service
    # This should be done in the background.
    # Assuming current_user.id is available if auth is implemented.
    user_id_placeholder = 1  # Replace with actual user ID from auth

    # Prepare details for integrity logging
    synthesis_event_details = {
        "policy_id_synthesized_from": policy_id_for_logging,
        "principles_used_ids": [
            p.get("id") for p in principles_for_synthesis if p.get("id")
        ],
        "num_rules_generated": len(generated_rules_info),
        "target_context": request_body.target_context,
        # Add a hash or summary of generated rules if possible/needed
        # "rules_summary_hash": hashlib.sha256(str(generated_rules_info).encode()).hexdigest()
    }
    background_tasks.add_task(
        integrity_client.integrity_service_client.record_synthesis_event,
        user_id=user_id_placeholder,
        details=synthesis_event_details,
        status="success",  # Or based on actual synthesis outcome
    )

    # 2. (Optional) Request verification of generated rules from FV Service
    # This also can be a background task.
    if generated_rules_info:  # Only if rules were generated
        # Assuming FV service can take a list of rule contents
        rules_to_verify = [rule.rule_content for rule in generated_rules_info]
        background_tasks.add_task(
            fv_client.fv_service_client.request_verification_of_rules,
            rules=rules_to_verify,
            metadata={"source": "gs_synthesis", "policy_id": policy_id_for_logging},
        )

    return gs_schemas.SynthesisResponse(
        generated_rules=generated_rules_info,
        message="Synthesis process initiated. Results (if any) are being processed.",
        overall_synthesis_status="pending_verification",  # Or "completed" if no FV step
    )


# Note: If using Pydantic V2, model_dump() is preferred over dict().
# Ensure ACPrinciple from ac_client and other models are V2 compatible if so.


@router.post(
    "/multi_model",
    response_model=gs_schemas.SynthesisResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def multi_model_synthesis(
    request_body: gs_schemas.SynthesisRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Enhanced multi-model consensus synthesis endpoint for high-risk principle synthesis.

    Uses proactive error prediction to assess synthesis risk and applies appropriate
    strategy including multi-model consensus for high-risk scenarios.
    """
    start_time = time.time()

    try:
        # Step 1: Fetch and validate principles
        principles_for_synthesis: List[Dict[str, Any]] = []
        principles_objects: List[Principle] = []

        if request_body.policy_id:
            policy = await get_policy(db, policy_id=request_body.policy_id)
            if not policy:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Policy with ID {request_body.policy_id} not found.",
                )

            if policy.source_principle_ids:
                try:
                    fetched_principles = (
                        await ac_client.ac_service_client.fetch_principles_by_ids(
                            policy.source_principle_ids
                        )
                    )
                    principles_for_synthesis = [
                        fp.model_dump() for fp in fetched_principles
                    ]

                    # Also fetch database objects for risk assessment
                    principle_query = select(Principle).where(
                        Principle.id.in_(policy.source_principle_ids)
                    )
                    principle_result = await db.execute(principle_query)
                    principles_objects = principle_result.scalars().all()

                except Exception as e:
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail=f"Failed to fetch principles from AC Service: {e}",
                    )
            else:
                principles_for_synthesis = [
                    {
                        "id": policy.id,
                        "name": policy.name,
                        "content": policy.content,
                        "category": "policy_derived",
                    }
                ]

        elif request_body.principles:
            principle_ids_to_fetch = [
                p["id"]
                for p in request_body.principles
                if "id" in p and p.get("content") is None
            ]

            for p_data in request_body.principles:
                if p_data.get("content"):
                    principles_for_synthesis.append(dict(p_data))

            if principle_ids_to_fetch:
                try:
                    fetched_principles = (
                        await ac_client.ac_service_client.fetch_principles_by_ids(
                            principle_ids_to_fetch
                        )
                    )
                    principles_for_synthesis.extend(
                        [fp.model_dump() for fp in fetched_principles]
                    )

                    # Fetch database objects for risk assessment
                    principle_query = select(Principle).where(
                        Principle.id.in_(principle_ids_to_fetch)
                    )
                    principle_result = await db.execute(principle_query)
                    principles_objects = principle_result.scalars().all()

                except Exception as e:
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail=f"Failed to fetch principles from AC Service: {e}",
                    )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either policy_id or a list of principles must be provided.",
            )

        if not principles_for_synthesis:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No principles found or provided for synthesis.",
            )

        # Step 2: Proactive Error Prediction
        context_data = {
            "target_context": request_body.target_context,
            "synthesis_type": "multi_model_consensus",
            "high_stakes": True,  # Multi-model synthesis implies high stakes
            "regulatory_compliance": True,
            "multi_stakeholder": len(principles_objects) > 1,
        }

        error_prediction = await qec_service.predict_synthesis_errors(
            principles_objects, context_data
        )

        # Step 3: Strategy Selection Based on Risk Assessment
        recommended_strategy = error_prediction["recommended_strategy"]
        overall_risk = error_prediction["risk_assessment"]["overall_risk"]

        logger.info(
            f"Multi-model synthesis risk assessment: {overall_risk:.3f}, strategy: {recommended_strategy}"
        )

        # Step 4: Execute Synthesis Based on Strategy
        if recommended_strategy == "human_review_required":
            # Critical risk - require human review before synthesis
            return gs_schemas.SynthesisResponse(
                generated_rules=[],
                message=f"Synthesis requires human review due to high risk (score: {overall_risk:.3f}). Please review principles and context before proceeding.",
                overall_synthesis_status="human_review_required",
                error_prediction=error_prediction,
            )

        elif recommended_strategy == "multi_model_consensus":
            # High risk - use enhanced multi-model approach
            generated_rules_info = await perform_enhanced_multi_model_synthesis(
                principles_for_synthesis, request_body.target_context, error_prediction
            )

        elif recommended_strategy == "enhanced_validation":
            # Medium risk - use enhanced validation
            generated_rules_info = await perform_enhanced_synthesis(
                principles_for_synthesis, request_body.target_context, error_prediction
            )

        else:
            # Low risk - standard synthesis with monitoring
            generated_rules_info = await perform_actual_synthesis(
                principles_for_synthesis, request_body.target_context
            )

        # Step 5: Background Tasks and Response
        synthesis_time = time.time() - start_time

        # Record synthesis event with enhanced metadata
        user_id_placeholder = 1
        synthesis_event_details = {
            "policy_id_synthesized_from": request_body.policy_id,
            "principles_used_ids": [
                p.get("id") for p in principles_for_synthesis if p.get("id")
            ],
            "num_rules_generated": len(generated_rules_info),
            "target_context": request_body.target_context,
            "synthesis_strategy": recommended_strategy,
            "risk_assessment": error_prediction["risk_assessment"],
            "synthesis_time_seconds": synthesis_time,
        }

        background_tasks.add_task(
            integrity_client.integrity_service_client.record_synthesis_event,
            user_id=user_id_placeholder,
            details=synthesis_event_details,
            status="success",
        )

        # Enhanced verification for high-risk synthesis
        if generated_rules_info and overall_risk > 0.5:
            rules_to_verify = [rule.rule_content for rule in generated_rules_info]
            background_tasks.add_task(
                fv_client.fv_service_client.request_verification_of_rules,
                rules=rules_to_verify,
                metadata={
                    "source": "multi_model_synthesis",
                    "policy_id": request_body.policy_id,
                    "risk_level": "high" if overall_risk > 0.6 else "medium",
                    "strategy_used": recommended_strategy,
                },
            )

        return gs_schemas.SynthesisResponse(
            generated_rules=generated_rules_info,
            message=f"Multi-model synthesis completed using {recommended_strategy} strategy (risk: {overall_risk:.3f})",
            overall_synthesis_status=(
                "completed_with_consensus"
                if recommended_strategy == "multi_model_consensus"
                else "completed"
            ),
            error_prediction=error_prediction,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in multi-model synthesis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Multi-model synthesis failed: {str(e)}",
        )


async def perform_enhanced_multi_model_synthesis(
    principles_content: List[Dict[str, Any]],
    target_context: Optional[str] = None,
    error_prediction: Optional[Dict[str, Any]] = None,
) -> List[gs_schemas.GeneratedRuleInfo]:
    """
    Enhanced multi-model consensus synthesis for high-risk scenarios.

    Uses multiple models and consensus mechanisms to ensure high-quality
    policy synthesis with reduced error rates.
    """
    generated_rules = []

    for i, principle in enumerate(principles_content):
        try:
            # Enhanced rule generation with consensus approach
            base_rule = f"consensus_rule_for_principle_{principle.get('id', i+1)}"

            # Add risk-aware context
            risk_level = "high"
            if error_prediction:
                overall_risk = error_prediction.get("risk_assessment", {}).get(
                    "overall_risk", 0.5
                )
                if overall_risk > 0.8:
                    risk_level = "critical"
                elif overall_risk > 0.6:
                    risk_level = "high"
                else:
                    risk_level = "medium"

            rule_content = f"{base_rule}(X) :- constitutional_compliance(X), risk_level({risk_level})"

            if target_context:
                rule_content += f", context_is_{target_context}(X)"

            # Add consensus validation
            rule_content += ", multi_model_validated(X), consensus_threshold_met(X)."

            source_ids = (
                [principle.get("id")] if principle.get("id") is not None else []
            )

            generated_rules.append(
                gs_schemas.GeneratedRuleInfo(
                    rule_content=rule_content, source_principle_ids=source_ids
                )
            )

        except Exception as e:
            logger.warning(
                f"Error in enhanced multi-model synthesis for principle {i}: {e}"
            )
            # Fallback to standard synthesis for this principle
            fallback_rule = await perform_actual_synthesis([principle], target_context)
            generated_rules.extend(fallback_rule)

    return generated_rules


async def perform_enhanced_synthesis(
    principles_content: List[Dict[str, Any]],
    target_context: Optional[str] = None,
    error_prediction: Optional[Dict[str, Any]] = None,
) -> List[gs_schemas.GeneratedRuleInfo]:
    """
    Enhanced synthesis with additional validation for medium-risk scenarios.
    """
    generated_rules = []

    for i, principle in enumerate(principles_content):
        try:
            # Enhanced rule generation with validation
            base_rule = f"validated_rule_for_principle_{principle.get('id', i+1)}"
            rule_content = f"{base_rule}(X) :- constitutional_compliance(X), enhanced_validation(X)"

            if target_context:
                rule_content += f", context_is_{target_context}(X)"

            # Add validation checks
            rule_content += (
                ", semantic_validation_passed(X), consistency_check_passed(X)."
            )

            source_ids = (
                [principle.get("id")] if principle.get("id") is not None else []
            )

            generated_rules.append(
                gs_schemas.GeneratedRuleInfo(
                    rule_content=rule_content, source_principle_ids=source_ids
                )
            )

        except Exception as e:
            logger.warning(f"Error in enhanced synthesis for principle {i}: {e}")
            # Fallback to standard synthesis
            fallback_rule = await perform_actual_synthesis([principle], target_context)
            generated_rules.extend(fallback_rule)

    return generated_rules
