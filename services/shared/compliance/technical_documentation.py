"""
EU AI Act Technical Documentation Manager

Automated technical documentation generation and management system
implementing EU AI Act Annex IV requirements for high-risk AI systems.
Ensures comprehensive, up-to-date documentation for regulatory compliance.

Key Features:
- Automated technical documentation generation per Annex IV
- Document version control and change tracking
- Compliance validation and gap analysis
- Multi-format document export (PDF, HTML, JSON)
- Integration with system monitoring for real-time updates
"""

import hashlib
import json
import logging
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from services.shared.monitoring.intelligent_alerting_system import AlertingSystem
from services.shared.security.enhanced_audit_logging import AuditLogger

logger = logging.getLogger(__name__)


class DocumentationType(Enum):
    """Types of technical documentation per EU AI Act Annex IV"""

    GENERAL_DESCRIPTION = "general_description"
    DETAILED_DESCRIPTION = "detailed_description"
    DESIGN_SPECIFICATIONS = "design_specifications"
    RISK_MANAGEMENT = "risk_management"
    DATA_GOVERNANCE = "data_governance"
    TRAINING_VALIDATION = "training_validation"
    ACCURACY_METRICS = "accuracy_metrics"
    ROBUSTNESS_CYBERSECURITY = "robustness_cybersecurity"
    HUMAN_OVERSIGHT = "human_oversight"
    QUALITY_MANAGEMENT = "quality_management"
    CONFORMITY_ASSESSMENT = "conformity_assessment"
    POST_MARKET_MONITORING = "post_market_monitoring"


class DocumentStatus(Enum):
    """Document status"""

    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    PUBLISHED = "published"
    OUTDATED = "outdated"
    DEPRECATED = "deprecated"


@dataclass
class DocumentationRequirement:
    """EU AI Act documentation requirement"""

    requirement_id: str
    annex_section: str
    title: str
    description: str
    mandatory_elements: list[str]
    optional_elements: list[str]
    update_frequency_days: int
    responsible_role: str


@dataclass
class DocumentationPackage:
    """Complete technical documentation package"""

    package_id: str
    system_name: str
    system_version: str
    package_version: str
    creation_date: datetime
    last_updated: datetime
    status: DocumentStatus
    documents: dict[DocumentationType, dict[str, Any]]
    compliance_score: float
    missing_elements: list[str]
    next_review_date: datetime
    approval_history: list[dict[str, Any]]


@dataclass
class DocumentationTemplate:
    """Template for generating documentation"""

    template_id: str
    document_type: DocumentationType
    template_content: str
    required_variables: list[str]
    optional_variables: list[str]
    format_type: str
    version: str
    created_date: datetime


