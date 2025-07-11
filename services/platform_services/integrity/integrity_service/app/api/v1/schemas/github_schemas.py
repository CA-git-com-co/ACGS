"""
GitHub Webhook Schemas for ACGS Integrity Service
Constitutional Hash: cdd01ef066bc6cf2

Pydantic schemas for GitHub webhook payload validation and response models.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


# Request schemas
class GitHubCommit(BaseModel):
    """GitHub commit information."""
    id: str
    message: str
    timestamp: Optional[str] = None
    author: Optional[Dict[str, Any]] = None
    url: Optional[str] = None


class GitHubRepository(BaseModel):
    """GitHub repository information."""
    id: int
    name: str
    full_name: str
    private: bool = False
    archived: bool = False
    url: Optional[str] = None
    description: Optional[str] = None


class GitHubPullRequest(BaseModel):
    """GitHub pull request information."""
    id: int
    number: int
    title: str
    body: Optional[str] = None
    state: str
    draft: bool = False
    base: Optional[Dict[str, Any]] = None
    head: Optional[Dict[str, Any]] = None
    user: Optional[Dict[str, Any]] = None


class GitHubSecurityAdvisory(BaseModel):
    """GitHub security advisory information."""
    ghsa_id: str
    summary: str
    description: Optional[str] = None
    severity: str
    identifiers: Optional[List[Dict[str, Any]]] = None
    references: Optional[List[Dict[str, Any]]] = None


class GitHubCodeScanningAlert(BaseModel):
    """GitHub code scanning alert information."""
    number: int
    state: str
    rule: Dict[str, Any]
    tool: Optional[Dict[str, Any]] = None
    most_recent_instance: Optional[Dict[str, Any]] = None


# Webhook payload schemas
class GitHubPushPayload(BaseModel):
    """GitHub push event payload."""
    ref: str
    before: str
    after: str
    commits: List[GitHubCommit]
    repository: GitHubRepository
    pusher: Optional[Dict[str, Any]] = None
    head_commit: Optional[GitHubCommit] = None


class GitHubPullRequestPayload(BaseModel):
    """GitHub pull request event payload."""
    action: str
    number: int
    pull_request: GitHubPullRequest
    repository: GitHubRepository
    sender: Optional[Dict[str, Any]] = None


class GitHubSecurityAdvisoryPayload(BaseModel):
    """GitHub security advisory event payload."""
    action: str
    security_advisory: GitHubSecurityAdvisory
    repository: GitHubRepository
    sender: Optional[Dict[str, Any]] = None


class GitHubCodeScanningPayload(BaseModel):
    """GitHub code scanning alert event payload."""
    action: str
    alert: GitHubCodeScanningAlert
    repository: GitHubRepository
    sender: Optional[Dict[str, Any]] = None


class GitHubRepositoryPayload(BaseModel):
    """GitHub repository event payload."""
    action: str
    repository: GitHubRepository
    sender: Optional[Dict[str, Any]] = None


# Response schemas
class ConstitutionalComplianceCheck(BaseModel):
    """Constitutional compliance validation result."""
    compliant: bool
    constitutional_hash: str = CONSTITUTIONAL_HASH
    violations: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


class GitHubWebhookProcessingResult(BaseModel):
    """Result of processing a GitHub webhook."""
    event_type: str
    repository: str
    processed_at: datetime
    constitutional_hash: str = CONSTITUTIONAL_HASH
    compliance_check: Optional[ConstitutionalComplianceCheck] = None
    audit_entry_created: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GitHubPushProcessingResult(GitHubWebhookProcessingResult):
    """Result of processing a GitHub push event."""
    ref: str
    commit_count: int
    compliance_violations: List[Dict[str, Any]] = Field(default_factory=list)
    constitutional_commits: List[str] = Field(default_factory=list)


class GitHubPullRequestProcessingResult(GitHubWebhookProcessingResult):
    """Result of processing a GitHub pull request event."""
    action: str
    pr_number: int
    pr_title: str
    governance_flags: List[str] = Field(default_factory=list)
    requires_constitutional_validation: bool = False
    has_constitutional_hash: bool = False
    constitutional_compliance: bool = True


class GitHubSecurityProcessingResult(GitHubWebhookProcessingResult):
    """Result of processing a GitHub security event."""
    severity: Optional[str] = None
    requires_immediate_attention: bool = False
    security_context: Dict[str, Any] = Field(default_factory=dict)


class GitHubWebhookResponse(BaseModel):
    """Standard GitHub webhook response."""
    status: str
    message: str = ""
    event_type: str
    delivery_id: Optional[str] = None
    constitutional_hash: str = CONSTITUTIONAL_HASH
    audit_recorded: bool = False
    processing_result: Optional[GitHubWebhookProcessingResult] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class GitHubWebhookConfig(BaseModel):
    """GitHub webhook configuration."""
    supported_events: Dict[str, str]
    webhook_url: str
    required_headers: List[str]
    constitutional_compliance: Dict[str, Any]
    configuration_guide: Dict[str, Any]


class GitHubWebhookHealth(BaseModel):
    """GitHub webhook service health status."""
    status: str
    service: str = "github-webhooks"
    constitutional_hash: str = CONSTITUTIONAL_HASH
    supported_events: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metrics: Optional[Dict[str, Any]] = None


# Test schemas
class GitHubWebhookTestPayload(BaseModel):
    """Test payload for webhook testing."""
    event_type: str = "push"
    repository_name: str = "test/repo"
    test_data: Dict[str, Any] = Field(default_factory=dict)
    constitutional_hash: str = CONSTITUTIONAL_HASH


class GitHubWebhookTestResponse(BaseModel):
    """Response for webhook testing."""
    status: str = "test_processed"
    constitutional_hash: str = CONSTITUTIONAL_HASH
    test_data: GitHubWebhookProcessingResult
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    validation_results: Optional[Dict[str, Any]] = None


# Audit trail integration schemas
class GitHubAuditEntry(BaseModel):
    """Audit trail entry for GitHub webhook events."""
    event_type: str = "github_webhook"
    event_data: GitHubWebhookProcessingResult
    constitutional_hash: str = CONSTITUTIONAL_HASH
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str = "github_integration"
    integrity_validation: Optional[Dict[str, Any]] = None
    cryptographic_proof: Optional[str] = None


# Configuration and management schemas
class GitHubIntegrationSettings(BaseModel):
    """GitHub integration configuration settings."""
    webhook_secret: Optional[str] = Field(None, description="Webhook signature verification secret")
    signature_verification_enabled: bool = True
    constitutional_validation_enabled: bool = True
    audit_trail_enabled: bool = True
    supported_events: List[str] = Field(default_factory=lambda: [
        "push", "pull_request", "security_advisory", 
        "code_scanning_alert", "repository", "release", "issues"
    ])
    constitutional_hash: str = CONSTITUTIONAL_HASH
    
    class Config:
        schema_extra = {
            "example": {
                "webhook_secret": "your-secure-webhook-secret",
                "signature_verification_enabled": True,
                "constitutional_validation_enabled": True,
                "audit_trail_enabled": True,
                "supported_events": ["push", "pull_request", "security_advisory"],
                "constitutional_hash": CONSTITUTIONAL_HASH
            }
        }


class GitHubIntegrationStatus(BaseModel):
    """GitHub integration operational status."""
    enabled: bool = True
    last_webhook_received: Optional[datetime] = None
    total_webhooks_processed: int = 0
    successful_processsing_rate: float = 0.0
    constitutional_compliance_rate: float = 0.0
    constitutional_hash: str = CONSTITUTIONAL_HASH
    health_status: str = "healthy"
    error_count: int = 0
    last_error: Optional[str] = None