"""
Policy-to-SMT Compiler for Formal Verification

Comprehensive compiler that translates governance policies and constitutional principles
into SMT-LIB format for formal verification with Z3 solver.
"""

import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any

import yaml
import z3

logger = logging.getLogger(__name__)


class PolicyType(Enum):
    """Types of policies that can be compiled to SMT."""

    ACCESS_CONTROL = "access_control"
    GOVERNANCE_RULE = "governance_rule"
    CONSTITUTIONAL_PRINCIPLE = "constitutional_principle"
    COMPLIANCE_REQUIREMENT = "compliance_requirement"


@dataclass
class SMTVariable:
    """SMT variable with type information."""

    name: str
    var_type: str  # bool, int, string
    z3_var: Any
    domain: list[str] | None = None


@dataclass
class SMTConstraint:
    """SMT constraint with metadata."""

    constraint: Any  # Z3 constraint
    source_policy: str
    policy_type: PolicyType
    priority: int = 1


class PolicySMTCompiler:
    """
    Comprehensive compiler for translating policies to SMT constraints.

    Supports governance policies, constitutional principles, and compliance
    requirements with formal verification capabilities.
    """

    def __init__(self):
        """Initialize the policy-to-SMT compiler."""
        self.variables: dict[str, SMTVariable] = {}
        self.constraints: list[SMTConstraint] = []
        self.constitutional_hash = "cdd01ef066bc6cf2"

        # Predefined domains for common policy elements
        self.domains = {
            "roles": ["admin", "user", "auditor", "guest"],
            "resources": ["data", "system", "config", "logs"],
            "actions": ["read", "write", "execute", "delete"],
            "compliance_levels": ["strict", "moderate", "advisory"],
        }

        logger.info("Policy-to-SMT compiler initialized")

    def compile_governance_policy(
        self, policy_content: str, policy_id: str
    ) -> list[SMTConstraint]:
        """
        Compile governance policy to SMT constraints.

        Args:
            policy_content: Policy content (OPA Rego or structured format)
            policy_id: Unique policy identifier

        Returns:
            List of SMT constraints
        """
        try:
            constraints = []

            # Detect policy format
            if "package" in policy_content and "allow" in policy_content:
                # OPA Rego format
                constraints.extend(self._compile_rego_policy(policy_content, policy_id))
            elif policy_content.strip().startswith("{"):
                # JSON format
                import json

                policy_data = json.loads(policy_content)
                constraints.extend(
                    self._compile_structured_policy(policy_data, policy_id)
                )
            else:
                # Datalog-style rules
                constraints.extend(
                    self._compile_datalog_policy(policy_content, policy_id)
                )

            self.constraints.extend(constraints)
            logger.info(
                f"Compiled policy {policy_id} to {len(constraints)} SMT constraints"
            )

            return constraints

        except Exception as e:
            logger.exception(f"Failed to compile policy {policy_id}: {e}")
            return []

    def compile_constitutional_principles(
        self, principles_file: str
    ) -> list[SMTConstraint]:
        """
        Compile constitutional principles from YAML file to SMT constraints.

        Args:
            principles_file: Path to principles.yaml file

        Returns:
            List of SMT constraints for constitutional principles
        """
        try:
            with open(principles_file, encoding="utf-8") as f:
                principles_data = yaml.safe_load(f)

            constraints = []

            # Process constitutional principles
            if "constitutional_principles" in principles_data:
                for principle_name, principle_data in principles_data[
                    "constitutional_principles"
                ].items():
                    principle_constraints = self._compile_constitutional_principle(
                        principle_name, principle_data
                    )
                    constraints.extend(principle_constraints)

            # Process governance requirements
            if "governance_requirements" in principles_data:
                for req_name, req_data in principles_data[
                    "governance_requirements"
                ].items():
                    req_constraints = self._compile_governance_requirement(
                        req_name, req_data
                    )
                    constraints.extend(req_constraints)

            self.constraints.extend(constraints)
            logger.info(
                f"Compiled constitutional principles to {len(constraints)} SMT constraints"
            )

            return constraints

        except Exception as e:
            logger.exception(f"Failed to compile constitutional principles: {e}")
            return []

    def _compile_rego_policy(
        self, rego_content: str, policy_id: str
    ) -> list[SMTConstraint]:
        """Compile OPA Rego policy to SMT constraints."""
        constraints = []

        try:
            # Extract allow rules
            allow_rules = re.findall(
                r"allow\s*(?:if\s*)?\{([^}]+)\}", rego_content, re.DOTALL
            )

            for i, rule_body in enumerate(allow_rules):
                rule_id = f"{policy_id}_allow_{i}"

                # Parse conditions in rule body
                conditions = self._parse_rego_conditions(rule_body)

                if conditions:
                    # Create SMT constraint for allow rule
                    allow_var = self._get_or_create_variable(f"allow_{rule_id}", "bool")
                    condition_constraint = (
                        z3.And(*conditions) if len(conditions) > 1 else conditions[0]
                    )

                    # allow_rule => conditions
                    constraint = z3.Implies(allow_var.z3_var, condition_constraint)

                    constraints.append(
                        SMTConstraint(
                            constraint=constraint,
                            source_policy=policy_id,
                            policy_type=PolicyType.ACCESS_CONTROL,
                            priority=1,
                        )
                    )

        except Exception as e:
            logger.exception(f"Failed to compile Rego policy {policy_id}: {e}")

        return constraints

    def _parse_rego_conditions(self, rule_body: str) -> list[Any]:
        """Parse conditions from Rego rule body."""
        conditions = []

        # Split by newlines and clean up
        lines = [line.strip() for line in rule_body.split("\n") if line.strip()]

        for line in lines:
            # Skip comments
            if line.startswith("#"):
                continue

            # Parse different condition types
            if "==" in line:
                # Equality condition
                left, right = line.split("==", 1)
                left = left.strip()
                right = right.strip().strip('"')

                condition = self._create_equality_condition(left, right)
                if condition is not None:
                    conditions.append(condition)

            elif "input." in line:
                # Input validation
                condition = self._create_input_condition(line)
                if condition is not None:
                    conditions.append(condition)

        return conditions

    def _create_equality_condition(self, left: str, right: str) -> Any | None:
        """Create SMT equality condition."""
        try:
            # Handle input.role == "admin" style conditions
            if left.startswith("input."):
                var_name = left.replace("input.", "")
                var = self._get_or_create_variable(var_name, "string")

                # Create string equality
                return var.z3_var == z3.StringVal(right)

            # Handle other equality patterns
            left_var = self._get_or_create_variable(left, "string")
            return left_var.z3_var == z3.StringVal(right)

        except Exception as e:
            logger.warning(
                f"Failed to create equality condition for {left} == {right}: {e}"
            )
            return None

    def _create_input_condition(self, condition_line: str) -> Any | None:
        """Create SMT condition for input validation."""
        try:
            # Handle input.field patterns
            if "input." in condition_line:
                # Extract field name
                field_match = re.search(r"input\.(\w+)", condition_line)
                if field_match:
                    field_name = field_match.group(1)
                    var = self._get_or_create_variable(f"input_{field_name}", "bool")
                    return var.z3_var

            return None

        except Exception as e:
            logger.warning(
                f"Failed to create input condition for {condition_line}: {e}"
            )
            return None

    def _compile_constitutional_principle(
        self, principle_name: str, principle_data: dict[str, Any]
    ) -> list[SMTConstraint]:
        """Compile constitutional principle to SMT constraints."""
        constraints = []

        try:
            # Create principle variable
            principle_var = self._get_or_create_variable(
                f"principle_{principle_name}", "bool"
            )

            # Process requirements
            if "requirements" in principle_data:
                requirements = principle_data["requirements"]
                requirement_conditions = []

                for req in requirements:
                    if isinstance(req, str):
                        # Simple requirement
                        req_var = self._get_or_create_variable(
                            f"req_{req.replace(' ', '_')}", "bool"
                        )
                        requirement_conditions.append(req_var.z3_var)
                    elif isinstance(req, dict):
                        # Complex requirement with conditions
                        req_condition = self._process_complex_requirement(req)
                        if req_condition is not None:
                            requirement_conditions.append(req_condition)

                if requirement_conditions:
                    # Principle holds if all requirements are satisfied
                    all_requirements = (
                        z3.And(*requirement_conditions)
                        if len(requirement_conditions) > 1
                        else requirement_conditions[0]
                    )
                    constraint = z3.Implies(principle_var.z3_var, all_requirements)

                    constraints.append(
                        SMTConstraint(
                            constraint=constraint,
                            source_policy=principle_name,
                            policy_type=PolicyType.CONSTITUTIONAL_PRINCIPLE,
                            priority=3,  # High priority for constitutional principles
                        )
                    )

            # Process enforcement level
            if "enforcement" in principle_data:
                enforcement = principle_data["enforcement"]
                if enforcement == "strict":
                    # Strict enforcement - principle must always hold
                    constraint = principle_var.z3_var
                    constraints.append(
                        SMTConstraint(
                            constraint=constraint,
                            source_policy=principle_name,
                            policy_type=PolicyType.CONSTITUTIONAL_PRINCIPLE,
                            priority=5,  # Highest priority for strict enforcement
                        )
                    )

        except Exception as e:
            logger.exception(
                f"Failed to compile constitutional principle {principle_name}: {e}"
            )

        return constraints

    def _process_complex_requirement(self, requirement: dict[str, Any]) -> Any | None:
        """Process complex requirement with conditions."""
        try:
            if "condition" in requirement:
                condition = requirement["condition"]

                if condition.get("type") == "threshold":
                    # Threshold condition
                    metric = condition.get("metric")
                    threshold = condition.get("value", 0.8)

                    metric_var = self._get_or_create_variable(
                        f"metric_{metric}", "real"
                    )
                    return metric_var.z3_var >= z3.RealVal(str(threshold))

                if condition.get("type") == "boolean":
                    # Boolean condition
                    field = condition.get("field")
                    value = condition.get("value", True)

                    bool_var = self._get_or_create_variable(field, "bool")
                    return bool_var.z3_var if value else z3.Not(bool_var.z3_var)

            return None

        except Exception as e:
            logger.warning(f"Failed to process complex requirement: {e}")
            return None

    def _get_or_create_variable(self, name: str, var_type: str) -> SMTVariable:
        """Get existing variable or create new one."""
        if name in self.variables:
            return self.variables[name]

        # Create new Z3 variable based on type
        if var_type == "bool":
            z3_var = z3.Bool(name)
        elif var_type == "int":
            z3_var = z3.Int(name)
        elif var_type == "real":
            z3_var = z3.Real(name)
        elif var_type == "string":
            z3_var = z3.String(name)
        else:
            # Default to boolean
            z3_var = z3.Bool(name)

        smt_var = SMTVariable(name=name, var_type=var_type, z3_var=z3_var)

        self.variables[name] = smt_var
        return smt_var

    def generate_formal_properties(self) -> list[SMTConstraint]:
        """Generate formal properties for verification."""
        properties = []

        try:
            # Correctness property: All policies must be consistent
            consistency_constraints = [
                constraint.constraint
                for constraint in self.constraints
                if constraint.policy_type == PolicyType.ACCESS_CONTROL
            ]

            if consistency_constraints:
                consistency_property = z3.And(*consistency_constraints)
                properties.append(
                    SMTConstraint(
                        constraint=consistency_property,
                        source_policy="system_consistency",
                        policy_type=PolicyType.COMPLIANCE_REQUIREMENT,
                        priority=4,
                    )
                )

            # Completeness property: Constitutional principles must be satisfied
            constitutional_constraints = [
                c.constraint
                for c in self.constraints
                if c.policy_type == PolicyType.CONSTITUTIONAL_PRINCIPLE
            ]

            if constitutional_constraints:
                completeness_property = z3.And(*constitutional_constraints)
                properties.append(
                    SMTConstraint(
                        constraint=completeness_property,
                        source_policy="constitutional_completeness",
                        policy_type=PolicyType.CONSTITUTIONAL_PRINCIPLE,
                        priority=5,
                    )
                )

            logger.info(f"Generated {len(properties)} formal properties")

        except Exception as e:
            logger.exception(f"Failed to generate formal properties: {e}")

        return properties

    def export_smt_lib(self) -> str:
        """Export all constraints as SMT-LIB format."""
        try:
            smt_lib_lines = [
                "(set-logic QF_LIA)",  # Quantifier-free linear integer arithmetic
                "",
            ]

            # Declare variables
            for var in self.variables.values():
                if var.var_type == "bool":
                    smt_lib_lines.append(f"(declare-fun {var.name} () Bool)")
                elif var.var_type == "int":
                    smt_lib_lines.append(f"(declare-fun {var.name} () Int)")
                elif var.var_type == "real":
                    smt_lib_lines.append(f"(declare-fun {var.name} () Real)")

            smt_lib_lines.append("")

            # Add constraints
            smt_lib_lines.extend(
                f"(assert {constraint.constraint})" for constraint in self.constraints
            )

            smt_lib_lines.extend(["", "(check-sat)", "(exit)"])

            return "\n".join(smt_lib_lines)

        except Exception as e:
            logger.exception(f"Failed to export SMT-LIB: {e}")
            return ""

    def get_compilation_summary(self) -> dict[str, Any]:
        """Get summary of compilation results."""
        try:
            constraint_counts = {}
            for constraint in self.constraints:
                policy_type = constraint.policy_type.value
                constraint_counts[policy_type] = (
                    constraint_counts.get(policy_type, 0) + 1
                )

            return {
                "total_variables": len(self.variables),
                "total_constraints": len(self.constraints),
                "constraint_breakdown": constraint_counts,
                "constitutional_hash": self.constitutional_hash,
                "variable_types": {
                    var_type: sum(
                        1 for v in self.variables.values() if v.var_type == var_type
                    )
                    for var_type in ["bool", "int", "real", "string"]
                },
            }

        except Exception as e:
            logger.exception(f"Failed to generate compilation summary: {e}")
            return {"error": str(e)}
