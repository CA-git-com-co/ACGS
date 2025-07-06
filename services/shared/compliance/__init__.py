"""
EU AI Act Compliance Framework

Comprehensive compliance framework implementing the European Union's Artificial
Intelligence Act requirements for high-risk AI systems, ensuring ACGS meets
all regulatory obligations for constitutional AI governance systems.

Key Components:
- EU AI Act classification and risk assessment
- Conformity assessment procedures
- Technical documentation and record keeping
- Human oversight and transparency requirements
- Quality management system integration
- Post-market monitoring and incident reporting
"""
# Constitutional Hash: cdd01ef066bc6cf2

from .compliance_monitor import (
    ComplianceMetrics,
    ComplianceMonitor,
    ComplianceReport,
    ComplianceViolation,
)
from .conformity_assessment import (
    AssessmentProcedure,
    ConformityAssessment,
    ConformityStatus,
    NotifiedBody,
)
from .eu_ai_act_compliance import (
    AISystemCategory,
    AISystemRiskLevel,
    ComplianceAssessment,
    ComplianceRequirement,
    ComplianceStatus,
    EUAIActCompliance,
    RiskAssessment,
)
from .human_oversight import (
    EscalationRule,
    HumanOversightManager,
    HumanReviewer,
    OversightLevel,
)
from .technical_documentation import (
    DocumentationPackage,
    DocumentationTemplate,
    DocumentationType,
    TechnicalDocumentationManager,
)

__all__ = [
    "EUAIActCompliance",
    "AISystemRiskLevel",
    "AISystemCategory",
    "ComplianceStatus",
    "ComplianceRequirement",
    "ComplianceAssessment",
    "RiskAssessment",
    "ComplianceMonitor",
    "ComplianceViolation",
    "ComplianceMetrics",
    "ComplianceReport",
    "TechnicalDocumentationManager",
    "DocumentationType",
    "DocumentationPackage",
    "DocumentationTemplate",
    "ConformityAssessment",
    "ConformityStatus",
    "AssessmentProcedure",
    "NotifiedBody",
    "HumanOversightManager",
    "OversightLevel",
    "HumanReviewer",
    "EscalationRule",
]
