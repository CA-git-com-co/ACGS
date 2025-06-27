#!/usr/bin/env python3
"""
Constitutional Safety Framework
Enhanced safety and ethics guidelines for ACGS constitutional AI governance.
Implements defensive security practices for constitutional AI systems.
"""

import logging
import re
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class ThreatCategory(Enum):
    """Categories of constitutional threats."""
    CONSTITUTIONAL_BYPASS = "constitutional_bypass"
    GOVERNANCE_NULLIFICATION = "governance_nullification"
    DEMOCRATIC_SUBVERSION = "democratic_subversion"
    PRIVACY_VIOLATION = "privacy_violation"
    DISCRIMINATION = "discrimination"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    PROCEDURAL_VIOLATION = "procedural_violation"
    MALICIOUS_CONTENT = "malicious_content"


class RiskLevel(Enum):
    """Risk assessment levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ThreatPattern:
    """Definition of a constitutional threat pattern."""
    id: str
    category: ThreatCategory
    patterns: List[str]
    description: str
    risk_level: RiskLevel
    mitigation_strategy: str
    constitutional_principles_affected: List[str]


@dataclass
class SafetyViolation:
    """Detected safety violation."""
    violation_id: str
    threat_category: ThreatCategory
    risk_level: RiskLevel
    pattern_matched: str
    confidence_score: float
    affected_principles: List[str]
    mitigation_required: bool
    timestamp: float = field(default_factory=time.time)


class ConstitutionalSafetyValidator:
    """Validates content against constitutional safety principles."""
    
    def __init__(self):
        self.threat_patterns = self._initialize_threat_patterns()
        self.constitutional_principles = {
            "democratic_participation",
            "transparency_requirement", 
            "accountability_framework",
            "rights_protection",
            "separation_of_powers",
            "due_process",
            "equal_protection",
            "privacy_rights"
        }
    
    def _initialize_threat_patterns(self) -> List[ThreatPattern]:
        """Initialize constitutional threat detection patterns."""
        return [
            ThreatPattern(
                id="CONST_BYPASS_001",
                category=ThreatCategory.CONSTITUTIONAL_BYPASS,
                patterns=[
                    r"bypass\s+constitutional",
                    r"ignore\s+constitutional",
                    r"override\s+constitutional",
                    r"void\s+constitutional",
                    r"circumvent\s+constitutional",
                    r"suspend\s+constitutional"
                ],
                description="Attempts to bypass constitutional requirements",
                risk_level=RiskLevel.CRITICAL,
                mitigation_strategy="Block request and log violation",
                constitutional_principles_affected=["all"]
            ),
            
            ThreatPattern(
                id="GOV_NULL_001", 
                category=ThreatCategory.GOVERNANCE_NULLIFICATION,
                patterns=[
                    r"nullify\s+governance",
                    r"dissolve\s+government",
                    r"terminate\s+democracy",
                    r"abolish\s+democratic",
                    r"eliminate\s+oversight"
                ],
                description="Attempts to nullify governance structures",
                risk_level=RiskLevel.CRITICAL,
                mitigation_strategy="Block request and escalate to security team",
                constitutional_principles_affected=["democratic_participation", "separation_of_powers"]
            ),
            
            ThreatPattern(
                id="DEMO_SUBV_001",
                category=ThreatCategory.DEMOCRATIC_SUBVERSION,
                patterns=[
                    r"subvert\s+democracy",
                    r"undermine\s+voting",
                    r"manipulate\s+elections",
                    r"suppress\s+voters?",
                    r"disenfranchise",
                    r"rig\s+election"
                ],
                description="Attempts to subvert democratic processes",
                risk_level=RiskLevel.CRITICAL,
                mitigation_strategy="Block request and report to authorities",
                constitutional_principles_affected=["democratic_participation", "equal_protection"]
            ),
            
            ThreatPattern(
                id="PRIV_VIOL_001",
                category=ThreatCategory.PRIVACY_VIOLATION,
                patterns=[
                    r"access\s+private\s+data",
                    r"breach\s+privacy",
                    r"expose\s+personal\s+information",
                    r"unauthorized\s+surveillance",
                    r"violate\s+privacy\s+rights"
                ],
                description="Privacy rights violations",
                risk_level=RiskLevel.HIGH,
                mitigation_strategy="Block request and implement privacy review",
                constitutional_principles_affected=["privacy_rights", "due_process"]
            ),
            
            ThreatPattern(
                id="DISC_001",
                category=ThreatCategory.DISCRIMINATION,
                patterns=[
                    r"discriminate\s+against",
                    r"exclude\s+based\s+on",
                    r"deny\s+rights\s+to",
                    r"treat\s+unequally",
                    r"systematic\s+bias"
                ],
                description="Discriminatory policies or practices",
                risk_level=RiskLevel.HIGH,
                mitigation_strategy="Block request and conduct bias review",
                constitutional_principles_affected=["equal_protection", "rights_protection"]
            ),
            
            ThreatPattern(
                id="UNAUTH_ACCESS_001",
                category=ThreatCategory.UNAUTHORIZED_ACCESS,
                patterns=[
                    r"unauthorized\s+access",
                    r"escalate\s+privileges",
                    r"bypass\s+authentication",
                    r"admin\s+backdoor",
                    r"root\s+access"
                ],
                description="Unauthorized system access attempts",
                risk_level=RiskLevel.CRITICAL,
                mitigation_strategy="Block immediately and alert security",
                constitutional_principles_affected=["accountability_framework", "transparency_requirement"]
            ),
            
            ThreatPattern(
                id="PROC_VIOL_001",
                category=ThreatCategory.PROCEDURAL_VIOLATION,
                patterns=[
                    r"skip\s+due\s+process",
                    r"bypass\s+procedure",
                    r"ignore\s+protocol",
                    r"circumvent\s+oversight",
                    r"avoid\s+review"
                ],
                description="Procedural and due process violations",
                risk_level=RiskLevel.MEDIUM,
                mitigation_strategy="Require additional review and approval",
                constitutional_principles_affected=["due_process", "accountability_framework"]
            ),
            
            ThreatPattern(
                id="MAL_CONTENT_001",
                category=ThreatCategory.MALICIOUS_CONTENT,
                patterns=[
                    r"malicious\s+code",
                    r"harmful\s+payload",
                    r"exploit\s+vulnerability",
                    r"inject\s+script",
                    r"social\s+engineering"
                ],
                description="Malicious content designed to harm systems",
                risk_level=RiskLevel.HIGH,
                mitigation_strategy="Block content and scan for threats",
                constitutional_principles_affected=["accountability_framework"]
            )
        ]
    
    def validate_content(self, content: str, context: Optional[Dict[str, Any]] = None) -> Tuple[bool, List[SafetyViolation]]:
        """
        Validate content against constitutional safety principles.
        
        Args:
            content: Content to validate
            context: Additional context for validation
            
        Returns:
            Tuple of (is_safe, violations_list)
        """
        violations = []
        content_lower = content.lower()
        
        for pattern_def in self.threat_patterns:
            for pattern in pattern_def.patterns:
                matches = re.finditer(pattern, content_lower, re.IGNORECASE)
                for match in matches:
                    violation = SafetyViolation(
                        violation_id=f"{pattern_def.id}_{int(time.time())}_{match.start()}",
                        threat_category=pattern_def.category,
                        risk_level=pattern_def.risk_level,
                        pattern_matched=match.group(),
                        confidence_score=self._calculate_confidence(match, content),
                        affected_principles=pattern_def.constitutional_principles_affected,
                        mitigation_required=pattern_def.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
                    )
                    violations.append(violation)
        
        # Additional context-based validation
        if context:
            violations.extend(self._validate_context(content, context))
        
        # Determine if content is safe
        critical_violations = [v for v in violations if v.risk_level == RiskLevel.CRITICAL]
        high_risk_violations = [v for v in violations if v.risk_level == RiskLevel.HIGH]
        
        is_safe = len(critical_violations) == 0 and len(high_risk_violations) <= 1
        
        return is_safe, violations
    
    def _calculate_confidence(self, match: re.Match, content: str) -> float:
        """Calculate confidence score for a pattern match."""
        base_confidence = 0.8
        
        # Adjust based on context
        match_context = content[max(0, match.start()-50):match.end()+50].lower()
        
        # Higher confidence if multiple threat indicators
        threat_indicators = ["attack", "exploit", "hack", "breach", "unauthorized", "illegal"]
        indicator_count = sum(1 for indicator in threat_indicators if indicator in match_context)
        confidence_boost = min(0.15, indicator_count * 0.05)
        
        return min(0.95, base_confidence + confidence_boost)
    
    def _validate_context(self, content: str, context: Dict[str, Any]) -> List[SafetyViolation]:
        """Perform context-based validation."""
        violations = []
        
        # Check for constitutional hash manipulation
        if context.get("constitutional_hash") and context["constitutional_hash"] != "cdd01ef066bc6cf2":
            violations.append(SafetyViolation(
                violation_id=f"HASH_MISMATCH_{int(time.time())}",
                threat_category=ThreatCategory.CONSTITUTIONAL_BYPASS,
                risk_level=RiskLevel.HIGH,
                pattern_matched="constitutional_hash_mismatch",
                confidence_score=0.9,
                affected_principles=["accountability_framework"],
                mitigation_required=True
            ))
        
        # Check for privileged operation requests
        if context.get("requires_admin") and not context.get("admin_approved"):
            violations.append(SafetyViolation(
                violation_id=f"UNAUTH_ADMIN_{int(time.time())}",
                threat_category=ThreatCategory.UNAUTHORIZED_ACCESS,
                risk_level=RiskLevel.CRITICAL,
                pattern_matched="unapproved_admin_operation",
                confidence_score=0.95,
                affected_principles=["accountability_framework", "separation_of_powers"],
                mitigation_required=True
            ))
        
        return violations
    
    def get_mitigation_strategy(self, violation: SafetyViolation) -> Dict[str, Any]:
        """Get appropriate mitigation strategy for a violation."""
        pattern_def = next(
            (p for p in self.threat_patterns if p.category == violation.threat_category),
            None
        )
        
        if not pattern_def:
            return {"action": "review", "escalation": False}
        
        strategy = {
            "action": "block" if violation.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL] else "review",
            "escalation": violation.risk_level == RiskLevel.CRITICAL,
            "strategy": pattern_def.mitigation_strategy,
            "constitutional_principles": pattern_def.constitutional_principles_affected,
            "requires_human_review": violation.confidence_score < 0.8 or violation.risk_level == RiskLevel.CRITICAL
        }
        
        return strategy


class ConstitutionalEthicsFramework:
    """Framework for ethical decision-making in constitutional AI."""
    
    def __init__(self):
        self.ethical_principles = {
            "beneficence": "AI systems should act in the best interests of democratic governance",
            "non_maleficence": "AI systems must not harm democratic institutions or processes", 
            "autonomy": "Respect for human agency and democratic participation",
            "justice": "Fair and equitable treatment of all stakeholders",
            "transparency": "Clear communication of AI decision-making processes",
            "accountability": "Clear responsibility and oversight mechanisms"
        }
        
        self.safety_validator = ConstitutionalSafetyValidator()
    
    def evaluate_ethical_compliance(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a request for ethical compliance."""
        content = request.get("content", "")
        action = request.get("action", "")
        context = request.get("context", {})
        
        # Safety validation
        is_safe, violations = self.safety_validator.validate_content(content, context)
        
        # Ethical principle evaluation
        ethical_scores = {}
        for principle, description in self.ethical_principles.items():
            ethical_scores[principle] = self._evaluate_principle(content, action, principle)
        
        overall_ethical_score = sum(ethical_scores.values()) / len(ethical_scores)
        
        return {
            "ethical_compliance": {
                "is_safe": is_safe,
                "safety_violations": len(violations),
                "critical_violations": len([v for v in violations if v.risk_level == RiskLevel.CRITICAL]),
                "ethical_scores": ethical_scores,
                "overall_ethical_score": overall_ethical_score,
                "compliant": is_safe and overall_ethical_score >= 0.7
            },
            "violations": [
                {
                    "id": v.violation_id,
                    "category": v.threat_category.value,
                    "risk_level": v.risk_level.value,
                    "pattern": v.pattern_matched,
                    "confidence": v.confidence_score,
                    "mitigation": self.safety_validator.get_mitigation_strategy(v)
                }
                for v in violations
            ],
            "recommendations": self._generate_recommendations(violations, ethical_scores),
            "constitutional_hash": "cdd01ef066bc6cf2",
            "timestamp": time.time()
        }
    
    def _evaluate_principle(self, content: str, action: str, principle: str) -> float:
        """Evaluate compliance with a specific ethical principle."""
        content_lower = content.lower()
        action_lower = action.lower()
        
        principle_indicators = {
            "beneficence": ["benefit", "improve", "enhance", "strengthen", "support"],
            "non_maleficence": ["safe", "secure", "protect", "prevent", "avoid"],
            "autonomy": ["choice", "voluntary", "consent", "participation", "democratic"],
            "justice": ["fair", "equal", "equitable", "impartial", "unbiased"],
            "transparency": ["open", "transparent", "public", "clear", "visible"],
            "accountability": ["responsible", "accountable", "oversight", "review", "audit"]
        }
        
        indicators = principle_indicators.get(principle, [])
        matches = sum(1 for indicator in indicators if indicator in content_lower or indicator in action_lower)
        
        base_score = min(1.0, matches / max(1, len(indicators) * 0.5))
        
        # Adjust based on content quality and constitutional alignment
        if "constitutional" in content_lower:
            base_score += 0.1
        if "democratic" in content_lower:
            base_score += 0.1
        
        return min(1.0, base_score)
    
    def _generate_recommendations(self, violations: List[SafetyViolation], ethical_scores: Dict[str, float]) -> List[str]:
        """Generate recommendations based on violations and ethical scores."""
        recommendations = []
        
        if violations:
            critical_violations = [v for v in violations if v.risk_level == RiskLevel.CRITICAL]
            if critical_violations:
                recommendations.append("CRITICAL: Block request immediately and escalate to security team")
            
            high_risk_violations = [v for v in violations if v.risk_level == RiskLevel.HIGH]
            if high_risk_violations:
                recommendations.append("HIGH RISK: Require additional review and approval")
        
        # Ethical improvement recommendations
        low_scoring_principles = [p for p, score in ethical_scores.items() if score < 0.5]
        if low_scoring_principles:
            recommendations.append(f"Strengthen ethical compliance in: {', '.join(low_scoring_principles)}")
        
        # Constitutional compliance recommendations
        if not violations and all(score >= 0.7 for score in ethical_scores.values()):
            recommendations.append("Content meets constitutional and ethical standards")
        
        return recommendations


