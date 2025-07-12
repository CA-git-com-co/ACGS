"""
Sentry Agent Monitoring for Multi-Agent Coordination

Provides comprehensive monitoring for agent coordination, consensus building,
conflict resolution, and task distribution with constitutional compliance.

Constitutional Hash: cdd01ef066bc6cf2
"""

import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import sentry_sdk
from enum import Enum

# Import shared monitoring utilities
try:
    from services.shared.monitoring.sentry_integration import (
        init_sentry,
        track_agent_coordination,
        capture_constitutional_event,
        monitor_performance_target
    )
    from services.shared.monitoring.sentry_alerts import (
        ConstitutionalAlertManager,
        AlertRules
    )
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False
    print("Warning: Sentry monitoring not available")


CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class AgentType(Enum):
    """Types of agents in the coordination system"""
    ETHICS = "ethics"
    LEGAL = "legal"
    OPERATIONAL = "operational"
    ORCHESTRATOR = "orchestrator"
    DOMAIN_SPECIALIST = "domain_specialist"
    WORKER = "worker"


class CoordinationPhase(Enum):
    """Phases of multi-agent coordination"""
    TASK_DECOMPOSITION = "task_decomposition"
    AGENT_SELECTION = "agent_selection"
    TASK_DISTRIBUTION = "task_distribution"
    EXECUTION = "execution"
    CONSENSUS_BUILDING = "consensus_building"
    CONFLICT_RESOLUTION = "conflict_resolution"
    RESULT_SYNTHESIS = "result_synthesis"


