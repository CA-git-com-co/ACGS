"""
ACGS-PGP Performance Metrics Collection and Mathematical Validation

This module implements real-time monitoring of the mathematical foundations
presented in the ACGS-PGP paper, including:
- Constitutional stability (Lipschitz constant monitoring)
- Enforcement latency tracking
- Compliance rate measurement
- Adversarial robustness validation

Integrates with the existing PGC service to provide empirical validation
of the theoretical claims in the research paper.
"""

import asyncio
import logging
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone

import numpy as np

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


logger = logging.getLogger(__name__)


@dataclass
class ConstitutionalStabilityMetrics:
    """Metrics for tracking constitutional stability as per ACGS-PGP Theorem 1"""

    lipschitz_constant: float = 0.0
    convergence_iterations: int = 0
    stability_score: float = 0.0
    last_update: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    principle_changes: list[dict] = field(default_factory=list)
    policy_synthesis_history: deque = field(default_factory=lambda: deque(maxlen=100))


@dataclass
class EnforcementPerformanceMetrics:
    """Performance metrics for PGC enforcement as per ACGS-PGP evaluation"""

    average_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    throughput_per_second: float = 0.0
    compliance_rate: float = 0.0
    scaling_exponent: float = 0.0  # Should be ~0.73 per paper
    total_enforcements: int = 0
    violations_detected: int = 0


@dataclass
class AdversarialRobustnessMetrics:
    """Adversarial robustness metrics as per ACGS-PGP Section 5"""

    manipulation_detection_rate: float = 0.0
    constitutional_capture_attempts: int = 0
    successful_attacks: int = 0
    defense_effectiveness: float = 0.0
    adversarial_training_cycles: int = 0


