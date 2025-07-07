"""
ACGS-2 Constitutional OpenAPI Documentation Generator
Generates comprehensive API documentation with constitutional compliance tags.

Constitutional Hash: cdd01ef066bc6cf2
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


class ConstitutionalOpenAPIGenerator:
    """
    Enhanced OpenAPI generator with constitutional compliance metadata.
    """

    def __init__(self, output_dir: str = "docs/api/constitutional"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Service configurations with constitutional context
        self.service_configs = {
            "constitutional-core": {
                "name": "Constitutional Core Service",
                "description": "Unified Constitutional AI & Formal Verification Service",
                "version": "2.1.0",
                "port": 8001,
                "constitutional_level": "critical",
                "tags": [
                    "constitutional-ai",
                    "formal-verification",
                    "constitutional-compliance",
                    "constitutional-validation",
                ],
            },
            "integrity": {
                "name": "Integrity Service",
                "description": "Data Integrity and Cryptographic Verification Service",
                "version": "2.0.0",
                "port": 8002,
                "constitutional_level": "high",
                "tags": ["integrity", "cryptography", "audit", "constitutional-audit"],
            },
            "governance-engine": {
                "name": "Governance Engine",
                "description": "Unified Governance Synthesis & Policy Compliance Service",
                "version": "2.1.0",
                "port": 8004,
                "constitutional_level": "critical",
                "tags": [
                    "governance",
                    "policy",
                    "synthesis",
                    "constitutional-governance",
                ],
            },
            "api-gateway": {
                "name": "API Gateway",
                "description": "Enhanced API Gateway with Integrated Authentication",
                "version": "2.0.0",
                "port": 8080,
                "constitutional_level": "high",
                "tags": [
                    "gateway",
                    "authentication",
                    "routing",
                    "constitutional-routing",
                ],
            },
        }

    def generate_constitutional_openapi_spec(
        self, service_key: str, include_examples: bool = True
    ) -> Dict[str, Any]:
        """Generate OpenAPI spec with constitutional compliance metadata."""

        config = self.service_configs.get(service_key)
        if not config:
            raise ValueError(f"Unknown service: {service_key}")

        # Base OpenAPI specification
        spec = {
            "openapi": "3.0.3",
            "info": {
                "title": config["name"],
                "description": f"{config['description']}\n\n**Constitutional Hash:** `{CONSTITUTIONAL_HASH}`",
                "version": config["version"],
                "contact": {
                    "name": "ACGS Development Team",
                    "url": "https://acgs.dev/support",
                    "email": "api-support@acgs.dev",
                },
                "license": {
                    "name": "ACGS Constitutional License",
                    "url": "https://acgs.dev/license",
                },
                "x-constitutional-hash": CONSTITUTIONAL_HASH,
                "x-constitutional-level": config["constitutional_level"],
                "x-service-port": config["port"],
            },
            "servers": [
                {
                    "url": f"http://localhost:{config['port']}",
                    "description": "Development server",
                    "x-constitutional-compliance": True,
                },
                {
                    "url": f"https://api.acgs.dev/{service_key}",
                    "description": "Development environment",
                    "x-constitutional-compliance": True,
                },
                {
                    "url": f"https://api.acgs.com/{service_key}",
                    "description": "Production environment",
                    "x-constitutional-compliance": True,
                },
            ],
            "paths": {},
            "components": {
                "schemas": self._get_constitutional_schemas(),
                "securitySchemes": {
                    "ConstitutionalAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT",
                        "description": "JWT token with constitutional compliance validation",
                        "x-constitutional-required": True,
                    },
                    "ConstitutionalApiKey": {
                        "type": "apiKey",
                        "in": "header",
                        "name": "X-Constitutional-API-Key",
                        "description": "API key with constitutional hash validation",
                        "x-constitutional-hash": CONSTITUTIONAL_HASH,
                    },
                },
            },
            "security": [{"ConstitutionalAuth": []}, {"ConstitutionalApiKey": []}],
            "tags": self._get_constitutional_tags(config),
            "x-constitutional-metadata": {
                "hash": CONSTITUTIONAL_HASH,
                "compliance_level": config["constitutional_level"],
                "generated_at": datetime.utcnow().isoformat(),
                "service_port": config["port"],
            },
        }

        # Add service-specific paths
        spec["paths"] = self._generate_constitutional_paths(service_key, config)

        return spec

    def _get_constitutional_schemas(self) -> Dict[str, Any]:
        """Get constitutional compliance schemas."""
        return {
            "ConstitutionalResponse": {
                "type": "object",
                "properties": {
                    "success": {
                        "type": "boolean",
                        "description": "Operation success status",
                    },
                    "data": {"description": "Response data"},
                    "message": {
                        "type": "string",
                        "description": "Human-readable message",
                    },
                    "constitutional_metadata": {
                        "$ref": "#/components/schemas/ConstitutionalMetadata"
                    },
                },
                "required": ["success", "constitutional_metadata"],
            },
            "ConstitutionalMetadata": {
                "type": "object",
                "properties": {
                    "constitutional_hash": {
                        "type": "string",
                        "pattern": "^[a-f0-9]{16}$",
                        "example": CONSTITUTIONAL_HASH,
                        "description": "Constitutional compliance hash",
                    },
                    "compliance_validated": {
                        "type": "boolean",
                        "description": "Whether constitutional compliance was validated",
                    },
                    "validation_timestamp": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Timestamp of constitutional validation",
                    },
                    "service_port": {
                        "type": "integer",
                        "description": "Service port for infrastructure validation",
                    },
                    "request_id": {
                        "type": "string",
                        "format": "uuid",
                        "description": "Request correlation ID",
                    },
                },
                "required": [
                    "constitutional_hash",
                    "compliance_validated",
                    "service_port",
                ],
            },
            "ConstitutionalError": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "enum": [False]},
                    "error": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string", "description": "Error code"},
                            "message": {
                                "type": "string",
                                "description": "Error message",
                            },
                            "constitutional_violation": {
                                "type": "boolean",
                                "description": "Whether this error represents a constitutional violation",
                            },
                        },
                    },
                    "constitutional_metadata": {
                        "$ref": "#/components/schemas/ConstitutionalMetadata"
                    },
                },
                "required": ["success", "error", "constitutional_metadata"],
            },
            "HealthCheck": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["healthy", "unhealthy", "degraded"],
                    },
                    "service": {"type": "string", "description": "Service name"},
                    "version": {"type": "string", "description": "Service version"},
                    "constitutional_hash": {
                        "type": "string",
                        "example": CONSTITUTIONAL_HASH,
                        "description": "Constitutional compliance hash",
                    },
                    "constitutional_compliance": {
                        "type": "string",
                        "enum": ["active", "inactive", "degraded"],
                        "description": "Constitutional compliance status",
                    },
                    "infrastructure_port": {
                        "type": "integer",
                        "description": "Service infrastructure port",
                    },
                    "timestamp": {"type": "string", "format": "date-time"},
                },
                "required": [
                    "status",
                    "constitutional_hash",
                    "constitutional_compliance",
                    "infrastructure_port",
                ],
            },
        }

    def _get_constitutional_tags(self, config: Dict[str, Any]) -> List[Dict[str, str]]:
        """Get constitutional tags for service."""
        tags = []

        # Constitutional compliance tags
        constitutional_tags = {
            "constitutional-compliance": "Constitutional compliance validation and enforcement",
            "constitutional-validation": "Constitutional hash and policy validation",
            "constitutional-governance": "Constitutional governance operations",
            "constitutional-audit": "Constitutional audit and logging",
            "constitutional-routing": "Constitutional-aware request routing",
        }

        # Service-specific tags
        service_tags = {
            "health": "Service health checks with constitutional validation",
            "authentication": "Authentication with constitutional compliance",
            "authorization": "Authorization with constitutional governance",
            "governance": "Governance policy management",
            "integrity": "Data integrity and cryptographic operations",
            "audit": "Audit logging and compliance tracking",
        }

        # Combine all tags
        all_tags = {**constitutional_tags, **service_tags}

        for tag in config["tags"]:
            if tag in all_tags:
                tags.append(
                    {
                        "name": tag,
                        "description": all_tags[tag],
                        "x-constitutional-level": config["constitutional_level"],
                    }
                )

        return tags

    def _generate_constitutional_paths(
        self, service_key: str, config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate constitutional API paths for service."""

        paths = {}

        # Health endpoint (all services)
        paths["/health"] = {
            "get": {
                "tags": ["health"],
                "summary": "Health Check with Constitutional Validation",
                "description": f"Check service health with constitutional compliance validation\n\n**Infrastructure Port:** {config['port']}",
                "operationId": f"healthCheck{service_key.title().replace('-', '')}",
                "responses": {
                    "200": {
                        "description": "Service is healthy with constitutional compliance active",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/HealthCheck"},
                                "example": {
                                    "status": "healthy",
                                    "service": config["name"],
                                    "version": config["version"],
                                    "constitutional_hash": CONSTITUTIONAL_HASH,
                                    "constitutional_compliance": "active",
                                    "infrastructure_port": config["port"],
                                    "timestamp": "2025-01-08T10:30:00Z",
                                },
                            }
                        },
                    },
                    "503": {
                        "description": "Service unavailable or constitutional compliance issues",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ConstitutionalError"
                                }
                            }
                        },
                    },
                },
                "x-constitutional-required": True,
                "x-infrastructure-port": config["port"],
            }
        }

        # Constitutional validation endpoint
        paths["/health/constitutional"] = {
            "get": {
                "tags": ["constitutional-compliance"],
                "summary": "Constitutional Compliance Check",
                "description": f"Detailed constitutional compliance validation\n\n**Constitutional Hash:** {CONSTITUTIONAL_HASH}\n**Infrastructure Port:** {config['port']}",
                "operationId": f"constitutionalCheck{service_key.title().replace('-', '')}",
                "responses": {
                    "200": {
                        "description": "Constitutional compliance status",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ConstitutionalResponse"
                                },
                                "example": {
                                    "success": True,
                                    "data": {
                                        "constitutional_hash": CONSTITUTIONAL_HASH,
                                        "compliance_status": "active",
                                        "last_validation": "2025-01-08T10:30:00Z",
                                        "compliance_score": 1.0,
                                    },
                                    "message": "Constitutional compliance active",
                                    "constitutional_metadata": {
                                        "constitutional_hash": CONSTITUTIONAL_HASH,
                                        "compliance_validated": True,
                                        "validation_timestamp": "2025-01-08T10:30:00Z",
                                        "service_port": config["port"],
                                        "request_id": "550e8400-e29b-41d4-a716-446655440000",
                                    },
                                },
                            }
                        },
                    }
                },
                "x-constitutional-hash": CONSTITUTIONAL_HASH,
                "x-infrastructure-port": config["port"],
            }
        }

        # Service-specific endpoints
        if service_key == "constitutional-core":
            paths.update(self._get_constitutional_core_paths())
        elif service_key == "integrity":
            paths.update(self._get_integrity_paths(config))
        elif service_key == "governance-engine":
            paths.update(self._get_governance_paths(config))
        elif service_key == "api-gateway":
            paths.update(self._get_gateway_paths(config))

        return paths

    def _get_constitutional_core_paths(self) -> Dict[str, Any]:
        """Get constitutional core service paths."""
        return {
            "/api/v1/constitutional/validate": {
                "post": {
                    "tags": ["constitutional-validation"],
                    "summary": "Validate Constitutional Compliance",
                    "description": f"Validate policy or operation against constitutional requirements\n\n**Constitutional Hash:** {CONSTITUTIONAL_HASH}",
                    "operationId": "validateConstitutionalCompliance",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "policy": {"type": "object"},
                                        "validation_mode": {
                                            "type": "string",
                                            "enum": [
                                                "basic",
                                                "comprehensive",
                                                "critical",
                                            ],
                                        },
                                        "constitutional_hash": {
                                            "type": "string",
                                            "example": CONSTITUTIONAL_HASH,
                                        },
                                    },
                                    "required": ["policy", "constitutional_hash"],
                                }
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Validation results",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ConstitutionalResponse"
                                    }
                                }
                            },
                        }
                    },
                    "x-constitutional-hash": CONSTITUTIONAL_HASH,
                }
            }
        }

    def _get_integrity_paths(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get integrity service paths."""
        return {
            "/api/v1/integrity/audit": {
                "get": {
                    "tags": ["constitutional-audit"],
                    "summary": "Get Constitutional Audit Log",
                    "description": f"Retrieve constitutional compliance audit entries\n\n**Infrastructure Port:** {config['port']}",
                    "operationId": "getConstitutionalAuditLog",
                    "responses": {
                        "200": {
                            "description": "Audit log entries with constitutional metadata",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ConstitutionalResponse"
                                    }
                                }
                            },
                        }
                    },
                    "x-infrastructure-port": config["port"],
                }
            }
        }

    def _get_governance_paths(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get governance engine paths."""
        return {
            "/api/v1/governance/policies": {
                "get": {
                    "tags": ["constitutional-governance"],
                    "summary": "Get Constitutional Policies",
                    "description": f"Retrieve constitutional governance policies\n\n**Infrastructure Port:** {config['port']}",
                    "operationId": "getConstitutionalPolicies",
                    "responses": {
                        "200": {
                            "description": "Constitutional policies",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ConstitutionalResponse"
                                    }
                                }
                            },
                        }
                    },
                    "x-infrastructure-port": config["port"],
                }
            }
        }

    def _get_gateway_paths(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get API gateway paths."""
        return {
            "/gateway/routes": {
                "get": {
                    "tags": ["constitutional-routing"],
                    "summary": "Get Constitutional Routes",
                    "description": f"Get available routes with constitutional compliance info\n\n**Infrastructure Port:** {config['port']}",
                    "operationId": "getConstitutionalRoutes",
                    "responses": {
                        "200": {
                            "description": "Available routes with constitutional metadata",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ConstitutionalResponse"
                                    }
                                }
                            },
                        }
                    },
                    "x-infrastructure-port": config["port"],
                }
            }
        }

    def generate_swagger_docs(self, service_key: str, spec: Dict[str, Any]) -> str:
        """Generate Swagger UI HTML with constitutional styling."""

        config = self.service_configs[service_key]

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{config["name"]} - Constitutional API Documentation</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui.css" />
    <style>
        body {{
            margin: 0;
            background: #fafafa;
        }}
        .swagger-ui .topbar {{
            background-color: #1f2937;
            padding: 10px;
        }}
        .swagger-ui .topbar::before {{
            content: "🏛️ Constitutional Hash: {CONSTITUTIONAL_HASH} | Port: {config['port']}";
            color: #3b82f6;
            font-weight: bold;
            margin-right: 20px;
        }}
        .swagger-ui .info .title {{
            color: #1f2937;
        }}
        .swagger-ui .info .description {{
            margin: 15px 0;
        }}
        .constitutional-tag {{
            background-color: #3b82f6 !important;
            color: white !important;
        }}
        .swagger-ui .opblock.opblock-get .opblock-summary-method {{
            background: #3b82f6;
        }}
        .swagger-ui .opblock.opblock-post .opblock-summary-method {{
            background: #059669;
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
                url: './{service_key}_constitutional_openapi.json',
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
                    // Add constitutional headers
                    request.headers['X-Constitutional-Hash'] = '{CONSTITUTIONAL_HASH}';
                    request.headers['X-Infrastructure-Port'] = '{config["port"]}';
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
</html>"""

        return html_content

    def save_constitutional_docs(
        self, service_key: str, formats: List[str] = ["json", "yaml", "html"]
    ) -> Dict[str, str]:
        """Save constitutional documentation in multiple formats."""

        spec = self.generate_constitutional_openapi_spec(service_key)
        saved_files = {}

        base_filename = f"{service_key}_constitutional_openapi"

        # Save JSON format
        if "json" in formats:
            json_path = self.output_dir / f"{base_filename}.json"
            with open(json_path, "w") as f:
                json.dump(spec, f, indent=2)
            saved_files["json"] = str(json_path)
            logger.info(f"Saved constitutional JSON spec: {json_path}")

        # Save YAML format
        if "yaml" in formats:
            yaml_path = self.output_dir / f"{base_filename}.yaml"
            with open(yaml_path, "w") as f:
                yaml.dump(spec, f, default_flow_style=False, sort_keys=False)
            saved_files["yaml"] = str(yaml_path)
            logger.info(f"Saved constitutional YAML spec: {yaml_path}")

        # Save HTML documentation
        if "html" in formats:
            html_content = self.generate_swagger_docs(service_key, spec)
            html_path = self.output_dir / f"{service_key}_constitutional_docs.html"
            with open(html_path, "w") as f:
                f.write(html_content)
            saved_files["html"] = str(html_path)
            logger.info(f"Saved constitutional HTML docs: {html_path}")

        return saved_files

    def generate_all_constitutional_docs(
        self, formats: List[str] = ["json", "yaml", "html"]
    ) -> Dict[str, Dict[str, str]]:
        """Generate constitutional documentation for all services."""

        all_docs = {}

        for service_key in self.service_configs.keys():
            try:
                logger.info(f"Generating constitutional docs for {service_key}")
                docs = self.save_constitutional_docs(service_key, formats)
                all_docs[service_key] = docs
                logger.info(
                    f"Successfully generated constitutional docs for {service_key}"
                )
            except Exception as e:
                logger.error(
                    f"Failed to generate constitutional docs for {service_key}: {e}"
                )
                all_docs[service_key] = {}

        return all_docs
