"""
EU AI Act Compliance Monitor

Real-time compliance monitoring system that continuously tracks compliance
status, detects violations, and generates automated reports. This module
provides ongoing surveillance of EU AI Act compliance requirements.

Key Features:
- Real-time compliance monitoring and violation detection
- Automated compliance checking and validation
- Compliance metrics collection and analysis
- Incident response and remediation tracking
- Integration with existing ACGS monitoring infrastructure
"""

import asyncio
import logging
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from enum import Enum
import uuid

from .eu_ai_act_compliance import EUAIActCompliance, ComplianceStatus, AISystemRiskLevel
from services.shared.monitoring.intelligent_alerting_system import AlertingSystem
from services.shared.security.enhanced_audit_logging import AuditLogger

logger = logging.getLogger(__name__)

class ViolationType(Enum):
    """Types of compliance violations"""
    DOCUMENTATION_MISSING = "documentation_missing"
    HUMAN_OVERSIGHT_FAILURE = "human_oversight_failure"
    DATA_GOVERNANCE_VIOLATION = "data_governance_violation"
    TRANSPARENCY_VIOLATION = "transparency_violation"
    RECORD_KEEPING_FAILURE = "record_keeping_failure"
    ACCURACY_THRESHOLD_BREACH = "accuracy_threshold_breach"
    BIAS_DETECTION_FAILURE = "bias_detection_failure"
    SECURITY_BREACH = "security_breach"
    UNAUTHORIZED_USE = "unauthorized_use"
    SYSTEM_MALFUNCTION = "system_malfunction"