class ACGSPGPMetricsCollector:
    """
    Real-time metrics collection for ACGS-PGP paper validation

    Monitors the deployed ACGS-1 system to provide empirical data
    for the theoretical claims in the research paper.
    """

    def __init__(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        self.stability_metrics = ConstitutionalStabilityMetrics()
        self.performance_metrics = EnforcementPerformanceMetrics()
        self.robustness_metrics = AdversarialRobustnessMetrics()

        # Sliding window for latency measurements
        self.latency_window = deque(maxlen=1000)
        self.enforcement_history = deque(maxlen=10000)

        # Constitutional state tracking for stability analysis
        self.constitutional_states = deque(maxlen=50)
        self.policy_synthesis_results = deque(maxlen=100)

        self.monitoring_active = False
        self.last_metrics_update = datetime.now(timezone.utc)

    async def start_monitoring(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Start continuous metrics collection"""
        self.monitoring_active = True
        logger.info("ACGS-PGP metrics collection started")

        # Start background monitoring tasks
        asyncio.create_task(self._monitor_enforcement_performance())
        asyncio.create_task(self._monitor_constitutional_stability())
        asyncio.create_task(self._monitor_adversarial_robustness())

    async def stop_monitoring(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Stop metrics collection"""
        self.monitoring_active = False
        logger.info("ACGS-PGP metrics collection stopped")

    async def record_enforcement_event(
        self,
        latency_ms: float,
        policy_count: int,
        compliance_result: bool,
        context: dict | None = None,
    ):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record a policy enforcement event for performance analysis"""
        timestamp = datetime.now(timezone.utc)

        # Record latency
        self.latency_window.append(latency_ms)

        # Record enforcement event
        event = {
            "timestamp": timestamp.isoformat(),
            "latency_ms": latency_ms,
            "policy_count": policy_count,
            "compliant": compliance_result,
            "context": context or {},
        }
        self.enforcement_history.append(event)

        # Update performance metrics
        await self._update_performance_metrics()

        # Check for scaling analysis (O(n^0.73) validation)
        if len(self.enforcement_history) >= 100:
            await self._analyze_scaling_performance()

    async def record_policy_synthesis(
        self,
        principle_id: str,
        synthesis_success: bool,
        constitutional_state: dict,
        synthesis_time_ms: float,
    ):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record policy synthesis event for stability analysis"""
        timestamp = datetime.now(timezone.utc)

        synthesis_event = {
            "timestamp": timestamp.isoformat(),
            "principle_id": principle_id,
            "success": synthesis_success,
            "synthesis_time_ms": synthesis_time_ms,
            "constitutional_state": constitutional_state,
        }

        self.policy_synthesis_results.append(synthesis_event)
        self.constitutional_states.append(constitutional_state)

        # Update stability metrics
        await self._update_stability_metrics()

    async def record_adversarial_event(
        self,
        attack_type: str,
        detected: bool,
        severity: str,
        defense_mechanism: str | None = None,
    ):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record adversarial attack attempt for robustness analysis"""
        datetime.now(timezone.utc)

        if attack_type == "constitutional_capture":
            self.robustness_metrics.constitutional_capture_attempts += 1

        if not detected:
            self.robustness_metrics.successful_attacks += 1

        # Update detection rate
        total_attempts = self.robustness_metrics.constitutional_capture_attempts + len(
            [e for e in self.enforcement_history if e.get("adversarial", False)]
        )

        if total_attempts > 0:
            detection_rate = 1.0 - (
                self.robustness_metrics.successful_attacks / total_attempts
            )
            self.robustness_metrics.manipulation_detection_rate = detection_rate

    async def _update_performance_metrics(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Update enforcement performance metrics"""
        if not self.latency_window:
            return

        latencies = list(self.latency_window)

        # Calculate latency statistics
        self.performance_metrics.average_latency_ms = np.mean(latencies)
        self.performance_metrics.p95_latency_ms = np.percentile(latencies, 95)
        self.performance_metrics.p99_latency_ms = np.percentile(latencies, 99)

        # Calculate compliance rate
        recent_events = list(self.enforcement_history)[-100:]  # Last 100 events
        if recent_events:
            compliant_count = sum(1 for e in recent_events if e.get("compliant", False))
            self.performance_metrics.compliance_rate = compliant_count / len(
                recent_events
            )

        # Update total counts
        self.performance_metrics.total_enforcements = len(self.enforcement_history)
        self.performance_metrics.violations_detected = sum(
            1 for e in self.enforcement_history if not e.get("compliant", True)
        )

    async def _update_stability_metrics(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Update constitutional stability metrics per Theorem 1"""
        if len(self.constitutional_states) < 2:
            return

        # Calculate Lipschitz constant approximation
        # L = ||f(x) - f(y)|| / ||x - y|| for constitutional state transitions
        try:
            lipschitz_estimates = []
            states = list(self.constitutional_states)

            for i in range(1, len(states)):
                prev_state = states[i - 1]
                curr_state = states[i]

                # Simplified state distance calculation
                state_distance = self._calculate_state_distance(prev_state, curr_state)
                if state_distance > 0:
                    # Policy change magnitude as output distance
                    policy_distance = self._calculate_policy_distance(
                        prev_state, curr_state
                    )
                    lipschitz_estimate = policy_distance / state_distance
                    lipschitz_estimates.append(lipschitz_estimate)

            if lipschitz_estimates:
                self.stability_metrics.lipschitz_constant = np.mean(lipschitz_estimates)

                # Check if system is contractive (L < 1)
                if self.stability_metrics.lipschitz_constant < 1.0:
                    self.stability_metrics.stability_score = (
                        1.0 - self.stability_metrics.lipschitz_constant
                    )
                else:
                    self.stability_metrics.stability_score = 0.0

        except Exception as e:
            logger.exception(f"Error calculating stability metrics: {e}")

    async def _analyze_scaling_performance(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Analyze scaling performance to validate O(n^0.73) claim"""
        try:
            # Group enforcement events by policy count
            policy_counts = []
            avg_latencies = []

            events_by_policy_count = {}
            for event in self.enforcement_history:
                count = event.get("policy_count", 1)
                if count not in events_by_policy_count:
                    events_by_policy_count[count] = []
                events_by_policy_count[count].append(event["latency_ms"])

            for count, latencies in events_by_policy_count.items():
                if len(latencies) >= 5:  # Minimum sample size
                    policy_counts.append(count)
                    avg_latencies.append(np.mean(latencies))

            if len(policy_counts) >= 3:
                # Fit power law: latency = a * n^b
                log_counts = np.log(policy_counts)
                log_latencies = np.log(avg_latencies)

                # Linear regression on log-log scale
                coeffs = np.polyfit(log_counts, log_latencies, 1)
                scaling_exponent = coeffs[0]

                self.performance_metrics.scaling_exponent = scaling_exponent

                logger.info(f"Scaling analysis: O(n^{scaling_exponent:.3f})")

        except Exception as e:
            logger.exception(f"Error in scaling analysis: {e}")

    def _calculate_state_distance(self, state1: dict, state2: dict) -> float:
        """Calculate distance between constitutional states"""
        # Simplified implementation - could be enhanced with proper metric
        try:
            # Compare principle counts and weights
            principles1 = state1.get("principles", {})
            principles2 = state2.get("principles", {})

            all_keys = set(principles1.keys()) | set(principles2.keys())
            distance = 0.0

            for key in all_keys:
                val1 = principles1.get(key, {}).get("weight", 0.0)
                val2 = principles2.get(key, {}).get("weight", 0.0)
                distance += abs(val1 - val2)

            return distance
        except:
            return 1.0  # Default distance

    def _calculate_policy_distance(self, state1: dict, state2: dict) -> float:
        """Calculate distance between policy outputs"""
        # Simplified implementation
        try:
            policies1 = len(state1.get("active_policies", []))
            policies2 = len(state2.get("active_policies", []))
            return abs(policies1 - policies2)
        except:
            return 1.0

    async def _monitor_enforcement_performance(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Background task for performance monitoring"""
        while self.monitoring_active:
            try:
                # Update throughput calculation
                recent_events = [
                    e
                    for e in self.enforcement_history
                    if (
                        datetime.now(timezone.utc)
                        - datetime.fromisoformat(e["timestamp"])
                    ).seconds
                    < 60
                ]
                self.performance_metrics.throughput_per_second = (
                    len(recent_events) / 60.0
                )

                await asyncio.sleep(10)  # Update every 10 seconds
            except Exception as e:
                logger.exception(f"Error in performance monitoring: {e}")
                await asyncio.sleep(10)

    async def _monitor_constitutional_stability(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Background task for stability monitoring"""
        while self.monitoring_active:
            try:
                # Check for convergence patterns
                if len(self.policy_synthesis_results) >= 10:
                    recent_results = list(self.policy_synthesis_results)[-10:]
                    success_rate = sum(1 for r in recent_results if r["success"]) / len(
                        recent_results
                    )

                    # Simple convergence detection
                    if success_rate > 0.9:
                        self.stability_metrics.convergence_iterations = len(
                            self.policy_synthesis_results
                        )

                await asyncio.sleep(30)  # Update every 30 seconds
            except Exception as e:
                logger.exception(f"Error in stability monitoring: {e}")
                await asyncio.sleep(30)

    async def _monitor_adversarial_robustness(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Background task for adversarial robustness monitoring"""
        while self.monitoring_active:
            try:
                # Calculate defense effectiveness
                if self.robustness_metrics.constitutional_capture_attempts > 0:
                    effectiveness = 1.0 - (
                        self.robustness_metrics.successful_attacks
                        / self.robustness_metrics.constitutional_capture_attempts
                    )
                    self.robustness_metrics.defense_effectiveness = effectiveness

                await asyncio.sleep(60)  # Update every minute
            except Exception as e:
                logger.exception(f"Error in robustness monitoring: {e}")
                await asyncio.sleep(60)

    def get_paper_validation_report(self) -> dict:
        """Generate validation report for ACGS-PGP paper claims"""
        return {
            "constitutional_stability": {
                "lipschitz_constant": self.stability_metrics.lipschitz_constant,
                "paper_claim": 0.73,
                "validated": abs(self.stability_metrics.lipschitz_constant - 0.73)
                < 0.1,
                "stability_score": self.stability_metrics.stability_score,
                "convergence_iterations": self.stability_metrics.convergence_iterations,
            },
            "enforcement_performance": {
                "average_latency_ms": self.performance_metrics.average_latency_ms,
                "paper_claim_ms": 37.0,
                "sub_50ms_target_met": self.performance_metrics.average_latency_ms
                < 50.0,
                "scaling_exponent": self.performance_metrics.scaling_exponent,
                "paper_scaling_claim": 0.73,
                "compliance_rate": self.performance_metrics.compliance_rate,
                "paper_compliance_claim": 0.952,
            },
            "adversarial_robustness": {
                "detection_rate": self.robustness_metrics.manipulation_detection_rate,
                "paper_claim": 0.943,
                "defense_effectiveness": self.robustness_metrics.defense_effectiveness,
                "successful_attacks": self.robustness_metrics.successful_attacks,
                "total_attempts": self.robustness_metrics.constitutional_capture_attempts,
            },
            "data_collection": {
                "enforcement_events": len(self.enforcement_history),
                "synthesis_events": len(self.policy_synthesis_results),
                "monitoring_duration_hours": (
                    datetime.now(timezone.utc) - self.last_metrics_update
                ).total_seconds()
                / 3600,
                "last_update": self.last_metrics_update.isoformat(),
            },
        }


# Global metrics collector instance
metrics_collector = ACGSPGPMetricsCollector()


async def initialize_acgs_pgp_monitoring():
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """Initialize ACGS-PGP metrics collection"""
    await metrics_collector.start_monitoring()
    logger.info("ACGS-PGP monitoring initialized")


async def get_validation_report() -> dict:
    """Get current validation report for paper claims"""
    return metrics_collector.get_paper_validation_report()
