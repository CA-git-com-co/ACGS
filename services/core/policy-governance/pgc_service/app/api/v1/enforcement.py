import time
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status  # Added Request

from ... import schemas  # Relative imports for app directory
from ...core.auth import User, require_policy_evaluation_triggerer  # Placeholder auth
from ...core.datalog_engine import datalog_engine  # Global Datalog engine instance
from ...core.limiter import limiter  # Import the limiter
from ...core.opa_client import get_opa_client
from ...core.policy_manager import policy_manager  # Global policy manager instance
from ...core.realtime_compliance_engine import (
    ActionContext,
    ActionType,
    ComplianceLevel,
    EnforcementAction,
    RealTimeComplianceEngine,
    get_compliance_engine,
)
from ...core.wina_enforcement_optimizer import (
    EnforcementContext,
    get_wina_enforcement_optimizer,
)
from ...core.wina_policy_compiler import WINAPolicyCompiler

router = APIRouter()


@validate_policy_input
@router.post(
    "/evaluate",
    response_model=schemas.PolicyQueryResponse,
    status_code=status.HTTP_200_OK,
)
@limiter.limit("30/minute")  # Apply rate limit
async def evaluate_policy_query(
    request: Request,  # Added Request for limiter (must be named 'request')
    policy_query_payload: schemas.PolicyQueryRequest,  # Renamed original 'request'
    current_user: User = Depends(require_policy_evaluation_triggerer),  # Protect this endpoint
):
    """
    Evaluates a policy query against the currently active Datalog policies.
    """
    # 1. Ensure policies are loaded (PolicyManager handles caching and refreshing)
    # The policy_manager already loads rules into the datalog_engine when refreshed.
    # We might force a refresh if needed, or rely on its internal schedule.
    # For an evaluation endpoint, typically we want the most up-to-date rules,
    # but frequent forced refreshes on every call could be inefficient.
    # For now, let's ensure rules are loaded once before evaluation if not already.
    # The current_user is now available in request.scope['current_user'] for the limiter
    if not policy_manager._last_refresh_time:  # Check if initial load has happened
        print("PGC Endpoint: Initial policy load triggered by first evaluation request.")
        await policy_manager.get_active_rules(force_refresh=True)

    active_rules_content = policy_manager.get_active_rule_strings()
    if not active_rules_content:
        # This might happen if Integrity Service has no verified rules or failed to load
        return schemas.PolicyQueryResponse(
            decision="error",
            reason="No active policies loaded or available for evaluation.",
            error_message="Policy set is empty or could not be loaded.",
        )

    # 2. Prepare Datalog engine: Load rules (done by PolicyManager) and add facts from context
    # Datalog engine rules are managed by PolicyManager.
    # We need to clear any facts from previous queries and add current context facts.
    datalog_engine.clear_rules_and_facts()  # Clear previous facts (rules are reloaded by PolicyManager)

    # Reload rules to ensure the engine instance for this request is clean and has the latest rules
    # (PolicyManager's load_rules clears before loading)
    datalog_engine.load_rules(active_rules_content)

    context_facts = datalog_engine.build_facts_from_context(
        policy_query_payload.context.model_dump()
    )
    datalog_engine.add_facts(context_facts)

    # --- Placeholder for PETs/TEEs ---
    # Example: If context indicates a need for PET/TEE processing before evaluation
    # This is highly conceptual and depends on specific policy requirements.
    # if policy_query_payload.context.user.get("requires_pet_processing"):
    #     pet_input = schemas.PETContextInput(data=policy_query_payload.context.user, transformation="differential_privacy")
    #     pet_output = await apply_pet_transformation(pet_input)
    #     if pet_output.status == "success":
    #          # Update context_facts with processed data or add new facts
    #          # e.g., datalog_engine.add_facts([f"+processed_user_attribute('some_attr', '{pet_output.processed_data}')"])
    #          pass
    #     else:
    #         return schemas.PolicyQueryResponse(decision="error", reason="PET processing failed.", error_message=str(pet_output.processed_data))

    # if policy_query_payload.context.action.get("requires_tee_execution"):
    #     tee_input = schemas.TEEContextInput(data=policy_query_payload.context.action, code_to_execute="some_sensitive_check")
    #     tee_output = await execute_in_mock_tee(tee_input)
    #     if tee_output.status == "success" and tee_output.result.get("decision") == "permit_tee":
    #         # Add facts based on TEE outcome
    #         # e.g., datalog_engine.add_facts(["+tee_approved_action(policy_query_payload.context.action.type)"])
    #         pass
    #     else:
    #         return schemas.PolicyQueryResponse(decision="deny", reason=f"TEE execution denied or failed. Details: {tee_output.result}", error_message=str(tee_output.status))

    # 3. Formulate and execute the Datalog query
    # The query needs to be constructed based on the request context.
    # Example: Check for a predicate like 'allow(User, Action, Resource)'.
    # For simplicity, let's assume a generic 'allow' predicate that takes context IDs.
    # A more robust system would derive the query target from the request or policy structure.

    user_id = policy_query_payload.context.user.get(
        "id", "_"
    )  # Use actual ID or wildcard if not present
    resource_id = policy_query_payload.context.resource.get("id", "_")
    action_type = policy_query_payload.context.action.get("type", "_")

    # SECURITY: Enhanced input validation and safe query construction
    # Prevent injection attacks with comprehensive validation and parameterized queries
    import re
    from typing import Dict, Any

