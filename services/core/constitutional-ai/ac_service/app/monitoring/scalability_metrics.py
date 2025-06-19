"""
Scalability Metrics Collection System for Constitutional Council

This module provides comprehensive metrics collection for monitoring
Constitutional Council performance, scalability, and democratic governance workflows.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

try:
    from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram

    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of scalability metrics."""

    PERFORMANCE = "performance"
    THROUGHPUT = "throughput"
    LATENCY = "latency"
    AVAILABILITY = "availability"
    CONSENSUS = "consensus"
    DEMOCRATIC_PARTICIPATION = "democratic_participation"


class GovernancePhase(Enum):
    """Phases of democratic governance workflow."""

    PROPOSAL = "proposal"
    REVIEW = "review"
    CONSULTATION = "consultation"
    VOTING = "voting"
    IMPLEMENTATION = "implementation"
    MONITORING = "monitoring"


@dataclass
class ScalabilityMetric:
    """Individual scalability metric data point."""

    metric_type: MetricType
    name: str
    value: float
    unit: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    governance_phase: Optional[GovernancePhase] = None
    amendment_id: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DemocraticParticipationMetrics:
    """Metrics for democratic participation and engagement."""

    total_eligible_voters: int = 0
    active_participants: int = 0
    participation_rate: float = 0.0
    consensus_level: float = 0.0
    stakeholder_diversity_score: float = 0.0
    public_engagement_score: float = 0.0
    transparency_score: float = 0.0

    def calculate_participation_rate(self) -> float:
        """Calculate participation rate."""
        if self.total_eligible_voters == 0:
            return 0.0
        return self.active_participants / self.total_eligible_voters


@dataclass
class PerformanceMetrics:
    """Performance metrics for Constitutional Council operations."""

    amendment_processing_time_ms: float = 0.0
    voting_completion_time_ms: float = 0.0
    consensus_achievement_time_ms: float = 0.0
    database_query_time_ms: float = 0.0
    api_response_time_ms: float = 0.0
    cache_hit_rate: float = 0.0
    error_rate: float = 0.0
    availability_percentage: float = 100.0


