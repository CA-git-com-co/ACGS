#!/usr/bin/env python3
"""
ACGS Enhanced Automated Documentation Generator
Constitutional Hash: cdd01ef066bc6cf2

This enhanced tool automatically generates and maintains documentation with:
- Cross-reference synchronization and validation
- API endpoint documentation generation from code
- Automated linking and relationship maintenance
- Missing documentation detection and generation
- Broken link resolution with suggestions
- Constitutional compliance validation and updates
"""

import json
import re
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

# Import our validation tools
AdvancedCrossReferenceAnalyzer = None
APICodeSyncValidator = None
SERVICE_MAPPING = {
    "authentication": {
        "service_path": (
            "services/platform_services/authentication/auth_service/app/main.py"
        ),
        "api_doc": "docs/api/authentication.md",
        "port": 8016,
        "description": "Authentication and authorization service",
    },
    "constitutional-ai": {
        "service_path": "services/core/constitutional-ai/ac_service/app/main.py",
        "api_doc": "docs/api/constitutional-ai.md",
        "port": 8001,
        "description": "Constitutional AI compliance service",
    },
    "integrity": {
        "service_path": (
            "services/platform_services/integrity/integrity_service/app/main.py"
        ),
        "api_doc": "docs/api/integrity.md",
        "port": 8002,
        "description": "Data integrity validation service",
    },
    "formal-verification": {
        "service_path": "services/core/formal-verification/fv_service/main.py",
        "api_doc": "docs/api/formal-verification.md",
        "port": 8003,
        "description": "Formal verification service",
    },
    "governance_synthesis": {
        "service_path": "services/core/governance-synthesis/gs_service/app/main.py",
        "api_doc": "docs/api/governance_synthesis.md",
        "port": 8004,
        "description": "Governance policy synthesis service",
    },
    "policy-governance": {
        "service_path": "services/core/policy-governance/pgc_service/app/main.py",
        "api_doc": "docs/api/policy-governance.md",
        "port": 8005,
        "description": "Policy governance and management service",
    },
    "evolutionary-computation": {
        "service_path": "services/core/evolutionary-computation/main.py",
        "api_doc": "docs/api/evolutionary-computation.md",
        "port": 8006,
        "description": "Evolutionary computation service",
    },
}

try:
    # Try to import validation tools from the validation directory
    import importlib.util

    # Import advanced cross-reference analyzer
    analyzer_path = (
        Path(__file__).parent.parent
        / "validation"
        / "advanced_cross_reference_analyzer.py"
    )
    if analyzer_path.exists():
        spec = importlib.util.spec_from_file_location(
            "advanced_cross_reference_analyzer", analyzer_path
        )
        analyzer_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(analyzer_module)
        AdvancedCrossReferenceAnalyzer = analyzer_module.AdvancedCrossReferenceAnalyzer
        print("✅ Advanced Cross-Reference Analyzer imported successfully")

    # Import API sync validator
    validator_path = (
        Path(__file__).parent.parent / "validation" / "api_code_sync_validator.py"
    )
    if validator_path.exists():
        spec = importlib.util.spec_from_file_location(
            "api_code_sync_validator", validator_path
        )
        validator_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(validator_module)
        APICodeSyncValidator = validator_module.APICodeSyncValidator
        print("✅ API Code Sync Validator imported successfully")

except Exception as e:
    print(f"⚠️ Could not import validation tools: {e}")
    print("📝 Will use fallback documentation generation methods")

# Configuration
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
REPO_ROOT = Path(__file__).parent.parent.parent
DOCS_DIR = REPO_ROOT / "docs"


