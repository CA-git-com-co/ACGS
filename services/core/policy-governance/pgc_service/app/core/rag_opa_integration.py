"""
RAG-OPA Integration Service

Provides end-to-end integration between RAG-based rule generation and OPA deployment,
enabling seamless policy synthesis from constitutional principles to deployed governance rules.

Constitutional Hash: cdd01ef066bc6cf2

Key Features:
- End-to-end rule generation and deployment pipeline
- Automated validation and quality assurance
- Rollback capabilities for failed deployments
- Performance monitoring and metrics
- Human review workflow integration
"""

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from .opa_bundle_manager import (
    BundleMetadata,
    DeploymentResult,
    OPABundleManager,
    get_bundle_manager,
)
from .rag_integration import RAGIntegrationService, get_rag_integration_service
from .rag_rule_generator import RegoRuleResult

# Constitutional compliance hash for ACGS-2
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


@dataclass
class PolicySynthesisRequest:
    """Request for end-to-end policy synthesis."""

    request_id: str
    query: str
    context: dict[str, Any] = field(default_factory=dict)
    risk_threshold: float = 0.55
    bundle_name: str | None = None
    bundle_version: str | None = None
    auto_deploy: bool = True
    require_human_review: bool = False
    constitutional_hash: str = CONSTITUTIONAL_HASH


@dataclass
class PolicySynthesisResult:
    """Result of end-to-end policy synthesis."""

    request_id: str
    success: bool
    rag_result: RegoRuleResult | None = None
    bundle_metadata: BundleMetadata | None = None
    deployment_result: DeploymentResult | None = None
    human_review_required: bool = False
    processing_time_ms: float = 0.0
    error_message: str | None = None
    constitutional_hash: str = CONSTITUTIONAL_HASH


@dataclass
class HumanReviewRequest:
    """Request for human review of generated rules."""

    review_id: str
    rule_result: RegoRuleResult
    synthesis_request: PolicySynthesisRequest
    created_at: datetime
    reviewer_assigned: str | None = None
    review_status: str = "pending"  # pending, approved, rejected, modified
    review_comments: str | None = None
    modified_rule_content: str | None = None


