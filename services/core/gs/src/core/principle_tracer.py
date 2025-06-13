"""
Principle-Rule Traceability Enhancement for ACGS-1 Governance Synthesis
Target: 100% traceability coverage with quantified impact measurement

This module implements a sophisticated traceability system that maps constitutional
principles to governance rules using directed graph representation and impact scoring.

Key Features:
- Directed graph representation of principle-rule relationships
- Impact scoring algorithm (0.0-1.0 scale) based on frequency and severity
- Principle influence measurement across governance workflows
- High-impact rule identification (affecting >5 constitutional principles)
- Graph visualization capabilities for governance dashboard
- Integration with existing Policy Synthesis Engine
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Set, Any
import hashlib
import json
from enum import Enum
import networkx as nx
import numpy as np
from collections import defaultdict, Counter

# Prometheus metrics
try:
    from prometheus_client import Counter as PrometheusCounter, Histogram, Gauge
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

# Policy Synthesis Engine integration
try:
    from services.core.gs.src.core.policy_synthesis_engine import PolicySynthesisEngine
    POLICY_ENGINE_AVAILABLE = True
except ImportError:
    POLICY_ENGINE_AVAILABLE = False

logger = logging.getLogger(__name__)

# Prometheus metrics for traceability
if PROMETHEUS_AVAILABLE:
    TRACEABILITY_COVERAGE = Gauge('gs_traceability_coverage_percent', 'Principle-rule traceability coverage')
    IMPACT_SCORE_DISTRIBUTION = Histogram('gs_impact_score_distribution', 'Distribution of impact scores')
    HIGH_IMPACT_RULES = Gauge('gs_high_impact_rules_count', 'Number of high-impact rules')
    PRINCIPLE_INFLUENCE = Gauge('gs_principle_influence_score', 'Principle influence measurement')


class RelationshipType(Enum):
    """Types of principle-rule relationships."""
    DIRECT_IMPLEMENTATION = "direct_implementation"  # Rule directly implements principle
    INDIRECT_SUPPORT = "indirect_support"  # Rule supports principle indirectly
    CONSTRAINT_ENFORCEMENT = "constraint_enforcement"  # Rule enforces principle constraints
    CONFLICT_RESOLUTION = "conflict_resolution"  # Rule resolves principle conflicts
    DERIVED_REQUIREMENT = "derived_requirement"  # Rule derived from principle requirements


class ImpactLevel(Enum):
    """Impact level classifications."""
    CRITICAL = "critical"  # 0.8-1.0
    HIGH = "high"  # 0.6-0.8
    MEDIUM = "medium"  # 0.4-0.6
    LOW = "low"  # 0.2-0.4
    MINIMAL = "minimal"  # 0.0-0.2


@dataclass
class ConstitutionalPrinciple:
    """Constitutional principle representation."""
    principle_id: str
    title: str
    description: str
    category: str
    priority: int  # 1-10, higher = more important
    constitutional_hash: str
    created_at: datetime
    last_updated: datetime


@dataclass
class GovernanceRule:
    """Governance rule representation."""
    rule_id: str
    title: str
    content: str
    category: str
    policy_id: Optional[str]
    enforcement_level: str  # strict, moderate, advisory
    created_at: datetime
    last_updated: datetime
    usage_frequency: int = 0


@dataclass
class PrincipleRuleRelationship:
    """Relationship between principle and rule."""
    principle_id: str
    rule_id: str
    relationship_type: RelationshipType
    impact_score: float  # 0.0-1.0
    confidence: float  # 0.0-1.0
    reasoning: str
    evidence: List[str]
    created_at: datetime
    last_validated: datetime


@dataclass
class TraceabilityMetrics:
    """Traceability analysis metrics."""
    total_principles: int
    total_rules: int
    total_relationships: int
    coverage_percentage: float
    avg_impact_score: float
    high_impact_rules_count: int
    orphaned_principles: List[str]  # Principles with no rules
    orphaned_rules: List[str]  # Rules with no principles
    principle_influence_scores: Dict[str, float]


class PrincipleTracer:
    """
    Principle-rule traceability system with directed graph representation.
    
    Features:
    - Directed graph mapping of principle-rule relationships
    - Impact scoring based on frequency, severity, and influence
    - Comprehensive traceability analysis and reporting
    - Integration with Policy Synthesis Engine
    """
    
    def __init__(
        self,
        constitutional_hash: str = "cdd01ef066bc6cf2",
        impact_threshold: float = 0.5,
        high_impact_principle_threshold: int = 5
    ):
        self.constitutional_hash = constitutional_hash
        self.impact_threshold = impact_threshold
        self.high_impact_principle_threshold = high_impact_principle_threshold
        
        # Graph representation
        self.traceability_graph = nx.DiGraph()
        
        # Data storage
        self.principles: Dict[str, ConstitutionalPrinciple] = {}
        self.rules: Dict[str, GovernanceRule] = {}
        self.relationships: Dict[Tuple[str, str], PrincipleRuleRelationship] = {}
        
        # Performance tracking
        self.analysis_stats = {
            "total_analyses": 0,
            "avg_analysis_time_ms": 0.0,
            "last_analysis_timestamp": None,
            "coverage_history": []
        }
        
        # Policy engine integration
        self.policy_engine = None
        
        logger.info(f"Initialized PrincipleTracer with constitutional_hash={constitutional_hash}")
    
    async def initialize_policy_engine(self):
        """Initialize Policy Synthesis Engine integration."""
        if POLICY_ENGINE_AVAILABLE:
            try:
                self.policy_engine = PolicySynthesisEngine()
                await self.policy_engine.initialize()
                logger.info("Policy Synthesis Engine integration initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Policy Synthesis Engine: {e}")
                self.policy_engine = None
        else:
            logger.warning("Policy Synthesis Engine not available")
    
    async def add_principle(self, principle: ConstitutionalPrinciple) -> bool:
        """Add constitutional principle to traceability system."""
        try:
            self.principles[principle.principle_id] = principle
            
            # Add to graph
            self.traceability_graph.add_node(
                principle.principle_id,
                node_type="principle",
                title=principle.title,
                category=principle.category,
                priority=principle.priority
            )
            
            logger.debug(f"Added principle {principle.principle_id}: {principle.title}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add principle {principle.principle_id}: {e}")
            return False
    
    async def add_rule(self, rule: GovernanceRule) -> bool:
        """Add governance rule to traceability system."""
        try:
            self.rules[rule.rule_id] = rule
            
            # Add to graph
            self.traceability_graph.add_node(
                rule.rule_id,
                node_type="rule",
                title=rule.title,
                category=rule.category,
                enforcement_level=rule.enforcement_level,
                usage_frequency=rule.usage_frequency
            )
            
            logger.debug(f"Added rule {rule.rule_id}: {rule.title}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add rule {rule.rule_id}: {e}")
            return False
    
    async def add_relationship(self, relationship: PrincipleRuleRelationship) -> bool:
        """Add principle-rule relationship to traceability system."""
        try:
            # Validate that both principle and rule exist
            if relationship.principle_id not in self.principles:
                logger.error(f"Principle {relationship.principle_id} not found")
                return False
            
            if relationship.rule_id not in self.rules:
                logger.error(f"Rule {relationship.rule_id} not found")
                return False
            
            # Store relationship
            key = (relationship.principle_id, relationship.rule_id)
            self.relationships[key] = relationship
            
            # Add edge to graph
            self.traceability_graph.add_edge(
                relationship.principle_id,
                relationship.rule_id,
                relationship_type=relationship.relationship_type.value,
                impact_score=relationship.impact_score,
                confidence=relationship.confidence,
                reasoning=relationship.reasoning
            )
            
            logger.debug(f"Added relationship: {relationship.principle_id} -> {relationship.rule_id} "
                        f"(impact: {relationship.impact_score:.3f})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add relationship: {e}")
            return False
    
    def calculate_impact_score(
        self,
        principle: ConstitutionalPrinciple,
        rule: GovernanceRule,
        relationship_type: RelationshipType,
        usage_frequency: int = 0,
        severity_indicators: List[str] = None
    ) -> float:
        """
        Calculate impact score for principle-rule relationship.
        
        Impact score factors:
        - Principle priority (weight: 0.3)
        - Rule usage frequency (weight: 0.2)
        - Relationship type strength (weight: 0.3)
        - Severity indicators (weight: 0.2)
        """
        try:
            # Principle priority component (0.0-1.0)
            priority_score = principle.priority / 10.0
            
            # Usage frequency component (0.0-1.0)
            # Normalize frequency using log scale for better distribution
            max_frequency = 1000  # Assumed maximum frequency
            frequency_score = min(1.0, np.log1p(usage_frequency) / np.log1p(max_frequency))
            
            # Relationship type strength
            type_weights = {
                RelationshipType.DIRECT_IMPLEMENTATION: 1.0,
                RelationshipType.CONSTRAINT_ENFORCEMENT: 0.9,
                RelationshipType.DERIVED_REQUIREMENT: 0.8,
                RelationshipType.CONFLICT_RESOLUTION: 0.7,
                RelationshipType.INDIRECT_SUPPORT: 0.5
            }
            type_score = type_weights.get(relationship_type, 0.5)
            
            # Severity indicators component
            severity_score = 0.5  # Default
            if severity_indicators:
                critical_indicators = ["safety", "security", "constitutional", "violation", "breach"]
                severity_count = sum(1 for indicator in severity_indicators 
                                   if any(critical in indicator.lower() for critical in critical_indicators))
                severity_score = min(1.0, 0.3 + (severity_count * 0.2))
            
            # Weighted combination
            impact_score = (
                priority_score * 0.3 +
                frequency_score * 0.2 +
                type_score * 0.3 +
                severity_score * 0.2
            )
            
            return min(1.0, max(0.0, impact_score))
            
        except Exception as e:
            logger.error(f"Failed to calculate impact score: {e}")
            return 0.5  # Default moderate impact
    
    def get_impact_level(self, impact_score: float) -> ImpactLevel:
        """Classify impact score into impact level."""
        if impact_score >= 0.8:
            return ImpactLevel.CRITICAL
        elif impact_score >= 0.6:
            return ImpactLevel.HIGH
        elif impact_score >= 0.4:
            return ImpactLevel.MEDIUM
        elif impact_score >= 0.2:
            return ImpactLevel.LOW
        else:
            return ImpactLevel.MINIMAL
    
    async def analyze_principle_influence(self, principle_id: str) -> Dict[str, Any]:
        """Analyze influence of a specific principle across governance workflows."""
        try:
            if principle_id not in self.principles:
                raise ValueError(f"Principle {principle_id} not found")
            
            principle = self.principles[principle_id]
            
            # Get all rules connected to this principle
            connected_rules = []
            total_impact = 0.0
            impact_distribution = defaultdict(int)
            
            for (p_id, r_id), relationship in self.relationships.items():
                if p_id == principle_id:
                    connected_rules.append(r_id)
                    total_impact += relationship.impact_score
                    impact_level = self.get_impact_level(relationship.impact_score)
                    impact_distribution[impact_level.value] += 1
            
            # Calculate influence metrics
            rule_count = len(connected_rules)
            avg_impact = total_impact / max(1, rule_count)
            
            # Calculate workflow coverage
            workflow_categories = set()
            for rule_id in connected_rules:
                if rule_id in self.rules:
                    workflow_categories.add(self.rules[rule_id].category)
            
            # Calculate influence score (0.0-1.0)
            influence_score = min(1.0, (
                (rule_count / max(1, len(self.rules))) * 0.4 +  # Coverage factor
                avg_impact * 0.4 +  # Impact factor
                (len(workflow_categories) / 10.0) * 0.2  # Diversity factor
            ))
            
            return {
                "principle_id": principle_id,
                "principle_title": principle.title,
                "connected_rules_count": rule_count,
                "total_impact_score": total_impact,
                "average_impact_score": avg_impact,
                "influence_score": influence_score,
                "workflow_coverage": len(workflow_categories),
                "impact_distribution": dict(impact_distribution),
                "connected_rules": connected_rules,
                "analysis_timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze principle influence for {principle_id}: {e}")
            return {
                "principle_id": principle_id,
                "error": str(e),
                "influence_score": 0.0
            }

    async def identify_high_impact_rules(self) -> List[Dict[str, Any]]:
        """Identify rules that affect more than the threshold number of principles."""
        try:
            rule_principle_count = defaultdict(list)
            rule_total_impact = defaultdict(float)

            # Count principles affected by each rule
            for (p_id, r_id), relationship in self.relationships.items():
                rule_principle_count[r_id].append(p_id)
                rule_total_impact[r_id] += relationship.impact_score

            high_impact_rules = []

            for rule_id, affected_principles in rule_principle_count.items():
                if len(affected_principles) >= self.high_impact_principle_threshold:
                    rule = self.rules.get(rule_id)
                    if rule:
                        avg_impact = rule_total_impact[rule_id] / len(affected_principles)

                        high_impact_rules.append({
                            "rule_id": rule_id,
                            "rule_title": rule.title,
                            "affected_principles_count": len(affected_principles),
                            "affected_principles": affected_principles,
                            "total_impact_score": rule_total_impact[rule_id],
                            "average_impact_score": avg_impact,
                            "rule_category": rule.category,
                            "enforcement_level": rule.enforcement_level,
                            "usage_frequency": rule.usage_frequency
                        })

            # Sort by number of affected principles (descending)
            high_impact_rules.sort(key=lambda x: x["affected_principles_count"], reverse=True)

            # Update Prometheus metrics
            if PROMETHEUS_AVAILABLE:
                HIGH_IMPACT_RULES.set(len(high_impact_rules))

            logger.info(f"Identified {len(high_impact_rules)} high-impact rules")
            return high_impact_rules

        except Exception as e:
            logger.error(f"Failed to identify high-impact rules: {e}")
            return []

    async def calculate_traceability_coverage(self) -> TraceabilityMetrics:
        """Calculate comprehensive traceability coverage metrics."""
        start_time = time.time()

        try:
            total_principles = len(self.principles)
            total_rules = len(self.rules)
            total_relationships = len(self.relationships)

            # Find orphaned principles (no connected rules)
            principles_with_rules = set()
            rules_with_principles = set()
            impact_scores = []

            for (p_id, r_id), relationship in self.relationships.items():
                principles_with_rules.add(p_id)
                rules_with_principles.add(r_id)
                impact_scores.append(relationship.impact_score)

            orphaned_principles = [p_id for p_id in self.principles.keys()
                                 if p_id not in principles_with_rules]
            orphaned_rules = [r_id for r_id in self.rules.keys()
                            if r_id not in rules_with_principles]

            # Calculate coverage percentage
            if total_principles > 0:
                coverage_percentage = (len(principles_with_rules) / total_principles) * 100.0
            else:
                coverage_percentage = 0.0

            # Calculate average impact score
            avg_impact_score = np.mean(impact_scores) if impact_scores else 0.0

            # Calculate principle influence scores
            principle_influence_scores = {}
            for principle_id in self.principles.keys():
                influence_analysis = await self.analyze_principle_influence(principle_id)
                principle_influence_scores[principle_id] = influence_analysis.get("influence_score", 0.0)

            # Identify high-impact rules
            high_impact_rules = await self.identify_high_impact_rules()

            metrics = TraceabilityMetrics(
                total_principles=total_principles,
                total_rules=total_rules,
                total_relationships=total_relationships,
                coverage_percentage=coverage_percentage,
                avg_impact_score=avg_impact_score,
                high_impact_rules_count=len(high_impact_rules),
                orphaned_principles=orphaned_principles,
                orphaned_rules=orphaned_rules,
                principle_influence_scores=principle_influence_scores
            )

            # Update performance stats
            analysis_time = (time.time() - start_time) * 1000
            self.analysis_stats["total_analyses"] += 1
            self.analysis_stats["avg_analysis_time_ms"] = (
                (self.analysis_stats["avg_analysis_time_ms"] * (self.analysis_stats["total_analyses"] - 1) +
                 analysis_time) / self.analysis_stats["total_analyses"]
            )
            self.analysis_stats["last_analysis_timestamp"] = datetime.now(timezone.utc)
            self.analysis_stats["coverage_history"].append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "coverage_percentage": coverage_percentage
            })

            # Keep only recent history
            if len(self.analysis_stats["coverage_history"]) > 100:
                self.analysis_stats["coverage_history"] = self.analysis_stats["coverage_history"][-100:]

            # Update Prometheus metrics
            if PROMETHEUS_AVAILABLE:
                TRACEABILITY_COVERAGE.set(coverage_percentage)
                if impact_scores:
                    for score in impact_scores:
                        IMPACT_SCORE_DISTRIBUTION.observe(score)

                # Update principle influence metrics
                if principle_influence_scores:
                    avg_influence = np.mean(list(principle_influence_scores.values()))
                    PRINCIPLE_INFLUENCE.set(avg_influence)

            logger.info(f"Traceability analysis completed: {coverage_percentage:.1f}% coverage, "
                       f"{len(high_impact_rules)} high-impact rules, analysis_time={analysis_time:.1f}ms")

            return metrics

        except Exception as e:
            logger.error(f"Failed to calculate traceability coverage: {e}")
            return TraceabilityMetrics(
                total_principles=0, total_rules=0, total_relationships=0,
                coverage_percentage=0.0, avg_impact_score=0.0, high_impact_rules_count=0,
                orphaned_principles=[], orphaned_rules=[], principle_influence_scores={}
            )

    async def generate_traceability_report(self) -> Dict[str, Any]:
        """Generate comprehensive traceability analysis report."""
        try:
            # Calculate current metrics
            metrics = await self.calculate_traceability_coverage()

            # Get high-impact rules
            high_impact_rules = await self.identify_high_impact_rules()

            # Analyze principle influence for top principles
            top_principles = sorted(
                metrics.principle_influence_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]

            principle_analyses = []
            for principle_id, influence_score in top_principles:
                analysis = await self.analyze_principle_influence(principle_id)
                principle_analyses.append(analysis)

            # Generate graph statistics
            graph_stats = {
                "nodes": self.traceability_graph.number_of_nodes(),
                "edges": self.traceability_graph.number_of_edges(),
                "density": nx.density(self.traceability_graph),
                "is_connected": nx.is_weakly_connected(self.traceability_graph),
                "strongly_connected_components": nx.number_strongly_connected_components(self.traceability_graph)
            }

            # Compile comprehensive report
            report = {
                "report_metadata": {
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "constitutional_hash": self.constitutional_hash,
                    "analysis_version": "1.0.0",
                    "target_coverage": 100.0
                },
                "traceability_metrics": {
                    "total_principles": metrics.total_principles,
                    "total_rules": metrics.total_rules,
                    "total_relationships": metrics.total_relationships,
                    "coverage_percentage": metrics.coverage_percentage,
                    "avg_impact_score": metrics.avg_impact_score,
                    "high_impact_rules_count": metrics.high_impact_rules_count
                },
                "coverage_analysis": {
                    "covered_principles": metrics.total_principles - len(metrics.orphaned_principles),
                    "covered_rules": metrics.total_rules - len(metrics.orphaned_rules),
                    "orphaned_principles": metrics.orphaned_principles,
                    "orphaned_rules": metrics.orphaned_rules,
                    "coverage_target_met": metrics.coverage_percentage >= 95.0
                },
                "high_impact_analysis": {
                    "high_impact_rules": high_impact_rules[:10],  # Top 10
                    "impact_threshold": self.high_impact_principle_threshold,
                    "total_high_impact_rules": len(high_impact_rules)
                },
                "principle_influence_analysis": {
                    "top_influential_principles": principle_analyses,
                    "avg_influence_score": np.mean(list(metrics.principle_influence_scores.values())) if metrics.principle_influence_scores else 0.0,
                    "influence_distribution": self._calculate_influence_distribution(metrics.principle_influence_scores)
                },
                "graph_analysis": graph_stats,
                "performance_metrics": {
                    "total_analyses": self.analysis_stats["total_analyses"],
                    "avg_analysis_time_ms": self.analysis_stats["avg_analysis_time_ms"],
                    "last_analysis": self.analysis_stats["last_analysis_timestamp"].isoformat() if self.analysis_stats["last_analysis_timestamp"] else None,
                    "coverage_trend": self._calculate_coverage_trend()
                },
                "recommendations": self._generate_recommendations(metrics, high_impact_rules)
            }

            return report

        except Exception as e:
            logger.error(f"Failed to generate traceability report: {e}")
            return {
                "error": str(e),
                "generated_at": datetime.now(timezone.utc).isoformat()
            }

    def _calculate_influence_distribution(self, influence_scores: Dict[str, float]) -> Dict[str, int]:
        """Calculate distribution of influence scores."""
        distribution = {"high": 0, "medium": 0, "low": 0}

        for score in influence_scores.values():
            if score >= 0.7:
                distribution["high"] += 1
            elif score >= 0.4:
                distribution["medium"] += 1
            else:
                distribution["low"] += 1

        return distribution

    def _calculate_coverage_trend(self) -> str:
        """Calculate coverage trend from history."""
        history = self.analysis_stats["coverage_history"]
        if len(history) < 2:
            return "insufficient_data"

        recent_coverage = [entry["coverage_percentage"] for entry in history[-5:]]
        if len(recent_coverage) < 2:
            return "stable"

        trend = np.polyfit(range(len(recent_coverage)), recent_coverage, 1)[0]

        if trend > 1.0:
            return "improving"
        elif trend < -1.0:
            return "declining"
        else:
            return "stable"

    def _generate_recommendations(self, metrics: TraceabilityMetrics, high_impact_rules: List[Dict]) -> List[str]:
        """Generate actionable recommendations based on analysis."""
        recommendations = []

        # Coverage recommendations
        if metrics.coverage_percentage < 95.0:
            recommendations.append(f"Improve traceability coverage from {metrics.coverage_percentage:.1f}% to target 100%")

        if metrics.orphaned_principles:
            recommendations.append(f"Address {len(metrics.orphaned_principles)} orphaned principles without implementing rules")

        if metrics.orphaned_rules:
            recommendations.append(f"Review {len(metrics.orphaned_rules)} orphaned rules without constitutional basis")

        # Impact recommendations
        if metrics.avg_impact_score < 0.6:
            recommendations.append(f"Strengthen principle-rule relationships (avg impact: {metrics.avg_impact_score:.3f})")

        if len(high_impact_rules) > 10:
            recommendations.append(f"Review {len(high_impact_rules)} high-impact rules for potential decomposition")

        # Performance recommendations
        if self.analysis_stats["avg_analysis_time_ms"] > 1000:
            recommendations.append("Optimize traceability analysis performance (current: >1s)")

        return recommendations


# Global principle tracer instance
_principle_tracer: Optional[PrincipleTracer] = None


async def get_principle_tracer(
    constitutional_hash: str = "cdd01ef066bc6cf2",
    impact_threshold: float = 0.5
) -> PrincipleTracer:
    """Get or create global principle tracer instance."""
    global _principle_tracer

    if _principle_tracer is None:
        _principle_tracer = PrincipleTracer(
            constitutional_hash=constitutional_hash,
            impact_threshold=impact_threshold
        )
        await _principle_tracer.initialize_policy_engine()

    return _principle_tracer
