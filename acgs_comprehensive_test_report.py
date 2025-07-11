#!/usr/bin/env python3
"""
ACGS-2 Comprehensive End-to-End Test Report Generator
Constitutional Hash: cdd01ef066bc6cf2
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

class ComprehensiveTestReportGenerator:
    def __init__(self):
        self.report_data = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "acgs_version": "2.0",
                "test_suite_version": "1.0"
            },
            "executive_summary": {},
            "detailed_results": {},
            "constitutional_compliance": {},
            "performance_analysis": {},
            "recommendations": []
        }
    
    def load_test_results(self) -> Dict[str, Any]:
        """Load all test result files"""
        result_files = {
            "comprehensive": "acgs_test_results.json",
            "database": "database_integration_results.json", 
            "api": "api_endpoint_results.json",
            "performance": "performance_test_results.json"
        }
        
        loaded_results = {}
        
        for test_type, filename in result_files.items():
            if os.path.exists(filename):
                try:
                    with open(filename, 'r') as f:
                        loaded_results[test_type] = json.load(f)
                    logger.info(f"Loaded {test_type} test results from {filename}")
                except Exception as e:
                    logger.error(f"Failed to load {filename}: {e}")
                    loaded_results[test_type] = {"error": str(e)}
            else:
                logger.warning(f"Test result file {filename} not found")
                loaded_results[test_type] = {"error": "File not found"}
        
        return loaded_results
    
    def analyze_constitutional_compliance(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze constitutional compliance across all tests"""
        compliance_analysis = {
            "overall_compliance_rate": 0.0,
            "compliant_tests": 0,
            "total_tests": 0,
            "compliance_by_category": {},
            "constitutional_hash_verification": {
                "expected_hash": CONSTITUTIONAL_HASH,
                "services_with_correct_hash": [],
                "services_with_incorrect_hash": [],
                "services_without_hash": []
            }
        }
        
        total_compliant = 0
        total_tests = 0
        
        for test_category, results in test_results.items():
            if "error" in results:
                continue
                
            category_compliant = 0
            category_total = 0
            
            # Handle different result structures
            if "detailed_results" in results:
                for result in results["detailed_results"]:
                    category_total += 1
                    total_tests += 1
                    
                    if result.get("constitutional_compliance", False):
                        category_compliant += 1
                        total_compliant += 1
                    
                    # Check constitutional hash
                    if "constitutional_hash" in result.get("details", {}):
                        hash_value = result["details"]["constitutional_hash"]
                        service_name = result.get("service", "unknown")
                        
                        if hash_value == CONSTITUTIONAL_HASH:
                            if service_name not in compliance_analysis["constitutional_hash_verification"]["services_with_correct_hash"]:
                                compliance_analysis["constitutional_hash_verification"]["services_with_correct_hash"].append(service_name)
                        else:
                            if service_name not in compliance_analysis["constitutional_hash_verification"]["services_with_incorrect_hash"]:
                                compliance_analysis["constitutional_hash_verification"]["services_with_incorrect_hash"].append(service_name)
            
            if category_total > 0:
                compliance_analysis["compliance_by_category"][test_category] = {
                    "compliant_tests": category_compliant,
                    "total_tests": category_total,
                    "compliance_rate": (category_compliant / category_total) * 100
                }
        
        if total_tests > 0:
            compliance_analysis["overall_compliance_rate"] = (total_compliant / total_tests) * 100
            compliance_analysis["compliant_tests"] = total_compliant
            compliance_analysis["total_tests"] = total_tests
        
        return compliance_analysis
    
    def analyze_performance_metrics(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance metrics across all tests"""
        performance_analysis = {
            "targets": {
                "p99_latency_ms": 5.0,
                "throughput_rps": 100.0,
                "cache_hit_rate_percent": 85.0
            },
            "actual_metrics": {},
            "target_compliance": {},
            "performance_summary": "UNKNOWN"
        }
        
        # Extract performance data
        if "performance" in test_results and "summary" in test_results["performance"]:
            perf_data = test_results["performance"]["summary"]
            
            # Latency metrics
            if "latency_results" in perf_data:
                latency_metrics = {}
                for service, result in perf_data["latency_results"].items():
                    if "error" not in result:
                        latency_metrics[service] = {
                            "p99_latency_ms": result.get("p99_latency_ms", 0),
                            "avg_latency_ms": result.get("avg_latency_ms", 0),
                            "constitutional_compliance_rate": result.get("constitutional_compliance_rate", 0)
                        }
                performance_analysis["actual_metrics"]["latency"] = latency_metrics
            
            # Throughput metrics
            if "throughput_results" in perf_data:
                throughput_metrics = {}
                for service, result in perf_data["throughput_results"].items():
                    throughput_metrics[service] = {
                        "requests_per_second": result.get("requests_per_second", 0),
                        "success_rate": (result.get("successful_requests", 0) / result.get("total_requests", 1)) * 100,
                        "constitutional_compliance_rate": result.get("constitutional_compliance_rate", 0)
                    }
                performance_analysis["actual_metrics"]["throughput"] = throughput_metrics
            
            # Cache metrics
            if "cache_results" in perf_data:
                cache_result = perf_data["cache_results"]
                performance_analysis["actual_metrics"]["cache"] = {
                    "hit_rate_percent": cache_result.get("cache_hit_rate_percent", 0),
                    "operations_per_second": cache_result.get("operations_per_second", 0)
                }
            
            # Target compliance
            performance_analysis["target_compliance"] = perf_data.get("performance_summary", {})
            performance_analysis["performance_summary"] = "PASS" if perf_data.get("all_targets_met", False) else "FAIL"
        
        return performance_analysis
    
    def generate_recommendations(self, compliance_analysis: Dict[str, Any], performance_analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Constitutional compliance recommendations
        if compliance_analysis["overall_compliance_rate"] < 100.0:
            recommendations.append(
                f"🔴 CRITICAL: Constitutional compliance rate is {compliance_analysis['overall_compliance_rate']:.1f}%. "
                f"Target is 100%. Review services without proper constitutional hash implementation."
            )
        
        # Performance recommendations
        if performance_analysis["performance_summary"] == "FAIL":
            recommendations.append(
                "🟡 PERFORMANCE: Some performance targets not met. Consider optimizing service response times and caching strategies."
            )
        
        # Latency recommendations
        if "latency" in performance_analysis["actual_metrics"]:
            for service, metrics in performance_analysis["actual_metrics"]["latency"].items():
                if metrics["p99_latency_ms"] > 5.0:
                    recommendations.append(
                        f"🟡 LATENCY: {service} P99 latency ({metrics['p99_latency_ms']:.2f}ms) exceeds 5ms target. "
                        f"Consider implementing request caching or optimizing service logic."
                    )
        
        # Service availability recommendations
        if compliance_analysis["constitutional_hash_verification"]["services_with_incorrect_hash"]:
            recommendations.append(
                f"🔴 HASH MISMATCH: Services with incorrect constitutional hash: "
                f"{', '.join(compliance_analysis['constitutional_hash_verification']['services_with_incorrect_hash'])}"
            )
        
        # Positive recommendations
        if compliance_analysis["overall_compliance_rate"] >= 90.0:
            recommendations.append("✅ GOOD: High constitutional compliance rate achieved.")
        
        if performance_analysis["performance_summary"] == "PASS":
            recommendations.append("✅ GOOD: All performance targets met.")
        
        return recommendations
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate the comprehensive test report"""
        logger.info("Generating comprehensive ACGS-2 test report...")
        
        # Load all test results
        test_results = self.load_test_results()
        
        # Analyze constitutional compliance
        compliance_analysis = self.analyze_constitutional_compliance(test_results)
        
        # Analyze performance metrics
        performance_analysis = self.analyze_performance_metrics(test_results)
        
        # Generate recommendations
        recommendations = self.generate_recommendations(compliance_analysis, performance_analysis)
        
        # Build executive summary
        executive_summary = {
            "overall_status": "PASS" if compliance_analysis["overall_compliance_rate"] >= 90.0 and performance_analysis["performance_summary"] == "PASS" else "FAIL",
            "constitutional_compliance_rate": compliance_analysis["overall_compliance_rate"],
            "performance_targets_met": performance_analysis["performance_summary"] == "PASS",
            "total_tests_executed": compliance_analysis["total_tests"],
            "services_tested": len(set(
                compliance_analysis["constitutional_hash_verification"]["services_with_correct_hash"] +
                compliance_analysis["constitutional_hash_verification"]["services_with_incorrect_hash"]
            )),
            "critical_issues": len([r for r in recommendations if r.startswith("🔴")]),
            "warnings": len([r for r in recommendations if r.startswith("🟡")])
        }
        
        # Compile final report
        self.report_data.update({
            "executive_summary": executive_summary,
            "detailed_results": test_results,
            "constitutional_compliance": compliance_analysis,
            "performance_analysis": performance_analysis,
            "recommendations": recommendations
        })
        
        return self.report_data
    
    def save_report(self, filename: str = "acgs_comprehensive_test_report.json"):
        """Save the comprehensive report to file"""
        with open(filename, 'w') as f:
            json.dump(self.report_data, f, indent=2)
        logger.info(f"Comprehensive test report saved to {filename}")
    
    def print_summary(self):
        """Print a summary of the test report"""
        summary = self.report_data["executive_summary"]
        compliance = self.report_data["constitutional_compliance"]
        performance = self.report_data["performance_analysis"]
        
        print("\n" + "="*80)
        print("ACGS-2 COMPREHENSIVE END-TO-END TEST REPORT")
        print("="*80)
        print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
        print(f"Report Generated: {self.report_data['report_metadata']['generated_at']}")
        print(f"Overall Status: {'✅ PASS' if summary['overall_status'] == 'PASS' else '❌ FAIL'}")
        
        print("\nEXECUTIVE SUMMARY:")
        print(f"• Constitutional Compliance Rate: {summary['constitutional_compliance_rate']:.1f}%")
        print(f"• Performance Targets Met: {'✅ YES' if summary['performance_targets_met'] else '❌ NO'}")
        print(f"• Total Tests Executed: {summary['total_tests_executed']}")
        print(f"• Services Tested: {summary['services_tested']}")
        print(f"• Critical Issues: {summary['critical_issues']}")
        print(f"• Warnings: {summary['warnings']}")
        
        print("\nCONSTITUTIONAL COMPLIANCE ANALYSIS:")
        print(f"• Overall Compliance: {compliance['overall_compliance_rate']:.1f}%")
        print(f"• Compliant Tests: {compliance['compliant_tests']}/{compliance['total_tests']}")
        print(f"• Services with Correct Hash: {len(compliance['constitutional_hash_verification']['services_with_correct_hash'])}")
        print(f"• Services with Issues: {len(compliance['constitutional_hash_verification']['services_with_incorrect_hash'])}")
        
        print("\nPERFORMANCE ANALYSIS:")
        print(f"• Performance Summary: {'✅ PASS' if performance['performance_summary'] == 'PASS' else '❌ FAIL'}")
        if "cache" in performance["actual_metrics"]:
            cache_metrics = performance["actual_metrics"]["cache"]
            print(f"• Cache Hit Rate: {cache_metrics['hit_rate_percent']:.1f}%")
        
        print("\nRECOMMENDATIONS:")
        for i, recommendation in enumerate(self.report_data["recommendations"][:10], 1):  # Show first 10
            print(f"{i}. {recommendation}")
        
        if len(self.report_data["recommendations"]) > 10:
            print(f"... and {len(self.report_data['recommendations']) - 10} more recommendations")

def main():
    """Main report generation"""
    generator = ComprehensiveTestReportGenerator()
    report = generator.generate_comprehensive_report()
    generator.save_report()
    generator.print_summary()
    
    # Return appropriate exit code
    if report["executive_summary"]["overall_status"] == "PASS":
        print(f"\n✅ SUCCESS: ACGS-2 comprehensive testing completed successfully")
        return 0
    else:
        print(f"\n⚠️  WARNING: ACGS-2 testing completed with issues that need attention")
        return 1

if __name__ == "__main__":
    exit(main())