class TechnicalDocumentationManager:
    """
    EU AI Act Technical Documentation Management System
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}
        self.alerting = AlertingSystem()
        self.audit_logger = AuditLogger()

        # Configuration
        self.system_name = config.get("system_name", "ACGS")
        self.system_version = config.get("system_version", "1.0.0")
        self.organization = config.get("organization", "Constitutional AI Organization")
        self.documentation_dir = Path(
            config.get("documentation_dir", "./documentation")
        )

        # Documentation state
        self.documentation_packages = {}
        self.documentation_requirements = {}
        self.templates = {}

        # Create documentation directory
        self.documentation_dir.mkdir(parents=True, exist_ok=True)

        # Initialize documentation requirements
        self._initialize_documentation_requirements()
        self._initialize_templates()

    def _initialize_documentation_requirements(self):
        """Initialize EU AI Act Annex IV documentation requirements"""

        # Section 1: General description
        self.documentation_requirements["general_description"] = (
            DocumentationRequirement(
                requirement_id="annexiv_1_general",
                annex_section="Annex IV, Section 1",
                title="General Description of the AI System",
                description=(
                    "General description of the AI system including its intended"
                    " purpose"
                ),
                mandatory_elements=[
                    "intended_purpose",
                    "deployment_context",
                    "user_categories",
                    "performance_specifications",
                    "risk_level_classification",
                    "ai_system_category",
                    "deployment_timeline",
                ],
                optional_elements=[
                    "business_case",
                    "market_analysis",
                    "competitive_landscape",
                ],
                update_frequency_days=180,  # 6 months
                responsible_role="System Architect",
            )
        )

        # Section 2: Detailed description
        self.documentation_requirements["detailed_description"] = (
            DocumentationRequirement(
                requirement_id="annexiv_2_detailed",
                annex_section="Annex IV, Section 2",
                title="Detailed Description of Elements and Functioning",
                description=(
                    "Detailed description of the elements of the AI system and"
                    " functioning"
                ),
                mandatory_elements=[
                    "algorithmic_design",
                    "model_architecture",
                    "decision_logic",
                    "input_data_specifications",
                    "output_specifications",
                    "computational_requirements",
                    "integration_points",
                    "performance_characteristics",
                ],
                optional_elements=[
                    "optimization_techniques",
                    "scaling_considerations",
                    "deployment_variations",
                ],
                update_frequency_days=90,  # 3 months
                responsible_role="Technical Lead",
            )
        )

        # Section 3: Design specifications
        self.documentation_requirements["design_specifications"] = (
            DocumentationRequirement(
                requirement_id="annexiv_3_design",
                annex_section="Annex IV, Section 3",
                title="Design Specifications and Architecture",
                description=(
                    "Detailed design specifications, architecture, and development"
                    " methodology"
                ),
                mandatory_elements=[
                    "system_architecture",
                    "component_specifications",
                    "interface_definitions",
                    "data_flow_diagrams",
                    "security_design",
                    "scalability_design",
                    "reliability_requirements",
                    "development_methodology",
                ],
                optional_elements=[
                    "alternative_designs_considered",
                    "architectural_decisions_rationale",
                    "technology_stack_justification",
                ],
                update_frequency_days=120,  # 4 months
                responsible_role="Solution Architect",
            )
        )

        # Section 4: Risk management
        self.documentation_requirements["risk_management"] = DocumentationRequirement(
            requirement_id="annexiv_4_risk",
            annex_section="Annex IV, Section 4",
            title="Risk Management Documentation",
            description="Risk management system documentation and procedures",
            mandatory_elements=[
                "risk_management_process",
                "identified_risks",
                "risk_assessments",
                "mitigation_measures",
                "residual_risks",
                "risk_monitoring_procedures",
                "risk_review_schedule",
                "risk_ownership",
            ],
            optional_elements=[
                "risk_appetite_statement",
                "risk_tolerance_levels",
                "third_party_risk_assessments",
            ],
            update_frequency_days=60,  # 2 months
            responsible_role="Risk Manager",
        )

        # Section 5: Data governance
        self.documentation_requirements["data_governance"] = DocumentationRequirement(
            requirement_id="annexiv_5_data",
            annex_section="Annex IV, Section 5",
            title="Data Governance Documentation",
            description=(
                "Data governance, quality management, and bias mitigation documentation"
            ),
            mandatory_elements=[
                "data_governance_framework",
                "data_collection_procedures",
                "data_quality_standards",
                "data_preprocessing_methods",
                "bias_identification_procedures",
                "bias_mitigation_measures",
                "data_lineage_documentation",
                "data_retention_policies",
            ],
            optional_elements=[
                "data_sharing_agreements",
                "data_privacy_impact_assessments",
                "external_data_sources",
            ],
            update_frequency_days=90,  # 3 months
            responsible_role="Data Governance Officer",
        )

        # Section 6: Training and validation
        self.documentation_requirements["training_validation"] = (
            DocumentationRequirement(
                requirement_id="annexiv_6_training",
                annex_section="Annex IV, Section 6",
                title="Training and Validation Documentation",
                description=(
                    "Training procedures, validation methodology, and testing results"
                ),
                mandatory_elements=[
                    "training_methodology",
                    "training_data_specifications",
                    "model_training_procedures",
                    "validation_methodology",
                    "testing_procedures",
                    "performance_metrics",
                    "validation_results",
                    "model_versioning",
                ],
                optional_elements=[
                    "hyperparameter_tuning_logs",
                    "cross_validation_results",
                    "benchmark_comparisons",
                ],
                update_frequency_days=30,  # Monthly
                responsible_role="ML Engineer",
            )
        )

        # Section 7: Accuracy and performance
        self.documentation_requirements["accuracy_metrics"] = DocumentationRequirement(
            requirement_id="annexiv_7_accuracy",
            annex_section="Annex IV, Section 7",
            title="Accuracy and Performance Metrics",
            description=(
                "Accuracy levels, performance metrics, and measurement procedures"
            ),
            mandatory_elements=[
                "accuracy_metrics_definition",
                "performance_benchmarks",
                "measurement_procedures",
                "test_datasets",
                "accuracy_results",
                "performance_monitoring",
                "degradation_thresholds",
                "measurement_frequency",
            ],
            optional_elements=[
                "comparative_analysis",
                "industry_benchmarks",
                "performance_optimization_history",
            ],
            update_frequency_days=30,  # Monthly
            responsible_role="Quality Assurance Lead",
        )

        # Section 8: Robustness and cybersecurity
        self.documentation_requirements["robustness_cybersecurity"] = (
            DocumentationRequirement(
                requirement_id="annexiv_8_robustness",
                annex_section="Annex IV, Section 8",
                title="Robustness and Cybersecurity",
                description="Robustness measures and cybersecurity documentation",
                mandatory_elements=[
                    "robustness_requirements",
                    "stress_testing_procedures",
                    "failure_mode_analysis",
                    "cybersecurity_measures",
                    "threat_model",
                    "security_testing_results",
                    "incident_response_procedures",
                    "security_monitoring",
                ],
                optional_elements=[
                    "penetration_testing_reports",
                    "security_certifications",
                    "third_party_security_assessments",
                ],
                update_frequency_days=90,  # 3 months
                responsible_role="Security Officer",
            )
        )

        # Section 9: Human oversight
        self.documentation_requirements["human_oversight"] = DocumentationRequirement(
            requirement_id="annexiv_9_oversight",
            annex_section="Annex IV, Section 9",
            title="Human Oversight Documentation",
            description="Human oversight measures, procedures, and training",
            mandatory_elements=[
                "oversight_framework",
                "human_review_procedures",
                "escalation_mechanisms",
                "oversight_training_requirements",
                "reviewer_qualifications",
                "oversight_monitoring",
                "intervention_procedures",
                "override_capabilities",
            ],
            optional_elements=[
                "oversight_effectiveness_metrics",
                "reviewer_performance_tracking",
                "oversight_system_improvements",
            ],
            update_frequency_days=60,  # 2 months
            responsible_role="Human Oversight Coordinator",
        )

    def _initialize_templates(self):
        """Initialize documentation templates"""

        # General description template
        self.templates[DocumentationType.GENERAL_DESCRIPTION] = DocumentationTemplate(
            template_id="general_desc_template_v1",
            document_type=DocumentationType.GENERAL_DESCRIPTION,
            template_content=self._get_general_description_template(),
            required_variables=[
                "system_name",
                "system_version",
                "intended_purpose",
                "deployment_context",
                "user_categories",
                "risk_level",
            ],
            optional_variables=["business_case", "market_analysis"],
            format_type="markdown",
            version="1.0",
            created_date=datetime.utcnow(),
        )

        # Risk management template
        self.templates[DocumentationType.RISK_MANAGEMENT] = DocumentationTemplate(
            template_id="risk_mgmt_template_v1",
            document_type=DocumentationType.RISK_MANAGEMENT,
            template_content=self._get_risk_management_template(),
            required_variables=[
                "system_name",
                "risk_management_process",
                "identified_risks",
                "mitigation_measures",
                "residual_risks",
            ],
            optional_variables=["risk_appetite", "third_party_assessments"],
            format_type="markdown",
            version="1.0",
            created_date=datetime.utcnow(),
        )

        # Data governance template
        self.templates[DocumentationType.DATA_GOVERNANCE] = DocumentationTemplate(
            template_id="data_governance_template_v1",
            document_type=DocumentationType.DATA_GOVERNANCE,
            template_content=self._get_data_governance_template(),
            required_variables=[
                "system_name",
                "data_governance_framework",
                "data_quality_standards",
                "bias_mitigation_measures",
                "data_lineage",
            ],
            optional_variables=["data_sharing_agreements", "privacy_assessments"],
            format_type="markdown",
            version="1.0",
            created_date=datetime.utcnow(),
        )

    def _get_general_description_template(self) -> str:
        """Get general description template"""
        return """# General Description of {system_name}

