"""
GitHub MCP Service
Constitutional Hash: cdd01ef066bc6cf2
Port: 3002

Model Context Protocol service for secure GitHub operations
with constitutional compliance validation.
"""

import asyncio
import json
import logging
import base64
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from uuid import UUID, uuid4

import aiohttp
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .models import (
    GitHubRepository,
    GitHubIssue,
    GitHubPullRequest,
    GitHubFile,
    GitHubUser,
    GitHubOperation,
    ConstitutionalContext,
    ConstitutionalValidation,
    GitHubMetrics,
    GitHubAPIRateLimits,
    RepositoryPermissions
)

# Initialize FastAPI app
app = FastAPI(
    title="GitHub MCP Service",
    description="Secure GitHub operations with constitutional compliance",
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


class GitHubSecurityPolicy:
    """Security policy for GitHub operations"""
    
    def __init__(self):
        # Allowed operations
        self.allowed_operations = {
            "read_repository", "list_repositories", "get_file", "list_files",
            "get_issues", "list_issues", "get_pull_requests", "list_pull_requests",
            "get_user", "search_repositories", "get_commits", "get_branches"
        }
        
        # Restricted operations (require elevated permissions)
        self.restricted_operations = {
            "create_issue", "update_issue", "create_pull_request",
            "create_file", "update_file", "delete_file",
            "create_repository", "delete_repository"
        }
        
        # Forbidden operations (not allowed in constitutional AI context)
        self.forbidden_operations = {
            "delete_repository_permanent", "force_push", "modify_webhooks",
            "manage_secrets", "modify_security_settings"
        }
        
        # Sensitive file patterns
        self.sensitive_file_patterns = {
            ".env", "*.key", "*.pem", "*.p12", "*.pfx",
            "config.json", "secrets.yaml", "credentials.json",
            "id_rsa", "id_dsa", "id_ecdsa", "id_ed25519"
        }
        
        # Maximum file size for operations (10MB)
        self.max_file_size = 10 * 1024 * 1024
        
        # Rate limiting
        self.max_requests_per_hour = 1000
    
    def validate_operation(self, operation: str, context: ConstitutionalContext) -> ConstitutionalValidation:
        """Validate GitHub operation for constitutional compliance"""
        
        # Check forbidden operations
        if operation in self.forbidden_operations:
            return ConstitutionalValidation(
                is_compliant=False,
                compliance_score=0.0,
                violations=[f"Forbidden GitHub operation: {operation}"],
                recommendations=["Use read-only operations for constitutional AI analysis"]
            )
        
        # Check restricted operations
        if operation in self.restricted_operations:
            if context.compliance_level.value != "high":
                return ConstitutionalValidation(
                    is_compliant=False,
                    compliance_score=0.3,
                    violations=[f"Restricted operation '{operation}' requires high compliance level"],
                    recommendations=["Upgrade to high compliance level for write operations"]
                )
        
        # Check allowed operations
        if operation not in self.allowed_operations and operation not in self.restricted_operations:
            return ConstitutionalValidation(
                is_compliant=False,
                compliance_score=0.1,
                violations=[f"Unknown or unsupported operation: {operation}"],
                recommendations=["Use supported GitHub operations only"]
            )
        
        return ConstitutionalValidation(
            is_compliant=True,
            compliance_score=1.0,
            violations=[],
            recommendations=[]
        )
    
    def validate_file_access(self, file_path: str) -> ConstitutionalValidation:
        """Validate file access for security compliance"""
        
        import fnmatch
        
        # Check sensitive file patterns
        for pattern in self.sensitive_file_patterns:
            if fnmatch.fnmatch(file_path.lower(), pattern.lower()):
                return ConstitutionalValidation(
                    is_compliant=False,
                    compliance_score=0.0,
                    violations=[f"Access to sensitive file pattern: {pattern}"],
                    recommendations=["Avoid accessing credential and key files"]
                )
        
        return ConstitutionalValidation(
            is_compliant=True,
            compliance_score=1.0,
            violations=[],
            recommendations=[]
        )


class GitHubAPIClient:
    """GitHub API client with constitutional compliance"""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token
        self.base_url = "https://api.github.com"
        self.session = None
        self.security_policy = GitHubSecurityPolicy()
        self.metrics = GitHubMetrics()
        self.rate_limits = GitHubAPIRateLimits()
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if not self.session:
            headers = {
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "ACGS-2-MCP-GitHub/1.0.0"
            }
            if self.token:
                headers["Authorization"] = f"token {self.token}"
            
            self.session = aiohttp.ClientSession(headers=headers)
        
        return self.session
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make GitHub API request with rate limiting and error handling"""
        
        session = await self._get_session()
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            async with session.request(
                method,
                url,
                params=params,
                json=data,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                # Update rate limits
                if "X-RateLimit-Remaining" in response.headers:
                    self.rate_limits.core_remaining = int(response.headers["X-RateLimit-Remaining"])
                    self.rate_limits.core_reset = int(response.headers.get("X-RateLimit-Reset", 0))
                
                if response.status == 200:
                    self.metrics.successful_requests += 1
                    return await response.json()
                elif response.status == 403 and "rate limit" in (await response.text()).lower():
                    self.metrics.rate_limit_hits += 1
                    raise HTTPException(status_code=429, detail="GitHub API rate limit exceeded")
                else:
                    self.metrics.failed_requests += 1
                    error_text = await response.text()
                    raise HTTPException(
                        status_code=response.status,
                        detail=f"GitHub API error: {error_text}"
                    )
        
        except aiohttp.ClientError as e:
            self.metrics.failed_requests += 1
            raise HTTPException(status_code=500, detail=f"GitHub API client error: {str(e)}")
    
    async def get_repository(
        self,
        owner: str,
        repo: str,
        constitutional_context: ConstitutionalContext
    ) -> Dict[str, Any]:
        """Get repository information"""
        
        # Validate operation
        validation = self.security_policy.validate_operation("read_repository", constitutional_context)
        if not validation.is_compliant:
            raise HTTPException(status_code=403, detail=f"Constitutional violation: {validation.violations}")
        
        return await self._make_request("GET", f"repos/{owner}/{repo}")
    
    async def get_file(
        self,
        owner: str,
        repo: str,
        path: str,
        ref: str = "main",
        constitutional_context: ConstitutionalContext = None
    ) -> Dict[str, Any]:
        """Get file content from repository"""
        
        # Validate operation
        validation = self.security_policy.validate_operation("get_file", constitutional_context)
        if not validation.is_compliant:
            raise HTTPException(status_code=403, detail=f"Constitutional violation: {validation.violations}")
        
        # Validate file access
        file_validation = self.security_policy.validate_file_access(path)
        if not file_validation.is_compliant:
            raise HTTPException(status_code=403, detail=f"File access violation: {file_validation.violations}")
        
        params = {"ref": ref} if ref != "main" else None
        response = await self._make_request("GET", f"repos/{owner}/{repo}/contents/{path}", params=params)
        
        # Decode content if it's base64 encoded
        if response.get("encoding") == "base64":
            try:
                content = base64.b64decode(response["content"]).decode("utf-8")
                response["decoded_content"] = content
            except Exception as e:
                logger.warning(f"Could not decode file content: {str(e)}")
        
        return response
    
    async def list_repository_files(
        self,
        owner: str,
        repo: str,
        path: str = "",
        ref: str = "main",
        constitutional_context: ConstitutionalContext = None
    ) -> Dict[str, Any]:
        """List files in repository directory"""
        
        # Validate operation
        validation = self.security_policy.validate_operation("list_files", constitutional_context)
        if not validation.is_compliant:
            raise HTTPException(status_code=403, detail=f"Constitutional violation: {validation.violations}")
        
        params = {"ref": ref} if ref != "main" else None
        endpoint = f"repos/{owner}/{repo}/contents"
        if path:
            endpoint += f"/{path}"
        
        return await self._make_request("GET", endpoint, params=params)
    
    async def get_issues(
        self,
        owner: str,
        repo: str,
        state: str = "open",
        per_page: int = 30,
        constitutional_context: ConstitutionalContext = None
    ) -> List[Dict[str, Any]]:
        """Get repository issues"""
        
        # Validate operation
        validation = self.security_policy.validate_operation("get_issues", constitutional_context)
        if not validation.is_compliant:
            raise HTTPException(status_code=403, detail=f"Constitutional violation: {validation.violations}")
        
        params = {
            "state": state,
            "per_page": min(per_page, 100)  # GitHub API limit
        }
        
        return await self._make_request("GET", f"repos/{owner}/{repo}/issues", params=params)
    
    async def get_pull_requests(
        self,
        owner: str,
        repo: str,
        state: str = "open",
        per_page: int = 30,
        constitutional_context: ConstitutionalContext = None
    ) -> List[Dict[str, Any]]:
        """Get repository pull requests"""
        
        # Validate operation
        validation = self.security_policy.validate_operation("get_pull_requests", constitutional_context)
        if not validation.is_compliant:
            raise HTTPException(status_code=403, detail=f"Constitutional violation: {validation.violations}")
        
        params = {
            "state": state,
            "per_page": min(per_page, 100)  # GitHub API limit
        }
        
        return await self._make_request("GET", f"repos/{owner}/{repo}/pulls", params=params)
    
    async def search_repositories(
        self,
        query: str,
        sort: str = "stars",
        order: str = "desc",
        per_page: int = 30,
        constitutional_context: ConstitutionalContext = None
    ) -> Dict[str, Any]:
        """Search GitHub repositories"""
        
        # Validate operation
        validation = self.security_policy.validate_operation("search_repositories", constitutional_context)
        if not validation.is_compliant:
            raise HTTPException(status_code=403, detail=f"Constitutional violation: {validation.violations}")
        
        params = {
            "q": query,
            "sort": sort,
            "order": order,
            "per_page": min(per_page, 100)  # GitHub API limit
        }
        
        return await self._make_request("GET", "search/repositories", params=params)
    
    async def get_user(
        self,
        username: str,
        constitutional_context: ConstitutionalContext = None
    ) -> Dict[str, Any]:
        """Get GitHub user information"""
        
        # Validate operation
        validation = self.security_policy.validate_operation("get_user", constitutional_context)
        if not validation.is_compliant:
            raise HTTPException(status_code=403, detail=f"Constitutional violation: {validation.violations}")
        
        return await self._make_request("GET", f"users/{username}")
    
    async def get_commits(
        self,
        owner: str,
        repo: str,
        sha: Optional[str] = None,
        path: Optional[str] = None,
        per_page: int = 30,
        constitutional_context: ConstitutionalContext = None
    ) -> List[Dict[str, Any]]:
        """Get repository commits"""
        
        # Validate operation
        validation = self.security_policy.validate_operation("get_commits", constitutional_context)
        if not validation.is_compliant:
            raise HTTPException(status_code=403, detail=f"Constitutional violation: {validation.violations}")
        
        params = {"per_page": min(per_page, 100)}
        if sha:
            params["sha"] = sha
        if path:
            params["path"] = path
        
        return await self._make_request("GET", f"repos/{owner}/{repo}/commits", params=params)
    
    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()


# Initialize GitHub client
github_client = GitHubAPIClient()


# MCP Protocol Endpoints

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    
    return {
        "status": "healthy",
        "service": "GitHub MCP Service",
        "version": "1.0.0",
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "capabilities": ["tools", "resources"],
        "metrics": {
            "total_requests": github_client.metrics.successful_requests + github_client.metrics.failed_requests,
            "successful_requests": github_client.metrics.successful_requests,
            "failed_requests": github_client.metrics.failed_requests,
            "rate_limit_hits": github_client.metrics.rate_limit_hits,
            "repositories_accessed": github_client.metrics.repositories_accessed,
            "files_read": github_client.metrics.files_read
        },
        "rate_limits": {
            "core_remaining": github_client.rate_limits.core_remaining,
            "core_reset": github_client.rate_limits.core_reset
        }
    }


@app.post("/mcp/tools_list")
async def list_tools():
    """List available GitHub tools"""
    
    tools = [
        {
            "name": "get_repository",
            "description": "Get GitHub repository information",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "owner": {"type": "string", "description": "Repository owner"},
                    "repo": {"type": "string", "description": "Repository name"}
                },
                "required": ["owner", "repo"]
            }
        },
        {
            "name": "get_file",
            "description": "Get file content from GitHub repository",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "owner": {"type": "string", "description": "Repository owner"},
                    "repo": {"type": "string", "description": "Repository name"},
                    "path": {"type": "string", "description": "File path in repository"},
                    "ref": {"type": "string", "description": "Git reference (branch, tag, commit)", "default": "main"}
                },
                "required": ["owner", "repo", "path"]
            }
        },
        {
            "name": "list_files",
            "description": "List files in GitHub repository directory",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "owner": {"type": "string", "description": "Repository owner"},
                    "repo": {"type": "string", "description": "Repository name"},
                    "path": {"type": "string", "description": "Directory path", "default": ""},
                    "ref": {"type": "string", "description": "Git reference", "default": "main"}
                },
                "required": ["owner", "repo"]
            }
        },
        {
            "name": "get_issues",
            "description": "Get GitHub repository issues",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "owner": {"type": "string", "description": "Repository owner"},
                    "repo": {"type": "string", "description": "Repository name"},
                    "state": {"type": "string", "enum": ["open", "closed", "all"], "default": "open"},
                    "per_page": {"type": "integer", "minimum": 1, "maximum": 100, "default": 30}
                },
                "required": ["owner", "repo"]
            }
        },
        {
            "name": "get_pull_requests",
            "description": "Get GitHub repository pull requests",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "owner": {"type": "string", "description": "Repository owner"},
                    "repo": {"type": "string", "description": "Repository name"},
                    "state": {"type": "string", "enum": ["open", "closed", "all"], "default": "open"},
                    "per_page": {"type": "integer", "minimum": 1, "maximum": 100, "default": 30}
                },
                "required": ["owner", "repo"]
            }
        },
        {
            "name": "search_repositories",
            "description": "Search GitHub repositories",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "sort": {"type": "string", "enum": ["stars", "forks", "updated"], "default": "stars"},
                    "order": {"type": "string", "enum": ["asc", "desc"], "default": "desc"},
                    "per_page": {"type": "integer", "minimum": 1, "maximum": 100, "default": 30}
                },
                "required": ["query"]
            }
        },
        {
            "name": "get_user",
            "description": "Get GitHub user information",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "username": {"type": "string", "description": "GitHub username"}
                },
                "required": ["username"]
            }
        },
        {
            "name": "get_commits",
            "description": "Get repository commits",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "owner": {"type": "string", "description": "Repository owner"},
                    "repo": {"type": "string", "description": "Repository name"},
                    "sha": {"type": "string", "description": "Git SHA or branch name"},
                    "path": {"type": "string", "description": "Filter commits by file path"},
                    "per_page": {"type": "integer", "minimum": 1, "maximum": 100, "default": 30}
                },
                "required": ["owner", "repo"]
            }
        }
    ]
    
    return {"tools": tools}


@app.post("/mcp/tools_call")
async def call_tool(request: Dict[str, Any]):
    """Execute GitHub tool"""
    
    tool_name = request.get("name")
    arguments = request.get("arguments", {})
    
    # Create constitutional context
    constitutional_context = ConstitutionalContext(
        constitutional_hash=CONSTITUTIONAL_HASH,
        purpose=f"GitHub operation: {tool_name}",
        additional_constraints=["github_security", "api_rate_limiting"]
    )
    
    try:
        if tool_name == "get_repository":
            result = await github_client.get_repository(
                arguments["owner"],
                arguments["repo"],
                constitutional_context
            )
            github_client.metrics.repositories_accessed += 1
            
        elif tool_name == "get_file":
            result = await github_client.get_file(
                arguments["owner"],
                arguments["repo"],
                arguments["path"],
                arguments.get("ref", "main"),
                constitutional_context
            )
            github_client.metrics.files_read += 1
            
        elif tool_name == "list_files":
            result = await github_client.list_repository_files(
                arguments["owner"],
                arguments["repo"],
                arguments.get("path", ""),
                arguments.get("ref", "main"),
                constitutional_context
            )
            
        elif tool_name == "get_issues":
            result = await github_client.get_issues(
                arguments["owner"],
                arguments["repo"],
                arguments.get("state", "open"),
                arguments.get("per_page", 30),
                constitutional_context
            )
            
        elif tool_name == "get_pull_requests":
            result = await github_client.get_pull_requests(
                arguments["owner"],
                arguments["repo"],
                arguments.get("state", "open"),
                arguments.get("per_page", 30),
                constitutional_context
            )
            
        elif tool_name == "search_repositories":
            result = await github_client.search_repositories(
                arguments["query"],
                arguments.get("sort", "stars"),
                arguments.get("order", "desc"),
                arguments.get("per_page", 30),
                constitutional_context
            )
            
        elif tool_name == "get_user":
            result = await github_client.get_user(
                arguments["username"],
                constitutional_context
            )
            
        elif tool_name == "get_commits":
            result = await github_client.get_commits(
                arguments["owner"],
                arguments["repo"],
                arguments.get("sha"),
                arguments.get("path"),
                arguments.get("per_page", 30),
                constitutional_context
            )
            
        else:
            raise HTTPException(status_code=400, detail=f"Unknown tool: {tool_name}")
        
        return {
            "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Tool execution error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mcp/resources_list")
async def list_resources():
    """List available GitHub resources"""
    
    # Dynamic resources based on common GitHub endpoints
    resources = [
        {
            "uri": "github://repository/{owner}/{repo}",
            "name": "GitHub Repository",
            "description": "Access to GitHub repository information",
            "mimeType": "application/json"
        },
        {
            "uri": "github://file/{owner}/{repo}/{path}",
            "name": "GitHub File",
            "description": "Access to files in GitHub repositories",
            "mimeType": "text/plain"
        },
        {
            "uri": "github://issues/{owner}/{repo}",
            "name": "GitHub Issues",
            "description": "Access to GitHub repository issues",
            "mimeType": "application/json"
        },
        {
            "uri": "github://pulls/{owner}/{repo}",
            "name": "GitHub Pull Requests",
            "description": "Access to GitHub repository pull requests",
            "mimeType": "application/json"
        },
        {
            "uri": "github://user/{username}",
            "name": "GitHub User",
            "description": "Access to GitHub user information",
            "mimeType": "application/json"
        }
    ]
    
    return {"resources": resources}


@app.post("/mcp/resources_read")
async def read_resource(request: Dict[str, Any]):
    """Read GitHub resource"""
    
    uri = request.get("uri", "")
    
    # Parse GitHub URI
    if not uri.startswith("github://"):
        raise HTTPException(status_code=400, detail="Invalid GitHub URI")
    
    # Remove github:// prefix and parse
    path_parts = uri[9:].split("/")
    
    # Create constitutional context
    constitutional_context = ConstitutionalContext(
        constitutional_hash=CONSTITUTIONAL_HASH,
        purpose="Resource access",
        additional_constraints=["github_security"]
    )
    
    try:
        if len(path_parts) >= 3 and path_parts[0] == "repository":
            # Repository resource
            owner, repo = path_parts[1], path_parts[2]
            result = await github_client.get_repository(owner, repo, constitutional_context)
            
        elif len(path_parts) >= 4 and path_parts[0] == "file":
            # File resource
            owner, repo = path_parts[1], path_parts[2]
            file_path = "/".join(path_parts[3:])
            result = await github_client.get_file(owner, repo, file_path, "main", constitutional_context)
            
        elif len(path_parts) >= 3 and path_parts[0] == "issues":
            # Issues resource
            owner, repo = path_parts[1], path_parts[2]
            result = await github_client.get_issues(owner, repo, "open", 30, constitutional_context)
            
        elif len(path_parts) >= 3 and path_parts[0] == "pulls":
            # Pull requests resource
            owner, repo = path_parts[1], path_parts[2]
            result = await github_client.get_pull_requests(owner, repo, "open", 30, constitutional_context)
            
        elif len(path_parts) >= 2 and path_parts[0] == "user":
            # User resource
            username = path_parts[1]
            result = await github_client.get_user(username, constitutional_context)
            
        else:
            raise HTTPException(status_code=400, detail="Unsupported GitHub resource")
        
        return {
            "contents": [{
                "uri": uri,
                "mimeType": "application/json",
                "text": json.dumps(result, indent=2)
            }]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Resource read error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/metrics")
async def get_metrics():
    """Get GitHub service metrics"""
    
    total_requests = github_client.metrics.successful_requests + github_client.metrics.failed_requests
    
    return {
        "total_requests": total_requests,
        "successful_requests": github_client.metrics.successful_requests,
        "failed_requests": github_client.metrics.failed_requests,
        "success_rate": github_client.metrics.successful_requests / max(1, total_requests),
        "rate_limit_hits": github_client.metrics.rate_limit_hits,
        "repositories_accessed": github_client.metrics.repositories_accessed,
        "files_read": github_client.metrics.files_read,
        "rate_limits": {
            "core_remaining": github_client.rate_limits.core_remaining,
            "core_reset": github_client.rate_limits.core_reset
        },
        "constitutional_hash": CONSTITUTIONAL_HASH
    }


@app.get("/api/v1/security-policy")
async def get_security_policy():
    """Get current GitHub security policy"""
    
    return {
        "allowed_operations": list(github_client.security_policy.allowed_operations),
        "restricted_operations": list(github_client.security_policy.restricted_operations),
        "forbidden_operations": list(github_client.security_policy.forbidden_operations),
        "sensitive_file_patterns": list(github_client.security_policy.sensitive_file_patterns),
        "max_file_size": github_client.security_policy.max_file_size,
        "max_requests_per_hour": github_client.security_policy.max_requests_per_hour,
        "constitutional_hash": CONSTITUTIONAL_HASH
    }


@app.on_event("startup")
async def startup_event():
    """Initialize service on startup"""
    
    logger.info("Starting GitHub MCP Service")
    logger.info(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    
    # Initialize GitHub token from environment if available
    import os
    github_token = os.getenv("GITHUB_TOKEN")
    if github_token:
        github_client.token = github_token
        logger.info("GitHub token configured")
    else:
        logger.warning("No GitHub token configured - running in public-only mode")
    
    logger.info("GitHub MCP Service initialization complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    
    await github_client.close()
    logger.info("GitHub MCP Service shutdown complete")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3002)