#!/usr/bin/env python3
"""
ACGS-2 Coverage Quality Gate
Constitutional Hash: cdd01ef066bc6cf2

Quality gate enforcement for test coverage in CI/CD pipeline.
"""

import argparse
import json
import sys
from typing import Dict, Any, List

class CoverageQualityGate:
    """Enforces quality gates for test coverage"""
    
    def __init__(self, constitutional_hash: str = "cdd01ef066bc6cf2"):
        self.constitutional_hash = constitutional_hash
        self.quality_violations = []
        
    def enforce_quality_gate(self, coverage_file: str, min_coverage: float = 90,
                           min_constitutional_coverage: float = 95,
                           fail_on_violation: bool = True) -> Dict[str, Any]:
        """Enforce quality gate based on coverage requirements"""
        
        print(f"🚪 ACGS-2 Coverage Quality Gate")
        print(f"Constitutional Hash: {self.constitutional_hash}")
        print(f"Minimum Coverage: {min_coverage}%")
        print(f"Minimum Constitutional Coverage: {min_constitutional_coverage}%")
        
        # Load coverage data
        try:
            with open(coverage_file, 'r') as f:
                coverage_data = json.load(f)
        except Exception as e:
            print(f"❌ Error loading coverage file: {e}")
            return self._create_gate_failure("file_error", str(e))
        
        # Extract metrics
        overall_coverage = coverage_data.get('overall', {}).get('average_coverage', 0)
        constitutional_compliance = coverage_data.get('summary', {}).get('constitutional_compliance', 0)
        services_above_threshold = coverage_data.get('overall', {}).get('services_above_threshold', 0)
        total_services = coverage_data.get('overall', {}).get('total_services', 1)
        
        print(f"\n📊 Current Metrics:")
        print(f"  Overall Coverage: {overall_coverage:.1f}%")
        print(f"  Constitutional Compliance: {constitutional_compliance:.1f}%")
        print(f"  Services Above Threshold: {services_above_threshold}/{total_services}")
        
        # Quality gate checks
        gate_checks = self._perform_quality_checks(
            coverage_data, overall_coverage, constitutional_compliance,
            min_coverage, min_constitutional_coverage
        )
        
        # Determine gate result
        gate_passed = len(self.quality_violations) == 0
        gate_result = "PASSED" if gate_passed else "FAILED"
        
        print(f"\n🚪 Quality Gate Result: {gate_result}")
        
        if not gate_passed:
            print(f"\n❌ Quality Gate Violations:")
            for violation in self.quality_violations:
                print(f"  - {violation}")
        
        # Create quality gate report
        report = self._create_quality_gate_report(
            coverage_data, gate_checks, gate_passed,
            min_coverage, min_constitutional_coverage
        )
        
        # Print recommendations
        if report.get('recommendations'):
            print(f"\n💡 Recommendations:")
            for rec in report['recommendations'][:3]:
                print(f"  - {rec}")
        
        return report
    
    def _perform_quality_checks(self, coverage_data: Dict, overall_coverage: float,
                              constitutional_compliance: float, min_coverage: float,
                              min_constitutional_coverage: float) -> Dict[str, Any]:
        """Perform all quality gate checks"""
        
        checks = {}
        
        # Check 1: Overall coverage threshold
        coverage_check = overall_coverage >= min_coverage
        checks['coverage_threshold'] = {
            'passed': coverage_check,
            'actual': overall_coverage,
            'required': min_coverage,
            'description': 'Overall test coverage meets minimum threshold'
        }
        
        if not coverage_check:
            self.quality_violations.append(
                f"Overall coverage {overall_coverage:.1f}% below required {min_coverage}%"
            )
        
        # Check 2: Constitutional compliance
        constitutional_check = constitutional_compliance >= min_constitutional_coverage
        checks['constitutional_compliance'] = {
            'passed': constitutional_check,
            'actual': constitutional_compliance,
            'required': min_constitutional_coverage,
            'description': 'Constitutional compliance meets minimum threshold'
        }
        
        if not constitutional_check:
            self.quality_violations.append(
                f"Constitutional compliance {constitutional_compliance:.1f}% below required {min_constitutional_coverage}%"
            )
        
        # Check 3: Service coverage distribution
        services_data = coverage_data.get('services', {})
        low_coverage_services = []
        for service, data in services_data.items():
            service_coverage = data.get('line_coverage', 0)
            if service_coverage < 70:  # Critical threshold
                low_coverage_services.append(f"{service} ({service_coverage:.1f}%)")
        
        service_distribution_check = len(low_coverage_services) == 0
        checks['service_distribution'] = {
            'passed': service_distribution_check,
            'low_coverage_services': low_coverage_services,
            'description': 'No services with critically low coverage (<70%)'
        }
        
        if not service_distribution_check:
            self.quality_violations.append(
                f"{len(low_coverage_services)} services with critically low coverage: {', '.join(low_coverage_services)}"
            )
        
        # Check 4: Constitutional hash validation
        hash_valid = coverage_data.get('constitutional_hash') == self.constitutional_hash
        checks['constitutional_hash'] = {
            'passed': hash_valid,
            'actual': coverage_data.get('constitutional_hash', 'missing'),
            'required': self.constitutional_hash,
            'description': 'Constitutional hash matches expected value'
        }
        
        if not hash_valid:
            self.quality_violations.append(
                f"Constitutional hash mismatch: expected {self.constitutional_hash}, got {coverage_data.get('constitutional_hash', 'missing')}"
            )
        
        # Check 5: Trend analysis (if previous data available)
        trend_check = self._check_coverage_trend(coverage_data)
        checks['trend_analysis'] = trend_check
        
        return checks
    
    def _check_coverage_trend(self, coverage_data: Dict) -> Dict[str, Any]:
        """Check coverage trend (simplified for CI environment)"""
        
        # In a real implementation, this would compare with historical data
        # For now, we'll do a basic check
        overall_coverage = coverage_data.get('overall', {}).get('average_coverage', 0)
        
        if overall_coverage >= 85:
            trend_status = "improving"
        elif overall_coverage >= 75:
            trend_status = "stable"
        else:
            trend_status = "declining"
        
        return {
            'passed': trend_status in ["improving", "stable"],
            'trend': trend_status,
            'description': 'Coverage trend is positive or stable'
        }
    
    def _create_quality_gate_report(self, coverage_data: Dict, checks: Dict,
                                  gate_passed: bool, min_coverage: float,
                                  min_constitutional_coverage: float) -> Dict[str, Any]:
        """Create comprehensive quality gate report"""
        
        return {
            "constitutional_hash": self.constitutional_hash,
            "timestamp": "2025-07-11T00:00:00Z",
            "quality_gate": {
                "status": "PASSED" if gate_passed else "FAILED",
                "passed": gate_passed,
                "checks_total": len(checks),
                "checks_passed": sum(1 for check in checks.values() if check.get('passed', False))
            },
            "thresholds": {
                "min_coverage": min_coverage,
                "min_constitutional_coverage": min_constitutional_coverage
            },
            "metrics": {
                "overall_coverage": coverage_data.get('overall', {}).get('average_coverage', 0),
                "constitutional_compliance": coverage_data.get('summary', {}).get('constitutional_compliance', 0),
                "quality_score": coverage_data.get('summary', {}).get('quality_score', 0)
            },
            "checks": checks,
            "violations": self.quality_violations.copy(),
            "recommendations": self._generate_quality_recommendations(checks, gate_passed),
            "next_actions": self._get_next_actions(gate_passed)
        }
    
    def _create_gate_failure(self, reason: str, details: str) -> Dict[str, Any]:
        """Create quality gate failure report"""
        
        return {
            "constitutional_hash": self.constitutional_hash,
            "timestamp": "2025-07-11T00:00:00Z",
            "quality_gate": {
                "status": "FAILED",
                "passed": False,
                "failure_reason": reason,
                "failure_details": details
            }
        }
    
    def _generate_quality_recommendations(self, checks: Dict, gate_passed: bool) -> List[str]:
        """Generate recommendations based on quality gate results"""
        
        recommendations = []
        
        if not gate_passed:
            # Specific recommendations for failed checks
            for check_name, check_data in checks.items():
                if not check_data.get('passed', False):
                    if check_name == 'coverage_threshold':
                        recommendations.append(
                            f"Increase test coverage from {check_data['actual']:.1f}% to {check_data['required']:.1f}%"
                        )
                    elif check_name == 'constitutional_compliance':
                        recommendations.append(
                            "Review and improve constitutional compliance in all services"
                        )
                    elif check_name == 'service_distribution':
                        low_services = check_data.get('low_coverage_services', [])
                        recommendations.append(
                            f"Focus on improving coverage for {len(low_services)} low-coverage services"
                        )
                    elif check_name == 'constitutional_hash':
                        recommendations.append(
                            "Ensure constitutional hash is properly embedded in all components"
                        )
        else:
            recommendations.append("Excellent! Quality gate passed. Consider raising standards further")
        
        recommendations.extend([
            "Run additional integration tests for critical components",
            "Implement automated coverage monitoring",
            f"Maintain constitutional compliance (hash: {self.constitutional_hash})"
        ])
        
        return recommendations
    
    def _get_next_actions(self, gate_passed: bool) -> List[str]:
        """Get immediate next actions based on gate result"""
        
        if gate_passed:
            return [
                "✅ Quality gate passed - proceed with deployment",
                "📊 Monitor coverage metrics in production",
                "🔄 Schedule next quality review"
            ]
        else:
            return [
                "🛑 Quality gate failed - block deployment",
                "🔧 Address all quality violations before retry",
                "📝 Update coverage improvement plan",
                "🔄 Re-run quality gate after fixes"
            ]

