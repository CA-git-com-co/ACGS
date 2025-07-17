"""
Filesystem MCP Service
Constitutional Hash: cdd01ef066bc6cf2
Port: 3001

Model Context Protocol service for secure filesystem operations
with constitutional compliance validation.
"""

import asyncio
import os
import json
import logging
import mimetypes
import stat
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .models import (
    FilesystemTool,
    FilesystemResource,
    FileOperation,
    FilePermissions,
    ConstitutionalContext,
    ConstitutionalValidation,
    MCPRequest,
    MCPResponse,
    SecurityPolicy,
    PathValidator,
    FileSystemMetrics
)

# Initialize FastAPI app
app = FastAPI(
    title="Filesystem MCP Service",
    description="Secure filesystem operations with constitutional compliance",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constitutional hash validation
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class FilesystemSecurityPolicy:
    """Security policy for filesystem operations"""
    
    def __init__(self):
        # Allowed base directories (configurable)
        self.allowed_base_paths = {
            "/app/data",
            "/app/workspace", 
            "/app/temp",
            "/app/uploads"
        }
        
        # Forbidden paths (security critical)
        self.forbidden_paths = {
            "/etc", "/sys", "/proc", "/dev", "/root",
            "/boot", "/usr/bin", "/usr/sbin", "/sbin",
            "/.ssh", "/.env", "/var/log/auth.log"
        }
        
        # Forbidden file extensions
        self.forbidden_extensions = {
            ".exe", ".dll", ".so", ".dylib", ".deb", ".rpm",
            ".sh", ".bat", ".cmd", ".ps1", ".scr"
        }
        
        # Maximum file size (100MB)
        self.max_file_size = 100 * 1024 * 1024
        
        # Maximum directory depth
        self.max_depth = 10
    
    def validate_path(self, path: str) -> ConstitutionalValidation:
        """Validate path for security compliance"""
        
        try:
            # Normalize path
            normalized_path = os.path.normpath(os.path.abspath(path))
            
            # Check forbidden paths
            for forbidden in self.forbidden_paths:
                if normalized_path.startswith(forbidden):
                    return ConstitutionalValidation(
                        is_compliant=False,
                        compliance_score=0.0,
                        violations=[f"Access to forbidden path: {forbidden}"],
                        recommendations=["Use allowed workspace directories"]
                    )
            
            # Check if path is within allowed base paths
            path_allowed = False
            for allowed_base in self.allowed_base_paths:
                if normalized_path.startswith(allowed_base):
                    path_allowed = True
                    break
            
            if not path_allowed:
                return ConstitutionalValidation(
                    is_compliant=False,
                    compliance_score=0.2,
                    violations=["Path not within allowed directories"],
                    recommendations=[f"Use paths within: {', '.join(self.allowed_base_paths)}"]
                )
            
            # Check file extension
            file_ext = Path(normalized_path).suffix.lower()
            if file_ext in self.forbidden_extensions:
                return ConstitutionalValidation(
                    is_compliant=False,
                    compliance_score=0.1,
                    violations=[f"Forbidden file extension: {file_ext}"],
                    recommendations=["Use safe file formats for data exchange"]
                )
            
            # Check directory depth
            depth = len(Path(normalized_path).parts)
            if depth > self.max_depth:
                return ConstitutionalValidation(
                    is_compliant=False,
                    compliance_score=0.3,
                    violations=[f"Path depth exceeds maximum: {self.max_depth}"],
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


class FilesystemOperations:
    """Core filesystem operations with constitutional compliance"""
    
    def __init__(self):
        self.security_policy = FilesystemSecurityPolicy()
        self.metrics = FileSystemMetrics()
    
    async def read_file(
        self,
        file_path: str,
        constitutional_context: ConstitutionalContext
    ) -> Dict[str, Any]:
        """Read file with constitutional validation"""
        
        start_time = datetime.utcnow()
        
        # Validate path
        validation = self.security_policy.validate_path(file_path)
        if not validation.is_compliant:
            self.metrics.failed_operations += 1
            raise HTTPException(
                status_code=403,
                detail=f"Constitutional violation: {validation.violations}"
            )
        
        try:
            path = Path(file_path)
            
            # Check if file exists
            if not path.exists():
                raise HTTPException(status_code=404, detail="File not found")
            
            if not path.is_file():
                raise HTTPException(status_code=400, detail="Path is not a file")
            
            # Check file size
            file_size = path.stat().st_size
            if file_size > self.security_policy.max_file_size:
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large: {file_size} bytes"
                )
            
            # Determine MIME type
            mime_type, _ = mimetypes.guess_type(str(path))
            mime_type = mime_type or "application/octet-stream"
            
            # Read file content
            if mime_type.startswith("text/") or mime_type in [
                "application/json", "application/xml", "application/yaml"
            ]:
                # Text file
                content = path.read_text(encoding="utf-8")
                content_type = "text"
            else:
                # Binary file (base64 encoded)
                import base64
                content = base64.b64encode(path.read_bytes()).decode("utf-8")
                content_type = "blob"
            
            # Update metrics
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            self.metrics.successful_operations += 1
            self.metrics.total_bytes_read += file_size
            self.metrics.average_operation_time_ms = (
                (self.metrics.average_operation_time_ms * (self.metrics.successful_operations - 1) + execution_time) /
                self.metrics.successful_operations
            )
            
            return {
                "uri": f"file://{file_path}",
                "mimeType": mime_type,
                content_type: content,
                "size": file_size,
                "lastModified": datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
                "constitutional_compliance": validation.compliance_score,
                "execution_time_ms": execution_time
            }
            
        except Exception as e:
            self.metrics.failed_operations += 1
            logger.error(f"File read error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def write_file(
        self,
        file_path: str,
        content: Union[str, bytes],
        constitutional_context: ConstitutionalContext,
        overwrite: bool = False
    ) -> Dict[str, Any]:
        """Write file with constitutional validation"""
        
        start_time = datetime.utcnow()
        
        # Validate path
        validation = self.security_policy.validate_path(file_path)
        if not validation.is_compliant:
            self.metrics.failed_operations += 1
            raise HTTPException(
                status_code=403,
                detail=f"Constitutional violation: {validation.violations}"
            )
        
        try:
            path = Path(file_path)
            
            # Check if file exists and overwrite policy
            if path.exists() and not overwrite:
                raise HTTPException(
                    status_code=409,
                    detail="File exists and overwrite not allowed"
                )
            
            # Create parent directories if needed
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Validate content size
            content_size = len(content) if isinstance(content, str) else len(content)
            if content_size > self.security_policy.max_file_size:
                raise HTTPException(
                    status_code=413,
                    detail=f"Content too large: {content_size} bytes"
                )
            
            # Write content
            if isinstance(content, str):
                path.write_text(content, encoding="utf-8")
            else:
                path.write_bytes(content)
            
            # Update metrics
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            self.metrics.successful_operations += 1
            self.metrics.total_bytes_written += content_size
            
            return {
                "uri": f"file://{file_path}",
                "size": content_size,
                "created": datetime.utcnow().isoformat(),
                "constitutional_compliance": validation.compliance_score,
                "execution_time_ms": execution_time
            }
            
        except Exception as e:
            self.metrics.failed_operations += 1
            logger.error(f"File write error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def list_directory(
        self,
        dir_path: str,
        constitutional_context: ConstitutionalContext,
        recursive: bool = False
    ) -> Dict[str, Any]:
        """List directory contents with constitutional validation"""
        
        start_time = datetime.utcnow()
        
        # Validate path
        validation = self.security_policy.validate_path(dir_path)
        if not validation.is_compliant:
            self.metrics.failed_operations += 1
            raise HTTPException(
                status_code=403,
                detail=f"Constitutional violation: {validation.violations}"
            )
        
        try:
            path = Path(dir_path)
            
            # Check if directory exists
            if not path.exists():
                raise HTTPException(status_code=404, detail="Directory not found")
            
            if not path.is_dir():
                raise HTTPException(status_code=400, detail="Path is not a directory")
            
            # List directory contents
            entries = []
            pattern = "**/*" if recursive else "*"
            
            for item in path.glob(pattern):
                try:
                    # Get item stats
                    item_stat = item.stat()
                    
                    # Determine item type
                    if item.is_file():
                        item_type = "file"
                        mime_type, _ = mimetypes.guess_type(str(item))
                    elif item.is_dir():
                        item_type = "directory"
                        mime_type = "inode/directory"
                    else:
                        item_type = "other"
                        mime_type = "application/octet-stream"
                    
                    entry = {
                        "name": item.name,
                        "path": str(item),
                        "type": item_type,
                        "size": item_stat.st_size,
                        "mimeType": mime_type,
                        "lastModified": datetime.fromtimestamp(item_stat.st_mtime).isoformat(),
                        "permissions": oct(stat.S_IMODE(item_stat.st_mode))
                    }
                    
                    entries.append(entry)
                    
                except Exception as e:
                    # Skip items that can't be accessed
                    logger.warning(f"Could not access {item}: {str(e)}")
                    continue
            
            # Update metrics
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            self.metrics.successful_operations += 1
            
            return {
                "directory": dir_path,
                "entries": entries,
                "count": len(entries),
                "recursive": recursive,
                "constitutional_compliance": validation.compliance_score,
                "execution_time_ms": execution_time
            }
            
        except Exception as e:
            self.metrics.failed_operations += 1
            logger.error(f"Directory listing error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def delete_file(
        self,
        file_path: str,
        constitutional_context: ConstitutionalContext
    ) -> Dict[str, Any]:
        """Delete file with constitutional validation"""
        
        start_time = datetime.utcnow()
        
        # Validate path
        validation = self.security_policy.validate_path(file_path)
        if not validation.is_compliant:
            self.metrics.failed_operations += 1
            raise HTTPException(
                status_code=403,
                detail=f"Constitutional violation: {validation.violations}"
            )
        
        try:
            path = Path(file_path)
            
            # Check if file exists
            if not path.exists():
                raise HTTPException(status_code=404, detail="File not found")
            
            # Get file size before deletion
            file_size = path.stat().st_size
            
            # Delete file
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                import shutil
                shutil.rmtree(path)
            else:
                raise HTTPException(status_code=400, detail="Cannot delete this type of item")
            
            # Update metrics
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            self.metrics.successful_operations += 1
            self.metrics.files_deleted += 1
            
            return {
                "deleted": file_path,
                "size": file_size,
                "deleted_at": datetime.utcnow().isoformat(),
                "constitutional_compliance": validation.compliance_score,
                "execution_time_ms": execution_time
            }
            
        except Exception as e:
            self.metrics.failed_operations += 1
            logger.error(f"File deletion error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))


# Initialize filesystem operations
fs_ops = FilesystemOperations()


# MCP Protocol Endpoints

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    
    return {
        "status": "healthy",
        "service": "Filesystem MCP Service",
        "version": "1.0.0",
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "capabilities": ["tools", "resources"],
        "metrics": {
            "total_operations": fs_ops.metrics.successful_operations + fs_ops.metrics.failed_operations,
            "successful_operations": fs_ops.metrics.successful_operations,
            "failed_operations": fs_ops.metrics.failed_operations,
            "total_bytes_read": fs_ops.metrics.total_bytes_read,
            "total_bytes_written": fs_ops.metrics.total_bytes_written,
            "files_deleted": fs_ops.metrics.files_deleted,
            "average_operation_time_ms": fs_ops.metrics.average_operation_time_ms
        }
    }


@app.post("/mcp/tools_list")
async def list_tools():
    """List available filesystem tools"""
    
    tools = [
        {
            "name": "read_file",
            "description": "Read file contents with constitutional validation",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path to read"
                    }
                },
                "required": ["path"]
            }
        },
        {
            "name": "write_file",
            "description": "Write content to file with constitutional validation",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path to write"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write"
                    },
                    "overwrite": {
                        "type": "boolean",
                        "description": "Allow overwriting existing files",
                        "default": False
                    }
                },
                "required": ["path", "content"]
            }
        },
        {
            "name": "list_directory",
            "description": "List directory contents with constitutional validation",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory path to list"
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "List recursively",
                        "default": False
                    }
                },
                "required": ["path"]
            }
        },
        {
            "name": "delete_file",
            "description": "Delete file or directory with constitutional validation",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to delete"
                    }
                },
                "required": ["path"]
            }
        }
    ]
    
    return {"tools": tools}


