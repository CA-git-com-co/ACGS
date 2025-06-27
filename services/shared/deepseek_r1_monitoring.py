#!/usr/bin/env python3
"""
DeepSeek R1 Pilot Monitoring Dashboard

Real-time monitoring and metrics collection for the DeepSeek R1 migration pilot.
Tracks constitutional compliance, cost savings, performance metrics, and A/B testing results.

Key Metrics:
- Constitutional compliance rate (target: >95%)
- Response time P95/P99 (target: ≤2s)
- Cost reduction percentage (target: 96.4%)
- A/B testing performance comparison
- DGM safety pattern compliance
"""

import asyncio
import json
import logging
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx
from services.shared.utils import get_config

logger = logging.getLogger(__name__)


@dataclass
class PilotMetrics:
    """Real-time metrics for DeepSeek R1 pilot."""
    timestamp: datetime
    constitutional_compliance_rate: float
    response_time_p95_ms: float
    response_time_p99_ms: float
    cost_reduction_percentage: float
    success_rate: float
    error_rate: float
    fallback_rate: float
    total_requests: int
    deepseek_requests: int
    control_requests: int
    constitutional_hash: str
    pilot_enabled: bool


@dataclass
class CostAnalysis:
    """Cost analysis for pilot evaluation."""
    current_model_cost_per_request: float
    deepseek_cost_per_request: float
    cost_savings_per_request: float
    projected_daily_savings: float
    projected_monthly_savings: float
    projected_annual_savings: float
    cost_reduction_percentage: float


@dataclass
class ComplianceReport:
    """Constitutional compliance analysis."""
    total_validations: int
    compliant_responses: int
    non_compliant_responses: int
    compliance_rate: float
    average_confidence_score: float
    violations_by_type: Dict[str, int]
    constitutional_hash_verified: bool