# Global instances
_safety_validator: Optional[ConstitutionalSafetyValidator] = None
_ethics_framework: Optional[ConstitutionalEthicsFramework] = None


def get_safety_validator() -> ConstitutionalSafetyValidator:
    """Get global safety validator instance."""
    global _safety_validator
    if _safety_validator is None:
        _safety_validator = ConstitutionalSafetyValidator()
    return _safety_validator


def get_ethics_framework() -> ConstitutionalEthicsFramework:
    """Get global ethics framework instance."""
    global _ethics_framework
    if _ethics_framework is None:
        _ethics_framework = ConstitutionalEthicsFramework()
    return _ethics_framework


def validate_constitutional_safety(content: str, context: Optional[Dict[str, Any]] = None) -> Tuple[bool, List[SafetyViolation]]:
    """Convenience function for constitutional safety validation."""
    return get_safety_validator().validate_content(content, context)


def evaluate_constitutional_ethics(request: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function for constitutional ethics evaluation."""
    return get_ethics_framework().evaluate_ethical_compliance(request)


# Export main components
__all__ = [
    'ThreatCategory',
    'RiskLevel',
    'ThreatPattern',
    'SafetyViolation',
    'ConstitutionalSafetyValidator',
    'ConstitutionalEthicsFramework',
    'get_safety_validator',
    'get_ethics_framework',
    'validate_constitutional_safety',
    'evaluate_constitutional_ethics'
]