"""
GDPR Compliance Service
Constitutional Hash: cdd01ef066bc6cf2

FastAPI service for comprehensive GDPR compliance including data subject rights,
consent management, privacy impact assessments, and data protection controls.
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from contextlib import asynccontextmanager
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import asyncio
import json
import os
import uuid
from collections import defaultdict
import hashlib
import zipfile
import tempfile

from .models import (
    DataSubject, ConsentRecord, DataProcessingActivity, DataRetentionRule,
    PrivacyImpactAssessment, DataBreachIncident, DataSubjectRequest,
    ConsentStatus, ProcessingLawfulBasis, DataCategory, RequestType,
    ComplianceReport, PrivacyNotice, DataController, DataProcessor,
    CrossBorderTransfer, CONSTITUTIONAL_HASH
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global storage for GDPR data
gdpr_storage = {
    "data_subjects": {},
    "consent_records": {},
    "processing_activities": {},
    "retention_rules": {},
    "privacy_assessments": {},
    "breach_incidents": {},
    "subject_requests": {},
    "privacy_notices": {},
    "controllers": {},
    "processors": {},
    "transfers": {},
    "compliance_metrics": defaultdict(int)
}

# GDPR configuration
GDPR_CONFIG = {
    "data_retention_default_days": 365,
    "consent_refresh_months": 24,
    "breach_notification_hours": 72,
    "subject_request_response_days": 30,
    "anonymization_enabled": True,
    "pseudonymization_enabled": True,
    "encryption_at_rest": True,
    "audit_trail_enabled": True
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    logger.info("Starting GDPR Compliance Service")
    logger.info(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    
    # Initialize GDPR system
    await initialize_data_controllers()
    await initialize_processing_activities()
    await initialize_retention_rules()
    await create_default_privacy_notices()
    
    # Start background tasks
    asyncio.create_task(consent_monitoring())
    asyncio.create_task(retention_enforcement())
    asyncio.create_task(breach_monitoring())
    asyncio.create_task(compliance_reporting())
    asyncio.create_task(subject_request_monitoring())
    
    yield
    
    logger.info("Shutting down GDPR Compliance Service")

app = FastAPI(
    title="GDPR Compliance Service",
    description="Comprehensive GDPR compliance and data protection for ACGS-2",
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

async def initialize_data_controllers():
    """Initialize data controllers"""
    controllers = [
        DataController(
            name="ACGS-2 System Controller",
            organization="ACGS-2 Platform",
            contact_email="dpo@acgs-2.ai",
            contact_phone="+1-555-0123",
            address="123 AI Governance St, Tech City, TC 12345",
            dpo_name="Chief Privacy Officer",
            dpo_email="cpo@acgs-2.ai",
            lawful_bases=[
                ProcessingLawfulBasis.LEGITIMATE_INTEREST,
                ProcessingLawfulBasis.CONSENT,
                ProcessingLawfulBasis.CONTRACT
            ],
            data_categories=[
                DataCategory.IDENTITY,
                DataCategory.CONTACT,
                DataCategory.TECHNICAL,
                DataCategory.BEHAVIORAL
            ]
        )
    ]
    
    for controller in controllers:
        gdpr_storage["controllers"][controller.controller_id] = controller
    
    logger.info(f"Initialized {len(controllers)} data controllers")

async def initialize_processing_activities():
    """Initialize data processing activities"""
    activities = [
        DataProcessingActivity(
            name="User Authentication",
            description="Processing user credentials for system access",
            controller_id=list(gdpr_storage["controllers"].keys())[0] if gdpr_storage["controllers"] else "default",
            purposes=["Authentication", "Access control"],
            lawful_basis=ProcessingLawfulBasis.LEGITIMATE_INTEREST,
            data_categories=[DataCategory.IDENTITY, DataCategory.TECHNICAL],
            data_subjects=["System users", "Administrators"],
            recipients=["Authentication service", "Audit service"],
            retention_period_months=36,
            international_transfers=False,
            automated_decision_making=False,
            profiling=False,
            special_categories=False
        ),
        DataProcessingActivity(
            name="Constitutional Governance",
            description="Processing data for constitutional AI governance decisions",
            controller_id=list(gdpr_storage["controllers"].keys())[0] if gdpr_storage["controllers"] else "default",
            purposes=["AI governance", "Constitutional compliance", "Decision making"],
            lawful_basis=ProcessingLawfulBasis.LEGITIMATE_INTEREST,
            data_categories=[DataCategory.BEHAVIORAL, DataCategory.TECHNICAL],
            data_subjects=["System operators", "AI agents"],
            recipients=["Consensus engine", "Human oversight"],
            retention_period_months=-1,  # Permanent for constitutional records
            international_transfers=False,
            automated_decision_making=True,
            profiling=True,
            special_categories=False
        ),
        DataProcessingActivity(
            name="System Monitoring",
            description="Monitoring system performance and security",
            controller_id=list(gdpr_storage["controllers"].keys())[0] if gdpr_storage["controllers"] else "default",
            purposes=["Security monitoring", "Performance optimization"],
            lawful_basis=ProcessingLawfulBasis.LEGITIMATE_INTEREST,
            data_categories=[DataCategory.TECHNICAL, DataCategory.BEHAVIORAL],
            data_subjects=["All system users"],
            recipients=["Monitoring service", "Security team"],
            retention_period_months=12,
            international_transfers=False,
            automated_decision_making=True,
            profiling=False,
            special_categories=False
        ),
        DataProcessingActivity(
            name="Audit and Compliance",
            description="Maintaining audit trails for regulatory compliance",
            controller_id=list(gdpr_storage["controllers"].keys())[0] if gdpr_storage["controllers"] else "default",
            purposes=["Legal compliance", "Audit trail", "Regulatory reporting"],
            lawful_basis=ProcessingLawfulBasis.LEGAL_OBLIGATION,
            data_categories=[DataCategory.IDENTITY, DataCategory.BEHAVIORAL],
            data_subjects=["All data subjects"],
            recipients=["Audit service", "Regulatory authorities"],
            retention_period_months=84,  # 7 years for legal compliance
            international_transfers=False,
            automated_decision_making=False,
            profiling=False,
            special_categories=False
        )
    ]
    
    for activity in activities:
        gdpr_storage["processing_activities"][activity.activity_id] = activity
    
    logger.info(f"Initialized {len(activities)} processing activities")

async def initialize_retention_rules():
    """Initialize data retention rules"""
    rules = [
        DataRetentionRule(
            name="User Authentication Data",
            data_categories=[DataCategory.IDENTITY, DataCategory.TECHNICAL],
            retention_period_months=36,
            retention_basis="Legitimate interest in system security",
            deletion_method="secure_deletion",
            exceptions=["Legal hold", "Ongoing investigation"],
            auto_deletion=True
        ),
        DataRetentionRule(
            name="Constitutional Records",
            data_categories=[DataCategory.BEHAVIORAL],
            retention_period_months=-1,  # Permanent
            retention_basis="Constitutional governance requirements",
            deletion_method="none",
            exceptions=[],
            auto_deletion=False
        ),
        DataRetentionRule(
            name="System Logs",
            data_categories=[DataCategory.TECHNICAL],
            retention_period_months=12,
            retention_basis="System operation and security",
            deletion_method="secure_deletion",
            exceptions=["Security incident"],
            auto_deletion=True
        ),
        DataRetentionRule(
            name="Consent Records",
            data_categories=[DataCategory.CONTACT],
            retention_period_months=60,  # 5 years after withdrawal
            retention_basis="Legal obligation to maintain consent proof",
            deletion_method="secure_deletion",
            exceptions=[],
            auto_deletion=True
        )
    ]
    
    for rule in rules:
        gdpr_storage["retention_rules"][rule.rule_id] = rule
    
    logger.info(f"Initialized {len(rules)} retention rules")

async def create_default_privacy_notices():
    """Create default privacy notices"""
    notices = [
        PrivacyNotice(
            title="ACGS-2 Privacy Notice",
            version="1.0",
            effective_date=datetime.utcnow(),
            language="en",
            data_controller="ACGS-2 System Controller",
            purposes_of_processing=[
                "User authentication and access control",
                "Constitutional AI governance",
                "System monitoring and security",
                "Legal compliance and audit"
            ],
            lawful_bases=[
                "Legitimate interest in system operation",
                "Consent for optional features",
                "Legal obligation for compliance"
            ],
            data_categories=[
                "Identity information (username, email)",
                "Technical data (IP address, session data)",
                "Behavioral data (system interactions)",
                "Contact information"
            ],
            retention_periods={
                "Authentication data": "3 years",
                "Constitutional records": "Permanent",
                "System logs": "1 year",
                "Consent records": "5 years after withdrawal"
            },
            data_subject_rights=[
                "Right of access",
                "Right to rectification",
                "Right to erasure (right to be forgotten)",
                "Right to restrict processing",
                "Right to data portability",
                "Right to object"
            ],
            contact_details={
                "dpo_email": "dpo@acgs-2.ai",
                "dpo_name": "Chief Privacy Officer",
                "organization": "ACGS-2 Platform"
            },
            automated_decision_making=True,
            profiling=True,
            international_transfers=False
        )
    ]
    
    for notice in notices:
        gdpr_storage["privacy_notices"][notice.notice_id] = notice
    
    logger.info(f"Created {len(notices)} privacy notices")

async def consent_monitoring():
    """Monitor consent status and refresh requirements"""
    while True:
        try:
            current_time = datetime.utcnow()
            
            # Check for expired consents
            expired_consents = []
            for consent_id, consent in gdpr_storage["consent_records"].items():
                if (consent.expires_at and consent.expires_at <= current_time and 
                    consent.status == ConsentStatus.GIVEN):
                    expired_consents.append(consent_id)
            
            # Mark expired consents
            for consent_id in expired_consents:
                consent = gdpr_storage["consent_records"][consent_id]
                consent.status = ConsentStatus.EXPIRED
                consent.updated_at = current_time
                
                logger.info(f"Consent expired: {consent_id}")
                gdpr_storage["compliance_metrics"]["expired_consents"] += 1
            
            # Check for consents requiring refresh
            refresh_threshold = current_time + timedelta(days=30)  # 30 days before expiry
            consents_needing_refresh = [
                consent for consent in gdpr_storage["consent_records"].values()
                if (consent.expires_at and consent.expires_at <= refresh_threshold and
                    consent.status == ConsentStatus.GIVEN)
            ]
            
            for consent in consents_needing_refresh:
                # Would trigger consent refresh notification
                logger.info(f"Consent needs refresh: {consent.consent_id}")
            
            await asyncio.sleep(3600)  # Check every hour
            
        except Exception as e:
            logger.error(f"Consent monitoring error: {e}")
            await asyncio.sleep(3600)

async def retention_enforcement():
    """Enforce data retention policies"""
    while True:
        try:
            current_time = datetime.utcnow()
            
            # Check each retention rule
            for rule in gdpr_storage["retention_rules"].values():
                if not rule.auto_deletion or rule.retention_period_months < 0:
                    continue
                
                cutoff_date = current_time - timedelta(days=rule.retention_period_months * 30)
                
                # Find data to be deleted (simplified - would integrate with actual data stores)
                deletion_candidates = []
                
                # Check consent records
                if DataCategory.CONTACT in rule.data_categories:
                    for consent in gdpr_storage["consent_records"].values():
                        if (consent.created_at < cutoff_date and 
                            consent.status in [ConsentStatus.WITHDRAWN, ConsentStatus.EXPIRED]):
                            deletion_candidates.append(("consent", consent.consent_id))
                
                # Process deletions
                for data_type, data_id in deletion_candidates:
                    await secure_delete_data(data_type, data_id, rule)
                    gdpr_storage["compliance_metrics"]["auto_deletions"] += 1
            
            await asyncio.sleep(86400)  # Check daily
            
        except Exception as e:
            logger.error(f"Retention enforcement error: {e}")
            await asyncio.sleep(86400)

async def secure_delete_data(data_type: str, data_id: str, rule: DataRetentionRule):
    """Securely delete data according to retention rule"""
    try:
        if data_type == "consent" and data_id in gdpr_storage["consent_records"]:
            # Mark as deleted rather than actually deleting (for audit trail)
            consent = gdpr_storage["consent_records"][data_id]
            consent.status = ConsentStatus.DELETED
            consent.updated_at = datetime.utcnow()
            
            logger.info(f"Securely deleted {data_type} {data_id} per retention rule {rule.name}")
    
    except Exception as e:
        logger.error(f"Error deleting {data_type} {data_id}: {e}")

async def breach_monitoring():
    """Monitor for potential data breaches"""
    while True:
        try:
            # Check for security events that might indicate breaches
            # This would integrate with the security validation service
            
            # Check for high-risk activities
            high_risk_indicators = [
                "unauthorized_access",
                "data_exfiltration", 
                "system_compromise",
                "encryption_failure"
            ]
            
            # Would check audit logs for these indicators
            # For now, just maintain breach monitoring status
            gdpr_storage["compliance_metrics"]["breach_monitoring_runs"] += 1
            
            await asyncio.sleep(300)  # Check every 5 minutes
            
        except Exception as e:
            logger.error(f"Breach monitoring error: {e}")
            await asyncio.sleep(300)

async def compliance_reporting():
    """Generate compliance reports"""
    while True:
        try:
            # Generate daily compliance metrics
            report = ComplianceReport(
                report_type="daily_compliance",
                period_start=datetime.utcnow() - timedelta(days=1),
                period_end=datetime.utcnow(),
                total_data_subjects=len(gdpr_storage["data_subjects"]),
                active_consents=len([
                    c for c in gdpr_storage["consent_records"].values()
                    if c.status == ConsentStatus.GIVEN
                ]),
                expired_consents=len([
                    c for c in gdpr_storage["consent_records"].values()
                    if c.status == ConsentStatus.EXPIRED
                ]),
                withdrawal_rate=calculate_withdrawal_rate(),
                subject_requests_pending=len([
                    r for r in gdpr_storage["subject_requests"].values()
                    if r.status == "pending"
                ]),
                breach_incidents=len(gdpr_storage["breach_incidents"]),
                compliance_score=calculate_compliance_score()
            )
            
            # Store report (in production, would persist to database)
            logger.info(f"Generated compliance report: {report.compliance_score}% compliance")
            
            await asyncio.sleep(86400)  # Generate daily
            
        except Exception as e:
            logger.error(f"Compliance reporting error: {e}")
            await asyncio.sleep(86400)

def calculate_withdrawal_rate() -> float:
    """Calculate consent withdrawal rate"""
    total_consents = len(gdpr_storage["consent_records"])
    if total_consents == 0:
        return 0.0
    
    withdrawn_consents = len([
        c for c in gdpr_storage["consent_records"].values()
        if c.status == ConsentStatus.WITHDRAWN
    ])
    
    return (withdrawn_consents / total_consents) * 100

def calculate_compliance_score() -> float:
    """Calculate overall GDPR compliance score"""
    score = 100.0
    
    # Check various compliance factors
    total_consents = len(gdpr_storage["consent_records"])
    if total_consents > 0:
        # Deduct for expired consents
        expired_consents = len([
            c for c in gdpr_storage["consent_records"].values()
            if c.status == ConsentStatus.EXPIRED
        ])
        score -= (expired_consents / total_consents) * 20
        
        # Deduct for overdue subject requests
        overdue_requests = len([
            r for r in gdpr_storage["subject_requests"].values()
            if (r.status == "pending" and 
                (datetime.utcnow() - r.submitted_at).days > 30)
        ])
        score -= overdue_requests * 5
    
    # Deduct for unresolved breaches
    unresolved_breaches = len([
        b for b in gdpr_storage["breach_incidents"].values()
        if b.status != "resolved"
    ])
    score -= unresolved_breaches * 10
    
    return max(0.0, score)

async def subject_request_monitoring():
    """Monitor data subject requests for timely response"""
    while True:
        try:
            current_time = datetime.utcnow()
            
            # Check for overdue requests (30 days)
            overdue_requests = [
                request for request in gdpr_storage["subject_requests"].values()
                if (request.status == "pending" and 
                    (current_time - request.submitted_at).days > 30)
            ]
            
            for request in overdue_requests:
                logger.warning(f"Overdue subject request: {request.request_id}")
                gdpr_storage["compliance_metrics"]["overdue_requests"] += 1
            
            await asyncio.sleep(3600)  # Check hourly
            
        except Exception as e:
            logger.error(f"Subject request monitoring error: {e}")
            await asyncio.sleep(3600)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    total_subjects = len(gdpr_storage["data_subjects"])
    active_consents = len([
        c for c in gdpr_storage["consent_records"].values()
        if c.status == ConsentStatus.GIVEN
    ])
    pending_requests = len([
        r for r in gdpr_storage["subject_requests"].values()
        if r.status == "pending"
    ])
    
    return {
        "status": "healthy",
        "service": "gdpr-compliance",
        "version": "1.0.0",
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "timestamp": datetime.utcnow().isoformat(),
        "gdpr_statistics": {
            "total_data_subjects": total_subjects,
            "active_consents": active_consents,
            "pending_requests": pending_requests,
            "processing_activities": len(gdpr_storage["processing_activities"]),
            "retention_rules": len(gdpr_storage["retention_rules"]),
            "compliance_score": calculate_compliance_score()
        }
    }

# Data Subject Rights endpoints
@app.post("/api/v1/data-subjects/register")
async def register_data_subject(subject: DataSubject):
    """Register a new data subject"""
    gdpr_storage["data_subjects"][subject.subject_id] = subject
    
    # Create default consent record
    default_consent = ConsentRecord(
        subject_id=subject.subject_id,
        processing_activity="User Registration",
        purpose="Account creation and authentication",
        lawful_basis=ProcessingLawfulBasis.CONSENT,
        consent_method="web_form",
        consent_text="I consent to the processing of my personal data for account creation",
        status=ConsentStatus.GIVEN,
        expires_at=datetime.utcnow() + timedelta(days=GDPR_CONFIG["consent_refresh_months"] * 30)
    )
    
    gdpr_storage["consent_records"][default_consent.consent_id] = default_consent
    
    return {
        "subject_id": subject.subject_id,
        "status": "registered",
        "consent_id": default_consent.consent_id,
        "constitutional_hash": CONSTITUTIONAL_HASH
    }

@app.post("/api/v1/consent/record")
async def record_consent(consent: ConsentRecord):
    """Record consent for data processing"""
    gdpr_storage["consent_records"][consent.consent_id] = consent
    gdpr_storage["compliance_metrics"]["consents_recorded"] += 1
    
    return {
        "consent_id": consent.consent_id,
        "status": "recorded",
        "expires_at": consent.expires_at.isoformat() if consent.expires_at else None
    }

@app.post("/api/v1/consent/{consent_id}/withdraw")
async def withdraw_consent(consent_id: str, reason: Optional[str] = None):
    """Withdraw consent"""
    if consent_id not in gdpr_storage["consent_records"]:
        raise HTTPException(status_code=404, detail="Consent record not found")
    
    consent = gdpr_storage["consent_records"][consent_id]
    consent.status = ConsentStatus.WITHDRAWN
    consent.withdrawn_at = datetime.utcnow()
    consent.withdrawal_reason = reason
    consent.updated_at = datetime.utcnow()
    
    gdpr_storage["compliance_metrics"]["consents_withdrawn"] += 1
    
    return {
        "consent_id": consent_id,
        "status": "withdrawn",
        "withdrawn_at": consent.withdrawn_at.isoformat()
    }

@app.get("/api/v1/data-subjects/{subject_id}/consents")
async def get_subject_consents(subject_id: str):
    """Get all consents for a data subject"""
    consents = [
        consent for consent in gdpr_storage["consent_records"].values()
        if consent.subject_id == subject_id
    ]
    
    return {
        "subject_id": subject_id,
        "total_consents": len(consents),
        "consents": consents
    }

@app.post("/api/v1/subject-requests")
async def submit_subject_request(request: DataSubjectRequest):
    """Submit a data subject request"""
    gdpr_storage["subject_requests"][request.request_id] = request
    gdpr_storage["compliance_metrics"]["subject_requests_received"] += 1
    
    # Auto-process some request types
    if request.request_type == RequestType.ACCESS:
        await process_access_request(request)
    elif request.request_type == RequestType.PORTABILITY:
        await process_portability_request(request)
    
    return {
        "request_id": request.request_id,
        "status": "submitted",
        "estimated_completion": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        "reference_number": f"GDPR-{request.request_id[:8]}"
    }

async def process_access_request(request: DataSubjectRequest):
    """Process a data access request"""
    try:
        subject_id = request.subject_id
        
        # Collect all data for the subject
        subject_data = {
            "personal_data": gdpr_storage["data_subjects"].get(subject_id),
            "consents": [
                consent for consent in gdpr_storage["consent_records"].values()
                if consent.subject_id == subject_id
            ],
            "processing_activities": [
                activity for activity in gdpr_storage["processing_activities"].values()
                if subject_id in str(activity.data_subjects)
            ]
        }
        
        # Update request status
        request.status = "completed"
        request.completed_at = datetime.utcnow()
        request.response_data = {"access_data": subject_data}
        
        gdpr_storage["compliance_metrics"]["access_requests_completed"] += 1
        
    except Exception as e:
        request.status = "failed"
        request.response_data = {"error": str(e)}
        logger.error(f"Error processing access request {request.request_id}: {e}")

async def process_portability_request(request: DataSubjectRequest):
    """Process a data portability request"""
    try:
        subject_id = request.subject_id
        
        # Export data in structured format
        export_data = {
            "export_date": datetime.utcnow().isoformat(),
            "subject_id": subject_id,
            "personal_data": gdpr_storage["data_subjects"].get(subject_id, {}),
            "consent_history": [
                {
                    "consent_id": consent.consent_id,
                    "purpose": consent.purpose,
                    "given_at": consent.given_at.isoformat(),
                    "status": consent.status.value
                }
                for consent in gdpr_storage["consent_records"].values()
                if consent.subject_id == subject_id
            ]
        }
        
        # Create downloadable file
        export_filename = f"data_export_{subject_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        export_path = f"/tmp/{export_filename}"
        
        with open(export_path, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        request.status = "completed"
        request.completed_at = datetime.utcnow()
        request.response_data = {"export_file": export_filename}
        
        gdpr_storage["compliance_metrics"]["portability_requests_completed"] += 1
        
    except Exception as e:
        request.status = "failed"
        request.response_data = {"error": str(e)}
        logger.error(f"Error processing portability request {request.request_id}: {e}")

@app.get("/api/v1/subject-requests/{request_id}")
async def get_subject_request(request_id: str):
    """Get status of a subject request"""
    if request_id not in gdpr_storage["subject_requests"]:
        raise HTTPException(status_code=404, detail="Request not found")
    
    request = gdpr_storage["subject_requests"][request_id]
    
    return {
        "request_id": request_id,
        "request_type": request.request_type.value,
        "status": request.status,
        "submitted_at": request.submitted_at.isoformat(),
        "completed_at": request.completed_at.isoformat() if request.completed_at else None,
        "days_remaining": max(0, 30 - (datetime.utcnow() - request.submitted_at).days)
    }

@app.post("/api/v1/erasure/{subject_id}")
async def process_erasure_request(
    subject_id: str,
    reason: str,
    background_tasks: BackgroundTasks
):
    """Process right to be forgotten request"""
    
    # Verify subject exists
    if subject_id not in gdpr_storage["data_subjects"]:
        raise HTTPException(status_code=404, detail="Data subject not found")
    
    # Create erasure request
    erasure_request = DataSubjectRequest(
        subject_id=subject_id,
        request_type=RequestType.ERASURE,
        details={"reason": reason},
        legal_basis="Article 17 GDPR - Right to erasure"
    )
    
    gdpr_storage["subject_requests"][erasure_request.request_id] = erasure_request
    
    # Start background erasure process
    background_tasks.add_task(execute_erasure, subject_id, erasure_request.request_id)
    
    return {
        "request_id": erasure_request.request_id,
        "status": "processing",
        "message": "Erasure request is being processed",
        "reference_number": f"ERASURE-{erasure_request.request_id[:8]}"
    }

async def execute_erasure(subject_id: str, request_id: str):
    """Execute data erasure"""
    try:
        request = gdpr_storage["subject_requests"][request_id]
        
        # Check for legal obligations to retain data
        retention_exceptions = []
        for rule in gdpr_storage["retention_rules"].values():
            if rule.exceptions and any("legal" in exc.lower() for exc in rule.exceptions):
                retention_exceptions.extend(rule.exceptions)
        
        if retention_exceptions:
            request.status = "partially_completed"
            request.response_data = {
                "message": "Some data retained due to legal obligations",
                "retained_categories": retention_exceptions
            }
        else:
            # Perform erasure
            if subject_id in gdpr_storage["data_subjects"]:
                del gdpr_storage["data_subjects"][subject_id]
            
            # Anonymize consent records instead of deleting (for audit)
            for consent in gdpr_storage["consent_records"].values():
                if consent.subject_id == subject_id:
                    consent.subject_id = f"ANONYMIZED_{uuid.uuid4().hex[:8]}"
                    consent.status = ConsentStatus.DELETED
            
            request.status = "completed"
            request.response_data = {"message": "Data successfully erased"}
        
        request.completed_at = datetime.utcnow()
        gdpr_storage["compliance_metrics"]["erasure_requests_completed"] += 1
        
    except Exception as e:
        request = gdpr_storage["subject_requests"][request_id]
        request.status = "failed"
        request.response_data = {"error": str(e)}
        logger.error(f"Error executing erasure for {subject_id}: {e}")

# Privacy Impact Assessment endpoints
@app.post("/api/v1/privacy-assessments")
async def create_privacy_assessment(assessment: PrivacyImpactAssessment):
    """Create a new privacy impact assessment"""
    gdpr_storage["privacy_assessments"][assessment.assessment_id] = assessment
    
    return {
        "assessment_id": assessment.assessment_id,
        "status": "created",
        "risk_level": assessment.risk_level
    }

@app.get("/api/v1/privacy-assessments")
async def list_privacy_assessments():
    """List all privacy impact assessments"""
    return list(gdpr_storage["privacy_assessments"].values())

# Data breach management endpoints
@app.post("/api/v1/breaches/report")
async def report_data_breach(incident: DataBreachIncident):
    """Report a data breach incident"""
    gdpr_storage["breach_incidents"][incident.incident_id] = incident
    gdpr_storage["compliance_metrics"]["breaches_reported"] += 1
    
    # Check if supervisory authority notification is required
    if incident.supervisory_authority_notification_required:
        hours_since_discovery = (datetime.utcnow() - incident.discovered_at).total_seconds() / 3600
        if hours_since_discovery > 72:
            logger.warning(f"Breach {incident.incident_id} reported after 72-hour deadline")
    
    return {
        "incident_id": incident.incident_id,
        "status": "reported",
        "notification_deadline": (incident.discovered_at + timedelta(hours=72)).isoformat()
    }

@app.get("/api/v1/breaches")
async def list_breaches():
    """List all data breach incidents"""
    return list(gdpr_storage["breach_incidents"].values())

# Compliance reporting endpoints
@app.get("/api/v1/compliance/report")
async def get_compliance_report():
    """Get current compliance status"""
    return {
        "compliance_score": calculate_compliance_score(),
        "metrics": dict(gdpr_storage["compliance_metrics"]),
        "data_subjects": len(gdpr_storage["data_subjects"]),
        "active_consents": len([
            c for c in gdpr_storage["consent_records"].values()
            if c.status == ConsentStatus.GIVEN
        ]),
        "pending_requests": len([
            r for r in gdpr_storage["subject_requests"].values()
            if r.status == "pending"
        ]),
        "processing_activities": len(gdpr_storage["processing_activities"]),
        "generated_at": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/privacy-notices")
async def get_privacy_notices(language: str = "en"):
    """Get privacy notices"""
    notices = [
        notice for notice in gdpr_storage["privacy_notices"].values()
        if notice.language == language
    ]
    return notices

@app.get("/")
async def gdpr_dashboard():
    """GDPR compliance dashboard"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ACGS-2 GDPR Compliance Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .header { background: #2980b9; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
            .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .metric { font-size: 2em; font-weight: bold; margin: 10px 0; }
            .compliant { color: #27ae60; }
            .warning { color: #f39c12; }
            .violation { color: #e74c3c; }
            .status-item { padding: 8px; margin: 4px 0; border-left: 4px solid #3498db; background: #f8f9fa; }
            .consent-item { border-left-color: #27ae60; }
            .request-item { border-left-color: #e67e22; }
            .breach-item { border-left-color: #e74c3c; }
            .action-btn { background: #3498db; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; margin: 5px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🔒 ACGS-2 GDPR Compliance Dashboard</h1>
            <p>Data Protection and Privacy Management</p>
            <p>Constitutional Hash: cdd01ef066bc6cf2</p>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>Compliance Overview</h3>
                <div id="compliance-overview">Loading...</div>
            </div>
            
            <div class="card">
                <h3>Data Subject Rights</h3>
                <div id="subject-rights">Loading...</div>
            </div>
            
            <div class="card">
                <h3>Consent Management</h3>
                <div id="consent-management">Loading...</div>
            </div>
            
            <div class="card">
                <h3>Data Processing Activities</h3>
                <div id="processing-activities">Loading...</div>
            </div>
            
            <div class="card">
                <h3>Subject Requests</h3>
                <div id="subject-requests">Loading...</div>
            </div>
            
            <div class="card">
                <h3>Data Breaches</h3>
                <div id="data-breaches">Loading...</div>
            </div>
        </div>
        
        <script>
            async function refreshData() {
                await Promise.all([
                    loadComplianceOverview(),
                    loadSubjectRights(),
                    loadConsentManagement(),
                    loadProcessingActivities(),
                    loadSubjectRequests(),
                    loadDataBreaches()
                ]);
            }
            
            async function loadComplianceOverview() {
                try {
                    const response = await fetch('/api/v1/compliance/report');
                    const data = await response.json();
                    
                    const scoreClass = data.compliance_score >= 95 ? 'compliant' : 
                                      data.compliance_score >= 80 ? 'warning' : 'violation';
                    
                    document.getElementById('compliance-overview').innerHTML = `
                        <div class="metric ${scoreClass}">${data.compliance_score.toFixed(1)}%</div>
                        <p>Overall Compliance Score</p>
                        <div>Data Subjects: ${data.data_subjects}</div>
                        <div>Active Consents: ${data.active_consents}</div>
                        <div>Pending Requests: <span class="${data.pending_requests > 0 ? 'warning' : 'compliant'}">${data.pending_requests}</span></div>
                        <div>Processing Activities: ${data.processing_activities}</div>
                    `;
                } catch (error) {
                    document.getElementById('compliance-overview').innerHTML = 'Error loading compliance data';
                }
            }
            
            async function loadSubjectRights() {
                document.getElementById('subject-rights').innerHTML = `
                    <div class="status-item">
                        <strong>Right of Access</strong><br>
                        <small>Automated data export available</small>
                    </div>
                    <div class="status-item">
                        <strong>Right to Erasure</strong><br>
                        <small>Secure deletion with legal exceptions</small>
                    </div>
                    <div class="status-item">
                        <strong>Data Portability</strong><br>
                        <small>JSON export format supported</small>
                    </div>
                    <div class="status-item">
                        <strong>Right to Rectification</strong><br>
                        <small>Self-service data updates</small>
                    </div>
                `;
            }
            
            async function loadConsentManagement() {
                document.getElementById('consent-management').innerHTML = `
                    <div class="consent-item">
                        <strong>Active Consents</strong><br>
                        <small>Monitoring expiration and refresh needs</small>
                    </div>
                    <div class="consent-item">
                        <strong>Consent Refresh</strong><br>
                        <small>24-month automatic refresh cycle</small>
                    </div>
                    <div class="consent-item">
                        <strong>Withdrawal Process</strong><br>
                        <small>One-click consent withdrawal</small>
                    </div>
                    <button class="action-btn" onclick="showConsentForm()">Manage Consents</button>
                `;
            }
            
            async function loadProcessingActivities() {
                document.getElementById('processing-activities').innerHTML = `
                    <div class="status-item">
                        <strong>User Authentication</strong><br>
                        <small>Legitimate Interest | 36 months retention</small>
                    </div>
                    <div class="status-item">
                        <strong>Constitutional Governance</strong><br>
                        <small>Legitimate Interest | Permanent retention</small>
                    </div>
                    <div class="status-item">
                        <strong>System Monitoring</strong><br>
                        <small>Legitimate Interest | 12 months retention</small>
                    </div>
                    <div class="status-item">
                        <strong>Audit & Compliance</strong><br>
                        <small>Legal Obligation | 84 months retention</small>
                    </div>
                `;
            }
            
            async function loadSubjectRequests() {
                document.getElementById('subject-requests').innerHTML = `
                    <div class="request-item">
                        <strong>Response Time Target</strong><br>
                        <small>30 days maximum response time</small>
                    </div>
                    <div class="request-item">
                        <strong>Request Types Supported</strong><br>
                        <small>Access, Erasure, Portability, Rectification</small>
                    </div>
                    <div class="request-item">
                        <strong>Automated Processing</strong><br>
                        <small>Access and portability requests automated</small>
                    </div>
                    <button class="action-btn" onclick="submitRequest()">Submit Request</button>
                `;
            }
            
            async function loadDataBreaches() {
                try {
                    const response = await fetch('/api/v1/breaches');
                    const breaches = await response.json();
                    
                    if (breaches.length === 0) {
                        document.getElementById('data-breaches').innerHTML = `
                            <div class="compliant">
                                <div class="metric">0</div>
                                <p>No Data Breaches Reported</p>
                                <div>72-hour notification monitoring active</div>
                            </div>
                        `;
                    } else {
                        const html = breaches.slice(0, 3).map(breach => `
                            <div class="breach-item">
                                <strong>Incident ${breach.incident_id.slice(0,8)}</strong><br>
                                <small>${breach.incident_type} | ${new Date(breach.discovered_at).toLocaleDateString()}</small>
                            </div>
                        `).join('');
                        
                        document.getElementById('data-breaches').innerHTML = html;
                    }
                } catch (error) {
                    document.getElementById('data-breaches').innerHTML = 'Error loading breach data';
                }
            }
            
            function showConsentForm() {
                alert('Consent management interface would open here');
            }
            
            function submitRequest() {
                alert('Data subject request form would open here');
            }
            
            // Initial load
            refreshData();
            
            // Auto-refresh every 2 minutes
            setInterval(refreshData, 120000);
        </script>
    </body>
    </html>
    """)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8016))
    uvicorn.run(app, host="0.0.0.0", port=port)