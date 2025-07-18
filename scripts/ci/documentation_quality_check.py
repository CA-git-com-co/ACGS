#!/usr/bin/env python3
'''
ACGS-2 Documentation Quality Check for CI/CD
Constitutional Hash: cdd01ef066bc6cf2
'''

import sys
import json
from pathlib import Path

def check_documentation_quality():
    '''Check documentation quality and return exit code'''
    
    # Import the validator
    sys.path.append(str(Path(__file__).parent.parent / "validation"))
    from documentation_standards_validator import DocumentationStandardsValidator
    
    validator = DocumentationStandardsValidator()
    
    # Run validation
    metrics = validator.validate_all_documentation()
    cross_ref_metrics = validator.validate_cross_reference_integrity()
    
    # Check quality thresholds
    quality_passed = True
    issues = []
    
    # Check section compliance (target: >95%)
    if metrics["section_compliance_rate"] < 95.0:
        issues.append(f"Section compliance below target: {metrics['section_compliance_rate']}% (target: >95%)")
        quality_passed = False
        
    # Check constitutional hash compliance (target: >98%)
    if metrics["hash_compliance_rate"] < 98.0:
        issues.append(f"Constitutional hash compliance below target: {metrics['hash_compliance_rate']}% (target: >98%)")
        quality_passed = False
        
    # Check cross-reference validity (target: >88%)
    if cross_ref_metrics.get("link_validity_rate", 0) < 88.0:
        issues.append(f"Cross-reference validity below target: {cross_ref_metrics.get('link_validity_rate', 0)}% (target: >88%)")
        quality_passed = False
        
    # Generate report
    report = {
        "quality_passed": quality_passed,
        "issues": issues,
        "metrics": metrics,
        "cross_reference_metrics": cross_ref_metrics,
        "constitutional_hash": "cdd01ef066bc6cf2"
    }
    
    # Save report
    report_path = Path("reports/validation/ci_documentation_quality_check.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    # Print results
    if quality_passed:
        print("✅ Documentation quality checks PASSED")
        return 0
    else:
        print("❌ Documentation quality checks FAILED")
        for issue in issues:
            print(f"  - {issue}")
        return 1

if __name__ == "__main__":
    exit_code = check_documentation_quality()
    sys.exit(exit_code)
