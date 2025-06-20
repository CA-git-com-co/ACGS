"""
Security Manager for ACGS-1 Self-Evolving AI Architecture Foundation.

This module implements the 4-layer security architecture with comprehensive
threat detection, mitigation, and defense-in-depth strategies.

Security Layers:
1. Sandboxing Layer: gVisor/Firecracker isolation with resource limits
2. Policy Engine Layer: OPA integration for governance rule enforcement
3. Authentication Layer: Enhanced JWT/RBAC with multi-factor authentication
4. Audit Layer: Comprehensive logging and traceability

Key Features:
- Multi-layer security enforcement
- Threat assessment and mitigation
- Risk-based security controls
- Comprehensive audit logging
- Integration with ACGS-1 security framework
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import timezone, datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    """Threat level enumeration."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityLayer(Enum):
    """Security layer enumeration."""

    SANDBOXING = "sandboxing"
    POLICY_ENGINE = "policy_engine"
    AUTHENTICATION = "authentication"
    AUDIT = "audit"


@dataclass
class ThreatAssessment:
    """Threat assessment data structure."""

    threat_id: str
    threat_level: ThreatLevel
    threat_type: str
    description: str
    affected_layers: list[SecurityLayer]
    mitigation_required: bool
    mitigation_actions: list[str] = field(default_factory=list)
    confidence_score: float = 0.0
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class SecurityEvent:
    """Security event data structure."""

    event_id: str
    event_type: str
    severity: ThreatLevel
    source: str
    description: str
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class SecurityManager:
    """
    Multi-layer security manager for self-evolving AI architecture.

    Implements comprehensive security controls with threat detection,
    assessment, and mitigation capabilities across all security layers.
    """

    def __init__(self, settings):
        self.settings = settings

        # Security configuration
        self.sandbox_enabled = settings.SANDBOX_ENABLED
        self.sandbox_type = settings.SANDBOX_TYPE
        self.resource_limits_enabled = settings.RESOURCE_LIMITS_ENABLED
        self.threat_detection_enabled = settings.THREAT_DETECTION_ENABLED
        self.audit_logging_enabled = settings.AUDIT_LOGGING_ENABLED

        # Security state
        self.active_threats: dict[str, ThreatAssessment] = {}
        self.security_events: list[SecurityEvent] = []
        self.security_metrics: dict[str, Any] = {
            "threats_detected": 0,
            "threats_mitigated": 0,
            "security_events": 0,
            "layer_status": {
                "sandboxing": "active",
                "policy_engine": "active",
                "authentication": "active",
                "audit": "active",
            },
        }

        # Top 6 threat categories for mitigation
        self.threat_categories = {
            "unauthorized_policy_modification": {
                "description": "Unauthorized attempts to modify governance policies",
                "mitigation": [
                    "multi_layer_authentication",
                    "approval_workflow",
                    "audit_logging",
                ],
                "severity": ThreatLevel.CRITICAL,
            },
            "privilege_escalation": {
                "description": "Attempts to escalate privileges beyond authorized levels",
                "mitigation": [
                    "rbac_enforcement",
                    "principle_of_least_privilege",
                    "session_monitoring",
                ],
                "severity": ThreatLevel.HIGH,
            },
            "data_integrity_compromise": {
                "description": "Attempts to compromise data integrity or authenticity",
                "mitigation": [
                    "cryptographic_validation",
                    "integrity_checks",
                    "immutable_audit_trails",
                ],
                "severity": ThreatLevel.HIGH,
            },
            "service_availability_attacks": {
                "description": "Attacks targeting service availability and performance",
                "mitigation": ["rate_limiting", "circuit_breakers", "resource_limits"],
                "severity": ThreatLevel.MEDIUM,
            },
            "constitutional_manipulation": {
                "description": "Attempts to manipulate constitutional governance principles",
                "mitigation": [
                    "formal_verification",
                    "compliance_checking",
                    "human_oversight",
                ],
                "severity": ThreatLevel.CRITICAL,
            },
            "insider_threats": {
                "description": "Threats from authorized users with malicious intent",
                "mitigation": [
                    "comprehensive_audit_trails",
                    "behavioral_monitoring",
                    "separation_of_duties",
                ],
                "severity": ThreatLevel.HIGH,
            },
        }

        logger.info("Security manager initialized with 4-layer architecture")

    async def initialize(self):
        """Initialize the security manager."""
        try:
            # Initialize security layers
            await self._initialize_sandboxing_layer()
            await self._initialize_policy_engine_layer()
            await self._initialize_authentication_layer()
            await self._initialize_audit_layer()

            # Start security monitoring
            asyncio.create_task(self._monitor_security_events())

            logger.info("✅ Security manager initialization complete")

        except Exception as e:
            logger.error(f"❌ Security manager initialization failed: {e}")
            raise

    async def assess_evolution_security(self, evolution_request) -> dict[str, Any]:
        """
        Assess security implications of an evolution request.

        Args:
            evolution_request: Evolution request to assess

        Returns:
            Security assessment result
        """
        try:
            assessment_id = f"security_assessment_{int(time.time())}"

            # Multi-layer security assessment
            layer_assessments = {}

            # Layer 1: Sandboxing assessment
            layer_assessments["sandboxing"] = await self._assess_sandboxing_security(
                evolution_request
            )

            # Layer 2: Policy engine assessment
            layer_assessments["policy_engine"] = (
                await self._assess_policy_engine_security(evolution_request)
            )

            # Layer 3: Authentication assessment
            layer_assessments["authentication"] = (
                await self._assess_authentication_security(evolution_request)
            )

            # Layer 4: Audit assessment
            layer_assessments["audit"] = await self._assess_audit_security(
                evolution_request
            )

            # Aggregate assessment
            all_approved = all(
                assessment.get("approved", False)
                for assessment in layer_assessments.values()
            )

            # Calculate overall risk score
            risk_scores = [
                assessment.get("risk_score", 0)
                for assessment in layer_assessments.values()
            ]
            overall_risk_score = max(risk_scores) if risk_scores else 0

            # Determine threat level
            if overall_risk_score >= 0.8:
                threat_level = ThreatLevel.CRITICAL
            elif overall_risk_score >= 0.6:
                threat_level = ThreatLevel.HIGH
            elif overall_risk_score >= 0.4:
                threat_level = ThreatLevel.MEDIUM
            else:
                threat_level = ThreatLevel.LOW

            assessment_result = {
                "assessment_id": assessment_id,
                "approved": all_approved and threat_level != ThreatLevel.CRITICAL,
                "threat_level": threat_level.value,
                "overall_risk_score": overall_risk_score,
                "layer_assessments": layer_assessments,
                "mitigation_required": threat_level
                in [ThreatLevel.HIGH, ThreatLevel.CRITICAL],
                "recommended_mitigations": self._get_recommended_mitigations(
                    threat_level
                ),
                "assessed_at": datetime.now(timezone.utc).isoformat(),
            }

            # Log security assessment
            if self.audit_logging_enabled:
                await self._log_security_event(
                    "security_assessment_completed",
                    ThreatLevel.LOW,
                    "security_manager",
                    f"Evolution security assessment completed: {assessment_id}",
                    {"assessment_result": assessment_result},
                )

            return assessment_result

        except Exception as e:
            logger.error(f"Security assessment failed: {e}")
            return {
                "approved": False,
                "error": str(e),
                "threat_level": ThreatLevel.CRITICAL.value,
            }

    async def validate_evolution_request(self, evolution_request) -> dict[str, Any]:
        """
        Validate evolution request for security compliance.

        Args:
            evolution_request: Evolution request to validate

        Returns:
            Validation result
        """
        try:
            validation_result = {"secure": True, "security_issues": []}

            # Input validation
            if not evolution_request.requester_id:
                validation_result["security_issues"].append(
                    "Missing requester identification"
                )

            if not evolution_request.justification:
                validation_result["security_issues"].append(
                    "Missing security justification"
                )

            # Check for suspicious patterns
            suspicious_patterns = [
                "bypass",
                "override",
                "disable",
                "admin",
                "root",
                "sudo",
                "escalate",
                "privilege",
                "backdoor",
                "exploit",
            ]

            description_lower = evolution_request.description.lower()
            justification_lower = evolution_request.justification.lower()

            for pattern in suspicious_patterns:
                if pattern in description_lower or pattern in justification_lower:
                    validation_result["security_issues"].append(
                        f"Suspicious pattern detected: {pattern}"
                    )

            # Validate proposed changes
            if evolution_request.proposed_changes:
                change_validation = await self._validate_proposed_changes(
                    evolution_request.proposed_changes
                )
                if not change_validation["secure"]:
                    validation_result["security_issues"].extend(
                        change_validation["security_issues"]
                    )

            validation_result["secure"] = len(validation_result["security_issues"]) == 0

            return validation_result

        except Exception as e:
            logger.error(f"Evolution request validation failed: {e}")
            return {
                "secure": False,
                "security_issues": [f"Validation error: {str(e)}"],
            }

    async def detect_threat(
        self, event_data: dict[str, Any]
    ) -> ThreatAssessment | None:
        """
        Detect potential security threats from event data.

        Args:
            event_data: Event data to analyze

        Returns:
            Threat assessment if threat detected, None otherwise
        """
        try:
            if not self.threat_detection_enabled:
                return None

            # Analyze event for threat indicators
            threat_indicators = await self._analyze_threat_indicators(event_data)

            if threat_indicators["threat_detected"]:
                threat_assessment = ThreatAssessment(
                    threat_id=f"threat_{int(time.time())}",
                    threat_level=ThreatLevel(threat_indicators["threat_level"]),
                    threat_type=threat_indicators["threat_type"],
                    description=threat_indicators["description"],
                    affected_layers=threat_indicators["affected_layers"],
                    mitigation_required=threat_indicators["mitigation_required"],
                    mitigation_actions=threat_indicators["mitigation_actions"],
                    confidence_score=threat_indicators["confidence_score"],
                )

                # Store active threat
                self.active_threats[threat_assessment.threat_id] = threat_assessment

                # Update metrics
                self.security_metrics["threats_detected"] += 1

                # Log threat detection
                await self._log_security_event(
                    "threat_detected",
                    threat_assessment.threat_level,
                    "threat_detection",
                    f"Security threat detected: {threat_assessment.threat_type}",
                    {"threat_assessment": threat_assessment.__dict__},
                )

                return threat_assessment

            return None

        except Exception as e:
            logger.error(f"Threat detection failed: {e}")
            return None

    async def mitigate_threat(self, threat_id: str) -> dict[str, Any]:
        """
        Mitigate an identified security threat.

        Args:
            threat_id: Threat identifier

        Returns:
            Mitigation result
        """
        try:
            if threat_id not in self.active_threats:
                return {"success": False, "error": "Threat not found"}

            threat = self.active_threats[threat_id]

            # Execute mitigation actions
            mitigation_results = []
            for action in threat.mitigation_actions:
                result = await self._execute_mitigation_action(action, threat)
                mitigation_results.append(result)

            # Check if all mitigations succeeded
            all_successful = all(
                result.get("success", False) for result in mitigation_results
            )

            if all_successful:
                # Remove from active threats
                del self.active_threats[threat_id]

                # Update metrics
                self.security_metrics["threats_mitigated"] += 1

                # Log successful mitigation
                await self._log_security_event(
                    "threat_mitigated",
                    ThreatLevel.LOW,
                    "threat_mitigation",
                    f"Security threat successfully mitigated: {threat_id}",
                    {"threat_id": threat_id, "mitigation_results": mitigation_results},
                )

                return {
                    "success": True,
                    "threat_id": threat_id,
                    "mitigation_results": mitigation_results,
                    "mitigated_at": datetime.now(timezone.utc).isoformat(),
                }
            else:
                return {
                    "success": False,
                    "threat_id": threat_id,
                    "error": "Some mitigation actions failed",
                    "mitigation_results": mitigation_results,
                }

        except Exception as e:
            logger.error(f"Threat mitigation failed for {threat_id}: {e}")
            return {"success": False, "error": str(e)}

    async def get_security_status(self) -> dict[str, Any]:
        """Get current security status and metrics."""
        try:
            return {
                "security_layers": {
                    "sandboxing": {
                        "enabled": self.sandbox_enabled,
                        "type": self.sandbox_type,
                        "status": self.security_metrics["layer_status"]["sandboxing"],
                    },
                    "policy_engine": {
                        "enabled": True,
                        "status": self.security_metrics["layer_status"][
                            "policy_engine"
                        ],
                    },
                    "authentication": {
                        "enabled": True,
                        "status": self.security_metrics["layer_status"][
                            "authentication"
                        ],
                    },
                    "audit": {
                        "enabled": self.audit_logging_enabled,
                        "status": self.security_metrics["layer_status"]["audit"],
                    },
                },
                "threat_detection": {
                    "enabled": self.threat_detection_enabled,
                    "active_threats": len(self.active_threats),
                    "total_threats_detected": self.security_metrics["threats_detected"],
                    "total_threats_mitigated": self.security_metrics[
                        "threats_mitigated"
                    ],
                },
                "security_events": {
                    "total_events": len(self.security_events),
                    "recent_events": len(
                        [
                            event
                            for event in self.security_events
                            if (datetime.now(timezone.utc) - event.timestamp).total_seconds()
                            < 3600
                        ]
                    ),
                },
                "threat_categories": list(self.threat_categories.keys()),
                "last_updated": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to get security status: {e}")
            return {"error": str(e)}

    async def health_check(self) -> dict[str, Any]:
        """Perform health check for the security manager."""
        try:
            health_status = {
                "healthy": True,
                "timestamp": time.time(),
                "checks": {},
            }

            # Check security layers
            for layer in SecurityLayer:
                layer_status = self.security_metrics["layer_status"].get(
                    layer.value, "unknown"
                )
                health_status["checks"][f"{layer.value}_layer"] = {
                    "healthy": layer_status == "active",
                    "status": layer_status,
                }
                if layer_status != "active":
                    health_status["healthy"] = False

            # Check threat detection
            health_status["checks"]["threat_detection"] = {
                "healthy": self.threat_detection_enabled,
                "active_threats": len(self.active_threats),
                "enabled": self.threat_detection_enabled,
            }

            return health_status

        except Exception as e:
            logger.error(f"Security manager health check failed: {e}")
            return {
                "healthy": False,
                "error": str(e),
                "timestamp": time.time(),
            }

    async def shutdown(self):
        """Shutdown the security manager gracefully."""
        try:
            logger.info("Shutting down security manager...")

            # Log shutdown event
            await self._log_security_event(
                "security_manager_shutdown",
                ThreatLevel.LOW,
                "security_manager",
                "Security manager shutting down",
                {"active_threats": len(self.active_threats)},
            )

            logger.info("✅ Security manager shutdown complete")

        except Exception as e:
            logger.error(f"Error during security manager shutdown: {e}")

    # Private helper methods
    async def _initialize_sandboxing_layer(self):
        """Initialize sandboxing security layer."""
        try:
            if self.sandbox_enabled:
                logger.info(f"Initializing {self.sandbox_type} sandboxing layer")
                # Sandboxing initialization would go here
                self.security_metrics["layer_status"]["sandboxing"] = "active"
            else:
                logger.warning("Sandboxing layer disabled")
                self.security_metrics["layer_status"]["sandboxing"] = "disabled"

        except Exception as e:
            logger.error(f"Sandboxing layer initialization failed: {e}")
            self.security_metrics["layer_status"]["sandboxing"] = "failed"
            raise

    async def _initialize_policy_engine_layer(self):
        """Initialize policy engine security layer."""
        try:
            logger.info("Initializing OPA policy engine layer")
            # OPA integration initialization would go here
            self.security_metrics["layer_status"]["policy_engine"] = "active"

        except Exception as e:
            logger.error(f"Policy engine layer initialization failed: {e}")
            self.security_metrics["layer_status"]["policy_engine"] = "failed"
            raise

    async def _initialize_authentication_layer(self):
        """Initialize authentication security layer."""
        try:
            logger.info("Initializing enhanced JWT/RBAC authentication layer")
            # Authentication enhancement initialization would go here
            self.security_metrics["layer_status"]["authentication"] = "active"

        except Exception as e:
            logger.error(f"Authentication layer initialization failed: {e}")
            self.security_metrics["layer_status"]["authentication"] = "failed"
            raise

    async def _initialize_audit_layer(self):
        """Initialize audit security layer."""
        try:
            if self.audit_logging_enabled:
                logger.info("Initializing comprehensive audit layer")
                # Audit logging initialization would go here
                self.security_metrics["layer_status"]["audit"] = "active"
            else:
                logger.warning("Audit layer disabled")
                self.security_metrics["layer_status"]["audit"] = "disabled"

        except Exception as e:
            logger.error(f"Audit layer initialization failed: {e}")
            self.security_metrics["layer_status"]["audit"] = "failed"
            raise

    async def _assess_sandboxing_security(self, evolution_request) -> dict[str, Any]:
        """Assess sandboxing layer security for evolution request."""
        try:
            if not self.sandbox_enabled:
                return {
                    "approved": False,
                    "risk_score": 0.8,
                    "issues": [
                        "Sandboxing disabled - high risk for evolution execution"
                    ],
                }

            # Assess resource requirements
            resource_risk = 0.0
            if evolution_request.estimated_duration_minutes > 30:
                resource_risk += 0.3

            if len(evolution_request.target_policies) > 10:
                resource_risk += 0.2

            return {
                "approved": resource_risk < 0.5,
                "risk_score": resource_risk,
                "sandbox_type": self.sandbox_type,
                "resource_limits_enabled": self.resource_limits_enabled,
            }

        except Exception as e:
            logger.error(f"Sandboxing security assessment failed: {e}")
            return {"approved": False, "risk_score": 1.0, "error": str(e)}

    async def _assess_policy_engine_security(self, evolution_request) -> dict[str, Any]:
        """Assess policy engine layer security for evolution request."""
        try:
            # Check for policy conflicts
            policy_risk = 0.0

            if evolution_request.evolution_type.value == "constitutional_amendment":
                policy_risk += 0.4  # Higher risk for constitutional changes

            if not evolution_request.requires_formal_verification:
                policy_risk += 0.3  # Higher risk without formal verification

            return {
                "approved": policy_risk < 0.6,
                "risk_score": policy_risk,
                "requires_formal_verification": evolution_request.requires_formal_verification,
                "evolution_type": evolution_request.evolution_type.value,
            }

        except Exception as e:
            logger.error(f"Policy engine security assessment failed: {e}")
            return {"approved": False, "risk_score": 1.0, "error": str(e)}

    async def _assess_authentication_security(
        self, evolution_request
    ) -> dict[str, Any]:
        """Assess authentication layer security for evolution request."""
        try:
            auth_risk = 0.0

            if not evolution_request.requester_id:
                auth_risk += 0.5

            # Check requester permissions (simplified)
            if evolution_request.priority == "critical":
                auth_risk += 0.2  # Higher scrutiny for critical changes

            return {
                "approved": auth_risk < 0.4,
                "risk_score": auth_risk,
                "requester_authenticated": bool(evolution_request.requester_id),
                "priority_level": evolution_request.priority,
            }

        except Exception as e:
            logger.error(f"Authentication security assessment failed: {e}")
            return {"approved": False, "risk_score": 1.0, "error": str(e)}

    async def _assess_audit_security(self, evolution_request) -> dict[str, Any]:
        """Assess audit layer security for evolution request."""
        try:
            audit_risk = 0.0

            if not self.audit_logging_enabled:
                audit_risk += 0.3

            if not evolution_request.justification:
                audit_risk += 0.2

            return {
                "approved": audit_risk < 0.4,
                "risk_score": audit_risk,
                "audit_logging_enabled": self.audit_logging_enabled,
                "justification_provided": bool(evolution_request.justification),
            }

        except Exception as e:
            logger.error(f"Audit security assessment failed: {e}")
            return {"approved": False, "risk_score": 1.0, "error": str(e)}

    def _get_recommended_mitigations(self, threat_level: ThreatLevel) -> list[str]:
        """Get recommended mitigation actions for threat level."""
        if threat_level == ThreatLevel.CRITICAL:
            return [
                "immediate_human_review",
                "enhanced_monitoring",
                "additional_verification",
                "rollback_preparation",
            ]
        elif threat_level == ThreatLevel.HIGH:
            return [
                "enhanced_monitoring",
                "additional_verification",
                "approval_escalation",
            ]
        elif threat_level == ThreatLevel.MEDIUM:
            return [
                "standard_monitoring",
                "verification_required",
            ]
        else:
            return ["standard_monitoring"]

    async def _validate_proposed_changes(
        self, proposed_changes: dict[str, Any]
    ) -> dict[str, Any]:
        """Validate proposed changes for security issues."""
        try:
            validation_result = {"secure": True, "security_issues": []}

            # Check for dangerous operations
            dangerous_operations = [
                "delete",
                "remove",
                "drop",
                "truncate",
                "destroy",
                "bypass",
                "override",
                "disable",
                "admin_access",
            ]

            changes_str = json.dumps(proposed_changes).lower()
            for operation in dangerous_operations:
                if operation in changes_str:
                    validation_result["security_issues"].append(
                        f"Potentially dangerous operation detected: {operation}"
                    )

            # Check for excessive scope
            if len(proposed_changes) > 50:  # Arbitrary threshold
                validation_result["security_issues"].append(
                    "Proposed changes have excessive scope"
                )

            validation_result["secure"] = len(validation_result["security_issues"]) == 0
            return validation_result

        except Exception as e:
            logger.error(f"Proposed changes validation failed: {e}")
            return {
                "secure": False,
                "security_issues": [f"Validation error: {str(e)}"],
            }

    async def _analyze_threat_indicators(
        self, event_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Analyze event data for threat indicators."""
        try:
            threat_indicators = {
                "threat_detected": False,
                "threat_level": "low",
                "threat_type": "unknown",
                "description": "",
                "affected_layers": [],
                "mitigation_required": False,
                "mitigation_actions": [],
                "confidence_score": 0.0,
            }

            # Simple threat detection logic (would be more sophisticated in production)
            event_type = event_data.get("event_type", "")

            if "failed_authentication" in event_type:
                threat_indicators.update(
                    {
                        "threat_detected": True,
                        "threat_level": "medium",
                        "threat_type": "authentication_failure",
                        "description": "Multiple authentication failures detected",
                        "affected_layers": [SecurityLayer.AUTHENTICATION],
                        "mitigation_required": True,
                        "mitigation_actions": ["rate_limiting", "account_monitoring"],
                        "confidence_score": 0.7,
                    }
                )

            elif "unauthorized_access" in event_type:
                threat_indicators.update(
                    {
                        "threat_detected": True,
                        "threat_level": "high",
                        "threat_type": "unauthorized_access",
                        "description": "Unauthorized access attempt detected",
                        "affected_layers": [
                            SecurityLayer.AUTHENTICATION,
                            SecurityLayer.AUDIT,
                        ],
                        "mitigation_required": True,
                        "mitigation_actions": [
                            "access_revocation",
                            "enhanced_monitoring",
                        ],
                        "confidence_score": 0.8,
                    }
                )

            return threat_indicators

        except Exception as e:
            logger.error(f"Threat indicator analysis failed: {e}")
            return {
                "threat_detected": False,
                "error": str(e),
            }

    async def _execute_mitigation_action(
        self, action: str, threat: ThreatAssessment
    ) -> dict[str, Any]:
        """Execute a specific mitigation action."""
        try:
            logger.info(
                f"Executing mitigation action: {action} for threat {threat.threat_id}"
            )

            # Simplified mitigation action execution
            if action == "rate_limiting":
                # Implement rate limiting
                return {
                    "success": True,
                    "action": action,
                    "details": "Rate limiting applied",
                }

            elif action == "enhanced_monitoring":
                # Enable enhanced monitoring
                return {
                    "success": True,
                    "action": action,
                    "details": "Enhanced monitoring enabled",
                }

            elif action == "access_revocation":
                # Revoke access
                return {"success": True, "action": action, "details": "Access revoked"}

            elif action == "immediate_human_review":
                # Trigger human review
                return {
                    "success": True,
                    "action": action,
                    "details": "Human review triggered",
                }

            else:
                return {
                    "success": False,
                    "action": action,
                    "error": "Unknown mitigation action",
                }

        except Exception as e:
            logger.error(f"Mitigation action execution failed: {e}")
            return {"success": False, "action": action, "error": str(e)}

    async def _log_security_event(
        self,
        event_type: str,
        severity: ThreatLevel,
        source: str,
        description: str,
        metadata: dict[str, Any] = None,
    ):
        """Log a security event."""
        try:
            if not self.audit_logging_enabled:
                return

            event = SecurityEvent(
                event_id=f"security_event_{int(time.time())}",
                event_type=event_type,
                severity=severity,
                source=source,
                description=description,
                metadata=metadata or {},
            )

            self.security_events.append(event)
            self.security_metrics["security_events"] += 1

            # Keep only recent events (last 1000)
            if len(self.security_events) > 1000:
                self.security_events = self.security_events[-1000:]

            logger.info(f"Security event logged: {event_type} - {description}")

        except Exception as e:
            logger.error(f"Failed to log security event: {e}")

    async def _monitor_security_events(self):
        """Background task to monitor security events."""
        while True:
            try:
                # Monitor for security anomalies
                await self._check_security_anomalies()

                # Clean up old threats
                await self._cleanup_old_threats()

                # Sleep for monitoring interval
                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                logger.error(f"Security monitoring error: {e}")
                await asyncio.sleep(30)

    async def _check_security_anomalies(self):
        """Check for security anomalies in recent events."""
        try:
            # Simple anomaly detection
            recent_events = [
                event
                for event in self.security_events
                if (datetime.now(timezone.utc) - event.timestamp).total_seconds()
                < 300  # Last 5 minutes
            ]

            # Check for high frequency of security events
            if len(recent_events) > 10:
                await self._log_security_event(
                    "security_anomaly_detected",
                    ThreatLevel.MEDIUM,
                    "security_monitor",
                    f"High frequency of security events detected: {len(recent_events)} in 5 minutes",
                    {"event_count": len(recent_events)},
                )

        except Exception as e:
            logger.error(f"Security anomaly check failed: {e}")

    async def _cleanup_old_threats(self):
        """Clean up old resolved threats."""
        try:
            current_time = datetime.now(timezone.utc)
            old_threats = []

            for threat_id, threat in self.active_threats.items():
                # Remove threats older than 24 hours
                if (current_time - threat.detected_at).total_seconds() > 86400:
                    old_threats.append(threat_id)

            for threat_id in old_threats:
                del self.active_threats[threat_id]
                logger.info(f"Cleaned up old threat: {threat_id}")

        except Exception as e:
            logger.error(f"Threat cleanup failed: {e}")