class MultiAgentSentryMonitor:
    """Monitor multi-agent coordination with Sentry integration"""
    
    def __init__(self, service_name: str = "multi-agent-coordinator"):
        self.service_name = service_name
        self.alert_manager = None
        self.active_coordination_sessions: Dict[str, Any] = {}
        self.initialized = False
        
    def initialize(self, environment: str = "development") -> None:
        """Initialize Sentry monitoring for multi-agent coordination"""
        if not SENTRY_AVAILABLE or self.initialized:
            return
            
        # Initialize base Sentry
        init_sentry(
            service_name=self.service_name,
            environment=environment,
            sample_rate=0.3 if environment == "production" else 1.0,
            enable_profiling=True
        )
        
        # Initialize alert manager
        self.alert_manager = ConstitutionalAlertManager(self.service_name)
        
        # Set multi-agent context
        sentry_sdk.set_context("multi_agent_system", {
            "coordinator_version": "2.0.0",
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "agent_types": [agent.value for agent in AgentType],
            "coordination_phases": [phase.value for phase in CoordinationPhase]
        })
        
        self.initialized = True
        
    def start_coordination_session(
        self,
        session_id: str,
        task_type: str,
        agents: List[str],
        complexity_score: float,
        constitutional_context: Dict[str, Any]
    ) -> None:
        """Start monitoring a coordination session"""
        if not SENTRY_AVAILABLE:
            return
            
        # Create transaction for the entire coordination session
        transaction = sentry_sdk.start_transaction(
            op="agent.coordination.session",
            name=f"{task_type}_coordination"
        )
        
        transaction.set_tag("session_id", session_id)
        transaction.set_tag("task_type", task_type)
        transaction.set_tag("agent_count", str(len(agents)))
        transaction.set_tag("complexity_score", str(complexity_score))
        transaction.set_tag("constitutional_hash", CONSTITUTIONAL_HASH)
        
        # Store session info
        self.active_coordination_sessions[session_id] = {
            "transaction": transaction,
            "start_time": time.time(),
            "task_type": task_type,
            "agents": agents,
            "complexity_score": complexity_score,
            "phase_timings": {},
            "consensus_attempts": 0,
            "conflicts_resolved": 0
        }
        
        # Add breadcrumb
        sentry_sdk.add_breadcrumb(
            message=f"Coordination session started: {task_type}",
            category="agent.coordination",
            level="info",
            data={
                "session_id": session_id,
                "agents": agents,
                "complexity": complexity_score,
                "constitutional_context": constitutional_context
            }
        )
        
    def track_coordination_phase(
        self,
        session_id: str,
        phase: CoordinationPhase,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Any]:
        """Track a specific phase of coordination"""
        if not SENTRY_AVAILABLE or session_id not in self.active_coordination_sessions:
            return None
            
        session = self.active_coordination_sessions[session_id]
        
        # Create span for phase
        span = sentry_sdk.start_span(
            op=f"agent.coordination.{phase.value}",
            name=phase.value
        )
        
        span.set_tag("phase", phase.value)
        span.set_tag("session_id", session_id)
        
        if metadata:
            for key, value in metadata.items():
                span.set_data(key, value)
                
        # Track phase timing
        phase_start = time.time()
        session["phase_timings"][phase.value] = {
            "start": phase_start,
            "span": span
        }
        
        return span
        
    def complete_coordination_phase(
        self,
        session_id: str,
        phase: CoordinationPhase,
        success: bool,
        results: Optional[Dict[str, Any]] = None
    ) -> None:
        """Complete a coordination phase and track metrics"""
        if not SENTRY_AVAILABLE or session_id not in self.active_coordination_sessions:
            return
            
        session = self.active_coordination_sessions[session_id]
        
        if phase.value in session["phase_timings"]:
            phase_data = session["phase_timings"][phase.value]
            phase_duration = time.time() - phase_data["start"]
            
            # Finish span
            if "span" in phase_data:
                span = phase_data["span"]
                span.set_data("duration_ms", phase_duration * 1000)
                span.set_data("success", success)
                
                if results:
                    span.set_data("results", results)
                    
                span.finish()
                
            # Check performance targets for critical phases
            if phase in [CoordinationPhase.CONSENSUS_BUILDING, CoordinationPhase.EXECUTION]:
                monitor_performance_target(
                    target_name=f"{phase.value}_duration",
                    target_value=5000,  # 5 second target for complex phases
                    actual_value=phase_duration * 1000,
                    unit="ms"
                )
                
    def track_agent_task(
        self,
        session_id: str,
        agent_type: AgentType,
        task_id: str,
        task_description: str
    ) -> None:
        """Track individual agent task execution"""
        if not SENTRY_AVAILABLE:
            return
            
        with sentry_sdk.start_span(
            op=f"agent.task.{agent_type.value}",
            name=task_description
        ) as span:
            span.set_tag("agent_type", agent_type.value)
            span.set_tag("task_id", task_id)
            span.set_tag("session_id", session_id)
            
            sentry_sdk.add_breadcrumb(
                message=f"{agent_type.value} agent executing: {task_description}",
                category="agent.task",
                level="info",
                data={
                    "agent": agent_type.value,
                    "task_id": task_id
                }
            )
            
    def track_consensus_attempt(
        self,
        session_id: str,
        consensus_algorithm: str,
        participants: List[str],
        consensus_achieved: bool,
        confidence_score: float,
        iterations: int
    ) -> None:
        """Track consensus building attempts"""
        if not SENTRY_AVAILABLE:
            return
            
        if session_id in self.active_coordination_sessions:
            self.active_coordination_sessions[session_id]["consensus_attempts"] += 1
            
        with sentry_sdk.start_span(
            op="agent.consensus",
            name=consensus_algorithm
        ) as span:
            span.set_tag("algorithm", consensus_algorithm)
            span.set_tag("consensus_achieved", str(consensus_achieved))
            span.set_data("participants", participants)
            span.set_data("confidence_score", confidence_score)
            span.set_data("iterations", iterations)
            
            # Alert on low consensus
            if self.alert_manager:
                AlertRules.check_multi_agent_consensus(
                    consensus_rate=confidence_score,
                    task_type=consensus_algorithm,
                    service_name=self.service_name
                )
                
            # Capture failed consensus as event
            if not consensus_achieved:
                capture_constitutional_event(
                    event_type="consensus_failure",
                    description=f"Failed to achieve consensus using {consensus_algorithm}",
                    metadata={
                        "participants": participants,
                        "confidence_score": confidence_score,
                        "iterations": iterations,
                        "session_id": session_id
                    },
                    level="warning"
                )
                
    def track_conflict_resolution(
        self,
        session_id: str,
        conflict_type: str,
        agents_in_conflict: List[str],
        resolution_method: str,
        resolved: bool,
        escalated_to_human: bool = False
    ) -> None:
        """Track conflict resolution between agents"""
        if not SENTRY_AVAILABLE:
            return
            
        if session_id in self.active_coordination_sessions and resolved:
            self.active_coordination_sessions[session_id]["conflicts_resolved"] += 1
            
        with sentry_sdk.start_span(
            op="agent.conflict_resolution",
            name=conflict_type
        ) as span:
            span.set_tag("conflict_type", conflict_type)
            span.set_tag("resolved", str(resolved))
            span.set_tag("escalated", str(escalated_to_human))
            span.set_data("agents_in_conflict", agents_in_conflict)
            span.set_data("resolution_method", resolution_method)
            
            # Alert on escalation
            if escalated_to_human:
                sentry_sdk.capture_message(
                    f"Agent conflict escalated to human: {conflict_type}",
                    level="warning",
                    tags={
                        "human_intervention_required": True,
                        "conflict_type": conflict_type,
                        "constitutional_hash": CONSTITUTIONAL_HASH
                    },
                    extra={
                        "agents_in_conflict": agents_in_conflict,
                        "session_id": session_id
                    }
                )
                
    def complete_coordination_session(
        self,
        session_id: str,
        success: bool,
        final_result: Optional[Dict[str, Any]] = None,
        constitutional_compliance_score: float = 1.0
    ) -> None:
        """Complete a coordination session and report metrics"""
        if not SENTRY_AVAILABLE or session_id not in self.active_coordination_sessions:
            return
            
        session = self.active_coordination_sessions[session_id]
        duration = time.time() - session["start_time"]
        
        # Set final transaction data
        transaction = session["transaction"]
        transaction.set_data("duration_seconds", duration)
        transaction.set_data("success", success)
        transaction.set_data("consensus_attempts", session["consensus_attempts"])
        transaction.set_data("conflicts_resolved", session["conflicts_resolved"])
        transaction.set_data("constitutional_compliance_score", constitutional_compliance_score)
        
        if final_result:
            transaction.set_data("result_summary", final_result)
            
        # Check constitutional compliance
        if self.alert_manager:
            AlertRules.check_constitutional_compliance(
                compliance_rate=constitutional_compliance_score,
                service_name=self.service_name
            )
            
        # Performance metrics
        monitor_performance_target(
            target_name="coordination_session_duration",
            target_value=30000,  # 30 second target for full session
            actual_value=duration * 1000,
            unit="ms"
        )
        
        # Capture session summary
        capture_constitutional_event(
            event_type="coordination_session_complete",
            description=f"Completed {session['task_type']} coordination",
            metadata={
                "session_id": session_id,
                "duration_seconds": duration,
                "success": success,
                "agents": session["agents"],
                "complexity_score": session["complexity_score"],
                "consensus_attempts": session["consensus_attempts"],
                "conflicts_resolved": session["conflicts_resolved"],
                "constitutional_compliance": constitutional_compliance_score
            },
            level="info" if success else "error"
        )
        
        # Finish transaction
        transaction.finish()
        
        # Clean up session
        del self.active_coordination_sessions[session_id]
        
    def report_agent_failure(
        self,
        agent_type: AgentType,
        failure_reason: str,
        task_context: Dict[str, Any],
        recovery_attempted: bool = False
    ) -> None:
        """Report agent failure with context"""
        if not SENTRY_AVAILABLE:
            return
            
        sentry_sdk.capture_message(
            f"Agent failure: {agent_type.value}",
            level="error",
            tags={
                "agent_failure": True,
                "agent_type": agent_type.value,
                "recovery_attempted": str(recovery_attempted),
                "constitutional_hash": CONSTITUTIONAL_HASH
            },
            extra={
                "failure_reason": failure_reason,
                "task_context": task_context,
                "service": self.service_name
            }
        )
        
        # Trigger alert if critical agent
        if agent_type in [AgentType.ORCHESTRATOR, AgentType.ETHICS]:
            if self.alert_manager:
                self.alert_manager.trigger_agent_coordination_failure(
                    agents_involved=[agent_type.value],
                    task_type=task_context.get("task_type", "unknown"),
                    failure_reason=failure_reason,
                    consensus_score=None
                )


# Global monitor instance
agent_monitor = MultiAgentSentryMonitor()


# Convenience decorators
def monitor_agent_task(agent_type: AgentType, task_description: str):
    """Decorator to monitor agent task execution"""
    def decorator(func):
        @track_agent_coordination(agent_type.value, task_description)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def monitor_consensus(algorithm: str):
    """Decorator to monitor consensus building"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                
                # Track consensus attempt
                if hasattr(result, "consensus_achieved"):
                    agent_monitor.track_consensus_attempt(
                        session_id=kwargs.get("session_id", "unknown"),
                        consensus_algorithm=algorithm,
                        participants=kwargs.get("participants", []),
                        consensus_achieved=result.consensus_achieved,
                        confidence_score=getattr(result, "confidence_score", 0.0),
                        iterations=getattr(result, "iterations", 1)
                    )
                    
                return result
                
            except Exception as e:
                sentry_sdk.capture_exception(e)
                raise
                
        return wrapper
    return decorator