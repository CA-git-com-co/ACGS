"""
ACGS-1 Versioned Router System

Provides version-aware routing with intelligent fallback, endpoint versioning,
and seamless integration with existing FastAPI routing infrastructure.
"""

import logging
from typing import Dict, List, Optional, Callable, Any, Union
from functools import wraps
from collections import defaultdict

from fastapi import APIRouter, Request, Response, HTTPException, Depends
from fastapi.routing import APIRoute
from fastapi.responses import JSONResponse

from .version_manager import APIVersion, VersionManager, UnsupportedVersionError
from .response_transformers import VersionedResponseBuilder
from ..api_models import APIResponse, APIStatus, APIError, ErrorCode

logger = logging.getLogger(__name__)


class VersionedEndpoint:
    """Represents a versioned API endpoint with multiple version handlers."""
    
    def __init__(self, path: str, method: str):
        self.path = path
        self.method = method
        self.handlers: Dict[str, Callable] = {}  # version -> handler
        self.fallback_handler: Optional[Callable] = None
        self.metadata: Dict[str, Any] = {}
    
    def add_handler(self, version: APIVersion, handler: Callable):
        """Add a version-specific handler."""
        version_str = str(version)
        self.handlers[version_str] = handler
        logger.debug(f"Added handler for {self.method} {self.path} v{version_str}")
    
    def set_fallback_handler(self, handler: Callable):
        """Set fallback handler for unsupported versions."""
        self.fallback_handler = handler
    
    def get_handler(self, version: APIVersion) -> Optional[Callable]:
        """Get handler for specific version with intelligent fallback."""
        version_str = str(version)
        
        # Direct version match
        if version_str in self.handlers:
            return self.handlers[version_str]
        
        # Find compatible version (same major, highest minor)
        compatible_versions = []
        for handler_version_str in self.handlers.keys():
            handler_version = APIVersion.from_string(handler_version_str)
            if handler_version.is_compatible_with(version):
                compatible_versions.append(handler_version)
        
        if compatible_versions:
            # Return handler for highest compatible version
            best_version = max(compatible_versions)
            return self.handlers[str(best_version)]
        
        # Return fallback handler if available
        return self.fallback_handler
    
    def get_supported_versions(self) -> List[APIVersion]:
        """Get list of supported versions for this endpoint."""
        return [APIVersion.from_string(v) for v in self.handlers.keys()]