## System Overview
**System Name:** {system_name}
**Version:** {system_version}
**Classification:** {risk_level} Risk AI System
**Category:** Democratic Processes (EU AI Act Annex III)

## Intended Purpose
{intended_purpose}

## Deployment Context
{deployment_context}

## Target Users
{user_categories}

## Performance Specifications
- **Accuracy Requirements:** {accuracy_requirements}
- **Response Time:** {response_time}
- **Availability:** {availability}
- **Throughput:** {throughput}

## System Capabilities
- Constitutional AI reasoning and decision-making
- Policy synthesis and recommendation
- Democratic governance support
- Bias detection and mitigation
- Explainable AI outputs

## Limitations and Constraints
- Requires human oversight for critical decisions
- Performance dependent on data quality
- Limited to constitutional and governance domains
- Subject to bias in training data

## Regulatory Classification
- **EU AI Act Classification:** High-Risk AI System
- **Regulatory Category:** Democratic Processes
- **Compliance Requirements:** Articles 8-15 EU AI Act
- **Conformity Assessment:** Required

## Deployment Timeline
- **Development Phase:** {development_phase}
- **Testing Phase:** {testing_phase}
- **Pilot Deployment:** {pilot_deployment}
- **Production Deployment:** {production_deployment}

{business_case}

{market_analysis}
"""

    def _get_risk_management_template(self) -> str:
        """Get risk management template"""
        return """# Risk Management Documentation for {system_name}

## Risk Management Process
{risk_management_process}

## Risk Assessment Framework
### Risk Categories
1. **Technical Risks**
   - Model performance degradation
   - System failures and outages
   - Data quality issues
   - Cybersecurity vulnerabilities

2. **Operational Risks**
   - Human oversight failures
   - Process compliance violations
   - Capacity and scalability issues
   - Third-party dependencies

