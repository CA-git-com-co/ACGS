#!/usr/bin/env python3
"""
ACGS-2 Test Coverage Analysis
HASH-OK:cdd01ef066bc6cf2

Analyzes test coverage across the ACGS-2 codebase and identifies gaps
in constitutional compliance testing and integration tests.
"""

import os
import re
import json
import time
from pathlib import Path
from typing import Dict, List, Set, Any
from dataclasses import dataclass
from collections import defaultdict

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

@dataclass
class TestCoverageMetrics:
    total_python_files: int
    total_test_files: int
    test_coverage_ratio: float
    constitutional_test_files: int
    integration_test_files: int
    performance_test_files: int
    unit_test_files: int
    missing_test_areas: List[str]
    constitutional_compliance_coverage: float

@dataclass
class ServiceTestAnalysis:
    service_name: str
    service_path: str
    python_files: int
    test_files: int
    has_constitutional_tests: bool
    has_integration_tests: bool
    has_performance_tests: bool
    test_coverage_estimate: float
    missing_test_types: List[str]

class ACGSTestCoverageAnalyzer:
    def __init__(self, project_root: str = "/home/dislove/ACGS-2"):
        self.project_root = Path(project_root)
        self.services_dir = self.project_root / "services"
        self.tests_dir = self.project_root / "tests"
        
        # Patterns for different test types
        self.constitutional_patterns = [
            r"constitutional",
            r"compliance",
            r"hash.*validation",
            r"cdd01ef066bc6cf2"
        ]
        
        self.integration_patterns = [
            r"integration",
            r"e2e",
            r"end.*to.*end",
            r"api.*test",
            r"service.*test"
        ]
        
        self.performance_patterns = [
            r"performance",
            r"load.*test",
            r"stress.*test",
            r"benchmark",
            r"latency",
            r"throughput"
        ]

    def analyze_file_content(self, file_path: Path) -> Dict[str, bool]:
        """Analyze file content for different test types."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            return {
                "has_constitutional": any(re.search(pattern, content, re.IGNORECASE) 
                                        for pattern in self.constitutional_patterns),
                "has_integration": any(re.search(pattern, content, re.IGNORECASE) 
                                     for pattern in self.integration_patterns),
                "has_performance": any(re.search(pattern, content, re.IGNORECASE) 
                                     for pattern in self.performance_patterns),
                "has_constitutional_hash": CONSTITUTIONAL_HASH in content
            }
        except Exception:
            return {
                "has_constitutional": False,
                "has_integration": False,
                "has_performance": False,
                "has_constitutional_hash": False
            }

    def find_python_files(self, directory: Path) -> List[Path]:
        """Find all Python files in a directory."""
        if not directory.exists():
            return []
        
        python_files = []
        for file_path in directory.rglob("*.py"):
            # Skip __pycache__ and .venv directories
            if "__pycache__" in str(file_path) or ".venv" in str(file_path):
                continue
            python_files.append(file_path)
        
        return python_files

    def find_test_files(self, directory: Path) -> List[Path]:
        """Find all test files in a directory."""
        if not directory.exists():
            return []
        
        test_files = []
        for file_path in directory.rglob("*.py"):
            # Skip __pycache__ and .venv directories
            if "__pycache__" in str(file_path) or ".venv" in str(file_path):
                continue
            
            # Check if it's a test file
            if (file_path.name.startswith("test_") or 
                file_path.name.endswith("_test.py") or
                "test" in str(file_path).lower()):
                test_files.append(file_path)
        
        return test_files

    def analyze_service_coverage(self, service_path: Path) -> ServiceTestAnalysis:
        """Analyze test coverage for a specific service."""
        service_name = service_path.name
        
        # Find Python files in service
        python_files = self.find_python_files(service_path)
        
        # Find test files in service
        test_files = self.find_test_files(service_path)
        
        # Analyze test types
        has_constitutional = False
        has_integration = False
        has_performance = False
        
        for test_file in test_files:
            analysis = self.analyze_file_content(test_file)
            if analysis["has_constitutional"]:
                has_constitutional = True
            if analysis["has_integration"]:
                has_integration = True
            if analysis["has_performance"]:
                has_performance = True
        
        # Estimate coverage (simple heuristic)
        test_coverage_estimate = min(len(test_files) / max(len(python_files), 1), 1.0)
        
        # Identify missing test types
        missing_test_types = []
        if not has_constitutional:
            missing_test_types.append("constitutional_compliance")
        if not has_integration:
            missing_test_types.append("integration")
        if not has_performance:
            missing_test_types.append("performance")
        
        return ServiceTestAnalysis(
            service_name=service_name,
            service_path=str(service_path),
            python_files=len(python_files),
            test_files=len(test_files),
            has_constitutional_tests=has_constitutional,
            has_integration_tests=has_integration,
            has_performance_tests=has_performance,
            test_coverage_estimate=test_coverage_estimate,
            missing_test_types=missing_test_types
        )

    def analyze_overall_coverage(self) -> TestCoverageMetrics:
        """Analyze overall test coverage across the project."""
        print("🔍 Analyzing ACGS-2 Test Coverage...")
        print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
        print()
        
        # Find all Python files
        all_python_files = self.find_python_files(self.project_root)
        
        # Find all test files
        all_test_files = self.find_test_files(self.project_root)
        
        # Analyze test types
        constitutional_tests = 0
        integration_tests = 0
        performance_tests = 0
        constitutional_hash_coverage = 0
        
        for test_file in all_test_files:
            analysis = self.analyze_file_content(test_file)
            if analysis["has_constitutional"]:
                constitutional_tests += 1
            if analysis["has_integration"]:
                integration_tests += 1
            if analysis["has_performance"]:
                performance_tests += 1
            if analysis["has_constitutional_hash"]:
                constitutional_hash_coverage += 1
        
        # Calculate metrics
        test_coverage_ratio = len(all_test_files) / max(len(all_python_files), 1)
        constitutional_compliance_coverage = constitutional_hash_coverage / max(len(all_test_files), 1)
        
        # Identify missing test areas
        missing_areas = []
        if constitutional_tests < 10:  # Arbitrary threshold
            missing_areas.append("insufficient_constitutional_tests")
        if integration_tests < 5:
            missing_areas.append("insufficient_integration_tests")
        if performance_tests < 3:
            missing_areas.append("insufficient_performance_tests")
        if constitutional_compliance_coverage < 0.5:
            missing_areas.append("low_constitutional_hash_coverage")
        
        return TestCoverageMetrics(
            total_python_files=len(all_python_files),
            total_test_files=len(all_test_files),
            test_coverage_ratio=test_coverage_ratio,
            constitutional_test_files=constitutional_tests,
            integration_test_files=integration_tests,
            performance_test_files=performance_tests,
            unit_test_files=len(all_test_files) - constitutional_tests - integration_tests - performance_tests,
            missing_test_areas=missing_areas,
            constitutional_compliance_coverage=constitutional_compliance_coverage
        )

    def generate_coverage_report(self) -> Dict[str, Any]:
        """Generate comprehensive test coverage report."""
        print("=" * 80)
        print("🎯 ACGS-2 Test Coverage Analysis Report")
        print("=" * 80)
        
        # Overall coverage analysis
        overall_metrics = self.analyze_overall_coverage()
        
        print(f"📊 Overall Coverage Metrics:")
        print(f"   Total Python Files: {overall_metrics.total_python_files:,}")
        print(f"   Total Test Files: {overall_metrics.total_test_files:,}")
        print(f"   Test Coverage Ratio: {overall_metrics.test_coverage_ratio:.1%}")
        print(f"   Constitutional Tests: {overall_metrics.constitutional_test_files}")
        print(f"   Integration Tests: {overall_metrics.integration_test_files}")
        print(f"   Performance Tests: {overall_metrics.performance_test_files}")
        print(f"   Constitutional Hash Coverage: {overall_metrics.constitutional_compliance_coverage:.1%}")
        print()
        
        # Service-level analysis
        print("🏗️ Service-Level Coverage Analysis:")
        service_analyses = []
        
        if self.services_dir.exists():
            for service_dir in self.services_dir.iterdir():
                if service_dir.is_dir() and not service_dir.name.startswith('.'):
                    # Check subdirectories for actual services
                    for subdir in service_dir.iterdir():
                        if subdir.is_dir() and not subdir.name.startswith('.'):
                            analysis = self.analyze_service_coverage(subdir)
                            service_analyses.append(analysis)
                            
                            coverage_icon = "✅" if analysis.test_coverage_estimate >= 0.8 else "⚠️" if analysis.test_coverage_estimate >= 0.5 else "❌"
                            constitutional_icon = "✅" if analysis.has_constitutional_tests else "❌"
                            
                            print(f"   {coverage_icon} {analysis.service_name}:")
                            print(f"      Files: {analysis.python_files} Python, {analysis.test_files} Tests")
                            print(f"      Coverage Estimate: {analysis.test_coverage_estimate:.1%}")
                            print(f"      Constitutional Tests: {constitutional_icon}")
                            if analysis.missing_test_types:
                                print(f"      Missing: {', '.join(analysis.missing_test_types)}")
                            print()
        
        # Coverage assessment
        coverage_status = "EXCELLENT" if overall_metrics.test_coverage_ratio >= 0.8 else \
                         "GOOD" if overall_metrics.test_coverage_ratio >= 0.6 else \
                         "NEEDS_IMPROVEMENT"
        
        constitutional_status = "EXCELLENT" if overall_metrics.constitutional_compliance_coverage >= 0.8 else \
                               "GOOD" if overall_metrics.constitutional_compliance_coverage >= 0.5 else \
                               "CRITICAL"
        
        print("📋 Coverage Assessment:")
        print(f"   Overall Test Coverage: {coverage_status}")
        print(f"   Constitutional Compliance Coverage: {constitutional_status}")
        
        if overall_metrics.missing_test_areas:
            print(f"   Areas Needing Attention: {', '.join(overall_metrics.missing_test_areas)}")
        
        print(f"\n🎯 Constitutional Hash Validation: {CONSTITUTIONAL_HASH}")
        
        return {
            "timestamp": time.time(),
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "overall_metrics": {
                "total_python_files": overall_metrics.total_python_files,
                "total_test_files": overall_metrics.total_test_files,
                "test_coverage_ratio": overall_metrics.test_coverage_ratio,
                "constitutional_test_files": overall_metrics.constitutional_test_files,
                "integration_test_files": overall_metrics.integration_test_files,
                "performance_test_files": overall_metrics.performance_test_files,
                "constitutional_compliance_coverage": overall_metrics.constitutional_compliance_coverage,
                "missing_test_areas": overall_metrics.missing_test_areas
            },
            "service_analyses": [
                {
                    "service_name": analysis.service_name,
                    "python_files": analysis.python_files,
                    "test_files": analysis.test_files,
                    "test_coverage_estimate": analysis.test_coverage_estimate,
                    "has_constitutional_tests": analysis.has_constitutional_tests,
                    "has_integration_tests": analysis.has_integration_tests,
                    "has_performance_tests": analysis.has_performance_tests,
                    "missing_test_types": analysis.missing_test_types
                } for analysis in service_analyses
            ],
            "coverage_status": coverage_status,
            "constitutional_status": constitutional_status
        }

def main():
    """Main execution function."""
    analyzer = ACGSTestCoverageAnalyzer()
    
    try:
        report = analyzer.generate_coverage_report()
        
        # Save report
        report_file = f"test_coverage_report_{int(time.time())}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        print(f"HASH-OK:{CONSTITUTIONAL_HASH}")
        
        # Return appropriate exit code
        overall_good = report["overall_metrics"]["test_coverage_ratio"] >= 0.6
        constitutional_good = report["overall_metrics"]["constitutional_compliance_coverage"] >= 0.5
        
        return 0 if overall_good and constitutional_good else 1
        
    except Exception as e:
        print(f"❌ Test coverage analysis failed: {e}")
        return 1

if __name__ == "__main__":
    exit(exit_code := main())
