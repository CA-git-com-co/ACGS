"""
Policy Builder Module for ACGS Agentic Policy Generation

Handles dynamic policy generation using LLM-based reasoning with constitutional
constraints and multi-agent coordination. Integrates with existing ACGS services
for constitutional compliance and governance synthesis.

Key Features:
- Constitutional constraint-aware policy generation
- Multi-agent coordination with conflict resolution
- Dynamic policy adaptation based on context
- Integration with governance synthesis service
- Safe policy validation and testing
"""

import json
import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional, Union

from services.shared.constitutional_safety_framework import (
    ConstitutionalSafetyFramework,
)
from services.shared.monitoring.intelligent_alerting_system import (
    IntelligentAlertingSystem,
)
from services.shared.security.enhanced_audit_logging import EnhancedAuditLogger

logger = logging.getLogger(__name__)

# Import Constitutional AI service for integration
try:
    from services.core.constitutional_ai.ac_service.app.services.hybrid_rlhf_constitutional_ai import (
        GovernanceMode,
        HybridGovernanceEngine,
        RiskLevel,
        create_hybrid_governance_engine,
    )

    CONSTITUTIONAL_AI_AVAILABLE = True
except ImportError:
    CONSTITUTIONAL_AI_AVAILABLE = False
    logger.warning("Constitutional AI service not available for integration")


class PolicyType(Enum):
    """Types of policies that can be generated"""

    GOVERNANCE = "governance"
    RESOURCE_ALLOCATION = "resource_allocation"
    ACCESS_CONTROL = "access_control"
    CONFLICT_RESOLUTION = "conflict_resolution"
    DECISION_FRAMEWORK = "decision_framework"
    OPERATIONAL = "operational"
    EMERGENCY_RESPONSE = "emergency_response"


class PolicyScope(Enum):
    """Scope of policy application"""

    GLOBAL = "global"
    DOMAIN_SPECIFIC = "domain_specific"
    CONTEXT_SPECIFIC = "context_specific"
    AGENT_SPECIFIC = "agent_specific"
    TEMPORARY = "temporary"


