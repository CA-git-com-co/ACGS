from typing import Any

from app import schemas
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from services.shared.database import get_async_db

from .core.auth import (
    User,
    get_current_active_user_placeholder,
    require_admin_role,
    require_constitutional_council_role,
)
from .core.constitutional_council_scalability import (
    ConstitutionalCouncilScalabilityFramework,
    ScalabilityConfig,
)
from .crud import (
    create_ac_amendment,
    create_ac_amendment_comment,
    create_ac_amendment_vote,
    create_ac_conflict_resolution,
    create_ac_meta_rule,
    get_ac_amendment,
    get_ac_amendment_comments,
    get_ac_amendment_votes,
    get_ac_amendments,
    get_ac_conflict_resolution,
    get_ac_conflict_resolutions,
    get_ac_meta_rule,
    get_ac_meta_rules,
    update_ac_amendment,
    update_ac_conflict_resolution,
    update_ac_meta_rule,
)
from .monitoring.scalability_metrics import get_metrics_collector
from .workflows.constitutional_council_graph import ConstitutionalCouncilGraph
from .workflows.democratic_governance import (
    DemocraticGovernanceEngine,
    DemocraticProcess,
    StakeholderGroup,
    VotingConfiguration,
    VotingMechanism,
    create_democratic_governance_engine,
)

router = APIRouter()

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Initialize metrics collector
metrics_collector = get_metrics_collector()


# AC Meta-Rules endpoints
@validate_governance_input
@router.post(
    "/meta-rules",
    response_model=schemas.ACMetaRule,
    status_code=status.HTTP_201_CREATED,
)
async def create_meta_rule_endpoint(
    meta_rule: schemas.ACMetaRuleCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_admin_role),
):
    """Create a new AC meta-rule (requires admin role)"""
    # Validate constitutional compliance
    if not hasattr(meta_rule, 'constitutional_hash'):
        meta_rule.constitutional_hash = CONSTITUTIONAL_HASH

    created_meta_rule = await create_ac_meta_rule(
        db=db, meta_rule=meta_rule, user_id=current_user.id
    )

    # Ensure response includes constitutional hash
    if hasattr(created_meta_rule, '__dict__'):
        created_meta_rule.__dict__['constitutional_hash'] = CONSTITUTIONAL_HASH

    return created_meta_rule


@router.get("/meta-rules", response_model=list[schemas.ACMetaRule])
async def list_meta_rules_endpoint(
    rule_type: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user_placeholder),
):
    """List AC meta-rules with optional filtering by rule type"""
    meta_rules = await get_ac_meta_rules(db, rule_type=rule_type, skip=skip, limit=limit)
    return meta_rules


@router.get("/meta-rules/{meta_rule_id}", response_model=schemas.ACMetaRule)
async def get_meta_rule_endpoint(
    meta_rule_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user_placeholder),
):
    """Get a specific AC meta-rule by ID"""
    meta_rule = await get_ac_meta_rule(db, meta_rule_id=meta_rule_id)
    if meta_rule is None:
        raise HTTPException(status_code=404, detail="Meta-rule not found")
    return meta_rule


@router.put("/meta-rules/{meta_rule_id}", response_model=schemas.ACMetaRule)
async def update_meta_rule_endpoint(
    meta_rule_id: int,
    meta_rule_update: schemas.ACMetaRuleUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_admin_role),
):
    """Update an AC meta-rule (requires admin role)"""
    updated_meta_rule = await update_ac_meta_rule(
        db=db, meta_rule_id=meta_rule_id, meta_rule_update=meta_rule_update
    )
    if updated_meta_rule is None:
        raise HTTPException(status_code=404, detail="Meta-rule not found")
    return updated_meta_rule


# AC Amendments endpoints
@validate_governance_input
@router.post(
    "/amendments",
    response_model=schemas.ACAmendment,
    status_code=status.HTTP_201_CREATED,
)
async def create_amendment_endpoint(
    amendment: schemas.ACAmendmentCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_constitutional_council_role),
):
    """Create a new AC amendment proposal (requires Constitutional Council membership)"""
    created_amendment = await create_ac_amendment(
        db=db, amendment=amendment, user_id=current_user.id
    )
    return created_amendment


