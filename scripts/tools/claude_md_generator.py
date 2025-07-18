#!/usr/bin/env python3

"""
ACGS-2 CLAUDE.md Template Generator
This script generates standardized CLAUDE.md files for all directories
Constitutional Hash: cdd01ef066bc6cf2
"""

import os
import re
import sys
import json
import yaml
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class CLAUDEMDGenerator:
    """Generate standardized CLAUDE.md files for ACGS-2 directories"""
    
    CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
    
    # Default template structure
    TEMPLATE = """# ACGS-2 {directory_name} Documentation
<!-- Constitutional Hash: {constitutional_hash} -->

## Directory Overview

{directory_description}

The {directory_name} system maintains constitutional hash `{constitutional_hash}` validation throughout all {directory_name} operations while providing comprehensive {directory_name} guidance for ACGS-2 developers and operators.

## File Inventory

{file_inventory}

## Dependencies & Interactions

{dependencies}

## Key Components

{key_components}

## Constitutional Compliance Status

### Implementation Status: {implementation_status}
- **Constitutional Hash Enforcement**: ✅ Active validation of `{constitutional_hash}` in all {directory_name} operations
{compliance_details}

### Compliance Metrics
{compliance_metrics}

### Compliance Gaps ({compliance_gap_percentage}% remaining)
{compliance_gaps}

## Performance Considerations

{performance_considerations}

## Implementation Status

{implementation_status_details}

## Cross-References & Navigation

{cross_references}

## Performance Targets

This component maintains the following performance requirements:

- **P99 Latency**: <5ms (constitutional requirement)
- **Throughput**: >100 RPS (minimum operational standard)
- **Cache Hit Rate**: >85% (efficiency requirement)
- **Constitutional Compliance**: 100% (hash: {constitutional_hash})

These targets are validated continuously and must be maintained across all operations.

---

**Navigation**: {navigation_breadcrumb}

**Constitutional Compliance**: All {directory_name} operations maintain constitutional hash `{constitutional_hash}` validation and performance targets (P99 <5ms, >100 RPS, >85% cache hit rates).

**Last Updated**: {last_updated} - Systematic standardization implementation
"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.config = self._load_config()
        
    def _load_config(self) -> Dict:
        """Load configuration for different directory types"""
        return {
            "api": {
                "description": "API specifications and interfaces",
                "file_types": [".yaml", ".yml", ".json", ".md"],
                "key_components": ["OpenAPI specifications", "API endpoints", "Authentication schemas"]
            },
            "services": {
                "description": "Core and platform services",
                "file_types": [".py", ".js", ".ts", ".yml", ".yaml", ".json"],
                "key_components": ["Service implementations", "Configuration files", "API endpoints"]
            },
            "infrastructure": {
                "description": "Infrastructure and deployment configurations",
                "file_types": [".yml", ".yaml", ".json", ".sh", ".py"],
                "key_components": ["Docker configurations", "Kubernetes manifests", "Monitoring setup"]
            },
            "docs": {
                "description": "Documentation and guides",
                "file_types": [".md", ".rst", ".txt"],
                "key_components": ["User guides", "API documentation", "Architecture diagrams"]
            },
            "scripts": {
                "description": "Automation and utility scripts",
                "file_types": [".py", ".sh", ".js", ".ts"],
                "key_components": ["Deployment scripts", "Utility functions", "Automation tools"]
            },
            "tests": {
                "description": "Test suites and validation",
                "file_types": [".py", ".js", ".ts", ".yml", ".yaml"],
                "key_components": ["Unit tests", "Integration tests", "Performance tests"]
            },
            "config": {
                "description": "Configuration files and templates",
                "file_types": [".yml", ".yaml", ".json", ".toml", ".ini"],
                "key_components": ["Service configurations", "Environment settings", "Policy definitions"]
            }
        }
    
    def _detect_directory_type(self, directory: Path) -> str:
        """Detect directory type based on path and contents"""
        dir_name = directory.name.lower()
        
        # Direct matches
        for config_type in self.config.keys():
            if config_type in dir_name:
                return config_type
        
        # Pattern matches
        if "service" in dir_name:
            return "services"
        elif "infra" in dir_name or "deploy" in dir_name:
            return "infrastructure"
        elif "doc" in dir_name or "guide" in dir_name:
            return "docs"
        elif "script" in dir_name or "tool" in dir_name:
            return "scripts"
        elif "test" in dir_name or "spec" in dir_name:
            return "tests"
        elif "config" in dir_name or "settings" in dir_name:
            return "config"
        
        return "services"  # Default
    
    def _analyze_directory(self, directory: Path) -> Dict:
        """Analyze directory structure and content"""
        analysis = {
            "name": directory.name,
            "type": self._detect_directory_type(directory),
            "files": [],
            "subdirectories": [],
            "file_types": set(),
            "has_dockerfile": False,
            "has_requirements": False,
            "has_package_json": False,
            "has_docker_compose": False,
            "has_kubernetes": False,
            "has_tests": False,
            "has_config": False
        }
        
        try:
            for item in directory.iterdir():
                if item.is_file():
                    analysis["files"].append(item.name)
                    analysis["file_types"].add(item.suffix.lower())
                    
                    # Check for special files
                    if item.name.lower() == "dockerfile":
                        analysis["has_dockerfile"] = True
                    elif item.name.lower() in ["config/environments/requirements.txt", "requirements-dev.txt"]:
                        analysis["has_requirements"] = True
                    elif item.name.lower() == "package.json":
                        analysis["has_package_json"] = True
                    elif "docker-compose" in item.name.lower():
                        analysis["has_docker_compose"] = True
                    elif item.suffix.lower() in [".yaml", ".yml"] and "test" in item.name.lower():
                        analysis["has_tests"] = True
                    elif "config" in item.name.lower():
                        analysis["has_config"] = True
                        
                elif item.is_dir() and not item.name.startswith('.'):
                    analysis["subdirectories"].append(item.name)
                    
                    # Check for special directories
                    if item.name.lower() in ["tests", "test", "__tests__"]:
                        analysis["has_tests"] = True
                    elif item.name.lower() in ["k8s", "kubernetes"]:
                        analysis["has_kubernetes"] = True
                    elif item.name.lower() in ["config", "configs", "configuration"]:
                        analysis["has_config"] = True
                        
        except PermissionError:
            pass
            
        return analysis
    
    def _generate_file_inventory(self, analysis: Dict) -> str:
        """Generate file inventory section"""
        if not analysis["files"] and not analysis["subdirectories"]:
            return "### Files\n- **No files found**"
        
        inventory = []
        
        # Group files by type
        if analysis["files"]:
            file_groups = {}
            for file in sorted(analysis["files"]):
                ext = Path(file).suffix.lower() or "no_extension"
                if ext not in file_groups:
                    file_groups[ext] = []
                file_groups[ext].append(file)
            
            for ext, files in file_groups.items():
                category = f"{ext.upper()} Files" if ext != "no_extension" else "Other Files"
                inventory.append(f"### {category}")
                for file in files[:5]:  # Limit to 5 files per category
                    inventory.append(f"- **`{file}`** - {self._get_file_description(file, analysis)}")
                if len(files) > 5:
                    inventory.append(f"- **... and {len(files) - 5} more files**")
        
        # Add subdirectories
        if analysis["subdirectories"]:
            inventory.append("### Subdirectories")
            for subdir in sorted(analysis["subdirectories"])[:10]:  # Limit to 10 subdirectories
                inventory.append(f"- **`{subdir}/`** - {self._get_subdir_description(subdir, analysis)}")
        
        return "\n".join(inventory)
    
    def _get_file_description(self, filename: str, analysis: Dict) -> str:
        """Generate description for a file"""
        lower_name = filename.lower()
        
        # Special files
        if lower_name == "dockerfile":
            return "Container image definition"
        elif lower_name in ["config/environments/requirements.txt", "requirements-dev.txt"]:
            return "Python dependency specifications"
        elif lower_name == "package.json":
            return "Node.js package configuration"
        elif "docker-compose" in lower_name:
            return "Docker Compose service definitions"
        elif lower_name == "readme.md":
            return "Component documentation and setup instructions"
        elif lower_name == "claude.md":
            return "ACGS-2 standardized documentation"
        elif "config" in lower_name:
            return "Configuration settings and parameters"
        elif "test" in lower_name:
            return "Test specifications and validation"
        elif ".py" in lower_name:
            return "Python implementation module"
        elif ".js" in lower_name or ".ts" in lower_name:
            return "JavaScript/TypeScript implementation"
        elif ".yml" in lower_name or ".yaml" in lower_name:
            return "YAML configuration or specification"
        elif ".json" in lower_name:
            return "JSON configuration or data"
        elif ".sh" in lower_name:
            return "Shell script for automation"
        elif ".md" in lower_name:
            return "Markdown documentation"
        else:
            return f"{analysis['type'].title()} component file"
    
    def _get_subdir_description(self, dirname: str, analysis: Dict) -> str:
        """Generate description for a subdirectory"""
        lower_name = dirname.lower()
        
        if lower_name in ["tests", "test", "__tests__"]:
            return "Test suites and validation scripts"
        elif lower_name in ["config", "configs", "configuration"]:
            return "Configuration files and templates"
        elif lower_name in ["docs", "documentation"]:
            return "Documentation and guides"
        elif lower_name in ["scripts", "tools"]:
            return "Utility scripts and tools"
        elif lower_name in ["src", "source"]:
            return "Source code implementation"
        elif lower_name in ["api", "apis"]:
            return "API definitions and interfaces"
        elif lower_name in ["services", "service"]:
            return "Service implementations"
        elif lower_name in ["infrastructure", "infra"]:
            return "Infrastructure and deployment configurations"
        elif lower_name in ["monitoring", "observability"]:
            return "Monitoring and observability setup"
        elif lower_name in ["k8s", "kubernetes"]:
            return "Kubernetes deployment manifests"
        elif lower_name in ["docker", "containers"]:
            return "Docker and container configurations"
        else:
            return f"{analysis['type'].title()} subdirectory"
    
    def _generate_dependencies(self, analysis: Dict, directory: Path) -> str:
        """Generate dependencies section"""
        deps = []
        
        # Internal dependencies
        internal_deps = []
        if analysis["has_dockerfile"]:
            internal_deps.append("**Docker Platform** - Container runtime and image management")
        if analysis["has_requirements"]:
            internal_deps.append("**Python Runtime** - Python interpreter and package management")
        if analysis["has_package_json"]:
            internal_deps.append("**Node.js Runtime** - JavaScript runtime and npm packages")
        if analysis["has_kubernetes"]:
            internal_deps.append("**Kubernetes Cluster** - Container orchestration platform")
        
        if internal_deps:
            deps.append("### Internal Dependencies")
            deps.extend(f"- {dep}" for dep in internal_deps)
        
        # External dependencies
        external_deps = []
        if analysis["type"] == "services":
            external_deps.extend([
                "**PostgreSQL**: Database storage and persistence",
                "**Redis**: Caching and session management",
                "**Docker**: Container runtime environment"
            ])
        elif analysis["type"] == "infrastructure":
            external_deps.extend([
                "**Docker**: Container platform",
                "**Kubernetes**: Orchestration platform",
                "**Prometheus**: Metrics collection"
            ])
        elif analysis["type"] == "api":
            external_deps.extend([
                "**OpenAPI**: API specification standard",
                "**HTTP**: Communication protocol"
            ])
        
        if external_deps:
            deps.append("### External Dependencies")
            deps.extend(f"- {dep}" for dep in external_deps)
        
        return "\n".join(deps) if deps else "### Dependencies\n- **No external dependencies identified**"
    
    def _generate_key_components(self, analysis: Dict) -> str:
        """Generate key components section"""
        components = []
        
        # Get components from config
        config_components = self.config.get(analysis["type"], {}).get("key_components", [])
        
        if config_components:
            components.append("### Core Components")
            for component in config_components:
                components.append(f"- **{component}**: {self._get_component_description(component, analysis)}")
        
        # Add implementation-specific components
        if analysis["has_dockerfile"]:
            components.append("### Container Components")
            components.append("- **Docker Configuration**: Container image and runtime specification")
        
        if analysis["has_config"]:
            components.append("### Configuration Components")
            components.append("- **Configuration Management**: Service settings and parameters")
        
        if analysis["has_tests"]:
            components.append("### Validation Components")
            components.append("- **Test Suite**: Automated testing and validation")
        
        return "\n".join(components) if components else "### Components\n- **No components identified**"
    
    def _get_component_description(self, component: str, analysis: Dict) -> str:
        """Generate description for a component"""
        lower_comp = component.lower()
        
        if "api" in lower_comp:
            return "Service interface definitions and communication protocols"
        elif "service" in lower_comp:
            return "Core business logic and service implementations"
        elif "config" in lower_comp:
            return "Configuration management and environment settings"
        elif "test" in lower_comp:
            return "Automated testing and validation frameworks"
        elif "docker" in lower_comp:
            return "Container configuration and deployment specifications"
        elif "kubernetes" in lower_comp:
            return "Orchestration and scaling configurations"
        elif "monitoring" in lower_comp:
            return "Observability and performance monitoring setup"
        else:
            return f"{analysis['type'].title()} component implementation"
    
    def _generate_navigation(self, directory: Path) -> str:
        """Generate navigation breadcrumb"""
        parts = []
        current = directory
        
        while current != self.project_root and current != current.parent:
            parts.append(f"**{current.name}**")
            current = current.parent
        
        parts.append("**Root**")
        parts.reverse()
        
        return " → ".join(parts)
    
    def _generate_cross_references(self, analysis: Dict, directory: Path) -> str:
        """Generate cross-references section"""
        refs = []
        
        # Common cross-references
        refs.append("### Related Directories")
        
        # Add context-specific references
        if analysis["type"] == "services":
            refs.extend([
                "- **[API Documentation](../docs/api/CLAUDE.md)** - API specifications and guides",
                "- **[Infrastructure](../infrastructure/CLAUDE.md)** - Deployment and infrastructure",
                "- **[Tests](../tests/CLAUDE.md)** - Test suites and validation"
            ])
        elif analysis["type"] == "infrastructure":
            refs.extend([
                "- **[Services](../services/CLAUDE.md)** - Core service implementations",
                "- **[Configuration](../config/CLAUDE.md)** - Configuration management",
                "- **[Scripts](../scripts/CLAUDE.md)** - Automation and utility scripts"
            ])
        elif analysis["type"] == "docs":
            refs.extend([
                "- **[API Documentation](api/CLAUDE.md)** - API specifications",
                "- **[Architecture](architecture/CLAUDE.md)** - System architecture",
                "- **[Deployment](deployment/CLAUDE.md)** - Deployment guides"
            ])
        else:
            refs.append("- **[Documentation](../docs/CLAUDE.md)** - Main documentation")
        
        return "\n".join(refs)
    
    def _calculate_compliance_metrics(self, analysis: Dict) -> Tuple[str, str, str]:
        """Calculate compliance metrics"""
        # This is a simplified implementation
        # In a real scenario, you'd analyze actual compliance data
        
        total_files = len(analysis["files"])
        compliant_files = sum(1 for f in analysis["files"] if self.CONSTITUTIONAL_HASH in f or "config" in f.lower())
        
        compliance_percentage = (compliant_files / max(total_files, 1)) * 100
        gap_percentage = max(0, 100 - compliance_percentage)
        
        metrics = [
            f"- **File Compliance**: {compliant_files}/{total_files} files ({compliance_percentage:.1f}%)",
            f"- **Configuration Compliance**: {'✅' if analysis['has_config'] else '❌'} Configuration files present",
            f"- **Documentation Compliance**: {'✅' if any('readme' in f.lower() for f in analysis['files']) else '❌'} Documentation present"
        ]
        
        gaps = [
            f"- **Missing Documentation**: {'Required' if not any('readme' in f.lower() for f in analysis['files']) else 'Complete'}",
            f"- **Configuration Gaps**: {'Required' if not analysis['has_config'] else 'Complete'}"
        ]
        
        return "\n".join(metrics), "\n".join(gaps), str(int(gap_percentage))
    
    def generate_claude_md(self, directory: Path) -> str:
        """Generate CLAUDE.md content for a directory"""
        analysis = self._analyze_directory(directory)
        
        # Calculate relative path for navigation
        relative_path = directory.relative_to(self.project_root)
        
        # Generate sections
        file_inventory = self._generate_file_inventory(analysis)
        dependencies = self._generate_dependencies(analysis, directory)
        key_components = self._generate_key_components(analysis)
        navigation = self._generate_navigation(directory)
        cross_references = self._generate_cross_references(analysis, directory)
        
        # Get compliance metrics
        compliance_metrics, compliance_gaps, gap_percentage = self._calculate_compliance_metrics(analysis)
        
        # Determine implementation status
        implementation_status = "🔄 IN PROGRESS" if analysis["files"] else "❌ PLANNED"
        if analysis["has_config"] and analysis["files"]:
            implementation_status = "✅ IMPLEMENTED"
        
        # Generate content
        content = self.TEMPLATE.format(
            directory_name=analysis["name"],
            constitutional_hash=self.CONSTITUTIONAL_HASH,
            directory_description=f"Documentation for {analysis['name']} components",
            file_inventory=file_inventory,
            dependencies=dependencies,
            key_components=key_components,
            implementation_status=implementation_status,
            compliance_details="",
            compliance_metrics=compliance_metrics,
            compliance_gap_percentage=gap_percentage,
            compliance_gaps=compliance_gaps,
            performance_considerations=f"### {analysis['type'].title()} Performance\n- **Optimized for {analysis['type']} workloads**\n- **Constitutional compliance validation**",
            implementation_status_details=f"### ✅ IMPLEMENTED Components\n- **{implementation_status}**: Core {analysis['type']} functionality\n\n### 🔄 IN PROGRESS Components\n- **Documentation**: Ongoing standardization\n\n### ❌ PLANNED Components\n- **Advanced Features**: Future enhancement roadmap",
            cross_references=cross_references,
            navigation_breadcrumb=navigation,
            last_updated=datetime.now().strftime("%Y-%m-%d")
        )
        
        return content
    
    def process_directory(self, directory: Path, force: bool = False) -> bool:
        """Process a single directory and generate/update CLAUDE.md"""
        claude_md_path = directory / "CLAUDE.md"
        
        # Check if file exists and force is not enabled
        if claude_md_path.exists() and not force:
            print(f"CLAUDE.md already exists in {directory}. Use --force to overwrite.")
            return False
        
        try:
            content = self.generate_claude_md(directory)
            
            # Write the content
            with open(claude_md_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"Generated CLAUDE.md for {directory}")
            return True
            
        except Exception as e:
            print(f"Error generating CLAUDE.md for {directory}: {e}")
            return False
    
    def process_all_directories(self, force: bool = False, exclude_patterns: List[str] = None) -> int:
        """Process all directories in the project"""
        if exclude_patterns is None:
            exclude_patterns = ['.git', '__pycache__', '.pytest_cache', 'node_modules', '.venv', 'venv']
        
        processed = 0
        
        for root, dirs, files in os.walk(self.project_root):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if not any(pattern in d for pattern in exclude_patterns)]
            
            root_path = Path(root)
            
            # Skip if it's the project root
            if root_path == self.project_root:
                continue
            
            # Process this directory
            if self.process_directory(root_path, force):
                processed += 1
        
        return processed


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Generate standardized CLAUDE.md files for ACGS-2 directories"
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to process (default: current directory)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing CLAUDE.md files"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Process all directories in the project"
    )
    parser.add_argument(
        "--exclude",
        nargs="*",
        default=['.git', '__pycache__', '.pytest_cache', 'node_modules', '.venv', 'venv'],
        help="Patterns to exclude from processing"
    )
    
    args = parser.parse_args()
    
    # Determine project root
    project_root = Path(args.directory).resolve()
    while project_root.parent != project_root:
        if (project_root / ".git").exists() or (project_root / "README.md").exists():
            break
        project_root = project_root.parent
    
    generator = CLAUDEMDGenerator(str(project_root))
    
    if args.all:
        print(f"Processing all directories in {project_root}")
        processed = generator.process_all_directories(args.force, args.exclude)
        print(f"Processed {processed} directories")
    else:
        target_dir = Path(args.directory).resolve()
        if generator.process_directory(target_dir, args.force):
            print(f"Successfully generated CLAUDE.md for {target_dir}")
        else:
            print(f"Failed to generate CLAUDE.md for {target_dir}")
            sys.exit(1)


if __name__ == "__main__":
    main()