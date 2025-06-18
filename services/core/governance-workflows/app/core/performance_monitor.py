"""
Performance Monitor for ACGS-1 Advanced Governance Workflows.

This module implements WINA (Workflow Intelligence and Automation) oversight
with real-time performance monitoring, bottleneck analysis, and optimization.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """Performance metric data structure."""

    metric_name: str
    value: float
    unit: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    tags: dict[str, str] = field(default_factory=dict)


@dataclass
class BottleneckAnalysis:
    """Bottleneck analysis result."""

    bottleneck_id: str
    component: str
    severity: str  # low, medium, high, critical
    description: str
    impact_score: float
    recommended_actions: list[str]
    detected_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class OptimizationPlan:
    """Optimization plan data structure."""

    plan_id: str
    target_component: str
    optimization_type: str
    expected_improvement: float
    implementation_steps: list[str]
    estimated_duration_minutes: int
    risk_level: str  # low, medium, high
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class PerformanceMonitor:
    """
    WINA oversight performance monitor for governance workflows.

    This monitor provides real-time performance tracking, bottleneck analysis,
    and automated optimization recommendations for governance workflows.
    """

    def __init__(self, settings):
        self.settings = settings

        # Performance targets
        self.performance_targets = {
            "response_time_ms": settings.RESPONSE_TIME_TARGET_MS,
            "availability_percent": settings.AVAILABILITY_TARGET_PERCENT,
            "compliance_accuracy_percent": settings.COMPLIANCE_ACCURACY_TARGET_PERCENT,
            "wina_optimization_percent": settings.WINA_OPTIMIZATION_TARGET_PERCENT,
        }

        # Monitoring state
        self.active_monitoring_sessions: dict[str, dict[str, Any]] = {}
        self.performance_metrics: list[PerformanceMetric] = []
        self.bottleneck_analyses: list[BottleneckAnalysis] = []
        self.optimization_plans: list[OptimizationPlan] = []

        # Configuration
        self.monitoring_interval = settings.WINA_OVERSIGHT_MONITORING_INTERVAL_SECONDS
        self.optimization_threshold = settings.WINA_OVERSIGHT_OPTIMIZATION_THRESHOLD
        self.reporting_interval = settings.WINA_OVERSIGHT_REPORTING_INTERVAL_MINUTES

        # Performance statistics
        self.performance_stats = {
            "total_monitoring_sessions": 0,
            "active_sessions": 0,
            "bottlenecks_detected": 0,
            "optimizations_implemented": 0,
            "average_improvement_percent": 0,
        }

        logger.info("Performance monitor initialized with WINA oversight")

    async def initialize(self):
        """Initialize the performance monitor."""
        try:
            # Start background monitoring tasks
            asyncio.create_task(self._continuous_monitoring())
            asyncio.create_task(self._bottleneck_detection())
            asyncio.create_task(self._optimization_engine())
            asyncio.create_task(self._performance_reporting())

            logger.info("✅ Performance monitor initialization complete")

        except Exception as e:
            logger.error(f"❌ Performance monitor initialization failed: {e}")
            raise

    async def start_monitoring(self, monitoring_data: dict[str, Any]) -> dict[str, Any]:
        """Start a new performance monitoring session."""
        try:
            session_id = (
                f"monitor_{int(time.time())}_{len(self.active_monitoring_sessions)}"
            )

            monitoring_session = {
                "session_id": session_id,
                "workflow_id": monitoring_data.get("workflow_id"),
                "component": monitoring_data.get("component", "workflow"),
                "started_at": datetime.now(UTC),
                "metrics": [],
                "status": "active",
            }

            self.active_monitoring_sessions[session_id] = monitoring_session
            self.performance_stats["total_monitoring_sessions"] += 1
            self.performance_stats["active_sessions"] = len(
                self.active_monitoring_sessions
            )

            logger.info(f"Started monitoring session: {session_id}")

            return {
                "success": True,
                "session_id": session_id,
                "monitoring_interval": self.monitoring_interval,
                "performance_targets": self.performance_targets,
            }

        except Exception as e:
            logger.error(f"Failed to start monitoring: {e}")
            return {"success": False, "error": str(e)}

    async def analyze_bottlenecks(self, workflow_id: str) -> dict[str, Any]:
        """Analyze bottlenecks for a specific workflow."""
        try:
            # Find monitoring session for workflow
            monitoring_session = None
            for session in self.active_monitoring_sessions.values():
                if session.get("workflow_id") == workflow_id:
                    monitoring_session = session
                    break

            if not monitoring_session:
                return {
                    "success": False,
                    "error": "No monitoring session found for workflow",
                }

            # Analyze performance metrics for bottlenecks
            bottlenecks = await self._detect_bottlenecks(monitoring_session)

            # Store bottleneck analyses
            for bottleneck in bottlenecks:
                self.bottleneck_analyses.append(bottleneck)

            self.performance_stats["bottlenecks_detected"] += len(bottlenecks)

            logger.info(
                f"Analyzed bottlenecks for workflow {workflow_id}: {len(bottlenecks)} found"
            )

            return {
                "success": True,
                "workflow_id": workflow_id,
                "bottlenecks_count": len(bottlenecks),
                "bottlenecks": [
                    {
                        "bottleneck_id": b.bottleneck_id,
                        "component": b.component,
                        "severity": b.severity,
                        "description": b.description,
                        "impact_score": b.impact_score,
                        "recommended_actions": b.recommended_actions,
                    }
                    for b in bottlenecks
                ],
            }

        except Exception as e:
            logger.error(f"Failed to analyze bottlenecks: {e}")
            return {"success": False, "error": str(e)}

    async def plan_optimization(self, workflow_id: str) -> dict[str, Any]:
        """Plan optimization for a specific workflow."""
        try:
            # Find relevant bottlenecks
            relevant_bottlenecks = [
                b
                for b in self.bottleneck_analyses
                if workflow_id in b.bottleneck_id or b.severity in ["high", "critical"]
            ]

            if not relevant_bottlenecks:
                return {
                    "success": True,
                    "workflow_id": workflow_id,
                    "optimization_needed": False,
                    "message": "No significant bottlenecks requiring optimization",
                }

            # Create optimization plans
            optimization_plans = []
            for bottleneck in relevant_bottlenecks:
                plan = await self._create_optimization_plan(bottleneck)
                optimization_plans.append(plan)
                self.optimization_plans.append(plan)

            logger.info(
                f"Created {len(optimization_plans)} optimization plans for workflow {workflow_id}"
            )

            return {
                "success": True,
                "workflow_id": workflow_id,
                "optimization_needed": True,
                "plans_count": len(optimization_plans),
                "optimization_plans": [
                    {
                        "plan_id": p.plan_id,
                        "target_component": p.target_component,
                        "optimization_type": p.optimization_type,
                        "expected_improvement": p.expected_improvement,
                        "implementation_steps": p.implementation_steps,
                        "estimated_duration_minutes": p.estimated_duration_minutes,
                        "risk_level": p.risk_level,
                    }
                    for p in optimization_plans
                ],
            }

        except Exception as e:
            logger.error(f"Failed to plan optimization: {e}")
            return {"success": False, "error": str(e)}

    async def implement_optimization(self, workflow_id: str) -> dict[str, Any]:
        """Implement optimization plans for a workflow."""
        try:
            # Find optimization plans for workflow
            relevant_plans = [
                p
                for p in self.optimization_plans
                if workflow_id in p.plan_id and p.risk_level in ["low", "medium"]
            ]

            if not relevant_plans:
                return {
                    "success": True,
                    "workflow_id": workflow_id,
                    "optimizations_implemented": 0,
                    "message": "No safe optimization plans available for implementation",
                }

            # Implement optimizations
            implemented_count = 0
            implementation_results = []

            for plan in relevant_plans:
                result = await self._implement_optimization_plan(plan)
                implementation_results.append(result)

                if result.get("success", False):
                    implemented_count += 1

            self.performance_stats["optimizations_implemented"] += implemented_count

            logger.info(
                f"Implemented {implemented_count} optimizations for workflow {workflow_id}"
            )

            return {
                "success": True,
                "workflow_id": workflow_id,
                "optimizations_implemented": implemented_count,
                "total_plans": len(relevant_plans),
                "implementation_results": implementation_results,
            }

        except Exception as e:
            logger.error(f"Failed to implement optimization: {e}")
            return {"success": False, "error": str(e)}

    async def generate_report(self, workflow_id: str) -> dict[str, Any]:
        """Generate performance report for a workflow."""
        try:
            # Find monitoring session
            monitoring_session = None
            for session in self.active_monitoring_sessions.values():
                if session.get("workflow_id") == workflow_id:
                    monitoring_session = session
                    break

            if not monitoring_session:
                return {
                    "success": False,
                    "error": "No monitoring session found for workflow",
                }

            # Generate comprehensive report
            report = {
                "workflow_id": workflow_id,
                "monitoring_session_id": monitoring_session["session_id"],
                "monitoring_duration_minutes": (
                    (
                        datetime.now(UTC) - monitoring_session["started_at"]
                    ).total_seconds()
                    / 60
                ),
                "performance_summary": await self._calculate_performance_summary(
                    monitoring_session
                ),
                "bottlenecks_summary": await self._summarize_bottlenecks(workflow_id),
                "optimizations_summary": await self._summarize_optimizations(
                    workflow_id
                ),
                "recommendations": await self._generate_recommendations(workflow_id),
                "generated_at": datetime.now(UTC).isoformat(),
            }

            logger.info(f"Generated performance report for workflow {workflow_id}")

            return {
                "success": True,
                "workflow_id": workflow_id,
                "report": report,
            }

        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
            return {"success": False, "error": str(e)}

    async def get_performance_metrics(self) -> dict[str, Any]:
        """Get current performance metrics."""
        try:
            # Calculate current performance statistics
            recent_metrics = [
                m
                for m in self.performance_metrics
                if (datetime.now(UTC) - m.timestamp).total_seconds() < 3600  # Last hour
            ]

            # Calculate averages
            response_times = [
                m.value for m in recent_metrics if m.metric_name == "response_time_ms"
            ]
            avg_response_time = (
                sum(response_times) / len(response_times) if response_times else 0
            )

            availability_metrics = [
                m.value
                for m in recent_metrics
                if m.metric_name == "availability_percent"
            ]
            avg_availability = (
                sum(availability_metrics) / len(availability_metrics)
                if availability_metrics
                else 100
            )

            return {
                "performance_targets": self.performance_targets,
                "current_performance": {
                    "average_response_time_ms": round(avg_response_time, 2),
                    "average_availability_percent": round(avg_availability, 2),
                    "target_compliance": {
                        "response_time": avg_response_time
                        <= self.performance_targets["response_time_ms"],
                        "availability": avg_availability
                        >= self.performance_targets["availability_percent"],
                    },
                },
                "monitoring_statistics": self.performance_stats,
                "active_sessions": len(self.active_monitoring_sessions),
                "recent_metrics_count": len(recent_metrics),
                "last_updated": datetime.now(UTC).isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            return {"error": str(e)}

    async def health_check(self) -> dict[str, Any]:
        """Perform health check for the performance monitor."""
        try:
            health_status = {
                "healthy": True,
                "timestamp": time.time(),
                "checks": {},
            }

            # Check monitoring capacity
            active_sessions = len(self.active_monitoring_sessions)
            health_status["checks"]["monitoring_capacity"] = {
                "healthy": active_sessions < 100,  # Arbitrary limit
                "active_sessions": active_sessions,
                "capacity_usage_percent": (active_sessions / 100) * 100,
            }

            # Check performance targets compliance
            metrics = await self.get_performance_metrics()
            current_perf = metrics.get("current_performance", {})
            target_compliance = current_perf.get("target_compliance", {})

            health_status["checks"]["performance_targets"] = {
                "healthy": all(target_compliance.values()),
                "response_time_compliant": target_compliance.get(
                    "response_time", False
                ),
                "availability_compliant": target_compliance.get("availability", False),
            }

            if not all(target_compliance.values()):
                health_status["healthy"] = False

            return health_status

        except Exception as e:
            logger.error(f"Performance monitor health check failed: {e}")
            return {
                "healthy": False,
                "error": str(e),
                "timestamp": time.time(),
            }

    async def shutdown(self):
        """Shutdown the performance monitor gracefully."""
        try:
            logger.info("Shutting down performance monitor...")

            # Stop active monitoring sessions
            for session_id in list(self.active_monitoring_sessions.keys()):
                session = self.active_monitoring_sessions[session_id]
                session["status"] = "stopped"
                session["stopped_at"] = datetime.now(UTC)
                del self.active_monitoring_sessions[session_id]

            logger.info("✅ Performance monitor shutdown complete")

        except Exception as e:
            logger.error(f"Error during performance monitor shutdown: {e}")

    # Private helper methods
    async def _continuous_monitoring(self):
        """Background task for continuous performance monitoring."""
        while True:
            try:
                # Collect metrics from active sessions
                for _session_id, session in self.active_monitoring_sessions.items():
                    await self._collect_session_metrics(session)

                # Sleep for monitoring interval
                await asyncio.sleep(self.monitoring_interval)

            except Exception as e:
                logger.error(f"Continuous monitoring error: {e}")
                await asyncio.sleep(self.monitoring_interval)

    async def _collect_session_metrics(self, session: dict[str, Any]):
        """Collect metrics for a monitoring session."""
        try:
            # Simulate metric collection (in production, this would collect real metrics)
            current_time = datetime.now(UTC)

            # Response time metric
            response_time_metric = PerformanceMetric(
                metric_name="response_time_ms",
                value=float(200 + (time.time() % 100)),  # Simulated response time
                unit="milliseconds",
                timestamp=current_time,
                tags={
                    "session_id": session["session_id"],
                    "component": session["component"],
                },
            )

            # Availability metric
            availability_metric = PerformanceMetric(
                metric_name="availability_percent",
                value=99.9,  # Simulated availability
                unit="percent",
                timestamp=current_time,
                tags={
                    "session_id": session["session_id"],
                    "component": session["component"],
                },
            )

            # Add metrics to session and global list
            session["metrics"].extend([response_time_metric, availability_metric])
            self.performance_metrics.extend([response_time_metric, availability_metric])

            # Keep only recent metrics (last 24 hours)
            cutoff_time = datetime.now(UTC).timestamp() - 86400
            self.performance_metrics = [
                m
                for m in self.performance_metrics
                if m.timestamp.timestamp() > cutoff_time
            ]

        except Exception as e:
            logger.error(f"Failed to collect session metrics: {e}")

    async def _bottleneck_detection(self):
        """Background task for bottleneck detection."""
        while True:
            try:
                # Analyze recent metrics for bottlenecks
                for _session_id, session in self.active_monitoring_sessions.items():
                    if len(session["metrics"]) >= 10:  # Need sufficient data
                        bottlenecks = await self._detect_bottlenecks(session)
                        for bottleneck in bottlenecks:
                            self.bottleneck_analyses.append(bottleneck)

                # Sleep for detection interval
                await asyncio.sleep(300)  # Check every 5 minutes

            except Exception as e:
                logger.error(f"Bottleneck detection error: {e}")
                await asyncio.sleep(300)

    async def _detect_bottlenecks(
        self, session: dict[str, Any]
    ) -> list[BottleneckAnalysis]:
        """Detect bottlenecks in a monitoring session."""
        bottlenecks = []

        try:
            # Analyze response time bottlenecks
            response_times = [
                m.value
                for m in session["metrics"]
                if m.metric_name == "response_time_ms"
            ]

            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
                if avg_response_time > self.performance_targets["response_time_ms"]:
                    severity = (
                        "high"
                        if avg_response_time
                        > self.performance_targets["response_time_ms"] * 2
                        else "medium"
                    )

                    bottleneck = BottleneckAnalysis(
                        bottleneck_id=f"response_time_{session['session_id']}_{int(time.time())}",
                        component=session["component"],
                        severity=severity,
                        description=f"Average response time ({avg_response_time:.2f}ms) exceeds target ({self.performance_targets['response_time_ms']}ms)",
                        impact_score=min(
                            avg_response_time
                            / self.performance_targets["response_time_ms"],
                            10.0,
                        ),
                        recommended_actions=[
                            "Optimize database queries",
                            "Implement caching",
                            "Scale horizontally",
                            "Review algorithm efficiency",
                        ],
                    )
                    bottlenecks.append(bottleneck)

            # Analyze availability bottlenecks
            availability_metrics = [
                m.value
                for m in session["metrics"]
                if m.metric_name == "availability_percent"
            ]

            if availability_metrics:
                avg_availability = sum(availability_metrics) / len(availability_metrics)
                if avg_availability < self.performance_targets["availability_percent"]:
                    severity = "critical" if avg_availability < 95 else "high"

                    bottleneck = BottleneckAnalysis(
                        bottleneck_id=f"availability_{session['session_id']}_{int(time.time())}",
                        component=session["component"],
                        severity=severity,
                        description=f"Availability ({avg_availability:.2f}%) below target ({self.performance_targets['availability_percent']}%)",
                        impact_score=(
                            self.performance_targets["availability_percent"]
                            - avg_availability
                        )
                        / 10,
                        recommended_actions=[
                            "Implement circuit breakers",
                            "Add redundancy",
                            "Improve error handling",
                            "Monitor dependencies",
                        ],
                    )
                    bottlenecks.append(bottleneck)

        except Exception as e:
            logger.error(f"Failed to detect bottlenecks: {e}")

        return bottlenecks

    async def _create_optimization_plan(
        self, bottleneck: BottleneckAnalysis
    ) -> OptimizationPlan:
        """Create an optimization plan for a bottleneck."""
        plan_id = f"opt_plan_{bottleneck.bottleneck_id}_{int(time.time())}"

        # Determine optimization type and steps based on bottleneck
        if "response_time" in bottleneck.bottleneck_id:
            optimization_type = "performance_optimization"
            implementation_steps = [
                "Analyze current performance metrics",
                "Identify slow operations",
                "Implement caching layer",
                "Optimize database queries",
                "Monitor improvement",
            ]
            expected_improvement = min(50.0, bottleneck.impact_score * 10)
            estimated_duration = 30
            risk_level = "low"

        elif "availability" in bottleneck.bottleneck_id:
            optimization_type = "reliability_improvement"
            implementation_steps = [
                "Implement health checks",
                "Add circuit breakers",
                "Configure auto-scaling",
                "Set up monitoring alerts",
                "Test failover procedures",
            ]
            expected_improvement = min(30.0, bottleneck.impact_score * 5)
            estimated_duration = 45
            risk_level = "medium"

        else:
            optimization_type = "general_optimization"
            implementation_steps = [
                "Analyze bottleneck root cause",
                "Design optimization strategy",
                "Implement improvements",
                "Validate results",
            ]
            expected_improvement = 20.0
            estimated_duration = 60
            risk_level = "medium"

        return OptimizationPlan(
            plan_id=plan_id,
            target_component=bottleneck.component,
            optimization_type=optimization_type,
            expected_improvement=expected_improvement,
            implementation_steps=implementation_steps,
            estimated_duration_minutes=estimated_duration,
            risk_level=risk_level,
        )

    async def _implement_optimization_plan(
        self, plan: OptimizationPlan
    ) -> dict[str, Any]:
        """Implement an optimization plan."""
        try:
            # Simulate optimization implementation
            logger.info(f"Implementing optimization plan: {plan.plan_id}")

            # In production, this would execute actual optimization steps
            await asyncio.sleep(1)  # Simulate implementation time

            # Simulate success/failure
            success = plan.risk_level in [
                "low",
                "medium",
            ]  # Higher success rate for lower risk

            if success:
                return {
                    "success": True,
                    "plan_id": plan.plan_id,
                    "implemented_steps": len(plan.implementation_steps),
                    "actual_improvement": plan.expected_improvement
                    * 0.8,  # Slightly less than expected
                    "implementation_time_minutes": plan.estimated_duration_minutes
                    * 0.9,
                }
            else:
                return {
                    "success": False,
                    "plan_id": plan.plan_id,
                    "error": "Implementation failed due to high risk",
                }

        except Exception as e:
            logger.error(f"Failed to implement optimization plan: {e}")
            return {"success": False, "plan_id": plan.plan_id, "error": str(e)}

    async def _optimization_engine(self):
        """Background optimization engine."""
        while True:
            try:
                # Find high-impact bottlenecks that need optimization
                critical_bottlenecks = [
                    b
                    for b in self.bottleneck_analyses
                    if b.severity in ["high", "critical"]
                    and b.impact_score > self.optimization_threshold
                ]

                # Create and implement optimization plans for critical bottlenecks
                for bottleneck in critical_bottlenecks[-5:]:  # Limit to 5 most recent
                    plan = await self._create_optimization_plan(bottleneck)
                    if (
                        plan.risk_level == "low"
                    ):  # Only auto-implement low-risk optimizations
                        result = await self._implement_optimization_plan(plan)
                        if result.get("success", False):
                            self.performance_stats["optimizations_implemented"] += 1

                # Sleep for optimization interval
                await asyncio.sleep(1800)  # Check every 30 minutes

            except Exception as e:
                logger.error(f"Optimization engine error: {e}")
                await asyncio.sleep(1800)

    async def _performance_reporting(self):
        """Background performance reporting."""
        while True:
            try:
                # Generate periodic performance reports
                logger.info("Generating periodic performance report")

                # Calculate overall performance statistics
                total_sessions = (
                    len(self.active_monitoring_sessions)
                    + self.performance_stats["total_monitoring_sessions"]
                )
                if total_sessions > 0:
                    optimization_rate = (
                        self.performance_stats["optimizations_implemented"]
                        / total_sessions
                    ) * 100
                    self.performance_stats["average_improvement_percent"] = (
                        optimization_rate
                    )

                # Sleep for reporting interval
                await asyncio.sleep(
                    self.reporting_interval * 60
                )  # Convert minutes to seconds

            except Exception as e:
                logger.error(f"Performance reporting error: {e}")
                await asyncio.sleep(self.reporting_interval * 60)

    async def _calculate_performance_summary(
        self, session: dict[str, Any]
    ) -> dict[str, Any]:
        """Calculate performance summary for a session."""
        try:
            metrics = session.get("metrics", [])
            if not metrics:
                return {"error": "No metrics available"}

            # Calculate response time statistics
            response_times = [
                m.value for m in metrics if m.metric_name == "response_time_ms"
            ]
            response_time_stats = {
                "average": (
                    sum(response_times) / len(response_times) if response_times else 0
                ),
                "min": min(response_times) if response_times else 0,
                "max": max(response_times) if response_times else 0,
                "target": self.performance_targets["response_time_ms"],
                "compliant": (
                    (sum(response_times) / len(response_times))
                    <= self.performance_targets["response_time_ms"]
                    if response_times
                    else False
                ),
            }

            # Calculate availability statistics
            availability_metrics = [
                m.value for m in metrics if m.metric_name == "availability_percent"
            ]
            availability_stats = {
                "average": (
                    sum(availability_metrics) / len(availability_metrics)
                    if availability_metrics
                    else 100
                ),
                "min": min(availability_metrics) if availability_metrics else 100,
                "target": self.performance_targets["availability_percent"],
                "compliant": (
                    (sum(availability_metrics) / len(availability_metrics))
                    >= self.performance_targets["availability_percent"]
                    if availability_metrics
                    else True
                ),
            }

            return {
                "response_time": response_time_stats,
                "availability": availability_stats,
                "metrics_count": len(metrics),
                "monitoring_duration_minutes": (
                    (datetime.now(UTC) - session["started_at"]).total_seconds() / 60
                ),
            }

        except Exception as e:
            logger.error(f"Failed to calculate performance summary: {e}")
            return {"error": str(e)}

    async def _summarize_bottlenecks(self, workflow_id: str) -> dict[str, Any]:
        """Summarize bottlenecks for a workflow."""
        relevant_bottlenecks = [
            b for b in self.bottleneck_analyses if workflow_id in b.bottleneck_id
        ]

        return {
            "total_bottlenecks": len(relevant_bottlenecks),
            "by_severity": {
                "critical": len(
                    [b for b in relevant_bottlenecks if b.severity == "critical"]
                ),
                "high": len([b for b in relevant_bottlenecks if b.severity == "high"]),
                "medium": len(
                    [b for b in relevant_bottlenecks if b.severity == "medium"]
                ),
                "low": len([b for b in relevant_bottlenecks if b.severity == "low"]),
            },
            "average_impact_score": (
                sum(b.impact_score for b in relevant_bottlenecks)
                / len(relevant_bottlenecks)
                if relevant_bottlenecks
                else 0
            ),
        }

    async def _summarize_optimizations(self, workflow_id: str) -> dict[str, Any]:
        """Summarize optimizations for a workflow."""
        relevant_plans = [
            p for p in self.optimization_plans if workflow_id in p.plan_id
        ]

        return {
            "total_plans": len(relevant_plans),
            "by_risk_level": {
                "low": len([p for p in relevant_plans if p.risk_level == "low"]),
                "medium": len([p for p in relevant_plans if p.risk_level == "medium"]),
                "high": len([p for p in relevant_plans if p.risk_level == "high"]),
            },
            "total_expected_improvement": sum(
                p.expected_improvement for p in relevant_plans
            ),
            "total_estimated_duration_minutes": sum(
                p.estimated_duration_minutes for p in relevant_plans
            ),
        }

    async def _generate_recommendations(self, workflow_id: str) -> list[str]:
        """Generate recommendations for a workflow."""
        recommendations = []

        # Analyze bottlenecks and suggest improvements
        relevant_bottlenecks = [
            b for b in self.bottleneck_analyses if workflow_id in b.bottleneck_id
        ]

        if relevant_bottlenecks:
            high_impact_bottlenecks = [
                b for b in relevant_bottlenecks if b.impact_score > 5.0
            ]
            if high_impact_bottlenecks:
                recommendations.append("Address high-impact bottlenecks immediately")
                recommendations.append("Implement performance monitoring alerts")

            response_time_issues = [
                b for b in relevant_bottlenecks if "response_time" in b.bottleneck_id
            ]
            if response_time_issues:
                recommendations.append(
                    "Optimize response time through caching and query optimization"
                )

            availability_issues = [
                b for b in relevant_bottlenecks if "availability" in b.bottleneck_id
            ]
            if availability_issues:
                recommendations.append(
                    "Improve system reliability with circuit breakers and redundancy"
                )
        else:
            recommendations.append(
                "Continue monitoring to maintain optimal performance"
            )
            recommendations.append("Consider proactive optimization opportunities")

        return recommendations
