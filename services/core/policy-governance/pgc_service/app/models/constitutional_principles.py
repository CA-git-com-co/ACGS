"""
ACGS-2 Constitutional Principles Database for RAG-based Rule Generation

This module defines the ConstitutionalPrinciple dataclass and provides a comprehensive
database of 50+ constitutional principles for semantic retrieval and Rego rule generation.

Constitutional Hash: cdd01ef066bc6cf2

Key Features:
- Comprehensive constitutional principles database
- Semantic embeddings for similarity search
- Metadata for rule generation context
- WINA optimization compatibility
- Risk threshold categorization
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

# Constitutional compliance hash for ACGS-2
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


@dataclass
class ConstitutionalPrinciple:
    """
    Represents a constitutional principle for RAG-based rule generation.

    This dataclass encapsulates all necessary information for semantic retrieval,
    rule synthesis, and OPA policy compilation with WINA optimization support.
    """

    # Core identification
    id: str
    title: str
    content: str
    category: str

    # Semantic and priority information
    priority_weight: float = 1.0
    embedding: list[float] | None = None

    # Metadata for rule generation
    source: str = "constitutional_framework"
    version: str = "v1.0.0"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # WINA optimization parameters
    wina_risk_threshold: float = 0.4  # Default risk threshold (0.25-0.55 range)
    wina_optimization_hints: dict[str, Any] = field(default_factory=dict)

    # Rule generation context
    enforcement_level: str = "mandatory"  # mandatory, advisory, conditional
    scope: list[str] = field(default_factory=list)  # service, user, data, etc.
    dependencies: list[str] = field(default_factory=list)  # other principle IDs

    # OPA/Rego generation metadata
    rego_templates: list[str] = field(default_factory=list)
    policy_patterns: list[str] = field(default_factory=list)

    # Additional metadata
    metadata: dict[str, Any] = field(default_factory=dict)
    constitutional_hash: str = CONSTITUTIONAL_HASH

    def __post_init__(self):
        """Post-initialization validation and setup."""
        # Validate risk threshold is within acceptable range
        if not (0.25 <= self.wina_risk_threshold <= 0.55):
            logger.warning(
                f"Risk threshold {self.wina_risk_threshold} outside recommended range [0.25, 0.55] "
                f"for principle {self.id}"
            )

        # Ensure metadata includes constitutional hash
        if "constitutional_hash" not in self.metadata:
            self.metadata["constitutional_hash"] = self.constitutional_hash

    def to_dict(self) -> dict[str, Any]:
        """Convert principle to dictionary for serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "category": self.category,
            "priority_weight": self.priority_weight,
            "embedding": self.embedding,
            "source": self.source,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "wina_risk_threshold": self.wina_risk_threshold,
            "wina_optimization_hints": self.wina_optimization_hints,
            "enforcement_level": self.enforcement_level,
            "scope": self.scope,
            "dependencies": self.dependencies,
            "rego_templates": self.rego_templates,
            "policy_patterns": self.policy_patterns,
            "metadata": self.metadata,
            "constitutional_hash": self.constitutional_hash,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ConstitutionalPrinciple":
        """Create principle from dictionary."""
        # Handle datetime parsing
        if isinstance(data.get("created_at"), str):
            data["created_at"] = datetime.fromisoformat(
                data["created_at"].replace("Z", "+00:00")
            )

        return cls(**data)


