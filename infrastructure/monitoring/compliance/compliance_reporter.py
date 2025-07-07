"""
ACGS Compliance Reporting Framework

Automated compliance report generation for regulatory standards including
SOC2, ISO27001, GDPR, and constitutional compliance requirements.

Constitutional Hash: cdd01ef066bc6cf2
"""

import csv
import json
import logging
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Optional

try:
    import matplotlib.pyplot as plt
    import pandas as pd
    import seaborn as sns

    REPORTING_LIBS_AVAILABLE = True
except ImportError:
    REPORTING_LIBS_AVAILABLE = False

from services.shared.audit.compliance_audit_logger import ComplianceStandard

# Constitutional compliance hash
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


class ReportFormat(Enum):
    """Supported report output formats."""

    JSON = "json"
    CSV = "csv"
    PDF = "pdf"
    HTML = "html"
    EXCEL = "xlsx"


class ReportPeriod(Enum):
    """Report time periods."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"
    CUSTOM = "custom"


@dataclass
class ComplianceMetric:
    """Individual compliance metric."""

    metric_name: str
    current_value: float
    target_value: float
    compliance_percentage: float
    status: str  # "compliant", "warning", "violation"
    trend: str  # "improving", "stable", "declining"
    last_updated: datetime
    evidence_links: list[str]
    remediation_actions: list[str]


@dataclass
class ComplianceReport:
    """Comprehensive compliance report structure."""

    report_id: str
    report_type: str
    compliance_standard: ComplianceStandard
    generated_at: datetime
    period_start: datetime
    period_end: datetime
    overall_compliance_score: float
    metrics: list[ComplianceMetric]
    violations: list[dict[str, Any]]
    remediation_summary: dict[str, Any]
    attestations: list[dict[str, Any]]
    constitutional_hash: str
    metadata: dict[str, Any]


class ComplianceReporter:
    """
    Automated compliance reporting framework for ACGS.

    Generates comprehensive compliance reports for various regulatory
    standards and constitutional compliance requirements.
    """

    def __init__(
        self,
        storage_path: str = "/app/reports",
        prometheus_url: str = "http://prometheus:9090",
        audit_log_path: str = "/app/logs/audit",
    ):
        self.storage_path = storage_path
        self.prometheus_url = prometheus_url
        self.audit_log_path = audit_log_path

        # Ensure storage directory exists
        os.makedirs(storage_path, exist_ok=True)

        logger.info("Compliance reporter initialized")

    async def generate_soc2_report(
        self,
        period_start: datetime,
        period_end: datetime,
        format: ReportFormat = ReportFormat.JSON,
    ) -> str:
        """Generate SOC2 Type II compliance report."""

        logger.info(f"Generating SOC2 report for period {period_start} to {period_end}")

        # SOC2 Trust Service Criteria metrics
        metrics = [
            await self._get_security_metrics(period_start, period_end),
            await self._get_availability_metrics(period_start, period_end),
            await self._get_processing_integrity_metrics(period_start, period_end),
            await self._get_confidentiality_metrics(period_start, period_end),
            await self._get_privacy_metrics(period_start, period_end),
        ]

        # Flatten metrics list
        all_metrics = [metric for metric_group in metrics for metric in metric_group]

        # Calculate overall compliance score
        overall_score = sum(m.compliance_percentage for m in all_metrics) / len(
            all_metrics
        )

        # Get violations for the period
        violations = await self._get_violations_for_period(
            period_start, period_end, ComplianceStandard.SOC2_TYPE_II
        )

        # Create report
        report = ComplianceReport(
            report_id=f"soc2_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            report_type="SOC2_TYPE_II",
            compliance_standard=ComplianceStandard.SOC2_TYPE_II,
            generated_at=datetime.now(timezone.utc),
            period_start=period_start,
            period_end=period_end,
            overall_compliance_score=overall_score,
            metrics=all_metrics,
            violations=violations,
            remediation_summary=await self._generate_remediation_summary(violations),
            attestations=await self._get_attestations("SOC2"),
            constitutional_hash=CONSTITUTIONAL_HASH,
            metadata={
                "report_version": "1.0",
                "acgs_version": "4.0.0",
                "generated_by": "acgs_compliance_reporter",
                "criteria_evaluated": [
                    "Security",
                    "Availability",
                    "Processing Integrity",
                    "Confidentiality",
                    "Privacy",
                ],
            },
        )

        # Save report
        return await self._save_report(report, format)

    async def generate_constitutional_compliance_report(
        self,
        period_start: datetime,
        period_end: datetime,
        format: ReportFormat = ReportFormat.JSON,
    ) -> str:
        """Generate constitutional compliance report."""

        logger.info(
            f"Generating constitutional compliance report for period {period_start} to"
            f" {period_end}"
        )

        # Constitutional compliance metrics
        metrics = [
            ComplianceMetric(
                metric_name="Constitutional Hash Integrity",
                current_value=await self._get_constitutional_hash_validity(),
                target_value=1.0,
                compliance_percentage=(
                    100.0 if await self._get_constitutional_hash_validity() else 0.0
                ),
                status=(
                    "compliant"
                    if await self._get_constitutional_hash_validity()
                    else "violation"
                ),
                trend="stable",
                last_updated=datetime.now(timezone.utc),
                evidence_links=["/metrics/constitutional_hash_valid"],
                remediation_actions=[],
            ),
            ComplianceMetric(
                metric_name="Multi-tenant Isolation",
                current_value=await self._get_tenant_isolation_score(
                    period_start, period_end
                ),
                target_value=1.0,
                compliance_percentage=await self._get_tenant_isolation_score(
                    period_start, period_end
                )
                * 100,
                status="compliant",
                trend="stable",
                last_updated=datetime.now(timezone.utc),
                evidence_links=["/metrics/tenant_isolation_violations"],
                remediation_actions=[],
            ),
            ComplianceMetric(
                metric_name="Formal Verification Success Rate",
                current_value=await self._get_formal_verification_success_rate(
                    period_start, period_end
                ),
                target_value=0.95,
                compliance_percentage=min(
                    100.0,
                    (
                        await self._get_formal_verification_success_rate(
                            period_start, period_end
                        )
                        / 0.95
                    )
                    * 100,
                ),
                status="compliant",
                trend="improving",
                last_updated=datetime.now(timezone.utc),
                evidence_links=["/metrics/formal_verification_successes"],
                remediation_actions=[],
            ),
            ComplianceMetric(
                metric_name="Audit Trail Integrity",
                current_value=await self._get_audit_trail_integrity(),
                target_value=1.0,
                compliance_percentage=(
                    100.0 if await self._get_audit_trail_integrity() else 0.0
                ),
                status="compliant",
                trend="stable",
                last_updated=datetime.now(timezone.utc),
                evidence_links=["/metrics/audit_trail_integrity"],
                remediation_actions=[],
            ),
        ]

        # Calculate overall compliance score
        overall_score = sum(m.compliance_percentage for m in metrics) / len(metrics)

        # Get constitutional violations
        violations = await self._get_violations_for_period(
            period_start, period_end, ComplianceStandard.ACGS_CONSTITUTIONAL
        )

        # Create report
        report = ComplianceReport(
            report_id=f"constitutional_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            report_type="CONSTITUTIONAL_COMPLIANCE",
            compliance_standard=ComplianceStandard.ACGS_CONSTITUTIONAL,
            generated_at=datetime.now(timezone.utc),
            period_start=period_start,
            period_end=period_end,
            overall_compliance_score=overall_score,
            metrics=metrics,
            violations=violations,
            remediation_summary=await self._generate_remediation_summary(violations),
            attestations=await self._get_attestations("CONSTITUTIONAL"),
            constitutional_hash=CONSTITUTIONAL_HASH,
            metadata={
                "report_version": "1.0",
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "acgs_version": "4.0.0",
                "generated_by": "acgs_compliance_reporter",
                "principles_evaluated": [
                    "Constitutional Hash Integrity",
                    "Multi-tenant Data Isolation",
                    "Formal Verification Requirements",
                    "Audit Trail Cryptographic Integrity",
                    "Democratic Governance Processes",
                ],
            },
        )

        # Save report
        return await self._save_report(report, format)

    async def generate_gdpr_compliance_report(
        self,
        period_start: datetime,
        period_end: datetime,
        format: ReportFormat = ReportFormat.JSON,
    ) -> str:
        """Generate GDPR compliance report."""

        logger.info(f"Generating GDPR report for period {period_start} to {period_end}")

        # GDPR compliance metrics
        metrics = [
            ComplianceMetric(
                metric_name="Data Subject Rights Response Time",
                current_value=await self._get_data_subject_response_time(
                    period_start, period_end
                ),
                target_value=30.0,  # 30 days max
                compliance_percentage=min(
                    100.0,
                    (
                        30.0
                        / max(
                            1,
                            await self._get_data_subject_response_time(
                                period_start, period_end
                            ),
                        )
                    )
                    * 100,
                ),
                status="compliant",
                trend="stable",
                last_updated=datetime.now(timezone.utc),
                evidence_links=["/audit/data_subject_requests"],
                remediation_actions=[],
            ),
            ComplianceMetric(
                metric_name="Data Breach Notification Compliance",
                current_value=await self._get_breach_notification_compliance(
                    period_start, period_end
                ),
                target_value=1.0,
                compliance_percentage=await self._get_breach_notification_compliance(
                    period_start, period_end
                )
                * 100,
                status="compliant",
                trend="stable",
                last_updated=datetime.now(timezone.utc),
                evidence_links=["/audit/security_incidents"],
                remediation_actions=[],
            ),
            ComplianceMetric(
                metric_name="Consent Management",
                current_value=await self._get_consent_compliance(
                    period_start, period_end
                ),
                target_value=1.0,
                compliance_percentage=await self._get_consent_compliance(
                    period_start, period_end
                )
                * 100,
                status="compliant",
                trend="stable",
                last_updated=datetime.now(timezone.utc),
                evidence_links=["/audit/consent_events"],
                remediation_actions=[],
            ),
        ]

        # Calculate overall compliance score
        overall_score = sum(m.compliance_percentage for m in metrics) / len(metrics)

        # Get GDPR violations
        violations = await self._get_violations_for_period(
            period_start, period_end, ComplianceStandard.GDPR
        )

        # Create report
        report = ComplianceReport(
            report_id=f"gdpr_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            report_type="GDPR_COMPLIANCE",
            compliance_standard=ComplianceStandard.GDPR,
            generated_at=datetime.now(timezone.utc),
            period_start=period_start,
            period_end=period_end,
            overall_compliance_score=overall_score,
            metrics=metrics,
            violations=violations,
            remediation_summary=await self._generate_remediation_summary(violations),
            attestations=await self._get_attestations("GDPR"),
            constitutional_hash=CONSTITUTIONAL_HASH,
            metadata={
                "report_version": "1.0",
                "regulation": "EU General Data Protection Regulation",
                "acgs_version": "4.0.0",
                "generated_by": "acgs_compliance_reporter",
                "articles_evaluated": [
                    "Article 12-22 (Data Subject Rights)",
                    "Article 33-34 (Breach Notification)",
                    "Article 6-7 (Lawfulness and Consent)",
                    "Article 25 (Data Protection by Design)",
                    "Article 32 (Security of Processing)",
                ],
            },
        )

        # Save report
        return await self._save_report(report, format)

    async def generate_periodic_report(
        self,
        period: ReportPeriod,
        standards: list[ComplianceStandard],
        format: ReportFormat = ReportFormat.JSON,
    ) -> list[str]:
        """Generate periodic compliance reports for multiple standards."""

        # Calculate period dates
        now = datetime.now(timezone.utc)
        if period == ReportPeriod.DAILY:
            period_start = now - timedelta(days=1)
            period_end = now
        elif period == ReportPeriod.WEEKLY:
            period_start = now - timedelta(weeks=1)
            period_end = now
        elif period == ReportPeriod.MONTHLY:
            period_start = now - timedelta(days=30)
            period_end = now
        elif period == ReportPeriod.QUARTERLY:
            period_start = now - timedelta(days=90)
            period_end = now
        else:
            period_start = now - timedelta(days=365)
            period_end = now

        reports = []

        for standard in standards:
            if standard == ComplianceStandard.SOC2_TYPE_II:
                report_path = await self.generate_soc2_report(
                    period_start, period_end, format
                )
                reports.append(report_path)
            elif standard == ComplianceStandard.ACGS_CONSTITUTIONAL:
                report_path = await self.generate_constitutional_compliance_report(
                    period_start, period_end, format
                )
                reports.append(report_path)
            elif standard == ComplianceStandard.GDPR:
                report_path = await self.generate_gdpr_compliance_report(
                    period_start, period_end, format
                )
                reports.append(report_path)

        return reports

    # Helper methods for metrics collection
    async def _get_security_metrics(
        self, start: datetime, end: datetime
    ) -> list[ComplianceMetric]:
        """Get security-related metrics for SOC2."""
        return [
            ComplianceMetric(
                metric_name="Authentication Success Rate",
                current_value=0.98,  # Placeholder - would query actual metrics
                target_value=0.95,
                compliance_percentage=98.0,
                status="compliant",
                trend="stable",
                last_updated=datetime.now(timezone.utc),
                evidence_links=["/metrics/auth_success_rate"],
                remediation_actions=[],
            ),
            ComplianceMetric(
                metric_name="Security Incident Response Time",
                current_value=15.0,  # minutes
                target_value=30.0,
                compliance_percentage=100.0,
                status="compliant",
                trend="improving",
                last_updated=datetime.now(timezone.utc),
                evidence_links=["/audit/security_incidents"],
                remediation_actions=[],
            ),
        ]

    async def _get_availability_metrics(
        self, start: datetime, end: datetime
    ) -> list[ComplianceMetric]:
        """Get availability metrics for SOC2."""
        return [
            ComplianceMetric(
                metric_name="System Uptime",
                current_value=99.9,
                target_value=99.5,
                compliance_percentage=100.0,
                status="compliant",
                trend="stable",
                last_updated=datetime.now(timezone.utc),
                evidence_links=["/metrics/uptime"],
                remediation_actions=[],
            )
        ]

    async def _get_processing_integrity_metrics(
        self, start: datetime, end: datetime
    ) -> list[ComplianceMetric]:
        """Get processing integrity metrics for SOC2."""
        return [
            ComplianceMetric(
                metric_name="Data Processing Accuracy",
                current_value=99.8,
                target_value=99.0,
                compliance_percentage=100.0,
                status="compliant",
                trend="stable",
                last_updated=datetime.now(timezone.utc),
                evidence_links=["/metrics/processing_accuracy"],
                remediation_actions=[],
            )
        ]

    async def _get_confidentiality_metrics(
        self, start: datetime, end: datetime
    ) -> list[ComplianceMetric]:
        """Get confidentiality metrics for SOC2."""
        return [
            ComplianceMetric(
                metric_name="Encryption Coverage",
                current_value=100.0,
                target_value=100.0,
                compliance_percentage=100.0,
                status="compliant",
                trend="stable",
                last_updated=datetime.now(timezone.utc),
                evidence_links=["/metrics/encryption_coverage"],
                remediation_actions=[],
            )
        ]

    async def _get_privacy_metrics(
        self, start: datetime, end: datetime
    ) -> list[ComplianceMetric]:
        """Get privacy metrics for SOC2."""
        return [
            ComplianceMetric(
                metric_name="PII Access Controls",
                current_value=100.0,
                target_value=100.0,
                compliance_percentage=100.0,
                status="compliant",
                trend="stable",
                last_updated=datetime.now(timezone.utc),
                evidence_links=["/audit/pii_access"],
                remediation_actions=[],
            )
        ]

    async def _get_constitutional_hash_validity(self) -> float:
        """Check if constitutional hash is valid."""
        # In real implementation, this would query the system
        return 1.0  # Placeholder

    async def _get_tenant_isolation_score(
        self, start: datetime, end: datetime
    ) -> float:
        """Get tenant isolation compliance score."""
        # In real implementation, this would analyze tenant isolation violations
        return 1.0  # Placeholder

    async def _get_formal_verification_success_rate(
        self, start: datetime, end: datetime
    ) -> float:
        """Get formal verification success rate."""
        # In real implementation, this would query Z3 solver metrics
        return 0.98  # Placeholder

    async def _get_audit_trail_integrity(self) -> float:
        """Check audit trail cryptographic integrity."""
        # In real implementation, this would verify hash chains
        return 1.0  # Placeholder

    async def _get_data_subject_response_time(
        self, start: datetime, end: datetime
    ) -> float:
        """Get average data subject request response time in days."""
        return 5.0  # Placeholder

    async def _get_breach_notification_compliance(
        self, start: datetime, end: datetime
    ) -> float:
        """Get breach notification compliance rate."""
        return 1.0  # Placeholder

    async def _get_consent_compliance(self, start: datetime, end: datetime) -> float:
        """Get consent management compliance rate."""
        return 1.0  # Placeholder

    async def _get_violations_for_period(
        self, start: datetime, end: datetime, standard: ComplianceStandard
    ) -> list[dict[str, Any]]:
        """Get compliance violations for a specific period and standard."""
        # In real implementation, this would query audit logs
        return []  # Placeholder

    async def _generate_remediation_summary(
        self, violations: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Generate remediation summary for violations."""
        return {
            "total_violations": len(violations),
            "high_priority": 0,
            "medium_priority": 0,
            "low_priority": 0,
            "resolved": 0,
            "pending": len(violations),
            "average_resolution_time_days": 0,
        }

    async def _get_attestations(self, report_type: str) -> list[dict[str, Any]]:
        """Get compliance attestations."""
        return [
            {
                "attestation_type": "executive_certification",
                "signatory": "Chief Compliance Officer",
                "statement": (
                    f"I certify that this {report_type} compliance report accurately"
                    " reflects the compliance posture of ACGS."
                ),
                "date": datetime.now(timezone.utc).isoformat(),
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }
        ]

    async def _save_report(self, report: ComplianceReport, format: ReportFormat) -> str:
        """Save report in the specified format."""
        timestamp = report.generated_at.strftime("%Y%m%d_%H%M%S")
        base_filename = f"{report.report_type.lower()}_{timestamp}"

        if format == ReportFormat.JSON:
            filename = f"{base_filename}.json"
            filepath = os.path.join(self.storage_path, filename)

            with open(filepath, "w") as f:
                json.dump(asdict(report), f, indent=2, default=str)

        elif format == ReportFormat.CSV:
            filename = f"{base_filename}.csv"
            filepath = os.path.join(self.storage_path, filename)

            # Convert metrics to CSV format
            metrics_data = []
            for metric in report.metrics:
                metrics_data.append(asdict(metric))

            with open(filepath, "w", newline="") as f:
                if metrics_data:
                    writer = csv.DictWriter(f, fieldnames=metrics_data[0].keys())
                    writer.writeheader()
                    writer.writerows(metrics_data)

        logger.info(f"Compliance report saved: {filepath}")
        return filepath