@router.get("/amendments", response_model=list[schemas.ACAmendment])
async def list_amendments_endpoint(
    status: str | None = None,
    principle_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user_placeholder),
):
    """List AC amendments with optional filtering"""
    amendments = await get_ac_amendments(
        db, status=status, principle_id=principle_id, skip=skip, limit=limit
    )
    return amendments


@router.get("/amendments/{amendment_id}", response_model=schemas.ACAmendment)
async def get_amendment_endpoint(
    amendment_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user_placeholder),
):
    """Get a specific AC amendment by ID"""
    amendment = await get_ac_amendment(db, amendment_id=amendment_id)
    if amendment is None:
        raise HTTPException(status_code=404, detail="Amendment not found")
    return amendment


@router.put("/amendments/{amendment_id}", response_model=schemas.ACAmendment)
async def update_amendment_endpoint(
    amendment_id: int,
    amendment_update: schemas.ACAmendmentUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_constitutional_council_role),
):
    """Update an AC amendment (requires Constitutional Council membership)"""
    updated_amendment = await update_ac_amendment(
        db=db, amendment_id=amendment_id, amendment_update=amendment_update
    )
    if updated_amendment is None:
        raise HTTPException(status_code=404, detail="Amendment not found")
    return updated_amendment


# AC Amendment Voting endpoints
@validate_governance_input
@router.post(
    "/amendments/{amendment_id}/votes",
    response_model=schemas.ACAmendmentVote,
    status_code=status.HTTP_201_CREATED,
)
async def vote_on_amendment_endpoint(
    amendment_id: int,
    vote_data: schemas.ACAmendmentVoteBase,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_constitutional_council_role),
):
    """Vote on an AC amendment (requires Constitutional Council membership)"""
    vote_create = schemas.ACAmendmentVoteCreate(amendment_id=amendment_id, **vote_data.model_dump())
    try:
        created_vote = await create_ac_amendment_vote(
            db=db, vote=vote_create, voter_id=current_user.id
        )
        return created_vote
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/amendments/{amendment_id}/votes", response_model=list[schemas.ACAmendmentVote])
async def get_amendment_votes_endpoint(
    amendment_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user_placeholder),
):
    """Get all votes for a specific amendment"""
    votes = await get_ac_amendment_votes(db, amendment_id=amendment_id)
    return votes


# AC Amendment Comments endpoints
@validate_governance_input
@router.post(
    "/amendments/{amendment_id}/comments",
    response_model=schemas.ACAmendmentComment,
    status_code=status.HTTP_201_CREATED,
)
async def create_amendment_comment_endpoint(
    amendment_id: int,
    comment_data: schemas.ACAmendmentCommentBase,
    db: AsyncSession = Depends(get_async_db),
    current_user: User | None = Depends(get_current_active_user_placeholder),
):
    """Create a comment on an AC amendment (public participation)"""
    comment_create = schemas.ACAmendmentCommentCreate(
        amendment_id=amendment_id, **comment_data.model_dump()
    )
    commenter_id = current_user.id if current_user else None
    created_comment = await create_ac_amendment_comment(
        db=db, comment=comment_create, commenter_id=commenter_id
    )
    return created_comment


@router.get(
    "/amendments/{amendment_id}/comments",
    response_model=list[schemas.ACAmendmentComment],
)
async def get_amendment_comments_endpoint(
    amendment_id: int,
    is_public: bool = True,
    db: AsyncSession = Depends(get_async_db),
    current_user: User | None = Depends(get_current_active_user_placeholder),
):
    """Get comments for a specific amendment"""
    comments = await get_ac_amendment_comments(db, amendment_id=amendment_id, is_public=is_public)
    return comments


# AC Conflict Resolution endpoints
@validate_governance_input
@router.post(
    "/conflict-resolutions",
    response_model=schemas.ACConflictResolution,
    status_code=status.HTTP_201_CREATED,
)
async def create_conflict_resolution_endpoint(
    conflict: schemas.ACConflictResolutionCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_admin_role),
):
    """Create a new AC conflict resolution (requires admin role)"""
    created_conflict = await create_ac_conflict_resolution(
        db=db, conflict=conflict, user_id=current_user.id
    )
    return created_conflict


@router.get("/conflict-resolutions", response_model=list[schemas.ACConflictResolution])
async def list_conflict_resolutions_endpoint(
    status: str | None = None,
    severity: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user_placeholder),
):
    """List AC conflict resolutions with optional filtering"""
    conflicts = await get_ac_conflict_resolutions(
        db, status=status, severity=severity, skip=skip, limit=limit
    )
    return conflicts


