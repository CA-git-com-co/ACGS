#!/usr/bin/env python3
"""
ACGS-1 Simplified OpenAPI Documentation Generator

This is a simplified version of the OpenAPI generator that works without FastAPI
dependencies for testing and CI/CD environments where services may not be running.

It generates comprehensive OpenAPI 3.0 specifications based on predefined service
configurations and integrates with the unified response format and error handling.
"""

import os
import sys
import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import argparse
import logging

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SimpleOpenAPIGenerator:
    """Simplified OpenAPI documentation generator for ACGS services."""
    
    def __init__(self, output_dir: str = "docs/api/generated"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.service_configs = {
            "auth": {
                "name": "Authentication Service",
                "description": "ACGS Authentication and Authorization Service providing user management, token-based authentication, and role-based access control.",
                "version": "2.1.0",
                "port": 8000,
                "tags": ["authentication", "authorization", "users", "tokens"]
            },
            "ac": {
                "name": "Constitutional AI Service", 
                "description": "ACGS Constitutional AI Principles and Compliance Service for managing constitutional rules and ensuring system compliance.",
                "version": "2.1.0",
                "port": 8001,
                "tags": ["constitutional-ai", "principles", "compliance", "council"]
            },
            "integrity": {
                "name": "Integrity Service",
                "description": "ACGS Cryptographic Integrity and Audit Service providing digital signatures, certificates, and audit logging.",
                "version": "2.0.0",
                "port": 8002,
                "tags": ["integrity", "cryptography", "audit", "certificates"]
            },
            "fv": {
                "name": "Formal Verification Service",
                "description": "ACGS Formal Verification and Mathematical Proof Service using Z3 SMT solver for property verification.",
                "version": "1.5.0", 
                "port": 8003,
                "tags": ["formal-verification", "proofs", "z3", "smt"]
            },
            "gs": {
                "name": "Governance Synthesis Service",
                "description": "ACGS Governance Policy Synthesis and Generation Service for creating governance policies from constitutional principles.",
                "version": "2.2.0",
                "port": 8004,
                "tags": ["governance", "synthesis", "policies", "templates"]
            },
            "pgc": {
                "name": "Policy Governance Service",
                "description": "ACGS Policy Governance and Enforcement Service using OPA for policy evaluation and enforcement.",
                "version": "2.0.0",
                "port": 8005,
                "tags": ["policy", "governance", "enforcement", "opa"]
            },
            "ec": {
                "name": "Evolutionary Computation Service",
                "description": "ACGS Evolutionary Computation and Optimization Service for genetic algorithms and evolutionary optimization.",
                "version": "1.8.0",
                "port": 8006,
                "tags": ["evolution", "optimization", "algorithms", "metrics"]
            },
            "dgm": {
                "name": "Darwin Gödel Machine Service", 
                "description": "ACGS Darwin Gödel Machine Self-Improvement Service for recursive self-optimization and improvement.",
                "version": "1.0.0",
                "port": 8007,
                "tags": ["self-improvement", "godel", "darwin", "workspace"]
            }
        }
        
        self.global_schemas = self._create_global_schemas()
    
    def _create_global_schemas(self) -> Dict[str, Any]:
        """Create global schemas for unified responses and error handling."""
        return {
            "UnifiedResponse": {
                "type": "object",
                "description": "Standard unified response format for all ACGS services",
                "properties": {
                    "success": {
                        "type": "boolean",
                        "description": "Indicates if the request was successful"
                    },
                    "data": {
                        "description": "Response data payload",
                        "nullable": True
                    },
                    "message": {
                        "type": "string", 
                        "description": "Human-readable response message"
                    },
                    "metadata": {
                        "$ref": "#/components/schemas/ResponseMetadata"
                    },
                    "pagination": {
                        "$ref": "#/components/schemas/PaginationMetadata",
                        "nullable": True
                    }
                },
                "required": ["success", "data", "message", "metadata"],
                "example": {
                    "success": True,
                    "data": {"example": "data"},
                    "message": "Request completed successfully",
                    "metadata": {
                        "timestamp": "2025-06-22T10:30:00Z",
                        "request_id": "550e8400-e29b-41d4-a716-446655440000",
                        "version": "1.0.0",
                        "service": "example-service"
                    }
                }
            },
            "ResponseMetadata": {
                "type": "object",
                "description": "Response metadata for request tracking and debugging",
                "properties": {
                    "timestamp": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Response timestamp in ISO 8601 format"
                    },
                    "request_id": {
                        "type": "string",
                        "format": "uuid",
                        "description": "Unique request identifier for correlation"
                    },
                    "version": {
                        "type": "string",
                        "description": "API version"
                    },
                    "service": {
                        "type": "string", 
                        "description": "Service name"
                    },
                    "execution_time_ms": {
                        "type": "number",
                        "description": "Request execution time in milliseconds",
                        "nullable": True
                    }
                },
                "required": ["timestamp", "request_id", "version", "service"]
            },
            "PaginationMetadata": {
                "type": "object",
                "description": "Pagination metadata for paginated responses",
                "properties": {
                    "page": {
                        "type": "integer",
                        "minimum": 1,
                        "description": "Current page number"
                    },
                    "limit": {
                        "type": "integer", 
                        "minimum": 1,
                        "description": "Number of items per page"
                    },
                    "total": {
                        "type": "integer",
                        "minimum": 0,
                        "description": "Total number of items"
                    },
                    "has_next": {
                        "type": "boolean",
                        "description": "Whether there are more pages"
                    },
                    "has_previous": {
                        "type": "boolean",
                        "description": "Whether there are previous pages"
                    }
                },
                "required": ["page", "limit", "total", "has_next", "has_previous"]
            },
            "ErrorResponse": {
                "type": "object",
                "description": "Standard error response format",
                "properties": {
                    "success": {
                        "type": "boolean",
                        "enum": [False],
                        "description": "Always false for error responses"
                    },
                    "error": {
                        "$ref": "#/components/schemas/ErrorDetails"
                    },
                    "data": {
                        "nullable": True,
                        "description": "Always null for error responses"
                    },
                    "metadata": {
                        "$ref": "#/components/schemas/ResponseMetadata"
                    }
                },
                "required": ["success", "error", "data", "metadata"],
                "example": {
                    "success": False,
                    "error": {
                        "code": "AUTH_AUTHENTICATION_002",
                        "message": "Invalid credentials",
                        "details": {"username": "user123"},
                        "timestamp": "2025-06-22T10:30:00Z",
                        "request_id": "550e8400-e29b-41d4-a716-446655440000",
                        "service": "authentication-service",
                        "category": "AUTHENTICATION",
                        "severity": "warning",
                        "retryable": False,
                        "resolution_guidance": "Verify username and password are correct"
                    },
                    "data": None,
                    "metadata": {
                        "timestamp": "2025-06-22T10:30:00Z",
                        "request_id": "550e8400-e29b-41d4-a716-446655440000",
                        "version": "2.1.0",
                        "service": "authentication-service"
                    }
                }
            },
            "ErrorDetails": {
                "type": "object",
                "description": "Detailed error information",
                "properties": {
                    "code": {
                        "type": "string",
                        "pattern": "^[A-Z]+_[A-Z_]+_[0-9]{3}$",
                        "description": "Hierarchical error code (SERVICE_CATEGORY_NUMBER)"
                    },
                    "message": {
                        "type": "string",
                        "description": "Human-readable error message"
                    },
                    "details": {
                        "type": "object",
                        "description": "Additional error details and context"
                    },
                    "timestamp": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Error timestamp"
                    },
                    "request_id": {
                        "type": "string",
                        "format": "uuid", 
                        "description": "Request identifier for correlation"
                    },
                    "service": {
                        "type": "string",
                        "description": "Service that generated the error"
                    },
                    "category": {
                        "type": "string",
                        "enum": ["VALIDATION", "AUTHENTICATION", "AUTHORIZATION", "BUSINESS_LOGIC", "EXTERNAL_SERVICE", "SYSTEM_ERROR"],
                        "description": "Error category"
                    },
                    "severity": {
                        "type": "string",
                        "enum": ["info", "warning", "error", "critical"],
                        "description": "Error severity level"
                    },
                    "retryable": {
                        "type": "boolean",
                        "description": "Whether the error is retryable"
                    },
                    "resolution_guidance": {
                        "type": "string",
                        "description": "Guidance on how to resolve the error"
                    }
                },
                "required": ["code", "message", "details", "timestamp", "request_id", "service", "category", "severity", "retryable", "resolution_guidance"]
            }
        }
    
    def generate_service_spec(self, service_key: str) -> Dict[str, Any]:
        """Generate OpenAPI specification for a specific service."""
        
        config = self.service_configs.get(service_key)
        if not config:
            raise ValueError(f"Unknown service: {service_key}")
        
        # Create base OpenAPI specification
        spec = {
            "openapi": "3.0.3",
            "info": {
                "title": config["name"],
                "description": config["description"],
                "version": config["version"],
                "contact": {
                    "name": "ACGS Development Team",
                    "url": "https://acgs.com/support",
                    "email": "api-support@acgs.com"
                },
                "license": {
                    "name": "ACGS License",
                    "url": "https://acgs.com/license"
                }
            },
            "servers": [
                {
                    "url": f"http://localhost:{config['port']}",
                    "description": "Development server"
                },
                {
                    "url": f"https://api.acgs.dev/{service_key}",
                    "description": "Development environment"
                },
                {
                    "url": f"https://api.acgs.com/{service_key}",
                    "description": "Production environment"
                }
            ],
            "paths": self._generate_service_paths(service_key, config),
            "components": {
                "schemas": self.global_schemas.copy(),
                "securitySchemes": {
                    "BearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT",
                        "description": "JWT token authentication"
                    },
                    "CookieAuth": {
                        "type": "apiKey",
                        "in": "cookie",
                        "name": "access_token_cookie",
                        "description": "Cookie-based authentication"
                    }
                }
            },
            "tags": [
                {"name": tag, "description": f"{tag.replace('-', ' ').title()} operations"}
                for tag in config["tags"]
            ],
            "externalDocs": {
                "description": "ACGS API Documentation",
                "url": "https://docs.acgs.com"
            }
        }
        
        # Add security requirement for non-auth services
        if service_key != "auth":
            spec["security"] = [
                {"BearerAuth": []},
                {"CookieAuth": []}
            ]
        
        return spec
    
    def _generate_service_paths(self, service_key: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate API paths for a service."""
        
        paths = {
            "/health": {
                "get": {
                    "tags": ["health"],
                    "summary": "Health Check",
                    "description": "Check service health and status",
                    "responses": {
                        "200": {
                            "description": "Service is healthy",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/UnifiedResponse"},
                                    "example": {
                                        "success": True,
                                        "data": {
                                            "status": "healthy",
                                            "service": config["name"],
                                            "version": config["version"]
                                        },
                                        "message": "Service is healthy",
                                        "metadata": {
                                            "timestamp": "2025-06-22T10:30:00Z",
                                            "request_id": "550e8400-e29b-41d4-a716-446655440000",
                                            "version": config["version"],
                                            "service": f"{service_key}-service"
                                        }
                                    }
                                }
                            }
                        },
                        "503": {
                            "description": "Service unavailable",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                                }
                            }
                        }
                    }
                }
            }
        }
        
        # Add service-specific paths
        if service_key == "auth":
            paths.update(self._get_auth_paths())
        elif service_key == "ac":
            paths.update(self._get_ac_paths())
        elif service_key == "integrity":
            paths.update(self._get_integrity_paths())
        elif service_key == "fv":
            paths.update(self._get_fv_paths())
        elif service_key == "gs":
            paths.update(self._get_gs_paths())
        elif service_key == "pgc":
            paths.update(self._get_pgc_paths())
        elif service_key == "ec":
            paths.update(self._get_ec_paths())
        elif service_key == "dgm":
            paths.update(self._get_dgm_paths())
        
        return paths
    
    def _get_auth_paths(self) -> Dict[str, Any]:
        """Get authentication service paths."""
        return {
            "/auth/register": {
                "post": {
                    "tags": ["authentication"],
                    "summary": "Register User",
                    "description": "Register a new user account",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "username": {"type": "string"},
                                        "email": {"type": "string", "format": "email"},
                                        "password": {"type": "string", "minLength": 8},
                                        "first_name": {"type": "string"},
                                        "last_name": {"type": "string"}
                                    },
                                    "required": ["username", "email", "password"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "User registered successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/UnifiedResponse"}
                                }
                            }
                        },
                        "400": {"$ref": "#/components/responses/BadRequest"},
                        "409": {"$ref": "#/components/responses/Conflict"}
                    }
                }
            },
            "/auth/login": {
                "post": {
                    "tags": ["authentication"],
                    "summary": "User Login",
                    "description": "Authenticate user and return access token",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/x-www-form-urlencoded": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "username": {"type": "string"},
                                        "password": {"type": "string"}
                                    },
                                    "required": ["username", "password"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Authentication successful",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/UnifiedResponse"}
                                }
                            }
                        },
                        "401": {"$ref": "#/components/responses/Unauthorized"}
                    }
                }
            }
        }
    
    def _get_ac_paths(self) -> Dict[str, Any]:
        """Get constitutional AI service paths."""
        return {
            "/api/v1/constitutional/principles": {
                "get": {
                    "tags": ["principles"],
                    "summary": "Get Constitutional Principles",
                    "description": "Retrieve constitutional principles and rules",
                    "responses": {
                        "200": {
                            "description": "Principles retrieved successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/UnifiedResponse"}
                                }
                            }
                        }
                    }
                }
            }
        }
    
    def _get_integrity_paths(self) -> Dict[str, Any]:
        """Get integrity service paths."""
        return {
            "/api/v1/integrity/audit-log": {
                "get": {
                    "tags": ["audit"],
                    "summary": "Get Audit Log",
                    "description": "Retrieve system audit log entries",
                    "responses": {
                        "200": {
                            "description": "Audit log retrieved successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/UnifiedResponse"}
                                }
                            }
                        }
                    }
                }
            }
        }
    
    def _get_fv_paths(self) -> Dict[str, Any]:
        """Get formal verification service paths."""
        return {
            "/api/v1/verification/verify": {
                "post": {
                    "tags": ["verification"],
                    "summary": "Verify Property",
                    "description": "Formally verify a mathematical property",
                    "responses": {
                        "200": {
                            "description": "Verification completed",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/UnifiedResponse"}
                                }
                            }
                        }
                    }
                }
            }
        }
    
    def _get_gs_paths(self) -> Dict[str, Any]:
        """Get governance synthesis service paths."""
        return {
            "/api/v1/synthesis/generate": {
                "post": {
                    "tags": ["synthesis"],
                    "summary": "Generate Policy",
                    "description": "Generate governance policy from principles",
                    "responses": {
                        "200": {
                            "description": "Policy generated successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/UnifiedResponse"}
                                }
                            }
                        }
                    }
                }
            }
        }
    
    def _get_pgc_paths(self) -> Dict[str, Any]:
        """Get policy governance service paths."""
        return {
            "/api/v1/enforcement/policies": {
                "get": {
                    "tags": ["policies"],
                    "summary": "Get Policies",
                    "description": "Retrieve governance policies",
                    "responses": {
                        "200": {
                            "description": "Policies retrieved successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/UnifiedResponse"}
                                }
                            }
                        }
                    }
                }
            }
        }
    
    def _get_ec_paths(self) -> Dict[str, Any]:
        """Get evolutionary computation service paths."""
        return {
            "/api/v1/evolution/optimize": {
                "post": {
                    "tags": ["optimization"],
                    "summary": "Start Optimization",
                    "description": "Start evolutionary optimization process",
                    "responses": {
                        "200": {
                            "description": "Optimization started successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/UnifiedResponse"}
                                }
                            }
                        }
                    }
                }
            }
        }
    
    def _get_dgm_paths(self) -> Dict[str, Any]:
        """Get Darwin Gödel Machine service paths."""
        return {
            "/api/v1/dgm/workspace": {
                "get": {
                    "tags": ["workspace"],
                    "summary": "Get Workspace",
                    "description": "Get self-improvement workspace status",
                    "responses": {
                        "200": {
                            "description": "Workspace status retrieved successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/UnifiedResponse"}
                                }
                            }
                        }
                    }
                }
            }
        }
    
    def save_spec(self, service_key: str, spec: Dict[str, Any], formats: List[str] = ["json", "yaml"]):
        """Save OpenAPI specification in multiple formats."""
        
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
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{config['name']} API Documentation</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui.css" />
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui-bundle.js"></script>
    <script>
        window.onload = function() {{
            const ui = SwaggerUIBundle({{
                url: './{service_key}_openapi.json',
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [SwaggerUIBundle.presets.apis],
                layout: "StandaloneLayout"
            }});
        }};
    </script>
</body>
</html>"""
        
        html_path = self.output_dir / f"{service_key}_docs.html"
        with open(html_path, "w") as f:
            f.write(html_content)
        
        logger.info(f"Generated HTML docs: {html_path}")
    
    def generate_all_specs(self, formats: List[str] = ["json", "yaml", "html"]) -> Dict[str, Dict[str, Any]]:
        """Generate OpenAPI specifications for all services."""
        
        specs = {}
        
        for service_key in self.service_configs.keys():
            try:
                logger.info(f"Generating OpenAPI spec for {service_key}")
                spec = self.generate_service_spec(service_key)
                specs[service_key] = spec
                self.save_spec(service_key, spec, formats)
                logger.info(f"Successfully generated spec for {service_key}")
            except Exception as e:
                logger.error(f"Failed to generate spec for {service_key}: {e}")
                specs[service_key] = None
        
        return specs


def main():
    """Main function for CLI usage."""
    parser = argparse.ArgumentParser(description="Generate OpenAPI documentation for ACGS services")
    parser.add_argument("--service", help="Generate docs for specific service", 
                       choices=list(SimpleOpenAPIGenerator().service_configs.keys()) + ["all"])
    parser.add_argument("--output", default="docs/api/generated", help="Output directory")
    parser.add_argument("--format", nargs="+", default=["json", "yaml", "html"], 
                       choices=["json", "yaml", "html"], help="Output formats")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    generator = SimpleOpenAPIGenerator(args.output)
    
    if args.service == "all" or args.service is None:
        # Generate for all services
        logger.info("Generating OpenAPI specifications for all services")
        generator.generate_all_specs(args.format)
    else:
        # Generate for specific service
        logger.info(f"Generating OpenAPI specification for {args.service}")
        spec = generator.generate_service_spec(args.service)
        generator.save_spec(args.service, spec, args.format)
    
    logger.info("Documentation generation complete")


if __name__ == "__main__":
    main()