class ScalabilityMetricsCollector:
    """Collects and manages scalability metrics for Constitutional Council."""

    def __init__(self, redis_client=None, prometheus_enabled: bool = True):
        self.redis_client = redis_client
        self.prometheus_enabled = prometheus_enabled and PROMETHEUS_AVAILABLE
        self.metrics_buffer: List[ScalabilityMetric] = []
        self.max_buffer_size = 1000

        if self.prometheus_enabled:
            self._setup_prometheus_metrics()

    def _setup_prometheus_metrics(self):
        """Setup Prometheus metrics."""
        if not self.prometheus_enabled:
            return

        self.registry = CollectorRegistry()

        # Performance metrics
        self.amendment_processing_time = Histogram(
            "constitutional_council_amendment_processing_seconds",
            "Time to process constitutional amendments",
            registry=self.registry,
        )

        self.voting_completion_time = Histogram(
            "constitutional_council_voting_completion_seconds",
            "Time to complete voting process",
            registry=self.registry,
        )

        self.consensus_achievement_time = Histogram(
            "constitutional_council_consensus_achievement_seconds",
            "Time to achieve consensus",
            registry=self.registry,
        )

        # Participation metrics
        self.participation_rate = Gauge(
            "constitutional_council_participation_rate",
            "Democratic participation rate",
            registry=self.registry,
        )

        self.consensus_level = Gauge(
            "constitutional_council_consensus_level",
            "Level of consensus achieved",
            registry=self.registry,
        )

        self.stakeholder_diversity = Gauge(
            "constitutional_council_stakeholder_diversity_score",
            "Stakeholder diversity score",
            registry=self.registry,
        )

        # System metrics
        self.api_response_time = Histogram(
            "constitutional_council_api_response_seconds",
            "API response time",
            registry=self.registry,
        )

        self.error_rate = Gauge(
            "constitutional_council_error_rate", "Error rate percentage", registry=self.registry
        )

        self.availability = Gauge(
            "constitutional_council_availability_percentage",
            "System availability percentage",
            registry=self.registry,
        )

        # Counters
        self.amendments_total = Counter(
            "constitutional_council_amendments_total",
            "Total number of amendments processed",
            ["status"],
            registry=self.registry,
        )

        self.votes_total = Counter(
            "constitutional_council_votes_total",
            "Total number of votes cast",
            ["vote_type"],
            registry=self.registry,
        )

    async def record_metric(self, metric: ScalabilityMetric):
        """Record a single metric."""
        self.metrics_buffer.append(metric)

        # Update Prometheus metrics
        if self.prometheus_enabled:
            await self._update_prometheus_metric(metric)

        # Store in Redis if available
        if self.redis_client:
            await self._store_metric_in_redis(metric)

        # Flush buffer if it's getting too large
        if len(self.metrics_buffer) > self.max_buffer_size:
            await self._flush_metrics_buffer()

    async def _update_prometheus_metric(self, metric: ScalabilityMetric):
        """Update Prometheus metrics."""
        try:
            if metric.name == "amendment_processing_time_ms":
                self.amendment_processing_time.observe(metric.value / 1000)
            elif metric.name == "voting_completion_time_ms":
                self.voting_completion_time.observe(metric.value / 1000)
            elif metric.name == "consensus_achievement_time_ms":
                self.consensus_achievement_time.observe(metric.value / 1000)
            elif metric.name == "api_response_time_ms":
                self.api_response_time.observe(metric.value / 1000)
            elif metric.name == "participation_rate":
                self.participation_rate.set(metric.value)
            elif metric.name == "consensus_level":
                self.consensus_level.set(metric.value)
            elif metric.name == "stakeholder_diversity_score":
                self.stakeholder_diversity.set(metric.value)
            elif metric.name == "error_rate":
                self.error_rate.set(metric.value)
            elif metric.name == "availability_percentage":
                self.availability.set(metric.value)
        except Exception as e:
            logger.warning(f"Failed to update Prometheus metric: {e}")

    async def _store_metric_in_redis(self, metric: ScalabilityMetric):
        """Store metric in Redis for real-time monitoring."""
        try:
            if not self.redis_client:
                return

            key = f"constitutional_council:metrics:{metric.name}"
            data = {
                "value": metric.value,
                "unit": metric.unit,
                "timestamp": metric.timestamp.isoformat(),
                "governance_phase": (
                    metric.governance_phase.value if metric.governance_phase else None
                ),
                "amendment_id": metric.amendment_id,
                "metadata": metric.metadata,
            }

            # Store latest value
            await self.redis_client.hset(key, mapping=data)

            # Store in time series for historical analysis
            ts_key = f"constitutional_council:timeseries:{metric.name}"
            await self.redis_client.zadd(
                ts_key,
                {f"{metric.timestamp.timestamp()}:{metric.value}": metric.timestamp.timestamp()},
            )

            # Expire old time series data (keep 30 days)
            cutoff = datetime.utcnow() - timedelta(days=30)
            await self.redis_client.zremrangebyscore(ts_key, 0, cutoff.timestamp())

        except Exception as e:
            logger.warning(f"Failed to store metric in Redis: {e}")

    async def _flush_metrics_buffer(self):
        """Flush metrics buffer to persistent storage."""
        # In a real implementation, this would write to a database
        logger.info(f"Flushing {len(self.metrics_buffer)} metrics to persistent storage")
        self.metrics_buffer.clear()

    async def get_performance_summary(self) -> PerformanceMetrics:
        """Get current performance metrics summary."""
        # This would typically aggregate from Redis or database
        return PerformanceMetrics(
            amendment_processing_time_ms=250.0,  # Mock data
            voting_completion_time_ms=1500.0,
            consensus_achievement_time_ms=3000.0,
            database_query_time_ms=15.0,
            api_response_time_ms=45.0,
            cache_hit_rate=0.85,
            error_rate=0.02,
            availability_percentage=99.7,
        )

    async def get_democratic_participation_summary(self) -> DemocraticParticipationMetrics:
        """Get current democratic participation metrics."""
        # This would typically aggregate from database
        metrics = DemocraticParticipationMetrics(
            total_eligible_voters=150,  # Mock data
            active_participants=127,
            stakeholder_diversity_score=0.78,
            public_engagement_score=0.65,
            transparency_score=0.92,
            consensus_level=0.73,
        )
        metrics.participation_rate = metrics.calculate_participation_rate()
        return metrics

    async def record_amendment_processing_time(self, amendment_id: int, processing_time_ms: float):
        """Record amendment processing time."""
        metric = ScalabilityMetric(
            metric_type=MetricType.PERFORMANCE,
            name="amendment_processing_time_ms",
            value=processing_time_ms,
            unit="milliseconds",
            amendment_id=amendment_id,
            governance_phase=GovernancePhase.PROPOSAL,
        )
        await self.record_metric(metric)

    async def record_voting_completion(
        self, amendment_id: int, completion_time_ms: float, participation_rate: float
    ):
        """Record voting completion metrics."""
        # Processing time
        time_metric = ScalabilityMetric(
            metric_type=MetricType.PERFORMANCE,
            name="voting_completion_time_ms",
            value=completion_time_ms,
            unit="milliseconds",
            amendment_id=amendment_id,
            governance_phase=GovernancePhase.VOTING,
        )
        await self.record_metric(time_metric)

        # Participation rate
        participation_metric = ScalabilityMetric(
            metric_type=MetricType.DEMOCRATIC_PARTICIPATION,
            name="participation_rate",
            value=participation_rate,
            unit="percentage",
            amendment_id=amendment_id,
            governance_phase=GovernancePhase.VOTING,
        )
        await self.record_metric(participation_metric)

    async def record_api_response_time(self, endpoint: str, response_time_ms: float):
        """Record API response time."""
        metric = ScalabilityMetric(
            metric_type=MetricType.LATENCY,
            name="api_response_time_ms",
            value=response_time_ms,
            unit="milliseconds",
            metadata={"endpoint": endpoint},
        )
        await self.record_metric(metric)


# Global metrics collector instance
_metrics_collector: Optional[ScalabilityMetricsCollector] = None


def get_metrics_collector() -> ScalabilityMetricsCollector:
    """Get the global metrics collector instance."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = ScalabilityMetricsCollector()
    return _metrics_collector


async def initialize_metrics_collector(redis_client=None, prometheus_enabled: bool = True):
    """Initialize the global metrics collector."""
    global _metrics_collector
    _metrics_collector = ScalabilityMetricsCollector(
        redis_client=redis_client, prometheus_enabled=prometheus_enabled
    )
    logger.info("Constitutional Council scalability metrics collector initialized")
