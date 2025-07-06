"""
Enhanced Performance Monitor for ACGS Multi-Agent Systems

Tracks advanced metrics for revolutionary multi-agent architectures including:
- 40% reduction in communication overhead
- 20% improvement in response latency  
- Coordination efficiency metrics
- Document-based communication effectiveness
- Hierarchical coordination performance
- Memory architecture utilization (EMU framework)
- A2A protocol interoperability metrics

Key Features:
- Real-time performance tracking
- Constitutional compliance monitoring
- Multi-agent coordination efficiency
- Structured communication analysis
- Performance regression detection
- Automated alerting and optimization
"""

import asyncio
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
import statistics

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class MetricType(Enum):
    """Types of performance metrics"""
    
    COMMUNICATION_OVERHEAD = "communication_overhead"
    RESPONSE_LATENCY = "response_latency"
    COORDINATION_EFFICIENCY = "coordination_efficiency"
    DOCUMENT_COMMUNICATION = "document_communication"
    HIERARCHICAL_PERFORMANCE = "hierarchical_performance"
    MEMORY_UTILIZATION = "memory_utilization"
    A2A_INTEROPERABILITY = "a2a_interoperability"
    CONSTITUTIONAL_COMPLIANCE = "constitutional_compliance"


class PerformanceTarget(BaseModel):
    """Performance target definition"""
    
    metric_name: str = Field(..., description="Name of the metric")
    target_value: float = Field(..., description="Target value to achieve")
    current_value: float = Field(default=0.0, description="Current measured value")
    improvement_percentage: float = Field(default=0.0, description="Improvement from baseline")
    baseline_value: Optional[float] = Field(None, description="Baseline value for comparison")
    threshold_warning: float = Field(..., description="Warning threshold")
    threshold_critical: float = Field(..., description="Critical threshold")
    unit: str = Field(default="", description="Unit of measurement")
    is_higher_better: bool = Field(default=True, description="Whether higher values are better")


@dataclass
class MetricDataPoint:
    """Individual metric measurement"""
    
    timestamp: datetime
    metric_type: MetricType
    value: float
    agent_id: Optional[str] = None
    workflow_id: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    constitutional_hash: str = CONSTITUTIONAL_HASH


@dataclass
class PerformanceAlert:
    """Performance alert definition"""
    
    alert_id: str
    metric_name: str
    severity: str  # "warning", "critical"
    message: str
    current_value: float
    threshold_value: float
    timestamp: datetime
    agent_id: Optional[str] = None
    workflow_id: Optional[str] = None
    resolved: bool = False


