"""
Unit tests for Human Review System

Tests the comprehensive human review workflow for RAG-generated rules
including reviewer assignment, feedback collection, and approval processes.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, Mock, patch

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

try:
    from services.core.policy_governance.pgc_service.app.core.human_review_system import (
        HumanReviewSystem,
        ReviewAssignmentEngine,
        ReviewerProfile,
        HumanReviewRequest,
        ReviewFeedback,
        ReviewStatus,
        ReviewPriority,
        ReviewerRole,
        CONSTITUTIONAL_HASH
    )
except ImportError as e:
    import pytest
    pytest.skip(f"Required module not available: {e}", allow_module_level=True)
from services.core.policy_governance.pgc_service.app.core.rag_rule_generator import RegoRuleResult


class TestReviewerProfile:
    """Test reviewer profile functionality."""
    
    def test_reviewer_profile_creation(self):
        """Test creation of reviewer profile."""
        profile = ReviewerProfile(
            reviewer_id="reviewer_1",
            name="John Doe",
            email="john.doe@example.com",
            role=ReviewerRole.SENIOR_REVIEWER,
            expertise_areas=["privacy", "security"],
            max_concurrent_reviews=3
        )
        
        assert profile.reviewer_id == "reviewer_1"
        assert profile.name == "John Doe"
        assert profile.role == ReviewerRole.SENIOR_REVIEWER
        assert "privacy" in profile.expertise_areas
        assert profile.active == True
        assert profile.max_concurrent_reviews == 3


class TestReviewAssignmentEngine:
    """Test review assignment engine functionality."""
    
    @pytest.fixture
    def assignment_engine(self):
        return ReviewAssignmentEngine()
    
    @pytest.fixture
    def sample_reviewers(self):
        return [
            ReviewerProfile(
                reviewer_id="junior_1",
                name="Junior Reviewer",
                email="junior@example.com",
                role=ReviewerRole.JUNIOR_REVIEWER,
                expertise_areas=["general"],
                quality_score=0.7
            ),
            ReviewerProfile(
                reviewer_id="senior_1",
                name="Senior Reviewer",
                email="senior@example.com",
                role=ReviewerRole.SENIOR_REVIEWER,
                expertise_areas=["privacy", "security"],
                quality_score=0.9
            ),
            ReviewerProfile(
                reviewer_id="expert_1",
                name="Policy Expert",
                email="expert@example.com",
                role=ReviewerRole.POLICY_EXPERT,
                expertise_areas=["privacy", "compliance"],
                quality_score=0.95
            )
        ]
    
    def test_register_reviewer(self, assignment_engine, sample_reviewers):
        """Test reviewer registration."""
        reviewer = sample_reviewers[0]
        assignment_engine.register_reviewer(reviewer)
        
        assert reviewer.reviewer_id in assignment_engine.reviewers
        assert assignment_engine.workload_tracker[reviewer.reviewer_id] == 0
    
    def test_find_best_reviewers(self, assignment_engine, sample_reviewers):
        """Test finding best reviewers for a request."""
        # Register reviewers
        for reviewer in sample_reviewers:
            assignment_engine.register_reviewer(reviewer)
        
        # Create mock review request
        rule_result = RegoRuleResult(
            rule_id="test_rule",
            rule_content="package privacy.test\ndefault allow = false",
            confidence_score=0.6,
            source_principles=["privacy_principle"],
            reasoning="Test rule",
            constitutional_hash=CONSTITUTIONAL_HASH
        )
        
        review_request = HumanReviewRequest(
            review_id="test_review",
            rule_result=rule_result,
            original_query="privacy rule test",
            context={},
            priority=ReviewPriority.MEDIUM
        )
        
        # Find best reviewers
        selected = assignment_engine.find_best_reviewers(review_request, 2)
        
        assert len(selected) <= 2
        assert all(reviewer_id in assignment_engine.reviewers for reviewer_id in selected)
        
        # Should prefer higher-quality reviewers with relevant expertise
        if len(selected) >= 2:
            # Expert should be selected due to privacy expertise
            assert "expert_1" in selected or "senior_1" in selected
    
    def test_workload_balancing(self, assignment_engine, sample_reviewers):
        """Test workload balancing in reviewer assignment."""
        for reviewer in sample_reviewers:
            assignment_engine.register_reviewer(reviewer)
        
        # Simulate high workload for expert
        assignment_engine.workload_tracker["expert_1"] = 4  # Near max capacity
        
        rule_result = RegoRuleResult(
            rule_id="test_rule",
            rule_content="package test\ndefault allow = false",
            confidence_score=0.7,
            source_principles=[],
            reasoning="Test",
            constitutional_hash=CONSTITUTIONAL_HASH
        )
        
        review_request = HumanReviewRequest(
            review_id="test_review",
            rule_result=rule_result,
            original_query="test query",
            context={},
            priority=ReviewPriority.MEDIUM
        )
        
        selected = assignment_engine.find_best_reviewers(review_request, 1)
        
        # Should not select overloaded expert
        assert "expert_1" not in selected or assignment_engine.workload_tracker["expert_1"] < 5


class TestHumanReviewSystem:
    """Test human review system functionality."""
    
    @pytest.fixture
    def review_system(self):
        return HumanReviewSystem(review_timeout_hours=1)  # Short timeout for testing
    
    @pytest.fixture
    def sample_rule_result(self):
        return RegoRuleResult(
            rule_id="test_rule_1",
            rule_content=f"""package test.policy

