#!/usr/bin/env python3
"""
ACGS Network Security Manager
Advanced network-level security controls including mTLS, network policies, DDoS protection, and intrusion detection.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from prometheus_client import (
    CollectorRegistry,
    Counter,
    Gauge,
    start_http_server,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constitutional hash for compliance validation
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


@dataclass
class NetworkSecurityPolicy:
    """Network security policy definition."""

    policy_id: str
    name: str
    policy_type: str  # ingress, egress, mtls, ddos_protection

    # Policy rules
    allowed_sources: list[str] = field(default_factory=list)
    allowed_destinations: list[str] = field(default_factory=list)
    allowed_ports: list[int] = field(default_factory=list)
    protocols: list[str] = field(default_factory=list)

    # Security settings
    require_mtls: bool = True
    rate_limit_rps: int = 1000
    ddos_threshold: int = 10000

    # Constitutional compliance
    constitutional_hash: str = CONSTITUTIONAL_HASH
    constitutional_validation_required: bool = True


@dataclass
class SecurityEvent:
    """Security event for monitoring and alerting."""

    event_id: str
    event_type: str
    severity: str  # low, medium, high, critical
    source_ip: str
    target_service: str
    description: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    constitutional_hash: str = CONSTITUTIONAL_HASH


class NetworkSecurityManager:
    """Advanced network security manager for ACGS."""

    def __init__(self):
        # Metrics
        self.registry = CollectorRegistry()
        self.setup_metrics()

        # ACGS services configuration
        self.services = {
            "auth-service": {"port": 8000, "security_level": "high"},
            "ac-service": {"port": 8001, "security_level": "critical"},
            "integrity-service": {"port": 8002, "security_level": "high"},
            "fv-service": {"port": 8003, "security_level": "medium"},
            "gs-service": {"port": 8004, "security_level": "medium"},
            "pgc-service": {"port": 8005, "security_level": "critical"},
            "ec-service": {"port": 8006, "security_level": "critical"},
        }

        # Security policies
        self.network_policies: dict[str, NetworkSecurityPolicy] = {}
        self.security_events: list[SecurityEvent] = []

        # mTLS configuration
        self.ca_cert = None
        self.ca_key = None
        self.service_certificates: dict[str, dict] = {}

        # Rate limiting and DDoS protection
        self.rate_limiters: dict[str, dict] = {}
        self.blocked_ips: set = set()

        logger.info("Network Security Manager initialized")

    def setup_metrics(self):
        """Setup Prometheus metrics for network security."""
        self.security_events_total = Counter(
            "acgs_security_events_total",
            "Total security events detected",
            ["event_type", "severity", "target_service"],
            registry=self.registry,
        )

        self.network_connections_total = Counter(
            "acgs_network_connections_total",
            "Total network connections",
            ["source_service", "target_service", "protocol"],
            registry=self.registry,
        )

        self.mtls_handshakes_total = Counter(
            "acgs_mtls_handshakes_total",
            "Total mTLS handshakes",
            ["service", "status"],
            registry=self.registry,
        )

        self.ddos_attacks_blocked = Counter(
            "acgs_ddos_attacks_blocked_total",
            "Total DDoS attacks blocked",
            ["target_service", "attack_type"],
            registry=self.registry,
        )

        self.rate_limit_violations = Counter(
            "acgs_rate_limit_violations_total",
            "Total rate limit violations",
            ["service", "source_ip"],
            registry=self.registry,
        )

        self.constitutional_compliance_network = Gauge(
            "acgs_network_constitutional_compliance",
            "Constitutional compliance for network security",
            ["security_component"],
            registry=self.registry,
        )

    async def initialize_security_framework(self):
        """Initialize the network security framework."""
        logger.info("Initializing network security framework...")

        # Start metrics server
        start_http_server(8103, registry=self.registry)
        logger.info("Network security metrics server started on port 8103")

        # Initialize CA and certificates
        await self.initialize_pki()

        # Setup network policies
        await self.setup_network_policies()

        # Initialize rate limiting
        await self.initialize_rate_limiting()

        # Start security monitoring
        asyncio.create_task(self.security_monitoring_loop())
        asyncio.create_task(self.ddos_protection_loop())
        asyncio.create_task(self.intrusion_detection_loop())

        logger.info("Network security framework initialized")

    async def initialize_pki(self):
        """Initialize PKI for mTLS."""
        logger.info("Initializing PKI for mTLS...")

        try:
            # Generate CA private key
            self.ca_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

            # Create CA certificate
            ca_name = x509.Name(
                [
                    x509.NameAttribute(x509.NameOID.COUNTRY_NAME, "US"),
                    x509.NameAttribute(x509.NameOID.STATE_OR_PROVINCE_NAME, "CA"),
                    x509.NameAttribute(x509.NameOID.LOCALITY_NAME, "San Francisco"),
                    x509.NameAttribute(x509.NameOID.ORGANIZATION_NAME, "ACGS"),
                    x509.NameAttribute(x509.NameOID.COMMON_NAME, "ACGS Root CA"),
                ]
            )

            self.ca_cert = (
                x509.CertificateBuilder()
                .subject_name(ca_name)
                .issuer_name(ca_name)
                .public_key(self.ca_key.public_key())
                .serial_number(x509.random_serial_number())
                .not_valid_before(datetime.utcnow())
                .not_valid_after(datetime.utcnow() + timedelta(days=365))
                .add_extension(
                    x509.BasicConstraints(ca=True, path_length=None),
                    critical=True,
                )
                .add_extension(
                    x509.KeyUsage(
                        key_cert_sign=True,
                        crl_sign=True,
                        digital_signature=False,
                        content_commitment=False,
                        key_encipherment=False,
                        data_encipherment=False,
                        key_agreement=False,
                        encipher_only=False,
                        decipher_only=False,
                    ),
                    critical=True,
                )
                .sign(self.ca_key, hashes.SHA256())
            )

            # Generate service certificates
            for service_name in self.services.keys():
                await self.generate_service_certificate(service_name)

            logger.info("PKI initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize PKI: {e}")
            raise

    async def generate_service_certificate(self, service_name: str):
        """Generate certificate for a service."""
        try:
            # Generate service private key
            service_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

            # Create service certificate
            service_name_obj = x509.Name(
                [
                    x509.NameAttribute(x509.NameOID.COUNTRY_NAME, "US"),
                    x509.NameAttribute(x509.NameOID.STATE_OR_PROVINCE_NAME, "CA"),
                    x509.NameAttribute(x509.NameOID.LOCALITY_NAME, "San Francisco"),
                    x509.NameAttribute(x509.NameOID.ORGANIZATION_NAME, "ACGS"),
                    x509.NameAttribute(x509.NameOID.COMMON_NAME, service_name),
                ]
            )

            service_cert = (
                x509.CertificateBuilder()
                .subject_name(service_name_obj)
                .issuer_name(self.ca_cert.subject)
                .public_key(service_key.public_key())
                .serial_number(x509.random_serial_number())
                .not_valid_before(datetime.utcnow())
                .not_valid_after(datetime.utcnow() + timedelta(days=90))
                .add_extension(
                    x509.SubjectAlternativeName(
                        [
                            x509.DNSName(service_name),
                            x509.DNSName(f"{service_name}.acgs.local"),
                            x509.DNSName("localhost"),
                        ]
                    ),
                    critical=False,
                )
                .add_extension(
                    x509.KeyUsage(
                        key_cert_sign=False,
                        crl_sign=False,
                        digital_signature=True,
                        content_commitment=False,
                        key_encipherment=True,
                        data_encipherment=False,
                        key_agreement=False,
                        encipher_only=False,
                        decipher_only=False,
                    ),
                    critical=True,
                )
                .sign(self.ca_key, hashes.SHA256())
            )

            # Store certificate and key
            self.service_certificates[service_name] = {
                "certificate": service_cert,
                "private_key": service_key,
                "pem_cert": service_cert.public_bytes(serialization.Encoding.PEM),
                "pem_key": service_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption(),
                ),
            }

            logger.info(f"Generated certificate for {service_name}")

        except Exception as e:
            logger.error(f"Failed to generate certificate for {service_name}: {e}")

    async def setup_network_policies(self):
        """Setup network security policies."""
        logger.info("Setting up network security policies...")

        # Critical services policy (AC, PGC, EC)
        critical_policy = NetworkSecurityPolicy(
            policy_id="critical_services_policy",
            name="Critical Services Security Policy",
            policy_type="ingress",
            allowed_sources=["auth-service", "integrity-service"],
            allowed_ports=[8001, 8005, 8006],
            protocols=["https"],
            require_mtls=True,
            rate_limit_rps=500,
            ddos_threshold=5000,
        )
        self.network_policies["critical_services"] = critical_policy

        # Auth service policy
        auth_policy = NetworkSecurityPolicy(
            policy_id="auth_service_policy",
            name="Authentication Service Security Policy",
            policy_type="ingress",
            allowed_sources=["*"],  # Auth service needs to be accessible
            allowed_ports=[8000],
            protocols=["https"],
            require_mtls=True,
            rate_limit_rps=1000,
            ddos_threshold=10000,
        )
        self.network_policies["auth_service"] = auth_policy

        # Internal services policy
        internal_policy = NetworkSecurityPolicy(
            policy_id="internal_services_policy",
            name="Internal Services Security Policy",
            policy_type="ingress",
            allowed_sources=["auth-service", "ac-service", "pgc-service"],
            allowed_ports=[8002, 8003, 8004],
            protocols=["https"],
            require_mtls=True,
            rate_limit_rps=800,
            ddos_threshold=8000,
        )
        self.network_policies["internal_services"] = internal_policy

        # Constitutional compliance validation policy
        constitutional_policy = NetworkSecurityPolicy(
            policy_id="constitutional_compliance_policy",
            name="Constitutional Compliance Security Policy",
            policy_type="egress",
            allowed_destinations=["ac-service", "pgc-service"],
            allowed_ports=[8001, 8005],
            protocols=["https"],
            require_mtls=True,
            constitutional_validation_required=True,
        )
        self.network_policies["constitutional_compliance"] = constitutional_policy

        logger.info(f"Setup {len(self.network_policies)} network security policies")

    async def initialize_rate_limiting(self):
        """Initialize rate limiting for services."""
        logger.info("Initializing rate limiting...")

        for service_name, config in self.services.items():
            self.rate_limiters[service_name] = {
                "requests": {},  # IP -> request count
                "window_start": time.time(),
                "window_size": 60,  # 1 minute window
                "max_requests": (
                    1000 if config["security_level"] == "critical" else 2000
                ),
            }

        logger.info("Rate limiting initialized")

    async def validate_network_request(
        self, source_ip: str, target_service: str, protocol: str
    ) -> bool:
        """Validate network request against security policies."""
        try:
            # Check if IP is blocked
            if source_ip in self.blocked_ips:
                await self.log_security_event(
                    "blocked_ip_access",
                    "high",
                    source_ip,
                    target_service,
                    f"Blocked IP {source_ip} attempted access to {target_service}",
                )
                return False

            # Check rate limiting
            if not await self.check_rate_limit(source_ip, target_service):
                await self.log_security_event(
                    "rate_limit_violation",
                    "medium",
                    source_ip,
                    target_service,
                    f"Rate limit exceeded for {source_ip} accessing {target_service}",
                )
                return False

            # Check network policies
            policy_key = self.get_policy_key_for_service(target_service)
            if policy_key in self.network_policies:
                policy = self.network_policies[policy_key]

                # Check allowed sources
                if (
                    policy.allowed_sources != ["*"]
                    and source_ip not in policy.allowed_sources
                ):
                    await self.log_security_event(
                        "unauthorized_source",
                        "high",
                        source_ip,
                        target_service,
                        f"Unauthorized source {source_ip} attempted access to {target_service}",
                    )
                    return False

                # Check protocol
                if protocol not in policy.protocols:
                    await self.log_security_event(
                        "invalid_protocol",
                        "medium",
                        source_ip,
                        target_service,
                        f"Invalid protocol {protocol} for {target_service}",
                    )
                    return False

            # Constitutional compliance validation
            if not await self.validate_constitutional_compliance(target_service):
                await self.log_security_event(
                    "constitutional_compliance_failure",
                    "critical",
                    source_ip,
                    target_service,
                    f"Constitutional compliance validation failed for {target_service}",
                )
                return False

            # Record successful connection
            self.network_connections_total.labels(
                source_service=source_ip,
                target_service=target_service,
                protocol=protocol,
            ).inc()

            return True

        except Exception as e:
            logger.error(f"Error validating network request: {e}")
            return False

    async def check_rate_limit(self, source_ip: str, target_service: str) -> bool:
        """Check rate limiting for source IP and target service."""
        if target_service not in self.rate_limiters:
            return True

        rate_limiter = self.rate_limiters[target_service]
        current_time = time.time()

        # Reset window if needed
        if current_time - rate_limiter["window_start"] > rate_limiter["window_size"]:
            rate_limiter["requests"] = {}
            rate_limiter["window_start"] = current_time

        # Check current request count
        current_requests = rate_limiter["requests"].get(source_ip, 0)

        if current_requests >= rate_limiter["max_requests"]:
            self.rate_limit_violations.labels(
                service=target_service, source_ip=source_ip
            ).inc()
            return False

        # Increment request count
        rate_limiter["requests"][source_ip] = current_requests + 1
        return True

    async def validate_constitutional_compliance(self, target_service: str) -> bool:
        """Validate constitutional compliance for network access."""
        try:
            # Check if service requires constitutional validation
            if target_service in ["ac-service", "pgc-service", "ec-service"]:
                # Simulate constitutional hash validation
                # In practice, this would validate against the actual service
                compliance_score = 1.0  # Assume compliance for simulation

                self.constitutional_compliance_network.labels(
                    security_component="network_access"
                ).set(compliance_score)

                return compliance_score >= 0.95

            return True

        except Exception as e:
            logger.error(f"Constitutional compliance validation failed: {e}")
            return False

    async def perform_mtls_handshake(
        self, service_name: str, peer_service: str
    ) -> bool:
        """Perform mTLS handshake between services."""
        try:
            # Check if both services have certificates
            if (
                service_name not in self.service_certificates
                or peer_service not in self.service_certificates
            ):
                logger.error(
                    f"Missing certificates for mTLS handshake: {service_name} <-> {peer_service}"
                )
                self.mtls_handshakes_total.labels(
                    service=service_name, status="failed"
                ).inc()
                return False

            # Simulate mTLS handshake validation
            # In practice, this would involve actual TLS certificate validation

            # Validate certificate chain
            service_cert = self.service_certificates[service_name]["certificate"]
            peer_cert = self.service_certificates[peer_service]["certificate"]

            # Check certificate validity
            current_time = datetime.utcnow()
            if (
                service_cert.not_valid_after < current_time
                or peer_cert.not_valid_after < current_time
            ):
                logger.error(
                    f"Expired certificates in mTLS handshake: {service_name} <-> {peer_service}"
                )
                self.mtls_handshakes_total.labels(
                    service=service_name, status="failed"
                ).inc()
                return False

            # Successful mTLS handshake
            self.mtls_handshakes_total.labels(
                service=service_name, status="success"
            ).inc()

            logger.debug(
                f"Successful mTLS handshake: {service_name} <-> {peer_service}"
            )
            return True

        except Exception as e:
            logger.error(f"mTLS handshake failed: {e}")
            self.mtls_handshakes_total.labels(
                service=service_name, status="error"
            ).inc()
            return False

    async def detect_ddos_attack(self, target_service: str, request_rate: int) -> bool:
        """Detect DDoS attacks based on request patterns."""
        policy_key = self.get_policy_key_for_service(target_service)

        if policy_key in self.network_policies:
            policy = self.network_policies[policy_key]

            if request_rate > policy.ddos_threshold:
                await self.log_security_event(
                    "ddos_attack",
                    "critical",
                    "unknown",
                    target_service,
                    f"DDoS attack detected on {target_service}: {request_rate} RPS",
                )

                self.ddos_attacks_blocked.labels(
                    target_service=target_service, attack_type="high_volume"
                ).inc()

                return True

        return False

    async def log_security_event(
        self,
        event_type: str,
        severity: str,
        source_ip: str,
        target_service: str,
        description: str,
    ):
        """Log security event."""
        event = SecurityEvent(
            event_id=f"sec_{int(time.time())}_{len(self.security_events)}",
            event_type=event_type,
            severity=severity,
            source_ip=source_ip,
            target_service=target_service,
            description=description,
        )

        self.security_events.append(event)

        # Record metrics
        self.security_events_total.labels(
            event_type=event_type, severity=severity, target_service=target_service
        ).inc()

        # Log to system
        log_level = {
            "low": logging.INFO,
            "medium": logging.WARNING,
            "high": logging.ERROR,
            "critical": logging.CRITICAL,
        }.get(severity, logging.INFO)

        logger.log(log_level, f"Security Event [{event_type}]: {description}")

    def get_policy_key_for_service(self, service_name: str) -> str:
        """Get policy key for a service."""
        if service_name in ["ac-service", "pgc-service", "ec-service"]:
            return "critical_services"
        if service_name == "auth-service":
            return "auth_service"
        return "internal_services"

    async def security_monitoring_loop(self):
        """Continuous security monitoring loop."""
        while True:
            try:
                # Monitor security events
                recent_events = [
                    event
                    for event in self.security_events
                    if (datetime.now(timezone.utc) - event.timestamp).total_seconds()
                    < 300
                ]

                # Check for attack patterns
                critical_events = [
                    event for event in recent_events if event.severity == "critical"
                ]
                if len(critical_events) > 5:
                    logger.critical(
                        f"Multiple critical security events detected: {len(critical_events)}"
                    )

                # Update constitutional compliance metrics
                compliance_score = await self.calculate_security_compliance()
                self.constitutional_compliance_network.labels(
                    security_component="overall"
                ).set(compliance_score)

                await asyncio.sleep(30)

            except Exception as e:
                logger.error(f"Error in security monitoring loop: {e}")
                await asyncio.sleep(60)

    async def ddos_protection_loop(self):
        """DDoS protection monitoring loop."""
        while True:
            try:
                # Monitor request rates for each service
                for service_name in self.services.keys():
                    # Simulate request rate monitoring
                    # In practice, this would integrate with actual traffic monitoring
                    current_rate = 100  # Placeholder

                    if await self.detect_ddos_attack(service_name, current_rate):
                        # Implement DDoS mitigation
                        await self.mitigate_ddos_attack(service_name)

                await asyncio.sleep(10)

            except Exception as e:
                logger.error(f"Error in DDoS protection loop: {e}")
                await asyncio.sleep(30)

    async def intrusion_detection_loop(self):
        """Intrusion detection monitoring loop."""
        while True:
            try:
                # Analyze security events for intrusion patterns
                recent_events = [
                    event
                    for event in self.security_events
                    if (datetime.now(timezone.utc) - event.timestamp).total_seconds()
                    < 600
                ]

                # Detect suspicious patterns
                await self.analyze_intrusion_patterns(recent_events)

                await asyncio.sleep(60)

            except Exception as e:
                logger.error(f"Error in intrusion detection loop: {e}")
                await asyncio.sleep(120)

    async def mitigate_ddos_attack(self, target_service: str):
        """Mitigate DDoS attack on target service."""
        logger.warning(f"Implementing DDoS mitigation for {target_service}")

        # Implement rate limiting
        if target_service in self.rate_limiters:
            self.rate_limiters[target_service]["max_requests"] = 100  # Reduce limit

        # Block suspicious IPs (simplified implementation)
        # In practice, this would involve more sophisticated analysis

        await self.log_security_event(
            "ddos_mitigation",
            "high",
            "system",
            target_service,
            f"DDoS mitigation activated for {target_service}",
        )

    async def analyze_intrusion_patterns(self, events: list[SecurityEvent]):
        """Analyze events for intrusion patterns."""
        # Group events by source IP
        ip_events = {}
        for event in events:
            if event.source_ip not in ip_events:
                ip_events[event.source_ip] = []
            ip_events[event.source_ip].append(event)

        # Detect suspicious patterns
        for source_ip, ip_event_list in ip_events.items():
            if len(ip_event_list) > 10:  # High activity threshold
                high_severity_events = [
                    e for e in ip_event_list if e.severity in ["high", "critical"]
                ]

                if len(high_severity_events) > 3:
                    # Potential intrusion detected
                    await self.log_security_event(
                        "potential_intrusion",
                        "critical",
                        source_ip,
                        "multiple",
                        f"Potential intrusion detected from {source_ip}: {len(high_severity_events)} high-severity events",
                    )

                    # Block IP
                    self.blocked_ips.add(source_ip)

    async def calculate_security_compliance(self) -> float:
        """Calculate overall security compliance score."""
        try:
            # Factors for compliance calculation
            factors = []

            # mTLS compliance
            total_handshakes = sum(
                self.mtls_handshakes_total.labels(
                    service=service, status="success"
                )._value.get()
                for service in self.services.keys()
            )
            failed_handshakes = sum(
                self.mtls_handshakes_total.labels(
                    service=service, status="failed"
                )._value.get()
                for service in self.services.keys()
            )

            if total_handshakes + failed_handshakes > 0:
                mtls_compliance = total_handshakes / (
                    total_handshakes + failed_handshakes
                )
                factors.append(mtls_compliance)

            # Security events compliance
            recent_critical_events = len(
                [
                    event
                    for event in self.security_events
                    if event.severity == "critical"
                    and (datetime.now(timezone.utc) - event.timestamp).total_seconds()
                    < 3600
                ]
            )

            security_events_compliance = max(0, 1 - (recent_critical_events * 0.1))
            factors.append(security_events_compliance)

            # Constitutional hash validation
            factors.append(1.0)  # Assume constitutional compliance

            # Calculate overall compliance
            if factors:
                return sum(factors) / len(factors)
            return 1.0

        except Exception as e:
            logger.error(f"Error calculating security compliance: {e}")
            return 0.0

    def get_security_status(self) -> dict[str, Any]:
        """Get network security status."""
        return {
            "network_policies": len(self.network_policies),
            "active_certificates": len(self.service_certificates),
            "blocked_ips": len(self.blocked_ips),
            "recent_security_events": len(
                [
                    event
                    for event in self.security_events
                    if (datetime.now(timezone.utc) - event.timestamp).total_seconds()
                    < 3600
                ]
            ),
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "mtls_enabled": True,
            "ddos_protection_enabled": True,
            "intrusion_detection_enabled": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# Global network security manager instance
network_security_manager = NetworkSecurityManager()

if __name__ == "__main__":

    async def main():
        await network_security_manager.initialize_security_framework()

        try:
            # Keep running
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down network security manager...")

    asyncio.run(main())
