#!/usr/bin/env python3
"""
ACGS-2 Constitutional Compliance Validator for CI/CD
Constitutional Hash: cdd01ef066bc6cf2

Validates constitutional compliance in test coverage and service implementations.
"""

import argparse
import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional

class ConstitutionalComplianceValidator:
    """Validates constitutional compliance across ACGS services"""
    
    def __init__(self, constitutional_hash: str = "cdd01ef066bc6cf2"):
        self.constitutional_hash = constitutional_hash
        self.compliance_score = 100
        self.violations = []
        
    def validate_service_compliance(self, service: str, coverage_file: Optional[str] = None) -> Dict[str, Any]:
        """Validate constitutional compliance for a specific service"""
        
        print(f"🔍 Validating constitutional compliance for service: {service}")
        print(f"Constitutional Hash: {self.constitutional_hash}")
        
        # Check if service exists
        service_path = Path(f"services/{service}")
        if not service_path.exists():
            # Try different service path patterns
            service_patterns = [
                f"services/core/{service}",
                f"services/platform_services/{service}",
                f"services/core/constitutional-ai/ac_service" if service == "ac-service" else None,
                f"services/core/governance-synthesis/gs_service" if service == "gs-service" else None,
                f"services/core/formal-verification/fv_service" if service == "fv-service" else None,
                f"services/core/policy-governance/pgc_service" if service == "pgc-service" else None,
                f"services/core/evolutionary-computation/ec_service" if service == "ec-service" else None,
                f"services/platform_services/authentication/auth_service" if service == "auth-service" else None,
                f"services/platform_services/integrity/integrity_service" if service == "integrity-service" else None,
            ]
            
            for pattern in service_patterns:
                if pattern and Path(pattern).exists():
                    service_path = Path(pattern)
                    break
            else:
                print(f"⚠️ Service {service} not found, skipping validation")
                return self._create_compliance_report(service, "service_not_found")
        
        print(f"📁 Service path: {service_path}")
        
        # Validate constitutional hash presence
        hash_found = self._check_constitutional_hash(service_path)
        
        # Validate coverage if provided
        coverage_valid = True
        coverage_score = 0
        
        if coverage_file and os.path.exists(coverage_file):
            coverage_valid, coverage_score = self._validate_coverage(coverage_file)
        elif coverage_file:
            print(f"⚠️ Coverage file {coverage_file} not found")
        
        # Validate service structure
        structure_valid = self._validate_service_structure(service_path)
        
        # Calculate compliance score
        compliance_score = self._calculate_compliance_score(
            hash_found, coverage_valid, structure_valid, coverage_score
        )
        
        return self._create_compliance_report(
            service, "validated", 
            hash_found=hash_found,
            coverage_valid=coverage_valid,
            structure_valid=structure_valid,
            coverage_score=coverage_score,
            compliance_score=compliance_score
        )
    
    def _check_constitutional_hash(self, service_path: Path) -> bool:
        """Check if constitutional hash is present in service files"""
        
        hash_found = False
        search_patterns = ["*.py", "*.md", "*.yaml", "*.yml", "*.json"]
        
        for pattern in search_patterns:
            for file_path in service_path.rglob(pattern):
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if self.constitutional_hash in content:
                            print(f"✅ Constitutional hash found in {file_path}")
                            hash_found = True
                            break
                except Exception:
                    continue
            if hash_found:
                break
        
        if not hash_found:
            print(f"❌ Constitutional hash {self.constitutional_hash} not found in {service_path}")
            self.violations.append(f"Missing constitutional hash in {service_path}")
        
        return hash_found
    
    def _validate_coverage(self, coverage_file: str) -> tuple[bool, float]:
        """Validate test coverage meets constitutional requirements"""
        
        try:
            with open(coverage_file, 'r') as f:
                coverage_data = json.load(f)
            
            # Extract coverage percentage
            coverage_percent = 0
            if 'totals' in coverage_data and 'percent_covered' in coverage_data['totals']:
                coverage_percent = coverage_data['totals']['percent_covered']
            elif 'coverage' in coverage_data:
                coverage_percent = coverage_data['coverage']
            
            print(f"📊 Coverage: {coverage_percent}%")
            
            # Constitutional requirement: minimum 80% coverage
            if coverage_percent >= 80:
                print("✅ Coverage meets constitutional requirements")
                return True, coverage_percent
            else:
                print(f"❌ Coverage {coverage_percent}% below constitutional minimum of 80%")
                self.violations.append(f"Coverage {coverage_percent}% below minimum")
                return False, coverage_percent
                
        except Exception as e:
            print(f"❌ Error validating coverage: {e}")
            return False, 0
    
    def _validate_service_structure(self, service_path: Path) -> bool:
        """Validate service follows constitutional structure requirements"""
        
        required_patterns = [
            "main.py",  # Entry point
            "*.py",     # Python files
        ]
        
        structure_valid = True
        
        for pattern in required_patterns:
            if not list(service_path.rglob(pattern)):
                print(f"⚠️ Missing required pattern: {pattern}")
                structure_valid = False
        
        # Check for basic service structure
        if service_path.name.endswith('_service') or 'main.py' in [f.name for f in service_path.rglob('*.py')]:
            print("✅ Valid service structure detected")
        else:
            print("⚠️ Service structure may not follow conventions")
        
        return structure_valid
    
    def _calculate_compliance_score(self, hash_found: bool, coverage_valid: bool, 
                                  structure_valid: bool, coverage_score: float) -> float:
        """Calculate overall constitutional compliance score"""
        
        score = 100.0
        
        # Deduct points for violations
        if not hash_found:
            score -= 30  # Major violation
        if not coverage_valid:
            score -= 20  # Significant violation
        if not structure_valid:
            score -= 10  # Minor violation
        
        # Bonus for high coverage
        if coverage_score >= 90:
            score += 5
        
        return max(0, min(100, score))
    
    def _create_compliance_report(self, service: str, status: str, **kwargs) -> Dict[str, Any]:
        """Create constitutional compliance report"""
        
        return {
            "service": service,
            "status": status,
            "constitutional_hash": self.constitutional_hash,
            "timestamp": "2025-07-11T00:00:00Z",
            "compliance_score": kwargs.get('compliance_score', 0),
            "hash_found": kwargs.get('hash_found', False),
            "coverage_valid": kwargs.get('coverage_valid', False),
            "structure_valid": kwargs.get('structure_valid', False),
            "coverage_score": kwargs.get('coverage_score', 0),
            "violations": self.violations.copy()
        }

