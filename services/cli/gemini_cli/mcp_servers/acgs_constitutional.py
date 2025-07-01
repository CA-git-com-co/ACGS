"""
ACGS Constitutional MCP Server
Provides constitutional compliance checking and policy verification
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from mcp import Server, Tool, Resource
from mcp.types import TextContent

logger = logging.getLogger(__name__)


@dataclass
class ConstitutionalPrinciple:
    """Represents a constitutional principle"""
    id: str
    name: str
    description: str
    enforcement_level: str  # strict, moderate, advisory


class ACGSConstitutionalServer:
    """MCP server for constitutional compliance"""
    
    def __init__(self):
        self.server = Server("acgs-constitutional")
        self.constitutional_hash = os.environ.get("CONSTITUTIONAL_HASH", "cdd01ef066bc6cf2")
        self.principles = self._load_principles()
        self._setup_tools()
        self._setup_resources()
    
    def _load_principles(self) -> Dict[str, ConstitutionalPrinciple]:
        """Load constitutional principles"""
        return {
            "non_maleficence": ConstitutionalPrinciple(
                id="non_maleficence",
                name="Non-Maleficence",
                description="Agents must not cause harm to humans, systems, or data",
                enforcement_level="strict"
            ),
            "human_autonomy": ConstitutionalPrinciple(
                id="human_autonomy",
                name="Human Autonomy",
                description="Respect human decision-making authority",
                enforcement_level="strict"
            ),
            "transparency": ConstitutionalPrinciple(
                id="transparency",
                name="Transparency",
                description="All actions must be auditable and explainable",
                enforcement_level="strict"
            ),
            "least_privilege": ConstitutionalPrinciple(
                id="least_privilege",
                name="Least Privilege",
                description="Agents operate with minimum necessary permissions",
                enforcement_level="moderate"
            ),
            "data_protection": ConstitutionalPrinciple(
                id="data_protection",
                name="Data Protection",
                description="Protect sensitive data and privacy",
                enforcement_level="strict"
            )
        }
    
    def _setup_tools(self):
        """Set up MCP tools"""
        
        @self.server.tool()
        async def check_constitutional_compliance(
            action: str,
            context: Dict[str, Any],
            strict_mode: bool = True
        ) -> Tool:
            """Check if an action complies with constitutional principles"""
            return Tool(
                name="check_constitutional_compliance",
                description="Verify action compliance with ACGS constitutional principles",
                input_schema={
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "description": "Action to check"},
                        "context": {"type": "object", "description": "Context for the action"},
                        "strict_mode": {"type": "boolean", "description": "Enable strict checking"}
                    },
                    "required": ["action", "context"]
                },
                handler=lambda params: self._check_compliance(
                    params["action"],
                    params["context"],
                    params.get("strict_mode", True)
                )
            )
        
        @self.server.tool()
        async def verify_policy(
            policy_text: str,
            policy_type: str
        ) -> Tool:
            """Verify a policy against constitutional principles"""
            return Tool(
                name="verify_policy",
                description="Verify policy compliance with constitutional framework",
                input_schema={
                    "type": "object",
                    "properties": {
                        "policy_text": {"type": "string", "description": "Policy text to verify"},
                        "policy_type": {"type": "string", "description": "Type of policy"}
                    },
                    "required": ["policy_text", "policy_type"]
                },
                handler=lambda params: self._verify_policy(
                    params["policy_text"],
                    params["policy_type"]
                )
            )
        
        @self.server.tool()
        async def analyze_risk(
            operation: Dict[str, Any]
        ) -> Tool:
            """Analyze constitutional risk of an operation"""
            return Tool(
                name="analyze_risk",
                description="Analyze constitutional risk level of an operation",
                input_schema={
                    "type": "object",
                    "properties": {
                        "operation": {"type": "object", "description": "Operation details"}
                    },
                    "required": ["operation"]
                },
                handler=lambda params: self._analyze_risk(params["operation"])
            )
    
    def _setup_resources(self):
        """Set up MCP resources"""
        
        @self.server.resource()
        async def constitutional_principles() -> Resource:
            """Get all constitutional principles"""
            content = json.dumps({
                "hash": self.constitutional_hash,
                "principles": [
                    {
                        "id": p.id,
                        "name": p.name,
                        "description": p.description,
                        "enforcement_level": p.enforcement_level
                    }
                    for p in self.principles.values()
                ]
            }, indent=2)
            
            return Resource(
                uri="acgs://constitutional/principles",
                name="Constitutional Principles",
                description="ACGS constitutional principles and framework",
                mime_type="application/json",
                text=content
            )
        
        @self.server.resource()
        async def compliance_guidelines() -> Resource:
            """Get compliance guidelines"""
            guidelines = {
                "code_execution": {
                    "required_checks": ["sandbox_isolation", "resource_limits", "no_network_access"],
                    "approval_threshold": 0.8
                },
                "data_access": {
                    "required_checks": ["permission_verification", "data_classification", "audit_logging"],
                    "approval_threshold": 0.9
                },
                "system_modification": {
                    "required_checks": ["change_impact_analysis", "rollback_plan", "human_approval"],
                    "approval_threshold": 0.95
                }
            }
            
            return Resource(
                uri="acgs://constitutional/guidelines",
                name="Compliance Guidelines",
                description="Guidelines for constitutional compliance",
                mime_type="application/json",
                text=json.dumps(guidelines, indent=2)
            )
    
    async def _check_compliance(self, action: str, context: Dict, strict_mode: bool) -> Dict:
        """Check compliance implementation"""
        compliance_score = 0.0
        violations = []
        recommendations = []
        
        # Check each principle
        for principle_id, principle in self.principles.items():
            if principle_id == "non_maleficence":
                # Check for harmful actions
                harmful_keywords = ["delete", "destroy", "kill", "harm", "damage"]
                if any(keyword in action.lower() for keyword in harmful_keywords):
                    if strict_mode or principle.enforcement_level == "strict":
                        violations.append(f"Potential violation of {principle.name}")
                    else:
                        recommendations.append(f"Review for {principle.name} compliance")
            
            elif principle_id == "transparency":
                # Check for audit trail
                if not context.get("audit_enabled", True):
                    violations.append(f"Violation of {principle.name}: No audit trail")
            
            elif principle_id == "least_privilege":
                # Check permissions
                required_perms = context.get("required_permissions", [])
                if len(required_perms) > 3:
                    recommendations.append(f"Consider reducing permissions per {principle.name}")
        
        # Calculate compliance score
        total_checks = len(self.principles)
        passed_checks = total_checks - len(violations)
        compliance_score = passed_checks / total_checks
        
        return {
            "compliant": len(violations) == 0,
            "compliance_score": compliance_score,
            "violations": violations,
            "recommendations": recommendations,
            "constitutional_hash": self.constitutional_hash
        }
    
    async def _verify_policy(self, policy_text: str, policy_type: str) -> Dict:
        """Verify policy implementation"""
        issues = []
        suggestions = []
        
        # Basic policy checks
        if len(policy_text) < 50:
            issues.append("Policy text too short - needs more detail")
        
        if policy_type == "data_access":
            required_sections = ["purpose", "scope", "retention", "security"]
            for section in required_sections:
                if section not in policy_text.lower():
                    issues.append(f"Missing required section: {section}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions,
            "policy_type": policy_type,
            "constitutional_hash": self.constitutional_hash
        }
    
    async def _analyze_risk(self, operation: Dict) -> Dict:
        """Analyze risk implementation"""
        risk_factors = []
        risk_score = 0.0
        
        # Analyze operation type
        op_type = operation.get("type", "")
        if op_type in ["code_execution", "system_modification"]:
            risk_factors.append("High-risk operation type")
            risk_score += 0.3
        
        # Check for sensitive data
        if operation.get("involves_pii", False):
            risk_factors.append("Involves personally identifiable information")
            risk_score += 0.25
        
        # Check permissions
        perms = operation.get("required_permissions", [])
        if len(perms) > 5:
            risk_factors.append("Requires extensive permissions")
            risk_score += 0.2
        
        # Determine risk level
        if risk_score < 0.3:
            risk_level = "low"
        elif risk_score < 0.6:
            risk_level = "medium"
        else:
            risk_level = "high"
        
        return {
            "risk_level": risk_level,
            "risk_score": min(risk_score, 1.0),
            "risk_factors": risk_factors,
            "requires_human_review": risk_level == "high",
            "constitutional_hash": self.constitutional_hash
        }
    
    async def run(self):
        """Run the MCP server"""
        async with self.server:
            await self.server.serve()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    server = ACGSConstitutionalServer()
    asyncio.run(server.run())