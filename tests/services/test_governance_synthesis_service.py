#!/usr/bin/env python3
"""
Comprehensive Test Suite for Governance Synthesis Service

Tests the enhanced OPA governance synthesis with:
- Advanced policy evaluation engine
- Multi-policy orchestration
- Policy conflict resolution
- Constitutional compliance validation
- Performance optimizations

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import json
import os

# Add service path
import sys
import time
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

import pytest

sys.path.append(
    os.path.join(os.path.dirname(__file__), "../../services/core/governance-synthesis")
)

from advanced_opa_engine import (
    AdvancedGovernanceSynthesisEngine,
    DecisionType,
    OPAEvaluationEngine,
    PolicyConflict,
    PolicyConflictType,
    PolicyDecision,
    PolicyEvaluationContext,
    PolicyType,
)


class TestPolicyEvaluationContext:
    """Test suite for Policy Evaluation Context."""

    def test_context_creation(self):
        """Test policy evaluation context creation."""
        context = PolicyEvaluationContext(
            request_id="test_001",
            timestamp=datetime.now(timezone.utc),
            principal={"id": "user_123", "type": "human"},
            resource={"id": "resource_456", "type": "data"},
            action="read",
            environment={"ip": "192.168.1.1"},
            constitutional_requirements={"fairness": True},
        )

        assert context.request_id == "test_001"
        assert context.principal["id"] == "user_123"
        assert context.action == "read"
        assert context.constitutional_requirements["fairness"] is True

    def test_context_serialization(self):
        """Test context serialization for caching."""
        context = PolicyEvaluationContext(
            request_id="test_002",
            timestamp=datetime.now(timezone.utc),
            principal={"id": "user_123"},
            resource={"id": "resource_456"},
            action="write",
        )

        # Should be serializable
        serialized = json.dumps(
            {
                "request_id": context.request_id,
                "principal": context.principal,
                "resource": context.resource,
                "action": context.action,
            }
        )
        assert serialized is not None


class TestOPAEvaluationEngine:
    """Test suite for OPA Evaluation Engine."""

    @pytest.fixture
    def opa_engine(self):
        """Create OPA evaluation engine instance."""
        return OPAEvaluationEngine(
            opa_url="http://localhost:8181", policies_path="./policies"
        )

    @pytest.fixture
    def sample_context(self):
        """Create sample evaluation context."""
        return PolicyEvaluationContext(
            request_id="eval_001",
            timestamp=datetime.now(timezone.utc),
            principal={
                "id": "user_123",
                "type": "human",
                "authenticated": True,
                "roles": ["user", "analyst"],
            },
            resource={
                "id": "resource_789",
                "type": "governance_policy",
                "sensitivity": "medium",
            },
            action="modify",
            environment={"time_of_day": "business_hours"},
            constitutional_requirements={
                "human_dignity": True,
                "fairness": True,
                "transparency": True,
            },
        )

    # Basic Evaluation Tests

    async def test_single_policy_evaluation(self, opa_engine, sample_context):
        """Test single policy evaluation."""
        decision = await opa_engine.evaluate_policy(
            "constitutional_principles", sample_context
        )

        assert decision is not None
        assert isinstance(decision.decision, DecisionType)
        assert 0 <= decision.confidence_score <= 1
        assert decision.constitutional_compliance in [True, False]
        assert len(decision.policies_evaluated) == 1
        assert decision.evaluation_time_ms > 0

    async def test_multiple_policy_evaluation(self, opa_engine, sample_context):
        """Test multiple policy evaluation."""
        policies = [
            "constitutional_principles",
            "security_compliance",
            "data_governance",
        ]
        decisions = await opa_engine.evaluate_multiple_policies(
            policies, sample_context
        )

        assert len(decisions) == 3
        assert all(isinstance(d, PolicyDecision) for d in decisions)
        assert all(d.constitutional_hash == "cdd01ef066bc6cf2" for d in decisions)

    async def test_constitutional_policy_evaluation(self, opa_engine, sample_context):
        """Test constitutional policy evaluation logic."""
        decision = await opa_engine.evaluate_policy(
            "constitutional_principles", sample_context
        )

        # Should have principle scores in metadata
        assert "principle_scores" in decision.metadata
        principle_scores = decision.metadata["principle_scores"]

        assert "human_dignity" in principle_scores
        assert "fairness" in principle_scores
        assert "transparency" in principle_scores
        assert "accountability" in principle_scores
        assert "privacy" in principle_scores

        # Scores should be reasonable
        for score in principle_scores.values():
            assert 0 <= score <= 1

    async def test_evolutionary_policy_evaluation(self, opa_engine):
        """Test evolutionary governance policy evaluation."""
        context = PolicyEvaluationContext(
            request_id="evo_001",
            timestamp=datetime.now(timezone.utc),
            principal={"id": "system", "type": "ai_agent"},
            resource={
                "id": "agent_123",
                "type": "ai_agent",
                "evolution_type": "capability_enhancement",
                "complexity_score": 3,
                "novelty_score": 4,
                "impact_score": 2,
            },
            action="agent_evolution",
        )

        decision = await opa_engine.evaluate_policy("evolutionary_governance", context)

        assert "risk_score" in decision.metadata
        assert "safety_score" in decision.metadata
        assert decision.metadata["risk_score"] < 0.6  # Moderate risk

    async def test_security_policy_evaluation(self, opa_engine):
        """Test security policy evaluation."""
        context = PolicyEvaluationContext(
            request_id="sec_001",
            timestamp=datetime.now(timezone.utc),
            principal={
                "id": "user_456",
                "authenticated": True,
                "authentication_methods": ["mfa"],
                "roles": ["admin"],
            },
            resource={"id": "sensitive_data", "type": "data"},
            action="delete",
            environment={"suspicious_activity": False},
        )

        decision = await opa_engine.evaluate_policy("security_compliance", context)

        assert "authentication_score" in decision.metadata
        assert "authorization_score" in decision.metadata
        assert "threat_score" in decision.metadata
        assert decision.metadata["authentication_score"] > 0.5  # MFA gives good score

    async def test_multi_tenant_policy_evaluation(self, opa_engine):
        """Test multi-tenant policy evaluation."""
        context = PolicyEvaluationContext(
            request_id="mt_001",
            timestamp=datetime.now(timezone.utc),
            principal={"id": "user_789", "tenant_id": "tenant_001"},
            resource={"id": "resource_123", "tenant_id": "tenant_001"},
            action="access",
        )

        decision = await opa_engine.evaluate_policy("multi_tenant_security", context)

        assert decision.decision == DecisionType.ALLOW  # Same tenant
        assert "isolation_score" in decision.metadata
        assert decision.metadata["isolation_score"] == 1.0

    # Caching Tests

    async def test_evaluation_caching(self, opa_engine, sample_context):
        """Test evaluation result caching."""
        # First evaluation
        decision1 = await opa_engine.evaluate_policy("test_policy", sample_context)
        time1 = decision1.evaluation_time_ms

        # Second evaluation (should be cached)
        decision2 = await opa_engine.evaluate_policy("test_policy", sample_context)

        # Cache hit should be faster
        assert decision2.evaluation_time_ms <= time1
        assert opa_engine.metrics.cache_hit_rate > 0

    async def test_cache_invalidation(self, opa_engine):
        """Test cache invalidation based on time."""
        context = PolicyEvaluationContext(
            request_id="cache_001",
            timestamp=datetime.now(timezone.utc) - timedelta(minutes=10),  # Old context
            principal={"id": "user_123"},
            resource={"id": "resource_456"},
            action="read",
        )

        # Should not use cache for old context
        decision = await opa_engine.evaluate_policy("test_policy", context)
        assert decision is not None

    # Error Handling Tests

    async def test_policy_evaluation_error_handling(self, opa_engine, sample_context):
        """Test error handling in policy evaluation."""
        # Simulate error by using non-existent policy
        with patch.object(
            opa_engine, "_simulate_opa_evaluation", side_effect=Exception("OPA error")
        ):
            decision = await opa_engine.evaluate_policy("error_policy", sample_context)

            assert decision.decision == DecisionType.DENY
            assert decision.confidence_score == 0.0
            assert "error" in decision.metadata
            assert not decision.constitutional_compliance

    # Performance Tests

    @pytest.mark.performance
    async def test_evaluation_performance(self, opa_engine, sample_context):
        """Test evaluation performance."""
        start_time = time.time()

        # Run 100 evaluations
        tasks = []
        for i in range(100):
            context_copy = PolicyEvaluationContext(
                request_id=f"perf_{i}",
                timestamp=sample_context.timestamp,
                principal=sample_context.principal,
                resource=sample_context.resource,
                action=sample_context.action,
            )
            tasks.append(
                opa_engine.evaluate_policy("constitutional_principles", context_copy)
            )

        results = await asyncio.gather(*tasks)

        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / 100

        assert all(r is not None for r in results)
        assert avg_time < 0.05  # Less than 50ms per evaluation

        print(f"Average evaluation time: {avg_time * 1000:.2f}ms")


class TestAdvancedGovernanceSynthesisEngine:
    """Test suite for Advanced Governance Synthesis Engine."""

    @pytest.fixture
    def synthesis_engine(self):
        """Create governance synthesis engine instance."""
        return AdvancedGovernanceSynthesisEngine(policies_path="./policies")

    @pytest.fixture
    def complex_context(self):
        """Create complex evaluation context."""
        return PolicyEvaluationContext(
            request_id="synthesis_001",
            timestamp=datetime.now(timezone.utc),
            principal={
                "id": "user_999",
                "type": "human",
                "tenant_id": "tenant_001",
                "roles": ["user", "analyst", "reviewer"],
                "authenticated": True,
                "authentication_methods": ["mfa", "certificate"],
            },
            resource={
                "id": "agent_evolution_request",
                "type": "ai_agent",
                "tenant_id": "tenant_001",
                "evolution_type": "capability_enhancement",
                "data_sensitivity": "high",
                "complexity_score": 7,
            },
            action="agent_evolution",
            environment={
                "ip_address": "192.168.1.100",
                "time_of_day": "business_hours",
                "request_source": "internal",
            },
            constitutional_requirements={
                "human_dignity": True,
                "fairness": True,
                "transparency": True,
                "accountability": True,
                "privacy": True,
            },
        )

    # Synthesis Tests

    async def test_basic_governance_synthesis(self, synthesis_engine, complex_context):
        """Test basic governance synthesis."""
        result = await synthesis_engine.synthesize_governance_decision(complex_context)

        assert result is not None
        assert "synthesis_id" in result
        assert "final_decision" in result
        assert result["final_decision"] in [
            "allow",
            "deny",
            "conditional",
            "escalate",
            "defer",
        ]
        assert result["constitutional_compliance"] in [True, False]
        assert result["synthesis_time_ms"] > 0
        assert len(result["policies_evaluated"]) > 0

    async def test_policy_scope_determination(self, synthesis_engine, complex_context):
        """Test automatic policy scope determination."""
        # Should determine relevant policies based on context
        applicable_policies = synthesis_engine._determine_applicable_policies(
            complex_context
        )

        assert (
            "constitutional_principles" in applicable_policies
        )  # Always included for governance
        assert (
            "evolutionary_governance" in applicable_policies
        )  # Due to agent_evolution action
        assert "multi_tenant_security" in applicable_policies  # Due to tenant context
        assert (
            "security_compliance" in applicable_policies
        )  # Due to authentication context

    async def test_conflict_detection(self, synthesis_engine):
        """Test policy conflict detection."""
        # Create conflicting decisions
        decision1 = PolicyDecision(
            decision_id="d1",
            decision=DecisionType.ALLOW,
            confidence_score=0.9,
            policies_evaluated=["policy1"],
            evaluation_time_ms=10,
            constitutional_compliance=True,
        )

        decision2 = PolicyDecision(
            decision_id="d2",
            decision=DecisionType.DENY,
            confidence_score=0.8,
            policies_evaluated=["policy2"],
            evaluation_time_ms=10,
            constitutional_compliance=True,
        )

        conflicts = synthesis_engine._detect_policy_conflicts(
            [decision1, decision2], None
        )

        assert len(conflicts) == 1
        assert conflicts[0].conflict_type == PolicyConflictType.LOGICAL_CONTRADICTION
        assert conflicts[0].severity == "high"

    async def test_conflict_resolution(self, synthesis_engine):
        """Test policy conflict resolution."""
        # Create conflict
        conflict = PolicyConflict(
            conflict_id="c1",
            conflict_type=PolicyConflictType.LOGICAL_CONTRADICTION,
            policies_involved=["constitutional_principles", "operational_policy"],
            severity="high",
            description="Policy contradiction",
        )

        # Update policy catalog for test
        synthesis_engine.policy_catalog["constitutional_principles"][
            "priority"
        ] = "critical"
        synthesis_engine.policy_catalog["operational_policy"] = {"priority": "medium"}

        resolved = await synthesis_engine._resolve_single_conflict(conflict, None)

        assert resolved.resolution_strategy is not None
        assert resolved.resolution_confidence > 0
        assert (
            "constitutional_principles" in resolved.resolution_strategy
        )  # Higher priority wins

    async def test_final_decision_synthesis(self, synthesis_engine):
        """Test final decision synthesis from multiple policies."""
        decisions = [
            PolicyDecision(
                decision_id="d1",
                decision=DecisionType.ALLOW,
                confidence_score=0.9,
                policies_evaluated=["policy1"],
                evaluation_time_ms=10,
                constitutional_compliance=True,
                reasons=["Policy 1 allows"],
            ),
            PolicyDecision(
                decision_id="d2",
                decision=DecisionType.ALLOW,
                confidence_score=0.8,
                policies_evaluated=["policy2"],
                evaluation_time_ms=15,
                constitutional_compliance=True,
                reasons=["Policy 2 allows"],
            ),
            PolicyDecision(
                decision_id="d3",
                decision=DecisionType.CONDITIONAL,
                confidence_score=0.7,
                policies_evaluated=["policy3"],
                evaluation_time_ms=20,
                constitutional_compliance=True,
                conditions=[{"type": "monitoring", "requirement": "Enable monitoring"}],
                reasons=["Policy 3 conditional"],
            ),
        ]

        final_decision = synthesis_engine._synthesize_final_decision(
            decisions, [], None
        )

        assert (
            final_decision.decision == DecisionType.CONDITIONAL
        )  # Conservative approach
        assert len(final_decision.reasons) >= 3  # All reasons included
        assert len(final_decision.conditions) >= 1  # Conditions preserved
        assert final_decision.constitutional_compliance is True

    async def test_weighted_decision_calculation(self, synthesis_engine):
        """Test weighted decision calculation."""
        decisions = [
            PolicyDecision(
                decision_id="d1",
                decision=DecisionType.ALLOW,
                confidence_score=0.9,
                policies_evaluated=["p1"],
                evaluation_time_ms=10,
                constitutional_compliance=True,
            ),
            PolicyDecision(
                decision_id="d2",
                decision=DecisionType.DENY,
                confidence_score=0.6,
                policies_evaluated=["p2"],
                evaluation_time_ms=10,
                constitutional_compliance=True,
            ),
        ]

        weights = synthesis_engine._calculate_decision_weights(decisions)

        assert weights["allow"] > weights["deny"]  # Higher confidence for allow
        assert abs(sum(weights.values()) - 1.0) < 0.01  # Weights sum to 1

    # Complex Scenarios

    async def test_multi_policy_synthesis_with_conflicts(
        self, synthesis_engine, complex_context
    ):
        """Test synthesis with multiple policies and conflicts."""
        # Specify policies that might conflict
        policy_scope = [
            "constitutional_principles",
            "evolutionary_governance",
            "security_compliance",
            "multi_tenant_security",
        ]

        result = await synthesis_engine.synthesize_governance_decision(
            complex_context, policy_scope
        )

        assert result["synthesis_id"] is not None
        assert len(result["policy_decisions"]) == 4
        assert result["conflicts_detected"] >= 0
        assert result["conflicts_resolved"] == result["conflicts_detected"]

        # Check audit trail
        assert len(result["audit_trail"]) > 0
        assert any(
            entry["event"] == "synthesis_started" for entry in result["audit_trail"]
        )

    async def test_constitutional_precedence(self, synthesis_engine):
        """Test constitutional principle precedence."""
        # Create context that violates constitutional principles
        violating_context = PolicyEvaluationContext(
            request_id="const_violation",
            timestamp=datetime.now(timezone.utc),
            principal={"id": "system"},
            resource={
                "id": "resource",
                "privacy_preserving": False,
                "transparency": False,
            },
            action="invasive_monitoring",
            constitutional_requirements={"privacy": True, "transparency": True},
        )

        result = await synthesis_engine.synthesize_governance_decision(
            violating_context
        )

        # Should deny due to constitutional violations
        assert result["final_decision"] == "deny"
        assert not result["constitutional_compliance"]
        assert any("constitutional" in reason.lower() for reason in result["reasons"])

    # Performance Tests

    @pytest.mark.performance
    async def test_synthesis_performance(self, synthesis_engine, complex_context):
        """Test synthesis performance under load."""
        start_time = time.time()

        # Run 50 synthesis operations
        tasks = []
        for i in range(50):
            context_copy = PolicyEvaluationContext(
                request_id=f"perf_synthesis_{i}",
                timestamp=complex_context.timestamp,
                principal=complex_context.principal,
                resource=complex_context.resource,
                action=complex_context.action,
                environment=complex_context.environment,
                constitutional_requirements=complex_context.constitutional_requirements,
            )
            tasks.append(synthesis_engine.synthesize_governance_decision(context_copy))

        results = await asyncio.gather(*tasks)

        end_time = time.time()
        total_time = end_time - start_time
        avg_time = (total_time / 50) * 1000  # Convert to ms

        assert all(r is not None for r in results)
        assert avg_time < 100  # Less than 100ms per synthesis

        print(f"Average synthesis time: {avg_time:.2f}ms")

    # Metrics Tests

    async def test_performance_metrics_tracking(
        self, synthesis_engine, complex_context
    ):
        """Test performance metrics tracking."""
        # Perform several syntheses
        for i in range(10):
            context = PolicyEvaluationContext(
                request_id=f"metrics_{i}",
                timestamp=datetime.now(timezone.utc),
                principal={"id": f"user_{i}"},
                resource={"id": f"resource_{i}"},
                action="read",
            )
            await synthesis_engine.synthesize_governance_decision(context)

        # Get metrics
        metrics = await synthesis_engine.get_performance_metrics()

        assert "synthesis_metrics" in metrics
        assert metrics["synthesis_metrics"]["total_syntheses"] >= 10
        assert metrics["synthesis_metrics"]["average_synthesis_time_ms"] > 0
        assert "decision_distribution" in metrics["synthesis_metrics"]

        assert "evaluation_engine_metrics" in metrics
        assert metrics["evaluation_engine_metrics"]["total_evaluations"] > 0

    # Edge Cases

    async def test_empty_policy_scope(self, synthesis_engine):
        """Test synthesis with no applicable policies."""
        minimal_context = PolicyEvaluationContext(
            request_id="minimal",
            timestamp=datetime.now(timezone.utc),
            principal={"id": "user"},
            resource={"id": "resource"},
            action="unknown_action",
        )

        result = await synthesis_engine.synthesize_governance_decision(
            minimal_context, []
        )

        # Should still provide a decision
        assert result["final_decision"] in [
            "allow",
            "deny",
            "conditional",
            "escalate",
            "defer",
        ]
        assert (
            len(result["policies_evaluated"]) >= 1
        )  # At least constitutional principles

    async def test_error_recovery(self, synthesis_engine, complex_context):
        """Test error recovery in synthesis."""
        # Mock evaluation error
        with patch.object(
            synthesis_engine.evaluation_engine,
            "evaluate_multiple_policies",
            side_effect=Exception("Evaluation error"),
        ):
            result = await synthesis_engine.synthesize_governance_decision(
                complex_context
            )

            assert result["final_decision"] == "deny"  # Safe default
            assert "error" in result
            assert result["error_message"] == "Evaluation error"


class TestPolicyTypes:
    """Test suite for different policy types."""

    def test_policy_type_enum(self):
        """Test policy type enumeration."""
        assert PolicyType.CONSTITUTIONAL.value == "constitutional"
        assert PolicyType.SECURITY.value == "security"
        assert PolicyType.EVOLUTIONARY.value == "evolutionary"
        assert PolicyType.DATA_GOVERNANCE.value == "data_governance"
        assert PolicyType.MULTI_TENANT.value == "multi_tenant"

    def test_decision_type_enum(self):
        """Test decision type enumeration."""
        assert DecisionType.ALLOW.value == "allow"
        assert DecisionType.DENY.value == "deny"
        assert DecisionType.CONDITIONAL.value == "conditional"
        assert DecisionType.ESCALATE.value == "escalate"
        assert DecisionType.DEFER.value == "defer"

    def test_conflict_type_enum(self):
        """Test conflict type enumeration."""
        assert PolicyConflictType.LOGICAL_CONTRADICTION.value == "logical_contradiction"
        assert (
            PolicyConflictType.CONSTITUTIONAL_VIOLATION.value
            == "constitutional_violation"
        )
        assert (
            PolicyConflictType.TEMPORAL_INCONSISTENCY.value == "temporal_inconsistency"
        )


# Integration Tests


class TestGovernanceSynthesisIntegration:
    """Integration tests for the complete governance synthesis system."""

    @pytest.fixture
    async def mock_opa_server(self):
        """Mock OPA server responses."""
        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {
                "result": {"allow": True, "compliance_score": 0.85}
            }
            mock_post.return_value = mock_response
            yield mock_post

    async def test_end_to_end_synthesis(self, synthesis_engine):
        """Test end-to-end governance synthesis."""
        # Complex multi-domain request
        context = PolicyEvaluationContext(
            request_id="e2e_test",
            timestamp=datetime.now(timezone.utc),
            principal={
                "id": "admin_user",
                "type": "human",
                "roles": ["admin", "security_officer"],
                "tenant_id": "enterprise_001",
                "authenticated": True,
                "authentication_methods": ["mfa", "biometric"],
            },
            resource={
                "id": "critical_system",
                "type": "infrastructure",
                "criticality": "high",
                "data_classification": "confidential",
                "tenant_id": "enterprise_001",
            },
            action="modify_security_settings",
            environment={
                "source_ip": "10.0.0.1",
                "time_of_day": "business_hours",
                "location": "headquarters",
                "threat_level": "low",
            },
            constitutional_requirements={
                "human_dignity": True,
                "fairness": True,
                "transparency": True,
                "accountability": True,
                "privacy": True,
            },
        )

        result = await synthesis_engine.synthesize_governance_decision(context)

        # Comprehensive validation
        assert result["synthesis_id"] is not None
        assert result["final_decision"] in [
            "allow",
            "conditional",
        ]  # Admin with proper auth
        assert result["confidence_score"] > 0.7  # High confidence
        assert result["constitutional_compliance"] is True
        assert len(result["policies_evaluated"]) >= 4  # Multiple policies involved

        # Verify audit trail completeness
        audit_events = [entry["event"] for entry in result["audit_trail"]]
        assert "synthesis_started" in audit_events

        # Check metadata
        assert result["metadata"]["constitutional_hash"] == "cdd01ef066bc6cf2"
        assert result["metadata"]["synthesis_engine"] == "advanced_opa_engine"


# Pytest configuration


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "performance: mark test as a performance test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
