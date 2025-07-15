"""
Constitutional Prompting Module for ACGS-PGP Phase 1 - Enhanced

This module implements constitutional prompting methodology that systematically
integrates AC principles as constitutional context in LLM prompts for policy synthesis.
Enhanced with Chain-of-Thought reasoning, retrieval-augmented generation, and
positive action-focused phrasing patterns for improved constitutional compliance.

Key Enhancements:
- Chain-of-Thought constitutional reasoning with intermediate steps
- Retrieval-augmented generation for constitutional precedent lookup
- Positive action-focused phrasing patterns for better alignment
- Red-teaming capabilities for adversarial validation
- Constitutional fidelity scoring mechanisms
"""

import logging
import re
from datetime import datetime, timezone
from typing import Any

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


try:
    from services.core.governance-synthesis.gs_service.app.services.ac_client import (
        ac_service_client,
    )
except ImportError:
    try:
        from ..services.ac_client import ac_service_client
    except ImportError:
        # Fallback for testing environments
        from unittest.mock import MagicMock

        ac_service_client = MagicMock()

# Import WINA constitutional integration
try:
    import logging

    from services.shared.wina.constitutional_integration import (
        WINAConstitutionalPrincipleAnalyzer,
        WINAConstitutionalUpdateService,
    )

    WINA_AVAILABLE = True
except ImportError:
    WINA_AVAILABLE = False
    _logger = logging.getLogger(__name__)
    _logger.warning("WINA constitutional integration not available")

logger = logging.getLogger(__name__)


