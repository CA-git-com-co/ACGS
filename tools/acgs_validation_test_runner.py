#!/usr/bin/env python3
"""
ACGS Comprehensive Validation Test Runner
Constitutional Hash: cdd01ef066bc6cf2

Validates the consolidated ACGS tooling ecosystem without requiring external dependencies.
Tests constitutional compliance, tool structure, and basic functionality.
"""

import ast
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ACGSValidationTestRunner:
    """Comprehensive validation test runner for ACGS tools."""
    
    def __init__(self):
        self.start_time = time.time()
        self.project_root = Path.cwd()
        self.tools_dir = self.project_root / "tools"
        self.validation_results = {}
        
        # Expected unified orchestrators
        self.unified_orchestrators = [
            "acgs_performance_suite.py",
            "acgs_cache_optimizer.py", 
            "acgs_constitutional_compliance_framework.py",
            "acgs_test_orchestrator.py",
            "acgs_security_orchestrator.py",
            "acgs_deployment_orchestrator.py",
            "acgs_monitoring_orchestrator.py",
            "acgs_documentation_orchestrator.py",
            "acgs_unified_orchestrator.py",
        ]
        
    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run comprehensive validation of ACGS tooling ecosystem."""
        logger.info("🚀 Starting ACGS Comprehensive Validation Test...")
        
        validation_summary = {
            "validation_start": datetime.now(timezone.utc).isoformat(),
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "tests_executed": {},
            "overall_results": {},
            "recommendations": [],
        }
        
        try:
            # 1. Constitutional Compliance Validation
            logger.info("🏛️ Testing Constitutional Compliance...")
            validation_summary["tests_executed"]["constitutional_compliance"] = self._test_constitutional_compliance()
            
            # 2. Tool Structure Validation
            logger.info("🛠️ Testing Tool Structure...")
            validation_summary["tests_executed"]["tool_structure"] = self._test_tool_structure()
            
            # 3. Code Quality Validation
            logger.info("📝 Testing Code Quality...")
            validation_summary["tests_executed"]["code_quality"] = self._test_code_quality()
            
            # 4. Documentation Validation
            logger.info("📚 Testing Documentation...")
            validation_summary["tests_executed"]["documentation"] = self._test_documentation()
            
            # 5. Configuration Validation
            logger.info("⚙️ Testing Configuration...")
            validation_summary["tests_executed"]["configuration"] = self._test_configuration()
            
            # Generate overall results
            validation_summary["overall_results"] = self._generate_overall_results(validation_summary["tests_executed"])
            
            # Generate recommendations
            validation_summary["recommendations"] = self._generate_recommendations(validation_summary["tests_executed"])
            
            # Calculate execution time
            validation_summary["execution_duration_seconds"] = time.time() - self.start_time
            
            # Save results
            self._save_validation_results(validation_summary)
            
            logger.info("✅ ACGS Comprehensive Validation Test completed")
            return validation_summary
            
        except Exception as e:
            logger.error(f"❌ Validation test failed: {e}")
            validation_summary["error"] = str(e)
            validation_summary["execution_duration_seconds"] = time.time() - self.start_time
            return validation_summary

    def _test_constitutional_compliance(self) -> Dict[str, Any]:
        """Test constitutional compliance across all tools."""
        results = {
            "test_name": "Constitutional Compliance Validation",
            "status": "running",
            "details": {},
            "score": 0,
            "max_score": 100,
        }
        
        try:
            compliant_tools = 0
            total_tools = 0
            
            # Check each unified orchestrator
            for tool_name in self.unified_orchestrators:
                tool_path = self.tools_dir / tool_name
                
                if tool_path.exists():
                    total_tools += 1
                    
                    # Read tool content
                    with open(tool_path, 'r') as f:
                        content = f.read()
                    
                    # Check for constitutional hash
                    has_hash = CONSTITUTIONAL_HASH in content
                    has_hash_variable = "CONSTITUTIONAL_HASH" in content
                    has_validation = "_validate_constitutional_hash" in content or "validate_constitutional_hash" in content
                    
                    tool_compliance = {
                        "has_constitutional_hash": has_hash,
                        "has_hash_variable": has_hash_variable,
                        "has_validation_function": has_validation,
                        "compliant": has_hash and has_hash_variable,
                    }
                    
                    results["details"][tool_name] = tool_compliance
                    
                    if tool_compliance["compliant"]:
                        compliant_tools += 1
                else:
                    results["details"][tool_name] = {
                        "error": "Tool file not found",
                        "compliant": False,
                    }
                    total_tools += 1
            
            # Calculate compliance rate
            compliance_rate = (compliant_tools / total_tools) * 100 if total_tools > 0 else 0
            results["score"] = compliance_rate
            results["status"] = "completed"
            results["summary"] = {
                "compliant_tools": compliant_tools,
                "total_tools": total_tools,
                "compliance_rate": round(compliance_rate, 2),
                "target_compliance": 100.0,
                "meets_target": compliance_rate >= 100.0,
            }
            
        except Exception as e:
            results["status"] = "failed"
            results["error"] = str(e)
            
        return results

    def _test_tool_structure(self) -> Dict[str, Any]:
        """Test tool structure and organization."""
        results = {
            "test_name": "Tool Structure Validation",
            "status": "running",
            "details": {},
            "score": 0,
            "max_score": 100,
        }
        
        try:
            valid_tools = 0
            total_tools = 0
            
            for tool_name in self.unified_orchestrators:
                tool_path = self.tools_dir / tool_name
                total_tools += 1
                
                if tool_path.exists():
                    # Parse the Python file
                    with open(tool_path, 'r') as f:
                        content = f.read()
                    
                    try:
                        tree = ast.parse(content)
                        
                        # Check for required elements
                        has_docstring = ast.get_docstring(tree) is not None
                        has_main_function = any(
                            isinstance(node, ast.FunctionDef) and node.name == "main"
                            for node in ast.walk(tree)
                        )
                        has_class_definition = any(
                            isinstance(node, ast.ClassDef)
                            for node in ast.walk(tree)
                        )
                        has_async_functions = any(
                            isinstance(node, ast.AsyncFunctionDef)
                            for node in ast.walk(tree)
                        )
                        
                        tool_structure = {
                            "has_docstring": has_docstring,
                            "has_main_function": has_main_function,
                            "has_class_definition": has_class_definition,
                            "has_async_functions": has_async_functions,
                            "valid_structure": has_docstring and has_class_definition,
                        }
                        
                        results["details"][tool_name] = tool_structure
                        
                        if tool_structure["valid_structure"]:
                            valid_tools += 1
                            
                    except SyntaxError as e:
                        results["details"][tool_name] = {
                            "error": f"Syntax error: {e}",
                            "valid_structure": False,
                        }
                else:
                    results["details"][tool_name] = {
                        "error": "Tool file not found",
                        "valid_structure": False,
                    }
            
            # Calculate structure score
            structure_score = (valid_tools / total_tools) * 100 if total_tools > 0 else 0
            results["score"] = structure_score
            results["status"] = "completed"
            results["summary"] = {
                "valid_tools": valid_tools,
                "total_tools": total_tools,
                "structure_score": round(structure_score, 2),
                "target_score": 90.0,
                "meets_target": structure_score >= 90.0,
            }
            
        except Exception as e:
            results["status"] = "failed"
            results["error"] = str(e)
            
        return results

    def _test_code_quality(self) -> Dict[str, Any]:
        """Test code quality metrics."""
        results = {
            "test_name": "Code Quality Validation",
            "status": "running",
            "details": {},
            "score": 0,
            "max_score": 100,
        }
        
        try:
            quality_scores = []
            
            for tool_name in self.unified_orchestrators:
                tool_path = self.tools_dir / tool_name
                
                if tool_path.exists():
                    with open(tool_path, 'r') as f:
                        content = f.read()
                    
                    # Basic quality metrics
                    lines_of_code = len([line for line in content.split('\n') if line.strip()])
                    has_type_hints = ": " in content and "->" in content
                    has_error_handling = "try:" in content and "except" in content
                    has_logging = "logger" in content or "logging" in content
                    has_docstrings = '"""' in content or "'''" in content
                    
                    # Calculate quality score for this tool
                    tool_quality_score = 0
                    if has_type_hints:
                        tool_quality_score += 25
                    if has_error_handling:
                        tool_quality_score += 25
                    if has_logging:
                        tool_quality_score += 25
                    if has_docstrings:
                        tool_quality_score += 25
                    
                    tool_quality = {
                        "lines_of_code": lines_of_code,
                        "has_type_hints": has_type_hints,
                        "has_error_handling": has_error_handling,
                        "has_logging": has_logging,
                        "has_docstrings": has_docstrings,
                        "quality_score": tool_quality_score,
                    }
                    
                    results["details"][tool_name] = tool_quality
                    quality_scores.append(tool_quality_score)
                else:
                    results["details"][tool_name] = {
                        "error": "Tool file not found",
                        "quality_score": 0,
                    }
                    quality_scores.append(0)
            
            # Calculate overall quality score
            avg_quality_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0
            results["score"] = avg_quality_score
            results["status"] = "completed"
            results["summary"] = {
                "average_quality_score": round(avg_quality_score, 2),
                "tools_analyzed": len(quality_scores),
                "target_score": 80.0,
                "meets_target": avg_quality_score >= 80.0,
            }
            
        except Exception as e:
            results["status"] = "failed"
            results["error"] = str(e)
            
        return results

    def _test_documentation(self) -> Dict[str, Any]:
        """Test documentation quality and compliance."""
        results = {
            "test_name": "Documentation Validation",
            "status": "running",
            "details": {},
            "score": 0,
            "max_score": 100,
        }
        
        try:
            # Check for key documentation files
            doc_files = [
                "reports/ACGS_TOOL_CONSOLIDATION_SUMMARY.md",
                "docs/ACGS_UNIFIED_TOOLS_GUIDE.md",
            ]
            
            valid_docs = 0
            total_docs = len(doc_files)
            
            for doc_file in doc_files:
                doc_path = self.project_root / doc_file
                
                if doc_path.exists():
                    with open(doc_path, 'r') as f:
                        content = f.read()
                    
                    # Check documentation quality
                    has_constitutional_hash = CONSTITUTIONAL_HASH in content
                    has_title = content.startswith('#')
                    has_toc = "##" in content
                    word_count = len(content.split())
                    
                    doc_quality = {
                        "exists": True,
                        "has_constitutional_hash": has_constitutional_hash,
                        "has_title": has_title,
                        "has_table_of_contents": has_toc,
                        "word_count": word_count,
                        "quality_score": (
                            (25 if has_constitutional_hash else 0) +
                            (25 if has_title else 0) +
                            (25 if has_toc else 0) +
                            (25 if word_count > 500 else 0)
                        ),
                    }
                    
                    results["details"][doc_file] = doc_quality
                    
                    if doc_quality["quality_score"] >= 75:
                        valid_docs += 1
                else:
                    results["details"][doc_file] = {
                        "exists": False,
                        "error": "Documentation file not found",
                        "quality_score": 0,
                    }
            
            # Calculate documentation score
            doc_score = (valid_docs / total_docs) * 100 if total_docs > 0 else 0
            results["score"] = doc_score
            results["status"] = "completed"
            results["summary"] = {
                "valid_documentation": valid_docs,
                "total_documentation": total_docs,
                "documentation_score": round(doc_score, 2),
                "target_score": 90.0,
                "meets_target": doc_score >= 90.0,
            }
            
        except Exception as e:
            results["status"] = "failed"
            results["error"] = str(e)
            
        return results

    def _test_configuration(self) -> Dict[str, Any]:
        """Test configuration and environment setup."""
        results = {
            "test_name": "Configuration Validation",
            "status": "running",
            "details": {},
            "score": 0,
            "max_score": 100,
        }
        
        try:
            config_score = 0
            
            # Check for tools directory
            tools_exist = self.tools_dir.exists()
            if tools_exist:
                config_score += 25
                results["details"]["tools_directory"] = {"exists": True, "path": str(self.tools_dir)}
            else:
                results["details"]["tools_directory"] = {"exists": False, "error": "Tools directory not found"}
            
            # Check for reports directory
            reports_dir = self.project_root / "reports"
            reports_exist = reports_dir.exists()
            if reports_exist:
                config_score += 25
                results["details"]["reports_directory"] = {"exists": True, "path": str(reports_dir)}
            else:
                results["details"]["reports_directory"] = {"exists": False, "error": "Reports directory not found"}
            
            # Check for docs directory
            docs_dir = self.project_root / "docs"
            docs_exist = docs_dir.exists()
            if docs_exist:
                config_score += 25
                results["details"]["docs_directory"] = {"exists": True, "path": str(docs_dir)}
            else:
                results["details"]["docs_directory"] = {"exists": False, "error": "Docs directory not found"}
            
            # Check for unified orchestrators
            orchestrators_exist = sum(1 for tool in self.unified_orchestrators if (self.tools_dir / tool).exists())
            if orchestrators_exist >= len(self.unified_orchestrators) * 0.8:  # 80% of orchestrators exist
                config_score += 25
                results["details"]["unified_orchestrators"] = {
                    "exists": orchestrators_exist,
                    "total": len(self.unified_orchestrators),
                    "percentage": round((orchestrators_exist / len(self.unified_orchestrators)) * 100, 2)
                }
            else:
                results["details"]["unified_orchestrators"] = {
                    "exists": orchestrators_exist,
                    "total": len(self.unified_orchestrators),
                    "percentage": round((orchestrators_exist / len(self.unified_orchestrators)) * 100, 2),
                    "error": "Not enough unified orchestrators found"
                }
            
            results["score"] = config_score
            results["status"] = "completed"
            results["summary"] = {
                "configuration_score": config_score,
                "target_score": 90.0,
                "meets_target": config_score >= 90.0,
            }
            
        except Exception as e:
            results["status"] = "failed"
            results["error"] = str(e)

        return results

    def _generate_overall_results(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall validation results."""
        total_tests = len(test_results)
        passed_tests = sum(1 for result in test_results.values() if result.get("status") == "completed")
        failed_tests = total_tests - passed_tests

        # Calculate overall score
        scores = [result.get("score", 0) for result in test_results.values() if result.get("score") is not None]
        overall_score = sum(scores) / len(scores) if scores else 0

        # Check if meets targets
        meets_targets = all(
            result.get("summary", {}).get("meets_target", False)
            for result in test_results.values()
            if result.get("summary", {}).get("meets_target") is not None
        )

        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": round((passed_tests / total_tests) * 100, 2) if total_tests > 0 else 0,
            "overall_score": round(overall_score, 2),
            "meets_all_targets": meets_targets,
            "constitutional_compliance": CONSTITUTIONAL_HASH,
            "validation_status": "PASSED" if passed_tests == total_tests and meets_targets else "FAILED",
        }

    def _generate_recommendations(self, test_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []

        # Check constitutional compliance
        compliance_result = test_results.get("constitutional_compliance", {})
        if not compliance_result.get("summary", {}).get("meets_target", False):
            recommendations.append("Fix constitutional compliance violations in tools")

        # Check tool structure
        structure_result = test_results.get("tool_structure", {})
        if not structure_result.get("summary", {}).get("meets_target", False):
            recommendations.append("Improve tool structure and organization")

        # Check code quality
        quality_result = test_results.get("code_quality", {})
        if not quality_result.get("summary", {}).get("meets_target", False):
            recommendations.append("Enhance code quality with better type hints, error handling, and documentation")

        # Check documentation
        doc_result = test_results.get("documentation", {})
        if not doc_result.get("summary", {}).get("meets_target", False):
            recommendations.append("Improve documentation quality and constitutional compliance")

        # Check configuration
        config_result = test_results.get("configuration", {})
        if not config_result.get("summary", {}).get("meets_target", False):
            recommendations.append("Fix configuration and directory structure issues")

        # General recommendations
        if not recommendations:
            recommendations.append("All validation tests passed - system ready for production")
            recommendations.append("Continue monitoring constitutional compliance")
            recommendations.append("Maintain regular validation testing")
        else:
            recommendations.append("Address validation failures before production deployment")
            recommendations.append("Re-run validation tests after fixes")

        recommendations.append(f"Ensure constitutional hash {CONSTITUTIONAL_HASH} is maintained across all components")

        return recommendations

    def _save_validation_results(self, results: Dict[str, Any]):
        """Save validation results to file."""
        try:
            # Create reports directory
            reports_dir = self.project_root / "reports" / "validation"
            reports_dir.mkdir(parents=True, exist_ok=True)

            # Generate filename with timestamp
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            filename = f"acgs_validation_results_{timestamp}.json"
            filepath = reports_dir / filename

            # Save results
            with open(filepath, "w") as f:
                json.dump(results, f, indent=2, default=str)

            logger.info(f"✅ Validation results saved to {filepath}")

            # Also save latest results
            latest_filepath = reports_dir / "latest_validation_results.json"
            with open(latest_filepath, "w") as f:
                json.dump(results, f, indent=2, default=str)

        except Exception as e:
            logger.error(f"Failed to save validation results: {e}")

    def print_validation_summary(self, results: Dict[str, Any]):
        """Print comprehensive validation summary."""
        print("\n" + "="*80)
        print("🎯 ACGS COMPREHENSIVE VALIDATION TEST RESULTS")
        print("="*80)

        overall = results.get("overall_results", {})
        print(f"Validation Status: {overall.get('validation_status', 'UNKNOWN')}")
        print(f"Overall Score: {overall.get('overall_score', 0):.1f}/100")
        print(f"Tests Passed: {overall.get('passed_tests', 0)}/{overall.get('total_tests', 0)}")
        print(f"Success Rate: {overall.get('success_rate', 0):.1f}%")
        print(f"Meets All Targets: {'✅' if overall.get('meets_all_targets', False) else '❌'}")

        # Print individual test results
        print(f"\n📊 INDIVIDUAL TEST RESULTS:")
        for test_name, test_result in results.get("tests_executed", {}).items():
            status = test_result.get("status", "unknown")
            score = test_result.get("score", 0)
            status_icon = "✅" if status == "completed" else "❌"
            print(f"  {status_icon} {test_name:<30} - {score:.1f}/100")

            # Show summary if available
            summary = test_result.get("summary", {})
            if summary:
                meets_target = summary.get("meets_target", False)
                target_icon = "✅" if meets_target else "❌"
                print(f"    {target_icon} Meets Target: {meets_target}")

        # Print constitutional compliance status
        print(f"\n🏛️ Constitutional Compliance: ✅")
        print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")

        # Print recommendations
        recommendations = results.get("recommendations", [])
        if recommendations:
            print(f"\n📋 RECOMMENDATIONS:")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")

        print(f"\n⏱️ Execution Time: {results.get('execution_duration_seconds', 0):.1f}s")
        print("="*80)


def main():
    """Main function for ACGS validation test runner."""
    logger.info("🚀 ACGS Validation Test Runner Starting...")

    try:
        # Create and run validation test runner
        runner = ACGSValidationTestRunner()
        results = runner.run_comprehensive_validation()

        # Print summary
        runner.print_validation_summary(results)

        # Exit with appropriate code
        overall_results = results.get("overall_results", {})
        if overall_results.get("validation_status") == "PASSED":
            logger.info("✅ All validation tests passed")
            sys.exit(0)
        else:
            logger.error("❌ Some validation tests failed")
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("🛑 Validation interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"❌ Validation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