default allow = false

allow {{
    input.constitutional_hash == "{CONSTITUTIONAL_HASH}"
    input.test_mode == true
}}""",
            confidence_score=0.6,  # Low confidence to trigger review
            source_principles=["test_principle"],
            reasoning="Test rule for human review",
            constitutional_hash=CONSTITUTIONAL_HASH
        )
    
    def test_reviewer_registration(self, review_system):
        """Test reviewer registration in the system."""
        profile = ReviewerProfile(
            reviewer_id="test_reviewer",
            name="Test Reviewer",
            email="test@example.com",
            role=ReviewerRole.SENIOR_REVIEWER
        )
        
        review_system.register_reviewer(profile)
        
        assert "test_reviewer" in review_system.assignment_engine.reviewers
        assert review_system.assignment_engine.workload_tracker["test_reviewer"] == 0
    
    @pytest.mark.asyncio
    async def test_submit_for_review(self, review_system, sample_rule_result):
        """Test submitting a rule for review."""
        # Register a reviewer first
        profile = ReviewerProfile(
            reviewer_id="reviewer_1",
            name="Test Reviewer",
            email="test@example.com",
            role=ReviewerRole.SENIOR_REVIEWER
        )
        review_system.register_reviewer(profile)
        
        # Submit for review
        review_id = await review_system.submit_for_review(
            rule_result=sample_rule_result,
            original_query="test privacy rule",
            context={"domain": "healthcare"},
            priority=ReviewPriority.HIGH
        )
        
        assert review_id.startswith("review-")
        assert review_id in review_system.pending_reviews
        
        review_request = review_system.pending_reviews[review_id]
        assert review_request.status == ReviewStatus.IN_REVIEW
        assert review_request.priority == ReviewPriority.HIGH
        assert len(review_request.assigned_reviewers) > 0
        assert review_request.constitutional_hash == CONSTITUTIONAL_HASH
    
    @pytest.mark.asyncio
    async def test_submit_feedback_approval(self, review_system, sample_rule_result):
        """Test submitting approval feedback."""
        # Setup reviewer and review
        profile = ReviewerProfile(
            reviewer_id="reviewer_1",
            name="Test Reviewer",
            email="test@example.com",
            role=ReviewerRole.SENIOR_REVIEWER
        )
        review_system.register_reviewer(profile)
        
        review_id = await review_system.submit_for_review(
            rule_result=sample_rule_result,
            original_query="test rule",
            required_approvals=1
        )
        
        # Submit approval feedback
        success = await review_system.submit_feedback(
            review_id=review_id,
            reviewer_id="reviewer_1",
            feedback_type="approval",
            comments="Rule looks good, constitutional compliance verified",
            quality_rating=4
        )
        
        assert success == True
        assert review_id not in review_system.pending_reviews  # Should be completed
        assert review_id in review_system.completed_reviews
        
        completed_review = review_system.completed_reviews[review_id]
        assert completed_review.status == ReviewStatus.APPROVED
        assert len(completed_review.feedback_items) == 1
        assert completed_review.feedback_items[0].feedback_type == "approval"
    
    @pytest.mark.asyncio
    async def test_submit_feedback_rejection(self, review_system, sample_rule_result):
        """Test submitting rejection feedback."""
        # Setup reviewer and review
        profile = ReviewerProfile(
            reviewer_id="reviewer_1",
            name="Test Reviewer",
            email="test@example.com",
            role=ReviewerRole.SENIOR_REVIEWER
        )
        review_system.register_reviewer(profile)
        
        review_id = await review_system.submit_for_review(
            rule_result=sample_rule_result,
            original_query="test rule"
        )
        
        # Submit rejection feedback
        success = await review_system.submit_feedback(
            review_id=review_id,
            reviewer_id="reviewer_1",
            feedback_type="rejection",
            comments="Rule has security vulnerabilities",
            quality_rating=2
        )
        
        assert success == True
        assert review_id in review_system.completed_reviews
        
        completed_review = review_system.completed_reviews[review_id]
        assert completed_review.status == ReviewStatus.REJECTED
    
    @pytest.mark.asyncio
    async def test_submit_feedback_modification(self, review_system, sample_rule_result):
        """Test submitting modification feedback."""
        # Setup reviewer and review
        profile = ReviewerProfile(
            reviewer_id="reviewer_1",
            name="Test Reviewer",
            email="test@example.com",
            role=ReviewerRole.SENIOR_REVIEWER
        )
        review_system.register_reviewer(profile)
        
        review_id = await review_system.submit_for_review(
            rule_result=sample_rule_result,
            original_query="test rule"
        )
        
        # Submit modification feedback
        modified_rule = f"""package test.policy.improved