# Security validation imports
from services.shared.security_validation import (
    validate_user_input,
    validate_policy_input,
    validate_governance_input
)

    def validate_and_sanitize_datalog_input(value: str, field_name: str, max_length: int = 50) -> str:
        """
        Validate and sanitize input for Datalog queries with enhanced security.

        Args:
            value: Input value to validate
            field_name: Name of the field for error reporting
            max_length: Maximum allowed length

        Returns:
            Sanitized value

        Raises:
            HTTPException: If validation fails
        """
        if not value or not isinstance(value, str):
            raise HTTPException(status_code=400, detail=f"Invalid {field_name}: must be non-empty string")

        # Trim whitespace first
        value = value.strip()

        # Check if empty after trimming
        if not value:
            raise HTTPException(status_code=400, detail=f"Invalid {field_name}: must be non-empty string")

        # Length check
        if len(value) > max_length:
            raise HTTPException(status_code=400, detail=f"Invalid {field_name}: exceeds maximum length of {max_length}")

        # Enhanced pattern validation - only allow safe characters
        # Alphanumeric, underscores, hyphens, and dots for resource IDs
        safe_pattern = r"^[a-zA-Z0-9_.-]+$"
        if not re.match(safe_pattern, value):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid {field_name} format: only alphanumeric characters, underscores, hyphens, and dots allowed"
            )

        # Additional security: check for potential Datalog injection patterns
        dangerous_patterns = [
            r"['\"].*['\"]",  # Nested quotes
            r"[();,]",        # Datalog syntax characters
            r"\s*(and|or|not|:-|<=)\s*",  # Datalog operators
            r"[\\]",          # Escape characters
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid {field_name}: contains potentially dangerous characters"
                )

        return value

    def build_safe_datalog_query(user_id: str, action_type: str, resource_id: str) -> str:
        """
        Build a safe Datalog query using validated inputs.

        Args:
            user_id: Validated user identifier
            action_type: Validated action type
            resource_id: Validated resource identifier

        Returns:
            Safe Datalog query string
        """
        # Use a predefined query template to prevent injection
        # This ensures the query structure cannot be modified by user input
        query_template = "allow('{}', '{}', '{}')"

        # Double-check inputs one more time before query construction
        safe_user_id = validate_and_sanitize_datalog_input(user_id, "user_id")
        safe_action_type = validate_and_sanitize_datalog_input(action_type, "action_type")
        safe_resource_id = validate_and_sanitize_datalog_input(resource_id, "resource_id")

        # Construct query with validated inputs
        return query_template.format(safe_user_id, safe_action_type, safe_resource_id)

    # Apply enhanced validation to all inputs
    try:
        validated_user_id = validate_and_sanitize_datalog_input(user_id, "user_id")
        validated_action_type = validate_and_sanitize_datalog_input(action_type, "action_type")
        validated_resource_id = validate_and_sanitize_datalog_input(resource_id, "resource_id")

        # Build safe query using validated inputs
        target_query = build_safe_datalog_query(validated_user_id, validated_action_type, validated_resource_id)

    except HTTPException as e:
        # Log security violation attempt
        print(f"SECURITY ALERT: Datalog injection attempt blocked - {e.detail}")
        print(f"Attempted inputs - user_id: {user_id}, action_type: {action_type}, resource_id: {resource_id}")
        raise e

    print(f"PGC Endpoint: Executing Datalog query: {target_query}")
    query_results = datalog_engine.query(target_query)

    # 4. Interpret results and form response
    decision = "deny"  # Default to deny
    reason = "No specific policy grants permission for the given context."
    matching_rules_info = None  # Future: trace which rules fired

    if query_results:  # If the query returns any results (e.g., [()] for a ground query)
        decision = "permit"
        reason = f"Action '{action_type}' on resource '{resource_id}' by user '{user_id}' is permitted by policy."
        # In a real system with rule tracing, identify matching rules here.
        # matching_rules_info = [{"id": "rule_xyz", "content": "allow(...)"}]

    # Clear facts for the next request (rules are managed by PolicyManager's refresh cycle)
    # datalog_engine.clear_rules_and_facts() # Reconsidering this: facts should be cleared at start of next request.
    # Rules are cleared/reloaded by PolicyManager.

    return schemas.PolicyQueryResponse(
        decision=decision, reason=reason, matching_rules=matching_rules_info
    )


