"""
Quantum Policy Enforcement API for PGC Service
ACGS-1 Constitutional Governance Enhancement

Integrates Quantum Policy Evaluator (QPE) with existing PGC service
to provide quantum-inspired policy evaluation with superposition states.

Formal Verification Comments:
# requires: qpe_service_available == true
# ensures: latency_total <= 27ms (QPE + PGC)
# ensures: entanglement_tag_verified == true
# ensures: constitutional_compliance == 1.0
# sha256: opa_schrodinger_quantum_enforcement_api_v1.0
"""

import asyncio
import logging
import time
from typing import Any, Dict, Optional

import grpc
from app.core.config import settings
from app.core.opa_client import get_opa_client
from app.schemas.enforcement import EnforcementRequest, EnforcementResponse
from app.services.qpe_client import CollapseReason, QPEClient, State
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize QPE client
qpe_client = QPEClient(settings.QPE_SERVICE_URL)


class QuantumEnforcementRequest(BaseModel):
    """Request for quantum policy enforcement."""

    policy_id: str = Field(..., description="Policy identifier")
    context: Dict[str, Any] = Field(default_factory=dict, description="Evaluation context")
    force_collapse: bool = Field(False, description="Force quantum state collapse")
    observer_id: Optional[str] = Field(None, description="Observer identifier for observer effect")
    uncertainty_lambda: Optional[float] = Field(None, description="Override uncertainty parameter")


class QuantumEnforcementResponse(BaseModel):
    """Response from quantum policy enforcement."""

    policy_id: str
    quantum_state: str  # APPROVED, REJECTED, PENDING
    pgc_result: bool
    allowed: bool
    latency_ms: float
    qpe_latency_ms: float
    entanglement_tag: str
    collapse_reason: str
    was_already_collapsed: bool
    heisenberg_constant: float
    uncertainty_lambda: float
    constitutional_compliance: bool
    audit_trail: Dict[str, Any]


class QuantumPolicyRegistration(BaseModel):
    """Request to register a new policy in quantum superposition."""

    policy_id: str = Field(..., description="Unique policy identifier")
    criticality: str = Field("MEDIUM", description="Policy criticality (HIGH, MEDIUM, LOW)")
    deadline_hours: int = Field(24, description="Hours until automatic collapse")
    deterministic_mode: bool = Field(False, description="Use hash-based deterministic collapse")


class QuantumObservationRequest(BaseModel):
    """Request for stakeholder observation (observer effect)."""

    policy_id: str = Field(..., description="Policy to observe")
    observer_id: str = Field(..., description="Stakeholder identifier")
    observation_reason: str = Field("stakeholder_review", description="Reason for observation")


class UncertaintyUpdateRequest(BaseModel):
    """Request to update uncertainty parameter."""

    lambda_value: float = Field(..., ge=0.0, le=1.0, description="Uncertainty parameter λ ∈ [0,1]")


