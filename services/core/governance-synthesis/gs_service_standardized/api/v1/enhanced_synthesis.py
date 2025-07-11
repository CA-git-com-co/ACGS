"""
Enhanced Governance Synthesis API Endpoints

API endpoints for the enhanced governance synthesis service with OPA integration,
providing comprehensive policy validation, conflict detection, and performance
optimization.

Phase 2: Governance Synthesis Hardening with Rego/OPA Integration
"""

import logging
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from pydantic import BaseModel, Field

from ...core.opa_integration import OPAIntegrationError
from ...services.enhanced_governance_synthesis import (  # Constitutional compliance hash for ACGS
    CONSTITUTIONAL_HASH,
    EnhancedSynthesisRequest,
    get_enhanced_synthesis_service,
)

from ...services.policy_validator import ValidationLevel

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)

router = APIRouter()


# Pydantic models for API requests and responses
class ConstitutionalPrincipleAPI(BaseModel):
    """Constitutional principle for API requests."""

    description: str = Field(..., description="Description of the constitutional principle")
    type: str = Field(..., description="Type of principle (e.g., fairness, transparency)")
    category: str | None = Field(None, description="Category of the principle")
    weight: float | None = Field(1.0, description="Weight/importance of the principle")


class EnhancedSynthesisRequestAPI(BaseModel):
    """Enhanced synthesis request for API."""

    synthesis_goal: str = Field(..., description="Goal of the policy synthesis")
    constitutional_principles: list[ConstitutionalPrincipleAPI] = Field(
        ..., description="Constitutional principles to consider"
    )
    constraints: list[str] | None = Field(None, description="Additional constraints")
    context_data: dict[str, Any] | None = Field(None, description="Context data for synthesis")
    target_format: str = Field("rego", description="Target format for the policy")
    policy_type: str = Field("governance_rule", description="Type of policy to synthesize")

    # Validation options
    validation_level: str = Field(
        "standard", description="Validation level (basic, standard, comprehensive)"
    )
    enable_opa_validation: bool = Field(True, description="Enable OPA-based validation")
    enable_conflict_detection: bool = Field(True, description="Enable conflict detection")
    enable_compliance_checking: bool = Field(True, description="Enable compliance checking")
    enable_constitutional_validation: bool = Field(
        True, description="Enable constitutional validation"
    )

    # Performance options
    enable_parallel_validation: bool = Field(True, description="Enable parallel validation")
    max_validation_latency_ms: int = Field(
        50, description="Maximum validation latency in milliseconds"
    )

    # Integration options
    enable_wina_optimization: bool = Field(True, description="Enable WINA optimization")
    enable_alphaevolve_synthesis: bool = Field(True, description="Enable AlphaEvolve synthesis")
    enable_langgraph_workflow: bool = Field(True, description="Enable LangGraph workflow")


class ValidationResultAPI(BaseModel):
    """Validation result for API response."""

    is_valid: bool
    overall_score: float
    validation_time_ms: float
    errors: list[str]
    warnings: list[str]
    recommendations: list[str]
    decision_latency_ms: float
    cache_hit: bool


class EnhancedSynthesisResponseAPI(BaseModel):
    """Enhanced synthesis response for API."""

    synthesis_id: str
    synthesis_time_ms: float
    synthesized_policy: str
    policy_metadata: dict[str, Any]
    validation_result: ValidationResultAPI | None
    is_valid: bool
    validation_score: float
    synthesis_latency_ms: float
    validation_latency_ms: float
    total_latency_ms: float
    wina_metadata: dict[str, Any] | None
    alphaevolve_metadata: dict[str, Any] | None
    langgraph_metadata: dict[str, Any] | None
    errors: list[str]
    warnings: list[str]
    recommendations: list[str]


class BatchSynthesisRequestAPI(BaseModel):
    """Batch synthesis request for API."""

    requests: list[EnhancedSynthesisRequestAPI] = Field(
        ..., description="List of synthesis requests"
    )
    enable_parallel_processing: bool = Field(
        True, description="Enable parallel processing of requests"
    )