@app.post("/mcp/tools_call")
async def call_tool(request: Dict[str, Any]):
    """Execute filesystem tool"""
    
    tool_name = request.get("name")
    arguments = request.get("arguments", {})
    
    # Create constitutional context
    constitutional_context = ConstitutionalContext(
        constitutional_hash=CONSTITUTIONAL_HASH,
        purpose=f"Filesystem operation: {tool_name}",
        additional_constraints=["filesystem_security"]
    )
    
    try:
        if tool_name == "read_file":
            result = await fs_ops.read_file(
                arguments["path"],
                constitutional_context
            )
            return {
                "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
            }
        
        elif tool_name == "write_file":
            result = await fs_ops.write_file(
                arguments["path"],
                arguments["content"],
                constitutional_context,
                arguments.get("overwrite", False)
            )
            return {
                "content": [{"type": "text", "text": f"File written successfully: {result}"}]
            }
        
        elif tool_name == "list_directory":
            result = await fs_ops.list_directory(
                arguments["path"],
                constitutional_context,
                arguments.get("recursive", False)
            )
            return {
                "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
            }
        
        elif tool_name == "delete_file":
            result = await fs_ops.delete_file(
                arguments["path"],
                constitutional_context
            )
            return {
                "content": [{"type": "text", "text": f"File deleted successfully: {result}"}]
            }
        
        else:
            raise HTTPException(status_code=400, detail=f"Unknown tool: {tool_name}")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Tool execution error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mcp/resources_list")
