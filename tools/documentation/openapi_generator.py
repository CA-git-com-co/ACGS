#!/usr/bin/env python3
"""
ACGS-1 Automated OpenAPI Documentation Generator

This tool automatically generates comprehensive OpenAPI 3.0 specifications for all
ACGS microservices by analyzing FastAPI applications, extracting schemas, and
creating standardized documentation with examples and error responses.

Features:
- Automatic FastAPI application discovery and analysis
- OpenAPI 3.0 specification generation with unified response formats
- Error response schema integration from error catalog
- Example generation for request/response payloads
- Service-specific customization and branding
- Multi-format output (JSON, YAML, HTML)
- CI/CD pipeline integration support
"""

import os
import sys
import json
import yaml
import asyncio
import importlib
import inspect
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import argparse
import logging

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from fastapi import FastAPI
    from fastapi.openapi.utils import get_openapi
    from fastapi.routing import APIRoute
    import uvicorn

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    print("Warning: FastAPI not available. Install with: pip install fastapi uvicorn")

try:
    from services.shared.errors.error_catalog import (
        export_error_catalog,
        get_service_errors,
        ServiceCode,
    )
    from services.shared.response.unified_response import UnifiedResponse

    ERROR_CATALOG_AVAILABLE = True
except ImportError:
    ERROR_CATALOG_AVAILABLE = False
    print("Warning: Error catalog not available")


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class OpenAPIGenerator:
    """Automated OpenAPI documentation generator for ACGS services."""

    def __init__(self, output_dir: str = "docs/api/generated"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.service_configs = {
            "auth": {
                "name": "Authentication Service",
                "description": "ACGS Authentication and Authorization Service",
                "version": "2.1.0",
                "port": 8000,
                "module_path": "services.platform.authentication.auth_service.app.main",
                "app_variable": "app",
                "tags": ["authentication", "authorization", "users", "tokens"],
            },
            "ac": {
                "name": "Constitutional AI Service",
                "description": "ACGS Constitutional AI Principles and Compliance Service",
                "version": "2.1.0",
                "port": 8001,
                "module_path": "services.platform.constitutional_ai.ac_service.app.main",
                "app_variable": "app",
                "tags": ["constitutional-ai", "principles", "compliance", "council"],
            },
            "integrity": {
                "name": "Integrity Service",
                "description": "ACGS Cryptographic Integrity and Audit Service",
                "version": "2.0.0",
                "port": 8002,
                "module_path": "services.platform.integrity.integrity_service.app.main",
                "app_variable": "app",
                "tags": ["integrity", "cryptography", "audit", "certificates"],
            },
            "fv": {
                "name": "Formal Verification Service",
                "description": "ACGS Formal Verification and Mathematical Proof Service",
                "version": "1.5.0",
                "port": 8003,
                "module_path": "services.platform.formal_verification.fv_service.app.main",
                "app_variable": "app",
                "tags": ["formal-verification", "proofs", "z3", "smt"],
            },
            "gs": {
                "name": "Governance Synthesis Service",
                "description": "ACGS Governance Policy Synthesis and Generation Service",
                "version": "2.2.0",
                "port": 8004,
                "module_path": "services.platform.governance_synthesis.gs_service.app.main",
                "app_variable": "app",
                "tags": ["governance", "synthesis", "policies", "templates"],
            },
            "pgc": {
                "name": "Policy Governance Service",
                "description": "ACGS Policy Governance and Enforcement Service",
                "version": "2.0.0",
                "port": 8005,
                "module_path": "services.platform.policy_governance.pgc_service.app.main",
                "app_variable": "app",
                "tags": ["policy", "governance", "enforcement", "opa"],
            },
            "ec": {
                "name": "Evolutionary Computation Service",
                "description": "ACGS Evolutionary Computation and Optimization Service",
                "version": "1.8.0",
                "port": 8006,
                "module_path": "services.platform.evolutionary_computation.ec_service.app.main",
                "app_variable": "app",
                "tags": ["evolution", "optimization", "algorithms", "metrics"],
            },
            "dgm": {
                "name": "Darwin Gödel Machine Service",
                "description": "ACGS Darwin Gödel Machine Self-Improvement Service",
                "version": "1.0.0",
                "port": 8007,
                "module_path": "services.platform.darwin_godel_machine.dgm_service.app.main",
                "app_variable": "app",
                "tags": ["self-improvement", "godel", "darwin", "workspace"],
            },
        }

        self.global_schemas = {}
        self.error_responses = {}
        self._load_global_schemas()

    def _load_global_schemas(self):
        """Load global schemas for unified responses and error handling."""

        # Unified response schema
        self.global_schemas["UnifiedResponse"] = {
            "type": "object",
            "properties": {
                "success": {
                    "type": "boolean",
                    "description": "Indicates if the request was successful",
                },
                "data": {"description": "Response data payload", "nullable": True},
                "message": {
                    "type": "string",
                    "description": "Human-readable response message",
                },
                "metadata": {"$ref": "#/components/schemas/ResponseMetadata"},
                "pagination": {
                    "$ref": "#/components/schemas/PaginationMetadata",
                    "nullable": True,
                },
            },
            "required": ["success", "data", "message", "metadata"],
        }

        # Response metadata schema
        self.global_schemas["ResponseMetadata"] = {
            "type": "object",
            "properties": {
                "timestamp": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Response timestamp in ISO 8601 format",
                },
                "request_id": {
                    "type": "string",
                    "format": "uuid",
                    "description": "Unique request identifier for correlation",
                },
                "version": {"type": "string", "description": "API version"},
                "service": {"type": "string", "description": "Service name"},
                "execution_time_ms": {
                    "type": "number",
                    "description": "Request execution time in milliseconds",
                    "nullable": True,
                },
            },
            "required": ["timestamp", "request_id", "version", "service"],
        }

        # Pagination metadata schema
        self.global_schemas["PaginationMetadata"] = {
            "type": "object",
            "properties": {
                "page": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Current page number",
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Number of items per page",
                },
                "total": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "Total number of items",
                },
                "has_next": {
                    "type": "boolean",
                    "description": "Whether there are more pages",
                },
                "has_previous": {
                    "type": "boolean",
                    "description": "Whether there are previous pages",
                },
            },
            "required": ["page", "limit", "total", "has_next", "has_previous"],
        }

        # Error response schema
        self.global_schemas["ErrorResponse"] = {
            "type": "object",
            "properties": {
                "success": {
                    "type": "boolean",
                    "enum": [False],
                    "description": "Always false for error responses",
                },
                "error": {"$ref": "#/components/schemas/ErrorDetails"},
                "data": {
                    "nullable": True,
                    "description": "Always null for error responses",
                },
                "metadata": {"$ref": "#/components/schemas/ResponseMetadata"},
            },
            "required": ["success", "error", "data", "metadata"],
        }

        # Error details schema
        self.global_schemas["ErrorDetails"] = {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "pattern": "^[A-Z]+_[A-Z_]+_[0-9]{3}$",
                    "description": "Hierarchical error code (SERVICE_CATEGORY_NUMBER)",
                },
                "message": {
                    "type": "string",
                    "description": "Human-readable error message",
                },
                "details": {
                    "type": "object",
                    "description": "Additional error details and context",
                },
                "timestamp": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Error timestamp",
                },
                "request_id": {
                    "type": "string",
                    "format": "uuid",
                    "description": "Request identifier for correlation",
                },
                "service": {
                    "type": "string",
                    "description": "Service that generated the error",
                },
                "category": {
                    "type": "string",
                    "enum": [
                        "VALIDATION",
                        "AUTHENTICATION",
                        "AUTHORIZATION",
                        "BUSINESS_LOGIC",
                        "EXTERNAL_SERVICE",
                        "SYSTEM_ERROR",
                    ],
                    "description": "Error category",
                },
                "severity": {
                    "type": "string",
                    "enum": ["info", "warning", "error", "critical"],
                    "description": "Error severity level",
                },
                "retryable": {
                    "type": "boolean",
                    "description": "Whether the error is retryable",
                },
                "resolution_guidance": {
                    "type": "string",
                    "description": "Guidance on how to resolve the error",
                },
            },
            "required": [
                "code",
                "message",
                "details",
                "timestamp",
                "request_id",
                "service",
                "category",
                "severity",
                "retryable",
                "resolution_guidance",
            ],
        }

        # Load error responses from catalog
        if ERROR_CATALOG_AVAILABLE:
            self._load_error_responses()

    def _load_error_responses(self):
        """Load error responses from error catalog."""
        try:
            error_catalog = export_error_catalog()

            for error_code, error_data in error_catalog["errors"].items():
                self.error_responses[error_data["http_status"]] = {
                    "description": f"Error response - {error_data['message']}",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ErrorResponse"},
                            "example": {
                                "success": False,
                                "error": {
                                    "code": error_code,
                                    "message": error_data["message"],
                                    "details": {},
                                    "timestamp": "2025-06-22T10:30:00Z",
                                    "request_id": "550e8400-e29b-41d4-a716-446655440000",
                                    "service": error_data["service"].lower()
                                    + "-service",
                                    "category": error_data["category"],
                                    "severity": error_data["severity"],
                                    "retryable": error_data["retryable"],
                                    "resolution_guidance": error_data[
                                        "resolution_guidance"
                                    ],
                                },
                                "data": None,
                                "metadata": {
                                    "timestamp": "2025-06-22T10:30:00Z",
                                    "request_id": "550e8400-e29b-41d4-a716-446655440000",
                                    "version": "1.0.0",
                                    "service": error_data["service"].lower()
                                    + "-service",
                                },
                            },
                        }
                    },
                }
        except Exception as e:
            logger.warning(f"Could not load error responses: {e}")

    def discover_fastapi_app(self, service_key: str) -> Optional[FastAPI]:
        """Discover and load FastAPI application for a service."""
        if not FASTAPI_AVAILABLE:
            logger.error("FastAPI not available")
            return None

        config = self.service_configs.get(service_key)
        if not config:
            logger.error(f"Unknown service: {service_key}")
            return None

        try:
            # Try to import the module
            module = importlib.import_module(config["module_path"])
            app = getattr(module, config["app_variable"])

            if isinstance(app, FastAPI):
                logger.info(f"Successfully loaded FastAPI app for {config['name']}")
                return app
            else:
                logger.error(
                    f"Found {config['app_variable']} but it's not a FastAPI instance"
                )
                return None

        except ImportError as e:
            logger.warning(f"Could not import {config['module_path']}: {e}")
            return None
        except AttributeError as e:
            logger.warning(
                f"Could not find {config['app_variable']} in {config['module_path']}: {e}"
            )
            return None
        except Exception as e:
            logger.error(f"Error loading FastAPI app for {service_key}: {e}")
            return None

    def create_mock_fastapi_app(self, service_key: str) -> FastAPI:
        """Create a mock FastAPI app with common endpoints for documentation generation."""
        if not FASTAPI_AVAILABLE:
            raise ImportError("FastAPI not available")

        config = self.service_configs[service_key]

        app = FastAPI(
            title=config["name"],
            description=config["description"],
            version=config["version"],
            tags_metadata=[
                {
                    "name": tag,
                    "description": f"{tag.replace('-', ' ').title()} operations",
                }
                for tag in config["tags"]
            ],
        )

        # Add common endpoints based on service type
        self._add_common_endpoints(app, service_key, config)

        return app

    def _add_common_endpoints(
        self, app: FastAPI, service_key: str, config: Dict[str, Any]
    ):
        """Add common endpoints to mock FastAPI app."""

        # Health endpoint (all services)
        @app.get("/health", tags=["health"], summary="Health Check")
        async def health_check():
            """Check service health and status."""
            return {
                "status": "healthy",
                "service": config["name"],
                "version": config["version"],
                "timestamp": datetime.now().isoformat(),
            }

        # Service-specific endpoints
        if service_key == "auth":
            self._add_auth_endpoints(app)
        elif service_key == "ac":
            self._add_ac_endpoints(app)
        elif service_key == "integrity":
            self._add_integrity_endpoints(app)
        elif service_key == "fv":
            self._add_fv_endpoints(app)
        elif service_key == "gs":
            self._add_gs_endpoints(app)
        elif service_key == "pgc":
            self._add_pgc_endpoints(app)
        elif service_key == "ec":
            self._add_ec_endpoints(app)
        elif service_key == "dgm":
            self._add_dgm_endpoints(app)

    def _add_auth_endpoints(self, app: FastAPI):
        """Add authentication service endpoints."""

        @app.post("/auth/register", tags=["authentication"], summary="Register User")
        async def register_user():
            """Register a new user account."""
            pass

        @app.post("/auth/login", tags=["authentication"], summary="User Login")
        async def login():
            """Authenticate user and return access token."""
            pass

        @app.post("/auth/logout", tags=["authentication"], summary="User Logout")
        async def logout():
            """Logout user and revoke tokens."""
            pass

        @app.get("/auth/me", tags=["users"], summary="Get Current User")
        async def get_current_user():
            """Get current authenticated user information."""
            pass

        @app.post("/auth/token/refresh", tags=["tokens"], summary="Refresh Token")
        async def refresh_token():
            """Refresh authentication token."""
            pass

    def _add_ac_endpoints(self, app: FastAPI):
        """Add constitutional AI service endpoints."""

        @app.get(
            "/api/v1/constitutional/principles",
            tags=["principles"],
            summary="Get Constitutional Principles",
        )
        async def get_principles():
            """Retrieve constitutional principles and rules."""
            pass

        @app.post(
            "/api/v1/constitutional/principles",
            tags=["principles"],
            summary="Create Principle",
        )
        async def create_principle():
            """Create a new constitutional principle."""
            pass

        @app.get(
            "/api/v1/constitutional/council",
            tags=["council"],
            summary="Get Council Status",
        )
        async def get_council():
            """Get constitutional council status and members."""
            pass

        @app.get(
            "/api/v1/constitutional/compliance",
            tags=["compliance"],
            summary="Check Compliance",
        )
        async def check_compliance():
            """Check constitutional compliance for operations."""
            pass

    def _add_integrity_endpoints(self, app: FastAPI):
        """Add integrity service endpoints."""

        @app.get("/api/v1/integrity/audit-log", tags=["audit"], summary="Get Audit Log")
        async def get_audit_log():
            """Retrieve system audit log entries."""
            pass

        @app.get(
            "/api/v1/integrity/certificates",
            tags=["certificates"],
            summary="Get Certificates",
        )
        async def get_certificates():
            """Retrieve cryptographic certificates."""
            pass

        @app.post(
            "/api/v1/integrity/verify",
            tags=["verification"],
            summary="Verify Signature",
        )
        async def verify_signature():
            """Verify digital signature integrity."""
            pass

    def _add_fv_endpoints(self, app: FastAPI):
        """Add formal verification service endpoints."""

        @app.post(
            "/api/v1/verification/verify",
            tags=["verification"],
            summary="Verify Property",
        )
        async def verify_property():
            """Formally verify a mathematical property."""
            pass

        @app.get(
            "/api/v1/verification/results",
            tags=["results"],
            summary="Get Verification Results",
        )
        async def get_results():
            """Retrieve formal verification results."""
            pass

        @app.get(
            "/api/v1/verification/rules",
            tags=["rules"],
            summary="Get Verification Rules",
        )
        async def get_rules():
            """Get available verification rules and templates."""
            pass

    def _add_gs_endpoints(self, app: FastAPI):
        """Add governance synthesis service endpoints."""

        @app.post(
            "/api/v1/synthesis/generate", tags=["synthesis"], summary="Generate Policy"
        )
        async def generate_policy():
            """Generate governance policy from principles."""
            pass

        @app.get(
            "/api/v1/synthesis/templates", tags=["templates"], summary="Get Templates"
        )
        async def get_templates():
            """Retrieve policy generation templates."""
            pass

        @app.get(
            "/api/v1/synthesis/history",
            tags=["history"],
            summary="Get Generation History",
        )
        async def get_history():
            """Get policy generation history."""
            pass

    def _add_pgc_endpoints(self, app: FastAPI):
        """Add policy governance service endpoints."""

        @app.get(
            "/api/v1/enforcement/policies", tags=["policies"], summary="Get Policies"
        )
        async def get_policies():
            """Retrieve governance policies."""
            pass

        @app.post(
            "/api/v1/enforcement/evaluate",
            tags=["evaluation"],
            summary="Evaluate Policy",
        )
        async def evaluate_policy():
            """Evaluate policy against input data."""
            pass

        @app.get(
            "/api/v1/enforcement/decisions", tags=["decisions"], summary="Get Decisions"
        )
        async def get_decisions():
            """Get policy evaluation decisions."""
            pass

    def _add_ec_endpoints(self, app: FastAPI):
        """Add evolutionary computation service endpoints."""

        @app.post(
            "/api/v1/evolution/optimize",
            tags=["optimization"],
            summary="Start Optimization",
        )
        async def start_optimization():
            """Start evolutionary optimization process."""
            pass

        @app.get("/api/v1/evolution/metrics", tags=["metrics"], summary="Get Metrics")
        async def get_metrics():
            """Get evolutionary computation metrics."""
            pass

        @app.get(
            "/api/v1/evolution/history",
            tags=["history"],
            summary="Get Evolution History",
        )
        async def get_history():
            """Get evolution process history."""
            pass

    def _add_dgm_endpoints(self, app: FastAPI):
        """Add Darwin Gödel Machine service endpoints."""

        @app.get("/api/v1/dgm/workspace", tags=["workspace"], summary="Get Workspace")
        async def get_workspace():
            """Get self-improvement workspace status."""
            pass

        @app.post(
            "/api/v1/dgm/propose", tags=["improvement"], summary="Propose Improvement"
        )
        async def propose_improvement():
            """Propose self-improvement modification."""
            pass

        @app.get("/api/v1/dgm/metrics", tags=["metrics"], summary="Get Metrics")
        async def get_metrics():
            """Get self-improvement metrics."""
            pass

    def generate_openapi_spec(
        self, service_key: str, use_mock: bool = False
    ) -> Dict[str, Any]:
        """Generate OpenAPI 3.0 specification for a service."""

        config = self.service_configs.get(service_key)
        if not config:
            raise ValueError(f"Unknown service: {service_key}")

        # Try to load real FastAPI app first, fall back to mock
        app = None
        if not use_mock:
            app = self.discover_fastapi_app(service_key)

        if app is None:
            logger.info(f"Using mock FastAPI app for {config['name']}")
            app = self.create_mock_fastapi_app(service_key)

        # Generate base OpenAPI spec
        openapi_spec = get_openapi(
            title=config["name"],
            version=config["version"],
            description=config["description"],
            routes=app.routes,
            tags=app.tags_metadata,
        )

        # Enhance the specification
        self._enhance_openapi_spec(openapi_spec, service_key, config)

        return openapi_spec

    def _enhance_openapi_spec(
        self, spec: Dict[str, Any], service_key: str, config: Dict[str, Any]
    ):
        """Enhance OpenAPI specification with ACGS-specific features."""

        # Add server information
        spec["servers"] = [
            {
                "url": f"http://localhost:{config['port']}",
                "description": "Development server",
            },
            {
                "url": f"https://api.acgs.dev/{service_key}",
                "description": "Development environment",
            },
            {
                "url": f"https://api.acgs.com/{service_key}",
                "description": "Production environment",
            },
        ]

        # Add contact and license information
        spec["info"]["contact"] = {
            "name": "ACGS Development Team",
            "url": "https://acgs.com/support",
            "email": "api-support@acgs.com",
        }

        spec["info"]["license"] = {
            "name": "ACGS License",
            "url": "https://acgs.com/license",
        }

        # Add external documentation
        spec["externalDocs"] = {
            "description": "ACGS API Documentation",
            "url": "https://docs.acgs.com",
        }

        # Ensure components section exists
        if "components" not in spec:
            spec["components"] = {}

        if "schemas" not in spec["components"]:
            spec["components"]["schemas"] = {}

        # Add global schemas
        spec["components"]["schemas"].update(self.global_schemas)

        # Add security schemes
        spec["components"]["securitySchemes"] = {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "JWT token authentication",
            },
            "CookieAuth": {
                "type": "apiKey",
                "in": "cookie",
                "name": "access_token_cookie",
                "description": "Cookie-based authentication",
            },
        }

        # Add global security requirement
        if service_key != "auth":  # Auth service has its own security handling
            spec["security"] = [{"BearerAuth": []}, {"CookieAuth": []}]

        # Enhance paths with unified responses and error handling
        self._enhance_paths(spec, service_key)

        # Add service-specific tags
        if "tags" not in spec:
            spec["tags"] = []

        spec["tags"].extend(
            [
                {
                    "name": tag,
                    "description": f"{tag.replace('-', ' ').title()} operations",
                }
                for tag in config["tags"]
            ]
        )

    def _enhance_paths(self, spec: Dict[str, Any], service_key: str):
        """Enhance API paths with unified responses and error handling."""

        if "paths" not in spec:
            return

        for path, path_item in spec["paths"].items():
            for method, operation in path_item.items():
                if method.lower() in ["get", "post", "put", "patch", "delete"]:
                    self._enhance_operation(operation, service_key)

    def _enhance_operation(self, operation: Dict[str, Any], service_key: str):
        """Enhance individual operation with unified responses."""

        # Ensure responses section exists
        if "responses" not in operation:
            operation["responses"] = {}

        # Add success response with unified format
        if "200" not in operation["responses"]:
            operation["responses"]["200"] = {
                "description": "Successful response",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/UnifiedResponse"},
                        "example": {
                            "success": True,
                            "data": {},
                            "message": "Request completed successfully",
                            "metadata": {
                                "timestamp": "2025-06-22T10:30:00Z",
                                "request_id": "550e8400-e29b-41d4-a716-446655440000",
                                "version": "1.0.0",
                                "service": f"{service_key}-service",
                            },
                        },
                    }
                },
            }

        # Add common error responses
        error_responses = {
            "400": "Bad Request - Invalid input parameters",
            "401": "Unauthorized - Authentication required",
            "403": "Forbidden - Insufficient permissions",
            "404": "Not Found - Resource not found",
            "422": "Unprocessable Entity - Validation failed",
            "500": "Internal Server Error - Unexpected error",
            "503": "Service Unavailable - Service temporarily unavailable",
        }

        for status_code, description in error_responses.items():
            if status_code not in operation["responses"]:
                operation["responses"][status_code] = {
                    "description": description,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                        }
                    },
                }

        # Add request ID parameter for correlation
        if "parameters" not in operation:
            operation["parameters"] = []

        # Check if X-Request-ID parameter already exists
        has_request_id = any(
            param.get("name") == "X-Request-ID" for param in operation["parameters"]
        )

        if not has_request_id:
            operation["parameters"].append(
                {
                    "name": "X-Request-ID",
                    "in": "header",
                    "required": False,
                    "schema": {"type": "string", "format": "uuid"},
                    "description": "Optional request ID for correlation tracking",
                }
            )

    def generate_all_specs(self, use_mock: bool = False) -> Dict[str, Dict[str, Any]]:
        """Generate OpenAPI specifications for all services."""

        specs = {}

        for service_key in self.service_configs.keys():
            try:
                logger.info(f"Generating OpenAPI spec for {service_key}")
                spec = self.generate_openapi_spec(service_key, use_mock)
                specs[service_key] = spec
                logger.info(f"Successfully generated spec for {service_key}")
            except Exception as e:
                logger.error(f"Failed to generate spec for {service_key}: {e}")
                specs[service_key] = None

        return specs

    def save_spec(
        self,
        service_key: str,
        spec: Dict[str, Any],
        formats: List[str] = ["json", "yaml"],
    ):
        """Save OpenAPI specification in multiple formats."""

        config = self.service_configs[service_key]
        base_filename = f"{service_key}_openapi"

        # Save JSON format
        if "json" in formats:
            json_path = self.output_dir / f"{base_filename}.json"
            with open(json_path, "w") as f:
                json.dump(spec, f, indent=2)
            logger.info(f"Saved JSON spec: {json_path}")

        # Save YAML format
        if "yaml" in formats:
            yaml_path = self.output_dir / f"{base_filename}.yaml"
            with open(yaml_path, "w") as f:
                yaml.dump(spec, f, default_flow_style=False, sort_keys=False)
            logger.info(f"Saved YAML spec: {yaml_path}")

        # Generate HTML documentation
        if "html" in formats:
            self._generate_html_docs(service_key, spec)

    def _generate_html_docs(self, service_key: str, spec: Dict[str, Any]):
        """Generate HTML documentation using Swagger UI."""

        config = self.service_configs[service_key]
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{config['name']} API Documentation</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui.css" />
    <style>
        html {{
            box-sizing: border-box;
            overflow: -moz-scrollbars-vertical;
            overflow-y: scroll;
        }}
        *, *:before, *:after {{
            box-sizing: inherit;
        }}
        body {{
            margin:0;
            background: #fafafa;
        }}
        .swagger-ui .topbar {{
            background-color: #1f2937;
        }}
        .swagger-ui .topbar .download-url-wrapper .download-url-button {{
            background-color: #3b82f6;
        }}
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {{
            const ui = SwaggerUIBundle({{
                url: './{service_key}_openapi.json',
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout",
                tryItOutEnabled: true,
                requestInterceptor: function(request) {{
                    // Add request ID header
                    request.headers['X-Request-ID'] = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {{
                        var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
                        return v.toString(16);
                    }});
                    return request;
                }}
            }});
        }};
    </script>
