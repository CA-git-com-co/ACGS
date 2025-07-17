"""
Domain Models for GitHub MCP Service
Constitutional Hash: cdd01ef066bc6cf2
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from uuid import UUID, uuid4


# GitHub Operation Types
class GitHubOperationType(Enum):
    """Types of GitHub operations"""
    READ_REPOSITORY = "read_repository"
    LIST_REPOSITORIES = "list_repositories"
    GET_FILE = "get_file"
    LIST_FILES = "list_files"
    CREATE_FILE = "create_file"
    UPDATE_FILE = "update_file"
    DELETE_FILE = "delete_file"
    GET_ISSUES = "get_issues"
    CREATE_ISSUE = "create_issue"
    UPDATE_ISSUE = "update_issue"
    GET_PULL_REQUESTS = "get_pull_requests"
    CREATE_PULL_REQUEST = "create_pull_request"
    GET_USER = "get_user"
    SEARCH_REPOSITORIES = "search_repositories"
    GET_COMMITS = "get_commits"
    GET_BRANCHES = "get_branches"


class RepositoryVisibility(Enum):
    """Repository visibility levels"""
    PUBLIC = "public"
    PRIVATE = "private"
    INTERNAL = "internal"


class IssueState(Enum):
    """GitHub issue states"""
    OPEN = "open"
    CLOSED = "closed"
    ALL = "all"


class PullRequestState(Enum):
    """GitHub pull request states"""
    OPEN = "open"
    CLOSED = "closed"
    MERGED = "merged"
    ALL = "all"


class ComplianceLevel(Enum):
    """Constitutional compliance levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class SecurityLevel(Enum):
    """Security access levels"""
    PUBLIC = "public"
    RESTRICTED = "restricted"
    CONFIDENTIAL = "confidential"
    SECRET = "secret"


# Core Domain Models

@dataclass
class ConstitutionalContext:
    """Constitutional context for GitHub operations"""
    constitutional_hash: str = "cdd01ef066bc6cf2"
    purpose: str = ""
    tenant_id: Optional[str] = None
    compliance_level: ComplianceLevel = ComplianceLevel.HIGH
    additional_constraints: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConstitutionalValidation:
    """Result of constitutional validation"""
    is_compliant: bool
    compliance_score: float  # 0.0 to 1.0
    violations: List[str]
    recommendations: List[str]
    validation_timestamp: datetime = field(default_factory=datetime.utcnow)
    validator_version: str = "1.0.0"


@dataclass
class GitHubUser:
    """GitHub user information"""
    id: int
    login: str
    name: Optional[str] = None
    email: Optional[str] = None
    bio: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    blog: Optional[str] = None
    avatar_url: str = ""
    html_url: str = ""
    public_repos: int = 0
    public_gists: int = 0
    followers: int = 0
    following: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    type: str = "User"
    site_admin: bool = False


@dataclass
class GitHubRepository:
    """GitHub repository information"""
    id: int
    name: str
    full_name: str
    owner: GitHubUser
    description: Optional[str] = None
    homepage: Optional[str] = None
    html_url: str = ""
    clone_url: str = ""
    git_url: str = ""
    ssh_url: str = ""
    visibility: RepositoryVisibility = RepositoryVisibility.PUBLIC
    private: bool = False
    fork: bool = False
    archived: bool = False
    disabled: bool = False
    default_branch: str = "main"
    language: Optional[str] = None
    languages_url: str = ""
    size: int = 0
    stargazers_count: int = 0
    watchers_count: int = 0
    forks_count: int = 0
    open_issues_count: int = 0
    has_issues: bool = True
    has_projects: bool = True
    has_wiki: bool = True
    has_pages: bool = False
    has_downloads: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    pushed_at: Optional[datetime] = None
    license: Optional[Dict[str, Any]] = None
    topics: List[str] = field(default_factory=list)
    security_level: SecurityLevel = SecurityLevel.PUBLIC
    constitutional_compliance: float = 1.0


@dataclass
class GitHubFile:
    """GitHub file information"""
    name: str
    path: str
    sha: str
    size: int
    type: str  # "file" or "dir"
    download_url: Optional[str] = None
    git_url: str = ""
    html_url: str = ""
    encoding: Optional[str] = None
    content: Optional[str] = None
    decoded_content: Optional[str] = None
    mime_type: str = "text/plain"
    is_binary: bool = False
    is_sensitive: bool = False
    security_level: SecurityLevel = SecurityLevel.PUBLIC
    constitutional_compliance: float = 1.0


