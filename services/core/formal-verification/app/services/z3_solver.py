"""
Z3 SMT Solver Service

Core service for formal verification using Z3 theorem prover.
"""

import hashlib
import logging
import pickle
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any

from z3 import (
    And,
    Bool,
    BoolVal,
    Implies,
    ModelRef,
    Not,
    OrElse,
    Repeat,
    Solver,
    String,
    Tactic,
    sat,
    simplify,
    unknown,
    unsat,
)

try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from ..core.simple_config import settings

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


logger = logging.getLogger(__name__)


@dataclass
class VerificationResult:
    """Structured verification result with caching metadata."""

    satisfiable: bool
    unsatisfiable: bool
    unknown: bool
    policy_count: int
    constraint_count: int
    verification_time_ms: int
    solver_stats: dict
    variables: list
    cached: bool = False
    cache_hit: bool = False
    approximated: bool = False
    constitutional_hash: str = CONSTITUTIONAL_HASH

    def to_dict(self) -> dict:
        return asdict(self)


class OptimizedCache:
    """High-performance cache for Z3 verification results."""

    def __init__(self, max_memory_items: int = 1000, redis_ttl: int = 3600):
        self.max_memory_items = max_memory_items
        self.redis_ttl = redis_ttl
        self.memory_cache: dict[str, tuple[VerificationResult, datetime]] = {}
        self.cache_stats = {"hits": 0, "misses": 0, "redis_hits": 0, "memory_hits": 0}

        # Initialize Redis if available
        self.redis_client = None
        if REDIS_AVAILABLE:
            try:
                self.redis_client = redis.Redis(
                    host="localhost", port=6379, decode_responses=False
                )
                self.redis_client.ping()
            except:
                self.redis_client = None
                logger.warning("Redis not available, using memory-only cache")

    def get(self, key: str) -> VerificationResult | None:
        """Get cached result with multi-tier lookup."""
        # Check memory cache first
        if key in self.memory_cache:
            result, timestamp = self.memory_cache[key]
            if datetime.now() - timestamp < timedelta(hours=1):  # 1 hour TTL
                self.cache_stats["hits"] += 1
                self.cache_stats["memory_hits"] += 1
                result.cache_hit = True
                return result
            del self.memory_cache[key]

        # Check Redis cache
        if self.redis_client:
            try:
                cached_data = self.redis_client.get(f"z3_verification:{key}")
                if cached_data:
                    result = pickle.loads(cached_data)
                    # Store in memory cache for faster access
                    self.memory_cache[key] = (result, datetime.now())
                    self._cleanup_memory_cache()

                    self.cache_stats["hits"] += 1
                    self.cache_stats["redis_hits"] += 1
                    result.cache_hit = True
                    return result
            except Exception as e:
                logger.warning(f"Redis cache lookup failed: {e}")

        self.cache_stats["misses"] += 1
        return None

    def set(self, key: str, result: VerificationResult) -> None:
        """Store result in multi-tier cache."""
        result.cached = True

        # Store in memory cache
        self.memory_cache[key] = (result, datetime.now())
        self._cleanup_memory_cache()

        # Store in Redis cache
        if self.redis_client:
            try:
                cached_data = pickle.dumps(result)
                self.redis_client.setex(
                    f"z3_verification:{key}", self.redis_ttl, cached_data
                )
            except Exception as e:
                logger.warning(f"Redis cache store failed: {e}")

    def _cleanup_memory_cache(self) -> None:
        """Remove old entries from memory cache."""
        if len(self.memory_cache) > self.max_memory_items:
            # Remove oldest entries
            items = list(self.memory_cache.items())
            items.sort(key=lambda x: x[1][1])  # Sort by timestamp
            for key, _ in items[: -self.max_memory_items // 2]:
                del self.memory_cache[key]

    def get_stats(self) -> dict:
        """Get cache performance statistics."""
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = (
            self.cache_stats["hits"] / total_requests if total_requests > 0 else 0
        )

        return {
            **self.cache_stats,
            "hit_rate": hit_rate,
            "memory_cache_size": len(self.memory_cache),
            "redis_available": self.redis_client is not None,
        }


class Z3SolverService:
    """
    Enhanced Z3 SMT solver service for formal verification.

    Features:
    - Policy consistency checking with optimized caching
    - Constitutional compliance verification
    - Satisfiability checking with approximation
    - Proof generation
    - Incremental solving
    - Multi-tier caching (memory + Redis)
    - Formula simplification and approximation
    """

    def __init__(self):
        # Legacy cache for backwards compatibility
        self.solver_cache: dict[str, dict[str, Any]] = {}
        self.proof_cache: dict[str, str] = {}

        # New optimized cache
        self.cache = OptimizedCache()

        # Performance settings
        self.enable_approximation = True
        self.approximation_threshold_ms = 1000  # Use approximation if solving takes >1s
        self.simplification_enabled = True

        # Statistics
        self.stats = {
            "verifications": 0,
            "cache_hits": 0,
            "approximations": 0,
            "simplifications": 0,
            "total_time_ms": 0,
        }

    def verify_policy_consistency(
        self,
        policies: list[dict[str, Any]],
        constitutional_principles: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        Verify that a set of policies is consistent and complies with constitutional principles.
        Enhanced with caching, approximation, and optimization.

        Args:
            policies: List of policy definitions
            constitutional_principles: List of constitutional principles to check against

        Returns:
            Verification result with satisfiability, conflicts, and proof
        """
        start_time = time.time()
        self.stats["verifications"] += 1

        try:
            # Generate cache key
            cache_key = self._generate_cache_key(policies, constitutional_principles)

            # Check cache first
            cached_result = self.cache.get(cache_key)
            if cached_result:
                self.stats["cache_hits"] += 1
                logger.debug(f"Cache hit for verification (key: {cache_key[:16]}...)")
                return cached_result.to_dict()

            # Try fast approximation first for simple cases
            if self.enable_approximation and self._is_simple_verification(
                policies, constitutional_principles
            ):
                approx_result = self._approximate_verification(
                    policies, constitutional_principles, start_time
                )
                if approx_result:
                    # Cache the approximation result
                    self.cache.set(cache_key, approx_result)
                    return approx_result.to_dict()

            # Use full Z3 verification
            result = self._full_z3_verification(
                policies, constitutional_principles, start_time
            )

            # Cache the result
            self.cache.set(cache_key, result)

            return result.to_dict()

        except Exception as e:
            logger.exception(f"Policy verification failed: {e}")
            error_result = VerificationResult(
                satisfiable=False,
                unsatisfiable=False,
                unknown=True,
                policy_count=len(policies),
                constraint_count=0,
                verification_time_ms=int((time.time() - start_time) * 1000),
                solver_stats={},
                variables=[],
                cached=False,
            )
            error_result.error = str(e)
            error_result.message = "Verification failed due to error"
            return error_result.to_dict()

    def _full_z3_verification(
        self,
        policies: list[dict[str, Any]],
        constitutional_principles: list[dict[str, Any]] | None,
        start_time: float,
    ) -> VerificationResult:
        """Perform full Z3 verification with optimizations."""
        # Create Z3 solver instance with optimized tactics
        solver = self._create_optimized_solver()

        # Convert policies to Z3 constraints
        policy_constraints = []
        variable_declarations = {}

        for i, policy in enumerate(policies):
            constraint, variables = self._policy_to_z3_constraint(policy, i)
            if constraint is not None:
                # Apply simplification if enabled
                if self.simplification_enabled:
                    constraint = simplify(constraint)
                    self.stats["simplifications"] += 1

                policy_constraints.append(constraint)
                variable_declarations.update(variables)

        # Add constitutional principles as constraints
        if constitutional_principles:
            for principle in constitutional_principles:
                constraint, variables = self._principle_to_z3_constraint(principle)
                if constraint is not None:
                    if self.simplification_enabled:
                        constraint = simplify(constraint)
                    policy_constraints.append(constraint)
                    variable_declarations.update(variables)

        # Add all constraints to solver
        for constraint in policy_constraints:
            solver.add(constraint)

        # Check satisfiability
        result = solver.check()

        verification_time_ms = int((time.time() - start_time) * 1000)
        self.stats["total_time_ms"] += verification_time_ms

        verification_result = VerificationResult(
            satisfiable=(result == sat),
            unsatisfiable=(result == unsat),
            unknown=(result == unknown),
            policy_count=len(policies),
            constraint_count=len(policy_constraints),
            verification_time_ms=verification_time_ms,
            solver_stats=self._get_solver_statistics(solver),
            variables=list(variable_declarations.keys()),
            cached=False,
        )

        if result == sat:
            # Get model (satisfying assignment)
            model = solver.model()
            verification_result.model = self._model_to_dict(
                model, variable_declarations
            )
            verification_result.message = "Policies are consistent"

        elif result == unsat:
            # Get unsat core if enabled
            if settings.ENABLE_UNSAT_CORE:
                unsat_core = solver.unsat_core()
                verification_result.unsat_core = [
                    str(constraint) for constraint in unsat_core
                ]
                verification_result.conflicting_constraints = len(unsat_core)

            verification_result.message = "Policies contain contradictions"

            # Try to identify specific conflicts
            conflicts = self._identify_policy_conflicts(
                solver, policy_constraints, policies
            )
            verification_result.conflicts = conflicts

        else:
            verification_result.message = (
                "Verification inconclusive (timeout or complexity)"
            )

        # Generate proof if requested and available
        if settings.ENABLE_PROOF_GENERATION and result in {sat, unsat}:
            try:
                proof = solver.proof() if result == unsat else None
                if proof:
                    verification_result.proof = str(proof)
                    verification_result.proof_size = len(str(proof))
            except:
                logger.warning("Proof generation failed")

        return verification_result

    def _create_optimized_solver(self) -> Solver:
        """Create Z3 solver with optimized tactics."""
        # Use tactics for better performance
        # qe = quantifier elimination, simplify = formula simplification, smt = main SMT solver
        tactics = Repeat(OrElse(Tactic("simplify"), Tactic("qe"), Tactic("smt")))
        solver = tactics.solver()
        solver.set("timeout", settings.Z3_TIMEOUT_MS)
        return solver

    def _generate_cache_key(
        self,
        policies: list[dict[str, Any]],
        constitutional_principles: list[dict[str, Any]] | None,
    ) -> str:
        """Generate deterministic cache key for verification request."""
        # Create normalized representation for consistent caching
        policies_str = str(sorted([str(sorted(p.items())) for p in policies]))
        principles_str = (
            str(sorted([str(sorted(p.items())) for p in constitutional_principles]))
            if constitutional_principles
            else ""
        )

        combined = f"{policies_str}:{principles_str}:{CONSTITUTIONAL_HASH}"
        return hashlib.sha256(combined.encode()).hexdigest()

    def _is_simple_verification(
        self,
        policies: list[dict[str, Any]],
        constitutional_principles: list[dict[str, Any]] | None,
    ) -> bool:
        """Determine if verification request is simple enough for approximation."""
        # Use approximation for simple cases
        total_items = len(policies) + (
            len(constitutional_principles) if constitutional_principles else 0
        )

        # Simple heuristics
        if total_items <= 3:
            return True

        # Check for simple policy structures
        simple_policies = all(
            len(policy.get("conditions", [])) <= 2
            and len(policy.get("actions", [])) <= 2
            for policy in policies
        )

        return simple_policies and total_items <= 5

    def _approximate_verification(
        self,
        policies: list[dict[str, Any]],
        constitutional_principles: list[dict[str, Any]] | None,
        start_time: float,
    ) -> VerificationResult | None:
        """Fast approximation for simple verification cases."""
        self.stats["approximations"] += 1

        try:
            # Simple rule-based approximation
            # Check for obvious conflicts in policy actions
            actions_seen = set()
            conflicting_actions = []

            for policy in policies:
                for action in policy.get("actions", []):
                    action_key = f"{action.get('type')}:{action.get('operation')}"
                    if action_key in actions_seen:
                        # Potential conflict if same operation has different actions
                        conflicting_actions.append(action_key)
                    actions_seen.add(action_key)

            # Check for explicit denies vs allows
            allows = set()
            denies = set()

            for policy in policies:
                for action in policy.get("actions", []):
                    operation = action.get("operation")
                    if action.get("type") == "allow":
                        allows.add(operation)
                    elif action.get("type") == "deny":
                        denies.add(operation)

            # Find conflicts
            conflicts = allows.intersection(denies)
            has_conflicts = len(conflicts) > 0

            verification_time_ms = int((time.time() - start_time) * 1000)

            result = VerificationResult(
                satisfiable=not has_conflicts,
                unsatisfiable=has_conflicts,
                unknown=False,
                policy_count=len(policies),
                constraint_count=len(policies),  # Approximation
                verification_time_ms=verification_time_ms,
                solver_stats={"approximated": True},
                variables=[],
                approximated=True,
            )

            if has_conflicts:
                result.message = (
                    f"Approximation detected conflicts in operations: {list(conflicts)}"
                )
                result.conflicts = [
                    {"operation": op, "conflict_type": "allow_deny_conflict"}
                    for op in conflicts
                ]
            else:
                result.message = "Approximation suggests policies are consistent"

            logger.debug(
                f"Used approximation for verification ({verification_time_ms}ms)"
            )
            return result

        except Exception as e:
            logger.warning(f"Approximation failed: {e}")
            return None

    def get_performance_stats(self) -> dict[str, Any]:
        """Get comprehensive performance statistics."""
        cache_stats = self.cache.get_stats()

        avg_time = self.stats["total_time_ms"] / max(self.stats["verifications"], 1)

        return {
            "verifications_total": self.stats["verifications"],
            "cache_hits_total": self.stats["cache_hits"],
            "approximations_total": self.stats["approximations"],
            "simplifications_total": self.stats["simplifications"],
            "average_verification_time_ms": avg_time,
            "total_time_ms": self.stats["total_time_ms"],
            "cache_hit_rate": cache_stats["hit_rate"],
            "memory_cache_size": cache_stats["memory_cache_size"],
            "redis_available": cache_stats["redis_available"],
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

    def clear_cache(self) -> None:
        """Clear all caches and reset statistics."""
        self.solver_cache.clear()
        self.proof_cache.clear()
        self.cache = OptimizedCache()  # Reset optimized cache

        # Reset stats but keep constitutional hash
        self.stats = {
            "verifications": 0,
            "cache_hits": 0,
            "approximations": 0,
            "simplifications": 0,
            "total_time_ms": 0,
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
            logger.exception(f"Constitutional compliance verification failed: {e}")
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
            logger.exception(f"Failed to convert policy to Z3 constraint: {e}")
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
            principle.get("id")
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
            logger.exception(f"Failed to convert principle to Z3 constraint: {e}")
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
                        if k not in {i, j}:
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