class DeepSeekR1Monitor:
    """
    Real-time monitoring system for DeepSeek R1 pilot deployment.
    
    Provides comprehensive metrics collection, analysis, and alerting
    for the cost optimization migration while ensuring constitutional compliance.
    """
    
    def __init__(self):
        self.config = get_config()
        self.pilot_config = self.config.get("deepseek_r1_pilot", {})
        self.metrics_history: List[PilotMetrics] = []
        self.cost_history: List[CostAnalysis] = []
        self.compliance_history: List[ComplianceReport] = []
        
        # Alert thresholds from configuration
        self.alert_thresholds = {
            "critical_compliance": float(self.config.get("alert_critical_compliance_threshold", 0.75)),
            "critical_response_time": int(self.config.get("alert_critical_response_time_ms", 5000)),
            "high_compliance": float(self.config.get("alert_high_compliance_threshold", 0.90)),
            "high_response_time": int(self.config.get("alert_high_response_time_ms", 2000)),
            "moderate_compliance": float(self.config.get("alert_moderate_compliance_threshold", 0.95)),
        }
        
        logger.info("DeepSeek R1 Monitor initialized with alert thresholds")
    
    async def collect_metrics(self, ai_model_service) -> PilotMetrics:
        """Collect current pilot metrics from AI model service."""
        pilot_summary = ai_model_service.get_pilot_summary()
        
        if pilot_summary.get("status") == "no_data":
            return self._create_empty_metrics()
        
        # Extract performance metrics
        deepseek_perf = pilot_summary.get("deepseek_performance", {})
        control_perf = pilot_summary.get("control_performance", {})
        cost_analysis = pilot_summary.get("cost_analysis", {})
        
        # Calculate response time percentiles (simplified)
        response_times = []
        if deepseek_perf:
            response_times.append(deepseek_perf.get("avg_response_time_ms", 0))
        if control_perf:
            response_times.append(control_perf.get("avg_response_time_ms", 0))
        
        p95_response_time = max(response_times) * 1.2 if response_times else 0  # Approximation
        p99_response_time = max(response_times) * 1.4 if response_times else 0  # Approximation
        
        metrics = PilotMetrics(
            timestamp=datetime.now(timezone.utc),
            constitutional_compliance_rate=deepseek_perf.get("avg_compliance", 0.0),
            response_time_p95_ms=p95_response_time,
            response_time_p99_ms=p99_response_time,
            cost_reduction_percentage=cost_analysis.get("cost_reduction_percent", 0.0),
            success_rate=deepseek_perf.get("success_rate", 0.0),
            error_rate=1.0 - deepseek_perf.get("success_rate", 1.0),
            fallback_rate=0.0,  # Would need to track this separately
            total_requests=pilot_summary.get("total_requests", 0),
            deepseek_requests=pilot_summary.get("deepseek_requests", 0),
            control_requests=pilot_summary.get("control_requests", 0),
            constitutional_hash=pilot_summary.get("constitutional_hash", ""),
            pilot_enabled=pilot_summary.get("pilot_status") == "active"
        )
        
        self.metrics_history.append(metrics)
        
        # Keep only last 1000 metrics for memory management
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]
        
        return metrics
    
    def _create_empty_metrics(self) -> PilotMetrics:
        """Create empty metrics when no data is available."""
        return PilotMetrics(
            timestamp=datetime.now(timezone.utc),
            constitutional_compliance_rate=0.0,
            response_time_p95_ms=0.0,
            response_time_p99_ms=0.0,
            cost_reduction_percentage=0.0,
            success_rate=0.0,
            error_rate=0.0,
            fallback_rate=0.0,
            total_requests=0,
            deepseek_requests=0,
            control_requests=0,
            constitutional_hash=self.pilot_config.get("constitutional_hash", ""),
            pilot_enabled=self.pilot_config.get("enabled", False)
        )
    
    def analyze_cost_savings(self, metrics: PilotMetrics) -> CostAnalysis:
        """Analyze cost savings from DeepSeek R1 migration."""
        # Cost per 1M tokens
        claude_cost = 15.00  # $15.00/1M tokens
        deepseek_cost = 0.55  # $0.55/1M tokens
        
        # Estimate tokens per request (500 average)
        tokens_per_request = 500
        
        # Calculate costs per request
        current_cost_per_request = (tokens_per_request / 1000000) * claude_cost
        deepseek_cost_per_request = (tokens_per_request / 1000000) * deepseek_cost
        
        cost_savings_per_request = current_cost_per_request - deepseek_cost_per_request
        cost_reduction_percentage = (cost_savings_per_request / current_cost_per_request) * 100
        
        # Project savings based on request volume
        daily_requests = 2740  # ~1M requests/year ÷ 365 days
        monthly_requests = daily_requests * 30
        annual_requests = 1000000

        # Scale up for realistic enterprise usage
        enterprise_multiplier = 10  # Assume 10M requests/year for enterprise
        
        cost_analysis = CostAnalysis(
            current_model_cost_per_request=current_cost_per_request,
            deepseek_cost_per_request=deepseek_cost_per_request,
            cost_savings_per_request=cost_savings_per_request,
            projected_daily_savings=cost_savings_per_request * daily_requests * enterprise_multiplier,
            projected_monthly_savings=cost_savings_per_request * monthly_requests * enterprise_multiplier,
            projected_annual_savings=cost_savings_per_request * annual_requests * enterprise_multiplier,
            cost_reduction_percentage=cost_reduction_percentage
        )
        
        self.cost_history.append(cost_analysis)
        return cost_analysis
    
    def check_alerts(self, metrics: PilotMetrics) -> List[Dict[str, Any]]:
        """Check for alert conditions based on current metrics."""
        alerts = []
        
        # Critical alerts
        if metrics.constitutional_compliance_rate < self.alert_thresholds["critical_compliance"]:
            alerts.append({
                "severity": "critical",
                "type": "constitutional_compliance",
                "message": f"Constitutional compliance critically low: {metrics.constitutional_compliance_rate:.3f}",
                "threshold": self.alert_thresholds["critical_compliance"],
                "current_value": metrics.constitutional_compliance_rate,
                "action_required": "immediate_rollback"
            })
        
        if metrics.response_time_p95_ms > self.alert_thresholds["critical_response_time"]:
            alerts.append({
                "severity": "critical",
                "type": "response_time",
                "message": f"Response time critically high: {metrics.response_time_p95_ms:.1f}ms",
                "threshold": self.alert_thresholds["critical_response_time"],
                "current_value": metrics.response_time_p95_ms,
                "action_required": "immediate_rollback"
            })
        
        # High priority alerts
        if metrics.constitutional_compliance_rate < self.alert_thresholds["high_compliance"]:
            alerts.append({
                "severity": "high",
                "type": "constitutional_compliance",
                "message": f"Constitutional compliance below target: {metrics.constitutional_compliance_rate:.3f}",
                "threshold": self.alert_thresholds["high_compliance"],
                "current_value": metrics.constitutional_compliance_rate,
                "action_required": "investigate_and_monitor"
            })
        
        if metrics.response_time_p95_ms > self.alert_thresholds["high_response_time"]:
            alerts.append({
                "severity": "high",
                "type": "response_time",
                "message": f"Response time above target: {metrics.response_time_p95_ms:.1f}ms",
                "threshold": self.alert_thresholds["high_response_time"],
                "current_value": metrics.response_time_p95_ms,
                "action_required": "performance_optimization"
            })
        
        # Moderate alerts
        if metrics.constitutional_compliance_rate < self.alert_thresholds["moderate_compliance"]:
            alerts.append({
                "severity": "moderate",
                "type": "constitutional_compliance",
                "message": f"Constitutional compliance slightly below target: {metrics.constitutional_compliance_rate:.3f}",
                "threshold": self.alert_thresholds["moderate_compliance"],
                "current_value": metrics.constitutional_compliance_rate,
                "action_required": "monitor_closely"
            })
        
        return alerts
    
    def generate_dashboard_data(self) -> Dict[str, Any]:
        """Generate data for monitoring dashboard."""
        if not self.metrics_history:
            return {"status": "no_data", "message": "No pilot metrics available"}
        
        latest_metrics = self.metrics_history[-1]
        latest_cost_analysis = self.cost_history[-1] if self.cost_history else None
        
        # Calculate trends (last 10 metrics)
        recent_metrics = self.metrics_history[-10:] if len(self.metrics_history) >= 10 else self.metrics_history
        
        compliance_trend = "stable"
        if len(recent_metrics) >= 2:
            compliance_change = recent_metrics[-1].constitutional_compliance_rate - recent_metrics[0].constitutional_compliance_rate
            if compliance_change > 0.01:
                compliance_trend = "improving"
            elif compliance_change < -0.01:
                compliance_trend = "declining"
        
        dashboard_data = {
            "pilot_status": {
                "enabled": latest_metrics.pilot_enabled,
                "traffic_percentage": self.pilot_config.get("traffic_percentage", 0),
                "constitutional_hash": latest_metrics.constitutional_hash,
                "last_updated": latest_metrics.timestamp.isoformat(),
            },
            "performance_metrics": {
                "constitutional_compliance_rate": latest_metrics.constitutional_compliance_rate,
                "response_time_p95_ms": latest_metrics.response_time_p95_ms,
                "response_time_p99_ms": latest_metrics.response_time_p99_ms,
                "success_rate": latest_metrics.success_rate,
                "error_rate": latest_metrics.error_rate,
                "compliance_trend": compliance_trend,
            },
            "traffic_metrics": {
                "total_requests": latest_metrics.total_requests,
                "deepseek_requests": latest_metrics.deepseek_requests,
                "control_requests": latest_metrics.control_requests,
                "deepseek_percentage": (latest_metrics.deepseek_requests / max(latest_metrics.total_requests, 1)) * 100,
            },
            "cost_analysis": asdict(latest_cost_analysis) if latest_cost_analysis else {},
            "alerts": self.check_alerts(latest_metrics),
            "targets": {
                "constitutional_compliance_min": 0.95,
                "response_time_max_ms": 2000,
                "cost_reduction_target_percent": 96.4,
                "success_rate_min": 0.98,
            },
            "phase_progress": {
                "current_phase": "phase_1",
                "phase_name": "Initial Pilot",
                "duration_days": 7,
                "traffic_percentage": 10,
                "success_criteria_met": self._check_phase_success_criteria(latest_metrics),
            }
        }
        
        return dashboard_data
    
    def _check_phase_success_criteria(self, metrics: PilotMetrics) -> Dict[str, bool]:
        """Check if current phase success criteria are met."""
        return {
            "constitutional_compliance": metrics.constitutional_compliance_rate >= 0.95,
            "response_time": metrics.response_time_p95_ms <= 2000,
            "error_rate": metrics.error_rate <= 0.01,
            "overall": (
                metrics.constitutional_compliance_rate >= 0.95 and
                metrics.response_time_p95_ms <= 2000 and
                metrics.error_rate <= 0.01
            )
        }
    
    def export_metrics(self, filepath: str):
        """Export metrics history to JSON file."""
        export_data = {
            "export_timestamp": datetime.now(timezone.utc).isoformat(),
            "pilot_configuration": self.pilot_config,
            "metrics_history": [asdict(m) for m in self.metrics_history],
            "cost_history": [asdict(c) for c in self.cost_history],
            "alert_thresholds": self.alert_thresholds,
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        logger.info(f"Metrics exported to {filepath}")
    
    async def start_monitoring(self, ai_model_service, interval_seconds: int = 30):
        """Start continuous monitoring loop."""
        logger.info(f"Starting DeepSeek R1 pilot monitoring (interval: {interval_seconds}s)")
        
        while True:
            try:
                # Collect current metrics
                metrics = await self.collect_metrics(ai_model_service)
                
                # Analyze cost savings
                cost_analysis = self.analyze_cost_savings(metrics)
                
                # Check for alerts
                alerts = self.check_alerts(metrics)
                
                # Log key metrics
                logger.info(f"Pilot metrics - Compliance: {metrics.constitutional_compliance_rate:.3f}, "
                           f"Response: {metrics.response_time_p95_ms:.1f}ms, "
                           f"Cost reduction: {cost_analysis.cost_reduction_percentage:.1f}%, "
                           f"Alerts: {len(alerts)}")
                
                # Handle critical alerts
                for alert in alerts:
                    if alert["severity"] == "critical":
                        logger.critical(f"CRITICAL ALERT: {alert['message']}")
                        if alert.get("action_required") == "immediate_rollback":
                            logger.critical("Immediate rollback recommended!")
                
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(interval_seconds)


# Global monitor instance
_monitor: Optional[DeepSeekR1Monitor] = None


def get_monitor() -> DeepSeekR1Monitor:
    """Get global monitor instance."""
    global _monitor
    if _monitor is None:
        _monitor = DeepSeekR1Monitor()
    return _monitor