class HealthCheckResponseAPI(BaseModel):
    """Health check response for API."""

    service: str
    status: str
    components: dict[str, Any]
    service_metrics: dict[str, Any]
    timestamp: str


@validate_policy_input
@router.post("/synthesize", response_model=EnhancedSynthesisResponseAPI)
async def synthesize_policy(
    request: EnhancedSynthesisRequestAPI, background_tasks: BackgroundTasks
) -> EnhancedSynthesisResponseAPI:
    """
    Synthesize a governance policy with comprehensive OPA validation.

    This endpoint provides enhanced policy synthesis with:
    - Multiple synthesis methods (WINA, AlphaEvolve, LangGraph)
    - Comprehensive OPA-based validation
    - Constitutional compliance checking
    - Policy conflict detection
    - Performance optimization with <50ms validation target
    """
    try:
        # Get enhanced synthesis service
        synthesis_service = await get_enhanced_synthesis_service()

        # Convert API request to service request
        service_request = EnhancedSynthesisRequest(
            synthesis_goal=request.synthesis_goal,
            constitutional_principles=[
                {
                    "description": p.description,
                    "type": p.type,
                    "category": p.category,
                    "weight": p.weight,
                }
                for p in request.constitutional_principles
            ],
            constraints=request.constraints,
            context_data=request.context_data or {},
            target_format=request.target_format,
            policy_type=request.policy_type,
            validation_level=ValidationLevel(request.validation_level),
            enable_opa_validation=request.enable_opa_validation,
            enable_conflict_detection=request.enable_conflict_detection,
            enable_compliance_checking=request.enable_compliance_checking,
            enable_constitutional_validation=request.enable_constitutional_validation,
            enable_parallel_validation=request.enable_parallel_validation,
            max_validation_latency_ms=request.max_validation_latency_ms,
            enable_wina_optimization=request.enable_wina_optimization,
            enable_alphaevolve_synthesis=request.enable_alphaevolve_synthesis,
            enable_langgraph_workflow=request.enable_langgraph_workflow,
        )

        # Execute synthesis
        synthesis_response = await synthesis_service.synthesize_policy(service_request)

        # Convert validation response
        validation_result = None
        if synthesis_response.validation_response:
            validation_result = ValidationResultAPI(
                is_valid=synthesis_response.validation_response.is_valid,
                overall_score=synthesis_response.validation_response.overall_score,
                validation_time_ms=synthesis_response.validation_response.validation_time_ms,
                errors=synthesis_response.validation_response.errors,
                warnings=synthesis_response.validation_response.warnings,
                recommendations=synthesis_response.validation_response.recommendations,
                decision_latency_ms=synthesis_response.validation_response.decision_latency_ms,
                cache_hit=synthesis_response.validation_response.cache_hit,
            )

        # Convert service response to API response
        api_response = EnhancedSynthesisResponseAPI(
            synthesis_id=synthesis_response.synthesis_id,
            synthesis_time_ms=synthesis_response.synthesis_time_ms,
            synthesized_policy=synthesis_response.synthesized_policy,
            policy_metadata=synthesis_response.policy_metadata,
            validation_result=validation_result,
            is_valid=synthesis_response.is_valid,
            validation_score=synthesis_response.validation_score,
            synthesis_latency_ms=synthesis_response.synthesis_latency_ms,
            validation_latency_ms=synthesis_response.validation_latency_ms,
            total_latency_ms=synthesis_response.total_latency_ms,
            wina_metadata=(
                synthesis_response.wina_result.__dict__ if synthesis_response.wina_result else None
            ),
            alphaevolve_metadata=synthesis_response.alphaevolve_metadata,
            langgraph_metadata=synthesis_response.langgraph_metadata,
            errors=synthesis_response.errors,
            warnings=synthesis_response.warnings,
            recommendations=synthesis_response.recommendations,
        )

        logger.info(f"Enhanced synthesis completed: {synthesis_response.synthesis_id}")
        return api_response

    except OPAIntegrationError as e:
        logger.error(f"OPA integration error in synthesis: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"OPA integration error: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Enhanced synthesis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Synthesis failed: {str(e)}",
        )