class ConstitutionalPromptBuilder:
    """
    Builds constitutional prompts that integrate AC principles as constitutional context
    for LLM-based policy synthesis. Enhanced with WINA-informed constitutional updates.
    """

    def __init__(self, enable_wina_integration: bool = True):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """
        Initialize the Constitutional Prompt Builder.

        Args:
            enable_wina_integration: Whether to enable WINA constitutional integration
        """
        self.enable_wina_integration = enable_wina_integration and WINA_AVAILABLE

        # Initialize WINA services if available
        if self.enable_wina_integration:
            self.wina_analyzer = WINAConstitutionalPrincipleAnalyzer()
            self.wina_update_service = WINAConstitutionalUpdateService(
                analyzer=self.wina_analyzer
            )
            logger.info("WINA constitutional integration enabled")
        else:
            self.wina_analyzer = None
            self.wina_update_service = None
            logger.info("WINA constitutional integration disabled")

        # Initialize enhanced capabilities for Phase 1 improvements
        self.constitutional_precedents = {}
        self.precedent_cache_timestamp = None
        self.cot_templates = self._initialize_cot_templates()
        self.positive_action_patterns = self._initialize_positive_patterns()

        logger.info("Enhanced constitutional prompting capabilities initialized")

        self.constitutional_preamble = """
You are an AI Constitutional Interpreter for the ACGS-PGP (AI Compliance Governance System - Policy Generation Platform).
Your role is to synthesize governance policies that are constitutionally compliant with the established AC (Artificial Constitution) principles.

CONSTITUTIONAL FRAMEWORK:
The AC principles provided below form the constitutional foundation that MUST guide all policy synthesis.
Each principle has priority weights, scope definitions, and normative statements that constrain policy generation.

WINA OPTIMIZATION CONTEXT:
When WINA (Weight Informed Neuron Activation) optimization is enabled, constitutional principles may include
efficiency optimization constraints that balance performance gains with constitutional compliance.
These WINA-informed principles ensure that LLM optimization maintains constitutional integrity.

CONSTITUTIONAL COMPLIANCE REQUIREMENTS:
1. All generated policies MUST align with the constitutional principles
2. Higher priority principles take precedence in case of conflicts
3. Policies MUST respect the scope limitations of each principle
4. Generated rules MUST be traceable to their constitutional foundations
5. Constitutional fidelity is paramount - never violate core principles
"""

    async def build_constitutional_context(
        self,
        context: str,
        category: str | None = None,
        auth_token: str | None = None,
    ) -> dict[str, Any]:
        """
        Build constitutional context by fetching relevant AC principles for the given context.

        Args:
            context: The target context for policy synthesis
            category: Optional category filter for principles
            auth_token: Authentication token for AC service

        Returns:
            Dictionary containing constitutional context information
        """
        try:
            # Fetch active principles for the given context
            # This would use the new enhanced AC service endpoints
            relevant_principles = await self._fetch_relevant_principles(
                context, category, auth_token
            )

            constitutional_context = {
                "context": context,
                "category": category,
                "principles": relevant_principles,
                "principle_count": len(relevant_principles),
                "constitutional_hierarchy": self._build_principle_hierarchy(
                    relevant_principles
                ),
                "scope_constraints": self._extract_scope_constraints(
                    relevant_principles
                ),
                "normative_framework": self._build_normative_framework(
                    relevant_principles
                ),
            }

            logger.info(
                f"Built constitutional context for '{context}' with {len(relevant_principles)} principles"
            )
            return constitutional_context

        except Exception as e:
            logger.exception(
                f"Failed to build constitutional context for '{context}': {e}"
            )
            return {
                "context": context,
                "category": category,
                "principles": [],
                "principle_count": 0,
                "error": "An internal error occurred while building the constitutional context.",
            }

    async def _fetch_relevant_principles(
        self,
        context: str,
        category: str | None = None,
        auth_token: str | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch principles relevant to the given context and category."""
        try:
            # Use the enhanced AC service endpoints for context-specific principles
            relevant_principles_objs = (
                await ac_service_client.get_principles_for_context(
                    context=context, category=category, auth_token=auth_token
                )
            )

            # Convert to dictionaries and sort by priority weight
            relevant_principles = [
                principle.model_dump() for principle in relevant_principles_objs
            ]

            # Sort by priority weight (highest first)
            relevant_principles.sort(
                key=lambda p: p.get("priority_weight", 0.0), reverse=True
            )

            # If no context-specific principles found, fall back to category-based search
            if not relevant_principles and category:
                category_principles = (
                    await ac_service_client.get_principles_by_category(
                        category=category, auth_token=auth_token
                    )
                )
                relevant_principles = [
                    principle.model_dump() for principle in category_principles
                ]
                relevant_principles.sort(
                    key=lambda p: p.get("priority_weight", 0.0), reverse=True
                )

            # If still no principles, try keyword-based search
            if not relevant_principles:
                context_keywords = context.lower().split()
                keyword_principles = (
                    await ac_service_client.search_principles_by_keywords(
                        keywords=context_keywords, auth_token=auth_token
                    )
                )
                relevant_principles = [
                    principle.model_dump() for principle in keyword_principles
                ]
                relevant_principles.sort(
                    key=lambda p: p.get("priority_weight", 0.0), reverse=True
                )

            return relevant_principles

        except Exception as e:
            logger.exception(f"Failed to fetch relevant principles: {e}")
            # Fallback to the original method
            try:
                all_principles = await ac_service_client.list_principles(
                    auth_token=auth_token
                )

                relevant_principles = []
                for principle in all_principles:
                    principle_dict = principle.model_dump()

                    # Check if principle applies to the context
                    if self._principle_applies_to_context(principle_dict, context):
                        # Check category filter if provided
                        if (
                            category is None
                            or principle_dict.get("category") == category
                        ):
                            relevant_principles.append(principle_dict)

                # Sort by priority weight (highest first)
                relevant_principles.sort(
                    key=lambda p: p.get("priority_weight", 0.0), reverse=True
                )

                return relevant_principles
            except Exception as fallback_error:
                logger.exception(
                    f"Fallback principle fetch also failed: {fallback_error}"
                )
                return []

    def _principle_applies_to_context(
        self, principle: dict[str, Any], context: str
    ) -> bool:
        """Check if a principle applies to the given context."""
        scope = principle.get("scope", [])

        # If no scope defined, assume it applies to all contexts
        if not scope:
            return True

        # Check if context matches any scope item
        return context in scope or any(context.lower() in s.lower() for s in scope)

    def _build_principle_hierarchy(
        self, principles: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Build a hierarchical representation of principles based on priority weights."""
        hierarchy = []

        for principle in principles:
            priority_weight = principle.get("priority_weight", 0.0)

            # Categorize by priority level
            if priority_weight >= 0.8:
                priority_level = "CRITICAL"
            elif priority_weight >= 0.6:
                priority_level = "HIGH"
            elif priority_weight >= 0.4:
                priority_level = "MEDIUM"
            elif priority_weight >= 0.2:
                priority_level = "LOW"
            else:
                priority_level = "INFORMATIONAL"

            hierarchy.append(
                {
                    "id": principle.get("id"),
                    "name": principle.get("name"),
                    "priority_weight": priority_weight,
                    "priority_level": priority_level,
                    "category": principle.get("category"),
                    "normative_statement": principle.get("normative_statement"),
                }
            )

        return hierarchy

    def _extract_scope_constraints(
        self, principles: list[dict[str, Any]]
    ) -> dict[str, list[str]]:
        """Extract scope constraints from principles."""
        constraints = {}

        for principle in principles:
            principle_id = str(principle.get("id"))
            scope = principle.get("scope", [])
            constraints[principle_id] = scope

        return constraints

    def _build_normative_framework(
        self, principles: list[dict[str, Any]]
    ) -> dict[str, str]:
        """Build a normative framework from principle normative statements."""
        framework = {}

        for principle in principles:
            principle_id = str(principle.get("id"))
            normative_statement = principle.get("normative_statement")

            if normative_statement:
                framework[principle_id] = normative_statement

        return framework

    def _initialize_cot_templates(self) -> dict[str, str]:
        """Initialize Chain-of-Thought reasoning templates for constitutional analysis."""
        return {
            "constitutional_analysis": """
CONSTITUTIONAL REASONING PROCESS:

Step 1: PRINCIPLE IDENTIFICATION
- Identify which constitutional principles apply to this synthesis request
- Determine the priority hierarchy of applicable principles
- Note any potential conflicts between principles

Step 2: SCOPE ANALYSIS
- Analyze the scope constraints of each applicable principle
- Determine if the synthesis request falls within these scopes
- Identify any scope limitations that must be respected

Step 3: NORMATIVE INTERPRETATION
- Interpret the normative statements of applicable principles
- Determine what actions are required, permitted, or prohibited
- Resolve any ambiguities using constitutional interpretation methods

Step 4: CONFLICT RESOLUTION
- If principles conflict, apply the priority hierarchy
- Use the most restrictive interpretation that satisfies all principles
- Document the reasoning for conflict resolution decisions

Step 5: POLICY SYNTHESIS
- Generate policy rules that comply with all constitutional requirements
- Ensure traceability from each rule to its constitutional foundation
- Validate that the synthesized policy maintains constitutional integrity
""",
            "precedent_analysis": """
CONSTITUTIONAL PRECEDENT ANALYSIS:

Step 1: PRECEDENT IDENTIFICATION
- Search for similar constitutional interpretations in precedent database
- Identify relevant past decisions and their reasoning
- Note any established patterns of constitutional interpretation

Step 2: PRECEDENT EVALUATION
- Assess the relevance of identified precedents to current request
- Evaluate the constitutional reasoning used in precedents
- Determine if precedents support or constrain current synthesis

Step 3: PRECEDENT APPLICATION
- Apply relevant precedent reasoning to current synthesis
- Adapt precedent patterns to current constitutional context
- Ensure consistency with established constitutional interpretations
""",
            "positive_action_focus": """
POSITIVE ACTION-FOCUSED SYNTHESIS:

Step 1: POSITIVE FRAMING
- Frame constitutional requirements as positive actions to take
- Emphasize what the system SHOULD do rather than what it should not do
- Use constructive language that promotes beneficial outcomes

Step 2: CAPABILITY ENHANCEMENT
- Focus on how policies can enhance system capabilities
- Identify opportunities for positive constitutional compliance
- Design policies that actively promote constitutional values

Step 3: PROACTIVE COMPLIANCE
- Create policies that proactively ensure constitutional adherence
- Build in positive feedback mechanisms for constitutional compliance
- Design systems that naturally tend toward constitutional behavior
""",
        }

    def _initialize_positive_patterns(self) -> dict[str, list[str]]:
        """Initialize positive action-focused phrasing patterns."""
        return {
            "requirement_patterns": [
                "The system SHALL actively ensure",
                "The system MUST proactively implement",
                "The system SHALL continuously maintain",
                "The system MUST effectively provide",
                "The system SHALL systematically uphold",
            ],
            "capability_patterns": [
                "Enable the system to",
                "Empower the system to",
                "Enhance the system's ability to",
                "Strengthen the system's capacity to",
                "Improve the system's capability to",
            ],
            "outcome_patterns": [
                "to achieve constitutional compliance",
                "to promote constitutional values",
                "to ensure constitutional integrity",
                "to maintain constitutional fidelity",
                "to advance constitutional objectives",
            ],
            "monitoring_patterns": [
                "The system SHALL monitor and verify",
                "The system MUST track and validate",
                "The system SHALL observe and confirm",
                "The system MUST assess and ensure",
                "The system SHALL evaluate and maintain",
            ],
        }

    async def _retrieve_constitutional_precedents(
        self, context: str, principles: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Retrieve constitutional precedents for RAG enhancement."""
        try:
            # Check cache freshness (refresh every hour)
            current_time = datetime.now(timezone.utc)
            if (
                self.precedent_cache_timestamp is None
                or (current_time - self.precedent_cache_timestamp).seconds > 3600
            ):
                await self._refresh_precedent_cache()

            # Search for relevant precedents
            relevant_precedents = []
            context_keywords = context.lower().split()

            for precedent_data in self.constitutional_precedents.values():
                # Check if precedent is relevant to current context
                if any(
                    keyword in precedent_data.get("keywords", [])
                    for keyword in context_keywords
                ):
                    relevant_precedents.append(precedent_data)

                # Check if precedent involves similar principles
                precedent_principles = precedent_data.get("principle_ids", [])
                current_principle_ids = [str(p.get("id")) for p in principles]
                if any(pid in precedent_principles for pid in current_principle_ids):
                    relevant_precedents.append(precedent_data)

            # Sort by relevance score
            relevant_precedents.sort(
                key=lambda p: p.get("relevance_score", 0.0), reverse=True
            )

            return {
                "precedents": relevant_precedents[:5],  # Top 5 most relevant
                "total_found": len(relevant_precedents),
                "cache_timestamp": self.precedent_cache_timestamp,
            }

        except Exception as e:
            logger.exception(f"Failed to retrieve constitutional precedents: {e}")
            return {"precedents": [], "total_found": 0, "error": str(e)}

    async def _refresh_precedent_cache(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Refresh the constitutional precedent cache."""
        try:
            # In a real implementation, this would fetch from a precedent database
            # For now, we'll use mock precedents
            self.constitutional_precedents = {
                "privacy_data_protection": {
                    "keywords": ["privacy", "data", "protection", "personal"],
                    "principle_ids": ["1", "2", "5"],
                    "reasoning": "Privacy principles require proactive data protection",
                    "outcome": "Implemented encryption and access controls",
                    "relevance_score": 0.9,
                },
                "fairness_algorithmic": {
                    "keywords": ["fairness", "bias", "discrimination", "algorithmic"],
                    "principle_ids": ["3", "4", "7"],
                    "reasoning": "Fairness requires bias detection and mitigation",
                    "outcome": "Deployed bias monitoring and correction systems",
                    "relevance_score": 0.85,
                },
                "transparency_accountability": {
                    "keywords": [
                        "transparency",
                        "accountability",
                        "audit",
                        "explainable",
                    ],
                    "principle_ids": ["6", "8", "9"],
                    "reasoning": "Transparency requires explainable decision processes",
                    "outcome": "Implemented audit trails and explanation systems",
                    "relevance_score": 0.8,
                },
            }

            self.precedent_cache_timestamp = datetime.now(timezone.utc)
            logger.info("Constitutional precedent cache refreshed")

        except Exception as e:
            logger.exception(f"Failed to refresh precedent cache: {e}")

    async def build_constitutional_prompt(
        self,
        constitutional_context: dict[str, Any],
        synthesis_request: str,
        target_format: str = "datalog",
        enable_cot: bool = True,
        enable_rag: bool = True,
    ) -> str:
        """
        Build an enhanced constitutional prompt with Chain-of-Thought reasoning and RAG.

        Args:
            constitutional_context: Constitutional context built by build_constitutional_context
            synthesis_request: The specific synthesis request
            target_format: Target format for generated policies (datalog, rego, etc.)
            enable_cot: Whether to enable Chain-of-Thought reasoning
            enable_rag: Whether to enable Retrieval-Augmented Generation

        Returns:
            Enhanced constitutional prompt for LLM
        """
        principles = constitutional_context.get("principles", [])
        hierarchy = constitutional_context.get("constitutional_hierarchy", [])
        context = constitutional_context.get("context", "general")

        # Retrieve constitutional precedents if RAG is enabled
        precedent_data = {}
        if enable_rag:
            precedent_data = await self._retrieve_constitutional_precedents(
                context, principles
            )

        # Build enhanced sections
        constitutional_principles_section = self._build_enhanced_principles_section(
            principles, hierarchy, precedent_data
        )

        # Build Chain-of-Thought reasoning section
        cot_section = ""
        if enable_cot:
            cot_section = self._build_cot_reasoning_section(
                constitutional_context, synthesis_request, precedent_data
            )

        # Build enhanced synthesis instructions with positive action patterns
        synthesis_instructions = self._build_enhanced_synthesis_instructions(
            constitutional_context, synthesis_request, target_format
        )

        # Combine all sections with enhanced structure
        full_prompt = f"""
{self.constitutional_preamble}

{constitutional_principles_section}

{cot_section}

{synthesis_instructions}

SYNTHESIS REQUEST:
{synthesis_request}

TARGET FORMAT: {target_format.upper()}

ENHANCED CONSTITUTIONAL COMPLIANCE VERIFICATION:
Follow this systematic verification process:

1. CONSTITUTIONAL ALIGNMENT CHECK:
   - Verify all generated policies align with constitutional principles
   - Confirm higher priority principles take precedence
   - Validate scope constraints are respected

2. POSITIVE ACTION VALIDATION:
   - Ensure policies use positive, action-focused language
   - Confirm policies promote beneficial outcomes
   - Validate proactive compliance mechanisms

3. PRECEDENT CONSISTENCY:
   - Check consistency with constitutional precedents
   - Apply established interpretation patterns
   - Maintain constitutional reasoning continuity

4. TRACEABILITY VERIFICATION:
   - Document constitutional foundation for each rule
   - Provide clear reasoning chain from principles to policies
   - Ensure transparent constitutional interpretation

5. FINAL CONSTITUTIONAL INTEGRITY CHECK:
   - Confirm no constitutional violations exist
   - Validate overall constitutional coherence
   - Ensure synthesis maintains constitutional fidelity

Please provide your constitutionally compliant policy synthesis following this enhanced framework:
"""

        return full_prompt.strip()

    def _build_enhanced_principles_section(
        self,
        principles: list[dict[str, Any]],
        hierarchy: list[dict[str, Any]],
        precedent_data: dict[str, Any],
    ) -> str:
        """Build enhanced constitutional principles section with precedent context."""
        if not principles:
            return "CONSTITUTIONAL PRINCIPLES: None applicable to this context."

        section = "ENHANCED CONSTITUTIONAL PRINCIPLES (with precedent context):\n\n"

        # Add precedent context if available
        precedents = precedent_data.get("precedents", [])
        if precedents:
            section += "RELEVANT CONSTITUTIONAL PRECEDENTS:\n"
            for i, precedent in enumerate(precedents[:3], 1):  # Top 3 precedents
                section += (
                    f"{i}. {precedent.get('reasoning', 'No reasoning available')}\n"
                )
                section += (
                    f"   Outcome: {precedent.get('outcome', 'No outcome recorded')}\n"
                )
            section += "\n"

        section += "APPLICABLE PRINCIPLES (in priority order):\n\n"

        for i, principle in enumerate(principles, 1):
            priority_weight = principle.get("priority_weight", 0.0)
            priority_info = next(
                (h for h in hierarchy if h["id"] == principle["id"]), {}
            )
            priority_level = priority_info.get("priority_level", "UNSPECIFIED")

            # Apply positive action patterns to principle description
            enhanced_content = self._apply_positive_patterns(
                principle.get("content", "")
            )

            section += f"{i}. PRINCIPLE {principle['id']}: {principle['name']}\n"
            section += f"   Priority: {priority_weight:.2f} ({priority_level})\n"
            section += f"   Category: {principle.get('category', 'Unspecified')}\n"
            section += f"   Enhanced Content: {enhanced_content}\n"

            if principle.get("normative_statement"):
                enhanced_normative = self._apply_positive_patterns(
                    principle["normative_statement"]
                )
                section += f"   Normative Statement: {enhanced_normative}\n"

            if principle.get("scope"):
                section += f"   Scope: {', '.join(principle['scope'])}\n"

            if principle.get("constraints"):
                section += f"   Constraints: {principle['constraints']}\n"

            section += "\n"

        return section

    def _build_cot_reasoning_section(
        self,
        constitutional_context: dict[str, Any],
        synthesis_request: str,
        precedent_data: dict[str, Any],
    ) -> str:
        """Build Chain-of-Thought reasoning section for constitutional analysis."""
        principles = constitutional_context.get("principles", [])
        context = constitutional_context.get("context", "general")

        section = "CHAIN-OF-THOUGHT CONSTITUTIONAL REASONING:\n\n"

        # Add constitutional analysis template
        section += self.cot_templates["constitutional_analysis"]

        # Add precedent analysis if precedents are available
        if precedent_data.get("precedents"):
            section += "\n" + self.cot_templates["precedent_analysis"]

        # Add positive action focus
        section += "\n" + self.cot_templates["positive_action_focus"]

        # Add context-specific reasoning guidance
        section += f"""

CONTEXT-SPECIFIC REASONING GUIDANCE:
Current Context: {context}
Synthesis Request: {synthesis_request}
Applicable Principles: {len(principles)}

REASONING STEPS TO FOLLOW:
1. Analyze how each principle applies to the specific context
2. Identify potential conflicts and resolution strategies
3. Consider precedent patterns for similar contexts
4. Apply positive action-focused interpretation
5. Synthesize policies that proactively ensure compliance

"""

        return section

    def _build_enhanced_synthesis_instructions(
        self,
        constitutional_context: dict[str, Any],
        synthesis_request: str,
        target_format: str,
    ) -> str:
        """Build enhanced synthesis instructions with positive action patterns."""
        context = constitutional_context.get("context", "general")
        principle_count = constitutional_context.get("principle_count", 0)

        return f"""
ENHANCED SYNTHESIS INSTRUCTIONS:
Context: {context}
Applicable Principles: {principle_count}

You must synthesize governance policies using this enhanced framework:

1. CONSTITUTIONAL COMPLIANCE REQUIREMENTS:
   - Ensure ALL applicable principles are satisfied
   - Apply priority hierarchy for conflict resolution
   - Respect scope constraints and normative statements
   - Generate {target_format} rules that are enforceable and verifiable

2. POSITIVE ACTION-FOCUSED SYNTHESIS:
   - Use positive, constructive language patterns
   - Frame requirements as capabilities to be enabled
   - Focus on proactive compliance mechanisms
   - Emphasize beneficial outcomes and system enhancements

3. CHAIN-OF-THOUGHT REASONING:
   - Follow the constitutional reasoning process outlined above
   - Document your reasoning at each step
   - Show how principles influence policy decisions
   - Provide clear traceability from principles to rules

4. PRECEDENT-INFORMED SYNTHESIS:
   - Consider relevant constitutional precedents
   - Apply established interpretation patterns
   - Maintain consistency with prior constitutional decisions
   - Adapt precedent reasoning to current context

5. ENHANCED CONFLICT RESOLUTION:
   - Use systematic conflict resolution methodology
   - Apply constitutional interpretation principles
   - Choose interpretations that maximize constitutional compliance
   - Document conflict resolution reasoning

POSITIVE LANGUAGE PATTERNS TO USE:
- "The system SHALL actively ensure..." instead of "The system shall not..."
- "Enable the system to..." instead of "Prevent the system from..."
- "Proactively implement..." instead of "Avoid..."
- "Continuously maintain..." instead of "Do not compromise..."
"""

    def _apply_positive_patterns(self, text: str) -> str:
        """Apply positive action-focused patterns to text."""
        if not text:
            return text

        enhanced_text = text

        # Convert negative patterns to positive ones
        negative_to_positive = {
            r"shall not\s+(\w+)": r"shall actively prevent \1",
            r"must not\s+(\w+)": r"must proactively avoid \1",
            r"do not\s+(\w+)": r"actively ensure against \1",
            r"cannot\s+(\w+)": r"must maintain safeguards against \1",
            r"should not\s+(\w+)": r"should actively prevent \1",
        }

        for pattern, replacement in negative_to_positive.items():
            enhanced_text = re.sub(
                pattern, replacement, enhanced_text, flags=re.IGNORECASE
            )

        return enhanced_text

    def _build_principles_section(
        self, principles: list[dict[str, Any]], hierarchy: list[dict[str, Any]]
    ) -> str:
        """Build the constitutional principles section of the prompt."""
        if not principles:
            return "CONSTITUTIONAL PRINCIPLES: None applicable to this context."

        section = "CONSTITUTIONAL PRINCIPLES (in priority order):\n\n"

        for i, principle in enumerate(principles, 1):
            priority_weight = principle.get("priority_weight", 0.0)
            priority_info = next(
                (h for h in hierarchy if h["id"] == principle["id"]), {}
            )
            priority_level = priority_info.get("priority_level", "UNSPECIFIED")

            section += f"{i}. PRINCIPLE {principle['id']}: {principle['name']}\n"
            section += f"   Priority: {priority_weight:.2f} ({priority_level})\n"
            section += f"   Category: {principle.get('category', 'Unspecified')}\n"
            section += f"   Content: {principle['content']}\n"

            if principle.get("normative_statement"):
                section += (
                    f"   Normative Statement: {principle['normative_statement']}\n"
                )

            if principle.get("scope"):
                section += f"   Scope: {', '.join(principle['scope'])}\n"

            if principle.get("constraints"):
                section += f"   Constraints: {principle['constraints']}\n"

            section += "\n"

        return section

    def _build_synthesis_instructions(
        self,
        constitutional_context: dict[str, Any],
        synthesis_request: str,
        target_format: str,
    ) -> str:
        """Build synthesis instructions based on constitutional context."""
        context = constitutional_context.get("context", "general")
        principle_count = constitutional_context.get("principle_count", 0)

        return f"""
SYNTHESIS INSTRUCTIONS:
Context: {context}
Applicable Principles: {principle_count}

You must synthesize governance policies that:
1. Are constitutionally compliant with ALL applicable principles above
2. Respect the priority hierarchy (higher priority principles override lower ones)
3. Stay within the scope constraints of each principle
4. Generate {target_format} rules that are enforceable and verifiable
5. Include constitutional traceability (which principles influenced each rule)

CONSTITUTIONAL CONFLICT RESOLUTION:
If principles conflict, resolve using this hierarchy:
1. Higher priority_weight principles take precedence
2. More specific scope constraints override general ones
3. Explicit normative statements guide interpretation
4. When in doubt, choose the most restrictive interpretation that satisfies all principles
"""

    async def build_wina_enhanced_constitutional_context(
        self,
        context: str,
        category: str | None = None,
        auth_token: str | None = None,
        optimization_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Build WINA-enhanced constitutional context with optimization analysis.

        Args:
            context: The target context for policy synthesis
            category: Optional category filter for principles
            auth_token: Authentication token for AC service
            optimization_context: WINA optimization context

        Returns:
            Enhanced constitutional context with WINA analysis
        """
        # Build base constitutional context
        constitutional_context = await self.build_constitutional_context(
            context, category, auth_token
        )

        # Add WINA enhancements if available
        if self.enable_wina_integration and self.wina_analyzer:
            try:
                # Set default optimization context
                if not optimization_context:
                    optimization_context = {
                        "target_gflops_reduction": 0.5,
                        "min_accuracy_retention": 0.95,
                        "optimization_mode": "conservative",
                        "context": context,
                    }

                # Analyze principles for WINA optimization
                wina_analysis_results = {}
                principles = constitutional_context.get("principles", [])

                for principle in principles:
                    try:
                        analysis = await self.wina_analyzer.analyze_principle_for_wina_optimization(
                            principle, optimization_context
                        )
                        wina_analysis_results[str(principle.get("id"))] = analysis

                    except Exception as e:
                        logger.exception(
                            f"WINA analysis failed for principle {principle.get('id')}: {e}"
                        )
                        wina_analysis_results[str(principle.get("id"))] = {
                            "error": str(e),
                            "optimization_potential": 0.0,
                        }

                # Add WINA enhancements to constitutional context
                constitutional_context.update(
                    {
                        "wina_enabled": True,
                        "wina_analysis": wina_analysis_results,
                        "optimization_context": optimization_context,
                        "wina_summary": self._build_wina_summary(wina_analysis_results),
                        "optimization_recommendations": self._build_optimization_recommendations(
                            wina_analysis_results
                        ),
                    }
                )

                logger.info(
                    f"Enhanced constitutional context with WINA analysis for {len(principles)} principles"
                )

            except Exception as e:
                logger.exception(f"WINA enhancement failed: {e}")
                constitutional_context["wina_enabled"] = False
                constitutional_context["wina_error"] = str(e)
        else:
            constitutional_context["wina_enabled"] = False

        return constitutional_context

    def _build_wina_summary(
        self, wina_analysis_results: dict[str, Any]
    ) -> dict[str, Any]:
        """Build summary of WINA analysis results."""
        if not wina_analysis_results:
            return {"total_principles": 0, "optimization_potential": 0.0}

        total_principles = len(wina_analysis_results)
        high_potential = len(
            [
                r
                for r in wina_analysis_results.values()
                if r.get("optimization_potential", 0) > 0.7
            ]
        )
        medium_potential = len(
            [
                r
                for r in wina_analysis_results.values()
                if 0.4 <= r.get("optimization_potential", 0) <= 0.7
            ]
        )
        low_potential = len(
            [
                r
                for r in wina_analysis_results.values()
                if r.get("optimization_potential", 0) < 0.4
            ]
        )

        avg_potential = (
            sum(
                r.get("optimization_potential", 0)
                for r in wina_analysis_results.values()
            )
            / total_principles
        )

        return {
            "total_principles": total_principles,
            "high_potential_count": high_potential,
            "medium_potential_count": medium_potential,
            "low_potential_count": low_potential,
            "average_optimization_potential": avg_potential,
            "optimization_feasible": avg_potential > 0.3,
        }

    def _build_optimization_recommendations(
        self, wina_analysis_results: dict[str, Any]
    ) -> list[str]:
        """Build optimization recommendations based on WINA analysis."""
        recommendations = []

        if not wina_analysis_results:
            return ["No WINA analysis available"]

        high_potential_principles = [
            principle_id
            for principle_id, analysis in wina_analysis_results.items()
            if analysis.get("optimization_potential", 0) > 0.7
        ]

        if high_potential_principles:
            recommendations.append(
                f"Consider aggressive WINA optimization for principles: {', '.join(high_potential_principles)}"
            )

        safety_critical_principles = [
            principle_id
            for principle_id, analysis in wina_analysis_results.items()
            if "safety_critical_principle" in analysis.get("risk_factors", [])
        ]

        if safety_critical_principles:
            recommendations.append(
                f"Implement additional safety monitoring for: {', '.join(safety_critical_principles)}"
            )

        recommendations.extend(
            (
                "Monitor constitutional compliance continuously during optimization",
                "Implement fallback mechanisms for optimization failures",
            )
        )

        return recommendations

    def build_wina_enhanced_constitutional_prompt(
        self,
        constitutional_context: dict[str, Any],
        synthesis_request: str,
        target_format: str = "datalog",
    ) -> str:
        """
        Build WINA-enhanced constitutional prompt with optimization context.

        Args:
            constitutional_context: WINA-enhanced constitutional context
            synthesis_request: The specific synthesis request
            target_format: Target format for generated policies

        Returns:
            WINA-enhanced constitutional prompt for LLM
        """
        # Build base prompt
        base_prompt = self.build_constitutional_prompt(
            constitutional_context, synthesis_request, target_format
        )

        # Add WINA enhancements if available
        if constitutional_context.get("wina_enabled"):
            wina_section = self._build_wina_optimization_section(constitutional_context)

            # Insert WINA section before synthesis instructions
            prompt_parts = base_prompt.split("SYNTHESIS INSTRUCTIONS:")
            if len(prompt_parts) == 2:
                enhanced_prompt = f"{prompt_parts[0]}\n{wina_section}\n\nSYNTHESIS INSTRUCTIONS:{prompt_parts[1]}"
            else:
                enhanced_prompt = f"{base_prompt}\n\n{wina_section}"
        else:
            enhanced_prompt = base_prompt

        return enhanced_prompt

    def _build_wina_optimization_section(
        self, constitutional_context: dict[str, Any]
    ) -> str:
        """Build WINA optimization section for constitutional prompt."""
        wina_summary = constitutional_context.get("wina_summary", {})
        optimization_recommendations = constitutional_context.get(
            "optimization_recommendations", []
        )
        optimization_context = constitutional_context.get("optimization_context", {})

        avg_potential = wina_summary.get("average_optimization_potential", 0.0)
        section = f"""
WINA OPTIMIZATION CONTEXT:
Optimization Mode: {optimization_context.get("optimization_mode", "conservative")}
Target GFLOPs Reduction: {optimization_context.get("target_gflops_reduction", 0.5)}
Minimum Accuracy Retention: {optimization_context.get("min_accuracy_retention", 0.95)}

OPTIMIZATION ANALYSIS SUMMARY:
- Total Principles Analyzed: {wina_summary.get("total_principles", 0)}
- High Optimization Potential: {wina_summary.get("high_potential_count", 0)}
- Medium Optimization Potential: {wina_summary.get("medium_potential_count", 0)}
- Low Optimization Potential: {wina_summary.get("low_potential_count", 0)}
- Average Optimization Potential: {avg_potential:.3f}
- Optimization Feasible: {wina_summary.get("optimization_feasible", False)}

OPTIMIZATION RECOMMENDATIONS:
"""

        for i, recommendation in enumerate(optimization_recommendations, 1):
            section += f"{i}. {recommendation}\n"

        section += """
WINA CONSTITUTIONAL CONSTRAINTS:
When generating policies, ensure that:
1. WINA optimization constraints are included where applicable
2. Efficiency gains do not compromise constitutional compliance
3. Fallback mechanisms are specified for optimization failures
4. Performance monitoring requirements are included
5. Constitutional fidelity is maintained during optimization
"""

        return section


# Global instance for use across the GS service
constitutional_prompt_builder = ConstitutionalPromptBuilder()