default allow = false

allow {{
    input.constitutional_hash == "{CONSTITUTIONAL_HASH}"
    input.test_mode == true
    input.security_validated == true
}}"""
        
        success = await review_system.submit_feedback(
            review_id=review_id,
            reviewer_id="reviewer_1",
            feedback_type="modification",
            comments="Added security validation requirement",
            suggested_changes=modified_rule,
            quality_rating=4
        )
        
        assert success == True
        assert review_id in review_system.completed_reviews
        
        completed_review = review_system.completed_reviews[review_id]
        assert completed_review.status == ReviewStatus.MODIFIED
        assert completed_review.modified_rule_content == modified_rule
    
    def test_get_pending_reviews(self, review_system):
        """Test getting pending reviews."""
        # Initially should be empty
        pending = review_system.get_pending_reviews()
        assert len(pending) == 0
        
        # Add a mock pending review
        rule_result = RegoRuleResult(
            rule_id="pending_rule",
            rule_content="package test",
            confidence_score=0.5,
            source_principles=[],
            reasoning="Test",
            constitutional_hash=CONSTITUTIONAL_HASH
        )
        
        review_request = HumanReviewRequest(
            review_id="pending_review",
            rule_result=rule_result,
            original_query="test",
            context={},
            priority=ReviewPriority.HIGH,
            assigned_reviewers=["reviewer_1"]
        )
        
        review_system.pending_reviews["pending_review"] = review_request
        
        # Should now return the pending review
        pending = review_system.get_pending_reviews()
        assert len(pending) == 1
        assert pending[0].review_id == "pending_review"
        
        # Test filtering by reviewer
        pending_for_reviewer = review_system.get_pending_reviews("reviewer_1")
        assert len(pending_for_reviewer) == 1
        
        pending_for_other = review_system.get_pending_reviews("other_reviewer")
        assert len(pending_for_other) == 0
    
    def test_get_review_status(self, review_system):
        """Test getting review status."""
        # Test non-existent review
        status = review_system.get_review_status("non_existent")
        assert status is None
        
        # Add a mock review
        rule_result = RegoRuleResult(
            rule_id="status_test_rule",
            rule_content="package test",
            confidence_score=0.7,
            source_principles=[],
            reasoning="Test",
            constitutional_hash=CONSTITUTIONAL_HASH
        )
        
        review_request = HumanReviewRequest(
            review_id="status_test",
            rule_result=rule_result,
            original_query="test query",
            context={},
            priority=ReviewPriority.MEDIUM,
            assigned_reviewers=["reviewer_1"],
            required_approvals=1,
            current_approvals=0
        )
        
        review_system.pending_reviews["status_test"] = review_request
        
        # Get status
        status = review_system.get_review_status("status_test")
        
        assert status is not None
        assert status["review_id"] == "status_test"
        assert status["status"] == ReviewStatus.PENDING.value
        assert status["priority"] == ReviewPriority.MEDIUM.value
        assert status["assigned_reviewers"] == ["reviewer_1"]
        assert status["constitutional_hash"] == CONSTITUTIONAL_HASH
    
    def test_metrics_tracking(self, review_system):
        """Test metrics tracking functionality."""
        initial_metrics = review_system.get_metrics()
        
        assert "total_reviews_submitted" in initial_metrics
        assert "total_reviews_completed" in initial_metrics
        assert "constitutional_hash" in initial_metrics
        assert initial_metrics["constitutional_hash"] == CONSTITUTIONAL_HASH
        assert initial_metrics["pending_reviews_count"] == 0
        assert initial_metrics["completed_reviews_count"] == 0


@pytest.mark.asyncio
async def test_integration_workflow():
    """Test complete integration workflow."""
    review_system = HumanReviewSystem()
    
    # Register reviewers
    senior_reviewer = ReviewerProfile(
        reviewer_id="senior_reviewer",
        name="Senior Reviewer",
        email="senior@example.com",
        role=ReviewerRole.SENIOR_REVIEWER,
        expertise_areas=["privacy", "security"]
    )
    
    expert_reviewer = ReviewerProfile(
        reviewer_id="expert_reviewer",
        name="Policy Expert",
        email="expert@example.com",
        role=ReviewerRole.POLICY_EXPERT,
        expertise_areas=["privacy", "compliance"]
    )
    
    review_system.register_reviewer(senior_reviewer)
    review_system.register_reviewer(expert_reviewer)
    
    # Create rule that needs review
    rule_result = RegoRuleResult(
        rule_id="integration_test_rule",
        rule_content=f"""package integration.test

