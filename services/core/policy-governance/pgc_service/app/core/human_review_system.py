"""
Human Review System for RAG-Generated Rules

Comprehensive human review workflow for low confidence (<0.8) rule generation
with approval mechanisms, feedback loops, and quality assurance processes.

Constitutional Hash: cdd01ef066bc6cf2

Key Features:
- Automated review queue management
- Multi-reviewer approval workflow
- Feedback collection and learning
- Quality metrics and analytics
- Integration with notification systems
- Audit trail for compliance
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4

from .rag_rule_generator import RegoRuleResult

# Constitutional compliance hash for ACGS-2
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


class ReviewStatus(Enum):
    """Status of human review requests."""
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"
    ESCALATED = "escalated"
    EXPIRED = "expired"


class ReviewPriority(Enum):
    """Priority levels for review requests."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ReviewerRole(Enum):
    """Roles for reviewers in the system."""
    JUNIOR_REVIEWER = "junior_reviewer"
    SENIOR_REVIEWER = "senior_reviewer"
    POLICY_EXPERT = "policy_expert"
    SECURITY_EXPERT = "security_expert"
    COMPLIANCE_OFFICER = "compliance_officer"
    ADMIN = "admin"


@dataclass
class ReviewerProfile:
    """Profile information for a reviewer."""
    
    reviewer_id: str
    name: str
    email: str
    role: ReviewerRole
    expertise_areas: List[str] = field(default_factory=list)
    active: bool = True
    max_concurrent_reviews: int = 5
    avg_review_time_hours: float = 24.0
    total_reviews_completed: int = 0
    approval_rate: float = 0.0
    quality_score: float = 0.0


@dataclass
class ReviewFeedback:
    """Feedback provided by reviewers."""
    
    feedback_id: str
    reviewer_id: str
    review_id: str
    feedback_type: str  # "approval", "rejection", "modification", "question"
    comments: str
    suggested_changes: Optional[str] = None
    quality_rating: Optional[int] = None  # 1-5 scale
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    constitutional_hash: str = CONSTITUTIONAL_HASH


@dataclass
class HumanReviewRequest:
    """Comprehensive human review request."""
    
    review_id: str
    rule_result: RegoRuleResult
    original_query: str
    context: Dict[str, Any]
    priority: ReviewPriority
    status: ReviewStatus = ReviewStatus.PENDING
    
    # Assignment and timing
    assigned_reviewers: List[str] = field(default_factory=list)
    required_approvals: int = 1
    current_approvals: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    assigned_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    # Review content
    feedback_items: List[ReviewFeedback] = field(default_factory=list)
    final_decision: Optional[str] = None
    modified_rule_content: Optional[str] = None
    
    # Metadata
    constitutional_hash: str = CONSTITUTIONAL_HASH
    escalation_reason: Optional[str] = None
    quality_metrics: Dict[str, Any] = field(default_factory=dict)


