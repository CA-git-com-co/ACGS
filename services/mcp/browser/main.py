"""
Browser MCP Service
Constitutional Hash: cdd01ef066bc6cf2
Port: 3003

Model Context Protocol service for secure web browsing operations
with constitutional compliance validation.
"""

import asyncio
import json
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from uuid import UUID, uuid4
from urllib.parse import urlparse, urljoin

import aiohttp
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from bs4 import BeautifulSoup

from .models import (
    WebPage,
    WebResource,
    BrowserOperation,
    ConstitutionalContext,
    ConstitutionalValidation,
    BrowserMetrics,
    BrowserSecurityPolicy,
    NavigationResult,
    WebElement,
    ScreenshotResult,
    FormData
)

# Initialize FastAPI app
app = FastAPI(
    title="Browser MCP Service",
    description="Secure web browsing operations with constitutional compliance",
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


class BrowserSecurityPolicy:
    """Security policy for web browsing operations"""
    
    def __init__(self):
        # Allowed domains (configurable whitelist)
        self.allowed_domains = {
            "wikipedia.org", "github.com", "stackoverflow.com",
            "arxiv.org", "scholar.google.com", "pubmed.ncbi.nlm.nih.gov",
            "docs.python.org", "developer.mozilla.org", "w3.org"
        }
        
        # Forbidden domains (security/privacy concerns)
        self.forbidden_domains = {
            "localhost", "127.0.0.1", "10.", "192.168.", "172.16.",
            "admin.", "internal.", "private.", "secret.",
            "malware", "phishing", "suspicious"
        }
        
        # Forbidden URL patterns
        self.forbidden_patterns = {
            r".*\.(exe|dll|bat|cmd|ps1|sh|scr)$",  # Executable files
            r".*\.(zip|rar|7z|tar|gz)$",  # Archives (potentially unsafe)
            r".*/admin/.*", r".*/wp-admin/.*",  # Admin interfaces
            r".*/\.git/.*", r".*/\.env.*",  # Hidden/config files
            r".*javascript:.*", r".*data:.*"  # Script/data URIs
        }
        
        # Maximum page size (10MB)
        self.max_page_size = 10 * 1024 * 1024
        
        # Request timeout
        self.request_timeout = 30
        
        # User agent
        self.user_agent = "ACGS-2-Browser-MCP/1.0 (Constitutional AI Research)"
    
    def validate_url(self, url: str) -> ConstitutionalValidation:
        """Validate URL for security compliance"""
        
        try:
            parsed = urlparse(url)
            
            # Check scheme
            if parsed.scheme not in ["http", "https"]:
                return ConstitutionalValidation(
                    is_compliant=False,
                    compliance_score=0.0,
                    violations=[f"Unsupported URL scheme: {parsed.scheme}"],
                    recommendations=["Use HTTP or HTTPS URLs only"]
                )
            
            # Check domain
            domain = parsed.netloc.lower()
            
            # Remove port if present
            if ":" in domain:
                domain = domain.split(":")[0]
            
            # Check forbidden domains
            for forbidden in self.forbidden_domains:
                if forbidden in domain or domain.startswith(forbidden):
                    return ConstitutionalValidation(
                        is_compliant=False,
                        compliance_score=0.0,
                        violations=[f"Access to forbidden domain: {forbidden}"],
                        recommendations=["Use public, educational, or documentation websites"]
                    )
            
            # Check if domain is in allowed list (if configured)
            if self.allowed_domains:
                domain_allowed = any(
                    allowed in domain or domain.endswith(f".{allowed}")
                    for allowed in self.allowed_domains
                )
                
                if not domain_allowed:
                    return ConstitutionalValidation(
                        is_compliant=False,
                        compliance_score=0.3,
                        violations=["Domain not in allowed list"],
                        recommendations=[f"Use domains from: {', '.join(self.allowed_domains)}"]
                    )
            
            # Check forbidden patterns
            for pattern in self.forbidden_patterns:
                if re.match(pattern, url.lower()):
                    return ConstitutionalValidation(
                        is_compliant=False,
                        compliance_score=0.1,
                        violations=[f"URL matches forbidden pattern: {pattern}"],
                        recommendations=["Avoid executable files and admin interfaces"]
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
                violations=[f"URL validation error: {str(e)}"],
                recommendations=["Provide valid HTTP/HTTPS URL"]
            )


class WebBrowserClient:
    """Web browser client with constitutional compliance"""
    
    def __init__(self):
        self.session = None
        self.security_policy = BrowserSecurityPolicy()
        self.metrics = BrowserMetrics()
        self.current_page = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if not self.session:
            headers = {
                "User-Agent": self.security_policy.user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1"
            }
            
            timeout = aiohttp.ClientTimeout(total=self.security_policy.request_timeout)
            self.session = aiohttp.ClientSession(headers=headers, timeout=timeout)
        
        return self.session
    
    async def navigate_to_url(
        self,
        url: str,
        constitutional_context: ConstitutionalContext
    ) -> NavigationResult:
        """Navigate to URL with constitutional validation"""
        
        start_time = datetime.utcnow()
        
        # Validate URL
        validation = self.security_policy.validate_url(url)
        if not validation.is_compliant:
            self.metrics.failed_requests += 1
            raise HTTPException(
                status_code=403,
                detail=f"Constitutional violation: {validation.violations}"
            )
        
        try:
            session = await self._get_session()
            
            async with session.get(url) as response:
                # Check response size
                content_length = response.headers.get("Content-Length")
                if content_length and int(content_length) > self.security_policy.max_page_size:
                    raise HTTPException(
                        status_code=413,
                        detail=f"Page too large: {content_length} bytes"
                    )
                
                # Read content
                content = await response.read()
                
                # Check actual size
                if len(content) > self.security_policy.max_page_size:
                    raise HTTPException(
                        status_code=413,
                        detail=f"Page content too large: {len(content)} bytes"
                    )
                
                # Decode content
                try:
                    text_content = content.decode("utf-8")
                except UnicodeDecodeError:
                    try:
                        text_content = content.decode("latin-1")
                    except UnicodeDecodeError:
                        text_content = str(content)
                
                # Parse HTML
                soup = BeautifulSoup(text_content, "html.parser")
                
                # Extract page information
                title = soup.title.string.strip() if soup.title else "No title"
                
                # Extract meta information
                meta_description = ""
                meta_desc = soup.find("meta", attrs={"name": "description"})
                if meta_desc:
                    meta_description = meta_desc.get("content", "")
                
                # Extract links
                links = []
                for link in soup.find_all("a", href=True):
                    href = link["href"]
                    # Convert relative URLs to absolute
                    absolute_url = urljoin(url, href)
                    links.append({
                        "text": link.get_text().strip(),
                        "href": absolute_url,
                        "title": link.get("title", "")
                    })
                
                # Extract headings
                headings = []
                for i in range(1, 7):  # h1 to h6
                    for heading in soup.find_all(f"h{i}"):
                        headings.append({
                            "level": i,
                            "text": heading.get_text().strip()
                        })
                
                # Extract paragraphs
                paragraphs = [p.get_text().strip() for p in soup.find_all("p")]
                
                # Create page object
                page = WebPage(
                    url=url,
                    title=title,
                    content=text_content[:10000],  # Limit content for storage
                    meta_description=meta_description,
                    links=links[:50],  # Limit links
                    headings=headings[:20],  # Limit headings
                    paragraphs=paragraphs[:20],  # Limit paragraphs
                    status_code=response.status,
                    content_type=response.headers.get("Content-Type", ""),
                    content_length=len(content),
                    load_time=(datetime.utcnow() - start_time).total_seconds() * 1000
                )
                
                self.current_page = page
                
                # Update metrics
                self.metrics.successful_requests += 1
                self.metrics.pages_loaded += 1
                self.metrics.total_bytes_downloaded += len(content)
                
                return NavigationResult(
                    success=True,
                    page=page,
                    constitutional_validation=validation,
                    execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
                )
        
        except aiohttp.ClientError as e:
            self.metrics.failed_requests += 1
            logger.error(f"HTTP client error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Browser error: {str(e)}")
        
        except Exception as e:
            self.metrics.failed_requests += 1
            logger.error(f"Navigation error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def extract_text(self, url: str, constitutional_context: ConstitutionalContext) -> Dict[str, Any]:
        """Extract clean text from webpage"""
        
        result = await self.navigate_to_url(url, constitutional_context)
        
        if not result.success or not result.page:
            raise HTTPException(status_code=500, detail="Failed to load page")
        
        page = result.page
        soup = BeautifulSoup(page.content, "html.parser")
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Extract clean text
        clean_text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in clean_text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = "\n".join(chunk for chunk in chunks if chunk)
        
        return {
            "url": url,
            "title": page.title,
            "text": clean_text[:50000],  # Limit text size
            "word_count": len(clean_text.split()),
            "extraction_time": datetime.utcnow().isoformat(),
            "constitutional_compliance": result.constitutional_validation.compliance_score
        }
    
    async def search_page(
        self,
        url: str,
        search_term: str,
        constitutional_context: ConstitutionalContext
    ) -> Dict[str, Any]:
        """Search for term within webpage"""
        
        result = await self.navigate_to_url(url, constitutional_context)
        
        if not result.success or not result.page:
            raise HTTPException(status_code=500, detail="Failed to load page")
        
        page = result.page
        soup = BeautifulSoup(page.content, "html.parser")
        
        # Extract text content
        text_content = soup.get_text().lower()
        search_term_lower = search_term.lower()
        
        # Find occurrences
        occurrences = []
        start = 0
        while True:
            pos = text_content.find(search_term_lower, start)
            if pos == -1:
                break
            
            # Extract context around the match
            context_start = max(0, pos - 100)
            context_end = min(len(text_content), pos + len(search_term) + 100)
            context = text_content[context_start:context_end]
            
            occurrences.append({
                "position": pos,
                "context": context.strip()
            })
            
            start = pos + 1
            
            # Limit results
            if len(occurrences) >= 10:
                break
        
        return {
            "url": url,
            "search_term": search_term,
            "total_occurrences": len(occurrences),
            "occurrences": occurrences,
            "constitutional_compliance": result.constitutional_validation.compliance_score
        }
    
    async def get_page_links(
        self,
        url: str,
        constitutional_context: ConstitutionalContext
    ) -> Dict[str, Any]:
        """Extract all links from webpage"""
        
        result = await self.navigate_to_url(url, constitutional_context)
        
        if not result.success or not result.page:
            raise HTTPException(status_code=500, detail="Failed to load page")
        
        page = result.page
        
        # Filter and categorize links
        internal_links = []
        external_links = []
        
        base_domain = urlparse(url).netloc
        
        for link in page.links:
            link_domain = urlparse(link["href"]).netloc
            
            if link_domain == base_domain or not link_domain:
                internal_links.append(link)
            else:
                external_links.append(link)
        
        return {
            "url": url,
            "total_links": len(page.links),
            "internal_links": internal_links[:25],  # Limit results
            "external_links": external_links[:25],  # Limit results
            "constitutional_compliance": result.constitutional_validation.compliance_score
        }
    
    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()


# Initialize browser client
browser_client = WebBrowserClient()


# MCP Protocol Endpoints

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    
    return {
        "status": "healthy",
        "service": "Browser MCP Service",
        "version": "1.0.0",
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "capabilities": ["tools", "resources"],
        "metrics": {
            "total_requests": browser_client.metrics.successful_requests + browser_client.metrics.failed_requests,
            "successful_requests": browser_client.metrics.successful_requests,
            "failed_requests": browser_client.metrics.failed_requests,
            "pages_loaded": browser_client.metrics.pages_loaded,
            "total_bytes_downloaded": browser_client.metrics.total_bytes_downloaded
        },
        "security_policy": {
            "allowed_domains": list(browser_client.security_policy.allowed_domains),
            "max_page_size": browser_client.security_policy.max_page_size,
            "request_timeout": browser_client.security_policy.request_timeout
        }
    }


@app.post("/mcp/tools_list")
async def list_tools():
    """List available browser tools"""
    
    tools = [
        {
            "name": "navigate_to_url",
            "description": "Navigate to a webpage and extract its content",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL to navigate to",
                        "format": "uri"
                    }
                },
                "required": ["url"]
            }
        },
        {
            "name": "extract_text",
            "description": "Extract clean text content from a webpage",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL to extract text from",
                        "format": "uri"
                    }
                },
                "required": ["url"]
            }
        },
        {
            "name": "search_page",
            "description": "Search for a term within a webpage",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL to search within",
                        "format": "uri"
                    },
                    "search_term": {
                        "type": "string",
                        "description": "Term to search for"
                    }
                },
                "required": ["url", "search_term"]
            }
        },
        {
            "name": "get_page_links",
            "description": "Extract all links from a webpage",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL to extract links from",
                        "format": "uri"
                    }
                },
                "required": ["url"]
            }
        }
    ]
    
    return {"tools": tools}