3. **Regulatory Risks**
   - Non-compliance with EU AI Act
   - Privacy regulation violations
   - Audit and inspection findings
   - Legal and litigation risks

4. **Ethical Risks**
   - Bias and discrimination
   - Fairness and equity issues
   - Transparency failures
   - Democratic process impacts

## Identified Risks
{identified_risks}

## Risk Mitigation Measures
{mitigation_measures}

## Residual Risks
{residual_risks}

## Risk Monitoring and Review
- **Monitoring Frequency:** Continuous
- **Risk Assessment Reviews:** Quarterly
- **Risk Register Updates:** Monthly
- **Escalation Procedures:** Defined in Risk Response Plan

## Risk Governance
- **Risk Owner:** Chief Risk Officer
- **Risk Committee:** AI Governance Committee
- **Reporting:** Executive Dashboard and Board Reports

{risk_appetite}

{third_party_assessments}
"""

    def _get_data_governance_template(self) -> str:
        """Get data governance template"""
        return """# Data Governance Documentation for {system_name}

## Data Governance Framework
{data_governance_framework}

## Data Quality Standards
{data_quality_standards}

## Data Collection and Processing
### Data Sources
- **Primary Sources:** Constitutional documents, legal precedents
- **Secondary Sources:** Policy databases, democratic participation data
- **External Sources:** Public consultation responses, stakeholder feedback

### Data Collection Procedures
1. Data identification and sourcing
2. Data quality assessment
3. Data validation and verification
4. Data ingestion and processing
5. Data lineage documentation

## Bias Identification and Mitigation
{bias_mitigation_measures}

### Bias Detection Methods
- Statistical bias analysis
- Fairness metrics evaluation
- Demographic parity assessment
- Equalized odds testing

### Mitigation Strategies
- Data augmentation and balancing
- Algorithmic fairness constraints
- Post-processing bias correction
- Continuous monitoring and adjustment

## Data Lineage and Traceability
{data_lineage}

## Data Retention and Lifecycle Management
- **Retention Policy:** {data_retention_policy}
- **Archival Procedures:** {archival_procedures}
- **Deletion Protocols:** {deletion_protocols}

## Data Security and Privacy
- **Access Controls:** Role-based access control (RBAC)
- **Encryption:** End-to-end encryption for sensitive data
- **Privacy Measures:** Data minimization and pseudonymization
- **Compliance:** GDPR and data protection regulations

{data_sharing_agreements}

