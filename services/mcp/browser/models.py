"""
Domain Models for Browser MCP Service
Constitutional Hash: cdd01ef066bc6cf2
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from uuid import UUID, uuid4


# Browser Operation Types
class BrowserOperationType(Enum):
    """Types of browser operations"""
    NAVIGATE = "navigate"
    EXTRACT_TEXT = "extract_text"
    SEARCH_PAGE = "search_page"
    GET_LINKS = "get_links"
    TAKE_SCREENSHOT = "take_screenshot"
    FILL_FORM = "fill_form"
    CLICK_ELEMENT = "click_element"
    SCROLL_PAGE = "scroll_page"
    WAIT_FOR_ELEMENT = "wait_for_element"


class PageLoadStatus(Enum):
    """Page load status"""
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    BLOCKED = "blocked"
    REDIRECTED = "redirected"


class ElementType(Enum):
    """Web element types"""
    LINK = "link"
    BUTTON = "button"
    INPUT = "input"
    TEXT = "text"
    IMAGE = "image"
    FORM = "form"
    DIV = "div"
    SPAN = "span"
    HEADING = "heading"
    PARAGRAPH = "paragraph"


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
    """Constitutional context for browser operations"""
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
class WebPage:
    """Web page information"""
    url: str
    title: str
    content: str
    meta_description: str = ""
    meta_keywords: str = ""
    language: str = "en"
    charset: str = "utf-8"
    status_code: int = 200
    content_type: str = "text/html"
    content_length: int = 0
    load_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    links: List[Dict[str, str]] = field(default_factory=list)
    headings: List[Dict[str, Any]] = field(default_factory=list)
    paragraphs: List[str] = field(default_factory=list)
    images: List[Dict[str, str]] = field(default_factory=list)
    forms: List[Dict[str, Any]] = field(default_factory=list)
    scripts: List[str] = field(default_factory=list)
    stylesheets: List[str] = field(default_factory=list)
    security_level: SecurityLevel = SecurityLevel.PUBLIC
    constitutional_compliance: float = 1.0


@dataclass
class WebElement:
    """Web page element"""
    tag_name: str
    element_type: ElementType
    text: str = ""
    attributes: Dict[str, str] = field(default_factory=dict)
    xpath: str = ""
    css_selector: str = ""
    position: Dict[str, int] = field(default_factory=dict)  # x, y, width, height
    is_visible: bool = True
    is_clickable: bool = False
    is_editable: bool = False
    parent_element: Optional[str] = None
    child_elements: List[str] = field(default_factory=list)


@dataclass
class NavigationResult:
    """Result of navigation operation"""
    success: bool
    url: str = ""
    final_url: str = ""  # After redirects
    page: Optional[WebPage] = None
    status_code: int = 0
    error_message: str = ""
    load_time: float = 0.0
    redirects: List[str] = field(default_factory=list)
    constitutional_validation: Optional[ConstitutionalValidation] = None
    execution_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BrowserOperation:
    """Browser operation record"""
    operation_id: UUID = field(default_factory=uuid4)
    operation_type: BrowserOperationType = BrowserOperationType.NAVIGATE
    url: str = ""
    target_element: Optional[str] = None
    input_data: Dict[str, Any] = field(default_factory=dict)
    constitutional_context: ConstitutionalContext = field(default_factory=ConstitutionalContext)
    validation_result: Optional[ConstitutionalValidation] = None
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    success: bool = False
    error_message: Optional[str] = None
    result_data: Dict[str, Any] = field(default_factory=dict)
    execution_time_ms: float = 0.0
    bytes_downloaded: int = 0
    requests_made: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WebResource:
    """Web resource (images, scripts, etc.)"""
    url: str
    resource_type: str  # image, script, stylesheet, etc.
    mime_type: str
    size: int = 0
    status_code: int = 200
    load_time: float = 0.0
    cached: bool = False
    security_level: SecurityLevel = SecurityLevel.PUBLIC
    constitutional_compliance: float = 1.0


@dataclass
class FormData:
    """Form data for submission"""
    form_selector: str
    fields: Dict[str, str] = field(default_factory=dict)
    submit_button: Optional[str] = None
    method: str = "POST"
    action: str = ""
    encoding: str = "application/x-www-form-urlencoded"
    constitutional_context: ConstitutionalContext = field(default_factory=ConstitutionalContext)


@dataclass
class ScreenshotResult:
    """Screenshot operation result"""
    success: bool
    image_data: Optional[bytes] = None
    image_format: str = "png"
    width: int = 0
    height: int = 0
    file_size: int = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    error_message: str = ""
    constitutional_compliance: float = 1.0


@dataclass
class BrowserMetrics:
    """Metrics for browser operations"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    pages_loaded: int = 0
    total_bytes_downloaded: int = 0
    total_load_time_ms: float = 0.0
    average_page_load_time_ms: float = 0.0
    peak_load_time_ms: float = 0.0
    urls_visited: set = field(default_factory=set)
    domains_accessed: set = field(default_factory=set)
    constitutional_violations: int = 0
    security_violations: int = 0
    blocked_requests: int = 0
    redirects_followed: int = 0
    forms_submitted: int = 0
    elements_clicked: int = 0
    screenshots_taken: int = 0
    last_reset: datetime = field(default_factory=datetime.utcnow)
    
    def update_load_time(self, load_time_ms: float):
        """Update page load timing metrics"""
        self.total_requests += 1
        self.total_load_time_ms += load_time_ms
        self.average_page_load_time_ms = self.total_load_time_ms / self.total_requests
        if load_time_ms > self.peak_load_time_ms:
            self.peak_load_time_ms = load_time_ms