@validate_policy_input
@router.post(
    "/evaluate-wina",
    response_model=schemas.PolicyQueryResponse,
    status_code=status.HTTP_200_OK,
)
@limiter.limit("30/minute")
async def evaluate_policy_query_with_wina(
    request: Request,
    policy_query_payload: schemas.PolicyQueryRequest,
    current_user: User = Depends(require_policy_evaluation_triggerer),
):
    """
    Evaluates a policy query using WINA-optimized enforcement for enhanced performance.

    This endpoint leverages WINA (Weight Informed Neuron Activation) optimization
    to provide more efficient policy enforcement while maintaining constitutional compliance.
    """
    try:
        # Get WINA enforcement optimizer
        wina_optimizer = await get_wina_enforcement_optimizer()

        # Initialize WINA components if not already done
        if not wina_optimizer.opa_client:
            opa_client = await get_opa_client()
            wina_policy_compiler = WINAPolicyCompiler(enable_wina=True)
            await wina_optimizer.initialize(opa_client, wina_policy_compiler)

        # Get active policies
        active_rules = await policy_manager.get_active_rules()

        # Create enforcement context
        context = EnforcementContext(
            user_id=policy_query_payload.context.user.get("id", "unknown"),
            action_type=policy_query_payload.context.action.get("type", "unknown"),
            resource_id=policy_query_payload.context.resource.get("id", "unknown"),
            environment_factors=policy_query_payload.context.environment or {},
            priority_level=policy_query_payload.context.get("priority", "normal"),
            constitutional_requirements=policy_query_payload.context.get(
                "constitutional_requirements", []
            ),
            performance_constraints=policy_query_payload.context.get("performance_constraints", {}),
        )

        # Perform WINA-optimized enforcement
        wina_result = await wina_optimizer.optimize_enforcement(
            context=context,
            policies=active_rules,
            optimization_hints=policy_query_payload.context.get("optimization_hints"),
        )

        # Convert WINA result to standard response format
        matching_rules_info = None
        if wina_result.matching_rules:
            matching_rules_info = [
                {
                    "id": f"rule_{i}",
                    "content": str(rule.get("node", {})),
                    "location": rule.get("location", {}),
                }
                for i, rule in enumerate(wina_result.matching_rules)
            ]

        # Add WINA-specific information to the reason
        enhanced_reason = wina_result.reason
        if wina_result.optimization_applied:
            enhanced_reason += (
                f" (WINA-optimized: {wina_result.enforcement_metrics.strategy_used.value})"
            )
        if wina_result.constitutional_compliance:
            enhanced_reason += " [Constitutional compliance verified]"

        return schemas.PolicyQueryResponse(
            decision=wina_result.decision,
            reason=enhanced_reason,
            matching_rules=matching_rules_info,
            # Add WINA-specific metadata if the schema supports it
            metadata=(
                {
                    "wina_optimization_applied": wina_result.optimization_applied,
                    "enforcement_time_ms": wina_result.enforcement_metrics.enforcement_time_ms,
                    "strategy_used": wina_result.enforcement_metrics.strategy_used.value,
                    "constitutional_compliance": wina_result.constitutional_compliance,
                    "confidence_score": wina_result.confidence_score,
                    "performance_improvement": wina_result.enforcement_metrics.performance_improvement,
                    "wina_insights": wina_result.wina_insights,
                }
                if hasattr(schemas.PolicyQueryResponse, "metadata")
                else None
            ),
        )

    except Exception as e:
        # Fallback to standard enforcement if WINA fails
        print(f"WINA enforcement failed, falling back to standard: {e}")

        # Fallback to original implementation
        await policy_manager.get_active_rules()

        user_id = policy_query_payload.context.user.get("id", "_")
        resource_id = policy_query_payload.context.resource.get("id", "_")
        action_type = policy_query_payload.context.action.get("type", "_")

        target_query = f"allow('{user_id}', '{action_type}', '{resource_id}')"
        query_results = datalog_engine.query(target_query)

        decision = "permit" if query_results else "deny"
        reason = f"Action '{action_type}' on resource '{resource_id}' by user '{user_id}' is {'permitted' if query_results else 'denied'} by policy (fallback enforcement)"

        return schemas.PolicyQueryResponse(decision=decision, reason=reason, matching_rules=None)


