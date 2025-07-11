#!/usr/bin/env python3
"""
ACGS-2 Coverage Threshold Checker
Constitutional Hash: cdd01ef066bc6cf2

Checks if coverage meets constitutional requirements and thresholds.
"""

import argparse
import json
import sys
from typing import Dict, List, Any

class CoverageThresholdChecker:
    """Checks coverage against constitutional thresholds"""
    
    def __init__(self, constitutional_hash: str = "cdd01ef066bc6cf2"):
        self.constitutional_hash = constitutional_hash
        self.violations = []
        
    def check_thresholds(self, coverage_file: str, fail_on_violation: bool = False) -> Dict[str, Any]:
        """Check coverage thresholds against constitutional requirements"""
        
        print(f"🔍 Checking ACGS-2 Coverage Thresholds")
        print(f"Constitutional Hash: {self.constitutional_hash}")
        
        # Load coverage data
        try:
            with open(coverage_file, 'r') as f:
                coverage_data = json.load(f)
        except Exception as e:
            print(f"❌ Error loading coverage file: {e}")
            return self._create_failure_report("file_not_found", str(e))
        
        # Constitutional thresholds
        min_coverage = 80.0
        min_constitutional_coverage = 95.0
        
        # Check overall coverage
        overall_coverage = coverage_data.get('overall', {}).get('average_coverage', 0)
        constitutional_compliance = coverage_data.get('summary', {}).get('constitutional_compliance', 0)
        
        print(f"📊 Overall Coverage: {overall_coverage:.1f}%")
        print(f"🔒 Constitutional Compliance: {constitutional_compliance:.1f}%")
        
        # Check thresholds
        coverage_passed = overall_coverage >= min_coverage
        constitutional_passed = constitutional_compliance >= min_constitutional_coverage
        
        if not coverage_passed:
            violation = f"Overall coverage {overall_coverage:.1f}% below minimum {min_coverage}%"
            self.violations.append(violation)
            print(f"❌ {violation}")
        else:
            print(f"✅ Coverage threshold met: {overall_coverage:.1f}% >= {min_coverage}%")
        
        if not constitutional_passed:
            violation = f"Constitutional compliance {constitutional_compliance:.1f}% below minimum {min_constitutional_coverage}%"
            self.violations.append(violation)
            print(f"❌ {violation}")
        else:
            print(f"✅ Constitutional threshold met: {constitutional_compliance:.1f}% >= {min_constitutional_coverage}%")
        
        # Check individual services
        services_below_threshold = []
        for service, data in coverage_data.get('services', {}).items():
            service_coverage = data.get('line_coverage', 0)
            if service_coverage < min_coverage:
                services_below_threshold.append({
                    'service': service,
                    'coverage': service_coverage,
                    'shortfall': min_coverage - service_coverage
                })
        
        if services_below_threshold:
            print(f"\n⚠️ Services below {min_coverage}% threshold:")
            for service in services_below_threshold:
                print(f"  - {service['service']}: {service['coverage']:.1f}% (shortfall: {service['shortfall']:.1f}%)")
        
        # Create report
        report = self._create_threshold_report(
            coverage_data, coverage_passed, constitutional_passed, 
            services_below_threshold, min_coverage, min_constitutional_coverage
        )
        
        # Determine if we should fail
        should_fail = False
        if fail_on_violation and self.violations:
            should_fail = True
        
        # Print summary
        self._print_summary(report, should_fail)
        
        return report
    
    def _create_threshold_report(self, coverage_data: Dict, coverage_passed: bool, 
                               constitutional_passed: bool, services_below: List,
                               min_coverage: float, min_constitutional: float) -> Dict[str, Any]:
        """Create threshold check report"""
        
        overall_passed = coverage_passed and constitutional_passed and len(services_below) == 0
        
        return {
            "constitutional_hash": self.constitutional_hash,
            "timestamp": "2025-07-11T00:00:00Z",
            "thresholds": {
                "min_coverage": min_coverage,
                "min_constitutional_coverage": min_constitutional,
            },
            "results": {
                "overall_passed": overall_passed,
                "coverage_passed": coverage_passed,
                "constitutional_passed": constitutional_passed,
                "services_below_threshold": len(services_below),
                "total_services": len(coverage_data.get('services', {}))
            },
            "metrics": {
                "overall_coverage": coverage_data.get('overall', {}).get('average_coverage', 0),
                "constitutional_compliance": coverage_data.get('summary', {}).get('constitutional_compliance', 0),
                "services_above_threshold": coverage_data.get('overall', {}).get('services_above_threshold', 0)
            },
            "violations": self.violations.copy(),
            "services_needing_improvement": services_below,
            "recommendations": self._generate_threshold_recommendations(
                coverage_passed, constitutional_passed, services_below
            )
        }
    
    def _create_failure_report(self, reason: str, details: str) -> Dict[str, Any]:
        """Create failure report when check cannot be performed"""
        
        return {
            "constitutional_hash": self.constitutional_hash,
            "timestamp": "2025-07-11T00:00:00Z",
            "status": "failed",
            "reason": reason,
            "details": details,
            "results": {
                "overall_passed": False,
                "coverage_passed": False,
                "constitutional_passed": False
            }
        }
    
    def _generate_threshold_recommendations(self, coverage_passed: bool, 
                                          constitutional_passed: bool, 
                                          services_below: List) -> List[str]:
        """Generate recommendations based on threshold results"""
        
        recommendations = []
        
        if not coverage_passed:
            recommendations.append("Increase overall test coverage to meet 80% minimum threshold")
        
        if not constitutional_passed:
            recommendations.append("Improve constitutional compliance to meet 95% requirement")
        
        if services_below:
            recommendations.append(f"Focus on improving {len(services_below)} services below threshold")
            for service in services_below[:3]:  # Top 3 services needing improvement
                recommendations.append(
                    f"Prioritize {service['service']} (needs {service['shortfall']:.1f}% improvement)"
                )
        
        if coverage_passed and constitutional_passed and not services_below:
            recommendations.append("Excellent! All thresholds met. Consider setting higher targets")
        
        recommendations.append(f"Maintain constitutional compliance (hash: {self.constitutional_hash})")
        
        return recommendations
    
    def _print_summary(self, report: Dict, should_fail: bool):
        """Print threshold check summary"""
        
        print(f"\n📋 Coverage Threshold Check Summary")
        print(f"Overall Result: {'✅ PASSED' if report['results']['overall_passed'] else '❌ FAILED'}")
        print(f"Coverage Threshold: {'✅ PASSED' if report['results']['coverage_passed'] else '❌ FAILED'}")
        print(f"Constitutional Threshold: {'✅ PASSED' if report['results']['constitutional_passed'] else '❌ FAILED'}")
        print(f"Services Below Threshold: {report['results']['services_below_threshold']}")
        
        if report.get('violations'):
            print(f"\n⚠️ Violations:")
            for violation in report['violations']:
                print(f"  - {violation}")
        
        if report.get('recommendations'):
            print(f"\n💡 Recommendations:")
            for rec in report['recommendations'][:3]:  # Show top 3
                print(f"  - {rec}")
        
        if should_fail:
            print(f"\n❌ FAILING due to threshold violations")
        else:
            print(f"\n✅ Threshold check completed")

def main():
    """Main execution function"""
    
    parser = argparse.ArgumentParser(
        description='ACGS-2 Coverage Threshold Checker'
    )
    parser.add_argument('--coverage-file', 
                       default='aggregated_coverage.json',
                       help='Aggregated coverage file to check')
    parser.add_argument('--constitutional-hash', 
                       default='cdd01ef066bc6cf2',
                       help='Constitutional hash to validate')
    parser.add_argument('--fail-on-threshold-violation', 
                       action='store_true',
                       help='Exit with error code if thresholds not met')
    parser.add_argument('--output-file',
                       help='Save threshold report to file')
    
    args = parser.parse_args()
    
    # Initialize checker
    checker = CoverageThresholdChecker(args.constitutional_hash)
    
    # Run threshold check
    report = checker.check_thresholds(
        args.coverage_file, 
        args.fail_on_threshold_violation
    )
    
    # Save report if requested
    if args.output_file:
        with open(args.output_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"📄 Threshold report saved to: {args.output_file}")
    
    # Exit with appropriate code
    if args.fail_on_threshold_violation and not report['results']['overall_passed']:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()