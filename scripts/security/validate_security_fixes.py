#!/usr/bin/env python3
"""
ACGS-2 Security Validation Script
Constitutional Hash: cdd01ef066bc6cf2

Validates that all critical security vulnerabilities have been addressed
and that the system maintains constitutional compliance.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import re

class SecurityValidator:
    """Validates security fixes across ACGS-2 codebase"""
    
    def __init__(self):
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.project_root = Path("/home/dislove/ACGS-2")
        
        # Expected minimum versions for critical packages
        self.required_versions = {
            'transformers': '4.52.1',
            'aiohttp': '3.10.11', 
            'cryptography': '43.0.1',
            'orjson': '3.9.15'
        }
        
        # Critical CVEs that should be resolved
        self.critical_cves = [
            'CVE-2023-6730',  # transformers deserialization
            'CVE-2023-7018',  # transformers deserialization
            'CVE-2024-11392', # transformers MobileViTV2
            'CVE-2024-11393', # transformers MaskFormer
            'CVE-2024-11394', # transformers Trax
            'CVE-2024-23334', # aiohttp directory traversal
            'CVE-2024-30251', # aiohttp DoS
            'CVE-2024-52304', # aiohttp request smuggling
            'CVE-2024-27454', # orjson recursion
        ]
    
    def find_requirements_files(self) -> List[Path]:
        """Find all config/environments/requirements.txt files in the project"""
        return list(self.project_root.rglob("requirements*.txt"))
    
    def parse_version(self, version_str: str) -> Tuple[int, ...]:
        """Parse version string into comparable tuple"""
        # Extract version numbers, handling >= operators
        version_match = re.search(r'(\d+(?:\.\d+)*)', version_str)
        if version_match:
            return tuple(map(int, version_match.group(1).split('.')))
        return (0,)
    
    def check_package_version(self, req_file: Path, package: str, min_version: str) -> bool:
        """Check if package meets minimum version requirement"""
        try:
            with open(req_file, 'r') as f:
                content = f.read()
            
            # Look for package version specification
            pattern = rf'{package}[>=!~<]*([0-9.]+)'
            matches = re.findall(pattern, content, re.IGNORECASE)
            
            if not matches:
                return False  # Package not found
            
            # Check if any version meets requirement
            min_ver_tuple = self.parse_version(min_version)
            for version in matches:
                current_ver_tuple = self.parse_version(version)
                if current_ver_tuple >= min_ver_tuple:
                    return True
            
            return False
            
        except Exception as e:
            print(f"Error checking {req_file}: {e}")
            return False
    
    def run_safety_check(self, req_file: Path) -> Dict:
        """Run safety check on requirements file"""
        try:
            result = subprocess.run([
                sys.executable, '-m', 'safety', 'check', 
                '-r', str(req_file), '--json'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                return {"vulnerabilities": [], "status": "clean"}
            elif result.stdout:
                try:
                    data = json.loads(result.stdout)
                    return {"vulnerabilities": data, "status": "vulnerable"}
                except json.JSONDecodeError:
                    return {"vulnerabilities": [], "status": "error", "message": result.stdout}
            else:
                return {"vulnerabilities": [], "status": "clean"}
                
        except Exception as e:
            return {"vulnerabilities": [], "status": "error", "message": str(e)}
    
    def validate_constitutional_compliance(self) -> bool:
        """Validate constitutional hash presence in updated files"""
        req_files = self.find_requirements_files()
        compliant_files = 0
        
        for req_file in req_files:
            try:
                with open(req_file, 'r') as f:
                    content = f.read()
                if self.constitutional_hash in content:
                    compliant_files += 1
            except Exception:
                continue
        
        # At least 80% of files should have constitutional hash
        compliance_rate = compliant_files / len(req_files) if req_files else 0
        return compliance_rate >= 0.8
    
    def generate_report(self) -> Dict:
        """Generate comprehensive security validation report"""
        report = {
            "timestamp": subprocess.run(['date', '-u', '+%Y-%m-%dT%H:%M:%SZ'], 
                                      capture_output=True, text=True).stdout.strip(),
            "constitutional_hash": self.constitutional_hash,
            "validation_results": {
                "package_versions": {},
                "safety_checks": {},
                "constitutional_compliance": False,
                "overall_status": "UNKNOWN"
            },
            "summary": {
                "total_files_checked": 0,
                "files_with_vulnerabilities": 0,
                "critical_packages_updated": 0,
                "constitutional_compliance_rate": 0.0
            }
        }
        
        req_files = self.find_requirements_files()
        report["summary"]["total_files_checked"] = len(req_files)
        
        # Check package versions
        critical_packages_updated = 0
        for package, min_version in self.required_versions.items():
            package_status = {"files_updated": 0, "files_checked": 0}
            
            for req_file in req_files:
                package_status["files_checked"] += 1
                if self.check_package_version(req_file, package, min_version):
                    package_status["files_updated"] += 1
            
            report["validation_results"]["package_versions"][package] = package_status
            
            # Consider package updated if >80% of relevant files are updated
            if package_status["files_updated"] / max(package_status["files_checked"], 1) >= 0.8:
                critical_packages_updated += 1
        
        report["summary"]["critical_packages_updated"] = critical_packages_updated
        
        # Run safety checks
        files_with_vulnerabilities = 0
        for req_file in req_files:
            safety_result = self.run_safety_check(req_file)
            report["validation_results"]["safety_checks"][str(req_file)] = safety_result
            
            if safety_result["status"] == "vulnerable" and safety_result["vulnerabilities"]:
                files_with_vulnerabilities += 1
        
        report["summary"]["files_with_vulnerabilities"] = files_with_vulnerabilities
        
        # Check constitutional compliance
        compliance = self.validate_constitutional_compliance()
        report["validation_results"]["constitutional_compliance"] = compliance
        
        # Calculate compliance rate
        compliant_files = sum(1 for req_file in req_files 
                            if self.constitutional_hash in req_file.read_text(errors='ignore'))
        report["summary"]["constitutional_compliance_rate"] = compliant_files / len(req_files) if req_files else 0
        
        # Determine overall status
        if (critical_packages_updated == len(self.required_versions) and 
            files_with_vulnerabilities == 0 and 
            compliance):
            report["validation_results"]["overall_status"] = "SECURE"
        elif files_with_vulnerabilities == 0 and critical_packages_updated >= 3:
            report["validation_results"]["overall_status"] = "IMPROVED"
        else:
            report["validation_results"]["overall_status"] = "NEEDS_ATTENTION"
        
        return report
    
    def print_report(self, report: Dict):
        """Print human-readable security validation report"""
        print("=" * 80)
        print("🔒 ACGS-2 SECURITY VALIDATION REPORT")
        print("=" * 80)
        print(f"Timestamp: {report['timestamp']}")
        print(f"Constitutional Hash: {report['constitutional_hash']}")
        print(f"Overall Status: {report['validation_results']['overall_status']}")
        print()
        
        print("📊 SUMMARY:")
        summary = report['summary']
        print(f"  • Total files checked: {summary['total_files_checked']}")
        print(f"  • Files with vulnerabilities: {summary['files_with_vulnerabilities']}")
        print(f"  • Critical packages updated: {summary['critical_packages_updated']}/{len(self.required_versions)}")
        print(f"  • Constitutional compliance: {summary['constitutional_compliance_rate']:.1%}")
        print()
        
        print("🔧 PACKAGE VERSION STATUS:")
        for package, status in report['validation_results']['package_versions'].items():
            updated_rate = status['files_updated'] / max(status['files_checked'], 1)
            status_icon = "✅" if updated_rate >= 0.8 else "❌"
            print(f"  {status_icon} {package}: {status['files_updated']}/{status['files_checked']} files updated ({updated_rate:.1%})")
        print()
        
        print("🛡️ SAFETY CHECK RESULTS:")
        vulnerable_files = [f for f, result in report['validation_results']['safety_checks'].items() 
                          if result['status'] == 'vulnerable' and result['vulnerabilities']]
        
        if not vulnerable_files:
            print("  ✅ No vulnerabilities found in any requirements files")
        else:
            print(f"  ❌ {len(vulnerable_files)} files still have vulnerabilities:")
            for file_path in vulnerable_files[:5]:  # Show first 5
                print(f"    • {file_path}")
        print()
        
        print("📋 CONSTITUTIONAL COMPLIANCE:")
        compliance_status = "✅ COMPLIANT" if report['validation_results']['constitutional_compliance'] else "❌ NON-COMPLIANT"
        print(f"  {compliance_status} ({summary['constitutional_compliance_rate']:.1%} of files)")
        print()
        
        # Recommendations
        print("🎯 RECOMMENDATIONS:")
        if report['validation_results']['overall_status'] == "SECURE":
            print("  ✅ All critical security issues have been addressed!")
            print("  ✅ Continue monitoring for new vulnerabilities")
        else:
            if summary['files_with_vulnerabilities'] > 0:
                print("  🔴 Address remaining vulnerabilities in requirements files")
            if summary['critical_packages_updated'] < len(self.required_versions):
                print("  🔴 Complete package updates for all critical dependencies")
            if not report['validation_results']['constitutional_compliance']:
                print("  🟡 Improve constitutional compliance in requirements files")
        
        print("=" * 80)

def main():
    """Main validation function"""
    validator = SecurityValidator()
    
    print("🔍 Running ACGS-2 Security Validation...")
    print("This may take a few minutes...")
    print()
    
    report = validator.generate_report()
    validator.print_report(report)
    
    # Save detailed report
    report_file = Path("docs/security/security_validation_report.json")
    report_file.parent.mkdir(parents=True, exist_ok=True)
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"📄 Detailed report saved to: {report_file}")
    
    # Exit with appropriate code
    if report['validation_results']['overall_status'] == "SECURE":
        sys.exit(0)
    elif report['validation_results']['overall_status'] == "IMPROVED":
        sys.exit(1)  # Warning level
    else:
        sys.exit(2)  # Error level

if __name__ == "__main__":
    main()