class EnhancedAutoDocGenerator:
    """Enhanced documentation generator with cross-reference maintenance."""

    def __init__(self):
        self.generated_files = []
        self.updated_files = []
        self.cross_ref_analyzer = None
        self.api_sync_validator = None
        self.service_endpoints = {}
        self.broken_links = []
        self.suggested_fixes = []

    def initialize_analyzers(self):
        """Initialize validation and analysis tools."""
        if AdvancedCrossReferenceAnalyzer:
            self.cross_ref_analyzer = AdvancedCrossReferenceAnalyzer()
            print("✅ Cross-reference analyzer initialized")

        if APICodeSyncValidator:
            self.api_sync_validator = APICodeSyncValidator()
            print("✅ API-code sync validator initialized")

    def generate_missing_api_documentation(self) -> list[str]:
        """Generate missing API documentation files based on service implementations."""
        generated_docs = []

        if not self.api_sync_validator:
            print("⚠️ API sync validator not available, skipping API doc generation")
            return generated_docs

        print("🔍 Analyzing service implementations for missing API docs...")

        # Run API sync analysis
        sync_results = self.api_sync_validator.analyze_all_services()

        for service_name, service_config in SERVICE_MAPPING.items():
            if service_name in self.api_sync_validator.service_analyses:
                service_analysis = self.api_sync_validator.service_analyses[
                    service_name
                ]

                # Check if API doc exists
                api_doc_path = REPO_ROOT / service_config["api_doc"]

                if not api_doc_path.exists() or len(service_analysis.endpoints) > 0:
                    print(f"📝 Generating API documentation for {service_name}...")

                    api_doc_content = self._generate_api_documentation(
                        service_name, service_analysis, service_config
                    )

                    # Ensure directory exists
                    api_doc_path.parent.mkdir(parents=True, exist_ok=True)

                    with open(api_doc_path, "w") as f:
                        f.write(api_doc_content)

                    generated_docs.append(str(api_doc_path.relative_to(REPO_ROOT)))
                    self.generated_files.append(str(api_doc_path))

                    print(f"✅ Generated {api_doc_path.relative_to(REPO_ROOT)}")

        return generated_docs

    def _generate_api_documentation(
        self, service_name: str, service_analysis, service_config: dict[str, Any]
    ) -> str:
        """Generate comprehensive API documentation for a service."""
        port = service_config.get("port", 8000)

        # Group endpoints by path prefix
        endpoint_groups = defaultdict(list)
        for endpoint in service_analysis.endpoints:
            # Group by first path segment after /api/
            path_parts = endpoint.path.split("/")
            if len(path_parts) > 3 and path_parts[1] == "api":
                group = path_parts[3]  # e.g., 'constitutional', 'multimodal'
            elif endpoint.path.startswith("/api/"):
                group = "core"
            else:
                group = "system"
            endpoint_groups[group].append(endpoint)

        doc_content = f"""# {service_name.replace('_', ' ').replace('-', ' ').title()} API Documentation

<!-- Constitutional Hash: {CONSTITUTIONAL_HASH} -->

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Constitutional Hash**: `{CONSTITUTIONAL_HASH}`
**Service Port**: {port}
**API Version**: v1

## Service Overview

{service_analysis.service_path.replace('/', ' ').replace('_', ' ').title()} provides {service_config.get('description', 'core functionality')} for the ACGS platform.

### Base URL
```
http://localhost:{port}
```

### Authentication
All API endpoints require JWT authentication unless otherwise specified.

```http
Authorization: Bearer <jwt_token>
```

### Response Format
All API responses include the constitutional hash for compliance verification:

```json
{{
  "data": "response content",
  "constitutional_hash": "{CONSTITUTIONAL_HASH}",
  "timestamp": "ISO 8601 timestamp"
}}
```

## Endpoints

### Quick Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
"""

        # Add quick reference table
        for endpoint in sorted(
            service_analysis.endpoints, key=lambda x: (x.path, x.method)
        ):
            description = endpoint.description or "No description available"
            # Truncate long descriptions
            if len(description) > 80:
                description = description[:77] + "..."
            doc_content += (
                f"| {endpoint.method} | `{endpoint.path}` | {description} |\n"
            )

        # Add detailed endpoint documentation by group
        for group_name, endpoints in sorted(endpoint_groups.items()):
            if not endpoints:
                continue

            doc_content += f"\n### {group_name.title()} Endpoints\n\n"

            for endpoint in sorted(endpoints, key=lambda x: x.path):
                doc_content += self._generate_endpoint_documentation(
                    endpoint, service_name, port
                )

        # Add error handling section
        doc_content += f"""
## Error Handling

### Standard Error Response
```json
{{
  "error": {{
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": {{}}
  }},
  "constitutional_hash": "{CONSTITUTIONAL_HASH}",
  "timestamp": "ISO 8601 timestamp"
}}
```

### Common Error Codes

| Code | Status | Description |
|------|--------|-------------|
| VALIDATION_ERROR | 400 | Request validation failed |
| UNAUTHORIZED | 401 | Authentication required |
| FORBIDDEN | 403 | Insufficient permissions |
| NOT_FOUND | 404 | Resource not found |
| CONSTITUTIONAL_VIOLATION | 422 | Constitutional compliance violation |
| INTERNAL_ERROR | 500 | Internal server error |

## Performance Targets

- **Latency**: P99 ≤ 5ms for cached queries
- **Throughput**: ≥ 100 RPS sustained
- **Cache Hit Rate**: ≥ 85%
- **Availability**: 99.9% uptime
- **Constitutional Compliance**: 100% validation

## Monitoring

### Health Check
```http
GET /health
```

### Metrics
```http
GET /metrics
```

## Related Documentation

- [Service Architecture](../architecture/ACGS_SERVICE_OVERVIEW.md)
- [Deployment Guide](../deployment/ACGS_IMPLEMENTATION_GUIDE.md)
- [API Index](AUTOMATED_API_INDEX.md)

## Constitutional Compliance

This API implements constitutional compliance with hash `{CONSTITUTIONAL_HASH}`:
- ✅ All responses include constitutional hash
- ✅ All operations validated for constitutional compliance
- ✅ Audit logging with constitutional tracking
- ✅ Security controls with constitutional verification

---

**Auto-Generated**: This documentation is automatically generated from service implementation
**Constitutional Hash**: `{CONSTITUTIONAL_HASH}` ✅
**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        return doc_content

    def _generate_endpoint_documentation(
        self, endpoint, service_name: str, port: int
    ) -> str:
        """Generate detailed documentation for a single endpoint."""
        doc = f"\n#### {endpoint.method} {endpoint.path}\n\n"

        if endpoint.description:
            doc += f"{endpoint.description}\n\n"

        # Request format
        doc += (
            f"**Request**\n```http\n{endpoint.method} {endpoint.path}\nHost:"
            f" localhost:{port}\n"
        )

        if endpoint.method in ["POST", "PUT", "PATCH"]:
            doc += "Content-Type: application/json\n"

        doc += (
            "Authorization: Bearer <token>\nX-Constitutional-Hash:"
            f" {CONSTITUTIONAL_HASH}\n```\n\n"
        )

        # Parameters
        if endpoint.parameters:
            doc += "**Parameters**\n\n"
            for param in endpoint.parameters:
                if param not in ["session", "tenant_context"]:  # Skip internal params
                    doc += f"- `{param}`: (auto-detected parameter)\n"
            doc += "\n"

        # Response example
        doc += "**Response**\n```json\n{\n"
        doc += '  "result": "success",\n'
        doc += f'  "constitutional_hash": "{CONSTITUTIONAL_HASH}",\n'
        doc += f'  "timestamp": "{datetime.now().isoformat()}"\n'
        doc += "}\n```\n\n"

        return doc

    def fix_broken_cross_references(self) -> list[str]:
        """Identify and fix broken cross-references."""
        fixed_refs = []

        if not self.cross_ref_analyzer:
            print("⚠️ Cross-reference analyzer not available")
            return fixed_refs

        print("🔍 Analyzing cross-references for broken links...")

        # Run cross-reference analysis
        analysis_results = self.cross_ref_analyzer.run_comprehensive_analysis()

        # Find broken reference issues
        broken_ref_issues = [
            issue
            for issue in analysis_results["validation_issues"]
            if issue["category"] == "broken_reference"
        ]

        print(f"Found {len(broken_ref_issues)} broken references")

        for issue in broken_ref_issues:
            if issue["related_files"]:
                # Try to fix with suggestions
                fixed = self._attempt_reference_fix(issue)
                if fixed:
                    fixed_refs.append(f"{issue['file_path']}:{issue['line_number']}")

        return fixed_refs

    def _attempt_reference_fix(self, issue: dict[str, Any]) -> bool:
        """Attempt to fix a broken reference using suggestions."""
        try:
            file_path = REPO_ROOT / issue["file_path"]
            if not file_path.exists():
                return False

            with open(file_path) as f:
                content = f.read()
                lines = content.split("\n")

            # Find the broken link in the content
            line_num = issue.get("line_number", 1) - 1
            if 0 <= line_num < len(lines):
                line = lines[line_num]

                # Look for the best suggestion
                suggestions = issue.get("related_files", [])
                if suggestions:
                    best_suggestion = suggestions[0]  # Take the first suggestion

                    # Try to replace the broken link
                    # This is a simplified approach - in practice, would need more sophisticated logic
                    link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"

                    def replace_link(match):
                        link_text = match.group(1)
                        old_url = match.group(2)
                        # Replace with the suggestion
                        return f"[{link_text}]({best_suggestion})"

                    new_line = re.sub(link_pattern, replace_link, line)
                    if new_line != line:
                        lines[line_num] = new_line

                        # Write back the fixed content
                        with open(file_path, "w") as f:
                            f.write("\n".join(lines))

                        self.updated_files.append(str(file_path))
                        print(
                            "✅ Fixed broken reference in"
                            f" {file_path.relative_to(REPO_ROOT)}"
                        )
                        return True

        except Exception as e:
            print(f"❌ Failed to fix reference in {issue['file_path']}: {e}")

        return False

    def generate_cross_reference_index(self) -> str:
        """Generate a comprehensive cross-reference index."""
        print("📊 Generating cross-reference index...")

        index_path = DOCS_DIR / "CROSS_REFERENCE_INDEX.md"

        if self.cross_ref_analyzer:
            analysis_results = self.cross_ref_analyzer.run_comprehensive_analysis()
            dependency_graph = analysis_results["dependency_graph"]

            # Generate index content
            index_content = f"""# ACGS Documentation Cross-Reference Index