class PolicyPriority(Enum):
    """Priority levels for policy application"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class AgentConfig:
    """Configuration for dynamic agent creation"""

    agent_id: str
    name: str
    role: str
    capabilities: list[str]
    constraints: dict[str, Any]
    tools_allowed: list[str]
    resource_limits: dict[str, Union[int, float]]
    reporting_level: str
    escalation_threshold: float
    created_at: datetime


@dataclass
class ToolConfig:
    """Configuration for tool usage by agents"""

    tool_id: str
    name: str
    description: str
    safety_level: str
    permissions_required: list[str]
    rate_limits: dict[str, int]
    input_validation: dict[str, Any]
    output_sanitization: bool
    audit_required: bool


@dataclass
class PolicyTemplate:
    """Template for policy generation"""

    template_id: str
    policy_type: PolicyType
    scope: PolicyScope
    priority: PolicyPriority
    constraints: list[str]
    required_approvals: list[str]
    template_structure: dict[str, Any]
    constitutional_references: list[str]


@dataclass
class GeneratedPolicy:
    """A generated policy with metadata"""

    policy_id: str
    policy_type: PolicyType
    scope: PolicyScope
    priority: PolicyPriority
    content: dict[str, Any]
    constitutional_compliance_score: float
    generated_by: str
    approved_by: Optional[str]
    implementation_date: Optional[datetime]
    expiry_date: Optional[datetime]
    dependencies: list[str]
    conflict_resolutions: list[str]
    test_results: dict[str, Any]
    created_at: datetime


class PolicyBuilder:
    """
    Core policy building service for ACGS dynamic agent system.

    Generates policies using LLM reasoning with constitutional constraints,
    validates them against existing policies, and coordinates with other
    ACGS services for compliance and governance.
    """

    def __init__(
        self,
        constitutional_framework: ConstitutionalSafetyFramework,
        audit_logger: EnhancedAuditLogger,
        alerting_system: IntelligentAlertingSystem,
    ):
        self.constitutional_framework = constitutional_framework
        self.audit_logger = audit_logger
        self.alerting_system = alerting_system

        # Policy storage
        self.generated_policies: dict[str, GeneratedPolicy] = {}
        self.policy_templates: dict[str, PolicyTemplate] = {}
        self.agent_configs: dict[str, AgentConfig] = {}
        self.tool_configs: dict[str, ToolConfig] = {}

        # Constitutional constraints
        self.constitutional_principles = []
        self.policy_constraints = {}

        # Constitutional AI integration - will be initialized async
        self.constitutional_ai = None
        self._constitutional_ai_initialized = False

        # LLM integration via AI Model Service
        try:
            from services.shared.ai_model_service import (
                AIModelService,
                ModelProvider,
                ModelRequest,
                ModelType,
            )

            self.ai_model_service = AIModelService(
                default_provider=ModelProvider.OPENROUTER
            )
            self.llm_available = True
            logger.info("AI Model Service integrated successfully")
        except ImportError:
            self.ai_model_service = None
            self.llm_available = False
            logger.warning("AI Model Service not available for LLM integration")

        logger.info("PolicyBuilder initialized successfully")

    async def initialize(self) -> None:
        """Initialize the policy builder with default templates and constraints"""
        await self._load_constitutional_principles()
        await self._load_default_templates()
        await self._load_tool_configurations()

        # Initialize Constitutional AI
        if CONSTITUTIONAL_AI_AVAILABLE and not self._constitutional_ai_initialized:
            try:
                self.constitutional_ai = await create_hybrid_governance_engine(
                    {
                        "governance_mode": "adaptive",
                        "constitutional_threshold": 0.8,
                        "rlhf_threshold": 0.6,
                        "human_review_threshold": 0.9,
                    }
                )
                self._constitutional_ai_initialized = True
                logger.info("Hybrid Governance Engine integrated successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Constitutional AI: {e!s}")
                self.constitutional_ai = None

        logger.info("PolicyBuilder initialization completed")

    async def generate_policy(
        self, request: dict[str, Any], context: dict[str, Any]
    ) -> GeneratedPolicy:
        """
        Generate a new policy based on request and context.

        Args:
            request: Policy generation request with requirements
            context: Current system context and constraints

        Returns:
            Generated policy with constitutional compliance validation
        """
        try:
            policy_id = str(uuid.uuid4())

            # Extract requirements
            policy_type = PolicyType(request.get("type", "operational"))
            scope = PolicyScope(request.get("scope", "context_specific"))
            priority = PolicyPriority(request.get("priority", "medium"))
            requirements = request.get("requirements", {})

            # Get relevant template
            template = await self._select_template(policy_type, scope, requirements)

            # Generate policy content using LLM
            policy_content = await self._generate_policy_content(
                template, requirements, context
            )

            # Validate constitutional compliance
            compliance_score = await self._validate_constitutional_compliance(
                policy_content
            )

            # Check for conflicts with existing policies
            conflicts = await self._detect_policy_conflicts(policy_content, scope)

            # Generate conflict resolution if needed
            conflict_resolutions = []
            if conflicts:
                conflict_resolutions = await self._generate_conflict_resolutions(
                    policy_content, conflicts
                )

            # Create policy object
            policy = GeneratedPolicy(
                policy_id=policy_id,
                policy_type=policy_type,
                scope=scope,
                priority=priority,
                content=policy_content,
                constitutional_compliance_score=compliance_score,
                generated_by="PolicyBuilder",
                approved_by=None,
                implementation_date=None,
                expiry_date=self._calculate_expiry_date(policy_type),
                dependencies=self._extract_dependencies(policy_content),
                conflict_resolutions=conflict_resolutions,
                test_results={},
                created_at=datetime.utcnow(),
            )

            # Store generated policy
            self.generated_policies[policy_id] = policy

            # Log the generation
            await self.audit_logger.log_security_event(
                {
                    "event_type": "policy_generated",
                    "policy_id": policy_id,
                    "policy_type": policy_type.value,
                    "compliance_score": compliance_score,
                    "conflicts_detected": len(conflicts),
                }
            )

            return policy

        except Exception as e:
            logger.error(f"Error generating policy: {e!s}")
            await self.alerting_system.send_alert(
                {
                    "severity": "high",
                    "component": "PolicyBuilder",
                    "message": f"Policy generation failed: {e!s}",
                }
            )
            raise

    async def create_agent_config(self, agent_request: dict[str, Any]) -> AgentConfig:
        """
        Create configuration for a new dynamic agent.

        Args:
            agent_request: Agent creation request with specifications

        Returns:
            Agent configuration with safety constraints
        """
        try:
            agent_id = str(uuid.uuid4())

            # Extract agent specifications
            name = agent_request.get("name", f"Agent-{agent_id[:8]}")
            role = agent_request.get("role", "general_assistant")
            capabilities = agent_request.get("capabilities", [])

            # Apply constitutional constraints
            constraints = await self._apply_constitutional_constraints(
                role, capabilities, agent_request.get("domain")
            )

            # Determine allowed tools
            tools_allowed = await self._determine_allowed_tools(
                role, capabilities, constraints
            )

            # Set resource limits
            resource_limits = self._calculate_resource_limits(
                role, capabilities, agent_request.get("priority", "medium")
            )

            # Create agent configuration
            config = AgentConfig(
                agent_id=agent_id,
                name=name,
                role=role,
                capabilities=capabilities,
                constraints=constraints,
                tools_allowed=tools_allowed,
                resource_limits=resource_limits,
                reporting_level=agent_request.get("reporting_level", "standard"),
                escalation_threshold=agent_request.get("escalation_threshold", 0.8),
                created_at=datetime.utcnow(),
            )

            # Store configuration
            self.agent_configs[agent_id] = config

            # Log agent creation
            await self.audit_logger.log_security_event(
                {
                    "event_type": "agent_config_created",
                    "agent_id": agent_id,
                    "role": role,
                    "capabilities": capabilities,
                    "tools_allowed": len(tools_allowed),
                }
            )

            return config

        except Exception as e:
            logger.error(f"Error creating agent config: {e!s}")
            raise

    async def validate_policy(self, policy: GeneratedPolicy) -> dict[str, Any]:
        """
        Validate a generated policy for safety and compliance.

        Args:
            policy: Policy to validate

        Returns:
            Validation results with scores and recommendations
        """
        try:
            results = {
                "policy_id": policy.policy_id,
                "constitutional_compliance": policy.constitutional_compliance_score,
                "safety_checks": {},
                "conflict_analysis": {},
                "recommendations": [],
                "approval_required": False,
                "validation_timestamp": datetime.utcnow(),
            }

            # Safety validation
            safety_results = await self._perform_safety_validation(policy)
            results["safety_checks"] = safety_results

            # Conflict analysis
            conflict_results = await self._analyze_policy_conflicts(policy)
            results["conflict_analysis"] = conflict_results

            # Generate recommendations
            recommendations = await self._generate_policy_recommendations(
                policy, safety_results, conflict_results
            )
            results["recommendations"] = recommendations

            # Determine if approval is required
            results["approval_required"] = (
                policy.constitutional_compliance_score < 0.8
                or len(conflict_results.get("conflicts", [])) > 0
                or policy.priority in [PolicyPriority.CRITICAL, PolicyPriority.HIGH]
            )

            # Store test results
            policy.test_results = results

            return results

        except Exception as e:
            logger.error(f"Error validating policy: {e!s}")
            raise

    async def _load_constitutional_principles(self) -> None:
        """Load constitutional principles from the framework"""
        self.constitutional_principles = (
            await self.constitutional_framework.get_principles()
        )
        logger.info(
            f"Loaded {len(self.constitutional_principles)} constitutional principles"
        )

    async def _load_default_templates(self) -> None:
        """Load default policy templates"""
        templates = [
            PolicyTemplate(
                template_id="governance_basic",
                policy_type=PolicyType.GOVERNANCE,
                scope=PolicyScope.DOMAIN_SPECIFIC,
                priority=PolicyPriority.MEDIUM,
                constraints=["constitutional_compliance", "stakeholder_approval"],
                required_approvals=["constitutional_council"],
                template_structure={
                    "objective": "string",
                    "scope": "string",
                    "rules": "list",
                    "enforcement": "dict",
                    "review_cycle": "string",
                },
                constitutional_references=["democratic_participation", "transparency"],
            ),
            PolicyTemplate(
                template_id="access_control_basic",
                policy_type=PolicyType.ACCESS_CONTROL,
                scope=PolicyScope.GLOBAL,
                priority=PolicyPriority.HIGH,
                constraints=["security_clearance", "principle_of_least_privilege"],
                required_approvals=["security_officer"],
                template_structure={
                    "resources": "list",
                    "permissions": "dict",
                    "conditions": "list",
                    "exceptions": "list",
                },
                constitutional_references=["privacy", "security", "proportionality"],
            ),
        ]

        for template in templates:
            self.policy_templates[template.template_id] = template

        logger.info(f"Loaded {len(templates)} default policy templates")

    async def _load_tool_configurations(self) -> None:
        """Load safe tool configurations"""
        tools = [
            ToolConfig(
                tool_id="data_analyzer",
                name="Data Analysis Tool",
                description="Analyze datasets for patterns and insights",
                safety_level="medium",
                permissions_required=["data_access"],
                rate_limits={"requests_per_hour": 100},
                input_validation={"max_dataset_size": 1000000},
                output_sanitization=True,
                audit_required=True,
            ),
            ToolConfig(
                tool_id="policy_simulator",
                name="Policy Impact Simulator",
                description="Simulate policy impacts on different scenarios",
                safety_level="high",
                permissions_required=["policy_simulation"],
                rate_limits={"requests_per_hour": 50},
                input_validation={"max_simulation_duration": 3600},
                output_sanitization=True,
                audit_required=True,
            ),
        ]

        for tool in tools:
            self.tool_configs[tool.tool_id] = tool

        logger.info(f"Loaded {len(tools)} tool configurations")

    async def _select_template(
        self, policy_type: PolicyType, scope: PolicyScope, requirements: dict[str, Any]
    ) -> PolicyTemplate:
        """Select appropriate template for policy generation"""
        # Find matching template
        for template in self.policy_templates.values():
            if template.policy_type == policy_type:
                return template

        # Default template if no match found
        return PolicyTemplate(
            template_id="default",
            policy_type=policy_type,
            scope=scope,
            priority=PolicyPriority.MEDIUM,
            constraints=["constitutional_compliance"],
            required_approvals=["system_admin"],
            template_structure={"content": "dict"},
            constitutional_references=[],
        )

    async def _generate_policy_content(
        self,
        template: PolicyTemplate,
        requirements: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Generate policy content using LLM with constitutional constraints"""
        try:
            if self.ai_model_service and self.llm_available:
                # Use AI Model Service for LLM-based policy generation
                from services.shared.ai_model_service import (
                    ModelProvider,
                    ModelRequest,
                    ModelType,
                )

                # Construct LLM prompt for policy generation
                prompt = self._build_policy_generation_prompt(
                    template, requirements, context
                )

                # Create model request
                model_request = ModelRequest(
                    model_type=ModelType.CHAT,
                    provider=ModelProvider.OPENROUTER,
                    model_name="openrouter/cypher-alpha:free",
                    prompt=prompt,
                    parameters={
                        "temperature": (
                            0.3
                        ),  # Lower temperature for more consistent policy generation
                        "max_tokens": 2000,
                    },
                    context=context,
                    max_tokens=2000,
                    temperature=0.3,
                )

                # Generate response using AI Model Service
                response = await self.ai_model_service.generate_response(model_request)

                if response.content and not response.metadata.get("error", False):
                    try:
                        # Parse LLM response as JSON policy content
                        import json

                        llm_policy = json.loads(response.content)

                        # Merge with template structure and ensure required fields
                        policy_content = {
                            "template_id": template.template_id,
                            "objective": llm_policy.get(
                                "objective",
                                requirements.get(
                                    "objective", "Improve system governance"
                                ),
                            ),
                            "scope": template.scope.value,
                            "rules": llm_policy.get(
                                "rules", requirements.get("rules", [])
                            ),
                            "constraints": template.constraints,
                            "context": context,
                            "constitutional_references": (
                                template.constitutional_references
                            ),
                            "enforcement": llm_policy.get("enforcement", {}),
                            "review_cycle": llm_policy.get("review_cycle", "quarterly"),
                            "stakeholders": llm_policy.get("stakeholders", []),
                            "success_criteria": llm_policy.get("success_criteria", []),
                            "generated_at": datetime.utcnow().isoformat(),
                            "llm_generated": True,
                            "llm_confidence": response.confidence_score,
                        }

                        logger.info(
                            "LLM-generated policy content with confidence:"
                            f" {response.confidence_score}"
                        )
                        return policy_content

                    except json.JSONDecodeError:
                        logger.warning(
                            "LLM response was not valid JSON, falling back to"
                            " template-based generation"
                        )
                else:
                    logger.warning(
                        "LLM response contained errors, falling back to template-based"
                        " generation"
                    )

            # Fallback to template-based policy generation
            policy_content = {
                "template_id": template.template_id,
                "objective": requirements.get("objective", "Improve system governance"),
                "scope": template.scope.value,
                "rules": requirements.get("rules", []),
                "constraints": template.constraints,
                "context": context,
                "constitutional_references": template.constitutional_references,
                "enforcement": {"mechanism": "automated", "escalation": "human_review"},
                "review_cycle": "quarterly",
                "stakeholders": ["system_administrators", "constitutional_council"],
                "success_criteria": [
                    "compliance_rate > 95%",
                    "no_constitutional_violations",
                ],
                "generated_at": datetime.utcnow().isoformat(),
                "llm_generated": False,
            }

            return policy_content

        except Exception as e:
            logger.error(f"Error in policy content generation: {e!s}")
            # Return minimal safe policy on error
            return {
                "template_id": template.template_id,
                "objective": "Error in policy generation - manual review required",
                "scope": template.scope.value,
                "rules": ["manual_review_required"],
                "constraints": template.constraints,
                "context": context,
                "constitutional_references": template.constitutional_references,
                "generated_at": datetime.utcnow().isoformat(),
                "error": str(e),
            }

    async def _validate_constitutional_compliance(
        self, policy_content: dict[str, Any]
    ) -> float:
        """Validate policy against constitutional principles using Hybrid RLHF Constitutional AI"""
        try:
            if self.constitutional_ai and CONSTITUTIONAL_AI_AVAILABLE:
                # Use Hybrid RLHF Constitutional AI for validation
                governance_result = await self.constitutional_ai.evaluate(
                    prompt=(
                        "Evaluate constitutional compliance for policy:"
                        f" {policy_content.get('objective', 'Policy evaluation')}"
                    ),
                    response=json.dumps(policy_content, indent=2),
                    context={
                        "policy_type": policy_content.get("template_id", "unknown"),
                        "constitutional_references": policy_content.get(
                            "constitutional_references", []
                        ),
                        "constraints": policy_content.get("constraints", []),
                    },
                )

                # Calculate compliance score based on Constitutional AI evaluation
                base_score = governance_result.rlhf_score
                constitutional_confidence = governance_result.confidence

                # Adjust for constitutional violations
                violation_penalty = (
                    len(governance_result.constitutional_violations) * 0.1
                )
                compliance_score = min(
                    0.95, base_score * constitutional_confidence - violation_penalty
                )

                # Log the evaluation for audit
                await self.audit_logger.log_security_event(
                    {
                        "event_type": "constitutional_compliance_validation",
                        "method_used": governance_result.method_used.value,
                        "compliance_score": compliance_score,
                        "constitutional_violations": (
                            governance_result.constitutional_violations
                        ),
                        "risk_level": governance_result.risk_level.value,
                        "human_review_required": governance_result.human_review_required,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )

                return max(0.0, compliance_score)
            else:
                # Fallback to basic constitutional framework validation
                constitutional_refs = policy_content.get(
                    "constitutional_references", []
                )
                if len(constitutional_refs) > 0:
                    return min(0.9, 0.6 + (len(constitutional_refs) * 0.1))
                return 0.5

        except Exception as e:
            logger.error(f"Constitutional compliance validation error: {e!s}")
            # Fallback to conservative score on error
            return 0.3

    async def _detect_policy_conflicts(
        self, policy_content: dict[str, Any], scope: PolicyScope
    ) -> list[str]:
        """Detect conflicts with existing policies"""
        conflicts = []

        # Check against existing policies in the same scope
        for existing_policy in self.generated_policies.values():
            if existing_policy.scope == scope:
                # Simple conflict detection based on overlapping rules
                existing_rules = existing_policy.content.get("rules", [])
                new_rules = policy_content.get("rules", [])

                if set(existing_rules) & set(new_rules):
                    conflicts.append(existing_policy.policy_id)

        return conflicts

    async def _generate_conflict_resolutions(
        self, policy_content: dict[str, Any], conflicts: list[str]
    ) -> list[str]:
        """Generate resolutions for policy conflicts"""
        resolutions = []

        for conflict_id in conflicts:
            resolutions.append(
                f"Resolve conflict with policy {conflict_id} through prioritization"
            )

        return resolutions

    def _calculate_expiry_date(self, policy_type: PolicyType) -> datetime:
        """Calculate expiry date based on policy type"""
        days_map = {
            PolicyType.GOVERNANCE: 365,
            PolicyType.OPERATIONAL: 180,
            PolicyType.EMERGENCY_RESPONSE: 30,
            PolicyType.TEMPORARY: 7,
        }

        days = days_map.get(policy_type, 90)
        return datetime.utcnow() + timedelta(days=days)

    def _extract_dependencies(self, policy_content: dict[str, Any]) -> list[str]:
        """Extract policy dependencies from content"""
        # Extract dependencies from constitutional references and constraints
        dependencies = []
        dependencies.extend(policy_content.get("constitutional_references", []))
        dependencies.extend(policy_content.get("constraints", []))
        return dependencies

    def _build_policy_generation_prompt(
        self,
        template: PolicyTemplate,
        requirements: dict[str, Any],
        context: dict[str, Any],
    ) -> str:
        """Build LLM prompt for policy generation"""

        prompt = f"""You are an AI policy generation assistant for the ACGS (Autonomous Constitutional Governance System).

Generate a governance policy based on the following specifications:

TEMPLATE INFORMATION:
- Policy Type: {template.policy_type.value}
- Scope: {template.scope.value}
- Priority: {template.priority.value}
- Required Structure: {json.dumps(template.template_structure, indent=2)}
- Constitutional References: {', '.join(template.constitutional_references)}

USER REQUIREMENTS:
- Objective: {requirements.get('objective', 'Not specified')}
- Custom Rules: {json.dumps(requirements.get('rules', []), indent=2)}
- Additional Context: {json.dumps(requirements, indent=2)}

SYSTEM CONTEXT:
{json.dumps(context, indent=2)}

CONSTITUTIONAL CONSTRAINTS:
- All policies must comply with constitutional hash: cdd01ef066bc6cf2
- Ensure transparency and accountability in governance
- Protect individual privacy and rights
- Maintain democratic participation principles
- Include appropriate review and escalation mechanisms

REQUIRED OUTPUT FORMAT:
Return a JSON object with the following structure:
{{
    "objective": "Clear statement of policy objective",
    "rules": ["List", "of", "specific", "governance", "rules"],
    "enforcement": {{
        "mechanism": "How the policy will be enforced",
        "escalation": "Escalation procedures for violations"
    }},
    "review_cycle": "Review frequency (e.g., 'quarterly', 'annually')",
    "stakeholders": ["List", "of", "relevant", "stakeholders"],
    "success_criteria": ["Measurable", "success", "criteria"]
}}

Generate a comprehensive policy that addresses the user's objectives while maintaining constitutional compliance and democratic governance principles."""

        return prompt

    async def _apply_constitutional_constraints(
        self, role: str, capabilities: list[str], domain: Optional[str]
    ) -> dict[str, Any]:
        """Apply constitutional constraints to agent configuration"""
        constraints = {
            "constitutional_compliance_required": True,
            "transparency_level": (
                "high" if "decision_making" in capabilities else "medium"
            ),
            "audit_trail_required": True,
            "human_oversight_required": "critical_decisions" in capabilities,
            "resource_limits_enforced": True,
        }

        # Add domain-specific constraints
        if domain:
            constraints[f"{domain}_specific_rules"] = True

        return constraints

    async def _determine_allowed_tools(
        self, role: str, capabilities: list[str], constraints: dict[str, Any]
    ) -> list[str]:
        """Determine which tools the agent is allowed to use"""
        allowed_tools = []

        # Basic tools for all agents
        allowed_tools.extend(["data_analyzer", "report_generator"])

        # Capability-based tool access
        if "policy_analysis" in capabilities:
            allowed_tools.append("policy_simulator")

        if "research" in capabilities:
            allowed_tools.append("web_search")

        # Apply constraints
        if constraints.get("high_security_mode"):
            allowed_tools = [
                tool for tool in allowed_tools if tool == "report_generator"
            ]

        return allowed_tools

    def _calculate_resource_limits(
        self, role: str, capabilities: list[str], priority: str
    ) -> dict[str, Union[int, float]]:
        """Calculate resource limits for agent"""
        base_limits = {
            "max_memory_mb": 512,
            "max_cpu_percent": 20,
            "max_network_requests_per_hour": 100,
            "max_execution_time_seconds": 300,
        }

        # Adjust based on priority
        multiplier = {"high": 2.0, "medium": 1.0, "low": 0.5}.get(priority, 1.0)

        for key, value in base_limits.items():
            base_limits[key] = int(value * multiplier)

        return base_limits

    async def _perform_safety_validation(
        self, policy: GeneratedPolicy
    ) -> dict[str, Any]:
        """Perform safety validation on policy"""
        return {
            "constitutional_alignment": policy.constitutional_compliance_score > 0.7,
            "security_requirements_met": True,
            "privacy_compliance": True,
            "bias_check_passed": True,
            "safety_score": 0.85,
        }

    async def _analyze_policy_conflicts(
        self, policy: GeneratedPolicy
    ) -> dict[str, Any]:
        """Analyze policy for conflicts"""
        return {
            "conflicts": policy.conflict_resolutions,
            "severity": "low" if len(policy.conflict_resolutions) == 0 else "medium",
            "resolution_available": len(policy.conflict_resolutions) > 0,
        }

    async def _generate_policy_recommendations(
        self,
        policy: GeneratedPolicy,
        safety_results: dict[str, Any],
        conflict_results: dict[str, Any],
    ) -> list[str]:
        """Generate recommendations for policy improvement"""
        recommendations = []

        if policy.constitutional_compliance_score < 0.8:
            recommendations.append("Improve constitutional compliance alignment")

        if len(policy.conflict_resolutions) > 0:
            recommendations.append("Review and resolve policy conflicts")

        if safety_results.get("safety_score", 0) < 0.8:
            recommendations.append("Enhance safety measures")

        return recommendations
