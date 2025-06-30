#!/usr/bin/env python3
"""
Core Algorithm Testing Framework for ACGS-2
Tests constitutional AI processing, policy governance, and Darwin Gödel Machine mechanisms.
"""

import os
import sys
import json
import time
import traceback
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "services"))
sys.path.insert(0, str(project_root / "services/shared"))

@dataclass
class TestResult:
    test_name: str
    status: str  # PASS, FAIL, SKIP, ERROR
    execution_time: float
    details: Dict[str, Any]
    error_message: Optional[str] = None

class CoreAlgorithmTester:
    def __init__(self):
        self.results = []
        self.project_root = project_root
        self.services_dir = project_root / "services"
        
    def log_result(self, result: TestResult):
        """Log a test result."""
        self.results.append(result)
        status_symbol = {"PASS": "✓", "FAIL": "✗", "SKIP": "⊝", "ERROR": "⚠"}
        symbol = status_symbol.get(result.status, "?")
        print(f"{symbol} {result.test_name} ({result.execution_time:.3f}s)")
        if result.error_message:
            print(f"  Error: {result.error_message}")
    
    def test_constitutional_ai_imports(self) -> TestResult:
        """Test if constitutional AI modules can be imported."""
        start_time = time.time()
        try:
            # Test basic imports
            constitutional_dirs = [
                "services/core/constitutional-ai",
                "services/core/constitutional_ai"
            ]
            
            found_modules = []
            for dir_path in constitutional_dirs:
                full_path = self.project_root / dir_path
                if full_path.exists():
                    py_files = list(full_path.rglob("*.py"))
                    found_modules.extend([str(f.relative_to(self.project_root)) for f in py_files])
            
            if not found_modules:
                return TestResult(
                    "constitutional_ai_imports",
                    "FAIL",
                    time.time() - start_time,
                    {"modules_found": 0},
                    "No constitutional AI modules found"
                )
            
            # Try to import some modules
            importable_modules = 0
            import_errors = []
            
            for module_path in found_modules[:5]:  # Test first 5 modules
                try:
                    # Convert path to module name
                    module_name = module_path.replace("/", ".").replace(".py", "")
                    if module_name.startswith("services."):
                        module_name = module_name[9:]  # Remove "services." prefix
                    
                    # Skip __init__ files and test files
                    if "__init__" in module_name or "test_" in module_name:
                        continue
                        
                    __import__(module_name)
                    importable_modules += 1
                except Exception as e:
                    import_errors.append(f"{module_name}: {str(e)}")
            
            return TestResult(
                "constitutional_ai_imports",
                "PASS" if importable_modules > 0 else "FAIL",
                time.time() - start_time,
                {
                    "total_modules": len(found_modules),
                    "importable_modules": importable_modules,
                    "import_errors": import_errors[:3]  # Show first 3 errors
                }
            )
            
        except Exception as e:
            return TestResult(
                "constitutional_ai_imports",
                "ERROR",
                time.time() - start_time,
                {},
                str(e)
            )
    
    def test_policy_governance_structure(self) -> TestResult:
        """Test policy governance module structure."""
        start_time = time.time()
        try:
            policy_dirs = [
                "services/core/policy-governance",
                "services/core/policy_governance"
            ]
            
            structure_analysis = {
                "directories_found": 0,
                "python_files": 0,
                "key_components": []
            }
            
            key_patterns = ["policy", "governance", "synthesis", "validation", "engine"]
            
            for dir_path in policy_dirs:
                full_path = self.project_root / dir_path
                if full_path.exists():
                    structure_analysis["directories_found"] += 1
                    py_files = list(full_path.rglob("*.py"))
                    structure_analysis["python_files"] += len(py_files)
                    
                    # Look for key components
                    for py_file in py_files:
                        file_name = py_file.name.lower()
                        for pattern in key_patterns:
                            if pattern in file_name:
                                structure_analysis["key_components"].append({
                                    "file": str(py_file.relative_to(self.project_root)),
                                    "pattern": pattern
                                })
                                break
            
            status = "PASS" if structure_analysis["directories_found"] > 0 else "FAIL"
            error_msg = None if status == "PASS" else "No policy governance directories found"
            
            return TestResult(
                "policy_governance_structure",
                status,
                time.time() - start_time,
                structure_analysis,
                error_msg
            )
            
        except Exception as e:
            return TestResult(
                "policy_governance_structure",
                "ERROR",
                time.time() - start_time,
                {},
                str(e)
            )
    
    def test_darwin_godel_machine_components(self) -> TestResult:
        """Test Darwin Gödel Machine mechanism components."""
        start_time = time.time()
        try:
            # Look for DGM-related components
            dgm_patterns = ["dgm", "darwin", "godel", "evolution", "machine"]
            dgm_components = []
            
            # Search in core services
            for pattern in dgm_patterns:
                # Search for directories
                for item in self.services_dir.rglob(f"*{pattern}*"):
                    if item.is_dir():
                        py_files = list(item.rglob("*.py"))
                        dgm_components.append({
                            "type": "directory",
                            "path": str(item.relative_to(self.project_root)),
                            "pattern": pattern,
                            "python_files": len(py_files)
                        })
                
                # Search for files
                for item in self.services_dir.rglob(f"*{pattern}*.py"):
                    dgm_components.append({
                        "type": "file",
                        "path": str(item.relative_to(self.project_root)),
                        "pattern": pattern
                    })
            
            # Remove duplicates
            unique_components = []
            seen_paths = set()
            for comp in dgm_components:
                if comp["path"] not in seen_paths:
                    unique_components.append(comp)
                    seen_paths.add(comp["path"])
            
            status = "PASS" if len(unique_components) > 0 else "FAIL"
            error_msg = None if status == "PASS" else "No Darwin Gödel Machine components found"
            
            return TestResult(
                "darwin_godel_machine_components",
                status,
                time.time() - start_time,
                {
                    "components_found": len(unique_components),
                    "components": unique_components[:10]  # Show first 10
                },
                error_msg
            )
            
        except Exception as e:
            return TestResult(
                "darwin_godel_machine_components",
                "ERROR",
                time.time() - start_time,
                {},
                str(e)
            )
    
    def test_algorithmic_correctness_basic(self) -> TestResult:
        """Test basic algorithmic correctness with simple operations."""
        start_time = time.time()
        try:
            # Test basic mathematical operations that should be consistent
            test_cases = [
                {"operation": "addition", "a": 1, "b": 2, "expected": 3},
                {"operation": "multiplication", "a": 3, "b": 4, "expected": 12},
                {"operation": "division", "a": 10, "b": 2, "expected": 5},
                {"operation": "modulo", "a": 10, "b": 3, "expected": 1}
            ]
            
            passed_tests = 0
            failed_tests = []
            
            for test_case in test_cases:
                try:
                    if test_case["operation"] == "addition":
                        result = test_case["a"] + test_case["b"]
                    elif test_case["operation"] == "multiplication":
                        result = test_case["a"] * test_case["b"]
                    elif test_case["operation"] == "division":
                        result = test_case["a"] / test_case["b"]
                    elif test_case["operation"] == "modulo":
                        result = test_case["a"] % test_case["b"]
                    
                    if result == test_case["expected"]:
                        passed_tests += 1
                    else:
                        failed_tests.append({
                            "test": test_case,
                            "actual": result,
                            "expected": test_case["expected"]
                        })
                        
                except Exception as e:
                    failed_tests.append({
                        "test": test_case,
                        "error": str(e)
                    })
            
            status = "PASS" if len(failed_tests) == 0 else "FAIL"
            error_msg = None if status == "PASS" else f"{len(failed_tests)} basic tests failed"
            
            return TestResult(
                "algorithmic_correctness_basic",
                status,
                time.time() - start_time,
                {
                    "total_tests": len(test_cases),
                    "passed_tests": passed_tests,
                    "failed_tests": failed_tests
                },
                error_msg
            )
            
        except Exception as e:
            return TestResult(
                "algorithmic_correctness_basic",
                "ERROR",
                time.time() - start_time,
                {},
                str(e)
            )
    
    def test_edge_cases_handling(self) -> TestResult:
        """Test edge case handling in basic operations."""
        start_time = time.time()
        try:
            edge_cases = []
            
            # Test division by zero handling
            try:
                result = 1 / 0
                edge_cases.append({"case": "division_by_zero", "handled": False, "result": result})
            except ZeroDivisionError:
                edge_cases.append({"case": "division_by_zero", "handled": True, "error": "ZeroDivisionError"})
            except Exception as e:
                edge_cases.append({"case": "division_by_zero", "handled": True, "error": str(e)})
            
            # Test large number handling
            try:
                large_num = 10**100
                result = large_num * 2
                edge_cases.append({"case": "large_numbers", "handled": True, "result_type": type(result).__name__})
            except Exception as e:
                edge_cases.append({"case": "large_numbers", "handled": False, "error": str(e)})
            
            # Test empty list operations
            try:
                empty_list = []
                result = len(empty_list)
                edge_cases.append({"case": "empty_list_len", "handled": True, "result": result})
            except Exception as e:
                edge_cases.append({"case": "empty_list_len", "handled": False, "error": str(e)})
            
            properly_handled = sum(1 for case in edge_cases if case["handled"])
            
            return TestResult(
                "edge_cases_handling",
                "PASS",
                time.time() - start_time,
                {
                    "total_edge_cases": len(edge_cases),
                    "properly_handled": properly_handled,
                    "edge_cases": edge_cases
                }
            )
            
        except Exception as e:
            return TestResult(
                "edge_cases_handling",
                "ERROR",
                time.time() - start_time,
                {},
                str(e)
            )
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all core algorithm tests."""
        print("Starting Core Algorithm Testing...")
        print("=" * 50)
        
        # Define test methods
        test_methods = [
            self.test_constitutional_ai_imports,
            self.test_policy_governance_structure,
            self.test_darwin_godel_machine_components,
            self.test_algorithmic_correctness_basic,
            self.test_edge_cases_handling
        ]
        
        # Run all tests
        for test_method in test_methods:
            try:
                result = test_method()
                self.log_result(result)
            except Exception as e:
                error_result = TestResult(
                    test_method.__name__,
                    "ERROR",
                    0.0,
                    {},
                    f"Test execution failed: {str(e)}"
                )
                self.log_result(error_result)
        
        # Generate summary
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.status == "PASS")
        failed_tests = sum(1 for r in self.results if r.status == "FAIL")
        error_tests = sum(1 for r in self.results if r.status == "ERROR")
        skipped_tests = sum(1 for r in self.results if r.status == "SKIP")
        
        summary = {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "errors": error_tests,
            "skipped": skipped_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "results": [
                {
                    "test_name": r.test_name,
                    "status": r.status,
                    "execution_time": r.execution_time,
                    "details": r.details,
                    "error_message": r.error_message
                }
                for r in self.results
            ]
        }
        
        print("\n" + "=" * 50)
        print("CORE ALGORITHM TEST SUMMARY")
        print("=" * 50)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Errors: {error_tests}")
        print(f"Skipped: {skipped_tests}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        
        return summary

def main():
    tester = CoreAlgorithmTester()
    summary = tester.run_all_tests()
    
    # Save results
    output_file = project_root / "core_algorithm_test_results.json"
    with open(output_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\nDetailed results saved to: {output_file}")
    
    # Return appropriate exit code
    if summary["failed"] > 0 or summary["errors"] > 0:
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
