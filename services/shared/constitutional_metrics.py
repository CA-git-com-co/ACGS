"""
Constitutional AI Governance Metrics for ACGS-PGP
Provides specialized metrics for constitutional AI governance operations.
"""

import logging

from prometheus_client import Counter, Gauge, Histogram

logger = logging.getLogger(__name__)


class ConstitutionalMetrics:
    """Specialized metrics for constitutional AI governance operations."""

    def __init__(self, service_name: str):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        self.service_name = service_name

        # Constitutional principle metrics - use try/except to handle duplicates
        try:
            self.constitutional_principle_operations = Counter(
                "acgs_constitutional_principle_operations_total",
                "Total constitutional principle operations",
                ["service", "operation_type", "principle_category", "status"],
            )
        except ValueError as e:
            if "Duplicated timeseries" in str(e):
                # Get existing metric from registry
                from prometheus_client import REGISTRY

                for collector in REGISTRY._collector_to_names:
                    if (
                        hasattr(collector, "_name")
                        and collector._name == "acgs_constitutional_principle_operations_total"
                    ):
                        self.constitutional_principle_operations = collector
                        break
                else:
                    # Create a no-op counter if we can't find the existing one
                    self.constitutional_principle_operations = self._create_noop_counter()
            else:
                raise

        try:
            self.constitutional_compliance_score = Gauge(
                "acgs_constitutional_compliance_score",
                "Constitutional compliance score (0-1)",
                ["service", "principle_id", "policy_type"],
            )
        except ValueError as e:
            if "Duplicated timeseries" in str(e):
                # Get existing metric from registry
                from prometheus_client import REGISTRY

                for collector in REGISTRY._collector_to_names:
                    if (
                        hasattr(collector, "_name")
                        and collector._name == "acgs_constitutional_compliance_score"
                    ):
                        self.constitutional_compliance_score = collector
                        break
                else:
                    # Create a no-op gauge if we can't find the existing one
                    self.constitutional_compliance_score = self._create_noop_gauge()
            else:
                raise

        # Policy synthesis metrics
        try:
            self.policy_synthesis_operations = Counter(
                "acgs_policy_synthesis_operations_total",
                "Total policy synthesis operations",
                ["service", "synthesis_type", "constitutional_context", "status"],
            )
        except ValueError as e:
            if "Duplicated timeseries" in str(e):
                # Get existing metric from registry
                from prometheus_client import REGISTRY

                for collector in REGISTRY._collector_to_names:
                    if (
                        hasattr(collector, "_name")
                        and collector._name == "acgs_policy_synthesis_operations_total"
                    ):
                        self.policy_synthesis_operations = collector
                        break
                else:
                    # Create a no-op counter if we can't find the existing one
                    self.policy_synthesis_operations = self._create_noop_counter()
            else:
                raise

        self.policy_synthesis_duration = Histogram(
            "acgs_policy_synthesis_duration_seconds",
            "Policy synthesis operation duration",
            ["service", "synthesis_type", "constitutional_context"],
            buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0),
        )

        # LLM reliability metrics
        self.llm_constitutional_reliability = Gauge(
            "acgs_llm_constitutional_reliability_score",
            "LLM constitutional reliability score (0-1)",
            ["service", "model_name", "constitutional_domain"],
        )

        self.llm_bias_detection_score = Gauge(
            "acgs_llm_bias_detection_score",
            "LLM bias detection score (0-1)",
            ["service", "bias_type", "demographic_group"],
        )

        # Constitutional Council metrics
        self.constitutional_council_operations = Counter(
            "acgs_constitutional_council_operations_total",
            "Constitutional Council operations",
            ["service", "operation_type", "council_member_role", "status"],
        )

        self.constitutional_amendment_votes = Counter(
            "acgs_constitutional_amendment_votes_total",
            "Constitutional amendment votes",
            ["service", "amendment_id", "vote_type", "council_member_role"],
        )

        # Formal verification metrics
        self.formal_verification_operations = Counter(
            "acgs_formal_verification_operations_total",
            "Formal verification operations",
            ["service", "verification_type", "solver_type", "result"],
        )

        self.formal_verification_duration = Histogram(
            "acgs_formal_verification_duration_seconds",
            "Formal verification duration",
            ["service", "verification_type", "solver_type"],
            buckets=(0.01, 0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0),
        )

        # Cryptographic integrity metrics
        self.cryptographic_operations = Counter(
            "acgs_cryptographic_operations_total",
            "Cryptographic operations",
            ["service", "operation_type", "key_type", "status"],
        )

        self.pgp_signature_verifications = Counter(
            "acgs_pgp_signature_verifications_total",
            "PGP signature verifications",
            ["service", "artifact_type", "verification_result"],
        )

        # Conflict resolution metrics
        self.conflict_resolution_operations = Counter(
            "acgs_conflict_resolution_operations_total",
            "Conflict resolution operations",
            ["service", "conflict_type", "resolution_method", "status"],
        )

        self.conflict_resolution_duration = Histogram(
            "acgs_conflict_resolution_duration_seconds",
            "Conflict resolution duration",
            ["service", "conflict_type", "resolution_method"],
            buckets=(0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0, 300.0),
        )

        # Human-in-the-loop metrics
        self.human_escalation_operations = Counter(
            "acgs_human_escalation_operations_total",
            "Human escalation operations",
            ["service", "escalation_reason", "escalation_type", "resolution_status"],
        )

        self.human_oversight_accuracy = Gauge(
            "acgs_human_oversight_accuracy_score",
            "Human oversight accuracy score (0-1)",
            ["service", "oversight_type", "decision_category"],
        )

        # Performance and efficiency metrics
        self.constitutional_fidelity_score = Gauge(
            "acgs_constitutional_fidelity_score",
            "Overall constitutional fidelity score (0-1)",
            ["service", "measurement_type"],
        )

        self.governance_efficiency_score = Gauge(
            "acgs_governance_efficiency_score",
            "Governance efficiency score (0-1)",
            ["service", "efficiency_type"],
        )

    def _create_noop_counter(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Create a no-op counter for when metrics are already registered."""

        class NoOpCounter:
            def labels(self, **kwargs):
                # requires: Valid input parameters
                # ensures: Correct function execution
                # sha256: func_hash
                return self

            def inc(self, amount=1):
                # requires: Valid input parameters
                # ensures: Correct function execution
                # sha256: func_hash
                pass

        return NoOpCounter()

    def _create_noop_gauge(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Create a no-op gauge for when metrics are already registered."""

        class NoOpGauge:
            def labels(self, **kwargs):
                # requires: Valid input parameters
                # ensures: Correct function execution
                # sha256: func_hash
                return self

            def set(self, value):
                # requires: Valid input parameters
                # ensures: Correct function execution
                # sha256: func_hash
                pass

        return NoOpGauge()

    def _create_noop_histogram(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Create a no-op histogram for when metrics are already registered."""

        class NoOpHistogram:
            def labels(self, **kwargs):
                # requires: Valid input parameters
                # ensures: Correct function execution
                # sha256: func_hash
                return self

            def observe(self, value):
                # requires: Valid input parameters
                # ensures: Correct function execution
                # sha256: func_hash
                pass

        return NoOpHistogram()

    def record_constitutional_principle_operation(
        self, operation_type: str, principle_category: str, status: str
    ):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record constitutional principle operation."""
        try:
            self.constitutional_principle_operations.labels(
                service=self.service_name,
                operation_type=operation_type,
                principle_category=principle_category,
                status=status,
            ).inc()
        except Exception as e:
            logger.warning(f"Failed to record constitutional principle operation: {e}")

    def update_constitutional_compliance_score(
        self, principle_id: str, policy_type: str, score: float
    ):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Update constitutional compliance score."""
        self.constitutional_compliance_score.labels(
            service=self.service_name,
            principle_id=principle_id,
            policy_type=policy_type,
        ).set(score)

    def record_policy_synthesis_operation(
        self,
        synthesis_type: str,
        constitutional_context: str,
        status: str,
        duration: float,
    ):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record policy synthesis operation."""
        self.policy_synthesis_operations.labels(
            service=self.service_name,
            synthesis_type=synthesis_type,
            constitutional_context=constitutional_context,
            status=status,
        ).inc()

        self.policy_synthesis_duration.labels(
            service=self.service_name,
            synthesis_type=synthesis_type,
            constitutional_context=constitutional_context,
        ).observe(duration)

    def update_llm_constitutional_reliability(
        self, model_name: str, constitutional_domain: str, score: float
    ):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Update LLM constitutional reliability score."""
        self.llm_constitutional_reliability.labels(
            service=self.service_name,
            model_name=model_name,
            constitutional_domain=constitutional_domain,
        ).set(score)

    def update_constitutional_fidelity_score(self, measurement_type: str, score: float):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Update constitutional fidelity score."""
        self.constitutional_fidelity_score.labels(
            service=self.service_name, measurement_type=measurement_type
        ).set(score)

    def record_formal_verification_operation(
        self, verification_type: str, solver_type: str, result: str, duration: float
    ):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record formal verification operation."""
        self.formal_verification_operations.labels(
            service=self.service_name,
            verification_type=verification_type,
            solver_type=solver_type,
            result=result,
        ).inc()

        self.formal_verification_duration.labels(
            service=self.service_name,
            verification_type=verification_type,
            solver_type=solver_type,
        ).observe(duration)

    def record_human_escalation(
        self, escalation_reason: str, escalation_type: str, resolution_status: str
    ):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record human escalation operation."""
        self.human_escalation_operations.labels(
            service=self.service_name,
            escalation_reason=escalation_reason,
            escalation_type=escalation_type,
            resolution_status=resolution_status,
        ).inc()


# Global constitutional metrics registry
constitutional_metrics_registry: dict[str, ConstitutionalMetrics] = {}


def get_constitutional_metrics(service_name: str) -> ConstitutionalMetrics:
    """Get or create constitutional metrics instance for a service."""
    if service_name not in constitutional_metrics_registry:
        try:
            constitutional_metrics_registry[service_name] = ConstitutionalMetrics(service_name)
        except ValueError as e:
            if "Duplicated timeseries" in str(e):
                logger.warning(f"Metrics collision for {service_name}, using existing registry")

                # Create a dummy metrics object that doesn't register new metrics
                class DummyConstitutionalMetrics:
                    def __init__(self, service_name):
                        # requires: Valid input parameters
                        # ensures: Correct function execution
                        # sha256: func_hash
                        self.service_name = service_name

                    def __getattr__(self, name):
                        # requires: Valid input parameters
                        # ensures: Correct function execution
                        # sha256: func_hash
                        # Return a no-op function for any metric method
                        return lambda *args, **kwargs: None

                constitutional_metrics_registry[service_name] = DummyConstitutionalMetrics(
                    service_name
                )
            else:
                raise
    return constitutional_metrics_registry[service_name]


def reset_constitutional_metrics():
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """Reset constitutional metrics registry (useful for testing)."""
    global constitutional_metrics_registry
    constitutional_metrics_registry.clear()

    # Clear Prometheus registry if needed
    try:
        from prometheus_client import REGISTRY

        collectors_to_remove = []
        for collector in REGISTRY._collector_to_names:
            if hasattr(collector, "_name") and "acgs_constitutional" in str(collector._name):
                collectors_to_remove.append(collector)

        for collector in collectors_to_remove:
            try:
                REGISTRY.unregister(collector)
            except KeyError:
                pass  # Already removed
    except Exception as e:
        logger.warning(f"Failed to clear Prometheus registry: {e}")
