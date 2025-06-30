#!/usr/bin/env python3
"""
Comprehensive test coverage analysis for ACGS-2 system.
Analyzes test gaps, identifies critical components, and provides recommendations.
"""

import os
import sys
import json
import ast
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple

class TestCoverageAnalyzer:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.services_dir = project_root / "services"
        self.tests_dir = project_root / "tests"
        self.coverage_data = {}
        self.test_files = {}
        self.service_files = {}
        
    def analyze_service_structure(self) -> Dict:
        """Analyze the service directory structure and identify key components."""
        print("Analyzing service structure...")
        
        structure = {
            "core_services": [],
            "shared_components": [],
            "platform_services": [],
            "total_python_files": 0,
            "critical_components": []
        }
        
        # Analyze core services
        core_dir = self.services_dir / "core"
        if core_dir.exists():
            for item in core_dir.iterdir():
                if item.is_dir():
                    py_files = list(item.rglob("*.py"))
                    structure["core_services"].append({
                        "name": item.name,
                        "path": str(item),
                        "python_files": len(py_files),
                        "files": [str(f.relative_to(self.project_root)) for f in py_files]
                    })
                    structure["total_python_files"] += len(py_files)
        
        # Analyze shared components
        shared_dir = self.services_dir / "shared"
        if shared_dir.exists():
            py_files = list(shared_dir.glob("*.py"))
            structure["shared_components"] = [str(f.relative_to(self.project_root)) for f in py_files]
            structure["total_python_files"] += len(py_files)
        
        # Analyze platform services
        platform_dir = self.services_dir / "platform"
        if platform_dir.exists():
            for item in platform_dir.iterdir():
                if item.is_dir():
                    py_files = list(item.rglob("*.py"))
                    structure["platform_services"].append({
                        "name": item.name,
                        "path": str(item),
                        "python_files": len(py_files),
                        "files": [str(f.relative_to(self.project_root)) for f in py_files]
                    })
                    structure["total_python_files"] += len(py_files)
        
        # Identify critical components based on naming patterns
        critical_patterns = [
            "constitutional", "wina", "policy", "governance", "auth", 
            "security", "cache", "database", "monitoring"
        ]
        
        for service in structure["core_services"]:
            for pattern in critical_patterns:
                if pattern in service["name"].lower():
                    structure["critical_components"].append(service)
                    break
        
        return structure
    
    def analyze_test_structure(self) -> Dict:
        """Analyze the test directory structure and categorize tests."""
        print("Analyzing test structure...")
        
        test_structure = {
            "unit_tests": [],
            "integration_tests": [],
            "e2e_tests": [],
            "performance_tests": [],
            "security_tests": [],
            "total_test_files": 0
        }
        
        test_categories = {
            "unit": "unit_tests",
            "integration": "integration_tests", 
            "e2e": "e2e_tests",
            "performance": "performance_tests",
            "security": "security_tests"
        }
        
        for category, key in test_categories.items():
            test_dir = self.tests_dir / category
            if test_dir.exists():
                test_files = list(test_dir.rglob("test_*.py"))
                test_structure[key] = [str(f.relative_to(self.project_root)) for f in test_files]
                test_structure["total_test_files"] += len(test_files)
        
        return test_structure
    
    def identify_coverage_gaps(self, service_structure: Dict, test_structure: Dict) -> Dict:
        """Identify gaps in test coverage by comparing services to tests."""
        print("Identifying coverage gaps...")
        
        gaps = {
            "untested_services": [],
            "critical_gaps": [],
            "missing_test_categories": [],
            "coverage_percentage": 0
        }
        
        # Create a set of all service names for comparison
        service_names = set()
        for service in service_structure["core_services"]:
            service_names.add(service["name"])
        for service in service_structure["platform_services"]:
            service_names.add(service["name"])
        
        # Extract test targets from test file names
        tested_components = set()
        for test_files in test_structure.values():
            if isinstance(test_files, list):
                for test_file in test_files:
                    # Extract component name from test file
                    filename = Path(test_file).name
                    if filename.startswith("test_"):
                        component = filename[5:].replace(".py", "").replace("_", "-")
                        tested_components.add(component)
        
        # Find untested services
        for service_name in service_names:
            service_tested = False
            for tested in tested_components:
                if service_name in tested or tested in service_name:
                    service_tested = True
                    break
            if not service_tested:
                gaps["untested_services"].append(service_name)
        
        # Check critical components
        for critical_service in service_structure["critical_components"]:
            service_name = critical_service["name"]
            if service_name in gaps["untested_services"]:
                gaps["critical_gaps"].append(critical_service)
        
        # Calculate rough coverage percentage
        total_services = len(service_names)
        tested_services = total_services - len(gaps["untested_services"])
        gaps["coverage_percentage"] = (tested_services / total_services * 100) if total_services > 0 else 0
        
        return gaps
    
    def analyze_wina_components(self) -> Dict:
        """Specifically analyze WINA optimization components."""
        print("Analyzing WINA components...")
        
        wina_analysis = {
            "wina_files": [],
            "optimization_files": [],
            "performance_files": [],
            "test_coverage": {
                "wina_tests": [],
                "performance_tests": [],
                "optimization_tests": []
            }
        }
        
        # Find WINA-related files
        wina_patterns = ["wina", "optimization", "performance", "oversight"]
        
        for pattern in wina_patterns:
            # Search in services
            service_files = list(self.services_dir.rglob(f"*{pattern}*.py"))
            for f in service_files:
                if "wina" in pattern:
                    wina_analysis["wina_files"].append(str(f.relative_to(self.project_root)))
                elif "optimization" in pattern:
                    wina_analysis["optimization_files"].append(str(f.relative_to(self.project_root)))
                elif "performance" in pattern:
                    wina_analysis["performance_files"].append(str(f.relative_to(self.project_root)))
            
            # Search in tests
            test_files = list(self.tests_dir.rglob(f"*{pattern}*.py"))
            for f in test_files:
                if "wina" in pattern:
                    wina_analysis["test_coverage"]["wina_tests"].append(str(f.relative_to(self.project_root)))
                elif "optimization" in pattern:
                    wina_analysis["test_coverage"]["optimization_tests"].append(str(f.relative_to(self.project_root)))
                elif "performance" in pattern:
                    wina_analysis["test_coverage"]["performance_tests"].append(str(f.relative_to(self.project_root)))
        
        return wina_analysis
    
    def generate_recommendations(self, gaps: Dict, wina_analysis: Dict) -> List[str]:
        """Generate specific recommendations for improving test coverage."""
        recommendations = []
        
        # Critical gaps
        if gaps["critical_gaps"]:
            recommendations.append("CRITICAL: The following critical components lack test coverage:")
            for component in gaps["critical_gaps"]:
                recommendations.append(f"  - {component['name']} ({component['python_files']} files)")
        
        # WINA-specific recommendations
        wina_files_count = len(wina_analysis["wina_files"])
        wina_tests_count = len(wina_analysis["test_coverage"]["wina_tests"])
        
        if wina_files_count > 0 and wina_tests_count == 0:
            recommendations.append("CRITICAL: WINA optimization components have no test coverage")
        elif wina_tests_count < wina_files_count:
            recommendations.append(f"HIGH: WINA test coverage is incomplete ({wina_tests_count}/{wina_files_count} files)")
        
        # Performance testing
        perf_files_count = len(wina_analysis["performance_files"])
        perf_tests_count = len(wina_analysis["test_coverage"]["performance_tests"])
        
        if perf_files_count > 0 and perf_tests_count < 3:
            recommendations.append("HIGH: Insufficient performance testing for sub-5ms P99 latency requirements")
        
        # General coverage
        if gaps["coverage_percentage"] < 80:
            recommendations.append(f"MEDIUM: Overall test coverage is {gaps['coverage_percentage']:.1f}%, target is 80%")
        
        # Untested services
        if gaps["untested_services"]:
            recommendations.append("MEDIUM: The following services need test coverage:")
            for service in gaps["untested_services"][:5]:  # Show first 5
                recommendations.append(f"  - {service}")
            if len(gaps["untested_services"]) > 5:
                recommendations.append(f"  ... and {len(gaps['untested_services']) - 5} more")
        
        return recommendations
    
    def run_analysis(self) -> Dict:
        """Run the complete test coverage analysis."""
        print("Starting comprehensive test coverage analysis...")
        print("=" * 60)
        
        service_structure = self.analyze_service_structure()
        test_structure = self.analyze_test_structure()
        coverage_gaps = self.identify_coverage_gaps(service_structure, test_structure)
        wina_analysis = self.analyze_wina_components()
        recommendations = self.generate_recommendations(coverage_gaps, wina_analysis)
        
        analysis_result = {
            "service_structure": service_structure,
            "test_structure": test_structure,
            "coverage_gaps": coverage_gaps,
            "wina_analysis": wina_analysis,
            "recommendations": recommendations,
            "summary": {
                "total_services": len(service_structure["core_services"]) + len(service_structure["platform_services"]),
                "total_test_files": test_structure["total_test_files"],
                "coverage_percentage": coverage_gaps["coverage_percentage"],
                "critical_gaps": len(coverage_gaps["critical_gaps"]),
                "wina_coverage": len(wina_analysis["test_coverage"]["wina_tests"]) / max(len(wina_analysis["wina_files"]), 1) * 100
            }
        }
        
        return analysis_result

def main():
    project_root = Path(__file__).parent
    analyzer = TestCoverageAnalyzer(project_root)
    
    try:
        result = analyzer.run_analysis()
        
        # Print summary
        print("\n" + "=" * 60)
        print("TEST COVERAGE ANALYSIS SUMMARY")
        print("=" * 60)
        
        summary = result["summary"]
        print(f"Total Services: {summary['total_services']}")
        print(f"Total Test Files: {summary['total_test_files']}")
        print(f"Overall Coverage: {summary['coverage_percentage']:.1f}%")
        print(f"Critical Gaps: {summary['critical_gaps']}")
        print(f"WINA Coverage: {summary['wina_coverage']:.1f}%")
        
        print("\nRECOMMENDATIONS:")
        print("-" * 40)
        for i, rec in enumerate(result["recommendations"], 1):
            print(f"{i}. {rec}")
        
        # Save detailed results
        output_file = project_root / "test_coverage_analysis.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\nDetailed analysis saved to: {output_file}")
        
        return result
        
    except Exception as e:
        print(f"Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()