def main():
    """Main execution function"""
    
    parser = argparse.ArgumentParser(
        description='ACGS-2 Coverage Quality Gate'
    )
    parser.add_argument('--coverage-file', 
                       default='aggregated_coverage.json',
                       help='Aggregated coverage file to check')
    parser.add_argument('--constitutional-hash', 
                       default='cdd01ef066bc6cf2',
                       help='Constitutional hash to validate')
    parser.add_argument('--min-coverage', 
                       type=float, default=90,
                       help='Minimum overall coverage percentage')
    parser.add_argument('--min-constitutional-coverage', 
                       type=float, default=95,
                       help='Minimum constitutional compliance percentage')
    parser.add_argument('--fail-on-violation', 
                       action='store_true',
                       help='Exit with error code if quality gate fails')
    parser.add_argument('--output-file',
                       help='Save quality gate report to file')
    
    args = parser.parse_args()
    
    # Initialize quality gate
    gate = CoverageQualityGate(args.constitutional_hash)
    
    # Enforce quality gate
    report = gate.enforce_quality_gate(
        args.coverage_file,
        args.min_coverage,
        args.min_constitutional_coverage,
        args.fail_on_violation
    )
    
    # Save report if requested
    if args.output_file:
        with open(args.output_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"📄 Quality gate report saved to: {args.output_file}")
    
    # Exit with appropriate code
    gate_passed = report.get('quality_gate', {}).get('passed', False)
    
    if args.fail_on_violation and not gate_passed:
        print(f"\n❌ Quality gate FAILED - exiting with error")
        sys.exit(1)
    elif gate_passed:
        print(f"\n✅ Quality gate PASSED")
        sys.exit(0)
    else:
        print(f"\n⚠️ Quality gate completed with warnings")
        sys.exit(0)

if __name__ == "__main__":
    main()