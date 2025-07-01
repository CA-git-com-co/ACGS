"""
Comprehensive unit tests for Principle-Rule Traceability Enhancement
Target: >90% test coverage with traceability validation

Tests cover:
- Principle and rule management
- Relationship mapping and impact scoring
- Traceability coverage analysis
- High-impact rule identification
- Graph representation and analysis
- Performance metrics and reporting
"""

import os

# Import the module under test
import sys
from datetime import datetime, timezone

import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src", "core"))

from principle_tracer import (
    ConstitutionalPrinciple,
    GovernanceRule,
    ImpactLevel,
    PrincipleRuleRelationship,
    PrincipleTracer,
    RelationshipType,
    TraceabilityMetrics,
    get_principle_tracer,
)


class TestRelationshipType:
    """Test RelationshipType enum."""

    def test_relationship_type_values(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Test relationship type enum values."""
        assert RelationshipType.DIRECT_IMPLEMENTATION.value == "direct_implementation"
        assert RelationshipType.INDIRECT_SUPPORT.value == "indirect_support"
        assert RelationshipType.CONSTRAINT_ENFORCEMENT.value == "constraint_enforcement"
        assert RelationshipType.CONFLICT_RESOLUTION.value == "conflict_resolution"
        assert RelationshipType.DERIVED_REQUIREMENT.value == "derived_requirement"


class TestImpactLevel:
    """Test ImpactLevel enum."""

    def test_impact_level_values(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Test impact level enum values."""
        assert ImpactLevel.CRITICAL.value == "critical"
        assert ImpactLevel.HIGH.value == "high"
        assert ImpactLevel.MEDIUM.value == "medium"
        assert ImpactLevel.LOW.value == "low"
        assert ImpactLevel.MINIMAL.value == "minimal"


class TestConstitutionalPrinciple:
    """Test ConstitutionalPrinciple dataclass."""

    def test_principle_creation(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Test constitutional principle creation."""
        principle = ConstitutionalPrinciple(
            principle_id="PRIN-001",
            title="Constitutional Governance",
            description="Ensures all governance follows constitutional principles",
            category="governance",
            priority=9,
            constitutional_hash="cdd01ef066bc6cf2",
            created_at=datetime.now(timezone.utc),
            last_updated=datetime.now(timezone.utc),
        )

        assert principle.principle_id == "PRIN-001"
        assert principle.title == "Constitutional Governance"
        assert principle.priority == 9
        assert principle.constitutional_hash == "cdd01ef066bc6cf2"


class TestGovernanceRule:
    """Test GovernanceRule dataclass."""

    def test_rule_creation(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Test governance rule creation."""
        rule = GovernanceRule(
            rule_id="RULE-001",
            title="Policy Approval Process",
            content="All policies must undergo constitutional review",
            category="governance",
            policy_id="POL-001",
            enforcement_level="strict",
            created_at=datetime.now(timezone.utc),
            last_updated=datetime.now(timezone.utc),
            usage_frequency=50,
        )

        assert rule.rule_id == "RULE-001"
        assert rule.title == "Policy Approval Process"
        assert rule.enforcement_level == "strict"
        assert rule.usage_frequency == 50


class TestPrincipleRuleRelationship:
    """Test PrincipleRuleRelationship dataclass."""

    def test_relationship_creation(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Test principle-rule relationship creation."""
        relationship = PrincipleRuleRelationship(
            principle_id="PRIN-001",
            rule_id="RULE-001",
            relationship_type=RelationshipType.DIRECT_IMPLEMENTATION,
            impact_score=0.85,
            confidence=0.9,
            reasoning="Rule directly implements constitutional governance principle",
            evidence=["constitutional_review", "approval_process"],
            created_at=datetime.now(timezone.utc),
            last_validated=datetime.now(timezone.utc),
        )

        assert relationship.principle_id == "PRIN-001"
        assert relationship.rule_id == "RULE-001"
        assert relationship.relationship_type == RelationshipType.DIRECT_IMPLEMENTATION
        assert relationship.impact_score == 0.85
        assert relationship.confidence == 0.9
        assert len(relationship.evidence) == 2


class TestPrincipleTracer:
    """Test PrincipleTracer functionality."""

    @pytest.fixture
    def tracer(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Create principle tracer for testing."""
        return PrincipleTracer(
            constitutional_hash="cdd01ef066bc6cf2",
            impact_threshold=0.5,
            high_impact_principle_threshold=3,
        )

    @pytest.fixture
    def sample_principle(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Sample constitutional principle."""
        return ConstitutionalPrinciple(
            principle_id="PRIN-TEST-001",
            title="Test Constitutional Principle",
            description="A test principle for unit testing",
            category="test",
            priority=8,
            constitutional_hash="cdd01ef066bc6cf2",
            created_at=datetime.now(timezone.utc),
            last_updated=datetime.now(timezone.utc),
        )

    @pytest.fixture
    def sample_rule(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Sample governance rule."""
        return GovernanceRule(
            rule_id="RULE-TEST-001",
            title="Test Governance Rule",
            content="A test rule for unit testing",
            category="test",
            policy_id="POL-TEST-001",
            enforcement_level="moderate",
            created_at=datetime.now(timezone.utc),
            last_updated=datetime.now(timezone.utc),
            usage_frequency=25,
        )

    def test_tracer_initialization(self, tracer):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Test tracer initialization."""
        assert tracer.constitutional_hash == "cdd01ef066bc6cf2"
        assert tracer.impact_threshold == 0.5
        assert tracer.high_impact_principle_threshold == 3
        assert len(tracer.principles) == 0
        assert len(tracer.rules) == 0
        assert len(tracer.relationships) == 0
        assert tracer.traceability_graph.number_of_nodes() == 0

    @pytest.mark.asyncio
    async def test_add_principle(self, tracer, sample_principle):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Test adding constitutional principle."""
        result = await tracer.add_principle(sample_principle)

        assert result is True
        assert sample_principle.principle_id in tracer.principles
        assert tracer.traceability_graph.has_node(sample_principle.principle_id)

        # Check node attributes
        node_data = tracer.traceability_graph.nodes[sample_principle.principle_id]
        assert node_data["node_type"] == "principle"
        assert node_data["title"] == sample_principle.title
        assert node_data["priority"] == sample_principle.priority

    @pytest.mark.asyncio
    async def test_add_rule(self, tracer, sample_rule):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Test adding governance rule."""
        result = await tracer.add_rule(sample_rule)

        assert result is True
        assert sample_rule.rule_id in tracer.rules
        assert tracer.traceability_graph.has_node(sample_rule.rule_id)

        # Check node attributes
        node_data = tracer.traceability_graph.nodes[sample_rule.rule_id]
        assert node_data["node_type"] == "rule"
        assert node_data["title"] == sample_rule.title
        assert node_data["enforcement_level"] == sample_rule.enforcement_level

    @pytest.mark.asyncio
    async def test_add_relationship(self, tracer, sample_principle, sample_rule):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Test adding principle-rule relationship."""
        # First add principle and rule
        await tracer.add_principle(sample_principle)
        await tracer.add_rule(sample_rule)

        # Create relationship
        relationship = PrincipleRuleRelationship(
            principle_id=sample_principle.principle_id,
            rule_id=sample_rule.rule_id,
            relationship_type=RelationshipType.DIRECT_IMPLEMENTATION,
            impact_score=0.8,
            confidence=0.9,
            reasoning="Test relationship",
            evidence=["test_evidence"],
            created_at=datetime.now(timezone.utc),
            last_validated=datetime.now(timezone.utc),
        )

        result = await tracer.add_relationship(relationship)

        assert result is True
        key = (sample_principle.principle_id, sample_rule.rule_id)
        assert key in tracer.relationships
        assert tracer.traceability_graph.has_edge(
            sample_principle.principle_id, sample_rule.rule_id
        )

        # Check edge attributes
        edge_data = tracer.traceability_graph.edges[
            sample_principle.principle_id, sample_rule.rule_id
        ]
        assert (
            edge_data["relationship_type"]
            == RelationshipType.DIRECT_IMPLEMENTATION.value
        )
        assert edge_data["impact_score"] == 0.8
        assert edge_data["confidence"] == 0.9

    @pytest.mark.asyncio
    async def test_add_relationship_missing_principle(self, tracer, sample_rule):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Test adding relationship with missing principle."""
        await tracer.add_rule(sample_rule)

        relationship = PrincipleRuleRelationship(
            principle_id="NONEXISTENT-PRIN",
            rule_id=sample_rule.rule_id,
            relationship_type=RelationshipType.DIRECT_IMPLEMENTATION,
            impact_score=0.8,
            confidence=0.9,
            reasoning="Test relationship",
            evidence=["test_evidence"],
            created_at=datetime.now(timezone.utc),
            last_validated=datetime.now(timezone.utc),
        )

        result = await tracer.add_relationship(relationship)
        assert result is False

    def test_calculate_impact_score(self, tracer, sample_principle, sample_rule):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Test impact score calculation."""
        # Test with different parameters
        impact_score = tracer.calculate_impact_score(
            principle=sample_principle,
            rule=sample_rule,
            relationship_type=RelationshipType.DIRECT_IMPLEMENTATION,
            usage_frequency=100,
            severity_indicators=["safety", "constitutional"],
        )

        assert 0.0 <= impact_score <= 1.0
        assert (
            impact_score > 0.5
        )  # Should be high due to high priority and direct implementation

        # Test with low impact parameters
        low_impact_score = tracer.calculate_impact_score(
            principle=sample_principle,
            rule=sample_rule,
            relationship_type=RelationshipType.INDIRECT_SUPPORT,
            usage_frequency=1,
            severity_indicators=[],
        )

        assert low_impact_score < impact_score  # Should be lower

    def test_get_impact_level(self, tracer):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Test impact level classification."""
        assert tracer.get_impact_level(0.9) == ImpactLevel.CRITICAL
        assert tracer.get_impact_level(0.7) == ImpactLevel.HIGH
        assert tracer.get_impact_level(0.5) == ImpactLevel.MEDIUM
        assert tracer.get_impact_level(0.3) == ImpactLevel.LOW
        assert tracer.get_impact_level(0.1) == ImpactLevel.MINIMAL

    @pytest.mark.asyncio
    async def test_analyze_principle_influence(
        self, tracer, sample_principle, sample_rule
    ):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Test principle influence analysis."""
        # Setup principle and rule with relationship
        await tracer.add_principle(sample_principle)
        await tracer.add_rule(sample_rule)

        relationship = PrincipleRuleRelationship(
            principle_id=sample_principle.principle_id,
            rule_id=sample_rule.rule_id,
            relationship_type=RelationshipType.DIRECT_IMPLEMENTATION,
            impact_score=0.8,
            confidence=0.9,
            reasoning="Test relationship",
            evidence=["test_evidence"],
            created_at=datetime.now(timezone.utc),
            last_validated=datetime.now(timezone.utc),
        )
        await tracer.add_relationship(relationship)

        # Analyze influence
        analysis = await tracer.analyze_principle_influence(
            sample_principle.principle_id
        )

        assert analysis["principle_id"] == sample_principle.principle_id
        assert analysis["connected_rules_count"] == 1
        assert analysis["total_impact_score"] == 0.8
        assert analysis["average_impact_score"] == 0.8
        assert 0.0 <= analysis["influence_score"] <= 1.0
        assert analysis["workflow_coverage"] >= 1
        assert sample_rule.rule_id in analysis["connected_rules"]

    @pytest.mark.asyncio
    async def test_analyze_principle_influence_nonexistent(self, tracer):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Test principle influence analysis for nonexistent principle."""
        analysis = await tracer.analyze_principle_influence("NONEXISTENT")

        assert "error" in analysis
        assert analysis["influence_score"] == 0.0

    @pytest.mark.asyncio
    async def test_identify_high_impact_rules(self, tracer):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Test high-impact rule identification."""
        # Create multiple principles and one rule that affects all of them
        principles = []
        for i in range(5):  # More than threshold (3)
            principle = ConstitutionalPrinciple(
                principle_id=f"PRIN-{i:03d}",
                title=f"Test Principle {i}",
                description=f"Test principle {i}",
                category="test",
                priority=8,
                constitutional_hash="cdd01ef066bc6cf2",
                created_at=datetime.now(timezone.utc),
                last_updated=datetime.now(timezone.utc),
            )
            principles.append(principle)
            await tracer.add_principle(principle)

        # Create high-impact rule
        high_impact_rule = GovernanceRule(
            rule_id="HIGH-IMPACT-RULE",
            title="High Impact Rule",
            content="Rule affecting multiple principles",
            category="governance",
            policy_id="POL-HIGH",
            enforcement_level="strict",
            created_at=datetime.now(timezone.utc),
            last_updated=datetime.now(timezone.utc),
            usage_frequency=100,
        )
        await tracer.add_rule(high_impact_rule)

        # Create relationships
        for principle in principles:
            relationship = PrincipleRuleRelationship(
                principle_id=principle.principle_id,
                rule_id=high_impact_rule.rule_id,
                relationship_type=RelationshipType.DIRECT_IMPLEMENTATION,
                impact_score=0.7,
                confidence=0.9,
                reasoning="High impact relationship",
                evidence=["test"],
                created_at=datetime.now(timezone.utc),
                last_validated=datetime.now(timezone.utc),
            )
            await tracer.add_relationship(relationship)

        # Identify high-impact rules
        high_impact_rules = await tracer.identify_high_impact_rules()

        assert len(high_impact_rules) == 1
        assert high_impact_rules[0]["rule_id"] == "HIGH-IMPACT-RULE"
        assert high_impact_rules[0]["affected_principles_count"] == 5
        assert high_impact_rules[0]["total_impact_score"] == 3.5  # 5 * 0.7
        assert high_impact_rules[0]["average_impact_score"] == 0.7

    @pytest.mark.asyncio
    async def test_calculate_traceability_coverage(
        self, tracer, sample_principle, sample_rule
    ):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Test traceability coverage calculation."""
        # Add principle and rule with relationship
        await tracer.add_principle(sample_principle)
        await tracer.add_rule(sample_rule)

        relationship = PrincipleRuleRelationship(
            principle_id=sample_principle.principle_id,
            rule_id=sample_rule.rule_id,
            relationship_type=RelationshipType.DIRECT_IMPLEMENTATION,
            impact_score=0.8,
            confidence=0.9,
            reasoning="Test relationship",
            evidence=["test"],
            created_at=datetime.now(timezone.utc),
            last_validated=datetime.now(timezone.utc),
        )
        await tracer.add_relationship(relationship)

        # Calculate coverage
        metrics = await tracer.calculate_traceability_coverage()

        assert isinstance(metrics, TraceabilityMetrics)
        assert metrics.total_principles == 1
        assert metrics.total_rules == 1
        assert metrics.total_relationships == 1
        assert metrics.coverage_percentage == 100.0  # 1/1 principles covered
        assert metrics.avg_impact_score == 0.8
        assert len(metrics.orphaned_principles) == 0
        assert len(metrics.orphaned_rules) == 0
        assert sample_principle.principle_id in metrics.principle_influence_scores

    @pytest.mark.asyncio
    async def test_calculate_traceability_coverage_with_orphans(self, tracer):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Test traceability coverage with orphaned principles and rules."""
        # Add orphaned principle (no rules)
        orphaned_principle = ConstitutionalPrinciple(
            principle_id="ORPHANED-PRIN",
            title="Orphaned Principle",
            description="Principle without rules",
            category="test",
            priority=5,
            constitutional_hash="cdd01ef066bc6cf2",
            created_at=datetime.now(timezone.utc),
            last_updated=datetime.now(timezone.utc),
        )
        await tracer.add_principle(orphaned_principle)

        # Add orphaned rule (no principles)
        orphaned_rule = GovernanceRule(
            rule_id="ORPHANED-RULE",
            title="Orphaned Rule",
            content="Rule without principles",
            category="test",
            policy_id="POL-ORPHAN",
            enforcement_level="advisory",
            created_at=datetime.now(timezone.utc),
            last_updated=datetime.now(timezone.utc),
        )
        await tracer.add_rule(orphaned_rule)

        # Calculate coverage
        metrics = await tracer.calculate_traceability_coverage()

        assert metrics.total_principles == 1
        assert metrics.total_rules == 1
        assert metrics.total_relationships == 0
        assert metrics.coverage_percentage == 0.0  # No principles covered
        assert "ORPHANED-PRIN" in metrics.orphaned_principles
        assert "ORPHANED-RULE" in metrics.orphaned_rules


class TestPrincipleTracerIntegration:
    """Integration tests for principle tracer."""

    @pytest.mark.asyncio
    async def test_global_tracer_singleton(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Test global tracer singleton pattern."""
        tracer1 = await get_principle_tracer()
        tracer2 = await get_principle_tracer()

        # Should return same instance
        assert tracer1 is tracer2

    @pytest.mark.asyncio
    async def test_generate_traceability_report(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Test comprehensive traceability report generation."""
        tracer = await get_principle_tracer()

        # Add some test data
        principle = ConstitutionalPrinciple(
            principle_id="REPORT-PRIN",
            title="Report Test Principle",
            description="Principle for report testing",
            category="test",
            priority=7,
            constitutional_hash="cdd01ef066bc6cf2",
            created_at=datetime.now(timezone.utc),
            last_updated=datetime.now(timezone.utc),
        )
        await tracer.add_principle(principle)

        rule = GovernanceRule(
            rule_id="REPORT-RULE",
            title="Report Test Rule",
            content="Rule for report testing",
            category="test",
            policy_id="POL-REPORT",
            enforcement_level="moderate",
            created_at=datetime.now(timezone.utc),
            last_updated=datetime.now(timezone.utc),
            usage_frequency=30,
        )
        await tracer.add_rule(rule)

        relationship = PrincipleRuleRelationship(
            principle_id=principle.principle_id,
            rule_id=rule.rule_id,
            relationship_type=RelationshipType.DIRECT_IMPLEMENTATION,
            impact_score=0.75,
            confidence=0.85,
            reasoning="Report test relationship",
            evidence=["report_test"],
            created_at=datetime.now(timezone.utc),
            last_validated=datetime.now(timezone.utc),
        )
        await tracer.add_relationship(relationship)

        # Generate report
        report = await tracer.generate_traceability_report()

        # Verify report structure
        required_sections = [
            "report_metadata",
            "traceability_metrics",
            "coverage_analysis",
            "high_impact_analysis",
            "principle_influence_analysis",
            "graph_analysis",
            "performance_metrics",
            "recommendations",
        ]

        for section in required_sections:
            assert section in report

        # Verify metadata
        assert report["report_metadata"]["constitutional_hash"] == "cdd01ef066bc6cf2"
        assert "generated_at" in report["report_metadata"]

        # Verify metrics
        assert report["traceability_metrics"]["total_principles"] >= 1
        assert report["traceability_metrics"]["total_rules"] >= 1
        assert report["traceability_metrics"]["total_relationships"] >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=principle_tracer", "--cov-report=term-missing"])