<!-- Constitutional Hash: {CONSTITUTIONAL_HASH} -->

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Constitutional Hash**: `{CONSTITUTIONAL_HASH}`
**Total Documents**: {len(dependency_graph['nodes'])}
**Total Cross-References**: {len(dependency_graph['edges'])}

## Document Categories

### API Documentation
"""

            # Group documents by category
            api_docs = [
                node for node in dependency_graph["nodes"] if "/api/" in node["id"]
            ]
            architecture_docs = [
                node
                for node in dependency_graph["nodes"]
                if "/architecture/" in node["id"]
            ]
            deployment_docs = [
                node
                for node in dependency_graph["nodes"]
                if "/deployment/" in node["id"]
            ]

            for doc in sorted(api_docs, key=lambda x: x["id"]):
                connections = doc["degree"]
                compliance = "✅" if doc["constitutional_hash"] else "❌"
                index_content += (
                    f"- [{doc['title'] or doc['id'].split('/')[-1]}]({doc['id']})"
                    f" ({connections} refs) {compliance}\n"
                )

            index_content += "\n### Architecture Documentation\n"
            for doc in sorted(architecture_docs, key=lambda x: x["id"]):
                connections = doc["degree"]
                compliance = "✅" if doc["constitutional_hash"] else "❌"
                index_content += (
                    f"- [{doc['title'] or doc['id'].split('/')[-1]}]({doc['id']})"
                    f" ({connections} refs) {compliance}\n"
                )

            index_content += "\n### Deployment Documentation\n"
            for doc in sorted(deployment_docs, key=lambda x: x["id"]):
                connections = doc["degree"]
                compliance = "✅" if doc["constitutional_hash"] else "❌"
                index_content += (
                    f"- [{doc['title'] or doc['id'].split('/')[-1]}]({doc['id']})"
                    f" ({connections} refs) {compliance}\n"
                )

            # Add relationship analysis
            index_content += """

