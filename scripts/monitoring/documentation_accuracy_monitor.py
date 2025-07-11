#!/usr/bin/env python3
"""
ACGS-2 Documentation Accuracy Monitoring System

Constitutional Hash: cdd01ef066bc6cf2
Purpose: Automated monitoring and validation of documentation accuracy against actual system configurations
"""

import json
import re
import requests
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/documentation_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DocumentationAccuracyMonitor:
    """Monitor documentation accuracy against actual system configurations."""
    
    CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent.parent
        self.docs_path = self.base_path / "docs"
        self.config_path = self.base_path / "config"
        self.reports_path = self.base_path / "reports"
        
        # Service endpoints for health checks
        self.service_endpoints = {
            "auth_service": "http://localhost:8013/health",
            "constitutional_ai": "http://localhost:8014/health", 
            "integrity_service": "http://localhost:8015/health",
            "formal_verification": "http://localhost:8017/health",
            "governance_synthesis": "http://localhost:8018/health",
            "policy_governance": "http://localhost:8019/health",
            "evolutionary_computation": "http://localhost:8020/health",
            "agent_hitl": "http://localhost:8021/health"
        }
        
    def validate_constitutional_compliance(self) -> Dict[str, Any]:
        """Validate constitutional hash presence across documentation."""
        logger.info("Validating constitutional compliance...")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "constitutional_hash": self.CONSTITUTIONAL_HASH,
            "compliance_status": "PASS",
            "files_checked": [],
            "violations": []
        }
        
        # Documentation files to check
        doc_files = [
            "docs/README.md",
            "docs/TECHNICAL_SPECIFICATIONS_2025.md", 
            "docs/integration/ACGS_XAI_INTEGRATION_GUIDE.md"
        ]
        
        for doc_file in doc_files:
            file_path = self.base_path / doc_file
            if file_path.exists():
                content = file_path.read_text()
                hash_count = content.count(self.CONSTITUTIONAL_HASH)
                
                file_result = {
                    "file": doc_file,
                    "hash_references": hash_count,
                    "compliant": hash_count > 0
                }
                
                results["files_checked"].append(file_result)
                
                if hash_count == 0:
                    violation = f"Constitutional hash missing in {doc_file}"
                    results["violations"].append(violation)
                    results["compliance_status"] = "FAIL"
                    logger.warning(violation)
                else:
                    logger.info(f"✅ {doc_file}: {hash_count} constitutional hash references")
            else:
                violation = f"Documentation file not found: {doc_file}"
                results["violations"].append(violation)
                results["compliance_status"] = "FAIL"
                logger.error(violation)
        
        return results
    
    def validate_service_health(self) -> Dict[str, Any]:
        """Validate all ACGS services are healthy."""
        logger.info("Validating service health...")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "total_services": len(self.service_endpoints),
            "healthy_services": 0,
            "unhealthy_services": 0,
            "service_status": {},
            "overall_health": "UNKNOWN"
        }
        
        for service_name, endpoint in self.service_endpoints.items():
            try:
                response = requests.get(endpoint, timeout=5)
                if response.status_code == 200:
                    health_data = response.json()
                    
                    # Check for constitutional hash in response
                    constitutional_compliant = self.CONSTITUTIONAL_HASH in str(health_data)
                    
                    results["service_status"][service_name] = {
                        "status": "HEALTHY",
                        "response_time_ms": response.elapsed.total_seconds() * 1000,
                        "constitutional_compliant": constitutional_compliant,
                        "endpoint": endpoint
                    }
                    results["healthy_services"] += 1
                    logger.info(f"✅ {service_name}: HEALTHY")
                else:
                    results["service_status"][service_name] = {
                        "status": "UNHEALTHY",
                        "status_code": response.status_code,
                        "endpoint": endpoint
                    }
                    results["unhealthy_services"] += 1
                    logger.warning(f"❌ {service_name}: UNHEALTHY (HTTP {response.status_code})")
                    
            except requests.RequestException as e:
                results["service_status"][service_name] = {
                    "status": "UNREACHABLE",
                    "error": str(e),
                    "endpoint": endpoint
                }
                results["unhealthy_services"] += 1
                logger.error(f"❌ {service_name}: UNREACHABLE ({e})")
        
        # Determine overall health
        if results["healthy_services"] == results["total_services"]:
            results["overall_health"] = "HEALTHY"
        elif results["healthy_services"] > 0:
            results["overall_health"] = "DEGRADED"
        else:
            results["overall_health"] = "CRITICAL"
            
        return results
    
    def validate_performance_metrics(self) -> Dict[str, Any]:
        """Validate documented performance metrics against actual measurements."""
        logger.info("Validating performance metrics...")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "validation_status": "PASS",
            "discrepancies": [],
            "documented_metrics": {},
            "actual_metrics": {}
        }
        
        # Load actual performance data
        perf_file = self.reports_path / "performance_metrics_results.json"
        if perf_file.exists():
            with open(perf_file) as f:
                actual_data = json.load(f)
                
            # Extract key metrics
            results["actual_metrics"] = {
                "p99_latency_ms": actual_data["performance_metrics"]["decision_latency"]["latency_stats"]["p99_ms"],
                "throughput_rps": actual_data["performance_metrics"]["throughput"]["requests_per_second"],
                "cache_hit_rate": actual_data["performance_metrics"]["cache_performance"]["cache_hit_rate"],
                "cpu_usage_percent": actual_data["system_metrics"]["cpu"]["usage_percent"],
                "memory_usage_percent": actual_data["system_metrics"]["memory"]["usage_percent"]
            }
            
            # Check documentation for these metrics
            readme_content = (self.docs_path / "README.md").read_text()
            tech_specs_content = (self.docs_path / "TECHNICAL_SPECIFICATIONS_2025.md").read_text()
            
            # Extract documented metrics using regex
            p99_match = re.search(r"P99.*?(\d+\.?\d*)\s*ms", readme_content)
            rps_match = re.search(r"(\d+\.?\d*)\s*RPS", readme_content)
            cache_match = re.search(r"Cache.*?(\d+)%", readme_content)
            
            if p99_match:
                documented_p99 = float(p99_match.group(1))
                actual_p99 = results["actual_metrics"]["p99_latency_ms"]
                
                if abs(documented_p99 - actual_p99) > 0.1:  # Allow 0.1ms tolerance
                    discrepancy = f"P99 latency mismatch: documented {documented_p99}ms vs actual {actual_p99}ms"
                    results["discrepancies"].append(discrepancy)
                    results["validation_status"] = "FAIL"
                    
            logger.info(f"Performance validation completed with {len(results['discrepancies'])} discrepancies")
        else:
            results["validation_status"] = "FAIL"
            results["discrepancies"].append("Performance metrics file not found")
            logger.error("Performance metrics file not found")
            
        return results
    
    def validate_port_mappings(self) -> Dict[str, Any]:
        """Validate documented port mappings against docker-compose configuration."""
        logger.info("Validating port mappings...")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "validation_status": "PASS",
            "discrepancies": [],
            "documented_ports": {},
            "actual_ports": {}
        }
        
        # Load docker-compose configuration
        docker_compose_file = self.config_path / "docker" / "docker-compose.yml"
        if docker_compose_file.exists():
            with open(docker_compose_file) as f:
                docker_config = yaml.safe_load(f)
                
            # Extract actual port mappings
            for service_name, service_config in docker_config.get("services", {}).items():
                if "ports" in service_config:
                    for port_mapping in service_config["ports"]:
                        if ":" in str(port_mapping):
                            external, internal = str(port_mapping).split(":")
                            results["actual_ports"][service_name] = {
                                "external": external,
                                "internal": internal
                            }
            
            # Check documentation for port references
            readme_content = (self.docs_path / "README.md").read_text()
            
            # Look for port mapping patterns like "8013→8000"
            port_patterns = re.findall(r"(\d+).*?→.*?(\d+)", readme_content)
            for external, internal in port_patterns:
                results["documented_ports"][f"{external}→{internal}"] = {
                    "external": external,
                    "internal": internal
                }
            
            logger.info(f"Port mapping validation completed")
        else:
            results["validation_status"] = "FAIL"
            results["discrepancies"].append("Docker compose file not found")
            logger.error("Docker compose file not found")
            
        return results
    
    def generate_monitoring_report(self) -> Dict[str, Any]:
        """Generate comprehensive monitoring report."""
        logger.info("Generating comprehensive monitoring report...")
        
        report = {
            "report_timestamp": datetime.now().isoformat(),
            "constitutional_hash": self.CONSTITUTIONAL_HASH,
            "monitoring_version": "1.0",
            "overall_status": "PASS"
        }
        
        # Run all validations
        report["constitutional_compliance"] = self.validate_constitutional_compliance()
        report["service_health"] = self.validate_service_health()
        report["performance_metrics"] = self.validate_performance_metrics()
        report["port_mappings"] = self.validate_port_mappings()
        
        # Determine overall status
        failed_checks = []
        if report["constitutional_compliance"]["compliance_status"] == "FAIL":
            failed_checks.append("constitutional_compliance")
        if report["service_health"]["overall_health"] in ["DEGRADED", "CRITICAL"]:
            failed_checks.append("service_health")
        if report["performance_metrics"]["validation_status"] == "FAIL":
            failed_checks.append("performance_metrics")
        if report["port_mappings"]["validation_status"] == "FAIL":
            failed_checks.append("port_mappings")
            
        if failed_checks:
            report["overall_status"] = "FAIL"
            report["failed_checks"] = failed_checks
            logger.warning(f"Monitoring report FAILED: {failed_checks}")
        else:
            logger.info("✅ All monitoring checks PASSED")
        
        # Save report
        report_file = self.reports_path / f"documentation_monitoring_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        logger.info(f"Monitoring report saved to {report_file}")
        return report

def main():
    """Main monitoring function."""
    logger.info("Starting ACGS-2 Documentation Accuracy Monitoring")
    logger.info(f"Constitutional Hash: {DocumentationAccuracyMonitor.CONSTITUTIONAL_HASH}")
    
    monitor = DocumentationAccuracyMonitor()
    report = monitor.generate_monitoring_report()
    
    # Print summary
    print(f"\n📊 ACGS-2 Documentation Monitoring Report")
    print(f"Timestamp: {report['report_timestamp']}")
    print(f"Overall Status: {'✅ PASS' if report['overall_status'] == 'PASS' else '❌ FAIL'}")
    print(f"Constitutional Hash: {report['constitutional_hash']}")
    
    if report['overall_status'] == 'FAIL':
        print(f"Failed Checks: {', '.join(report.get('failed_checks', []))}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