@app.post("/mcp/tools_call")
async def call_tool(request: Dict[str, Any]):
    """Execute browser tool"""
    
    tool_name = request.get("name")
    arguments = request.get("arguments", {})
    
    # Create constitutional context
    constitutional_context = ConstitutionalContext(
        constitutional_hash=CONSTITUTIONAL_HASH,
        purpose=f"Web browsing operation: {tool_name}",
        additional_constraints=["web_security", "content_filtering"]
    )
    
    try:
        if tool_name == "navigate_to_url":
            result = await browser_client.navigate_to_url(
                arguments["url"],
                constitutional_context
            )
            
            # Convert result to serializable format
            page_data = {
                "url": result.page.url,
                "title": result.page.title,
                "status_code": result.page.status_code,
                "content_type": result.page.content_type,
                "content_length": result.page.content_length,
                "load_time": result.page.load_time,
                "headings": result.page.headings[:10],  # Limit for response size
                "links_count": len(result.page.links),
                "paragraphs_count": len(result.page.paragraphs),
                "constitutional_compliance": result.constitutional_validation.compliance_score
            }
            
            return {
                "content": [{"type": "text", "text": json.dumps(page_data, indent=2)}]
            }
        
        elif tool_name == "extract_text":
            result = await browser_client.extract_text(
                arguments["url"],
                constitutional_context
            )
            
            return {
                "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
            }
        
        elif tool_name == "search_page":
            result = await browser_client.search_page(
                arguments["url"],
                arguments["search_term"],
                constitutional_context
            )
            
            return {
                "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
            }
        
        elif tool_name == "get_page_links":
            result = await browser_client.get_page_links(
                arguments["url"],
                constitutional_context
            )
            
            return {
                "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
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
    """List available browser resources"""
    
    # Dynamic resources based on browsing capabilities
    resources = [
        {
            "uri": "web://page/{url}",
            "name": "Web Page",
            "description": "Access to web page content",
            "mimeType": "text/html"
        },
        {
            "uri": "web://text/{url}",
            "name": "Web Page Text",
            "description": "Clean text content from web pages",
            "mimeType": "text/plain"
        },
        {
            "uri": "web://links/{url}",
            "name": "Web Page Links",
            "description": "Links extracted from web pages",
            "mimeType": "application/json"
        }
    ]
    
    return {"resources": resources}


@app.post("/mcp/resources_read")
async def read_resource(request: Dict[str, Any]):
    """Read browser resource"""
    
    uri = request.get("uri", "")
    
    # Parse web URI
    if not uri.startswith("web://"):
        raise HTTPException(status_code=400, detail="Invalid web URI")
    
    # Remove web:// prefix and parse
    path_parts = uri[6:].split("/", 1)
    
    if len(path_parts) < 2:
        raise HTTPException(status_code=400, detail="Invalid web resource URI")
    
    resource_type = path_parts[0]
    url = path_parts[1]
    
    # Create constitutional context
    constitutional_context = ConstitutionalContext(
        constitutional_hash=CONSTITUTIONAL_HASH,
        purpose="Web resource access",
        additional_constraints=["web_security"]
    )
    
    try:
        if resource_type == "page":
            # Full page resource
            result = await browser_client.navigate_to_url(url, constitutional_context)
            content = {
                "url": result.page.url,
                "title": result.page.title,
                "content": result.page.content[:10000],  # Limit content
                "meta_description": result.page.meta_description,
                "headings": result.page.headings,
                "constitutional_compliance": result.constitutional_validation.compliance_score
            }
            
        elif resource_type == "text":
            # Text content only
            content = await browser_client.extract_text(url, constitutional_context)
            
        elif resource_type == "links":
            # Links only
            content = await browser_client.get_page_links(url, constitutional_context)
            
        else:
            raise HTTPException(status_code=400, detail="Unsupported web resource type")
        
        return {
            "contents": [{
                "uri": uri,
                "mimeType": "application/json",
                "text": json.dumps(content, indent=2)
            }]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Resource read error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/metrics")
async def get_metrics():
    """Get browser service metrics"""
    
    total_requests = browser_client.metrics.successful_requests + browser_client.metrics.failed_requests
    
    return {
        "total_requests": total_requests,
        "successful_requests": browser_client.metrics.successful_requests,
        "failed_requests": browser_client.metrics.failed_requests,
        "success_rate": browser_client.metrics.successful_requests / max(1, total_requests),
        "pages_loaded": browser_client.metrics.pages_loaded,
        "total_bytes_downloaded": browser_client.metrics.total_bytes_downloaded,
        "average_page_load_time_ms": browser_client.metrics.average_page_load_time_ms,
        "constitutional_violations": browser_client.metrics.constitutional_violations,
        "constitutional_hash": CONSTITUTIONAL_HASH
    }


@app.get("/api/v1/security-policy")
async def get_security_policy():
    """Get current browser security policy"""
    
    return {
        "allowed_domains": list(browser_client.security_policy.allowed_domains),
        "forbidden_domains": list(browser_client.security_policy.forbidden_domains),
        "forbidden_patterns": list(browser_client.security_policy.forbidden_patterns),
        "max_page_size": browser_client.security_policy.max_page_size,
        "request_timeout": browser_client.security_policy.request_timeout,
        "user_agent": browser_client.security_policy.user_agent,
        "constitutional_hash": CONSTITUTIONAL_HASH
    }


@app.on_event("startup")
async def startup_event():
    """Initialize service on startup"""
    
    logger.info("Starting Browser MCP Service")
    logger.info(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    logger.info(f"Allowed domains: {browser_client.security_policy.allowed_domains}")
    logger.info("Browser MCP Service initialization complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    
    await browser_client.close()
    logger.info("Browser MCP Service shutdown complete")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3003)