@dataclass
class GitHubIssue:
    """GitHub issue information"""
    id: int
    number: int
    title: str
    body: Optional[str] = None
    user: Optional[GitHubUser] = None
    assignee: Optional[GitHubUser] = None
    assignees: List[GitHubUser] = field(default_factory=list)
    state: IssueState = IssueState.OPEN
    locked: bool = False
    milestone: Optional[Dict[str, Any]] = None
    comments: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    html_url: str = ""
    labels: List[Dict[str, Any]] = field(default_factory=list)
    repository_url: str = ""


@dataclass
class GitHubPullRequest:
    """GitHub pull request information"""
    id: int
    number: int
    title: str
    body: Optional[str] = None
    user: Optional[GitHubUser] = None
    assignee: Optional[GitHubUser] = None
    assignees: List[GitHubUser] = field(default_factory=list)
    state: PullRequestState = PullRequestState.OPEN
    locked: bool = False
    draft: bool = False
    merged: bool = False
    mergeable: Optional[bool] = None
    merged_at: Optional[datetime] = None
    merge_commit_sha: Optional[str] = None
    head: Optional[Dict[str, Any]] = None
    base: Optional[Dict[str, Any]] = None
    milestone: Optional[Dict[str, Any]] = None
    comments: int = 0
    review_comments: int = 0
    commits: int = 0
    additions: int = 0
    deletions: int = 0
    changed_files: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    html_url: str = ""
    diff_url: str = ""
    patch_url: str = ""
    labels: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class GitHubCommit:
    """GitHub commit information"""
    sha: str
    commit: Dict[str, Any]
    author: Optional[GitHubUser] = None
    committer: Optional[GitHubUser] = None
    parents: List[Dict[str, str]] = field(default_factory=list)
    stats: Optional[Dict[str, int]] = None
    files: List[Dict[str, Any]] = field(default_factory=list)
    html_url: str = ""


@dataclass
class GitHubBranch:
    """GitHub branch information"""
    name: str
    commit: Dict[str, Any]
    protected: bool = False
    protection_url: str = ""


@dataclass
class GitHubOperation:
    """GitHub operation record"""
    operation_id: UUID = field(default_factory=uuid4)
    operation_type: GitHubOperationType = GitHubOperationType.READ_REPOSITORY
    repository: Optional[str] = None
    file_path: Optional[str] = None
    constitutional_context: ConstitutionalContext = field(default_factory=ConstitutionalContext)
    validation_result: Optional[ConstitutionalValidation] = None
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    success: bool = False
    error_message: Optional[str] = None
    api_calls: int = 0
    rate_limit_hit: bool = False
    execution_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RepositoryPermissions:
    """Repository access permissions"""
    admin: bool = False
    maintain: bool = False
    push: bool = False
    triage: bool = False
    pull: bool = True