</body>
</html>
        """

        html_path = self.output_dir / f"{service_key}_docs.html"
        with open(html_path, "w") as f:
            f.write(html_content)

        logger.info(f"Generated HTML docs: {html_path}")

    def generate_combined_spec(
        self, specs: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate combined OpenAPI specification for all services."""

        combined_spec = {
            "openapi": "3.0.3",
            "info": {
                "title": "ACGS API Documentation",
                "description": "Comprehensive API documentation for all ACGS microservices",
                "version": "1.0.0",
                "contact": {
                    "name": "ACGS Development Team",
                    "url": "https://acgs.com/support",
                    "email": "api-support@acgs.com",
                },
                "license": {"name": "ACGS License", "url": "https://acgs.com/license"},
            },
            "servers": [
                {"url": "http://localhost", "description": "Development environment"},
                {
                    "url": "https://api.acgs.com",
                    "description": "Production environment",
                },
            ],
            "paths": {},
            "components": {
                "schemas": self.global_schemas,
                "securitySchemes": {
                    "BearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT",
                    }
                },
            },
            "tags": [],
        }

        # Combine paths from all services
        for service_key, spec in specs.items():
            if spec is None:
                continue

            service_config = self.service_configs[service_key]

            # Add service-specific paths with prefix
            if "paths" in spec:
                for path, path_item in spec["paths"].items():
                    # Add service prefix to path
                    prefixed_path = (
                        f"/{service_key}{path}"
                        if not path.startswith(f"/{service_key}")
                        else path
                    )
                    combined_spec["paths"][prefixed_path] = path_item

            # Add service tags
            if "tags" in spec:
                combined_spec["tags"].extend(spec["tags"])

        return combined_spec


