#!/usr/bin/env python3
"""
Comprehensive Error Tracking and Analysis System for ACGS
Implements advanced error tracking, root cause analysis, and correlation with constitutional compliance.
"""

import asyncio
import json
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Set, Tuple

import aiohttp
import numpy as np
from prometheus_client import (
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    start_http_server,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constitutional hash for compliance validation
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


@dataclass
class ErrorEvent:
    """Represents a single error event."""

    timestamp: datetime
    service_name: str
    service_port: int
    error_type: str
    error_code: str
    error_message: str
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    endpoint: Optional[str] = None
    response_time_ms: Optional[float] = None
    constitutional_compliance_score: Optional[float] = None
    stack_trace: Optional[str] = None
    context: Dict = field(default_factory=dict)


@dataclass
class ErrorPattern:
    """Represents an identified error pattern."""

    pattern_id: str
    error_type: str
    frequency: int
    services_affected: Set[str]
    first_seen: datetime
    last_seen: datetime
    avg_response_time: float
    constitutional_impact: float
    root_cause_hypothesis: str
    suggested_remediation: List[str]


class ComprehensiveErrorTracker:
    """Advanced error tracking and analysis system."""

    def __init__(self):
        self.registry = CollectorRegistry()
        self.setup_metrics()

        # Error storage and analysis
        self.error_events: deque = deque(maxlen=10000)  # Keep last 10k errors
        self.error_patterns: Dict[str, ErrorPattern] = {}
        self.service_error_rates: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=100)
        )

        # ACGS services configuration
        self.services = {
            "auth-service": 8000,
            "ac-service": 8001,
            "integrity-service": 8002,
            "fv-service": 8003,
            "gs-service": 8004,
            "pgc-service": 8005,
            "ec-service": 8006,
            "nats": 4222,
            "prometheus": 9090,
            "grafana": 3001,
            "redis": 6379,
        }

        # Analysis configuration
        self.analysis_window_minutes = 15
        self.error_rate_threshold = 0.01  # 1% target
        self.constitutional_compliance_threshold = 0.95

        logger.info("Comprehensive Error Tracker initialized")

    def setup_metrics(self):
        """Setup Prometheus metrics for error tracking."""
        self.error_events_total = Counter(
            "acgs_error_events_total",
            "Total number of error events",
            ["service", "error_type", "error_code"],
            registry=self.registry,
        )

        self.error_rate_by_service = Gauge(
            "acgs_error_rate_by_service",
            "Error rate per service",
            ["service"],
            registry=self.registry,
        )

        self.constitutional_compliance_errors = Counter(
            "acgs_constitutional_compliance_errors_total",
            "Errors related to constitutional compliance",
            ["service", "compliance_score_range"],
            registry=self.registry,
        )

        self.error_response_time = Histogram(
            "acgs_error_response_time_seconds",
            "Response time for requests that resulted in errors",
            ["service", "error_type"],
            registry=self.registry,
        )

        self.error_patterns_detected = Gauge(
            "acgs_error_patterns_detected",
            "Number of distinct error patterns detected",
            registry=self.registry,
        )

    async def start_monitoring(self):
        """Start the error monitoring system."""
        logger.info("Starting comprehensive error monitoring...")

        # Start Prometheus metrics server
        start_http_server(8090, registry=self.registry)
        logger.info("Prometheus metrics server started on port 8090")

        # Start monitoring tasks
        tasks = [
            asyncio.create_task(self.collect_service_errors()),
            asyncio.create_task(self.analyze_error_patterns()),
            asyncio.create_task(self.generate_error_reports()),
            asyncio.create_task(self.monitor_constitutional_compliance()),
        ]

        await asyncio.gather(*tasks)

    async def collect_service_errors(self):
        """Continuously collect error data from all services."""
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    for service_name, port in self.services.items():
                        await self.collect_service_error_data(
                            session, service_name, port
                        )

                await asyncio.sleep(30)  # Collect every 30 seconds

            except Exception as e:
                logger.error(f"Error in error collection: {e}")
                await asyncio.sleep(10)

    async def collect_service_error_data(
        self, session: aiohttp.ClientSession, service_name: str, port: int
    ):
        """Collect error data from a specific service."""
        try:
            # Try to get metrics from service
            metrics_url = f"http://localhost:{port}/metrics"
            async with session.get(metrics_url, timeout=5) as response:
                if response.status == 200:
                    metrics_text = await response.text()
                    await self.parse_service_metrics(service_name, metrics_text)

            # Try to get health status
            health_url = f"http://localhost:{port}/health"
            async with session.get(health_url, timeout=5) as response:
                if response.status != 200:
                    # Service is down or unhealthy
                    error_event = ErrorEvent(
                        timestamp=datetime.now(timezone.utc),
                        service_name=service_name,
                        service_port=port,
                        error_type="SERVICE_UNAVAILABLE",
                        error_code=str(response.status),
                        error_message=f"Service health check failed with status {response.status}",
                    )
                    await self.record_error_event(error_event)

        except asyncio.TimeoutError:
            error_event = ErrorEvent(
                timestamp=datetime.now(timezone.utc),
                service_name=service_name,
                service_port=port,
                error_type="TIMEOUT",
                error_code="TIMEOUT",
                error_message="Service request timed out",
            )
            await self.record_error_event(error_event)

        except Exception as e:
            error_event = ErrorEvent(
                timestamp=datetime.now(timezone.utc),
                service_name=service_name,
                service_port=port,
                error_type="CONNECTION_ERROR",
                error_code="CONNECTION_FAILED",
                error_message=f"Failed to connect to service: {str(e)}",
            )
            await self.record_error_event(error_event)

    async def parse_service_metrics(self, service_name: str, metrics_text: str):
        """Parse Prometheus metrics to extract error information."""
        lines = metrics_text.split("\n")

        for line in lines:
            if line.startswith("#") or not line.strip():
                continue

            # Parse error-related metrics
            if "error" in line.lower() or "failed" in line.lower():
                try:
                    # Extract metric name, labels, and value
                    parts = line.split(" ")
                    if len(parts) >= 2:
                        metric_part = parts[0]
                        value = float(parts[1])

                        # Extract labels if present
                        if "{" in metric_part and "}" in metric_part:
                            metric_name = metric_part.split("{")[0]
                            labels_str = metric_part.split("{")[1].split("}")[0]
                            labels = self.parse_labels(labels_str)
                        else:
                            metric_name = metric_part
                            labels = {}

                        # Record error if value indicates an error
                        if value > 0 and "error" in metric_name.lower():
                            await self.record_metric_error(
                                service_name, metric_name, labels, value
                            )

                except (ValueError, IndexError) as e:
                    logger.debug(f"Could not parse metric line: {line}, error: {e}")

    def parse_labels(self, labels_str: str) -> Dict[str, str]:
        """Parse Prometheus metric labels."""
        labels = {}
        pairs = labels_str.split(",")

        for pair in pairs:
            if "=" in pair:
                key, value = pair.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"')
                labels[key] = value

        return labels

    async def record_metric_error(
        self, service_name: str, metric_name: str, labels: Dict[str, str], value: float
    ):
        """Record an error event from metrics."""
        error_event = ErrorEvent(
            timestamp=datetime.now(timezone.utc),
            service_name=service_name,
            service_port=self.services.get(service_name, 0),
            error_type="METRIC_ERROR",
            error_code=labels.get("error_code", "UNKNOWN"),
            error_message=f"Metric {metric_name} indicates error: {value}",
            context={"metric_name": metric_name, "labels": labels, "value": value},
        )
        await self.record_error_event(error_event)

    async def record_error_event(self, error_event: ErrorEvent):
        """Record an error event for analysis."""
        self.error_events.append(error_event)

        # Update Prometheus metrics
        self.error_events_total.labels(
            service=error_event.service_name,
            error_type=error_event.error_type,
            error_code=error_event.error_code,
        ).inc()

        # Update service error rate
        current_time = time.time()
        self.service_error_rates[error_event.service_name].append(current_time)

        # Calculate and update error rate
        error_rate = self.calculate_service_error_rate(error_event.service_name)
        self.error_rate_by_service.labels(service=error_event.service_name).set(
            error_rate
        )

        # Track constitutional compliance errors
        if error_event.constitutional_compliance_score is not None:
            compliance_range = self.get_compliance_score_range(
                error_event.constitutional_compliance_score
            )
            self.constitutional_compliance_errors.labels(
                service=error_event.service_name,
                compliance_score_range=compliance_range,
            ).inc()

        # Track response time for errors
        if error_event.response_time_ms is not None:
            self.error_response_time.labels(
                service=error_event.service_name, error_type=error_event.error_type
            ).observe(error_event.response_time_ms / 1000.0)

        logger.debug(
            f"Recorded error event: {error_event.service_name} - {error_event.error_type}"
        )

    def calculate_service_error_rate(self, service_name: str) -> float:
        """Calculate error rate for a service over the analysis window."""
        current_time = time.time()
        window_start = current_time - (self.analysis_window_minutes * 60)

        # Count errors in the time window
        error_times = self.service_error_rates[service_name]
        recent_errors = sum(1 for t in error_times if t >= window_start)

        # Estimate total requests (simplified - in production, get from actual metrics)
        estimated_requests = max(
            100, recent_errors * 10
        )  # Assume 10% error rate as baseline

        return recent_errors / estimated_requests if estimated_requests > 0 else 0.0

    def get_compliance_score_range(self, score: float) -> str:
        """Categorize constitutional compliance score."""
        if score >= 0.95:
            return "excellent"
        elif score >= 0.90:
            return "good"
        elif score >= 0.75:
            return "acceptable"
        else:
            return "poor"

    async def analyze_error_patterns(self):
        """Analyze error events to identify patterns and root causes."""
        while True:
            try:
                await asyncio.sleep(300)  # Analyze every 5 minutes

                if len(self.error_events) < 10:
                    continue

                # Group errors by type and service
                error_groups = defaultdict(list)
                current_time = datetime.now(timezone.utc)
                analysis_window = current_time - timedelta(hours=1)

                for event in self.error_events:
                    if event.timestamp >= analysis_window:
                        key = f"{event.service_name}:{event.error_type}"
                        error_groups[key].append(event)

                # Analyze each group for patterns
                for group_key, events in error_groups.items():
                    # Minimum events to consider a pattern
                    if len(events) >= 3:
                        await self.identify_error_pattern(group_key, events)

                # Update pattern metrics
                self.error_patterns_detected.set(len(self.error_patterns))

                pattern_count = len(self.error_patterns)
                logger.info(f"Pattern analysis complete. {pattern_count} patterns.")

            except Exception as e:
                logger.error(f"Error in pattern analysis: {e}")

    async def identify_error_pattern(self, group_key: str, events: List[ErrorEvent]):
        """Identify and analyze an error pattern."""
        service_name, error_type = group_key.split(":", 1)

        # Calculate pattern statistics
        frequency = len(events)
        first_seen = min(event.timestamp for event in events)
        last_seen = max(event.timestamp for event in events)

        response_times = [
            e.response_time_ms for e in events if e.response_time_ms is not None
        ]
        avg_response_time = np.mean(response_times) if response_times else 0.0

        compliance_scores = [
            e.constitutional_compliance_score
            for e in events
            if e.constitutional_compliance_score is not None
        ]
        constitutional_impact = (
            1.0 - np.mean(compliance_scores) if compliance_scores else 0.0
        )

        # Generate root cause hypothesis
        root_cause_hypothesis = self.generate_root_cause_hypothesis(events)

        # Generate remediation suggestions
        suggested_remediation = self.generate_remediation_suggestions(
            error_type, events
        )

        # Create or update pattern
        pattern_id = f"{service_name}_{error_type}_{int(first_seen.timestamp())}"

        pattern = ErrorPattern(
            pattern_id=pattern_id,
            error_type=error_type,
            frequency=frequency,
            services_affected={service_name},
            first_seen=first_seen,
            last_seen=last_seen,
            avg_response_time=avg_response_time,
            constitutional_impact=constitutional_impact,
            root_cause_hypothesis=root_cause_hypothesis,
            suggested_remediation=suggested_remediation,
        )

        self.error_patterns[pattern_id] = pattern
        logger.info(
            f"Identified error pattern: {pattern_id} with {frequency} occurrences"
        )

    def generate_root_cause_hypothesis(self, events: List[ErrorEvent]) -> str:
        """Generate a hypothesis about the root cause of errors."""
        error_codes = [e.error_code for e in events]
        error_messages = [e.error_message for e in events]

        # Analyze common patterns
        if all("timeout" in msg.lower() for msg in error_messages):
            return "Service response timeouts - possible performance degradation or resource exhaustion"
        elif all("connection" in msg.lower() for msg in error_messages):
            return "Connection failures - possible network issues or service unavailability"
        elif any("constitutional" in msg.lower() for msg in error_messages):
            return "Constitutional compliance violations - policy validation failures"
        elif all(code.startswith("5") for code in error_codes if code.isdigit()):
            return "Server-side errors - possible application bugs or infrastructure issues"
        elif all(code.startswith("4") for code in error_codes if code.isdigit()):
            return "Client-side errors - possible invalid requests or authentication issues"
        else:
            return "Mixed error pattern - requires detailed investigation"

    def generate_remediation_suggestions(
        self, error_type: str, events: List[ErrorEvent]
    ) -> List[str]:
        """Generate remediation suggestions based on error type and patterns."""
        suggestions = []

        if error_type == "TIMEOUT":
            suggestions.extend(
                [
                    "Increase service timeout configurations",
                    "Implement circuit breakers to prevent cascade failures",
                    "Scale up service resources (CPU/Memory)",
                    "Optimize database queries and API calls",
                    "Implement request queuing and rate limiting",
                ]
            )
        elif error_type == "CONNECTION_ERROR":
            suggestions.extend(
                [
                    "Check network connectivity between services",
                    "Verify service discovery and load balancer configuration",
                    "Implement connection pooling and keep-alive",
                    "Add retry mechanisms with exponential backoff",
                    "Monitor and alert on service health",
                ]
            )
        elif error_type == "SERVICE_UNAVAILABLE":
            suggestions.extend(
                [
                    "Implement health checks and auto-restart mechanisms",
                    "Add service redundancy and failover capabilities",
                    "Monitor resource utilization and auto-scaling",
                    "Implement graceful shutdown and startup procedures",
                    "Add dependency health monitoring",
                ]
            )
        elif "constitutional" in error_type.lower():
            suggestions.extend(
                [
                    "Review and update constitutional policy definitions",
                    "Validate constitutional hash consistency across services",
                    "Implement policy caching to reduce validation latency",
                    "Add constitutional compliance monitoring and alerting",
                    "Review policy validation logic for edge cases",
                ]
            )
        else:
            suggestions.extend(
                [
                    "Enable detailed error logging and tracing",
                    "Implement comprehensive monitoring and alerting",
                    "Add automated error recovery mechanisms",
                    "Review and update error handling patterns",
                    "Conduct root cause analysis with development team",
                ]
            )

        return suggestions

    async def generate_error_reports(self):
        """Generate periodic error analysis reports."""
        while True:
            try:
                await asyncio.sleep(3600)  # Generate reports every hour

                report = await self.create_error_analysis_report()
                await self.save_error_report(report)

                # Log critical findings
                if report["overall_error_rate"] > self.error_rate_threshold:
                    logger.warning(
                        f"Error rate {report['overall_error_rate']:.2%} exceeds target "
                        f"{self.error_rate_threshold:.2%}"
                    )

            except Exception as e:
                logger.error(f"Error in report generation: {e}")

    async def create_error_analysis_report(self) -> Dict:
        """Create comprehensive error analysis report."""
        current_time = datetime.now(timezone.utc)
        report_window = current_time - timedelta(hours=1)

        # Filter recent events
        recent_events = [e for e in self.error_events if e.timestamp >= report_window]

        # Calculate overall metrics
        total_errors = len(recent_events)
        estimated_total_requests = max(1000, total_errors * 20)  # Simplified estimation
        overall_error_rate = total_errors / estimated_total_requests

        # Service-specific analysis
        service_analysis = {}
        for service_name in self.services.keys():
            service_errors = [
                e for e in recent_events if e.service_name == service_name
            ]
            service_error_rate = self.calculate_service_error_rate(service_name)

            service_analysis[service_name] = {
                "error_count": len(service_errors),
                "error_rate": service_error_rate,
                "top_error_types": self.get_top_error_types(service_errors),
                "avg_response_time": self.calculate_avg_response_time(service_errors),
            }

        # Constitutional compliance analysis
        compliance_events = [
            e for e in recent_events if e.constitutional_compliance_score is not None
        ]
        avg_compliance = (
            np.mean([e.constitutional_compliance_score for e in compliance_events])
            if compliance_events
            else 1.0
        )

        # Top error patterns
        top_patterns = sorted(
            self.error_patterns.values(), key=lambda p: p.frequency, reverse=True
        )[:10]

        report = {
            "timestamp": current_time.isoformat(),
            "analysis_window_hours": 1,
            "overall_error_rate": overall_error_rate,
            "total_errors": total_errors,
            "constitutional_compliance_avg": avg_compliance,
            "service_analysis": service_analysis,
            "top_error_patterns": [
                {
                    "pattern_id": p.pattern_id,
                    "error_type": p.error_type,
                    "frequency": p.frequency,
                    "services_affected": list(p.services_affected),
                    "constitutional_impact": p.constitutional_impact,
                    "root_cause_hypothesis": p.root_cause_hypothesis,
                    "suggested_remediation": p.suggested_remediation,
                }
                for p in top_patterns
            ],
            "recommendations": self.generate_overall_recommendations(
                recent_events, service_analysis
            ),
        }

        return report

    def get_top_error_types(self, events: List[ErrorEvent]) -> List[Tuple[str, int]]:
        """Get top error types by frequency."""
        error_counts = defaultdict(int)
        for event in events:
            error_counts[event.error_type] += 1

        return sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    def calculate_avg_response_time(self, events: List[ErrorEvent]) -> float:
        """Calculate average response time for events."""
        response_times = [
            e.response_time_ms for e in events if e.response_time_ms is not None
        ]
        return np.mean(response_times) if response_times else 0.0

    def generate_overall_recommendations(
        self, events: List[ErrorEvent], service_analysis: Dict
    ) -> List[str]:
        """Generate overall system recommendations."""
        recommendations = []

        # Check for high error rate services
        high_error_services = [
            service
            for service, analysis in service_analysis.items()
            if analysis["error_rate"] > self.error_rate_threshold
        ]

        if high_error_services:
            recommendations.append(
                f"Priority: Address high error rates in services: {', '.join(high_error_services)}"
            )

        # Check for constitutional compliance issues
        compliance_events = [
            e for e in events if e.constitutional_compliance_score is not None
        ]
        if compliance_events:
            avg_compliance = np.mean(
                [e.constitutional_compliance_score for e in compliance_events]
            )
            if avg_compliance < self.constitutional_compliance_threshold:
                recommendations.append(
                    f"Critical: Constitutional compliance ({avg_compliance:.2%}) below threshold "
                    f"({self.constitutional_compliance_threshold:.2%})"
                )

        # Check for timeout patterns
        timeout_events = [e for e in events if "timeout" in e.error_type.lower()]
        if len(timeout_events) > len(events) * 0.3:  # More than 30% timeouts
            recommendations.append(
                "Performance: High timeout rate detected - investigate service performance"
            )

        # Check for connection issues
        connection_events = [e for e in events if "connection" in e.error_type.lower()]
        if (
            len(connection_events) > len(events) * 0.2
        ):  # More than 20% connection issues
            recommendations.append(
                "Infrastructure: High connection failure rate - check network and service health"
            )

        return recommendations

    async def save_error_report(self, report: Dict):
        """Save error analysis report to file."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"infrastructure/monitoring/error_analysis/reports/error_analysis_{timestamp}.json"

        try:
            import os

            os.makedirs(os.path.dirname(filename), exist_ok=True)

            with open(filename, "w") as f:
                json.dump(report, f, indent=2, default=str)

            logger.info(f"Error analysis report saved: {filename}")

        except Exception as e:
            logger.error(f"Failed to save error report: {e}")

    async def monitor_constitutional_compliance(self):
        """Monitor constitutional compliance across all services."""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute

                async with aiohttp.ClientSession() as session:
                    for service_name, port in self.services.items():
                        if service_name in [
                            "ac-service",
                            "pgc-service",
                        ]:  # Services with constitutional validation
                            await self.check_constitutional_compliance(
                                session, service_name, port
                            )

            except Exception as e:
                logger.error(f"Error in constitutional compliance monitoring: {e}")

    async def check_constitutional_compliance(
        self, session: aiohttp.ClientSession, service_name: str, port: int
    ):
        """Check constitutional compliance for a specific service."""
        try:
            compliance_url = f"http://localhost:{port}/api/v1/metrics/constitutional"
            async with session.get(compliance_url, timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    compliance_score = data.get("compliance_score", 1.0)

                    if compliance_score < self.constitutional_compliance_threshold:
                        error_event = ErrorEvent(
                            timestamp=datetime.now(timezone.utc),
                            service_name=service_name,
                            service_port=port,
                            error_type="CONSTITUTIONAL_COMPLIANCE_VIOLATION",
                            error_code="COMPLIANCE_LOW",
                            error_message=f"Constitutional compliance score {compliance_score:.2%} below threshold",
                            constitutional_compliance_score=compliance_score,
                            context={"constitutional_hash": CONSTITUTIONAL_HASH},
                        )
                        await self.record_error_event(error_event)

        except Exception as e:
            logger.debug(
                f"Could not check constitutional compliance for {service_name}: {e}"
            )


if __name__ == "__main__":
    tracker = ComprehensiveErrorTracker()
    asyncio.run(tracker.start_monitoring())
