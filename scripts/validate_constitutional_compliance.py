#!/usr/bin/env python3
"""
Constitutional Compliance Validation Script for ACGS-1
Validates constitutional hash integrity and governance compliance
"""

import sys
import json
import hashlib
import hmac
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional

# Constitutional reference hash
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
PGC_SERVICE_URL = "http://localhost:8005"

class ConstitutionalComplianceValidator:
    """Validates constitutional compliance for ACGS-1 system"""
    
    def __init__(self):
        self.validation_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "validation_status": "pending",
            "compliance_score": 0.0,
            "checks_performed": [],
            "violations": [],
            "recommendations": []
        }
    
    def validate_constitutional_hash(self) -> bool:
        """Validate constitutional hash integrity"""
        try:
            # Test constitutional hash validation endpoint
            response = requests.get(
                f"{PGC_SERVICE_URL}/api/v1/constitutional/validate",
                params={"validation_level": "comprehensive"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                hash_valid = data.get("hash_valid", False)
                compliance_score = data.get("compliance_score", 0.0)
                
                self.validation_results["checks_performed"].append({
                    "check": "constitutional_hash_validation",
                    "status": "passed" if hash_valid else "failed",
                    "score": compliance_score,
                    "details": data
                })
                
                return hash_valid and compliance_score >= 0.95
            else:
                self.validation_results["violations"].append({
                    "type": "service_unavailable",
                    "message": f"PGC service returned {response.status_code}",
                    "severity": "high"
                })
                return False
                
        except Exception as e:
            self.validation_results["violations"].append({
                "type": "connection_error",
                "message": f"Failed to connect to PGC service: {str(e)}",
                "severity": "critical"
            })
            return False
    
    def validate_governance_workflows(self) -> bool:
        """Validate governance workflow compliance"""
        workflows = [
            "policy_creation",
            "constitutional_compliance", 
            "policy_enforcement",
            "wina_oversight",
            "audit_transparency"
        ]
        
        workflow_status = {}
        all_workflows_valid = True
        
        for workflow in workflows:
            try:
                # Test workflow endpoint
                response = requests.get(
                    f"{PGC_SERVICE_URL}/api/v1/governance/workflows/{workflow}",
                    timeout=5
                )
                
                if response.status_code == 200:
                    workflow_status[workflow] = "operational"
                else:
                    workflow_status[workflow] = "failed"
                    all_workflows_valid = False
                    
            except Exception as e:
                workflow_status[workflow] = "error"
                all_workflows_valid = False
        
        self.validation_results["checks_performed"].append({
            "check": "governance_workflows",
            "status": "passed" if all_workflows_valid else "failed",
            "details": workflow_status
        })
        
        if not all_workflows_valid:
            self.validation_results["violations"].append({
                "type": "workflow_failure",
                "message": "One or more governance workflows are not operational",
                "severity": "high",
                "details": workflow_status
            })
        
        return all_workflows_valid
    
    def validate_service_health(self) -> bool:
        """Validate core service health"""
        services = {
            "auth": 8000,
            "ac": 8001, 
            "integrity": 8002,
            "fv": 8003,
            "gs": 8004,
            "pgc": 8005,
            "ec": 8006
        }
        
        service_status = {}
        healthy_services = 0
        
        for service, port in services.items():
            try:
                response = requests.get(f"http://localhost:{port}/health", timeout=3)
                if response.status_code == 200:
                    service_status[service] = "healthy"
                    healthy_services += 1
                else:
                    service_status[service] = "unhealthy"
            except Exception:
                service_status[service] = "unreachable"
        
        availability_percentage = (healthy_services / len(services)) * 100
        
        self.validation_results["checks_performed"].append({
            "check": "service_health",
            "status": "passed" if availability_percentage >= 75 else "failed",
            "score": availability_percentage / 100,
            "details": {
                "services": service_status,
                "availability_percentage": availability_percentage,
                "healthy_services": healthy_services,
                "total_services": len(services)
            }
        })
        
        if availability_percentage < 75:
            self.validation_results["violations"].append({
                "type": "service_availability",
                "message": f"Service availability {availability_percentage}% below 75% threshold",
                "severity": "high"
            })
        
        return availability_percentage >= 75
    
    def validate_security_posture(self) -> bool:
        """Validate security posture compliance"""
        security_checks = []
        
        # Check for HTTPS enforcement
        try:
            response = requests.get(f"{PGC_SERVICE_URL}/health", timeout=5)
            if response.url.startswith('https://'):
                security_checks.append({"check": "https_enforcement", "status": "passed"})
            else:
                security_checks.append({"check": "https_enforcement", "status": "warning"})
        except Exception:
            security_checks.append({"check": "https_enforcement", "status": "failed"})
        
        # Check constitutional state endpoint
        try:
            response = requests.get(f"{PGC_SERVICE_URL}/api/v1/constitutional/state", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("constitutional_hash") == CONSTITUTIONAL_HASH:
                    security_checks.append({"check": "constitutional_state", "status": "passed"})
                else:
                    security_checks.append({"check": "constitutional_state", "status": "failed"})
            else:
                security_checks.append({"check": "constitutional_state", "status": "failed"})
        except Exception:
            security_checks.append({"check": "constitutional_state", "status": "failed"})
        
        passed_checks = sum(1 for check in security_checks if check["status"] == "passed")
        security_score = passed_checks / len(security_checks) if security_checks else 0
        
        self.validation_results["checks_performed"].append({
            "check": "security_posture",
            "status": "passed" if security_score >= 0.8 else "failed",
            "score": security_score,
            "details": security_checks
        })
        
        return security_score >= 0.8
    
    def calculate_overall_compliance(self) -> float:
        """Calculate overall compliance score"""
        total_score = 0.0
        total_checks = 0
        
        for check in self.validation_results["checks_performed"]:
            if "score" in check:
                total_score += check["score"]
                total_checks += 1
        
        return total_score / total_checks if total_checks > 0 else 0.0
    
    def run_validation(self) -> Dict[str, Any]:
        """Run complete constitutional compliance validation"""
        print("🏛️  Starting Constitutional Compliance Validation...")
        
        # Run all validation checks
        checks = [
            ("Constitutional Hash Validation", self.validate_constitutional_hash),
            ("Governance Workflows", self.validate_governance_workflows),
            ("Service Health", self.validate_service_health),
            ("Security Posture", self.validate_security_posture)
        ]
        
        passed_checks = 0
        for check_name, check_func in checks:
            print(f"   Validating {check_name}...")
            if check_func():
                print(f"   ✅ {check_name}: PASSED")
                passed_checks += 1
            else:
                print(f"   ❌ {check_name}: FAILED")
        
        # Calculate final compliance score
        compliance_score = self.calculate_overall_compliance()
        self.validation_results["compliance_score"] = compliance_score
        
        # Determine overall status
        if passed_checks == len(checks) and compliance_score >= 0.95:
            self.validation_results["validation_status"] = "compliant"
            print(f"\n✅ Constitutional Compliance: PASSED ({compliance_score:.1%})")
        else:
            self.validation_results["validation_status"] = "non_compliant"
            print(f"\n❌ Constitutional Compliance: FAILED ({compliance_score:.1%})")
        
        # Add recommendations
        if compliance_score < 0.95:
            self.validation_results["recommendations"].extend([
                "Review and address all failed validation checks",
                "Ensure all core services are operational",
                "Verify constitutional hash integrity",
                "Test all governance workflows end-to-end"
            ])
        
        return self.validation_results

def main():
    """Main validation function"""
    validator = ConstitutionalComplianceValidator()
    results = validator.run_validation()
    
    # Output results
    print("\n" + "="*60)
    print("CONSTITUTIONAL COMPLIANCE VALIDATION REPORT")
    print("="*60)
    print(f"Timestamp: {results['timestamp']}")
    print(f"Constitutional Hash: {results['constitutional_hash']}")
    print(f"Validation Status: {results['validation_status'].upper()}")
    print(f"Compliance Score: {results['compliance_score']:.1%}")
    print(f"Checks Performed: {len(results['checks_performed'])}")
    print(f"Violations Found: {len(results['violations'])}")
    
    if results['violations']:
        print("\n🚨 VIOLATIONS:")
        for violation in results['violations']:
            print(f"   - {violation['type']}: {violation['message']} ({violation['severity']})")
    
    if results['recommendations']:
        print("\n💡 RECOMMENDATIONS:")
        for rec in results['recommendations']:
            print(f"   - {rec}")
    
    # Save results to file
    with open('constitutional_compliance_report.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Full report saved to: constitutional_compliance_report.json")
    
    # Exit with appropriate code
    if results['validation_status'] == 'compliant':
        print("\n🎉 Constitutional compliance validation PASSED!")
        sys.exit(0)
    else:
        print("\n⚠️  Constitutional compliance validation FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    main()
