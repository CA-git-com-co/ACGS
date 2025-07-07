"""
Security Monitoring for ACGS
Constitutional Hash: cdd01ef066bc6cf2

Provides security event monitoring and alerting.
"""

import logging
import time
from datetime import datetime, timezone
from typing import Dict, Any, List
from enum import Enum

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)

class SecurityEventType(Enum):
    """Types of security events."""
    AUTHENTICATION_FAILURE = "auth_failure"
    AUTHORIZATION_FAILURE = "authz_failure"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    CONSTITUTIONAL_VIOLATION = "constitutional_violation"
    SECURITY_SCAN_DETECTED = "security_scan"

class SecurityMonitor:
    """Security event monitoring and alerting."""
    
    def __init__(self):
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.security_events = []
        self.alert_thresholds = {
            SecurityEventType.AUTHENTICATION_FAILURE: 5,  # 5 failures in window
            SecurityEventType.RATE_LIMIT_EXCEEDED: 3,     # 3 rate limit hits
            SecurityEventType.CONSTITUTIONAL_VIOLATION: 1, # Any violation
        }
        self.time_window_seconds = 300  # 5 minutes
    
    def log_security_event(
        self, 
        event_type: SecurityEventType, 
        details: Dict[str, Any],
        source_ip: str = None,
        user_id: str = None
    ) -> None:
        """Log a security event."""
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type.value,
            "details": details,
            "source_ip": source_ip,
            "user_id": user_id,
            "constitutional_hash": self.constitutional_hash,
        }
        
        self.security_events.append(event)
        logger.warning(f"Security event: {event_type.value} - {details}")
        
        # Check if alert threshold is exceeded
        self._check_alert_thresholds(event_type, source_ip, user_id)
    
    def _check_alert_thresholds(
        self, 
        event_type: SecurityEventType, 
        source_ip: str = None,
        user_id: str = None
    ) -> None:
        """Check if alert thresholds are exceeded."""
        threshold = self.alert_thresholds.get(event_type)
        if not threshold:
            return
        
        # Count recent events of this type
        current_time = time.time()
        recent_events = [
            event for event in self.security_events
            if (
                event["event_type"] == event_type.value and
                (current_time - time.mktime(
                    datetime.fromisoformat(event["timestamp"].replace("Z", "+00:00")).timetuple()
                )) <= self.time_window_seconds
            )
        ]
        
        if len(recent_events) >= threshold:
            self._trigger_security_alert(event_type, recent_events, source_ip, user_id)
    
    def _trigger_security_alert(
        self, 
        event_type: SecurityEventType, 
        events: List[Dict[str, Any]],
        source_ip: str = None,
        user_id: str = None
    ) -> None:
        """Trigger security alert."""
        alert = {
            "alert_type": "SECURITY_THRESHOLD_EXCEEDED",
            "event_type": event_type.value,
            "event_count": len(events),
            "time_window_seconds": self.time_window_seconds,
            "source_ip": source_ip,
            "user_id": user_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "constitutional_hash": self.constitutional_hash,
        }
        
        logger.critical(f"SECURITY ALERT: {alert}")
        
        # In production, this would send alerts to monitoring systems
        # For now, just log the alert
    
    def get_security_summary(self) -> Dict[str, Any]:
        """Get security events summary."""
        current_time = time.time()
        recent_events = [
            event for event in self.security_events
            if (current_time - time.mktime(
                datetime.fromisoformat(event["timestamp"].replace("Z", "+00:00")).timetuple()
            )) <= self.time_window_seconds
        ]
        
        event_counts = {}
        for event in recent_events:
            event_type = event["event_type"]
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        return {
            "total_events": len(self.security_events),
            "recent_events": len(recent_events),
            "event_counts": event_counts,
            "constitutional_hash": self.constitutional_hash,
        }

# Global security monitor instance
security_monitor = SecurityMonitor()