async def list_resources():
    """List available filesystem resources"""
    
    # Return dynamic resources based on allowed directories
    resources = []
    
    for base_path in fs_ops.security_policy.allowed_base_paths:
        if os.path.exists(base_path):
            resources.append({
                "uri": f"file://{base_path}",
                "name": f"Workspace: {os.path.basename(base_path)}",
                "description": f"Files and directories in {base_path}",
                "mimeType": "inode/directory"
            })
    
    return {"resources": resources}


@app.post("/mcp/resources_read")
async def read_resource(request: Dict[str, Any]):
    """Read filesystem resource"""
    
    uri = request.get("uri", "")
    
    # Extract file path from URI
    if uri.startswith("file://"):
        file_path = uri[7:]  # Remove "file://" prefix
    else:
        raise HTTPException(status_code=400, detail="Invalid file URI")
    
    # Create constitutional context
    constitutional_context = ConstitutionalContext(
        constitutional_hash=CONSTITUTIONAL_HASH,
        purpose="Resource access",
        additional_constraints=["filesystem_security"]
    )
    
    try:
        result = await fs_ops.read_file(file_path, constitutional_context)
        
        return {
            "contents": [{
                "uri": uri,
                "mimeType": result["mimeType"],
                "text": result.get("text"),
                "blob": result.get("blob")
            }]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Resource read error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/metrics")
async def get_metrics():
    """Get filesystem service metrics"""
    
    return {
        "total_operations": fs_ops.metrics.successful_operations + fs_ops.metrics.failed_operations,
        "successful_operations": fs_ops.metrics.successful_operations,
        "failed_operations": fs_ops.metrics.failed_operations,
        "success_rate": (
            fs_ops.metrics.successful_operations / 
            max(1, fs_ops.metrics.successful_operations + fs_ops.metrics.failed_operations)
        ),
        "total_bytes_read": fs_ops.metrics.total_bytes_read,
        "total_bytes_written": fs_ops.metrics.total_bytes_written,
        "files_deleted": fs_ops.metrics.files_deleted,
        "average_operation_time_ms": fs_ops.metrics.average_operation_time_ms,
        "constitutional_hash": CONSTITUTIONAL_HASH
    }


@app.get("/api/v1/security-policy")
async def get_security_policy():
    """Get current filesystem security policy"""
    
    return {
        "allowed_base_paths": list(fs_ops.security_policy.allowed_base_paths),
        "forbidden_paths": list(fs_ops.security_policy.forbidden_paths),
        "forbidden_extensions": list(fs_ops.security_policy.forbidden_extensions),
        "max_file_size": fs_ops.security_policy.max_file_size,
        "max_depth": fs_ops.security_policy.max_depth,
        "constitutional_hash": CONSTITUTIONAL_HASH
    }


@app.on_event("startup")
async def startup_event():
    """Initialize service on startup"""
    
    logger.info("Starting Filesystem MCP Service")
    logger.info(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    
    # Ensure allowed directories exist
    for base_path in fs_ops.security_policy.allowed_base_paths:
        try:
            os.makedirs(base_path, exist_ok=True)
            logger.info(f"Ensured directory exists: {base_path}")
        except Exception as e:
            logger.warning(f"Could not create directory {base_path}: {str(e)}")
    
    logger.info("Filesystem MCP Service initialization complete")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3001)