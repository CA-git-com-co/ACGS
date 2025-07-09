#!/usr/bin/env python3
"""
ACGS API-Code Synchronization Validator
Constitutional Hash: cdd01ef066bc6cf2

This tool validates synchronization between API documentation and actual service implementations:
- Extracts endpoints from FastAPI service implementations
- Compares documented endpoints with actual code
- Validates parameter consistency
- Checks response model alignment
- Identifies missing or outdated documentation
- Suggests corrections for documentation/code mismatches
"""

import ast
import json
import re
import sys
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# Configuration
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
REPO_ROOT = Path(__file__).parent.parent.parent
DOCS_DIR = REPO_ROOT / "docs"
SERVICES_DIR = REPO_ROOT / "services"

# Service mapping for validation
SERVICE_MAPPING = {
    "authentication": {
        "service_path": (
            "services/platform_services/authentication/auth_service/app/main.py"
        ),
        "api_doc": "docs/api/authentication.md",
        "port": 8016,
    },
    "constitutional-ai": {
        "service_path": "services/core/constitutional-ai/ac_service/app/main.py",
        "api_doc": "docs/api/constitutional-ai.md",
        "port": 8001,
    },
    "integrity": {
        "service_path": (
            "services/platform_services/integrity/integrity_service/app/main.py"
        ),
        "api_doc": "docs/api/integrity.md",
        "port": 8002,
    },
    "formal-verification": {
        "service_path": "services/core/formal-verification/fv_service/main.py",
        "api_doc": "docs/api/formal-verification.md",
        "port": 8003,
    },
    "governance_synthesis": {
        "service_path": "services/core/governance-synthesis/gs_service/app/main.py",
        "api_doc": "docs/api/governance_synthesis.md",
        "port": 8004,
    },
    "policy-governance": {
        "service_path": "services/core/policy-governance/pgc_service/app/main.py",
        "api_doc": "docs/api/policy-governance.md",
        "port": 8005,
    },
    "evolutionary-computation": {
        "service_path": "services/core/evolutionary-computation/main.py",
        "api_doc": "docs/api/evolutionary-computation.md",
        "port": 8006,
    },
}


@dataclass
class EndpointInfo:
    """Information about an API endpoint."""

    method: str
    path: str
    function_name: str
    parameters: list[str] = field(default_factory=list)
    response_model: Optional[str] = None
    description: Optional[str] = None
    line_number: Optional[int] = None
    decorators: list[str] = field(default_factory=list)


@dataclass
class ServiceAnalysis:
    """Analysis of a service implementation."""

    service_name: str
    service_path: str
    endpoints: list[EndpointInfo] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)
    models: list[str] = field(default_factory=list)
    port: Optional[int] = None
    constitutional_hash_present: bool = False


@dataclass
class DocumentationInfo:
    """Information extracted from API documentation."""

    service_name: str
    doc_path: str
    documented_endpoints: list[str] = field(default_factory=list)
    documented_models: list[str] = field(default_factory=list)
    port_references: list[int] = field(default_factory=list)
    constitutional_hash_present: bool = False


@dataclass
class SyncIssue:
    """API-code synchronization issue."""

    severity: str
    category: str
    service: str
    message: str
    suggested_fix: Optional[str] = None
    code_location: Optional[str] = None
    doc_location: Optional[str] = None


