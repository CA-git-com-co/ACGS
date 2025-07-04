"""
Enhanced Audit Logging System for ACGS

This module provides comprehensive audit logging with real-time monitoring,
compliance tracking, and constitutional governance validation.
"""

import asyncio
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Set
from enum import Enum
from dataclasses import dataclass, field, asdict
from abc import ABC, abstractmethod
import gzip
import os

import structlog
from pydantic import BaseModel

logger = structlog.get_logger(__name__)

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class AuditEventType(Enum):
    """Types of audit events."""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    POLICY_CHANGE = "policy_change"
    CONSTITUTIONAL_CHANGE = "constitutional_change"
    GOVERNANCE_DECISION = "governance_decision"
    SECURITY_INCIDENT = "security_incident"
    SYSTEM_CONFIGURATION = "system_configuration"
    USER_MANAGEMENT = "user_management"
    API_ACCESS = "api_access"
    VOTING_EVENT = "voting_event"
    SYNTHESIS_EVENT = "synthesis_event"
    VERIFICATION_EVENT = "verification_event"
    ESCALATION_EVENT = "escalation_event"


class AuditLevel(Enum):
    """Audit logging levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    CONSTITUTIONAL = "constitutional"  # Highest level for constitutional events


class ComplianceFramework(Enum):
    """Supported compliance frameworks."""
    SOC2 = "soc2"
    GDPR = "gdpr"
    ISO27001 = "iso27001"
    NIST = "nist"
    CONSTITUTIONAL_AI = "constitutional_ai"
    CUSTOM = "custom"


@dataclass
class AuditEvent:
    """Comprehensive audit event record."""
    event_id: str
    event_type: AuditEventType
    level: AuditLevel
    timestamp: datetime
    user_id: Optional[str]
    session_id: Optional[str]
    source_ip: Optional[str]
    user_agent: Optional[str]
    resource_type: Optional[str]
    resource_id: Optional[str]
    action: str
    outcome: str  # success, failure, partial
    details: Dict[str, Any] = field(default_factory=dict)
    sensitive_data_hash: Optional[str] = None
    compliance_tags: Set[ComplianceFramework] = field(default_factory=set)
    constitutional_hash: str = CONSTITUTIONAL_HASH
    service_name: Optional[str] = None
    request_duration_ms: Optional[float] = None
    error_message: Optional[str] = None
    risk_score: float = 0.0
    correlation_id: Optional[str] = None


@dataclass
class AuditMetrics:
    """Audit logging metrics."""
    total_events: int = 0
    events_by_type: Dict[str, int] = field(default_factory=dict)
    events_by_level: Dict[str, int] = field(default_factory=dict)
    failed_events: int = 0
    high_risk_events: int = 0
    constitutional_events: int = 0
    compliance_violations: int = 0
    last_reset: datetime = field(default_factory=datetime.now)


class AuditStorage(ABC):
    """Abstract base class for audit storage backends."""
    
    @abstractmethod
    async def store_event(self, event: AuditEvent) -> bool:
        """Store an audit event."""
        pass
    
    @abstractmethod
    async def query_events(
        self,
        start_time: datetime,
        end_time: datetime,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[AuditEvent]:
        """Query audit events."""
        pass
    
    @abstractmethod
    async def get_metrics(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> AuditMetrics:
        """Get audit metrics for a time period."""
        pass


class FileAuditStorage(AuditStorage):
    """File-based audit storage with compression and rotation."""
    
    def __init__(
        self,
        base_path: str = "/var/log/acgs/audit",
        max_file_size_mb: int = 100,
        compression_enabled: bool = True,
        retention_days: int = 2555  # ~7 years
    ):
        self.base_path = base_path
        self.max_file_size = max_file_size_mb * 1024 * 1024
        self.compression_enabled = compression_enabled
        self.retention_days = retention_days
        self.current_file_path = None
        self.current_file_size = 0
        
        # Ensure directory exists
        os.makedirs(base_path, exist_ok=True)
    
    async def store_event(self, event: AuditEvent) -> bool:
        """Store audit event to file."""
        try:
            # Serialize event
            event_dict = asdict(event)
            event_dict['timestamp'] = event.timestamp.isoformat()
            event_dict['compliance_tags'] = [tag.value for tag in event.compliance_tags]
            event_line = json.dumps(event_dict) + '\n'
            
            # Check if we need a new file
            if self._needs_new_file():
                await self._rotate_file()
            
            # Write to current file
            file_path = self._get_current_file_path()
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(event_line)
                self.current_file_size += len(event_line.encode('utf-8'))
            
            # Cleanup old files
            await self._cleanup_old_files()
            
            return True
            
        except Exception as e:
            logger.error(
                "Failed to store audit event to file",
                event_id=event.event_id,
                error=str(e)
            )
            return False
    
    async def query_events(
        self,
        start_time: datetime,
        end_time: datetime,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[AuditEvent]:
        """Query events from files."""
        events = []
        filters = filters or {}
        
        try:
            # Get relevant files
            files = self._get_files_for_time_range(start_time, end_time)
            
            for file_path in files:
                if file_path.endswith('.gz'):
                    with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                        events.extend(self._parse_events_from_file(f, start_time, end_time, filters))
                else:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        events.extend(self._parse_events_from_file(f, start_time, end_time, filters))
        
        except Exception as e:
            logger.error(
                "Failed to query audit events from files",
                error=str(e)
            )
        
        return events
    
    async def get_metrics(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> AuditMetrics:
        """Calculate metrics from stored events."""
        events = await self.query_events(start_time, end_time)
        
        metrics = AuditMetrics()
        metrics.total_events = len(events)
        
        for event in events:
            # Count by type
            event_type = event.event_type.value
            metrics.events_by_type[event_type] = metrics.events_by_type.get(event_type, 0) + 1
            
            # Count by level
            level = event.level.value
            metrics.events_by_level[level] = metrics.events_by_level.get(level, 0) + 1
            
            # Count failures
            if event.outcome == "failure":
                metrics.failed_events += 1
            
            # Count high risk events
            if event.risk_score >= 0.7:
                metrics.high_risk_events += 1
            
            # Count constitutional events
            if event.level == AuditLevel.CONSTITUTIONAL:
                metrics.constitutional_events += 1
        
        return metrics
    
    def _needs_new_file(self) -> bool:
        """Check if we need to create a new file."""
        return (
            self.current_file_path is None or
            self.current_file_size >= self.max_file_size
        )
    
    def _get_current_file_path(self) -> str:
        """Get current log file path."""
        if self.current_file_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.current_file_path = os.path.join(
                self.base_path,
                f"audit_{timestamp}.jsonl"
            )
            self.current_file_size = 0
        
        return self.current_file_path
    
    async def _rotate_file(self):
        """Rotate to a new file and optionally compress the old one."""
        if self.current_file_path and os.path.exists(self.current_file_path):
            # Compress old file if enabled
            if self.compression_enabled:
                compressed_path = self.current_file_path + '.gz'
                with open(self.current_file_path, 'rb') as f_in:
                    with gzip.open(compressed_path, 'wb') as f_out:
                        f_out.writelines(f_in)
                os.remove(self.current_file_path)
        
        # Reset for new file
        self.current_file_path = None
        self.current_file_size = 0
    
    async def _cleanup_old_files(self):
        """Remove files older than retention period."""
        cutoff_time = datetime.now() - timedelta(days=self.retention_days)
        
        try:
            for filename in os.listdir(self.base_path):
                file_path = os.path.join(self.base_path, filename)
                if os.path.getctime(file_path) < cutoff_time.timestamp():
                    os.remove(file_path)
        except Exception as e:
            logger.warning(f"Failed to cleanup old audit files: {e}")
    
    def _get_files_for_time_range(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> List[str]:
        """Get files that might contain events in the time range."""
        files = []
        
        try:
            for filename in os.listdir(self.base_path):
                if filename.startswith('audit_'):
                    file_path = os.path.join(self.base_path, filename)
                    file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                    
                    # Include file if it might contain relevant events
                    if file_time >= start_time - timedelta(days=1):
                        files.append(file_path)
        
        except Exception as e:
            logger.error(f"Failed to get files for time range: {e}")
        
        return sorted(files)
    
    def _parse_events_from_file(
        self,
        file_handle,
        start_time: datetime,
        end_time: datetime,
        filters: Dict[str, Any]
    ) -> List[AuditEvent]:
        """Parse events from a file handle."""
        events = []
        
        for line in file_handle:
            try:
                event_dict = json.loads(line.strip())
                event_time = datetime.fromisoformat(event_dict['timestamp'])
                
                # Check time range
                if not (start_time <= event_time <= end_time):
                    continue
                
                # Apply filters
                if not self._matches_filters(event_dict, filters):
                    continue
                
                # Convert back to AuditEvent
                event_dict['timestamp'] = event_time
                event_dict['event_type'] = AuditEventType(event_dict['event_type'])
                event_dict['level'] = AuditLevel(event_dict['level'])
                event_dict['compliance_tags'] = {
                    ComplianceFramework(tag) for tag in event_dict.get('compliance_tags', [])
                }
                
                # Remove fields that aren't in the dataclass
                valid_fields = {field.name for field in AuditEvent.__dataclass_fields__.values()}
                filtered_dict = {k: v for k, v in event_dict.items() if k in valid_fields}
                
                event = AuditEvent(**filtered_dict)
                events.append(event)
                
            except Exception as e:
                logger.warning(f"Failed to parse audit event line: {e}")
                continue
        
        return events
    
    def _matches_filters(self, event_dict: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if event matches the provided filters."""
        for key, value in filters.items():
            if key not in event_dict:
                return False
            
            if isinstance(value, list):
                if event_dict[key] not in value:
                    return False
            else:
                if event_dict[key] != value:
                    return False
        
        return True


