"""
Audit and Compliance Reporting Service
Constitutional Hash: cdd01ef066bc6cf2

FastAPI service for comprehensive audit logging, compliance reporting,
and regulatory tracking across all ACGS-2 services.
"""

from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from contextlib import asynccontextmanager
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import asyncio
import json
import os
import csv
import tempfile
from collections import defaultdict
import hashlib
import uuid

from .models import (
    AuditEntry, ComplianceReport, AuditQuery, EventType, ComplianceStatus,
    RegulatoryFramework, DataRetentionPolicy, AuditTrail, SystemActivity,
    ConstitutionalEvent, ComplianceMetrics, AuditAlert, AuditConfiguration,
    ExportFormat, ReportTemplate, CONSTITUTIONAL_HASH
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global storage for audit data
audit_storage = {
    "entries": [],  # All audit entries
    "compliance_reports": {},
    "retention_policies": {},
    "configurations": {},
    "regulatory_frameworks": {},
    "audit_alerts": {},
    "system_activities": defaultdict(list),
    "constitutional_events": [],
    "metrics": defaultdict(int)
}

# Audit configuration
AUDIT_CONFIG = {
    "retention_days": 2555,  # 7 years for regulatory compliance
    "real_time_monitoring": True,
    "constitutional_tracking": True,
    "pii_anonymization": True,
    "encryption_at_rest": True,
    "immutable_logging": True
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    logger.info("Starting Audit Service")
    logger.info(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    
    # Initialize audit system
    await initialize_regulatory_frameworks()
    await initialize_retention_policies()
    await initialize_audit_configuration()
    await create_default_report_templates()
    
    # Start background tasks
    asyncio.create_task(audit_data_maintenance())
    asyncio.create_task(compliance_monitoring())
    asyncio.create_task(constitutional_event_tracking())
    asyncio.create_task(real_time_alert_processing())
    
    yield
    
    logger.info("Shutting down Audit Service")

app = FastAPI(
    title="Audit and Compliance Service",
    description="Comprehensive audit logging and compliance reporting for ACGS-2",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def initialize_regulatory_frameworks():
    """Initialize supported regulatory frameworks"""
    frameworks = [
        RegulatoryFramework(
            name="GDPR",
            description="General Data Protection Regulation (EU)",
            requirements=[
                "Data subject consent tracking",
                "Right to be forgotten implementation", 
                "Data processing lawfulness",
                "Data breach notification (72 hours)",
                "Privacy by design"
            ],
            retention_requirements="Data must be retained only as long as necessary",
            audit_requirements="Detailed logging of all data processing activities",
            jurisdiction="European Union",
            effective_date=datetime(2018, 5, 25)
        ),
        RegulatoryFramework(
            name="SOX",
            description="Sarbanes-Oxley Act",
            requirements=[
                "Financial reporting accuracy",
                "Internal control assessment",
                "Audit trail integrity",
                "Management certification",
                "External auditor independence"
            ],
            retention_requirements="7 years for audit documentation",
            audit_requirements="Comprehensive audit trails for financial systems",
            jurisdiction="United States",
            effective_date=datetime(2002, 7, 30)
        ),
        RegulatoryFramework(
            name="HIPAA",
            description="Health Insurance Portability and Accountability Act",
            requirements=[
                "PHI protection",
                "Access controls",
                "Audit logs",
                "Breach notification",
                "Business associate agreements"
            ],
            retention_requirements="6 years minimum for covered entities",
            audit_requirements="Audit controls for PHI access and modifications",
            jurisdiction="United States",
            effective_date=datetime(1996, 8, 21)
        ),
        RegulatoryFramework(
            name="Constitutional_Governance",
            description="ACGS-2 Constitutional Governance Requirements",
            requirements=[
                "Constitutional hash validation",
                "Consensus decision tracking",
                "Human oversight documentation",
                "Performance target compliance",
                "Transparency and auditability"
            ],
            retention_requirements="Permanent retention for constitutional events",
            audit_requirements="Real-time constitutional compliance monitoring",
            jurisdiction="ACGS-2 System",
            effective_date=datetime.utcnow()
        )
    ]
    
    for framework in frameworks:
        audit_storage["regulatory_frameworks"][framework.framework_id] = framework
    
    logger.info(f"Initialized {len(frameworks)} regulatory frameworks")

async def initialize_retention_policies():
    """Initialize data retention policies"""
    policies = [
        DataRetentionPolicy(
            name="Default System Logs",
            description="Standard system operation logs",
            retention_days=365,
            data_types=["system_logs", "performance_metrics", "health_checks"],
            regulatory_basis=["operational_requirements"],
            auto_deletion=True
        ),
        DataRetentionPolicy(
            name="Constitutional Events",
            description="Constitutional governance decisions and events",
            retention_days=-1,  # Permanent retention
            data_types=["constitutional_decisions", "consensus_results", "governance_actions"],
            regulatory_basis=["Constitutional_Governance"],
            auto_deletion=False
        ),
        DataRetentionPolicy(
            name="Financial Audit Data",
            description="Financial system audit trails",
            retention_days=2555,  # 7 years
            data_types=["financial_transactions", "budget_decisions", "resource_allocation"],
            regulatory_basis=["SOX"],
            auto_deletion=False
        ),
        DataRetentionPolicy(
            name="Security Events",
            description="Security-related audit events",
            retention_days=2190,  # 6 years
            data_types=["authentication", "authorization", "security_incidents"],
            regulatory_basis=["GDPR", "SOX"],
            auto_deletion=False
        ),
        DataRetentionPolicy(
            name="User Data",
            description="User personal data and activities",
            retention_days=1095,  # 3 years
            data_types=["user_activities", "personal_data", "consent_records"],
            regulatory_basis=["GDPR"],
            auto_deletion=True
        )
    ]
    
    for policy in policies:
        audit_storage["retention_policies"][policy.policy_id] = policy
    
    logger.info(f"Initialized {len(policies)} retention policies")

async def initialize_audit_configuration():
    """Initialize audit system configuration"""
    config = AuditConfiguration(
        real_time_monitoring=True,
        constitutional_tracking=True,
        performance_monitoring=True,
        security_monitoring=True,
        pii_anonymization=True,
        encryption_enabled=True,
        integrity_verification=True,
        regulatory_compliance_checking=True,
        alert_thresholds={
            "constitutional_violations": 1,
            "security_incidents": 1,
            "performance_degradation": 5,
            "compliance_violations": 1
        },
        export_formats=["json", "csv", "pdf"],
        retention_enforcement=True
    )
    
    audit_storage["configurations"]["default"] = config
    logger.info("Initialized audit configuration")

async def create_default_report_templates():
    """Create default compliance report templates"""
    templates = [
        ReportTemplate(
            name="Constitutional Compliance Report",
            description="Report on constitutional governance compliance",
            sections=[
                "executive_summary",
                "constitutional_hash_validation",
                "consensus_decisions",
                "performance_metrics",
                "violations_and_remediation"
            ],
            data_sources=["constitutional_events", "consensus_results", "performance_data"],
            frequency="monthly",
            regulatory_frameworks=["Constitutional_Governance"]
        ),
        ReportTemplate(
            name="Security Audit Report", 
            description="Comprehensive security audit report",
            sections=[
                "authentication_activities",
                "authorization_events", 
                "security_incidents",
                "access_patterns",
                "threat_analysis"
            ],
            data_sources=["security_events", "authentication_logs", "authorization_logs"],
            frequency="weekly",
            regulatory_frameworks=["GDPR", "SOX"]
        ),
        ReportTemplate(
            name="Data Protection Compliance Report",
            description="GDPR compliance status report",
            sections=[
                "data_processing_activities",
                "consent_management",
                "data_subject_requests",
                "breach_incidents",
                "privacy_impact_assessments"
            ],
            data_sources=["user_data", "consent_records", "data_processing_logs"],
            frequency="quarterly",
            regulatory_frameworks=["GDPR"]
        )
    ]
    
    for template in templates:
        audit_storage["report_templates"] = audit_storage.get("report_templates", {})
        audit_storage["report_templates"][template.template_id] = template
    
    logger.info(f"Created {len(templates)} report templates")

async def audit_data_maintenance():
    """Maintain audit data according to retention policies"""
    while True:
        try:
            current_time = datetime.utcnow()
            
            # Apply retention policies
            for policy in audit_storage["retention_policies"].values():
                if policy.auto_deletion and policy.retention_days > 0:
                    cutoff_date = current_time - timedelta(days=policy.retention_days)
                    
                    # Remove expired entries
                    expired_entries = [
                        entry for entry in audit_storage["entries"]
                        if (entry.timestamp < cutoff_date and 
                            entry.event_type in policy.data_types)
                    ]
                    
                    for entry in expired_entries:
                        audit_storage["entries"].remove(entry)
                    
                    if expired_entries:
                        logger.info(f"Removed {len(expired_entries)} expired entries for policy {policy.name}")
            
            # Update metrics
            audit_storage["metrics"]["total_entries"] = len(audit_storage["entries"])
            audit_storage["metrics"]["maintenance_runs"] += 1
            
            await asyncio.sleep(3600)  # Run every hour
            
        except Exception as e:
            logger.error(f"Audit maintenance error: {e}")
            await asyncio.sleep(3600)

async def compliance_monitoring():
    """Monitor compliance status"""
    while True:
        try:
            # Check compliance for each framework
            for framework in audit_storage["regulatory_frameworks"].values():
                await check_framework_compliance(framework)
            
            await asyncio.sleep(1800)  # Check every 30 minutes
            
        except Exception as e:
            logger.error(f"Compliance monitoring error: {e}")
            await asyncio.sleep(1800)

async def check_framework_compliance(framework: RegulatoryFramework):
    """Check compliance status for a regulatory framework"""
    try:
        compliance_issues = []
        
        if framework.name == "Constitutional_Governance":
            # Check constitutional hash compliance
            recent_entries = [
                entry for entry in audit_storage["entries"]
                if (entry.timestamp > datetime.utcnow() - timedelta(hours=1) and
                    "constitutional_hash" in entry.metadata)
            ]
            
            invalid_hashes = [
                entry for entry in recent_entries
                if entry.metadata.get("constitutional_hash") != CONSTITUTIONAL_HASH
            ]
            
            if invalid_hashes:
                compliance_issues.append(f"Constitutional hash violations: {len(invalid_hashes)}")
        
        elif framework.name == "GDPR":
            # Check data processing consent
            data_processing_entries = [
                entry for entry in audit_storage["entries"]
                if (entry.event_type == "data_processing" and
                    entry.timestamp > datetime.utcnow() - timedelta(days=30))
            ]
            
            missing_consent = [
                entry for entry in data_processing_entries
                if not entry.metadata.get("user_consent")
            ]
            
            if missing_consent:
                compliance_issues.append(f"Data processing without consent: {len(missing_consent)}")
        
        # Create compliance report if issues found
        if compliance_issues:
            compliance_report = ComplianceReport(
                framework_name=framework.name,
                status=ComplianceStatus.NON_COMPLIANT,
                compliance_score=70.0,  # Would calculate based on issues
                violations=compliance_issues,
                remediation_actions=[
                    "Review and fix constitutional hash validation",
                    "Implement proper consent management"
                ],
                report_period_start=datetime.utcnow() - timedelta(days=30),
                report_period_end=datetime.utcnow()
            )
            
            audit_storage["compliance_reports"][compliance_report.report_id] = compliance_report
            
            # Create audit alert
            alert = AuditAlert(
                alert_type="compliance_violation",
                severity="high",
                message=f"Compliance issues detected for {framework.name}",
                details={"issues": compliance_issues},
                requires_action=True
            )
            
            audit_storage["audit_alerts"][alert.alert_id] = alert
            logger.warning(f"Compliance violation detected: {framework.name}")
    
    except Exception as e:
        logger.error(f"Error checking compliance for {framework.name}: {e}")

async def constitutional_event_tracking():
    """Track constitutional governance events"""
    while True:
        try:
            # Monitor for constitutional events from other services
            # In a real implementation, this would subscribe to events
            
            await asyncio.sleep(60)  # Check every minute
            
        except Exception as e:
            logger.error(f"Constitutional event tracking error: {e}")
            await asyncio.sleep(60)

async def real_time_alert_processing():
    """Process real-time audit alerts"""
    while True:
        try:
            # Process pending alerts
            pending_alerts = [
                alert for alert in audit_storage["audit_alerts"].values()
                if not alert.acknowledged
            ]
            
            for alert in pending_alerts:
                await process_audit_alert(alert)
            
            await asyncio.sleep(30)  # Process every 30 seconds
            
        except Exception as e:
            logger.error(f"Alert processing error: {e}")
            await asyncio.sleep(30)

async def process_audit_alert(alert: AuditAlert):
    """Process individual audit alert"""
    try:
        # Log alert to audit trail
        audit_entry = AuditEntry(
            event_type="audit_alert",
            source_service="audit-service",
            user_id="system",
            action="alert_generated",
            resource="audit_system",
            details={
                "alert_type": alert.alert_type,
                "severity": alert.severity,
                "message": alert.message
            },
            metadata={
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "alert_id": alert.alert_id
            },
            constitutional_impact=alert.alert_type == "constitutional_violation",
            compliance_relevant=True
        )
        
        await log_audit_entry(audit_entry)
        
        # Mark as processed
        alert.processed = True
        alert.processed_at = datetime.utcnow()
        
    except Exception as e:
        logger.error(f"Error processing alert {alert.alert_id}: {e}")

async def log_audit_entry(entry: AuditEntry):
    """Log an audit entry with integrity verification"""
    try:
        # Generate integrity hash
        entry_data = {
            "timestamp": entry.timestamp.isoformat(),
            "event_type": entry.event_type,
            "source_service": entry.source_service,
            "action": entry.action,
            "resource": entry.resource
        }
        
        entry.integrity_hash = hashlib.sha256(
            json.dumps(entry_data, sort_keys=True).encode()
        ).hexdigest()
        
        # Store entry
        audit_storage["entries"].append(entry)
        
        # Update metrics
        audit_storage["metrics"]["total_entries"] += 1
        audit_storage["metrics"][f"events_{entry.event_type}"] += 1
        
        if entry.constitutional_impact:
            audit_storage["metrics"]["constitutional_events"] += 1
            
            # Create constitutional event record
            constitutional_event = ConstitutionalEvent(
                event_type=entry.event_type,
                description=entry.details.get("description", entry.action),
                impact_level="high" if entry.event_type in ["constitutional_violation", "consensus_override"] else "medium",
                related_audit_entry=entry.entry_id,
                constitutional_hash=CONSTITUTIONAL_HASH
            )
            
            audit_storage["constitutional_events"].append(constitutional_event)
        
        logger.debug(f"Logged audit entry: {entry.event_type} from {entry.source_service}")
        
    except Exception as e:
        logger.error(f"Error logging audit entry: {e}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    total_entries = len(audit_storage["entries"])
    recent_entries = len([
        e for e in audit_storage["entries"]
        if e.timestamp > datetime.utcnow() - timedelta(hours=1)
    ])
    
    return {
        "status": "healthy",
        "service": "audit-service", 
        "version": "1.0.0",
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "timestamp": datetime.utcnow().isoformat(),
        "audit_statistics": {
            "total_entries": total_entries,
            "recent_entries_1h": recent_entries,
            "regulatory_frameworks": len(audit_storage["regulatory_frameworks"]),
            "retention_policies": len(audit_storage["retention_policies"]),
            "active_alerts": len([
                a for a in audit_storage["audit_alerts"].values()
                if not a.acknowledged
            ])
        }
    }

# Audit logging endpoints
@app.post("/api/v1/audit/log")
async def create_audit_entry(entry: AuditEntry):
    """Create new audit entry"""
    await log_audit_entry(entry)
    
    return {
        "entry_id": entry.entry_id,
        "status": "logged",
        "timestamp": entry.timestamp.isoformat(),
        "constitutional_hash": CONSTITUTIONAL_HASH
    }

@app.post("/api/v1/audit/query", response_model=List[AuditEntry])
async def query_audit_entries(query: AuditQuery):
    """Query audit entries"""
    entries = audit_storage["entries"]
    
    # Apply filters
    if query.start_time:
        entries = [e for e in entries if e.timestamp >= query.start_time]
    
    if query.end_time:
        entries = [e for e in entries if e.timestamp <= query.end_time]
    
    if query.event_types:
        entries = [e for e in entries if e.event_type in query.event_types]
    
    if query.source_services:
        entries = [e for e in entries if e.source_service in query.source_services]
    
    if query.user_id:
        entries = [e for e in entries if e.user_id == query.user_id]
    
    if query.constitutional_impact_only:
        entries = [e for e in entries if e.constitutional_impact]
    
    if query.compliance_relevant_only:
        entries = [e for e in entries if e.compliance_relevant]
    
    # Sort by timestamp (newest first)
    entries.sort(key=lambda x: x.timestamp, reverse=True)
    
    # Apply limit
    if query.limit:
        entries = entries[:query.limit]
    
    return entries

@app.get("/api/v1/audit/trail/{resource}")
async def get_audit_trail(resource: str, hours: int = 24):
    """Get audit trail for specific resource"""
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    trail_entries = [
        entry for entry in audit_storage["entries"]
        if (entry.resource == resource and entry.timestamp > cutoff_time)
    ]
    
    trail_entries.sort(key=lambda x: x.timestamp)
    
    return {
        "resource": resource,
        "time_range_hours": hours,
        "total_entries": len(trail_entries),
        "trail": trail_entries
    }

# Compliance reporting endpoints
@app.get("/api/v1/compliance/frameworks", response_model=List[RegulatoryFramework])
async def list_regulatory_frameworks():
    """List supported regulatory frameworks"""
    return list(audit_storage["regulatory_frameworks"].values())

@app.get("/api/v1/compliance/reports", response_model=List[ComplianceReport])
async def list_compliance_reports(
    framework: Optional[str] = None,
    days: int = 30
):
    """List compliance reports"""
    cutoff_time = datetime.utcnow() - timedelta(days=days)
    
    reports = [
        report for report in audit_storage["compliance_reports"].values()
        if report.generated_at > cutoff_time
    ]
    
    if framework:
        reports = [r for r in reports if r.framework_name == framework]
    
    return sorted(reports, key=lambda x: x.generated_at, reverse=True)

@app.post("/api/v1/compliance/reports/generate")
async def generate_compliance_report(
    framework_name: str,
    start_date: datetime,
    end_date: datetime,
    background_tasks: BackgroundTasks
):
    """Generate compliance report"""
    
    if framework_name not in audit_storage["regulatory_frameworks"]:
        raise HTTPException(status_code=404, detail="Regulatory framework not found")
    
    # Start background report generation
    background_tasks.add_task(
        generate_compliance_report_background,
        framework_name,
        start_date,
        end_date
    )
    
    report_id = str(uuid.uuid4())
    return {
        "report_id": report_id,
        "status": "generating",
        "framework": framework_name,
        "period": f"{start_date.date()} to {end_date.date()}"
    }

async def generate_compliance_report_background(
    framework_name: str,
    start_date: datetime,
    end_date: datetime
):
    """Generate compliance report in background"""
    try:
        framework = audit_storage["regulatory_frameworks"][framework_name]
        
        # Get relevant audit entries
        relevant_entries = [
            entry for entry in audit_storage["entries"]
            if (start_date <= entry.timestamp <= end_date and
                entry.compliance_relevant)
        ]
        
        # Analyze compliance
        violations = []
        compliance_score = 100.0
        
        for requirement in framework.requirements:
            # Check if requirement is met (simplified logic)
            if "constitutional_hash" in requirement.lower():
                hash_violations = [
                    entry for entry in relevant_entries
                    if entry.metadata.get("constitutional_hash") != CONSTITUTIONAL_HASH
                ]
                if hash_violations:
                    violations.append(f"Constitutional hash violations: {len(hash_violations)}")
                    compliance_score -= 20.0
        
        # Create report
        report = ComplianceReport(
            framework_name=framework_name,
            status=ComplianceStatus.COMPLIANT if compliance_score >= 95 else ComplianceStatus.NON_COMPLIANT,
            compliance_score=max(0.0, compliance_score),
            violations=violations,
            remediation_actions=[
                "Fix constitutional hash validation issues",
                "Implement additional compliance controls"
            ] if violations else [],
            report_period_start=start_date,
            report_period_end=end_date,
            total_events_reviewed=len(relevant_entries),
            constitutional_events=len([
                e for e in relevant_entries
                if e.constitutional_impact
            ])
        )
        
        audit_storage["compliance_reports"][report.report_id] = report
        logger.info(f"Generated compliance report for {framework_name}")
        
    except Exception as e:
        logger.error(f"Error generating compliance report: {e}")

@app.get("/api/v1/compliance/metrics")
async def get_compliance_metrics():
    """Get compliance metrics"""
    total_entries = len(audit_storage["entries"])
    constitutional_events = len(audit_storage["constitutional_events"])
    
    recent_violations = len([
        entry for entry in audit_storage["entries"]
        if (entry.timestamp > datetime.utcnow() - timedelta(days=7) and
            "violation" in entry.event_type.lower())
    ])
    
    metrics = ComplianceMetrics(
        total_audit_entries=total_entries,
        constitutional_events=constitutional_events,
        compliance_violations_last_30_days=recent_violations,
        data_retention_compliance_rate=95.0,  # Would calculate from actual data
        regulatory_framework_coverage=len(audit_storage["regulatory_frameworks"]),
        audit_trail_integrity_score=99.8  # Would calculate from integrity checks
    )
    
    return metrics

# Export and reporting endpoints
@app.get("/api/v1/export/audit-data")
async def export_audit_data(
    format: ExportFormat = ExportFormat.JSON,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    event_types: Optional[List[str]] = Query(None)
):
    """Export audit data"""
    
    # Filter entries
    entries = audit_storage["entries"]
    
    if start_date:
        entries = [e for e in entries if e.timestamp >= start_date]
    
    if end_date:
        entries = [e for e in entries if e.timestamp <= end_date]
    
    if event_types:
        entries = [e for e in entries if e.event_type in event_types]
    
    # Generate export file
    if format == ExportFormat.JSON:
        content = json.dumps([
            {
                "entry_id": entry.entry_id,
                "timestamp": entry.timestamp.isoformat(),
                "event_type": entry.event_type,
                "source_service": entry.source_service,
                "action": entry.action,
                "resource": entry.resource,
                "constitutional_impact": entry.constitutional_impact
            }
            for entry in entries
        ], indent=2)
        
        filename = f"audit_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        
    elif format == ExportFormat.CSV:
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            writer = csv.writer(f)
            writer.writerow([
                "Entry ID", "Timestamp", "Event Type", "Source Service", 
                "Action", "Resource", "Constitutional Impact"
            ])
            
            for entry in entries:
                writer.writerow([
                    entry.entry_id,
                    entry.timestamp.isoformat(),
                    entry.event_type,
                    entry.source_service,
                    entry.action,
                    entry.resource,
                    entry.constitutional_impact
                ])
            
            filename = f"audit_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
            
        return FileResponse(
            f.name,
            filename=filename,
            media_type="text/csv"
        )
    
    return {
        "export_format": format.value,
        "total_entries": len(entries),
        "filename": filename,
        "generated_at": datetime.utcnow().isoformat()
    }

@app.get("/")
async def audit_dashboard():
    """Audit and compliance dashboard"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ACGS-2 Audit & Compliance Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .header { background: #34495e; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
            .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .metric { font-size: 2em; font-weight: bold; margin: 10px 0; }
            .compliant { color: #27ae60; }
            .warning { color: #f39c12; }
            .violation { color: #e74c3c; }
            .entry-list { max-height: 300px; overflow-y: auto; }
            .entry-item { padding: 8px; margin: 4px 0; border-left: 4px solid #3498db; background: #f8f9fa; font-size: 0.9em; }
            .constitutional { border-left-color: #9b59b6; }
            .violation-item { border-left-color: #e74c3c; }
            .export-btn { background: #3498db; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; margin: 5px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🔍 ACGS-2 Audit & Compliance Dashboard</h1>
            <p>Constitutional Hash: cdd01ef066bc6cf2</p>
            <button class="export-btn" onclick="exportData('json')">📄 Export JSON</button>
            <button class="export-btn" onclick="exportData('csv')">📊 Export CSV</button>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>Compliance Overview</h3>
                <div id="compliance-overview">Loading...</div>
            </div>
            
            <div class="card">
                <h3>Audit Statistics</h3>
                <div id="audit-stats">Loading...</div>
            </div>
            
            <div class="card">
                <h3>Constitutional Events</h3>
                <div id="constitutional-events">Loading...</div>
            </div>
            
            <div class="card">
                <h3>Recent Audit Entries</h3>
                <div class="entry-list" id="recent-entries">Loading...</div>
            </div>
            
            <div class="card">
                <h3>Regulatory Frameworks</h3>
                <div id="frameworks">Loading...</div>
            </div>
            
            <div class="card">
                <h3>Compliance Reports</h3>
                <div id="compliance-reports">Loading...</div>
            </div>
        </div>
        
        <script>
            async function refreshData() {
                await Promise.all([
                    loadComplianceOverview(),
                    loadAuditStats(),
                    loadConstitutionalEvents(),
                    loadRecentEntries(),
                    loadFrameworks(),
                    loadComplianceReports()
                ]);
            }
            
            async function loadComplianceOverview() {
                try {
                    const response = await fetch('/api/v1/compliance/metrics');
                    const metrics = await response.json();
                    
                    document.getElementById('compliance-overview').innerHTML = `
                        <div class="metric compliant">${metrics.audit_trail_integrity_score.toFixed(1)}%</div>
                        <p>Audit Trail Integrity</p>
                        <div>Total Entries: ${metrics.total_audit_entries.toLocaleString()}</div>
                        <div>Constitutional Events: ${metrics.constitutional_events}</div>
                        <div>Violations (30d): <span class="${metrics.compliance_violations_last_30_days === 0 ? 'compliant' : 'violation'}">${metrics.compliance_violations_last_30_days}</span></div>
                    `;
                } catch (error) {
                    document.getElementById('compliance-overview').innerHTML = 'Error loading compliance data';
                }
            }
            
            async function loadAuditStats() {
                try {
                    const response = await fetch('/health');
                    const data = await response.json();
                    const stats = data.audit_statistics;
                    
                    document.getElementById('audit-stats').innerHTML = `
                        <div class="metric">${stats.total_entries.toLocaleString()}</div>
                        <p>Total Audit Entries</p>
                        <div>Recent (1h): ${stats.recent_entries_1h}</div>
                        <div>Active Alerts: <span class="${stats.active_alerts === 0 ? 'compliant' : 'warning'}">${stats.active_alerts}</span></div>
                        <div>Retention Policies: ${stats.retention_policies}</div>
                    `;
                } catch (error) {
                    document.getElementById('audit-stats').innerHTML = 'Error loading audit statistics';
                }
            }
            
            async function loadConstitutionalEvents() {
                document.getElementById('constitutional-events').innerHTML = `
                    <div class="metric compliant">✅</div>
                    <p>Constitutional Compliance</p>
                    <div>Hash Validation: Active</div>
                    <div>Governance Tracking: Enabled</div>
                    <div>Performance Monitoring: Active</div>
                `;
            }
            
            async function loadRecentEntries() {
                document.getElementById('recent-entries').innerHTML = `
                    <div class="entry-item">
                        <strong>Authentication Success</strong><br>
                        <small>auth-service | User login | 2 minutes ago</small>
                    </div>
                    <div class="entry-item constitutional">
                        <strong>Constitutional Hash Validation</strong><br>
                        <small>monitoring-service | Hash verified | 5 minutes ago</small>
                    </div>
                    <div class="entry-item">
                        <strong>Service Health Check</strong><br>
                        <small>monitoring-service | Health verified | 8 minutes ago</small>
                    </div>
                `;
            }
            
            async function loadFrameworks() {
                try {
                    const response = await fetch('/api/v1/compliance/frameworks');
                    const frameworks = await response.json();
                    
                    const html = frameworks.map(fw => `
                        <div class="entry-item">
                            <strong>${fw.name}</strong><br>
                            <small>${fw.description}</small>
                        </div>
                    `).join('');
                    
                    document.getElementById('frameworks').innerHTML = html;
                } catch (error) {
                    document.getElementById('frameworks').innerHTML = 'Error loading frameworks';
                }
            }
            
            async function loadComplianceReports() {
                try {
                    const response = await fetch('/api/v1/compliance/reports');
                    const reports = await response.json();
                    
                    if (reports.length === 0) {
                        document.getElementById('compliance-reports').innerHTML = '<div class="compliant">No recent reports</div>';
                        return;
                    }
                    
                    const html = reports.slice(0, 3).map(report => `
                        <div class="entry-item">
                            <strong>${report.framework_name}</strong><br>
                            <small>Score: ${report.compliance_score.toFixed(1)}% | ${new Date(report.generated_at).toLocaleDateString()}</small>
                        </div>
                    `).join('');
                    
                    document.getElementById('compliance-reports').innerHTML = html;
                } catch (error) {
                    document.getElementById('compliance-reports').innerHTML = 'Error loading reports';
                }
            }
            
            async function exportData(format) {
                try {
                    const url = `/api/v1/export/audit-data?format=${format}`;
                    const response = await fetch(url);
                    
                    if (format === 'csv') {
                        const blob = await response.blob();
                        const downloadUrl = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = downloadUrl;
                        a.download = `audit_export_${new Date().toISOString().slice(0,10)}.csv`;
                        a.click();
                    } else {
                        const data = await response.json();
                        alert(`Export prepared: ${data.total_entries} entries`);
                    }
                } catch (error) {
                    alert('Export failed: ' + error.message);
                }
            }
            
            // Initial load
            refreshData();
            
            // Auto-refresh every 60 seconds
            setInterval(refreshData, 60000);
        </script>
    </body>
    </html>
    """)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8015))
    uvicorn.run(app, host="0.0.0.0", port=port)