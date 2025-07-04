#!/usr/bin/env python3
"""
ACGS-1 API Documentation Enhancement Framework

This script provides comprehensive API documentation enhancement including
interactive documentation generation, SDK creation, integration guides,
and developer experience optimization for the ACGS-1 Constitutional
Governance System.

Features:
- Interactive OpenAPI/Swagger documentation
- Multi-language SDK generation
- Comprehensive integration guides
- API testing and validation tools
- Developer onboarding automation
- Version management and deprecation
- Performance and security documentation
"""

import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import structlog
import yaml

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


logger = structlog.get_logger(__name__)


@dataclass
class APIEndpoint:
    """API endpoint definition."""

    path: str
    method: str
    summary: str
    description: str
    parameters: list[dict[str, Any]] = field(default_factory=list)
    request_body: dict[str, Any] | None = None
    responses: dict[str, dict[str, Any]] = field(default_factory=dict)
    security: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    examples: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class ServiceAPI:
    """Service API definition."""

    name: str
    version: str
    description: str
    base_url: str
    port: int
    endpoints: list[APIEndpoint] = field(default_factory=list)
    schemas: dict[str, Any] = field(default_factory=dict)
    security_schemes: dict[str, Any] = field(default_factory=dict)


class APIDocumentationEnhancer:
    """Comprehensive API documentation enhancement manager."""

    def __init__(self, project_root: Path):
        """Initialize API documentation enhancer."""
        self.project_root = project_root
        self.services: list[ServiceAPI] = []
        self.output_dir = project_root / "docs" / "api" / "enhanced"

        # Configuration
        self.config = {
            "openapi_version": "3.0.3",
            "generate_sdks": True,
            "supported_languages": ["python", "javascript", "go", "rust"],
            "interactive_docs": True,
            "generate_postman": True,
            "include_examples": True,
            "validate_schemas": True,
        }

        # Initialize ACGS services
        self._initialize_acgs_services()

    def _initialize_acgs_services(self):
        """Initialize ACGS service definitions."""
        acgs_services = [
            {
                "name": "Authentication Service",
                "version": "2.1.0",
                "description": "ACGS Authentication and Authorization Service",
                "base_url": "http://localhost",
                "port": 8000,
                "endpoints": [
                    {
                        "path": "/auth/login",
                        "method": "POST",
                        "summary": "User Authentication",
                        "description": "Authenticate user and return JWT token",
                        "request_body": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "username": {
                                                "type": "string",
                                                "example": "user@acgs.gov",
                                            },
                                            "password": {
                                                "type": "string",
                                                "example": "secure_password",
                                            },
                                        },
                                        "required": ["username", "password"],
                                    }
                                }
                            },
                        },
                        "responses": {
                            "200": {
                                "description": "Authentication successful",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "access_token": {"type": "string"},
                                                "token_type": {
                                                    "type": "string",
                                                    "example": "bearer",
                                                },
                                                "expires_in": {
                                                    "type": "integer",
                                                    "example": 3600,
                                                },
                                            },
                                        }
                                    }
                                },
                            },
                            "401": {
                                "description": "Authentication failed",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/Error"}
                                    }
                                },
                            },
                        },
                        "tags": ["authentication"],
                    },
                    {
                        "path": "/auth/me",
                        "method": "GET",
                        "summary": "Get Current User",
                        "description": "Get current authenticated user information",
                        "security": ["BearerAuth"],
                        "responses": {
                            "200": {
                                "description": "User information",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/User"}
                                    }
                                },
                            }
                        },
                        "tags": ["authentication", "users"],
                    },
                ],
            },
            {
                "name": "Constitutional AI Service",
                "version": "2.1.0",
                "description": "ACGS Constitutional AI Principles and Compliance Service",
                "base_url": "http://localhost",
                "port": 8001,
                "endpoints": [
                    {
                        "path": "/api/v1/constitutional/validate",
                        "method": "POST",
                        "summary": "Validate Constitutional Compliance",
                        "description": "Validate policy or action against constitutional principles",
                        "security": ["BearerAuth"],
                        "request_body": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "content": {
                                                "type": "string",
                                                "description": "Content to validate",
                                            },
                                            "context": {
                                                "type": "object",
                                                "description": "Validation context",
                                            },
                                            "strict_mode": {
                                                "type": "boolean",
                                                "default": False,
                                            },
                                        },
                                        "required": ["content"],
                                    }
                                }
                            },
                        },
                        "responses": {
                            "200": {
                                "description": "Validation result",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": "#/components/schemas/ValidationResult"
                                        }
                                    }
                                },
                            }
                        },
                        "tags": ["constitutional-ai", "validation"],
                    }
                ],
            },
        ]

        for service_data in acgs_services:
            endpoints = []
            for endpoint_data in service_data["endpoints"]:
                endpoint = APIEndpoint(
                    path=endpoint_data["path"],
                    method=endpoint_data["method"],
                    summary=endpoint_data["summary"],
                    description=endpoint_data["description"],
                    request_body=endpoint_data.get("request_body"),
                    responses=endpoint_data.get("responses", {}),
                    security=endpoint_data.get("security", []),
                    tags=endpoint_data.get("tags", []),
                )
                endpoints.append(endpoint)

            service = ServiceAPI(
                name=service_data["name"],
                version=service_data["version"],
                description=service_data["description"],
                base_url=service_data["base_url"],
                port=service_data["port"],
                endpoints=endpoints,
            )

            self.services.append(service)

    async def enhance_api_documentation(self) -> dict[str, Any]:
        """Enhance API documentation comprehensively."""
        logger.info("🚀 Starting comprehensive API documentation enhancement...")

        enhancement_start = time.time()

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Step 1: Generate OpenAPI specifications
        openapi_specs = await self._generate_openapi_specifications()

        # Step 2: Create interactive documentation
        interactive_docs = await self._create_interactive_documentation()

        # Step 3: Generate SDKs
        sdk_generation = await self._generate_sdks()

        # Step 4: Create integration guides
        integration_guides = await self._create_integration_guides()

        # Step 5: Generate API testing tools
        testing_tools = await self._generate_api_testing_tools()

        # Step 6: Create developer onboarding
        onboarding_materials = await self._create_developer_onboarding()

        # Step 7: Generate API reference
        api_reference = await self._generate_comprehensive_api_reference()

        enhancement_duration = time.time() - enhancement_start

        results = {
            "enhancement_id": f"api_docs_{int(time.time())}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "services_documented": len(self.services),
            "openapi_specs": openapi_specs,
            "interactive_docs": interactive_docs,
            "sdk_generation": sdk_generation,
            "integration_guides": integration_guides,
            "testing_tools": testing_tools,
            "onboarding_materials": onboarding_materials,
            "api_reference": api_reference,
            "enhancement_duration_seconds": round(enhancement_duration, 2),
        }

        # Save results
        await self._save_enhancement_results(results)

        logger.info(
            f"✅ API documentation enhancement completed in {enhancement_duration:.2f}s"
        )

        return results

    async def _generate_openapi_specifications(self) -> dict[str, Any]:
        """Generate comprehensive OpenAPI 3.0 specifications."""
        logger.info("📋 Generating OpenAPI specifications...")

        specs_generated = 0

        for service in self.services:
            # Generate OpenAPI spec for service
            spec = {
                "openapi": self.config["openapi_version"],
                "info": {
                    "title": service.name,
                    "version": service.version,
                    "description": service.description,
                    "contact": {
                        "name": "ACGS Development Team",
                        "email": "api-support@acgs.gov",
                        "url": "https://acgs.gov/support",
                    },
                    "license": {
                        "name": "ACGS License",
                        "url": "https://acgs.gov/license",
                    },
                },
                "servers": [
                    {
                        "url": f"{service.base_url}:{service.port}",
                        "description": "Development server",
                    },
                    {
                        "url": "https://api.acgs.gov",
                        "description": "Production server",
                    },
                ],
                "paths": {},
                "components": {
                    "schemas": self._get_common_schemas(),
                    "securitySchemes": {
                        "BearerAuth": {
                            "type": "http",
                            "scheme": "bearer",
                            "bearerFormat": "JWT",
                        }
                    },
                },
                "security": [{"BearerAuth": []}],
                "tags": self._get_service_tags(service),
            }

            # Add endpoints to spec
            for endpoint in service.endpoints:
                if endpoint.path not in spec["paths"]:
                    spec["paths"][endpoint.path] = {}

                spec["paths"][endpoint.path][endpoint.method.lower()] = {
                    "summary": endpoint.summary,
                    "description": endpoint.description,
                    "tags": endpoint.tags,
                    "responses": endpoint.responses,
                }

                if endpoint.request_body:
                    spec["paths"][endpoint.path][endpoint.method.lower()][
                        "requestBody"
                    ] = endpoint.request_body

                if endpoint.security:
                    spec["paths"][endpoint.path][endpoint.method.lower()][
                        "security"
                    ] = [{scheme: []} for scheme in endpoint.security]

            # Save OpenAPI spec
            spec_file = (
                self.output_dir
                / f"{service.name.lower().replace(' ', '_')}_openapi.yaml"
            )
            with open(spec_file, "w") as f:
                yaml.dump(spec, f, default_flow_style=False, sort_keys=False)

            specs_generated += 1
            logger.info(f"Generated OpenAPI spec: {spec_file}")

        return {
            "specs_generated": specs_generated,
            "output_directory": str(self.output_dir),
        }

    async def _create_interactive_documentation(self) -> dict[str, Any]:
        """Create interactive API documentation."""
        logger.info("🌐 Creating interactive documentation...")

        # Generate Swagger UI HTML
        swagger_html = self._generate_swagger_ui_html()

        # Generate Redoc HTML
        redoc_html = self._generate_redoc_html()

        # Save interactive docs
        swagger_file = self.output_dir / "swagger-ui.html"
        with open(swagger_file, "w") as f:
            f.write(swagger_html)

        redoc_file = self.output_dir / "redoc.html"
        with open(redoc_file, "w") as f:
            f.write(redoc_html)

        return {
            "swagger_ui": str(swagger_file),
            "redoc": str(redoc_file),
            "interactive_docs_created": 2,
        }

    async def _generate_sdks(self) -> dict[str, Any]:
        """Generate SDKs for supported languages."""
        logger.info("🛠️ Generating SDKs...")

        if not self.config["generate_sdks"]:
            return {"sdks_generated": 0, "message": "SDK generation disabled"}

        sdks_generated = {}

        for language in self.config["supported_languages"]:
            sdk_dir = self.output_dir / "sdks" / language
            sdk_dir.mkdir(parents=True, exist_ok=True)

            if language == "python":
                sdk_content = self._generate_python_sdk()
                sdk_file = sdk_dir / "acgs_client.py"
                with open(sdk_file, "w") as f:
                    f.write(sdk_content)
                sdks_generated[language] = str(sdk_file)

            elif language == "javascript":
                sdk_content = self._generate_javascript_sdk()
                sdk_file = sdk_dir / "acgs-client.js"
                with open(sdk_file, "w") as f:
                    f.write(sdk_content)
                sdks_generated[language] = str(sdk_file)

        return {
            "sdks_generated": len(sdks_generated),
            "languages": list(sdks_generated.keys()),
            "sdk_files": sdks_generated,
        }

    async def _create_integration_guides(self) -> dict[str, Any]:
        """Create comprehensive integration guides."""
        logger.info("📚 Creating integration guides...")

        guides_created = []

        # Quick start guide
        quick_start = self._generate_quick_start_guide()
        quick_start_file = self.output_dir / "quick-start-guide.md"
        with open(quick_start_file, "w") as f:
            f.write(quick_start)
        guides_created.append(str(quick_start_file))

        # Authentication guide
        auth_guide = self._generate_authentication_guide()
        auth_guide_file = self.output_dir / "authentication-guide.md"
        with open(auth_guide_file, "w") as f:
            f.write(auth_guide)
        guides_created.append(str(auth_guide_file))

        # Error handling guide
        error_guide = self._generate_error_handling_guide()
        error_guide_file = self.output_dir / "error-handling-guide.md"
        with open(error_guide_file, "w") as f:
            f.write(error_guide)
        guides_created.append(str(error_guide_file))

        return {"guides_created": len(guides_created), "guide_files": guides_created}

    async def _generate_api_testing_tools(self) -> dict[str, Any]:
        """Generate API testing tools."""
        logger.info("🧪 Generating API testing tools...")

        # Generate Postman collection
        postman_collection = self._generate_postman_collection()
        postman_file = self.output_dir / "acgs-api.postman_collection.json"
        with open(postman_file, "w") as f:
            json.dump(postman_collection, f, indent=2)

        # Generate test scripts
        test_scripts = self._generate_test_scripts()
        test_dir = self.output_dir / "tests"
        test_dir.mkdir(exist_ok=True)

        test_files = []
        for script_name, script_content in test_scripts.items():
            test_file = test_dir / f"{script_name}.py"
            with open(test_file, "w") as f:
                f.write(script_content)
            test_files.append(str(test_file))

        return {
            "postman_collection": str(postman_file),
            "test_scripts": len(test_files),
            "test_files": test_files,
        }

    async def _create_developer_onboarding(self) -> dict[str, Any]:
        """Create developer onboarding materials."""
        logger.info("👨‍💻 Creating developer onboarding materials...")

        # Generate developer guide
        dev_guide = self._generate_developer_guide()
        dev_guide_file = self.output_dir / "developer-guide.md"
        with open(dev_guide_file, "w") as f:
            f.write(dev_guide)

        # Generate setup script
        setup_script = self._generate_setup_script()
        setup_file = self.output_dir / "setup.sh"
        with open(setup_file, "w") as f:
            f.write(setup_script)
        setup_file.chmod(0o755)

        return {
            "developer_guide": str(dev_guide_file),
            "setup_script": str(setup_file),
            "onboarding_materials": 2,
        }

    async def _generate_comprehensive_api_reference(self) -> dict[str, Any]:
        """Generate comprehensive API reference."""
        logger.info("📖 Generating comprehensive API reference...")

        # Generate master API reference
        api_ref = self._generate_master_api_reference()
        api_ref_file = self.output_dir / "api-reference.md"
        with open(api_ref_file, "w") as f:
            f.write(api_ref)

        return {
            "api_reference": str(api_ref_file),
            "services_documented": len(self.services),
        }

    def _get_common_schemas(self) -> dict[str, Any]:
        """Get common API schemas."""
        return {
            "Error": {
                "type": "object",
                "properties": {
                    "error": {"type": "string"},
                    "message": {"type": "string"},
                    "code": {"type": "integer"},
                    "timestamp": {"type": "string", "format": "date-time"},
                },
                "required": ["error", "message"],
            },
            "User": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "username": {"type": "string"},
                    "email": {"type": "string", "format": "email"},
                    "role": {"type": "string"},
                    "created_at": {"type": "string", "format": "date-time"},
                },
            },
            "ValidationResult": {
                "type": "object",
                "properties": {
                    "is_valid": {"type": "boolean"},
                    "score": {"type": "number", "minimum": 0, "maximum": 1},
                    "violations": {"type": "array", "items": {"type": "string"}},
                    "recommendations": {"type": "array", "items": {"type": "string"}},
                },
            },
        }

    def _get_service_tags(self, service: ServiceAPI) -> list[dict[str, str]]:
        """Get tags for a service."""
        all_tags = set()
        for endpoint in service.endpoints:
            all_tags.update(endpoint.tags)

        return [
            {"name": tag, "description": f"{tag.title()} operations"}
            for tag in sorted(all_tags)
        ]

    def _generate_swagger_ui_html(self) -> str:
        """Generate Swagger UI HTML."""
        return """<!DOCTYPE html>
<html>
<head>
    <title>ACGS-1 API Documentation</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@3.52.5/swagger-ui.css" />
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@3.52.5/swagger-ui-bundle.js"></script>
    <script>
        SwaggerUIBundle({
            url: './authentication_service_openapi.yaml',
            dom_id: '#swagger-ui',
            presets: [
                SwaggerUIBundle.presets.apis,
                SwaggerUIBundle.presets.standalone
            ]
        });
    </script>
</body>
</html>"""

    def _generate_redoc_html(self) -> str:
        """Generate Redoc HTML."""
        return """<!DOCTYPE html>
<html>
<head>
    <title>ACGS-1 API Documentation</title>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
    <style>
        body { margin: 0; padding: 0; }
    </style>
</head>
<body>
    <redoc spec-url='./authentication_service_openapi.yaml'></redoc>
    <script src="https://cdn.jsdelivr.net/npm/redoc@2.0.0/bundles/redoc.standalone.js"></script>
</body>
</html>"""
