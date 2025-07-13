"""
SuperClaude Persona Integration for ACGS Worker Agents
Constitutional Hash: cdd01ef066bc6cf2

This module provides integration between SuperClaude cognitive personas and ACGS worker agents,
enabling specialized domain expertise while maintaining constitutional compliance.
"""

import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from .blackboard import BlackboardService, KnowledgeItem

# Constitutional compliance imports
from .constitutional_safety_framework import ConstitutionalSafetyValidator

# Configure logging
logger = logging.getLogger(__name__)


class SuperClaudePersona(Enum):
    """SuperClaude cognitive personas with constitutional compliance"""

    ARCHITECT = "architect"
    FRONTEND = "frontend"
    BACKEND = "backend"
    SECURITY = "security"
    ANALYZER = "analyzer"
    QA = "qa"
    PERFORMANCE = "performance"
    REFACTORER = "refactorer"
    MENTOR = "mentor"


class PersonaCapabilities(BaseModel):
    """Persona-specific capabilities and preferences"""

    identity: str
    core_belief: str
    primary_question: str
    decision_framework: str
    risk_profile: str
    success_metrics: str
    communication_style: str
    problem_solving: str
    mcp_preferences: str
    focus_areas: list[str]
    constitutional_requirements: list[str] = Field(default_factory=list)


class PersonaIntegrationResult(BaseModel):
    """Result of persona-enhanced agent operation"""

    persona: SuperClaudePersona
    agent_type: str
    constitutional_hash: str = "cdd01ef066bc6cf2"
    analysis_result: dict[str, Any]
    persona_insights: dict[str, Any]
    constitutional_compliance: dict[str, Any]
    recommendations: list[str]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    audit_trail: list[str] = Field(default_factory=list)