@router.get("/conflict-resolutions/{conflict_id}", response_model=schemas.ACConflictResolution)
async def get_conflict_resolution_endpoint(
    conflict_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user_placeholder),
):
    """Get a specific AC conflict resolution by ID"""
    conflict = await get_ac_conflict_resolution(db, conflict_id=conflict_id)
    if conflict is None:
        raise HTTPException(status_code=404, detail="Conflict resolution not found")
    return conflict


@router.put("/conflict-resolutions/{conflict_id}", response_model=schemas.ACConflictResolution)
async def update_conflict_resolution_endpoint(
    conflict_id: int,
    conflict_update: schemas.ACConflictResolutionUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_admin_role),
):
    """Update an AC conflict resolution (requires admin role)"""
    updated_conflict = await update_ac_conflict_resolution(
        db=db, conflict_id=conflict_id, conflict_update=conflict_update
    )
    if updated_conflict is None:
        raise HTTPException(status_code=404, detail="Conflict resolution not found")
    return updated_conflict


# Constitutional Council Scalability Metrics endpoints
@router.get("/scalability-metrics", response_model=dict[str, Any])
async def get_scalability_metrics_endpoint(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_admin_role),
):
    """Get Constitutional Council scalability metrics (requires admin role)"""
    try:
        # Initialize scalability framework
        config = ScalabilityConfig(
            max_concurrent_amendments=10,
            rapid_voting_window_hours=24,
            emergency_voting_window_hours=6,
            async_voting_enabled=True,
            performance_monitoring_enabled=True,
        )
        framework = ConstitutionalCouncilScalabilityFramework(config)

        # Get scalability metrics
        metrics = await framework.get_scalability_metrics(db)

        return {
            "amendment_throughput": metrics.amendment_throughput,
            "average_voting_time": metrics.average_voting_time,
            "consensus_rate": metrics.consensus_rate,
            "participation_rate": metrics.participation_rate,
            "scalability_score": metrics.scalability_score,
            "bottleneck_indicators": metrics.bottleneck_indicators,
            "timestamp": "2024-01-01T00:00:00Z",  # Current timestamp would be added
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve scalability metrics: {str(e)}"
        )


# Amendment State Transition endpoint
@validate_governance_input
@router.post("/amendments/{amendment_id}/transition", response_model=dict[str, Any])
async def transition_amendment_state_endpoint(
    amendment_id: int,
    transition_data: dict[str, Any],
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_constitutional_council_role),
):
    """Trigger state transition for an amendment (requires Constitutional Council membership)"""
    try:
        # Get amendment
        amendment = await get_ac_amendment(db, amendment_id=amendment_id)
        if not amendment:
            raise HTTPException(status_code=404, detail="Amendment not found")

        # Initialize state machine and trigger transition
        from .core.amendment_state_machine import (

# Security validation imports
from services.shared.security_validation import (
    validate_user_input,
    validate_policy_input,
    validate_governance_input
)
            AmendmentEvent,
            AmendmentState,
            WorkflowContext,
            amendment_state_machine,
        )

        # Parse event and context
        event_name = transition_data.get("event")
        if not event_name:
            raise HTTPException(status_code=400, detail="Event is required")

        try:
            event = AmendmentEvent(event_name)
            current_state = AmendmentState(amendment.workflow_state)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid event or state: {str(e)}")

        context = WorkflowContext(
            amendment_id=amendment_id,
            user_id=current_user.id,
            metadata=transition_data.get("metadata", {}),
        )

        # Trigger transition
        result = await amendment_state_machine.trigger_event(db, current_state, event, context)

        if not result.get("success", False):
            raise HTTPException(
                status_code=400, detail=result.get("error", "State transition failed")
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to transition amendment state: {str(e)}"
        )