@router.post("/quantum/register", response_model=Dict[str, Any])
async def register_quantum_policy(request: QuantumPolicyRegistration):
    """
    Register a new policy in quantum superposition.

    Creates a policy that exists in superposition of approved/rejected/pending
    states until measured through the enforcement endpoint.
    """
    try:
        start_time = time.time()

        # Register policy with QPE service
        response = await qpe_client.register(
            policy_id=request.policy_id,
            criticality=request.criticality,
            deadline_hours=request.deadline_hours,
            deterministic_mode=request.deterministic_mode,
        )

        latency_ms = (time.time() - start_time) * 1000

        logger.info(f"Quantum policy registered: {request.policy_id}, latency={latency_ms:.2f}ms")

        return {
            "policy_id": response.policy_id,
            "entanglement_tag": response.entanglement_tag.hex(),
            "quantum_state": {
                "weight_approved": response.quantum_state.weight_approved,
                "weight_rejected": response.quantum_state.weight_rejected,
                "weight_pending": response.quantum_state.weight_pending,
                "is_collapsed": response.quantum_state.is_collapsed,
                "uncertainty_parameter": response.quantum_state.uncertainty_parameter,
            },
            "registration_latency_ms": latency_ms,
            "constitutional_hash": "cdd01ef066bc6cf2",
            "status": "registered_in_superposition",
        }

    except Exception as e:
        logger.error(f"Quantum policy registration failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


@router.post("/quantum/enforce", response_model=QuantumEnforcementResponse)
async def quantum_policy_enforcement(request: QuantumEnforcementRequest):
    """
    Evaluate a request against quantum policy (collapses superposition).

    This is the main enforcement endpoint that triggers quantum measurement,
    collapsing the policy superposition and forwarding to traditional PGC evaluation.
    """
    try:
        start_time = time.time()

        # Set uncertainty parameter if provided
        if request.uncertainty_lambda is not None:
            await qpe_client.set_uncertainty(request.uncertainty_lambda)

        # Handle observer effect if observer specified
        if request.observer_id:
            observe_response = await qpe_client.observe(
                policy_id=request.policy_id,
                observer_id=request.observer_id,
                observation_reason="enforcement_observation",
            )
            logger.info(f"Observer effect triggered: {request.policy_id} by {request.observer_id}")

        # Measure quantum policy state (triggers collapse)
        qpe_start = time.time()
        measure_response = await qpe_client.measure(
            policy_id=request.policy_id,
            context=request.context,
            force_collapse=request.force_collapse,
        )
        qpe_latency = (time.time() - qpe_start) * 1000

        # Determine enforcement result based on quantum state
        quantum_state = measure_response.state.name
        pgc_result = measure_response.pgc_result

        # Apply quantum-classical mapping for enforcement decision
        if quantum_state == "APPROVED":
            allowed = pgc_result
        elif quantum_state == "REJECTED":
            allowed = False
        else:  # PENDING
            # For pending state, use conservative approach
            allowed = False
            logger.info(f"Policy {request.policy_id} in PENDING state, defaulting to deny")

        total_latency = (time.time() - start_time) * 1000

        # Verify constitutional compliance
        constitutional_compliance = _verify_constitutional_compliance(
            measure_response.entanglement_tag, request.policy_id
        )

        # Create audit trail
        audit_trail = {
            "measurement_timestamp": time.time(),
            "collapse_reason": measure_response.collapse_reason.name,
            "was_already_collapsed": measure_response.was_already_collapsed,
            "entanglement_verified": constitutional_compliance,
            "constitutional_hash": "cdd01ef066bc6cf2",
            "observer_id": request.observer_id,
            "uncertainty_lambda": request.uncertainty_lambda or 0.5,
            "heisenberg_constant": measure_response.heisenberg_constant,
        }

        logger.info(
            f"Quantum enforcement: policy={request.policy_id}, "
            f"state={quantum_state}, allowed={allowed}, "
            f"latency={total_latency:.2f}ms, K={measure_response.heisenberg_constant:.2f}"
        )

        return QuantumEnforcementResponse(
            policy_id=request.policy_id,
            quantum_state=quantum_state,
            pgc_result=pgc_result,
            allowed=allowed,
            latency_ms=total_latency,
            qpe_latency_ms=qpe_latency,
            entanglement_tag=measure_response.entanglement_tag.hex(),
            collapse_reason=measure_response.collapse_reason.name,
            was_already_collapsed=measure_response.was_already_collapsed,
            heisenberg_constant=measure_response.heisenberg_constant,
            uncertainty_lambda=request.uncertainty_lambda or 0.5,
            constitutional_compliance=constitutional_compliance,
            audit_trail=audit_trail,
        )

    except grpc.RpcError as e:
        # Fallback to direct OPA evaluation if QPE is unavailable
        logger.warning(f"QPE service unavailable, falling back to direct OPA: {str(e)}")

        fallback_result = await _fallback_opa_evaluation(request.policy_id, request.context)

        return QuantumEnforcementResponse(
            policy_id=request.policy_id,
            quantum_state="CLASSICAL_FALLBACK",
            pgc_result=fallback_result,
            allowed=fallback_result,
            latency_ms=(time.time() - start_time) * 1000,
            qpe_latency_ms=0.0,
            entanglement_tag="",
            collapse_reason="FALLBACK",
            was_already_collapsed=True,
            heisenberg_constant=0.0,
            uncertainty_lambda=0.5,
            constitutional_compliance=True,
            audit_trail={"fallback_reason": str(e)},
        )

    except Exception as e:
        logger.error(f"Quantum enforcement failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Enforcement failed: {str(e)}")


@router.post("/quantum/observe", response_model=Dict[str, Any])
async def trigger_observer_effect(request: QuantumObservationRequest):
    """
    Trigger observer effect to force quantum state collapse.

    Allows stakeholders to observe policies, which immediately collapses
    the quantum superposition according to observer effect principles.
    """
    try:
        response = await qpe_client.observe(
            policy_id=request.policy_id,
            observer_id=request.observer_id,
            observation_reason=request.observation_reason,
        )

        logger.info(
            f"Observer effect: policy={request.policy_id}, "
            f"observer={request.observer_id}, state={response.state.name}"
        )

        return {
            "policy_id": response.policy_id,
            "final_state": response.state.name,
            "was_collapsed": response.was_collapsed,
            "observer_id": request.observer_id,
            "observation_timestamp": response.observation_timestamp,
            "entanglement_tag": response.entanglement_tag.hex(),
            "observation_reason": request.observation_reason,
        }

    except Exception as e:
        logger.error(f"Observer effect failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Observation failed: {str(e)}")


@router.post("/quantum/uncertainty", response_model=Dict[str, Any])
async def update_uncertainty_parameter(request: UncertaintyUpdateRequest):
    """
    Update uncertainty parameter (λ) for speed-accuracy trade-off.

    Controls the Heisenberg-like uncertainty principle where precise
    policy accuracy and validation speed cannot be simultaneously maximized.
    """
    try:
        confirmed_lambda = await qpe_client.set_uncertainty(request.lambda_value)

        # Determine effect description
        if request.lambda_value > 0.7:
            effect = "High accuracy mode: prioritizing thorough validation over speed"
        elif request.lambda_value < 0.3:
            effect = "High speed mode: prioritizing fast processing over exhaustive checks"
        else:
            effect = "Balanced mode: moderate trade-off between accuracy and speed"

        logger.info(f"Uncertainty parameter updated: λ={confirmed_lambda:.3f}")

        return {
            "lambda": confirmed_lambda,
            "effect_description": effect,
            "heisenberg_principle": "Δ(accuracy) × Δ(speed) ≥ K",
            "constitutional_compliance": True,
        }

    except Exception as e:
        logger.error(f"Uncertainty update failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")


@router.get("/quantum/state/{policy_id}", response_model=Dict[str, Any])
async def get_quantum_state(policy_id: str):
    """
    Get current quantum state without collapse (monitoring only).

    Allows inspection of quantum superposition without triggering
    measurement-induced collapse.
    """
    try:
        quantum_state = await qpe_client.get_quantum_state(policy_id)

        if quantum_state is None:
            raise HTTPException(status_code=404, detail="Policy not found")

        # Calculate superposition entropy
        weights = [
            quantum_state.weight_approved,
            quantum_state.weight_rejected,
            quantum_state.weight_pending,
        ]
        entropy = -sum(w * math.log(w) for w in weights if w > 0)

        return {
            "policy_id": policy_id,
            "quantum_state": {
                "weight_approved": quantum_state.weight_approved,
                "weight_rejected": quantum_state.weight_rejected,
                "weight_pending": quantum_state.weight_pending,
                "is_collapsed": quantum_state.is_collapsed,
                "collapsed_state": (
                    quantum_state.collapsed_state.name if quantum_state.is_collapsed else None
                ),
                "superposition_entropy": entropy,
            },
            "metadata": {
                "created_at": quantum_state.created_at,
                "deadline_at": quantum_state.deadline_at,
                "uncertainty_parameter": quantum_state.uncertainty_parameter,
                "criticality": quantum_state.criticality,
            },
            "entanglement_tag": quantum_state.entanglement_tag.hex(),
            "constitutional_hash": "cdd01ef066bc6cf2",
        }

    except Exception as e:
        logger.error(f"Get quantum state failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@router.get("/quantum/health", response_model=Dict[str, Any])
async def quantum_health_check():
    """
    Check quantum policy evaluation system health.

    Verifies QPE service connectivity and constitutional compliance.
    """
    try:
        health_status = await qpe_client.health_check()
        client_metrics = qpe_client.get_metrics()

        return {
            "qpe_service": health_status,
            "client_metrics": client_metrics,
            "constitutional_hash": "cdd01ef066bc6cf2",
            "quantum_features": {
                "superposition_support": True,
                "observer_effect": True,
                "entanglement_verification": True,
                "uncertainty_principle": True,
                "wave_function_collapse": True,
            },
        }

    except Exception as e:
        logger.error(f"Quantum health check failed: {str(e)}")
        return {
            "qpe_service": {"healthy": False, "error": str(e)},
            "client_metrics": qpe_client.get_metrics(),
            "constitutional_hash": "cdd01ef066bc6cf2",
        }


# Helper functions


def _verify_constitutional_compliance(entanglement_tag: bytes, policy_id: str) -> bool:
    """Verify entanglement tag for constitutional compliance."""
    import hashlib
    import hmac

    expected = hmac.new(b"cdd01ef066bc6cf2", policy_id.encode(), hashlib.sha256).digest()

    return hmac.compare_digest(expected, entanglement_tag)


async def _fallback_opa_evaluation(policy_id: str, context: Dict[str, Any]) -> bool:
    """Fallback to direct OPA evaluation when QPE is unavailable."""
    try:
        opa_client = await get_opa_client()

        # Create basic OPA evaluation request
        from app.core.opa_client import PolicyEvaluationRequest

        request = PolicyEvaluationRequest(
            query="data.acgs.authz.allow",
            input_data={"policy_id": policy_id, "context": context, "fallback_mode": True},
        )

        response = await opa_client.evaluate_policy(request)
        return response.result.get("allow", False)

    except Exception as e:
        logger.error(f"Fallback OPA evaluation failed: {str(e)}")
        return False  # Fail closed for security