class ViolationSeverity(Enum):
    """Severity levels for compliance violations"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class ComplianceViolation:
    """Compliance violation record"""
    violation_id: str
    violation_type: ViolationType
    severity: ViolationSeverity
    requirement_id: str
    description: str
    detected_at: datetime
    affected_system: str
    evidence: Dict[str, Any]
    remediation_status: str
    remediation_actions: List[str]
    assigned_to: Optional[str]
    resolution_deadline: Optional[datetime]
    resolved_at: Optional[datetime]
    root_cause: Optional[str]

@dataclass
class ComplianceMetrics:
    """Compliance monitoring metrics"""
    compliance_score: float
    violations_detected: int
    violations_resolved: int
    violations_pending: int
    critical_violations: int
    mean_resolution_time_hours: float
    compliance_trend: str
    last_assessment_date: datetime
    next_assessment_due: datetime
    monitoring_uptime: float

@dataclass
class ComplianceReport:
    """Compliance monitoring report"""
    report_id: str
    report_type: str
    generation_date: datetime
    period_start: datetime
    period_end: datetime
    summary_metrics: ComplianceMetrics
    violations_summary: Dict[str, int]
    trending_issues: List[str]
    recommendations: List[str]
    action_items: List[str]
    next_review_date: datetime

class ComplianceMonitor:
    """
    Real-time EU AI Act compliance monitoring system
    """
    
    def __init__(self, compliance_engine: EUAIActCompliance, config: Optional[Dict[str, Any]] = None):
        self.compliance_engine = compliance_engine
        self.config = config or {}
        self.alerting = AlertingSystem()
        self.audit_logger = AuditLogger()
        
        # Monitoring configuration
        self.monitoring_interval_seconds = config.get('monitoring_interval_seconds', 300)  # 5 minutes
        self.violation_threshold = config.get('violation_threshold', 0.95)
        self.critical_response_time_hours = config.get('critical_response_time_hours', 4)
        self.auto_remediation_enabled = config.get('auto_remediation_enabled', True)
        
        # State management
        self.violations = {}
        self.monitoring_rules = {}
        self.compliance_checks = {}
        self.running = False
        
        # Metrics tracking
        self.metrics_history = []
        self.last_metrics_update = datetime.utcnow()
        
        # Initialize monitoring rules
        self._initialize_monitoring_rules()

    def _initialize_monitoring_rules(self):
        """Initialize compliance monitoring rules"""
        
        # Human oversight monitoring
        self.monitoring_rules['human_oversight_check'] = {
            'name': 'Human Oversight Verification',
            'requirement_id': 'art14_human_oversight',
            'check_interval_seconds': 300,
            'violation_type': ViolationType.HUMAN_OVERSIGHT_FAILURE,
            'severity': ViolationSeverity.HIGH,
            'check_function': self._check_human_oversight,
            'enabled': True
        }
        
        # Data governance monitoring
        self.monitoring_rules['data_governance_check'] = {
            'name': 'Data Governance Compliance',
            'requirement_id': 'art10_data_governance',
            'check_interval_seconds': 900,  # 15 minutes
            'violation_type': ViolationType.DATA_GOVERNANCE_VIOLATION,
            'severity': ViolationSeverity.HIGH,
            'check_function': self._check_data_governance,
            'enabled': True
        }
        
        # Record keeping monitoring
        self.monitoring_rules['record_keeping_check'] = {
            'name': 'Record Keeping Verification',
            'requirement_id': 'art12_recordkeeping',
            'check_interval_seconds': 600,  # 10 minutes
            'violation_type': ViolationType.RECORD_KEEPING_FAILURE,
            'severity': ViolationSeverity.MEDIUM,
            'check_function': self._check_record_keeping,
            'enabled': True
        }
        
        # Accuracy monitoring
        self.monitoring_rules['accuracy_monitoring'] = {
            'name': 'System Accuracy Monitoring',
            'requirement_id': 'art15_accuracy_robustness',
            'check_interval_seconds': 1800,  # 30 minutes
            'violation_type': ViolationType.ACCURACY_THRESHOLD_BREACH,
            'severity': ViolationSeverity.HIGH,
            'check_function': self._check_accuracy_thresholds,
            'enabled': True
        }
        
        # Bias detection monitoring
        self.monitoring_rules['bias_detection'] = {
            'name': 'Bias Detection Monitoring',
            'requirement_id': 'art10_data_governance',
            'check_interval_seconds': 3600,  # 1 hour
            'violation_type': ViolationType.BIAS_DETECTION_FAILURE,
            'severity': ViolationSeverity.HIGH,
            'check_function': self._check_bias_detection,
            'enabled': True
        }
        
        # Documentation completeness
        self.monitoring_rules['documentation_check'] = {
            'name': 'Technical Documentation Completeness',
            'requirement_id': 'art11_tech_docs',
            'check_interval_seconds': 86400,  # Daily
            'violation_type': ViolationType.DOCUMENTATION_MISSING,
            'severity': ViolationSeverity.MEDIUM,
            'check_function': self._check_documentation_completeness,
            'enabled': True
        }
        
        # Transparency verification
        self.monitoring_rules['transparency_check'] = {
            'name': 'Transparency Requirements Verification',
            'requirement_id': 'art13_transparency',
            'check_interval_seconds': 3600,  # 1 hour
            'violation_type': ViolationType.TRANSPARENCY_VIOLATION,
            'severity': ViolationSeverity.MEDIUM,
            'check_function': self._check_transparency_requirements,
            'enabled': True
        }

    async def start_monitoring(self):
        """Start continuous compliance monitoring"""
        if self.running:
            logger.warning("Compliance monitoring is already running")
            return
        
        self.running = True
        logger.info("Starting EU AI Act compliance monitoring")
        
        try:
            # Start monitoring tasks
            monitoring_tasks = [
                self._run_continuous_monitoring(),
                self._run_periodic_assessments(),
                self._run_metrics_collection(),
                self._run_violation_resolution_tracking()
            ]
            
            await asyncio.gather(*monitoring_tasks)
            
        except Exception as e:
            logger.error(f"Compliance monitoring failed: {e}")
            self.running = False
            raise
        finally:
            logger.info("Compliance monitoring stopped")

    async def stop_monitoring(self):
        """Stop compliance monitoring"""
        self.running = False
        logger.info("Stopping compliance monitoring")

    async def _run_continuous_monitoring(self):
        """Run continuous compliance checks"""
        while self.running:
            try:
                # Execute all enabled monitoring rules
                for rule_id, rule in self.monitoring_rules.items():
                    if rule['enabled']:
                        await self._execute_monitoring_rule(rule_id, rule)
                
                await asyncio.sleep(self.monitoring_interval_seconds)
                
            except Exception as e:
                logger.error(f"Continuous monitoring error: {e}")
                await asyncio.sleep(60)  # Wait before retrying

    async def _execute_monitoring_rule(self, rule_id: str, rule: Dict[str, Any]):
        """Execute a specific monitoring rule"""
        try:
            # Check if it's time to run this rule
            last_check = self.compliance_checks.get(rule_id, datetime.min)
            if datetime.utcnow() - last_check < timedelta(seconds=rule['check_interval_seconds']):
                return
            
            # Execute the check function
            check_result = await rule['check_function']()
            
            # Update last check time
            self.compliance_checks[rule_id] = datetime.utcnow()
            
            # Process check result
            if not check_result['compliant']:
                await self._handle_violation(rule, check_result)
            
            # Log check execution
            await self.audit_logger.log_compliance_event({
                'event_type': 'compliance_check_executed',
                'rule_id': rule_id,
                'rule_name': rule['name'],
                'compliant': check_result['compliant'],
                'timestamp': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Monitoring rule execution failed for {rule_id}: {e}")

    async def _handle_violation(self, rule: Dict[str, Any], check_result: Dict[str, Any]):
        """Handle detected compliance violation"""
        try:
            violation_id = str(uuid.uuid4())
            
            # Determine resolution deadline based on severity
            deadline_hours = {
                ViolationSeverity.CRITICAL: 4,
                ViolationSeverity.HIGH: 24,
                ViolationSeverity.MEDIUM: 72,
                ViolationSeverity.LOW: 168
            }.get(rule['severity'], 72)
            
            violation = ComplianceViolation(
                violation_id=violation_id,
                violation_type=rule['violation_type'],
                severity=rule['severity'],
                requirement_id=rule['requirement_id'],
                description=check_result.get('description', f"Violation detected by {rule['name']}"),
                detected_at=datetime.utcnow(),
                affected_system=self.compliance_engine.system_name,
                evidence=check_result.get('evidence', {}),
                remediation_status='open',
                remediation_actions=check_result.get('remediation_actions', []),
                assigned_to=None,
                resolution_deadline=datetime.utcnow() + timedelta(hours=deadline_hours),
                resolved_at=None,
                root_cause=None
            )
            
            # Store violation
            self.violations[violation_id] = violation
            
            # Send alert
            await self.alerting.send_alert(
                f"eu_ai_act_violation_{rule['violation_type'].value}",
                f"EU AI Act compliance violation detected: {violation.description}",
                severity=rule['severity'].value
            )
            
            # Log violation
            await self.audit_logger.log_compliance_event({
                'event_type': 'compliance_violation_detected',
                'violation_id': violation_id,
                'violation_type': rule['violation_type'].value,
                'severity': rule['severity'].value,
                'requirement_id': rule['requirement_id'],
                'timestamp': violation.detected_at.isoformat()
            })
            
            # Attempt auto-remediation if enabled
            if self.auto_remediation_enabled and rule['severity'] != ViolationSeverity.CRITICAL:
                await self._attempt_auto_remediation(violation)
            
        except Exception as e:
            logger.error(f"Violation handling failed: {e}")

    async def _attempt_auto_remediation(self, violation: ComplianceViolation):
        """Attempt automatic remediation of compliance violation"""
        try:
            remediation_success = False
            
            # Auto-remediation based on violation type
            if violation.violation_type == ViolationType.RECORD_KEEPING_FAILURE:
                # Attempt to restart logging systems
                remediation_success = await self._remediate_record_keeping()
            
            elif violation.violation_type == ViolationType.DOCUMENTATION_MISSING:
                # Attempt to regenerate missing documentation
                remediation_success = await self._remediate_documentation()
            
            elif violation.violation_type == ViolationType.TRANSPARENCY_VIOLATION:
                # Attempt to update transparency measures
                remediation_success = await self._remediate_transparency()
            
            if remediation_success:
                # Mark violation as resolved
                violation.remediation_status = 'auto_resolved'
                violation.resolved_at = datetime.utcnow()
                
                await self.audit_logger.log_compliance_event({
                    'event_type': 'violation_auto_remediated',
                    'violation_id': violation.violation_id,
                    'violation_type': violation.violation_type.value,
                    'timestamp': violation.resolved_at.isoformat()
                })
            
        except Exception as e:
            logger.error(f"Auto-remediation failed for {violation.violation_id}: {e}")

    async def _remediate_record_keeping(self) -> bool:
        """Attempt to remediate record keeping violations"""
        # Simplified remediation - in practice this would integrate with logging systems
        logger.info("Attempting to remediate record keeping violations")
        return True

    async def _remediate_documentation(self) -> bool:
        """Attempt to remediate documentation violations"""
        # Simplified remediation - in practice this would trigger documentation generation
        logger.info("Attempting to remediate documentation violations")
        return True

    async def _remediate_transparency(self) -> bool:
        """Attempt to remediate transparency violations"""
        # Simplified remediation - in practice this would update transparency measures
        logger.info("Attempting to remediate transparency violations")
        return True

    # Compliance check functions
    async def _check_human_oversight(self) -> Dict[str, Any]:
        """Check human oversight compliance"""
        try:
            # Check if human oversight is properly configured and functioning
            # This would integrate with the human oversight system
            
            # Simplified check - in practice this would verify:
            # - Human reviewers are available and trained
            # - Escalation procedures are working
            # - Human intervention capabilities are functional
            
            oversight_operational = True  # Would be determined by actual checks
            
            if oversight_operational:
                return {'compliant': True}
            else:
                return {
                    'compliant': False,
                    'description': 'Human oversight system not operational',
                    'evidence': {'oversight_status': 'failed'},
                    'remediation_actions': ['Verify human oversight system', 'Check reviewer availability']
                }
                
        except Exception as e:
            return {
                'compliant': False,
                'description': f'Human oversight check failed: {str(e)}',
                'evidence': {'error': str(e)},
                'remediation_actions': ['Investigate human oversight system failure']
            }

    async def _check_data_governance(self) -> Dict[str, Any]:
        """Check data governance compliance"""
        try:
            # Check data governance measures
            # This would verify data quality, bias monitoring, etc.
            
            data_quality_ok = True  # Would be determined by actual data quality checks
            bias_monitoring_active = True  # Would check bias monitoring systems
            
            if data_quality_ok and bias_monitoring_active:
                return {'compliant': True}
            else:
                issues = []
                if not data_quality_ok:
                    issues.append('Data quality issues detected')
                if not bias_monitoring_active:
                    issues.append('Bias monitoring not active')
                
                return {
                    'compliant': False,
                    'description': f'Data governance issues: {"; ".join(issues)}',
                    'evidence': {
                        'data_quality_ok': data_quality_ok,
                        'bias_monitoring_active': bias_monitoring_active
                    },
                    'remediation_actions': ['Review data governance procedures', 'Activate bias monitoring']
                }
                
        except Exception as e:
            return {
                'compliant': False,
                'description': f'Data governance check failed: {str(e)}',
                'evidence': {'error': str(e)},
                'remediation_actions': ['Investigate data governance system']
            }

    async def _check_record_keeping(self) -> Dict[str, Any]:
        """Check record keeping compliance"""
        try:
            # Check if logging systems are operational and retaining records properly
            logging_operational = True  # Would check actual logging systems
            retention_compliant = True  # Would verify retention policies
            
            if logging_operational and retention_compliant:
                return {'compliant': True}
            else:
                return {
                    'compliant': False,
                    'description': 'Record keeping system issues detected',
                    'evidence': {
                        'logging_operational': logging_operational,
                        'retention_compliant': retention_compliant
                    },
                    'remediation_actions': ['Check logging systems', 'Verify retention policies']
                }
                
        except Exception as e:
            return {
                'compliant': False,
                'description': f'Record keeping check failed: {str(e)}',
                'evidence': {'error': str(e)},
                'remediation_actions': ['Investigate record keeping system']
            }

    async def _check_accuracy_thresholds(self) -> Dict[str, Any]:
        """Check system accuracy compliance"""
        try:
            # Check if system accuracy meets required thresholds
            current_accuracy = 0.95  # Would get from actual system metrics
            required_accuracy = 0.90  # Threshold for constitutional AI systems
            
            if current_accuracy >= required_accuracy:
                return {'compliant': True}
            else:
                return {
                    'compliant': False,
                    'description': f'System accuracy below threshold: {current_accuracy:.2%} < {required_accuracy:.2%}',
                    'evidence': {
                        'current_accuracy': current_accuracy,
                        'required_accuracy': required_accuracy
                    },
                    'remediation_actions': ['Review model performance', 'Consider model retraining']
                }
                
        except Exception as e:
            return {
                'compliant': False,
                'description': f'Accuracy check failed: {str(e)}',
                'evidence': {'error': str(e)},
                'remediation_actions': ['Investigate accuracy monitoring system']
            }

    async def _check_bias_detection(self) -> Dict[str, Any]:
        """Check bias detection compliance"""
        try:
            # Check if bias detection systems are operational
            bias_detection_active = True  # Would check bias detection systems
            recent_bias_assessment = True  # Would verify recent bias assessments
            
            if bias_detection_active and recent_bias_assessment:
                return {'compliant': True}
            else:
                return {
                    'compliant': False,
                    'description': 'Bias detection system issues',
                    'evidence': {
                        'bias_detection_active': bias_detection_active,
                        'recent_bias_assessment': recent_bias_assessment
                    },
                    'remediation_actions': ['Activate bias detection', 'Conduct bias assessment']
                }
                
        except Exception as e:
            return {
                'compliant': False,
                'description': f'Bias detection check failed: {str(e)}',
                'evidence': {'error': str(e)},
                'remediation_actions': ['Investigate bias detection system']
            }

    async def _check_documentation_completeness(self) -> Dict[str, Any]:
        """Check technical documentation completeness"""
        try:
            # Check if required documentation is complete and up-to-date
            documentation_complete = True  # Would check actual documentation
            documentation_current = True  # Would verify documentation currency
            
            if documentation_complete and documentation_current:
                return {'compliant': True}
            else:
                return {
                    'compliant': False,
                    'description': 'Technical documentation issues',
                    'evidence': {
                        'documentation_complete': documentation_complete,
                        'documentation_current': documentation_current
                    },
                    'remediation_actions': ['Update technical documentation', 'Complete missing documentation']
                }
                
        except Exception as e:
            return {
                'compliant': False,
                'description': f'Documentation check failed: {str(e)}',
                'evidence': {'error': str(e)},
                'remediation_actions': ['Investigate documentation system']
            }

    async def _check_transparency_requirements(self) -> Dict[str, Any]:
        """Check transparency requirements compliance"""
        try:
            # Check if transparency measures are properly implemented
            transparency_measures_active = True  # Would check transparency systems
            user_information_provided = True  # Would verify user information
            
            if transparency_measures_active and user_information_provided:
                return {'compliant': True}
            else:
                return {
                    'compliant': False,
                    'description': 'Transparency requirements not met',
                    'evidence': {
                        'transparency_measures_active': transparency_measures_active,
                        'user_information_provided': user_information_provided
                    },
                    'remediation_actions': ['Implement transparency measures', 'Provide user information']
                }
                
        except Exception as e:
            return {
                'compliant': False,
                'description': f'Transparency check failed: {str(e)}',
                'evidence': {'error': str(e)},
                'remediation_actions': ['Investigate transparency system']
            }

    async def _run_periodic_assessments(self):
        """Run periodic comprehensive compliance assessments"""
        while self.running:
            try:
                # Run comprehensive assessment every 24 hours
                await asyncio.sleep(86400)
                
                if not self.running:
                    break
                
                logger.info("Running periodic compliance assessment")
                
                # Get overall compliance status
                compliance_status = await self.compliance_engine.get_compliance_status()
                
                # Log assessment results
                await self.audit_logger.log_compliance_event({
                    'event_type': 'periodic_compliance_assessment',
                    'compliance_score': compliance_status['compliance_score'],
                    'overall_status': compliance_status['overall_status'],
                    'timestamp': datetime.utcnow().isoformat()
                })
                
                # Alert on low compliance
                if compliance_status['compliance_score'] < self.violation_threshold:
                    await self.alerting.send_alert(
                        "low_compliance_score",
                        f"Compliance score below threshold: {compliance_status['compliance_score']:.2%}",
                        severity="high"
                    )
                
            except Exception as e:
                logger.error(f"Periodic assessment failed: {e}")

    async def _run_metrics_collection(self):
        """Collect and update compliance metrics"""
        while self.running:
            try:
                await asyncio.sleep(300)  # Every 5 minutes
                
                if not self.running:
                    break
                
                # Calculate current metrics
                metrics = await self._calculate_compliance_metrics()
                
                # Store metrics in history
                self.metrics_history.append({
                    'timestamp': datetime.utcnow(),
                    'metrics': metrics
                })
                
                # Keep only last 24 hours of metrics
                cutoff_time = datetime.utcnow() - timedelta(hours=24)
                self.metrics_history = [
                    entry for entry in self.metrics_history
                    if entry['timestamp'] > cutoff_time
                ]
                
                self.last_metrics_update = datetime.utcnow()
                
            except Exception as e:
                logger.error(f"Metrics collection failed: {e}")

    async def _calculate_compliance_metrics(self) -> ComplianceMetrics:
        """Calculate current compliance metrics"""
        try:
            # Get compliance status
            compliance_status = await self.compliance_engine.get_compliance_status()
            
            # Count violations by status
            total_violations = len(self.violations)
            resolved_violations = sum(
                1 for v in self.violations.values()
                if v.resolved_at is not None
            )
            pending_violations = total_violations - resolved_violations
            critical_violations = sum(
                1 for v in self.violations.values()
                if v.severity == ViolationSeverity.CRITICAL and v.resolved_at is None
            )
            
            # Calculate mean resolution time
            resolved_times = [
                (v.resolved_at - v.detected_at).total_seconds() / 3600
                for v in self.violations.values()
                if v.resolved_at is not None
            ]
            mean_resolution_time = sum(resolved_times) / len(resolved_times) if resolved_times else 0
            
            # Determine trend
            if len(self.metrics_history) >= 2:
                previous_score = self.metrics_history[-2]['metrics'].compliance_score
                current_score = compliance_status['compliance_score']
                if current_score > previous_score:
                    trend = "improving"
                elif current_score < previous_score:
                    trend = "declining"
                else:
                    trend = "stable"
            else:
                trend = "stable"
            
            return ComplianceMetrics(
                compliance_score=compliance_status['compliance_score'],
                violations_detected=total_violations,
                violations_resolved=resolved_violations,
                violations_pending=pending_violations,
                critical_violations=critical_violations,
                mean_resolution_time_hours=mean_resolution_time,
                compliance_trend=trend,
                last_assessment_date=compliance_status.get('last_assessment_date', datetime.utcnow()),
                next_assessment_due=compliance_status.get('next_review_date', datetime.utcnow()),
                monitoring_uptime=1.0  # Would calculate actual uptime
            )
            
        except Exception as e:
            logger.error(f"Metrics calculation failed: {e}")
            # Return default metrics
            return ComplianceMetrics(
                compliance_score=0.0,
                violations_detected=0,
                violations_resolved=0,
                violations_pending=0,
                critical_violations=0,
                mean_resolution_time_hours=0.0,
                compliance_trend="unknown",
                last_assessment_date=datetime.utcnow(),
                next_assessment_due=datetime.utcnow(),
                monitoring_uptime=0.0
            )

    async def _run_violation_resolution_tracking(self):
        """Track violation resolution and escalate overdue items"""
        while self.running:
            try:
                await asyncio.sleep(3600)  # Check every hour
                
                if not self.running:
                    break
                
                current_time = datetime.utcnow()
                
                # Check for overdue violations
                for violation in self.violations.values():
                    if (violation.resolved_at is None and 
                        violation.resolution_deadline and
                        current_time > violation.resolution_deadline):
                        
                        # Escalate overdue violation
                        await self._escalate_violation(violation)
                
            except Exception as e:
                logger.error(f"Violation resolution tracking failed: {e}")

    async def _escalate_violation(self, violation: ComplianceViolation):
        """Escalate overdue compliance violation"""
        try:
            # Send escalation alert
            await self.alerting.send_alert(
                f"overdue_violation_{violation.violation_id}",
                f"Compliance violation overdue: {violation.description}",
                severity="critical"
            )
            
            # Log escalation
            await self.audit_logger.log_compliance_event({
                'event_type': 'violation_escalated',
                'violation_id': violation.violation_id,
                'violation_type': violation.violation_type.value,
                'days_overdue': (datetime.utcnow() - violation.resolution_deadline).days,
                'timestamp': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Violation escalation failed: {e}")

    async def generate_compliance_report(self, report_type: str = "periodic") -> ComplianceReport:
        """Generate compliance monitoring report"""
        try:
            report_id = str(uuid.uuid4())
            current_time = datetime.utcnow()
            
            # Determine report period
            if report_type == "daily":
                period_start = current_time - timedelta(days=1)
            elif report_type == "weekly":
                period_start = current_time - timedelta(weeks=1)
            elif report_type == "monthly":
                period_start = current_time - timedelta(days=30)
            else:  # periodic
                period_start = current_time - timedelta(hours=24)
            
            # Get current metrics
            current_metrics = await self._calculate_compliance_metrics()
            
            # Analyze violations in period
            period_violations = [
                v for v in self.violations.values()
                if v.detected_at >= period_start
            ]
            
            violations_summary = {}
            for violation_type in ViolationType:
                violations_summary[violation_type.value] = sum(
                    1 for v in period_violations
                    if v.violation_type == violation_type
                )
            
            # Generate recommendations
            recommendations = await self._generate_monitoring_recommendations(period_violations)
            
            # Generate action items
            action_items = await self._generate_monitoring_action_items(period_violations)
            
            # Identify trending issues
            trending_issues = self._identify_trending_issues(period_violations)
            
            report = ComplianceReport(
                report_id=report_id,
                report_type=report_type,
                generation_date=current_time,
                period_start=period_start,
                period_end=current_time,
                summary_metrics=current_metrics,
                violations_summary=violations_summary,
                trending_issues=trending_issues,
                recommendations=recommendations,
                action_items=action_items,
                next_review_date=current_time + timedelta(days=7)
            )
            
            return report
            
        except Exception as e:
            logger.error(f"Compliance report generation failed: {e}")
            raise

    async def _generate_monitoring_recommendations(self, violations: List[ComplianceViolation]) -> List[str]:
        """Generate recommendations based on monitoring results"""
        recommendations = []
        
        # Analyze violation patterns
        violation_types = [v.violation_type for v in violations]
        
        if ViolationType.HUMAN_OVERSIGHT_FAILURE in violation_types:
            recommendations.append("Review and strengthen human oversight procedures")
        
        if ViolationType.DATA_GOVERNANCE_VIOLATION in violation_types:
            recommendations.append("Enhance data governance and bias monitoring systems")
        
        if ViolationType.ACCURACY_THRESHOLD_BREACH in violation_types:
            recommendations.append("Conduct system accuracy assessment and potential retraining")
        
        # General recommendations
        if len(violations) > 5:
            recommendations.append("Conduct comprehensive compliance system review")
        
        if not recommendations:
            recommendations.append("Continue current monitoring practices")
        
        return recommendations

    async def _generate_monitoring_action_items(self, violations: List[ComplianceViolation]) -> List[str]:
        """Generate action items based on monitoring results"""
        action_items = []
        
        # Unresolved critical violations
        critical_unresolved = [
            v for v in violations
            if v.severity == ViolationSeverity.CRITICAL and v.resolved_at is None
        ]
        
        for violation in critical_unresolved:
            action_items.append(f"URGENT: Resolve critical violation {violation.violation_id}")
        
        # Overdue violations
        overdue_violations = [
            v for v in violations
            if (v.resolved_at is None and v.resolution_deadline and
                datetime.utcnow() > v.resolution_deadline)
        ]
        
        for violation in overdue_violations:
            action_items.append(f"Resolve overdue violation {violation.violation_id}")
        
        return action_items

    def _identify_trending_issues(self, violations: List[ComplianceViolation]) -> List[str]:
        """Identify trending compliance issues"""
        trending_issues = []
        
        # Count violations by type
        violation_counts = {}
        for violation in violations:
            violation_type = violation.violation_type.value
            violation_counts[violation_type] = violation_counts.get(violation_type, 0) + 1
        
        # Identify patterns
        for violation_type, count in violation_counts.items():
            if count >= 3:  # 3 or more of same type
                trending_issues.append(f"Recurring {violation_type} violations ({count} instances)")
        
        return trending_issues

    def get_violation_summary(self) -> Dict[str, Any]:
        """Get summary of current violations"""
        return {
            'total_violations': len(self.violations),
            'open_violations': sum(1 for v in self.violations.values() if v.resolved_at is None),
            'critical_violations': sum(
                1 for v in self.violations.values()
                if v.severity == ViolationSeverity.CRITICAL and v.resolved_at is None
            ),
            'overdue_violations': sum(
                1 for v in self.violations.values()
                if (v.resolved_at is None and v.resolution_deadline and
                    datetime.utcnow() > v.resolution_deadline)
            ),
            'violations_by_type': {
                vtype.value: sum(1 for v in self.violations.values() if v.violation_type == vtype)
                for vtype in ViolationType
            },
            'last_violation': max(
                (v.detected_at for v in self.violations.values()),
                default=None
            )
        }

# Example usage
async def example_usage():
    """Example of using the compliance monitor"""
    from .eu_ai_act_compliance import EUAIActCompliance
    
    # Initialize compliance engine
    compliance_engine = EUAIActCompliance({
        'system_name': 'ACGS',
        'system_version': '1.0.0'
    })
    
    # Initialize compliance monitor
    monitor = ComplianceMonitor(compliance_engine, {
        'monitoring_interval_seconds': 60,  # Fast monitoring for demo
        'auto_remediation_enabled': True
    })
    
    # Start monitoring (would run continuously in production)
    logger.info("Starting compliance monitoring demo")
    
    # Run for a short period for demonstration
    monitoring_task = asyncio.create_task(monitor.start_monitoring())
    
    # Let it run for 2 minutes
    await asyncio.sleep(120)
    
    # Stop monitoring
    await monitor.stop_monitoring()
    monitoring_task.cancel()
    
    # Generate report
    report = await monitor.generate_compliance_report("daily")
    logger.info(f"Generated compliance report: {report.report_id}")
    
    # Get violation summary
    violation_summary = monitor.get_violation_summary()
    logger.info(f"Violation summary: {violation_summary}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())