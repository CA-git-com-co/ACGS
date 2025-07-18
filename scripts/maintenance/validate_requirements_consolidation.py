#!/usr/bin/env python3
"""
Validate requirements consolidation across ACGS services.
Constitutional Hash: cdd01ef066bc6cf2
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict
import sys

def find_requirements_files() -> List[Path]:
    """Find all config/environments/requirements.txt files in the project."""
    root = Path(__file__).parent.parent.parent
    requirements_files = []
    
    for pattern in ["**/requirements*.txt", "**/config/environments/requirements.txt"]:
        for file_path in root.glob(pattern):
            # Skip temporary and backup directories
            if any(skip in str(file_path) for skip in ["temp/", "backup-", "__pycache__", ".git"]):
                continue
            requirements_files.append(file_path)
    
    return sorted(requirements_files)

def parse_requirements(file_path: Path) -> Dict[str, str]:
    """Parse requirements file and return package->version mapping."""
    requirements = {}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip empty lines, comments, and include directives
                if not line or line.startswith('#') or line.startswith('-r'):
                    continue
                
                # Parse package and version constraint
                match = re.match(r'([a-zA-Z0-9_-]+[a-zA-Z0-9_.-]*)\s*([><=!~]+.*)?', line)
                if match:
                    package = match.group(1).lower()  # Normalize package names
                    version = match.group(2) or ""
                    requirements[package] = version
                else:
                    # Handle special cases like git URLs or local paths
                    if '://' in line or line.startswith('.'):
                        continue
                    print(f"Warning: Could not parse line {line_num} in {file_path}: {line}")
    
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    
    return requirements

def normalize_version(version: str) -> str:
    """Normalize version constraints for comparison."""
    if not version:
        return "any"
    
    # Remove extra whitespace and normalize operators
    version = version.strip()
    version = re.sub(r'\s+', '', version)
    
    return version

def compare_versions(version1: str, version2: str) -> str:
    """Compare two version constraints and return conflict type."""
    v1 = normalize_version(version1)
    v2 = normalize_version(version2)
    
    if v1 == v2:
        return "identical"
    
    # Extract version numbers for basic comparison
    v1_num = re.search(r'[\d.]+', v1)
    v2_num = re.search(r'[\d.]+', v2)
    
    if v1_num and v2_num:
        v1_version = v1_num.group()
        v2_version = v2_num.group()
        
        if v1_version == v2_version:
            return "same_version_different_constraint"
        else:
            return "different_version"
    
    return "complex_constraint"

def analyze_duplicates(all_packages: Dict[str, List[Tuple[str, str]]]) -> Dict:
    """Analyze duplicate packages and version conflicts."""
    analysis = {
        "total_packages": len(all_packages),
        "duplicate_packages": 0,
        "version_conflicts": 0,
        "packages": {}
    }
    
    for package, files in all_packages.items():
        if len(files) > 1:
            analysis["duplicate_packages"] += 1
            
            versions = [version for _, version in files]
            unique_versions = set(normalize_version(v) for v in versions)
            
            conflict_type = "none"
            if len(unique_versions) > 1:
                analysis["version_conflicts"] += 1
                conflict_type = "version_conflict"
            
            analysis["packages"][package] = {
                "files": files,
                "versions": versions,
                "unique_versions": list(unique_versions),
                "conflict_type": conflict_type,
                "file_count": len(files)
            }
    
    return analysis

def generate_recommendations(analysis: Dict) -> List[str]:
    """Generate specific recommendations for consolidation."""
    recommendations = []
    
    # High priority conflicts
    critical_packages = ["cryptography", "fastapi", "uvicorn", "pydantic", "sqlalchemy"]
    
    for package, data in analysis["packages"].items():
        if data["conflict_type"] == "version_conflict":
            if package in critical_packages:
                recommendations.append(f"CRITICAL: Resolve {package} version conflict - {data['versions']}")
            else:
                recommendations.append(f"HIGH: Resolve {package} version conflict - {data['versions']}")
    
    # Consolidation opportunities
    high_duplicate_packages = [
        (pkg, data) for pkg, data in analysis["packages"].items()
        if data["file_count"] >= 5 and data["conflict_type"] != "version_conflict"
    ]
    
    if high_duplicate_packages:
        recommendations.append(f"MEDIUM: Consider consolidating {len(high_duplicate_packages)} packages duplicated across 5+ files")
    
    return recommendations

def create_consolidation_plan(analysis: Dict) -> Dict:
    """Create a detailed consolidation plan."""
    plan = {
        "shared_requirements_updates": {},
        "service_migrations": [],
        "version_alignments": []
    }
    
    # Identify packages that should be in shared requirements
    common_packages = [
        (pkg, data) for pkg, data in analysis["packages"].items()
        if data["file_count"] >= 3
    ]
    
    for package, data in common_packages:
        if data["conflict_type"] == "version_conflict":
            # Find the highest version
            versions = [v for v in data["versions"] if v]
            if versions:
                recommended_version = max(versions, key=lambda x: x.replace(">=", "").replace("==", ""))
                plan["version_alignments"].append({
                    "package": package,
                    "current_versions": data["versions"],
                    "recommended_version": recommended_version,
                    "files_affected": [f[0] for f in data["files"]]
                })
    
    return plan

def main():
    """Main validation function."""
    print("ACGS Requirements Consolidation Validation")
    print("Constitutional Hash: cdd01ef066bc6cf2")
    print("=" * 50)
    
    # Find all requirements files
    files = find_requirements_files()
    print(f"\nFound {len(files)} requirements files")
    
    # Parse all requirements
    all_packages = defaultdict(list)
    
    for file_path in files:
        requirements = parse_requirements(file_path)
        relative_path = str(file_path.relative_to(Path(__file__).parent.parent.parent))
        
        for package, version in requirements.items():
            all_packages[package].append((relative_path, version))
    
    # Analyze duplicates and conflicts
    analysis = analyze_duplicates(all_packages)
    
    # Display results
    print(f"\n📊 Analysis Results:")
    print(f"  Total unique packages: {analysis['total_packages']}")
    print(f"  Packages with duplicates: {analysis['duplicate_packages']}")
    print(f"  Packages with version conflicts: {analysis['version_conflicts']}")
    
    if analysis['version_conflicts'] > 0:
        print(f"\n⚠️  Version Conflicts Found:")
        for package, data in analysis["packages"].items():
            if data["conflict_type"] == "version_conflict":
                print(f"  {package}:")
                for file_path, version in data["files"]:
                    print(f"    {file_path}: {version or 'any'}")
    
    # Show high-duplicate packages
    high_duplicates = [
        (pkg, data) for pkg, data in analysis["packages"].items()
        if data["file_count"] >= 5
    ]
    
    if high_duplicates:
        print(f"\n🔄 High Consolidation Opportunities ({len(high_duplicates)} packages):")
        for package, data in sorted(high_duplicates, key=lambda x: x[1]["file_count"], reverse=True):
            conflict_indicator = "⚠️" if data["conflict_type"] == "version_conflict" else "✅"
            print(f"  {conflict_indicator} {package}: {data['file_count']} files")
    
    # Generate recommendations
    recommendations = generate_recommendations(analysis)
    
    if recommendations:
        print(f"\n📋 Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
    
    # Create detailed plan
    plan = create_consolidation_plan(analysis)
    
    # Save detailed analysis to file
    output_file = Path(__file__).parent.parent.parent / "requirements_analysis.json"
    with open(output_file, 'w') as f:
        json.dump({
            "analysis": analysis,
            "recommendations": recommendations,
            "consolidation_plan": plan
        }, f, indent=2)
    
    print(f"\n💾 Detailed analysis saved to: {output_file}")
    
    # Return exit code based on conflicts
    if analysis['version_conflicts'] > 0:
        print(f"\n❌ Validation failed: {analysis['version_conflicts']} version conflicts found")
        return 1
    else:
        print(f"\n✅ Validation passed: No version conflicts found")
        return 0

if __name__ == "__main__":
    sys.exit(main())