def main():
    """Main execution function"""
    
    parser = argparse.ArgumentParser(
        description='ACGS-2 Constitutional Compliance Validator'
    )
    parser.add_argument('--service', required=True, 
                       help='Service name to validate')
    parser.add_argument('--coverage-file', 
                       help='Path to coverage JSON file')
    parser.add_argument('--constitutional-hash', 
                       default='cdd01ef066bc6cf2',
                       help='Constitutional hash to validate')
    parser.add_argument('--output-file',
                       help='Output file for compliance report')
    
    args = parser.parse_args()
    
    # Initialize validator
    validator = ConstitutionalComplianceValidator(args.constitutional_hash)
    
    # Run validation
    report = validator.validate_service_compliance(
        args.service, 
        args.coverage_file
    )
    
    # Output report
    if args.output_file:
        with open(args.output_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"📄 Report saved to: {args.output_file}")
    
    # Print summary
    print(f"\n📋 Constitutional Compliance Summary")
    print(f"Service: {report['service']}")
    print(f"Compliance Score: {report['compliance_score']}/100")
    print(f"Constitutional Hash: {report['constitutional_hash']}")
    
    if report['violations']:
        print(f"\n⚠️ Violations:")
        for violation in report['violations']:
            print(f"  - {violation}")
    
    # Exit with appropriate code
    if report['compliance_score'] >= 80:
        print(f"\n✅ Constitutional compliance validation PASSED")
        sys.exit(0)
    else:
        print(f"\n❌ Constitutional compliance validation FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()