class ReviewAssignmentEngine:
    """Intelligent assignment of reviews to appropriate reviewers."""
    
    def __init__(self):
        self.reviewers: Dict[str, ReviewerProfile] = {}
        self.assignment_history: List[Dict[str, Any]] = []
        self.workload_tracker: Dict[str, int] = {}  # reviewer_id -> current_reviews
    
    def register_reviewer(self, profile: ReviewerProfile):
        """Register a new reviewer in the system."""
        self.reviewers[profile.reviewer_id] = profile
        self.workload_tracker[profile.reviewer_id] = 0
        logger.info(f"Registered reviewer: {profile.name} ({profile.role.value})")
    
    def find_best_reviewers(
        self,
        review_request: HumanReviewRequest,
        required_count: int = 1
    ) -> List[str]:
        """Find the best reviewers for a given request."""
        available_reviewers = []
        
        for reviewer_id, profile in self.reviewers.items():
            if not profile.active:
                continue
            
            current_workload = self.workload_tracker.get(reviewer_id, 0)
            if current_workload >= profile.max_concurrent_reviews:
                continue
            
            # Calculate suitability score
            suitability_score = self._calculate_suitability_score(
                profile, review_request
            )
            
            available_reviewers.append((reviewer_id, suitability_score))
        
        # Sort by suitability score (descending)
        available_reviewers.sort(key=lambda x: x[1], reverse=True)
        
        # Return top reviewers
        selected_reviewers = [r[0] for r in available_reviewers[:required_count]]
        
        # Update workload tracker
        for reviewer_id in selected_reviewers:
            self.workload_tracker[reviewer_id] += 1
        
        return selected_reviewers
    
    def _calculate_suitability_score(
        self,
        profile: ReviewerProfile,
        review_request: HumanReviewRequest
    ) -> float:
        """Calculate how suitable a reviewer is for a specific request."""
        score = 0.0
        
        # Base score by role
        role_scores = {
            ReviewerRole.JUNIOR_REVIEWER: 0.3,
            ReviewerRole.SENIOR_REVIEWER: 0.6,
            ReviewerRole.POLICY_EXPERT: 0.8,
            ReviewerRole.SECURITY_EXPERT: 0.7,
            ReviewerRole.COMPLIANCE_OFFICER: 0.9,
            ReviewerRole.ADMIN: 1.0
        }
        score += role_scores.get(profile.role, 0.5)
        
        # Expertise area matching
        rule_content = review_request.rule_result.rule_content.lower()
        for expertise in profile.expertise_areas:
            if expertise.lower() in rule_content:
                score += 0.2
        
        # Priority matching
        if review_request.priority == ReviewPriority.CRITICAL:
            if profile.role in [ReviewerRole.COMPLIANCE_OFFICER, ReviewerRole.ADMIN]:
                score += 0.3
        
        # Quality and performance factors
        score += min(profile.quality_score * 0.2, 0.2)
        score += min((1.0 - profile.avg_review_time_hours / 48.0) * 0.1, 0.1)
        
        # Workload balancing
        current_workload = self.workload_tracker.get(profile.reviewer_id, 0)
        workload_factor = max(0, 1.0 - (current_workload / profile.max_concurrent_reviews))
        score *= workload_factor
        
        return min(score, 1.0)
    
    def release_reviewer(self, reviewer_id: str):
        """Release a reviewer from their current assignment."""
        if reviewer_id in self.workload_tracker:
            self.workload_tracker[reviewer_id] = max(0, self.workload_tracker[reviewer_id] - 1)


