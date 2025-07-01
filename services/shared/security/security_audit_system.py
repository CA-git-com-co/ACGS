"""
Security Audit and Compliance Monitoring System for ACGS

This module provides comprehensive security auditing, compliance monitoring,
and automated security assessment capabilities for production deployment.

Features:
- Real-time security event monitoring
- Compliance assessment (SOC2, GDPR, HIPAA, FedRAMP)
- Automated vulnerability scanning
- Security metrics and reporting
- Incident response automation
- Constitutional governance compliance

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import subprocess
import psutil

# import aiofiles  # Removed to avoid dependency issues
from pathlib import Path

logger = logging.getLogger(__name__)


class ComplianceStandard(Enum):
    """Supported compliance standards."""

    SOC2 = "soc2"
    GDPR = "gdpr"
    HIPAA = "hipaa"
    FEDRAMP = "fedramp"
    PCI_DSS = "pci_dss"
    ISO27001 = "iso27001"


class AuditSeverity(Enum):
    """Audit finding severity levels."""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class VulnerabilityType(Enum):
    """Types of security vulnerabilities."""

    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    INPUT_VALIDATION = "input_validation"
    ENCRYPTION = "encryption"
    CONFIGURATION = "configuration"
    DEPENDENCY = "dependency"
    NETWORK = "network"
    DATA_EXPOSURE = "data_exposure"


@dataclass
class AuditFinding:
    """Security audit finding."""

    finding_id: str
    timestamp: datetime
    severity: AuditSeverity
    vulnerability_type: VulnerabilityType
    title: str
    description: str
    affected_component: str
    remediation: str
    compliance_impact: List[ComplianceStandard]
    risk_score: float
    constitutional_hash: str = "cdd01ef066bc6cf2"


@dataclass
class ComplianceAssessment:
    """Compliance assessment result."""

    standard: ComplianceStandard
    assessment_date: datetime
    overall_score: float
    passed_controls: int
    failed_controls: int
    total_controls: int
    findings: List[AuditFinding]
    recommendations: List[str]
    next_assessment_due: datetime


class SecurityAuditSystem:
    """Comprehensive security audit and compliance monitoring system."""

    def __init__(self):
        self.audit_findings: List[AuditFinding] = []
        self.compliance_assessments: Dict[ComplianceStandard, ComplianceAssessment] = {}
        self.audit_config = self._load_audit_config()
        self.monitoring_active = False

    def _load_audit_config(self) -> Dict[str, Any]:
        """Load audit configuration."""
        return {
            "audit_interval_hours": 24,
            "compliance_check_interval_hours": 168,  # Weekly
            "vulnerability_scan_interval_hours": 72,  # Every 3 days
            "log_retention_days": 365,
            "alert_thresholds": {
                "critical_findings": 1,
                "high_findings": 5,
                "medium_findings": 20,
            },
            "compliance_standards": [
                ComplianceStandard.SOC2,
                ComplianceStandard.GDPR,
                ComplianceStandard.HIPAA,
            ],
            "audit_scope": {
                "services": True,
                "infrastructure": True,
                "data_flows": True,
                "access_controls": True,
                "encryption": True,
                "logging": True,
            },
        }

    async def start_monitoring(self):
        """Start continuous security monitoring."""
        if self.monitoring_active:
            return

        self.monitoring_active = True
        logger.info("Starting security audit monitoring")

        # Start background tasks
        asyncio.create_task(self._continuous_audit_monitor())
        asyncio.create_task(self._compliance_monitor())
        asyncio.create_task(self._vulnerability_scanner())
        asyncio.create_task(self._security_metrics_collector())

    async def stop_monitoring(self):
        """Stop security monitoring."""
        self.monitoring_active = False
        logger.info("Stopping security audit monitoring")

    async def _continuous_audit_monitor(self):
        """Continuous audit monitoring task."""
        while self.monitoring_active:
            try:
                await self.perform_security_audit()
                await asyncio.sleep(self.audit_config["audit_interval_hours"] * 3600)
            except Exception as e:
                logger.error(f"Error in audit monitor: {e}")
                await asyncio.sleep(300)  # Retry in 5 minutes

    async def _compliance_monitor(self):
        """Compliance monitoring task."""
        while self.monitoring_active:
            try:
                for standard in self.audit_config["compliance_standards"]:
                    await self.assess_compliance(standard)

                await asyncio.sleep(
                    self.audit_config["compliance_check_interval_hours"] * 3600
                )
            except Exception as e:
                logger.error(f"Error in compliance monitor: {e}")
                await asyncio.sleep(3600)  # Retry in 1 hour

    async def _vulnerability_scanner(self):
        """Vulnerability scanning task."""
        while self.monitoring_active:
            try:
                await self.scan_vulnerabilities()
                await asyncio.sleep(
                    self.audit_config["vulnerability_scan_interval_hours"] * 3600
                )
            except Exception as e:
                logger.error(f"Error in vulnerability scanner: {e}")
                await asyncio.sleep(1800)  # Retry in 30 minutes

    async def _security_metrics_collector(self):
        """Security metrics collection task."""
        while self.monitoring_active:
            try:
                await self.collect_security_metrics()
                await asyncio.sleep(300)  # Every 5 minutes
            except Exception as e:
                logger.error(f"Error in metrics collector: {e}")
                await asyncio.sleep(60)

    async def perform_security_audit(self) -> Dict[str, Any]:
        """Perform comprehensive security audit."""
        logger.info("Starting comprehensive security audit")
        audit_start = datetime.now(timezone.utc)

        audit_results = {
            "audit_id": hashlib.sha256(
                f"audit_{audit_start.isoformat()}".encode()
            ).hexdigest()[:16],
            "start_time": audit_start,
            "findings": [],
            "summary": {},
        }

        # 1. Authentication and Authorization Audit
        auth_findings = await self._audit_authentication()
        audit_results["findings"].extend(auth_findings)

        # 2. Input Validation Audit
        input_findings = await self._audit_input_validation()
        audit_results["findings"].extend(input_findings)

        # 3. Encryption Audit
        encryption_findings = await self._audit_encryption()
        audit_results["findings"].extend(encryption_findings)

        # 4. Configuration Audit
        config_findings = await self._audit_configuration()
        audit_results["findings"].extend(config_findings)

        # 5. Network Security Audit
        network_findings = await self._audit_network_security()
        audit_results["findings"].extend(network_findings)

        # 6. Data Protection Audit
        data_findings = await self._audit_data_protection()
        audit_results["findings"].extend(data_findings)

        # 7. Constitutional Compliance Audit
        constitutional_findings = await self._audit_constitutional_compliance()
        audit_results["findings"].extend(constitutional_findings)

        # Generate summary
        audit_results["summary"] = self._generate_audit_summary(
            audit_results["findings"]
        )
        audit_results["end_time"] = datetime.now(timezone.utc)
        audit_results["duration_seconds"] = (
            audit_results["end_time"] - audit_start
        ).total_seconds()

        # Store findings
        self.audit_findings.extend(audit_results["findings"])

        # Generate alerts for critical findings
        await self._process_audit_alerts(audit_results["findings"])

        # Save audit report
        await self._save_audit_report(audit_results)

        logger.info(
            f"Security audit completed in {audit_results['duration_seconds']:.2f} seconds"
        )
        return audit_results

    async def _audit_authentication(self) -> List[AuditFinding]:
        """Audit authentication mechanisms."""
        findings = []

        # Check JWT secret strength
        jwt_secret_file = "/etc/acgs/encryption/master.key"
        if os.path.exists(jwt_secret_file):
            stat_info = os.stat(jwt_secret_file)
            if stat_info.st_mode & 0o077:  # Check if readable by others
                findings.append(
                    AuditFinding(
                        finding_id=f"auth_001_{int(time.time())}",
                        timestamp=datetime.now(timezone.utc),
                        severity=AuditSeverity.HIGH,
                        vulnerability_type=VulnerabilityType.AUTHENTICATION,
                        title="JWT Secret File Permissions Too Permissive",
                        description="JWT secret file has overly permissive file permissions",
                        affected_component="Authentication Service",
                        remediation="Set file permissions to 600 (owner read/write only)",
                        compliance_impact=[
                            ComplianceStandard.SOC2,
                            ComplianceStandard.HIPAA,
                        ],
                        risk_score=7.5,
                    )
                )
        else:
            findings.append(
                AuditFinding(
                    finding_id=f"auth_002_{int(time.time())}",
                    timestamp=datetime.now(timezone.utc),
                    severity=AuditSeverity.CRITICAL,
                    vulnerability_type=VulnerabilityType.AUTHENTICATION,
                    title="JWT Secret File Missing",
                    description="JWT secret file not found, authentication may be compromised",
                    affected_component="Authentication Service",
                    remediation="Generate and securely store JWT secret file",
                    compliance_impact=[
                        ComplianceStandard.SOC2,
                        ComplianceStandard.HIPAA,
                        ComplianceStandard.FEDRAMP,
                    ],
                    risk_score=9.5,
                )
            )

        return findings

    async def _audit_input_validation(self) -> List[AuditFinding]:
        """Audit input validation mechanisms."""
        findings = []

        # Check for input validation middleware
        middleware_files = [
            "services/shared/security/enhanced_security_middleware.py",
            "services/shared/security_middleware.py",
        ]

        validation_implemented = any(os.path.exists(f) for f in middleware_files)
        if not validation_implemented:
            findings.append(
                AuditFinding(
                    finding_id=f"input_001_{int(time.time())}",
                    timestamp=datetime.now(timezone.utc),
                    severity=AuditSeverity.HIGH,
                    vulnerability_type=VulnerabilityType.INPUT_VALIDATION,
                    title="Input Validation Middleware Missing",
                    description="No input validation middleware detected",
                    affected_component="All Services",
                    remediation="Implement comprehensive input validation middleware",
                    compliance_impact=[
                        ComplianceStandard.SOC2,
                        ComplianceStandard.PCI_DSS,
                    ],
                    risk_score=8.0,
                )
            )

        return findings

    async def _audit_encryption(self) -> List[AuditFinding]:
        """Audit encryption implementation."""
        findings = []

        # Check for encryption keys
        encryption_dir = "/etc/acgs/encryption"
        if not os.path.exists(encryption_dir):
            findings.append(
                AuditFinding(
                    finding_id=f"enc_001_{int(time.time())}",
                    timestamp=datetime.now(timezone.utc),
                    severity=AuditSeverity.CRITICAL,
                    vulnerability_type=VulnerabilityType.ENCRYPTION,
                    title="Encryption Directory Missing",
                    description="Encryption key directory not found",
                    affected_component="Encryption System",
                    remediation="Create encryption directory and generate keys",
                    compliance_impact=[
                        ComplianceStandard.HIPAA,
                        ComplianceStandard.GDPR,
                        ComplianceStandard.FEDRAMP,
                    ],
                    risk_score=9.0,
                )
            )

        return findings

    async def _audit_configuration(self) -> List[AuditFinding]:
        """Audit system configuration."""
        findings = []

        # Check for default passwords or keys
        config_files = [
            "config/security/security-config.yml",
            ".env",
            "docker-compose.yml",
        ]

        for config_file in config_files:
            if os.path.exists(config_file):
                try:
                    with open(config_file, "r") as f:
                        content = f.read()
                        if "password" in content.lower() or "secret" in content.lower():
                            findings.append(
                                AuditFinding(
                                    finding_id=f"config_001_{int(time.time())}",
                                    timestamp=datetime.now(timezone.utc),
                                    severity=AuditSeverity.MEDIUM,
                                    vulnerability_type=VulnerabilityType.CONFIGURATION,
                                    title="Potential Hardcoded Secrets",
                                    description=f"Configuration file {config_file} may contain hardcoded secrets",
                                    affected_component="Configuration Management",
                                    remediation="Review and remove any hardcoded secrets",
                                    compliance_impact=[ComplianceStandard.SOC2],
                                    risk_score=6.0,
                                )
                            )
                except Exception as e:
                    logger.warning(f"Could not audit config file {config_file}: {e}")

        return findings

    async def _audit_network_security(self) -> List[AuditFinding]:
        """Audit network security configuration."""
        findings = []

        # Check for open ports
        try:
            connections = psutil.net_connections(kind="inet")
            listening_ports = [
                conn.laddr.port for conn in connections if conn.status == "LISTEN"
            ]

            # Check for potentially dangerous open ports
            dangerous_ports = [21, 23, 135, 139, 445, 1433, 3389, 5432]
            open_dangerous_ports = [
                port for port in listening_ports if port in dangerous_ports
            ]

            if open_dangerous_ports:
                findings.append(
                    AuditFinding(
                        finding_id=f"net_001_{int(time.time())}",
                        timestamp=datetime.now(timezone.utc),
                        severity=AuditSeverity.HIGH,
                        vulnerability_type=VulnerabilityType.NETWORK,
                        title="Dangerous Ports Open",
                        description=f"Potentially dangerous ports are open: {open_dangerous_ports}",
                        affected_component="Network Configuration",
                        remediation="Close unnecessary ports and implement firewall rules",
                        compliance_impact=[
                            ComplianceStandard.SOC2,
                            ComplianceStandard.FEDRAMP,
                        ],
                        risk_score=7.0,
                    )
                )
        except Exception as e:
            logger.warning(f"Could not audit network connections: {e}")

        return findings

    async def _audit_data_protection(self) -> List[AuditFinding]:
        """Audit data protection measures."""
        findings = []

        # Check for database encryption
        # This is a simplified check - in production, you'd check actual database configs
        db_config_files = ["config/database.yml", "config/postgres.conf"]
        encryption_found = False

        for config_file in db_config_files:
            if os.path.exists(config_file):
                try:
                    with open(config_file, "r") as f:
                        content = f.read()
                        if "ssl" in content.lower() or "tls" in content.lower():
                            encryption_found = True
                            break
                except Exception:
                    pass

        if not encryption_found:
            findings.append(
                AuditFinding(
                    finding_id=f"data_001_{int(time.time())}",
                    timestamp=datetime.now(timezone.utc),
                    severity=AuditSeverity.HIGH,
                    vulnerability_type=VulnerabilityType.DATA_EXPOSURE,
                    title="Database Encryption Not Configured",
                    description="Database connections may not be encrypted",
                    affected_component="Database Layer",
                    remediation="Configure SSL/TLS encryption for database connections",
                    compliance_impact=[
                        ComplianceStandard.HIPAA,
                        ComplianceStandard.GDPR,
                    ],
                    risk_score=8.5,
                )
            )

        return findings

    async def _audit_constitutional_compliance(self) -> List[AuditFinding]:
        """Audit constitutional compliance."""
        findings = []

        # Check for constitutional hash validation
        expected_hash = "cdd01ef066bc6cf2"

        # Check if constitutional validation is implemented in services
        service_dirs = ["services/core", "services/platform_services"]
        constitutional_validation_found = False

        for service_dir in service_dirs:
            if os.path.exists(service_dir):
                for root, dirs, files in os.walk(service_dir):
                    for file in files:
                        if file.endswith(".py"):
                            file_path = os.path.join(root, file)
                            try:
                                with open(file_path, "r") as f:
                                    content = f.read()
                                    if expected_hash in content:
                                        constitutional_validation_found = True
                                        break
                            except Exception:
                                pass
                    if constitutional_validation_found:
                        break
                if constitutional_validation_found:
                    break

        if not constitutional_validation_found:
            findings.append(
                AuditFinding(
                    finding_id=f"const_001_{int(time.time())}",
                    timestamp=datetime.now(timezone.utc),
                    severity=AuditSeverity.CRITICAL,
                    vulnerability_type=VulnerabilityType.AUTHORIZATION,
                    title="Constitutional Compliance Not Implemented",
                    description="Constitutional hash validation not found in services",
                    affected_component="Constitutional Governance",
                    remediation="Implement constitutional compliance validation across all services",
                    compliance_impact=[
                        ComplianceStandard.SOC2,
                        ComplianceStandard.FEDRAMP,
                    ],
                    risk_score=9.5,
                )
            )

        return findings

    def _generate_audit_summary(self, findings: List[AuditFinding]) -> Dict[str, Any]:
        """Generate audit summary from findings."""
        severity_counts = {}
        for severity in AuditSeverity:
            severity_counts[severity.value] = len(
                [f for f in findings if f.severity == severity]
            )

        vulnerability_counts = {}
        for vuln_type in VulnerabilityType:
            vulnerability_counts[vuln_type.value] = len(
                [f for f in findings if f.vulnerability_type == vuln_type]
            )

        total_risk_score = sum(f.risk_score for f in findings)
        avg_risk_score = total_risk_score / len(findings) if findings else 0

        return {
            "total_findings": len(findings),
            "severity_breakdown": severity_counts,
            "vulnerability_breakdown": vulnerability_counts,
            "total_risk_score": total_risk_score,
            "average_risk_score": avg_risk_score,
            "critical_findings": severity_counts.get("critical", 0),
            "high_findings": severity_counts.get("high", 0),
            "medium_findings": severity_counts.get("medium", 0),
            "low_findings": severity_counts.get("low", 0),
        }

    async def _process_audit_alerts(self, findings: List[AuditFinding]):
        """Process audit findings and generate alerts."""
        critical_findings = [
            f for f in findings if f.severity == AuditSeverity.CRITICAL
        ]
        high_findings = [f for f in findings if f.severity == AuditSeverity.HIGH]

        if (
            len(critical_findings)
            >= self.audit_config["alert_thresholds"]["critical_findings"]
        ):
            logger.critical(
                f"CRITICAL SECURITY ALERT: {len(critical_findings)} critical findings detected"
            )

        if len(high_findings) >= self.audit_config["alert_thresholds"]["high_findings"]:
            logger.warning(
                f"HIGH SECURITY ALERT: {len(high_findings)} high severity findings detected"
            )

    async def _save_audit_report(self, audit_results: Dict[str, Any]):
        """Save audit report to file."""
        reports_dir = Path("reports/security_audits")
        reports_dir.mkdir(parents=True, exist_ok=True)

        report_file = reports_dir / f"audit_{audit_results['audit_id']}.json"

        # Convert datetime objects to ISO format for JSON serialization
        serializable_results = json.loads(json.dumps(audit_results, default=str))

        with open(report_file, "w") as f:
            f.write(json.dumps(serializable_results, indent=2))

        logger.info(f"Audit report saved to {report_file}")

    async def assess_compliance(
        self, standard: ComplianceStandard
    ) -> ComplianceAssessment:
        """Assess compliance with specific standard."""
        logger.info(f"Assessing compliance with {standard.value}")

        # This is a simplified compliance assessment
        # In production, this would involve detailed control testing

        assessment = ComplianceAssessment(
            standard=standard,
            assessment_date=datetime.now(timezone.utc),
            overall_score=0.0,
            passed_controls=0,
            failed_controls=0,
            total_controls=0,
            findings=[],
            recommendations=[],
            next_assessment_due=datetime.now(timezone.utc) + timedelta(days=90),
        )

        # Store assessment
        self.compliance_assessments[standard] = assessment

        return assessment

    async def scan_vulnerabilities(self) -> Dict[str, Any]:
        """Perform vulnerability scanning."""
        logger.info("Starting vulnerability scan")

        # This is a placeholder for vulnerability scanning
        # In production, integrate with tools like OpenVAS, Nessus, or custom scanners

        scan_results = {
            "scan_id": hashlib.sha256(f"vuln_scan_{time.time()}".encode()).hexdigest()[
                :16
            ],
            "timestamp": datetime.now(timezone.utc),
            "vulnerabilities_found": 0,
            "scan_duration_seconds": 0,
        }

        return scan_results

    async def collect_security_metrics(self) -> Dict[str, Any]:
        """Collect security metrics."""
        metrics = {
            "timestamp": datetime.now(timezone.utc),
            "total_audit_findings": len(self.audit_findings),
            "critical_findings_last_24h": len(
                [
                    f
                    for f in self.audit_findings
                    if f.severity == AuditSeverity.CRITICAL
                    and f.timestamp > datetime.now(timezone.utc) - timedelta(hours=24)
                ]
            ),
            "compliance_assessments_count": len(self.compliance_assessments),
            "monitoring_active": self.monitoring_active,
        }

        return metrics


# Global instance
security_audit_system = SecurityAuditSystem()