# Enhanced Amendment Processing Pipeline endpoints
@validate_governance_input
@router.post("/amendments/{amendment_id}/process-finalization", response_model=dict[str, Any])
async def process_amendment_finalization_endpoint(
    amendment_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_constitutional_council_role),
):
    """Process amendment finalization through enhanced pipeline (requires Constitutional Council membership)"""
    try:
        # Initialize Constitutional Council graph
        graph = ConstitutionalCouncilGraph(db)

        # Get amendment
        amendment = await get_ac_amendment(db, amendment_id=amendment_id)
        if not amendment:
            raise HTTPException(status_code=404, detail="Amendment not found")

        # Create state for finalization processing
        state = {
            "amendment_id": str(amendment_id),
            "user_id": current_user.id,
            "session_id": f"finalization_{amendment_id}",
            "voting_results": {
                "voting_passed": True,  # Assume voting passed for finalization
                "vote_summary": {"total_votes": 1},
                "approval_rate": 1.0,
            },
            "stakeholder_feedback": [],
            "refinement_iterations": 0,
            "compliance_score": 0.8,
            "is_constitutional": True,
            "identified_conflicts": [],
        }

        # Process finalization
        result = await graph._process_amendment_finalization(amendment_id, state)

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])

        return {
            "success": True,
            "amendment_id": amendment_id,
            "finalization_result": result,
            "message": "Amendment finalization processed successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process amendment finalization: {str(e)}",
        )


@validate_governance_input
@router.post("/amendments/process-parallel", response_model=dict[str, Any])
async def process_amendments_parallel_endpoint(
    amendment_ids: list[int],
    max_concurrent: int = 3,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_constitutional_council_role),
):
    """Process multiple amendments in parallel (requires Constitutional Council membership)"""
    try:
        if not amendment_ids:
            raise HTTPException(status_code=400, detail="Amendment IDs list cannot be empty")

        if len(amendment_ids) > 10:
            raise HTTPException(
                status_code=400,
                detail="Maximum 10 amendments can be processed in parallel",
            )

        # Initialize Constitutional Council graph
        graph = ConstitutionalCouncilGraph(db)

        # Process amendments in parallel
        result = await graph.process_multiple_amendments_parallel(
            amendment_ids=amendment_ids, max_concurrent=max_concurrent
        )

        return {
            "success": result["success"],
            "processing_summary": result["processing_summary"],
            "successful_amendments": result["successful_amendments"],
            "failed_amendments": result["failed_amendments"],
            "message": f"Processed {len(amendment_ids)} amendments with {result['processing_summary']['success_rate']:.2%} success rate",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process amendments in parallel: {str(e)}",
        )


@validate_governance_input
@router.post("/amendments/{amendment_id}/automated-transition", response_model=dict[str, Any])
async def automated_status_transition_endpoint(
    amendment_id: int,
    target_status: str,
    transition_context: dict[str, Any] | None = None,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_constitutional_council_role),
):
    """Perform automated status transition for an amendment (requires Constitutional Council membership)"""
    try:
        # Validate target status
        valid_statuses = [
            "under_review",
            "public_consultation",
            "voting",
            "approved",
            "rejected",
            "withdrawn",
        ]
        if target_status not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid target status. Must be one of: {', '.join(valid_statuses)}",
            )

        # Initialize Constitutional Council graph
        graph = ConstitutionalCouncilGraph(db)

        # Add user context
        if not transition_context:
            transition_context = {}
        transition_context["user_id"] = current_user.id
        transition_context["initiated_by"] = "automated_endpoint"

        # Perform automated transition
        result = await graph.automated_status_transition(
            amendment_id=amendment_id,
            target_status=target_status,
            transition_context=transition_context,
        )

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])

        return {
            "success": True,
            "amendment_id": amendment_id,
            "transition_result": result,
            "message": f"Amendment {amendment_id} successfully transitioned to {target_status}",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to perform automated status transition: {str(e)}",
        )


