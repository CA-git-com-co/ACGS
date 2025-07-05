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

from .eu_ai_act_compliance import (
    EUAIActCompliance,
    AISystemRiskLevel,
    AISystemCategory,
    ComplianceStatus,
    ComplianceRequirement,
    ComplianceAssessment,
    RiskAssessment
)

from .compliance_monitor import (
    ComplianceMonitor,
    ComplianceViolation,
    ComplianceMetrics,
    ComplianceReport
)

from .technical_documentation import (
    TechnicalDocumentationManager,
    DocumentationType,
    DocumentationPackage,
    DocumentationTemplate
)

from .conformity_assessment import (
    ConformityAssessment,
    ConformityStatus,
    AssessmentProcedure,
    NotifiedBody
)

from .human_oversight import (
    HumanOversightManager,
    OversightLevel,
    HumanReviewer,
    EscalationRule
)

__all__ = [
    'EUAIActCompliance',
    'AISystemRiskLevel',
    'AISystemCategory', 
    'ComplianceStatus',
    'ComplianceRequirement',
    'ComplianceAssessment',
    'RiskAssessment',
    'ComplianceMonitor',
    'ComplianceViolation',
    'ComplianceMetrics',
    'ComplianceReport',
    'TechnicalDocumentationManager',
    'DocumentationType',
    'DocumentationPackage',
    'DocumentationTemplate',
    'ConformityAssessment',
    'ConformityStatus',
    'AssessmentProcedure',
    'NotifiedBody',
    'HumanOversightManager',
    'OversightLevel',
    'HumanReviewer',
    'EscalationRule'
]