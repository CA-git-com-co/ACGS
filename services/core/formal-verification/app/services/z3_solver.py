"""
Z3 SMT Solver Service

Core service for formal verification using Z3 theorem prover.
"""

import hashlib
import logging
import time
from typing import Any

from z3 import *

from ..core.config import settings

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


logger = logging.getLogger(__name__)


class Z3SolverService:
    """
    Z3 SMT solver service for formal verification.

    Features:
    - Policy consistency checking
    - Constitutional compliance verification
    - Satisfiability checking
    - Proof generation
    - Incremental solving
    """

    def __init__(self):
        self.solver_cache: dict[str, dict[str, Any]] = {}
        self.proof_cache: dict[str, str] = {}

    def verify_policy_consistency(
        self,
        policies: list[dict[str, Any]],
        constitutional_principles: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        Verify that a set of policies is consistent and complies with constitutional principles.

        Args:
            policies: List of policy definitions
            constitutional_principles: List of constitutional principles to check against

        Returns:
            Verification result with satisfiability, conflicts, and proof
        """
        start_time = time.time()

        try:
            # Create Z3 solver instance
            solver = Solver()
            solver.set("timeout", settings.Z3_TIMEOUT_MS)

            # Convert policies to Z3 constraints
            policy_constraints = []
            variable_declarations = {}

            for i, policy in enumerate(policies):
                constraint, variables = self._policy_to_z3_constraint(policy, i)
                if constraint is not None:
                    policy_constraints.append(constraint)
                    variable_declarations.update(variables)

            # Add constitutional principles as constraints
            if constitutional_principles:
                for principle in constitutional_principles:
                    constraint, variables = self._principle_to_z3_constraint(principle)
                    if constraint is not None:
                        policy_constraints.append(constraint)
                        variable_declarations.update(variables)

            # Add all constraints to solver
            for constraint in policy_constraints:
                solver.add(constraint)

            # Check satisfiability
            result = solver.check()

            verification_result = {
                "satisfiable": result == sat,
                "unsatisfiable": result == unsat,
                "unknown": result == unknown,
                "policy_count": len(policies),
                "constraint_count": len(policy_constraints),
                "verification_time_ms": int((time.time() - start_time) * 1000),
                "solver_stats": self._get_solver_statistics(solver),
                "variables": list(variable_declarations.keys()),
            }

            if result == sat:
                # Get model (satisfying assignment)
                model = solver.model()
                verification_result["model"] = self._model_to_dict(
                    model, variable_declarations
                )
                verification_result["message"] = "Policies are consistent"

            elif result == unsat:
                # Get unsat core if enabled
                if settings.ENABLE_UNSAT_CORE:
                    unsat_core = solver.unsat_core()
                    verification_result["unsat_core"] = [
                        str(constraint) for constraint in unsat_core
                    ]
                    verification_result["conflicting_constraints"] = len(unsat_core)

                verification_result["message"] = "Policies contain contradictions"

                # Try to identify specific conflicts
                conflicts = self._identify_policy_conflicts(
                    solver, policy_constraints, policies
                )
                verification_result["conflicts"] = conflicts

            else:
                verification_result["message"] = (
                    "Verification inconclusive (timeout or complexity)"
                )

            # Generate proof if requested and available
            if settings.ENABLE_PROOF_GENERATION and result in [sat, unsat]:
                try:
                    proof = solver.proof() if result == unsat else None
                    if proof:
                        verification_result["proof"] = str(proof)
                        verification_result["proof_size"] = len(str(proof))
                except:
                    logger.warning("Proof generation failed")

            return verification_result

        except Exception as e:
            logger.error(f"Policy verification failed: {e}")
            return {
                "satisfiable": False,
                "error": str(e),
                "verification_time_ms": int((time.time() - start_time) * 1000),
                "message": "Verification failed due to error",
            }

    def verify_single_policy(
        self,
        policy: dict[str, Any],
        existing_policies: list[dict[str, Any]] | None = None,
        constitutional_principles: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        Verify a single policy against existing policies and constitutional principles.

        Args:
            policy: Policy to verify
            existing_policies: List of existing policies to check against
            constitutional_principles: Constitutional principles

        Returns:
            Verification result
        """
        all_policies = existing_policies.copy() if existing_policies else []
        all_policies.append(policy)

        # First check the complete set
        full_result = self.verify_policy_consistency(
            all_policies, constitutional_principles
        )

        # If inconsistent, check if the new policy is the cause
        if not full_result.get("satisfiable", False) and existing_policies:
            baseline_result = self.verify_policy_consistency(
                existing_policies, constitutional_principles
            )

            if baseline_result.get("satisfiable", False):
                # The new policy causes inconsistency
                full_result["new_policy_causes_conflict"] = True
                full_result["message"] = "New policy conflicts with existing policies"
            else:
                # Existing policies were already inconsistent
                full_result["new_policy_causes_conflict"] = False
                full_result["message"] = "Existing policies already contain conflicts"

        return full_result

    def verify_constitutional_compliance(
        self, policy: dict[str, Any], principle_id: str
    ) -> dict[str, Any]:
        """
        Verify that a policy complies with a specific constitutional principle.

        Args:
            policy: Policy to verify
            principle_id: ID of constitutional principle to check

        Returns:
            Compliance verification result
        """
        start_time = time.time()

        try:
            principle = settings.CONSTITUTIONAL_PRINCIPLES.get(principle_id)
            if not principle:
                return {
                    "compliant": False,
                    "error": f"Unknown constitutional principle: {principle_id}",
                    "verification_time_ms": 0,
                }

            # Create solver
            solver = Solver()
            solver.set("timeout", settings.Z3_TIMEOUT_MS)

            # Convert policy to Z3 constraint
            policy_constraint, policy_vars = self._policy_to_z3_constraint(policy, 0)

            # Convert principle to Z3 constraint
            principle_constraint, principle_vars = self._principle_to_z3_constraint(
                principle
            )

            if policy_constraint is None or principle_constraint is None:
                return {
                    "compliant": False,
                    "error": "Failed to convert policy or principle to formal constraint",
                    "verification_time_ms": int((time.time() - start_time) * 1000),
                }

            # Add policy constraint
            solver.add(policy_constraint)

            # Check if policy implies principle (policy -> principle)
            # This is equivalent to checking if (policy AND NOT principle) is unsatisfiable
            solver.push()  # Create checkpoint
            solver.add(Not(principle_constraint))

            result = solver.check()

            compliance_result = {
                "compliant": result == unsat,  # Unsat means policy implies principle
                "principle_id": principle_id,
                "principle_name": principle.get("name"),
                "verification_time_ms": int((time.time() - start_time) * 1000),
            }

            if result == unsat:
                compliance_result["message"] = (
                    f"Policy complies with {principle.get('name')}"
                )
            elif result == sat:
                # Get counterexample
                model = solver.model()
                compliance_result["message"] = (
                    f"Policy violates {principle.get('name')}"
                )
                compliance_result["counterexample"] = self._model_to_dict(
                    model, {**policy_vars, **principle_vars}
                )
            else:
                compliance_result["message"] = "Compliance verification inconclusive"

            solver.pop()  # Restore checkpoint

            return compliance_result

        except Exception as e:
            logger.error(f"Constitutional compliance verification failed: {e}")
            return {
                "compliant": False,
                "error": str(e),
                "verification_time_ms": int((time.time() - start_time) * 1000),
            }

    def _policy_to_z3_constraint(
        self, policy: dict[str, Any], policy_index: int
    ) -> tuple[Any | None, dict[str, Any]]:
        """
        Convert a policy definition to Z3 constraint.

        This is a simplified implementation. In production, you would have
        a more sophisticated policy language parser.
        """
        try:
            variables = {}

            # Extract policy components
            policy_id = policy.get("id", f"policy_{policy_index}")
            conditions = policy.get("conditions", [])
            actions = policy.get("actions", [])

            # Create boolean variables for policy activation and effects
            policy_active = Bool(f"{policy_id}_active")
            variables[f"{policy_id}_active"] = policy_active

            constraints = []

            # Process conditions
            for i, condition in enumerate(conditions):
                condition_var = Bool(f"{policy_id}_condition_{i}")
                variables[f"{policy_id}_condition_{i}"] = condition_var

                # Add condition logic based on type
                if condition.get("type") == "agent_type":
                    agent_type_var = String("agent_type")
                    variables["agent_type"] = agent_type_var
                    # In a real implementation, you'd have proper string constraints

                elif condition.get("type") == "permission":
                    permission_var = Bool(
                        f"has_permission_{condition.get('permission')}"
                    )
                    variables[f"has_permission_{condition.get('permission')}"] = (
                        permission_var
                    )
                    constraints.append(
                        Implies(policy_active, permission_var == condition_var)
                    )

            # Process actions
            for i, action in enumerate(actions):
                action_var = Bool(f"{policy_id}_action_{i}")
                variables[f"{policy_id}_action_{i}"] = action_var

                if action.get("type") == "allow":
                    operation_var = Bool(f"operation_{action.get('operation')}_allowed")
                    variables[f"operation_{action.get('operation')}_allowed"] = (
                        operation_var
                    )
                    constraints.append(Implies(policy_active, operation_var))

                elif action.get("type") == "deny":
                    operation_var = Bool(f"operation_{action.get('operation')}_allowed")
                    variables[f"operation_{action.get('operation')}_allowed"] = (
                        operation_var
                    )
                    constraints.append(Implies(policy_active, Not(operation_var)))

            # Combine all constraints for this policy
            if constraints:
                policy_constraint = And(constraints)
            else:
                policy_constraint = BoolVal(True)  # Trivially satisfied

            return policy_constraint, variables

        except Exception as e:
            logger.error(f"Failed to convert policy to Z3 constraint: {e}")
            return None, {}

    def _principle_to_z3_constraint(
        self, principle: dict[str, Any]
    ) -> tuple[Any | None, dict[str, Any]]:
        """
        Convert a constitutional principle to Z3 constraint.

        This is a simplified implementation. In production, you would have
        a formal specification language parser.
        """
        try:
            variables = {}
            principle_id = principle.get("id")
            formal_spec = principle.get("formal_spec", "")

            # This is a simplified mapping. In practice, you'd have a proper
            # formal specification language (like TLA+, Alloy, or custom DSL)

            if "not permitted" in formal_spec.lower():
                # Non-maleficence: harmful actions not permitted
                harmful_action = Bool("harmful_action")
                action_permitted = Bool("action_permitted")
                variables["harmful_action"] = harmful_action
                variables["action_permitted"] = action_permitted

                constraint = Implies(harmful_action, Not(action_permitted))
                return constraint, variables

            if "not override" in formal_spec.lower():
                # Human autonomy: don't override human decisions
                human_decision = Bool("human_decision")
                agent_override = Bool("agent_override")
                variables["human_decision"] = human_decision
                variables["agent_override"] = agent_override

                constraint = Implies(human_decision, Not(agent_override))
                return constraint, variables

            if "auditable" in formal_spec.lower():
                # Transparency: actions must be auditable
                agent_action = Bool("agent_action")
                action_auditable = Bool("action_auditable")
                action_explainable = Bool("action_explainable")
                variables["agent_action"] = agent_action
                variables["action_auditable"] = action_auditable
                variables["action_explainable"] = action_explainable

                constraint = Implies(
                    agent_action, And(action_auditable, action_explainable)
                )
                return constraint, variables

            if "necessary" in formal_spec.lower():
                # Least privilege: permissions must be necessary
                has_permission = Bool("has_permission")
                permission_necessary = Bool("permission_necessary")
                variables["has_permission"] = has_permission
                variables["permission_necessary"] = permission_necessary

                constraint = Implies(has_permission, permission_necessary)
                return constraint, variables

            if "protected" in formal_spec.lower():
                # Data protection: sensitive data must be protected
                sensitive_data = Bool("sensitive_data")
                data_protected = Bool("data_protected")
                data_leaked = Bool("data_leaked")
                variables["sensitive_data"] = sensitive_data
                variables["data_protected"] = data_protected
                variables["data_leaked"] = data_leaked

                constraint = Implies(
                    sensitive_data, And(data_protected, Not(data_leaked))
                )
                return constraint, variables

            # Default: create a tautology for unknown principles
            return BoolVal(True), variables

        except Exception as e:
            logger.error(f"Failed to convert principle to Z3 constraint: {e}")
            return None, {}

    def _identify_policy_conflicts(
        self, solver: Solver, constraints: list[Any], policies: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Identify specific policy conflicts causing inconsistency."""
        conflicts = []

        try:
            # Try removing each constraint pair to find conflicts
            for i in range(len(constraints)):
                for j in range(i + 1, len(constraints)):
                    test_solver = Solver()
                    test_solver.set(
                        "timeout", 1000
                    )  # Short timeout for conflict detection

                    # Add all constraints except the pair being tested
                    for k, constraint in enumerate(constraints):
                        if k != i and k != j:
                            test_solver.add(constraint)

                    if test_solver.check() == sat:
                        # Removing this pair makes it satisfiable, so they conflict
                        conflicts.append(
                            {
                                "policy_1_index": i,
                                "policy_2_index": j,
                                "policy_1_id": (
                                    policies[i].get("id", f"policy_{i}")
                                    if i < len(policies)
                                    else f"constraint_{i}"
                                ),
                                "policy_2_id": (
                                    policies[j].get("id", f"policy_{j}")
                                    if j < len(policies)
                                    else f"constraint_{j}"
                                ),
                                "conflict_type": "mutual_exclusion",
                            }
                        )

                        # Limit the number of conflicts reported
                        if len(conflicts) >= 10:
                            break

                if len(conflicts) >= 10:
                    break

        except Exception as e:
            logger.warning(f"Conflict identification failed: {e}")

        return conflicts

    def _get_solver_statistics(self, solver: Solver) -> dict[str, Any]:
        """Get solver performance statistics."""
        try:
            stats = solver.statistics()
            return {
                "decisions": stats.get_key_value("decisions"),
                "propagations": stats.get_key_value("propagations"),
                "conflicts": stats.get_key_value("conflicts"),
                "restarts": stats.get_key_value("restarts"),
            }
        except:
            return {}

    def _model_to_dict(
        self, model: ModelRef, variables: dict[str, Any]
    ) -> dict[str, Any]:
        """Convert Z3 model to dictionary."""
        result = {}
        try:
            for var_name, var_obj in variables.items():
                if model[var_obj] is not None:
                    result[var_name] = str(model[var_obj])
        except:
            pass
        return result

    def get_cache_key(self, data: Any) -> str:
        """Generate cache key for verification result."""
        return hashlib.sha256(str(data).encode()).hexdigest()

    def clear_cache(self) -> None:
        """Clear verification cache."""
        self.solver_cache.clear()
        self.proof_cache.clear()
