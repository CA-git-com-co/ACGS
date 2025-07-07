"""
Policy Management Domain Entities
Constitutional Hash: cdd01ef066bc6cf2

Core entities for policy lifecycle management and compliance.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Set
from enum import Enum

from services.shared.domain.base import (
    MultiTenantAggregateRoot,
    Entity,
    EntityId,
    TenantId
)
from .value_objects import (
    PolicyVersion,
    PolicyScope,
    ComplianceLevel,
    PolicyStatus,
    PolicyMetadata,
    ComplianceResult
)
from .events import (
    PolicyCreatedEvent,
    PolicyUpdatedEvent,
    PolicyActivatedEvent,
    PolicyDeactivatedEvent,
    ComplianceEvaluatedEvent,
    PolicyViolationDetectedEvent
)


class Policy(MultiTenantAggregateRoot):
    """
    Aggregate root representing a policy in the governance system.
    
    Policies define rules, constraints, and requirements that govern
    system behavior and decision-making.
    """
    
    def __init__(
        self,
        policy_id: EntityId,
        tenant_id: TenantId,
        policy_type: str,
        title: str,
        description: str,
        scope: PolicyScope,
        rules: List[Dict[str, Any]],
        metadata: PolicyMetadata
    ):
        super().__init__(policy_id, tenant_id)
        self.policy_type = policy_type
        self.title = title
        self.description = description
        self.scope = scope
        self._rules = rules.copy()
        self.metadata = metadata
        self._version = PolicyVersion(1, 0, 0)
        self._status = PolicyStatus.DRAFT
        self._effective_date: Optional[datetime] = None
        self._expiration_date: Optional[datetime] = None
        self._compliance_history: List[ComplianceResult] = []
        self._dependencies: Set[EntityId] = set()
        self._conflicts: Set[EntityId] = set()
    
    @property
    def version(self) -> PolicyVersion:
        """Get current policy version."""
        return self._version
    
    @property
    def status(self) -> PolicyStatus:
        """Get current policy status."""
        return self._status
    
    @property
    def rules(self) -> List[Dict[str, Any]]:
        """Get policy rules."""
        return self._rules.copy()
    
    @property
    def effective_date(self) -> Optional[datetime]:
        """Get policy effective date."""
        return self._effective_date
    
    @property
    def expiration_date(self) -> Optional[datetime]:
        """Get policy expiration date."""
        return self._expiration_date
    
    @property
    def is_active(self) -> bool:
        """Check if policy is currently active."""
        now = datetime.utcnow()
        return (
            self._status == PolicyStatus.ACTIVE and
            (self._effective_date is None or self._effective_date <= now) and
            (self._expiration_date is None or self._expiration_date > now)
        )
    
    @property
    def dependencies(self) -> Set[EntityId]:
        """Get policy dependencies."""
        return self._dependencies.copy()
    
    @property
    def conflicts(self) -> Set[EntityId]:
        """Get conflicting policies."""
        return self._conflicts.copy()
    
    def update_content(
        self, 
        title: str, 
        description: str, 
        rules: List[Dict[str, Any]]
    ) -> None:
        """Update policy content."""
        if self._status == PolicyStatus.ACTIVE:
            raise ValueError("Cannot update active policy without versioning")
        
        old_title = self.title
        old_rules = self._rules.copy()
        
        self.title = title
        self.description = description
        self._rules = rules.copy()
        
        self._add_domain_event(PolicyUpdatedEvent(
            aggregate_id=self.id,
            policy_id=self.id,
            version=self._version.to_string(),
            changes={
                "title": {"old": old_title, "new": title},
                "rules_updated": True,
                "rule_count": len(rules)
            },
            occurred_at=datetime.utcnow()
        ))
    
    def create_new_version(
        self, 
        version_type: str = "minor"
    ) -> 'Policy':
        """Create new version of the policy."""
        if version_type == "major":
            new_version = PolicyVersion(
                self._version.major + 1, 0, 0
            )
        elif version_type == "minor":
            new_version = PolicyVersion(
                self._version.major, self._version.minor + 1, 0
            )
        else:  # patch
            new_version = PolicyVersion(
                self._version.major, self._version.minor, self._version.patch + 1
            )
        
        # Create new policy instance with incremented version
        new_policy = Policy(
            policy_id=EntityId(),  # New ID for new version
            tenant_id=self.tenant_id,
            policy_type=self.policy_type,
            title=self.title,
            description=self.description,
            scope=self.scope,
            rules=self._rules,
            metadata=self.metadata
        )
        new_policy._version = new_version
        
        return new_policy
    
    def activate(
        self, 
        effective_date: Optional[datetime] = None,
        expiration_date: Optional[datetime] = None
    ) -> None:
        """Activate the policy."""
        if self._status == PolicyStatus.ACTIVE:
            raise ValueError("Policy is already active")
        
        if self._status == PolicyStatus.DEPRECATED:
            raise ValueError("Cannot activate deprecated policy")
        
        self._status = PolicyStatus.ACTIVE
        self._effective_date = effective_date or datetime.utcnow()
        self._expiration_date = expiration_date
        
        self._add_domain_event(PolicyActivatedEvent(
            aggregate_id=self.id,
            policy_id=self.id,
            version=self._version.to_string(),
            effective_date=self._effective_date,
            expiration_date=self._expiration_date,
            occurred_at=datetime.utcnow()
        ))
    
    def deactivate(self, reason: str) -> None:
        """Deactivate the policy."""
        if self._status != PolicyStatus.ACTIVE:
            raise ValueError("Policy is not active")
        
        self._status = PolicyStatus.INACTIVE
        
        self._add_domain_event(PolicyDeactivatedEvent(
            aggregate_id=self.id,
            policy_id=self.id,
            version=self._version.to_string(),
            reason=reason,
            occurred_at=datetime.utcnow()
        ))
    
    def deprecate(self) -> None:
        """Mark policy as deprecated."""
        self._status = PolicyStatus.DEPRECATED
    
    def add_dependency(self, policy_id: EntityId) -> None:
        """Add policy dependency."""
        if policy_id == self.id:
            raise ValueError("Policy cannot depend on itself")
        
        self._dependencies.add(policy_id)
    
    def remove_dependency(self, policy_id: EntityId) -> None:
        """Remove policy dependency."""
        self._dependencies.discard(policy_id)
    
    def add_conflict(self, policy_id: EntityId) -> None:
        """Add conflicting policy."""
        if policy_id == self.id:
            raise ValueError("Policy cannot conflict with itself")
        
        self._conflicts.add(policy_id)
    
    def remove_conflict(self, policy_id: EntityId) -> None:
        """Remove policy conflict."""
        self._conflicts.discard(policy_id)
    
    def evaluate_compliance(
        self, 
        context: Dict[str, Any]
    ) -> ComplianceResult:
        """Evaluate compliance against this policy."""
        if not self.is_active:
            return ComplianceResult(
                policy_id=self.id,
                compliance_level=ComplianceLevel.NOT_APPLICABLE,
                evaluation_score=0.0,
                violations=[],
                recommendations=[],
                context_data=context
            )
        
        violations = []
        recommendations = []
        evaluation_score = 1.0
        
        # Evaluate each rule
        for rule in self._rules:
            rule_result = self._evaluate_rule(rule, context)
            if not rule_result["compliant"]:
                violations.append(rule_result)
                evaluation_score -= rule_result.get("severity", 0.1)
        
        # Determine compliance level
        if evaluation_score >= 0.9:
            compliance_level = ComplianceLevel.FULLY_COMPLIANT
        elif evaluation_score >= 0.7:
            compliance_level = ComplianceLevel.PARTIALLY_COMPLIANT
        elif evaluation_score >= 0.5:
            compliance_level = ComplianceLevel.NON_COMPLIANT
        else:
            compliance_level = ComplianceLevel.SEVERELY_NON_COMPLIANT
        
        result = ComplianceResult(
            policy_id=self.id,
            compliance_level=compliance_level,
            evaluation_score=max(0.0, evaluation_score),
            violations=violations,
            recommendations=recommendations,
            context_data=context
        )
        
        # Store compliance result
        self._compliance_history.append(result)
        
        # Raise domain event
        self._add_domain_event(ComplianceEvaluatedEvent(
            aggregate_id=self.id,
            policy_id=self.id,
            compliance_result=result.to_dict(),
            occurred_at=datetime.utcnow()
        ))
        
        # Raise violation event if needed
        if violations:
            self._add_domain_event(PolicyViolationDetectedEvent(
                aggregate_id=self.id,
                policy_id=self.id,
                violations=violations,
                severity=self._calculate_violation_severity(violations),
                occurred_at=datetime.utcnow()
            ))
        
        return result
    
    def get_compliance_history(
        self, 
        limit: Optional[int] = None
    ) -> List[ComplianceResult]:
        """Get compliance evaluation history."""
        history = sorted(
            self._compliance_history, 
            key=lambda x: x.evaluated_at, 
            reverse=True
        )
        return history[:limit] if limit else history
    
    def get_compliance_trends(self) -> Dict[str, Any]:
        """Get compliance trends over time."""
        if not self._compliance_history:
            return {"trend": "no_data", "average_score": 0.0}
        
        scores = [result.evaluation_score for result in self._compliance_history]
        recent_scores = scores[-10:]  # Last 10 evaluations
        
        if len(recent_scores) < 2:
            return {"trend": "insufficient_data", "average_score": scores[0]}
        
        # Calculate trend
        early_avg = sum(recent_scores[:len(recent_scores)//2]) / (len(recent_scores)//2)
        recent_avg = sum(recent_scores[len(recent_scores)//2:]) / (len(recent_scores) - len(recent_scores)//2)
        
        if recent_avg > early_avg + 0.1:
            trend = "improving"
        elif recent_avg < early_avg - 0.1:
            trend = "declining"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "average_score": sum(scores) / len(scores),
            "recent_average": recent_avg,
            "evaluation_count": len(self._compliance_history)
        }
    
    def _evaluate_rule(self, rule: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a single rule against context."""
        # Simplified rule evaluation - in practice this would be more sophisticated
        rule_type = rule.get("type", "unknown")
        
        if rule_type == "threshold":
            return self._evaluate_threshold_rule(rule, context)
        elif rule_type == "conditional":
            return self._evaluate_conditional_rule(rule, context)
        elif rule_type == "constraint":
            return self._evaluate_constraint_rule(rule, context)
        else:
            return {
                "rule_id": rule.get("id", "unknown"),
                "compliant": True,
                "message": "Rule type not implemented"
            }
    
    def _evaluate_threshold_rule(self, rule: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate threshold-based rule."""
        field = rule.get("field")
        operator = rule.get("operator", "<=")
        threshold = rule.get("threshold")
        
        if field not in context:
            return {
                "rule_id": rule.get("id"),
                "compliant": False,
                "message": f"Required field '{field}' not found in context",
                "severity": 0.3
            }
        
        value = context[field]
        
        if operator == "<=":
            compliant = value <= threshold
        elif operator == ">=":
            compliant = value >= threshold
        elif operator == "<":
            compliant = value < threshold
        elif operator == ">":
            compliant = value > threshold
        elif operator == "==":
            compliant = value == threshold
        else:
            compliant = True
        
        return {
            "rule_id": rule.get("id"),
            "compliant": compliant,
            "message": f"Value {value} {operator} {threshold}",
            "severity": rule.get("severity", 0.2)
        }
    
    def _evaluate_conditional_rule(self, rule: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate conditional rule."""
        condition = rule.get("condition")
        # Simplified conditional evaluation
        return {
            "rule_id": rule.get("id"),
            "compliant": True,
            "message": "Conditional rule evaluation simplified"
        }
    
    def _evaluate_constraint_rule(self, rule: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate constraint rule."""
        constraint = rule.get("constraint")
        # Simplified constraint evaluation
        return {
            "rule_id": rule.get("id"),
            "compliant": True,
            "message": "Constraint rule evaluation simplified"
        }
    
    def _calculate_violation_severity(self, violations: List[Dict[str, Any]]) -> str:
        """Calculate overall violation severity."""
        if not violations:
            return "none"
        
        max_severity = max(v.get("severity", 0.0) for v in violations)
        
        if max_severity >= 0.8:
            return "critical"
        elif max_severity >= 0.6:
            return "high"
        elif max_severity >= 0.4:
            return "medium"
        else:
            return "low"


class PolicySet(MultiTenantAggregateRoot):
    """
    Aggregate root representing a collection of related policies.
    
    Policy sets help organize and manage groups of policies that
    work together to achieve specific governance objectives.
    """
    
    def __init__(
        self,
        set_id: EntityId,
        tenant_id: TenantId,
        name: str,
        description: str,
        category: str
    ):
        super().__init__(set_id, tenant_id)
        self.name = name
        self.description = description
        self.category = category
        self._policies: Set[EntityId] = set()
        self._status = "active"
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    @property
    def policies(self) -> Set[EntityId]:
        """Get policies in this set."""
        return self._policies.copy()
    
    @property
    def status(self) -> str:
        """Get policy set status."""
        return self._status
    
    def add_policy(self, policy_id: EntityId) -> None:
        """Add policy to the set."""
        self._policies.add(policy_id)
        self.updated_at = datetime.utcnow()
    
    def remove_policy(self, policy_id: EntityId) -> None:
        """Remove policy from the set."""
        self._policies.discard(policy_id)
        self.updated_at = datetime.utcnow()
    
    def activate(self) -> None:
        """Activate the policy set."""
        self._status = "active"
        self.updated_at = datetime.utcnow()
    
    def deactivate(self) -> None:
        """Deactivate the policy set."""
        self._status = "inactive"
        self.updated_at = datetime.utcnow()
    
    def get_policy_count(self) -> int:
        """Get number of policies in the set."""
        return len(self._policies)