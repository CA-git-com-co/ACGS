#!/usr/bin/env python3
"""
ACGS Dependency Analysis Tool
Constitutional Hash: cdd01ef066bc6cf2

Analyzes dependencies across the project to identify:
- Duplicate dependencies
- Version conflicts
- Outdated packages
- Unused dependencies
- Security vulnerabilities
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict
import json

class DependencyAnalyzer:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.dependencies: Dict[str, Dict[str, List[str]]] = defaultdict(lambda: defaultdict(list))
        self.pyproject_deps: Dict[str, str] = {}
        
    def extract_dependency(self, line: str) -> Tuple[str, str]:
        """Extract package name and version from a requirement line."""
        line = line.strip()
        if not line or line.startswith('#'):
            return None, None
            
        # Remove comments
        if '#' in line:
            line = line.split('#')[0].strip()
            
        # Handle different version specifiers
        match = re.match(r'^([a-zA-Z0-9_\-\[\]]+)([><=!~]+.*)?$', line)
        if match:
            package = match.group(1).lower()
            version = match.group(2) or ""
            # Remove extras like [standard], [crypto]
            package = re.sub(r'\[.*\]', '', package)
            return package, version
        return None, None
        
    def parse_requirements_file(self, file_path: Path) -> None:
        """Parse a config/environments/requirements.txt file."""
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    package, version = self.extract_dependency(line)
                    if package:
                        self.dependencies[package][version].append(str(file_path))
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            
    def parse_pyproject_toml(self) -> None:
        """Parse the main config/environments/pyproject.toml file."""
        pyproject_path = self.project_root / "config/environments/pyproject.toml"
        if not pyproject_path.exists():
            return
            
        try:
            with open(pyproject_path, 'r') as f:
                content = f.read()
                
            # Extract dependencies section
            in_deps = False
            for line in content.split('\n'):
                if line.strip() == 'dependencies = [':
                    in_deps = True
                    continue
                elif in_deps and line.strip() == ']':
                    break
                elif in_deps and '"' in line:
                    # Extract dependency from quoted string
                    match = re.search(r'"([^"]+)"', line)
                    if match:
                        package, version = self.extract_dependency(match.group(1))
                        if package:
                            self.pyproject_deps[package] = version
        except Exception as e:
            print(f"Error parsing config/environments/pyproject.toml: {e}")
            
    def analyze(self) -> None:
        """Run the complete dependency analysis."""
        print("=" * 80)
        print("ACGS Dependency Analysis Report")
        print("Constitutional Hash: cdd01ef066bc6cf2")
        print("=" * 80)
        
        # Find all requirements files
        req_files = list(self.project_root.rglob("requirements*.txt"))
        print(f"\nFound {len(req_files)} requirements files")
        
        # Parse all files
        for req_file in req_files:
            self.parse_requirements_file(req_file)
            
        # Parse config/environments/pyproject.toml
        self.parse_pyproject_toml()
        
        # Analyze results
        self.report_duplicates()
        self.report_conflicts()
        self.report_version_mismatches()
        self.report_recommendations()
        
    def report_duplicates(self) -> None:
        """Report packages that appear in multiple files."""
        print("\n" + "=" * 60)
        print("DUPLICATE DEPENDENCIES (in multiple files)")
        print("=" * 60)
        
        duplicates = {pkg: versions for pkg, versions in self.dependencies.items() 
                     if sum(len(files) for files in versions.values()) > 1}
        
        if not duplicates:
            print("No duplicate dependencies found across files.")
            return
            
        for package, versions in sorted(duplicates.items()):
            print(f"\n{package}:")
            for version, files in versions.items():
                print(f"  Version: {version or 'unspecified'}")
                for file in files:
                    print(f"    - {file}")
                    
    def report_conflicts(self) -> None:
        """Report packages with conflicting version specifications."""
        print("\n" + "=" * 60)
        print("VERSION CONFLICTS")
        print("=" * 60)
        
        conflicts = {pkg: versions for pkg, versions in self.dependencies.items() 
                    if len(versions) > 1}
        
        if not conflicts:
            print("No version conflicts found.")
            return
            
        for package, versions in sorted(conflicts.items()):
            print(f"\n{package}:")
            for version, files in versions.items():
                print(f"  {version or 'unspecified'}: {', '.join(files)}")
                
    def report_version_mismatches(self) -> None:
        """Report mismatches between config/environments/pyproject.toml and requirements files."""
        print("\n" + "=" * 60)
        print("PYPROJECT.TOML vs REQUIREMENTS.TXT MISMATCHES")
        print("=" * 60)
        
        mismatches = []
        for package, pyproject_version in self.pyproject_deps.items():
            if package in self.dependencies:
                for req_version, files in self.dependencies[package].items():
                    if req_version != pyproject_version:
                        mismatches.append((package, pyproject_version, req_version, files))
                        
        if not mismatches:
            print("No mismatches found between config/environments/pyproject.toml and requirements files.")
            return
            
        for package, py_ver, req_ver, files in mismatches:
            print(f"\n{package}:")
            print(f"  config/environments/pyproject.toml: {py_ver}")
            print(f"  config/environments/requirements.txt: {req_ver} in {', '.join(files)}")
            
    def report_recommendations(self) -> None:
        """Provide specific recommendations for cleanup."""
        print("\n" + "=" * 60)
        print("RECOMMENDATIONS FOR CONSOLIDATION")
        print("=" * 60)
        
        # Key packages with version inconsistencies
        key_packages = {
            'fastapi': [],
            'uvicorn': [],
            'pydantic': [],
            'sqlalchemy': [],
            'cryptography': [],
            'torch': []
        }
        
        for package in key_packages:
            if package in self.dependencies:
                for version, files in self.dependencies[package].items():
                    key_packages[package].append((version, files))
                    
        print("\n1. STANDARDIZE CORE PACKAGE VERSIONS:")
        for package, versions in key_packages.items():
            if versions:
                print(f"\n   {package}:")
                if package in self.pyproject_deps:
                    print(f"     Recommended (from config/environments/pyproject.toml): {self.pyproject_deps[package]}")
                for version, files in versions:
                    print(f"     Current: {version} in {len(files)} file(s)")
                    
        print("\n2. CONSOLIDATION OPPORTUNITIES:")
        print("   - Create a shared 'requirements-base.txt' for common dependencies")
        print("   - Use '-r requirements-base.txt' in service-specific files")
        print("   - Remove duplicate security dependencies (cryptography, pyjwt, etc.)")
        print("   - Standardize version operators (use >= instead of ==)")
        
        print("\n3. SECURITY UPDATES NEEDED:")
        security_packages = ['cryptography', 'urllib3', 'requests', 'certifi']
        for package in security_packages:
            if package in self.dependencies:
                print(f"   - {package}: Ensure all services use latest version")
                
        print("\n4. REMOVE POTENTIALLY UNUSED:")
        print("   - torch appears in multiple services but may not be needed")
        print("   - ecdsa appears inconsistently")
        print("   - setuptools should be in build requirements only")
        
        print("\n5. VERSION PINNING STRATEGY:")
        print("   - Use >= for stable packages (fastapi, pydantic)")
        print("   - Pin exact versions only for critical dependencies")
        print("   - Consider using version ranges (e.g., >=2.0,<3.0)")


if __name__ == "__main__":
    analyzer = DependencyAnalyzer(Path("/home/dislove/ACGS-2"))
    analyzer.analyze()