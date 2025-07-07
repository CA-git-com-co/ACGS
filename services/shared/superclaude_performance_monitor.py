"""
SuperClaude Performance Monitor
Constitutional Hash: cdd01ef066bc6cf2

This module provides comprehensive performance monitoring for SuperClaude operations
within the ACGS system, ensuring performance targets are met while maintaining
constitutional compliance.
"""

import asyncio
import logging
import time
import statistics
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Set, Union
from uuid import uuid4
from collections import defaultdict, deque
from dataclasses import dataclass, field

from pydantic import BaseModel, Field

from .superclaude_persona_integration import SuperClaudePersona
from .constitutional_mcp_integration import MCPTool
from .blackboard import BlackboardService, KnowledgeItem

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics for SuperClaude operations"""
    operation_type: str
    persona: Optional[str] = None
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    latency_ms: Optional[float] = None
    constitutional_overhead_ms: float = 0.0
    mcp_overhead_ms: float = 0.0
    memory_usage_mb: float = 0.0
    success: bool = True
    constitutional_compliant: bool = True
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

class PerformanceReport(BaseModel):
    """Comprehensive performance report"""
    constitutional_hash: str = "cdd01ef066bc6cf2"
    report_period: str
    total_operations: int
    success_rate: float
    constitutional_compliance_rate: float
    avg_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    throughput_rps: float
    constitutional_overhead_avg_ms: float
    mcp_overhead_avg_ms: float
    performance_targets_met: Dict[str, bool]
    persona_performance: Dict[str, Dict[str, float]]
    mcp_tool_performance: Dict[str, Dict[str, float]]
    recommendations: List[str]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SuperClaudePerformanceMonitor:
    """Performance monitor for SuperClaude operations"""
    
    # ACGS Performance Targets
    PERFORMANCE_TARGETS = {
        'p99_latency_ms': 5000,  # P99 <5ms for coordination operations
        'p95_latency_ms': 3000,  # P95 <3ms 
        'avg_latency_ms': 2000,  # Average <2ms
        'throughput_rps': 100,   # >100 RPS for task handoffs
        'success_rate': 0.99,    # 99% success rate
        'constitutional_compliance_rate': 1.0,  # 100% constitutional compliance
        'constitutional_overhead_ms': 1000,  # <1ms additional latency for constitutional validation
        'cache_hit_rate': 0.85   # >85% cache hit rate
    }
    
    # Persona-specific performance targets
    PERSONA_TARGETS = {
        SuperClaudePersona.ARCHITECT: {'p99_latency_ms': 8000, 'complexity_factor': 1.6},
        SuperClaudePersona.SECURITY: {'p99_latency_ms': 6000, 'complexity_factor': 1.2},
        SuperClaudePersona.ANALYZER: {'p99_latency_ms': 7000, 'complexity_factor': 1.4},
        SuperClaudePersona.QA: {'p99_latency_ms': 5000, 'complexity_factor': 1.0},
        SuperClaudePersona.PERFORMANCE: {'p99_latency_ms': 3000, 'complexity_factor': 0.6},
        SuperClaudePersona.FRONTEND: {'p99_latency_ms': 4000, 'complexity_factor': 0.8},
        SuperClaudePersona.BACKEND: {'p99_latency_ms': 5000, 'complexity_factor': 1.0},
        SuperClaudePersona.REFACTORER: {'p99_latency_ms': 6000, 'complexity_factor': 1.2},
        SuperClaudePersona.MENTOR: {'p99_latency_ms': 9000, 'complexity_factor': 1.8}
    }
    
    def __init__(self, blackboard_service: BlackboardService, window_size: int = 1000):
        """Initialize performance monitor"""
        self.blackboard = blackboard_service
        self.window_size = window_size
        self.logger = logging.getLogger(__name__)
        
        # Performance data storage
        self.metrics_history: deque = deque(maxlen=window_size)
        self.operation_counters = defaultdict(int)
        self.persona_metrics = defaultdict(list)
        self.mcp_tool_metrics = defaultdict(list)
        
        # Real-time tracking
        self.active_operations: Dict[str, PerformanceMetrics] = {}
        self.hourly_stats = defaultdict(lambda: defaultdict(list))
        
        # Performance alerting
        self.alert_thresholds = {
            'high_latency_ms': self.PERFORMANCE_TARGETS['p99_latency_ms'] * 1.5,
            'low_throughput_rps': self.PERFORMANCE_TARGETS['throughput_rps'] * 0.8,
            'constitutional_violation_rate': 0.01  # 1% violation rate triggers alert
        }
    
    def start_operation(
        self,
        operation_id: str,
        operation_type: str,
        persona: Optional[SuperClaudePersona] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Start tracking a SuperClaude operation"""
        
        metrics = PerformanceMetrics(
            operation_type=operation_type,
            persona=persona.value if persona else None,
            start_time=time.time()
        )
        
        self.active_operations[operation_id] = metrics
        self.operation_counters[operation_type] += 1
        
        self.logger.debug(f"Started tracking operation {operation_id}: {operation_type}")
        return operation_id
    
    def end_operation(
        self,
        operation_id: str,
        success: bool = True,
        constitutional_compliant: bool = True,
        constitutional_overhead_ms: float = 0.0,
        mcp_overhead_ms: float = 0.0,
        memory_usage_mb: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PerformanceMetrics:
        """End tracking a SuperClaude operation"""
        
        if operation_id not in self.active_operations:
            self.logger.warning(f"Operation {operation_id} not found in active operations")
            return None
        
        metrics = self.active_operations[operation_id]
        metrics.end_time = time.time()
        metrics.latency_ms = (metrics.end_time - metrics.start_time) * 1000
        metrics.success = success
        metrics.constitutional_compliant = constitutional_compliant
        metrics.constitutional_overhead_ms = constitutional_overhead_ms
        metrics.mcp_overhead_ms = mcp_overhead_ms
        metrics.memory_usage_mb = memory_usage_mb
        
        # Store metrics
        self.metrics_history.append(metrics)
        
        # Update persona metrics
        if metrics.persona:
            self.persona_metrics[metrics.persona].append(metrics.latency_ms)
        
        # Update hourly stats
        hour_key = datetime.now().replace(minute=0, second=0, microsecond=0)
        self.hourly_stats[hour_key][metrics.operation_type].append(metrics.latency_ms)
        
        # Remove from active operations
        del self.active_operations[operation_id]
        
        # Check for performance alerts
        asyncio.create_task(self._check_performance_alerts(metrics))
        
        self.logger.debug(
            f"Completed operation {operation_id}: {metrics.latency_ms:.2f}ms, "
            f"success={success}, constitutional_compliant={constitutional_compliant}"
        )
        
        return metrics
    
    async def _check_performance_alerts(self, metrics: PerformanceMetrics) -> None:
        """Check for performance issues and generate alerts"""
        
        alerts = []
        
        # High latency alert
        if metrics.latency_ms > self.alert_thresholds['high_latency_ms']:
            alerts.append({
                'type': 'high_latency',
                'operation': metrics.operation_type,
                'persona': metrics.persona,
                'latency_ms': metrics.latency_ms,
                'threshold_ms': self.alert_thresholds['high_latency_ms'],
                'severity': 'WARNING'
            })
        
        # Constitutional compliance alert
        if not metrics.constitutional_compliant:
            alerts.append({
                'type': 'constitutional_violation',
                'operation': metrics.operation_type,
                'persona': metrics.persona,
                'severity': 'CRITICAL'
            })
        
        # High constitutional overhead alert
        if metrics.constitutional_overhead_ms > self.PERFORMANCE_TARGETS['constitutional_overhead_ms']:
            alerts.append({
                'type': 'high_constitutional_overhead',
                'operation': metrics.operation_type,
                'overhead_ms': metrics.constitutional_overhead_ms,
                'threshold_ms': self.PERFORMANCE_TARGETS['constitutional_overhead_ms'],
                'severity': 'WARNING'
            })
        
        # Log alerts to blackboard
        for alert in alerts:
            await self._log_performance_alert(alert, metrics)
    
    async def _log_performance_alert(self, alert: Dict[str, Any], metrics: PerformanceMetrics) -> None:
        """Log performance alert to blackboard"""
        
        knowledge_item = KnowledgeItem(
            id=str(uuid4()),
            content={
                'type': 'superclaude_performance_alert',
                'alert': alert,
                'metrics': {
                    'operation_type': metrics.operation_type,
                    'persona': metrics.persona,
                    'latency_ms': metrics.latency_ms,
                    'constitutional_compliant': metrics.constitutional_compliant,
                    'constitutional_overhead_ms': metrics.constitutional_overhead_ms
                },
                'constitutional_hash': 'cdd01ef066bc6cf2'
            },
            metadata={
                'source': 'superclaude_performance_monitor',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'severity': alert.get('severity', 'INFO'),
                'alert_type': alert['type']
            },
            tags=['performance', 'alert', 'superclaude', alert['type'], alert.get('severity', 'INFO').lower()]
        )
        
        await self.blackboard.add_knowledge(knowledge_item)
    
    def get_current_performance(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        
        if not self.metrics_history:
            return {'status': 'no_data'}
        
        recent_metrics = list(self.metrics_history)[-100:]  # Last 100 operations
        
        latencies = [m.latency_ms for m in recent_metrics if m.latency_ms is not None]
        constitutional_overheads = [m.constitutional_overhead_ms for m in recent_metrics]
        successes = [m.success for m in recent_metrics]
        constitutional_compliances = [m.constitutional_compliant for m in recent_metrics]
        
        if not latencies:
            return {'status': 'no_latency_data'}
        
        # Calculate throughput (operations per second in last minute)
        now = time.time()
        recent_ops = [m for m in recent_metrics if (now - m.start_time) <= 60]
        throughput_rps = len(recent_ops) / 60.0 if recent_ops else 0.0
        
        current_performance = {
            'avg_latency_ms': statistics.mean(latencies),
            'p95_latency_ms': statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else max(latencies),
            'p99_latency_ms': statistics.quantiles(latencies, n=100)[98] if len(latencies) >= 100 else max(latencies),
            'throughput_rps': throughput_rps,
            'success_rate': sum(successes) / len(successes),
            'constitutional_compliance_rate': sum(constitutional_compliances) / len(constitutional_compliances),
            'avg_constitutional_overhead_ms': statistics.mean(constitutional_overheads) if constitutional_overheads else 0.0,
            'total_operations': len(recent_metrics),
            'active_operations': len(self.active_operations)
        }
        
        # Check against targets
        targets_met = {
            'p99_latency': current_performance['p99_latency_ms'] <= self.PERFORMANCE_TARGETS['p99_latency_ms'],
            'throughput': current_performance['throughput_rps'] >= self.PERFORMANCE_TARGETS['throughput_rps'],
            'success_rate': current_performance['success_rate'] >= self.PERFORMANCE_TARGETS['success_rate'],
            'constitutional_compliance': current_performance['constitutional_compliance_rate'] >= self.PERFORMANCE_TARGETS['constitutional_compliance_rate'],
            'constitutional_overhead': current_performance['avg_constitutional_overhead_ms'] <= self.PERFORMANCE_TARGETS['constitutional_overhead_ms']
        }
        
        current_performance['targets_met'] = targets_met
        current_performance['overall_target_compliance'] = all(targets_met.values())
        
        return current_performance
    
    def get_persona_performance(self) -> Dict[str, Dict[str, float]]:
        """Get performance metrics by persona"""
        
        persona_performance = {}
        
        for persona, latencies in self.persona_metrics.items():
            if latencies:
                persona_performance[persona] = {
                    'avg_latency_ms': statistics.mean(latencies),
                    'p95_latency_ms': statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else max(latencies),
                    'p99_latency_ms': statistics.quantiles(latencies, n=100)[98] if len(latencies) >= 100 else max(latencies),
                    'operation_count': len(latencies),
                    'target_met': (statistics.quantiles(latencies, n=100)[98] if len(latencies) >= 100 else max(latencies)) <= self.PERSONA_TARGETS.get(SuperClaudePersona(persona), {}).get('p99_latency_ms', self.PERFORMANCE_TARGETS['p99_latency_ms'])
                }
        
        return persona_performance
    
    def get_mcp_tool_performance(self) -> Dict[str, Dict[str, float]]:
        """Get performance metrics by MCP tool"""
        
        # Filter metrics by MCP operations
        mcp_metrics = [m for m in self.metrics_history if 'mcp_' in m.operation_type]
        
        tool_performance = defaultdict(list)
        for metrics in mcp_metrics:
            # Extract tool name from operation type (e.g., 'mcp_sequential_analysis' -> 'sequential')
            parts = metrics.operation_type.split('_')
            if len(parts) >= 2 and parts[0] == 'mcp':
                tool_name = parts[1]
                tool_performance[tool_name].append(metrics.latency_ms)
        
        result = {}
        for tool, latencies in tool_performance.items():
            if latencies:
                result[tool] = {
                    'avg_latency_ms': statistics.mean(latencies),
                    'p95_latency_ms': statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else max(latencies),
                    'p99_latency_ms': statistics.quantiles(latencies, n=100)[98] if len(latencies) >= 100 else max(latencies),
                    'operation_count': len(latencies)
                }
        
        return result
    
    async def generate_performance_report(self, period_hours: int = 24) -> PerformanceReport:
        """Generate comprehensive performance report"""
        
        # Filter metrics for the specified period
        cutoff_time = time.time() - (period_hours * 3600)
        period_metrics = [m for m in self.metrics_history if m.start_time >= cutoff_time]
        
        if not period_metrics:
            # Return empty report
            return PerformanceReport(
                report_period=f"last_{period_hours}_hours",
                total_operations=0,
                success_rate=0.0,
                constitutional_compliance_rate=0.0,
                avg_latency_ms=0.0,
                p95_latency_ms=0.0,
                p99_latency_ms=0.0,
                throughput_rps=0.0,
                constitutional_overhead_avg_ms=0.0,
                mcp_overhead_avg_ms=0.0,
                performance_targets_met={},
                persona_performance={},
                mcp_tool_performance={},
                recommendations=["No operations in the specified period"]
            )
        
        # Calculate metrics
        latencies = [m.latency_ms for m in period_metrics if m.latency_ms is not None]
        constitutional_overheads = [m.constitutional_overhead_ms for m in period_metrics]
        mcp_overheads = [m.mcp_overhead_ms for m in period_metrics]
        successes = [m.success for m in period_metrics]
        constitutional_compliances = [m.constitutional_compliant for m in period_metrics]
        
        avg_latency_ms = statistics.mean(latencies) if latencies else 0.0
        p95_latency_ms = statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else (max(latencies) if latencies else 0.0)
        p99_latency_ms = statistics.quantiles(latencies, n=100)[98] if len(latencies) >= 100 else (max(latencies) if latencies else 0.0)
        
        success_rate = sum(successes) / len(successes) if successes else 0.0
        constitutional_compliance_rate = sum(constitutional_compliances) / len(constitutional_compliances) if constitutional_compliances else 0.0
        
        # Calculate throughput
        throughput_rps = len(period_metrics) / (period_hours * 3600)
        
        # Check performance targets
        performance_targets_met = {
            'p99_latency': p99_latency_ms <= self.PERFORMANCE_TARGETS['p99_latency_ms'],
            'p95_latency': p95_latency_ms <= self.PERFORMANCE_TARGETS['p95_latency_ms'],
            'avg_latency': avg_latency_ms <= self.PERFORMANCE_TARGETS['avg_latency_ms'],
            'throughput': throughput_rps >= self.PERFORMANCE_TARGETS['throughput_rps'],
            'success_rate': success_rate >= self.PERFORMANCE_TARGETS['success_rate'],
            'constitutional_compliance': constitutional_compliance_rate >= self.PERFORMANCE_TARGETS['constitutional_compliance_rate']
        }
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            performance_targets_met, avg_latency_ms, p99_latency_ms, throughput_rps, 
            success_rate, constitutional_compliance_rate
        )
        
        # Create performance report
        report = PerformanceReport(
            report_period=f"last_{period_hours}_hours",
            total_operations=len(period_metrics),
            success_rate=success_rate,
            constitutional_compliance_rate=constitutional_compliance_rate,
            avg_latency_ms=avg_latency_ms,
            p95_latency_ms=p95_latency_ms,
            p99_latency_ms=p99_latency_ms,
            throughput_rps=throughput_rps,
            constitutional_overhead_avg_ms=statistics.mean(constitutional_overheads) if constitutional_overheads else 0.0,
            mcp_overhead_avg_ms=statistics.mean(mcp_overheads) if mcp_overheads else 0.0,
            performance_targets_met=performance_targets_met,
            persona_performance=self.get_persona_performance(),
            mcp_tool_performance=self.get_mcp_tool_performance(),
            recommendations=recommendations
        )
        
        # Log report to blackboard
        await self._log_performance_report(report)
        
        return report
    
    def _generate_recommendations(
        self,
        targets_met: Dict[str, bool],
        avg_latency_ms: float,
        p99_latency_ms: float,
        throughput_rps: float,
        success_rate: float,
        constitutional_compliance_rate: float
    ) -> List[str]:
        """Generate performance recommendations"""
        
        recommendations = []
        
        # Latency recommendations
        if not targets_met.get('p99_latency', True):
            recommendations.append(
                f"P99 latency ({p99_latency_ms:.2f}ms) exceeds target ({self.PERFORMANCE_TARGETS['p99_latency_ms']}ms). "
                "Consider optimizing constitutional validation or implementing caching."
            )
        
        if not targets_met.get('avg_latency', True):
            recommendations.append(
                f"Average latency ({avg_latency_ms:.2f}ms) exceeds target ({self.PERFORMANCE_TARGETS['avg_latency_ms']}ms). "
                "Review persona-specific optimizations."
            )
        
        # Throughput recommendations
        if not targets_met.get('throughput', True):
            recommendations.append(
                f"Throughput ({throughput_rps:.2f} RPS) below target ({self.PERFORMANCE_TARGETS['throughput_rps']} RPS). "
                "Consider scaling multi-agent coordination or implementing parallelization."
            )
        
        # Success rate recommendations
        if not targets_met.get('success_rate', True):
            recommendations.append(
                f"Success rate ({success_rate:.2%}) below target ({self.PERFORMANCE_TARGETS['success_rate']:.2%}). "
                "Investigate error patterns and improve error handling."
            )
        
        # Constitutional compliance recommendations
        if not targets_met.get('constitutional_compliance', True):
            recommendations.append(
                f"Constitutional compliance rate ({constitutional_compliance_rate:.2%}) below target (100%). "
                "CRITICAL: Review constitutional validation processes immediately."
            )
        
        # General recommendations
        if all(targets_met.values()):
            recommendations.append("All performance targets met. Continue monitoring for sustained performance.")
        else:
            recommendations.append("Performance optimization required. Prioritize constitutional compliance and latency improvements.")
        
        return recommendations
    
    async def _log_performance_report(self, report: PerformanceReport) -> None:
        """Log performance report to blackboard"""
        
        knowledge_item = KnowledgeItem(
            id=str(uuid4()),
            content={
                'type': 'superclaude_performance_report',
                'report': report.dict(),
                'constitutional_hash': 'cdd01ef066bc6cf2'
            },
            metadata={
                'source': 'superclaude_performance_monitor',
                'timestamp': report.timestamp.isoformat(),
                'report_period': report.report_period,
                'constitutional_compliance': report.constitutional_compliance_rate >= 1.0,
                'performance_summary': 'targets_met' if all(report.performance_targets_met.values()) else 'targets_missed'
            },
            tags=['performance', 'report', 'superclaude', report.report_period]
        )
        
        await self.blackboard.add_knowledge(knowledge_item)