class HumanReviewSystem:
    """Comprehensive human review system for RAG-generated rules."""
    
    def __init__(self, review_timeout_hours: int = 48):
        self.assignment_engine = ReviewAssignmentEngine()
        self.pending_reviews: Dict[str, HumanReviewRequest] = {}
        self.completed_reviews: Dict[str, HumanReviewRequest] = {}
        self.review_timeout_hours = review_timeout_hours
        
        self.metrics = {
            "total_reviews_submitted": 0,
            "total_reviews_completed": 0,
            "total_reviews_approved": 0,
            "total_reviews_rejected": 0,
            "total_reviews_modified": 0,
            "total_reviews_expired": 0,
            "avg_review_time_hours": 0.0,
            "avg_approval_rate": 0.0,
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
        
        # Start background tasks
        self._cleanup_task: Optional[asyncio.Task] = None
        # Note: Background tasks will be started manually to avoid issues in testing
        
        logger.info("Human Review System initialized")
    
    def _start_background_tasks(self):
        """Start background maintenance tasks."""
        self._cleanup_task = asyncio.create_task(self._periodic_cleanup())
    
    async def _periodic_cleanup(self):
        """Periodic cleanup of expired reviews."""
        while True:
            try:
                await self._cleanup_expired_reviews()
                await asyncio.sleep(3600)  # Run every hour
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup task error: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def _cleanup_expired_reviews(self):
        """Clean up expired review requests."""
        current_time = datetime.now(timezone.utc)
        expired_reviews = []
        
        for review_id, review_request in self.pending_reviews.items():
            if review_request.expires_at and current_time > review_request.expires_at:
                expired_reviews.append(review_id)
        
        for review_id in expired_reviews:
            review_request = self.pending_reviews[review_id]
            review_request.status = ReviewStatus.EXPIRED
            
            # Release assigned reviewers
            for reviewer_id in review_request.assigned_reviewers:
                self.assignment_engine.release_reviewer(reviewer_id)
            
            # Move to completed
            self.completed_reviews[review_id] = review_request
            del self.pending_reviews[review_id]
            
            self.metrics["total_reviews_expired"] += 1
            logger.warning(f"Review {review_id} expired")
    
    def register_reviewer(self, profile: ReviewerProfile):
        """Register a reviewer in the system."""
        self.assignment_engine.register_reviewer(profile)
    
    async def submit_for_review(
        self,
        rule_result: RegoRuleResult,
        original_query: str,
        context: Dict[str, Any] = None,
        priority: ReviewPriority = ReviewPriority.MEDIUM,
        required_approvals: int = 1
    ) -> str:
        """Submit a rule for human review."""
        review_id = f"review-{int(time.time())}-{str(uuid4())[:8]}"
        
        # Determine priority based on confidence and context
        if rule_result.confidence_score < 0.5:
            priority = ReviewPriority.HIGH
        elif rule_result.confidence_score < 0.3:
            priority = ReviewPriority.CRITICAL
        
        # Create review request
        review_request = HumanReviewRequest(
            review_id=review_id,
            rule_result=rule_result,
            original_query=original_query,
            context=context or {},
            priority=priority,
            required_approvals=required_approvals,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=self.review_timeout_hours)
        )
        
        # Assign reviewers
        required_reviewers = max(required_approvals, 1)
        assigned_reviewers = self.assignment_engine.find_best_reviewers(
            review_request, required_reviewers
        )
        
        if not assigned_reviewers:
            logger.error(f"No available reviewers for {review_id}")
            raise ValueError("No available reviewers")
        
        review_request.assigned_reviewers = assigned_reviewers
        review_request.assigned_at = datetime.now(timezone.utc)
        review_request.status = ReviewStatus.IN_REVIEW
        
        # Store review
        self.pending_reviews[review_id] = review_request
        self.metrics["total_reviews_submitted"] += 1
        
        logger.info(f"Review {review_id} submitted with priority {priority.value}")
        logger.info(f"Assigned reviewers: {assigned_reviewers}")
        
        return review_id
    
    async def submit_feedback(
        self,
        review_id: str,
        reviewer_id: str,
        feedback_type: str,
        comments: str,
        suggested_changes: Optional[str] = None,
        quality_rating: Optional[int] = None
    ) -> bool:
        """Submit feedback for a review."""
        if review_id not in self.pending_reviews:
            logger.error(f"Review {review_id} not found")
            return False
        
        review_request = self.pending_reviews[review_id]
        
        if reviewer_id not in review_request.assigned_reviewers:
            logger.error(f"Reviewer {reviewer_id} not assigned to {review_id}")
            return False
        
        # Create feedback
        feedback = ReviewFeedback(
            feedback_id=f"feedback-{int(time.time())}-{str(uuid4())[:8]}",
            reviewer_id=reviewer_id,
            review_id=review_id,
            feedback_type=feedback_type,
            comments=comments,
            suggested_changes=suggested_changes,
            quality_rating=quality_rating
        )
        
        review_request.feedback_items.append(feedback)
        
        # Process feedback
        if feedback_type == "approval":
            review_request.current_approvals += 1
            
            if review_request.current_approvals >= review_request.required_approvals:
                await self._complete_review(review_id, ReviewStatus.APPROVED)
        
        elif feedback_type == "rejection":
            await self._complete_review(review_id, ReviewStatus.REJECTED)
        
        elif feedback_type == "modification":
            if suggested_changes:
                review_request.modified_rule_content = suggested_changes
                await self._complete_review(review_id, ReviewStatus.MODIFIED)
        
        logger.info(f"Feedback submitted for {review_id} by {reviewer_id}: {feedback_type}")
        return True
    
    async def _complete_review(self, review_id: str, final_status: ReviewStatus):
        """Complete a review with final status."""
        if review_id not in self.pending_reviews:
            return
        
        review_request = self.pending_reviews[review_id]
        review_request.status = final_status
        review_request.completed_at = datetime.now(timezone.utc)
        
        # Release assigned reviewers
        for reviewer_id in review_request.assigned_reviewers:
            self.assignment_engine.release_reviewer(reviewer_id)
        
        # Update metrics
        self.metrics["total_reviews_completed"] += 1
        
        if final_status == ReviewStatus.APPROVED:
            self.metrics["total_reviews_approved"] += 1
        elif final_status == ReviewStatus.REJECTED:
            self.metrics["total_reviews_rejected"] += 1
        elif final_status == ReviewStatus.MODIFIED:
            self.metrics["total_reviews_modified"] += 1
        
        # Calculate review time
        if review_request.assigned_at:
            review_time = (review_request.completed_at - review_request.assigned_at).total_seconds() / 3600
            self._update_avg_review_time(review_time)
        
        # Move to completed
        self.completed_reviews[review_id] = review_request
        del self.pending_reviews[review_id]
        
        logger.info(f"Review {review_id} completed with status: {final_status.value}")
    
    def _update_avg_review_time(self, review_time_hours: float):
        """Update average review time metric."""
        current_avg = self.metrics["avg_review_time_hours"]
        completed_count = self.metrics["total_reviews_completed"]
        
        if completed_count > 1:
            self.metrics["avg_review_time_hours"] = (
                (current_avg * (completed_count - 1) + review_time_hours) / completed_count
            )
        else:
            self.metrics["avg_review_time_hours"] = review_time_hours
    
    def get_pending_reviews(self, reviewer_id: Optional[str] = None) -> List[HumanReviewRequest]:
        """Get pending reviews, optionally filtered by reviewer."""
        reviews = list(self.pending_reviews.values())
        
        if reviewer_id:
            reviews = [r for r in reviews if reviewer_id in r.assigned_reviewers]
        
        # Sort by priority and creation time
        priority_order = {
            ReviewPriority.CRITICAL: 0,
            ReviewPriority.HIGH: 1,
            ReviewPriority.MEDIUM: 2,
            ReviewPriority.LOW: 3
        }
        
        reviews.sort(key=lambda r: (priority_order[r.priority], r.created_at))
        return reviews
    
    def get_review_status(self, review_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific review."""
        review_request = self.pending_reviews.get(review_id) or self.completed_reviews.get(review_id)
        
        if not review_request:
            return None
        
        return {
            "review_id": review_id,
            "status": review_request.status.value,
            "priority": review_request.priority.value,
            "assigned_reviewers": review_request.assigned_reviewers,
            "current_approvals": review_request.current_approvals,
            "required_approvals": review_request.required_approvals,
            "created_at": review_request.created_at.isoformat(),
            "completed_at": review_request.completed_at.isoformat() if review_request.completed_at else None,
            "feedback_count": len(review_request.feedback_items),
            "constitutional_hash": review_request.constitutional_hash
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive review system metrics."""
        total_completed = self.metrics["total_reviews_completed"]
        
        approval_rate = 0.0
        if total_completed > 0:
            approval_rate = (
                self.metrics["total_reviews_approved"] + self.metrics["total_reviews_modified"]
            ) / total_completed
        
        return {
            **self.metrics,
            "pending_reviews_count": len(self.pending_reviews),
            "completed_reviews_count": len(self.completed_reviews),
            "approval_rate": approval_rate,
            "active_reviewers": len([r for r in self.assignment_engine.reviewers.values() if r.active]),
            "avg_workload": sum(self.assignment_engine.workload_tracker.values()) / max(len(self.assignment_engine.workload_tracker), 1)
        }
    
    async def shutdown(self):
        """Shutdown the review system."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Human Review System shutdown complete")


# Global instance for service integration
_review_system: Optional[HumanReviewSystem] = None


async def get_review_system() -> HumanReviewSystem:
    """Get or create global review system instance."""
    global _review_system
    
    if _review_system is None:
        _review_system = HumanReviewSystem()
    
    return _review_system
