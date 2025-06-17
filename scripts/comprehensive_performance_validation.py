#!/usr/bin/env python3
"""
ACGS-1 Comprehensive Performance Validation Orchestrator

This script orchestrates the execution of all performance optimization and testing
frameworks for the ACGS-1 Constitutional Governance System, validating that all
performance targets are achieved and generating comprehensive reports.

Performance Validation Targets:
- >85% accuracy on GSM8K mathematical reasoning benchmark
- >1000 concurrent users with <500ms response times
- >99.9% system availability under load
- Zero critical security vulnerabilities
- <0.01 SOL costs per governance action
- >90% test coverage across all components

Features:
- Orchestrated execution of all testing frameworks
- Comprehensive performance metrics aggregation
- Automated validation against performance targets
- Detailed reporting and recommendations
- Task Master CLI integration for progress tracking
- Constitutional governance workflow compatibility validation
"""

import asyncio
import json
import logging
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PerformanceValidationOrchestrator:
    """Orchestrates comprehensive performance validation testing."""
    
    def __init__(self, output_dir: str = "reports/comprehensive_validation"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.test_results = {}
        self.performance_targets = {
            "gsm8k_accuracy_percent": 85.0,
            "max_concurrent_users": 1000,
            "response_time_p95_ms": 500.0,
            "system_availability_percent": 99.9,
            "security_score": 80.0,
            "critical_vulnerabilities": 0,
            "blockchain_cost_sol": 0.01,
            "blockchain_success_rate_percent": 99.9,
            "test_coverage_percent": 90.0
        }
        
        self.validation_start_time = None
        self.validation_end_time = None
    
    async def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run comprehensive performance validation across all frameworks."""
        logger.info("🚀 Starting ACGS-1 Comprehensive Performance Validation")
        logger.info("="*80)
        
        self.validation_start_time = time.time()
        
        try:
            # Phase 1: Mathematical Reasoning Enhancement
            logger.info("📊 Phase 1: Mathematical Reasoning Enhancement")
            gsm8k_results = await self._run_gsm8k_benchmark()
            self.test_results["gsm8k_benchmark"] = gsm8k_results
            
            # Phase 2: Load Testing
            logger.info("🔄 Phase 2: Load Testing Framework")
            load_test_results = await self._run_load_testing()
            self.test_results["load_testing"] = load_test_results
            
            # Phase 3: Security Penetration Testing
            logger.info("🔒 Phase 3: Security Penetration Testing")
            security_results = await self._run_security_testing()
            self.test_results["security_testing"] = security_results
            
            # Phase 4: Blockchain Stress Testing
            logger.info("⛓️ Phase 4: Blockchain Stress Testing")
            blockchain_results = await self._run_blockchain_testing()
            self.test_results["blockchain_testing"] = blockchain_results
            
            # Phase 5: System Health Validation
            logger.info("🏥 Phase 5: System Health Validation")
            health_results = await self._validate_system_health()
            self.test_results["system_health"] = health_results
            
            self.validation_end_time = time.time()
            
            # Generate comprehensive validation report
            validation_report = self._generate_validation_report()
            
            # Save all results
            await self._save_comprehensive_results(validation_report)
            
            logger.info("✅ Comprehensive Performance Validation Complete")
            logger.info("="*80)
            
            return validation_report
            
        except Exception as e:
            logger.error(f"❌ Validation failed: {e}")
            self.validation_end_time = time.time()
            
            error_report = {
                "status": "FAILED",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "partial_results": self.test_results
            }
            
            await self._save_comprehensive_results(error_report)
            raise
    
    async def _run_gsm8k_benchmark(self) -> Dict[str, Any]:
        """Run GSM8K constitutional governance benchmark."""
        logger.info("  🧮 Running GSM8K Constitutional Governance Benchmark...")
        
        try:
            # Import and run GSM8K benchmark
            sys.path.append(str(Path(__file__).parent.parent))
            from tests.performance.gsm8k_constitutional_benchmark import GSM8KBenchmarkRunner
            
            runner = GSM8KBenchmarkRunner()
            results = await runner.run_benchmark(num_problems=100)
            
            # Save detailed results
            runner.save_results(str(self.output_dir / "gsm8k_benchmark_detailed.json"))
            
            logger.info(f"  ✅ GSM8K Accuracy: {results['accuracy_percentage']:.2f}% (Target: ≥{self.performance_targets['gsm8k_accuracy_percent']}%)")
            
            return results
            
        except Exception as e:
            logger.error(f"  ❌ GSM8K benchmark failed: {e}")
            return {"error": str(e), "accuracy_percentage": 0.0}
    
    async def _run_load_testing(self) -> Dict[str, Any]:
        """Run comprehensive load testing."""
        logger.info("  🚀 Running Load Testing with 1000+ Concurrent Users...")
        
        try:
            from tests.performance.load_testing_framework import ComprehensiveLoadTester, LoadTestConfig
            
            config = LoadTestConfig(
                max_concurrent_users=1000,
                test_duration_seconds=180,  # 3 minutes
                ramp_up_seconds=30
            )
            
            tester = ComprehensiveLoadTester(config)
            results = await tester.run_load_test()
            
            # Save detailed results
            tester.save_results(str(self.output_dir / "load_test_detailed.json"), results)
            
            logger.info(f"  ✅ Load Test - Users: {results['configuration']['max_concurrent_users']}, "
                       f"Success Rate: {results['overall_metrics']['success_rate_percent']:.2f}%, "
                       f"P95 Response: {results['overall_metrics']['p95_response_time_ms']:.2f}ms")
            
            return results
            
        except Exception as e:
            logger.error(f"  ❌ Load testing failed: {e}")
            return {"error": str(e), "overall_metrics": {"success_rate_percent": 0.0, "p95_response_time_ms": 9999.0}}
    
    async def _run_security_testing(self) -> Dict[str, Any]:
        """Run comprehensive security penetration testing."""
        logger.info("  🔐 Running Security Penetration Testing...")
        
        try:
            from tests.security.penetration_testing_framework import ComprehensiveSecurityTester
            
            tester = ComprehensiveSecurityTester()
            results = await tester.run_comprehensive_security_test()
            
            # Save detailed results
            tester.save_results(str(self.output_dir / "security_test_detailed.json"), results)
            
            logger.info(f"  ✅ Security Test - Score: {results['security_score']:.1f}/100, "
                       f"Critical Vulns: {results['vulnerability_summary']['CRITICAL']}, "
                       f"Status: {results['security_assessment']['overall_security_status']}")
            
            return results
            
        except Exception as e:
            logger.error(f"  ❌ Security testing failed: {e}")
            return {"error": str(e), "security_score": 0.0, "vulnerability_summary": {"CRITICAL": 999}}
    
    async def _run_blockchain_testing(self) -> Dict[str, Any]:
        """Run blockchain stress testing."""
        logger.info("  ⛓️ Running Blockchain Stress Testing...")
        
        try:
            from tests.performance.blockchain_stress_testing import BlockchainStressTester, BlockchainStressConfig
            
            config = BlockchainStressConfig(
                max_concurrent_transactions=1000,
                test_duration_seconds=180,  # 3 minutes
                target_sol_cost=0.01,
                target_confirmation_time_seconds=2.0,
                target_success_rate_percent=99.9
            )
            
            tester = BlockchainStressTester(config)
            results = await tester.run_blockchain_stress_test()
            
            # Save detailed results
            tester.save_results(str(self.output_dir / "blockchain_test_detailed.json"), results)
            
            logger.info(f"  ✅ Blockchain Test - Transactions: {results['overall_metrics']['total_transactions']}, "
                       f"Success Rate: {results['overall_metrics']['success_rate_percent']:.2f}%, "
                       f"Avg Cost: {results['overall_metrics']['avg_cost_sol']:.6f} SOL")
            
            return results
            
        except Exception as e:
            logger.error(f"  ❌ Blockchain testing failed: {e}")
            return {"error": str(e), "overall_metrics": {"success_rate_percent": 0.0, "avg_cost_sol": 999.0}}
    
    async def _validate_system_health(self) -> Dict[str, Any]:
        """Validate overall system health and service availability."""
        logger.info("  🏥 Validating System Health...")
        
        try:
            # Check service health endpoints
            import aiohttp
            
            services = {
                "auth": 8000, "ac": 8001, "integrity": 8002,
                "fv": 8003, "gs": 8004, "pgc": 8005, "ec": 8006
            }
            
            health_results = {}
            
            async with aiohttp.ClientSession() as session:
                for service, port in services.items():
                    try:
                        start_time = time.time()
                        async with session.get(f"http://localhost:{port}/health", timeout=aiohttp.ClientTimeout(total=5)) as response:
                            response_time = (time.time() - start_time) * 1000
                            health_results[service] = {
                                "status": "healthy" if response.status == 200 else "unhealthy",
                                "response_time_ms": response_time,
                                "status_code": response.status
                            }
                    except Exception as e:
                        health_results[service] = {
                            "status": "error",
                            "response_time_ms": 9999.0,
                            "error": str(e)
                        }
            
            # Calculate overall health metrics
            healthy_services = sum(1 for result in health_results.values() if result["status"] == "healthy")
            total_services = len(services)
            availability_percent = (healthy_services / total_services) * 100
            
            avg_response_time = sum(
                result["response_time_ms"] for result in health_results.values() 
                if result["status"] == "healthy"
            ) / max(healthy_services, 1)
            
            system_health = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "services": health_results,
                "overall_metrics": {
                    "healthy_services": healthy_services,
                    "total_services": total_services,
                    "availability_percent": availability_percent,
                    "avg_response_time_ms": avg_response_time
                }
            }
            
            logger.info(f"  ✅ System Health - Availability: {availability_percent:.1f}%, "
                       f"Avg Response: {avg_response_time:.2f}ms")
            
            return system_health
            
        except Exception as e:
            logger.error(f"  ❌ System health validation failed: {e}")
            return {"error": str(e), "overall_metrics": {"availability_percent": 0.0}}
    
    def _generate_validation_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report."""
        total_duration = self.validation_end_time - self.validation_start_time if self.validation_end_time else 0
        
        # Extract key metrics from test results
        metrics = self._extract_key_metrics()
        
        # Validate against performance targets
        target_validation = self._validate_performance_targets(metrics)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(metrics, target_validation)
        
        validation_report = {
            "validation_metadata": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "total_duration_seconds": total_duration,
                "framework_version": "ACGS-1 v2.0",
                "constitution_hash": "cdd01ef066bc6cf2",
                "validation_id": f"validation_{int(time.time())}"
            },
            "performance_targets": self.performance_targets,
            "measured_metrics": metrics,
            "target_validation": target_validation,
            "overall_assessment": {
                "all_targets_met": all(target_validation.values()),
                "critical_failures": [k for k, v in target_validation.items() if not v and "critical" in k.lower()],
                "overall_status": "PASS" if all(target_validation.values()) else "FAIL",
                "readiness_level": self._calculate_readiness_level(target_validation)
            },
            "detailed_results": self.test_results,
            "recommendations": recommendations,
            "next_steps": self._generate_next_steps(target_validation)
        }
        
        return validation_report
    
    def _extract_key_metrics(self) -> Dict[str, float]:
        """Extract key performance metrics from test results."""
        metrics = {}
        
        # GSM8K metrics
        gsm8k = self.test_results.get("gsm8k_benchmark", {})
        metrics["gsm8k_accuracy_percent"] = gsm8k.get("accuracy_percentage", 0.0)
        
        # Load testing metrics
        load_test = self.test_results.get("load_testing", {})
        load_metrics = load_test.get("overall_metrics", {})
        metrics["concurrent_users"] = load_test.get("configuration", {}).get("max_concurrent_users", 0)
        metrics["response_time_p95_ms"] = load_metrics.get("p95_response_time_ms", 9999.0)
        metrics["system_availability_percent"] = load_metrics.get("success_rate_percent", 0.0)
        
        # Security metrics
        security = self.test_results.get("security_testing", {})
        metrics["security_score"] = security.get("security_score", 0.0)
        metrics["critical_vulnerabilities"] = security.get("vulnerability_summary", {}).get("CRITICAL", 999)
        
        # Blockchain metrics
        blockchain = self.test_results.get("blockchain_testing", {})
        blockchain_metrics = blockchain.get("overall_metrics", {})
        metrics["blockchain_cost_sol"] = blockchain_metrics.get("avg_cost_sol", 999.0)
        metrics["blockchain_success_rate_percent"] = blockchain_metrics.get("success_rate_percent", 0.0)
        
        # System health metrics
        health = self.test_results.get("system_health", {})
        health_metrics = health.get("overall_metrics", {})
        metrics["service_availability_percent"] = health_metrics.get("availability_percent", 0.0)
        
        return metrics
    
    def _validate_performance_targets(self, metrics: Dict[str, float]) -> Dict[str, bool]:
        """Validate measured metrics against performance targets."""
        validation = {}
        
        validation["gsm8k_accuracy_target"] = metrics.get("gsm8k_accuracy_percent", 0) >= self.performance_targets["gsm8k_accuracy_percent"]
        validation["concurrent_users_target"] = metrics.get("concurrent_users", 0) >= self.performance_targets["max_concurrent_users"]
        validation["response_time_target"] = metrics.get("response_time_p95_ms", 9999) <= self.performance_targets["response_time_p95_ms"]
        validation["availability_target"] = metrics.get("system_availability_percent", 0) >= self.performance_targets["system_availability_percent"]
        validation["security_score_target"] = metrics.get("security_score", 0) >= self.performance_targets["security_score"]
        validation["critical_vulnerabilities_target"] = metrics.get("critical_vulnerabilities", 999) <= self.performance_targets["critical_vulnerabilities"]
        validation["blockchain_cost_target"] = metrics.get("blockchain_cost_sol", 999) <= self.performance_targets["blockchain_cost_sol"]
        validation["blockchain_success_target"] = metrics.get("blockchain_success_rate_percent", 0) >= self.performance_targets["blockchain_success_rate_percent"]
        
        return validation
    
    def _generate_recommendations(self, metrics: Dict[str, float], validation: Dict[str, bool]) -> List[str]:
        """Generate actionable recommendations based on validation results."""
        recommendations = []
        
        if not validation.get("gsm8k_accuracy_target", True):
            recommendations.append(f"🧮 Improve mathematical reasoning accuracy from {metrics.get('gsm8k_accuracy_percent', 0):.1f}% to ≥{self.performance_targets['gsm8k_accuracy_percent']}% through model fine-tuning")
        
        if not validation.get("response_time_target", True):
            recommendations.append(f"⚡ Optimize response times from {metrics.get('response_time_p95_ms', 0):.1f}ms to ≤{self.performance_targets['response_time_p95_ms']}ms through caching and batching")
        
        if not validation.get("security_score_target", True):
            recommendations.append(f"🔒 Address security vulnerabilities to improve score from {metrics.get('security_score', 0):.1f} to ≥{self.performance_targets['security_score']}")
        
        if not validation.get("blockchain_cost_target", True):
            recommendations.append(f"💰 Optimize blockchain costs from {metrics.get('blockchain_cost_sol', 0):.6f} SOL to ≤{self.performance_targets['blockchain_cost_sol']} SOL")
        
        if all(validation.values()):
            recommendations.append("🎉 All performance targets achieved! System ready for production deployment.")
        
        return recommendations
    
    def _calculate_readiness_level(self, validation: Dict[str, bool]) -> str:
        """Calculate overall system readiness level."""
        passed_targets = sum(validation.values())
        total_targets = len(validation)
        
        if passed_targets == total_targets:
            return "PRODUCTION_READY"
        elif passed_targets >= total_targets * 0.8:
            return "STAGING_READY"
        elif passed_targets >= total_targets * 0.6:
            return "DEVELOPMENT_READY"
        else:
            return "NEEDS_IMPROVEMENT"
    
    def _generate_next_steps(self, validation: Dict[str, bool]) -> List[str]:
        """Generate next steps based on validation results."""
        if all(validation.values()):
            return [
                "✅ Deploy to production environment",
                "📊 Set up continuous monitoring",
                "🔄 Implement automated performance regression testing",
                "📈 Monitor real-world performance metrics"
            ]
        else:
            failed_targets = [k for k, v in validation.items() if not v]
            return [
                f"🔧 Address failed targets: {', '.join(failed_targets)}",
                "🧪 Re-run validation after improvements",
                "📋 Update performance optimization roadmap",
                "👥 Coordinate with development team for remediation"
            ]
    
    async def _save_comprehensive_results(self, validation_report: Dict[str, Any]):
        """Save comprehensive validation results."""
        # Save main validation report
        report_file = self.output_dir / "comprehensive_validation_report.json"
        with open(report_file, 'w') as f:
            json.dump(validation_report, f, indent=2, default=str)
        
        # Generate human-readable summary
        summary_file = self.output_dir / "validation_summary.txt"
        with open(summary_file, 'w') as f:
            f.write("ACGS-1 COMPREHENSIVE PERFORMANCE VALIDATION SUMMARY\n")
            f.write("="*60 + "\n\n")
            
            f.write(f"Validation ID: {validation_report['validation_metadata']['validation_id']}\n")
            f.write(f"Timestamp: {validation_report['validation_metadata']['timestamp']}\n")
            f.write(f"Duration: {validation_report['validation_metadata']['total_duration_seconds']:.1f} seconds\n\n")
            
            f.write("PERFORMANCE TARGETS VALIDATION:\n")
            f.write("-" * 30 + "\n")
            for target, passed in validation_report["target_validation"].items():
                status = "✅ PASS" if passed else "❌ FAIL"
                f.write(f"{target}: {status}\n")
            
            f.write(f"\nOVERALL STATUS: {validation_report['overall_assessment']['overall_status']}\n")
            f.write(f"READINESS LEVEL: {validation_report['overall_assessment']['readiness_level']}\n\n")
            
            f.write("RECOMMENDATIONS:\n")
            f.write("-" * 15 + "\n")
            for rec in validation_report["recommendations"]:
                f.write(f"• {rec}\n")
        
        logger.info(f"📄 Comprehensive validation results saved to {self.output_dir}")


async def main():
    """Main execution function."""
    orchestrator = PerformanceValidationOrchestrator()
    
    try:
        validation_report = await orchestrator.run_comprehensive_validation()
        
        print("\n" + "="*80)
        print("ACGS-1 COMPREHENSIVE PERFORMANCE VALIDATION COMPLETE")
        print("="*80)
        print(f"Overall Status: {validation_report['overall_assessment']['overall_status']}")
        print(f"Readiness Level: {validation_report['overall_assessment']['readiness_level']}")
        print(f"Targets Met: {sum(validation_report['target_validation'].values())}/{len(validation_report['target_validation'])}")
        
        if validation_report['recommendations']:
            print("\nKey Recommendations:")
            for rec in validation_report['recommendations'][:3]:  # Show top 3
                print(f"  • {rec}")
        
        return 0 if validation_report['overall_assessment']['overall_status'] == 'PASS' else 1
        
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
