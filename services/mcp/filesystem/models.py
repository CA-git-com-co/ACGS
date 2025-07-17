"""
Domain Models for Filesystem MCP Service
Constitutional Hash: cdd01ef066bc6cf2
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from uuid import UUID, uuid4
from pathlib import Path


# Filesystem Operation Types
class FileOperationType(Enum):
    """Types of filesystem operations"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    LIST = "list"
    CREATE_DIRECTORY = "create_directory"
    COPY = "copy"
    MOVE = "move"
    STAT = "stat"


class FileType(Enum):
    """File types"""
    FILE = "file"
    DIRECTORY = "directory"
    SYMLINK = "symlink"
    OTHER = "other"


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
    """Constitutional context for filesystem operations"""
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
class FilePermissions:
    """File permissions and access control"""
    owner_read: bool = True
    owner_write: bool = True
    owner_execute: bool = False
    group_read: bool = True
    group_write: bool = False
    group_execute: bool = False
    other_read: bool = False
    other_write: bool = False
    other_execute: bool = False
    
    def to_octal(self) -> str:
        """Convert to octal notation"""
        owner = (4 if self.owner_read else 0) + (2 if self.owner_write else 0) + (1 if self.owner_execute else 0)
        group = (4 if self.group_read else 0) + (2 if self.group_write else 0) + (1 if self.group_execute else 0)
        other = (4 if self.other_read else 0) + (2 if self.other_write else 0) + (1 if self.other_execute else 0)
        return f"{owner}{group}{other}"


@dataclass
class FileMetadata:
    """File metadata information"""
    name: str
    path: str
    type: FileType
    size: int
    mime_type: str
    created_at: datetime
    modified_at: datetime
    accessed_at: datetime
    permissions: FilePermissions
    owner: str = "unknown"
    group: str = "unknown"
    is_hidden: bool = False
    is_readonly: bool = False
    security_level: SecurityLevel = SecurityLevel.PUBLIC
    constitutional_compliance: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FileOperation:
    """Filesystem operation record"""
    operation_id: UUID = field(default_factory=uuid4)
    operation_type: FileOperationType = FileOperationType.READ
    source_path: str = ""
    target_path: Optional[str] = None
    constitutional_context: ConstitutionalContext = field(default_factory=ConstitutionalContext)
    validation_result: Optional[ConstitutionalValidation] = None
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    success: bool = False
    error_message: Optional[str] = None
    bytes_processed: int = 0
    execution_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FilesystemTool:
    """MCP tool for filesystem operations"""
    name: str
    description: str
    operation_type: FileOperationType
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any] = field(default_factory=dict)
    constitutional_requirements: List[str] = field(default_factory=list)
    security_level: SecurityLevel = SecurityLevel.PUBLIC
    requires_approval: bool = False
    timeout_seconds: int = 30
    max_file_size: Optional[int] = None
    allowed_extensions: List[str] = field(default_factory=list)
    forbidden_paths: List[str] = field(default_factory=list)


@dataclass
class FilesystemResource:
    """MCP resource for filesystem access"""
    uri: str
    name: str
    description: str
    path: str
    type: FileType
    mime_type: str
    security_level: SecurityLevel = SecurityLevel.PUBLIC
    constitutional_access_level: ComplianceLevel = ComplianceLevel.MEDIUM
    size: Optional[int] = None
    last_modified: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SecurityPolicy:
    """Filesystem security policy"""
    policy_id: UUID = field(default_factory=uuid4)
    name: str = "Default Filesystem Policy"
    allowed_base_paths: List[str] = field(default_factory=list)
    forbidden_paths: List[str] = field(default_factory=list)
    forbidden_extensions: List[str] = field(default_factory=list)
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    max_directory_depth: int = 10
    allow_symlinks: bool = False
    allow_hidden_files: bool = False
    require_constitutional_validation: bool = True
    constitutional_hash: str = "cdd01ef066bc6cf2"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PathValidator:
    """Path validation logic"""
    security_policy: SecurityPolicy = field(default_factory=SecurityPolicy)
    
    def validate_path(self, path: str) -> ConstitutionalValidation:
        """Validate filesystem path"""
        try:
            normalized_path = str(Path(path).resolve())
            
            # Check forbidden paths
            for forbidden in self.security_policy.forbidden_paths:
                if normalized_path.startswith(forbidden):
                    return ConstitutionalValidation(
                        is_compliant=False,
                        compliance_score=0.0,
                        violations=[f"Access to forbidden path: {forbidden}"],
                        recommendations=["Use allowed workspace directories"]
                    )
            
            # Check allowed base paths
            if self.security_policy.allowed_base_paths:
                path_allowed = any(
                    normalized_path.startswith(allowed)
                    for allowed in self.security_policy.allowed_base_paths
                )
                
                if not path_allowed:
                    return ConstitutionalValidation(
                        is_compliant=False,
                        compliance_score=0.2,
                        violations=["Path not within allowed directories"],
                        recommendations=[f"Use paths within: {', '.join(self.security_policy.allowed_base_paths)}"]
                    )
            
            # Check file extension
            file_ext = Path(path).suffix.lower()
            if file_ext in self.security_policy.forbidden_extensions:
                return ConstitutionalValidation(
                    is_compliant=False,
                    compliance_score=0.1,
                    violations=[f"Forbidden file extension: {file_ext}"],
                    recommendations=["Use safe file formats"]
                )
            
            # Check directory depth
            depth = len(Path(normalized_path).parts)
            if depth > self.security_policy.max_directory_depth:
                return ConstitutionalValidation(
                    is_compliant=False,
                    compliance_score=0.3,
                    violations=[f"Path depth exceeds maximum: {self.security_policy.max_directory_depth}"],
                    recommendations=["Use shallower directory structures"]
                )
            
            return ConstitutionalValidation(
                is_compliant=True,
                compliance_score=1.0,
                violations=[],
                recommendations=[]
            )
            
        except Exception as e:
            return ConstitutionalValidation(
                is_compliant=False,
                compliance_score=0.0,
                violations=[f"Path validation error: {str(e)}"],
                recommendations=["Provide valid filesystem path"]
            )