@validate_policy_input
@router.post("/batch-synthesize", response_model=list[EnhancedSynthesisResponseAPI])
async def batch_synthesize_policies(
    request: BatchSynthesisRequestAPI, background_tasks: BackgroundTasks
) -> list[EnhancedSynthesisResponseAPI]:
    """
    Synthesize multiple governance policies in batch for improved performance.

    This endpoint provides batch processing with:
    - Parallel synthesis execution
    - Optimized resource utilization
    - Comprehensive validation for all policies
    - Performance metrics for batch operations
    """
    try:
        if not request.requests:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No synthesis requests provided",
            )

        if len(request.requests) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Batch size exceeds maximum limit of 100 requests",
            )

        # Get enhanced synthesis service
        synthesis_service = await get_enhanced_synthesis_service()

        # Convert API requests to service requests
        service_requests = []
        for api_req in request.requests:
            service_req = EnhancedSynthesisRequest(
                synthesis_goal=api_req.synthesis_goal,
                constitutional_principles=[
                    {
                        "description": p.description,
                        "type": p.type,
                        "category": p.category,
                        "weight": p.weight,
                    }
                    for p in api_req.constitutional_principles
                ],
                constraints=api_req.constraints,
                context_data=api_req.context_data or {},
                target_format=api_req.target_format,
                policy_type=api_req.policy_type,
                validation_level=ValidationLevel(api_req.validation_level),
                enable_opa_validation=api_req.enable_opa_validation,
                enable_conflict_detection=api_req.enable_conflict_detection,
                enable_compliance_checking=api_req.enable_compliance_checking,
                enable_constitutional_validation=api_req.enable_constitutional_validation,
                enable_parallel_validation=request.enable_parallel_processing,
                max_validation_latency_ms=api_req.max_validation_latency_ms,
                enable_wina_optimization=api_req.enable_wina_optimization,
                enable_alphaevolve_synthesis=api_req.enable_alphaevolve_synthesis,
                enable_langgraph_workflow=api_req.enable_langgraph_workflow,
            )
            service_requests.append(service_req)

        # Execute batch synthesis
        synthesis_responses = await synthesis_service.batch_synthesize(service_requests)

        # Convert service responses to API responses
        api_responses = []
        for synthesis_response in synthesis_responses:
            if isinstance(synthesis_response, Exception):
                # Handle exceptions in batch processing
                api_response = EnhancedSynthesisResponseAPI(
                    synthesis_id=f"error_{len(api_responses)}",
                    synthesis_time_ms=0.0,
                    synthesized_policy="",
                    policy_metadata={},
                    validation_result=None,
                    is_valid=False,
                    validation_score=0.0,
                    synthesis_latency_ms=0.0,
                    validation_latency_ms=0.0,
                    total_latency_ms=0.0,
                    wina_metadata=None,
                    alphaevolve_metadata=None,
                    langgraph_metadata=None,
                    errors=[str(synthesis_response)],
                    warnings=[],
                    recommendations=["Fix synthesis errors and retry"],
                )
            else:
                # Convert validation response
                validation_result = None
                if synthesis_response.validation_response:
                    validation_result = ValidationResultAPI(
                        is_valid=synthesis_response.validation_response.is_valid,
                        overall_score=synthesis_response.validation_response.overall_score,
                        validation_time_ms=synthesis_response.validation_response.validation_time_ms,
                        errors=synthesis_response.validation_response.errors,
                        warnings=synthesis_response.validation_response.warnings,
                        recommendations=synthesis_response.validation_response.recommendations,
                        decision_latency_ms=synthesis_response.validation_response.decision_latency_ms,
                        cache_hit=synthesis_response.validation_response.cache_hit,
                    )

                api_response = EnhancedSynthesisResponseAPI(
                    synthesis_id=synthesis_response.synthesis_id,
                    synthesis_time_ms=synthesis_response.synthesis_time_ms,
                    synthesized_policy=synthesis_response.synthesized_policy,
                    policy_metadata=synthesis_response.policy_metadata,
                    validation_result=validation_result,
                    is_valid=synthesis_response.is_valid,
                    validation_score=synthesis_response.validation_score,
                    synthesis_latency_ms=synthesis_response.synthesis_latency_ms,
                    validation_latency_ms=synthesis_response.validation_latency_ms,
                    total_latency_ms=synthesis_response.total_latency_ms,
                    wina_metadata=(
                        synthesis_response.wina_result.__dict__
                        if synthesis_response.wina_result
                        else None
                    ),
                    alphaevolve_metadata=synthesis_response.alphaevolve_metadata,
                    langgraph_metadata=synthesis_response.langgraph_metadata,
                    errors=synthesis_response.errors,
                    warnings=synthesis_response.warnings,
                    recommendations=synthesis_response.recommendations,
                )

            api_responses.append(api_response)

        logger.info(f"Batch synthesis completed: {len(api_responses)} policies")
        return api_responses

    except Exception as e:
        logger.error(f"Batch synthesis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch synthesis failed: {str(e)}",
        )


