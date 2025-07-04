"""
Performance Monitoring and WINA Integration for Multi-Agent Coordination
Extends existing ACGS performance monitoring with multi-agent metrics and WINA optimization.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from uuid import uuid4

from ...shared.blackboard import BlackboardService
from ...shared.wina.core import WINACore
from ...shared.wina.performance_monitoring import WINAPerformanceCollector
from ...shared.performance_monitoring import PerformanceMonitor

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"



@dataclass
class AgentPerformanceMetrics:
    """Performance metrics for individual agents"""
    agent_id: str
    agent_type: str
    tasks_completed: int
    tasks_failed: int
    average_processing_time: float
    success_rate: float
    current_load: int
    last_heartbeat: datetime
    constitutional_compliance_rate: float
    efficiency_score: float
    collaboration_score: float
    confidence: float = 0.8  # Default confidence score


@dataclass
class CoordinationMetrics:
    """Metrics for multi-agent coordination"""
    active_agents: int
    total_governance_requests: int
    completed_requests: int
    failed_requests: int
    average_request_completion_time: float
    coordination_efficiency: float
    conflict_resolution_rate: float
    consensus_success_rate: float
    blackboard_performance: Dict[str, Any]
    system_throughput: float


@dataclass
class WINAOptimizationMetrics:
    """WINA-specific optimization metrics"""
    optimization_cycles_completed: int
    performance_improvements: float
    resource_utilization_efficiency: float
    adaptation_effectiveness: float
    learning_convergence_rate: float
    constitutional_alignment_score: float


class MultiAgentPerformanceMonitor:
    """
    Enhanced performance monitoring for multi-agent coordination system.
    Integrates with existing ACGS monitoring and adds WINA optimization capabilities.
    """
    
    def __init__(
        self,
        blackboard_service: BlackboardService,
        wina_core: Optional[WINACore] = None,
        wina_performance_monitor: Optional[WINAPerformanceCollector] = None,
        base_performance_monitor: Optional[PerformanceMonitor] = None
    ):
        self.blackboard = blackboard_service
        self.wina_core = wina_core
        self.wina_performance_monitor = wina_performance_monitor
        self.base_performance_monitor = base_performance_monitor
        
        self.logger = logging.getLogger(__name__)
        self.is_monitoring = False
        
        # Performance data storage
        self.agent_metrics: Dict[str, AgentPerformanceMetrics] = {}
        self.coordination_history: List[CoordinationMetrics] = []
        self.wina_optimization_history: List[WINAOptimizationMetrics] = []
        
        # Performance thresholds
        self.performance_thresholds = {
            'agent_success_rate_min': 0.85,
            'average_processing_time_max': 30.0,  # seconds
            'coordination_efficiency_min': 0.75,
            'conflict_resolution_rate_min': 0.90,
            'consensus_success_rate_min': 0.80,
            'constitutional_compliance_min': 0.95,
            'system_throughput_min': 10.0  # requests per minute
        }
        
        # WINA optimization parameters
        self.wina_optimization_config = {
            'optimization_interval_minutes': 15,
            'performance_window_minutes': 60,
            'learning_rate': 0.01,
            'adaptation_threshold': 0.1,
            'convergence_tolerance': 0.05
        }

    async def start_monitoring(self) -> None:
        """Start the multi-agent performance monitoring"""
        self.is_monitoring = True
        
        # Start monitoring loops
        asyncio.create_task(self._agent_metrics_collection_loop())
        asyncio.create_task(self._coordination_metrics_collection_loop())
        asyncio.create_task(self._wina_optimization_loop())
        asyncio.create_task(self._performance_analysis_loop())
        asyncio.create_task(self._alerting_loop())
        
        self.logger.info("Multi-agent performance monitoring started")

    async def stop_monitoring(self) -> None:
        """Stop the performance monitoring"""
        self.is_monitoring = False
        self.logger.info("Multi-agent performance monitoring stopped")

    async def _agent_metrics_collection_loop(self) -> None:
        """Collect individual agent performance metrics"""
        while self.is_monitoring:
            try:
                # Get active agents from blackboard
                active_agents = await self.blackboard.get_active_agents()
                
                for agent_id in active_agents:
                    await self._collect_agent_metrics(agent_id)
                
                await asyncio.sleep(30)  # Collect every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in agent metrics collection: {str(e)}")
                await asyncio.sleep(60)

    async def _collect_agent_metrics(self, agent_id: str) -> None:
        """Collect metrics for a specific agent"""
        try:
            # Query agent's recent tasks and performance
            agent_knowledge = await self.blackboard.query_knowledge(
                space='governance',
                agent_id=agent_id,
                limit=100
            )
            
            if not agent_knowledge:
                return
            
            # Calculate performance metrics
            completed_tasks = len([k for k in agent_knowledge if 'analysis_complete' in k.tags])
            failed_tasks = len([k for k in agent_knowledge if 'failed' in k.content.get('task_status', '')])
            total_tasks = completed_tasks + failed_tasks
            
            success_rate = completed_tasks / total_tasks if total_tasks > 0 else 1.0
            
            # Calculate average processing time
            processing_times = []
            for knowledge in agent_knowledge:
                if 'processing_time' in knowledge.content:
                    processing_times.append(knowledge.content['processing_time'])
            
            avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0.0
            
            # Get agent type from knowledge
            agent_type = self._determine_agent_type(agent_id, agent_knowledge)
            
            # Calculate constitutional compliance rate
            compliance_rate = await self._calculate_constitutional_compliance_rate(agent_id, agent_knowledge)
            
            # Calculate efficiency and collaboration scores
            efficiency_score = await self._calculate_efficiency_score(agent_id, success_rate, avg_processing_time)
            collaboration_score = await self._calculate_collaboration_score(agent_id, agent_knowledge)
            
            # Get current load (active tasks)
            current_load = await self._get_agent_current_load(agent_id)
            
            # Calculate confidence score based on performance metrics
            confidence_score = min(1.0, (success_rate + efficiency_score + compliance_rate) / 3.0)

            # Update agent metrics
            metrics = AgentPerformanceMetrics(
                agent_id=agent_id,
                agent_type=agent_type,
                tasks_completed=completed_tasks,
                tasks_failed=failed_tasks,
                average_processing_time=avg_processing_time,
                success_rate=success_rate,
                current_load=current_load,
                last_heartbeat=datetime.now(timezone.utc),
                constitutional_compliance_rate=compliance_rate,
                efficiency_score=efficiency_score,
                collaboration_score=collaboration_score,
                confidence=confidence_score
            )
            
            self.agent_metrics[agent_id] = metrics
            
            # Report to WINA if available
            if self.wina_performance_monitor:
                await self.wina_performance_monitor.record_agent_performance(agent_id, {
                    'success_rate': success_rate,
                    'processing_time': avg_processing_time,
                    'efficiency_score': efficiency_score,
                    'compliance_rate': compliance_rate
                })
            
        except Exception as e:
            self.logger.error(f"Error collecting metrics for agent {agent_id}: {str(e)}")

    async def _coordination_metrics_collection_loop(self) -> None:
        """Collect system-wide coordination metrics"""
        while self.is_monitoring:
            try:
                # Get blackboard metrics
                blackboard_metrics = await self.blackboard.get_metrics()
                
                # Calculate coordination metrics
                coordination_metrics = await self._calculate_coordination_metrics(blackboard_metrics)
                
                # Store metrics
                self.coordination_history.append(coordination_metrics)
                
                # Keep only recent history (last 24 hours)
                cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)
                self.coordination_history = [
                    m for m in self.coordination_history 
                    if hasattr(m, 'timestamp') and m.timestamp > cutoff_time
                ]
                
                await asyncio.sleep(60)  # Collect every minute
                
            except Exception as e:
                self.logger.error(f"Error in coordination metrics collection: {str(e)}")
                await asyncio.sleep(120)

    async def _calculate_coordination_metrics(self, blackboard_metrics: Dict[str, Any]) -> CoordinationMetrics:
        """Calculate system-wide coordination metrics"""
        
        # Get task metrics from blackboard
        task_metrics = blackboard_metrics.get('tasks', {})
        completed_tasks = task_metrics.get('completed', 0)
        failed_tasks = task_metrics.get('failed', 0)
        pending_tasks = task_metrics.get('pending', 0)
        in_progress_tasks = task_metrics.get('in_progress', 0)
        
        total_tasks = completed_tasks + failed_tasks + pending_tasks + in_progress_tasks
        
        # Calculate completion rate and average time
        governance_knowledge = await self.blackboard.query_knowledge(
            space='governance',
            knowledge_type='governance_result',
            limit=100
        )
        
        completion_times = []
        for knowledge in governance_knowledge:
            processing_duration = knowledge.content.get('processing_duration', 0)
            if processing_duration > 0:
                completion_times.append(processing_duration)
        
        avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0.0
        
        # Calculate coordination efficiency
        active_agents = len(self.agent_metrics)
        if active_agents > 0 and total_tasks > 0:
            coordination_efficiency = completed_tasks / (total_tasks * active_agents)
        else:
            coordination_efficiency = 0.0
        
        # Calculate conflict resolution rate
        conflict_metrics = blackboard_metrics.get('conflicts', {})
        total_conflicts = conflict_metrics.get('open', 0) + conflict_metrics.get('resolved', 0)
        resolved_conflicts = conflict_metrics.get('resolved', 0)
        conflict_resolution_rate = resolved_conflicts / total_conflicts if total_conflicts > 0 else 1.0
        
        # Calculate consensus success rate (would need consensus engine integration)
        consensus_success_rate = await self._calculate_consensus_success_rate()
        
        # Calculate system throughput (requests per minute)
        current_time = datetime.utcnow()
        recent_completions = len([
            k for k in governance_knowledge 
            if (current_time - k.timestamp).total_seconds() < 300  # Last 5 minutes
        ])
        system_throughput = recent_completions / 5.0 * 60  # Convert to per minute
        
        return CoordinationMetrics(
            active_agents=active_agents,
            total_governance_requests=total_tasks,
            completed_requests=completed_tasks,
            failed_requests=failed_tasks,
            average_request_completion_time=avg_completion_time,
            coordination_efficiency=coordination_efficiency,
            conflict_resolution_rate=conflict_resolution_rate,
            consensus_success_rate=consensus_success_rate,
            blackboard_performance=blackboard_metrics,
            system_throughput=system_throughput
        )

    async def _wina_optimization_loop(self) -> None:
        """WINA optimization loop for continuous improvement"""
        if not self.wina_core:
            return
        
        while self.is_monitoring:
            try:
                optimization_interval = self.wina_optimization_config['optimization_interval_minutes']
                
                # Perform WINA optimization
                optimization_results = await self._perform_wina_optimization()
                
                # Store optimization metrics
                if optimization_results:
                    self.wina_optimization_history.append(optimization_results)
                
                await asyncio.sleep(optimization_interval * 60)  # Convert to seconds
                
            except Exception as e:
                self.logger.error(f"Error in WINA optimization loop: {str(e)}")
                await asyncio.sleep(300)  # Wait 5 minutes on error

    async def _perform_wina_optimization(self) -> Optional[WINAOptimizationMetrics]:
        """Perform WINA optimization based on current performance"""
        if not self.wina_core:
            return None
        
        try:
            # Collect current performance data
            current_performance = await self._get_current_system_performance()
            
            # Get historical performance for comparison
            historical_performance = await self._get_historical_performance()
            
            # Perform WINA optimization
            optimization_results = await self.wina_core.optimize_performance(
                current_metrics=current_performance,
                historical_metrics=historical_performance,
                optimization_targets=self.performance_thresholds
            )
            
            # Calculate optimization metrics
            performance_improvement = optimization_results.get('performance_improvement', 0.0)
            resource_efficiency = optimization_results.get('resource_efficiency', 0.0)
            adaptation_effectiveness = optimization_results.get('adaptation_effectiveness', 0.0)
            
            # Calculate constitutional alignment
            constitutional_alignment = await self._calculate_constitutional_alignment()
            
            return WINAOptimizationMetrics(
                optimization_cycles_completed=len(self.wina_optimization_history) + 1,
                performance_improvements=performance_improvement,
                resource_utilization_efficiency=resource_efficiency,
                adaptation_effectiveness=adaptation_effectiveness,
                learning_convergence_rate=optimization_results.get('convergence_rate', 0.0),
                constitutional_alignment_score=constitutional_alignment
            )
            
        except Exception as e:
            self.logger.error(f"Error in WINA optimization: {str(e)}")
            return None

    async def _performance_analysis_loop(self) -> None:
        """Analyze performance trends and generate insights"""
        while self.is_monitoring:
            try:
                # Perform performance analysis every 5 minutes
                await self._analyze_performance_trends()
                await self._detect_performance_anomalies()
                await self._generate_optimization_recommendations()
                
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error in performance analysis: {str(e)}")
                await asyncio.sleep(600)  # Wait longer on error

    async def _alerting_loop(self) -> None:
        """Monitor for performance issues and send alerts"""
        while self.is_monitoring:
            try:
                # Check performance thresholds
                alerts = await self._check_performance_thresholds()
                
                # Send alerts if any issues detected
                for alert in alerts:
                    await self._send_performance_alert(alert)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error in alerting loop: {str(e)}")
                await asyncio.sleep(120)

    async def _check_performance_thresholds(self) -> List[Dict[str, Any]]:
        """Check if any performance metrics exceed thresholds"""
        alerts = []
        
        # Check individual agent performance
        for agent_id, metrics in self.agent_metrics.items():
            if metrics.success_rate < self.performance_thresholds['agent_success_rate_min']:
                alerts.append({
                    'type': 'agent_performance',
                    'severity': 'warning',
                    'agent_id': agent_id,
                    'metric': 'success_rate',
                    'value': metrics.success_rate,
                    'threshold': self.performance_thresholds['agent_success_rate_min'],
                    'message': f"Agent {agent_id} success rate below threshold"
                })
            
            if metrics.average_processing_time > self.performance_thresholds['average_processing_time_max']:
                alerts.append({
                    'type': 'agent_performance',
                    'severity': 'warning',
                    'agent_id': agent_id,
                    'metric': 'processing_time',
                    'value': metrics.average_processing_time,
                    'threshold': self.performance_thresholds['average_processing_time_max'],
                    'message': f"Agent {agent_id} processing time exceeds threshold"
                })
            
            if metrics.constitutional_compliance_rate < self.performance_thresholds['constitutional_compliance_min']:
                alerts.append({
                    'type': 'constitutional_compliance',
                    'severity': 'critical',
                    'agent_id': agent_id,
                    'metric': 'compliance_rate',
                    'value': metrics.constitutional_compliance_rate,
                    'threshold': self.performance_thresholds['constitutional_compliance_min'],
                    'message': f"Agent {agent_id} constitutional compliance below threshold"
                })
        
        # Check system-wide coordination metrics
        if self.coordination_history:
            latest_coordination = self.coordination_history[-1]
            
            if latest_coordination.coordination_efficiency < self.performance_thresholds['coordination_efficiency_min']:
                alerts.append({
                    'type': 'coordination_performance',
                    'severity': 'warning',
                    'metric': 'coordination_efficiency',
                    'value': latest_coordination.coordination_efficiency,
                    'threshold': self.performance_thresholds['coordination_efficiency_min'],
                    'message': "System coordination efficiency below threshold"
                })
            
            if latest_coordination.system_throughput < self.performance_thresholds['system_throughput_min']:
                alerts.append({
                    'type': 'system_performance',
                    'severity': 'warning',
                    'metric': 'throughput',
                    'value': latest_coordination.system_throughput,
                    'threshold': self.performance_thresholds['system_throughput_min'],
                    'message': "System throughput below threshold"
                })
        
        return alerts

    async def _send_performance_alert(self, alert: Dict[str, Any]) -> None:
        """Send performance alert"""
        # Add alert knowledge to blackboard
        from ...shared.blackboard import KnowledgeItem
        
        alert_knowledge = KnowledgeItem(
            space='performance',
            agent_id='multi_agent_performance_monitor',
            knowledge_type='performance_alert',
            content=alert,
            priority=1 if alert['severity'] == 'critical' else 2,
            tags={'alert', 'performance', alert['type']}
        )
        
        await self.blackboard.add_knowledge(alert_knowledge)
        
        # Log alert
        severity = alert['severity'].upper()
        message = alert['message']
        self.logger.warning(f"PERFORMANCE ALERT [{severity}]: {message}")

    # Helper methods for metric calculations
    
    def _determine_agent_type(self, agent_id: str, agent_knowledge: List) -> str:
        """Determine agent type from knowledge"""
        if 'ethics' in agent_id.lower():
            return 'ethics_agent'
        elif 'legal' in agent_id.lower():
            return 'legal_agent'
        elif 'operational' in agent_id.lower():
            return 'operational_agent'
        elif 'coordinator' in agent_id.lower():
            return 'coordinator'
        else:
            return 'unknown'

    async def _calculate_constitutional_compliance_rate(self, agent_id: str, agent_knowledge: List) -> float:
        """Calculate constitutional compliance rate for an agent"""
        compliant_decisions = 0
        total_decisions = 0
        
        for knowledge in agent_knowledge:
            if 'constitutional_compliance' in knowledge.content:
                total_decisions += 1
                compliance = knowledge.content['constitutional_compliance']
                if compliance.get('compliant', False):
                    compliant_decisions += 1
        
        return compliant_decisions / total_decisions if total_decisions > 0 else 1.0

    async def _calculate_efficiency_score(self, agent_id: str, success_rate: float, avg_processing_time: float) -> float:
        """Calculate efficiency score for an agent"""
        # Normalize processing time (lower is better)
        time_efficiency = max(0.0, 1.0 - (avg_processing_time / 60.0))  # Normalize to 60 seconds
        
        # Combine success rate and time efficiency
        efficiency_score = (success_rate * 0.7) + (time_efficiency * 0.3)
        return min(1.0, efficiency_score)

    async def _calculate_collaboration_score(self, agent_id: str, agent_knowledge: List) -> float:
        """Calculate collaboration score based on knowledge sharing and coordination"""
        # Simple implementation - could be enhanced
        knowledge_shared = len([k for k in agent_knowledge if 'collaboration' in k.tags])
        total_knowledge = len(agent_knowledge)
        
        return knowledge_shared / total_knowledge if total_knowledge > 0 else 0.5

    async def _get_agent_current_load(self, agent_id: str) -> int:
        """Get current task load for an agent"""
        # Query for in-progress tasks assigned to this agent
        blackboard_metrics = await self.blackboard.get_metrics()
        # This would need to be implemented in the blackboard to track agent-specific loads
        return 0  # Placeholder

    async def _calculate_consensus_success_rate(self) -> float:
        """Calculate consensus success rate"""
        # This would integrate with the consensus engine
        return 0.85  # Placeholder

    async def _get_current_system_performance(self) -> Dict[str, Any]:
        """Get current system performance metrics"""
        if not self.coordination_history:
            return {}
        
        latest_metrics = self.coordination_history[-1]
        
        return {
            'coordination_efficiency': latest_metrics.coordination_efficiency,
            'system_throughput': latest_metrics.system_throughput,
            'conflict_resolution_rate': latest_metrics.conflict_resolution_rate,
            'consensus_success_rate': latest_metrics.consensus_success_rate,
            'active_agents': latest_metrics.active_agents,
            'average_completion_time': latest_metrics.average_request_completion_time
        }

    async def _get_historical_performance(self) -> Dict[str, Any]:
        """Get historical performance for comparison"""
        if len(self.coordination_history) < 2:
            return {}
        
        # Get metrics from 1 hour ago
        historical_metrics = self.coordination_history[-60] if len(self.coordination_history) >= 60 else self.coordination_history[0]
        
        return {
            'coordination_efficiency': historical_metrics.coordination_efficiency,
            'system_throughput': historical_metrics.system_throughput,
            'conflict_resolution_rate': historical_metrics.conflict_resolution_rate,
            'consensus_success_rate': historical_metrics.consensus_success_rate
        }

    async def _calculate_constitutional_alignment(self) -> float:
        """Calculate overall constitutional alignment score"""
        if not self.agent_metrics:
            return 1.0
        
        compliance_rates = [metrics.constitutional_compliance_rate for metrics in self.agent_metrics.values()]
        return sum(compliance_rates) / len(compliance_rates)

    async def _analyze_performance_trends(self) -> None:
        """Analyze performance trends over time"""
        # Implementation for trend analysis
        pass

    async def _detect_performance_anomalies(self) -> None:
        """Detect performance anomalies using statistical methods"""
        # Implementation for anomaly detection
        pass

    async def _generate_optimization_recommendations(self) -> None:
        """Generate optimization recommendations based on performance data"""
        # Implementation for generating recommendations
        pass

    # Public API methods
    
    async def get_agent_performance(self, agent_id: str) -> Optional[AgentPerformanceMetrics]:
        """Get performance metrics for a specific agent"""
        return self.agent_metrics.get(agent_id)

    async def get_system_performance(self) -> Optional[CoordinationMetrics]:
        """Get current system performance metrics"""
        return self.coordination_history[-1] if self.coordination_history else None

    async def get_wina_optimization_status(self) -> Optional[WINAOptimizationMetrics]:
        """Get latest WINA optimization metrics"""
        return self.wina_optimization_history[-1] if self.wina_optimization_history else None

    async def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        system_perf = await self.get_system_performance()
        wina_status = await self.get_wina_optimization_status()
        
        # Calculate average agent performance
        agent_success_rates = [m.success_rate for m in self.agent_metrics.values()]
        avg_agent_success_rate = sum(agent_success_rates) / len(agent_success_rates) if agent_success_rates else 0.0
        
        agent_compliance_rates = [m.constitutional_compliance_rate for m in self.agent_metrics.values()]
        avg_compliance_rate = sum(agent_compliance_rates) / len(agent_compliance_rates) if agent_compliance_rates else 0.0
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'system_health': 'healthy' if avg_agent_success_rate > 0.8 else 'degraded',
            'active_agents': len(self.agent_metrics),
            'average_agent_success_rate': avg_agent_success_rate,
            'average_constitutional_compliance': avg_compliance_rate,
            'system_throughput': system_perf.system_throughput if system_perf else 0.0,
            'coordination_efficiency': system_perf.coordination_efficiency if system_perf else 0.0,
            'wina_optimization_active': self.wina_core is not None,
            'wina_performance_improvement': wina_status.performance_improvements if wina_status else 0.0,
            'alerts_active': len(await self._check_performance_thresholds())
        }

    async def update_performance_thresholds(self, new_thresholds: Dict[str, float]) -> None:
        """Update performance thresholds"""
        self.performance_thresholds.update(new_thresholds)
        self.logger.info(f"Performance thresholds updated: {new_thresholds}")

    async def trigger_manual_optimization(self) -> Optional[WINAOptimizationMetrics]:
        """Manually trigger WINA optimization"""
        if not self.wina_core:
            return None
        
        self.logger.info("Manual WINA optimization triggered")
        return await self._perform_wina_optimization()