@dataclass
class BrowserSecurityPolicy:
    """Security policy for browser operations"""
    allowed_domains: set = field(default_factory=set)
    forbidden_domains: set = field(default_factory=set)
    forbidden_patterns: set = field(default_factory=set)
    max_page_size: int = 10 * 1024 * 1024  # 10MB
    max_redirects: int = 10
    request_timeout: int = 30
    max_concurrent_requests: int = 5
    user_agent: str = "ACGS-2-Browser-MCP/1.0"
    allow_javascript: bool = False
    allow_cookies: bool = False
    allow_popups: bool = False
    allow_downloads: bool = False
    block_ads: bool = True
    block_trackers: bool = True
    require_constitutional_validation: bool = True
    constitutional_hash: str = "cdd01ef066bc6cf2"
    
    def is_domain_allowed(self, domain: str) -> bool:
        """Check if domain is allowed"""
        domain = domain.lower()
        
        # Check forbidden domains
        for forbidden in self.forbidden_domains:
            if forbidden in domain or domain.endswith(f".{forbidden}"):
                return False
        
        # Check allowed domains (if specified)
        if self.allowed_domains:
            return any(
                allowed in domain or domain.endswith(f".{allowed}")
                for allowed in self.allowed_domains
            )
        
        return True


@dataclass
class SearchResult:
    """Search result within a page"""
    term: str
    url: str
    total_matches: int = 0
    matches: List[Dict[str, Any]] = field(default_factory=list)
    search_time_ms: float = 0.0
    constitutional_compliance: float = 1.0


@dataclass
class LinkExtraction:
    """Link extraction result"""
    url: str
    total_links: int = 0
    internal_links: List[Dict[str, str]] = field(default_factory=list)
    external_links: List[Dict[str, str]] = field(default_factory=list)
    broken_links: List[Dict[str, str]] = field(default_factory=list)
    mailto_links: List[str] = field(default_factory=list)
    javascript_links: List[str] = field(default_factory=list)
    extraction_time_ms: float = 0.0
    constitutional_compliance: float = 1.0


@dataclass
class TextExtraction:
    """Text extraction result"""
    url: str
    raw_text: str
    clean_text: str
    word_count: int = 0
    character_count: int = 0
    paragraph_count: int = 0
    heading_count: int = 0
    language: str = "en"
    readability_score: Optional[float] = None
    extraction_time_ms: float = 0.0
    constitutional_compliance: float = 1.0


@dataclass
class BrowserSession:
    """Browser session information"""
    session_id: UUID = field(default_factory=uuid4)
    user_agent: str = ""
    viewport_size: Dict[str, int] = field(default_factory=lambda: {"width": 1920, "height": 1080})
    current_url: str = ""
    history: List[str] = field(default_factory=list)
    cookies: Dict[str, str] = field(default_factory=dict)
    local_storage: Dict[str, str] = field(default_factory=dict)
    session_storage: Dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
    constitutional_context: ConstitutionalContext = field(default_factory=ConstitutionalContext)


@dataclass
class BrowserAuditEntry:
    """Audit entry for browser operations"""
    audit_id: UUID = field(default_factory=uuid4)
    operation: BrowserOperation = field(default_factory=BrowserOperation)
    session_id: Optional[UUID] = None
    user_context: Dict[str, Any] = field(default_factory=dict)
    constitutional_context: ConstitutionalContext = field(default_factory=ConstitutionalContext)
    validation_result: ConstitutionalValidation = field(default_factory=ConstitutionalValidation)
    page_content_hash: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert audit entry to dictionary"""
        return {
            "audit_id": str(self.audit_id),
            "operation_id": str(self.operation.operation_id),
            "operation_type": self.operation.operation_type.value,
            "url": self.operation.url,
            "success": self.operation.success,
            "bytes_downloaded": self.operation.bytes_downloaded,
            "requests_made": self.operation.requests_made,
            "execution_time_ms": self.operation.execution_time_ms,
            "constitutional_compliance": self.validation_result.is_compliant,
            "compliance_score": self.validation_result.compliance_score,
            "violations": self.validation_result.violations,
            "timestamp": self.timestamp.isoformat(),
            "constitutional_hash": self.constitutional_context.constitutional_hash
        }


@dataclass
class BrowserConfiguration:
    """Configuration for browser MCP service"""
    service_name: str = "Browser MCP Service"
    service_version: str = "1.0.0"
    constitutional_hash: str = "cdd01ef066bc6cf2"
    security_policy: BrowserSecurityPolicy = field(default_factory=BrowserSecurityPolicy)
    enable_audit_logging: bool = True
    enable_metrics: bool = True
    enable_constitutional_validation: bool = True
    max_concurrent_sessions: int = 10
    session_timeout_seconds: int = 3600
    page_cache_size: int = 100
    page_cache_ttl_seconds: int = 300
    enable_javascript: bool = False
    enable_images: bool = True
    enable_css: bool = True
    proxy_url: Optional[str] = None
    custom_headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class BrowserCapabilities:
    """Capabilities of the browser MCP service"""
    can_navigate: bool = True
    can_extract_text: bool = True
    can_extract_links: bool = True
    can_search_content: bool = True
    can_take_screenshots: bool = False  # Requires additional dependencies
    can_fill_forms: bool = False  # Restricted for security
    can_click_elements: bool = False  # Restricted for security
    can_execute_javascript: bool = False  # Disabled for security
    can_download_files: bool = False  # Disabled for security
    can_upload_files: bool = False  # Disabled for security
    supports_authentication: bool = False  # Disabled for security
    supports_cookies: bool = False  # Disabled for privacy
    max_page_size: int = 10 * 1024 * 1024  # 10MB
    supported_content_types: List[str] = field(default_factory=lambda: [
        "text/html", "text/plain", "application/xhtml+xml"
    ])
    constitutional_validation: bool = True
    security_filtering: bool = True