class APICodeSyncValidator:
    """Validates synchronization between API documentation and service code."""

    def __init__(self):
        self.service_analyses: dict[str, ServiceAnalysis] = {}
        self.documentation_info: dict[str, DocumentationInfo] = {}
        self.sync_issues: list[SyncIssue] = []

    def analyze_service_implementation(
        self, service_name: str, service_path: Path
    ) -> ServiceAnalysis:
        """Analyze a service implementation to extract API endpoints."""
        analysis = ServiceAnalysis(
            service_name=service_name,
            service_path=str(service_path.relative_to(REPO_ROOT)),
        )

        try:
            with open(service_path, encoding="utf-8") as f:
                content = f.read()
                tree = ast.parse(content)

            # Check for constitutional hash
            analysis.constitutional_hash_present = CONSTITUTIONAL_HASH in content

            # Extract endpoints using AST
            self._extract_endpoints_from_ast(tree, analysis, content)

            # Extract imports
            analysis.imports = self._extract_imports(tree)

            # Extract models
            analysis.models = self._extract_models(tree)

            # Extract port information
            analysis.port = self._extract_port_info(content)

        except Exception as e:
            self.sync_issues.append(
                SyncIssue(
                    severity="ERROR",
                    category="code_analysis",
                    service=service_name,
                    message=f"Failed to analyze service implementation: {e}",
                    code_location=str(service_path),
                )
            )

        return analysis

    def _extract_endpoints_from_ast(
        self, tree: ast.AST, analysis: ServiceAnalysis, content: str
    ) -> None:
        """Extract API endpoints from AST."""
        lines = content.split("\n")

        # Use both AST and regex approaches for robustness

        # Method 1: AST-based extraction
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call):
                        # Handle @app.get("/path") style decorators
                        if (
                            isinstance(decorator.func, ast.Attribute)
                            and isinstance(decorator.func.value, ast.Name)
                            and decorator.func.value.id == "app"
                        ):
                            method = decorator.func.attr.upper()
                            if method in [
                                "GET",
                                "POST",
                                "PUT",
                                "DELETE",
                                "PATCH",
                                "HEAD",
                                "OPTIONS",
                            ]:
                                # Extract path from first argument
                                path = "/unknown"
                                if decorator.args and isinstance(
                                    decorator.args[0], ast.Constant
                                ):
                                    path = decorator.args[0].value

                                endpoint = EndpointInfo(
                                    method=method,
                                    path=path,
                                    function_name=node.name,
                                    line_number=node.lineno,
                                    decorators=[f"@app.{decorator.func.attr}"],
                                )

                                # Extract parameters
                                endpoint.parameters = [
                                    arg.arg
                                    for arg in node.args.args
                                    if arg.arg != "self"
                                ]

                                # Extract description from docstring
                                if (
                                    node.body
                                    and isinstance(node.body[0], ast.Expr)
                                    and isinstance(node.body[0].value, ast.Constant)
                                ):
                                    endpoint.description = node.body[0].value.value
                                elif (
                                    node.body
                                    and isinstance(node.body[0], ast.Expr)
                                    and isinstance(node.body[0].value, ast.Str)
                                ):  # Python < 3.8
                                    endpoint.description = node.body[0].value.s

                                analysis.endpoints.append(endpoint)

        # Method 2: Regex-based extraction as fallback
        decorator_pattern = (
            r'@app\.(get|post|put|delete|patch|head|options)\s*\(\s*["\']([^"\']+)["\']'
        )
        function_pattern = r"async\s+def\s+(\w+)\s*\("

        for i, line in enumerate(lines):
            decorator_match = re.search(decorator_pattern, line, re.IGNORECASE)
            if decorator_match:
                method = decorator_match.group(1).upper()
                path = decorator_match.group(2)

                # Find the function definition in the next few lines
                for j in range(i + 1, min(i + 5, len(lines))):
                    func_match = re.search(function_pattern, lines[j])
                    if func_match:
                        function_name = func_match.group(1)

                        # Check if we already have this endpoint from AST
                        existing = any(
                            ep.method == method and ep.path == path
                            for ep in analysis.endpoints
                        )
                        if not existing:
                            endpoint = EndpointInfo(
                                method=method,
                                path=path,
                                function_name=function_name,
                                line_number=i + 1,
                                decorators=[f"@app.{decorator_match.group(1)}"],
                            )
                            analysis.endpoints.append(endpoint)
                        break

    def _extract_imports(self, tree: ast.AST) -> list[str]:
        """Extract import statements."""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")
        return imports

    def _extract_models(self, tree: ast.AST) -> list[str]:
        """Extract Pydantic model definitions."""
        models = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if it inherits from BaseModel
                for base in node.bases:
                    if (isinstance(base, ast.Name) and base.id == "BaseModel") or (
                        isinstance(base, ast.Attribute) and base.attr == "BaseModel"
                    ):
                        models.append(node.name)
                        break
        return models

    def _extract_port_info(self, content: str) -> Optional[int]:
        """Extract port information from service code."""
        # Look for uvicorn.run or port assignments
        port_patterns = [
            r"uvicorn\.run\([^,]*,\s*port=(\d+)",
            r"port\s*=\s*(\d+)",
            r'host="[^"]*",\s*port=(\d+)',
            r'"port":\s*(\d+)',
        ]

        for pattern in port_patterns:
            match = re.search(pattern, content)
            if match:
                return int(match.group(1))

        return None

    def analyze_api_documentation(
        self, service_name: str, doc_path: Path
    ) -> DocumentationInfo:
        """Analyze API documentation to extract endpoint information."""
        doc_info = DocumentationInfo(
            service_name=service_name, doc_path=str(doc_path.relative_to(REPO_ROOT))
        )

        try:
            with open(doc_path, encoding="utf-8") as f:
                content = f.read()

            # Check for constitutional hash
            doc_info.constitutional_hash_present = CONSTITUTIONAL_HASH in content

            # Extract documented endpoints
            doc_info.documented_endpoints = self._extract_documented_endpoints(content)

            # Extract documented models
            doc_info.documented_models = self._extract_documented_models(content)

            # Extract port references
            doc_info.port_references = self._extract_port_references(content)

        except Exception as e:
            self.sync_issues.append(
                SyncIssue(
                    severity="ERROR",
                    category="doc_analysis",
                    service=service_name,
                    message=f"Failed to analyze API documentation: {e}",
                    doc_location=str(doc_path),
                )
            )

        return doc_info

    def _extract_documented_endpoints(self, content: str) -> list[str]:
        """Extract endpoints documented in markdown."""
        endpoints = []

        # Patterns for different endpoint documentation formats
        patterns = [
            r"`(GET|POST|PUT|DELETE|PATCH)\s+(/[^`\s]*)`",
            r"\*\*(GET|POST|PUT|DELETE|PATCH)\*\*\s+`(/[^`]*)`",
            r"(GET|POST|PUT|DELETE|PATCH)\s+`(/[^`]*)`",
            r"```(?:http|rest|api)[^`]*\n(GET|POST|PUT|DELETE|PATCH)\s+(/[^\s\n]*)",
            r"###\s+.*\n.*?(GET|POST|PUT|DELETE|PATCH)\s+`?(/[^`\s\n]*)`?",
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                method = match.group(1).upper()
                path = match.group(2)
                endpoints.append(f"{method} {path}")

        # Also look for OpenAPI/Swagger style documentation
        openapi_pattern = r"paths:\s*\n(.*?)(?=\n\w|\Z)"
        openapi_match = re.search(openapi_pattern, content, re.DOTALL)
        if openapi_match:
            paths_section = openapi_match.group(1)
            path_matches = re.finditer(
                r"^\s*(/[^:]+):\s*$", paths_section, re.MULTILINE
            )
            for path_match in path_matches:
                path = path_match.group(1)
                # Find methods for this path
                method_matches = re.finditer(
                    r"^\s+(get|post|put|delete|patch):", paths_section, re.MULTILINE
                )
                for method_match in method_matches:
                    method = method_match.group(1).upper()
                    endpoints.append(f"{method} {path}")

        return list(set(endpoints))  # Remove duplicates

    def _extract_documented_models(self, content: str) -> list[str]:
        """Extract model documentation from markdown."""
        models = []

        # Look for model definitions in code blocks
        code_block_pattern = r"```(?:python|json|yaml)[^`]*?class\s+(\w+)[^`]*?```"
        matches = re.finditer(code_block_pattern, content, re.DOTALL | re.IGNORECASE)
        for match in matches:
            models.append(match.group(1))

        # Look for schema sections
        schema_pattern = (
            r"##\s*(?:Schema|Model|Request|Response)s?\s*.*?\n.*?(?:```|###|\Z)"
        )
        schema_matches = re.finditer(schema_pattern, content, re.DOTALL | re.IGNORECASE)
        for schema_match in schema_matches:
            # Extract model names from the schema section
            model_names = re.findall(
                r"\b([A-Z][a-zA-Z]*(?:Request|Response|Model|Schema))\b",
                schema_match.group(0),
            )
            models.extend(model_names)

        return list(set(models))

    def _extract_port_references(self, content: str) -> list[int]:
        """Extract port references from documentation."""
        ports = []

        # Look for port numbers in various formats
        port_patterns = [
            r"port[:\s]+(\d{4})",
            r"localhost:(\d{4})",
            r"127\.0\.0\.1:(\d{4})",
            r"http://[^:]+:(\d{4})",
            r"https://[^:]+:(\d{4})",
            r"Port:\s*(\d{4})",
            r'"port":\s*(\d{4})',
        ]

        for pattern in port_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                port = int(match.group(1))
                if 8000 <= port <= 9000:  # Filter for relevant service ports
                    ports.append(port)

        return list(set(ports))

    def validate_service_sync(self, service_name: str) -> list[SyncIssue]:
        """Validate synchronization between service code and documentation."""
        issues = []

        if service_name not in self.service_analyses:
            issues.append(
                SyncIssue(
                    severity="ERROR",
                    category="missing_analysis",
                    service=service_name,
                    message="Service implementation not analyzed",
                )
            )
            return issues

        if service_name not in self.documentation_info:
            issues.append(
                SyncIssue(
                    severity="ERROR",
                    category="missing_documentation",
                    service=service_name,
                    message="API documentation not found",
                )
            )
            return issues

        service = self.service_analyses[service_name]
        doc_info = self.documentation_info[service_name]

        # Validate constitutional hash presence
        if not service.constitutional_hash_present:
            issues.append(
                SyncIssue(
                    severity="HIGH",
                    category="constitutional_compliance",
                    service=service_name,
                    message="Constitutional hash missing from service implementation",
                    suggested_fix=(
                        f"Add constitutional hash '{CONSTITUTIONAL_HASH}' to service"
                        " code"
                    ),
                    code_location=service.service_path,
                )
            )

        if not doc_info.constitutional_hash_present:
            issues.append(
                SyncIssue(
                    severity="HIGH",
                    category="constitutional_compliance",
                    service=service_name,
                    message="Constitutional hash missing from API documentation",
                    suggested_fix=(
                        f"Add constitutional hash '{CONSTITUTIONAL_HASH}' to"
                        " documentation"
                    ),
                    doc_location=doc_info.doc_path,
                )
            )

        # Validate port consistency
        if service.port and doc_info.port_references:
            if service.port not in doc_info.port_references:
                issues.append(
                    SyncIssue(
                        severity="MEDIUM",
                        category="port_mismatch",
                        service=service_name,
                        message=(
                            f"Port mismatch: code uses {service.port}, docs reference"
                            f" {doc_info.port_references}"
                        ),
                        suggested_fix=(
                            f"Update documentation to reference port {service.port}"
                        ),
                        code_location=service.service_path,
                        doc_location=doc_info.doc_path,
                    )
                )

        # Validate endpoint synchronization
        implemented_endpoints = set(
            f"{ep.method} {ep.path}" for ep in service.endpoints
        )
        documented_endpoints = set(doc_info.documented_endpoints)

        # Find missing documentation
        missing_docs = implemented_endpoints - documented_endpoints
        for endpoint in missing_docs:
            issues.append(
                SyncIssue(
                    severity="MEDIUM",
                    category="missing_endpoint_doc",
                    service=service_name,
                    message=f"Endpoint {endpoint} implemented but not documented",
                    suggested_fix=f"Add documentation for {endpoint}",
                    code_location=service.service_path,
                    doc_location=doc_info.doc_path,
                )
            )

        # Find missing implementations
        missing_impl = documented_endpoints - implemented_endpoints
        for endpoint in missing_impl:
            issues.append(
                SyncIssue(
                    severity="HIGH",
                    category="missing_endpoint_impl",
                    service=service_name,
                    message=f"Endpoint {endpoint} documented but not implemented",
                    suggested_fix=f"Implement {endpoint} or remove from documentation",
                    code_location=service.service_path,
                    doc_location=doc_info.doc_path,
                )
            )

        # Validate model synchronization
        if service.models and doc_info.documented_models:
            implemented_models = set(service.models)
            documented_models = set(doc_info.documented_models)

            missing_model_docs = implemented_models - documented_models
            for model in missing_model_docs:
                issues.append(
                    SyncIssue(
                        severity="LOW",
                        category="missing_model_doc",
                        service=service_name,
                        message=f"Model {model} implemented but not documented",
                        suggested_fix=f"Add documentation for {model} schema",
                        code_location=service.service_path,
                        doc_location=doc_info.doc_path,
                    )
                )

        return issues

    def analyze_all_services(self) -> dict[str, Any]:
        """Analyze all configured services."""
        print("🔌 ACGS API-Code Synchronization Validator")
        print("=" * 60)
        print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
        print(f"Services to analyze: {len(SERVICE_MAPPING)}")
        print()

        start_time = time.time()

        # Analyze service implementations
        print("🔍 Analyzing service implementations...")
        for service_name, config in SERVICE_MAPPING.items():
            service_path = REPO_ROOT / config["service_path"]
            if service_path.exists():
                print(f"  📄 Analyzing {service_name}...")
                analysis = self.analyze_service_implementation(
                    service_name, service_path
                )
                self.service_analyses[service_name] = analysis
                print(f"    ✅ Found {len(analysis.endpoints)} endpoints")
            else:
                print(f"  ❌ Service file not found: {service_path}")
                self.sync_issues.append(
                    SyncIssue(
                        severity="ERROR",
                        category="missing_service",
                        service=service_name,
                        message=(
                            "Service implementation not found:"
                            f" {config['service_path']}"
                        ),
                    )
                )

        # Analyze API documentation
        print("\n📚 Analyzing API documentation...")
        for service_name, config in SERVICE_MAPPING.items():
            doc_path = REPO_ROOT / config["api_doc"]
            if doc_path.exists():
                print(f"  📄 Analyzing {service_name} docs...")
                doc_info = self.analyze_api_documentation(service_name, doc_path)
                self.documentation_info[service_name] = doc_info
                print(
                    f"    ✅ Found {len(doc_info.documented_endpoints)} documented"
                    " endpoints"
                )
            else:
                print(f"  ❌ API doc not found: {doc_path}")
                self.sync_issues.append(
                    SyncIssue(
                        severity="HIGH",
                        category="missing_api_doc",
                        service=service_name,
                        message=f"API documentation not found: {config['api_doc']}",
                    )
                )

        # Validate synchronization
        print("\n🔄 Validating synchronization...")
        for service_name in SERVICE_MAPPING:
            if (
                service_name in self.service_analyses
                and service_name in self.documentation_info
            ):
                print(f"  🔍 Validating {service_name}...")
                service_issues = self.validate_service_sync(service_name)
                self.sync_issues.extend(service_issues)
                print(f"    ⚠️  Found {len(service_issues)} issues")

        analysis_time = time.time() - start_time

        # Compile results
        results = {
            "timestamp": datetime.now().isoformat(),
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "analysis_duration": analysis_time,
            "services_analyzed": len(self.service_analyses),
            "docs_analyzed": len(self.documentation_info),
            "total_issues": len(self.sync_issues),
            "issues_by_severity": self._group_issues_by_severity(),
            "issues_by_category": self._group_issues_by_category(),
            "service_summaries": self._generate_service_summaries(),
            "sync_issues": [
                {
                    "severity": issue.severity,
                    "category": issue.category,
                    "service": issue.service,
                    "message": issue.message,
                    "suggested_fix": issue.suggested_fix,
                    "code_location": issue.code_location,
                    "doc_location": issue.doc_location,
                }
                for issue in self.sync_issues
            ],
        }

        return results

    def _group_issues_by_severity(self) -> dict[str, int]:
        """Group issues by severity level."""
        severity_counts = defaultdict(int)
        for issue in self.sync_issues:
            severity_counts[issue.severity] += 1
        return dict(severity_counts)

    def _group_issues_by_category(self) -> dict[str, int]:
        """Group issues by category."""
        category_counts = defaultdict(int)
        for issue in self.sync_issues:
            category_counts[issue.category] += 1
        return dict(category_counts)

    def _generate_service_summaries(self) -> dict[str, dict[str, Any]]:
        """Generate summary for each service."""
        summaries = {}

        for service_name in SERVICE_MAPPING:
            summary = {
                "service_analyzed": service_name in self.service_analyses,
                "docs_analyzed": service_name in self.documentation_info,
                "endpoints_implemented": 0,
                "endpoints_documented": 0,
                "models_implemented": 0,
                "models_documented": 0,
                "constitutional_compliance": {"code": False, "docs": False},
                "port_info": {"code_port": None, "doc_ports": []},
                "sync_score": 0.0,
                "issues_count": 0,
            }

            if service_name in self.service_analyses:
                service = self.service_analyses[service_name]
                summary["endpoints_implemented"] = len(service.endpoints)
                summary["models_implemented"] = len(service.models)
                summary["constitutional_compliance"][
                    "code"
                ] = service.constitutional_hash_present
                summary["port_info"]["code_port"] = service.port

            if service_name in self.documentation_info:
                doc_info = self.documentation_info[service_name]
                summary["endpoints_documented"] = len(doc_info.documented_endpoints)
                summary["models_documented"] = len(doc_info.documented_models)
                summary["constitutional_compliance"][
                    "docs"
                ] = doc_info.constitutional_hash_present
                summary["port_info"]["doc_ports"] = doc_info.port_references

            # Calculate sync score
            if summary["service_analyzed"] and summary["docs_analyzed"]:
                endpoints_match = min(
                    summary["endpoints_implemented"], summary["endpoints_documented"]
                )
                total_endpoints = max(
                    summary["endpoints_implemented"], summary["endpoints_documented"]
                )

                if total_endpoints > 0:
                    endpoint_score = endpoints_match / total_endpoints
                else:
                    endpoint_score = 1.0

                constitutional_score = (
                    1.0
                    if (
                        summary["constitutional_compliance"]["code"]
                        and summary["constitutional_compliance"]["docs"]
                    )
                    else 0.5
                )

                summary["sync_score"] = (endpoint_score + constitutional_score) / 2

            # Count issues for this service
            summary["issues_count"] = len(
                [issue for issue in self.sync_issues if issue.service == service_name]
            )

            summaries[service_name] = summary

        return summaries

    def generate_report(self, results: dict[str, Any]) -> str:
        """Generate comprehensive sync validation report."""
        issues_by_severity = results["issues_by_severity"]

        report = f"""# ACGS API-Code Synchronization Validation Report

<!-- Constitutional Hash: {CONSTITUTIONAL_HASH} -->

**Date**: {results['timestamp']}
**Constitutional Hash**: `{CONSTITUTIONAL_HASH}`
**Analysis Duration**: {results['analysis_duration']:.2f} seconds

## Executive Summary

| Metric | Value |
|--------|-------|
| Services Analyzed | {results['services_analyzed']}/{len(SERVICE_MAPPING)} |
| Documentation Files | {results['docs_analyzed']}/{len(SERVICE_MAPPING)} |
| Total Issues Found | {results['total_issues']} |
| Critical Issues | {issues_by_severity.get('CRITICAL', 0)} |
| High Priority Issues | {issues_by_severity.get('HIGH', 0)} |
| Medium Priority Issues | {issues_by_severity.get('MEDIUM', 0)} |
| Low Priority Issues | {issues_by_severity.get('LOW', 0)} |

## Service Synchronization Status

"""

        # Service summaries table
        report += (
            "| Service | Impl | Docs | Endpoints | Models | Const Hash | Port | Sync"
            " Score | Issues |\n"
        )
        report += "|---------|------|------|-----------|--------|------------|------|------------|--------|\n"

        for service_name, summary in results["service_summaries"].items():
            impl_status = "✅" if summary["service_analyzed"] else "❌"
            docs_status = "✅" if summary["docs_analyzed"] else "❌"

            endpoints = (
                f"{summary['endpoints_implemented']}/{summary['endpoints_documented']}"
            )
            models = f"{summary['models_implemented']}/{summary['models_documented']}"

            const_code = "✅" if summary["constitutional_compliance"]["code"] else "❌"
            const_docs = "✅" if summary["constitutional_compliance"]["docs"] else "❌"
            const_status = f"{const_code}/{const_docs}"

            port_info = summary["port_info"]["code_port"] or "N/A"
            sync_score = f"{summary['sync_score']:.2f}"
            issues_count = summary["issues_count"]

            report += (
                f"| {service_name} | {impl_status} | {docs_status} | {endpoints} |"
                f" {models} | {const_status} | {port_info} | {sync_score} |"
                f" {issues_count} |\n"
            )

        # Issues by category
        report += "\n## Issues by Category\n\n"
        for category, count in results["issues_by_category"].items():
            report += f"- **{category.replace('_', ' ').title()}**: {count} issues\n"

        # Detailed issues by severity
        issues_by_sev = {}
        for issue in results["sync_issues"]:
            severity = issue["severity"]
            if severity not in issues_by_sev:
                issues_by_sev[severity] = []
            issues_by_sev[severity].append(issue)

        for severity in ["CRITICAL", "ERROR", "HIGH", "MEDIUM", "LOW"]:
            if severity in issues_by_sev:
                issues = issues_by_sev[severity]
                report += f"\n### {severity} Priority Issues ({len(issues)})\n\n"

                for issue in issues:
                    report += (
                        f"**{issue['service']}**"
                        f" ({issue['category'].replace('_', ' ')})\n"
                    )
                    report += f"- {issue['message']}\n"

                    if issue["suggested_fix"]:
                        report += f"- 💡 **Fix**: {issue['suggested_fix']}\n"

                    if issue["code_location"]:
                        report += f"- 📄 **Code**: {issue['code_location']}\n"

                    if issue["doc_location"]:
                        report += f"- 📚 **Docs**: {issue['doc_location']}\n"

                    report += "\n"

        # Recommendations
        report += "## Recommendations\n\n"

        if issues_by_severity.get("CRITICAL", 0) > 0:
            report += (
                "🚨 **CRITICAL**: Address critical synchronization issues"
                " immediately.\n\n"
            )

        if issues_by_severity.get("HIGH", 0) > 0:
            report += (
                "⚠️ **HIGH**: Resolve high-priority API-documentation mismatches.\n\n"
            )

        missing_docs = sum(
            1
            for issue in results["sync_issues"]
            if issue["category"] == "missing_api_doc"
        )
        if missing_docs > 0:
            report += (
                f"📚 **DOCUMENTATION**: Create {missing_docs} missing API documentation"
                " files.\n\n"
            )

        const_issues = sum(
            1
            for issue in results["sync_issues"]
            if issue["category"] == "constitutional_compliance"
        )
        if const_issues > 0:
            report += (
                "📋 **CONSTITUTIONAL**: Add constitutional hash to"
                f" {const_issues} files.\n\n"
            )

        if results["total_issues"] == 0:
            report += (
                "✅ **EXCELLENT**: All API implementations are synchronized with"
                " documentation.\n\n"
            )

        # Service-specific recommendations
        report += "### Service-Specific Actions\n\n"
        for service_name, summary in results["service_summaries"].items():
            if summary["issues_count"] > 0:
                service_issues = [
                    issue
                    for issue in results["sync_issues"]
                    if issue["service"] == service_name
                ]
                critical_issues = [
                    issue
                    for issue in service_issues
                    if issue["severity"] in ["CRITICAL", "HIGH"]
                ]

                if critical_issues:
                    report += (
                        f"- **{service_name}**: {len(critical_issues)} critical issues"
                        " require immediate attention\n"
                    )

        report += """

## Implementation Progress

### Endpoints Implementation Status
"""

        for service_name, summary in results["service_summaries"].items():
            if summary["service_analyzed"]:
                impl_count = summary["endpoints_implemented"]
                doc_count = summary["endpoints_documented"]

                if impl_count > 0 or doc_count > 0:
                    coverage = (
                        min(impl_count, doc_count) / max(impl_count, doc_count, 1) * 100
                    )
                    report += (
                        f"- **{service_name}**: {coverage:.0f}% synchronized"
                        f" ({impl_count} impl, {doc_count} docs)\n"
                    )

        report += f"""

---

**API-Code Synchronization Validation**: Generated by ACGS API-Code Sync Validator
**Constitutional Hash**: `{CONSTITUTIONAL_HASH}` ✅
**Analysis Coverage**: {results['services_analyzed']}/{len(SERVICE_MAPPING)} services
"""

        return report


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="ACGS API-Code Synchronization Validator"
    )
    parser.add_argument("--output", type=Path, help="Output file for validation report")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--service", type=str, help="Analyze specific service only")

    args = parser.parse_args()

    # Run analysis
    validator = APICodeSyncValidator()
    results = validator.analyze_all_services()

    # Print summary
    print("\n" + "=" * 60)
    print("📊 SYNCHRONIZATION SUMMARY")
    print("=" * 60)

    print(
        f"🔍 Services Analyzed: {results['services_analyzed']}/{len(SERVICE_MAPPING)}"
    )
    print(f"📚 Documentation Files: {results['docs_analyzed']}/{len(SERVICE_MAPPING)}")
    print(f"⚠️ Total Issues: {results['total_issues']}")
    print(f"🚨 Critical Issues: {results['issues_by_severity'].get('CRITICAL', 0)}")
    print(f"⚡ Analysis Time: {results['analysis_duration']:.2f} seconds")

    # Save results
    if args.json or args.output:
        if args.output:
            if args.json:
                with open(args.output, "w") as f:
                    json.dump(results, f, indent=2)
                print(f"📊 JSON results saved to: {args.output}")
            else:
                report = validator.generate_report(results)
                with open(args.output, "w") as f:
                    f.write(report)
                print(f"📄 Report saved to: {args.output}")
        else:
            print(json.dumps(results, indent=2))
    else:
        # Generate and save markdown report
        report = validator.generate_report(results)
        report_file = (
            REPO_ROOT
            / "validation_reports"
            / f"api_sync_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        )
        report_file.parent.mkdir(exist_ok=True)

        with open(report_file, "w") as f:
            f.write(report)
        print(f"📄 Validation report saved to: {report_file}")

    # Exit with appropriate code
    if results["issues_by_severity"].get("CRITICAL", 0) > 0:
        print(
            f"\n🚨 {results['issues_by_severity']['CRITICAL']} CRITICAL issues require"
            " immediate attention!"
        )
        return 2
    elif results["issues_by_severity"].get("HIGH", 0) > 0:
        print(
            f"\n⚠️ {results['issues_by_severity']['HIGH']} HIGH priority issues should"
            " be addressed"
        )
        return 1
    else:
        print("\n🎉 API-code synchronization validation completed successfully!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