@router.get("/health", response_model=HealthCheckResponseAPI)
async def health_check() -> HealthCheckResponseAPI:
    """
    Perform health check on enhanced governance synthesis service.

    Returns status of all components including:
    - OPA integration
    - Policy validation engine
    - WINA synthesizer
    - AlphaEvolve bridge
    - Performance metrics
    """
    try:
        synthesis_service = await get_enhanced_synthesis_service()
        health_status = await synthesis_service.health_check()

        return HealthCheckResponseAPI(
            service=health_status["service"],
            status=health_status["status"],
            components=health_status["components"],
            service_metrics=health_status["service_metrics"],
            timestamp=health_status["timestamp"],
        )

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Health check failed: {str(e)}",
        )


@validate_policy_input
@router.post("/multi-model-consensus", response_model=dict[str, Any])
async def multi_model_consensus_synthesis(
    request: EnhancedSynthesisRequestAPI, background_tasks: BackgroundTasks
) -> dict[str, Any]:
    """
    Phase 2 Enhanced Multi-Model Consensus Synthesis with DeepSeek and Qwen Integration.

    This endpoint provides advanced policy synthesis using:
    - DeepSeek Chat v3 and DeepSeek R1 models for constitutional reasoning
    - Qwen3-235B for governance analysis
    - Multi-model consensus with weighted voting
    - Constitutional compliance validation
    - Performance targets: >95% accuracy, <2s response times
    """
    import time
    import uuid

    from ..core.phase_a3_multi_model_consensus import (
        ConsensusStrategy,
        PhaseA3MultiModelConsensusEngine,
    )
    from services.shared.security_validation import (
        validate_governance_input,
        validate_policy_input,
        validate_user_input,
    )

    synthesis_id = str(uuid.uuid4())[:8]
    start_time = time.time()

    logger.info(f"Starting Phase 2 multi-model consensus synthesis {synthesis_id}")

    try:
        # Initialize consensus engine with Phase 2 configuration
        consensus_config = {
            "consensus_threshold": 0.95,  # High accuracy target
            "timeout_seconds": 2.0,  # <2s response time target
            "enable_red_teaming": True,
            "enable_constitutional_fidelity": True,
        }

        consensus_engine = PhaseA3MultiModelConsensusEngine(config=consensus_config)
        await consensus_engine.initialize()

        # Construct synthesis prompt
        prompt_parts = [
            f"CONSTITUTIONAL POLICY SYNTHESIS: {request.synthesis_goal}",
            "",
            "CONSTITUTIONAL PRINCIPLES:",
        ]

        for i, principle in enumerate(request.constitutional_principles, 1):
            prompt_parts.append(f"{i}. {principle.description} (Type: {principle.type})")

        if request.constraints:
            prompt_parts.extend(["", "CONSTRAINTS:"])
            for i, constraint in enumerate(request.constraints, 1):
                prompt_parts.append(f"{i}. {constraint}")

        prompt_parts.extend(
            [
                "",
                "REQUIREMENTS:",
                "- Ensure full constitutional compliance",
                "- Provide actionable policy recommendations",
                "- Consider democratic governance principles",
                "- Include implementation guidance",
                "",
                "Provide a comprehensive policy synthesis addressing the goal while maintaining constitutional integrity.",
            ]
        )

        synthesis_prompt = "\n".join(prompt_parts)

        # Prepare context for consensus
        synthesis_context = {
            "goal": request.synthesis_goal,
            "principles": [p.description for p in request.constitutional_principles],
            "constraints": request.constraints or [],
            "context": request.context_data or {},
            "synthesis_id": synthesis_id,
        }

        # Execute multi-model consensus
        consensus_result = await consensus_engine.get_consensus(
            prompt=synthesis_prompt,
            context=synthesis_context,
            strategy=ConsensusStrategy.WEIGHTED_AVERAGE,
            require_constitutional_compliance=True,
            enable_red_teaming=True,
            enable_constitutional_fidelity=True,
        )

        # Calculate performance metrics
        synthesis_time = (time.time() - start_time) * 1000

        # Extract participating models
        participating_models = [
            {
                "model_id": response.model_id,
                "provider": response.provider,
                "confidence": response.confidence_score,
                "constitutional_compliance": response.constitutional_compliance,
                "response_time_ms": response.response_time_ms,
                "error": response.error,
            }
            for response in consensus_result.model_responses
        ]

        # Calculate accuracy based on consensus metrics
        accuracy_achieved = (
            consensus_result.overall_confidence * 0.6
            + consensus_result.constitutional_compliance * 0.4
        )

        # Prepare comprehensive response
        response_data = {
            "synthesis_id": synthesis_id,
            "synthesized_policy": consensus_result.consensus_content,
            "consensus_metrics": {
                "strategy_used": consensus_result.consensus_strategy.value,
                "agreement_level": consensus_result.agreement_level.value,
                "overall_confidence": consensus_result.overall_confidence,
                "constitutional_compliance": consensus_result.constitutional_compliance,
                "accuracy_achieved": accuracy_achieved,
            },
            "performance_metrics": {
                "synthesis_time_ms": synthesis_time,
                "target_response_time_ms": 2000,
                "target_accuracy": 0.95,
                "performance_targets_met": {
                    "response_time": synthesis_time < 2000,
                    "accuracy": accuracy_achieved >= 0.95,
                },
            },
            "participating_models": participating_models,
            "quality_assurance": {
                "red_teaming_passed": consensus_result.adversarial_validation_passed,
                "constitutional_fidelity_score": (
                    consensus_result.constitutional_fidelity_score.overall_score
                    if consensus_result.constitutional_fidelity_score
                    else None
                ),
                "requires_human_review": consensus_result.requires_human_review,
                "iterative_alignment_applied": consensus_result.iterative_alignment_applied,
            },
            "recommendations": consensus_result.recommendations,
            "timestamp": time.time(),
        }

        # Add warnings if performance targets not met
        warnings = []
        if synthesis_time >= 2000:
            warnings.append(f"Response time {synthesis_time:.0f}ms exceeded 2s target")
        if accuracy_achieved < 0.95:
            warnings.append(f"Accuracy {accuracy_achieved:.2%} below 95% target")
        if not consensus_result.adversarial_validation_passed:
            warnings.append("Adversarial validation detected potential issues")

        response_data["warnings"] = warnings

        logger.info(
            f"Phase 2 consensus synthesis {synthesis_id} completed in {synthesis_time:.2f}ms "
            f"with {accuracy_achieved:.2%} accuracy"
        )

        return response_data

    except Exception as e:
        synthesis_time = (time.time() - start_time) * 1000
        logger.error(
            f"Phase 2 consensus synthesis {synthesis_id} failed after {synthesis_time:.2f}ms: {e}"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Multi-model consensus synthesis failed: {str(e)}",
        )


@router.get("/metrics")
async def get_metrics() -> dict[str, Any]:
    """
    Get performance metrics for enhanced governance synthesis service.

    Returns comprehensive metrics including:
    - Synthesis performance statistics
    - Validation latency metrics
    - OPA integration performance
    - Success/failure rates
    """
    try:
        synthesis_service = await get_enhanced_synthesis_service()
        return synthesis_service.get_metrics()

    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get metrics: {str(e)}",
        )