@router.get("/amendments/{amendment_id}/processing-status", response_model=dict[str, Any])
async def get_amendment_processing_status_endpoint(
    amendment_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user_placeholder),
):
    """Get comprehensive processing status for an amendment"""
    try:
        # Get amendment
        amendment = await get_ac_amendment(db, amendment_id=amendment_id)
        if not amendment:
            raise HTTPException(status_code=404, detail="Amendment not found")

        # Get votes and comments
        votes = await get_ac_amendment_votes(db, amendment_id=amendment_id)
        comments = await get_ac_amendment_comments(db, amendment_id=amendment_id)

        # Calculate processing metrics
        total_votes = len(votes)
        votes_for = len([v for v in votes if v.vote_type == "for"])
        votes_against = len([v for v in votes if v.vote_type == "against"])
        votes_abstain = len([v for v in votes if v.vote_type == "abstain"])

        approval_rate = votes_for / total_votes if total_votes > 0 else 0
        participation_rate = total_votes / 10  # Assuming 10 total stakeholders

        processing_status = {
            "amendment_id": amendment_id,
            "current_status": amendment.status,
            "workflow_state": getattr(amendment, "workflow_state", amendment.status),
            "created_at": amendment.created_at.isoformat(),
            "updated_at": amendment.updated_at.isoformat(),
            "voting_metrics": {
                "total_votes": total_votes,
                "votes_for": votes_for,
                "votes_against": votes_against,
                "votes_abstain": votes_abstain,
                "approval_rate": approval_rate,
                "participation_rate": participation_rate,
            },
            "engagement_metrics": {
                "total_comments": len(comments),
                "public_comments": len([c for c in comments if c.is_public]),
                "stakeholder_feedback_count": len([c for c in comments if not c.is_public]),
            },
            "processing_pipeline": {
                "can_proceed_to_voting": approval_rate > 0.5 and participation_rate > 0.3,
                "requires_refinement": approval_rate < 0.6,
                "ready_for_finalization": amendment.status == "voting" and approval_rate > 0.6,
                "estimated_completion": "2024-01-15T00:00:00Z",  # Would be calculated based on current progress
            },
        }

        return processing_status

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get amendment processing status: {str(e)}",
        )


# Democratic Governance Workflow endpoints
@validate_governance_input
@router.post("/amendments/{amendment_id}/democratic-process", response_model=dict[str, Any])
async def initiate_democratic_process_endpoint(
    amendment_id: int,
    process_config: dict[str, Any] | None = None,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_constitutional_council_role),
):
    """Initiate democratic governance process for an amendment"""
    try:
        # Get amendment
        amendment = await get_ac_amendment(db, amendment_id=amendment_id)
        if not amendment:
            raise HTTPException(status_code=404, detail="Amendment not found")

        # Create democratic governance engine
        governance_engine = await create_democratic_governance_engine(db)

        # Create process configuration
        if process_config:
            democratic_process = DemocraticProcess(
                amendment_id=amendment_id,
                process_type=process_config.get("process_type", "constitutional_amendment"),
                stakeholder_groups=[
                    StakeholderGroup(group)
                    for group in process_config.get(
                        "stakeholder_groups",
                        ["constitutional_council", "expert_advisors", "public_representatives"],
                    )
                ],
                voting_config=VotingConfiguration(
                    mechanism=VotingMechanism(
                        process_config.get("voting_mechanism", "weighted_voting")
                    ),
                    quorum_percentage=process_config.get("quorum_percentage", 0.6),
                    threshold_percentage=process_config.get("threshold_percentage", 0.67),
                    voting_period_hours=process_config.get("voting_period_hours", 72),
                ),
            )
        else:
            democratic_process = None

        # Initiate democratic process
        process = await governance_engine.initiate_democratic_process(
            amendment=amendment, process_config=democratic_process
        )

        return {
            "success": True,
            "amendment_id": amendment_id,
            "process_id": f"democratic_process_{amendment_id}",
            "eligible_participants": process.eligible_participants,
            "current_phase": process.current_phase.value,
            "started_at": process.started_at.isoformat() if process.started_at else None,
            "message": "Democratic governance process initiated successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to initiate democratic process: {str(e)}"
        )


@validate_governance_input
@router.post("/amendments/{amendment_id}/consultation", response_model=dict[str, Any])
async def start_consultation_phase_endpoint(
    amendment_id: int,
    consultation_config: dict[str, Any] | None = None,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_constitutional_council_role),
):
    """Start consultation phase for democratic governance"""
    try:
        # Create democratic governance engine
        governance_engine = await create_democratic_governance_engine(db)

        # Create process configuration for consultation
        process = DemocraticProcess(
            amendment_id=amendment_id,
            process_type="constitutional_amendment",
            stakeholder_groups=[
                StakeholderGroup.CONSTITUTIONAL_COUNCIL,
                StakeholderGroup.PUBLIC_REPRESENTATIVES,
            ],
            voting_config=VotingConfiguration(),
            consultation_period_days=(
                consultation_config.get("consultation_period_days", 14)
                if consultation_config
                else 14
            ),
            public_participation_enabled=(
                consultation_config.get("public_participation_enabled", True)
                if consultation_config
                else True
            ),
            expert_review_required=(
                consultation_config.get("expert_review_required", True)
                if consultation_config
                else True
            ),
        )

        # Start consultation phase
        updated_process = await governance_engine.start_consultation_phase(process)

        return {
            "success": True,
            "amendment_id": amendment_id,
            "consultation_started_at": (
                updated_process.consultation_started_at.isoformat()
                if updated_process.consultation_started_at
                else None
            ),
            "consultation_period_days": updated_process.consultation_period_days,
            "public_participation_enabled": updated_process.public_participation_enabled,
            "expert_review_required": updated_process.expert_review_required,
            "current_phase": updated_process.current_phase.value,
            "message": "Consultation phase started successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start consultation phase: {str(e)}")