## Cross-Reference Analysis

### Most Connected Documents
"""

            sorted_nodes = sorted(
                dependency_graph["nodes"], key=lambda x: x["degree"], reverse=True
            )
            for node in sorted_nodes[:10]:
                index_content += (
                    f"- [{node['id'].split('/')[-1]}]({node['id']}) -"
                    f" {node['degree']} connections\n"
                )

            # Add orphaned documents
            orphaned = [
                node for node in dependency_graph["nodes"] if node["degree"] == 0
            ]
            if orphaned:
                index_content += "\n### Orphaned Documents (No Cross-References)\n"
                for node in orphaned:
                    index_content += (
                        f"- [{node['id'].split('/')[-1]}]({node['id']}) - Consider"
                        " adding cross-references\n"
                    )

            index_content += f"""

## Validation Status

- **Total Issues**: {analysis_results['summary']['total_issues']}
- **Broken References**: {analysis_results['summary'].get('high_issues', 0)}
- **Missing References**: {analysis_results['summary'].get('low_issues', 0)}

## Related Tools

- [Advanced Cross-Reference Analyzer](../tools/validation/advanced_cross_reference_analyzer.py)
- [API-Code Sync Validator](../tools/validation/api_code_sync_validator.py)
- [Documentation Relationship Graph](../visualization_output/index.html)

---

**Auto-Generated**: This index is automatically updated during documentation maintenance
**Constitutional Hash**: `{CONSTITUTIONAL_HASH}` ✅
"""
        else:
            # Fallback content if analyzer not available
            index_content = f"""# ACGS Documentation Cross-Reference Index

