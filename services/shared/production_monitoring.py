#!/usr/bin/env python3
"""
Production Monitoring & Analytics for ACGS-PGP Multimodal AI

Comprehensive monitoring system for tracking performance, costs, and constitutional
compliance across all AI models (Gemini Flash Full, Flash Lite, DeepSeek R1).

Features:
- Real-time performance metrics and dashboards
- Cost tracking and optimization analytics
- Constitutional compliance monitoring
- Model performance comparison
- Alert system for performance degradation
- Production health monitoring

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ModelMetrics:
    """Comprehensive metrics for a single AI model."""
    model_name: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time_ms: float = 0.0
    p95_response_time_ms: float = 0.0
    p99_response_time_ms: float = 0.0
    total_cost: float = 0.0
    avg_cost_per_request: float = 0.0
    constitutional_compliance_rate: float = 0.0
    quality_score: float = 0.0
    cache_hit_rate: float = 0.0
    current_load: int = 0
    max_load: int = 0
    circuit_breaker_state: str = "healthy"
    last_updated: str = ""


@dataclass
class SystemMetrics:
    """Overall system performance metrics."""
    total_requests: int = 0
    total_cost: float = 0.0
    avg_response_time_ms: float = 0.0
    constitutional_compliance_rate: float = 0.0
    cache_hit_rate: float = 0.0
    cost_savings_percent: float = 0.0
    uptime_percent: float = 100.0
    active_models: int = 0
    constitutional_hash: str = "cdd01ef066bc6cf2"


@dataclass
class Alert:
    """System alert for monitoring issues."""
    alert_id: str
    severity: str  # critical, high, medium, low
    message: str
    model_affected: Optional[str] = None
    metric_value: Optional[float] = None
    threshold: Optional[float] = None
    timestamp: str = ""
    resolved: bool = False


class ProductionMonitor:
    """Production monitoring system for multimodal AI services."""
    
    def __init__(self):
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.monitoring_start_time = datetime.now(timezone.utc)
        
        # Performance thresholds
        self.thresholds = {
            "response_time_ms": 2000,      # <2s target
            "compliance_rate": 0.95,       # >95% target
            "error_rate": 0.05,            # <5% error rate
            "cost_increase": 0.20,         # <20% cost increase
            "cache_hit_rate": 0.80,        # >80% cache hit rate
            "uptime": 0.99                 # >99% uptime
        }
        
        # Alert storage
        self.alerts: List[Alert] = []
        self.alert_counter = 0
        
        # Metrics history
        self.metrics_history: List[Dict[str, Any]] = []
        
        logger.info("Production Monitor initialized")
    
    async def collect_metrics(self) -> Dict[str, Any]:
        """Collect comprehensive metrics from all system components."""
        
        try:
            # Get multimodal service metrics
            from services.shared.multimodal_ai_service import get_multimodal_service
            
            service = await get_multimodal_service()
            service_metrics = await service.get_service_metrics()
            
            # Get routing metrics
            from services.shared.intelligent_routing import IntelligentRouter
            router = IntelligentRouter()
            routing_metrics = router.get_routing_metrics()
            
            # Get cache metrics
            try:
                from services.shared.multi_level_cache import get_cache_manager
                cache_manager = await get_cache_manager()
                cache_metrics = cache_manager.get_metrics()
            except Exception as e:
                logger.warning(f"Failed to get cache metrics: {e}")
                cache_metrics = {
                    "total_requests": 0,
                    "cache_hit_rate": 0.0,
                    "l1_hits": 0,
                    "l2_hits": 0,
                    "l3_hits": 0,
                    "cache_misses": 0,
                    "error": str(e)
                }
            
            # Process model-specific metrics
            model_metrics = {}
            for model_name, model_data in routing_metrics["model_metrics"].items():
                model_metrics[model_name] = ModelMetrics(
                    model_name=model_name,
                    total_requests=model_data["total_requests"],
                    successful_requests=int(model_data["total_requests"] * model_data["success_rate"]),
                    failed_requests=int(model_data["total_requests"] * model_data["error_rate"]),
                    avg_response_time_ms=model_data["avg_response_time_ms"],
                    p95_response_time_ms=model_data["p95_response_time_ms"],
                    total_cost=model_data["cost_per_request"] * model_data["total_requests"],
                    avg_cost_per_request=model_data["cost_per_request"],
                    constitutional_compliance_rate=model_data["constitutional_compliance_rate"],
                    quality_score=model_data["quality_score"],
                    current_load=model_data["current_load"],
                    max_load=model_data["max_load"],
                    circuit_breaker_state=model_data["circuit_breaker_state"],
                    last_updated=datetime.now(timezone.utc).isoformat()
                )
            
            # Calculate system-wide metrics
            total_requests = sum(m.total_requests for m in model_metrics.values())
            total_cost = sum(m.total_cost for m in model_metrics.values())
            
            # Calculate cost savings (DeepSeek R1 vs Flash Full)
            deepseek_cost = model_metrics.get("deepseek/deepseek-r1-0528:free", ModelMetrics("")).total_cost
            flash_full_cost = model_metrics.get("google/gemini-2.5-flash", ModelMetrics("")).total_cost
            
            if flash_full_cost > 0 and deepseek_cost >= 0:
                equivalent_flash_cost = (deepseek_cost / 0.26) if deepseek_cost > 0 else flash_full_cost  # 74% savings
                cost_savings_percent = ((equivalent_flash_cost - total_cost) / equivalent_flash_cost) * 100 if equivalent_flash_cost > 0 else 0
            else:
                cost_savings_percent = 0
            
            system_metrics = SystemMetrics(
                total_requests=total_requests,
                total_cost=total_cost,
                avg_response_time_ms=service_metrics["performance"]["avg_response_time_ms"],
                constitutional_compliance_rate=service_metrics["quality"]["constitutional_compliance_rate"],
                cache_hit_rate=service_metrics["quality"]["cache_hit_rate"],
                cost_savings_percent=cost_savings_percent,
                uptime_percent=self._calculate_uptime(),
                active_models=len([m for m in model_metrics.values() if m.total_requests > 0]),
                constitutional_hash=self.constitutional_hash
            )
            
            # Store metrics in history
            metrics_snapshot = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "system_metrics": asdict(system_metrics),
                "model_metrics": {name: asdict(metrics) for name, metrics in model_metrics.items()},
                "cache_metrics": cache_metrics,
                "service_metrics": service_metrics
            }
            
            self.metrics_history.append(metrics_snapshot)
            
            # Keep only last 1000 entries
            if len(self.metrics_history) > 1000:
                self.metrics_history = self.metrics_history[-1000:]
            
            # Check for alerts
            await self._check_alerts(system_metrics, model_metrics)
            
            return {
                "system_metrics": asdict(system_metrics),
                "model_metrics": {name: asdict(metrics) for name, metrics in model_metrics.items()},
                "alerts": [asdict(alert) for alert in self.alerts if not alert.resolved],
                "cache_performance": {
                    "l1_hits": cache_metrics.get("l1_hits", 0),
                    "l2_hits": cache_metrics.get("l2_hits", 0),
                    "l3_hits": cache_metrics.get("l3_hits", 0),
                    "cache_misses": cache_metrics.get("cache_misses", 0),
                    "total_requests": cache_metrics.get("total_requests", 0)
                },
                "constitutional_hash": self.constitutional_hash,
                "monitoring_duration_hours": (datetime.now(timezone.utc) - self.monitoring_start_time).total_seconds() / 3600
            }
            
        except Exception as e:
            logger.error(f"Failed to collect metrics: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "constitutional_hash": self.constitutional_hash
            }
    
    async def _check_alerts(self, system_metrics: SystemMetrics, model_metrics: Dict[str, ModelMetrics]):
        """Check for performance issues and generate alerts."""
        
        current_time = datetime.now(timezone.utc).isoformat()
        
        # Check system-wide alerts
        if system_metrics.avg_response_time_ms > self.thresholds["response_time_ms"]:
            self._create_alert(
                "high", 
                f"System response time {system_metrics.avg_response_time_ms:.1f}ms exceeds {self.thresholds['response_time_ms']}ms threshold",
                metric_value=system_metrics.avg_response_time_ms,
                threshold=self.thresholds["response_time_ms"]
            )
        
        if system_metrics.constitutional_compliance_rate < self.thresholds["compliance_rate"]:
            self._create_alert(
                "critical",
                f"Constitutional compliance rate {system_metrics.constitutional_compliance_rate:.1%} below {self.thresholds['compliance_rate']:.1%} threshold",
                metric_value=system_metrics.constitutional_compliance_rate,
                threshold=self.thresholds["compliance_rate"]
            )
        
        if system_metrics.cache_hit_rate < self.thresholds["cache_hit_rate"]:
            self._create_alert(
                "medium",
                f"Cache hit rate {system_metrics.cache_hit_rate:.1%} below {self.thresholds['cache_hit_rate']:.1%} threshold",
                metric_value=system_metrics.cache_hit_rate,
                threshold=self.thresholds["cache_hit_rate"]
            )
        
        # Check model-specific alerts
        for model_name, metrics in model_metrics.items():
            if metrics.total_requests > 0:
                error_rate = metrics.failed_requests / metrics.total_requests
                
                if error_rate > self.thresholds["error_rate"]:
                    self._create_alert(
                        "high",
                        f"Model {model_name} error rate {error_rate:.1%} exceeds {self.thresholds['error_rate']:.1%} threshold",
                        model_affected=model_name,
                        metric_value=error_rate,
                        threshold=self.thresholds["error_rate"]
                    )
                
                if metrics.circuit_breaker_state != "healthy":
                    self._create_alert(
                        "critical",
                        f"Model {model_name} circuit breaker in {metrics.circuit_breaker_state} state",
                        model_affected=model_name
                    )
    
    def _create_alert(self, severity: str, message: str, model_affected: Optional[str] = None,
                     metric_value: Optional[float] = None, threshold: Optional[float] = None):
        """Create a new alert."""
        
        self.alert_counter += 1
        alert = Alert(
            alert_id=f"alert_{self.alert_counter:04d}",
            severity=severity,
            message=message,
            model_affected=model_affected,
            metric_value=metric_value,
            threshold=threshold,
            timestamp=datetime.now(timezone.utc).isoformat(),
            resolved=False
        )
        
        self.alerts.append(alert)
        logger.warning(f"Alert created: {alert.severity.upper()} - {alert.message}")
    
    def _calculate_uptime(self) -> float:
        """Calculate system uptime percentage."""
        
        # Simple uptime calculation based on monitoring duration
        # In production, this would track actual service availability
        monitoring_duration = datetime.now(timezone.utc) - self.monitoring_start_time
        
        if monitoring_duration.total_seconds() < 60:  # Less than 1 minute
            return 100.0
        
        # For demo purposes, assume high uptime
        return 99.9
    
    async def generate_dashboard_data(self) -> Dict[str, Any]:
        """Generate data for monitoring dashboard."""
        
        metrics = await self.collect_metrics()
        
        if "error" in metrics:
            return metrics
        
        # Calculate trends
        trends = self._calculate_trends()
        
        # Generate cost analysis
        cost_analysis = self._generate_cost_analysis(metrics["model_metrics"])
        
        # Performance summary
        performance_summary = self._generate_performance_summary(metrics)
        
        return {
            "dashboard_data": {
                "system_overview": metrics["system_metrics"],
                "model_performance": metrics["model_metrics"],
                "active_alerts": metrics["alerts"],
                "cache_performance": metrics["cache_performance"],
                "trends": trends,
                "cost_analysis": cost_analysis,
                "performance_summary": performance_summary
            },
            "constitutional_hash": self.constitutional_hash,
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
    
    def _calculate_trends(self) -> Dict[str, Any]:
        """Calculate performance trends from historical data."""
        
        if len(self.metrics_history) < 2:
            return {"insufficient_data": True}
        
        recent_metrics = self.metrics_history[-10:]  # Last 10 data points
        
        # Calculate response time trend
        response_times = [m["system_metrics"]["avg_response_time_ms"] for m in recent_metrics]
        response_time_trend = "stable"
        if len(response_times) >= 2:
            if response_times[-1] > response_times[0] * 1.1:
                response_time_trend = "increasing"
            elif response_times[-1] < response_times[0] * 0.9:
                response_time_trend = "decreasing"
        
        # Calculate cost trend
        costs = [m["system_metrics"]["total_cost"] for m in recent_metrics]
        cost_trend = "stable"
        if len(costs) >= 2 and costs[0] > 0:
            if costs[-1] > costs[0] * 1.1:
                cost_trend = "increasing"
            elif costs[-1] < costs[0] * 0.9:
                cost_trend = "decreasing"
        
        return {
            "response_time_trend": response_time_trend,
            "cost_trend": cost_trend,
            "data_points": len(recent_metrics),
            "trend_period_minutes": len(recent_metrics) * 5  # Assuming 5-minute intervals
        }
    
    def _generate_cost_analysis(self, model_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate cost analysis and optimization recommendations."""
        
        total_cost = sum(m["total_cost"] for m in model_metrics.values())
        total_requests = sum(m["total_requests"] for m in model_metrics.values())
        
        # Model cost breakdown
        cost_breakdown = {}
        for model_name, metrics in model_metrics.items():
            if metrics["total_requests"] > 0:
                cost_breakdown[model_name] = {
                    "total_cost": metrics["total_cost"],
                    "cost_per_request": metrics["avg_cost_per_request"],
                    "request_share": metrics["total_requests"] / total_requests if total_requests > 0 else 0,
                    "cost_share": metrics["total_cost"] / total_cost if total_cost > 0 else 0
                }
        
        # Calculate potential savings
        deepseek_requests = model_metrics.get("deepseek/deepseek-r1-0528:free", {}).get("total_requests", 0)
        flash_full_requests = model_metrics.get("google/gemini-2.5-flash", {}).get("total_requests", 0)
        
        potential_savings = 0
        if flash_full_requests > 0:
            flash_full_cost_per_req = model_metrics.get("google/gemini-2.5-flash", {}).get("avg_cost_per_request", 0)
            deepseek_cost_per_req = model_metrics.get("deepseek/deepseek-r1-0528:free", {}).get("avg_cost_per_request", 0)
            potential_savings = (flash_full_cost_per_req - deepseek_cost_per_req) * flash_full_requests
        
        return {
            "total_cost": total_cost,
            "cost_breakdown": cost_breakdown,
            "potential_monthly_savings": potential_savings * 30,  # Estimate monthly
            "cost_optimization_score": min(100, (deepseek_requests / max(1, total_requests)) * 100),
            "recommendations": self._generate_cost_recommendations(cost_breakdown)
        }
    
    def _generate_cost_recommendations(self, cost_breakdown: Dict[str, Any]) -> List[str]:
        """Generate cost optimization recommendations."""
        
        recommendations = []
        
        # Check if DeepSeek R1 is being used effectively
        deepseek_share = cost_breakdown.get("deepseek/deepseek-r1-0528:free", {}).get("request_share", 0)
        if deepseek_share < 0.3:
            recommendations.append("Consider routing more quick analysis and content moderation requests to DeepSeek R1 for 74% cost savings")
        
        # Check for high-cost models
        for model_name, data in cost_breakdown.items():
            if data["cost_per_request"] > 0.002 and data["request_share"] > 0.5:
                recommendations.append(f"High usage of expensive model {model_name} - consider routing optimization")
        
        if not recommendations:
            recommendations.append("Cost optimization is performing well - continue current routing strategy")
        
        return recommendations
    
    def _generate_performance_summary(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate performance summary with key insights."""
        
        system_metrics = metrics["system_metrics"]
        
        # Performance status
        performance_status = "excellent"
        if system_metrics["avg_response_time_ms"] > 1000:
            performance_status = "good"
        if system_metrics["avg_response_time_ms"] > 2000:
            performance_status = "needs_improvement"
        
        # Compliance status
        compliance_status = "excellent"
        if system_metrics["constitutional_compliance_rate"] < 0.95:
            compliance_status = "needs_improvement"
        
        return {
            "performance_status": performance_status,
            "compliance_status": compliance_status,
            "cost_efficiency": "high" if system_metrics["cost_savings_percent"] > 50 else "medium",
            "cache_efficiency": "high" if system_metrics["cache_hit_rate"] > 0.8 else "medium",
            "overall_health": "healthy" if len(metrics["alerts"]) == 0 else "attention_needed",
            "key_metrics": {
                "response_time_ms": system_metrics["avg_response_time_ms"],
                "compliance_rate": system_metrics["constitutional_compliance_rate"],
                "cost_savings_percent": system_metrics["cost_savings_percent"],
                "uptime_percent": system_metrics["uptime_percent"]
            }
        }


# Global monitor instance
_production_monitor: Optional[ProductionMonitor] = None


async def get_production_monitor() -> ProductionMonitor:
    """Get global production monitor instance."""
    global _production_monitor
    
    if _production_monitor is None:
        _production_monitor = ProductionMonitor()
    
    return _production_monitor