class EnhancedAuditLogger:
    """Enhanced audit logging system with real-time monitoring."""
    
    def __init__(
        self,
        storage: Optional[AuditStorage] = None,
        service_name: str = "acgs-service",
        enable_real_time_alerts: bool = True,
        risk_threshold: float = 0.7
    ):
        self.storage = storage or FileAuditStorage()
        self.service_name = service_name
        self.enable_real_time_alerts = enable_real_time_alerts
        self.risk_threshold = risk_threshold
        self.metrics = AuditMetrics()
        self.alert_callbacks: List[callable] = []
        self.compliance_rules: Dict[ComplianceFramework, Dict[str, Any]] = {}
        self._initialize_compliance_rules()
    
    def _initialize_compliance_rules(self):
        """Initialize compliance framework rules."""
        self.compliance_rules[ComplianceFramework.CONSTITUTIONAL_AI] = {
            "required_events": [
                AuditEventType.CONSTITUTIONAL_CHANGE,
                AuditEventType.GOVERNANCE_DECISION,
                AuditEventType.POLICY_CHANGE
            ],
            "retention_days": 2555,  # ~7 years
            "encryption_required": True,
            "real_time_monitoring": True
        }
        
        self.compliance_rules[ComplianceFramework.SOC2] = {
            "required_events": [
                AuditEventType.AUTHENTICATION,
                AuditEventType.AUTHORIZATION,
                AuditEventType.DATA_ACCESS,
                AuditEventType.SECURITY_INCIDENT
            ],
            "retention_days": 365,
            "encryption_required": True
        }
        
        self.compliance_rules[ComplianceFramework.GDPR] = {
            "required_events": [
                AuditEventType.DATA_ACCESS,
                AuditEventType.DATA_MODIFICATION,
                AuditEventType.USER_MANAGEMENT
            ],
            "retention_days": 2555,
            "right_to_erasure": True,
            "data_protection_impact_assessment": True
        }
    
    async def log_event(
        self,
        event_type: AuditEventType,
        action: str,
        outcome: str,
        user_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        level: AuditLevel = AuditLevel.INFO,
        session_id: Optional[str] = None,
        source_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_duration_ms: Optional[float] = None,
        error_message: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> str:
        """Log an audit event."""
        try:
            # Generate event ID
            event_id = self._generate_event_id()
            
            # Calculate risk score
            risk_score = self._calculate_risk_score(
                event_type, outcome, details or {}, error_message
            )
            
            # Determine compliance tags
            compliance_tags = self._determine_compliance_tags(event_type, details or {})
            
            # Hash sensitive data if present
            sensitive_data_hash = None
            if details and self._contains_sensitive_data(details):
                sensitive_data_hash = self._hash_sensitive_data(details)
            
            # Create audit event
            event = AuditEvent(
                event_id=event_id,
                event_type=event_type,
                level=level,
                timestamp=datetime.now(),
                user_id=user_id,
                session_id=session_id,
                source_ip=source_ip,
                user_agent=user_agent,
                resource_type=resource_type,
                resource_id=resource_id,
                action=action,
                outcome=outcome,
                details=details or {},
                sensitive_data_hash=sensitive_data_hash,
                compliance_tags=compliance_tags,
                service_name=self.service_name,
                request_duration_ms=request_duration_ms,
                error_message=error_message,
                risk_score=risk_score,
                correlation_id=correlation_id
            )
            
            # Store event
            success = await self.storage.store_event(event)
            
            if success:
                # Update metrics
                self._update_metrics(event)
                
                # Check for real-time alerts
                if self.enable_real_time_alerts:
                    await self._check_real_time_alerts(event)
                
                logger.debug(
                    "Audit event logged",
                    event_id=event_id,
                    event_type=event_type.value,
                    action=action,
                    outcome=outcome,
                    risk_score=risk_score,
                    constitutional_hash=CONSTITUTIONAL_HASH
                )
            else:
                logger.error(
                    "Failed to store audit event",
                    event_id=event_id,
                    event_type=event_type.value
                )
            
            return event_id
            
        except Exception as e:
            logger.error(
                "Failed to log audit event",
                event_type=event_type.value if event_type else "unknown",
                action=action,
                error=str(e)
            )
            return ""
    
    async def log_authentication_event(
        self,
        action: str,
        outcome: str,
        user_id: Optional[str] = None,
        source_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ) -> str:
        """Log authentication-specific event."""
        return await self.log_event(
            event_type=AuditEventType.AUTHENTICATION,
            action=action,
            outcome=outcome,
            user_id=user_id,
            source_ip=source_ip,
            user_agent=user_agent,
            details=details,
            session_id=session_id,
            level=AuditLevel.WARNING if outcome == "failure" else AuditLevel.INFO
        )
    
    async def log_constitutional_event(
        self,
        action: str,
        outcome: str,
        user_id: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None
    ) -> str:
        """Log constitutional governance event."""
        return await self.log_event(
            event_type=AuditEventType.CONSTITUTIONAL_CHANGE,
            action=action,
            outcome=outcome,
            user_id=user_id,
            resource_type="constitutional_rule",
            resource_id=resource_id,
            details=details,
            level=AuditLevel.CONSTITUTIONAL,
            correlation_id=correlation_id
        )
    
    async def log_security_incident(
        self,
        action: str,
        user_id: Optional[str] = None,
        source_ip: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        severity: str = "medium"
    ) -> str:
        """Log security incident."""
        level_map = {
            "low": AuditLevel.WARNING,
            "medium": AuditLevel.ERROR,
            "high": AuditLevel.CRITICAL,
            "critical": AuditLevel.CRITICAL
        }
        
        return await self.log_event(
            event_type=AuditEventType.SECURITY_INCIDENT,
            action=action,
            outcome="detected",
            user_id=user_id,
            source_ip=source_ip,
            details=details or {},
            level=level_map.get(severity, AuditLevel.ERROR)
        )
    
    def add_alert_callback(self, callback: callable):
        """Add callback for real-time alerts."""
        self.alert_callbacks.append(callback)
    
    async def query_events(
        self,
        start_time: datetime,
        end_time: datetime,
        event_types: Optional[List[AuditEventType]] = None,
        user_id: Optional[str] = None,
        outcome: Optional[str] = None,
        min_risk_score: Optional[float] = None
    ) -> List[AuditEvent]:
        """Query audit events with filters."""
        filters = {}
        
        if event_types:
            filters['event_type'] = [et.value for et in event_types]
        if user_id:
            filters['user_id'] = user_id
        if outcome:
            filters['outcome'] = outcome
        
        events = await self.storage.query_events(start_time, end_time, filters)
        
        # Apply risk score filter
        if min_risk_score is not None:
            events = [e for e in events if e.risk_score >= min_risk_score]
        
        return events
    
    async def get_compliance_report(
        self,
        framework: ComplianceFramework,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """Generate compliance report for a specific framework."""
        rules = self.compliance_rules.get(framework, {})
        required_events = rules.get("required_events", [])
        
        # Get all events for the period
        all_events = await self.storage.query_events(start_time, end_time)
        
        # Filter events by compliance tags
        compliance_events = [
            e for e in all_events
            if framework in e.compliance_tags
        ]
        
        # Check coverage of required event types
        covered_types = set()
        for event in compliance_events:
            if event.event_type in required_events:
                covered_types.add(event.event_type)
        
        missing_types = set(required_events) - covered_types
        
        report = {
            "framework": framework.value,
            "period": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat()
            },
            "total_events": len(compliance_events),
            "required_event_types": len(required_events),
            "covered_event_types": len(covered_types),
            "missing_event_types": [et.value for et in missing_types],
            "compliance_score": len(covered_types) / len(required_events) if required_events else 1.0,
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
        
        return report
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID."""
        import uuid
        return str(uuid.uuid4())
    
    def _calculate_risk_score(
        self,
        event_type: AuditEventType,
        outcome: str,
        details: Dict[str, Any],
        error_message: Optional[str]
    ) -> float:
        """Calculate risk score for the event."""
        score = 0.0
        
        # Base score by event type
        type_scores = {
            AuditEventType.SECURITY_INCIDENT: 0.8,
            AuditEventType.CONSTITUTIONAL_CHANGE: 0.9,
            AuditEventType.AUTHENTICATION: 0.3,
            AuditEventType.AUTHORIZATION: 0.4,
            AuditEventType.DATA_MODIFICATION: 0.5
        }
        
        score += type_scores.get(event_type, 0.2)
        
        # Outcome modifier
        if outcome == "failure":
            score += 0.3
        elif outcome == "partial":
            score += 0.1
        
        # Error message modifier
        if error_message:
            score += 0.2
        
        # Details analysis
        suspicious_patterns = [
            "injection", "xss", "unauthorized", "escalation",
            "breach", "violation", "attack", "malicious"
        ]
        
        detail_text = json.dumps(details).lower()
        for pattern in suspicious_patterns:
            if pattern in detail_text:
                score += 0.1
        
        return min(1.0, score)
    
    def _determine_compliance_tags(
        self,
        event_type: AuditEventType,
        details: Dict[str, Any]
    ) -> Set[ComplianceFramework]:
        """Determine which compliance frameworks apply to this event."""
        tags = set()
        
        # Constitutional AI framework always applies
        tags.add(ComplianceFramework.CONSTITUTIONAL_AI)
        
        # Check other frameworks based on event type
        for framework, rules in self.compliance_rules.items():
            required_events = rules.get("required_events", [])
            if event_type in required_events:
                tags.add(framework)
        
        return tags
    
    def _contains_sensitive_data(self, details: Dict[str, Any]) -> bool:
        """Check if details contain sensitive data."""
        sensitive_keys = [
            "password", "token", "key", "secret", "credential",
            "ssn", "credit_card", "personal_data", "private"
        ]
        
        detail_text = json.dumps(details).lower()
        return any(key in detail_text for key in sensitive_keys)
    
    def _hash_sensitive_data(self, details: Dict[str, Any]) -> str:
        """Create hash of sensitive data for audit trail."""
        sensitive_str = json.dumps(details, sort_keys=True)
        return hashlib.sha256(sensitive_str.encode()).hexdigest()
    
    def _update_metrics(self, event: AuditEvent):
        """Update audit metrics."""
        self.metrics.total_events += 1
        
        event_type = event.event_type.value
        self.metrics.events_by_type[event_type] = (
            self.metrics.events_by_type.get(event_type, 0) + 1
        )
        
        level = event.level.value
        self.metrics.events_by_level[level] = (
            self.metrics.events_by_level.get(level, 0) + 1
        )
        
        if event.outcome == "failure":
            self.metrics.failed_events += 1
        
        if event.risk_score >= self.risk_threshold:
            self.metrics.high_risk_events += 1
        
        if event.level == AuditLevel.CONSTITUTIONAL:
            self.metrics.constitutional_events += 1
    
    async def _check_real_time_alerts(self, event: AuditEvent):
        """Check for conditions that should trigger real-time alerts."""
        should_alert = (
            event.level in [AuditLevel.CRITICAL, AuditLevel.CONSTITUTIONAL] or
            event.risk_score >= self.risk_threshold or
            event.event_type == AuditEventType.SECURITY_INCIDENT
        )
        
        if should_alert:
            alert_data = {
                "event_id": event.event_id,
                "event_type": event.event_type.value,
                "level": event.level.value,
                "risk_score": event.risk_score,
                "user_id": event.user_id,
                "action": event.action,
                "outcome": event.outcome,
                "timestamp": event.timestamp.isoformat(),
                "constitutional_hash": CONSTITUTIONAL_HASH
            }
            
            for callback in self.alert_callbacks:
                try:
                    await callback(alert_data)
                except Exception as e:
                    logger.error(f"Alert callback failed: {e}")


# Utility functions for easy integration
def create_audit_logger(
    service_name: str,
    storage_type: str = "file",
    storage_config: Optional[Dict[str, Any]] = None
) -> EnhancedAuditLogger:
    """Create audit logger with specified storage backend."""
    storage_config = storage_config or {}
    
    if storage_type == "file":
        storage = FileAuditStorage(**storage_config)
    else:
        raise ValueError(f"Unsupported storage type: {storage_type}")
    
    return EnhancedAuditLogger(
        storage=storage,
        service_name=service_name
    )


async def log_user_action(
    audit_logger: EnhancedAuditLogger,
    user_id: str,
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    outcome: str = "success",
    details: Optional[Dict[str, Any]] = None,
    request_context: Optional[Dict[str, Any]] = None
) -> str:
    """Utility function to log user actions."""
    context = request_context or {}
    
    return await audit_logger.log_event(
        event_type=AuditEventType.DATA_ACCESS,
        action=action,
        outcome=outcome,
        user_id=user_id,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        source_ip=context.get("source_ip"),
        user_agent=context.get("user_agent"),
        session_id=context.get("session_id"),
        correlation_id=context.get("correlation_id")
    )