class HumanReviewManager:
    """Manages human review workflow for low-confidence rules."""

    def __init__(self):
        self.pending_reviews: dict[str, HumanReviewRequest] = {}
        self.review_history: list[HumanReviewRequest] = []
        self.metrics = {
            "total_reviews": 0,
            "approved_reviews": 0,
            "rejected_reviews": 0,
            "modified_reviews": 0,
            "avg_review_time_hours": 0.0,
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

    async def submit_for_review(
        self, rule_result: RegoRuleResult, synthesis_request: PolicySynthesisRequest
    ) -> str:
        """Submit a rule for human review."""
        review_id = f"review-{int(time.time())}-{str(uuid4())[:8]}"

        review_request = HumanReviewRequest(
            review_id=review_id,
            rule_result=rule_result,
            synthesis_request=synthesis_request,
            created_at=datetime.now(timezone.utc),
        )

        self.pending_reviews[review_id] = review_request
        self.metrics["total_reviews"] += 1

        logger.info(
            f"Rule {rule_result.rule_id} submitted for human review: {review_id}"
        )
        return review_id

    async def get_pending_reviews(self) -> list[HumanReviewRequest]:
        """Get all pending review requests."""
        return list(self.pending_reviews.values())

    async def approve_review(
        self, review_id: str, reviewer: str, comments: str = ""
    ) -> bool:
        """Approve a review request."""
        if review_id not in self.pending_reviews:
            return False

        review = self.pending_reviews[review_id]
        review.review_status = "approved"
        review.reviewer_assigned = reviewer
        review.review_comments = comments

        # Move to history
        self.review_history.append(review)
        del self.pending_reviews[review_id]

        self.metrics["approved_reviews"] += 1
        logger.info(f"Review {review_id} approved by {reviewer}")
        return True

    async def reject_review(self, review_id: str, reviewer: str, comments: str) -> bool:
        """Reject a review request."""
        if review_id not in self.pending_reviews:
            return False

        review = self.pending_reviews[review_id]
        review.review_status = "rejected"
        review.reviewer_assigned = reviewer
        review.review_comments = comments

        # Move to history
        self.review_history.append(review)
        del self.pending_reviews[review_id]

        self.metrics["rejected_reviews"] += 1
        logger.info(f"Review {review_id} rejected by {reviewer}")
        return True

    async def modify_and_approve_review(
        self,
        review_id: str,
        reviewer: str,
        modified_rule_content: str,
        comments: str = "",
    ) -> bool:
        """Modify and approve a review request."""
        if review_id not in self.pending_reviews:
            return False

        review = self.pending_reviews[review_id]
        review.review_status = "modified"
        review.reviewer_assigned = reviewer
        review.review_comments = comments
        review.modified_rule_content = modified_rule_content

        # Update the original rule result
        review.rule_result.rule_content = modified_rule_content
        review.rule_result.confidence_score = (
            1.0  # Human-reviewed rules get max confidence
        )
        review.rule_result.requires_human_review = False

        # Move to history
        self.review_history.append(review)
        del self.pending_reviews[review_id]

        self.metrics["modified_reviews"] += 1
        logger.info(f"Review {review_id} modified and approved by {reviewer}")
        return True

    def get_metrics(self) -> dict[str, Any]:
        """Get human review metrics."""
        total_completed = (
            self.metrics["approved_reviews"]
            + self.metrics["rejected_reviews"]
            + self.metrics["modified_reviews"]
        )

        approval_rate = 0.0
        if total_completed > 0:
            approval_rate = (
                self.metrics["approved_reviews"] + self.metrics["modified_reviews"]
            ) / total_completed

        return {
            **self.metrics,
            "pending_reviews": len(self.pending_reviews),
            "completed_reviews": total_completed,
            "approval_rate": approval_rate,
        }


class RAGOPAIntegrationService:
    """
    End-to-end integration service for RAG rule generation and OPA deployment.

    Orchestrates the complete pipeline from natural language queries to deployed
    governance policies with human review workflow integration.
    """

    def __init__(self):
        self.rag_service: RAGIntegrationService | None = None
        self.bundle_manager: OPABundleManager | None = None
        self.human_review_manager = HumanReviewManager()

        self.metrics = {
            "total_synthesis_requests": 0,
            "successful_deployments": 0,
            "failed_deployments": 0,
            "human_reviews_required": 0,
            "avg_end_to_end_time_ms": 0.0,
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

        logger.info("RAG-OPA Integration Service initialized")

    async def initialize(self):
        """Initialize the integration service."""
        try:
            self.rag_service = await get_rag_integration_service()
            self.bundle_manager = await get_bundle_manager()

            logger.info("RAG-OPA Integration Service initialization complete")

        except Exception as e:
            logger.exception(f"Failed to initialize RAG-OPA Integration Service: {e}")
            raise

    async def synthesize_and_deploy_policy(
        self, request: PolicySynthesisRequest
    ) -> PolicySynthesisResult:
        """
        Perform end-to-end policy synthesis and deployment.

        Args:
            request: Policy synthesis request

        Returns:
            PolicySynthesisResult with complete pipeline results
        """
        if not self.rag_service or not self.bundle_manager:
            await self.initialize()

        start_time = time.time()
        self.metrics["total_synthesis_requests"] += 1

        try:
            # Step 1: Generate rule using RAG
            logger.info(f"Starting policy synthesis for request: {request.request_id}")

            rag_result = await self.rag_service.generate_rule_from_query(
                query=request.query,
                context=request.context,
                risk_threshold=request.risk_threshold,
            )

            # Step 2: Check if human review is required
            if (
                rag_result.requires_human_review
                or request.require_human_review
                or rag_result.confidence_score < 0.8
            ):

                self.metrics["human_reviews_required"] += 1

                # Submit for human review
                review_id = await self.human_review_manager.submit_for_review(
                    rag_result, request
                )

                processing_time = (time.time() - start_time) * 1000

                return PolicySynthesisResult(
                    request_id=request.request_id,
                    success=False,  # Pending human review
                    rag_result=rag_result,
                    human_review_required=True,
                    processing_time_ms=processing_time,
                    error_message=f"Human review required. Review ID: {review_id}",
                )

            # Step 3: Compile and validate rule
            metadata, compilation_results = (
                await self.bundle_manager.compile_rag_rules_to_bundle(
                    [rag_result],
                    bundle_name=request.bundle_name,
                    bundle_version=request.bundle_version,
                )
            )

            # Check compilation success
            if not all(r.compiled_successfully for r in compilation_results):
                processing_time = (time.time() - start_time) * 1000
                self.metrics["failed_deployments"] += 1

                return PolicySynthesisResult(
                    request_id=request.request_id,
                    success=False,
                    rag_result=rag_result,
                    bundle_metadata=metadata,
                    processing_time_ms=processing_time,
                    error_message="Rule compilation failed",
                )

            # Step 4: Deploy to OPA (if auto_deploy is enabled)
            deployment_result = None
            if request.auto_deploy:
                rules = [(rag_result.rule_id, rag_result.rule_content)]
                deployment_result = await self.bundle_manager.deploy_bundle_to_opa(
                    metadata, rules, validate_deployment=True
                )

                if deployment_result.success:
                    self.metrics["successful_deployments"] += 1
                    logger.info(f"Policy successfully deployed: {request.request_id}")
                else:
                    self.metrics["failed_deployments"] += 1
                    logger.error(f"Policy deployment failed: {request.request_id}")

            # Step 5: Create final result
            processing_time = (time.time() - start_time) * 1000
            self._update_timing_metrics(processing_time)

            success = deployment_result.success if deployment_result else True

            return PolicySynthesisResult(
                request_id=request.request_id,
                success=success,
                rag_result=rag_result,
                bundle_metadata=metadata,
                deployment_result=deployment_result,
                processing_time_ms=processing_time,
            )

        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            self.metrics["failed_deployments"] += 1

            logger.exception(f"Policy synthesis failed for {request.request_id}: {e}")

            return PolicySynthesisResult(
                request_id=request.request_id,
                success=False,
                processing_time_ms=processing_time,
                error_message=str(e),
            )

    async def process_human_review_approval(
        self, review_id: str
    ) -> PolicySynthesisResult | None:
        """Process an approved human review and continue deployment."""
        pending_reviews = await self.human_review_manager.get_pending_reviews()
        review_request = None

        for review in pending_reviews:
            if review.review_id == review_id:
                review_request = review
                break

        if not review_request:
            logger.error(f"Review request not found: {review_id}")
            return None

        # Continue with deployment using the reviewed rule
        synthesis_request = review_request.synthesis_request

        # Update the synthesis request to skip human review
        synthesis_request.require_human_review = False

        # Re-run synthesis with the approved rule
        return await self.synthesize_and_deploy_policy(synthesis_request)

    def _update_timing_metrics(self, processing_time_ms: float):
        """Update timing metrics."""
        current_avg = self.metrics["avg_end_to_end_time_ms"]
        total_requests = self.metrics["total_synthesis_requests"]

        if total_requests > 0:
            self.metrics["avg_end_to_end_time_ms"] = (
                current_avg * (total_requests - 1) + processing_time_ms
            ) / total_requests
        else:
            self.metrics["avg_end_to_end_time_ms"] = processing_time_ms

    def get_metrics(self) -> dict[str, Any]:
        """Get comprehensive integration metrics."""
        success_rate = 0.0
        total_completed = (
            self.metrics["successful_deployments"] + self.metrics["failed_deployments"]
        )
        if total_completed > 0:
            success_rate = self.metrics["successful_deployments"] / total_completed

        human_review_rate = 0.0
        if self.metrics["total_synthesis_requests"] > 0:
            human_review_rate = (
                self.metrics["human_reviews_required"]
                / self.metrics["total_synthesis_requests"]
            )

        return {
            **self.metrics,
            "deployment_success_rate": success_rate,
            "human_review_rate": human_review_rate,
            "rag_service_metrics": (
                self.rag_service.get_metrics() if self.rag_service else {}
            ),
            "bundle_manager_metrics": (
                self.bundle_manager.get_metrics() if self.bundle_manager else {}
            ),
            "human_review_metrics": self.human_review_manager.get_metrics(),
        }

    async def health_check(self) -> dict[str, Any]:
        """Perform comprehensive health check."""
        health_status = {
            "status": "healthy",
            "integration_service_initialized": (
                self.rag_service is not None and self.bundle_manager is not None
            ),
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "timestamp": time.time(),
        }

        try:
            if self.rag_service:
                rag_health = await self.rag_service.health_check()
                health_status["rag_service_health"] = rag_health

                if rag_health.get("status") != "healthy":
                    health_status["status"] = "degraded"

            if self.bundle_manager:
                bundle_health = await self.bundle_manager.health_check()
                health_status["bundle_manager_health"] = bundle_health

                if bundle_health.get("status") != "healthy":
                    health_status["status"] = "degraded"

            if not health_status["integration_service_initialized"]:
                health_status["status"] = "not_initialized"

        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)
            logger.exception(f"Integration service health check failed: {e}")

        return health_status


# Global instance for service integration
_integration_service: RAGOPAIntegrationService | None = None


async def get_integration_service() -> RAGOPAIntegrationService:
    """Get or create global integration service instance."""
    global _integration_service

    if _integration_service is None:
        _integration_service = RAGOPAIntegrationService()
        await _integration_service.initialize()

    return _integration_service