{privacy_assessments}
"""

    async def generate_documentation_package(
        self, system_details: dict[str, Any]
    ) -> DocumentationPackage:
        """Generate complete technical documentation package"""
        try:
            package_id = str(uuid.uuid4())
            current_time = datetime.utcnow()

            logger.info(f"Generating documentation package for {self.system_name}")

            # Generate documents for each required type
            documents = {}
            missing_elements = []

            for doc_type in DocumentationType:
                if doc_type in self.templates:
                    try:
                        document = await self._generate_document(
                            doc_type, system_details
                        )
                        documents[doc_type] = document
                    except Exception as e:
                        logger.error(
                            f"Failed to generate {doc_type.value} document: {e}"
                        )
                        missing_elements.append(f"{doc_type.value}_document")
                else:
                    logger.warning(f"No template available for {doc_type.value}")
                    missing_elements.append(f"{doc_type.value}_template")

            # Calculate compliance score
            total_requirements = len(self.documentation_requirements)
            completed_requirements = len(documents)
            compliance_score = (
                completed_requirements / total_requirements
                if total_requirements > 0
                else 0.0
            )

            # Create documentation package
            package = DocumentationPackage(
                package_id=package_id,
                system_name=self.system_name,
                system_version=self.system_version,
                package_version="1.0",
                creation_date=current_time,
                last_updated=current_time,
                status=DocumentStatus.DRAFT,
                documents=documents,
                compliance_score=compliance_score,
                missing_elements=missing_elements,
                next_review_date=current_time + timedelta(days=30),
                approval_history=[],
            )

            # Store package
            self.documentation_packages[package_id] = package

            # Save package to disk
            await self._save_documentation_package(package)

            # Log package generation
            await self.audit_logger.log_compliance_event({
                "event_type": "documentation_package_generated",
                "package_id": package_id,
                "system_name": self.system_name,
                "compliance_score": compliance_score,
                "documents_generated": len(documents),
                "missing_elements": len(missing_elements),
                "timestamp": current_time.isoformat(),
            })

            return package

        except Exception as e:
            logger.error(f"Documentation package generation failed: {e}")
            raise

    async def _generate_document(
        self, doc_type: DocumentationType, system_details: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate individual document"""
        try:
            template = self.templates[doc_type]

            # Prepare template variables
            template_vars = {
                "system_name": self.system_name,
                "system_version": self.system_version,
                "organization": self.organization,
                "generation_date": datetime.utcnow().strftime("%Y-%m-%d"),
                **system_details,
            }

            # Fill in missing required variables with defaults
            for var in template.required_variables:
                if var not in template_vars:
                    template_vars[var] = f"[{var.upper()}_TO_BE_DEFINED]"

            # Generate document content
            document_content = template.template_content.format(**template_vars)

            # Calculate content hash for version tracking
            content_hash = hashlib.md5(document_content.encode()).hexdigest()

            document = {
                "document_id": str(uuid.uuid4()),
                "document_type": doc_type.value,
                "title": (
                    self.documentation_requirements[
                        doc_type.value.replace("_", "")
                    ].title
                    if doc_type.value.replace("_", "")
                    in self.documentation_requirements
                    else f"{doc_type.value.replace('_', ' ').title()} Documentation"
                ),
                "content": document_content,
                "content_hash": content_hash,
                "template_id": template.template_id,
                "template_version": template.version,
                "generation_date": datetime.utcnow(),
                "last_updated": datetime.utcnow(),
                "status": DocumentStatus.DRAFT.value,
                "word_count": len(document_content.split()),
                "completeness_score": self._calculate_document_completeness(
                    document_content, template
                ),
                "metadata": {
                    "format": template.format_type,
                    "generated_by": "TechnicalDocumentationManager",
                    "variables_used": list(template_vars.keys()),
                    "template_source": template.template_id,
                },
            }

            return document

        except Exception as e:
            logger.error(f"Document generation failed for {doc_type.value}: {e}")
            raise

    def _calculate_document_completeness(
        self, content: str, template: DocumentationTemplate
    ) -> float:
        """Calculate document completeness score"""
        try:
            # Count placeholder variables that haven't been filled
            placeholder_count = content.count("[") + content.count("TO_BE_DEFINED")

            # Calculate based on required variables filled
            total_variables = len(template.required_variables) + len(
                template.optional_variables
            )

            if total_variables == 0:
                return 1.0

            # Penalize for unfilled placeholders
            penalty = min(placeholder_count * 0.1, 0.5)
            base_score = 0.8  # Base score for generated content

            return max(0.0, min(1.0, base_score - penalty))

        except Exception:
            return 0.5  # Default moderate score

    async def _save_documentation_package(self, package: DocumentationPackage):
        """Save documentation package to disk"""
        try:
            package_dir = self.documentation_dir / f"package_{package.package_id}"
            package_dir.mkdir(parents=True, exist_ok=True)

            # Save package metadata
            metadata_file = package_dir / "package_metadata.json"
            with open(metadata_file, "w") as f:
                # Convert package to dict, handling datetime serialization
                package_dict = asdict(package)
                package_dict["creation_date"] = package.creation_date.isoformat()
                package_dict["last_updated"] = package.last_updated.isoformat()
                package_dict["next_review_date"] = package.next_review_date.isoformat()

                # Convert documents dict keys from enum to string
                package_dict["documents"] = {
                    (
                        doc_type.value
                        if isinstance(doc_type, DocumentationType)
                        else str(doc_type)
                    ): doc_data
                    for doc_type, doc_data in package.documents.items()
                }

                json.dump(package_dict, f, indent=2, default=str)

            # Save individual documents
            for doc_type, document in package.documents.items():
                doc_filename = (
                    f"{doc_type.value if isinstance(doc_type, DocumentationType) else str(doc_type)}.md"
                )
                doc_file = package_dir / doc_filename

                with open(doc_file, "w") as f:
                    f.write(document["content"])

            logger.info(f"Documentation package saved to {package_dir}")

        except Exception as e:
            logger.error(f"Failed to save documentation package: {e}")

    async def update_documentation(
        self, package_id: str, updates: dict[str, Any]
    ) -> DocumentationPackage:
        """Update existing documentation package"""
        try:
            if package_id not in self.documentation_packages:
                raise ValueError(f"Documentation package {package_id} not found")

            package = self.documentation_packages[package_id]

            # Update package metadata
            package.last_updated = datetime.utcnow()
            package.status = DocumentStatus.UNDER_REVIEW

            # Update specific documents if provided
            if "documents" in updates:
                for doc_type, doc_updates in updates["documents"].items():
                    if isinstance(doc_type, str):
                        doc_type = DocumentationType(doc_type)

                    if doc_type in package.documents:
                        package.documents[doc_type].update(doc_updates)
                        package.documents[doc_type]["last_updated"] = datetime.utcnow()

            # Recalculate compliance score
            total_docs = len(DocumentationType)
            completed_docs = len(package.documents)
            package.compliance_score = completed_docs / total_docs

            # Update next review date
            if "next_review_date" in updates:
                package.next_review_date = updates["next_review_date"]

            # Add to approval history
            package.approval_history.append({
                "action": "updated",
                "timestamp": package.last_updated,
                "updated_by": updates.get("updated_by", "system"),
                "changes": updates.get("changes", []),
            })

            # Save updated package
            await self._save_documentation_package(package)

            # Log update
            await self.audit_logger.log_compliance_event({
                "event_type": "documentation_package_updated",
                "package_id": package_id,
                "updates": list(updates.keys()),
                "new_compliance_score": package.compliance_score,
                "timestamp": package.last_updated.isoformat(),
            })

            return package

        except Exception as e:
            logger.error(f"Documentation update failed: {e}")
            raise

    async def validate_documentation_compliance(
        self, package_id: str
    ) -> dict[str, Any]:
        """Validate documentation package for EU AI Act compliance"""
        try:
            if package_id not in self.documentation_packages:
                raise ValueError(f"Documentation package {package_id} not found")

            package = self.documentation_packages[package_id]
            validation_results = {
                "package_id": package_id,
                "validation_date": datetime.utcnow(),
                "overall_compliant": True,
                "compliance_score": package.compliance_score,
                "document_results": {},
                "missing_requirements": [],
                "recommendations": [],
                "critical_issues": [],
                "next_actions": [],
            }

            # Validate each documentation requirement
            for req_id, requirement in self.documentation_requirements.items():
                doc_type = (
                    DocumentationType(req_id)
                    if req_id in [dt.value for dt in DocumentationType]
                    else None
                )

                if doc_type and doc_type in package.documents:
                    # Document exists - validate content
                    document = package.documents[doc_type]
                    doc_validation = await self._validate_document_content(
                        document, requirement
                    )
                    validation_results["document_results"][req_id] = doc_validation

                    if not doc_validation["compliant"]:
                        validation_results["overall_compliant"] = False
                        validation_results["critical_issues"].extend(
                            doc_validation["issues"]
                        )
                else:
                    # Document missing
                    validation_results["overall_compliant"] = False
                    validation_results["missing_requirements"].append(requirement.title)
                    validation_results["critical_issues"].append(
                        f"Missing: {requirement.title}"
                    )

            # Generate recommendations
            if validation_results["missing_requirements"]:
                validation_results["recommendations"].append(
                    "Generate missing documentation:"
                    f" {', '.join(validation_results['missing_requirements'])}"
                )

            if package.compliance_score < 0.9:
                validation_results["recommendations"].append(
                    "Improve documentation completeness"
                )

            # Check for outdated documents
            outdated_docs = self._check_outdated_documents(package)
            if outdated_docs:
                validation_results["recommendations"].append(
                    f"Update outdated documents: {', '.join(outdated_docs)}"
                )

            # Generate next actions
            validation_results["next_actions"] = self._generate_next_actions(
                validation_results
            )

            # Log validation
            await self.audit_logger.log_compliance_event({
                "event_type": "documentation_validation_completed",
                "package_id": package_id,
                "overall_compliant": validation_results["overall_compliant"],
                "compliance_score": validation_results["compliance_score"],
                "critical_issues_count": len(validation_results["critical_issues"]),
                "timestamp": validation_results["validation_date"].isoformat(),
            })

            return validation_results

        except Exception as e:
            logger.error(f"Documentation validation failed: {e}")
            raise

    async def _validate_document_content(
        self, document: dict[str, Any], requirement: DocumentationRequirement
    ) -> dict[str, Any]:
        """Validate individual document content"""
        try:
            validation_result = {
                "compliant": True,
                "completeness_score": document.get("completeness_score", 0.0),
                "issues": [],
                "recommendations": [],
            }

            content = document.get("content", "")

            # Check for mandatory elements
            missing_elements = []
            for element in requirement.mandatory_elements:
                element_keywords = element.replace("_", " ").split()
                if not any(
                    keyword.lower() in content.lower() for keyword in element_keywords
                ):
                    missing_elements.append(element)

            if missing_elements:
                validation_result["compliant"] = False
                validation_result["issues"].extend([
                    f"Missing mandatory element: {elem}" for elem in missing_elements
                ])
                validation_result["recommendations"].append(
                    "Add missing mandatory elements"
                )

            # Check document completeness
            if document.get("completeness_score", 0.0) < 0.8:
                validation_result["compliant"] = False
                validation_result["issues"].append(
                    "Document completeness below threshold"
                )
                validation_result["recommendations"].append(
                    "Improve document completeness"
                )

            # Check for placeholder content
            if "[" in content and "TO_BE_DEFINED" in content:
                validation_result["issues"].append(
                    "Document contains unfilled placeholders"
                )
                validation_result["recommendations"].append(
                    "Fill in all placeholder content"
                )

            # Check document length (minimum content requirement)
            word_count = document.get("word_count", 0)
            if word_count < 500:  # Minimum 500 words for substantial documentation
                validation_result["issues"].append(
                    "Document too short - may lack sufficient detail"
                )
                validation_result["recommendations"].append("Expand document content")

            return validation_result

        except Exception as e:
            logger.error(f"Document content validation failed: {e}")
            return {
                "compliant": False,
                "completeness_score": 0.0,
                "issues": [f"Validation error: {e!s}"],
                "recommendations": ["Review document content manually"],
            }

    def _check_outdated_documents(self, package: DocumentationPackage) -> list[str]:
        """Check for outdated documents based on update frequency requirements"""
        outdated_docs = []
        current_time = datetime.utcnow()

        for doc_type, document in package.documents.items():
            doc_type_str = (
                doc_type.value
                if isinstance(doc_type, DocumentationType)
                else str(doc_type)
            )

            if doc_type_str in self.documentation_requirements:
                requirement = self.documentation_requirements[doc_type_str]
                last_updated = document.get("last_updated")

                if isinstance(last_updated, str):
                    last_updated = datetime.fromisoformat(last_updated)
                elif not isinstance(last_updated, datetime):
                    continue

                days_since_update = (current_time - last_updated).days
                if days_since_update > requirement.update_frequency_days:
                    outdated_docs.append(requirement.title)

        return outdated_docs

    def _generate_next_actions(self, validation_results: dict[str, Any]) -> list[str]:
        """Generate next actions based on validation results"""
        actions = []

        if validation_results["missing_requirements"]:
            actions.append("Generate missing documentation sections")

        if validation_results["critical_issues"]:
            actions.append("Address critical compliance issues")

        if validation_results["compliance_score"] < 0.9:
            actions.append("Improve overall documentation quality")

        actions.extend(validation_results["recommendations"])

        return list(set(actions))  # Remove duplicates

    async def export_documentation(
        self, package_id: str, format_type: str = "pdf"
    ) -> str:
        """Export documentation package in specified format"""
        try:
            if package_id not in self.documentation_packages:
                raise ValueError(f"Documentation package {package_id} not found")

            package = self.documentation_packages[package_id]
            export_dir = self.documentation_dir / f"exports/{package_id}"
            export_dir.mkdir(parents=True, exist_ok=True)

            if format_type.lower() == "pdf":
                export_file = await self._export_to_pdf(package, export_dir)
            elif format_type.lower() == "html":
                export_file = await self._export_to_html(package, export_dir)
            elif format_type.lower() == "json":
                export_file = await self._export_to_json(package, export_dir)
            else:
                raise ValueError(f"Unsupported export format: {format_type}")

            # Log export
            await self.audit_logger.log_compliance_event({
                "event_type": "documentation_exported",
                "package_id": package_id,
                "format": format_type,
                "export_file": str(export_file),
                "timestamp": datetime.utcnow().isoformat(),
            })

            return str(export_file)

        except Exception as e:
            logger.error(f"Documentation export failed: {e}")
            raise

    async def _export_to_html(
        self, package: DocumentationPackage, export_dir: Path
    ) -> Path:
        """Export documentation package to HTML"""
        try:
            import markdown

            html_file = export_dir / f"{package.system_name}_documentation.html"

            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>{package.system_name} Technical Documentation</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    h1 {{ color: #2c3e50; }}
                    h2 {{ color: #34495e; }}
                    .header {{ background-color: #ecf0f1; padding: 20px; margin-bottom: 30px; }}
                    .document {{ margin-bottom: 40px; border-bottom: 1px solid #bdc3c7; padding-bottom: 20px; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>{package.system_name} Technical Documentation</h1>
                    <p><strong>Version:</strong> {package.system_version}</p>
                    <p><strong>Generated:</strong> {package.creation_date.strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p><strong>Compliance Score:</strong> {package.compliance_score:.1%}</p>
                </div>
            """

            for doc_type, document in package.documents.items():
                doc_title = document.get(
                    "title",
                    (
                        doc_type.value
                        if isinstance(doc_type, DocumentationType)
                        else str(doc_type)
                    ),
                )
                doc_content = document.get("content", "")

                # Convert markdown to HTML
                html_doc_content = markdown.markdown(doc_content)

                html_content += f"""
                <div class="document">
                    <h2>{doc_title}</h2>
                    {html_doc_content}
                </div>
                """

            html_content += """
            </body>
            </html>
            """

            with open(html_file, "w", encoding="utf-8") as f:
                f.write(html_content)

            return html_file

        except Exception as e:
            logger.error(f"HTML export failed: {e}")
            # Fallback to simple HTML
            html_file = export_dir / f"{package.system_name}_documentation_simple.html"
            with open(html_file, "w") as f:
                f.write(
                    f"<h1>{package.system_name} Documentation</h1><p>Export generated:"
                    f" {datetime.utcnow()}</p>"
                )
            return html_file

    async def _export_to_json(
        self, package: DocumentationPackage, export_dir: Path
    ) -> Path:
        """Export documentation package to JSON"""
        json_file = export_dir / f"{package.system_name}_documentation.json"

        # Convert package to JSON-serializable format
        package_dict = asdict(package)
        package_dict["creation_date"] = package.creation_date.isoformat()
        package_dict["last_updated"] = package.last_updated.isoformat()
        package_dict["next_review_date"] = package.next_review_date.isoformat()

        # Convert documents dict keys
        package_dict["documents"] = {
            (
                doc_type.value
                if isinstance(doc_type, DocumentationType)
                else str(doc_type)
            ): doc_data
            for doc_type, doc_data in package.documents.items()
        }

        with open(json_file, "w") as f:
            json.dump(package_dict, f, indent=2, default=str)

        return json_file

    async def _export_to_pdf(
        self, package: DocumentationPackage, export_dir: Path
    ) -> Path:
        """Export documentation package to PDF (simplified version)"""
        # For now, create a text file as PDF generation requires additional dependencies
        pdf_file = export_dir / f"{package.system_name}_documentation.txt"

        content = f"{package.system_name} Technical Documentation\n"
        content += "=" * 50 + "\n\n"
        content += f"Version: {package.system_version}\n"
        content += f"Generated: {package.creation_date}\n"
        content += f"Compliance Score: {package.compliance_score:.1%}\n\n"

        for doc_type, document in package.documents.items():
            doc_title = document.get("title", str(doc_type))
            doc_content = document.get("content", "")

            content += f"\n{doc_title}\n"
            content += "-" * len(doc_title) + "\n"
            content += doc_content + "\n\n"

        with open(pdf_file, "w") as f:
            f.write(content)

        return pdf_file

    def get_documentation_status(self) -> dict[str, Any]:
        """Get overall documentation status"""
        total_packages = len(self.documentation_packages)

        if total_packages == 0:
            return {
                "total_packages": 0,
                "average_compliance_score": 0.0,
                "packages_by_status": {},
                "outdated_packages": 0,
                "next_review_due": None,
            }

        # Calculate statistics
        compliance_scores = [
            pkg.compliance_score for pkg in self.documentation_packages.values()
        ]
        avg_compliance = sum(compliance_scores) / len(compliance_scores)

        # Count by status
        status_counts = {}
        for package in self.documentation_packages.values():
            status = package.status.value
            status_counts[status] = status_counts.get(status, 0) + 1

        # Check for outdated packages
        current_time = datetime.utcnow()
        outdated_count = sum(
            1
            for pkg in self.documentation_packages.values()
            if pkg.next_review_date < current_time
        )

        # Find next review due
        next_reviews = [
            pkg.next_review_date for pkg in self.documentation_packages.values()
        ]
        next_review_due = min(next_reviews) if next_reviews else None

        return {
            "total_packages": total_packages,
            "average_compliance_score": avg_compliance,
            "packages_by_status": status_counts,
            "outdated_packages": outdated_count,
            "next_review_due": next_review_due,
            "templates_available": len(self.templates),
            "requirements_defined": len(self.documentation_requirements),
        }


# Example usage
async def example_usage():
    """Example of using the technical documentation manager"""
    # Initialize documentation manager
    doc_manager = TechnicalDocumentationManager({
        "system_name": "ACGS",
        "system_version": "1.0.0",
        "organization": "Constitutional AI Research Institute",
        "documentation_dir": "./acgs_documentation",
    })

    # Prepare system details
    system_details = {
        "intended_purpose": (
            "Constitutional AI governance and democratic decision support"
        ),
        "deployment_context": "Government and public sector constitutional governance",
        "user_categories": (
            "Government officials, legal experts, constitutional scholars"
        ),
        "accuracy_requirements": "95% for constitutional interpretations",
        "response_time": "<2 seconds for standard queries",
        "availability": "99.9% uptime",
        "throughput": "1000 queries per second",
        "development_phase": "Completed Q1 2024",
        "testing_phase": "Completed Q2 2024",
        "pilot_deployment": "Q3 2024",
        "production_deployment": "Q4 2024",
    }

    # Generate documentation package
    package = await doc_manager.generate_documentation_package(system_details)
    logger.info(f"Generated documentation package: {package.package_id}")
    logger.info(f"Compliance score: {package.compliance_score:.1%}")

    # Validate compliance
    validation_results = await doc_manager.validate_documentation_compliance(
        package.package_id
    )
    logger.info(
        f"Validation complete. Compliant: {validation_results['overall_compliant']}"
    )

    # Export documentation
    export_file = await doc_manager.export_documentation(package.package_id, "html")
    logger.info(f"Documentation exported to: {export_file}")

    # Get status
    status = doc_manager.get_documentation_status()
    logger.info(f"Documentation status: {status}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(example_usage())