@dataclass
class GitHubAPIRateLimits:
    """GitHub API rate limit information"""
    core_limit: int = 5000
    core_remaining: int = 5000
    core_reset: int = 0
    search_limit: int = 30
    search_remaining: int = 30
    search_reset: int = 0
    graphql_limit: int = 5000
    graphql_remaining: int = 5000
    graphql_reset: int = 0
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class GitHubMetrics:
    """Metrics for GitHub operations"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    rate_limit_hits: int = 0
    repositories_accessed: int = 0
    files_read: int = 0
    files_written: int = 0
    issues_accessed: int = 0
    pull_requests_accessed: int = 0
    users_accessed: int = 0
    search_operations: int = 0
    average_response_time_ms: float = 0.0
    peak_response_time_ms: float = 0.0
    constitutional_violations: int = 0
    security_violations: int = 0
    last_reset: datetime = field(default_factory=datetime.utcnow)
    
    def update_response_time(self, response_time_ms: float):
        """Update response timing metrics"""
        self.total_requests += 1
        self.average_response_time_ms = (
            (self.average_response_time_ms * (self.total_requests - 1) + response_time_ms) /
            self.total_requests
        )
        if response_time_ms > self.peak_response_time_ms:
            self.peak_response_time_ms = response_time_ms


@dataclass
class GitHubSecurityPolicy:
    """Security policy for GitHub operations"""
    allowed_operations: set = field(default_factory=lambda: {
        "read_repository", "list_repositories", "get_file", "list_files",
        "get_issues", "list_issues", "get_pull_requests", "list_pull_requests",
        "get_user", "search_repositories", "get_commits", "get_branches"
    })
    restricted_operations: set = field(default_factory=lambda: {
        "create_issue", "update_issue", "create_pull_request",
        "create_file", "update_file", "delete_file",
        "create_repository", "delete_repository"
    })
    forbidden_operations: set = field(default_factory=lambda: {
        "delete_repository_permanent", "force_push", "modify_webhooks",
        "manage_secrets", "modify_security_settings"
    })
    sensitive_file_patterns: set = field(default_factory=lambda: {
        ".env", "*.key", "*.pem", "*.p12", "*.pfx",
        "config.json", "secrets.yaml", "credentials.json",
        "id_rsa", "id_dsa", "id_ecdsa", "id_ed25519"
    })
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    max_requests_per_hour: int = 1000
    require_constitutional_validation: bool = True
    constitutional_hash: str = "cdd01ef066bc6cf2"


@dataclass
class GitHubSearchResult:
    """GitHub search result"""
    total_count: int
    incomplete_results: bool
    items: List[Dict[str, Any]] = field(default_factory=list)
    search_query: str = ""
    search_type: str = "repositories"
    constitutional_compliance: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GitHubWebhook:
    """GitHub webhook configuration"""
    id: int
    name: str
    active: bool
    events: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    url: str = ""
    test_url: str = ""
    ping_url: str = ""


@dataclass
class GitHubAuditEntry:
    """Audit entry for GitHub operations"""
    audit_id: UUID = field(default_factory=uuid4)
    operation: GitHubOperation = field(default_factory=GitHubOperation)
    user_context: Dict[str, Any] = field(default_factory=dict)
    constitutional_context: ConstitutionalContext = field(default_factory=ConstitutionalContext)
    validation_result: ConstitutionalValidation = field(default_factory=ConstitutionalValidation)
    api_rate_limit_info: GitHubAPIRateLimits = field(default_factory=GitHubAPIRateLimits)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert audit entry to dictionary"""
        return {
            "audit_id": str(self.audit_id),
            "operation_id": str(self.operation.operation_id),
            "operation_type": self.operation.operation_type.value,
            "repository": self.operation.repository,
            "file_path": self.operation.file_path,
            "success": self.operation.success,
            "api_calls": self.operation.api_calls,
            "rate_limit_hit": self.operation.rate_limit_hit,
            "execution_time_ms": self.operation.execution_time_ms,
            "constitutional_compliance": self.validation_result.is_compliant,
            "compliance_score": self.validation_result.compliance_score,
            "violations": self.validation_result.violations,
            "rate_limit_remaining": self.api_rate_limit_info.core_remaining,
            "timestamp": self.timestamp.isoformat(),
            "constitutional_hash": self.constitutional_context.constitutional_hash
        }


@dataclass
class GitHubConfiguration:
    """Configuration for GitHub MCP service"""
    service_name: str = "GitHub MCP Service"
    service_version: str = "1.0.0"
    constitutional_hash: str = "cdd01ef066bc6cf2"
    api_token: Optional[str] = None
    api_base_url: str = "https://api.github.com"
    security_policy: GitHubSecurityPolicy = field(default_factory=GitHubSecurityPolicy)
    enable_audit_logging: bool = True
    enable_metrics: bool = True
    enable_constitutional_validation: bool = True
    max_concurrent_requests: int = 10
    request_timeout_seconds: int = 30
    rate_limit_buffer: int = 100  # Keep this many requests in reserve
    default_per_page: int = 30
    max_per_page: int = 100


@dataclass
class GitHubCapabilities:
    """Capabilities of the GitHub MCP service"""
    can_read_repositories: bool = True
    can_read_files: bool = True
    can_read_issues: bool = True
    can_read_pull_requests: bool = True
    can_read_users: bool = True
    can_search: bool = True
    can_read_commits: bool = True
    can_read_branches: bool = True
    can_write_files: bool = False  # Requires elevated permissions
    can_create_issues: bool = False  # Requires elevated permissions
    can_create_pull_requests: bool = False  # Requires elevated permissions
    supports_webhooks: bool = False
    supports_graphql: bool = False
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    supported_file_types: List[str] = field(default_factory=lambda: [
        "text/plain", "application/json", "text/markdown", 
        "application/yaml", "application/xml", "text/csv"
    ])
    constitutional_validation: bool = True
    rate_limit_aware: bool = True