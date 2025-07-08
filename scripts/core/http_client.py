"""
ACGS HTTP Client
Constitutional Hash: cdd01ef066bc6cf2

Async HTTP client with retry logic and constitutional compliance validation.
"""

import asyncio
import aiohttp
import time
from typing import Dict, Any, Optional, List, Union
from urllib.parse import urljoin

from .config import ServiceConfig
from .logger import get_logger
from .exceptions import ServiceError, TimeoutError, RetryExhaustedError, ConstitutionalComplianceError
from .utils import retry_async, validate_service_response

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class HTTPClient:
    """Async HTTP client with ACGS-specific features."""
    
    def __init__(
        self,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        validate_constitutional_compliance: bool = True
    ):
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.validate_constitutional_compliance = validate_constitutional_compliance
        self.logger = get_logger("http-client")
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def _ensure_session(self):
        """Ensure HTTP session is created."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                headers={
                    "User-Agent": f"ACGS-Scripts/1.0 (Constitutional-Hash: {CONSTITUTIONAL_HASH})",
                    "X-Constitutional-Hash": CONSTITUTIONAL_HASH,
                }
            )
    
    async def close(self):
        """Close HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None
    
    @retry_async(max_retries=3, delay=1.0, backoff=2.0)
    async def request(
        self,
        method: str,
        url: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic."""
        await self._ensure_session()
        
        start_time = time.time()
        
        # Prepare headers
        request_headers = headers or {}
        request_headers.setdefault("X-Constitutional-Hash", CONSTITUTIONAL_HASH)
        
        try:
            self.logger.debug(f"Making {method} request to {url}")
            
            async with self._session.request(
                method=method,
                url=url,
                json=json_data,
                params=params,
                headers=request_headers,
                **kwargs
            ) as response:
                duration_ms = (time.time() - start_time) * 1000
                
                # Read response
                try:
                    response_data = await response.json()
                except Exception:
                    response_data = {"text": await response.text()}
                
                # Log performance
                self.logger.performance(f"{method} {url}", duration_ms)
                
                # Check for HTTP errors
                if response.status >= 400:
                    raise ServiceError(
                        f"HTTP {response.status}: {response.reason}",
                        status_code=response.status,
                        response_data=response_data
                    )
                
                # Validate constitutional compliance if enabled
                if self.validate_constitutional_compliance:
                    validate_service_response(response_data)
                
                return response_data
                
        except asyncio.TimeoutError as e:
            duration_ms = (time.time() - start_time) * 1000
            raise TimeoutError(
                f"Request timeout after {duration_ms:.0f}ms: {method} {url}",
                timeout_seconds=self.timeout,
                operation=f"{method} {url}"
            ) from e
        except aiohttp.ClientError as e:
            raise ServiceError(f"Client error: {e}") from e
    
    async def get(self, url: str, **kwargs) -> Dict[str, Any]:
        """Make GET request."""
        return await self.request("GET", url, **kwargs)
    
    async def post(self, url: str, json_data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Make POST request."""
        return await self.request("POST", url, json_data=json_data, **kwargs)
    
    async def put(self, url: str, json_data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Make PUT request."""
        return await self.request("PUT", url, json_data=json_data, **kwargs)
    
    async def delete(self, url: str, **kwargs) -> Dict[str, Any]:
        """Make DELETE request."""
        return await self.request("DELETE", url, **kwargs)
    
    async def health_check(self, service_config: ServiceConfig) -> Dict[str, Any]:
        """Perform health check on a service."""
        try:
            start_time = time.time()
            response = await self.get(service_config.health_url)
            duration_ms = (time.time() - start_time) * 1000
            
            # Log health check result
            healthy = response.get("status") == "healthy"
            self.logger.service_health(
                service_config.name, 
                healthy, 
                response_time_ms=duration_ms
            )
            
            return {
                "service": service_config.name,
                "healthy": healthy,
                "response_time_ms": duration_ms,
                "response": response,
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }
            
        except Exception as e:
            self.logger.service_health(service_config.name, False)
            return {
                "service": service_config.name,
                "healthy": False,
                "error": str(e),
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }
    
    async def health_check_multiple(
        self, 
        service_configs: List[ServiceConfig],
        max_concurrent: int = 10
    ) -> List[Dict[str, Any]]:
        """Perform health checks on multiple services concurrently."""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def check_with_semaphore(service_config: ServiceConfig) -> Dict[str, Any]:
            async with semaphore:
                return await self.health_check(service_config)
        
        self.logger.info(f"Performing health checks on {len(service_configs)} services")
        
        start_time = time.time()
        results = await asyncio.gather(
            *[check_with_semaphore(config) for config in service_configs],
            return_exceptions=True
        )
        duration_ms = (time.time() - start_time) * 1000
        
        # Process results and handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                service_name = service_configs[i].name
                self.logger.error(f"Health check failed for {service_name}", error=result)
                processed_results.append({
                    "service": service_name,
                    "healthy": False,
                    "error": str(result),
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                })
            else:
                processed_results.append(result)
        
        # Log summary
        healthy_count = sum(1 for r in processed_results if r.get("healthy", False))
        self.logger.performance(
            f"Health checks for {len(service_configs)} services", 
            duration_ms,
            healthy_services=healthy_count,
            total_services=len(service_configs)
        )
        
        return processed_results
    
    async def batch_request(
        self,
        requests: List[Dict[str, Any]],
        max_concurrent: int = 10
    ) -> List[Dict[str, Any]]:
        """Execute multiple requests concurrently."""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def request_with_semaphore(request_config: Dict[str, Any]) -> Dict[str, Any]:
            async with semaphore:
                try:
                    result = await self.request(**request_config)
                    return {"success": True, "data": result, "config": request_config}
                except Exception as e:
                    return {"success": False, "error": str(e), "config": request_config}
        
        self.logger.info(f"Executing batch of {len(requests)} requests")
        
        start_time = time.time()
        results = await asyncio.gather(
            *[request_with_semaphore(req) for req in requests],
            return_exceptions=True
        )
        duration_ms = (time.time() - start_time) * 1000
        
        # Process results
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                processed_results.append({
                    "success": False,
                    "error": str(result),
                    "config": None
                })
            else:
                processed_results.append(result)
        
        # Log summary
        success_count = sum(1 for r in processed_results if r.get("success", False))
        self.logger.performance(
            f"Batch execution of {len(requests)} requests",
            duration_ms,
            successful_requests=success_count,
            total_requests=len(requests)
        )
        
        return processed_results