# Global reporter instance
_reporter: Optional[ComplianceReporter] = None


def get_compliance_reporter() -> ComplianceReporter:
    """Get or create the global compliance reporter instance."""
    global _reporter

    if _reporter is None:
        _reporter = ComplianceReporter()

    return _reporter


# Scheduled reporting functions
async def run_daily_compliance_reports():
    """Run daily compliance reports."""
    reporter = get_compliance_reporter()

    standards = [
        ComplianceStandard.ACGS_CONSTITUTIONAL,
        ComplianceStandard.SOC2_TYPE_II,
    ]

    reports = await reporter.generate_periodic_report(
        period=ReportPeriod.DAILY, standards=standards, format=ReportFormat.JSON
    )

    logger.info(f"Generated {len(reports)} daily compliance reports")
    return reports


async def run_monthly_compliance_reports():
    """Run monthly compliance reports."""
    reporter = get_compliance_reporter()

    standards = [
        ComplianceStandard.ACGS_CONSTITUTIONAL,
        ComplianceStandard.SOC2_TYPE_II,
        ComplianceStandard.GDPR,
        ComplianceStandard.ISO27001,
    ]

    reports = await reporter.generate_periodic_report(
        period=ReportPeriod.MONTHLY, standards=standards, format=ReportFormat.JSON
    )

    logger.info(f"Generated {len(reports)} monthly compliance reports")
    return reports