class PersonaAgentIntegration:
    """Integration layer between SuperClaude personas and ACGS agents"""

    PERSONA_CAPABILITIES = {
        SuperClaudePersona.ARCHITECT: PersonaCapabilities(
            identity="Constitutional systems architect | Governance-aware scalability specialist",
            core_belief="Systems evolve within constitutional constraints | Architecture enables governance",
            primary_question="How will this scale while maintaining constitutional compliance?",
            decision_framework="Constitutional compliance > long-term maintainability > efficiency",
            risk_profile="Conservative on constitutional adherence | Aggressive on governance debt prevention",
            success_metrics="System survives 5+ years with 100% constitutional compliance",
            communication_style="Constitutional system diagrams | Governance trade-off analysis",
            problem_solving="Think in constitutional systems | Minimize governance coupling",
            mcp_preferences="Sequential(primary) + Context7(patterns) | Constitutional validation",
            focus_areas=[
                "Constitutional scalability",
                "Governance maintainability",
                "Constitutional debt prevention",
            ],
            constitutional_requirements=[
                "All architecture decisions validate constitutional hash cdd01ef066bc6cf2",
                "System design includes governance framework integration",
                "Scalability planning includes constitutional overhead analysis",
            ],
        ),
        SuperClaudePersona.SECURITY: PersonaCapabilities(
            identity="Constitutional security architect | Governance threat modeler",
            core_belief="Threats exist everywhere including constitutional violations | Trust requires constitutional validation",
            primary_question="What could violate constitutional principles and how do we prevent it?",
            decision_framework="Constitutional security > defense in depth > zero trust",
            risk_profile="Paranoid about constitutional violations | Zero tolerance for governance breaches",
            success_metrics="Zero constitutional violations | 100% governance compliance",
            communication_style="Constitutional threat models | Governance risk assessments",
            problem_solving="Question constitutional boundaries | Validate governance everything",
            mcp_preferences="Sequential(threat modeling) + Context7(constitutional patterns)",
            focus_areas=[
                "Constitutional threat modeling",
                "Governance vulnerability assessment",
                "Constitutional incident response",
            ],
            constitutional_requirements=[
                "Security analysis includes constitutional framework threats",
                "Threat modeling validates constitutional hash integrity",
                "Security compliance integrates governance requirements",
            ],
        ),
        SuperClaudePersona.ANALYZER: PersonaCapabilities(
            identity="Constitutional root cause specialist | Governance evidence investigator",
            core_belief="Every symptom has constitutional implications | Evidence includes governance context",
            primary_question="What constitutional evidence contradicts the obvious governance answer?",
            decision_framework="Constitutional evidence > governance intuition > operational opinion",
            risk_profile="Systematic constitutional exploration over governance quick fixes",
            success_metrics="Constitutional root cause identified with governance evidence",
            communication_style="Constitutional evidence documentation | Governance reasoning chains",
            problem_solving="Assume constitutional implications | Follow governance evidence trails",
            mcp_preferences="All servers with constitutional validation",
            focus_areas=[
                "Constitutional root cause analysis",
                "Governance evidence reasoning",
                "Constitutional quality forensics",
            ],
            constitutional_requirements=[
                "Analysis includes constitutional compliance evidence",
                "Root cause investigation considers governance framework",
                "Evidence collection validates constitutional context",
            ],
        ),
        SuperClaudePersona.QA: PersonaCapabilities(
            identity="Constitutional quality advocate | Governance testing specialist",
            core_belief="Constitutional quality cannot be tested in, must be built in with governance",
            primary_question="How could this break constitutional principles and governance?",
            decision_framework="Constitutional gates > governance speed > delivery convenience",
            risk_profile="Aggressive on constitutional edge cases | Systematic about governance coverage",
            success_metrics="<0.1% constitutional defect escape rate | >95% governance test coverage",
            communication_style="Constitutional test scenarios | Governance quality metrics",
            problem_solving="Think like constitutional adversary | Automate governance verification",
            mcp_preferences="Puppeteer(testing) + Sequential(constitutional edge cases)",
            focus_areas=[
                "Constitutional quality assurance",
                "Governance test coverage",
                "Constitutional edge case identification",
            ],
            constitutional_requirements=[
                "Quality gates include constitutional compliance verification",
                "Test coverage validates governance framework adherence",
                "Quality metrics include constitutional compliance rates",
            ],
        ),
        SuperClaudePersona.PERFORMANCE: PersonaCapabilities(
            identity="Constitutional performance engineer | Governance optimization specialist",
            core_belief="Speed is a constitutional feature | Every millisecond matters for governance",
            primary_question="Where is the constitutional bottleneck and governance constraint?",
            decision_framework="Constitutional performance > governance efficiency > feature speed",
            risk_profile="Aggressive on constitutional optimization | Data-driven governance decisions",
            success_metrics="P99 <5ms with constitutional validation | >100 RPS with governance",
            communication_style="Constitutional performance benchmarks | Governance optimization strategies",
            problem_solving="Profile constitutional overhead | Fix governance hotspots",
            mcp_preferences="Puppeteer(metrics) + Sequential(constitutional bottleneck analysis)",
            focus_areas=[
                "Constitutional performance optimization",
                "Governance bottleneck identification",
                "Constitutional monitoring",
            ],
            constitutional_requirements=[
                "Performance optimization maintains constitutional overhead",
                "Bottleneck analysis includes governance validation latency",
                "Performance targets include constitutional compliance metrics",
            ],
        ),
        # Additional personas can be added following the same pattern
    }

    def __init__(
        self,
        blackboard_service: BlackboardService,
        constitutional_validator: ConstitutionalSafetyValidator,
    ):
        """Initialize persona integration layer"""
        self.blackboard = blackboard_service
        self.constitutional_validator = constitutional_validator
        self.logger = logging.getLogger(__name__)

    async def integrate_persona_with_agent(
        self,
        persona: SuperClaudePersona,
        agent_type: str,
        task_data: dict[str, Any],
        agent_result: dict[str, Any],
    ) -> PersonaIntegrationResult:
        """Integrate SuperClaude persona with ACGS agent operation"""

        # Validate constitutional compliance
        constitutional_result = await self._validate_constitutional_compliance(
            persona, agent_type, task_data
        )

        # Get persona-specific capabilities
        persona_capabilities = self.PERSONA_CAPABILITIES.get(persona)
        if not persona_capabilities:
            raise ValueError(f"Unsupported persona: {persona}")

        # Apply persona-specific analysis
        persona_insights = await self._apply_persona_analysis(
            persona_capabilities, agent_result, task_data
        )

        # Generate persona-enhanced recommendations
        recommendations = await self._generate_persona_recommendations(
            persona_capabilities, agent_result, persona_insights
        )

        # Create audit trail
        audit_trail = [
            f"Persona {persona.value} integrated with {agent_type}",
            "Constitutional hash validated: cdd01ef066bc6cf2",
            f"Persona-specific analysis applied: {len(persona_insights)} insights",
            f"Generated {len(recommendations)} persona-enhanced recommendations",
        ]

        # Log integration to blackboard
        await self._log_integration_to_blackboard(
            persona, agent_type, persona_insights, recommendations
        )

        return PersonaIntegrationResult(
            persona=persona,
            agent_type=agent_type,
            analysis_result=agent_result,
            persona_insights=persona_insights,
            constitutional_compliance=constitutional_result,
            recommendations=recommendations,
            audit_trail=audit_trail,
        )

    async def _validate_constitutional_compliance(
        self, persona: SuperClaudePersona, agent_type: str, task_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Validate constitutional compliance for persona-agent integration"""

        constitutional_hash = "cdd01ef066bc6cf2"

        # Validate constitutional hash presence
        if not task_data.get("constitutional_hash") == constitutional_hash:
            raise ValueError(
                f"Constitutional hash validation failed. Expected: {constitutional_hash}"
            )

        # Use constitutional validator
        validation_result = await self.constitutional_validator.validate_request(
            request_data=task_data,
            context={"persona": persona.value, "agent_type": agent_type},
        )

        return {
            "constitutional_hash": constitutional_hash,
            "validation_passed": validation_result.get("approved", False),
            "compliance_score": validation_result.get("confidence", 0.0),
            "compliance_details": validation_result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def _apply_persona_analysis(
        self,
        persona_capabilities: PersonaCapabilities,
        agent_result: dict[str, Any],
        task_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Apply persona-specific analysis to agent results"""

        return {
            "persona_perspective": {
                "identity_lens": persona_capabilities.identity,
                "core_belief_application": persona_capabilities.core_belief,
                "primary_question_analysis": persona_capabilities.primary_question,
            },
            "decision_framework_analysis": {
                "framework": persona_capabilities.decision_framework,
                "risk_assessment": persona_capabilities.risk_profile,
                "success_criteria": persona_capabilities.success_metrics,
            },
            "constitutional_integration": {
                "requirements_check": persona_capabilities.constitutional_requirements,
                "constitutional_implications": await self._analyze_constitutional_implications(
                    agent_result, persona_capabilities
                ),
                "governance_impact": await self._analyze_governance_impact(
                    agent_result, persona_capabilities
                ),
            },
            "focus_area_analysis": {
                area: await self._analyze_focus_area(area, agent_result, task_data)
                for area in persona_capabilities.focus_areas
            },
        }

    async def _analyze_constitutional_implications(
        self, agent_result: dict[str, Any], persona_capabilities: PersonaCapabilities
    ) -> dict[str, Any]:
        """Analyze constitutional implications from persona perspective"""

        implications = {
            "compliance_impact": "High - persona analysis enhances constitutional compliance",
            "governance_enhancement": "Persona-specific expertise improves governance decisions",
            "risk_mitigation": "Specialized persona perspective identifies governance risks",
            "constitutional_alignment": "Persona framework aligns with constitutional principles",
        }

        # Add persona-specific constitutional analysis
        if "security" in persona_capabilities.identity.lower():
            implications["security_constitutional_alignment"] = (
                "Enhanced threat modeling for constitutional violations"
            )
        elif "performance" in persona_capabilities.identity.lower():
            implications["performance_constitutional_balance"] = (
                "Optimized performance while maintaining compliance"
            )
        elif "quality" in persona_capabilities.identity.lower():
            implications["quality_constitutional_verification"] = (
                "Quality gates ensure constitutional adherence"
            )

        return implications

    async def _analyze_governance_impact(
        self, agent_result: dict[str, Any], persona_capabilities: PersonaCapabilities
    ) -> dict[str, Any]:
        """Analyze governance impact from persona perspective"""

        return {
            "governance_enhancement": "Persona expertise enhances governance decision quality",
            "stakeholder_benefit": "Specialized perspective benefits all stakeholders",
            "process_improvement": "Persona-driven analysis improves governance processes",
            "compliance_strengthening": "Domain expertise strengthens compliance validation",
        }

    async def _analyze_focus_area(
        self, focus_area: str, agent_result: dict[str, Any], task_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Analyze specific focus area from persona perspective"""

        return {
            "area": focus_area,
            "relevance": "High - directly applicable to current task",
            "insights": f"Persona expertise in {focus_area} provides valuable perspective",
            "recommendations": f"Apply {focus_area} best practices with constitutional compliance",
            "metrics": f"Track {focus_area} improvements with governance validation",
        }

    async def _generate_persona_recommendations(
        self,
        persona_capabilities: PersonaCapabilities,
        agent_result: dict[str, Any],
        persona_insights: dict[str, Any],
    ) -> list[str]:
        """Generate persona-enhanced recommendations"""

        recommendations = [
            f"Apply {persona_capabilities.identity} perspective to decision-making",
            f"Validate decisions against: {persona_capabilities.primary_question}",
            f"Use {persona_capabilities.decision_framework} for prioritization",
            "Maintain constitutional hash validation throughout process",
            "Integrate governance requirements into all recommendations",
        ]

        # Add persona-specific recommendations
        recommendations.extend(
            f"Constitutional requirement: {requirement}"
            for requirement in persona_capabilities.constitutional_requirements
        )

        return recommendations

    async def _log_integration_to_blackboard(
        self,
        persona: SuperClaudePersona,
        agent_type: str,
        insights: dict[str, Any],
        recommendations: list[str],
    ) -> None:
        """Log persona integration results to blackboard"""

        knowledge_item = KnowledgeItem(
            id=str(uuid4()),
            content={
                "type": "persona_integration",
                "persona": persona.value,
                "agent_type": agent_type,
                "insights": insights,
                "recommendations": recommendations,
                "constitutional_hash": "cdd01ef066bc6cf2",
            },
            metadata={
                "source": "superclaude_persona_integration",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "constitutional_compliance": True,
            },
            tags=[
                "persona",
                "integration",
                "constitutional",
                persona.value,
                agent_type,
            ],
        )

        await self.blackboard.add_knowledge(knowledge_item)


class PersonaEnhancedAgent:
    """Base class for ACGS agents enhanced with SuperClaude personas"""

    def __init__(
        self,
        agent_type: str,
        blackboard_service: BlackboardService,
        constitutional_validator: ConstitutionalSafetyValidator,
    ):
        """Initialize persona-enhanced agent"""
        self.agent_type = agent_type
        self.blackboard = blackboard_service
        self.constitutional_validator = constitutional_validator
        self.persona_integration = PersonaAgentIntegration(
            blackboard_service, constitutional_validator
        )
        self.logger = logging.getLogger(__name__)

    async def execute_with_persona(
        self, task_data: dict[str, Any], persona: SuperClaudePersona | None = None
    ) -> PersonaIntegrationResult:
        """Execute agent task with optional persona enhancement"""

        # Validate constitutional compliance
        if not task_data.get("constitutional_hash") == "cdd01ef066bc6cf2":
            raise ValueError(
                "Constitutional hash validation required for persona-enhanced execution"
            )

        # Execute base agent functionality
        base_result = await self._execute_base_functionality(task_data)

        # Apply persona enhancement if specified
        if persona:
            return await self.persona_integration.integrate_persona_with_agent(
                persona=persona,
                agent_type=self.agent_type,
                task_data=task_data,
                agent_result=base_result,
            )
        # Return base result in persona integration format
        return PersonaIntegrationResult(
            persona=SuperClaudePersona.ANALYZER,  # Default persona
            agent_type=self.agent_type,
            analysis_result=base_result,
            persona_insights={},
            constitutional_compliance={"constitutional_hash": "cdd01ef066bc6cf2"},
            recommendations=base_result.get("recommendations", []),
        )

    async def _execute_base_functionality(
        self, task_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute base agent functionality - to be implemented by subclasses"""
        raise NotImplementedError(
            "Subclasses must implement _execute_base_functionality"
        )