class EnhancedPerformanceMonitor:
    """
    Enhanced performance monitoring system for multi-agent architectures.
    
    Tracks revolutionary improvements in:
    - Communication overhead reduction (target: 40%)
    - Response latency improvement (target: 20%)
    - Coordination efficiency optimization
    - Document-based communication effectiveness
    """
    
    def __init__(self, retention_hours: int = 24):
        self.retention_hours = retention_hours
        
        # Metric storage
        self.metrics: Dict[MetricType, deque] = {
            metric_type: deque(maxlen=10000) for metric_type in MetricType
        }
        
        # Performance targets based on article benchmarks
        self.performance_targets = {
            "communication_overhead_reduction": PerformanceTarget(
                metric_name="communication_overhead_reduction",
                target_value=40.0,  # 40% reduction target
                threshold_warning=30.0,
                threshold_critical=20.0,
                unit="percentage",
                is_higher_better=True
            ),
            "response_latency_improvement": PerformanceTarget(
                metric_name="response_latency_improvement", 
                target_value=20.0,  # 20% improvement target
                threshold_warning=15.0,
                threshold_critical=10.0,
                unit="percentage",
                is_higher_better=True
            ),
            "coordination_efficiency": PerformanceTarget(
                metric_name="coordination_efficiency",
                target_value=0.85,  # 85% efficiency target
                threshold_warning=0.75,
                threshold_critical=0.65,
                unit="ratio",
                is_higher_better=True
            ),
            "document_communication_effectiveness": PerformanceTarget(
                metric_name="document_communication_effectiveness",
                target_value=0.90,  # 90% effectiveness target
                threshold_warning=0.80,
                threshold_critical=0.70,
                unit="ratio",
                is_higher_better=True
            ),
            "p99_latency": PerformanceTarget(
                metric_name="p99_latency",
                target_value=5.0,  # Sub-5ms P99 latency target
                threshold_warning=7.0,
                threshold_critical=10.0,
                unit="milliseconds",
                is_higher_better=False
            ),
            "cache_hit_rate": PerformanceTarget(
                metric_name="cache_hit_rate",
                target_value=85.0,  # >85% cache hit rate target
                threshold_warning=75.0,
                threshold_critical=65.0,
                unit="percentage",
                is_higher_better=True
            ),
            "constitutional_compliance_rate": PerformanceTarget(
                metric_name="constitutional_compliance_rate",
                target_value=95.0,  # >95% constitutional compliance
                threshold_warning=90.0,
                threshold_critical=85.0,
                unit="percentage",
                is_higher_better=True
            )
        }
        
        # Baseline measurements for comparison
        self.baselines: Dict[str, float] = {}
        
        # Active alerts
        self.active_alerts: Dict[str, PerformanceAlert] = {}
        
        # Performance statistics
        self.stats = {
            "total_measurements": 0,
            "alerts_generated": 0,
            "targets_achieved": 0,
            "monitoring_start_time": datetime.now(timezone.utc),
            "last_cleanup": datetime.now(timezone.utc)
        }
        
        # Background tasks
        self.is_running = False
        self.cleanup_task: Optional[asyncio.Task] = None
        self.analysis_task: Optional[asyncio.Task] = None
        
        logger.info("Enhanced Performance Monitor initialized with revolutionary metrics tracking")
    
    async def start(self) -> None:
        """Start the performance monitoring system"""
        try:
            self.is_running = True
            
            # Start background tasks
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())
            self.analysis_task = asyncio.create_task(self._analysis_loop())
            
            logger.info("Enhanced Performance Monitor started")
            
        except Exception as e:
            logger.error(f"Failed to start performance monitor: {e!s}")
            raise
    
    async def stop(self) -> None:
        """Stop the performance monitoring system"""
        try:
            self.is_running = False
            
            # Cancel background tasks
            if self.cleanup_task:
                self.cleanup_task.cancel()
            if self.analysis_task:
                self.analysis_task.cancel()
            
            logger.info("Enhanced Performance Monitor stopped")
            
        except Exception as e:
            logger.error(f"Error stopping performance monitor: {e!s}")
    
    async def record_metric(self, metric_type: MetricType, value: float,
                          agent_id: Optional[str] = None,
                          workflow_id: Optional[str] = None,
                          context: Optional[Dict[str, Any]] = None) -> None:
        """Record a performance metric measurement"""
        try:
            data_point = MetricDataPoint(
                timestamp=datetime.now(timezone.utc),
                metric_type=metric_type,
                value=value,
                agent_id=agent_id,
                workflow_id=workflow_id,
                context=context or {}
            )
            
            self.metrics[metric_type].append(data_point)
            self.stats["total_measurements"] += 1
            
            # Check for alerts
            await self._check_performance_alerts(metric_type, value, agent_id, workflow_id)
            
            logger.debug(f"Recorded {metric_type.value}: {value} for agent {agent_id}")
            
        except Exception as e:
            logger.error(f"Failed to record metric: {e!s}")
    
    async def record_communication_overhead(self, baseline_messages: int, 
                                          optimized_messages: int,
                                          agent_id: Optional[str] = None) -> None:
        """Record communication overhead reduction"""
        try:
            if baseline_messages > 0:
                reduction_percentage = ((baseline_messages - optimized_messages) / baseline_messages) * 100
                await self.record_metric(
                    MetricType.COMMUNICATION_OVERHEAD,
                    reduction_percentage,
                    agent_id=agent_id,
                    context={
                        "baseline_messages": baseline_messages,
                        "optimized_messages": optimized_messages
                    }
                )
                
                # Update performance target
                target = self.performance_targets["communication_overhead_reduction"]
                target.current_value = reduction_percentage
                if target.baseline_value is None:
                    target.baseline_value = 0.0
                target.improvement_percentage = reduction_percentage
                
        except Exception as e:
            logger.error(f"Failed to record communication overhead: {e!s}")
    
    async def record_response_latency(self, baseline_latency: float, 
                                    current_latency: float,
                                    agent_id: Optional[str] = None) -> None:
        """Record response latency improvement"""
        try:
            if baseline_latency > 0:
                improvement_percentage = ((baseline_latency - current_latency) / baseline_latency) * 100
                await self.record_metric(
                    MetricType.RESPONSE_LATENCY,
                    improvement_percentage,
                    agent_id=agent_id,
                    context={
                        "baseline_latency_ms": baseline_latency,
                        "current_latency_ms": current_latency
                    }
                )
                
                # Update performance target
                target = self.performance_targets["response_latency_improvement"]
                target.current_value = improvement_percentage
                if target.baseline_value is None:
                    target.baseline_value = baseline_latency
                target.improvement_percentage = improvement_percentage
                
        except Exception as e:
            logger.error(f"Failed to record response latency: {e!s}")

    async def record_coordination_efficiency(self, successful_coordinations: int,
                                           total_coordinations: int,
                                           workflow_id: Optional[str] = None) -> None:
        """Record coordination efficiency metrics"""
        try:
            if total_coordinations > 0:
                efficiency = successful_coordinations / total_coordinations
                await self.record_metric(
                    MetricType.COORDINATION_EFFICIENCY,
                    efficiency,
                    workflow_id=workflow_id,
                    context={
                        "successful_coordinations": successful_coordinations,
                        "total_coordinations": total_coordinations
                    }
                )

                # Update performance target
                target = self.performance_targets["coordination_efficiency"]
                target.current_value = efficiency

        except Exception as e:
            logger.error(f"Failed to record coordination efficiency: {e!s}")

    async def record_document_communication_effectiveness(self, successful_exchanges: int,
                                                        total_exchanges: int,
                                                        workflow_id: Optional[str] = None) -> None:
        """Record document-based communication effectiveness"""
        try:
            if total_exchanges > 0:
                effectiveness = successful_exchanges / total_exchanges
                await self.record_metric(
                    MetricType.DOCUMENT_COMMUNICATION,
                    effectiveness,
                    workflow_id=workflow_id,
                    context={
                        "successful_exchanges": successful_exchanges,
                        "total_exchanges": total_exchanges
                    }
                )

                # Update performance target
                target = self.performance_targets["document_communication_effectiveness"]
                target.current_value = effectiveness

        except Exception as e:
            logger.error(f"Failed to record document communication effectiveness: {e!s}")

    async def record_p99_latency(self, latency_ms: float,
                               agent_id: Optional[str] = None) -> None:
        """Record P99 latency measurement"""
        try:
            await self.record_metric(
                MetricType.RESPONSE_LATENCY,
                latency_ms,
                agent_id=agent_id,
                context={"metric_type": "p99_latency"}
            )

            # Update performance target
            target = self.performance_targets["p99_latency"]
            target.current_value = latency_ms

        except Exception as e:
            logger.error(f"Failed to record P99 latency: {e!s}")

    async def record_constitutional_compliance(self, compliant_operations: int,
                                             total_operations: int,
                                             agent_id: Optional[str] = None) -> None:
        """Record constitutional compliance rate"""
        try:
            if total_operations > 0:
                compliance_rate = (compliant_operations / total_operations) * 100
                await self.record_metric(
                    MetricType.CONSTITUTIONAL_COMPLIANCE,
                    compliance_rate,
                    agent_id=agent_id,
                    context={
                        "compliant_operations": compliant_operations,
                        "total_operations": total_operations,
                        "constitutional_hash": CONSTITUTIONAL_HASH
                    }
                )

                # Update performance target
                target = self.performance_targets["constitutional_compliance_rate"]
                target.current_value = compliance_rate

        except Exception as e:
            logger.error(f"Failed to record constitutional compliance: {e!s}")

    async def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        try:
            summary = {
                "targets_status": {},
                "recent_metrics": {},
                "alerts": {
                    "active_count": len(self.active_alerts),
                    "critical_alerts": [
                        alert for alert in self.active_alerts.values()
                        if alert.severity == "critical" and not alert.resolved
                    ]
                },
                "statistics": self.stats,
                "constitutional_compliance": {
                    "hash": CONSTITUTIONAL_HASH,
                    "monitoring_active": self.is_running
                }
            }

            # Check target achievement
            for name, target in self.performance_targets.items():
                is_achieved = self._is_target_achieved(target)
                summary["targets_status"][name] = {
                    "achieved": is_achieved,
                    "current_value": target.current_value,
                    "target_value": target.target_value,
                    "improvement_percentage": target.improvement_percentage,
                    "unit": target.unit
                }

            # Get recent metrics for each type
            for metric_type in MetricType:
                recent_values = self._get_recent_values(metric_type, minutes=10)
                if recent_values:
                    summary["recent_metrics"][metric_type.value] = {
                        "count": len(recent_values),
                        "average": statistics.mean(recent_values),
                        "min": min(recent_values),
                        "max": max(recent_values),
                        "latest": recent_values[-1] if recent_values else 0
                    }

            return summary

        except Exception as e:
            logger.error(f"Failed to get performance summary: {e!s}")
            return {"error": str(e)}

    async def _check_performance_alerts(self, metric_type: MetricType, value: float,
                                      agent_id: Optional[str] = None,
                                      workflow_id: Optional[str] = None) -> None:
        """Check if metric value triggers performance alerts"""
        try:
            # Find relevant performance target
            target = None
            for target_name, target_obj in self.performance_targets.items():
                if metric_type.value in target_name or target_name in metric_type.value:
                    target = target_obj
                    break

            if not target:
                return

            # Check thresholds
            alert_severity = None
            threshold_value = None

            if target.is_higher_better:
                if value < target.threshold_critical:
                    alert_severity = "critical"
                    threshold_value = target.threshold_critical
                elif value < target.threshold_warning:
                    alert_severity = "warning"
                    threshold_value = target.threshold_warning
            else:
                if value > target.threshold_critical:
                    alert_severity = "critical"
                    threshold_value = target.threshold_critical
                elif value > target.threshold_warning:
                    alert_severity = "warning"
                    threshold_value = target.threshold_warning

            if alert_severity:
                alert_id = f"{metric_type.value}_{agent_id or 'system'}_{int(time.time())}"
                alert = PerformanceAlert(
                    alert_id=alert_id,
                    metric_name=target.metric_name,
                    severity=alert_severity,
                    message=f"{target.metric_name} {alert_severity}: {value} {target.unit} (threshold: {threshold_value})",
                    current_value=value,
                    threshold_value=threshold_value,
                    timestamp=datetime.now(timezone.utc),
                    agent_id=agent_id,
                    workflow_id=workflow_id
                )

                self.active_alerts[alert_id] = alert
                self.stats["alerts_generated"] += 1

                logger.warning(f"Performance alert: {alert.message}")

        except Exception as e:
            logger.error(f"Failed to check performance alerts: {e!s}")

    def _is_target_achieved(self, target: PerformanceTarget) -> bool:
        """Check if performance target is achieved"""
        if target.is_higher_better:
            return target.current_value >= target.target_value
        else:
            return target.current_value <= target.target_value

    def _get_recent_values(self, metric_type: MetricType, minutes: int = 10) -> List[float]:
        """Get recent metric values within specified time window"""
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=minutes)
            recent_values = [
                point.value for point in self.metrics[metric_type]
                if point.timestamp >= cutoff_time
            ]
            return recent_values

        except Exception as e:
            logger.error(f"Failed to get recent values: {e!s}")
            return []

    async def _cleanup_loop(self) -> None:
        """Background loop to clean up old metrics"""
        while self.is_running:
            try:
                await self._cleanup_old_metrics()
                await asyncio.sleep(3600)  # Cleanup every hour

            except Exception as e:
                logger.error(f"Error in cleanup loop: {e!s}")
                await asyncio.sleep(3600)

    async def _analysis_loop(self) -> None:
        """Background loop for performance analysis"""
        while self.is_running:
            try:
                await self._analyze_performance_trends()
                await asyncio.sleep(300)  # Analyze every 5 minutes

            except Exception as e:
                logger.error(f"Error in analysis loop: {e!s}")
                await asyncio.sleep(300)

    async def _cleanup_old_metrics(self) -> None:
        """Clean up metrics older than retention period"""
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=self.retention_hours)

            for metric_type in MetricType:
                metrics_deque = self.metrics[metric_type]
                # Remove old metrics from the front of deque
                while metrics_deque and metrics_deque[0].timestamp < cutoff_time:
                    metrics_deque.popleft()

            self.stats["last_cleanup"] = datetime.now(timezone.utc)

        except Exception as e:
            logger.error(f"Failed to cleanup old metrics: {e!s}")

    async def _analyze_performance_trends(self) -> None:
        """Analyze performance trends and update targets"""
        try:
            # Count achieved targets
            achieved_count = sum(
                1 for target in self.performance_targets.values()
                if self._is_target_achieved(target)
            )

            self.stats["targets_achieved"] = achieved_count

            # Log performance status
            total_targets = len(self.performance_targets)
            achievement_rate = (achieved_count / total_targets) * 100 if total_targets > 0 else 0

            logger.info(f"Performance targets achieved: {achieved_count}/{total_targets} ({achievement_rate:.1f}%)")

        except Exception as e:
            logger.error(f"Failed to analyze performance trends: {e!s}")