@dataclass
class FileSystemMetrics:
    """Metrics for filesystem operations"""
    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    total_bytes_read: int = 0
    total_bytes_written: int = 0
    files_created: int = 0
    files_deleted: int = 0
    directories_created: int = 0
    directories_deleted: int = 0
    average_operation_time_ms: float = 0.0
    peak_operation_time_ms: float = 0.0
    constitutional_violations: int = 0
    security_violations: int = 0
    last_reset: datetime = field(default_factory=datetime.utcnow)
    
    def update_operation_time(self, execution_time_ms: float):
        """Update operation timing metrics"""
        self.total_operations += 1
        self.average_operation_time_ms = (
            (self.average_operation_time_ms * (self.total_operations - 1) + execution_time_ms) /
            self.total_operations
        )
        if execution_time_ms > self.peak_operation_time_ms:
            self.peak_operation_time_ms = execution_time_ms


@dataclass
class MCPRequest:
    """MCP request for filesystem operations"""
    request_id: UUID = field(default_factory=uuid4)
    method: str = ""
    tool_name: Optional[str] = None
    arguments: Dict[str, Any] = field(default_factory=dict)
    constitutional_context: ConstitutionalContext = field(default_factory=ConstitutionalContext)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    client_id: Optional[str] = None
    session_id: Optional[UUID] = None


@dataclass
class MCPResponse:
    """MCP response for filesystem operations"""
    request_id: UUID = field(default_factory=uuid4)
    success: bool = True
    content: List[Dict[str, Any]] = field(default_factory=list)
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    constitutional_validation: Optional[ConstitutionalValidation] = None
    execution_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DirectoryListing:
    """Directory listing result"""
    path: str
    entries: List[FileMetadata] = field(default_factory=list)
    total_count: int = 0
    total_size: int = 0
    recursive: bool = False
    constitutional_compliance: float = 1.0
    access_restrictions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FileContent:
    """File content container"""
    path: str
    content: Union[str, bytes]
    encoding: str = "utf-8"
    mime_type: str = "text/plain"
    size: int = 0
    checksum: Optional[str] = None
    constitutional_compliance: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FilesystemAuditEntry:
    """Audit entry for filesystem operations"""
    audit_id: UUID = field(default_factory=uuid4)
    operation: FileOperation = field(default_factory=FileOperation)
    user_context: Dict[str, Any] = field(default_factory=dict)
    constitutional_context: ConstitutionalContext = field(default_factory=ConstitutionalContext)
    validation_result: ConstitutionalValidation = field(default_factory=ConstitutionalValidation)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert audit entry to dictionary"""
        return {
            "audit_id": str(self.audit_id),
            "operation_id": str(self.operation.operation_id),
            "operation_type": self.operation.operation_type.value,
            "source_path": self.operation.source_path,
            "target_path": self.operation.target_path,
            "success": self.operation.success,
            "bytes_processed": self.operation.bytes_processed,
            "execution_time_ms": self.operation.execution_time_ms,
            "constitutional_compliance": self.validation_result.is_compliant,
            "compliance_score": self.validation_result.compliance_score,
            "violations": self.validation_result.violations,
            "timestamp": self.timestamp.isoformat(),
            "constitutional_hash": self.constitutional_context.constitutional_hash
        }


@dataclass
class FilesystemConfiguration:
    """Configuration for filesystem MCP service"""
    service_name: str = "Filesystem MCP Service"
    service_version: str = "1.0.0"
    constitutional_hash: str = "cdd01ef066bc6cf2"
    security_policy: SecurityPolicy = field(default_factory=SecurityPolicy)
    enable_audit_logging: bool = True
    enable_metrics: bool = True
    enable_constitutional_validation: bool = True
    max_concurrent_operations: int = 100
    operation_timeout_seconds: int = 30
    temp_directory: str = "/tmp/filesystem_mcp"
    workspace_directories: List[str] = field(default_factory=lambda: [
        "/app/data", "/app/workspace", "/app/temp", "/app/uploads"
    ])


@dataclass
class FilesystemCapabilities:
    """Capabilities of the filesystem MCP service"""
    can_read_files: bool = True
    can_write_files: bool = True
    can_delete_files: bool = True
    can_create_directories: bool = True
    can_list_directories: bool = True
    can_copy_files: bool = True
    can_move_files: bool = True
    can_get_file_stats: bool = True
    supports_symlinks: bool = False
    supports_binary_files: bool = True
    supports_large_files: bool = True
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    supported_encodings: List[str] = field(default_factory=lambda: ["utf-8", "ascii", "latin-1"])
    constitutional_validation: bool = True