class VersionedRouter:
    """
    Version-aware router that manages multiple API versions with intelligent routing.
    
    Features:
    - Version-specific endpoint handlers
    - Intelligent fallback to compatible versions
    - Automatic version detection and validation
    - Performance monitoring and metrics
    - Seamless FastAPI integration
    """
    
    def __init__(
        self,
        service_name: str,
        version_manager: Optional[VersionManager] = None,
        response_builder: Optional[VersionedResponseBuilder] = None,
        enable_fallback: bool = True,
        enable_metrics: bool = True
    ):
        self.service_name = service_name
        self.enable_fallback = enable_fallback
        self.enable_metrics = enable_metrics
        
        # Version management
        self.version_manager = version_manager or VersionManager(
            service_name=service_name
        )
        self.response_builder = response_builder or VersionedResponseBuilder(
            service_name=service_name
        )
        
        # Endpoint registry
        self.endpoints: Dict[str, VersionedEndpoint] = {}  # "METHOD:path" -> endpoint
        
        # FastAPI routers for each version
        self.routers: Dict[str, APIRouter] = {}
        
        # Metrics
        self.request_count = 0
        self.version_usage: Dict[str, int] = defaultdict(int)
        
        logger.info(f"VersionedRouter initialized for {service_name}")
    
    def create_version_router(self, version: APIVersion, **router_kwargs) -> APIRouter:
        """Create or get FastAPI router for specific version."""
        version_str = str(version)
        
        if version_str not in self.routers:
            # Create router with version-specific prefix
            router_kwargs.setdefault('prefix', f'/api/{version_str}')
            router_kwargs.setdefault('tags', [f'{version_str}'])
            
            self.routers[version_str] = APIRouter(**router_kwargs)
            logger.info(f"Created router for version {version_str}")
        
        return self.routers[version_str]
    
    def version(
        self,
        version: Union[str, APIVersion],
        path: str,
        methods: List[str] = None,
        **route_kwargs
    ):
        """
        Decorator to register version-specific endpoint handlers.
        
        Usage:
            @router.version("v1.0.0", "/users", ["GET"])
            async def get_users_v1():
                return {"users": []}
        """
        if isinstance(version, str):
            version = APIVersion.from_string(version)
        
        methods = methods or ["GET"]
        
        def decorator(handler: Callable):
            # Register endpoint for each HTTP method
            for method in methods:
                endpoint_key = f"{method.upper()}:{path}"
                
                if endpoint_key not in self.endpoints:
                    self.endpoints[endpoint_key] = VersionedEndpoint(path, method.upper())
                
                self.endpoints[endpoint_key].add_handler(version, handler)
                
                # Add to version-specific router
                version_router = self.create_version_router(version)
                route_method = getattr(version_router, method.lower())
                route_method(path, **route_kwargs)(handler)
            
            return handler
        
        return decorator
    
    def fallback(self, path: str, methods: List[str] = None):
        """
        Decorator to register fallback handlers for unsupported versions.
        
        Usage:
            @router.fallback("/users", ["GET"])
            async def get_users_fallback():
                return {"error": "Version not supported"}
        """
        methods = methods or ["GET"]
        
        def decorator(handler: Callable):
            for method in methods:
                endpoint_key = f"{method.upper()}:{path}"
                
                if endpoint_key not in self.endpoints:
                    self.endpoints[endpoint_key] = VersionedEndpoint(path, method.upper())
                
                self.endpoints[endpoint_key].set_fallback_handler(handler)
            
            return handler
        
        return decorator
    
    def route_request(self, request: Request) -> Callable:
        """
        Route request to appropriate version handler.
        
        This method is called by the version routing middleware.
        """
        # Get version from request state (set by middleware)
        version = getattr(request.state, 'api_version', self.version_manager.current_version)
        
        # Find endpoint
        endpoint_key = f"{request.method}:{request.url.path}"
        
        # Remove version prefix from path for lookup
        clean_path = self._clean_path_for_lookup(request.url.path)
        clean_endpoint_key = f"{request.method}:{clean_path}"
        
        endpoint = self.endpoints.get(clean_endpoint_key)
        if not endpoint:
            raise HTTPException(status_code=404, detail="Endpoint not found")
        
        # Get version-specific handler
        handler = endpoint.get_handler(version)
        if not handler:
            if self.enable_fallback and endpoint.fallback_handler:
                handler = endpoint.fallback_handler
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Version {version} not supported for {endpoint_key}"
                )
        
        # Track metrics
        if self.enable_metrics:
            self.request_count += 1
            self.version_usage[str(version)] += 1
        
        return handler
    
    def _clean_path_for_lookup(self, path: str) -> str:
        """Remove version prefix from path for endpoint lookup."""
        # Remove /api/vX.Y.Z prefix
        import re
        pattern = r'^/api/v\d+\.\d+\.\d+'
        return re.sub(pattern, '', path) or '/'
    
    def get_version_info(self) -> Dict[str, Any]:
        """Get comprehensive version information for all endpoints."""
        info = {
            "service": self.service_name,
            "total_endpoints": len(self.endpoints),
            "total_requests": self.request_count,
            "version_usage": dict(self.version_usage),
            "endpoints": {}
        }
        
        for endpoint_key, endpoint in self.endpoints.items():
            supported_versions = [str(v) for v in endpoint.get_supported_versions()]
            info["endpoints"][endpoint_key] = {
                "path": endpoint.path,
                "method": endpoint.method,
                "supported_versions": supported_versions,
                "has_fallback": endpoint.fallback_handler is not None
            }
        
        return info
    
    def create_openapi_spec(self) -> Dict[str, Any]:
        """Create OpenAPI specification for all versions."""
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": f"{self.service_name} API",
                "version": "multi-version",
                "description": "Multi-version API with backward compatibility"
            },
            "servers": [],
            "paths": {},
            "components": {
                "schemas": {},
                "parameters": {
                    "ApiVersion": {
                        "name": "API-Version",
                        "in": "header",
                        "description": "API version to use",
                        "schema": {"type": "string", "example": "v1.0.0"}
                    }
                }
            }
        }
        
        # Add servers for each version
        for version_str in self.routers.keys():
            spec["servers"].append({
                "url": f"/api/{version_str}",
                "description": f"API {version_str}"
            })
        
        # Add paths from each router
        for version_str, router in self.routers.items():
            if hasattr(router, 'routes'):
                for route in router.routes:
                    if isinstance(route, APIRoute):
                        path_key = route.path
                        if path_key not in spec["paths"]:
                            spec["paths"][path_key] = {}
                        
                        for method in route.methods:
                            if method.lower() != 'head':  # Skip HEAD methods
                                spec["paths"][path_key][method.lower()] = {
                                    "summary": f"{method} {path_key} ({version_str})",
                                    "parameters": [
                                        {"$ref": "#/components/parameters/ApiVersion"}
                                    ],
                                    "responses": {
                                        "200": {"description": "Success"},
                                        "400": {"description": "Bad Request"},
                                        "404": {"description": "Not Found"}
                                    },
                                    "tags": [version_str]
                                }
        
        return spec


# Utility functions for creating versioned routers
def create_versioned_router(
    service_name: str,
    current_version: str = "v1.0.0",
    supported_versions: Optional[List[str]] = None,
    **kwargs
) -> VersionedRouter:
    """
    Factory function to create a versioned router with sensible defaults.
    
    Args:
        service_name: Name of the service
        current_version: Current API version
        supported_versions: List of supported versions
        **kwargs: Additional router configuration
    
    Returns:
        Configured VersionedRouter instance
    """
    # Create version manager
    version_manager = VersionManager(
        service_name=service_name,
        current_version=current_version
    )
    
    # Register supported versions
    if supported_versions:
        for version_str in supported_versions:
            version_manager.register_version(version_str)
    
    return VersionedRouter(
        service_name=service_name,
        version_manager=version_manager,
        **kwargs
    )


# Dependency for getting current API version in endpoints
def get_api_version(request: Request) -> APIVersion:
    """FastAPI dependency to get current API version from request."""
    return getattr(request.state, 'api_version', APIVersion(1, 0, 0))


# Decorator for automatic version-aware response building
def versioned_response(
    response_builder: Optional[VersionedResponseBuilder] = None
):
    """
    Decorator to automatically build version-aware responses.
    
    Usage:
        @versioned_response()
        async def get_users(version: APIVersion = Depends(get_api_version)):
            return {"users": []}
    """
    def decorator(handler: Callable):
        @wraps(handler)
        async def wrapper(*args, **kwargs):
            # Extract request and version from arguments
            request = None
            version = None
            
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            for key, value in kwargs.items():
                if isinstance(value, APIVersion):
                    version = value
                    break
            
            # Call original handler
            result = await handler(*args, **kwargs)
            
            # Build versioned response if response_builder is available
            if response_builder and version:
                if isinstance(result, dict):
                    return response_builder.build_response(
                        status=APIStatus.SUCCESS,
                        data=result,
                        target_version=version
                    )
            
            return result
        
        return wrapper
    
    return decorator
