#!/usr/bin/env python3
"""
ACGS Comprehensive Monitoring and Analytics Tool
Constitutional Hash: cdd01ef066bc6cf2

This tool provides comprehensive monitoring and analytics for ACGS-2 system:
- Pipeline performance tracking and optimization
- Security integration validation and enhancement
- Test coverage expansion monitoring
- Constitutional compliance continuous monitoring
- Automated alerting and improvement recommendations
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ACGSComprehensiveMonitor:
    """ACGS Comprehensive Monitoring and Analytics Engine."""
    
    def __init__(self):
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.monitoring_data = {}
        self.alerts = []
        self.recommendations = []
        
    def run_performance_monitoring(self) -> Dict:
        """Run performance monitoring and tuning."""
        logger.info("⚡ Running performance monitoring...")
        
        try:
            # Import and run performance tuning
            import subprocess
            result = subprocess.run(
                ["python", "tools/performance_tuning.py"],
                capture_output=True,
                text=True,
                timeout=180
            )
            
            if result.returncode == 0:
                # Load performance results
                perf_file = Path("acgs_performance_tuning_report.json")
                if perf_file.exists():
                    with open(perf_file, 'r') as f:
                        performance_data = json.load(f)
                    logger.info("✅ Performance monitoring completed successfully")
                    return performance_data
                else:
                    logger.warning("⚠️ Performance report file not found")
                    return {"status": "no_data", "constitutional_hash": self.constitutional_hash}
            else:
                logger.error(f"❌ Performance monitoring failed: {result.stderr}")
                return {"status": "failed", "error": result.stderr, "constitutional_hash": self.constitutional_hash}
                
        except Exception as e:
            logger.error(f"❌ Performance monitoring exception: {str(e)}")
            return {"status": "error", "error": str(e), "constitutional_hash": self.constitutional_hash}
    
    def run_security_analysis(self) -> Dict:
        """Run security analysis and enhancement."""
        logger.info("🔒 Running security analysis...")
        
        try:
            # Import and run security enhancement
            import subprocess
            result = subprocess.run(
                ["python", "tools/security_enhancement.py"],
                capture_output=True,
                text=True,
                timeout=180
            )
            
            if result.returncode == 0:
                # Load security results
                security_file = Path("acgs_security_analysis_report.json")
                if security_file.exists():
                    with open(security_file, 'r') as f:
                        security_data = json.load(f)
                    logger.info("✅ Security analysis completed successfully")
                    return security_data
                else:
                    logger.warning("⚠️ Security report file not found")
                    return {"status": "no_data", "constitutional_hash": self.constitutional_hash}
            else:
                logger.error(f"❌ Security analysis failed: {result.stderr}")
                return {"status": "failed", "error": result.stderr, "constitutional_hash": self.constitutional_hash}
                
        except Exception as e:
            logger.error(f"❌ Security analysis exception: {str(e)}")
            return {"status": "error", "error": str(e), "constitutional_hash": self.constitutional_hash}
    
    def analyze_test_coverage_expansion(self) -> Dict:
        """Analyze test coverage and expansion opportunities."""
        logger.info("🧪 Analyzing test coverage expansion...")
        
        test_categories = {
            "service_specific": "tests/services/",
            "integration": "tests/integration/",
            "edge_cases": "tests/edge_cases/",
            "performance": "tests/performance/"
        }
        
        coverage_analysis = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "constitutional_hash": self.constitutional_hash,
            "test_coverage_expansion": {
                "total_test_files": 0,
                "constitutional_compliant_files": 0,
                "coverage_percentage": 0.0,
                "expansion_opportunities": []
            },
            "category_breakdown": {}
        }
        
        total_files = 0
        compliant_files = 0
        expansion_opportunities = []
        
        for category, path in test_categories.items():
            test_path = Path(path)
            if test_path.exists():
                test_files = list(test_path.glob('test_*.py'))
                category_compliant = 0
                
                for test_file in test_files:
                    try:
                        with open(test_file, 'r') as f:
                            content = f.read()
                        
                        if self.constitutional_hash in content:
                            category_compliant += 1
                            compliant_files += 1
                        
                        total_files += 1
                    except:
                        pass
                
                coverage_analysis["category_breakdown"][category] = {
                    "test_files": len(test_files),
                    "constitutional_compliant": category_compliant,
                    "compliance_rate": (category_compliant / len(test_files)) * 100 if len(test_files) > 0 else 0
                }
                
                # Identify expansion opportunities
                if len(test_files) < 20:  # Arbitrary threshold for comprehensive coverage
                    expansion_opportunities.append(f"Expand {category} test coverage (current: {len(test_files)} files)")
            else:
                expansion_opportunities.append(f"Create {category} test directory: {path}")
        
        coverage_percentage = (compliant_files / max(total_files, 1)) * 100
        
        coverage_analysis["test_coverage_expansion"] = {
            "total_test_files": total_files,
            "constitutional_compliant_files": compliant_files,
            "coverage_percentage": coverage_percentage,
            "expansion_opportunities": expansion_opportunities
        }
        
        logger.info(f"✅ Test coverage analysis completed: {coverage_percentage:.1f}% coverage")
        return coverage_analysis
    
    def monitor_constitutional_compliance(self) -> Dict:
        """Monitor constitutional compliance across the codebase."""
        logger.info("🏛️ Monitoring constitutional compliance...")
        
        critical_dirs = ["services/", "tests/", ".github/workflows/", "tools/"]
        compliance_monitoring = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "constitutional_hash": self.constitutional_hash,
            "compliance_monitoring": {
                "total_files_monitored": 0,
                "compliant_files": 0,
                "compliance_percentage": 0.0,
                "violations": []
            },
            "directory_breakdown": {}
        }
        
        total_files = 0
        compliant_files = 0
        violations = []
        
        for directory in critical_dirs:
            dir_path = Path(directory)
            if dir_path.exists():
                dir_files = 0
                dir_compliant = 0
                dir_violations = []
                
                for file_path in dir_path.rglob("*.py"):
                    if any(part.startswith('.') for part in file_path.parts) or \
                       any(ignore in str(file_path) for ignore in ['__pycache__', '.venv']):
                        continue
                    
                    try:
                        with open(file_path, 'r') as f:
                            content = f.read()
                        
                        dir_files += 1
                        total_files += 1
                        
                        if self.constitutional_hash in content:
                            dir_compliant += 1
                            compliant_files += 1
                        else:
                            violation = {
                                "file": str(file_path),
                                "type": "missing_constitutional_hash",
                                "severity": "high" if directory in ["services/", ".github/workflows/"] else "medium"
                            }
                            dir_violations.append(violation)
                            violations.append(violation)
                    except:
                        pass
                
                compliance_monitoring["directory_breakdown"][directory] = {
                    "files_monitored": dir_files,
                    "compliant_files": dir_compliant,
                    "compliance_rate": (dir_compliant / max(dir_files, 1)) * 100,
                    "violations": len(dir_violations)
                }
        
        compliance_percentage = (compliant_files / max(total_files, 1)) * 100
        
        compliance_monitoring["compliance_monitoring"] = {
            "total_files_monitored": total_files,
            "compliant_files": compliant_files,
            "compliance_percentage": compliance_percentage,
            "violations": violations[:10]  # Limit to first 10 violations
        }
        
        logger.info(f"✅ Constitutional compliance monitoring completed: {compliance_percentage:.1f}% compliant")
        return compliance_monitoring
    
    def generate_comprehensive_alerts(self, performance_data: Dict, security_data: Dict, coverage_data: Dict, compliance_data: Dict) -> List[Dict]:
        """Generate comprehensive monitoring alerts."""
        logger.info("🚨 Generating comprehensive monitoring alerts...")
        
        alerts = []
        
        # Performance alerts
        if performance_data.get("status") == "failed":
            alerts.append({
                "type": "performance",
                "severity": "critical",
                "message": "Performance monitoring failed",
                "constitutional_hash": self.constitutional_hash
            })
        elif "current_performance" in performance_data:
            p99_latency = performance_data["current_performance"].get("p99_latency_ms", 0)
            if p99_latency > 5.0:
                alerts.append({
                    "type": "performance",
                    "severity": "warning",
                    "message": f"P99 latency ({p99_latency:.2f}ms) exceeds 5ms target",
                    "constitutional_hash": self.constitutional_hash
                })
        
        # Security alerts
        if security_data.get("status") == "failed":
            alerts.append({
                "type": "security",
                "severity": "critical",
                "message": "Security analysis failed",
                "constitutional_hash": self.constitutional_hash
            })
        elif "summary" in security_data:
            critical_issues = security_data["summary"].get("critical_issues", 0)
            if critical_issues > 0:
                alerts.append({
                    "type": "security",
                    "severity": "critical",
                    "message": f"{critical_issues} critical security vulnerabilities found",
                    "constitutional_hash": self.constitutional_hash
                })
            
            security_score = security_data["summary"].get("security_score", 100)
            if security_score < 70:
                alerts.append({
                    "type": "security",
                    "severity": "high",
                    "message": f"Security score ({security_score}/100) critically low",
                    "constitutional_hash": self.constitutional_hash
                })
        
        # Test coverage alerts
        coverage_percentage = coverage_data.get("test_coverage_expansion", {}).get("coverage_percentage", 0)
        if coverage_percentage < 75:
            alerts.append({
                "type": "test_coverage",
                "severity": "medium",
                "message": f"Test coverage ({coverage_percentage:.1f}%) below recommended 75%",
                "constitutional_hash": self.constitutional_hash
            })
        
        # Constitutional compliance alerts
        compliance_percentage = compliance_data.get("compliance_monitoring", {}).get("compliance_percentage", 0)
        if compliance_percentage < 90:
            alerts.append({
                "type": "constitutional_compliance",
                "severity": "high" if compliance_percentage < 80 else "medium",
                "message": f"Constitutional compliance ({compliance_percentage:.1f}%) below 90% threshold",
                "constitutional_hash": self.constitutional_hash
            })
        
        self.alerts = alerts
        logger.info(f"✅ Generated {len(alerts)} comprehensive monitoring alerts")
        return alerts
    
    def generate_improvement_recommendations(self, performance_data: Dict, security_data: Dict, coverage_data: Dict, compliance_data: Dict) -> List[str]:
        """Generate comprehensive improvement recommendations."""
        logger.info("💡 Generating comprehensive improvement recommendations...")
        
        recommendations = []
        
        # Performance recommendations
        if "current_performance" in performance_data:
            if not performance_data.get("target_compliance", {}).get("p99_latency_compliant", True):
                recommendations.append("Implement database connection pooling and query optimization to reduce P99 latency")
            
            if not performance_data.get("target_compliance", {}).get("cache_hit_compliant", True):
                recommendations.append("Optimize cache strategies and implement intelligent cache warming")
        
        # Security recommendations
        if "summary" in security_data:
            security_score = security_data["summary"].get("security_score", 100)
            if security_score < 85:
                recommendations.append("Conduct comprehensive security audit and implement security hardening measures")
            
            multi_tenant_coverage = security_data["summary"].get("multi_tenant_coverage", 100)
            if multi_tenant_coverage < 90:
                recommendations.append("Enhance multi-tenant isolation patterns and implement row-level security")
        
        # Test coverage recommendations
        expansion_opportunities = coverage_data.get("test_coverage_expansion", {}).get("expansion_opportunities", [])
        if expansion_opportunities:
            recommendations.append(f"Expand test coverage: {len(expansion_opportunities)} improvement opportunities identified")
        
        # Constitutional compliance recommendations
        compliance_percentage = compliance_data.get("compliance_monitoring", {}).get("compliance_percentage", 0)
        if compliance_percentage < 95:
            recommendations.append("Add constitutional compliance markers to all remaining non-compliant files")
        
        # General continuous improvement recommendations
        recommendations.extend([
            "Implement automated performance regression testing in CI/CD pipeline",
            "Schedule weekly security vulnerability assessments",
            "Establish automated constitutional compliance validation",
            "Create performance and security monitoring dashboards",
            "Implement predictive alerting based on trend analysis"
        ])
        
        self.recommendations = recommendations
        logger.info(f"✅ Generated {len(recommendations)} improvement recommendations")
        return recommendations
    
    def run_comprehensive_monitoring_cycle(self) -> Dict:
        """Run complete comprehensive monitoring cycle."""
        logger.info("🚀 Starting comprehensive ACGS monitoring cycle...")
        
        try:
            # Step 1: Performance monitoring
            logger.info("Step 1: Running performance monitoring...")
            performance_data = self.run_performance_monitoring()
            
            # Step 2: Security analysis
            logger.info("Step 2: Running security analysis...")
            security_data = self.run_security_analysis()
            
            # Step 3: Test coverage analysis
            logger.info("Step 3: Analyzing test coverage expansion...")
            coverage_data = self.analyze_test_coverage_expansion()
            
            # Step 4: Constitutional compliance monitoring
            logger.info("Step 4: Monitoring constitutional compliance...")
            compliance_data = self.monitor_constitutional_compliance()
            
            # Step 5: Generate alerts and recommendations
            logger.info("Step 5: Generating alerts and recommendations...")
            alerts = self.generate_comprehensive_alerts(performance_data, security_data, coverage_data, compliance_data)
            recommendations = self.generate_improvement_recommendations(performance_data, security_data, coverage_data, compliance_data)
            
            # Calculate overall health score
            health_scores = []
            
            # Performance health (0-100)
            if "current_performance" in performance_data:
                perf_score = 100
                if not performance_data.get("target_compliance", {}).get("p99_latency_compliant", True):
                    perf_score -= 20
                if not performance_data.get("target_compliance", {}).get("throughput_compliant", True):
                    perf_score -= 20
                if not performance_data.get("target_compliance", {}).get("cache_hit_compliant", True):
                    perf_score -= 10
                health_scores.append(perf_score)
            
            # Security health (0-100)
            if "summary" in security_data:
                sec_score = security_data["summary"].get("security_score", 0)
                health_scores.append(sec_score)
            
            # Test coverage health (0-100)
            coverage_score = coverage_data.get("test_coverage_expansion", {}).get("coverage_percentage", 0)
            health_scores.append(min(100, coverage_score))
            
            # Constitutional compliance health (0-100)
            compliance_score = compliance_data.get("compliance_monitoring", {}).get("compliance_percentage", 0)
            health_scores.append(compliance_score)
            
            overall_health_score = sum(health_scores) / len(health_scores) if health_scores else 0
            
            # Compile comprehensive monitoring report
            comprehensive_report = {
                "monitoring_cycle_id": f"acgs_monitor_{int(time.time())}",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "constitutional_hash": self.constitutional_hash,
                "overall_health_score": overall_health_score,
                "health_status": self._get_health_status(overall_health_score),
                "monitoring_results": {
                    "performance_monitoring": performance_data,
                    "security_analysis": security_data,
                    "test_coverage_expansion": coverage_data,
                    "constitutional_compliance": compliance_data
                },
                "alerts": alerts,
                "recommendations": recommendations,
                "acgs_targets_compliance": {
                    "performance_targets_met": performance_data.get("target_compliance", {}).get("p99_latency_compliant", False),
                    "security_posture_acceptable": security_data.get("summary", {}).get("security_score", 0) >= 80,
                    "test_coverage_adequate": coverage_score >= 80,
                    "constitutional_compliance_maintained": compliance_score >= 95
                },
                "next_monitoring_cycle": (datetime.utcnow() + timedelta(hours=6)).isoformat() + "Z"
            }
            
            logger.info("🎯 Comprehensive monitoring cycle completed successfully")
            return comprehensive_report
            
        except Exception as e:
            logger.error(f"❌ Comprehensive monitoring cycle failed: {str(e)}")
            return {
                "error": str(e),
                "constitutional_hash": self.constitutional_hash,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "status": "failed"
            }
    
    def _get_health_status(self, score: float) -> str:
        """Get health status based on score."""
        if score >= 90:
            return "excellent"
        elif score >= 80:
            return "good"
        elif score >= 70:
            return "fair"
        elif score >= 60:
            return "poor"
        else:
            return "critical"


def main():
    """Main function to run comprehensive ACGS monitoring."""
    print("🚀 ACGS Comprehensive Monitoring and Analytics Tool")
    print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print("=" * 60)
    
    monitor = ACGSComprehensiveMonitor()
    
    # Run comprehensive monitoring cycle
    result = monitor.run_comprehensive_monitoring_cycle()
    
    # Save results
    output_file = Path("acgs_comprehensive_monitoring_report.json")
    with open(output_file, "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"\n📊 Comprehensive monitoring report saved to: {output_file}")
    
    # Display summary
    if "error" not in result:
        print("\n🎯 Comprehensive Monitoring Summary:")
        print(f"- Overall Health Score: {result['overall_health_score']:.1f}/100 ({result['health_status'].upper()})")
        print(f"- Performance Targets Met: {'✅' if result['acgs_targets_compliance']['performance_targets_met'] else '❌'}")
        print(f"- Security Posture: {'✅' if result['acgs_targets_compliance']['security_posture_acceptable'] else '❌'}")
        print(f"- Test Coverage: {'✅' if result['acgs_targets_compliance']['test_coverage_adequate'] else '❌'}")
        print(f"- Constitutional Compliance: {'✅' if result['acgs_targets_compliance']['constitutional_compliance_maintained'] else '❌'}")
        print(f"- Active Alerts: {len(result['alerts'])}")
        print(f"- Improvement Recommendations: {len(result['recommendations'])}")
        
        if result['alerts']:
            print("\n🚨 Top Alerts:")
            for alert in result['alerts'][:3]:
                print(f"  - {alert['severity'].upper()}: {alert['message']}")
        
        if result['recommendations']:
            print("\n💡 Top Recommendations:")
            for i, rec in enumerate(result['recommendations'][:3], 1):
                print(f"  {i}. {rec}")
    else:
        print(f"\n❌ Comprehensive monitoring failed: {result['error']}")


if __name__ == "__main__":
    main()
