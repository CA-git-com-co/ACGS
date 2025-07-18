"""
Monitoring Service Models
Constitutional Hash: cdd01ef066bc6cf2

Data models for system monitoring, metrics, alerts, and observability.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field
import uuid

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class HealthStatus(str, Enum):
    """Service health status"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class AlertSeverity(str, Enum):
    """Alert severity levels"""

    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class AlertStatus(str, Enum):
    """Alert status"""

    ACTIVE = "active"
    RESOLVED = "resolved"
    ACKNOWLEDGED = "acknowledged"
    SUPPRESSED = "suppressed"


class ServiceHealth(BaseModel):
    """Service health information"""

    service_name: str
    status: HealthStatus
    response_time_ms: float
    last_check: datetime
    details: Dict[str, Any] = {}
    constitutional_compliance: bool = True
    error_message: Optional[str] = None
    uptime_percent: Optional[float] = None


class MetricPoint(BaseModel):
    """Single metric data point"""

    service_name: str
    metric_name: str
    value: float
    labels: Dict[str, str] = {}
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ServiceMetrics(BaseModel):
    """Aggregated service metrics"""

    service_name: str
    request_count: int = 0
    error_count: int = 0
    total_response_time_ms: float = 0.0
    avg_response_time_ms: float = 0.0
    p95_response_time_ms: float = 0.0
    p99_response_time_ms: float = 0.0
    cpu_usage_percent: float = 0.0
    memory_usage_percent: float = 0.0
    throughput_rps: float = 0.0
    error_rate_percent: float = 0.0
    uptime_seconds: int = 0
    measurement_window_minutes: int = 60
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class PerformanceMetrics(BaseModel):
    """Performance metrics for a service"""

    service_name: str
    avg_response_time_ms: float
    p95_response_time_ms: float
    p99_response_time_ms: float
    throughput_rps: float
    error_rate_percent: float
    uptime_percent: float
    measurement_window_minutes: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Alert(BaseModel):
    """System alert"""

    alert_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    rule_id: str
    service_name: str
    severity: AlertSeverity
    status: AlertStatus = AlertStatus.ACTIVE
    message: str
    details: Dict[str, Any] = {}
    constitutional_impact: bool = False
    triggered_at: datetime = Field(default_factory=datetime.utcnow)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None


class AlertRule(BaseModel):
    """Alert rule definition"""

    rule_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    condition: str  # Rule condition expression
    severity: AlertSeverity
    threshold: float = 1.0
    evaluation_window_minutes: int = 5
    cooldown_minutes: int = 15
    enabled: bool = True
    constitutional_impact: bool = False
    notification_channels: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SystemOverview(BaseModel):
    """Overall system health overview"""

    total_services: int
    healthy_services: int
    degraded_services: int
    unhealthy_services: int
    overall_availability_percent: float
    constitutional_compliance_percent: float
    active_alerts: int
    critical_alerts: int
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class ServiceDependency(BaseModel):
    """Service dependency information"""

    service_name: str
    dependencies: List[str] = []
    dependency_status: str = "healthy"  # healthy, degraded, unhealthy
    last_checked: datetime = Field(default_factory=datetime.utcnow)


class MonitoringConfig(BaseModel):
    """Monitoring configuration"""

    check_interval_seconds: int = 30
    metric_retention_hours: int = 168  # 7 days
    alert_retention_days: int = 30
    health_check_timeout_seconds: int = 10
    constitutional_compliance_required: bool = True
    performance_targets: Dict[str, float] = {
        "max_response_time_ms": 5000,
        "min_uptime_percent": 99.0,
        "max_error_rate_percent": 1.0,
    }


class SystemEvent(BaseModel):
    """System event for audit trail"""

    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str
    service_name: Optional[str] = None
    severity: str = "info"
    message: str
    details: Dict[str, Any] = {}
    constitutional_impact: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class HealthCheckResult(BaseModel):
    """Health check result"""

    service_name: str
    status: HealthStatus
    response_time_ms: float
    status_code: Optional[int] = None
    response_body: Optional[Dict[str, Any]] = None
    error_details: Optional[str] = None
    constitutional_hash_valid: bool = True
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class MetricQuery(BaseModel):
    """Metric query parameters"""

    service_name: Optional[str] = None
    metric_name: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    aggregation: str = "avg"  # avg, sum, min, max, count
    group_by: List[str] = []


class DashboardWidget(BaseModel):
    """Dashboard widget configuration"""

    widget_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    widget_type: str  # chart, table, metric, alert_list
    config: Dict[str, Any] = {}
    position: Dict[str, int] = {"x": 0, "y": 0, "width": 1, "height": 1}
    refresh_interval_seconds: int = 30