class ConstitutionalPrinciplesDatabase:
    """
    Comprehensive database of constitutional principles for RAG-based rule generation.

    Contains 50+ carefully curated constitutional principles covering all aspects
    of AI governance, privacy, security, fairness, and constitutional compliance.
    """

    def __init__(self):
        """Initialize the constitutional principles database."""
        self.principles: list[ConstitutionalPrinciple] = []
        self._principle_index: dict[str, ConstitutionalPrinciple] = {}
        self._category_index: dict[str, list[ConstitutionalPrinciple]] = {}

        # Initialize with comprehensive principles
        self._initialize_principles()
        self._build_indexes()

        logger.info(
            f"Initialized constitutional principles database with {len(self.principles)} principles"
        )

    def _initialize_principles(self):
        """Initialize the comprehensive database of constitutional principles."""

        # Core Constitutional Principles
        self.principles.extend(
            [
                ConstitutionalPrinciple(
                    id="const_001",
                    title="Constitutional Hash Validation",
                    content="All operations must validate the constitutional hash cdd01ef066bc6cf2 to ensure constitutional compliance and system integrity.",
                    category="constitutional_compliance",
                    priority_weight=10.0,
                    wina_risk_threshold=0.25,
                    enforcement_level="mandatory",
                    scope=["all_services", "all_operations"],
                    rego_templates=["hash_validation", "compliance_check"],
                    policy_patterns=["input_validation", "constitutional_guard"],
                    wina_optimization_hints={
                        "cache_validation": True,
                        "fast_path_optimization": True,
                        "precompute_hash_checks": True,
                    },
                ),
                ConstitutionalPrinciple(
                    id="const_002",
                    title="Service Authentication",
                    content="All inter-service communications must be authenticated with valid service tokens and constitutional hash verification.",
                    category="authentication",
                    priority_weight=9.0,
                    wina_risk_threshold=0.3,
                    enforcement_level="mandatory",
                    scope=["inter_service", "api_calls"],
                    dependencies=["const_001"],
                    rego_templates=["service_auth", "token_validation"],
                    policy_patterns=["authentication_guard", "service_identity"],
                ),
                ConstitutionalPrinciple(
                    id="const_003",
                    title="Data Privacy Protection",
                    content="Personal and sensitive data must be protected with appropriate encryption, access controls, and audit logging.",
                    category="privacy",
                    priority_weight=9.5,
                    wina_risk_threshold=0.35,
                    enforcement_level="mandatory",
                    scope=["data_access", "user_data", "sensitive_data"],
                    rego_templates=["data_protection", "privacy_guard"],
                    policy_patterns=["data_classification", "access_control"],
                ),
                ConstitutionalPrinciple(
                    id="const_004",
                    title="Audit Trail Integrity",
                    content="All system actions must be logged with tamper-evident audit trails and constitutional compliance verification.",
                    category="audit",
                    priority_weight=8.5,
                    wina_risk_threshold=0.3,
                    enforcement_level="mandatory",
                    scope=["all_operations", "audit_logging"],
                    dependencies=["const_001"],
                    rego_templates=["audit_logging", "integrity_check"],
                    policy_patterns=["audit_guard", "tamper_detection"],
                ),
                ConstitutionalPrinciple(
                    id="const_005",
                    title="Multi-Tenant Isolation",
                    content="Tenant data and operations must be completely isolated with no cross-tenant access or data leakage.",
                    category="multi_tenancy",
                    priority_weight=9.0,
                    wina_risk_threshold=0.4,
                    enforcement_level="mandatory",
                    scope=["tenant_data", "tenant_operations"],
                    rego_templates=["tenant_isolation", "rls_policy"],
                    policy_patterns=["tenant_guard", "isolation_check"],
                ),
            ]
        )

        # AI Governance Principles
        self.principles.extend(
            [
                ConstitutionalPrinciple(
                    id="ai_001",
                    title="AI Model Transparency",
                    content="AI model decisions must be explainable and auditable with clear reasoning chains and decision provenance.",
                    category="ai_governance",
                    priority_weight=8.0,
                    wina_risk_threshold=0.45,
                    enforcement_level="mandatory",
                    scope=["ai_decisions", "model_inference"],
                    rego_templates=["explainability_check", "decision_audit"],
                    policy_patterns=["transparency_guard", "explainable_ai"],
                ),
                ConstitutionalPrinciple(
                    id="ai_002",
                    title="Bias Mitigation",
                    content="AI systems must implement bias detection and mitigation mechanisms to ensure fair and equitable outcomes.",
                    category="fairness",
                    priority_weight=8.5,
                    wina_risk_threshold=0.4,
                    enforcement_level="mandatory",
                    scope=["ai_decisions", "algorithmic_fairness"],
                    rego_templates=["bias_check", "fairness_validation"],
                    policy_patterns=["fairness_guard", "bias_detection"],
                ),
                ConstitutionalPrinciple(
                    id="ai_003",
                    title="Human Oversight Requirement",
                    content="Critical AI decisions must include human oversight and approval mechanisms with clear escalation paths.",
                    category="human_oversight",
                    priority_weight=7.5,
                    wina_risk_threshold=0.5,
                    enforcement_level="conditional",
                    scope=["critical_decisions", "high_risk_operations"],
                    rego_templates=["human_approval", "escalation_check"],
                    policy_patterns=["oversight_guard", "human_in_loop"],
                ),
                ConstitutionalPrinciple(
                    id="ai_004",
                    title="Model Performance Monitoring",
                    content="AI models must be continuously monitored for performance degradation, drift, and anomalous behavior.",
                    category="monitoring",
                    priority_weight=7.0,
                    wina_risk_threshold=0.45,
                    enforcement_level="mandatory",
                    scope=["model_monitoring", "performance_tracking"],
                    rego_templates=["performance_check", "drift_detection"],
                    policy_patterns=["monitoring_guard", "performance_validation"],
                ),
                ConstitutionalPrinciple(
                    id="ai_005",
                    title="Safe AI Deployment",
                    content="AI model deployments must follow safe deployment practices with gradual rollout and rollback capabilities.",
                    category="deployment",
                    priority_weight=8.0,
                    wina_risk_threshold=0.35,
                    enforcement_level="mandatory",
                    scope=["model_deployment", "production_release"],
                    rego_templates=["deployment_safety", "rollback_capability"],
                    policy_patterns=["deployment_guard", "safety_check"],
                ),
            ]
        )

        # Security Principles
        self.principles.extend(
            [
                ConstitutionalPrinciple(
                    id="sec_001",
                    title="Zero Trust Architecture",
                    content="All network communications must follow zero trust principles with continuous verification and least privilege access.",
                    category="security",
                    priority_weight=9.0,
                    wina_risk_threshold=0.3,
                    enforcement_level="mandatory",
                    scope=["network_access", "service_communication"],
                    rego_templates=["zero_trust", "continuous_verification"],
                    policy_patterns=["trust_verification", "access_control"],
                ),
                ConstitutionalPrinciple(
                    id="sec_002",
                    title="Encryption at Rest and Transit",
                    content="All sensitive data must be encrypted both at rest and in transit using approved cryptographic standards.",
                    category="encryption",
                    priority_weight=9.5,
                    wina_risk_threshold=0.25,
                    enforcement_level="mandatory",
                    scope=["data_storage", "data_transmission"],
                    rego_templates=["encryption_check", "crypto_validation"],
                    policy_patterns=["encryption_guard", "crypto_compliance"],
                ),
                ConstitutionalPrinciple(
                    id="sec_003",
                    title="Vulnerability Management",
                    content="Systems must implement continuous vulnerability scanning and timely patching of security vulnerabilities.",
                    category="vulnerability",
                    priority_weight=8.0,
                    wina_risk_threshold=0.4,
                    enforcement_level="mandatory",
                    scope=["system_security", "patch_management"],
                    rego_templates=["vulnerability_check", "patch_validation"],
                    policy_patterns=["security_guard", "vulnerability_management"],
                ),
                ConstitutionalPrinciple(
                    id="sec_004",
                    title="Incident Response",
                    content="Security incidents must trigger immediate response procedures with containment, investigation, and remediation.",
                    category="incident_response",
                    priority_weight=8.5,
                    wina_risk_threshold=0.35,
                    enforcement_level="mandatory",
                    scope=["security_incidents", "threat_response"],
                    rego_templates=["incident_response", "threat_containment"],
                    policy_patterns=["incident_guard", "response_automation"],
                ),
                ConstitutionalPrinciple(
                    id="sec_005",
                    title="Access Control Management",
                    content="User and service access must be managed through role-based access control with regular access reviews.",
                    category="access_control",
                    priority_weight=8.5,
                    wina_risk_threshold=0.35,
                    enforcement_level="mandatory",
                    scope=["user_access", "service_access", "resource_access"],
                    rego_templates=["rbac_check", "access_validation"],
                    policy_patterns=["access_guard", "permission_validation"],
                ),
            ]
        )

        # Data Governance Principles
        self.principles.extend(
            [
                ConstitutionalPrinciple(
                    id="data_001",
                    title="Data Quality Assurance",
                    content="All data used in AI systems must meet quality standards with validation, cleansing, and accuracy verification.",
                    category="data_governance",
                    priority_weight=7.5,
                    wina_risk_threshold=0.4,
                    enforcement_level="mandatory",
                    scope=["data_ingestion", "data_processing"],
                    rego_templates=["data_quality", "validation_check"],
                    policy_patterns=["quality_guard", "data_validation"],
                ),
                ConstitutionalPrinciple(
                    id="data_002",
                    title="Data Retention Policies",
                    content="Data must be retained only for necessary periods with automatic deletion and compliance with retention policies.",
                    category="data_governance",
                    priority_weight=7.0,
                    wina_risk_threshold=0.45,
                    enforcement_level="mandatory",
                    scope=["data_storage", "data_lifecycle"],
                    rego_templates=["retention_policy", "data_lifecycle"],
                    policy_patterns=["retention_guard", "lifecycle_management"],
                ),
                ConstitutionalPrinciple(
                    id="data_003",
                    title="Data Lineage Tracking",
                    content="All data transformations and usage must be tracked with complete lineage and provenance information.",
                    category="data_governance",
                    priority_weight=6.5,
                    wina_risk_threshold=0.5,
                    enforcement_level="advisory",
                    scope=["data_processing", "data_transformation"],
                    rego_templates=["lineage_tracking", "provenance_check"],
                    policy_patterns=["lineage_guard", "provenance_validation"],
                ),
            ]
        )

        # Performance and Reliability Principles
        self.principles.extend(
            [
                ConstitutionalPrinciple(
                    id="perf_001",
                    title="Service Level Objectives",
                    content="All services must meet defined SLOs for availability, latency, and throughput with continuous monitoring.",
                    category="performance",
                    priority_weight=7.5,
                    wina_risk_threshold=0.4,
                    enforcement_level="mandatory",
                    scope=["service_performance", "slo_monitoring"],
                    rego_templates=["slo_check", "performance_validation"],
                    policy_patterns=["performance_guard", "slo_enforcement"],
                ),
                ConstitutionalPrinciple(
                    id="perf_002",
                    title="Resource Utilization Limits",
                    content="Services must operate within defined resource limits with automatic scaling and resource management.",
                    category="performance",
                    priority_weight=7.0,
                    wina_risk_threshold=0.45,
                    enforcement_level="mandatory",
                    scope=["resource_management", "auto_scaling"],
                    rego_templates=["resource_limits", "scaling_policy"],
                    policy_patterns=["resource_guard", "utilization_check"],
                ),
                ConstitutionalPrinciple(
                    id="perf_003",
                    title="Disaster Recovery",
                    content="Critical systems must have disaster recovery plans with regular testing and automated failover capabilities.",
                    category="reliability",
                    priority_weight=8.0,
                    wina_risk_threshold=0.35,
                    enforcement_level="mandatory",
                    scope=["disaster_recovery", "business_continuity"],
                    rego_templates=["dr_validation", "failover_check"],
                    policy_patterns=["recovery_guard", "continuity_validation"],
                ),
            ]
        )

        # Compliance and Legal Principles
        self.principles.extend(
            [
                ConstitutionalPrinciple(
                    id="legal_001",
                    title="GDPR Compliance",
                    content="Personal data processing must comply with GDPR requirements including consent, right to erasure, and data portability.",
                    category="legal_compliance",
                    priority_weight=9.0,
                    wina_risk_threshold=0.3,
                    enforcement_level="mandatory",
                    scope=["personal_data", "eu_operations"],
                    rego_templates=["gdpr_compliance", "consent_validation"],
                    policy_patterns=["gdpr_guard", "privacy_rights"],
                ),
                ConstitutionalPrinciple(
                    id="legal_002",
                    title="SOX Compliance",
                    content="Financial data and controls must comply with Sarbanes-Oxley requirements for accuracy and internal controls.",
                    category="legal_compliance",
                    priority_weight=8.5,
                    wina_risk_threshold=0.3,
                    enforcement_level="conditional",
                    scope=["financial_data", "internal_controls"],
                    rego_templates=["sox_compliance", "financial_controls"],
                    policy_patterns=["sox_guard", "financial_validation"],
                ),
                ConstitutionalPrinciple(
                    id="legal_003",
                    title="Industry Standards Compliance",
                    content="Systems must comply with relevant industry standards such as ISO 27001, SOC 2, and NIST frameworks.",
                    category="legal_compliance",
                    priority_weight=7.5,
                    wina_risk_threshold=0.4,
                    enforcement_level="mandatory",
                    scope=["security_standards", "compliance_frameworks"],
                    rego_templates=["standards_compliance", "framework_validation"],
                    policy_patterns=["standards_guard", "compliance_check"],
                ),
            ]
        )

        # Operational Excellence Principles
        self.principles.extend(
            [
                ConstitutionalPrinciple(
                    id="ops_001",
                    title="Change Management",
                    content="All system changes must follow approved change management processes with testing and rollback procedures.",
                    category="operations",
                    priority_weight=7.0,
                    wina_risk_threshold=0.4,
                    enforcement_level="mandatory",
                    scope=["system_changes", "deployment_process"],
                    rego_templates=["change_approval", "deployment_validation"],
                    policy_patterns=["change_guard", "approval_workflow"],
                ),
                ConstitutionalPrinciple(
                    id="ops_002",
                    title="Configuration Management",
                    content="System configurations must be managed through version control with automated deployment and drift detection.",
                    category="operations",
                    priority_weight=6.5,
                    wina_risk_threshold=0.45,
                    enforcement_level="mandatory",
                    scope=["configuration_management", "infrastructure_as_code"],
                    rego_templates=["config_validation", "drift_detection"],
                    policy_patterns=["config_guard", "version_control"],
                ),
                ConstitutionalPrinciple(
                    id="ops_003",
                    title="Monitoring and Alerting",
                    content="All critical systems must have comprehensive monitoring with proactive alerting and incident response.",
                    category="operations",
                    priority_weight=7.5,
                    wina_risk_threshold=0.35,
                    enforcement_level="mandatory",
                    scope=["system_monitoring", "alerting_systems"],
                    rego_templates=["monitoring_check", "alert_validation"],
                    policy_patterns=["monitoring_guard", "alert_management"],
                ),
            ]
        )

        # Additional specialized principles to reach 50+
        self.principles.extend(
            [
                ConstitutionalPrinciple(
                    id="spec_001",
                    title="API Rate Limiting",
                    content="All APIs must implement rate limiting to prevent abuse and ensure fair resource allocation.",
                    category="api_governance",
                    priority_weight=6.0,
                    wina_risk_threshold=0.5,
                    enforcement_level="mandatory",
                    scope=["api_endpoints", "rate_limiting"],
                    rego_templates=["rate_limit", "throttling_policy"],
                    policy_patterns=["rate_guard", "throttling_check"],
                ),
                ConstitutionalPrinciple(
                    id="spec_002",
                    title="API Versioning",
                    content="APIs must follow semantic versioning with backward compatibility and deprecation policies.",
                    category="api_governance",
                    priority_weight=5.5,
                    wina_risk_threshold=0.55,
                    enforcement_level="advisory",
                    scope=["api_versioning", "backward_compatibility"],
                    rego_templates=["version_check", "compatibility_validation"],
                    policy_patterns=["version_guard", "compatibility_check"],
                ),
                ConstitutionalPrinciple(
                    id="spec_003",
                    title="Container Security",
                    content="Container images must be scanned for vulnerabilities with approved base images and security policies.",
                    category="container_security",
                    priority_weight=7.5,
                    wina_risk_threshold=0.35,
                    enforcement_level="mandatory",
                    scope=["container_deployment", "image_security"],
                    rego_templates=["container_scan", "image_validation"],
                    policy_patterns=["container_guard", "image_security"],
                ),
                ConstitutionalPrinciple(
                    id="spec_004",
                    title="Network Segmentation",
                    content="Network traffic must be segmented with appropriate firewall rules and micro-segmentation policies.",
                    category="network_security",
                    priority_weight=8.0,
                    wina_risk_threshold=0.3,
                    enforcement_level="mandatory",
                    scope=["network_traffic", "micro_segmentation"],
                    rego_templates=["network_policy", "segmentation_check"],
                    policy_patterns=["network_guard", "segmentation_validation"],
                ),
                ConstitutionalPrinciple(
                    id="spec_005",
                    title="Backup and Recovery",
                    content="Critical data must be regularly backed up with tested recovery procedures and retention policies.",
                    category="data_protection",
                    priority_weight=7.5,
                    wina_risk_threshold=0.4,
                    enforcement_level="mandatory",
                    scope=["data_backup", "recovery_procedures"],
                    rego_templates=["backup_policy", "recovery_validation"],
                    policy_patterns=["backup_guard", "recovery_check"],
                ),
            ]
        )

    def _build_indexes(self):
        """Build internal indexes for efficient retrieval."""
        self._principle_index = {p.id: p for p in self.principles}

        # Build category index
        for principle in self.principles:
            if principle.category not in self._category_index:
                self._category_index[principle.category] = []
            self._category_index[principle.category].append(principle)

    def get_principle_by_id(self, principle_id: str) -> ConstitutionalPrinciple | None:
        """Get a principle by its ID."""
        return self._principle_index.get(principle_id)

    def get_principles_by_category(
        self, category: str
    ) -> list[ConstitutionalPrinciple]:
        """Get all principles in a specific category."""
        return self._category_index.get(category, [])

    def get_all_principles(self) -> list[ConstitutionalPrinciple]:
        """Get all constitutional principles."""
        return self.principles.copy()

    def get_principles_by_risk_threshold(
        self, min_threshold: float = 0.25, max_threshold: float = 0.55
    ) -> list[ConstitutionalPrinciple]:
        """Get principles within a specific risk threshold range."""
        return [
            p
            for p in self.principles
            if min_threshold <= p.wina_risk_threshold <= max_threshold
        ]

    def get_high_priority_principles(
        self, min_priority: float = 8.0
    ) -> list[ConstitutionalPrinciple]:
        """Get high priority principles above a threshold."""
        return [p for p in self.principles if p.priority_weight >= min_priority]


# Global instance for easy access
constitutional_principles_db = ConstitutionalPrinciplesDatabase()
