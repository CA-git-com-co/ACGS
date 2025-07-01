#!/usr/bin/env python3
"""
ACGS DDoS Protection & Intrusion Detection System
Advanced DDoS protection and intrusion detection with constitutional compliance validation.
"""

import asyncio
import json
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Set, Tuple

import aiohttp
import ipaddress
from prometheus_client import (
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    start_http_server,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constitutional hash for compliance validation
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


@dataclass
class TrafficPattern:
    """Traffic pattern for analysis."""

    source_ip: str
    target_service: str
    request_count: int
    request_rate: float
    error_rate: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # Pattern characteristics
    user_agent: str = ""
    request_size: int = 0
    geographic_location: str = ""

    # Constitutional compliance
    constitutional_hash: str = CONSTITUTIONAL_HASH


@dataclass
class ThreatIntelligence:
    """Threat intelligence data."""

    ip_address: str
    threat_type: str  # malicious, suspicious, known_attacker
    confidence_score: float  # 0.0 to 1.0
    source: str  # threat_feed, behavioral_analysis, manual
    first_seen: datetime
    last_seen: datetime

    # Additional context
    attack_vectors: List[str] = field(default_factory=list)
    geographic_origin: str = ""

    # Constitutional compliance
    constitutional_hash: str = CONSTITUTIONAL_HASH


class DDoSProtectionSystem:
    """Advanced DDoS protection and intrusion detection system."""

    def __init__(self):
        # Metrics
        self.registry = CollectorRegistry()
        self.setup_metrics()

        # Traffic monitoring
        self.traffic_patterns: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=1000)
        )
        self.request_rates: Dict[str, Dict[str, int]] = defaultdict(
            lambda: defaultdict(int)
        )
        self.blocked_ips: Set[str] = set()

        # Threat intelligence
        self.threat_intelligence: Dict[str, ThreatIntelligence] = {}
        self.suspicious_patterns: List[TrafficPattern] = []

        # DDoS detection thresholds
        self.ddos_thresholds = {
            "auth-service": {"rps": 1000, "concurrent": 500},
            "ac-service": {"rps": 500, "concurrent": 200},
            "integrity-service": {"rps": 800, "concurrent": 300},
            "fv-service": {"rps": 600, "concurrent": 250},
            "gs-service": {"rps": 700, "concurrent": 300},
            "pgc-service": {"rps": 400, "concurrent": 150},
            "ec-service": {"rps": 300, "concurrent": 100},
        }

        # Rate limiting windows
        self.rate_windows = {"1m": 60, "5m": 300, "15m": 900, "1h": 3600}

        # Intrusion detection patterns
        self.attack_signatures = [
            {
                "name": "SQL Injection",
                "pattern": r"(union|select|insert|delete|drop|exec)",
                "severity": "high",
            },
            {
                "name": "XSS Attack",
                "pattern": r"(<script|javascript:|onload=|onerror=)",
                "severity": "medium",
            },
            {
                "name": "Path Traversal",
                "pattern": r"(\.\./|\.\.\\|%2e%2e)",
                "severity": "high",
            },
            {
                "name": "Command Injection",
                "pattern": r"(;|&&|\|\||`|\$\()",
                "severity": "critical",
            },
            {
                "name": "Constitutional Hash Manipulation",
                "pattern": r"constitutional[_-]?hash",
                "severity": "critical",
            },
        ]

        logger.info("DDoS Protection System initialized")

    def setup_metrics(self):
        """Setup Prometheus metrics for DDoS protection."""
        self.requests_per_second = Gauge(
            "acgs_ddos_requests_per_second",
            "Current requests per second by service and source",
            ["service", "source_type"],
            registry=self.registry,
        )

        self.ddos_attacks_detected = Counter(
            "acgs_ddos_attacks_detected_total",
            "Total DDoS attacks detected",
            ["service", "attack_type", "severity"],
            registry=self.registry,
        )

        self.intrusion_attempts = Counter(
            "acgs_intrusion_attempts_total",
            "Total intrusion attempts detected",
            ["service", "attack_signature", "severity"],
            registry=self.registry,
        )

        self.blocked_requests = Counter(
            "acgs_blocked_requests_total",
            "Total requests blocked by DDoS protection",
            ["service", "block_reason"],
            registry=self.registry,
        )

        self.threat_intelligence_score = Gauge(
            "acgs_threat_intelligence_score",
            "Threat intelligence score for IP addresses",
            ["ip_address", "threat_type"],
            registry=self.registry,
        )

        self.constitutional_compliance_ddos = Gauge(
            "acgs_ddos_constitutional_compliance",
            "Constitutional compliance during DDoS protection",
            ["protection_component"],
            registry=self.registry,
        )

    async def start_protection_system(self):
        """Start the DDoS protection system."""
        logger.info("Starting DDoS Protection System...")

        # Start metrics server
        start_http_server(8104, registry=self.registry)
        logger.info("DDoS protection metrics server started on port 8104")

        # Start monitoring tasks
        asyncio.create_task(self.traffic_monitoring_loop())
        asyncio.create_task(self.ddos_detection_loop())
        asyncio.create_task(self.intrusion_detection_loop())
        asyncio.create_task(self.threat_intelligence_loop())
        asyncio.create_task(self.cleanup_loop())

        logger.info("DDoS Protection System started")

    async def analyze_request(
        self, source_ip: str, target_service: str, request_data: Dict
    ) -> bool:
        """Analyze incoming request for threats."""
        try:
            # Check if IP is blocked
            if source_ip in self.blocked_ips:
                self.blocked_requests.labels(
                    service=target_service, block_reason="blocked_ip"
                ).inc()
                return False

            # Check threat intelligence
            if source_ip in self.threat_intelligence:
                threat = self.threat_intelligence[source_ip]
                if threat.confidence_score > 0.8:
                    logger.warning(
                        f"High-confidence threat detected: {source_ip} -> {target_service}"
                    )
                    self.blocked_requests.labels(
                        service=target_service, block_reason="threat_intelligence"
                    ).inc()
                    return False

            # Rate limiting check
            if not await self.check_rate_limits(source_ip, target_service):
                self.blocked_requests.labels(
                    service=target_service, block_reason="rate_limit"
                ).inc()
                return False

            # Intrusion detection
            if await self.detect_intrusion_attempt(request_data, target_service):
                self.blocked_requests.labels(
                    service=target_service, block_reason="intrusion_attempt"
                ).inc()
                return False

            # Constitutional compliance validation
            if not await self.validate_constitutional_compliance(
                request_data, target_service
            ):
                self.blocked_requests.labels(
                    service=target_service, block_reason="constitutional_violation"
                ).inc()
                return False

            # Record traffic pattern
            await self.record_traffic_pattern(source_ip, target_service, request_data)

            return True

        except Exception as e:
            logger.error(f"Error analyzing request: {e}")
            return False

    async def check_rate_limits(self, source_ip: str, target_service: str) -> bool:
        """Check rate limits for source IP and target service."""
        current_time = int(time.time())

        # Check different time windows
        for window_name, window_size in self.rate_windows.items():
            window_start = current_time - window_size

            # Count requests in this window
            request_count = 0
            if source_ip in self.traffic_patterns:
                for pattern in self.traffic_patterns[source_ip]:
                    if pattern.timestamp.timestamp() >= window_start:
                        if pattern.target_service == target_service:
                            request_count += pattern.request_count

            # Check against thresholds
            threshold = self.ddos_thresholds.get(target_service, {"rps": 1000})
            max_requests = threshold["rps"] * (
                window_size / 60
            )  # Convert to requests per window

            if request_count > max_requests:
                logger.warning(
                    f"Rate limit exceeded: {source_ip} -> {target_service} ({request_count}/{max_requests} in {window_name})"
                )
                return False

        return True

    async def detect_intrusion_attempt(
        self, request_data: Dict, target_service: str
    ) -> bool:
        """Detect intrusion attempts in request data."""
        try:
            # Analyze request content
            request_content = json.dumps(request_data).lower()

            for signature in self.attack_signatures:
                import re

                if re.search(signature["pattern"], request_content, re.IGNORECASE):
                    logger.warning(
                        f"Intrusion attempt detected: {signature['name']} in {target_service}"
                    )

                    self.intrusion_attempts.labels(
                        service=target_service,
                        attack_signature=signature["name"],
                        severity=signature["severity"],
                    ).inc()

                    return True

            # Check for constitutional hash manipulation
            if "constitutional_hash" in request_content:
                provided_hash = request_data.get("constitutional_hash", "")
                if provided_hash != CONSTITUTIONAL_HASH:
                    logger.critical(
                        f"Constitutional hash manipulation detected: {provided_hash}"
                    )

                    self.intrusion_attempts.labels(
                        service=target_service,
                        attack_signature="Constitutional Hash Manipulation",
                        severity="critical",
                    ).inc()

                    return True

            return False

        except Exception as e:
            logger.error(f"Error in intrusion detection: {e}")
            return False

    async def validate_constitutional_compliance(
        self, request_data: Dict, target_service: str
    ) -> bool:
        """Validate constitutional compliance for request."""
        try:
            # Check if service requires constitutional validation
            if target_service in ["ac-service", "pgc-service", "ec-service"]:
                # Validate constitutional hash if present
                if "constitutional_hash" in request_data:
                    provided_hash = request_data.get("constitutional_hash")
                    if provided_hash != CONSTITUTIONAL_HASH:
                        logger.warning(f"Invalid constitutional hash: {provided_hash}")
                        return False

                # Update compliance metrics
                self.constitutional_compliance_ddos.labels(
                    protection_component="request_validation"
                ).set(1.0)

            return True

        except Exception as e:
            logger.error(f"Constitutional compliance validation failed: {e}")
            return False

    async def record_traffic_pattern(
        self, source_ip: str, target_service: str, request_data: Dict
    ):
        """Record traffic pattern for analysis."""
        try:
            pattern = TrafficPattern(
                source_ip=source_ip,
                target_service=target_service,
                request_count=1,
                request_rate=1.0,  # Will be calculated in analysis
                error_rate=0.0,
                user_agent=request_data.get("user_agent", ""),
                request_size=len(json.dumps(request_data)),
            )

            self.traffic_patterns[source_ip].append(pattern)

        except Exception as e:
            logger.error(f"Error recording traffic pattern: {e}")

    async def traffic_monitoring_loop(self):
        """Monitor traffic patterns continuously."""
        while True:
            try:
                current_time = time.time()

                # Calculate current request rates
                for service_name in self.ddos_thresholds.keys():
                    total_rps = 0
                    unique_ips = set()

                    for ip, patterns in self.traffic_patterns.items():
                        recent_patterns = [
                            p
                            for p in patterns
                            if p.target_service == service_name
                            and (current_time - p.timestamp.timestamp()) < 60
                        ]

                        if recent_patterns:
                            unique_ips.add(ip)
                            total_rps += len(recent_patterns)

                    # Update metrics
                    self.requests_per_second.labels(
                        service=service_name, source_type="total"
                    ).set(
                        total_rps / 60
                    )  # Convert to RPS

                    self.requests_per_second.labels(
                        service=service_name, source_type="unique_ips"
                    ).set(len(unique_ips))

                await asyncio.sleep(10)

            except Exception as e:
                logger.error(f"Error in traffic monitoring loop: {e}")
                await asyncio.sleep(30)

    async def ddos_detection_loop(self):
        """Detect DDoS attacks continuously."""
        while True:
            try:
                current_time = time.time()

                for service_name, thresholds in self.ddos_thresholds.items():
                    # Analyze traffic patterns for this service
                    service_patterns = []

                    for ip, patterns in self.traffic_patterns.items():
                        recent_patterns = [
                            p
                            for p in patterns
                            if p.target_service == service_name
                            and (current_time - p.timestamp.timestamp())
                            < 300  # 5 minutes
                        ]

                        if recent_patterns:
                            service_patterns.extend(recent_patterns)

                    # Calculate metrics
                    total_requests = len(service_patterns)
                    unique_ips = len(set(p.source_ip for p in service_patterns))
                    avg_rps = total_requests / 300 if total_requests > 0 else 0

                    # Detect volumetric attacks
                    if avg_rps > thresholds["rps"]:
                        await self.handle_ddos_attack(
                            service_name,
                            "volumetric",
                            f"High RPS detected: {avg_rps:.1f} > {thresholds['rps']}",
                        )

                    # Detect distributed attacks
                    if unique_ips > thresholds["concurrent"]:
                        await self.handle_ddos_attack(
                            service_name,
                            "distributed",
                            f"High concurrent IPs: {unique_ips} > {thresholds['concurrent']}",
                        )

                    # Detect application layer attacks
                    error_patterns = [p for p in service_patterns if p.error_rate > 0.5]
                    if len(error_patterns) > total_requests * 0.3:  # 30% error rate
                        await self.handle_ddos_attack(
                            service_name,
                            "application_layer",
                            f"High error rate detected: {len(error_patterns)}/{total_requests}",
                        )

                await asyncio.sleep(30)

            except Exception as e:
                logger.error(f"Error in DDoS detection loop: {e}")
                await asyncio.sleep(60)

    async def handle_ddos_attack(
        self, service_name: str, attack_type: str, description: str
    ):
        """Handle detected DDoS attack."""
        logger.critical(
            f"DDoS attack detected on {service_name}: {attack_type} - {description}"
        )

        # Record attack
        severity = (
            "critical" if attack_type in ["volumetric", "application_layer"] else "high"
        )
        self.ddos_attacks_detected.labels(
            service=service_name, attack_type=attack_type, severity=severity
        ).inc()

        # Implement mitigation strategies
        await self.mitigate_ddos_attack(service_name, attack_type)

    async def mitigate_ddos_attack(self, service_name: str, attack_type: str):
        """Implement DDoS mitigation strategies."""
        logger.info(f"Implementing DDoS mitigation for {service_name} ({attack_type})")

        try:
            # Reduce rate limits temporarily
            if service_name in self.ddos_thresholds:
                original_rps = self.ddos_thresholds[service_name]["rps"]
                self.ddos_thresholds[service_name]["rps"] = int(original_rps * 0.5)
                logger.info(
                    f"Reduced rate limit for {service_name} to {self.ddos_thresholds[service_name]['rps']} RPS"
                )

            # Block top attacking IPs
            await self.block_top_attacking_ips(service_name)

            # Enable additional filtering
            await self.enable_enhanced_filtering(service_name)

            # Schedule mitigation removal
            asyncio.create_task(
                self.remove_mitigation_after_delay(service_name, 300)
            )  # 5 minutes

        except Exception as e:
            logger.error(f"Error implementing DDoS mitigation: {e}")

    async def block_top_attacking_ips(self, service_name: str, top_n: int = 10):
        """Block top attacking IP addresses."""
        try:
            # Analyze recent traffic patterns
            current_time = time.time()
            ip_request_counts = defaultdict(int)

            for ip, patterns in self.traffic_patterns.items():
                recent_patterns = [
                    p
                    for p in patterns
                    if p.target_service == service_name
                    and (current_time - p.timestamp.timestamp()) < 300
                ]
                ip_request_counts[ip] = len(recent_patterns)

            # Sort by request count and block top attackers
            top_attackers = sorted(
                ip_request_counts.items(), key=lambda x: x[1], reverse=True
            )[:top_n]

            for ip, request_count in top_attackers:
                if request_count > 100:  # Threshold for blocking
                    self.blocked_ips.add(ip)
                    logger.warning(
                        f"Blocked attacking IP: {ip} ({request_count} requests)"
                    )

                    # Add to threat intelligence
                    self.threat_intelligence[ip] = ThreatIntelligence(
                        ip_address=ip,
                        threat_type="ddos_attacker",
                        confidence_score=0.9,
                        source="ddos_mitigation",
                        first_seen=datetime.now(timezone.utc),
                        last_seen=datetime.now(timezone.utc),
                        attack_vectors=["ddos"],
                    )

        except Exception as e:
            logger.error(f"Error blocking attacking IPs: {e}")

    async def enable_enhanced_filtering(self, service_name: str):
        """Enable enhanced filtering during DDoS attack."""
        logger.info(f"Enabling enhanced filtering for {service_name}")

        # This would integrate with actual filtering mechanisms
        # For now, we'll simulate by updating metrics
        self.constitutional_compliance_ddos.labels(
            protection_component="enhanced_filtering"
        ).set(1.0)

    async def remove_mitigation_after_delay(
        self, service_name: str, delay_seconds: int
    ):
        """Remove DDoS mitigation after specified delay."""
        await asyncio.sleep(delay_seconds)

        try:
            # Restore original rate limits
            if service_name in self.ddos_thresholds:
                # This is simplified - in practice, you'd store original values
                original_rps = int(self.ddos_thresholds[service_name]["rps"] * 2)
                self.ddos_thresholds[service_name]["rps"] = original_rps
                logger.info(
                    f"Restored rate limit for {service_name} to {original_rps} RPS"
                )

            logger.info(f"DDoS mitigation removed for {service_name}")

        except Exception as e:
            logger.error(f"Error removing DDoS mitigation: {e}")

    async def intrusion_detection_loop(self):
        """Continuous intrusion detection."""
        while True:
            try:
                # Analyze recent traffic patterns for suspicious behavior
                current_time = time.time()

                for ip, patterns in self.traffic_patterns.items():
                    recent_patterns = [
                        p
                        for p in patterns
                        if (current_time - p.timestamp.timestamp()) < 3600  # 1 hour
                    ]

                    if len(recent_patterns) > 50:  # High activity threshold
                        await self.analyze_suspicious_behavior(ip, recent_patterns)

                await asyncio.sleep(60)

            except Exception as e:
                logger.error(f"Error in intrusion detection loop: {e}")
                await asyncio.sleep(120)

    async def analyze_suspicious_behavior(
        self, ip: str, patterns: List[TrafficPattern]
    ):
        """Analyze patterns for suspicious behavior."""
        try:
            # Check for scanning behavior
            unique_services = set(p.target_service for p in patterns)
            if len(unique_services) > 5:  # Accessing many services
                logger.warning(
                    f"Potential scanning detected from {ip}: {len(unique_services)} services"
                )

                # Add to threat intelligence
                if ip not in self.threat_intelligence:
                    self.threat_intelligence[ip] = ThreatIntelligence(
                        ip_address=ip,
                        threat_type="suspicious",
                        confidence_score=0.6,
                        source="behavioral_analysis",
                        first_seen=datetime.now(timezone.utc),
                        last_seen=datetime.now(timezone.utc),
                        attack_vectors=["scanning"],
                    )

            # Check for rapid requests
            time_span = max(p.timestamp for p in patterns) - min(
                p.timestamp for p in patterns
            )
            if time_span.total_seconds() < 60 and len(patterns) > 100:
                logger.warning(
                    f"Rapid requests detected from {ip}: {len(patterns)} in {time_span.total_seconds()}s"
                )

                # Increase threat score
                if ip in self.threat_intelligence:
                    self.threat_intelligence[ip].confidence_score = min(
                        1.0, self.threat_intelligence[ip].confidence_score + 0.2
                    )

        except Exception as e:
            logger.error(f"Error analyzing suspicious behavior: {e}")

    async def threat_intelligence_loop(self):
        """Update threat intelligence continuously."""
        while True:
            try:
                # Update threat intelligence metrics
                for ip, threat in self.threat_intelligence.items():
                    self.threat_intelligence_score.labels(
                        ip_address=ip, threat_type=threat.threat_type
                    ).set(threat.confidence_score)

                # Clean up old threat intelligence
                cutoff_time = datetime.now(timezone.utc) - timedelta(days=7)
                expired_threats = [
                    ip
                    for ip, threat in self.threat_intelligence.items()
                    if threat.last_seen < cutoff_time and threat.confidence_score < 0.5
                ]

                for ip in expired_threats:
                    del self.threat_intelligence[ip]
                    if ip in self.blocked_ips:
                        self.blocked_ips.remove(ip)

                await asyncio.sleep(300)  # 5 minutes

            except Exception as e:
                logger.error(f"Error in threat intelligence loop: {e}")
                await asyncio.sleep(600)

    async def cleanup_loop(self):
        """Clean up old data periodically."""
        while True:
            try:
                current_time = time.time()
                cutoff_time = current_time - 3600  # 1 hour

                # Clean up old traffic patterns
                for ip in list(self.traffic_patterns.keys()):
                    patterns = self.traffic_patterns[ip]
                    # Remove patterns older than 1 hour
                    while patterns and patterns[0].timestamp.timestamp() < cutoff_time:
                        patterns.popleft()

                    # Remove empty entries
                    if not patterns:
                        del self.traffic_patterns[ip]

                logger.info(
                    f"Cleaned up old traffic patterns. Active IPs: {len(self.traffic_patterns)}"
                )

                await asyncio.sleep(600)  # 10 minutes

            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(1200)

    def get_protection_status(self) -> Dict[str, Any]:
        """Get DDoS protection system status."""
        return {
            "active_traffic_patterns": len(self.traffic_patterns),
            "blocked_ips": len(self.blocked_ips),
            "threat_intelligence_entries": len(self.threat_intelligence),
            "suspicious_patterns": len(self.suspicious_patterns),
            "ddos_thresholds": self.ddos_thresholds,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "protection_enabled": True,
            "intrusion_detection_enabled": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# Global DDoS protection system instance
ddos_protection = DDoSProtectionSystem()

if __name__ == "__main__":

    async def main():
        await ddos_protection.start_protection_system()

        try:
            # Keep running
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down DDoS protection system...")

    asyncio.run(main())
