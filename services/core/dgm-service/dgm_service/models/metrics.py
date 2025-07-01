"""
Performance metrics model for DGM service.
"""

import enum
from typing import Any

from sqlalchemy import JSON, Column, DateTime, Enum, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class MetricType(enum.Enum):
    """Type of performance metric."""

    LATENCY = "latency"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    RESOURCE_USAGE = "resource_usage"
    CONSTITUTIONAL_COMPLIANCE = "constitutional_compliance"
    IMPROVEMENT_SUCCESS_RATE = "improvement_success_rate"
    BANDIT_REWARD = "bandit_reward"
    SYSTEM_HEALTH = "system_health"


class MetricScope(enum.Enum):
    """Scope of the metric measurement."""

    SERVICE = "service"
    SYSTEM = "system"
    IMPROVEMENT = "improvement"
    EXPERIMENT = "experiment"


class PerformanceMetric(Base):
    """Performance metrics for DGM operations."""

    __tablename__ = "performance_metrics"
    __table_args__ = {"schema": "dgm"}

    id = Column(
        PG_UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()
    )
    metric_name = Column(String(255), nullable=False, index=True)
    metric_type = Column(Enum(MetricType), nullable=False, index=True)
    metric_scope = Column(Enum(MetricScope), nullable=False, index=True)

    # Metric values
    value = Column(Numeric(15, 6), nullable=False)
    unit = Column(String(50), nullable=False)

    # Context and metadata
    service_name = Column(String(255), nullable=True, index=True)
    improvement_id = Column(PG_UUID(as_uuid=True), nullable=True, index=True)
    experiment_id = Column(PG_UUID(as_uuid=True), nullable=True, index=True)

    # Additional metric data
    tags = Column(JSON, default=dict)  # Key-value pairs for filtering
    dimensions = Column(JSON, default=dict)  # Dimensional data
    metadata = Column(JSON, default=dict)

    # Constitutional compliance
    constitutional_hash = Column(String(64), nullable=False, default="cdd01ef066bc6cf2")
    constitutional_compliance_score = Column(Numeric(3, 2), nullable=True)

    # Timestamps
    timestamp = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), index=True
    )
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    def __repr__(self):
        return f"<PerformanceMetric(name={self.metric_name}, type={self.metric_type}, value={self.value})>"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": str(self.id),
            "metric_name": self.metric_name,
            "metric_type": self.metric_type.value if self.metric_type else None,
            "metric_scope": self.metric_scope.value if self.metric_scope else None,
            "value": float(self.value),
            "unit": self.unit,
            "service_name": self.service_name,
            "improvement_id": str(self.improvement_id) if self.improvement_id else None,
            "experiment_id": str(self.experiment_id) if self.experiment_id else None,
            "tags": self.tags,
            "dimensions": self.dimensions,
            "metadata": self.metadata,
            "constitutional_hash": self.constitutional_hash,
            "constitutional_compliance_score": (
                float(self.constitutional_compliance_score)
                if self.constitutional_compliance_score
                else None
            ),
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class MetricAggregation(Base):
    """Aggregated performance metrics for efficient querying."""

    __tablename__ = "metric_aggregations"
    __table_args__ = {"schema": "dgm"}

    id = Column(
        PG_UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()
    )
    metric_name = Column(String(255), nullable=False, index=True)
    metric_type = Column(Enum(MetricType), nullable=False, index=True)

    # Aggregation details
    aggregation_type = Column(String(50), nullable=False)  # avg, sum, min, max, count
    time_window = Column(String(50), nullable=False)  # 1m, 5m, 1h, 1d

    # Aggregated values
    value = Column(Numeric(15, 6), nullable=False)
    count = Column(Integer, nullable=False, default=1)
    min_value = Column(Numeric(15, 6), nullable=True)
    max_value = Column(Numeric(15, 6), nullable=True)

    # Context
    service_name = Column(String(255), nullable=True, index=True)
    tags = Column(JSON, default=dict)

    # Time range
    window_start = Column(DateTime(timezone=True), nullable=False, index=True)
    window_end = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    def __repr__(self):
        return (
            f"<MetricAggregation(name={self.metric_name}, "
            f"window={self.time_window}, value={self.value})>"
        )