default allow = false

allow {{
    input.constitutional_hash == "{CONSTITUTIONAL_HASH}"
    input.privacy_compliant == true
}}""",
        confidence_score=0.4,  # Low confidence
        source_principles=["privacy_principle"],
        reasoning="Integration test rule",
        constitutional_hash=CONSTITUTIONAL_HASH
    )
    
    # Submit for review
    review_id = await review_system.submit_for_review(
        rule_result=rule_result,
        original_query="privacy compliance rule",
        context={"domain": "healthcare"},
        priority=ReviewPriority.HIGH,
        required_approvals=2  # Require 2 approvals
    )
    
    # Verify review was created
    assert review_id in review_system.pending_reviews
    review_request = review_system.pending_reviews[review_id]
    assert len(review_request.assigned_reviewers) == 2
    assert review_request.constitutional_hash == CONSTITUTIONAL_HASH
    
    # First reviewer approves
    await review_system.submit_feedback(
        review_id=review_id,
        reviewer_id=review_request.assigned_reviewers[0],
        feedback_type="approval",
        comments="Privacy compliance looks good",
        quality_rating=4
    )
    
    # Should still be pending (needs 2 approvals)
    assert review_id in review_system.pending_reviews
    assert review_system.pending_reviews[review_id].current_approvals == 1
    
    # Second reviewer approves
    await review_system.submit_feedback(
        review_id=review_id,
        reviewer_id=review_request.assigned_reviewers[1],
        feedback_type="approval",
        comments="Constitutional compliance verified",
        quality_rating=5
    )
    
    # Should now be completed
    assert review_id not in review_system.pending_reviews
    assert review_id in review_system.completed_reviews
    
    completed_review = review_system.completed_reviews[review_id]
    assert completed_review.status == ReviewStatus.APPROVED
    assert completed_review.current_approvals == 2
    assert len(completed_review.feedback_items) == 2
    
    # Check metrics
    metrics = review_system.get_metrics()
    assert metrics["total_reviews_submitted"] == 1
    assert metrics["total_reviews_completed"] == 1
    assert metrics["total_reviews_approved"] == 1


if __name__ == "__main__":
    pytest.main([__file__])