@router.get("/wina-performance", status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def get_wina_performance_metrics(
    request: Request, current_user: User = Depends(require_policy_evaluation_triggerer)
):
    """
    Get WINA enforcement performance metrics and statistics.

    Returns comprehensive performance data including enforcement times,
    strategy distribution, constitutional compliance rates, and optimization effectiveness.
    """
    try:
        # Get WINA enforcement optimizer
        wina_optimizer = await get_wina_enforcement_optimizer()

        # Get performance summary
        performance_summary = wina_optimizer.get_performance_summary()

        return {
            "status": "success",
            "wina_performance_metrics": performance_summary,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve WINA performance metrics: {str(e)}",
        )


@validate_policy_input
@router.post("/realtime-compliance", status_code=status.HTTP_200_OK)
@limiter.limit("100/minute")  # Higher rate limit for real-time operations
async def realtime_compliance_check(
    request: Request,
    compliance_request: dict,
    current_user: User = Depends(require_policy_evaluation_triggerer),
    compliance_engine: RealTimeComplianceEngine = Depends(get_compliance_engine),
):
    """
    Phase 2 Enhanced Real-Time Compliance Checking with <200ms validation latency.

    This endpoint provides ultra-fast compliance validation with:
    - Action interception and validation
    - Rule evaluation engine
    - Comprehensive audit logging
    - Performance optimization targeting <200ms latency
    - Constitutional compliance enforcement
    """
    start_time = time.time()

    try:
        # Extract action details from request
        action_type_str = compliance_request.get("action_type", "user_action")
        action_type = (
            ActionType(action_type_str)
            if action_type_str in [e.value for e in ActionType]
            else ActionType.USER_ACTION
        )

        user_id = compliance_request.get(
            "user_id", current_user.id if hasattr(current_user, "id") else "unknown"
        )
        resource_id = compliance_request.get("resource_id", "unknown")
        action_data = compliance_request.get("action_data", {})

        # Determine compliance level based on action criticality
        compliance_level = ComplianceLevel.STANDARD
        if action_type in [
            ActionType.CONSTITUTIONAL_AMENDMENT,
            ActionType.POLICY_CREATION,
        ]:
            compliance_level = ComplianceLevel.THOROUGH
        elif compliance_request.get("fast_mode", False):
            compliance_level = ComplianceLevel.FAST

        # Create action context
        context = ActionContext(
            action_id=f"rt-{int(time.time() * 1000)}",
            action_type=action_type,
            user_id=user_id,
            resource_id=resource_id,
            action_data=action_data,
            environment=compliance_request.get("environment", {}),
            required_compliance_level=compliance_level,
            constitutional_principles=compliance_request.get("constitutional_principles", []),
        )

        # Perform real-time compliance validation
        compliance_result = await compliance_engine.validate_action(context)

        # Calculate total response time
        total_time_ms = (time.time() - start_time) * 1000

        # Prepare comprehensive response
        response_data = {
            "action_id": compliance_result.action_id,
            "enforcement_decision": compliance_result.enforcement_action.value,
            "compliant": compliance_result.compliant,
            "confidence_score": compliance_result.confidence_score,
            # Performance metrics
            "performance": {
                "total_response_time_ms": total_time_ms,
                "validation_time_ms": compliance_result.validation_time_ms,
                "target_latency_ms": 200,
                "performance_target_met": total_time_ms < 200,
                "rule_evaluations": compliance_result.rule_evaluations,
                "cache_hits": compliance_result.cache_hits,
            },
            # Compliance details
            "compliance": {
                "compliance_score": compliance_result.compliance_score,
                "compliance_level": compliance_level.value,
                "violations": compliance_result.violations,
                "warnings": compliance_result.warnings,
                "recommendations": compliance_result.recommendations,
            },
            # Audit information
            "audit": {
                "rules_applied": compliance_result.rules_applied,
                "constitutional_analysis": compliance_result.constitutional_analysis,
                "audit_trail_entries": len(compliance_result.audit_trail),
                "constitutional_hash": "cdd01ef066bc6cf2",
            },
            # Metadata
            "metadata": {
                "action_type": action_type.value,
                "user_id": user_id,
                "resource_id": resource_id,
                "timestamp": compliance_result.timestamp.isoformat(),
                "engine_version": "phase2-realtime-v1.0",
            },
        }

        # Add performance warnings if targets not met
        if total_time_ms >= 200:
            response_data["warnings"] = response_data.get("warnings", [])
            response_data["warnings"].append(
                f"Response time {total_time_ms:.2f}ms exceeded 200ms target"
            )

        logger.info(
            f"Real-time compliance check completed for action {compliance_result.action_id} "
            f"in {total_time_ms:.2f}ms: {compliance_result.enforcement_action.value}"
        )

        return response_data

    except Exception as e:
        total_time_ms = (time.time() - start_time) * 1000
        logger.error(f"Real-time compliance check failed after {total_time_ms:.2f}ms: {e}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Real-time compliance check failed: {str(e)}",
        )


@validate_policy_input
@router.post("/intercept-action", status_code=status.HTTP_200_OK)
@limiter.limit("200/minute")  # High rate limit for action interception
async def intercept_and_validate_action(
    request: Request,
    action_request: dict,
    current_user: User = Depends(require_policy_evaluation_triggerer),
    compliance_engine: RealTimeComplianceEngine = Depends(get_compliance_engine),
):
    """
    Intercept and validate actions in real-time with comprehensive enforcement.

    This endpoint provides action interception capabilities for:
    - Policy creation and modification
    - Governance decisions
    - Constitutional amendments
    - System operations
    - Data access requests
    """
    start_time = time.time()

    try:
        # Extract action details
        action_type_str = action_request.get("action_type", "user_action")
        action_type = (
            ActionType(action_type_str)
            if action_type_str in [e.value for e in ActionType]
            else ActionType.USER_ACTION
        )

        action_data = action_request.get("action_data", {})
        user_id = action_request.get(
            "user_id", current_user.id if hasattr(current_user, "id") else "unknown"
        )
        resource_id = action_request.get("resource_id", "unknown")

        # Perform action interception and validation
        compliance_result = await compliance_engine.intercept_action(
            action_type=action_type,
            action_data=action_data,
            user_id=user_id,
            resource_id=resource_id,
        )

        # Calculate response time
        response_time_ms = (time.time() - start_time) * 1000

        # Determine if action should be allowed to proceed
        action_allowed = compliance_result.enforcement_action in [
            EnforcementAction.ALLOW,
            EnforcementAction.MODIFY,
            EnforcementAction.AUDIT_ONLY,
        ]

        # Prepare interception response
        response_data = {
            "action_id": compliance_result.action_id,
            "action_allowed": action_allowed,
            "enforcement_action": compliance_result.enforcement_action.value,
            "compliance_result": {
                "compliant": compliance_result.compliant,
                "compliance_score": compliance_result.compliance_score,
                "confidence_score": compliance_result.confidence_score,
                "violations": compliance_result.violations,
                "warnings": compliance_result.warnings,
            },
            "performance_metrics": {
                "response_time_ms": response_time_ms,
                "validation_time_ms": compliance_result.validation_time_ms,
                "target_met": response_time_ms < 200,
            },
            "next_steps": _generate_next_steps(compliance_result),
            "audit_reference": compliance_result.action_id,
            "timestamp": compliance_result.timestamp.isoformat(),
        }

        # Log interception result
        logger.info(
            f"Action interception completed for {action_type.value} "
            f"in {response_time_ms:.2f}ms: {compliance_result.enforcement_action.value}"
        )

        return response_data

    except Exception as e:
        response_time_ms = (time.time() - start_time) * 1000
        logger.error(f"Action interception failed after {response_time_ms:.2f}ms: {e}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Action interception failed: {str(e)}",
        )


@router.get("/compliance-metrics", status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def get_compliance_performance_metrics(
    request: Request,
    current_user: User = Depends(require_policy_evaluation_triggerer),
    compliance_engine: RealTimeComplianceEngine = Depends(get_compliance_engine),
):
    """
    Get comprehensive performance metrics for the real-time compliance engine.

    Returns metrics including:
    - Average validation latency
    - Cache hit rates
    - Enforcement action distribution
    - Violation detection rates
    - Performance target compliance
    """
    try:
        # Get performance metrics from compliance engine
        metrics = compliance_engine.get_performance_metrics()

        # Get recent audit log entries
        recent_audits = compliance_engine.get_audit_log(limit=50)

        # Calculate additional derived metrics
        derived_metrics = {
            "performance_grade": "A" if metrics["latency_compliance"] else "B",
            "efficiency_score": min(100, metrics["cache_hit_rate"] * 100),
            "reliability_score": 95.0,  # Would be calculated from actual uptime data
            "recent_activity": {
                "total_recent_validations": len(recent_audits),
                "recent_violations": len([a for a in recent_audits if a.get("violations", [])]),
                "recent_average_latency": sum(a.get("validation_time_ms", 0) for a in recent_audits)
                / max(len(recent_audits), 1),
            },
        }

        return {
            "status": "success",
            "compliance_engine_metrics": metrics,
            "derived_metrics": derived_metrics,
            "performance_targets": {
                "target_latency_ms": 200,
                "target_cache_hit_rate": 0.8,
                "target_availability": 0.995,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve compliance metrics: {str(e)}",
        )


def _generate_next_steps(compliance_result) -> List[str]:
    """Generate next steps based on compliance result."""

    next_steps = []

    if compliance_result.enforcement_action == EnforcementAction.DENY:
        next_steps.append("Action has been denied due to compliance violations")
        next_steps.append("Review violations and modify action before retrying")

    elif compliance_result.enforcement_action == EnforcementAction.REQUIRE_APPROVAL:
        next_steps.append("Action requires additional approval before proceeding")
        next_steps.append("Submit action for review by authorized personnel")

    elif compliance_result.enforcement_action == EnforcementAction.MODIFY:
        next_steps.append("Action can proceed with modifications")
        next_steps.extend(compliance_result.recommendations)

    elif compliance_result.enforcement_action == EnforcementAction.ESCALATE:
        next_steps.append("Action has been escalated for further review")
        next_steps.append("Wait for escalation resolution before proceeding")

    else:  # ALLOW or AUDIT_ONLY
        next_steps.append("Action is compliant and can proceed")
        if compliance_result.warnings:
            next_steps.append("Consider addressing warnings for optimal compliance")

    return next_steps