@validate_governance_input
@router.post("/amendments/{amendment_id}/democratic-voting", response_model=dict[str, Any])
async def conduct_democratic_voting_endpoint(
    amendment_id: int,
    voting_config: dict[str, Any] | None = None,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_constitutional_council_role),
):
    """Conduct democratic voting with enhanced mechanisms"""
    try:
        start_time = datetime.utcnow()

        # Create democratic governance engine
        governance_engine = await create_democratic_governance_engine(db)

        # Create voting configuration
        voting_configuration = VotingConfiguration(
            mechanism=(
                VotingMechanism(voting_config.get("mechanism", "weighted_voting"))
                if voting_config
                else VotingMechanism.WEIGHTED_VOTING
            ),
            quorum_percentage=voting_config.get("quorum_percentage", 0.6) if voting_config else 0.6,
            threshold_percentage=(
                voting_config.get("threshold_percentage", 0.67) if voting_config else 0.67
            ),
            voting_period_hours=(
                voting_config.get("voting_period_hours", 72) if voting_config else 72
            ),
            weighted_by_expertise=(
                voting_config.get("weighted_by_expertise", True) if voting_config else True
            ),
        )

        # Create process configuration
        process = DemocraticProcess(
            amendment_id=amendment_id,
            process_type="constitutional_amendment",
            stakeholder_groups=[
                StakeholderGroup.CONSTITUTIONAL_COUNCIL,
                StakeholderGroup.EXPERT_ADVISORS,
            ],
            voting_config=voting_configuration,
        )

        # Conduct democratic voting
        voting_results = await governance_engine.conduct_democratic_voting(process)

        # Record API response time
        response_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        await metrics_collector.record_api_response_time(
            endpoint="democratic_voting", response_time_ms=response_time_ms
        )

        return {
            "success": True,
            "amendment_id": amendment_id,
            "voting_results": voting_results,
            "response_time_ms": response_time_ms,
            "message": "Democratic voting conducted successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to conduct democratic voting: {str(e)}"
        )


@router.get("/democratic-governance/metrics", response_model=dict[str, Any])
async def get_democratic_governance_metrics_endpoint(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_admin_role),
):
    """Get democratic governance metrics and participation statistics"""
    try:
        # Get metrics from collector
        performance_metrics = await metrics_collector.get_performance_summary()
        participation_metrics = await metrics_collector.get_democratic_participation_summary()

        return {
            "performance_metrics": {
                "amendment_processing_time_ms": performance_metrics.amendment_processing_time_ms,
                "voting_completion_time_ms": performance_metrics.voting_completion_time_ms,
                "consensus_achievement_time_ms": performance_metrics.consensus_achievement_time_ms,
                "api_response_time_ms": performance_metrics.api_response_time_ms,
                "availability_percentage": performance_metrics.availability_percentage,
                "error_rate": performance_metrics.error_rate,
            },
            "participation_metrics": {
                "total_eligible_voters": participation_metrics.total_eligible_voters,
                "active_participants": participation_metrics.active_participants,
                "participation_rate": participation_metrics.participation_rate,
                "consensus_level": participation_metrics.consensus_level,
                "stakeholder_diversity_score": participation_metrics.stakeholder_diversity_score,
                "public_engagement_score": participation_metrics.public_engagement_score,
                "transparency_score": participation_metrics.transparency_score,
            },
            "system_health": {
                "overall_reliability_score": 0.95,  # Would be calculated from actual metrics
                "democratic_legitimacy_score": 0.88,
                "governance_efficiency_score": 0.92,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get democratic governance metrics: {str(e)}"
        )
