#!/usr/bin/env python3
"""
Advanced Threat Detection Monitor
Real-time threat detection and automated response system.
"""

import json
import time
import logging
from collections import defaultdict, deque
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


class ThreatDetectionMonitor:
    """Advanced threat detection and response system."""

    def __init__(self):
        self.config_path = Path("config/security/threat_detection.json")
        self.load_configuration()
        self.event_history = defaultdict(deque)
        self.blocked_ips = {}

    def load_configuration(self):
        """Load threat detection configuration."""
        with open(self.config_path) as f:
            self.config = json.load(f)["threat_detection"]

    def analyze_event(self, event_type: str, source_ip: str, user_id: str = None):
        """Analyze security event for threat patterns."""
        current_time = datetime.now()

        # Add event to history
        self.event_history[f"{event_type}:{source_ip}"].append(current_time)

        # Check each detection rule
        for rule in self.config["detection_rules"]:
            if self.check_rule_violation(rule, event_type, source_ip, current_time):
                self.trigger_response(rule, source_ip, user_id)

    def check_rule_violation(self, rule, event_type, source_ip, current_time):
        """Check if event violates detection rule."""
        pattern = rule["pattern"]
        threshold = rule["threshold"]
        window_minutes = rule["window_minutes"]

        # Get events in time window
        window_start = current_time - timedelta(minutes=window_minutes)
        event_key = f"{pattern}:{source_ip}"

        # Count events in window
        recent_events = [
            event_time
            for event_time in self.event_history[event_key]
            if event_time >= window_start
        ]

        return len(recent_events) >= threshold

    def trigger_response(self, rule, source_ip, user_id):
        """Trigger automated threat response."""
        action = rule["action"]
        response_config = self.config["response_actions"][action]

        logger.warning(f"Threat detected: {rule['name']} from {source_ip}")

        if action == "block_ip":
            self.block_ip(source_ip, response_config["duration_minutes"])
        elif action == "rate_limit":
            self.apply_rate_limit(source_ip, response_config)
        elif action == "alert_security_team":
            self.alert_security_team(rule, source_ip, user_id, response_config)

    def block_ip(self, ip_address, duration_minutes):
        """Block IP address for specified duration."""
        unblock_time = datetime.now() + timedelta(minutes=duration_minutes)
        self.blocked_ips[ip_address] = unblock_time
        logger.info(f"Blocked IP {ip_address} until {unblock_time}")

    def apply_rate_limit(self, ip_address, config):
        """Apply rate limiting to IP address."""
        logger.info(
            f"Applied rate limit to {ip_address}: {config['limit_requests_per_minute']} req/min"
        )

    def alert_security_team(self, rule, source_ip, user_id, config):
        """Send alert to security team."""
        alert_message = f"Security Alert: {rule['name']} detected from {source_ip}"
        if user_id:
            alert_message += f" (User: {user_id})"

        logger.critical(alert_message)
        # In production, integrate with actual alerting systems


def main():
    """Main threat detection monitoring loop."""
    monitor = ThreatDetectionMonitor()

    # Simulate threat detection (in production, integrate with log streams)
    print("🛡️ Threat detection monitor started")
    print("Monitoring for security threats...")

    # Example threat simulation
    monitor.analyze_event("failed_login", "192.168.1.100")
    monitor.analyze_event("failed_login", "192.168.1.100")
    monitor.analyze_event("failed_login", "192.168.1.100")
    monitor.analyze_event("failed_login", "192.168.1.100")
    monitor.analyze_event("failed_login", "192.168.1.100")
    monitor.analyze_event("failed_login", "192.168.1.100")  # Should trigger block

    print("✅ Threat detection simulation completed")


if __name__ == "__main__":
    main()
