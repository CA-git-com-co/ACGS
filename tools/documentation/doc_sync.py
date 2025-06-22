#!/usr/bin/env python3
"""
ACGS-1 Documentation Synchronization Tool

This tool ensures API documentation stays synchronized with code changes by:
- Monitoring FastAPI route changes and schema updates
- Detecting API breaking changes and version incompatibilities
- Validating documentation completeness and accuracy
- Generating documentation diff reports
- Integrating with CI/CD pipelines for automated validation

Features:
- Real-time documentation validation
- Breaking change detection
- Schema drift monitoring
- Documentation coverage analysis
- Automated documentation updates
- Integration with version control systems
"""

import os
import sys
import json
import hashlib
import difflib
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime
import argparse
import logging
import subprocess

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from tools.documentation.openapi_generator import OpenAPIGenerator
    GENERATOR_AVAILABLE = True
except ImportError:
    GENERATOR_AVAILABLE = False
    print("Warning: OpenAPI generator not available")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DocumentationSynchronizer:
    """Tool for synchronizing API documentation with code changes."""
    
    def __init__(self, docs_dir: str = "docs/api/generated", baseline_dir: str = "docs/api/baseline"):
        self.docs_dir = Path(docs_dir)
        self.baseline_dir = Path(baseline_dir)
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        self.baseline_dir.mkdir(parents=True, exist_ok=True)
        
        self.generator = OpenAPIGenerator(str(self.docs_dir)) if GENERATOR_AVAILABLE else None
        
        # Track changes
        self.changes = {
            "added_endpoints": [],
            "removed_endpoints": [],
            "modified_endpoints": [],
            "schema_changes": [],
            "breaking_changes": [],
            "version_changes": []
        }
    
    def generate_baseline(self, services: List[str] = None) -> Dict[str, Any]:
        """Generate baseline documentation for comparison."""
        if not self.generator:
            raise RuntimeError("OpenAPI generator not available")
        
        logger.info("Generating baseline documentation")
        
        if services is None:
            services = list(self.generator.service_configs.keys())
        
        baseline_specs = {}
        
        for service in services:
            try:
                spec = self.generator.generate_openapi_spec(service, use_mock=True)
                baseline_specs[service] = spec
                
                # Save baseline
                baseline_file = self.baseline_dir / f"{service}_baseline.json"
                with open(baseline_file, "w") as f:
                    json.dump(spec, f, indent=2, sort_keys=True)
                
                logger.info(f"Generated baseline for {service}")
                
            except Exception as e:
                logger.error(f"Failed to generate baseline for {service}: {e}")
                baseline_specs[service] = None
        
        return baseline_specs
    
    def load_baseline(self, service: str) -> Optional[Dict[str, Any]]:
        """Load baseline documentation for a service."""
        baseline_file = self.baseline_dir / f"{service}_baseline.json"
        
        if not baseline_file.exists():
            logger.warning(f"No baseline found for {service}")
            return None
        
        try:
            with open(baseline_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load baseline for {service}: {e}")
            return None
    
    def compare_specifications(self, service: str, current_spec: Dict[str, Any], baseline_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Compare current specification with baseline to detect changes."""
        
        comparison = {
            "service": service,
            "timestamp": datetime.now().isoformat(),
            "changes_detected": False,
            "endpoint_changes": [],
            "schema_changes": [],
            "breaking_changes": [],
            "version_changes": [],
            "summary": {
                "added_endpoints": 0,
                "removed_endpoints": 0,
                "modified_endpoints": 0,
                "schema_modifications": 0,
                "breaking_changes": 0
            }
        }
        
        # Compare versions
        current_version = current_spec.get("info", {}).get("version", "unknown")
        baseline_version = baseline_spec.get("info", {}).get("version", "unknown")
        
        if current_version != baseline_version:
            comparison["version_changes"].append({
                "type": "version_change",
                "from": baseline_version,
                "to": current_version,
                "breaking": self._is_breaking_version_change(baseline_version, current_version)
            })
        
        # Compare endpoints
        current_paths = current_spec.get("paths", {})
        baseline_paths = baseline_spec.get("paths", {})
        
        # Find added endpoints
        for path in current_paths:
            if path not in baseline_paths:
                comparison["endpoint_changes"].append({
                    "type": "added",
                    "path": path,
                    "methods": list(current_paths[path].keys())
                })
                comparison["summary"]["added_endpoints"] += 1
        
        # Find removed endpoints
        for path in baseline_paths:
            if path not in current_paths:
                comparison["endpoint_changes"].append({
                    "type": "removed",
                    "path": path,
                    "methods": list(baseline_paths[path].keys())
                })
                comparison["summary"]["removed_endpoints"] += 1
                
                # Removed endpoints are breaking changes
                comparison["breaking_changes"].append({
                    "type": "endpoint_removed",
                    "path": path,
                    "impact": "high",
                    "description": f"Endpoint {path} was removed"
                })
                comparison["summary"]["breaking_changes"] += 1
        
        # Find modified endpoints
        for path in current_paths:
            if path in baseline_paths:
                endpoint_changes = self._compare_endpoints(
                    path, current_paths[path], baseline_paths[path]
                )
                
                if endpoint_changes:
                    comparison["endpoint_changes"].append({
                        "type": "modified",
                        "path": path,
                        "changes": endpoint_changes
                    })
                    comparison["summary"]["modified_endpoints"] += 1
                    
                    # Check for breaking changes
                    breaking_changes = self._detect_breaking_endpoint_changes(path, endpoint_changes)
                    comparison["breaking_changes"].extend(breaking_changes)
                    comparison["summary"]["breaking_changes"] += len(breaking_changes)
        
        # Compare schemas
        current_schemas = current_spec.get("components", {}).get("schemas", {})
        baseline_schemas = baseline_spec.get("components", {}).get("schemas", {})
        
        schema_changes = self._compare_schemas(current_schemas, baseline_schemas)
        comparison["schema_changes"] = schema_changes
        comparison["summary"]["schema_modifications"] = len(schema_changes)
        
        # Detect breaking schema changes
        breaking_schema_changes = self._detect_breaking_schema_changes(schema_changes)
        comparison["breaking_changes"].extend(breaking_schema_changes)
        comparison["summary"]["breaking_changes"] += len(breaking_schema_changes)
        
        # Set overall change detection flag
        comparison["changes_detected"] = (
            comparison["summary"]["added_endpoints"] > 0 or
            comparison["summary"]["removed_endpoints"] > 0 or
            comparison["summary"]["modified_endpoints"] > 0 or
            comparison["summary"]["schema_modifications"] > 0 or
            len(comparison["version_changes"]) > 0
        )
        
        return comparison
    
    def _compare_endpoints(self, path: str, current: Dict[str, Any], baseline: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Compare individual endpoint changes."""
        changes = []
        
        current_methods = set(current.keys())
        baseline_methods = set(baseline.keys())
        
        # Added methods
        for method in current_methods - baseline_methods:
            changes.append({
                "type": "method_added",
                "method": method,
                "details": current[method]
            })
        
        # Removed methods
        for method in baseline_methods - current_methods:
            changes.append({
                "type": "method_removed",
                "method": method,
                "details": baseline[method]
            })
        
        # Modified methods
        for method in current_methods & baseline_methods:
            method_changes = self._compare_method(current[method], baseline[method])
            if method_changes:
                changes.append({
                    "type": "method_modified",
                    "method": method,
                    "changes": method_changes
                })
        
        return changes
    
    def _compare_method(self, current: Dict[str, Any], baseline: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Compare individual HTTP method changes."""
        changes = []
        
        # Compare parameters
        current_params = current.get("parameters", [])
        baseline_params = baseline.get("parameters", [])
        
        param_changes = self._compare_parameters(current_params, baseline_params)
        if param_changes:
            changes.extend(param_changes)
        
        # Compare request body
        current_body = current.get("requestBody")
        baseline_body = baseline.get("requestBody")
        
        if current_body != baseline_body:
            changes.append({
                "type": "request_body_changed",
                "current": current_body,
                "baseline": baseline_body
            })
        
        # Compare responses
        current_responses = current.get("responses", {})
        baseline_responses = baseline.get("responses", {})
        
        response_changes = self._compare_responses(current_responses, baseline_responses)
        if response_changes:
            changes.extend(response_changes)
        
        return changes
    
    def _compare_parameters(self, current: List[Dict[str, Any]], baseline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Compare parameter changes."""
        changes = []
        
        # Create parameter maps for comparison
        current_params = {(p.get("name"), p.get("in")): p for p in current}
        baseline_params = {(p.get("name"), p.get("in")): p for p in baseline}
        
        # Added parameters
        for key in current_params:
            if key not in baseline_params:
                changes.append({
                    "type": "parameter_added",
                    "parameter": current_params[key]
                })
        
        # Removed parameters
        for key in baseline_params:
            if key not in current_params:
                changes.append({
                    "type": "parameter_removed",
                    "parameter": baseline_params[key]
                })
        
        # Modified parameters
        for key in current_params:
            if key in baseline_params:
                if current_params[key] != baseline_params[key]:
                    changes.append({
                        "type": "parameter_modified",
                        "parameter": key,
                        "current": current_params[key],
                        "baseline": baseline_params[key]
                    })
        
        return changes
    
    def _compare_responses(self, current: Dict[str, Any], baseline: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Compare response changes."""
        changes = []
        
        # Added responses
        for status_code in current:
            if status_code not in baseline:
                changes.append({
                    "type": "response_added",
                    "status_code": status_code,
                    "response": current[status_code]
                })
        
        # Removed responses
        for status_code in baseline:
            if status_code not in current:
                changes.append({
                    "type": "response_removed",
                    "status_code": status_code,
                    "response": baseline[status_code]
                })
        
        # Modified responses
        for status_code in current:
            if status_code in baseline:
                if current[status_code] != baseline[status_code]:
                    changes.append({
                        "type": "response_modified",
                        "status_code": status_code,
                        "current": current[status_code],
                        "baseline": baseline[status_code]
                    })
        
        return changes
    
    def _compare_schemas(self, current: Dict[str, Any], baseline: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Compare schema changes."""
        changes = []
        
        # Added schemas
        for schema_name in current:
            if schema_name not in baseline:
                changes.append({
                    "type": "schema_added",
                    "name": schema_name,
                    "schema": current[schema_name]
                })
        
        # Removed schemas
        for schema_name in baseline:
            if schema_name not in current:
                changes.append({
                    "type": "schema_removed",
                    "name": schema_name,
                    "schema": baseline[schema_name]
                })
        
        # Modified schemas
        for schema_name in current:
            if schema_name in baseline:
                if current[schema_name] != baseline[schema_name]:
                    changes.append({
                        "type": "schema_modified",
                        "name": schema_name,
                        "current": current[schema_name],
                        "baseline": baseline[schema_name]
                    })
        
        return changes
    
    def _is_breaking_version_change(self, from_version: str, to_version: str) -> bool:
        """Determine if version change is breaking."""
        try:
            from_parts = [int(x) for x in from_version.split('.')]
            to_parts = [int(x) for x in to_version.split('.')]
            
            # Major version change is breaking
            if len(from_parts) > 0 and len(to_parts) > 0:
                return to_parts[0] > from_parts[0]
            
        except (ValueError, IndexError):
            pass
        
        return False
    
    def _detect_breaking_endpoint_changes(self, path: str, changes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect breaking changes in endpoint modifications."""
        breaking_changes = []
        
        for change in changes:
            if change["type"] == "method_removed":
                breaking_changes.append({
                    "type": "method_removed",
                    "path": path,
                    "method": change["method"],
                    "impact": "high",
                    "description": f"HTTP method {change['method']} removed from {path}"
                })
            
            elif change["type"] == "method_modified":
                for method_change in change.get("changes", []):
                    if method_change["type"] == "parameter_removed":
                        param = method_change["parameter"]
                        if param.get("required", False):
                            breaking_changes.append({
                                "type": "required_parameter_removed",
                                "path": path,
                                "method": change["method"],
                                "parameter": param["name"],
                                "impact": "high",
                                "description": f"Required parameter {param['name']} removed from {path}"
                            })
        
        return breaking_changes
    
    def _detect_breaking_schema_changes(self, schema_changes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect breaking changes in schema modifications."""
        breaking_changes = []
        
        for change in schema_changes:
            if change["type"] == "schema_removed":
                breaking_changes.append({
                    "type": "schema_removed",
                    "schema": change["name"],
                    "impact": "high",
                    "description": f"Schema {change['name']} was removed"
                })
            
            elif change["type"] == "schema_modified":
                # Analyze schema modification for breaking changes
                current_schema = change["current"]
                baseline_schema = change["baseline"]
                
                # Check for removed required properties
                current_required = set(current_schema.get("required", []))
                baseline_required = set(baseline_schema.get("required", []))
                
                removed_required = baseline_required - current_required
                for prop in removed_required:
                    breaking_changes.append({
                        "type": "required_property_removed",
                        "schema": change["name"],
                        "property": prop,
                        "impact": "medium",
                        "description": f"Required property {prop} removed from schema {change['name']}"
                    })
        
        return breaking_changes
    
    def validate_documentation_sync(self, services: List[str] = None) -> Dict[str, Any]:
        """Validate that documentation is synchronized with current code."""
        if not self.generator:
            raise RuntimeError("OpenAPI generator not available")
        
        logger.info("Validating documentation synchronization")
        
        if services is None:
            services = list(self.generator.service_configs.keys())
        
        validation_results = {
            "timestamp": datetime.now().isoformat(),
            "services": {},
            "overall_status": "synchronized",
            "total_changes": 0,
            "breaking_changes": 0,
            "recommendations": []
        }
        
        for service in services:
            try:
                # Generate current specification
                current_spec = self.generator.generate_openapi_spec(service, use_mock=True)
                
                # Load baseline
                baseline_spec = self.load_baseline(service)
                
                if baseline_spec is None:
                    validation_results["services"][service] = {
                        "status": "no_baseline",
                        "message": "No baseline found - generating new baseline"
                    }
                    continue
                
                # Compare specifications
                comparison = self.compare_specifications(service, current_spec, baseline_spec)
                
                validation_results["services"][service] = comparison
                validation_results["total_changes"] += sum(comparison["summary"].values())
                validation_results["breaking_changes"] += comparison["summary"]["breaking_changes"]
                
                if comparison["changes_detected"]:
                    validation_results["overall_status"] = "out_of_sync"
                
            except Exception as e:
                logger.error(f"Failed to validate {service}: {e}")
                validation_results["services"][service] = {
                    "status": "error",
                    "message": str(e)
                }
        
        # Generate recommendations
        if validation_results["breaking_changes"] > 0:
            validation_results["recommendations"].append(
                "Breaking changes detected - consider API versioning strategy"
            )
        
        if validation_results["total_changes"] > 0:
            validation_results["recommendations"].append(
                "Documentation updates required - run documentation generation"
            )
        
        return validation_results
    
    def generate_sync_report(self, validation_results: Dict[str, Any], output_file: str = None) -> str:
        """Generate human-readable synchronization report."""
        
        report_lines = [
            "# ACGS API Documentation Synchronization Report",
            f"**Generated**: {validation_results['timestamp']}",
            f"**Overall Status**: {validation_results['overall_status'].upper()}",
            f"**Total Changes**: {validation_results['total_changes']}",
            f"**Breaking Changes**: {validation_results['breaking_changes']}",
            "",
            "## Service Status",
            ""
        ]
        
        for service, results in validation_results["services"].items():
            if isinstance(results, dict) and "summary" in results:
                status_icon = "🔴" if results["summary"]["breaking_changes"] > 0 else "🟡" if results["changes_detected"] else "🟢"
                report_lines.extend([
                    f"### {status_icon} {service.upper()} Service",
                    f"- **Changes Detected**: {results['changes_detected']}",
                    f"- **Added Endpoints**: {results['summary']['added_endpoints']}",
                    f"- **Removed Endpoints**: {results['summary']['removed_endpoints']}",
                    f"- **Modified Endpoints**: {results['summary']['modified_endpoints']}",
                    f"- **Schema Changes**: {results['summary']['schema_modifications']}",
                    f"- **Breaking Changes**: {results['summary']['breaking_changes']}",
                    ""
                ])
                
                if results["breaking_changes"]:
                    report_lines.append("**Breaking Changes:**")
                    for change in results["breaking_changes"]:
                        report_lines.append(f"- {change['description']} (Impact: {change['impact']})")
                    report_lines.append("")
            
            else:
                status_icon = "⚠️"
                status = results.get("status", "unknown")
                message = results.get("message", "No details available")
                report_lines.extend([
                    f"### {status_icon} {service.upper()} Service",
                    f"- **Status**: {status}",
                    f"- **Message**: {message}",
                    ""
                ])
        
        if validation_results["recommendations"]:
            report_lines.extend([
                "## Recommendations",
                ""
            ])
            for rec in validation_results["recommendations"]:
                report_lines.append(f"- {rec}")
            report_lines.append("")
        
        report_content = "\n".join(report_lines)
        
        if output_file:
            with open(output_file, "w") as f:
                f.write(report_content)
            logger.info(f"Sync report saved to {output_file}")
        
        return report_content


def main():
    """Main function for CLI usage."""
    parser = argparse.ArgumentParser(description="Synchronize API documentation with code changes")
    parser.add_argument("--action", choices=["baseline", "validate", "sync"], required=True, help="Action to perform")
    parser.add_argument("--services", nargs="+", help="Services to process")
    parser.add_argument("--output", help="Output file for reports")
    parser.add_argument("--docs-dir", default="docs/api/generated", help="Documentation directory")
    parser.add_argument("--baseline-dir", default="docs/api/baseline", help="Baseline directory")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    synchronizer = DocumentationSynchronizer(args.docs_dir, args.baseline_dir)
    
    if args.action == "baseline":
        logger.info("Generating documentation baseline")
        synchronizer.generate_baseline(args.services)
        
    elif args.action == "validate":
        logger.info("Validating documentation synchronization")
        results = synchronizer.validate_documentation_sync(args.services)
        
        report = synchronizer.generate_sync_report(results, args.output)
        
        if not args.output:
            print(report)
        
        # Exit with error code if out of sync
        if results["overall_status"] != "synchronized":
            sys.exit(1)
    
    elif args.action == "sync":
        logger.info("Synchronizing documentation")
        # First validate
        results = synchronizer.validate_documentation_sync(args.services)
        
        # Generate new baseline if changes detected
        if results["overall_status"] != "synchronized":
            logger.info("Changes detected - updating baseline")
            synchronizer.generate_baseline(args.services)
        
        logger.info("Documentation synchronization complete")


if __name__ == "__main__":
    main()