<!-- Constitutional Hash: {CONSTITUTIONAL_HASH} -->

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Constitutional Hash**: `{CONSTITUTIONAL_HASH}`

## Documentation Structure

This index provides an overview of documentation cross-references and relationships within the ACGS project.

### API Documentation
- [Authentication API](api/authentication.md)
- [Constitutional AI API](api/constitutional-ai.md)
- [Integrity API](api/integrity.md)
- [Formal Verification API](api/formal-verification.md)
- [Governance Synthesis API](api/governance_synthesis.md)
- [Policy Governance API](api/policy-governance.md)
- [Evolutionary Computation API](api/evolutionary-computation.md)

### Architecture Documentation
- [Service Architecture Overview](architecture/ACGS_SERVICE_OVERVIEW.md)
- [Code Analysis Engine Architecture](architecture/ACGS_CODE_ANALYSIS_ENGINE_ARCHITECTURE.md)

### Deployment Documentation
- [Implementation Guide](deployment/ACGS_IMPLEMENTATION_GUIDE.md)
- [Deployment Guide](deployment/DEPLOYMENT_GUIDE.md)

---

**Auto-Generated**: This index is automatically updated during documentation maintenance
**Constitutional Hash**: `{CONSTITUTIONAL_HASH}` ✅
"""

        with open(index_path, "w") as f:
            f.write(index_content)

        self.generated_files.append(str(index_path))
        return str(index_path.relative_to(REPO_ROOT))

    def update_documentation_links(self) -> list[str]:
        """Update and maintain documentation links across all files."""
        updated_files = []

        print("🔗 Updating documentation links...")

        # Find all markdown files
        md_files = list(DOCS_DIR.rglob("*.md"))

        for md_file in md_files:
            try:
                with open(md_file) as f:
                    content = f.read()

                original_content = content

                # Update constitutional hash references
                content = self._update_constitutional_hash_references(content)

                # Update API documentation links
                content = self._update_api_documentation_links(content)

                # Update service port references
                content = self._update_service_port_references(content)

                # Update cross-references to moved files
                content = self._update_moved_file_references(content)

                # If content changed, write it back
                if content != original_content:
                    with open(md_file, "w") as f:
                        f.write(content)

                    updated_files.append(str(md_file.relative_to(REPO_ROOT)))
                    self.updated_files.append(str(md_file))

            except Exception as e:
                print(f"❌ Error updating {md_file}: {e}")

        return updated_files

    def _update_constitutional_hash_references(self, content: str) -> str:
        """Update constitutional hash references in content."""
        # Replace old hash patterns with current hash
        old_hash_pattern = r"cdd01ef066bc6cf[0-9a-f]*"
        content = re.sub(old_hash_pattern, CONSTITUTIONAL_HASH, content)

        # Ensure constitutional hash is present in comment format
        if CONSTITUTIONAL_HASH not in content and "# " in content:
            # Add after first H1 header
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if line.startswith("# "):
                    lines.insert(i + 1, "")
                    lines.insert(
                        i + 2, f"<!-- Constitutional Hash: {CONSTITUTIONAL_HASH} -->"
                    )
                    lines.insert(i + 3, "")
                    break
            content = "\n".join(lines)

        return content

    def _update_api_documentation_links(self, content: str) -> str:
        """Update API documentation links to ensure they point to existing files."""
        # Update relative API links
        api_link_pattern = r"\[([^\]]+)\]\(api/([^)]+\.md)\)"

        def update_api_link(match):
            link_text = match.group(1)
            api_file = match.group(2)
            api_path = DOCS_DIR / "api" / api_file

            if api_path.exists():
                return f"[{link_text}](api/{api_file})"
            else:
                # Try to find similar API file
                api_dir = DOCS_DIR / "api"
                if api_dir.exists():
                    for existing_file in api_dir.glob("*.md"):
                        if (
                            api_file.replace("-", "_") == existing_file.name
                            or api_file.replace("_", "-") == existing_file.name
                        ):
                            return f"[{link_text}](api/{existing_file.name})"

                # Return original if no match found
                return match.group(0)

        content = re.sub(api_link_pattern, update_api_link, content)
        return content

    def _update_service_port_references(self, content: str) -> str:
        """Update service port references to match current configuration."""
        for service_name, config in SERVICE_MAPPING.items():
            port = config.get("port")
            if port:
                # Update port references for this service
                service_patterns = [
                    service_name,
                    service_name.replace("_", "-"),
                    service_name.replace("-", "_"),
                ]

                for pattern in service_patterns:
                    # Update localhost:XXXX references
                    old_port_pattern = rf"(localhost:|127\.0\.0\.1:)(\d{{4}})(\s*[#\s]*{re.escape(pattern)})"
                    content = re.sub(
                        old_port_pattern,
                        rf"\g<1>{port}\g<3>",
                        content,
                        flags=re.IGNORECASE,
                    )

        return content

    def _update_moved_file_references(self, content: str) -> str:
        """Update references to files that may have been moved."""
        # This would implement logic to detect and update references to moved files
        # For now, just return content unchanged
        return content

    def generate_enhanced_documentation(self) -> dict[str, Any]:
        """Generate and maintain all enhanced documentation."""
        print("📚 ACGS Enhanced Automated Documentation Generator")
        print("=" * 70)
        print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
        print(f"Repository: {REPO_ROOT}")
        print()

        start_time = time.time()

        # Initialize analyzers
        self.initialize_analyzers()

        results = {
            "generated_files": [],
            "updated_files": [],
            "fixed_references": [],
            "total_operations": 0,
            "generation_time": 0,
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

        # Generate missing API documentation
        print("📝 Generating missing API documentation...")
        generated_api_docs = self.generate_missing_api_documentation()
        results["generated_files"].extend(generated_api_docs)
        print(f"✅ Generated {len(generated_api_docs)} API documentation files")

        # Fix broken cross-references
        print("\n🔗 Fixing broken cross-references...")
        fixed_refs = self.fix_broken_cross_references()
        results["fixed_references"] = fixed_refs
        print(f"✅ Fixed {len(fixed_refs)} broken references")

        # Generate cross-reference index
        print("\n📊 Generating cross-reference index...")
        index_file = self.generate_cross_reference_index()
        results["generated_files"].append(index_file)
        print(f"✅ Generated cross-reference index: {index_file}")

        # Update documentation links
        print("\n🔄 Updating documentation links...")
        updated_links = self.update_documentation_links()
        results["updated_files"].extend(updated_links)
        print(f"✅ Updated {len(updated_links)} files with corrected links")

        # Calculate totals
        results["total_operations"] = (
            len(results["generated_files"])
            + len(results["updated_files"])
            + len(results["fixed_references"])
        )
        results["generation_time"] = time.time() - start_time

        print()
        print("=" * 70)
        print("📊 GENERATION SUMMARY")
        print("=" * 70)
        print(f"📄 Generated files: {len(results['generated_files'])}")
        print(f"📝 Updated files: {len(results['updated_files'])}")
        print(f"🔗 Fixed references: {len(results['fixed_references'])}")
        print(f"⏱️ Total time: {results['generation_time']:.2f} seconds")
        print(f"🔗 Constitutional Hash: {CONSTITUTIONAL_HASH}")

        if results["generated_files"]:
            print("\n📁 Generated files:")
            for file_path in results["generated_files"]:
                print(f"  - {file_path}")

        if results["updated_files"]:
            print("\n📝 Updated files:")
            for file_path in results["updated_files"][:10]:  # Show first 10
                print(f"  - {file_path}")
            if len(results["updated_files"]) > 10:
                print(f"  ... and {len(results['updated_files']) - 10} more")

        return results


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="ACGS Enhanced Automated Documentation Generator"
    )
    parser.add_argument(
        "--api-docs-only", action="store_true", help="Generate only API documentation"
    )
    parser.add_argument(
        "--fix-links-only", action="store_true", help="Fix only broken links"
    )
    parser.add_argument("--output", type=Path, help="Output file for generation report")

    args = parser.parse_args()

    generator = EnhancedAutoDocGenerator()

    if args.api_docs_only:
        generated_docs = generator.generate_missing_api_documentation()
        print(f"\n✅ Generated {len(generated_docs)} API documentation files")
    elif args.fix_links_only:
        fixed_refs = generator.fix_broken_cross_references()
        updated_files = generator.update_documentation_links()
        print(
            f"\n✅ Fixed {len(fixed_refs)} references and updated"
            f" {len(updated_files)} files"
        )
    else:
        results = generator.generate_enhanced_documentation()

        if args.output:
            with open(args.output, "w") as f:
                json.dump(results, f, indent=2)
            print(f"\n📊 Results saved to: {args.output}")

    print("\n🎉 Documentation generation completed!")
    print(f"🔗 Constitutional Hash: {CONSTITUTIONAL_HASH}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