def main():
    """Main function for CLI usage."""
    parser = argparse.ArgumentParser(
        description="Generate OpenAPI documentation for ACGS services"
    )

    # Create a temporary generator to get service choices
    temp_generator = OpenAPIGenerator("temp")
    service_choices = list(temp_generator.service_configs.keys()) + ["all"]

    parser.add_argument(
        "--service", help="Generate docs for specific service", choices=service_choices
    )
    parser.add_argument(
        "--output", default="docs/api/generated", help="Output directory"
    )
    parser.add_argument(
        "--format",
        nargs="+",
        default=["json", "yaml", "html"],
        choices=["json", "yaml", "html"],
        help="Output formats",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Use mock FastAPI apps instead of discovering real ones",
    )
    parser.add_argument(
        "--combined",
        action="store_true",
        help="Generate combined specification for all services",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    generator = OpenAPIGenerator(args.output)

    if args.service == "all" or args.service is None:
        # Generate for all services
        logger.info("Generating OpenAPI specifications for all services")
        specs = generator.generate_all_specs(use_mock=args.mock)

        for service_key, spec in specs.items():
            if spec is not None:
                generator.save_spec(service_key, spec, args.format)

        # Generate combined specification
        if args.combined:
            logger.info("Generating combined specification")
            combined_spec = generator.generate_combined_spec(specs)
            generator.save_spec("combined", combined_spec, args.format)

    else:
        # Generate for specific service
        logger.info(f"Generating OpenAPI specification for {args.service}")
        spec = generator.generate_openapi_spec(args.service, use_mock=args.mock)
        generator.save_spec(args.service, spec, args.format)

    logger.info("Documentation generation complete")


if __name__ == "__main__":
    main()
